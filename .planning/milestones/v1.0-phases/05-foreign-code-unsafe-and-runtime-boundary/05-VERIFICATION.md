---
phase: 05-foreign-code-unsafe-and-runtime-boundary
verified: 2026-06-03T21:16:28Z
status: passed
score: "23/23 must-haves verified"
generated_by: gsd-verifier
lifecycle_mode: yolo
phase_lifecycle_id: 5-2026-06-03T12-58-01
generated_at: 2026-06-03T21:16:28Z
lifecycle_validated: true
overrides_applied: 0
deferred:
  - truth: "Simulator/hardware proof of actual MCU clock, interrupt, DMA, watchdog, mutex timing, semaphore wakeup, event-group ordering, and scheduler timing behavior."
    addressed_in: "Phase 11"
    evidence: "Phase 11 success criteria require a parity pyramid with simulator flows and hardware smoke gates; Phase 5 context D-08, D-12, and D-18 require these behaviors to stay classified as non-local evidence."
---

# Phase 5: Foreign Code, Unsafe, and Runtime Boundary Verification Report

**Phase Goal:** Rust firmware can boot and orchestrate supported runtime shells through explicit retained-code and unsafe boundaries.
**Verified:** 2026-06-03T21:16:28Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Developer can inspect a foreign-code inventory for every retained C, C++, ASM, generated, and vendor component with reason, source/version, ownership boundary, safe facade, and replacement posture. | VERIFIED | `foreign_code_inventory.json` has schema version 1, phase 05, 31 components, required IDs including STM32 startup/linker, HAL/CMSIS, FreeRTOS, Marlin, WUI/network, filesystems, generated assets, and auxiliary runtime surfaces. Markdown inventory exists and Bazel labels expose it. |
| 2 | Developer can audit every `unsafe`, FFI, MMIO, DMA, interrupt, linker-symbol, static-memory, allocator, and panic-boundary surface inside narrow adapter crates with documented invariants and tests. | VERIFIED | `unsafe_boundary_audit.json` has 21 surfaces, required kinds, exact adapter `source_path` rows, and requirement IDs. `phase5_verify.py --all` passed, including unsafe locality and scanner regression checks. |
| 3 | Rust firmware preserves STM32 startup, memory layout, vector/interrupt behavior, board clocks, HAL/CMSIS integration, watchdog behavior, and linker-controlled sections for supported MCU families. | VERIFIED | Phase 5 preserves this at the boundary-contract level: retained startup/linker/HAL paths are inventoried, `clock.rs`, `mcu.rs`, `startup.rs`, `linker.rs`, and `panic_boundary.rs` model STM32F4, STM32G0, and STM32H503 xBuddy Extension surfaces, and tests passed. Hardware proof is correctly classified as non-local evidence. |
| 4 | Rust firmware preserves FreeRTOS task orchestration, task dependency readiness, static task memory assumptions, synchronization behavior, queues, timers, and startup ordering for master and auxiliary firmware. | VERIFIED | `task.rs`, `static_memory.rs`, `queue.rs`, `timer.rs`, and `synchronization.rs` expose typed FreeRTOS contracts for master and auxiliary personalities. `cargo test --all-features` ran 32 runtime-adapter tests, including task masks, static memory, timers, queues, and synchronization evidence classes. |
| 5 | Developer can run a local Phase 5 verifier before adapter implementation depends on manifests. | VERIFIED | `tools/bazel/phase5_verify.py --all` passed and prints the required success line. |
| 6 | Developer can inspect every retained runtime island named by context/research through explicit inventory rows. | VERIFIED | Inventory contains 31 component IDs, including startup/linker, clock tree, HAL/CMSIS, FreeRTOS, synchronization wrappers, master and auxiliary runtime shells, WUI/network/filesystem, generated assets, and puppy auxiliary runtime. |
| 7 | Developer can inspect every unsafe/runtime boundary through explicit audit rows. | VERIFIED | Audit manifest contains all required surface IDs from FFI through watchdog, including allocator, static memory, mutex, semaphore, event group, wait condition, and task dependency readiness. |
| 8 | Local verification distinguishes manifest/static checks from simulator, hardware-smoke, and manual-hardware-required evidence. | VERIFIED | Audit text and Markdown include `local manifest/static/Rust checks`, `simulator-flow`, `hardware-smoke`, and `manual-hardware-required`; overclaim grep found no forbidden local hardware-pass phrases. |
| 9 | Developer can construct board/HAL/MMIO/DMA/interrupt/FFI contracts from validated profile data instead of unchecked primitives. | VERIFIED | Board adapter modules expose typed constructors and rejection tests for profiles, memory regions, DMA visibility, interrupt priority, FFI symbols, and MMIO register addresses. |
| 10 | STM32F4, STM32G0, and STM32H503 xBuddy Extension runtime surfaces are distinguishable in the board adapter. | VERIFIED | `McuFamily::Stm32H503XbuddyExtension`, profile mapping tests, and `BoardClockTree` family-specific evidence are present. |
| 11 | Board clock-tree evidence for supported MCU families is typed contract data. | VERIFIED | `BoardClockTree` maps STM32F4, STM32G0, and STM32H503 xBuddy Extension to source evidence and non-local clock evidence wording. |
| 12 | DMA-visible memory and CCMRAM are not interchangeable in safe constructors. | VERIFIED | `DmaBufferRegion::new` rejects `CoreCoupledRam` and accepts only `DmaAccessibleRam`; tests passed. |
| 13 | Board-adapter unsafe occurrences are limited to audited adapter modules. | VERIFIED | Unsafe grep found real unsafe operations only in `board-adapter/src/mmio.rs`; audit manifest includes that exact source path, and verifier unsafe locality passed. |
| 14 | Developer can inspect startup, vector, linker-section, allocator, panic/assert, watchdog, and crash-dump contracts without changing retained startup assembly or linker scripts. | VERIFIED | Runtime adapter modules exist and are substantive; audit rows point to retained startup/linker/panic/watchdog/crash-dump surfaces while Rust code remains contract-only. |
| 15 | STM32F4, STM32G0, and STM32H503 startup/linker surfaces remain distinct contract data. | VERIFIED | `StartupSurface` and `BootModeLinkerScript` tests cover F4 boot/noboot, G0 auxiliary, and H503 wrapper linker scripts. |
| 16 | Runtime contracts classify hardware-only startup, watchdog, clock, and crash-dump evidence honestly. | VERIFIED | `startup.rs`, `panic_boundary.rs`, audit rows, and Markdown use simulator/hardware/manual evidence classes; no local hardware-proof overclaim found. |
| 17 | Developer can inspect FreeRTOS task identity, dependency readiness, static task memory, queues, timers, mutexes, semaphores, event groups, wait conditions, and startup ordering as typed Rust data. | VERIFIED | Runtime adapter exports all Plan 04 modules and contracts; runtime-adapter tests cover the named behaviors. |
| 18 | Master-board and auxiliary runtime personalities are represented, including Dwarf, ModularBed, and xBuddy Extension task/startup surfaces. | VERIFIED | `task.rs`, `startup.rs`, `linker.rs`, and `static_memory.rs` contain Dwarf, ModularBed, and xBuddy Extension profile tests and contract data. |
| 19 | Runtime synchronization contracts classify scheduler and wakeup timing as non-local evidence. | VERIFIED | `synchronization.rs` exposes `SimulatorFlow`, `HardwareSmoke`, and `ManualHardwareRequired`; tests assert non-local scheduler evidence. |
| 20 | Developer can run Phase 5 verification through `bazel run //tools/bazel:phase5_verify` and `just phase5-verify`. | VERIFIED | `just phase5-verify` passed through Bazel and ran `//tools/bazel:phase5_verify`; direct Bazel labels query also passed. |
| 21 | Developer can query retained-code inventory and unsafe-boundary audit labels through Bazel. | VERIFIED | Bazel query returned `//tools/bazel:retained_foreign_code`, `//tools/bazel:unsafe_boundary_audit`, and root aliases. |
| 22 | The verifier checks adapter modules, board-clock contracts, synchronization contracts, unsafe locality, manifest coverage, Bazel labels, just recipes, and Rust fmt/lint/build/tests. | VERIFIED | `phase5_verify.py` defines `check_adapter_surface`, `check_bazel_surface`, `check_just_surface`, `check_no_hardware_overclaim`, and `check_rust_toolchain`; `--all` passed. |
| 23 | Pure crates remain unsafe-free while audited adapter crates are the only allowed unsafe surfaces. | VERIFIED | `buddy-domain`, `buddy-application`, and `buddy-runtime-adapter` contain `#![forbid(unsafe_code)]`; unsafe scan found audited MMIO operations only in `board-adapter/src/mmio.rs`. |

**Score:** 23/23 truths verified

### Deferred Items

Items not yet locally proven but explicitly classified as later non-local evidence, not Phase 5 blockers.

| # | Item | Addressed In | Evidence |
|---|------|-------------|----------|
| 1 | Actual MCU clock, interrupt, DMA, watchdog, mutex timing, semaphore wakeup, event-group ordering, and scheduler timing proof. | Phase 11 | Phase 11 requires simulator flows and hardware smoke gates; Phase 5 context D-08/D-12/D-18 and audit artifacts require non-local evidence classification. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tools/bazel/phase5_verify.py` | Phase 5 static and aggregate verifier | VERIFIED | 797 lines; contains schema checks, adapter checks, unsafe scanner, Bazel/just checks, overclaim guard, and Rust toolchain checks. |
| `tools/bazel/manifests/foreign_code_inventory.json` | Machine-readable retained foreign-code inventory | VERIFIED | 31 components; includes required IDs and RUST-03/CORE-01/CORE-02 mapping. |
| `tools/bazel/manifests/unsafe_boundary_audit.json` | Machine-readable unsafe/runtime audit | VERIFIED | 21 surfaces; includes required surface IDs, evidence classes, exact source paths, and RUST-04/CORE mappings. |
| `05-FOREIGN-CODE-INVENTORY.md` | Human-readable retained-code inventory | VERIFIED | Contains matching row IDs and xBuddy Extension STM32H503 evidence. |
| `05-UNSAFE-BOUNDARY-AUDIT.md` | Human-readable unsafe/runtime audit | VERIFIED | Contains all required evidence classes and local-vs-non-local evidence section. |
| `rust/crates/board-adapter/src/*.rs` | Board/HAL/MMIO/DMA/interrupt/FFI contracts | VERIFIED | All Plan 02 modules exist, are exported by `lib.rs`, and are covered by cargo tests. |
| `rust/crates/runtime-adapter/src/*.rs` | Startup/linker/allocator/panic/FreeRTOS contracts | VERIFIED | All Plan 03 and Plan 04 modules exist, are exported by `lib.rs`, and are covered by cargo tests. |
| `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` | Bazel and just Phase 5 verification surfaces | VERIFIED | Root aliases, tool labels, workflow dispatch, and `phase5-verify` recipe are present and pass. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `phase5_verify.py` | `foreign_code_inventory.json` | JSON manifest validation | WIRED | Pattern `foreign_code_inventory.json` present; direct verifier passed. |
| `phase5_verify.py` | `unsafe_boundary_audit.json` | JSON manifest validation | WIRED | Pattern `unsafe_boundary_audit.json` present; direct verifier passed. |
| `unsafe_boundary_audit.json` | `board-adapter/src/mmio.rs` | Exact `source_path` audit row | WIRED | Exact source path present; unsafe operations are audited. |
| `unsafe_boundary_audit.json` | `runtime-adapter/src/synchronization.rs` | Exact `source_path` audit row | WIRED | Exact source path present; synchronization surface IDs present. |
| `unsafe_boundary_audit.json` | `runtime-adapter/src/allocator.rs` | `allocator-heap-contracts` row | WIRED | Exact row present and verifier enforces it. |
| `unsafe_boundary_audit.json` | `runtime-adapter/src/static_memory.rs` | `static-task-memory-contracts` row | WIRED | Exact row present and verifier enforces it. |
| `board-adapter/src/lib.rs` | `board-adapter/src/mcu.rs` | Public module export | WIRED | `pub mod mcu` present. |
| `runtime-adapter/src/task.rs` | `include/tasks.hpp` | TaskDeps names modeled | WIRED | `bootstrap_done` and task dependency contracts present. |
| `runtime-adapter/src/synchronization.rs` | `src/freertos/mutex.cpp` and related wrappers | Audit IDs and retained evidence | WIRED | `freertos-mutex-contracts`, semaphore, event-group, and wait-condition contracts present. |
| `justfile` | `//tools/bazel:phase5_verify` | `phase5-verify` recipe | WIRED | `just phase5-verify` passed through Bazel. |
| `rust_workflow.sh` | `phase5_verify.py` | `phase5_verify)` dispatch | WIRED | Dispatch calls `python3 tools/bazel/phase5_verify.py --all`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| Manifests and adapter contracts | Static contract rows and typed profile-derived contract values | JSON manifests plus `ProductProfile`-based Rust constructors | Yes | VERIFIED - no dynamic UI/API data flow; contract data is parsed from manifests or validated Rust profiles and exercised by tests. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Aggregate Phase 5 verifier passes | `PATH=~/.cargo/bin:/opt/homebrew/bin:... python3 tools/bazel/phase5_verify.py --all` | Printed `Phase 5 runtime boundary verification passed` | PASS |
| Developer facade runs Phase 5 gate | `just phase5-verify` | Bazel built and ran `//tools/bazel:phase5_verify`; verifier passed | PASS |
| Rust tests pass independently | `cargo test --all-features` | 62 unit tests passed across application, board-adapter, domain, and runtime-adapter; doc-test harnesses passed with 0 doctests | PASS |
| Bazel labels are queryable | `bazel query "//tools/bazel:phase5_verify + //tools/bazel:retained_foreign_code + //tools/bazel:unsafe_boundary_audit + //:phase5_verify + //:retained_foreign_code + //:unsafe_boundary_audit"` | Returned all six labels | PASS |
| Artifact markers are present | Local Python artifact-pattern check | 26/26 plan artifact markers passed | PASS |
| Plan key links are present | Local Python key-link check | 17/17 key-link patterns passed | PASS |

Environment note: one first attempt at `python3 tools/bazel/phase5_verify.py --all` failed because the inherited shell PATH did not include `~/.cargo/bin`; rerunning with the full tool PATH passed. The failure was tool discovery, not implementation behavior.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| RUST-03 | 05-01, 05-05 | Foreign-code inventory for retained C/C++/ASM/generated/vendor components. | SATISFIED | Inventory manifest has 31 components and Bazel labels expose retained-code artifacts. |
| RUST-04 | 05-01, 05-02, 05-03, 05-04, 05-05 | Unsafe/FFI/MMIO/DMA/interrupt/linker/static-memory/allocator/panic code through narrow adapter crates with invariants and tests. | SATISFIED | Audit manifest has 21 surfaces; adapter modules and unsafe locality verifier passed; cargo tests passed. |
| CORE-01 | 05-01, 05-02, 05-03, 05-05 | Preserve STM32 startup, memory layout, interrupt/vector behavior, clocks, HAL/CMSIS, watchdog, and linker sections. | SATISFIED | Retained source paths inventoried; board/runtime contracts model STM32F4, STM32G0, and STM32H503; hardware proof classified non-local. |
| CORE-02 | 05-01, 05-04, 05-05 | Preserve FreeRTOS orchestration, task readiness, static task memory, synchronization, queues, timers, and startup ordering. | SATISFIED | Runtime contracts and tests cover task masks, auxiliary startup, static memory, queue, timer, mutex, semaphore, event-group, and wait-condition surfaces. |

No orphaned Phase 5 requirements were found: RUST-03, RUST-04, CORE-01, and CORE-02 are all claimed by Phase 5 plans. `.planning/REQUIREMENTS.md` still marks them pending, which is expected until the orchestrator updates state after verification.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `tools/bazel/phase5_verify.py` | 371, 377 | `return None` | Info | Parser sentinel returns inside raw-string scanning helpers; not a stub and not user-visible output. |

No TODO/FIXME/placeholders, hardcoded empty user-visible data, or console-only implementations were found in the Phase 5 files scanned.

### Human Verification Required

None for the Phase 5 contract goal. Hardware/scheduler behavior is intentionally not claimed as locally proven and is listed as deferred non-local evidence.

### Gaps Summary

No Phase 5 gaps found. The phase achieved the goal at the intended boundary-contract level: retained foreign code is named, unsafe/runtime surfaces are audit-linked, board/runtime adapters expose typed contracts, pure crates remain unsafe-free, and Bazel/just provide a passing aggregate gate.

---

_Verified: 2026-06-03T21:16:28Z_
_Verifier: the agent (gsd-verifier)_
