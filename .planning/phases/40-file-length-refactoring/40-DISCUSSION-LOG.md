# Phase 40: File Length Refactoring - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-27
**Phase:** 40-file-length-refactoring
**Mode:** Yolo
**Areas discussed:** Exception governance, deep-module strategy, campaign delivery, verification evidence

## Exception governance

| Option | Description | Selected |
| --- | --- | --- |
| Reason-tagged exact-path ledger | Use the managed checker's native exact-path exceptions plus stable reasons and focused invariant verification. | ✓ |
| Typed policy manifest plus generated ledger | Maintain richer typed metadata and generate the checker input. | |
| Merge-base ratchet | Compare the ledger against a target-branch baseline. | |

**User's choice:** Make the checker green immediately with exact exceptions, then shrink the owned temporary set to zero.
**Notes:** The permanent set is 838 provenance/declarative files plus exactly three approved owned deep-module exceptions.

## Deep-module strategy

| Option | Description | Selected |
| --- | --- | --- |
| Stable façade with private concept modules | Preserve external interfaces while concentrating implementation behind deep private modules. | ✓ |
| Separate internal targets | Add package, crate, or library seams where dependency closure warrants them. | |
| Staged compatibility adapters | Move stateful behavior gradually behind temporary adapters. | |

**User's choice:** Broad internal redesign is allowed while every external contract remains stable.
**Notes:** Concept-oriented modules are required; numbered chunks and shallow pass-through modules are rejected.

## Campaign delivery

| Option | Description | Selected |
| --- | --- | --- |
| Fully serial micro-changes | Merge each small change before beginning the next. | |
| Shallow stacks | Prepare multiple dependent changes concurrently. | |
| Serial campaign gates with limited intra-campaign parallelism | Keep the fixed low-risk-to-high-risk order while parallelizing only non-overlapping work inside one campaign. | ✓ |

**User's choice:** Ratchet in small reviewable waves, lowest risk first, with `marlin_server.cpp` last.
**Notes:** A temporary exception leaves the ledger only with its verified refactor.

## Verification evidence

| Option | Description | Selected |
| --- | --- | --- |
| Risk-tiered campaign evidence | Record targeted evidence per campaign and reconcile it at final acceptance. | ✓ |
| Uniform full matrix | Run every available cross-stack gate for every change. | |
| Targeted checks plus final dossier | Keep only lightweight campaign records and rerun everything at the end. | |

**User's choice:** Use characterization, targeted tests, builds, and simulator evidence in proportion to risk.
**Notes:** Physical hardware is reserved for behavior changes or simulator gaps. Wrapper commands that only print instructions do not count as executed evidence.

## the agent's Discretion

- Private module names and exact task grouping within the locked campaign structure.
- Minimal enforcement tooling around the native exception ledger.

## Deferred Ideas

None.
