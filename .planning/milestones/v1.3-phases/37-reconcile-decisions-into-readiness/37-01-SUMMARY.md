---
phase: 37-reconcile-decisions-into-readiness
plan: 01
subsystem: decision-readiness
tags: [python, bazel, typed-identity, reconciliation, fail-closed]
requires:
  - phase: 32-blocker-register-and-evidence-triage
    provides: canonical blocker row IDs and separate decision-axis/subject identity
  - phase: 33-maintainer-decision-inputs
    provides: explicit maintainer decision records and Phase 34 handoff artifacts
  - phase: 36-normalize-evidence-and-blocker-rows
    provides: immutable source identity and canonical decision-domain rows
provides:
  - typed Phase 33 decision targets bound by row reference, decision axis, and decision subject
  - exact-match Phase 34 reconciliation core with axis-specific approval semantics
  - stable fail-closed diagnostics for ambiguous, stale, invalid, rejected, and hard-blocker decisions
affects: [37-02, phase34-readiness-ledger, phase38-cutover-boundary]
tech-stack:
  added: []
  patterns: [typed boundary normalization, pure exact-key reconciliation, orthogonal demotion authorization]
key-files:
  created:
    - tools/bazel/phase34_decision_reconciliation.py
    - tools/bazel/phase34_decision_reconciliation_test.py
  modified:
    - tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json
    - tools/bazel/phase33_maintainer_decision_inputs.py
    - tools/bazel/phase33_maintainer_decision_inputs_test.py
key-decisions:
  - "Resolve decisions only through the complete row_ref + decision_axis + decision_subject_id identity."
  - "Treat conflicting typed targets as blockers instead of selecting a decision by timestamp."
  - "Map the Phase 33 reference_demotion decision type to the canonical demotion axis while keeping its readiness effect independent."
patterns-established:
  - "Phase 33 owns typed target parsing and publishes source_row_refs only as the exact decision_targets row-ref projection."
  - "Phase 34 decision reconciliation is a filesystem-free data transformation with stable reason codes."
requirements-completed:
  - DECIDE-01
  - DECIDE-02
  - READY-01
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 37-2026-07-26T06-52-46
generated_at: 2026-07-26T07:49:29Z
duration: 12min
completed: 2026-07-26
---

# Phase 37 Plan 01: Typed Decision Reconciliation Summary

**Exact typed Phase 33 targets now resolve canonical Phase 32 rows through a pure, axis-aware Phase 34 core without weakening fail-closed readiness or demotion separation.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-26T07:37:55Z
- **Completed:** 2026-07-26T07:49:29Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Extended the Phase 33 contract and normalizer with explicit `decision_targets` containing canonical row, axis, and subject identity.
- Enforced exact target matching, deterministic `source_row_refs` projection, and specific rejection of malformed, mismatched, duplicate, and conflicting bindings.
- Added a pure Phase 34 reconciliation core covering all five axes, readiness prerequisites, stale inputs, invalid/rejected values, hard blockers, and demotion orthogonality.
- Proved the boundary with 37 Phase 33 tests, 18 reconciliation tests, the full Rust workspace sequence, and `just phase34-verify`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Normalize explicit typed decision targets at the Phase 33 boundary** - `c7ed3413f` (feat)
2. **Task 2: Implement the pure exact-match decision reconciliation core** - `41bbab4fe` (feat)

## Files Created/Modified

- `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` - Declares required typed targets, exact match fields, projection semantics, and forbidden fallback matching.
- `tools/bazel/phase33_maintainer_decision_inputs.py` - Validates typed targets against the canonical Phase 32 snapshot and preserves them in safe handoffs.
- `tools/bazel/phase33_maintainer_decision_inputs_test.py` - Covers exact target publication and fail-closed boundary failures.
- `tools/bazel/phase34_decision_reconciliation.py` - Parses and reconciles canonical rows and normalized decisions without filesystem orchestration.
- `tools/bazel/phase34_decision_reconciliation_test.py` - Covers exact resolution, exhaustive axis semantics, and all required negative reason categories.

## Decisions Made

- Exact resolution requires the complete typed triple; gate, stream, path, prefix, and similar-subject fallback identities are never consulted.
- Multiple records for one exact target are blocking, whether they duplicate a value or conflict across values.
- A valid demotion decision records independent authorization state and never clears readiness; non-demotion approvals never grant demotion authority.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The repository's `pre-commit` command and repo-managed YAPF executable were unavailable locally. No formatter was installed ad hoc; Python syntax/tests, all plan-required Rust checks, `git diff --check`, and the repository-owned Phase 34 verifier passed.
- The first summary self-check used zsh's special lowercase `path` variable and temporarily changed command lookup inside that shell. The check was rerun in a fresh shell with `candidate_path`; all files, commits, and lifecycle fields were then verified.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 37-02 can integrate the typed reconciliation results into the authoritative Phase 34 ledger and real-producer regression.
- Phase 31 remains evidence authority, and Phase 38's cutover, stale-authority replacement, and production demotion scope remains untouched.

## Self-Check: PASSED

- All five implementation files and this summary exist.
- Task commits `c7ed3413f` and `41bbab4fe` exist in repository history.
- Summary lifecycle mode, lifecycle ID, generator provenance, and frontmatter boundaries match the originating plan.

*Phase: 37-reconcile-decisions-into-readiness*
*Completed: 2026-07-26*
