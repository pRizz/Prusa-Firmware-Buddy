#include "gcode_info.hpp"

#include <cctype>
#include <cstdio>
#include <cstring>

void GCodeInfo::parse_comment(GcodeBuffer::String comment) {
    auto [name, val] = comment.parse_metadata();
    if (name.begin == nullptr || val.begin == nullptr) {
        return;
    }

    if (name == gcode_info::time) {
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wformat-truncation"
        snprintf(printing_time.begin(), printing_time.size(), "%s", val.c_str());
#pragma GCC diagnostic pop
        return;
    }

    const bool is_filament_type = (name == gcode_info::filament_type);
    const bool is_filament_used_mm = (name == gcode_info::filament_mm);
    const bool is_filament_used_g = (name == gcode_info::filament_g);
    const bool is_extruder_colour = (name == gcode_info::extruder_colour);

    if (is_filament_type || is_filament_used_g || is_filament_used_mm || is_extruder_colour) {
        std::span<char> value(val.c_str(), val.len());
        size_t extruder = 0;
        while (const auto item = iterate_items(value, is_filament_type || is_extruder_colour ? ';' : ',')) {
            if (extruder >= per_extruder_info.size()) {
                continue;
            }

            if (is_filament_type) {
                filament_buff filament_name;
                snprintf(filament_name.begin(), filament_name.size(), "%.*s", item->size(), item->data());
                per_extruder_info[extruder].filament_name = filament_name;
                filament_described = true;
            } else if (is_filament_used_mm) {
                float filament_used_mm;
                sscanf(item->data(), "%f", &filament_used_mm);
                per_extruder_info[extruder].filament_used_mm = filament_used_mm;
            } else if (is_filament_used_g) {
                float filament_used_g;
                sscanf(item->data(), "%f", &filament_used_g);
                per_extruder_info[extruder].filament_used_g = filament_used_g;
            } else {
                per_extruder_info[extruder].extruder_colour = Color::from_string(*item);
            }
            extruder++;
        }
    }
#if EXTRUDERS > 1
    else if (name == gcode_info::filament_wipe_tower_g) {
        float temp;
        sscanf(val.c_str(), "%f", &temp);
        filament_wipe_tower_g = temp;
    }
#endif
}

std::optional<std::string_view> GCodeInfo::iterate_items(std::span<char> &buffer, char separator) {
    while (buffer[0] && isspace(*buffer.data())) {
        buffer = buffer.subspan(1);
    }

    size_t item_length = 0;
    for (; item_length < buffer.size(); item_length++) {
        if (buffer[item_length] == 0 || buffer[item_length] == separator) {
            break;
        }
    }
    std::span<char> next_buffer = buffer.subspan(buffer[item_length] == separator ? item_length + 1 : item_length);

    while (item_length && isspace(buffer[item_length - 1])) {
        item_length--;
    }

    const auto result = item_length ? std::make_optional(std::string_view(buffer.begin(), buffer.begin() + item_length)) : std::nullopt;
    buffer = next_buffer;
    return result;
}
