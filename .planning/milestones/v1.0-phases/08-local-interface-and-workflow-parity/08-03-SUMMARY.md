---
phase: 08-local-interface-and-workflow-parity
plan: 03
subsystem: verification
tags: [phase8, gui, bazel, just, rust, verifier]

requires:
  - phase: 08-local-interface-and-workflow-parity
    provides: Phase 8 GUI workflow, layout, concern, and Rust domain contracts from Plans 01 and 02
provides:
  - Phase 8 static verifier and verifier regression suite
  - Bazel labels and root aliases for Phase 8 verification
  - `just phase8-verify` developer facade
  - Completed Phase 8 Nyquist validation sign-off for local evidence
affects: [phase9-network-and-service-parity, phase10-auxiliary-runtime-parity, phase11-cutover-validation]

tech-stack:
  added: []
  patterns:
    - Python stdlib phase verifier with unittest regression coverage
    - Bazel shell_binary verifier facade through rust_workflow.sh
    - Validation artifact with local versus non-local evidence boundaries

key-files:
  created:
    - tools/bazel/phase8_verify.py
    - tools/bazel/phase8_verify_test.py
  modified:
    - BUILD.bazel
    - justfile
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - .planning/phases/08-local-interface-and-workflow-parity/08-VALIDATION.md

key-decisions:
  - Require canonical `requirement_id` and `reference_sources` schema fields in Phase 8 manifests.
  - Keep simulator, hardware, touch, timing, and long-run GUI proof classified as non-local evidence.
  - Route `just phase8-verify` through Bazel verifier tests before the aggregate verifier.

patterns-established:
  - Phase verifiers should test their own negative cases before aggregate validation runs.
  - Phase validation files should mark automated local evidence green only after commands have run.

requirements-completed: [IFCE-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 8-2026-06-13T16-58-45
generated_at: 2026-06-13T18:33:46Z

duration: 16m 24s
completed: 2026-06-13
---

# Phase 8 Plan 03: Verifier and Facade Summary

**Phase 8 GUI parity contracts now have a static verifier, negative regression tests, Bazel labels, a just facade, and completed local validation evidence.**

## Performance

- **Duration:** 16m 24s
- **Started:** 2026-06-13T18:17:22Z
- **Completed:** 2026-06-13T18:33:46Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Added a RED-first `Phase8VerifierTest` suite covering schema, semantic action, display-class, concern, secret-marker, Rust API, overclaim, and wiring failures.
- Implemented `tools/bazel/phase8_verify.py` with quick and full modes for manifests, Rust API shape, validation text, Bazel/just surface, secret markers, and local-proof wording.
- Wired Phase 8 verification through `//tools/bazel:phase8_verify`, `//tools/bazel:phase8_verify_tests`, root aliases, and `just phase8-verify`.
- Updated `08-VALIDATION.md` to mark local Wave 0 evidence complete while preserving non-local simulator and hardware evidence classes.

## Task Commits

1. **Task 1: Add RED verifier tests** - `00e1a7d59` (`test`)
2. **Task 2: Implement Phase 8 verifier** - `2c49d7141` (`feat`)
3. **Task 3: Wire Bazel, just, and validation sign-off** - `207176ecf` (`feat`)

## Files Created/Modified

- `tools/bazel/phase8_verify_test.py` - Regression suite for required Phase 8 verifier failure modes.
- `tools/bazel/phase8_verify.py` - Static verifier for Phase 8 manifest, Rust API, validation, facade, secret-marker, and wording contracts.
- `tools/bazel/BUILD.bazel` - Adds Phase 8 verifier and verifier-test shell binaries.
- `tools/bazel/rust_workflow.sh` - Dispatches Phase 8 verifier labels.
- `BUILD.bazel` - Adds Phase 8 docs filegroup and root aliases.
- `justfile` - Adds `phase8-verify`.
- `.planning/phases/08-local-interface-and-workflow-parity/08-VALIDATION.md` - Marks local Wave 0 validation green after verification.

## Decisions Made

- Used Python stdlib and the existing Phase 7 verifier pattern rather than adding a schema dependency.
- Required semantic action IDs for print-control workflows so icon/action coverage stays explicit.
- Preserved simulator, hardware, touch, and long-run UI checks as non-local evidence rather than implying local static proof.

## Deviations from Plan

None - plan executed as written.

## Issues Encountered

- Task 2 `--quick` verification was not expected to pass until Task 3 because the verifier intentionally checks Bazel, just, and validation wiring. The missing wiring was completed in Task 3 and the same quick verifier then passed.
- The verifier regression suite exposed that CL-008 and crash-dump concern text needed to be enforced inside `regression_guard.required_strings`, not merely somewhere in the concern row. The implementation was tightened before Task 2 was committed.

## Verification Evidence

- `rg 'class Phase8VerifierTest|test_requires_gui_semantic_action_ids|test_rejects_semantic_action_on_wrong_workflow|test_rejects_legacy_manifest_schema_fields|test_rejects_display_layout_without_both_display_classes|test_requires_cl008_and_crash_dump_concerns|test_rejects_secret_or_crash_dump_byte_markers|test_requires_gui_rust_api_surface|test_rejects_phase8_overclaims|test_requires_bazel_and_just_wiring' tools/bazel/phase8_verify_test.py` - passed.
- `python3 tools/bazel/phase8_verify_test.py` before Task 2 - failed RED as expected because `phase8_verify.py` did not exist.
- `python3 -m py_compile tools/bazel/phase8_verify.py tools/bazel/phase8_verify_test.py` - passed.
- `python3 tools/bazel/phase8_verify_test.py` - passed, 9 tests.
- `python3 tools/bazel/phase8_verify.py --quick` - passed.
- `bazel query "//tools/bazel:phase8_verify + //tools/bazel:phase8_verify_tests + //:phase8_verify + //:phase8_verify_tests + //:phase8_local_interface_docs"` - passed and listed all five labels.
- `bazel run //tools/bazel:phase8_verify_tests` - passed, 9 tests.
- `bazel run //tools/bazel:phase8_verify` - passed.
- `just phase8-verify` - passed; it ran verifier tests before aggregate verification.
- `cargo fmt --all -- --check` - passed.
- `cargo clippy --all-targets --all-features -- -D warnings` - passed.
- `cargo build --all-targets --all-features` - passed.
- `cargo test --all-features` - passed, including 107 Rust unit tests plus doc-tests.

## Known Stubs

None. Stub scan across the created and modified plan files returned no `TODO`, `FIXME`, placeholder text, or empty UI data-source patterns.

## Threat Flags

None. The new executable surface is verifier-only Bazel/just wiring covered by the plan threat model.

## User Setup Required

None - no external service configuration required.

## Residual Risks

- Physical LCD, touch/encoder timing, simulator display flows, long-run GUI behavior, network service behavior, auxiliary runtime behavior, and final cutover evidence remain non-local by design and are tracked in `08-VALIDATION.md`.
- `.planning/config.json` had a pre-existing uncommitted change before this plan began and was intentionally left untouched.

## Self-Check: PASSED

- Files found: `tools/bazel/phase8_verify.py`, `tools/bazel/phase8_verify_test.py`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `BUILD.bazel`, `justfile`, `.planning/phases/08-local-interface-and-workflow-parity/08-VALIDATION.md`.
- Commits found: `00e1a7d59`, `2c49d7141`, `207176ecf`.
- Scope check: only the pre-existing `.planning/config.json` change remains outside this plan.

---
*Phase: 08-local-interface-and-workflow-parity*
*Completed: 2026-06-13*
