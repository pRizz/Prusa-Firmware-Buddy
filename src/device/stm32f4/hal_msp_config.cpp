#include "hal_msp_config.hpp"

#include <buddy/main.h>
#include "hwio_pindef.h"
#include "printers.h"
#include <buddy/priorities_config.h>
#include <device/board.h>
#include <option/has_burst_stepping.h>

namespace buddy::hw::msp_config {
namespace {

    template <typename T, size_t Size>
    constexpr size_t count(const T (&)[Size]) {
        return Size;
    }

#define PERIPHERAL(instance_, clocks_, gpios_, dmas_, irqs_, uart_actions_, deinit_dma_, disable_irq_) \
    { instance_, clocks_, count(clocks_), gpios_, count(gpios_), dmas_, count(dmas_), irqs_, count(irqs_), uart_actions_, deinit_dma_, disable_irq_ }

#define PERIPHERAL_NO_DMA(instance_, clocks_, gpios_, irqs_, uart_actions_, disable_irq_) \
    { instance_, clocks_, count(clocks_), gpios_, count(gpios_), nullptr, 0, irqs_, count(irqs_), uart_actions_, DeinitDma::none, disable_irq_ }

#define PERIPHERAL_NO_IRQ(instance_, clocks_, gpios_, dmas_, uart_actions_, deinit_dma_) \
    { instance_, clocks_, count(clocks_), gpios_, count(gpios_), dmas_, count(dmas_), nullptr, 0, uart_actions_, deinit_dma_, false }

#define PERIPHERAL_MINIMAL(instance_, clocks_, gpios_) \
    { instance_, clocks_, count(clocks_), gpios_, count(gpios_), nullptr, 0, nullptr, 0, uart_none, DeinitDma::none, false }

#if BOARD_IS_BUDDY()
    constexpr Clock spi2_clocks[] = { Clock::spi2, Clock::gpio_c, Clock::gpio_b };
    const Gpio spi2_gpios[] = {
        { GPIOC, GPIO_PIN_2 | GPIO_PIN_3, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF5_SPI2 },
        { GPIOB, GPIO_PIN_10, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF5_SPI2 },
    };
    const Dma spi2_dmas[] = {
        { DmaSlot::spi2_tx, DMA1_Stream4, DMA_CHANNEL_0, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_MEDIUM, DmaLink::tx },
        { DmaSlot::spi2_rx, DMA1_Stream3, DMA_CHANNEL_0, DMA_PERIPH_TO_MEMORY, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::rx },
    };

    constexpr Clock spi3_clocks[] = { Clock::spi3, Clock::gpio_c };
    const Gpio spi3_gpios[] = {
        { GPIOC, FLASH_SCK_Pin | FLASH_MISO_Pin | FLASH_MOSI_Pin, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF6_SPI3 },
    };
    const Dma spi3_dmas[] = {
        { DmaSlot::spi3_tx, DMA1_Stream7, DMA_CHANNEL_0, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_MEDIUM, DmaLink::tx },
        { DmaSlot::spi3_rx, DMA1_Stream0, DMA_CHANNEL_0, DMA_PERIPH_TO_MEMORY, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::rx },
    };

    const Peripheral spi_configs[] = {
        PERIPHERAL_NO_IRQ(SPI2, spi2_clocks, spi2_gpios, spi2_dmas, uart_none, DeinitDma::tx_rx),
        PERIPHERAL_NO_IRQ(SPI3, spi3_clocks, spi3_gpios, spi3_dmas, uart_none, DeinitDma::none),
    };

    constexpr Clock usart1_clocks[] = { Clock::usart1, Clock::gpio_b };
    const Gpio usart1_gpios[] = {
        { GPIOB, TX1_Pin | RX1_Pin, GPIO_MODE_AF_PP, GPIO_PULLUP, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF7_USART1 },
    };
    const Dma usart1_dmas[] = {
        { DmaSlot::usart1_rx, DMA2_Stream2, DMA_CHANNEL_4, DMA_PERIPH_TO_MEMORY, DMA_CIRCULAR, DMA_PRIORITY_LOW, DmaLink::rx },
    };

    constexpr Clock usart2_clocks[] = { Clock::usart2, Clock::gpio_d };
    const Gpio usart2_gpios[] = {
        { GPIOD, GPIO_PIN_5, GPIO_PIN_5 | GPIO_PIN_6, GPIO_MODE_AF_OD, GPIO_PULLUP, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF7_USART2 },
    };
    const Dma usart2_dmas[] = {
        { DmaSlot::usart2_rx, DMA1_Stream5, DMA_CHANNEL_4, DMA_PERIPH_TO_MEMORY, DMA_CIRCULAR, DMA_PRIORITY_LOW, DmaLink::rx },
    };
    const Irq usart2_irqs[] = { { USART2_IRQn, ISR_PRIORITY_DEFAULT, 0 } };

    constexpr Clock usart6_clocks[] = { Clock::usart6, Clock::gpio_c };
    const Gpio usart6_gpios[] = {
        { GPIOC, ESP_TX_Pin | ESP_RX_Pin, GPIO_MODE_AF_PP, GPIO_PULLUP, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF8_USART6 },
    };
    const Dma usart6_dmas[] = {
        { DmaSlot::usart6_rx, DMA2_Stream1, DMA_CHANNEL_5, DMA_PERIPH_TO_MEMORY, DMA_CIRCULAR, DMA_PRIORITY_LOW, DmaLink::rx },
        { DmaSlot::usart6_tx, DMA2_Stream6, DMA_CHANNEL_5, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::tx },
    };
    const Irq usart6_irqs[] = { { USART6_IRQn, ISR_PRIORITY_DEFAULT, 0 } };

    const Peripheral uart_configs[] = {
        PERIPHERAL_NO_IRQ(USART1, usart1_clocks, usart1_gpios, usart1_dmas, uart_none, DeinitDma::rx),
    PERIPHERAL(USART2, usart2_clocks, usart2_gpios, usart2_dmas, usart2_irqs, uart_enable_idle | uart_enable_tc | uart_clear_tc, DeinitDma::rx, false),
        PERIPHERAL(USART6, usart6_clocks, usart6_gpios, usart6_dmas, usart6_irqs, uart_enable_idle | uart_enable_tc | uart_clear_tc, DeinitDma::rx, true),
    };
#elif BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    constexpr Clock spi2_clocks[] = { Clock::spi2, Clock::gpio_c, Clock::gpio_b };
    const Gpio spi2_gpios[] = {
        { GPIOC, GPIO_PIN_2, GPIO_MODE_AF_PP,
    #if BOARD_IS_XBUDDY()
            GPIO_PULLDOWN, GPIO_SPEED_FREQ_MEDIUM,
    #else
            GPIO_NOPULL, GPIO_SPEED_FREQ_VERY_HIGH,
    #endif
            GPIO_AF5_SPI2 },
        { GPIOC, GPIO_PIN_3, GPIO_MODE_AF_PP, GPIO_NOPULL,
    #if BOARD_IS_XBUDDY()
            GPIO_SPEED_FREQ_MEDIUM,
    #else
            GPIO_SPEED_FREQ_VERY_HIGH,
    #endif
            GPIO_AF5_SPI2 },
        { GPIOB, GPIO_PIN_10, GPIO_MODE_AF_PP,
    #if spi_accelerometer == 2
            GPIO_PULLUP,
    #else
            GPIO_NOPULL,
    #endif
    #if BOARD_IS_XBUDDY()
            GPIO_SPEED_FREQ_MEDIUM,
    #else
            GPIO_SPEED_FREQ_VERY_HIGH,
    #endif
            GPIO_AF5_SPI2 },
    };
    #if BOARD_IS_XBUDDY()
    const Dma spi2_dmas[] = {
        { DmaSlot::spi2_rx, DMA1_Stream3, DMA_CHANNEL_0, DMA_PERIPH_TO_MEMORY, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::rx },
        { DmaSlot::spi2_tx, DMA1_Stream4, DMA_CHANNEL_0, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_MEDIUM, DmaLink::tx },
    };
    #endif

    constexpr Clock spi3_clocks[] = { Clock::spi3, Clock::gpio_c };
    const Gpio spi3_gpios[] = {
        { GPIOC, GPIO_PIN_10 | GPIO_PIN_11 | GPIO_PIN_12, GPIO_MODE_AF_PP, GPIO_PULLDOWN, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF6_SPI3 },
    };
    const Dma spi3_dmas[] = {
        { DmaSlot::spi3_rx, DMA1_Stream0, DMA_CHANNEL_0, DMA_PERIPH_TO_MEMORY, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::rx },
        { DmaSlot::spi3_tx, DMA1_Stream5, DMA_CHANNEL_0, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::tx },
    };
    const Irq spi3_irqs[] = { { SPI3_IRQn, ISR_PRIORITY_DEFAULT, 0 } };

    constexpr Clock spi4_clocks[] = { Clock::spi4, Clock::gpio_e };
    const Gpio spi4_gpios[] = {
        { GPIOE, GPIO_PIN_2 | GPIO_PIN_5 | GPIO_PIN_6, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF5_SPI4 },
    };
    #if HAS_BURST_STEPPING()
    const Irq spi4_irqs[] = { { SPI4_IRQn, ISR_PRIORITY_DEFAULT, 0 } };
    #else
    const Dma spi4_dmas[] = {
        { DmaSlot::spi4_tx, DMA2_Stream1, DMA_CHANNEL_4, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::tx },
    };
    #endif

    constexpr Clock spi5_clocks[] = { Clock::spi5, Clock::gpio_f };
    const Gpio spi5_gpios[] = {
        { GPIOF, GPIO_PIN_7 | GPIO_PIN_8 | GPIO_PIN_9, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF5_SPI5 },
    };
    const Dma spi5_dmas[] = {
        { DmaSlot::spi5_tx, DMA2_Stream6, DMA_CHANNEL_7, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_MEDIUM, DmaLink::tx },
        { DmaSlot::spi5_rx, DMA2_Stream3, DMA_CHANNEL_2, DMA_PERIPH_TO_MEMORY, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::rx },
    };

    constexpr Clock spi6_clocks[] = { Clock::spi6, Clock::gpio_g };
    const Gpio spi6_gpios[] = {
        { GPIOG, GPIO_PIN_12 | GPIO_PIN_13 | GPIO_PIN_14, GPIO_MODE_AF_PP, GPIO_PULLDOWN, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF5_SPI6 },
    };
    const Dma spi6_dmas[] = {
        { DmaSlot::spi6_tx, DMA2_Stream5, DMA_CHANNEL_1, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::tx },
    };

    const Peripheral spi_configs[] = {
    #if BOARD_IS_XBUDDY()
        PERIPHERAL_NO_IRQ(SPI2, spi2_clocks, spi2_gpios, spi2_dmas, uart_none, DeinitDma::none),
    #else
        PERIPHERAL_MINIMAL(SPI2, spi2_clocks, spi2_gpios),
    #endif
        PERIPHERAL(SPI3, spi3_clocks, spi3_gpios, spi3_dmas, spi3_irqs, uart_none, DeinitDma::rx_tx, true),
    #if HAS_BURST_STEPPING()
        PERIPHERAL_NO_DMA(SPI4, spi4_clocks, spi4_gpios, spi4_irqs, uart_none, false),
    #else
        PERIPHERAL_NO_IRQ(SPI4, spi4_clocks, spi4_gpios, spi4_dmas, uart_none, DeinitDma::none),
    #endif
        PERIPHERAL_NO_IRQ(SPI5, spi5_clocks, spi5_gpios, spi5_dmas, uart_none, DeinitDma::none),
        PERIPHERAL_NO_IRQ(SPI6, spi6_clocks, spi6_gpios, spi6_dmas, uart_none, DeinitDma::tx_rx),
    };

    constexpr Clock uart8_clocks[] = { Clock::uart8, Clock::gpio_e };
    const Gpio uart8_gpios[] = {
        { GPIOE, GPIO_PIN_0 | GPIO_PIN_1, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF8_UART8 },
    };
    const Dma uart8_dmas[] = {
        { DmaSlot::uart8_rx, DMA1_Stream6, DMA_CHANNEL_5, DMA_PERIPH_TO_MEMORY, DMA_CIRCULAR, DMA_PRIORITY_LOW, DmaLink::rx },
        { DmaSlot::uart8_tx, DMA1_Stream0, DMA_CHANNEL_5, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::tx },
    };
    const Irq uart8_irqs[] = { { UART8_IRQn, ISR_PRIORITY_DEFAULT, 0 } };

    constexpr Clock usart6_clocks[] = { Clock::usart6, Clock::gpio_c };
    const Gpio usart6_gpios[] = {
        { GPIOC, MMU_TX_Pin | MMU_RX_Pin, GPIO_MODE_AF_PP, GPIO_PULLUP, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF8_USART6 },
    };
    const Dma usart6_dmas[] = {
        { DmaSlot::usart6_rx, DMA2_Stream2, DMA_CHANNEL_5, DMA_PERIPH_TO_MEMORY, DMA_CIRCULAR, DMA_PRIORITY_LOW, DmaLink::rx },
        { DmaSlot::usart6_tx, DMA2_Stream7, DMA_CHANNEL_5, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::tx },
    };
    #if PRINTER_IS_PRUSA_iX() || PRINTER_IS_PRUSA_COREONE()
    const Irq usart6_irqs[] = { { USART6_IRQn, ISR_PRIORITY_PUPPIES_USART, 0 } };
    #else
    const Irq usart6_irqs[] = { { USART6_IRQn, ISR_PRIORITY_DEFAULT, 0 } };
    #endif

    #if BOARD_IS_XLBUDDY()
    constexpr Clock usart3_clocks[] = { Clock::usart3, Clock::gpio_d };
    const Gpio usart3_gpios[] = {
        { GPIOD, GPIO_PIN_8, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF7_USART3 },
        { GPIOD, GPIO_PIN_9, GPIO_MODE_AF_PP, GPIO_PULLUP, GPIO_SPEED_FREQ_VERY_HIGH, GPIO_AF7_USART3 },
    };
    const Dma usart3_dmas[] = {
        { DmaSlot::usart3_rx, DMA1_Stream1, DMA_CHANNEL_4, DMA_PERIPH_TO_MEMORY, DMA_CIRCULAR, DMA_PRIORITY_LOW, DmaLink::rx },
        { DmaSlot::usart3_tx, DMA1_Stream3, DMA_CHANNEL_4, DMA_MEMORY_TO_PERIPH, DMA_NORMAL, DMA_PRIORITY_LOW, DmaLink::tx },
    };
    const Irq usart3_irqs[] = { { USART3_IRQn, ISR_PRIORITY_PUPPIES_USART, 0 } };
    #endif

    const Peripheral uart_configs[] = {
    #if BOARD_IS_XLBUDDY()
        PERIPHERAL(USART3, usart3_clocks, usart3_gpios, usart3_dmas, usart3_irqs, uart_enable_idle | uart_clear_tc, DeinitDma::rx_tx, true),
    #endif
        PERIPHERAL(UART8, uart8_clocks, uart8_gpios, uart8_dmas, uart8_irqs, uart_enable_idle | uart_enable_tc | uart_clear_tc, DeinitDma::rx_tx, false),
        PERIPHERAL(USART6, usart6_clocks, usart6_gpios, usart6_dmas, usart6_irqs, uart_enable_idle | uart_clear_tc, DeinitDma::rx, true),
    };
#else
    #error "Unknown board"
#endif

    template <size_t Size>
    const Peripheral *find(const Peripheral (&configs)[Size], const void *instance) {
        for (const auto &config : configs) {
            if (config.instance == instance) {
                return &config;
            }
        }
        return nullptr;
    }

} // namespace

const Peripheral *spi(const void *instance) {
    return find(spi_configs, instance);
}

const Peripheral *uart(const void *instance) {
    return find(uart_configs, instance);
}

} // namespace buddy::hw::msp_config
