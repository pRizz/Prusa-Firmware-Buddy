# Project Research Summary

**Project:** Prusa Firmware Buddy Rust Port
**Domain:** Behavior-parity Rust+Bazel rewrite of STM32/FreeRTOS 3D printer firmware
**Researched:** 2026-06-02
**Confidence:** HIGH for roadmap direction; MEDIUM for exact board-level toolchain and hardware validation details

## Executive Summary

This project is a safety-relevant brownfield firmware replacement, not a greenfield Rust experiment. The current C/C++/CMake Prusa-Firmware-Buddy codebase remains the behavioral oracle, and the Rust firmware is only credible when it preserves supported printer behavior, release artifacts, generated resources, persistent storage compatibility, UI flows, networking, transfers, safety behavior, auxiliary-board behavior, and simulator/hardware evidence. Experts should build this as a product family with an explicit build matrix, typed product profiles, deterministic generation, retained foreign-code boundaries, and continuous reference comparison.

The recommended approach is Bazel primary from the start, using pinned Bazel 9.1.0, Bzlmod, rules_rust 0.70.0, Rust 1.96.0 stable with edition 2024, `no_std` firmware crates, rules_cc for retained C/ASM/vendor code, and a small `justfile` facade for common workflows. Keep FreeRTOS, STM32 HAL/CMSIS, startup/linker code, LwIP, mbedTLS, filesystems, TinyUSB, and other vendor/runtime components behind explicit Rust adapter crates initially. Use Rust where it matters most first: product profiles, state machines, parser boundaries, command validation, storage schemas, transfer states, UI workflow state, safety policy, and application orchestration.

The main risks are behavior drift hidden behind a successful boot, hardware safety changes hidden behind "safe Rust", Bazel becoming a non-hermetic CMake clone, wrong cross-compilation/linker choices, ambiguous retained vendor code, and tests that are too narrow for a Big Bang cutover. Mitigate these by starting with a reference baseline and safety envelope, creating a parity exception ledger for known defects, proving Bazel toolchains and release artifacts early, isolating all `unsafe` and FFI in adapters, moving generated assets into Bazel-owned rules, and making parity tests continuous rather than a final sweep.

## Key Findings

### Recommended Stack

The stack should make Bazel the single authority for firmware images, host tools, generated assets, tests, and release packages. Cargo may remain useful for crate metadata or IDE support, but product builds and artifacts must come from Bazel. Firmware crates should default to `no_std`; `std` belongs in host tools, generators, simulator helpers, and tests. Retained C/ASM/vendor code is expected in v1, but it must be owned by Bazel packages and wrapped by narrow Rust adapters.

Use explicit versions and toolchain registration rather than inheriting developer-local tools. The first implementation phase should validate each MCU family, target triple, linker script, vector table, panic strategy, objcopy/map output, FFI ABI, and artifact format before broader subsystem work depends on it.

**Core technologies:**

- Bazel 9.1.0: authoritative build/test/package graph - required for one declared graph across Rust, retained C/ASM, generators, resources, simulator tests, and firmware artifacts.
- Bzlmod / `MODULE.bazel`: external dependency model - current Bazel dependency flow and the documented path for rules_rust and Bazel Central Registry modules.
- rules_rust 0.70.0: Rust toolchains and Bazel Rust rules - supports Rust libraries, binaries, tests, crate integration, embedded targets, and Rust-side objcopy integration.
- Rust 1.96.0 stable, edition 2024: firmware and host Rust compiler - pin through Bazel instead of relying on local installations.
- Rust `no_std`: firmware crate environment - keep allocation and runtime assumptions explicit on constrained STM32 targets.
- Rust Cortex-M targets: likely `thumbv7em-none-eabihf` for STM32F4/M4F, `thumbv6m-none-eabi` for STM32G0/M0+, and an STM32H5/M33 `thumbv8m.main-*` target after FPU validation.
- rules_cc 0.2.19: retained C/ASM/vendor build support - required for startup, HAL/CMSIS, FreeRTOS, LwIP, mbedTLS, FatFs/littlefs, TinyUSB, and other retained code.
- ARM GNU / ST C toolchain: C/ASM compiler/linker support - register in Bazel and keep artifact production out of CMake.
- FreeRTOS: retained scheduler initially - changing scheduler while rewriting language and build system would multiply timing and task-ordering risk.
- STM32 HAL/CMSIS C stack: retained initially - preserve board behavior and expose only typed Rust-facing peripheral capabilities.
- just 1.51.0: developer workflow facade - small wrappers around Bazel/Rust commands, not a second build system.

**Supporting Rust libraries and tools:**

- `cortex-m`, optional `cortex-m-rt`, `critical-section`, `embedded-hal` 1.0.0, `embedded-io`, `embedded-storage`, `heapless`, and `static_cell` for low-level embedded APIs, typed hardware boundaries, fixed-capacity data, and static ownership.
- `defmt`, `defmt-rtt`, `panic-probe`, `rtt-target`, and `probe-rs` for probe/debug profiles, not as an unapproved replacement for production logging behavior.
- rules_python and rules_pkg for existing Python tooling, simulator/parity tests, and package primitives where they fit.

### Expected Features

For this project, features are parity deliverables and acceptance gates. v1 is not a reduced MVP; v1 is the replacement cutover. A feature can be omitted only if the supported reference firmware behavior is explicitly descoped.

**Must have (table stakes):**

- Supported printer, board, MCU, bootloader, and artifact matrix - preserve COREONE, MINI, MK4, MK3.5, XL, iX, XL_DEV_KIT, Buddy/XBuddy/XLBuddy/Dwarf/ModularBed/xBuddy Extension variants, boot/noboot modes, debug/release outputs, `.bin`, `.bbf`, `.dfu`, `.map`, metadata, signing, and resource images.
- Bazel-primary build and `justfile` workflow parity - build firmware, host tools, generated assets, unit tests, simulator/integration inputs, release artifacts, and auxiliary firmware through Bazel.
- STM32 startup, HAL/CMSIS, linker, FreeRTOS, and task orchestration - preserve board startup, interrupts, memory layout, watchdogs, task dependencies, filesystem/network/display/connect/puppy startup, and crash/error paths.
- Marlin-derived printing core and Buddy bridge behavior - preserve G-code, planner-visible behavior, thermal state, pause/resume/cancel, `marlin_server`/`marlin_client`, BGcode/file parsing, and GUI/Connect command routing.
- Safety-critical thermal, motion, selftest, and recovery behavior - preserve safe outputs, watchdog/assert/BSOD/redscreen flows, min/max/runaway errors, calibration, crash detection, power panic, emergency stop, and selftests.
- Printer-specific feature gates - preserve sensors, TMC paths, homing, phase/burst stepping, input shaper, loadcell, beds, ESP flashing, displays/touch, LEDs, MMU2, NFC, door/chamber, nozzle cleaner, toolchanger, and xBuddy Extension behavior by valid product combination.
- GUI workflows for supported display classes - preserve 240x320 and 480x320 layouts, dialogs, menus, wizards, warnings, redscreens, translations, print controls, registration, and layout/text-fit behavior.
- Networking, Prusa Connect, PrusaLink/WUI, transfers, TLS, telemetry, and service protocols - preserve registration, tokens/fingerprints, events, WebSocket-current behavior, TLS 1.2 verification, current proxy limitations, custom certificate behavior after fix, API v1, OctoPrint-compatible endpoints, WUI assets, auth, downloads, SNTP, mDNS, metrics, and syslog.
- Persistent configuration, migrations, filesystems, settings import/export, and credentials - treat config storage as a compatibility protocol with schema/hash/migration fixtures.
- Resources, localization, fonts, web assets, ESP blobs, bootloader resources, and generated files - put deterministic generation and drift checks under Bazel.
- Puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, and toolchanger ecosystem - treat auxiliary firmware and Modbus/RS485 protocols as first-class product behavior.
- Observability, diagnostics, support artifacts, and verification gates - preserve logs, metrics, crash dump export behavior, provenance, map files, memory reports, simulator logs, and expand parity evidence.

**Should have (competitive):**

- Typed printer/board/feature/artifact model - invalid product combinations should fail at Bazel analysis or Rust construction boundaries.
- Pure state-machine cores with thin adapters - make G-code, Connect, transfers, config migrations, UI workflows, selftests, and puppy behavior cheap to unit test.
- Hermetic Bazel code generation and packaging - eliminate generated asset drift and make releases reproducible.
- Explicit foreign-code boundary manifest - make retained C/C++/ASM/vendor code visible, owned, justified, and testable.
- Rust safety wrappers for RTOS, queues, locks, DMA/buffers, filesystem handles, sockets, TLS contexts, and hardware resources - narrow and document `unsafe`.
- Defect-remediation parity gate - fix known concerns where appropriate, but track each fix as an intentional delta.
- Reference-firmware comparison harness - compare artifacts, protocol traces, simulator flows, storage migrations, safety errors, UI states, and resource hashes against the C/C++ reference.
- Developer workflow convergence through `just` - provide discoverable commands such as `just bootstrap`, `just build`, `just test`, `just fmt`, `just lint`, `just codegen-check`, `just sim-test`, and `just release`.

**Defer (v2+):**

- New printer UX or product features - defer until parity is proven.
- Multi-transfer or concurrent transfer redesign - current single-slot semantics are a compatibility constraint.
- Broad proxy authentication, enterprise TLS modes, or new cloud APIs - preserve current network behavior first.
- Full Rust replacement of every vendor/upstream component - replace only after contracts, licensing, update cadence, and hardware tests justify the churn.
- New display resolutions or UI frameworks - defer unless required by current supported printers.

### Architecture Approach

Use functional core / imperative shell adapted to embedded firmware. Pure Rust domain crates should own printer/product profiles, G-code and protocol parsing, print and transfer state, thermal/safety policies, config migrations, UI navigation state, resource manifests, and puppy/MMU protocol state. Application crates orchestrate those decisions over traits. Adapter crates own effects: startup, linker symbols, HAL/CMSIS, FreeRTOS, queues, mutexes, DMA, filesystems, sockets, TLS, display/touch I/O, watchdogs, flash writes, random numbers, logging sinks, and retained C/C++/ASM FFI.

**Major components:**

1. Bazel product matrix and release graph - models printers, boards, MCUs, bootloader modes, display/resource/network axes, toolchains, generators, packages, and parity targets.
1. Firmware entry binaries - small board/personality entrypoints for master boards and auxiliary firmware that wire product profile, startup, adapters, panic policy, and task graph.
1. Pure Rust domain crates - typed product capabilities, G-code, motion intents, thermal policy, config schema, Connect protocol, transfer model, UI model, resources, and puppy protocol.
1. Application orchestrators - print, Connect, transfer, UI, and startup controllers that sequence domain decisions without owning raw hardware or C state.
1. Adapter crates - safe facades over HAL, FreeRTOS, LwIP, mbedTLS, FatFs/littlefs, TinyUSB, display/touch, logging, CrashCatcher, and vendor FFI.
1. Foreign packages - retained C/ASM/C++/vendor libraries with private visibility, inventory entries, retention reason, safe facade, and tests.
1. Assets and tools - source assets, deterministic generators, package tools, resource images, translations, fonts, WUI/ESP/puppy blobs, and metadata.
1. Parity harnesses - reference artifact diffs, pure domain corpora, adapter contracts, simulator comparisons, hardware smoke matrix, and intentional delta ledger.

### Critical Pitfalls

1. **Behavior parity becomes "it builds and prints a demo"** - capture executable reference fixtures before subsystem rewrites, compare every behavior class continuously, and keep known bug fixes in a parity exception ledger.
1. **Hardware safety changes hide behind safer-looking Rust** - define a board-by-board safety envelope, keep MMIO/FFI/interrupts in reviewed adapters, and exercise safe-state, watchdog, panic/fault, heater, motor, fan, endstop, probe, and startup error paths.
1. **Bazel becomes a non-hermetic CMake clone or selects the wrong cross-compilation world** - define explicit platforms/toolchains, declared generator inputs/outputs, linker scripts, target triples, C ABI flags, objcopy/map checks, and artifact parity tests from the start.
1. **Retained vendor code is neither owned nor replaced** - inventory every retained C/C++/ASM/vendor island with upstream/version/license, retention reason, boundary, unsafe invariants, tests, and replacement posture.
1. **Parity tests are too narrow for a Big Bang cutover** - use a full pyramid: pure Rust unit tests, adapter contract tests, reference fixtures, simulator flows, network/TLS suites, generated drift checks, release artifact checks, and hardware matrix evidence.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Reference Baseline and Safety Envelope

**Rationale:** The Big Bang posture removes incremental production feedback, so the first deliverable must be an executable definition of "same behavior" and "safe hardware state" before implementation can drift.

**Delivers:** Current product/build/artifact inventory, reference fixtures, supported-printer matrix, safety envelope, known concern ledger, parity exception ledger, cutover checklist, and initial test pyramid design.

**Addresses:** Behavior-parity baseline, safety-critical behavior, known concern disposition, reference comparison strategy, and test sufficiency.

**Avoids:** Demo-only parity, silent safety changes, known bugs being fossilized or silently changed, and final-phase discovery of missing test categories.

### Phase 2: Bazel/Rust Toolchain and Artifact Parity

**Rationale:** Bazel is a project decision, not a later cleanup. Toolchains, platforms, generators, and release artifacts must be reliable before subsystem code depends on them.

**Delivers:** `MODULE.bazel`, `.bazelversion`, `.bazelrc`, toolchain registration, Rust/C/C++/ASM cross-compilation spike, initial product platforms, generated product profile crate/data, `justfile`, generator/check targets, minimal firmware link per MCU family, and reference-vs-Rust artifact checks for early products.

**Uses:** Bazel 9.1.0, Bzlmod, rules_rust 0.70.0, Rust 1.96.0, rules_cc 0.2.19, ARM GNU/ST toolchain, rules_python, rules_pkg, and just 1.51.0.

**Implements:** Bazel product matrix, toolchains, firmware image rules, generated option/resource ownership, and artifact parity harnesses.

**Avoids:** Non-hermetic Bazel, CMake-as-release-authority, wrong linker/target triple, undeclared generated inputs, and artifact mismatch discovered late.

### Phase 3: Hardware Abstraction and Retained Vendor Boundary

**Rationale:** Product behavior depends on retained C/ASM/vendor code and hardware-specific contracts. Those boundaries must be explicit before application/domain code spreads `unsafe` assumptions.

**Delivers:** Retained-code inventory, `foreign/*` Bazel packages, private visibility, C ABI shims or bindgen allowlists where appropriate, safe adapter crates for startup/HAL/FreeRTOS/LwIP/mbedTLS/filesystems/TinyUSB/display/logging, board startup/linker/vector reviews, task/queue/mutex/event wrappers, and unsafe invariant documentation.

**Addresses:** STM32 startup, HAL/CMSIS, FreeRTOS task orchestration, retained vendor dependencies, hardware safety envelope, logging/diagnostics shell, and board/MCU-specific constraints.

**Avoids:** Foreign calls from everywhere, unowned C islands, broad bindgen APIs, raw RTOS handles in domain code, and hidden Marlin/runtime dependency decisions.

### Phase 4: Core Domain Parity

**Rationale:** Once build and hardware boundaries are stable, the value of Rust comes from typed domain decisions that can be tested cheaply on host and reused across simulator and hardware flows.

**Delivers:** Typed product/feature/artifact model, G-code command model, print/planner-facing state, thermal/probe/selftest policy, persistent config schema and migrations, MMU/puppy state, transfer state model, Connect command model, safety-state logic, host unit tests, reference corpora, and intentional deltas for known defect fixes.

**Addresses:** Marlin-derived behavior, Buddy bridge decisions, thermal/motion/selftest/recovery logic, persistent storage compatibility, MMU availability, probe analysis defect disposition, and typed invariants.

**Avoids:** C sentinel patterns copied into Rust, product `cfg` sprawl in domain logic, config migration breakage, probe threshold regressions, and behavior changes without fixtures.

### Phase 5: UI, Network, Transfers, and Generated Assets

**Rationale:** These are the most user-visible and integration-heavy surfaces, and they depend on the product model, adapters, resources, storage, and core state machines already established.

**Delivers:** GUI parity for both display classes, UI workflow and layout tests, Connect/PrusaLink/WUI protocol parity, TLS/custom CA fix and negative tests, transfer/download parity, proxy/current limitation tests, metrics/syslog behavior, deterministic translation/font/resource/WUI/ESP/puppy generation, resource package checks, and stress/performance measurements for stacks and buffers.

**Addresses:** Local UI, networking, TLS, transfers, localization, generated assets, WUI, Connect registration/telemetry/events/WebSocket behavior, storage/media races, and diagnostic support artifacts.

**Avoids:** Network/TLS regressions escaping host tests, generated asset drift, GUI freeze paths, transfer direct-sector races, stack overflows in progress/logging, and changed auth/API/error shapes.

### Phase 6: Release Qualification, Hardware Matrix, and Cutover

**Rationale:** Cutover should qualify completed behavior, not introduce first-time implementation. This phase proves the Rust+Bazel firmware is a release replacement.

**Delivers:** Full supported matrix builds, artifact metadata/section/resource/signing comparisons, simulator parity, hardware smoke/failure matrix, bootloader/update/install proof, storage migration proof from reference fixtures, security review for TLS/credentials/crash dumps, performance/stack/memory evidence, unresolved delta review, and final cutover decision.

**Addresses:** Behavior parity, release packaging, bootloader/resource install, hardware safety, persistent config compatibility, network/security, auxiliary firmware, and support diagnostics.

**Avoids:** Unqualified Big Bang cutover, final-phase implementation churn, direct-flash-only validation, missing bootloader proof, and hardware-only regressions found after release.

### Phase Ordering Rationale

- Reference evidence must precede rewrite work because the current firmware is the acceptance oracle and the known defects need explicit disposition.
- Bazel/toolchains/artifacts come before subsystem implementation because build authority and release outputs are project constraints, not optional infrastructure.
- Hardware and retained-code boundaries come before application/domain fan-out to prevent raw FFI, RTOS, HAL, and linker assumptions from leaking across the Rust codebase.
- Core domain parity comes before UI/network/transfers because those surfaces depend on printer state, storage, command, safety, and product-capability models.
- UI/network/transfers/resources are grouped because they share storage, generated assets, buffers, TLS/network constraints, telemetry, and user-visible flows.
- Release qualification is last and should only verify already-built capabilities against the matrix; unresolved implementation work should move backward to the owning phase.

### Research Flags

Phases likely needing deeper research during planning:

- **Phase 2:** Exact Rust target triples, STM32H503 FPU/ABI, linker/startup ownership, C/C++ toolchain registration, map/objcopy behavior, BBF/DFU/package rules, and signing/update contracts need implementation-specific validation.
- **Phase 3:** Retained-code boundaries need subsystem-by-subsystem research, especially Marlin reference-only versus temporary bridge, HAL/CMSIS wrappers, FreeRTOS task/stack ownership, mbedTLS buffer lifetimes, and C++ shim strategy.
- **Phase 4:** Marlin-derived behavior, probe-analysis threshold correction, persistent config hash/migration fixtures, MMU availability states, and safety policy corpora need focused domain research before coding.
- **Phase 5:** Connect/WUI/TLS/proxy/download protocol traces, custom CA security policy, generated asset ownership, GUI layout/golden strategy, and transfer media-race tests need deeper phase research.
- **Phase 6:** Hardware matrix design, failure-injection mechanics, bootloader/update install proof, and release signing procedures need hardware/release-specific validation.

Phases with standard patterns (skip research-phase unless unknowns surface):

- **Phase 1:** The reference-baseline, safety-envelope, and parity-ledger structure is well established by the research; execution should gather local artifacts rather than re-research the concept.
- **Phase 6:** The qualification checklist pattern is clear from the research; additional work should focus on concrete board availability and release mechanics, not generic cutover theory.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions and rule choices are grounded in official Bazel, rules_rust, Rust, and crate references. Exact STM32H5/M33 FPU/ABI and linker details remain medium-confidence until the Phase 2 spike. |
| Features | HIGH | Table stakes are derived from local project decisions and repository evidence. Cost and validation scope are medium-confidence until hardware and simulator plans are written. |
| Architecture | HIGH | Functional core / imperative shell, typed product profiles, adapter crates, private Bazel packages, and parity harnesses align with Bright Builds standards and embedded rewrite risk. Exact package shape can evolve during toolchain and boundary phases. |
| Pitfalls | HIGH | Pitfalls are backed by local concerns, current test gaps, official embedded/Bazel/toolchain docs, and known fragile firmware areas. |

**Overall confidence:** HIGH for roadmap sequencing and architectural direction; MEDIUM for exact board-level parameters and hardware/release qualification details until early spikes complete.

### Gaps to Address

- Exact Rust target triples and FPU ABI per MCU family: validate in Phase 2 with minimal linked firmware, ELF/map/vector table checks, and per-board platform definitions.
- STM32H503/xBuddy Extension toolchain strategy: confirm M33 target, FPU/no-FPU choice, linker script, panic path, and startup ownership before depending on it.
- Marlin retention contract: decide whether Marlin is reference-only or temporarily bridged through a phase-bounded C ABI, with tests and an exit plan.
- MK3.9/MK3.5/MK4 product mapping ambiguity: resolve before locking the product matrix.
- Generated-file ownership map: inventory translations, fonts, resources, logging docs, presets, struct visitors, option headers, resource hashes, and package metadata before moving generators.
- Package/signing/update details: define BBF/DFU descriptors, resource bootstrap, signing inputs, map/archive expectations, and bootloader install proof.
- Hardware availability and HIL scope: identify representative boards, safety failure cases, and which suites can run locally versus CI/lab.
- Persistent config fixtures: capture real/reference EEPROM/internal storage examples for migrations, deprecated IDs, credentials, and crash-dump policy.
- Network/TLS protocol corpus: collect Connect, PrusaLink/WUI, proxy, custom CA, invalid cert, timeout, duplicate command, long command, and transfer traces.
- Performance budgets: define task stack high-water targets, TLS handshake memory/latency budgets, buffer capacities, transfer stack constraints, and no-heap/alloc policy.

## Sources

### Primary (HIGH confidence)

- `.planning/PROJECT.md` - project decisions: Big Bang migration, behavior parity, Bazel primary now, `justfile`, Bright Builds standards, retained foreign-code constraints.
- `.planning/research/STACK.md` - recommended Rust+Bazel stack, versions, alternatives, target triples, and crate/tool recommendations.
- `.planning/research/FEATURES.md` - table-stakes parity scope, differentiators, anti-features, dependencies, MVP/cutover definition, and priority matrix.
- `.planning/research/ARCHITECTURE.md` - functional-core/imperative-shell architecture, package structure, adapter boundaries, retained code policy, parity harnesses, and roadmap implications.
- `.planning/research/PITFALLS.md` - critical pitfalls, prevention strategies, phase mapping, gotchas, security mistakes, performance traps, and recovery strategies.
- `.planning/codebase/CONCERNS.md` - known tech debt, bugs, security concerns, performance bottlenecks, fragile areas, missing features, and test gaps.
- `AGENTS.md`, `AGENTS.bright-builds.md`, and `standards-overrides.md` - repo-local instruction routing, Bright Builds pin, and absence of active local overrides.
- Bazel 9.1.0 release: https://github.com/bazelbuild/bazel/releases/tag/9.1.0 - current Bazel version recommendation.
- Bazel Bzlmod docs: https://bazel.build/docs/bzlmod - external dependency model.
- Bazel platforms docs: https://bazel.build/docs/platforms - product/platform modeling.
- Bazel hermeticity: https://bazel.build/basics/hermeticity - declared tools, inputs, and reproducible builds.
- Bazel toolchains: https://bazel.build/extending/toolchains - platform-aware toolchain resolution.
- Bazel C/C++ rules: https://bazel.build/reference/be/c-cpp - retained C/ASM integration.
- Bazel Central Registry, rules_rust 0.70.0: https://registry.bazel.build/modules/rules_rust - Rust rule version.
- rules_rust docs: https://bazelbuild.github.io/rules_rust/ - Rust rules and Bzlmod setup.
- rules_rust toolchains: https://bazelbuild.github.io/rules_rust/rust_toolchains.html - Rust toolchain and target configuration.
- rules_rust target triples/repositories: https://bazelbuild.github.io/rules_rust/rust_repositories.html - target triple/toolchain details.
- rules_rust bindgen docs: https://bazelbuild.github.io/rules_rust/rust_bindgen.html - curated FFI generation boundaries.
- Bazel Central Registry, rules_cc 0.2.19: https://registry.bazel.build/modules/rules_cc - retained C rule version.
- Bazel Central Registry, rules_python 2.0.2: https://registry.bazel.build/modules/rules_python - Python tooling/test support.
- Bazel Central Registry, rules_pkg 1.2.0: https://registry.bazel.build/modules/rules_pkg - package primitive support.
- Rust stable channel manifest: https://static.rust-lang.org/dist/channel-rust-stable.toml - Rust 1.96.0 stable reference.
- Rust platform support target list: https://doc.rust-lang.org/rustc/platform-support.html - Cortex-M target support.
- Rust Embedded Book, `no_std`: https://docs.rust-embedded.org/book/intro/no-std.html - embedded Rust runtime model.
- Rustonomicon FFI: https://doc.rust-lang.org/nomicon/ffi.html - FFI safety context.
- Rust Reference external blocks: https://doc.rust-lang.org/reference/items/external-blocks.html - Rust extern boundary rules.
- Rust Reference unsafe keyword: https://doc.rust-lang.org/reference/unsafe-keyword.html - safety obligation context.
- bindgen user guide: https://rust-lang.github.io/rust-bindgen/ - generated binding strategy.
- embedded-hal docs: https://docs.rs/embedded-hal/latest/embedded_hal/ - embedded traits.
- embedded-io docs: https://docs.rs/embedded-io/latest/embedded_io/ - byte I/O traits.
- cortex-m-rt docs: https://docs.rs/cortex-m-rt/latest/cortex_m_rt/ - optional startup/runtime context.
- heapless docs: https://docs.rs/heapless/latest/heapless/ - fixed-capacity collections.
- probe-rs docs: https://probe.rs/ - probe/debug tooling.
- Mbed TLS X.509 API docs: https://mbed-tls.readthedocs.io/projects/api/en/v2.28.9/api/file/x509\_\_crt_8h/ - DER parsing and buffer lifetime risk.
- FreeRTOS stack overflow checking: https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/09-Memory-management/02-Stack-usage-and-stack-overflow-checking - stack instrumentation context.
- FreeRTOS `uxTaskGetStackHighWaterMark`: https://www.freertos.org/Documentation/02-Kernel/04-API-references/03-Task-utilities/04-uxTaskGetStackHighWaterMark - stack high-water measurement.
- just 1.51.0 release: https://github.com/casey/just/releases/tag/1.51.0 - workflow wrapper version.
- Bright Builds standards index: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/index.md - standards routing and rule levels.
- Bright Builds architecture standard: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md - functional core, parse at boundaries, illegal states.
- Bright Builds verification standard: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/verification.md - repo-native verification expectations.
- Bright Builds testing standard: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md - unit test expectations.
- Bright Builds Rust standard: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md - Rust module layout, `let...else`, `maybe_`, newtypes, adapters, and verification notes.

### Secondary (MEDIUM confidence)

- Local build and option evidence: `ProjectOptions.cmake`, `CMakePresets.json`, `CMakeLists.txt`, `utils/build.py`, `utils/presets/presets.json` - product matrix and artifact surface.
- Local runtime and feature evidence: `src/buddy`, `src/common`, `src/common/feature`, `src/feature`, `src/gui`, `src/connect`, `src/transfers`, `src/persistent_stores`, `src/resources`, `src/mmu2`, `src/puppies`, `src/puppy`, `lib/Marlin`, `lib/WUI` - current subsystem responsibilities.
- Local verification evidence: `tests/unit`, `tests/integration`, `tests/blockdevice`, `.pre-commit-config.yaml`, `utils/holly/build-pr.jenkins`, `README.md`, `tests/unit/README.md`, `tests/integration/README.md` - current verification surfaces and gaps.

### Tertiary (LOW confidence)

- None. Open questions are captured as planning gaps rather than low-confidence claims.

______________________________________________________________________

*Research completed: 2026-06-02*
*Ready for roadmap: yes*
