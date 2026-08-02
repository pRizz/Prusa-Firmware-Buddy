---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 37-2026-07-26T06-52-46
generated_at: 2026-07-26T07:00:07.736Z
---

# Phase 37: Reconcile Decisions Into Readiness - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 37 joins the canonical Phase 32 decision-domain blocker population with explicit Phase 33 retained-code, residual-risk, exception, and readiness decisions so Phase 34 can generate an unblocked readiness packet from complete valid inputs.

The phase does not reclassify evidence, create a new maintainer-decision vocabulary, publish the Phase 35 cutover verdict, repair stale-authority replacement across the full workflow, or perform reference demotion. Those responsibilities remain with the existing Phase 31-36 boundaries and Phase 38.

</domain>

<decisions>
## Implementation Decisions

### Canonical readiness ledger population

- **D-01:** Build Phase 34's canonical ledger as a dual-source typed union. Phase 31 remains the evidence-completeness and accepted-final provenance authority, while Phase 32 canonical Phase 27/28 decision-domain rows become first-class ledger rows rather than exceptional dangling blockers.
- **D-02:** Keep evidence rows and decision-domain rows on explicit evaluation paths within one canonical ledger. Do not reconstruct clean evidence from Phase 32, double-count subjects, or promote Phase 32 above Phase 31's finality boundary.
- **D-03:** Preserve each decision-domain row's immutable canonical `row_id`, `decision_axis`, `decision_subject_id`, source lineage, proof eligibility, and blocker classification in the ledger and all derived JSON/Markdown outputs.

### Exact typed decision resolution

- **D-04:** Normalize each Phase 33 decision target as an explicit per-reference typed binding containing `row_ref`, `decision_axis`, and `decision_subject_id`.
- **D-05:** Resolve a binding only when all three identity fields exactly match one canonical Phase 32 row. Gate names, stream names, paths, prefixes, similar subjects, or other fallback keys must never resolve a row.
- **D-06:** A decision may target multiple rows only by enumerating each typed binding explicitly. Every binding must match exactly once; missing, duplicate, colliding, mismatched, stale, malformed, or conflicting bindings remain visible blockers.
- **D-07:** Apply axis-specific decision semantics. Only the valid approving value for the row's axis may clear that row. Rejected retained code, rejected residual risk, rejected exceptions, and readiness `block` decisions stay linked and blocking.
- **D-08:** Readiness and reference-demotion authorization remain orthogonal. Phase 37 may reconcile demotion-domain identity without allowing evidence, readiness, retained-code acceptance, residual-risk acceptance, or approved exceptions to imply demotion approval.

### Integrated approved-path regression boundary

- **D-09:** Add a dedicated Phase 31-through-34 producer-chain integration regression that uses actual Phase 31, Phase 32, and Phase 33 producer outputs and exercises Phase 34's real loading, evaluation, and publication boundary.
- **D-10:** The valid baseline must reach Phase 34 `readiness_state: unblocked` only when all required evidence and exact typed decisions are valid.
- **D-11:** Derive focused one-concern negative cases from the same baseline for uncovered rows, row-reference mismatch, decision-axis mismatch, decision-subject mismatch, stale lifecycle data, invalid decision values, duplicate bindings, and conflicting decisions. Every case must remain blocking with specific diagnostics.
- **D-12:** Stop Phase 37 integration coverage at the Phase 34 authoritative readiness artifacts. Full Phase 31-35 workflow approval, durable stale-authority replacement, and cutover routing remain Phase 38 scope.

### the agent's Discretion

- Choose the smallest clear helper/module split for typed ledger rows, target-binding parsing, exact join validation, and axis-specific evaluation.
- Choose whether Phase 33 emits typed bindings directly or a Phase 34 boundary adapter normalizes the existing clear-text tuple, provided schema ownership is explicit and no opaque-only resolution key is introduced.
- Choose exact reason-code spellings and report layout while preserving stable, specific, fail-closed diagnostics.
- Reuse existing real-producer fixture helpers where practical, but keep the Phase 31-34 integration test readable and keep each negative test focused on one concern.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and audit gap

- `.planning/PROJECT.md` — v1.3 cutover-approval scope, explicit demotion boundary, and out-of-scope production actions.
- `.planning/REQUIREMENTS.md` — `DECIDE-01`, `DECIDE-02`, and `READY-01` acceptance requirements.
- `.planning/ROADMAP.md` — Phase 37 goal, dependency, gap-closure scope, and success criteria.
- `.planning/STATE.md` — Current fail-closed, evidence-sanitization, and authority decisions.
- `.planning/v1.3-MILESTONE-AUDIT.md` — Integration gap B1 and the broken complete-approved path Phase 37 must close.

### Upstream identity and decision boundaries

- `.planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md` — Independent maintainer-decision axes and Phase 34 handoff rules.
- `.planning/phases/33-maintainer-decision-inputs/33-01-SUMMARY.md` — Delivered Phase 33 artifacts and workflow behavior.
- `.planning/phases/36-normalize-evidence-and-blocker-rows/36-CONTEXT.md` — Immutable source identity, separate decision identity, and exact matching decisions.
- `.planning/phases/36-normalize-evidence-and-blocker-rows/36-01-SUMMARY.md` — Producer normalization core and canonical identity implementation.
- `.planning/phases/36-normalize-evidence-and-blocker-rows/36-02-SUMMARY.md` — Fail-closed Phase 27/28 container normalization.
- `.planning/phases/36-normalize-evidence-and-blocker-rows/36-VERIFICATION.md` — Passed real-producer and canonical-identity evidence.
- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` — Canonical blocker source and decision-identity fields.
- `tools/bazel/phase32_blocker_normalization.py` — Pure canonical row and decision identity construction.
- `tools/bazel/phase32_blocker_register_triage.py` — Real Phase 27/28 normalization and Phase 32 handoff publication.
- `tools/bazel/phase32_blocker_register_triage_test.py` — Existing real-producer fixture and fail-closed regression patterns.
- `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` — Current Phase 33 decision schema and handoff contract.
- `tools/bazel/phase33_maintainer_decision_inputs.py` — Decision normalization, validation, and Phase 34 handoff producer.
- `tools/bazel/phase33_maintainer_decision_inputs_test.py` — Decision-axis and source-row validation regressions.

### Readiness consumer and verification

- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-CONTEXT.md` — Phase 34 canonical ledger, fail-closed readiness, and independent demotion decisions.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-01-SUMMARY.md` — Current Phase 34 implementation and artifact boundary.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-02-SUMMARY.md` — Required-stream completeness gap closure.
- `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json` — Ledger schema, reason codes, outputs, and gate semantics.
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py` — Current ledger construction, dangling-row behavior, decision matching, readiness evaluation, and output publication.
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py` — Existing readiness, dangling-row, decision, and demotion regressions.
- `tools/bazel/BUILD.bazel` — Hermetic phase verifier/test runfiles and targets.
- `BUILD.bazel` — Root phase aliases and planning-doc filegroups.
- `tools/bazel/rust_workflow.sh` — Phase workflow dispatch and producer orchestration.
- `justfile` — Repository-owned verification facade.

### Required standards

- `AGENTS.md` — Repository instructions, GSD enforcement, project constraints, and local conventions.
- `AGENTS.bright-builds.md` — Bright Builds workflow, architecture, code-shape, verification, and testing defaults.
- `standards/core/architecture.md` — Functional core, imperative shell, boundary parsing, and illegal-state modeling.
- `standards/core/code-shape.md` — Early returns, rerunnable scripts, and function/file refactor triggers.
- `standards/core/testing.md` — Behavior-focused, one-concern, Arrange/Act/Assert tests.
- `standards/core/verification.md` — Sync-first and repo-native pre-commit verification requirements.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase32_blocker_normalization.py` already provides a pure canonical identity core with immutable source tuples and separate decision identities.
- `tools/bazel/phase32_blocker_register_triage_test.py` already generates actual Phase 26/27/28/31 producer outputs and can supply the Phase 37 integration fixture pattern.
- `tools/bazel/phase33_maintainer_decision_inputs.py` already validates independent decision axes and publishes the Phase 34 handoff.
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py` already owns the canonical readiness ledger, readiness evaluation, demotion evaluation, and retained output bundle.

### Established Patterns

- Phase 31 remains the accepted-final provenance and required-evidence boundary.
- Phase 32 is a sparse blocker/decision-domain overlay, not the authority for reconstructing clean evidence.
- Phase 33 decisions are explicit machine-readable inputs and never inferred from green evidence.
- Phase 34 generates JSON and Markdown from one canonical ledger and keeps readiness separate from demotion authorization.
- Bright Builds guidance materially requires pure transformation logic behind thin filesystem/orchestration shells, exact boundary parsing, fail-closed domain types, and focused tests.

### Integration Points

- Extend the Phase 34 contract and ledger builder to materialize canonical Phase 32 decision-domain rows.
- Tighten the Phase 33-to-34 handoff around explicit typed decision targets.
- Extend Phase 34 tests and Bazel runfiles with the real Phase 31-33 producer chain.
- Keep the existing `just phase34-verify` and Bazel phase targets as the repository-owned verification surface unless planning identifies a narrow Phase 37 alias.

</code-context>

<specifics>
## Specific Ideas

- Preserve two identities deliberately: canonical source identity answers “which row is this,” while the typed decision identity answers “what decision may resolve it.”
- Keep valid decision-domain rows first-class in the readiness ledger instead of treating them as a special case of dangling evidence.
- Make the successful integrated path diagnostic: the same valid baseline should support small, isolated negative mutations that identify exactly why readiness stayed blocked.

</specifics>

<deferred>
## Deferred Ideas

- Full Phase 31-35 workflow approval and production-cutover routing — Phase 38.
- Durable replacement of stale Phase 34/35 authority after upstream-source failure — Phase 38.
- Production reference demotion — post-cutover work and outside v1.3 execution scope.

</deferred>

***

*Phase: 37-reconcile-decisions-into-readiness*
*Context gathered: 2026-07-26*
