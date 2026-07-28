#include "marlin_server_internal.hpp"

using namespace ExtUI;

LOG_COMPONENT_REF(MarlinServer);

namespace marlin_server {
using namespace internal;

RequestQueue request_queue;
std::atomic<uint32_t> request_flags = 0;
static_assert(std::to_underlying(RequestFlag::_cnt) <= 32, "There are more flags than bits");

static void server_set_var(const Request &request);

void do_babystep_Z(float offs) {
    babystep.add_steps(Z_AXIS, std::round(offs * planner.settings.axis_steps_per_mm[Z_AXIS]));
}

extern void move_axis(float pos, float feedrate, size_t axis) {
    current_position[axis] = pos;
    line_to_current_position(feedrate);
}

void move_xyz_axes_to(xyz_float_t position, float feedrate) {
    current_position = position;
    line_to_current_position(feedrate);
}

void enqueue_gcode(const char *gcode) {
    if (!queue.enqueue_one(gcode)) {
        bsod("enqueue_gcode failed");
    }
}

[[nodiscard]] bool enqueue_gcode_try(const char *gcode) {
    return queue.enqueue_one(gcode);
}

void enqueue_gcode_printf(const char *gcode, ...) {
    ArrayStringBuilder<MARLIN_MAX_REQUEST> request;
    {
        va_list ap;
        va_start(ap, gcode);
        request.append_vprintf(gcode, ap);
        va_end(ap);
    }
    enqueue_gcode(request.str());
}

bool inject(InjectQueueRecord record) {
    if (!queue.inject(record)) {
        // TODO: If requested, figure out thread-safe way to call Sound_Play(eSOUND_TYPE::SingleBeepAlwaysLoud);
        return false;
    }
    return true;
}

#if HAS_SELFTEST()
void test_start([[maybe_unused]] const uint64_t test_mask, [[maybe_unused]] const selftest::TestData test_data) {
    if (((server.print_state == State::Idle) || (server.print_state == State::Finished) || (server.print_state == State::Aborted)) && (!SelftestInstance().IsInProgress())) {
        SelftestInstance().Start(test_mask, test_data);
    }
}

void test_abort() {
    if (SelftestInstance().IsInProgress()) {
        SelftestInstance().Abort();
    }
}
#endif

void quick_stop() {
#if HAS_TOOLCHANGER()
    prusa_toolchanger.quick_stop();
#endif
    planner.quick_stop();
    disable_all_steppers();
    set_all_unhomed();
    server.flags |= MARLIN_SFLG_STOPPED;
}

void internal::server_update_vars_now() {
    const auto prefetch_metrics = media_prefetch.get_metrics();

    marlin_vars().gqueue = queue.length;
    marlin_vars().inject_queue_empty = inject_queue.is_empty();
    marlin_vars().is_processing = is_processing();

    // Get native position
    xyze_pos_t pos_mm, curr_pos_mm;
    planner.get_axis_position_mm(pos_mm);
    curr_pos_mm = current_position;
    LOOP_XYZE(i) {
        marlin_vars().native_pos[i] = pos_mm[i];
        marlin_vars().native_curr_pos[i] = curr_pos_mm[i];
    }
    // Convert to logical position
    planner.unapply_leveling(pos_mm);
    toLogical(pos_mm);
    toLogical(curr_pos_mm);
    LOOP_XYZE(i) {
        marlin_vars().logical_pos[i] = pos_mm[i];
        marlin_vars().logical_curr_pos[i] = curr_pos_mm[i];
    }

    HOTEND_LOOP() {
        auto &extruder = marlin_vars().hotend(e);

        extruder.temp_nozzle = thermalManager.degHotend(e);
        extruder.target_nozzle = thermalManager.degTargetHotend(e);
        extruder.pwm_nozzle = thermalManager.getHeaterPower(static_cast<heater_ind_t>(H_E0 + e));

#if (TEMP_SENSOR_HEATBREAK > 0)
        // TODO: this should track multiple extruders
        extruder.temp_heatbreak = thermalManager.temp_heatbreak[e].celsius;
        extruder.target_heatbreak = thermalManager.temp_heatbreak[e].target;
#endif
        extruder.flow_factor = static_cast<uint16_t>(planner.flow_percentage[e]);
        extruder.print_fan_rpm = Fans::print(e).get_actual_rpm();
        extruder.heatbreak_fan_rpm = Fans::heat_break(e).get_actual_rpm();
    }

    marlin_vars().temp_bed = thermalManager.degBed();
    marlin_vars().target_bed = thermalManager.degTargetBed();
#if HAS_MODULAR_BED()
    marlin_vars().enabled_bedlet_mask = thermalManager.getEnabledBedletMask();
#endif

    marlin_vars().z_offset = probe_offset.z;
#if FAN_COUNT > 0
    marlin_vars().print_fan_speed = thermalManager.fan_speed[0];
#endif
    marlin_vars().print_speed = static_cast<uint16_t>(feedrate_percentage);

    auto progress_data = oProgressData.mode_specific(config_store().stealth_mode.get());

    // If the mode-specific progress data is all empty (never set by the M73 command),
    // fall back to standard mode progress data to show at least something
    if (!progress_data.percent_done.mIsUsed() && !progress_data.time_to_end.mIsUsed() && !progress_data.time_to_pause.mIsUsed()) {
        progress_data = oProgressData.standard_mode;
    }

    marlin_vars().print_duration = print_job_timer.duration();
    marlin_vars().sd_percent_done = [&]() -> uint8_t {
        if (progress_data.percent_done.mIsActual(marlin_vars().print_duration)) {
            return static_cast<uint8_t>(progress_data.percent_done.mGetValue());
        } else if (prefetch_metrics.stream_size_estimate > 0) {
            return std::min<uint8_t>(std::round(100.0f * queue.last_executed_sdpos / prefetch_metrics.stream_size_estimate), 99);
        } else {
            return 0;
        }
    }();

    if (const bool media = usb_host::is_media_inserted(); marlin_vars().media_inserted != media) {
        marlin_vars().media_inserted = media;
        send_notify_event(marlin_vars().media_inserted ? Event::MediaInserted : Event::MediaRemoved, 0, 0);
    }

    const auto duration = marlin_vars().print_duration.get();
    const auto print_speed = marlin_vars().print_speed.get();

    const auto update_time_to = [&](const ClValidityValueSec &progress_data_value, MarlinVariable<uint32_t> &marlin_var) {
        uint32_t v = TIME_TO_END_INVALID;
        if (progress_data.percent_done.mIsActual(duration) && progress_data_value.mIsActual(duration)) {
            v = progress_data_value.mGetValue();
        }

        if (print_speed == 100 || v == TIME_TO_END_INVALID) {
            marlin_var = v;
        } else {
            // multiply by 100 is safe, it limits time_to_end to ~21mil. seconds (248 days)
            marlin_var = (v * 100) / print_speed;
        }
    };
    update_time_to(progress_data.time_to_end, marlin_vars().time_to_end);
    update_time_to(progress_data.time_to_pause, marlin_vars().time_to_pause);

    if (server.print_state == State::Printing) {
        marlin_vars().time_to_end.execute_with([&](const uint32_t &time_to_end) {
            if (time_to_end != TIME_TO_END_INVALID) {
                marlin_vars().print_end_time = time(nullptr) + time_to_end;
            } else {
                marlin_vars().print_end_time = TIMESTAMP_INVALID;
            }
        });
    }

    marlin_vars().job_id = job_id;
    marlin_vars().travel_acceleration = planner.settings.travel_acceleration;
    marlin_vars().max_printed_z = planner.max_printed_z;

    uint8_t mmu2State =
#if HAS_MMU2()
        uint8_t(MMU2::mmu2.State());
#else
        0;
#endif
    marlin_vars().mmu2_state = mmu2State;

    bool mmu2FindaPressed =
#if HAS_MMU2()
        MMU2::mmu2.FindaDetectsFilament();
#else
        false;
#endif

    marlin_vars().mmu2_finda = mmu2FindaPressed;

    marlin_vars().active_extruder = active_extruder;

#if ENABLED(PREVENT_COLD_EXTRUSION)
    marlin_vars().extrude_min_temp = thermalManager.extrude_min_temp;
    marlin_vars().allow_cold_extrude = thermalManager.allow_cold_extrude;
#endif /* ENABLED(PREVENT_COLD_EXTRUSION) */

    // print state is updated last, to make sure other related variables (like job_id, filenames) are already set when we start print
    marlin_vars().print_state = static_cast<State>(server.print_state);

    marlin_vars().media_position = media_position();

    marlin_vars().media_size_estimate = prefetch_metrics.stream_size_estimate;
}

bool process_server_valid_request(const Request &request, int client_id) {
    switch (request.type) {
    case Request::Type::Gcode:
        //@TODO return value depending on success of enqueueing gcode
        return enqueue_gcode_try(request.gcode);
    case Request::Type::Inject:
        inject(request.inject);
        return true;
    case Request::Type::SetVariable:
        server_set_var(request);
        return true;
    case Request::Type::Babystep:
        do_babystep_Z(request.babystep);
        return true;
#if HAS_CANCEL_OBJECT()
    case Request::Type::CancelObjectID:
    case Request::Type::UncancelObjectID:
        buddy::cancel_object().set_object_cancelled(request.cancel_object_id, request.type == Request::Type::CancelObjectID);
        return true;
#else
    case Request::Type::CancelObjectID:
    case Request::Type::UncancelObjectID:
        return false;
#endif
    case Request::Type::PrintStart:
        print_start(request.print_start.filename, GCodeReaderPosition(), request.print_start.skip_preview);
        return true;
    case Request::Type::SetWarning:
        set_warning(request.warning_type);
        return true;
    case Request::Type::EventMask:
        server.notify_events[client_id] = request.event_mask;
        // Send Event::MediaInserted event if media currently inserted
        // This is temporary solution, Event::MediaInserted and Event::MediaRemoved events are replaced
        // with variable media_inserted, but some parts of application still using the events.
        // We need this workaround for app startup.
        if ((server.notify_events[client_id] & make_mask(Event::MediaInserted)) && marlin_vars().media_inserted) {
            server.client_events[client_id] |= make_mask(Event::MediaInserted);
        }
        return true;
#if HAS_SELFTEST()
    case Request::Type::TestStart:
        marlin_server::test_start(
            request.test_start.test_mask,
            selftest::deserialize_test_data_from_int(request.test_start.test_data_index, request.test_start.test_data_data));
        return true;
#else
        return false;
#endif
    }
    bsod("Unknown request %d", std::to_underlying(request.type));
}

void send_request_flag(const RequestFlag request) {

    // These requests shouldn't be called at once (in single step of marlin_server's cycle)
    static constexpr uint32_t exclusive_print_request_mask = (0x1 << std::to_underlying(RequestFlag::PrintResume)) | (0x1 << std::to_underlying(RequestFlag::PrintPause)) | (0x1 << std::to_underlying(RequestFlag::PrintAbort));
    const uint32_t curr_request_flag = 0x1 << std::to_underlying(request);

    uint32_t flags = request_flags.load();
    uint32_t new_flags;

    do {
        new_flags = flags;
        // Clear exclusive print flags if set
        if (curr_request_flag & exclusive_print_request_mask) {
            new_flags &= ~exclusive_print_request_mask;
        }
        new_flags |= curr_request_flag;
    } while (!request_flags.compare_exchange_strong(flags, new_flags));
}

void internal::process_request_flags() {
    const uint32_t flags = request_flags.exchange(0);
    if (flags == 0) {
        return;
    }

    for (uint8_t i = 0; i < std::to_underlying(RequestFlag::_cnt); i++) {
        if (!(flags & (0x1 << i))) {
            continue;
        }

        switch (RequestFlag(i)) {
        case RequestFlag::PrintReady:
            gui_ready_to_print();
            break;
        case RequestFlag::PrintAbort:
            print_abort();
            break;
        case RequestFlag::PrintPause:
            print_pause();
            break;
        case RequestFlag::PrintResume:
            print_resume();
            break;
        case RequestFlag::TryRecoverFromMediaError:
            try_recover_from_media_error();
            break;
        case RequestFlag::PrintExit:
            print_exit();
            break;
        case RequestFlag::KnobMoveUp:
            buddy::safety_timer().reset_norestore();
            server.knob_position++;
            break;
        case RequestFlag::KnobMoveDown:
            buddy::safety_timer().reset_norestore();
            server.knob_position--;
            break;
        case RequestFlag::KnobClick:
            buddy::safety_timer().reset_restore_nonblocking();
            break;
        case RequestFlag::GuiCantPrint:
            gui_cant_print();
            break;
#if HAS_SELFTEST()
        case RequestFlag::TestAbort:
            test_abort();
            break;
#endif
#if HAS_CANCEL_OBJECT()
        case RequestFlag::CancelCurrentObject:
            buddy::cancel_object().set_object_cancelled(buddy::cancel_object().current_object(), true);
            break;
#endif
        case RequestFlag::_cnt:
            break;
        }
    }
}

bool internal::process_server_request(const Request &request) {
    const uint8_t client_id = request.client_id;
    if (client_id >= MARLIN_MAX_CLIENTS) {
        return true;
    }

    const bool processed = process_server_valid_request(request, client_id);

    // force update of marlin variables after proecssing request -> to ensure client can read latest variables after request completion
    server_update_vars_now();

    if (request.response_required) {
        Event evt_result = processed ? Event::Acknowledge : Event::NotAcknowledge;
        if (!send_notify_event_to_client(client_id, marlin_client::marlin_client_queue[client_id], evt_result, 0, 0)) {
            // FIXME: Take care of resending process elsewhere.
            server.client_events[client_id] |= make_mask(evt_result); // set bit if notification not sent
        }
    }
    return processed;
}

// set variable from string request
static void server_set_var(const Request &request) {
    const uintptr_t variable_identifier = request.set_variable.variable;

    // Set normal (non-extruder) variables
    if (variable_identifier == reinterpret_cast<uintptr_t>(&marlin_vars().target_bed)) {
        marlin_vars().target_bed = request.set_variable.float_value;
        thermalManager.setTargetBed(marlin_vars().target_bed);
        return;
    }
    if (variable_identifier == reinterpret_cast<uintptr_t>(&marlin_vars().z_offset)) {
        marlin_vars().z_offset = request.set_variable.float_value;
#if HAS_BED_PROBE
        probe_offset.z = marlin_vars().z_offset;
#endif // HAS_BED_PROBE
        return;
    }
    if (variable_identifier == reinterpret_cast<uintptr_t>(&marlin_vars().print_fan_speed)) {
        marlin_vars().print_fan_speed = request.set_variable.uint32_value;
#if FAN_COUNT > 0
        thermalManager.set_fan_speed(0, marlin_vars().print_fan_speed);
#endif
        return;
    }
    if (variable_identifier == reinterpret_cast<uintptr_t>(&marlin_vars().print_speed)) {
        marlin_vars().print_speed = request.set_variable.uint32_value;
        feedrate_percentage = (int16_t)marlin_vars().print_speed;
        return;
    }
    if (variable_identifier == reinterpret_cast<uintptr_t>(&marlin_vars().fan_check_enabled)) {
        marlin_vars().fan_check_enabled = request.set_variable.uint32_value;
        return;
    }

    // Now see if extruder variable is set
    HOTEND_LOOP() {
        auto &extruder = marlin_vars().hotend(e);
        if (reinterpret_cast<uintptr_t>(&extruder.target_nozzle) == variable_identifier) {
            extruder.target_nozzle = request.set_variable.float_value;
            thermalManager.setTargetHotend(extruder.target_nozzle, e);
            return;
        } else if (reinterpret_cast<uintptr_t>(&extruder.flow_factor) == variable_identifier) {
            extruder.flow_factor = request.set_variable.uint32_value;
            planner.flow_percentage[e] = (int16_t)extruder.flow_factor;
            planner.refresh_e_factor(e);
            return;
        } else if (reinterpret_cast<uintptr_t>(&extruder.display_nozzle) == variable_identifier) {
            extruder.display_nozzle = request.set_variable.float_value;
            return;
        }
    }

    // if we got here, no variable was set, return error
    bsod("unimplemented server_set_var for var_id %i", (int)variable_identifier);
}

} // namespace marlin_server
