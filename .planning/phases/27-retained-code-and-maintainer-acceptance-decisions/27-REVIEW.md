---
phase: 27-retained-code-and-maintainer-acceptance-decisions
reviewed: 2026-06-25T02:33:34Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json
  - tools/bazel/phase27_retained_code_acceptance_decisions.py
  - tools/bazel/phase27_retained_code_acceptance_decisions_test.py
  - tools/bazel/rust_workflow.sh
findings:
  critical: 0
  warning: 5
  info: 0
  total: 5
status: issues_found
---

# Phase 27: Code Review Report

**Reviewed:** 2026-06-25T02:33:34Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the Phase 27 Bazel/just/shell wiring, contract manifest, verifier, and unit tests. This review was informed by `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the Bright Builds architecture, code-shape, verification, and testing standards.

The wiring is present and the current Phase 27 unit suite passes, but the verifier accepts several malformed maintainer/evidence inputs that can produce acceptance artifacts inconsistent with the canonical Phase 18 and Phase 26 contracts.

Verification performed during review:

- `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` passed: 19 tests.
- Targeted reproductions confirmed that stale lifecycle IDs, inconsistent final decision/status pairs, wrong retained packet roles, empty evidence refs, and invalid timestamps currently pass `--quick`.

## Warnings

### WR-01: Phase 26 Row Identity Is Not Revalidated Against Phase 18

**File:** `tools/bazel/phase27_retained_code_acceptance_decisions.py:467`
**Issue:** `load_phase26_upstream_rows` verifies that required fields exist and that the `criterion_id` sequence matches Phase 18, but it does not compare per-row identity fields back to the canonical requirement. A row with `source_lifecycle_id: "stale-phase-lifecycle"` and `source_lifecycle_status: "current"` passes and produces a `passed` final readiness row with no `lifecycle-mismatch` hard failure. That undermines the Phase 27 hard-blocker policy because stale Phase 26 evidence can be treated as current.
**Fix:**
```python
requirement_by_id = {
    require_string(requirement, "criterion_id", "Phase 18 upstream requirement"): requirement
    for requirement in phase18_upstream_requirements(phase18_contract)
}
for index, row in enumerate(rows):
    # ...existing required-field checks...
    criterion_id = require_string(row, "criterion_id", row_name)
    requirement = requirement_by_id[criterion_id]
    if row.get("evidence_family") != requirement.get("evidence_family"):
        errors.append(f"{row_name} evidence_family must match Phase 18")
    if row.get("owning_phase") != requirement.get("source_phase"):
        errors.append(f"{row_name} owning_phase must match Phase 18")
    if row.get("source_lifecycle_id") != requirement.get("source_lifecycle_id"):
        errors.append(f"{row_name} source_lifecycle_id must match Phase 18")
```

Add a regression test that mutates a Phase 26 row's `source_lifecycle_id` while leaving `source_lifecycle_status` as `current` and expects `--quick` to fail or hard-block the row.

### WR-02: Maintainer Input Phase Metadata Is Ignored

**File:** `tools/bazel/phase27_retained_code_acceptance_decisions.py:549`
**Issue:** `load_maintainer_input` only checks that the file is a JSON object. It never validates `schema_version`, `phase`, `phase_lifecycle_id`, or `reference_demotion_decision`, even though the generated template includes those fields and the contract fixes the Phase 27 lifecycle ID. A stale or wrong-phase maintainer input can be accepted as current Phase 27 approval evidence.
**Fix:**
```python
def load_maintainer_input(root: Path, maybe_path: str | None) -> dict[str, Any] | None:
    # ...existing load and redaction checks...
    expected = {
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
    }
    errors = [
        f"--maintainer-input {field} must be {value!r}"
        for field, value in expected.items()
        if data.get(field) != value
    ]
    demotion = require_dict(data, "reference_demotion_decision", "--maintainer-input")
    if demotion.get("demotion_authorization") != "blocked":
        errors.append("reference_demotion_decision demotion_authorization must stay blocked")
    if demotion.get("phase27_may_authorize_demotion") is not False:
        errors.append("reference_demotion_decision phase27_may_authorize_demotion must be false")
    if errors:
        raise VerificationError("\n".join(errors))
    return data
```

Add a test that changes `phase_lifecycle_id` to a stale value and expects rejection.

### WR-03: Final Decision Status And Decision Can Contradict Each Other

**File:** `tools/bazel/phase27_retained_code_acceptance_decisions.py:886`
**Issue:** `normalize_final_decisions` checks `decision` and `status` independently against global vocabularies, then derives `maintainer_decision` from `decision` while preserving many supplied statuses. As a result, `decision: "reject", status: "passed"` emits a row with `status: "passed"` and `maintainer_decision: "rejected"`, while `decision: "approve", status: "failed"` emits `maintainer_decision: "accepted"`. These contradictory artifacts can corrupt final readiness summaries and status counts.
**Fix:**
```python
if status == "passed" and decision != "approve":
    raise VerificationError(f"{row_name} status passed requires decision approve")
if status in {"exception-approved", "not-applicable"} and decision != "exception":
    raise VerificationError(f"{row_name} status {status} requires decision exception")
if decision == "approve" and status != "passed":
    raise VerificationError(f"{row_name} approve requires status passed")
if decision == "reject" and status in {"passed", "exception-approved", "not-applicable"}:
    raise VerificationError(f"{row_name} reject cannot use accepting status {status}")
```

Add tests for `reject` + `passed` and `approve` + `failed`.

### WR-04: Accepted Decisions Can Omit Evidence Refs And Use Invalid Timestamps

**File:** `tools/bazel/phase27_retained_code_acceptance_decisions.py:669`
**Issue:** `validate_decision_common` only requires `decision_timestamp` to be a non-empty string and `evidence_refs` to be a list of non-empty strings. It accepts `decision_timestamp: "not-a-timestamp"` and `evidence_refs: []`; accepted retained packets and passed final readiness rows are then written with no evidence references or auditable timestamp. Phase 18 validates ISO UTC timestamps and requires non-empty refs for accepting statuses.
**Fix:**
```python
def require_iso_utc(value: str, row_name: str) -> None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        raise VerificationError(f"{row_name} decision_timestamp must be ISO UTC")

def validate_decision_common(..., require_evidence_refs: bool = False) -> None:
    # ...existing field checks...
    require_iso_utc(require_string(row, "decision_timestamp", row_name), row_name)
    evidence_refs = require_string_list(row, "evidence_refs", row_name)
    if require_evidence_refs and not evidence_refs:
        raise VerificationError(f"{row_name} evidence_refs must not be empty")
```

Call it with `require_evidence_refs=True` for accepted retained decisions, passed final decisions, and approved exceptions.

### WR-05: Retained Packet Approver Roles Are Not Enforced

**File:** `tools/bazel/phase27_retained_code_acceptance_decisions.py:740`
**Issue:** Retained packet decisions only pass through `validate_sensitive_role`, which enforces a subset of safety/release/network token policies. The canonical packet `approver_role` from Phase 18 is not checked. For example, `packet-freertos-runtime` expects `runtime-maintainer`, but `approver_role: "cutover-maintainer"` passes and the packet is emitted as accepted.
**Fix:**
```python
packet = packet_by_id[packet_id]
expected_role = require_string(packet, "approver_role", f"Phase 18 retained packet {packet_id}")
approver_role = require_string(row, "approver_role", row_name)
if approver_role != expected_role:
    raise VerificationError(f"{row_name} approver_role must be {expected_role}")
validate_sensitive_role(
    contract,
    subject_text(packet_id, packet.get("title"), packet.get("taxonomy_tags"), exception_surface),
    approver_role,
    row_name,
)
```

Add a regression test that changes a non-sensitive retained packet role away from the packet's `approver_role` and expects rejection.

---

_Reviewed: 2026-06-25T02:33:34Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
