# Phase 25: Live-Service Evidence Execution - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-23T21:12:46.652Z
**Phase:** 25-Live-Service Evidence Execution
**Mode:** Yolo
**Areas discussed:** Evidence input model, Status and acceptance semantics, Live-service coverage and redaction, Retained artifacts and integration, Verification

## Evidence Input Model

| Option | Description | Selected |
|--------|-------------|----------|
| Wrap Phase 16 | Preserve Phase 16 as the scenario catalog and add a v1.2 execution packet around it. | yes |
| Redefine scenarios | Create a new Phase 25 scenario list. | |

**User's choice:** Auto-selected recommended approach: wrap Phase 16.
**Notes:** This follows Phase 23 and Phase 24 and avoids schema drift.

## Status and Acceptance Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Normalize to v1.2 statuses | Emit `passed`, `failed`, `blocked`, or `exception-requested`, preserving Phase 16 source status separately. | yes |
| Reuse Phase 16 status vocabulary | Let pending/manual/live-service statuses appear directly as Phase 25 status. | |

**User's choice:** Auto-selected recommended approach: normalize to v1.2 statuses.
**Notes:** Pending live-service inputs cannot count as Phase 25 passes.

## Live-Service Coverage and Redaction

| Option | Description | Selected |
|--------|-------------|----------|
| Distinct service rows | Preserve service surface, mode, evidence type, redaction summary, and residual risk per scenario. | yes |
| Aggregate network pass | Collapse Connect/WUI/TLS/transfer/proxy/crash scenarios into one result. | |

**User's choice:** Auto-selected recommended approach: distinct service rows.
**Notes:** This keeps Connect, WUI, TLS, proxy, transfer, negative-protocol, long-transfer, and crash-dump evidence independently reviewable.

## Retained Artifacts and Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 23/24 retained-output pattern | Write manifest, normalized summary, redacted summary, template, artifact summary, snapshots, and upstream row under `build/ci-evidence/phase25`. | yes |
| Ad hoc output files | Write only a prose summary. | |

**User's choice:** Auto-selected recommended approach: Phase 23/24 retained-output pattern.
**Notes:** Later acceptance phases need machine-readable upstream rows.

## Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Focused Python tests plus Bazel/just wiring | Cover positive and negative packet validation, secret guards, outputs, and wiring. | yes |
| Manual-only verification | Rely on reviewer inspection. | |

**User's choice:** Auto-selected recommended approach: focused tests plus Bazel/just wiring.
**Notes:** Local quick mode remains blocked placeholder evidence until maintainers provide real live-service inputs.

## the agent's Discretion

- Exact file names and JSON field names may follow the Phase 23/24 conventions.
- The implementation may be a new Phase 25 wrapper around Phase 16 rather than edits to Phase 16 itself.

## Deferred Ideas

- Release/signing/provenance and broad upstream result evidence belongs to Phase 26.
- Retained-code, residual-risk, exception, and final maintainer acceptance decisions belong to Phase 27 and Phase 28.
