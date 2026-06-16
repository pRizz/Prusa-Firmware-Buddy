---
generated_by: gsd-phase-researcher
lifecycle_mode: yolo
phase_lifecycle_id: 10-2026-06-14T15-08-30
generated_at: 2026-06-14
---

# Phase 10: Auxiliary Controllers and Expansion Ecosystem - Research

**Researched:** 2026-06-14  
**Domain:** Embedded auxiliary-controller parity, Rust domain contracts, Bazel verification  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

The following constraints are copied verbatim from `.planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-CONTEXT.md`. [VERIFIED: .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-CONTEXT.md]

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)

- Full physical auxiliary-controller, RS485, toolchanger/dock, MMU, and long-run update proof remains Phase 11 cutover evidence unless Phase 10 adds explicit simulator or hardware-smoke artifacts.
- Replacing retained LightModbus, retained MMU vendor code, HAL/RTOS/runtime shells, or upstream auxiliary firmware with native Rust implementations beyond parity contracts remains v2 unless directly required for IFCE-06.
- New auxiliary-controller features unrelated to existing behavior parity remain out of scope for v1.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| IFCE-06 | Rust firmware preserves puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, Modbus/RS485, toolchanger, dock/tool offset, startup flashing, skip-flash/prebuilt firmware, and auxiliary-controller update flows. [VERIFIED: .planning/REQUIREMENTS.md] | Source-backed parity manifests, pure Rust auxiliary domain contracts, Bazel/`just` verifier wiring, and explicit non-local evidence rows are the planning backbone for IFCE-06. [VERIFIED: 10-CONTEXT.md; VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: rust/crates/domain/src/product.rs; VERIFIED: ProjectOptions.cmake] |

</phase_requirements>

## Summary

Phase 10 should be planned as a parity-contract phase, not as a from-scratch auxiliary firmware rewrite. The C++/CMake implementation remains the oracle for master-side puppy orchestration, Dwarf, ModularBed, xBuddy Extension, MMU2, LightModbus, descriptor generation, resource packaging, prebuilt paths, and skip-flash behavior. [VERIFIED: 10-CONTEXT.md; VERIFIED: ProjectOptions.cmake; VERIFIED: CMakeLists.txt; VERIFIED: src/CMakeLists.txt; VERIFIED: src/puppies/puppy_task.cpp; VERIFIED: src/puppies/PuppyBootstrap.cpp; VERIFIED: src/puppies/PuppyModbus.cpp; VERIFIED: src/mmu2/mmu2_bootloader.cpp]

The safest plan shape is the Phase 6 through Phase 9 pattern: add source-backed JSON manifests, extend `buddy-domain` with pure typed contracts, expose deterministic Python verification through Bazel and `just`, and record simulator/hardware/update proof as non-local unless concrete evidence artifacts exist. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/phase8_verify.py; VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: justfile; VERIFIED: tools/bazel/BUILD.bazel]

**Primary recommendation:** Use explicit Phase 10 manifests plus a new `buddy-domain` auxiliary module and a `phase10_verify.py` gate before any plan attempts runtime rewrites. [VERIFIED: 10-CONTEXT.md; VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: tools/bazel/phase9_verify.py]

## Project Constraints (from AGENTS.md)

- The root `AGENTS.md` requires reading `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant Bright Builds canonical standards before planning, review, implementation, or audit work. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md; VERIFIED: standards-overrides.md]
- The project is a full Rust rewrite while preserving supported Prusa-Firmware-Buddy behavior, with Bazel as the authoritative build and C/C++/CMake kept as reference, comparison, or compatibility where necessary. [VERIFIED: AGENTS.md]
- The project requires a `justfile` for common workflows, so Phase 10 verification must be developer-facing through `just`. [VERIFIED: AGENTS.md; VERIFIED: justfile]
- Bright Builds architecture, code-shape, verification, testing, and Rust standards apply unless a narrow local override is documented; `standards-overrides.md` contains no active real override. [VERIFIED: AGENTS.md; VERIFIED: standards-overrides.md]
- Embedded firmware behavior requires tests, hardware-aware review, simulator flows, or explicit evidence before replacement claims are complete. [VERIFIED: AGENTS.md]
- Retained third-party, HAL, generated, and upstream imported code must be named and justified instead of silently hidden behind new abstractions. [VERIFIED: AGENTS.md; VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md]
- New owned files should follow repo naming and formatting conventions: snake-case paths for owned C/C++ and Python, Rust module layout from Bright Builds, no boilerplate file headers, generated files updated through their owning generators, and repo-native pre-commit/generator checks where applicable. [VERIFIED: AGENTS.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]
- New pure Rust code should keep `unsafe_code = forbid`, use enums/newtypes/fallible constructors for invariants, use `maybe_` for internal optional names, and prefer `let...else` guard extraction. [VERIFIED: Cargo.toml; VERIFIED: rust/crates/domain/src/lib.rs; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/code-shape.md]
- Unit tests should test behavior, one concern per test, and use Arrange/Act/Assert structure when useful. [VERIFIED: AGENTS.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md]

## Standard Stack

### Core

| Library/Surface | Version | Purpose | Why Standard |
|-----------------|---------|---------|--------------|
| `buddy-domain` Rust crate | workspace crate, Rust edition 2024, `rust-version = 1.85` [VERIFIED: Cargo.toml] | Own pure auxiliary-controller concepts: controller kind, runtime state, update mode, MMU transport state, Modbus identity, dock/tool offset identity, fault class, parity row identity. [VERIFIED: 10-CONTEXT.md; VERIFIED: rust/crates/domain/src/lib.rs] | Existing migration phases already put pure product, feature, resource, safety, storage, protocol, and network contracts in this crate. [VERIFIED: rust/crates/domain/src/product.rs; VERIFIED: rust/crates/domain/src/feature.rs; VERIFIED: rust/crates/domain/src/resource.rs] |
| `buddy-runtime-adapter` Rust crate | workspace crate, Rust edition 2024, `rust-version = 1.85` [VERIFIED: Cargo.toml] | Expose auxiliary runtime boundary checks over validated product profiles without owning hardware behavior. [VERIFIED: rust/crates/runtime-adapter/src/lib.rs] | Existing `is_auxiliary_runtime()` already models the boundary Phase 10 must extend, not duplicate. [VERIFIED: rust/crates/runtime-adapter/src/lib.rs; VERIFIED: 10-CONTEXT.md] |
| Bazel `sh_binary` plus `rust_workflow.sh` | repo-owned Bazel surface, local Bazel 9.1.1 installed [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: local `bazel --version` probe on 2026-06-14] | Run Phase 10 verifier/tests and Rust workflow commands from Bazel labels. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh] | Phase 6 through Phase 9 already expose verifiers through this path. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh] |
| `justfile` phase recipe | repo-owned workflow facade, local just 1.48.0 installed [VERIFIED: justfile; VERIFIED: local `just --version` probe on 2026-06-14] | Provide `just phase10-verify` with verifier tests before aggregate verification. [VERIFIED: justfile; VERIFIED: 10-CONTEXT.md] | Prior phase recipes make `just` the human-facing gate for phase verification. [VERIFIED: justfile] |
| Python stdlib verifier | Python 3.14.4 installed locally; project minimum Python 3.8+ [VERIFIED: local `python3 --version` probe on 2026-06-14; VERIFIED: README.md; VERIFIED: utils/bootstrap.py] | Validate JSON manifests, source paths, Rust API surface, Bazel/just labels, lifecycle metadata, and overclaim wording. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: 10-CONTEXT.md] | Existing phase verifiers are standard-library Python scripts that run locally and under Bazel. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/phase8_verify.py; VERIFIED: tools/bazel/phase9_verify.py] |
| C++/CMake auxiliary reference implementation | reference source, not new standard stack dependency [VERIFIED: 10-CONTEXT.md] | Source oracle for Dwarf, ModularBed, xBuddy Extension, MMU2, Modbus/RS485, toolchanger/dock offsets, startup flashing, resources, and update flows. [VERIFIED: ProjectOptions.cmake; VERIFIED: CMakeLists.txt; VERIFIED: src/CMakeLists.txt; VERIFIED: lib/AddMarlin.cmake; VERIFIED: src/puppies/; VERIFIED: src/puppy/; VERIFIED: src/mmu2/] | Locked decision D-01 requires treating these paths as the reference oracle. [VERIFIED: 10-CONTEXT.md] |

### Supporting

| Library/Surface | Version | Purpose | When to Use |
|-----------------|---------|---------|-------------|
| `lib/liblightmodbus` through `lib/AddLiblightmodbus.cmake` | retained vendored/reference dependency [VERIFIED: lib/AddLiblightmodbus.cmake; VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md] | Reference Modbus/RS485 framing and behavior for puppy master-side communication. [VERIFIED: include/puppies/PuppyModbus.hpp; VERIFIED: src/puppies/PuppyModbus.cpp] | Use as retained reference; do not replace with a native Modbus implementation in Phase 10. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md] |
| `lib/Prusa-Firmware-MMU` through `lib/AddMMU2.cmake` | retained vendored/reference dependency [VERIFIED: lib/AddMMU2.cmake; VERIFIED: lib/Prusa-Firmware-MMU/; VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md] | Reference MMU protocol/runtime behavior and MMU firmware resource relationship. [VERIFIED: src/mmu2/; VERIFIED: src/resources/CMakeLists.txt] | Use for parity rows and typed state contracts; do not rewrite the vendor protocol in this phase. [VERIFIED: 10-CONTEXT.md] |
| `utils/gen_puppies_descriptor.py` | repo generator script [VERIFIED: utils/gen_puppies_descriptor.py] | Generate puppy firmware descriptor metadata after binary creation. [VERIFIED: CMakeLists.txt; VERIFIED: utils/gen_puppies_descriptor.py] | Use through Bazel-owned generated-output labels/manifests and avoid hand-authored descriptors. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: tools/bazel/manifests/phase7_generated_outputs.json] |
| `src/resources/CMakeLists.txt` MMU and puppy resource wiring | reference CMake resource packager [VERIFIED: src/resources/CMakeLists.txt] | Documents `/mmu/fw.bin` and `/puppies/fw-*.bin` runtime resource paths. [VERIFIED: src/resources/CMakeLists.txt; VERIFIED: rust/crates/domain/src/resource.rs] | Consume existing Phase 7 resource contracts and add Phase 10 build/update evidence rows. [VERIFIED: tools/bazel/manifests/phase7_resources.json; VERIFIED: 10-CONTEXT.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Source-backed manifests plus typed Rust contracts | Direct Rust reimplementation of Modbus, MMU, and auxiliary firmware runtime | Direct reimplementation would exceed the locked parity-contract boundary and would hide retained LightModbus/MMU/HAL surfaces that Phase 5 requires naming. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md] |
| Python stdlib verifier | Ad hoc shell checks or external validation packages | Existing phase verifiers are Python stdlib, run under Bazel, and avoid adding new dependencies. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/BUILD.bazel] |
| `buddy-domain` enums/newtypes | String maps in JSON only | Prior Rust surfaces use typed enums and fallible constructors, and D-07 rejects primitive string maps as the main contract. [VERIFIED: 10-CONTEXT.md; VERIFIED: rust/crates/domain/src/product.rs; VERIFIED: rust/crates/domain/src/resource.rs] |

**Installation:** No new external packages are recommended for Phase 10 research. [VERIFIED: Cargo.toml; VERIFIED: MODULE.bazel; VERIFIED: tools/bazel/phase9_verify.py]

**Version verification:** No npm package versions apply. Local tool versions were checked by command probes on 2026-06-14, and no new registry dependency is recommended. [VERIFIED: local command probes on 2026-06-14]

## Architecture Patterns

### Recommended Project Structure

```text
rust/crates/domain/src/
|-- auxiliary.rs              # public auxiliary domain entrypoint
`-- auxiliary/                # only if the module grows past a single file
    |-- controller.rs         # controller kind, board/product compatibility
    |-- state.rs              # runtime/update/MMU transport states
    |-- modbus.rs             # unit identity and request kind types
    `-- parity.rs             # parity row IDs and evidence enums

tools/bazel/
|-- phase10_verify.py         # stdlib verifier matching Phase 6-9 style
|-- phase10_verify_test.py    # verifier regression tests
|-- BUILD.bazel               # sh_binary labels and runfiles
`-- manifests/
    |-- phase10_auxiliary_controllers.json
    |-- phase10_mmu_transport.json
    |-- phase10_modbus_rs485.json
    |-- phase10_toolchanger_dock_offsets.json
    |-- phase10_auxiliary_build_update.json
    `-- phase10_concern_dispositions.json
```

The structure above is a recommendation derived from the existing Phase 6 through Phase 9 verifier/manifests pattern and Bright Builds Rust module guidance. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/manifests/; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]

### Pattern 1: Source-Backed Parity Manifests

**What:** Each Phase 10 behavior claim should be a manifest row with `requirement_id`, `retained_source_paths`, `reference_behavior`, `rust_surface`, `evidence_class`, `proof_scope`, `build_or_update_surface`, and `intentional_delta`. [VERIFIED: 10-CONTEXT.md]

**When to use:** Use this for Dwarf, ModularBed, xBuddy Extension, MMU transport, Modbus/RS485, toolchanger/dock offsets, startup flashing, prebuilt paths, skip-flash modes, crash dump, and update behavior. [VERIFIED: 10-CONTEXT.md; VERIFIED: ProjectOptions.cmake; VERIFIED: CMakeLists.txt; VERIFIED: src/resources/CMakeLists.txt; VERIFIED: src/puppies/; VERIFIED: src/mmu2/]

**Planning detail:** Split manifests by behavior domain so each plan can own a narrow evidence class and source surface. [VERIFIED: 10-CONTEXT.md]

### Pattern 2: Typed Rust Auxiliary Domain

**What:** Model observable auxiliary states and identities as Rust enums/newtypes, with fallible constructors for bounded IDs, paths, and combinations. [VERIFIED: 10-CONTEXT.md; VERIFIED: rust/crates/domain/src/product.rs; VERIFIED: rust/crates/domain/src/resource.rs]

**When to use:** Use for booleans that currently overclaim availability, especially MMU availability/reporting and controller state transitions. [VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: src/mmu2/mmu2_reporting.cpp]

**Example:**

```rust
// Source pattern: 10-CONTEXT.md D-07/D-08, product.rs, resource.rs,
// and Bright Builds Rust guidance.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AuxiliaryRuntimeState {
    Bootloader,
    Unavailable,
    Active,
    Stopped,
    Updating,
    UpdateFailed,
    CommunicationFault,
    UnknownReferenceDeferred,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ModbusUnitId(u8);

impl ModbusUnitId {
    pub const fn new(value: u8) -> Option<Self> {
        if value == 0 {
            return None;
        }

        Some(Self(value))
    }
}
```

The example uses only concepts required by the context and existing Rust patterns; exact type names remain planner discretion. [VERIFIED: 10-CONTEXT.md; VERIFIED: rust/crates/domain/src/product.rs; VERIFIED: rust/crates/domain/src/resource.rs]

### Pattern 3: Verifier as Phase Gate

**What:** Implement `tools/bazel/phase10_verify.py` with narrow checks for manifest schema, source paths, Rust exports, no unsafe in pure domain code, concern disposition, Bazel/just labels, lifecycle ID, validation artifact presence, and overclaim wording. [VERIFIED: 10-CONTEXT.md; VERIFIED: tools/bazel/phase9_verify.py]

**When to use:** Use as the local deterministic gate because Phase 10 cannot locally prove physical RS485, toolchanger, MMU, startup flashing, or long-run update behavior without non-local evidence. [VERIFIED: 10-CONTEXT.md]

**Example:**

```python
REQUIRED_LIFECYCLE_ID = "10-2026-06-14T15-08-30"

REQUIRED_MANIFESTS = [
    "tools/bazel/manifests/phase10_auxiliary_controllers.json",
    "tools/bazel/manifests/phase10_mmu_transport.json",
    "tools/bazel/manifests/phase10_modbus_rs485.json",
    "tools/bazel/manifests/phase10_toolchanger_dock_offsets.json",
    "tools/bazel/manifests/phase10_auxiliary_build_update.json",
    "tools/bazel/manifests/phase10_concern_dispositions.json",
]
```

The verifier skeleton mirrors existing phase verifier constants and the locked lifecycle decision. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: 10-CONTEXT.md]

### Pattern 4: Bazel and just as First-Class Surfaces

**What:** Add `//tools/bazel:phase10_verify`, `//tools/bazel:phase10_verify_tests`, root aliases, runfiles for phase docs/manifests/Rust sources, `rust_workflow.sh` cases, and `just phase10-verify`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]

**When to use:** Use this for every Phase 10 plan that changes manifests, Rust domain contracts, or validation files. [VERIFIED: 10-CONTEXT.md]

### Anti-Patterns to Avoid

- **Boolean availability contracts:** A boolean cannot represent bootloader, unavailable, active, stopped, updating, failed, communication fault, and reference-deferred states. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: src/mmu2/mmu2_reporting.cpp]
- **Generic H5 abstraction for xBuddy Extension:** xBuddy Extension is locked as a special STM32H503 runtime surface with retained startup/linker/HAL/FreeRTOS evidence. [VERIFIED: 10-CONTEXT.md; VERIFIED: src/puppy/xbuddy_extension/; VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md]
- **Freehand hardware claims:** Local verification may prove source coverage and contracts, but hardware RS485/toolchanger/MMU/update behavior needs simulator or hardware-smoke evidence before being claimed. [VERIFIED: 10-CONTEXT.md]
- **Recreating descriptor/resource generation by hand:** Puppy descriptors and MMU/puppy resources already have source-backed generators and Phase 7 contracts. [VERIFIED: utils/gen_puppies_descriptor.py; VERIFIED: src/resources/CMakeLists.txt; VERIFIED: tools/bazel/manifests/phase7_generated_outputs.json; VERIFIED: tools/bazel/manifests/phase7_resources.json]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Modbus/RS485 framing and retry semantics | A new Rust Modbus stack in Phase 10 | Retained `lib/liblightmodbus` behavior plus typed Rust contracts and manifests [VERIFIED: lib/AddLiblightmodbus.cmake; VERIFIED: src/puppies/PuppyModbus.cpp] | Existing behavior includes single-threaded request ownership, retry decisions, timeout behavior, skipped/error states, and power-panic special cases. [VERIFIED: include/puppies/PuppyModbus.hpp; VERIFIED: src/puppies/PuppyModbus.cpp] |
| MMU vendor protocol/runtime | A native Rust MMU protocol implementation | Retained `lib/Prusa-Firmware-MMU` and `src/mmu2/` source-backed contracts [VERIFIED: lib/AddMMU2.cmake; VERIFIED: src/mmu2/; VERIFIED: lib/Prusa-Firmware-MMU/] | Phase 5 keeps MMU vendor code as retained reference, and Phase 10 scope is parity contracts. [VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md; VERIFIED: 10-CONTEXT.md] |
| Puppy firmware descriptors | Hand-authored descriptor blobs | `utils/gen_puppies_descriptor.py` and generated-output manifests [VERIFIED: utils/gen_puppies_descriptor.py; VERIFIED: tools/bazel/generated_drift.py] | Descriptor layout is tied to `include/puppies/crash_dump_shared.hpp`, so manual drift is a compatibility risk. [VERIFIED: utils/gen_puppies_descriptor.py] |
| MMU/puppy resource paths | Opaque embedded payload values in planning artifacts | Phase 7 resource path contracts and source-backed CMake resource wiring [VERIFIED: src/resources/CMakeLists.txt; VERIFIED: rust/crates/domain/src/resource.rs; VERIFIED: tools/bazel/manifests/phase7_resources.json] | D-06 forbids opaque or credential-like payload values in planning artifacts. [VERIFIED: 10-CONTEXT.md] |
| Cryptographic fingerprint/signing behavior | Custom hashing/signing logic in verifier/domain | Existing reference behavior and existing signing/key boundaries [VERIFIED: src/puppies/PuppyBootstrap.cpp; VERIFIED: ProjectOptions.cmake; VERIFIED: AGENTS.md] | Fingerprints are part of boot/update parity, and `SIGNING_KEY` material must remain outside committed docs/source. [VERIFIED: src/puppies/PuppyBootstrap.cpp; VERIFIED: AGENTS.md] |
| Hardware smoke proof | Local fake "pass" rows | Explicit `non-local` or `manual-hardware-required` evidence rows until simulator/hardware artifacts exist [VERIFIED: 10-CONTEXT.md; VERIFIED: tools/bazel/phase9_verify.py] | Phase 10 cannot honestly prove physical RS485, toolchanger, MMU, and long-run updates without external evidence. [VERIFIED: 10-CONTEXT.md] |

**Key insight:** The hard part of Phase 10 is not syntax; it is preventing silent overclaim while preserving complex retained runtime behavior behind typed, inspectable contracts. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: src/puppies/; VERIFIED: src/mmu2/]

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | No repo database/key rename is in Phase 10 scope, but persistent firmware surfaces related to dock/tool offsets and MMU/auxiliary behavior remain compatibility-sensitive. [VERIFIED: 10-CONTEXT.md; VERIFIED: src/gui/screen/toolhead/screen_toolhead_settings_dock.cpp; VERIFIED: src/gui/screen/toolhead/screen_toolhead_settings_nozzle_offset.cpp; VERIFIED: .planning/codebase/ARCHITECTURE.md] | Add source-backed parity rows and avoid schema/storage claims unless the plan adds explicit storage migration evidence. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Live service config | None identified for this phase; locked Phase 10 surfaces are repo-local firmware, manifests, generated resources, Bazel, and `just`, not external service UIs/databases. [VERIFIED: 10-CONTEXT.md] | No live-service migration task required; keep non-local hardware/simulator proof separate from service config. [VERIFIED: 10-CONTEXT.md] |
| OS-registered state | None identified for this phase; no launchd/systemd/Task Scheduler/pm2 registration appears in the locked source surfaces. [VERIFIED: 10-CONTEXT.md] | No OS registration migration task required. [VERIFIED: 10-CONTEXT.md] |
| Secrets/env vars | `SIGNING_KEY` is a CMake cache path to private signing material and must remain outside committed docs/source; D-06 also forbids opaque or credential-like payload values in planning artifacts. [VERIFIED: AGENTS.md; VERIFIED: ProjectOptions.cmake; VERIFIED: 10-CONTEXT.md] | Do not rename or embed secret values; model signing/resource boundaries with source paths and evidence classes only. [VERIFIED: AGENTS.md; VERIFIED: 10-CONTEXT.md] |
| Build artifacts | Firmware binaries, descriptors, DFU/BBF packages, resource images, `.dependencies/` toolchains, Bazel outputs, and CMake build outputs are generated artifacts, not source truth. [VERIFIED: CMakeLists.txt; VERIFIED: src/resources/CMakeLists.txt; VERIFIED: utils/bootstrap.py; VERIFIED: tools/bazel/generated_drift.py; VERIFIED: AGENTS.md] | Plan generator/check labels and packageability manifests; do not commit build outputs unless the repo already tracks the generated artifact and its owning generator requires it. [VERIFIED: AGENTS.md; VERIFIED: tools/bazel/manifests/phase7_generated_outputs.json] |

## Common Pitfalls

### Pitfall 1: Treating CMake Build Options as Implementation Details

**What goes wrong:** Plans miss `DWARF_BINARY_PATH`, `MODULARBED_BINARY_PATH`, `XBUDDY_EXTENSION_BINARY_PATH`, `PUPPY_SKIP_FLASH_FW`, `PUPPY_FLASH_FW`, and `HAS_PUPPIES_BOOTLOADER`. [VERIFIED: ProjectOptions.cmake]

**Why it happens:** The options are spread across feature gates, external project wiring, resource packaging, and board-specific source dispatch. [VERIFIED: ProjectOptions.cmake; VERIFIED: CMakeLists.txt; VERIFIED: src/CMakeLists.txt; VERIFIED: src/resources/CMakeLists.txt]

**How to avoid:** Add a dedicated build/update manifest and verifier checks for these names. [VERIFIED: 10-CONTEXT.md]

**Warning signs:** A plan says "build auxiliary firmware" without naming prebuilt/skip-flash/startup flashing/resource surfaces. [VERIFIED: 10-CONTEXT.md]

### Pitfall 2: Preserving MMU Stub Behavior Without Naming the Defect

**What goes wrong:** `MMUAvailable()` and `UseMMU()` stay unconditional, and the Rust surface appears to support states it cannot inspect. [VERIFIED: src/mmu2/mmu2_reporting.cpp; VERIFIED: .planning/codebase/CONCERNS.md]

**Why it happens:** The reference implementation has known availability/reporting stubs and a puppy/MMU serial stub path. [VERIFIED: src/mmu2/mmu2_reporting.cpp; VERIFIED: src/mmu2/mmu2_serial.cpp]

**How to avoid:** Convert the concern into typed state and manifest disposition rows, or label any behavior change as an intentional delta with regression evidence. [VERIFIED: 10-CONTEXT.md]

**Warning signs:** A Rust API exposes only `available: bool` or a manifest row claims MMU parity without concern disposition. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md]

### Pitfall 3: Normalizing xBuddy Extension MMU Bridge Timing

**What goes wrong:** The plan "cleans up" speculative accepted responses or timeout coupling without recording a compatibility delta. [VERIFIED: include/puppies/xbuddy_extension.hpp; VERIFIED: src/puppies/xbuddy_extension.cpp]

**Why it happens:** The reference includes comments and behavior around accepted-response handling and a timeout window tied to `PuppyModbus::MODBUS_READ_TIMEOUT_MS`. [VERIFIED: src/puppies/xbuddy_extension.cpp; VERIFIED: include/puppies/PuppyModbus.hpp]

**How to avoid:** Make those comments explicit parity rows or typed contracts before any rewrite. [VERIFIED: 10-CONTEXT.md]

**Warning signs:** A manifest mentions xBuddy Extension MMU bridge without `accepted`, `valid response`, or timeout terms. [VERIFIED: src/puppies/xbuddy_extension.cpp; VERIFIED: 10-CONTEXT.md]

### Pitfall 4: Treating the Representative XBE Manifest as Product Truth

**What goes wrong:** The planner copies existing representative-product fixture data without reconciling it with current feature gates. [VERIFIED: tools/bazel/manifests/representative_products.json; VERIFIED: ProjectOptions.cmake]

**Why it happens:** Prior manifests exposed xBuddy Extension as an auxiliary profile fixture, while `ProjectOptions.cmake` gates standard xBuddy Extension to `COREONE` and the xBuddy Extension firmware CMake also has a source-level `iX` variant branch. [VERIFIED: tools/bazel/manifests/representative_products.json; VERIFIED: ProjectOptions.cmake; VERIFIED: src/puppy/xbuddy_extension/CMakeLists.txt]

**How to avoid:** Treat product/board combinations as manifest claims backed by current source gates, not by prior fixture names alone. [VERIFIED: 10-CONTEXT.md; VERIFIED: ProjectOptions.cmake]

**Warning signs:** A Phase 10 row lists XBE with XL product semantics without explaining the source path or reference-deferred status. [VERIFIED: tools/bazel/manifests/representative_products.json; VERIFIED: ProjectOptions.cmake]

### Pitfall 5: Claiming Hardware Proof From Local Source Checks

**What goes wrong:** The verifier passes locally and the phase claims RS485, toolchanger, MMU, or long-run update behavior is fully proven. [VERIFIED: 10-CONTEXT.md]

**Why it happens:** Phase verifiers can check source-backed contracts but cannot create physical hardware evidence. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: 10-CONTEXT.md]

**How to avoid:** Require `proof_scope` or equivalent fields and reject overclaim wording. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: 10-CONTEXT.md]

**Warning signs:** Validation artifacts lack `non-local`, `manual-hardware-required`, `simulator-flow`, or `hardware-smoke` status for hardware-dependent rows. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: 10-CONTEXT.md]

## Code Examples

Verified patterns from local sources:

### Manifest Row Shape

```json
{
  "id": "IFCE-06-XBE-MMU-BRIDGE-001",
  "requirement_id": "IFCE-06",
  "retained_source_paths": [
    "include/puppies/xbuddy_extension.hpp",
    "src/puppies/xbuddy_extension.cpp",
    "include/puppies/PuppyModbus.hpp"
  ],
  "reference_behavior": "MMU request state and valid-response timing are modeled as retained compatibility behavior.",
  "rust_surface": "buddy_domain::auxiliary::MmuTransportState",
  "evidence_class": "static-source-audit",
  "proof_scope": "local-source",
  "build_or_update_surface": "tools/bazel/manifests/phase10_mmu_transport.json",
  "intentional_delta": "none"
}
```

This row shape is directly derived from D-03 and the existing verifier/manifest pattern. [VERIFIED: 10-CONTEXT.md; VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/manifests/phase7_resources.json]

### Rust State Contract

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MmuTransportState {
    Disabled,
    Unavailable,
    Bootloader,
    Stopped,
    Active,
    Updating,
    UpdateFailed,
    CommunicationFault,
    UnknownReferenceDeferred,
}
```

This contract maps the D-08 state requirement and the MMU availability concern into inspectable Rust states. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: src/mmu2/mmu2_reporting.cpp]

### Verifier Ordering Through just

```make
phase10-verify:
    bazel run //tools/bazel:phase10_verify_tests
    bazel run //tools/bazel:phase10_verify
```

The ordering mirrors prior phase recipes that run verifier tests before aggregate verification. [VERIFIED: justfile]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Freehand parity notes in planning artifacts | Source-backed manifests plus deterministic phase verifiers | Established by prior Rust+Bazel phases before Phase 10 [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/phase8_verify.py; VERIFIED: tools/bazel/phase9_verify.py] | Phase 10 plans should add rows/checks, not prose-only claims. [VERIFIED: 10-CONTEXT.md] |
| Boolean or stubbed availability for MMU/runtime surfaces | Typed state contracts with concern dispositions | Required by Phase 10 decisions [VERIFIED: 10-CONTEXT.md] | Planner must handle disabled/unavailable/bootloader/stopped/active/update/fault/reference-deferred states. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md] |
| CMake as build truth | Bazel Primary Now with CMake as reference/comparison | Project constraint and Phase 10 decision [VERIFIED: AGENTS.md; VERIFIED: 10-CONTEXT.md] | Plans must expose Bazel labels/manifests for auxiliary build/package/update surface. [VERIFIED: 10-CONTEXT.md] |
| Local verifier pass as enough for all behavior | Local proof plus explicit non-local evidence classification | Established by prior phase verifier pattern and Phase 10 decision [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: 10-CONTEXT.md] | Hardware and long-run update claims must remain non-local unless backed by artifacts. [VERIFIED: 10-CONTEXT.md] |

**Deprecated/outdated:**

- Treating `MMUAvailable()`/`UseMMU()` as a complete compatibility contract is outdated for Phase 10 because the current concern ledger says those functions cannot represent disabled, unavailable, bootloader, stopped, active, or fault states reliably. [VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: src/mmu2/mmu2_reporting.cpp; VERIFIED: 10-CONTEXT.md]
- Treating xBuddy Extension as a generic STM32H5 target is out of bounds because Phase 10 locks STM32H503 xBuddy Extension as a special retained runtime surface. [VERIFIED: 10-CONTEXT.md; VERIFIED: src/puppy/xbuddy_extension/]

## Assumptions Log

All claims in this research were verified from repo files, local command probes, user-provided phase context, or cited official documentation. No assumed-provenance claims are intentionally present. [VERIFIED: this research session]

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| - | No assumed claims recorded. [VERIFIED: this research session] | - | - |

## Open Questions (RESOLVED)

1. **Which non-local artifacts, if any, should Phase 10 create instead of deferring to Phase 11?**  
   What we know: The context allows simulator or hardware-smoke evidence if concrete artifacts exist, but says full physical auxiliary-controller, RS485, toolchanger/dock, MMU, and long-run update proof remain Phase 11 unless Phase 10 adds explicit evidence. [VERIFIED: 10-CONTEXT.md]  
   Resolution: Phase 10 should plan local source-backed manifests, Rust domain contracts, Bazel/`just` verification, and non-local evidence placeholders. It should not require physical hardware, live RS485/MMU/toolchanger proof, long-run update proof, or final cutover proof for local green verification unless a specific plan adds concrete simulator or hardware-smoke artifacts. [VERIFIED: 10-CONTEXT.md; VERIFIED: 10-VALIDATION.md]

2. **How should the xBuddy Extension `iX` source branch be represented?**  
   What we know: `ProjectOptions.cmake` enables standard xBuddy Extension for `COREONE`, while `src/puppy/xbuddy_extension/CMakeLists.txt` contains a source branch for `iX`. [VERIFIED: ProjectOptions.cmake; VERIFIED: src/puppy/xbuddy_extension/CMakeLists.txt]  
   Resolution: Phase 10 should add an explicit concern or manifest row for the `iX` branch and mark it as retained/reference-deferred unless the source-backed product gates prove it is an active supported production combination. Do not silently enable an unsupported xBuddy Extension product profile and do not collapse the branch into generic H5 support. [VERIFIED: 10-CONTEXT.md; VERIFIED: ProjectOptions.cmake; VERIFIED: src/puppy/xbuddy_extension/CMakeLists.txt]

3. **Does Phase 10 fix MMU availability/reporting stubs or only model them?**  
   What we know: D-11 requires disposition of the concern, and D-14 allows intentional deltas only when named and tested. [VERIFIED: 10-CONTEXT.md]  
   Resolution: Phase 10 should first model the MMU availability/reporting states and concern disposition as typed Rust/domain and manifest contracts. Runtime behavior changes are not required by default; any fix to `MMUAvailable()` or `UseMMU()` must be a named intentional delta with regression evidence. [VERIFIED: 10-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 10 verifier and tests | yes [VERIFIED: local `python3 --version` probe on 2026-06-14] | 3.14.4 [VERIFIED: local `python3 --version` probe on 2026-06-14] | Project minimum is Python 3.8+; use bootstrap-managed environment if local packages are needed. [VERIFIED: README.md; VERIFIED: utils/bootstrap.py] |
| Bazel | Phase 10 labels and queryability | yes [VERIFIED: local `bazel --version` probe on 2026-06-14] | 9.1.1 [VERIFIED: local `bazel --version` probe on 2026-06-14] | No fallback for Bazel-primary verification. [VERIFIED: AGENTS.md; VERIFIED: 10-CONTEXT.md] |
| just | Developer verification facade | yes [VERIFIED: local `just --version` probe on 2026-06-14] | 1.48.0 [VERIFIED: local `just --version` probe on 2026-06-14] | Direct `bazel run` commands can execute labels, but the phase should still add `just phase10-verify`. [VERIFIED: justfile; VERIFIED: 10-CONTEXT.md] |
| cargo | Rust fmt/lint/build/tests | yes [VERIFIED: local `cargo --version` probe on 2026-06-14] | 1.91.1 [VERIFIED: local `cargo --version` probe on 2026-06-14] | No fallback for Rust domain verification. [VERIFIED: Cargo.toml; VERIFIED: 10-CONTEXT.md] |
| rustc | Rust crate compilation | yes [VERIFIED: local `rustc --version` probe on 2026-06-14] | 1.91.1 [VERIFIED: local `rustc --version` probe on 2026-06-14] | Rust workspace declares minimum 1.85. [VERIFIED: Cargo.toml] |
| CMake | Reference build/source inspection and optional comparison | yes [VERIFIED: local `cmake --version` probe on 2026-06-14] | 3.27.9 [VERIFIED: local `cmake --version` probe on 2026-06-14] | Repo bootstrap downloads pinned CMake for normal firmware builds. [VERIFIED: utils/bootstrap.py] |
| Ninja | Reference CMake build backend | yes [VERIFIED: local `ninja --version` probe on 2026-06-14] | 1.13.2 [VERIFIED: local `ninja --version` probe on 2026-06-14] | Repo bootstrap downloads pinned Ninja. [VERIFIED: utils/bootstrap.py] |
| `arm-none-eabi-objcopy` | MMU firmware resource conversion and full firmware packaging reference | no on PATH [VERIFIED: local `command -v arm-none-eabi-objcopy` probe on 2026-06-14] | - | Bootstrap-managed GCC Arm None Eabi under `.dependencies/` or Bazel-owned toolchain setup. [VERIFIED: utils/bootstrap.py; VERIFIED: src/resources/CMakeLists.txt] |
| pre-commit | Repo formatting/generated-file checks | no on PATH [VERIFIED: local `command -v pre-commit` probe on 2026-06-14] | - | Install via project requirements/bootstrap before pre-commit-only checks. [VERIFIED: requirements.txt; VERIFIED: utils/bootstrap.py; VERIFIED: .pre-commit-config.yaml] |

**Missing dependencies with no fallback:**

- None for local Phase 10 research and contract verification, because Python, Bazel, just, cargo, rustc, CMake, and Ninja are available. [VERIFIED: local environment audit on 2026-06-14]

**Missing dependencies with fallback:**

- `arm-none-eabi-objcopy` is missing on PATH; full MMU firmware conversion/package comparison should use bootstrap-managed toolchains or be recorded as non-local/full-build evidence. [VERIFIED: local environment audit on 2026-06-14; VERIFIED: utils/bootstrap.py; VERIFIED: src/resources/CMakeLists.txt]
- `pre-commit` is missing on PATH; use bootstrap/project requirements before running pre-commit hooks. [VERIFIED: local environment audit on 2026-06-14; VERIFIED: requirements.txt; VERIFIED: .pre-commit-config.yaml]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib verifier tests plus Rust unit tests plus Bazel `sh_binary` labels. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: Cargo.toml] |
| Config file | `.planning/config.json` enables `workflow.nyquist_validation`; `Cargo.toml`, `tools/bazel/BUILD.bazel`, `BUILD.bazel`, and `justfile` provide verification wiring. [VERIFIED: .planning/config.json; VERIFIED: Cargo.toml; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile] |
| Quick run command | `python3 tools/bazel/phase10_verify.py --quick` after the verifier exists. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: 10-CONTEXT.md] |
| Full suite command | `just phase10-verify` after the recipe exists. [VERIFIED: justfile; VERIFIED: 10-CONTEXT.md] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| IFCE-06 | Required auxiliary-controller source surfaces are present in manifests with source paths and evidence classes. [VERIFIED: 10-CONTEXT.md] | manifest/schema unit | `python3 tools/bazel/phase10_verify.py --manifests-only` [VERIFIED: tools/bazel/phase9_verify.py] | no, Wave 0 gap [VERIFIED: repository scan on 2026-06-14] |
| IFCE-06 | Rust domain exposes typed auxiliary states, identities, update modes, MMU transport state, and fault classes without `unsafe`. [VERIFIED: 10-CONTEXT.md] | Rust unit/API check | `cargo test -p buddy-domain auxiliary` and `python3 tools/bazel/phase10_verify.py --rust-only` [VERIFIED: Cargo.toml; VERIFIED: tools/bazel/phase9_verify.py] | no, Wave 0 gap [VERIFIED: repository scan on 2026-06-14] |
| IFCE-06 | Bazel and `just` expose Phase 10 verifier labels and a quick aggregate recipe. [VERIFIED: 10-CONTEXT.md] | build graph smoke | `bazel query //tools/bazel:phase10_verify && bazel run //tools/bazel:phase10_verify_tests && just phase10-verify` [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile] | no, Wave 0 gap [VERIFIED: repository scan on 2026-06-14] |
| IFCE-06 | Build/package/update rows cover Dwarf, ModularBed, xBuddy Extension, MMU firmware resources, descriptor generation, prebuilt paths, skip-flash, crash dump, and update flows. [VERIFIED: 10-CONTEXT.md; VERIFIED: ProjectOptions.cmake; VERIFIED: CMakeLists.txt; VERIFIED: src/resources/CMakeLists.txt] | manifest/source audit | `python3 tools/bazel/phase10_verify.py --package-update-only` [VERIFIED: tools/bazel/phase9_verify.py] | no, Wave 0 gap [VERIFIED: repository scan on 2026-06-14] |
| IFCE-06 | Hardware/simulator/manual-only proof is not overclaimed. [VERIFIED: 10-CONTEXT.md] | validation artifact and wording check | `python3 tools/bazel/phase10_verify.py --evidence-only` [VERIFIED: tools/bazel/phase9_verify.py] | no, Wave 0 gap [VERIFIED: repository scan on 2026-06-14] |

### Sampling Rate

- **Per task commit:** Run the focused verifier mode plus affected Rust tests, for example `python3 tools/bazel/phase10_verify.py --rust-only` and `cargo test -p buddy-domain auxiliary`. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: Cargo.toml]
- **Per wave merge:** Run `bazel run //tools/bazel:phase10_verify_tests`, `bazel run //tools/bazel:phase10_verify`, and the relevant Rust workflow command. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh]
- **Phase gate:** Run `just phase10-verify`, plus explicit non-local evidence review for simulator/hardware/manual rows. [VERIFIED: justfile; VERIFIED: 10-CONTEXT.md]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase10_auxiliary_controllers.json` - covers controller families, Dwarf, ModularBed, xBuddy Extension, and runtime states for IFCE-06. [VERIFIED: 10-CONTEXT.md]
- [ ] `tools/bazel/manifests/phase10_mmu_transport.json` - covers MMU2 availability/reporting, bootloader, UART/puppy transport, firmware resource, and update states for IFCE-06. [VERIFIED: 10-CONTEXT.md; VERIFIED: src/mmu2/]
- [ ] `tools/bazel/manifests/phase10_modbus_rs485.json` - covers LightModbus, RS485 request/retry/timeout/skipped/error behavior, and XBE MMU bridge timing for IFCE-06. [VERIFIED: include/puppies/PuppyModbus.hpp; VERIFIED: src/puppies/PuppyModbus.cpp; VERIFIED: src/puppies/xbuddy_extension.cpp]
- [ ] `tools/bazel/manifests/phase10_toolchanger_dock_offsets.json` - covers toolchanger update/init and dock/tool offset source surfaces for IFCE-06. [VERIFIED: src/puppies/puppy_task.cpp; VERIFIED: lib/AddMarlin.cmake; VERIFIED: src/gui/screen/toolhead/screen_toolhead_settings_dock.cpp; VERIFIED: src/gui/screen/toolhead/screen_toolhead_settings_nozzle_offset.cpp]
- [ ] `tools/bazel/manifests/phase10_auxiliary_build_update.json` - covers CMake external projects, descriptor generation, resource paths, prebuilt binary paths, skip-flash, startup flashing, crash dump, and update evidence for IFCE-06. [VERIFIED: ProjectOptions.cmake; VERIFIED: CMakeLists.txt; VERIFIED: src/resources/CMakeLists.txt; VERIFIED: src/puppies/PuppyBootstrap.cpp]
- [ ] `tools/bazel/manifests/phase10_concern_dispositions.json` - covers MMU availability/reporting, xBuddy Extension H503 special handling, BuddyHeaders/error-code coupling if touched, and intentional deltas. [VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: 10-CONTEXT.md]
- [ ] `rust/crates/domain/src/auxiliary.rs` and optional `rust/crates/domain/src/auxiliary/` submodules. [VERIFIED: rust/crates/domain/src/lib.rs; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]
- [ ] `tools/bazel/phase10_verify.py` and `tools/bazel/phase10_verify_test.py`. [VERIFIED: tools/bazel/phase9_verify.py]
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` Phase 10 wiring. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]
- [ ] `.planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VALIDATION.md` after implementation evidence exists. [VERIFIED: .planning/config.json; VERIFIED: 10-CONTEXT.md]

## Security Domain

OWASP ASVS is a web-application security verification standard, and the official ASVS page says the latest stable version is 5.0.0 as of the 2026-06-14 research session. [CITED: https://owasp.org/www-project-application-security-verification-standard/] For this embedded firmware phase, ASVS categories are used as a structured security checklist rather than a claim that the firmware is a web application. [VERIFIED: AGENTS.md; CITED: https://owasp.org/www-project-application-security-verification-standard/]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no for Phase 10 domain contracts; Phase 10 does not add user authentication flows. [VERIFIED: 10-CONTEXT.md] | No new auth control; do not embed credential-like payloads in artifacts. [VERIFIED: 10-CONTEXT.md] |
| V3 Session Management | no for Phase 10 domain contracts; no web/session state is introduced by the auxiliary parity contracts. [VERIFIED: 10-CONTEXT.md] | No session control required in Phase 10. [VERIFIED: 10-CONTEXT.md] |
| V4 Access Control | yes for firmware/update authority boundaries and valid product/controller combinations. [VERIFIED: ProjectOptions.cmake; VERIFIED: rust/crates/domain/src/product.rs; VERIFIED: 10-CONTEXT.md] | Use typed product/controller/update state checks and source-backed manifests instead of accepting arbitrary combinations. [VERIFIED: rust/crates/domain/src/product.rs; VERIFIED: 10-CONTEXT.md] |
| V5 Input Validation | yes for manifest schema, resource paths, Modbus IDs/request kinds, firmware image source, dock identity, and tool offset identity. [VERIFIED: 10-CONTEXT.md; VERIFIED: rust/crates/domain/src/resource.rs] | Use fallible Rust constructors, enum parsing, JSON schema-like verifier checks, and resource path parsing patterns. [VERIFIED: rust/crates/domain/src/resource.rs; VERIFIED: tools/bazel/phase9_verify.py] |
| V6 Cryptography | yes for retained firmware signing/fingerprint/update boundaries, but Phase 10 should not implement new cryptography. [VERIFIED: src/puppies/PuppyBootstrap.cpp; VERIFIED: ProjectOptions.cmake; VERIFIED: AGENTS.md] | Preserve reference behavior and never hand-roll hashing/signing/key handling in Phase 10 contracts. [VERIFIED: src/puppies/PuppyBootstrap.cpp; VERIFIED: AGENTS.md] |

### Known Threat Patterns for Auxiliary Controller Parity

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unsupported controller/product combination accepted by Rust contracts | Elevation of privilege / Tampering | Fallible constructors and product compatibility checks backed by `ProjectOptions.cmake` and `product.rs`. [VERIFIED: ProjectOptions.cmake; VERIFIED: rust/crates/domain/src/product.rs] |
| Resource path traversal or opaque firmware payload in planning artifacts | Tampering / Information disclosure | Reuse `ResourceRuntimePath` parsing and D-06 source-backed path policy. [VERIFIED: rust/crates/domain/src/resource.rs; VERIFIED: 10-CONTEXT.md] |
| Forged local hardware proof | Spoofing / Repudiation | Evidence classes and verifier overclaim guards must distinguish local source proof from simulator/hardware/manual evidence. [VERIFIED: 10-CONTEXT.md; VERIFIED: tools/bazel/phase9_verify.py] |
| Modbus timeout or accepted-response semantic drift | Tampering / Denial of service | Source-backed parity rows for `PuppyModbus` timeout/retry behavior and XBE MMU bridge timing. [VERIFIED: include/puppies/PuppyModbus.hpp; VERIFIED: src/puppies/PuppyModbus.cpp; VERIFIED: src/puppies/xbuddy_extension.cpp] |
| Update state ambiguity after failed bootload/flash | Tampering / Denial of service | Typed update and runtime states: updating, update-failed, bootloader, communication-fault, unknown/reference-deferred. [VERIFIED: 10-CONTEXT.md; VERIFIED: src/puppies/PuppyBootstrap.cpp; VERIFIED: src/mmu2/mmu2_bootloader.cpp] |
| Secret/key disclosure through planning artifacts | Information disclosure | Keep `SIGNING_KEY` and opaque payloads out of committed docs; use source paths and evidence classes. [VERIFIED: AGENTS.md; VERIFIED: ProjectOptions.cmake; VERIFIED: 10-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-CONTEXT.md` - user decisions, phase boundary, lifecycle ID, verification/non-local evidence boundary. [VERIFIED]
- `.planning/REQUIREMENTS.md` - IFCE-06 requirement text and phase mapping. [VERIFIED]
- `.planning/STATE.md` - active Phase 10 focus. [VERIFIED]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` - project-local workflow, Bazel/Rust/Bright Builds constraints, and override status. [VERIFIED]
- `ProjectOptions.cmake`, `CMakeLists.txt`, `src/CMakeLists.txt`, `src/resources/CMakeLists.txt`, `lib/AddMarlin.cmake`, `lib/AddMMU2.cmake`, `lib/AddLiblightmodbus.cmake` - reference build, feature, resource, and auxiliary packaging behavior. [VERIFIED]
- `src/puppies/`, `include/puppies/`, `src/puppy/`, `src/mmu2/`, `lib/Prusa-Firmware-MMU/`, `lib/liblightmodbus/` - reference runtime/protocol surfaces. [VERIFIED]
- `rust/crates/domain/src/product.rs`, `rust/crates/domain/src/feature.rs`, `rust/crates/domain/src/resource.rs`, `rust/crates/runtime-adapter/src/lib.rs` - existing Rust contract surfaces. [VERIFIED]
- `tools/bazel/phase6_verify.py`, `tools/bazel/phase7_verify.py`, `tools/bazel/phase8_verify.py`, `tools/bazel/phase9_verify.py`, `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - established verifier/Bazel/just patterns. [VERIFIED]
- `.planning/codebase/CONCERNS.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/INTEGRATIONS.md` - known concerns and mapped integration surfaces. [VERIFIED]

### Secondary (MEDIUM confidence)

- Bright Builds pinned canonical standards: architecture, code-shape, testing, verification, and Rust pages at `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/...` - project-required standards referenced from AGENTS. [CITED]
- OWASP ASVS project page `https://owasp.org/www-project-application-security-verification-standard/` - ASVS purpose and latest stable version 5.0.0 during research. [CITED]

### Tertiary (LOW confidence)

- None. [VERIFIED: this research session]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - no new external package recommendation; stack is repo-owned Rust/Bazel/just/Python plus retained source oracles verified from local files. [VERIFIED: Cargo.toml; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile; VERIFIED: 10-CONTEXT.md]
- Architecture: HIGH - follows explicit user decisions and existing Phase 6 through Phase 9 verifier/manifest pattern. [VERIFIED: 10-CONTEXT.md; VERIFIED: tools/bazel/phase9_verify.py]
- Pitfalls: HIGH - each pitfall maps to source files or known concern ledger entries. [VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: src/mmu2/mmu2_reporting.cpp; VERIFIED: src/puppies/xbuddy_extension.cpp; VERIFIED: ProjectOptions.cmake]
- Environment: HIGH for local probes, MEDIUM for bootstrap fallback until bootstrap is rerun in an implementation phase. [VERIFIED: local command probes on 2026-06-14; VERIFIED: utils/bootstrap.py]

**Research date:** 2026-06-14  
**Valid until:** 2026-07-14 for local source-map and contract-planning facts; re-run environment probes before execution. [VERIFIED: this research session]
