---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 26-2026-06-24T13-36-46
generated_at: 2026-06-24T13:36:46.286Z
---

# Phase 26: Release, Signing, and Upstream Result Evidence - Context

**Gathered:** 2026-06-24
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 26 executes the release/signing/provenance evidence path and makes upstream cutover gate result rows maintainable for review. It should let release managers supply secret-safe release-environment evidence for firmware artifacts, signing identity, provenance, comparison references, and retention metadata, then let maintainers inspect normalized upstream rows for every required cutover gate.

This phase does not redefine the v1.0 parity contracts, does not repeat simulator, hardware/media/safety, or live-service evidence execution, does not approve retained-code or residual-risk decisions, and does not allow final reference demotion. It turns release evidence and upstream result row validation into a secret-safe, machine-readable handoff for Phase 27 retained-code/decision work and Phase 28 final readiness.

</domain>

<decisions>
## Implementation Decisions

### Release Evidence Input Model
- **D-01:** Treat `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json`, `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`, and `tools/bazel/manifests/phase20_release_environment_inputs.template.json` as the canonical release/signing/provenance sources. Phase 26 may add a v1.2 execution wrapper/schema, but it must not silently redefine the Phase 17 or Phase 20 release row IDs.
- **D-02:** Require every Phase 20 release evidence row to be represented by the release-manager input packet. Missing, duplicate, unknown, or row-ID-drifted release evidence must fail validation or remain blocked.
- **D-03:** Accept release evidence as sanitized release metadata plus artifact references, not raw firmware payloads, signing payload bytes, private keys, private certificates, credentials, raw logs, or binary dumps.
- **D-04:** Passed release rows require artifact digests, build input identity, signing identity reference, provenance references, comparison references, retention references, verification outcome, operator, timestamp, and release run identity where the source contract requires those fields.

### Signing, Provenance, and Secret Handling
- **D-05:** Signing identity is reference-only: key fingerprint, signing authority, certificate chain reference, or external release key evidence may be retained, but private key material, raw key bytes, signing payload bytes, and credential values must be rejected.
- **D-06:** Treat `approved-release-run` and `external-release-key-evidence` as eligible proof classes for pass status. `template-only`, `local-smoke`, `pending-release-input`, `release-run-required`, `external-signing-required`, and `blocked-signing-key-unavailable` must not pass without explicit exception metadata.
- **D-07:** Reject or block secret-tainted evidence before writing retained outputs. Redaction failure is a hard blocker and cannot be converted into a normal exception approval.
- **D-08:** Keep release proof distinct from simulator, hardware/media/safety, live-service, retained-code, residual-risk, final readiness, and demotion approval. Release pass status must not imply those other gates are accepted.

### Upstream Result Row Coverage
- **D-09:** Treat `tools/bazel/manifests/phase18_cutover_review_contract.json` as the canonical upstream result requirement list for final cutover gate rows.
- **D-10:** Phase 26 should produce or validate upstream rows for every required gate family: CI, simulator, hardware/media/safety, live-service, release/signing, retained-code, residual-risk, maintainer-decision/final-readiness, and reference-demotion status where the Phase 18 contract expects a row.
- **D-11:** Every upstream row must name requirement IDs, owning phase or gate, source lifecycle ID or lifecycle status, evidence family, criterion ID, evidence refs, artifact refs, status, failure reason, redaction status, source-ref status, exception status, maintainer state, and generated timestamp.
- **D-12:** Missing, stale, lifecycle-mismatched, source-ref-invalid, failed, blocked, secret-tainted, schema-invalid, or overclaiming rows remain blocked until corrected or explicitly exception-approved where the source contract allows exceptions.
- **D-13:** Retained-code acceptance, residual-risk review, maintainer-decision, and reference-demotion rows can be present as blocked, pending, or not-required scaffolding for later phases, but Phase 26 must not approve those decisions.

### Retained Outputs and Integration
- **D-14:** Retained Phase 26 outputs should live under `build/ci-evidence/phase26`, following the Phase 23-25 execution conventions.
- **D-15:** Store a normalized release evidence summary, upstream result row table, release run manifest, redaction/provenance summary, source contract snapshot or refs, operator input template, artifact reference summary, and machine-readable upstream result manifest for later acceptance phases.
- **D-16:** Keep generated evidence under ignored build output directories. Repo-tracked artifacts should be source contracts, input templates, verifier code, tests, Bazel/just wiring, and GSD planning artifacts.

### Verification
- **D-17:** Add Phase 26 verification as a narrow extension around existing Bazel/Python evidence tooling, with root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring consistent with Phases 20, 23, 24, and 25.
- **D-18:** Include focused Python tests for release row coverage, status/proof-class normalization, signing identity redaction, artifact digest requirements, provenance/comparison/retention metadata, upstream row schema, exception eligibility, stale/lifecycle/source-ref blockers, secret/overclaim guards, retained output writing, and wiring checks.
- **D-19:** Phase 26 quick verification should pass from checked-in safe fixtures and blocked placeholders while clearly distinguishing fixture/template evidence from real release-environment proof.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 26 release input template, release evidence manifest, upstream result manifest, normalized summaries, and row table, provided the names are explicit, tested, and stable for Phases 27 and 28.
- Decide whether Phase 26 should be one cohesive verifier or a thin orchestrator around Phase 20 plus a separate upstream-row validator. Prefer the smallest design that keeps release evidence and upstream row validation clear.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless research finds a real dependency split.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 26 Scope
- `.planning/ROADMAP.md` - Phase 26 goal, success criteria, dependency, and active milestone scope.
- `.planning/REQUIREMENTS.md` - EVID-04 and ACPT-01 requirements and v1.2 traceability table.
- `.planning/PROJECT.md` - Current milestone posture, non-local evidence constraints, release proof decisions, and demotion blocking decisions.
- `.planning/phases/23-simulator-evidence-execution/23-CONTEXT.md` - Prior decision that simulator proof remains separate and emits upstream-consumable rows.
- `.planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md` - Prior decision that hardware/media/safety proof remains separate and emits upstream-consumable rows.
- `.planning/phases/25-live-service-evidence-execution/25-CONTEXT.md` - Prior decision that live-service proof remains separate and emits upstream-consumable rows.

### Release and Signing Source Contracts
- `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` - v1.1 release candidate artifact/signing gate rows, release input schema, release workflow identity, artifact outputs, proof scopes, and secret/overclaim boundaries.
- `tools/bazel/phase17_release_candidate_evidence.py` - Existing Phase 17 release evidence verifier and guard behavior.
- `tools/bazel/phase17_release_candidate_evidence_test.py` - Test patterns for release evidence schema, artifacts, signing, provenance, and redaction.
- `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` - Phase 20 release production contract, row metadata requirements, proof classes, status vocabulary, and output-root policy.
- `tools/bazel/manifests/phase20_release_environment_inputs.template.json` - Current release-manager input template and row shape for pending release evidence.
- `tools/bazel/phase20_release_candidate_artifacts.py` - Phase 20 verifier, retained result writer, release input validation, secret guards, and no-overclaim checks.
- `tools/bazel/phase20_release_candidate_artifacts_test.py` - Test patterns for release input acceptance, failed/blocked release rows, output-root containment, redaction, and wiring.

### Upstream Result and Final Review Consumers
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - Canonical upstream result requirement list, required row fields, status vocabularies, exception-coverable statuses, hard blockers, and final demotion constraints.
- `tools/bazel/phase18_cutover_review.py` - Final review upstream-row consumption, exception coverage, demotion blocking, redaction/overclaim policy, and row validation behavior.
- `tools/bazel/phase18_cutover_review_test.py` - Test patterns for upstream result manifests, exception handling, and demotion blocking.
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - Aggregate cutover gate model and external-input placeholders for evidence families.
- `tools/bazel/phase19_aggregate_ci_evidence.py` - Aggregate evidence retention, upstream gate placeholder behavior, and run manifest style.
- `tools/bazel/phase23_simulator_evidence_execution.py` - v1.2 simulator execution pattern for retained outputs and upstream result row generation.
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` - v1.2 hardware/media/safety execution pattern for retained outputs and upstream result row generation.
- `tools/bazel/phase25_live_service_evidence_execution.py` - v1.2 live-service execution pattern for retained outputs and upstream result row generation.

### Build and Workflow Wiring
- `BUILD.bazel` - Root filegroups and aliases for phase evidence docs and verification labels.
- `tools/bazel/BUILD.bazel` - Evidence verifier targets, data dependencies, and shell binary wiring.
- `tools/bazel/rust_workflow.sh` - Dispatch cases for phase verification commands.
- `justfile` - Developer-facing phase verification recipes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase20_release_candidate_artifacts.py` already validates release candidate artifact rows, release input metadata, proof classes, approved release-run evidence, artifact refs, digests, signing identity refs, provenance refs, comparison refs, retention refs, output roots, and secret/overclaim guards.
- `tools/bazel/manifests/phase20_release_environment_inputs.template.json` already provides pending release-manager evidence rows that can become the Phase 26 input model seed.
- `tools/bazel/manifests/phase18_cutover_review_contract.json` already names the upstream result families, required row fields, acceptable statuses, exception-coverable statuses, and hard blockers that Phase 26 should surface for maintainers.
- `tools/bazel/phase18_cutover_review.py` already consumes upstream result rows to block demotion when rows are missing, failed, stale, redaction-failed, source-ref-invalid, or not exception-covered.
- `tools/bazel/phase23_simulator_evidence_execution.py`, `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`, and `tools/bazel/phase25_live_service_evidence_execution.py` already show the v1.2 execution pattern for wrapping v1.1 source contracts with real evidence submission, retained output writing, blocked quick placeholders, and upstream rows.

### Established Patterns
- Phase evidence tools are Python scripts under `tools/bazel/`, with matching `*_test.py` unit tests, manifest JSON under `tools/bazel/manifests/`, Bazel shell targets, root aliases, `rust_workflow.sh` dispatch, and a `just phaseXX-verify` facade.
- Evidence output roots use `build/ci-evidence/phaseXX`, keep generated artifacts out of source control, and retain safe planning/source manifests in the repo.
- Existing verification favors fail-closed schema checks, complete scenario/row coverage, explicit source refs, repo-relative or `external://phaseXX/` artifact refs, secret redaction, and phrase-based guards against non-local proof overclaims.
- Previous v1.2 phases let quick/local verification pass only by writing blocked placeholders and safe summaries, never by pretending external evidence was supplied.

### Integration Points
- Phase 26 should add new Bazel/just labels without breaking existing Phase 17, 18, 19, 20, 23, 24, or 25 labels.
- Phase 27 needs Phase 26 upstream rows to separate release evidence status from retained-code decisions and residual-risk acceptance.
- Phase 28 needs Phase 26 output manifests to assemble final readiness without allowing automatic reference demotion.
- `.planning/phases/26-release-signing-and-upstream-result-evidence/` owns Phase 26 lifecycle artifacts, while generated evidence remains under ignored build output directories.

</code_context>

<specifics>
## Specific Ideas

No user-supplied examples beyond the v1.2 roadmap. Use the Phase 20 release artifact verifier and the Phase 23-25 v1.2 evidence-execution wrappers as concrete models.

</specifics>

<deferred>
## Deferred Ideas

- Retained-code acceptance, residual-risk rationale, exception approval, and maintainer final decision inputs belong to Phase 27.
- Final cutover readiness packet generation, default blocked readiness, and explicit reference-demotion approval belong to Phase 28.
- Automatic reference demotion remains out of scope unless maintainers explicitly approve it in the final readiness phase.

</deferred>

---

*Phase: 26-release-signing-and-upstream-result-evidence*
*Context gathered: 2026-06-24*
