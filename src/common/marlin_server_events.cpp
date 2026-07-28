#include "marlin_server_internal.hpp"
using namespace ExtUI;
LOG_COMPONENT_REF(MarlinServer);
namespace marlin_server {
using namespace internal;

static MutexAtomic<EncodedFSMResponse, freertos::Mutex> fsm_response = empty_encoded_fsm_response;
static std::bitset<std::to_underlying(WarningType::_cnt)> warning_flags;
static uint32_t active_warning_pop_timestamp_sec = 0;
namespace {
    class ErrorChecker {
    public:
        constexpr ErrorChecker() = default;
        constexpr bool isFailed() const { return m_failed; }
        void checkTrue(bool condition, WarningType warning, bool disable_hotend, bool pause_print_on_error) {
            if (condition || m_failed) {
                return;
            }
            set_warning(warning);
            if (pause_print_on_error && server.print_state == State::Printing) {
                pause_print(); // Must store current hotend temperatures before they are set to 0
                server.print_state = State::Pausing_WaitIdle;
            }
            if (disable_hotend) {
                HOTEND_LOOP() {
                    thermalManager.setTargetHotend(0, e);
                    set_temp_to_display(0, e);
                }
            }
            m_failed = true;
        };
        constexpr void reset() { m_failed = false; }

    protected:
        bool m_failed = false;
    };
    class HotendErrorChecker : private ErrorChecker {
    public:
        constexpr HotendErrorChecker() = default;
        void checkTrue(bool condition) {
            if (!condition && !m_failed) {
                if (server.print_state == State::Printing) {
                    m_postponeFullPrintFan = true;
                } else {
#if FAN_COUNT > 0
                    thermalManager.set_fan_speed(0, 255);
#endif
                }
            }
            ErrorChecker::checkTrue(condition, WarningType::HotendTempDiscrepancy, true, true);
            if (condition) {
                reset();
            }
        }
        bool runFullFan() {
            const bool retVal = m_postponeFullPrintFan;
            m_postponeFullPrintFan = false;
            return retVal;
        }
        using ErrorChecker::isFailed;

    private:
        bool m_postponeFullPrintFan = false;
    };
    /// Check MCU temperature and trigger warning and redscreen
    class MCUTempErrorChecker : public ErrorChecker {
        static constexpr const int32_t mcu_temp_warning = 85; ///< When to show warning and pause the print
        static constexpr const int32_t mcu_temp_hysteresis = 2; ///< Hysteresis to reset warning
        static constexpr const int32_t mcu_temp_redscreen = 95; ///< When to show redscreen error
        int32_t ewma_buffer = 0; ///< Buffer for EWMA [1/8 degrees Celsius]
        bool warning = false; ///< True during warning state, enables hysteresis
    public:
        constexpr MCUTempErrorChecker() {};
        /**
         * @brief Check one MCU temperature.
         * @param temperature MCU temperature [degrees Celsius]
         */
        void check(int32_t temperature, WarningType warning_type, const char *error_arg) {
            ewma_buffer = (ewma_buffer * 7 / 8) + temperature; // Simple EWMA filter (stays 1 degree below stable value)
            const auto filtered_temperature = ewma_buffer / 8;
            // Trigger reset immediately
            if (filtered_temperature >= mcu_temp_redscreen) {
                fatal_error(ErrCode::ERR_TEMPERATURE_MCU_MAXTEMP_ERR, error_arg);
            }
            // Trigger and reset warning
            if (warning) {
                if (filtered_temperature < mcu_temp_warning - mcu_temp_hysteresis) {
                    warning = false;
                }
            } else {
                if (filtered_temperature >= mcu_temp_warning) {
                    warning = true;
                }
            }
            this->checkTrue(!warning, warning_type, true, true);
        }
    };
    constinit std::array<ErrorChecker, HOTENDS> hotendFanErrorChecker;
    constinit ErrorChecker printFanErrorChecker;
#if XBUDDY_EXTENSION_VARIANT_STANDARD()
    constinit ErrorChecker xbe_cool_fan_checker; // Handles both cooling fans (we cannot differentiate anyway)
    constinit ErrorChecker xbe_filter_fan_checker;
#endif
#if XL_ENCLOSURE_SUPPORT()
    constinit ErrorChecker enclosure_fan_checker;
#endif
#ifdef HAS_TEMP_HEATBREAK
    constinit std::array<ErrorChecker, HOTENDS> heatBreakThermistorErrorChecker;
#endif
    constinit HotendErrorChecker hotendErrorChecker;
    constinit MCUTempErrorChecker mcuMaxTempErrorChecker; ///< Check Buddy MCU temperature
#if HAS_DWARF()
    static constexpr std::array<const char *, HOTENDS> dwarf_names {
        "Dwarf 1", "Dwarf 2", "Dwarf 3", "Dwarf 4", "Dwarf 5", "Dwarf 6"
    };
    /// Check Dwarf MCU temperature
    constinit std::array<MCUTempErrorChecker, HOTENDS> dwarfMaxTempErrorChecker;
#endif /*HAS_DWARF()*/
#if HAS_REMOTE_BED()
    constinit MCUTempErrorChecker modbedMaxTempErrorChecker; ///< Check ModularBed MCU temperature
#endif

} // namespace
void internal::handle_warnings() {
    const auto phase_opt = fsm_states[ClientFSM::Warning];
    if (!phase_opt.has_value()) {
        return;
    }
    const auto phase = static_cast<PhasesWarning>(phase_opt->GetPhase());
    const auto warning_type = fsm::deserialize_data<WarningType>(phase_opt->GetData());
    // Timeout
    if (fsm_states.get_top()->fsm_type != ClientFSM::Warning) {
        // Some other FSM is on top of Warning FSM - reset warning lifespan timestamp
        active_warning_pop_timestamp_sec = ticks_s();
    }
    if (ticks_s() - active_warning_pop_timestamp_sec > warning_lifespan_sec(warning_type)) {
        clear_warning(warning_type);
        return;
    }
    // Peek the response, only some of the warnings consume it
    const auto response = get_response_from_phase(phase, false);
    if (response == Response::_none) {
        return;
    }
    switch (phase) {
    case PhasesWarning::Warning:
        // The only response is OK, at which point we just consume the response and hide the warning.
        break;
#if HAS_CHAMBER_VENTS()
    case PhasesWarning::ChamberVents:
        if (response == Response::Disable) {
            config_store().check_chamber_vent_state.set(false);
        }
        break;
#endif
#if HAS_CHAMBER_FILTRATION_API()
    case PhasesWarning::EnclosureFilterExpiration:
        buddy::chamber_filtration().handle_filter_expiration_warning(response);
        break;
#endif
#if HAS_ILI9488_DISPLAY()
    case PhasesWarning::DisplayProblemDetected:
        config_store().reduce_display_baudrate.set(response == Response::Yes);
        break;
#endif
    default:
        // Most warnings are handled somewhere else and we shouldn't process the responses here
        // Return to avoid consuming the response
        return;
    }
    // Consume the response now
    get_response_from_phase(phase, true);
    clear_warning(warning_type);
}
static void update_warning_fsm() {
    if (warning_flags.any()) {
        size_t i = 0;
        for (; !warning_flags.test(i); i++)
            ;
        const WarningType type = static_cast<WarningType>(i);
        const fsm::PhaseData data = fsm::serialize_data<WarningType>(type);
        // Avoid reinit of warning timestamp timer if warning is already shown
        if (!fsm_states[ClientFSM::Warning].has_value() || fsm_states[ClientFSM::Warning]->GetData() != data) {
            active_warning_pop_timestamp_sec = ticks_s();
            // Clear any pending responses for this FSM.
            // The displayed warning has changed, we don't want some stray response to be accidentally processed
            clear_fsm_response(ClientFSM::Warning);
            fsm_create(warning_type_phase(type), data);
        }
    } else {
        fsm_destroy(ClientFSM::Warning);
    }
}
void set_warning(WarningType type) {
    log_warning(MarlinServer, "Warning type %d set", (int)type);
    log_info(MarlinServer, "WARNING: %" PRIu32, std::to_underlying(type));
    warning_flags.set(std::to_underlying(type));
    update_warning_fsm();
}
void clear_warning(WarningType type) {
    warning_flags.reset(std::to_underlying(type));
    update_warning_fsm();
}
bool is_warning_active(WarningType type) {
    return warning_flags.test(std::to_underlying(type));
}
Response prompt_warning(WarningType type, uint32_t timeout_ms) {
    set_warning(type);
    const Response r = wait_for_response(warning_type_phase(type), timeout_ms);
    clear_warning(type);
    return r;
}
/******************************************************************************/
// FSM Manipulation
static void commit_fsm_states() {
    fsm_states.increment_state_id();
    marlin_vars().set_fsm_states(fsm_states);
    fsm_states.log();
}
void fsm_create(FSMAndPhase fsm_and_phase, fsm::PhaseData data) {
    fsm_change(fsm_and_phase, data);
}
void fsm_destroy(ClientFSM type) {
    if (fsm_states[type].has_value()) {
        fsm_states[type] = std::nullopt;
        commit_fsm_states();
    }
}
void fsm_change(FSMAndPhase fsm_and_phase, fsm::PhaseData data) {
    const auto base_data = fsm::BaseData(fsm_and_phase.phase, data);
    auto &fsm_state = fsm_states[fsm_and_phase.fsm];
    if (fsm_state->GetPhase() != fsm_and_phase.phase) {
        // Clear any pending responses for this FSM. They might have been sent a long time ago and we don't want them to affect the behavior.
        marlin_server::clear_fsm_response(fsm_and_phase.fsm);
    }
    if (fsm_state != base_data) {
        fsm_state = base_data;
        commit_fsm_states();
    }
}
void internal::fsm_destroy_and_create(ClientFSM old_type, ClientFSM new_type, fsm::BaseData data) {
    fsm_states[old_type] = std::nullopt;
    fsm_states[new_type] = data;
    commit_fsm_states();
}
//-----------------------------------------------------------------------------
// variables

bool internal::send_notify_event_to_client([[maybe_unused]] int client_id, ClientQueue &queue, Event evt_id, uint32_t usr32, uint16_t usr16) {
    const marlin_client::ClientEvent client_message {
        .event = evt_id,
        .unused = 0,
        .usr16 = usr16,
        .usr32 = usr32,
    };
    return queue.try_send(client_message, 0);
}
// send event notification to client - multiple events (called from server thread)
// returns mask of successfully sent events
uint64_t internal::send_notify_events_to_client(int client_id, ClientQueue &queue, uint64_t evt_msk) {
    if (evt_msk == 0) {
        return 0;
    }
    uint64_t sent = 0;
    uint64_t msk = 1;
    for (uint8_t evt_int = 0; evt_int <= std::to_underlying(Event::_last); evt_int++) {
        Event evt_id = Event(evt_int);
        if (msk & evt_msk) {
            switch (Event(evt_id)) {
                // Events without arguments
                // TODO: send all these in a single message as a bitfield
            case Event::MediaInserted:
            case Event::MediaError:
            case Event::MediaRemoved:
            case Event::RequestCalibrationsScreen:
                if (send_notify_event_to_client(client_id, queue, evt_id, 0, 0)) {
                    sent |= msk; // event sent, set bit
                }
                break;
            case Event::NotAcknowledge:
            case Event::Acknowledge:
                if (send_notify_event_to_client(client_id, queue, evt_id, 0, 0)) {
                    sent |= msk; // event sent, set bit
                }
                break;
            // unused events
            case Event::_count:
                assert(false);
                break;
            }
            if ((sent & msk) == 0) {
                break; // skip sending if queue is full
            }
        }
        msk <<= 1;
    }
    return sent;
}
// send event notification to all clients (called from server thread)
// returns bitmask - bit0 = notify for client0 successfully send, bit1 for client1...
uint8_t internal::send_notify_event(Event evt_id, uint32_t usr32, uint16_t usr16) {
    uint8_t client_msk = 0;
    for (int client_id = 0; client_id < MARLIN_MAX_CLIENTS; client_id++) {
        if (server.notify_events[client_id] & ((uint64_t)1 << std::to_underlying(evt_id))) {
            if (send_notify_event_to_client(client_id, marlin_client::marlin_client_queue[client_id], evt_id, usr32, usr16) == 0) {
                server.client_events[client_id] |= ((uint64_t)1 << std::to_underlying(evt_id)); // event not sent, set bit
            } else {
                // event sent, clear flag
                client_msk |= (1 << client_id);
            }
        }
    }
    return client_msk;
}
// update all server variables

bool active_extruder_fan_checks() {
    if (marlin_vars().fan_check_enabled
#if HAS_TOOLCHANGER()
        && prusa_toolchanger.is_any_tool_active() // Nothing to check
#endif /*HAS_TOOLCHANGER()*/
    ) {
        auto check_fan = [](CFanCtlCommon &fan, const char *fan_name) {
            if (!fan.is_fan_ok()) {
                log_error(MarlinServer, "%s FAN RPM is not OK - Actual: %d rpm, PWM: %d",
                    fan_name,
                    (int)fan.get_actual_rpm(),
                    fan.get_pwm());
                return true;
            }
            return false;
        };
        bool fan_failed = false;
#if !PRINTER_IS_PRUSA_iX()
        fan_failed |= check_fan(Fans::heat_break(active_extruder), "Heatbreak");
#endif
        fan_failed |= check_fan(Fans::print(active_extruder), "Print");
        return fan_failed;
    }
    return false;
}
void internal::resuming_reheating() {
    buddy::safety_timer().reset_restore_nonblocking();
    if (hotendErrorChecker.isFailed()) {
        set_warning(WarningType::HotendTempDiscrepancy);
        thermalManager.setTargetHotend(0, 0);
#if FAN_COUNT > 0
        thermalManager.set_fan_speed(0, 255);
#endif
        server.print_state = State::Paused;
        return;
    }
    if (active_extruder_fan_checks()) {
        server.print_state = State::Paused;
        return;
    }
    // Check if nozzles are being reheated
    for (uint8_t hotend = 0; hotend < HOTENDS; hotend++) {
        if (Temperature::degTargetHotend(hotend) != server.resume.nozzle_temp[hotend]) {
            // Stopped reheating, can happen if there is an error during reheating
            server.print_state = State::Paused;
            return;
        }
    }
    if (!Temperature::are_all_temperatures_reached()) {
        return;
    }
#if ENABLED(CRASH_RECOVERY)
    if (crash_s.get_state() == Crash_s::REPEAT_WAIT) {
        server.print_state = State::Resuming_UnparkHead_ZE; // Skip unpark when recovering from toolcrash or homing fail
        return;
    }
#endif /*ENABLED(CRASH_RECOVERY)*/
    unpark_head_XY();
    server.print_state = State::Resuming_UnparkHead_XY;
}

void internal::run_safety_checks() {
    bool do_fan_check = marlin_vars().fan_check_enabled;
#if HAS_SELFTEST()
    // Do not check fan error in marlin server during Fan selftest
    do_fan_check &= !fsm_states[ClientFSM::FansSelftest].has_value();
#endif
    if (do_fan_check) {
        HOTEND_LOOP() {
#if !PRINTER_IS_PRUSA_iX()
            const auto fan_state = Fans::heat_break(e).get_state();
            hotendFanErrorChecker[e].checkTrue(fan_state != CFanCtlCommon::FanState::error_running && fan_state != CFanCtlCommon::FanState::error_starting, WarningType::HotendFanError, true, true);
#endif
        }
        const auto fan_state = Fans::print(active_extruder).get_state();
        printFanErrorChecker.checkTrue(fan_state != CFanCtlCommon::FanState::error_running && fan_state != CFanCtlCommon::FanState::error_starting, WarningType::PrintFanError, false, true);
#if XBUDDY_EXTENSION_VARIANT_STANDARD()
        const bool cool_fan_ok = buddy::xbuddy_extension().is_fan_ok(buddy::XBuddyExtension::Fan::cooling_fan_1) && buddy::xbuddy_extension().is_fan_ok(buddy::XBuddyExtension::Fan::cooling_fan_2);
        xbe_cool_fan_checker.checkTrue(cool_fan_ok, WarningType::ChamberCoolingFanError, false, false);
        if (cool_fan_ok) {
            xbe_cool_fan_checker.reset();
        }
        const bool filter_fan_ok = buddy::xbuddy_extension().is_fan_ok(buddy::XBuddyExtension::Fan::filtration_fan);
        xbe_filter_fan_checker.checkTrue(filter_fan_ok, WarningType::ChamberFiltrationFanError, false, false);
        if (filter_fan_ok) {
            xbe_filter_fan_checker.reset();
        }
#endif /* XBUDDY_EXTENSION_VARIANT_STANDARD() */
#if XL_ENCLOSURE_SUPPORT()
        const bool enclosure_fan_ok = Fans::enclosure().is_fan_ok();
        if (!enclosure_fan_ok && !enclosure_fan_checker.isFailed()) {
            xl_enclosure.setEnabled(false);
        }
        enclosure_fan_checker.checkTrue(enclosure_fan_ok, WarningType::EnclosureFanError, false, false);
        if (enclosure_fan_ok) {
            enclosure_fan_checker.reset();
        }
#endif
    }
    HOTEND_LOOP() {
        if (Fans::heat_break(e).get_rpm_is_ok()) {
            hotendFanErrorChecker[e].reset();
        }
    }
    if (Fans::print(active_extruder).get_rpm_is_ok()) {
        printFanErrorChecker.reset();
    }
#if HAS_TEMP_HEATBREAK
    HOTEND_LOOP() {
    #if ENABLED(PRUSA_TOOLCHANGER)
        if (!prusa_toolchanger.is_tool_enabled(e)) {
            continue;
        }
    #endif
        const auto temp = thermalManager.degHeatbreak(e);
        // Heatbreak is not yet initialized -> nothing to check
        if (temp == TempInfo::celsius_uninitialized) {
            continue;
        }
        // Heatbreak started reporting valid temperatures -> clear the warning
        else if (temp > 10) {
            heatBreakThermistorErrorChecker[e].reset();
        }
        // Getting 0 -> heatbreak error
        else {
            heatBreakThermistorErrorChecker[e].checkTrue(!NEAR_ZERO(temp), WarningType::HeatBreakThermistorFail, true, true);
        }
    }
#endif
    hotendErrorChecker.checkTrue(Temperature::saneTempReadingHotend(0));
    // Check MCU temperatures
    mcuMaxTempErrorChecker.check(AdcGet::getMCUTemp(), WarningType::BuddyMCUMaxTemp, "Buddy");
#if HAS_DWARF()
    HOTEND_LOOP() {
        if (prusa_toolchanger.is_tool_enabled(e)) {
            dwarfMaxTempErrorChecker[e].check(buddy::puppies::dwarfs[e].get_mcu_temperature(), WarningType::DwarfMCUMaxTemp, dwarf_names[e]);
        }
    }
#endif /*HAS_DWARF()*/
#if HAS_REMOTE_BED()
    modbedMaxTempErrorChecker.check(remote_bed::get_mcu_temperature(), WarningType::BedMCUMaxTemp, "Bed");
#endif
}
bool internal::hotend_error_failed() {
    return hotendErrorChecker.isFailed();
}
bool internal::consume_postponed_full_fan() {
    return hotendErrorChecker.runFullFan();
}
void internal::reset_safety_errors() {
    HOTEND_LOOP() {
        hotendFanErrorChecker[e].reset();
    }
    printFanErrorChecker.reset();
    mcuMaxTempErrorChecker.reset();
#if HAS_DWARF()
    HOTEND_LOOP() {
        if (prusa_toolchanger.is_tool_enabled(e)) {
            dwarfMaxTempErrorChecker[e].reset();
        }
    }
#endif
#if HAS_REMOTE_BED()
    modbedMaxTempErrorChecker.reset();
#endif
}
FSMResponseVariant get_response_variant_from_phase(FSMAndPhase fsm_and_phase, bool consume_response) {
    // The FSM should be active the whole time we're waiting for the response.
    // If it isn't, something's probably wrong
    assert(fsm_states[fsm_and_phase.fsm].has_value());
    FSMResponseVariant result;
    fsm_response.transform([&](EncodedFSMResponse &value) {
        if (value.fsm_and_phase != fsm_and_phase) {
            // The response is for a different phase -> do not consume it, do not return it
            return;
        }
        result = value.response;
        if (consume_response) {
            value = empty_encoded_fsm_response;
        }
    });
    if (result != FSMResponseVariant {}) {
        // Receiving a valid response from anywhere (for example Connect) counts as activity, prolong the activity heaters timeout
        buddy::safety_timer().reset_norestore();
    }
    return result;
}
void set_response(const EncodedFSMResponse &response) {
    fsm_response = response;
}
/// Clears any pending response for the provided FSM
void clear_fsm_response(ClientFSM fsm) {
    fsm_response.transform([fsm](EncodedFSMResponse &response) {
        if (response.fsm_and_phase.fsm == fsm) {
            response = empty_encoded_fsm_response;
        }
    });
}
Response wait_for_response(FSMAndPhase fsm_and_phase, uint32_t timeout_ms) {
    // Warning phase response is consumed in marlin_server::handle_warnings
    assert(fsm_and_phase != PhasesWarning::Warning);
    const auto wait_start = ticks_ms();
    while (true) {
        if (auto r = get_response_from_phase(fsm_and_phase); r != Response::_none) {
            return r;
        }
        if (timeout_ms && ticks_diff(ticks_ms(), wait_start) > int32_t(timeout_ms)) {
            return Response::_none;
        }
        ::idle(true);
    }
}
} // namespace marlin_server
