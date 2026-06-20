---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T17:01:30Z
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

**Reviewed:** 2026-06-20T17:01:30Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Re-reviewed the listed Phase 18 verifier, contract manifest, tests, Bazel wiring, shell workflow, and just recipe at standard depth after fix `c480970c4`. This review used `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and Bright Builds architecture, code-shape, verification, and testing standards. No project-local skills were present under `.claude/skills/` or `.agents/skills/`.

Fix `c480970c4` resolves the prior row-status overclaim gap by comparing generated final and retained row statuses against validated decision input. One warning-level redaction gap remains in the Phase 18 verifier.

Verification performed:

- `python3 -m py_compile tools/bazel/phase18_cutover_review.py tools/bazel/phase18_cutover_review_test.py` passed.
- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 43 tests.
- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --security-only` passed.
- Targeted temp-root probe reproduced the finding: a decision input containing top-level `apiKey` returned exit code 0 with "Phase 18 security scan passed."

## Warnings

### WR-01: Redaction Scan Allows CamelCase API-Key Fields

**File:** `tools/bazel/phase18_cutover_review.py:427`
**Issue:** `reject_forbidden_json_fields` only compares JSON keys by exact spelling against `FORBIDDEN_FIELD_NAMES`. The recent fix adds `api_key`, `api-key`, `apikey`, `access_token`, and `bearer_token`, but common camelCase forms such as `apiKey` still pass because the decision-input schema allows extra fields. A Phase 18 maintainer decision input or generated artifact can therefore contain an obvious credential-bearing field while `--security-only` reports success, weakening the name-only/redacted evidence boundary.
**Fix:**
```python
FORBIDDEN_NORMALIZED_FIELD_NAMES = {
    "accesstoken",
    "apikey",
    "authorization",
    "authorizationheader",
    "bearertoken",
    "connecttoken",
    "credentialvalue",
    "password",
    "privatekey",
    "secret",
}


def normalized_field_name(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


if key in FORBIDDEN_FIELD_NAMES or normalized_field_name(key) in FORBIDDEN_NORMALIZED_FIELD_NAMES:
    errors.append(f"{source_name} contains forbidden field name {key} at {nested_path}")
```
Add regression tests for `apiKey`, `accessToken`, and one authorization-header variant in both decision input and generated artifact scans.

---

_Reviewed: 2026-06-20T17:01:30Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
