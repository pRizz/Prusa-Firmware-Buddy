---
phase: 20-release-candidate-artifact-production
reviewed: 2026-06-21T13:59:48Z
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
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 20: Code Review Report

**Reviewed:** 2026-06-21T13:59:48Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the Phase 20 release artifact verifier, Bazel/just wiring, Phase 17 compatibility guard changes, tests, and release manifest templates. Repo guidance applied: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, and `standards/core/testing.md`.

The Bazel and just wiring is coherent, and the targeted verifier/test commands pass. Two release-evidence correctness gaps remain: one allows `passed` release rows without contract-declared release/signing metadata, and one allows broken source traceability refs to pass contract validation.

## Critical Issues

### CR-01: Passed Release Input Can Omit Contract-Required Release And Signing Metadata

**File:** `tools/bazel/phase20_release_candidate_artifacts.py:499`

**Issue:** `validate_release_row` only enforces `REQUIRED_PASS_FIELDS` and comparison metadata for `status == "passed"`. It does not enforce the per-row metadata declared in the contract under `release_metadata_required`, `signing_metadata_required`, `provenance_metadata_required`, and `retention_metadata_required`. A temporary probe with every row marked `passed` but with no `release_run_id`, `operator`, `timestamp`, `signing_mode`, or `key_identity_ref` exited 0 and wrote a passed manifest. That lets Phase 20 overclaim approved release/signing evidence.

**Fix:**
```python
def validate_required_metadata(row: dict[str, Any], contract_row: dict[str, Any], row_name: str, errors: list[str]) -> None:
    metadata_fields = [
        *contract_row["release_metadata_required"],
        *contract_row["signing_metadata_required"],
        *contract_row["provenance_metadata_required"],
        *contract_row["retention_metadata_required"],
    ]
    for field in metadata_fields:
        try:
            if field in {"artifact_refs", "retention_refs"}:
                validate_ref_list(row, field, row_name, require_nonempty=True)
            elif field == "subject_digests":
                validate_subject_digests(row, row_name, errors)
            else:
                require_string(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))
```

Call this inside the `status == "passed"` branch, preserve the accepted metadata in `quick_result_row`/summaries as needed by Phase 21, and add regression tests that passed rows fail when each contract-declared metadata field is missing.

## Warnings

### WR-01: Contract Source References Are Not Resolved

**File:** `tools/bazel/phase20_release_candidate_artifacts.py:370`

**Issue:** Phase 20 contract validation checks that `source_contract_refs` is a list of non-empty strings, but it never verifies that each `file#row-id` points to an approved manifest and an existing row. A temporary probe changed the first row to `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json#does-not-exist`; `--contract-only` still passed. This weakens the release traceability claim.

**Fix:** Port the Phase 17 source-ref resolver pattern into Phase 20: keep an approved manifest path to row-collection map, require repo-relative `file#row-id` refs, load the referenced JSON, and fail unless the row ID exists exactly once in an approved collection. Add a regression test that a nonexistent source row fails `--contract-only`.

---

_Reviewed: 2026-06-21T13:59:48Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
