#include "connect.hpp"
#include "tls/tls.hpp"
#include "command_id.hpp"
#include "segmented_json.h"
#include "render.hpp"
#include "json_out.hpp"
#include "connection_cache.hpp"

#include <http/httpc.hpp>
#include <http/websocket.hpp>

#include <logging/log.hpp>
#include <str_utils.hpp>

#include <atomic>
#include <cassert>
#include <cstring>
#include <debug.h>
#include <cstring>
#include <optional>
#include <variant>
#include <charconv>

using namespace http;
using json::ChunkRenderer;
using json::JsonRenderer;
using json::JsonResult;
using std::decay_t;
using std::get;
using std::get_if;
using std::holds_alternative;
using std::is_same_v;
using std::make_optional;
using std::make_tuple;
using std::monostate;
using std::move;
using std::nullopt;
using std::optional;
using std::string_view;
using std::variant;
using std::visit;

LOG_COMPONENT_DEF(connect, logging::Severity::debug);

namespace connect_client {

namespace {

    // Send a ping if there's no activity from us during this time (15_000 ms = 15s)
    constexpr uint32_t ping_inactivity = 15000;

    // These two should actually be a atomic<tuple<.., ..>>. This won't compile on our platform.
    // But, considering the error is informative only and we set these only in
    // this thread, any temporary inconsistency in them is of no concern
    // anyway, so they can be two separate atomics without any adverse effects.
    std::atomic<ConnectionStatus> last_known_status = ConnectionStatus::Unknown;
    std::atomic<OnlineError> last_connection_error = OnlineError::NoError;
    std::atomic<optional<uint8_t>> retries_left;

    std::atomic<bool> registration = false;
    std::atomic<const char *> registration_code_ptr = nullptr;

    void process_status(monostate, ConnectionStatus) {}

    void process_status(OnlineError error, ConnectionStatus err_status) {
        last_known_status = err_status;
        last_connection_error = error;
    }

    void process_status(ConnectionStatus status, ConnectionStatus /* err_status unused */) {
        last_known_status = status;
        switch (status) {
        case ConnectionStatus::Ok:
        case ConnectionStatus::NoConfig:
        case ConnectionStatus::Off:
        case ConnectionStatus::RegistrationCode:
        case ConnectionStatus::RegistrationDone:
            // These are the states we want to stay in, if we are in one,
            // any past errors make no sense, we are happy.
            last_connection_error = OnlineError::NoError;
            retries_left = nullopt;
            break;
        default:
            break;
        }
    }

    void process_status(ErrWithRetry err, ConnectionStatus err_status) {
        last_connection_error = err.err;
        retries_left = err.retry;
        if (err.retry == 0) {
            last_known_status = err_status;
        }
    }

    void process_status(CommResult status, ConnectionStatus err_status) {
        visit([&](auto s) { process_status(s, err_status); }, status);
    }

    class BasicRequest final : public JsonPostRequest {
    private:
        HeaderOut hdrs[3];
        Renderer renderer_impl;
        const char *target_url;
        static const char *url(const Sleep &) {
            // Sleep already handled at upper level.
            assert(0);
            return "";
        }
        static const char *url(const ReadCommand &) {
            // Not used in non-websocket mode
            assert(0);
            return "";
        }
        static const char *url(const transfers::Download::InlineRequest &) {
            // Not used in non-websocket mode and websocket doesn't call url.
            assert(0);
            return "";
        }
        static const char *url(const SendTelemetry &) {
            return "/p/telemetry";
        }
        static const char *url(const Event &) {
            return "/p/events";
        }

    protected:
        virtual ChunkRenderer &renderer() override {
            return renderer_impl;
        }

    public:
        BasicRequest(Printer &printer, const Printer::Config &config, const Action &action, optional<CommandId> background_command_id)
            : hdrs {
                // Even though the fingerprint is on a temporary, that
                // pointer is guaranteed to stay stable.
                { "Fingerprint", printer.printer_info().fingerprint, Printer::PrinterInfo::FINGERPRINT_HDR_SIZE },
                { "Token", config.token, nullopt },
                { nullptr, nullptr, nullopt }
            }
            , renderer_impl(RenderState(printer, action, background_command_id))
            , target_url(visit([](const auto &action) { return url(action); }, action)) {}
        virtual const char *url() const override {
            return target_url;
        }
        virtual const HeaderOut *extra_headers() const override {
            return hdrs;
        }
    };

    class UpgradeRequest final : public http::Request {
    private:
        // 2 for auth
        // 1 for upgrade
        // 3 for websocket negotiation
        // 1 for sentinel
        HeaderOut hdrs[7];

    public:
        UpgradeRequest(Printer &printer, const Printer::Config &config, const WebSocketKey &key)
            : hdrs {
                // Even though the fingerprint is on a temporary, that
                // pointer is guaranteed to stay stable.
                { "Fingerprint", printer.printer_info().fingerprint, Printer::PrinterInfo::FINGERPRINT_HDR_SIZE },
                { "Token", config.token, nullopt },
                { "Upgrade", "websocket", nullopt },
                { "Sec-WebSocket-Key", key.req(), nullopt },
                { "Sec-WebSocket-Version", "13", nullopt },
                { "Sec-WebSocket-Protocol", "prusa-connect", nullopt },
                { nullptr, nullptr, nullopt }
            } {}
        virtual const char *url() const override {
            return "/p/ws";
        }
        virtual Method method() const override {
            return Method::Get;
        }
        virtual ContentType content_type() const override {
            // Not actually used for a get request
            return ContentType::ApplicationOctetStream;
        }
        virtual const HeaderOut *extra_headers() const override {
            return hdrs;
        }

        virtual const char *connection() const override {
            return "upgrade";
        }
    };

    // TODO: We probably want to be able to both have a smaller buffer and
    // handle larger responses. We need some kind of parse-as-it-comes approach
    // for that.
    // Note: This buffer is huge, but we are in the shallow waters of the stack, so it
    // should be fine, even 3200 buffer still did not overflow in my tests, even in debug.
    // So unless the call stack changes significantly, we are fine, just beware if doing
    // larger changes, or using this elsewhere.
    const constexpr size_t MAX_RESP_SIZE = 512;

    // Send a full telemetry every 5 minutes.
    const constexpr Duration FULL_TELEMETRY_EVERY = 5 * 60 * 1000;

    // Wait this long between config change checking when Connect is off.
    const constexpr Duration CONFIG_ENABLED_RECHECK = 1000;
} // namespace

#if WEBSOCKET()
CommResult Connect::send_ping(CachedFactory &conn_factory) {
    log_debug(connect, "Sending ping");
    uint8_t buffer[0] = {};
    if (auto error = websocket->send(WebSocket::Ping, /*last=*/true, buffer, 0); error.has_value()) {
        conn_factory.invalidate();
        return err_to_status(*error);
    }

    last_send = now();

    return ConnectionStatus::Ok;
}

CommResult Connect::prepare_connection(CachedFactory &conn_factory, const Printer::Config &config) {
    if (!conn_factory.is_valid()) {
        // With websocket, we don't try the connection if we are in the error
        // state, so get rid of potential error state first.
        conn_factory.invalidate();

        // Could have been using the old connection and contain a dangling pointer. Get rid of it.
        // (We currently don't do a proper shutdown
        websocket.reset();
        // Similarly, any download that has been running might have missing /
        // confused chunks, we need a new one.
        planner().transfer_reset();
        last_known_status = ConnectionStatus::Connecting;
    }
    // Let it reconnect if it needs it.
    conn_factory.refresh(config);

    HttpClient http(conn_factory);

    if (conn_factory.is_valid() && !websocket.has_value()) {
        // Let's do the upgrade
        log_debug(connect, "Starting WS handshake");

        WebSocketKey websocket_key;
        WebSocketAccept upgrade_hdrs(websocket_key);
        UpgradeRequest upgrade(printer, config, websocket_key);
        const auto result = http.send(upgrade, &upgrade_hdrs);
        if (holds_alternative<Error>(result)) {
            conn_factory.invalidate();
            return err_to_status(get<Error>(result));
        }

        auto resp = get<http::Response>(result);
        switch (resp.status) {
        case Status::SwitchingProtocols: {
            if (!upgrade_hdrs.key_matched() || !upgrade_hdrs.all_supported()) {
                conn_factory.invalidate();
                return OnlineError::Server;
            }

            log_debug(connect, "WS complete");

            // Read and throw away the body, if any. Not interesting.
            uint8_t throw_away[128];
            size_t received = 0;
            do {
                auto result = resp.read_body(throw_away, sizeof throw_away);
                if (holds_alternative<Error>(result)) {
                    conn_factory.invalidate();
                    return err_to_status(get<Error>(result));
                }
                received = get<size_t>(result);
            } while (received > 0);

            websocket = WebSocket::from_response(resp);
            // Initiating the connection is a "send" in some sense.
            last_send = now();
            break;
        }
        default: {
            log_info(connect, "Failed with %" PRIu16, static_cast<uint16_t>(resp.status));
            conn_factory.invalidate();
            planner().action_done(ActionResult::Refused);
            switch (resp.status) {
            case Status::BadRequest:
                return OnlineError::Internal;
            case Status::Forbidden:
            case Status::Unauthorized:
                return OnlineError::Auth;
            default:
                return OnlineError::Server;
            }
            break;
        }
        }
    }

    return monostate {};
}

CommResult Connect::send_command(CachedFactory &conn_factory, const Printer::Config &, Action &&action, optional<CommandId> background_command_id) {
    log_debug(connect, "Sending to server");
    if (!websocket.has_value()) {
        planner().action_done(ActionResult::Failed);
        return OnlineError::Network;
    }
    Renderer renderer(RenderState(printer, action, background_command_id));
    uint8_t buffer[MAX_RESP_SIZE];
    bool more = true;
    bool first = true;
    while (more) {
        const auto [result, written_json] = renderer.render(buffer, sizeof buffer);
        switch (result) {
        case JsonResult::Abort:
        case JsonResult::BufferTooSmall:
            return OnlineError::Internal;
        case JsonResult::Complete:
            more = false;
            break;
        case JsonResult::Incomplete:
            break;
        }

        log_debug(connect, "Send %.*s", written_json, buffer);

        if (auto error = websocket->send(first ? WebSocket::Text : WebSocket::Continuation, !more, buffer, written_json); error.has_value()) {
            conn_factory.invalidate();
            planner().action_done(ActionResult::Failed);
            return err_to_status(*error);
        }

        last_send = now();

        first = false;
    }

    log_debug(connect, "Sending done");

    planner().action_done(ActionResult::Ok);

    return ConnectionStatus::Ok;
}
#else
CommResult Connect::prepare_connection(CachedFactory &conn_factory, const Printer::Config &config) {
    if (!conn_factory.is_valid()) {
        last_known_status = ConnectionStatus::Connecting;
    }
    // Let it reconnect if it needs it.
    conn_factory.refresh(config);

    return monostate {};
}

CommResult Connect::send_command(CachedFactory &conn_factory, const Printer::Config &config, Action &&action, optional<CommandId> background_command_id) {
    log_debug(connect, "Sending to connect");
    BasicRequest request(printer, config, action, background_command_id);
    ExtractCommanId cmd_id;

    HttpClient http(conn_factory);

    const auto result = http.send(request, &cmd_id);
    // Drop current job paths (if any) to make space for potentially parsing a command from the server.
    // In case we failed to send the JOB_INFO event that uses the paths, we
    // will acquire it and fill it in the next iteration anyway.
    //
    // Note that this invalidates the paths inside params in the current printer snapshot.
    printer.drop_paths();

    if (holds_alternative<Error>(result)) {
        log_debug(connect, "Failed to exchange");
        planner().action_done(ActionResult::Failed);
        conn_factory.invalidate();
        return err_to_status(get<Error>(result));
    }

    http::Response resp = get<http::Response>(result);
    log_debug(connect, "Response with status %" PRIu16, static_cast<uint16_t>(resp.status));
    if (!resp.can_keep_alive) {
        conn_factory.invalidate();
    }
    switch (resp.status) {
    // The server has nothing to tell us
    case Status::NoContent:
        log_debug(connect, "Have a response without body");
        planner().action_done(ActionResult::Ok);
        return ConnectionStatus::Ok;
    case Status::Ok: {
        log_debug(connect, "Have a response with body");
        if (cmd_id.command_id.has_value()) {
            const auto sub_resp = handle_server_resp(resp, *cmd_id.command_id);
            return visit([&](auto &&arg) -> CommResult {
                // Trick out of std::visit documentation. Switch by the type of arg.
                using T = decay_t<decltype(arg)>;

                if constexpr (is_same_v<T, monostate>) {
                    planner().action_done(ActionResult::Ok);
                    return ConnectionStatus::Ok;
                } else if constexpr (is_same_v<T, Command>) {
                    planner().action_done(ActionResult::Ok);
                    planner().command(arg);
                    return ConnectionStatus::Ok;
                } else if constexpr (is_same_v<T, Error>) {
                    planner().action_done(ActionResult::Failed);
                    planner().command(Command {
                        cmd_id.command_id.value(),
                        BrokenCommand { to_str(arg) },
                    });
                    conn_factory.invalidate();
                    return err_to_status(arg);
                }
            },
                sub_resp);
        } else {
            // We have received a command without command ID
            // There's no better action for us than just throw it away.
            planner().action_done(ActionResult::Refused);
            conn_factory.invalidate();
            return OnlineError::Confused;
        }
    }
    case Status::RequestTimeout:
    case Status::TooManyRequests:
    case Status::ServiceTemporarilyUnavailable:
    case Status::GatewayTimeout:
        conn_factory.invalidate();
        // These errors are likely temporary and will go away eventually.
        planner().action_done(ActionResult::Failed);
        return OnlineError::Server;
    default:
        conn_factory.invalidate();
        // We don't know that exactly the server answer means, but we guess
        // that it will persist, so we consider it refused and throw the
        // request away.
        planner().action_done(resp.status == Status::BadRequest ? ActionResult::RefusedFast : ActionResult::Refused);
        // Switch just to provide proper error message
        switch (resp.status) {
        case Status::BadRequest:
            return OnlineError::Internal;
        case Status::Forbidden:
        case Status::Unauthorized:
            return OnlineError::Auth;
        default:
            return OnlineError::Server;
        }
    }
}
#endif

CommResult Connect::communicate(CachedFactory &conn_factory) {
    const auto [config, cfg_changed] = printer.config();

    // Make sure to reconnect if the configuration changes .
    if (cfg_changed) {
        conn_factory.invalidate();
        // Possibly new server
        planner().reset();
    }

    if (!config.enabled) {
        planner().reset();
        Sleep::idle(CONFIG_ENABLED_RECHECK).perform(printer, planner());
        return ConnectionStatus::Off;
    } else if (config.host[0] == '\0' || config.token[0] == '\0') {
        planner().reset();
        Sleep::idle(CONFIG_ENABLED_RECHECK).perform(printer, planner());
        return ConnectionStatus::NoConfig;
    }

    printer.drop_paths(); // In case they were left in there in some early-return case.
    auto borrow = buffer.borrow();
    if (planner().wants_job_paths()) {
        assert(borrow.has_value());
    } else {
        borrow.reset();
    }
    printer.renew(move(borrow));

    // This is a bit of a hack, we want to keep watching for USB being inserted
    // or not. We don't have a good place, so we stuck it here.
    transfers::ChangedPath::instance.media_inserted(printer.params().has_usb);

    Connection *wake_on_readable = nullptr;
#if WEBSOCKET()
    // The "ordinary" http exchange gets data in the response, websocket at any
    // time so we want to let it get woken up by arriving data in sleep (the
    // planner checks if it _can_ receive the command at that point).
    if (conn_factory.is_valid() && websocket.has_value()) {
        wake_on_readable = websocket->inner_connection();

        if (now() - last_send > ping_inactivity) {
            return send_ping(conn_factory);
        }
    } else {
        // The server node might want to have fresh telemetry. Important in websocket mode, because:
        // * We stretch the time between telemetries to much longer in
        //   websocket mode, so the time to "auto-recover" is longer.
        // * The server node in the websocket mode can keep a bit more context
        //   internally, unlike the http-based exchange.
        planner().reset_telemetry();
    }
#endif
    auto action = planner().next_action(buffer, wake_on_readable);

    // Handle sleeping first. That one doesn't need the connection.
    if (auto *s = get_if<Sleep>(&action)) {
        s->perform(printer, planner());
        return monostate {};
    }

    auto prepared = prepare_connection(conn_factory, config);
    if (!holds_alternative<monostate>(prepared)) {
        log_debug(connect, "No connection to communicate");
        if (holds_alternative<Event>(action) || holds_alternative<SendTelemetry>(action)) {
            planner().action_done(ActionResult::Failed);
        }

        return prepared;
    }

    const auto background_command_id = planner().background_command_id();

    if (holds_alternative<ReadCommand>(action)) {
#if WEBSOCKET()
        return receive_command(conn_factory);
#else
        assert(0); // Doesn't happen in non-websocket mode, commands come in responses
        return err_to_status(Error::InternalError);
#endif
    } else {
        return send_command(conn_factory, config, move(action), background_command_id);
    }
}

void Connect::run() {
    log_debug(connect, "%s", "Connect client starts\n");

    CachedFactory conn_factory;

    while (true) {
        auto reg_wanted = registration.load();
        auto reg_running = holds_alternative<Registrator>(guts);
        if (reg_wanted && reg_running) {
            const auto new_status = get<Registrator>(guts).communicate(conn_factory);
            process_status(new_status, ConnectionStatus::RegistrationError);
        } else if (reg_wanted && !reg_running) {
            guts.emplace<Registrator>(printer);
            last_known_status = ConnectionStatus::Unknown;
            last_connection_error = OnlineError::NoError;
            retries_left = nullopt;
            conn_factory.invalidate();
            registration_code_ptr = get<Registrator>(guts).get_code();
        } else if (!reg_wanted && reg_running) {
            last_known_status = ConnectionStatus::Unknown;
            last_connection_error = OnlineError::NoError;
            retries_left = nullopt;
            registration_code_ptr = nullptr;
            guts.emplace<Planner>(printer);
            conn_factory.invalidate();
        } else {
            const auto new_status = communicate(conn_factory);
            process_status(new_status, ConnectionStatus::Error);
        }
    }
}

Planner &Connect::planner() {
    assert(holds_alternative<Planner>(guts));
    return get<Planner>(guts);
}

Connect::Connect(Printer &printer, SharedBuffer &buffer)
    : guts(Planner(printer))
    , printer(printer)
    , buffer(buffer) {}

OnlineStatus last_status() {
    return make_tuple(last_known_status.load(), last_connection_error.load(), retries_left.load());
}

bool is_connect_registered() {
    switch (last_known_status.load()) {
    case ConnectionStatus::Ok:
    case ConnectionStatus::Connecting:
    case ConnectionStatus::Error:
        return true;
    default:
        break;
    }
    return false;
}

void request_registration() {
    bool old = registration.exchange(true);
    // Avoid warnings
    (void)old;
    assert(!old);
}

void leave_registration() {
    bool old = registration.exchange(false);
    // Avoid warnings
    (void)old;
    assert(old);
}

const char *registration_code() {
    // Note: This is just a safety, the caller shall not call us in case this
    // is not the case.
    const auto status = last_known_status.load();
    if (status == ConnectionStatus::RegistrationCode || status == ConnectionStatus::RegistrationDone) {
        return registration_code_ptr;
    } else {
        return nullptr;
    }
}

} // namespace connect_client
