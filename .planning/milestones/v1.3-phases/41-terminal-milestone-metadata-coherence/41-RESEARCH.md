---
phase: 41
slug: terminal-milestone-metadata-coherence
status: complete
researched: 2026-08-01
---

# Phase 41 — Research

## Research Summary

Phase 41 should extend the repository's existing Python/Bazel verifier style, not add a new planning schema or depend on a user-local GSD installation at runtime. The repair has two distinct responsibilities:

1. Reconcile current projections from already-passed lifecycle evidence.
2. Add a read-only consistency gate that independently prevents the same projections from drifting before audit or archival.

The current gap audit establishes the failure precisely: runtime flows are green, but ROADMAP, REQUIREMENTS, STATE, exact plan inventories, and three VALIDATION files disagree. A successful plan must preserve this separation and must never use the current audit as evidence that makes its own findings pass.

## Existing Patterns to Reuse

### Python functional core with thin CLI

`tools/bazel/phase22_metadata_reconciliation.py` and its policy/tests establish the repository pattern: parse planning inputs, evaluate deterministic policy, publish or report bounded results, expose a command-line entrypoint, wire it into `tools/bazel/BUILD.bazel`, and wrap it with `just`.

Phase 22 is useful as a structural precedent but not as a complete implementation. Its verifier is tied to the earlier phase contract and output bundle. Phase 41 needs a smaller read-only normalized snapshot dedicated to terminal coherence.

Recommended split:

- `phase41_terminal_consistency.py`: filesystem/frontmatter/Markdown boundary parsing and CLI.
- `phase41_terminal_consistency_policy.py`: pure normalized models and comparison rules.
- `phase41_terminal_consistency_test.py`: coherent fixture plus one-invariant mutations.
- Optional fixture helper only if it keeps each test focused and below the file-length trigger.

### Supported GSD mutation and discovery surfaces

Use GSD commands for surfaces they own:

- `requirements mark-complete <ids>` for requirement checkbox and traceability completion.
- `roadmap update-plan-progress <phase>` and `roadmap update-status <phase>` where their output is the intended target.
- `state planned-phase`, `state begin-phase`, progress/session helpers, and execution completion helpers for STATE.
- `summary-extract`, `roadmap analyze`, `init milestone-op`, `phase-plan-index`, and lifecycle verification for discovery and assertions.

Phase 39 proved that supported commands may not synthesize every exact plan-list or narrative field and may rewrite historical projections unexpectedly. Plans must specify bounded exceptions explicitly: run the supported command first, restore only proven historical fields when needed, edit only the unsupported projection, and require byte-for-byte or exact-set assertions immediately afterward.

### Bazel and just integration

Follow the existing `py_binary`/`py_test` phase targets in `tools/bazel/BUILD.bazel`. Expose one stable `just phase41-verify` recipe that runs:

1. focused Python/Bazel policy tests;
2. the live repository checker in the appropriate mode;
3. `bun scripts/bright-builds-check.ts all` without modifying the managed checker.

The terminal checker must not read `$HOME/.codex` during normal Bazel/CI execution. GSD commands are suitable for workflow-owned mutation and supplementary discovery, not as the checker implementation dependency.

## Normalized Authority Model

Parse raw artifacts into explicit internal types before comparison:

- `RequirementRecord`: ID, checkbox completion, traceability phase/status, plan claims, summary completion evidence, verification evidence.
- `PhaseRecord`: phase number/name, roadmap status, disk lifecycle state, completion date, requirement ownership.
- `PlanInventory`: exact sorted PLAN basenames, exact sorted SUMMARY basenames, roadmap listed basenames, count projection.
- `ValidationRecord`: phase number, `nyquist_compliant`, `wave_0_complete`, exact task/campaign statuses, sign-off.
- `MilestoneProjection`: ROADMAP milestone label/coverage/progress, REQUIREMENTS rollup, STATE counters/position, audit verdict/scores.

Do not compare duplicated counts to decide truth. Derive expected values from exact evidence sets and then compare every projection to that expectation.

## Required Checker Modes

### Pre-audit

Require:

- exact ROADMAP/REQUIREMENTS/STATE agreement for all lifecycle evidence available before the audit;
- exact phase-local PLAN/SUMMARY inventories;
- all prior and current Nyquist validation records complete with no partial or missing phase;
- no stale milestone narrative that claims archival readiness;
- no requirement semantic text changes relative to the scoped repair.

This mode may accept Phase 41 as executed/verified but not yet archival-ready.

### Pre-archive

Require everything from pre-audit plus:

- a fresh audit covering Phases 31–41;
- exactly sixteen coherent requirements;
- zero integration, flow, metadata, or Nyquist gap;
- terminal milestone lifecycle state that agrees with the fresh audit.

### Exit and diagnostic contract

- Exit `0`: selected mode fully coherent.
- Exit `1`: missing, malformed, stale, contradictory, partial, or otherwise incoherent repository state.
- Exit `2`: invalid CLI invocation only.
- Emit deterministic sorted violations containing a stable code, artifact path, observed value, and expected value.
- Never repair state implicitly; the checker is read-only.

## Current Reconciliation Targets

- ROADMAP: milestone narrative, Phase 41 ownership, all sixteen requirement rows/rollups, exact Phase 36/37/39 plan lists, Phase 41 plan inventory, and progress row.
- REQUIREMENTS: all sixteen checkbox/traceability/coverage surfaces with seven IDs owned by Phase 41 without altering requirement prose.
- STATE: phase/milestone position, phase counts, plan counts, current focus, and completion narrative through supported GSD lifecycle operations.
- Phase 37 VALIDATION: replace five pending task rows and Wave 0 placeholders only where Phase 37 plans/summaries/verification and executed tests prove green.
- Phase 38 VALIDATION: replace five pending task rows and Wave 0 placeholders only where Phase 38 evidence proves green.
- Phase 40 VALIDATION: reconcile `wave_0_complete`, campaign rows, Wave 0 items, sign-off, and executed command evidence from all eighteen summaries plus verification.
- Milestone audit: replace the current diagnostic `gaps_found` report only after pre-audit is green and Phase 41 verification exists.

## Test Strategy

Build one minimal coherent fixture tree and mutate one concern per unit test. Required negative tests include:

- unchecked requirement or non-Complete traceability row;
- missing, duplicate, or extra requirement ID;
- wrong requirement owner or changed requirement prose hash/snapshot;
- wrong phase status/count/date projection;
- missing, extra, cross-owned, or count-only plan inventory mismatch;
- PLAN without SUMMARY and SUMMARY without PLAN;
- STATE phase/plan counters or narrative disagreeing with disk evidence;
- validation file missing, `nyquist_compliant: false`, `wave_0_complete: false`, pending/red task row, or incomplete sign-off;
- historical `gaps_found` audit presented as fresh/pass evidence;
- pre-archive without Phase 41 verification, eleven-phase scope, sixteen coherent requirements, or zero gap totals;
- malformed frontmatter, missing file, duplicate table row, or unsupported status fails closed;
- deterministic diagnostic ordering and exit codes 0/1/2.

Add a live-repository smoke test/target using declared `.planning` inputs so fixture correctness cannot mask parser drift.

## Validation Architecture

### Sampling layers

1. **Task-level:** focused Python unit tests for the normalized model or one reconciliation surface; `git diff --check`; managed Bright Builds check for touched source files.
2. **Wave-level:** Bazel policy test target plus the live checker in the least strict currently satisfiable mode.
3. **Pre-verification:** `just phase41-verify`, ordered Rust workspace checks, exact changed-path review, and lifecycle validation.
4. **Terminal acceptance:** Nyquist discovery with zero partial/missing phases, Phase 41 verification, pre-audit checker, one fresh official audit, then pre-archive checker.

### Wave 0

Wave 0 must create the checker core/CLI/tests and Bazel/`just` wiring before any metadata repair depends on it. The live checker is expected to fail on the current repository with named M1/Nyquist violations; fixture tests and malformed-input behavior must already pass.

### Threats to test

- Circular authority: audit or duplicated rollup used as source evidence.
- Status laundering: metadata changed without plan/summary/verification support.
- Inventory spoofing: counts agree while filenames or ownership differ.
- Partial Nyquist: compliant frontmatter paired with pending task/campaign rows.
- Stale audit: old timestamp/scope/verdict accepted as terminal.
- Parser ambiguity: duplicate rows, malformed frontmatter, unsupported status, or missing input silently ignored.
- Secret leakage: diagnostics copy evidence payloads instead of paths/IDs/statuses.

## Planning Recommendations

Use three sequential plans:

1. Build and prove the fail-closed checker on fixtures and the current intentionally failing live tree.
2. Reconcile ROADMAP/REQUIREMENTS/STATE and exact plan inventories through supported mutations plus narrowly asserted exceptions.
3. Reconcile Nyquist evidence, run the complete gate, create terminal verification/audit evidence, and prove pre-archive mode.

Do not parallelize plans that share ROADMAP, REQUIREMENTS, STATE, validation files, or audit inputs. Preserve the existing modified gap audit until the final audit task is authorized by all prerequisites.

## Sources

- `.planning/phases/41-terminal-milestone-metadata-coherence/41-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/v1.3-MILESTONE-AUDIT.md`
- `.planning/phases/39-milestone-metadata-reconciliation/39-01-PLAN.md`
- `.planning/phases/39-milestone-metadata-reconciliation/39-VERIFICATION.md`
- `.planning/phases/37-reconcile-decisions-into-readiness/37-VALIDATION.md`
- `.planning/phases/38-fail-closed-cutover-workflow/38-VALIDATION.md`
- `.planning/phases/40-file-length-refactoring/40-VALIDATION.md`
- `tools/bazel/phase22_metadata_reconciliation.py`
- `tools/bazel/phase22_metadata_reconciliation_test.py`
- `tools/bazel/BUILD.bazel`
- `justfile`
