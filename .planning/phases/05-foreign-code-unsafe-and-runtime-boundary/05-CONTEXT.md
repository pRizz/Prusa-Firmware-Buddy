---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 5-2026-06-03T12-58-01
generated_at: 2026-06-03T12:57:57.165Z
---

# Phase 5: Foreign Code, Unsafe, and Runtime Boundary - Context

**Gathered:** 2026-06-03
**Status:** Ready for planning
**Mode:** Yolo

<domain>

## Phase Boundary

Phase 5 makes the Rust firmware runtime boundary explicit. It should inventory every retained C, C++, ASM, generated, and vendor component that remains part of the v1 Rust+Bazel firmware, then introduce narrow Rust adapter surfaces for startup, linker sections, HAL/CMSIS, MMIO, DMA, interrupts, panic/allocator/static-memory assumptions, and FreeRTOS orchestration.

This phase should not implement printing-core parity, persistence/resource compatibility, GUI workflows, network service parity, or auxiliary-controller behavior beyond the runtime boundary needed to boot and orchestrate supported master and auxiliary firmware personalities. Those subsystem behaviors remain Phase 6 through Phase 10 work.

</domain>

<decisions>

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

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project, Standards, And Workflow

- `.planning/PROJECT.md` - Big Bang Rust+Bazel posture, behavior parity bar, retained foreign-code constraint, and current project decisions.
- `.planning/REQUIREMENTS.md` - RUST-03, RUST-04, CORE-01, and CORE-02 requirements.
- `.planning/ROADMAP.md` - Phase 5 goal, success criteria, dependency on Phase 4, and later subsystem boundaries.
- `.planning/STATE.md` - Current focus, residual Phase 5 risks, and accumulated decisions.
- `AGENTS.md` - Repo-local GSD, Bright Builds, Rust, verification, and generated-file instructions.
- `AGENTS.bright-builds.md` - Pinned Bright Builds sidecar and sync/verification requirements.
- `standards-overrides.md` - Local standards exceptions; no active real override.
- `/Users/peterryszkiewicz/Repos/coding-and-architecture-requirements/standards/index.md` - Canonical Bright Builds standards entrypoint used for this phase.
- `/Users/peterryszkiewicz/Repos/coding-and-architecture-requirements/standards/core/architecture.md` - Functional-core/imperative-shell and domain boundary guidance.
- `/Users/peterryszkiewicz/Repos/coding-and-architecture-requirements/standards/core/code-shape.md` - Early-return, optional naming, and code-shape guidance.
- `/Users/peterryszkiewicz/Repos/coding-and-architecture-requirements/standards/core/verification.md` - Sync-first and repo-native pre-commit verification guidance.
- `/Users/peterryszkiewicz/Repos/coding-and-architecture-requirements/standards/core/testing.md` - Unit-test expectations and Arrange/Act/Assert structure.
- `/Users/peterryszkiewicz/Repos/coding-and-architecture-requirements/standards/languages/rust.md` - Rust module, `maybe_`, unsafe, invariant, and verification guidance.

### Prior Phase Evidence

- `.planning/phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md` - Supported product, board, MCU, bootloader, feature, artifact, and safety surfaces.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md` - Startup, watchdog, thermal, motion, crash, emergency, update, and auxiliary safety evidence classes.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md` - Known defects and fragile-area dispositions that retained boundaries must not hide.
- `.planning/phases/02-bazel-authority-and-developer-facade/02-CONTEXT.md` - Bazel authority, platform labels, workflow targets, and `justfile` decisions.
- `.planning/phases/03-artifact-and-generator-parity/03-CONTEXT.md` - Artifact/generator ownership and reference comparison boundary decisions.
- `.planning/phases/04-rust-architecture-and-invariant-model/04-CONTEXT.md` - Rust workspace and invariant-model decisions that Phase 5 extends.
- `.planning/phases/04-rust-architecture-and-invariant-model/04-VERIFICATION.md` - Passed Phase 4 evidence and residual runtime-boundary risks.

### Current Rust And Bazel Surface

- `Cargo.toml` - Rust workspace membership, edition, rust-version, and current workspace lint policy.
- `Cargo.lock` - Locked Rust dependency state.
- `rust/crates/domain/src/lib.rs` - Pure domain crate and current `unsafe`-free invariant boundary.
- `rust/crates/application/src/lib.rs` - Pure application policy crate that consumes validated domain profiles.
- `rust/crates/board-adapter/src/lib.rs` - Current board-adapter shell and Phase 5 handoff comment for HAL/MMIO/FFI.
- `rust/crates/runtime-adapter/src/lib.rs` - Current runtime-adapter shell and Phase 5 handoff for FreeRTOS/startup work.
- `BUILD.bazel` - Root aliases and `rust_workspace_sources` filegroup.
- `tools/bazel/BUILD.bazel` - Existing Bazel workflow labels, retained-foreign-code placeholder, and Rust check targets.
- `tools/bazel/rust_workflow.sh` - Existing Bazel-to-Cargo Rust workflow runner.
- `tools/bazel/phase4_verify.py` - Model for a standard-library Rust architecture verifier.
- `justfile` - Developer-facing workflow facade to extend with Phase 5 verification.

### Runtime Boundary Reference Sources

- `ProjectOptions.cmake` - Printer, board, MCU, bootloader, and feature matrix used to select runtime personalities.
- `CMakeLists.txt` - Current firmware target graph, linker/package hooks, and global retained-code composition.
- `src/CMakeLists.txt` - Board-specific source-directory dispatcher for master boards, Dwarf, ModularBed, xBuddy Extension, and XL dev kit.
- `src/device/CMakeLists.txt` - MCU-family startup, linker, interrupt, and peripheral source selection.
- `src/device/stm32f4/CMakeLists.txt` - STM32F4 startup/linker/peripheral source selection.
- `src/device/stm32g0/CMakeLists.txt` - STM32G0 startup/linker/peripheral source selection.
- `src/device/stm32f4/linker/` - STM32F4 linker scripts and section layout.
- `src/device/stm32g0/linker/` - STM32G0 linker scripts and section layout.
- `src/device/stm32f4/startup/` - STM32F4 startup assembly and vector table surface.
- `lib/Drivers/` - STM32 HAL/CMSIS retained vendor surface.
- `lib/Middlewares/Third_Party/FreeRTOS/` - Retained FreeRTOS scheduler/runtime surface.
- `include/stm32f4_hal/FreeRTOSConfig.h` - STM32F4 FreeRTOS configuration and assert behavior.
- `include/stm32g0_hal/FreeRTOSConfig.h` - STM32G0 FreeRTOS configuration and assert behavior.
- `include/tasks.hpp` - Current task identity/dependency contract.
- `src/buddy/main.cpp` - Master-board HAL/peripheral init and FreeRTOS task orchestration.
- `src/common/appmain.cpp` - Default task and Marlin server loop entrypoint.
- `src/freertos/system_tasks.cpp` - Static idle/timer task memory assumptions.
- `src/freertos/queue.cpp` - Queue wrapper behavior.
- `src/freertos/mutex.cpp` - Mutex wrapper behavior.
- `src/common/Pin.cpp` - GPIO/interrupt behavior and STM32G0 already-enabled IRQ concern.
- `src/common/crash_dump/dump.cpp` - Crash dump memory collection boundary.
- `src/puppy/dwarf/main.cpp` - Dwarf auxiliary firmware runtime entrypoint.
- `src/puppy/modularbed/main.cpp` - ModularBed auxiliary firmware runtime entrypoint.
- `src/puppy/xbuddy_extension/main.cpp` - xBuddy Extension runtime entrypoint.
- `lib/AddMarlin.cmake` - Marlin retained-reference source selection and integration.
- `lib/WUI/` - Retained WUI/network code surface that must be inventory-visible even if later behavior parity is Phase 9.
- `.planning/codebase/STRUCTURE.md` - Directory and runtime entrypoint map.
- `.planning/codebase/CONCERNS.md` - Runtime, security, and retained dependency concerns relevant to inventory and unsafe boundaries.
- `.planning/codebase/TESTING.md` - Current test surfaces and verification commands.
- `.planning/codebase/INTEGRATIONS.md` - External/runtime integration surfaces relevant to retained code.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- Phase 4 already created `buddy-domain`, `buddy-application`, `buddy-board-adapter`, and `buddy-runtime-adapter`. Phase 5 can extend the adapter crates instead of inventing a separate Rust boundary shape.
- `tools/bazel/phase4_verify.py` and `tools/bazel/rust_workflow.sh` provide a proven pattern for a local verifier plus Bazel/`just` workflow target.
- `tools/bazel:retained_foreign_code` exists as a Phase 2 placeholder. Phase 5 should replace or supplement it with real inventory/verification behavior.
- Phase 1 baseline artifacts already identify supported MCUs, boards, safety evidence classes, and retained reference surfaces.

### Established Patterns

- New Rust pure logic should stay `unsafe`-free, tested, and separated from imperative runtime shells.
- Existing Bazel workflow targets often call small repo-owned scripts, with `just` recipes as the stable developer facade.
- Heavy firmware, simulator, and hardware checks are allowed to be evidence-classed instead of forced into every local run, but local verifiers must be honest about what passed.
- Generated and retained-heavy artifacts should be named and traceable instead of silently appearing through broad globs.

### Integration Points

- `rust/crates/board-adapter` is the natural home for board/HAL/MMIO boundary types and safe facades.
- `rust/crates/runtime-adapter` is the natural home for startup, FreeRTOS task, static-memory, panic, and allocator boundary contracts.
- `tools/bazel/BUILD.bazel`, `BUILD.bazel`, and `justfile` are the surfaces downstream developers should use to inspect and run Phase 5 checks.
- Runtime boundary docs and manifests should feed later Phase 6 through Phase 10 planners so subsystem parity work knows which foreign-code islands are retained and which safe adapters are available.

</code_context>

<specifics>

## Specific Ideas

- Prefer an explicit `05-FOREIGN-CODE-INVENTORY.md` or machine-readable companion manifest over prose-only inventory.
- Add an unsafe-boundary audit artifact that distinguishes `unsafe` blocks, FFI declarations, retained linker/startup symbols, and hardware-only assumptions.
- Keep absolute statements narrow: "locally verified manifest and adapter contracts" is acceptable; "hardware-safe across all printers" requires simulator or hardware evidence.
- Treat the STM32H503/xBuddy Extension runtime strategy as a first-class Phase 5 question rather than an afterthought.

</specifics>

<deferred>

## Deferred Ideas

- Printing-core behavior parity, motion/thermal safety behavior, and feature gates remain Phase 6.
- Persistent storage, resources, and migration compatibility remain Phase 7.
- GUI, network service, transfer, and auxiliary-controller behavior parity remain Phase 8 through Phase 10.
- Replacing retained vendor/HAL/RTOS/network/filesystem components with Rust alternatives remains post-parity v2 work unless a narrow v1 safety reason forces a replacement.

</deferred>

---

*Phase: 05-foreign-code-unsafe-and-runtime-boundary*
*Context gathered: 2026-06-03*
