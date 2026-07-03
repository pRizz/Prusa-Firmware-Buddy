---
phase: 29-upstream-evidence-flow-closure
plan: 29-01
subsystem: upstream-evidence-flow-closure
generated_by: gsd-executor
lifecycle_mode: yolo
phase_lifecycle_id: 29-2026-06-25T20-26-39
generated_at: 2026-06-25T21:19:16Z
requirements:
  - ACPT-01
  - READ-01
  - READ-02
key-files:
  modified:
    - tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json
    - tools/bazel/phase26_release_signing_upstream_evidence.py
    - tools/bazel/phase26_release_signing_upstream_evidence_test.py
    - tools/bazel/phase28_final_readiness_packet.py
    - tools/bazel/phase28_final_readiness_packet_test.py
---

# Phase 29 Plan 01: Phase 26 Upstream Row Ingestion Summary

Phase 26 quick mode now accepts explicit Phase 23, Phase 24, and Phase 25 compact upstream row inputs, validates them against source identity and allowed refs, and canonicalizes them into Phase 18/26 upstream rows. Absent row inputs still keep the existing fail-closed defaults.

Phase 28 now preserves Phase 26 evidence lineage in packet criteria by merging Phase 26 and Phase 27 evidence refs. This keeps producer manifests and input row paths visible in the final readiness packet without changing the separate explicit reference-demotion authorization gate.

## Tasks Completed

| Task | Summary |
| ---- | ------- |
| 29-01-01 | Added `--phase23-simulator-row`, `--phase24-hardware-media-safety-row`, and `--phase25-live-service-row` quick-only inputs, the contract `upstream_row_inputs` policy, compact-row validation, canonicalization, and Phase 26 regression coverage. |
| 29-01-02 | Added Phase 28 packet propagation coverage, proved the initial evidence-ref drop, then merged Phase 26 and Phase 27 evidence refs in `normalize_readiness_criteria(...)`. |

## Verification

Passed:

- `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` - 31 tests passed after code-review fixes.
- `python3 tools/bazel/phase28_final_readiness_packet_test.py` - 28 tests passed after code-review fixes.
- `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --contract-only`
- `python3 tools/bazel/phase28_final_readiness_packet.py --contract-only`
- `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26`
- `just phase26-verify`
- `just phase28-verify`
- `git diff --check`

Failure reproduced and fixed:

- `python3 tools/bazel/phase28_final_readiness_packet_test.py` initially failed because Phase 28 packet `evidence_refs` kept Phase 27 decision refs but dropped consumed Phase 26 producer refs for simulator, hardware/media/safety, and live-service rows.

## Residual Risks

- Default `just phase28-verify` remains blocked because it intentionally runs Phase 26 quick mode without real Phase 23/24/25 compact rows. The consumed-row path is covered by focused Phase 26 and Phase 28 tests.
- Real upstream artifacts still need external production and redaction review before final release readiness can become unblocked.
