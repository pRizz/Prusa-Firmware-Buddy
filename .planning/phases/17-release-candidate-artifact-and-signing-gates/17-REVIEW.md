---
phase: 17-release-candidate-artifact-and-signing-gates
reviewed: 2026-06-19T15:10:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/manifests/phase17_release_candidate_evidence_contract.json
  - tools/bazel/phase17_release_candidate_evidence.py
  - tools/bazel/phase17_release_candidate_evidence_test.py
  - tools/bazel/rust_workflow.sh
findings:
  critical: 2
  warning: 2
  info: 1
  total: 5
status: issues_found
---

# Phase 17: Code Review Report

**Reviewed:** 2026-06-19T15:10:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the Phase 17 Bazel/just wiring, release evidence contract, verifier, tests, and Rust workflow dispatch. Material guidance came from `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` (no active override), and `standards/core/{architecture,code-shape,testing,verification}.md`; no project-local skills were present.

The main risks are release-gate false positives: the release-candidate artifact label is currently backed by local representative smoke artifacts, and release evidence statuses are not constrained to each contract row's allowed statuses. I ran `python3 tools/bazel/phase17_release_candidate_evidence_test.py`; all 13 existing tests passed, but they do not cover the false-positive cases below.

## Critical Issues

### CR-01: Release Candidate Target Wraps Local Smoke Artifacts

**File:** `tools/bazel/BUILD.bazel:377`
**Issue:** `phase17_release_candidate_artifacts` points directly at `:representative_release_artifacts`, while the contract and verifier treat `//tools/bazel:phase17_release_candidate_artifacts` as the release-run-required identity. The local-smoke guard only rejects direct labels such as `//tools/bazel:representative_release_artifacts`, so the wrapper can make representative smoke output look like the approved release artifact surface.
**Fix:**
```starlark
filegroup(
    name = "phase17_representative_release_smoke",
    srcs = [":representative_release_artifacts"],
)

# Point this only at real release-candidate outputs, not smoke fixtures.
filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = [":real_release_candidate_artifacts"],
)
```

Until a real release target exists, keep smoke behind `phase17_representative_release_smoke` and have the verifier reject `//tools/bazel:phase17_release_candidate_artifacts` as release proof when it resolves to smoke dependencies.

### CR-02: Release Evidence Can Use Disallowed Success-Like Statuses

**File:** `tools/bazel/phase17_release_candidate_evidence.py:637`
**Issue:** `validate_release_row_against_contract` reads `result` but never checks it against `STATUS_VOCABULARY` or the matched contract row's `allowed_statuses`. Because passed-proof checks only run for `result == "passed"`, release evidence for a release-run-required row can use `source-contract-passed` and bypass the approved-release evidence type and non-empty ref requirements; the generated normalized output then records that status for a release artifact row.
**Fix:**
```python
result = require_string(row, "result", row_name)
allowed_statuses = set(require_list_of_strings(contract_row, "allowed_statuses", str(contract_row["id"])))
if result not in STATUS_VOCABULARY:
    errors.append(f"{row_name} uses unsupported result: {result}")
elif result not in allowed_statuses:
    errors.append(f"{row_name} result {result} is not allowed for {contract_row['id']}")
```

Also validate each contract row's `default_status` against its own `allowed_statuses` in `validate_row_shape`, and add a regression test using a release-run row with `result: "source-contract-passed"`.

## Warnings

### WR-01: Wiring Checks Can Pass on Unrelated Text

**File:** `tools/bazel/phase17_release_candidate_evidence.py:844`
**Issue:** `check_wiring` uses raw substring checks across entire files. A comment, an unrelated Bazel rule, or a command outside the `phase17-verify` recipe can satisfy the verifier even when the actual target or just recipe is miswired.
**Fix:** Scope the checks to parsed structures. For example, extract the `phase17-verify` recipe body before checking command order, and inspect the specific `phase17_verify` / `phase17_verify_tests` rule blocks rather than searching the whole BUILD file. Add negative tests where required strings appear only in comments or unrelated recipes.

### WR-02: Source Ref Resolution Is Too Broad

**File:** `tools/bazel/phase17_release_candidate_evidence.py:343`
**Issue:** `resolve_source_ref` allows any repo-relative JSON file and `row_id_exists` accepts the first matching nested `id` anywhere in the document. That can falsely satisfy traceability with a self-reference, a wrong manifest, or an unrelated nested object that happens to reuse the same ID.
**Fix:**
```python
allowed_ref_paths = {Path(path) for path in SOURCE_REF_MANIFESTS}
if relative_path not in allowed_ref_paths:
    raise VerificationError(f"{row_name} source ref path is not an approved Phase 17 source manifest: {source_ref}")
```

Then resolve IDs through known manifest row collections, or require exactly one matching row in the intended collection instead of recursively accepting any nested `id`.

## Info

### IN-01: Verifier File Exceeds Code-Shape Refactor Trigger

**File:** `tools/bazel/phase17_release_candidate_evidence.py:1`
**Issue:** The verifier is 941 lines and mixes contract validation, release-evidence validation, artifact writing, security scanning, and wiring checks. Bright Builds code-shape guidance treats files over roughly 628 lines as a refactor trigger, and this concentration is already hiding the status and wiring validation gaps above.
**Fix:** Split into focused modules or sections such as contract schema validation, release input validation, artifact emission, redaction scanning, and wiring validation, with tests grouped around each boundary.

---

_Reviewed: 2026-06-19T15:10:00Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
