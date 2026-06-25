# Phase 29: Upstream Evidence Flow Closure - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-25T20:29:12.668Z
**Phase:** 29-Upstream Evidence Flow Closure
**Mode:** Yolo
**Areas discussed:** Upstream row ingestion, status and traceability propagation, final readiness packet behavior, metadata hygiene

---

## Upstream Row Ingestion

| Option | Description | Selected |
|--------|-------------|----------|
| Add explicit Phase 23/24/25 upstream row inputs to Phase 26 | Closes the audit gap at the Phase 26 aggregation boundary and preserves Phase 28 as a consumer of Phase 26 rows. | yes |
| Make Phase 28 read Phase 23/24/25 rows directly | Faster to surface evidence in the packet but bypasses the Phase 26 source-of-truth row table and creates duplicate validation. | |
| Re-run Phase 23/24/25 producers from Phase 26 | Reduces missing-input friction but can create false freshness and broadens Phase 26 into orchestration. | |
| Leave Phase 26 placeholders and document manual review | Lowest implementation cost but does not close the milestone audit gap. | |

**User's choice:** Auto-selected explicit Phase 26 upstream row inputs as the recommended yolo default.
**Notes:** Each input must be validated before it can influence a Phase 26 row.

---

## Status and Traceability Propagation

| Option | Description | Selected |
|--------|-------------|----------|
| Use consumed row state as the source for matching Phase 26 criteria | Preserves real status, source refs, lifecycle metadata, redaction guard state, artifact refs, and requirement traceability. | yes |
| Copy only pass/fail status from upstream rows | Simpler but loses the proof chain that the audit specifically found missing. | |
| Treat all upstream rows as attachments while retaining default pending statuses | Keeps current behavior but does not create true evidence flow. | |
| Normalize every consumed row to Phase 26 release statuses | Reduces vocabulary but blurs evidence-family semantics and can overclaim. | |

**User's choice:** Auto-selected consumed row state propagation as the recommended yolo default.
**Notes:** EVID-01, EVID-02, and EVID-03 must remain visible through Phase 26 and Phase 28 outputs.

---

## Final Readiness Packet Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Keep Phase 28 dependent on Phase 26 rows and Phase 27 handoff | Preserves the existing architecture while requiring the packet to expose propagated upstream evidence refs. | yes |
| Expand Phase 28 into a cross-phase evidence collector | Easier to present every row but duplicates Phase 26 validation and risks policy drift. | |
| Generate a separate milestone audit packet outside Phase 28 | Useful for auditors but does not satisfy READ-01/READ-02 final packet flow. | |

**User's choice:** Auto-selected Phase 28 as a Phase 26/27 consumer as the recommended yolo default.
**Notes:** Reference demotion remains a separate blocked/explicit decision and cannot be inferred from upstream evidence quality.

---

## Metadata Hygiene

| Option | Description | Selected |
|--------|-------------|----------|
| Fix summary and validation metadata as part of Phase 29 | Closes the audit's traceability/validation metadata debt with the evidence-flow work. | yes |
| Leave metadata fixes for a later cleanup phase | Smaller implementation but leaves the milestone audit status partially unresolved. | |
| Update only ROADMAP/REQUIREMENTS status | Gives a clean dashboard but lacks artifact-level proof and reproducible validation metadata. | |

**User's choice:** Auto-selected metadata cleanup in Phase 29 as the recommended yolo default.
**Notes:** ACPT-01, READ-01, and READ-02 should be marked complete only after verification passes.

---

## the agent's Discretion

- Exact helper names, CLI flag names, JSON field names, and test fixture organization.
- Whether to extract reusable upstream row validation helpers or keep them local to Phase 26.
- Exact plan split, with a bias toward one cohesive implementation plan.

## Deferred Ideas

- New dashboards, soak analytics, hardware farm orchestration, and production evidence acquisition.
- Creating or implying non-local maintainer demotion approvals.
