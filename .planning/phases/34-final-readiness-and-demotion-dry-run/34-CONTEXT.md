---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 34-2026-07-25T18-18-48
generated_at: 2026-07-25T18:18:48.752Z
---

# Phase 34: Final Readiness and Demotion Dry Run - Context

**Gathered:** 2026-07-25
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 34 generates a final readiness packet from the real, sanitized evidence and decision rows consumed by Phases 31 through 33. It proves that every required row is accounted for, that blocking conditions remain fail-closed unless covered by an exact valid decision, and that the reference-demotion dry run opens only when readiness is otherwise unblocked and a separate explicit demotion approval is valid.

The phase does not collect or reclassify evidence, create maintainer decisions, publish the Phase 35 cutover verdict, or perform production reference demotion.

</domain>

<decisions>
## Implementation Decisions

### Readiness Packet Lineage and Coverage
- **D-01:** Build a contract-driven coverage ledger over the Phase 31 final-intake boundary, Phase 32 blocker register and classifications, and Phase 33 decision handoff.
- **D-02:** Derive the expected evidence set from Phase 31 accepted-final receipts and their consumed row references. Do not derive completeness from Phase 32 alone because Phase 32 intentionally omits clean passed rows.
- **D-03:** Join Phase 32 classifications and Phase 33 decisions through exact stable row references and affected-gate scope. Missing, duplicate, dangling, stale, malformed, redaction-failed, source-ref-failed, secret-tainted, lifecycle-mismatched, unknown, underclassified, or uncovered entries must block readiness.
- **D-04:** Preserve every consumed row's requirement ids, proof eligibility, evidence and artifact refs, blocker state, exception coverage, retained-code decision, residual-risk decision, and readiness effect in the generated ledger.
- **D-05:** Generate the human-readable readiness report from the same canonical ledger as the JSON packet so prose cannot drift from machine-readable gate results.

### Reference-Demotion Dry-Run Semantics
- **D-06:** Model readiness and reference-demotion approval as orthogonal predicates. The dry run is `open` only when readiness is `unblocked`, the demotion input is valid, and the explicit decision value is `approve`.
- **D-07:** Missing, malformed, stale, lifecycle-mismatched, rejected, or otherwise invalid demotion input must produce a durable `blocked` dry-run artifact. A verifier error alone is not an adequate blocked result.
- **D-08:** The dry-run artifact must retain separate readiness state, approval-validation state, approval-decision state, aggregate gate state, stable reason codes, and source refs so multiple simultaneous blockers remain visible.
- **D-09:** Green evidence, accepted retained code, approved exceptions, accepted residual risk, or a readiness approval must never imply demotion approval.
- **D-10:** This phase proves authorization logic only. It must not mutate reference code, build defaults, production branches, or release policy.

### Phase 34 Implementation Boundary
- **D-11:** Implement a new Phase 34 contract, verifier, regression test suite, Bazel targets, workflow case arms, and `just phase34-verify` facade that consume the Phase 33 downstream handoff under `build/ci-evidence/phase33`.
- **D-12:** Keep Phase 28 unchanged as a semantic precedent and regression oracle. Do not adapt Phase 33 rows into Phase 28's Phase 26/27-shaped criteria or create dual readiness authorities.
- **D-13:** Write Phase 34 generated outputs under `build/ci-evidence/phase34`, including a final readiness packet, coverage ledger, blocker/coverage summary, demotion dry-run result, run manifest, redacted report, contract snapshots, and any safe input template needed for local verification.
- **D-14:** Keep aggregation and gate evaluation as pure data transformations where practical, with filesystem loading, validation, security scanning, and artifact writing in the imperative shell.
- **D-15:** The default or quick verification path must remain visibly blocked and must not synthesize maintainer approval. Tests should also exercise an isolated valid-input fixture that proves the open conjunction without changing repository defaults.

### the agent's Discretion
- The agent may choose exact JSON filenames and internal helper boundaries as long as there is one canonical coverage ledger and one canonical demotion dry-run result.
- The agent may choose stable reason-code spellings, provided every fail-closed condition is explicit in the contract and covered by focused tests.
- The agent may choose whether contract snapshots are copied by a shared helper or directly by the Phase 34 verifier.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements
- `.planning/PROJECT.md` — v1.3 cutover approval trial scope, explicit demotion boundary, and out-of-scope production actions.
- `.planning/REQUIREMENTS.md` — READY-01 through READY-03 and Phase 35 downstream requirements.
- `.planning/ROADMAP.md` — Phase 34 goal, success criteria, dependency, and milestone sequencing.
- `.planning/STATE.md` — Current milestone state, active blockers, and external evidence constraints.

### v1.3 Upstream Boundaries
- `.planning/phases/31-final-evidence-intake/31-CONTEXT.md` — Accepted-final receipt and real evidence provenance boundary.
- `.planning/phases/31-final-evidence-intake/31-01-SUMMARY.md` — Delivered Phase 31 files and workflow behavior.
- `.planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md` — Canonical blocker taxonomy, proof eligibility, and triage handoff rules.
- `.planning/phases/32-blocker-register-and-evidence-triage/32-01-SUMMARY.md` — Delivered Phase 32 register and generated artifact behavior.
- `.planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md` — Explicit independent decision axes and Phase 34 handoff boundary.
- `.planning/phases/33-maintainer-decision-inputs/33-01-SUMMARY.md` — Delivered Phase 33 contract, verifier, tests, and workflow wiring.
- `tools/bazel/manifests/phase31_final_evidence_intake_contract.json` — Final-intake receipts, lifecycle, accepted/rejected output contract, and source refs.
- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` — Blocker rows, proof eligibility, problem kinds, and downstream registers.
- `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` — Readiness and demotion handoff schema plus independent decision vocabulary.
- `tools/bazel/phase33_maintainer_decision_inputs.py` — Current Phase 34 handoff producer and fail-closed decision validation.
- `tools/bazel/phase33_maintainer_decision_inputs_test.py` — Regression examples for the upstream decision and handoff states.

### Readiness and Demotion Precedent
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md` — Prior readiness and explicit-demotion decisions.
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-01-SUMMARY.md` — Prior generated readiness artifacts and verification behavior.
- `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` — Existing fail-closed readiness and demotion policy vocabulary.
- `tools/bazel/phase28_final_readiness_packet.py` — Prior two-axis readiness and demotion evaluator to use as a semantic precedent, not a mutable dependency.
- `tools/bazel/phase28_final_readiness_packet_test.py` — Existing blocker, exception, readiness, demotion, and security regression cases.

### Build and Workflow Wiring
- `tools/bazel/BUILD.bazel` — Phase verifier/test target and data dependency patterns.
- `BUILD.bazel` — Root phase aliases and planning-doc filegroups.
- `tools/bazel/rust_workflow.sh` — Phase orchestration case-arm patterns.
- `justfile` — Developer-facing phase verification facade.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase33_maintainer_decision_inputs.py`: Reuse its Phase 32 handoff loading, exact row-reference validation, approved-exception coverage, accepted residual-risk coverage, readiness handoff, and demotion handoff concepts.
- `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json`: Treat its generated handoff artifacts and independent decision axes as the authoritative Phase 34 input contract.
- `tools/bazel/phase28_final_readiness_packet.py`: Reuse policy vocabulary and test ideas for hard-blocker precedence, explicit demotion approval, security scans, redacted reports, and generated-output validation without modifying the file.
- Existing Phase 31-33 verifier tests: Reuse fixture and focused `unittest` patterns for contracts, lifecycle mismatches, unsafe refs, prohibited markers, generated artifacts, and wiring.

### Established Patterns
- Evidence and decision phases use Python standard-library verifier scripts, JSON contracts, script-local regression tests, Bazel `sh_binary` targets, root aliases, `rust_workflow.sh` arms, and `just` facades.
- Quick/default verification paths generate blocked or template-only artifacts and never claim real maintainer authorization.
- Secret, unsafe-ref, path-root, lifecycle, and overclaim checks run before generated outputs are trusted downstream.
- Machine-readable artifacts are authoritative; redacted Markdown reports are derived audit views.

### Integration Points
- Phase 34 consumes `build/ci-evidence/phase33/downstream-handoff-manifest.json` and the safe artifacts referenced by that manifest.
- Phase 34 outputs feed Phase 35's cutover decision artifact with readiness state, demotion dry-run state, blockers, exceptions, residual risks, retained-code decisions, and exact source refs.
- Bazel and `just` verification must regenerate prerequisite quick artifacts deterministically while preserving their blocked status.

</code-context>

<specifics>
## Specific Ideas

- Prefer a row-complete coverage ledger plus a compact top-level packet, rather than flattening the result into only criterion-level status.
- Emit a durable blocked dry-run JSON result even when the explicit demotion input is malformed or stale, while retaining a nonzero verifier result when appropriate.
- Keep a single human-readable report derived from the packet and ledger, with blocked/open headline plus every failed predicate and reason code.

</specifics>

<deferred>
## Deferred Ideas

- The approved, blocked, or approved-with-exceptions cutover verdict and next-milestone routing belong to Phase 35.
- Production reference demotion belongs to POST-01 after an approved v1.3 cutover decision.
- Content-addressed provenance graphs, attestation signing, retained vendor/HAL replacement, long-run dashboards, and expanded printer behavior remain future work.

</deferred>

*Phase: 34-final-readiness-and-demotion-dry-run*
*Context gathered: 2026-07-25*
