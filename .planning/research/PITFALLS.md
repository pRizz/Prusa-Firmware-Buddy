# Pitfalls Research

**Domain:** Big Bang Rust+Bazel rewrite of safety-relevant embedded 3D printer firmware
**Researched:** 2026-06-02
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Behavior Parity Becomes "It Builds And Prints A Demo"

**What goes wrong:**
The Rust firmware appears successful because it boots, renders the UI, connects to the network, and prints a basic file, while edge behavior diverges from the C/C++ reference. Drift can show up in G-code sequencing, Marlin planner behavior, pause/resume flows, thermal state transitions, persistent config migration, selftest, MMU/puppy behavior, Connect command reporting, transfer recovery, translations, and error-code mapping.

**Why it happens:**
A Big Bang migration removes incremental production feedback. The existing firmware has many implicit contracts spread across CMake options, generated headers, Marlin integration, FreeRTOS tasks, GUI screens, Connect, WUI, transfers, resources, bootloader packaging, and persistent stores. If parity is defined by broad manual scenarios, teams will unconsciously verify happy paths and miss compatibility edge cases.

**How to avoid:**
Start with a reference-baseline phase that captures current C/C++ behavior as executable fixtures before rewriting subsystems. Build parity gates for every behavior class: build matrix, boot, task readiness, G-code queueing, planner-visible outcomes, thermal and safety states, GUI workflows, Connect/WUI APIs, transfers, persistent config migrations, generated assets, firmware packages, and release metadata. Treat known defects from `.planning/codebase/CONCERNS.md` as explicit decisions: either preserve for compatibility until a named fix phase, or fix with new expected fixtures and regression tests.

**Warning signs:**
Parity tickets say "manual compare", "same enough", or "covered by simulator smoke test"; tests only assert successful boot/print; old C++ fixtures are deleted before Rust fixtures exist; new Rust APIs expose raw primitives where the old firmware had implicit invariants; known bugs such as probe classification, TLS custom cert loading, or GUI freeze paths are neither preserved nor intentionally fixed.

**Phase to address:**
Phase 1: Reference Baseline and Safety Envelope. Keep it active as an acceptance gate through all later phases.

______________________________________________________________________

### Pitfall 2: Hardware Safety Changes Hide Behind Safer-Looking Rust

**What goes wrong:**
Heaters, steppers, fans, endstops, loadcell/probe analysis, watchdogs, power-fail handling, IRQ setup, safe-state entry, crash dumps, and boot error screens behave differently under failure. The rewrite may be memory-safe in ordinary Rust code but still unsafe at the hardware boundary, where wrong register writes, interrupt priority, task ordering, DMA buffers, or linker sections can create safety-relevant faults.

**Why it happens:**
Rust does not remove the need for `unsafe` around MMIO, startup, vector tables, linker symbols, FFI, DMA, interrupt handlers, and retained C/HAL code. Bare-metal Rust uses `no_std`; the standard runtime and its protections are not available by default. The existing firmware also relies on FreeRTOS startup dependencies, static task memory, board-specific HAL/CMSIS files, and board/printer macros that can be mis-modeled during a rewrite.

**How to avoid:**
Define a hardware safety envelope before implementation: pin and peripheral maps, safe output states, watchdog expectations, IRQ priority rules, stack budgets, panic/fault paths, and task dependency contracts for every supported board. Keep all MMIO/FFI/interrupt code in small reviewed adapter modules with documented safety invariants. Add hardware-in-loop or simulator failure injection for heater cutoff, endstop/probe events, network stalls during print, USB/media loss, watchdog reset, and startup error-screen paths. Use FreeRTOS stack high-water/overflow instrumentation or an equivalent Rust-side measurement for every task that replaces an existing task.

**Warning signs:**
`unsafe` appears in domain modules; HAL wrappers are accepted without written invariants; task stack sizes are copied without measurement; panic paths are left as placeholders; board support is declared done without map/linker/interrupt comparison; safety states are only reviewed in code and not exercised.

**Phase to address:**
Phase 1: Reference Baseline and Safety Envelope; Phase 3: Hardware Abstraction and Retained Vendor Boundary.

______________________________________________________________________

### Pitfall 3: Bazel Becomes A Non-Hermetic CMake Clone

**What goes wrong:**
Bazel is "primary" in name, but it calls ad hoc scripts, consumes host-installed tools, reads generated files that are not declared as inputs, or mirrors CMake global include behavior. Builds pass on one developer machine and fail or produce different artifacts in CI. Tracked generated files such as `CMakePresets.json`, logging docs, struct visitors, font headers, font indices, and translation templates drift from their generators.

**Why it happens:**
The existing build has broad target coupling through `BuddyHeaders`, generated option headers, manual translation/font regeneration, duplicated pre-commit generation hooks, and CMake/Python packaging behavior. Bazel's value depends on hermetic declared inputs, tools, outputs, and platforms; copying CMake's global target shape into Bazel preserves the fragility while adding a second build language.

**How to avoid:**
Make Bazel the single authority for toolchains, generated outputs, resources, and release artifacts from Phase 2. Every generator must have declared `srcs`, `tools`, `outs`, check mode, and a stable owner. Keep a `just generated-check` wrapper that runs Bazel drift checks for all tracked generated outputs. Split global include surfaces into explicit subsystem libraries during Bazel modeling instead of preserving `BuddyHeaders` as a catch-all. Treat any shell/Python generation script without rerun safety and check mode as unfinished infrastructure.

**Warning signs:**
Bazel rules use `genrule` with undeclared host tools; actions depend on files outside declared inputs; generated headers are modified by manual scripts after Bazel build; CMake remains the only path that can create `.bbf`, `.dfu`, resources, or puppy artifacts; Bazel target names mirror old global targets without ownership boundaries.

**Phase to address:**
Phase 2: Bazel/Rust Toolchain and Artifact Parity.

______________________________________________________________________

### Pitfall 4: Rust+Bazel Cross-Compilation Selects The Wrong World

**What goes wrong:**
The firmware links with the wrong linker, wrong target triple, wrong panic strategy, wrong Rust core/alloc artifacts, wrong C ABI flags, wrong linker script, wrong memory sections, or wrong platform constraints. The build may pass for a host test or a generic ARM target while producing unusable firmware for STM32F4, STM32G0, puppy boards, or xBuddy Extension variants.

**Why it happens:**
Bazel distinguishes execution platforms from target platforms, and rules_rust toolchains require explicit target triples, Rust std/core artifacts, linkers, and platform-compatible configuration. Rust target support differs by tier; many embedded targets are `no_std` only. Mixed Rust/C/C++/ASM builds also need consistent C toolchain, linker script, startup object, object-copy, map-file, and symbol behavior.

**How to avoid:**
Create explicit Bazel platforms for every board/MCU/printer artifact combination and use them from day one. Define Rust and C/C++ toolchains together, including linker, linker script, objcopy, strip/debug info, panic strategy, LTO policy, target JSON if needed, and FFI ABI assumptions. Add build tests that inspect ELF sections, map files, vector table placement, memory budgets, exported symbols, binary sizes, and artifact metadata. Host tests must use separate host platforms so they cannot accidentally prove target firmware behavior.

**Warning signs:**
`--platforms` is optional for firmware builds; host tests and firmware use the same target labels without platform distinction; `select()` still depends on legacy CPU flags; Rust crates compile with `std` on host but are not tested for `no_std`; link failures are fixed by broad flags rather than toolchain ownership.

**Phase to address:**
Phase 2: Bazel/Rust Toolchain and Artifact Parity.

______________________________________________________________________

### Pitfall 5: Retained Vendor Code Is Neither Owned Nor Replaced

**What goes wrong:**
Marlin, STM32 HAL/CMSIS, FreeRTOS, mbedTLS, LwIP, FatFs/littlefs, TinyUSB, WUI, TMCStepper, Prusa error codes, MMU firmware, puppy firmware, and other vendored code remain in the build, but the roadmap treats the firmware as "rewritten in Rust." Unsafe FFI and adapter behavior becomes ambiguous, upstream versions are unclear, and long-lived C/C++ islands block later safety and parity audits.

**Why it happens:**
The user explicitly scoped out rewriting vendor/upstream components before their boundary is understood. In a Big Bang rewrite, retained foreign code is a practical necessity, but it becomes a pitfall when the project fails to distinguish retained reference code, retained vendor code, generated code, and newly authored Rust. The current `lib/` tree is large and manually integrated without active root submodules.

**How to avoid:**
Create a retained-code inventory in Phase 3 with one row per C/C++/ASM/vendor island: upstream source/version, license, reason retained, Rust boundary, unsafe/FFI invariants, tests, update procedure, and replacement decision. Encapsulate each retained island behind a thin adapter and keep domain decisions in Rust types/state machines. For Marlin-derived behavior, decide whether the Rust rewrite reimplements it or retains specific components temporarily; do not leave "Marlin compatibility" implicit.

**Warning signs:**
The roadmap says "Rust firmware" while `lib/` objects still provide major behavior; bindgen output is reviewed as implementation instead of boundary glue; upstream versions are not recorded; unsafe calls lack preconditions; C/C++ global state is reachable from Rust domain logic; retained code is justified as "temporary" without an exit or ownership phase.

**Phase to address:**
Phase 3: Hardware Abstraction and Retained Vendor Boundary.

______________________________________________________________________

### Pitfall 6: Parity Tests Are Too Narrow For A Big Bang Cutover

**What goes wrong:**
The project has many tests, but they do not cover enough production behavior to justify replacing firmware. Existing C++ Catch2 tests, pytest simulator tests, block-device tests, generated automata tests, and Python binding tests cover useful slices; however, disabled Connect module tests, missing coverage thresholds, network/TLS edge gaps, transfer media races, probe analysis regression gaps, and generated-file drift gaps remain.

**Why it happens:**
Big Bang migration raises the bar for test sufficiency. Tests that were adequate for incremental C++ changes are not enough to prove a full firmware replacement. It is tempting to port unit tests to Rust and call that parity, but many firmware risks only appear through simulator, hardware, packaging, generated assets, and network conditions.

**How to avoid:**
Define a parity test pyramid before subsystem work starts: pure Rust unit tests for domain logic, adapter contract tests for retained code, golden tests against C/C++ reference fixtures, simulator integration tests, network/TLS tests, generated drift tests, release artifact checks, and hardware matrix tests. Re-enable or replace the stale Connect module integration coverage. For known fragile areas, add targeted tests first: transfer media races, transfer monitor lock ordering, custom DER certificate loading, probe analysis thresholds, persistent-store hash migration, and GUI flash-action failure paths.

**Warning signs:**
Most new tests are host-only; simulator tests are postponed until cutover; disabled legacy tests stay disabled without replacement; no negative/failure fixtures exist; generated files are checked by pre-commit only; hardware tests are described but not automated or scheduled.

**Phase to address:**
Phase 1: Reference Baseline and Safety Envelope; Phase 6: Release Qualification, Hardware Matrix, and Cutover.

______________________________________________________________________

### Pitfall 7: Bootloader, Resource, And Release Artifacts Do Not Match The Contract

**What goes wrong:**
The Rust firmware works when flashed directly but fails release, bootloader, resource bootstrap, puppy firmware bundling, DFU generation, signing, map/archive expectations, or field-update compatibility. `.bin`, `.bbf`, `.dfu`, littlefs resources, ESP blobs, WUI assets, translation/font assets, puppy firmware images, bootloader descriptors, and release metadata can silently diverge from the established release format.

**Why it happens:**
The current packaging contract is spread across root CMake rules, `utils/build.py`, `utils/pack_fw.py`, `cmake/Littlefs.cmake`, resource CMake files, puppy `ExternalProject_Add` flows, and bootloader/update logic in firmware. Bazel Primary Now means these contracts must move early, but artifact behavior is easy to under-specify if the team focuses on compiling Rust code first.

**How to avoid:**
Create an artifact parity phase gate in Phase 2. For each supported printer/board/bootloader mode, generate the C/C++ reference artifact and the Rust/Bazel artifact, then compare required metadata, section layout, resource contents, checksums, descriptors, file names, signing inputs, and update behavior. Use byte-for-byte comparison where the format is expected to match and semantic comparison where timestamps or compiler output legitimately differ. Add bootloader/simulator/hardware update tests before cutover.

**Warning signs:**
Firmware is only tested via debug flash; release packaging stays in CMake; puppies or ESP resources are omitted from early Bazel targets; artifact names change casually; signing is tested only manually; map files and section budgets are not checked in CI.

**Phase to address:**
Phase 2: Bazel/Rust Toolchain and Artifact Parity; Phase 6: Release Qualification, Hardware Matrix, and Cutover.

______________________________________________________________________

### Pitfall 8: Network And TLS Regressions Escape Host Tests

**What goes wrong:**
Prusa Connect, PrusaLink/WUI, transfers, proxy support, TLS verification, custom certificate provisioning, WebSocket commands, telemetry/events, registration, DNS/SNTP, metrics/syslog, and download behavior regress. The most dangerous failures are not simple connection failures: accepting weak/incorrect certificates, parsing uninitialized or short-lived certificate buffers, breaking token/fingerprint headers, changing timeout behavior during prints, or corrupting files during ranged/encrypted downloads.

**Why it happens:**
The current code already has a broken custom DER certificate path, legacy digest modules compiled into TLS config, CPU/memory-sensitive TLS handshakes, fixed whole-response buffers, disabled/stale Connect module integration tests, and transfer stack constraints. mbedTLS `parse_der_nocopy` deliberately trades memory for stronger buffer lifetime requirements, which must be represented explicitly in Rust if retained.

**How to avoid:**
Make network/TLS a dedicated parity and security workstream, not a late integration task. Build a deterministic host test server suite for Connect registration, telemetry, events, WebSocket commands, proxy tunnel handoff, downloads, invalid/missing/valid custom DER files, weak/legacy cert rejection, expired certs, wrong hostnames, network stalls, and large responses. Keep TLS certificate buffers owned for the required lifetime or use copying APIs with measured memory budget. Add handshake latency and memory telemetry under UI/network load.

**Warning signs:**
TLS tests only check success against one server; custom CA is marked done without invalid/missing/valid fixtures; proxy behavior has no tests; command execution is verified without duplicate/long command cases; Connect buffers grow without memory measurement; RNG and certificate policies are not part of code review.

**Phase to address:**
Phase 5: UI, Network, Transfers, and Generated Assets; Phase 6: Release Qualification, Hardware Matrix, and Cutover.

______________________________________________________________________

### Pitfall 9: Persistent Configuration Compatibility Is Broken Or Over-Preserved

**What goes wrong:**
Existing printers lose settings, credentials, calibration state, PrusaLink/Connect identity, MMU state, or migration history after flashing Rust firmware. The opposite failure is also possible: Rust preserves collision-sensitive hashed IDs and deprecated fields mechanically, carrying insecure or confusing storage behavior forward without a decision.

**Why it happens:**
The current config store uses typed items, migrations, deprecated hash IDs, generated journal hashes, and direct EEPROM writes. The concerns map identifies collision sensitivity, migration-heavy behavior, visible credential storage without encryption-at-rest, and crash dump handling that can include sensitive memory. A rewrite can easily change layouts while believing that typed Rust structs are inherently safer.

**How to avoid:**
Treat persistent storage as a compatibility protocol. Freeze the current schema, generated hashes, deprecated ID behavior, migrations, default values, import/export settings keys, credential fields, and crash-dump policy before rewriting. Add migration tests from real reference EEPROM/internal-storage fixtures to Rust fixtures. Use Rust newtypes and constructors for validated config values, but keep wire/storage compatibility explicit. Make any security change, such as credential scrubbing or encryption, a named compatibility decision with rollback behavior.

**Warning signs:**
Rust structs are generated from current config without golden migration fixtures; deprecated items are removed because they look unused; hash generation is not in Bazel drift checks; credential and crash-dump regions are not reviewed; settings import/export behavior is tested only through default config.

**Phase to address:**
Phase 4: Core Domain Parity; Phase 6: Release Qualification, Hardware Matrix, and Cutover.

______________________________________________________________________

### Pitfall 10: Known Bugs Are Accidentally Fossilized

**What goes wrong:**
The rewrite copies known defects because behavior parity is interpreted as preserving every observable bug, or it silently fixes defects without updating thresholds, fixtures, UI messages, or external behavior. Both outcomes are risky: fossilized bugs waste the rewrite, while untracked fixes look like regressions.

**Why it happens:**
The concerns map includes bugs and fragile areas that interact with behavior: custom TLS DER parsing never reads bytes, probe variance uses wrong mean but classifier thresholds depend on it, home screen can freeze after flash action failure, partial transfer progress is disabled due to AsyncIO stack overflow, block-device tests can pick an out-of-range block, MMU availability is stubbed true, and Connect duplicate command behavior is unresolved.

**How to avoid:**
Create a "parity exception ledger" in Phase 1. Each known bug gets one of three statuses: preserve until cutover with a test, fix during rewrite with new expected behavior, or defer with an explicit risk owner. For defects coupled to thresholds or external behavior, such as probe analysis, update fixtures and thresholds together. For safety/security defects, prefer fixing during rewrite, but document the changed behavior and verify it through regression tests.

**Warning signs:**
Bug names appear only in notes; no tests assert old or new behavior; developers disagree whether a mismatch is a bug fix or regression; thresholds change without fixture provenance; TODO stubs are ported as `todo!()` or unconditional success.

**Phase to address:**
Phase 1: Reference Baseline and Safety Envelope; subsystem fix phases as assigned by the ledger.

______________________________________________________________________

### Pitfall 11: RTOS And Concurrency Semantics Drift

**What goes wrong:**
The printer boots and runs, but task readiness, lock ordering, queue ownership, stack usage, buffer lifetimes, background command execution, and filesystem/media races differ from the reference. Symptoms include deadlocks, dropped Marlin events, GUI stalls, Connect duplicate command confusion, transfer corruption, missing progress, watchdog resets, or failures that only appear under network plus UI plus print load.

**Why it happens:**
The existing architecture relies on FreeRTOS tasks, `TaskDeps`, static storage, single server/client request patterns, fixed GUI storage, transfer monitor lock rules, and shared buffers. Rust abstractions can make ownership cleaner, but if they obscure blocking behavior, priority, stack use, or ISR/task boundaries, they can change timing-sensitive firmware semantics.

**How to avoid:**
Model every cross-task protocol as a state machine with explicit ownership and blocking rules. Add tests for startup dependency order, Marlin request/event serialization, transfer monitor lock misuse, duplicate Connect commands, long G-code lines, USB/media unplug/replug, delete/recreate races, and queue saturation. Measure stack high-water marks and heap/static memory use under stress. Keep "snapshot" APIs instead of lock-holding public objects wherever possible.

**Warning signs:**
Lock-order comments from C++ disappear without replacement tests; channels/queues are introduced without capacity rationale; stack sizes are guessed; `async` or RTOS wrappers hide blocking operations; direct-sector writes are treated as ordinary file writes; transfer/media tests remain unit-only.

**Phase to address:**
Phase 4: Core Domain Parity; Phase 5: UI, Network, Transfers, and Generated Assets.

______________________________________________________________________

### Pitfall 12: Scope Pressure Turns Big Bang Into An Unqualified Cutover

**What goes wrong:**
The roadmap reaches a point where most code is Rust and Bazel builds artifacts, but unresolved safety, hardware, release, generated-file, vendor, and parity gaps remain. Because incremental production migration is out of scope, there is no safe partial deployment path; the team either delays indefinitely or ships under-qualified firmware.

**Why it happens:**
Big Bang migration concentrates integration risk at the end. If phases are organized by implementation convenience instead of acceptance gates, the final phase becomes a pile of unresolved cross-cutting work: hardware matrix, release artifacts, Connect, bootloader, persistent migrations, resources, and known defects.

**How to avoid:**
Structure the roadmap around gates, not subsystems alone. Each phase must retire specific classes of risk and leave behind executable evidence. The final cutover phase should be qualification only, not first discovery of missing artifact or safety work. Maintain a running cutover checklist from Phase 1 and block phase completion when parity evidence is absent.

**Warning signs:**
"Cutover validation" contains first-time work; artifact parity, hardware safety, or network/TLS tests are deferred to the last phase; phases close with manual signoff only; retained vendor boundaries are unknown; new feature work appears before parity gates pass.

**Phase to address:**
All phases; especially Phase 6: Release Qualification, Hardware Matrix, and Cutover.

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Port CMake option macros directly into Bazel globals | Fast first build | Recreates global target coupling and feature leakage | Only as a short-lived compatibility target with an exit date |
| Keep `BuddyHeaders`-style include reachability in Bazel | Fewer initial build errors | Subsystem ownership remains invisible; wrong board/feature dependencies compile accidentally | Never for new Rust or Bazel-owned code |
| Leave generated files as manually regenerated tracked outputs | Avoids rewriting generators early | Presets, logging docs, fonts, translations, resource hashes, and struct visitors drift | Only if paired with a Bazel drift check before phase completion |
| Treat CMake as the release oracle indefinitely | Reduces early Bazel packaging work | Bazel Primary Now is not achieved; release parity is discovered late | Only for Phase 1 reference capture |
| Wrap vendor C APIs with broad unsafe Rust modules | Fast FFI progress | Unsafe preconditions spread across the codebase | Never; unsafe belongs in small adapter capsules |
| Preserve known defects for parity without a ledger | Avoids hard behavioral decisions | Bugs become permanent or fixes look like regressions | Only when explicitly marked "preserve until cutover" with tests |
| Keep disabled or stale tests as "future work" | Saves migration time | Parity evidence is weaker than the old codebase's risk profile | Never for safety, network/TLS, storage, transfer, or release paths |
| Use host Rust tests as proof of embedded behavior | Fast feedback | `std`, allocator, timing, stack, linker, and hardware assumptions go untested | Acceptable only for pure domain logic |
| Add new printer features during parity work | Demonstrates progress | Obscures whether Rust matches reference behavior | Never until replacement cutover passes |

## Integration Gotchas

Common mistakes when connecting to external services and firmware-adjacent systems.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Prusa Connect | Test only registration/telemetry happy path | Cover registration, token/fingerprint headers, events, WebSocket commands, duplicate commands, long G-code, proxy, reconnect, and timeout behavior |
| PrusaLink/WUI | Preserve HTTP routes but change auth, API error shapes, or file semantics | Golden-test API responses, digest/API-key behavior, transfer endpoints, static assets, and storage routes |
| TLS/custom CA | Use `parse_der_nocopy` without stable buffer ownership or test only built-in certs | Own certificate buffers for CRT lifetime or use copying parser; test missing, invalid, valid, weak, expired, and wrong-host certificates |
| Transfers/downloads | Treat direct-sector partial file writes as ordinary file writes | Preserve media identity, lock lifetime, range/encryption behavior, non-contiguous rejection, and unplug/delete/recreate tests |
| Persistent config | Rename/remove deprecated store items because Rust has cleaner structs | Treat config as a compatibility protocol with generated hash drift checks and migration fixtures |
| Bootloader/release | Verify direct debug flash but not `.bbf`/`.dfu`/resource update | Add artifact metadata, section, resource, descriptor, signing, and bootloader update tests |
| Puppies/MMU | Retain stubs or unconditional availability during Rust port | Model availability and bootloader/runtime states as explicit enums with tests |
| GUI/localization | Port screens but skip generated fonts/translations and failure flows | Test display resolutions, resource/font generation, translations, error dialogs, flash action failure, and event-disabled recovery |
| Metrics/syslog/crash dumps | Keep diagnostics behavior without privacy review | Preserve useful telemetry while documenting credential/memory scrubbing and upload policy |

## Performance Traps

Patterns that work at small scale but fail under real firmware load.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| TLS handshake CPU/memory pressure | Connect misses timing, UI stutters, allocations fail | Measure handshake latency and memory under UI/network/print load; keep buffers scoped and reuse safely | Under reconnects, proxy, high UI load, or constrained LwIP pools |
| Whole-response Connect buffers | Larger responses fail or force bigger shared buffers | Add incremental parsing and response size tests | When Connect commands or metadata exceed legacy assumptions |
| LwIP one-packet workaround copied forever | Low throughput and hidden TCP behavior differences | Reproduce packet-order issue, then either keep as explicit policy or fix with regression tests | During downloads, telemetry bursts, or remote print control |
| Transfer direct-sector writes | File corruption or stalled transfers after media changes | Validate media identity, file contiguity, lock lifetime, and USB queue behavior | USB unplug/replug, delete/recreate, or concurrent access |
| Generated font/resource headers stay source-heavy | Slow builds, noisy reviews, stale assets | Move generation under Bazel with drift checks; consider binary assets where release-compatible | Translation/resource updates and full matrix builds |
| Rust allocation appears harmless on host | Firmware heap/stack exhaustion | Keep `no_std` target tests, explicit alloc policy, stack watermarks, and panic behavior checks | Under embedded target and RTOS task load |
| Logging/telemetry in constrained tasks | Stack overflow, dropped progress, watchdog resets | Measure task stacks and move verbose formatting to safe contexts | Transfer progress, TLS, and diagnostic bursts |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Custom CA parser does not read/own DER bytes correctly | Certificate validation fails or parses invalid memory | Fix before porting; test file read, parse, lifetime, invalid DER, and valid DER |
| Retaining MD5/SHA1 modules without policy | Future certificate paths may accept weak legacy signatures | Disable unused legacy digests or explicitly reject weak signatures after compatibility review |
| Generic RNG fallback used for security | Deterministic output can reach security-sensitive code | Keep cryptographic entropy APIs distinct and fail closed on hardware RNG failure |
| Network secrets stored without reviewed at-rest policy | Physical access or crash dumps can expose credentials | Document physical-access assumptions; scrub diagnostics; consider credential-specific erase/encryption if hardware allows |
| Crash dump upload over plain socket HTTP | Sensitive RAM can leave device without TLS | Keep upload disabled until TLS, consent, and scrubbing exist |
| Fixture keys/certs enter release artifacts | Test credentials could be confused with production material | Quarantine fixtures and add packaging exclusions |
| Signing key path handled casually in Bazel | Release key leakage or unsigned artifacts | Keep signing key external, model signing inputs explicitly, and test unsigned/signed artifact workflows |
| Proxy/network behavior accepted without auth/TLS review | Unexpected traffic path or downgrade behavior | Test proxy tunnel, certificate verification after tunnel, and document unsupported proxy auth |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Same mechanical print result but different prompts/errors | Users and support cannot follow existing workflows | Golden-test screen text, dialog order, error codes, and support-visible states |
| GUI event-disabled paths freeze | Printer appears stuck even if firmware continues | Replace event disable/reenable with typed action result states and recovery tests |
| Transfer progress remains hidden | Users think upload/download is stalled | Emit progress from a task with safe stack budget or use compact telemetry |
| MMU availability always "true" | Users see impossible maintenance or print options | Model disabled, unavailable, bootloader, stopped, and active MMU states |
| Translation/font generation drifts | Missing glyphs, wrong labels, inconsistent UI | Put translations and fonts under Bazel generation and visual/simulator checks |
| PrusaLink/Connect credentials change behavior | Users lose connection or cannot authenticate | Preserve import/export keys, display flows, token behavior, and migration fixtures |
| Boot/update flow differs from release firmware | Users cannot update or recover normally | Test bootloader update, resource bootstrap, and release package install paths before cutover |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Rust firmware build:** Often missing board/printer/platform matrix - verify every supported board, MCU, bootloader mode, and feature option in Bazel.
- [ ] **Bazel primary:** Often missing artifact ownership - verify `.bin`, `.bbf`, `.dfu`, map files, resources, puppy images, and generated assets are produced by Bazel.
- [ ] **Behavior parity:** Often missing failure scenarios - verify G-code, planner, thermal, pause/resume, selftest, probe, GUI, Connect, transfers, and config migrations against reference fixtures.
- [ ] **Hardware safety:** Often missing failure injection - verify safe outputs, watchdog, panic/fault, IRQ, heater, motor, fan, endstop, and probe failure paths.
- [ ] **Generated files:** Often missing drift checks - verify fonts, translations, logging docs, options, struct visitors, resource hashes, and presets through one `just`/Bazel command.
- [ ] **Vendor boundary:** Often missing inventory - verify every retained C/C++/ASM/vendor component has owner, version, rationale, unsafe boundary, and tests.
- [ ] **TLS/network:** Often missing negative tests - verify custom CA, invalid certs, weak certs, wrong hostnames, proxy, timeouts, WebSocket commands, and large responses.
- [ ] **Persistent storage:** Often missing real migration fixtures - verify existing EEPROM/internal data upgrades without losing settings or credentials.
- [ ] **Release artifacts:** Often missing bootloader install proof - verify update/install path, signing inputs, descriptors, resource bootstrap, and rollback/recovery behavior.
- [ ] **Known concerns:** Often missing disposition - verify each item in `.planning/codebase/CONCERNS.md` is fixed, preserved with test, or explicitly deferred.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Behavior drift discovered late | HIGH | Rebuild reference fixtures, classify as bug fix or regression, add parity test, then adjust Rust behavior or documented compatibility exception |
| Hardware safety mismatch | HIGH | Freeze affected board release path, reproduce on simulator/HIL, inspect adapter/unsafe boundary, add failure test, and rerun hardware matrix |
| Bazel non-hermetic output | MEDIUM | Identify undeclared input/tool, move generator into Bazel, add check mode, and compare clean-machine/CI outputs |
| Wrong cross toolchain/linker | HIGH | Stop firmware builds, define explicit platform/toolchain constraints, inspect ELF/map/vector table, and add regression build tests |
| Retained vendor ambiguity | MEDIUM | Inventory retained code, isolate adapter, document upstream/version/license, and add boundary contract tests |
| Insufficient parity tests | HIGH | Do not proceed to cutover; create missing test class first, starting with safety, artifact, storage, network, and transfer gaps |
| Bootloader/package mismatch | HIGH | Compare reference package metadata, restore release contract in Bazel, test update path, then rerun full artifact matrix |
| TLS regression | HIGH | Disable affected custom/network path, add deterministic TLS fixture tests, fix parser/lifetime/policy, and verify under memory/timing load |
| Persistent config breakage | HIGH | Stop migration rollout, restore from reference fixtures, add migration rollback/compat tests, and document changed storage policy |
| Generated asset drift | MEDIUM | Regenerate through Bazel, add source markers/check targets, and block phase completion on drift |
| Concurrency deadlock or stack overflow | HIGH | Capture task/stack evidence, reduce lock-holding API surface, add stress/failure tests, and measure high-water marks |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Behavior drift | Phase 1: Reference Baseline and Safety Envelope | Golden/reference fixtures for every behavior class; mismatch ledger reviewed each phase |
| Hardware safety changes | Phase 1 and Phase 3 | Safe-state tests, IRQ/pin/linker reviews, hardware-in-loop failure cases, panic/fault path proof |
| Hidden generated-file drift | Phase 2 | Bazel generator targets plus `just generated-check`; clean checkout drift check passes |
| Bazel/Rust cross-compilation traps | Phase 2 | Explicit platforms/toolchains; firmware ELF/map/vector/section checks for each board |
| Retained vendor code ambiguity | Phase 3 | Retained-code inventory with owner, version, license, unsafe invariants, tests, and replacement decision |
| Parity test insufficiency | Phase 1 and Phase 6 | Test pyramid accepted before implementation; final cutover has no first-time test categories |
| Bootloader/release artifact mismatch | Phase 2 and Phase 6 | Reference vs Rust artifact metadata comparison plus bootloader/update install proof |
| Network/TLS regressions | Phase 5 and Phase 6 | Deterministic Connect/WUI/TLS/proxy/download suite with negative cert and timeout fixtures |
| Persistent config incompatibility | Phase 4 and Phase 6 | Golden EEPROM/internal fixtures, hash drift checks, migration tests, credential/crash-dump review |
| Known codebase concerns reintroduced | Phase 1 plus owning subsystem phase | Every concern has "fix", "preserve with test", or "defer with owner" status |
| RTOS/concurrency drift | Phase 4 and Phase 5 | State-machine tests, lock misuse tests, queue capacity rationale, stack high-water evidence |
| Unqualified Big Bang cutover | Phase 6 | Cutover checklist contains only final qualification, not unresolved implementation work |

Recommended phase structure:

1. **Reference Baseline and Safety Envelope** - freeze behavior evidence, safety invariants, known-bug ledger, and cutover checklist before rewriting.
1. **Bazel/Rust Toolchain and Artifact Parity** - make Bazel authoritative for target platforms, generators, resources, and release outputs before subsystem code grows.
1. **Hardware Abstraction and Retained Vendor Boundary** - isolate unsafe, HAL, RTOS, Marlin/vendor, FFI, and board-specific contracts.
1. **Core Domain Parity** - rebuild G-code, planner-facing state, thermal/probe/selftest, persistent config, MMU, and safety-state logic with typed Rust invariants.
1. **UI, Network, Transfers, and Generated Assets** - rebuild GUI, Connect, WUI, TLS, transfers, localization, resources, and diagnostics with parity and stress coverage.
1. **Release Qualification, Hardware Matrix, and Cutover** - run final simulator/hardware/artifact/security/storage qualification; no first-time implementation belongs here.

## Sources

- `.planning/PROJECT.md` - project constraints: Big Bang, behavior parity, Bazel primary, retained vendor boundary, known concern priorities. Confidence: HIGH.
- `.planning/codebase/CONCERNS.md` - known bugs, security risks, generated drift, fragile transfer/network/config areas, test gaps. Confidence: HIGH.
- `.planning/codebase/TESTING.md` - existing Catch2, pytest, simulator, block-device, disabled Connect module, CI/pre-commit verification surfaces. Confidence: HIGH.
- `.planning/codebase/ARCHITECTURE.md` - current firmware layers, FreeRTOS task flows, Marlin bridge, GUI, Connect, persistent stores, resources, puppy firmware, packaging. Confidence: HIGH.
- `.planning/codebase/INTEGRATIONS.md` - Connect, PrusaLink/WUI, TLS, downloads, storage, auth, diagnostics, CI/deployment integrations. Confidence: HIGH.
- Bright Builds architecture standard, pinned commit: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md - functional core, parse at boundaries, illegal states. Confidence: HIGH.
- Bright Builds testing standard, pinned commit: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md - pure/business logic unit testing and Arrange/Act/Assert. Confidence: HIGH.
- Bright Builds verification standard, pinned commit: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/verification.md - repo-native verification and generated/script checks. Confidence: HIGH.
- Bright Builds Rust standard, pinned commit: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md - Rust module structure, guard extraction, optional naming, newtypes/enums. Confidence: HIGH.
- Rust Embedded Book, `no_std`: https://doc.rust-lang.org/stable/embedded-book/intro/no-std.html - bare-metal Rust lacks `std` runtime and uses `core`. Confidence: HIGH.
- Rust Reference, unsafe keyword: https://doc.rust-lang.org/reference/unsafe-keyword.html - `unsafe` defines or discharges safety obligations. Confidence: HIGH.
- rustc platform support: https://doc.rust-lang.org/rustc/platform-support.html - target tiers and `no_std` target distinctions. Confidence: HIGH.
- Bazel hermeticity: https://bazel.build/basics/hermeticity - builds should isolate tools and declared inputs from host machine drift. Confidence: HIGH.
- Bazel toolchains: https://bazel.build/extending/toolchains - toolchain resolution decouples rule logic from platform-based tool selection. Confidence: HIGH.
- Bazel platforms migration: https://bazel.build/concepts/platforms - explicit platforms, toolchain existence, `select()` and transition migration pitfalls. Confidence: HIGH.
- rules_rust toolchains: https://bazelbuild.github.io/rules_rust/rust_toolchains.html - Rust toolchain attributes, target triples, linkers, target JSON, and exec/target behavior. Confidence: HIGH.
- Mbed TLS X.509 API docs: https://mbed-tls.readthedocs.io/projects/api/en/v2.28.9/api/file/x509\_\_crt_8h/ - `mbedtls_x509_crt_parse_der_nocopy` buffer lifetime requirement. Confidence: HIGH.
- FreeRTOS stack usage and stack overflow checking: https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/09-Memory-management/02-Stack-usage-and-stack-overflow-checking - stack overflow checking is configured through `configCHECK_FOR_STACK_OVERFLOW`. Confidence: MEDIUM, official page content was discoverable but dynamic rendering limited extraction.
- FreeRTOS `uxTaskGetStackHighWaterMark`: https://www.freertos.org/Documentation/02-Kernel/04-API-references/03-Task-utilities/04-uxTaskGetStackHighWaterMark - high-water mark API for stack margin measurement. Confidence: MEDIUM, official page content was discoverable but dynamic rendering limited extraction.

______________________________________________________________________

*Pitfalls research for: Big Bang Rust+Bazel rewrite of safety-relevant embedded 3D printer firmware*
*Researched: 2026-06-02*
