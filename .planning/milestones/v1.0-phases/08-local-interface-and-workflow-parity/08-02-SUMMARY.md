---
phase: 08-local-interface-and-workflow-parity
plan: 02
subsystem: rust-domain
tags: [rust, buddy-domain, gui, parity, invariants]

requires:
  - phase: 07-persistence-storage-and-resource-compatibility
    provides: "Resource, storage, localization, and evidence-class domain patterns consumed by Phase 8 GUI contracts"
provides:
  - "Pure Rust Phase 8 GUI/display/evidence contracts in buddy-domain"
  - "Fallible parsers for display classes, GUI evidence, proof scopes, workflows, row IDs, intentional-delta status, and semantic actions"
  - "Validated GuiParityContract construction that rejects impossible local proof and semantic-action workflow bindings"
affects: [phase8-verifier, gui-manifests, local-interface-parity, IFCE-01]

tech-stack:
  added: []
  patterns:
    - "Pure Rust domain newtypes/enums with fallible boundary parsing"
    - "GuiParityContractInput groups parity row facts before invariant enforcement"
    - "Non-local simulator/hardware/manual evidence cannot be recorded as local proof"

key-files:
  created:
    - rust/crates/domain/src/gui.rs
  modified:
    - rust/crates/domain/src/lib.rs

key-decisions:
  - "Represented Phase 8 GUI parity facts as buddy-domain newtypes and enums instead of verifier-only primitive strings."
  - "Rejected Local proof scope for simulator-flow, hardware-smoke, and manual-hardware-required evidence classes."
  - "Bound pause/resume/cancel/stop/reprint to PrintControl and preview to PrintPreview before adapter code can consume semantic actions."
  - "Used GuiParityContractInput to keep contract construction explicit and clippy-clean."

patterns-established:
  - "DisplayClass parses 240x320, 480x320, and mock while keeping mock out of physical display proof."
  - "GuiParityRowId rejects empty, path-like, control-character, and over-96-byte row identities."
  - "GuiSemanticAction exposes exact manifest IDs plus expected_workflow() for workflow binding checks."

requirements-completed: [IFCE-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 8-2026-06-13T16-58-45
generated_at: 2026-06-13T18:11:05Z

duration: 8 min
completed: 2026-06-13
---

# Phase 08 Plan 02: GUI Domain Contracts Summary

**Typed Rust GUI parity contracts with display/evidence/proof and semantic-action invariants for Phase 8 local interface workflows**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-13T18:02:42Z
- **Completed:** 2026-06-13T18:11:05Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `rust/crates/domain/src/gui.rs` with typed display classes, GUI workflows, surfaces, evidence classes, proof scopes, row IDs, localization surfaces, intentional-delta status, semantic actions, and `GuiParityContract`.
- Extended `rust/crates/domain/src/lib.rs` with `pub mod gui;`, public GUI exports, and Phase 8 invariant error variants with display messages.
- Added focused Arrange/Act/Assert Rust unit tests for display parsing, row ID validation, evidence/proof compatibility, semantic action parsing, and workflow binding rejection.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add failing GUI domain tests** - `1396e54ef` (test)
2. **Task 2: Implement GUI domain contracts and exports** - `d059a0448` (feat)

## Files Created/Modified

- `rust/crates/domain/src/gui.rs` - Pure Phase 8 GUI/display/evidence domain contracts and tests.
- `rust/crates/domain/src/lib.rs` - GUI module export, public type exports, and new invariant errors.

## Decisions Made

- Used exact lower-kebab manifest strings for GUI parser methods to match Phase 8 manifest conventions.
- Kept mock display parsing available as `DisplayClass::MockTestOnly`, but `is_physical_display_proof()` returns false for mock.
- Added `GuiParityContractInput` instead of a wide constructor so future call sites name every contract fact while satisfying clippy.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Replaced wide contract constructor with input struct**
- **Found during:** Task 2 (Implement GUI domain contracts and exports)
- **Issue:** `cargo clippy --all-targets --all-features -- -D warnings` rejected the initial `GuiParityContract::new` signature for having too many arguments.
- **Fix:** Added `GuiParityContractInput` with named fields and changed `GuiParityContract::new` to accept that single input value.
- **Files modified:** `rust/crates/domain/src/gui.rs`, `rust/crates/domain/src/lib.rs`
- **Verification:** `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` passed.
- **Committed in:** `d059a0448`

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix keeps the same domain behavior and improves call-site clarity without expanding scope.

## Issues Encountered

- Clippy rejected the first constructor shape; resolved by introducing `GuiParityContractInput`.

## Known Stubs

None - stub and placeholder scan of touched Rust files found no TODO, FIXME, placeholder, coming soon, not available, or hardcoded empty UI data patterns.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 08-03 can consume the exported `buddy-domain` GUI types in the Phase 8 verifier and manifest wiring. Hardware display, simulator-flow, and manual proof remain explicitly non-local unless later plans run that evidence.

## Self-Check: PASSED

- Found summary file: `.planning/phases/08-local-interface-and-workflow-parity/08-02-SUMMARY.md`
- Found task commit: `1396e54ef`
- Found task commit: `d059a0448`
- Confirmed `.planning/STATE.md`, `.planning/ROADMAP.md`, and `.planning/REQUIREMENTS.md` have no 08-02 changes.

---
*Phase: 08-local-interface-and-workflow-parity*
*Completed: 2026-06-13*
