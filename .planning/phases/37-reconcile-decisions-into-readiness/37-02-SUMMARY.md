---
phase: 37-reconcile-decisions-into-readiness
plan: 02
subsystem: decision-readiness
tags: [python, bazel, canonical-ledger, integration-testing, fail-closed]
requires:
  - phase: 37-reconcile-decisions-into-readiness
    provides: exact typed Phase 33 targets and the pure Phase 34 reconciliation core from Plan 01
  - phase: 31-final-evidence-intake
    provides: accepted-final evidence receipts and required-stream authority
  - phase: 32-blocker-register-and-evidence-triage
    provides: canonical Phase 27/28 decision-domain rows
  - phase: 33-maintainer-decision-inputs
    provides: normalized maintainer decisions and readiness/demotion handoffs
provides:
  - one Phase 34 ledger containing distinct Phase 31 evidence and Phase 32 decision-domain rows
  - retained Phase 34 readiness artifacts that resolve exact typed decisions with stable diagnostics
  - real-producer approved-path and eight-category negative integration coverage
  - authoritative Phase 34 Bazel gate covering boundary, core, ledger, and producer-chain suites
affects: [phase34-readiness-ledger, phase38-cutover-boundary, READY-01]
tech-stack:
  added: []
  patterns: [dual-source typed ledger, producer-chain fixture, fail-closed diagnostic publication]
key-files:
  created:
    - tools/bazel/phase34_decision_reconciliation_integration_test.py
  modified:
    - tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json
    - tools/bazel/phase34_final_readiness_demotion_dry_run.py
    - tools/bazel/phase34_final_readiness_demotion_dry_run_test.py
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
key-decisions:
  - "Keep Phase 31 accepted-final receipts as the sole evidence completeness authority while adding canonical Phase 32 decision-domain rows as a distinct ledger kind."
  - "Derive every retained JSON and Markdown view from one typed ledger, with exact target diagnostics blocking readiness but demotion-only diagnostics remaining independent."
  - "Use the existing just phase34-verify facade to run all four Phase 33/34 suites before Phase 34 publication."
patterns-established:
  - "Phase 34 constructs evidence rows and decision-domain rows explicitly before merging them into the canonical ledger."
  - "Real-producer integration starts with actual Phase 31, 32, and 33 outputs, mutates one normalized decision concern, and asserts the retained Phase 34 diagnostic."
requirements-completed:
  - DECIDE-01
  - DECIDE-02
  - READY-01
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 37-2026-07-26T06-52-46
generated_at: 2026-07-26T08:17:07Z
duration: 22min
completed: 2026-07-26
---

# Phase 37 Plan 02: Decision Readiness Ledger Integration Summary

**Phase 34 now publishes one typed dual-source ledger whose complete real-producer inputs reach unblocked readiness and whose invalid decision bindings remain durably blocked with specific diagnostics.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-07-26T07:55:08Z
- **Completed:** 2026-07-26T08:17:07Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Added first-class Phase 27/28 decision-domain rows to the Phase 34 ledger while preserving canonical row, axis, subject, lifecycle, lineage, classification, gate, requirement, and decision-reference fields.
- Kept Phase 31 receipts as the only evidence completeness/finality authority and derived every retained packet, blocker summary, dry run, and Markdown report from the same canonical ledger.
- Proved an actual Phase 31-through-34 approved chain reaches `readiness_state: unblocked`.
- Covered omission, row-ref mismatch, axis mismatch, subject mismatch, stale lifecycle, invalid value, duplicate binding, and conflicting binding as separate blocked Phase 34 outcomes with stable diagnostics.
- Extended the hermetic Phase 34 gate to run 37 Phase 33 boundary tests, 18 pure reconciliation tests, 40 ledger tests, and 9 producer-chain integration tests before publication.

## Task Commits

Each task was committed atomically:

1. **Task 1: Materialize and reconcile first-class decision-domain ledger rows** - `6c7b506de` (feat)
2. **Task 2: Prove the real Phase 31-through-34 approved and blocked paths** - `6a98af310` (test)
3. **Task 3: Wire the reconciliation regressions into the authoritative Phase 34 gate** - `4d9bbdf3b` (chore)

## Files Created/Modified

- `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json` - Defines the typed evidence/decision-domain ledger union and decision reconciliation policy.
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py` - Constructs both row kinds, consumes the pure reconciliation core, and publishes retained Phase 34 views.
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py` - Covers canonical ledger preservation, exact decision coverage, and demotion diagnostic orthogonality.
- `tools/bazel/phase34_decision_reconciliation_integration_test.py` - Exercises actual Phase 31, 32, 33, and 34 producer paths plus eight one-concern mutations.
- `tools/bazel/BUILD.bazel` - Carries all producer fixtures, contracts, modules, and suites in the Phase 34 runfiles.
- `tools/bazel/rust_workflow.sh` - Runs the boundary, pure-core, ledger, and real-producer suites before Phase 34 publication.

## Decisions Made

- Phase 32 contributes canonical decision-domain identity and classification but never replaces Phase 31 as evidence authority.
- A decision-domain row clears only through one exact `row_ref + decision_axis + decision_subject_id` match with an axis-appropriate approving value.
- Readiness derives from blocked ledger rows; reference-demotion authorization and demotion-only diagnostics remain orthogonal.
- The public verification surface stays `just phase34-verify`; no Phase 37-specific alias or downstream cutover dispatch was added.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Kept demotion-only target diagnostics out of readiness prerequisites**

- **Found during:** Task 2 (real producer and mutation integration)
- **Issue:** The Task 1 diagnostic aggregate treated every unmatched decision diagnostic as a readiness prerequisite, including diagnostics belonging exclusively to the independent demotion axis.
- **Fix:** Classified reconciliation diagnostics by their source decision axis and excluded demotion-only diagnostics from readiness prerequisite blocking while retaining them in the canonical ledger.
- **Files modified:** `tools/bazel/phase34_final_readiness_demotion_dry_run.py`, `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
- **Verification:** The focused orthogonality regression, all 40 ledger tests, all 9 integration tests, `just phase34-verify`, and the mandatory Rust sequence pass.
- **Committed in:** `6a98af310`

**Total deviations:** 1 auto-fixed (1 bug)

**Impact on plan:** The fix was required to satisfy the planned readiness/demotion separation and introduced no additional scope.

## Issues Encountered

- The first producer fixture used an incorrect external phase reference for non-release receipts; Phase 31 rejected it against the contract allowlist. The fixture now derives the correct Phase 23/24/25 roots and passes the actual Phase 31 validator.
- Importing the Phase 32 helper class directly exposed its test class to `unittest` discovery. Importing its module instead keeps the integration suite at the intended nine tests while still reusing the producer helpers.
- Local Bazel upgraded only the lockfile format during verification. That generated-only rewrite was removed because no dependency graph changed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 37 is complete: exact typed decisions now flow through Phase 34 retained readiness artifacts with a proven unblocked path and fail-closed mutation coverage.
- Phase 38 can consume these retained artifacts for its separately scoped cutover work.
- No production reference was demoted and no downstream cutover artifact was invoked or published.

## Known Stubs

None - the created and modified paths contain no goal-blocking placeholders or unwired mock data.

## Self-Check: PASSED

- All six implementation files and this summary exist.
- Task commits `6c7b506de`, `6a98af310`, and `4d9bbdf3b` exist in repository history.
- Summary lifecycle mode, lifecycle ID, generator provenance, and frontmatter boundaries match the originating plan.
