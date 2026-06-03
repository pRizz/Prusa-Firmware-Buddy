---
phase: 05-foreign-code-unsafe-and-runtime-boundary
plan: 05
subsystem: runtime-boundary-verification
tags: [phase5, bazel, justfile, verifier, retained-code, unsafe-boundary]

requires:
  - phase: 05-01
    provides: Phase 5 retained-code inventory, unsafe-boundary audit, and verifier foundation
  - phase: 05-02
    provides: Board adapter contracts for MCU, clock, memory, DMA, MMIO, interrupts, and FFI
  - phase: 05-03
    provides: Runtime startup, linker, allocator, panic, watchdog, and crash-dump contracts
  - phase: 05-04
    provides: FreeRTOS task, queue, timer, static-memory, and synchronization contracts
provides:
  - Bazel labels and root aliases for Phase 5 verification, retained-code inventory, and unsafe audit
  - `just phase5-verify` facade for the aggregate Phase 5 gate
  - Hardened Phase 5 verifier for adapter drift, unsafe locality, Bazel/just surfaces, and evidence wording
affects: [phase6-runtime-consumers, phase11-cutover-evidence, bazel-facade, runtime-adapter, board-adapter]

tech-stack:
  added: []
  patterns: [Bazel-exposed phase verification, standard-library static verifier, non-local evidence wording guard]

key-files:
  created:
    - .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-05-SUMMARY.md
  modified:
    - BUILD.bazel
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - tools/bazel/phase5_verify.py
    - justfile

key-decisions:
  - "Expose Phase 5 retained-code and unsafe-boundary artifacts through Bazel labels and the checked justfile facade."
  - "Keep the aggregate verifier standard-library Python while enforcing exact adapter files, exact audit rows, and unsafe source locality."
  - "Reject local evidence wording that would blur manifest/static checks with simulator or hardware evidence classes."

patterns-established:
  - "Phase-specific Bazel verifier labels should carry the machine-readable manifests, human-readable phase docs, and Rust workspace sources as runfiles."
  - "Verifier `--quick` runs all static checks, while `--all` adds Cargo format, clippy, build, and tests."

requirements-completed: [RUST-03, RUST-04, CORE-01, CORE-02]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 5-2026-06-03T12-58-01
generated_at: 2026-06-03T20:49:54Z

duration: 4m 48s
completed: 2026-06-03
---

# Phase 5 Plan 5: Bazel and Verifier Surface Summary

**Bazel and just expose Phase 5 retained-code, unsafe-boundary, adapter-contract, and aggregate verification gates**

## Performance

- **Duration:** 4m 48s
- **Started:** 2026-06-03T20:45:06Z
- **Completed:** 2026-06-03T20:49:54Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added `//tools/bazel:phase5_verify`, `//tools/bazel:unsafe_boundary_audit`, root aliases, and `//:phase5_runtime_boundary_docs`.
- Updated `//tools/bazel:retained_foreign_code` runfiles to include the Phase 5 inventory and runtime-boundary docs.
- Added `just phase5-verify`, which runs `bazel run //tools/bazel:phase5_verify`.
- Hardened `tools/bazel/phase5_verify.py` so `--quick` checks adapter module presence, exact audit rows, pure-crate unsafe posture, unsafe locality, Bazel labels, just recipe discovery, and evidence wording.

## Task Commits

Each task was committed atomically after passing verification:

1. **Task 1: Wire Phase 5 Bazel labels and just recipe** - `6324b29c4` (feat)
2. **Task 2: Harden verifier for adapters, labels, and evidence claims** - `efa1c66e6` (fix)

**Plan metadata:** committed by the final docs commit after this summary self-check.

## Files Created/Modified

- `BUILD.bazel` - Adds Phase 5 runtime-boundary docs and root aliases.
- `tools/bazel/BUILD.bazel` - Adds the Phase 5 verifier target, unsafe audit filegroup, and retained-code runfiles.
- `tools/bazel/rust_workflow.sh` - Dispatches `phase5_verify` to `python3 tools/bazel/phase5_verify.py --all`.
- `tools/bazel/phase5_verify.py` - Adds aggregate static checks for adapters, Bazel/just surfaces, unsafe locality, and evidence wording.
- `justfile` - Adds the `phase5-verify` developer facade.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-05-SUMMARY.md` - Execution summary and self-check record.

## Decisions Made

- Kept Phase 5 verification as one standard-library Python script rather than introducing schema or test dependencies.
- Treated the Task 1 Bazel/just wiring as the developer entrypoint and the Task 2 direct Python verifier as the static enforcement source.
- Limited hardware wording rejection to Phase 5 verification artifacts and summaries, so planning/research documents can still describe forbidden phrases as examples.

## Deviations from Plan

### Process Adjustments

**1. TDD RED state used the planned acceptance check instead of a committed failing test**
- **Reason:** The task write scope allowed only `tools/bazel/phase5_verify.py`, and repo-local pre-commit rules require passing format, clippy, build, and tests before each commit. A deliberately failing test commit would violate those higher-priority rules.
- **Evidence:** Before editing, `rg "check_adapter_surface|check_bazel_surface|check_just_surface|check_no_hardware_overclaim" tools/bazel/phase5_verify.py` failed. After editing, the same check passed and `python3 tools/bazel/phase5_verify.py --quick` passed.

**Total deviations:** 0 auto-fixed, 1 instruction-hierarchy process adjustment.
**Impact on plan:** No scope change; the verifier hardening and all acceptance criteria were completed.

## Issues Encountered

None. Bazel downloaded Bazel 9.1.1 during the first query and all subsequent Bazel/just commands ran successfully.

## Known Stubs

None. Stub-pattern scan found only local accumulator initializations inside the Python verifier, not placeholder data, TODO/FIXME markers, or unwired mock surfaces.

## Threat Flags

None. The changed trust boundaries were planned in the 05-05 threat model: Bazel/just facade to verifier, verifier to Rust adapter crates, and local verification to non-local evidence classification.

## User Setup Required

None - no external service configuration required.

## Verification

- `bazel query "//tools/bazel:phase5_verify + //tools/bazel:retained_foreign_code + //tools/bazel:unsafe_boundary_audit"` passed and returned all three labels.
- `just --list` passed and listed `phase5-verify`.
- `python3 -m py_compile tools/bazel/phase5_verify.py` passed.
- `python3 tools/bazel/phase5_verify.py --quick` passed and printed `Phase 5 runtime boundary verification passed`.
- `python3 tools/bazel/phase5_verify.py --all` passed.
- `just phase5-verify` passed through Bazel.
- `just rust-format`, `just rust-lint`, `just rust-build`, and `just rust-test` passed.
- Repo-required Rust pre-commit sequence passed before each task commit: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`.

## Next Phase Readiness

Phase 5 runtime boundary work is now exposed through Bazel, `just`, and the aggregate verifier. Phase 6 can consume the retained-code inventory, unsafe audit, board adapter contracts, and runtime adapter contracts with a local gate that catches adapter drift and keeps simulator or hardware evidence classified as non-local until real evidence exists.

---
*Phase: 05-foreign-code-unsafe-and-runtime-boundary*
*Completed: 2026-06-03*

## Self-Check: PASSED

- Verified `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-05-SUMMARY.md` exists.
- Verified task commits `6324b29c4` and `efa1c66e6` exist.
- Verified `python3 tools/bazel/phase5_verify.py --quick` still passes with this summary present.
