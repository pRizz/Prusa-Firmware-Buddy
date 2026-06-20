---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T16:54:06Z
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
  warning: 2
  info: 0
  total: 2
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-06-20T16:54:06Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Re-reviewed the listed Phase 18 verifier, contract manifest, tests, Bazel wiring, shell workflow, and just recipe at standard depth after fix `8ae5d32e4`. This review used `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and Bright Builds architecture, code-shape, verification, and testing standards. No project-local skills were present under `.claude/skills/` or `.agents/skills/`.

Fix `8ae5d32e4` correctly reuses the retained-acceptance consistency check in `--security-only` for top-level demotion overclaims. Two warning-level gaps remain in the Phase 18 verifier: row-level generated artifacts can still overclaim retained packet acceptance when demotion stays blocked, and the redaction scanner misses common API-key field names.

Verification performed:

- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 41 tests.
- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --security-only` passed.
- Targeted temp-root probes reproduced both findings without modifying source files.

## Warnings

### WR-01: Security scan misses row-level retained acceptance overclaims

**File:** `tools/bazel/phase18_cutover_review.py:1324`
**Issue:** When generated `run-manifest.json` says `decision_inputs_supplied: true`, `validate_generated_overclaim_guards` only rejects `demotion_allowed: true` if it conflicts with validated decision input, then returns before checking `retained-code-acceptance-summary.json`. A stale or tampered summary can therefore change retained packet rows from `blocked` to `accepted` while `demotion_allowed` remains false, and `--security-only --decision-input ...` still passes. That is a retained-code acceptance overclaim in a machine-readable Phase 18 artifact.
**Fix:**
```python
expected_retained_rows = normalize_retained_reviews(packets, retained_reviews)
expected_retained_statuses = {row["id"]: row["status"] for row in expected_retained_rows}

retained_path = output_dir / "retained-code-acceptance-summary.json"
if retained_path.exists():
    retained = json.loads(retained_path.read_text(encoding="utf-8"))
    for row in retained.get("packets", []):
        packet_id = row.get("id")
        if row.get("status") != expected_retained_statuses.get(packet_id):
            errors.append(f"generated retained-code packet status mismatch: {packet_id}")
```
Apply the same comparison to `normalized-final-demotion-results.json` row statuses, and add a regression test that tampers generated retained rows to `accepted` while decision input keeps those packet reviews `blocked`.

### WR-02: Redaction scan allows common API-key field names

**File:** `tools/bazel/phase18_cutover_review.py:165`
**Issue:** `reject_forbidden_json_fields` only rejects exact keys listed in `FORBIDDEN_FIELD_NAMES`, and that list omits common secret-bearing names such as `api_key`, `apikey`, `api-key`, `access_token`, and `bearer_token`. A Phase 18 decision input with an `api_key` field currently passes `--security-only`, weakening the name-only/redacted evidence boundary.
**Fix:** Extend the forbidden field-name vocabulary with common credential key variants and add focused tests for at least `api_key` and `access_token`.

---

_Reviewed: 2026-06-20T16:54:06Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
