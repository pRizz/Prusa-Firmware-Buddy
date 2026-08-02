---
phase: 38-fail-closed-cutover-workflow
fixed_at: 2026-07-26T18:27:47Z
review_path: .planning/phases/38-fail-closed-cutover-workflow/38-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 38: Code Review Fix Report

**Fixed at:** 2026-07-26T18:27:47Z
**Source review:** `.planning/phases/38-fail-closed-cutover-workflow/38-REVIEW.md`
**Iteration:** 1

**Summary:**

- Findings in scope: 3
- Fixed: 3
- Skipped: 0

## Fixed Issues

### CR-01: Non-JSON read failures bypass the Phase 34 blocked replacement

**Files modified:** `tools/bazel/phase34_final_readiness_demotion_dry_run.py`, `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
**Commit:** c83caaccc
**Applied fix:** Converted Unicode and filesystem failures at the JSON read boundary into `VerificationError` while preserving missing-input semantics. Added invalid-UTF-8 and injected read-error regressions for Phase 31 manifest/receipt and Phase 33 handoff/register inputs; every case proves the exact blocked Phase 34 bundle replaces seeded prior authority.

### CR-02: Nonzero workflow results can still advertise positive authority

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase38_cutover_workflow.py`, `tools/bazel/phase38_cutover_workflow_test.py`
**Commit:** 99e383807
**Applied fix:** Made successful Phase 34 and Phase 35 operations a prerequisite for `final_authority_available`, `production_cutover_planning`, and `reference_demotion_authorized`. Added separate truth-table regressions for each nonzero producer outcome with otherwise approved/open authority.

### CR-03: Invalid Phase 34 authority leaves prior Phase 35 approval unguarded

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase38_cutover_workflow.py`, `tools/bazel/phase38_cutover_workflow_test.py`, `tools/bazel/phase38_cutover_workflow_integration_test.py`
**Commit:** 87260511d
**Applied fix:** Published and validated the existing path-safe Phase 35 authority guard before Phase 34 starts. Successful Phase 35 staged installation remains the only path that clears it. Added unit coverage for ordering and guard-publication failure plus a real-producer regression proving a forced Phase 34 canonical-path failure leaves seeded Phase 35 approval blocked by the durable guard.

## Verification

- `python3 -m py_compile` passed for every changed Python module and test.
- Phase 34 focused suite passed: 53 tests.
- Phase 38 unit suite passed: 30 tests after all fixes.
- Phase 38 real-producer integration suite passed: 9 tests after all fixes.
- Before every fix commit, `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` passed.
- Before every fix commit, `bash -n tools/bazel/rust_workflow.sh`, `just phase38-verify`, and scoped `git diff --check` passed.
- Final three-commit range passed `git diff --check`.

***

_Fixed: 2026-07-26T18:27:47Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
