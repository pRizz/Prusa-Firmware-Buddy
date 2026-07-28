#pragma once

#include <stm32h5xx_hal.h>

namespace hal_config {

void configure_uart(UART_HandleTypeDef &uart, USART_TypeDef *instance, uint32_t baud_rate);
void configure_adc(ADC_HandleTypeDef &adc);
ADC_ChannelConfTypeDef adc_channel();
void configure_i2c(I2C_HandleTypeDef &i2c);

GPIO_InitTypeDef uart_rs485_rx_tx_gpio();
GPIO_InitTypeDef uart_rs485_de_gpio();
GPIO_InitTypeDef uart_mmu_tx_gpio();
GPIO_InitTypeDef uart_mmu_rx_gpio();
GPIO_InitTypeDef adc_gpio();
GPIO_InitTypeDef tim1_gpio();
GPIO_InitTypeDef tim2_gpio();
GPIO_InitTypeDef tim3_gpio_a();
GPIO_InitTypeDef tim3_gpio_b();
GPIO_InitTypeDef i2c_gpio();
GPIO_InitTypeDef output_gpio(uint32_t pin);
GPIO_InitTypeDef filament_sensor_gpio();
uint32_t filament_sensor_pin();

uint32_t tim1_ccmr1();
uint32_t tim1_ccmr2();

} // namespace hal_config
