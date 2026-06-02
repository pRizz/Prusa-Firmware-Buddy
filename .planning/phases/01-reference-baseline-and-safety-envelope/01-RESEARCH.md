---
generated_by: gsd-phase-researcher
lifecycle_mode: yolo
phase_lifecycle_id: 1-2026-06-02T15-50-10
generated_at: 2026-06-02T15:50:10.638Z
status: complete
phase: 1
requirements: [BASE-01, BASE-02, BASE-03, BASE-04]
---

# Phase 1: Reference Baseline and Safety Envelope - Research

## Research Complete

Phase 1 is a documentation and verification-contract phase. The implementation should create a small set of traceable baseline artifacts and lightweight checks that downstream Rust+Bazel phases can treat as the reference oracle.

## Planning Inputs

### Requirement Mapping

- **BASE-01:** Needs an inspectable matrix derived from existing firmware reference sources. The strongest source set is `ProjectOptions.cmake`, `utils/presets/presets.json`, `CMakePresets.json`, `CMakeLists.txt`, and `utils/build.py`.
- **BASE-02:** Needs a reference-capture catalog for existing behavior fixtures. Capture commands should cover builds, generated assets, protocol traces, simulator flows, storage migrations, and release artifacts, even when some commands are marked CI-only, hardware-required, or manually staged.
- **BASE-03:** Needs an intentional-delta ledger seeded from `.planning/codebase/CONCERNS.md`. It should preserve the distinction between current behavior, known bug, safety/security concern, rewrite disposition, and verification expectation.
- **BASE-04:** Needs a board-aware safety envelope. The envelope should describe startup, watchdogs, safe outputs, thermal/motion states, probes/loadcell, power panic, crash dumps, emergency/error flows, and auxiliary-controller safety using explicit evidence classes.

### Useful Source Surfaces

| Surface | Why It Matters |
|---------|----------------|
| `ProjectOptions.cmake` | Declares supported printers, boards, MCU options, bootloader modes, and feature flags. |
| `utils/presets/presets.json` | Source for generated CMake presets and build combinations. |
| `CMakePresets.json` | Maintainer-visible generated build preset surface. |
| `utils/build.py` | High-level current build and artifact-generation wrapper. |
| `CMakeLists.txt` | Firmware target graph, package outputs, generated headers, and board-specific source inclusion. |
| `.pre-commit-config.yaml` | Current formatting, generated-file, and drift-check hook ownership. |
| `.planning/codebase/CONCERNS.md` | Seed data for known defects, fragile areas, security considerations, and scaling limits. |
| `.planning/codebase/TESTING.md` | Current local/CI test command map. |
| `.planning/codebase/INTEGRATIONS.md` | Connect, WUI, storage, TLS, metrics, CI, and runtime integration surfaces. |

### Recommended Artifact Set

1. `01-BASELINE-MATRIX.md`
   - Human-readable matrix for supported printers, boards, MCU families, bootloader modes, major feature flags, generated resources, and release artifact types.
   - Include source references beside each group so future agents can refresh it.

2. `01-REFERENCE-CAPTURE.md`
   - Catalog of capture commands and evidence outputs.
   - Each row should include command, source inputs, output path, evidence class, local/CI/hardware requirement, and linked requirement.

3. `01-CONCERN-LEDGER.md`
   - Intentional-delta ledger seeded from `.planning/codebase/CONCERNS.md`.
   - Each entry should include category, affected files, current behavior, risk, disposition, target phase, and verification expectation.

4. `01-SAFETY-ENVELOPE.md`
   - Board-aware safety envelope covering the safety-critical flows from CONTEXT.md.
   - Use evidence classes instead of binary pass/fail claims where physical hardware is not available.

5. `01-VERIFY.py` or an equivalent lightweight check
   - Verifies artifact existence, required headings, requirement IDs, source references, and core status values.
   - Should be runnable without firmware build dependencies.

### Implementation Risks

- **False confidence:** A doc-only baseline can look complete while missing source traceability. Mitigate with a verification script that checks required source references and requirement IDs.
- **Overrunning Phase 1:** Running every firmware build or simulator flow locally can dominate the phase. Mitigate by documenting capture contracts now and marking heavy commands by evidence class.
- **Silent behavior changes:** Fixing known bugs while creating the baseline undermines parity. Mitigate by classifying concerns instead of editing subsystem code.
- **Secret leakage:** Crash dumps, signing keys, WiFi credentials, PrusaLink password, Connect token, and certificates must be described by key/path only. Do not embed values or fixture contents.
- **Generated-file churn:** Avoid committing generated firmware/resource outputs in this phase unless the plan explicitly names ownership and drift checks.

### Verification Commands To Prefer

- `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py`
- `git diff --check`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" verify lifecycle 1 --require-plans --require-verification --raw`

Full firmware builds and simulator flows should be listed in `01-REFERENCE-CAPTURE.md`; they do not need to run during Phase 1 unless the plan deliberately narrows one smoke target.

## Validation Architecture

Phase 1 validation should sample every produced artifact rather than every future firmware behavior. The validation architecture is:

1. **Schema/structure checks:** A lightweight script verifies each baseline artifact exists and contains required sections, requirement IDs, evidence classes, and canonical source paths.
2. **Traceability checks:** The same script validates that BASE-01 through BASE-04 appear in the appropriate artifacts and that concern dispositions use only approved values.
3. **Command contract checks:** Reference-capture commands are checked for declared inputs, output locations, and evidence classes, not necessarily executed if CI-only or hardware-required.
4. **Manual/hardware evidence tracking:** Hardware-bound items are marked `manual-hardware-required` or `hardware-smoke` with instructions. Their absence is tracked as evidence debt, not hidden.
5. **Lifecycle checks:** GSD lifecycle validation must pass before execution and before final commit/push.

## Recommended Plan Shape

- **Plan 01:** Create the four baseline artifacts and the verification script.
- **Plan 02:** Run the verification script, update state/roadmap traceability, and produce phase verification evidence.

If the planner chooses one plan instead, it must still keep task boundaries clear enough for the verifier to map BASE-01 through BASE-04 independently.

## Research Constraints

- Do not add Rust or Bazel implementation yet.
- Do not modify firmware behavior.
- Do not run destructive git commands.
- Do not commit before wrapper-level verification passes.
