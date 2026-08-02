---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 39-2026-07-29T01-32-55
generated_at: 2026-07-29T01:33:59.337000Z
---

# Phase 39: Milestone Metadata Reconciliation - Context

**Gathered:** 2026-07-28
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Restore truthful, parser-supported completion provenance for the Phase 31 intake requirements; reconcile the stale Phase 31, Phase 32, and Phase 34 roadmap plan inventories with their on-disk artifacts; and prove the v1.3 requirement, roadmap, summary, phase-verification, and state metadata agree before a fresh milestone audit. This phase changes planning and audit metadata only. It does not alter evidence-gate behavior, rerun external evidence collection, authorize cutover or reference demotion, or absorb unrelated Phase 40 work.

</domain>

<decisions>
## Implementation Decisions

### Completion provenance

- **D-01:** Add the canonical hyphenated `requirements-completed` field to `.planning/phases/31-final-evidence-intake/31-01-SUMMARY.md` with `INTAKE-01`, `INTAKE-02`, `INTAKE-03`, and `INTAKE-04`, exactly matching the Phase 31 plan and passed verification.
- **D-02:** Preserve every existing Phase 31 provenance field, including `generated_by`, lifecycle ID, generation timestamp, and completion timestamp. The repair is a narrow metadata backfill, not a rewrite of Phase 31 history.
- **D-03:** Do not add a duplicate `requirements_completed` alias or extend the extractor. The supported `summary-extract` path and current summary convention use only `requirements-completed`.
- **D-04:** Phase 39's own plan, summary, and verification must record the reconciliation work for `INTAKE-01` through `INTAKE-03`; Phase 36 retains its separate `INTAKE-04` gap-closure provenance.

### Roadmap artifact inventory

- **D-05:** Reconcile plan metadata surgically against phase-local plan/summary pairs: Phase 31 is `1/1` with `31-01`, Phase 32 is `1/1` with `32-01`, and Phase 34 is `2/2` with `34-01` and `34-02`.
- **D-06:** Keep later gap-closure plans under their owning Phases 36 through 38. Do not count them again under the original phases or add nonstandard provenance prose to the plan lists.
- **D-07:** Derive each repaired plan-list description from its matching plan goal and completed summary. A plan may be marked complete only when the matching summary exists.

### Consistency proof and re-audit boundary

- **D-08:** Use a layered, fail-closed metadata gate before re-audit. It must check all sixteen v1.3 requirement IDs across `REQUIREMENTS.md`, supported summary extraction, passed phase-verification evidence, roadmap phase status, on-disk plan/summary inventory, and milestone/state counts.
- **D-09:** Update checkboxes, traceability statuses, roadmap completion state, and milestone/state progress only from already passed phase evidence and the completed Phase 39 reconciliation. Do not use metadata edits to conceal a semantic integration gap.
- **D-10:** Require Phase 39 verification and lifecycle validation to pass before refreshing the milestone audit. The fresh audit remains the final cross-source evaluation.
- **D-11:** If the fresh audit finds a semantic or behavioral contradiction, keep the milestone fail-closed and route that issue to separate repair work. Phase 39 must not broaden into replaying or modifying the Phase 31 through Phase 40 implementations.

### the agent's Discretion

- Choose the smallest deterministic implementation for the pre-audit metadata gate: existing GSD commands plus focused assertions, or a narrow read-only repository checker when existing commands cannot express an invariant.
- Choose the exact wording of repaired roadmap plan descriptions, provided each description is faithful to the corresponding plan and summary.
- Choose whether the fresh audit updates the existing canonical audit artifact in place or through the repository's normal audit workflow, provided provenance and the previous gap history remain reviewable.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and audit gaps

- `.planning/PROJECT.md` — v1.3 milestone scope, safety constraints, and the requirement that Phase 39 reconcile metadata before re-audit.
- `.planning/REQUIREMENTS.md` — all sixteen v1.3 requirements, completion checkboxes, and traceability rows.
- `.planning/ROADMAP.md` — Phase 39 goal, requirements, gap-closure boundary, success criteria, and stale phase inventories.
- `.planning/STATE.md` — active milestone position, completed Phase 40 independence, and current Phase 39 focus.
- `.planning/v1.3-MILESTONE-AUDIT.md` — three-source completion gaps and stale Phase 31, Phase 32, and Phase 34 roadmap inventory findings.

### Completion provenance

- `.planning/phases/31-final-evidence-intake/31-01-PLAN.md` — original Phase 31 claim for `INTAKE-01` through `INTAKE-04`.
- `.planning/phases/31-final-evidence-intake/31-01-SUMMARY.md` — historical summary missing the supported completion field.
- `.planning/phases/31-final-evidence-intake/31-VERIFICATION.md` — passed evidence for all four intake requirements.
- `.planning/phases/36-normalize-evidence-and-blocker-rows/36-01-SUMMARY.md` — separate Phase 36 `INTAKE-04` gap-closure provenance.

### Roadmap inventory sources

- `.planning/phases/32-blocker-register-and-evidence-triage/32-01-PLAN.md` — Phase 32's sole original plan.
- `.planning/phases/32-blocker-register-and-evidence-triage/32-01-SUMMARY.md` — completed Phase 32 plan evidence.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-01-PLAN.md` — first Phase 34 plan.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-01-SUMMARY.md` — completed first Phase 34 plan evidence.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-02-PLAN.md` — second Phase 34 plan.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-02-SUMMARY.md` — completed second Phase 34 plan evidence.

### Locked upstream closure evidence

- `.planning/phases/36-normalize-evidence-and-blocker-rows/36-VERIFICATION.md` — passed release-table and blocker-identity normalization evidence.
- `.planning/phases/37-reconcile-decisions-into-readiness/37-VERIFICATION.md` — passed exact decision-to-readiness reconciliation evidence.
- `.planning/phases/38-fail-closed-cutover-workflow/38-VERIFICATION.md` — passed fail-closed workflow and route evidence.
- `.planning/phases/40-file-length-refactoring/40-VERIFICATION.md` — completed independent Phase 40 evidence that must remain outside Phase 39 scope.

### Repository standards

- `AGENTS.md` — GSD workflow enforcement, project constraints, and planning-document rules.
- `AGENTS.bright-builds.md` — sync-first, evidence-backed verification, and managed-check requirements.
- `standards-overrides.md` — no active override to the applicable standards.
- `standards/core/verification.md` — repo-native verification and fail-before-commit requirements.
- `standards/core/testing.md` — focused behavior-test expectations for any added metadata checker.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets

- `gsd-tools.cjs summary-extract`: Supported extraction path for the canonical `requirements-completed` summary key.
- `gsd-tools.cjs roadmap analyze` and phase-operation initialization: Existing structured views of phase status, disk plan counts, summaries, and lifecycle state.
- Existing Phase 31, Phase 32, Phase 34, Phase 36, Phase 37, Phase 38, and Phase 40 verification reports: Already-passed evidence that the metadata layer must report truthfully rather than reimplement.

### Established Patterns

- Plan frontmatter declares requirement ownership; summary frontmatter records completed requirements; verification frontmatter and requirement tables prove goal achievement.
- Phase directories and matching `*-PLAN.md`/`*-SUMMARY.md` pairs are the source of truth for plan inventory.
- GSD state and roadmap mutations use `gsd-tools.cjs`; direct edits are reserved for planning artifacts that the workflow explicitly owns.
- Planning Markdown uses a single YAML frontmatter block and avoids standalone `---` body separators.

### Integration Points

- Phase 31 summary metadata feeds milestone `summary-extract`.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` provide the human and machine-readable milestone status surfaces.
- Phase 39 plan summaries and verification must close the metadata requirement rows without changing underlying evidence semantics.
- The fresh v1.3 milestone audit is the final three-source and integration cross-check.

</code-context>

<specifics>
## Specific Ideas

- Treat the Phase 31 edit as an additive provenance repair: add one canonical field and leave the original historical record untouched otherwise.
- Build one deterministic sixteen-requirement matrix before re-audit so missing summary extraction, pending traceability, or verification disagreement fails early and visibly.
- Compare roadmap plan lists to exact phase-prefixed filenames rather than plan counts alone, preventing another cross-phase copy/paste mismatch.
- Internal `.planning/` metadata is not an appropriate OpenLinks identity-placement surface; no promotional or product-chrome change belongs in this phase.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

*Phase: 39-milestone-metadata-reconciliation*
*Context gathered: 2026-07-28*
