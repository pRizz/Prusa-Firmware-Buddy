#include "server.h"

#include <algorithm>
#include <cassert>
#include <lwip/sys.h>
#include <lwip/tcpip.h>

namespace nhttp {

using handler::Idle;
using std::holds_alternative;

void Server::InactivityTimeout::schedule(uint32_t after) {
    last_activity = sys_now();
    quants_left = (after + INACTIVITY_TIME_QUANT - 1) / INACTIVITY_TIME_QUANT;
    assert(!past());
}

void Server::InactivityTimeout::poll_inactivity() {
    uint32_t now = sys_now();
    uint32_t since_activity = now - last_activity;
    if (quants_left > 0 && since_activity >= INACTIVITY_TIME_QUANT) {
        quants_left--;
    }
}

bool Server::InactivityTimeout::past() const {
    return quants_left == 0;
}

void Server::ConnectionSlot::release_buffer() {
    if (buffer) {
        buffer->reset();
        buffer = nullptr;
    }
}

void Server::ConnectionSlot::release_partial() {
    if (partial) {
        if (conn != nullptr) {
            altcp_recved(conn, partial->tot_len);
        }
        partial.reset();
    }
    partial_consumed = 0;
}

uint16_t Server::ConnectionSlot::send_space() const {
    if (conn) {
        return std::min(altcp_mss(conn), altcp_sndbuf(conn));
    }
    return 0;
}

bool Server::ConnectionSlot::has_unacked_data() const {
    return buffer != nullptr;
}

bool Server::ConnectionSlot::want_read() const {
    return std::visit([](const auto &phase) -> bool { return phase.want_read(); }, state);
}

bool Server::ConnectionSlot::want_write() const {
    return std::visit([](const auto &phase) -> bool { return phase.want_write(); }, state);
}

bool Server::Slot::close() {
    assert(conn);
    Server::remove_callbacks(conn);
    if (altcp_close(conn) == ERR_OK) {
        release();
        return true;
    }

    Server::set_callbacks(conn, this);
    return false;
}

void Server::Slot::release() {
    conn = nullptr;
}

void Server::Slot::forward_progress() {
    while (step()) {
    }
}

void Server::ConnectionSlot::release() {
    state = Idle();
    release_partial();
    release_buffer();
    client_closed = false;
    Slot::release();
    server->try_send_transfer_response(this);
}

bool Server::ConnectionSlot::is_empty() const {
    return holds_alternative<Idle>(state);
}

bool Server::ConnectionSlot::take_pbuf(pbuf *data) {
    if (!data) {
        client_closed = true;
    }

    if (partial) {
        return false;
    }

    assert(partial_consumed == 0);
    if (data) {
        partial.reset(data);
    }

    return true;
}

Server::Server(const ServerDefs &defs)
    : defs(defs) {
    for (auto &slot : idle_slots) {
        slot.server = this;
    }
    for (auto &slot : active_slots) {
        slot.server = this;
    }
    transfer_slot.server = this;
}

err_t Server::accept_wrap(void *me, struct altcp_pcb *new_conn, err_t err) {
    return static_cast<Server *>(me)->accept(new_conn, err);
}

err_t Server::accept(altcp_pcb *new_conn, err_t err) {
    if ((err != ERR_OK) || (new_conn == nullptr)) {
        return ERR_VAL;
    }

    set_callbacks(new_conn, idle_slots.begin());
    altcp_setprio(new_conn, IDLE_PRIO);
    altcp_nagle_disable(new_conn);
    return ERR_OK;
}

void Server::set_callbacks(altcp_pcb *conn, BaseSlot *slot) {
    altcp_err(conn, lost_conn_wrap);
    altcp_poll(conn, idle_conn_wrap, POLL_TIME);
    altcp_recv(conn, received_wrap);
    altcp_sent(conn, sent_wrap);
    altcp_arg(conn, slot);
    slot->server->activity(conn, slot);
}

void Server::remove_callbacks(altcp_pcb *conn) {
    altcp_err(conn, nullptr);
    altcp_poll(conn, nullptr, 0);
    altcp_recv(conn, nullptr);
    altcp_sent(conn, nullptr);
    altcp_arg(conn, nullptr);
}

void Server::lost_conn_wrap(void *slot, err_t) {
    if (is_active_slot(slot)) {
        static_cast<Slot *>(slot)->release();
    }
}

err_t Server::idle_conn_wrap(void *slot, altcp_pcb *conn) {
    BaseSlot *base_slot = static_cast<BaseSlot *>(slot);
    if (base_slot->get_slot_type() == BaseSlot::SlotType::TransferSlot) {
        TransferSlot *transfer_slot = static_cast<TransferSlot *>(slot);
        transfer_slot->forward_progress();

        if (transfer_slot->pbuf_queue_size > 0) {
            return ERR_OK;
        }
    }
    base_slot->timeout.poll_inactivity();
    if (!base_slot->timeout.past()) {
        return ERR_OK;
    }

    bool send_goodbye = false;
    bool has_unacked_data = false;
    Slot *active_slot = nullptr;
    if (is_active_slot(slot)) {
        active_slot = static_cast<Slot *>(slot);
        send_goodbye = active_slot->want_read();
        has_unacked_data = active_slot->has_unacked_data();
    }
    lost_conn_wrap(slot, ERR_OK);
    if (conn != nullptr) {
        if (send_goodbye) {
            static const char goodbye[] = "HTTP/1.1 408 Request Timeout\r\n\r\n";
            altcp_write(conn, goodbye, sizeof(goodbye), 0);
            altcp_output(conn);
        }
        remove_callbacks(conn);
        if (active_slot != nullptr) {
            active_slot->release();
        }
        if (has_unacked_data || altcp_close(conn) != ERR_OK) {
            altcp_abort(conn);
            return ERR_ABRT;
        }
    }

    return ERR_OK;
}

err_t Server::received_wrap(void *raw_slot, struct altcp_pcb *conn, pbuf *data, [[maybe_unused]] err_t err) {
    assert(raw_slot != nullptr);
    assert(conn != nullptr);

    BaseSlot *base_slot = static_cast<BaseSlot *>(raw_slot);
    if (!is_active_slot(base_slot)) {
        if (data == nullptr) {
            remove_callbacks(conn);
            if (altcp_close(conn) == ERR_OK) {
                return ERR_OK;
            }
            altcp_abort(conn);
            return ERR_ABRT;
        }

        if (ConnectionSlot *active_slot = base_slot->server->find_empty_slot(); active_slot != nullptr) {
            assert(!active_slot->partial);
            assert(active_slot->partial_consumed == 0);
            assert(!active_slot->buffer);
            assert(holds_alternative<Idle>(active_slot->state));

            active_slot->state.emplace<handler::RequestParser>(*active_slot->server);
            active_slot->conn = conn;
            altcp_arg(conn, active_slot);
            base_slot = active_slot;
            altcp_setprio(conn, ACTIVE_PRIO);
        } else {
            return ERR_MEM;
        }
    }

    assert(is_active_slot(base_slot));
    Slot *slot = static_cast<Slot *>(base_slot);
    slot->server->activity(conn, slot);

    if (!slot->take_pbuf(data)) {
        return ERR_MEM;
    }

    slot->forward_progress();
    return ERR_OK;
}

err_t Server::sent_wrap(void *raw_slot, altcp_pcb *conn, uint16_t len) {
    if (is_active_slot(raw_slot)) {
        Slot *slot = static_cast<Slot *>(raw_slot);
        slot->server->sent(slot, len);
        slot->server->activity(conn, slot);
    }
    return ERR_OK;
}

void Server::ConnectionSlot::sent(uint16_t len) {
    assert(buffer != nullptr);
    assert(buffer->write_pos >= buffer->acked);
    const uint16_t unacked = buffer->write_pos - buffer->acked;
    assert(len <= unacked);
    (void)unacked;
    buffer->acked += len;
}

void Server::sent(Slot *slot, uint16_t len) {
    slot->sent(len);
    step();
}

void Server::step() {
    const uint8_t count = active_slots.size();
    for (uint8_t sleeping_slots = 0, index = (last_active_slot + 1) % count; sleeping_slots < count; index = (index + 1) % count) {
        if (active_slots[index].step()) {
            last_active_slot = index;
            sleeping_slots = 0;
        } else {
            sleeping_slots += 1;
        }
    }
    transfer_slot.forward_progress();
}

bool Server::is_active_slot(void *slot) {
    if (!slot) {
        return false;
    }

    BaseSlot *base_slot = static_cast<BaseSlot *>(slot);
    return base_slot->get_slot_type() == BaseSlot::SlotType::ConnectionSlot || base_slot->get_slot_type() == BaseSlot::SlotType::TransferSlot;
}

void Server::activity(altcp_pcb *conn, BaseSlot *slot) {
    if (is_active_slot(slot)) {
        slot->timeout.schedule(ACTIVE_TIMEOUT);
        return;
    }

    const uint32_t now = sys_now();
    const size_t slot_id = (now / IDLE_TIMEOUT) % slot->server->idle_slots.size();
    slot = &slot->server->idle_slots[slot_id];
    slot->timeout.schedule(IDLE_TIMEOUT);
    altcp_arg(conn, slot);
}

Server::ConnectionSlot *Server::find_empty_slot() {
    for (auto &slot : active_slots) {
        if (slot.is_empty()) {
            return &slot;
        }
    }
    return nullptr;
}

Server::Buffer *Server::find_empty_buffer() {
    for (auto &buffer : buffers) {
        if (!buffer.owned) {
            return &buffer;
        }
    }
    return nullptr;
}

bool Server::start() {
    if (listener) {
        return true;
    }

    LOCK_TCPIP_CORE();
    listener.reset(defs.listener_alloc());
    if (!listener) {
        UNLOCK_TCPIP_CORE();
        return false;
    }

    altcp_arg(listener.get(), this);
    altcp_accept(listener.get(), Server::accept_wrap);
    UNLOCK_TCPIP_CORE();
    return true;
}

void Server::stop() {
    listener.reset();
}

} // namespace nhttp
