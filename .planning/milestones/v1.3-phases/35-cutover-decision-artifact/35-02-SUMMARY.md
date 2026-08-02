---
phase: 35-cutover-decision-artifact
plan: "02"
subsystem: ci-evidence
tags: [bazel, cutover, fail-closed, atomic-replacement, evidence]
requires:
  - phase: 35-cutover-decision-artifact
    provides: Phase 35 cutover reducer, audit index, route projection, and eight-artifact normal bundle
provides:
  - Contracted three-artifact blocked bundle for invalid or unavailable source evidence
  - Atomic staged replacement of prior Phase 35 canonical output
  - End-to-end regressions proving stale approvals cannot survive source failures
affects: [cutover-verification, milestone-routing, reference-demotion]
tech-stack:
  added: []
  patterns: [sibling-directory staging, validated atomic bundle replacement, safe failure reason taxonomy]
key-files:
  created: []
  modified:
    - tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json
    - tools/bazel/phase35_cutover_decision_artifact.py
    - tools/bazel/phase35_cutover_decision_artifact_test.py
key-decisions:
  - "Any source-boundary failure publishes the exact durable three-artifact blocked bundle before the command returns nonzero."
  - "Both normal and failure bundles are validated in sibling staging directories before replacing the canonical output."
  - "Failure output keeps cutover verdict, demotion validation/value/source lineage, and demotion gate state independent."
patterns-established:
  - "Fail-closed evidence publication: replace stale authority with a minimal readable blocked result before surfacing failure."
  - "Atomic evidence bundles: stage and validate the complete artifact set, then replace the canonical directory as one unit."
requirements-completed: [CUTOVER-01, CUTOVER-02, CUTOVER-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 35-2026-07-25T21-06-10
generated_at: 2026-07-25T23:56:03Z
duration: 14min
completed: 2026-07-25
---

# Phase 35 Plan 02: Stale Approval Gap Closure Summary

**Atomic fail-closed Phase 35 publication replaces stale cutover approvals with a contract-safe blocked decision and targeted-repair route whenever source validation fails.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-07-25T23:42:15Z
- **Completed:** 2026-07-25T23:56:03Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Defined an exact three-artifact failure bundle and seven safe, non-secret-bearing source failure reason codes.
- Implemented sibling-directory staging and validated canonical replacement for both the normal eight-artifact bundle and the fail-closed bundle.
- Added nine end-to-end regressions that seed an approved output, corrupt each source boundary family, require a nonzero result, and prove that no stale approval artifact survives.
- Preserved independent cutover, demotion decision, source lineage, and demotion gate projections in every failure artifact.

## Task Commits

Each task was committed atomically:

1. **Task 1: Freeze the source-failure bundle contract and add RED stale-approval regressions** - `09ad9b56e` (test)
2. **Task 2: Implement atomic full/failure replacement and durable fail-closed CLI behavior** - `dbced213b` (fix)

## Files Created/Modified

- `tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json` - Contracts the exact failure artifact set, safe reasons, and no-authority projections.
- `tools/bazel/phase35_cutover_decision_artifact.py` - Classifies source failures, validates staged output, and atomically replaces canonical artifacts.
- `tools/bazel/phase35_cutover_decision_artifact_test.py` - Exercises stale approval replacement across missing, malformed, stale, mismatched, tainted, unsafe, and unreadable inputs.

## Decisions Made

- Source-validation failures are durable publication outcomes: the command installs a readable blocked bundle before returning nonzero.
- A prior canonical directory is never restored after a failed generation because doing so could restore stale authority.
- The fallback bundle contains no inferred owners, repair actions, trusted source references, audit index, report, snapshots, exception IDs, or production authorization.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The repository environment did not expose a `pre-commit` executable. An isolated temporary runner was installed outside the repository and used with the repository configuration; all scoped hooks passed.
- Bazel updated `MODULE.bazel.lock` during the acceptance gate. The generated side effect was restored to its exact pre-gate SHA-256 (`21587df8a47a42952e5301f59f4809b23eba5f336780847d0c3bc02422275a03`).

## Verification

- `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q` - 58 passed.
- `python3 tools/bazel/phase35_cutover_decision_artifact.py --contract-only` - passed.
- `python3 tools/bazel/phase35_cutover_decision_artifact.py --wiring-only` - passed.
- `python3 tools/bazel/phase35_cutover_decision_artifact.py --security-only` - passed.
- `bazel run //tools/bazel:phase35_verify_tests` - 58 passed.
- `bazel run //tools/bazel:phase35_verify` - complete Phase 31-35 chain passed.
- `just phase35-verify` - tests and verifier passed.
- `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q` - 36 passed.
- `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` - passed.
- Scoped repository pre-commit hooks and `git diff --check` - passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CUTOVER-01 through CUTOVER-03 now remain fail-closed even when required source evidence cannot be trusted or read.
- Phase 35 normal output retains the exact eight-artifact bundle and all existing verdict/route truth tables.
- No known implementation stubs or new unmodeled trust-boundary surfaces remain.

## Self-Check: PASSED

- All three modified implementation/test/contract files and this summary exist.
- Task commits `09ad9b56e` and `dbced213b` are reachable from repository history.
- `MODULE.bazel.lock` matches its pre-verification SHA-256 and `.planning/config.json` remains untouched by this plan.

***

*Phase: 35-cutover-decision-artifact*
*Completed: 2026-07-25*
