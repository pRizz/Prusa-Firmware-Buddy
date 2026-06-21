---
phase: 20-release-candidate-artifact-production
reviewed: 2026-06-21T14:13:13Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - tools/bazel/phase17_release_candidate_evidence.py
  - tools/bazel/phase17_release_candidate_evidence_test.py
  - tools/bazel/phase20_release_candidate_artifacts.py
  - tools/bazel/phase20_release_candidate_artifacts_test.py
  - tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json
  - tools/bazel/manifests/phase20_release_environment_inputs.template.json
findings:
  critical: 1
  warning: 0
  info: 0
  total: 1
status: issues_found
---

# Phase 20: Code Review Report

**Reviewed:** 2026-06-21T14:13:13Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Re-reviewed the Phase 20 release artifact verifier, Phase 17 compatibility guard changes, Bazel/just wiring, tests, and Phase 20 manifest templates after the CR-01/WR-01 fix report. Repo guidance applied: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, and `standards/core/testing.md`.

The previous findings were materially addressed: contract source refs now resolve against approved row collections, and passed release rows now require the contract-declared release/signing/provenance/retention metadata. The targeted verifier and test commands pass.

One remaining release-evidence correctness gap remains: Phase 20 can still produce `passed` rows without substantive comparison metadata.

## Critical Issues

### CR-01: Passed Rows Can Still Overclaim Comparison Evidence

**File:** `tools/bazel/phase20_release_candidate_artifacts.py:453,556-558`

**Issue:** `validate_row` accepts `default_status == "passed"` because it only checks the status vocabulary, so a contract edit can make `--quick` emit a passed row without release input. Separately, `validate_release_row` only checks that comparison metadata keys exist for passed rows; empty `mismatch_reason`, empty `residual_risk`, wrong `owner_phase`, and wrong `affected_artifact_surface` are accepted. Temporary probes confirmed both paths exit 0 and write passed artifacts.

**Fix:**
```python
if default_status == "passed":
    errors.append(f"{row_name} default_status cannot be passed without approved release input")

for field in contract_row["comparison_metadata_required"]:
    value = require_string(row, field, row_name)
    if field == "owner_phase" and value != PHASE:
        errors.append(f"{row_name} owner_phase must be {PHASE}")
    if field == "affected_artifact_surface" and value != contract_row["artifact_surface"]:
        errors.append(f"{row_name} affected_artifact_surface must match contract row {contract_row['id']}")
```

Add regression tests that `--contract-only` rejects a Phase 20 row with `default_status: "passed"`, and that `--quick --release-input` rejects passed rows with empty comparison strings or mismatched `owner_phase` / `affected_artifact_surface`.

## Verification

- `python3 -m py_compile tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py tools/bazel/phase20_release_candidate_artifacts.py tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --security-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --quick` passed.
- Negative probes confirmed the remaining issue.

---

_Reviewed: 2026-06-21T14:13:13Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
