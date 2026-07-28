#include <buddy/unreachable.hpp>
#include <device/board.h>
#include <device/peripherals.h>
#include <buddy/phase_stepping_opts.h>
#include <atomic>
#include "Pin.hpp"
#include "hwio_pindef.h"
#include "safe_state.h"
#include <buddy/main.h>
#include "adc.hpp"
#include "stm32f4xx_hal_adc.h"
#include "timer_defaults.h"
#include "PCA9557.hpp"
#include "TCA6408A.hpp"
#include <logging/log.hpp>
#include "timing_precise.hpp"
#include <option/has_burst_stepping.h>
#include <option/has_i2c_expander.h>
#include <printers.h>
#include "peripheral_config.hpp"
// breakpoint
#include "FreeRTOS.h"
#include "task.h"
#if (BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY())
    #include "hw_configuration.hpp"
#endif
//
// I2C
//
I2C_HandleTypeDef hi2c1;
I2C_HandleTypeDef hi2c2;
I2C_HandleTypeDef hi2c3;
//
// SPI
//
SPI_HandleTypeDef hspi2;
SPI_HandleTypeDef hspi3;
SPI_HandleTypeDef hspi4;
SPI_HandleTypeDef hspi5;
SPI_HandleTypeDef hspi6;
//
// ADCs
//
ADC_HandleTypeDef hadc1;
ADC_HandleTypeDef hadc2;
ADC_HandleTypeDef hadc3;
//
// Timers
//
TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim8;
TIM_HandleTypeDef htim9;
TIM_HandleTypeDef htim13;
TIM_HandleTypeDef htim14;
//
// Other
//
RTC_HandleTypeDef hrtc;
RNG_HandleTypeDef hrng;
namespace buddy::hw {
#if HAS_I2C_EXPANDER() // HAS_I2C_EXPANDER corresponds to FDM-MK4-GPIO, not io_expander1 which connects DWARFs
TCA6408A io_expander2(I2C_HANDLE_FOR(io_expander2));
#endif // HAS_I2C_EXPANDER()
#if BOARD_IS_XLBUDDY()
PCA9557 io_expander1(I2C_HANDLE_FOR(io_expander1), 0x1);
#endif // BOARD_IS_XLBUDDY()
} // namespace buddy::hw
//
// Initialization
//
#if PRINTER_IS_PRUSA_iX()
// called at earliest possible time after system/core inits to set turbine PWM pin (heatbed PWM pin) high and disable it
void hw_preinit_turbine_disable() {
    uint32_t offset = 0;
    uint32_t pin = BED_HEAT_Pin;
    while (!(pin & 0x1)) {
        pin >>= 1;
        offset++;
    }
    uint32_t temp = BED_HEAT_GPIO_Port->MODER;
    temp &= ~(GPIO_MODER_MODER0 << (offset * 2U));
    temp |= ((GPIO_MODE_OUTPUT_PP) << (offset * 2U));
    BED_HEAT_GPIO_Port->MODER = temp;
    temp = BED_HEAT_GPIO_Port->ODR;
    temp |= BED_HEAT_Pin;
    BED_HEAT_GPIO_Port->ODR = temp;
}
#endif
void hw_rtc_init() {
    buddy::hw::peripheral_config::configure_rtc(hrtc);
    if (HAL_RTC_Init(&hrtc) != HAL_OK) {
        Error_Handler();
    }
    HAL_RTC_DeactivateAlarm(&hrtc, RTC_ALARM_A);
    HAL_RTC_DeactivateAlarm(&hrtc, RTC_ALARM_B);
    HAL_RTCEx_DeactivateCalibrationOutPut(&hrtc);
    HAL_RTCEx_DeactivateTamper(&hrtc, RTC_TAFCR_TAMP1E);
    HAL_RTCEx_DeactivateTimeStamp(&hrtc);
}
void hw_rng_init() {
    hrng.Instance = RNG;
    if (HAL_RNG_Init(&hrng) != HAL_OK) {
        Error_Handler();
    }
}
void hw_gpio_init() {
    GPIO_InitTypeDef GPIO_InitStruct {};
    // GPIO Ports Clock Enable
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOD_CLK_ENABLE();
    __HAL_RCC_GPIOE_CLK_ENABLE();
    __HAL_RCC_GPIOF_CLK_ENABLE();
    __HAL_RCC_GPIOG_CLK_ENABLE();
    __HAL_RCC_GPIOH_CLK_ENABLE();
    // Configure GPIO pins : USB_OVERC_Pin ESP_GPIO0_Pin BED_MON_Pin WP1_Pin
    GPIO_InitStruct.Pin = USB_OVERC_Pin | ESP_GPIO0_Pin | BED_MON_Pin | WP1_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);
    // NOTE: Configuring GPIO causes a short drop of pin output to low. This is
    //       avoided by first setting the pin and then initilizing the GPIO. In case
    //       this does not work we first initilize ESP GPIO0 to avoid reset low
    //       followed by ESP GPIO low as this sequence can switch esp to boot mode */
    // Configure ESP GPIO0 (PROG, High for ESP module boot from Flash)
    GPIO_InitStruct.Pin =
#if (BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY())
        GPIO_PIN_15
#else
        GPIO_PIN_6
#endif
        ;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_WritePin(GPIOE,
#if (BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY())
        GPIO_PIN_15
#else
        GPIO_PIN_6
#endif
        ,
        GPIO_PIN_SET);
    HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);
    // Configure GPIO pins : ESP_RST_Pin
    GPIO_InitStruct.Pin = ESP_RST_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_WritePin(GPIOC, ESP_RST_Pin, GPIO_PIN_SET);
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    // Configure GPIO pins : WP2_Pin
    GPIO_InitStruct.Pin = WP2_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    PIN_TABLE(CONFIGURE_PINS);
#if defined(EXTENDER_PIN_TABLE)
    EXTENDER_PIN_TABLE(CONFIGURE_PINS);
#endif
    buddy::hw::hwio_configure_board_revision_changed_pins();
}
void hw_dma_init() {
    __HAL_RCC_DMA1_CLK_ENABLE();
    __HAL_RCC_DMA2_CLK_ENABLE();
    const auto irqs = buddy::hw::peripheral_config::dma_irqs();
    for (size_t index = 0; index < irqs.size; ++index) {
        const auto &irq = irqs.data[index];
        HAL_NVIC_SetPriority(irq.irq, irq.priority, irq.subpriority);
        HAL_NVIC_EnableIRQ(irq.irq);
    }
}
void static config_adc(ADC_HandleTypeDef *hadc, ADC_TypeDef *ADC_NUM, uint32_t NbrOfConversion) {
    buddy::hw::peripheral_config::configure_adc(*hadc, ADC_NUM, NbrOfConversion);
    if (HAL_ADC_Init(hadc) != HAL_OK) {
        Error_Handler();
    }
}
static void config_adc_ch(ADC_HandleTypeDef *hadc, uint32_t Channel, uint32_t Rank) {
    // To make the MCU temperature measurement accurate we need to have higher sample time.
    // The data sheet says for 1C accuracy measure for at least 10us.
    // With 480 cycles we get around +- 0.3C accuracy.
    // With 144 cycles we get around +- 0.5C accuracy + the total value is about 0.35 higher then with 480 cycles.
    // 144 cycles is still good enough (also still keeps AWDG fast).
    // If the MCU overheat will keep happening we can increase the cycles to 480
    auto sample_time = ADC_SAMPLETIME_28CYCLES;
    if (hadc == &hadc1 && (Channel == ADC_CHANNEL_TEMPSENSOR || Channel == ADC_CHANNEL_VREFINT)) {
        sample_time = ADC_SAMPLETIME_480CYCLES;
    }
    Rank++; // Channel rank starts at 1, but for array indexing, we need to start from 0.
    ADC_ChannelConfTypeDef sConfig = { Channel, Rank, sample_time, 0 };
    if (HAL_ADC_ConfigChannel(hadc, &sConfig) != HAL_OK) {
        Error_Handler();
    }
}
void hw_adc1_init() {
    config_adc(&hadc1, ADC1, AdcChannel::ADC1_CH_CNT);
    const auto channels = buddy::hw::peripheral_config::adc1_channels();
    for (size_t index = 0; index < channels.size; ++index) {
        config_adc_ch(&hadc1, channels.data[index].channel, channels.data[index].rank);
    }
    HAL_NVIC_DisableIRQ(DMA2_Stream4_IRQn);
}
#ifdef HAS_ADC3
void hw_adc3_init() {
    config_adc(&hadc3, ADC3, AdcChannel::ADC3_CH_CNT);
    const auto channels = buddy::hw::peripheral_config::adc3_channels();
    for (size_t index = 0; index < channels.size; ++index) {
        config_adc_ch(&hadc3, channels.data[index].channel, channels.data[index].rank);
    }
    HAL_NVIC_DisableIRQ(DMA2_Stream0_IRQn);
}
#endif
void hw_adc_irq_init() {
    HAL_NVIC_SetPriority(ADC_IRQn, ISR_PRIORITY_DEFAULT, 0);
    HAL_NVIC_EnableIRQ(ADC_IRQn);
}
struct hw_pin {
    GPIO_TypeDef *port;
    uint16_t no;
};
/**
 * @brief Set the pin to open-drain
 */
static void set_pin_od(hw_pin pin) {
    GPIO_InitTypeDef GPIO_InitStruct {};
    GPIO_InitStruct.Pin = pin.no;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FAST;
    GPIO_InitStruct.Alternate = 0;
    HAL_GPIO_Init(pin.port, &GPIO_InitStruct);
}
/**
 * @brief Set the pin to input
 */
static void set_pin_in(hw_pin pin) {
    GPIO_InitTypeDef GPIO_InitStruct {};
    GPIO_InitStruct.Pin = pin.no;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FAST;
    GPIO_InitStruct.Alternate = 0;
    HAL_GPIO_Init(pin.port, &GPIO_InitStruct);
}
/**
 * @brief calculate edge timing
 * edges timing is of half period
 * round up
 *
 * @param clk frequency [Hz]
 * @return constexpr uint32_t half of period [us]
 */
static constexpr uint32_t i2c_get_edge_us(uint32_t clk) {
    // clk + 1 .. round up
    // / 2     .. need half of period
    return (1'000'000 % clk ? (1'000'000 / clk + 1) : (1'000'000 / clk)) / 2;
}
/**
 * @brief unblock i2c data pin
 * apply up to 32 clock pulses and check SDA logical level
 * make sure it is in '1', so master can manipulate with it
 *
 * @param clk   frequency [Hz]
 * @param sda   pin of data
 * @param scl   pin of clock
 */
static void i2c_unblock_sda(uint32_t clk, hw_pin sda, hw_pin scl) {
    delay_us_precise(i2c_get_edge_us(clk)); // half period - ensure first edge is not too short
    // ORIGINAL COMMENT (i < 9): 9 pulses, there is no point to try it more times - 9th bit is ACK (will be NACK)
    // Changed to an arbitrary higher value, because comm with the touchscreen controller is extra sketchy, clock gets lost sometimes and such
    // Cannot be used on multi-master buses
    for (size_t i = 0; i < 32; ++i) {
        HAL_GPIO_WritePin(scl.port, scl.no, GPIO_PIN_SET); // set clock to '1'
        delay_us_precise(i2c_get_edge_us(clk)); // wait half period
        if (HAL_GPIO_ReadPin(sda.port, sda.no) == GPIO_PIN_SET) { // check if slave does not pull SDA to '0' while SCL == 1
            return; // sda is not pulled by a slave, it is done
        }
        HAL_GPIO_WritePin(scl.port, scl.no, GPIO_PIN_RESET); // set clock to '0'
        delay_us_precise(i2c_get_edge_us(clk)); // wait half period
    }
// in case code reaches this, there is some HW issue
// but we cannot log it or rise red screen, it is too early
#if defined(_DEBUG) || DEVELOPER_MODE()
    buddy_disable_heaters();
    __BKPT(0);
#endif
    HAL_GPIO_WritePin(scl.port, scl.no, GPIO_PIN_SET); // this code should never be reached, just in case it was set clock to '1'
}
/**
 * @brief free I2C in case of slave deadlock
 * in case printer is resetted during I2C transmit, slave can deadlock
 * it has not been resetted and is expecting clock to finish its command
 * problem is that it can hold SDA in '0' - it blocks the bus so master cannot do start / stop condition
 * this code generates a clock until SDA is in '1' and than master sdoes start + stop to end any slave communication
 *
 * @param clk   frequency [Hz]
 * @param sda   pin of data
 * @param scl   pin of clock
 */
static void i2c_free_bus_in_case_of_slave_deadlock(uint32_t clk, hw_pin sda, hw_pin scl) {
    set_pin_in(sda); // configure SDA to input
    if (HAL_GPIO_ReadPin(sda.port, sda.no) == GPIO_PIN_RESET) { // check if slave pulls SDA to '0' while SCL == 1
        set_pin_od(scl); // configure SCL to open-drain
        i2c_unblock_sda(clk, sda, scl); // get SDA pin in state pin can be "moved"
    }
    set_pin_od(sda); // reconfigure SDA to open-drain, to be able to move it
    HAL_GPIO_WritePin(sda.port, sda.no, GPIO_PIN_RESET); // set SDA to '0' while SCL == '1' - start condition
    delay_us_precise(i2c_get_edge_us(clk)); // wait half period
    HAL_GPIO_WritePin(sda.port, sda.no, GPIO_PIN_RESET); // set SDA to '1' while SCL == '1' - stop condition
    delay_us_precise(i2c_get_edge_us(clk)); // wait half period
}
#if HAS_I2CN(1)
static constexpr uint32_t i2c1_speed = 400'000;
void hw_i2c1_pins_init() {
    GPIO_InitTypeDef GPIO_InitStruct {};
    __HAL_RCC_GPIOB_CLK_ENABLE();
    i2c_free_bus_in_case_of_slave_deadlock(i2c1_speed, { i2c1_SDA_PORT, i2c1_SDA_PIN }, { i2c1_SCL_PORT, i2c1_SCL_PIN });
    // GPIO I2C mode
    GPIO_InitStruct.Pin = i2c1_SDA_PIN | i2c1_SCL_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF4_I2C1;
    HAL_GPIO_Init(i2c1_SDA_PORT, &GPIO_InitStruct);
    // Peripheral clock enable
    __HAL_RCC_I2C1_CLK_ENABLE();
}
void hw_i2c1_init() {
    buddy::hw::peripheral_config::configure_i2c(hi2c1, I2C1, i2c1_speed);
    if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
        Error_Handler();
    }
    #if defined(I2C_FLTR_ANOFF) && defined(I2C_FLTR_DNF)
    // Configure Analog filter
    if (HAL_I2CEx_ConfigAnalogFilter(&hi2c1, I2C_ANALOGFILTER_ENABLE) != HAL_OK) {
        Error_Handler();
    }
    // Configure Digital filter
    if (HAL_I2CEx_ConfigDigitalFilter(&hi2c1, 0) != HAL_OK) {
        Error_Handler();
    }
    #endif
}
#endif // HAS_I2CN(1)
#if HAS_I2CN(2)
// speed must be 400k, maybe, for reasons lost in time
static constexpr uint32_t i2c2_speed = 400'000;
void hw_i2c2_pins_init() {
    GPIO_InitTypeDef GPIO_InitStruct {};
    __HAL_RCC_GPIOF_CLK_ENABLE();
    i2c_free_bus_in_case_of_slave_deadlock(i2c2_speed, { i2c2_SDA_PORT, i2c2_SDA_PIN }, { i2c2_SCL_PORT, i2c2_SCL_PIN });
    // GPIO I2C mode
    GPIO_InitStruct.Pin = i2c2_SDA_PIN | i2c2_SCL_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF4_I2C2;
    HAL_GPIO_Init(i2c2_SDA_PORT, &GPIO_InitStruct);
    // Peripheral clock enable
    __HAL_RCC_I2C2_CLK_ENABLE();
}
void hw_i2c2_init() {
    buddy::hw::peripheral_config::configure_i2c(hi2c2, I2C2, i2c2_speed);
    if (HAL_I2C_Init(&hi2c2) != HAL_OK) {
        Error_Handler();
    }
    #if defined(I2C_FLTR_ANOFF) && defined(I2C_FLTR_DNF)
    // Configure Analog filter
    if (HAL_I2CEx_ConfigAnalogFilter(&hi2c2, I2C_ANALOGFILTER_ENABLE) != HAL_OK) {
        Error_Handler();
    }
    // Configure Digital filter to maximum (tHD:STA 0.357us delay)
    if (HAL_I2CEx_ConfigDigitalFilter(&hi2c2, 0x0F) != HAL_OK) {
        Error_Handler();
    }
    #endif
}
#endif // HAS_I2CN(2)
#if HAS_I2CN(3)
static constexpr uint32_t i2c3_speed = 100'000;
void hw_i2c3_pins_init() {
    GPIO_InitTypeDef GPIO_InitStruct {};
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    i2c_free_bus_in_case_of_slave_deadlock(i2c3_speed, { i2c3_SDA_PORT, i2c3_SDA_PIN }, { i2c3_SCL_PORT, i2c3_SCL_PIN });
    // GPIO I2C mode
    GPIO_InitStruct.Pin = i2c3_SDA_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_OD;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF4_I2C3;
    HAL_GPIO_Init(i2c3_SDA_PORT, &GPIO_InitStruct);
    GPIO_InitStruct.Pin = i2c3_SCL_PIN;
    HAL_GPIO_Init(i2c3_SCL_PORT, &GPIO_InitStruct);
    // Peripheral clock enable
    __HAL_RCC_I2C3_CLK_ENABLE();
}
void hw_i2c3_init() {
    buddy::hw::peripheral_config::configure_i2c(hi2c3, I2C3, i2c3_speed);
    if (HAL_I2C_Init(&hi2c3) != HAL_OK) {
        Error_Handler();
    }
    #if defined(I2C_FLTR_ANOFF) && defined(I2C_FLTR_DNF)
    // Configure Analogue filter
    if (HAL_I2CEx_ConfigAnalogFilter(&hi2c3, I2C_ANALOGFILTER_ENABLE) != HAL_OK) {
        Error_Handler();
    }
    // Configure Digital filter
    if (HAL_I2CEx_ConfigDigitalFilter(&hi2c3, 0) != HAL_OK) {
        Error_Handler();
    }
    #endif
}
#endif // HAS_I2CN(3)
void hw_spi2_init() {
#if spi_accelerometer == 2
    constexpr auto polarity = SPI_POLARITY_HIGH;
    constexpr auto phase = SPI_PHASE_2EDGE;
    constexpr auto prescaler = SPI_BAUDRATEPRESCALER_8;
#elif spi_lcd == 2
    constexpr auto polarity = SPI_POLARITY_LOW;
    constexpr auto phase = SPI_PHASE_1EDGE;
    constexpr auto prescaler = SPI_BAUDRATEPRESCALER_2;
#endif
    buddy::hw::peripheral_config::configure_spi(hspi2, SPI2, polarity, phase, prescaler);
    if (HAL_SPI_Init(&hspi2) != HAL_OK) {
        Error_Handler();
    }
}
void hw_spi3_init() {
#if (BOARD_IS_BUDDY())
    constexpr auto prescaler = SPI_BAUDRATEPRESCALER_2;
#else
    constexpr auto prescaler = SPI_BAUDRATEPRESCALER_8;
#endif
    buddy::hw::peripheral_config::configure_spi(hspi3, SPI3, SPI_POLARITY_LOW, SPI_PHASE_1EDGE, prescaler);
    if (HAL_SPI_Init(&hspi3) != HAL_OK) {
        Error_Handler();
    }
}
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
void hw_spi4_init() {
    // SPI 4 is used for side leds, but only on specific HW revisions
    buddy::hw::peripheral_config::configure_spi(hspi4, SPI4, SPI_POLARITY_LOW, SPI_PHASE_1EDGE, SPI_BAUDRATEPRESCALER_8);
    if (HAL_SPI_Init(&hspi4) != HAL_OK) {
        Error_Handler();
    }
}
#endif
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
void hw_spi5_init() {
    buddy::hw::peripheral_config::configure_spi(hspi5, SPI5, SPI_POLARITY_LOW, SPI_PHASE_1EDGE, SPI_BAUDRATEPRESCALER_2);
    if (HAL_SPI_Init(&hspi5) != HAL_OK) {
        Error_Handler();
    }
}
#endif
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
void hw_spi6_init() {
    buddy::hw::peripheral_config::configure_spi(hspi6, SPI6, SPI_POLARITY_LOW, SPI_PHASE_1EDGE, SPI_BAUDRATEPRESCALER_2);
    if (HAL_SPI_Init(&hspi6) != HAL_OK) {
        Error_Handler();
    }
}
#endif
void hw_tim1_init() {
    auto sClockSourceConfig = buddy::hw::peripheral_config::timer_clock();
    auto sMasterConfig = buddy::hw::peripheral_config::timer_master();
    auto sConfigOC = buddy::hw::peripheral_config::timer_pwm(0);
    TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig {};
    buddy::hw::peripheral_config::configure_timer(htim1, TIM1, TIM1_default_Prescaler, TIM_COUNTERMODE_DOWN, TIM1_default_Period);
    htim1.Init.RepetitionCounter = 0;
    if (HAL_TIM_Base_Init(&htim1) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_PWM_Init(&htim1) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK) {
        Error_Handler();
    }
    sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
    sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
    sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
    if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1) != HAL_OK) { //_PWM_FAN1
        Error_Handler();
    }
    if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_2) != HAL_OK) { //_PWM_FAN
        Error_Handler();
    }
    sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
    sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
    sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
    sBreakDeadTimeConfig.DeadTime = 0;
    sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
    sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
    sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
    if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK) {
        Error_Handler();
    }
    __HAL_TIM_ENABLE(&htim1);
}
void hw_tim2_init() {
    auto sClockSourceConfig = buddy::hw::peripheral_config::timer_clock();
    auto sMasterConfig = buddy::hw::peripheral_config::timer_master();
    auto sConfigOC = buddy::hw::peripheral_config::timer_pwm(21000);
    buddy::hw::peripheral_config::configure_timer(htim2, TIM2, 100, TIM_COUNTERMODE_DOWN, 42000);
    if (HAL_TIM_Base_Init(&htim2) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_PWM_Init(&htim2) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1) != HAL_OK) {
        Error_Handler();
    }
    HAL_TIM_MspPostInit(&htim2);
}
void hw_tim3_init() {
    auto sClockSourceConfig = buddy::hw::peripheral_config::timer_clock();
    auto sMasterConfig = buddy::hw::peripheral_config::timer_master();
    auto sConfigOC = buddy::hw::peripheral_config::timer_pwm(21000);
#if BOARD_IS_BUDDY()
    constexpr auto prescaler = TIM3_default_Prescaler; // 49ms, 20.3Hz
#elif BOARD_IS_XBUDDY()
    constexpr auto prescaler = 11; // 36us, 33.0kHz
#elif BOARD_IS_XLBUDDY()
    BUDDY_UNREACHABLE();
    constexpr auto prescaler = 0;
#else
    // If there ever is another board, this needs to fail loudly.
    #error "Unsupported board"
#endif
    buddy::hw::peripheral_config::configure_timer(htim3, TIM3, prescaler, TIM_COUNTERMODE_DOWN, TIM3_default_Period);
    if (HAL_TIM_Base_Init(&htim3) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_PWM_Init(&htim3) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_3) != HAL_OK) { //_PWM_HEATER_BED
        Error_Handler();
    }
    if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_4) != HAL_OK) { //_PWM_HEATER_0
        Error_Handler();
    }
    HAL_TIM_MspPostInit(&htim3);
    __HAL_TIM_ENABLE(&htim3);
}
void hw_tim8_init() {
    auto sClockSourceConfig = buddy::hw::peripheral_config::timer_clock();
    auto sMasterConfig = buddy::hw::peripheral_config::timer_master();
    using phase_stepping::opts::GPIO_BUFFER_SIZE;
    using phase_stepping::opts::REFRESH_FREQ;
    // Clock the period ever-so-slighly faster than the required number of events to create a gap
    // between two bursts big enough to allow scheduling in the case of two full buffers and a
    // shorter-than-expected interval between the ISRs.
    uint32_t period = 168'000'000 / (REFRESH_FREQ * (GPIO_BUFFER_SIZE + 1)) - 1;
    buddy::hw::peripheral_config::configure_timer(htim8, TIM8, 0, TIM_COUNTERMODE_UP, period);
    if (HAL_TIM_Base_Init(&htim8) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_ConfigClockSource(&htim8, &sClockSourceConfig) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIMEx_MasterConfigSynchronization(&htim8, &sMasterConfig) != HAL_OK) {
        Error_Handler();
    }
    HAL_TIM_MspPostInit(&htim8);
}
void hw_tim9_init() {
    auto sClockSourceConfig = buddy::hw::peripheral_config::timer_clock();
    auto sMasterConfig = buddy::hw::peripheral_config::timer_master();
    // This timer is used for local accelerometer polling. The polling rate has
    // to be higher than the actual accelerometer sampling rate. The sampling
    // rate of LIS2DH12 is ~1.5 kH. Hence, we use double the rate.
    buddy::hw::peripheral_config::configure_timer(htim9, TIM9, 1680 - 1, TIM_COUNTERMODE_UP, 33 - 1);
    if (HAL_TIM_Base_Init(&htim9) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIM_ConfigClockSource(&htim9, &sClockSourceConfig) != HAL_OK) {
        Error_Handler();
    }
    if (HAL_TIMEx_MasterConfigSynchronization(&htim9, &sMasterConfig) != HAL_OK) {
        Error_Handler();
    }
    HAL_TIM_MspPostInit(&htim9);
}
void hw_tim13_init() {
    buddy::hw::peripheral_config::configure_timer(htim13, TIM13, 0, TIM_COUNTERMODE_UP, 84'000'000 / phase_stepping::opts::REFRESH_FREQ - 1);
    htim13.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Base_Init(&htim13) != HAL_OK) {
        Error_Handler();
    }
}
void hw_tim14_init() {
    buddy::hw::peripheral_config::configure_timer(htim14, TIM14, 84, TIM_COUNTERMODE_UP, 1000);
    if (HAL_TIM_Base_Init(&htim14) != HAL_OK) {
        Error_Handler();
    }
    HAL_TIM_Base_Start_IT(&htim14);
}
