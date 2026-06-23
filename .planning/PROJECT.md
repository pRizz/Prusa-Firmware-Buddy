# Prusa Firmware Buddy Rust Port

## What This Is

This project is a full Rust rewrite of the Prusa-Firmware-Buddy firmware while preserving the behavior of the current supported printer firmware. The existing C/C++/CMake codebase remains the reference implementation, but the target end state is a Rust firmware with Bazel as the authoritative build system and a `justfile` for common developer workflows.

The work is intentionally standards-driven: Bright Builds Rules guide architecture, code shape, verification, testing, and Rust module structure. Known defects and fragile areas identified in the codebase map should be fixed during the rewrite instead of being mechanically carried forward.

## Core Value

Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.

## Current State

Milestone v1.0 Rust Port Evidence Foundation shipped on 2026-06-15. The project now has a clean source-backed evidence foundation for the Rust+Bazel rewrite: all 30 v1 requirements are complete, all 12 v1 phases are complete, the follow-up milestone audit passed, and the archive lives under `.planning/milestones/`.

Milestone v1.1 Cutover Evidence Hardening shipped on 2026-06-22. It turned the remaining non-local cutover blockers into durable gate capabilities: CI aggregate evidence, simulator evidence, hardware/safety/media evidence, live network/TLS/WUI/transfer/proxy evidence, release-candidate signing/provenance/comparison evidence, retained-code acceptance, upstream-result consumption, validation metadata reconciliation, and a passed audit rerun.

The replacement firmware is not yet cut over. Final reference demotion remains intentionally blocked until the validated external simulator, hardware, live-service, release, signing, upstream-result, retained-code, residual-risk, and maintainer-decision inputs are supplied and accepted under the v1.1 contracts.

Phase 23 of v1.2 is complete. Maintainers can now submit Phase 14-compatible simulator evidence packets for startup, G-code, GUI, storage, transfer, and selected failure flows, with v1.2 status normalization, secret/overclaim guards, retained redacted outputs, upstream result rows, Bazel labels, and `just phase23-verify`.

## Current Milestone: v1.2 Cutover Evidence Execution and Acceptance

**Goal:** Execute the real external cutover evidence gates created in v1.1 and produce a maintainer-reviewable final readiness packet.

**Target features:**

- Collect and retain full external evidence packets for simulator, hardware/media/safety, live services, release/signing, and upstream results.
- Drive retained-code, residual-risk, exception, and maintainer acceptance decisions through machine-readable inputs.
- Produce a final cutover readiness report that is decision-ready while keeping reference demotion blocked unless maintainers explicitly approve.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Build firmware for the currently supported Prusa printers using existing board, printer, bootloader, and feature option matrices — existing CMake/Python workflow in `CMakeLists.txt`, `ProjectOptions.cmake`, `CMakePresets.json`, and `utils/build.py`
- ✓ Support STM32-based embedded firmware targets with board-specific startup, HAL/CMSIS integration, linker scripts, and RTOS task orchestration — existing code in `src/device`, `src/buddy/main.cpp`, `lib/Drivers`, and `lib/Middlewares/Third_Party/FreeRTOS`
- ✓ Preserve the Marlin-derived printing core behavior, G-code handling, motion/planner flows, thermal behavior, and Buddy-specific server/client bridge — existing code in `lib/Marlin`, `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, and `src/marlin_stubs`
- ✓ Provide GUI-driven printer workflows for supported display resolutions, dialogs, menus, setup flows, errors, and print controls — existing code in `src/gui` and `src/guiapi`
- ✓ Provide local networking, Prusa Connect, PrusaLink/WUI, transfer, TLS, telemetry, registration, and command-channel behavior — existing code in `src/connect`, `src/transfers`, `src/common/http`, and `lib/WUI`
- ✓ Preserve persistent configuration, feature flags, language/resource generation, bootloader packaging, firmware artifacts, and host/simulator testing workflows — existing code in `src/persistent_stores`, `src/lang`, `src/gui/res`, `utils/`, and `tests/`
- ✓ Inspect retained foreign-code and unsafe/runtime boundaries through Phase 5 inventory, audit, adapter contracts, Bazel/just labels, and `tools/bazel/phase5_verify.py`
- ✓ Model STM32 startup/linker/clock/HAL surfaces and FreeRTOS task/synchronization/runtime contracts as typed Rust boundary data, with hardware-only behavior classified as non-local evidence for later parity gates
- ✓ Model printing-core routing, safety/recovery/fatal policies, and printer-specific feature gates as typed Rust domain contracts backed by Phase 6 manifests, verifier regression tests, Bazel/just labels, and explicit non-local evidence classification for physical behavior
- ✓ Preserve persistent configuration, storage/media surfaces, generated resources, bundled runtime assets, and Phase 7 concern dispositions through source-backed manifests, redacted fixture catalogs, typed Rust storage/resource contracts, Bazel/just verifier labels, and explicit non-local evidence boundaries
- ✓ Preserve local GUI workflow, display-class, warning/error, print-control, setup, Connect-entry, PrusaLink credential-display, localization, and concern-disposition contracts through Phase 8 source-backed manifests, typed Rust GUI contracts, Bazel/just verifier labels, and explicit non-local evidence boundaries
- ✓ Preserve Prusa Connect, PrusaLink/WUI, network-service, transfer, TLS/secret, proxy, telemetry, command-channel, and concern-disposition contracts through Phase 9 source-backed manifests, typed Rust network contracts, negative network fixtures, Bazel/just verifier labels, and explicit non-local evidence boundaries
- ✓ Preserve puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, Modbus/RS485, toolchanger, dock/tool offset, startup flashing, skip-flash/prebuilt firmware, and auxiliary-controller update contracts through Phase 10 source-backed manifests, typed Rust auxiliary contracts, Bazel/just verifier labels, clean review closure, and explicit non-local hardware/simulator/cutover evidence boundaries
- ✓ Review v1.0 cutover readiness through Phase 11 parity pyramid, all-requirement evidence, reference comparisons, retained-code justifications, Bazel/just aggregate verification, and explicit final-demotion blockers
- ✓ Archive v1.0 from clean planning metadata through Phase 12 requirement, roadmap, validation, manifest wording, and follow-up audit hygiene
- ✓ Complete all v1.0 requirements, phase summaries, verification reports, and milestone audit evidence — v1.0 Rust Port Evidence Foundation
- ✓ Run the aggregate cutover verifier in CI and persist machine-readable redacted evidence through Phase 13 workflow, contract, manifest, artifact retention, Bazel labels, and `just phase13-verify`
- ✓ Maintainers can review simulator evidence for startup, G-code, GUI, storage, transfer, and failure flows through the Phase 14 simulator evidence contract, dry-run artifacts, explicit real-run prerequisites, Bazel labels, and `just phase14-verify`
- ✓ Release managers can produce and verify signed release-candidate artifacts, resources, maps, provenance, and auxiliary packages through Phase 20 release identity, release input template, result manifest, verifier, Bazel labels, and `just phase20-verify`
- ✓ Maintainers can review hardware, safety, storage-media, UI-input, MMU, RS485, and toolchanger evidence through the Phase 15 contract, operator input schema, sanitized artifact policy, Phase 19 aggregate retention, Bazel labels, and `just phase15-verify`
- ✓ Maintainers can review live Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump upload evidence through the Phase 16 contract, secret guards, Phase 19 aggregate retention, Bazel labels, and `just phase16-verify`
- ✓ Maintainers can evaluate retained-code acceptance and final reference-demotion decisions through Phase 18 review packets, Phase 21 upstream-result consumption, explicit maintainer decision inputs, and a blocked-by-default `demotion_allowed` gate
- ✓ Reconcile v1.1 requirement traceability, validation metadata, roadmap state, and milestone audit readiness through Phase 22 verification and the passed 2026-06-22 audit rerun
- ✓ Maintainers can supply and retain real simulator evidence results for startup, G-code, GUI, storage, transfer, and selected failure flows through the Phase 23 evidence packet schema, retained redacted outputs, v1.2 status vocabulary, secret/overclaim guards, upstream result row, Bazel labels, and `just phase23-verify`

### Active

<!-- Current scope. Building toward these. -->

- [ ] Execute and retain real hardware/media/safety, live-service, release/signing, and upstream-result evidence packets through the v1.1 gate contracts.
- [ ] Drive retained-code, residual-risk, exception, and maintainer acceptance decisions with machine-readable inputs.
- [ ] Produce a final cutover readiness report that remains blocked by default unless explicit maintainer approval allows reference demotion.

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Incremental dual-ownership migration as the primary strategy — user chose a Big Bang rewrite posture rather than subsystem-by-subsystem production cutover.
- Dropping existing supported printers to reduce migration work — behavior parity is a project constraint.
- Treating Bazel as a secondary experiment while CMake remains authoritative — user chose Bazel Primary Now.
- Adding new printer features unrelated to parity or defect remediation — new feature work would obscure whether the Rust firmware matches the existing baseline.
- Rewriting vendor or upstream third-party components before their replacement boundary is understood — firmware behavior takes priority over churn; any retained C/ASM/vendor code must be made explicit in requirements and roadmap phases.

## Context

The existing repository is a large embedded firmware codebase for Original Prusa printers. The current stack is C++23, C, ASM, CMake, Python tooling, STM32 HAL/CMSIS, FreeRTOS, Marlin, LwIP, mbedTLS, FatFs/littlefs, TinyUSB, Catch2, pytest, and a custom bootstrap flow. The codebase map in `.planning/codebase/` is the reference for current architecture, testing practices, integrations, and known concerns.

Phase 1 established the reference baseline package for the rewrite: supported matrix, reference-capture catalog, intentional-delta concern ledger, safety envelope, phase-local verifier, and verification report under `.planning/phases/01-reference-baseline-and-safety-envelope/`. Phase 2 established the root Bazel module, product platform labels, registered firmware toolchain labels, Bazel workflow targets, checked `justfile`, and Phase 2 verifier under `.planning/phases/02-bazel-authority-and-developer-facade/`. Phase 3 established artifact and generator parity scaffolding. Phase 4 established the Rust workspace and invariant model. Phase 5 established explicit retained-code, unsafe, board-runtime, and FreeRTOS boundary contracts plus aggregate verification. Phase 6 established typed printing-core, safety/recovery/fatal, and ProductProfile-keyed feature-gate contracts with manifest-backed verification. Phase 7 established source-backed persistence, storage media, generated resource, concern disposition, redacted migration fixture, Rust storage/resource domain, and Bazel/just verification contracts with manual hardware/media/release proof explicitly deferred. Phase 8 established source-backed local GUI workflow, display-layout, warning/error, print-control, setup, Connect-entry, PrusaLink credential-display, localization, and concern-disposition contracts with typed Rust GUI domain invariants, verifier regression tests, Bazel/just labels, clean review closure, and physical/simulator/touch/network/auxiliary/cutover proof explicitly deferred. Phase 9 established source-backed Connect, WUI/PrusaLink, network-service, transfer, TLS/secret, proxy, telemetry, command-channel, negative-fixture, and concern-disposition contracts with typed Rust network domain invariants, verifier regression tests, Bazel/just labels, clean review closure, and live cloud/simulator/physical network/TLS/media/cutover proof explicitly deferred. Phase 10 established source-backed auxiliary-controller, MMU, Modbus/RS485, toolchanger, build/update, and concern-disposition contracts with typed Rust auxiliary invariants, verifier regression tests, Bazel/just labels, clean review closure, and physical/simulator/live-transport/cutover proof explicitly deferred. Phase 11 established the parity pyramid, all-requirement evidence, reference comparison rows, cutover readiness, retained-code justifications, aggregate verifier, and final reference-demotion blockers. Phase 12 closed the v1.0 milestone metadata drift, and v1.0 is now archived as the Rust port evidence foundation.

v1.1 used the archived v1.0 source-backed evidence baseline without redefining parity contracts. Phase 13 added CI evidence orchestration, Phase 14 added simulator evidence gates, Phase 15 added hardware evidence gates, Phase 16 added live-network evidence gates, Phase 17 added release-candidate evidence gates, Phase 18 added retained-code acceptance review, Phase 19 added aggregate cutover evidence CI, Phase 20 added release artifact production identity and verification, Phase 21 forced final readiness to consume machine-readable upstream result rows, and Phase 22 reconciled requirement, validation, roadmap, and audit metadata before the passed milestone audit rerun. Phase 23 started v1.2 execution with the simulator evidence execution contract, real evidence input validator, retained output writer, upstream result row, regression tests, Bazel/root/just wiring, and a clean post-fix review while keeping hardware-only behaviors outside simulator proof.

The current architecture is a CMake-composed firmware target with board/printer feature gates, a FreeRTOS imperative shell, Marlin as the printing core, and application layers for GUI, Connect, WUI, transfers, persistent stores, puppies/MMU, resources, and packaging. The Rust rewrite should deliberately separate pure firmware/domain decisions from hardware, RTOS, filesystem, networking, UI, and packaging adapters where practical.

The project should use Rust to make illegal states unrepresentable, parse raw boundary data into domain types, and keep optional internal names explicit with `maybe_` naming. New Rust modules should prefer `foo.rs` plus `foo/` over `foo/mod.rs`, use `let...else` for guard-style extraction where clearer, and include unit tests for pure/business logic with Arrange, Act, Assert structure.

Known concerns to prioritize during planning include global build target coupling, generated asset drift, unsafe or incomplete shell scripts, disabled/outdated Connect tests, custom TLS certificate parsing risk, probe-analysis classification coupling, GUI freeze paths, transfer stack constraints, and large mixed-responsibility files. These should become roadmap work, not merely documentation notes.

## Constraints

- **Migration posture**: Big Bang — the roadmap should lead to a full replacement cutover instead of relying on incremental production migration as the primary strategy.
- **Compatibility**: Behavior Parity — current supported printers, release artifacts, generated assets, tests, network behavior, persistent config, and safety-critical firmware behavior must remain compatible unless explicitly descoped.
- **Build system**: Bazel Primary Now — Bazel becomes the authoritative build from the start of the planned work; CMake may remain only as a reference, comparison, or compatibility path where necessary.
- **Developer workflow**: `justfile` required — common commands should have discoverable, stable wrappers that call Bazel/Rust tooling and any remaining compatibility checks.
- **Standards**: Bright Builds Rules — architecture, code shape, Rust guidance, verification, and testing standards apply unless a narrow local override is documented in `standards-overrides.md`.
- **Safety**: Embedded firmware behavior must be validated with tests, hardware-aware review, simulator flows, or explicit evidence before replacement is considered complete.
- **Third-party code**: Vendor, HAL, generated, and upstream imported code may require staged boundary decisions before full Rust replacement; retained foreign code must be named and justified.

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Port the firmware to Rust | Improve safety, testability, domain modeling, and long-term maintainability. | — Pending |
| Use a Big Bang replacement posture | User explicitly chose a full replacement strategy instead of incremental production migration. | — Pending |
| Preserve behavior parity | Existing supported printers and workflows are the acceptance baseline. | — Pending |
| Make Bazel primary immediately | User explicitly chose Bazel as the authoritative build system from the start. | Phase 2 added the root Bazel module, configs, platforms, toolchain labels, and workflow targets. |
| Add a `justfile` | Common workflows need stable, discoverable convenience commands on top of Bazel/Rust tooling. | Phase 2 added the root checked `justfile` facade. |
| Apply Bright Builds Rules | The migration should use explicit standards for architecture, verification, testing, code shape, and Rust style. | — Pending |
| Retain foreign code only behind explicit boundaries | Phase 5 verified that retained C/C++/ASM/vendor/runtime surfaces need named ownership, invariants, and non-local evidence classification before subsystem parity work depends on them. | Phase 5 added inventory/audit manifests, board/runtime adapter contracts, review-clean fixes, and aggregate verification. |
| Treat physical printing and safety proof as non-local evidence until later parity gates | Phase 6 can define typed contracts and fixture/manifests, but real thermal, motion, watchdog, crash recovery, emergency stop, safe-output, MMU/toolchanger, and auxiliary-controller behavior needs simulator or hardware evidence. | Phase 6 verifier passed with these physical behaviors explicitly deferred to Phase 10 or Phase 11 instead of overclaiming local proof. |
| Treat persistent storage and resource compatibility proof as source-backed local contracts until hardware/release gates | Phase 7 can verify manifests, redacted fixture identities, Rust domain types, Bazel labels, and generated-resource wiring locally, but actual USB media, flash wear, simulator flow, hardware media proof, full generator execution, and byte-for-byte release parity need later evidence. | Phase 7 verifier passed with `just phase7-verify`, Bazel verifier labels, Rust checks, and explicit deferred non-local evidence boundaries. |
| Treat local GUI parity proof as source-backed contracts until simulator, physical display, and cutover gates | Phase 8 can verify GUI workflow/layout/concern manifests, Rust GUI domain invariants, verifier tests, and Bazel/just wiring locally, but physical LCD, touch/encoder timing, long-run UI behavior, simulator display flows, network-backed behavior, auxiliary behavior, and final UI state fixtures need later evidence. | Phase 8 verifier passed with `just phase8-verify`, Bazel verifier labels, Rust checks, clean review closure, and explicit deferred non-local evidence boundaries. |
| Treat network, web-service, and transfer parity proof as source-backed local contracts until live, simulator, hardware, and cutover gates | Phase 9 can verify manifests, typed Rust domain invariants, negative fixtures, verifier tests, Bazel/just wiring, and secret-redaction boundaries locally, but live Connect, WebSocket, real TLS, physical/simulator network, USB/media race, long-transfer, crash-dump upload, and final cutover behavior need later evidence. | Phase 9 verifier passed with `just phase9-verify`, Rust checks, clean review closure, and explicit deferred non-local evidence boundaries. |
| Treat auxiliary-controller parity proof as source-backed local contracts until hardware, simulator, live transport, and cutover gates | Phase 10 can verify source-backed manifests, typed Rust auxiliary/MMU/domain invariants, verifier tests, Bazel/just wiring, and sensitive-payload boundaries locally, but physical RS485, toolchanger, live MMU, long-running update, and final cutover behavior need later evidence. | Phase 10 verifier passed with `just phase10-verify`, Rust checks, clean review closure, and explicit deferred non-local evidence boundaries. |
| Treat cutover evidence as source-backed local proof until non-local gates are accepted | Phase 11 can aggregate requirement evidence, reference comparisons, retained-code justifications, Rust contracts, Bazel/just wiring, and security scans locally, but simulator, hardware, live network/TLS, release-candidate, signing, storage-media, MMU, RS485, toolchanger, retained-code acceptance, maintainer approval, and reference demotion remain non-local gates. | Phase 11 verifier passed while keeping `criteria-reference-demotion-blocked` not cutover ready. |
| Treat v1.0 milestone hygiene as metadata-only cleanup | Phase 12 should reconcile stale planning/evidence records without changing firmware behavior or converting non-local gates into local pass claims. | Phase 12 audit passed with `metadata_debt: 0` and non-local evidence gates preserved. |
| Archive v1.0 before starting v1.1 | The completed milestone needs a stable historical record and fresh requirements surface before new cutover-hardening work begins. | v1.0 archives created under `.planning/milestones/`; next milestone should start from fresh requirements. |
| Treat v1.1 as evidence hardening, not parity redesign | The v1.0 source-backed contracts already define what must be true; v1.1 should make the remaining CI, simulator, hardware, live-service, release, and maintainer gates durable and auditable. | v1.1 shipped with Phase 13-22 gate capabilities and a passed audit rerun while preserving external evidence and final demotion as blocked until valid inputs exist. |
| Treat simulator evidence as traceable pending-input proof until real simulator inputs are supplied | Phase 14 can make simulator gates inspectable and runnable while still preventing quick/dry-run checks from claiming firmware or hardware behavior. | Phase 14 added the simulator evidence contract, quick artifact writer, explicit `--run-simulator --firmware` path, overclaim/secret guards, Bazel labels, and `just phase14-verify`. |
| Treat release artifact production as explicit release-environment input until approved release runs are supplied | Phase 20 can replace the empty release identity with a concrete Bazel target and verifier while still preventing local smoke fixtures or template rows from passing release proof. | Phase 20 added the release-environment input manifest, release-result manifest writer, signing/provenance/comparison guards, output-root symlink containment tests, Bazel/root/just wiring, and clean code review. |
| Treat final readiness as result-consuming review, not prose-link approval | Final reference demotion can only be meaningful if it consumes machine-readable upstream result manifests and maintainer decision inputs. | Phase 21 blocks `demotion_allowed` when upstream manifests are missing, failed, stale, redaction-failed, or not covered by approved exceptions. |
| Treat milestone archival as source-backed only after metadata reconciliation | Requirement status, validation metadata, roadmap progress, and audit state must agree before the milestone can be closed. | Phase 22 produced a validation signoff, audit-readiness artifact, and passed 2026-06-22 audit rerun before v1.1 archival. |
| Treat simulator execution evidence as retained input proof, not hardware proof | Phase 23 can validate and retain real simulator result packets, but hardware-only behavior must stay outside simulator claims until Phase 24 supplies hardware/media/safety evidence. | Phase 23 added the v1.2 simulator evidence execution contract, verifier, retained output writer, upstream row, secret/overclaim guards, and clean review closure. |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
1. Requirements validated? → Move to Validated with phase reference
1. New requirements emerged? → Add to Active
1. Decisions to log? → Add to Key Decisions
1. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections
1. Core Value check — still the right priority?
1. Audit Out of Scope — reasons still valid?
1. Update Context with current state

______________________________________________________________________

*Last updated: 2026-06-23 after Phase 23 completion*
