# Architecture

**Analysis Date:** 2026-06-01

## Pattern Overview

**Overall:** CMake-composed embedded firmware with board/printer feature gates, a FreeRTOS imperative shell, and Marlin as the motion/printing core.

**Key Characteristics:**

- `CMakeLists.txt` creates one `firmware` executable, then `src/CMakeLists.txt` adds board-specific source trees according to `BOARD`, `PRINTER`, and generated option headers from `ProjectOptions.cmake`.
- `src/buddy/main.cpp` is the master-board runtime shell: it initializes HAL/peripherals, creates FreeRTOS tasks, coordinates `TaskDeps`, and delegates printing logic to `app_run()` in `src/common/appmain.cpp`.
- `lib/Marlin/Marlin/src` supplies the motion planner, G-code queue, thermal management, and printer mechanics; Buddy-specific orchestration wraps it through `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, and `src/marlin_stubs`.
- `src/gui`, `src/connect`, `src/transfers`, `src/puppies`, and `src/persistent_stores` are feature/application layers built into the same firmware target when options enable them.
- `src/puppy/dwarf`, `src/puppy/modularbed`, and `src/puppy/xbuddy_extension` are separate firmware personalities selected by `BOARD`, not ordinary modules inside the master-board runtime.

## Layers

**Build, Options, and Target Composition:**

- Purpose: Select printer, board, MCU, bootloader mode, feature flags, generated option headers, subprojects, firmware packaging, and linked libraries.
- Location: `CMakeLists.txt`, `ProjectOptions.cmake`, `CMakePresets.json`, `cmake/Options.cmake`, `cmake/GccArmNoneEabi.cmake`, `utils/build.py`, `utils/bootstrap.py`
- Contains: `firmware` target creation, `BuddyHeaders`, `Marlin_Config`, `FreeRTOS_Config`, `target_sources(...)`, `target_link_libraries(...)`, generated `include/option/*.h` files under the build directory, `.bbf`/`.dfu` packaging hooks.
- Depends on: `lib/CMakeLists.txt`, `lib/AddMarlin.cmake`, `lib/Add*.cmake`, `utils/gen_puppies_descriptor.py`, `utils/pack_fw.py`, `utils/mklittlefs.py`
- Used by: Every source layer through option macros such as `HAS_GUI()`, `HAS_PUPPIES()`, `BUDDY_ENABLE_CONNECT()`, board macros from `include/device/board.h`, and printer macros from `include/printers.h`.

**MCU, Startup, and Device Support:**

- Purpose: Provide startup assembly, linker scripts, CMSIS/HAL setup, interrupt routing, core clock/timer initialization, and MCU-specific peripheral entrypoints.
- Location: `src/device`, `src/device/stm32f4`, `src/device/stm32g0`, `src/puppy/xbuddy_extension`, `include/device`, `include/stm32f4_hal`, `include/stm32g0_hal`
- Contains: Startup sources such as `src/device/stm32f4/startup/stm32f427zitx.s`, linker scripts such as `src/device/stm32f4/linker/stm32f42x_boot.ld`, HAL glue such as `src/device/stm32f4/hal_msp.cpp`, and board interrupt files such as `src/device/stm32f4/interrupts_XBUDDY.cpp`.
- Depends on: STM32 HAL/CMSIS libraries from `lib/Drivers`, FreeRTOS configuration from `src/device/CMakeLists.txt`, and `BuddyHeaders` from `CMakeLists.txt`.
- Used by: `src/buddy/main.cpp`, puppy entrypoints in `src/puppy/dwarf/main.cpp` and `src/puppy/modularbed/main.cpp`, and low-level hardware code in `src/hw`.

**Board Hardware and Peripheral Shell:**

- Purpose: Initialize board GPIO, DMA, ADC, timers, I2C/SPI/UART, USB, filesystems, watchdogs, power, and board-specific hardware configuration.
- Location: `src/buddy`, `src/hw`, `include/buddy`, `include/usb_host`, `include/device`
- Contains: Master-board boot orchestration in `src/buddy/main.cpp`, USB device task in `src/buddy/usb_device.cpp`, USB host integration in `src/buddy/usb_host.cpp`, filesystem mounts in `src/buddy/filesystem.cpp`, hardware configuration in `src/hw/mk4_ix_coreone/hw_configuration.cpp`, `src/hw/xl/hw_configuration.cpp`, and `src/hw/xbuddy_xlbuddy/hw_configuration_common.cpp`.
- Depends on: `src/device`, STM32 HAL, TinyUSB, FatFS, littlefs, libsysbase, generated options, and board macros from `include/device/board.h`.
- Used by: The FreeRTOS startup path in `src/buddy/main.cpp`, application logic in `src/common/appmain.cpp`, GUI display/touch code in `src/gui`, Connect/WUI network setup, and Marlin hardware adapters.

**RTOS and Task Coordination:**

- Purpose: Wrap FreeRTOS primitives, allocate system tasks, coordinate startup readiness, and provide task-safe synchronization helpers.
- Location: `src/freertos`, `src/freertos/include/freertos`, `include/tasks.hpp`, `src/common/tasks.cpp`, `include/buddy/ccm_thread.hpp`
- Contains: Mutex/queue/semaphore wrappers in `src/freertos`, static idle/timer task memory in `src/freertos/system_tasks.cpp`, event-group dependency masks in `include/tasks.hpp`, and CCMRAM thread definition macros in `include/buddy/ccm_thread.hpp`.
- Depends on: `FreeRTOS::FreeRTOS`, CMSIS-OS headers, board memory sections, and generated feature options.
- Used by: `src/buddy/main.cpp`, `src/common/appmain.cpp`, `src/gui/guimain.cpp`, `src/connect/run.cpp`, `src/puppies/puppy_task.cpp`, `src/buddy/usb_device.cpp`, and logging/task code in `src/logging`.

**Printing Core and Marlin Bridge:**

- Purpose: Run Marlin setup/loop, serialize UI/network requests into server-side printing operations, expose events/state to client tasks, and add Prusa-specific G-code handlers.
- Location: `lib/Marlin/Marlin/src`, `lib/AddMarlin.cmake`, `src/common/appmain.cpp`, `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, `src/common/marlin_server_request.hpp`, `src/common/marlin_client_queue.hpp`, `src/marlin_stubs`
- Contains: Marlin source selection in `lib/AddMarlin.cmake`, server loop in `src/common/marlin_server.cpp`, task-bound client registration in `src/common/marlin_client.cpp`, request/event queues in `src/common/marlin_server_request.hpp` and `src/common/marlin_client_queue.hpp`, and Buddy G-code implementations such as `src/marlin_stubs/M862_1.cpp` and `src/marlin_stubs/pause/M600.cpp`.
- Depends on: `lib/Marlin/Marlin/src`, Arduino Core, TMCStepper, FreeRTOS wrappers, `marlin_server_types`, `buddy_utils`, error codes, config store, and feature options.
- Used by: GUI screens in `src/gui`, Connect client in `src/connect`, transfers in `src/transfers`, selftest and feature modules in `src/common/feature`, MMU code in `src/mmu2`, and puppy/toolchanger integration in `src/puppies`.

**Application/Common Domain Layer:**

- Purpose: Own printer application state outside raw Marlin, including config, metrics, sensors, selftest, G-code scanning, media prefetch, safety timers, feature managers, and utility code shared by UI/network paths.
- Location: `src/common`, `src/common/feature`, `src/common/selftest`, `src/common/gcode`, `src/common/marlin_server_types`, `src/module/utils`
- Contains: Main application loop in `src/common/appmain.cpp`, sensor and filament support in `src/common/filament_sensor*.cpp`, metrics in `src/common/metric.cpp`, feature modules such as `src/common/feature/chamber/chamber.cpp`, and pure/shared helper libraries in `src/module/utils`.
- Depends on: Marlin APIs, hardware shell, config store, FreeRTOS wrappers, generated options, logging, and `buddy_utils`.
- Used by: `src/buddy/main.cpp`, `src/gui`, `src/connect`, `src/marlin_stubs`, `src/puppies`, and unit tests under `tests/unit/common`.

**GUI Layer:**

- Purpose: Render display UI, manage screen stack/dialogs, handle input, expose print controls, display errors, and mediate GUI readiness for printing.
- Location: `src/gui`, `src/gui/dialogs`, `src/gui/screen`, `src/gui/menu_item`, `src/gui/footer`, `src/gui/wizard`, `src/guiapi`
- Contains: GUI task loop in `src/gui/guimain.cpp`, screen stack in `src/gui/ScreenHandler.hpp`, fixed-storage screen factory in `src/gui/ScreenFactory.hpp`, screen classes such as `src/gui/screen_home.hpp`, and resolution-specific modules under `src/gui/resolution_240x320` and `src/gui/resolution_480x320`.
- Depends on: `marlin_client` from `src/common/marlin_client.hpp`, config store, `src/common` models, resources, display/touch hardware, generated options, and language translation code in `src/lang`.
- Used by: `src/buddy/main.cpp` via `StartDisplayTask`, user-facing workflows, bootstrap/resource update progress, crash/error display, and GUI unit tests under `tests/unit/gui`.

**Network, Connect, Web UI, and Transfers:**

- Purpose: Provide Prusa Connect client behavior, network-backed printer state/control, downloads, transfer recovery, syslog/metrics transport, and the embedded web UI backend.
- Location: `src/connect`, `src/connect/tls`, `src/transfers`, `src/state`, `src/syslog`, `lib/WUI`
- Contains: Connect task entry in `src/connect/run.cpp`, abstract printer contract in `src/connect/printer.hpp`, Marlin-backed implementation in `src/connect/marlin_printer.cpp`, transfer state machines in `src/transfers`, Connect-visible state mapping in `src/state/printer_state.cpp`, and WUI HTTP implementation in `lib/WUI`.
- Depends on: WUI/LwIP, mbedTLS, hardware RNG, config store, filesystem mounts, `marlin_client`, `marlin_vars`, and generated options `BUDDY_ENABLE_WUI()` and `BUDDY_ENABLE_CONNECT()`.
- Used by: `src/buddy/main.cpp` through `start_network_task(...)` and `StartConnectTask`, Connect/WUI tests in `tests/unit/connect`, `tests/unit/transfers`, and `tests/unit/lib/WUI`.

**Persistent Storage and Filesystem Layer:**

- Purpose: Persist configuration, mount internal/USB/semihosting filesystems, migrate old EEPROM data, and expose POSIX-like file operations through libsysbase devoptabs.
- Location: `src/persistent_stores`, `src/buddy/filesystem*.cpp`, `include/buddy/filesystem*.h`, `lib/libsysbase`
- Contains: Config store entry in `src/persistent_stores/store_instances/config_store/store_instance.cpp`, store definitions/migrations in `src/persistent_stores/store_instances/config_store/store_definition.cpp`, journal backend in `src/persistent_stores/journal/backend.cpp`, USB FatFS mount named `usb` in `src/buddy/filesystem_fatfs.cpp`, internal littlefs mount named `internal` in `src/buddy/filesystem_littlefs_internal.cpp`, and root device listing in `src/buddy/filesystem_root.cpp`.
- Depends on: EEPROM/NFC driver initialization in `src/buddy/main.cpp`, `lib/libsysbase`, littlefs, FatFS, CRC utilities, generated options, and C++ reflection helpers under `include/common`.
- Used by: GUI settings, Connect configuration, print file access, crash dump storage, resources/bootstrap logic, and tests under `tests/unit/persistent_stores`.

**Resources, Localization, and Generated Assets:**

- Purpose: Package web assets, ESP firmware blobs, puppy firmware blobs, MMU firmware, QOI image data, bootloader update resources, and translation data.
- Location: `src/resources`, `src/gui/res`, `src/lang`, `utils/resources`, `utils/translations_and_fonts`
- Contains: Resource image setup in `src/resources/CMakeLists.txt`, bootstrap/hash logic in `src/resources/bootstrap.cpp`, static web files in `src/resources/web`, ESP blobs in `src/resources/esp32` and `src/resources/esp8266`, translation providers in `src/lang/translation_provider_FILE.cpp` and `src/lang/translation_provider_CPUFLASH.cpp`, and `.po` files in `src/lang/po`.
- Depends on: littlefs image CMake helpers in `cmake/Littlefs.cmake`, Python generators in `utils/resources/generate_hash_file.py`, `utils/translations_and_fonts/lang.py`, and generated options for resources/translations.
- Used by: Firmware packaging in `CMakeLists.txt`, GUI image/font access, bootloader/resources bootstrap in `src/buddy/main.cpp`, WUI assets, ESP flashing, and puppy bootload flows.

**Puppy and Expansion-Board Firmware Layer:**

- Purpose: Build and run auxiliary board firmware, bootstrap/flash puppies from master firmware resources, and communicate with Dwarf, ModularBed, and xBuddy Extension devices over Modbus/fifo protocols.
- Location: `src/puppies`, `include/puppies`, `src/puppy/dwarf`, `src/puppy/modularbed`, `src/puppy/shared`, `src/puppy/xbuddy_extension`, `src/puppy/xbuddy_extension_shared`
- Contains: Master-side puppy task in `src/puppies/puppy_task.cpp`, bootloader protocol in `src/puppies/BootloaderProtocol.cpp`, Dwarf abstraction in `src/puppies/Dwarf.cpp`, ModularBed abstraction in `src/puppies/modular_bed.cpp`, Dwarf firmware entrypoint in `src/puppy/dwarf/main.cpp`, ModularBed firmware entrypoint in `src/puppy/modularbed/main.cpp`, and xBuddy Extension firmware target setup in `src/puppy/xbuddy_extension/CMakeLists.txt`.
- Depends on: `lib/liblightmodbus`, `src/common`, Marlin toolchanger APIs, resources packaged by `src/resources/CMakeLists.txt`, and `ExternalProject_Add` flows in `CMakeLists.txt`.
- Used by: XL/iX/COREONE master firmware when `HAS_PUPPIES()`, `HAS_PUPPIES_BOOTLOADER()`, or `HAS_XBUDDY_EXTENSION()` options are enabled.

**Third-Party and Subrepo Libraries:**

- Purpose: Provide firmware dependencies and upstream code kept under repository control.
- Location: `lib`, `lib/Marlin`, `lib/Prusa-Firmware-MMU`, `lib/Prusa-Error-Codes`, `lib/Drivers`, `lib/Middlewares`, `lib/WUI`, `lib/tinyusb`
- Contains: CMake wrappers in `lib/Add*.cmake`, upstream source trees, STM32 HAL/CMSIS, FreeRTOS, TinyUSB, mbedTLS, Prusa error codes, MMU firmware, WUI, TMCStepper, CrashCatcher, and utility libraries.
- Depends on: `lib/CMakeLists.txt` inclusion from root `CMakeLists.txt` and project-specific interface targets such as `BuddyHeaders`.
- Used by: Almost every firmware target through `target_link_libraries(firmware ...)` in `CMakeLists.txt`.

## Data Flow

**Master-Board Boot and Task Startup:**

1. Startup assembly from `src/device/stm32f4/startup` or `src/device/stm32g0/startup` calls `main()` in `src/buddy/main.cpp`.
1. `main()` in `src/buddy/main.cpp` performs minimal `SystemInit()`, `HAL_Init()`, timer/core setup, crash/debug setup, creates the `startup_task`, and starts the FreeRTOS scheduler with `osKernelStart()`.
1. `startup_task()` in `src/buddy/main.cpp` initializes CRC, I2C mutexes, EEPROM/config store via `init_config_store()` in `src/persistent_stores/store_instances/config_store/store_instance.cpp`, runs C/C++ constructors via `__libc_init_array()`, then calls `main_cpp()`.
1. `main_cpp()` in `src/buddy/main.cpp` initializes board peripherals, error-screen fast path, logging, filesystems, resources, USB, ESP flashing, default/display/connect/puppy tasks, and startup dependencies through `TaskDeps` from `include/tasks.hpp`.
1. `StartDefaultTask()` in `src/buddy/main.cpp` calls `app_run()` in `src/common/appmain.cpp`, which waits for dependencies, calls Marlin `setup()`, initializes `marlin_server`, and runs `marlin_server::loop()` forever.

**GUI/Connect Print Command to Marlin Execution:**

1. GUI code in `src/gui/guimain.cpp` and screens such as `src/gui/screen_home.cpp`, or Connect code in `src/connect/marlin_printer.cpp`, initialize a task-bound client through `marlin_client::init()` in `src/common/marlin_client.cpp`.
1. Client calls such as `marlin_client::gcode(...)`, `marlin_client::print_start(...)`, or `marlin_client::FSM_response(...)` create `marlin_server::Request` records from `src/common/marlin_server_request.hpp`.
1. `marlin_server::request_queue` in `src/common/marlin_server.cpp` serializes requests into the default task running `marlin_server::loop()`.
1. `marlin_server::loop()` in `src/common/marlin_server.cpp` calls into Marlin queues and modules under `lib/Marlin/Marlin/src`, updates `marlin_vars`, and sends client events through `marlin_client::ClientQueue` from `src/common/marlin_client_queue.hpp`.
1. GUI and Connect tasks periodically call `marlin_client::loop()` from `src/common/marlin_client.cpp` to receive events, update dialogs/state, and display or report printer progress.

**Network Download and Remote Control Flow:**

1. `src/buddy/main.cpp` waits for ESP flashing through `TaskDeps::Tasks::network`, then starts WUI/networking with `start_network_task(...)` from `lib/WUI`.
1. `StartConnectTask()` in `src/buddy/main.cpp` calls `connect_client::run()` in `src/connect/run.cpp`.
1. `src/connect/run.cpp` builds a `connect_client::Connect` client with a `connect_client::MarlinPrinter` adapter from `src/connect/marlin_printer.cpp`.
1. `src/connect/marlin_printer.cpp` reads printer state from `marlin_vars`, `config_store()`, WUI/netdev APIs, filesystem paths, and feature modules, then maps remote commands into `marlin_client` calls.
1. Download and file-transfer paths use `src/transfers/download.cpp`, `src/transfers/transfer.cpp`, and filesystem mounts from `src/buddy/filesystem.cpp`, while printer state for remote consumers is normalized in `src/state/printer_state.cpp`.

**Puppy Bootstrap and Runtime Flow:**

1. Root `CMakeLists.txt` uses `ExternalProject_Add` to build Dwarf, ModularBed, and xBuddy Extension firmware when `HAS_PUPPIES_BOOTLOADER` and related options are active.
1. `src/resources/CMakeLists.txt` embeds generated puppy firmware binaries as `/puppies/fw-dwarf.bin`, `/puppies/fw-modularbed.bin`, or `/puppies/fw-xbuddy-extension.bin`.
1. `src/buddy/main.cpp` opens the puppy UART, starts `buddy::puppies::start_puppy_task()` from `src/puppies/puppy_task.cpp`, and coordinates readiness through `TaskDeps`.
1. `src/puppies/puppy_task.cpp` runs `PuppyBootstrap` from `src/puppies/PuppyBootstrap.cpp`, verifies connected puppies, performs initial scans through `src/puppies/Dwarf.cpp` and `src/puppies/modular_bed.cpp`, then runs periodic refresh/fifo/toolchanger work.
1. Dedicated puppy firmware entrypoints in `src/puppy/dwarf/main.cpp`, `src/puppy/modularbed/main.cpp`, and `src/puppy/xbuddy_extension/main.cpp` run their own HAL/FreeRTOS/application loops when those boards are built directly.

**Persistent Settings and Resource Flow:**

1. `startup_task()` in `src/buddy/main.cpp` initializes EEPROM/NFC access before constructors, then calls `init_config_store()` in `src/persistent_stores/store_instances/config_store/store_instance.cpp`.
1. `config_store()` uses journal storage in `src/persistent_stores/journal/backend.cpp`, store definitions in `src/persistent_stores/store_instances/config_store/store_definition.cpp`, and storage drivers in `src/persistent_stores/storage_drivers/eeprom_storage.cpp`.
1. `filesystem_init()` in `src/buddy/filesystem.cpp` mounts `/usb` through `src/buddy/filesystem_fatfs.cpp`, `/internal` through `src/buddy/filesystem_littlefs_internal.cpp`, and optional `/semihosting` through `src/buddy/filesystem_semihosting.cpp`.
1. `resources_update()` in `src/buddy/main.cpp` validates resource revisions from generated headers under the build tree and bootstraps missing resources through `src/resources/bootstrap.cpp`.
1. UI, Connect, transfers, crash dumps, and MMU/ESP update flows consume these filesystems and resources through ordinary POSIX-like calls provided by `lib/libsysbase`.

**State Management:**

- Startup dependencies use FreeRTOS event bits in `include/tasks.hpp` and initialization in `src/common/tasks.cpp`.
- Printing state is centralized around `marlin_server::server_t`, request/event queues, and `marlin_vars` in `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, and `src/common/marlin_vars.cpp`.
- GUI navigation state uses the `Screens` stack in `src/gui/ScreenHandler.hpp` and fixed storage from `src/gui/ScreenFactory.hpp`.
- Persistent configuration uses `config_store()` from `src/persistent_stores/store_instances/config_store/store_instance.hpp`.
- Network-visible device state is mapped in `src/state/printer_state.cpp`.
- Compile-time state is generated from `ProjectOptions.cmake` into build-tree `include/option/*.h` headers consumed through `#include <option/...>`.

## Key Abstractions

**`firmware` Target:**

- Purpose: Aggregate selected sources into one embedded image for a selected `BOARD`/`PRINTER`.
- Examples: `CMakeLists.txt`, `src/CMakeLists.txt`, `src/buddy/CMakeLists.txt`, `src/common/CMakeLists.txt`, `src/gui/CMakeLists.txt`
- Pattern: Global executable assembled through nested `target_sources(firmware ...)` and option-gated `add_subdirectory(...)`.

**Generated Feature Options:**

- Purpose: Convert CMake feature decisions into C/C++ preprocessor macros and `option::` constants.
- Examples: `ProjectOptions.cmake`, `cmake/Options.cmake`, `include/option/option_boolean.h.in`, generated build-tree `include/option/has_gui.h`
- Pattern: CMake functions `define_boolean_option(...)` and `define_enum_option(...)` generate headers consumed by source files such as `src/buddy/main.cpp`.

**Board and Printer Macros:**

- Purpose: Encapsulate board/printer identity checks and keep source conditions readable.
- Examples: `include/device/board.h`, `include/printers.h`, `include/device/mcu.h`
- Pattern: `BOARD_IS_*()`, `PRINTER_IS_PRUSA_*()`, and `MCU_IS_*()` macro helpers generated from compile definitions in `CMakeLists.txt`.

**Task Dependencies:**

- Purpose: Model readiness relationships between startup components and runtime tasks.
- Examples: `include/tasks.hpp`, `src/common/tasks.cpp`, `src/buddy/main.cpp`, `src/gui/guimain.cpp`, `src/puppies/puppy_task.cpp`
- Pattern: FreeRTOS event group masks with `TaskDeps::wait(...)` and `TaskDeps::provide(...)`.

**Marlin Server/Client Boundary:**

- Purpose: Keep Marlin operations serialized on the default task while GUI, Connect, and other tasks submit requests safely.
- Examples: `src/common/marlin_server.hpp`, `src/common/marlin_client.hpp`, `src/common/marlin_server_request.hpp`, `src/common/marlin_client_queue.hpp`
- Pattern: Single server loop plus per-task client IDs, one-slot request queue, event masks, and acknowledgement events.

**Screen Stack and Static Screen Allocation:**

- Purpose: Manage GUI screens without heap allocation and preserve navigation state.
- Examples: `src/gui/ScreenFactory.hpp`, `src/gui/ScreenHandler.hpp`, `src/gui/screen_home.hpp`, `src/gui/dialogs/DialogHandler.cpp`
- Pattern: `ScreenFactory::Creator` creates screens inside fixed storage, while `Screens` keeps a bounded stack of creators and init state.

**Config Store and Journal:**

- Purpose: Persist typed printer settings and migrate old EEPROM/config versions.
- Examples: `src/persistent_stores/store_instances/config_store/store_definition.hpp`, `src/persistent_stores/store_instances/config_store/store_instance.cpp`, `src/persistent_stores/journal/backend.cpp`
- Pattern: Typed store items backed by append-only journal transactions, CRC validation, bank selection, and migration hooks.

**Logging Components and Destinations:**

- Purpose: Define compile-time/log-section components and runtime destinations for RTT, syslog, USB, file, and buffer logging.
- Examples: `src/logging/include/logging/log.hpp`, `src/logging/log.cpp`, `src/buddy/logging.cpp`, `src/logging/CMakeLists.txt`
- Pattern: `LOG_COMPONENT_DEF(...)` places components in a linker section, and `logging::Destination` instances are registered at runtime.

**Filesystem Devices:**

- Purpose: Expose internal flash, USB, BBF, semihosting, and root directory through libsysbase/newlib-style operations.
- Examples: `src/buddy/filesystem.cpp`, `src/buddy/filesystem_fatfs.cpp`, `src/buddy/filesystem_littlefs_internal.cpp`, `src/buddy/filesystem_root.cpp`, `lib/libsysbase`
- Pattern: `devoptab_t` device implementations registered with `AddDevice(...)` and used by POSIX-like file APIs.

**Puppy Devices and Bootloader Protocol:**

- Purpose: Represent auxiliary boards, flash them, verify fingerprints, refresh registers, and recover after communication faults.
- Examples: `src/puppies/PuppyBootstrap.cpp`, `src/puppies/PuppyModbus.cpp`, `src/puppies/Dwarf.cpp`, `src/puppies/modular_bed.cpp`, `src/puppies/puppy_task.cpp`
- Pattern: Master-side task owns Modbus scanning/bootstrap/runtime refresh and exposes device-specific classes for Dwarf, ModularBed, and xBuddy Extension.

## Entry Points

**Build Wrapper:**

- Location: `utils/build.py`
- Triggers: Developer or CI invokes `python utils/build.py`.
- Responsibilities: Bootstrap dependencies, expand presets from `utils/presets`, configure CMake builds, and place products under `build/products`.

**CMake Root:**

- Location: `CMakeLists.txt`
- Triggers: `cmake` configure/generate step or `utils/build.py`.
- Responsibilities: Define project language/version, global compiler/linker flags, interface targets, Marlin and third-party config targets, puppy external projects, tests for host builds, firmware packaging, and final firmware link libraries.

**Source Composition:**

- Location: `src/CMakeLists.txt`
- Triggers: Root `CMakeLists.txt` after `add_executable(firmware)`.
- Responsibilities: Add board-specific source directories, including master-board modules, puppy firmware modules, or xBuddy Extension firmware modules.

**Master-Board Runtime:**

- Location: `src/buddy/main.cpp`
- Triggers: MCU reset vector/startup assembly.
- Responsibilities: Minimal pre-RTOS setup, FreeRTOS scheduler startup, C++ runtime initialization in `startup_task`, board/peripheral initialization in `main_cpp`, task creation, bootstrap/error-screen flow, resources/bootloader updates, and dependency coordination.

**Default Printing Task:**

- Location: `src/common/appmain.cpp`
- Triggers: `StartDefaultTask()` in `src/buddy/main.cpp`.
- Responsibilities: Wait for startup dependencies, set up Marlin logging, call Marlin `setup()`, initialize `marlin_server`, mark default task ready, and run `marlin_server::loop()`.

**Display Task:**

- Location: `src/gui/guimain.cpp`
- Triggers: `StartDisplayTask()` in `src/buddy/main.cpp`.
- Responsibilities: Initialize GUI/display, show bootstrap/error/home screens, register as a Marlin client, process screen/dialog loops, and signal GUI readiness.

**Connect Task:**

- Location: `src/connect/run.cpp`
- Triggers: `StartConnectTask()` or `StartConnectTaskError()` in `src/buddy/main.cpp`.
- Responsibilities: Create `Connect` with either `MarlinPrinter` or `ErrorPrinter`, then run the Connect client loop.

**Puppy Master Task:**

- Location: `src/puppies/puppy_task.cpp`
- Triggers: `buddy::puppies::start_puppy_task()` in `src/buddy/main.cpp`.
- Responsibilities: Wait for ESP flashing, bootstrap puppies, verify/scan connected boards, signal readiness, and maintain periodic device refresh.

**Dwarf Firmware Runtime:**

- Location: `src/puppy/dwarf/main.cpp`
- Triggers: Dwarf board reset vector/startup assembly for `BOARD=DWARF`.
- Responsibilities: Minimal HAL setup, FreeRTOS scheduler startup, C++ runtime initialization, and Dwarf startup task dispatch.

**ModularBed Firmware Runtime:**

- Location: `src/puppy/modularbed/main.cpp`
- Triggers: ModularBed board reset vector/startup assembly for `BOARD=MODULARBED`.
- Responsibilities: HAL/system setup, watchdog setup, Modbus register/protocol initialization, measurement/PWM/control logic initialization, and FreeRTOS scheduler startup.

**xBuddy Extension Firmware Runtime:**

- Location: `src/puppy/xbuddy_extension/main.cpp`
- Triggers: xBuddy Extension board reset vector/startup assembly for `BOARD=XBUDDY_EXTENSION`.
- Responsibilities: STM32H5 firmware entrypoint compiled with `src/puppy/xbuddy_extension/CMakeLists.txt`, shared MMU protocol support, extension variant selection, and extension app loop.

**Unit Test Entry:**

- Location: `tests/unit/CMakeLists.txt`
- Triggers: Non-cross-compiling CMake configure with `UNITTESTS_ENABLE`.
- Responsibilities: Define `UNITTESTS`, enable RTTI for tests, create `catch_main`, provide `add_catch_test(...)`, and include test subdirectories.

**Integration Test Entry:**

- Location: `tests/integration/conftest.py`
- Triggers: `pytest tests/integration --firmware <firmware.bin to test>`.
- Responsibilities: Configure simulator-driven integration tests for supported firmware builds and provide pytest fixtures/actions.

## Error Handling

**Strategy:** Fail fast into safe state, crash dump, BSOD/redscreen GUI, and typed error codes where available.

**Patterns:**

- `src/buddy/main.cpp` routes startup failures, watchdog warnings, HAL errors, asserts, and error-screen fast path through `Error_Handler()`, `app_error()`, `init_error_screen()`, `crash_dump::save_message(...)`, and `trigger_crash_dump()`.
- `include/stm32f4_hal/FreeRTOSConfig.h` and `include/stm32g0_hal/FreeRTOSConfig.h` map FreeRTOS `configASSERT` failures into `_bsod(...)` or `fatal_error(...)`.
- `src/common/crash_dump/CMakeLists.txt` wires CrashCatcher sources into master-board firmware; `src/puppy/dwarf/CMakeLists.txt` and `src/puppy/modularbed/CMakeLists.txt` wire ARMv6-M CrashCatcher sources for puppy boards.
- `src/common/safe_state.cpp`, `src/puppy/modularbed/main.cpp`, and `src/puppy/dwarf/main.cpp` push hardware into safe outputs before hard failure loops.
- `lib/Prusa-Error-Codes` and generated `error_codes` targets are linked from `CMakeLists.txt`; user/Connect-visible mappings appear in `src/state/printer_state.cpp`.
- `src/puppies/PuppyBootstrap.cpp`, `src/puppies/Dwarf.cpp`, and `src/puppies/modular_bed.cpp` convert auxiliary-board failures into `fatal_error(ErrCode::...)` or crash-dump download/report flows.

## Cross-Cutting Concerns

**Logging:** Use `LOG_COMPONENT_DEF(...)` and `LOG_COMPONENT_REF(...)` from `src/logging/include/logging/log.hpp`; initialize master-board destinations in `src/buddy/logging.cpp`; add destination-specific code under `src/logging/log_dest_*.cpp`; keep component lists discoverable through linker sections defined by `src/logging/log.cpp`.

**Validation:** Encode build-time validity in `ProjectOptions.cmake`, `include/device/board.h`, `include/printers.h`, and generated `include/option/*.h`; keep runtime request validation at boundaries such as `src/common/marlin_client.cpp`, config validation/migration in `src/persistent_stores/store_instances/config_store/store_definition.cpp`, and filesystem error mapping in `src/buddy/filesystem_fatfs.cpp`.

**Authentication:** Connect credentials and proxy/TLS configuration live in `connect_client::Printer::Config` in `src/connect/printer.hpp` and are loaded by `src/connect/marlin_printer.cpp`; the firmware architecture has no central web/API middleware layer in `src`.

**Memory Management:** Prefer static task/storage patterns in firmware paths: `src/freertos/system_tasks.cpp` provides static FreeRTOS task memory, `include/buddy/ccm_thread.hpp` allocates task buffers in CCMRAM, `src/gui/ScreenFactory.hpp` uses bounded static screen storage, and `src/common/static_storage.cpp`/`include/common/static_storage.hpp` provide shared static storage helpers.

**Generated Code and Assets:** Treat build-tree headers under `include/option` and resource revision headers from `src/resources/CMakeLists.txt` as generated; source definitions belong in `ProjectOptions.cmake`, `src/resources`, `src/lang/po`, and `src/gui/res`.

______________________________________________________________________

*Architecture analysis: 2026-06-01*
