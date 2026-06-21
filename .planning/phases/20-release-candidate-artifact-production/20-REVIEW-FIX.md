---
phase: 20-release-candidate-artifact-production
fixed_at: 2026-06-21T14:42:04Z
review_path: .planning/phases/20-release-candidate-artifact-production/20-REVIEW.md
iteration: 4
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 20: Code Review Fix Report

**Fixed at:** 2026-06-21T14:42:04Z
**Source review:** .planning/phases/20-release-candidate-artifact-production/20-REVIEW.md
**Iteration:** 4

**Summary:**
- Findings in scope: 2
- Fixed: 2
- Skipped: 0

## Fixed Issues

### CR-01: Phase 20 Output Root Symlink Can Delete In-Repo Targets

**Files modified:** `tools/bazel/phase20_release_candidate_artifacts.py`, `tools/bazel/phase20_release_candidate_artifacts_test.py`
**Commit:** 83056ad29
**Applied fix:** `resolved_output_dir()` now keeps the allowed `build/ci-evidence/phase20` root lexical under the resolved repo root while resolving the candidate output path. A checked-in root symlink therefore fails containment before `shutil.rmtree()` can delete the symlink target. Added a regression test that symlinks `build/ci-evidence/phase20` to an in-repo victim directory and verifies the marker file survives.

### CR-02: Phase 17 Output Root Symlink Can Delete In-Repo Targets

**Files modified:** `tools/bazel/phase17_release_candidate_evidence.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`
**Commit:** 83056ad29
**Applied fix:** `contained_output_dir()` now applies the same lexical allowed-root containment for `build/ci-evidence/phase17` while resolving the candidate output path. Added the matching Phase 17 regression test that symlinks the output root to an in-repo victim directory and verifies the marker file survives.

## Verification

- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` passed.
- `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --security-only` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --quick` passed.
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only` passed.
- `git diff --check` passed.

## Iteration Notes

Iteration 4 fixes the two output-root symlink containment findings from the current review. Iteration 3 fixed relative output-dir symlink containment in commit `84966c9d3`. Iteration 2 fixed passed-row overclaiming in commit `8f4b53877`. Iteration 1 fixed earlier metadata and source-ref findings in commits `9e4e85996` and `a090a1a34`.

---

_Fixed: 2026-06-21T14:42:04Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 4_
