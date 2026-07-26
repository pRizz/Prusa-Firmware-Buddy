# Phase 36: Normalize Evidence and Blocker Rows - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the alternatives considered.

**Date:** 2026-07-26T00:33:39.346Z
**Phase:** 36-normalize-evidence-and-blocker-rows
**Mode:** Yolo
**Areas discussed:** Release row-table normalization, canonical blocker identity, fail-closed shape policy and regression boundary

***

## Release Row-Table Normalization

| Option | Description | Selected |
| --- | --- | --- |
| Explicit Phase 32 adapter | Validate the canonical Phase 26 `{"rows": [...]}` table atomically while preserving Phase 31 finality and row lineage. | ✓ |
| Change Phase 26/31 producers | Expose one consumed reference per row and migrate established producer and receipt contracts. | |
| Generic recursive row flattener | Discover nested rows heuristically without producer-specific domain dispatch. | |

**Agent's choice:** Explicit Phase 32 adapter
**Notes:** This is the smallest change that preserves the locked Phase 31/32 authority boundary. Valid all-passed tables stay eligible; malformed tables fail as a whole.

***

## Canonical Blocker Identity

| Option | Description | Selected |
| --- | --- | --- |
| Typed composite identity plus canonical refs | Derive `row_id` from immutable source-domain fields and keep exact decision-axis identity separate. | ✓ |
| Artifact locator identity | Derive identity primarily from source paths and artifact locations. | |
| Opaque Phase 32 identity registry | Mint durable IDs in a new persistent mapping layer. | |

**Agent's choice:** Typed composite identity plus canonical refs
**Notes:** Existing producer-native packet, row, and criterion IDs are sufficient natural subjects. Mutable status, owner, evidence, timestamps, and paths must not alter `row_id`.

***

## Fail-Closed Shape Policy and Regression Boundary

| Option | Description | Selected |
| --- | --- | --- |
| Contract-keyed required-core adapters | Validate decision-bearing fields and types, tolerate additive non-semantic metadata, and return explicit malformed or unknown blockers. | ✓ |
| Closed-world exact-key adapters | Reject any producer field addition or omission. | |
| Normalize tables in Phase 31 | Move canonicalization authority and receipt-shape changes upstream. | |

**Agent's choice:** Contract-keyed required-core adapters
**Notes:** Positive tests must exercise actual Phase 26 output through Phase 31 and real Phase 27/28 output into Phase 32. Negative tests mutate one concern at a time. Verification stops at the Phase 32 handoff.

## the agent's Discretion

- Choose the internal helper/module split and exact test invocation route.
- Decide how to preserve non-authoritative additive metadata without expanding the trusted decision surface.

## Deferred Ideas

- Phase 34 decision reconciliation belongs to Phase 37.
- Full Phase 31-35 authority-flow regressions belong to Phase 38.
- Milestone metadata reconciliation belongs to Phase 39.
