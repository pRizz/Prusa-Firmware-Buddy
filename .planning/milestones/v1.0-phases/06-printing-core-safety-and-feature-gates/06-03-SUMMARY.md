---
phase: 06-printing-core-safety-and-feature-gates
plan: 03
subsystem: safety-policy
tags: [rust, domain, safety, recovery, manifests, phase6]

# Dependency graph
requires:
  - phase: 06-01
    provides: Phase 6 verifier facade, CORE-04 safety manifest schema, and concern disposition rows.
  - phase: 06-02
    provides: Existing buddy-domain Phase 6 print policy export pattern.
provides:
  - Typed pure Rust safety flow, action, evidence class, fatal-path policy, and policy surface data for CORE-04.
  - Focused Rust tests for fatal-boundary, crash-dump, watchdog, emergency-stop, probe/loadcell, and retained source-path classification.
  - CORE-04 safety manifest rows bound to exact Rust safety policy surfaces and retained source references.
affects: [CORE-04, buddy-domain, phase6-safety-gates, fatal-boundary-policy]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Pure Rust safety policy metadata built from static slices with no retained HAL, RTOS, watchdog, crash-dump, or safe-output calls.
    - Manifest rows that bind safety claims to exact Rust policy surfaces while preserving non-local evidence classes.

key-files:
  created:
    - rust/crates/domain/src/safety.rs
    - .planning/phases/06-printing-core-safety-and-feature-gates/06-03-SUMMARY.md
  modified:
    - rust/crates/domain/src/lib.rs
    - tools/bazel/manifests/phase6_safety_gates.json

key-decisions:
  - "Kept safety classification in buddy-domain as pure static policy metadata, leaving HAL, RTOS, watchdog, crash-dump, and safe-output effects behind retained boundaries."
  - "Modeled fatal-path policy with allows_allocation: false and Phase 5 panic, crash-dump, and watchdog audit surface IDs."
  - "Classified crash dump, watchdog, power panic, and emergency-stop physical behavior as non-local evidence instead of local Rust host proof."

patterns-established:
  - "SafetyPolicySurface uses maybe_ optional fields and static source-path slices for no-allocation policy construction."
  - "CORE-04 manifest rust_surface values point to exact Rust enum variants, actions, or FatalPathPolicy instead of broad generic contracts."

requirements-completed: [CORE-04]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 6-2026-06-04T09-48-48
generated_at: 2026-06-04T11:04:39Z

# Metrics
duration: 5m 30s
completed: 2026-06-04
---

# Phase 06 Plan 03: Safety Policy Surface Summary

**Typed Rust safety and recovery policy metadata with CORE-04 manifest bindings to retained fatal, crash-dump, watchdog, emergency-stop, and probe/loadcell evidence**

## Performance

- **Duration:** 5m 30s
- **Started:** 2026-06-04T10:59:10Z
- **Completed:** 2026-06-04T11:04:39Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added `rust/crates/domain/src/safety.rs` with `SafetyFlow`, `SafetyAction`, `EvidenceClass`, `FatalPathPolicy`, `SafetyPolicySurface`, and `classify_safety_flow`.
- Exported the safety policy module and public types from `buddy-domain` while preserving `#![forbid(unsafe_code)]`.
- Covered CORE-04 safety classifications with Rust unit tests using Arrange/Act/Assert structure.
- Updated `phase6_safety_gates.json` so safety rows reference exact Rust surfaces and keep hardware, watchdog, crash-dump, emergency-stop, and power-panic evidence non-local.

## Task Commits

Each task was committed atomically. Task 1 followed TDD, so it has separate RED and GREEN commits:

1. **Task 1 RED: Add failing safety policy tests** - `6f6c9cf35` (test)
2. **Task 1 GREEN: Implement pure safety policy model** - `b31bbe4a4` (feat)
3. **Task 2: Bind safety policies to evidence rows** - `b05f0ea0b` (feat)

## Files Created/Modified

- `rust/crates/domain/src/safety.rs` - Defines pure safety flow/action/evidence policy data, fatal-path constraints, static retained source paths, known concern links, and CORE-04 tests.
- `rust/crates/domain/src/lib.rs` - Exports the safety module and public safety policy symbols from `buddy-domain`.
- `tools/bazel/manifests/phase6_safety_gates.json` - Binds CORE-04 rows to exact Rust policy surfaces and retained source/evidence references.
- `.planning/phases/06-printing-core-safety-and-feature-gates/06-03-SUMMARY.md` - Captures execution results for this plan.

## Decisions Made

- Safety policy construction uses static slices and const classification so the domain layer does not allocate or call retained fatal/HAL/RTOS effects.
- Fatal-boundary policy names `panic-bsod-assert-boundary`, `crash-dump-memory-boundary`, and `watchdog-boundary` and sets `allows_allocation: false`.
- Probe/loadcell classification cites `CL-007` and retained `src/common/probe_analysis.cpp` behavior instead of changing classifier thresholds.
- Crash-dump handling cites `CL-011` and source paths only, without copying crash memory contents or changing dump/export behavior.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The repo-local `standards/` directory was not present, so the pinned Bright Builds canonical standards pages were loaded from the exact commit named by `AGENTS.bright-builds.md`.
- `.planning/config.json` remained modified from workflow state and was intentionally not staged or committed per the execution instruction.

## Verification Evidence

- RED: `cargo test --all-features -p buddy-domain safety` failed on missing safety policy symbols before implementation.
- `cargo test --all-features -p buddy-domain safety` passed after implementation and final verification.
- `python3 tools/bazel/phase6_verify.py --safety-only` passed after manifest updates and final verification.
- `python3 tools/bazel/phase6_verify.py --quick` passed.
- Acceptance `rg` checks for safety exports, fatal audit surface IDs, `allows_allocation: false`, `CL-007`, manifest rust surfaces, retained source paths, `manual-hardware-required`, and Arrange/Act/Assert markers passed.
- Rust pre-commit sequence passed: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`.

## Known Stubs

None. Stub scan found no unresolved marker text or hardcoded empty UI/data patterns in the plan-created or modified files.

## Threat Flags

None. This plan added pure Rust domain policy metadata and manifest rows only; it did not add new network endpoints, auth paths, file access behavior, or schema trust boundaries beyond the plan threat model.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

CORE-04 now has tested Rust safety policy data and manifest evidence bindings. STATE.md and ROADMAP.md were not updated because the execution request explicitly excluded those updates.

## Self-Check: PASSED

- Confirmed created files exist: `rust/crates/domain/src/safety.rs` and `.planning/phases/06-printing-core-safety-and-feature-gates/06-03-SUMMARY.md`.
- Confirmed task commits `6f6c9cf35`, `b31bbe4a4`, and `b05f0ea0b` are reachable in git history.
- Re-ran `python3 tools/bazel/phase6_verify.py --quick` after writing this summary; it passed.
- Stub scan found no unresolved marker text or hardcoded empty UI/data patterns in the plan-created or modified files.
- Verified `.planning/config.json` remains unstaged and was not committed.

---
*Phase: 06-printing-core-safety-and-feature-gates*
*Completed: 2026-06-04*
