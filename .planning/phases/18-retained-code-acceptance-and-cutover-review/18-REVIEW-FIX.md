---
phase: 18-retained-code-acceptance-and-cutover-review
fixed_at: 2026-06-20T15:56:14Z
review_path: .planning/phases/18-retained-code-acceptance-and-cutover-review/18-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 18: Code Review Fix Report

**Fixed at:** 2026-06-20T15:56:14Z
**Source review:** .planning/phases/18-retained-code-acceptance-and-cutover-review/18-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2
- Fixed: 2
- Skipped: 0

## Fixed Issues

### CR-01: Final demotion accepts rejected decisions and empty evidence

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 7dd3060e3
**Applied fix:** Final decision validation now requires `passed` rows to use `decision: approve` with non-empty Phase 18 evidence refs. `exception-approved` and `not-applicable` rows require `decision: exception`, non-empty final evidence refs, and complete exception metadata with non-empty exception evidence refs. The demotion predicate now rejects missing or mismatched decision objects instead of trusting status alone.

### CR-02: Decision input can omit the Phase 18 lifecycle envelope

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 6c06a052a
**Applied fix:** Decision input now requires a `decision_packet` object before retained reviews or final decisions are accepted, and validates that the packet is bound to Phase 18 and lifecycle id `18-2026-06-20T14-27-15`.

---

_Fixed: 2026-06-20T15:56:14Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
