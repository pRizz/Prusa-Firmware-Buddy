---
phase: 40-file-length-refactoring
plan: 07
subsystem: evidence-tooling
tags: [python, bazel, finality, cutover, authority, file-lengths]
requires:
  - phase: 40-06
    provides: Stable Phase 18-28 evidence façades and phase-local policy modules
provides:
  - Stable Phase 31-38 final-evidence, triage, decision, readiness, cutover, and workflow entrypoints over phase-local modules
  - Preserved finality, provenance, authority revocation, routing, guarded publication, rollback, and independent demotion behavior
  - Focused interface, failure, security, publication, producer, and actual-workflow test suites
  - All twelve Phase 31-38 temporary file-length exceptions retired with 41 temporary paths remaining
affects: [evidence-tooling, cutover-authority, bazel-runfiles, file-length-verification]
tech-stack:
  added: []
  patterns:
    - stable phase entrypoint over phase-local parsing, policy, publication, and test-support modules
    - fail-closed authority and workflow-attempt markers retained in security-owning coordinators
    - pure final authority evaluation isolated from Phase 38 producer coordination
key-files:
  created:
    - tools/bazel/phase31_intake_policy.py
    - tools/bazel/phase32_triage_policy.py
    - tools/bazel/phase33_decision_policy.py
    - tools/bazel/phase34_readiness_policy.py
    - tools/bazel/phase35_cutover_policy.py
    - tools/bazel/phase38_workflow_policy.py
    - tools/bazel/phase38_cutover_workflow_failure_test.py
  modified:
    - .bright-builds-rules-checks.tsv
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - tools/bazel/phase31_final_evidence_intake.py
    - tools/bazel/phase32_blocker_register_triage.py
    - tools/bazel/phase33_maintainer_decision_inputs.py
    - tools/bazel/phase34_final_readiness_demotion_dry_run.py
    - tools/bazel/phase35_cutover_decision_artifact.py
    - tools/bazel/phase38_cutover_workflow.py
key-decisions:
  - "Phase 31-38 public scripts and Bazel labels remain stable façades; phase-prefixed helpers do not form a new cross-phase framework."
  - "Phase 34 readiness and Phase 35 cutover artifacts remain the only public authority bundles, and reference demotion remains an independent predicate."
  - "Phase 38 extracts only pure final-status policy; workflow-attempt markers, guarded execution, and producer sequencing stay in the coordinator."
patterns-established:
  - "Split final-evidence tooling at phase-local contract, policy, publication, security, and fixture boundaries without weakening finality."
  - "Retire ledger rows only after original entrypoints, extracted modules, phase gates, and the Phase 40 policy all pass below 629 lines."
requirements-completed: [D-05, D-06, D-08, D-09, D-11, D-12, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T21:21:00Z
duration: 40m
completed: 2026-07-27
---

# Phase 40 Plan 07: Phase 31-38 Final-Evidence and Cutover Refactoring Summary

Stable Phase 31-38 entrypoints now front phase-local finality, decision, readiness, publication, security, and workflow policy modules while all fail-closed authority contracts and actual-producer outcomes remain exact.

## Performance

- **Duration:** 40 minutes
- **Started:** 2026-07-27T20:41:00Z
- **Completed:** 2026-07-27T21:21:00Z
- **Tasks:** 3
- **Files modified:** 64

## Accomplishments

- Reduced all twelve campaign-owned Phase 31-38 production/test originals and every extracted phase-local module below 629 physical lines.
- Preserved accepted-final receipts, provenance, blocker identities, exact decision correlation, fixed-path guards, rollback, stale-authority replacement, routes, diagnostics, and exits.
- Kept Phase 34 readiness, Phase 35 cutover, and reference-demotion authorization as independent fail-closed decisions.
- Added explicit Phase 38 execution coverage for 28 extracted failure/security cases and retained all 11 actual-producer integration cases.
- Removed all twelve Phase 31-38 temporary ledger rows, leaving 838 permanent and 41 temporary exceptions with zero policy findings.

## Task Commits

1. **Task 1: Refactor Phase 31-32 intake and triage** - `04162f793`
2. **Task 2: Refactor Phase 33-35 decision and authority tools** - `15e97bb7f`
3. **Task 3: Refactor the Phase 38 coordinator** - `28656af18`

## Files Created/Modified

- `tools/bazel/phase31_intake_*.py` - intake policy, receipt publication, wiring, fixture support, and failure coverage behind the stable Phase 31 CLI.
- `tools/bazel/phase32_*adapter.py`, `phase32_triage_*.py`, and Phase 32 test support - producer normalization and blocker-triage boundaries behind the stable Phase 32 CLI.
- `tools/bazel/phase33_decision_*.py` - decision validation, policy, output, and wiring responsibilities behind the Phase 33 entrypoint.
- `tools/bazel/phase34_*.py` - source validation, readiness policy, coverage diagnostics, publication state, bundle installation, wiring, and focused test seams.
- `tools/bazel/phase35_*.py` - contract security, cutover policy, source bundle, authority guard, guarded wiring, and focused authority/failure suites.
- `tools/bazel/phase38_workflow_policy.py` - pure final authority consistency, routing, and outcome evaluation.
- `tools/bazel/phase38_cutover_workflow_failure_test.py` and `phase38_test_support.py` - extracted marker, guard, coordinator, and rollback regressions without copied integration fixtures.
- `tools/bazel/BUILD.bazel` and `tools/bazel/rust_workflow.sh` - complete runtime/test runfiles and execution wiring for every extracted module.
- `.bright-builds-rules-checks.tsv` - removes all twelve completed Phase 31-38 campaign exceptions.

## Decisions Made

- Existing Phase 31-38 scripts remain the public CLI and orchestration façades so direct invocation, output paths, schemas, and Bazel labels do not change.
- Parsing, normalization, pure policy, publication, security, and fixture seams remain phase-prefixed and phase-local.
- Phase 38 delegates only pure outcome/authority evaluation; attempt markers, guard publication, producer ordering, and final authority loading stay in the coordinator.
- A successful cutover verdict cannot authorize reference demotion without its separate valid decision, open gate, and unblocked readiness state.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Closed isolated actual-producer fixture dependencies**

- **Found during:** Tasks 2 and 3
- **Issue:** Temporary repository fixtures copied stable entrypoints without every newly extracted sibling module, causing subprocess imports to fail.
- **Fix:** Added the complete Phase 33-35 and Phase 38 runtime closures to the existing fixture copy lists and Bazel runfiles.
- **Files modified:** `tools/bazel/phase34_decision_reconciliation_integration_test.py`, `tools/bazel/phase38_cutover_workflow_integration_test.py`, `tools/bazel/BUILD.bazel`
- **Verification:** Phase 34 integration passed 9 cases; Phase 38 actual-producer integration passed all 11 cases; all public phase gates passed.
- **Committed in:** `15e97bb7f`, `28656af18`

**2. [Rule 3 - Blocking] Preserved execution coverage for the extracted Phase 38 failure suite**

- **Found during:** Task 3
- **Issue:** Adding the new failure file to Bazel runfiles made it available but did not execute its 28 guard, marker, coordinator, and cleanup regressions.
- **Fix:** Added one explicit invocation to the existing `phase38_verify_tests` shell branch.
- **Files modified:** `tools/bazel/rust_workflow.sh`
- **Verification:** `just phase38-verify` visibly ran and passed the 28-case failure suite before the 11-case actual-producer integration suite.
- **Committed in:** `28656af18`

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both changes were necessary verification/runtime closure for the planned splits; neither changed public behavior or authority ownership.

## Issues Encountered

- The system Python environment did not provide YAPF or pre-commit. Extracted code retained surrounding formatting, Python compilation passed, and repository format/policy gates reported zero findings.
- Bazel refreshed `MODULE.bazel.lock` from format version 26 to 28 during verification. That unrelated generated drift was restored with a targeted patch before every implementation commit and before metadata updates.

## User Setup Required

None - no external service configuration required.

## Known Stubs

- `tools/bazel/phase31_intake_receipts.py:172` retains the established `quick-placeholder` and `default-placeholder` classifications. These are intentional fail-closed evidence categories rejected as final proof, not unwired implementation paths.

## Residual Risks

- The structural refactor does not create simulator, hardware, live-service, signing, maintainer-approval, or release evidence. Missing non-local proof remains blocked through the existing workflow.
- The final verified workflow correctly remained `blocked` on `targeted-blocker-repair`, with production cutover planning and reference demotion unauthorized and a fresh cutover decision required.

## Verification

- Required ordered Rust checks before implementation commits: `cargo fmt --all`; `cargo clippy --all-targets --all-features -- -D warnings`; `cargo build --all-targets --all-features`; `cargo test --all-features` - passed.
- `just phase31-verify` through `just phase35-verify`, plus `just phase38-verify` - all verifier, interface, failure, security, publication, and actual-producer targets passed.
- Phase 38 focused coverage - 18 interface/policy cases, 28 failure/security cases, and 11 actual-producer integration cases passed.
- `just phase40-verify` and `bun scripts/bright-builds-check.ts all` - policy tests passed with 838 permanent, 41 temporary, 879 total exceptions, and zero findings.
- Physical-line scan - all twelve campaign originals and every new phase-local module are below 629 lines.
- Ledger scan - every Phase 31-38 campaign row is absent.
- `python3 -m py_compile` for the Phase 38 coordinator, policy, support, and test files - passed.
- `git diff --check` - passed.

## Self-Check: PASSED

- Summary and representative Phase 31-38 policy/test artifacts exist.
- Task commits `04162f793`, `15e97bb7f`, and `28656af18` exist in repository history.
- All twelve planned temporary exception rows are absent, and `git diff --check` passes.
