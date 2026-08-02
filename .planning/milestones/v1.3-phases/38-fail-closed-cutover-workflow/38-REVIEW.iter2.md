---
phase: 38-fail-closed-cutover-workflow
reviewed: 2026-07-26T18:16:56Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json
  - tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json
  - tools/bazel/phase34_final_readiness_demotion_dry_run.py
  - tools/bazel/phase34_final_readiness_demotion_dry_run_test.py
  - tools/bazel/phase35_cutover_decision_artifact.py
  - tools/bazel/phase35_cutover_decision_artifact_test.py
  - tools/bazel/phase38_cutover_workflow.py
  - tools/bazel/phase38_cutover_workflow_integration_test.py
  - tools/bazel/phase38_cutover_workflow_test.py
  - tools/bazel/rust_workflow.sh
findings:
  critical: 3
  warning: 0
  info: 0
  total: 3
status: issues_found
---

# Phase 38: Code Review Report

**Reviewed:** 2026-07-26T18:16:56Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

The Phase 38 implementation adds substantial fail-closed coverage and all focused and real-producer suites pass. Three uncovered authority failures remain: non-JSON text read failures can bypass Phase 34 replacement entirely, the final reducer can advertise positive authority during an operational failure, and the coordinator can return without revoking a prior Phase 35 approval when Phase 34 canonical validation fails.

Verification performed:

- Python bytecode compilation passed for the seven reviewed Python modules.
- `phase34_final_readiness_demotion_dry_run_test.py`: 49 tests passed.
- `phase35_cutover_decision_artifact_test.py`: 74 tests passed.
- `phase38_cutover_workflow_test.py`: 27 tests passed.
- `phase38_cutover_workflow_integration_test.py`: 8 tests passed.
- `bash -n tools/bazel/rust_workflow.sh` passed.
- `git diff --check` passed for the review scope.
- An additional invalid-UTF-8 reproduction returned nonzero with a traceback while the seeded prior Phase 34 packet remained `unblocked`/`approved`.
- An additional invalid-Phase-34 reproduction returned nonzero while the prior Phase 35 `approved` decision remained on disk with no blocking authority guard.

## Critical Issues

### CR-01: Non-JSON read failures bypass the Phase 34 blocked replacement

**File:** `tools/bazel/phase34_final_readiness_demotion_dry_run.py:255-262`

**Issue:** `load_json` converts only `json.JSONDecodeError` into `VerificationError`. Invalid UTF-8 and filesystem read failures such as `UnicodeDecodeError`, `PermissionError`, and other `OSError` subclasses escape `run_quick`'s source-failure publication boundary. The CLI then exits through a traceback without replacing prior Phase 34 authority. A reproduction that wrote invalid UTF-8 to a Phase 31 receipt left the seeded `readiness_state: unblocked`, `cutover_verdict_state: approved`, and `stale-prior-authority.json` intact. Because `_run_phase34` also catches only `phase34.VerificationError`, the same exception can abort the Phase 38 coordinator before Phase 35 finalization.

**Fix:**

```python
def load_json(
    root: Path,
    relative_path: Path,
    field: str | None = None,
) -> dict[str, Any]:
    full_path = root / relative_path
    try:
        if not full_path.is_file():
            raise FileNotFoundError(relative_path.as_posix())
        value = json.loads(full_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError) as error:
        raise VerificationError(
            f"{field or relative_path.as_posix()} is unreadable or invalid JSON"
        ) from error
    if not isinstance(value, dict):
        raise VerificationError(
            f"{field or relative_path.as_posix()} must contain a top-level object"
        )
    return value
```

Add invalid-UTF-8 and injected read-error regressions for Phase 31 receipts/manifests and Phase 33 handoff/register inputs. Each test should seed prior approval and assert that the exact blocked Phase 34 bundle is installed before the nonzero return.

### CR-02: Nonzero workflow results can still advertise positive authority

**File:** `tools/bazel/phase38_cutover_workflow.py:138-155`

**Issue:** `production_cutover_planning` and `reference_demotion_authorized` are computed solely from the supplied authority before producer statuses are evaluated. Calling the reducer with a nonzero Phase 34 result and an otherwise consistent approved authority produces `status: 7` together with `final_authority_available: true`, `production_cutover_planning: true`, and `reference_demotion_authorized: true`. These are explicit authority booleans, so a downstream consumer can observe authorization from a workflow that reports an operational failure. The existing nonzero-status test uses only a blocked authority and misses this state.

**Fix:**

```python
operations_succeeded = (
    phase34_outcome.status == 0
    and phase35_outcome.status == 0
)
production_cutover_planning = (
    operations_succeeded
    and authority_consistent
    and authority.verdict == "approved"
    and authority.route == "production-cutover-planning"
)
reference_demotion_authorized = (
    operations_succeeded
    and authority_consistent
    and authority.readiness_state == "unblocked"
    and authority.demotion_validation_state == "valid"
    and authority.demotion_decision_state == "approve"
    and authority.demotion_gate_state == "open"
)
```

Also add truth-table tests for approved/open authority combined with each nonzero producer outcome. Positive authority fields must be false whenever the overall operation failed.

### CR-03: Invalid Phase 34 authority leaves prior Phase 35 approval unguarded

**File:** `tools/bazel/phase38_cutover_workflow.py:347-358`

**Issue:** When Phase 34 does not leave a valid canonical bundle, the coordinator returns immediately without running Phase 35 and without publishing the Phase 35 blocking guard. A prior `approved` Phase 35 decision and `production-cutover-planning` route therefore remain on the public authority surface. A reproduction using a symlinked Phase 34 output returned `phase34-authority-invalid`, but the seeded Phase 35 approved decision survived and `.phase35-authority-guard.json` was absent. This violates the phase requirement that the workflow cannot exit while prior Phase 34 or Phase 35 approval remains authoritative.

**Fix:** Publish and validate the Phase 35 blocking authority guard before starting Phase 34. Leave it in force through every Phase 34 failure and allow only a successfully validated Phase 35 staged installation to clear it. Alternatively, the invalid-Phase-34 branch must install a validated blocked Phase 35 source-failure bundle before returning. Add a regression that seeds a real approved Phase 35 bundle, forces Phase 34 publication/canonical validation failure, and proves either a validated blocked Phase 35 replacement exists or the durable guard blocks the restored prior bundle.

***

_Reviewed: 2026-07-26T18:16:56Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
