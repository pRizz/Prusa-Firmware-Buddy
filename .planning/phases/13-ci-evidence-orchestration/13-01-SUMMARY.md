---
phase: 13-ci-evidence-orchestration
plan: 01
subsystem: ci-evidence
tags: [bazel, github-actions, ci, evidence, verification]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 13-2026-06-16T14-21-01
generated_at: 2026-06-16T15:17:43Z

requires:
  - phase: 11-parity-pyramid-and-cutover-evidence
    provides: aggregate cutover verifier and v1.0 evidence manifests
provides:
  - Phase 13 CI evidence contract and verifier modes
  - Repo-owned GitHub Actions workflow for PR and manual CI evidence generation
  - Bazel and just facade for Phase 13 verification
  - Local validation sign-off for CIEV-01, CIEV-02, and CIEV-03
affects: [phase14-simulator-evidence, phase15-hardware-evidence, phase16-live-service-evidence, phase17-release-evidence, phase18-cutover-review]

tech-stack:
  added: [python-stdlib-unittest, github-actions-workflow, bazel-shell-binary]
  patterns: [checked-in evidence contracts, thin CI workflow, generated ignored evidence bundle]

key-files:
  created:
    - tools/bazel/manifests/phase13_ci_evidence_contract.json
    - tools/bazel/phase13_ci_evidence.py
    - tools/bazel/phase13_ci_evidence_test.py
    - .github/workflows/ci-evidence.yml
    - .planning/phases/13-ci-evidence-orchestration/13-01-SUMMARY.md
    - .planning/phases/13-ci-evidence-orchestration/13-REVIEW.md
  modified:
    - tools/bazel/BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - BUILD.bazel
    - justfile
    - .planning/phases/13-ci-evidence-orchestration/13-VALIDATION.md
    - tools/bazel/phase11_verify.py
    - tools/bazel/phase11_verify_test.py

key-decisions:
  - "Phase 13 uses a checked-in JSON contract plus generated run manifest instead of deriving gate shape from workflow text."
  - "The CI workflow remains a thin read-only GitHub Actions wrapper around the repo-owned Python verifier."
  - "Later simulator, hardware, live-service, release, signing, retained-code, and maintainer review evidence remains pending non-local evidence."
  - "Archived v1.0 evidence is accepted for Phase 11 aggregate verification after milestone archival."

patterns-established:
  - "Evidence orchestration uses Python verifier modes for contract, workflow, security, wiring, quick, and CI output checks."
  - "Generated CI evidence is written to ignored build/ci-evidence/phase13/ and summarized through redacted JSON."

requirements-completed:
  - CIEV-01
  - CIEV-02
  - CIEV-03

duration: 18 min
completed: 2026-06-16
---

# Phase 13 Plan 01: CI Evidence Orchestration Summary

**Repo-owned CI evidence contract, workflow, manifest writer, and Bazel/just verification facade for cutover evidence gates**

## Performance

- **Duration:** 18 min
- **Started:** 2026-06-16T14:59:56Z
- **Completed:** 2026-06-16T15:17:43Z
- **Tasks:** 3
- **Files modified:** 13

## Accomplishments

- Added a checked-in Phase 13 CI evidence contract mapping CIEV-01, CIEV-02, and CIEV-03 to explicit gate IDs, status vocabulary, source evidence refs, and artifact paths.
- Added `tools/bazel/phase13_ci_evidence.py` with contract, workflow, security, wiring, quick, and CI evidence output modes plus unittest coverage.
- Added `.github/workflows/ci-evidence.yml` with PR path filters, manual dispatch, read-only permissions, and artifact upload from `build/ci-evidence/phase13/`.
- Wired `bazel run //tools/bazel:phase13_verify_tests`, `bazel run //tools/bazel:phase13_verify`, and `just phase13-verify`.
- Updated validation metadata to `local-signoff` while leaving later non-local evidence classes pending.
- Hardened generated evidence retention after code review so forbidden snapshot, log, and contract metadata cannot be retained in uploaded artifacts.
- Recorded a clean advisory code review after the hardening fixes.

## Task Commits

1. **Blocker fix: Archived v1.0 Phase 11 evidence** - `f5e85b7` (fix)
2. **Task 0: Phase 13 contract and verifier test harness** - `23e1330` (feat)
3. **Task 1: Repo-owned CI workflow and generated evidence writer** - `32bf674` (feat)
4. **Task 2: Bazel, just, and validation sign-off** - `d7df0ef` (feat)
5. **Post-review hardening: Artifact redaction ordering** - `0d0e79c` (fix)
6. **Post-review hardening: Generated gate metadata and Phase 11 Bazel archival** - `3c5e00f` (fix)
7. **Advisory code review artifact** - `e5d5544` (docs)

## Files Created/Modified

- `tools/bazel/manifests/phase13_ci_evidence_contract.json` - Phase 13 gate contract.
- `tools/bazel/phase13_ci_evidence.py` - Verifier and generated CI evidence writer.
- `tools/bazel/phase13_ci_evidence_test.py` - Regression tests for contract, workflow, security, CI output, and wiring behavior.
- `.github/workflows/ci-evidence.yml` - PR/manual CI evidence workflow.
- `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `BUILD.bazel`, `justfile` - Bazel and developer facade wiring.
- `.planning/phases/13-ci-evidence-orchestration/13-VALIDATION.md` - Local Wave 0 sign-off.
- `.planning/phases/13-ci-evidence-orchestration/13-REVIEW.md` - Clean advisory review after post-review hardening.
- `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py` - Archive-aware Phase 11 aggregate verifier prerequisite.

## Decisions Made

- Kept substantive CI logic in Python rather than GitHub Actions YAML.
- Preserved later non-local evidence as named pending classes in `redacted-summary.json`.
- Treated v1.0 milestone archival as a supported evidence location for Phase 11 aggregate verification.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Phase 11 aggregate verifier needed archived v1.0 evidence resolution**
- **Found during:** Task 1 (generated evidence writer verification)
- **Issue:** `python3 tools/bazel/phase11_verify.py --quick` failed because Phase 11 source artifacts and v1 requirements had moved under `.planning/milestones/v1.0-*`.
- **Fix:** Made Phase 11 source artifact checks archive-aware and taught tests to use the archived v1.0 requirements fixture when present.
- **Files modified:** `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`
- **Verification:** `python3 tools/bazel/phase11_verify_test.py`; `python3 tools/bazel/phase11_verify.py --quick`
- **Committed in:** `f5e85b7`

**2. [Rule 3 - Blocking] Root Bazel package analysis failed on archived Phase 1 glob**
- **Found during:** Task 2 (`just phase13-verify`)
- **Issue:** `BUILD.bazel` used a non-empty glob for `.planning/phases/01-reference-baseline-and-safety-envelope/01-*.md`, which no longer exists after v1.0 archival.
- **Fix:** Made `phase1_reference_baseline` include both active and archived paths with empty-safe globs.
- **Files modified:** `BUILD.bazel`
- **Verification:** `just phase13-verify`
- **Committed in:** `d7df0ef`

**3. [Rule 2 - Missing Critical] Generated evidence needed pre-retention redaction**
- **Found during:** Code review gate
- **Issue:** Copied snapshots and command logs could be written under `build/ci-evidence/phase13/` before the security scan returned failure.
- **Fix:** Sanitized command logs before write, rejected unsafe copied snapshots before retention, cleaned the generated output directory before each run, and marked redaction failures in the generated gate rows.
- **Files modified:** `tools/bazel/phase13_ci_evidence.py`, `tools/bazel/phase13_ci_evidence_test.py`
- **Verification:** `python3 tools/bazel/phase13_ci_evidence_test.py`; `python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13`
- **Committed in:** `0d0e79c`

**4. [Rule 2 - Missing Critical] Generated gate metadata and archived Phase 11 evidence needed hardening**
- **Found during:** Code review re-check
- **Issue:** Malformed contract gate metadata could flow into generated JSON before final scan, archived `11-VERIFICATION.md` was outside the Phase 11 security scan, and the Bazel Phase 11 verifier docs filegroup still referenced removed active Phase 11 docs.
- **Fix:** Generated artifact rows now use static gate metadata whenever contract validation or field sanitization fails; Phase 11 scans archived verification docs; root `phase11_cutover_evidence_docs` uses empty-safe active and archived globs.
- **Files modified:** `tools/bazel/phase13_ci_evidence.py`, `tools/bazel/phase13_ci_evidence_test.py`, `tools/bazel/phase11_verify.py`, `tools/bazel/phase11_verify_test.py`, `BUILD.bazel`
- **Verification:** `python3 tools/bazel/phase13_ci_evidence_test.py`; `python3 tools/bazel/phase11_verify_test.py`; `bazel run //tools/bazel:phase11_verify`; `just phase13-verify`
- **Committed in:** `3c5e00f`

**Total deviations:** 4 auto-fixed (2 blocking, 2 missing critical)
**Impact on plan:** All fixes strengthen the planned CI evidence and archive-handling guarantees. No Phase 14-18 evidence was converted into local pass evidence.

## Issues Encountered

- Bazel server startup took about 40 seconds on the first `just phase13-verify` run, then subsequent runs completed quickly.
- Advisory code review initially found generated-artifact redaction gaps; both rounds were fixed and the final review status is `clean`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 13 local CI evidence orchestration is ready for phase-level verification. Phases 14-18 should attach the pending simulator, hardware, live-service, release/signing, retained-code, and maintainer review evidence classes named in the generated redacted summary.

*Phase: 13-ci-evidence-orchestration*
*Completed: 2026-06-16*
