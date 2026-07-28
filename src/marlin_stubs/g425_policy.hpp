#pragma once

#include <stdint.h>

#include "core/types.h"

namespace g425_policy {

/// Center probing refines an approximate center over increasingly precise phases.
enum class Phase : uint8_t {
    first,
    second,
    final,
    _count
};

void go_to_safe_height();
xy_pos_t probe_xy_verify(const xyz_pos_t center, const float angle, const float probe_distance, const uint8_t tool, const Phase phase);
float probe_z(const xyz_pos_t position, float uncertainty, const int num_measurements, const uint8_t tool, const Phase phase);

#if HOTENDS > 1
void set_nozzle(const uint8_t extruder);
#endif

#if HAS_HOTEND_OFFSET
void normalize_hotend_offsets();
#endif

} // namespace g425_policy
