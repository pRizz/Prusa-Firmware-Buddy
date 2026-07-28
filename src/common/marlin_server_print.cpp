#include "marlin_server_internal.hpp"

using namespace ExtUI;

LOG_COMPONENT_REF(MarlinServer);

namespace marlin_server {
using namespace internal;

void internal::pre_finalize_print([[maybe_unused]] bool finished) {
#if HAS_AUTO_RETRACT()
    // During multi tool printing, slicer handles retraction/ramming and keeps FW in the dark
    // RetractTracker keeps track of retracted distances on each hotend
    // This overwrites retracted distances in persistent storage with temporary ones from RetractTracker
    for (uint8_t i = 0; i < HOTENDS; i++) {
        const auto dist = buddy::retract_tracker().get_retracted_distance(i);
        // Do not save retract_tracker value before it was validated
        if (dist.has_value()) {
            // update only used hotends
            buddy::auto_retract().set_retracted_distance(i, dist);
        }
    }
#endif
#if ENABLED(PRUSA_MMU2)
    if (MMU2::mmu2.Enabled()) {
        // Unloading from nozzle is handled by Slicer, do not use auto_retract (frequent filament changes cause retract_tracker cannot properly hold valid value)
        // When we are running single-filament gcode with MMU, we should unload current filament.
        if (!finished || GCodeInfo::getInstance().is_singletool_gcode()) {
            safely_unload_filament_from_nozzle_to_mmu();
        }
    } else
#endif // ENABLED(PRUSA_MMU2)
#if HAS_AUTO_RETRACT()
        if (true) {
        buddy::auto_retract().maybe_retract_from_nozzle();
    } else
#endif
    {
    }
}

void internal::finalize_print(bool finished) {
#if ENABLED(POWER_PANIC)
    power_panic::reset();
#endif

    fsm_destroy(ClientFSM::Serial_printing);

    print_job_timer.stop();
    server_update_vars_now();
    // Check if the stopwatch was NOT stopped to and add the current printime to the statistics.
    // finalize_print is being called multiple times and we don't want to add the time twice.
    if (!server.was_print_time_saved) {
        Odometer_s::instance().add_time(marlin_vars().print_duration);
        server.was_print_time_saved = true;
    }
    // print_maintenance();
#if HAS_MMU2()
    if (!server.mmu_maintenance_checked) {
        if (auto reason = MMU2::check_maintenance(); reason.has_value()) {
            switch (reason.value()) {
            case MMU2::MaintenanceReason::Changes:
                set_warning(WarningType::MaintenanceWarningChanges);
                break;
            case MMU2::MaintenanceReason::Failures:
                set_warning(WarningType::MaintenanceWarningFails);
                break;
            default:
                BUDDY_UNREACHABLE();
            }
        }
        server.mmu_maintenance_checked = true;
    }
#endif // HAS_MMU2()

#if !PRINTER_IS_PRUSA_iX()
    // On iX, we're not cooling down the bed after the print.
    // Resetting bounding rect would result in turning all bedlets on, which we don't want.
    // First - it's increasing power consumption; second - it could clear the bed preheat status.
    // BFW-5085
    print_area.reset_bounding_rect();
#endif

#if ENABLED(PRUSA_TOOL_MAPPING)
    tool_mapper.reset();
    spool_join.reset();
#endif

    gcode.compatibility = {};

#if HAS_CHAMBER_API()
    buddy::chamber().reset();
#endif
    // Reset IS at the end of the print
    input_shaper::init();

    media_prefetch.stop();

    server.print_is_serial = false; // reset flag about serial print

    marlin_vars().print_end_time = time(nullptr);
    marlin_vars().add_job_result(job_id, finished ? marlin_vars_t::JobInfo::JobResult::finished : marlin_vars_t::JobInfo::JobResult::aborted);

#if HAS_CHAMBER_FILTRATION_API()
    buddy::chamber_filtration().check_filter_expiration();
#endif

    if (config_store().show_fsensors_disabled_warning_after_print.get()) {
        config_store().show_fsensors_disabled_warning_after_print.set(false);
        set_warning(WarningType::FilamentSensorsDisabled);
    }

    // Do not remove, needed for 3rd party tools such as octoprint to get status that the gcode file printing has finished
    SERIAL_ECHOLNPGM(MSG_FILE_PRINTED);
}

void gui_ready_to_print() {
    switch (server.print_state) {

    case State::WaitGui:
        server.print_state = State::PrintPreviewInit;
        break;

    default:
        log_error(MarlinServer, "Wrong print state, expected: %u, is: %u",
            static_cast<unsigned>(State::WaitGui), static_cast<unsigned>(server.print_state));
        break;
    }
}

void gui_cant_print() {
    switch (server.print_state) {

    case State::WaitGui:
        server.print_state = State::Idle;
        break;

    default:
        log_error(MarlinServer, "Wrong print state, expected: %u, is: %u",
            static_cast<unsigned>(State::WaitGui), static_cast<unsigned>(server.print_state));
        break;
    }
}

void serial_print_finalize(void) {
    switch (server.print_state) {

    case State::Printing:
    case State::Paused:
    case State::Resuming_Reheating:
    case State::Finishing_WaitIdle:
#if HAS_TOOLCHANGER()
    case State::CrashRecovery_Tool_Pickup:
#endif
        server.print_state = State::Finishing_WaitIdle;
        break;
    default:
        break;
    }
}

void print_abort(void) {

    switch (server.print_state) {

#if ENABLED(POWER_PANIC)
    case State::PowerPanic_Resume:
    case State::PowerPanic_AwaitingResume:
#endif
    case State::Printing:
    case State::Paused:
    case State::MediaErrorRecovery_BufferData:
    case State::Resuming_BufferData:
    case State::Resuming_Reheating:
    case State::Finishing_WaitIdle:
#if HAS_TOOLCHANGER()
    case State::CrashRecovery_Tool_Pickup:
#endif
        server.print_state = State::Aborting_Begin;
        break;

    case State::PrintPreviewInit:
    case State::PrintPreviewImage:
    case State::PrintPreviewConfirmed:
    case State::PrintPreviewQuestions:
#if HAS_TOOLCHANGER() || HAS_MMU2()
    case State::PrintPreviewToolsMapping:
#endif
        server.print_state = State::Aborting_Preview;
        break;

    default:
        break;
    }
}

void print_exit(void) {
    switch (server.print_state) {

#if ENABLED(POWER_PANIC)
    case State::PowerPanic_Resume:
    case State::PowerPanic_AwaitingResume:
#endif
    case State::Printing:
    case State::Paused:
    case State::Resuming_Reheating:
    case State::Finishing_WaitIdle:
        // do nothing
        break;

    default:
        server.print_state = State::Exit;
        break;
    }
}

void print_pause(void) {
    print_state.resume_pending = false;

    switch (server.print_state) {
    case State::Printing:
    case State::Finishing_WaitIdle:
        server.print_state = State::Pausing_Begin;
        break;

    default:
        break;
    }
}

bool internal::process_preview_and_start_state(State state, bool &did_not_start_print) {
    switch (state) {
    case State::Idle:
        break;
    case State::WaitGui:
        // without gui just act as if state == State::PrintPreviewInit
#if HAS_GUI()
        break;
#endif
    case State::PrintPreviewInit:
        did_not_start_print = true;
        // reset both percentage counters (normal and silent)
        oProgressData.standard_mode.percent_done.mSetValue(0, 0);
        oProgressData.stealth_mode.percent_done.mSetValue(0, 0);
        PrintPreview::Instance().Init();
        server.print_state = State::PrintPreviewImage;
        break;

    case State::PrintPreviewImage:
    case State::PrintPreviewConfirmed:
#if HAS_TOOLCHANGER() || HAS_MMU2()
    case State::PrintPreviewToolsMapping:
#endif
    case State::PrintPreviewQuestions: {
        // button evaluation
        // We don't particularly care about the
        // difference, but downstream users do.

        auto old_state = server.print_state;
        auto new_state = old_state;
        switch (PrintPreview::Instance().Loop()) {

        case PrintPreview::Result::Wait:
            break;

        case PrintPreview::Result::MarkStarted:
            // The job_id is used to identify a job for Connect & Link. We want to
            // have a unique one for each job, but have the same one through the
            // whole job. From UI perspective, the questions about filament /
            // printer type / etc are already part of the job (there's a preview in
            // Connect for whatever is being printed).

            // First, reserve the job_id in eeprom. In case we get reset, we need
            // that to not get reused by accident.
            config_store().job_id.set(job_id + 1);
            // And increment the job ID before we actually stop printing.
            job_id++;
            // Reset "time to" and percents before asking questions to "unknown"
            oProgressData.mInit();

            new_state = State::PrintPreviewConfirmed;
            break;

        case PrintPreview::Result::Image:
            new_state = State::PrintPreviewImage;
            break;

        case PrintPreview::Result::Questions:
            new_state = State::PrintPreviewQuestions;
            break;

        case PrintPreview::Result::Abort:
            new_state = did_not_start_print ? State::Idle : State::Finishing_WaitIdle;
            if (did_not_start_print) {
                // Saving the result for connect, we already send the job id to them at this point.
                marlin_vars().add_job_result(job_id, marlin_vars_t::JobInfo::JobResult::aborted);
            }
            media_prefetch.stop();
            fsm_destroy(ClientFSM::PrintPreview);
            break;

#if HAS_TOOLCHANGER() || HAS_MMU2()
        case PrintPreview::Result::ToolsMapping:
            new_state = State::PrintPreviewToolsMapping;
            break;
#endif

        case PrintPreview::Result::Print:
        case PrintPreview::Result::Inactive:
            did_not_start_print = false;
            new_state = State::PrintInit;

#if HAS_TOOLCHANGER()
            if (prusa_toolchanger.is_toolchanger_enabled()) {
                // Handle singletool G-code which doesn't have T commands in it
                if (GCodeInfo::getInstance().is_singletool_gcode()) {
                    enqueue_gcode("T0 S1 D0"); // Pick tool 0 (can be remapped to anything) before print
                }
            }
#endif /*HAS_TOOLCHANGER()*/
#if HAS_MMU2()
            if (MMU2::mmu2.Enabled() && GCodeInfo::getInstance().is_singletool_gcode() && MMU2::mmu2.get_current_tool() == MMU2::FILAMENT_UNKNOWN) {
                // POC: Handle singletool G-code which doesn't have T commands in it
                // In case we don't have other filament loaded!
                // Unfortunately we don't have the nozzle heated, an ugly workaround is to enqueue an M109 :(

                const uint16_t preheat_temp = GCodeInfo::getInstance().get_hotend_preheat_temp().value_or(215U);
                enqueue_gcode_printf("M109 S%" PRIu16, preheat_temp); // speculatively, use PLA temp for MMU prints, anything else is highly unprobable at this stage
                enqueue_gcode("T0"); // tool change T0 (can be remapped to anything)
                enqueue_gcode("G92 E0"); // reset extruder position to 0

                bool is_relative = gcode.axis_is_relative(AxisEnum::E_AXIS);

                enqueue_gcode("M82"); // set E to absolute positions
    #if HAS_LOADCELL()
                enqueue_gcode("G1 E25 F1860"); // push filament into the nozzle - load distance from fsensor into nozzle tuned (hardcoded) for now
                enqueue_gcode("G1 E35 F300"); // slowly push another 10mm (absolute E)
    #else
                enqueue_gcode("G1 E50 F1860"); // push filament into the nozzle - load distance from fsensor into nozzle tuned (hardcoded) for now
                enqueue_gcode("G1 E62 F300"); // slowly push another 12mm (absolute E)
    #endif
                if (is_relative) {
                    enqueue_gcode("M83"); // set E back to relative positions
                }

                // In case of need, we can perform a custom purge line from the other end of the heatbed
                // It would require homing the axes first, moving to [maxx-10, -4] and slowly purging while moving towards the origin
            }
#endif
            break;
        }

        server.print_state = new_state;

        break;
    }

    case State::PrintInit:
    case State::SerialPrintInit:
        server.print_is_serial = (server.print_state == State::SerialPrintInit);
        server.was_print_time_saved = false;
#if HAS_MMU2()
        server.mmu_maintenance_checked = false;
#endif
        planner.max_printed_z = 0;

        if (!server.print_is_serial) {
            feedrate_percentage = 100;

            // Reset flow factor for all extruders
            HOTEND_LOOP() {
                planner.flow_percentage[e] = 100;
                planner.refresh_e_factor(e);
            }
        }

#if ENABLED(PRUSA_TOOL_MAPPING) && (HOTENDS > 1)
        if (!server.print_is_serial) {
            // Cooldown unused tools
            // Ignore spool join - spool joined tools will get heated as spool join is activated
            // BFW-5996
            for (uint8_t physical_tool = 0; physical_tool < HOTENDS; physical_tool++) {
                if (tool_mapper.to_gcode(physical_tool) == tools_mapping::no_tool) {
                    thermalManager.setTargetHotend(0, physical_tool);
                }
            }
        }
#endif

#if ENABLED(CRASH_RECOVERY)
        crash_s.reset();
        crash_s.counters.reset();
        endstops.enable_globally(true);

        // Crash Detection is disabled during serial printing, because it does not work
        if (!server.print_is_serial) {
            crash_s.set_state(Crash_s::PRINTING);
        }
#endif // ENABLED(CRASH_RECOVERY)

#if HAS_CEILING_CLEARANCE()
        buddy::reenable_ceiling_clearance_warning();
#endif

#if HAS_CANCEL_OBJECT()
        buddy::cancel_object().reset();
        for (auto &cancel_object_name : marlin_vars().cancel_object_names) {
            cancel_object_name.set(""); // Erase object names
        }
#endif

#if HAS_LOADCELL()
        if (!server.print_is_serial) {
            // Reset Live-Adjust-Z value before every print
            probe_offset.z = 0;
            marlin_vars().z_offset = 0;
        }
#endif // HAS_LOADCELL()

        print_job_timer.start();
        marlin_vars().print_start_time = time(nullptr);

        if (!server.print_is_serial) {
            marlin_vars().time_to_end = TIME_TO_END_INVALID;
            marlin_vars().time_to_pause = TIME_TO_END_INVALID;
        }

        server.print_state = State::Printing;

        if (server.print_is_serial) {
            fsm_create(PhasesSerialPrinting::active);
        } else {

            if (fsm_states.is_active(ClientFSM::PrintPreview)) {
                fsm_destroy_and_create(ClientFSM::PrintPreview, ClientFSM::Printing, fsm::BaseData());
            }
            if (!fsm_states.is_active(ClientFSM::Printing)) {
                // FIXME make this atomic change. It would require improvements in PrintScreen so that it can re-initialize upon phase change.
                // FYI the DESTROY invoke is in print_start()
                // NOTE this works surely thanks to State::WaitGui being in between the DESTROY and CREATE
                fsm_create(PhasesPrinting::active);
            }
        }
#if HAS_CHAMBER_VENTS()
        buddy::chamber().manage_ventilation_state();
#endif
#if HAS_CHAMBER_FILTRATION_API()
        buddy::chamber_filtration().check_filter_expiration();
#endif
        break;

    case State::Printing:
        print_state.resume_pending = false;

        if (server.print_is_serial) {
            SerialPrinting::print_loop();
        } else {
            media_print_loop();
        }
        break;

    default:
        return false;
    }
    return true;
}

bool internal::process_pause_state(State state) {
    switch (state) {
    case State::Pausing_Begin:
        pause_print();
        [[fallthrough]];
    case State::Pausing_Failed_Code:
        server.print_state = State::Pausing_WaitIdle;
        break;
    case State::Pausing_WaitIdle:
        if (!is_processing()) {
            park_head();
            server.print_state = State::Pausing_ParkHead;
        }
        break;
    case State::Pausing_ParkHead:
        if (!planner.processing()) {
            server.print_state = State::Paused;
        }
        break;
    case State::Paused:
        // resume queuing serial commands (to be able to resume)
        GCodeQueue::pause_serial_commands = false;

        if (print_state.resume_pending) {
            print_state.resume_pending = false;
            print_resume();
        } else if (print_state.recover_media_error_at.has_value() && ticks_diff(*print_state.recover_media_error_at, ticks_s()) <= 0) {
            log_info(MarlinServer, "Try recover from media error");
            print_state.recover_media_error_at.reset();
            try_recover_from_media_error();
            // Ensure we do try to unpause here.
            assert(server.print_state != State::Paused);
        }

        break;

    default:
        return false;
    }
    return true;
}

bool internal::process_resume_state(State state, bool &abort_resuming) {
    switch (state) {
    case State::Resuming_Begin:
#if ENABLED(CRASH_RECOVERY)
    #if ENABLED(AXIS_MEASURE)
        if (crash_s.is_repeated_crash() && xy_axes_length_ok() != Axis_length_t::ok) {
            /// resuming after a crash but axes are not ok => check again
            fsm_create(PhasesCrashRecovery::check_X);
            measure_axes_and_home();
            break;
        }
    #endif

        // forget the XYZ resume position if requested
        if (!(crash_s.recover_flags & Crash_s::RECOVER_XY_POSITION)) {
            LOOP_XY(i) {
                server.resume.pos[i] = current_position[i];
            }
        }
        if (!(crash_s.recover_flags & Crash_s::RECOVER_Z_POSITION)) {
            server.resume.pos[Z_AXIS] = current_position[Z_AXIS];
        }
#endif
        resuming_begin();
        break;
    case State::Resuming_Reheating:
        resuming_reheating();
        break;
    case State::Resuming_UnparkHead_XY:
        if (active_extruder_fan_checks()) {
            abort_resuming = true;
        }
        if (planner.processing()) {
            break;
        }
        unpark_head_ZE();
        server.print_state = State::Resuming_UnparkHead_ZE;
        break;
    case State::Resuming_UnparkHead_ZE:
        if (active_extruder_fan_checks()) {
            abort_resuming = true;
        }

        if (is_processing()) {
            break;
        }

#if ENABLED(CRASH_RECOVERY)
        if (crash_s.get_state() == Crash_s::RECOVERY) {
            endstops.enable_globally(true);
            crash_s.set_state(Crash_s::REPLAY);
        } else if (crash_s.get_state() == Crash_s::REPEAT_WAIT) {
            endstops.enable_globally(true);
            crash_s.set_state(Crash_s::PRINTING); // Coming from toolcrash or homing fail, no replay
        } else {
            // UnparkHead can be called after a pause, in which case crash handling should already
            // be active and we don't need to change any other setting

            // Crash Detection is disabled during serial printing, because it does not work
            assert(server.print_is_serial || crash_s.get_state() == Crash_s::PRINTING);
        }
#endif
        if (abort_resuming) {
            server.print_state = State::Pausing_WaitIdle;
            abort_resuming = false;
            break;
        }
        // server.motion_param.load();  // TODO: currently disabled (see Crash_s::save_parameters())
        if (print_job_timer.isPaused()) {
            print_job_timer.start();
        }
#if FAN_COUNT > 0
        thermalManager.set_fan_speed(0, server.resume.fan_speed); // restore fan speed
#endif
        feedrate_percentage = server.resume.print_speed;
        SerialPrinting::resume();
        server.print_state = State::Printing;
        break;

    default:
        return false;
    }
    return true;
}

void internal::server_print_loop() {
    static bool did_not_start_print = true;
    static bool abort_resuming = false;
    const State state = server.print_state;

    if (process_preview_and_start_state(state, did_not_start_print)
        || process_pause_state(state)
        || process_media_recovery_state(state)
        || process_resume_state(state, abort_resuming)
        || process_finish_state(state)
        || process_crash_state(state)
        || process_power_panic_state(state)) {
        run_safety_checks();
        return;
    }

    run_safety_checks();
}

} // namespace marlin_server
