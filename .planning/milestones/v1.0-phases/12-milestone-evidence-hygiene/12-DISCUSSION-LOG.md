# Phase 12: Milestone Evidence Hygiene - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-15T18:32:52.775Z
**Phase:** 12-milestone-evidence-hygiene
**Mode:** Yolo
**Areas discussed:** cleanup scope, requirement and roadmap metadata, validation and cutover evidence, verification strategy

---

## Cleanup Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Metadata-only cleanup | Limit work to audit-identified planning, validation, and evidence metadata drift. | yes |
| Reopen implementation behavior | Treat audit findings as product implementation gaps. | |
| Start v2 evidence execution | Move directly into simulator/hardware/live-service evidence. | |

**User's choice:** Auto-selected metadata-only cleanup.
**Notes:** The audit found tech debt, not local implementation blockers.

## Requirement and Roadmap Metadata

| Option | Description | Selected |
|--------|-------------|----------|
| Align existing evidence metadata | Make requirements and roadmap status agree with already-passed phase evidence. | yes |
| Reset requirements to pending | Treat metadata drift as unsatisfied product behavior. | |
| Leave drift until archival | Accept the audit debt and archive anyway. | |

**User's choice:** Auto-selected align existing evidence metadata.
**Notes:** `BAZL-03`, `BAZL-05`, and Phase 9 progress are the primary cleanup targets.

## Validation and Cutover Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Remove stale wording, preserve blockers | Update stale metadata while keeping non-local cutover gates blocked. | yes |
| Mark all cutover evidence passed | Overclaim simulator, hardware, live-service, release, and retained-code proof. | |
| Leave stale wording | Keep contradictory evidence text. | |

**User's choice:** Auto-selected remove stale wording, preserve blockers.
**Notes:** Reference demotion remains intentionally blocked until non-local evidence exists.

## Verification Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse Phase 11 verifier modes and re-audit | Validate cleanup with existing deterministic checks plus a follow-up milestone audit. | yes |
| Add a new verifier first | Create new tooling before trying the existing checks. | |
| Manual inspection only | Rely on human review without executable evidence. | |

**User's choice:** Auto-selected reuse Phase 11 verifier modes and re-audit.
**Notes:** Existing verifier modes already cover requirement, wiring, cutover, and aggregate evidence.

## the agent's Discretion

- Exact wording and table edits may be chosen by the agent as long as they are minimal and audit-traceable.

## Deferred Ideas

- v2 non-local evidence execution remains outside Phase 12.
