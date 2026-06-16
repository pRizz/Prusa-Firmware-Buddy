---
phase: 09
slug: network-web-services-and-transfers
status: complete
nyquist_compliant: true
wave_0_complete: true
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
| **Quick run command** | `python3 tools/bazel/phase9_verify.py --quick` |
| **Full suite command** | `just phase9-verify` |
| **Estimated runtime** | less than 30 seconds for static checks; Rust clippy/build/test runtime depends on local cargo cache |

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
| 09-01-01 | 01 | 1 | IFCE-02 / IFCE-03 | T-09-01-01 / T-09-01-02 | Connect, WUI, transfer, and service contract fields are source-backed and secret-bearing fields remain named-only. | manifest verifier | `python3 tools/bazel/phase9_verify.py --manifests-only` | yes - `tools/bazel/manifests/phase9_connect_contracts.json`, `tools/bazel/manifests/phase9_wui_contracts.json` | green |
| 09-01-02 | 01 | 1 | IFCE-02 | T-09-01-03 | TLS, proxy, custom certificate, stale test, transfer, and crash dump boundaries are explicit concern dispositions before parity is claimed. | manifest verifier | `python3 tools/bazel/phase9_verify.py --manifests-only` | yes - `tools/bazel/manifests/phase9_network_concern_dispositions.json` | green |
| 09-01-03 | 01 | 1 | IFCE-02 / IFCE-03 | T-09-01-04 | Transfer and local service contracts classify media, cloud, physical network, and simulator proof as non-local when local commands did not run those environments. | manifest verifier | `python3 tools/bazel/phase9_verify.py --manifests-only` | yes - `tools/bazel/manifests/phase9_transfer_contracts.json`, `tools/bazel/manifests/phase9_network_service_contracts.json` | green |
| 09-02-01 | 02 | 1 | IFCE-02 / IFCE-03 | T-09-02-01 / T-09-02-02 | Rust domain contracts reject invalid network evidence, proof scope, row IDs, proxy, auth, service, and transfer states. | Rust unit | `python3 tools/bazel/phase9_verify.py --rust-only` | yes - `rust/crates/domain/src/network.rs` | green |
| 09-02-02 | 02 | 1 | IFCE-02 / IFCE-03 | T-09-02-03 | Phase 9 domain exports remain visible from `buddy-domain` without unsafe code. | Rust workspace verification | `cargo test --all-features` | yes - `rust/crates/domain/src/lib.rs` | green |
| 09-03-01 | 03 | 2 | IFCE-02 / IFCE-03 | T-09-03-01 / T-09-03-02 | Aggregate verifier checks manifests, Rust API shape, lifecycle metadata, redaction, Bazel/just wiring, and non-local overclaim wording. | verifier regression | `python3 tools/bazel/phase9_verify_test.py` | yes - `tools/bazel/phase9_verify.py`, `tools/bazel/phase9_verify_test.py` | green |
| 09-03-02 | 03 | 2 | IFCE-02 / IFCE-03 | T-09-03-03 / T-09-03-04 | Security-only checks reject forbidden secret markers and unsupported local proof claims across Phase 9 artifacts. | security verifier | `python3 tools/bazel/phase9_verify.py --security-only` | yes - Phase 9 manifests, negative fixtures, validation, and summaries | green |
| 09-03-03 | 03 | 2 | IFCE-02 / IFCE-03 | T-09-03-06 | Negative protocol and TLS fixtures cover custom certificates, invalid certificates, weak signatures, duplicate commands, large commands, proxy behavior, and stalled networks without live network calls. | negative fixture runner | `python3 tools/bazel/phase9_negative_fixtures.py --cases tools/bazel/fixtures/phase9_negative_network_cases.json` | yes - `tools/bazel/fixtures/phase9_negative_network_cases.json`, `tools/bazel/phase9_negative_fixtures.py` | green |
| 09-04-01 | 04 | 3 | IFCE-02 / IFCE-03 | T-09-04-01 / T-09-04-02 / T-09-04-06 | Bazel and just facade wiring route Phase 9 verifier tests before aggregate verifier and include manifests, docs, Rust sources, and negative fixture runfiles. | Bazel / just verifier | `bazel run //tools/bazel:phase9_verify_tests` | yes - `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `BUILD.bazel`, `justfile` | green |
| 09-04-02 | 04 | 3 | IFCE-02 / IFCE-03 | T-09-04-03 / T-09-04-04 / T-09-04-05 | Validation sign-off records exact local command outcomes and keeps live cloud, physical network, real TLS, simulator, media, transfer, crash dump upload, and cutover proof non-local. | aggregate verifier | `just phase9-verify` | yes - `.planning/phases/09-network-web-services-and-transfers/09-VALIDATION.md` | green |

*Status: pending / green / red / flaky. A row is `green` only after its listed automated command has passed locally or the same command is included in a passing aggregate listed below.*

---

## Final Automated Evidence

| Command | Outcome |
|---------|---------|
| `python3 tools/bazel/phase9_verify.py --manifests-only` | passed - validated all five Phase 9 manifests and source references |
| `python3 tools/bazel/phase9_verify.py --rust-only` | passed - validated `buddy-domain` Phase 9 network API shape and unsafe-code guard |
| `python3 tools/bazel/phase9_verify.py --security-only` | passed - validated redaction, overclaim, and negative fixture security guards |
| `python3 tools/bazel/phase9_verify.py --negative-fixtures-only` | passed - ran the metadata-only negative fixture validator |
| `python3 tools/bazel/phase9_negative_fixtures_test.py` | passed - ran five focused negative fixture tests |
| `python3 tools/bazel/phase9_negative_fixtures.py --cases tools/bazel/fixtures/phase9_negative_network_cases.json` | passed - validated required negative protocol/TLS fixture cases |
| `python3 tools/bazel/phase9_verify_test.py` | passed - ran twelve verifier regression tests |
| `bazel query "//tools/bazel:phase9_verify + //tools/bazel:phase9_verify_tests + //:phase9_verify + //:phase9_verify_tests + //:phase9_network_web_services_docs"` | passed - resolved all tools and root Phase 9 labels |
| `bazel run //tools/bazel:phase9_verify_tests` | passed - ran `phase9_verify_test.py` and `phase9_negative_fixtures_test.py` |
| `bazel run //tools/bazel:phase9_verify` | passed - ran aggregate Phase 9 verifier through Bazel |
| `just phase9-verify` | passed - ran verifier tests before aggregate verifier |
| `cargo fmt --all -- --check` | passed - Rust formatting check clean |
| `cargo clippy --all-targets --all-features -- -D warnings` | passed - Rust lint clean |
| `cargo build --all-targets --all-features` | passed - Rust workspace build clean |
| `cargo test --all-features` | passed - Rust workspace tests clean |

Additional quick gate:

- `python3 tools/bazel/phase9_verify.py --quick` passed after validation sign-off.

Verifier compatibility anchors retained for the existing Phase 9 verifier: `09-W0-01` through `09-W0-05` map to the exact task IDs above; exact task IDs are authoritative for this validation record.

---

## Wave 0 Requirements

- [x] `rust/crates/domain/src/network.rs` or equivalent module - checked Phase 9 Connect/WUI/transfer/network evidence types.
- [x] `tools/bazel/manifests/phase9_connect_contracts.json` - Connect/TLS/proxy/command/telemetry/transfer source rows.
- [x] `tools/bazel/manifests/phase9_wui_contracts.json` - WUI endpoint/auth/static/resource rows.
- [x] `tools/bazel/manifests/phase9_transfer_contracts.json` - single-slot/range/encryption/recovery/error rows.
- [x] `tools/bazel/manifests/phase9_network_service_contracts.json` - SNTP/mDNS/DNS/metrics/syslog rows.
- [x] `tools/bazel/manifests/phase9_network_concern_dispositions.json` - TLS/proxy/transfer/auth/stale-test concern rows.
- [x] `tools/bazel/phase9_verify.py` and `tools/bazel/phase9_verify_test.py` - schema, source, redaction, overclaim, Bazel label, lifecycle, and concern-disposition checks.
- [x] `tools/bazel/fixtures/phase9_negative_network_cases.json`, `tools/bazel/phase9_negative_fixtures.py`, and `tools/bazel/phase9_negative_fixtures_test.py` - negative protocol/TLS fixture coverage.
- [x] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, and `justfile` - Phase 9 verifier/test labels and recipe.

---

## Manual-Only Verifications

| Behavior | Requirement | Evidence Class | Why Manual | Test Instructions |
|----------|-------------|----------------|------------|-------------------|
| Live Prusa Connect registration and command channel | IFCE-02 | manual-hardware-required | Requires printer/network credentials and live Connect environment | Register a supported printer, observe token/fingerprint persistence, telemetry/events, WebSocket command handling, and download initiation against the approved cloud or test service |
| Physical Ethernet/Wi-Fi network behavior | IFCE-02 / IFCE-03 | hardware-smoke | Requires hardware network module, AP/router conditions, and printer runtime | Exercise DHCP/static settings, DNS, Connect, WUI, SNTP, mDNS, metrics, and syslog on supported hardware |
| Simulator network flows | IFCE-02 / IFCE-03 | simulator-flow | Requires simulator networking setup and reference flow artifacts not produced by local static verification | Run simulator Connect, PrusaLink/WUI, DNS, SNTP, metrics, syslog, and transfer flows with captured logs and expected reference outcomes |
| Real TLS handshakes and custom certificate provisioning | IFCE-02 | manual-hardware-required | Requires approved TLS endpoint, certificate provisioning path, and captured handshake evidence | Exercise built-in trust and `/internal/connect/connect.der` provisioning with valid, missing, and invalid certificate scenarios against an approved endpoint |
| USB/media race and direct-sector transfer behavior | IFCE-02 / IFCE-03 | manual-hardware-required | Requires removable media timing and block-device behavior not available in local unit tests | Run transfer/download start, monitor, interruption, unplug/replug, recovery, and failure scenarios on representative media |
| Long-running stalled network transfers | IFCE-02 / IFCE-03 | manual-hardware-required | Requires simulator or hardware network fault injection | Start range/encrypted downloads, inject stalls/timeouts/proxy failures, and verify recovery/error semantics match reference firmware |
| Crash dump upload approval and redaction proof | IFCE-02 | manual-hardware-required | Requires explicit user consent, TLS evidence, and redaction artifacts beyond this local static gate | Run only in an approved crash-dump validation plan with consent and redaction records |
| Final Rust+Bazel cutover proof | VERF-04 / VERF-05 | manual-hardware-required | Belongs to Phase 11 parity pyramid and cutover evidence | Complete the Phase 11 cutover evidence matrix before demoting the reference path |

Live Prusa Connect registration, live WebSocket commands, real TLS handshakes, physical Ethernet/Wi-Fi, simulator network flows, USB/media races, direct-sector media behavior, long-running stalled transfers, crash dump upload approval, and final cutover proof remain non-local evidence unless concrete run artifacts are recorded.

Docker metrics collector, live metrics service, proxy authentication, transfer concurrency redesign, broader TLS capability, auxiliary-controller network/update behavior, and Phase 11 cutover were not marked locally passed by Phase 9.

---

## Validation Sign-Off

- [x] All tasks have automated verify commands or explicit non-local evidence classification.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify after Wave 0.
- [x] Wave 0 covers all missing Phase 9 verifier/domain references.
- [x] Negative protocol/TLS fixtures are included in Bazel runfiles and aggregate verification.
- [x] No watch-mode flags.
- [x] Feedback latency target is less than 30 seconds for local static checks after Wave 0.
- [x] `nyquist_compliant: true` set in frontmatter.
- [x] `status: complete` set in frontmatter.
- [x] `wave_0_complete: true` set in frontmatter.
- [x] `phase_lifecycle_id: 9-2026-06-14T02-15-21` preserved.

**Approval:** approved 2026-06-14
