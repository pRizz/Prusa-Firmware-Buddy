#include "marlin_server_internal.hpp"

using namespace ExtUI;

LOG_COMPONENT_REF(MarlinServer);

namespace marlin_server {
using namespace internal;

void internal::pause_print(PauseType type) {
    if (!server.print_is_serial) {
        switch (type) {

        case PauseType::Crash:
            print_state.skip_gcode = false;
            break;

        case PauseType::Pause:
            print_state.skip_gcode = true;
            break;
        }

        media_prefetch.stop();
        queue.clear();
        log_debug(MarlinServer, "Paused at %" PRIu32 ", skip %i", media_position(), print_state.skip_gcode);
    }

    SerialPrinting::pause();

    print_job_timer.pause();
    server.resume.nozzle_temp = buddy::safety_timer().original_hotend_targets();
    server.resume.fan_speed = marlin_vars().print_fan_speed; // save fan speed
    server.resume.print_speed = marlin_vars().print_speed;
#if FAN_COUNT > 0
    if (consume_postponed_full_fan()) {
        thermalManager.set_fan_speed(0, 255);
    } else {
        thermalManager.set_fan_speed(0, 0); // disable print fan
    }
#endif
}
#if ENABLED(CRASH_RECOVERY)
/**
 * @brief Go to homing or measure axis and follow with homing.
 */
void internal::measure_axes_and_home() {
    #if ENABLED(AXIS_MEASURE)
    if (crash_s.is_repeated_crash()) {
        // Measure axes
        enqueue_gcode("G163 X Y S" STRINGIFY(AXIS_MEASURE_STALL_GUARD) " P" STRINGIFY(AXIS_MEASURE_CRASH_PERIOD));
        server.print_state = State::CrashRecovery_XY_Measure;
        return;
    }
    #endif

    // Homing
    set_axis_is_not_at_home(X_AXIS);
    set_axis_is_not_at_home(Y_AXIS);
    server.print_state = State::CrashRecovery_XY_HOME;
}

    #if HAS_TOOLCHANGER()
/**
 * @brief Deselect tool, disable XY steppers and switch to Tool_Pickup server print_state.
 */
static void prepare_tool_pickup() {
    prusa_toolchanger.crash_deselect_dwarf(); // Deselect dwarf as if all were parked
    disable_XY(); // Let user move the carriage

    // Disable heaters
    HOTEND_LOOP() {
        if ((marlin_vars().hotend(e).target_nozzle > 0)) {
            thermalManager.setTargetHotend(0, e);
            set_temp_to_display(0, e);
        }
    }

    server.print_state = State::CrashRecovery_Tool_Pickup; // Continue with screen to wait for user to pick tools
}

/**
 * @brief Part of crash recovery begin when reason of crash is the toolchanger.
 * @note This has to call fsm_create() exactly once.
 * @return true on toolcrash when there is no parking and replay and when should break current switch case
 */
static bool crash_recovery_begin_toolchange() {
    Crash_recovery_tool_fsm cr_fsm(prusa_toolchanger.get_enabled_mask(), 0);
    fsm_create(PhasesCrashRecovery::tool_recovery, cr_fsm.Serialize()); // Ask user to park all dwarves

    if (crash_s.get_state() == Crash_s::REPEAT_WAIT) {
        prepare_tool_pickup(); // If crash happens during toolchange, skip crash recovery and go directly to tool pickup
        return true;
    }
    return false;
}
    #endif /*HAS_TOOLCHANGER()*/

/**
 * @brief Part of crash recovery begin when reason of crash is failed homing.
 * @note This has to call fsm_create() exactly once.
 * @note Should break current switch case after this.
 */
static void crash_recovery_begin_home() {
    Crash_recovery_fsm cr_fsm(SelftestSubtestState_t::running, SelftestSubtestState_t::undef);
    fsm_create(PhasesCrashRecovery::home, cr_fsm.Serialize());

    measure_axes_and_home(); // If crash happens during homing, skip crash recovery and go directly to measuring axes / homing
}

    #if ENABLED(AXIS_MEASURE)
/**
 * @brief Part of crash recovery begin when it is a regular crash, axis measure is enabled and this is a repeated crash.
 * @note This has to call fsm_create() exactly once.
 * @note Do not break current switch case after this, will park and replay.
 */
static void crash_recovery_begin_axis_measure() {
    Crash_recovery_fsm cr_fsm(SelftestSubtestState_t::running, SelftestSubtestState_t::undef);
    fsm_create(PhasesCrashRecovery::check_X, cr_fsm.Serialize()); // check axes first
}
    #endif /*ENABLED(AXIS_MEASURE)*/

/**
 * @brief Part of crash recovery begin when it is a regular crash.
 * @note This has to call fsm_create() exactly once.
 * @note Do not break current switch case after this, will park and replay.
 */
static void crash_recovery_begin_crash() {
    Crash_recovery_fsm cr_fsm(SelftestSubtestState_t::running, SelftestSubtestState_t::undef);
    fsm_create(PhasesCrashRecovery::home, cr_fsm.Serialize());
}
#endif /*ENABLED(CRASH_RECOVERY)*/
#if ENABLED(POWER_PANIC)
void powerpanic_resume(const char *media_SFN_path, const GCodeReaderPosition &resume_pos, bool auto_recover) {
    print_start(media_SFN_path, resume_pos, marlin_server::PreviewSkipIfAble::all);
    crash_s.set_state(Crash_s::PRINTING);

    // open printing screen
    fsm_create(PhasesPrinting::active);

    // Warn user of possible print fail caused by cold heatbed during PP
    if (!auto_recover) {
        set_warning(WarningType::HeatbedColdAfterPP);
    }

    // enter the main powerpanic resume loop
    server.print_state = auto_recover ? State::PowerPanic_Resume : State::PowerPanic_AwaitingResume;
    METRIC_DEF(power, "power_panic", METRIC_VALUE_EVENT, 0, METRIC_ENABLED);
    metric_record_event(&power);
}

void powerpanic_finish_recovery() {
    // WARNING: this sequence needs to _just_ set the server state and exit
    // perform any higher-level operation inside power_panic::atomic_finish

    // setup for replay and start recovery
    crash_s.set_state(Crash_s::RECOVERY);
    server.print_state = State::Resuming_UnparkHead_ZE;
}

void powerpanic_finish_pause() {
    // WARNING: this sequence needs to _just_ set the server state and exit
    // perform any higher-level operation inside power_panic::atomic_finish

    // restore leveling state and planner position (mind the order!)
    planner.leveling_active = crash_s.leveling_active;
    current_position = crash_s.start_current_position;
    planner.set_position_mm(current_position);
    server.print_state = State::Paused;
}

    #if HAS_TOOLCHANGER()
void powerpanic_finish_toolcrash() {
    // WARNING: this sequence needs to _just_ set the server state and exit
    // perform any higher-level operation inside power_panic::atomic_finish

    // Restore leveling state, do not tweak planner position manually as leveling was off when the panic happened
    set_bed_leveling_enabled(crash_s.leveling_active);

    // Go through ToolchangePowerPanic to set up the toolchanger correctly
    crash_s.set_state(Crash_s::REPEAT_WAIT);
    server.print_state = State::CrashRecovery_ToolchangePowerPanic;
}
    #endif /*HAS_TOOLCHANGER()*/
#endif /*ENABLED(POWER_PANIC)*/

#if ENABLED(AXIS_MEASURE)
static Axis_length_t axis_length_ok(AxisEnum axis) {
    #if HAS_SELFTEST()
    const float len = server.axis_length.pos[axis];

    switch (axis) {
    case X_AXIS:
        return len < selftest::Config_XAxis.length_min ? Axis_length_t::shorter : (len > selftest::Config_XAxis.length_max ? Axis_length_t::longer : Axis_length_t::ok);
    case Y_AXIS:
        return len < selftest::Config_YAxis.length_min ? Axis_length_t::shorter : (len > selftest::Config_YAxis.length_max ? Axis_length_t::longer : Axis_length_t::ok);
    default:;
    }
    return Axis_length_t::shorter;
    #else
    return Axis_length_t::ok;
    #endif // HAS_SELFTEST
}

/// \returns true if X and Y axes have correct lengths.
/// You have to measure the length of the axes before this.
Axis_length_t internal::xy_axes_length_ok() {
    Axis_length_t alx = axis_length_ok(X_AXIS);
    Axis_length_t aly = axis_length_ok(Y_AXIS);
    if (alx == aly && aly == Axis_length_t::ok) {
        return Axis_length_t::ok;
    }
    // shorter is worse than longer
    if (alx == Axis_length_t::shorter || aly == Axis_length_t::shorter) {
        return Axis_length_t::shorter;
    }
    return Axis_length_t::longer;
}

static SelftestSubtestState_t axis_length_check(AxisEnum axis) {
    return axis_length_ok(axis) == Axis_length_t::ok ? SelftestSubtestState_t::ok : SelftestSubtestState_t::not_good;
}

/// Sets lengths of axes to "by-pass" xy_axes_length_ok()
static void axes_length_set_ok() {
    server.axis_length.pos[X_AXIS] = (selftest::Config_XAxis.length_min + selftest::Config_XAxis.length_max) / 2;
    server.axis_length.pos[Y_AXIS] = (selftest::Config_YAxis.length_min + selftest::Config_YAxis.length_max) / 2;
}

void set_axes_length(xy_float_t xy) {
    server.axis_length = xy;
}
#endif // ENABLED(AXIS_MEASURE)

// Checking valid behaviour of Heatbreak fan & Print fan of currently active extruder/tool

bool internal::process_crash_state(State state) {
    switch (state) {
#if ENABLED(CRASH_RECOVERY)
    case State::CrashRecovery_Begin: {
        // pause and set correct resume position: this will stop media reading and clear the queue
        // TODO: this is completely broken for crashes coming from serial printing
        pause_print(PauseType::Crash);
        set_media_position(crash_s.sdpos);

        endstops.enable_globally(false);
        crash_s.send_reports();
        crash_s.count_crash();
        if (crash_s.get_state() == Crash_s::TRIGGERED_TOOLCRASH || crash_s.get_state() == Crash_s::TRIGGERED_HOMEFAIL) {
            crash_s.set_state(Crash_s::REPEAT_WAIT);
        } else {
            crash_s.set_state(Crash_s::RECOVERY);
        }

        /**
         * Unreadable switch with 4 posibilites:
         *
         * HAS_TOOLCHANGER() && ENABLED(AXIS_MEASURE)
         * if {toolchange} -> else if {home} -> else if {axis_measure} -> else {crash}
         *
         * HAS_TOOLCHANGER() && !ENABLED(AXIS_MEASURE)
         * if {toolchange} -> else if {home} -> else {crash}
         *
         * !HAS_TOOLCHANGER() && ENABLED(AXIS_MEASURE)
         * if {home} -> else if {axis_measure} -> else {crash}
         *
         * !HAS_TOOLCHANGER() && !ENABLED(AXIS_MEASURE)
         * if {home} -> else {crash}
         *
         * Allways exactly one crash_recovery_begin_~~~() is called.
         * Each of them calls fsm_create() exactly once.
         */
        if (0) {
        } // dummy if to start with else

    #if HAS_TOOLCHANGER()
        else if (crash_s.is_toolchange_event()) {
            if (crash_recovery_begin_toolchange()) {
                break; // Skip crash recovery and go directly to toolchange
            }
        }
    #endif /*HAS_TOOLCHANGER()*/

        else if (crash_s.get_state() == Crash_s::REPEAT_WAIT) { // REPEAT_WAIT could be toolfall, but it was handled above
            crash_recovery_begin_home();
            break; // Skip crash recovery and go directly to homing
        }

    #if ENABLED(AXIS_MEASURE)
        else if (crash_s.is_repeated_crash()) {
            crash_recovery_begin_axis_measure();
        }
    #endif /*ENABLED(AXIS_MEASURE)*/

        else { // All toolfalls, crashes and homing fails are handled above, only regular crash remains
            crash_recovery_begin_crash();
        }

        // save the current resume position
        server.resume.pos = current_position;

    #if ENABLED(ADVANCED_PAUSE_FEATURE)
        /// retract and save E stepper position
        retract();
    #endif // ENABLED(ADVANCED_PAUSE_FEATURE)

        server.print_state = State::CrashRecovery_Retracting;
        break;
    }
    #if HAS_TOOLCHANGER()
    case State::CrashRecovery_ToolchangePowerPanic: {
        // server.resume.nozzle_temp is already configured by powerpanic
        endstops.enable_globally(false);
        crash_recovery_begin_toolchange(); // Also sets server.print_state
        break;
    }
    #endif /*HAS_TOOLCHANGER()*/
    case State::CrashRecovery_Retracting: {
        if (planner.processing()) {
            break;
        }

        lift_head();
        server.print_state = State::CrashRecovery_Lifting;
        break;
    }
    case State::CrashRecovery_Lifting: {
        if (planner.processing()) {
            break;
        }

    #if HAS_TOOLCHANGER()
        if (crash_s.is_toolchange_event()) {
            prepare_tool_pickup(); // Go to tool pickup instead of homing
            break;
        }
    #endif /*HAS_TOOLCHANGER()*/

        measure_axes_and_home();
        break;
    }
    case State::CrashRecovery_XY_Measure: {
        if (is_processing()) {
            break;
        }

    #if ENABLED(AXIS_MEASURE)
        METRIC_DEF(crash_len, "crash_length", METRIC_VALUE_CUSTOM, 0, METRIC_ENABLED);
        metric_record_custom(&crash_len, " x=%.3f,y=%.3f", (double)server.axis_length[X_AXIS], (double)server.axis_length[Y_AXIS]);
    #endif

        set_axis_is_not_at_home(X_AXIS);
        set_axis_is_not_at_home(Y_AXIS);
        server.print_state = State::CrashRecovery_XY_HOME;
        break;
    }
    #if HAS_TOOLCHANGER()
    case State::CrashRecovery_Tool_Pickup: {
        if (is_processing()) {
            break;
        }

        if ((marlin_server::get_response_from_phase(PhasesCrashRecovery::tool_recovery) == Response::Continue)
            && (prusa_toolchanger.get_enabled_mask() == prusa_toolchanger.get_parked_mask())) {

            // Show homing screen, TODO: perhaps a new screen would be better
            Crash_recovery_fsm cr_fsm(SelftestSubtestState_t::running, SelftestSubtestState_t::undef);
            fsm_change(PhasesCrashRecovery::home, cr_fsm.Serialize());

            // Pickup lost tool
            tool_return_t return_type = tool_return_t::no_return; // If it continues with replay, no need to return
            xyz_pos_t return_pos = current_position; //                              return Z to current Z
            if (crash_s.get_state() == Crash_s::REPEAT_WAIT) {
                // After toolcrash, return to what was requested before the crash
                return_pos = prusa_toolchanger.get_precrash().return_pos;
                toNative(return_pos); // Needs to be modified in place, stored in logical coordinates
                return_type = prusa_toolchanger.get_precrash().return_type;
            }
            if (!prusa_toolchanger.tool_change(prusa_toolchanger.get_precrash().tool_nr,
                    return_type,
                    return_pos,
                    tool_change_lift_t::no_lift,
                    /*z_return =*/true)) {
                if (crash_s.get_state() == Crash_s::TRIGGERED_AC_FAULT) {
                    break; // Powerpanic, do not retry just end
                }

                // Toolchange failed again, ask user again to park all dwarves
                crash_s.count_crash(); // Count as another crash
                Crash_recovery_tool_fsm cr_fsm(prusa_toolchanger.get_enabled_mask(), 0);
                fsm_change(PhasesCrashRecovery::tool_recovery, cr_fsm.Serialize());

                prepare_tool_pickup();
                break;
            }

            server.print_state = State::CrashRecovery_XY_HOME; // Reheat and resume, unpark is skipped in later stages
        } else {
            Crash_recovery_tool_fsm cr_fsm(prusa_toolchanger.get_enabled_mask(), prusa_toolchanger.get_parked_mask());
            fsm_change(PhasesCrashRecovery::tool_recovery, cr_fsm.Serialize());
        }
        break;
    }
    #endif /*HAS_TOOLCHANGER()*/
    case State::CrashRecovery_XY_HOME: {
        if (is_processing()) {
            break;
        }

        // TODO: this doesn't respect Crash_s::REPLAY_NONE which should prevent re-home as well
        if (axis_unhomed_error(_BV(X_AXIS) | _BV(Y_AXIS)
                | (crash_s.is_homefail_z() ? _BV(Z_AXIS) : 0))) { // Needs homing
            TemporaryBedLevelingState tbs(false); // Disable for the additional homing, keep previous state after homing
            if (!GcodeSuite::G28_no_parser(true, true, crash_s.is_homefail_z(), { .z_raise = 0 })) {
                // Unsuccesfull rehome
                set_axis_is_not_at_home(X_AXIS);
                set_axis_is_not_at_home(Y_AXIS);
                crash_s.count_crash(); // Count as another crash

                if (crash_s.is_repeated_crash()) { // Cannot home repeatedly
                    disable_XY(); // Let user move the carriage
                    Crash_recovery_fsm cr_fsm(SelftestSubtestState_t::undef, SelftestSubtestState_t::undef);
                    fsm_change(PhasesCrashRecovery::home_fail, cr_fsm.Serialize()); // Retry screen
                    server.print_state = State::CrashRecovery_HOMEFAIL; // Ask to retry
                }
                break;
            }
        }

        if (!crash_s.is_repeated_crash()) {
            fsm_destroy(ClientFSM::CrashRecovery);

            // Necessary for print_resume to work
            server.print_state = State::Paused;
            print_resume();
            break;
        }
    #if ENABLED(AXIS_MEASURE)
        Axis_length_t alok = xy_axes_length_ok();
        if (alok != Axis_length_t::ok) {
            server.print_state = State::CrashRecovery_Axis_NOK;
            Crash_recovery_fsm cr_fsm(axis_length_check(X_AXIS), axis_length_check(Y_AXIS));
            PhasesCrashRecovery pcr = (alok == Axis_length_t::shorter) ? PhasesCrashRecovery::axis_short : PhasesCrashRecovery::axis_long;
            fsm_change(pcr, cr_fsm.Serialize());
            break;
        }
    #endif
        Crash_recovery_fsm cr_fsm(SelftestSubtestState_t::undef, SelftestSubtestState_t::undef);
        fsm_change(PhasesCrashRecovery::repeated_crash, cr_fsm.Serialize());
        server.print_state = State::CrashRecovery_Repeated_Crash;
        break;
    }
    case State::CrashRecovery_HOMEFAIL: {
        switch (marlin_server::get_response_from_phase(PhasesCrashRecovery::home_fail)) {
        case Response::Retry: {
            Crash_recovery_fsm cr_fsm(SelftestSubtestState_t::running, SelftestSubtestState_t::undef);
            fsm_change(PhasesCrashRecovery::home, cr_fsm.Serialize()); // Homing screen
            measure_axes_and_home();
            break;
        }
        default:
            break;
        }
        break;
    }
    case State::CrashRecovery_Axis_NOK: {
        switch (marlin_server::get_response_from_phase(PhasesCrashRecovery::axis_NOK)) {
        case Response::Retry:
            measure_axes_and_home();
            break;
        case Response::Resume: /// ignore wrong length of axes
            fsm_destroy(ClientFSM::CrashRecovery);
    #if ENABLED(AXIS_MEASURE)
            axes_length_set_ok(); /// ignore re-test of lengths
    #endif
            // Necessary for print_resume to work
            server.print_state = State::Paused;
            print_resume();
            break;
        case Response::_none:
            break;
        default:
            server.print_state = State::Paused;
            fsm_destroy(ClientFSM::CrashRecovery);
        }
        break;
    }
    case State::CrashRecovery_Repeated_Crash: {
        switch (marlin_server::get_response_from_phase(PhasesCrashRecovery::repeated_crash)) {
        case Response::Resume:
            fsm_destroy(ClientFSM::CrashRecovery);

            // Necessary for print_resume to work
            server.print_state = State::Paused;
            print_resume();
            break;
        case Response::_none:
            break;
        default:
            server.print_state = State::Paused;
            fsm_destroy(ClientFSM::CrashRecovery);
        }
        break;
    }
#endif // ENABLED(CRASH_RECOVERY)

    default:
        return false;
    }
    return true;
}

bool internal::process_power_panic_state(State state) {
    switch (state) {
#if ENABLED(POWER_PANIC)
    case State::PowerPanic_acFault:
        power_panic::panic_loop();
        break;
    case State::PowerPanic_AwaitingResume:
    case State::PowerPanic_Resume:
        power_panic::resume_loop();
        break;
#endif // ENABLED(POWER_PANIC)

    default:
        return false;
    }
    return true;
}

void resuming_begin(void) {
    reset_safety_errors();

    for (uint8_t hotend = 0; hotend < HOTENDS; hotend++) {
        thermalManager.setTargetHotend(server.resume.nozzle_temp[hotend], hotend);
        set_temp_to_display(server.resume.nozzle_temp[hotend], hotend);
    }

#if FAN_COUNT > 0
    thermalManager.set_fan_speed(0, 0); // disable print fan
#endif
    server.print_state = State::Resuming_Reheating;
}

const GCodeReaderStreamRestoreInfo &stream_restore_info() {
    return print_state.media_restore_info;
}

void print_quick_stop_powerpanic() {
    queue.clear();
}

uint32_t media_position() {
    return queue.last_executed_sdpos;
}

void set_media_position(uint32_t set) {
    // Both sdpos and last_executed_sdpos are needed to be set cause if any gcode is queued and sdpos is invalid while lastExecutedSdpos is not,
    // it is overridden and therefore lost. (This was happening during PP when the print was paused)
    queue.sdpos = set;
    queue.last_executed_sdpos = set;
}

} // namespace marlin_server
