# Phase 38: Fail-Closed Cutover Workflow - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-26
**Phase:** 38-fail-closed-cutover-workflow
**Mode:** Yolo
**Areas discussed:** Durable authority replacement, Safe staged installation, End-to-end routing matrix

## Durable authority replacement

| Option | Description | Selected |
| --- | --- | --- |
| Phase-local staged fallbacks plus explicit workflow finalization | Phase 34 publishes a contract-defined blocked bundle for every source-validation failure; the workflow still runs Phase 35 before returning nonzero. | ✓ |
| Attempt-first blocked invalidation | Publish blocked Phase 34 and Phase 35 authority before running upstream commands. | |
| Generation directory plus atomic authority pointer | Publish versioned cross-phase generations and atomically select an approved or blocked authority generation. | |

**Agent's choice:** Phase-local staged fallbacks plus explicit workflow finalization.

**Notes:** This is the smallest change that preserves existing Phase 34/35 artifact boundaries. It closes B3 only when Phase 34 expands fallback coverage and workflow status handling no longer relies on `set -e` to skip Phase 35.

## Safe staged installation

| Option | Description | Selected |
| --- | --- | --- |
| Authority-aware backup restore | Restore the previous bundle only after proving it cannot revive stronger or stale authority. | |
| Fail-closed authority guard plus compensating restore | Publish a durable blocking guard before mutation, restore for availability on failure, and clear the guard only after a validated safe install. | ✓ |
| Immutable generations plus atomic active descriptor | Keep immutable bundles and switch a descriptor to the validated active generation. | |

**Agent's choice:** Fail-closed authority guard plus compensating restore.

**Notes:** A restore-only fix can revive the stale approval being replaced. The guard makes authority monotonic across the two-rename window while preserving a recoverable prior bundle for availability.

## End-to-end routing matrix

| Option | Description | Selected |
| --- | --- | --- |
| Shared workflow coordinator with one live-producer matrix plus focused install-fault tests | Reuse the Phase 31-through-34 real-producer fixture, extend it through Phase 35, and directly test the same coordinator called by the shell. | ✓ |
| Full isolated-workspace matrix through `rust_workflow.sh` | Run every path through the shell in isolated workspaces and inject source/install failures at subprocess boundaries. | |
| Contract-gated producer snapshots through Phase 34 and Phase 35 | Use deterministic snapshots and mutations for a fast matrix, with separate producer-shape checks. | |

**Agent's choice:** Shared workflow coordinator with one live-producer matrix plus focused install-fault tests.

**Notes:** This boundary proves real producer compatibility and production finalization behavior without a slow Cartesian-product shell suite. Demotion remains an orthogonal predicate matrix rather than being folded into the cutover verdict.

## the agent's Discretion

- Exact coordinator module, guard artifact, reason-code spellings, and helper boundaries.
- Fault-injection seam and test helper organization.
- Narrow module splits needed to keep Phase 38 changes readable.

## Deferred Ideas

- Immutable generation directories with an atomic active-generation pointer.
- Production cutover and reference demotion.
- Phase 39 milestone metadata reconciliation.
