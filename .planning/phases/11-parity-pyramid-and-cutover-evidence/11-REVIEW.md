---
phase: 11-parity-pyramid-and-cutover-evidence
reviewed: 2026-06-14T21:45:06Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - tools/bazel/phase11_verify.py
  - tools/bazel/phase11_verify_test.py
  - tools/bazel/manifests/phase11_parity_pyramid.json
  - tools/bazel/manifests/phase11_requirement_evidence.json
  - tools/bazel/manifests/phase11_reference_comparisons.json
  - tools/bazel/manifests/phase11_cutover_readiness.json
  - tools/bazel/manifests/phase11_retained_code_justifications.json
  - rust/crates/domain/src/cutover.rs
  - rust/crates/domain/src/lib.rs
findings:
  critical: 0
  warning: 4
  info: 0
  total: 4
status: issues_found
---

# Phase 11: Code Review Report

**Reviewed:** 2026-06-14T21:45:06Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Re-reviewed the Phase 11 Bazel wiring, just facade, verifier, verifier tests, evidence manifests, and Rust cutover domain contract after the WR-01 through WR-05 fixes. The earlier five warnings are addressed, and the current local verifier/test surface passes. The remaining findings are verifier/evidence gaps that can still allow malformed or stale cutover evidence to pass.

Review context included repo `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, the installed `gsd-code-review` and `bright-builds-rules` skill instructions, and the pinned Bright Builds architecture, code-shape, verification, testing, and Rust standards.

Verification run during review:

- `python3 tools/bazel/phase11_verify.py --quick` passed.
- `python3 tools/bazel/phase11_verify.py --wiring-only` passed.
- `python3 tools/bazel/phase11_verify_test.py` passed, 26 tests.
- `python3 -m json.tool` passed for all five Phase 11 manifests.
- `cargo test --all-features -p buddy-domain` passed, 89 tests.
- `cargo clippy -p buddy-domain --all-targets --all-features -- -D warnings` passed.
- `bash -n tools/bazel/rust_workflow.sh` passed.

## Warnings

### WR-01: Security Scan Misses Phase 11 Context And Research Docs

**File:** `tools/bazel/phase11_verify.py:774`
**Issue:** `existing_security_paths()` scans Phase 11 manifests, `11-VALIDATION.md`, and `11-*-SUMMARY.md`, but it skips `11-CONTEXT.md` and `11-RESEARCH.md`. Those files are cited as source artifacts by the reviewed manifests, so a secret marker or overclaim can be added there while `python3 tools/bazel/phase11_verify.py --security-only` still passes. I verified this with a temp fixture containing `token_value` in `11-CONTEXT.md`; the security check returned success.
**Fix:**
```python
phase_doc_patterns = [
    "11-CONTEXT.md",
    "11-RESEARCH.md",
    "11-VALIDATION.md",
    "11-*-SUMMARY.md",
]
for pattern in phase_doc_patterns:
    paths.extend(path.relative_to(root) for path in sorted(phase_dir.glob(pattern)))
```
Add a regression test that writes a forbidden marker to `11-CONTEXT.md` or `11-RESEARCH.md` and expects `--security-only` to fail.

### WR-02: Non-Local Evidence Rows Can Omit Their Required Evidence List

**File:** `tools/bazel/phase11_verify.py:356`
**Issue:** `check_pyramid()` and `check_comparisons()` allow `required_non_local_evidence` to be empty, and `check_requirements()` only checks that field for a subset of pending requirement IDs. That lets simulator, CI, hardware, manual, or retained-code rows pass without naming the non-local evidence gate they are supposed to preserve. I verified temp fixtures where a simulator pyramid row and a CI comparison row had `required_non_local_evidence: []`; both checks returned success.
**Fix:**
```python
def require_required_non_local_evidence(
    row: dict[str, object],
    row_name: str,
    proof_scope: str,
) -> None:
    if proof_scope in NON_LOCAL_PROOF_SCOPES:
        require_non_empty_list_of_strings(row, "required_non_local_evidence", row_name)
        return
    require_list_of_strings(row, "required_non_local_evidence", row_name)
```
Call this helper after `proof_scope` validation in `check_pyramid()`, `check_requirements()`, and `check_comparisons()`, and add negative tests for non-local rows with empty evidence lists.

### WR-03: Cutover Evidence Lists Accept Non-String Values

**File:** `tools/bazel/phase11_verify.py:719`
**Issue:** `check_cutover()` uses `require_fields()` for `required_evidence` and `verifier_commands`, which only rejects missing or empty values. It does not verify that these fields are lists of strings. A manifest can set `required_evidence` to `[123]` in `cutover_criteria` or `retained_code_justifications` and `--cutover-only` still passes, leaving malformed machine-readable evidence in the cutover contract.
**Fix:**
```python
require_non_empty_list_of_strings(row, "verifier_commands", row_name)
require_non_empty_list_of_strings(row, "required_evidence", row_name)
```
Apply the `required_evidence` check to retained-code rows as well, and add negative tests for non-string list entries.

### WR-04: Phase 11 Manifests Still Contain Stale Plan-Prerequisite Statuses

**File:** `tools/bazel/manifests/phase11_parity_pyramid.json:77`
**Issue:** The pyramid still reports `requires-plan-11-03-reference-comparison-rows` and `requires-plan-11-04-retained-code-review` even though the reference-comparison and retained-code manifests now exist and are wired. `phase11_requirement_evidence.json:254` also says retained-code acceptance rows are "not created yet." These stale values can mislead downstream cutover consumers into treating completed evidence rows as missing plan prerequisites instead of source-backed rows that remain blocked only by non-local/maintainer evidence.
**Fix:** Update those statuses/blockers to describe the current state, for example `reference-comparisons-source-backed-pending-non-local-evidence` and `retained-code-justifications-source-backed-pending-maintainer-acceptance`. Extend the verifier's stale-marker check to reject `requires-plan-11-03`, `requires-plan-11-04`, and "not created yet" once the later Phase 11 manifests exist.

---

_Reviewed: 2026-06-14T21:45:06Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
