---
phase: 10-auxiliary-controllers-and-expansion-ecosystem
plan: 02
subsystem: domain
tags: [rust, buddy-domain, auxiliary-controllers, mmu, modbus, invariants]

# Dependency graph
requires:
  - phase: 06-printing-core-safety-and-feature-gates
    provides: ProductProfile and Phase 6 feature-gate handoff for auxiliary behavior
  - phase: 07-persistence-storage-and-resource-compatibility
    provides: Resource runtime path conventions for MMU and puppy firmware assets
provides:
  - Pure Rust Phase 10 auxiliary-controller domain contracts
  - Typed auxiliary/MMU/Modbus/dock/update/fault parity values
  - Product-profile-gated auxiliary controller contract validation
affects: [phase10-verifier, phase10-manifests, phase11-cutover]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Fallible Rust newtypes and enums for Phase 10 boundary parsing
    - Local proof/evidence compatibility checks before adapter consumption

key-files:
  created:
    - rust/crates/domain/src/auxiliary.rs
    - .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-02-SUMMARY.md
  modified:
    - rust/crates/domain/src/lib.rs

key-decisions:
  - "Represent Phase 10 auxiliary facts as pure buddy-domain types instead of verifier-only primitive strings."
  - "Keep firmware image sources named-only with no payload or byte accessors."
  - "Reject local proof scope for simulator, hardware-smoke, and manual evidence classes."
  - "Gate auxiliary controller contracts through validated ProductProfile/controller pairs."

patterns-established:
  - "Auxiliary row IDs are path-free printable ASCII values capped at 96 bytes."
  - "Auxiliary controller availability is accepted only for valid profile/controller combinations."
  - "MMU transport and auxiliary runtime ambiguity is modeled with explicit update, fault, bootloader, and deferred states."

requirements-completed: [IFCE-06]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 10-2026-06-14T15-08-30
generated_at: 2026-06-14T16:20:30Z

# Metrics
duration: 8 min
completed: 2026-06-14
---

# Phase 10 Plan 02: Auxiliary Domain Contracts Summary

**Pure Rust auxiliary-controller contracts for IFCE-06, including typed MMU, Modbus, dock, firmware-source, update, fault, proof, and product/controller invariants.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-14T16:12:48Z
- **Completed:** 2026-06-14T16:20:30Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `buddy-domain` auxiliary contracts for controller kinds, runtime states, firmware image sources, update modes, Modbus identities/request kinds, bus evidence, proof scope, MMU transport, dock identities, tool offsets, fault classes, parity row IDs, parity contracts, and controller contracts.
- Added unit tests covering row ID validation, evidence/proof compatibility, named-only firmware image sources, runtime/MMU states, Modbus bounds, dock and tool-offset identities, controller faults, update/request parsing, and product/controller compatibility.
- Extended `InvariantError` and public crate exports so future Phase 10 manifests and verifiers can consume typed auxiliary values instead of unchecked strings.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add failing auxiliary domain tests** - `67517e467` (test)
2. **Task 2: Implement auxiliary domain contracts and exports** - `26dd9b044` (feat)

## Files Created/Modified

- `rust/crates/domain/src/auxiliary.rs` - Pure Phase 10 auxiliary-controller domain contracts and unit tests.
- `rust/crates/domain/src/lib.rs` - Public auxiliary exports and invariant error variants/messages.

## Decisions Made

- Kept all Phase 10 auxiliary logic in `buddy-domain` with no adapter, filesystem, firmware update, Modbus execution, simulator, hardware, or payload behavior.
- Modeled firmware sources as named enum values only, covering the CMake variables and runtime paths required by IFCE-06.
- Treated non-local evidence classes as invalid for `AuxiliaryProofScope::Local`, matching the Phase 10 overclaim boundary.
- Used validated `ProductProfile` facts to reject unsupported controller/product combinations before runtime adapter code can consume them.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The worktree had a pre-existing `.planning/config.json` diff, which was left unstaged and uncommitted per the wave executor instruction.

## User Setup Required

None - no external service configuration required.

## Verification

- `cargo test -p buddy-domain --all-features auxiliary` - passed
- `cargo fmt --all -- --check` - passed
- `cargo clippy --all-targets --all-features -- -D warnings` - passed
- `cargo build --all-targets --all-features` - passed
- `cargo test --all-features` - passed
- Acceptance `rg` checks for all planned auxiliary API/error/export surfaces - passed
- `rg "unsafe" rust/crates/domain/src/auxiliary.rs` - no matches

## Known Stubs

None.

## Next Phase Readiness

Plan 10-03 can verify the new Rust auxiliary API surface and connect these typed contracts to Phase 10 manifests and aggregate verifier checks. Non-local hardware, simulator, RS485, dock/toolchanger, MMU, and long-run update proof remains honestly deferred to later verification gates.

## Self-Check: PASSED

- Found summary file at `.planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-02-SUMMARY.md`.
- Found task commit `67517e467`.
- Found task commit `26dd9b044`.
- Confirmed `phase_lifecycle_id: 10-2026-06-14T15-08-30`.
- Confirmed `requirements-completed: [IFCE-06]`.

---
*Phase: 10-auxiliary-controllers-and-expansion-ecosystem*
*Completed: 2026-06-14*
