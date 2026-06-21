# Phase 22: Evidence Metadata Reconciliation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-21T16:59:18.640Z
**Phase:** 22-evidence-metadata-reconciliation
**Mode:** Yolo
**Areas discussed:** Requirements and traceability reconciliation, Validation metadata reconciliation, Roadmap/state consistency, Milestone audit rerun readiness

---

## Requirements and Traceability Reconciliation

| Option | Description | Selected |
|--------|-------------|----------|
| Keep pending with evidence notes | Preserve pending requirement rows until final external evidence has passed. | |
| Mark complete without qualifiers | Flip statuses to complete with minimal text. | |
| Evidence-qualified complete in existing rows | Mark gate capability complete while preserving result-level pending boundaries. | yes |
| Split gate status from result status | Add a larger dual-status traceability model. | |

**User's choice:** Auto-selected recommended yolo default: evidence-qualified completion.
**Notes:** `SIM-03`, `REV-02`, and `REV-03` should reflect verified traceability/final-readiness gates without claiming hardware-only simulator proof or final demotion approval.

---

## Validation Metadata Reconciliation

| Option | Description | Selected |
|--------|-------------|----------|
| In-place local metadata reconciliation with explicit boundary notes | Clear stale Wave 0 metadata where local verifier files exist and passed, while preserving non-local evidence boundaries. | yes |
| Phase 22 reconciliation ledger/addendum only | Leave prior validation files untouched and add a central exception ledger. | |
| Machine-checked reconciliation script/report | Add repeatable checker/report as the primary reconciliation path. | |
| Keep Wave 0 incomplete until all external gates pass | Leave validation metadata incomplete until external evidence passes. | |

**User's choice:** Auto-selected recommended yolo default: in-place reconciliation with explicit no-overclaim notes.
**Notes:** Phase 14-18 validation files should no longer claim Wave 0 dependencies are missing once verifier files, contracts, tests, and wiring exist.

---

## Roadmap, Phase Directory, and STATE Consistency

| Option | Description | Selected |
|--------|-------------|----------|
| Tool-anchored targeted reconciliation | Derive counts and statuses from `gsd-tools`, lifecycle checks, phase directories, summaries, and verification reports before editing. | yes |
| Manual surgical reconciliation | Edit stale roadmap/state rows directly, then verify. | |
| Defer reconciliation until final Phase 22 audit rerun | Leave metadata stale until the end of Phase 22. | |
| Add derived metadata/preflight automation | Build a reusable derived metadata tool for future audits. | |

**User's choice:** Auto-selected recommended yolo default: tool-anchored targeted reconciliation.
**Notes:** Phase 21 is valid on disk but stale in roadmap/state displays. Phase 22 should update counts and state with GSD-owned commands where available.

---

## Milestone Audit Rerun Readiness

| Option | Description | Selected |
|--------|-------------|----------|
| Source-backed reconciliation manifest plus rerun verifier | Add a durable manifest/checker that validates metadata consistency and allows only explicit non-blocking debt. | yes |
| Generated CI audit snapshot only | Rely on generated CI/run artifacts for audit state. | |
| Prose and checkbox reconciliation only | Update planning prose without a machine-readable verifier. | |
| Attested digest index for generated evidence | Add provenance/digest identity for generated evidence artifacts. | |

**User's choice:** Auto-selected recommended yolo default: source-backed reconciliation manifest plus rerun verifier.
**Notes:** Generated audit artifacts should stay under ignored `build/ci-evidence/phase22`; source-backed policy should be checked in.

---

## the agent's Discretion

- Exact file names, manifest fields, helper boundaries, and status vocabulary are left to the planner/executor if the result stays deterministic, traceable, redacted, and hard to overclaim.
- Prefer focused standard-library Python and existing Bazel/just patterns over broad audit-framework rewrites.

## Deferred Ideas

- Attested digest indexes or provenance exports for generated evidence can be revisited later.
- A general derived metadata dashboard can be considered if milestone metadata drift repeats.
