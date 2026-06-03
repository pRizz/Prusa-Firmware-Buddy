---
phase: 05
slug: foreign-code-unsafe-and-runtime-boundary
status: ready
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-03
---

# Phase 05 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Cargo Rust tests, standard-library Python verifier, Bazel 9.1.0 labels, and `just` facade recipes. |
| **Config file** | `Cargo.toml`, `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `justfile`, and new `tools/bazel/phase5_verify.py`. |
| **Quick run command** | `python3 tools/bazel/phase5_verify.py --quick` after Wave 0 adds the verifier. |
| **Full suite command** | `just phase5-verify` after Wave 0 adds the recipe and Bazel target. |
| **Estimated runtime** | Quick: <30 seconds after Wave 0; full local suite: ~2-4 minutes depending on Cargo and Bazel cache state. |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase5_verify.py --quick` once Wave 0 creates it, plus focused `cargo test --all-features` when Rust adapter code changes.
- **After every plan wave:** Run `just phase5-verify`.
- **Before `/gsd-verify-work`:** Run `just phase5-verify`, `just rust-format`, `just rust-lint`, `just rust-build`, `just rust-test`, `just --list`, and targeted `bazel query` for Phase 5 labels.
- **Max feedback latency:** 120 seconds for default local checks. Simulator, full embedded firmware, and hardware evidence may be classified as non-local evidence.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 0 | RUST-03, RUST-04, CORE-01, CORE-02 | T-05-01 / T-05-02 | Phase 5 verifier rejects missing inventory/audit rows, missing adapter boundary labels, and unsupported evidence claims. | verifier | `python3 tools/bazel/phase5_verify.py --quick` | no - Wave 0 | pending |
| 05-01-02 | 01 | 0 | RUST-03, CORE-01 | T-05-03 | Foreign-code inventory covers retained C, C++, ASM, generated, HAL/CMSIS, FreeRTOS, Marlin, WUI/network/filesystem/vendor, and auxiliary runtime surfaces with required fields and evidence classes. | manifest/verifier | `python3 tools/bazel/phase5_verify.py --quick` | no - Wave 0 | pending |
| 05-01-03 | 01 | 0 | RUST-04 | T-05-01 / T-05-04 | Unsafe-boundary audit covers Rust unsafe, FFI, MMIO, DMA, interrupts, linker symbols, static memory, allocator, panic, mutable statics, and retained C ABI boundaries. | manifest/verifier | `python3 tools/bazel/phase5_verify.py --quick && cargo test --all-features` | no - Wave 0 | pending |
| 05-02-01 | 02 | 1 | RUST-04, CORE-01 | T-05-03 / T-05-04 | Board adapter constructs safe host-testable contracts for MCU family, memory regions, MMIO, DMA, interrupts, and FFI boundaries without relaxing pure-domain unsafe policy. | Rust unit tests | `cargo test --all-features` | no - Wave 0 | pending |
| 05-02-02 | 02 | 1 | RUST-04, CORE-02 | T-05-02 / T-05-05 | Runtime adapter constructs safe host-testable contracts for startup, linker regions, tasks, queues, timers, static memory, allocator, and panic boundaries. | Rust unit tests | `cargo test --all-features` | no - Wave 0 | pending |
| 05-03-01 | 03 | 2 | RUST-03, RUST-04, CORE-01, CORE-02 | T-05-01 / T-05-05 | Bazel and `just` expose Phase 5 inventory, audit, adapter, and verification surfaces without claiming hardware-only evidence locally. | Bazel/query/facade | `bazel query "//tools/bazel:phase5_verify + //tools/bazel:retained_foreign_code + //tools/bazel:unsafe_boundary_audit" && just --list` | no - Wave 0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/phase5_verify.py` - verifies RUST-03, RUST-04, CORE-01, and CORE-02 manifest/static coverage.
- [ ] `tools/bazel/manifests/foreign_code_inventory.json` - machine-readable retained-code source of truth.
- [ ] `tools/bazel/manifests/unsafe_boundary_audit.json` - machine-readable unsafe/runtime boundary source of truth.
- [ ] `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md` - human-readable retained-code inventory.
- [ ] `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-UNSAFE-BOUNDARY-AUDIT.md` - human-readable unsafe/runtime audit.
- [ ] `rust/crates/board-adapter/src/{mcu,memory_region,mmio,dma,interrupt,ffi}.rs` - safe board facade contracts and host tests.
- [ ] `rust/crates/runtime-adapter/src/{startup,linker,task,queue,timer,static_memory,allocator,panic_boundary}.rs` - safe runtime contracts and host tests.
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, and `justfile` Phase 5 labels/recipes - developer-visible verification surface.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full embedded firmware startup preservation | CORE-01 | Local host checks cannot prove MCU reset/vector/clock/watchdog behavior, and `arm-none-eabi-gcc` is not currently available on PATH. | After bootstrap/toolchain availability, run the documented embedded build or simulator flow for representative STM32F4, STM32G0, and STM32H503 surfaces; record evidence class in Phase 5 verification. |
| Hardware interrupt, DMA, MMIO, and watchdog behavior | CORE-01, RUST-04 | These depend on physical MCU behavior or simulator fidelity beyond host Rust tests. | Run simulator or hardware smoke checks for representative boards; keep missing hardware as `manual-hardware-required`, not passed. |
| FreeRTOS scheduler timing and task startup ordering on hardware | CORE-02 | Host adapter tests can prove contracts, but not scheduler timing under real interrupts and board clocks. | Run simulator or hardware task-startup smoke checks once runtime integration exists; record task readiness and static memory evidence. |

---

## Validation Sign-Off

- [x] All tasks have automated verify commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing verifier/helper references.
- [x] No watch-mode flags.
- [x] Feedback latency target is below 120 seconds for default local checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-03
