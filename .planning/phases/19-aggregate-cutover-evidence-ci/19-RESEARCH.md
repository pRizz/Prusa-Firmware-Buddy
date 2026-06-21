---
generated_by: gsd-plan-phase
lifecycle_mode: yolo
phase_lifecycle_id: 19-2026-06-21T01-07-45
generated_at: 2026-06-21T01:18:00.000Z
---

# Phase 19 Research: Aggregate Cutover Evidence CI

## Research Complete

Phase 19 should be implemented as a repo-owned Python verifier that composes the already established Phase 14-18 evidence scripts and retains their generated outputs under one CI artifact root. The existing verifier family provides the contract:

- Phase 13 owns the current CI evidence workflow, artifact retention pattern, redaction scan, and Bazel/just wiring checks.
- Phase 14-18 scripts each expose deterministic local modes: `--contract-only`, `--wiring-only`, `--security-only`, and `--quick`.
- Phase 15, 16, 17, and 18 accept optional external evidence inputs only in their quick modes. When no external input is provided, their generated artifacts preserve pending or blocked status values instead of passing non-local evidence.
- `.github/workflows/ci-evidence.yml` currently runs only `tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13` and uploads only `build/ci-evidence/phase13/`.

## Implementation Pattern

The lowest-risk implementation is a Phase 19-specific aggregate verifier:

1. Validate a new `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` contract.
1. Run Phase 14-18 local deterministic commands and capture sanitized logs in `build/ci-evidence/phase19/logs/`.
1. Run Phase 14-18 quick modes with their normal output directories, then copy selected generated artifacts into `build/ci-evidence/phase19/phase-artifacts/phaseNN/`.
1. Produce `build/ci-evidence/phase19/run-manifest.json` with gate rows containing requirement IDs, owning phase, command or evidence input, artifact path, status, and failure reason.
1. Produce `build/ci-evidence/phase19/redacted-summary.json` and `external-input-placeholders.json`.
1. Update the CI evidence workflow to call the Phase 19 verifier and upload `build/ci-evidence/phase19/`.
1. Add Bazel aliases and `just phase19-verify` so tests run before the verifier.

## Validation Architecture

Validation should be a Python unit-test and verifier loop:

- Unit command: `python3 tools/bazel/phase19_aggregate_ci_evidence_test.py`
- Direct verifier command: `python3 tools/bazel/phase19_aggregate_ci_evidence.py --ci --output-dir build/ci-evidence/phase19`
- Bazel facade command: `bazel run //tools/bazel:phase19_verify_tests && bazel run //tools/bazel:phase19_verify`
- Just facade command: `just phase19-verify`

The tests must prove:

- The contract covers all Phase 19 requirement IDs.
- CI workflow text calls the Phase 19 verifier and uploads the Phase 19 artifact directory.
- The aggregate manifest contains Phase 14-18 gate rows with requirement IDs, phase ownership, artifact paths, and failure reasons.
- External-only statuses remain pending or blocked when no external input file is provided.
- Bazel, `rust_workflow.sh`, and `justfile` expose Phase 19 tests and verifier in the expected order.

## Risks

- Phase 19 must not silently upgrade external evidence to `passed`; tests should fail if forbidden local pass wording or external-only passed statuses appear.
- The aggregate runner should keep generated evidence under `build/ci-evidence/phase19/` and should not commit generated output.
- The runner should not depend on GitHub-specific environment variables so local verification and CI use the same code path.
