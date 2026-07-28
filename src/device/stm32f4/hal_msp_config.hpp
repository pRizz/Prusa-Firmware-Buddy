#pragma once

#include <cstddef>
#include <cstdint>
#include <device/hal.h>

namespace buddy::hw::msp_config {

enum class Clock : uint8_t {
    gpio_b,
    gpio_c,
    gpio_d,
    gpio_e,
    gpio_f,
    gpio_g,
    spi2,
    spi3,
    spi4,
    spi5,
    spi6,
    usart1,
    usart2,
    usart3,
    usart6,
    uart8,
};

enum class DmaSlot : uint8_t {
    spi2_rx,
    spi2_tx,
    spi3_rx,
    spi3_tx,
    spi4_tx,
    spi5_rx,
    spi5_tx,
    spi6_tx,
    usart1_rx,
    usart2_rx,
    usart3_rx,
    usart3_tx,
    usart6_rx,
    usart6_tx,
    uart8_rx,
    uart8_tx,
};

enum class DmaLink : uint8_t {
    rx,
    tx,
};

struct Gpio {
    GPIO_TypeDef *port;
    uint32_t pins;
    uint32_t deinit_pins;
    uint32_t mode;
    uint32_t pull;
    uint32_t speed;
    uint32_t alternate;

    constexpr Gpio(GPIO_TypeDef *port, uint32_t pins, uint32_t mode, uint32_t pull, uint32_t speed, uint32_t alternate)
        : port(port)
        , pins(pins)
        , deinit_pins(pins)
        , mode(mode)
        , pull(pull)
        , speed(speed)
        , alternate(alternate) {
    }

    constexpr Gpio(GPIO_TypeDef *port, uint32_t pins, uint32_t deinit_pins, uint32_t mode, uint32_t pull, uint32_t speed, uint32_t alternate)
        : port(port)
        , pins(pins)
        , deinit_pins(deinit_pins)
        , mode(mode)
        , pull(pull)
        , speed(speed)
        , alternate(alternate) {
    }
};

struct Dma {
    DmaSlot slot;
    DMA_Stream_TypeDef *stream;
    uint32_t channel;
    uint32_t direction;
    uint32_t mode;
    uint32_t priority;
    DmaLink link;
};

struct Irq {
    IRQn_Type irq;
    uint32_t priority;
    uint32_t subpriority;
};

enum UartAction : uint8_t {
    uart_none = 0,
    uart_enable_idle = 1 << 0,
    uart_enable_tc = 1 << 1,
    uart_clear_tc = 1 << 2,
};

enum class DeinitDma : uint8_t {
    none,
    rx,
    rx_tx,
    tx_rx,
};

struct Peripheral {
    const void *instance;
    const Clock *clocks;
    size_t clock_count;
    const Gpio *gpios;
    size_t gpio_count;
    const Dma *dmas;
    size_t dma_count;
    const Irq *irqs;
    size_t irq_count;
    uint8_t uart_actions;
    DeinitDma deinit_dma;
    bool disable_irq;
};

const Peripheral *spi(const void *instance);
const Peripheral *uart(const void *instance);

} // namespace buddy::hw::msp_config
