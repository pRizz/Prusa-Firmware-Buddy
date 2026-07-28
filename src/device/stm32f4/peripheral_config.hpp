#pragma once

#include <cstddef>
#include <cstdint>

#include <device/board.h>

namespace buddy::hw::peripheral_config {

struct Irq {
    IRQn_Type irq;
    uint32_t priority;
    uint32_t subpriority;
};

struct AdcInput {
    uint32_t channel;
    uint32_t rank;
};

template <typename T>
struct Range {
    const T *data;
    size_t size;
};

Range<Irq> dma_irqs();
Range<AdcInput> adc1_channels();
#ifdef HAS_ADC3
Range<AdcInput> adc3_channels();
#endif

void configure_rtc(RTC_HandleTypeDef &rtc);
void configure_adc(ADC_HandleTypeDef &adc, ADC_TypeDef *instance, uint32_t conversion_count);
void configure_i2c(I2C_HandleTypeDef &i2c, I2C_TypeDef *instance, uint32_t clock_speed);
void configure_spi(SPI_HandleTypeDef &spi, SPI_TypeDef *instance, uint32_t polarity, uint32_t phase, uint32_t prescaler);
void configure_timer(TIM_HandleTypeDef &timer, TIM_TypeDef *instance, uint32_t prescaler, uint32_t counter_mode, uint32_t period);
TIM_ClockConfigTypeDef timer_clock();
TIM_MasterConfigTypeDef timer_master();
TIM_OC_InitTypeDef timer_pwm(uint32_t pulse);

} // namespace buddy::hw::peripheral_config
