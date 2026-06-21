---
phase: 14
slug: simulator-evidence-gates
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-17
---

# Phase 14 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` for verifier tests; existing pytest simulator suite for real simulator execution |
| **Config file** | `tools/bazel/manifests/phase14_simulator_evidence_contract.json` |
| **Quick run command** | `python3 tools/bazel/phase14_simulator_evidence.py --quick` |
| **Full suite command** | `just phase14-verify` |
| **Estimated runtime** | ~30 seconds for deterministic dry-run/contract checks; real simulator mode depends on firmware, Mini404/QEMU, OCR/cache, and pytest runtime |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase14_simulator_evidence_test.py` and `python3 tools/bazel/phase14_simulator_evidence.py --quick`
- **After every plan wave:** Run `just phase14-verify`
- **Before `/gsd-verify-work`:** `just phase14-verify`, `git diff --check`, and lifecycle validation must be green
- **Max feedback latency:** 30 seconds for dry-run/contract checks; real simulator execution is a retained evidence path and may exceed this when firmware/simulator inputs are available

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | SIM-01, SIM-02, SIM-03 | T-14-01 | Contract rows reject overclaim and secret-bearing artifacts | unit/contract | `python3 tools/bazel/phase14_simulator_evidence_test.py` | yes - Wave 0 files exist | green |
| 14-01-02 | 01 | 1 | SIM-01, SIM-02, SIM-03 | T-14-02 | Dry-run artifacts stay under `build/ci-evidence/phase14` and record residual gates | unit/artifact | `python3 tools/bazel/phase14_simulator_evidence.py --quick` | yes - Wave 0 files exist | green |
| 14-01-03 | 01 | 1 | SIM-01, SIM-02, SIM-03 | T-14-03 | Bazel/just wiring runs tests before verifier | wiring | `just phase14-verify` | yes - Wave 0 files exist | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [x] `tools/bazel/manifests/phase14_simulator_evidence_contract.json` - scenario rows for startup, task readiness, watchdog-visible startup, G-code, GUI, storage/resource, transfer, and selected failure flows.
- [x] `tools/bazel/phase14_simulator_evidence.py` - contract verifier, deterministic dry-run artifact writer, optional simulator command builder, redaction/overclaim scanner, and wiring checks.
- [x] `tools/bazel/phase14_simulator_evidence_test.py` - stdlib regression tests for SIM coverage, source refs, skipped-node handling, artifacts, wiring, path guards, and security scans.
- [x] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 14 verifier/test labels, aliases, dispatch, and developer recipe.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real simulator execution against firmware `.bin` and adjacent `.bbf` | SIM-01, SIM-02 | Local checkout lacks active pytest deps, Mini404/QEMU, and a firmware input; deterministic dry-run mode remains the local verification gate | Bootstrap dependencies, build or provide MK4 noboot firmware, then run the Phase 14 real simulator mode documented by `tools/bazel/phase14_simulator_evidence.py --help` |
| Hardware watchdog timing, thermal/motion safety, physical media, physical UI input, MMU, RS485, and toolchanger proof | SIM-03 | Phase 14 must not mark hardware-only behavior as simulator-proven | Keep these rows classified as residual Phase 15/18 evidence and verify the Phase 14 contract rejects pass claims for them |

---

## Validation Sign-Off

- [x] All planned tasks have automated dry-run/contract verification.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing Phase 14 verifier, contract, test, and wiring references.
- [x] No watch-mode flags.
- [x] Feedback latency < 30s for deterministic dry-run/contract checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-17 for planning; implementation must keep real simulator execution explicitly separate from local dry-run pass evidence.
