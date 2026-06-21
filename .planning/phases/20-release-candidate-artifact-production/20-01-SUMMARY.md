---
phase: 20-release-candidate-artifact-production
plan: 01
subsystem: release-engineering
tags: [bazel, release-candidate, signing, provenance, verifier, redaction]

requires:
  - phase: 17-release-candidate-artifact-and-signing-gates
    provides: Phase 17 release artifact surface vocabulary, signing/provenance evidence shape, and mismatch classification vocabulary.
  - phase: 19-aggregate-cutover-evidence-ci
    provides: CI evidence retention pattern and pending external release-input boundary.
provides:
  - Phase 20 release artifact contract covering REL-01, REL-02, and REL-03 rows.
  - Source-backed release-environment input template using pending template-only evidence rows.
  - Stdlib verifier/result writer for contract, security, quick, and approved release-input validation.
  - Regression tests for no-overclaim, redaction, path, and comparison metadata behavior.
affects: [phase20-release-candidate-artifact-production, phase21-final-readiness-result-consumption]

tech-stack:
  added: []
  patterns:
    - Stdlib-only Python verifier with pure validation helpers and confined generated evidence writes.
    - Release proof classes separate local/template evidence from approved release evidence.

key-files:
  created:
    - tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json
    - tools/bazel/manifests/phase20_release_environment_inputs.template.json
    - tools/bazel/phase20_release_candidate_artifacts.py
    - tools/bazel/phase20_release_candidate_artifacts_test.py
  modified: []

key-decisions:
  - "Phase 20 Plan 01 keeps release rows pending in quick mode unless approved release input is supplied."
  - "Release refs are limited to external://phase20/... or repo-relative build/ci-evidence/phase20 paths."
  - "Private key, credential, token, password, raw payload, and crash-dump field names are rejected at the release input boundary."

patterns-established:
  - "Phase 20 quick artifacts write release-result-manifest.json as the release status source for downstream Phase 21 consumption."
  - "Comparison evidence requires mismatch_class, mismatch_reason, owner_phase, affected_artifact_surface, and residual_risk."

requirements-completed: [REL-01, REL-02, REL-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 20-2026-06-21T12-40-17
generated_at: 2026-06-21T13:33:38Z

duration: 12 min
completed: 2026-06-21
---

# Phase 20 Plan 01: Release Candidate Artifact Production Summary

**Phase 20 release artifact contract and verifier that write pending quick evidence while rejecting smoke, template-only, secret-bearing, path-escaping, or underclassified release proof**

## Performance

- **Duration:** 12 min
- **Started:** 2026-06-21T13:21:45Z
- **Completed:** 2026-06-21T13:33:38Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added the Phase 20 release artifact contract with REL-01, REL-02, and REL-03 row coverage, exact Phase 17 artifact output vocabulary, proof classes, statuses, and mismatch classes.
- Added a release-environment input template whose rows stay `template-only` and `pending-release-input` until release managers supply approved metadata.
- Added a stdlib Python verifier/result writer with `--contract-only`, `--security-only`, `--quick`, `--release-input`, and `--output-dir`.
- Added regression tests for required surfaces, pending quick output, proof-class overclaim rejection, redaction, ref confinement, and comparison metadata.

## Task Commits

1. **Task 1: Write RED Phase 20 contract and verifier tests** - `dcb90b50c` (test)
2. **Task 2: Implement Phase 20 contract, input template, verifier, and result writer** - `42e0f59ce` (feat)

## Files Created/Modified

- `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` - Phase 20 contract for release artifact rows, proof classes, statuses, signing/provenance/retention metadata, and comparison metadata.
- `tools/bazel/manifests/phase20_release_environment_inputs.template.json` - Release-environment input template with `external://phase20/` refs and pending template-only rows.
- `tools/bazel/phase20_release_candidate_artifacts.py` - Contract/security verifier, approved release-input validator, path/redaction guard, and quick artifact writer.
- `tools/bazel/phase20_release_candidate_artifacts_test.py` - TDD regression tests for contract completeness, no-overclaim behavior, redaction, path guards, and comparison classification requirements.

## Decisions Made

- Quick mode intentionally does not mark any release row `passed` without validated release input.
- `external://phase20/` is the only external ref scheme accepted by Phase 20 release evidence; local refs must stay under `build/ci-evidence/phase20/`.
- Release comparison metadata is mandatory for passed rows and restricted to `pass`, `intentional-delta`, `blocker`, and `deferred-retained-code-issue`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The first GREEN implementation returned a generic redaction marker name for forbidden release-input fields. The verifier now reports the exact rejected field, and the regression tests pass.

## Known Stubs

None. The empty strings and empty arrays in `phase20_release_environment_inputs.template.json` are intentional pending release-environment inputs; the verifier rejects them as passed proof.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for `20-02-PLAN.md`, which owns Bazel/root/just wiring and the non-empty release identity target. Phase 21 can later consume `build/ci-evidence/phase20/release-result-manifest.json`.

## Verification

Passed:

- `python3 tools/bazel/phase20_release_candidate_artifacts_test.py`
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only`
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --security-only`
- `python3 tools/bazel/phase20_release_candidate_artifacts.py --quick`
- `rg -n '"release_inputs_supplied": false' build/ci-evidence/phase20/release-result-manifest.json`
- `rg -n '"status": "passed"' build/ci-evidence/phase20/release-result-manifest.json` returned no matches after quick mode without release input.
- `cargo fmt --all` passed before task commits.
- `cargo clippy --all-targets --all-features -- -D warnings` passed before task commits.
- `cargo build --all-targets --all-features` passed before task commits.
- `cargo test --all-features` passed before task commits.

## Self-Check: PASSED

- Found `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`.
- Found `tools/bazel/manifests/phase20_release_environment_inputs.template.json`.
- Found `tools/bazel/phase20_release_candidate_artifacts.py`.
- Found `tools/bazel/phase20_release_candidate_artifacts_test.py`.
- Found task commit `dcb90b50c`.
- Found task commit `42e0f59ce`.

---
*Phase: 20-release-candidate-artifact-production*
*Completed: 2026-06-21*
