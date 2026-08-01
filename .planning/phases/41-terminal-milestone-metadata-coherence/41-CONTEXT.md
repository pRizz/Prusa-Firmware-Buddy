---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 41-2026-08-01T16-27-53
generated_at: 2026-08-01T16:34:58.401Z
---

# Phase 41: Terminal Milestone Metadata Coherence - Context

**Gathered:** 2026-08-01
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Reconcile the terminal v1.3 planning projection so ROADMAP, REQUIREMENTS, STATE, exact phase plan inventories, Nyquist validation records, and the milestone audit agree with already-completed evidence. Add a repo-owned fail-closed consistency gate that blocks audit or archival when these surfaces drift. This phase does not redefine requirement meaning, runtime cutover behavior, demotion authorization, or firmware behavior.

</domain>

<decisions>
## Implementation Decisions

### Terminal Metadata Authority

- **D-01:** Use evidence-led authority rather than treating duplicated planning documents as peer authorities. Requirement prose and exclusions remain the semantic contract; plan claims, supported summary extraction, passed phase verification, and completed validation evidence authorize completion projections.
- **D-02:** Exact phase-prefixed PLAN and SUMMARY files on disk authorize plan inventories. A count-only match is insufficient; ROADMAP plan lists and progress rows must agree with the exact on-disk filenames and completion state.
- **D-03:** Treat ROADMAP statuses/counts/lists, REQUIREMENTS checkboxes/traceability/rollups, STATE position/counters, VALIDATION execution markers, and milestone-audit rollups as derived projections that must agree with their evidence inputs.
- **D-04:** Treat the milestone audit as a fresh terminal consumer, never as evidence that can make its own prerequisites true. Historical `gaps_found` audit content is diagnostic context only.
- **D-05:** Use supported `gsd-tools.cjs` commands for ROADMAP and STATE mutations. Where no supported writer exists for a bounded projection, make a targeted edit and immediately prove the exact resulting values with the repo-owned checker.
- **D-06:** Preserve the already-verified runtime meaning of all sixteen v1.3 requirements. Phase 41 may correct ownership, status, coverage, and rollup metadata but may not weaken or reinterpret acceptance semantics.

### Fail-Closed Consistency Enforcement

- **D-07:** Build a repo-owned Python normalized-snapshot checker with a pure comparison core and a thin read-only CLI, following the established `tools/bazel/phase*` verifier pattern.
- **D-08:** Parse each supported artifact shape once into normalized requirement, phase, plan/summary inventory, lifecycle, and Nyquist models. Compare projections against evidence rather than comparing duplicated counts to one another.
- **D-09:** Aggregate deterministic, sorted, path-qualified violation codes. Exit `0` only when the selected gate is coherent, `1` for missing, malformed, stale, contradictory, or incomplete repository state, and `2` only for invalid CLI invocation.
- **D-10:** Provide pre-audit and pre-archive modes from the same core. Both fail closed; pre-archive additionally requires the authoritative fresh audit and terminal lifecycle state.
- **D-11:** Cover the checker with a minimal coherent fixture tree plus one-concern mutations for every protected invariant, and add a live-repository smoke target over declared planning inputs.
- **D-12:** Wire the checker through Bazel and `just phase41-verify`. Compose it with, but do not modify, the managed `scripts/bright-builds-check.ts` checker.

### Nyquist and Audit Sequencing

- **D-13:** Reconcile Phase 37, 38, and 40 VALIDATION files from executed evidence. Replace stale pending/Wave 0 markers only when the corresponding plans, summaries, tests, and verification reports prove completion; do not manufacture green state from metadata alone.
- **D-14:** Use an evidence-first sequence: reconcile prior validation records, implement and run the Phase 41 consistency gate, execute and verify Phase 41, ensure Nyquist discovery reports no partial or missing phase, then run one authoritative fresh milestone audit covering eleven phases and all sixteen requirements.
- **D-15:** Keep the milestone in a non-archival, non-terminal state until the fresh audit passes. The final audit must report no integration, flow, metadata, or Nyquist gap before archival-ready metadata is allowed. Nothing in this sequence authorizes production cutover or reference demotion.

### the agent's Discretion

- Choose the concrete Python module split, normalized dataclasses/types, violation-code names, fixture layout, Bazel target names, and `just` recipe internals while preserving the locked behavior above.
- Choose the narrowest supported GSD CLI commands and targeted projection edits needed to reconcile ROADMAP, REQUIREMENTS, and STATE.
- Choose whether the checker prints human-readable text, JSON, or both, provided deterministic diagnostics and exit semantics remain testable.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Terminal Planning and Audit State

- `.planning/ROADMAP.md` — Phase 41 boundary, success criteria, requirement ownership, plan inventories, and progress projection.
- `.planning/REQUIREMENTS.md` — Authoritative v1.3 requirement semantics, checked rows, traceability ownership, and stale rollup to reconcile.
- `.planning/STATE.md` — GSD-owned lifecycle position and milestone counters; mutate through supported CLI operations.
- `.planning/v1.3-MILESTONE-AUDIT.md` — Current `gaps_found` diagnosis, M1 metadata blocker, and partial Nyquist inventory; diagnostic input only, not completion authority.

### Prior Metadata and Validation Evidence

- `.planning/phases/39-milestone-metadata-reconciliation/39-CONTEXT.md` — Locked Phase 39 metadata decisions and the requirement-neutral reconciliation boundary.
- `.planning/phases/39-milestone-metadata-reconciliation/39-01-SUMMARY.md` — Executed Phase 39 work and completed requirement metadata evidence.
- `.planning/phases/39-milestone-metadata-reconciliation/39-VERIFICATION.md` — Passed Phase 39 verification and the claims Phase 41 must reconcile without changing runtime meaning.
- `.planning/phases/37-reconcile-decisions-into-readiness/37-VALIDATION.md` — Stale task-state projection to reconcile against Phase 37 summaries and verification.
- `.planning/phases/38-fail-closed-cutover-workflow/38-VALIDATION.md` — Stale task-state projection to reconcile against Phase 38 summaries and verification.
- `.planning/phases/40-file-length-refactoring/40-VALIDATION.md` — Stale Wave 0 and campaign-state projection to reconcile against Phase 40 summaries and verification.

### Repository Verification Patterns

- `tools/bazel/phase22_metadata_reconciliation.py` — Existing planning-metadata parsing and validation pattern to reuse selectively rather than duplicate blindly.
- `tools/bazel/phase22_metadata_reconciliation_test.py` — Existing fixture and negative-test patterns for metadata reconciliation.
- `tools/bazel/BUILD.bazel` — Bazel ownership and test wiring for phase verifier tools.
- `justfile` — Stable developer-facing verification façade.
- `scripts/bright-builds-check.ts` — Managed generic checker that Phase 41 composes with but does not modify.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets

- `gsd-tools.cjs` roadmap, state, lifecycle, summary-extract, and audit commands provide supported mutation and discovery boundaries for GSD-owned state.
- Phase 22 metadata reconciliation already demonstrates Python parsing, deterministic validation, fixture-based tests, Bazel wiring, and `just` integration.
- Phase 39 summary and verification provide the completed evidence set whose stale terminal projections caused M1.

### Established Patterns

- Repo-owned verification logic lives under `tools/bazel/` as testable Python cores with Bazel targets and stable `just` wrappers.
- Planning metadata is YAML-frontmatter Markdown; standalone `---` is reserved for the opening and closing frontmatter delimiters.
- Runtime authority and demotion remain fail closed and separate. Metadata repair cannot manufacture either authority.

### Integration Points

- Add Phase 41 checker/test targets to `tools/bazel/BUILD.bazel` and a stable aggregate recipe to `justfile`.
- Reconcile planning projections through GSD CLI ownership plus bounded targeted edits, then run the live checker against `.planning/`.
- Gate the official milestone audit and archival path with the same normalized consistency core in progressively stricter modes.

</code-context>

<specifics>
## Specific Ideas

- Prefer exact sets and stable identities over counters: exact requirement IDs, exact plan/summary basenames, exact phase numbers, and exact validation task/campaign rows.
- Make every drift diagnostic name the artifact path and invariant so unattended failures are actionable.
- Preserve the current `gaps_found` audit until all prerequisites are evidenced; replace it only with the one fresh authoritative audit.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

***

*Phase: 41-terminal-milestone-metadata-coherence*
*Context gathered: 2026-08-01*
