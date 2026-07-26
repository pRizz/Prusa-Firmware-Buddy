# Phase 37: Reconcile Decisions Into Readiness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the alternatives considered.

**Date:** 2026-07-26
**Phase:** 37-reconcile-decisions-into-readiness
**Mode:** Yolo
**Areas discussed:** Canonical readiness ledger population, exact typed decision resolution, integrated approved-path regression boundary

## Canonical Readiness Ledger Population

| Option | Description | Selected |
| --- | --- | --- |
| Dual-source typed union | Keep Phase 31 as evidence-completeness authority and add Phase 32 canonical decision-domain rows as first-class ledger rows. | ✓ |
| Phase 32-first ledger with Phase 31 complement | Use Phase 32 as the primary row population and reconstruct clean/required evidence from Phase 31. | |
| Decision-aware unmatched-row reconciliation | Keep the current ledger shape and special-case valid Phase 27/28 unmatched rows. | |

**Agent's choice:** Dual-source typed union
**Notes:** This preserves the Phase 31 finality boundary, uses Phase 36's separate source and decision identities as intended, and avoids keeping valid decision rows on an exceptional dangling path.

## Exact Typed Decision Resolution

| Option | Description | Selected |
| --- | --- | --- |
| Per-reference typed target bindings | Bind every target with clear-text `row_ref`, `decision_axis`, and `decision_subject_id`, requiring exact equality. | ✓ |
| One typed subject per decision | Store one scalar axis/subject pair plus enumerated row refs, splitting multi-subject actions into separate decisions. | |
| Canonical opaque resolution key | Hash the three-field tuple into a scalar join key while retaining clear-text diagnostics. | |

**Agent's choice:** Per-reference typed target bindings
**Notes:** Exact three-field bindings are the most auditable model and make zero-match, multi-match, mismatch, duplicate, and conflict failures precise. Opaque-only keys are intentionally avoided.

## Integrated Approved-Path Regression Boundary

| Option | Description | Selected |
| --- | --- | --- |
| Dedicated Phase 31-34 producer-chain integration test | Use actual Phase 31-33 outputs and exercise Phase 34 loading, evaluation, and publication. | ✓ |
| Producer-generated inputs with in-process Phase 34 reconciliation | Reuse real shapes but call only reconciliation helpers for faster local tests. | |
| Full Phase 31-35 workflow regression | Exercise readiness, cutover verdict, orchestration, and stale-authority behavior together. | |

**Agent's choice:** Dedicated Phase 31-34 producer-chain integration test
**Notes:** This proves the Phase 37 readiness boundary without absorbing Phase 38's full workflow and stale-authority responsibilities.

## the agent's Discretion

- Internal helper and module boundaries.
- Exact stable reason-code names.
- Whether typed target bindings are emitted by Phase 33 or normalized explicitly at the Phase 34 boundary.
- Exact fixture-sharing mechanics, provided real producer shapes and one-concern negative tests remain visible.

## Deferred Ideas

- Full Phase 31-35 approved/blocked workflow routing and stale-authority replacement remain Phase 38 scope.
- Production reference demotion remains outside this phase and v1.3 execution.
