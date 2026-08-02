---
phase: 40-file-length-refactoring
plan: 18
subsystem: testing
tags: [python, unittest, bazel, file-length, cutover]
requires:
  - phase: 40-17
    provides: "Terminal 841-exception baseline and ordinary Phase 33-34 test composition"
provides:
  - "Ordinary Phase 35 cutover cases, failure, and security mixins"
  - "Directly declared guarded-publication and source-failure replacement test classes"
  - "Exact 75-test inventory through explicit imports and unittest discovery"
  - "Removal of Phase 35 executable test-source reconstruction"
affects: [phase35-cutover-decision, phase38-cutover-workflow, phase40-verification]
tech-stack:
  added: []
  patterns: [ordinary behavior mixins, stable unittest entrypoint, narrow test-contract support]
key-files:
  created:
    - tools/bazel/phase35_test_support.py
  modified:
    - tools/bazel/BUILD.bazel
    - tools/bazel/phase35_cutover_decision_artifact_test.py
    - tools/bazel/phase35_cutover_decision_cases_test.py
    - tools/bazel/phase35_cutover_decision_failure_test.py
    - tools/bazel/phase35_cutover_decision_security_test.py
    - tools/bazel/phase35_guarded_publication_test.py
    - tools/bazel/phase35_source_failure_replacement_test.py
key-decisions:
  - "Keep Phase35TestSupport fixture and helper methods in the stable public entrypoint, then compose three phase-local behavior mixins through ordinary inheritance."
  - "Use a narrow phase35_test_support.py only for shared imports and immutable test-contract vocabulary, leaving security behavior in the security module."
patterns-established:
  - "Phase-local test behavior clusters expose ordinary mixins whose removal visibly removes that behavior from the public suite."
  - "Encoded-payload retirement proves AST-normalized test-body parity and exact recursive unittest inventory parity."
requirements-completed: [D-05, D-06, D-08, D-11, D-12, D-13, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-28T03:40:58Z
duration: 7min
completed: 2026-07-27
---

# Phase 40 Plan 18: Phase 35 Test Materialization Summary

**Phase 35 now exposes the same 75 cutover, security, publication, and source-replacement tests through ordinary Python mixins and classes without executable source strings.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-07-28T03:33:56Z
- **Completed:** 2026-07-28T03:40:58Z
- **Tasks:** 1
- **Files modified:** 8

## Accomplishments

- Materialized 1,982 logical payload lines into named Phase 35 cases, failure, security, guarded-publication, and source-failure classes while preserving every encoded method/class at AST-normalized parity.
- Replaced `importlib.import_module`, `textwrap`, `TEST_METHODS`, `TEST_CLASSES`, and `exec()` assembly with explicit imports and ordinary inheritance/discovery.
- Preserved direct-script behavior, both existing Phase 35 Bazel labels, fail-closed publication/source-replacement behavior, and exactly 75 unique public test names.
- Kept all seven Python files below 629 physical lines; the largest is the 532-line cutover cases mixin.

## Task Commits

1. **Task 1: Materialize the Phase 35 cutover and guarded-publication suites** - `570c4d174` (refactor)

## Files Created/Modified

- `tools/bazel/phase35_test_support.py` - narrow shared imports and immutable Phase 35 test-contract vocabulary.
- `tools/bazel/phase35_cutover_decision_artifact_test.py` - stable fixture-owning public `unittest` entrypoint with explicit mixin composition.
- `tools/bazel/phase35_cutover_decision_cases_test.py` - ordinary cutover contract, verdict, audit-link, and repair-scope behavior mixin.
- `tools/bazel/phase35_cutover_decision_failure_test.py` - ordinary source, demotion, path, and failure-domain behavior mixin.
- `tools/bazel/phase35_cutover_decision_security_test.py` - ordinary security and authority-boundary behavior mixin.
- `tools/bazel/phase35_guarded_publication_test.py` - directly declared guarded-publication `TestCase`.
- `tools/bazel/phase35_source_failure_replacement_test.py` - directly declared source-failure replacement `TestCase`.
- `tools/bazel/BUILD.bazel` - includes the narrow support module in the unchanged `phase35_test_modules` runfiles boundary.

## Decisions Made

- Retained all fixture construction and helper behavior in `Phase35TestSupport` inside the stable public entrypoint.
- Introduced a narrow support module for shared imports and immutable contract constants because importing the public entrypoint from its mixins would create a circular/direct-script split identity.
- Kept the guarded-publication and source-failure suites as independent imported `unittest.TestCase` classes, preserving their original setup/cleanup lifecycle and discovery identity.

## Verification Evidence

- Pre-edit inventory: 75 discovered names, 75 unique names, no duplicates; sorted baseline SHA-256 `be6027fa88420ddc9379c597825dc004f7f4a63f4f71e1a63938630a66299449`.
- Post-edit inventory: exact sorted-name equality with the baseline, 75 discovered names, 75 unique names, and no duplicates.
- Payload parity: all 24 cases methods, 16 failure methods, 11 security methods, guarded-publication class, and source-failure replacement class match their normalized pre-edit ASTs.
- Direct entrypoint: 75 tests passed.
- Stable Bazel labels: `//tools/bazel:phase35_verify_tests` and `//tools/bazel:phase35_verify` passed.
- Required façades: `just phase35-verify`, `just phase38-verify`, and `just phase40-verify --terminal` passed.
- Terminal policy: 841 permanent exceptions, zero temporary exceptions, and three owned permanent exceptions.
- Managed checks: `bun scripts/bright-builds-check.ts all` reported `SUMMARY all findings=0`.
- Static checks: seven-file `py_compile`, forbidden-reconstruction scan, sub-629 assertions, `git diff --check`, and exact `MODULE.bazel.lock` restoration passed.
- Required pre-commit sequence passed in order: Cargo format, Clippy with warnings denied, all-target/all-feature build, and all-feature tests (136 unit tests plus documentation tests).

## Deviations from Plan

### Approved Architecture Adjustment

**1. Added a narrow shared Phase 35 test-contract module and BUILD wiring**

- **Found during:** Task 1 (materializing the mixins)
- **Issue:** Keeping constants in the public entrypoint would require mixins to import that entrypoint while it imported the mixins, breaking ordinary direct-script composition; making the security module the generic support owner would violate concept ownership.
- **Resolution:** Kept fixture/helper behavior in the public entrypoint and added `phase35_test_support.py` for shared imports/constants only, wired through the existing test filegroup.
- **Files modified:** `tools/bazel/phase35_test_support.py`, `tools/bazel/BUILD.bazel`
- **Verification:** Direct and Bazel discovery, AST parity, Phase 35/38/40 gates, and Bright Builds all passed.
- **Committed in:** `570c4d174`

**Total deviations:** 1 approved architecture adjustment
**Impact on plan:** The additional narrow module prevents circular imports and preserves concept ownership without changing any public label or behavior.

## Issues Encountered

- Bazel rewrote `MODULE.bazel.lock` from format 26 to 28 during verification. The two-field drift was restored exactly before the implementation commit.
- The first mechanical layout incorrectly made the security module the general support owner. It was replaced before verification/commit with the narrower support boundary described above.
- A trailing blank line in the new support module was caught by staged diff review, removed, and the implementation commit was amended only after rerunning the required Rust sequence.

## Known Stubs

None. Empty collections and empty string inputs in the materialized methods are deliberate failure-domain arrangements preserved from the original tests.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The final Phase 33-35 executable-source reconstruction gap is closed with exact behavior and discovery parity.
- Phase 40 is ready for independent terminal re-verification; this plan does not replace the verifier-owned `40-VERIFICATION.md`.

## Self-Check: PASSED

- The Plan 18 summary exists at the expected phase path.
- Implementation commit `570c4d174` exists in repository history.
- All eight implementation paths are present in the task commit, `MODULE.bazel.lock` has no diff, and no unrelated worktree changes remain.

***

*Phase: 40-file-length-refactoring*
*Completed: 2026-07-27*
