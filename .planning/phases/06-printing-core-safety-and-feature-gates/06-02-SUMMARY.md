---
phase: 06-printing-core-safety-and-feature-gates
plan: 02
subsystem: printing-core
tags: [rust, domain, printing, gcode, manifests, phase6]

# Dependency graph
requires:
  - phase: 06-01
    provides: Phase 6 verifier facade and printing manifest validation foundation
provides:
  - Typed Rust print job state, source, command, planner-flow, fixture-id, and G-code route policies
  - CORE-03 manifest rows bound to exact Rust policy surfaces and retained Marlin/Buddy oracle paths
  - Verifier regression coverage for no-delta printing rows using null intentional_delta values
affects: [CORE-03, printing-core, phase6-verifier, buddy-domain]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Pure Rust domain policy models with fallible newtypes and explicit transition errors
    - Manifest rows that tie Rust policy claims to retained C/C++ source oracle paths

key-files:
  created:
    - rust/crates/domain/src/print.rs
    - .planning/phases/06-printing-core-safety-and-feature-gates/06-02-SUMMARY.md
  modified:
    - rust/crates/domain/src/lib.rs
    - tools/bazel/manifests/phase6_printing_core.json
    - tools/bazel/phase6_verify.py
    - tools/bazel/phase6_verify_test.py

key-decisions:
  - "Modeled file and serial printing as distinct PrintSource variants so policy code cannot collapse their retained behavior families."
  - "Kept transition and G-code routing logic pure Rust domain policy, with retained Marlin/Buddy sources remaining the behavior oracle."
  - "Allowed null intentional_delta only for that manifest field so planned no-delta rows remain valid without weakening other required-field checks."

patterns-established:
  - "Print policy surfaces expose explicit state transitions and errors instead of rewriting retained planner or media algorithms."
  - "Phase 6 printing manifest rust_surface values point to exact Rust file/type/function surfaces."

requirements-completed: [CORE-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 6-2026-06-04T09-48-48
generated_at: 2026-06-04T10:47:15Z

# Metrics
duration: 9m 24s
completed: 2026-06-04
---

# Phase 06 Plan 02: Print Policy Surfaces Summary

**Typed Rust print state, fixture identity, planner-flow, and G-code routing policies tied to retained Marlin/Buddy source contracts**

## Performance

- **Duration:** 9m 24s
- **Started:** 2026-06-04T10:37:51Z
- **Completed:** 2026-06-04T10:47:15Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added `rust/crates/domain/src/print.rs` with tested print source, state, command, transition, planner-flow, fixture-id, and G-code route policies.
- Exported the new print policy types from `buddy-domain` while preserving `#![forbid(unsafe_code)]`.
- Updated CORE-03 printing manifest rows to reference exact Rust surfaces while preserving retained Marlin/Buddy source paths as behavior oracles.
- Preserved the 06-01 verifier foundation and added coverage for the plan-required `intentional_delta: null` manifest shape.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add print state and command routing model (RED)** - `9969d8587` (test)
2. **Task 1: Add print state and command routing model (GREEN)** - `d4ab7a54c` (feat)
3. **Task 2: Bind print policies to reference fixture rows** - `df04e4f77` (fix)

_Note: Task 1 followed TDD, so it has separate failing-test and implementation commits._

## Files Created/Modified

- `rust/crates/domain/src/print.rs` - Defines print source/state/command policy types, fallible fixture and G-code mnemonic newtypes, explicit transition errors, pure transition logic, and routing classification.
- `rust/crates/domain/src/lib.rs` - Exports the print module and public print policy symbols from `buddy-domain`.
- `tools/bazel/manifests/phase6_printing_core.json` - Binds CORE-03 printing rows to exact Rust surfaces and keeps retained reference source paths.
- `tools/bazel/phase6_verify.py` - Treats `intentional_delta: null` as valid for required-field validation while keeping other required fields strict.
- `tools/bazel/phase6_verify_test.py` - Adds printing-manifest verifier coverage for null intentional deltas and complete retained source-path requirements.
- `.planning/phases/06-printing-core-safety-and-feature-gates/06-02-SUMMARY.md` - Captures execution results for this plan.

## Decisions Made

- File and serial printing remain separate `PrintSource` variants because the retained C/C++ paths enter and recover differently.
- Rust print policy models classify allowed transitions and routes only; they do not claim planner, media prefetch, or motion equivalence.
- Manifest no-delta rows use `intentional_delta: null`, with verifier support narrowed to that one field.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Allowed planned null intentional deltas in the Phase 6 verifier**
- **Found during:** Task 2 (Bind print policies to reference fixture rows)
- **Issue:** `python3 tools/bazel/phase6_verify.py --printing-only` rejected the plan-required `intentional_delta: null` rows as empty required fields.
- **Fix:** Added field-aware required-value validation so only `intentional_delta` may be null, then added a regression test for printing-only manifests using null no-delta rows.
- **Files modified:** `tools/bazel/phase6_verify.py`, `tools/bazel/phase6_verify_test.py`
- **Verification:** `python3 -m py_compile tools/bazel/phase6_verify.py tools/bazel/phase6_verify_test.py`, `python3 tools/bazel/phase6_verify_test.py`, `python3 tools/bazel/phase6_verify.py --printing-only`, and `python3 tools/bazel/phase6_verify.py --quick`
- **Committed in:** `df04e4f77`

***

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix was required to satisfy the plan's manifest schema and keeps validation strict for all other required fields.

## Issues Encountered

- The verifier compatibility issue above was resolved in Task 2.
- `.planning/config.json` remained modified from external workflow state and was intentionally not staged or committed per the execution instruction.

## Verification Evidence

- `cargo test --all-features -p buddy-domain print` - passed after RED failure was committed and after final verification.
- `python3 tools/bazel/phase6_verify.py --printing-only` - passed.
- `python3 tools/bazel/phase6_verify.py --quick` - passed.
- `python3 tools/bazel/phase6_verify_test.py` - passed, 4 tests.
- `python3 -m py_compile tools/bazel/phase6_verify.py tools/bazel/phase6_verify_test.py` - passed.
- `cargo fmt --all` - passed.
- `cargo clippy --all-targets --all-features -- -D warnings` - passed.
- `cargo build --all-targets --all-features` - passed.
- `cargo test --all-features` - passed.
- `rg "pub mod print|PrintJobState|PrintSource|PrintCommand|PlannerFlowState|route_gcode_mnemonic|transition_print_state" rust/crates/domain/src/lib.rs rust/crates/domain/src/print.rs` - found all required strings.
- `rg "StartSerial|StartFile|PowerPanicAwaitingResume|MediaErrorAwaitingRecovery|BuddyGcodeHandler|MarlinQueue" rust/crates/domain/src/print.rs` - found all required strings.
- `rg "// Arrange|// Act|// Assert" rust/crates/domain/src/print.rs` - found all required test-section markers.
- `rg "route_gcode_mnemonic|PrintSource::Serial|PrintSource::File|PlannerFlowState|CommandRoute::BuddyGcodeHandler" tools/bazel/manifests/phase6_printing_core.json` - found all required Rust surface bindings.
- `rg "src/common/marlin_server.cpp|src/common/serial_printing.cpp|src/marlin_stubs/gcode.cpp|lib/AddMarlin.cmake" tools/bazel/manifests/phase6_printing_core.json` - found all required retained oracle paths.

## Known Stubs

None. Stub scan found no placeholder text, unwired UI data, or goal-blocking hardcoded empty values in the created or modified plan files.

## Threat Flags

None. This plan added pure Rust domain policy code and manifest/verifier metadata only; it did not add new endpoints, auth paths, file access boundaries, or schema trust boundaries beyond the plan threat model.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

CORE-03 now has tested Rust print policy surfaces and manifest bindings that future Phase 6 plans can reference without weakening the retained Marlin/Buddy oracle model. STATE.md and ROADMAP.md were not updated because the execution request explicitly excluded those updates.

## Self-Check: PASSED

- Verified created/modified files exist: `rust/crates/domain/src/print.rs`, `rust/crates/domain/src/lib.rs`, `tools/bazel/manifests/phase6_printing_core.json`, `tools/bazel/phase6_verify.py`, `tools/bazel/phase6_verify_test.py`, and `.planning/phases/06-printing-core-safety-and-feature-gates/06-02-SUMMARY.md`.
- Verified task commits exist: `9969d8587`, `d4ab7a54c`, and `df04e4f77`.
- Verified only `.planning/config.json` remains outside the plan summary commit scope, and it was intentionally not staged.

***
*Phase: 06-printing-core-safety-and-feature-gates*
*Completed: 2026-06-04*
