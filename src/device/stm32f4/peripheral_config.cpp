#include "peripheral_config.hpp"

#include <buddy/priorities_config.h>
#include <printers.h>

#include "adc.hpp"

namespace buddy::hw::peripheral_config {
namespace {

    template <typename T, size_t Size>
    constexpr Range<T> range(const T (&values)[Size]) {
        return { values, Size };
    }

    constexpr Irq dma_irq_configs[] = {
#if !PRINTER_IS_PRUSA_MINI()
        { DMA1_Stream3_IRQn,
    #if PRINTER_IS_PRUSA_XL()
            ISR_PRIORITY_PUPPIES_USART,
    #else
            ISR_PRIORITY_DEFAULT,
    #endif
            0 },
#endif
#if BOARD_IS_XBUDDY()
        { DMA1_Stream3_IRQn, ISR_PRIORITY_ACCELEROMETER, 0 },
        { DMA1_Stream4_IRQn, ISR_PRIORITY_ACCELEROMETER, 0 },
#endif
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
        { DMA1_Stream0_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA1_Stream2_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA1_Stream6_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA2_Stream3_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA2_Stream4_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA2_Stream5_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA2_Stream7_IRQn,
    #if PRINTER_IS_PRUSA_iX() || PRINTER_IS_PRUSA_COREONE()
            ISR_PRIORITY_PUPPIES_USART,
    #else
            ISR_PRIORITY_DEFAULT,
    #endif
            0 },
#endif
        { DMA1_Stream0_IRQn, ISR_PRIORITY_DEFAULT, 0 },
#if BOARD_IS_XLBUDDY()
        { DMA1_Stream1_IRQn, ISR_PRIORITY_PUPPIES_USART, 0 },
        { DMA2_Stream0_IRQn, ISR_PRIORITY_DEFAULT, 0 },
#endif
        { DMA1_Stream4_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA1_Stream5_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA1_Stream7_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA2_Stream1_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA2_Stream2_IRQn,
#if PRINTER_IS_PRUSA_iX() || PRINTER_IS_PRUSA_COREONE()
            ISR_PRIORITY_PUPPIES_USART,
#else
            ISR_PRIORITY_DEFAULT,
#endif
            0 },
        { DMA2_Stream4_IRQn, ISR_PRIORITY_DEFAULT, 0 },
        { DMA2_Stream6_IRQn, ISR_PRIORITY_DEFAULT, 0 },
    };

#if BOARD_IS_BUDDY()
    constexpr AdcInput adc1_channel_configs[] = {
        { ADC_CHANNEL_10, AdcChannel::hotend_T },
        { ADC_CHANNEL_4, AdcChannel::heatbed_T },
        { ADC_CHANNEL_5, AdcChannel::board_T },
        { ADC_CHANNEL_6, AdcChannel::pinda_T },
        { ADC_CHANNEL_3, AdcChannel::heatbed_U },
        { ADC_CHANNEL_TEMPSENSOR, AdcChannel::mcu_temperature },
        { ADC_CHANNEL_VREFINT, AdcChannel::vref },
    };
#elif BOARD_IS_XBUDDY() && PRINTER_IS_PRUSA_MK3_5()
    constexpr AdcInput adc1_channel_configs[] = {
        { ADC_CHANNEL_10, AdcChannel::hotend_T },
        { ADC_CHANNEL_4, AdcChannel::heatbed_T },
        { ADC_CHANNEL_5, AdcChannel::heatbed_U },
        { ADC_CHANNEL_3, AdcChannel::hotend_U },
        { ADC_CHANNEL_VREFINT, AdcChannel::vref },
        { ADC_CHANNEL_TEMPSENSOR, AdcChannel::mcu_temperature },
    };
#elif BOARD_IS_XBUDDY()
    constexpr AdcInput adc1_channel_configs[] = {
        { ADC_CHANNEL_10, AdcChannel::hotend_T },
        { ADC_CHANNEL_4, AdcChannel::heatbed_T },
        { ADC_CHANNEL_5, AdcChannel::heatbed_U },
        { ADC_CHANNEL_6, AdcChannel::heatbreak_T },
        { ADC_CHANNEL_3, AdcChannel::hotend_U },
        { ADC_CHANNEL_VREFINT, AdcChannel::vref },
        { ADC_CHANNEL_TEMPSENSOR, AdcChannel::mcu_temperature },
    };
#elif BOARD_IS_XLBUDDY()
    constexpr AdcInput adc1_channel_configs[] = {
        { ADC_CHANNEL_4, AdcChannel::dwarf_I },
        { ADC_CHANNEL_5, AdcChannel::mux1_y },
        { ADC_CHANNEL_8, AdcChannel::mux1_x },
        { ADC_CHANNEL_VREFINT, AdcChannel::vref },
        { ADC_CHANNEL_TEMPSENSOR, AdcChannel::mcu_temperature },
    };
#else
    #error "Unknown board"
#endif

#ifdef HAS_ADC3
    #if BOARD_IS_XBUDDY()
    constexpr AdcInput adc3_channel_configs[] = {
        { ADC_CHANNEL_4, AdcChannel::MMU_I },
        { ADC_CHANNEL_8, AdcChannel::board_T },
        { ADC_CHANNEL_9, AdcChannel::hotend_I },
        { ADC_CHANNEL_14, AdcChannel::board_I },
        #if PRINTER_IS_PRUSA_iX()
        { ADC_CHANNEL_15, AdcChannel::case_T },
        #elif PRINTER_IS_PRUSA_COREONE() || PRINTER_IS_PRUSA_MK4()
        { ADC_CHANNEL_15, AdcChannel::door_sensor },
        #endif
    };
    #elif BOARD_IS_XLBUDDY()
    constexpr AdcInput adc3_channel_configs[] = {
        { ADC_CHANNEL_8, AdcChannel::board_T },
        { ADC_CHANNEL_4, AdcChannel::mux2_y },
        { ADC_CHANNEL_10, AdcChannel::mux2_x },
    };
    #else
        #error "Unknown board"
    #endif
#endif

} // namespace

Range<Irq> dma_irqs() {
    return range(dma_irq_configs);
}

Range<AdcInput> adc1_channels() {
    return range(adc1_channel_configs);
}

#ifdef HAS_ADC3
Range<AdcInput> adc3_channels() {
    return range(adc3_channel_configs);
}
#endif

void configure_rtc(RTC_HandleTypeDef &rtc) {
    rtc.Instance = RTC;
    rtc.Init.HourFormat = RTC_HOURFORMAT_24;
    rtc.Init.AsynchPrediv = 127;
    rtc.Init.SynchPrediv = 255;
    rtc.Init.OutPut = RTC_OUTPUT_DISABLE;
    rtc.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
    rtc.Init.OutPutType = RTC_OUTPUT_TYPE_OPENDRAIN;
}

void configure_adc(ADC_HandleTypeDef &adc, ADC_TypeDef *instance, uint32_t conversion_count) {
    adc.Instance = instance;
    adc.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    adc.Init.Resolution = ADC_RESOLUTION_12B;
    adc.Init.ScanConvMode = ENABLE;
    adc.Init.ContinuousConvMode = ENABLE;
    adc.Init.DiscontinuousConvMode = DISABLE;
    adc.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    adc.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    adc.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    adc.Init.NbrOfConversion = conversion_count;
    adc.Init.DMAContinuousRequests = ENABLE;
    adc.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
}

void configure_i2c(I2C_HandleTypeDef &i2c, I2C_TypeDef *instance, uint32_t clock_speed) {
    i2c.Instance = instance;
    i2c.Init.ClockSpeed = clock_speed;
    i2c.Init.DutyCycle = I2C_DUTYCYCLE_2;
    i2c.Init.OwnAddress1 = 0;
    i2c.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    i2c.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    i2c.Init.OwnAddress2 = 0;
    i2c.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    i2c.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
}

void configure_spi(SPI_HandleTypeDef &spi, SPI_TypeDef *instance, uint32_t polarity, uint32_t phase, uint32_t prescaler) {
    spi.Instance = instance;
    spi.Init.Mode = SPI_MODE_MASTER;
    spi.Init.Direction = SPI_DIRECTION_2LINES;
    spi.Init.DataSize = SPI_DATASIZE_8BIT;
    spi.Init.CLKPolarity = polarity;
    spi.Init.CLKPhase = phase;
    spi.Init.NSS = SPI_NSS_SOFT;
    spi.Init.BaudRatePrescaler = prescaler;
    spi.Init.FirstBit = SPI_FIRSTBIT_MSB;
    spi.Init.TIMode = SPI_TIMODE_DISABLE;
    spi.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    spi.Init.CRCPolynomial = 10;
}

void configure_timer(TIM_HandleTypeDef &timer, TIM_TypeDef *instance, uint32_t prescaler, uint32_t counter_mode, uint32_t period) {
    timer.Instance = instance;
    timer.Init.Prescaler = prescaler;
    timer.Init.CounterMode = counter_mode;
    timer.Init.Period = period;
    timer.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
}

TIM_ClockConfigTypeDef timer_clock() {
    TIM_ClockConfigTypeDef config {};
    config.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    return config;
}

TIM_MasterConfigTypeDef timer_master() {
    TIM_MasterConfigTypeDef config {};
    config.MasterOutputTrigger = TIM_TRGO_RESET;
    config.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    return config;
}

TIM_OC_InitTypeDef timer_pwm(uint32_t pulse) {
    TIM_OC_InitTypeDef config {};
    config.OCMode = TIM_OCMODE_PWM1;
    config.Pulse = pulse;
    config.OCPolarity = TIM_OCPOLARITY_HIGH;
    config.OCFastMode = TIM_OCFAST_DISABLE;
    return config;
}

} // namespace buddy::hw::peripheral_config
