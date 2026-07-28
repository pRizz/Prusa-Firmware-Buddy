/**
 * @file pause.cpp
 * @author Radek Vana
 * @brief stubbed version of marlin pause.cpp
 * mainly used for load / unload / change filament
 * @date 2020-12-18
 */

#include "pause_internal.hpp"

LOG_COMPONENT_REF(MarlinServer);

#if HAS_NOZZLE_CLEANER()
GCodeLoader nozzle_cleaner_gcode_loader;
#endif

PauseMenuResponse pause_menu_response;

uint8_t did_pause_print = 0;

void do_pause_e_move(const float &length, const feedRate_t &fr_mm_s) {
    mapi::extruder_move(length, fr_mm_s);
    planner.synchronize();
}

void unhomed_z_lift(float amount_mm) {
    if (amount_mm > current_position.z) {
        TemporaryGlobalEndstopsState park_move_endstops(true);
        do_homing_move((AxisEnum)(Z_AXIS), amount_mm - current_position.z, MMM_TO_MMS(HOMING_FEEDRATE_INVERTED_Z), false);
        current_position.z = amount_mm;
        sync_plan_position();
    }
}

PausePrivatePhase::PausePrivatePhase()
    : phase(PhasesLoadUnload::initial) {
}

void PausePrivatePhase::setPhase(PhasesLoadUnload ph) {
    phase = ph;
    if (load_unload_mode) {
        log_info(MarlinServer, "setPhase %i %i", int(ph), int(state));
        marlin_server::fsm_change(phase, fsm::serialize_data(FSMLoadUnloadData { .mode = *load_unload_mode, .progress = progress_mapper.current_progress() }));
    }
}

Response PausePrivatePhase::getResponse() {
    return marlin_server::get_response_from_phase(phase);
}

Pause &Pause::Instance() {
    static Pause instance;
    return instance;
}

bool Pause::is_unstoppable() const {
    switch (load_type) {
    case LoadType::load:
        return FSensors_instance().HasMMU();
    case LoadType::filament_change:
    case LoadType::filament_stuck:
        return true;
    case LoadType::autoload:
    case LoadType::load_purge:
    case LoadType::unload:
    case LoadType::unload_confirm:
    case LoadType::load_to_gears:
    case LoadType::unload_from_gears:
        return false;
    }

    bsod("Unhandled LoadType");
}

LoadUnloadMode Pause::get_load_unload_mode() {
    switch (load_type) {
    case Pause::LoadType::load:
    case Pause::LoadType::autoload:
    case Pause::LoadType::load_to_gears:
        return LoadUnloadMode::Load;
    case Pause::LoadType::load_purge:
        return LoadUnloadMode::Purge;
    case Pause::LoadType::unload:
    case Pause::LoadType::unload_confirm:
    case Pause::LoadType::unload_from_gears:
        return LoadUnloadMode::Unload;
    case Pause::LoadType::filament_change:
        return LoadUnloadMode::Change;
    case Pause::LoadType::filament_stuck:
        return LoadUnloadMode::FilamentStuck;
    }

    bsod("Unhandled LoadType");
}

bool Pause::should_park() {
    switch (load_type) {
    case Pause::LoadType::load_purge:
        return true;
    case Pause::LoadType::load_to_gears:
        return !FSensors_instance().has_filament_surely(LogicalFilamentSensor::extruder);
    case Pause::LoadType::autoload:
    case Pause::LoadType::load:
        return option::has_human_interactions || !FSensors_instance().has_filament_surely(LogicalFilamentSensor::extruder);
    case Pause::LoadType::unload_from_gears:
        return false;
    default:
        return true;
    }
}

bool Pause::is_target_temperature_safe() {
    buddy::safety_timer().reset_restore_nonblocking();

#if HAS_AUTO_RETRACT()
    if (load_type == LoadType::unload && auto_retract().is_safely_retracted_for_unload(hotend_from_extruder(active_extruder))) {
        return true;
    }
#endif
    if (!DEBUGGING(DRYRUN) && thermalManager.targetTooColdToExtrude(active_extruder)) {
        SERIAL_ECHO_MSG(MSG_ERR_HOTEND_TOO_COLD);
        return false;
    }
    return true;
}

bool Pause::ensureSafeTemperatureNotifyProgress() {
    buddy::SafetyTimerBlocker safety_timer_blocker;

    if (!is_target_temperature_safe()) {
        return false;
    }

    const auto is_temperature_reached = [] {
        return buddy::safety_timer().state() == buddy::SafetyTimer::State::idle
            && Temperature::degHotend(active_extruder) + heating_phase_min_hotend_diff > Temperature::degTargetHotend(active_extruder);
    };

    if (is_temperature_reached()) {
        return true;
    }

    setPhase(is_unstoppable() ? PhasesLoadUnload::WaitingTemp_unstoppable : PhasesLoadUnload::WaitingTemp_stoppable);

    PauseFsmNotifier notifier(*this, Temperature::degHotend(active_extruder),
        Temperature::degTargetHotend(active_extruder) - heating_phase_min_hotend_diff, marlin_vars().hotend(active_extruder).temp_nozzle);

    while (!is_temperature_reached()) {
        if (check_user_stop(getResponse())) {
            return false;
        }
        idle(true);
    }

    if (Temperature::degTargetHotend(active_extruder) == 0) {
        return false;
    }

    return true;
}

[[nodiscard]] Pause::StopConditions Pause::do_e_move_notify_progress(const float &length, const feedRate_t &fr_mm_s, StopConditions check_for) {
    PauseFsmNotifier notifier(*this, current_position.e, current_position.e + length, marlin_vars().native_pos[MARLIN_VAR_INDEX_E]);

    mapi::extruder_move(length, fr_mm_s);
    return wait_for_motion_finish_stoppable(check_for);
}

[[nodiscard]] Pause::StopConditions Pause::do_e_move_notify_progress_coldextrude(const float &length, const feedRate_t &fr_mm_s, StopConditions check_for) {
    AutoRestore cold_extrude_guard(thermalManager.allow_cold_extrude, true);
    return do_e_move_notify_progress(length, fr_mm_s, check_for);
}

[[nodiscard]] Pause::StopConditions Pause::do_e_move_notify_progress_hotextrude(const float &length, const feedRate_t &fr_mm_s, StopConditions check_for) {
    PhasesLoadUnload last_phase = getPhase();

    if (!ensureSafeTemperatureNotifyProgress()) {
        return StopConditions::Failed;
    }

    setPhase(last_phase);
    return do_e_move_notify_progress(length, fr_mm_s, check_for);
}

void Pause::plan_e_move(const float &length, const feedRate_t &fr_mm_s) {
    while (!mapi::extruder_move(length, fr_mm_s) && !planner.draining()) {
        delay(50);
    }
}

bool Pause::tool_change([[maybe_unused]] uint8_t target_extruder, [[maybe_unused]] LoadType load_type_,
    [[maybe_unused]] const pause::Settings &settings_) {
#if HAS_TOOLCHANGER()
    if (target_extruder != active_extruder) {
        settings = settings_;
        load_type = load_type_;

        settings.park_pos.x = std::numeric_limits<float>::quiet_NaN();
        settings.park_pos.y = std::numeric_limits<float>::quiet_NaN();

        FSM_HolderLoadUnload holder(*this);
        setPhase(PhasesLoadUnload::ChangingTool);

        return prusa_toolchanger.tool_change(target_extruder, tool_return_t::no_return, current_position, tool_change_lift_t::no_lift, false);
    }
#endif

    return true;
}

bool Pause::perform(LoadType load_type_, const pause::Settings &settings_) {
    load_type = load_type_;
    settings = settings_;
    return invoke_loop();
}

bool Pause::invoke_loop() {
#if ENABLED(PID_EXTRUSION_SCALING)
    bool extrusion_scaling_enabled = thermalManager.getExtrusionScalingEnabled();
    thermalManager.setExtrusionScalingEnabled(false);
#endif

    FSM_HolderLoadUnload holder(*this);
    buddy::SafetyTimerNonBlockingGuard non_blocking_guard;

    set(LoadState::start);

    while (!finished()) {
        auto response { getResponse() };
        if (planner.draining() || check_user_stop(response)) {
            set(LoadState::stop);
        }
        (this->*(state_handlers[state]))(response);
        idle(true);
    };

#if ENABLED(PID_EXTRUSION_SCALING)
    thermalManager.setExtrusionScalingEnabled(extrusion_scaling_enabled);
#endif

    return finished_ok();
}

Pause::FSM_HolderLoadUnload::FSM_HolderLoadUnload(Pause &pause_)
    : FSM_Holder(PhasesLoadUnload::initial)
    , pause(pause_) {
    pause.set_mode(pause.get_load_unload_mode());
    if (pause.should_park()) {
        pause.park_nozzle_and_notify();
    }
    active = true;
    original_print_fan_speed = thermalManager.get_fan_speed(0);
    thermalManager.set_fan_speed(0, 0);
}

Pause::FSM_HolderLoadUnload::~FSM_HolderLoadUnload() {
    thermalManager.set_fan_speed(0, original_print_fan_speed);
    active = false;

    const float min_layer_height = 0.05f;
    if (!axes_need_homing() && pause.settings.resume_pos.z != NAN && std::abs(current_position.z - pause.settings.resume_pos.z) >= min_layer_height && (marlin_client::is_printing() || marlin_client::is_paused())) {
        if (!pause.ensureSafeTemperatureNotifyProgress()) {
            return;
        }
        pause.unpark_nozzle_and_notify();
    }
    pause.clr_mode();
}

bool Pause::FSM_HolderLoadUnload::active = false;
