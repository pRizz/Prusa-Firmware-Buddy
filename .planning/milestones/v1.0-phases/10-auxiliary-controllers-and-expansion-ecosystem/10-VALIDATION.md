---
phase: 10
slug: auxiliary-controllers-and-expansion-ecosystem
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-14
phase_lifecycle_id: 10-2026-06-14T15-08-30
lifecycle_mode: yolo
---

# Phase 10 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib verifier tests plus Rust unit tests plus Bazel `sh_binary` labels |
| **Config file** | `.planning/config.json`, `Cargo.toml`, `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, and `justfile` |
| **Quick run command** | `python3 tools/bazel/phase10_verify.py --quick` |
| **Full suite command** | `just phase10-verify` |
| **Estimated runtime** | ~60 seconds for local deterministic checks after Bazel analysis and Rust cache warm-up |

---

## Sampling Rate

- **After every task commit:** Run the most focused verifier mode for the touched surface, plus affected Rust tests when `rust/crates/domain` changes.
- **After every plan wave:** Run `bazel run //tools/bazel:phase10_verify_tests`, `bazel run //tools/bazel:phase10_verify`, and the relevant Rust workflow command.
- **Before phase verification:** `just phase10-verify` must be green, and non-local simulator, hardware, RS485, MMU live-transport, Toolchanger, long-running update, and final replacement cutover proof must remain outside local claims.
- **Max feedback latency:** 90 seconds for local deterministic checks after tool caches are warm.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 10-01 | 1 | IFCE-06 | T-10-01-01..T-10-01-06 | Controller, MMU, retained source paths, and evidence classes are explicit; no anonymous retained auxiliary surface | manifest/source audit | `python3 tools/bazel/phase10_verify.py --manifests-only` | yes | green |
| 10-01-02 | 10-01 | 1 | IFCE-06 | T-10-01-01..T-10-01-06 | Modbus/RS485, xBuddy Extension bridge, Toolchanger dock, and tool-offset rows preserve source facts and non-local proof boundaries | manifest/source audit | `python3 tools/bazel/phase10_verify.py --manifests-only` | yes | green |
| 10-01-03 | 10-01 | 1 | IFCE-06 | T-10-01-01..T-10-01-06 | Build/update/prebuilt/resource/crash-dump rows name paths and labels without firmware byte content, signing-key material, credentials, MMU HEX payload values, or raw crash-dump contents | manifest/source audit | `python3 tools/bazel/phase10_verify.py --package-update-only` | yes | green |
| 10-02-01 | 10-02 | 1 | IFCE-06 | T-10-02-01..T-10-02-06 | Failing Rust tests define row ID, evidence, runtime, MMU, Modbus, dock, tool-offset, fault, and product/controller compatibility behavior first | Rust unit/API check | `cargo test -p buddy-domain --all-features auxiliary` | yes | green |
| 10-02-02 | 10-02 | 1 | IFCE-06 | T-10-02-01..T-10-02-06 | Typed Rust states reject impossible auxiliary/MMU/update/proof combinations without runtime hardware or payload effects | Rust unit/API check | `python3 tools/bazel/phase10_verify.py --rust-only` | yes | green |
| 10-03-01 | 10-03 | 2 | IFCE-06 | T-10-03-01..T-10-03-06 | Verifier regression tests reject missing rows, missing Rust surface, proof overclaims, and sensitive artifact markers | Python unittest | `python3 tools/bazel/phase10_verify_test.py` | yes | green |
| 10-03-02 | 10-03 | 2 | IFCE-06 | T-10-03-01..T-10-03-06 | Aggregate verifier checks manifests, Rust API, package/update evidence, proof scope, lifecycle metadata, and security markers | Python verifier | `python3 tools/bazel/phase10_verify.py --security-only` | yes | green |
| 10-04-01 | 10-04 | 3 | IFCE-06 | T-10-04-01..T-10-04-06 | Bazel labels and `just phase10-verify` expose deterministic Phase 10 verification with tests before aggregate verification | build graph smoke | `bazel query "//tools/bazel:phase10_verify + //tools/bazel:phase10_verify_tests + //tools/bazel:phase10_auxiliary_build_update_manifest + //:phase10_verify + //:phase10_verify_tests + //:phase10_auxiliary_controller_docs"` | yes | green |
| 10-04-02 | 10-04 | 3 | IFCE-06 | T-10-04-01..T-10-04-06 | Validation sign-off records local evidence and excludes hardware, simulator, RS485, MMU live-transport, Toolchanger, long-running update, and final replacement cutover proof from local claims | validation/lifecycle audit | `just phase10-verify` | yes | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [x] `tools/bazel/manifests/phase10_auxiliary_controllers.json` - covers controller families, Dwarf, ModularBed, xBuddy Extension, and runtime states for IFCE-06.
- [x] `tools/bazel/manifests/phase10_mmu_transport.json` - covers MMU2 availability/reporting, bootloader, UART/puppy transport, firmware resource, and update states for IFCE-06.
- [x] `tools/bazel/manifests/phase10_modbus_rs485.json` - covers LightModbus, RS485 request/retry/timeout/skipped/error behavior, and xBuddy Extension MMU bridge timing for IFCE-06.
- [x] `tools/bazel/manifests/phase10_toolchanger_dock_offsets.json` - covers Toolchanger update/init and dock/tool offset source surfaces for IFCE-06.
- [x] `tools/bazel/manifests/phase10_auxiliary_build_update.json` - covers CMake external projects, descriptor generation, resource paths, prebuilt binary paths, skip-flash, startup flashing, crash dump, and update evidence for IFCE-06.
- [x] `tools/bazel/manifests/phase10_concern_dispositions.json` - covers MMU availability/reporting, xBuddy Extension H503 special handling, BuddyHeaders/error-code coupling if touched, and intentional deltas.
- [x] `rust/crates/domain/src/auxiliary.rs` and optional `rust/crates/domain/src/auxiliary/` submodules.
- [x] `tools/bazel/phase10_verify.py` and `tools/bazel/phase10_verify_test.py`.
- [x] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` Phase 10 wiring.

---

## Final Automated Evidence

| Command | Local Outcome |
|---------|---------------|
| `python3 tools/bazel/phase10_verify.py --manifests-only` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `python3 tools/bazel/phase10_verify.py --rust-only` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `python3 tools/bazel/phase10_verify.py --package-update-only` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `python3 tools/bazel/phase10_verify.py --evidence-only` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `python3 tools/bazel/phase10_verify.py --security-only` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `python3 tools/bazel/phase10_verify.py --wiring-only` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `python3 tools/bazel/phase10_verify_test.py` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `bazel query "//tools/bazel:phase10_verify + //tools/bazel:phase10_verify_tests + //tools/bazel:phase10_auxiliary_build_update_manifest + //:phase10_verify + //:phase10_verify_tests + //:phase10_auxiliary_controller_docs"` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `bazel run //tools/bazel:phase10_verify_tests` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `bazel run //tools/bazel:phase10_verify` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `just phase10-verify` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `cargo fmt --all -- --check` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `cargo clippy --all-targets --all-features -- -D warnings` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `cargo build --all-targets --all-features` | Required final Plan 10-04 evidence; exits 0 in the local verification run |
| `cargo test --all-features` | Required final Plan 10-04 evidence; exits 0 in the local verification run |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| RS485/Modbus timing on physical buses | IFCE-06 | Requires connected Dwarf, ModularBed, xBuddy Extension, or equivalent hardware/simulator-flow evidence | Run the future hardware-smoke procedure and attach logs to Phase 11 cutover evidence; local Phase 10 records only source-backed rows and verifier checks. |
| physical toolchanger dock and offset behavior | IFCE-06 | Requires physical Toolchanger mechanics, dock calibration, and tool-offset calibration motion | Validate through Phase 11 cutover/hardware-smoke gate unless a later plan adds explicit simulator or hardware artifacts. |
| Long-running auxiliary startup flashing and update recovery | IFCE-06 | Requires real firmware images, update timing, power-cycle behavior, and failure injection | Preserve source-backed contracts locally; run manual-hardware-required or simulator update proof before production replacement. |
| live MMU behavior over live transport | IFCE-06 | Requires MMU hardware or simulator capable of protocol fault injection | Phase 10 verifies typed state and source mapping locally; live behavior stays non-local until hardware/simulator proof exists. |
| simulator auxiliary flows | IFCE-06 | Requires a configured simulator scenario with auxiliary-controller, MMU, and Toolchanger coverage | Keep `simulator-flow` rows classified as non-local until the simulator emits artifacts that can be checked in or referenced by Phase 11 evidence. |
| final replacement cutover proof | IFCE-06, VERF-04, VERF-05 | Requires the full parity pyramid across Rust+Bazel outputs, simulator runs, hardware smoke, and release approval | Phase 10 does not claim final replacement cutover proof; this remains Phase 11 evidence. |

---

## Threat Coverage

| Threat Group | Coverage |
|--------------|----------|
| `T-10-01-01`..`T-10-01-06` | Manifest rows require source paths, IFCE-06 mapping, lifecycle metadata, non-local proof scope, and payload-free path-only auxiliary build/update evidence. |
| `T-10-02-01`..`T-10-02-06` | Rust domain contracts parse auxiliary row IDs, proof scopes, firmware image source names, controller/product compatibility, Modbus identities, MMU states, and controller fault classes. |
| `T-10-03-01`..`T-10-03-06` | Phase 10 verifier checks manifests, Rust API surface, validation notes, proof overclaims, forbidden sensitive markers, and subprocess execution without shell expansion. |
| `T-10-04-01`..`T-10-04-06` | Bazel and `just` wiring expose `phase10_verify`, `phase10_verify_tests`, `phase10_auxiliary_build_update_manifest`, `phase10_auxiliary_controller_docs`, fixed workflow dispatch, and bounded local verification. |

---

## Validation Sign-Off

- [x] All tasks have automated verifier commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verification.
- [x] Wave 0 covers all missing validation references.
- [x] No watch-mode flags.
- [x] Feedback latency target remains < 90 seconds for local deterministic checks after warm-up.
- [x] `nyquist_compliant: true` set in frontmatter after Wave 0 is complete.

**Approval:** complete for local Phase 10 source-backed evidence; non-local hardware, simulator, RS485, MMU live-transport, Toolchanger, long-running update, and final replacement cutover proof remain outside local claims.
