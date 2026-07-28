/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2019 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * @file
 */

#include "G425.hpp"
#include "g425_policy.hpp"

#include <algorithm>
#include <array>
#include <span>
#include <stdint.h>
#include <sys/types.h>
#include <limits>

#include "core/types.h"
#include "metric.h"

#include "../../Marlin.h"

#include "../gcode.h"
#include "inc/Conditionals_LCD.h"

#if ENABLED(BACKLASH_GCODE)
    #include "../../feature/backlash.h"
#endif

#include "../../module/motion.h"
#include "../../module/planner.h"
#include "../../module/tool_change.h"
#include "../../module/endstops.h"
#include "../../module/prusa/homing_corexy.hpp"
#include "../../feature/bedlevel/bedlevel.h"
#include "../../feature/pressure_advance/pressure_advance_config.hpp"
#include "Marlin/src/gcode/gcode.h"
#include "../../module/stepper.h"

#if ENABLED(PRUSA_TOOLCHANGER)
    #include "loadcell.hpp"
    #include "../../module/prusa/toolchanger.h"
    #include "../../module/probe.h"
#endif

#if ENABLED(CRASH_RECOVERY)
    #include "src/feature/prusa/crash_recovery.hpp"
#endif

#include <common/mapi/parking.hpp>
#include <bsod_gui.hpp>
#include <marlin_server.hpp>
#include <center_approx.hpp>

/**
 * G425 backs away from the calibration object by various distances
 * depending on the confidence level:
 *
 *   UNKNOWN   - No real notion on where the calibration object is on the bed
 *   UNCERTAIN - Measurement may be uncertain due to backlash
 *   CERTAIN   - Measurement obtained with backlash compensation
 */

#ifndef CALIBRATION_MEASUREMENT_UNKNOWN
    #define CALIBRATION_MEASUREMENT_UNKNOWN 5.0f // mm
#endif
#ifndef CALIBRATION_MEASUREMENT_UNCERTAIN
    #define CALIBRATION_MEASUREMENT_UNCERTAIN 1.0f // mm
#endif
#ifndef CALIBRATION_MEASUREMENT_CERTAIN
    #define CALIBRATION_MEASUREMENT_CERTAIN 0.5f // mm
#endif

#define NUM_Z_MEASUREMENTS 20

#define HAS_X_CENTER BOTH(CALIBRATION_MEASURE_LEFT, CALIBRATION_MEASURE_RIGHT)
#define HAS_Y_CENTER BOTH(CALIBRATION_MEASURE_FRONT, CALIBRATION_MEASURE_BACK)

#if ENABLED(ARC_SUPPORT)
void plan_arc(const xyze_pos_t &, const ab_float_t &, const bool, const uint8_t);
#else
    #error "G425 requires ARC_SUPPORT"
#endif

namespace g425_policy {

// Raw XY probe [mm]
METRIC_DEF(metric_xy_raw_hit, "g425_rxy", METRIC_VALUE_CUSTOM, 100, METRIC_ENABLED);
// Verified XY probe - two raw probes agree on position [mm]
METRIC_DEF(metric_xy_hit, "g425_xy", METRIC_VALUE_CUSTOM, 100, METRIC_ENABLED);
// Raw Z probe [mm]
METRIC_DEF(metric_z_raw_hit, "g425_rz", METRIC_VALUE_CUSTOM, 100, METRIC_ENABLED);
// Averaged Z probe - N raw probes averaged [mm]
METRIC_DEF(metric_z_hit, "g425_z", METRIC_VALUE_CUSTOM, 100, METRIC_ENABLED);
constexpr xyz_float_t dimensions { { CALIBRATION_OBJECT_DIMENSIONS } };
constexpr xyz_pos_t true_center { { CALIBRATION_OBJECT_CENTER } };
constexpr xyz_pos_t true_top_center = { { { .x = true_center.x,
    .y = true_center.y,
    .z = dimensions.z } } };

constexpr float PROBE_Z_BORE_MM { 1 };
constexpr auto PROBE_Z_UNCERTAIN_DIST_MM { 5 };
constexpr auto PROBE_Z_CERTAIN_DIST_MM { 1 };
constexpr float PIN_DIAMETER_MM { 6 };
constexpr float PROBE_XY_TIGHT_DIST_MM { PIN_DIAMETER_MM / 2 + 3 };
constexpr float PROBE_XY_CERTAIN_DIST_MM { PROBE_XY_TIGHT_DIST_MM + 1 };
constexpr float PROBE_XY_UNCERTAIN_DIST_MM { PROBE_XY_CERTAIN_DIST_MM + 1 };
constexpr feedRate_t PROBE_FEEDRATE_MMS { 3 };
constexpr feedRate_t INTERPROBE_FEEDRATE_MMS { 25 };
constexpr auto NUM_PROBE_TRIES { 5 }; // Keep low, the noise is not random, but rather the measurement jumps a few values
constexpr auto PROBE_ALLOWED_ERROR { 0.03f };
constexpr auto NUM_PROBE_SAMPLES { 2 };
constexpr auto PROBE_FAIL_THRESHOLD_MM { 3 };
constexpr auto XY_ACCELERATION_MMSS { 500 };
constexpr auto RESONANCE_DAMPER_WAIT_MS { 500 };
constexpr auto MIN_TRAVELED_DISTANCE_MM { 0.1f };
inline void calibration_move() {
    do_blocking_move_to(current_position, MMM_TO_MMS(CALIBRATION_FEEDRATE_TRAVEL));
}

inline void wait_ms(const uint32_t duration_ms) {
    const uint32_t point = ticks_ms();
    while (ticks_ms() - point < duration_ms) {
        idle(true);
    }
}

#if HOTENDS > 1
void set_nozzle(const uint8_t extruder) {
    if (extruder != active_extruder) {
        tool_change(extruder);
    }
}
#endif

#if HAS_HOTEND_OFFSET
void normalize_hotend_offsets() {
    for (uint8_t e = 1; e < HOTENDS; e++) {
        hotend_offset[e] -= hotend_offset[0];
    }
    hotend_offset[0].reset();
    hotend_offset[PrusaToolChanger::MARLIN_NO_TOOL_PICKED].reset(); // Avoid offset on no tool
}
#endif

/// Return one of evenly distributed position on circle
xy_pos_t pos_on_circle(float radius, int idx, int total_points) {
    float goniom_dist = (static_cast<float>(idx) / static_cast<float>(total_points)) * 2 * static_cast<float>(M_PI);
    return { { { std::cos(goniom_dist) * radius, std::sin(goniom_dist) * radius } } };
}

// This function requires normalize_hotend_offsets() to be called
inline void report_hotend_offsets() {
    for (uint8_t e = 1; e < HOTENDS; e++) {
        SERIAL_ECHOLNPAIR("T", int(e), " Hotend Offset X", hotend_offset[e].x, " Y", hotend_offset[e].y, " Z", hotend_offset[e].z);
    }
}

xy_pos_t closest_point_on_circle(const xy_pos_t point, const xy_pos_t center, const float radius) {
    const float distance_factor = sqrt(pow(point.x - center.x, 2) + pow(point.y - center.y, 2));

    if (distance_factor == 0) {
        return { { { .x = center.x + radius,
            .y = center.y } } };
    }

    return { { { .x = center.x + radius * (point.x - center.x) / distance_factor,
        .y = center.y + radius * (point.y - center.y) / distance_factor } } };
}

void go_to_safe_height() {
    current_position.z = true_top_center.z + PROBE_Z_UNCERTAIN_DIST_MM;
    line_to_current_position(INTERPROBE_FEEDRATE_MMS);
    planner.synchronize();
}

void go_to_safety_circle(const xyz_pos_t center, const float radius) {
    current_position.set(closest_point_on_circle(current_position, center, radius));
    line_to_current_position(INTERPROBE_FEEDRATE_MMS);
    planner.synchronize();
}

xyz_pos_t initial_position(const xyz_pos_t center, const float angle, const float radius) {
    return { { { .x = center.x + cos(angle) * radius,
        .y = center.y + sin(angle) * radius,
        .z = center.z - PROBE_Z_BORE_MM } } };
}

void go_to_initial(const xyz_pos_t center, const float angle, const float radius) {
    const xyz_pos_t initial = initial_position(center, angle, radius);
    const xy_pos_t current = current_position;

    if (current != initial) {
        feedrate_mm_s = INTERPROBE_FEEDRATE_MMS;
        plan_arc(initial, { { { .x = center.x - current.x, .y = center.y - current.y } } }, false, 0);
    }
    planner.synchronize();

    current_position.z = initial.z;
    line_to_current_position(INTERPROBE_FEEDRATE_MMS);
    planner.synchronize();
}

xy_pos_t probe_xy(const xyz_pos_t center, const float angle, const uint8_t tool, const Phase phase) {
    // As we perform measurements, we need to ensure the current position has been reached first
    planner.buffer_line(current_position, PROBE_FEEDRATE_MMS, active_extruder, { .raw_block = true });
    planner.synchronize();

    // Mark initial position
    xyze_long_t initial_pos_msteps = planner.get_position_msteps();
    xyze_pos_t initial_mm = current_position;

    // Setup probe for XY endstop
    loadcell.set_xy_endstop(true);

    // Wait for resonance to damper and tare
    wait_ms(RESONANCE_DAMPER_WAIT_MS);
    loadcell.WaitBarrier(); // Sync samples before tare
    loadcell.Tare(Loadcell::TareMode::Continuous);

    if (loadcell.GetXYEndstop()) {
        // This is hopefully rare situation when the loadcell data are totally wrong. If we know this happens
        // and why it happens we should add a red screen with appropriate text.
        bsod("XY probe triggered");
    }

    // Expect pin hit
    endstops.enable_xy_probe(true);
#if ENABLED(CRASH_RECOVERY)
    crash_s.deactivate();
#endif

    // Go to center
    do_blocking_move_to_xy(center.x, center.y, PROBE_FEEDRATE_MMS);

    // No longer expecting pin hit
    const bool reached = endstops.trigger_state();
#if ENABLED(CRASH_RECOVERY)
    crash_s.activate();
#endif
    loadcell.set_xy_endstop(false);
    endstops.enable_xy_probe(false);

    // Something is terribly wrong, maybe the nozzle is already being bend, bail out.
    if (!reached) {
        fatal_error(ErrCode::ERR_MECHANICAL_PIN_NOT_REACHED);
    }

    // Get hit position
    endstops.hit_on_purpose();
    planner.reset_position();
    xyze_long_t hit_steps = { { { stepper.position(A_AXIS), stepper.position(B_AXIS),
        stepper.position(C_AXIS), stepper.position(E_AXIS) } } };
    xyze_pos_t hit_mm;
    corexy_ab_to_xyze(hit_steps, hit_mm);

    // Discard result if not moved enough to reach the pin (probe triggered too early?)
    if ((hit_mm - initial_mm).magnitude() < MIN_TRAVELED_DISTANCE_MM) {
        hit_mm.reset();
    }

    // Return to initial
    planner._buffer_msteps(initial_pos_msteps, initial_mm, INTERPROBE_FEEDRATE_MMS, active_extruder, { .raw_block = true });
    planner.synchronize();
    current_position = initial_mm;

    metric_record_custom(
        &metric_xy_raw_hit,
        ",t=%u,p=%u,a=%.3f x=%.3f,y=%.3f",
        tool,
        std::to_underlying(phase),
        static_cast<double>(angle),
        static_cast<double>(hit_mm.x),
        static_cast<double>(hit_mm.y));

    return hit_mm;
}

xy_pos_t synthetic_probe(const xyz_pos_t center, const float angle) {
    return { { { .x = center.x + (PIN_DIAMETER_MM / 2 + PROBE_Z_BORE_MM) * cos(angle),
        .y = center.y + (PIN_DIAMETER_MM / 2 + PROBE_Z_BORE_MM) * sin(angle) } } };
}

xy_pos_t probe_xy_verify(const xyz_pos_t center, const float angle, const float probe_distance, const uint8_t tool, const Phase phase) {
    go_to_safety_circle(center, probe_distance);
    go_to_initial(center, angle, probe_distance);

    // Take all samples
    std::array<xy_pos_t, NUM_PROBE_SAMPLES> hits;
    for (auto &hit : hits) {
        hit = probe_xy(center, angle, tool, phase);
    }

    for (uint i = 0; i < NUM_PROBE_TRIES; ++i) {
        // Compute position from hits
        xy_pos_t pos {};
        for (auto &hit : hits) {
            pos += hit;
        }
        pos = pos / static_cast<int>(hits.size());

        // Compute sum of hit distances from position
        float distance = 0;
        for (auto &hit : hits) {
            auto dist = (pos - hit).magnitude();
            if (dist > distance) {
                distance = dist;
            }
            if (!hit.magnitude()) {
                distance = std::numeric_limits<float>::infinity();
            }
        }

        // Check samples consistency
        if (distance > PROBE_ALLOWED_ERROR) {
            // Redo one of the samples and try again
            hits[i % hits.size()] = probe_xy(center, angle, tool, phase);
            continue;
        }

        // Samples are consistent
        metric_record_custom(
            &metric_xy_hit,
            ",t=%u,p=%u,a=%.3f x=%.3f,y=%.3f",
            tool,
            std::to_underlying(phase),
            static_cast<double>(angle),
            static_cast<double>(pos.x),
            static_cast<double>(pos.y));

        const float exp_dist = (pos - synthetic_probe(center, angle)).magnitude();
        if (exp_dist > PROBE_FAIL_THRESHOLD_MM) {
            fatal_error(ErrCode::ERR_MECHANICAL_XY_POSITION_INVALID, static_cast<double>(exp_dist), static_cast<double>(PROBE_FAIL_THRESHOLD_MM));
        }

        return pos;
    }

    fatal_error(ErrCode::ERR_MECHANICAL_XY_PROBE_UNSTABLE);

    return hits[0];
}

/// Probe in Z, first in the middle then it does circle around center of the pin, just to distribute the probes over larger area to minimize errors
float probe_z(const xyz_pos_t position, float uncertainty, const int num_measurements, const uint8_t tool, const Phase phase) {
    constexpr xyz_float_t dimensions = { { CALIBRATION_OBJECT_DIMENSIONS } };

    // radius of circle that we are probing around for more variety
    constexpr float circle_radius = std::min(dimensions.x, dimensions.y) / 4;

    // Move to safe clearance above calibration object first
    float top_expected_position = position.z;
    current_position.z = top_expected_position + uncertainty;
    calibration_move();

    float sum = 0;
    for (int i = 0; i < num_measurements; i++) {
        xy_pos_t offset = { { { 0, 0 } } };
        if (i > 0) {
            offset = pos_on_circle(circle_radius, i - 1, num_measurements - 1);
        }

        // Move to the position where we probe
        current_position = xy_pos_t(position) + offset;
        current_position.z = top_expected_position + uncertainty;
        calibration_move();

        float measurement = probe_here(top_expected_position);
        if (std::isnan(measurement)) {
            fatal_error(ErrCode::ERR_MECHANICAL_PIN_NOT_REACHED);
        }
        SERIAL_ECHOPAIR_F("Probe: ", static_cast<double>(measurement));
        SERIAL_EOL();
        metric_record_custom(
            &metric_z_raw_hit,
            ",t=%u,p=%u x=%.3f,y=%.3f,z=%.3f",
            tool,
            std::to_underlying(phase),
            static_cast<double>(current_position.x),
            static_cast<double>(current_position.y),
            static_cast<double>(measurement));

        // now that we have first probe, update top position and uncertainty to speed-up further probes
        top_expected_position = measurement;
        uncertainty = 1;

        sum += measurement;
    }

    float measurement_avg = sum / num_measurements;
    SERIAL_ECHOPAIR_F("Average: ", static_cast<double>(measurement_avg));
    SERIAL_EOL();

    metric_record_custom(
        &metric_z_hit,
        ",t=%u,p=%u,x=%.3f,y=%.3f z=%.3f",
        tool,
        static_cast<unsigned>(phase),
        static_cast<double>(current_position.x),
        static_cast<double>(current_position.y),
        static_cast<double>(measurement_avg));

    return measurement_avg;
}

} // namespace g425_policy

/**
 * \addtogroup G-Codes
 */

/**
 *### G425: Perform calibration with calibration object <a href="https://reprap.org/wiki/G-code#G425:_Perform_auto-calibration_with_calibration_cube">G425: Perform auto-calibration with calibration cube</a>
 *
 * Only XL
 *
 *#### Usage
 *
 *    G425
 *
 */
void GcodeSuite::G425() {
    full_calibration();
}
/** @}*/
