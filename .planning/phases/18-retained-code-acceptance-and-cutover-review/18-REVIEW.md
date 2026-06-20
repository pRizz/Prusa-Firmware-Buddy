---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T16:25:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - tools/bazel/manifests/phase18_cutover_review_contract.json
  - tools/bazel/phase18_cutover_review.py
  - tools/bazel/phase18_cutover_review_test.py
  - tools/bazel/BUILD.bazel
  - BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - justfile
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-06-20T16:25:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Re-reviewed the listed Phase 18 verifier, contract manifest, tests, Bazel wiring, shell workflow, and just recipe at standard depth after fix `7e9d00a46` and report update `6efdd6e50`. This review used the repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and Bright Builds architecture, code-shape, verification, and testing standards. No project-local skills were present under `.claude/skills/` or `.agents/skills/`.

The prior report's retained approver-role, custom output directory, and final decision ID findings are fixed in the current files. One generated-artifact overclaim guard gap remains.

Verification performed:

- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 36 tests.
- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --quick --output-dir build/ci-evidence/phase18/review-check` passed.
- `python3 tools/bazel/phase18_cutover_review.py --security-only --output-dir build/ci-evidence/phase18/review-check` passed on restored quick artifacts.
- Targeted tamper check reproduced WR-01: changing `run-manifest.json` to `"decision_inputs_supplied": "false"` and `demotion_allowed: true` still made `--security-only` print `Phase 18 security scan passed`.

## Warnings

### WR-01: No-decision overclaim guard can be bypassed with a non-boolean manifest flag

**File:** `tools/bazel/phase18_cutover_review.py:1275`
**Issue:** `validate_generated_overclaim_guards` returns whenever `decision_inputs_supplied` is not exactly boolean `False`. A malformed or tampered generated `run-manifest.json` can set `"decision_inputs_supplied": "false"` or omit the flag, then set `demotion_allowed: true`; the security scan skips the no-decision overclaim checks for `demotion_allowed`, allowed final statuses, and accepted retained packet statuses. This weakens the Phase 18 guard that is supposed to reject unsupported reference-demotion claims in generated review artifacts.
**Fix:**
```python
decision_inputs_supplied = run_manifest.get("decision_inputs_supplied")
if not isinstance(decision_inputs_supplied, bool):
    errors.append("generated run-manifest.json decision_inputs_supplied must be boolean")
    return
if decision_inputs_supplied:
    return
if run_manifest.get("demotion_allowed") is True:
    errors.append("generated no-decision run-manifest.json cannot set demotion_allowed true")
```
Also add regression tests for string, missing, or otherwise non-boolean `decision_inputs_supplied` values combined with `demotion_allowed: true`, an allowed final criterion status, or an accepted retained packet status.

---

_Reviewed: 2026-06-20T16:25:00Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
