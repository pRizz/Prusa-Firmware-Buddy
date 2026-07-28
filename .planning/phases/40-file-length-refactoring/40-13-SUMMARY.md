---
phase: 40-file-length-refactoring
plan: 13
subsystem: print-safety-lifecycle
tags: [startup, print-preview, power-panic, calibration, pause, file-length]
requires:
  - phase: 40-file-length-refactoring
    provides: ordered high-risk file-length campaign through Plan 40-12
provides:
  - five sub-629 startup, preview, recovery, calibration, and pause facades
  - private lifecycle policy and pause motion/state modules behind stable firmware interfaces
  - exact symbol, section-size, and supported-product build evidence for retained behavior
affects: [phase-40-verification, print-lifecycle, firmware-builds, marlin-server]
tech-stack:
  added: []
  patterns: [stable effect facade with private policy module, concept-oriented state-machine split]
key-files:
  created:
    - src/buddy/startup_tasks.cpp
    - src/common/print_preview_policy.cpp
    - src/common/power_panic_state.cpp
    - src/marlin_stubs/g425_policy.cpp
    - src/marlin_stubs/g425_policy.hpp
    - src/marlin_stubs/pause/pause_internal.hpp
    - src/marlin_stubs/pause/pause_motion.cpp
    - src/marlin_stubs/pause/pause_state.cpp
    - src/marlin_stubs/pause/pause_unload_state.cpp
  modified:
    - src/buddy/main.cpp
    - src/common/marlin_print_preview.cpp
    - src/common/power_panic.cpp
    - src/marlin_stubs/G425.cpp
    - src/marlin_stubs/pause/pause.cpp
    - .bright-builds-rules-checks.tsv
key-decisions:
  - "Keep FreeRTOS, Marlin, filesystem, GUI, motion, hardware, and fatal effects in their existing public facades while extracting cohesive policy and state-machine concepts."
  - "Split the 1,646-line pause implementation by load state, unload state, and motion behavior because a single extracted source could not satisfy the strict 629-line limit."
patterns-established:
  - "Lifecycle split: private policy and transition modules own decisions; original files retain public symbols and ordered effects."
  - "High-risk refactors use exact symbol and section-size comparisons plus representative product links; no simulator or hardware claim is made when the environment cannot execute it."
requirements-completed: [D-05, D-07, D-08, D-09, D-11, D-12, D-14, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-28T01:40:05Z
duration: 44min
completed: 2026-07-27
---

# Phase 40 Plan 13: Print and Safety Lifecycle Summary

**Startup, preview, power-panic, calibration, and pause sources reduced below 629 lines while preserving public symbols, effect ordering, product links, and firmware section sizes**

## Performance

- **Duration:** 44 min
- **Started:** 2026-07-28T00:56:06Z
- **Completed:** 2026-07-28T01:40:05Z
- **Tasks:** 2
- **Files modified:** 19

## Accomplishments

- Reduced all five planned oversized originals and every new implementation source below the strict 629-line threshold, then removed exactly five temporary ledger rows.
- Preserved startup task ownership, preview decisions, power-panic recovery, G425 calibration flow, and pause load/unload/motion behavior behind stable interfaces.
- Left one temporary owned exception, `src/common/marlin_server.cpp`, for the final ordered campaign while the Bright Builds aggregate remains green with zero findings.

## Task Commits

Each task was committed atomically:

1. **Task 1: Refactor startup, preview, and power-panic lifecycle** - `bfa84e70a`
2. **Task 2: Refactor G425 and pause state machines** - `78617026b`

## Files Created/Modified

- `src/buddy/startup_tasks.cpp` - Startup task construction and dependency sequencing behind the existing application entrypoint.
- `src/common/print_preview_policy.cpp` - Preview-state policy separated from filesystem, GUI, and Marlin effects.
- `src/common/power_panic_state.cpp` - Power-loss state transitions separated from hardware and recovery effects.
- `src/marlin_stubs/g425_policy.*` - Private calibration policy used by the unchanged public G425 command facade.
- `src/marlin_stubs/pause/pause_internal.hpp` - Private pause contracts shared only inside the pause implementation.
- `src/marlin_stubs/pause/pause_state.cpp` - Load-side pause transitions.
- `src/marlin_stubs/pause/pause_unload_state.cpp` - Unload-side pause transitions.
- `src/marlin_stubs/pause/pause_motion.cpp` - Pause motion and park behavior.
- Original facades and their `CMakeLists.txt` files - Retained public symbols, feature guards, ordered effects, and linked the private modules.
- `.bright-builds-rules-checks.tsv` - Removed five qualified temporary rows.

## Decisions Made

- Kept FreeRTOS task creation, Marlin queues, motion, GUI prompts, filesystem access, hardware calls, and fatal behavior in their established effect-bearing surfaces.
- Used concept-oriented pause modules instead of numbered chunks so load, unload, and motion knowledge remains local and each implementation source stays below threshold.

## Deviations from Plan

### Auto-added Critical Functionality

**1. [Rule 2 - Missing Critical Functionality] Added concept-oriented pause modules beyond the single planned extraction**

- **Found during:** Task 2
- **Issue:** The 1,646-line pause implementation could not be divided into only the original facade and one new source while keeping both below 629 lines.
- **Fix:** Added private shared contracts plus dedicated load-state, unload-state, and motion modules, preserving the original public pause interface and effect ordering.
- **Files modified:** `src/marlin_stubs/pause/pause_internal.hpp`, `src/marlin_stubs/pause/pause_state.cpp`, `src/marlin_stubs/pause/pause_unload_state.cpp`, `src/marlin_stubs/pause/pause_motion.cpp`, `src/marlin_stubs/pause/pause.cpp`, `src/marlin_stubs/pause/CMakeLists.txt`
- **Verification:** All sources are below threshold; COREONE, XL, and iX bootloader/no-bootloader products compiled and linked; pause symbol inventory and XL section sizes matched the baseline exactly.
- **Committed in:** `78617026b`

**Total deviations:** 1 auto-added correctness requirement.
**Impact on plan:** The additional private modules are the minimum cohesive split needed to satisfy the mandated limit without weakening the pause abstraction.

## Verification

- `bun scripts/bright-builds-check.ts all` passed with `findings=0` and 842 exceptions: 841 permanent, one temporary, and three approved owned permanent exceptions.
- `just phase40-verify` passed all 14 tests and the ledger policy check after each atomic row removal.
- `just test` and `just generated-check` passed.
- COREONE and XL release bootloader/no-bootloader builds compiled, linked, and packaged after Task 1.
- COREONE, XL, and iX release bootloader/no-bootloader builds compiled, linked, and packaged after Task 2, covering MMU, nozzle-cleaner, no-human-interaction, auto-retract, and wastebin branches.
- XL section sizes matched the pre-refactor baseline exactly: bootloader `text=1908236`, `data=136`, `bss=186252`; no-bootloader `text=1906284`, `data=136`, `bss=186212`.
- Pause public symbol inventory matched the baseline exactly for all 62 symbols.
- The required Rust sequence passed before each implementation commit: format, Clippy with warnings denied, all-target/all-feature build, and all-feature tests.
- `just phase6-verify` reached and passed its 11-test behavior suite, then its aggregate wrapper failed because three historical Phase 6 documents are archived under `.planning/milestones/v1.0-phases/` while the Bazel runfiles declaration still expects them in the active phase directory. This is a pre-existing verification-wiring gap outside Plan 40-13.
- Simulator integration was attempted with the XL firmware. Pytest collected 28 tests, skipped six, and reported 22 setup errors because the integration harness selected an MK4 machine profile for the XL image and Mini404 exited. Simulator parity is therefore not claimed.
- Physical-hardware verification was not available. Exact source/symbol/section comparisons and the supported-product build matrix provide the hardware-aware review evidence used for this structural-only refactor.
- The bundled `clang-format` executable could not start because its local Homebrew runtime lacks `libzstd.1.dylib`; all modified C++ sources compiled cleanly under the representative product matrix.

## Known Stubs

No stubs were introduced. Existing TODO/FIXME comments in the moved code were retained unchanged as part of behavior-preserving extraction.

## Threat Surface

No new network endpoint, authentication path, file-access boundary, schema, or externally visible protocol surface was introduced.

## Next Phase Readiness

- Plan 40-14 can refactor `src/common/marlin_server.cpp`, the sole remaining temporary exception.
- The Bright Builds aggregate is green, and the permanent exception inventory remains the approved 838 provenance/declarative paths plus three owned deletion-test exceptions.

## Self-Check: PASSED

- All nine created implementation files and this summary exist.
- Task commits `bfa84e70a` and `78617026b` exist in repository history.
- All five original facades and all nine extracted implementation/header files are below 629 lines.
