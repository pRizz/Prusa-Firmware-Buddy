---
phase: 23-simulator-evidence-execution
status: complete
nyquist_compliant: true
wave_0_complete: true
lifecycle_mode: yolo
phase_lifecycle_id: 23-2026-06-23T18-45-38
generated_by: gsd-plan-phase
generated_at: 2026-06-23T18:45:38Z
---

# Phase 23 Validation Strategy

## Validation Architecture

Phase 23 samples the required behavior at the evidence-boundary level:

1. **Schema and contract validation:** The Phase 23 manifest and the Phase 14 simulator contract must agree on scenario coverage and status semantics.
2. **Positive execution path:** A complete maintainer simulator evidence packet must validate and produce retained normalized outputs.
3. **Negative execution paths:** Missing scenarios, invalid statuses, pending source statuses marked as passed, missing exception metadata, forbidden evidence fields, and unsafe artifact refs must fail.
4. **Wiring:** Bazel labels, `rust_workflow.sh`, and `justfile` must expose Phase 23 verify and test entrypoints.
5. **Non-local boundaries:** Quick fixtures and blocked rows must never claim hardware, live-service, release, or demotion proof.

## Expected Verification Commands

- `python3 tools/bazel/phase23_simulator_evidence_execution_test.py`
- `python3 tools/bazel/phase23_simulator_evidence_execution.py --wiring-only`
- `python3 tools/bazel/phase23_simulator_evidence_execution.py --quick --output-dir build/ci-evidence/phase23`
- `just phase23-verify`
- `git diff --check`

## Acceptance Sampling

| Requirement | Sample | Expected |
|-------------|--------|----------|
| EVID-01 | Complete input packet with one row per Phase 14 scenario | accepted, retained, summarized |
| EVID-01 | Missing or duplicate scenario row | rejected |
| EVID-01 | `source_status: pending-simulator-input` with `status: passed` | rejected |
| EVID-01 | `exception-requested` without owner/rationale/evidence/revisit metadata | rejected |
| EVID-01 | Quick mode without real input | retained as blocked placeholder, not passed proof |
