---
phase: 19-aggregate-cutover-evidence-ci
reviewed: 2026-06-21T01:33:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - tools/bazel/phase19_aggregate_ci_evidence.py
  - tools/bazel/phase19_aggregate_ci_evidence_test.py
  - tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json
  - .github/workflows/ci-evidence.yml
  - tools/bazel/BUILD.bazel
  - BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - justfile
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 19: Code Review Report

**Reviewed:** 2026-06-21T01:33:00Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the Phase 19 aggregate CI evidence verifier, manifest contract, unit tests, GitHub Actions workflow, Bazel wrappers, shell dispatch, and just entrypoint. This review was informed by `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/index.md`, and the Bright Builds verification, code-shape, and testing pages. No project skills were present under `.claude/skills/` or `.agents/skills/`.

The CI wiring is thin and permission-scoped, and external evidence rows remain pending instead of passing without inputs. The main risks are in artifact-retention semantics and path hardening: the aggregator can mark retention passed without checking the contract's required artifacts, and the output path guard is lexical only before destructive writes.

## Warnings

### WR-01: Artifact Retention Can Pass Without Required Phase Artifacts

**File:** `tools/bazel/phase19_aggregate_ci_evidence.py:584`
**Issue:** The contract lists `expected_artifacts` for each source phase, but the aggregate writer does not enforce that list. `check_contract()` only checks that the list is non-empty, while `write_ci_evidence()` copies whatever files exist in the quick output directory and marks the `*-artifact-retention` row as `passed` whenever `copy_artifact_tree()` returns no copy failures. An existing but empty or incomplete `build/ci-evidence/phaseNN` directory would therefore produce a passed retention row and contribute requirement coverage even if `run-manifest.json` or the redacted summary is missing. The test only asserts that the destination phase directories exist (`tools/bazel/phase19_aggregate_ci_evidence_test.py:72`), so this semantic gap is not covered.
**Fix:**
```python
expected_artifacts = require_list_of_strings(phase, "expected_artifacts", owning_phase)
missing_artifacts = [
    artifact
    for artifact in expected_artifacts
    if not (root / quick_output_dir / artifact).is_file()
]
if missing_artifacts:
    copy_failures.extend(
        f"missing expected source artifact: {(quick_output_dir / artifact).as_posix()}"
        for artifact in missing_artifacts
    )
```
Add a negative test fixture where a source phase quick directory exists but omits one expected artifact, and assert that `--ci` exits nonzero and marks the retention row failed.

### WR-02: Output Path Guard Does Not Prevent Symlink Escapes

**File:** `tools/bazel/phase19_aggregate_ci_evidence.py:527`
**Issue:** `require_repo_relative_under()` rejects absolute paths and `..`, but it only performs a lexical `relative_to()` check. `write_ci_evidence()` then immediately calls `shutil.rmtree(output_root)` and creates directories under `output_root`. If an existing workspace contains a symlinked parent such as `build` or `build/ci-evidence`, the verifier can delete or write outside the repository while still passing the lexical guard. This matters because the script is CI-facing and handles artifact retention paths.
**Fix:**
```python
def require_safe_output_dir(root: Path, path_value: str | Path, row_name: str) -> Path:
    relative_path = require_repo_relative_under(path_value, DEFAULT_OUTPUT_DIR, row_name)
    intended_root = root.resolve() / DEFAULT_OUTPUT_DIR
    resolved_path = (root / relative_path).resolve()
    try:
        resolved_path.relative_to(intended_root)
    except ValueError as error:
        raise VerificationError(f"{row_name} resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}") from error
    return relative_path
```
Use this resolved check before any `rmtree()`, `mkdir()`, or artifact copy, and add a test that a symlinked `build/ci-evidence` parent is rejected.

## Info

### IN-01: Remove Dead Snapshot Source Extension

**File:** `tools/bazel/phase19_aggregate_ci_evidence.py:546`
**Issue:** `snapshot_sources.extend(... for phase in [])` is a permanent no-op. It looks like leftover scaffolding and makes the manifest snapshot setup harder to audit.
**Fix:** Delete the line, or replace it with a real source list if another snapshot class is intended.

---

_Reviewed: 2026-06-21T01:33:00Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
