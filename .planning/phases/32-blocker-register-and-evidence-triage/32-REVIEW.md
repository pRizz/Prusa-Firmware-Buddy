---
phase: 32-blocker-register-and-evidence-triage
reviewed: 2026-07-03T15:26:55Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - tools/bazel/manifests/phase32_blocker_register_triage_contract.json
  - tools/bazel/phase32_blocker_register_triage.py
  - tools/bazel/phase32_blocker_register_triage_test.py
findings:
  critical: 0
  warning: 2
  info: 0
  total: 2
status: issues_found
---

# Phase 32: Code Review Report

**Reviewed:** 2026-07-03T15:26:55Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the Phase 32 Bazel/just wiring, contract manifest, Python verifier, and unit tests against the GSD reviewer scope plus repo-local Bright Builds guidance from `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/index.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, and `standards/core/testing.md`.

The wiring and baseline verifier commands pass, but two triage correctness issues can omit or misroute blocker rows in the canonical register.

Verification run during review:

- `python3 -m py_compile tools/bazel/phase32_blocker_register_triage.py tools/bazel/phase32_blocker_register_triage_test.py`
- `python3 tools/bazel/phase32_blocker_register_triage_test.py -q`
- `python3 tools/bazel/phase32_blocker_register_triage.py --contract-only`
- `python3 tools/bazel/phase32_blocker_register_triage.py --wiring-only`
- `python3 tools/bazel/phase32_blocker_register_triage.py --security-only --output-dir build/ci-evidence/phase32`

## Warnings

### WR-01: Stale Lifecycle Source Rows Are Skipped Before Classification

**File:** `tools/bazel/phase32_blocker_register_triage.py:471`

**Issue:** `is_non_blocking_source_row()` treats a consumed source row as non-blocking when `status`, redaction, source-ref, and exception status are clean, but it ignores `source_lifecycle_status`. The classifier does understand `source_lifecycle_status in {"stale", "mismatch", "lifecycle-mismatch"}` as `lifecycle_mismatch`, yet `load_phase31_rows()` skips the row at line 560 before classification runs. A row with `status: "passed"` and `source_lifecycle_status: "stale"` is therefore dropped from `blocker-register.json`, even though the contract marks stale/lifecycle-mismatch evidence as blocker material.

**Fix:**

```python
def is_non_blocking_source_row(signal: dict[str, Any]) -> bool:
    return (
        signal.get("status") == "passed"
        and signal.get("redaction_status", "passed") == "passed"
        and signal.get("source_ref_status", "passed") == "passed"
        and signal.get("source_lifecycle_status", "passed") in {"passed", "", None}
        and signal.get("exception_status", "none") in {"none", "", None}
    )
```

Add a regression test with a Phase 31 accepted receipt consuming a source row whose `status` is `passed` and `source_lifecycle_status` is `stale`; assert the register contains a `lifecycle_mismatch` blocker row.

### WR-02: Phase 27 Exception Rows Lose Their Real Gate

**File:** `tools/bazel/phase32_blocker_register_triage.py:634`

**Issue:** Phase 32 hardcodes Phase 27 exception-register rows as `source_stream="retained-code"` and only passes `item.get("criterion_id")` into the blocker signal. The Phase 27 producer writes exception rows with `row_id` and `row_type`, not `criterion_id`, so final-readiness exception rows fall back to the retained-code default gate (`final-retained-code-acceptance`). That misroutes downstream decision work even though the `source_ref` still contains the original row id.

**Fix:**

```python
row_type = str(item.get("row_type") or "")
source_stream = "retained-code" if row_type == "retained_code_decision" else "readiness"
gate_id = str(item.get("criterion_id") or item.get("row_id") or stable_sha12(item))

rows.append(
    build_blocker_row(
        row_id_prefix="phase27-exception",
        source_stream=source_stream,
        source_ref=f"{exception_path.as_posix()}#{gate_id}",
        signal={
            "status": "exception-requested",
            "exception_status": item.get("exception_state", "exception-requested"),
            "owner": item.get("owner"),
            "criterion_id": gate_id,
            "row_id": gate_id,
            "evidence_refs": [exception_path.as_posix()],
        },
    )
)
```

Update the Phase 32 tests so their Phase 27 exception fixture matches the actual Phase 27 `exception-decision-register.json` shape (`row_type` + `row_id`) and assert that a final-readiness exception keeps its original affected gate.

***

_Reviewed: 2026-07-03T15:26:55Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
