#include "marlin_server_internal.hpp"

using namespace ExtUI;

LOG_COMPONENT_DEF(MarlinServer, logging::Severity::info);

namespace marlin_server {

CallbackHookPoint<> idle_hook_point;

namespace internal {
    ServerState server {};
    PrintState print_state {};
    fsm::States fsm_states;
} // namespace internal

using namespace internal;

bool printer_idle() {
    return server.print_state == State::Idle
        || server.print_state == State::Paused
        || server.print_state == State::Aborted
        || server.print_state == State::Finished
        || server.print_state == State::Exit;
}

bool print_preview() {
    return server.print_state == State::PrintPreviewInit
        || server.print_state == State::PrintPreviewImage
        || server.print_state == State::PrintPreviewConfirmed
        || server.print_state == State::PrintPreviewQuestions
#if HAS_TOOLCHANGER() || HAS_MMU2()
        || server.print_state == State::PrintPreviewToolsMapping
#endif
        || server.print_state == State::WaitGui;
}

bool is_printing() {
    switch (marlin_vars().print_state) {
    case State::Aborted:
    case State::Idle:
    case State::Finished:
    case State::PrintPreviewInit:
    case State::PrintPreviewImage:
#if HAS_TOOLCHANGER() || HAS_MMU2()
    case State::PrintPreviewToolsMapping:
#endif
        return false;
    default:
        return true;
    }
}

bool is_processing() {
    return queue.has_commands_queued()
        || planner.processing()
        || gcode.busy_state != GcodeSuite::NOT_BUSY // We might be still in the gcode (while no commands are queued)
#if HAS_SELFTEST()
        || SelftestInstance().IsInProgress() // Some selftests are still not gcodes :(
#endif
        || !inject_queue.is_empty() //
        ;
}

bool aborting_or_aborted() {
    return (server.print_state >= State::Aborting_Begin && server.print_state <= State::Aborted);
}

bool finishing_or_finished() {
    switch (server.print_state) {
    case State::Finishing_UnloadFilament:
    case State::Finishing_ParkHead:
    case State::Finished:
        return true;

        // ! WaitIdle means the printer is waiting for the queued gcodes to finish, so it's still a printing state!
    case State::Finishing_WaitIdle:
    default:
        return false;
    }
}

bool printer_paused() {
    return server.print_state == State::Paused;
}

// Printer is paused, parking for pause, resuming from pause...
bool printer_paused_extended() {
    return is_extended_paused_state(server.print_state);
}

void serial_print_start() {
    server.print_state = State::SerialPrintInit;
    print_state = {};
}

void retract() {
#if HAS_AUTO_RETRACT()
    if (buddy::auto_retract().will_deretract()) {
        // Filament is already retracted, don't retact it more
        return;
    }
#endif

// server.motion_param.save_reset();  // TODO: currently disabled (see Crash_s::save_parameters())
#if ENABLED(ADVANCED_PAUSE_FEATURE)
    float mm = PAUSE_PARK_RETRACT_LENGTH / planner.e_factor[active_extruder];
    plan_move_by(PAUSE_PARK_RETRACT_FEEDRATE, 0, 0, 0, -mm);
#endif // ENABLED(ADVANCED_PAUSE_FEATURE)
}

void lift_head() {
    const float distance = std::min<float>(
                               std::max<float>({
                                   Z_NOZZLE_PARK_RISE + std::max(current_position.z, planner.max_printed_z),
#ifdef Z_NOZZLE_PARK_POINT_MIN
                                   Z_NOZZLE_PARK_POINT_MIN,
#endif
                               }),
                               Z_MAX_POS)
        - current_position.z;
    static_assert(Z_NOZZLE_PARK_POINT > 0);

    if (axes_home_level.is_homed(Z_AXIS, AxisHomeLevel::imprecise)) {
        // Do prepare_move_to_destination, as it segments the move and thus allows better emergency_stop
        AutoRestore _ar(feedrate_mm_s, MMM_TO_MMS(HOMING_FEEDRATE_INVERTED_Z));
        destination = current_position;
        destination.z += distance;
        prepare_move_to_destination({});
        planner.synchronize();

    } else {
        // If the Z is not homed, do a "homing" move with quickstops that will stop as soon as we hit the limits
        TemporaryGlobalEndstopsState _es(true);

        auto cpz = current_position.z;

        // do_homing_move does not update current position, we have to do it manually
        // have to use HOMING_FEEDRATE, otherwise the stallguards might not trigger
        if (do_homing_move(Z_AXIS, distance, MMM_TO_MMS(HOMING_FEEDRATE_INVERTED_Z))) {
            current_position.z = Z_MAX_POS;
        } else {
            // BFW-7734 but sometimes it zeroes Z - this is to prevent ceiling hit tests from triggering in such a case
            current_position.z = cpz + distance;
        }
        sync_plan_position();
    }
}

void park_head() {
    server.resume.pos = current_position;
    retract();
    lift_head();

    if (!all_axes_homed()) {
        return;
    }

#if HAS_TOOLCHANGER()
    // Check that we are not in dock
    // Can happen if stopped during toolchanging, toolchange will finish but last move doesn't wait for planner.synchronize();
    if (current_position.y > PrusaToolChanger::SAFE_Y_WITH_TOOL) {
        current_position.y = PrusaToolChanger::SAFE_Y_WITH_TOOL;
        line_to_current_position(NOZZLE_PARK_XY_FEEDRATE); // Move to safe Y
        planner.synchronize();
    }
#endif /*HAS_TOOLCHANGER()*/

    xyz_pos_t park = XYZ_NOZZLE_PARK_POINT_ON_PRINT_END;
    park.z = current_position.z;
    plan_park_move_to_xyz(park, NOZZLE_PARK_XY_FEEDRATE, NOZZLE_PARK_Z_FEEDRATE, Segmented::yes);
}

void unpark_head_XY(void) {
    // TODO: double check this condition: when recovering from a crash, Z is not known, but we *can*
    // unpark, so we bypass this check as we need to move back
    if (TERN1(CRASH_RECOVERY, !crash_s.did_trigger()) && !all_axes_homed()) {
        return;
    }

    current_position.x = server.resume.pos.x;
    current_position.y = server.resume.pos.y;
    NOMORE(current_position.y, Y_BED_SIZE); // Prevent crashing into parked tools
    line_to_current_position(NOZZLE_PARK_XY_FEEDRATE);
}

void unpark_head_ZE(void) {
    // TODO: see comment above on unparking: if axes are not known, lift is skipped, but not this
    if (!all_axes_homed()) {
        return;
    }

    // Move Z
    destination = current_position;
    destination.z = server.resume.pos.z;
    prepare_internal_move_to_destination(NOZZLE_PARK_Z_FEEDRATE);

#if ENABLED(ADVANCED_PAUSE_FEATURE)
    // Undo E retract
    plan_move_by(PAUSE_PARK_RETRACT_FEEDRATE, 0, 0, 0, server.resume.pos.e - current_position.e);
#endif // ENABLED(ADVANCED_PAUSE_FEATURE)
}

bool all_axes_homed(void) {
    return ::all_axes_homed();
}

bool all_axes_known(void) {
    return ::all_axes_known();
}

int get_exclusive_mode(void) {
    return (server.flags & MARLIN_SFLG_EXCMODE) ? 1 : 0;
}

void set_exclusive_mode(int exclusive) {
    if (exclusive) {
        SerialUSB.setIsWriteOnly(true);
        server.flags |= MARLIN_SFLG_EXCMODE; // enter exclusive mode
    } else {
        server.flags &= ~MARLIN_SFLG_EXCMODE; // exit exclusive mode
        SerialUSB.setIsWriteOnly(false);
    }
}

void set_target_bed(float value) {
    marlin_vars().target_bed = value;
    thermalManager.setTargetBed(value);
}

void set_temp_to_display(float value, uint8_t extruder) {
    marlin_vars().hotend(extruder).display_nozzle = value;
}

bool get_media_inserted(void) {
    return marlin_vars().media_inserted;
}

resume_state_t *get_resume_data() {
    return &server.resume;
}

void set_resume_data(const resume_state_t *data) {
    // ensure this is called only from the marlin thread
    assert(osThreadGetId() == server_task);
    server.resume = *data;
}

int32_t get_knob_position() {
    return server.knob_position;
}

} // namespace marlin_server

#if _DEBUG
void marlin_server_steppers_timeout_warning() {
    marlin_server::set_warning(WarningType::SteppersTimeout);
}
#endif

alignas(std::max_align_t) uint8_t FSMExtendedDataManager::extended_data_buffer[FSMExtendedDataManager::buffer_size] = { 0 };
size_t FSMExtendedDataManager::identifier = { 0 };

void marlin_server::request_calibrations_screen() {
    internal::send_notify_event(marlin_server::Event::RequestCalibrationsScreen, 0, 0);
}
