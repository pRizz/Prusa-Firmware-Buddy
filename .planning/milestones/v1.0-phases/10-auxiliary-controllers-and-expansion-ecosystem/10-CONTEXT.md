---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 10-2026-06-14T15-08-30
generated_at: 2026-06-14T15:09:46.271Z
---

# Phase 10: Auxiliary Controllers and Expansion Ecosystem - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning
**Mode:** Yolo

<domain>

## Phase Boundary

Phase 10 delivers IFCE-06 parity contracts for the auxiliary-controller ecosystem. The scope includes puppy controllers, Dwarf, ModularBed, xBuddy Extension, MMU2, Modbus/RS485, toolchanger, dock/tool offset behavior, startup flashing, skip-flash/prebuilt auxiliary firmware modes, auxiliary update flows, and crash-dump/update evidence that existing supported printer combinations depend on.

The phase should continue the established migration pattern: source-backed manifests, typed Rust domain contracts, Bazel/`just` verification labels, and explicit non-local evidence for behavior that cannot be locally proven without simulator or hardware access. This phase must not claim final cutover, physical hardware, or long-run protocol proof unless the plan adds concrete simulator or hardware-smoke evidence.

</domain>

<decisions>

## Implementation Decisions

### Auxiliary parity surface

- **D-01:** Treat the existing C++/CMake auxiliary-controller implementation as the Phase 10 reference oracle. Required source surfaces include `src/puppies/`, `include/puppies/`, `src/puppy/`, `src/puppy/shared/`, `src/puppy/xbuddy_extension_shared/`, `src/mmu2/`, `lib/AddMMU2.cmake`, `lib/AddLiblightmodbus.cmake`, `lib/Prusa-Firmware-MMU/`, `lib/liblightmodbus/`, `ProjectOptions.cmake`, `CMakeLists.txt`, and `utils/gen_puppies_descriptor.py`.
- **D-02:** Build explicit Phase 10 manifests for puppy controller families, Dwarf runtime behavior, ModularBed runtime behavior, xBuddy Extension runtime and MMU bridge behavior, MMU2 availability/transport behavior, Modbus/RS485 protocol surfaces, toolchanger/dock/tool offset behavior, auxiliary startup flashing, prebuilt/skip-flash modes, and auxiliary update/crash-dump evidence.
- **D-03:** Manifest rows should name requirement ID, retained source paths, reference behavior, Rust surface, evidence class, local/non-local proof status, update/build surface, and intentional-delta status. Do not accept freehand auxiliary parity claims without source paths, fixture identities, or explicit non-local evidence.

### Build, packaging, and update flow

- **D-04:** Preserve the Bazel Primary Now posture. CMake remains a reference for auxiliary firmware selection, external project wiring, descriptor generation, resource packaging, and prebuilt binary paths, but Phase 10 plans should add Bazel-owned labels or manifests for the corresponding Rust migration surface.
- **D-05:** Phase 10 should cover auxiliary firmware packageability through Bazel and `just`, including Dwarf, ModularBed, xBuddy Extension, MMU firmware resource paths, puppy descriptor generation, startup-flashing resources, `DWARF_BINARY_PATH`, `MODULARBED_BINARY_PATH`, `XBUDDY_EXTENSION_BINARY_PATH`, and skip-flash options.
- **D-06:** Resource compatibility from Phase 7 stays in force. MMU firmware and puppy/update resources must use source-backed runtime paths and generated-output ownership instead of embedding opaque or credential-like payload values in planning artifacts.

### Rust domain contracts

- **D-07:** Extend the existing `buddy-domain` style with pure Rust types for auxiliary ecosystem concepts rather than primitive string maps. Good candidates include auxiliary controller kind, auxiliary runtime state, firmware image source, update mode, Modbus unit identity, Modbus request kind, bus evidence class, MMU transport state, dock identity, tool offset identity, controller fault class, and auxiliary parity row identity.
- **D-08:** Model runtime states explicitly: bootloader, unavailable, active, stopped, updating, update-failed, communication-fault, and unknown/reference-deferred. Avoid unconditional availability stubs. The existing MMU availability concern should be converted into a typed state contract or intentional-delta row.
- **D-09:** Keep pure domain modules `unsafe`-free, use fallible constructors and enums to reject impossible combinations, and follow Bright Builds Rust guidance: `foo.rs` plus `foo/` for new multi-file modules, `maybe_` for internal optional values, `let...else` for clear guard extraction, and Arrange/Act/Assert unit tests for pure behavior.
- **D-10:** Integrate with prior Rust surfaces instead of duplicating them. `rust/crates/domain/src/product.rs` already models Dwarf, ModularBed, xBuddy Extension, auxiliary bootloader mode, and product/feature compatibility. `rust/crates/domain/src/feature.rs` intentionally marks most auxiliary feature gates as `OutOfScopePhase10`. `rust/crates/domain/src/resource.rs` already models MMU firmware resource paths. `rust/crates/runtime-adapter/src/lib.rs` already exposes auxiliary runtime detection.

### Known concerns and intentional deltas

- **D-11:** Phase 10 must explicitly disposition the long-lived MMU availability/reporting concern from `.planning/codebase/CONCERNS.md`: `MMUAvailable()` and `UseMMU()` currently do not represent disabled, unavailable, bootloader, stopped, active, or fault states reliably.
- **D-12:** xBuddy Extension STM32H503 remains a special retained runtime surface, not a generic STM32H5 abstraction. Plans must preserve the Phase 5 decision to keep `src/puppy/xbuddy_extension/` startup, linker, HAL clock, FreeRTOS config, and hard-float evidence visible.
- **D-13:** Preserve Modbus/RS485 behavior honestly. The xBuddy Extension MMU bridge has timing, accepted-response, and timeout comments that should become source-backed parity rows or typed contracts rather than silently normalized behavior.
- **D-14:** If the Rust rewrite fixes a known auxiliary reference defect, the plan must name it as an intentional delta, map it to IFCE-06, and add regression evidence. Otherwise, preserve the current reference behavior until a later approved fix changes it.

### Verification and lifecycle

- **D-15:** Add a repo-owned Phase 10 verifier exposed through Bazel and `just`, following the Phase 5 through Phase 9 pattern. It should check required manifests, Rust API shape, source-path coverage, concern dispositions, Bazel/just labels, validation artifact presence, lifecycle metadata, and overclaim wording.
- **D-16:** Relevant local verification should include Rust formatting/lint/build/tests, Phase 10 verifier regression tests, a quick `just phase10-verify` path, Bazel queryability for new labels, lifecycle validation, and source-backed evidence checks. Heavy firmware builds, simulator auxiliary flows, RS485 hardware behavior, physical toolchanger/dock behavior, long-run update flows, and final cutover proof may be recorded as explicit non-local evidence.
- **D-17:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 10-2026-06-14T15-08-30`.

### the agent's Discretion

- Exact manifest names, row IDs, schema field order, Rust type names, verifier helper layout, and fixture granularity are flexible if they remain source-backed, reviewable, and covered by tests.
- The planner may split Phase 10 into focused plans by auxiliary reference manifests, Rust domain contracts, Bazel/package/update wiring, known concern dispositions, and aggregate verification.
- Local proof should stay deterministic and standard-library friendly where practical. Do not require hardware, live printers, or external services for green local verification unless the plan explicitly marks that work as non-local/manual evidence.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and phase scope

- `.planning/PROJECT.md` - Rust+Bazel rewrite constraints, validated prior phase outcomes, and Phase 10 focus.
- `.planning/REQUIREMENTS.md` - IFCE-06 requirement text plus verification and cutover boundaries.
- `.planning/ROADMAP.md` - Phase 10 goal, dependencies, success criteria, and Phase 11 cutover boundary.
- `.planning/STATE.md` - Current milestone state and active Phase 10 focus.
- `AGENTS.md` - Repo-local GSD, Bright Builds, Rust, verification, generated-file, and project architecture instructions.
- `AGENTS.bright-builds.md` - Pinned Bright Builds sidecar and sync/verification requirements.
- `standards-overrides.md` - Local standards exceptions; no active real override.
- `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/index.md` - Pinned Bright Builds standards entrypoint.
- `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md` - Functional-core/imperative-shell, parse-at-boundaries, and illegal-state guidance.
- `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/code-shape.md` - Early-return, optional naming, and file/function shape guidance.
- `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md` - Unit-test and Arrange/Act/Assert expectations.
- `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/verification.md` - Sync-first and repo-native verification requirements.
- `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md` - Rust module, `maybe_`, invariant, and verification guidance.

### Prior phase contracts

- `.planning/phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md` - Supported matrix, feature, artifact, and auxiliary surfaces.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md` - Startup, watchdog, crash, update, and auxiliary evidence classes.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md` - Known concern dispositions that Phase 10 must preserve or explicitly change.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md` - retained foreign-code, unsafe, runtime, and FreeRTOS boundary decisions.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md` - auxiliary runtime, MMU, LightModbus, and retained firmware surfaces.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-UNSAFE-BOUNDARY-AUDIT.md` - startup, clock, panic, watchdog, and H503/xBuddy Extension evidence classes.
- `.planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md` - printing/safety/feature-gate decisions and Phase 10 deferral for auxiliary behavior.
- `.planning/phases/06-printing-core-safety-and-feature-gates/06-RESEARCH.md` - feature-gate facts, MMU/toolchanger deferrals, and Phase 10 warnings.
- `.planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md` - resource, MMU firmware, generated-output, and non-local evidence contracts.
- `.planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md` - GUI auxiliary deferral and overclaim guard language.
- `.planning/phases/09-network-web-services-and-transfers/09-CONTEXT.md` - transfer/network boundary and auxiliary-controller deferral.
- `.planning/phases/09-network-web-services-and-transfers/09-VERIFICATION.md` - passed Phase 9 evidence and remaining Phase 10/11 proof boundaries.

### Codebase maps and concerns

- `.planning/codebase/ARCHITECTURE.md` - puppy, auxiliary runtime, task, resource, packaging, and source-layer integration points.
- `.planning/codebase/STRUCTURE.md` - source layout for `src/puppies`, `src/puppy`, `src/mmu2`, tests, and build tooling.
- `.planning/codebase/INTEGRATIONS.md` - flash/update flows, serial/UART, MMU communication, puppy/RS485 Modbus support, and resource packaging.
- `.planning/codebase/TESTING.md` - existing unit and integration test surfaces including `tests/unit/puppies/fifo_coder_tests.cpp`.
- `.planning/codebase/CONCERNS.md` - MMU hard-coded availability/reporting, BuddyHeaders coupling, generated asset drift, and auxiliary-related risks.
- `.planning/codebase/CONVENTIONS.md` - naming, formatting, generated-file, logging, and test conventions.

### Reference source surfaces

- `ProjectOptions.cmake` - board/printer feature gates, master vs auxiliary board classification, MMU transport, puppy firmware options, prebuilt binary paths, and skip-flash options.
- `CMakeLists.txt` - auxiliary external project wiring, descriptor generation, packaging hooks, and xBuddy Extension branch.
- `src/CMakeLists.txt` - board-specific source-directory dispatch for master boards and auxiliary firmware personalities.
- `lib/AddMarlin.cmake` - MMU2, toolchanger, and xBuddy Extension Marlin source selection.
- `lib/AddMMU2.cmake` - retained MMU2 library wiring.
- `lib/AddLiblightmodbus.cmake` - retained LightModbus dependency wiring.
- `utils/gen_puppies_descriptor.py` - puppy descriptor generation reference.
- `src/puppies/puppy_task.cpp` - master-side puppy task and startup/update orchestration.
- `src/puppies/PuppyBootstrap.cpp` - auxiliary bootloader/bootstrap behavior and address selection.
- `src/puppies/PuppyModbus.cpp` and `include/puppies/PuppyModbus.hpp` - Modbus master/request behavior.
- `src/puppies/Dwarf.cpp` and `include/puppies/Dwarf.hpp` - Dwarf runtime behavior, FIFO/log/loadcell/fan/toolhead surfaces, and fault handling.
- `src/puppies/modular_bed.cpp` and `include/puppies/modular_bed.hpp` - ModularBed runtime behavior.
- `src/puppies/xbuddy_extension.cpp` and `include/puppies/xbuddy_extension.hpp` - xBuddy Extension bridge and MMU Modbus behavior.
- `src/puppy/dwarf/main.cpp`, `src/puppy/modularbed/main.cpp`, and `src/puppy/xbuddy_extension/main.cpp` - auxiliary firmware entrypoints.
- `src/puppy/shared/` - shared auxiliary firmware support.
- `src/puppy/xbuddy_extension_shared/` - xBuddy Extension shared bridge/protocol support.
- `src/mmu2/` and `lib/Prusa-Firmware-MMU/` - retained MMU runtime and protocol reference.
- `tests/unit/puppies/` - existing puppy/FIFO unit-test surfaces.
- `rust/crates/domain/src/product.rs` - existing product, board, MCU, bootloader, and auxiliary profile model.
- `rust/crates/domain/src/feature.rs` - Phase 6 feature-gate model with `OutOfScopePhase10` auxiliary gates.
- `rust/crates/domain/src/resource.rs` - MMU firmware and generated/resource path contracts from Phase 7.
- `rust/crates/runtime-adapter/src/lib.rs` - auxiliary runtime boundary detection.
- `tools/bazel/BUILD.bazel` - existing phase verifier labels and Rust workflow targets to extend.
- `tools/bazel/phase6_verify.py`, `tools/bazel/phase7_verify.py`, `tools/bazel/phase8_verify.py`, and `tools/bazel/phase9_verify.py` - verifier patterns and overclaim guards.
- `justfile` - developer-facing verification facade to extend with `phase10-verify`.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `rust/crates/domain/src/product.rs` already encodes Dwarf, ModularBed, xBuddy Extension, auxiliary bootloader mode, and auxiliary profile validation.
- `rust/crates/domain/src/feature.rs` already marks most auxiliary feature gates as `OutOfScopePhase10`, giving Phase 10 a direct handoff point.
- `rust/crates/domain/src/resource.rs` already names `/mmu/fw.bin` as the MMU firmware runtime path and provides resource-path parsing patterns.
- `rust/crates/runtime-adapter/src/lib.rs` already exposes `is_auxiliary_runtime()` over validated product profiles.
- `tools/bazel/phase6_verify.py` through `phase9_verify.py` and matching `justfile` recipes provide the established verifier shape and overclaim-guard pattern.

### Established Patterns

- Prior phases use source-backed JSON manifests plus pure Rust domain modules and a standard-library Python verifier exposed through Bazel and `just`.
- Local verification distinguishes local source/host-test evidence from simulator, hardware-smoke, and manual-hardware-required proof. Phase 10 should keep that distinction.
- Rust domain contracts stay pure and `unsafe`-free, while retained C/C++/ASM/HAL/RTOS behavior remains behind adapter/reference boundaries.

### Integration Points

- Extend `rust/crates/domain/src/lib.rs` with a new auxiliary-focused module or modules.
- Extend `tools/bazel/BUILD.bazel` with Phase 10 verifier and verifier-test labels.
- Extend `justfile` with a `phase10-verify` recipe matching the Phase 6 through Phase 9 pattern.
- Add Phase 10 manifests under `tools/bazel/manifests/` and any deterministic fixtures under `tools/bazel/fixtures/`.
- Add source-backed validation and verification artifacts under `.planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/`.

</code_context>

<specifics>

## Specific Ideas

- Use Phase 10 to turn prior `OutOfScopePhase10` markers into named auxiliary domain contracts rather than deleting them without traceability.
- Keep xBuddy Extension H503 separate from generic H5 runtime modeling unless a plan explicitly proves the abstraction.
- Treat MMU availability/reporting as a typed state problem with disabled, unavailable, bootloader, stopped, active, update, and fault states.
- Treat Modbus request/response timing and speculative accepted flags as compatibility facts first; do not "clean them up" without intentional-delta evidence.

</specifics>

<deferred>

## Deferred Ideas

- Full physical auxiliary-controller, RS485, toolchanger/dock, MMU, and long-run update proof remains Phase 11 cutover evidence unless Phase 10 adds explicit simulator or hardware-smoke artifacts.
- Replacing retained LightModbus, retained MMU vendor code, HAL/RTOS/runtime shells, or upstream auxiliary firmware with native Rust implementations beyond parity contracts remains v2 unless directly required for IFCE-06.
- New auxiliary-controller features unrelated to existing behavior parity remain out of scope for v1.

</deferred>

---

*Phase: 10-auxiliary-controllers-and-expansion-ecosystem*
*Context gathered: 2026-06-14*
