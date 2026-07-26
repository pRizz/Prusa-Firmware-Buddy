---
phase: 38-fail-closed-cutover-workflow
plan: 02
subsystem: cutover-workflow-orchestration
tags: [fail-closed, coordinator, bazel, authority, integration-testing]
requires:
  - phase: 38-fail-closed-cutover-workflow
    plan: 01
    provides: guarded Phase 34 and Phase 35 canonical publication
  - phase: 37-reconcile-decisions-into-readiness
    provides: decision-aware Phase 34 readiness authority
provides:
  - Status-preserving Phase 34-to-35 production coordinator
  - Actual-producer Phase 31-through-35 route and stale-authority matrix
  - Authoritative Bazel and just verification gate with tests before publication
affects: [cutover-verification, release-authority, production-cutover-planning]
tech-stack:
  added: []
  patterns:
    - pure final-authority evaluation behind a small imperative coordinator
    - mandatory finalization before nonzero workflow return
    - hermetic real-producer regression runfiles
key-files:
  created:
    - tools/bazel/phase38_cutover_workflow.py
    - tools/bazel/phase38_cutover_workflow_test.py
    - tools/bazel/phase38_cutover_workflow_integration_test.py
  modified:
    - tools/bazel/phase35_cutover_decision_artifact.py
    - tools/bazel/phase35_cutover_decision_artifact_test.py
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - BUILD.bazel
    - justfile
key-decisions:
  - "Preserve the earliest nonzero Phase 34 or Phase 35 status only after validating the final canonical authority."
  - "Authorize production-cutover planning only from a consistent approved verdict and production route; evaluate demotion independently."
  - "Route both Phase 35 and Phase 38 shell entrypoints through one explicit status-capturing coordinator."
patterns-established:
  - "A validated blocked replacement is a safe final authority state even when the originating operation remains nonzero."
  - "Bazel and just gates execute focused and actual-producer regressions before canonical default publication."
requirements-completed: [READY-02, READY-03, CUTOVER-01, CUTOVER-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 38-2026-07-26T16-29-23
generated_at: 2026-07-26T18:06:55Z
duration: 19m
completed: 2026-07-26
---

# Phase 38 Plan 02: Fail-Closed Cutover Workflow Summary

One coordinator now finalizes Phase 34 and Phase 35 authority before returning operational failure, with real-producer route coverage and a tests-first Bazel/just gate.

## Performance

- **Duration:** 19 minutes
- **Started:** 2026-07-26T17:47:53Z
- **Completed:** 2026-07-26T18:06:55Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added a production coordinator with a pure final-status evaluator that preserves the earliest nonzero status after safe Phase 35 finalization.
- Rejected missing, contradictory, guarded, malformed, unreadable, stale, absolute, traversal, symlink-escape, wrong-root, and non-directory authority states.
- Proved default blocked, complete approved, named targeted repair, invalid Phase 31, and invalid Phase 33 routes through actual Phase 31-through-35 producers.
- Proved seeded Phase 34/35 approval is durably replaced before invalid-source workflows return nonzero.
- Wired hermetic Bazel runfiles, root aliases, explicit shell status propagation, and `just phase38-verify` test-before-publication ordering.

## Task Commits

1. **Task 1 RED: coordinator authority regressions** - `06d7ba57f`
2. **Task 1 GREEN: fail-closed cutover coordinator** - `00178cbc2`
3. **Task 2 RED: actual-producer workflow matrix** - `e5c9af33a`
4. **Task 2 GREEN: actual route matrix and readiness-reason fix** - `a092a233b`
5. **Task 3: authoritative Phase 38 gate wiring** - `85252f4e9`

## Files Created/Modified

- `tools/bazel/phase38_cutover_workflow.py` - Coordinates Phase 34/35 publication and evaluates final route, readiness, demotion, and preserved status.
- `tools/bazel/phase38_cutover_workflow_test.py` - Covers status truth tables, guard states, route/demotion predicates, sequencing, and exact repository wiring.
- `tools/bazel/phase38_cutover_workflow_integration_test.py` - Exercises actual Phase 31-through-35 producer paths and stale-authority replacement.
- `tools/bazel/phase35_cutover_decision_artifact.py` - Separates readiness-blocking reasons from independent demotion diagnostics and validates coordinator-based Phase 35 wiring.
- `tools/bazel/phase35_cutover_decision_artifact_test.py` - Guards readiness-reason projection against demotion-only diagnostics.
- `tools/bazel/BUILD.bazel` - Adds hermetic Phase 38 coordinator and regression targets with actual-producer runfiles.
- `tools/bazel/rust_workflow.sh` - Dispatches Phase 35/38 finalization through one explicit status-preserving coordinator.
- `BUILD.bazel` - Exposes root Phase 38 verification aliases.
- `justfile` - Runs Phase 38 tests before default authority publication.

## Decisions Made

- Phase 35 runs after any Phase 34 result whose canonical success or blocked replacement validates; an invalid Phase 34 bundle prevents Phase 35 consumption.
- The final evaluator never changes a Phase 34 or Phase 35 operational failure into success after fallback publication.
- Cutover verdict, route, readiness, and demotion are distinct predicates; approved cutover never implies reference demotion.
- Any present Phase 35 guard is blocking, including a structurally valid guard, because its presence means canonical mutation has not completed safely.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Excluded independent demotion diagnostics from cutover-readiness reasons**

- **Found during:** Task 2 actual-producer demotion cases
- **Issue:** Phase 34 correctly appended demotion-only missing or rejected diagnostics to the packet, but Phase 35 projected every packet reason into readiness blockers and downgraded otherwise approved cutover authority.
- **Fix:** Derived Phase 35 cutover reasons only from ledger rows whose readiness effect is blocked, with a fail-closed fallback when blocked readiness has no such rows.
- **Files modified:** `tools/bazel/phase35_cutover_decision_artifact.py`, `tools/bazel/phase35_cutover_decision_artifact_test.py`
- **Verification:** 74 Phase 35 tests and all 8 actual-producer Phase 38 integration cases passed.
- **Committed in:** `a092a233b`

**2. [Rule 3 - Blocking] Updated Phase 35 exact-wiring validation for coordinator dispatch**

- **Found during:** Task 3 shell wiring
- **Issue:** The existing Phase 35 wiring validator required direct Phase 34 and Phase 35 quick commands, which contradicted the planned single coordinator finalization path.
- **Fix:** Replaced those exact commands with the explicit coordinator invocation while retaining the upstream producer and wiring-only checks.
- **Files modified:** `tools/bazel/phase35_cutover_decision_artifact.py`
- **Verification:** All 74 Phase 35 tests and `just phase38-verify` passed.
- **Committed in:** `85252f4e9`

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking issue)

**Impact on plan:** Both fixes were required to preserve readiness/demotion independence and make the planned coordinator the sole Phase 34/35 finalization path. No new authority schema or policy was added.

## Issues Encountered

- Bazel 9 rewrote `MODULE.bazel.lock` from lock format 26 to 28 during local verification. The generated rewrite was removed because it was unrelated to this plan.
- Lifecycle validation cannot become globally valid until the parent orchestrator adds lifecycle fields to the existing `38-01-SUMMARY.md` and creates `38-VERIFICATION.md`. This summary contains the required Phase 38 lifecycle metadata.

## Known Stubs

None. Empty collections found by the stub scan are test accumulators, blocked-state schema values, or local control-flow initialization; no unwired mock authority or placeholder publication remains.

## Verification

- `python3 tools/bazel/phase38_cutover_workflow_test.py -q` - 27 passed
- `python3 tools/bazel/phase38_cutover_workflow_integration_test.py -q` - 8 passed
- `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q` - 74 passed
- `bash -n tools/bazel/rust_workflow.sh` - passed
- `just phase38-verify` - passed twice; 225 focused/integration tests per run, followed by validated blocked targeted-repair publication
- `cargo fmt --all` - passed
- `cargo clippy --all-targets --all-features -- -D warnings` - passed
- `cargo build --all-targets --all-features` - passed
- `cargo test --all-features` - 136 unit tests and 4 doc-test suites passed
- `git diff --check` - passed
- `verify lifecycle 38 --require-plans` - plan 38-02 metadata valid; global phase validation awaits parent-owned 38-01 summary metadata and `38-VERIFICATION.md`

## User Setup Required

None - no external services or credentials are required.

## Next Phase Readiness

- The parent orchestrator can run Phase 38 code review and verification against one authoritative `just phase38-verify` path.
- Default authority remains deliberately blocked and routes to targeted repair until complete valid inputs and explicit decisions are supplied.

## Self-Check: PASSED

- All nine created or modified implementation, test, and wiring files exist.
- Task commits `06d7ba57f`, `00178cbc2`, `e5c9af33a`, `a092a233b`, and `85252f4e9` exist in repository history.
- No unplanned network endpoint, authentication path, schema, or external trust-boundary surface was introduced.
