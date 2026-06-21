---
phase: 20-release-candidate-artifact-production
fixed_at: 2026-06-21T14:31:41Z
review_path: .planning/phases/20-release-candidate-artifact-production/20-REVIEW.md
iteration: 3
findings_in_scope: 1
fixed: 1
skipped: 0
status: all_fixed
---

# Phase 20: Code Review Fix Report

**Fixed at:** 2026-06-21T14:31:41Z
**Source review:** .planning/phases/20-release-candidate-artifact-production/20-REVIEW.md
**Iteration:** 3

**Summary:**
- Findings in scope: 1
- Fixed: 1
- Skipped: 0

## Fixed Issues

### CR-01: Relative Output Directory Can Escape Through Symlinks

**Files modified:** `tools/bazel/phase20_release_candidate_artifacts.py`, `tools/bazel/phase20_release_candidate_artifacts_test.py`
**Commit:** 84966c9d3
**Applied fix:** `resolved_output_dir()` now resolves the repo root, expected `build/ci-evidence/phase20` root, and candidate output directory for both absolute and relative inputs before enforcing containment. Added a regression test that routes a relative output path through a symlink under the allowed tree to an outside temporary directory and verifies the run fails before deleting or writing the outside target.

## Verification

- `python3 -m py_compile tools/bazel/phase20_release_candidate_artifacts.py tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --security-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --quick` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only` passed.
- `git diff --check` passed.

## Iteration Notes

Iteration 3 fixes the remaining CR-01 from the current review. Iteration 2 previously fixed the passed-row overclaim finding in commit `8f4b53877`; iteration 1 fixed earlier review findings in commits `9e4e85996` and `a090a1a34`.

---

_Fixed: 2026-06-21T14:31:41Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 3_
