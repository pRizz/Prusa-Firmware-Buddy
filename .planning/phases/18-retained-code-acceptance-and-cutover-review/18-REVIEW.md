---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T15:48:02Z
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
  critical: 2
  warning: 0
  info: 0
  total: 2
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-06-20T15:48:02Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the Phase 18 verifier, manifest, Bazel wiring, shell workflow, just recipe, and tests using the repo-local AGENTS guidance plus Bright Builds architecture, code-shape, verification, and testing standards. The existing Phase 18 unit suite passes, but targeted negative checks show that the final demotion gate can still be unlocked by inconsistent or mis-scoped maintainer input.

## Critical Issues

### CR-01: Final demotion accepts rejected decisions and empty evidence

**File:** `tools/bazel/phase18_cutover_review.py:789`
**Issue:** `validate_final_decision` validates `decision`, `status`, and `evidence_refs` independently, while `final_status_allows_demotion` treats any `status == "passed"` as sufficient. A decision input with every final criterion set to `decision: "reject"`, `status: "passed"`, and `evidence_refs: []` exits successfully and writes `demotion_allowed=true`. That bypasses the Phase 18 evidence and maintainer approval contract.
**Fix:**
```python
def require_non_empty_refs(refs: list[str], row_name: str, field: str) -> None:
    if not refs:
        raise VerificationError(f"{row_name} {field} must include at least one Phase 18 evidence ref")


def validate_final_decision(row: Any, criterion_ids: set[str], row_index: int) -> dict[str, Any]:
    ...
    evidence_refs = require_list_of_strings(row, "evidence_refs", row_name)
    for ref in evidence_refs:
        require_phase18_artifact_ref(ref, f"{row_name} evidence_refs")

    if status == "passed":
        if decision != "approve":
            raise VerificationError(f"{row_name} status passed requires decision approve")
        require_non_empty_refs(evidence_refs, row_name, "evidence_refs")
    elif status in {"exception-approved", "not-applicable"}:
        if decision != "exception":
            raise VerificationError(f"{row_name} status {status} requires decision exception")
        require_non_empty_refs(evidence_refs, row_name, "evidence_refs")
        validate_exception_metadata(row["exception"], row_name)
```
Also make `final_status_allows_demotion` return `False` when no validated decision object is present or when the decision/status pair is inconsistent.

### CR-02: Decision input can omit the Phase 18 lifecycle envelope

**File:** `tools/bazel/phase18_cutover_review.py:752`
**Issue:** `load_decision_input` validates `decision_packet` only when the field is present. A complete approval payload without `decision_packet` still passes `--quick` and writes `demotion_allowed=true`, so stale or mis-scoped approvals are not bound to `phase_lifecycle_id`.
**Fix:**
```python
def load_decision_input(root: Path, maybe_path: str | None) -> dict[str, Any] | None:
    ...
    packet = data.get("decision_packet")
    if not isinstance(packet, dict):
        raise VerificationError("decision_packet must be present and must be an object")
    if packet.get("phase") != PHASE:
        raise VerificationError(f"decision_packet phase must be {PHASE}")
    if packet.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(f"decision_packet phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
```
Add regression tests for missing `decision_packet` and for stale `phase_lifecycle_id` values.

---

_Reviewed: 2026-06-20T15:48:02Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
