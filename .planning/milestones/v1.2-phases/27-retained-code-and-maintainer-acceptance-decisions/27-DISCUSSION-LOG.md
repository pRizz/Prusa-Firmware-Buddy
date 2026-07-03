# Phase 27: Retained-Code and Maintainer Acceptance Decisions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-25T01:06:35.730Z
**Phase:** 27-retained-code-and-maintainer-acceptance-decisions
**Mode:** Yolo
**Areas discussed:** Acceptance Source Coverage, Decision and Status Semantics, Exception and Residual-Risk Policy, Retained Output and Integration Pattern

---

## Acceptance Source Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Use Phase 18 contract directly | Minimal schema churn, but leaks Phase 18 lifecycle and output identity into Phase 27. | |
| Create a Phase 27 wrapper around Phase 18 | Preserves Phase 18 as canonical while giving Phase 27 its own lifecycle, output root, Phase 26 handoff, and exact-match checks. | yes |
| Build a separate Phase 27 acceptance schema | Tailored to the phase, but duplicates Phase 18 and increases drift risk. | |

**User's choice:** Auto-selected recommended answer: create a Phase 27 wrapper around Phase 18 and Phase 26.
**Notes:** Phase 18 remains canonical for schemas and vocabularies. Phase 27 owns lifecycle, outputs, acceptance inputs, and handoff to Phase 28.

---

## Decision and Status Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse Phase 18 flat status vocabularies | Fastest path, but conflates evidence lifecycle, maintainer judgment, exceptions, and demotion state. | |
| Orthogonal decision axes with derived readiness status | Separates upstream status, maintainer decision, exception state, residual-risk state, hard-failure state, and demotion authorization, then projects to Phase 18-compatible statuses. | yes |
| Append-only decision ledger plus current-state projection | Strong audit trail, but more ordering and supersession machinery than this phase needs by default. | |
| Attestation-style acceptance model | Future-friendly for signed approvals, but broadens Phase 27 beyond the existing manifest pattern. | |

**User's choice:** Auto-selected recommended answer: orthogonal decision axes with derived Phase 18-compatible status.
**Notes:** Redaction and overclaim become hard-failure axes. Green evidence alone cannot approve retained-code risk or reference demotion.

---

## Exception and Residual-Risk Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Schema-only exception metadata | Reuses Phase 18 fields, but weakly enforces blocker vs accepted-risk distinctions. | |
| Typed exception gate with hard evidence prechecks | Requires complete exception metadata and preserves redaction/overclaim as non-waivable blockers. | yes |
| Two-tier approval for high-risk surfaces | Adds stronger accountability for signing, service, crash-dump, safety, and hardware-adjacent surfaces. | partial |
| External risk register or issue tracker linkage | Durable follow-up tracking, but more tooling and fragmented state. | |

**User's choice:** Auto-selected recommended answer: typed exception gate as baseline; use stricter reviewer-role checks for high-risk surfaces when planning finds they are needed.
**Notes:** Exceptions require scope, rationale, approver, approver role, affected surface, mitigation or follow-up, expiry or review trigger, and evidence refs. Secret-tainted evidence and overclaiming stay hard blockers.

---

## Retained Output and Integration Pattern

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 27 acceptance wrapper with Phase 28 handoff manifest | Matches Phase 23-26, preserves Phase 18 criteria, consumes Phase 26 placeholders, and writes clear decision deltas under `build/ci-evidence/phase27`. | yes |
| Full Phase 27 replay of all nine upstream rows | Gives Phase 28 one table, but duplicates Phase 26 evidence statuses and risks stale carry-forward logic. | |
| Direct reuse of Phase 18 cutover-review contract/tool | Minimal new logic, but keeps old lifecycle/output semantics and weak Phase 27 traceability. | |
| Defer acceptance aggregation to Phase 28 | Small now, but fails Phase 27's machine-readable acceptance-output scope. | |

**User's choice:** Auto-selected recommended answer: Phase 27 wrapper with Phase 28 handoff manifest.
**Notes:** Expected outputs include acceptance run manifest, normalized retained-code decisions, residual-risk register, exception summary, final-readiness decision summary, Phase 28 handoff manifest, decision-row table, maintainer input template, artifact summary, and contract snapshots.

---

## the agent's Discretion

- Exact file names and JSON field names for Phase 27 artifacts.
- Whether to share helper logic with Phase 18/26 or keep the Phase 27 verifier standalone.
- Whether planning remains a single plan or splits only if research finds a real dependency boundary.

## Deferred Ideas

- Signed attestation-style approvals.
- External risk-register or issue-tracker integration for longer-lived exception tracking.
