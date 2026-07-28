#pragma once

#include "pause_stubbed.hpp"

#include "Marlin/src/Marlin.h"
#include "Marlin/src/core/language.h"
#include "Marlin/src/feature/pause.h"
#include "Marlin/src/gcode/gcode.h"
#include "Marlin/src/lcd/extensible_ui/ui_api.h"
#include "Marlin/src/lcd/ultralcd.h"
#include "Marlin/src/module/endstops.h"
#include "Marlin/src/module/motion.h"
#include "Marlin/src/module/planner.h"
#include "Marlin/src/module/printcounter.h"
#include "Marlin/src/module/stepper.h"
#include "Marlin/src/module/temperature.h"

#if ENABLED(PRUSA_MMU2)
    #include "Marlin/src/feature/prusa/MMU2/mmu2_mk4.h"
#endif

#if HAS_NOZZLE_CLEANER()
    #include <gcode_loader.hpp>
    #include <nozzle_cleaner.hpp>
#endif

#include "RAII.hpp"
#include "client_response.hpp"
#include "filament.hpp"
#include "filament_sensors_handler.hpp"
#include "filament_to_load.hpp"
#include "fs_event_autolock.hpp"
#include "fsm_loadunload_type.hpp"
#include "marlin_server.hpp"
#include "mapi/motion.hpp"

#include <buddy/unreachable.hpp>
#include <cmath>
#include <common/mapi/parking.hpp>
#include <common/marlin_client.hpp>
#include <config_store/store_instance.hpp>
#include <feature/ramming/ramming_sequence.hpp>
#include <feature/ramming/standard_ramming_sequence.hpp>
#include <feature/safety_timer/safety_timer.hpp>
#include <logging/log.hpp>
#include <scope_guard.hpp>
#include <utils/progress.hpp>

#include <option/has_auto_retract.h>
#include <option/has_human_interactions.h>
#include <option/has_mmu2.h>
#include <option/has_wastebin.h>

#if HAS_AUTO_RETRACT()
    #include <feature/auto_retract/auto_retract.hpp>
#endif

#ifndef NOZZLE_UNPARK_XY_FEEDRATE
    #define NOZZLE_UNPARK_XY_FEEDRATE NOZZLE_PARK_XY_FEEDRATE
#endif

#if (!ENABLED(EXTENSIBLE_UI)) || \
    (!ENABLED(ADVANCED_PAUSE_FEATURE)) || \
    HAS_FILAMENT_SENSOR || \
    HAS_BUZZER || \
    NUM_RUNOUT_SENSORS > 1 || \
    ENABLED(DUAL_X_CARRIAGE) || \
    ENABLED(ADVANCED_PAUSE_CONTINUOUS_PURGE)
    #error unsupported
#endif

using namespace buddy;

inline void report_progress(Pause &pause, ProgressPercent progress) {
    if (auto mode = pause.get_mode()) {
        const auto data = fsm::serialize_data(FSMLoadUnloadData { .mode = *mode, .progress = progress });
        marlin_server::fsm_change(pause.getPhase(), data);
    }
}

class PauseFsmNotifier : public CallbackHookGuard<> {
public:
    PauseFsmNotifier(Pause &pause, float min, float max, const MarlinVariable<float> &var)
        : CallbackHookGuard<>(marlin_server::idle_hook_point, [this, &var] {
            const auto progress = pause_.progress_mapper.update_progress(pause_.get_state(), to_normalized_progress(min_, max_, var.get()));
            report_progress(pause_, progress);
        })
        , pause_(pause)
        , min_(min)
        , max_(max) {}

private:
    Pause &pause_;
    float min_;
    float max_;
};

class PauseFsmDurationNotifier : public CallbackHookGuard<> {
public:
    PauseFsmDurationNotifier(Pause &pause, uint32_t duration_ms)
        : CallbackHookGuard<>(marlin_server::idle_hook_point, [this, duration_ms] {
            const auto progress = pause_.progress_mapper.update_progress(pause_.get_state(), to_normalized_progress(0, duration_ms, ticks_ms() - start_ms_));
            report_progress(pause_, progress);
        })
        , pause_(pause)
        , start_ms_(ticks_ms()) {}

private:
    Pause &pause_;
    uint32_t start_ms_;
};

class PauseFsmExplicitProgressNotifier : public CallbackHookGuard<> {
public:
    PauseFsmExplicitProgressNotifier(Pause &pause, float min, float max, ProgressPercent progress_min, ProgressPercent progress_max, const MarlinVariable<float> &var)
        : CallbackHookGuard<>(marlin_server::idle_hook_point, [this, &var] {
            const auto progress = progress_span_.map(to_normalized_progress(min_, max_, var.get()));
            report_progress(pause_, progress);
        })
        , pause_(pause)
        , min_(min)
        , max_(max)
        , progress_span_(progress_min, progress_max) {}

private:
    Pause &pause_;
    float min_;
    float max_;
    ProgressSpan progress_span_;
};

#if HAS_NOZZLE_CLEANER()
extern GCodeLoader nozzle_cleaner_gcode_loader;
#endif

#ifdef FILAMENT_RUNOUT_RAMMING_SEQUENCE
inline constexpr RammingSequenceArray runoutRammingSequence(FILAMENT_RUNOUT_RAMMING_SEQUENCE);
#else
inline constexpr RammingSequenceArray runoutRammingSequence(FILAMENT_UNLOAD_RAMMING_SEQUENCE);
#endif

inline constexpr RammingSequenceArray unloadRammingSequence(FILAMENT_UNLOAD_RAMMING_SEQUENCE);
