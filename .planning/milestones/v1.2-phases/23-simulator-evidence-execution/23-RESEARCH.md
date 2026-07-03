---
phase: 23-simulator-evidence-execution
generated_by: gsd-phase-researcher
lifecycle_mode: yolo
phase_lifecycle_id: 23-2026-06-23T18-45-38
generated_at: 2026-06-23T18:45:38Z
status: complete
---

# Phase 23: Simulator Evidence Execution Research

## Research Goal

Plan the smallest robust implementation that lets maintainers supply and retain real simulator evidence while preserving the v1.1 Phase 14 simulator contract and the v1.2 requirement EVID-01.

## Source Contracts

- `tools/bazel/manifests/phase14_simulator_evidence_contract.json` is the canonical simulator scenario catalog. It defines nine scenario IDs spanning startup/task readiness/watchdog-visible readiness, G-code telemetry, GUI navigation, storage/resource WUI behavior, transfer conflict behavior, selected thermal failures, and traceability boundaries.
- `tools/bazel/phase14_simulator_evidence.py` already supports contract validation, quick dry-run artifacts, real simulator execution with `--run-simulator --firmware`, redacted logs, and guards against secret content and non-local proof overclaims.
- `tools/bazel/phase19_aggregate_ci_evidence.py` shows how local verifiers retain generated evidence while making external input placeholders explicit.
- `tools/bazel/phase18_cutover_review.py` shows how upstream result rows are consumed later without allowing demotion when upstream evidence is missing, failed, or not exception-approved.

## Implementation Approach

Add a new Phase 23 verifier and manifest instead of mutating Phase 14. Phase 14 remains the v1.1 gate-capability contract; Phase 23 adds v1.2 real-result submission semantics around that contract.

The Phase 23 tool should:

- Validate the Phase 14 contract is present and complete.
- Validate an optional maintainer-supplied simulator evidence packet.
- Require one row per Phase 14 scenario.
- Normalize scenario statuses to `passed`, `failed`, `blocked`, or `exception-requested`.
- Reject pending Phase 14 source statuses when normalized as passed.
- Require exception metadata for `exception-requested`.
- Retain generated outputs under `build/ci-evidence/phase23`.
- Write an upstream-consumable row that later acceptance phases can ingest or reference.
- Reject secrets, unsafe field names, path traversal, raw payload markers, and non-local overclaim phrases.

## Validation Architecture

Phase 23 verification should include:

- Contract-only validation for the Phase 23 manifest and the referenced Phase 14 scenarios.
- Unit tests for accepted complete evidence input.
- Negative tests for missing scenario coverage, duplicate scenario IDs, invalid status, pending-as-passed, missing exception metadata, forbidden secret fields, and artifact path traversal.
- Wiring tests for `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile`.
- Quick mode that writes blocked placeholder rows, not fake pass proof.

## Risks and Controls

- **Risk:** A quick fixture accidentally claims real simulator proof.  
  **Control:** Quick mode writes `real_simulator_evidence_supplied: false`, scenario `blocked`, and a redacted summary that names the real input requirement.
- **Risk:** A maintainer supplies raw secrets or payloads.  
  **Control:** Validate forbidden field names and forbidden text before retaining artifacts.
- **Risk:** Phase 23 diverges from Phase 14 scenario IDs.  
  **Control:** Validate packet scenario IDs exactly match the Phase 14 contract.
- **Risk:** Simulator pass is overread as hardware or demotion proof.  
  **Control:** Preserve residual non-simulator gates in normalized outputs and reject overclaim phrases.

## Recommendation

Implement one cohesive plan: add the Phase 23 manifest/tool/tests, wire it into Bazel/just, update planning metadata, then verify with Python tests, quick verifier mode, and lifecycle validation.
