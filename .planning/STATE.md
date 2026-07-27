---
gsd_state_version: "1.0"
milestone: v1.3
milestone_name: Cutover Approval and Reference Demotion Trial
status: executing
stopped_at: Completed 40-03-PLAN.md
last_updated: "2026-07-27T19:05:49.302Z"
last_activity: "2026-07-27"
progress:
  total_phases: 10
  completed_phases: 8
  total_plans: 29
  completed_plans: 17
  percent: 59
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-27)

**Core value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.
**Current focus:** Phase 40 — File Length Refactoring

## Current Position

Milestone: v1.3 Cutover Approval and Reference Demotion Trial - active
Phase: 40 (File Length Refactoring) — EXECUTING
Plan: 4 of 15
Status: Ready to execute
Last activity: 2026-07-27

Progress: [########--] 80% (8/10 v1.3 phases complete; Phases 39 and 40 pending independently)

## Performance Metrics

**Velocity:**

- v1.3 plans completed: 16/29 currently planned
- v1.3 phases completed: 8/10
- Previous milestone baseline: v1.2 completed 9 plans across 8 phases
- Earlier milestone baseline: v1.1 completed 13 plans across 10 phases

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 31. Final Evidence Intake | 1/1 | - | - |
| 32. Blocker Register and Evidence Triage | 1/1 | 19min | 19min |
| 33. Maintainer Decision Inputs | 1/1 | 15min | 15min |
| 34. Final Readiness and Demotion Dry Run | 2/2 | - | - |
| 35. Cutover Decision Artifact | 2/2 | 34m42s | 17m21s |
| 36. Normalize Evidence and Blocker Rows | 2/2 | 39min | 19m30s |
| 37 | 2 | - | - |
| 38. Fail-Closed Cutover Workflow | 3/3 | 59min | 19m40s |
| 40. File Length Refactoring | 2/15 | 24m | 12m |

**Recent Trend:**

- Last 5 completed plans: Phase 38 P01, Phase 38 P02, Phase 38 P03, Phase 40 P01, Phase 40 P02
- Trend: Phase 40 retired its first four temporary paths through stable Rust-domain façades and private test extraction; Phase 39 remains pending independently.

**Recent Completed Plan Detail:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 32 P01 | 19min | 3 tasks | 8 files |
| Phase 33 P01 | 15min | 3 tasks | 8 files |
| Phase 35 P01 | 20m42s | 3 tasks | 8 files |
| Phase 35 P02 | 14min | 2 tasks | 3 files |
| Phase 36 P01 | 28min | 3 tasks | 7 files |
| Phase 36 P02 | 11min | 2 tasks | 2 files |
| Phase 37 P01 | 12min | 2 tasks | 5 files |
| Phase 37 P02 | 22min | 3 tasks | 6 files |
| Phase 38 P01 | 21min | 2 tasks | 6 files |
| Phase 38 P02 | 19min | 3 tasks | 7 files |
| Phase 38 P03 | 19min | 2 tasks | 7 files |
| Phase 40 P01 | 11m | 2 tasks | 7 files |
| Phase 40 P02 | 13m | 2 tasks | 18 files |
| Phase 40 P03 | 20m | 2 tasks | 10 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- v1.2 uses continuous phase numbering and starts at Phase 23 because v1.1 ended at Phase 22.
- v1.2 scope is execution and acceptance only; it does not redefine v1.0 parity contracts or v1.1 gate schemas unless a failed evidence row forces follow-up work.
- Final readiness stays blocked by default unless every required evidence gate passes or has an explicit approved exception.
- Reference demotion remains a separate explicit maintainer approval and is not automatic.
- Phase 30 is requirement-neutral metadata cleanup; it does not create new requirement IDs or reopen the completed v1.2 requirement coverage.
- [v1.2-complete]: Archived v1.2 roadmap, requirements, audit artifacts, and phase directories under `.planning/milestones/`; `/gsd-new-milestone` started from a fresh scope.
- [v1.3-start]: Scope v1.3 as cutover approval and reference-demotion trial work: real evidence intake, blocker triage, maintainer decisions, final readiness, demotion dry-run behavior, and a go/no-go artifact.
- [v1.3-roadmap]: Phase numbering continues after v1.2, so v1.3 starts at Phase 31 and runs through Phase 35.
- [v1.3-roadmap]: Requirements map to five milestone categories: evidence intake, evidence triage, maintainer decisions, readiness/demotion trial, and cutover decision.
- [v1.3-roadmap]: All 16 v1.3 requirements are mapped exactly once; no orphaned or duplicate mappings remain.
- [v1.3-roadmap]: Reference demotion remains fail-closed and requires a separate explicit maintainer approval; green evidence alone cannot authorize demotion.
- [Phase 32]: Phase 32 preserves Phase 31 as the finality/provenance boundary and follows accepted receipt row refs only after Phase 31 outputs load.
- [Phase 32]: Phase 32 emits blocker classification and downstream handoff state only; it does not approve exceptions, retained code, readiness, demotion, or cutover.
- [Phase 35]: Phase 35 derives verdict JSON, route JSON, and Markdown from one exact nine-kind canonical audit-link index.
- [Phase 35]: Blocked and approved-with-exceptions verdicts route to targeted repair and require a fresh cutover decision.
- [Phase 35]: Phase 33 demotion decision validation/value/source and the Phase 34 demotion gate remain independent from the cutover verdict.
- [Phase 35]: Any source-boundary failure publishes the exact durable three-artifact blocked bundle before the command returns nonzero.
- [Phase 35]: Both normal and failure bundles are validated in sibling staging directories before replacing the canonical output.
- [Phase 35]: Failure output keeps cutover verdict, demotion validation and value, source lineage, and demotion gate state independent.
- [Phase 36]: Canonical blocker row IDs derive only from the immutable producer source tuple; decision axis and subject remain a separate exact resolution identity.
- [Phase 36]: Phase 26 release tables are adapted only through an accepted-final Phase 31 receipt bound to the exact contracted artifact path.
- [Phase 36]: Recognized malformed and unsupported Phase 27/28 producer containers publish visible critical proof-ineligible rows while valid empty and nested producer bundles remain supported.
- [Phase 37]: Resolve decisions only through the complete row_ref + decision_axis + decision_subject_id identity.
- [Phase 37]: Treat conflicting typed targets as blockers instead of selecting a decision by timestamp.
- [Phase 37]: Keep canonical demotion authorization independent from readiness effects.
- [Phase 37]: Keep Phase 31 accepted-final receipts as the sole evidence completeness authority while Phase 32 contributes distinct canonical decision-domain rows.
- [Phase 37]: Derive retained Phase 34 views from one typed ledger while keeping demotion-only diagnostics independent from readiness.
- [Phase 37]: Run all Phase 33/34 reconciliation suites through the existing just phase34-verify facade before publication.
- [Phase 38]: Publish fixed-path private blocking shells before structured workflow-attempt or Phase 34 publication-state payloads so incomplete publication cannot revive stale authority.
- [Phase 38]: Accept a nonzero Phase 34 result only when persisted blocked authority matches the coordinator's exact attempt and safe reason.
- [Phase 38]: Treat a safe blocked fallback as authority state, not operational success; Phase 35 validation and source failures remain nonzero.
- [Phase 40]: Phase 40 added: File Length Refactoring — Execute the approved ratcheting program after Phase 39 without changing Phase 39 scope.
- [Phase 40]: The checker-consumed TSV is the sole active exception authority; embedded sets define immutable policy boundaries only.
- [Phase 40]: Temporary membership may only shrink, while owned permanence is restricted to the three locked deletion-test conversions.
- [Phase 40]: Terminal mode requires exactly the frozen 838 paths plus all three locked owned paths and no temporary reasons.
- [Phase 40]: Network and auxiliary preserve their public module paths through explicit facades over private concept modules.
- [Phase 40]: Feature and GUI retain cohesive production modules and move only cfg(test) suites into private children.
- [Phase 40]: Historical API verifiers follow declared private Rust children instead of requiring dead facade shims.
- [Phase 40]: Build configuration, preset generation, and artifact publication live behind a stable utils/build.py CLI and import facade.
- [Phase 40]: Phase-stepping numerical transforms remain pure; direct Serial and Plotly imports are confined to adapters while phase_stepping.py preserves every original public definition.
- [Phase 40]: Temporary utility exceptions are retired only after byte-for-byte CLI/generated-output comparisons and an executed representative build.

### Pending Todos

- Keep real evidence artifacts sanitized; use external refs for private keys, tokens, certificates, service payloads, raw crash dumps, and other secret-bearing data.

### Blockers/Concerns

- Real simulator, hardware/media/safety, live-service, release/signing, upstream-result, retained-code, residual-risk, and maintainer-decision inputs must be supplied externally.
- Evidence artifacts must avoid private signing keys, tokens, certificates, service payloads, raw crash dumps, and other secret-bearing data.
- Hardware availability and failure-injection scope can block final readiness if required scenarios cannot be observed or explicitly exception-approved.
- Quick/default placeholder outputs, smoke fixtures, and local-only dry-run rows must not be accepted as final cutover proof.
- Reference demotion must remain blocked unless readiness is otherwise unblocked and a valid explicit maintainer demotion approval is supplied.
- Post-cutover retained vendor/HAL replacement and long-run dashboards are deferred unless v1.3 evidence reveals a narrow decision-blocking defect.

## Session Continuity

Last session: 2026-07-27T19:05:49.299Z
Stopped at: Completed 40-03-PLAN.md
Resume file: None
