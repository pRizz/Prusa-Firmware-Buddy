# Roadmap: Prusa Firmware Buddy Rust Port

## Overview

This roadmap turns the C/C++/CMake firmware into a behavior-parity Rust+Bazel replacement by first freezing the reference baseline, then making Bazel authoritative, then rebuilding the firmware around typed Rust domain models, explicit retained-code boundaries, subsystem parity gates, and final cutover evidence. The shape follows the project decisions in `.planning/PROJECT.md`, the 30 v1 requirements in `.planning/REQUIREMENTS.md`, the research findings in `.planning/research/`, and the current codebase architecture and concerns in `.planning/codebase/`.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Reference Baseline and Safety Envelope** - Freeze the behavior oracle, supported matrix, safety envelope, and known-defect ledger before Rust implementation work can drift. (completed 2026-06-02)
- [x] **Phase 2: Bazel Authority and Developer Facade** - Make Bazel and `just` the normal developer entrypoint for builds, tests, generators, and release workflows from the start. (completed 2026-06-02)
- [x] **Phase 3: Artifact and Generator Parity** - Move release artifacts and deterministic generators into Bazel with drift and reference comparison gates. (completed 2026-06-03)
- [x] **Phase 4: Rust Architecture and Invariant Model** - Establish the Rust workspace, typed product/domain model, Bright Builds checks, and pure-logic test foundation. (completed 2026-06-03)
- [x] **Phase 5: Foreign Code, Unsafe, and Runtime Boundary** - Inventory retained C/C++/ASM/vendor code and wrap startup, HAL, RTOS, and unsafe boundaries behind safe Rust adapters. (completed 2026-06-03)
- [x] **Phase 6: Printing Core, Safety, and Feature Gates** - Preserve print behavior, safety-critical flows, and printer-specific feature combinations through typed Rust models and parity fixtures. (completed 2026-06-04)
- [ ] **Phase 7: Persistence, Storage, and Resource Compatibility** - Preserve config stores, migrations, filesystems, credentials, generated resources, translations, and bundled runtime assets.
- [ ] **Phase 8: Local Interface and Workflow Parity** - Preserve local GUI workflows, display-class behavior, dialogs, warnings, setup flows, and print controls.
- [ ] **Phase 9: Network, Web Services, and Transfers** - Preserve Connect, PrusaLink/WUI, TLS, telemetry, transfer, and local service behavior.
- [ ] **Phase 10: Auxiliary Controllers and Expansion Ecosystem** - Preserve puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, toolchanger, and auxiliary update flows.
- [ ] **Phase 11: Parity Pyramid and Cutover Evidence** - Prove the Rust+Bazel firmware satisfies all parity gates before demoting the CMake/C++ reference path.

## Phase Details

### Phase 1: Reference Baseline and Safety Envelope

**Goal**: Maintainers can define what behavior parity and safe hardware behavior mean before the Rust rewrite changes implementation details.
**Depends on**: Nothing (first phase)
**Requirements**: BASE-01, BASE-02, BASE-03, BASE-04
**Success Criteria** (what must be TRUE):

1. Maintainer can inspect the supported printer, board, MCU, bootloader, feature, and artifact matrix derived from the current firmware reference.
1. Maintainer can run reference-capture targets for builds, generated assets, protocol traces, simulator flows, storage migrations, and release artifacts.
1. Maintainer can review a concern ledger that classifies each known defect or fragile area as preserved temporarily, fixed during rewrite, or deferred.
1. Maintainer can review a board-aware safety envelope for startup, watchdogs, thermal states, motion safe states, probes, power panic, crash dumps, and emergency flows.
   **Plans**: `.planning/phases/01-reference-baseline-and-safety-envelope/01-01-PLAN.md`

### Phase 2: Bazel Authority and Developer Facade

**Goal**: Developers can use Bazel as the authoritative build/test graph and `just` as the discoverable workflow facade.
**Depends on**: Phase 1
**Requirements**: BAZL-01, BAZL-02, BAZL-04
**Success Criteria** (what must be TRUE):

1. Developer can build through `MODULE.bazel`, `.bazelrc`, registered Rust/C/C++/ASM toolchains, and explicit product platforms.
1. Developer can build Rust firmware, retained foreign code, generated assets, host tools, unit tests, simulator inputs, and release packages from Bazel without CMake being the source of truth.
1. Developer can run checked `just` commands for bootstrap, build, test, format, lint, generated-file checks, simulator/parity checks, and release packaging.
1. Developer can distinguish host tools/tests from embedded firmware targets through explicit Bazel platforms and target labels.
   **Plans**: `.planning/phases/02-bazel-authority-and-developer-facade/02-01-PLAN.md`

### Phase 3: Artifact and Generator Parity

**Goal**: Developers can produce deterministic generated outputs and reference-compatible firmware artifacts through Bazel.
**Depends on**: Phase 2
**Requirements**: BAZL-03, BAZL-05
**Success Criteria** (what must be TRUE):

1. Developer can produce `.bin`, `.bbf`, `.dfu`, map/provenance outputs, resource images, boot/noboot variants, and auxiliary firmware packages from Bazel.
1. Developer can run Bazel-owned generators for product profiles, option data, resources, translations, fonts, web assets, ESP blobs, puppy/MMU descriptors, and package metadata.
1. Developer can run deterministic drift checks that fail when tracked generated outputs no longer match their declared sources.
1. Maintainer can compare generated outputs and release artifact metadata against the C/C++ reference surface.
   **Plans**: 3 plans

Plans:
- [x] 03-01-PLAN.md — Create Phase 3 verifier, artifact packager, artifact manifest, and generated-drift helper layer.
- [x] 03-02-PLAN.md — Wire Bazel-produced representative release artifact outputs.
- [x] 03-03-PLAN.md — Wire full generator coverage, update targets, facade recipes, and guarded reference comparison.

### Phase 4: Rust Architecture and Invariant Model

**Goal**: Developers can build and verify a Rust workspace that encodes firmware invariants instead of copying sentinel-heavy C/C++ patterns.
**Depends on**: Phase 3
**Requirements**: RUST-01, RUST-02, RUST-05, VERF-02
**Success Criteria** (what must be TRUE):

1. Developer can inspect Rust crates that separate pure domain logic from board, runtime, application, and adapter code according to Bright Builds functional-core/imperative-shell guidance.
1. Developer can construct printer, board, MCU, bootloader, feature, storage schema, artifact, and protocol values through Rust types that reject invalid combinations early.
1. Developer can run Rust formatting, lint, unit-test, doc, and build checks through Bazel/just with Bright Builds Rust expectations enforced where practical.
1. Developer can run focused Arrange/Act/Assert tests for pure state machines, parsers, policies, migrations, and protocol decisions.
   **Plans**: `.planning/phases/04-rust-architecture-and-invariant-model/04-01-PLAN.md`

Plans:
- [x] 04-01-PLAN.md — Create Rust workspace, invariant domain model, boundary crates, and Bazel/just Rust verification.

### Phase 5: Foreign Code, Unsafe, and Runtime Boundary

**Goal**: Rust firmware can boot and orchestrate supported runtime shells through explicit retained-code and unsafe boundaries.
**Depends on**: Phase 4
**Requirements**: RUST-03, RUST-04, CORE-01, CORE-02
**Success Criteria** (what must be TRUE):

1. Developer can inspect a foreign-code inventory for every retained C, C++, ASM, generated, and vendor component with reason, source/version, ownership boundary, safe facade, and replacement posture.
1. Developer can audit every `unsafe`, FFI, MMIO, DMA, interrupt, linker-symbol, static-memory, allocator, and panic-boundary surface inside narrow adapter crates with documented invariants and tests.
1. Rust firmware preserves STM32 startup, memory layout, vector/interrupt behavior, board clocks, HAL/CMSIS integration, watchdog behavior, and linker-controlled sections for supported MCU families.
1. Rust firmware preserves FreeRTOS task orchestration, task dependency readiness, static task memory assumptions, synchronization behavior, queues, timers, and startup ordering for master and auxiliary firmware.
   **Plans**: 5 plans

Plans:
- [x] 05-01-PLAN.md — Create exhaustive retained-code inventory, unsafe-boundary audit, and Phase 5 verifier schema gates.
- [x] 05-02-PLAN.md — Add board adapter contracts for MCU, board-clock, memory, DMA, MMIO, interrupt, and FFI boundaries.
- [x] 05-03-PLAN.md — Add runtime startup, linker, allocator, panic, watchdog, and crash-dump boundary contracts.
- [x] 05-04-PLAN.md — Add FreeRTOS task, queue, timer, mutex, semaphore, event-group, and wait-condition contracts.
- [x] 05-05-PLAN.md — Wire Phase 5 Bazel/just labels and harden aggregate verification.

### Phase 6: Printing Core, Safety, and Feature Gates

**Goal**: Users get the same printing, safety, recovery, and printer-specific hardware behavior from the Rust firmware as from the reference firmware.
**Depends on**: Phase 5
**Requirements**: CORE-03, CORE-04, CORE-05
**Success Criteria** (what must be TRUE):

1. User can run G-code, serial printing, file printing, pause/resume/cancel, Buddy-specific G/M-code, and planner-visible flows with behavior matching reference fixtures.
1. User can observe the same thermal, motion, selftest, calibration, crash detection, power panic, emergency stop, safe-output, redscreen/BSOD/assert, and recovery behavior.
1. Maintainer can inspect typed feature gates for filament sensors, TMC paths, precise homing, input shaper, phase/burst stepping, loadcell, beds, chamber, door, MMU2, NFC, LEDs, toolchanger, and xBuddy Extension behavior.
1. Maintainer can see known concern dispositions reflected in fixtures or intentional deltas for the affected printing, probe, safety, and feature-gate paths.
   **Plans**: 5 plans

Plans:
- [x] 06-01-PLAN.md — Create Phase 6 verifier, manifests, concern dispositions, and Bazel/just validation entrypoints.
- [x] 06-02-PLAN.md — Add typed Rust printing-core state and command-routing contracts.
- [x] 06-03-PLAN.md — Add typed Rust safety, recovery, and fatal-boundary policy contracts.
- [x] 06-04-PLAN.md — Add ProductProfile-keyed Phase 6 feature-gate contracts.
- [x] 06-05-PLAN.md — Harden aggregate Phase 6 verification and complete Nyquist validation sign-off.

### Phase 7: Persistence, Storage, and Resource Compatibility

**Goal**: Existing printer state, storage formats, generated resources, and bundled runtime assets remain compatible under the Rust firmware.
**Depends on**: Phase 6
**Requirements**: IFCE-04, IFCE-05
**Success Criteria** (what must be TRUE):

1. User can upgrade from reference firmware storage fixtures without losing persistent configuration, defaults, deprecated item IDs, credentials, selftest state, or settings import/export behavior.
1. Rust firmware preserves EEPROM/internal flash behavior, FatFs/littlefs mounts, USB/internal/semihosting paths, config hash behavior, and journal migration behavior.
1. Runtime and release artifacts contain the expected translations, fonts, icons, littlefs images, bootloader resources, ESP blobs, language packs, resource hashes, and generated headers.
1. Developer can run storage migration, resource package, and generated-output parity checks through Bazel/just.
   **Plans**: TBD

### Phase 8: Local Interface and Workflow Parity

**Goal**: Users can operate supported printers through the local GUI with parity across supported display classes.
**Depends on**: Phase 7
**Requirements**: IFCE-01
**Success Criteria** (what must be TRUE):

1. User can navigate the same screen stacks, dialogs, menus, wizards, warnings, and redscreens on supported 240x320 and 480x320 display classes.
1. User can control prints, setup flows, selftest, calibration, Connect registration, and localization workflows through the local GUI.
1. User can see localized text, layout behavior, warnings, print previews, progress, and error surfaces that match reference fixtures within approved intentional deltas.
1. Maintainer can run GUI workflow and layout parity checks that include known freeze/error paths from the concerns ledger.
   **Plans**: TBD
   **UI hint**: yes

### Phase 9: Network, Web Services, and Transfers

**Goal**: Users and integrations can use Prusa Connect, PrusaLink/WUI, transfers, TLS, telemetry, and local services with parity.
**Depends on**: Phase 7, Phase 8
**Requirements**: IFCE-02, IFCE-03
**Success Criteria** (what must be TRUE):

1. User can register with Prusa Connect and preserve token, fingerprint, telemetry, event, WebSocket command, TLS verification, proxy-limit, and download behavior.
1. User can use PrusaLink/WUI HTTP API v1, OctoPrint-compatible endpoints, digest/API-key auth, static assets, SNTP, mDNS, metrics, and syslog behavior.
1. User can start, monitor, recover, and fail transfers/downloads with the same single-slot, storage, range, timeout, and error semantics as the reference firmware.
1. Maintainer can run negative protocol and TLS fixtures for custom certificates, invalid certificates, weak signatures, duplicate commands, large commands, proxy behavior, and stalled networks.
   **Plans**: TBD
   **UI hint**: yes

### Phase 10: Auxiliary Controllers and Expansion Ecosystem

**Goal**: Supported auxiliary controllers, expansion boards, MMU, and toolchanger flows behave as first-class Rust+Bazel firmware products.
**Depends on**: Phase 6, Phase 7
**Requirements**: IFCE-06
**Success Criteria** (what must be TRUE):

1. User can run affected printer combinations with puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, Modbus/RS485, toolchanger, dock/tool offset, and auxiliary update behavior preserved.
1. Maintainer can build and package auxiliary firmware, startup flashing resources, skip-flash/prebuilt modes, and crash-dump/update flows through Bazel.
1. Maintainer can inspect typed auxiliary-controller states for bootloader, unavailable, active, stopped, update, and fault paths instead of unconditional availability stubs.
1. Maintainer can run protocol, bootload, update, and hardware-aware smoke checks for auxiliary-controller behavior required by supported printers.
   **Plans**: TBD

### Phase 11: Parity Pyramid and Cutover Evidence

**Goal**: Maintainers can approve Rust+Bazel cutover from evidence that every v1 requirement is covered by passing parity gates or documented retained-code justification.
**Depends on**: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7, Phase 8, Phase 9, Phase 10
**Requirements**: VERF-01, VERF-03, VERF-04, VERF-05
**Success Criteria** (what must be TRUE):

1. Developer can run a parity test pyramid covering pure Rust unit tests, adapter contracts, generated drift checks, reference fixture comparisons, simulator flows, network/TLS/API tests, release artifact checks, and hardware smoke gates.
1. Developer can compare Rust outputs against the reference firmware for product artifacts, generated resources, storage migrations, protocol traces, G-code behavior fixtures, display-state fixtures, and release metadata.
1. Maintainer can review cutover evidence showing every v1 requirement mapped to passing tests, simulator or hardware evidence, intentional deltas, and residual retained-code justifications.
1. Maintainer can remove or demote the CMake/C++ reference path only after Rust+Bazel satisfies all parity gates and documented cutover criteria.
   **Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Reference Baseline and Safety Envelope | 1/1 | Complete    | 2026-06-02 |
| 2. Bazel Authority and Developer Facade | 1/1 | Complete    | 2026-06-02 |
| 3. Artifact and Generator Parity | 3/3 | Complete    | 2026-06-03 |
| 4. Rust Architecture and Invariant Model | 1/1 | Complete    | 2026-06-03 |
| 5. Foreign Code, Unsafe, and Runtime Boundary | 5/5 | Complete    | 2026-06-03 |
| 6. Printing Core, Safety, and Feature Gates | 5/5 | Complete    | 2026-06-04 |
| 7. Persistence, Storage, and Resource Compatibility | 4/5 | In Progress | - |
| 8. Local Interface and Workflow Parity | 0/TBD | Not started | - |
| 9. Network, Web Services, and Transfers | 0/TBD | Not started | - |
| 10. Auxiliary Controllers and Expansion Ecosystem | 0/TBD | Not started | - |
| 11. Parity Pyramid and Cutover Evidence | 0/TBD | Not started | - |
