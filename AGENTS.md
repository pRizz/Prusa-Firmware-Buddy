<!-- bright-builds-rules-managed:begin -->

# Bright Builds Rules

`AGENTS.md` is the entrypoint for repo-local instructions, not the complete Bright Builds Rules specification.

This managed block is owned upstream by `bright-builds-rules`. If this block needs a fix, open an upstream PR or issue instead of editing the managed text in a downstream repo. Keep downstream-specific instructions outside this managed block.

Before plan, review, implementation, or audit work:

1. Read the repo-local instructions in `AGENTS.md`, including any `## Repo-Local Guidance` section and any instructions outside this managed block.
1. Read `AGENTS.bright-builds.md`.
1. Read `standards-overrides.md` when present.
1. Read the pinned canonical standards pages relevant to the task.
1. If you have not done that yet, stop and load those sources before continuing.

Use this routing map when deciding what to load next:

- For repo-specific commands, prerequisites, generated-file ownership, CI-only suites, or recurring workflow facts, use the local `AGENTS.md`, especially `## Repo-Local Guidance`.
- For the Bright Builds default workflow and high-signal cross-cutting rules used in most tasks, use `AGENTS.bright-builds.md`.
- For deliberate repo-specific exceptions to the Bright Builds defaults, use `standards-overrides.md`.
- To choose the right pinned canonical standards page, start with the Bright Builds entrypoint `standards/index.md`.
- For business-logic structure, domain modeling, and functional-core versus imperative-shell decisions, use the canonical page `standards/core/architecture.md`.
- For control flow, naming, function/file size, and readability rules, use the canonical page `standards/core/code-shape.md`.
- For sync, bootstrap, and pre-commit verification rules, use the canonical page `standards/core/verification.md`.
- For unit-test expectations, use the canonical page `standards/core/testing.md`.
- For Rust or TypeScript/JavaScript-specific rules, use the matching canonical page under `standards/languages/`.
- Keep recurring repo-specific workflow facts, commands, and links in a `## Repo-Local Guidance` section elsewhere in this file.
- Record deliberate repo-specific exceptions and override decisions in `standards-overrides.md`.
- If instructions elsewhere in `AGENTS.md` conflict with `AGENTS.bright-builds.md`, follow the repo-local instructions and treat them as an explicit local exception.

<!-- bright-builds-rules-managed:end -->

<!-- GSD:project-start source:PROJECT.md -->

## Project

**Prusa Firmware Buddy Rust Port**

This project is a full Rust rewrite of the Prusa-Firmware-Buddy firmware while preserving the behavior of the current supported printer firmware. The existing C/C++/CMake codebase remains the reference implementation, but the target end state is a Rust firmware with Bazel as the authoritative build system and a `justfile` for common developer workflows.

The work is intentionally standards-driven: Bright Builds Rules guide architecture, code shape, verification, testing, and Rust module structure. Known defects and fragile areas identified in the codebase map should be fixed during the rewrite instead of being mechanically carried forward.

**Core Value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.

### Constraints

- **Migration posture**: Big Bang — the roadmap should lead to a full replacement cutover instead of relying on incremental production migration as the primary strategy.
- **Compatibility**: Behavior Parity — current supported printers, release artifacts, generated assets, tests, network behavior, persistent config, and safety-critical firmware behavior must remain compatible unless explicitly descoped.
- **Build system**: Bazel Primary Now — Bazel becomes the authoritative build from the start of the planned work; CMake may remain only as a reference, comparison, or compatibility path where necessary.
- **Developer workflow**: `justfile` required — common commands should have discoverable, stable wrappers that call Bazel/Rust tooling and any remaining compatibility checks.
- **Standards**: Bright Builds Rules — architecture, code shape, Rust guidance, verification, and testing standards apply unless a narrow local override is documented in `standards-overrides.md`.
- **Safety**: Embedded firmware behavior must be validated with tests, hardware-aware review, simulator flows, or explicit evidence before replacement is considered complete.
- **Third-party code**: Vendor, HAL, generated, and upstream imported code may require staged boundary decisions before full Rust replacement; retained foreign code must be named and justified.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- C++23 - Primary firmware, UI, networking, printer logic, and host-test language; the root build declares `CMAKE_CXX_STANDARD 23` in `CMakeLists.txt`, with source concentrated in `src/`, `include/`, `lib/`, and `tests/`.
- C - STM32 HAL, USB/network middleware, low-level drivers, and generated/ported embedded libraries; C is enabled by `project(Buddy LANGUAGES C CXX ASM ...)` in `CMakeLists.txt`, with sources in `lib/Drivers/`, `lib/Middlewares/`, `lib/WUI/`, and `src/`.
- ASM - Cortex-M startup, interrupt, and low-level support; assembly is enabled in `CMakeLists.txt` and startup sources live under `lib/Drivers/` and board-specific firmware trees.
- Python 3.8+ - Build orchestration, dependency bootstrapping, packaging, resource generation, simulator support, metrics tools, and integration tests; `README.md` requires Python 3.8+, `utils/bootstrap.py` enforces it, and scripts live under `utils/`, `tests/integration/`, and `src/common/http/`.
- CMake 3.21+/3.22+ - Build system and target graph; `CMakeLists.txt` requires 3.22, `CMakePresets.json` declares 3.21, and modules live under `cmake/` and `lib/Add*.cmake`.
- Shell/Groovy/Docker - CI, local tooling, and developer workflows; shell scripts live under `utils/`, Jenkins pipeline code is in `utils/holly/build-pr.jenkins`, and CI container setup is in `utils/holly/Dockerfile`.

## Runtime

- Embedded bare-metal/RTOS firmware for STM32 Cortex-M targets; `ProjectOptions.cmake` selects MCUs including `STM32F407VG`, `STM32F429VI`, `STM32F427ZI`, `STM32G070RBT6`, and `STM32H503CBU7`.
- Cross-compiled ARM runtime uses `arm-none-eabi-gcc`/`arm-none-eabi-g++` from `.dependencies/gcc-arm-none-eabi-13.2.1/bin`, configured by `cmake/GccArmNoneEabi.cmake` and `cmake/AnyGccArmNoneEabi.cmake`.
- Host runtime is used for tools and tests when `CMAKE_CROSSCOMPILING` is false; host targets are declared in `utils/translations_and_fonts/png2font/CMakeLists.txt`, `tests/CMakeLists.txt`, and `CMakePresets.json`.
- C/C++ toolchain dependencies are managed by the repo bootstrapper, not a system package manager; `utils/bootstrap.py` downloads CMake, Ninja, GCC Arm None Eabi, clang-format, bootloaders, simulator assets, and other binary dependencies into `.dependencies/`.
- Python packages are installed with `pip` into a virtual environment created by `utils/bootstrap.py`; core requirements are listed in `requirements.txt`, CI splits them through `utils/holly/build-requirements.txt` and `utils/holly/heavy-requirements.txt`, and optional tool requirements live in `utils/metrics/requirements.txt`, `utils/dumpserver/requirements.txt`, and `utils/phase_stepping/requirements.txt`.
- Lockfile: no Python hash lockfile is present; dependency pins and compatible ranges are maintained in `requirements.txt` and the tool-specific requirements files.

## Frameworks

- FreeRTOS/CMSIS-RTOS - Tasking and RTOS abstraction for firmware; CMake targets are declared in `lib/Middlewares/Third_Party/FreeRTOS/CMakeLists.txt`.
- STM32 HAL/CMSIS - MCU peripheral access for STM32F4, STM32G0, and STM32H5 families; HAL/CMSIS setup lives in `lib/Drivers/CMakeLists.txt`, `lib/Drivers/CMSIS/CMakeLists.txt`, `lib/Drivers/AddStm32f4Hal.cmake`, `lib/Drivers/AddStm32g0Hal.cmake`, and `lib/Drivers/AddStm32h5Hal.cmake`.
- Marlin printer core - Motion/planner/printer firmware base imported under `lib/Marlin/` and attached through `lib/AddMarlin.cmake`.
- LwIP - Embedded TCP/IP stack for Ethernet, WiFi, HTTP, SNTP, mDNS, UDP metrics, and Prusa Connect transport; configuration is in `include/buddy/lwipopts.h` and build wiring is in `lib/Middlewares/Third_Party/LwIP/CMakeLists.txt`.
- mbedTLS - TLS and cryptography for Prusa Connect, encrypted downloads, and AES helpers; build wiring is in `lib/Middlewares/Third_Party/mbedtls/CMakeLists.txt`, Connect TLS code is in `src/connect/tls/`, and transfer decryption is in `src/transfers/decrypt.hpp`.
- FatFs and littlefs - Removable USB/media and internal resource storage; FatFs is wired in `lib/Middlewares/Third_Party/FatFs/CMakeLists.txt`, littlefs is wired in `lib/Middlewares/Third_Party/littlefs/CMakeLists.txt`, and image generation is handled by `cmake/Littlefs.cmake` and `utils/mklittlefs.py`.
- TinyUSB - USB device stack used on boards with USB-device support; integration lives in `lib/AddTinyusb.cmake`, `src/buddy/usb_device.cpp`, and `src/buddy/usb_device_cdc.cpp`.
- Custom WUI HTTP server - Resource-constrained local HTTP/PrusaLink implementation; sources live in `lib/WUI/nhttp/`, API handlers live in `lib/WUI/link_content/`, and service startup lives in `lib/WUI/http_lifetime.cpp`.
- Catch2 - C++ unit-test framework linked by `lib/AddCatch2.cmake` and used through `tests/CMakeLists.txt` and `tests/unit/CMakeLists.txt`.
- CTest - CMake-native test runner for host unit tests; configured through `enable_testing()` in `tests/CMakeLists.txt` and host presets in `CMakePresets.json`.
- pytest and pytest-asyncio - Python integration and simulator-facing tests; dependencies are listed in `requirements.txt`, pytest config is in `pyproject.toml`, and test guidance is in `tests/integration/README.md`.
- Mini404/QEMU simulator support - Firmware simulation and integration testing dependency downloaded by `utils/bootstrap.py`, with simulator helpers under `utils/simulator/`.
- CMake + Ninja - Primary build engine; root configuration is in `CMakeLists.txt`, generated presets are in `CMakePresets.json`, preset sources are in `utils/presets/presets.json`, and shared CMake helpers live in `cmake/`.
- `utils/build.py` - High-level build wrapper for supported printer/board presets, bootloader variants, DFU generation, host tools, and artifact staging into `build/products`.
- `utils/bootstrap.py` - Deterministic dependency bootstrapper for `.dependencies/`, Python virtualenv setup, and requirements installation.
- pre-commit - Formatting and generated-file checks; hooks are declared in `.pre-commit-config.yaml` and cover `clang-format`, `cmake-format`, `yapf`, generated CMake presets, generated log-component docs, and requirements checks.
- clang-format/yapf/cmake-format - Formatting tools configured by `.clang-format`, `.pre-commit-config.yaml`, and generated bootstrap dependencies under `.dependencies/`.

## Key Dependencies

- `lib/Marlin/` - Core 3D-printer firmware logic, motion, G-code, planner, and hardware abstractions imported through `lib/AddMarlin.cmake`.
- `lib/Middlewares/Third_Party/FreeRTOS/` - Scheduler and task runtime for firmware built by `CMakeLists.txt`.
- `lib/Middlewares/Third_Party/LwIP/` - Network stack used by `lib/WUI/`, `src/connect/`, `src/common/http/`, `src/syslog/`, and `src/transfers/`.
- `lib/Middlewares/Third_Party/mbedtls/` - TLS, certificate validation, and AES support used by `src/connect/tls/` and `src/transfers/`.
- `src/persistent_stores/store_instances/config_store/` - Persistent configuration definitions and defaults for network, WiFi, PrusaLink, Connect, metrics, and feature state.
- `src/connect/` - Prusa Connect client, registration, telemetry/events, WebSocket command channel, and TLS/plain connection cache.
- `lib/WUI/` - PrusaLink local web UI/API, network device management, authentication, SNTP, optional mDNS, and HTTP serving.
- `src/puppies/`, `src/puppy/`, and `lib/AddLiblightmodbus.cmake` - XL/Dwarf/Modular Bed/xBuddy Extension auxiliary-controller support over Modbus/RS485.
- `requirements.txt` - Python tooling dependencies including `aiohttp`, `click`, `ecdsa`, `littlefs-python`, `numpy`, `pillow`, `polib`, `pre-commit`, `pytest`, `pytest-asyncio`, `pyyaml`, `qoi`, and `requests`.
- `lib/AddTMCStepper.cmake` and `lib/TMCStepper/` - Trinamic stepper driver support used by printer motion hardware.
- `lib/AddMMU2.cmake`, `lib/Prusa-Firmware-MMU/`, and `src/mmu2/` - MMU firmware/library integration and runtime support.
- `lib/esp32-nic/`, `lib/esp8266-nic/`, `src/buddy-esp-serial-flasher/`, and `lib/esp-serial-flasher/` - ESP network-module firmware and flashing support.
- `lib/AddBgcode.cmake` and `lib/libbgcode/` - Binary G-code support included through the shared library graph.
- `lib/AddPrusaErrorCodes.cmake` and `lib/Prusa-Error-Codes/` - Shared error-code definitions used by firmware diagnostics and UI.
- `utils/translations_and_fonts/`, `src/lang/`, and `src/resources/` - Translation, font, icon, QOI, and resource-generation pipeline.
- `utils/metrics/`, `utils/dumpserver/`, and `utils/phase_stepping/` - Developer/diagnostic host tools with separate Python requirements.

## Configuration

- Build selection is driven by CMake cache variables and generated presets; printer, board, MCU, bootloader, DFU, resource, translation, and feature flags are defined in `ProjectOptions.cmake`, `CMakePresets.json`, and `utils/presets/presets.json`.
- Supported printer presets include `COREONE`, `MINI`, `MK4`, `MK3.5`, `XL`, `iX`, and `XL_DEV_KIT`; supported boards include `BUDDY`, `XBUDDY`, `XLBUDDY`, `DWARF`, `MODULARBED`, `XL_DEV_KIT_XLB`, and `XBUDDY_EXTENSION` in `ProjectOptions.cmake`.
- Feature toggles such as `WUI`, `CONNECT`, `RESOURCES`, `TRANSLATIONS_ENABLED`, `TOUCH_ENABLED`, `HAS_MMU2`, `HAS_PUPPIES`, `HAS_DWARF`, `HAS_PUPPY_MODULARBED`, `HAS_XBUDDY_EXTENSION`, `HAS_USB_DEVICE`, and `HAS_NFC` live in `ProjectOptions.cmake`.
- `SIGNING_KEY` is a CMake cache path to a private EC signing key used for custom firmware signing; the path is configured through `ProjectOptions.cmake` and `utils/build.py`, while key material must remain outside committed docs and source.
- `BUDDY_NO_VIRTUALENV=1` disables automatic Python virtualenv creation in `utils/bootstrap.py` and `cmake/Utilities.cmake`.
- Firmware runtime configuration is persisted through `src/persistent_stores/store_instances/config_store/store_definition.hpp` and defaults in `src/persistent_stores/store_instances/config_store/defaults.hpp`.
- Root build graph: `CMakeLists.txt`.
- Build presets: `CMakePresets.json`, generated from `utils/presets/presets.json` by `utils/build.py` and checked by `.pre-commit-config.yaml`.
- Shared CMake modules: `cmake/Utilities.cmake`, `cmake/GccArmNoneEabi.cmake`, `cmake/AnyGccArmNoneEabi.cmake`, `cmake/Dependencies.cmake`, `cmake/Littlefs.cmake`, and `cmake/Tests.cmake`.
- Board/printer options: `ProjectOptions.cmake`.
- Tool/dependency bootstrap: `utils/bootstrap.py`.
- Firmware packaging: `utils/pack_fw.py`, `utils/dfu.py`, `utils/gen_puppies_descriptor.py`, `cmake/Littlefs.cmake`, and packaging rules in `CMakeLists.txt`.
- CI build pipeline: `utils/holly/build-pr.jenkins` with container definition in `utils/holly/Dockerfile`; GitHub workflow automation is limited to repository maintenance in `.github/workflows/bright-builds-auto-update.yml` and `.github/workflows/stale.yml`.

## Platform Requirements

- Python 3.8+ and `requests` are required before running `python utils/build.py`, as described in `README.md` and enforced by `utils/bootstrap.py`.
- Bootstrap downloads CMake 3.28.3, Ninja 1.10.2, GCC Arm None Eabi 13.2.1, clang-format 16, bootloaders, Mini404, CMSIS-SVD data, CrashDebug, and other pinned assets into `.dependencies/` via `utils/bootstrap.py`.
- Normal firmware builds run through `python utils/build.py`, with lower-level CMake/Ninja invocation available through `CMakePresets.json` and documented editor flows in `doc/editor/lsp-based-ides.md` and `doc/editor/vscode.md`.
- Debug/profiling flows use OpenOCD, GDB-compatible tooling, and optional puncover workflows documented in `doc/debugging_profiling.md`, `doc/editor/vscode.md`, and `doc/puncover.md`.
- Pre-commit formatting and generated-file checks are configured in `.pre-commit-config.yaml` and documented in `doc/contributing.md`.
- Production artifacts are embedded firmware images for STM32-based Prusa printer boards; board and MCU mapping is defined in `ProjectOptions.cmake`.
- Artifact types include `.bin`, `.bbf`, `.dfu`, `.map`, and resource images produced by rules in `CMakeLists.txt`, `cmake/Littlefs.cmake`, `utils/build.py`, and `utils/pack_fw.py`.
- Firmware update and custom build flows are documented in `README.md`, including board-specific appendix handling and XL puppy firmware handling.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- Use `snake_case.cpp`, `snake_case.hpp`, `snake_case.h`, and `snake_case.c` for new owned C/C++ files, following `doc/contributing.md`; examples include `src/connect/printer_common.cpp`, `src/common/str_utils.hpp`, and `tests/unit/common/str_utils_test.cpp`.
- Keep established subsystem and externally constrained names when extending existing code, including hardware part names in `src/hw/TCA6408A.cpp`, product names in `src/puppies/Dwarf.cpp`, Marlin command names in `src/marlin_stubs/M862_5.cpp`, HAL names in `include/stm32g0_hal/stm32g0xx_hal_conf.h`, and generated resource names in `src/gui/res/cc/font_regular_11x18_latin.hpp`.
- Use `CMakeLists.txt` per build directory, with subsystem test registration in files such as `tests/unit/common/CMakeLists.txt` and `tests/unit/connect/CMakeLists.txt`.
- Use Python script names that match surrounding `utils/` style: underscore names such as `utils/check-requirements.py`, generator names such as `utils/logging/generate_overview.py`, and package directories such as `utils/persistent_stores/`.
- Use test file names that identify the unit under test: C++ tests use `*_test.cpp` or `*_tests.cpp` such as `tests/unit/common/circle_buffer_test.cpp` and `tests/unit/connect/planner.cpp`; pytest modules use `test_*.py` such as `tests/integration/test_prusa_link.py`.
- Use `snake_case` for new repo-owned free functions and methods, matching `doc/contributing.md` and examples such as `from_chars_light` in `src/common/str_utils.hpp`, `advance_time_s` in `tests/unit/connect/time_mock.cpp`, and `log_destination_register` in `src/logging/include/logging/log.hpp`.
- Preserve legacy or external contract method names when editing code already using that style, such as `window_t::DisableLongHoldScreenAction` in `src/guiapi/src/window.cpp`, hardware classes in `src/hw/FUSB302B.cpp`, and Marlin command surfaces under `src/marlin_stubs/`.
- Use `constexpr`, `consteval`, or `static inline` helper functions for compile-time or header-local logic when the surrounding file already uses them, as in `src/common/str_utils.hpp` and `src/common/filament_eeprom.hpp`.
- For Python, use lowercase `snake_case` functions and fixtures, as in `tests/integration/conftest.py`, `tests/blockdevice/test_block_device.py`, and `utils/logging/generate_overview.py`.
- Use `snake_case` for local variables, members, namespaces, and enum-class items in new owned code, as directed by `doc/contributing.md`; examples include `mock_time` in `tests/unit/connect/time_mock.cpp`, `content_length_rest` in `src/common/http/httpc.cpp`, and `printer_flash_dir` in `tests/integration/conftest.py`.
- Use `SCREAMING_CASE` for global constants and preprocessor symbols, matching examples such as `PRINTER_TYPE` in `CMakeLists.txt`, `LOG_LOWEST_SEVERITY` in `src/logging/include/logging/log.hpp`, and `BLOCK_SIZE` in `tests/blockdevice/test_block_device.py`.
- Match local class-constant style when extending existing classes. Some C++ classes use PascalCase private constants such as `RectTextLayout::MaxLines` in `src/common/str_utils.hpp`; some embedded modules use all-caps constants such as `FAN_CNT` in `src/puppies/xbuddy_extension.cpp`.
- Bright Builds `standards/core/code-shape.md` applies because `standards-overrides.md` has no active override: new internal nullable or absence-like names should use a visible `maybe_` prefix when practical. Keep public, legacy, wire, HAL, and overridden method names stable in files such as `src/connect/printer.hpp`, `include/puppies/xbuddy_extension.hpp`, and `tests/unit/connect/mock_printer.h`.
- Use `PascalCase` for new C++ classes, structs, and enum classes, matching `doc/contributing.md` and examples such as `Printer` in `src/connect/printer.hpp`, `OutBuffer` in `src/common/http/httpc.cpp`, `MockPrinter` in `tests/unit/connect/mock_printer.h`, and `Timestamp` in `src/logging/include/logging/log.hpp`.
- Do not add `_t` suffixes for new owned C++ types, per `doc/contributing.md`. Existing legacy and C-compatible names such as `resume_state_t` in `src/common/marlin_server.hpp` and `SelftestAxis_t` in `src/common/selftest_axis_type.hpp` are surrounding-style exceptions.
- Prefer `enum class` for typed states and protocol enums, as seen in `src/logging/include/logging/log.hpp`, `src/connect/printer.hpp`, and `include/puppies/PuppyModbus.hpp`.

## Code Style

- Format C/C++ with clang-format using `.clang-format`. Key settings include 4-space indentation, no tabs, right pointer alignment, custom brace wrapping, `ColumnLimit: 0`, `SortIncludes: false`, `InsertBraces: true`, and preserved include blocks.
- Format Python with YAPF through `.pre-commit-config.yaml`; use `# yapf: disable` and `# yapf: enable` only for parser-heavy blocks such as `tests/integration/conftest.py`, `utils/build.py`, and `utils/dfu.py`.
- Format CMake with `cmake-format` using `.cmake-format.py`; file lists in `target_sources(PUBLIC|PRIVATE|INTERFACE ...)` are sortable, line width is 100, and wrapped calls dangle closing parentheses.
- Install and run pre-commit hooks from `.pre-commit-config.yaml` for formatting, generated-doc updates, preset generation, requirement synchronization, trailing whitespace, final newline, and mixed line endings. `doc/contributing.md` states that build server checks reject improperly formatted pull requests.
- Use `#pragma once` for new headers, following `doc/contributing.md` and common headers such as `src/connect/printer.hpp`, `include/puppies/PuppyModbus.hpp`, and `tests/unit/logging/utils.hpp`.
- Do not add new author, creation-time, or copyright headers to owned files, per `doc/contributing.md`; keep third-party headers intact under paths such as `lib/`, `include/stm32f4_hal/`, and `src/device/stm32g0/linker/`.
- No clang-tidy, cppcheck, mypy, or ruff configuration is detected in root config files such as `.clangd`, `pyproject.toml`, and `.pre-commit-config.yaml`.
- CMake applies baseline C/C++ warnings globally with `-Wall` and `-Wsign-compare` in `CMakeLists.txt`; firmware targets add `-Wextra`, selected suppressions, and `-Werror=delete-non-virtual-dtor` in `CMakeLists.txt`.
- Jenkins PR builds pass `-DCUSTOM_COMPILE_OPTIONS:STRING="-Werror"` through `utils/holly/build-pr.jenkins`, so new warnings in compiled targets should be treated as CI failures.
- `.clangd` adds editor diagnostics and compile flags including `-std=c++23`, `-Wno-deprecated-volatile`, and `-ferror-limit=0`; keep IDE-only flags there instead of duplicating them in `CMakeLists.txt`.

## Import Organization

- No language-level path alias system is detected; include resolution is controlled by CMake target include directories in `CMakeLists.txt`, `ProjectOptions.cmake`, and subsystem `CMakeLists.txt` files.
- Test include order often intentionally puts stubs before real headers, such as `tests/unit/connect/CMakeLists.txt` placing `tests/stubs` before `include`; keep this order when adding test targets.
- Generated build headers live under CMake binary directories, such as `${CMAKE_CURRENT_BINARY_DIR}/http_resp_automaton.cpp` in `tests/unit/connect/CMakeLists.txt` and `${CMAKE_BINARY_DIR}/http.cpp` in `tests/unit/common/automata/CMakeLists.txt`.

## Error Handling

- Use explicit value-or-error return types for recoverable C++ paths. `src/common/http/httpc.cpp` uses `std::optional<Error>` for no-value errors and `std::variant<size_t, Error>` for value-or-error I/O results.
- Use `std::optional<T>` for absence in normal control flow, as in `include/puppies/xbuddy_extension.hpp`, `src/hw/TCA6408A.cpp`, and `tests/unit/connect/mock_printer.h`; new internal names should apply `maybe_` when practical under Bright Builds code-shape rules.
- Use small guard helpers or early returns to propagate errors instead of nesting; `src/common/http/httpc.cpp` uses `CHECKED(...)` to return an `Error` immediately.
- Use `std::errc` for parse status in lightweight parsing utilities such as `from_chars_light_result` in `src/common/str_utils.hpp` and assertions in `tests/unit/common/str_utils_test.cpp`.
- Use `assert(...)` for programmer invariants and impossible states, as in `src/puppies/PuppyModbus.cpp`, `src/common/http/httpc.cpp`, and `include/common/array_extensions.hpp`.
- Use `bsod(...)` or `fatal_error(...)` only for firmware-fatal conditions, as in `src/common/Pin.cpp`, `src/hw/FUSB302B.cpp`, and `src/bootloader/bootloader_update.cpp`; unit tests replace these with throwing stubs in `tests/unit/mock/bsod.cpp`.
- Use `message(FATAL_ERROR ...)` for invalid CMake configuration, as in `ProjectOptions.cmake` and `CMakeLists.txt`.
- In Python tools, return a nonzero status or raise a specific test error rather than silently swallowing failures, as in `utils/check-requirements.py` and `tests/integration/conftest.py`.

## Logging

- Define one log component per logical subsystem with `LOG_COMPONENT_DEF(name, logging::Severity::...)`, as in `src/puppies/puppy_task.cpp`, `src/puppies/modular_bed.cpp`, and `src/common/http/httpc.cpp`.
- Reference cross-file log components with `LOG_COMPONENT_REF(component)`, as in `src/puppies/xbuddy_extension.cpp` and `src/logging/log_platform.cpp`.
- Log through severity macros `log_debug`, `log_info`, `log_warning`, `log_error`, and `log_critical` from `src/logging/include/logging/log.hpp`; avoid direct `_log_event(...)` except for special dynamic-component paths such as `src/puppies/Dwarf.cpp`.
- Use printf-style format strings with the typed integer macros already used in the codebase, such as `PRIu32` in `src/puppies/PuppyBootstrap.cpp` and `src/puppies/xbuddy_extension.cpp`.
- Keep logging component documentation generated from code by `utils/logging/generate_overview.py`; the generated output is `doc/logging_components.md` and the hook is configured in `.pre-commit-config.yaml`.
- Python integration tests use the standard `logging` module for diagnostic progress, as in `tests/integration/conftest.py` and `tests/integration/test_prusa_link.py`.

## Comments

- Explain protocol, hardware, firmware, and test-environment reasons rather than restating code mechanics. Examples include timeout concerns in `src/common/http/httpc.cpp`, power-panic behavior in `src/puppies/PuppyModbus.cpp`, and simulator setup in `tests/integration/conftest.py`.
- Keep comments close to non-obvious test scaffolding, such as source substitution in `tests/unit/connect/CMakeLists.txt`, fake time in `tests/unit/connect/time_mock.cpp`, and logging stubs in `tests/stubs/logging/log.hpp`.
- Do not add file header boilerplate to owned files, per `doc/contributing.md`; preserve required third-party headers under `lib/`, `include/stm32f4_hal/`, and `src/device/`.
- Mark generated files clearly when they are committed. `include/common/visit_all_struct_fields.hpp` says it is auto-generated by `utils/persistent_stores/visit_all_struct_fields_generator.py`, and `utils/logging/generate_overview.py` writes a generated notice into `doc/logging_components.md`.
- Not applicable. The repo is C/C++ and Python.
- Use Doxygen-style comments for public C++ API contracts and generated documentation, as in `src/logging/include/logging/log.hpp`, `src/common/str_utils.hpp`, and `include/puppies/BootloaderProtocol.hpp`.
- G-code command documentation has a repo-specific Markdown-in-comment format in `doc/contributing.md`; use that format when editing commands under `src/marlin_stubs/`.

## Function Design

## Module Design

## Generated File Conventions

- `CMakePresets.json` is generated from `utils/presets/presets.json` by `python utils/build.py --generate-cmake-presets`; `.pre-commit-config.yaml` runs this hook when JSON inputs change.
- `doc/logging_components.md` is generated by `utils/logging/generate_overview.py`; `.pre-commit-config.yaml` runs the generator and the generated document includes a "do not edit directly" notice.
- `include/common/visit_all_struct_fields.hpp` is generated by `utils/persistent_stores/visit_all_struct_fields_generator.py`; edit the generator rather than hand-editing the generated table.
- `src/lang/po/Prusa-Firmware-Buddy.pot` and font/resource outputs are maintained by scripts under `utils/translations_and_fonts/`, including `utils/translations_and_fonts/generate_pot.sh`, `utils/translations_and_fonts/new_translations.sh`, and `utils/translations_and_fonts/generate_all_fonts.sh`.
- `src/gui/res/cc/*.hpp` and `src/gui/res/fnt_png/*.png` are resource/font outputs owned by the translation and font tooling under `utils/translations_and_fonts/`; update source assets and rerun the relevant generator.
- Automata generated for tests are written to CMake binary directories, such as `${CMAKE_BINARY_DIR}/http.cpp` in `tests/unit/common/automata/CMakeLists.txt` and `${CMAKE_CURRENT_BINARY_DIR}/http_resp_automaton.cpp` in `tests/unit/connect/CMakeLists.txt`; do not commit those build outputs.
- Persistent-store hash headers are generated through `src/persistent_stores/GenerateJournalHashes.cmake` using `utils/persistent_stores/journal_hashes_generator.py`; generated output paths are target-specific and owned by CMake.
- Firmware artifacts such as `.bin`, `.bbf`, `.dfu`, linker maps, and LittleFS resources are generated by `CMakeLists.txt`, `cmake/Utilities.cmake`, and `utils/build.py`; keep generated build outputs under ignored build directories.
- Pre-commit excludes vendored and generated-heavy third-party paths in `.pre-commit-config.yaml`, including `lib/Catch2/`, `lib/Drivers/`, `lib/Middlewares/Third_Party/`, `lib/Prusa-Firmware-MMU/`, `lib/tinyusb/`, and selected generated test data.
- When changing generator inputs, run the owning generator or pre-commit hook and include the regenerated committed outputs only when those outputs are tracked by the repo.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## Pattern Overview

- `CMakeLists.txt` creates one `firmware` executable, then `src/CMakeLists.txt` adds board-specific source trees according to `BOARD`, `PRINTER`, and generated option headers from `ProjectOptions.cmake`.
- `src/buddy/main.cpp` is the master-board runtime shell: it initializes HAL/peripherals, creates FreeRTOS tasks, coordinates `TaskDeps`, and delegates printing logic to `app_run()` in `src/common/appmain.cpp`.
- `lib/Marlin/Marlin/src` supplies the motion planner, G-code queue, thermal management, and printer mechanics; Buddy-specific orchestration wraps it through `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, and `src/marlin_stubs`.
- `src/gui`, `src/connect`, `src/transfers`, `src/puppies`, and `src/persistent_stores` are feature/application layers built into the same firmware target when options enable them.
- `src/puppy/dwarf`, `src/puppy/modularbed`, and `src/puppy/xbuddy_extension` are separate firmware personalities selected by `BOARD`, not ordinary modules inside the master-board runtime.

## Layers

- Purpose: Select printer, board, MCU, bootloader mode, feature flags, generated option headers, subprojects, firmware packaging, and linked libraries.
- Location: `CMakeLists.txt`, `ProjectOptions.cmake`, `CMakePresets.json`, `cmake/Options.cmake`, `cmake/GccArmNoneEabi.cmake`, `utils/build.py`, `utils/bootstrap.py`
- Contains: `firmware` target creation, `BuddyHeaders`, `Marlin_Config`, `FreeRTOS_Config`, `target_sources(...)`, `target_link_libraries(...)`, generated `include/option/*.h` files under the build directory, `.bbf`/`.dfu` packaging hooks.
- Depends on: `lib/CMakeLists.txt`, `lib/AddMarlin.cmake`, `lib/Add*.cmake`, `utils/gen_puppies_descriptor.py`, `utils/pack_fw.py`, `utils/mklittlefs.py`
- Used by: Every source layer through option macros such as `HAS_GUI()`, `HAS_PUPPIES()`, `BUDDY_ENABLE_CONNECT()`, board macros from `include/device/board.h`, and printer macros from `include/printers.h`.
- Purpose: Provide startup assembly, linker scripts, CMSIS/HAL setup, interrupt routing, core clock/timer initialization, and MCU-specific peripheral entrypoints.
- Location: `src/device`, `src/device/stm32f4`, `src/device/stm32g0`, `src/puppy/xbuddy_extension`, `include/device`, `include/stm32f4_hal`, `include/stm32g0_hal`
- Contains: Startup sources such as `src/device/stm32f4/startup/stm32f427zitx.s`, linker scripts such as `src/device/stm32f4/linker/stm32f42x_boot.ld`, HAL glue such as `src/device/stm32f4/hal_msp.cpp`, and board interrupt files such as `src/device/stm32f4/interrupts_XBUDDY.cpp`.
- Depends on: STM32 HAL/CMSIS libraries from `lib/Drivers`, FreeRTOS configuration from `src/device/CMakeLists.txt`, and `BuddyHeaders` from `CMakeLists.txt`.
- Used by: `src/buddy/main.cpp`, puppy entrypoints in `src/puppy/dwarf/main.cpp` and `src/puppy/modularbed/main.cpp`, and low-level hardware code in `src/hw`.
- Purpose: Initialize board GPIO, DMA, ADC, timers, I2C/SPI/UART, USB, filesystems, watchdogs, power, and board-specific hardware configuration.
- Location: `src/buddy`, `src/hw`, `include/buddy`, `include/usb_host`, `include/device`
- Contains: Master-board boot orchestration in `src/buddy/main.cpp`, USB device task in `src/buddy/usb_device.cpp`, USB host integration in `src/buddy/usb_host.cpp`, filesystem mounts in `src/buddy/filesystem.cpp`, hardware configuration in `src/hw/mk4_ix_coreone/hw_configuration.cpp`, `src/hw/xl/hw_configuration.cpp`, and `src/hw/xbuddy_xlbuddy/hw_configuration_common.cpp`.
- Depends on: `src/device`, STM32 HAL, TinyUSB, FatFS, littlefs, libsysbase, generated options, and board macros from `include/device/board.h`.
- Used by: The FreeRTOS startup path in `src/buddy/main.cpp`, application logic in `src/common/appmain.cpp`, GUI display/touch code in `src/gui`, Connect/WUI network setup, and Marlin hardware adapters.
- Purpose: Wrap FreeRTOS primitives, allocate system tasks, coordinate startup readiness, and provide task-safe synchronization helpers.
- Location: `src/freertos`, `src/freertos/include/freertos`, `include/tasks.hpp`, `src/common/tasks.cpp`, `include/buddy/ccm_thread.hpp`
- Contains: Mutex/queue/semaphore wrappers in `src/freertos`, static idle/timer task memory in `src/freertos/system_tasks.cpp`, event-group dependency masks in `include/tasks.hpp`, and CCMRAM thread definition macros in `include/buddy/ccm_thread.hpp`.
- Depends on: `FreeRTOS::FreeRTOS`, CMSIS-OS headers, board memory sections, and generated feature options.
- Used by: `src/buddy/main.cpp`, `src/common/appmain.cpp`, `src/gui/guimain.cpp`, `src/connect/run.cpp`, `src/puppies/puppy_task.cpp`, `src/buddy/usb_device.cpp`, and logging/task code in `src/logging`.
- Purpose: Run Marlin setup/loop, serialize UI/network requests into server-side printing operations, expose events/state to client tasks, and add Prusa-specific G-code handlers.
- Location: `lib/Marlin/Marlin/src`, `lib/AddMarlin.cmake`, `src/common/appmain.cpp`, `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, `src/common/marlin_server_request.hpp`, `src/common/marlin_client_queue.hpp`, `src/marlin_stubs`
- Contains: Marlin source selection in `lib/AddMarlin.cmake`, server loop in `src/common/marlin_server.cpp`, task-bound client registration in `src/common/marlin_client.cpp`, request/event queues in `src/common/marlin_server_request.hpp` and `src/common/marlin_client_queue.hpp`, and Buddy G-code implementations such as `src/marlin_stubs/M862_1.cpp` and `src/marlin_stubs/pause/M600.cpp`.
- Depends on: `lib/Marlin/Marlin/src`, Arduino Core, TMCStepper, FreeRTOS wrappers, `marlin_server_types`, `buddy_utils`, error codes, config store, and feature options.
- Used by: GUI screens in `src/gui`, Connect client in `src/connect`, transfers in `src/transfers`, selftest and feature modules in `src/common/feature`, MMU code in `src/mmu2`, and puppy/toolchanger integration in `src/puppies`.
- Purpose: Own printer application state outside raw Marlin, including config, metrics, sensors, selftest, G-code scanning, media prefetch, safety timers, feature managers, and utility code shared by UI/network paths.
- Location: `src/common`, `src/common/feature`, `src/common/selftest`, `src/common/gcode`, `src/common/marlin_server_types`, `src/module/utils`
- Contains: Main application loop in `src/common/appmain.cpp`, sensor and filament support in `src/common/filament_sensor*.cpp`, metrics in `src/common/metric.cpp`, feature modules such as `src/common/feature/chamber/chamber.cpp`, and pure/shared helper libraries in `src/module/utils`.
- Depends on: Marlin APIs, hardware shell, config store, FreeRTOS wrappers, generated options, logging, and `buddy_utils`.
- Used by: `src/buddy/main.cpp`, `src/gui`, `src/connect`, `src/marlin_stubs`, `src/puppies`, and unit tests under `tests/unit/common`.
- Purpose: Render display UI, manage screen stack/dialogs, handle input, expose print controls, display errors, and mediate GUI readiness for printing.
- Location: `src/gui`, `src/gui/dialogs`, `src/gui/screen`, `src/gui/menu_item`, `src/gui/footer`, `src/gui/wizard`, `src/guiapi`
- Contains: GUI task loop in `src/gui/guimain.cpp`, screen stack in `src/gui/ScreenHandler.hpp`, fixed-storage screen factory in `src/gui/ScreenFactory.hpp`, screen classes such as `src/gui/screen_home.hpp`, and resolution-specific modules under `src/gui/resolution_240x320` and `src/gui/resolution_480x320`.
- Depends on: `marlin_client` from `src/common/marlin_client.hpp`, config store, `src/common` models, resources, display/touch hardware, generated options, and language translation code in `src/lang`.
- Used by: `src/buddy/main.cpp` via `StartDisplayTask`, user-facing workflows, bootstrap/resource update progress, crash/error display, and GUI unit tests under `tests/unit/gui`.
- Purpose: Provide Prusa Connect client behavior, network-backed printer state/control, downloads, transfer recovery, syslog/metrics transport, and the embedded web UI backend.
- Location: `src/connect`, `src/connect/tls`, `src/transfers`, `src/state`, `src/syslog`, `lib/WUI`
- Contains: Connect task entry in `src/connect/run.cpp`, abstract printer contract in `src/connect/printer.hpp`, Marlin-backed implementation in `src/connect/marlin_printer.cpp`, transfer state machines in `src/transfers`, Connect-visible state mapping in `src/state/printer_state.cpp`, and WUI HTTP implementation in `lib/WUI`.
- Depends on: WUI/LwIP, mbedTLS, hardware RNG, config store, filesystem mounts, `marlin_client`, `marlin_vars`, and generated options `BUDDY_ENABLE_WUI()` and `BUDDY_ENABLE_CONNECT()`.
- Used by: `src/buddy/main.cpp` through `start_network_task(...)` and `StartConnectTask`, Connect/WUI tests in `tests/unit/connect`, `tests/unit/transfers`, and `tests/unit/lib/WUI`.
- Purpose: Persist configuration, mount internal/USB/semihosting filesystems, migrate old EEPROM data, and expose POSIX-like file operations through libsysbase devoptabs.
- Location: `src/persistent_stores`, `src/buddy/filesystem*.cpp`, `include/buddy/filesystem*.h`, `lib/libsysbase`
- Contains: Config store entry in `src/persistent_stores/store_instances/config_store/store_instance.cpp`, store definitions/migrations in `src/persistent_stores/store_instances/config_store/store_definition.cpp`, journal backend in `src/persistent_stores/journal/backend.cpp`, USB FatFS mount named `usb` in `src/buddy/filesystem_fatfs.cpp`, internal littlefs mount named `internal` in `src/buddy/filesystem_littlefs_internal.cpp`, and root device listing in `src/buddy/filesystem_root.cpp`.
- Depends on: EEPROM/NFC driver initialization in `src/buddy/main.cpp`, `lib/libsysbase`, littlefs, FatFS, CRC utilities, generated options, and C++ reflection helpers under `include/common`.
- Used by: GUI settings, Connect configuration, print file access, crash dump storage, resources/bootstrap logic, and tests under `tests/unit/persistent_stores`.
- Purpose: Package web assets, ESP firmware blobs, puppy firmware blobs, MMU firmware, QOI image data, bootloader update resources, and translation data.
- Location: `src/resources`, `src/gui/res`, `src/lang`, `utils/resources`, `utils/translations_and_fonts`
- Contains: Resource image setup in `src/resources/CMakeLists.txt`, bootstrap/hash logic in `src/resources/bootstrap.cpp`, static web files in `src/resources/web`, ESP blobs in `src/resources/esp32` and `src/resources/esp8266`, translation providers in `src/lang/translation_provider_FILE.cpp` and `src/lang/translation_provider_CPUFLASH.cpp`, and `.po` files in `src/lang/po`.
- Depends on: littlefs image CMake helpers in `cmake/Littlefs.cmake`, Python generators in `utils/resources/generate_hash_file.py`, `utils/translations_and_fonts/lang.py`, and generated options for resources/translations.
- Used by: Firmware packaging in `CMakeLists.txt`, GUI image/font access, bootloader/resources bootstrap in `src/buddy/main.cpp`, WUI assets, ESP flashing, and puppy bootload flows.
- Purpose: Build and run auxiliary board firmware, bootstrap/flash puppies from master firmware resources, and communicate with Dwarf, ModularBed, and xBuddy Extension devices over Modbus/fifo protocols.
- Location: `src/puppies`, `include/puppies`, `src/puppy/dwarf`, `src/puppy/modularbed`, `src/puppy/shared`, `src/puppy/xbuddy_extension`, `src/puppy/xbuddy_extension_shared`
- Contains: Master-side puppy task in `src/puppies/puppy_task.cpp`, bootloader protocol in `src/puppies/BootloaderProtocol.cpp`, Dwarf abstraction in `src/puppies/Dwarf.cpp`, ModularBed abstraction in `src/puppies/modular_bed.cpp`, Dwarf firmware entrypoint in `src/puppy/dwarf/main.cpp`, ModularBed firmware entrypoint in `src/puppy/modularbed/main.cpp`, and xBuddy Extension firmware target setup in `src/puppy/xbuddy_extension/CMakeLists.txt`.
- Depends on: `lib/liblightmodbus`, `src/common`, Marlin toolchanger APIs, resources packaged by `src/resources/CMakeLists.txt`, and `ExternalProject_Add` flows in `CMakeLists.txt`.
- Used by: XL/iX/COREONE master firmware when `HAS_PUPPIES()`, `HAS_PUPPIES_BOOTLOADER()`, or `HAS_XBUDDY_EXTENSION()` options are enabled.
- Purpose: Provide firmware dependencies and upstream code kept under repository control.
- Location: `lib`, `lib/Marlin`, `lib/Prusa-Firmware-MMU`, `lib/Prusa-Error-Codes`, `lib/Drivers`, `lib/Middlewares`, `lib/WUI`, `lib/tinyusb`
- Contains: CMake wrappers in `lib/Add*.cmake`, upstream source trees, STM32 HAL/CMSIS, FreeRTOS, TinyUSB, mbedTLS, Prusa error codes, MMU firmware, WUI, TMCStepper, CrashCatcher, and utility libraries.
- Depends on: `lib/CMakeLists.txt` inclusion from root `CMakeLists.txt` and project-specific interface targets such as `BuddyHeaders`.
- Used by: Almost every firmware target through `target_link_libraries(firmware ...)` in `CMakeLists.txt`.

## Data Flow

- Startup dependencies use FreeRTOS event bits in `include/tasks.hpp` and initialization in `src/common/tasks.cpp`.
- Printing state is centralized around `marlin_server::server_t`, request/event queues, and `marlin_vars` in `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, and `src/common/marlin_vars.cpp`.
- GUI navigation state uses the `Screens` stack in `src/gui/ScreenHandler.hpp` and fixed storage from `src/gui/ScreenFactory.hpp`.
- Persistent configuration uses `config_store()` from `src/persistent_stores/store_instances/config_store/store_instance.hpp`.
- Network-visible device state is mapped in `src/state/printer_state.cpp`.
- Compile-time state is generated from `ProjectOptions.cmake` into build-tree `include/option/*.h` headers consumed through `#include <option/...>`.

## Key Abstractions

- Purpose: Aggregate selected sources into one embedded image for a selected `BOARD`/`PRINTER`.
- Examples: `CMakeLists.txt`, `src/CMakeLists.txt`, `src/buddy/CMakeLists.txt`, `src/common/CMakeLists.txt`, `src/gui/CMakeLists.txt`
- Pattern: Global executable assembled through nested `target_sources(firmware ...)` and option-gated `add_subdirectory(...)`.
- Purpose: Convert CMake feature decisions into C/C++ preprocessor macros and `option::` constants.
- Examples: `ProjectOptions.cmake`, `cmake/Options.cmake`, `include/option/option_boolean.h.in`, generated build-tree `include/option/has_gui.h`
- Pattern: CMake functions `define_boolean_option(...)` and `define_enum_option(...)` generate headers consumed by source files such as `src/buddy/main.cpp`.
- Purpose: Encapsulate board/printer identity checks and keep source conditions readable.
- Examples: `include/device/board.h`, `include/printers.h`, `include/device/mcu.h`
- Pattern: `BOARD_IS_*()`, `PRINTER_IS_PRUSA_*()`, and `MCU_IS_*()` macro helpers generated from compile definitions in `CMakeLists.txt`.
- Purpose: Model readiness relationships between startup components and runtime tasks.
- Examples: `include/tasks.hpp`, `src/common/tasks.cpp`, `src/buddy/main.cpp`, `src/gui/guimain.cpp`, `src/puppies/puppy_task.cpp`
- Pattern: FreeRTOS event group masks with `TaskDeps::wait(...)` and `TaskDeps::provide(...)`.
- Purpose: Keep Marlin operations serialized on the default task while GUI, Connect, and other tasks submit requests safely.
- Examples: `src/common/marlin_server.hpp`, `src/common/marlin_client.hpp`, `src/common/marlin_server_request.hpp`, `src/common/marlin_client_queue.hpp`
- Pattern: Single server loop plus per-task client IDs, one-slot request queue, event masks, and acknowledgement events.
- Purpose: Manage GUI screens without heap allocation and preserve navigation state.
- Examples: `src/gui/ScreenFactory.hpp`, `src/gui/ScreenHandler.hpp`, `src/gui/screen_home.hpp`, `src/gui/dialogs/DialogHandler.cpp`
- Pattern: `ScreenFactory::Creator` creates screens inside fixed storage, while `Screens` keeps a bounded stack of creators and init state.
- Purpose: Persist typed printer settings and migrate old EEPROM/config versions.
- Examples: `src/persistent_stores/store_instances/config_store/store_definition.hpp`, `src/persistent_stores/store_instances/config_store/store_instance.cpp`, `src/persistent_stores/journal/backend.cpp`
- Pattern: Typed store items backed by append-only journal transactions, CRC validation, bank selection, and migration hooks.
- Purpose: Define compile-time/log-section components and runtime destinations for RTT, syslog, USB, file, and buffer logging.
- Examples: `src/logging/include/logging/log.hpp`, `src/logging/log.cpp`, `src/buddy/logging.cpp`, `src/logging/CMakeLists.txt`
- Pattern: `LOG_COMPONENT_DEF(...)` places components in a linker section, and `logging::Destination` instances are registered at runtime.
- Purpose: Expose internal flash, USB, BBF, semihosting, and root directory through libsysbase/newlib-style operations.
- Examples: `src/buddy/filesystem.cpp`, `src/buddy/filesystem_fatfs.cpp`, `src/buddy/filesystem_littlefs_internal.cpp`, `src/buddy/filesystem_root.cpp`, `lib/libsysbase`
- Pattern: `devoptab_t` device implementations registered with `AddDevice(...)` and used by POSIX-like file APIs.
- Purpose: Represent auxiliary boards, flash them, verify fingerprints, refresh registers, and recover after communication faults.
- Examples: `src/puppies/PuppyBootstrap.cpp`, `src/puppies/PuppyModbus.cpp`, `src/puppies/Dwarf.cpp`, `src/puppies/modular_bed.cpp`, `src/puppies/puppy_task.cpp`
- Pattern: Master-side task owns Modbus scanning/bootstrap/runtime refresh and exposes device-specific classes for Dwarf, ModularBed, and xBuddy Extension.

## Entry Points

- Location: `utils/build.py`
- Triggers: Developer or CI invokes `python utils/build.py`.
- Responsibilities: Bootstrap dependencies, expand presets from `utils/presets`, configure CMake builds, and place products under `build/products`.
- Location: `CMakeLists.txt`
- Triggers: `cmake` configure/generate step or `utils/build.py`.
- Responsibilities: Define project language/version, global compiler/linker flags, interface targets, Marlin and third-party config targets, puppy external projects, tests for host builds, firmware packaging, and final firmware link libraries.
- Location: `src/CMakeLists.txt`
- Triggers: Root `CMakeLists.txt` after `add_executable(firmware)`.
- Responsibilities: Add board-specific source directories, including master-board modules, puppy firmware modules, or xBuddy Extension firmware modules.
- Location: `src/buddy/main.cpp`
- Triggers: MCU reset vector/startup assembly.
- Responsibilities: Minimal pre-RTOS setup, FreeRTOS scheduler startup, C++ runtime initialization in `startup_task`, board/peripheral initialization in `main_cpp`, task creation, bootstrap/error-screen flow, resources/bootloader updates, and dependency coordination.
- Location: `src/common/appmain.cpp`
- Triggers: `StartDefaultTask()` in `src/buddy/main.cpp`.
- Responsibilities: Wait for startup dependencies, set up Marlin logging, call Marlin `setup()`, initialize `marlin_server`, mark default task ready, and run `marlin_server::loop()`.
- Location: `src/gui/guimain.cpp`
- Triggers: `StartDisplayTask()` in `src/buddy/main.cpp`.
- Responsibilities: Initialize GUI/display, show bootstrap/error/home screens, register as a Marlin client, process screen/dialog loops, and signal GUI readiness.
- Location: `src/connect/run.cpp`
- Triggers: `StartConnectTask()` or `StartConnectTaskError()` in `src/buddy/main.cpp`.
- Responsibilities: Create `Connect` with either `MarlinPrinter` or `ErrorPrinter`, then run the Connect client loop.
- Location: `src/puppies/puppy_task.cpp`
- Triggers: `buddy::puppies::start_puppy_task()` in `src/buddy/main.cpp`.
- Responsibilities: Wait for ESP flashing, bootstrap puppies, verify/scan connected boards, signal readiness, and maintain periodic device refresh.
- Location: `src/puppy/dwarf/main.cpp`
- Triggers: Dwarf board reset vector/startup assembly for `BOARD=DWARF`.
- Responsibilities: Minimal HAL setup, FreeRTOS scheduler startup, C++ runtime initialization, and Dwarf startup task dispatch.
- Location: `src/puppy/modularbed/main.cpp`
- Triggers: ModularBed board reset vector/startup assembly for `BOARD=MODULARBED`.
- Responsibilities: HAL/system setup, watchdog setup, Modbus register/protocol initialization, measurement/PWM/control logic initialization, and FreeRTOS scheduler startup.
- Location: `src/puppy/xbuddy_extension/main.cpp`
- Triggers: xBuddy Extension board reset vector/startup assembly for `BOARD=XBUDDY_EXTENSION`.
- Responsibilities: STM32H5 firmware entrypoint compiled with `src/puppy/xbuddy_extension/CMakeLists.txt`, shared MMU protocol support, extension variant selection, and extension app loop.
- Location: `tests/unit/CMakeLists.txt`
- Triggers: Non-cross-compiling CMake configure with `UNITTESTS_ENABLE`.
- Responsibilities: Define `UNITTESTS`, enable RTTI for tests, create `catch_main`, provide `add_catch_test(...)`, and include test subdirectories.
- Location: `tests/integration/conftest.py`
- Triggers: `pytest tests/integration --firmware <firmware.bin to test>`.
- Responsibilities: Configure simulator-driven integration tests for supported firmware builds and provide pytest fixtures/actions.

## Error Handling

- `src/buddy/main.cpp` routes startup failures, watchdog warnings, HAL errors, asserts, and error-screen fast path through `Error_Handler()`, `app_error()`, `init_error_screen()`, `crash_dump::save_message(...)`, and `trigger_crash_dump()`.
- `include/stm32f4_hal/FreeRTOSConfig.h` and `include/stm32g0_hal/FreeRTOSConfig.h` map FreeRTOS `configASSERT` failures into `_bsod(...)` or `fatal_error(...)`.
- `src/common/crash_dump/CMakeLists.txt` wires CrashCatcher sources into master-board firmware; `src/puppy/dwarf/CMakeLists.txt` and `src/puppy/modularbed/CMakeLists.txt` wire ARMv6-M CrashCatcher sources for puppy boards.
- `src/common/safe_state.cpp`, `src/puppy/modularbed/main.cpp`, and `src/puppy/dwarf/main.cpp` push hardware into safe outputs before hard failure loops.
- `lib/Prusa-Error-Codes` and generated `error_codes` targets are linked from `CMakeLists.txt`; user/Connect-visible mappings appear in `src/state/printer_state.cpp`.
- `src/puppies/PuppyBootstrap.cpp`, `src/puppies/Dwarf.cpp`, and `src/puppies/modular_bed.cpp` convert auxiliary-board failures into `fatal_error(ErrCode::...)` or crash-dump download/report flows.

## Cross-Cutting Concerns

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.

<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.

<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.

<!-- GSD:profile-end -->
