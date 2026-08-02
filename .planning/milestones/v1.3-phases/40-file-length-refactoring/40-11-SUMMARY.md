---
phase: 40-file-length-refactoring
plan: 11
subsystem: persistent-storage
tags: [cpp, cmake, journal, config-store, migrations, file-length-policy]
requires:
  - phase: 40-file-length-refactoring
    provides: Plan 08 recovery characterization and Plan 10 target-wiring precedent
provides:
  - Deterministic journal bank, CRC, and transaction policy separated from storage effects
  - Ordered config migrations and persisted-field adapters behind an unchanged registry definition
  - Two persistent-storage file-length exceptions retired with byte-contract evidence
affects: [file-length-policy, persistent-storage, firmware-build, host-tests]
tech-stack:
  added: []
  patterns: [effectful-shell-state-policy, persistence-compatibility-module, atomic-policy-ledger-removal]
key-files:
  created:
    - src/persistent_stores/journal/backend_state.cpp
    - src/persistent_stores/store_instances/config_store/store_migrations.cpp
  modified:
    - .bright-builds-rules-checks.tsv
    - src/persistent_stores/journal/backend.cpp
    - src/persistent_stores/journal/CMakeLists.txt
    - src/persistent_stores/store_instances/config_store/store_definition.cpp
    - src/persistent_stores/store_instances/config_store/CMakeLists.txt
    - tests/unit/persistent_stores/CMakeLists.txt
key-decisions:
  - "Keep EEPROM access, recovery mutation, synchronization, initialization, and public journal lifetime behavior in backend.cpp while moving deterministic bank, CRC, and transaction policy."
  - "Treat ordered config migrations and legacy indexed persisted-field adapters as one compatibility seam while leaving the declarative registry and public header byte-for-byte unchanged."
patterns-established:
  - "Persistent effects remain in stable source façades while deterministic policy is linked through private translation units on the same target."
  - "Persistence exception rows are removed only after host recovery tests, unchanged generated hashes, and a real ARM firmware link."
requirements-completed: [D-05, D-07, D-08, D-09, D-11, D-12, D-14, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T23:50:37Z
duration: 17m
completed: 2026-07-27
---

# Phase 40 Plan 11: Persistent Storage Refactoring Summary

**Journal state policy and config migration compatibility now live in private sub-threshold sources while stored hashes, registry layout, defaults, recovery behavior, and public definitions remain unchanged.**

## Performance

- **Duration:** 17m
- **Started:** 2026-07-27T23:33:58Z
- **Completed:** 2026-07-27T23:50:37Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Moved deterministic journal bank selection, CRC calculation, capacity decisions, and transaction state into `backend_state.cpp`.
- Retained journal storage reads/writes, recovery effects, locking, initialization, metrics, and public lifetime symbols in `backend.cpp`.
- Moved ordered config migrations together with legacy indexed persisted-field adapters into `store_migrations.cpp`.
- Preserved the declarative config registry, public header, defaults, migration order, generated item hashes, and target ownership.
- Removed both qualified persistent-storage file-length exception rows.

## Task Commits

Each task was committed atomically:

1. **Task 1: Separate journal state policy from storage effects** - `a24c18434`
2. **Task 2: Extract config-store migration implementation** - `4d83bb341`

## Files Created/Modified

- `src/persistent_stores/journal/backend_state.cpp` - Deterministic bank, CRC, capacity, and transaction policy.
- `src/persistent_stores/journal/backend.cpp` - Stable effectful journal implementation, reduced to 602 lines.
- `src/persistent_stores/store_instances/config_store/store_migrations.cpp` - Ordered migrations and persisted-field compatibility adapters.
- `src/persistent_stores/store_instances/config_store/store_definition.cpp` - Registry-owned runtime implementation, reduced to 474 lines.
- Journal and config-store CMake files - New private sources wired into the existing firmware target.
- `tests/unit/persistent_stores/CMakeLists.txt` - Focused journal target wired to the extracted state source and its direct UTF-8 dependency.
- `.bright-builds-rules-checks.tsv` - Both temporary persistent-storage rows removed.

## Decisions Made

- Journal effects remain centralized in `backend.cpp`; extracted code is deterministic policy over existing state and types.
- Config migration ordering and bodies moved unchanged. Indexed footer, filament-sensor, tool, filament, and nozzle adapters moved with them because they form the persisted-representation compatibility seam.
- `store_definition.hpp` remains the sole declarative registry authority and was not modified.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Closed the focused journal target's direct UTF-8 dependency**

- **Found during:** Task 1
- **Issue:** Rebuilding the focused EEPROM target exposed an unresolved `StringReaderUtf8::getUtf8Char` symbol.
- **Fix:** Added `src/lang/string_view_utf8.cpp` directly to `eeprom_unit_tests`.
- **Files modified:** `tests/unit/persistent_stores/CMakeLists.txt`
- **Verification:** The focused target linked and passed 11 cases / 10,407 assertions.
- **Committed in:** `a24c18434`

**Total deviations:** 1 blocking direct-target dependency fix.

**Impact on plan:** The fix only closes the focused host target's source dependency; production storage behavior and architecture are unchanged.

## Verification Evidence

- Physical line caps:
  - `backend.cpp` 602; `backend_state.cpp` 83
  - `store_definition.cpp` 474; `store_migrations.cpp` 524
- Reconstructing the pre-split config implementation from the two post-split sources produced a zero diff before formatting.
- Persisted-definition SHA-256 remained `44a02a53366d452065ab33fadd7d2778a9d4fed380517f0eda86aa49d5647f72`.
- Defaults SHA-256 remained `bf8a80406193baab7e42d70c80f1a620d79768180acfca5fcd9da5c0277905c5`.
- Host, MK4, and COREONE generated journal-hash headers all remained `27c837ee83df711e27457f8d9af95872cc49241a05334a80a5b0e547f110e1db`.
- Focused journal storage and recovery suite passed 11 cases / 10,407 assertions.
- `just generated-check` passed.
- A real MK4 release/no-boot ARM firmware image linked and packaged with both extracted sources.
- Mandatory Rust sequence passed before both task commits: format, clippy with warnings denied, all-target build, and all-feature tests.
- Bright Builds all-check passed with zero findings.
- `just phase40-verify` passed 14 policy tests with `permanent=841`, `temporary=13`, `owned_permanent=3`, and `total=854`.
- `git diff --check` passed; temporary macOS linker workarounds and `MODULE.bazel.lock` drift were restored.

## Known Stubs

None. The extracted production sources contain no placeholder data flow or newly introduced TODO/FIXME implementation gaps.

## Issues Encountered

- The full host reference command stops at an unrelated Apple linker incompatibility because the global host graph passes GNU `--gc-sections` to Apple `ld`. A temporary uncommitted `if(NOT APPLE)` guard allowed the scoped EEPROM target to rebuild and pass; the root CMake file was restored.
- The bundled repository `clang-format` cannot start on this host because its `libzstd.1.dylib` dependency is absent. Homebrew LLVM clang-format was used for the two C++ files.
- The actual simulator command collected 28 tests but produced 22 fixture errors and 6 skips because Mini404 exits before loading firmware. Direct launch exits 134 because dyld cannot load `/usr/local/opt/dtc/lib/libfdt.1.dylib`; simulator parity coverage is not claimed.
- Catch2's successful `--list-tests` invocation returns 11, the discovered case count, so the plan's strict `set -e` form was adapted to accept that documented result before executing the suite.

## User Setup Required

None for the firmware changes. Simulator parity requires a compatible `libfdt` runtime or a native Mini404 build before the existing integration suite can start.

## Next Phase Readiness

- The persistent-storage campaign is complete with both temporary rows retired.
- Thirteen temporary file-length exceptions remain for subsequent Phase 40 plans.
- Storage/recovery host tests, generated artifacts, ARM firmware linkage, Rust checks, and policy gates are green; only the documented simulator-host dependency prevents executed simulator coverage.

## Self-Check: PASSED

Both created sources, this summary, and task commits `a24c18434` and `4d83bb341` exist.

*Phase: 40-file-length-refactoring*
*Completed: 2026-07-27*
