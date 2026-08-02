# Phase 34: Final Readiness and Demotion Dry Run - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-25
**Phase:** 34-final-readiness-and-demotion-dry-run
**Mode:** Yolo
**Areas discussed:** Readiness packet lineage and coverage, reference-demotion dry-run semantics, Phase 34 implementation boundary

## Readiness Packet Lineage and Coverage

| Option | Description | Selected |
| --- | --- | --- |
| Contract-driven coverage ledger over Phase 31-33 | Join every accepted receipt and consumed row to Phase 32 classifications and Phase 33 decisions, then fail closed on exact coverage gaps. | ✓ |
| Extend Phase 28 criteria-centric aggregation | Adapt the v1.2 criteria model and add explicit row-closure checks. | |
| Content-addressed evidence graph | Introduce typed provenance nodes and edges with digest-bound refs. | |

**Agent's choice:** Contract-driven coverage ledger over Phase 31-33.
**Notes:** Phase 32 intentionally omits clean passed rows, so Phase 31 must define the expected evidence set. Exact joins and anti-joins provide the strongest READY-01 and READY-02 auditability without inventing a new graph vocabulary.

## Reference-Demotion Dry-Run Semantics

| Option | Description | Selected |
| --- | --- | --- |
| Orthogonal predicates with conjunctive gate | Preserve readiness and explicit approval as separate axes; open only when all required predicates are true. | ✓ |
| Flattened product-state enum | Collapse readiness and approval combinations into one routing enum. | |
| Fail-fast invalid approval | Abort on malformed/stale approval instead of retaining a blocked result. | |

**Agent's choice:** Orthogonal predicates with conjunctive gate.
**Notes:** Separate axes avoid masking concurrent blockers and prove that green evidence never implies authorization. Invalid inputs need durable blocked artifacts for the Phase 35 audit trail.

## Phase 34 Implementation Boundary

| Option | Description | Selected |
| --- | --- | --- |
| Extend Phase 28 directly | Modify the v1.2 verifier for v1.3 inputs. | |
| Wrap Phase 28 | Translate Phase 33 data into Phase 28-shaped criteria and expose Phase 34 outputs. | |
| Fresh Phase 34 consumer over Phase 33 | Preserve Phase 28 and consume the declared v1.3 handoff directly. | ✓ |

**Agent's choice:** Fresh Phase 34 consumer over Phase 33.
**Notes:** Phase 28 is tied to Phase 26/27 lifecycles and criteria. A dedicated Phase 34 consumer avoids lossy adapters and dual readiness authorities while preserving Phase 28 as a semantic precedent.

## the agent's Discretion

- Exact output filenames and internal helper boundaries.
- Stable reason-code spellings.
- Contract snapshot copy implementation.

## Deferred Ideas

- Phase 35 cutover verdict and milestone routing.
- Production reference demotion.
- Content-addressed provenance graphs and attestation signing.
