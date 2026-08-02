# Phase 32: Blocker Register and Evidence Triage - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves alternatives considered.

**Date:** 2026-07-03T14:13:51.406Z
**Phase:** 32 - Blocker Register and Evidence Triage
**Mode:** Yolo
**Areas discussed:** Register input model, Blocker taxonomy and required fields, Placeholder and non-final proof rejection, Downstream handoff shape

## Register Input Model

| Option | Description | Selected |
| --- | --- | --- |
| Consume Phase 31 final-intake manifest/receipts directly | Treat Phase 31 as finality/provenance boundary, but may lose row-level detail. | |
| Normalize Phase 23-26 upstream rows independently | Gives direct source detail, but bypasses Phase 31 and duplicates finality policy. | |
| Small adapter layer over Phase 31 plus referenced source rows | Uses Phase 31 as finality authority, follows accepted receipt refs for detail, and includes rejected/quarantined rows as non-proof blockers. | yes |

**Auto-selected choice:** Small adapter layer over Phase 31 plus referenced source rows.
**Notes:** This preserves Phase 31 as the finality/provenance authority while giving Phase 32 enough row detail to satisfy TRIAGE-01 and TRIAGE-02.

## Blocker Taxonomy and Required Fields

| Option | Description | Selected |
| --- | --- | --- |
| Orthogonal canonical register | Separate row problem kind, blocker kind, severity, affected gate, required next action, and decision impact. | yes |
| Single overloaded blocker status | Smallest schema, but mixes evidence failure, decision state, and proof eligibility. | |
| Three routed queues: repair, exception, decision | Clear work queues, but duplicates rows unless derived from a canonical register. | |
| Policy-derived classifier with owner/action map | Good defaults, but stale policy could underclassify blockers unless unknown mappings fail closed. | |

**Auto-selected choice:** Orthogonal canonical register.
**Notes:** The canonical register must keep `blocker_kind` separate from `row_problem_kind` so redaction failures, stale rows, secret-tainted rows, and exception requests cannot accidentally imply approval.

## Placeholder and Non-Final Proof Rejection

| Option | Description | Selected |
| --- | --- | --- |
| Phase 32 ingestion/classification layer | Makes non-final rows visible in the register while only accepted-final receipts can count as proof. | yes |
| Expand Phase 31 rejection metadata | Canonicalizes rejection codes upstream, but reopens a passed Phase 31 surface. | |
| Phase 34 readiness-only enforcement | Keeps Phase 32 lighter, but shows maintainers the proof rejection too late. | |
| Shared proof-eligibility policy module | Consistent across phases, but adds broad abstraction before repeated drift is proven. | |

**Auto-selected choice:** Phase 32 ingestion/classification layer.
**Notes:** Phase 31 already quarantines quick output and rejects unsafe submissions. Phase 32 should classify those outcomes as blockers without making them proof.

## Downstream Handoff Shape

| Option | Description | Selected |
| --- | --- | --- |
| Normalized Phase 32 handoff bundle | One machine-readable source for Phase 33-35 while preserving Phase 31 boundaries. | yes |
| Monolithic blocker register only | Minimal artifact count, but downstream phases must derive decision inputs themselves. | |
| Per-downstream handoff artifacts | Tailored inputs, but duplicates data and encodes later-phase policy too early. | |
| Append-only triage ledger plus materialized views | Strong audit trail for repeated review cycles, but heavier than this cutover trial needs. | |

**Auto-selected choice:** Normalized Phase 32 handoff bundle.
**Notes:** The bundle should include `blocker-register.json`, derived exception/residual-risk request registers, `decision-impact-index.json`, `downstream-handoff-manifest.json`, and a redacted report.

## the agent's Discretion

- Exact helper/module split.
- Exact enum spelling when documented and tested.
- Exact Bazel labels and `just` target names, following existing phase patterns.

## Deferred Ideas

- Exception approval, retained-code acceptance, residual-risk acceptance, final-readiness approval, demotion authorization, and go/no-go verdict generation stay in Phases 33-35.
