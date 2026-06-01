# Technology Stack

**Analysis Date:** 2026-06-01

## Languages

**Primary:**

- C++23 - Primary firmware, UI, networking, printer logic, and host-test language; the root build declares `CMAKE_CXX_STANDARD 23` in `CMakeLists.txt`, with source concentrated in `src/`, `include/`, `lib/`, and `tests/`.
- C - STM32 HAL, USB/network middleware, low-level drivers, and generated/ported embedded libraries; C is enabled by `project(Buddy LANGUAGES C CXX ASM ...)` in `CMakeLists.txt`, with sources in `lib/Drivers/`, `lib/Middlewares/`, `lib/WUI/`, and `src/`.
- ASM - Cortex-M startup, interrupt, and low-level support; assembly is enabled in `CMakeLists.txt` and startup sources live under `lib/Drivers/` and board-specific firmware trees.

**Secondary:**

- Python 3.8+ - Build orchestration, dependency bootstrapping, packaging, resource generation, simulator support, metrics tools, and integration tests; `README.md` requires Python 3.8+, `utils/bootstrap.py` enforces it, and scripts live under `utils/`, `tests/integration/`, and `src/common/http/`.
- CMake 3.21+/3.22+ - Build system and target graph; `CMakeLists.txt` requires 3.22, `CMakePresets.json` declares 3.21, and modules live under `cmake/` and `lib/Add*.cmake`.
- Shell/Groovy/Docker - CI, local tooling, and developer workflows; shell scripts live under `utils/`, Jenkins pipeline code is in `utils/holly/build-pr.jenkins`, and CI container setup is in `utils/holly/Dockerfile`.

## Runtime

**Environment:**

- Embedded bare-metal/RTOS firmware for STM32 Cortex-M targets; `ProjectOptions.cmake` selects MCUs including `STM32F407VG`, `STM32F429VI`, `STM32F427ZI`, `STM32G070RBT6`, and `STM32H503CBU7`.
- Cross-compiled ARM runtime uses `arm-none-eabi-gcc`/`arm-none-eabi-g++` from `.dependencies/gcc-arm-none-eabi-13.2.1/bin`, configured by `cmake/GccArmNoneEabi.cmake` and `cmake/AnyGccArmNoneEabi.cmake`.
- Host runtime is used for tools and tests when `CMAKE_CROSSCOMPILING` is false; host targets are declared in `utils/translations_and_fonts/png2font/CMakeLists.txt`, `tests/CMakeLists.txt`, and `CMakePresets.json`.

**Package Manager:**

- C/C++ toolchain dependencies are managed by the repo bootstrapper, not a system package manager; `utils/bootstrap.py` downloads CMake, Ninja, GCC Arm None Eabi, clang-format, bootloaders, simulator assets, and other binary dependencies into `.dependencies/`.
- Python packages are installed with `pip` into a virtual environment created by `utils/bootstrap.py`; core requirements are listed in `requirements.txt`, CI splits them through `utils/holly/build-requirements.txt` and `utils/holly/heavy-requirements.txt`, and optional tool requirements live in `utils/metrics/requirements.txt`, `utils/dumpserver/requirements.txt`, and `utils/phase_stepping/requirements.txt`.
- Lockfile: no Python hash lockfile is present; dependency pins and compatible ranges are maintained in `requirements.txt` and the tool-specific requirements files.

## Frameworks

**Core:**

- FreeRTOS/CMSIS-RTOS - Tasking and RTOS abstraction for firmware; CMake targets are declared in `lib/Middlewares/Third_Party/FreeRTOS/CMakeLists.txt`.
- STM32 HAL/CMSIS - MCU peripheral access for STM32F4, STM32G0, and STM32H5 families; HAL/CMSIS setup lives in `lib/Drivers/CMakeLists.txt`, `lib/Drivers/CMSIS/CMakeLists.txt`, `lib/Drivers/AddStm32f4Hal.cmake`, `lib/Drivers/AddStm32g0Hal.cmake`, and `lib/Drivers/AddStm32h5Hal.cmake`.
- Marlin printer core - Motion/planner/printer firmware base imported under `lib/Marlin/` and attached through `lib/AddMarlin.cmake`.
- LwIP - Embedded TCP/IP stack for Ethernet, WiFi, HTTP, SNTP, mDNS, UDP metrics, and Prusa Connect transport; configuration is in `include/buddy/lwipopts.h` and build wiring is in `lib/Middlewares/Third_Party/LwIP/CMakeLists.txt`.
- mbedTLS - TLS and cryptography for Prusa Connect, encrypted downloads, and AES helpers; build wiring is in `lib/Middlewares/Third_Party/mbedtls/CMakeLists.txt`, Connect TLS code is in `src/connect/tls/`, and transfer decryption is in `src/transfers/decrypt.hpp`.
- FatFs and littlefs - Removable USB/media and internal resource storage; FatFs is wired in `lib/Middlewares/Third_Party/FatFs/CMakeLists.txt`, littlefs is wired in `lib/Middlewares/Third_Party/littlefs/CMakeLists.txt`, and image generation is handled by `cmake/Littlefs.cmake` and `utils/mklittlefs.py`.
- TinyUSB - USB device stack used on boards with USB-device support; integration lives in `lib/AddTinyusb.cmake`, `src/buddy/usb_device.cpp`, and `src/buddy/usb_device_cdc.cpp`.
- Custom WUI HTTP server - Resource-constrained local HTTP/PrusaLink implementation; sources live in `lib/WUI/nhttp/`, API handlers live in `lib/WUI/link_content/`, and service startup lives in `lib/WUI/http_lifetime.cpp`.

**Testing:**

- Catch2 - C++ unit-test framework linked by `lib/AddCatch2.cmake` and used through `tests/CMakeLists.txt` and `tests/unit/CMakeLists.txt`.
- CTest - CMake-native test runner for host unit tests; configured through `enable_testing()` in `tests/CMakeLists.txt` and host presets in `CMakePresets.json`.
- pytest and pytest-asyncio - Python integration and simulator-facing tests; dependencies are listed in `requirements.txt`, pytest config is in `pyproject.toml`, and test guidance is in `tests/integration/README.md`.
- Mini404/QEMU simulator support - Firmware simulation and integration testing dependency downloaded by `utils/bootstrap.py`, with simulator helpers under `utils/simulator/`.

**Build/Dev:**

- CMake + Ninja - Primary build engine; root configuration is in `CMakeLists.txt`, generated presets are in `CMakePresets.json`, preset sources are in `utils/presets/presets.json`, and shared CMake helpers live in `cmake/`.
- `utils/build.py` - High-level build wrapper for supported printer/board presets, bootloader variants, DFU generation, host tools, and artifact staging into `build/products`.
- `utils/bootstrap.py` - Deterministic dependency bootstrapper for `.dependencies/`, Python virtualenv setup, and requirements installation.
- pre-commit - Formatting and generated-file checks; hooks are declared in `.pre-commit-config.yaml` and cover `clang-format`, `cmake-format`, `yapf`, generated CMake presets, generated log-component docs, and requirements checks.
- clang-format/yapf/cmake-format - Formatting tools configured by `.clang-format`, `.pre-commit-config.yaml`, and generated bootstrap dependencies under `.dependencies/`.

## Key Dependencies

**Critical:**

- `lib/Marlin/` - Core 3D-printer firmware logic, motion, G-code, planner, and hardware abstractions imported through `lib/AddMarlin.cmake`.
- `lib/Middlewares/Third_Party/FreeRTOS/` - Scheduler and task runtime for firmware built by `CMakeLists.txt`.
- `lib/Middlewares/Third_Party/LwIP/` - Network stack used by `lib/WUI/`, `src/connect/`, `src/common/http/`, `src/syslog/`, and `src/transfers/`.
- `lib/Middlewares/Third_Party/mbedtls/` - TLS, certificate validation, and AES support used by `src/connect/tls/` and `src/transfers/`.
- `src/persistent_stores/store_instances/config_store/` - Persistent configuration definitions and defaults for network, WiFi, PrusaLink, Connect, metrics, and feature state.
- `src/connect/` - Prusa Connect client, registration, telemetry/events, WebSocket command channel, and TLS/plain connection cache.
- `lib/WUI/` - PrusaLink local web UI/API, network device management, authentication, SNTP, optional mDNS, and HTTP serving.
- `src/puppies/`, `src/puppy/`, and `lib/AddLiblightmodbus.cmake` - XL/Dwarf/Modular Bed/xBuddy Extension auxiliary-controller support over Modbus/RS485.

**Infrastructure:**

- `requirements.txt` - Python tooling dependencies including `aiohttp`, `click`, `ecdsa`, `littlefs-python`, `numpy`, `pillow`, `polib`, `pre-commit`, `pytest`, `pytest-asyncio`, `pyyaml`, `qoi`, and `requests`.
- `lib/AddTMCStepper.cmake` and `lib/TMCStepper/` - Trinamic stepper driver support used by printer motion hardware.
- `lib/AddMMU2.cmake`, `lib/Prusa-Firmware-MMU/`, and `src/mmu2/` - MMU firmware/library integration and runtime support.
- `lib/esp32-nic/`, `lib/esp8266-nic/`, `src/buddy-esp-serial-flasher/`, and `lib/esp-serial-flasher/` - ESP network-module firmware and flashing support.
- `lib/AddBgcode.cmake` and `lib/libbgcode/` - Binary G-code support included through the shared library graph.
- `lib/AddPrusaErrorCodes.cmake` and `lib/Prusa-Error-Codes/` - Shared error-code definitions used by firmware diagnostics and UI.
- `utils/translations_and_fonts/`, `src/lang/`, and `src/resources/` - Translation, font, icon, QOI, and resource-generation pipeline.
- `utils/metrics/`, `utils/dumpserver/`, and `utils/phase_stepping/` - Developer/diagnostic host tools with separate Python requirements.

## Configuration

**Environment:**

- Build selection is driven by CMake cache variables and generated presets; printer, board, MCU, bootloader, DFU, resource, translation, and feature flags are defined in `ProjectOptions.cmake`, `CMakePresets.json`, and `utils/presets/presets.json`.
- Supported printer presets include `COREONE`, `MINI`, `MK4`, `MK3.5`, `XL`, `iX`, and `XL_DEV_KIT`; supported boards include `BUDDY`, `XBUDDY`, `XLBUDDY`, `DWARF`, `MODULARBED`, `XL_DEV_KIT_XLB`, and `XBUDDY_EXTENSION` in `ProjectOptions.cmake`.
- Feature toggles such as `WUI`, `CONNECT`, `RESOURCES`, `TRANSLATIONS_ENABLED`, `TOUCH_ENABLED`, `HAS_MMU2`, `HAS_PUPPIES`, `HAS_DWARF`, `HAS_PUPPY_MODULARBED`, `HAS_XBUDDY_EXTENSION`, `HAS_USB_DEVICE`, and `HAS_NFC` live in `ProjectOptions.cmake`.
- `SIGNING_KEY` is a CMake cache path to a private EC signing key used for custom firmware signing; the path is configured through `ProjectOptions.cmake` and `utils/build.py`, while key material must remain outside committed docs and source.
- `BUDDY_NO_VIRTUALENV=1` disables automatic Python virtualenv creation in `utils/bootstrap.py` and `cmake/Utilities.cmake`.
- Firmware runtime configuration is persisted through `src/persistent_stores/store_instances/config_store/store_definition.hpp` and defaults in `src/persistent_stores/store_instances/config_store/defaults.hpp`.

**Build:**

- Root build graph: `CMakeLists.txt`.
- Build presets: `CMakePresets.json`, generated from `utils/presets/presets.json` by `utils/build.py` and checked by `.pre-commit-config.yaml`.
- Shared CMake modules: `cmake/Utilities.cmake`, `cmake/GccArmNoneEabi.cmake`, `cmake/AnyGccArmNoneEabi.cmake`, `cmake/Dependencies.cmake`, `cmake/Littlefs.cmake`, and `cmake/Tests.cmake`.
- Board/printer options: `ProjectOptions.cmake`.
- Tool/dependency bootstrap: `utils/bootstrap.py`.
- Firmware packaging: `utils/pack_fw.py`, `utils/dfu.py`, `utils/gen_puppies_descriptor.py`, `cmake/Littlefs.cmake`, and packaging rules in `CMakeLists.txt`.
- CI build pipeline: `utils/holly/build-pr.jenkins` with container definition in `utils/holly/Dockerfile`; GitHub workflow automation is limited to repository maintenance in `.github/workflows/bright-builds-auto-update.yml` and `.github/workflows/stale.yml`.

## Platform Requirements

**Development:**

- Python 3.8+ and `requests` are required before running `python utils/build.py`, as described in `README.md` and enforced by `utils/bootstrap.py`.
- Bootstrap downloads CMake 3.28.3, Ninja 1.10.2, GCC Arm None Eabi 13.2.1, clang-format 16, bootloaders, Mini404, CMSIS-SVD data, CrashDebug, and other pinned assets into `.dependencies/` via `utils/bootstrap.py`.
- Normal firmware builds run through `python utils/build.py`, with lower-level CMake/Ninja invocation available through `CMakePresets.json` and documented editor flows in `doc/editor/lsp-based-ides.md` and `doc/editor/vscode.md`.
- Debug/profiling flows use OpenOCD, GDB-compatible tooling, and optional puncover workflows documented in `doc/debugging_profiling.md`, `doc/editor/vscode.md`, and `doc/puncover.md`.
- Pre-commit formatting and generated-file checks are configured in `.pre-commit-config.yaml` and documented in `doc/contributing.md`.

**Production:**

- Production artifacts are embedded firmware images for STM32-based Prusa printer boards; board and MCU mapping is defined in `ProjectOptions.cmake`.
- Artifact types include `.bin`, `.bbf`, `.dfu`, `.map`, and resource images produced by rules in `CMakeLists.txt`, `cmake/Littlefs.cmake`, `utils/build.py`, and `utils/pack_fw.py`.
- Firmware update and custom build flows are documented in `README.md`, including board-specific appendix handling and XL puppy firmware handling.

______________________________________________________________________

*Stack analysis: 2026-06-01*
