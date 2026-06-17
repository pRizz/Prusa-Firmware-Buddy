---
phase: 15
slug: hardware-safety-and-media-qualification
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-17
lifecycle_mode: yolo
phase_lifecycle_id: 15-2026-06-17T22-53-45
---

# Phase 15 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` |
| **Config file** | none - Phase 15 verifier tests run directly |
| **Quick run command** | `python3 tools/bazel/phase15_hardware_evidence_test.py && python3 tools/bazel/phase15_hardware_evidence.py --quick` |
| **Full suite command** | `just phase15-verify` |
| **Estimated runtime** | ~10 seconds after Wave 0 files exist |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase15_hardware_evidence_test.py && python3 tools/bazel/phase15_hardware_evidence.py --quick`
- **After every plan wave:** Run `bazel run //tools/bazel:phase15_verify_tests`, `bazel run //tools/bazel:phase15_verify`, and `git diff --check`
- **Before `/gsd-verify-work`:** `just phase15-verify` and lifecycle validation must be green
- **Max feedback latency:** 30 seconds for local contract/dry-run checks

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | HARD-01 | T-15-01 | Hardware matrix rows cannot pass without explicit hardware/operator evidence. | unit / contract | `python3 tools/bazel/phase15_hardware_evidence_test.py` | no - Wave 0 creates file | pending |
| 15-01-02 | 01 | 1 | HARD-02 | T-15-02 | Safety rows keep physical proof separate from source-backed or simulator checks. | contract / security | `python3 tools/bazel/phase15_hardware_evidence.py --contract-only` | no - Wave 0 creates file | pending |
| 15-01-03 | 01 | 1 | HARD-03 | T-15-03 | Generated and operator evidence reject secrets, raw dumps, unsafe payloads, path traversal, and overclaim wording. | unit / security | `python3 tools/bazel/phase15_hardware_evidence.py --security-only` | no - Wave 0 creates file | pending |
| 15-01-04 | 01 | 1 | HARD-01,HARD-02,HARD-03 | T-15-04 | Bazel and just wiring run tests before the verifier and produce deterministic local evidence only. | integration / wiring | `just phase15-verify` | no - Wave 0 creates file | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase15_hardware_evidence_contract.json` - checked-in row-level hardware, safety, media, UI input, MMU, RS485, and toolchanger evidence contract.
- [ ] `tools/bazel/phase15_hardware_evidence.py` - contract/security/wiring/quick/operator validation for `HARD-01`, `HARD-02`, and `HARD-03`.
- [ ] `tools/bazel/phase15_hardware_evidence_test.py` - stdlib tests for required rows, source refs, statuses, path guards, metadata, secrets, overclaims, generated artifacts, and wiring.
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 15 labels, root aliases, docs filegroup, dispatch, and facade.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Supported-printer hardware smoke | HARD-01 | Requires physical printers, boards, and operator-run firmware builds. | Supply operator evidence JSON naming device/printer family, board, firmware build, operator, timestamp, scenario, result, artifact reference, and residual risk. |
| Physical storage media qualification | HARD-01,HARD-03 | USB/media insertion, removal, direct-sector transfer, and durability behavior require physical media. | Supply operator evidence JSON for each media scenario and keep raw media payloads out of committed artifacts. |
| Watchdog, thermal, motion, emergency stop, safe-output, crash recovery | HARD-02,HARD-03 | Physical timing and fault behavior cannot be proven by local source checks. | Supply redacted operator evidence with scenario ID, result, residual risk, and sanitized log references only. |
| Physical UI input | HARD-02 | Encoder, touch, and display interactions require physical device input paths. | Supply operator evidence JSON with device, input surface, scenario, result, and residual risk. |
| MMU, RS485, Modbus, toolchanger, dock/offset flows | HARD-01,HARD-02,HARD-03 | Auxiliary controller timing and mechanics require hardware combinations. | Supply operator evidence JSON with auxiliary combination, scenario, result, artifact reference, and residual risk. |

---

## Validation Sign-Off

- [x] All planned tasks must have automated verifier commands or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing local verification files
- [x] No watch-mode flags
- [x] Feedback latency target is below 30 seconds for local checks
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-17
