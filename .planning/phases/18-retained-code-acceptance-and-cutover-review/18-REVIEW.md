---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T17:08:39Z
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
  critical: 1
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-06-20T17:08:39Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Re-reviewed the listed Phase 18 verifier, manifest, tests, Bazel wiring, workflow wrapper, and just recipe after fix `4d9f1f88d`. Material guidance applied: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` (no active overrides), and Bright Builds core architecture, code-shape, verification, and testing standards.

The Phase 18 tests pass, but the verifier still has security/correctness gaps in the redaction and generated-overclaim guards.

Verification run:

```text
python3 tools/bazel/phase18_cutover_review_test.py
Ran 44 tests in 7.363s
OK
```

Additional probe: `reject_forbidden_json_fields` currently accepts camelCase forms of several existing forbidden fields: `signingKeyValue`, `certificatePrivateMaterial`, `rawFirmwarePayload`, `rawCrashDump`, `wifiPassword`, and `prusalinkPassword`.

## Critical Issues

### CR-01: Normalized Secret Field Denylist Is Incomplete

**File:** `tools/bazel/phase18_cutover_review.py:190`
**Issue:** The fix added `FORBIDDEN_NORMALIZED_FIELD_NAMES`, but the normalized list is manually maintained and only covers a subset of `FORBIDDEN_FIELD_NAMES`. CamelCase or otherwise normalized forms of already-forbidden fields such as `signingKeyValue`, `certificatePrivateMaterial`, `rawFirmwarePayload`, `rawCrashDump`, `wifiPassword`, and `prusalinkPassword` are not rejected. Because Phase 18 decision inputs and generated artifacts are explicitly redaction-gated, this allows sensitive or payload-bearing fields through the security scan by changing field casing.
**Fix:**

```python
def normalized_field_name(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


FORBIDDEN_NORMALIZED_FIELD_NAMES = {
    normalized_field_name(field_name) for field_name in FORBIDDEN_FIELD_NAMES
} | {
    "authorization",
    "authorizationheader",
}
```

Also extend `test_security_only_rejects_common_api_key_fields` or add a focused test that covers normalized forms for every existing forbidden field, especially signing, certificate, firmware payload, crash dump, and WiFi/PrusaLink password names.

## Warnings

### WR-01: Generated Row-Level Demotion Flags Can Be Tampered Without Detection

**File:** `tools/bazel/phase18_cutover_review.py:1369`
**Issue:** `--security-only` checks generated `normalized-final-demotion-results.json` statuses and top-level `demotion_allowed`, but it does not verify each row's `demotion_status_allows_cutover` value. A generated artifact can leave a row status as `pending` or `blocked`, keep top-level `demotion_allowed` false, but set that row's `demotion_status_allows_cutover` to `true`; the current scan passes. The redacted report says machine-readable gate rows determine final status, so row-level overclaims should be rejected too.
**Fix:**

```python
expected_final_allows = {
    row["id"]: bool(row["demotion_status_allows_cutover"])
    for row in expected_results
}

# In validate_generated_overclaim_guards, after loading each normalized row:
expected_allows = expected_final_allows.get(row_id)
if expected_allows is not None and row.get("demotion_status_allows_cutover") != expected_allows:
    errors.append(f"generated final criterion demotion flag mismatch: {row_id}")

# In the no-decision branch:
if row.get("demotion_status_allows_cutover") is True:
    errors.append(
        "generated no-decision normalized-final-demotion-results.json cannot set "
        f"{row.get('id', 'unknown')} demotion_status_allows_cutover true"
    )
```

Add tests that tamper `demotion_status_allows_cutover` in both no-decision and decision-input generated artifacts and assert `--security-only` rejects them.

---

_Reviewed: 2026-06-20T17:08:39Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
