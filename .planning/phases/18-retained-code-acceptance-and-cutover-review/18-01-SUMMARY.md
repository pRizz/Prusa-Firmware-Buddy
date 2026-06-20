---
phase: 18-retained-code-acceptance-and-cutover-review
plan: "01"
subsystem: verification
tags: [bazel, just, retained-code, cutover-review, redaction, firmware]
requires:
  - phase: 11-parity-pyramid-and-cutover-evidence
    provides: retained-code rows, cutover readiness criteria, source evidence refs
  - phase: 13-ci-evidence-orchestration
    provides: CI evidence contract rows
  - phase: 14-simulator-evidence-gates
    provides: simulator evidence contract rows
  - phase: 15-hardware-safety-and-media-qualification
    provides: hardware, safety, and media evidence contract rows
  - phase: 16-live-network-and-transfer-qualification
    provides: live-service, network, and transfer evidence contract rows
  - phase: 17-release-candidate-artifact-and-signing-gates
    provides: release artifact and signing evidence contract rows
provides:
  - Phase 18 retained-code acceptance packet contract
  - Phase 18 final demotion criteria and decision-input validation
  - Redacted quick artifact bundle under build/ci-evidence/phase18
  - Bazel labels, root aliases, rust workflow dispatch, and just facade
affects: [phase18, cutover, retained-code, release-readiness, bazel-workflows]
tech-stack:
  added: []
  patterns:
    - stdlib Python verifier with strict JSON/source-ref validation
    - deterministic generated evidence under build/ci-evidence
    - Bazel shell_binary facade through rust_workflow.sh
key-files:
  created:
    - tools/bazel/manifests/phase18_cutover_review_contract.json
    - tools/bazel/phase18_cutover_review.py
    - tools/bazel/phase18_cutover_review_test.py
  modified:
    - tools/bazel/BUILD.bazel
    - BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - justfile
key-decisions:
  - "Kept quick-mode output as review material only; demotion_allowed remains false without maintainer decision input."
  - "Validated all source refs against approved prior-phase manifests instead of treating prose references as sufficient evidence."
  - "Rejected secret, payload, crash-dump, credential, and cutover-approval overclaims before accepting inputs or generated artifacts."
patterns-established:
  - "Decision input is an explicit JSON packet; local quick artifacts cannot imply maintainer approval."
  - "Phase workflow wiring is self-checked through --wiring-only before quick artifact generation."
requirements-completed: [REV-01, REV-02, REV-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 18-2026-06-20T14-27-15
generated_at: 2026-06-20T15:40:01Z
duration: 30m 21s
completed: 2026-06-20
---

# Phase 18 Plan 01: Retained-Code Acceptance and Cutover Review Summary

**Retained-code acceptance and final cutover review gate with redacted quick artifacts, maintainer decision validation, and Bazel/just workflow wiring**

## Performance

- **Duration:** 30m 21s
- **Started:** 2026-06-20T15:09:40Z
- **Completed:** 2026-06-20T15:40:01Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Added the Phase 18 contract covering retained-code packets, final demotion criteria, exact status vocabularies, REV requirement coverage, and source-ref resolution across Phase 11/13/14/15/16/17 manifests.
- Implemented `phase18_cutover_review.py` with `--contract-only`, `--quick`, `--security-only`, `--decision-input`, `--output-dir`, and `--wiring-only`.
- Generated deterministic redacted artifacts under `build/ci-evidence/phase18` while keeping `demotion_allowed` false without valid maintainer decision input.
- Added Bazel targets, root aliases/docs, `rust_workflow.sh` dispatch, and `just phase18-verify` with tests-before-verifier ordering.

## Task Commits

Each task was committed atomically:

1. **Task 1 RED:** `b1e7cb911` - `test(18-01): add failing tests for cutover review contract`
2. **Task 1 GREEN:** `b518a1ed6` - `feat(18-01): define cutover review contract`
3. **Task 2 RED:** `6fd07e369` - `test(18-01): add failing tests for cutover review decisions`
4. **Task 2 GREEN:** `249ea9035` - `feat(18-01): implement cutover review decision artifacts`
5. **Task 3 RED:** `45c579d1a` - `test(18-01): add failing tests for phase18 wiring`
6. **Task 3 GREEN:** `cf242f574` - `feat(18-01): wire phase18 cutover review`

## Files Created/Modified

- `tools/bazel/manifests/phase18_cutover_review_contract.json` - Phase 18 retained packet and final demotion contract.
- `tools/bazel/phase18_cutover_review.py` - Contract, decision, security, quick artifact, and wiring verifier.
- `tools/bazel/phase18_cutover_review_test.py` - TDD coverage for schema, source refs, decisions, exceptions, redaction, demotion semantics, and wiring.
- `tools/bazel/BUILD.bazel` - Phase 18 source manifest filegroup and verifier/test shell_binary targets.
- `BUILD.bazel` - Phase 18 docs filegroup and root aliases.
- `tools/bazel/rust_workflow.sh` - Phase 18 verifier/test dispatch.
- `justfile` - `phase18-verify` facade.

## Decisions Made

- Quick mode writes review material only and never claims approval or reference demotion without decision input.
- Security scanning applies to the checked-in contract, optional decision input, and generated artifact bundle.
- Retained-code acceptance is blocked from overclaiming: accepted/deferred packet statuses require validated retained review input.

## Deviations from Plan

None - plan executed as written.

## Issues Encountered

- The first Task 1 green draft used narrower local schema names than the plan required. It was corrected before the implementation commit so the checked-in contract uses the exact planned packet and decision fields.

## Known Stubs

None - stub scan found no TODO/FIXME/placeholder-style markers or empty mock-data flows in the changed files.

## Verification

- `python3 tools/bazel/phase18_cutover_review_test.py` - passed, 22 tests.
- `python3 tools/bazel/phase18_cutover_review.py --contract-only` - passed.
- `python3 tools/bazel/phase18_cutover_review.py --quick` - passed, generated `build/ci-evidence/phase18` artifacts with `demotion_allowed=false`.
- `python3 tools/bazel/phase18_cutover_review.py --security-only` - passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` - passed.
- `bazel query "//tools/bazel:phase18_verify + //tools/bazel:phase18_verify_tests + //:phase18_verify + //:phase18_verify_tests"` - passed.
- `bazel run //tools/bazel:phase18_verify_tests && bazel run //tools/bazel:phase18_verify` - passed.
- `just phase18-verify` - passed.
- `node /Users/peterryszkiewicz/.codex/get-shit-done/bin/gsd-tools.cjs verify lifecycle 18 --expect-id 18-2026-06-20T14-27-15 --expect-mode yolo --require-plans` - passed with lifecycle valid.
- `git diff --check` - passed.
- Rust commit gates were run before each task commit: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 18 is exposed through local and Bazel workflows. The final review packet is ready for maintainer decision input, and local quick evidence remains explicitly blocked from approving reference demotion by itself.

## Self-Check: PASSED

- Key files exist: `tools/bazel/manifests/phase18_cutover_review_contract.json`, `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`, `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile`, and this summary.
- Task commits exist: `b1e7cb911`, `b518a1ed6`, `6fd07e369`, `249ea9035`, `45c579d1a`, and `cf242f574`.

---
*Phase: 18-retained-code-acceptance-and-cutover-review*
*Completed: 2026-06-20*
