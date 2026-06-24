---
phase: 26-release-signing-and-upstream-result-evidence
plan: "01"
subsystem: release-signing-upstream-evidence
tags:
  - release
  - signing
  - upstream-results
  - redaction
  - bazel
requirements:
  - EVID-04
  - ACPT-01
dependency_graph:
  requires:
    - phase17_release_candidate_evidence_contract
    - phase18_cutover_review_contract
    - phase20_release_candidate_artifacts_contract
    - phase20_release_environment_inputs_template
    - phase23_simulator_evidence_execution_contract
    - phase24_hardware_media_safety_evidence_execution_contract
    - phase25_live_service_evidence_execution_contract
  provides:
    - phase26_release_signing_upstream_evidence_contract
    - phase26_release_signing_upstream_evidence_verifier
    - phase26_normalized_upstream_result_rows
    - phase26_redacted_retained_release_evidence_outputs
    - phase26_bazel_and_just_verification_targets
  affects:
    - phase27_final_cutover_acceptance
    - phase28_reference_demotion_decision
tech_stack:
  added:
    - Python standard-library verifier and unittest suite
    - Bazel sh_binary wiring
    - just workflow recipe
  patterns:
    - functional core with thin CLI and file-output shell
    - generated evidence retained under ignored build tree
    - contract-backed source row loading
key_files:
  created:
    - tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json
    - tools/bazel/phase26_release_signing_upstream_evidence.py
    - tools/bazel/phase26_release_signing_upstream_evidence_test.py
    - tools/bazel/BUILD.bazel
    - .planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md
  modified:
    - BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - justfile
decisions:
  - Phase 26 only treats approved-release-run and external-release-key-evidence as pass-capable release proof classes.
  - Quick mode generates blocked or pending retained evidence outputs and does not approve final cutover, retained code, or reference demotion decisions.
  - Retained evidence files are generated under build/ci-evidence/phase26 and remain uncommitted build outputs.
metrics:
  started_at_utc: 2026-06-24T14:15:38Z
  completed_at_utc: 2026-06-24T14:33:40Z
  duration: 18m02s
  tasks_completed: 3
  commits: 3
---

# Phase 26 Plan 01: Release Signing and Upstream Result Evidence Summary

Phase 26 adds a contract-backed verifier for release/signing evidence and normalized upstream result rows. It preserves Phase 17, Phase 18, and Phase 20 source identities, blocks template/local-smoke/release-candidate proof from passing release evidence, rejects secret-tainted inputs before retained writes, and exposes the workflow through Bazel and `just phase26-verify`.

## Task Outcomes

| Task | Outcome | Commit |
| ---- | ------- | ------ |
| 1. Contract and release evidence validator | Added Phase 26 contract, release input validation, Phase 20 row coverage checks, proof-class policy, secret guard, output-root guard, and regression tests. | `6167c0abc` |
| 2. Upstream row normalization and retained outputs | Added nine canonical Phase 18 upstream rows, D-11 row schema enforcement, redacted retained output generation, contract snapshots, and quick-mode blocked/pending semantics. | `7dca9a017` |
| 3. Bazel, workflow, and just wiring | Added Bazel targets, root aliases, workflow script cases, `just phase26-verify`, and wiring drift tests. | `b9cac70ef` |

## Verification Evidence

All task-specific checks and the required Rust pre-commit sequence passed before each task commit.

- `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` passed with 22 tests.
- `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --contract-only` passed.
- `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --security-only` passed.
- `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --wiring-only` passed.
- `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26` passed and generated the expected retained evidence files.
- Plan row-table assertion passed for the exact nine canonical Phase 18 criterion IDs and required D-11 fields.
- `just phase26-verify` passed through `bazel run //tools/bazel:phase26_verify_tests` and `bazel run //tools/bazel:phase26_verify`.
- `git diff --check` passed.
- Required Rust sequence passed before each commit and after implementation: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, `cargo test --all-features`.

## Retained Outputs

Quick mode writes the plan-required generated artifacts under `build/ci-evidence/phase26`:

- `release-upstream-run-manifest.json`
- `normalized-release-evidence-summary.json`
- `upstream-result-row-table.json`
- `upstream-result-manifest.json`
- `redaction-provenance-summary.json`
- `artifact-reference-summary.json`
- `operator-release-input-template.json`
- `contract-snapshots/phase17_release_candidate_evidence_contract.json`
- `contract-snapshots/phase18_cutover_review_contract.json`
- `contract-snapshots/phase20_release_candidate_artifacts_contract.json`
- `contract-snapshots/phase20_release_environment_inputs.template.json`

These files are intentionally generated under the ignored build tree and were not committed.

## Deviations from Plan

None - the plan implementation was executed as written.

Shared `.planning/STATE.md`, `.planning/ROADMAP.md`, and `.planning/REQUIREMENTS.md` updates were intentionally skipped because the executor prompt assigns shared state ownership to the orchestrator.

## Auto-Fixed Issues

None.

## Authentication Gates

None.

## Known Stubs

None. Quick-mode pending and blocked rows are intentional release-manager and maintainer decision placeholders, not implementation stubs; they do not mark final acceptance as passed.

## Threat Flags

None. The new filesystem write surface is limited to the plan-defined ignored output root and is covered by output-root and symlink-escape validation.

## Residual Risk

- Real release/signing acceptance still requires an external release input packet with approved release-run or external release-key evidence. Quick mode deliberately does not satisfy final release acceptance.
- Phase 26 does not approve retained-code acceptance, residual-risk review, final maintainer readiness, or reference demotion. Those rows remain blocked, pending, or not-required for later maintainer decisions.
- Generated retained outputs are evidence artifacts only; source contracts and verifier code are the committed authority.

## Self-Check

PASSED.

- Found `.planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md`.
- Found task commit `6167c0abc`.
- Found task commit `7dca9a017`.
- Found task commit `b9cac70ef`.
