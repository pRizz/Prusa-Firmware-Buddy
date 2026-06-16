# Phase 5: Foreign Code, Unsafe, and Runtime Boundary - Research

**Researched:** 2026-06-03
**Domain:** Embedded Rust runtime boundary, retained C/C++/ASM/vendor inventory, STM32 startup/linker/HAL, FreeRTOS orchestration
**Confidence:** HIGH for local source inventory and workflow shape; MEDIUM for hardware-preservation evidence because final parity still needs simulator or hardware gates. [VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md; .planning/REQUIREMENTS.md; local source audit]

<user_constraints>

## User Constraints (from CONTEXT.md)

All text in this block is copied verbatim from `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md`. [VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md]

### Locked Decisions

## Implementation Decisions

### Retained Foreign-Code Inventory

- **D-01:** Build a tracked foreign-code inventory for retained `lib/`, `src/device`, startup ASM, linker scripts, generated headers/resources, HAL/CMSIS, FreeRTOS, Marlin, WUI/network/filesystem/vendor, and auxiliary firmware surfaces that Phase 5 depends on.
- **D-02:** Each inventory row must include component path, language/kind, source or version evidence, ownership boundary, retention reason, safe Rust facade or adapter, replacement posture, risk class, and required evidence before cutover.
- **D-03:** Retention is allowed for v1 when behavior parity or hardware risk requires it, but every retained island must be named. No new anonymous C/C++/ASM/vendor dependency should be introduced through Bazel or Rust adapter code.
- **D-04:** Keep CMake and current C/C++ code as reference/comparison surfaces. Bazel remains the developer authority and must expose inspectable labels or manifests for retained-code inventory and runtime-boundary verification.

### Unsafe And FFI Boundary Shape

- **D-05:** Preserve Phase 4's pure `buddy-domain` and policy crates as `unsafe`-free. Any required `unsafe` belongs in narrow adapter crates or modules that document invariants close to the call sites.
- **D-06:** Add explicit unsafe/FFI audit artifacts for MMIO, DMA, interrupt registration, linker symbols, startup vectors, static task memory, allocator or heap setup, panic/BSOD boundary, C ABI calls, and mutable statics.
- **D-07:** Use safe Rust facade types around raw handles, pointers, memory ranges, task objects, queues, timers, and linker regions where practical. Parse raw board/runtime facts into domain or boundary types before adapter code can use unchecked primitives.
- **D-08:** Tests should cover pure boundary decisions and facade contracts on host where possible. Hardware-only invariants must be documented with `hardware-smoke`, `simulator-flow`, or `manual-hardware-required` evidence instead of being claimed as locally passed.

### STM32 Startup, HAL, And Memory Layout

- **D-09:** Preserve supported MCU-family startup behavior, vector/interrupt layout, linker-controlled sections, boot/noboot differences, reset flow, board clocks, watchdog behavior, and HAL/CMSIS integration for STM32F4, STM32G0, and STM32H5 surfaces captured in the baseline.
- **D-10:** Keep linker scripts and startup assembly as retained foreign code until a safe Rust replacement has explicit evidence. Phase 5 may wrap and manifest them; it should not churn them gratuitously.
- **D-11:** xBuddy Extension and STM32H503 strategy must be made explicit because Phase 4 left exact target triples, linker/FPU choices, and H503 handling as residual Phase 5 risks.
- **D-12:** Runtime verification should include manifest checks, static source audits, Rust adapter tests, Bazel/`just` target coverage, and honest evidence classes for simulator or hardware steps that cannot run locally.

### FreeRTOS Runtime Orchestration

- **D-13:** Preserve FreeRTOS task orchestration, task dependency readiness, static idle/timer task memory assumptions, synchronization behavior, queues, timers, and startup ordering for master-board and auxiliary firmware personalities.
- **D-14:** The Rust runtime adapter should model task identity, dependency readiness, task memory contracts, and synchronization boundaries as typed contracts before Phase 6+ subsystem code depends on them.
- **D-15:** Existing `src/buddy/main.cpp`, `src/common/appmain.cpp`, `src/freertos`, `include/tasks.hpp`, and auxiliary `src/puppy/*/main.cpp` are reference surfaces. Do not silently change their behavior unless the plan ties the change to a Phase 5 runtime-boundary requirement and verification evidence.
- **D-16:** Use early-return, functional-core/imperative-shell structure for new Rust logic: pure contract modeling and manifest validation in testable Rust, thin imperative shells for retained C/HAL/RTOS calls.

### Verification Strategy

- **D-17:** Add a Phase 5 verifier exposed through Bazel and `just`, following the Phase 2 through Phase 4 pattern. It should check inventory presence, required runtime-boundary strings/types, adapter crate/module boundaries, unsafe-audit coverage, target queryability, and relevant Rust checks.
- **D-18:** Relevant pre-commit verification for this phase should include Rust formatting/lint/build/tests, the new Phase 5 verifier, and targeted Bazel query or `just --list` checks for added labels. Heavy firmware/simulator/hardware evidence may be documented as explicit non-local gates.
- **D-19:** Lifecycle validation must remain clean before git finalization: context, plan, execution summary, verification, and phase artifacts must share the same lifecycle metadata.

### the agent's Discretion

The agent may choose exact artifact names, manifest schema, adapter module names, and verifier implementation details. Prefer small standard-library Rust/Python helpers and clear Bazel/`just` labels over broad build-system rewrites. Keep implementation minimal but auditable: one clear inventory, one clear unsafe boundary surface, one verifier, and focused tests are better than scattered documentation.

### Deferred Ideas (OUT OF SCOPE)

## Deferred Ideas

- Printing-core behavior parity, motion/thermal safety behavior, and feature gates remain Phase 6.
- Persistent storage, resources, and migration compatibility remain Phase 7.
- GUI, network service, transfer, and auxiliary-controller behavior parity remain Phase 8 through Phase 10.
- Replacing retained vendor/HAL/RTOS/network/filesystem components with Rust alternatives remains post-parity v2 work unless a narrow v1 safety reason forces a replacement.

</user_constraints>

## Summary

Phase 5 should plan one inspectable foreign-code inventory, one unsafe/FFI/runtime-boundary audit, narrow Rust facade contracts in `buddy-board-adapter` and `buddy-runtime-adapter`, and one Phase 5 verifier exposed by Bazel and `just`. [VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md; rust/crates/board-adapter/src/lib.rs; rust/crates/runtime-adapter/src/lib.rs; tools/bazel/phase4_verify.py; justfile]

The current repo already has the Phase 4 Rust workspace with `buddy-domain`, `buddy-application`, `buddy-board-adapter`, and `buddy-runtime-adapter`; the workspace uses Rust edition 2024, Rust minimum 1.85, and a workspace lint forbidding unsafe code. [VERIFIED: Cargo.toml; rust/crates/board-adapter/src/lib.rs; rust/crates/runtime-adapter/src/lib.rs] Phase 5 should keep `buddy-domain` and `buddy-application` unsafe-free while changing only adapter crates or specific adapter modules to permit audited unsafe surfaces where needed. [VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md; Cargo.toml]

The runtime boundary is not uniform across all MCU families: STM32F4 and STM32G0 startup/linker surfaces live under `src/device`, while xBuddy Extension STM32H503 startup/linker/HAL configuration lives under `src/puppy/xbuddy_extension`. [VERIFIED: src/device/CMakeLists.txt; src/device/stm32f4/CMakeLists.txt; src/device/stm32g0/CMakeLists.txt; src/puppy/xbuddy_extension/CMakeLists.txt] The planner should preserve this distinction instead of creating a generic `src/device/stm32h5` assumption. [VERIFIED: src/device/CMakeLists.txt; find audit of src/device and src/puppy/xbuddy_extension]

**Primary recommendation:** Implement Phase 5 as a manifest-driven boundary layer: tracked inventory + unsafe audit + typed adapter contracts + standard-library verifier + evidence-classed hardware/simulator gates. [VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md; tools/bazel/phase4_verify.py; AGENTS.bright-builds.md]

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RUST-03 | Developer can inspect a foreign-code inventory for every retained C, C++, ASM, generated, and vendor component, including retention reason, version/source, ownership boundary, safe Rust facade, and replacement posture. [VERIFIED: .planning/REQUIREMENTS.md] | Use a tracked manifest plus Markdown inventory covering `lib/`, `src/device`, startup ASM, linker scripts, generated outputs, HAL/CMSIS, FreeRTOS, Marlin, WUI/network/filesystem/vendor, and auxiliary firmware surfaces. [VERIFIED: 05-CONTEXT.md; lib/CMakeLists.txt; src/device/CMakeLists.txt; tools/bazel/generated_drift.py] |
| RUST-04 | Developer can audit all `unsafe`, FFI, MMIO, DMA, interrupt, linker-symbol, static-memory, allocator, and panic-boundary code through narrow adapter crates with documented invariants and tests. [VERIFIED: .planning/REQUIREMENTS.md] | Keep pure crates unsafe-free, allow audited unsafe only in adapter modules, and require audit rows for Rust unsafe blocks, C ABI declarations, linker attributes, MMIO volatile access, DMA buffers, IRQ registration, allocator/panic hooks, mutable statics, and retained C/C++ boundary calls. [VERIFIED: 05-CONTEXT.md; Cargo.toml; Rust 2024 unsafe extern docs; Rust 2024 unsafe attributes docs] |
| CORE-01 | Rust firmware preserves STM32 startup, memory layout, vector/interrupt behavior, board clocks, HAL/CMSIS integration, watchdog behavior, and linker-controlled sections for supported MCU families. [VERIFIED: .planning/REQUIREMENTS.md] | Inventory and facade rows must explicitly cover F4/G0 startup/linker directories, xBuddy Extension H503 startup/linker files, HAL config targets, MCU compile/link flags, boot/noboot scripts, watchdog entrypoints, and evidence class per family. [VERIFIED: ProjectOptions.cmake; CMakeLists.txt; src/device/*; src/puppy/xbuddy_extension/*; src/common/wdt.cpp] |
| CORE-02 | Rust firmware preserves FreeRTOS task orchestration, task dependency readiness, static task memory assumptions, synchronization behavior, queues, timers, and startup ordering for master and auxiliary firmware. [VERIFIED: .planning/REQUIREMENTS.md] | Runtime adapter contracts must model `TaskDeps`, static idle/timer memory callbacks, queue/mutex wrappers, `src/buddy/main.cpp`, `src/common/appmain.cpp`, and auxiliary `src/puppy/*/main.cpp` startup order with host-testable contract checks and hardware/simulator evidence gates. [VERIFIED: include/tasks.hpp; src/freertos/system_tasks.cpp; src/freertos/queue.hpp; src/freertos/mutex.hpp; src/buddy/main.cpp; src/common/appmain.cpp; src/puppy/dwarf/main.cpp; src/puppy/modularbed/main.cpp; src/puppy/xbuddy_extension/main.cpp] |

</phase_requirements>

## Project Constraints (from AGENTS.md)

- Follow repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the pinned Bright Builds standards before planning or implementation. [VERIFIED: AGENTS.md; AGENTS.bright-builds.md]
- The project is a Big Bang Rust+Bazel rewrite with behavior parity as the compatibility bar and Bazel as the authoritative build system. [VERIFIED: AGENTS.md; .planning/PROJECT.md; .planning/STATE.md]
- Common workflows must remain discoverable through `justfile` wrappers that call Bazel/Rust tooling. [VERIFIED: AGENTS.md; justfile]
- Bright Builds architecture guidance requires functional core / imperative shell: pure contract modeling and manifest validation should be testable, while retained HAL/RTOS/FFI calls stay in thin imperative adapter shells. [VERIFIED: AGENTS.bright-builds.md; standards/core/architecture.md]
- New Rust code should use clear typed boundaries, early returns, `let...else` where useful, `maybe_` for optional values where practical, and repo-native Rust verification. [VERIFIED: standards/core/code-shape.md; standards/languages/rust.md]
- Unit tests should test behavior, one concern per test, and use Arrange, Act, Assert sections when structure benefits clarity. [VERIFIED: AGENTS.md; standards/core/testing.md]
- Before committing Rust work, run `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` or document why a command cannot run. [VERIFIED: AGENTS.md]
- Do not add anonymous retained C/C++/ASM/vendor islands; retained foreign code must be named, justified, and bounded. [VERIFIED: AGENTS.md; .planning/REQUIREMENTS.md; 05-CONTEXT.md]
- `standards-overrides.md` has no active real override for this phase. [VERIFIED: standards-overrides.md]

## Standard Stack

### Core

| Library / Surface | Version | Purpose | Why Standard |
|-------------------|---------|---------|--------------|
| `buddy-domain` | `0.1.0` local crate | Keep product/board/MCU/feature/artifact/protocol invariants pure and unsafe-free. [VERIFIED: rust/crates/domain/Cargo.toml; rust/crates/domain/src/lib.rs] | Phase 4 established this as the pure domain crate and the Phase 5 context locks pure crates as unsafe-free. [VERIFIED: 05-CONTEXT.md; Cargo.toml] |
| `buddy-application` | `0.1.0` local crate | Keep policy/application decisions consuming validated domain profiles without unsafe code. [VERIFIED: rust/crates/application/Cargo.toml; rust/crates/application/src/lib.rs] | It matches Bright Builds functional-core guidance and currently forbids unsafe. [VERIFIED: AGENTS.bright-builds.md; rust/crates/application/src/lib.rs] |
| `buddy-board-adapter` | `0.1.0` local crate | Add safe facade types for HAL/CMSIS, board identity, MMIO, DMA, interrupts, retained board C/C++/ASM, and memory-region contracts. [VERIFIED: rust/crates/board-adapter/Cargo.toml; rust/crates/board-adapter/src/lib.rs; 05-CONTEXT.md] | The existing crate is already the Phase 5 handoff point for HAL/MMIO/FFI/interrupt wiring. [VERIFIED: rust/crates/board-adapter/src/lib.rs] |
| `buddy-runtime-adapter` | `0.1.0` local crate | Add safe facade types for startup, linker regions, FreeRTOS tasks, static task memory, queues, timers, allocator, and panic/BSOD boundaries. [VERIFIED: rust/crates/runtime-adapter/Cargo.toml; rust/crates/runtime-adapter/src/lib.rs; 05-CONTEXT.md] | The existing crate is already the Phase 5 handoff point for FreeRTOS/startup work. [VERIFIED: rust/crates/runtime-adapter/src/lib.rs] |
| Retained startup/linker/HAL/RTOS C/ASM | Repo-vendored, source-evidenced per inventory row | Preserve current STM32F4/G0/H5 startup, linker, HAL/CMSIS, FreeRTOS, and auxiliary runtime shells while Rust facades narrow access. [VERIFIED: ProjectOptions.cmake; src/device/*; src/puppy/xbuddy_extension/*; lib/Drivers; lib/Middlewares/Third_Party/FreeRTOS] | Phase 5 explicitly requires retained-code inventory and prohibits gratuitous startup/linker churn. [VERIFIED: 05-CONTEXT.md] |

### Supporting

| Library / Surface | Version | Purpose | When to Use |
|-------------------|---------|---------|-------------|
| `tools/bazel/phase5_verify.py` | New standard-library Python script | Verify inventory completeness, unsafe-audit coverage, adapter crate/module boundaries, Bazel labels, `just` recipes, and Rust checks. [RECOMMENDED: 05-CONTEXT.md; VERIFIED: tools/bazel/phase4_verify.py] | Use as the Phase 5 equivalent of `phase4_verify.py`; keep `--quick` static checks and `--all` Rust toolchain checks. [VERIFIED: tools/bazel/phase4_verify.py] |
| `tools/bazel/BUILD.bazel` `shell_binary` labels | Existing Bazel facade pattern | Expose `phase5_verify` and inventory/audit filegroups to developers. [VERIFIED: tools/bazel/BUILD.bazel] | Use for `bazel run //tools/bazel:phase5_verify` and queryable retained-code surfaces. [VERIFIED: justfile; tools/bazel/BUILD.bazel] |
| `justfile` | Existing developer facade | Add `phase5-verify` and keep Rust commands discoverable. [VERIFIED: justfile; 05-CONTEXT.md] | Use as the stable command surface for local verification. [VERIFIED: AGENTS.md; justfile] |
| Rust official unsafe/FFI rules | Rust 2024 edition docs | Ensure `unsafe extern` blocks and unsafe attributes are audited explicitly. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html; https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html] | Use for any Rust FFI or linker-symbol entrypoint added in adapter crates. [CITED: https://doc.rust-lang.org/nomicon/ffi.html] |
| FreeRTOS static allocation APIs | Repo-vendored FreeRTOS plus official API docs | Preserve caller-provided static buffers for tasks, queues, idle, and timer service memory. [VERIFIED: src/freertos/system_tasks.cpp; src/freertos/queue.hpp; CITED: https://freertos.org/xTaskCreateStatic.html; https://freertos.org/xQueueCreateStatic.html; https://www.freertos.org/Documentation/02-Kernel/03-Supported-devices/02-Customization] | Use when modeling runtime task and queue memory contracts in `buddy-runtime-adapter`. [VERIFIED: include/tasks.hpp; src/freertos/system_tasks.cpp] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Retained startup assembly/linker manifests | Immediate Rust startup replacement with a Cortex-M runtime crate | Do not use in Phase 5 because D-10 locks retained startup/linker scripts until replacement evidence exists. [VERIFIED: 05-CONTEXT.md] |
| Narrow hand-authored C ABI adapter contracts | Broad auto-generated bindings for all retained C/C++ code | Do not make broad generated bindings the Phase 5 standard because the requirement is inspectable retained islands and safe facades, not a bulk bridge to anonymous C/C++ surfaces. [VERIFIED: 05-CONTEXT.md; .planning/REQUIREMENTS.md] |
| Manifest-driven inventory plus static checks | A full CMake/C++ source parser | Do not hand-roll a parser for the entire reference build graph; use explicit manifests, known CMake selection files, Bazel labels, and `rg`/path checks for locally verifiable coverage. [VERIFIED: 05-CONTEXT.md; tools/bazel/phase4_verify.py; lib/CMakeLists.txt; src/CMakeLists.txt] |
| Evidence-classed hardware gates | Claiming host verifier proves MCU parity | Do not claim hardware parity from local host checks; D-08 and D-12 require `hardware-smoke`, `simulator-flow`, or `manual-hardware-required` evidence for hardware-only invariants. [VERIFIED: 05-CONTEXT.md] |

**Installation:**

No new third-party packages are recommended for Phase 5. [VERIFIED: Cargo.toml; AGENTS.md dependency guidance] The planner should add repo-owned Rust/Python files and Bazel/`just` labels, then use the existing Cargo/Bazel/just toolchain. [VERIFIED: tools/bazel/phase4_verify.py; tools/bazel/BUILD.bazel; justfile]

**Version verification:** No npm package versions apply. [VERIFIED: no package.json in root audit; Cargo.toml] Rust crate versions are local `0.1.0` crate manifests, and environment tool versions were audited under `## Environment Availability`. [VERIFIED: rust/crates/*/Cargo.toml; local command availability audit]

## Architecture Patterns

### Recommended Project Structure

```text
.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/
├── 05-FOREIGN-CODE-INVENTORY.md     # Human-readable retained-code inventory.
├── 05-UNSAFE-BOUNDARY-AUDIT.md      # Human-readable unsafe/FFI/runtime audit.
└── 05-VERIFICATION.md               # Execution evidence produced after implementation.

tools/bazel/
├── phase5_verify.py                 # Standard-library verifier modeled on phase4_verify.py.
├── manifests/
│   ├── foreign_code_inventory.json   # Machine-readable retained-code inventory.
│   └── unsafe_boundary_audit.json    # Machine-readable unsafe/runtime boundary audit.
└── BUILD.bazel                       # phase5_verify label and manifest filegroups.

rust/crates/board-adapter/src/
├── lib.rs
├── dma.rs
├── ffi.rs
├── interrupt.rs
├── mcu.rs
├── memory_region.rs
└── mmio.rs

rust/crates/runtime-adapter/src/
├── lib.rs
├── allocator.rs
├── linker.rs
├── panic_boundary.rs
├── queue.rs
├── static_memory.rs
├── startup.rs
├── task.rs
└── timer.rs
```

This structure keeps manifests and verification close to the phase artifact, puts machine-readable inputs under the existing Bazel tooling tree, and uses `foo.rs` modules rather than `foo/mod.rs`. [VERIFIED: tools/bazel/phase4_verify.py; standards/languages/rust.md]

### Pattern 1: Manifest-First Retained-Code Inventory

**What:** Maintain a machine-readable inventory plus Markdown report where every retained island has `id`, `path`, `kind`, `language`, `source_version_evidence`, `ownership_boundary`, `retention_reason`, `safe_facade`, `replacement_posture`, `risk_class`, `evidence_required`, and `bazel_label`. [VERIFIED: 05-CONTEXT.md]

**When to use:** Use for all retained C, C++, ASM, generated, and vendor components that remain in the v1 Rust+Bazel firmware boundary. [VERIFIED: .planning/REQUIREMENTS.md; 05-CONTEXT.md]

**Minimum inventory families:** `lib/Drivers`, `lib/Middlewares/Third_Party/FreeRTOS`, `lib/Middlewares/Third_Party/LwIP`, `lib/Middlewares/Third_Party/mbedtls`, `lib/Middlewares/Third_Party/FatFs`, `lib/Middlewares/Third_Party/littlefs`, `lib/Marlin`, `lib/WUI`, `lib/tinyusb`, `lib/Prusa-Firmware-MMU`, `lib/Prusa-Error-Codes`, `lib/libbgcode`, `lib/esp*`, `src/device/stm32f4`, `src/device/stm32g0`, `src/puppy/xbuddy_extension`, generated headers/resources, and packaging/generator outputs that the runtime or release artifacts retain. [VERIFIED: lib/CMakeLists.txt; lib/Middlewares/CMakeLists.txt; src/device/CMakeLists.txt; src/puppy/xbuddy_extension/CMakeLists.txt; tools/bazel/generated_drift.py]

**Example:**

```json
{
  "id": "startup-stm32h503-xbuddy-extension",
  "path": "src/puppy/xbuddy_extension/stm32h503.s",
  "kind": "startup-vector",
  "language": "asm",
  "source_version_evidence": "repo source; selected by src/puppy/xbuddy_extension/CMakeLists.txt",
  "ownership_boundary": "buddy-runtime-adapter::startup",
  "retention_reason": "STM32H503 reset/vector behavior is Phase 5 parity-critical",
  "safe_facade": "RuntimeStartupPlan",
  "replacement_posture": "retain-v1; replace only with hardware evidence",
  "risk_class": "safety-critical-runtime",
  "evidence_required": ["manifest-check", "bazel-query", "manual-hardware-required"],
  "bazel_label": "//tools/bazel:retained_foreign_code"
}
```

The example follows D-02 fields and the xBuddy Extension H503 source path selected by the local CMake file. [VERIFIED: 05-CONTEXT.md; src/puppy/xbuddy_extension/CMakeLists.txt]

### Pattern 2: Unsafe Audit Rows Next To Narrow Adapter Modules

**What:** For every unsafe or runtime-boundary surface, require an audit row with `surface_id`, `crate`, `module`, `source_path`, `kind`, `raw_operation`, `invariant`, `safe_facade`, `test_or_static_check`, `evidence_class`, and `review_status`. [VERIFIED: 05-CONTEXT.md]

**When to use:** Use for Rust `unsafe` blocks, `unsafe extern` blocks, `#[unsafe(no_mangle)]`, `#[unsafe(export_name)]`, `#[unsafe(link_section)]`, MMIO volatile access, DMA buffer typing, interrupt registration, linker symbols, static memory callbacks, allocator hooks, panic/BSOD hooks, retained C ABI calls, mutable statics, and scheduler-stop/crash-dump boundaries. [VERIFIED: 05-CONTEXT.md; CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html; https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html; VERIFIED: src/common/crash_dump/dump.cpp; src/freertos/system_tasks.cpp]

**Example:**

```rust
// Source: Rust 2024 unsafe extern rules and Rustonomicon FFI guidance.
// [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html]
// [CITED: https://doc.rust-lang.org/nomicon/ffi.html]
unsafe extern "C" {
    fn buddy_watchdog_init();
}

pub struct WatchdogBoundary;

impl WatchdogBoundary {
    pub fn initialize(&self) {
        // SAFETY: audit row `ffi-watchdog-init` must prove the symbol is linked once,
        // has no Rust aliasing contract, and is called only during runtime startup.
        unsafe { buddy_watchdog_init() }
    }
}
```

This pattern exposes a safe method while leaving the raw ABI and its safety proof close to the call site. [CITED: https://doc.rust-lang.org/nomicon/ffi.html; VERIFIED: 05-CONTEXT.md]

### Pattern 3: Typed Memory Regions Before MMIO/DMA/Linker Use

**What:** Parse raw addresses, section names, and linker symbols into typed boundary values before unsafe code can use them. [VERIFIED: 05-CONTEXT.md; AGENTS.bright-builds.md]

**When to use:** Use for CCMRAM, DMA-visible buffers, H503 shared/non-shared regions, `.isr_vector`, `.fw_descriptor`, FreeRTOS privileged sections, bootloader descriptor regions, and crash-dump memory collection boundaries. [VERIFIED: include/buddy/ccm_thread.hpp; src/puppy/xbuddy_extension/stm32h503.ld; src/puppy/xbuddy_extension/main.cpp; src/common/crash_dump/dump.cpp]

**Example:**

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MemoryRegionKind {
    CoreCoupledRam,
    DmaAccessibleRam,
    MemoryMappedRegister,
    LinkerSection,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MemoryRegion {
    start: usize,
    len: usize,
    kind: MemoryRegionKind,
}

impl MemoryRegion {
    pub fn new(start: usize, len: usize, kind: MemoryRegionKind) -> Result<Self, MemoryRegionError> {
        if len == 0 {
            return Err(MemoryRegionError::Empty);
        }

        let Some(end) = start.checked_add(len) else {
            return Err(MemoryRegionError::Overflow);
        };

        if end <= start {
            return Err(MemoryRegionError::Overflow);
        }

        Ok(Self { start, len, kind })
    }
}
```

The example follows Bright Builds early-return and typed-boundary guidance; the concrete address ranges must come from manifest rows and source-linked linker scripts. [VERIFIED: standards/core/code-shape.md; standards/core/architecture.md; src/device/stm32f4/linker; src/device/stm32g0/linker; src/puppy/xbuddy_extension/stm32h503.ld]

### Pattern 4: FreeRTOS Contracts As Data Before Calls

**What:** Model task identity, dependency masks, priority, stack words, static control block location, queue item sizes, timer availability, and startup order as Rust data that can be host-tested before any C/RTOS call. [VERIFIED: 05-CONTEXT.md; include/tasks.hpp; src/freertos/system_tasks.cpp; src/freertos/queue.hpp]

**When to use:** Use for `TaskDeps::Dependency`, `TaskDeps::Tasks::*` masks, `xTaskCreateStatic`, `xQueueCreateStatic`, idle/timer task memory callbacks, master startup task, default task, Dwarf/ModularBed/xBuddy Extension auxiliary runtime entrypoints, and timer availability differences across FreeRTOS configs. [VERIFIED: include/tasks.hpp; src/buddy/main.cpp; src/common/appmain.cpp; src/puppy/dwarf/main.cpp; src/puppy/modularbed/main.cpp; src/puppy/xbuddy_extension/main.cpp; include/stm32f4_hal/FreeRTOSConfig.h; include/stm32g0_hal/FreeRTOSConfig.h; src/puppy/xbuddy_extension/config/FreeRTOSConfig.h]

**Example:**

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RuntimeTask {
    Startup,
    Default,
    Network,
    Connect,
    Syslog,
    Puppy,
    AuxiliaryMain,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StaticTaskMemory {
    pub stack_words: u32,
    pub control_block_region: MemoryRegionKind,
}

impl StaticTaskMemory {
    pub fn new(stack_words: u32, control_block_region: MemoryRegionKind) -> Result<Self, TaskMemoryError> {
        if stack_words == 0 {
            return Err(TaskMemoryError::EmptyStack);
        }

        Ok(Self { stack_words, control_block_region })
    }
}
```

This pattern makes the host-testable contract explicit while leaving the actual RTOS creation call in an adapter shell. [VERIFIED: AGENTS.bright-builds.md; src/freertos/system_tasks.cpp; CITED: https://freertos.org/xTaskCreateStatic.html]

### Anti-Patterns to Avoid

- **Relaxing unsafe lints across the whole workspace:** The current workspace forbids unsafe, and Phase 5 only permits unsafe in narrow adapter modules. [VERIFIED: Cargo.toml; 05-CONTEXT.md]
- **Treating H503 as a normal `src/device/stm32h5` implementation:** `src/device/CMakeLists.txt` references `stm32h5`, but the present H503 xBuddy Extension files live under `src/puppy/xbuddy_extension`. [VERIFIED: src/device/CMakeLists.txt; src/puppy/xbuddy_extension/CMakeLists.txt; find audit]
- **Using prose-only inventory:** D-17 requires verifier checks, so the inventory and unsafe audit need machine-readable data or verifier-parsable structure. [VERIFIED: 05-CONTEXT.md; tools/bazel/phase4_verify.py]
- **Claiming hardware preservation from static checks:** Hardware-only invariants must stay evidence-classed until simulator or hardware evidence exists. [VERIFIED: 05-CONTEXT.md]
- **Bulk-binding C++ directly into Rust:** Rust FFI documentation covers C ABI boundaries, while the Rustonomicon notes Rust cannot call directly into C++ without a C interface. [CITED: https://doc.rust-lang.org/nomicon/ffi.html]
- **Letting generated/vendor code appear only through globs:** Retained generated and vendor-heavy surfaces must have named rows and evidence. [VERIFIED: 05-CONTEXT.md; tools/bazel/generated_drift.py; lib/CMakeLists.txt]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Whole-repo retained-code discovery | A fragile CMake/C++ parser that tries to infer every retained component automatically. | Explicit manifest rows plus verifier checks against known source-selection files and Bazel labels. [VERIFIED: 05-CONTEXT.md; tools/bazel/phase4_verify.py] | The required output is an auditable retained-code boundary, and explicit rows make ownership, reason, facade, and evidence visible. [VERIFIED: 05-CONTEXT.md] |
| FFI surface | Generated bindings for broad C/C++ subsystems. | Narrow `extern "C"` adapter entrypoints with safe Rust facades and audit rows. [CITED: https://doc.rust-lang.org/nomicon/ffi.html; VERIFIED: 05-CONTEXT.md] | Broad bindings can hide anonymous retained dependencies and make invariants harder to review. [VERIFIED: .planning/REQUIREMENTS.md; 05-CONTEXT.md] |
| MMIO access | A custom volatile abstraction that hides pointer/alignment/provenance rules. | Thin wrappers around `core::ptr::read_volatile` and `core::ptr::write_volatile` with typed address/register contracts. [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html; https://doc.rust-lang.org/core/ptr/fn.write_volatile.html] | Official docs make volatile externally observable but not atomic, so synchronization and safety invariants must remain explicit. [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html; https://doc.rust-lang.org/core/ptr/fn.write_volatile.html] |
| DMA safety | Pointer wrappers that ignore memory-region constraints. | Typed `MemoryRegion`/`DmaBuffer` contracts that reject CCMRAM or non-DMA-visible regions. [VERIFIED: include/buddy/ccm_thread.hpp] | The local code already documents that DMA cannot use CCMRAM. [VERIFIED: include/buddy/ccm_thread.hpp] |
| FreeRTOS task memory | Guessing stack bytes or TCB lifetime in Rust. | Contract types mirroring `xTaskCreateStatic` inputs and static idle/timer callbacks. [VERIFIED: src/freertos/system_tasks.cpp; CITED: https://freertos.org/xTaskCreateStatic.html; https://www.freertos.org/Documentation/02-Kernel/03-Supported-devices/02-Customization] | FreeRTOS static APIs require persistent caller-provided buffers, and stack depth is in `StackType_t` words. [CITED: https://freertos.org/xTaskCreateStatic.html] |
| Queue semantics | Rust queues with different copy/lifetime behavior. | A facade over retained FreeRTOS queue contracts with item-size and trivially-copyable constraints documented. [VERIFIED: src/freertos/queue.hpp; CITED: https://freertos.org/xQueueCreateStatic.html] | FreeRTOS queues copy fixed-size items into caller-provided storage. [CITED: https://freertos.org/xQueueCreateStatic.html] |
| Startup/linker preservation | Rewriting vector tables and linker scripts in Phase 5. | Retain startup ASM/linker scripts and manifest/wrap them until replacement evidence exists. [VERIFIED: 05-CONTEXT.md] | D-10 explicitly locks retention until a safe Rust replacement has evidence. [VERIFIED: 05-CONTEXT.md] |
| Hardware parity proof | A local verifier that says "preserved" for clocks, watchdogs, vector tables, and interrupts. | Evidence classes: `manifest-check`, `static-source-audit`, `simulator-flow`, `hardware-smoke`, and `manual-hardware-required`. [VERIFIED: 05-CONTEXT.md; .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md] | Host checks can prove manifests and contracts, not physical MCU behavior. [VERIFIED: 05-CONTEXT.md] |

**Key insight:** Phase 5 succeeds by making retained runtime risk auditable and narrow; it does not need to replace or deeply bind every retained component. [VERIFIED: 05-CONTEXT.md; .planning/ROADMAP.md]

## Common Pitfalls

### Pitfall 1: Adapter Unsafe Blocked By Workspace Lint

**What goes wrong:** The workspace lint `unsafe_code = "forbid"` and crate-level `#![forbid(unsafe_code)]` currently block any Rust unsafe or FFI code. [VERIFIED: Cargo.toml; rust/crates/*/src/lib.rs]

**Why it happens:** Phase 4 intentionally made all crates unsafe-free before Phase 5. [VERIFIED: rust/crates/board-adapter/src/lib.rs; rust/crates/runtime-adapter/src/lib.rs]

**How to avoid:** Preserve `forbid(unsafe_code)` in `buddy-domain` and `buddy-application`, then relax only audited adapter modules or adapter crates and add stricter linting such as `unsafe_op_in_unsafe_fn` where Rust supports it. [VERIFIED: 05-CONTEXT.md; ASSUMED]

**Warning signs:** `cargo clippy` fails before runtime adapter code can compile, or unsafe allowances appear outside adapter crates. [VERIFIED: Cargo.toml; 05-CONTEXT.md]

### Pitfall 2: Rust 2024 FFI and Linker Attributes Missed

**What goes wrong:** New FFI/linker-symbol code uses old Rust syntax and misses explicit unsafe markers for extern blocks or linker-affecting attributes. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html; https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html]

**Why it happens:** The workspace edition is 2024, and Rust 2024 requires `unsafe extern` blocks and unsafe marking for `no_mangle`, `export_name`, and `link_section`. [VERIFIED: Cargo.toml; CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html; https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html]

**How to avoid:** Add verifier checks for `unsafe extern`, `#[unsafe(no_mangle)]`, `#[unsafe(export_name)]`, and `#[unsafe(link_section)]` audit rows whenever those strings appear in adapter crates. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html; https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html; VERIFIED: 05-CONTEXT.md]

**Warning signs:** Linker symbol attributes exist without a matching unsafe-audit manifest entry. [VERIFIED: 05-CONTEXT.md; CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html]

### Pitfall 3: H503/xBuddy Extension Modeled In The Wrong Place

**What goes wrong:** A plan assumes H5 startup/linker files are under `src/device/stm32h5`, but the current xBuddy Extension H503 startup/linker/HAL setup is under `src/puppy/xbuddy_extension`. [VERIFIED: src/device/CMakeLists.txt; src/puppy/xbuddy_extension/CMakeLists.txt; find audit]

**Why it happens:** `src/device/CMakeLists.txt` references `stm32h5`, while the actual visible H503 files in this repo are local to xBuddy Extension. [VERIFIED: src/device/CMakeLists.txt; src/puppy/xbuddy_extension/stm32h503.s; src/puppy/xbuddy_extension/stm32h503.ld]

**How to avoid:** Give xBuddy Extension its own inventory rows and adapter contracts for `stm32h503.s`, `stm32h503_boot.ld`, `stm32h503_noboot.ld`, HAL config, FreeRTOS config, shared/non-shared data, and MPU regions. [VERIFIED: src/puppy/xbuddy_extension/CMakeLists.txt; src/puppy/xbuddy_extension/config/FreeRTOSConfig.h; src/puppy/xbuddy_extension/main.cpp; src/puppy/xbuddy_extension/stm32h503.ld]

**Warning signs:** The plan contains a `src/device/stm32h5` implementation task without first resolving the xBuddy Extension special case. [VERIFIED: local source audit]

### Pitfall 4: FreeRTOS Static Memory Lifetime Collapsed Into Ordinary Rust Values

**What goes wrong:** A Rust facade permits stack-local task/queue buffers or byte-count stack sizing when the retained RTOS contract expects persistent static memory and stack depth in words. [CITED: https://freertos.org/xTaskCreateStatic.html; https://freertos.org/xQueueCreateStatic.html]

**Why it happens:** The C wrappers hide some static allocation details, while FreeRTOS static APIs require caller-provided storage. [VERIFIED: src/freertos/system_tasks.cpp; src/freertos/queue.hpp; CITED: https://www.freertos.org/Documentation/02-Kernel/03-Supported-devices/02-Customization]

**How to avoid:** Add `StaticTaskMemory`, `StaticQueueStorage`, and `TimerTaskMemory` contracts with explicit units, lifetime notes, and section/region fields. [VERIFIED: src/freertos/system_tasks.cpp; src/freertos/queue.hpp; 05-CONTEXT.md]

**Warning signs:** Facade constructors take raw `usize` byte lengths without naming `StackType_t` words or persistent storage ownership. [CITED: https://freertos.org/xTaskCreateStatic.html]

### Pitfall 5: DMA And CCMRAM Treated As Interchangeable

**What goes wrong:** Rust memory-region facades allow DMA buffers in CCMRAM. [VERIFIED: include/buddy/ccm_thread.hpp]

**Why it happens:** Current C++ code uses section attributes and helper checks that are easy to lose in a Rust abstraction. [VERIFIED: include/buddy/ccm_thread.hpp; src/freertos/system_tasks.cpp]

**How to avoid:** Encode DMA visibility as a typed property and test that `CoreCoupledRam` cannot become `DmaBuffer`. [VERIFIED: include/buddy/ccm_thread.hpp; AGENTS.bright-builds.md]

**Warning signs:** Adapter tests never mention CCMRAM or DMA visibility. [VERIFIED: 05-CONTEXT.md; include/buddy/ccm_thread.hpp]

### Pitfall 6: Task Dependency Ordering Reduced To Names Only

**What goes wrong:** The runtime adapter records task names but not dependency masks and readiness semantics. [VERIFIED: include/tasks.hpp]

**Why it happens:** `TaskDeps::Tasks::*` encodes behavior through bitmasks and waits/provides on a FreeRTOS event group, not just through task labels. [VERIFIED: include/tasks.hpp; src/common/tasks.cpp]

**How to avoid:** Model task dependencies as typed masks and add host tests for known dependency combinations such as `default_start`, `network`, `connect`, `syslog`, `bootstrap_done`, and `puppy_task_start`. [VERIFIED: include/tasks.hpp]

**Warning signs:** The plan only lists task entrypoints and omits `TaskDeps::Dependency` and `TaskDeps::Tasks`. [VERIFIED: include/tasks.hpp]

### Pitfall 7: Watchdog And Panic Boundaries Hidden Behind Generic Startup

**What goes wrong:** Watchdog, BSOD/fatal-error, assert, and crash-dump surfaces are not given explicit audit rows. [VERIFIED: src/common/wdt.cpp; include/stm32f4_hal/FreeRTOSConfig.h; include/stm32g0_hal/FreeRTOSConfig.h; src/common/crash_dump/dump.cpp]

**Why it happens:** These paths are invoked through startup, FreeRTOS config, asserts, and low-level error handlers rather than one obvious subsystem. [VERIFIED: src/buddy/main.cpp; include/stm32f4_hal/FreeRTOSConfig.h; include/stm32g0_hal/FreeRTOSConfig.h; src/puppy/xbuddy_extension/config/FreeRTOSConfig.h]

**How to avoid:** Require audit rows for `watchdog_init`, `wdt_iwdg_refresh`, `configASSERT`, `_bsod`/`fatal_error`/`hal_panic`, panic handler strategy, and crash-dump raw memory access. [VERIFIED: src/common/wdt.cpp; src/common/crash_dump/dump.cpp; include/stm32f4_hal/FreeRTOSConfig.h; include/stm32g0_hal/FreeRTOSConfig.h; src/puppy/xbuddy_extension/config/FreeRTOSConfig.h]

**Warning signs:** `CORE-01` verification only checks linker/startup files and omits watchdog/assert/panic paths. [VERIFIED: .planning/REQUIREMENTS.md; 05-CONTEXT.md]

### Pitfall 8: Local Verifier Overstates Hardware Evidence

**What goes wrong:** `phase5_verify.py` reports complete CORE-01/CORE-02 preservation after manifest/static checks only. [VERIFIED: 05-CONTEXT.md]

**Why it happens:** The verifier can inspect files, labels, Rust tests, and strings locally, but it cannot prove MCU clocks, interrupts, DMA, watchdog timing, or scheduler behavior on hardware. [VERIFIED: 05-CONTEXT.md; .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md]

**How to avoid:** Make verifier output separate local pass/fail from evidence classes, and require non-local gates to remain pending until actual simulator or hardware evidence is attached. [VERIFIED: 05-CONTEXT.md]

**Warning signs:** Evidence files use "hardware-safe" language without `hardware-smoke`, `simulator-flow`, or `manual-hardware-required` records. [VERIFIED: 05-CONTEXT.md]

## Code Examples

Verified patterns from official sources and local standards:

### Safe FFI Wrapper Contract

```rust
// Source: Rust 2024 unsafe extern and Rustonomicon FFI guidance.
// [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html]
// [CITED: https://doc.rust-lang.org/nomicon/ffi.html]
unsafe extern "C" {
    fn buddy_runtime_start_scheduler() -> i32;
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SchedulerStartResult {
    started: bool,
}

pub fn start_scheduler() -> SchedulerStartResult {
    // SAFETY: `unsafe-boundary-audit.runtime-scheduler-start` documents that the C symbol is linked
    // once, has C ABI-compatible signature, and may only be called after static task memory is ready.
    let result = unsafe { buddy_runtime_start_scheduler() };

    SchedulerStartResult {
        started: result == 0,
    }
}
```

The wrapper keeps the raw C ABI private and exposes a typed result to the rest of Rust. [CITED: https://doc.rust-lang.org/nomicon/ffi.html; VERIFIED: AGENTS.bright-builds.md]

### MMIO Volatile Wrapper

```rust
// Source: core::ptr volatile docs.
// [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html]
// [CITED: https://doc.rust-lang.org/core/ptr/fn.write_volatile.html]
pub struct Register32 {
    address: *mut u32,
}

impl Register32 {
    pub const fn new(address: *mut u32) -> Self {
        Self { address }
    }

    pub fn read(&self) -> u32 {
        // SAFETY: audit row proves address is a valid 32-bit hardware register for this MCU,
        // aligned, non-trapping, and not used for inter-thread synchronization.
        unsafe { core::ptr::read_volatile(self.address) }
    }

    pub fn write(&self, value: u32) {
        // SAFETY: audit row proves address is a valid 32-bit hardware register for this MCU,
        // aligned, non-trapping, and side effects are hardware-defined.
        unsafe { core::ptr::write_volatile(self.address, value) }
    }
}
```

Volatile reads/writes are not atomic synchronization, so synchronization must remain a separate runtime contract. [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html; https://doc.rust-lang.org/core/ptr/fn.write_volatile.html]

### Phase 5 Verifier Shape

```python
REQUIRED_INVENTORY_FIELDS = [
    "id",
    "path",
    "kind",
    "source_version_evidence",
    "ownership_boundary",
    "retention_reason",
    "safe_facade",
    "replacement_posture",
    "risk_class",
    "evidence_required",
]

REQUIRED_UNSAFE_KINDS = [
    "ffi",
    "mmio",
    "dma",
    "interrupt",
    "linker-symbol",
    "startup-vector",
    "static-memory",
    "allocator",
    "panic-boundary",
]
```

This mirrors the existing `phase4_verify.py` approach: make required files/strings/fields explicit and fail fast when the declared boundary is incomplete. [VERIFIED: tools/bazel/phase4_verify.py; 05-CONTEXT.md]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `extern "C"` blocks without explicit unsafe marker | Rust 2024 requires `unsafe extern` blocks. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html] | Rust 1.82 added support, and Edition 2024 requires it. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html] | Every adapter FFI declaration must have an unsafe-audit row and correct signature review. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html; VERIFIED: 05-CONTEXT.md] |
| `no_mangle`, `export_name`, and `link_section` as ordinary attributes | Rust 2024 requires unsafe marking for these attributes. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html] | Rust 1.82 added unsafe attribute syntax, and Edition 2024 requires it. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html] | Linker/vector/panic/startup symbols must be explicitly audited for symbol uniqueness and section correctness. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html; VERIFIED: 05-CONTEXT.md] |
| Treating volatile access as synchronization | Volatile access is externally observable but not atomic and not inter-thread synchronization. [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html; https://doc.rust-lang.org/core/ptr/fn.write_volatile.html] | Current Rust core docs. [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html] | MMIO facades must keep synchronization/interrupt/task safety as separate invariants. [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html; VERIFIED: include/tasks.hpp] |
| Hosted Rust assumptions | Embedded firmware uses `#![no_std]`/`libcore` patterns when code runs without OS-provided `std`. [CITED: https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html] | Stable Embedded Rust Book guidance. [CITED: https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html] | If Phase 5 introduces Rust that participates in firmware startup rather than host-only contracts, panic/allocator/runtime integration must be explicit. [CITED: https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html; VERIFIED: 05-CONTEXT.md] |
| Dynamic RTOS allocation by default | FreeRTOS static APIs require application-provided task/queue memory when using `xTaskCreateStatic` and `xQueueCreateStatic`. [CITED: https://freertos.org/xTaskCreateStatic.html; https://freertos.org/xQueueCreateStatic.html] | FreeRTOS static allocation API docs; local code already uses static callbacks/wrappers. [VERIFIED: src/freertos/system_tasks.cpp; src/freertos/queue.hpp] | Runtime adapter contracts must encode persistent storage, stack words, TCB storage, and queue storage. [CITED: https://freertos.org/xTaskCreateStatic.html; https://freertos.org/xQueueCreateStatic.html] |

**Deprecated/outdated:**

- Treating `lib/` as one retained dependency is inadequate for Phase 5 because RUST-03 requires every retained C/C++/ASM/generated/vendor component to have reason, source/version, ownership boundary, safe facade, and replacement posture. [VERIFIED: .planning/REQUIREMENTS.md]
- Treating `unsafe` as either globally forbidden or globally allowed is inadequate because Phase 5 needs narrow adapter-only unsafe with documented invariants and tests. [VERIFIED: 05-CONTEXT.md; Cargo.toml]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Adapter crates can relax unsafe policy narrowly while preserving `buddy-domain` and `buddy-application` as `unsafe`-free. [ASSUMED] | Common Pitfalls; Standard Stack | If Cargo lint configuration cannot be narrowed cleanly, the plan must add a different crate/module boundary or lint strategy before unsafe adapter work. |
| A2 | No new third-party Rust/Python dependencies are needed for Phase 5 manifests and verification. [ASSUMED] | Standard Stack | If manifest validation complexity grows, the planner may need to justify a schema/serialization crate or keep validation in Python stdlib JSON. |
| A3 | `tools/bazel/manifests/foreign_code_inventory.json` and `unsafe_boundary_audit.json` are acceptable artifact names under the agent's discretion. [ASSUMED] | Architecture Patterns | If the user prefers phase-directory-only artifacts, the planner should keep machine-readable files beside `05-RESEARCH.md` and expose them through Bazel filegroups. |

## Open Questions

All Phase 5 planning questions are RESOLVED for this plan set. The decisions below are narrow planning resolutions, not final cutover evidence.

1. **RESOLVED - STM32H503/xBuddy Extension Bazel strategy**
   - Resolution: Treat xBuddy Extension STM32H503 as a first-class retained runtime surface in inventory, audit, adapter contracts, and verifier checks before adding any generic STM32H5 abstraction. [VERIFIED: 05-CONTEXT.md; src/puppy/xbuddy_extension/CMakeLists.txt]
   - Implementation consequence: Phase 5 plans must name `src/puppy/xbuddy_extension/stm32h503.s`, `src/puppy/xbuddy_extension/stm32h503.ld`, `src/puppy/xbuddy_extension/stm32h503_boot.ld`, `src/puppy/xbuddy_extension/stm32h503_noboot.ld`, `src/puppy/xbuddy_extension/cmsis.cpp`, `src/puppy/xbuddy_extension/hal_clock.cpp`, and Cortex-M33 hard-float `fpv5-sp-d16` evidence. [VERIFIED: CMakeLists.txt; src/puppy/xbuddy_extension/CMakeLists.txt; source audit]
   - Deferred consequence: Exact production Bazel platform/toolchain labels for H503 remain later build-system refinement, but Phase 5 verifier labels must expose H503 inventory and runtime-boundary evidence so the later toolchain work cannot silently collapse H503 into a generic H5 bucket. [VERIFIED: 05-CONTEXT.md]

2. **RESOLVED - unsafe lint strategy**
   - Resolution: Preserve `#![forbid(unsafe_code)]` in pure crates (`buddy-domain` and `buddy-application`) and permit unsafe only in adapter crates with `#![deny(unsafe_op_in_unsafe_fn)]`, audited module allow-lists, local `// SAFETY:` comments, and manifest `source_path` rows. [VERIFIED: Cargo.toml; rust/crates/domain/src/lib.rs; rust/crates/application/src/lib.rs; 05-CONTEXT.md]
   - Implementation consequence: Adapter crates may relax crate-level unsafe linting only as needed for audited modules; the Phase 5 verifier must fail if unsafe operations, unsafe extern declarations, unsafe attributes, or adapter unsafe allowances appear outside the audited board/runtime adapter files. [VERIFIED: Rust 2024 unsafe extern docs; Rust 2024 unsafe attributes docs; 05-CONTEXT.md]
   - Deferred consequence: No broad generated binding surface or global unsafe allowance is accepted in Phase 5. [VERIFIED: 05-CONTEXT.md]

3. **RESOLVED - simulator and hardware gate availability**
   - Resolution: Required local Phase 5 gates are manifest/schema checks, static source audits, Rust host tests, Bazel queryability, and `just` facade discovery. Simulator and hardware checks are evidence classes, not local pass/fail claims, until the required simulator/hardware/toolchain access is available. [VERIFIED: 05-CONTEXT.md; Environment Availability audit]
   - Implementation consequence: `arm-none-eabi-gcc` and hardware access are not required for local plan completion; full embedded firmware startup, board-clock, DMA, interrupt, watchdog, and scheduler timing checks must remain marked `simulator-flow`, `hardware-smoke`, or `manual-hardware-required` where local checks cannot prove them. [VERIFIED: Environment Availability audit; 05-CONTEXT.md]
   - Deferred consequence: Later verification/cutover phases must replace `manual-hardware-required` evidence with simulator or hardware results before claiming firmware-level parity. [VERIFIED: .planning/REQUIREMENTS.md; .planning/ROADMAP.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `python3` | Phase 5 verifier and manifest checks | ✓ | Python 3.14.4 | None needed. [VERIFIED: local command availability audit] |
| `cargo` | Rust fmt/clippy/build/test/doc checks | ✓ | cargo 1.91.1 | None needed. [VERIFIED: local command availability audit] |
| `rustc` | Rust workspace build and tests | ✓ | rustc 1.91.1 | None needed. [VERIFIED: local command availability audit] |
| `bazel` | Bazel `phase5_verify` and queryable labels | ✓ | Bazel 9.1.0 | Direct `python3 tools/bazel/phase5_verify.py --quick` for static checks if Bazel invocation fails. [VERIFIED: local command availability audit; tools/bazel/phase4_verify.py] |
| `just` | Developer facade | ✓ | just 1.48.0 | Direct Bazel/Python commands. [VERIFIED: local command availability audit; justfile] |
| `rg` | Source audit and verifier support | ✓ | ripgrep 15.1.0 | Python stdlib file scanning. [VERIFIED: local command availability audit] |
| `cmake` | Reference comparison only | ✓ | cmake 3.27.9 | Use existing source files and Bazel manifests for Phase 5 local checks. [VERIFIED: local command availability audit; 05-CONTEXT.md] |
| `ninja` | Reference CMake builds if needed | ✓ | 1.13.2 | Skip local CMake build unless planner explicitly adds reference build evidence. [VERIFIED: local command availability audit] |
| `arm-none-eabi-gcc` | Full embedded reference builds and firmware-level checks | ✗ | — | Use repo bootstrap `.dependencies` path if installed later, or classify embedded firmware builds as non-local/blocking evidence. [VERIFIED: local command availability audit; README.md; utils/bootstrap.py] |
| `pre-commit` | Repo hook verification and generated-file checks | ✗ | — | Use explicit `just`/Bazel/Python checks locally; install or bootstrap before final hook-level verification. [VERIFIED: local command availability audit; .pre-commit-config.yaml] |

**Missing dependencies with no fallback:**

- Full local embedded firmware build evidence is blocked until `arm-none-eabi-gcc` is available through system PATH or repo bootstrap dependencies. [VERIFIED: local command availability audit; utils/bootstrap.py]

**Missing dependencies with fallback:**

- `pre-commit` is missing, but Phase 5 can still run explicit Rust, Bazel, just, and Python verifier commands; hook-level verification should remain documented until the tool is installed. [VERIFIED: local command availability audit; justfile; .pre-commit-config.yaml]

## Validation Architecture

`workflow.nyquist_validation` is explicitly enabled in `.planning/config.json`, so the planner must include Wave 0 validation work. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Cargo Rust tests through cargo 1.91.1, Python stdlib verifier, Bazel 9.1.0, and just 1.48.0. [VERIFIED: local command availability audit; tools/bazel/phase4_verify.py; justfile] |
| Config file | `Cargo.toml`; `tools/bazel/BUILD.bazel`; `justfile`; new `tools/bazel/phase5_verify.py`. [VERIFIED: Cargo.toml; tools/bazel/BUILD.bazel; justfile] |
| Quick run command | `python3 tools/bazel/phase5_verify.py --quick` after Wave 0 adds the script. [RECOMMENDED: tools/bazel/phase4_verify.py; 05-CONTEXT.md] |
| Full suite command | `just phase5-verify` after Wave 0 adds the recipe and Bazel target. [RECOMMENDED: justfile; 05-CONTEXT.md] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| RUST-03 | Inventory has required rows and fields for retained C/C++/ASM/generated/vendor families. [VERIFIED: .planning/REQUIREMENTS.md; 05-CONTEXT.md] | Static manifest/verifier | `python3 tools/bazel/phase5_verify.py --quick` | ❌ Wave 0 |
| RUST-04 | Unsafe/FFI/runtime audit covers all declared unsafe kinds and all Rust adapter unsafe occurrences. [VERIFIED: .planning/REQUIREMENTS.md; 05-CONTEXT.md] | Static verifier + Rust unit tests | `python3 tools/bazel/phase5_verify.py --quick` and `cargo test --all-features` | ❌ Wave 0 for verifier; ✅ existing Cargo test infra |
| CORE-01 | STM32F4/G0/H5 startup, linker, HAL/CMSIS, watchdog, vector, boot/noboot, and section surfaces are represented with evidence classes. [VERIFIED: .planning/REQUIREMENTS.md; ProjectOptions.cmake; src/device/*; src/puppy/xbuddy_extension/*] | Static manifest + evidence review | `python3 tools/bazel/phase5_verify.py --quick` | ❌ Wave 0 |
| CORE-02 | FreeRTOS task dependencies, static memory, queues, timers, sync, and startup ordering are modeled as typed runtime contracts. [VERIFIED: .planning/REQUIREMENTS.md; include/tasks.hpp; src/freertos/system_tasks.cpp] | Rust unit tests + static manifest | `cargo test --all-features` and `python3 tools/bazel/phase5_verify.py --quick` | ❌ Wave 0 for new tests/manifests; ✅ existing Cargo test infra |

### Sampling Rate

- **Per task commit:** `python3 tools/bazel/phase5_verify.py --quick` plus focused `cargo test --all-features` for changed adapter crates. [RECOMMENDED: tools/bazel/phase4_verify.py; 05-CONTEXT.md]
- **Per wave merge:** `just phase5-verify`. [RECOMMENDED: justfile; 05-CONTEXT.md]
- **Phase gate:** `just phase5-verify`, `just rust-format`, `just rust-lint`, `just rust-build`, `just rust-test`, `just --list`, and targeted `bazel query` for Phase 5 labels. [VERIFIED: justfile; 05-CONTEXT.md]

### Wave 0 Gaps

- [ ] `tools/bazel/phase5_verify.py` — verifies RUST-03, RUST-04, CORE-01, and CORE-02 manifest/static coverage. [RECOMMENDED: tools/bazel/phase4_verify.py; 05-CONTEXT.md]
- [ ] `tools/bazel/manifests/foreign_code_inventory.json` — machine-readable RUST-03 source of truth. [RECOMMENDED: 05-CONTEXT.md]
- [ ] `tools/bazel/manifests/unsafe_boundary_audit.json` — machine-readable RUST-04 source of truth. [RECOMMENDED: 05-CONTEXT.md]
- [ ] `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md` — human-readable retained-code inventory. [RECOMMENDED: 05-CONTEXT.md]
- [ ] `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-UNSAFE-BOUNDARY-AUDIT.md` — human-readable unsafe/runtime audit. [RECOMMENDED: 05-CONTEXT.md]
- [ ] `rust/crates/board-adapter/src/{mcu,memory_region,mmio,dma,interrupt,ffi}.rs` — safe board facade contracts and host tests. [RECOMMENDED: rust/crates/board-adapter/src/lib.rs; 05-CONTEXT.md]
- [ ] `rust/crates/runtime-adapter/src/{startup,linker,task,queue,timer,static_memory,allocator,panic_boundary}.rs` — runtime contracts and host tests. [RECOMMENDED: rust/crates/runtime-adapter/src/lib.rs; 05-CONTEXT.md]
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, and `justfile` Phase 5 labels/recipes — developer-visible verification surface. [RECOMMENDED: tools/bazel/BUILD.bazel; BUILD.bazel; justfile; 05-CONTEXT.md]

## Security Domain

Security enforcement is enabled by default because `.planning/config.json` does not set `security_enforcement` to `false`. [VERIFIED: .planning/config.json]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | No for Phase 5 runtime-boundary implementation; network/auth parity is deferred to Phase 9. [VERIFIED: 05-CONTEXT.md; .planning/ROADMAP.md] | Inventory retained auth/network code, but do not implement auth behavior in Phase 5. [VERIFIED: 05-CONTEXT.md] |
| V3 Session Management | No for Phase 5; GUI/network sessions are Phase 8/9 work. [VERIFIED: .planning/ROADMAP.md] | Keep any retained WUI/network session code visible in inventory only. [VERIFIED: 05-CONTEXT.md; lib/WUI] |
| V4 Access Control | Yes for low-level privilege/MPU/interrupt/runtime boundaries. [VERIFIED: src/puppy/xbuddy_extension/main.cpp; src/puppy/xbuddy_extension/config/FreeRTOSConfig.h] | Model MPU regions, interrupt priorities, task privilege, and scheduler boundary as typed adapter contracts with evidence classes. [VERIFIED: src/puppy/xbuddy_extension/main.cpp; include/tasks.hpp] |
| V5 Input Validation | Yes for manifest schemas, raw runtime facts, addresses, sizes, task identities, and dependency masks. [VERIFIED: 05-CONTEXT.md; AGENTS.bright-builds.md] | Use Rust constructors/newtypes and Python JSON validation before unchecked primitives are accepted. [VERIFIED: standards/core/architecture.md; tools/bazel/phase4_verify.py] |
| V6 Cryptography | Inventory-only in Phase 5; TLS/crypto behavior parity is Phase 9. [VERIFIED: 05-CONTEXT.md; .planning/ROADMAP.md] | Retain and inventory mbedTLS/decrypt surfaces; do not hand-roll crypto. [VERIFIED: lib/Middlewares/Third_Party/mbedtls; AGENTS.md dependency/security guidance] |

### Known Threat Patterns for Embedded Runtime Boundary

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Wrong FFI signature or symbol collision | Tampering / Elevation of privilege | Require `unsafe extern` audit rows, linker-symbol audit rows, and verifier checks for unsafe attributes. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html; https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html] |
| MMIO pointer to wrong address or alignment | Tampering / Denial of service | Parse MMIO addresses into typed register contracts and document non-trapping/alignment invariants. [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html; https://doc.rust-lang.org/core/ptr/fn.write_volatile.html] |
| DMA buffer in non-DMA-accessible memory | Tampering / Denial of service | Reject CCMRAM-backed DMA buffers in safe constructors. [VERIFIED: include/buddy/ccm_thread.hpp] |
| Incorrect task dependency readiness | Denial of service | Model `TaskDeps` masks and startup order as host-tested runtime contracts. [VERIFIED: include/tasks.hpp; src/buddy/main.cpp] |
| Panic/assert boundary diverges from reference | Denial of service / Repudiation | Inventory and audit BSOD/fatal/hal panic/configASSERT boundaries with evidence class per board family. [VERIFIED: include/stm32f4_hal/FreeRTOSConfig.h; include/stm32g0_hal/FreeRTOSConfig.h; src/puppy/xbuddy_extension/config/FreeRTOSConfig.h] |
| Crash dump raw memory collection exposes or corrupts memory | Information disclosure / Tampering | Treat crash dump memory ranges as unsafe boundary rows with linker/memory-region evidence. [VERIFIED: src/common/crash_dump/dump.cpp] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md` — locked user decisions, discretion, deferred scope, canonical references, and verification strategy. [VERIFIED: local file]
- `.planning/REQUIREMENTS.md` — RUST-03, RUST-04, CORE-01, CORE-02 requirement text. [VERIFIED: local file]
- `.planning/ROADMAP.md` — Phase 5 goal, dependency, and success criteria. [VERIFIED: local file]
- `.planning/STATE.md` — current Phase 5 focus and residual H503/target/linker/FPU risks. [VERIFIED: local file]
- `AGENTS.md`, `AGENTS.bright-builds.md`, and `standards-overrides.md` — repo-local workflow, Bright Builds rules, and no active local override. [VERIFIED: local files]
- `Cargo.toml` and `rust/crates/*` — Rust workspace membership, edition 2024, rust-version 1.85, unsafe lint, current adapter handoff comments. [VERIFIED: local files]
- `tools/bazel/phase4_verify.py`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `BUILD.bazel`, and `justfile` — existing verifier/Bazel/just pattern. [VERIFIED: local files]
- `ProjectOptions.cmake`, `CMakeLists.txt`, `src/CMakeLists.txt`, `src/device/*`, and `src/puppy/xbuddy_extension/*` — supported boards/MCUs, startup/linker/HAL selection, and H503 special case. [VERIFIED: local files]
- `include/tasks.hpp`, `src/common/tasks.cpp`, `src/buddy/main.cpp`, `src/common/appmain.cpp`, `src/freertos/*`, and `src/puppy/*/main.cpp` — FreeRTOS task dependency, static memory, queue/mutex, and startup-order reference surfaces. [VERIFIED: local files]
- `lib/CMakeLists.txt`, `lib/Middlewares`, `lib/Drivers`, `lib/Marlin`, `lib/WUI`, and retained vendor directories — retained foreign-code source families. [VERIFIED: local source audit]

### Primary External (HIGH confidence)

- Rust Edition Guide: unsafe extern blocks — checked Rust 2024 FFI syntax and safety responsibility. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html]
- Rust Edition Guide: unsafe attributes — checked Rust 2024 `no_mangle`, `export_name`, and `link_section` unsafe marking. [CITED: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html]
- Rustonomicon FFI — checked C ABI binding and safe wrapper pattern. [CITED: https://doc.rust-lang.org/nomicon/ffi.html]
- Rust `core::ptr::read_volatile` and `write_volatile` docs — checked MMIO volatile semantics and safety constraints. [CITED: https://doc.rust-lang.org/core/ptr/fn.read_volatile.html; https://doc.rust-lang.org/core/ptr/fn.write_volatile.html]
- Embedded Rust Book `no_std` chapter — checked `no_std`/`libcore` runtime implications for firmware. [CITED: https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html]
- FreeRTOS `xTaskCreateStatic`, `xQueueCreateStatic`, and customization docs — checked static task/queue/idle/timer memory requirements. [CITED: https://freertos.org/xTaskCreateStatic.html; https://freertos.org/xQueueCreateStatic.html; https://www.freertos.org/Documentation/02-Kernel/03-Supported-devices/02-Customization]

### Secondary (MEDIUM confidence)

- None required; conclusions are based on local source files and official Rust/FreeRTOS documentation. [VERIFIED: source list above]

### Tertiary (LOW confidence)

- None used as authoritative research. [VERIFIED: source list above]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — local crates, Bazel labels, just recipes, and retained runtime files were verified directly. [VERIFIED: Cargo.toml; rust/crates/*; tools/bazel/BUILD.bazel; justfile; src/device/*; src/puppy/xbuddy_extension/*]
- Architecture: HIGH for manifest/verifier/facade shape because it is locked by Phase 5 context and existing Phase 4 patterns; MEDIUM for exact lint configuration because implementation must choose the narrowest workable unsafe allowance. [VERIFIED: 05-CONTEXT.md; tools/bazel/phase4_verify.py; ASSUMED]
- Pitfalls: HIGH for local startup/FreeRTOS/H503/unsafe-lint pitfalls; HIGH for Rust 2024 and FreeRTOS static API pitfalls from official docs. [VERIFIED: local source audit; CITED: Rust and FreeRTOS docs]
- Hardware parity: MEDIUM — source surfaces are verified, but actual clock/watchdog/interrupt/scheduler preservation requires simulator or hardware evidence not available in this research pass. [VERIFIED: 05-CONTEXT.md; Environment Availability audit]

**Research date:** 2026-06-03
**Valid until:** 2026-07-03 for local source topology unless runtime files change; 2026-06-17 for Rust/FreeRTOS API guidance because toolchains and docs can change. [ASSUMED]
