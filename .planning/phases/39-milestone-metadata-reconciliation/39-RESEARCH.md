---
phase: 39-milestone-metadata-reconciliation
generated_by: gsd-phase-researcher-fallback
lifecycle_mode: yolo
phase_lifecycle_id: 39-2026-07-29T01-32-55
generated_at: 2026-07-29T01:55:17.224000Z
status: complete
---

# Phase 39 Research: Milestone Metadata Reconciliation

## Research Summary

Phase 39 is a narrow planning-metadata repair. The underlying Phase 31 intake behavior and Phase 36 through Phase 38 gap-closure behavior already have passed verification reports. The remaining contradictions are:

1. `31-01-SUMMARY.md` omits the only completion key consumed by `summary-extract`.
1. The Phase 31, Phase 32, and Phase 34 roadmap detail blocks do not list their own on-disk plan/summary pairs.
1. Seven v1.3 requirement checkboxes and traceability statuses remain pending even though their owning gap-closure phases passed.
1. Phase 39 itself has no plan, summary, or verification evidence yet.

The smallest robust plan edits the historical summary additively, repairs the three roadmap inventories, uses the supported requirement mutation command after execution, and verifies the resulting sixteen-requirement matrix before a new milestone audit. It should not rerun external evidence collection, change Phase 31 through Phase 38 implementation code, touch Phase 40, or refresh the canonical audit before Phase 39 verification passes.

## Exact Metadata Mechanics

### Supported summary extraction

`$HOME/.codex/get-shit-done/bin/lib/commands.cjs` maps only:

```text
requirements_completed: fm['requirements-completed'] || []
```

The exact verification command is:

```bash
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" \
  summary-extract \
  .planning/phases/31-final-evidence-intake/31-01-SUMMARY.md \
  --fields requirements_completed
```

The result must contain exactly `INTAKE-01`, `INTAKE-02`, `INTAKE-03`, and `INTAKE-04`. Do not add `requirements_completed`; it is not read.

The Phase 31 summary backfill must not modify `phase`, `plan`, `status`, `generated_by`, `lifecycle_mode`, `phase_lifecycle_id`, `generated_at`, or `completed_at`.

### Roadmap plan inventory

The phase directories are the artifact source of truth:

| Phase | Plans | Summaries | Required roadmap inventory                             |
| ----- | ----: | --------: | ------------------------------------------------------ |
| 31    |     1 |         1 | `1 plan`, `31-01-PLAN.md` checked                      |
| 32    |     1 |         1 | `1 plan`, `32-01-PLAN.md` checked                      |
| 34    |     2 |         2 | `2 plans`, `34-01-PLAN.md` and `34-02-PLAN.md` checked |

Use plan objectives and summaries for the descriptions. Do not list Phase 36 through Phase 38 plans under these phases.

`roadmap get-phase` reads the manual detail section, while `roadmap analyze` derives plan and summary counts from disk. Verification must compare both views:

```bash
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 31
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 32
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap get-phase 34
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze
```

### Requirement status

Use the supported mutation command rather than ad hoc checkbox rewriting:

```bash
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" requirements mark-complete \
  INTAKE-01 INTAKE-02 INTAKE-03 READY-02 READY-03 CUTOVER-01 CUTOVER-03
```

This command updates both requirement checkboxes and traceability statuses. Run it only after confirming the relevant passed verification and summary evidence:

- Phase 31: `INTAKE-01` through `INTAKE-04`
- Phase 38: `READY-02`, `READY-03`, `CUTOVER-01`, `CUTOVER-03`
- Phase 39: `INTAKE-01`, `INTAKE-02`, `INTAKE-03` metadata reconciliation

The executor's normal plan-completion flow will copy Phase 39's plan requirements verbatim into `39-01-SUMMARY.md` and invoke the same requirement command for the Phase 39 IDs.

## Files in Scope

Required phase-work edits:

- `.planning/phases/31-final-evidence-intake/31-01-SUMMARY.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md` through `gsd-tools.cjs requirements mark-complete`
- `.planning/phases/39-milestone-metadata-reconciliation/39-VALIDATION.md`
- `.planning/phases/39-milestone-metadata-reconciliation/39-01-PLAN.md`

Workflow-owned outputs after execution:

- `.planning/phases/39-milestone-metadata-reconciliation/39-01-SUMMARY.md`
- `.planning/phases/39-milestone-metadata-reconciliation/39-VERIFICATION.md`
- `.planning/STATE.md`
- `.planning/ROADMAP.md` Phase 39 completion and plan status

Out of scope:

- evidence-gate implementation under `tools/bazel/`
- raw or secret-bearing evidence
- external evidence collection
- Phase 40 artifacts
- production cutover or reference demotion
- canonical audit refresh before Phase 39 passes

## Security Threat Boundaries

### T-39-01: False completion

Metadata must not mark a requirement complete unless a plan claim, supported summary extraction, and passed verification evidence agree.

### T-39-02: Historical provenance corruption

The Phase 31 backfill must not change original lifecycle, timestamps, status, or narrative evidence.

### T-39-03: Cross-phase plan substitution

Roadmap inventory must use exact phase-prefixed filenames and matching summaries so later gap-closure plans cannot be copied into an earlier phase.

### T-39-04: Audit laundering

Metadata edits must not hide a semantic integration gap. A fresh audit finding remains blocking and routes to separate repair.

### T-39-05: Sensitive evidence disclosure

Planning artifacts may contain IDs, paths, statuses, counts, and sanitized refs only. They must not copy packet bodies, private keys, tokens, certificates, crash dumps, or service payloads.

No high-severity threat may remain open. A Phase 39 plan should include a `<threat-model>` block covering these threats.

## Pitfalls to Avoid

- Adding the unsupported underscore completion key.
- Rewriting the whole Phase 31 summary instead of adding one field.
- Using `roadmap analyze` alone; it does not prove the manual plan list is correct.
- Marking requirements complete before the evidence matrix agrees.
- Editing `.planning/STATE.md` directly instead of using GSD commands.
- Updating the old audit result before Phase 39 verification and lifecycle validation pass.
- Running all Phase 31 through Phase 40 behavior suites for a metadata-only change.

## Validation Architecture

### Layer 1: Changed-file and formatting guard

```bash
git diff --check
mdformat --check \
  .planning/ROADMAP.md \
  .planning/REQUIREMENTS.md \
  .planning/phases/31-final-evidence-intake/31-01-SUMMARY.md
```

Review `git diff --name-only` and reject implementation changes outside the locked metadata scope.

### Layer 2: Summary extraction

Run `summary-extract` for every v1.3 summary and build a set of completed IDs. The Phase 31 result must contain all four intake IDs. Phase 39's summary must contain `INTAKE-01` through `INTAKE-03`.

### Layer 3: Roadmap inventory

For Phases 31, 32, and 34, compare:

- manual `roadmap get-phase` plan count/list;
- on-disk `*-PLAN.md` count;
- on-disk `*-SUMMARY.md` count;
- `roadmap analyze` `plan_count`, `summary_count`, and `disk_status`.

All exact filenames and counts must agree.

### Layer 4: Sixteen-requirement matrix

For every v1.3 requirement ID, require:

- checked requirement checkbox;
- `Complete` traceability status;
- appearance in supported summary extraction;
- passed owning phase verification evidence.

The matrix must report 16/16 with no missing or duplicate IDs.

### Layer 5: Phase and lifecycle gate

Require `39-VERIFICATION.md` status `passed`, then run:

```bash
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" \
  verify lifecycle 39 --require-plans --require-verification --raw
```

Only after both pass may the normal milestone-audit workflow refresh `.planning/v1.3-MILESTONE-AUDIT.md`.

### Repository pre-commit gates

Before each commit, run:

```bash
bun scripts/bright-builds-check.ts all
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

No manual-only behavior is required; all Phase 39 outcomes are deterministic Markdown, YAML frontmatter, and GSD CLI behavior.

## RESEARCH COMPLETE
