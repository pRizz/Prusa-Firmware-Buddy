---
phase: 40-file-length-refactoring
plan: 10
subsystem: firmware-architecture
tags: [cpp, cmake, filesystem, media-prefetch, connect, transfers, file-length-policy]
requires:
  - phase: 40-file-length-refactoring
    provides: Plan 09 host inventories and locked conversion precedent
provides:
  - Five repo-owned filesystem, media, Connect, Marlin, and transfer implementations split below 629 lines
  - Stable effectful adapters backed by focused directory, prefetch-policy, command, state, and recovery-policy modules
  - Final approved owned deep-module classification for the byte-identical Connect planner
affects: [file-length-policy, firmware-build, host-tests, network-media-campaign]
tech-stack:
  added: []
  patterns: [stable-facade-private-module, effectful-shell-policy-extraction, atomic-policy-ledger-removal]
key-files:
  created:
    - src/buddy/filesystem_fatfs_dir.cpp
    - src/common/media_prefetch/media_prefetch_policy.cpp
    - src/connect/connect_commands.cpp
    - src/connect/marlin_printer_state.cpp
  modified:
    - .bright-builds-rules-checks.tsv
    - src/buddy/filesystem_fatfs.cpp
    - src/common/media_prefetch/media_prefetch.cpp
    - src/connect/connect.cpp
    - src/connect/marlin_printer.cpp
    - src/transfers/transfer.cpp
    - src/transfers/transfer_recovery.cpp
key-decisions:
  - "Keep FatFS registration, prefetch I/O, Connect transport, Marlin effects, and transfer orchestration in their stable adapters while extracting cohesive policy."
  - "Place transfer download-order decisions in the already-owned recovery translation unit so firmware and host recovery behavior share one policy boundary."
  - "Retain planner.cpp byte-for-byte as the single Connect scheduling, retry, event, command, and transfer-lifecycle state authority."
patterns-established:
  - "Effectful firmware entry points remain stable while target-local source files own directory operations and decision policy."
  - "A locked deep-module conversion records a path-specific deletion test and proves source bytes are unchanged."
requirements-completed: [D-03, D-05, D-07, D-08, D-09, D-11, D-12, D-14, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T23:29:14Z
duration: 24m
completed: 2026-07-27
---

# Phase 40 Plan 10: Filesystem, Media, and Connect Refactoring Summary

**Five oversized network/media implementations now delegate to cohesive sub-threshold modules, and the byte-identical Connect planner is the third and final approved owned deep module.**

## Performance

- **Duration:** 24m
- **Started:** 2026-07-27T23:04:50Z
- **Completed:** 2026-07-27T23:29:14Z
- **Tasks:** 3
- **Files modified:** 18

## Accomplishments

- Split FatFS directory operations and media-prefetch readiness/capacity policy while preserving devoptab, media-record, and asynchronous I/O contracts.
- Split Connect response/WebSocket command handling and Marlin state/action adaptation while preserving public symbols, compile guards, protocol statuses, and hardware effects.
- Moved transfer download-order decisions into the recovery policy source without changing filenames, retries, partial-file semantics, or recovery effects.
- Removed five temporary network/media rows and converted only `src/connect/planner.cpp` to the final authorized owned deep-module reason.
- Linked and packaged real COREONE boot/noboot and MK4 noboot firmware images.

## Task Commits

Each task was committed atomically:

1. **Task 1: Refactor filesystem and media prefetch** - `ad2c7aa4a`
2. **Task 2: Refactor Connect, Marlin adapter, and transfers** - `dd3bc2897`
3. **Task 3: Convert the locked planner exception** - `6277d1113`

## Files Created/Modified

- `src/buddy/filesystem_fatfs_dir.cpp` - FatFS directory, metadata, rename, unlink, and volume-stat operations.
- `src/common/media_prefetch/media_prefetch_policy.cpp` - Prefetch readiness, metrics, and ring-capacity decisions.
- `src/connect/connect_commands.cpp` - HTTP command response parsing and WebSocket command dispatch.
- `src/connect/marlin_printer_state.cpp` - Print control, readiness, reset, dialog, and completed-job state adaptation.
- `src/transfers/transfer_recovery.cpp` - Recovery serialization plus plain-G-code and generic download ordering.
- `.bright-builds-rules-checks.tsv` - Five temporary rows removed and the locked planner conversion recorded.
- CMake and focused host-test sources - New translation units and direct test interfaces wired to their owning targets.

## Decisions Made

- FatFS registration and prefetch worker I/O remain effectful shells; extracted modules own cohesive directory and policy behavior.
- Connect transport lifetime remains in `connect.cpp`; response parsing and WebSocket command dispatch move together because they share command-buffer ownership and protocol status handling.
- The Marlin adapter retains device/configuration integration while state and action methods form a separate cohesive adapter source.
- `planner.cpp` remains the single stateful authority because deleting any scheduling, retry, event, command, or transfer-lifecycle region would break ordering invariants across the whole Connect workflow.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Closed two direct GUI host-target dependencies**

- **Found during:** Task 1
- **Issue:** The Plan 09 source splits exposed a missing UTF-8 implementation in `color_tests` and missing encoder up/down callbacks in the window test target.
- **Fix:** Added `string_view_utf8.cpp` to the color target and supplied the two focused window callback stubs.
- **Files modified:** `tests/unit/gui/CMakeLists.txt`, `tests/unit/gui/window/empty_mocks.cpp`
- **Verification:** The host build advanced past both targets; focused media tests and firmware builds passed.
- **Committed in:** `ad2c7aa4a`

**2. [Rule 3 - Blocking] Completed the focused transfer partial-file test interface**

- **Found during:** Task 2
- **Issue:** Linking download-order policy from `transfer_recovery.cpp` required the focused test double to implement `has_valid_tail` and `get_state`.
- **Fix:** Added behavior-compatible implementations to the existing partial-file mock.
- **Files modified:** `tests/unit/transfers/partial_file_mock.cpp`
- **Verification:** A fresh `transfers_tests` binary linked and passed 10 cases / 514,726 assertions.
- **Committed in:** `dd3bc2897`

**Total deviations:** 2 blocking dependency fixes.

**Impact on plan:** Both fixes are direct translation-unit wiring required by the planned extractions; no production behavior or architectural scope changed.

## Verification Evidence

- Physical line caps:
  - `filesystem_fatfs.cpp` 612; `filesystem_fatfs_dir.cpp` 246
  - `media_prefetch.cpp` 606; `media_prefetch_policy.cpp` 72
  - `connect.cpp` 617; `connect_commands.cpp` 289
  - `marlin_printer.cpp` 547; `marlin_printer_state.cpp` 134
  - `transfer.cpp` 576; `transfer_recovery.cpp` 485
- Fresh focused host binaries passed:
  - Connect: 45 cases / 263 assertions
  - Transfers: 10 cases / 514,726 assertions
- Unchanged Plan 09 inventories re-executed:
  - Planner: 21 cases / 197 assertions
  - Registration: 1 case / 14 assertions
- Real ARM firmware linked and packaged:
  - COREONE release boot and noboot
  - MK4 release noboot for the supported simulator input
- Planner SHA-256 remained `e73cc01eac267cce9dfa1dc8ef1cf88c8ae5f71516fa46bee99e720e8e7bffdc`.
- `just phase40-verify` passed 14 policy tests with `permanent=841`, `temporary=15`, `owned_permanent=3`, `total=856`, and zero findings.
- Bright Builds all-check passed with zero findings.
- Mandatory Rust sequence passed before every task commit: format, clippy with warnings denied, all-target build, and all-feature tests.
- `git diff --check` passed; temporary macOS linker workarounds and `MODULE.bazel.lock` drift were restored.

## Known Stubs

- `tests/unit/transfers/partial_file_mock.cpp:9` - Intentional `has_valid_tail` host-test double required to link and exercise recovery ordering.
- `tests/unit/transfers/partial_file_mock.cpp:13` - Intentional stored-state host-test implementation required by download-order policy.
- `tests/unit/gui/window/empty_mocks.cpp` - Intentional no-op encoder callbacks for the focused window host binary.
- Pre-existing TODO/FIXME comments remain in moved production code; this plan introduced no production placeholder data flow.

## Issues Encountered

- A clean `connect_planner_tests` macOS link lacks direct `str_utils` and `string_view_utf8` sources. Per the bounded execution re-plan, no further unrelated host-target closure was added; the unchanged Plan 09 binary still passed 21 cases / 197 assertions.
- The actual simulator command collected 28 tests but produced 22 fixture errors and 6 skips because bundled Mini404 exits before firmware startup. Direct launch proves dyld cannot load `/usr/local/opt/dtc/lib/libfdt.1.dylib` for the x86_64 simulator binary.
- `BUDDY_BAZEL_EXECUTE_REFERENCE=1 just test` remains blocked later by an unrelated `url_decode_tests` direct-dependency closure after progressing past the two scoped Task 1 fixes.

## User Setup Required

None for the firmware changes. Simulator parity requires a native Mini404 build or a compatible local `libfdt` runtime before the existing integration suite can start.

## Next Phase Readiness

- The network/media campaign is complete: five temporary rows are removed and its sole locked conversion is documented.
- Fifteen temporary file-length exceptions remain for the remaining Phase 40 campaigns.
- Production builds, focused changed-code host tests, Rust checks, and policy gates are green; only the documented host/simulator environment limitations remain.

## Self-Check: PASSED

All created files and task commits exist; the planner hash matches its pre-conversion value.

*Phase: 40-file-length-refactoring*
*Completed: 2026-07-27*
