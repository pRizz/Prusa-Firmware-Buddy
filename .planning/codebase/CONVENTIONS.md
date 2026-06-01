# Coding Conventions

**Analysis Date:** 2026-06-01

## Naming Patterns

**Files:**

- Use `snake_case.cpp`, `snake_case.hpp`, `snake_case.h`, and `snake_case.c` for new owned C/C++ files, following `doc/contributing.md`; examples include `src/connect/printer_common.cpp`, `src/common/str_utils.hpp`, and `tests/unit/common/str_utils_test.cpp`.
- Keep established subsystem and externally constrained names when extending existing code, including hardware part names in `src/hw/TCA6408A.cpp`, product names in `src/puppies/Dwarf.cpp`, Marlin command names in `src/marlin_stubs/M862_5.cpp`, HAL names in `include/stm32g0_hal/stm32g0xx_hal_conf.h`, and generated resource names in `src/gui/res/cc/font_regular_11x18_latin.hpp`.
- Use `CMakeLists.txt` per build directory, with subsystem test registration in files such as `tests/unit/common/CMakeLists.txt` and `tests/unit/connect/CMakeLists.txt`.
- Use Python script names that match surrounding `utils/` style: underscore names such as `utils/check-requirements.py`, generator names such as `utils/logging/generate_overview.py`, and package directories such as `utils/persistent_stores/`.
- Use test file names that identify the unit under test: C++ tests use `*_test.cpp` or `*_tests.cpp` such as `tests/unit/common/circle_buffer_test.cpp` and `tests/unit/connect/planner.cpp`; pytest modules use `test_*.py` such as `tests/integration/test_prusa_link.py`.

**Functions:**

- Use `snake_case` for new repo-owned free functions and methods, matching `doc/contributing.md` and examples such as `from_chars_light` in `src/common/str_utils.hpp`, `advance_time_s` in `tests/unit/connect/time_mock.cpp`, and `log_destination_register` in `src/logging/include/logging/log.hpp`.
- Preserve legacy or external contract method names when editing code already using that style, such as `window_t::DisableLongHoldScreenAction` in `src/guiapi/src/window.cpp`, hardware classes in `src/hw/FUSB302B.cpp`, and Marlin command surfaces under `src/marlin_stubs/`.
- Use `constexpr`, `consteval`, or `static inline` helper functions for compile-time or header-local logic when the surrounding file already uses them, as in `src/common/str_utils.hpp` and `src/common/filament_eeprom.hpp`.
- For Python, use lowercase `snake_case` functions and fixtures, as in `tests/integration/conftest.py`, `tests/blockdevice/test_block_device.py`, and `utils/logging/generate_overview.py`.

**Variables:**

- Use `snake_case` for local variables, members, namespaces, and enum-class items in new owned code, as directed by `doc/contributing.md`; examples include `mock_time` in `tests/unit/connect/time_mock.cpp`, `content_length_rest` in `src/common/http/httpc.cpp`, and `printer_flash_dir` in `tests/integration/conftest.py`.
- Use `SCREAMING_CASE` for global constants and preprocessor symbols, matching examples such as `PRINTER_TYPE` in `CMakeLists.txt`, `LOG_LOWEST_SEVERITY` in `src/logging/include/logging/log.hpp`, and `BLOCK_SIZE` in `tests/blockdevice/test_block_device.py`.
- Match local class-constant style when extending existing classes. Some C++ classes use PascalCase private constants such as `RectTextLayout::MaxLines` in `src/common/str_utils.hpp`; some embedded modules use all-caps constants such as `FAN_CNT` in `src/puppies/xbuddy_extension.cpp`.
- Bright Builds `standards/core/code-shape.md` applies because `standards-overrides.md` has no active override: new internal nullable or absence-like names should use a visible `maybe_` prefix when practical. Keep public, legacy, wire, HAL, and overridden method names stable in files such as `src/connect/printer.hpp`, `include/puppies/xbuddy_extension.hpp`, and `tests/unit/connect/mock_printer.h`.

**Types:**

- Use `PascalCase` for new C++ classes, structs, and enum classes, matching `doc/contributing.md` and examples such as `Printer` in `src/connect/printer.hpp`, `OutBuffer` in `src/common/http/httpc.cpp`, `MockPrinter` in `tests/unit/connect/mock_printer.h`, and `Timestamp` in `src/logging/include/logging/log.hpp`.
- Do not add `_t` suffixes for new owned C++ types, per `doc/contributing.md`. Existing legacy and C-compatible names such as `resume_state_t` in `src/common/marlin_server.hpp` and `SelftestAxis_t` in `src/common/selftest_axis_type.hpp` are surrounding-style exceptions.
- Prefer `enum class` for typed states and protocol enums, as seen in `src/logging/include/logging/log.hpp`, `src/connect/printer.hpp`, and `include/puppies/PuppyModbus.hpp`.

## Code Style

**Formatting:**

- Format C/C++ with clang-format using `.clang-format`. Key settings include 4-space indentation, no tabs, right pointer alignment, custom brace wrapping, `ColumnLimit: 0`, `SortIncludes: false`, `InsertBraces: true`, and preserved include blocks.
- Format Python with YAPF through `.pre-commit-config.yaml`; use `# yapf: disable` and `# yapf: enable` only for parser-heavy blocks such as `tests/integration/conftest.py`, `utils/build.py`, and `utils/dfu.py`.
- Format CMake with `cmake-format` using `.cmake-format.py`; file lists in `target_sources(PUBLIC|PRIVATE|INTERFACE ...)` are sortable, line width is 100, and wrapped calls dangle closing parentheses.
- Install and run pre-commit hooks from `.pre-commit-config.yaml` for formatting, generated-doc updates, preset generation, requirement synchronization, trailing whitespace, final newline, and mixed line endings. `doc/contributing.md` states that build server checks reject improperly formatted pull requests.
- Use `#pragma once` for new headers, following `doc/contributing.md` and common headers such as `src/connect/printer.hpp`, `include/puppies/PuppyModbus.hpp`, and `tests/unit/logging/utils.hpp`.
- Do not add new author, creation-time, or copyright headers to owned files, per `doc/contributing.md`; keep third-party headers intact under paths such as `lib/`, `include/stm32f4_hal/`, and `src/device/stm32g0/linker/`.

**Linting:**

- No clang-tidy, cppcheck, mypy, or ruff configuration is detected in root config files such as `.clangd`, `pyproject.toml`, and `.pre-commit-config.yaml`.
- CMake applies baseline C/C++ warnings globally with `-Wall` and `-Wsign-compare` in `CMakeLists.txt`; firmware targets add `-Wextra`, selected suppressions, and `-Werror=delete-non-virtual-dtor` in `CMakeLists.txt`.
- Jenkins PR builds pass `-DCUSTOM_COMPILE_OPTIONS:STRING="-Werror"` through `utils/holly/build-pr.jenkins`, so new warnings in compiled targets should be treated as CI failures.
- `.clangd` adds editor diagnostics and compile flags including `-std=c++23`, `-Wno-deprecated-volatile`, and `-ferror-limit=0`; keep IDE-only flags there instead of duplicating them in `CMakeLists.txt`.

## Import Organization

**Order:**

1. Put the file's own local header first when present, as in `src/common/http/httpc.cpp` including `"httpc.hpp"` before other headers.
1. Group related local quoted headers next, as in `src/common/http/httpc.cpp` with `"os_porting.hpp"`, `"resp_parser.h"`, `"chunked.h"`, and `"debug.h"`.
1. Put system headers in angle brackets after local headers, as in `src/common/http/httpc.cpp` with `<cassert>`, `<cstring>`, `<cstdlib>`, and `<cstdarg>`.
1. Put project and library angle-bracket headers after system headers, as in `src/common/http/httpc.cpp` with `<common/printer_model.hpp>` and `<version/version.hpp>`.
1. Preserve manual include order because `.clang-format` sets `SortIncludes: false`; do not rely on automatic include sorting for C/C++.
1. In Python, use standard-library imports, a blank line, then third-party and local imports; examples are `tests/integration/conftest.py`, `tests/integration/test_prusa_link.py`, and `utils/logging/generate_overview.py`.

**Path Aliases:**

- No language-level path alias system is detected; include resolution is controlled by CMake target include directories in `CMakeLists.txt`, `ProjectOptions.cmake`, and subsystem `CMakeLists.txt` files.
- Test include order often intentionally puts stubs before real headers, such as `tests/unit/connect/CMakeLists.txt` placing `tests/stubs` before `include`; keep this order when adding test targets.
- Generated build headers live under CMake binary directories, such as `${CMAKE_CURRENT_BINARY_DIR}/http_resp_automaton.cpp` in `tests/unit/connect/CMakeLists.txt` and `${CMAKE_BINARY_DIR}/http.cpp` in `tests/unit/common/automata/CMakeLists.txt`.

## Error Handling

**Patterns:**

- Use explicit value-or-error return types for recoverable C++ paths. `src/common/http/httpc.cpp` uses `std::optional<Error>` for no-value errors and `std::variant<size_t, Error>` for value-or-error I/O results.
- Use `std::optional<T>` for absence in normal control flow, as in `include/puppies/xbuddy_extension.hpp`, `src/hw/TCA6408A.cpp`, and `tests/unit/connect/mock_printer.h`; new internal names should apply `maybe_` when practical under Bright Builds code-shape rules.
- Use small guard helpers or early returns to propagate errors instead of nesting; `src/common/http/httpc.cpp` uses `CHECKED(...)` to return an `Error` immediately.
- Use `std::errc` for parse status in lightweight parsing utilities such as `from_chars_light_result` in `src/common/str_utils.hpp` and assertions in `tests/unit/common/str_utils_test.cpp`.
- Use `assert(...)` for programmer invariants and impossible states, as in `src/puppies/PuppyModbus.cpp`, `src/common/http/httpc.cpp`, and `include/common/array_extensions.hpp`.
- Use `bsod(...)` or `fatal_error(...)` only for firmware-fatal conditions, as in `src/common/Pin.cpp`, `src/hw/FUSB302B.cpp`, and `src/bootloader/bootloader_update.cpp`; unit tests replace these with throwing stubs in `tests/unit/mock/bsod.cpp`.
- Use `message(FATAL_ERROR ...)` for invalid CMake configuration, as in `ProjectOptions.cmake` and `CMakeLists.txt`.
- In Python tools, return a nonzero status or raise a specific test error rather than silently swallowing failures, as in `utils/check-requirements.py` and `tests/integration/conftest.py`.

## Logging

**Framework:** custom firmware logging in `src/logging/include/logging/log.hpp`

**Patterns:**

- Define one log component per logical subsystem with `LOG_COMPONENT_DEF(name, logging::Severity::...)`, as in `src/puppies/puppy_task.cpp`, `src/puppies/modular_bed.cpp`, and `src/common/http/httpc.cpp`.
- Reference cross-file log components with `LOG_COMPONENT_REF(component)`, as in `src/puppies/xbuddy_extension.cpp` and `src/logging/log_platform.cpp`.
- Log through severity macros `log_debug`, `log_info`, `log_warning`, `log_error`, and `log_critical` from `src/logging/include/logging/log.hpp`; avoid direct `_log_event(...)` except for special dynamic-component paths such as `src/puppies/Dwarf.cpp`.
- Use printf-style format strings with the typed integer macros already used in the codebase, such as `PRIu32` in `src/puppies/PuppyBootstrap.cpp` and `src/puppies/xbuddy_extension.cpp`.
- Keep logging component documentation generated from code by `utils/logging/generate_overview.py`; the generated output is `doc/logging_components.md` and the hook is configured in `.pre-commit-config.yaml`.
- Python integration tests use the standard `logging` module for diagnostic progress, as in `tests/integration/conftest.py` and `tests/integration/test_prusa_link.py`.

## Comments

**When to Comment:**

- Explain protocol, hardware, firmware, and test-environment reasons rather than restating code mechanics. Examples include timeout concerns in `src/common/http/httpc.cpp`, power-panic behavior in `src/puppies/PuppyModbus.cpp`, and simulator setup in `tests/integration/conftest.py`.
- Keep comments close to non-obvious test scaffolding, such as source substitution in `tests/unit/connect/CMakeLists.txt`, fake time in `tests/unit/connect/time_mock.cpp`, and logging stubs in `tests/stubs/logging/log.hpp`.
- Do not add file header boilerplate to owned files, per `doc/contributing.md`; preserve required third-party headers under `lib/`, `include/stm32f4_hal/`, and `src/device/`.
- Mark generated files clearly when they are committed. `include/common/visit_all_struct_fields.hpp` says it is auto-generated by `utils/persistent_stores/visit_all_struct_fields_generator.py`, and `utils/logging/generate_overview.py` writes a generated notice into `doc/logging_components.md`.

**JSDoc/TSDoc:**

- Not applicable. The repo is C/C++ and Python.
- Use Doxygen-style comments for public C++ API contracts and generated documentation, as in `src/logging/include/logging/log.hpp`, `src/common/str_utils.hpp`, and `include/puppies/BootloaderProtocol.hpp`.
- G-code command documentation has a repo-specific Markdown-in-comment format in `doc/contributing.md`; use that format when editing commands under `src/marlin_stubs/`.

## Function Design

**Size:** Treat functions over roughly 161 lines as refactor triggers under `standards/core/code-shape.md`, and split by named workflow steps when the split improves clarity. Large embedded flows exist in areas such as `src/connect/planner.cpp`; new changes should prefer smaller helpers over extending those flows.

**Parameters:** Prefer explicit domain types, references, `std::optional`, and `std::variant` over ambiguous primitives when the surrounding module already uses them. Examples include `Printer::Params` in `src/connect/printer.hpp`, `RequestTiming` in `include/puppies/PuppyModbus.hpp`, and typed fixtures in `tests/integration/conftest.py`.

**Return Values:** Return structured status rather than hidden side effects for recoverable paths. Use `std::optional<Error>` and `std::variant<T, Error>` in HTTP and connection code such as `src/common/http/httpc.cpp`, `std::errc` in parsing code such as `src/common/str_utils.hpp`, and pytest assertions or `pytest.fail(...)` in integration tests such as `tests/integration/conftest.py`.

## Module Design

**Exports:** Headers expose module APIs directly through CMake include paths; examples include `src/connect/printer.hpp`, `src/logging/include/logging/log.hpp`, and `include/puppies/PuppyModbus.hpp`. Add implementation files to the owning `CMakeLists.txt`, such as `src/connect/CMakeLists.txt` or `tests/unit/common/CMakeLists.txt`.

**Barrel Files:** No TypeScript-style barrel files are used. Aggregate CMake targets and interface libraries provide grouping, such as `BuddyHeaders` in `CMakeLists.txt`, `catch_main` in `tests/unit/CMakeLists.txt`, and subsystem test targets in `tests/unit/*/CMakeLists.txt`.

**Anonymous/Internal Scope:** Prefer anonymous namespaces for file-local C++ helpers, matching `doc/contributing.md` and examples in `src/common/http/httpc.cpp` and `tests/unit/connect/planner.cpp`.

## Generated File Conventions

**Committed generated files:**

- `CMakePresets.json` is generated from `utils/presets/presets.json` by `python utils/build.py --generate-cmake-presets`; `.pre-commit-config.yaml` runs this hook when JSON inputs change.
- `doc/logging_components.md` is generated by `utils/logging/generate_overview.py`; `.pre-commit-config.yaml` runs the generator and the generated document includes a "do not edit directly" notice.
- `include/common/visit_all_struct_fields.hpp` is generated by `utils/persistent_stores/visit_all_struct_fields_generator.py`; edit the generator rather than hand-editing the generated table.
- `src/lang/po/Prusa-Firmware-Buddy.pot` and font/resource outputs are maintained by scripts under `utils/translations_and_fonts/`, including `utils/translations_and_fonts/generate_pot.sh`, `utils/translations_and_fonts/new_translations.sh`, and `utils/translations_and_fonts/generate_all_fonts.sh`.
- `src/gui/res/cc/*.hpp` and `src/gui/res/fnt_png/*.png` are resource/font outputs owned by the translation and font tooling under `utils/translations_and_fonts/`; update source assets and rerun the relevant generator.

**Build-only generated files:**

- Automata generated for tests are written to CMake binary directories, such as `${CMAKE_BINARY_DIR}/http.cpp` in `tests/unit/common/automata/CMakeLists.txt` and `${CMAKE_CURRENT_BINARY_DIR}/http_resp_automaton.cpp` in `tests/unit/connect/CMakeLists.txt`; do not commit those build outputs.
- Persistent-store hash headers are generated through `src/persistent_stores/GenerateJournalHashes.cmake` using `utils/persistent_stores/journal_hashes_generator.py`; generated output paths are target-specific and owned by CMake.
- Firmware artifacts such as `.bin`, `.bbf`, `.dfu`, linker maps, and LittleFS resources are generated by `CMakeLists.txt`, `cmake/Utilities.cmake`, and `utils/build.py`; keep generated build outputs under ignored build directories.

**Hook ownership:**

- Pre-commit excludes vendored and generated-heavy third-party paths in `.pre-commit-config.yaml`, including `lib/Catch2/`, `lib/Drivers/`, `lib/Middlewares/Third_Party/`, `lib/Prusa-Firmware-MMU/`, `lib/tinyusb/`, and selected generated test data.
- When changing generator inputs, run the owning generator or pre-commit hook and include the regenerated committed outputs only when those outputs are tracked by the repo.

______________________________________________________________________

*Convention analysis: 2026-06-01*
