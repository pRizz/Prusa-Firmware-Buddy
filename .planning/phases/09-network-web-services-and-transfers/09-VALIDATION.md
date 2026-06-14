---
phase: 09
slug: network-web-services-and-transfers
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-14
phase_lifecycle_id: 9-2026-06-14T02-15-21
lifecycle_mode: yolo
---

# Phase 09 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib verifier tests, Rust unit tests, Bazel `shell_binary`, and existing Catch2 host-test references |
| **Config file** | `.planning/config.json`, `tools/bazel/BUILD.bazel`, `Cargo.toml`, `justfile` |
| **Quick run command** | `bazel run //tools/bazel:phase9_verify_tests && bazel run //tools/bazel:phase9_verify` after Wave 0 creates the targets |
| **Full suite command** | `just phase9-verify` after Wave 0 adds the recipe |
| **Estimated runtime** | less than 30 seconds after Wave 0 |

---

## Sampling Rate

- **After every task commit:** Run `cargo test -p buddy-domain network` for Rust domain changes and `bazel run //tools/bazel:phase9_verify_tests` for verifier changes after the targets exist.
- **After every plan wave:** Run `bazel run //tools/bazel:phase9_verify_tests && bazel run //tools/bazel:phase9_verify`.
- **Before `/gsd-verify-work`:** Run `just phase9-verify`, `just bazel-query`, and relevant Rust checks.
- **Max feedback latency:** less than 30 seconds for local verifier/domain checks after Wave 0.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | IFCE-02 / IFCE-03 | T-09-01 / T-09-02 | Secret-bearing network fields are named only, never value-bearing | verifier regression | `bazel run //tools/bazel:phase9_verify_tests` | no - Wave 0 creates | pending |
| 09-01-02 | 01 | 1 | IFCE-02 | T-09-03 | Custom cert/proxy/TLS concerns have explicit dispositions before parity is claimed | verifier regression | `bazel run //tools/bazel:phase9_verify_tests` | no - Wave 0 creates | pending |
| 09-02-01 | 02 | 1 | IFCE-02 / IFCE-03 | T-09-04 | Rust domain contracts reject invalid network evidence, proxy, auth, and transfer states | Rust unit | `cargo test -p buddy-domain network` | no - Wave 0 creates | pending |
| 09-03-01 | 03 | 2 | IFCE-02 / IFCE-03 | T-09-05 | Aggregate verifier rejects overclaimed live cloud, hardware, media, simulator, and cutover proof | Bazel / just verifier | `just phase9-verify` | no - Wave 0 creates | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `rust/crates/domain/src/network.rs` or equivalent module - checked Phase 9 Connect/WUI/transfer/network evidence types.
- [ ] `tools/bazel/manifests/phase9_connect_contracts.json` - Connect/TLS/proxy/command/telemetry/transfer source rows.
- [ ] `tools/bazel/manifests/phase9_wui_contracts.json` - WUI endpoint/auth/static/resource rows.
- [ ] `tools/bazel/manifests/phase9_transfer_contracts.json` - single-slot/range/encryption/recovery/error rows.
- [ ] `tools/bazel/manifests/phase9_network_service_contracts.json` - SNTP/mDNS/DNS/metrics/syslog rows.
- [ ] `tools/bazel/manifests/phase9_network_concern_dispositions.json` - TLS/proxy/transfer/auth/stale-test concern rows.
- [ ] `tools/bazel/phase9_verify.py` and `tools/bazel/phase9_verify_test.py` - schema, source, redaction, overclaim, Bazel label, lifecycle, and concern-disposition checks.
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, and `justfile` - Phase 9 verifier/test labels and recipe.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live Prusa Connect registration and command channel | IFCE-02 | Requires printer/network credentials and live Connect environment | Register a supported printer, observe token/fingerprint persistence, telemetry/events, WebSocket command handling, and download initiation against the approved cloud or test service |
| Physical Ethernet/Wi-Fi network behavior | IFCE-02 / IFCE-03 | Requires hardware network module, AP/router conditions, and printer runtime | Exercise DHCP/static settings, DNS, Connect, WUI, SNTP, mDNS, metrics, and syslog on supported hardware |
| USB/media race and direct-sector transfer behavior | IFCE-02 / IFCE-03 | Requires removable media timing and block-device behavior not available in local unit tests | Run transfer/download start, monitor, interruption, unplug/replug, recovery, and failure scenarios on representative media |
| Long-running stalled network transfers | IFCE-02 / IFCE-03 | Requires simulator or hardware network fault injection | Start range/encrypted downloads, inject stalls/timeouts/proxy failures, and verify recovery/error semantics match reference firmware |

---

## Validation Sign-Off

- [x] All tasks have automated verify commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify after Wave 0.
- [x] Wave 0 covers all missing Phase 9 verifier/domain references.
- [x] No watch-mode flags.
- [x] Feedback latency target is less than 30 seconds for local checks after Wave 0.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-14
