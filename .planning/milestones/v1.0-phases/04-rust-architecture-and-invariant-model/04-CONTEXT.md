---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 4-2026-06-03T12-43-57
generated_at: 2026-06-03T12:43:57.000Z
---

# Phase 4: Rust Architecture and Invariant Model - Context

**Gathered:** 2026-06-03
**Status:** Ready for planning
**Mode:** Yolo

<domain>

## Phase Boundary

Phase 4 establishes a real Rust workspace and pure domain model for firmware invariants. It should make the Rust architecture inspectable, buildable, and testable through Bazel and `just`, with invalid printer/board/MCU/bootloader/feature/storage/artifact/protocol values rejected before adapter code can use unchecked primitives.

This phase should not implement STM32 startup, FreeRTOS orchestration, unsafe HAL/FFI, retained C/C++/ASM/vendor boundaries, subsystem behavior parity, simulator parity, or hardware validation. Phase 5 owns foreign-code and runtime boundaries; later phases own subsystem parity.

</domain>

<decisions>

## Implementation Decisions

### Rust Workspace Shape

- **D-01:** Add a root Cargo workspace now so Rust formatting, clippy, build, docs, and tests can run locally and through Bazel/`just`.
- **D-02:** Use one pure `buddy-domain` crate as the functional core for product, board, MCU, bootloader, feature, storage, artifact, and protocol invariants.
- **D-03:** Add thin `buddy-application`, `buddy-board-adapter`, and `buddy-runtime-adapter` crates so developers can inspect the intended functional-core/imperative-shell boundaries without introducing HAL/RTOS/unsafe code early.

### Invariant Modeling

- **D-04:** Parse boundary values into Rust enums/newtypes and fallible constructors. Avoid copying sentinel-heavy C/C++ primitive patterns into the domain layer.
- **D-05:** Seed product/board/MCU/feature combinations from Phase 1 baseline evidence, `ProjectOptions.cmake`, and `utils/presets/presets.json`.
- **D-06:** Keep the initial model dependency-free and `unsafe`-free. Any future unsafe, MMIO, FFI, linker, static-memory, or retained-code boundary belongs to Phase 5.

### Verification

- **D-07:** Add a repo-owned Phase 4 verifier that checks the static architecture surface and runs `cargo fmt --check`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --workspace --all-features`, `cargo test --all-features`, and `cargo doc --workspace --all-features --no-deps`.
- **D-08:** Expose individual Rust check labels plus a full `phase4-verify` recipe through Bazel and `just`.
- **D-09:** Unit tests should prove pure state machines, constructors, policy decisions, storage migration guards, artifact parsing, and protocol transitions with explicit Arrange/Act/Assert sections.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project And Standards

- `.planning/PROJECT.md` - Big Bang Rust+Bazel posture, behavior parity bar, and `justfile` requirement.
- `.planning/REQUIREMENTS.md` - RUST-01, RUST-02, RUST-05, and VERF-02.
- `.planning/ROADMAP.md` - Phase 4 goal, success criteria, dependency on Phase 3, and downstream Phase 5 boundary.
- `.planning/STATE.md` - Current progress and known runtime-boundary concerns.
- `AGENTS.md` - Repo-local GSD, Bright Builds, Rust, and verification instructions.
- `AGENTS.bright-builds.md` - Pinned Bright Builds sidecar and workflow requirements.
- `standards-overrides.md` - Local standards exceptions; no active real override.

### Prior Phase Evidence

- `.planning/phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md` - Supported printer, board, MCU, feature, and artifact surface.
- `.planning/phases/02-bazel-authority-and-developer-facade/02-CONTEXT.md` - Bazel/`just` authority decisions and placeholder Rust target surface.
- `.planning/phases/03-artifact-and-generator-parity/03-CONTEXT.md` - Artifact and generator boundary decisions that Phase 4 must not overclaim.
- `.planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md` - Passed Phase 3 evidence and remaining Rust architecture handoff.

### Reference Sources

- `ProjectOptions.cmake` - Current printer, board, MCU, bootloader, and feature option definitions.
- `utils/presets/presets.json` - Current developer-visible supported product presets.
- `tools/bazel/BUILD.bazel` - Bazel workflow labels that Phase 4 should extend.
- `justfile` - Developer facade that Phase 4 should extend.

</canonical_refs>

<code_context>

## Existing Code Insights

- The repo already has Bazel root files, platform labels, local `shell_binary` support, and `just` recipes from Phases 2 and 3.
- Local `rustc`, `cargo`, `rustfmt`, and `clippy` are installed, so Phase 4 can run real Rust checks without adding dependencies.
- `rules_rust` is not yet introduced. Phase 4 can keep Bazel integration as explicit shell workflow labels around Cargo while later toolchain phases decide whether to adopt a deeper Rust Bazel ruleset.

</code_context>

<deferred>

## Deferred Ideas

- Real embedded Rust target triples, linker scripts, HAL/RTOS integration, FFI, unsafe boundaries, retained-code inventory, and startup behavior move to Phase 5.
- Subsystem parity models for printing, storage, network, GUI, and auxiliary controllers move to Phases 6-10.

</deferred>

---

*Phase: 04-rust-architecture-and-invariant-model*
*Context gathered: 2026-06-03*
