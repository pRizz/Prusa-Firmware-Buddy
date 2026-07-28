#include "ili9488_commands.hpp"

#include "ili9488.hpp"

#include <cstddef>

namespace {

constexpr uint8_t flag_dma = 0x08;
constexpr uint8_t default_madctl = 0xE0;
constexpr uint8_t default_colmod = 0x66;
constexpr uint8_t mask_control_brightness = 1 << 5;
constexpr uint8_t mask_control_backlight = 1 << 2;

enum Command : uint8_t {
    command_sleep_out = 0x11,
    command_inversion_off = 0x20,
    command_inversion_on = 0x21,
    command_gamma_set = 0x26,
    command_display_off = 0x28,
    command_display_on = 0x29,
    command_column_address_set = 0x2A,
    command_row_address_set = 0x2B,
    command_memory_write = 0x2C,
    command_memory_access_control = 0x36,
    command_pixel_format = 0x3A,
    command_write_brightness = 0x51,
    command_write_control = 0x53,
    command_backlight_pwm = 0xC8,
};

struct Config {
    uint8_t flags;
    uint8_t gamma;
    uint8_t brightness;
    uint8_t is_inverted;
    uint8_t control;
};

Config config {
    .flags = flag_dma,
    .gamma = 0,
    .brightness = 0,
    .is_inverted = 0,
    .control = 0,
};

enum class StartupAction : uint8_t {
    command,
    delay,
    clear,
    inversion_on,
};

struct StartupStep {
    StartupAction action;
    uint8_t command;
    const uint8_t *data;
    uint8_t data_size;
    uint16_t value;
};

constexpr uint8_t data_madctl[] = { default_madctl };
constexpr uint8_t data_colmod[] = { default_colmod };
constexpr uint8_t data_adjust_control[] = { 0xA9, 0x51, 0x2C, 0x82 };
constexpr uint8_t data_frame_rate[] = { 0xA0, 0x11 };
constexpr uint8_t data_inversion_control[] = { 0x02 };
constexpr uint8_t data_power_control_1[] = { 0x0F, 0x0F };
constexpr uint8_t data_power_control_2[] = { 0x41 };
constexpr uint8_t data_power_control_3[] = { 0x22 };
constexpr uint8_t data_vcom_control[] = { 0x00, 0x53, 0x80 };
constexpr uint8_t data_entry_mode[] = { 0xC6 };
constexpr uint8_t data_positive_gamma[] = { 0x00, 0x08, 0x0C, 0x02, 0x0E, 0x04, 0x30, 0x45, 0x47, 0x04, 0x0C, 0x0A, 0x2E, 0x34, 0x0F };
constexpr uint8_t data_negative_gamma[] = { 0x00, 0x11, 0x0D, 0x01, 0x0F, 0x05, 0x39, 0x36, 0x51, 0x06, 0x0F, 0x0D, 0x33, 0x37, 0x0F };

constexpr StartupStep old_manufacturer_startup[] = {
    { StartupAction::command, command_sleep_out, nullptr, 0, 0 },
    { StartupAction::delay, 0, nullptr, 0, 120 },
    { StartupAction::command, command_memory_access_control, data_madctl, sizeof(data_madctl), 0 },
    { StartupAction::command, command_pixel_format, data_colmod, sizeof(data_colmod), 0 },
    { StartupAction::command, command_display_on, nullptr, 0, 0 },
    { StartupAction::delay, 0, nullptr, 0, 10 },
    { StartupAction::clear, 0, nullptr, 0, 0 },
    { StartupAction::delay, 0, nullptr, 0, 100 },
    { StartupAction::inversion_on, 0, nullptr, 0, 0 },
};

constexpr StartupStep new_manufacturer_startup[] = {
    { StartupAction::command, 0xF7, data_adjust_control, sizeof(data_adjust_control), 0 },
    { StartupAction::command, command_memory_access_control, data_madctl, sizeof(data_madctl), 0 },
    { StartupAction::command, command_pixel_format, data_colmod, sizeof(data_colmod), 0 },
    { StartupAction::command, 0xB1, data_frame_rate, sizeof(data_frame_rate), 0 },
    { StartupAction::command, 0xB4, data_inversion_control, sizeof(data_inversion_control), 0 },
    { StartupAction::command, 0xC0, data_power_control_1, sizeof(data_power_control_1), 0 },
    { StartupAction::command, 0xC1, data_power_control_2, sizeof(data_power_control_2), 0 },
    { StartupAction::command, 0xC2, data_power_control_3, sizeof(data_power_control_3), 0 },
    { StartupAction::command, 0xC5, data_vcom_control, sizeof(data_vcom_control), 0 },
    { StartupAction::command, 0xB7, data_entry_mode, sizeof(data_entry_mode), 0 },
    { StartupAction::command, 0xE0, data_positive_gamma, sizeof(data_positive_gamma), 0 },
    { StartupAction::command, 0xE1, data_negative_gamma, sizeof(data_negative_gamma), 0 },
    { StartupAction::inversion_on, 0, nullptr, 0, 0 },
    { StartupAction::command, command_sleep_out, nullptr, 0, 0 },
    { StartupAction::delay, 0, nullptr, 0, 120 },
    { StartupAction::command, command_display_on, nullptr, 0, 0 },
    { StartupAction::clear, 0, nullptr, 0, 0 },
};

constexpr StartupStep bootloader_startup[] = {
    { StartupAction::command, command_memory_access_control, data_madctl, sizeof(data_madctl), 0 },
    { StartupAction::command, command_pixel_format, data_colmod, sizeof(data_colmod), 0 },
    { StartupAction::inversion_on, 0, nullptr, 0, 0 },
};

} // namespace

void ili9488_cmd(uint8_t command, const uint8_t *data, uint16_t size);
void ili9488_rd(uint8_t *data, uint16_t size);
void ili9488_delay_ms(uint32_t milliseconds);

namespace {

template <size_t Size>
void run(const StartupStep (&steps)[Size]) {
    for (const auto &step : steps) {
        switch (step.action) {
        case StartupAction::command:
            ili9488_cmd(step.command, step.data, step.data_size);
            break;
        case StartupAction::delay:
            ili9488_delay_ms(step.value);
            break;
        case StartupAction::clear:
            ili9488_clear(0x000000);
            break;
        case StartupAction::inversion_on:
            ili9488_inversion_on();
            break;
        }
    }
}

} // namespace

uint8_t ili9488_default_flags() {
    return config.flags;
}

void ili9488_run_startup_commands(bool new_manufacturer) {
    if (new_manufacturer) {
        run(new_manufacturer_startup);
    } else {
        run(old_manufacturer_startup);
    }
}

void ili9488_run_bootloader_commands() {
    run(bootloader_startup);
}

void ili9488_configure_backlight_pwm() {
    uint8_t pwm_inverted = 0b10110001;
    ili9488_cmd(command_backlight_pwm, &pwm_inverted, sizeof(pwm_inverted));
}

void ili9488_cmd_dispon() {
    ili9488_cmd(command_display_on, nullptr, 0);
}

void ili9488_cmd_dispoff() {
    ili9488_cmd(command_display_off, nullptr, 0);
}

void ili9488_cmd_caset(uint16_t x, uint16_t end_x) {
    uint8_t data[] = {
        static_cast<uint8_t>(x >> 8),
        static_cast<uint8_t>(x),
        static_cast<uint8_t>(end_x >> 8),
        static_cast<uint8_t>(end_x),
    };
    ili9488_cmd(command_column_address_set, data, sizeof(data));
}

void ili9488_cmd_raset(uint16_t y, uint16_t end_y) {
    uint8_t data[] = {
        static_cast<uint8_t>(y >> 8),
        static_cast<uint8_t>(y),
        static_cast<uint8_t>(end_y >> 8),
        static_cast<uint8_t>(end_y),
    };
    ili9488_cmd(command_row_address_set, data, sizeof(data));
}

void ili9488_cmd_ramwr(uint8_t *data, uint16_t size) {
    ili9488_cmd(command_memory_write, data, size);
}

void ili9488_cmd_ramrd(uint8_t *data, uint16_t size) {
    ili9488_rd(data, size);
}

void ili9488_inversion_on() {
    config.is_inverted = 1;
    ili9488_cmd(command_inversion_on, nullptr, 0);
}

void ili9488_inversion_off() {
    config.is_inverted = 0;
    ili9488_cmd(command_inversion_off, nullptr, 0);
}

void ili9488_inversion_tgl() {
    config.is_inverted = !config.is_inverted;
    ili9488_cmd(command_inversion_off + config.is_inverted, nullptr, 0);
}

uint8_t ili9488_inversion_get() {
    return config.is_inverted;
}

void ili9488_gamma_set_direct(uint8_t gamma) {
    config.gamma = gamma;
    ili9488_cmd(command_gamma_set, &config.gamma, sizeof(config.gamma));
}

void ili9488_gamma_next() {
    ili9488_gamma_set_direct(((config.gamma << 1) | (config.gamma >> 3)) & 0x0F);
}

void ili9488_gamma_prev() {
    ili9488_gamma_set_direct(((config.gamma << 3) | (config.gamma >> 1)) & 0x0F);
}

void ili9488_gamma_set(uint8_t gamma) {
    if (gamma != ili9488_gamma_get()) {
        ili9488_gamma_set_direct(1 << (gamma & 0x03));
    }
}

uint8_t ili9488_gamma_get() {
    uint8_t position = 3;
    for (; position != 0; --position) {
        if (config.gamma == 1 << position) {
            break;
        }
    }
    return position;
}

void ili9488_ctrl_set(uint8_t control) {
    config.control = control;
    ili9488_cmd(command_write_control, &config.control, sizeof(config.control));
}

void ili9488_brightness_enable() {
    ili9488_ctrl_set(config.control | mask_control_brightness | mask_control_backlight);
}

void ili9488_brightness_disable() {
    ili9488_ctrl_set(config.control & ~mask_control_brightness & ~mask_control_backlight);
}

void ili9488_brightness_set(uint8_t brightness) {
    config.brightness = brightness;
    ili9488_cmd(command_write_brightness, &config.brightness, sizeof(config.brightness));
}

uint8_t ili9488_brightness_get() {
    return config.brightness;
}
