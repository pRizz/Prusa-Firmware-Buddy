# Phase 21: Final Readiness Result Consumption - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the alternatives considered.

**Date:** 2026-06-21T16:02:06.276Z
**Phase:** 21-final-readiness-result-consumption
**Mode:** Yolo
**Areas discussed:** Upstream result authority, gating semantics, input and artifact model, traceability and verification

---

## Upstream Result Authority

| Option | Description | Selected |
|--------|-------------|----------|
| Extend Phase 18 | Keep final review authority in Phase 18 and add upstream result prerequisites there. | yes |
| Add standalone Phase 21 verifier | Create a separate final-readiness verifier that wraps Phase 18. | |
| Trust decision refs | Continue accepting guarded decision refs as proof. | |

**User's choice:** Auto-selected the recommended Phase 18 extension.
**Notes:** This keeps `demotion_allowed` in one authoritative final-review path and directly closes the audit gap.

---

## Gating Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Hard prerequisite | Final criteria can pass only with valid upstream results or explicit valid exceptions. | yes |
| Advisory summary | Show upstream results but let decisions pass independently. | |
| External refs only | Require refs but do not validate result contents. | |

**User's choice:** Auto-selected hard prerequisite semantics.
**Notes:** Missing, failed, stale, redaction-failed, overclaiming, or pending upstream results must keep final demotion blocked.

---

## Input and Artifact Model

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated upstream input | Add a machine-readable upstream result input separate from maintainer decision input. | yes |
| Reuse decision refs | Parse upstream proof out of final decision evidence refs. | |
| Generated-only | Consume whatever artifacts already exist under build outputs without an explicit input. | |

**User's choice:** Auto-selected a dedicated upstream input model.
**Notes:** A distinct input makes validation explicit and avoids treating arbitrary external refs as upstream pass evidence.

---

## Traceability and Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Focused regression tests | Add tests for missing, failed, stale, redaction-failed, and valid upstream results. | yes |
| Broad verifier rewrite | Refactor the large Phase 18 verifier before adding behavior. | |
| Planning-only documentation | Document the policy without enforcing it in code. | |

**User's choice:** Auto-selected focused tests and narrow implementation.
**Notes:** The Phase 18 verifier is already large, so this phase should avoid unrelated restructuring while still adding a real enforcement gate.

---

## the agent's Discretion

- Exact JSON field names and helper boundaries are left to implementation.
- Exact generated artifact names are flexible if they are deterministic and traceable.
- Keep generated evidence ignored under `build/ci-evidence/`.

## Deferred Ideas

- Metadata reconciliation remains Phase 22 scope.
- Large-file refactoring for Phase 18/20 remains non-blocking maintainer debt unless required to implement this safely.
