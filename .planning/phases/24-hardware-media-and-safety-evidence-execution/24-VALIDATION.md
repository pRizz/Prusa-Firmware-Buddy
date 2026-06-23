---
phase: 24-hardware-media-and-safety-evidence-execution
status: complete
nyquist_compliant: true
wave_0_complete: true
lifecycle_mode: yolo
phase_lifecycle_id: 24-2026-06-23T19-52-32
generated_by: gsd-plan-phase
generated_at: 2026-06-23T19:52:32.454Z
---

# Phase 24 Validation Strategy

## Validation Architecture

Phase 24 samples the required behavior at the evidence-boundary level:

1. **Schema and source-contract validation:** The Phase 24 manifest and the Phase 15 hardware evidence contract must agree on scenario coverage, required operator fields, supported boards/families, media surfaces, artifact kinds, and unsupported claims.
2. **Positive execution path:** A complete maintainer hardware/media/safety evidence packet must validate and produce retained normalized outputs under `build/ci-evidence/phase24`.
3. **Negative execution paths:** Missing scenarios, duplicate scenarios, unknown scenarios, invalid statuses, Phase 15 pending/manual/blocking statuses marked as Phase 24 pass, missing exception metadata, missing residual risk, unsafe artifact refs, forbidden evidence fields, forbidden text, and overclaim phrases must fail.
4. **Media and safety specificity:** Storage evidence must preserve the Phase 15 media surfaces, and safety evidence must fail or block when watchdog, thermal, motion, safe-output, UI-input, MMU, RS485, toolchanger, or auxiliary-controller rows are missing or unresolved.
5. **Wiring:** Bazel labels, `rust_workflow.sh`, and `justfile` must expose Phase 24 verify and test entrypoints.
6. **Non-local boundaries:** Quick fixtures and blocked rows must never claim live-service proof, release/signing proof, retained-code acceptance, final readiness, or reference demotion approval.

## Expected Verification Commands

- `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py`
- `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --contract-only`
- `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --security-only`
- `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --wiring-only`
- `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --quick --output-dir build/ci-evidence/phase24`
- `just phase24-verify`
- `git diff --check`

## Acceptance Sampling

| Requirement | Sample | Expected |
|-------------|--------|----------|
| EVID-02 | Complete input packet with one row per Phase 15 scenario | accepted, retained, summarized |
| EVID-02 | Missing, duplicate, or unknown scenario row | rejected |
| EVID-02 | `source_status: pending-hardware-input`, `manual-hardware-required`, or `blocked-hardware-unavailable` with `status: passed` | rejected |
| EVID-02 | `exception-requested` without owner/rationale/evidence/revisit metadata | rejected |
| EVID-02 | Storage row without media surface, filesystem/resource behavior, failure observations, or residual risk | rejected |
| EVID-02 | Safety row missing artifact refs or residual risk | rejected |
| EVID-02 | Artifact ref outside `build/ci-evidence/phase24/` or `external://phase24/` | rejected |
| EVID-02 | Secret-bearing fields/text or raw firmware/crash payload markers | rejected |
| EVID-02 | Quick mode without real input | retained as blocked placeholder, not passed proof |

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json` declares Phase 24 schema, v1.2 statuses, required Phase 15 IDs, allowed artifact roots, and upstream row identity.
- [ ] `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` implements contract/security/wiring/quick/evidence-input modes.
- [ ] `tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` covers the acceptance samples above.
- [ ] `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` expose `phase24_verify` and `phase24_verify_tests`.

## Manual-Only Verifications

Real hardware operation remains a maintainer-supplied external evidence input. The local Phase 24 verifier validates the packet schema, coverage, redaction, retained summaries, and upstream row shape; it does not operate printers or claim physical hardware behavior from local fixtures.

## Validation Sign-Off

- [x] All tasks require automated verifier/test commands or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verification
- [x] Wave 0 covers all missing test and verifier files
- [x] No watch-mode flags
- [x] Feedback latency target: direct Python tests before `just phase24-verify`
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-23
