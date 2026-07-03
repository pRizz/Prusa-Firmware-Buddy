# Phase 25: Live-Service Evidence Execution - Research

**Researched:** 2026-06-23
**Domain:** Python/Bazel evidence execution wrapper around existing live-service contracts
**Confidence:** HIGH

## Summary

Phase 25 should be implemented as a new `phase25_live_service_evidence_execution.py` verifier plus `phase25_live_service_evidence_execution_contract.json`, not as edits to the Phase 16 contract. Phase 16 already defines the 20 canonical live-service scenarios, including Connect registration, telemetry, command channel, proxy, transfers, PrusaLink/WUI routes/auth, SNTP, mDNS, syslog/metrics, TLS/custom CA, negative-protocol cases, long transfers, crash-dump upload, and contract traceability.

The best local model is Phase 24: import the v1.1 source contract, assert exact scenario identity, add a v1.2 packet schema and status vocabulary, reject secret-bearing evidence, write blocked quick placeholders, validate complete real evidence packets, retain redacted outputs, and emit an upstream row for later final-readiness consumers.

## Source Contracts

- `tools/bazel/manifests/phase16_live_network_evidence_contract.json` is the canonical scenario catalog.
- `tools/bazel/phase16_live_network_evidence.py` provides the existing live-network evidence guardrails.
- `tools/bazel/manifests/phase18_cutover_review_contract.json` and `tools/bazel/phase18_cutover_review.py` define downstream cutover review expectations.
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` and `tools/bazel/phase19_aggregate_ci_evidence.py` define aggregate placeholder behavior.
- `tools/bazel/phase23_simulator_evidence_execution.py` and `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` are the current v1.2 execution wrapper patterns.

## Implementation Pattern

Use a single cohesive plan:

1. Add a Phase 25 execution contract that names Phase 16, Phase 18, Phase 19, Phase 23, and Phase 24 as source contracts.
2. Add a Phase 25 verifier with `--contract-only`, `--security-only`, `--wiring-only`, `--quick`, `--evidence-input`, and `--output-dir`.
3. Add focused Python tests for complete packet acceptance, missing/duplicate/unknown scenarios, invalid statuses, blocked source statuses, exception metadata, service-surface drift, evidence-type mismatch, artifact ref bounds, secret/overclaim guards, retained outputs, and wiring.
4. Add Bazel targets, root aliases, `rust_workflow.sh` cases, and `just phase25-verify`.

## Verification Strategy

Run:

- `python3 tools/bazel/phase25_live_service_evidence_execution_test.py`
- `python3 tools/bazel/phase25_live_service_evidence_execution.py --contract-only`
- `python3 tools/bazel/phase25_live_service_evidence_execution.py --security-only`
- `python3 tools/bazel/phase25_live_service_evidence_execution.py --wiring-only`
- `python3 tools/bazel/phase25_live_service_evidence_execution.py --quick --output-dir build/ci-evidence/phase25`
- `just phase25-verify`
- `git diff --check`

## Risks

- The Phase 16 contract uses live-service source statuses that are broader than the v1.2 status vocabulary. The wrapper must preserve source status separately and fail closed when a non-pass source status is submitted as a Phase 25 pass.
- The Phase 16 contract has a source-contract boundary scenario. It should pass only with `source-contract-passed` and `source-contract-validation`, not with generic live evidence.
- Secret scanning must cover service-specific terms, including tokens, registration codes, fingerprints, API keys, auth headers, raw HTTP/TLS logs, raw production payloads, and crash dumps.
