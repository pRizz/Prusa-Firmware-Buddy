#include "marlin_server_internal.hpp"

using namespace ExtUI;

LOG_COMPONENT_REF(MarlinServer);

namespace marlin_server {
using namespace internal;

osThreadId server_task = 0;
static bool is_cycle_running = false;

void init(void) {
    int i;
    server = ServerState();
    server.flags = 0;
    for (i = 0; i < MARLIN_MAX_CLIENTS; i++) {
        server.notify_events[i] = make_mask(Event::Acknowledge); // by default only ack
        server.notify_changes[i] = 0; // by default nothing
    }
    server_task = osThreadGetId();

    // Random at boot, to avoid chance of reusing the same (0/1) dialog ID
    // after a reboot.
    fsm_states.init_state_id();

#if HAS_SHEET_PROFILES()
    SteelSheets::CheckIfCurrentValid();
#endif
    settings_load();
}

void print_fan_spd() {
    static uint32_t last_fan_report = 0;
    uint32_t current_time = ticks_s();
    if (M123::fan_auto_report_delay && (current_time - last_fan_report) >= M123::fan_auto_report_delay) {
        M123::print_fan_speed();
        last_fan_report = current_time;
    }
}

#if HAS_NFC()

void handle_nfc() {
    static uint32_t last_check = 0;
    const uint32_t current_time = ticks_ms();
    if (last_check > current_time || (current_time - last_check) >= nfc::OPTIMAL_CHECK_DIFF_MS) {
        last_check = current_time;

        if (nfc::has_activity()) {
            if (const std::optional<WifiCredentials> wifi_credentials = nfc::consume_data()) {
                network_wizard::network_nfc_wizard(*wifi_credentials);
            }
        }
    }
}

#endif

#if ENABLED(PRUSA_MMU2)
/// Helper function that enqueues gcodes to safely unload filament from nozzle back to mmu
///
/// To safely unload a filament we need to ensure that the nozzle has correct temperature.
/// This can be safely done by using the `M702` gcode with `W2` argument. The gcode unloads
/// the filament back to mmu and with the argument waits  for correct temperature (if the
/// temperature is bigger than nessesary the gcode (with this argument) doesn't wait for
/// cooldown.
///
/// After the filament is unloaded then we need to restore original temperature. Since we
/// are enqueueing gcode, we can't set it directly and we need to enque another gcode. We
/// can do this since this will be only called at the end of the print or when aborting.
/// So it shouldn't overwrite any important gcodes.
void internal::safely_unload_filament_from_nozzle_to_mmu() {
    if (MMU2::WhereIsFilament() == MMU2::FilamentState::NOT_PRESENT) {
        return; // no filament loaded, nothing to do
    }
    const uint16_t original_temp = thermalManager.degTargetHotend(active_extruder);
    enqueue_gcode_printf("M702 W2 T%" PRIu8, active_extruder);
    enqueue_gcode_printf("M104 S%" PRIu16, original_temp);
}
#endif

void server_update_vars() {
    uint32_t tick = ticks_ms();
    if ((tick - server.last_update) > MARLIN_UPDATE_PERIOD) {
        server.last_update = tick;
        server_update_vars_now();
    }
}

void send_notifications_to_clients() {
    for (int client_id = 0; client_id < MARLIN_MAX_CLIENTS; client_id++) {
        ClientQueue &queue = marlin_client::marlin_client_queue[client_id];
        if (const uint64_t msk = server.client_events[client_id]) {
            server.client_events[client_id] &= ~send_notify_events_to_client(client_id, queue, msk);
        }
    }
}

#if HAS_I2C_EXPANDER()

// Used to avoid multiple triggering of pressed buttons.
static uint8_t io_expander_button_trigger_check(uint8_t pin_states, uint8_t pin_mask) {
    static uint8_t prev_pressed_buttons = 0;

    // Pin states are inversed - pin is low on button press
    const auto pressed_buttons = (~pin_states) & pin_mask;
    const auto triggered_buttons = pressed_buttons & ~prev_pressed_buttons;
    prev_pressed_buttons = pressed_buttons;

    return triggered_buttons;
}

void io_expander_read_loop() {
    if (!buddy::hw::io_expander2.is_initialized()) {
        return;
    }
    if (uint8_t pin_mask = config_store().io_expander_config_register.get()) {
        static constexpr int32_t io_expander_read_loop_delay_ms = 500;
        static uint32_t last_tick_ms = ticks_ms();
        uint32_t tick_ms = ticks_ms();
        if (ticks_diff(tick_ms, last_tick_ms) >= io_expander_read_loop_delay_ms) {
            if (const auto value = buddy::hw::io_expander2.read(pin_mask)) {

                // Debouncing mechanism - after pressing a button, there have to be at least one released state before button can be pressed again
                uint8_t pressed_buttons_mask = io_expander_button_trigger_check(*value, pin_mask);

                for (uint8_t pin_number = 0; pin_number < buddy::hw::TCA6408A::pin_count; pin_number++) {
                    // Create a mask and extract the pin from the pressed_buttons_mask
                    const uint8_t single_pin_mask = 0x1 << pin_number;

                    if (pin_mask & single_pin_mask & pressed_buttons_mask) {
                        if (!inject(GCodeMacroButton(pin_number))) {
                            SERIAL_ECHOLIST("Injecting Macro Button failed, pin: ", pin_number);
                        }
                    }
                }
            }
            last_tick_ms = tick_ms;
        }
    }
}
#endif // HAS_I2C_EXPANDER()

static void cycle() {
    // Some things are somewhat time-sensitive and should be updated even in nested loops
#if HAS_CHAMBER_API()
    buddy::chamber().step();
#endif

#if HAS_CHAMBER_FILTRATION_API()
    buddy::chamber_filtration().step();
#endif

#if HAS_EMERGENCY_STOP()
    buddy::emergency_stop().step();
#endif

#if XBUDDY_EXTENSION_VARIANT_STANDARD()
    buddy::xbuddy_extension().step();
#endif

    buddy::safety_timer().step();

    // Although the timeout should never trigger within idle() (= when a gcode is run),
    // We still need to run the step() there to prevent "sampling bias" so that the timer could reset itself during movements and single-injected gcodes
    buddy::stepper_timeout().step();

    record_fanctl_metrics();

    idle_hook_point.call_all();

    if (is_cycle_running) {
        return;
    }
    AutoRestore _nr(is_cycle_running, true);

#if HAS_MMU2()
    MMU2::Fsm::Instance().Loop();
#endif

    handle_warnings();

#if XL_ENCLOSURE_SUPPORT()
    int16_t dwarf_temp = std::numeric_limits<int16_t>().min();
    #if HAS_TOOLCHANGER()
    dwarf_temp = prusa_toolchanger.getActiveToolOrFirst().get_board_temperature();
    #endif

    xl_enclosure.loop(remote_bed::get_mcu_temperature(), dwarf_temp);
#endif

#if HAS_SELFTEST()
    if (!SelftestInstance().IsInProgress()) {
#else
    {
#endif
        server_print_loop(); // we need call print loop here because it must be processed while blocking commands (M109)
    }

    // Clear temporary print status messages that have timed out -
    // but only if the printer isn't paused.
    // [BFW-6485] People like to use M117 (show message) before M601
    if (!is_extended_paused_state(server.print_state)) {
        print_status_message().clear_timed_out_temporary();
    }

    print_fan_spd();

#if HAS_TOOLCHANGER()
    // Check if tool didn't fall off
    prusa_toolchanger.loop(!printer_idle(), printer_paused());
#endif /*HAS_TOOLCHANGER()*/

#if HAS_I2C_EXPANDER()
    io_expander_read_loop();
#endif // HAS_I2C_EXPANDER()

    process_request_flags();

    if (Request request; request_queue.try_receive(request, 0)) {
        process_server_request(request);
    }

    // update variables
    send_notifications_to_clients();
    server_update_vars();
}
#if ANY(CRASH_RECOVERY, POWER_PANIC)
static void check_crash() {
    // reset the nested loop check once per main server iteration
    crash_s.needs_stack_unwind = false;

    #if ENABLED(POWER_PANIC)
    // handle server state-change overrides happening in the ISRs here (and nowhere else)
    if (power_panic::panic_is_active()) {
        server.print_state = State::PowerPanic_acFault;
        return;
    }
    #endif

    // Start crash recovery if TRIGGERED, but not if print is already being aborted
    if ((server.print_state != State::Aborting_Begin)
        && ((crash_s.get_state() == Crash_s::TRIGGERED_ISR)
            || (crash_s.get_state() == Crash_s::TRIGGERED_TOOLFALL)
            || (crash_s.get_state() == Crash_s::TRIGGERED_TOOLCRASH)
            || (crash_s.get_state() == Crash_s::TRIGGERED_HOMEFAIL))) {

        // Set again to prevent race when ISR happens during this function
        crash_s.needs_stack_unwind = false;
        server.print_state = State::CrashRecovery_Begin;
        return;
    }
}
#endif // ENABLED(CRASH_RECOVERY)

void loop() {
    ::idle(false); // Do an idle first so boot is slightly faster
    queue.advance();

#if HAS_SELFTEST()
    if (SelftestInstance().IsInProgress()) {
        SelftestInstance().Loop();
    }
#endif

#if ANY(CRASH_RECOVERY, POWER_PANIC)
    check_crash();
#endif

    // Revert quick_stop when commands already drained
    if (server.flags & MARLIN_SFLG_STOPPED && !is_processing()) {
        planner.resume_queuing();
        server.flags &= ~MARLIN_SFLG_STOPPED;
    }

    cycle();

#if HAS_EMERGENCY_STOP()
    // During printing, possibly block anytime
    if (is_printing_state(server.print_state)) {
        buddy::emergency_stop().maybe_block();
    }
#endif

#if HAS_NFC()
    if (printer_idle() && !fsm_states.get_top().has_value()) {
        handle_nfc();
    }
#endif
}

static bool idle_running = false;

static void idle(void) {
    cycle();

    // cycle -> loop -> idle -> MarlinUI::update() -> ExtUI::onIdle -> idle -> cycle
    // This is only a work-around: this should be avoided at a higher level
    if (idle_running) {
        return;
    }

    AutoRestore _ar(idle_running, true);

#if HAS_EMERGENCY_STOP()
    // During printing, possibly block anytime, with exception of Load Unload sequence
    // In case there would be planned unsafe moves, there is another buddy::emergency_stop().maybe_block() directly in planner
    if (is_printing_state(server.print_state) && !fsm_states.is_active(ClientFSM::Load_unload)) {
        buddy::emergency_stop().maybe_block();
    }
#endif
}

void internal::settings_load() {
    (void)settings.reset();
#if HAS_SHEET_PROFILES()
    probe_offset.z = SteelSheets::GetZOffset();
#endif
#if ENABLED(PIDTEMPBED)
    Temperature::temp_bed.pid.Kp = config_store().pid_bed_p.get();
    Temperature::temp_bed.pid.Ki = config_store().pid_bed_i.get();
    Temperature::temp_bed.pid.Kd = config_store().pid_bed_d.get();
#endif
#if ENABLED(PIDTEMP)
    HOTEND_LOOP() {
        Temperature::temp_hotend[e].pid.Kp = config_store().pid_nozzle_p.get();
        Temperature::temp_hotend[e].pid.Ki = config_store().pid_nozzle_i.get();
        Temperature::temp_hotend[e].pid.Kd = config_store().pid_nozzle_d.get();
    }
    thermalManager.updatePID();
#endif

    marlin_vars().fan_check_enabled = config_store().fan_check_enabled.get();

    planner.set_stealth_mode(config_store().stealth_mode.get());

    job_id = config_store().job_id.get();

#if ENABLED(PRUSA_TOOLCHANGER)
    // TODO: This is temporary until better offset store method is implemented
    prusa_toolchanger.load_tool_offsets();
#endif

#if HAS_PHASE_STEPPING()
    phase_stepping::load();
#endif
}

bool internal::process_finish_state(State state) {
    switch (state) {
    case State::Aborting_Begin:
#if ENABLED(CRASH_RECOVERY)
        if (crash_s.is_toolchange_in_progress()) {
            break; // Wait for toolchange to end
        }
#endif /*ENABLED(CRASH_RECOVERY)*/
        if (marlin_vars().gcode_command.get() == Cmd::G28) {
            break; // Wait for homing to end
        }

        // Unstuck any operation that is skippable
        skippable_gcode().request_skip();

        media_prefetch.stop();
        queue.clear();

        print_job_timer.stop();
        planner.quick_stop();
        wait_for_heatup = false; // This is necessary because M109/wait_for_hotend can be in progress, we need to abort it

#if ENABLED(CRASH_RECOVERY)
        // TODO: the following should be moved to State::Aborting_ParkHead once the "stopping"
        // state is handled properly
        endstops.enable_globally(false);
        crash_s.counters.save_to_eeprom();
        server.aborting_did_crash_trigger = crash_s.did_trigger(); // Remember as it is cleared by crash_s.reset()
        crash_s.reset();
#endif // ENABLED(CRASH_RECOVERY)

        server.print_state = State::Aborting_WaitIdle;
        break;
    case State::Aborting_WaitIdle:
        if (is_processing()) {
            break;
        }

        // allow movements again
        planner.resume_queuing();
        if (server.print_is_serial) {
            // will enqueue gcode that will send abort to print host
            SerialPrinting::abort();
        }
        set_current_from_steppers();
        sync_plan_position();
        report_current_position();

#if HAS_EMERGENCY_STOP()
        if (!buddy::emergency_stop().in_emergency()) {
#else
        {
#endif
            if (axes_need_homing()
#if ENABLED(CRASH_RECOVERY)
                || server.aborting_did_crash_trigger
#endif /*ENABLED(CRASH_RECOVERY)*/
            )
                lift_head(); // It would be dangerous to move XY
            else {
                park_head();
            }
        }

        thermalManager.disable_all_heaters();

#if FAN_COUNT > 0
        thermalManager.set_fan_speed(0, 0);
#endif
        HOTEND_LOOP() {
            set_temp_to_display(0, e);
        }

        server.print_state = State::Aborting_UnloadFilament;
        break;

    case State::Aborting_UnloadFilament:
        if (is_processing()) {
            break;
        }

        pre_finalize_print(false);
        server.print_state = State::Aborting_ParkHead;
        break;
    case State::Aborting_ParkHead:
        if (!is_processing()) {
            disable_XY();
#ifndef Z_ALWAYS_ON
            disable_Z();
#endif // Z_ALWAYS_ON
            disable_e_steppers();
            server.print_state = State::Aborted;
            finalize_print(false);
        }
        break;
    case State::Aborting_Preview:
        // Wait for operations to finish
        if (is_processing()) {
            break;
        }

#if HAS_TOOLCHANGER() || HAS_MMU2()
        if (PrintPreview::Instance().GetState() == PrintPreview::State::tools_mapping_wait_user) {
            PrintPreview::tools_mapping_cleanup();
        }
#endif

        // Can go directly to Idle because we didn't really start printing.
        server.print_state = State::Idle;
        PrintPreview::Instance().ChangeState(IPrintPreview::State::inactive);
        fsm_destroy(ClientFSM::PrintPreview);
        media_prefetch.stop();
        break;

    case State::Finishing_WaitIdle:
        if (!is_processing()) {
#if ENABLED(CRASH_RECOVERY)
            // TODO: the following should be moved to State::Finishing_ParkHead once the "stopping"
            // state is handled properly
            endstops.enable_globally(false);
            crash_s.counters.save_to_eeprom();
            crash_s.reset();
#endif // ENABLED(CRASH_RECOVERY)

            // ! Must be before the park_head(), otherwise the head parking is still considered a print state
            server.print_state = State::Finishing_UnloadFilament;

#ifdef PARK_HEAD_ON_PRINT_FINISH
            if (!server.print_is_serial) {
                // do not move head if printing via serial
                park_head();
            }
#endif // PARK_HEAD_ON_PRINT_FINISH
        }
        break;
    case State::Finishing_UnloadFilament:
        if (is_processing()) {
            break;
        }

        pre_finalize_print(true);
        server.print_state = State::Finishing_ParkHead;
        break;
    case State::Finishing_ParkHead:
        if (!is_processing()) {
            server.print_state = State::Finished;
            finalize_print(true);
        }
        break;
    case State::Exit:
        // make the State::Exit state more resilient to repeated calls (e.g. USB drive pulled out prematurely at the end-of-print screen)
        if (fsm_states.is_active(ClientFSM::Printing)) {
            finalize_print(false);
            fsm_destroy(ClientFSM::Printing);
        }
        if (fsm_states.is_active(ClientFSM::Serial_printing)) {
            finalize_print(false);
        }

        media_prefetch.stop();
        server.print_state = State::Idle;
        break;

    default:
        return false;
    }
    return true;
}

} // namespace marlin_server

[[noreturn]] void kill(PGM_P const lcd_error, PGM_P const lcd_component, [[maybe_unused]] const bool steppers_off) {
    const char *msg = lcd_error ?: GET_TEXT(MSG_KILLED);
    log_info(MarlinServer, "Printer killed: %s", msg);
    fatal_error(msg, lcd_component);
}

namespace ExtUI {
using namespace marlin_server;

void onStartup() {
}

void onIdle() {
    idle();

    // update sensor values for metrics and sensor screens
    sensor_data().update();
    buddy::metrics::record();

    print_utils_loop();
}

void onPrintTimerStarted() {
    log_info(MarlinServer, "ExtUI: onPrintTimerStarted");
}

void onPrintTimerPaused() {
    log_info(MarlinServer, "ExtUI: onPrintTimerPaused");
}

void onPrintTimerStopped() {
    log_info(MarlinServer, "ExtUI: onPrintTimerStopped");
}

void onUserConfirmRequired(const char *const msg) {
    log_info(MarlinServer, "ExtUI: onUserConfirmRequired: %s", msg);
}

void onFactoryReset() {
    log_info(MarlinServer, "ExtUI: onFactoryReset");
}

void onLoadSettings(char const *) {
    log_info(MarlinServer, "ExtUI: onLoadSettings");
}

void onStoreSettings(char *) {
    log_info(MarlinServer, "ExtUI: onStoreSettings");
}

void onConfigurationStoreWritten([[maybe_unused]] bool success) {
    log_info(MarlinServer, "ExtUI: onConfigurationStoreWritten");
}

void onConfigurationStoreRead([[maybe_unused]] bool success) {
    log_info(MarlinServer, "ExtUI: onConfigurationStoreRead");
}

void onMeshUpdate([[maybe_unused]] const uint8_t xpos, [[maybe_unused]] const uint8_t ypos, [[maybe_unused]] const float zval) {
    log_debug(MarlinServer, "ExtUI: onMeshUpdate x: %u, y: %u, z: %.2f", xpos, ypos, (double)zval);
}

} // namespace ExtUI
