---
phase: 16
slug: live-network-and-transfer-qualification
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-18
phase_lifecycle_id: 16-2026-06-18T01-09-34
---

# Phase 16 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` |
| **Config file** | `tools/bazel/manifests/phase16_live_network_evidence_contract.json` |
| **Quick run command** | `python3 tools/bazel/phase16_live_network_evidence.py --quick` |
| **Full suite command** | `just phase16-verify` |
| **Estimated runtime** | ~30 seconds after Phase 16 tooling exists |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase16_live_network_evidence_test.py` and `python3 tools/bazel/phase16_live_network_evidence.py --quick`.
- **After every plan wave:** Run `just phase16-verify`.
- **Before `/gsd-verify-work`:** `just phase16-verify` and the GSD phase verifier must be green.
- **Max feedback latency:** 60 seconds for local deterministic checks.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | LIVE-01 | T-16-01 | Connect rows cover registration, telemetry, WebSocket commands, token/fingerprint behavior, and proxy limitations without storing secrets. | unit + contract | `python3 tools/bazel/phase16_live_network_evidence_test.py` | No - Wave 0 creates | pending |
| 16-01-02 | 01 | 1 | LIVE-02 | T-16-02 | WUI rows cover HTTP API, digest/API-key auth, SNTP, mDNS, syslog, metrics, and transfer behavior with pending defaults for missing live input. | unit + contract | `python3 tools/bazel/phase16_live_network_evidence_test.py` | No - Wave 0 creates | pending |
| 16-01-03 | 01 | 1 | LIVE-03 | T-16-03 | TLS, certificate, redaction, negative protocol, long-transfer, and crash-dump rows reject forbidden secrets and overclaim wording. | unit + security negative | `python3 tools/bazel/phase16_live_network_evidence_test.py` | No - Wave 0 creates | pending |
| 16-01-04 | 01 | 1 | LIVE-01/LIVE-02/LIVE-03 | T-16-04 | Bazel, `rust_workflow.sh`, root aliases, and `just phase16-verify` execute the verifier tests before the verifier. | wiring | `just phase16-verify` | No - Wave 0 creates | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase16_live_network_evidence_contract.json` - required row coverage for `LIVE-01`, `LIVE-02`, and `LIVE-03`.
- [ ] `tools/bazel/phase16_live_network_evidence.py` - contract, security, wiring, quick, and operator-evidence modes.
- [ ] `tools/bazel/phase16_live_network_evidence_test.py` - tests for required rows, redaction, overclaim rejection, source refs, path safety, operator evidence, and workflow wiring.
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 16 Bazel/just exposure.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Approved Connect or controlled-service run | LIVE-01, LIVE-03 | Credentials and service endpoints are not committed. | Supply operator evidence JSON with external artifact refs and redacted summaries. The local verifier must keep rows pending when this input is absent. |
| WUI-capable printer or simulator endpoint with auth | LIVE-02 | Endpoint, password, API key, and digest artifacts are operator-controlled. | Supply operator evidence JSON naming the fixture, auth outcome class, transfer result, and redaction summary without raw secrets. |
| TLS/private certificate and crash-dump evidence | LIVE-03 | Private certs and raw crash dumps must not enter git. | Supply fixture names, hashes, redacted outcomes, and external artifact refs only. |

---

## Validation Sign-Off

- [x] All planned tasks have automated verify commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing validation references.
- [x] No watch-mode flags.
- [x] Feedback latency target is less than 60 seconds.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-18
