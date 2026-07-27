#include "MItem_tools.hpp"
#include "img_resources.hpp"
#include "marlin_client.hpp"
#include "marlin_server.hpp"
#include "gui.hpp"
#include "time_helper.hpp"
#include "window_dlg_wait.hpp"
#include "window_file_list.hpp"
#include "sound.hpp"
#include "wui_api.h"
#include "printers.h"
#include "i18n.h"
#include "ScreenHandler.hpp"
#include "bsod.h"
#include "filament_sensors_handler.hpp"
#include "liveadjust_z.hpp"
#include "filament_sensor.hpp"
#include <buddy/main.h>
#include "Pin.hpp"
#include "hwio_pindef.h"
#include "config.h"
#include "WindowMenuSpin.hpp"
#include "time_tools.hpp"
#include "footer_eeprom.hpp"
#include <version/version.hpp>
#include <common/sys.hpp>
#include <common/w25x.hpp>
#include <bootloader/bootloader.hpp>
#include "config_features.h"
#include <config_store/store_instance.hpp>
#include "connect/marlin_printer.hpp"
#include <crash_dump/dump.hpp>
#include <feature/prusa/e-stall_detector.h>
#include <option/bootloader.h>
#include <option/filament_sensor.h>
#include <option/has_phase_stepping_toggle.h>
#include <option/has_side_leds.h>
#include <option/has_coldpull.h>
#include <RAII.hpp>
#include <time.h>
#include <footer_items_heaters.hpp>
#include <footer_line.hpp>
#include <freertos/critical_section.hpp>
#include <utils/string_builder.hpp>
#include <netdev.h>
#include <wui.h>
#include <power_panic.hpp>
#include <logging/log_dest_file.hpp>
#include <numeric_input_config_common.hpp>

#include <type_traits>

#if ENABLED(PRUSA_TOOLCHANGER)
    #include "../../../lib/Marlin/Marlin/src/module/prusa/toolchanger.h"
    #include "screen_menu_tools.hpp"
    #include <window_tool_action_box.hpp>
#endif

#if HAS_LEDS()
    #include <leds/status_leds_handler.hpp>
#endif

#if HAS_SIDE_LEDS()
    #include <leds/side_strip_handler.hpp>
#endif

#if BUDDY_ENABLE_CONNECT()
    #include <connect/marlin_printer.hpp>
#endif

#include <option/has_xbuddy_extension.h>
#if HAS_XBUDDY_EXTENSION()
    #include <puppies/xbuddy_extension.hpp>
#endif

#ifdef HAS_TMC_WAVETABLE
    #include <feature/tmc_util.h>
#endif

#if BOARD_IS_XBUDDY()
MI_INFO_HEATER_VOLTAGE::MI_INFO_HEATER_VOLTAGE()
    : MenuItemAutoUpdatingLabel(_("Heater Voltage"), "%.1f V",
          [](auto) { return sensor_data().heaterVoltage.load(); } //
      ) {}

MI_INFO_HEATER_CURRENT::MI_INFO_HEATER_CURRENT()
    : MenuItemAutoUpdatingLabel(_("Heater Current"), "%.1f A",
          [](auto) { return sensor_data().heaterCurrent.load(); } //
      ) {}

MI_INFO_INPUT_CURRENT::MI_INFO_INPUT_CURRENT()
    : MenuItemAutoUpdatingLabel(_("Input Current"), "%.1f A",
          [](auto) { return sensor_data().inputCurrent.load(); } //
      ) {}

MI_INFO_MMU_CURRENT::MI_INFO_MMU_CURRENT()
    : MenuItemAutoUpdatingLabel(_("MMU Current"), "%.1f A",
          [](auto) { return sensor_data().mmuCurrent.load(); } //
      ) {}
#endif

#if BOARD_IS_XLBUDDY()
MI_INFO_5V_VOLTAGE::MI_INFO_5V_VOLTAGE()
    : MenuItemAutoUpdatingLabel(_("5V Voltage"), "%.1f V",
          [](auto) { return sensor_data().sandwich5VVoltage.load(); } //
      ) {}

MI_INFO_SANDWICH_5V_CURRENT::MI_INFO_SANDWICH_5V_CURRENT()
    : MenuItemAutoUpdatingLabel(_("Sandwich 5V Current"), "%.2f A",
          [](auto) { return sensor_data().sandwich5VCurrent.load(); } //
      ) {}

MI_INFO_BUDDY_5V_CURRENT::MI_INFO_BUDDY_5V_CURRENT()
    : MenuItemAutoUpdatingLabel(_("XL Buddy 5V Current"), "%.2f A",
          [](auto) { return sensor_data().buddy5VCurrent.load(); } //
      ) {}
#endif

MI_INFO_INPUT_VOLTAGE::MI_INFO_INPUT_VOLTAGE()
    : MenuItemAutoUpdatingLabel(_("Input Voltage"), "%.1f V",
          [](auto) { return sensor_data().inputVoltage.load(); } //
      ) {}

MI_INFO_BOARD_TEMP::MI_INFO_BOARD_TEMP()
    : MenuItemAutoUpdatingLabel(_("Board Temperature"), standard_print_format::temp_c,
          [](auto) { return sensor_data().boardTemp.load(); } //
      ) {
}

#if HAS_DOOR_SENSOR()
MI_INFO_DOOR_SENSOR::MI_INFO_DOOR_SENSOR()
    : MenuItemAutoUpdatingLabel(
          _("Door Sensor"),
          [this](const std::span<char> &buffer) { print_val(buffer); },
          [](auto) { return sensor_data().door_sensor_detailed_state.load(); } //
      ) {
}

void MI_INFO_DOOR_SENSOR::print_val(const std::span<char> &buffer) const {
    static constexpr EnumArray<buddy::DoorSensor::State, const char *, 3> texts {
        { buddy::DoorSensor::State::sensor_detached, N_("detached") },
        { buddy::DoorSensor::State::door_open, N_("open") },
        { buddy::DoorSensor::State::door_closed, N_("closed") },
    };
    const auto detailed_state = value();
    StringBuilder sb(buffer);
    sb.append_string_view(_(texts[detailed_state.state]));
    sb.append_printf(" / 0x%04x", detailed_state.raw_data);
}
#endif

MI_INFO_MCU_TEMP::MI_INFO_MCU_TEMP()
    : MenuItemAutoUpdatingLabel(_("MCU Temperature"), standard_print_format::temp_c,
          [](auto) { return sensor_data().MCUTemp.load(); } //
      ) {}

MI_FOOTER_RESET::MI_FOOTER_RESET()
    : IWindowMenuItem(_(label), nullptr, is_enabled_t::yes, is_hidden_t::no) {
}

void MI_FOOTER_RESET::click([[maybe_unused]] IWindowMenu &window_menu) {
    // simple reset of footer eeprom would be better
    // but footer does not have reload method
    FooterItemHeater::ResetDrawMode();
    FooterLine::SetCenterN(footer::default_center_n_and_fewer);

    for (size_t i = 0; i < FOOTER_ITEMS_PER_LINE__; ++i) {
        config_store().set_footer_setting(i, footer::default_items[i]);
    }
    // send event for all footers
    Screens::Access()->ScreenEvent(nullptr, GUI_event_t::REINIT_FOOTER, footer::encode_item_for_event(footer::Item::none));

    // close this menu, because it is no longer valid and needs to be redrawn
    Screens::Access()->Close();
}

static constexpr const char *heatup_bed_values[] = {
    N_("Nozzle"),
    N_("All"),
};

MI_FILAMENT_CHANGE_PREHEAT_ALL::MI_FILAMENT_CHANGE_PREHEAT_ALL()
    : MenuItemSwitch(_("For Filament Change, Preheat"), heatup_bed_values, config_store().filament_change_preheat_all.get()) {
}
void MI_FILAMENT_CHANGE_PREHEAT_ALL::OnChange(size_t old_index) {
    config_store().filament_change_preheat_all.set(!old_index);
}

MI_SET_READY::MI_SET_READY()
    : IWindowMenuItem(_(label), &img::set_ready_16x16, connect_client::MarlinPrinter::is_printer_ready() ? is_enabled_t::no : is_enabled_t::yes, is_hidden_t::no) {
}

void MI_SET_READY::click([[maybe_unused]] IWindowMenu &window_menu) {
    if (connect_client::MarlinPrinter::set_printer_ready(true)) {
        set_enabled(false);
    }
}

#if HAS_PHASE_STEPPING_TOGGLE()
MI_PHASE_STEPPING_TOGGLE::MI_PHASE_STEPPING_TOGGLE()
    : WI_ICON_SWITCH_OFF_ON_t(0, _(label), nullptr, is_enabled_t::yes, is_hidden_t::no) {
    bool phstep_enabled = config_store().get_phase_stepping_enabled();
    set_value(phstep_enabled);
}

void MI_PHASE_STEPPING_TOGGLE::OnChange([[maybe_unused]] size_t old_index) {
    if (event_in_progress) {
        return;
    }

    if (value() && (config_store().selftest_result_phase_stepping.get() != TestResult_Passed)) {
    #if PRINTER_IS_PRUSA_iX() || PRINTER_IS_PRUSA_COREONE()
        if (MsgBoxQuestion(_("Turn on Phase stepping uncalibrated?"), Responses_YesNo) == Response::No) {
            AutoRestore ar(event_in_progress, true);
            set_value(old_index);
            return;
        }
    #else
        AutoRestore ar(event_in_progress, true);
        MsgBoxWarning(_("Phase stepping not ready: perform calibration first."), Responses_Ok);
        set_value(old_index);
        return;
    #endif
    }

    if (value()) {
        marlin_client::gcode("M970 X1 Y1"); // turn phase stepping on
    } else {
        marlin_client::gcode("M970 X0 Y0"); // turn phase stepping off
    }

    // we need to wait until the action actually takes place so that when returning
    // to the menu (if any) the new state is already reflected
    window_dlg_wait_t::wait_for_gcodes_to_finish();
}
#endif

#if HAS_COLDPULL()
MI_COLD_PULL::MI_COLD_PULL()
    : IWindowMenuItem(_(label), nullptr, is_enabled_t::yes, is_hidden_t::no) {
}

void MI_COLD_PULL::click([[maybe_unused]] IWindowMenu &window_menu) {
    marlin_client::gcode("M1702");
}
#endif

MI_GCODE_VERIFY::MI_GCODE_VERIFY()
    : WI_ICON_SWITCH_OFF_ON_t(config_store().verify_gcode.get(), _(label), nullptr, is_enabled_t::yes, is_hidden_t::no) {}

void MI_GCODE_VERIFY::OnChange([[maybe_unused]] size_t old_index) {
    bool newState = !config_store().verify_gcode.get();
    config_store().verify_gcode.set(newState);
}

/*****************************************************************************/
// MI_DEVHASH_IN_QR
MI_DEVHASH_IN_QR::MI_DEVHASH_IN_QR()
    : WI_ICON_SWITCH_OFF_ON_t(config_store().devhash_in_qr.get(), _(label), nullptr, is_enabled_t::yes, is_hidden_t::no) {}
void MI_DEVHASH_IN_QR::OnChange(size_t old_index) {
    config_store().devhash_in_qr.set(!old_index);
}

#ifdef HAS_TMC_WAVETABLE
MI_WAVETABLE_XYZ::MI_WAVETABLE_XYZ()
    : WI_ICON_SWITCH_OFF_ON_t(config_store().tmc_wavetable_enabled.get(), _(label), nullptr, is_enabled_t::yes, is_hidden_t::dev) {}
void MI_WAVETABLE_XYZ::OnChange(size_t old_index) {
    /// enable
    old_index ? tmc_disable_wavetable(true, true, true) : tmc_enable_wavetable(true, true, true);
    config_store().tmc_wavetable_enabled.set(!old_index);
}
#endif

/**********************************************************************************************/
// MI_LOAD_SETTINGS

MI_LOAD_SETTINGS::MI_LOAD_SETTINGS()
    : IWindowMenuItem(_(label), nullptr, is_enabled_t::yes, is_hidden_t::no) {
}

void MI_LOAD_SETTINGS::click(IWindowMenu & /*window_menu*/) {
    auto build_message = [](StringBuilder &msg_builder, const string_view_utf8 &name, bool ok) {
        msg_builder.append_string_view(name);
        msg_builder.append_string(": ");
        msg_builder.append_string_view(ok ? _("Ok") : _("Failed"));
        msg_builder.append_char('\n');
    };
    std::array<char, 150> msg;
    StringBuilder msg_builder(msg);
    msg_builder.append_string_view(_("\nLoading settings finished.\n\n"));

    const bool network_settings_loaded = netdev_load_ini_to_eeprom();
    if (network_settings_loaded) {
        notify_reconfigure();
    }
    build_message(msg_builder, _("Network"), network_settings_loaded);

#if BUDDY_ENABLE_CONNECT()
    build_message(msg_builder, _("Connect"), connect_client::MarlinPrinter::load_cfg_from_ini());
#endif

    MsgBoxInfo(string_view_utf8::MakeRAM(msg.data()), Responses_Ok);
}

#if HAS_LEDS()
/**********************************************************************************************/
// MI_LEDS_ENABLE
MI_LEDS_ENABLE::MI_LEDS_ENABLE()
    : WI_ICON_SWITCH_OFF_ON_t(leds::StatusLedsHandler::instance().get_active(), _(label), nullptr, is_enabled_t::yes, is_hidden_t::no) {
}
void MI_LEDS_ENABLE::OnChange(size_t old_index) {
    if (old_index) {
        leds::StatusLedsHandler::instance().set_active(false);
    } else {
        leds::StatusLedsHandler::instance().set_active(true);
    }
}
#endif

#if HAS_SIDE_LEDS()
/**********************************************************************************************/
// MI_SIDE_LEDS_MAX_BRIGTHNESS
MI_SIDE_LEDS_MAX_BRIGTHNESS::MI_SIDE_LEDS_MAX_BRIGTHNESS()
    : WiSpin(
          static_cast<float>(leds::SideStripHandler::instance().get_max_brightness()) * 100 / 255,
          numeric_input_config::percent_with_off,
          _(label)) {
}

void MI_SIDE_LEDS_MAX_BRIGTHNESS::OnClick() {
    leds::SideStripHandler::instance().set_max_brightness(static_cast<uint8_t>(value()) * 255 / 100);
}
#endif

#if HAS_SIDE_LEDS()
/**********************************************************************************************/
// MI_SIDE_LEDS_DIMMED_BRIGTHNESS

MI_SIDE_LEDS_DIMMED_BRIGTHNESS::MI_SIDE_LEDS_DIMMED_BRIGTHNESS()
    : WiSpin(
          static_cast<float>(leds::SideStripHandler::instance().get_dimmed_brightness()) * 100 / 255,
          numeric_input_config::percent_with_off,
          _(label)) {
}

void MI_SIDE_LEDS_DIMMED_BRIGTHNESS::OnClick() {
    leds::SideStripHandler::instance().set_dimmed_brightness(static_cast<uint8_t>(value()) * 255 / 100);
}

void MI_SIDE_LEDS_DIMMED_BRIGTHNESS::Loop() {
    set_enabled(leds::SideStripHandler::instance().get_dimming_enabled() != leds::DimmingEnabled::never);
}
#endif

#if HAS_SIDE_LEDS()
/**********************************************************************************************/
// MI_SIDE_LEDS_DIMMING_ENABLE
static constexpr EnumArray<leds::DimmingEnabled, const char *, leds::DimmingEnabled::_cnt> dimming_enabled_values {
    { leds::DimmingEnabled::never, N_("Never") },
    { leds::DimmingEnabled::always, N_("Always") },
    { leds::DimmingEnabled::not_printing, N_("On Idle") },
};

MI_SIDE_LEDS_DIMMING_ENABLE::MI_SIDE_LEDS_DIMMING_ENABLE()
    : MenuItemSwitch(_(label), dimming_enabled_values, std::to_underlying(leds::SideStripHandler::instance().get_dimming_enabled())) {
}
void MI_SIDE_LEDS_DIMMING_ENABLE::OnChange([[maybe_unused]] size_t old_index) {
    leds::SideStripHandler::instance().set_dimming_enabled(static_cast<leds::DimmingEnabled>(get_index()));
}
#endif

#if ENABLED(PRUSA_TOOLCHANGER)
/**********************************************************************************************/
// MI_TOOL_LEDS_ENABLE
MI_TOOL_LEDS_ENABLE::MI_TOOL_LEDS_ENABLE()
    : WI_ICON_SWITCH_OFF_ON_t(config_store().tool_leds_enabled.get(), _(label), nullptr, is_enabled_t::yes, prusa_toolchanger.is_toolchanger_enabled() ? is_hidden_t::no : is_hidden_t::yes) {
}
void MI_TOOL_LEDS_ENABLE::OnChange(size_t old_index) {
    HOTEND_LOOP() {
        prusa_toolchanger.getTool(e).set_cheese_led(!old_index ? 0xff : 0x00, 0x00);
    }
    config_store().tool_leds_enabled.set(!old_index);
}
#endif

/*****************************************************************************/
#if ENABLED(POWER_PANIC)
MI_TRIGGER_POWER_PANIC::MI_TRIGGER_POWER_PANIC()
    : IWindowMenuItem(_(label), nullptr, is_enabled_t::yes, is_hidden_t::dev, expands_t::no) {
}

void MI_TRIGGER_POWER_PANIC::click([[maybe_unused]] IWindowMenu &windowMenu) {
    buddy::hw::acFault.triggerIT();
}
#endif

#if ENABLED(PRUSA_TOOLCHANGER)
/*****************************************************************************/
MI_PICK_PARK_TOOL::MI_PICK_PARK_TOOL()
    : IWindowMenuItem(_(label), nullptr, is_enabled_t::yes, prusa_toolchanger.is_toolchanger_enabled() ? is_hidden_t::no : is_hidden_t::yes, expands_t::yes) {
}

void MI_PICK_PARK_TOOL::click(IWindowMenu & /*window_menu*/) {
    ToolActionBox<ToolBox::MenuPickPark>();
}

/*****************************************************************************/
MI_CALIBRATE_DOCK::MI_CALIBRATE_DOCK()
    : IWindowMenuItem(_(label), nullptr, is_enabled_t::yes, prusa_toolchanger.is_toolchanger_enabled() ? is_hidden_t::no : is_hidden_t::yes, expands_t::yes) {
}

void MI_CALIBRATE_DOCK::click(IWindowMenu & /*window_menu*/) {
    ToolActionBox<ToolBox::MenuCalibrateDock>();
    Screens::Access()->Get()->Validate();
}
#endif

/*****************************************************************************/
#if HAS_ILI9488_DISPLAY()
static constexpr const char *display_baudrate_items[] {
    N_("High"), N_("Low")
};

MI_DISPLAY_BAUDRATE::MI_DISPLAY_BAUDRATE()
    : MenuItemSwitch(_("Display Refresh Speed"), display_baudrate_items, config_store().reduce_display_baudrate.get()) {
}

void MI_DISPLAY_BAUDRATE::OnChange(size_t) {
    config_store().reduce_display_baudrate.set(get_index());
}
#endif

/*****************************************************************************/
MI_LOG_TO_TXT::MI_LOG_TO_TXT()
    : WI_ICON_SWITCH_OFF_ON_t(logging::file_log_is_enabled(), _("Save Logs To File")) {}

void MI_LOG_TO_TXT::OnChange(size_t) {
    if (!value()) {
        logging::file_log_disable();
        MsgBoxInfo(_("Logging has been turned off. You can now safely remove the USB drive."), Responses_Ok);
        return;
    }

    static constexpr const char *location = "/usb/";
    static constexpr const char *filename = "log.txt";

    ArrayStringBuilder<FILE_PATH_BUFFER_LEN> filepath;
    filepath.append_string(location);
    filepath.append_string(filename);

    StringViewUtf8Parameters<FILE_NAME_BUFFER_LEN> fmt_buf;

    if (!logging::file_log_enable(filepath.str())) {
        MsgBoxError(_("Failed to open file '%s' for writing.").formatted(fmt_buf, filename), Responses_Ok);
        set_value(false);
        return;
    }

    log_info(Marlin, "Printer: %s", PrinterModelInfo::current().id_str);
    log_info(Marlin, "Version: %s", version::project_version_full);

    MsgBoxInfo(_("The printer will now save all logs to file until restart.\n\nLog file: %s").formatted(fmt_buf, filename), Responses_Ok);
    MsgBoxWarning(_("Turn the logging off before disconnecting the USB drive, or you risk damaging the filesystem!"), Responses_Ok);
}

#if HAS_AUTO_RETRACT()
MI_PRE_NOZZLE_CLEANING_RETRACT::MI_PRE_NOZZLE_CLEANING_RETRACT()
    : WI_ICON_SWITCH_OFF_ON_t(config_store().pre_nozzle_cleaning_retraction_enable.get(), _("Nozzle Cleaning Retraction")) {}

void MI_PRE_NOZZLE_CLEANING_RETRACT::OnChange(size_t) {
    config_store().pre_nozzle_cleaning_retraction_enable.set(value());
}
#endif
