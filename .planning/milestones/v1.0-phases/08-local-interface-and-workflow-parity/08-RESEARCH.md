---
generated_by: gsd-phase-researcher
phase_lifecycle_id: 8-2026-06-13T16-58-45
generated_at: 2026-06-13
---

# Phase 8: Local Interface and Workflow Parity - Research

**Researched:** 2026-06-13 [VERIFIED: local environment current_date]
**Domain:** Local GUI workflow parity, display-class layout contracts, Rust domain invariants, Bazel/just verification [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
**Confidence:** HIGH for repo implementation patterns; MEDIUM for future simulator/hardware proof because Phase 8 explicitly classifies those as non-local evidence until later gates [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

<user_constraints>
## User Constraints (from CONTEXT.md) [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

### Locked Decisions

### GUI workflow parity surface

- **D-01:** Treat the existing C++ GUI layer as the Phase 8 reference oracle. Required source surfaces include `src/gui`, `src/guiapi`, `src/gui/dialogs`, `src/gui/menu_item`, `src/gui/footer`, `src/gui/wizard`, `src/gui/resolution_240x320`, `src/gui/resolution_480x320`, and display task startup through `src/gui/guimain.cpp`.
- **D-02:** Build explicit Phase 8 manifests for screen-stack behavior, dialog/menu/wizard workflows, print controls, setup/selftest/calibration flows, Connect registration entry surfaces, warning/redscreen/error surfaces, localization/layout behavior, and known concern dispositions.
- **D-03:** Manifest rows should name requirement ID, retained source paths, reference behavior, Rust surface, evidence class, local/non-local proof status, and intentional-delta status. Do not accept freehand GUI parity claims without source paths or fixture identities.

### Display classes, layout, and localization

- **D-04:** Preserve both supported display classes as first-class parity dimensions: 240x320 and 480x320. Phase 8 plans should include display-class-specific layout contracts instead of assuming one resolution generalizes to the other.
- **D-05:** Preserve localized text, font/resource visibility, truncation/layout behavior, print preview/progress surfaces, and error/warning text as compatibility contracts tied to `src/lang`, `src/gui/res`, `src/guiapi/include`, and Phase 7 resource compatibility work.
- **D-06:** Local verification may prove manifest coverage, Rust type behavior, source path traceability, layout fixture shape, and simulator-test wiring. Actual LCD/touch behavior, timing-sensitive rendering, physical controls, and long-run UI operation must stay classified as non-local evidence until simulator or hardware gates prove them.

### Rust domain contracts

- **D-07:** Extend the existing `buddy-domain` style with pure Rust types for Phase 8 GUI concepts rather than introducing primitive string maps. Good candidates include display class, screen identity, workflow identity, dialog kind, warning/error surface, localization surface, GUI evidence class, and workflow parity row identity.
- **D-08:** Use fallible constructors and enums to reject impossible display/workflow/evidence combinations early. Keep pure domain modules `unsafe`-free and test them with focused Arrange/Act/Assert unit tests.
- **D-09:** Keep GUI adapter or runtime effects thin. Rust domain contracts should describe and validate parity facts; retained C++ GUI, simulator, or hardware integration remains an adapter/reference surface until later implementation proves replacement behavior.

### Known concerns and intentional deltas

- **D-10:** Phase 8 must explicitly disposition `CL-008`: home screen can remain active with events disabled when a flash action fails to start. This concern must receive a GUI/error-flow parity test or an approved intentional delta with evidence for no-op flash action and event re-enable behavior.
- **D-11:** Phase 8 should preserve the crash dump warning surface that appears through the GUI while leaving crash dump transport/security implementation to the Phase 6 and Phase 9 boundaries already established.
- **D-12:** If the Rust rewrite fixes a known GUI reference defect, the plan must name it as an intentional delta, map it to IFCE-01, and add regression evidence. Otherwise, preserve current reference behavior until a later approved fix changes it.

### Verification and lifecycle

- **D-13:** Add a repo-owned Phase 8 verifier exposed through Bazel and `just`, following the Phase 4 through Phase 7 pattern. It should check required manifests, Rust API shape, source-path coverage, concern dispositions, Bazel/just labels, validation artifact presence, lifecycle metadata, and overclaim wording.
- **D-14:** Relevant local verification should include Rust formatting/lint/build/tests, Phase 8 verifier regression tests, a quick `just phase8-verify` path, Bazel queryability for new labels, and lifecycle validation. Heavy firmware builds, simulator display flows, and hardware display/touch checks may be recorded as explicit non-local evidence.
- **D-15:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 8-2026-06-13T16-58-45`.

### the agent's Discretion

- Exact manifest names, row IDs, schema field order, Rust type names, and verifier helper structure are flexible if they remain source-backed, reviewable, and covered by tests.
- The planner may split Phase 8 into focused plans by GUI reference manifests, Rust domain contracts, display/layout/localization fixtures, concern dispositions, and aggregate verification wiring.
- Fixture granularity is flexible, but each fixture should prove one GUI compatibility concern and avoid embedding sensitive crash dump or credential values.

### Deferred Ideas (OUT OF SCOPE)

- Network service, TLS, transfer, and WUI API behavior parity belongs to Phase 9 except for the local GUI entry surfaces needed by IFCE-01.
- Puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, toolchanger, and auxiliary update runtime parity belongs to Phase 10 except for local GUI controls needed to preserve IFCE-01.
- Full cutover evidence, final display-state fixture comparison across all products, and hardware acceptance remain Phase 11 unless Phase 8 creates a narrow prerequisite artifact.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| IFCE-01 | Rust firmware preserves GUI workflows for supported display classes, including screen stack behavior, dialogs, menus, wizards, warnings, redscreens, print controls, selftest/calibration flows, Connect registration, and localization. [VERIFIED: .planning/REQUIREMENTS.md] | Implement source-backed Phase 8 manifests, Rust GUI domain types, display/layout fixtures, concern dispositions, and a Bazel/just verifier. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: rust/crates/domain/src/lib.rs] |
</phase_requirements>

## Summary

Phase 8 should not implement a new GUI framework; it should encode the current C++ GUI as a reference oracle through manifests, pure Rust domain contracts, and verifier coverage. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] The relevant reference surfaces are `src/gui`, `src/guiapi`, `src/gui/dialogs`, `src/gui/menu_item`, `src/gui/footer`, `src/gui/wizard`, the two resolution directories, and `src/gui/guimain.cpp`. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/codebase/ARCHITECTURE.md]

The existing architecture uses a bounded screen stack, fixed storage screen allocation, dialog/FSM display mapping, display-specific defaults, translation providers, and simulator-facing OCR helpers. [VERIFIED: src/gui/ScreenHandler.hpp; VERIFIED: src/gui/ScreenFactory.hpp; VERIFIED: src/gui/dialogs/DialogHandler.cpp; VERIFIED: include/guiconfig/GuiDefaults.hpp; VERIFIED: src/lang/translator.cpp; VERIFIED: tests/integration/actions/screen.py] Phase 8 should represent those facts as explicit compatibility contracts before any adapter or runtime replacement claims parity. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

The proven local implementation pattern from Phases 6 and 7 is a Python standard-library verifier, JSON manifests under `tools/bazel/manifests/`, optional fixtures under `tools/bazel/fixtures/`, Rust `buddy-domain` newtypes/enums, Bazel `shell_binary` targets, root aliases, and a `just phaseN-verify` facade. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile; VERIFIED: rust/crates/domain/src/lib.rs] The Phase 8 verifier must retain the prior overclaim guard style because local checks can prove source-path coverage, schema shape, Rust invariants, and wiring, but not physical LCD/touch or long-run simulator behavior. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tools/bazel/phase7_verify.py]

**Primary recommendation:** Build Phase 8 as `phase8_gui_workflows.json`, `phase8_display_layouts.json`, `phase8_concern_dispositions.json`, a new `rust/crates/domain/src/gui.rs`, `tools/bazel/phase8_verify.py`, `tools/bazel/phase8_verify_test.py`, Bazel/just wiring, and `08-VALIDATION.md`; do not claim runtime GUI parity beyond the evidence class recorded in each row. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: rust/crates/domain/src/resource.rs]

## Project Constraints (from AGENTS.md)

- Read `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` when present, and relevant Bright Builds standards before planning, implementation, or audit work. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md; VERIFIED: standards-overrides.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/index.md]
- The project is a Big Bang Rust rewrite with behavior parity, Bazel as the authoritative build system, a required `justfile`, Bright Builds Rules, safety evidence, and explicit retained foreign-code boundaries. [VERIFIED: AGENTS.md; VERIFIED: .planning/PROJECT.md]
- Do not edit managed Bright Builds blocks or sidecar files directly. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md]
- Keep source-backed evidence explicit and do not overclaim local hardware, simulator, physical display, or cutover proof. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/PROJECT.md]
- For Rust code, use the existing workspace style, forbid unsafe code in pure domain modules, prefer `foo.rs` plus `foo/` for new multi-file modules, use fallible constructors/newtypes/enums for invariants, and test pure logic with Arrange/Act/Assert unit tests. [VERIFIED: Cargo.toml; VERIFIED: rust/crates/domain/src/lib.rs; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md]
- Prefer functional core / imperative shell, parse raw values into domain types at boundaries, and make illegal states unrepresentable when practical. [CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md; VERIFIED: rust/crates/domain/src/lib.rs]
- Prefer early returns and `let...else` for guard-style Rust extraction when clearer, and use `maybe_` names for internal optional values when practical. [CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/code-shape.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]
- Use repo-owned verification entrypoints before low-level tool sequences, and run relevant verification before commits. [CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/verification.md; VERIFIED: justfile]
- Project skills directories `.claude/skills/` and `.agents/skills/` were not present in this checkout. [VERIFIED: local command `find .claude/skills .agents/skills -maxdepth 2 -type f -name SKILL.md`]
- The local checked-in `standards/` directory was absent, so canonical Bright Builds standards were fetched from the pinned commit in `AGENTS.bright-builds.md`. [VERIFIED: local command `rg --files | rg '(^|/)standards(/|$)'`; VERIFIED: AGENTS.bright-builds.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/index.md]

## Standard Stack

### Core

| Component | Version / Source | Purpose | Why Standard |
|-----------|------------------|---------|--------------|
| Existing C++ GUI oracle | C++23 reference under `src/gui` and `src/guiapi` [VERIFIED: AGENTS.md; VERIFIED: .planning/codebase/ARCHITECTURE.md] | Defines screen stacks, display task startup, dialogs, menus, wizards, errors, print controls, and layout behavior. [VERIFIED: src/gui/guimain.cpp; VERIFIED: src/gui/ScreenHandler.hpp; VERIFIED: src/gui/dialogs/DialogHandler.cpp] | Locked by Phase 8 decisions as the reference oracle. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |
| `buddy-domain` Rust crate | `0.1.0`, workspace edition 2024, rust-version 1.85 [VERIFIED: rust/crates/domain/Cargo.toml; VERIFIED: Cargo.toml] | Hosts pure Rust invariant types for firmware domains. [VERIFIED: rust/crates/domain/src/lib.rs] | Prior phases use it for product, print, safety, storage, and resource invariants. [VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: rust/crates/domain/src/resource.rs] |
| Python stdlib verifier | Python 3.14.4 available locally [VERIFIED: local command `python3 --version`] | Validates manifests, source paths, lifecycle metadata, Rust API strings, Bazel/just wiring, and overclaim wording. [VERIFIED: tools/bazel/phase7_verify.py] | Phase 6 and Phase 7 verifiers use this deterministic pattern without adding verifier dependencies. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: tools/bazel/phase7_verify.py] |
| Bazel `shell_binary` wiring | Bazel 9.1.1 available locally [VERIFIED: local command `bazel --version`] | Exposes verifier and Rust workflow labels under `//tools/bazel:*` and root aliases. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel] | Existing phases already expose `phase6_verify`, `phase7_verify`, and verifier tests through Bazel. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel] |
| `justfile` facade | just 1.48.0 available locally [VERIFIED: local command `just --version`] | Provides developer-facing `phaseN-verify` recipes. [VERIFIED: justfile] | Project constraints require a `justfile` and Phase 7 already uses `just phase7-verify`. [VERIFIED: .planning/PROJECT.md; VERIFIED: justfile] |
| Cargo/Rust checks | cargo 1.91.1 and rustc 1.91.1 available locally; workspace rust-version is 1.85 [VERIFIED: local command `cargo --version`; VERIFIED: local command `rustc --version`; VERIFIED: Cargo.toml] | Runs `cargo fmt`, `cargo clippy`, `cargo test`, `cargo doc`, and `cargo build` through `rust_workflow.sh`. [VERIFIED: tools/bazel/rust_workflow.sh] | Existing Rust workflow labels call Cargo commands through Bazel. [VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: tools/bazel/BUILD.bazel] |

### Supporting

| Component | Version / Source | Purpose | When to Use |
|-----------|------------------|---------|-------------|
| Catch2 C++ unit-test surface | Vendored via existing CMake unit tests [VERIFIED: .planning/codebase/TESTING.md; VERIFIED: tests/unit/gui/CMakeLists.txt] | Tests GUI-adjacent C++ layout/window behavior where existing native unit tests are the right proof. [VERIFIED: tests/unit/gui/text_input_layout_tests.cpp] | Use only for narrow retained C++ GUI reference tests or fixture extraction checks. [VERIFIED: .planning/codebase/TESTING.md] |
| pytest simulator helpers | `pytest~=7.3.2`, `pytest-asyncio~=0.21`, `easyocr~=1.7`, and `pillow~=10.4` are listed in requirements [VERIFIED: requirements.txt; VERIFIED: pyproject.toml] | Supports simulator screen OCR and screenshot-based integration flows. [VERIFIED: tests/integration/actions/screen.py] | Record simulator-flow evidence only when a built firmware and simulator flow actually run. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tests/integration/actions/screen.py] |
| Phase 7 resource contracts | Phase 7 resources, translations, fonts, and generated outputs are already manifest-backed. [VERIFIED: tools/bazel/manifests/phase7_resources.json; VERIFIED: tools/bazel/manifests/phase7_generated_outputs.json] | Supplies GUI-visible localization/resource compatibility inputs for Phase 8 layout and text contracts. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] | Reference Phase 7 rows rather than duplicating resource-generation logic. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| JSON manifests plus Python stdlib verifier | YAML/TOML or a new schema-validation package | JSON keeps prior Phase 6/7 verifier patterns and avoids adding a dependency; new schema packages would need versioning and bootstrap decisions. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/manifests/phase7_resources.json] |
| Pure `buddy-domain` GUI types | Primitive string maps inside verifier-only code | Domain types make invalid display/workflow/evidence combinations rejectable before adapter code consumes them; primitive maps would conflict with D-07. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: rust/crates/domain/src/resource.rs] |
| Static manifest/source verification as the local quick path | Heavy firmware build or simulator OCR in every quick check | Phase 8 local proof is limited to source path, schema, Rust invariant, and wiring evidence; simulator/hardware proof remains explicit non-local evidence unless run. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |

**Installation:** No new npm, Cargo, or Python package installation is recommended for Phase 8 planning because the implementation can use the existing Rust workspace, Python standard library, Bazel wrapper, and `justfile`. [VERIFIED: Cargo.toml; VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: justfile]

```bash
# No new packages recommended for Phase 8.
```

**Version verification:** No new external package versions were introduced during research; local tool versions were verified with `python3 --version`, `bazel --version`, `just --version`, `cargo --version`, `rustc --version`, and `node --version`. [VERIFIED: local environment availability audit]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── phase8_verify.py                  # stdlib static verifier
├── phase8_verify_test.py             # unittest regression suite for verifier failures
├── manifests/
│   ├── phase8_gui_workflows.json      # screen stacks, dialogs, menus, wizards, print/setup workflows
│   ├── phase8_display_layouts.json    # 240x320 and 480x320 text/layout/progress contracts
│   └── phase8_concern_dispositions.json
└── fixtures/
    └── phase8_gui/
        └── layout_fixture_catalog.json # optional source-backed fixture identities, not screenshots unless captured

rust/crates/domain/src/
├── lib.rs
└── gui.rs                             # DisplayClass, GuiWorkflow, GuiSurface, GuiEvidenceClass, GuiParityRowId

.planning/phases/08-local-interface-and-workflow-parity/
├── 08-CONTEXT.md
├── 08-RESEARCH.md
└── 08-VALIDATION.md
```

This structure mirrors the Phase 7 verifier/manifests/fixtures/domain split and keeps Phase 8 artifacts in existing ownership locations. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/manifests/phase7_resources.json; VERIFIED: tools/bazel/fixtures/phase7_storage/redacted_migration_catalog.json; VERIFIED: rust/crates/domain/src/lib.rs]

### Pattern 1: Source-Backed GUI Workflow Manifests

**What:** Represent each GUI workflow as a manifest row with `id`, `requirement`, `source_paths`, `reference_behavior`, `rust_surface`, `display_classes`, `evidence_class`, `proof_scope`, `non_local_evidence`, and `intentional_delta`. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tools/bazel/phase7_verify.py]

**When to use:** Use for screen stack behavior, dialogs, menus, wizards, print controls, setup/selftest/calibration flows, Connect registration entry surfaces, warning/error surfaces, and redscreens. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**Reference facts to encode:**
- `Screens` keeps a bounded stack of `MAX_SCREENS = 16`, stores a current `ScreenFactory::UniquePtr`, exposes `Open`, `Close`, `CloseAll`, `ClosePrinting`, `Count`, `IsScreenOpened`, `IsScreenClosed`, and `gui_loop_until_dialog_closed`. [VERIFIED: src/gui/ScreenHandler.hpp]
- `ScreenFactory` creates screens in fixed static storage and uses `static_assert(sizeof(T) <= storage.size())`. [VERIFIED: src/gui/ScreenFactory.hpp]
- `gui_run()` initializes splash then pushes home, applies menu timeout from config, runs bootstrap, initializes `marlin_client`, sets event notify mask, closes splash, provides `gui_ready`, and loops dialogs, print readiness, screens, and GUI bare loop. [VERIFIED: src/gui/guimain.cpp]
- `DialogHandler` maps `ClientFSM` values to dialogs or screens and includes `Wait`, `SafetyTimer`, `Load_unload`, `Preheat`, `Selftest`, `NetworkSetup`, `Printing`, `QuickPause`, `Warning`, `PrintPreview`, and calibration/tuning flows behind feature gates. [VERIFIED: src/gui/dialogs/DialogHandler.cpp]

### Pattern 2: Display-Class Contracts Are Not Optional

**What:** Treat `DisplayClass::Mini240x320` and `DisplayClass::Large480x320` as explicit Rust values and manifest fields. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: include/guiconfig/guiconfig.h; VERIFIED: include/guiconfig/GuiDefaults.hpp]

**When to use:** Use for layout rows, localized text rows, print preview/progress rows, dialog layout rows, menu rows, redscreen rows, and Connect registration entry rows. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**Reference facts to encode:**
- `BOARD_IS_BUDDY()` selects `DISPLAY_TYPE_MINI`, while `BOARD_IS_XBUDDY()` and `BOARD_IS_XLBUDDY()` select `DISPLAY_TYPE_LARGE`. [VERIFIED: include/guiconfig/guiconfig.h]
- Mini display defaults use `ScreenWidth = 240` and `ScreenHeight = 320`, while large display defaults use `ScreenWidth = 480` and `ScreenHeight = 320`. [VERIFIED: include/guiconfig/GuiDefaults.hpp]
- Print preview base layout differs between `src/gui/resolution_240x320/screen_print_preview_base.cpp` and `src/gui/resolution_480x320/screen_print_preview_base.cpp`. [VERIFIED: src/gui/resolution_240x320/screen_print_preview_base.cpp; VERIFIED: src/gui/resolution_480x320/screen_print_preview_base.cpp]
- Print-control icon resources differ between 64x64 icons for 240x320 and 80x80 icons for 480x320. [VERIFIED: src/gui/resolution_240x320/screen_printing_layout.hpp; VERIFIED: src/gui/resolution_480x320/screen_printing_layout.hpp]

### Pattern 3: Rust GUI Domain Module

**What:** Add `rust/crates/domain/src/gui.rs`, export it from `lib.rs`, and add `InvariantError` variants for invalid GUI row IDs, display classes, workflow identities, localization/layout surfaces, and evidence classes. [VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: rust/crates/domain/src/resource.rs]

**When to use:** Use when manifest rows or future adapter code must parse raw GUI/display evidence into typed values before validating compatibility. [CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]

**Example type set:** `DisplayClass`, `GuiWorkflow`, `GuiSurface`, `GuiEvidenceClass`, `GuiParityRowId`, `LocalizationSurface`, and `IntentionalDeltaStatus`. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: rust/crates/domain/src/resource.rs]

### Pattern 4: Deterministic Phase Verifier

**What:** Implement `tools/bazel/phase8_verify.py` with constants for phase slug, lifecycle ID, expected manifest paths, required fields, required row IDs, allowed evidence classes, Rust API strings, and overclaim strings. [VERIFIED: tools/bazel/phase7_verify.py]

**When to use:** Use for the quick local gate and for the Bazel/just aggregate path. [VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]

**Checks to include:**
- JSON top-level `schema_version`, `phase`, `phase_lifecycle_id`, and collection shape. [VERIFIED: tools/bazel/phase7_verify.py]
- Required row IDs for screen stacks, print controls, setup/selftest/calibration, Connect registration entry, warnings/redscreens, localization/layout, CL-008, and crash dump warning. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md]
- Existing `source_paths` for every row. [VERIFIED: tools/bazel/phase7_verify.py]
- Allowed evidence classes, with non-local proof required for LCD/touch, simulator-only, hardware-only, timing-sensitive, and long-run UI claims. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tools/bazel/phase7_verify.py]
- Rust API surface strings in `rust/crates/domain/src/gui.rs` and `rust/crates/domain/src/lib.rs`. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: rust/crates/domain/src/lib.rs]
- Bazel labels, root aliases, `rust_workflow.sh` dispatch, and `just phase8-verify`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]
- Forbidden secret/byte markers for crash dump and credential-adjacent fixtures. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md; VERIFIED: tools/bazel/phase7_verify.py]

### Pattern 5: Validation Artifact From the Start

**What:** Create `08-VALIDATION.md` during planning or Wave 0 and require it in the verifier once the first implementation plan adds labels. [VERIFIED: .planning/config.json; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-VALIDATION.md]

**When to use:** Use because `.planning/config.json` sets `workflow.nyquist_validation` to `true`. [VERIFIED: .planning/config.json]

### Anti-Patterns to Avoid

- **Freehand parity statements:** A statement like "GUI parity implemented" without source paths, fixture identity, display class, evidence class, and proof scope conflicts with D-03 and should fail verification. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tools/bazel/phase7_verify.py]
- **One display class as proxy for all displays:** `GuiDefaults` and resolution-specific files prove that 240x320 and 480x320 layouts diverge. [VERIFIED: include/guiconfig/GuiDefaults.hpp; VERIFIED: src/gui/resolution_240x320/screen_printing_layout.hpp; VERIFIED: src/gui/resolution_480x320/screen_printing_layout.hpp]
- **Runtime replacement before contracts:** Phase 8 decisions say Rust domain contracts should describe and validate parity facts while retained C++ GUI, simulator, or hardware integration remains adapter/reference surface until later proof. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
- **Credential or crash dump bytes in fixtures:** Phase 1 safety guidance prohibits committed credential values, private signing keys, custom certificate bytes, and crash dump memory contents in planning artifacts. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md]
- **Network parity creep:** Connect registration entry surfaces are in Phase 8, but Connect, WUI, TLS, transfer, telemetry, and service behavior remain Phase 9. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/ROADMAP.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Screen navigation oracle | A new inferred Rust screen-stack model with guessed behavior | Source-backed rows tied to `ScreenHandler.hpp`, `ScreenFactory.hpp`, and `guimain.cpp` | The reference uses bounded stack state, fixed storage creation, pending-open flags, close modes, and GUI loop sequencing. [VERIFIED: src/gui/ScreenHandler.hpp; VERIFIED: src/gui/ScreenFactory.hpp; VERIFIED: src/gui/guimain.cpp] |
| Dialog/FSM workflow mapping | Ad hoc lists of dialog names | Rows derived from `DialogHandler.cpp` `FSMDisplayConfig` and feature gates | The source maps `ClientFSM` to dialogs/screens and asserts config size against `ClientFSM::_count`. [VERIFIED: src/gui/dialogs/DialogHandler.cpp] |
| Display-class generalization | A single layout contract for both screens | Explicit 240x320 and 480x320 rows | The source has display macros, different `GuiDefaults`, and resolution-specific print layout files. [VERIFIED: include/guiconfig/guiconfig.h; VERIFIED: include/guiconfig/GuiDefaults.hpp; VERIFIED: src/gui/resolution_240x320/screen_printing_layout.hpp; VERIFIED: src/gui/resolution_480x320/screen_printing_layout.hpp] |
| Localization engine | A duplicate translation/string system | Existing `src/lang` providers and Phase 7 resource contracts | The repo already generates translation hash tables and required chars from `.po` files and registers providers. [VERIFIED: src/lang/CMakeLists.txt; VERIFIED: src/lang/translator.cpp; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md] |
| Simulator screen reading | A new OCR/screenshot helper | Existing `tests/integration/actions/screen.py` when simulator evidence is in scope | The helper already takes screenshots, runs OCR with EasyOCR, waits for text, and detects home/booting fragments. [VERIFIED: tests/integration/actions/screen.py; VERIFIED: requirements.txt] |
| Verifier framework | New validation dependency or external schema runner | Python stdlib verifier plus `unittest` regression tests | Phase 7 already validates JSON, source paths, row IDs, evidence classes, Rust API strings, labels, and overclaims this way. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/phase7_verify_test.py] |
| Proof vocabulary | Boolean `passed` fields for all parity facts | Evidence classes and proof scopes | Phase 8 explicitly distinguishes local source/type/wiring proof from simulator, hardware, and manual evidence. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |

**Key insight:** The hard part of Phase 8 is not drawing screens; it is preventing unverifiable GUI parity claims from slipping in before each workflow, display class, localized layout, and known error path has source-backed identity and an evidence class. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tools/bazel/phase7_verify.py]

## Common Pitfalls

### Pitfall 1: Treating 480x320 As a Superset of 240x320

**What goes wrong:** The plan validates large-display layouts and assumes Mini display parity follows automatically. [VERIFIED: include/guiconfig/GuiDefaults.hpp]

**Why it happens:** `GuiDefaults`, preview layout, print-control icon sizing, text variants, and menu defaults contain display-specific branches. [VERIFIED: include/guiconfig/GuiDefaults.hpp; VERIFIED: src/gui/resolution_240x320/screen_print_preview_base.cpp; VERIFIED: src/gui/resolution_480x320/screen_print_preview_base.cpp; VERIFIED: src/gui/MItem_network.hpp]

**How to avoid:** Require every layout-sensitive manifest row to name `display_classes` and reject rows that do not cover `240x320` or `480x320` where IFCE-01 scope requires both. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**Warning signs:** A manifest row has one `reference_behavior` but no display class, or a verifier checks only `src/gui/resolution_480x320`. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

### Pitfall 2: Overclaiming Physical UI Proof From Static Checks

**What goes wrong:** `just phase8-verify` passes and a summary claims physical LCD, touch, timing-sensitive rendering, or long-run UI behavior is locally proven. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**Why it happens:** Manifest coverage and Rust type behavior are easy to confuse with runtime display evidence. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**How to avoid:** Add overclaim strings and require `non_local_evidence` fields for physical display, touch, simulator-only, hardware-smoke, and manual-hardware-required rows. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**Warning signs:** Phrases like "GUI parity implemented", "hardware display verified locally", or "full cutover evidence complete" appear in Phase 8 artifacts without matching evidence. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

### Pitfall 3: Missing CL-008 or Crash Dump Warning Disposition

**What goes wrong:** The plan covers common screens but leaves the known home-screen flash/freeze path or crash dump warning surface implicit. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**Why it happens:** CL-008 is a known bug path in `screen_home.cpp`, and crash dump warning text lives in the home screen rather than in a standalone crash-dump subsystem. [VERIFIED: src/gui/screen_home.cpp; VERIFIED: .planning/codebase/CONCERNS.md]

**How to avoid:** Require `phase8_concern_dispositions.json` rows for `CL-008`, crash dump warning surface, generated GUI resource drift inherited from Phase 7, and any IFCE-01 concern discovered during planning. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md]

**Warning signs:** The concern manifest has no `concern_id`, no `regression_guard`, or an intentional delta without IFCE-01 mapping. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

### Pitfall 4: Pulling Phase 9 or Phase 10 Runtime Scope Into GUI Parity

**What goes wrong:** Phase 8 starts implementing Connect registration transport, WUI APIs, TLS, transfers, or auxiliary-controller runtime parity. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/ROADMAP.md]

**Why it happens:** Some GUI screens expose entry surfaces for Connect, PrusaLink, MMU, and auxiliary features. [VERIFIED: src/gui/dialogs/DialogConnectReg.cpp; VERIFIED: src/gui/screen_prusa_link.cpp; VERIFIED: src/gui/MItem_mmu.cpp]

**How to avoid:** Keep Phase 8 rows to local GUI entry surfaces and classify network/service/auxiliary behavior as deferred unless a narrow local GUI fixture is required. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**Warning signs:** A Phase 8 task mentions TLS verification, WUI endpoint parity, transfer download behavior, puppy flashing runtime, or toolchanger runtime state beyond local GUI control surfaces. [VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

### Pitfall 5: Fixture Secrets or Memory Dumps

**What goes wrong:** A crash dump, password, token, certificate bytes, or signing key material appears in a GUI fixture or planning artifact. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md]

**Why it happens:** The home screen warning explicitly says crash dumps may include sensitive information, and Phase 1 prohibits committing credential-bearing material. [VERIFIED: src/gui/screen_home.cpp; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md]

**How to avoid:** Store fixture identities and expected text/layout facts, not raw dumps or secret values; add verifier forbidden markers for secrets, raw EEPROM, byte arrays, and dump bytes. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md]

**Warning signs:** Fixture fields named `password_value`, `token_value`, `certificate_bytes`, `raw_dump`, `ram_bytes`, or `BEGIN PRIVATE KEY`. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md]

## Code Examples

Verified patterns from official or repo sources:

### Bazel / Just Verifier Wiring

```bash
# Source pattern: tools/bazel/rust_workflow.sh
phase8_verify)
  python3 tools/bazel/phase8_verify.py --all
  ;;
phase8_verify_tests)
  python3 tools/bazel/phase8_verify_test.py
  ;;
```

Use this dispatch shape because Phase 6 and Phase 7 verifier labels already route through `rust_workflow.sh`. [VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: tools/bazel/BUILD.bazel]

```make
# Source pattern: justfile
phase8-verify:
    bazel run //tools/bazel:phase8_verify_tests
    bazel run //tools/bazel:phase8_verify
```

Use verifier tests before aggregate verifier, matching `phase7-verify`. [VERIFIED: justfile]

### Rust Newtype / Enum Pattern

```rust
// Source pattern: rust/crates/domain/src/resource.rs
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct GuiParityRowId(String);

impl GuiParityRowId {
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyGuiParityRowId);
        }
        if raw.len() > 96 || raw.contains('/') || raw.bytes().any(|byte| byte.is_ascii_control()) {
            return Err(InvariantError::InvalidGuiParityRowId);
        }
        Ok(Self(raw))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}
```

Follow the existing `ResourceRuntimePath`, `BazelLabel`, and `GeneratedSurface` fallible-constructor style when adding Phase 8 GUI domain types. [VERIFIED: rust/crates/domain/src/resource.rs; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]

### Manifest Row Shape

```json
{
  "id": "screen-stack-home-bootstrap",
  "requirement": "IFCE-01",
  "source_paths": [
    "src/gui/guimain.cpp",
    "src/gui/ScreenHandler.hpp",
    "src/gui/ScreenFactory.hpp",
    "src/gui/screen_home.cpp"
  ],
  "reference_behavior": "gui_run initializes splash, pushes home, runs bootstrap, closes splash, marks gui_ready, then loops dialogs, print readiness, screens, and gui loop",
  "rust_surface": "rust/crates/domain/src/gui.rs::GuiWorkflow",
  "display_classes": ["240x320", "480x320"],
  "evidence_class": "source-backed-manifest",
  "proof_scope": "source-path-and-domain-contract",
  "non_local_evidence": "simulator-flow-or-hardware-smoke-required-for-rendered-display-proof",
  "intentional_delta": "none"
}
```

This row shape follows the Phase 8 locked field requirements and Phase 7 manifest validation pattern. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tools/bazel/phase7_verify.py]

### Verifier Source-Path Validation Pattern

```python
# Source pattern: tools/bazel/phase7_verify.py
def require_existing_source_paths(row: dict[str, Any], row_name: str) -> set[str]:
    source_paths = require_list_of_strings(row, "source_paths", row_name)
    existing_paths: set[str] = set()
    for source_path in source_paths:
        if not (ROOT / source_path).exists():
            raise VerificationError(f"{row_name} references missing source path: {source_path}")
        existing_paths.add(source_path)
    return existing_paths
```

Use this exact validation style for all Phase 8 manifest rows because D-03 rejects GUI parity claims without source paths. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| C++/CMake GUI behavior existed as implementation-only behavior. [VERIFIED: .planning/codebase/ARCHITECTURE.md] | Phase 8 should create source-backed GUI manifests plus Rust domain contracts. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | Phase 8 planning scope, 2026-06-13 context. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | Planner can create explicit tasks for workflows, display classes, and known concerns instead of vague GUI parity work. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |
| Earlier local phases could over-index on source audits alone. [VERIFIED: .planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md] | Phase 6/7 and Phase 8 use evidence classes to distinguish local checks from simulator/hardware/manual proof. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | Phases 6 and 7 established the pattern before Phase 8. [VERIFIED: .planning/STATE.md; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-VALIDATION.md] | Phase 8 can block overclaims about physical UI behavior while still providing useful local proof. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |
| GUI display differences could be treated as conditional C++ details. [VERIFIED: include/guiconfig/GuiDefaults.hpp] | 240x320 and 480x320 must be first-class parity dimensions. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | Locked by D-04 in Phase 8 context. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | Layout and localization fixture rows should fail if they omit required display-class coverage. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |
| Known GUI defects could be silently preserved or fixed. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md] | Known defects require explicit concern dispositions or intentional deltas with evidence. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | Phase 1 concern ledger and Phase 8 D-10/D-12. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | CL-008 and crash dump warning must become planned checks, not incidental notes. [VERIFIED: src/gui/screen_home.cpp; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |

**Deprecated/outdated:**
- Freehand statements such as "GUI parity implemented" are outdated for this project because Phase 8 requires source paths, fixture identities, evidence classes, proof status, and intentional-delta status. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
- A single display-class proof is outdated for Phase 8 because 240x320 and 480x320 are locked as first-class dimensions. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: include/guiconfig/GuiDefaults.hpp]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| - | None. All recommendations are derived from Phase 8 context, repository source, local tool probes, or cited Bright Builds/OWASP sources. [VERIFIED: listed Sources section] | - | - |

**If this table is empty:** All claims in this research were verified or cited; no user confirmation is needed before planning. [VERIFIED: research provenance audit]

## Open Questions (RESOLVED)

1. **Should Phase 8 include any actual simulator display flow, or only simulator-flow wiring?**
   - What we know: Local checks may prove simulator-test wiring, while actual simulator display flows are non-local unless run. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
   - What's unclear: The phase context permits recording simulator flows as explicit non-local evidence, but does not require a specific simulator run in Phase 8. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
   - Recommendation: Plan static verifier and simulator fixture wiring first; add a simulator-flow task only if a built firmware fixture and stable OCR target are already available in the implementation wave. [VERIFIED: tests/integration/actions/screen.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
   - **RESOLVED:** Phase 8 execution uses static verifier coverage, source-backed simulator wiring references, and explicit non-local simulator evidence fields. It does not require an actual simulator display run unless a later task adds a built firmware fixture and records that run as `simulator-flow`.

2. **How granular should `phase8_gui_workflows.json` rows be?**
   - What we know: The agent has discretion over manifest names, row IDs, schema order, and fixture granularity. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
   - What's unclear: The context does not prescribe every row ID. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
   - Recommendation: Use one row per compatibility concern: screen-stack bootstrap/home, print preview, print start readiness, printing controls, each major dialog/FSM group, menu/settings group, selftest/calibration group, Connect registration entry, redscreen/error group, and CL-008. [VERIFIED: src/gui/guimain.cpp; VERIFIED: src/gui/dialogs/DialogHandler.cpp; VERIFIED: src/gui/screen_home.cpp]
   - **RESOLVED:** Use exact source-backed row IDs in Plan 08-01 for each compatibility concern, including semantic print-control actions for pause/resume/cancel/stop/reprint/preview icons. Avoid one catch-all GUI row.

3. **Should GUI C++ unit tests be added in Phase 8?**
   - What we know: Existing GUI unit tests cover layout/window/text-input surfaces, and CMake/Catch2 is the local C++ unit-test path. [VERIFIED: tests/unit/gui/CMakeLists.txt; VERIFIED: tests/unit/gui/text_input_layout_tests.cpp; VERIFIED: .planning/codebase/TESTING.md]
   - What's unclear: The locked Phase 8 decisions require local verification but do not require new C++ host tests. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
   - Recommendation: Prefer Rust domain and Python verifier regression tests for Phase 8; add C++ tests only for a narrow CL-008 or layout behavior that cannot be captured as a source-backed contract. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: tests/unit/gui/CMakeLists.txt]
   - **RESOLVED:** Phase 8 local proof uses Rust domain tests and Python verifier regression tests. Do not add new C++ GUI unit tests unless implementation discovers a narrow CL-008 or layout behavior that cannot be represented as a source-backed manifest contract.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | `tools/bazel/phase8_verify.py` and verifier tests | yes [VERIFIED: local command `python3 --version`] | Python 3.14.4 [VERIFIED: local command `python3 --version`] | None needed for stdlib verifier. [VERIFIED: tools/bazel/phase7_verify.py] |
| Bazel | `//tools/bazel:phase8_verify`, root aliases, queryability | yes [VERIFIED: local command `bazel --version`] | 9.1.1 [VERIFIED: local command `bazel --version`] | Direct `python3 tools/bazel/phase8_verify.py --quick` before labels exist. [VERIFIED: tools/bazel/phase7_verify.py] |
| just | `just phase8-verify` facade | yes [VERIFIED: local command `just --version`] | 1.48.0 [VERIFIED: local command `just --version`] | Bazel labels can be run directly before facade exists. [VERIFIED: justfile] |
| Cargo | Rust domain checks | yes [VERIFIED: local command `cargo --version`] | 1.91.1 local; workspace minimum 1.85 [VERIFIED: local command `cargo --version`; VERIFIED: Cargo.toml] | Bazel `rust_workflow.sh` calls Cargo when labels exist. [VERIFIED: tools/bazel/rust_workflow.sh] |
| rustc | Rust domain crate build/test | yes [VERIFIED: local command `rustc --version`] | 1.91.1 local; workspace minimum 1.85 [VERIFIED: local command `rustc --version`; VERIFIED: Cargo.toml] | None if Rust code is planned. [VERIFIED: Cargo.toml] |
| Node | GSD lifecycle/init tooling | yes [VERIFIED: local command `node --version`] | v24.13.0 [VERIFIED: local command `node --version`] | No fallback needed for planning artifact generation. [VERIFIED: local command `node ... gsd-tools.cjs init phase-op 8`] |
| pytest + OCR requirements | Optional simulator screen flows | listed in requirements, not probed as installed [VERIFIED: requirements.txt; VERIFIED: pyproject.toml] | `pytest~=7.3.2`, `pytest-asyncio~=0.21`, `easyocr~=1.7`, `pillow~=10.4` [VERIFIED: requirements.txt] | Keep simulator proof non-local unless dependencies and firmware fixture are prepared. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |

**Missing dependencies with no fallback:**
- None for the recommended static/Rust/Bazel/just implementation path because Python, Bazel, just, Cargo, rustc, and Node are available locally. [VERIFIED: environment availability audit]

**Missing dependencies with fallback:**
- Simulator/OCR dependencies were not probed during this research; Phase 8 can classify simulator display proof as non-local and rely on static verifier/Rust proof locally unless a simulator task explicitly installs or verifies those requirements. [VERIFIED: requirements.txt; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

## Validation Architecture

Nyquist validation applies because `.planning/config.json` sets `workflow.nyquist_validation` to `true`, and the user explicitly requested this section. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` for verifier regression tests, Rust `cargo test --all-features` for `buddy-domain`, Bazel `shell_binary` wrappers for aggregate labels, and `just` facade for developer workflow. [VERIFIED: tools/bazel/phase7_verify_test.py; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile] |
| Config file | `Cargo.toml`, `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `justfile`, and future `08-VALIDATION.md`. [VERIFIED: Cargo.toml; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile; VERIFIED: .planning/config.json] |
| Quick run command | `python3 tools/bazel/phase8_verify.py --quick` once created. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |
| Full suite command | `just phase8-verify` once created. [VERIFIED: justfile; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| IFCE-01 | Screen stack bootstrap/home behavior is manifest-covered with source paths and Rust surface. [VERIFIED: src/gui/guimain.cpp; VERIFIED: src/gui/ScreenHandler.hpp] | static verifier + Rust unit | `python3 tools/bazel/phase8_verify.py --quick` and `cargo test --all-features` | no; Wave 0 files required. [VERIFIED: local command `find .planning/phases/08-local-interface-and-workflow-parity -maxdepth 1 -type f`] |
| IFCE-01 | Dialog, menu, wizard, print-control, setup/selftest/calibration, warning, redscreen, and Connect registration entry rows exist. [VERIFIED: src/gui/dialogs/DialogHandler.cpp; VERIFIED: src/gui/dialogs/DialogConnectReg.cpp; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | static verifier | `python3 tools/bazel/phase8_verify.py --quick` | no; Wave 0 files required. [VERIFIED: tools/bazel/manifests] |
| IFCE-01 | 240x320 and 480x320 layout/localization/print preview/progress contracts are explicit. [VERIFIED: include/guiconfig/GuiDefaults.hpp; VERIFIED: src/gui/resolution_240x320/screen_print_preview_base.cpp; VERIFIED: src/gui/resolution_480x320/screen_print_preview_base.cpp] | static verifier + Rust unit | `python3 tools/bazel/phase8_verify.py --quick` and `cargo test --all-features` | no; Wave 0 files required. [VERIFIED: rust/crates/domain/src/lib.rs] |
| IFCE-01 | CL-008 and crash dump warning are explicitly dispositioned without secret or memory bytes. [VERIFIED: src/gui/screen_home.cpp; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md] | verifier regression tests | `python3 tools/bazel/phase8_verify_test.py` | no; Wave 0 files required. [VERIFIED: tools/bazel/phase7_verify_test.py] |
| IFCE-01 | Bazel labels, root aliases, `rust_workflow.sh`, `just phase8-verify`, lifecycle metadata, validation artifact, and overclaim guards are present. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] | Bazel/facade/static verifier | `bazel query "//tools/bazel:phase8_verify + //tools/bazel:phase8_verify_tests + //:phase8_verify + //:phase8_verify_tests"` and `just phase8-verify` | no; Wave 0 files required. [VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/BUILD.bazel] |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase8_verify.py --quick` once the verifier exists, plus focused `cargo test -p buddy-domain` or `cargo test --all-features` for touched Rust domain code. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: Cargo.toml]
- **Per wave merge:** Run `python3 tools/bazel/phase8_verify_test.py`, `python3 tools/bazel/phase8_verify.py --all`, and Bazel query for new Phase 8 labels once labels exist. [VERIFIED: tools/bazel/phase7_verify_test.py; VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/BUILD.bazel]
- **Phase gate:** Run `just phase8-verify`, Rust format/lint/build/tests through existing `just rust-*` recipes where Rust was touched, lifecycle validation through GSD tooling, and record simulator/hardware/manual evidence as non-local unless actually run. [VERIFIED: justfile; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

### Wave 0 Gaps

- [ ] `tools/bazel/phase8_verify.py` - validates manifests, source paths, Rust API surface, no unsafe pure domain code, concern dispositions, lifecycle, validation artifact, Bazel/just wiring, and overclaim guards. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
- [ ] `tools/bazel/phase8_verify_test.py` - regression tests for missing rows, missing source paths, invalid lifecycle, invalid evidence class, missing display class, missing CL-008, missing crash dump warning, secret markers, missing Rust API strings, missing labels, and overclaims. [VERIFIED: tools/bazel/phase7_verify_test.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
- [ ] `tools/bazel/manifests/phase8_gui_workflows.json` - screen stacks, dialogs, menus, wizards, print controls, setup/selftest/calibration flows, Connect registration entry surfaces, warnings, redscreens, and errors. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]
- [ ] `tools/bazel/manifests/phase8_display_layouts.json` - 240x320 and 480x320 layout, localized text, font/resource visibility, truncation, print preview, progress, and error/warning text rows. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: include/guiconfig/GuiDefaults.hpp]
- [ ] `tools/bazel/manifests/phase8_concern_dispositions.json` - CL-008, crash dump warning, generated GUI resource drift inherited from Phase 7, and any IFCE-01-specific concern discovered during planning. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md]
- [ ] `rust/crates/domain/src/gui.rs` and `rust/crates/domain/src/lib.rs` exports - pure GUI/display/evidence domain types and errors. [VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: rust/crates/domain/src/resource.rs]
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` Phase 8 labels/recipes. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]
- [ ] `.planning/phases/08-local-interface-and-workflow-parity/08-VALIDATION.md` - Nyquist contract with local/non-local evidence boundaries and phase lifecycle ID. [VERIFIED: .planning/config.json; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-VALIDATION.md]

## Security Domain

Security enforcement is enabled by default for this research because `.planning/config.json` does not set `security_enforcement` to `false`. [VERIFIED: .planning/config.json] OWASP ASVS latest stable version is 5.0.0 according to the OWASP project page and OWASP/ASVS GitHub page. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://github.com/OWASP/ASVS]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | limited | Phase 8 covers only local GUI entry surfaces for Connect registration and PrusaLink credential display; network auth behavior remains Phase 9. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/codebase/INTEGRATIONS.md] |
| V3 Session Management | no | Phase 8 local GUI manifests do not own web/session behavior, and Phase 9 owns Connect/WUI service behavior. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/ROADMAP.md] |
| V4 Access Control | limited | GUI controls should preserve feature-gated visibility and workflow availability, while authorization semantics for network services are out of scope. [VERIFIED: src/gui/dialogs/DialogHandler.cpp; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |
| V5 Input Validation | yes | Use Rust fallible constructors/newtypes for GUI row IDs, display classes, workflow identities, source paths, evidence classes, and layout fixture identities; validate JSON manifests in the verifier. [VERIFIED: rust/crates/domain/src/resource.rs; VERIFIED: tools/bazel/phase7_verify.py; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md] |
| V6 Cryptography | no for implementation; yes for boundary protection | Phase 8 should not implement TLS, token handling, or crash dump transport, but it must not commit credential values, private keys, certificate bytes, or crash dump memory contents in GUI fixtures. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md] |
| Error handling and data protection controls | yes | Preserve GUI warning/error surfaces, especially crash dump warning text, without weakening redaction or transport boundaries. [VERIFIED: src/gui/screen_home.cpp; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md] |

### Known Threat Patterns for Phase 8 Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Overclaiming local proof as hardware/display proof | Repudiation | Verifier overclaim scan plus required evidence-class and proof-scope fields. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |
| Secret or memory bytes in fixtures | Information Disclosure | Name-only fixture identities, forbidden secret markers, and no raw crash dump/credential byte material. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md; VERIFIED: tools/bazel/phase7_verify.py] |
| Invalid GUI manifest path or row identity | Tampering | Rust newtypes/fallible constructors and Python source-path validation. [VERIFIED: rust/crates/domain/src/resource.rs; VERIFIED: tools/bazel/phase7_verify.py] |
| Display-class omission causing incompatible layout behavior | Tampering / Denial of Service | Required `display_classes` coverage for 240x320 and 480x320 where the workflow is display-visible. [VERIFIED: include/guiconfig/GuiDefaults.hpp; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |
| Silent known-defect drift | Tampering / Repudiation | `phase8_concern_dispositions.json` rows for CL-008 and crash dump warning with regression guards or intentional-delta evidence. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md` - Phase 8 locked decisions, discretion, deferred scope, lifecycle ID, and source surfaces. [VERIFIED: file read]
- `.planning/REQUIREMENTS.md` - IFCE-01 requirement text and traceability. [VERIFIED: file read]
- `.planning/ROADMAP.md` - Phase 8 success criteria and Phase 9/10/11 boundaries. [VERIFIED: file read]
- `.planning/STATE.md` - prior phase decisions and Phase 7 completion state. [VERIFIED: file read]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` - repo workflow, Bright Builds sidecar, and local override state. [VERIFIED: file read]
- `src/gui/guimain.cpp`, `src/gui/ScreenHandler.hpp`, `src/gui/ScreenFactory.hpp`, `src/gui/screen_home.cpp`, `src/gui/dialogs/DialogHandler.cpp`, `src/gui/dialogs/DialogConnectReg.cpp` - GUI startup, stack, fixed storage, known concern, dialog/FSM, and Connect registration entry reference surfaces. [VERIFIED: file read]
- `include/guiconfig/guiconfig.h`, `include/guiconfig/GuiDefaults.hpp`, `src/gui/resolution_240x320/*`, `src/gui/resolution_480x320/*` - display-class selection and layout defaults. [VERIFIED: file read]
- `src/lang/CMakeLists.txt`, `src/lang/translator.cpp`, `src/gui/res/`, Phase 7 manifests - localization/resource compatibility inputs. [VERIFIED: file read; VERIFIED: file listing]
- `tools/bazel/phase7_verify.py`, `tools/bazel/phase7_verify_test.py`, `tools/bazel/rust_workflow.sh`, `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `justfile` - verifier, regression, Bazel, and facade patterns. [VERIFIED: file read]
- `rust/crates/domain/src/lib.rs`, `rust/crates/domain/src/resource.rs`, `Cargo.toml`, `rust/crates/domain/Cargo.toml` - Rust domain style and workspace version metadata. [VERIFIED: file read]
- Pinned Bright Builds standards - architecture, code shape, verification, testing, and Rust guidance. [CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/code-shape.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/verification.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]
- OWASP ASVS project and GitHub pages for current ASVS stable version context. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://github.com/OWASP/ASVS]

### Secondary (MEDIUM confidence)

- `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/INTEGRATIONS.md` - generated repo maps used for source discovery and testing/integration context. [VERIFIED: file read/grep]

### Tertiary (LOW confidence)

- None. [VERIFIED: research source audit]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - it uses existing repo tooling and locally verified tool versions, with no new package recommendations. [VERIFIED: environment availability audit; VERIFIED: tools/bazel/phase7_verify.py]
- Architecture: HIGH - patterns are direct continuations of Phase 6/7 artifacts and current GUI source surfaces. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: src/gui/guimain.cpp; VERIFIED: rust/crates/domain/src/lib.rs]
- Pitfalls: HIGH - pitfalls come from locked Phase 8 decisions, Phase 1 concerns, source comments, and existing verifier overclaim patterns. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md; VERIFIED: src/gui/screen_home.cpp; VERIFIED: tools/bazel/phase7_verify.py]
- Simulator/hardware execution: MEDIUM - the evidence boundary is clear, but actual simulator/hardware availability and proof are intentionally not claimed by this research. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md]

**Research date:** 2026-06-13 [VERIFIED: local environment current_date]
**Valid until:** 2026-07-13 for repository-local planning patterns, or sooner if Phase 8 context/ROADMAP changes. [VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-CONTEXT.md; VERIFIED: .planning/ROADMAP.md]
