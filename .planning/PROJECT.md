# Prusa Firmware Buddy Rust Port

## What This Is

This project is a full Rust rewrite of the Prusa-Firmware-Buddy firmware while preserving the behavior of the current supported printer firmware. The existing C/C++/CMake codebase remains the reference implementation, but the target end state is a Rust firmware with Bazel as the authoritative build system and a `justfile` for common developer workflows.

The work is intentionally standards-driven: Bright Builds Rules guide architecture, code shape, verification, testing, and Rust module structure. Known defects and fragile areas identified in the codebase map should be fixed during the rewrite instead of being mechanically carried forward.

## Core Value

Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Build firmware for the currently supported Prusa printers using existing board, printer, bootloader, and feature option matrices — existing CMake/Python workflow in `CMakeLists.txt`, `ProjectOptions.cmake`, `CMakePresets.json`, and `utils/build.py`
- ✓ Support STM32-based embedded firmware targets with board-specific startup, HAL/CMSIS integration, linker scripts, and RTOS task orchestration — existing code in `src/device`, `src/buddy/main.cpp`, `lib/Drivers`, and `lib/Middlewares/Third_Party/FreeRTOS`
- ✓ Preserve the Marlin-derived printing core behavior, G-code handling, motion/planner flows, thermal behavior, and Buddy-specific server/client bridge — existing code in `lib/Marlin`, `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, and `src/marlin_stubs`
- ✓ Provide GUI-driven printer workflows for supported display resolutions, dialogs, menus, setup flows, errors, and print controls — existing code in `src/gui` and `src/guiapi`
- ✓ Provide local networking, Prusa Connect, PrusaLink/WUI, transfer, TLS, telemetry, registration, and command-channel behavior — existing code in `src/connect`, `src/transfers`, `src/common/http`, and `lib/WUI`
- ✓ Preserve persistent configuration, feature flags, language/resource generation, bootloader packaging, firmware artifacts, and host/simulator testing workflows — existing code in `src/persistent_stores`, `src/lang`, `src/gui/res`, `utils/`, and `tests/`

### Active

<!-- Current scope. Building toward these. -->

- [ ] Replace the firmware implementation with Rust while preserving behavior parity for currently supported printers.
- [ ] Make Bazel the primary build system for firmware, host tools, generated assets, tests, and release artifacts from the start of the migration.
- [ ] Provide a `justfile` that wraps common workflows such as bootstrap, build, test, format, lint, generated-file checks, and release artifact creation.
- [ ] Encode printer, board, feature, and artifact invariants in Rust types, constructors, and state machines instead of carrying sentinel-heavy C/C++ patterns forward.
- [ ] Maintain parity gates against the existing firmware for build outputs, supported printer behavior, generated resources, integration tests, and release packaging.
- [ ] Fix known issues and fragile areas surfaced by `.planning/codebase/CONCERNS.md` as their subsystems are rebuilt.
- [ ] Preserve Bright Builds Rules as the default engineering standard for architecture, testing, verification, code shape, and Rust module layout.

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Incremental dual-ownership migration as the primary strategy — user chose a Big Bang rewrite posture rather than subsystem-by-subsystem production cutover.
- Dropping existing supported printers to reduce migration work — behavior parity is a project constraint.
- Treating Bazel as a secondary experiment while CMake remains authoritative — user chose Bazel Primary Now.
- Adding new printer features unrelated to parity or defect remediation — new feature work would obscure whether the Rust firmware matches the existing baseline.
- Rewriting vendor or upstream third-party components before their replacement boundary is understood — firmware behavior takes priority over churn; any retained C/ASM/vendor code must be made explicit in requirements and roadmap phases.

## Context

The existing repository is a large embedded firmware codebase for Original Prusa printers. The current stack is C++23, C, ASM, CMake, Python tooling, STM32 HAL/CMSIS, FreeRTOS, Marlin, LwIP, mbedTLS, FatFs/littlefs, TinyUSB, Catch2, pytest, and a custom bootstrap flow. The codebase map in `.planning/codebase/` is the reference for current architecture, testing practices, integrations, and known concerns.

Phase 1 established the reference baseline package for the rewrite: supported matrix, reference-capture catalog, intentional-delta concern ledger, safety envelope, phase-local verifier, and verification report under `.planning/phases/01-reference-baseline-and-safety-envelope/`. Phase 2 established the root Bazel module, product platform labels, registered firmware toolchain labels, Bazel workflow targets, checked `justfile`, and Phase 2 verifier under `.planning/phases/02-bazel-authority-and-developer-facade/`. Phase 3 should attach deterministic generator and release-artifact actions to that Bazel surface.

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

*Last updated: 2026-06-02 after Phase 2 completion*
