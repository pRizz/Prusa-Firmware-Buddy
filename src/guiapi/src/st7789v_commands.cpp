#include "st7789v_commands.hpp"

#include "st7789v.hpp"

#include <cstddef>

namespace {

constexpr uint8_t flg_dma = 0x08;
constexpr uint8_t default_madctl = 0xC0;
constexpr uint8_t default_colmod = 0x05;
constexpr uint8_t mask_ctrld_bctrl = 1 << 5;
constexpr uint8_t max_command_read_length = 4;

enum Command : uint8_t {
    cmd_madctl_read = 0x0b,
    cmd_sleep_out = 0x11,
    cmd_inversion_off = 0x20,
    cmd_inversion_on = 0x21,
    cmd_gamma_set = 0x26,
    cmd_display_on = 0x29,
    cmd_column_address_set = 0x2A,
    cmd_row_address_set = 0x2B,
    cmd_memory_write = 0x2C,
    cmd_memory_read = 0x2E,
    cmd_memory_access_control = 0x36,
    cmd_pixel_format = 0x3A,
    cmd_write_brightness = 0x51,
    cmd_write_control = 0x53,
};

struct Config {
    uint8_t flags;
    uint8_t gamma;
    uint8_t brightness;
    uint8_t is_inverted;
    uint8_t control;
};

Config config {
    .flags = flg_dma,
    .gamma = 0,
    .brightness = 0,
    .is_inverted = 0,
    .control = 0,
};

struct StartupCommand {
    uint8_t command;
    uint8_t data;
    uint8_t data_size;
    uint16_t delay_after_ms;
};

constexpr StartupCommand startup_commands[] = {
    { cmd_sleep_out, 0, 0, 120 },
    { cmd_memory_access_control, default_madctl, 1, 0 },
    { cmd_pixel_format, default_colmod, 1, 0 },
    { cmd_display_on, 0, 0, 10 },
};

} // namespace

void st7789v_cmd(uint8_t command, uint8_t *data, uint16_t size);
void st7789v_cmd_rd(uint8_t command, uint8_t *data);
void st7789v_rd(uint8_t *data, uint16_t size);
void st7789v_delay_ms(uint32_t milliseconds);

uint8_t st7789v_default_flags() {
    return config.flags;
}

void st7789v_run_startup_commands() {
    for (const auto &step : startup_commands) {
        auto data = step.data;
        st7789v_cmd(step.command, step.data_size == 0 ? nullptr : &data, step.data_size);
        if (step.delay_after_ms != 0) {
            st7789v_delay_ms(step.delay_after_ms);
        }
    }
}

void st7789v_cmd_caset(uint16_t x, uint16_t end_x) {
    uint8_t data[] = {
        static_cast<uint8_t>(x >> 8),
        static_cast<uint8_t>(x),
        static_cast<uint8_t>(end_x >> 8),
        static_cast<uint8_t>(end_x),
    };
    st7789v_cmd(cmd_column_address_set, data, sizeof(data));
}

void st7789v_cmd_raset(uint16_t y, uint16_t end_y) {
    uint8_t data[] = {
        static_cast<uint8_t>(y >> 8),
        static_cast<uint8_t>(y),
        static_cast<uint8_t>(end_y >> 8),
        static_cast<uint8_t>(end_y),
    };
    st7789v_cmd(cmd_row_address_set, data, sizeof(data));
}

void st7789v_cmd_colmod(uint8_t pixel_format) {
    st7789v_cmd(cmd_pixel_format, &pixel_format, 1);
}

void st7789v_cmd_ramwr(uint8_t *data, uint16_t size) {
    st7789v_cmd(cmd_memory_write, data, size);
}

void st7789v_cmd_ramrd(uint8_t *data, uint16_t size) {
    st7789v_cmd(cmd_memory_read, nullptr, 0);
    st7789v_rd(data, size);
}

bool st7789v_is_reset_required() {
    uint8_t data[max_command_read_length] {};
    st7789v_cmd_rd(cmd_madctl_read, data);
    return data[1] != 0xE0 && data[1] != 0xF0 && data[1] != 0xF8;
}

void st7789v_inversion_on() {
    config.is_inverted = 1;
    st7789v_cmd(cmd_inversion_on, nullptr, 0);
}

void st7789v_inversion_off() {
    config.is_inverted = 0;
    st7789v_cmd(cmd_inversion_off, nullptr, 0);
}

void st7789v_inversion_tgl() {
    config.is_inverted = !config.is_inverted;
    st7789v_cmd(cmd_inversion_off + config.is_inverted, nullptr, 0);
}

uint8_t st7789v_inversion_get() {
    return config.is_inverted;
}

void st7789v_gamma_set_direct(uint8_t gamma) {
    config.gamma = gamma;
    st7789v_cmd(cmd_gamma_set, &config.gamma, sizeof(config.gamma));
}

void st7789v_gamma_next() {
    st7789v_gamma_set_direct(((config.gamma << 1) | (config.gamma >> 3)) & 0x0f);
}

void st7789v_gamma_prev() {
    st7789v_gamma_set_direct(((config.gamma << 3) | (config.gamma >> 1)) & 0x0f);
}

void st7789v_gamma_set(uint8_t gamma) {
    if (gamma != st7789v_gamma_get()) {
        st7789v_gamma_set_direct(1 << (gamma & 0x03));
    }
}

uint8_t st7789v_gamma_get() {
    uint8_t position = 3;
    for (; position != 0; --position) {
        if (config.gamma == 1 << position) {
            break;
        }
    }
    return position;
}

void st7789v_ctrl_set(uint8_t control) {
    config.control = control;
    st7789v_cmd(cmd_write_control, &config.control, sizeof(config.control));
}

void st7789v_brightness_enable() {
    st7789v_ctrl_set(config.control | mask_ctrld_bctrl);
}

void st7789v_brightness_disable() {
    st7789v_ctrl_set(config.control & ~mask_ctrld_bctrl);
}

void st7789v_brightness_set(uint8_t brightness) {
    config.brightness = brightness;
    st7789v_cmd(cmd_write_brightness, &config.brightness, sizeof(config.brightness));
}

uint8_t st7789v_brightness_get() {
    return config.brightness;
}
