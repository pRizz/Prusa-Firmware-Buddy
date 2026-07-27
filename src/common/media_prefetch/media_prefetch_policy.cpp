#include "media_prefetch.hpp"

#include <cassert>

bool MediaPrefetchManager::check_buffer_empty() const {
    std::lock_guard mutex_guard(mutex);
    return (shared_state.read_head.buffer_pos == shared_state.read_tail.buffer_pos) && (shared_state.read_tail.status == Status::end_of_buffer);
}

MediaPrefetchManager::ReadyToStartPrintResult MediaPrefetchManager::check_ready_to_start_print() const {
    const auto metrics = get_metrics();

    if (metrics.buffer_occupancy_percent > 90) {
        return ReadyToStartPrintResult::ready;
    }

    switch (metrics.tail_status) {
    case Status::ok:
    case Status::end_of_buffer:
    case Status::not_downloaded:
        return ReadyToStartPrintResult::needs_fetching;

    case Status::end_of_file:
        return ReadyToStartPrintResult::ready;

    case Status::corruption:
    case Status::usb_error:
        return ReadyToStartPrintResult::error;
    }

    return ReadyToStartPrintResult::error;
}

MediaPrefetchManager::Metrics MediaPrefetchManager::get_metrics() const {
    std::lock_guard mutex_guard(mutex);
    const auto &state = shared_state;
    return Metrics {
        .commands_in_buffer = state.commands_in_buffer,
        .stream_size_estimate = state.stream_size_estimate,
        .buffer_occupancy_percent = static_cast<uint8_t>(((state.read_tail.buffer_pos - state.read_head.buffer_pos + buffer_size) % buffer_size * 100) / buffer_size),
        .tail_status = state.read_tail.status,
        .is_fetching = worker_job.is_active(),
    };
}

bool MediaPrefetchManager::can_read_entry_raw(size_t bytes) const {
    assert(bytes < buffer_size);

    const size_t read_pos = shared_state.read_head.buffer_pos;
    const size_t read_tail = shared_state.read_tail.buffer_pos;
    const size_t new_read_pos = (read_pos + bytes) % buffer_size;

    const bool does_wrap = new_read_pos < read_pos;
    // Readers may catch the tail exactly; only crossing it would consume unwritten data.
    const bool does_cross_tail = (read_pos <= read_tail) != (new_read_pos <= read_tail);

    return does_cross_tail == does_wrap;
}

bool MediaPrefetchManager::can_write_entry_raw(size_t bytes) const {
    assert(bytes < buffer_size);

    const size_t write_pos = worker_state.write_tail.buffer_pos;
    const size_t new_write_pos = (write_pos + bytes) % buffer_size;
    const size_t read_head = worker_state.read_head.buffer_pos;

    const bool does_wrap = new_write_pos < write_pos;
    // Writers must not catch the head because equal positions represent an empty buffer.
    const bool does_catch_up_read_head = (write_pos < read_head) != (new_write_pos < read_head);

    return does_catch_up_read_head == does_wrap;
}
