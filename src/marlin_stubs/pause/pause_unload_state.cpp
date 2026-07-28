#include "pause_internal.hpp"

LOG_COMPONENT_REF(MarlinServer);

void Pause::unload_start_process([[maybe_unused]] Response response) {
    if (!(load_type == LoadType::unload && FSensors_instance().HasMMU()) && !is_target_temperature_safe() && load_type != LoadType::unload_from_gears) {
        set(LoadState::stop);
        return;
    }

#if HAS_MMU2()
    if (FSensors_instance().HasMMU()) {
        set(LoadState::mmu_unload_start);
        return;
    }
#endif

    switch (load_type) {
    case LoadType::filament_stuck:
#if HAS_LOADCELL()
        set(LoadState::filament_stuck_ask);
#else
        set(LoadState::manual_unload);
#endif
        break;
    case LoadType::unload_from_gears:
        set(LoadState::unload_from_gears);
        break;
    default:
        set(LoadState::unload_wait_temp);
        break;
    }
}

#if HAS_LOADCELL()
void Pause::filament_stuck_ask_process(Response response) {
    setPhase(PhasesLoadUnload::FilamentStuck);

    if (response == Response::Unload) {
        set(LoadState::unload_wait_temp);
    }
}
#endif

#if HAS_AUTO_RETRACT()
void Pause::auto_retract_process([[maybe_unused]] Response response) {
    setPhase(PhasesLoadUnload::AutoRetracting);
    PauseFsmDurationNotifier progress_notifier(*this, standard_ramming_sequence(StandardRammingSequence::auto_retract, marlin_vars().active_hotend_id()).duration_estimate_ms());
    auto_retract().maybe_retract_from_nozzle();
    set(LoadState::_finished);
}
#endif

void Pause::ram_sequence_process([[maybe_unused]] Response response) {
#if HAS_AUTO_RETRACT()
    if (auto_retract().is_safely_retracted_for_unload()) {
        ram_retracted_distance = auto_retract().retracted_distance().value();
        set(LoadState::unload);
        return;
    }
#endif

    if (ram_filament()) {
        set(LoadState::unload);
    }
}

void Pause::unload_process([[maybe_unused]] Response response) {
    setPhase(is_unstoppable() ? PhasesLoadUnload::Unloading_unstoppable : PhasesLoadUnload::Unloading_stoppable);
    unload_filament();

    config_store().set_filament_type(settings.GetExtruder(), FilamentType::none);

    switch (load_type) {
    case LoadType::unload:
        if constexpr (option::has_human_interactions) {
            set(LoadState::unload_finish_or_change);
            break;
        }
    case LoadType::unload_confirm:
    case LoadType::filament_change:
    case LoadType::filament_stuck:
#if HAS_NOZZLE_CLEANER()
        nozzle_cleaner_gcode_loader.load_gcode(nozzle_cleaner::unload_filename, nozzle_cleaner::unload_sequence);
        set(LoadState::unload_nozzle_clean);
        return;
#endif

        if constexpr (!option::has_human_interactions) {
            runout_timer_ms = ticks_ms();
            set(LoadState::filament_not_in_fs);
        } else {
            set(LoadState::unloaded_ask);
        }
        break;
    default:
        break;
    }
}

void Pause::unloaded_ask_process(Response response) {
    setPhase(PhasesLoadUnload::IsFilamentUnloaded);

    if (response == Response::Yes) {
        set(LoadState::filament_not_in_fs);
        return;
    }
    if (response == Response::No) {
        disable_e_stepper(active_extruder);
        set(LoadState::manual_unload);
    }
}

void Pause::unload_from_gears_process([[maybe_unused]] Response response) {
    setPhase(PhasesLoadUnload::Unloading_stoppable);

    std::ignore = do_e_move_notify_progress_coldextrude(-settings.slow_load_length * (float)1.5, FILAMENT_CHANGE_FAST_LOAD_FEEDRATE, StopConditions::UserStopped);
    set(LoadState::unload_finish_or_change);
}

#if HAS_NOZZLE_CLEANER()
void Pause::unload_nozzle_clean_process([[maybe_unused]] Response response) {
    setPhase(PhasesLoadUnload::UnloadNozzleCleaning);
    auto loader_result = nozzle_cleaner_gcode_loader.get_result();

    if (loader_result.has_value()) {
        GcodeSuite::process_subcommands_now(loader_result.value());
    }

    if (loader_result.has_value() || loader_result.error() != GCodeLoader::BufferState::buffering) {
        nozzle_cleaner_gcode_loader.reset();
        if constexpr (!option::has_human_interactions) {
            runout_timer_ms = ticks_ms();
            set(LoadState::filament_not_in_fs);
        } else {
            set(LoadState::unloaded_ask);
        }
    }
}
#endif

void Pause::unload_finish_or_change_process([[maybe_unused]] Response response) {
    if (load_type == LoadType::filament_change || load_type == LoadType::filament_stuck) {
        set(LoadState::load_start);
    } else {
        set(LoadState::_finished);
    }
}

void Pause::filament_not_in_fs_process(Response response) {
    setPhase(PhasesLoadUnload::FilamentNotInFS);
    handle_help(response);
    if (!FSensors_instance().has_filament_surely(settings.extruder_mmu_rework ? LogicalFilamentSensor::primary_runout : LogicalFilamentSensor::secondary_runout)) {
        if constexpr (!option::has_human_interactions) {
            if (ticks_diff(ticks_ms(), runout_timer_ms) < 1000) {
                return;
            }
        }

        set(LoadState::unload_finish_or_change);
    } else if constexpr (!option::has_human_interactions) {
        runout_timer_ms = ticks_ms();
    }
}

void Pause::manual_unload_process(Response response) {
    const bool can_continue = !FSensors_instance().has_filament_surely(LogicalFilamentSensor::extruder);
    setPhase(can_continue ? PhasesLoadUnload::ManualUnload_continuable : PhasesLoadUnload::ManualUnload_uncontinuable);
    handle_help(response);

    if (response == Response::Continue && can_continue) {
        enable_e_steppers();
        set(LoadState::unload_finish_or_change);
    } else if (response == Response::Retry) {
        enable_e_steppers();
        set(LoadState::ram_sequence);
    }
}

bool Pause::ram_filament() {
    if (!ensureSafeTemperatureNotifyProgress()) {
        return false;
    }

    setPhase(is_unstoppable() ? PhasesLoadUnload::Ramming_unstoppable : PhasesLoadUnload::Ramming_stoppable);

    const RammingSequence *ramming_sequence = nullptr;
    switch (load_type) {
    case LoadType::filament_change:
    case LoadType::filament_stuck:
        ramming_sequence = &runoutRammingSequence;
        break;
    default:
        ramming_sequence = &unloadRammingSequence;
        break;
    }

    PauseFsmDurationNotifier notifier(*this, ramming_sequence->duration_estimate_ms());
    ram_retracted_distance = ramming_sequence->retracted_distance();
    ramming_sequence->execute([this] {
        return !check_user_stop(getResponse());
    });
    return true;
}

void Pause::unload_filament() {
    const float saved_acceleration = planner.user_settings.retract_acceleration;
    {
        auto planner_settings = planner.user_settings;
        planner_settings.retract_acceleration = FILAMENT_CHANGE_UNLOAD_ACCEL;
        planner.apply_settings(planner_settings);
    }

    const float remaining_unload_length = std::max<float>(std::abs(settings.unload_length) - ram_retracted_distance, 0);
    std::ignore = do_e_move_notify_progress_coldextrude(-remaining_unload_length, (FILAMENT_CHANGE_UNLOAD_FEEDRATE), StopConditions::UserStopped);

    {
        auto planner_settings = planner.user_settings;
        planner_settings.retract_acceleration = saved_acceleration;
        planner.apply_settings(planner_settings);
    }
}

bool Pause::check_user_stop(Response response) {
    if (response != Response::Stop) {
        return false;
    }
    set(LoadState::stop);
    return true;
}

void Pause::handle_filament_removal(LoadState state_to_set) {
    if (FSensors_instance().no_filament_surely(LogicalFilamentSensor::extruder)) {
        set(state_to_set);
        config_store().set_filament_type(settings.GetExtruder(), FilamentType::none);
    }
}

void Pause::handle_help(Response response) {
    if (response != Response::Help) {
        return;
    }

    WarningType warning = WarningType::FilamentSensorStuckHelp;
#if HAS_MMU2()
    if (MMU2::mmu2.Enabled()) {
        warning = WarningType::FilamentSensorStuckHelpMMU;
    }
#endif

    if (marlin_server::prompt_warning(warning) == Response::FS_disable) {
        FSensors_instance().set_enabled_global(false);
        while (FSensors_instance().is_enable_state_update_processing()) {
            idle(true);
        }
        marlin_server::set_warning(WarningType::FilamentSensorsDisabled);
        config_store().show_fsensors_disabled_warning_after_print.set(true);
    }
}

void Pause::setup_progress_mapper() {
    using LoadState = PausePrivatePhase::LoadState;
    using WorkflowStep = ProgressMapperWorkflowStep<LoadState>;

    const ProgressMapperWorkflow<LoadState> *result = nullptr;

    switch (load_type) {
    case LoadType::load_to_gears: {
        constexpr static ProgressMapperWorkflowArray workflow { std::to_array<WorkflowStep>({
            { LoadState::load_to_gears, 1 },
        }) };
        result = &workflow;
        break;
    }
    case LoadType::load:
    case LoadType::autoload: {
        constexpr static ProgressMapperWorkflowArray workflow { std::to_array<WorkflowStep>({
            { LoadState::load_to_gears, 1 },
            { LoadState::load_wait_temp, 3 },
            { LoadState::long_load, 1 },
            { LoadState::purge, 1 },
#if HAS_AUTO_RETRACT()
            { LoadState::auto_retract, 1 },
#endif
        }) };
        result = &workflow;
        break;
    }
    case LoadType::load_purge: {
        constexpr static ProgressMapperWorkflowArray workflow { std::to_array<WorkflowStep>({
            { LoadState::load_wait_temp, 3 },
            { LoadState::purge, 1 },
#if HAS_AUTO_RETRACT()
            { LoadState::auto_retract, 1 },
#endif
        }) };
        result = &workflow;
        break;
    }
    case LoadType::unload:
    case LoadType::unload_confirm:
    case LoadType::filament_stuck: {
        constexpr static ProgressMapperWorkflowArray workflow { std::to_array<WorkflowStep>({
            { LoadState::unload_wait_temp, 3 },
            { LoadState::ram_sequence, 2 },
            { LoadState::unload, 1 },
        }) };
        result = &workflow;
        break;
    }
    case LoadType::unload_from_gears: {
        constexpr static ProgressMapperWorkflowArray workflow { std::to_array<WorkflowStep>({
            { LoadState::unload_from_gears, 1 },
        }) };
        result = &workflow;
        break;
    }
    case LoadType::filament_change: {
        constexpr static ProgressMapperWorkflowArray workflow { std::to_array<WorkflowStep>({
            { LoadState::unload_wait_temp, 3 },
            { LoadState::ram_sequence, 1 },
            { LoadState::long_load, 2 },
            { LoadState::purge, 1 },
#if HAS_AUTO_RETRACT()
            { LoadState::auto_retract, 1 },
#endif
        }) };
        result = &workflow;
        break;
    }
    };

    progress_mapper.setup(*result);
}
