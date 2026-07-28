#include "power_panic.hpp"
#include "power_panic_storage.hpp"

#include "M73_PE.h"
#include "bsod.h"
#include "marlin_server.hpp"
#include "odometer.hpp"

#include "../lib/Marlin/Marlin/src/feature/input_shaper/input_shaper_config.hpp"
#include "../lib/Marlin/Marlin/src/feature/pressure_advance/pressure_advance_config.hpp"
#include "../lib/Marlin/Marlin/src/feature/prusa/crash_recovery.hpp"
#include "../lib/Marlin/Marlin/src/gcode/gcode.h"
#include "../lib/Marlin/Marlin/src/module/endstops.h"
#include "../lib/Marlin/Marlin/src/module/printcounter.h"
#include "../lib/Marlin/Marlin/src/module/temperature.h"

#include <assert.h>
#include <logging/log.hpp>
#include <option/has_cancel_object.h>
#include <option/has_chamber_api.h>
#include <option/has_modular_bed.h>
#include <option/has_nozzle_cleaner.h>
#include <option/has_puppies.h>
#include <option/has_toolchanger.h>
#include <usb_host/usbh_async_diskio.hpp>

#include <feature/safety_timer/safety_timer.hpp>

#if HAS_CANCEL_OBJECT()
    #include <feature/cancel_object/cancel_object.hpp>
#endif
#if HAS_CHAMBER_API()
    #include <feature/chamber/chamber.hpp>
#endif
#if ENABLED(PRUSA_SPOOL_JOIN)
    #include <module/prusa/spool_join.hpp>
#endif
#if ENABLED(PRUSA_TOOL_MAPPING)
    #include <module/prusa/tool_mapper.hpp>
#endif
#if HAS_TOOLCHANGER()
    #include <module/prusa/toolchanger.h>
#endif
#if HAS_PUPPIES()
    #include "puppies/puppy_task.hpp"
#endif

namespace {

constexpr uint16_t chamber_temp_off = 0xffff;

}

extern osThreadId defaultTaskHandle;
extern osThreadId displayTaskHandle;

namespace power_panic {

LOG_COMPONENT_REF(PowerPanic);

runtime_state_t runtime_state;
osThreadId ac_fault_task;
std::atomic<PPState> power_panic_state = PPState::Inactive;

enum class ResumeState : uint8_t {
    Setup,
    Resume,
    WaitForHeaters,
    Unpark,
    ParkForPause,
    Finish,
    Error,
};

std::atomic<ResumeState> resume_state = ResumeState::Setup;

void ac_fault_task_main([[maybe_unused]] void const *argument) {
    vTaskSuspend(NULL);

    marlin_server::print_quick_stop_powerpanic();
    endstops.enable_globally(false);
    vTaskSuspend(USBH_MSC_WorkerTaskHandle);

    // The display task may hold the CRC32 device during a fault.
    osThreadSetPriority(displayTaskHandle, osPriorityIdle);
#if HAS_PUPPIES()
    buddy::puppies::suspend_puppy_task();
#endif

    osThreadSetPriority(NULL, osPriorityIdle);

    // BFW-6419: xTaskAbortDelay can interrupt a mutex wait.
    freertos::Mutex::power_panic_mode_removeme = true;

    for (;;) {
        osSignalSet(defaultTaskHandle, ~0UL);
        xTaskAbortDelay(defaultTaskHandle);
    }
}

void prepare() {
    if (!runtime_state.nested_fault) {
        marlin_vars().media_SFN_path.copy_to(runtime_state.media_SFN_path, sizeof(runtime_state.media_SFN_path));
    }

    erase();
    fixed_t::save();

    log_info(PowerPanic, "powerpanic prepared");
    power_panic_state = PPState::Prepared;
}

static void atomic_reset() {
    if (state_stored()) {
        erase();
    }

    power_panic_state = PPState::Inactive;
    resume_state = ResumeState::Setup;
    runtime_state.nested_fault = false;
}

static void atomic_finish() {
    HAL_NVIC_DisableIRQ(buddy::hw::acFault.getIRQn());

#if HAS_TOOLCHANGER()
    if (state_buf.crash.crash_position.y > PrusaToolChanger::SAFE_Y_WITH_TOOL
        && prusa_toolchanger.is_toolchanger_enabled()) {
        marlin_server::powerpanic_finish_toolcrash();
    } else
#endif
    {
        if (state_buf.planner.was_paused) {
            marlin_server::powerpanic_finish_pause();
        } else {
            marlin_server::powerpanic_finish_recovery();
        }
    }
    atomic_reset();

    HAL_NVIC_EnableIRQ(buddy::hw::acFault.getIRQn());
}

void resume_print() {
    assert(state_stored());
    assert(marlin_server::printer_idle());

    fixed_t::load();
    state_t::load();

    log_info(PowerPanic, "resuming print");
    runtime_state.nested_fault = true;

    {
        print_job_timer.resume(state_buf.progress.print_duration);
        print_job_timer.pause();

        const auto mode_specific = [](const state_progress_t::ModeSpecificData &stored, ClProgressData::ModeSpecificData &progress) {
            progress.percent_done.mSetValue(stored.percent_done, state_buf.progress.print_duration);
            progress.percent_done.mSetValue(stored.time_to_end, state_buf.progress.print_duration);
            progress.percent_done.mSetValue(stored.time_to_pause, state_buf.progress.print_duration);
        };
        mode_specific(state_buf.progress.standard_mode, oProgressData.standard_mode);
        mode_specific(state_buf.progress.stealth_mode, oProgressData.stealth_mode);
    }

    const bool auto_recover = [] {
        if (state_buf.print.odometer_e_start >= Odometer_s::instance().get_extruded_all()) {
            return true;
        }

#if HAS_MODULAR_BED()
        thermalManager.setEnabledBedletMask(state_buf.planner.enabled_bedlets_mask);
#endif
        const float current_bed_temp = thermalManager.degBed();
        if (!state_buf.planner.target_bed || current_bed_temp >= state_buf.planner.target_bed) {
            return true;
        }
        return (state_buf.planner.target_bed - current_bed_temp) < POWER_PANIC_MAX_BED_DIFF;
    }();

    if (resume_state == ResumeState::Setup && auto_recover) {
        resume_state = ResumeState::Resume;
    }

    const GCodeReaderPosition gcode_pos {
        .restore_info = state_buf.gcode_stream_restore_info,
        .offset = state_buf.crash.sdpos,
    };
    marlin_server::powerpanic_resume(runtime_state.media_SFN_path, gcode_pos, auto_recover);
}

void resume_continue() {
    if (resume_state == ResumeState::Setup) {
        resume_state = ResumeState::Resume;
    }
}

void resume_loop() {
    switch (resume_state) {
    case ResumeState::Setup:
        thermalManager.setTargetBed(state_buf.planner.target_bed);
        break;

    case ResumeState::Resume: {
        marlin_server::resume_state_t resume;
        resume.pos = state_buf.crash.crash_current_position;
        resume.fan_speed = state_buf.planner.fan_speed;
        resume.print_speed = state_buf.planner.print_speed;
        resume.nozzle_temp = state_buf.planner.target_nozzle;
        marlin_server::set_resume_data(&resume);

        crash_s.sdpos = state_buf.crash.sdpos;
        thermalManager.setTargetBed(state_buf.planner.target_bed);
#if ENABLED(PREVENT_COLD_EXTRUSION)
        thermalManager.extrude_min_temp = state_buf.planner.extrude_min_temp;
        thermalManager.allow_cold_extrude = state_buf.planner.allow_cold_extrude;
#endif

        gcode.compatibility = state_buf.planner.compatibility;
        marlin_debug_flags = state_buf.planner.marlin_debug_flags;

        planner.apply_settings(state_buf.planner.settings);
        planner.refresh_acceleration_rates();
#if !HAS_CLASSIC_JERK
        planner.max_e_jerk = state_buf.planner.max_jerk.e;
        planner.junction_deviation_mm = state_buf.planner.junction_deviation_mm;
#endif

        assert(!planner.leveling_active);
        current_position[Z_AXIS] = state_buf.planner.z_position;
        planner.set_position_mm(current_position);
        axes_home_level[Z_AXIS] = state_buf.crash.axes_home_level[Z_AXIS];
        planner.max_printed_z = state_buf.planner.max_printed_z;

#if HAS_CANCEL_OBJECT()
        buddy::cancel_object().set_state(state_buf.cancel_object);
#endif
#if ENABLED(PRUSA_TOOL_MAPPING)
        tool_mapper.deserialize(state_buf.tool_mapping);
#endif
#if ENABLED(PRUSA_SPOOL_JOIN)
        spool_join.deserialize(state_buf.spool_join);
#endif
#if HAS_CHAMBER_API()
        if (state_buf.chamber_target_temp == chamber_temp_off) {
            buddy::chamber().set_target_temperature(std::nullopt);
        } else {
            buddy::chamber().set_target_temperature(state_buf.chamber_target_temp);
        }
#endif
#if HAS_TEMP_HEATBREAK_CONTROL
        for (uint8_t e = 0; e < HOTENDS; e++) {
            thermalManager.setTargetHeatbreak(state_buf.heatbreak_temperatures[e], e);
        }
#endif

#if HAS_TOOLCHANGER()
        if (state_buf.crash.crash_position.y > PrusaToolChanger::SAFE_Y_WITH_TOOL) {
            prusa_toolchanger.set_precrash_state({ state_buf.toolchanger.precrash_tool,
                state_buf.toolchanger.return_type,
                state_buf.toolchanger.return_pos });
            resume_state = ResumeState::Finish;
            break;
        }
#endif

        if (state_buf.crash.recover_flags & Crash_s::RECOVER_AXIS_STATE) {
            if (state_buf.crash.axes_home_level.is_homed(X_AXIS, AxisHomeLevel::imprecise)
                || state_buf.crash.axes_home_level.is_homed(Y_AXIS, AxisHomeLevel::imprecise)) {
                const float z_dist = current_position[Z_AXIS] - state_buf.crash.crash_current_position[Z_AXIS];
                const float z_lift = z_dist < Z_HOMING_HEIGHT ? Z_HOMING_HEIGHT - z_dist : 0;
                char cmd_buf[24];
                snprintf(cmd_buf, sizeof(cmd_buf), "G28 X Y D R%f", static_cast<double>(z_lift));
                marlin_server::enqueue_gcode(cmd_buf);
            }
        }

        if (state_buf.planner.was_paused) {
            resume_state = ResumeState::ParkForPause;
        } else {
            HOTEND_LOOP() {
                marlin_server::set_temp_to_display(state_buf.planner.target_nozzle[e], e);
                thermalManager.setTargetHotend(state_buf.planner.target_nozzle[e], e);
            }
            resume_state = ResumeState::WaitForHeaters;
        }
        break;
    }

    case ResumeState::WaitForHeaters:
        buddy::safety_timer().reset_restore_nonblocking();
        if (!Temperature::are_all_temperatures_reached()) {
            break;
        }
#if HAS_NOZZLE_CLEANER()
        marlin_server::enqueue_gcode("G12");
#endif
        resume_state = ResumeState::Unpark;
        break;

    case ResumeState::Unpark:
        if (marlin_server::is_processing()) {
            break;
        }
        if (!(state_buf.crash.recover_flags & Crash_s::RECOVER_XY_POSITION)) {
            LOOP_XY(i) {
                state_buf.crash.crash_current_position[i] = current_position[i];
            }
        }
        if (!(state_buf.crash.recover_flags & Crash_s::RECOVER_Z_POSITION)) {
            state_buf.crash.crash_current_position[Z_AXIS] = current_position[Z_AXIS];
        }
        if (state_buf.crash.axes_home_level.is_homed({ X_AXIS, Y_AXIS }, AxisHomeLevel::imprecise)) {
            plan_park_move_to_xyz(state_buf.crash.crash_current_position, NOZZLE_PARK_XY_FEEDRATE, NOZZLE_PARK_Z_FEEDRATE, Segmented::yes);
        }
        plan_move_by(PAUSE_PARK_RETRACT_FEEDRATE, 0, 0, 0, PAUSE_PARK_RETRACT_LENGTH / planner.e_factor[active_extruder]);
        resume_state = ResumeState::Finish;
        break;

    case ResumeState::ParkForPause:
        if (marlin_server::is_processing()) {
            break;
        }
        plan_park_move_to_xyz(state_buf.crash.start_current_position, NOZZLE_PARK_XY_FEEDRATE, NOZZLE_PARK_Z_FEEDRATE, Segmented::yes);
        resume_state = ResumeState::Finish;
        break;

    case ResumeState::Finish:
        if (marlin_server::is_processing()) {
            break;
        }

        HOTEND_LOOP() {
            planner.flow_percentage[e] = state_buf.planner.flow_percentage[e];
        }
        gcode.axis_relative = state_buf.planner.axis_relative;

        LOOP_XYZ(i) {
            if (state_buf.planner.axis_config[i].frequency == 0.f) {
                input_shaper::set_axis_config(static_cast<AxisEnum>(i), std::nullopt);
            } else {
                input_shaper::set_axis_config(static_cast<AxisEnum>(i), state_buf.planner.axis_config[i]);
            }
        }

        if (state_buf.planner.original_y.frequency == 0.f) {
            input_shaper::set_config_for_m74(Y_AXIS, std::nullopt);
        } else {
            input_shaper::set_config_for_m74(Y_AXIS, state_buf.planner.original_y);
        }

        if (state_buf.planner.axis_y_weight_adjust.frequency_delta != 0.f) {
            input_shaper::set_axis_y_weight_adjust(std::nullopt);
        } else {
            input_shaper::set_axis_y_weight_adjust(state_buf.planner.axis_y_weight_adjust);
        }
        pressure_advance::set_axis_e_config(state_buf.planner.axis_e_config);

        {
            const auto &stored = state_buf.crash;
            crash_s.start_current_position = stored.start_current_position;
            crash_s.crash_current_position = stored.crash_current_position;
            crash_s.crash_position = stored.crash_position;
            crash_s.segments_finished = stored.segments_finished;
            crash_s.leveling_active = stored.leveling_active;
            crash_s.recover_flags = stored.recover_flags;
            crash_s.fr_mm_s = stored.fr_mm_s;
            crash_s.counters.restore_data(stored.counters);
        }

        atomic_finish();
        log_info(PowerPanic, "resuming complete");
        resume_state = ResumeState::Error;
        break;

    case ResumeState::Error:
        bsod("resume loop not reset");
    }
}

bool is_power_panic_resuming() {
    return resume_state > ResumeState::Setup;
}

void reset() {
    atomic_reset();
    state_buf.print.odometer_e_start = Odometer_s::instance().get_extruded_all();
    log_info(PowerPanic, "powerpanic reset");
}

} // namespace power_panic
