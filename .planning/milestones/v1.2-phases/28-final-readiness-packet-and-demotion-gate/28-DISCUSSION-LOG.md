# Phase 28: Final Readiness Packet and Demotion Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-25T03:38:04.282Z
**Phase:** 28-Final Readiness Packet and Demotion Gate
**Mode:** Yolo
**Areas discussed:** Packet composition and traceability, readiness and exception semantics, reference demotion authorization, retained outputs and verification scope

---

## Packet Composition and Traceability

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 18/27 criteria-centric traceability packet | Aligns with canonical Phase 18 final criteria, preserves Phase 26 upstream rows and Phase 27 decision handoff, keeps demotion separate, and uses a secret-safe link model. | yes |
| Self-contained redacted readiness dossier | Easier offline review but duplicates source data, raises redaction risk, and can drift from generated outputs. | |
| Narrative maintainer brief with generated appendices | Useful as a human companion view but weak as the sole audit source. | |
| Assurance-case claims/evidence packet | Stronger safety-audit model but adds a second truth model and likely scope creep. | |

**User's choice:** Auto-selected criteria-centric, link-first packet as the recommended yolo default.
**Notes:** The machine-readable packet is the source of truth. The human-readable report is derived from those rows.

---

## Readiness and Exception Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Two-verdict fail-closed model | Keeps final readiness separate from reference demotion, starts blocked, and makes exception precedence explicit. | yes |
| Phase 18 status-reuse model | Minimizes schema drift but risks blurring evidence readiness with demotion authorization. | |
| Report-only readiness packet | Avoids automatic demotion but does not satisfy the phase goal for machine-readable approval. | |

**User's choice:** Auto-selected two-verdict fail-closed model as the recommended yolo default.
**Notes:** Hard blockers outrank exceptions. Exceptions can cover only contract-allowed statuses and require complete owner, rationale, evidence, residual-risk, mitigation, and review-trigger metadata.

---

## Reference Demotion Authorization

| Option | Description | Selected |
|--------|-------------|----------|
| Separate demotion authorization axis | Preserves Phase 27 handoff, satisfies READ-03, and prevents green evidence from becoming implicit approval. | yes |
| Use `final-reference-demotion-allowed` as the only approval surface | Smallest policy surface but risks accidental coupling between readiness and demotion. | |
| Dual record: readiness approval plus separate authorization | Auditable but duplicates state and needs precedence rules. | |
| Packet-only, always blocked in Phase 28 | Safest but does not fully meet the phase goal. | |

**User's choice:** Auto-selected separate demotion authorization axis as the recommended yolo default.
**Notes:** Readiness can become green or exception-covered while demotion remains blocked until explicit maintainer authorization.

---

## Retained Outputs and Verification Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 28 aggregate wrapper over Phase 26/27 retained outputs | Keeps evidence production in prior phases, preserves `phase28-handoff-manifest.json`, and supports packet plus gate summary. | yes |
| Re-run Phase 23-27 quick producers inside Phase 28 | Reduces missing-input friction but widens Phase 28 into orchestration and can create false freshness. | |
| Reuse Phase 18 final review as authoritative gate | Reuses existing policy but may conflate v1.1 review semantics with Phase 28 approval semantics. | |
| Report-only packet with no new machine-readable gate | Smallest surface but weak fit for READ-02/READ-03. | |

**User's choice:** Auto-selected aggregate wrapper over Phase 26/27 retained outputs as the recommended yolo default.
**Notes:** Retained outputs should live under `build/ci-evidence/phase28`, with Bazel/root/`rust_workflow.sh`/`just phase28-verify` wiring consistent with prior v1.2 phases.

## the agent's Discretion

- Exact filenames and JSON field names for Phase 28 artifacts.
- Whether to wrap shared Phase 18/26/27 helper code or keep a thin standalone verifier.
- Final plan count, with a bias toward one cohesive plan unless a real dependency split appears.

## Deferred Ideas

None.
