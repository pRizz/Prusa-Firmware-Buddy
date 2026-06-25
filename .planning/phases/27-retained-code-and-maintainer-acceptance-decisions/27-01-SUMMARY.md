---
phase: 27-retained-code-and-maintainer-acceptance-decisions
plan: "01"
title: "Retained-Code Acceptance Decisions"
subsystem: "Bazel evidence workflow"
tags:
  - acceptance
  - retained-code
  - maintainer-decisions
  - bazel
requirements-completed:
  - ACPT-02
  - ACPT-03
lifecycle_mode: yolo
phase_lifecycle_id: 27-2026-06-25T01-06-06
completed_at: 2026-06-25T02:23:59Z
dependency_graph:
  requires:
    - "26-release-signing-and-upstream-result-evidence"
    - "tools/bazel/manifests/phase18_cutover_review_contract.json"
  provides:
    - "phase27-retained-code-acceptance-decisions"
    - "build/ci-evidence/phase27"
  affects:
    - "Phase 28 final acceptance and reference-demotion handoff"
tech_stack:
  added:
    - "Phase 27 JSON contract"
    - "Phase 27 Python verifier/output writer"
    - "Bazel shell_binary targets and just wrapper"
  patterns:
    - "Phase 18 exact-match contract projection"
    - "Phase 26 upstream row consumption before Phase 27 quick generation"
key_files:
  created:
    - "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
    - "tools/bazel/phase27_retained_code_acceptance_decisions.py"
    - "tools/bazel/phase27_retained_code_acceptance_decisions_test.py"
    - ".planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-01-SUMMARY.md"
  modified:
    - "tools/bazel/BUILD.bazel"
    - "BUILD.bazel"
    - "tools/bazel/rust_workflow.sh"
    - "justfile"
decisions:
  - "Phase 27 projects Phase 18 retained-code/final-decision semantics without copying canonical IDs or vocabularies into the verifier."
  - "Phase 27 always keeps reference demotion blocked and emits a Phase 28 handoff instead of authorizing demotion."
metrics:
  tasks_completed: 3
  task_commits:
    - "ababa0be9"
    - "792055aa1"
    - "f12289b4f"
---

# Phase 27 Plan 01: Retained-Code Acceptance Decisions Summary

Phase 27 now has a machine-readable retained-code acceptance gate that consumes Phase 26 upstream rows, preserves Phase 18 decision semantics, and produces Phase 28 handoff artifacts without converting evidence status into maintainer acceptance.

## Completed Tasks

| Task | Result | Commit |
| ---- | ------ | ------ |
| 1 | Added the Phase 27 contract and contract/security regression coverage. | `ababa0be9` |
| 2 | Implemented maintainer input normalization, hard-block handling, role checks, output containment, and Phase 27 artifacts. | `792055aa1` |
| 3 | Wired Bazel labels, root aliases, workflow dispatch, and `just phase27-verify`. | `f12289b4f` |

## Outputs

- `build/ci-evidence/phase27/acceptance-run-manifest.json`
- `build/ci-evidence/phase27/normalized-retained-code-decisions.json`
- `build/ci-evidence/phase27/residual-risk-register.json`
- `build/ci-evidence/phase27/exception-decision-register.json`
- `build/ci-evidence/phase27/final-readiness-decision-summary.json`
- `build/ci-evidence/phase27/phase28-handoff-manifest.json`
- `build/ci-evidence/phase27/decision-row-table.json`
- `build/ci-evidence/phase27/maintainer-acceptance-input-template.json`
- `build/ci-evidence/phase27/artifact-reference-summary.json`
- `build/ci-evidence/phase27/contract-snapshots/phase18_cutover_review_contract.json`
- `build/ci-evidence/phase27/contract-snapshots/phase26_release_signing_upstream_evidence_contract.json`
- `build/ci-evidence/phase27/contract-snapshots/phase26-upstream-result-row-table.json`

## Verification

- `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
- `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --contract-only`
- `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --wiring-only`
- `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26`
- `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27`
- `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --security-only`
- `bazel query 'set(//tools/bazel:phase27_verify //tools/bazel:phase27_verify_tests)'`
- `just phase27-verify`
- No forbidden `demotion_authorization: "allowed"` or `demotion_allowed: true` markers found.
- `git diff --check`
- `cargo fmt --all`
- `cargo clippy --all-targets --all-features -- -D warnings`
- `cargo build --all-targets --all-features`
- `cargo test --all-features`

## Deviations from Plan

None - plan executed as written.

## Issues

None.

## Known Stubs

None. Blank fields exist only in the generated maintainer input template and test fixtures; the verifier treats missing maintainer input as pending, not accepted.

## Threat Flags

None. The new filesystem reads/writes are the planned Phase 26/27 evidence inputs and output-root-contained artifacts.

## Self-Check: PASSED

- Created files exist.
- Required task commits exist: `ababa0be9`, `792055aa1`, `f12289b4f`.
- Summary includes `requirements-completed: [ACPT-02, ACPT-03]`, `lifecycle_mode: yolo`, and `phase_lifecycle_id: 27-2026-06-25T01-06-06`.
