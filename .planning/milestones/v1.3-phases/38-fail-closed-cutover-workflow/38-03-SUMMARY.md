---
phase: 38-fail-closed-cutover-workflow
plan: "03"
subsystem: cutover-authority
tags: [fail-closed, authority-markers, attempt-correlation, rollback, python]
requires:
  - phase: 38-fail-closed-cutover-workflow
    provides: Phase 38 coordinator, guarded Phase 35 publication, and stale-authority verification findings
provides:
  - Durable private workflow-attempt and Phase 34 publication-state blockers
  - Exact-attempt validation for failed Phase 34 authority
  - Fresh blocked Phase 35 finalization after correlated producer failure
  - Actual-producer regressions for guard pre-creation and blocked-install faults
affects: [phase-38-verification, cutover-workflow, readiness-authority]
tech-stack:
  added: []
  patterns: [blocking-shell-before-payload, exact-attempt-authority, candidate-validation-before-marker-clear]
key-files:
  created: []
  modified:
    - tools/bazel/phase34_final_readiness_demotion_dry_run.py
    - tools/bazel/phase34_final_readiness_demotion_dry_run_test.py
    - tools/bazel/phase35_cutover_decision_artifact.py
    - tools/bazel/phase35_cutover_decision_artifact_test.py
    - tools/bazel/phase38_cutover_workflow.py
    - tools/bazel/phase38_cutover_workflow_test.py
    - tools/bazel/phase38_cutover_workflow_integration_test.py
key-decisions:
  - "Keep Phase 34 and Phase 35 as the only public authority bundles; private markers only revoke authority."
  - "Accept a nonzero Phase 34 result only when persisted blocked authority matches the coordinator's exact attempt and safe reason."
  - "Validate the installed Phase 35 candidate while protection remains active, then clear the workflow marker."
patterns-established:
  - "Blocking shell first: create a fixed-path blocking directory before attempting structured marker publication."
  - "Correlated failure authority: retained marker state or installed blocked bundle must match attempt identity and reason."
requirements-completed: [READY-02, READY-03, CUTOVER-01, CUTOVER-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 38-2026-07-26T16-29-23
generated_at: 2026-07-27T15:12:35Z
duration: 19min
completed: 2026-07-27
---

# Phase 38 Plan 03: Attempt-Correlated Fail-Closed Authority Summary

**Durable blocking markers and exact-attempt validation prevent stale Phase 34 readiness or Phase 35 approval from surviving publication faults.**

## Performance

- **Duration:** 19 min
- **Started:** 2026-07-27T14:53:46Z
- **Completed:** 2026-07-27T15:12:35Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Added fixed-path, fail-closed workflow-attempt and Phase 34 publication-state markers with strict payload, type, containment, symlink, and cleanup validation.
- Correlated every failed Phase 34 publication with the coordinator attempt and required exact persisted blocked authority before Phase 35 can finalize.
- Added focused and actual-producer regressions proving Phase 35 guard pre-creation failure and Phase 34 blocked-install failure cannot replay seeded approval.
- Preserved normal approved, blocked repair, targeted repair, and independent demotion behavior through the authoritative Phase 38 gate.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement durable marker primitives and focused path defenses** - `115172db9` (feat)
2. **Task 2: Close coordinator and actual-producer stale-authority reproductions** - `2040927fe` (fix)

## Files Created/Modified

- `tools/bazel/phase34_final_readiness_demotion_dry_run.py` - Publishes attempt-correlated blocked state before replacing failed-source authority.
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py` - Covers hostile marker paths and blocked-stage rollback.
- `tools/bazel/phase35_cutover_decision_artifact.py` - Rejects active workflow attempts and installs a fresh blocked bundle for correlated Phase 34 failure.
- `tools/bazel/phase35_cutover_decision_artifact_test.py` - Verifies true guard pre-creation failure blocks all canonical readers.
- `tools/bazel/phase38_cutover_workflow.py` - Owns attempt generation, exact authority evaluation, candidate validation, and protected marker cleanup.
- `tools/bazel/phase38_cutover_workflow_test.py` - Covers marker security, coordinator sequencing, and persistent guard failure.
- `tools/bazel/phase38_cutover_workflow_integration_test.py` - Exercises both faults through actual Phase 31-through-35 producers.

## Decisions Made

- Private markers are revocation metadata only and cannot grant readiness, cutover routing, or demotion authority.
- A restored older Phase 34 bundle remains non-authoritative behind retained current-attempt blocking state.
- Phase 35 publishes its existing blocked source-failure schema after a correlated Phase 34 failure instead of consuming restored unblocked content.
- Candidate Phase 35 output is inspected only for transition validation while the workflow marker remains active; public readers continue to reject it until cleanup succeeds.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Made direct module-selected unittest commands import production modules**

- **Found during:** Task 1 RED
- **Issue:** The plan's exact `python3 -m unittest tools.bazel...` command did not place `tools/bazel` on `sys.path` for existing bare production imports.
- **Fix:** Added deterministic repository-local module path setup in the affected test modules.
- **Files modified:** `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`, `tools/bazel/phase35_cutover_decision_artifact_test.py`, `tools/bazel/phase38_cutover_workflow_test.py`
- **Verification:** Both selected commands and the 199-test affected-module sweep passed.
- **Committed in:** `115172db9`, `2040927fe`

**2. [Rule 1 - Bug] Corrected filesystem fault fixtures**

- **Found during:** Task 1 GREEN iteration
- **Issue:** `Path.mkfifo()` is unavailable and unsafe-parent cases asserted the leaf marker existed even when the parent itself was the durable blocker.
- **Fix:** Used `os.mkfifo()` and asserted the blocking filesystem surface at either the shell or parent boundary.
- **Files modified:** `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`, `tools/bazel/phase38_cutover_workflow_test.py`
- **Verification:** All 28 focused marker tests passed without fixture failures.
- **Committed in:** `115172db9`

**Total deviations:** 2 auto-fixed (1 blocking issue, 1 test bug)

**Impact on plan:** Both fixes were limited to making the required security regressions executable and portable; no authority schema or workflow scope changed.

## Issues Encountered

- Bazel 9 rewrote only `MODULE.bazel.lock` format metadata during each authoritative gate. The incidental rewrite was reverted with a targeted patch before both commits.
- The full affected-module sweep initially found two old coordinator mocks targeting the replaced evaluator name and signature. The tests were updated to model workflow marker publication, exact-attempt evaluation, and cleanup sequencing.

## Known Stubs

None.

## Verification

- Task 1 selected marker tests: 28 passed.
- Task 2 selected fault regressions: 5 passed.
- Full affected Python modules: 199 passed.
- `just phase38-verify`: passed, including focused/integration tests before default blocked publication.
- `cargo fmt --all`: passed before each task commit.
- `cargo clippy --all-targets --all-features -- -D warnings`: passed before each task commit.
- `cargo build --all-targets --all-features`: passed before each task commit.
- `cargo test --all-features`: passed before each task commit.
- `git diff --check`: passed before each task commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The two remaining Phase 38 stale-authority gaps are covered by focused and actual-producer tests.
- Phase 38 verification can now assess the completed gap closure with no known implementation blocker.

## Self-Check: PASSED

- All seven implementation/test files and this summary exist.
- Task commits `115172db9` and `2040927fe` are present in repository history.
- Summary diff validation passed.

*Phase: 38-fail-closed-cutover-workflow*
*Completed: 2026-07-27*
