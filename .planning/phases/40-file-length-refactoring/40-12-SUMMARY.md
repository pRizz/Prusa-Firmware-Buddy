---
phase: 40-file-length-refactoring
plan: 12
subsystem: embedded-hardware
tags: [stm32, hal, display, modbus, dwarf, xbuddy-extension, file-length]
requires:
  - phase: 40-file-length-refactoring
    provides: ordered high-risk file-length campaign through Plan 40-11
provides:
  - seven sub-629 hardware and auxiliary adapters
  - private STM32F4, display, Dwarf, Modbus, and xBuddy configuration modules
  - exact ordering and board-build evidence for retained HAL and protocol behavior
affects: [phase-40-verification, hardware-auxiliary, firmware-builds]
tech-stack:
  added: []
  patterns: [effect adapter with declarative configuration, exact ordered command tables]
key-files:
  created:
    - src/device/stm32f4/hal_msp_config.cpp
    - src/device/stm32f4/peripheral_config.cpp
    - src/guiapi/src/ili9488_commands.cpp
    - src/guiapi/src/st7789v_commands.cpp
    - src/puppies/dwarf_registers.cpp
    - src/puppy/shared/modbus/modbus_state.cpp
    - src/puppy/xbuddy_extension/hal_config.cpp
  modified:
    - src/device/stm32f4/hal_msp.cpp
    - src/device/stm32f4/peripherals.cpp
    - src/guiapi/src/ili9488.cpp
    - src/guiapi/src/st7789v.cpp
    - src/puppies/Dwarf.cpp
    - src/puppy/shared/modbus/ModbusProtocol.cpp
    - src/puppy/xbuddy_extension/hal.cpp
    - .bright-builds-rules-checks.tsv
key-decisions:
  - "Keep every HAL, RCC, MMIO, wire-I/O, exported callback, and fatal path in its original effect adapter."
  - "Move only deterministic configuration construction, display command policy, cached Dwarf register access, and Modbus checksum transition logic."
patterns-established:
  - "Hardware split: pure ordered configuration in a private sibling module, effects and public symbols in the original adapter."
  - "High-risk refactors require source-order comparison plus representative board links; no physical-hardware claim without hardware evidence."
requirements-completed: [D-05, D-07, D-08, D-09, D-11, D-12, D-14, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-28T00:51:36Z
duration: 57min
completed: 2026-07-27
---

# Phase 40 Plan 12: Hardware and Auxiliary Adapter Summary

**Seven STM32, display, Dwarf, Modbus, and xBuddy adapters reduced below 629 lines while retaining exact effect ordering, command streams, wire calls, timeouts, and fatal paths**

## Performance

- **Duration:** 57 min
- **Started:** 2026-07-27T23:54:20Z
- **Completed:** 2026-07-28T00:51:36Z
- **Tasks:** 2
- **Files modified:** 26

## Accomplishments

- Reduced all seven planned originals and every new source below the strict 629-line threshold, then removed exactly seven temporary ledger rows.
- Preserved STM32F4 clock/GPIO/DMA/IRQ order and exact ILI9488/ST7789V command bytes and delays in effect-adapter plus declarative-policy splits.
- Preserved Dwarf register and bus behavior, the 256-entry Modbus CRC table, and xBuddy HAL/init/fatal ordering across XL, Dwarf, COREONE Extension, and forced iX Extension builds.

## Task Commits

Each task was committed atomically:

1. **Task 1: Refactor STM32F4 and display adapters** - `29e402ae3`
2. **Task 2: Refactor Dwarf, Modbus, and xBuddy Extension adapters** - `66c24e55b`

## Files Created/Modified

- `src/device/stm32f4/hal_msp_config.*` and `peripheral_config.*` - Ordered clock, GPIO, DMA, IRQ, ADC, and peripheral configuration policy.
- `src/guiapi/src/ili9488_commands.*` and `st7789v_commands.*` - Exact display startup command tables and state.
- `src/puppies/dwarf_registers.cpp` - Cached register accessors and dirty-state setters without bus I/O.
- `src/puppy/shared/modbus/modbus_state.cpp` - Pure CRC transition using the unchanged ordered table.
- `src/puppy/xbuddy_extension/hal_config.*` - Deterministic UART, ADC, I2C, GPIO, and timer configuration construction.
- Original adapters and their `CMakeLists.txt` files - Retained effects/public symbols and linked the private modules under the same guards.
- `.bright-builds-rules-checks.tsv` - Removed seven qualified hardware/auxiliary temporary rows.

## Decisions Made

- Kept display transport, HAL/RCC/MMIO operations, Modbus frame processing, Dwarf bus calls, static buffers/semaphores, and all fatal handling in the original adapters.
- Used source-level exact sequence comparisons and representative board links as hardware-aware evidence; physical-hardware behavior is not claimed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Preserved the XLBUDDY unreachable TIM3 initialization compile shape**

- **Found during:** Task 1 XL build
- **Issue:** Extracting the configuration exposed an undeclared prescaler after the existing `BUDDY_UNREACHABLE()` branch.
- **Fix:** Retained the unreachable path and supplied the same zero-initialized value the previous aggregate state implied.
- **Files modified:** `src/device/stm32f4/peripherals.cpp`
- **Verification:** XL/XLBUDDY firmware compiled and linked.
- **Committed in:** `29e402ae3`

**2. [Rule 1 - Bug] Routed both xBuddy filament-sensor branches through extracted pin policy**

- **Found during:** Task 2 standard and forced-iX xBuddy Extension builds
- **Issue:** Two branch-local reads still referenced the removed `FSENSOR_PIN` constant.
- **Fix:** Added a pure pin accessor and updated both read sites.
- **Files modified:** `src/puppy/xbuddy_extension/hal.cpp`, `src/puppy/xbuddy_extension/hal_config.cpp`, `src/puppy/xbuddy_extension/hal_config.hpp`
- **Verification:** COREONE/standard and forced-iX xBuddy Extension firmware both compiled and linked.
- **Committed in:** `66c24e55b`

**Total deviations:** 2 auto-fixed bugs.
**Impact on plan:** Both fixes preserve existing board-specific behavior without expanding architecture or scope.

## Verification

- Exact STM32F4 DMA stream/channel/direction/mode/priority/link comparisons and preprocessed MINI, MK4, and XL IRQ-order comparisons passed.
- Exact ILI9488 and ST7789V startup command, payload-byte, and delay comparisons passed.
- Modbus CRC table comparison passed for all 256 ordered entries.
- Dwarf comparison passed for 17 bus calls with arguments, 24 moved register-access method sequences, and unchanged timeout/fatal call order.
- xBuddy comparison passed for 21 `hal::init()` calls, 69 HAL effects, 14 GPIO target ports, 25 RCC effects, and 16 abort paths.
- MINI/BUDDY, MK4/XBUDDY, XL/XLBUDDY, standalone XL-Dwarf, COREONE xBuddy Extension, and forced-iX xBuddy Extension builds linked successfully.
- `cargo fmt --all`, clippy with warnings denied, all-target/all-feature build, and all-feature tests passed before each task commit.
- `just build`, `just simulator-parity`, and `just phase40-verify` passed their repository contracts; Phase 40 ran 14 policy tests and reported zero Bright Builds findings.
- Explicit integration pytest execution produced no simulator coverage: Mini404 selected an MK4 machine for the XL image and exited during setup (6 skipped, 22 errors).
- `just phase10-verify` was blocked before implementation checks by the absent historical `10-VALIDATION.md` artifact (1 independent test passed, 13 setup errors).

## Known Stubs

None introduced. Existing null callback initialization and TODO/FIXME comments in retained adapters predate this plan and do not block the refactor goal.

## Issues Encountered

- The explicit simulator run and Phase 10 historical-artifact failure are recorded in `deferred-items.md`; neither failure was caused by the refactor.
- No physical hardware was available, so board builds and exact effect-order review are the strongest local evidence.

## User Setup Required

None.

## Next Phase Readiness

- The hardware/auxiliary campaign is complete with all seven temporary exceptions removed.
- Restore/reconstruct the historical Phase 10 validation artifact and provide a matching Mini404 profile/image pair if those external evidence gaps must be closed.

## Self-Check: PASSED

- Verified all eight representative created artifacts exist.
- Verified task commits `29e402ae3` and `66c24e55b` exist.

*Phase: 40-file-length-refactoring*
*Completed: 2026-07-27*
