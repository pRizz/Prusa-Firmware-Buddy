---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 2-2026-06-02T20-31-42
generated_at: 2026-06-02T20:31:42.861Z
---

# Phase 2: Bazel Authority and Developer Facade - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning
**Mode:** Yolo

<domain>

## Phase Boundary

Phase 2 makes Bazel and `just` the visible authority surface for developers. It should add root Bazel module files, explicit product platforms, registered firmware-oriented toolchain placeholders, target labels for the required workflow classes, and a checked `justfile` facade.

This phase should not attempt the complete Rust firmware implementation, deterministic artifact production, or subsystem parity migration. Phase 3 owns release artifacts and generators. Phase 4 owns real Rust crate architecture. Phase 2 must still make the labels and commands those later phases will extend visible and queryable now.

</domain>

<decisions>

## Implementation Decisions

### Bazel Authority

- **D-01:** Add root `MODULE.bazel`, `.bazelrc`, and `BUILD.bazel` so Bazel is a first-class workspace entrypoint instead of a vendored-only detail.
- **D-02:** Register Rust, C/C++, ASM, and asset-generator toolchain types through repo-owned labels now. The first implementation can be metadata-only because compiler/linker integration belongs to the later Rust/runtime boundary phases.
- **D-03:** Treat CMake/Python commands as reference compatibility contracts only. Bazel target labels own the developer entrypoint; existing scripts remain the implementation backend until their work is replaced in later phases.

### Platforms And Product Matrix

- **D-04:** Add explicit platform labels for host tools/tests and representative embedded products, including MINI/BUDDY, MK4/XBUDDY, COREONE/XBUDDY, XL/XLBUDDY, DWARF, MODULARBED, and xBuddy Extension.
- **D-05:** Model runtime, printer, board, and MCU as Bazel constraint settings. This gives later toolchains a typed place to attach compile/link behavior.
- **D-06:** Include the STM32H503 xBuddy Extension platform because Phase 1 captured it as part of the current supported matrix.

### Workflow Targets

- **D-07:** Expose Bazel labels for bootstrap, firmware build, Rust firmware, retained foreign code, generated assets, host tools, unit tests, simulator inputs, simulator parity, release packages, format, lint, and generated-file checks.
- **D-08:** Keep the shell dispatcher in dry-run mode by default through `BUDDY_BAZEL_EXECUTE_REFERENCE=0`. Developers can opt into reference execution, but verification must not accidentally run heavy firmware builds or hardware-bound tests.
- **D-09:** Add a phase verifier that checks file existence, required strings, Bazel queryability, and `just --list` output.

### Developer Facade

- **D-10:** Add a root `justfile` with stable recipes for bootstrap, build, test, format, lint, generated checks, simulator/parity checks, release packaging, and Phase 2 verification.
- **D-11:** Keep recipe names short and predictable. Recipes should call Bazel labels rather than re-implementing command logic directly.

### Verification Strategy

- **D-12:** Verify Phase 2 with lightweight local checks: `python3 tools/bazel/phase2_verify.py`, Bazel query over the new graph, `just --list`, and whitespace diff checks.
- **D-13:** Do not claim hardware, simulator, full firmware, or release artifact parity from Phase 2. Record those as downstream requirements tied to Phase 3 and later phases.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project And Roadmap

- `.planning/PROJECT.md` - Big Bang posture, Bazel Primary Now, `justfile` requirement, and compatibility constraints.
- `.planning/REQUIREMENTS.md` - BAZL-01, BAZL-02, and BAZL-04 traceability.
- `.planning/ROADMAP.md` - Phase 2 goal, dependency on Phase 1, and later phase boundaries.
- `.planning/STATE.md` - Current project status and pending concerns.
- `AGENTS.md` - Repo-local GSD and Bright Builds instructions.
- `AGENTS.bright-builds.md` - Bright Builds workflow and verification rules.
- `standards-overrides.md` - Repo-specific standards exceptions.

### Phase 1 Inputs

- `.planning/phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md` - Supported product, board, MCU, feature, and artifact matrix.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-REFERENCE-CAPTURE.md` - Reference command catalog and evidence classes.
- `.planning/phases/01-reference-baseline-and-safety-envelope/01-SAFETY-ENVELOPE.md` - Safety evidence boundaries and downstream hardware debt.

### Current Build Sources

- `ProjectOptions.cmake` - Current printer, board, MCU, bootloader, and feature option definitions.
- `utils/presets/presets.json` - Preset source data.
- `CMakePresets.json` - Current developer-visible preset surface.
- `CMakeLists.txt` - Current firmware target, package, and generated-header graph.
- `utils/build.py` - Current bootstrap/build/package facade.
- `.pre-commit-config.yaml` - Current format and generated-file checks.

</canonical_refs>

<code_context>

## Existing Code Insights

- The repo has no authoritative root Bazel workspace before this phase; existing Bazel files are third-party or vendored.
- `bazel`, `bazelisk`, and `just` are available locally.
- Bazel 9.1 does not expose native `sh_binary`, so repo-owned shell executable support must be explicit if no external shell ruleset is introduced.
- `buildifier` is not available locally; formatting must be kept simple and verified through Bazel parsing plus `git diff --check`.

</code_context>

<risks>

## Risks And Guardrails

- **Heavy reference execution:** Keep `BUDDY_BAZEL_EXECUTE_REFERENCE=0` by default so Phase 2 checks do not start full firmware builds or hardware-bound flows.
- **Placeholder drift:** Toolchain metadata is intentionally shallow in Phase 2. Later phases must replace placeholder metadata with real Rust/C/C++/ASM compiler and linker integration.
- **Scope creep:** Do not move generators or release artifacts into Bazel in this phase; Phase 3 owns that work.
- **False authority:** Verification must prove the labels exist and are queryable, not claim completed artifact parity.

</risks>

<ready_for_plan>

Phase 2 is ready for one execution plan that adds the Bazel root surface, platform/toolchain labels, workflow targets, `justfile`, and verification script.

</ready_for_plan>
