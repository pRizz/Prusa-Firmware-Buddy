---
phase: 05-foreign-code-unsafe-and-runtime-boundary
plan: 02
subsystem: board-runtime-boundary
tags: [phase5, rust, board-adapter, mmio, dma, interrupts, ffi]

requires:
  - phase: 05-01
    provides: Phase 5 retained-code inventory, unsafe-boundary audit, and quick verifier
provides:
  - Board-side MCU family and retained runtime-surface contracts
  - Board clock-tree source-evidence contracts for STM32F4, STM32G0, and STM32H503 xBuddy Extension
  - Checked memory-region and DMA-visible buffer contracts
  - Audited MMIO register facade with volatile access isolated to `mmio.rs`
  - Interrupt priority and named FFI symbol contracts
affects: [05-03, 05-04, 05-05, runtime-adapter, phase6-runtime-consumers]

tech-stack:
  added: []
  patterns: [typed board boundary contracts, audit-linked unsafe locality, host-tested adapter facades]

key-files:
  created:
    - rust/crates/board-adapter/src/mcu.rs
    - rust/crates/board-adapter/src/clock.rs
    - rust/crates/board-adapter/src/memory_region.rs
    - rust/crates/board-adapter/src/dma.rs
    - rust/crates/board-adapter/src/mmio.rs
    - rust/crates/board-adapter/src/interrupt.rs
    - rust/crates/board-adapter/src/ffi.rs
    - .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-02-SUMMARY.md
  modified:
    - rust/crates/board-adapter/Cargo.toml
    - rust/crates/board-adapter/src/lib.rs

key-decisions:
  - "Keep board adapter clock, MCU, memory-region, and DMA contracts safe while relaxing unsafe linting only when MMIO volatile access is added."
  - "Represent STM32H503 xBuddy Extension as a distinct `McuFamily::Stm32H503XbuddyExtension`, not a generic STM32H5 device path."
  - "Treat host tests as contract validation only; physical clock, interrupt, DMA, and MMIO behavior remains non-local evidence."

patterns-established:
  - "Board adapter modules parse validated `ProductProfile` or checked memory-region values before exposing retained-runtime facts."
  - "Unsafe MMIO operations are fenced in one audited module with `mmio-register-contracts` safety comments and manifest source-path coverage."

requirements-completed: [RUST-04, CORE-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 5-2026-06-03T12-58-01
generated_at: 2026-06-03T14:24:07Z

duration: 6m 59s
completed: 2026-06-03
---

# Phase 5 Plan 2: Board Adapter Boundary Contracts Summary

**Typed Rust board contracts for MCU family, board clocks, memory, DMA, MMIO, interrupts, and retained FFI symbols**

## Performance

- **Duration:** 6m 59s
- **Started:** 2026-06-03T14:17:08Z
- **Completed:** 2026-06-03T14:24:07Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Added host-tested board runtime contracts for STM32F4, STM32G0, and STM32H503 xBuddy Extension surfaces.
- Added board clock-tree contracts that name retained source evidence without claiming hardware proof from host tests.
- Added memory-region and DMA contracts that reject zero-length ranges, checked-add overflow, and non-DMA-accessible memory such as CCMRAM.
- Added typed MMIO, interrupt, and FFI symbol facades, with volatile MMIO access isolated to `mmio.rs`.

## Task Commits

Each task was committed atomically after passing verification:

1. **Task 1: Add MCU, memory-region, and DMA contracts** - `3c1c80404` (feat)
2. **Task 2: Add MMIO, interrupt, and FFI symbol facades** - `9267308c8` (feat)

**Plan metadata:** committed by the final docs commit after this summary self-check.

## Files Created/Modified

- `rust/crates/board-adapter/Cargo.toml` - Allows unsafe only in the board adapter crate and denies unsafe operations inside unsafe functions.
- `rust/crates/board-adapter/src/lib.rs` - Exports the new board boundary modules and contract types.
- `rust/crates/board-adapter/src/mcu.rs` - Models MCU family and retained runtime-surface IDs.
- `rust/crates/board-adapter/src/clock.rs` - Models board clock-tree source evidence and non-local hardware proof notes.
- `rust/crates/board-adapter/src/memory_region.rs` - Adds checked memory-region ranges and region kinds.
- `rust/crates/board-adapter/src/dma.rs` - Adds DMA-visible buffer contracts.
- `rust/crates/board-adapter/src/mmio.rs` - Adds aligned register address checks and volatile `Register32` access.
- `rust/crates/board-adapter/src/interrupt.rs` - Adds interrupt priority and retained IRQ owner contracts.
- `rust/crates/board-adapter/src/ffi.rs` - Adds named retained-code FFI symbol contracts and unsafe locality tests.

## Decisions Made

- Preserved `#![forbid(unsafe_code)]` in pure crates by not editing `buddy-domain` or `buddy-application`.
- Kept H503/xBuddy Extension source evidence tied to `src/puppy/xbuddy_extension` rather than inventing `src/device/stm32h5`.
- Kept FFI symbol contracts as names and component IDs only; no generated C/C++ binding surface was added.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Re-exported `MemoryRegionError` for MMIO error contracts**
- **Found during:** Task 2 (Add MMIO, interrupt, and FFI symbol facades)
- **Issue:** `mmio.rs` exposed `MemoryRegionError` through `RegisterAddressError`, but the type was not available through the crate root import used by the module.
- **Fix:** Re-exported `MemoryRegionError` from `lib.rs`.
- **Files modified:** `rust/crates/board-adapter/src/lib.rs`
- **Verification:** `cargo test --all-features -p buddy-board-adapter` passed after the fix.
- **Committed in:** `9267308c8`

### Process Adjustments

**1. TDD RED states were run but not committed**
- **Reason:** Repo-local Rust pre-commit rules require `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` to pass before any commit. Deliberately failing RED states cannot satisfy that rule.
- **Evidence:** Task 1 RED failed on missing contract types; Task 2 RED failed on missing MMIO/interrupt/FFI types. Both failures were corrected before task commits.

**Total deviations:** 1 auto-fixed blocker, 1 instruction-hierarchy process adjustment.
**Impact on plan:** Contract scope remained unchanged; verification passed after the blocker fix.

## Issues Encountered

- Task 1 RED failed as expected on unresolved `BoardRuntimeSurface`, `BoardClockTree`, `MemoryRegion`, and `DmaBufferRegion` contracts.
- Task 2 RED failed as expected on unresolved `RegisterAddress`, `InterruptPriority`, and `ForeignSymbol` contracts.
- Task 2 initially failed compilation because of the `MemoryRegionError` root import described above; fixed in the Task 2 commit.

## Known Stubs

None. Stub-pattern scan found no placeholder, TODO/FIXME, empty UI-data, or unwired mock-data markers in the files created or modified by this plan.

## Threat Flags

None. The new MMIO, DMA, interrupt, and FFI surfaces match the plan threat model and existing Phase 5 unsafe-boundary audit rows.

## User Setup Required

None - no external service configuration required.

## Verification

- `cargo test --all-features -p buddy-board-adapter` passed with 13 unit tests.
- `rg "BoardClockTree|board-clock-tree-contracts|hal_clock.cpp" rust/crates/board-adapter/src tools/bazel/manifests/unsafe_boundary_audit.json` passed.
- `cargo clippy --all-targets --all-features -- -D warnings` passed.
- `python3 tools/bazel/phase5_verify.py --quick` passed and printed `Phase 5 runtime boundary verification passed`.
- Rust pre-commit sequence passed before each task commit: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`.

## Next Phase Readiness

Phase 05 Plan 03 can consume these board contracts when modeling startup, linker, allocator, panic, watchdog, and crash-dump boundaries. Physical MMIO, interrupt, DMA, and clock behavior still require simulator or hardware evidence before firmware parity can be claimed.

---
*Phase: 05-foreign-code-unsafe-and-runtime-boundary*
*Completed: 2026-06-03*

## Self-Check: PASSED

- Verified `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-02-SUMMARY.md` exists.
- Verified task commits `3c1c80404` and `9267308c8` exist.
