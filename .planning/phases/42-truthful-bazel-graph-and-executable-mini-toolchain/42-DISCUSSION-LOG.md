# Phase 42: Truthful Bazel Graph and Executable MINI Toolchain - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the alternatives considered.

**Date:** 2026-08-03
**Phase:** 42-truthful-bazel-graph-and-executable-mini-toolchain
**Mode:** Yolo
**Areas discussed:** Hermetic toolchain and host policy, Explicit platform rejection, Truthful developer facade and reference separation

## Hermetic toolchain and host policy

| Option | Description | Selected |
| --- | --- | --- |
| Linux x86_64 full pipeline; Darwin unsupported | Smallest qualification surface; all Darwin paths fail. | |
| Linux x86_64 full pipeline; Darwin host-only tier | Canonical Linux owns embedded qualification; Darwin retains separately named host/reference work and fails embedded commands visibly. | ✓ |
| Full Linux and Darwin hermetic parity | Verify same-version native/Rosetta Arm GNU and Mini404 dependencies across both hosts now. | |

**User's choice:** Auto-selected Linux x86_64 full pipeline with a Darwin host-only/reference tier.
**Notes:** The selected policy matches the Linux-canonical research while preserving useful macOS work that cannot be mistaken for embedded qualification.

## Explicit platform rejection

| Option | Description | Selected |
| --- | --- | --- |
| Single canonical Bazel platform allowlist | Use native target/execution constraints for one supported embedded tuple and reject everything else. | ✓ |
| Reviewed manifest-generated platform allowlist | Generate platforms and rejection cases from one matrix manifest. | |
| Independent build settings with a validation transition | Select product, board, MCU, and target independently and validate combinations through transitions. | |

**User's choice:** Auto-selected the single canonical Bazel platform allowlist.
**Notes:** This is the smallest explicit model for a milestone that intentionally supports exactly one embedded tuple.

## Truthful developer facade and reference separation

| Option | Description | Selected |
| --- | --- | --- |
| Stable verbs with analysis-time capability gates | Preserve the facade; unavailable later-phase capabilities fail during analysis and point to genuine Phase 42 work. | ✓ |
| Implemented-only command surface | Remove familiar generic verbs until each final capability lands. | |
| Capability manifest with dispatcher | Centralize readiness in a runtime registry/dispatcher. | |

**User's choice:** Auto-selected stable verbs with analysis-time capability gates.
**Notes:** Executable reference commands move to `reference-*`; print-only previews move to `reference-*-plan`; environment switches cannot change one label's authority class.

## the agent's Discretion

- Exact Starlark/provider names, repository decomposition, Python patch, mirror layout, and diagnostics are left to research/planning within the locked boundary.

## Deferred Ideas

- Native Darwin embedded qualification.
- Additional product tuples.
- Final firmware link, package lineage, and simulator scenarios owned by later phases.
