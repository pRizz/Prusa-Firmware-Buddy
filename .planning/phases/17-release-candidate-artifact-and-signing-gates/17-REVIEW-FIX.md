---
phase: 17-release-candidate-artifact-and-signing-gates
fixed_at: 2026-06-19T15:26:10Z
review_path: .planning/phases/17-release-candidate-artifact-and-signing-gates/17-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 17: Code Review Fix Report

**Fixed at:** 2026-06-19T15:26:10Z
**Source review:** `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 4
- Fixed: 4
- Skipped: 0

## Fixed Issues

### CR-01: Release Candidate Target Wraps Local Smoke Artifacts

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/BUILD.bazel`, `justfile`, `tools/bazel/phase17_release_candidate_evidence.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`
**Commit:** `e3261c8ae`
**Applied fix:** Split local representative smoke behind `phase17_representative_release_smoke`, left `phase17_release_candidate_artifacts` empty until real release-candidate outputs exist, updated the smoke just recipe to build the smoke target, and added verifier/test coverage rejecting smoke deps under the release target.
**Verification:**
- `python3 -m py_compile tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py` -> passed
- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` -> `Ran 14 tests ... OK`
- `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` -> `Phase 17 release candidate evidence wiring passed`
- `python3 tools/bazel/phase17_release_candidate_evidence.py --quick` -> `Phase 17 release candidate evidence written to build/ci-evidence/phase17`

### CR-02: Release Evidence Can Use Disallowed Success-Like Statuses

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase17_release_candidate_evidence.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`
**Commit:** `7500f8fa0`
**Applied fix:** Validated release evidence `result` values against the global status vocabulary and the matched contract row's `allowed_statuses`; also validated each contract row default status against its allowed statuses. Added regressions for `source-contract-passed` release evidence and unsupported result values.
**Verification:**
- `python3 -m py_compile tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py` -> passed
- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` -> `Ran 15 tests ... OK`
- `python3 tools/bazel/phase17_release_candidate_evidence.py --quick` -> `Phase 17 release candidate evidence written to build/ci-evidence/phase17`

### WR-01: Wiring Checks Can Pass on Unrelated Text

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase17_release_candidate_evidence.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`
**Commit:** `d1163764f`
**Applied fix:** Replaced file-wide substring wiring checks with scoped checks for Bazel rule blocks, root aliases, shell case arms, and just recipes. Added negative tests where required strings appear only in comments, unrelated case arms, or unrelated recipes.
**Verification:**
- `python3 -m py_compile tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py` -> passed
- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` -> `Ran 17 tests ... OK`
- `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` -> `Phase 17 release candidate evidence wiring passed`
- `python3 tools/bazel/phase17_release_candidate_evidence.py --quick` -> `Phase 17 release candidate evidence written to build/ci-evidence/phase17`
- `python3 -m yapf --diff tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py` -> formatter unavailable: `No module named yapf`

### WR-02: Source Ref Resolution Is Too Broad

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase17_release_candidate_evidence.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`
**Commit:** `7b941aa63`
**Applied fix:** Restricted source refs to approved Phase 17 manifests and resolved row IDs only through known top-level row collections, requiring exactly one match. Added regressions for unapproved manifests and nested non-row IDs.
**Verification:**
- `python3 -m py_compile tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py` -> passed
- `python3 tools/bazel/phase17_release_candidate_evidence.py --contract-only` -> `Phase 17 release candidate evidence contract passed`
- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` -> `Ran 19 tests ... OK`
- `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` -> `Phase 17 release candidate evidence wiring passed`
- `python3 tools/bazel/phase17_release_candidate_evidence.py --quick` -> `Phase 17 release candidate evidence written to build/ci-evidence/phase17`

## Skipped Issues

None.

## Verification Notes

- Full repository Rust/Cargo verification was not run because this GSD fixer pass uses per-finding focused verification and the changed paths are Phase 17 Python/Bazel/just wiring.
- The active Python did not have `yapf` installed, so formatter diff mode could not run locally.
- Project context loaded before edits: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and `standards/core/{architecture,code-shape,testing,verification}.md`. No project-local skills or lesson files were present.

---

_Fixed: 2026-06-19T15:26:10Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
