#include "connect.hpp"
#include "connection_cache.hpp"

#include <http/websocket.hpp>
#include <logging/log.hpp>
#include <str_utils.hpp>

#include <algorithm>
#include <charconv>
#include <cinttypes>
#include <optional>
#include <variant>

using namespace http;
using std::get;
using std::get_if;
using std::holds_alternative;
using std::make_optional;
using std::monostate;
using std::move;
using std::nullopt;
using std::string_view;
using std::variant;
using std::visit;

LOG_COMPONENT_REF(connect);

namespace connect_client {

namespace {

    constexpr size_t max_response_size = 512;

#if WEBSOCKET()
    class DebugHandler {
    public:
        uint32_t id;
        bool started = false;

        CommResult flush(const uint8_t *buffer, size_t size, bool) {
            const char *fmt = started ? "Msg from server: %.*s" : "Msg from server (cont): %.*s";
            log_info(connect, fmt, static_cast<int>(size), reinterpret_cast<const char *>(buffer));
            started = true;
            return monostate {};
        }
    };

    using BufferParser = Command (*)(CommandId id, uint8_t *data, size_t size, SharedBuffer::Borrow buffer);

    class CommandHandler {
    public:
        CommandId id;
        // This would be a reference if the handler did not need to be assignable.
        Planner *planner;
        SharedBuffer::Borrow buffer;
        BufferParser parser;
        bool broken = false;

        CommResult flush(uint8_t *data, size_t size, bool last) {
            if (broken) {
                return monostate {};
            }

            if (!last) {
                log_warning(connect, "Oversized command %" PRIu32 "X received", id);
                broken = true;
                planner->command(Command { id, BrokenCommand { "Oversized command" } });
                return monostate {};
            }

            planner->transfer_checkpoint();
            planner->command(parser(id, data, size, move(buffer)));
            return monostate {};
        }
    };

    class ChunkHandler {
    public:
        uint32_t id;
        Planner *planner;

        CommResult flush(const uint8_t *buffer, size_t size, bool) {
            const bool ok = planner->transfer_chunk(transfers::Download::InlineChunk {
                id,
                size,
                buffer,
            });
            return ok ? CommResult { monostate {} } : CommResult { OnlineError::Internal };
        }
    };

    class IgnoreCommand {
    public:
        CommResult flush(const uint8_t *, size_t, bool) {
            return monostate {};
        }
    };
#endif

} // namespace

Connect::ServerResp Connect::handle_server_resp(http::Response response, CommandId command_id) {
    // Consume the body even when the command is rejected so the connection can be reused.
    uint8_t receive_buffer[max_response_size];
    const auto result = response.read_all(receive_buffer, sizeof receive_buffer);
    if (const auto *error = get_if<Error>(&result); error != nullptr) {
        return *error;
    }
    const size_t size = get<size_t>(result);

    if (command_id == planner().background_command_id()) {
        return Command { command_id, ProcessingThisCommand {} };
    }

    auto maybe_buffer = buffer.borrow();
    if (!maybe_buffer.has_value()) {
        return Command { command_id, ProcessingOtherCommand {} };
    }

    switch (response.content_type) {
    case ContentType::TextGcode: {
        const string_view body(reinterpret_cast<const char *>(receive_buffer), size);
        return Command::gcode_command(command_id, body, move(*maybe_buffer));
    }
    case ContentType::ApplicationJson:
        return Command::parse_json_command(command_id, reinterpret_cast<char *>(receive_buffer), size, move(*maybe_buffer));
    default:
        return Command { command_id, UnknownCommand {} };
    }
}

#if WEBSOCKET()
CommResult Connect::receive_command(CachedFactory &connection_factory) {
    log_debug(connect, "Trying to receive a command from server");
    bool first = true;
    bool more = true;
    size_t read = 0;
    bool parsed = false;
    constexpr size_t header_length = 9;
    uint8_t receive_buffer[max_response_size + header_length];
    variant<IgnoreCommand, DebugHandler, ChunkHandler, CommandHandler> handler;

    while (more) {
        auto result = websocket->receive(first ? make_optional(0) : nullopt);
        if (holds_alternative<monostate>(result)) {
            log_debug(connect, "No command available now");
            break;
        }
        if (holds_alternative<Error>(result)) {
            log_error(connect, "Lost connection when reading command");
            connection_factory.invalidate();
            return err_to_status(get<Error>(result));
        }

        auto fragment = get<WebSocket::FragmentHeader>(result);
        switch (fragment.opcode) {
        case WebSocket::Opcode::Ping: {
            log_debug(connect, "Ping from server");
            constexpr size_t max_fragment_length = 126;
            if (fragment.len > max_fragment_length) {
                connection_factory.invalidate();
                return OnlineError::Confused;
            }

            uint8_t data[max_fragment_length];
            if (auto maybe_error = fragment.conn->rx_exact(data, fragment.len); maybe_error.has_value()) {
                connection_factory.invalidate();
                return err_to_status(*maybe_error);
            }
            if (auto maybe_error = websocket->send(WebSocket::Pong, true, data, fragment.len); maybe_error.has_value()) {
                connection_factory.invalidate();
                return err_to_status(*maybe_error);
            }
            last_send = now();
            continue;
        }
        case WebSocket::Opcode::Pong:
            fragment.ignore();
            continue;
        case WebSocket::Opcode::Close:
            connection_factory.invalidate();
            log_info(connect, "Close from server");
            return OnlineError::Network;
        default:
            break;
        }

        first = false;
        while (fragment.len > 0) {
            const size_t to_read = std::min(sizeof receive_buffer - read, fragment.len);
            if (auto maybe_error = fragment.conn->rx_exact(receive_buffer + read, to_read); maybe_error.has_value()) {
                connection_factory.invalidate();
                return err_to_status(*maybe_error);
            }

            fragment.len -= to_read;
            read += to_read;
            if (!fragment.last && read != sizeof receive_buffer) {
                continue;
            }

            size_t skip = 0;
            if (!parsed) {
                if (read < header_length) {
                    planner().command(Command { 0, BrokenCommand { "Message too short to contain header" } });
                    return ConnectionStatus::Ok;
                }

                CommandId command_id;
                const auto id_result = from_chars_light(
                    reinterpret_cast<const char *>(receive_buffer + 1),
                    reinterpret_cast<const char *>(receive_buffer + header_length),
                    command_id,
                    16);
                if (id_result.ec != std::errc {}) {
                    planner().command(Command { 0, BrokenCommand { "Could not parse command ID" } });
                    return ConnectionStatus::Ok;
                }

                const char command_type = receive_buffer[0];
                log_debug(connect, "Received a command from server %c %" PRIu32 "X", command_type, command_id);
                auto maybe_buffer = buffer.borrow();
                if (!maybe_buffer.has_value() && (command_type == 'G' || command_type == 'F' || command_type == 'J')) {
                    planner().command(Command { command_id, ProcessingOtherCommand {} });
                    handler = IgnoreCommand {};
                } else {
                    switch (command_type) {
                    case 'J':
                        handler = CommandHandler {
                            .id = command_id,
                            .planner = &planner(),
                            .buffer = move(*maybe_buffer),
                            .parser = [](CommandId id, uint8_t *data, size_t size, SharedBuffer::Borrow shared_buffer) {
                                return Command::parse_json_command(id, reinterpret_cast<char *>(data), size, move(shared_buffer));
                            },
                        };
                        break;
                    case 'G':
                    case 'F':
                        handler = CommandHandler {
                            .id = command_id,
                            .planner = &planner(),
                            .buffer = move(*maybe_buffer),
                            .parser = [](CommandId id, uint8_t *data, size_t size, SharedBuffer::Borrow shared_buffer) {
                                const string_view body(reinterpret_cast<const char *>(data), size);
                                return Command::gcode_command(id, body, move(shared_buffer));
                            },
                        };
                        break;
                    case 'D':
                        handler = DebugHandler { command_id };
                        break;
                    case 'T':
                        handler = ChunkHandler { command_id, &planner() };
                        break;
                    default:
                        planner().command(Command { command_id, BrokenCommand { "Unrecognized type of message" } });
                        handler = IgnoreCommand {};
                        break;
                    }
                }
                parsed = true;
                skip = header_length;
            }

            const auto flush_result = visit(
                [&](auto &&current_handler) {
                    return current_handler.flush(receive_buffer + skip, read - skip, fragment.last && fragment.len == 0);
                },
                handler);
            if (!holds_alternative<monostate>(flush_result)) {
                if (holds_alternative<OnlineError>(flush_result)) {
                    connection_factory.invalidate();
                }
                return flush_result;
            }
            read = 0;
        }

        if (fragment.last) {
            more = false;
        }
    }

    return ConnectionStatus::Ok;
}
#endif

} // namespace connect_client
