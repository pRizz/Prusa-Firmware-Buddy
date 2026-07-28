#include "hal_config.hpp"

#include "extension_variant.h"

namespace hal_config {

void configure_uart(UART_HandleTypeDef &uart, USART_TypeDef *instance, uint32_t baud_rate) {
    uart.Instance = instance;
    uart.Init.BaudRate = baud_rate;
    uart.Init.WordLength = UART_WORDLENGTH_8B;
    uart.Init.StopBits = UART_STOPBITS_1;
    uart.Init.Parity = UART_PARITY_NONE;
    uart.Init.Mode = UART_MODE_TX_RX;
    uart.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    uart.Init.OverSampling = UART_OVERSAMPLING_16;
    uart.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
    uart.Init.ClockPrescaler = UART_PRESCALER_DIV1;
    uart.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
}

void configure_adc(ADC_HandleTypeDef &adc) {
    adc.Instance = ADC1;
    adc.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV4;
    adc.Init.Resolution = ADC_RESOLUTION_12B;
    adc.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    adc.Init.ScanConvMode = ADC_SCAN_DISABLE;
    adc.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
    adc.Init.LowPowerAutoWait = DISABLE;
    adc.Init.ContinuousConvMode = DISABLE;
    adc.Init.NbrOfConversion = 1;
    adc.Init.DiscontinuousConvMode = DISABLE;
    adc.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    adc.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    adc.Init.DMAContinuousRequests = DISABLE;
    adc.Init.SamplingMode = ADC_SAMPLING_MODE_NORMAL;
    adc.Init.Overrun = ADC_OVR_DATA_PRESERVED;
    adc.Init.OversamplingMode = DISABLE;
}

ADC_ChannelConfTypeDef adc_channel() {
    ADC_ChannelConfTypeDef config {};
    config.Channel = ADC_CHANNEL_5;
    config.Rank = ADC_REGULAR_RANK_1;
    config.SamplingTime = ADC_SAMPLETIME_2CYCLES_5;
    config.SingleDiff = ADC_SINGLE_ENDED;
    config.OffsetNumber = ADC_OFFSET_NONE;
    config.Offset = 0;
    return config;
}

void configure_i2c(I2C_HandleTypeDef &i2c) {
    i2c.Instance = I2C2;
    i2c.Init.OwnAddress1 = 0;
    i2c.Init.Timing = 0x00707CBB;
    i2c.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    i2c.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    i2c.Init.OwnAddress2 = 0;
    i2c.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    i2c.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
}

GPIO_InitTypeDef uart_rs485_rx_tx_gpio() {
    return {
        .Pin = GPIO_PIN_7 | GPIO_PIN_8,
        .Mode = GPIO_MODE_AF_PP,
        .Pull = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
        .Alternate = GPIO_AF13_USART3,
    };
}

GPIO_InitTypeDef uart_rs485_de_gpio() {
    auto gpio = uart_rs485_rx_tx_gpio();
    gpio.Pin = GPIO_PIN_14;
    gpio.Alternate = GPIO_AF7_USART3;
    return gpio;
}

GPIO_InitTypeDef uart_mmu_tx_gpio() {
    return {
        .Pin = GPIO_PIN_15,
        .Mode = GPIO_MODE_AF_PP,
        .Pull = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
        .Alternate = GPIO_AF9_USART2,
    };
}

GPIO_InitTypeDef uart_mmu_rx_gpio() {
    auto gpio = uart_mmu_tx_gpio();
    gpio.Pin = GPIO_PIN_4;
    gpio.Alternate = GPIO_AF13_USART2;
    return gpio;
}

GPIO_InitTypeDef adc_gpio() {
    GPIO_InitTypeDef gpio {};
    gpio.Pin = GPIO_PIN_1;
    gpio.Mode = GPIO_MODE_ANALOG;
    gpio.Pull = GPIO_NOPULL;
    return gpio;
}

GPIO_InitTypeDef tim1_gpio() {
    return {
        .Pin =
#if EXTENSION_IS_IX()
            GPIO_PIN_8 | GPIO_PIN_10,
#else
            GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10,
#endif
        .Mode = GPIO_MODE_AF_PP,
        .Pull = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
        .Alternate = GPIO_AF1_TIM1,
    };
}

GPIO_InitTypeDef tim2_gpio() {
    return {
        .Pin = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3,
        .Mode = GPIO_MODE_AF_PP,
        .Pull = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
        .Alternate = GPIO_AF1_TIM2,
    };
}

GPIO_InitTypeDef tim3_gpio_a() {
    return {
        .Pin = GPIO_PIN_6 | GPIO_PIN_7,
        .Mode = GPIO_MODE_AF_PP,
        .Pull = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
        .Alternate = GPIO_AF2_TIM3,
    };
}

GPIO_InitTypeDef tim3_gpio_b() {
    auto gpio = tim3_gpio_a();
    gpio.Pin = GPIO_PIN_0;
    return gpio;
}

GPIO_InitTypeDef i2c_gpio() {
    return {
        .Pin = GPIO_PIN_10 | GPIO_PIN_13,
        .Mode = GPIO_MODE_AF_OD,
        .Pull = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
        .Alternate = GPIO_AF4_I2C2,
    };
}

GPIO_InitTypeDef output_gpio(uint32_t pin) {
    return {
        .Pin = pin,
        .Mode = GPIO_MODE_OUTPUT_PP,
        .Pull = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
        .Alternate = 0,
    };
}

GPIO_InitTypeDef filament_sensor_gpio() {
    return {
        .Pin = EXTENSION_IS_IX() ? GPIO_PIN_9 : GPIO_PIN_5,
        .Mode = GPIO_MODE_INPUT,
        .Pull = EXTENSION_IS_IX() ? GPIO_PULLUP : GPIO_PULLDOWN,
        .Speed = GPIO_SPEED_FREQ_LOW,
        .Alternate = 0,
    };
}

uint32_t filament_sensor_pin() {
    return EXTENSION_IS_IX() ? GPIO_PIN_9 : GPIO_PIN_5;
}

uint32_t tim1_ccmr1() {
    constexpr uint32_t capture_compare_selection = 0b01;
    constexpr uint32_t input_capture_filter = 0b0111;
    constexpr uint32_t input_capture_prescaler = 0b00;
    return (capture_compare_selection << TIM_CCMR1_CC1S_Pos)
        | (input_capture_prescaler << TIM_CCMR1_IC1PSC_Pos)
        | (input_capture_filter << TIM_CCMR1_IC1F_Pos)
        | (capture_compare_selection << TIM_CCMR1_CC2S_Pos)
        | (input_capture_prescaler << TIM_CCMR1_IC2PSC_Pos)
        | (input_capture_filter << TIM_CCMR1_IC2F_Pos);
}

uint32_t tim1_ccmr2() {
    constexpr uint32_t capture_compare_selection = 0b01;
    constexpr uint32_t input_capture_filter = 0b0111;
    constexpr uint32_t input_capture_prescaler = 0b00;
    return (capture_compare_selection << TIM_CCMR2_CC3S_Pos)
        | (input_capture_prescaler << TIM_CCMR2_IC3PSC_Pos)
        | (input_capture_filter << TIM_CCMR2_IC3F_Pos)
        | (capture_compare_selection << TIM_CCMR2_CC4S_Pos)
        | (input_capture_prescaler << TIM_CCMR2_IC4PSC_Pos)
        | (input_capture_filter << TIM_CCMR2_IC4F_Pos);
}

} // namespace hal_config
