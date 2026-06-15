---
phase: 05
slug: foreign-code-unsafe-and-runtime-boundary
status: complete
nyquist_compliant: true
wave_0_complete: true
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
| **Full suite command** | `just phase5-verify` after Plan 05 adds the recipe and Bazel target. |
| **Estimated runtime** | Quick: <30 seconds after Wave 0; focused Rust crate tests: <60 seconds; full local phase gate: ~2-4 minutes depending on Cargo and Bazel cache state. |

---

## Sampling Rate

- **After every task commit:** Run the task-local automated command from the map below.
- **After Wave 0:** Run `python3 tools/bazel/phase5_verify.py --quick`.
- **After every adapter task:** Run focused `cargo test --all-features -p buddy-board-adapter` or `cargo test --all-features -p buddy-runtime-adapter`, plus `python3 tools/bazel/phase5_verify.py --quick`.
- **After Plan 05 Task 1:** Run the targeted Bazel query and `just --list`.
- **After Plan 05 Task 2:** Run `python3 -m py_compile tools/bazel/phase5_verify.py && python3 tools/bazel/phase5_verify.py --quick`.
- **Before `/gsd-verify-work`:** Run one full gate: `just phase5-verify`, followed by `just rust-format`, `just rust-lint`, `just rust-build`, `just rust-test`, `just --list`, and targeted `bazel query` for Phase 5 labels.
- **Max feedback latency:** 120 seconds for default task-local checks. Simulator, full embedded firmware, and hardware evidence remain non-local evidence classes.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 0 | RUST-03, RUST-04, CORE-01, CORE-02 | T-05-01-01 / T-05-01-06 | Phase 5 verifier exposes required fields, required retained component IDs, required unsafe surface IDs, and evidence-class checks. | verifier | `python3 -m py_compile tools/bazel/phase5_verify.py && python3 tools/bazel/phase5_verify.py --help` | no - Plan 01 creates it | green |
| 05-01-02 | 01 | 0 | RUST-03, CORE-01, CORE-02 | T-05-01-03 / T-05-01-05 / T-05-01-07 | Foreign-code inventory covers every retained Phase 5 island named by context/research, including board-clock and synchronization rows. | manifest/verifier | `python3 tools/bazel/phase5_verify.py --inventory-only` | no - Plan 01 creates it | green |
| 05-01-03 | 01 | 0 | RUST-04, CORE-01, CORE-02 | T-05-01-01 / T-05-01-02 / T-05-01-04 / T-05-01-07 | Unsafe-boundary audit covers FFI, MMIO, DMA, interrupt, linker/startup, clock-tree, static memory, allocator, panic, crash dump, queues, timers, mutexes, semaphores, and event groups. | manifest/verifier | `python3 tools/bazel/phase5_verify.py --quick` | no - Plan 01 creates it | green |
| 05-02-01 | 02 | 1 | RUST-04, CORE-01 | T-05-02-02 / T-05-02-03 / T-05-02-04 | Board adapter constructs safe host-testable MCU, board-clock, memory-region, and DMA contracts without relaxing pure-domain unsafe policy. | Rust unit tests + verifier | `cargo test --all-features -p buddy-board-adapter && python3 tools/bazel/phase5_verify.py --quick` | no - Plan 02 creates it | green |
| 05-02-02 | 02 | 1 | RUST-04, CORE-01 | T-05-02-01 / T-05-02-02 / T-05-02-07 | Board adapter constructs audited MMIO, interrupt, and FFI facades while preserving retained C/C++ behavior. | Rust unit tests + verifier | `cargo test --all-features -p buddy-board-adapter && python3 tools/bazel/phase5_verify.py --quick` | no - Plan 02 creates it | green |
| 05-03-01 | 03 | 1 | RUST-04, CORE-01 | T-05-03-01 / T-05-03-02 / T-05-03-05 | Runtime adapter models startup vectors and linker scripts for F4, G0, and H503 with non-local hardware evidence classes. | Rust unit tests + verifier | `cargo test --all-features -p buddy-runtime-adapter && python3 tools/bazel/phase5_verify.py --quick` | no - Plan 03 creates it | green |
| 05-03-02 | 03 | 1 | RUST-04, CORE-01 | T-05-03-03 / T-05-03-04 / T-05-03-05 | Runtime adapter models allocator, panic/assert, watchdog, and crash-dump boundaries without claiming local hardware proof. | Rust unit tests + verifier | `cargo test --all-features -p buddy-runtime-adapter && python3 tools/bazel/phase5_verify.py --quick` | no - Plan 03 creates it | green |
| 05-04-01 | 04 | 2 | RUST-04, CORE-02 | T-05-04-01 / T-05-04-02 | Runtime adapter models task dependencies, static task memory, queue storage, timers, and startup ordering. | Rust unit tests + verifier | `cargo test --all-features -p buddy-runtime-adapter && python3 tools/bazel/phase5_verify.py --quick` | no - Plan 04 creates it | green |
| 05-04-02 | 04 | 2 | RUST-04, CORE-02 | T-05-04-03 / T-05-04-04 / T-05-04-05 | Runtime adapter models mutex, binary semaphore, counting semaphore, event-group, and wait-condition boundaries with non-local scheduler timing evidence. | Rust unit tests + verifier | `cargo test --all-features -p buddy-runtime-adapter && python3 tools/bazel/phase5_verify.py --quick` | no - Plan 04 creates it | green |
| 05-05-01 | 05 | 3 | RUST-03, RUST-04, CORE-01, CORE-02 | T-05-05-05 | Bazel and `just` expose Phase 5 inventory, audit, retained-code, and verifier surfaces. | Bazel/query/facade | `bazel query "//tools/bazel:phase5_verify + //tools/bazel:retained_foreign_code + //tools/bazel:unsafe_boundary_audit" && just --list` | no - Plan 05 creates it | green |
| 05-05-02 | 05 | 3 | RUST-03, RUST-04, CORE-01, CORE-02 | T-05-05-01 / T-05-05-02 / T-05-05-03 / T-05-05-04 / T-05-05-06 | Verifier enforces adapter module presence, pure-crate unsafe-free posture, audited unsafe locality, board-clock/synchronization coverage, Bazel labels, just recipe, and no local hardware overclaiming. | verifier | `python3 -m py_compile tools/bazel/phase5_verify.py && python3 tools/bazel/phase5_verify.py --quick` | no - Plan 05 updates it | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [x] `tools/bazel/phase5_verify.py` - verifies RUST-03, RUST-04, CORE-01, and CORE-02 manifest/static coverage.
- [x] `tools/bazel/manifests/foreign_code_inventory.json` - machine-readable retained-code source of truth.
- [x] `tools/bazel/manifests/unsafe_boundary_audit.json` - machine-readable unsafe/runtime boundary source of truth.
- [x] `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md` - human-readable retained-code inventory.
- [x] `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-UNSAFE-BOUNDARY-AUDIT.md` - human-readable unsafe/runtime audit.
- [x] `rust/crates/board-adapter/src/{mcu,clock,memory_region,mmio,dma,interrupt,ffi}.rs` - safe board facade contracts and host tests.
- [x] `rust/crates/runtime-adapter/src/{startup,linker,allocator,panic_boundary,task,queue,timer,static_memory,synchronization}.rs` - safe runtime contracts and host tests.
- [x] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, and `justfile` Phase 5 labels/recipes - developer-visible verification surface.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full embedded firmware startup and board-clock preservation | CORE-01 | Local host checks cannot prove MCU reset/vector/clock/watchdog behavior, and `arm-none-eabi-gcc` is not currently available on PATH. | After bootstrap/toolchain availability, run the documented embedded build or simulator flow for representative STM32F4, STM32G0, and STM32H503 surfaces; record evidence class in Phase 5 verification. |
| Hardware interrupt, DMA, MMIO, and watchdog behavior | CORE-01, RUST-04 | These depend on physical MCU behavior or simulator fidelity beyond host Rust tests. | Run simulator or hardware smoke checks for representative boards; keep missing hardware as `manual-hardware-required`, not passed. |
| FreeRTOS scheduler timing, synchronization wakeups, and task startup ordering on hardware | CORE-02 | Host adapter tests can prove contracts, but not scheduler timing, semaphore wakeups, event-group ordering, or mutex behavior under real interrupts and board clocks. | Run simulator or hardware task/synchronization startup smoke checks once runtime integration exists; record task readiness and static memory evidence. |

---

## Validation Sign-Off

- [x] All 11 actual tasks across 5 plans have automated verify commands.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing verifier/helper references.
- [x] No watch-mode flags.
- [x] Feedback latency target is below 120 seconds for default local checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-03
