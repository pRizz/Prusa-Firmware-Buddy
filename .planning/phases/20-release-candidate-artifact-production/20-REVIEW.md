---
phase: 20-release-candidate-artifact-production
reviewed: 2026-06-21T14:38:45Z
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
  critical: 2
  warning: 0
  info: 0
  total: 2
status: issues_found
---

# Phase 20: Code Review Report

**Reviewed:** 2026-06-21T14:38:45Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Final re-review of the Phase 20 release artifact verifier, Phase 17 compatibility guard, Bazel/just wiring, regression tests, and Phase 20 manifests after the output-directory containment fix. Repo guidance applied: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, and `standards/core/testing.md`.

The previously reported relative symlink-under-output-root escape is covered by the new Phase 20 regression test. However, both Phase 20 and Phase 17 still resolve the allowed output root itself before containment. If `build/ci-evidence/phase20` or `build/ci-evidence/phase17` is a symlink to another directory, the verifier can delete and replace that target before failing, or in Phase 17's case succeed.

## Critical Issues

### CR-01: Phase 20 Output Root Symlink Can Delete In-Repo Targets

**File:** `tools/bazel/phase20_release_candidate_artifacts.py:285`

**Issue:** `resolved_output_dir()` resolves `DEFAULT_OUTPUT_DIR` into `expected_root` before checking containment. If `build/ci-evidence/phase20` itself is a symlink to another in-repo directory, `full_output_dir.relative_to(expected_root)` passes because both paths resolve to the symlink target. `write_quick_artifacts()` then calls `shutil.rmtree(full_output_dir)` at line 689 and replaces the target before `check_security()` rejects the generated `output_dir` ref. A negative probe confirmed the marker file in the symlink target was deleted.

**Fix:**
```python
def resolved_output_dir(root: Path, output_dir: Path) -> tuple[Path, Path]:
    resolved_root = root.resolve(strict=False)
    expected_root = resolved_root / DEFAULT_OUTPUT_DIR
    if output_dir.is_absolute():
        candidate = output_dir
    else:
        if ".." in output_dir.parts:
            raise VerificationError(
                f"--output-dir must be contained by {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
            )
        candidate = resolved_root / output_dir
    full_output_dir = candidate.resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
        relative_output_dir = full_output_dir.relative_to(resolved_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        ) from error
    return relative_output_dir, full_output_dir
```

Add a regression test where `build/ci-evidence/phase20` is a symlink to a temporary in-repo victim directory, run `--quick`, and assert the verifier fails before deleting or writing into the victim.

### CR-02: Phase 17 Output Root Symlink Can Delete In-Repo Targets

**File:** `tools/bazel/phase17_release_candidate_evidence.py:313`

**Issue:** `contained_output_dir()` has the same root-symlink problem: it resolves `(root / DEFAULT_OUTPUT_DIR)` into `expected_root` and only checks `full_output_dir.relative_to(expected_root)`. If `build/ci-evidence/phase17` is a symlink to another directory, `write_quick_artifacts()` deletes that target at line 794 and writes Phase 17 artifacts there. A negative probe confirmed the marker file was deleted and the verifier still exited successfully.

**Fix:**
```python
def contained_output_dir(root: Path, output_dir: str | Path) -> Path:
    relative_path = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    resolved_root = root.resolve(strict=False)
    expected_root = resolved_root / DEFAULT_OUTPUT_DIR
    full_output_dir = (resolved_root / relative_path).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_path.as_posix()}") from error
    return full_output_dir
```

Add the matching Phase 17 regression test for a symlinked `build/ci-evidence/phase17` root and assert the marker survives.

## Verification

- `rg` quick-pattern scan found no hardcoded secrets, dangerous functions, debug artifacts, empty catches, or TODO/FIXME markers in the reviewed files.
- `python3 -m py_compile tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py tools/bazel/phase20_release_candidate_artifacts.py tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --security-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence.py --contract-only` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence.py --security-only` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` passed.
- `git diff --check` passed.
- Negative output-root symlink probes confirmed CR-01 and CR-02.

---

_Reviewed: 2026-06-21T14:38:45Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
