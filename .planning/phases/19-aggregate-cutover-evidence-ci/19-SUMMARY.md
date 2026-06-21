---
phase: 19-aggregate-cutover-evidence-ci
plan: 01
subsystem: ci-evidence
tags: [bazel, github-actions, python, verifier, cutover-evidence]
requires:
  - phase: 13-ci-evidence-orchestration
    provides: CI evidence workflow and artifact retention pattern
  - phase: 14-simulator-evidence-gates
    provides: simulator evidence verifier and quick artifacts
  - phase: 15-hardware-safety-and-media-qualification
    provides: hardware evidence verifier and operator input boundary
  - phase: 16-live-network-and-transfer-qualification
    provides: live network evidence verifier and operator input boundary
  - phase: 17-release-candidate-artifact-and-signing-gates
    provides: release evidence verifier and signing input boundary
  - phase: 18-retained-code-acceptance-and-cutover-review
    provides: final review verifier and maintainer decision boundary
provides:
  - Phase 19 aggregate CI evidence verifier
  - Phase 19 machine-readable contract manifest
  - Phase 19 Bazel, just, and GitHub Actions entrypoints
  - Phase 14-18 retained artifact aggregation under build/ci-evidence/phase19
affects: [phase20-release-candidate-artifact-production, phase21-final-readiness-result-consumption, phase22-evidence-metadata-reconciliation]
tech-stack:
  added: []
  patterns: [stdlib-python-verifier, bazel-shell-binary-facade, generated-evidence-redaction-scan]
key-files:
  created:
    - tools/bazel/phase19_aggregate_ci_evidence.py
    - tools/bazel/phase19_aggregate_ci_evidence_test.py
    - tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json
  modified:
    - .github/workflows/ci-evidence.yml
    - BUILD.bazel
    - justfile
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
key-decisions:
  - "Phase 19 composes Phase 14-18 quick verifier outputs instead of duplicating their evidence semantics."
  - "External-only simulator, hardware, live-service, release, and maintainer-decision rows remain pending without explicit inputs."
  - "The GitHub Actions workflow now uploads build/ci-evidence/phase19 rather than the Phase 13-only bundle."
patterns-established:
  - "Aggregate evidence manifests retain source phase outputs under phase-artifacts/phaseNN."
  - "External evidence placeholders are first-class manifest rows with pending statuses."
requirements-completed: [CIEV-01, CIEV-02, CIEV-03, SIM-01, SIM-02, HARD-01, HARD-02, HARD-03, LIVE-01, LIVE-02, LIVE-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 19-2026-06-21T01-07-45
generated_at: 2026-06-21T01:26:59.977Z
duration: 18 min
completed: 2026-06-21
---

# Phase 19 Plan 01: Aggregate Cutover Evidence CI Summary

**Phase 19 aggregate CI verifier with retained Phase 14-18 artifacts, pending external-input rows, and Bazel/GitHub Actions facade wiring**

## Performance

- **Duration:** 18 min
- **Started:** 2026-06-21T01:08:00Z
- **Completed:** 2026-06-21T01:26:59Z
- **Tasks:** 4
- **Files modified:** 9

## Accomplishments

- Added `tools/bazel/phase19_aggregate_ci_evidence.py`, which runs Phase 14-18 deterministic modes, captures logs, copies quick artifacts, writes `run-manifest.json`, and emits external evidence placeholders.
- Added `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` with requirement coverage for CIEV, SIM, HARD, and LIVE Phase 19 rows.
- Added `tools/bazel/phase19_aggregate_ci_evidence_test.py` for contract, workflow, manifest shape, artifact retention, and no-overclaim checks.
- Updated `.github/workflows/ci-evidence.yml` so CI uploads `build/ci-evidence/phase19/`.
- Added Bazel, `rust_workflow.sh`, and `just phase19-verify` entrypoints.
- Resolved code review warnings by enforcing expected artifact retention and symlink-safe output directory checks.

## Task Commits

1. **Task 19-01-01: aggregate evidence verifier** - `0641ad7fd` (`feat`)
2. **Task 19-01-02: verifier tests** - `3c6e1e132` (`test`)
3. **Task 19-01-03: CI and developer facade wiring** - `eeeed96de` (`chore`)
4. **Task 19-01-04: review hardening** - `76311d30a` (`fix`)
5. **Task 19-01-05: summary and verification artifacts** - recorded in plan metadata commits

## Files Created/Modified

- `tools/bazel/phase19_aggregate_ci_evidence.py` - Phase 19 aggregate evidence verifier and artifact writer.
- `tools/bazel/phase19_aggregate_ci_evidence_test.py` - Python `unittest` coverage for the Phase 19 verifier.
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - Machine-readable Phase 19 aggregate evidence contract.
- `.github/workflows/ci-evidence.yml` - CI now runs and uploads the Phase 19 aggregate evidence bundle.
- `tools/bazel/BUILD.bazel` - Adds Phase 19 Bazel shell binaries and source manifest grouping.
- `BUILD.bazel` - Adds root docs filegroup and Phase 19 aliases.
- `tools/bazel/rust_workflow.sh` - Adds Phase 19 verify and test dispatch cases.
- `justfile` - Adds `phase19-verify`.

## Review Follow-Up

Code review found no critical issues and identified two warnings plus one cleanup item. Follow-up commit `76311d30a`:

- Enforces each source phase contract's `expected_artifacts` list before artifact retention can pass.
- Adds negative test coverage for missing expected source artifacts.
- Hardens `--output-dir` against symlink escapes before destructive writes.
- Removes dead snapshot-source scaffolding.

## Verification

Passed:

- `python3 tools/bazel/phase19_aggregate_ci_evidence_test.py` (`7` tests)
- `python3 tools/bazel/phase19_aggregate_ci_evidence.py --ci --output-dir build/ci-evidence/phase19`
- `python3 tools/bazel/phase19_aggregate_ci_evidence.py --security-only`
- `python3 tools/bazel/phase19_aggregate_ci_evidence.py --wiring-only`
- `bazel run //tools/bazel:phase19_verify_tests`
- `bazel run //tools/bazel:phase19_verify`
- `git diff --check`

Generated manifest spot-check:

- Gate rows: 30
- Owning phases: Phase 14, Phase 15, Phase 16, Phase 17, Phase 18
- Requirement coverage: CIEV-01, CIEV-02, CIEV-03, SIM-01, SIM-02, HARD-01, HARD-02, HARD-03, LIVE-01, LIVE-02, LIVE-03
- External rows: pending simulator, pending hardware, pending live, pending release, pending maintainer review

## Decisions Made

- Kept source phase quick artifacts in their existing output roots first, then copied sanitized snapshots into the Phase 19 aggregate bundle.
- Left Phase 17 and Phase 18 external rows pending because Phase 20 and Phase 21 own real release output production and final readiness result consumption.
- Kept CI YAML thin and placed substantive logic in `tools/bazel/phase19_aggregate_ci_evidence.py`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Narrowed redaction scan to avoid safe contract identifier false positives**
- **Found during:** Task 19-01-02 verification
- **Issue:** The initial forbidden text pattern rejected Phase 17's safe `claim-firmware-payload-retention` contract identifier as if it were a payload value.
- **Fix:** Narrowed the payload scan to `firmware_payload_value`-style payload markers while preserving checks for private keys, token values, password values, certificate bytes, and crash dump values.
- **Files modified:** `tools/bazel/phase19_aggregate_ci_evidence.py`
- **Verification:** `python3 tools/bazel/phase19_aggregate_ci_evidence_test.py` passed.
- **Committed in:** `0641ad7fd`

**2. [Rule 2 - Missing Critical] Enforced expected artifact retention and symlink-safe output paths**
- **Found during:** Code review gate
- **Issue:** The aggregate writer could pass artifact retention without enforcing the contract's `expected_artifacts`, and the output directory guard was lexical before destructive writes.
- **Fix:** Added expected artifact checks, symlink-resolved output guard, and negative tests for both behaviors.
- **Files modified:** `tools/bazel/phase19_aggregate_ci_evidence.py`, `tools/bazel/phase19_aggregate_ci_evidence_test.py`
- **Verification:** Full Phase 19 direct, Bazel, and `just` verification commands passed.
- **Committed in:** `76311d30a`

**Total deviations:** 2 auto-fixed issues.
**Impact on plan:** No scope change; the implementation now has stronger artifact-retention and path-safety guarantees.

## Issues Encountered

- Parallel local verification commands raced on shared generated Phase 14-18 evidence directories. Serial verification matches the CI and `just`/Bazel execution path and passed cleanly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 20 can now target release-candidate artifact production knowing CI retains Phase 17's current pending release rows inside the Phase 19 aggregate bundle. Phase 21 can consume a single aggregate manifest once upstream result consumption is added.

## Self-Check: PASSED

- Key created files exist.
- Task commits are present.
- Summary reflects the actual verifier, tests, workflow, and facade wiring.

*Phase: 19-aggregate-cutover-evidence-ci*
*Completed: 2026-06-21*
