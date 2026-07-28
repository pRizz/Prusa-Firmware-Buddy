#pragma once

#include <cstdint>

uint8_t ili9488_default_flags();
void ili9488_run_startup_commands(bool new_manufacturer);
void ili9488_run_bootloader_commands();
void ili9488_configure_backlight_pwm();
void ili9488_cmd_caset(uint16_t x, uint16_t end_x);
void ili9488_cmd_raset(uint16_t y, uint16_t end_y);
void ili9488_cmd_ramwr(uint8_t *data, uint16_t size);
void ili9488_cmd_ramrd(uint8_t *data, uint16_t size);
