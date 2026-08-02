# Phase 41: Terminal Milestone Metadata Coherence - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01T16:34:58.401Z
**Phase:** 41-terminal-milestone-metadata-coherence
**Mode:** Yolo
**Areas discussed:** Terminal metadata authority, fail-closed consistency enforcement, Nyquist and audit sequencing

***

## Terminal Metadata Authority

| Option | Description | Selected |
| --- | --- | --- |
| Peer-authoritative documents | Keep each planning document independently authoritative and reconcile manually. | |
| Evidence-led authority with CLI-owned projections | Derive duplicated projections from plans, summaries, verification, validation evidence, and supported GSD mutations. | ✓ |
| Canonical milestone manifest with generated documents | Introduce a new manifest that generates all terminal documents. | |

**User's choice:** Evidence-led authority with CLI-owned projections (recommended default)
**Notes:** Preserves verified requirement meaning, avoids circular authority, and treats the audit as a consumer rather than a source.

## Fail-Closed Consistency Enforcement

| Option | Description | Selected |
| --- | --- | --- |
| Repo-owned Python normalized-snapshot checker with thin CLI | Use a pure normalized comparison core, deterministic violations, fixtures, Bazel, and `just`. | ✓ |
| Repo-owned Bun/TypeScript companion checker | Build a separate Bun checker adjacent to the managed Bright Builds checker. | |
| Thin orchestrator over installed `gsd-tools.cjs` | Depend on the developer's installed GSD commands plus shell/Node assertions. | |

**User's choice:** Repo-owned Python normalized-snapshot checker with thin CLI (recommended default)
**Notes:** Best matches Bazel-primary repository patterns and remains runnable in clean CI without depending on a user-local GSD installation.

## Nyquist and Audit Sequencing

| Option | Description | Selected |
| --- | --- | --- |
| Evidence-first, single final audit | Reconcile executed validation evidence, complete and verify Phase 41, then run one authoritative audit. | ✓ |
| Two-pass audit-driven closure | Replace the audit with an intermediate result and then replace it again after repair. | |
| Generated terminal projection | Generate all planning surfaces from a new projector before auditing. | |

**User's choice:** Evidence-first, single final audit (recommended default)
**Notes:** Keeps the existing gap audit diagnostic, prevents premature completion, and makes the final audit an external acceptance gate.

## the agent's Discretion

- Concrete Python module/type layout, violation-code names, fixture layout, and CLI output format.
- Exact supported GSD commands and bounded edits used for terminal projections.

## Deferred Ideas

None.
