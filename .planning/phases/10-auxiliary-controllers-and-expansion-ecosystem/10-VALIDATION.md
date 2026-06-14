---
phase: 10
slug: auxiliary-controllers-and-expansion-ecosystem
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| **Estimated runtime** | ~60 seconds after Wave 0 verifier infrastructure exists |

---

## Sampling Rate

- **After every task commit:** Run the most focused verifier mode for the touched surface, plus affected Rust tests when `rust/crates/domain` changes.
- **After every plan wave:** Run `bazel run //tools/bazel:phase10_verify_tests`, `bazel run //tools/bazel:phase10_verify`, and the relevant Rust workflow command.
- **Before phase verification:** `just phase10-verify` must be green, and non-local simulator/hardware/manual evidence rows must remain classified honestly.
- **Max feedback latency:** 90 seconds for local deterministic checks.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 10-W0-01 | TBD | 0 | IFCE-06 | T-10-01 | Source paths and evidence classes are explicit; no anonymous retained auxiliary surface | manifest/schema unit | `python3 tools/bazel/phase10_verify.py --manifests-only` | W0 missing | pending |
| 10-W0-02 | TBD | 0 | IFCE-06 | T-10-02 | Typed Rust states reject impossible auxiliary/MMU/update combinations | Rust unit/API check | `cargo test -p buddy-domain auxiliary` and `python3 tools/bazel/phase10_verify.py --rust-only` | W0 missing | pending |
| 10-W0-03 | TBD | 0 | IFCE-06 | T-10-03 | Bazel and `just` expose deterministic Phase 10 verification | build graph smoke | `bazel query //tools/bazel:phase10_verify && bazel run //tools/bazel:phase10_verify_tests && just phase10-verify` | W0 missing | pending |
| 10-W0-04 | TBD | 0 | IFCE-06 | T-10-04 | Build/package/update rows cover prebuilt, skip-flash, descriptor, MMU firmware, crash-dump, and update surfaces without payload leakage | manifest/source audit | `python3 tools/bazel/phase10_verify.py --package-update-only` | W0 missing | pending |
| 10-W0-05 | TBD | 0 | IFCE-06 | T-10-05 | Hardware, simulator, RS485, toolchanger, dock, MMU, and long-run update proof is not overclaimed as local | evidence wording check | `python3 tools/bazel/phase10_verify.py --evidence-only` | W0 missing | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase10_auxiliary_controllers.json` - covers controller families, Dwarf, ModularBed, xBuddy Extension, and runtime states for IFCE-06.
- [ ] `tools/bazel/manifests/phase10_mmu_transport.json` - covers MMU2 availability/reporting, bootloader, UART/puppy transport, firmware resource, and update states for IFCE-06.
- [ ] `tools/bazel/manifests/phase10_modbus_rs485.json` - covers LightModbus, RS485 request/retry/timeout/skipped/error behavior, and xBuddy Extension MMU bridge timing for IFCE-06.
- [ ] `tools/bazel/manifests/phase10_toolchanger_dock_offsets.json` - covers toolchanger update/init and dock/tool offset source surfaces for IFCE-06.
- [ ] `tools/bazel/manifests/phase10_auxiliary_build_update.json` - covers CMake external projects, descriptor generation, resource paths, prebuilt binary paths, skip-flash, startup flashing, crash dump, and update evidence for IFCE-06.
- [ ] `tools/bazel/manifests/phase10_concern_dispositions.json` - covers MMU availability/reporting, xBuddy Extension H503 special handling, BuddyHeaders/error-code coupling if touched, and intentional deltas.
- [ ] `rust/crates/domain/src/auxiliary.rs` and optional `rust/crates/domain/src/auxiliary/` submodules.
- [ ] `tools/bazel/phase10_verify.py` and `tools/bazel/phase10_verify_test.py`.
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` Phase 10 wiring.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| RS485/Modbus timing on physical auxiliary bus | IFCE-06 | Requires connected Dwarf/ModularBed/xBuddy Extension or equivalent hardware/simulator evidence | Run the future hardware smoke procedure and attach logs to cutover evidence; local Phase 10 may only record source-backed evidence rows. |
| Toolchanger dock/tool offset behavior on printer hardware | IFCE-06 | Requires physical toolchanger mechanics and calibration workflow | Validate through Phase 11 cutover/hardware-smoke gate unless a Phase 10 plan adds explicit simulator or hardware artifacts. |
| Long-running auxiliary startup flashing and update recovery | IFCE-06 | Requires real firmware images, update timing, power-cycle behavior, and failure injection | Preserve source-backed contracts locally; run manual or simulator update proof before production cutover. |
| MMU behavior over live transport | IFCE-06 | Requires MMU hardware or simulator capable of protocol fault injection | Phase 10 should verify typed state and source mapping locally; live behavior stays non-local until hardware/simulator proof exists. |

---

## Validation Sign-Off

- [ ] All tasks have automated verifier commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verification.
- [ ] Wave 0 covers all missing validation references.
- [ ] No watch-mode flags.
- [ ] Feedback latency < 90 seconds for local deterministic checks.
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 is complete.

**Approval:** pending
