#include <buddy/main.h>
#include <buddy/priorities_config.h>
#include <device/board.h>
#include <device/peripherals.h>
#include <option/has_burst_stepping.h>
#include "hal_msp_config.hpp"
#include "printers.h"

void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim);

#if BOARD_IS_BUDDY()
static DMA_HandleTypeDef hdma_spi2_rx, hdma_spi2_tx, hdma_spi3_rx, hdma_spi3_tx;
static DMA_HandleTypeDef hdma_usart1_rx, hdma_usart2_rx, hdma_usart6_rx, hdma_usart6_tx;
static DMA_HandleTypeDef hdma_adc1, hdma_tim8;
#elif BOARD_IS_XBUDDY()
static DMA_HandleTypeDef hdma_spi2_rx, hdma_spi2_tx, hdma_spi3_rx, hdma_spi3_tx;
static DMA_HandleTypeDef hdma_spi4_tx, hdma_spi5_tx, hdma_spi5_rx, hdma_spi6_tx;
static DMA_HandleTypeDef hdma_usart6_rx, hdma_usart6_tx, hdma_uart8_rx, hdma_uart8_tx;
static DMA_HandleTypeDef hdma_adc1, hdma_adc3, hdma_tim8;
#elif BOARD_IS_XLBUDDY()
static DMA_HandleTypeDef hdma_spi3_rx, hdma_spi3_tx;
    #if !HAS_BURST_STEPPING()
static DMA_HandleTypeDef hdma_spi4_tx;
    #endif
static DMA_HandleTypeDef hdma_spi5_tx, hdma_spi5_rx, hdma_spi6_tx;
static DMA_HandleTypeDef hdma_usart3_rx, hdma_usart3_tx, hdma_usart6_rx, hdma_usart6_tx;
static DMA_HandleTypeDef hdma_uart8_rx, hdma_uart8_tx, hdma_adc1, hdma_adc3, hdma_tim8;
#else
    #error "Unknown board"
#endif

namespace {

using namespace buddy::hw::msp_config;

DMA_HandleTypeDef &dma_handle(DmaSlot slot) {
    switch (slot) {
#if BOARD_IS_BUDDY() || BOARD_IS_XBUDDY()
    case DmaSlot::spi2_rx:
        return hdma_spi2_rx;
    case DmaSlot::spi2_tx:
        return hdma_spi2_tx;
#endif
    case DmaSlot::spi3_rx:
        return hdma_spi3_rx;
    case DmaSlot::spi3_tx:
        return hdma_spi3_tx;
#if (BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()) && !HAS_BURST_STEPPING()
    case DmaSlot::spi4_tx:
        return hdma_spi4_tx;
#endif
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    case DmaSlot::spi5_rx:
        return hdma_spi5_rx;
    case DmaSlot::spi5_tx:
        return hdma_spi5_tx;
    case DmaSlot::spi6_tx:
        return hdma_spi6_tx;
    case DmaSlot::uart8_rx:
        return hdma_uart8_rx;
    case DmaSlot::uart8_tx:
        return hdma_uart8_tx;
#endif
#if BOARD_IS_BUDDY()
    case DmaSlot::usart1_rx:
        return hdma_usart1_rx;
    case DmaSlot::usart2_rx:
        return hdma_usart2_rx;
#endif
#if BOARD_IS_XLBUDDY()
    case DmaSlot::usart3_rx:
        return hdma_usart3_rx;
    case DmaSlot::usart3_tx:
        return hdma_usart3_tx;
#endif
    case DmaSlot::usart6_rx:
        return hdma_usart6_rx;
    case DmaSlot::usart6_tx:
        return hdma_usart6_tx;
    default:
        Error_Handler();
        return hdma_adc1;
    }
}

void enable_clock(Clock clock) {
    switch (clock) {
    case Clock::gpio_b:
        __HAL_RCC_GPIOB_CLK_ENABLE();
        break;
    case Clock::gpio_c:
        __HAL_RCC_GPIOC_CLK_ENABLE();
        break;
    case Clock::gpio_d:
        __HAL_RCC_GPIOD_CLK_ENABLE();
        break;
    case Clock::gpio_e:
        __HAL_RCC_GPIOE_CLK_ENABLE();
        break;
    case Clock::gpio_f:
        __HAL_RCC_GPIOF_CLK_ENABLE();
        break;
    case Clock::gpio_g:
        __HAL_RCC_GPIOG_CLK_ENABLE();
        break;
    case Clock::spi2:
        __HAL_RCC_SPI2_CLK_ENABLE();
        break;
    case Clock::spi3:
        __HAL_RCC_SPI3_CLK_ENABLE();
        break;
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    case Clock::spi4:
        __HAL_RCC_SPI4_CLK_ENABLE();
        break;
    case Clock::spi5:
        __HAL_RCC_SPI5_CLK_ENABLE();
        break;
    case Clock::spi6:
        __HAL_RCC_SPI6_CLK_ENABLE();
        break;
#endif
    case Clock::usart1:
        __HAL_RCC_USART1_CLK_ENABLE();
        break;
    case Clock::usart2:
        __HAL_RCC_USART2_CLK_ENABLE();
        break;
    case Clock::usart3:
        __HAL_RCC_USART3_CLK_ENABLE();
        break;
    case Clock::usart6:
        __HAL_RCC_USART6_CLK_ENABLE();
        break;
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    case Clock::uart8:
        __HAL_RCC_UART8_CLK_ENABLE();
        break;
#endif
    default:
        Error_Handler();
        break;
    }
}

void disable_clock(Clock clock) {
    switch (clock) {
    case Clock::spi2:
        __HAL_RCC_SPI2_CLK_DISABLE();
        break;
    case Clock::spi3:
        __HAL_RCC_SPI3_CLK_DISABLE();
        break;
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    case Clock::spi4:
        __HAL_RCC_SPI4_CLK_DISABLE();
        break;
    case Clock::spi5:
        __HAL_RCC_SPI5_CLK_DISABLE();
        break;
    case Clock::spi6:
        __HAL_RCC_SPI6_CLK_DISABLE();
        break;
#endif
    case Clock::usart1:
        __HAL_RCC_USART1_CLK_DISABLE();
        break;
    case Clock::usart2:
        __HAL_RCC_USART2_CLK_DISABLE();
        break;
    case Clock::usart3:
        __HAL_RCC_USART3_CLK_DISABLE();
        break;
    case Clock::usart6:
        __HAL_RCC_USART6_CLK_DISABLE();
        break;
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    case Clock::uart8:
        __HAL_RCC_UART8_CLK_DISABLE();
        break;
#endif
    default:
        Error_Handler();
        break;
    }
}

void init_gpio(const Gpio &config) {
    GPIO_InitTypeDef gpio { config.pins, config.mode, config.pull, config.speed, config.alternate };
    HAL_GPIO_Init(config.port, &gpio);
}

template <typename Handle>
void init_peripheral(Handle *handle, const Peripheral &config) {
    for (size_t index = 0; index < config.clock_count; ++index) {
        enable_clock(config.clocks[index]);
    }
    for (size_t index = 0; index < config.gpio_count; ++index) {
        init_gpio(config.gpios[index]);
    }
    for (size_t index = 0; index < config.dma_count; ++index) {
        const auto &source = config.dmas[index];
        auto &dma = dma_handle(source.slot);
        dma.Instance = source.stream;
        dma.Init.Channel = source.channel;
        dma.Init.Direction = source.direction;
        dma.Init.PeriphInc = DMA_PINC_DISABLE;
        dma.Init.MemInc = DMA_MINC_ENABLE;
        dma.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
        dma.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
        dma.Init.Mode = source.mode;
        dma.Init.Priority = source.priority;
        dma.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
        if (HAL_DMA_Init(&dma) != HAL_OK) {
            Error_Handler();
        }
        if (source.link == DmaLink::rx) {
            __HAL_LINKDMA(handle, hdmarx, dma);
        } else {
            __HAL_LINKDMA(handle, hdmatx, dma);
        }
    }
}

void enable_irqs(const Peripheral &config) {
    for (size_t index = 0; index < config.irq_count; ++index) {
        const auto &irq = config.irqs[index];
        HAL_NVIC_SetPriority(irq.irq, irq.priority, irq.subpriority);
        HAL_NVIC_EnableIRQ(irq.irq);
    }
}

template <typename Handle>
void deinit_peripheral(Handle *handle, const Peripheral &config) {
    disable_clock(config.clocks[0]);
    for (size_t index = 0; index < config.gpio_count; ++index) {
        HAL_GPIO_DeInit(config.gpios[index].port, config.gpios[index].deinit_pins);
    }
    if (config.deinit_dma == DeinitDma::rx || config.deinit_dma == DeinitDma::rx_tx) {
        HAL_DMA_DeInit(handle->hdmarx);
    }
    if (config.deinit_dma == DeinitDma::tx_rx) {
        HAL_DMA_DeInit(handle->hdmatx);
        HAL_DMA_DeInit(handle->hdmarx);
    } else if (config.deinit_dma == DeinitDma::rx_tx) {
        HAL_DMA_DeInit(handle->hdmatx);
    }
    if (config.disable_irq && config.irq_count != 0) {
        HAL_NVIC_DisableIRQ(config.irqs[0].irq);
    }
}

} // namespace

void HAL_MspInit() {
    __HAL_RCC_SYSCFG_CLK_ENABLE();
    __HAL_RCC_PWR_CLK_ENABLE();
    HAL_EnableCompensationCell();
    HAL_NVIC_SetPriority(PendSV_IRQn, ISR_PRIORITY_PENDSV, 0);
}

void analog_gpio_init(GPIO_TypeDef *port, uint32_t pins) {
    GPIO_InitTypeDef gpio { pins, GPIO_MODE_ANALOG, GPIO_NOPULL, 0, 0 };
    HAL_GPIO_Init(port, &gpio);
}

void adc_dma_init(DMA_HandleTypeDef *dma, DMA_Stream_TypeDef *stream, uint32_t channel) {
    dma->Instance = stream;
    dma->Init.Channel = channel;
    dma->Init.Direction = DMA_PERIPH_TO_MEMORY;
    dma->Init.PeriphInc = DMA_PINC_DISABLE;
    dma->Init.MemInc = DMA_MINC_ENABLE;
    dma->Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    dma->Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
    dma->Init.Mode = DMA_CIRCULAR;
    dma->Init.Priority = DMA_PRIORITY_LOW;
    dma->Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    if (HAL_DMA_Init(dma) != HAL_OK) {
        Error_Handler();
    }
}

void HAL_ADC_MspInit(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) {
        __HAL_RCC_ADC1_CLK_ENABLE();
        __HAL_RCC_GPIOC_CLK_ENABLE();
        __HAL_RCC_GPIOA_CLK_ENABLE();
#if BOARD_IS_XBUDDY() && PRINTER_IS_PRUSA_MK3_5()
        analog_gpio_init(GPIOA, THERM_1_Pin | HEATER_VOLTAGE_Pin | BED_VOLTAGE_Pin);
        analog_gpio_init(THERM_0_GPIO_Port, THERM_0_Pin);
#elif BOARD_IS_XBUDDY()
        analog_gpio_init(GPIOA, THERM_1_Pin | THERM_HEATBREAK_Pin | HEATER_VOLTAGE_Pin | BED_VOLTAGE_Pin);
        analog_gpio_init(THERM_0_GPIO_Port, THERM_0_Pin);
#elif BOARD_IS_BUDDY()
        analog_gpio_init(GPIOA, BED_MON_Pin | THERM_1_Pin | THERM_2_Pin | THERM_PINDA_Pin);
        analog_gpio_init(THERM_0_GPIO_Port, THERM_0_Pin);
#elif BOARD_IS_XLBUDDY()
        analog_gpio_init(GPIOA, GPIO_PIN_4 | GPIO_PIN_5);
        analog_gpio_init(GPIOB, GPIO_PIN_0);
#endif
        adc_dma_init(&hdma_adc1, DMA2_Stream4, DMA_CHANNEL_0);
        __HAL_LINKDMA(hadc, DMA_Handle, hdma_adc1);
    }
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    if (hadc->Instance == ADC3) {
        __HAL_RCC_ADC3_CLK_ENABLE();
        __HAL_RCC_GPIOF_CLK_ENABLE();
    #if BOARD_IS_XBUDDY()
        analog_gpio_init(GPIOF, HEATER_CURRENT_Pin | INPUT_CURRENT_Pin | THERM3_Pin | MMU_CURRENT_Pin | THERM_2_Pin);
    #else
        analog_gpio_init(GPIOF, GPIO_PIN_10);
        analog_gpio_init(GPIOC, GPIO_PIN_0);
        analog_gpio_init(GPIOF, GPIO_PIN_6);
    #endif
        adc_dma_init(&hdma_adc3, DMA2_Stream0, DMA_CHANNEL_2);
        __HAL_LINKDMA(hadc, DMA_Handle, hdma_adc3);
    }
#endif
}

void HAL_ADC_MspDeInit(ADC_HandleTypeDef *hadc) {
    if (hadc->Instance == ADC1) {
        __HAL_RCC_ADC1_CLK_DISABLE();
        HAL_GPIO_DeInit(THERM_0_GPIO_Port, THERM_0_Pin);
        HAL_GPIO_DeInit(GPIOA, BED_MON_Pin | THERM_1_Pin | THERM_2_Pin
#if BOARD_IS_BUDDY()
                | THERM_PINDA_Pin
#endif
#if BOARD_IS_XBUDDY() && !PRINTER_IS_PRUSA_MK3_5()
                | THERM_HEATBREAK_Pin
#endif
        );
        HAL_DMA_DeInit(hadc->DMA_Handle);
    }
#if BOARD_IS_BUDDY() || BOARD_IS_XBUDDY()
    if (hadc->Instance == ADC2) {
        __HAL_RCC_ADC2_CLK_DISABLE();
        HAL_GPIO_DeInit(GPIOA, HW_IDENTIFY_Pin | THERM_2_Pin);
        HAL_DMA_DeInit(hadc->DMA_Handle);
    }
#endif
}

void HAL_I2C_MspInit(I2C_HandleTypeDef *hi2c) {
#if HAS_I2CN(1)
    if (hi2c->Instance == I2C1) {
        hw_i2c1_pins_init();
    }
#endif
#if HAS_I2CN(2)
    if (hi2c->Instance == I2C2) {
        hw_i2c2_pins_init();
    }
#endif
#if HAS_I2CN(3)
    if (hi2c->Instance == I2C3) {
        hw_i2c3_pins_init();
    }
#endif
}

void HAL_I2C_MspDeInit(I2C_HandleTypeDef *hi2c) {
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    if (hi2c->Instance == I2C2) {
        __HAL_RCC_I2C2_CLK_DISABLE();
        HAL_GPIO_DeInit(GPIOF, GPIO_PIN_0);
        HAL_GPIO_DeInit(GPIOF, GPIO_PIN_1);
    }
    #if HAS_I2CN(3)
    else if (hi2c->Instance == I2C3) {
        __HAL_RCC_I2C3_CLK_DISABLE();
        HAL_GPIO_DeInit(GPIOC, GPIO_PIN_9);
        HAL_GPIO_DeInit(GPIOA, GPIO_PIN_8);
    }
    #endif
#endif
#if BOARD_IS_BUDDY() || BOARD_IS_XLBUDDY()
    if (hi2c->Instance == I2C1) {
        __HAL_RCC_I2C1_CLK_DISABLE();
        HAL_GPIO_DeInit(GPIOB, GPIO_PIN_8 | GPIO_PIN_9);
    }
#endif
}

void HAL_RTC_MspInit(RTC_HandleTypeDef *hrtc) {
    if (hrtc->Instance == RTC) {
        __HAL_RCC_RTC_ENABLE();
    }
}

void HAL_RTC_MspDeInit(RTC_HandleTypeDef *hrtc) {
    if (hrtc->Instance == RTC) {
        __HAL_RCC_RTC_DISABLE();
    }
}

void HAL_SPI_MspInit(SPI_HandleTypeDef *hspi) {
    if (const auto *config = buddy::hw::msp_config::spi(hspi->Instance)) {
        init_peripheral(hspi, *config);
        enable_irqs(*config);
    }
}

void HAL_SPI_MspDeInit(SPI_HandleTypeDef *hspi) {
    if (const auto *config = buddy::hw::msp_config::spi(hspi->Instance)) {
        deinit_peripheral(hspi, *config);
    }
}

void HAL_TIM_Base_MspInit(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM1) {
        __HAL_RCC_TIM1_CLK_ENABLE();
    } else if (htim->Instance == TIM2) {
        __HAL_RCC_TIM2_CLK_ENABLE();
    } else if (htim->Instance == TIM3) {
        __HAL_RCC_TIM3_CLK_ENABLE();
    } else if (htim->Instance == TIM8) {
        __HAL_RCC_TIM8_CLK_ENABLE();
    } else if (htim->Instance == TIM9) {
        __HAL_RCC_TIM9_CLK_ENABLE();
        HAL_NVIC_SetPriority(TIM1_BRK_TIM9_IRQn, ISR_PRIORITY_ACCELEROMETER, 0);
        HAL_NVIC_EnableIRQ(TIM1_BRK_TIM9_IRQn);
    } else if (htim->Instance == TIM13) {
        __HAL_RCC_TIM13_CLK_ENABLE();
        __HAL_DBGMCU_FREEZE_TIM13();
        HAL_NVIC_SetPriority(TIM8_UP_TIM13_IRQn, ISR_PRIORITY_PHASE_TIMER, 1);
        HAL_NVIC_EnableIRQ(TIM8_UP_TIM13_IRQn);
    } else if (htim->Instance == TIM14) {
        __HAL_RCC_TIM14_CLK_ENABLE();
        HAL_NVIC_SetPriority(TIM8_TRG_COM_TIM14_IRQn, ISR_PRIORITY_DEFAULT, 0);
        HAL_NVIC_EnableIRQ(TIM8_TRG_COM_TIM14_IRQn);
    }
}

void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) {
        __HAL_RCC_GPIOA_CLK_ENABLE();
        GPIO_InitTypeDef gpio { BUZZER_Pin, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_LOW, GPIO_AF1_TIM2 };
        HAL_GPIO_Init(BUZZER_GPIO_Port, &gpio);
    } else if (htim->Instance == TIM3) {
        __HAL_RCC_GPIOB_CLK_ENABLE();
        GPIO_InitTypeDef gpio { BED_HEAT_Pin | HEAT0_Pin, GPIO_MODE_AF_PP, GPIO_NOPULL, GPIO_SPEED_FREQ_LOW, GPIO_AF2_TIM3 };
        HAL_GPIO_Init(GPIOB, &gpio);
    } else if (htim->Instance == TIM8) {
        hdma_tim8.Instance = DMA2_Stream1;
        hdma_tim8.Init.Channel = DMA_CHANNEL_7;
        hdma_tim8.Init.Direction = DMA_MEMORY_TO_PERIPH;
        hdma_tim8.Init.PeriphInc = DMA_PINC_DISABLE;
        hdma_tim8.Init.MemInc = DMA_MINC_ENABLE;
        hdma_tim8.Init.PeriphDataAlignment = DMA_PDATAALIGN_WORD;
        hdma_tim8.Init.MemDataAlignment = DMA_MDATAALIGN_WORD;
        hdma_tim8.Init.Mode = DMA_NORMAL;
        hdma_tim8.Init.Priority = DMA_PRIORITY_HIGH;
        hdma_tim8.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
        if (HAL_DMA_Init(&hdma_tim8) != HAL_OK) {
            Error_Handler();
        }
        __HAL_LINKDMA(htim, hdma[TIM_DMA_ID_UPDATE], hdma_tim8);
    }
}

void HAL_TIM_Base_MspDeInit(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM1) {
        __HAL_RCC_TIM1_CLK_DISABLE();
    } else if (htim->Instance == TIM2) {
        __HAL_RCC_TIM2_CLK_DISABLE();
    } else if (htim->Instance == TIM3) {
        __HAL_RCC_TIM3_CLK_DISABLE();
    } else if (htim->Instance == TIM9) {
        __HAL_RCC_TIM9_CLK_DISABLE();
        HAL_NVIC_DisableIRQ(TIM1_BRK_TIM9_IRQn);
    } else if (htim->Instance == TIM13) {
        __HAL_RCC_TIM13_CLK_DISABLE();
        HAL_NVIC_DisableIRQ(TIM8_UP_TIM13_IRQn);
    } else if (htim->Instance == TIM14) {
        __HAL_RCC_TIM14_CLK_DISABLE();
        HAL_NVIC_DisableIRQ(TIM8_TRG_COM_TIM14_IRQn);
    }
}

void HAL_UART_MspInit(UART_HandleTypeDef *huart) {
    const auto *config = buddy::hw::msp_config::uart(huart->Instance);
    if (!config) {
        return;
    }
    init_peripheral(huart, *config);
    if (config->uart_actions & uart_enable_idle) {
        __HAL_UART_ENABLE_IT(huart, UART_IT_IDLE);
    }
    if (config->uart_actions & uart_enable_tc) {
        __HAL_UART_ENABLE_IT(huart, UART_IT_TC);
    }
    if (config->uart_actions & uart_clear_tc) {
        __HAL_UART_CLEAR_FLAG(huart, UART_FLAG_TC);
    }
    enable_irqs(*config);
}

void HAL_UART_MspDeInit(UART_HandleTypeDef *huart) {
    if (const auto *config = buddy::hw::msp_config::uart(huart->Instance)) {
        deinit_peripheral(huart, *config);
    }
}

void HAL_RNG_MspInit(RNG_HandleTypeDef *hrng) {
    if (hrng->Instance == RNG) {
        __HAL_RCC_RNG_CLK_ENABLE();
    }
}

void HAL_RNG_MspDeInit(RNG_HandleTypeDef *hrng) {
    if (hrng->Instance == RNG) {
        __HAL_RCC_RNG_CLK_DISABLE();
    }
}
