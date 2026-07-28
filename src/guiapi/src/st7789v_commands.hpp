#pragma once

#include <cstdint>

uint8_t st7789v_default_flags();
void st7789v_run_startup_commands();
void st7789v_cmd_caset(uint16_t x, uint16_t end_x);
void st7789v_cmd_raset(uint16_t y, uint16_t end_y);
void st7789v_cmd_colmod(uint8_t pixel_format);
void st7789v_cmd_ramwr(uint8_t *data, uint16_t size);
void st7789v_cmd_ramrd(uint8_t *data, uint16_t size);
