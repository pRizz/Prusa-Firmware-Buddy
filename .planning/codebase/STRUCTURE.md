# Codebase Structure

**Analysis Date:** 2026-06-01

## Directory Layout

```text
Prusa-Firmware-Buddy/
├── CMakeLists.txt              # Root firmware target, global build configuration, packaging, tests, and library wiring
├── ProjectOptions.cmake        # Printer/board/feature option matrix and generated option-header definitions
├── CMakePresets.json           # Development configure presets for printers, boards, bootloader variants, tests, and host tools
├── cmake/                      # CMake helper modules, toolchain files, version resolution, littlefs packaging
├── include/                    # Public/shared headers and firmware configuration headers consumed across source trees
├── src/                        # Buddy firmware source, board startup, common app code, GUI, Connect, puppies, resources
├── lib/                        # In-repo third-party and subrepo dependencies with CMake adapters
├── tests/                      # Unit, module, integration, and host-side stubs
├── utils/                      # Python/build/debug/resource/translations/simulator tooling
├── doc/                        # Developer docs for logging, metrics, G-code, editors, EEPROM, timers, and packaging
├── .dependencies/              # Bootstrapped toolchains, bootloaders, simulators, and firmware blobs
└── .planning/codebase/         # Generated codebase intelligence docs
```

## Directory Purposes

**Root Build Files:**

- Purpose: Configure and compose all firmware builds.
- Contains: `CMakeLists.txt`, `ProjectOptions.cmake`, `CMakePresets.json`, `version.txt`, `requirements.txt`, `pyproject.toml`
- Key files: `CMakeLists.txt` owns `firmware`, `BuddyHeaders`, `Marlin_Config`, packaging, and final link libraries; `ProjectOptions.cmake` owns `PRINTER`, `BOARD`, feature flags, and option headers.

**`cmake`:**

- Purpose: Provide project-specific CMake helpers and cross-compilation toolchains.
- Contains: Toolchains, version logic, option-generation helpers, littlefs image helpers, target utilities.
- Key files: `cmake/GccArmNoneEabi.cmake`, `cmake/AnyGccArmNoneEabi.cmake`, `cmake/Options.cmake`, `cmake/Littlefs.cmake`, `cmake/ProjectVersion.cmake`, `cmake/Utilities.cmake`

**`include`:**

- Purpose: Shared headers that act as public firmware interfaces, generated-option include roots, board/printer macros, HAL configuration, and subsystem APIs.
- Contains: Board headers in `include/device`, firmware APIs in `include/buddy`, option templates in `include/option`, peripheral configs in `include/stm32f4_hal` and `include/stm32g0_hal`, and subsystem headers such as `include/puppies`, `include/resources`, and `include/usb_host`.
- Key files: `include/printers.h`, `include/tasks.hpp`, `include/device/board.h`, `include/device/mcu.h`, `include/buddy/main.h`, `include/option/option_boolean.h.in`

**`src`:**

- Purpose: Main firmware implementation and board/personality-specific source selection.
- Contains: Build composition in `src/CMakeLists.txt`, master-board runtime in `src/buddy`, common application code in `src/common`, GUI in `src/gui`, Connect/network code in `src/connect`, hardware in `src/hw`, device startup in `src/device`, and puppy firmware in `src/puppy`.
- Key files: `src/CMakeLists.txt`, `src/buddy/main.cpp`, `src/common/appmain.cpp`, `src/common/marlin_server.cpp`, `src/gui/guimain.cpp`, `src/connect/run.cpp`, `src/puppies/puppy_task.cpp`

**`src/buddy`:**

- Purpose: Master-board runtime shell and board services.
- Contains: Boot/task orchestration, USB host/device, filesystems, ESP flashing, logging init, timing/syscalls, FatFS/littlefs integration.
- Key files: `src/buddy/main.cpp`, `src/buddy/CMakeLists.txt`, `src/buddy/usb_device.cpp`, `src/buddy/usb_host.cpp`, `src/buddy/filesystem.cpp`, `src/buddy/filesystem_fatfs.cpp`, `src/buddy/filesystem_littlefs_internal.cpp`, `src/buddy/esp_flash_task.cpp`

**`src/common`:**

- Purpose: Application logic shared across UI/network/printing flows.
- Contains: Marlin server/client bridge, app loop, metrics, config helpers, sensors, filesystem utilities, selftest, media prefetch, G-code helpers, feature modules, and typed shared models.
- Key files: `src/common/CMakeLists.txt`, `src/common/appmain.cpp`, `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, `src/common/marlin_vars.cpp`, `src/common/tasks.cpp`, `src/common/feature/CMakeLists.txt`, `src/common/marlin_server_types/CMakeLists.txt`

**`src/common/feature`:**

- Purpose: Feature-scoped domain/application modules for printer behavior that is not raw Marlin or pure GUI.
- Contains: Feature directories such as `src/common/feature/chamber`, `src/common/feature/chamber_filtration`, `src/common/feature/cancel_object`, `src/common/feature/ramming`, `src/common/feature/safety_timer`, `src/common/feature/xbuddy_extension`.
- Key files: `src/common/feature/CMakeLists.txt`, `src/common/feature/chamber/chamber.cpp`, `src/common/feature/print_status_message/print_status_message_mgr.cpp`, `src/common/feature/ramming/ramming_sequence.cpp`

**`src/feature`:**

- Purpose: Higher-level feature slices that include both non-GUI and GUI/G-code pieces.
- Contains: `src/feature/gearbox_alignment`, `src/feature/door_sensor_calibration`, `src/feature/nozzle_cleaner`.
- Key files: `src/feature/CMakeLists.txt`, `src/feature/gearbox_alignment/gcode_gearbox_alignment.cpp`, `src/feature/gearbox_alignment/screen_gearbox_alignment.cpp`, `src/feature/door_sensor_calibration/screen_door_sensor_calibration.cpp`

**`src/gui`:**

- Purpose: Display application, screens, dialogs, menu items, resources, and resolution-specific UI.
- Contains: Screen classes, menu items, dialogs, GUI loops, screen stack, footers, wizards, display resources, resolution branches.
- Key files: `src/gui/CMakeLists.txt`, `src/gui/guimain.cpp`, `src/gui/ScreenFactory.hpp`, `src/gui/ScreenHandler.hpp`, `src/gui/screen_home.cpp`, `src/gui/dialogs/CMakeLists.txt`, `src/gui/menu_item/CMakeLists.txt`, `src/gui/resolution_240x320/CMakeLists.txt`, `src/gui/resolution_480x320/CMakeLists.txt`

**`src/guiapi`:**

- Purpose: Lower-level GUI API support compiled with GUI builds.
- Contains: GUI API headers under `src/guiapi/include` and implementation under `src/guiapi/src`.
- Key files: `src/guiapi/CMakeLists.txt`, `src/guiapi/src/CMakeLists.txt`

**`src/connect`:**

- Purpose: Prusa Connect client and remote printer adapter.
- Contains: Connect runtime, command parsing, status rendering, TLS/socket wrappers, printer abstraction, Marlin-backed printer implementation, error-printer implementation.
- Key files: `src/connect/CMakeLists.txt`, `src/connect/run.cpp`, `src/connect/connect.cpp`, `src/connect/printer.hpp`, `src/connect/marlin_printer.cpp`, `src/connect/error_printer.cpp`, `src/connect/tls/CMakeLists.txt`

**`src/transfers`:**

- Purpose: Network/file transfer and download state handling.
- Contains: Download implementation, partial-file tracking, file checks, transfer recovery, transfer monitor, decrypted transfers.
- Key files: `src/transfers/CMakeLists.txt`, `src/transfers/download.cpp`, `src/transfers/transfer.cpp`, `src/transfers/partial_file.cpp`, `src/transfers/transfer_recovery.cpp`

**`src/state` and `src/syslog`:**

- Purpose: Network-visible printer state and syslog transport.
- Contains: Printer state mapping in `src/state/printer_state.cpp` and syslog transport in `src/syslog/syslog_transport.cpp`.
- Key files: `src/state/CMakeLists.txt`, `src/state/printer_state.cpp`, `src/state/printer_state.hpp`, `src/syslog/CMakeLists.txt`, `src/syslog/syslog_transport.cpp`

**`src/device`:**

- Purpose: MCU-specific startup, linker scripts, CMSIS/HAL glue, interrupts, and peripheral declarations.
- Contains: `src/device/stm32f4`, `src/device/stm32g0`, startup assembly, linker scripts, HAL MSP, peripheral setup, board-specific interrupts.
- Key files: `src/device/CMakeLists.txt`, `src/device/stm32f4/CMakeLists.txt`, `src/device/stm32f4/linker/stm32f42x_boot.ld`, `src/device/stm32f4/startup/stm32f427zitx.s`, `src/device/stm32g0/CMakeLists.txt`, `src/device/stm32g0/linker/stm32g070rb_boot.ld`

**`src/hw`:**

- Purpose: Hardware components above raw MCU HAL and below application features.
- Contains: Board hardware configuration, USB-C controller, I/O expander, touchscreen driver, accelerometer support, serial buffering, board-specific config branches.
- Key files: `src/hw/CMakeLists.txt`, `src/hw/FUSB302B.cpp`, `src/hw/TCA6408A.cpp`, `src/hw/touchscreen/touchscreen.cpp`, `src/hw/mk4_ix_coreone/hw_configuration.cpp`, `src/hw/xl/hw_configuration.cpp`, `src/hw/xbuddy_xlbuddy/hw_configuration_common.cpp`

**`src/freertos`:**

- Purpose: C++ wrappers around FreeRTOS primitives and system task memory.
- Contains: Mutexes, queues, semaphores, timing, critical sections, wait conditions, static idle/timer task allocation.
- Key files: `src/freertos/CMakeLists.txt`, `src/freertos/system_tasks.cpp`, `src/freertos/queue.cpp`, `src/freertos/mutex.cpp`, `src/freertos/include/freertos/queue.hpp`

**`src/logging`:**

- Purpose: Runtime logging framework and board-specific destinations.
- Contains: Log component definitions, runtime destination registry, RTT/file/syslog/USB/buffer sinks, logging task.
- Key files: `src/logging/CMakeLists.txt`, `src/logging/include/logging/log.hpp`, `src/logging/log.cpp`, `src/logging/log_task.cpp`, `src/logging/log_dest_syslog.cpp`, `src/logging/log_dest_usb.cpp`

**`src/marlin_stubs`:**

- Purpose: Buddy-specific Marlin configuration and G-code command implementations.
- Contains: Printer-specific Marlin configuration directories, G/M-code handlers, pause/sdcard/host feature stubs, skippable G-code support.
- Key files: `src/marlin_stubs/CMakeLists.txt`, `src/marlin_stubs/M862_1.cpp`, `src/marlin_stubs/M997.cpp`, `src/marlin_stubs/pause/M600.cpp`, `src/marlin_stubs/host/M115.cpp`, `src/marlin_stubs/MK4/configuration.hpp`

**`src/mmu2`:**

- Purpose: Buddy-side MMU integration and Modbus-related MMU support.
- Contains: MMU FSM, maintenance, communication and support code selected when `HAS_MMU2`.
- Key files: `src/mmu2/CMakeLists.txt`, `src/mmu2/mmu2_fsm.hpp`, `src/mmu2/maintenance.hpp`

**`src/module`:**

- Purpose: Add-library style reusable modules separated from the global `firmware` source aggregation.
- Contains: `buddy_utils` object library and reusable helpers/filters.
- Key files: `src/module/CMakeLists.txt`, `src/module/utils/CMakeLists.txt`, `src/module/utils/utils/callback_hook.hpp`, `src/module/utils/utils/mutex_atomic.hpp`, `src/module/utils/filters/median_filter.cpp`

**`src/persistent_stores`:**

- Purpose: Typed persistent storage and EEPROM journal backend.
- Contains: Config store instance, definitions, migrations, journal backend, storage drivers, no-backend fallback.
- Key files: `src/persistent_stores/CMakeLists.txt`, `src/persistent_stores/store_instances/config_store/store_instance.cpp`, `src/persistent_stores/store_instances/config_store/store_definition.cpp`, `src/persistent_stores/journal/backend.cpp`, `src/persistent_stores/storage_drivers/eeprom_storage.cpp`

**`src/resources`:**

- Purpose: Build resource images and runtime resource bootstrap/hash support.
- Contains: ESP blobs, WUI static files, bootloader update resources, MMU firmware resource conversion, resource hash headers, QOI resource generation.
- Key files: `src/resources/CMakeLists.txt`, `src/resources/bootstrap.cpp`, `src/resources/hash.cpp`, `src/resources/QoiGenerator.cmake`, `src/resources/web/index.html`, `src/resources/esp32/uart_wifi.bin`, `src/resources/esp8266/uart_wifi.bin`

**`src/lang`:**

- Purpose: Translation and text formatting support.
- Contains: `.po` files, translation providers, string hashing, UTF-8 string helpers, generated hash-table dependency definitions.
- Key files: `src/lang/CMakeLists.txt`, `src/lang/translator.cpp`, `src/lang/translation_provider_FILE.cpp`, `src/lang/translation_provider_CPUFLASH.cpp`, `src/lang/po/Prusa-Firmware-Buddy.pot`

**`src/puppies` and `include/puppies`:**

- Purpose: Master-board abstractions for auxiliary boards.
- Contains: Puppy bootstrap, Modbus bus, Dwarf/ModularBed/xBuddy Extension abstractions, crash dump download, time sync, fifo encoding/decoding.
- Key files: `src/puppies/CMakeLists.txt`, `src/puppies/puppy_task.cpp`, `src/puppies/PuppyBootstrap.cpp`, `src/puppies/PuppyModbus.cpp`, `src/puppies/Dwarf.cpp`, `src/puppies/modular_bed.cpp`, `include/puppies/PuppyBootstrap.hpp`

**`src/puppy`:**

- Purpose: Firmware source for auxiliary boards when built as their own `BOARD`.
- Contains: Dwarf firmware in `src/puppy/dwarf`, ModularBed firmware in `src/puppy/modularbed`, shared puppy runtime in `src/puppy/shared`, xBuddy Extension firmware in `src/puppy/xbuddy_extension`, shared xBuddy Extension headers in `src/puppy/xbuddy_extension_shared`.
- Key files: `src/puppy/dwarf/main.cpp`, `src/puppy/dwarf/CMakeLists.txt`, `src/puppy/modularbed/main.cpp`, `src/puppy/modularbed/CMakeLists.txt`, `src/puppy/xbuddy_extension/CMakeLists.txt`, `src/puppy/xbuddy_extension/main.cpp`

**`src/bootloader`:**

- Purpose: Firmware-side bootloader update support.
- Contains: Bootloader update logic and headers used when bootloader resources are enabled.
- Key files: `src/bootloader/CMakeLists.txt`, `src/bootloader/bootloader.cpp`, `src/bootloader/bootloader_update.cpp`, `include/bootloader/bootloader.hpp`

**`src/version`:**

- Purpose: Version constants exposed to firmware.
- Contains: Version object target and public version header.
- Key files: `src/version/CMakeLists.txt`, `src/version/include/version/version.hpp`

**`lib`:**

- Purpose: Third-party dependencies and subrepos kept in-tree.
- Contains: Marlin, Prusa MMU firmware, Prusa error codes, STM32 drivers, FreeRTOS middlewares, TinyUSB, WUI, mbedTLS, CrashCatcher, TMCStepper, and utility libraries.
- Key files: `lib/CMakeLists.txt`, `lib/AddMarlin.cmake`, `lib/Marlin/Marlin/src/Marlin.cpp`, `lib/Prusa-Firmware-MMU/src/CMakeLists.txt`, `lib/WUI/CMakeLists.txt`, `lib/Drivers/AddStm32f4Hal.cmake`

**`tests`:**

- Purpose: Host-side unit tests, module tests, integration tests, and stubs.
- Contains: Catch2 unit tests under `tests/unit`, pytest simulator integration under `tests/integration`, Connect module tests under `tests/module/Connect`, and host stubs under `tests/stubs`.
- Key files: `tests/CMakeLists.txt`, `tests/unit/CMakeLists.txt`, `tests/unit/test_main.cpp`, `tests/unit/README.md`, `tests/integration/README.md`, `tests/integration/conftest.py`, `tests/stubs/FreeRTOS/CMakeLists.txt`

**`utils`:**

- Purpose: Developer tooling, dependency bootstrap, build orchestration, generated assets, simulator utilities, debug support, and packaging tools.
- Contains: Build/bootstrap scripts, QOI/png/font/translation generators, BBF/DFU tools, simulator wrappers, GDB helpers, metrics/logging containers, C project generation.
- Key files: `utils/build.py`, `utils/bootstrap.py`, `utils/pack_fw.py`, `utils/mklittlefs.py`, `utils/qoi_packer.py`, `utils/translations_and_fonts/lang.py`, `utils/simulator/simulator.py`

**`doc`:**

- Purpose: Human documentation for subsystem behavior and development workflows.
- Contains: Logging, metrics, G-code, timers, EEPROM, BBF packaging, editor setup, debugging/profiling, subrepo workflow.
- Key files: `doc/logging.md`, `doc/metrics.md`, `doc/gcode.md`, `doc/timers.md`, `doc/eeprom.txt`, `doc/bbf.md`, `doc/subrepo.md`

## Key File Locations

**Entry Points:**

- `utils/build.py`: High-level multi-preset build wrapper used from `README.md`.
- `CMakeLists.txt`: Root CMake entry that creates `firmware`, imports libraries, adds `src`, and packages `.bin`, `.bbf`, and `.dfu` outputs.
- `src/CMakeLists.txt`: Board-specific source-directory dispatcher for master boards, Dwarf, ModularBed, xBuddy Extension, and XL dev kit.
- `src/buddy/main.cpp`: Master-board runtime entrypoint and FreeRTOS task orchestration.
- `src/common/appmain.cpp`: Default task and Marlin server loop entrypoint.
- `src/gui/guimain.cpp`: Display task loop and GUI bootstrap/home flow.
- `src/connect/run.cpp`: Connect task entrypoint.
- `src/puppies/puppy_task.cpp`: Master-side puppy bootstrap/runtime task.
- `src/puppy/dwarf/main.cpp`: Dwarf firmware entrypoint.
- `src/puppy/modularbed/main.cpp`: ModularBed firmware entrypoint.
- `src/puppy/xbuddy_extension/main.cpp`: xBuddy Extension firmware entrypoint.

**Configuration:**

- `ProjectOptions.cmake`: Printer, board, MCU, feature, resources, translations, GUI, puppy, and network option matrix.
- `CMakePresets.json`: Preset names for COREONE, MINI, MK4, MK3.5, iX, XL, puppy boards, tests, and host tools.
- `cmake/Options.cmake`: `define_boolean_option(...)` and `define_enum_option(...)` helpers that generate option headers.
- `include/device/board.h`: Board identity macros.
- `include/printers.h`: Printer identity macros.
- `include/device/mcu.h`: MCU-family macros based on generated `option/mcu.h`.
- `include/stm32f4_hal/FreeRTOSConfig.h`: STM32F4 FreeRTOS configuration and assert mapping.
- `include/stm32g0_hal/FreeRTOSConfig.h`: STM32G0 FreeRTOS configuration and assert mapping.

**Core Logic:**

- `lib/AddMarlin.cmake`: Marlin source selection by feature/board and `Marlin` target setup.
- `src/common/marlin_server.cpp`: Serialized server-side print state and Marlin request handling.
- `src/common/marlin_client.cpp`: Task-local client registration and request submission API.
- `src/common/marlin_server_request.hpp`: Request record and request-flag contract between clients and server.
- `src/common/marlin_client_queue.hpp`: Client event queue contract.
- `src/common/marlin_vars.cpp`: Shared Marlin variable snapshot implementation.
- `src/persistent_stores/store_instances/config_store/store_definition.cpp`: Typed config store behavior and migrations.
- `src/persistent_stores/journal/backend.cpp`: Journaled persistent storage backend.
- `src/connect/marlin_printer.cpp`: Connect adapter over Marlin/config/filesystem/network state.
- `src/gui/ScreenHandler.hpp`: GUI screen stack.
- `src/gui/ScreenFactory.hpp`: Static screen allocation.

**Hardware and Peripherals:**

- `src/device/stm32f4/CMakeLists.txt`: STM32F4 startup/linker/peripheral source selection.
- `src/device/stm32g0/CMakeLists.txt`: STM32G0 startup/linker/peripheral source selection.
- `src/hw/CMakeLists.txt`: Board hardware component selection.
- `src/buddy/usb_device.cpp`: TinyUSB CDC device task.
- `src/buddy/usb_host.cpp`: USB host and media mount flow.
- `src/buddy/filesystem.cpp`: Filesystem initialization.
- `src/buddy/filesystem_fatfs.cpp`: `/usb` FatFS device.
- `src/buddy/filesystem_littlefs_internal.cpp`: `/internal` littlefs device.

**Testing:**

- `tests/unit/CMakeLists.txt`: Catch2 host unit-test root and `add_catch_test(...)`.
- `tests/unit/README.md`: Unit-test creation and run instructions.
- `tests/integration/README.md`: Simulator/pytest integration-test run instructions.
- `tests/integration/conftest.py`: Integration-test fixture entrypoint.
- `tests/stubs/FreeRTOS/CMakeLists.txt`: Host FreeRTOS stubs and wrappers.
- `tests/unit/common`, `tests/unit/gui`, `tests/unit/connect`, `tests/unit/transfers`, `tests/unit/persistent_stores`: Unit-test directories mirroring production modules.

## Naming Conventions

**Files:**

- Use lowercase snake_case for many common and utility files: `src/common/marlin_server.cpp`, `src/common/printer_model.cpp`, `src/common/path_utils.cpp`.
- Use subsystem prefixes for GUI screens and menus: `src/gui/screen_home.cpp`, `src/gui/screen_menu_settings.cpp`, `src/gui/MItem_network.cpp`.
- Use `M###.cpp`, `G###.cpp`, or combined G-code names for Marlin stubs: `src/marlin_stubs/M862_1.cpp`, `src/marlin_stubs/G26.cpp`, `src/marlin_stubs/M919-M920.cpp`.
- Use PascalCase class filenames where the local class/interface is PascalCase: `src/puppies/PuppyBootstrap.cpp`, `src/gui/ScreenFactory.hpp`, `src/hw/FUSB302B.cpp`.
- Use `CMakeLists.txt` in each compiled subdirectory and add files through `target_sources(...)` or `add_subdirectory(...)`.

**Directories:**

- Use source-tree ownership directories matching runtime layers: `src/buddy`, `src/common`, `src/gui`, `src/connect`, `src/device`, `src/hw`, `src/puppies`, `src/puppy`.
- Use `include_<PRINTER>` directories for printer-specific GUI/selftest includes: `src/gui/include_MK4`, `src/common/selftest/include_XL`, `src/gui/include_COREONE`.
- Use feature directories for optional feature slices: `src/common/feature/chamber`, `src/common/feature/cancel_object`, `src/feature/nozzle_cleaner`.
- Use MCU-family directories for startup/linker/HAL glue: `src/device/stm32f4`, `src/device/stm32g0`.
- Use mirrored test directories under `tests/unit/<module>` for production module coverage: `tests/unit/common`, `tests/unit/gui`, `tests/unit/connect`.

**Build Identifiers:**

- Use uppercase CMake cache/options for build inputs: `PRINTER`, `BOARD`, `MCU`, `BOOTLOADER`, `RESOURCES`, `TRANSLATIONS_ENABLED`.
- Use generated option headers with lowercase file names from uppercase option names: `include/option/option_boolean.h.in` produces build-tree headers such as `option/has_gui.h`.
- Use macros with function-like checks in C/C++ code: `HAS_GUI()`, `HAS_PUPPIES()`, `BUDDY_ENABLE_CONNECT()`, `BOARD_IS_XBUDDY()`, `PRINTER_IS_PRUSA_COREONE()`.
- Use CMake target names that match library boundaries: `firmware`, `BuddyHeaders`, `Marlin`, `Marlin_Config`, `freertos`, `logging`, `buddy_utils`, `Buddy::Lang`.

## Where to Add New Code

**New Master-Board Feature:**

- Primary code: `src/common/feature/<feature>` for domain/application behavior, with an entry in `src/common/feature/CMakeLists.txt`.
- UI code: `src/gui` for broadly integrated screens/menus, or `src/feature/<feature>` when the feature owns both G-code and screen code as in `src/feature/gearbox_alignment`.
- Build gate: Add feature selection to `ProjectOptions.cmake` and consume generated headers through `#include <option/<feature>.h>` in the relevant source.
- Tests: Add host coverage under `tests/unit/common/feature/<feature>` or another matching `tests/unit/<module>` path, then register it through the nearest `CMakeLists.txt`.

**New Marlin-Facing Command or Print Operation:**

- G-code implementation: `src/marlin_stubs/<command>.cpp` or a subdirectory such as `src/marlin_stubs/pause`.
- Build registration: `src/marlin_stubs/CMakeLists.txt` or a printer-specific CMake file such as `src/marlin_stubs/MK4/CMakeLists.txt`.
- Request/client API: `src/common/marlin_client.hpp`, `src/common/marlin_client.cpp`, `src/common/marlin_server_request.hpp`, and `src/common/marlin_server.cpp`.
- Tests: Add unit tests under `tests/unit/common/gcode`, `tests/unit/lib/Marlin`, or the feature-specific test directory.

**New GUI Screen, Dialog, or Menu Item:**

- Screen implementation: `src/gui/screen_<name>.hpp` and `src/gui/screen_<name>.cpp`, registered in `src/gui/CMakeLists.txt` or a subdirectory CMake file.
- Dialog implementation: `src/gui/dialogs` and `src/gui/dialogs/CMakeLists.txt`.
- Menu item implementation: `src/gui/menu_item`, `src/gui/menu_item/specific`, and `src/gui/menu_item/CMakeLists.txt`.
- Navigation integration: Use `ScreenFactory`/`Screens` from `src/gui/ScreenFactory.hpp` and `src/gui/ScreenHandler.hpp`.
- Tests: Add layout/window/input tests under `tests/unit/gui`, `tests/unit/gui/window`, or a new mirrored directory.

**New Hardware Peripheral:**

- Board-level component: `src/hw/<component>.cpp` and `src/hw/<component>.hpp`, registered in `src/hw/CMakeLists.txt`.
- MCU peripheral setup: `src/device/stm32f4/peripherals.cpp`, `src/device/stm32g0/peripherals.cpp`, or matching headers under `include/device/<mcu>/device`.
- Board-specific configuration: Add under `src/hw/mk4_ix_coreone`, `src/hw/xl`, `src/hw/mk3.5`, or `src/hw/xbuddy_xlbuddy` as appropriate.
- Public hardware API: Add to `include/buddy`, `include/device`, or a subsystem include directory only when multiple modules need it.

**New FreeRTOS Task or Startup Dependency:**

- Dependency definition: Add `TaskDeps::Dependency` and `TaskDeps::Tasks` masks in `include/tasks.hpp`.
- Dependency initialization/provider: Use `TaskDeps::components_init()` from `src/common/tasks.cpp`, then `TaskDeps::provide(...)` in the component that becomes ready.
- Task creation: Prefer the owner module and follow patterns in `src/buddy/main.cpp`, `src/buddy/usb_device.cpp`, `src/puppies/puppy_task.cpp`, or `src/logging/log_task.cpp`.
- Static task allocation: Use `include/buddy/ccm_thread.hpp` where CCMRAM stack placement is required.

**New Persistent Setting:**

- Store item: Add typed item definitions in `src/persistent_stores/store_instances/config_store/store_definition.hpp`.
- Behavior/migration: Add config checks or version migrations in `src/persistent_stores/store_instances/config_store/store_definition.cpp`.
- Backend changes: Modify `src/persistent_stores/journal` only for storage format/backend behavior.
- Tests: Add storage behavior tests under `tests/unit/persistent_stores`.

**New Connect or Network Behavior:**

- Connect protocol/client logic: `src/connect`.
- Printer adapter state/control: `src/connect/printer.hpp` and `src/connect/marlin_printer.cpp`.
- File transfer behavior: `src/transfers`.
- Network-visible state mapping: `src/state/printer_state.cpp`.
- HTTP/WUI behavior: `lib/WUI` when the change belongs to the embedded web UI library.
- Tests: Add tests under `tests/unit/connect`, `tests/unit/transfers`, or `tests/unit/lib/WUI`.

**New Resource, Asset, or Translation:**

- Static firmware resource: Add source asset under `src/resources` and register it in `src/resources/CMakeLists.txt`.
- GUI image/font source: Add source asset under `src/gui/res` and update generation flow through `src/resources/QoiGenerator.cmake` or `utils/translations_and_fonts`.
- Translation string/catalog work: Use `src/lang/po`, `src/lang/CMakeLists.txt`, and `utils/translations_and_fonts/lang.py`.
- Runtime resource bootstrap/hash behavior: Add to `src/resources/bootstrap.cpp`, `src/resources/hash.cpp`, or `src/resources/revision.cpp`.

**New Puppy or Expansion-Board Behavior:**

- Master-side device behavior: `src/puppies` and `include/puppies`.
- Dwarf firmware behavior: `src/puppy/dwarf`.
- ModularBed firmware behavior: `src/puppy/modularbed`.
- Shared puppy utilities: `src/puppy/shared`.
- xBuddy Extension firmware behavior: `src/puppy/xbuddy_extension` and `src/puppy/xbuddy_extension_shared`.
- Build/resource integration: `CMakeLists.txt`, `src/resources/CMakeLists.txt`, and `ProjectOptions.cmake`.

**Utilities:**

- Shared C++ firmware helpers intended as a clean library: `src/module/utils` and `src/module/utils/CMakeLists.txt`.
- Firmware-common helpers tied to the global `firmware` target: `src/common/utils` and `src/common/utils/CMakeLists.txt`.
- Host/developer scripts: `utils`, with generated output placed under build directories or documented gitignored locations.

## Special Directories

**`.dependencies`:**

- Purpose: Bootstrapped external tools and binary dependencies managed by `utils/bootstrap.py`.
- Generated: Yes.
- Committed: No.

**`build`, `build-*`, `build-vscode-*`:**

- Purpose: CMake build directories, generated option headers, generated resource headers, products, and intermediate puppy builds.
- Generated: Yes.
- Committed: No.

**`src/gui/res`:**

- Purpose: Source GUI image/font assets used by QOI/font/resource generation.
- Generated: Partly; source assets are committed, build outputs are generated by `src/resources/QoiGenerator.cmake` and `utils/translations_and_fonts`.
- Committed: Yes for source assets.

**`src/resources/web`:**

- Purpose: Embedded WUI static frontend assets packaged into the resource image by `src/resources/CMakeLists.txt`.
- Generated: Not detected in this repository layout; files are committed.
- Committed: Yes.

**`src/lang/po`:**

- Purpose: Translation catalogs used to generate firmware translation tables and optional external-flash `.mo` files.
- Generated: Source catalogs are committed; hash tables and required-char outputs are generated in the build tree by `src/lang/CMakeLists.txt`.
- Committed: Yes for `.po` source catalogs.

**`lib`:**

- Purpose: Third-party and subrepo dependencies used directly by firmware builds.
- Generated: No.
- Committed: Yes.

**`tests/stubs`:**

- Purpose: Host-side replacements for FreeRTOS, Marlin, device, config store, logging, and other firmware-only dependencies in unit tests.
- Generated: No.
- Committed: Yes.

**`.planning/codebase`:**

- Purpose: Generated codebase intelligence used by GSD planning/execution agents.
- Generated: Yes.
- Committed: Project/workflow dependent.

______________________________________________________________________

*Structure analysis: 2026-06-01*
