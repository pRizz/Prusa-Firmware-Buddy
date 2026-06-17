---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 14-2026-06-17T16-11-34
generated_at: 2026-06-17T16:12:37.174Z
---

# Phase 14: Simulator Evidence Gates - Context

**Gathered:** 2026-06-17
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 14 converts simulator-scoped cutover blockers into runnable, reviewable simulator evidence flows. It covers startup, task readiness, watchdog-visible startup behavior, representative G-code execution, GUI navigation, storage/resource access, transfers, selected failure behavior, and requirement traceability back to v1.0 evidence and v1.1 `SIM-*` criteria.

This phase does not prove physical watchdog timing, thermal or motion safety, physical storage-media behavior, physical UI input, live network/TLS behavior, MMU/RS485/toolchanger behavior, release-candidate packaging, retained-code maintainer acceptance, final reference demotion, or hardware-only safety outcomes. Those remain owned by later v1.1 phases.

</domain>

<decisions>
## Implementation Decisions

### Simulator Proof Scope

- **D-01:** Use a flow-by-flow simulator proof matrix rather than one umbrella simulator pass. Each simulator row should name its scenario, proof scope, `SIM-01`/`SIM-02`/`SIM-03` requirement mapping, source evidence refs, generated artifact path, expected pass/fail semantics, and residual non-simulator gates.
- **D-02:** Cover the roadmap-mandated scenario families: startup and task readiness, watchdog-visible startup behavior, representative G-code execution, GUI navigation, storage/resource access, transfers, and selected failure flows.
- **D-03:** Treat "watchdog-visible startup behavior" as simulator-observable startup/reset/readiness evidence, not physical watchdog timing or safety proof.
- **D-04:** Scenario rows should cite the relevant Phase 11 parity pyramid and reference-comparison rows so simulator proof layers on top of archived v1.0 evidence instead of rewriting it.

### Traceability and Artifact Contract

- **D-05:** Add a Phase 14-owned simulator evidence contract instead of mutating Phase 11 manifests or extending Phase 13's CI contract directly.
- **D-06:** The checked-in contract should mirror the Phase 13 pattern: stable schema, phase lifecycle metadata, status vocabulary, required artifact kinds, gate rows, source evidence refs, and generated output root under `build/ci-evidence/phase14`.
- **D-07:** Generated run artifacts should include a machine-readable run manifest, simulator log references, normalized scenario/result summaries, and redacted evidence summaries. Generated outputs stay ignored under `build/ci-evidence/phase14`.
- **D-08:** Every simulator gate must map to v1.1 requirements (`SIM-01`, `SIM-02`, `SIM-03`) and to relevant v1.0 requirement evidence, reference comparisons, parity-pyramid/cutover criteria, or retained-code rows.

### Runner and Developer Workflow

- **D-09:** Add a dedicated Phase 14 Python runner/verifier over existing simulator and pytest surfaces rather than a thin local-only wrapper or a broad Phase 13 retrofit.
- **D-10:** Expose Phase 14 through `tools/bazel/phase14_simulator_evidence.py`, `tools/bazel/phase14_simulator_evidence_test.py`, `tools/bazel/manifests/phase14_simulator_evidence_contract.json`, Bazel `phase14_verify` / `phase14_verify_tests` labels, and `just phase14-verify`.
- **D-11:** Prefer a deterministic dry-run/contract verification mode for local phase verification, with real simulator execution represented as a required runnable command and artifact contract when local Mini404/QEMU firmware inputs are unavailable.
- **D-12:** Keep existing `tests/integration/` and `utils/simulator/` as the simulator execution substrate; do not force full Bazel-native simulator tests in this phase unless the planner finds an existing hermetic path.

### Overclaim and Safety Boundaries

- **D-13:** Verifier guards must reject simulator rows or generated summaries that claim hardware proof, live service proof, release-candidate proof, signing proof, retained-code maintainer acceptance, final reference demotion, or cutover completion.
- **D-14:** Hardware-only scenarios should be represented with explicit residual statuses or classifications such as `manual-hardware-required`, `pending-hardware`, `pending-live-service`, `pending-release`, or `pending-review`, not as simulator passes.
- **D-15:** Evidence artifacts must remain secret-safe: no raw crash dumps, private certificates, signing keys, Connect tokens, Wi-Fi credentials, credential values, or firmware packages should be committed.
- **D-16:** Phase 14 may update the Phase 13 CI evidence surface only as a separate integration point if needed; simulator proof ownership stays in Phase 14 artifacts and lifecycle metadata.

### the agent's Discretion

- Exact simulator scenario IDs, artifact file names, schema field order, status vocabulary names, dry-run output shape, and verifier helper boundaries are flexible if the result remains deterministic, source-backed, traceable, redacted, and hard to overclaim.
- The planner may choose whether Phase 14 has one integrated plan or multiple sub-tasks inside one plan, but the roadmap expects one completed plan for this phase.
- Prefer standard-library Python, JSON manifests, small verifier helpers, Bazel/just wiring, and concise generated summaries over broad simulator framework rewrites.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` - Phase 14 goal, dependency, success criteria, and v1.1 roadmap position.
- `.planning/REQUIREMENTS.md` - `SIM-01`, `SIM-02`, and `SIM-03` acceptance requirements.
- `.planning/STATE.md` - current milestone state and Phase 14 starting point.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, safety, and Bright Builds constraints.
- `.planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md` - Phase 13 CI evidence contract, artifact-retention, and non-local proof boundary decisions.
- `.planning/phases/13-ci-evidence-orchestration/13-VERIFICATION.md` - passed Phase 13 local verification boundary.

### Archived v1.0 cutover evidence

- `.planning/milestones/v1.0-REQUIREMENTS.md` - archived v1.0 requirement surface that Phase 14 must not redefine.
- `.planning/milestones/v1.0-ROADMAP.md` - archived v1.0 phase history and evidence foundation.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` - v1.0 audit outcome and preserved non-local gates.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md` - parity pyramid, simulator/non-local proof, reference comparison, retained-code, and overclaim decisions.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md` - passed Phase 11 local evidence boundary.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-CONTEXT.md` - metadata hygiene and no-overclaim constraints for archived evidence.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-VERIFICATION.md` - v1.0 archive-clean verification record.

### Existing verifier, manifest, and workflow patterns

- `tools/bazel/phase13_ci_evidence.py` - latest Phase 13 standard-library verifier, CI evidence writer, artifact sanitizer, and overclaim scan pattern.
- `tools/bazel/phase13_ci_evidence_test.py` - latest Phase 13 regression-test pattern for contracts, workflow/wiring, generated outputs, and security checks.
- `tools/bazel/manifests/phase13_ci_evidence_contract.json` - checked-in contract schema, gate rows, status vocabulary, output-root, and artifact-kind pattern to mirror for Phase 14.
- `tools/bazel/phase11_verify.py` - aggregate cutover verifier and overclaim/security scan pattern.
- `tools/bazel/phase11_verify_test.py` - Phase 11 verifier regression-test pattern.
- `tools/bazel/manifests/phase11_parity_pyramid.json` - simulator layer, proof-scope, and cutover-status rows.
- `tools/bazel/manifests/phase11_requirement_evidence.json` - v1.0 requirement-to-evidence manifest pattern.
- `tools/bazel/manifests/phase11_reference_comparisons.json` - normalized comparison evidence rows for storage, protocol, G-code, GUI, transfer, and auxiliary flows.
- `tools/bazel/manifests/phase11_cutover_readiness.json` - final demotion gate and non-local blocker pattern.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` - retained-code acceptance evidence requirements.
- `tools/bazel/BUILD.bazel` - Bazel shell_binary wiring for phase verifiers.
- `tools/bazel/rust_workflow.sh` - Rust/phase verifier dispatch pattern.
- `justfile` - developer facade recipes and existing phase verification entrypoints.

### Simulator and integration test surfaces

- `.planning/codebase/TESTING.md` - simulator integration-test, pytest, CTest, CI, and pre-commit verification surfaces.
- `.planning/codebase/INTEGRATIONS.md` - network, transfer, storage, CI, artifact, credential, and service integration context.
- `.planning/codebase/CONCERNS.md` - known simulator/hardware/network/storage concern boundaries that Phase 14 must keep visible.
- `tests/integration/README.md` - simulator pytest prerequisites, command shape, firmware input, OCR/cache behavior, and debugger options.
- `tests/integration/conftest.py` - pytest simulator fixtures, firmware input handling, network ports, and simulator lifecycle.
- `tests/integration/test_basic_examples.py` - representative simulator startup and G-code examples.
- `tests/integration/test_safety.py` - simulator-visible safety/error examples and skipped-flow rationale.
- `tests/integration/test_prusa_link.py` - simulator-driven WUI/PrusaLink flow examples.
- `utils/simulator/simulator.py` - simulator process wrapper and Mini404/QEMU integration.

### Bright Builds and repo rules

- `AGENTS.md` - repo-local GSD and Bright Builds workflow rules.
- `AGENTS.bright-builds.md` - managed Bright Builds workflow and standards-routing rules.
- `standards-overrides.md` - confirms no active local Bright Builds override.
- `standards/core/architecture.md` - functional-core/imperative-shell and domain modeling guidance.
- `standards/core/code-shape.md` - early returns, `maybe_`, and size guidance.
- `standards/core/verification.md` - sync, hook, and pre-commit verification rules.
- `standards/core/testing.md` - focused unit-test and Arrange/Act/Assert expectations.
- `standards/languages/rust.md` - Rust standards if Phase 14 adds or changes Rust domain types.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase13_ci_evidence.py` and `tools/bazel/phase13_ci_evidence_test.py` provide the closest template for a checked-in evidence contract, generated run outputs, security scans, overclaim guards, and standard-library regression tests.
- `tools/bazel/manifests/phase13_ci_evidence_contract.json` already defines the CI evidence contract shape that Phase 14 can mirror while keeping phase ownership separate.
- `tools/bazel/manifests/phase11_parity_pyramid.json`, `phase11_reference_comparisons.json`, `phase11_requirement_evidence.json`, `phase11_cutover_readiness.json`, and `phase11_retained_code_justifications.json` provide the required source evidence and residual blocker taxonomy.
- `tests/integration/`, `tests/integration/conftest.py`, and `utils/simulator/simulator.py` provide the existing simulator execution substrate for startup, G-code, GUI, WUI, storage/resource, transfer, and failure examples.
- `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, root `BUILD.bazel`, and `justfile` already expose phase verifier labels and developer recipes.

### Established Patterns

- Phase verifiers use explicit constants for required IDs, required fields, source refs, generated output roots, forbidden markers, lifecycle IDs, status values, and wiring strings.
- Checked-in manifests define durable evidence contracts; generated run manifests, logs, normalized outputs, and redacted summaries live under ignored `build/` paths.
- Prior phases separate local/source-backed proof from simulator, hardware, live-service, release, signing, retained-code, and maintainer-review proof. Phase 14 must preserve that separation.
- Python verifier tests use stdlib `unittest`, temporary repo roots, explicit fixture writes/copies, and Arrange/Act/Assert comments.

### Integration Points

- Add Phase 14 simulator evidence manifest(s) under `tools/bazel/manifests/`.
- Add Phase 14 verifier/runner and tests under `tools/bazel/`.
- Add Bazel labels in `tools/bazel/BUILD.bazel`, root aliases/filegroups in `BUILD.bazel`, dispatch cases in `tools/bazel/rust_workflow.sh`, and `just phase14-verify`.
- Use `.planning/phases/14-simulator-evidence-gates/` for research, plan, summary, validation, verification, and lifecycle artifacts.
- Keep generated simulator evidence under `build/ci-evidence/phase14/` or another ignored `build/` subdirectory.

</code_context>

<specifics>
## Specific Ideas

- Maintainers should be able to answer "which simulator scenario failed, which requirement does it block, which artifact proves it, and which later gate still owns non-simulator proof" from the generated manifest alone.
- Phase 14 should not mutate archived v1.0 manifests; it should cite them and layer simulator evidence on top.
- The existing `just simulator-parity` recipe can inform naming, but Phase 14 needs stronger traceability than a thin wrapper around `pytest`.
- Real simulator execution may need firmware `.bin` inputs, Mini404/QEMU assets, OCR cache, dynamic ports, and longer runtime; local verification may need deterministic contract/dry-run modes when those prerequisites are unavailable.
- Keep raw firmware packages, raw crash dumps, private keys, certificates, tokens, and credential-bearing values out of committed source and planning artifacts.

</specifics>

<deferred>
## Deferred Ideas

- Physical hardware smoke, thermal/motion safety, emergency stop, safe-output, physical UI input, physical storage media, MMU, RS485, and toolchanger evidence belongs to Phase 15.
- Live Connect, WUI, TLS, telemetry, proxy, long-transfer, and crash-dump upload evidence belongs to Phase 16.
- Release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resources, signing, WUI, ESP, MMU, and auxiliary package proof belongs to Phase 17.
- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.
- Fully hermetic Bazel-native simulator test targets can be revisited after Phase 14 establishes the runner and evidence contract.

</deferred>

---

*Phase: 14-simulator-evidence-gates*
*Context gathered: 2026-06-17*
