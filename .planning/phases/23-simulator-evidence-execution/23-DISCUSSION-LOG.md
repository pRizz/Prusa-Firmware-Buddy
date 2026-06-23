# Phase 23: Simulator Evidence Execution - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-23T18:45:38-05:00
**Phase:** 23 - Simulator Evidence Execution
**Mode:** Yolo
**Areas discussed:** Evidence input model, status semantics, retained artifacts and redaction, integration and verification

---

## Evidence Input Model

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse Phase 14 contract | Treat `phase14_simulator_evidence_contract.json` as the canonical scenario catalog and build Phase 23 around real result submission/retention. | yes |
| Redefine simulator scenarios | Create a fresh v1.2 simulator scenario schema independent from Phase 14. | |
| Accept aggregate-only proof | Let maintainers submit only a high-level aggregate status. | |

**User's choice:** Reuse Phase 14 contract.
**Notes:** Auto-selected because Phase 23 explicitly uses the v1.1 simulator evidence contracts and must not redefine v1.0/v1.1 parity gates.

---

## Status Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Normalize to v1.2 statuses | Map real scenario outcomes to `passed`, `failed`, `blocked`, or `exception-requested`, while preserving Phase 14 source status context. | yes |
| Keep Phase 14 statuses only | Report `pending-simulator-input` and dependency statuses directly as final v1.2 outcomes. | |
| Boolean pass/fail only | Collapse all non-pass outcomes into failure. | |

**User's choice:** Normalize to v1.2 statuses.
**Notes:** Auto-selected because the roadmap requires the v1.2 status set and final readiness needs blocked and exception-requested states to remain distinct.

---

## Retained Artifacts and Redaction

| Option | Description | Selected |
|--------|-------------|----------|
| Secret-safe retained metadata | Store sanitized metadata, artifact refs, summaries, and manifest snapshots under the existing evidence-output convention. | yes |
| Commit raw simulator logs | Retain full logs and payload dumps directly in source/planning artifacts. | |
| Store only prose summaries | Keep human-readable notes without machine-readable retained evidence. | |

**User's choice:** Secret-safe retained metadata.
**Notes:** Auto-selected because v1.2 explicitly excludes private keys, tokens, certificates, payloads, and raw crash dumps from committed artifacts.

---

## Integration and Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Add focused Phase 23 verifier | Follow existing `tools/bazel/phaseXX_*` Python, Bazel, `rust_workflow.sh`, and `justfile` verification patterns. | yes |
| Hand-edit planning evidence only | Satisfy the phase with documentation changes and no executable verifier. | |
| Rework aggregate/final review first | Delay simulator execution until Phase 26-28 acceptance work. | |

**User's choice:** Add focused Phase 23 verifier.
**Notes:** Auto-selected because the phase success criteria require submit/retain behavior, scenario statuses, redacted artifacts, and links to parity requirements that should be validated by tests.

---

## the agent's Discretion

- Exact Phase 23 JSON filenames and field names.
- Whether Phase 23 wraps Phase 14 real-run output, accepts a separate maintainer input packet, or does both.
- Exact number of plans and wave split.

## Deferred Ideas

- Phase 24 hardware/media/safety evidence.
- Phase 25 live-service evidence.
- Phase 26 release/signing/upstream result evidence.
- Phase 27-28 maintainer decisions and final readiness.
