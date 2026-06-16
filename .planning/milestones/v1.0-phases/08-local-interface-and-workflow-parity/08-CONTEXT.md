---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 8-2026-06-13T16-58-45
generated_at: 2026-06-13T16:58:45.186Z
---

# Phase 8: Local Interface and Workflow Parity - Context

**Gathered:** 2026-06-13
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 8 preserves local GUI workflow behavior for IFCE-01 across supported display classes. It should establish source-backed parity contracts, typed Rust GUI/domain state, fixtures, verifier coverage, and local checks for screen stacks, dialogs, menus, wizards, warnings, redscreens, print controls, setup/selftest/calibration flows, Connect registration entry surfaces, localization display behavior, print previews, progress surfaces, and known GUI freeze/error paths.

This phase must not claim network service parity, transfer implementation parity, auxiliary-controller runtime parity, full firmware cutover evidence, or hardware display proof beyond explicit `simulator-flow`, `hardware-smoke`, or `manual-hardware-required` evidence classes. Those remain Phase 9, Phase 10, or Phase 11 unless a narrow local GUI fixture is required to preserve IFCE-01 behavior.

</domain>

<decisions>
## Implementation Decisions

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` - Phase 8 goal, IFCE-01 success criteria, dependencies, and later-phase boundaries.
- `.planning/REQUIREMENTS.md` - IFCE-01 requirement text and interfaces/resources traceability.
- `.planning/PROJECT.md` - Big Bang, behavior parity, Bazel Primary Now, `justfile`, and Bright Builds constraints.
- `.planning/STATE.md` - Current milestone state and prior phase decisions that affect Phase 8.

### Existing codebase maps

- `.planning/codebase/ARCHITECTURE.md` - GUI layer responsibilities, `ScreenFactory`/`Screens` pattern, GUI/Connect-to-Marlin flow, startup dependencies, and generated-resource cross-cutting concerns.
- `.planning/codebase/STRUCTURE.md` - GUI source layout, naming conventions, test placement guidance, and source ownership boundaries.
- `.planning/codebase/TESTING.md` - Unit-test and simulator-test surfaces relevant to GUI and screen behavior.
- `.planning/codebase/CONCERNS.md` - GUI freeze path, crash dump warning surface, generated asset drift, and font/translation concerns.
- `.planning/codebase/INTEGRATIONS.md` - PrusaLink credential display flow through `src/gui/screen_prusa_link.cpp`.

### Prior phase contracts

- `.planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md` - `CL-008`, `CL-011`, and GUI/resource-related concern dispositions.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md` - redscreen, crash dump, emergency/fatal GUI evidence classes.
- `.planning/phases/06-printing-core-safety-and-feature-gates/06-CONTEXT.md` - boundary that GUI workflow parity remains Phase 8 and physical behavior remains non-local evidence when not locally provable.
- `.planning/phases/07-persistence-storage-and-resource-compatibility/07-CONTEXT.md` - resource, localization, and storage compatibility contracts consumed by GUI workflows.

### Reference source surfaces

- `src/gui/guimain.cpp` - display task loop, bootstrap/home flow, Marlin client registration, and GUI readiness.
- `src/gui/ScreenHandler.hpp` - GUI screen stack behavior.
- `src/gui/ScreenFactory.hpp` - fixed-storage screen creation pattern.
- `src/gui/screen_home.cpp` - home screen flow, crash dump warning surface, and known flash/freeze concern.
- `src/gui/dialogs/` - dialog surfaces and dialog registration.
- `src/gui/menu_item/` - menu item and settings-control surfaces.
- `src/gui/wizard/` - wizard/setup workflow surfaces.
- `src/gui/resolution_240x320/` - 240x320 display-class behavior.
- `src/gui/resolution_480x320/` - 480x320 display-class behavior.
- `src/guiapi/` - lower-level GUI/window/display API support.
- `src/lang/` - localization providers and translation strings.
- `src/gui/res/` - GUI resource and font assets.
- `tests/unit/gui/` - existing GUI unit-test area.
- `tests/integration/actions/screen.py` - simulator screen interaction helper.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `src/gui/ScreenHandler.hpp`: central screen stack contract for navigation parity.
- `src/gui/ScreenFactory.hpp`: static screen allocation pattern that should inform Rust GUI identity and storage contracts.
- `src/gui/guimain.cpp`: display task startup, GUI loop, and Marlin client integration point.
- `src/gui/dialogs/`, `src/gui/menu_item/`, and `src/gui/wizard/`: reference groupings for dialog, menu, and setup workflow fixtures.
- `src/gui/resolution_240x320/` and `src/gui/resolution_480x320/`: display-class-specific parity surfaces.
- `src/lang/` and `src/gui/res/`: localization, font, icon, and resource inputs already classified by Phase 7.
- `tests/unit/gui/` and `tests/integration/actions/screen.py`: existing places for local GUI unit tests and simulator-facing screen flows.
- `tools/bazel/phase7_verify.py`, `tools/bazel/phase6_verify.py`, and `rust/crates/domain/src/resource.rs`: recent verifier and pure-domain patterns to mirror.

### Established Patterns

- Prior phases use source-backed JSON manifests, Rust domain types, standard-library verifiers, Bazel labels, and `just phaseN-verify` wrappers.
- Local checks distinguish `manifest-check`, `source-audit`, `static-source-audit`, `host-test`, `rust-host-test`, `simulator-flow`, `hardware-smoke`, and `manual-hardware-required` instead of overclaiming hardware behavior.
- Pure Rust domain code lives under `rust/crates/domain/src/`, keeps `unsafe` out, uses fallible constructors, and is tested with one-concern Arrange/Act/Assert tests.
- GUI source ownership is broad under `src/gui`; feature-owned UI slices may live under `src/feature/<feature>` when the feature owns both G-code and screen code.

### Integration Points

- Root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` are the established Bazel/just verification surfaces.
- `rust/crates/domain/src/lib.rs` exports pure domain modules and should expose any new Phase 8 GUI domain module.
- `tools/bazel/manifests/` is the established location for phase verifier manifests.
- `.planning/phases/08-local-interface-and-workflow-parity/08-VALIDATION.md` should capture local and non-local evidence without marking simulator or hardware proof as locally passed.

</code_context>

<specifics>
## Specific Ideas

- Use a `phase8_gui_workflows.json` manifest for screen stacks, dialogs, menus, wizards, print controls, setup/selftest/calibration flows, and Connect registration entry surfaces.
- Use a `phase8_display_layouts.json` manifest for display classes, localized text/layout contracts, print previews, progress surfaces, and resource/font dependencies.
- Use a `phase8_concern_dispositions.json` manifest for `CL-008`, GUI crash dump warning surfaces, generated GUI resource drift inherited from Phase 7, and any other IFCE-01-specific concerns discovered during planning.
- Add pure Rust domain contracts such as `DisplayClass`, `GuiWorkflow`, `GuiSurface`, `GuiEvidenceClass`, and `GuiParityManifest` if those names fit the existing `buddy-domain` style.
- Add an overclaim guard that rejects local-pass wording for physical LCD/touch behavior, full simulator coverage, network service parity, auxiliary runtime parity, and cutover evidence unless the artifact records the correct non-local evidence class.

</specifics>

<deferred>
## Deferred Ideas

- Network service, TLS, transfer, and WUI API behavior parity belongs to Phase 9 except for the local GUI entry surfaces needed by IFCE-01.
- Puppy, Dwarf, ModularBed, xBuddy Extension, MMU2, toolchanger, and auxiliary update runtime parity belongs to Phase 10 except for local GUI controls needed to preserve IFCE-01.
- Full cutover evidence, final display-state fixture comparison across all products, and hardware acceptance remain Phase 11 unless Phase 8 creates a narrow prerequisite artifact.

</deferred>

---

*Phase: 08-local-interface-and-workflow-parity*
*Context gathered: 2026-06-13*
