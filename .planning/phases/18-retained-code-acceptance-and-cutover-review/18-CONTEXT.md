---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 18-2026-06-20T14-27-15
generated_at: 2026-06-20T14:32:22.889Z
---

# Phase 18: Retained-Code Acceptance and Cutover Review - Context

**Gathered:** 2026-06-20
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 18 makes retained-code acceptance, final reference-demotion criteria, maintainer exceptions, and final cutover readiness explicit and auditable. It does not redefine archived v1.0 parity contracts and does not claim reference demotion by local checks alone. The phase should turn the Phase 13-17 evidence gates plus archived Phase 11 cutover blockers into a maintainer-review surface that can approve, reject, or exception each required gate with rationale.

</domain>

<decisions>
## Implementation Decisions

### Retained-code acceptance packets

- **D-01:** Use a Phase 18-owned row-level JSON acceptance packet contract as the authoritative retained-code acceptance model.
- **D-02:** Every retained C, C++, ASM, generated, vendor, HAL, RTOS, network, filesystem, signing, release-artifact, resource, MMU, auxiliary-controller, and runtime surface that remains at cutover needs a packet or an explicitly verified row mapping from the Phase 11 retained-code justifications.
- **D-03:** Each packet should require stable identity, taxonomy tags, retained source refs, prior phase refs, required evidence refs, supplied evidence result refs, owner, approver role, approval metadata, status, rationale, residual risk, blocker or deferred action, exception ref, secret-handling policy, and unsupported-claim guards.
- **D-04:** Use statuses that distinguish evidence collection from review: `pending-evidence`, `pending-maintainer-review`, `accepted`, `rejected`, `blocked`, `deferred-approved-exception`, `rejected-redaction`, and `rejected-overclaim`.
- **D-05:** Generate a maintainer-readable checklist or summary from the row-level packets for review ergonomics, but keep the JSON packets and verifier as the source of truth.

### Final reference-demotion checklist

- **D-06:** Model final-demotion review as an evidence index plus maintainer decision packet rather than prose-only approval. The evidence index resolves Phase 13-17 and archived Phase 11 evidence; the decision packet records approve, reject, or exception decisions.
- **D-07:** The checklist must link CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence. It should also preserve source-backed local proof versus non-local supplied evidence and maintainer-only approval boundaries.
- **D-08:** `demotion_allowed` must be derived deterministically. It may be true only when every required criterion is `passed`, `exception-approved`, or validly `not-applicable`; any `pending`, `failed`, `blocked`, `exception-requested`, `exception-rejected`, redaction rejection, or overclaim rejection keeps demotion false.
- **D-09:** Approved exceptions must require scope, rationale, approver, affected printer/release surface, mitigation or follow-up, expiry or review trigger, and links to the Phase 13-17 or archived v1.0 evidence that justifies the exception.
- **D-10:** Do not implement a broad policy mini-engine in this phase. Keep the evaluator explicit, reviewable, and close to the row schema.

### Final readiness dossier

- **D-11:** Use the Phase 13-17 pattern: checked-in contracts, schemas, verifier logic, dry-run examples, Bazel labels, and `just phase18-verify`; generated run manifests, retained-code snapshots, residual-risk registers, redacted summaries, and readiness reports live under `build/ci-evidence/phase18`.
- **D-12:** The generated human-readable readiness report is review material, not the authority. The machine-readable gate rows and maintainer decision input determine final status.
- **D-13:** Generated Phase 18 artifacts should include a run manifest, normalized final-demotion results, retained-code acceptance summary, residual-risk register, redacted readiness report, source-contract snapshot, and maintainer decision input template.
- **D-14:** The verifier must reject secret leakage, raw firmware payloads, raw crash dumps, credential values, private keys/certificates, path traversal, stale or missing source refs, local-only proof overclaims, retained-code acceptance overclaims, and reference-demotion approval without maintainer decision input.

### Traceability and workflow integration

- **D-15:** Every Phase 18 row must map to `REV-01`, `REV-02`, and/or `REV-03`, plus the relevant archived v1.0 and Phase 11 evidence rows and the applicable Phase 13-17 contract rows.
- **D-16:** Add a dedicated Phase 18 standard-library Python verifier/collector, likely `tools/bazel/phase18_cutover_review.py`, with focused unit tests in `tools/bazel/phase18_cutover_review_test.py`.
- **D-17:** Expose Phase 18 through a checked-in contract manifest, Bazel `phase18_verify` and `phase18_verify_tests` labels, root docs/alias filegroups, `tools/bazel/rust_workflow.sh`, and `just phase18-verify`.
- **D-18:** Local phase verification should be deterministic: validate contract schema, required review rows, source refs, wiring, dry-run generated artifacts, redaction, path guards, approval/exception semantics, demotion computation, and overclaim guards without requiring real maintainer sign-off.
- **D-19:** Preserve Phase 13 artifact-retention, Phase 14 simulator, Phase 15 hardware, Phase 16 live-service, and Phase 17 release/signing boundaries. Supporting evidence can feed Phase 18, but none of those gates should be silently upgraded to final cutover approval.

### the agent's Discretion

- Exact packet IDs, schema field order, status spelling, generated artifact filenames, helper boundaries, and dry-run output shape are flexible if the result stays deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated implementation plan with multiple tasks; the roadmap expects one completed plan for this phase.
- Prefer explicit JSON contracts and verifier tests over prose-only checklists. Human-facing review text is useful only when backed by machine-readable rows and verifier checks.
- External assurance vocabulary such as VEX, SLSA, in-toto, or GSN can inform names or future exports, but Phase 18 should not add a new attestation trust root unless the existing repo evidence contract needs it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` - Phase 18 goal, dependencies, success criteria, and v1.1 roadmap position.
- `.planning/REQUIREMENTS.md` - `REV-01`, `REV-02`, and `REV-03` acceptance requirements.
- `.planning/STATE.md` - current milestone state, blockers, and Phase 18 starting point.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, safety, retained-code, and Bright Builds constraints.
- `.planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md` - CI evidence contract, artifact retention, and non-local proof boundaries.
- `.planning/phases/13-ci-evidence-orchestration/13-VERIFICATION.md` - passed Phase 13 verification boundary.
- `.planning/phases/14-simulator-evidence-gates/14-CONTEXT.md` - simulator evidence contract, dry-run artifact, and hardware/non-local proof boundaries.
- `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md` - passed Phase 14 verification boundary.
- `.planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md` - hardware evidence contract, operator metadata, residual risk, and non-release proof boundaries.
- `.planning/phases/15-hardware-safety-and-media-qualification/15-VERIFICATION.md` - passed Phase 15 verification boundary.
- `.planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md` - live-service evidence contract, redaction, and non-release proof boundaries.
- `.planning/phases/16-live-network-and-transfer-qualification/16-VERIFICATION.md` - passed Phase 16 verification boundary.
- `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md` - release-candidate evidence, signing/provenance, artifact comparison, and retained-code issue decisions.
- `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md` - passed Phase 17 verification boundary.

### Archived v1.0 cutover and retained-code evidence

- `.planning/milestones/v1.0-REQUIREMENTS.md` - archived v1.0 requirement surface that Phase 18 must not redefine.
- `.planning/milestones/v1.0-ROADMAP.md` - archived v1.0 phase history and evidence foundation.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` - v1.0 audit outcome and preserved non-local retained-code/final-demotion gates.
- `.planning/milestones/v1.0-phases/05-foreign-code-unsafe-and-runtime-boundary/05-VERIFICATION.md` - retained foreign-code, unsafe, board runtime, and FreeRTOS boundary proof.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md` - parity pyramid, retained-code, final demotion, requirement traceability, and overclaim decisions.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md` - passed Phase 11 local evidence boundary.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-CONTEXT.md` - metadata hygiene and no-overclaim constraints for archived evidence.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-VERIFICATION.md` - v1.0 archive-clean verification record.

### Existing verifier, manifest, and final-gate patterns

- `tools/bazel/phase17_release_candidate_evidence.py` - latest evidence verifier template for contracts, external input validation, generated artifacts, path guards, security scans, and wiring checks.
- `tools/bazel/phase17_release_candidate_evidence_test.py` - latest standard-library regression-test pattern for evidence contract behavior.
- `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` - checked-in contract schema, status vocabulary, release rows, source refs, and generated artifact shape to mirror.
- `tools/bazel/phase16_live_network_evidence.py` - live evidence verifier and external input validation pattern.
- `tools/bazel/phase15_hardware_evidence.py` - hardware/operator evidence verifier and residual risk pattern.
- `tools/bazel/phase14_simulator_evidence.py` - simulator evidence verifier and overclaim boundary pattern.
- `tools/bazel/phase13_ci_evidence.py` - CI evidence writer, artifact sanitizer, and retention pattern.
- `tools/bazel/phase11_verify.py` - aggregate cutover verifier, proof-scope taxonomy, retained non-local blocker pattern, and no-overclaim guard.
- `tools/bazel/phase11_verify_test.py` - Phase 11 verifier regression-test pattern.
- `tools/bazel/manifests/phase11_cutover_readiness.json` - reference-demotion criteria, known concern dispositions, and `demotion_allowed: false` precedent.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` - retained-code surface taxonomy and required evidence pattern.
- `tools/bazel/manifests/phase11_parity_pyramid.json` - proof-scope taxonomy and non-local gate layering.
- `tools/bazel/manifests/phase11_requirement_evidence.json` - requirement-to-evidence mapping pattern.
- `tools/bazel/manifests/phase11_reference_comparisons.json` - normalized comparison and mismatch reference pattern.
- `tools/bazel/manifests/phase13_ci_evidence_contract.json` - CI evidence rows that Phase 18 must link.
- `tools/bazel/manifests/phase14_simulator_evidence_contract.json` - simulator evidence rows that Phase 18 must link.
- `tools/bazel/manifests/phase15_hardware_evidence_contract.json` - hardware evidence rows that Phase 18 must link.
- `tools/bazel/manifests/phase16_live_network_evidence_contract.json` - live-service evidence rows that Phase 18 must link.
- `tools/bazel/BUILD.bazel` - Bazel shell_binary wiring for phase verifiers.
- `BUILD.bazel` - root docs filegroups and aliases.
- `tools/bazel/rust_workflow.sh` - Rust/phase verifier dispatch pattern.
- `justfile` - developer facade recipes and existing phase verification entrypoints.

### Retained-code source evidence and concerns

- `tools/bazel/manifests/foreign_code_inventory.json` - retained foreign-code inventory used by prior retained-code proof.
- `tools/bazel/manifests/unsafe_boundary_audit.json` - unsafe/runtime boundary audit used by prior retained-code proof.
- `.planning/codebase/CONCERNS.md` - retained-code, safety, TLS, crash dump, generated asset, transfer, and hardware fragility concerns that final review must keep visible.
- `.planning/codebase/INTEGRATIONS.md` - CI, artifact, signing, network, credential, storage, MMU, RS485, and service integration context.
- `.planning/codebase/TESTING.md` - repo-native test, simulator, CTest, pytest, and CI verification surfaces.
- `.planning/codebase/STRUCTURE.md` - source layout for retained HAL, RTOS, network, filesystem, resource, release, MMU, and auxiliary-controller surfaces.

### Repo and standards guidance

- `AGENTS.md` - repo-local GSD workflow and Bright Builds routing rules.
- `AGENTS.bright-builds.md` - managed Bright Builds workflow, sync, verification, and standards-routing rules.
- `standards-overrides.md` - confirms no active local Bright Builds override.
- `standards/core/architecture.md` - functional-core/imperative-shell and domain modeling guidance.
- `standards/core/code-shape.md` - early returns, `maybe_`, and size guidance.
- `standards/core/verification.md` - sync, hook, and pre-commit verification rules.
- `standards/core/testing.md` - focused unit-test and Arrange/Act/Assert expectations.
- `standards/languages/rust.md` - Rust standards if Phase 18 adds or changes Rust domain types.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase17_release_candidate_evidence.py` and `tools/bazel/phase17_release_candidate_evidence_test.py` provide the nearest complete template for Phase 18: contract validation, source-ref resolution, external input validation, generated quick artifacts, security scans, overclaim guards, Bazel wiring checks, and standard-library unit tests.
- `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` provides a current row-level evidence contract with statuses, required fields, source refs, expected artifacts, residual gates, and unsupported claims.
- `tools/bazel/manifests/phase11_cutover_readiness.json` already models final demotion as false until aggregate, non-local, retained-code, and maintainer evidence is attached.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` already lists retained HAL/CMSIS/vendor, Marlin/C++, generated assets, network/TLS/filesystem/release, MMU, RS485, toolchanger, and other surfaces that Phase 18 should convert into acceptance packets.
- Phase 13 through Phase 17 contracts provide the evidence rows and generated-output patterns that Phase 18 should link rather than duplicate.
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` already expose phase verifiers through the established Bazel and developer-command pattern.

### Established Patterns

- Checked-in JSON manifests define durable evidence contracts; generated run manifests, normalized outputs, redacted summaries, source snapshots, operator inputs, and review reports live under ignored `build/` paths.
- Phase verifiers use explicit constants for required IDs, required fields, source refs, generated output roots, forbidden markers, lifecycle IDs, status values, and wiring strings.
- Prior phases strictly separate local deterministic checks from simulator, hardware, live-service, release, signing, retained-code, and maintainer-review proof.
- Python verifier tests use stdlib `unittest`, temporary roots, explicit fixture writes/copies, `subprocess.run(..., shell=False)`, and Arrange/Act/Assert comments.
- Redaction and no-overclaim checks are first-class verification behavior, not prose guidance.

### Integration Points

- Add a Phase 18 cutover review contract under `tools/bazel/manifests/`.
- Add Phase 18 verifier/collector and tests under `tools/bazel/`.
- Add Bazel labels in `tools/bazel/BUILD.bazel`, root docs/alias filegroups in `BUILD.bazel`, dispatch cases in `tools/bazel/rust_workflow.sh`, and `just phase18-verify`.
- Use `.planning/phases/18-retained-code-acceptance-and-cutover-review/` for research, plan, summary, validation, verification, and lifecycle artifacts.
- Keep generated Phase 18 evidence under `build/ci-evidence/phase18/` or explicit `external://phase18/...` references.

</code_context>

<specifics>
## Specific Ideas

- Retained-code acceptance should be reviewable by humans through a generated checklist, but the machine-readable JSON packets and verifier should remain authoritative.
- The final readiness report should be useful for maintainers, but it must not become a stale checked-in prose claim of cutover readiness.
- Exceptions are allowed only as explicit maintainer decisions with scoped rationale and follow-up; silent pending gates keep reference demotion blocked.
- No specific visual or UI requirements were captured; this is an evidence-governance and verifier phase.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 18-retained-code-acceptance-and-cutover-review*
*Context gathered: 2026-06-20*
