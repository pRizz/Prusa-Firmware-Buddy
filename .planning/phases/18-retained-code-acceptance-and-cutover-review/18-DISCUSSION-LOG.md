# Phase 18: Retained-Code Acceptance and Cutover Review - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-20T14:32:22.889Z
**Phase:** 18-Retained-Code Acceptance and Cutover Review
**Mode:** Yolo
**Areas discussed:** Retained-code packet taxonomy, Final reference-demotion checklist semantics, Final cutover readiness report

---

## Retained-Code Packet Taxonomy

| Option | Description | Selected |
|--------|-------------|----------|
| Phase-owned row-level JSON acceptance packets + generated checklist | One packet per retained surface, verifier-enforced taxonomy, evidence refs, owner, approver, status, rationale, residual risk, redaction and overclaim guards. | yes |
| Surface-family dossiers with nested packets | Human-friendly domain grouping, but nested rollups can hide missing sub-surfaces unless the verifier is strict. | |
| SBOM/VEX-inspired component statement model | Familiar component/status/justification fields, but behavior parity and firmware safety need custom extensions. | |
| PR/issue checklist approval workflow | Low implementation friction, but weak as a reproducible machine gate and prone to platform-state drift. | |

**User's choice:** Yolo recommendation selected phase-owned row-level JSON acceptance packets plus generated checklist.

**Notes:** The authoritative packet model should require identity, taxonomy tags, retained source refs, prior phase refs, required evidence refs, supplied evidence result refs, owner, approver role, approval metadata, status, rationale, residual risk, blocker/deferred action, exception ref, secret handling, and overclaim guards.

---

## Final Reference-Demotion Checklist Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Single canonical gate-matrix JSON | Simple `demotion_allowed` computation, but risks mixing evidence resolution and maintainer judgment in one wide schema. | |
| Evidence index + decision packet | Separates evidence provenance from maintainer decisions while keeping deterministic demotion computation. | yes |
| Policy manifest + evaluator | Extensible, but risks creating an unnecessary policy mini-engine for this phase. | |
| Markdown checklist with structured front matter | Human-friendly, but weakest deterministic enforcement and easiest to overclaim through stale prose. | |

**User's choice:** Yolo recommendation selected evidence index plus decision packet.

**Notes:** `demotion_allowed` can be true only when every required criterion is `passed`, `exception-approved`, or validly `not-applicable`. Approved exceptions require scope, rationale, approver, affected surface, mitigation or follow-up, review trigger, and evidence links.

---

## Final Cutover Readiness Report

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid checked-in contract + generated readiness dossier | Matches Phase 13-17 pattern: durable policy in source, per-run review outputs under ignored `build/ci-evidence/phase18`. | yes |
| Fully checked-in final readiness report and decision packet | Easy PR review, but likely to drift from latest evidence and raises redaction/overclaim risk. | |
| Generated-only CI readiness bundle | Reflects run state and avoids repo churn, but weakens git auditability and depends on artifact retention. | |
| SLSA/in-toto-style verification summary export | Useful future export shape, but adds trust-root/attestation decisions beyond the current phase need. | |

**User's choice:** Yolo recommendation selected hybrid checked-in contract plus generated readiness dossier.

**Notes:** Generated artifacts should include run manifest, normalized final-demotion results, retained-code acceptance summary, residual-risk register, redacted readiness report, source-contract snapshot, and maintainer decision input template.

---

## the agent's Discretion

- Exact packet IDs, status spelling, schema field order, generated filenames, and helper boundaries are flexible if deterministic, source-backed, redacted, traceable, and hard to overclaim.
- External assurance vocabulary may inform names, but Phase 18 should not add a new attestation trust root unless the existing repo evidence contract needs it.

## Deferred Ideas

None.
