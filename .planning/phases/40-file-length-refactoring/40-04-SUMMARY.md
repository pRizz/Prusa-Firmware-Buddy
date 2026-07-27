---
phase: 40-file-length-refactoring
plan: 04
subsystem: verifier-tooling
tags: [python, bazel, verifier-contracts, file-lengths, redaction]
requires:
  - phase: 40-03
    provides: Stable developer-utility façades and shrink-aware Phase 40 verification
provides:
  - Stable Phase 5-11 verifier façades over phase-local contract-policy modules
  - Interface and failure-domain verifier suites behind unchanged Bazel labels
  - Preserved manifests, diagnostics, proof-locality checks, redaction checks, and exit behavior
  - Twelve retired verifier exceptions with 77 temporary paths remaining
affects: [40-05, verifier-tooling, bazel-runfiles, file-length-verification]
tech-stack:
  added: []
  patterns:
    - stable verifier entrypoint façade over phase-local contract policy
    - stable test entrypoint combining interface and failure-domain suites
    - explicit policy-module runfiles for production and isolated test roots
key-files:
  created:
    - tools/bazel/phase5_runtime_policy.py
    - tools/bazel/phase6_contract_policy.py
    - tools/bazel/phase7_contract_policy.py
    - tools/bazel/phase7_verify_failure_test.py
    - tools/bazel/phase8_contract_policy.py
    - tools/bazel/phase8_verify_failure_test.py
    - tools/bazel/phase9_contract_policy.py
    - tools/bazel/phase9_verify_failure_test.py
    - tools/bazel/phase10_contract_policy.py
    - tools/bazel/phase10_verify_failure_test.py
    - tools/bazel/phase11_contract_policy.py
    - tools/bazel/phase11_verify_failure_test.py
  modified:
    - .bright-builds-rules-checks.tsv
    - tools/bazel/BUILD.bazel
    - tools/bazel/phase5_verify.py
    - tools/bazel/phase11_verify.py
key-decisions:
  - "Each Phase 5-11 verifier keeps its existing script and Bazel label as the public façade; extracted policy remains phase-local."
  - "Oversized verifier tests keep their existing entrypoint while loading a sibling failure-domain suite, preserving the public test label."
  - "Isolated verifier test roots copy the extracted policy module explicitly so direct-script imports remain representative of Bazel runfiles."
patterns-established:
  - "Extract verifier data validation without introducing a shared cross-phase evidence framework."
  - "Retire each temporary exception only in the green commit that places its original path below 629 lines."
requirements-completed: [D-05, D-06, D-08, D-09, D-11, D-12, D-15]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T19:31:05Z
duration: 23m
completed: 2026-07-27
---

# Phase 40 Plan 04: Phase 5-11 Verifier Contract Refactoring Summary

Stable Phase 5-11 verifier entrypoints now front phase-local contract and failure modules, preserving Bazel/CLI behavior while retiring all twelve campaign exceptions.

## Performance

- **Duration:** 23 minutes
- **Started:** 2026-07-27T19:07:52Z
- **Completed:** 2026-07-27T19:31:05Z
- **Tasks:** 3
- **Files modified:** 27

## Accomplishments

- Reduced every campaign-owned Phase 5-11 verifier and test entrypoint below 629 lines without changing its public filename or Bazel label.
- Extracted seven phase-local policy modules and five failure-domain suites; no cross-phase evidence framework or numbered chunk module was introduced.
- Preserved verifier modes, manifests, proof-scope checks, redaction diagnostics, CLI help bytes, and fail-closed test coverage.
- Removed exactly four temporary ledger rows per task, leaving Phase 40 at 838 permanent and 77 temporary exceptions with zero findings.

## Task Commits

1. **Task 1: Refactor Phase 5-7 verifier contracts** - `bd0d97fa0`
2. **Task 2: Refactor Phase 8-9 verifier contracts** - `db50fcb03`
3. **Task 3: Refactor Phase 10-11 verifier contracts** - `5aded82e2`

## Files Created/Modified

- `tools/bazel/phase5_runtime_policy.py` and `tools/bazel/phase5_verify.py` - Phase 5 runtime-boundary policy behind the stable verifier.
- `tools/bazel/phase6_contract_policy.py`, `tools/bazel/phase6_verify.py`, and `tools/bazel/phase6_verify_test.py` - Phase 6 contract policy plus isolated-root coverage.
- `tools/bazel/phase7_contract_policy.py`, `tools/bazel/phase7_verify.py`, `tools/bazel/phase7_verify_test.py`, and `tools/bazel/phase7_verify_failure_test.py` - Phase 7 policy and split interface/failure tests.
- `tools/bazel/phase8_contract_policy.py`, `tools/bazel/phase8_verify.py`, `tools/bazel/phase8_verify_test.py`, and `tools/bazel/phase8_verify_failure_test.py` - Phase 8 policy and split GUI workflow tests.
- `tools/bazel/phase9_contract_policy.py`, `tools/bazel/phase9_verify.py`, `tools/bazel/phase9_verify_test.py`, and `tools/bazel/phase9_verify_failure_test.py` - Phase 9 policy and split network/redaction tests.
- `tools/bazel/phase10_contract_policy.py`, `tools/bazel/phase10_verify.py`, `tools/bazel/phase10_verify_test.py`, and `tools/bazel/phase10_verify_failure_test.py` - Phase 10 auxiliary-controller policy and split tests.
- `tools/bazel/phase11_contract_policy.py`, `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`, and `tools/bazel/phase11_verify_failure_test.py` - Phase 11 cutover policy and split tests.
- `tools/bazel/BUILD.bazel` - Added every extracted policy and failure suite to the existing public runfiles.
- `.bright-builds-rules-checks.tsv` - Removed all twelve completed Phase 5-11 campaign exceptions.

## Decisions Made

- Original verifier scripts remain the orchestration and CLI façades so direct invocations and Bazel labels stay stable.
- Policy modules are phase-local even where validation shapes resemble another phase; this keeps deletion tests and threat boundaries explicit.
- Failure suites are loaded by the existing test entrypoints, so callers continue to execute the same public test labels.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated the Phase 6 isolated verifier fixture for the extracted policy**

- **Found during:** Task 1 (Refactor Phase 5-7 verifier contracts)
- **Issue:** `phase6_verify_test.py` creates a temporary repository containing the verifier, so the new sibling policy import was unavailable there.
- **Fix:** Copied `phase6_contract_policy.py` into the isolated root and updated its fixture wiring.
- **Files modified:** `tools/bazel/phase6_verify_test.py`
- **Verification:** All 11 Phase 6 verifier tests and `just phase6-verify` passed.
- **Committed in:** `bd0d97fa0`

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fixture-only change was required to exercise the planned module boundary; no production behavior or scope changed.

## Issues Encountered

- Archived Phase 1 and Phase 5-11 planning artifacts are no longer present under `.planning/phases/`. Temporary symlinks to the tracked milestone archive were used only while running the historical verifiers and removed before commits.
- Bazel refreshed `MODULE.bazel.lock` from format version 26 to 28 during verification. Only that unrelated generated drift was restored before each commit.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. The created policy and failure modules contain no placeholder or unwired data paths.

## Residual Risks

- This was a structural verifier refactor; it does not create new hardware evidence. Existing simulator, hardware, and maintainer evidence classifications remain fail-closed and were exercised through their established verifier contracts.

## Threat Flags

None. The refactor adds no endpoint, authentication path, schema boundary, or new trust-boundary file access; T-40-04 and T-40-05 remain covered by compatibility, failure-domain, redaction, and full phase-gate tests.

## Verification

- Exact ordered Cargo sequence before every task commit: `cargo fmt --all`; `cargo clippy --all-targets --all-features -- -D warnings`; `cargo build --all-targets --all-features`; `cargo test --all-features` - passed.
- `just phase5-verify` through `just phase11-verify` - all verifier targets and 101 focused Python tests passed, including the existing Phase 9 negative fixture suite.
- `just phase40-verify` - 14 policy regressions passed; active policy reports 838 permanent, 77 temporary, and 915 total exceptions.
- `bun scripts/bright-builds-check.ts all` - zero findings.
- Pre/post `--help` return code, stdout, and stderr were byte-identical for every Phase 5-11 verifier.
- Targeted `.venv/bin/pre-commit run --files ...` - passed for all three tasks.
- Physical line checks - all twelve campaign-owned original paths, the updated Phase 6 fixture, and every new module are below 629 lines.
- Ledger scan - all twelve planned Phase 5-11 temporary rows are absent.
- `git diff --check` - passed.

## Self-Check: PASSED

- All 27 implementation, test, runfile, and ledger files and this summary exist.
- Task commits `bd0d97fa0`, `db50fcb03`, and `5aded82e2` exist in repository history.
- All twelve planned temporary exception rows are absent, with the immutable permanent policy boundary unchanged.
