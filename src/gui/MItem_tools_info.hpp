/*****************************************************************************/
// menu items running tools
#pragma once
#include "WindowMenuItems.hpp"
#include "i18n.h"
#include "filament.hpp"
#include "WindowItemFormatableLabel.hpp"
#include "WindowItemFanLabel.hpp"
#include "config.h"
#include <buddy/door_sensor.hpp>
#include <common/filament_sensor.hpp>
#include <common/filament_sensor_states.hpp>
#include <utility_extensions.hpp>
#include <option/has_door_sensor.h>
#include <option/has_dwarf.h>
#include <option/has_filament_sensors_menu.h>
#include <option/has_coldpull.h>
#include <option/has_leds.h>
#include <option/has_phase_stepping_toggle.h>
#include <option/has_side_leds.h>
#include <option/buddy_enable_connect.h>
#include <option/has_belt_tuning.h>
#include <option/has_auto_retract.h>
#include <meta_utils.hpp>
#include <gui/menu_item/menu_item_gcode_action.hpp>

class MI_ODOMETER_DIST : public WI_FORMATABLE_LABEL_t<float> {
public:
    MI_ODOMETER_DIST(const string_view_utf8 &label, const img::Resource *icon, is_enabled_t enabled, is_hidden_t hidden, float initVal);
};

class MI_ODOMETER_DIST_X : public MI_ODOMETER_DIST {
    constexpr static const char *const label = N_("X Axis");

public:
    MI_ODOMETER_DIST_X();
};
class MI_ODOMETER_DIST_Y : public MI_ODOMETER_DIST {
    constexpr static const char *const label = N_("Y Axis");

public:
    MI_ODOMETER_DIST_Y();
};
class MI_ODOMETER_DIST_Z : public MI_ODOMETER_DIST {
    constexpr static const char *const label = N_("Z Axis");

public:
    MI_ODOMETER_DIST_Z();
};

/// Extruded filament
class MI_ODOMETER_DIST_E : public MI_ODOMETER_DIST {
    constexpr static const char *const generic_label = N_("Filament");

public:
    MI_ODOMETER_DIST_E(const char *const label, int index);
    MI_ODOMETER_DIST_E();
};

/// Tool picked
class MI_ODOMETER_TOOL : public WI_FORMATABLE_LABEL_t<uint32_t> {
    constexpr static const char *const generic_label = N_("Tools Changed");
    constexpr static const char *const times_label = N_("times"); // Tools Changed      123 times

public:
    MI_ODOMETER_TOOL(const char *const label, int index);
    MI_ODOMETER_TOOL();
};

class MI_ODOMETER_MMU_CHANGES : public WI_FORMATABLE_LABEL_t<uint32_t> {
    constexpr static const char *const label = N_("MMU filament loads");

public:
    MI_ODOMETER_MMU_CHANGES();
};

class MI_ODOMETER_TIME : public WI_FORMATABLE_LABEL_t<uint32_t> {
    constexpr static const char *const label = N_("Print Time");

public:
    MI_ODOMETER_TIME();
};

#if BOARD_IS_XBUDDY()
class MI_INFO_HEATER_VOLTAGE : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_HEATER_VOLTAGE();
};

class MI_INFO_HEATER_CURRENT : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_HEATER_CURRENT();
};

class MI_INFO_INPUT_CURRENT : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_INPUT_CURRENT();
};

class MI_INFO_MMU_CURRENT : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_MMU_CURRENT();
};
#endif

#if BOARD_IS_XLBUDDY()
class MI_INFO_5V_VOLTAGE : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_5V_VOLTAGE();
};

class MI_INFO_SANDWICH_5V_CURRENT : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_SANDWICH_5V_CURRENT();
};

class MI_INFO_BUDDY_5V_CURRENT : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_BUDDY_5V_CURRENT();
};
#endif

class MI_INFO_INPUT_VOLTAGE : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_INPUT_VOLTAGE();
};

class MI_INFO_BOARD_TEMP : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_BOARD_TEMP();
};

#if HAS_DOOR_SENSOR()
class MI_INFO_DOOR_SENSOR : public MenuItemAutoUpdatingLabel<buddy::DoorSensor::DetailedState> {
private:
    void print_val(const std::span<char> &buffer) const;

public:
    MI_INFO_DOOR_SENSOR();
};
#endif

class MI_INFO_MCU_TEMP final : public MenuItemAutoUpdatingLabel<float> {
public:
    MI_INFO_MCU_TEMP();
};
