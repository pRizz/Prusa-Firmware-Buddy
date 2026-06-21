---
phase: 20-release-candidate-artifact-production
reviewed: 2026-06-21T14:26:59Z
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

**Reviewed:** 2026-06-21T14:26:59Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Final re-review of the Phase 20 release artifact verifier, Phase 17 compatibility guard, Bazel/just wiring, regression tests, and Phase 20 manifests after the latest review-fix pass. Repo guidance applied: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, and `standards/core/testing.md`.

The previous passed-row overclaim finding is fixed: passed defaults are rejected, passed rows require approved proof classes, contract-declared release/signing/provenance/retention metadata, non-empty comparison metadata, Phase 20 ownership, and matching affected artifact surfaces.

One remaining security issue remains in custom output directory containment.

## Critical Issues

### CR-01: Relative Output Directory Can Escape Through Symlinks

**File:** `tools/bazel/phase20_release_candidate_artifacts.py:285`

**Issue:** `resolved_output_dir()` resolves and containment-checks absolute `--output-dir` paths, but the relative-path branch only performs lexical checks before returning `root / output_dir`. A relative path such as `build/ci-evidence/phase20/link/escaped`, where `link` is a symlink inside the allowed tree, resolves outside the repo without error. `write_quick_artifacts()` then calls `shutil.rmtree(full_output_dir)` before writing artifacts, so a crafted relative output path can delete and write outside the intended evidence root.

**Fix:**
```python
def resolved_output_dir(root: Path, output_dir: Path) -> tuple[Path, Path]:
    resolved_root = root.resolve(strict=False)
    expected_root = (resolved_root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
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
        relative_output_dir = full_output_dir.relative_to(resolved_root)
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        ) from error
    return relative_output_dir, full_output_dir
```

Add a regression test that creates `build/ci-evidence/phase20/link` as a symlink to a temporary outside directory, runs `--quick --output-dir build/ci-evidence/phase20/link/escaped`, and asserts the verifier fails without creating or deleting the outside target.

## Verification

- `python3 -m py_compile tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py tools/bazel/phase20_release_candidate_artifacts.py tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --security-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --quick` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence.py --contract-only` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence.py --security-only` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence.py --quick` passed.
- `git diff --check` passed.
- Negative symlink probe confirmed the remaining `--output-dir` escape.

---

_Reviewed: 2026-06-21T14:26:59Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
