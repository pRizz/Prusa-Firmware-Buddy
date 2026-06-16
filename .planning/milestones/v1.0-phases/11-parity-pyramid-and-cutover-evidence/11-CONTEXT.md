---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 11-2026-06-14T18-48-49
generated_at: 2026-06-14T18:48:49.708Z
---

# Phase 11: Parity Pyramid and Cutover Evidence - Context

**Gathered:** 2026-06-14
**Status:** Ready for planning
**Mode:** Yolo

<domain>

## Phase Boundary

Phase 11 delivers the final cutover evidence layer for the Rust+Bazel firmware replacement. It must prove that every v1 requirement is covered by passing local parity gates, explicit simulator or hardware/manual evidence, or documented retained-code justification before the CMake/C++ reference path can be demoted.

This phase does not add new product behavior. It aggregates, hardens, and audits the existing phase evidence from Phases 1 through 10, then adds final verifier, requirement traceability, reference-output comparison, and cutover-readiness contracts.

</domain>

<decisions>

## Implementation Decisions

### Parity Pyramid Shape

- **D-01:** Build a source-backed parity pyramid manifest that names every required verification layer: Rust unit tests, adapter/domain contract tests, generated drift checks, reference fixture comparisons, simulator flows, network/TLS/API checks, release artifact checks, and hardware smoke or manual gates.
- **D-02:** Classify each evidence row by proof scope: `local`, `ci`, `simulator`, `hardware-smoke`, `manual-hardware-required`, or `retained-code-justification`. Local verification may only mark deterministic checks green.
- **D-03:** Keep non-local proof honest. Simulator, hardware, media, long-running network, physical UI/touch, RS485, MMU, toolchanger, and final release-candidate proof must remain explicit pending/non-local evidence unless an actual runnable command or artifact exists.
- **D-04:** Preserve the existing phase verifier pattern: add a repo-owned `tools/bazel/phase11_verify.py`, `phase11_verify_test.py`, Bazel labels, and a `just phase11-verify` facade instead of burying final qualification in ad hoc documentation.

### Requirement Traceability

- **D-05:** Create a requirement-to-evidence manifest that covers every v1 requirement from `.planning/REQUIREMENTS.md`, including previously completed requirements and the Phase 11 requirements `VERF-01`, `VERF-03`, `VERF-04`, and `VERF-05`.
- **D-06:** Each requirement row must name the owning phase, phase artifacts, verifier command or evidence class, current status, intentional-delta status, residual retained-code justification when applicable, and any required non-local evidence before cutover approval.
- **D-07:** Do not treat the roadmap checkbox alone as evidence. Completed phases are inputs, but Phase 11 must cross-check actual artifacts such as `*-VERIFICATION.md`, manifests, Rust domain contracts, and Bazel/just labels.
- **D-08:** Requirements still marked pending in `.planning/REQUIREMENTS.md` must be resolved by the Phase 11 evidence manifest or intentionally kept pending with a named cutover blocker. No silent pass-through is allowed.

### Reference Output Comparison

- **D-09:** Add explicit reference-comparison rows for product artifacts, generated resources, storage migrations, protocol traces, G-code behavior fixtures, UI/display-state fixtures, network/TLS/API behavior, auxiliary-controller flows, and release metadata.
- **D-10:** Use normalized semantic comparisons where byte identity is not yet a valid local contract. Byte-for-byte claims require a named reference fixture, normalization rule, or generated output known to be deterministic.
- **D-11:** CMake/C++ remains the reference oracle for final comparison, but Bazel remains the developer authority. Any command that invokes CMake/Python reference tooling must be labeled reference-only and guarded from default local execution if it is heavy, hardware-bound, or signing-sensitive.
- **D-12:** Secret-bearing and sensitive evidence remains name-only or redacted. Do not store Wi-Fi passwords, PrusaLink passwords, Connect tokens, certificate bytes, signing key values, raw crash dumps, or firmware payload bytes in Phase 11 manifests.

### Cutover Criteria

- **D-13:** Add a cutover-readiness contract that states the minimum criteria for demoting the CMake/C++ reference path: all v1 requirements mapped, local verifier passed, non-local gates identified, retained-code justifications accepted, intentional deltas documented, and no overclaim wording present.
- **D-14:** Keep the final CMake/C++ demotion itself gated. Phase 11 may add criteria and evidence, but should not delete or demote the reference path unless the evidence contract can prove the criteria are satisfied and the plan explicitly owns that transition.
- **D-15:** Represent residual retained C/C++/ASM/vendor islands as accepted, blocked, or deferred with owners and evidence. A retained island is acceptable only when it has a named boundary and justification from the earlier phase artifacts.
- **D-16:** Known defects from `.planning/codebase/CONCERNS.md` and phase-specific concern disposition manifests must appear in the cutover evidence as preserved temporarily, fixed with tests, accepted retained behavior, or blocked.

### Verification And Lifecycle

- **D-17:** Relevant local verification should include the Phase 11 verifier tests, the Phase 11 verifier, Rust format/lint/build/test checks through existing Bazel/just labels, and lifecycle validation.
- **D-18:** The Phase 11 verifier must check for overclaim language that asserts hardware proof from local-only evidence, final cutover completion, or firmware byte identity when the evidence is only manifest, CI, simulator, hardware/manual, or retained-code justification.
- **D-19:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 11-2026-06-14T18-48-49`.

### the agent's Discretion

- Exact manifest names, row IDs, schema field order, Rust type names, and verifier helper structure are flexible if they remain source-backed, reviewable, deterministic, and covered by tests.
- The planner may split Phase 11 into focused plans by parity pyramid manifest, requirement traceability, reference comparison and cutover evidence, Rust domain contracts, and aggregate verifier/facade wiring.
- Prefer small standard-library Python helpers and pure Rust domain types over broad build-system rewrites. The final evidence layer should be auditable, not clever.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` - Phase 11 goal, dependencies, success criteria, and progress table.
- `.planning/REQUIREMENTS.md` - v1 requirement list and pending Phase 11 requirement IDs.
- `.planning/STATE.md` - current project state, recent decisions, and Phase 11 focus.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, and Bright Builds constraints.

### Prior phase evidence

- `.planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFICATION.md` - baseline and safety evidence.
- `.planning/phases/02-bazel-authority-and-developer-facade/02-VERIFICATION.md` - Bazel and just facade evidence.
- `.planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md` - artifact and generator parity evidence.
- `.planning/phases/04-rust-architecture-and-invariant-model/04-VERIFICATION.md` - Rust domain and invariant evidence.
- `.planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-VERIFICATION.md` - retained code and unsafe boundary evidence.
- `.planning/phases/06-printing-core-safety-and-feature-gates/06-VERIFICATION.md` - printing, safety, and feature gate evidence.
- `.planning/phases/07-persistence-storage-and-resource-compatibility/07-VERIFICATION.md` - persistence, storage, and resource evidence.
- `.planning/phases/08-local-interface-and-workflow-parity/08-VERIFICATION.md` - GUI/local interface evidence.
- `.planning/phases/09-network-web-services-and-transfers/09-VERIFICATION.md` - network, WUI, Connect, TLS, and transfer evidence.
- `.planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md` - auxiliary-controller and expansion evidence.

### Existing verifier and manifest patterns

- `tools/bazel/phase10_verify.py` - latest verifier structure and overclaim checks.
- `tools/bazel/phase10_verify_test.py` - latest verifier regression-test pattern.
- `tools/bazel/BUILD.bazel` - Bazel shell_binary wiring for phase verifiers.
- `justfile` - existing phase verification facade recipes.
- `tools/bazel/manifests/phase6_printing_core.json` - source-backed parity manifest pattern.
- `tools/bazel/manifests/phase7_generated_outputs.json` - generated-output parity evidence pattern.
- `tools/bazel/manifests/phase8_gui_workflows.json` - GUI workflow evidence pattern.
- `tools/bazel/manifests/phase9_connect_contracts.json` - network/service evidence pattern.
- `tools/bazel/manifests/phase10_auxiliary_controllers.json` - auxiliary-controller evidence pattern.

### Rust domain patterns

- `rust/crates/domain/src/lib.rs` - exported domain API and invariant error pattern.
- `rust/crates/domain/src/artifact.rs` - artifact invariant contracts.
- `rust/crates/domain/src/gui.rs` - GUI parity contract pattern.
- `rust/crates/domain/src/network.rs` - network parity contract pattern.
- `rust/crates/domain/src/auxiliary.rs` - auxiliary parity contract pattern.

### Codebase risk and verification references

- `.planning/codebase/TESTING.md` - existing unit, integration, simulator, and block-device test surfaces.
- `.planning/codebase/CONCERNS.md` - known bugs, fragile areas, security concerns, and scaling limits that must be reflected in cutover evidence.
- `.planning/codebase/INTEGRATIONS.md` - external service, storage, network, auth, TLS, metrics, CI, and firmware artifact surfaces.
- `standards-overrides.md` - confirms no active local Bright Builds override.
- `AGENTS.md` and `AGENTS.bright-builds.md` - repo-local and Bright Builds workflow rules.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- Existing Phase 6 through Phase 10 JSON manifests under `tools/bazel/manifests/` already encode source-backed parity rows with evidence classes, proof scopes, intentional deltas, lifecycle IDs, and non-local evidence handling.
- Existing phase verifiers from `tools/bazel/phase6_verify.py` through `tools/bazel/phase10_verify.py` provide the standard-library Python pattern for manifest checks, Rust API checks, overclaim checks, and command-line modes.
- `tools/bazel/rust_workflow.sh`, `tools/bazel/BUILD.bazel`, and `justfile` already expose repeatable Rust and phase verification entrypoints.
- `rust/crates/domain/src/*` already contains pure, unsafe-free domain contracts for artifacts, storage, GUI, network, printing, safety, resources, products, and auxiliary controllers.

### Established Patterns

- Phase verifiers use explicit constants for required row IDs, required fields, allowed evidence classes, forbidden markers, and overclaim strings.
- New Rust domain surfaces use enums, row-id newtypes, input structs, fallible constructors, and focused Arrange/Act/Assert tests.
- Planning artifacts distinguish local deterministic checks from simulator, hardware, manual, and retained-code evidence instead of claiming impossible local proof.
- Build-system integration uses `shell_binary` wrappers in `tools/bazel/BUILD.bazel` and short recipes in `justfile`.

### Integration Points

- Add Phase 11 manifests under `tools/bazel/manifests/`.
- Add Phase 11 verifier and tests under `tools/bazel/`.
- Add any pure Rust cutover/parity types in `rust/crates/domain/src/` and export them from `rust/crates/domain/src/lib.rs`.
- Wire Phase 11 verifier/test labels in `tools/bazel/BUILD.bazel` and `justfile`.
- Use `.planning/phases/11-parity-pyramid-and-cutover-evidence/` for research, plans, summaries, validation, and verification artifacts.

</code_context>

<specifics>

## Specific Ideas

- Phase 11 should be the final "evidence of evidence" layer. It should not repeat every subsystem implementation detail, but it must make missing evidence impossible to hide.
- Use source-backed manifests rather than prose-only completion claims.
- Treat heavy or hardware-bound proof as first-class evidence rows, not failed local checks.
- Keep the CMake/C++ reference path visible until the cutover criteria explicitly allow demotion.
- Make the verifier fail on overclaim wording and on missing mappings for pending requirements.

</specifics>

<deferred>

## Deferred Ideas

- Actual production cutover, deletion, or demotion of the CMake/C++ reference path is deferred unless the Phase 11 plan can prove all cutover criteria and explicitly owns that transition.
- New firmware features, improved proxy/TLS capabilities, transfer concurrency redesign, retained-vendor replacement, and hardware-lab dashboards remain v2 scope from `.planning/REQUIREMENTS.md`.

</deferred>

---

*Phase: 11-parity-pyramid-and-cutover-evidence*
*Context gathered: 2026-06-14*
