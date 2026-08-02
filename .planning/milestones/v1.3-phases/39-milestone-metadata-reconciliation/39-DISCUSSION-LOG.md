# Phase 39: Milestone Metadata Reconciliation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the alternatives considered.

**Date:** 2026-07-28
**Phase:** 39-milestone-metadata-reconciliation
**Mode:** Yolo
**Areas discussed:** Completion provenance, Roadmap artifact inventory, Consistency proof and re-audit boundary

______________________________________________________________________

## Completion provenance

| Option                                      | Description                                                                                                                                                          | Selected |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Layered canonical backfill                  | Add the canonical `requirements-completed` list to the Phase 31 summary, preserve its lifecycle provenance, and let Phase 39 separately record metadata gap closure. | ✓        |
| Dual-key compatibility backfill             | Add both hyphenated and underscore completion keys for possible legacy consumers.                                                                                    |          |
| Immutable addendum with extractor extension | Leave the historical summary unchanged and teach GSD/audit tooling to consume a separate addendum.                                                                   |          |

**User's choice:** Layered canonical backfill, auto-selected as the recommended default in yolo mode.
**Notes:** The Phase 31 plan already claims all four INTAKE requirements and its verification passes them. The current supported extractor reads the hyphenated key, so duplicate aliases or extractor changes add risk without evidence of a consumer need.

______________________________________________________________________

## Roadmap artifact inventory

| Option                                         | Description                                                                                                       | Selected |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | -------- |
| Phase-local surgical reconciliation            | Repair only the Phase 31, Phase 32, and Phase 34 counts/lists from their matching on-disk plan and summary pairs. | ✓        |
| Surgical reconciliation plus provenance notes  | Repair the counts and add prose describing later gap-closure lineage beside the original phase lists.             |          |
| Repository-wide generated inventory or checker | Introduce broader generation or validation machinery for every roadmap plan list.                                 |          |

**User's choice:** Phase-local surgical reconciliation, auto-selected as the recommended default in yolo mode.
**Notes:** On disk, Phase 31 has one completed plan, Phase 32 has one, and Phase 34 has two. Later Phases 36 through 38 own their own gap-closure plans and must not be double-counted.

______________________________________________________________________

## Consistency proof and re-audit boundary

| Option                                                         | Description                                                                                                                                                                   | Selected |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Layered metadata gate, Phase 39 verification, then fresh audit | Fail early on the sixteen-requirement matrix, exact plan inventory, phase/status/state consistency, and supported summary extraction before the canonical audit is refreshed. | ✓        |
| GSD-native commands followed directly by audit                 | Use existing structured commands and rely on the fresh audit to discover any remaining contradiction.                                                                         |          |
| Replay Phase 31-40 verification before audit                   | Re-run every implementation verification surface before checking metadata.                                                                                                    |          |

**User's choice:** Layered metadata gate, Phase 39 verification, then fresh audit, auto-selected as the recommended default in yolo mode.
**Notes:** Existing commands expose many facts but do not independently fail on every cross-file contradiction. Replaying all implementation suites would expand a metadata-only phase and blur failures; semantic gaps discovered by the audit remain separate repair work.

## the agent's Discretion

- The smallest deterministic assertion/checker mechanism for the pre-audit metadata gate.
- Exact repaired plan-list wording when it remains faithful to the matching plan and summary.
- The normal audit workflow's artifact refresh mechanics, with provenance preserved.

## Deferred Ideas

None.
