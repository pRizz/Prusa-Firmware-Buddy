---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 15-2026-06-17T22-53-45
generated_at: 2026-06-17T22:53:45.617Z
---

# Phase 15: Hardware Safety and Media Qualification - Context

**Gathered:** 2026-06-17
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 15 defines and captures the physical hardware, safety, storage-media, UI-input, MMU, RS485, and toolchanger evidence required before Rust+Bazel firmware cutover readiness can be accepted. It should turn the hardware-only blockers preserved by Phases 11, 13, and 14 into a durable evidence contract, runnable or operator-facing capture workflow, redacted artifacts, and local verification gates.

This phase does not prove live Connect/WUI/TLS behavior, release-candidate signing or packaging, retained-code maintainer acceptance, or final reference demotion. It also must not convert unavailable lab hardware into local pass claims. Missing physical runs should remain explicit pending hardware evidence with the device matrix, scenario, operator, artifact, and residual risk named.

</domain>

<decisions>
## Implementation Decisions

### Hardware Qualification Matrix

- **D-01:** Add a Phase 15-owned hardware evidence contract instead of mutating Phase 11, Phase 13, or Phase 14 manifests. The contract should name the required supported printer families, boards, storage media, auxiliary-controller combinations, and cutover requirement IDs covered by each row.
- **D-02:** Use row-level qualification rather than an umbrella hardware pass. Every row should name device/printer family, board, firmware build identity, media or auxiliary surface when applicable, scenario, requirement mapping, artifact path, expected result semantics, operator metadata requirements, and residual risk.
- **D-03:** Cover the roadmap-required families: supported-printer smoke, board startup/readiness, storage media, UI input, MMU, RS485/Modbus, toolchanger/dock/offset, and auxiliary-controller combinations.
- **D-04:** Hardware availability is a first-class status. Rows without physical execution should use explicit statuses such as `pending-hardware-input`, `manual-hardware-required`, or `blocked-hardware-unavailable`, never `passed`.

### Safety and Fault Evidence

- **D-05:** Safety rows must cover watchdog behavior, thermal safety, motion safety, emergency stop, safe-output behavior, crash recovery, physical UI input, MMU fault handling, RS485/Modbus faults, and toolchanger fault or calibration scenarios.
- **D-06:** The evidence model should distinguish observed physical behavior from source-backed contract checks. Source checks can validate schema, references, redaction, and overclaim guards; only operator-supplied hardware artifacts can satisfy physical safety rows.
- **D-07:** Crash-dump and fault evidence must be redacted or summarized. Do not commit raw crash dumps, RAM dumps, credential regions, printer identifiers that should stay private, Wi-Fi credentials, Connect tokens, certificates, signing keys, or unsafe operational payloads.
- **D-08:** Safety evidence should preserve residual risk. A pass row still records what was not covered, such as long-run soak, environmental extremes, unsupported media, unavailable auxiliary boards, or maintainer approval still owned by Phase 18.

### Artifact Capture and Redaction

- **D-09:** Generated Phase 15 runtime artifacts should live under an ignored directory such as `build/ci-evidence/phase15`, mirroring the Phase 13 and Phase 14 pattern. Checked-in files define contracts, schemas, verifier logic, and dry-run examples only.
- **D-10:** Generated artifacts should include a machine-readable run manifest, normalized scenario results, redacted hardware summaries, source contract snapshot, and log references. The generated manifest should be useful to maintainers without requiring reruns.
- **D-11:** Operator metadata is required for hardware evidence: device or printer family, board, firmware build, operator identity or role, timestamp, scenario, result, artifact reference, and residual risk.
- **D-12:** Add verifier guards that reject secret markers, raw payload markers, and overclaim wording such as local hardware proof, final cutover completion, release readiness, signing proof, or reference demotion.

### Runner and Developer Workflow

- **D-13:** Add a dedicated Phase 15 Python verifier/collector using the standard-library pattern from Phase 13 and Phase 14, with deterministic local modes for contract, security, wiring, and dry-run artifact validation.
- **D-14:** Expose Phase 15 through `tools/bazel/phase15_hardware_evidence.py`, `tools/bazel/phase15_hardware_evidence_test.py`, `tools/bazel/manifests/phase15_hardware_evidence_contract.json`, Bazel `phase15_verify` / `phase15_verify_tests` labels, root aliases/docs filegroups, `tools/bazel/rust_workflow.sh`, and `just phase15-verify`.
- **D-15:** Real hardware capture may be a manual/operator JSON input or a command mode that validates supplied evidence files. Local verification should be deterministic and should pass only contract/dry-run validation when hardware inputs are absent.
- **D-16:** Keep the workflow small and auditable: prefer JSON contracts, explicit status vocabularies, path guards, `subprocess.run` without shell execution when commands are needed, and focused stdlib tests over broad firmware build or lab automation rewrites.

### Traceability and Prior Evidence

- **D-17:** Every Phase 15 row must map to `HARD-01`, `HARD-02`, and/or `HARD-03` plus relevant v1.0/Phase 11 evidence rows. Rows should cite Phase 7 storage/media, Phase 8 UI, Phase 10 auxiliary, Phase 11 parity/cutover, Phase 13 CI, and Phase 14 simulator contracts where applicable.
- **D-18:** Preserve the Phase 14 boundary: simulator-visible proof may support readiness but cannot satisfy physical safety, media, UI input, RS485, MMU, or toolchanger evidence.
- **D-19:** Preserve Phase 13's artifact-retention model. CI may validate the contract and retain generated summaries, but CI without lab hardware does not become hardware proof.
- **D-20:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 15-2026-06-17T22-53-45`.

### the agent's Discretion

- Exact scenario IDs, schema field order, status names, generated artifact file names, helper function boundaries, and dry-run output shape are flexible if the result remains deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated implementation plan or several tasks inside one plan, but the roadmap expects one completed plan for this phase.
- Prefer explicit contracts and verifier tests over prose-only checklists. Operator-facing instructions are useful only when backed by machine-readable artifacts and verifier checks.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` - Phase 15 goal, dependency, success criteria, and v1.1 roadmap position.
- `.planning/REQUIREMENTS.md` - `HARD-01`, `HARD-02`, and `HARD-03` acceptance requirements.
- `.planning/STATE.md` - current milestone state, blockers, and Phase 15 starting point.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, safety, and Bright Builds constraints.
- `.planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md` - CI evidence contract, artifact retention, pending non-local proof, and redaction decisions.
- `.planning/phases/13-ci-evidence-orchestration/13-VERIFICATION.md` - passed Phase 13 local verification boundary.
- `.planning/phases/14-simulator-evidence-gates/14-CONTEXT.md` - simulator evidence contract, traceability, dry-run artifact, and hardware-boundary decisions.
- `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md` - passed Phase 14 verification and residual hardware risks.

### Archived v1.0 cutover evidence

- `.planning/milestones/v1.0-REQUIREMENTS.md` - archived v1.0 requirement surface that Phase 15 must not redefine.
- `.planning/milestones/v1.0-ROADMAP.md` - archived v1.0 phase history and evidence foundation.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` - v1.0 audit outcome and preserved non-local gates.
- `.planning/milestones/v1.0-phases/07-persistence-storage-and-resource-compatibility/07-VERIFICATION.md` - storage and media proof boundaries.
- `.planning/milestones/v1.0-phases/08-local-interface-and-workflow-parity/08-VERIFICATION.md` - GUI, display, and input proof boundaries.
- `.planning/milestones/v1.0-phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md` - MMU, RS485, toolchanger, and auxiliary-controller proof boundaries.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md` - parity pyramid, hardware/manual proof, retained-code, reference comparison, and overclaim decisions.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md` - passed Phase 11 local evidence boundary.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-CONTEXT.md` - metadata hygiene and no-overclaim constraints for archived evidence.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-VERIFICATION.md` - v1.0 archive-clean verification record.

### Existing verifier, manifest, and evidence patterns

- `tools/bazel/phase14_simulator_evidence.py` - closest runner/verifier template for contracts, dry-run artifacts, real-input validation, path guards, security scans, and wiring checks.
- `tools/bazel/phase14_simulator_evidence_test.py` - latest stdlib regression-test pattern for evidence contract behavior.
- `tools/bazel/manifests/phase14_simulator_evidence_contract.json` - checked-in contract schema, status vocabulary, scenario rows, external-input model, source refs, and generated artifact shape to mirror.
- `tools/bazel/phase13_ci_evidence.py` - CI evidence writer, artifact sanitizer, and overclaim scan pattern.
- `tools/bazel/phase13_ci_evidence_test.py` - CI evidence regression-test pattern.
- `tools/bazel/manifests/phase13_ci_evidence_contract.json` - artifact-retention and generated-output contract shape.
- `tools/bazel/phase11_verify.py` - aggregate cutover verifier, proof-scope taxonomy, and no-overclaim guard pattern.
- `tools/bazel/phase11_verify_test.py` - Phase 11 verifier regression-test pattern.
- `tools/bazel/manifests/phase11_parity_pyramid.json` - hardware/manual layer row and cutover proof-scope taxonomy.
- `tools/bazel/manifests/phase11_cutover_readiness.json` - reference-demotion blocker and non-local evidence model.
- `tools/bazel/manifests/phase11_reference_comparisons.json` - normalized comparison rows for storage, G-code, GUI, transfer, and auxiliary flows.
- `tools/bazel/manifests/phase11_requirement_evidence.json` - requirement-to-evidence mapping pattern.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` - retained-code hardware, runtime, filesystem, USB, MMU, RS485, and toolchanger evidence requirements.

### Hardware, storage, UI, and auxiliary source evidence

- `tools/bazel/manifests/phase7_storage_media.json` - EEPROM, USB media, internal flash, semihosting, and storage-media non-local evidence rows.
- `tools/bazel/manifests/phase8_gui_workflows.json` - local GUI workflow rows that later physical UI evidence should cite.
- `tools/bazel/manifests/phase8_display_layouts.json` - display-class and layout source-backed evidence.
- `tools/bazel/manifests/phase10_auxiliary_controllers.json` - Dwarf, ModularBed, xBuddy Extension, MMU, and auxiliary-controller contract rows.
- `tools/bazel/manifests/phase10_mmu_transport.json` - MMU transport state and surface contract rows.
- `tools/bazel/manifests/phase10_modbus_rs485.json` - Modbus/RS485 request, timing, and contention evidence rows.
- `tools/bazel/manifests/phase10_toolchanger_dock_offsets.json` - toolchanger dock and offset evidence rows.
- `tools/bazel/manifests/phase10_auxiliary_build_update.json` - auxiliary build, update, flashing, and crash-dump proof boundaries.
- `.planning/codebase/STRUCTURE.md` - firmware, hardware, GUI, storage, MMU, puppy, and utility source layout.
- `.planning/codebase/INTEGRATIONS.md` - USB media, internal resources, credentials, crash dumps, CI, firmware artifact, MMU, RS485, and service integration context.
- `.planning/codebase/TESTING.md` - unit, simulator, block-device, pytest, CTest, and hardware-adjacent test surfaces.
- `.planning/codebase/CONCERNS.md` - known safety, storage, transfer, UI, crash-dump, TLS/secret, MMU, and hardware fragility concerns.

### Repo and standards guidance

- `AGENTS.md` - repo-local GSD workflow and Bright Builds routing rules.
- `AGENTS.bright-builds.md` - managed Bright Builds workflow, sync, verification, and standards-routing rules.
- `standards-overrides.md` - confirms no active local Bright Builds override.
- `standards/core/architecture.md` - functional-core/imperative-shell and domain modeling guidance.
- `standards/core/code-shape.md` - early returns, `maybe_`, and size guidance.
- `standards/core/verification.md` - sync, hook, and pre-commit verification rules.
- `standards/core/testing.md` - focused unit-test and Arrange/Act/Assert expectations.
- `standards/languages/rust.md` - Rust standards if Phase 15 adds or changes Rust domain types.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase14_simulator_evidence.py` and `tools/bazel/phase14_simulator_evidence_test.py` provide the nearest template for a phase-owned evidence contract, deterministic quick mode, real input validation, path traversal guard, security/overclaim scan, generated artifacts, Bazel labels, and `just` facade wiring.
- `tools/bazel/phase13_ci_evidence.py`, `tools/bazel/phase13_ci_evidence_test.py`, and `tools/bazel/manifests/phase13_ci_evidence_contract.json` provide the artifact retention, generated manifest, redacted summary, and CI-safe contract model.
- `tools/bazel/manifests/phase11_*.json` already identify hardware/manual gates, retained-code surfaces, reference-comparison rows, and final cutover blockers that Phase 15 should satisfy or keep pending with explicit residual risk.
- `tools/bazel/manifests/phase7_storage_media.json`, `phase8_*`, and `phase10_*` provide source-backed rows for the physical storage, UI input, MMU, RS485, toolchanger, and auxiliary-controller surfaces Phase 15 must qualify.
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` already expose phase verifiers through the established Bazel and developer-command pattern.

### Established Patterns

- Checked-in JSON manifests define durable evidence contracts; generated run manifests, log references, normalized outputs, and redacted summaries live under ignored `build/` paths.
- Phase verifiers use explicit constants for required row IDs, required fields, source refs, generated output roots, forbidden markers, lifecycle IDs, status values, and wiring strings.
- Prior phases strictly separate local deterministic checks from simulator, hardware, live-service, release, signing, retained-code, and maintainer-review proof.
- Python verifier tests use stdlib `unittest`, temporary roots, explicit fixture writes/copies, and Arrange/Act/Assert comments.

### Integration Points

- Add Phase 15 hardware evidence contract under `tools/bazel/manifests/`.
- Add Phase 15 verifier/collector and tests under `tools/bazel/`.
- Add Bazel labels in `tools/bazel/BUILD.bazel`, root aliases/docs filegroups in `BUILD.bazel`, dispatch cases in `tools/bazel/rust_workflow.sh`, and `just phase15-verify`.
- Use `.planning/phases/15-hardware-safety-and-media-qualification/` for research, plan, summary, verification, and lifecycle artifacts.
- Keep generated Phase 15 evidence under `build/ci-evidence/phase15/` or another ignored `build/` subdirectory.

</code_context>

<specifics>
## Specific Ideas

- Maintainers should be able to answer "which printer/board/media/scenario failed, which requirement does it block, which artifact proves it, who ran it, when it ran, and what residual risk remains" from the generated manifest alone.
- Phase 15 should provide an operator-facing capture format or validation mode so real lab evidence can be supplied later without changing the contract.
- The local `just phase15-verify` path should validate contracts, generated dry-run artifacts, redaction, overclaim guards, source refs, and wiring, while clearly marking physical rows as pending hardware input when no lab artifact is supplied.
- Do not mutate archived v1.0 artifacts. Cite archived evidence and layer Phase 15 hardware proof on top.
- Keep raw crash dumps, memory dumps, firmware packages, private keys, certificates, tokens, Wi-Fi credentials, PrusaLink passwords, Connect tokens, and unsafe operational data out of committed source and planning artifacts.

</specifics>

<deferred>
## Deferred Ideas

- Live Connect, WUI, TLS, telemetry, proxy, long-transfer, and crash-dump upload evidence belongs to Phase 16.
- Release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resources, signing, WUI, ESP, MMU, and auxiliary package proof belongs to Phase 17.
- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.
- Long-run soak dashboards, trend analytics, broader hardware lab automation, and post-cutover vendor/HAL replacement belong to future milestones after the basic Phase 15 evidence contract exists.

</deferred>

---

*Phase: 15-hardware-safety-and-media-qualification*
*Context gathered: 2026-06-17*
