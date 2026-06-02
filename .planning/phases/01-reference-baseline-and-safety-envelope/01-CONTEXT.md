---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 1-2026-06-02T15-50-10
generated_at: 2026-06-02T15:50:10.638Z
---

# Phase 1: Reference Baseline and Safety Envelope - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning
**Mode:** Yolo

<domain>

## Phase Boundary

Phase 1 establishes the reference oracle for the Rust+Bazel rewrite before implementation can drift. It should produce inspectable baseline artifacts for the supported product matrix, current reference-capture surfaces, known-defect disposition, and board-aware safety envelope. It should not begin the Rust port, make Bazel authoritative, or fix subsystem defects except where a tiny supporting change is required to make the baseline capture artifact truthful and rerunnable.

</domain>

<decisions>

## Implementation Decisions

### Baseline Matrix

- **D-01:** Derive the supported printer, board, MCU, bootloader, feature, and artifact matrix from existing reference sources instead of maintaining a freehand table. Treat `ProjectOptions.cmake`, `utils/presets/presets.json`, `CMakePresets.json`, `CMakeLists.txt`, and `utils/build.py` as the first pass source set.
- **D-02:** Record both the human-readable matrix and the exact source paths/commands used to generate or validate it. If a value cannot be mechanically derived yet, mark it as `manual-evidence-needed` with the owning source path rather than guessing.
- **D-03:** Keep CMake/Python as the behavior reference in this phase. Bazel can be mentioned as the future authority, but Phase 2 owns Bazel toolchain and developer facade work.

### Reference Capture

- **D-04:** Define reference-capture targets as current-firmware oracle captures for builds, generated assets, protocol traces, simulator flows, storage migrations, and release artifacts. The capture contract should name command, inputs, outputs, expected location, and whether the output is committed, ignored, or CI-only.
- **D-05:** Prefer small repo-owned scripts or `just`-ready command descriptions that call the current existing tools rather than re-implementing build or generator logic. Avoid hidden shell snippets in documentation when a checked script is clearer.
- **D-06:** Capture output directories should be explicitly gitignored or documented as ephemeral unless the plan intentionally adds a tracked fixture.

### Concern Ledger

- **D-07:** Seed the intentional-delta ledger from `.planning/codebase/CONCERNS.md`. Every listed known bug, fragile area, security consideration, tech-debt item, and scaling limit should receive one disposition: `preserve-temporarily`, `fix-during-rewrite`, or `defer`.
- **D-08:** Do not silently fix known defects in Phase 1. If a defect is fixed during the rewrite later, the fix must be tied to a requirement/phase and parity evidence so maintainers can distinguish intentional deltas from accidental behavior changes.
- **D-09:** Concern entries should include the affected files, current behavior, risk, planned disposition, target phase when known, and verification evidence expected before cutover.

### Safety Envelope

- **D-10:** The safety envelope must be board-aware and failure-mode oriented. Cover startup, watchdogs, safe output states, thermal behavior, motion safe states, endstops/probes/loadcell, fans, power panic, crash dumps, redscreen/BSOD/assert handling, emergency stop, firmware update paths, and auxiliary-controller safety where applicable.
- **D-11:** Classify each safety item by required evidence type: `source-audit`, `host-test`, `simulator-flow`, `hardware-smoke`, or `manual-hardware-required`. Missing hardware should be recorded as a pending evidence class, not treated as pass.
- **D-12:** Keep secrets out of safety and baseline artifacts. Mention credential-bearing areas by config key/path only, and do not copy keys, tokens, certificates, crash-dump bytes, or private signing material.

### Verification Strategy

- **D-13:** Phase 1 verification should prove the baseline artifacts exist, are internally traceable to BASE-01 through BASE-04, and are generated or checked through documented commands where practical.
- **D-14:** Automated verification can be limited to artifact existence, schema/format checks, source-reference checks, and lightweight command smoke checks. Firmware builds, simulator traces, and hardware smoke checks may be documented as reference-capture commands if they are too heavy or hardware-bound for this phase.
- **D-15:** The plan should explicitly preserve the Big Bang, Behavior Parity, Bazel Primary Now, `justfile`, and Bright Builds constraints from project context.

### the agent's Discretion

The agent may choose the exact artifact names, document layout, and validation script boundaries as long as the outputs are easy for maintainers and downstream agents to inspect. Prefer narrow, auditable artifacts under `.planning/` plus lightweight repo commands over broad rewrites or large generated blobs.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project And Roadmap

- `.planning/PROJECT.md` - Project constraints, migration posture, compatibility bar, and Bright Builds standards.
- `.planning/REQUIREMENTS.md` - BASE-01 through BASE-04 and full v1 traceability.
- `.planning/ROADMAP.md` - Phase 1 goal, success criteria, dependencies, and phase sequencing.
- `.planning/STATE.md` - Current phase state and pending concerns.
- `AGENTS.md` - Repo-local GSD and Bright Builds instructions.
- `AGENTS.bright-builds.md` - Pinned Bright Builds sidecar and workflow requirements.
- `standards-overrides.md` - Active local standards exceptions; currently no real override.

### Current Build And Product Matrix Sources

- `ProjectOptions.cmake` - Printer, board, MCU, bootloader, and feature option definitions.
- `utils/presets/presets.json` - Source data for generated CMake presets.
- `CMakePresets.json` - Generated preset surface that maintainers currently see.
- `CMakeLists.txt` - Firmware target graph, package outputs, generated headers, and release artifact wiring.
- `utils/build.py` - Current high-level build, preset generation, DFU/package, and product staging wrapper.
- `.pre-commit-config.yaml` - Current generated-file and formatting hook ownership.
- `cmake/Utilities.cmake` - Firmware packaging and build utility behavior.
- `cmake/Littlefs.cmake` - LittleFS/resource image generation behavior.

### Codebase Maps And Known Concerns

- `.planning/codebase/STACK.md` - Current language, runtime, framework, and dependency map.
- `.planning/codebase/ARCHITECTURE.md` - Current CMake/firmware architecture and subsystem layering.
- `.planning/codebase/CONVENTIONS.md` - Local naming, formatting, generated-file, and error-handling conventions.
- `.planning/codebase/TESTING.md` - Current C++/pytest test organization and run commands.
- `.planning/codebase/INTEGRATIONS.md` - Network, storage, auth, TLS, CI, and external integration surfaces.
- `.planning/codebase/CONCERNS.md` - Seed source for the intentional-delta and fragile-area ledger.

### Safety-Critical Reference Surfaces

- `src/buddy/main.cpp` - Master-board runtime initialization and FreeRTOS task orchestration.
- `src/common/appmain.cpp` - Application runtime entry and printing orchestration boundary.
- `src/common/marlin_server.cpp` - Buddy/Marlin bridge and print control behavior.
- `src/common/Pin.cpp` - GPIO/interrupt safety-sensitive behavior and STM32G0 concern.
- `src/common/probe_analysis.cpp` - Probe classification concern and coupled thresholds.
- `src/common/crash_dump/dump.cpp` - Crash dump memory collection behavior.
- `src/common/crash_dump/crash_dump_distribute.cpp` - Crash dump upload behavior.
- `src/gui/screen_home.cpp` - Home-screen flash/freeze concern and crash dump warning surface.
- `src/connect/tls/tls.cpp` - TLS/custom certificate behavior and certificate parsing concern.
- `src/persistent_stores/store_instances/config_store/store_definition.hpp` - Persistent config keys, credentials, feature flags, and migration-sensitive storage.
- `src/persistent_stores/store_instances/config_store/migrations.cpp` - Config migration behavior.
- `src/transfers/partial_file.cpp` - Transfer partial-file and media safety concerns.
- `include/buddy/lwipopts.h` - Network stack constraints and throughput workaround.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `utils/build.py` already centralizes product build, preset, DFU, and package behavior; Phase 1 should reference or wrap it instead of recreating product logic.
- `utils/presets/presets.json` and `CMakePresets.json` provide a practical matrix seed for supported build surfaces.
- `.planning/codebase/*.md` already contains curated architecture, integration, testing, and concern evidence that can seed maintainable baseline artifacts.
- `.pre-commit-config.yaml` shows existing generated-file ownership and can inform drift-check decisions.

### Established Patterns

- Generated files are tracked only when existing tooling owns regeneration; new generated baseline outputs need clear ownership and ignored output locations.
- Current verification is split between CMake/Catch2 unit tests, pytest simulator/integration tests, Python tooling checks, pre-commit hooks, and Jenkins/Holly CI.
- Heavy hardware and simulator evidence is real but not always locally runnable; record commands and evidence classes separately from pass/fail claims.

### Integration Points

- Baseline artifacts should connect BASE-01 through BASE-04 to current source paths and future phase gates.
- Reference-capture commands should prepare Phase 2 and Phase 3 without making Bazel authoritative early.
- Concern dispositions should feed later subsystem phases, especially Rust architecture, foreign-code boundaries, printing safety, persistence/resources, network services, and auxiliary controllers.

</code_context>

<specifics>

## Specific Ideas

- Treat Phase 1 as a guardrail phase: it should make later drift visible before the Rust implementation begins.
- Use explicit statuses like `captured`, `manual-evidence-needed`, `ci-only`, `hardware-required`, and `deferred` rather than vague prose.
- Keep matrix and safety artifacts inspectable by maintainers who are comparing current C/C++ behavior against future Rust+Bazel behavior.

</specifics>

<deferred>

## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 01-reference-baseline-and-safety-envelope*
*Context gathered: 2026-06-02*
