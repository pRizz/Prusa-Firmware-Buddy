#include <buddy/main.h>

#include "appmain.hpp"
#include "cmsis_os.h"
#include "config_features.h"
#include "crc32.h"
#include "data_exchange.hpp"
#include "gui.hpp"
#include "hwio_pindef.h"
#include "i2c.hpp"
#include "heap.h"
#include "platform.h"
#include "printers.h"
#include "tasks.hpp"
#include "tick_timer_api.h"

#include <common/st25dv64k.h>
#include <config_store/store_instance.hpp>
#include <crash_dump/dump.hpp>
#include <freertos/critical_section.hpp>
#include <option/buddy_enable_connect.h>
#include <option/has_local_accelerometer.h>

#if BUDDY_ENABLE_CONNECT()
    #include "connect/run.hpp"
#endif

#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    #include "hw_configuration.hpp"
#endif

#if HAS_LOCAL_ACCELEROMETER()
    #include <module/prusa/accelerometer_local.hpp>
#endif

using namespace crash_dump;

void StartDefaultTask([[maybe_unused]] void const *argument) {
    app_run();
    for (;;) {
        osDelay(1);
    }
}

void StartDisplayTask([[maybe_unused]] void const *argument) {
    gui_run();
    for (;;) {
        osDelay(1);
    }
}

void StartErrorDisplayTask([[maybe_unused]] void const *argument) {
    gui_error_run();
    for (;;) {
        osDelay(1);
    }
}

#if BUDDY_ENABLE_CONNECT()
void StartConnectTask([[maybe_unused]] void const *argument) {
    connect_client::run();
}

void StartConnectTaskError([[maybe_unused]] void const *argument) {
    connect_client::run_error();
}
#endif

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
#if HAS_LOCAL_ACCELEROMETER()
    if (htim->Instance == TIM9) {
        prusa_accelerometer_handle_polling();
    }
#endif
    if (htim->Instance == TIM14) {
        app_tim14_tick();
    } else if (htim->Instance == TICK_TIMER) {
        app_tick_timer_overflow();
    }
}

void Error_Handler(void) {
    app_error();
}

void system_core_error_handler() {
    app_error();
}

void iwdg_warning_cb(void) {
    crash_dump::save_message(crash_dump::MsgType::IWDGW, 0, nullptr, nullptr);
    trigger_crash_dump();
}

extern "C" void idle_callback() {
    check_isr_stack_overflow();
}

static void enable_trap_on_division_by_zero() {
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk;
}

static void enable_backup_domain() {
    __HAL_RCC_PWR_CLK_ENABLE();
    HAL_PWR_EnableBkUpAccess();
}

static void enable_segger_sysview() {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    SEGGER_SYSVIEW_Conf();
}

static void eeprom_init_i2c() {
    I2C_INIT(eeprom);
}

extern "C" void __libc_init_array(void);

namespace {

/// Prepare EEPROM and initialize the C++ runtime before entering `main_cpp`.
extern "C" void startup_task(void const *) {
    crc32_init();
    i2c::ChannelMutex::static_init();
    eeprom_init_i2c();

    {
        freertos::CriticalSection critical_section;
        st25dv64k_init();

        init_config_store();
        config_store().perform_config_check();
    }

// Configuration must exist before timer 1 and global initialization.
#if BOARD_IS_XBUDDY() || BOARD_IS_XLBUDDY()
    buddy::hw::Configuration::Instance();
#endif

    __libc_init_array();
    main_cpp();
    osThreadTerminate(osThreadGetId());
}

} // namespace

/// Start the RTOS without relying on the not-yet-initialized C++ runtime.
int main() {
    SystemInit();
    HAL_Init();

    system_core_init();
    tick_timer_init();

    setup_isr_stack_overflow_trap();
    enable_trap_on_division_by_zero();
    enable_backup_domain();
    enable_segger_sysview();

    data_exchange_init();

#if PRINTER_IS_PRUSA_iX()
    hw_preinit_turbine_disable();
#endif

    osThreadDef(startup, startup_task, TASK_PRIORITY_STARTUP, 0, 1024 + 512 + 256);
    osThreadCreate(osThread(startup), NULL);
    osKernelStart();
}

#ifdef USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line) {
    app_assert(file, line);
}
#endif
