---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 21-2026-06-21T16-02-06
generated_at: 2026-06-21T16:02:06.276Z
---

# Phase 21: Final Readiness Result Consumption - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 21 hardens Phase 18 final cutover review so final readiness consumes machine-readable upstream result manifests before any final reference-demotion criterion can pass. It closes the v1.1 audit gap where Phase 18 linked prior-phase contracts and accepted guarded decision refs without independently proving that upstream CI, simulator, hardware, live-service, release, retained-code, residual-risk, and maintainer-decision evidence results were present, schema-valid, lifecycle-valid, source-ref-valid, redaction-clean, and in an acceptable status.

This phase does not execute real simulator, hardware, live-service, release, or maintainer review evidence. It consumes result manifests from Phase 19 aggregate CI, Phase 20 release artifact production, and Phase 18 review inputs, and it keeps final demotion blocked when required result evidence is missing, failed, stale, rejected, or only exception-requested.

</domain>

<decisions>
## Implementation Decisions

### Upstream Result Authority

- **D-01:** Update the Phase 18 final review surface rather than creating a separate final-readiness policy engine. Phase 18 remains the authority for `demotion_allowed`, but Phase 21 adds upstream result consumption as a prerequisite for final criterion pass status.
- **D-02:** Add a machine-readable upstream result contract to Phase 18's checked-in review contract. Each final criterion that depends on upstream evidence should name its required result family, required manifest refs, acceptable statuses, freshness or lifecycle constraints, and redaction/source-ref expectations.
- **D-03:** Use Phase 19 aggregate CI result manifests for CI, simulator, hardware, live-service, and Phase 18 aggregate retention evidence. Use Phase 20 release result manifests for release-candidate artifact, signing, provenance, and comparison evidence. Retained-code, residual-risk, and maintainer-decision criteria continue to require Phase 18 decision input, but they must still appear in the final result summary with explicit upstream consumption state.
- **D-04:** The final review must not infer upstream pass status from contract rows, source refs, external URLs, or prose summaries. A decision ref can support human review, but only a validated upstream result manifest can satisfy upstream result proof.

### Gating Semantics

- **D-05:** `demotion_allowed` stays false when any required upstream result is missing, stale, malformed, has an unexpected lifecycle id, has unresolved source refs, contains redaction or overclaim failures, has `failed`, `blocked`, `pending-*`, `rejected-redaction`, or `rejected-overclaim` status, or is outside the approved artifact/ref root.
- **D-06:** Maintainer decisions may approve, reject, or exception a criterion only after the relevant upstream result rows have been validated. Approving a criterion with missing or failed upstream results should be rejected. Exception-approved or not-applicable decisions may coexist with non-passing upstream result rows only when the exception metadata explicitly cites the affected upstream result and mitigation.
- **D-07:** Generated final-demotion rows should carry both maintainer decision status and upstream result status. A final criterion passes only when the decision status allows cutover and every required upstream result is acceptable or covered by a valid exception.
- **D-08:** Redaction and overclaim failures are hard blockers. They cannot be converted to ordinary pass claims by maintainer decision input; they require corrected upstream artifacts or an explicit exception status that still keeps `demotion_allowed` false unless policy allows that exact exception outcome.

### Input and Artifact Model

- **D-09:** Add an explicit upstream result input path to the Phase 18 verifier, likely `--upstream-results`, rather than overloading `--decision-input` evidence refs. The input should be a repo-relative JSON packet under an ignored evidence directory or a validated external ref converted into machine-readable rows by the caller.
- **D-10:** The upstream result input should normalize each consumed row with criterion id, evidence family, owning phase, manifest path or external ref, source lifecycle id, status, failure reason, artifact refs, redaction status, source-ref validation result, generated-at timestamp if available, and covered requirement IDs.
- **D-11:** Quick mode without upstream results should continue to generate a deterministic blocked readiness report, but the report must now explain that upstream result evidence is missing. Quick mode with upstream results should write an upstream-result-consumption artifact and thread those statuses into `run-manifest.json`, `normalized-final-demotion-results.json`, and the redacted readiness report.
- **D-12:** Keep generated outputs under `build/ci-evidence/phase18` or an explicitly supplied output dir. Do not commit generated result manifests, logs, raw evidence, release payloads, crash dumps, credentials, tokens, certificates, signing keys, or private operator data.

### Traceability and Verification

- **D-13:** Add focused regression tests that prove approved maintainer decision input cannot make `demotion_allowed` true without valid upstream result manifests.
- **D-14:** Add tests for missing upstream result input, failed upstream result status, stale or wrong lifecycle id, redaction failure, path traversal/out-of-root refs, and exception-approved criteria that cite non-passing upstream results.
- **D-15:** Preserve existing Phase 18 contract-only, quick, security-only, and wiring-only modes. Extend them narrowly rather than refactoring the large Phase 18 verifier wholesale.
- **D-16:** Update planning, verification, and generated artifacts so REV-02 and REV-03 explicitly depend on machine-readable result consumption, not on contract/source row linkage alone.

### the agent's Discretion

- Exact JSON field names, helper function boundaries, acceptable-status vocabulary details, and artifact filenames are flexible if the result remains deterministic, source-backed, redacted, traceable, and hard to overclaim.
- Prefer a narrow Phase 18 verifier/contract extension plus tests over a new standalone verifier unless implementation evidence shows a separate module is materially cleaner.
- Keep current no-overclaim behavior intact: missing real external evidence should block final readiness, not become a local pass.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and audit gap

- `.planning/ROADMAP.md` - Phase 21 goal, dependency, success criteria, and gap-closure text.
- `.planning/REQUIREMENTS.md` - `REV-02` and `REV-03` final review requirements.
- `.planning/STATE.md` - current milestone state and Phase 21 starting point.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, safety, and no-overclaim constraints.
- `.planning/v1.1-MILESTONE-AUDIT.md` - audit finding that Phase 18 final review consumes contracts and decision refs rather than upstream result manifests.

### Prior phase decisions and verification

- `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-CONTEXT.md` - Phase 18 final review, demotion guard, retained-code, and decision-input model.
- `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VERIFICATION.md` - passed Phase 18 local verification and upstream result-manifest gap.
- `.planning/phases/19-aggregate-cutover-evidence-ci/19-CONTEXT.md` - aggregate Phase 14-18 evidence retention, status reporting, and no-overclaim model.
- `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md` - passed Phase 19 verification and generated aggregate evidence behavior.
- `.planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md` - Phase 20 release result manifest authority and final-review handoff.
- `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md` - passed Phase 20 verification and Phase 20 result manifest behavior.

### Existing code and contracts

- `tools/bazel/phase18_cutover_review.py` - final review verifier, decision input validation, demotion computation, generated readiness artifacts, redaction, and no-overclaim guards.
- `tools/bazel/phase18_cutover_review_test.py` - existing Phase 18 regression tests for decision input, demotion guard, generated artifact security, and wiring.
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - final criterion rows, retained-code packets, allowed demotion statuses, decision schema, source refs, and generated artifact list.
- `tools/bazel/phase19_aggregate_ci_evidence.py` - aggregate CI runner that writes retained Phase 14-18 local verifier outputs, observed statuses, external-input placeholders, and aggregate run manifest.
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - aggregate evidence contract, expected artifacts, external pending statuses, and artifact retention paths.
- `tools/bazel/phase20_release_candidate_artifacts.py` - release result manifest writer, release input validation, signing/provenance/comparison checks, and generated Phase 20 artifacts.
- `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` - release rows, proof classes, acceptable status vocabulary, required outputs, release input schema, and Phase 20 output root.
- `tools/bazel/manifests/phase20_release_environment_inputs.template.json` - release-environment input template for approved release evidence.
- `tools/bazel/BUILD.bazel` - Phase 18-20 verifier labels, source-ref manifest filegroups, and release identity wiring.
- `BUILD.bazel` - root docs/verification facade pattern.
- `tools/bazel/rust_workflow.sh` - phase verifier dispatch pattern.
- `justfile` - `phase18-verify`, `phase19-verify`, and `phase20-verify` developer facade recipes.

### Standards and repo guidance

- `AGENTS.md` - repo-local GSD workflow and Bright Builds routing rules.
- `AGENTS.bright-builds.md` - managed Bright Builds sync, verification, and standards-routing rules.
- `standards-overrides.md` - confirms no active local Bright Builds override.
- `standards/core/architecture.md` - functional-core/imperative-shell and domain modeling guidance.
- `standards/core/code-shape.md` - early returns, `maybe_`, and size guidance.
- `standards/core/verification.md` - sync, hook, and pre-commit verification rules.
- `standards/core/testing.md` - focused unit-test and Arrange/Act/Assert expectations.
- `standards/languages/rust.md` - Rust standards if Rust domain surfaces are touched.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase18_cutover_review.py` already centralizes final criteria, maintainer decision input validation, demotion computation, generated readiness artifacts, and generated overclaim guards. This is the smallest authoritative place to add upstream result consumption.
- `tools/bazel/phase18_cutover_review_test.py` already has helpers for complete maintainer decision input and tests proving demotion stays false without valid decisions; those helpers can be extended with upstream result fixtures.
- `tools/bazel/phase19_aggregate_ci_evidence.py` writes `build/ci-evidence/phase19/run-manifest.json` with observed source statuses, external pending rows, local failed rows, and retained artifact paths.
- `tools/bazel/phase20_release_candidate_artifacts.py` writes `build/ci-evidence/phase20/release-result-manifest.json`, `normalized-release-results.json`, redacted signing/provenance summaries, and comparison classification outputs.
- `tools/bazel/manifests/phase18_cutover_review_contract.json` already has final criterion IDs and evidence families that can map to required upstream result families without inventing a new final readiness vocabulary.

### Established Patterns

- Prior phase verifiers use explicit constants for required IDs, status vocabularies, source refs, output roots, lifecycle ids, generated artifacts, and forbidden markers.
- Checked-in JSON contracts are the source of truth; generated result manifests stay ignored under `build/ci-evidence/phaseXX`.
- Local deterministic verification validates contracts, wiring, generated quick artifacts, redaction, and overclaim boundaries; it does not turn missing external evidence into pass status.
- Python tests use standard-library `unittest`, temp repo roots, explicit fixture copying/writes, and clear Arrange/Act/Assert comments.

### Integration Points

- Extend `tools/bazel/manifests/phase18_cutover_review_contract.json` with upstream result requirements and generated upstream-consumption artifact names.
- Extend `tools/bazel/phase18_cutover_review.py` with upstream result input parsing, validation, normalization, demotion gating, generated artifact output, and security scans.
- Extend `tools/bazel/phase18_cutover_review_test.py` with positive and negative upstream result cases.
- Update Phase 18 docs/planning artifacts for Phase 21 lifecycle.
- Keep generated evidence under `build/ci-evidence/phase18` or a caller-supplied subdirectory.

</code_context>

<specifics>
## Specific Ideas

- The generated readiness report should let maintainers answer: which final criterion is blocked, which upstream manifest or row caused it, which requirement IDs are affected, whether the result was missing/failed/pending/stale/redaction-failed, and which evidence refs were retained.
- The final review should clearly distinguish "decision input is complete" from "upstream result evidence is valid." Both must be true before demotion can be allowed.
- Release evidence should prefer Phase 20 result manifests rather than the older Phase 17 release contract rows, because Phase 20 exists specifically to replace the empty release identity with real release-environment result evidence.
- Phase 19 aggregate evidence can remain pending for real external inputs; Phase 21's job is to consume that pending/blocked state honestly and prevent final pass claims.

</specifics>

<deferred>
## Deferred Ideas

- Reconcile requirement checkboxes, validation metadata, roadmap progress, and milestone audit state after this functional gap closes in Phase 22.
- Broader refactoring of oversized Phase 18/20 verifier files remains non-blocking maintainer debt unless the Phase 21 change becomes unmanageably tangled.

</deferred>

---

*Phase: 21-final-readiness-result-consumption*
*Context gathered: 2026-06-21*
