---
phase: 40-file-length-refactoring
plan: 05
subsystem: evidence-tooling
tags: [python, bazel, evidence-contracts, file-lengths, redaction, signing]
requires:
  - phase: 40-04
    provides: Stable Phase 5-11 verifier façades and phase-local policy modules
provides:
  - Stable Phase 13-17 evidence CLI façades over phase-local policy and artifact modules
  - Interface and failure-domain suites behind unchanged Bazel labels
  - Preserved evidence schemas, status vocabularies, redaction, signing, provenance, artifacts, diagnostics, and exits
  - Eight retired evidence-tool exceptions with 69 temporary paths remaining
affects: [40-06, evidence-tooling, bazel-runfiles, file-length-verification]
tech-stack:
  added: []
  patterns:
    - stable evidence entrypoint façade over phase-local policy
    - phase-local release-input and artifact-publication boundaries
    - stable test entrypoint combining interface and failure-domain suites
key-files:
  created:
    - tools/bazel/phase13_evidence_policy.py
    - tools/bazel/phase14_evidence_policy.py
    - tools/bazel/phase15_evidence_policy.py
    - tools/bazel/phase15_hardware_evidence_failure_test.py
    - tools/bazel/phase16_evidence_policy.py
    - tools/bazel/phase16_live_network_evidence_failure_test.py
    - tools/bazel/phase17_evidence_policy.py
    - tools/bazel/phase17_release_evidence_policy.py
    - tools/bazel/phase17_evidence_artifacts.py
    - tools/bazel/phase17_release_candidate_evidence_failure_test.py
  modified:
    - .bright-builds-rules-checks.tsv
    - tools/bazel/BUILD.bazel
    - tools/bazel/phase13_ci_evidence.py
    - tools/bazel/phase14_simulator_evidence.py
    - tools/bazel/phase15_hardware_evidence.py
    - tools/bazel/phase16_live_network_evidence.py
    - tools/bazel/phase17_release_candidate_evidence.py
key-decisions:
  - "Each Phase 13-17 evidence script keeps its original filename and Bazel label as the public CLI and artifact façade."
  - "Security, signing, provenance, and release-input rules remain phase-local; no shared cross-phase evidence framework was introduced."
  - "Phase 17 separates core contract policy, release-input policy, and artifact publication so each trust-boundary module stays below 629 lines."
patterns-established:
  - "Split evidence policy by lifecycle responsibility while preserving the original orchestration entrypoint."
  - "Retire temporary exceptions only in the green commit that places every involved original and helper file below 629 lines."
requirements-completed: [D-05, D-06, D-08, D-09, D-11, D-12, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T20:01:59Z
duration: 27m
completed: 2026-07-27
---

# Phase 40 Plan 05: Phase 13-17 Evidence Contract Refactoring Summary

Stable Phase 13-17 evidence entrypoints now front phase-local validation, failure, and publication modules while retaining exact security-sensitive contracts and retiring all eight campaign exceptions.

## Performance

- **Duration:** 27 minutes
- **Started:** 2026-07-27T19:35:14Z
- **Completed:** 2026-07-27T20:01:59Z
- **Tasks:** 2
- **Files modified:** 22

## Accomplishments

- Reduced every campaign-owned Phase 13-17 evidence producer and test entrypoint, plus every new helper, below 629 physical lines.
- Preserved CLI help, exit status, stdout/stderr, artifact trees, JSON schemas, status vocabularies, redaction behavior, signing/provenance requirements, and stable Bazel labels.
- Split Phase 15-17 failure coverage behind the original test entrypoints without dropping negative protocol, secret, overclaim, output-containment, signing, or publication cases.
- Removed exactly four temporary ledger rows per task, leaving Phase 40 at 838 permanent and 69 temporary exceptions with zero findings.

## Task Commits

1. **Task 1: Refactor Phase 13-15 evidence contracts** - `8ea0eecc6`
2. **Task 2: Refactor Phase 16-17 evidence contracts** - `0c7f52fb5`

## Files Created/Modified

- `tools/bazel/phase13_evidence_policy.py` and `tools/bazel/phase13_ci_evidence.py` - CI evidence policy behind the stable Phase 13 CLI.
- `tools/bazel/phase14_evidence_policy.py` and `tools/bazel/phase14_simulator_evidence.py` - simulator evidence policy behind the stable Phase 14 CLI.
- `tools/bazel/phase15_evidence_policy.py`, `tools/bazel/phase15_hardware_evidence.py`, and `tools/bazel/phase15_hardware_evidence_failure_test.py` - hardware policy, façade, and split failure coverage.
- `tools/bazel/phase16_evidence_policy.py`, `tools/bazel/phase16_live_network_evidence.py`, and `tools/bazel/phase16_live_network_evidence_failure_test.py` - live-network contract policy, orchestration, and redaction/failure suite.
- `tools/bazel/phase17_evidence_policy.py`, `tools/bazel/phase17_release_evidence_policy.py`, `tools/bazel/phase17_evidence_artifacts.py`, and `tools/bazel/phase17_release_candidate_evidence.py` - release contract, input/signing/provenance, artifact-publication, and stable CLI layers.
- `tools/bazel/phase17_release_candidate_evidence_failure_test.py` - failure, security, wiring, and publication-boundary coverage loaded by the original test entrypoint.
- `tools/bazel/BUILD.bazel` - added every extracted policy, artifact helper, and failure suite to the existing public runfiles.
- `.bright-builds-rules-checks.tsv` - removed all eight completed Phase 13-17 campaign exceptions.

## Decisions Made

- Original evidence scripts remain the public orchestration and CLI façades so direct invocations, diagnostics, artifact paths, and Bazel labels stay stable.
- Phase 17 uses distinct phase-local modules for core contract policy, release evidence validation, and artifact publication because those responsibilities have different trust boundaries.
- Failure suites are loaded by the existing test entrypoints, so callers continue to execute the same public test labels.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated isolated evidence fixtures for extracted policy imports**

- **Found during:** Tasks 1 and 2
- **Issue:** Phase 13-17 tests create temporary repositories containing their public verifier scripts, so new sibling imports were unavailable in those roots.
- **Fix:** Copied the appropriate phase-local policies and Phase 17 artifact helper into each isolated root and added all new modules to the existing Bazel runfiles.
- **Files modified:** `tools/bazel/phase13_ci_evidence_test.py`, `tools/bazel/phase14_simulator_evidence_test.py`, `tools/bazel/phase15_hardware_evidence_test.py`, `tools/bazel/phase16_live_network_evidence_test.py`, `tools/bazel/phase17_release_candidate_evidence_test.py`, `tools/bazel/BUILD.bazel`
- **Verification:** All Phase 13-17 direct and Bazel-backed evidence suites passed.
- **Committed in:** `8ea0eecc6`, `0c7f52fb5`

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fixture and runfile updates were required to exercise the planned module boundaries; no external behavior or scope changed.

## Issues Encountered

- YAPF expanded several initially compliant raw splits beyond the 628-line maximum. The final design moved security traversal into the Phase 16 façade and separated Phase 17 core policy, release-input policy, and artifact publication by responsibility.
- Archived Phase 13-17 planning artifacts are no longer present under `.planning/phases/`. Temporary symlinks to tracked historical artifacts were used only while running the established verifiers and removed before commits.
- Bazel refreshed `MODULE.bazel.lock` from format version 26 to 28 during verification. Only that unrelated generated drift was restored before each commit.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. The created policy, artifact, and failure modules contain no placeholder or unwired data paths.

## Residual Risks

- This was a structural evidence-tool refactor; it does not create new live-service, hardware, signing-key, or maintainer evidence. Existing non-local classifications remain fail-closed and were exercised through their established contracts.

## Threat Flags

None. The refactor adds no endpoint, authentication path, schema boundary, or new trust-boundary file access; T-40-04 and T-40-05 remain covered by compatibility, failure-domain, redaction, signing, provenance, and full phase-gate tests.

## Verification

- Exact ordered Cargo sequence before every implementation commit: `cargo fmt --all`; `cargo clippy --all-targets --all-features -- -D warnings`; `cargo build --all-targets --all-features`; `cargo test --all-features` - passed.
- `just phase13-verify` through `just phase17-verify` - all verifier targets and 110 focused Python tests passed.
- Representative release-artifact dependencies executed through the Phase 17 Bazel targets; no additional reference command was printed.
- `just phase40-verify` - 14 policy regressions passed; active policy reports 838 permanent, 69 temporary, and 907 total exceptions.
- `bun scripts/bright-builds-check.ts all` - zero findings.
- Pre/post `--help` return code, stdout, and stderr were byte-identical for every Phase 13-17 evidence entrypoint.
- Pre/post artifact structures and bytes matched, excluding only documented generated timestamp fields.
- Targeted `.venv/bin/pre-commit run --files ...` - passed for both tasks.
- Physical line checks - all eight campaign-owned original paths and every new module are below 629 lines.
- Ledger scan - all eight planned Phase 13-17 temporary rows are absent.
- `git diff --check` - passed.

## Self-Check: PASSED

- All 22 implementation, test, runfile, and ledger files and this summary exist.
- Task commits `8ea0eecc6` and `0c7f52fb5` exist in repository history.
- All eight planned temporary exception rows are absent, with the immutable permanent policy boundary unchanged.
