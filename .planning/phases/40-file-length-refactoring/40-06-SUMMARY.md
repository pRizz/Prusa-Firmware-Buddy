---
phase: 40-file-length-refactoring
plan: 06
subsystem: evidence-tooling
tags: [python, bazel, cutover, release, readiness, file-lengths]
requires:
  - phase: 40-05
    provides: Stable Phase 13-17 evidence façades and phase-local policy modules
provides:
  - Stable Phase 18-28 cutover, release, execution, decision, and readiness CLIs over phase-local modules
  - Interface, failure-domain, security, wiring, and fixture-support suites behind unchanged public test entrypoints
  - Preserved fail-closed schemas, status vocabularies, redaction, approval, demotion, artifact, diagnostic, and exit behavior
  - Sixteen retired Phase 18-28 file-length exceptions with 53 temporary paths remaining
affects: [phase31-38-python, evidence-tooling, bazel-runfiles, file-length-verification]
tech-stack:
  added: []
  patterns:
    - stable phase CLI façade over phase-local contract, policy, security, and publication modules
    - phase-local test entrypoint combining interface and failure-domain suites
    - approval and reference-demotion policy retained as distinct fail-closed responsibilities
key-files:
  created:
    - tools/bazel/phase18_cutover_contract.py
    - tools/bazel/phase18_cutover_policy.py
    - tools/bazel/phase18_cutover_validation.py
    - tools/bazel/phase20_artifact_contract.py
    - tools/bazel/phase22_metadata_policy.py
    - tools/bazel/phase23_execution_policy.py
    - tools/bazel/phase24_execution_policy.py
    - tools/bazel/phase25_execution_policy.py
    - tools/bazel/phase26_release_policy.py
    - tools/bazel/phase27_decision_policy.py
    - tools/bazel/phase28_readiness_policy.py
  modified:
    - .bright-builds-rules-checks.tsv
    - tools/bazel/BUILD.bazel
    - tools/bazel/phase18_cutover_review.py
    - tools/bazel/phase20_release_candidate_artifacts.py
    - tools/bazel/phase22_metadata_reconciliation.py
    - tools/bazel/phase24_hardware_media_safety_evidence_execution.py
    - tools/bazel/phase26_release_signing_upstream_evidence.py
    - tools/bazel/phase27_retained_code_acceptance_decisions.py
    - tools/bazel/phase28_final_readiness_packet.py
key-decisions:
  - "Each Phase 18-28 public script and Bazel label remains the stable CLI or test façade over phase-prefixed modules."
  - "Contract, policy, security, normalization, publication, and test-support seams stay phase-local; no cross-phase evidence framework was introduced."
  - "Final readiness and explicit reference-demotion authorization remain separate fail-closed predicates."
patterns-established:
  - "Split oversized evidence tools by lifecycle responsibility while preserving the original entrypoint and output contract."
  - "Retire ledger exceptions only in the task commit that passes phase gates and places every original and helper below 629 lines."
requirements-completed: [D-05, D-06, D-08, D-09, D-11, D-12, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T20:47:25Z
duration: 40m
completed: 2026-07-27
---

# Phase 40 Plan 06: Phase 18-28 Cutover and Readiness Refactoring Summary

Stable Phase 18-28 evidence entrypoints now front cohesive phase-local contract, policy, security, and publication modules while retaining fail-closed behavior and retiring all sixteen campaign exceptions.

## Performance

- **Duration:** 40 minutes
- **Started:** 2026-07-27T20:07:01Z
- **Completed:** 2026-07-27T20:47:25Z
- **Tasks:** 3
- **Files modified:** 60

## Accomplishments

- Reduced all sixteen campaign-owned Phase 18-28 production and test entrypoints, plus every new phase-prefixed helper, below 629 physical lines.
- Preserved public CLIs, Bazel labels, schemas, status vocabularies, redaction, signing/provenance, approval/demotion separation, artifacts, diagnostics, and exit behavior.
- Partitioned interface, failure, security, upstream, wiring, and fixture-support concerns while retaining the original test entrypoints.
- Removed exactly sixteen temporary ledger rows, leaving Phase 40 at 838 permanent and 53 temporary exceptions with zero findings.

## Task Commits

1. **Task 1: Refactor Phase 18-20 cutover and release tools** - `226a9edda`
2. **Task 2: Refactor Phase 22-25 metadata and execution tools** - `7047acd10`
3. **Task 3: Refactor Phase 26-28 release and readiness tools** - `7d53b73e9`

## Files Created/Modified

- `tools/bazel/phase18_cutover_*.py` - contract, source-reference, upstream, decision, security, artifact, and validation seams behind the stable Phase 18 review CLI and test entrypoint.
- `tools/bazel/phase19_aggregate_policy.py` and `tools/bazel/phase19_aggregate_ci_evidence.py` - aggregate evidence policy behind unchanged Phase 19 publication.
- `tools/bazel/phase20_artifact_*.py` and Phase 20 test modules - release contract/policy and failure/wiring suites behind the stable artifact CLI.
- `tools/bazel/phase22_metadata_policy.py` and Phase 22 test modules - metadata reconciliation rules and isolated fixture coverage.
- `tools/bazel/phase23_execution_*.py` through `tools/bazel/phase25_execution_*.py` - phase-specific execution contracts, policy, fixture support, and publication shells.
- `tools/bazel/phase26_release_*.py` and `tools/bazel/phase26_upstream_policy.py` - release-input, signing, upstream-row, contract, publication, and failure responsibilities.
- `tools/bazel/phase27_decision_*.py` - acceptance-decision contract, validation, normalization, and fixture support behind the existing CLI.
- `tools/bazel/phase28_readiness_*.py` - final-readiness contract, demotion policy, and fixture support behind the existing packet publisher.
- `tools/bazel/BUILD.bazel` - declares every extracted phase-local module in the established verifier and test runfiles.
- `.bright-builds-rules-checks.tsv` - removes all sixteen completed Phase 18-28 campaign exceptions.

## Decisions Made

- Original scripts remain the public orchestration and CLI façades so direct invocations, diagnostics, output paths, and Bazel labels stay stable.
- Contract parsing, policy decisions, security scans, normalization, artifact publication, and fixture support are split only where those responsibilities form cohesive phase-local boundaries.
- Phase 28 readiness does not imply reference demotion; demotion still requires its explicit decision input and an unblocked readiness packet.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Closed extracted-module dependency boundaries**

- **Found during:** Tasks 1 and 3
- **Issue:** Initial phase-local splits left a lazy import and the Phase 28 `phase18_canonical_criteria` helper on the wrong side of their new module boundaries, causing focused tests to raise `NameError`.
- **Fix:** Added the required explicit/lazy imports and moved canonical Phase 18 contract interpretation into the Phase 28 contract module that consumes it.
- **Files modified:** `tools/bazel/phase18_cutover_*.py`, `tools/bazel/phase28_readiness_contract.py`, `tools/bazel/phase28_readiness_policy.py`
- **Verification:** Phase 18 passed 60 focused tests; Phase 28 passed 28 focused tests and its complete Bazel gate.
- **Committed in:** `226a9edda`, `7d53b73e9`

**2. [Rule 3 - Blocking] Updated isolated fixtures and Bazel runfiles for phase-local imports**

- **Found during:** Tasks 1-3
- **Issue:** The tests execute copied public scripts inside temporary repositories, where newly extracted sibling modules were otherwise unavailable.
- **Fix:** Copied each phase's complete local dependency closure into isolated fixtures and added the same modules to the existing Bazel runfiles.
- **Files modified:** Phase 18-28 test-support modules and `tools/bazel/BUILD.bazel`
- **Verification:** All 244 direct focused Python tests and all affected Phase 18-28 Bazel verifier/test targets passed.
- **Committed in:** `226a9edda`, `7047acd10`, `7d53b73e9`

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes were required to make the planned phase-local seams executable; public behavior and architectural scope did not change.

## Issues Encountered

- YAPF expanded several raw splits past the physical-line threshold. Additional cohesive contract, security, publication, and fixture-support seams brought every formatted file below 629 lines.
- Archived Phase 18-28 planning artifacts are no longer active under `.planning/phases/`. Exact temporary symlinks to tracked milestone artifacts were used for established Bazel runfiles and removed before each commit.
- Bazel refreshed `MODULE.bazel.lock` from format version 26 to 28 during verification. That unrelated generated drift was restored with a targeted patch before each commit.

## User Setup Required

None - no external service configuration required.

## Known Stubs

- `tools/bazel/phase19_aggregate_ci_evidence.py:254` intentionally publishes explicit external-input placeholders for evidence that cannot be claimed locally.
- `tools/bazel/phase23_execution_policy.py:207` intentionally emits a blocked `quick-placeholder` simulator record during deterministic quick validation.
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py:24` intentionally emits blocked hardware/media placeholders when no physical qualification run is supplied.
- `tools/bazel/phase25_live_service_evidence_execution.py:22` intentionally emits blocked, secret-safe live-service placeholders during quick validation.

These are existing fail-closed evidence contract modes, not unwired implementation paths.

## Residual Risks

- Phase 24 verification exercised its blocked quick mode and policy/failure suite. No physical printer, removable media, or hardware safety qualification was available or claimed by this refactor.
- This structural refactor does not create new simulator, live-service, signing-key, maintainer-approval, or release evidence; existing non-local evidence remains explicitly blocked or classified until supplied by the established workflows.

## Threat Flags

None. The refactor adds no endpoint, authentication path, schema trust boundary, or new file-access surface. T-40-04 through T-40-06 remain covered by exact contract tests, secret/overclaim scans, actual phase gates, and distinct readiness/demotion predicates.

## Verification

- Exact ordered Cargo sequence before every implementation commit: `cargo fmt --all`; `cargo clippy --all-targets --all-features -- -D warnings`; `cargo build --all-targets --all-features`; `cargo test --all-features` - passed.
- `just phase18-verify` through `just phase20-verify` and `just phase22-verify` through `just phase28-verify` - all affected verifier and test targets passed.
- Direct focused Python suites - 244 tests passed across the ten affected phases.
- `bun scripts/bright-builds-check.ts all` - zero findings.
- `just phase40-verify` - policy regressions passed; active policy reports 838 permanent, 53 temporary, and 891 total exceptions with zero findings.
- Pre/post `--help` return code, stdout, and stderr were byte-identical for all ten public Phase 18-28 entrypoints.
- Deterministic Phase 18-20 quick artifacts were byte-compatible; later producer shapes and fail-closed snapshots passed their established contract suites.
- Physical line checks - all sixteen campaign-owned originals and every new phase-local module are below 629 lines.
- Ledger scan - all sixteen planned Phase 18-28 temporary rows are absent.
- `git diff --check` - passed.

## Self-Check: PASSED

- All 60 implementation, test, runfile, and ledger files and this summary exist.
- Task commits `226a9edda`, `7047acd10`, and `7d53b73e9` exist in repository history.
- All sixteen planned temporary exception rows are absent, with the immutable permanent policy boundary unchanged.
