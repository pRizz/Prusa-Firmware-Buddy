#include "pause_internal.hpp"

LOG_COMPONENT_REF(MarlinServer);

uint32_t Pause::parkMoveZPercent(float z_move_len, float xy_move_len) const {
    const float z_time_ratio = std::abs(z_move_len / float(NOZZLE_PARK_Z_FEEDRATE));
    const float xy_time_ratio = std::abs(xy_move_len / float(NOZZLE_PARK_XY_FEEDRATE));

    if (!isfinite(z_time_ratio)) {
        return 100;
    }
    if (!isfinite(xy_time_ratio)) {
        return 0;
    }
    if ((z_time_ratio + xy_time_ratio) == 0) {
        return 50;
    }

    return 100.f * (z_time_ratio / (z_time_ratio + xy_time_ratio));
}

uint32_t Pause::parkMoveXYPercent(float z_move_len, float xy_move_len) const {
    return 100 - parkMoveZPercent(z_move_len, xy_move_len);
}

bool Pause::parkMoveXGreaterThanY(const xyz_pos_t &pos0, const xyz_pos_t &pos1) const {
    xy_bool_t pos_nan;
    LOOP_XY(axis) {
        pos_nan.pos[axis] = isnan(pos0.pos[axis]) || isnan(pos1.pos[axis]);
    }

    if (pos_nan.y) {
        return true;
    }
    if (pos_nan.x) {
        return false;
    }

    return std::abs(pos0.x - pos1.x) > std::abs(pos0.y - pos1.y);
}

[[nodiscard]] Pause::StopConditions Pause::wait_for_motion_finish_stoppable(StopConditions check_for) {
    while (planner.processing()) {
        if (check4(check_for, StopConditions::UserStopped) && check_user_stop(getResponse())) {
            return StopConditions::UserStopped;
        }
        if (check4(check_for, StopConditions::SideFilamentSensorRunout) && FSensors_instance().no_filament_surely(LogicalFilamentSensor::side)) {
            log_info(MarlinServer, "Pause::sideFS runout");
            planner.quick_stop_and_resume();
            return StopConditions::SideFilamentSensorRunout;
        }
        idle(true);
    }
    return StopConditions::Accomplished;
}

void Pause::park_nozzle_and_notify() {
    setPhase(is_unstoppable() ? PhasesLoadUnload::Parking_unstoppable : PhasesLoadUnload::Parking_stoppable);
    if (settings.retract && thermalManager.hotEnoughToExtrude(active_extruder)) {
        do_pause_e_move(settings.retract, PAUSE_PARK_RETRACT_FEEDRATE);
    }

    const float target_z = settings.park_pos.z;
    const float z_length = current_position.z - target_z;
    const float z_feedrate = settings.park_z_feedrate;

    float xy_length = 0;
    float begin_pos = 0;
    float end_pos = 0;
    const bool x_greater_than_y = parkMoveXGreaterThanY(current_position, settings.park_pos);
    if (x_greater_than_y) {
        if (!isnan(settings.park_pos.x)) {
            begin_pos = axes_need_homing(_BV(X_AXIS)) ? float(X_HOME_POS) : current_position.x;
            end_pos = settings.park_pos.x;
            xy_length = begin_pos - end_pos;
        }
    } else if (!isnan(settings.park_pos.y)) {
        begin_pos = axes_need_homing(_BV(Y_AXIS)) ? float(Y_HOME_POS) : current_position.y;
        end_pos = settings.park_pos.y;
        xy_length = begin_pos - end_pos;
    }

    if (isfinite(target_z)) {
        if (axes_need_homing(_BV(Z_AXIS))) {
            unhomed_z_lift(target_z);
        } else {
            PauseFsmExplicitProgressNotifier notifier(*this, current_position.z, target_z, 0, parkMoveZPercent(z_length, xy_length), marlin_vars().native_pos[MARLIN_VAR_INDEX_Z]);
            log_info(MarlinServer, "Parking");
            plan_park_move_to(current_position.x, current_position.y, target_z, NOZZLE_PARK_XY_FEEDRATE, z_feedrate, Segmented::yes);
            log_info(MarlinServer, "Park done");
            if (wait_for_motion_finish_stoppable() == StopConditions::UserStopped) {
                return;
            }
        }
    }

    if (xy_length != 0) {
#if CORE_IS_XY
        if (axes_need_homing(_BV(X_AXIS) | _BV(Y_AXIS))) {
            GcodeSuite::G28_no_parser(true, true, false,
                {
                    .only_if_needed = true,
                    .z_raise = 0,
                    .precise = false,
                });

            static constexpr xyz_pos_t park = XYZ_NOZZLE_PARK_POINT_M600;
            LOOP_XY(axis) {
                if (isnan(settings.park_pos.pos[axis])) {
                    settings.park_pos.pos[axis] = park[axis];
                }
            }
        } else {
            LOOP_XY(axis) {
                if (isnan(settings.park_pos.pos[axis])) {
                    settings.park_pos.pos[axis] = current_position.pos[axis];
                }
            }
        }
#else
        LOOP_XY(axis) {
            if (!isnan(settings.park_pos.pos[axis])) {
                GcodeSuite::G28_no_parser(axis == X_AXIS, axis == Y_AXIS, false,
                    {
                        .only_if_needed = true,
                        .z_raise = 0,
                        .precise = false,
                    });
            }
            if (check_user_stop(getResponse())) {
                return;
            }
            if (isnan(settings.park_pos.pos[axis])) {
                settings.park_pos.pos[axis] = current_position.pos[axis];
            }
        }
#endif

        PauseFsmExplicitProgressNotifier notifier(*this, begin_pos, end_pos, parkMoveZPercent(z_length, xy_length), 100, marlin_vars().native_pos[x_greater_than_y ? MARLIN_VAR_INDEX_X : MARLIN_VAR_INDEX_Y]);
        plan_park_move_to_xyz(settings.park_pos, NOZZLE_PARK_XY_FEEDRATE, z_feedrate, Segmented::yes);
        if (wait_for_motion_finish_stoppable() == StopConditions::UserStopped) {
            return;
        }
    }

    report_current_position();
}

void Pause::unpark_nozzle_and_notify() {
    if (settings.resume_pos.x == NAN || settings.resume_pos.y == NAN || settings.resume_pos.z == NAN) {
        return;
    }

    setPhase(PhasesLoadUnload::Unparking);
    const bool x_greater_than_y = parkMoveXGreaterThanY(current_position, settings.resume_pos);
    const float &begin_pos = x_greater_than_y ? current_position.x : current_position.y;
    const float &end_pos = x_greater_than_y ? settings.resume_pos.x : settings.resume_pos.y;

    const float z_length = current_position.z - settings.resume_pos.z;
    const float xy_length = begin_pos - end_pos;

    GcodeSuite::G28_no_parser(!isnan(settings.park_pos.pos[X_AXIS]), !isnan(settings.park_pos.pos[Y_AXIS]), false,
        {
            .only_if_needed = true,
            .z_raise = 0,
            .precise = false,
        });

    {
        PauseFsmExplicitProgressNotifier notifier(*this, begin_pos, end_pos, 0, parkMoveXYPercent(z_length, xy_length), marlin_vars().native_pos[x_greater_than_y ? MARLIN_VAR_INDEX_X : MARLIN_VAR_INDEX_Y]);
        do_blocking_move_to_xy(settings.resume_pos, NOZZLE_UNPARK_XY_FEEDRATE);
    }

    {
        auto adjusted_resume_position = settings.resume_pos;

#if HAS_LEVELING && !PLANNER_LEVELING
        planner.apply_leveling(adjusted_resume_position);
#endif

        PauseFsmExplicitProgressNotifier notifier(*this, current_position.z, adjusted_resume_position.z, parkMoveXYPercent(z_length, xy_length), 100, marlin_vars().native_pos[MARLIN_VAR_INDEX_Z]);
        do_blocking_move_to_z(adjusted_resume_position.z, feedRate_t(NOZZLE_PARK_Z_FEEDRATE), Segmented::yes);
        current_position.z = settings.resume_pos.z;
    }

    if (settings.retract) {
        plan_e_move(-settings.retract, PAUSE_PARK_RETRACT_FEEDRATE);
    }
}

void Pause::filament_change(const pause::Settings &settings_, bool is_filament_stuck) {
    settings = settings_;
    load_type = is_filament_stuck ? LoadType::filament_stuck : LoadType::filament_change;

    if (did_pause_print) {
        return;
    }

    buddy::safety_timer().reset_restore_nonblocking();

    if (!DEBUGGING(DRYRUN) && settings.unload_length && thermalManager.targetTooColdToExtrude(settings.target_extruder)) {
        SERIAL_ECHO_MSG(MSG_ERR_HOTEND_TOO_COLD);
        return;
    }

    FS_EventAutolock runout_disable;
    ++did_pause_print;

    print_job_timer.pause();
    planner.synchronize();

#if ENABLED(ADVANCED_PAUSE_FANS_PAUSE) && FAN_COUNT > 0
    thermalManager.set_fans_paused(true);
#endif

    invoke_loop();

#if ADVANCED_PAUSE_RESUME_PRIME != 0
    do_pause_e_move(ADVANCED_PAUSE_RESUME_PRIME, feedRate_t(ADVANCED_PAUSE_PURGE_FEEDRATE));
#endif

    planner.set_e_position_mm((destination.e = current_position.e = settings.resume_pos.e));
    --did_pause_print;

#if ENABLED(ADVANCED_PAUSE_FANS_PAUSE) && FAN_COUNT > 0
    thermalManager.set_fans_paused(false);
#endif

    if (print_job_timer.isPaused()) {
        print_job_timer.start();
    }

#if ENABLED(EXTENSIBLE_UI)
    ui.reset_status();
#endif
}
