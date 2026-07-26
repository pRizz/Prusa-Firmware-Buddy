---
phase: 36-normalize-evidence-and-blocker-rows
fixed_at: 2026-07-26T02:04:24Z
review_path: .planning/phases/36-normalize-evidence-and-blocker-rows/36-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 36: Code Review Fix Report

**Fixed at:** 2026-07-26T02:04:24Z
**Source review:** `.planning/phases/36-normalize-evidence-and-blocker-rows/36-REVIEW.md`
**Iteration:** 1

**Summary:**

- Findings in scope: 4
- Fixed: 4
- Skipped: 0

## Fixed Issues

### CR-01: Release adapter trusts any matching basename instead of the contracted Phase 26 artifact

**Files modified:** `tools/bazel/phase32_blocker_register_triage.py`, `tools/bazel/phase32_blocker_register_triage_test.py`
**Commit:** 1127c1ff4
**Status:** fixed: requires human verification
**Applied fix:** Enforced the exact contracted Phase 26 table path, validated the accepted Phase 31 release receipt's required provenance before trusting it, and added a producer-backed same-basename path substitution regression.

### CR-02: Unsupported demotion authorization values disappear from the blocker register

**Files modified:** `tools/bazel/phase32_blocker_register_triage.py`, `tools/bazel/phase32_blocker_register_triage_test.py`
**Commit:** 5e1905054
**Status:** fixed: requires human verification
**Applied fix:** Added explicit Phase 27 and Phase 28 authorization dispatch so unsupported values emit critical `unknown_unclassified` demotion rows, with separate producer-backed regressions for both artifacts.

### WR-01: Malformed Phase 26 tables are classified as high instead of critical

**Files modified:** `tools/bazel/manifests/phase32_blocker_register_triage_contract.json`, `tools/bazel/phase32_blocker_register_triage.py`, `tools/bazel/phase32_blocker_register_triage_test.py`
**Commit:** 47b45d19d
**Status:** fixed: requires human verification
**Applied fix:** Made the malformed policy critical, added contract validation that both fail-closed shape declarations match their policy-map severity and proof eligibility, and added a malformed Phase 26 table integration regression.

### WR-02: Unconditional policy overrides downgrade unknown Phase 27/28 inputs

**Files modified:** `tools/bazel/phase32_blocker_register_triage.py`, `tools/bazel/phase32_blocker_register_triage_test.py`
**Commit:** 3d04a5719
**Status:** fixed: requires human verification
**Applied fix:** Limited Phase 27 residual and Phase 28 readiness policy overrides to recognized inputs so unknown shapes retain critical fail-closed classification, with one producer-backed regression per adapter.

***

_Fixed: 2026-07-26T02:04:24Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
