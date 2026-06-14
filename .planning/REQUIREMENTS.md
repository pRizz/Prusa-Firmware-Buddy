# Requirements: Prusa Firmware Buddy Rust Port

**Defined:** 2026-06-02
**Core Value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.

## v1 Requirements

### Baseline and Parity

- [x] **BASE-01**: Maintainer can inspect a complete supported printer, board, MCU, bootloader, feature, and artifact matrix derived from the existing firmware reference.
- [x] **BASE-02**: Maintainer can run reference-capture targets that preserve existing C/C++ firmware behavior fixtures for builds, generated assets, protocol traces, simulator flows, persistent config migrations, and release artifacts.
- [x] **BASE-03**: Maintainer can review an intentional-delta ledger that classifies known defects from `.planning/codebase/CONCERNS.md` as preserved temporarily, fixed during rewrite, or explicitly deferred.
- [x] **BASE-04**: Maintainer can evaluate a safety envelope covering startup, watchdogs, thermal states, motion safe states, endstops, fans, loadcell/probe behavior, power panic, crash dumps, and emergency/error flows before Rust cutover.

### Bazel Build System

- [x] **BAZL-01**: Developer can use Bazel as the authoritative build graph through `MODULE.bazel`, `.bazelrc`, registered Rust/C/C++/ASM toolchains, and explicit product platforms.
- [x] **BAZL-02**: Developer can build Rust firmware, retained C/ASM/vendor code, generated assets, host tools, unit tests, simulator inputs, and release packages from Bazel without invoking CMake as the source of truth.
- [ ] **BAZL-03**: Developer can produce firmware artifacts matching the reference release surface, including `.bin`, `.bbf`, `.dfu`, map/provenance outputs, resource images, boot/noboot variants, and auxiliary firmware packages.
- [x] **BAZL-04**: Developer can run a checked `justfile` facade for common commands including bootstrap, build, test, format, lint, generated-file drift checks, simulator/parity checks, and release packaging.
- [ ] **BAZL-05**: Developer can run Bazel-owned generators for product profiles, option data, resources, translations, fonts, WUI assets, ESP blobs, puppy/MMU descriptors, and package metadata with deterministic drift checks.

### Rust Firmware Architecture

- [x] **RUST-01**: Developer can build a Rust workspace/crate layout that separates pure domain crates from board/runtime/application adapters according to Bright Builds functional-core/imperative-shell guidance.
- [x] **RUST-02**: Developer can represent printer, board, MCU, bootloader, feature, storage schema, artifact, and protocol invariants with Rust newtypes, enums, constructors, and state machines so invalid combinations fail early.
- [x] **RUST-03**: Developer can inspect a foreign-code inventory for every retained C, C++, ASM, generated, and vendor component, including retention reason, version/source, ownership boundary, safe Rust facade, and replacement posture.
- [x] **RUST-04**: Developer can audit all `unsafe`, FFI, MMIO, DMA, interrupt, linker-symbol, static-memory, allocator, and panic-boundary code through narrow adapter crates with documented invariants and tests.
- [x] **RUST-05**: Developer can run Rust formatting, clippy/lint, unit-test, doc, and build checks through Bazel/just with Bright Builds Rust style expectations enforced where practical.

### Core Firmware Behavior

- [x] **CORE-01**: Rust firmware preserves STM32 startup, memory layout, vector/interrupt behavior, board clocks, HAL/CMSIS integration, watchdog behavior, and linker-controlled sections for supported MCU families.
- [x] **CORE-02**: Rust firmware preserves FreeRTOS task orchestration, task dependency readiness, static task memory assumptions, synchronization behavior, queues, timers, and startup ordering for master and auxiliary firmware.
- [x] **CORE-03**: Rust firmware preserves printing core behavior for G-code parsing/routing, motion/planner-visible operations, thermal state transitions, pause/resume/cancel flows, serial printing, file printing, and Buddy-specific G/M-code handlers.
- [x] **CORE-04**: Rust firmware preserves safety-critical thermal, motion, selftest, calibration, crash detection, power panic, emergency stop, safe-output, redscreen/BSOD/assert, and recovery behavior.
- [x] **CORE-05**: Rust firmware preserves printer-specific feature gates including filament sensors, TMC paths, precise homing, input shaper, phase/burst stepping, loadcell/HX717, beds, chamber, door, MMU2, NFC, LEDs, toolchanger, and xBuddy Extension behavior.

### Interfaces and Resources

- [x] **IFCE-01**: Rust firmware preserves GUI workflows for supported display classes, including screen stack behavior, dialogs, menus, wizards, warnings, redscreens, print controls, selftest/calibration flows, Connect registration, and localization.
- [x] **IFCE-02**: Rust firmware preserves Prusa Connect behavior for registration, tokens/fingerprints, telemetry, events, WebSocket commands, TLS verification, transfer/download integration, and current proxy limitations unless explicitly fixed.
- [x] **IFCE-03**: Rust firmware preserves PrusaLink/WUI behavior including HTTP API v1, OctoPrint-compatible endpoints, digest/API-key auth, WUI static assets, SNTP, mDNS, metrics, and syslog.
- [x] **IFCE-04**: Rust firmware preserves persistent configuration, schema migrations, defaults, deprecated item IDs, credentials, settings import/export, EEPROM/internal flash behavior, FatFs/littlefs mounts, USB/internal/semihosting paths, and config hash/journal behavior.
- [x] **IFCE-05**: Rust firmware preserves resources, translations, fonts, icons, littlefs images, bootloader resources, ESP blobs, WUI assets, language packs, and generated headers visible to runtime or release artifacts.
- [ ] **IFCE-06**: Rust firmware preserves puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, Modbus/RS485, toolchanger, dock/tool offset, startup flashing, skip-flash/prebuilt firmware, and auxiliary-controller update flows.

### Verification and Cutover

- [ ] **VERF-01**: Developer can run a parity test pyramid covering pure Rust unit tests, adapter contract tests, generated drift checks, reference fixture comparisons, simulator flows, network/TLS/API tests, release artifact checks, and hardware smoke gates.
- [x] **VERF-02**: Developer can run tests for pure firmware/domain logic with focused Arrange, Act, Assert structure and near-total coverage for state machines, parsers, policy, migrations, and protocol decisions.
- [ ] **VERF-03**: Developer can compare Rust outputs against reference firmware for product artifacts, generated resources, storage migrations, protocol traces, G-code behavior fixtures, UI state fixtures, and release metadata.
- [ ] **VERF-04**: Maintainer can review cutover evidence showing every v1 requirement mapped to passing tests, simulator or hardware evidence, intentional deltas, and residual retained-code justifications.
- [ ] **VERF-05**: Maintainer can remove or demote the CMake/C++ reference path only after the Rust+Bazel build satisfies all parity gates and documented cutover criteria.

## v2 Requirements

### Post-Parity Improvements

- **V2-01**: Replace retained vendor C/HAL/RTOS/network/filesystem components with Rust alternatives where hardware evidence, maintenance cost, and ecosystem maturity justify it.
- **V2-02**: Add new printer UX or firmware features unrelated to parity after the Rust+Bazel firmware is verified as the production baseline.
- **V2-03**: Expand network/proxy/TLS capabilities beyond current firmware behavior after compatibility-sensitive cloud and local API parity is complete.
- **V2-04**: Redesign transfer concurrency, storage layout, or UI framework choices after v1 behavior parity is accepted.
- **V2-05**: Add broader hardware automation labs and long-run soak dashboards after the initial cutover evidence exists.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Incremental production migration as the primary plan | User chose Big Bang; roadmap can still use internal scaffolding but should lead to a full replacement cutover. |
| Dropping supported printers to make the port easier | User chose Behavior Parity as the compatibility bar. |
| CMake remaining authoritative while Bazel is experimental | User chose Bazel Primary Now. |
| New feature development during v1 | It would obscure whether the Rust firmware preserves existing behavior. |
| Silent changes to known bugs | Defect fixes must be documented as intentional deltas with tests. |
| Untracked retained C/C++/ASM/vendor islands | Any retained foreign code must have a named boundary, owner, reason, and test strategy. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BASE-01 | Phase 1 | Completed |
| BASE-02 | Phase 1 | Completed |
| BASE-03 | Phase 1 | Completed |
| BASE-04 | Phase 1 | Completed |
| BAZL-01 | Phase 2 | Completed |
| BAZL-02 | Phase 2 | Completed |
| BAZL-03 | Phase 3 | Pending |
| BAZL-04 | Phase 2 | Completed |
| BAZL-05 | Phase 3 | Pending |
| RUST-01 | Phase 4 | Completed |
| RUST-02 | Phase 4 | Completed |
| RUST-03 | Phase 5 | Complete |
| RUST-04 | Phase 5 | Complete |
| RUST-05 | Phase 4 | Completed |
| CORE-01 | Phase 5 | Complete |
| CORE-02 | Phase 5 | Complete |
| CORE-03 | Phase 6 | Complete |
| CORE-04 | Phase 6 | Complete |
| CORE-05 | Phase 6 | Complete |
| IFCE-01 | Phase 8 | Complete |
| IFCE-02 | Phase 9 | Complete |
| IFCE-03 | Phase 9 | Complete |
| IFCE-04 | Phase 7 | Complete |
| IFCE-05 | Phase 7 | Complete |
| IFCE-06 | Phase 10 | Pending |
| VERF-01 | Phase 11 | Pending |
| VERF-02 | Phase 4 | Completed |
| VERF-03 | Phase 11 | Pending |
| VERF-04 | Phase 11 | Pending |
| VERF-05 | Phase 11 | Pending |

**Coverage:**

- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0

______________________________________________________________________

*Requirements defined: 2026-06-02*
*Last updated: 2026-06-02 after Phase 1 completion*
