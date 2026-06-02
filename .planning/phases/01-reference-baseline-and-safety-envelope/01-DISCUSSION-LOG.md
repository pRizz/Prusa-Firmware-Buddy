# Phase 1: Reference Baseline and Safety Envelope - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-02T15:50:10.638Z
**Phase:** 1-Reference Baseline and Safety Envelope
**Mode:** Yolo
**Areas discussed:** Baseline Matrix, Reference Capture, Concern Ledger, Safety Envelope, Verification Strategy

---

## Baseline Matrix

| Option | Description | Selected |
|--------|-------------|----------|
| Derived matrix | Derive printer, board, MCU, feature, bootloader, and artifact data from existing build/config sources. | yes |
| Manual matrix | Write a manually curated maintainer table. | |
| Future Bazel matrix | Wait until Bazel authority exists before defining the baseline. | |

**User's choice:** Auto-selected derived matrix.
**Notes:** This keeps Phase 1 anchored to the existing C/C++/CMake reference and avoids inventing unsupported combinations.

## Reference Capture

| Option | Description | Selected |
|--------|-------------|----------|
| Capture contract first | Define commands, inputs, outputs, evidence classes, and artifact locations for existing reference workflows. | yes |
| Full fixture capture now | Run or store every heavy build, simulator, protocol, and hardware artifact immediately. | |
| Defer capture to Bazel phase | Wait until Phase 2/3 before naming reference capture surfaces. | |

**User's choice:** Auto-selected capture contract first.
**Notes:** Phase 1 should make the oracle explicit without overloading the first phase with hardware and CI-only work.

## Concern Ledger

| Option | Description | Selected |
|--------|-------------|----------|
| Classify known concerns | Seed from `.planning/codebase/CONCERNS.md` and classify each concern as preserved, fixed during rewrite, or deferred. | yes |
| Fix concerns immediately | Start repairing defects while creating the baseline. | |
| Ignore concerns until subsystem phases | Let later phases rediscover fragile areas independently. | |

**User's choice:** Auto-selected classify known concerns.
**Notes:** Silent behavior changes would weaken parity evidence, so fixes need explicit later phase ownership.

## Safety Envelope

| Option | Description | Selected |
|--------|-------------|----------|
| Board-aware evidence map | Document safety flows by board/failure mode and classify required evidence as source, host, simulator, hardware, or manual. | yes |
| Generic safety checklist | Create one checklist that applies uniformly to all products. | |
| Hardware-only gate | Require physical hardware evidence before any safety envelope artifact is accepted. | |

**User's choice:** Auto-selected board-aware evidence map.
**Notes:** This keeps hardware gaps visible without pretending every item can be verified locally during Phase 1.

## Verification Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Artifact and traceability checks | Verify Phase 1 by checking created artifacts, requirement links, source references, and lightweight smoke commands. | yes |
| Full firmware parity suite | Require the complete future parity pyramid in Phase 1. | |
| Documentation only | Create docs with no automated checks. | |

**User's choice:** Auto-selected artifact and traceability checks.
**Notes:** The phase should be verifiable now while preserving heavier parity execution for later phases.

## the agent's Discretion

- Exact artifact names and validation script boundaries can be chosen during planning.
- The implementation can choose whether to use Markdown, JSON, or a small script as long as outputs are inspectable and rerunnable.

## Deferred Ideas

None.
