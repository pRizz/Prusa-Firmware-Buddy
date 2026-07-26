---
phase: 36-normalize-evidence-and-blocker-rows
plan: "01"
subsystem: evidence-triage
tags: [python, bazel, evidence-intake, blocker-normalization, canonical-identity]
requires:
  - phase: 26-release-signing-and-upstream-result-evidence
    provides: canonical nine-row release and upstream evidence table
  - phase: 27-retained-code-and-maintainer-acceptance-decisions
    provides: retained-code, residual-risk, exception, and readiness decision rows
  - phase: 28-final-readiness-packet-and-demotion-gate
    provides: readiness, residual-risk, and demotion records
  - phase: 31-final-evidence-intake
    provides: accepted-final receipt and provenance authority
provides:
  - atomic Phase 26 table adaptation behind accepted-final Phase 31 receipts
  - immutable five-field canonical blocker source identities and stable row IDs
  - separate exact decision identities across retained-code, residual-risk, exception, readiness, and demotion axes
  - producer-backed Phase 26 through Phase 32 and Phase 27/28 through Phase 32 regression coverage
affects: [phase-37-blocker-reconciliation, phase-38-readiness-verdict]
tech-stack:
  added: []
  patterns:
    - pure producer-shape normalization core behind an imperative evidence shell
    - source-only stable row IDs with separate decision-resolution identities
    - atomic fail-closed table adapters
key-files:
  created:
    - tools/bazel/phase32_blocker_normalization.py
    - tools/bazel/phase32_blocker_normalization_test.py
  modified:
    - tools/bazel/manifests/phase32_blocker_register_triage_contract.json
    - tools/bazel/phase32_blocker_register_triage.py
    - tools/bazel/phase32_blocker_register_triage_test.py
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
key-decisions:
  - "Canonical row IDs derive only from the exact five-field producer source tuple; decision axis and subject remain separate resolution identity."
  - "Phase 26 tables are adapted only through accepted-final Phase 31 release-signing receipts and fail atomically on recognized malformed shapes."
  - "Phase 32 emits identity and triage facts only; producer regressions stop before Phase 34 reconciliation or approval semantics."
patterns-established:
  - "Producer adapter: select by exact stream and artifact kind, validate the complete envelope, then normalize rows."
  - "Fail closed: recognized malformed shapes emit one critical malformed blocker; unsupported shapes or statuses emit visible critical unknown blockers."
requirements-completed: [INTAKE-04, TRIAGE-01, TRIAGE-02]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 36-2026-07-26T00-27-52
generated_at: 2026-07-26T01:43:22Z
duration: 28min
completed: 2026-07-26
---

# Phase 36 Plan 01: Normalize Evidence and Blocker Rows Summary

**Atomic producer adapters and immutable canonical identities now carry real Phase 26-28 evidence into Phase 32 without false release blockers or approval overclaim.**

## Performance

- **Duration:** 28 min
- **Started:** 2026-07-26T01:15:00Z
- **Completed:** 2026-07-26T01:43:22Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Added an atomic Phase 26 upstream table adapter that preserves Phase 31 finality authority, accepts complete all-passed tables without emitting a release blocker, and collapses malformed tables into one critical proof-ineligible signal.
- Replaced mutable-payload hashes with stable source-only row IDs and separate exact decision identities across all five Phase 27/28 decision domains.
- Added focused pure normalization tests plus isolated real-producer tests covering Phase 26 through accepted Phase 31 intake and Phase 27/28 through Phase 32.
- Wired both Phase 32 test modules and their exact producer inputs into Bazel and the `just phase32-verify` workflow.

## Task Commits

Each task was committed atomically:

1. **Task 1: Contract canonical identities and add RED adapter regressions** - `71c28444f` (test)
2. **Task 2: Implement contract-keyed adapters and immutable blocker identities** - `a9194313a` (feat)
3. **Task 3: Exercise real Phase 26-28 producers through the Phase 32 boundary** - `29f65a8c4` (test)

## Files Created/Modified

- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` - Contracts canonical identity fields, closed producer enums, Phase 26 adapter selection, and fail-closed shape policy.
- `tools/bazel/phase32_blocker_normalization.py` - Pure canonical source identity, row ID, decision identity, binding validation, and atomic Phase 26 table adaptation.
- `tools/bazel/phase32_blocker_normalization_test.py` - Focused one-concern adapter and identity regressions.
- `tools/bazel/phase32_blocker_register_triage.py` - Applies producer-specific normalization to Phase 31 receipts and Phase 27/28 decision artifacts.
- `tools/bazel/phase32_blocker_register_triage_test.py` - Preserves existing integration coverage and adds isolated real-producer boundary tests.
- `tools/bazel/BUILD.bazel` - Supplies hermetic Phase 32 test and verifier runfiles.
- `tools/bazel/rust_workflow.sh` - Runs pure normalization tests before Phase 32 integration tests.

## Decisions Made

- Canonical blocker identity is the exact tuple of source domain, producer phase, producer artifact kind, source row kind, and producer-native subject ID. Mutable classification, owner, status, evidence, action, and decision metadata never enter `row_id`.
- Decision resolution uses the separate pair of decision axis and decision subject ID. The same subject on different axes remains distinct, while incompatible remapping of one source tuple is rejected.
- Phase 31 remains the provenance/finality authority. Phase 32 applies the Phase 26 table adapter only after an accepted-final release-signing receipt names the canonical table.
- Unknown envelopes, row kinds, and statuses remain visible critical proof-ineligible blockers; recognized invalid Phase 26 tables fail atomically as one malformed blocker.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The formatter adjusted the expanded Python integration test before commit; the focused and full suites were rerun after formatting.
- Bazel upgraded `MODULE.bazel.lock` metadata during final verification. The generated lockfile-only change was restored because dependency changes were outside Phase 36 scope.

## Known Stubs

None. Empty collections in the normalization code are local accumulators or explicit negative-test inputs, not unwired production data.

## Verification

- `python3 tools/bazel/phase32_blocker_normalization_test.py -q` — 17 passed
- `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` — 18 passed
- `python3 tools/bazel/phase32_blocker_register_triage_test.py Phase32ProducerShapeTest -q` — 2 passed
- `just phase32-verify` — Bazel test and verifier targets passed; Phase 32 wrote 43 fail-closed blocker rows for the default quick evidence chain
- `cargo fmt --all`
- `cargo clippy --all-targets --all-features -- -D warnings`
- `cargo build --all-targets --all-features`
- `cargo test --all-features` — 136 unit tests and all doc tests passed
- `git diff --check`

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 37 can resolve blockers using exact canonical row IDs and separate decision identities without path, stream, prefix, or gate fallback matching.
- Phase 32 still intentionally grants no approval, readiness reconciliation, or reference-demotion authority; those remain downstream responsibilities.

## Self-Check: PASSED

- All seven plan-owned code, contract, test, and workflow files exist.
- Task commits `71c28444f`, `a9194313a`, and `29f65a8c4` exist.
- Full Phase 32 verification and the required Rust pre-commit sequence passed.

*Phase: 36-normalize-evidence-and-blocker-rows*
*Completed: 2026-07-26*
