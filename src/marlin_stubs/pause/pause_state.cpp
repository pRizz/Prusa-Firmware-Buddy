#include "pause_internal.hpp"

LOG_COMPONENT_REF(MarlinServer);

void Pause::start_process([[maybe_unused]] Response response) {
    setup_progress_mapper();

    switch (load_type) {
    case LoadType::load:
    case LoadType::autoload:
    case LoadType::load_to_gears:
    case LoadType::load_purge:
        set(LoadState::load_start);
        break;
    case LoadType::unload:
    case LoadType::unload_confirm:
    case LoadType::unload_from_gears:
    case LoadType::filament_change:
    case LoadType::filament_stuck:
        set(LoadState::unload_start);
        break;
    }
}

void Pause::load_start_process([[maybe_unused]] Response response) {
    // TODO: this shouldn't be needed here
    // actual temperature does not matter, only target
    if (!is_target_temperature_safe() && load_type != LoadType::load_to_gears && option::has_human_interactions) {
        set(LoadState::stop);
        return;
    }

#if HAS_MMU2()
    if (FSensors_instance().HasMMU()) {
        set(LoadState::mmu_load_start);
        return;
    }
#endif

    switch (load_type) {
    case LoadType::load_to_gears:
        // if extruder sensor is not working, we cannot load filament automatically, we need the user to manually confirm the the filament is pushed in
        if (!FSensors_instance().is_working(LogicalFilamentSensor::extruder)) {
            set(LoadState::filament_push_ask);
            break;
        }
        // If we are loading and filament is not in extruder = loading triggered by sideFS -> need asisting
        if (FSensors_instance().no_filament_surely(LogicalFilamentSensor::extruder)) {
            set_timed(LoadState::assist_insertion);
        } else {
            set(LoadState::load_to_gears);
        }
        break;

    case LoadType::autoload:
        // if filament is not present we want to break and not set loaded filament
        // we have already loaded the filament in gear, now just wait for temperature to rise
        config_store().set_filament_type(settings.GetExtruder(), filament::get_type_to_load());
        set(LoadState::load_wait_temp);
        handle_filament_removal(LoadState::filament_push_ask);
        break;
    case LoadType::load_purge:
        set(LoadState::load_wait_temp);
        break;
    default:
        if (option::has_side_fsensor && settings.extruder_mmu_rework) {
            if (FSensors_instance().has_filament_surely(LogicalFilamentSensor::extruder)) {
                set(LoadState::move_to_purge);
            } else {
                set_timed(LoadState::await_filament);
            }
        } else {
            set(LoadState::filament_push_ask);
        }
        break;
    }
}

void Pause::filament_push_ask_process(Response response) {
    if constexpr (!option::has_human_interactions) {
        setPhase(is_unstoppable() ? PhasesLoadUnload::Inserting_unstoppable : PhasesLoadUnload::Inserting_stoppable);

        if (FSensors_instance().has_filament_surely(LogicalFilamentSensor::extruder)) {
            set(LoadState::move_to_purge);
        } else if constexpr (option::has_side_fsensor) {
            set_timed(LoadState::await_filament);
        } else {
            set(LoadState::load_to_gears);
        }

        return;
    }

    if (FSensors_instance().no_filament_surely(LogicalFilamentSensor::extruder)) {
        setPhase(is_unstoppable() ? PhasesLoadUnload::MakeSureInserted_unstoppable : PhasesLoadUnload::MakeSureInserted_stoppable);
        handle_help(response);

        // With extruder MMU rework, we gotta assist the user with inserting the filament
        // BFW-5134
        if (settings.extruder_mmu_rework) {
#if ENABLED(PREVENT_COLD_EXTRUSION)
            AutoRestore ar_ce(thermalManager.allow_cold_extrude, true);
#endif
            mapi::extruder_schedule_turning(3);
        }

    } else {
        setPhase(is_unstoppable() ? PhasesLoadUnload::UserPush_unstoppable : PhasesLoadUnload::UserPush_stoppable);
        const bool has_filament = FSensors_instance().has_filament_surely(LogicalFilamentSensor::extruder);
        const bool is_mmu_rework_and_has_filament = settings.extruder_mmu_rework && has_filament;
        const bool side_fs_empty = FSensors_instance().no_filament_surely(LogicalFilamentSensor::side);
        const bool extruder_fs_not_working = !FSensors_instance().is_working(LogicalFilamentSensor::extruder);

        if (response == Response::Continue || is_mmu_rework_and_has_filament) {
            set(LoadState::load_to_gears);
        } else if (!is_unstoppable() && side_fs_empty && extruder_fs_not_working) {
            set(LoadState::stop);
        }
    }
}

void Pause::await_filament_process([[maybe_unused]] Response response) {
    setPhase(is_unstoppable() ? PhasesLoadUnload::AwaitingFilament_unstoppable : PhasesLoadUnload::AwaitingFilament_stoppable);
    if (!FSensors_instance().is_working(LogicalFilamentSensor::extruder) || (!is_unstoppable() && ticks_diff(ticks_ms(), start_time_ms) > 10 * 60 * 1000)) {
        marlin_server::set_warning(WarningType::FilamentLoadingTimeout);
        set(LoadState::stop);
        return;
    }

    if (!FSensors_instance().no_filament_surely(LogicalFilamentSensor::side)) {
        mapi::home_if_needed_and_park(mapi::ZAction::no_move, mapi::park_positions[mapi::ParkPosition::load]);
        if (settings.extruder_mmu_rework) {
            set_timed(LoadState::assist_insertion);
        } else {
            set(LoadState::filament_push_ask);
        }
        return;
    }
}

void Pause::runout_during_load_process([[maybe_unused]] Response response) {
    setPhase(PhasesLoadUnload::Ejecting_unstoppable);
    std::ignore = do_e_move_notify_progress_coldextrude(-std::abs(settings.unload_length), (FILAMENT_CHANGE_UNLOAD_FEEDRATE), StopConditions::Accomplished);

    switch (load_type) {
    case LoadType::load_to_gears:
    case LoadType::filament_change:
    case LoadType::filament_stuck:
        set(LoadState::load_start);
        break;
    case LoadType::load:
    case LoadType::autoload:
        set(LoadState::filament_push_ask);
        break;
    default:
        break;
    }
}

void Pause::assist_insertion_process([[maybe_unused]] Response response) {
    const bool unstoppable { is_unstoppable() };
    setPhase(unstoppable ? PhasesLoadUnload::Inserting_unstoppable : PhasesLoadUnload::Inserting_stoppable);

    if (FSensors_instance().has_filament_surely(LogicalFilamentSensor::extruder)) {
        set(LoadState::load_to_gears);
        return;
    }

    if (ticks_diff(ticks_ms(), start_time_ms) > 40000) {
        set(unstoppable ? LoadState::load_start : LoadState::stop);
        return;
    }

    if (FSensors_instance().no_filament_surely(LogicalFilamentSensor::side)) {
        set(LoadState::unload_finish_or_change);
        return;
    }

#if ENABLED(PREVENT_COLD_EXTRUSION)
    AutoRestore<bool> cold_extrusion_restore(thermalManager.allow_cold_extrude);
    thermalManager.allow_cold_extrude = true;
#endif
    mapi::extruder_schedule_turning(FILAMENT_CHANGE_SLOW_LOAD_FEEDRATE, 0.1f);
}

void Pause::load_to_gears_process([[maybe_unused]] Response response) {
    setPhase(is_unstoppable() ? PhasesLoadUnload::LoadingToGears_unstoppable : PhasesLoadUnload::LoadingToGears_stoppable);

    const auto result = do_e_move_notify_progress_coldextrude(settings.slow_load_length, FILAMENT_CHANGE_SLOW_LOAD_FEEDRATE, StopConditions::All);

    if (result == StopConditions::SideFilamentSensorRunout) {
        set(LoadState::runout_during_load);
        return;
    }

    if (result == StopConditions::UserStopped) {
        set(LoadState::stop);
        return;
    }

    if (load_type == LoadType::load_to_gears) {
        set(LoadState::_finished);
    } else {
        set(LoadState::move_to_purge);
    }
    handle_filament_removal(LoadState::filament_push_ask);
}

void Pause::move_to_purge_process([[maybe_unused]] Response response) {
    if constexpr (option::has_side_fsensor) {
        mapi::home_if_needed_and_park(mapi::ZAction::no_move, mapi::park_positions[mapi::ParkPosition::purge]);
    }
    set(LoadState::load_wait_temp);
}

void Pause::load_wait_temp_process([[maybe_unused]] Response response) {
    if (ensureSafeTemperatureNotifyProgress()) {
        if (load_type == LoadType::load_purge) {
            set(LoadState::purge);
        } else {
            set(LoadState::long_load);
        }
    }
    handle_filament_removal(LoadState::filament_push_ask);
}

void Pause::unload_wait_temp_process([[maybe_unused]] Response response) {
    if (!ensureSafeTemperatureNotifyProgress()) {
        return;
    }

    set(LoadState::ram_sequence);
}

void Pause::long_load_process([[maybe_unused]] Response response) {
    setPhase(is_unstoppable() ? PhasesLoadUnload::Loading_unstoppable : PhasesLoadUnload::Loading_stoppable);

    const float saved_acceleration = planner.user_settings.retract_acceleration;
    {
        auto planner_settings = planner.user_settings;
        planner_settings.retract_acceleration = FILAMENT_CHANGE_FAST_LOAD_ACCEL;
        planner.apply_settings(planner_settings);
    }

    auto move_e_progress = do_e_move_notify_progress_hotextrude(settings.fast_load_length, FILAMENT_CHANGE_FAST_LOAD_FEEDRATE, StopConditions::All);

    {
        auto planner_settings = planner.user_settings;
        planner_settings.retract_acceleration = saved_acceleration;
        planner.apply_settings(planner_settings);
    }

    if (move_e_progress == StopConditions::SideFilamentSensorRunout) {
        set(LoadState::runout_during_load);
        return;
    }

    set(LoadState::purge);
    handle_filament_removal(LoadState::filament_push_ask);
}

static constexpr float retract_distance = -4.f;
static constexpr feedRate_t retract_feedrate = 35;

void Pause::purge_process([[maybe_unused]] Response response) {
    setPhase(is_unstoppable() ? PhasesLoadUnload::Purging_unstoppable : PhasesLoadUnload::Purging_stoppable);

    planner.synchronize();
    const auto purge_result = do_e_move_notify_progress_hotextrude(settings.purge_length(), ADVANCED_PAUSE_PURGE_FEEDRATE, StopConditions::All);
    if (purge_result == StopConditions::SideFilamentSensorRunout) {
        set(LoadState::runout_during_load);
        return;
    }
    if (purge_result == StopConditions::UserStopped) {
        planner.quick_stop_and_resume();
    }
    if (purge_result != StopConditions::Failed) {
        std::ignore = do_e_move_notify_progress_hotextrude(retract_distance, retract_feedrate, StopConditions::UserStopped);
    }

    config_store().set_filament_type(settings.GetExtruder(), filament::get_type_to_load());

    if constexpr (!option::has_human_interactions) {
        set(LoadState::load_prime);
        return;
    }

    setPhase(load_type == LoadType::load_purge ? PhasesLoadUnload::IsColorPurge : PhasesLoadUnload::IsColor);
    set(LoadState::color_correct_ask);
    handle_filament_removal(LoadState::filament_push_ask);
}

void Pause::color_correct_ask_process(Response response) {
    switch (response) {
    case Response::Purge_more:
        set(LoadState::purge);
        break;
    case Response::Retry:
        set(LoadState::eject);
        break;
    case Response::Yes:
        set(LoadState::load_prime);
        break;
    default:
        if (!FSensors_instance().HasMMU()) {
            handle_filament_removal(LoadState::filament_push_ask);
        }
    }
}

#if HAS_MMU2()
void Pause::mmu_load_start_process([[maybe_unused]] Response response) {
    if (load_type == LoadType::load) {
        if (!MMU2::mmu2.load_filament_to_nozzle(settings.mmu_filament_to_load)) {
            set(LoadState::load_prime);
            return;
        }

        config_store().set_filament_type(settings.GetExtruder(), filament::get_type_to_load());
        setPhase(PhasesLoadUnload::IsColor);
        set(LoadState::color_correct_ask);
    } else if (load_type == LoadType::filament_change) {
        if (settings.mmu_filament_to_load == MMU2::FILAMENT_UNKNOWN) {
            set(LoadState::load_prime);
            return;
        }

        setPhase(PhasesLoadUnload::LoadFilamentIntoMMU);
        set(LoadState::mmu_load_ask);
    }
}

void Pause::mmu_load_ask_process(Response response) {
    if (response == Response::Continue) {
        set(LoadState::mmu_load);
    }
}

void Pause::mmu_load_process([[maybe_unused]] Response response) {
    if (settings.mmu_filament_to_load == MMU2::FILAMENT_UNKNOWN) {
        set(LoadState::load_prime);
        return;
    }

    MMU2::mmu2.load_filament(settings.mmu_filament_to_load);
    MMU2::mmu2.load_filament_to_nozzle(settings.mmu_filament_to_load);

    setPhase(PhasesLoadUnload::IsColor);
    set(LoadState::color_correct_ask);
}

void Pause::mmu_unload_start_process([[maybe_unused]] Response response) {
    if (load_type == LoadType::unload) {
        MMU2::mmu2.unload();
        set(LoadState::_finished);
    } else if (load_type == LoadType::filament_change) {
        settings.mmu_filament_to_load = MMU2::mmu2.get_current_tool();
        if (settings.mmu_filament_to_load == MMU2::FILAMENT_UNKNOWN) {
            set(LoadState::unload_finish_or_change);
            return;
        }

        MMU2::mmu2.unload();
        MMU2::mmu2.eject_filament(settings.mmu_filament_to_load);
        set(LoadState::unload_finish_or_change);
    }
}
#endif

void Pause::eject_process([[maybe_unused]] Response response) {
#if HAS_MMU2()
    if (FSensors_instance().HasMMU()) {
        MMU2::mmu2.unload();
        if (load_type == LoadType::filament_change) {
            set(LoadState::mmu_load);
        } else {
            set(LoadState::load_start);
        }
        return;
    }
#endif

    if (!ram_filament()) {
        return;
    }

    setPhase(is_unstoppable() ? PhasesLoadUnload::Ejecting_unstoppable : PhasesLoadUnload::Ejecting_stoppable);
    unload_filament();

    switch (load_type) {
    case LoadType::load_to_gears:
    case LoadType::filament_change:
    case LoadType::filament_stuck:
        set(LoadState::load_start);
        break;
    case LoadType::load:
    case LoadType::autoload:
        set(LoadState::filament_push_ask);
        break;
    default:
        break;
    }
}

void Pause::load_prime_process([[maybe_unused]] Response response) {
#if HAS_AUTO_RETRACT()
    if (!marlin_server::is_printing()) {
        set(LoadState::auto_retract);
        return;
    }
#endif

    if (load_type == LoadType::filament_change || load_type == LoadType::filament_stuck) {
        plan_e_move(std::abs(retract_distance), 10);

        if (settings.retract) {
            plan_e_move(settings.retract, PAUSE_PARK_RETRACT_FEEDRATE);
        }

        planner.synchronize();
        delay(500);
    }

#if HAS_NOZZLE_CLEANER()
    switch (load_type) {
    case LoadType::load:
    case LoadType::autoload:
    case LoadType::load_to_gears:
    case LoadType::load_purge:
        nozzle_cleaner_gcode_loader.load_gcode(nozzle_cleaner::load_filename, nozzle_cleaner::load_sequence);
        break;
    case LoadType::filament_change:
    case LoadType::filament_stuck:
        nozzle_cleaner_gcode_loader.load_gcode(nozzle_cleaner::runout_filename, nozzle_cleaner::runout_sequence);
        break;
    default:
        break;
    }

    set(LoadState::load_nozzle_clean);
    return;
#endif

    set(LoadState::_finished);
}

#if HAS_NOZZLE_CLEANER()
void Pause::load_nozzle_clean_process([[maybe_unused]] Response response) {
    setPhase(PhasesLoadUnload::LoadNozzleCleaning);
    auto loader_result = nozzle_cleaner_gcode_loader.get_result();

    if (loader_result.has_value()) {
        GcodeSuite::process_subcommands_now(loader_result.value());
    }

    if (loader_result.has_value() || loader_result.error() != GCodeLoader::BufferState::buffering) {
        nozzle_cleaner_gcode_loader.reset();
        set(LoadState::_finished);
    }
}
#endif

void Pause::stop_process([[maybe_unused]] Response response) {
    if (!planner.busy()) {
        set(LoadState::_stopped);
        return;
    }

    planner.quick_stop_and_resume();
    xyze_pos_t real_current_position;
    planner.get_axis_position_mm(static_cast<xyz_pos_t &>(real_current_position));
    real_current_position[E_AXIS] = 0;
#if HAS_POSITION_MODIFIERS
    planner.unapply_modifiers(real_current_position
    #if HAS_LEVELING
        ,
        true
    #endif
    );
#endif

    if (xyz_pos_t(current_position) != xyz_pos_t(real_current_position)) {
        set_all_unhomed();
    }

    current_position = real_current_position;
    planner.set_position_mm(current_position);

    set(LoadState::_stopped);
}
