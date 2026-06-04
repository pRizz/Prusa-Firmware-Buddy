---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 6-2026-06-04T09-48-48
generated_at: 2026-06-04T09:48:48.542Z
---

# Phase 6: Printing Core, Safety, and Feature Gates - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning
**Mode:** Yolo

<domain>

## Phase Boundary

Phase 6 preserves reference printing, safety, recovery, and printer-specific feature-gate behavior in the Rust+Bazel firmware. It should model and verify G-code routing, serial/file printing, planner-visible operations, thermal and motion safety states, selftest/calibration/recovery flows, fatal/error boundaries, and supported feature combinations.

This phase must not claim persistence/resource compatibility, GUI workflow parity, network service parity, or auxiliary-controller behavior parity beyond the feature-gate facts needed by printing and safety decisions. Those behaviors remain Phase 7 through Phase 10 work.

</domain>

<decisions>

## Implementation Decisions

### Printing Behavior Parity

- **D-01:** Treat the retained Marlin/Buddy printing stack as the reference oracle for Phase 6. G-code parsing/routing, serial printing, file printing, pause/resume/cancel, planner-visible state, and Buddy-specific G/M-code handlers must be captured as fixtures or explicit reference contracts before Rust behavior is accepted.
- **D-02:** Add Rust domain models for print job state, command routing, pause/resume/cancel transitions, planner-visible flow state, and behavior fixture identities. The models should reject impossible transitions early instead of copying sentinel-heavy C/C++ state.
- **D-03:** Keep the first implementation focused on parity contracts and typed policy surfaces. Do not rewrite the full Marlin motion planner in this phase unless a plan can prove a narrow, fixture-backed slice with low regression risk.

### Safety And Recovery Gates

- **D-04:** Model safety-critical thermal, motion, selftest, calibration, crash detection, power panic, emergency stop, safe-output, redscreen/BSOD/assert, watchdog, and recovery behavior as named Rust policy surfaces with evidence classes.
- **D-05:** Separate locally testable pure safety decisions from hardware, RTOS, HAL, and retained fatal-path effects. Host Rust tests may prove state transitions and fixture classification; simulator, hardware-smoke, or manual-hardware-required evidence remains non-local and must not be described as locally passed.
- **D-06:** Fatal and recovery flows must preserve Phase 5 panic/watchdog/crash-dump boundary contracts. New code should not allocate or hide errors in fatal paths unless the retained reference behavior and safety envelope explicitly allow it.

### Feature Gate Matrix

- **D-07:** Derive printer feature gates from existing reference sources and Phase 1/5 evidence, not from freehand duplication. The model should cover filament sensors, TMC paths, precise homing, input shaper, phase/burst stepping, loadcell/HX717, beds, chamber, door, MMU2, NFC, LEDs, toolchanger, and xBuddy Extension gate facts.
- **D-08:** Encode feature availability as typed Rust data keyed by validated product profiles. Impossible or unsupported printer/board/feature combinations should fail at construction or verification time.
- **D-09:** Only gate facts needed for Phase 6 printing and safety are in scope. Auxiliary behavior implementation, Modbus protocol behavior, MMU runtime parity, and toolchanger/puppy behavior parity remain Phase 10 unless a printing safety gate needs a narrow reference fixture now.

### Known Concern Dispositions

- **D-10:** The Phase 6 plan must connect known printing and safety concerns to fixtures or intentional-delta entries. Probe-analysis classification coupling, home-screen flash/freeze side effects that affect print starts, MMU hard-coded availability/reporting, TMC/motion driver retention, and fatal/crash dump handling must not be silently changed.
- **D-11:** If the Rust rewrite fixes a known reference defect, the plan must name it as an intentional delta, tie it to a requirement, and add regression evidence. Otherwise the parity fixture should preserve the current behavior until a later approved fix.

### Verification Strategy

- **D-12:** Add a Phase 6 verifier exposed through Bazel and `just`, following the Phase 4 and Phase 5 pattern. It should check required artifacts, schema coverage, Rust API shape, feature-gate coverage, concern dispositions, Bazel/just labels, and relevant Rust checks.
- **D-13:** Verification should include focused Rust unit tests for pure state machines and gate policies with explicit Arrange/Act/Assert structure. Heavy C++ firmware builds, simulator flows, and hardware smoke checks may be documented as required non-local evidence when they cannot run locally.
- **D-14:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 6-2026-06-04T09-48-48`.

### the agent's Discretion

The agent may choose exact module names, manifest schemas, verifier implementation details, and fixture file layouts. Prefer minimal standard-library tooling, explicit manifests, and small pure Rust policy modules over broad rewrites. If a behavior cannot be proven locally, classify the evidence honestly instead of weakening the parity bar.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project, Standards, And Workflow

- `.planning/PROJECT.md` - Big Bang Rust+Bazel posture, behavior parity bar, current project decisions, and Phase 6 handoff.
- `.planning/REQUIREMENTS.md` - CORE-03, CORE-04, CORE-05, VERF-01, VERF-03, and cross-phase traceability.
- `.planning/ROADMAP.md` - Phase 6 goal, success criteria, dependency on Phase 5, and later phase boundaries.
- `.planning/STATE.md` - Current focus and residual Phase 6 concerns.
- `AGENTS.md` - Repo-local GSD, Bright Builds, Rust, verification, and generated-file instructions.
- `AGENTS.bright-builds.md` - Pinned Bright Builds sidecar and sync/verification requirements.
- `standards-overrides.md` - Local standards exceptions; no active real override.

### Prior Phase Evidence

- `.planning/phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md` - Supported printer, board, MCU, feature, artifact, and safety surfaces.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md` - Startup, watchdog, thermal, motion, crash, emergency, update, and auxiliary safety evidence classes.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md` - Known defects and fragile-area dispositions that Phase 6 must preserve or explicitly change.
- `.planning/phases/02-bazel-authority-and-developer-facade/02-CONTEXT.md` - Bazel authority, workflow targets, and `justfile` decisions.
- `.planning/phases/03-artifact-and-generator-parity/03-CONTEXT.md` - Artifact/generator boundary decisions that Phase 6 must not overclaim.
- `.planning/phases/04-rust-architecture-and-invariant-model/04-CONTEXT.md` - Rust workspace and invariant-model decisions that Phase 6 extends.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-CONTEXT.md` - Runtime boundary and retained-code decisions that Phase 6 must use.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md` - Retained Marlin, TMC, MMU, crash, filesystem, and auxiliary surfaces.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-UNSAFE-BOUNDARY-AUDIT.md` - Panic, watchdog, crash-dump, FreeRTOS, MMIO, DMA, interrupt, and startup evidence classes.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-VERIFICATION.md` - Passed Phase 5 boundary evidence and non-local hardware/scheduler deferrals.

### Current Rust And Bazel Surface

- `Cargo.toml` - Rust workspace membership, edition, rust-version, and workspace lint policy.
- `rust/crates/domain/src/lib.rs` - Pure domain crate and current invariant boundary.
- `rust/crates/domain/src/product.rs` - Validated product profile and supported matrix modeling.
- `rust/crates/domain/src/feature.rs` - Current feature set modeling to extend for Phase 6 gates.
- `rust/crates/application/src/lib.rs` - Pure application policy crate pattern.
- `rust/crates/board-adapter/src/lib.rs` - Board adapter boundary over validated profiles.
- `rust/crates/runtime-adapter/src/lib.rs` - Runtime adapter boundary over startup, task, panic, watchdog, and synchronization contracts.
- `tools/bazel/BUILD.bazel` - Existing Bazel workflow labels to extend with Phase 6 checks.
- `tools/bazel/rust_workflow.sh` - Existing Bazel-to-Cargo Rust workflow runner.
- `tools/bazel/phase5_verify.py` - Pattern for phase verifier structure and aggregate checks.
- `justfile` - Developer-facing workflow facade to extend with Phase 6 verification.

### Printing, Safety, And Feature Reference Sources

- `lib/Marlin/` - Retained Marlin printing core and planner/motion/thermal reference behavior.
- `lib/AddMarlin.cmake` - Marlin source selection and feature/board integration.
- `src/common/appmain.cpp` - Application runtime and Marlin server loop entry boundary.
- `src/common/marlin_server.cpp` - Buddy/Marlin bridge, print control, and server-side state.
- `src/common/marlin_client.cpp` - Task-local client request and event surface.
- `src/common/marlin_server_request.hpp` - Request flags and command contract.
- `src/common/marlin_client_queue.hpp` - Client event queue contract.
- `src/common/marlin_vars.cpp` - Shared Marlin variable snapshot behavior.
- `src/marlin_stubs/` - Buddy-specific G/M-code handlers and Marlin configuration stubs.
- `src/common/probe_analysis.cpp` - Probe-analysis bug and classifier-threshold coupling.
- `src/common/crash_dump/dump.cpp` - Crash dump memory collection behavior.
- `src/common/crash_dump/crash_dump_distribute.cpp` - Crash dump upload and retention-sensitive behavior.
- `src/common/Pin.cpp` - GPIO/interrupt behavior and STM32G0 already-enabled IRQ concern.
- `src/common/feature/` - Feature-scoped printing and safety-adjacent application modules.
- `src/feature/` - Higher-level feature slices with G-code and setup/calibration behavior.
- `src/hw/` - Hardware components above raw MCU HAL and below application features.
- `lib/TMCStepper/` and `lib/AddTMCStepper.cmake` - Trinamic motion driver reference surface.
- `src/mmu2/` and `lib/AddMMU2.cmake` - MMU gate and runtime reference surface.
- `ProjectOptions.cmake` - Printer, board, MCU, and feature option source.
- `utils/presets/presets.json` - Supported preset source data.
- `.planning/codebase/STRUCTURE.md` - Directory and runtime entrypoint map.
- `.planning/codebase/CONCERNS.md` - Printing, safety, MMU, TLS, transfer, probe, and fatal-path concerns.
- `.planning/codebase/TESTING.md` - Current C++/pytest/Rust test surfaces and run commands.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- Phase 4 created `buddy-domain` and `buddy-application` as pure Rust policy surfaces; Phase 6 can extend this pattern for print state, command routing, safety policy, and feature gates.
- Phase 5 created `buddy-board-adapter` and `buddy-runtime-adapter` boundary crates; Phase 6 should consume those contracts instead of reaching directly into HAL, RTOS, panic, watchdog, or retained startup surfaces.
- `tools/bazel/phase5_verify.py`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` provide the established pattern for phase-local verification exposed through Bazel and `just`.
- Phase 1 safety envelope and concern ledger already identify the evidence classes and defect dispositions that Phase 6 should connect to printing and safety fixtures.

### Established Patterns

- Pure Rust logic should stay in domain/application crates, use typed constructors, avoid impossible states, and include focused unit tests.
- Retained firmware behavior should be referenced through explicit source paths, manifests, fixtures, or verifier rows rather than implicit broad globs.
- Hardware, simulator, and scheduler evidence must be classified as non-local until actually run; local checks can prove schema, source coverage, Rust API shape, and host-test behavior only.

### Integration Points

- `rust/crates/domain/src/feature.rs` is the natural extension point for typed feature-gate facts.
- New print/safety policy code should live in pure Rust crates first, with board/runtime adapters providing only boundary facts.
- `tools/bazel/BUILD.bazel` and `justfile` should gain Phase 6 labels/recipes so developers can run aggregate checks consistently.
- Current Marlin/Buddy C++ sources remain the behavior oracle for fixtures and intentional-delta decisions.

</code_context>

<specifics>

## Specific Ideas

- Create a machine-readable Phase 6 manifest for reference printing fixtures, safety gates, feature gates, and known concern dispositions.
- Add small Rust state-machine modules for print job transitions, command routing class, safety action classification, and feature-gate construction.
- Add a verifier that fails when CORE-03, CORE-04, or CORE-05 has no artifact coverage, when concern dispositions are missing, or when local artifacts overclaim hardware evidence.
- Keep Phase 6 honest about scope: typed gate facts for MMU2, xBuddy Extension, and toolchanger may be needed here, but behavior parity for those ecosystems remains Phase 10.

</specifics>

<deferred>

## Deferred Ideas

- Persistent config, storage migrations, filesystems, credentials, and resource compatibility remain Phase 7.
- GUI workflow and display behavior parity remain Phase 8.
- Connect, PrusaLink/WUI, transfers, TLS, telemetry, and local network services remain Phase 9.
- Auxiliary controller, MMU runtime, Modbus, toolchanger, puppy update, and expansion ecosystem behavior parity remain Phase 10 except for feature-gate facts needed by Phase 6.
- Full cutover evidence, simulator parity pyramid, release metadata comparison, and hardware smoke gates remain Phase 11.

</deferred>

---

*Phase: 06-printing-core-safety-and-feature-gates*
*Context gathered: 2026-06-04*
