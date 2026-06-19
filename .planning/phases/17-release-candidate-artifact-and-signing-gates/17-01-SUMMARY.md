---
phase: 17-release-candidate-artifact-and-signing-gates
plan: 01
subsystem: release-engineering
tags: [bazel, release-candidate, signing-gates, evidence, redaction]

requires:
  - phase: 11-parity-pyramid-and-cutover-evidence
    provides: Reference comparison, cutover readiness, retained-code, and requirement evidence manifests.
  - phase: 13-ci-evidence-orchestration
    provides: CI evidence contract patterns and redacted evidence artifact expectations.
  - phase: 15-hardware-safety-and-media-qualification
    provides: Hardware evidence contract and redaction boundary patterns.
  - phase: 16-live-network-and-transfer-qualification
    provides: Live network evidence contract and wiring patterns.
provides:
  - Phase 17 release candidate evidence contract with row-level artifact, signing, provenance, retention, and comparison gates.
  - Stdlib verifier for contract, security, quick artifact generation, release evidence input, and wiring checks.
  - Bazel and just workflow labels for Phase 17 release candidate artifact verification.
affects: [phase17, release-artifacts, signing, provenance, bazel-workflows]

tech-stack:
  added: []
  patterns:
    - Stdlib-only Python verifier with repo-relative path guards and redaction scans.
    - Contract-driven evidence rows that keep local smoke labels separate from approved release-run evidence.

key-files:
  created:
    - tools/bazel/manifests/phase17_release_candidate_evidence_contract.json
    - tools/bazel/phase17_release_candidate_evidence.py
    - tools/bazel/phase17_release_candidate_evidence_test.py
    - .planning/phases/17-release-candidate-artifact-and-signing-gates/17-01-SUMMARY.md
  modified:
    - tools/bazel/BUILD.bazel
    - BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - justfile

key-decisions:
  - "Preserved lifecycle id 17-2026-06-19T13-57-17 in the Phase 17 contract, quick artifacts, and summary metadata."
  - "Kept production release proof gated on //tools/bazel:phase17_release_candidate_artifacts while representative labels remain local smoke only."
  - "Kept signing evidence name/digest/reference-only; private key material and firmware payload bytes are rejected."

patterns-established:
  - "Phase 17 quick evidence writes deterministic redacted artifacts under build/ci-evidence/phase17."
  - "Release evidence inputs must use external://phase17/... or guarded repo-relative paths under build/ci-evidence/phase17."

requirements-completed: [REL-01, REL-02, REL-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 17-2026-06-19T13-57-17
generated_at: 2026-06-19T15:01:58Z

duration: 23m43s
completed: 2026-06-19
---

# Phase 17 Plan 01: Release Candidate Artifact and Signing Gates Summary

**Release candidate evidence contract with redacted signing/provenance gates, deterministic quick artifacts, and Bazel/just verification entrypoints**

## Performance

- **Duration:** 23m43s
- **Started:** 2026-06-19T14:38:15Z
- **Completed:** 2026-06-19T15:01:58Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Added `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` covering all required release artifact families, supported products/boards, release workflow identity, local smoke identities, status vocabulary, and mismatch classes.
- Added `tools/bazel/phase17_release_candidate_evidence.py` with `--contract-only`, `--security-only`, `--quick`, `--release-evidence`, and `--wiring-only` modes.
- Added `tools/bazel/phase17_release_candidate_evidence_test.py` covering contract completeness, release evidence validation, redaction/path guards, generated quick artifacts, and workflow wiring.
- Wired `//tools/bazel:phase17_release_candidate_artifacts`, `//tools/bazel:phase17_verify`, `//tools/bazel:phase17_verify_tests`, root aliases, `rust_workflow.sh`, and `just phase17-verify`.

## Task Commits

1. **TDD RED: Phase 17 evidence tests** - `88a075e7f` (test)
2. **Tasks 1-2: Contract and verifier implementation** - `25b214acf` (feat)
3. **Task 3: Bazel, workflow, and just wiring** - `e78d8e900` (feat)

## Files Created/Modified

- `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` - Machine-readable release candidate evidence contract with lifecycle id `17-2026-06-19T13-57-17`.
- `tools/bazel/phase17_release_candidate_evidence.py` - Contract verifier, release evidence validator, redaction/security scanner, quick artifact writer, and wiring checker.
- `tools/bazel/phase17_release_candidate_evidence_test.py` - Unit tests for contract, verifier, security, release evidence, and wiring behavior.
- `tools/bazel/BUILD.bazel` - Phase 17 artifact, source manifest, verifier, and verifier-test targets.
- `BUILD.bazel` - Root Phase 17 docs filegroup and public aliases.
- `tools/bazel/rust_workflow.sh` - Phase 17 verifier dispatch cases.
- `justfile` - `phase17-verify` and `phase17-release-artifacts-smoke` recipes.

## Decisions Made

- The release target identity is `//tools/bazel:phase17_release_candidate_artifacts`; representative artifact labels are explicitly local smoke only and cannot satisfy production release proof.
- Quick mode writes pending/redacted evidence artifacts locally while retaining approved release-run and external signing proof as input-gated statuses.
- Security scanning rejects private key markers, credential assignments, payload markers, and release overclaims without echoing secret values.
- Shared planning state files were not updated in this executor run because the orchestrator owns `.planning/STATE.md` and `.planning/ROADMAP.md` for this execution.

## Deviations from Plan

### Auto-fixed Issues

None - no Rule 1-3 deviations were needed beyond ordinary TDD implementation iteration.

### Process Notes

- The RED test suite was committed once for the full Phase 17 surface, then implementation and wiring were committed separately. This kept the cross-validating contract/verifier/wiring expectations in one test file without changing plan scope.
- A parallel exploratory verification run briefly raced `--security-only` against `--quick` while quick mode rewrote the ignored output directory. The requested verification sequence was rerun sequentially and passed.

## Known Stubs

None. Stub scan findings were limited to local accumulator initializations and test helper defaults; no UI/data-source placeholder or unresolved evidence stub was introduced.

## Issues Encountered

None remaining.

## Verification

- `python3 tools/bazel/phase17_release_candidate_evidence_test.py` - passed
- `python3 tools/bazel/phase17_release_candidate_evidence.py --contract-only` - passed
- `python3 tools/bazel/phase17_release_candidate_evidence.py --security-only` - passed
- `python3 tools/bazel/phase17_release_candidate_evidence.py --quick` - passed
- `python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only` - passed
- `bazel query "//tools/bazel:phase17_release_candidate_artifacts + //:phase17_release_candidate_artifacts"` - passed
- `bazel build //tools/bazel:phase17_release_candidate_artifacts` - passed
- `bazel run //tools/bazel:phase17_verify_tests` - passed
- `bazel run //tools/bazel:phase17_verify` - passed
- `just phase17-verify` - passed
- `git diff --check` - passed
- `cargo fmt --all` - passed before task commits
- `cargo clippy --all-targets --all-features -- -D warnings` - passed before task commits
- `cargo build --all-targets --all-features` - passed before task commits
- `cargo test --all-features` - passed before task commits

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 17 now has a release-candidate evidence gate that can accept approved external release/signing evidence while keeping local quick checks deterministic and redacted. Remaining release proof is intentionally input-gated by approved release-run metadata, signing key identity references, artifact digests, retention paths, and comparison evidence.

## Self-Check: PASSED

- Found `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-01-SUMMARY.md`.
- Found task commit `88a075e7f`.
- Found task commit `25b214acf`.
- Found task commit `e78d8e900`.

---
*Phase: 17-release-candidate-artifact-and-signing-gates*
*Completed: 2026-06-19*
