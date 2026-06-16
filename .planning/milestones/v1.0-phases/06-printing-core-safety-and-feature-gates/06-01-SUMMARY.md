---
phase: 06-printing-core-safety-and-feature-gates
plan: 01
subsystem: verification
tags: [bazel, just, python, manifests, printing, safety, feature-gates]

requires:
  - phase: 05-foreign-code-unsafe-and-runtime-boundary
    provides: Retained-code inventory, unsafe/runtime boundary audit, and Rust workflow pattern.
provides:
  - Phase 6 verifier for manifest schema, lifecycle, source-path, evidence-class, facade, and overclaim checks.
  - CORE-03 printing contract manifest rows.
  - CORE-04 safety gate manifest rows.
  - CORE-05 feature gate manifest rows.
  - Phase 6 concern disposition manifest rows.
  - Bazel and just entrypoints for Phase 6 verification.
affects: [phase-06, CORE-03, CORE-04, CORE-05, phase6_verify]

tech-stack:
  added: none
  patterns: [stdlib-python-verifier, manifest-backed-evidence-contracts, bazel-shell-binary-facade]

key-files:
  created:
    - tools/bazel/phase6_verify.py
    - tools/bazel/phase6_verify_test.py
    - tools/bazel/manifests/phase6_printing_core.json
    - tools/bazel/manifests/phase6_safety_gates.json
    - tools/bazel/manifests/phase6_feature_gates.json
    - tools/bazel/manifests/phase6_concern_dispositions.json
    - .planning/phases/06-printing-core-safety-and-feature-gates/06-01-SUMMARY.md
  modified:
    - BUILD.bazel
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - justfile

key-decisions:
  - "Use a standard-library Python verifier with explicit schema/source/evidence checks and no new dependencies."
  - "Classify simulator and physical-printer evidence as non-local manifest facts until later validation phases provide that proof."
  - "Route direct Python, Bazel, and just entrypoints to the same Phase 6 verification contract."

patterns-established:
  - "Phase manifests must carry schema_version, phase, phase_lifecycle_id, requirement IDs, existing source_paths, allowed evidence_class values, and required row IDs."
  - "Known concerns get explicit Phase 6 dispositions before Rust policies can depend on them."
  - "Workflow labels use root aliases plus tools/bazel shell_binary targets backed by rust_workflow.sh dispatch."

requirements-completed: [CORE-03, CORE-04, CORE-05]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 6-2026-06-04T09-48-48
generated_at: 2026-06-04T10:35:14Z

duration: 8min
completed: 2026-06-04
---

# Phase 06 Plan 01: Wave 0 Verification Foundation Summary

**Stdlib Phase 6 verifier with manifest-backed printing, safety, feature-gate, and concern evidence wired through Bazel and just**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-04T10:27:18Z
- **Completed:** 2026-06-04T10:35:14Z
- **Tasks:** 3 completed
- **Files modified:** 11

## Accomplishments

- Created `tools/bazel/phase6_verify.py` with CLI modes for quick, all, manifest-only, printing, safety, features, and concerns validation.
- Added four Phase 6 manifests covering required CORE-03, CORE-04, CORE-05, and concern disposition rows with lifecycle and source-path checks.
- Exposed Phase 6 verification through direct Python, `//tools/bazel:phase6_verify`, root `//:phase6_verify`, and `just phase6-verify`.

## Task Commits

Each task was committed atomically. Task 1 used the planned TDD split:

1. **Task 1 RED: Phase 6 verifier tests** - `89951bfdc` (test)
2. **Task 1 GREEN: Phase 6 verifier schema gates** - `c0c11ac6e` (feat)
3. **Task 2: Phase 6 evidence manifests** - `3d9e6f951` (feat)
4. **Task 3: Bazel and just verification facade** - `1415acabb` (feat)

## Files Created/Modified

- `tools/bazel/phase6_verify.py` - Phase 6 verifier for manifests, source paths, lifecycle ID, evidence classes, facade wiring, overclaim strings, and Cargo checks under `--all`.
- `tools/bazel/phase6_verify_test.py` - TDD harness for help output, missing manifest errors, and evidence-class rejection.
- `tools/bazel/manifests/phase6_printing_core.json` - CORE-03 printing contracts for G-code routing, serial/file printing, planner-visible flow, and Buddy G/M-code handlers.
- `tools/bazel/manifests/phase6_safety_gates.json` - CORE-04 safety contracts for thermal, motion, selftest, power panic, fatal, watchdog, crash dump, probe, and loadcell flows.
- `tools/bazel/manifests/phase6_feature_gates.json` - CORE-05 gate facts for filament sensors, TMC, homing, input shaper, phase/burst stepping, loadcell/HX717, beds, chamber, door, MMU2, NFC, LEDs, toolchanger, and xBuddy Extension.
- `tools/bazel/manifests/phase6_concern_dispositions.json` - Phase 6 handling for CL-007, CL-008, CL-011, CL-014, CL-024, CL-002, and TMC driver retention.
- `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - Phase 6 verification facade wiring.

## Decisions Made

- Kept the verifier dependency-free and modeled after the Phase 5 verifier to match existing repo workflow.
- Made manifest rows the executable evidence contract for later Rust policy plans, rather than relying on prose-only references.
- Kept MMU, toolchanger, xBuddy Extension, screen workflow, networking, storage, and cutover proof outside Phase 6 implementation claims.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. `.planning/config.json` remained dirty from the auto-chain flag and was intentionally not staged.

## Verification Evidence

- `python3 -m py_compile tools/bazel/phase6_verify.py` passed.
- `python3 tools/bazel/phase6_verify.py --manifests-only` passed.
- `python3 tools/bazel/phase6_verify.py --quick` passed.
- `bazel query "//tools/bazel:phase6_verify + //:phase6_verify"` passed and printed both labels.
- `just --list` passed and listed `phase6-verify`.
- `python3 tools/bazel/phase6_verify_test.py` passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Wave 0 is ready for later Phase 6 plans to add Rust print, safety, and feature-gate policy code against executable manifest contracts.

## Self-Check: PASSED

- Confirmed all created and modified files exist on disk.
- Confirmed task commits `89951bfdc`, `c0c11ac6e`, `3d9e6f951`, and `1415acabb` are reachable in git history.
- Re-ran `python3 tools/bazel/phase6_verify.py --quick` after writing this summary; it passed.
- Stub scan found no placeholder, TODO, FIXME, or hardcoded empty-data patterns in the plan-created/modified files.

---
*Phase: 06-printing-core-safety-and-feature-gates*
*Completed: 2026-06-04*
