# Feature Research

**Domain:** Behavior-parity Rust+Bazel rewrite of STM32 Prusa printer firmware
**Researched:** 2026-06-02
**Confidence:** HIGH for repository-derived parity scope; MEDIUM for phase-cost estimates until hardware validation plans are written

## Feature Landscape

For this project, "features" means parity capabilities, migration deliverables, and acceptance gates. The current C/C++/CMake firmware is the reference product. The Rust replacement is not viable until it preserves the observable behavior of supported printer builds, artifacts, safety behavior, UI flows, network protocols, persistence, resources, and tests.

### Table Stakes (Users Expect These)

Missing any P1 item below means the Rust firmware is not a behavior-parity replacement.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Supported printer, board, MCU, bootloader, and artifact matrix | `ProjectOptions.cmake`, `CMakePresets.json`, and `README.md` define the release surface users and CI expect. | HIGH | Preserve COREONE, MINI, MK4, MK3.5, XL, iX, XL_DEV_KIT, BUDDY, XBUDDY, XLBUDDY, DWARF, MODULARBED, XL_DEV_KIT_XLB, XBUDDY_EXTENSION, STM32F4/G0/H5 MCUs, boot/noboot variants, debug/release presets, `.bin`, `.bbf`, `.dfu`, `.map`, signing, version fields, and resource images. Verify the README-listed MK3.9 mapping before roadmap lock because the CMake option matrix exposes MK3.5/MK4 but not a separate MK3.9 option. |
| Bazel-primary build and `justfile` workflow parity | The project decision makes Bazel authoritative now, and developers still need stable wrappers for common commands. | HIGH | Bazel must build firmware, host tools, generated assets, unit tests, simulator/integration inputs, release artifacts, and puppy/extension firmware. The `justfile` should wrap bootstrap, build, test, format, lint, codegen drift checks, and release packaging. |
| STM32 startup, HAL/CMSIS, linker, FreeRTOS, and task orchestration | Firmware cannot boot safely without board-specific startup, memory layout, interrupts, peripherals, scheduler, watchdog, and task dependency behavior. | HIGH | Preserve `src/device`, `src/buddy/main.cpp`, `src/freertos`, `TaskDeps`, filesystem/network/display/connect/puppy task startup, C/C++ runtime replacement semantics, crash dump entry paths, and safe-state failure behavior. |
| Marlin-derived printing core and Buddy bridge behavior | Printing behavior is the product baseline: G-code, motion, planner, thermal, pause/resume/cancel, host control, and slicer compatibility must not regress. | HIGH | Preserve Marlin setup/loop semantics, `marlin_server` serialization, `marlin_client` request/event behavior, `marlin_vars`, Buddy G/M-code stubs such as M862 checks, M997 updates, M600 color change, G29 mesh/probe flows, serial printing behavior, BGcode/file parsing, and GUI/Connect command routing. |
| Safety-critical thermal, motion, selftest, and recovery behavior | Users do not distinguish firmware rewrites from safety regressions; hardware must fail into known safe states. | HIGH | Preserve min/max/temp-runaway/preheat errors, crash detection, power panic, emergency stop, safe outputs, watchdog/assert/BSOD/redscreen flows, selftest gates, calibration flows, fan/loadcell/axis/first-layer tests, and integration tests such as `tests/integration/test_safety.py`. |
| Printer-specific hardware feature gates | Existing firmware behavior varies by printer and board; parity requires matching those combinations, not just compiling one generic image. | HIGH | Preserve filament sensor variants, Trinamic/TMC paths, precise homing, phase stepping, burst stepping, input shaper calibration, loadcell/HX717, beds/local/remote/modular, side sensors, ESP flashing, XLCD/touch, LEDs, MMU2, NFC, door sensor, chamber, cold pull, cancel object, auto retract, nozzle cleaner, belt tuning, gearbox alignment, wastebin, print fan type, and xBuddy extension gates. |
| GUI workflows for both display classes | The GUI is the primary local control surface. Missing screens or wrong layout behavior is a user-visible regression. | HIGH | Preserve 240x320 MINI and 480x320 XLCD layouts, touch defaults, screen stack/static allocation semantics, dialogs, menus, wizards, print preview/control/progress, redscreen/warning screens, language selection, filament workflows, selftest/calibration screens, Connect registration dialogs, PrusaLink screens, and unit layout/text-fit coverage. |
| Networking, Prusa Connect, PrusaLink/WUI, transfers, and service protocols | Remote control, local API access, downloads, and telemetry are existing firmware capabilities and integration surfaces. | HIGH | Preserve LwIP integration, Prusa Connect registration/telemetry/events/WebSocket-current behavior, token/fingerprint headers, TLS 1.2 verification, proxy behavior and its current limitations, custom certificate path after bug fix, PrusaLink API v1, OctoPrint-compatible endpoints, WUI static assets, digest/API-key auth, downloads, encrypted/ranged transfers, transfer recovery, SNTP, mDNS, metrics, and syslog. |
| Persistent configuration, migrations, filesystems, and settings import/export | Existing settings and credentials must survive firmware replacement without corrupting EEPROM/internal flash state. | HIGH | Preserve config-store schema, journal IDs/hashes, migrations, defaults, deprecated item IDs, EEPROM/NFC/storage drivers, `/usb`, `/internal`, optional `/semihosting`, FatFs, littlefs, config keys in `doc/prusa_printer_settings.ini`, Wi-Fi/PrusaLink/Connect credentials, selftest results, and resource revisions. |
| Resources, localization, fonts, web assets, ESP blobs, bootloader resources, and generated files | The firmware bundles assets into release artifacts and runtime resource images; stale generation changes user-visible behavior. | HIGH | Preserve littlefs images, QOI/icon/font generation, translations for CS/DE/ES/FR/IT/JA/PL/UK, MINI extflash translation behavior, WUI assets, ESP32/ESP8266 blobs, MMU/puppy firmware resources, bootloader update images, hash headers, and generated-file drift checks. |
| Puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, and toolchanger ecosystem | XL/iX/COREONE behavior depends on auxiliary controllers and bootload/update flows, not only master-board firmware. | HIGH | Preserve puppy firmware builds, resource embedding, startup flashing, Modbus/RS485 protocols, Dwarf and ModularBed runtime firmware, xBuddy Extension firmware, time sync, crash dump download, remote bed, toolchanger, dock/tool offset flows, MMU over UART/extension behavior, and development modes such as skip-flash/prebuilt binaries. |
| Observability, diagnostics, and support artifacts | Debugging firmware regressions depends on logs, metrics, crash dumps, version/provenance, and CI artifacts. | MEDIUM | Preserve log components/destinations, RTT/file/syslog/USB/buffer sinks, metrics G-codes and UDP output, generated error-code and translation reports, crash dump export behavior, firmware version/build suffixes, map files, memory reports, and simulator logs. |
| Host, simulator, unit, integration, and generated-file verification gates | Big Bang migration needs evidence, not assertion, that behavior still matches the reference firmware. | HIGH | Preserve and expand Catch2-style unit coverage as Rust unit tests where possible, pytest simulator flows, MK4 noboot integration baseline, blockdevice tests, Python binding tests or replacements, pre-commit/codegen checks, and CI-equivalent Bazel targets. Add parity harnesses against reference artifacts/protocol traces. |

### Differentiators (Competitive Advantage)

These are valuable outcomes of the rewrite. They should not add new printer behavior unless they directly support parity or fix known defects.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Typed printer/board/feature/artifact model | Replaces global macro coupling with explicit Rust/Bazel invariants. | HIGH | Encode valid printer-board-MCU-feature-artifact combinations as types, constructors, and Bazel transitions/rules so invalid builds fail early. |
| Pure state-machine cores with thin adapters | Makes Marlin bridge, Connect planner, transfers, config migrations, selftests, and resource decisions cheaper to test. | HIGH | Follow functional-core/imperative-shell: keep HAL, RTOS, filesystem, network, and FFI at boundaries; unit test pure transitions. |
| Hermetic Bazel code generation and packaging | Eliminates generated asset drift and makes releases reproducible. | HIGH | Make option headers, CMakePreset-equivalent matrix data, resources, translations, fonts, log docs, journal hashes, BBF/DFU packaging, and reports generated/checkable by Bazel targets. |
| Explicit foreign-code boundary manifest | Prevents accidental churn in vendor/HAL/Marlin/FreeRTOS/mbedTLS/TinyUSB code while still naming retained C/ASM dependencies. | MEDIUM | v1 can retain carefully wrapped C/ASM/vendor code where replacement would risk behavior; every retained boundary should have owner, reason, API, and verification gates. |
| Rust safety wrappers for RTOS, queues, locks, buffers, and hardware resources | Reduces concurrency, lifetime, and memory unsafety without pretending embedded firmware is fully safe Rust. | HIGH | Model task ownership, lock ordering, single-transfer slot semantics, DMA/buffer lifetimes, interrupt access, filesystem handles, and hardware capabilities with narrow unsafe boundaries. |
| Defect-remediation parity gate | Fixes known fragile areas while preserving behavior. | MEDIUM | Prioritize custom TLS DER read path, probe-analysis classification coupling, home-screen flash-action freeze, transfer direct-sector race constraints, MMU availability state, STM32G0 IRQ path, and generated drift checks. |
| Reference-firmware comparison harness | Gives roadmap phases a concrete acceptance mechanism. | HIGH | Compare build matrix, artifact metadata, resource hashes where appropriate, API responses, G-code outcomes, simulator screen flows, safety errors, config migrations, and network/transfer traces against the C/C++ reference. |
| Developer workflow convergence through `just` | Makes the new Bazel workflow discoverable and avoids CMake-era tribal knowledge. | LOW | Provide `just bootstrap`, `just build`, `just test`, `just fmt`, `just lint`, `just codegen-check`, `just sim-test`, and `just release` wrappers around Bazel/Rust tools. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Drop older or awkward printer variants to shrink v1 | It would reduce migration work. | It violates Behavior Parity and hides compatibility gaps until late. | Preserve the current supported matrix and explicitly resolve the MK3.9/MK3.5/MK4 mapping ambiguity before phase planning. |
| Incremental dual production ownership | It feels safer than Big Bang. | The user chose Big Bang; dual ownership can leave two firmware stacks with divergent behavior and unclear release authority. | Build parity harnesses and comparison gates while keeping the cutover target as one coherent Rust+Bazel firmware. |
| Add new printer/product features during parity work | New features create visible progress. | They obscure whether Rust matches the reference and expand the acceptance surface. | Only fix known defects or reduce migration risk; park new behavior for v1.x/v2. |
| Treat Bazel as a wrapper around CMake | It seems faster for initial builds. | It contradicts Bazel Primary Now and preserves the global target/codegen coupling the rewrite is meant to remove. | Use CMake as a reference/comparison input, but make Bazel the authoritative graph for builds, codegen, tests, and release artifacts. |
| Rewrite all vendor/upstream code immediately | A "pure Rust" target sounds cleaner. | Replacing Marlin, HAL/CMSIS, FreeRTOS, mbedTLS, TinyUSB, FatFs/littlefs, or low-level ASM too early risks behavior drift and schedule collapse. | Retain or wrap foreign code where prudent, document each boundary, and replace only when the behavior contract and tests are understood. |
| Copy C/C++ sentinel-heavy patterns into Rust | It is mechanically close to the reference. | It gives up the main rewrite benefit and carries known ambiguity into the new code. | Parse raw values into domain types and use enums/newtypes/state machines for printer, config, transfer, command, and hardware states. |
| Ship with compile-only or single-printer verification | It is cheaper than full parity testing. | Embedded behavior can compile while safety, network, UI, artifact, or printer-specific behavior is wrong. | Require matrix builds plus targeted unit, simulator, protocol, artifact, and hardware-aware gates. |
| Expand beyond existing transfer semantics, such as concurrent downloads | It can look like a platform improvement. | Existing code intentionally has single-slot transfer semantics and lock-order constraints; changing them is not parity. | Preserve one active transfer slot in v1; redesign concurrency only after parity is stable. |
| Add unsupported network/security extensions such as proxy auth or broad custom TLS behavior | It may satisfy enterprise requests. | Existing docs state proxy limitations; changing authentication/TLS flows risks compatibility and support surprises. | Fix the known custom DER read bug, preserve current proxy semantics, and defer new proxy/auth/security features to post-parity work. |
| Remove legacy protocols because a newer path exists | It simplifies implementation. | PrusaLink, OctoPrint-compatible endpoints, current Connect command paths, serial G-code, and firmware artifacts are compatibility surfaces. | Preserve existing protocol behavior first; deprecate only through an explicit compatibility decision later. |

## Feature Dependencies

```text
Reference firmware inventory
    requires -> Build matrix extraction
    requires -> Runtime capability inventory
    requires -> Test and artifact inventory

Bazel authoritative graph
    requires -> Toolchain and platform definitions
    requires -> Printer/board/MCU/feature model
    requires -> Codegen and resource ownership
    enables  -> justfile workflows
    enables  -> release artifact parity
    enables  -> simulator/test targets

STM32/HAL/RTOS shell
    requires -> Linker/startup/interrupt parity
    requires -> FreeRTOS/task primitive wrappers
    enables  -> Filesystems, GUI, networking, Marlin server, puppy task

Marlin printing core and Buddy bridge
    requires -> STM32/HAL/RTOS shell
    requires -> Config store and persistent state
    requires -> Filesystem/media access
    enables  -> GUI print controls
    enables  -> Connect/PrusaLink remote commands
    enables  -> Safety and selftest workflows

Persistent config and filesystems
    requires -> Storage drivers and migrations
    enables  -> Network credentials
    enables  -> Resources and translations
    enables  -> Transfers, crash dumps, settings import/export

Resources and generated assets
    requires -> Bazel codegen ownership
    requires -> Filesystem/image packaging
    enables  -> GUI assets, WUI assets, translations, ESP flashing, puppy bootload, bootloader updates

Puppy/MMU/toolchanger ecosystem
    requires -> Resource packaging
    requires -> Modbus/RS485 protocols
    requires -> Marlin/toolchanger integration
    enables  -> XL/iX/COREONE parity

Parity acceptance gates
    requires -> Reference artifacts and protocol traces
    requires -> Bazel-built Rust artifacts
    requires -> Simulator/hardware-aware execution
    gates    -> v1 cutover
```

### Dependency Notes

- **Bazel graph requires the feature matrix:** Printer, board, MCU, bootloader, resource, translation, GUI, touch, puppy, MMU, and network options must become authoritative structured data before reliable Rust target generation is possible.
- **Runtime shell precedes product behavior:** Marlin, GUI, Connect, WUI, resources, transfers, and puppies all depend on startup, HAL, FreeRTOS, task readiness, filesystems, and logging.
- **Config and storage unlock network/UI parity:** Connect, PrusaLink, Wi-Fi, credentials, settings import/export, selftest results, resources, and migrations all read/write the config store or mounted filesystems.
- **Resources are a release and runtime dependency:** WUI assets, ESP firmware, puppy firmware, bootloader resources, translations, fonts, QOI images, and hashes must be generated and packaged before end-to-end boot and UI parity can pass.
- **Puppies are not optional for XL/iX/COREONE parity:** Dwarf, ModularBed, and xBuddy Extension behavior gates toolchanger, remote bed, chamber, MMU pass-through, bootload, and crash-dump flows.
- **Known defect fixes require coupled tests:** Probe math, TLS DER loading, transfer races, GUI freeze paths, MMU availability, generated drift, and STM32G0 IRQ behavior should each gain regression guards when rebuilt.

## MVP Definition

### Launch With (v1)

Because the user chose Big Bang plus Behavior Parity, v1 launch is the replacement cutover, not a reduced product.

- [ ] Complete Bazel build matrix for supported master and auxiliary firmware targets, including boot/noboot, debug/release, resources, signing, `.bin`, `.bbf`, `.dfu`, `.map`, and host tools.
- [ ] `justfile` wrappers for bootstrap, build, test, format, lint, generated-file checks, simulator tests, and release artifact creation.
- [ ] STM32 startup/HAL/FreeRTOS/task/filesystem/logging shell parity for all supported boards and MCUs.
- [ ] Marlin printing core parity or an explicitly wrapped retained core with Rust-safe request/event/domain boundaries.
- [ ] Safety, thermal, crash, selftest, calibration, power panic, emergency stop, and recovery behavior parity.
- [ ] GUI parity across 240x320 and 480x320 display classes, including menus, dialogs, print controls, registration, warnings, redscreens, translations, and layout tests.
- [ ] Network parity for Prusa Connect, PrusaLink/WUI, OctoPrint-compatible API, TLS/proxy/custom-cert current behavior, downloads, transfers, SNTP, mDNS, metrics, and syslog.
- [ ] Persistent config, journal/migration, EEPROM/NFC/internal flash, filesystem, settings import/export, credential, and resource revision parity.
- [ ] Resource and localization generation/package parity for fonts, icons, translations, WUI, ESP blobs, puppy firmware, bootloader resources, and generated hashes.
- [ ] Puppy/Dwarf/ModularBed/xBuddy Extension/MMU2/toolchanger/remote bed/chamber feature parity for affected printers.
- [ ] Reference comparison gates for build artifacts, option matrix, generated assets, G-code behavior, simulator flows, PrusaLink/Connect responses, transfer behavior, config migrations, and safety errors.
- [ ] Documented foreign-code boundary manifest for retained C/C++/ASM/vendor components.

### Add After Validation (v1.x)

These are useful after the parity cutover is credible, but they should not block v1 unless a phase discovers they are required for parity.

- [ ] Wider simulator coverage beyond the current MK4 noboot baseline - add after Bazel can produce all simulator inputs reliably.
- [ ] Hardware-in-the-loop smoke matrix - add as soon as representative boards are available and core firmware boots.
- [ ] Dependency inventory and update policy for retained vendor code - add after the foreign-code boundary manifest stabilizes.
- [ ] Additional security hardening such as credential export policy or encryption-at-rest - add after compatibility and hardware assumptions are documented.
- [ ] Expanded observability dashboards and performance telemetry - add after parity tests can detect baseline regressions.
- [ ] Connect/WebSocket path cleanup or deprecation decisions - add only after current server behavior and protocol compatibility are validated.

### Future Consideration (v2+)

- [ ] New printer UX/product features - defer because they obscure parity.
- [ ] Multi-transfer or concurrent transfer redesign - defer because current single-slot semantics are a compatibility constraint.
- [ ] Broad proxy authentication, enterprise TLS modes, or new cloud APIs - defer because current docs and code define narrower behavior.
- [ ] Full Rust replacement of every vendor/upstream component - defer until behavior contracts, licensing, update cadence, and tests justify the churn.
- [ ] New display resolutions or UI frameworks - defer unless required by a supported printer in the current matrix.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Supported printer/board/build/artifact matrix | HIGH | HIGH | P1 |
| Bazel authoritative graph and `justfile` workflows | HIGH | HIGH | P1 |
| STM32/HAL/FreeRTOS runtime shell | HIGH | HIGH | P1 |
| Marlin printing core and Buddy bridge | HIGH | HIGH | P1 |
| Safety, thermal, crash, selftest, and recovery behavior | HIGH | HIGH | P1 |
| GUI parity across supported display classes | HIGH | HIGH | P1 |
| Networking, Connect, PrusaLink/WUI, transfers, TLS, metrics | HIGH | HIGH | P1 |
| Persistent config, migrations, filesystems, resources | HIGH | HIGH | P1 |
| Puppy/MMU/toolchanger/remote-bed ecosystem | HIGH | HIGH | P1 |
| Generated asset/codegen drift checks | HIGH | MEDIUM | P1 |
| Reference comparison harness | HIGH | HIGH | P1 |
| Typed domain model and Rust safety boundaries | HIGH | HIGH | P1 |
| Known defect remediation with regression tests | HIGH | MEDIUM | P1 |
| Wider simulator and hardware-in-loop coverage | HIGH | MEDIUM | P2 |
| Dependency inventory/update policy | MEDIUM | MEDIUM | P2 |
| Security hardening beyond current behavior | MEDIUM | HIGH | P2 |
| Performance/observability dashboards | MEDIUM | MEDIUM | P2 |
| New printer features | LOW for parity | HIGH | P3 |
| Full vendor rewrite | LOW for parity | HIGH | P3 |

**Priority key:**

- P1: Must have for v1 behavior-parity cutover
- P2: Should have after core parity is demonstrable or where a phase proves it is necessary
- P3: Future consideration; do not include in v1 parity scope

## Competitor Feature Analysis

For this brownfield rewrite, the "competitor" is the reference C/C++/CMake firmware. The Rust+Bazel replacement wins only by matching behavior while improving maintainability, testability, and build discipline.

| Feature | Reference Firmware | Risk if Missing | Our Approach |
|---------|--------------------|-----------------|--------------|
| Release build matrix | `utils/build.py`, `ProjectOptions.cmake`, and `CMakePresets.json` build supported printer/bootloader variants and products. | Users cannot install or compare release artifacts. | Encode the matrix in Bazel, expose `just` wrappers, and compare artifact metadata/resources against the reference. |
| Print behavior | Marlin plus Buddy server/client bridge owns G-code, motion, planner, thermal, pause/resume/cancel, and state reporting. | Unsafe or visibly different printing. | Retain/wrap or port with strict request/event/state-machine tests and simulator/hardware gates. |
| Local UI | `src/gui` provides screen stack, dialogs, menus, wizards, layouts, text fitting, translations, and print controls. | Printer feels broken even if motion works. | Port UI domain/state/layout logic with golden screen-flow tests and resolution-specific layout checks. |
| Remote/local network control | `src/connect`, `lib/WUI`, `src/transfers`, and LwIP/mbedTLS expose Connect, PrusaLink, WUI, downloads, TLS, proxy, SNTP, mDNS, metrics, syslog. | Existing apps, cloud, slicers, and support workflows regress. | Preserve APIs and protocol traces; fix known custom-cert defect with targeted tests. |
| Persistence/resources | Config store, journal, littlefs/FatFs, resource images, fonts, translations, WUI assets, ESP/puppy blobs, bootloader resources. | Settings loss, bad assets, failed bootload/update, missing localization. | Make codegen and image packaging hermetic in Bazel; add drift checks and migration tests. |
| Auxiliary boards | Puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, and toolchanger flows are built and flashed through the firmware/resource pipeline. | XL/iX/COREONE support is incomplete. | Treat auxiliary firmware and Modbus protocols as first-class Bazel targets with integration gates. |
| Verification | Catch2, CTest, pytest simulator, blockdevice tests, Python binding tests, pre-commit/codegen hooks, Jenkins stages. | Big Bang cutover relies on hope. | Replace/port tests into Bazel/Rust equivalents and add reference comparison gates. |

## Sources

- Local repository context: `.planning/PROJECT.md`
- Local codebase map: `.planning/codebase/STACK.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/CONCERNS.md`
- Local build and option evidence: `ProjectOptions.cmake`, `CMakePresets.json`, `CMakeLists.txt`, `utils/build.py`, `utils/presets/presets.json`
- Local runtime and feature evidence: `src/buddy`, `src/common`, `src/common/feature`, `src/feature`, `src/gui`, `src/connect`, `src/transfers`, `src/persistent_stores`, `src/resources`, `src/mmu2`, `src/puppies`, `src/puppy`, `lib/Marlin`, `lib/WUI`
- Local verification evidence: `tests/unit`, `tests/integration`, `tests/blockdevice`, `.pre-commit-config.yaml`, `utils/holly/build-pr.jenkins`, `README.md`, `tests/unit/README.md`, `tests/integration/README.md`
- External standards context: `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/index.md`
- External standards context: `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md`
- External standards context: `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/verification.md`
- External standards context: `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md`
- External standards context: `https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md`

______________________________________________________________________

*Feature research for: behavior-parity Rust+Bazel firmware rewrite*
*Researched: 2026-06-02*
