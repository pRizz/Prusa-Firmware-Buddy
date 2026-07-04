# Phase 33: Maintainer Decision Inputs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-04T01:38:20.362Z
**Phase:** 33-maintainer-decision-inputs
**Mode:** Yolo
**Areas discussed:** Decision input model, retained-code and residual-risk decisions, exception decisions, final-readiness decision input, reference-demotion decision input, generated artifacts and handoff

---

## Decision Input Model

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 33 wrapper over Phase 32 handoff | Build a v1.3 decision-input layer that consumes blocker, exception, residual-risk, and decision-impact handoff rows from Phase 32 while reusing Phase 27/28 vocabulary where useful. | yes |
| Extend Phase 32 to approve decisions | Let the triage phase also approve exceptions, retained code, readiness, or demotion. | |
| Reuse Phase 27 unchanged | Re-run the v1.2 retained-code decision machinery without binding decisions to Phase 32 v1.3 handoff rows. | |

**User's choice:** Auto-selected the Phase 33 wrapper over Phase 32 handoff.
**Notes:** This preserves Phase 32 as classification only and keeps approval semantics in Phase 33.

---

## Retained-Code and Residual-Risk Decisions

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit accept/reject/exception records | Require stable ids, maintainer identity refs, rationale, owner signoff, source row refs, and affected gates for retained-code and residual-risk decisions. | yes |
| Evidence-derived acceptance | Treat green evidence or source-backed retained-code justifications as maintainer acceptance. | |
| Prose-only review notes | Allow markdown-only decisions without normalized machine-readable outputs. | |

**User's choice:** Auto-selected explicit accept/reject/exception records.
**Notes:** Green evidence alone must not create retained-code acceptance or residual-risk acceptance.

---

## Exception Decisions

| Option | Description | Selected |
|--------|-------------|----------|
| Scoped exception approvals | Require matched blocker refs, affected requirements, affected gates, rationale, owner signoff, and expiration or review trigger. | yes |
| Broad exception flags | Allow generic exception approval without source-row matching. | |
| Readiness-only exception coverage | Let Phase 34 infer exception coverage from readiness state rather than Phase 33 decision records. | |

**User's choice:** Auto-selected scoped exception approvals.
**Notes:** Unmatched or broad exceptions remain invalid for readiness unblocking.

---

## Final-Readiness Decision Input

| Option | Description | Selected |
|--------|-------------|----------|
| Handoff-only readiness decision | Record explicit maintainer approval or block as a Phase 34 input without generating final readiness in Phase 33. | yes |
| Generate final readiness now | Let Phase 33 produce the final readiness packet directly. | |
| Infer readiness from blockers | Treat absence of blockers or covered blockers as readiness approval. | |

**User's choice:** Auto-selected handoff-only readiness decision.
**Notes:** Phase 34 still owns final readiness generation.

---

## Reference-Demotion Decision Input

| Option | Description | Selected |
|--------|-------------|----------|
| Separate explicit demotion input | Record approve/reject demotion authorization as its own decision axis and handoff record. | yes |
| Derive from readiness | Allow readiness approval to imply demotion authorization. | |
| Derive from green evidence | Allow green evidence to imply demotion authorization. | |

**User's choice:** Auto-selected separate explicit demotion input.
**Notes:** Missing, malformed, stale, or rejected demotion input preserves fail-closed behavior for Phase 34.

---

## Generated Artifacts and Handoff

| Option | Description | Selected |
|--------|-------------|----------|
| Machine-readable registers plus redacted report | Generate templates, normalized decision records, per-axis registers, readiness and demotion handoffs, validation report, downstream manifest, redacted report, and contract snapshots. | yes |
| Human report only | Produce a markdown report and rely on later phases to parse it. | |
| Single combined decision blob | Emit one unstructured JSON file without per-axis registers or manifest. | |

**User's choice:** Auto-selected machine-readable registers plus redacted report.
**Notes:** Phase 34 and Phase 35 need stable machine-readable handoffs that avoid rereading raw evidence or secret-bearing artifacts.

---

## the agent's Discretion

- Exact Python module split.
- Exact JSON filenames and enum spellings where not already locked by Phase 27, Phase 28, or Phase 32 contracts.
- Whether implementation uses one script with subcommands or a verifier script plus helpers.
- Exact Bazel labels and `just` target names, provided they follow existing phase patterns.

## Deferred Ideas

- Final readiness packet generation and reference-demotion dry-run behavior belong to Phase 34.
- The go/no-go cutover decision artifact belongs to Phase 35.
- Broad retained vendor/HAL replacement, new printer behavior, long-run dashboards, and production reference demotion remain future milestone work unless Phase 33 exposes a narrow decision-blocking defect.
