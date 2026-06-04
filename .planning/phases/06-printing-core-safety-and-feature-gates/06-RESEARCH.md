---
generated_by: gsd-phase-researcher
lifecycle_mode: yolo
phase_lifecycle_id: 6-2026-06-04T09-48-48
generated_at: 2026-06-04T09:58:24Z
---

# Phase 6: Printing Core, Safety, and Feature Gates - Research

**Researched:** 2026-06-04 [VERIFIED: current_date]
**Domain:** Rust domain models, retained Marlin/Buddy printing oracle, safety policy surfaces, feature-gate verification [VERIFIED: .planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md]
**Confidence:** HIGH for local source and verifier shape; MEDIUM for simulator/hardware evidence availability [VERIFIED: local source audit + environment probe]

<user_constraints>

## User Constraints (from CONTEXT.md)

All bullets in this section are copied verbatim from `.planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md`. [VERIFIED: .planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md]

### Locked Decisions

#### Printing Behavior Parity

- **D-01:** Treat the retained Marlin/Buddy printing stack as the reference oracle for Phase 6. G-code parsing/routing, serial printing, file printing, pause/resume/cancel, planner-visible state, and Buddy-specific G/M-code handlers must be captured as fixtures or explicit reference contracts before Rust behavior is accepted.
- **D-02:** Add Rust domain models for print job state, command routing, pause/resume/cancel transitions, planner-visible flow state, and behavior fixture identities. The models should reject impossible transitions early instead of copying sentinel-heavy C/C++ state.
- **D-03:** Keep the first implementation focused on parity contracts and typed policy surfaces. Do not rewrite the full Marlin motion planner in this phase unless a plan can prove a narrow, fixture-backed slice with low regression risk.

#### Safety And Recovery Gates

- **D-04:** Model safety-critical thermal, motion, selftest, calibration, crash detection, power panic, emergency stop, safe-output, redscreen/BSOD/assert, watchdog, and recovery behavior as named Rust policy surfaces with evidence classes.
- **D-05:** Separate locally testable pure safety decisions from hardware, RTOS, HAL, and retained fatal-path effects. Host Rust tests may prove state transitions and fixture classification; simulator, hardware-smoke, or manual-hardware-required evidence remains non-local and must not be described as locally passed.
- **D-06:** Fatal and recovery flows must preserve Phase 5 panic/watchdog/crash-dump boundary contracts. New code should not allocate or hide errors in fatal paths unless the retained reference behavior and safety envelope explicitly allow it.

#### Feature Gate Matrix

- **D-07:** Derive printer feature gates from existing reference sources and Phase 1/5 evidence, not from freehand duplication. The model should cover filament sensors, TMC paths, precise homing, input shaper, phase/burst stepping, loadcell/HX717, beds, chamber, door, MMU2, NFC, LEDs, toolchanger, and xBuddy Extension gate facts.
- **D-08:** Encode feature availability as typed Rust data keyed by validated product profiles. Impossible or unsupported printer/board/feature combinations should fail at construction or verification time.
- **D-09:** Only gate facts needed for Phase 6 printing and safety are in scope. Auxiliary behavior implementation, Modbus protocol behavior, MMU runtime parity, and toolchanger/puppy behavior parity remain Phase 10 unless a printing safety gate needs a narrow reference fixture now.

#### Known Concern Dispositions

- **D-10:** The Phase 6 plan must connect known printing and safety concerns to fixtures or intentional-delta entries. Probe-analysis classification coupling, home-screen flash/freeze side effects that affect print starts, MMU hard-coded availability/reporting, TMC/motion driver retention, and fatal/crash dump handling must not be silently changed.
- **D-11:** If the Rust rewrite fixes a known reference defect, the plan must name it as an intentional delta, tie it to a requirement, and add regression evidence. Otherwise the parity fixture should preserve the current behavior until a later approved fix.

#### Verification Strategy

- **D-12:** Add a Phase 6 verifier exposed through Bazel and `just`, following the Phase 4 and Phase 5 pattern. It should check required artifacts, schema coverage, Rust API shape, feature-gate coverage, concern dispositions, Bazel/just labels, and relevant Rust checks.
- **D-13:** Verification should include focused Rust unit tests for pure state machines and gate policies with explicit Arrange/Act/Assert structure. Heavy C++ firmware builds, simulator flows, and hardware smoke checks may be documented as required non-local evidence when they cannot run locally.
- **D-14:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 6-2026-06-04T09-48-48`.

### the agent's Discretion

The agent may choose exact module names, manifest schemas, verifier implementation details, and fixture file layouts. Prefer minimal standard-library tooling, explicit manifests, and small pure Rust policy modules over broad rewrites. If a behavior cannot be proven locally, classify the evidence honestly instead of weakening the parity bar.

### Deferred Ideas (OUT OF SCOPE)

- Persistent config, storage migrations, filesystems, credentials, and resource compatibility remain Phase 7.
- GUI workflow and display behavior parity remain Phase 8.
- Connect, PrusaLink/WUI, transfers, TLS, telemetry, and local network services remain Phase 9.
- Auxiliary controller, MMU runtime, Modbus, toolchanger, puppy update, and expansion ecosystem behavior parity remain Phase 10 except for feature-gate facts needed by Phase 6.
- Full cutover evidence, simulator parity pyramid, release metadata comparison, and hardware smoke gates remain Phase 11.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CORE-03 | Preserve printing core behavior for G-code parsing/routing, motion/planner-visible operations, thermal transitions, pause/resume/cancel, serial/file printing, Buddy-specific G/M-code handlers. [VERIFIED: .planning/REQUIREMENTS.md] | Use retained `lib/Marlin/`, `src/common/marlin_server*`, `src/common/serial_printing*`, `src/common/gcode/`, and `src/marlin_stubs/` as fixture or contract sources; model pure Rust print state and command-routing decisions only. [VERIFIED: local source audit] |
| CORE-04 | Preserve safety-critical thermal, motion, selftest, calibration, crash detection, power panic, emergency stop, safe-output, redscreen/BSOD/assert, recovery. [VERIFIED: .planning/REQUIREMENTS.md] | Use named safety policy surfaces with evidence classes from Phase 1/5; keep hardware, RTOS, HAL, watchdog, and fatal-path effects as non-local evidence unless actually run. [VERIFIED: 01-SAFETY-ENVELOPE.md + 05-UNSAFE-BOUNDARY-AUDIT.md] |
| CORE-05 | Preserve printer-specific feature gates including filament sensors, TMC paths, precise homing, input shaper, phase/burst stepping, loadcell/HX717, beds, chamber, door, MMU2, NFC, LEDs, toolchanger, xBuddy Extension. [VERIFIED: .planning/REQUIREMENTS.md] | Derive typed gate facts from `ProjectOptions.cmake`, `utils/presets/presets.json`, `lib/AddMarlin.cmake`, and current `ProductProfile`/`FeatureSet` Rust models. [VERIFIED: local source audit] |

</phase_requirements>

## Summary

Phase 6 should extend the existing pure Rust domain/application pattern, not the board or runtime adapters. The current Rust workspace already has `buddy-domain` for invariant types, `buddy-application` for pure policies, and adapter crates for runtime/board boundaries; Phase 6 should add print state, command-route, safety policy, feature-gate, fixture identity, and evidence-class types in the pure crates first. [VERIFIED: Cargo.toml + rust/crates/domain/src/lib.rs + rust/crates/application/src/lib.rs + rust/crates/board-adapter/src/lib.rs + rust/crates/runtime-adapter/src/lib.rs]

The retained C/C++ firmware remains the oracle. `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, `src/common/marlin_server_request.hpp`, `src/common/serial_printing.cpp`, `src/common/gcode/`, `src/marlin_stubs/`, `lib/Marlin/`, `lib/TMCStepper/`, and `lib/libbgcode/` provide the reference behavior and fixture sources for CORE-03; safety sources in `src/common/safe_state.cpp`, `src/common/feature/safety_timer/`, `src/common/power_panic*`, `src/common/crash_dump/`, `src/common/feature/emergency_stop/`, `src/common/selftest/`, and `src/common/probe_analysis.cpp` provide CORE-04 reference surfaces. [VERIFIED: local source audit]

**Primary recommendation:** Implement Phase 6 as typed Rust policy surfaces plus machine-readable manifests and a stdlib Python verifier wired through Bazel and `just`; do not rewrite Marlin motion, TMC drivers, MMU runtime, GUI, networking, persistence, or auxiliary behavior in this phase. [VERIFIED: 06-CONTEXT.md + tools/bazel/phase5_verify.py + justfile]

## Project Constraints (from AGENTS.md)

- Read repo-local instructions and Bright Builds sidecar before planning or implementation; `AGENTS.md`, `AGENTS.bright-builds.md`, and `standards-overrides.md` were present and read. [VERIFIED: AGENTS.md + AGENTS.bright-builds.md + standards-overrides.md]
- The local `standards/` directory was not present, so standards references named by `AGENTS.md` are available through the Bright Builds sidecar instructions rather than local checked-in pages. [VERIFIED: file existence probe]
- No repo-local `.claude/skills/` or `.agents/skills/` directory exists, so no project skill rules add Phase 6 constraints. [VERIFIED: file existence probe]
- Follow functional-core / imperative-shell structure: pure decision logic belongs in Rust domain/application modules, while effects stay behind board/runtime/reference boundaries. [VERIFIED: AGENTS.bright-builds.md]
- Parse boundary data into domain types and make invalid states unrepresentable where practical. [VERIFIED: AGENTS.bright-builds.md]
- Keep unit tests focused on one concern and use clear Arrange/Act/Assert structure for new pure Rust tests. [VERIFIED: AGENTS.md + AGENTS.bright-builds.md]
- Rust workspace lint forbids unsafe code, and Phase 5 already isolated runtime/board unsafe boundary concerns; Phase 6 pure modules should remain unsafe-free. [VERIFIED: Cargo.toml + 05-UNSAFE-BOUNDARY-AUDIT.md]
- Do not add dependencies unless maintenance status and necessity justify them; Phase 6 can use Rust stdlib and Python stdlib for the verifier. [VERIFIED: AGENTS.md + tools/bazel/phase5_verify.py]
- Before any later commit in this Rust project, run `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`; this research artifact does not create a code commit. [VERIFIED: AGENTS.md]
- Generated or managed files must be changed through their owning generator or avoided; Phase 6 should add new manifest/verifier files rather than hand-edit generated outputs. [VERIFIED: AGENTS.md + .planning/codebase/CONVENTIONS.md]

## Standard Stack

### Core

| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| Rust workspace `buddy-domain` and `buddy-application` | edition 2024, rust-version 1.85; local `rustc 1.91.1` [VERIFIED: Cargo.toml + environment probe] | Pure print state, command-route, safety policy, feature-gate, and evidence-class models [VERIFIED: 04-CONTEXT.md + rust/crates/domain/src/lib.rs] | Existing Phase 4 pattern already encodes product/profile invariants in Rust and rejects unsupported combinations early. [VERIFIED: rust/crates/domain/src/product.rs] |
| Retained Marlin/Buddy C++ reference sources | repo-local retained source [VERIFIED: 05-FOREIGN-CODE-INVENTORY.md] | Oracle for G-code, print state, planner-visible operations, thermal/safety, and Buddy-specific G/M-code behavior [VERIFIED: 06-CONTEXT.md + local source audit] | User locked retained Marlin/Buddy stack as Phase 6 reference oracle. [VERIFIED: 06-CONTEXT.md] |
| Bazel `shell_binary` + `tools/bazel/rust_workflow.sh` | local Bazel `9.1.1`; script dispatch present [VERIFIED: environment probe + tools/bazel/rust_workflow.sh] | Expose `phase6_verify` and Rust checks through the authoritative build facade [VERIFIED: tools/bazel/BUILD.bazel + justfile] | Phase 4/5 already use this pattern for aggregate Rust verifier targets. [VERIFIED: tools/bazel/BUILD.bazel] |
| Python stdlib verifier | local Python `3.14.4` [VERIFIED: environment probe] | Validate manifests, source coverage, API shape, evidence classes, lifecycle ID, Bazel/just labels, and overclaim strings [VERIFIED: tools/bazel/phase5_verify.py] | Phase 5 verifier uses stdlib `argparse`, `json`, `pathlib`, `subprocess`, and explicit schema checks without new dependencies. [VERIFIED: tools/bazel/phase5_verify.py] |

### Supporting

| Library/Tool | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| Catch2 C++ tests | vendored under `lib/Catch2/` [VERIFIED: .planning/codebase/TESTING.md] | Reference host tests for existing parser/reader/probe pieces [VERIFIED: tests/unit/common/gcode/parser/gcode_basic_parser_tests.cpp + tests/unit/common/gcode/reader/gcode_reader.cpp] | Use as evidence references, not as the main Phase 6 local verifier unless the plan intentionally adds C++ fixture extraction. [VERIFIED: 06-CONTEXT.md] |
| pytest simulator tests | `pytest` listed in requirements, missing from current shell [VERIFIED: .planning/codebase/TESTING.md + environment probe] | Non-local or separately bootstrapped safety simulator evidence [VERIFIED: tests/integration/test_safety.py] | Use only when a plan installs/bootstraps requirements and has firmware/simulator inputs; otherwise record as `simulator-flow` required evidence. [VERIFIED: 06-CONTEXT.md + environment probe] |
| Phase 1/5 planning artifacts | committed markdown/manifests [VERIFIED: find .planning/phases] | Baseline matrix, safety envelope, concern ledger, retained-code inventory, unsafe-boundary audit [VERIFIED: 01-BASELINE-MATRIX.md + 01-SAFETY-ENVELOPE.md + 05-FOREIGN-CODE-INVENTORY.md] | Use in `phase6_verify.py` to require concern dispositions and prevent hardware overclaims. [VERIFIED: tools/bazel/phase5_verify.py pattern] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Rust pure policy modules | Rewrite Marlin motion/planner now | Rejected for Phase 6 because D-03 limits this phase to parity contracts and typed policy surfaces unless a narrow fixture-backed slice is proven low risk. [VERIFIED: 06-CONTEXT.md] |
| Python stdlib verifier | Add a JSON schema or validation dependency | Rejected for Phase 6 because Phase 5 already proves stdlib checks are sufficient and AGENTS.md prefers minimal dependencies. [VERIFIED: tools/bazel/phase5_verify.py + AGENTS.md] |
| Derive gates from `ProjectOptions.cmake` and presets | Freehand Rust feature matrix | Rejected because D-07 requires deriving gates from reference sources and Phase 1/5 evidence. [VERIFIED: 06-CONTEXT.md] |
| Evidence classes with non-local markers | Claim hardware/simulator behavior from host tests | Rejected because D-05 and Phase 5 verification explicitly separate local checks from simulator/hardware/manual evidence. [VERIFIED: 06-CONTEXT.md + 05-VERIFICATION.md] |

**Installation:** No new packages should be installed for Phase 6 planning or the local verifier. [VERIFIED: tool audit + AGENTS.md]

```bash
# No npm, cargo, or Python dependency additions are required for the recommended Phase 6 verifier.
```

**Version verification:** `npm view` is not applicable because Phase 6 should not add npm packages. Local tool versions were verified with shell probes: Python 3.14.4, cargo 1.91.1, rustc 1.91.1, rustfmt 1.8.0-stable, clippy 0.1.91, Bazel 9.1.1, just 1.48.0, CMake 3.27.9, Ninja 1.13.2; `pytest` is missing from the current shell. [VERIFIED: environment probe]

## Architecture Patterns

### Recommended Project Structure

```text
rust/crates/domain/src/
|-- print.rs                 # typed print job state, command route, fixture IDs [RECOMMENDED: 06-CONTEXT.md]
|-- safety.rs                # pure safety policy surfaces and evidence classes [RECOMMENDED: 06-CONTEXT.md]
|-- feature.rs               # extend existing feature facts for Phase 6 gates [VERIFIED: rust/crates/domain/src/feature.rs]
`-- product.rs               # keep validated profile construction as the feature-gate key [VERIFIED: rust/crates/domain/src/product.rs]

rust/crates/application/src/
`-- printing.rs              # pure application policy helpers when domain-only code becomes too broad [RECOMMENDED: 04-CONTEXT.md]

tools/bazel/
|-- phase6_verify.py         # stdlib schema/source/API/lifecycle verifier [RECOMMENDED: tools/bazel/phase5_verify.py]
`-- manifests/
    |-- phase6_printing_core.json
    |-- phase6_safety_gates.json
    |-- phase6_feature_gates.json
    `-- phase6_concern_dispositions.json
```

### Pattern 1: Typed Print State Model

**What:** Model only the pure state and command-route decisions that Phase 6 can verify locally; keep actual queueing, planner motion, media prefetch, heatup, and host action side effects as retained reference contracts. [VERIFIED: 06-CONTEXT.md + src/common/marlin_server.cpp]

**When to use:** Use for start, serial start, pause, resume, abort, exit, media recovery, and fixture identity validation before any adapter or retained C/C++ call is made. [VERIFIED: src/common/marlin_server.cpp + src/common/marlin_client.cpp]

**Example:**

```rust
// Source pattern: typed constructors and invariant errors in rust/crates/domain/src/product.rs [VERIFIED]
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PrintState {
    Idle,
    Preview,
    Printing(PrintSource),
    Pausing,
    Paused,
    Resuming,
    Aborting,
    Finished,
    PowerPanicAwaitingResume,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PrintCommand {
    StartFile(FixtureId),
    StartSerial,
    Pause,
    Resume,
    Abort,
    Exit,
    RecoverMediaError,
}

pub fn transition(state: PrintState, command: PrintCommand) -> Result<PrintState, PrintError> {
    match (state, command) {
        (PrintState::Idle, PrintCommand::StartFile(fixture)) => {
            Ok(PrintState::Preview)
        }
        (PrintState::Idle, PrintCommand::StartSerial) => {
            Ok(PrintState::Printing(PrintSource::Serial))
        }
        (PrintState::Printing(source), PrintCommand::Pause) => {
            Ok(PrintState::Pausing)
        }
        (PrintState::Paused, PrintCommand::Resume) => {
            Ok(PrintState::Resuming)
        }
        (PrintState::Printing(_), PrintCommand::Abort)
        | (PrintState::Paused, PrintCommand::Abort)
        | (PrintState::Resuming, PrintCommand::Abort) => {
            Ok(PrintState::Aborting)
        }
        (state, command) => Err(PrintError::UnsupportedTransition { state, command }),
    }
}
```

### Pattern 2: Manifest-Backed Reference Fixtures

**What:** Store Phase 6 references as explicit JSON rows with `id`, `requirement`, `source_paths`, `reference_behavior`, `evidence_class`, `rust_surface`, and `intentional_delta` fields. [RECOMMENDED: tools/bazel/phase5_verify.py pattern]

**When to use:** Use for every CORE-03/04/05 row, every known concern disposition, and every feature gate that the Rust model claims to represent. [VERIFIED: 06-CONTEXT.md]

**Verifier checks:** Require top-level `schema_version`, `phase`, lifecycle id, row IDs, allowed evidence classes, existing source paths, requirement coverage, no missing concern IDs, and no hardware-overclaim strings. [VERIFIED: tools/bazel/phase5_verify.py]

### Pattern 3: Feature Gates Derived From Product Profiles

**What:** Extend `Feature`/`FeatureSet` with Phase 6 gate facts while keeping `ProductProfile::new(...)` as the construction boundary for printer, board, MCU, bootloader, and feature compatibility. [VERIFIED: rust/crates/domain/src/product.rs + rust/crates/domain/src/feature.rs]

**When to use:** Use for filament sensor kind, TMC paths, precise homing, input shaper, phase/burst stepping, loadcell/HX717, bed/chamber/door/NFC/LED/toolchanger/MMU/xBuddy Extension facts. [VERIFIED: ProjectOptions.cmake]

**Key detail:** `ProjectOptions.cmake` already separates master-board gates from auxiliary boards through `BOARD_IS_MASTER_BOARD` and helper functions, so the Rust gate model must preserve master-vs-auxiliary distinctions instead of treating printer name alone as sufficient. [VERIFIED: ProjectOptions.cmake]

### Anti-Patterns to Avoid

- **Planner rewrite inside Phase 6:** The retained Marlin planner and motion stack are the reference oracle, and D-03 rejects a broad rewrite in this phase. [VERIFIED: 06-CONTEXT.md]
- **One flat feature enum with no source provenance:** CORE-05 gates come from CMake options, presets, Marlin source inclusion, and Phase 1 evidence; verifier rows need source paths for each gate group. [VERIFIED: ProjectOptions.cmake + utils/presets/presets.json + 01-BASELINE-MATRIX.md]
- **Hardware claims from Rust unit tests:** Host Rust tests can prove pure transition logic, not thermal/motion hardware safety. [VERIFIED: 06-CONTEXT.md + 05-VERIFICATION.md]
- **Silent reference-defect fixes:** Probe classifier, MMU availability, home-screen print-start side effects, TMC retention, and crash dump handling require fixture or intentional-delta rows. [VERIFIED: 06-CONTEXT.md + .planning/codebase/CONCERNS.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Motion planner parity | A new Rust planner implementation | Retained `lib/Marlin/` contracts and narrow fixture-backed policies | D-03 keeps full planner rewrite out of scope. [VERIFIED: 06-CONTEXT.md] |
| G-code file decoding | A new `.gcode`/`.bgcode` reader | Existing `src/common/gcode/` and `lib/libbgcode/` reference fixtures | Existing tests cover plain, binary, meatpack, heatshrink, CRC failure, and stream restore behavior. [VERIFIED: tests/unit/common/gcode/reader/gcode_reader.cpp] |
| G/M-code dispatch inventory | A freehand command list | `src/marlin_stubs/gcode.cpp` and `src/marlin_stubs/` | Buddy-specific command behavior is spread across stub files and conditional includes. [VERIFIED: local source audit] |
| Feature matrix | Hand-maintained Rust-only truth | `ProjectOptions.cmake`, `utils/presets/presets.json`, `lib/AddMarlin.cmake`, and Phase 1 matrix | The CMake graph controls actual compiled feature availability today. [VERIFIED: ProjectOptions.cmake + lib/AddMarlin.cmake] |
| TMC/motion drivers | New driver logic | `lib/TMCStepper/` and `lib/AddTMCStepper.cmake` as retained reference | Phase 5 inventory marks TMC as safety-critical retained reference through Phase 6. [VERIFIED: 05-FOREIGN-CODE-INVENTORY.md] |
| Fatal, watchdog, crash dump effects | New fatal path behavior in pure policy code | Phase 5 runtime boundaries plus named evidence classes | Fatal/recovery flows must preserve panic/watchdog/crash-dump contracts. [VERIFIED: 06-CONTEXT.md + 05-UNSAFE-BOUNDARY-AUDIT.md] |
| Entropy or crypto behavior | A fallback RNG or crypto shim | Existing hardware RNG/TLS boundaries and later Phase 9 security work | `rand_u()` falls back to deterministic software RNG in production, and TLS has separate hardware entropy; Phase 6 should classify this concern, not invent crypto. [VERIFIED: src/common/random_hw.cpp + .planning/codebase/CONCERNS.md] |

**Key insight:** The hard part is not implementing algorithms; it is proving that every Rust policy claim has a retained reference source, evidence class, and phase-appropriate scope. [VERIFIED: 06-CONTEXT.md + Phase 1/5 artifacts]

## Common Pitfalls

### Pitfall 1: Local Tests Overclaim Hardware Safety

**What goes wrong:** A passing Rust transition test is described as proving thermal, watchdog, motion, or crash recovery behavior on hardware. [VERIFIED: 06-CONTEXT.md]
**Why it happens:** Phase 6 pure models are intentionally separated from RTOS, HAL, watchdog, and fatal effects. [VERIFIED: 05-UNSAFE-BOUNDARY-AUDIT.md]
**How to avoid:** Require `evidence_class` on every safety row and fail the verifier on hardware-overclaim strings. [VERIFIED: tools/bazel/phase5_verify.py]
**Warning signs:** Phrases like `hardware passed`, `hardware-safe`, or `locally passed hardware` in Phase 6 docs. [VERIFIED: tools/bazel/phase5_verify.py]

### Pitfall 2: Freehand Feature Gate Drift

**What goes wrong:** Rust accepts a profile/feature combination that CMake would not compile, or rejects one of the supported products. [VERIFIED: ProjectOptions.cmake + rust/crates/domain/src/product.rs]
**Why it happens:** Existing gates combine printer, board, master/auxiliary status, optional build flags, and Marlin source selection. [VERIFIED: ProjectOptions.cmake + lib/AddMarlin.cmake]
**How to avoid:** Build manifest rows from `ProjectOptions.cmake` groups and require verifier coverage for CORE-05 gate groups. [RECOMMENDED: local source audit]
**Warning signs:** Rust gate tests assert only printer names and ignore `BoardKind` or auxiliary bootloader mode. [VERIFIED: rust/crates/domain/src/product.rs]

### Pitfall 3: Serial and File Printing Collapse Into One Flow

**What goes wrong:** A Rust state model treats serial printing and file printing as identical. [VERIFIED: src/common/marlin_server.cpp + src/common/serial_printing.cpp]
**Why it happens:** Both reach `Printing`, but file printing uses media prefetch, preview, restore positions, and media error recovery; serial printing uses host action hooks and serial timeout behavior. [VERIFIED: src/common/marlin_server.cpp + src/common/serial_printing.cpp]
**How to avoid:** Model `PrintSource::File` and `PrintSource::Serial` separately and require fixtures for pause/resume/cancel differences. [RECOMMENDED: CORE-03]
**Warning signs:** No fixture row references `serial_print_start`, `SerialPrinting::pause`, `SerialPrinting::resume`, or media prefetch. [VERIFIED: src/common/serial_printing.cpp + src/common/marlin_server.cpp]

### Pitfall 4: Known Defects Are Fixed Accidentally

**What goes wrong:** The Rust rewrite changes probe classification, MMU availability reporting, crash dump behavior, or STM32G0 IRQ behavior without naming an intentional delta. [VERIFIED: 06-CONTEXT.md + .planning/codebase/CONCERNS.md]
**Why it happens:** Reference code contains known defects and temporary stubs that look obviously wrong. [VERIFIED: src/common/probe_analysis.cpp + src/mmu2/mmu2_reporting.cpp + src/common/Pin.cpp]
**How to avoid:** Add `phase6_concern_dispositions.json` and require rows for CL-007, CL-011, CL-014, CL-024, CL-002, and CL-008. [RECOMMENDED: 01-CONCERN-LEDGER.md + .planning/codebase/CONCERNS.md]
**Warning signs:** A code change says "cleanup" or "simplify" near those surfaces with no fixture or intentional-delta row. [RECOMMENDED: D-10/D-11]

## Code Examples

Verified patterns from existing sources and recommended Phase 6 shape:

### Strict Manifest Loader

```python
# Source pattern: tools/bazel/phase5_verify.py [VERIFIED]
def require_rows(data: dict[str, object], path: Path, collection_name: str) -> list[dict[str, object]]:
    if data.get("schema_version") != 1:
        raise VerificationError(f"{path} must set schema_version to 1")
    if data.get("phase") != "06-printing-core-safety-and-feature-gates":
        raise VerificationError(f"{path} has the wrong phase")
    if data.get("phase_lifecycle_id") != "6-2026-06-04T09-48-48":
        raise VerificationError(f"{path} has the wrong lifecycle id")

    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(f"{path} must contain {collection_name}")
    return [require_object(row, path, collection_name, index) for index, row in enumerate(rows)]
```

### Feature Gate Constructor

```rust
// Source pattern: ProductProfile::new rejects unsupported features [VERIFIED: rust/crates/domain/src/product.rs]
pub struct PrintFeatureGates {
    profile: ProductProfile,
    filament_sensor: FilamentSensorGate,
    motion: MotionGateSet,
    safety: SafetyGateSet,
}

impl PrintFeatureGates {
    pub fn new(
        profile: ProductProfile,
        filament_sensor: FilamentSensorGate,
        motion: MotionGateSet,
        safety: SafetyGateSet,
    ) -> Result<Self, InvariantError> {
        if !filament_sensor.is_supported_by(&profile) {
            return Err(InvariantError::UnsupportedFeature {
                printer: profile.printer(),
                board: profile.board(),
                feature: Feature::FilamentSensor,
            });
        }

        Ok(Self {
            profile,
            filament_sensor,
            motion,
            safety,
        })
    }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| C/C++ sentinel-heavy print states and request flags are the only behavior surface. [VERIFIED: src/common/marlin_server_types/marlin_server_state.h + src/common/marlin_server_request.hpp] | Rust typed policy models describe allowed transitions while retained C/C++ remains the oracle. [VERIFIED: 06-CONTEXT.md] | Phase 6 planning scope on 2026-06-04. [VERIFIED: 06-CONTEXT.md] | Planner should create small pure Rust modules plus fixtures, not a production planner rewrite. [RECOMMENDED: D-03] |
| Feature availability lives only in CMake options and source-selection logic. [VERIFIED: ProjectOptions.cmake + lib/AddMarlin.cmake] | Validated Rust product profiles already exist and should be extended with Phase 6 gate facts. [VERIFIED: rust/crates/domain/src/product.rs + rust/crates/domain/src/feature.rs] | Phase 4 introduced Rust invariant models; Phase 6 extends them. [VERIFIED: 04-CONTEXT.md + 06-CONTEXT.md] | Planner should derive gate data from reference sources and enforce impossible-combination rejection. [VERIFIED: D-07/D-08] |
| Safety evidence can be scattered across docs, C++ behavior, and manual hardware knowledge. [VERIFIED: 01-SAFETY-ENVELOPE.md] | Evidence classes are explicit and verifier-enforced through manifests. [VERIFIED: 05-UNSAFE-BOUNDARY-AUDIT.md + tools/bazel/phase5_verify.py] | Phase 1/5 established evidence classes before Phase 6. [VERIFIED: Phase 1/5 artifacts] | Planner should make every safety claim carry an evidence class and avoid local hardware overclaims. [VERIFIED: D-05/D-12] |

**Deprecated/outdated:** No external library deprecation affected this phase because the recommended stack adds no new external package. [VERIFIED: Standard Stack]

## Assumptions Log

All claims in this research were verified against local project files, current tool probes, or the Phase 6 user context; no `[ASSUMED]` claims are intentionally used. [VERIFIED: research source audit]

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| - | None | - | - |

## Open Questions

1. **How granular should print fixtures be?** [VERIFIED: D-01 leaves layout to agent discretion]
   - What we know: CORE-03 needs G-code routing, serial/file printing, pause/resume/cancel, planner-visible state, and Buddy G/M handlers covered. [VERIFIED: .planning/REQUIREMENTS.md]
   - What's unclear: The exact row granularity is not locked. [VERIFIED: 06-CONTEXT.md]
   - Recommendation: Start with one manifest row per behavior family, then split rows only when source paths, evidence class, or Rust API surface differs. [RECOMMENDED: phase5 verifier pattern]

2. **Which simulator/hardware checks will Phase 6 run locally?** [VERIFIED: environment probe]
   - What we know: `pytest` is missing in the current shell, and D-05 allows simulator/hardware/manual evidence to remain non-local. [VERIFIED: environment probe + 06-CONTEXT.md]
   - What's unclear: Whether the planner should include an optional bootstrap step for simulator safety tests. [VERIFIED: .planning/codebase/TESTING.md]
   - Recommendation: Make local Phase 6 verification Rust/Bazel/Python-only and list simulator/hardware evidence as required non-local rows unless a later plan explicitly provisions dependencies. [RECOMMENDED: D-05/D-13]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 6 stdlib verifier | yes | 3.14.4 | none needed [VERIFIED: environment probe] |
| cargo | Rust fmt/clippy/build/test | yes | 1.91.1 | none needed [VERIFIED: environment probe] |
| rustc | Rust workspace compile/test | yes | 1.91.1 | none needed [VERIFIED: environment probe] |
| rustfmt | `cargo fmt --all` | yes | 1.8.0-stable | none needed [VERIFIED: environment probe] |
| clippy | `cargo clippy --all-targets --all-features -- -D warnings` | yes | 0.1.91 | none needed [VERIFIED: environment probe] |
| Bazel | `bazel run //tools/bazel:phase6_verify` | yes | 9.1.1 | run verifier Python directly only during debugging [VERIFIED: environment probe] |
| just | `just phase6-verify` | yes | 1.48.0 | run Bazel label directly [VERIFIED: environment probe] |
| CMake | Optional retained C++ reference checks | yes | 3.27.9 | keep C++ checks non-local unless planned [VERIFIED: environment probe] |
| Ninja | Optional retained C++ reference checks | yes | 1.13.2 | keep C++ checks non-local unless planned [VERIFIED: environment probe] |
| pytest | Optional simulator safety evidence | no | - | install project requirements or classify as non-local simulator evidence [VERIFIED: environment probe + .planning/codebase/TESTING.md] |

**Missing dependencies with no fallback:** None for the recommended local Phase 6 verifier. [VERIFIED: environment probe]

**Missing dependencies with fallback:** `pytest` is missing; Phase 6 can still classify simulator safety checks as `simulator-flow` evidence until a plan provisions Python requirements and firmware/simulator inputs. [VERIFIED: environment probe + tests/integration/test_safety.py]

## Validation Architecture

`workflow.nyquist_validation` is explicitly `true`, so Phase 6 planning must include validation tasks. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Rust `cargo test` through Bazel/just, plus Python stdlib phase verifier [VERIFIED: Cargo.toml + tools/bazel/rust_workflow.sh] |
| Config file | `Cargo.toml`, `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `justfile` [VERIFIED: local source audit] |
| Quick run command | `python3 tools/bazel/phase6_verify.py --quick` after Wave 0 creates it [RECOMMENDED: tools/bazel/phase5_verify.py pattern] |
| Full suite command | `just phase6-verify` after Wave 0 wires Bazel and `just`; full path should include Rust fmt/clippy/build/test [RECOMMENDED: tools/bazel/rust_workflow.sh + justfile] |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CORE-03 | Print state, command routing, serial/file distinction, fixture coverage for retained reference surfaces [VERIFIED: .planning/REQUIREMENTS.md] | Rust unit + manifest/static-source verifier | `bazel run //tools/bazel:phase6_verify` [RECOMMENDED] | no, Wave 0 [VERIFIED: file search] |
| CORE-04 | Safety policy surface classification and evidence classes for thermal/motion/selftest/recovery/fatal flows [VERIFIED: .planning/REQUIREMENTS.md] | Rust unit + manifest/static-source verifier; simulator/hardware evidence non-local | `bazel run //tools/bazel:phase6_verify` [RECOMMENDED] | no, Wave 0 [VERIFIED: file search] |
| CORE-05 | Typed feature gates derived from reference CMake/preset/source-selection data [VERIFIED: .planning/REQUIREMENTS.md] | Rust unit + manifest/static-source verifier | `bazel run //tools/bazel:phase6_verify` [RECOMMENDED] | no, Wave 0 [VERIFIED: file search] |

### Sampling Rate

- **Per task commit:** `python3 tools/bazel/phase6_verify.py --quick` for manifest/source/API/lifecycle checks once created. [RECOMMENDED: phase5 verifier pattern]
- **Per wave merge:** `just phase6-verify` for Bazel-wired verifier and Rust checks once wired. [RECOMMENDED: tools/bazel/rust_workflow.sh + justfile]
- **Phase gate:** `just phase6-verify` green plus explicit non-local evidence rows for simulator/hardware/manual requirements before `/gsd-verify-work`. [VERIFIED: 06-CONTEXT.md + .planning/config.json]

### Wave 0 Gaps

- [ ] `tools/bazel/phase6_verify.py` - validates Phase 6 schema, lifecycle id, requirements, source paths, evidence classes, concern dispositions, Rust API shape, Bazel/just labels, and overclaim guard. [RECOMMENDED: tools/bazel/phase5_verify.py]
- [ ] `tools/bazel/manifests/phase6_printing_core.json` - covers CORE-03 print fixture/contract rows. [RECOMMENDED: CORE-03]
- [ ] `tools/bazel/manifests/phase6_safety_gates.json` - covers CORE-04 safety policy/evidence rows. [RECOMMENDED: CORE-04]
- [ ] `tools/bazel/manifests/phase6_feature_gates.json` - covers CORE-05 feature-gate rows derived from `ProjectOptions.cmake`. [RECOMMENDED: CORE-05]
- [ ] `tools/bazel/manifests/phase6_concern_dispositions.json` - covers D-10 known concerns and intentional deltas. [RECOMMENDED: 06-CONTEXT.md]
- [ ] `rust/crates/domain/src/print.rs` and tests - pure print transition and command route policies. [RECOMMENDED: D-02]
- [ ] `rust/crates/domain/src/safety.rs` and tests - pure safety policy classification and evidence types. [RECOMMENDED: D-04/D-05]
- [ ] `rust/crates/domain/src/feature.rs` extension and tests - Phase 6 feature gates keyed by validated product profiles. [RECOMMENDED: D-07/D-08]
- [ ] `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, root `BUILD.bazel`, and `justfile` labels/recipes for Phase 6. [RECOMMENDED: D-12]

## Security Domain

Security enforcement is enabled because `.planning/config.json` does not set `security_enforcement` to `false`. [VERIFIED: .planning/config.json]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Authentication/network behavior remains Phase 9 except feature-gate facts. [VERIFIED: 06-CONTEXT.md] |
| V3 Session Management | no | Session behavior remains Phase 9. [VERIFIED: 06-CONTEXT.md] |
| V4 Access Control | no | Access-control behavior remains Phase 9 unless a manifest row only records a Phase 6 gate fact. [VERIFIED: 06-CONTEXT.md] |
| V5 Input Validation | yes | Use typed Rust constructors and strict manifest schema checks for raw fixture IDs, feature gates, product profiles, and state transitions. [VERIFIED: rust/crates/domain/src/product.rs + tools/bazel/phase5_verify.py] |
| V6 Cryptography | limited | Do not hand-roll crypto or RNG; record CL-014 as a concern disposition and keep TLS/Connect behavior out of scope for Phase 9. [VERIFIED: src/common/random_hw.cpp + .planning/codebase/CONCERNS.md + 06-CONTEXT.md] |

### Known Threat Patterns for Phase 6 Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Manifest tampering or stale reference paths | Tampering | `phase6_verify.py` must require schema version, lifecycle id, existing paths, requirement IDs, and required row IDs. [RECOMMENDED: tools/bazel/phase5_verify.py] |
| Unsupported printer/board/feature combination accepted by Rust | Tampering/Safety | `ProductProfile`-keyed typed gates and rejection tests for impossible combinations. [VERIFIED: rust/crates/domain/src/product.rs + ProjectOptions.cmake] |
| Hardware safety overclaim in local docs | Repudiation/Safety | Evidence classes plus overclaim string guard. [VERIFIED: tools/bazel/phase5_verify.py + 06-CONTEXT.md] |
| Crash dump sensitive memory exposure | Information Disclosure | Preserve Phase 5 crash-dump boundary, keep upload behavior explicit, and require CL-011 disposition. [VERIFIED: src/common/crash_dump/dump.cpp + src/common/crash_dump/crash_dump_distribute.cpp + .planning/codebase/CONCERNS.md] |
| Fatal path allocation or swallowed errors | Denial of Service/Safety | Keep fatal/recovery effects behind Phase 5 boundaries; pure policies classify, adapters/effects require non-local evidence. [VERIFIED: 06-CONTEXT.md + 05-UNSAFE-BOUNDARY-AUDIT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md` - locked decisions, scope boundaries, lifecycle ID, verifier requirements. [VERIFIED]
- `.planning/REQUIREMENTS.md` - CORE-03, CORE-04, CORE-05 requirement text. [VERIFIED]
- `.planning/STATE.md` and `.planning/ROADMAP.md` - phase status, roadmap success criteria, phase boundaries. [VERIFIED]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` - repo workflow, Rust, testing, Bright Builds constraints. [VERIFIED]
- `Cargo.toml`, `rust/crates/domain/src/lib.rs`, `rust/crates/domain/src/product.rs`, `rust/crates/domain/src/feature.rs`, `rust/crates/application/src/lib.rs` - current Rust workspace and invariant model. [VERIFIED]
- `tools/bazel/phase5_verify.py`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, root `BUILD.bazel`, `justfile` - verifier/Bazel/just pattern. [VERIFIED]
- `ProjectOptions.cmake`, `utils/presets/presets.json`, `lib/AddMarlin.cmake`, `lib/AddTMCStepper.cmake` - feature-gate and Marlin/TMC source-selection references. [VERIFIED]
- `src/common/marlin_server.cpp`, `src/common/marlin_client.cpp`, `src/common/marlin_server_request.hpp`, `src/common/marlin_server_types/marlin_server_state.h`, `src/common/serial_printing.cpp`, `src/common/gcode/`, `src/marlin_stubs/` - printing behavior references. [VERIFIED]
- `src/common/safe_state.cpp`, `src/common/feature/safety_timer/`, `src/common/power_panic*`, `src/common/crash_dump/`, `src/common/feature/emergency_stop/`, `src/common/selftest/`, `src/common/probe_analysis.cpp`, `src/common/Pin.cpp`, `src/common/random_hw.cpp`, `src/mmu2/mmu2_reporting.cpp` - safety and known-concern references. [VERIFIED]
- Phase 1/5 artifacts: `01-BASELINE-MATRIX.md`, `01-SAFETY-ENVELOPE.md`, `01-CONCERN-LEDGER.md`, `05-FOREIGN-CODE-INVENTORY.md`, `05-UNSAFE-BOUNDARY-AUDIT.md`, `05-VERIFICATION.md`. [VERIFIED]

### Secondary (MEDIUM confidence)

- `.planning/codebase/TESTING.md` and `.planning/codebase/CONCERNS.md` - codebase intelligence summaries cross-checked against source files during this session. [VERIFIED: summary + source audit]

### Tertiary (LOW confidence)

- None used. [VERIFIED: research source audit]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new package selection; recommendations are existing repo Rust/Bazel/Python/stdlib patterns. [VERIFIED: Cargo.toml + tools/bazel/phase5_verify.py]
- Architecture: HIGH - module placement follows Phase 4 pure domain/application and Phase 5 boundary patterns. [VERIFIED: Phase 4/5 artifacts + Rust workspace]
- Pitfalls: HIGH for known local concerns; MEDIUM for future simulator/hardware availability because `pytest` is currently missing and hardware was not probed. [VERIFIED: source audit + environment probe]
- Security: MEDIUM - threat patterns are phase-scoped from known crash/RNG/fatal/reference concerns, not a full Phase 9 network/security audit. [VERIFIED: 06-CONTEXT.md + .planning/codebase/CONCERNS.md]

**Research date:** 2026-06-04 [VERIFIED: current_date]
**Valid until:** 2026-07-04 for local architecture and source mapping; re-run environment/tool probes before implementation if planning starts later. [RECOMMENDED: environment probe]
