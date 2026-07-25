---
gsd_state_version: "1.0"
milestone: v1.3
milestone_name: Cutover Approval and Reference Demotion Trial
status: planning
stopped_at: Phase 34 context gathered
last_updated: "2026-07-25T18:24:08.607Z"
last_activity: 2026-07-04 -- Phase 33 complete
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 3
  completed_plans: 3
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-04)

**Core value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.
**Current focus:** Phase 34 - Final Readiness and Demotion Dry Run

## Current Position

Milestone: v1.3 Cutover Approval and Reference Demotion Trial - active
Phase: 34 of 35 (4 of 5 in current milestone) - Final Readiness and Demotion Dry Run
Plan: Not planned
Status: Ready to plan Phase 34
Last activity: 2026-07-04 -- Phase 33 complete

Progress: [######----] 60% (3/5 v1.3 phases complete)

## Performance Metrics

**Velocity:**

- v1.3 plans completed: 3/3
- v1.3 phases completed: 3/5
- Previous milestone baseline: v1.2 completed 9 plans across 8 phases
- Earlier milestone baseline: v1.1 completed 13 plans across 10 phases

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 31. Final Evidence Intake | 1/1 | - | - |
| 32. Blocker Register and Evidence Triage | 1/1 | 19min | 19min |
| 33. Maintainer Decision Inputs | 1/1 | 15min | 15min |
| 34. Final Readiness and Demotion Dry Run | 0/TBD | - | - |
| 35. Cutover Decision Artifact | 0/TBD | - | - |

**Recent Trend:**

- Last 5 completed plans: Phase 29 P02, Phase 30 P01, Phase 31 P01, Phase 32 P01, Phase 33 P01
- Trend: v1.2 evidence execution, acceptance, final-readiness, upstream evidence-flow closure, metadata cleanup, and milestone archival are complete; v1.3 Phases 31, 32, and 33 are complete and Phase 34 is ready to plan.

**Recent Completed Plan Detail:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 32 P01 | 19min | 3 tasks | 8 files |
| Phase 33 P01 | 15min | 3 tasks | 8 files |

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

### Pending Todos

- Plan Phase 34: Final Readiness and Demotion Dry Run.
- Keep real evidence artifacts sanitized; use external refs for private keys, tokens, certificates, service payloads, raw crash dumps, and other secret-bearing data.

### Blockers/Concerns

- Real simulator, hardware/media/safety, live-service, release/signing, upstream-result, retained-code, residual-risk, and maintainer-decision inputs must be supplied externally.
- Evidence artifacts must avoid private signing keys, tokens, certificates, service payloads, raw crash dumps, and other secret-bearing data.
- Hardware availability and failure-injection scope can block final readiness if required scenarios cannot be observed or explicitly exception-approved.
- Quick/default placeholder outputs, smoke fixtures, and local-only dry-run rows must not be accepted as final cutover proof.
- Reference demotion must remain blocked unless readiness is otherwise unblocked and a valid explicit maintainer demotion approval is supplied.
- Post-cutover retained vendor/HAL replacement and long-run dashboards are deferred unless v1.3 evidence reveals a narrow decision-blocking defect.

## Session Continuity

Last session: 2026-07-25T18:24:08.602Z
Stopped at: Phase 34 context gathered
Resume file: .planning/phases/34-final-readiness-and-demotion-dry-run/34-CONTEXT.md
