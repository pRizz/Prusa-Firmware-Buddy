---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T16:02:08Z
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

**Reviewed:** 2026-06-20T16:02:08Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the listed Phase 18 verifier, contract manifest, tests, Bazel wiring, shell workflow, and just recipe after fixes `6c06a052a` and `7dd3060e3`. This review used the repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and Bright Builds architecture, code-shape, verification, and testing standards. No project-local skills were present under `.claude/skills/` or `.agents/skills/`.

The previously reported critical issues are fixed: decision inputs now require the Phase 18 lifecycle envelope, and allowed final demotion statuses now require matching decision/evidence/exception metadata. The repo-native Phase 18 verification passes. Two remaining validation gaps can still accept malformed maintainer input and should be fixed before relying on the generated demotion result.

Verification performed:

- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.
- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 30 tests.
- `just phase18-verify` passed, including Bazel-backed tests and quick artifact generation.
- Targeted temp-root probes reproduced both warnings below.

## Warnings

### WR-01: Deferred retained-code exceptions can pass without evidence

**File:** `tools/bazel/phase18_cutover_review.py:845`
**Issue:** `validate_retained_review` requires `supplied_evidence_result_refs` only for `accepted` retained-packet reviews. A review with `status: "deferred-approved-exception"`, an `exception_ref`, and a blocker action can leave `supplied_evidence_result_refs` empty. Because `write_quick_artifacts` treats `deferred-approved-exception` as an allowed retained packet status, a complete final approval payload can still write `demotion_allowed=true` with no packet evidence for that exception.
**Fix:**
```python
if status in {"accepted", "deferred-approved-exception"}:
    require_non_empty_refs(supplied_refs, row_name, "supplied_evidence_result_refs")

if status == "deferred-approved-exception":
    if row["exception_ref"] == "none" or row["blocker_or_deferred_action"] == "none":
        raise VerificationError(f"{row_name} deferred-approved-exception requires exception_ref and blocker action")
```
Add a regression test where one retained review is `deferred-approved-exception` with empty evidence and all final criteria otherwise pass; the verifier should reject it.

### WR-02: Exception metadata fields are not type-checked

**File:** `tools/bazel/phase18_cutover_review.py:770`
**Issue:** `validate_exception_metadata` checks that exception fields are present and that `evidence_refs` is a list of strings, but it does not require the other exception fields to be non-empty strings. A decision input can mark all final criteria `exception-approved` with values such as lists, numbers, booleans, or objects in `scope`, `rationale`, `approver`, and related fields, and the verifier still writes `demotion_allowed=true`.
**Fix:**
```python
def validate_exception_metadata(exception: Any, row_name: str) -> dict[str, Any]:
    if not isinstance(exception, dict):
        raise VerificationError(f"{row_name} exception must be an object")
    require_fields(exception, EXCEPTION_REQUIRED_FIELDS, f"{row_name} exception")
    for field in EXCEPTION_REQUIRED_FIELDS:
        if field == "evidence_refs":
            continue
        require_string(exception, field, f"{row_name} exception")
    evidence_refs = require_list_of_strings(exception, "evidence_refs", f"{row_name} exception")
    require_non_empty_refs(evidence_refs, f"{row_name} exception", "evidence_refs")
    for ref in evidence_refs:
        require_phase18_artifact_ref(ref, f"{row_name} exception evidence_refs")
    return exception
```
Add a regression test that sets an `exception-approved` final decision with non-string exception metadata and expects rejection.

---

_Reviewed: 2026-06-20T16:02:08Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
