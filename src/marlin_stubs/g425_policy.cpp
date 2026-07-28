#include "G425.hpp"
#include "g425_policy.hpp"

#include <algorithm>
#include <array>
#include <span>

#include "metric.h"

#include "../../Marlin.h"

#include "../../feature/bedlevel/bedlevel.h"
#include "../../feature/pressure_advance/pressure_advance_config.hpp"
#include "../../module/motion.h"
#include "../../module/planner.h"
#include "../../module/stepper.h"
#include "../../module/tool_change.h"

#if ENABLED(BACKLASH_GCODE)
    #include "../../feature/backlash.h"
#endif

#if ENABLED(PRUSA_TOOLCHANGER)
    #include "../../module/prusa/toolchanger.h"
    #include "loadcell.hpp"
#endif

#if ENABLED(CRASH_RECOVERY)
    #include "src/feature/prusa/crash_recovery.hpp"
#endif

#include <bsod_gui.hpp>
#include <center_approx.hpp>
#include <common/mapi/parking.hpp>
#include <marlin_server.hpp>

#define TEMPORARY_SOFT_ENDSTOP_STATE(enable) REMEMBER(tes, soft_endstops_enabled, enable);

#if ENABLED(BACKLASH_GCODE)
    #define TEMPORARY_BACKLASH_CORRECTION(value) REMEMBER(tbst, backlash.correction, value)
#else
    #define TEMPORARY_BACKLASH_CORRECTION(value)
#endif

#if ENABLED(BACKLASH_GCODE) && defined(BACKLASH_SMOOTHING_MM)
    #define TEMPORARY_BACKLASH_SMOOTHING(value) REMEMBER(tbsm, backlash.smoothing_mm, value)
#else
    #define TEMPORARY_BACKLASH_SMOOTHING(value)
#endif

namespace {

METRIC_DEF(metric_center, "g425_cen", METRIC_VALUE_CUSTOM, 100, METRIC_ENABLED);
METRIC_DEF(metric_offset, "g425_off", METRIC_VALUE_CUSTOM, 100, METRIC_ENABLED);
METRIC_DEF(metric_xy_dev, "g425_xy_dev", METRIC_VALUE_FLOAT, 100, METRIC_ENABLED);

constexpr xyz_float_t dimensions { { CALIBRATION_OBJECT_DIMENSIONS } };
constexpr xy_float_t nod = { { { CALIBRATION_NOZZLE_OUTER_DIAMETER, CALIBRATION_NOZZLE_OUTER_DIAMETER } } };
constexpr xyz_pos_t true_center { { CALIBRATION_OBJECT_CENTER } };
constexpr xyz_pos_t true_top_center = { { { .x = true_center.x,
    .y = true_center.y,
    .z = dimensions.z } } };

constexpr auto PROBE_Z_UNCERTAIN_DIST_MM { 5 };
constexpr auto PROBE_Z_CERTAIN_DIST_MM { 1 };
constexpr float PIN_DIAMETER_MM { 6 };
constexpr float PROBE_XY_TIGHT_DIST_MM { PIN_DIAMETER_MM / 2 + 3 };
constexpr float PROBE_XY_CERTAIN_DIST_MM { PROBE_XY_TIGHT_DIST_MM + 1 };
constexpr float PROBE_XY_UNCERTAIN_DIST_MM { PROBE_XY_CERTAIN_DIST_MM + 1 };
constexpr auto XY_ACCELERATION_MMSS { 500 };
constexpr auto MAX_DEVIATION_MM { 0.2f };
constexpr auto NUM_Z_MEASUREMENTS { 20 };

struct Measurements {
    xyz_pos_t obj_center = true_top_center;
    xyz_float_t pos_error;
    xy_float_t nozzle_outer_dimension = nod;
};

class AccelerationLimiter {
public:
    AccelerationLimiter(const float max_acceleration_mmss)
        : previous_x(planner.settings.max_acceleration_mm_per_s2[X_AXIS])
        , previous_y(planner.settings.max_acceleration_mm_per_s2[Y_AXIS]) {
        planner.set_max_acceleration(X_AXIS | Y_AXIS, max_acceleration_mmss);
    }

    ~AccelerationLimiter() {
        planner.set_max_acceleration(X_AXIS, previous_x);
        planner.set_max_acceleration(Y_AXIS, previous_y);
    }

private:
    const float previous_x;
    const float previous_y;
};

bool check_deviation(const xy_pos_t &center, std::span<const xy_pos_t> points) {
    float radius = 0;
    for (const xy_pos_t &point : points) {
        radius += (center - point).magnitude();
    }
    radius /= points.size();

    float max_deviation = 0;
    for (const xy_pos_t &point : points) {
        max_deviation = max(max_deviation, (center - point).magnitude() - radius);
    }

    if (max_deviation > MAX_DEVIATION_MM) {
        return false;
    }
    metric_record_float(&metric_xy_dev, max_deviation);
    return true;
}

const std::optional<xyz_pos_t> get_single_xyz_center(const xyz_pos_t initial, const uint8_t tool, const g425_policy::Phase phase) {
    static constexpr uint8_t PHASE_XY_HITS[std::to_underlying(g425_policy::Phase::_count)] = { 3, 3, 12 };
    static constexpr uint8_t PHASE_Z_HITS[std::to_underlying(g425_policy::Phase::_count)] = { 1, 0, NUM_Z_MEASUREMENTS };
    static constexpr float PHASE_Z_UNCERTAINTY[std::to_underlying(g425_policy::Phase::_count)] = { PROBE_XY_UNCERTAIN_DIST_MM, PROBE_Z_UNCERTAIN_DIST_MM, PROBE_Z_CERTAIN_DIST_MM };
    xyz_pos_t start = initial;

    if (PHASE_Z_HITS[std::to_underlying(phase)]) {
        start.z = g425_policy::probe_z(initial, PHASE_Z_UNCERTAINTY[std::to_underlying(phase)], PHASE_Z_HITS[std::to_underlying(phase)], tool, phase);
    }

    AccelerationLimiter acceleration_limiter(XY_ACCELERATION_MMSS);
    static constexpr uint8_t MAX_HITS = *std::max_element(std::begin(PHASE_XY_HITS), std::end(PHASE_XY_HITS));
    std::array<xy_pos_t, MAX_HITS> max_hits;
    std::span<xy_pos_t> hits(max_hits.begin(), PHASE_XY_HITS[std::to_underlying(phase)]);
    for (uint hit_no = 0; xy_pos_t & hit : hits) {
        hit = g425_policy::probe_xy_verify(start, 2 * PI / hits.size() * hit_no++, PROBE_XY_UNCERTAIN_DIST_MM, tool, phase);
    }
    xyz_pos_t center = approximate_center(hits);
    center.z = start.z;

    if (phase == g425_policy::Phase::final && !check_deviation(center, hits)) {
        return std::nullopt;
    }

    return center;
}

const std::optional<xyz_pos_t> get_xyz_center(const uint8_t tool) {
    auto loadcell_precision_enabler = Loadcell::HighPrecisionEnabler(loadcell);

    std::optional<xyz_pos_t> maybe_center = true_top_center;
    for (g425_policy::Phase phase = g425_policy::Phase::first; phase != g425_policy::Phase::_count; phase = g425_policy::Phase(std::to_underlying(phase) + 1)) {
        if (!maybe_center.has_value()) {
            return std::nullopt;
        }
        maybe_center = get_single_xyz_center(maybe_center.value(), tool, phase);
    }

    g425_policy::go_to_safe_height();
    return maybe_center;
}

inline void update_measurements(Measurements &measurements, const AxisEnum axis) {
#if HAS_HOTEND_OFFSET
    hotend_currently_applied_offset[axis] += measurements.pos_error[axis];
#endif
    measurements.obj_center[axis] = true_top_center[axis];
    measurements.pos_error[axis] = 0;
}

bool calibrate_toolhead(Measurements &measurements, const uint8_t extruder) {
    TEMPORARY_BACKLASH_CORRECTION(all_on);
    TEMPORARY_BACKLASH_SMOOTHING(0.0f);

    pressure_advance::PressureAdvanceDisabler pressure_advance_disabler;

#if HOTENDS > 1
    g425_policy::set_nozzle(extruder);
#else
    UNUSED(extruder);
#endif

    const std::optional<xyz_pos_t> maybe_center = get_xyz_center(extruder);
    if (!maybe_center.has_value()) {
        SERIAL_ECHOLNPAIR("G425: Tool ", extruder, " center not found.");
        return false;
    }
    measurements.obj_center = maybe_center.value();
    measurements.pos_error = true_top_center - maybe_center.value();

#if HAS_HOTEND_OFFSET
    #if HAS_X_CENTER
    hotend_offset[extruder].x += measurements.pos_error.x;
    #endif
    #if HAS_Y_CENTER
    hotend_offset[extruder].y += measurements.pos_error.y;
    #endif
    hotend_offset[extruder].z += measurements.pos_error.z;
    g425_policy::normalize_hotend_offsets();
#endif

#if HAS_X_CENTER
    update_measurements(measurements, X_AXIS);
#endif
#if HAS_Y_CENTER
    update_measurements(measurements, Y_AXIS);
#endif
    update_measurements(measurements, Z_AXIS);
    return true;
}

void calibrate_all_toolheads(Measurements &measurements) {
    TEMPORARY_BACKLASH_CORRECTION(all_on);
    TEMPORARY_BACKLASH_SMOOTHING(0.0f);

    HOTEND_LOOP() {
#if ENABLED(PRUSA_TOOLCHANGER)
        if (!prusa_toolchanger.getTool(e).is_enabled()) {
            continue;
        }
#endif
        calibrate_toolhead(measurements, e);
    }

#if HAS_HOTEND_OFFSET
    g425_policy::normalize_hotend_offsets();
    #if ENABLED(PRUSA_TOOLCHANGER)
    prusa_toolchanger.save_tool_offsets();
    #endif
#endif
}

[[maybe_unused]] void calibrate_all() {
    Measurements measurements;

#if HAS_HOTEND_OFFSET
    reset_hotend_offsets();
#endif

    TEMPORARY_BACKLASH_CORRECTION(all_on);
    TEMPORARY_BACKLASH_SMOOTHING(0.0f);
    calibrate_all_toolheads(measurements);

#if ENABLED(BACKLASH_GCODE)
    calibrate_backlash(measurements);
#endif

    tool_change(prusa_toolchanger.MARLIN_NO_TOOL_PICKED, tool_return_t::no_return);
}

bool calibrate_all_simple() {
    disable_e_steppers();

#if ENABLED(CRASH_RECOVERY)
    Crash_Temporary_Deactivate crash_recovery_disabler;
#endif

    planner.synchronize();
    planner.reset_position();

    pressure_advance::PressureAdvanceDisabler pressure_advance_disabler;

    reset_hotend_offsets();
    hotend_currently_applied_offset = 0.f;

    bool failed = false;
    std::array<xyz_pos_t, HOTENDS> centers;
    HOTEND_LOOP() {
#if ENABLED(PRUSA_TOOLCHANGER)
        if (!prusa_toolchanger.getTool(e).is_enabled()) {
            continue;
        }
#endif
        tool_change(e, tool_return_t::no_return);
        std::optional<xyz_pos_t> maybe_center = get_xyz_center(e);
        if (!maybe_center.has_value()) {
            SERIAL_ECHOLNPAIR("G425: Tool ", e, " center not found.");
            failed = true;
            break;
        }
        centers[e] = maybe_center.value();
        metric_record_custom(
            &metric_center,
            ",t=%u x=%.3f,y=%.3f,z=%.3f",
            e,
            static_cast<double>(centers[e].x),
            static_cast<double>(centers[e].y),
            static_cast<double>(centers[e].z));
    }

    if (failed) {
        mapi::park(mapi::ZAction::absolute_move, mapi::ParkingPosition::from_xyz_pos({ { XYZ_NOZZLE_PARK_POINT_M600 } }));
        marlin_server::set_warning(WarningType::NozzleDoesNotHaveRoundSection);
        return false;
    }

    tool_change(prusa_toolchanger.MARLIN_NO_TOOL_PICKED, tool_return_t::no_return);

    HOTEND_LOOP() {
        if (!prusa_toolchanger.getTool(e).is_enabled()) {
            continue;
        }
        hotend_offset[e] = -centers[e];
    }
    g425_policy::normalize_hotend_offsets();

    HOTEND_LOOP() {
#if ENABLED(PRUSA_TOOLCHANGER)
        if (!prusa_toolchanger.getTool(e).is_enabled()) {
            hotend_offset[e].reset();
            continue;
        }
#endif

        if (hotend_offset[e].x < X_MIN_OFFSET || hotend_offset[e].x > X_MAX_OFFSET) {
            fatal_error(ErrCode::ERR_MECHANICAL_TOOL_OFFSET_OUT_OF_BOUNDS, e + 1, 'X', static_cast<double>(hotend_offset[e].x), static_cast<double>(X_MIN_OFFSET), static_cast<double>(X_MAX_OFFSET));
        }
        if (hotend_offset[e].y < Y_MIN_OFFSET || hotend_offset[e].y > Y_MAX_OFFSET) {
            fatal_error(ErrCode::ERR_MECHANICAL_TOOL_OFFSET_OUT_OF_BOUNDS, e + 1, 'Y', static_cast<double>(hotend_offset[e].y), static_cast<double>(Y_MIN_OFFSET), static_cast<double>(Y_MAX_OFFSET));
        }
        if (hotend_offset[e].z < Z_MIN_OFFSET || hotend_offset[e].z > Z_MAX_OFFSET) {
            fatal_error(ErrCode::ERR_MECHANICAL_TOOL_OFFSET_OUT_OF_BOUNDS, e + 1, 'Z', static_cast<double>(hotend_offset[e].z), static_cast<double>(Z_MIN_OFFSET), static_cast<double>(Z_MAX_OFFSET));
        }
    }
    prusa_toolchanger.save_tool_offsets();

    HOTEND_LOOP() {
        if (!prusa_toolchanger.getTool(e).is_enabled()) {
            continue;
        }
        osDelay(100);
        metric_record_custom(
            &metric_offset,
            ",t=%u x=%.3f,y=%.3f,z=%.3f",
            e,
            static_cast<double>(hotend_offset[e].x),
            static_cast<double>(hotend_offset[e].y),
            static_cast<double>(hotend_offset[e].z));
    }
    return true;
}

} // namespace

bool full_calibration() {
    TEMPORARY_SOFT_ENDSTOP_STATE(false);
    TEMPORARY_BED_LEVELING_STATE(false);

    phase_stepping::EnsureDisabled phase_stepping_disabler {};

    if (axis_unhomed_error()) {
        return false;
    }

    return calibrate_all_simple();
}
