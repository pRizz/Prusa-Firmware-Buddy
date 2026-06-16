---
phase: 05-foreign-code-unsafe-and-runtime-boundary
plan: 03
subsystem: runtime-boundary-contracts
tags: [phase5, rust, runtime-adapter, startup, linker, allocator, panic, watchdog, crash-dump]

requires:
  - phase: 05-01
    provides: Phase 5 retained-code inventory, unsafe-boundary audit, and quick verifier
  - phase: 05-02
    provides: board-side MCU, clock, MMIO, DMA, interrupt, and FFI boundary contracts
provides:
  - Runtime startup/vector contracts for STM32F4, STM32G0, and STM32H503 xBuddy Extension
  - Linker section and boot/noboot linker script contracts
  - Allocator and heap-assumption contracts
  - Panic/assert/BSOD/fatal, watchdog, and crash-dump raw-memory contracts
affects: [05-04, 05-05, runtime-adapter, phase6-runtime-consumers]

tech-stack:
  added: []
  patterns: [typed runtime boundary contracts, non-local hardware evidence classes, retained startup/linker evidence]

key-files:
  created:
    - rust/crates/runtime-adapter/src/startup.rs
    - rust/crates/runtime-adapter/src/linker.rs
    - rust/crates/runtime-adapter/src/allocator.rs
    - rust/crates/runtime-adapter/src/panic_boundary.rs
    - .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-03-SUMMARY.md
  modified:
    - rust/crates/runtime-adapter/src/lib.rs

key-decisions:
  - "Keep retained startup assembly, linker scripts, assert, watchdog, and crash-dump code untouched while modeling them as Rust contracts."
  - "Represent STM32H503 xBuddy Extension as a distinct runtime surface with required fpv5-sp-d16 evidence."
  - "Classify startup, watchdog, crash-dump, and hardware placement behavior as simulator-flow, hardware-smoke, or manual-hardware-required instead of local proof."

patterns-established:
  - "Runtime adapter modules expose typed contract data and host tests without introducing runtime side effects."
  - "Boundary methods return retained source paths, audit surface IDs, and evidence classes so later plans cannot collapse hardware evidence into host tests."

requirements-completed: [RUST-04, CORE-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 5-2026-06-03T12-58-01
generated_at: 2026-06-03T20:30:38Z

duration: 7m 38s
completed: 2026-06-03
---

# Phase 5 Plan 3: Runtime Boundary Contracts Summary

**Typed Rust runtime contracts for STM32 startup, linker sections, allocator assumptions, panic/assert behavior, watchdog evidence, and crash-dump raw memory**

## Performance

- **Duration:** 7m 38s
- **Started:** 2026-06-03T20:23:00Z
- **Completed:** 2026-06-03T20:30:38Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added startup/vector contracts for STM32F4, STM32G0, and STM32H503 xBuddy Extension without editing retained startup assembly or CMake selection.
- Added linker script and section contracts that name F4/G0/H503 boot/noboot scripts and runtime-sensitive sections.
- Added allocator contracts that reject zero heap size and distinguish static-only from heap-backed runtime assumptions.
- Added panic/assert/BSOD/fatal, watchdog, and crash-dump raw-memory contracts with non-local hardware evidence classes.

## Task Commits

Each task was committed atomically after passing verification:

1. **Task 1: Add startup and linker contracts** - `63f61d7ac` (feat)
2. **Task 2: Add allocator, panic, watchdog, and crash-dump contracts** - `7157092a7` (feat)

**Plan metadata:** committed by the final docs commit after this summary self-check.

## Files Created/Modified

- `rust/crates/runtime-adapter/src/lib.rs` - Exports runtime startup, linker, allocator, and panic-boundary modules.
- `rust/crates/runtime-adapter/src/startup.rs` - Models startup vector surfaces, H503 `fpv5-sp-d16` evidence, and evidence classes.
- `rust/crates/runtime-adapter/src/linker.rs` - Models boot/noboot linker scripts and runtime-sensitive sections.
- `rust/crates/runtime-adapter/src/allocator.rs` - Models static-only and heap-backed allocator assumptions.
- `rust/crates/runtime-adapter/src/panic_boundary.rs` - Models panic/assert/BSOD/fatal, watchdog, and crash-dump boundaries.

## Decisions Made

- Kept `buddy-runtime-adapter` unsafe-free; no allocator, panic, or startup behavior was implemented, only boundary contracts.
- Kept H503/xBuddy Extension tied to `src/puppy/xbuddy_extension` and did not introduce a generic H5 runtime path.
- Used `EvidenceClass` values to separate local manifest/static/Rust-host proof from simulator, hardware smoke, and manual hardware evidence.

## Deviations from Plan

### Auto-fixed Issues

None.

### Process Adjustments

**1. TDD RED states were run but not committed**
- **Reason:** Repo-local Rust pre-commit rules require `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` to pass before every commit. Deliberately failing RED commits cannot satisfy that rule.
- **Evidence:** Task 1 RED failed on missing startup/linker contract exports. Task 2 RED failed on missing allocator/panic-boundary exports. Both were corrected before task commits.

**Total deviations:** 0 auto-fixed, 1 instruction-hierarchy process adjustment.
**Impact on plan:** Contract scope remained unchanged and all acceptance criteria passed.

## Issues Encountered

- Task 1 RED failed as expected on unresolved `StartupSurface`, `StartupVectorTable`, `BootModeLinkerScript`, `LinkerSection`, and `EvidenceClass`.
- Task 2 RED failed as expected on unresolved `AllocatorBoundary`, `PanicBoundary`, `WatchdogBoundary`, and `CrashDumpBoundary`.
- No unresolved implementation issues remain.

## Known Stubs

None. Stub-pattern scan found no placeholder, TODO/FIXME, empty UI-data, or unwired mock-data markers in the files created or modified by this plan.

## Threat Flags

None. Startup/linker, allocator, panic/assert, watchdog, and crash-dump surfaces were all planned in the Plan 03 threat model and Phase 5 unsafe-boundary audit.

## User Setup Required

None - no external service configuration required.

## Verification

- `cargo test --all-features -p buddy-runtime-adapter` passed with 14 unit tests.
- `cargo clippy --all-targets --all-features -- -D warnings` passed.
- `python3 tools/bazel/phase5_verify.py --quick` passed and printed `Phase 5 runtime boundary verification passed`.
- Task acceptance `rg` checks passed for `StartupSurface`, `BootModeLinkerScript`, `stm32h503_boot.ld`, `stm32h503_noboot.ld`, `fpv5-sp-d16`, `ManualHardwareRequired`, `AllocatorBoundary`, `PanicBoundary`, `WatchdogBoundary`, `CrashDumpBoundary`, `panic-bsod-assert-boundary`, `watchdog-boundary`, and `crash-dump-memory-boundary`.
- Rust pre-commit sequence passed before each task commit: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`.

## Next Phase Readiness

Phase 05 Plan 04 can build FreeRTOS task, queue, timer, static-memory, and synchronization contracts on top of these runtime evidence classes. Hardware startup, watchdog reset effects, crash-dump retention, and linker placement still require simulator or hardware evidence before firmware parity is claimed.

---
*Phase: 05-foreign-code-unsafe-and-runtime-boundary*
*Completed: 2026-06-03*

## Self-Check: PASSED

- Verified `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-03-SUMMARY.md` exists.
- Verified created runtime files `startup.rs`, `linker.rs`, `allocator.rs`, and `panic_boundary.rs` exist.
- Verified task commits `63f61d7ac` and `7157092a7` exist.
