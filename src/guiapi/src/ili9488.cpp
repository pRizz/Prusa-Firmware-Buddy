#include "ili9488.hpp"
#include "ili9488_commands.hpp"

#include <device/board.h>
#include <device/hal.h>
#include <span>
#include <string.h>
#include <stdlib.h>
#include "qoi_decoder.hpp"
#include <buddy/ccm_thread.hpp>
#include "cmath_ext.h"
#include <stdint.h>
#include "printers.h"
#include <common/spi_baud_rate_prescaler_guard.hpp>
#include "raster_opfn_c.h"
#include "hwio_pindef.h"
#include "cmsis_os.h"
#include "display_math_helper.h"

#include "hw_configuration.hpp"

#include <option/bootloader.h>
#include <option/has_touch.h>
#include <logging/log.hpp>

#if HAS_TOUCH()
    #include <hw/touchscreen/touchscreen.hpp>
#endif

LOG_COMPONENT_REF(GUI);

#define ILI9488_FLG_DMA  0x08 // DMA enabled
#define ILI9488_FLG_SAFE 0x20 // SAFE mode (no DMA and safe delay)

constexpr uint8_t CMD_MADCTLRD = 0x0B;
constexpr uint8_t CMD_RAMRD = 0x2E;
constexpr uint8_t CMD_NOP = 0x00;

uint8_t ili9488_flg = 0; // flags

static constexpr uint8_t ILI9488_MAX_COMMAND_READ_LENGHT = 4;

namespace {
bool do_complete_lcd_reinit = false;
}

static bool reduce_display_baudrate = false;

osThreadId ili9488_task_handle = 0;

#define ILI9488_SIG_SPI_TX 0x0008
#define ILI9488_SIG_SPI_RX 0x0008

uint8_t ili9488_buff[ILI9488_COLS * 3 * ILI9488_BUFF_ROWS]; // 3 bytes for pixel color
bool ili9488_buff_borrowed = false; ///< True if buffer is borrowed by someone else

uint8_t *ili9488_borrow_buffer() {
    assert(!ili9488_buff_borrowed && "Already lent");
    assert(ili9488_task_handle == osThreadGetId() && "Must be called only from one task");
    ili9488_buff_borrowed = true;
    return ili9488_buff;
}

void ili9488_return_buffer() {
    assert(ili9488_buff_borrowed);
    ili9488_buff_borrowed = false;
}

size_t ili9488_buffer_size() {
    return sizeof(ili9488_buff);
}

using namespace buddy::hw;

static void ili9488_set_cs(void) {
#if (BOARD_IS_BUDDY())
    displayCs.write(Pin::State::high);
#endif
}

static void ili9488_clr_cs(void) {
#if (BOARD_IS_BUDDY())
    displayCs.write(Pin::State::low);
#endif
}

static void ili9488_set_rs(void) {
    displayRs.write(Pin::State::high);
}

static void ili9488_clr_rs(void) {
    displayRs.write(Pin::State::low);
}

static void ili9488_set_rst(void) {
    displayRst.write(Pin::State::high);
}

static void ili9488_clr_rst(void) {
    displayRst.write(Pin::State::low);
}

static inline void ili9488_fill_ui16(uint16_t *p, uint16_t v, uint16_t c) {
    while (c--) {
        *(p++) = v;
    }
}

static void ili9488_fill_ui24(uint8_t *p, uint32_t v, int c) {
    while (c--) {
        p[0] = 0xFF & v;
        p[1] = 0xFF & (v >> 8);
        p[2] = 0xFF & (v >> 16);
        p += 3;
    }
}

static inline int is_interrupt(void) {
    return (SCB->ICSR & SCB_ICSR_VECTACTIVE_Msk) != 0;
}

void ili9488_delay_ms(uint32_t ms) {
    if (is_interrupt() || (ili9488_flg & ILI9488_FLG_SAFE)) {
        volatile uint32_t temp;
        while (ms--) {
            do {
                temp = SysTick->CTRL;
            } while ((temp & 0x01) && !(temp & (1 << 16)));
        }
    } else {
        osDelay(ms);
    }
}

void ili9488_spi_wr_byte(uint8_t b) {
    HAL_SPI_Transmit(&SPI_HANDLE_FOR(lcd), &b, 1, HAL_MAX_DELAY);
}

void ili9488_spi_wr_bytes(const uint8_t *pb, uint16_t size) {
    if ((ili9488_flg & ILI9488_FLG_DMA) && !(ili9488_flg & ILI9488_FLG_SAFE) && (size > 4)) {
        osSignalSet(ili9488_task_handle, ILI9488_SIG_SPI_TX);
        osSignalWait(ILI9488_SIG_SPI_TX, osWaitForever);
        assert(can_be_used_by_dma(pb));
        HAL_SPI_Transmit_DMA(&SPI_HANDLE_FOR(lcd), const_cast<uint8_t *>(pb), size);
        osSignalWait(ILI9488_SIG_SPI_TX, osWaitForever);
    } else {
        HAL_SPI_Transmit(&SPI_HANDLE_FOR(lcd), const_cast<uint8_t *>(pb), size, HAL_MAX_DELAY);
    }
}

void ili9488_spi_rd_bytes(uint8_t *pb, uint16_t size) {
    // reading is more reliable at 20MHz
    SPIBaudRatePrescalerGuard guard { &SPI_HANDLE_FOR(lcd), SPI_BAUDRATEPRESCALER_4 };

    HAL_SPI_Receive(&SPI_HANDLE_FOR(lcd), pb, size, HAL_MAX_DELAY);
}

void ili9488_cmd(uint8_t cmd, const uint8_t *pdata, uint16_t size) {
    // BFW-6328 Some displays possibly problematic with higher baudrate, reduce 40 -> 20 MHz
    SPIBaudRatePrescalerGuard _g(&SPI_HANDLE_FOR(lcd), SPI_BAUDRATEPRESCALER_4, reduce_display_baudrate);

    ili9488_clr_cs(); // CS = L
    ili9488_clr_rs(); // RS = L
    ili9488_spi_wr_byte(cmd); // write command byte
    if (pdata && size) {
        ili9488_set_rs(); // RS = H
        ili9488_spi_wr_bytes(pdata, size); // write data bytes
    }
    ili9488_set_cs(); // CS = H
}

template <size_t SZ>
void ili9488_cmd_array(uint8_t cmd, const std::array<uint8_t, SZ> &arr) {
    ili9488_cmd(cmd, arr.data(), SZ);
}

void ili9488_cmd_no_data(uint8_t cmd) {
    ili9488_cmd(cmd, nullptr, 0);
}

void ili9488_cmd_1_data(uint8_t cmd, uint8_t data) {
    ili9488_cmd(cmd, &data, 1);
}

void ili9488_cmd_rd(uint8_t cmd, uint8_t *pdata) {
    // reading is even more reliable at 10MHz
    SPIBaudRatePrescalerGuard guard { &SPI_HANDLE_FOR(lcd), SPI_BAUDRATEPRESCALER_8 };

    ili9488_clr_cs(); // CS = L
    ili9488_clr_rs(); // RS = L
    uint8_t data_to_write[ILI9488_MAX_COMMAND_READ_LENGHT] = { 0x00 };
    data_to_write[0] = cmd;
    data_to_write[1] = 0x00;
    HAL_SPI_TransmitReceive(&SPI_HANDLE_FOR(lcd), data_to_write, pdata, ILI9488_MAX_COMMAND_READ_LENGHT, HAL_MAX_DELAY);
    ili9488_set_cs();
}

void ili9488_wr(uint8_t *pdata, uint16_t size) {
    if (!(pdata && size)) {
        return; // null or empty data - return
    }

    // BFW-6328 Some displays possibly problematic with higher baudrate, reduce 40 -> 20 MHz
    SPIBaudRatePrescalerGuard _g(&SPI_HANDLE_FOR(lcd), SPI_BAUDRATEPRESCALER_4, reduce_display_baudrate);

    ili9488_clr_cs(); // CS = L
    ili9488_set_rs(); // RS = H
    ili9488_spi_wr_bytes(pdata, size); // write data bytes
    ili9488_set_cs(); // CS = H
}

void ili9488_rd(uint8_t *pdata, uint16_t size) {
    if (!(pdata && size)) {
        return; // null or empty data - return
    }
    // generate little pulse on displayCs, because ILI need change displayCs logic level
    displayCs.write(Pin::State::high);
    ili9488_delay_ms(1);
    displayCs.write(Pin::State::low);

    ili9488_clr_cs(); // CS = L
    ili9488_clr_rs(); // RS = L
    ili9488_spi_wr_byte(CMD_RAMRD); // write command byte
    ili9488_spi_wr_byte(0); // write dummy byte, datasheet p.122

    ili9488_spi_rd_bytes(pdata, size); // read data bytes
    ili9488_set_cs(); // CS = H

    // generate little pulse on displayCs, because ILI need change displayCs logic level
    displayCs.write(Pin::State::high);
    ili9488_delay_ms(1);
    displayCs.write(Pin::State::low);
}

bool ili9488_is_reset_required() {
    // REMOVEME: This is a bit of hack to reduce config_store locks.
    // This function is called in lcd::communication_check every 2 s.
    reduce_display_baudrate = config_store().reduce_display_baudrate.get();

    uint8_t pdata[ILI9488_MAX_COMMAND_READ_LENGHT] = { 0x00 };
    ili9488_cmd_rd(CMD_MADCTLRD, pdata);
    if ((pdata[1] != 0xE0 && pdata[1] != 0xF0 && pdata[1] != 0xF8)) {
        return true;
    }
    return false;
}

/*void ili9488_test_miso(void)
{
//	uint16_t data_out[8] = {CLR565_WHITE, CLR565_WHITE, CLR565_RED, CLR565_RED, CLR565_GREEN, CLR565_GREEN, CLR565_BLUE, CLR565_BLUE};
        uint8_t data_out[16] = {0xff, 0x00, 0xff, 0x00, 0xff, 0x00, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
        uint8_t data_in[32];
        memset(data_in, 0, sizeof(data_in));
        ili9488_clr_cs();
        ili9488_cmd_caset(0, ILI9488_COLS - 1);
        ili9488_cmd_raset(0, ILI9488_ROWS - 1);
        ili9488_cmd_ramwr((uint8_t*)data_out, 16);
        ili9488_set_cs();
        ili9488_clr_cs();
        ili9488_cmd_caset(0, ILI9488_COLS - 1);
        ili9488_cmd_raset(0, ILI9488_ROWS - 1);
        ili9488_cmd_ramrd(data_in, 32);
        ili9488_set_cs();
}*/

void ili9488_reset(void) {
    // some extra step based on new manufacturer recommendation
    if (Configuration::Instance().has_display_backlight_control()) {
        ili9488_set_rst();
        ili9488_delay_ms(1);
    }

    ili9488_clr_rst();
    ili9488_delay_ms(15);

#if HAS_TOUCH()
    touchscreen.reset_chip(ili9488_set_rst); // touch will restore reset
#else
    ili9488_set_rst();
#endif
}

void ili9488_power_down() {
    // activate reset pin of display, keep it enabled
    ili9488_clr_rst();
}

void ili9488_set_complete_lcd_reinit() {
    do_complete_lcd_reinit = true;
}

void ili9488_init(void) {
    displayCs.write(Pin::State::low);
    ili9488_task_handle = osThreadGetId();
    if (ili9488_flg & ILI9488_FLG_SAFE) {
        ili9488_flg &= ~ILI9488_FLG_DMA;
    } else {
        ili9488_flg = ili9488_default_flags();
    }

    if (!option::bootloader || do_complete_lcd_reinit) {
        ili9488_reset(); // 15ms reset pulse
        ili9488_delay_ms(120); // 120ms wait
        ili9488_run_startup_commands(buddy::hw::Configuration::Instance().has_display_backlight_control());
    } else {
        ili9488_run_bootloader_commands();
    }

#if HAS_TOUCH()
    if (touchscreen.is_enabled()) {
        touchscreen.upload_touchscreen_config();
    }
#endif

    if (Configuration::Instance().has_display_backlight_control()) {
        ili9488_brightness_enable();
        ili9488_configure_backlight_pwm();
    }

    ili9488_brightness_set(0xFF); // set backlight to maximum

    do_complete_lcd_reinit = false;
}

void ili9488_done(void) {
}

void ili9488_clear(uint32_t clr666) {
    assert(!ili9488_buff_borrowed && "Buffer lent to someone");

    int i;
    uint8_t *p_byte = (uint8_t *)ili9488_buff;

    for (i = 0; i < ILI9488_COLS * ILI9488_BUFF_ROWS - 1; i++) {
        *((uint32_t *)p_byte) = clr666;
        p_byte += 3; // increase the address by 3 because the color has 3 bytes
    }
    uint8_t *clr_ptr = (uint8_t *)&clr666;
    for (int j = 0; j < 3; j++) {
        *(p_byte + j) = *(clr_ptr + j);
    }

    ili9488_clr_cs();
    ili9488_cmd_caset(0, ILI9488_COLS - 1);
    ili9488_cmd_raset(0, ILI9488_ROWS - 1);
    ili9488_cmd_ramwr(0, 0);
    for (i = 0; i < ILI9488_ROWS / ILI9488_BUFF_ROWS; i++) {
        ili9488_wr(ili9488_buff, sizeof(ili9488_buff));
    }
    ili9488_set_cs();
    //	ili9488_test_miso();
}

void ili9488_set_pixel(uint16_t point_x, uint16_t point_y, uint32_t clr666) {
    ili9488_cmd_caset(point_x, point_x + 1);
    ili9488_cmd_raset(point_y, point_y + 1);
    ili9488_cmd_ramwr((uint8_t *)(&clr666), 3);
}

uint8_t *ili9488_get_block(uint16_t start_x, uint16_t start_y, uint16_t end_x, uint16_t end_y) {
    assert(!ili9488_buff_borrowed && "Buffer lent to someone");

    if (start_x >= ILI9488_COLS || start_y >= ILI9488_ROWS || end_x >= ILI9488_COLS || end_y >= ILI9488_ROWS) {
        return NULL;
    }
    ili9488_cmd_caset(start_x, end_x);
    ili9488_cmd_raset(start_y, end_y);
    ili9488_cmd_ramrd(ili9488_buff, ILI9488_COLS * 3 * ILI9488_BUFF_ROWS);
    return ili9488_buff;
}

uint32_t ili9488_get_pixel_colorFormat666(uint16_t point_x, uint16_t point_y) {
    enum { buff_sz = 5 };
    uint8_t buff[buff_sz];
    ili9488_cmd_caset(point_x, point_x + 1);
    ili9488_cmd_raset(point_y, point_y + 1);
    ili9488_cmd_ramrd(buff, buff_sz);
    uint32_t ret = ((buff[0] << 16) & 0xFC0000) + ((buff[1] << 8) & 0x00FC00) + (buff[2] & 0xFC);
    return ret; // directColor;
}

void ili9488_fill_rect_colorFormat666(uint16_t rect_x, uint16_t rect_y, uint16_t rect_w, uint16_t rect_h, uint32_t clr666) {
    // BFW-6328 Some displays possibly problematic with higher baudrate, reduce 40 -> 20 MHz
    SPIBaudRatePrescalerGuard _g(&SPI_HANDLE_FOR(lcd), SPI_BAUDRATEPRESCALER_4, reduce_display_baudrate);

    assert(!ili9488_buff_borrowed && "Buffer lent to someone");

    int i;
    uint32_t size = (uint32_t)rect_w * rect_h * 3;
    int n = size / sizeof(ili9488_buff);
    int s = size % sizeof(ili9488_buff);
    if (n) {
        ili9488_fill_ui24((uint8_t *)ili9488_buff, clr666, sizeof(ili9488_buff) / 3);
    } else {
        ili9488_fill_ui24((uint8_t *)ili9488_buff, clr666, size / 3);
    }
    ili9488_clr_cs();
    ili9488_cmd_caset(rect_x, rect_x + rect_w - 1);
    ili9488_cmd_raset(rect_y, rect_y + rect_h - 1);
    ili9488_cmd_ramwr(0, 0);
    for (i = 0; i < n; i++) {
        ili9488_wr(ili9488_buff, sizeof(ili9488_buff));
    }
    if (s) {
        ili9488_wr(ili9488_buff, s);
    }
    ili9488_set_cs();
}

void ili9488_draw_from_buffer(uint16_t x, uint16_t y, uint16_t w, uint16_t h) {
    /// @note This function is used when someone borrowed the buffer and filled it with data, don't check ili9488_buff_borrowed.
    /// @todo Cannot check that the buffer is borrowed because it is returned before calling this. Needs refactoring.

    ili9488_clr_cs();
    ili9488_cmd_caset(x, x + w - 1);
    ili9488_cmd_raset(y, y + h - 1);
    ili9488_cmd_ramwr(ili9488_buff, 3 * w * h);
    ili9488_set_cs();
}

void ili9488_draw_qoi_ex(point_ui16_t pt, AbstractByteReader &reader, Color back_color, uint8_t rop) {
    assert(!ili9488_buff_borrowed && "Buffer lent to someone");

    // BFW-6328 Some displays possibly problematic with higher baudrate, reduce 40 -> 20 MHz
    SPIBaudRatePrescalerGuard _g(&SPI_HANDLE_FOR(lcd), SPI_BAUDRATEPRESCALER_4, reduce_display_baudrate);

    // Current pixel position starts top-left where the image is placed
    point_i16_t pos = { static_cast<int16_t>(pt.x), static_cast<int16_t>(pt.y) };

    // Prepare input buffer
    std::span<uint8_t> i_buf(ili9488_buff, 512); ///< Input file buffer
    std::span<uint8_t> i_data; ///< Span of input data read from file

    // Prepare output buffer
    std::span<uint8_t> p_buf(ili9488_buff + i_buf.size(), std::size(ili9488_buff) - i_buf.size()); ///< Output pixel buffer
    auto o_data = p_buf.begin(); ///< Pointer to output pixel data in buffer

#if 0
    // Measure time it takes to draw QOI image
    #warning "Spamming the log"
    struct ImgMeasure {
        volatile uint32_t start_us;
        ImgMeasure() { start_us = ticks_us(); }
        ~ImgMeasure() { log_debug(GUI, "Img draw took %u us", ticks_us() - start_us); }
    } image_timing;
#endif /*0*/

    // Read header and image size to tweak drawn subrect
    auto header = reader.read(i_buf.subspan(0, qoi::Decoder::HEADER_SIZE));
    if (header.size() != qoi::Decoder::HEADER_SIZE) {
        return; // Header couldn't be read
    }
    Rect16 subrect = Rect16(pos, qoi::Decoder::get_image_size(std::span<uint8_t, qoi::Decoder::HEADER_SIZE>(i_buf)));
    subrect.Intersection(Rect16(0, 0, ILI9488_COLS, ILI9488_ROWS)); // Clip drawn subrect to display size

    // Prepare output
    // Set write rectangle
    ili9488_cmd_caset(subrect.Left(), subrect.Right());
    ili9488_cmd_raset(subrect.Top(), subrect.Bottom());
    // Start write of data
    ili9488_cmd_ramwr(0, 0);

    qoi::Decoder qoi_decoder; ///< QOI decoding statemachine
    while (1) {
        // Read more data from file
        i_data = reader.read(i_buf);
        if (i_data.empty()) {
            break; // Picture ends
        }

        // Process input data
        for (auto i_byte : i_data) {

            // Push byte to decoder
            qoi_decoder.push_byte((uint8_t)i_byte);

            // Pull pixels from decoder
            while (qoi_decoder.has_pixel()) {
                qoi::Pixel pixel = qoi_decoder.pull_pixel();

                // Keep track of pixel position
                auto orig_pos = pos;
                pos.x++;
                if (pos.x > subrect.Right()) {
                    pos.x = subrect.Left();
                    pos.y++;
                }

                // Skip pixels outside of subrect
                if (subrect.Contain(orig_pos) == false) {
                    if (orig_pos.y > subrect.Bottom()) { // Picture ends
                        // Write remaining pixels to display and close SPI transaction
                        ili9488_wr(p_buf.data(), o_data - p_buf.begin());
                        ili9488_set_cs();
                        return;
                    }
                    continue;
                }

                // Transform pixel data
                pixel = qoi::transform::apply_rop(pixel, rop);

                const Color c = Color::mix(back_color, Color::from_rgb(pixel.r, pixel.g, pixel.b), pixel.a);

                // Store to output buffer
                *o_data++ = c.b;
                *o_data++ = c.g;
                *o_data++ = c.r;

                // Another 3 bytes wouldn't fit, write to display
                if (p_buf.end() - o_data < 3) {
                    ili9488_wr(p_buf.data(), o_data - p_buf.begin());
                    o_data = p_buf.begin();
                }
            }
        }
    }

    // Write remaining pixels to display and close SPI transaction
    ili9488_wr(p_buf.data(), o_data - p_buf.begin());
    ili9488_set_cs();
}

//! @brief enable safe mode (direct acces + safe delay)
void ili9488_enable_safe_mode(void) {
    ili9488_flg |= ILI9488_FLG_SAFE;
}

void ili9488_spi_tx_complete(void) {
    osSignalSet(ili9488_task_handle, ILI9488_SIG_SPI_TX);
}

void ili9488_spi_rx_complete(void) {
    osSignalSet(ili9488_task_handle, ILI9488_SIG_SPI_RX);
}

void ili9488_cmd_nop() {
    ili9488_cmd(CMD_NOP, 0, 0);
}
