---
gsd_state_version: 1.0
milestone: v1.3
milestone_name: Cutover Approval and Reference Demotion Trial
status: defining_requirements
stopped_at: Started v1.3 milestone planning
last_updated: "2026-07-02T20:13:46-05:00"
last_activity: 2026-07-02
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-02)

**Core value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.
**Current focus:** Defining v1.3 cutover approval and reference-demotion trial requirements

## Current Position

Milestone: v1.3 Cutover Approval and Reference Demotion Trial - active
Phase: Not started (defining requirements)
Plan: -
Status: Defining requirements
Last activity: 2026-07-02

Progress: [----------] 0% (roadmap not yet created)

## Performance Metrics

**Velocity:**

- v1.3 plans completed: 0/0
- v1.3 phases completed: 0/0
- Previous milestone baseline: v1.2 completed 9 plans across 8 phases
- Earlier milestone baseline: v1.1 completed 13 plans across 10 phases

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**

- Last 5 completed plans: Phase 27 P01, Phase 28 P01, Phase 29 P01, Phase 29 P02, Phase 30 P01
- Trend: v1.2 external-evidence execution, acceptance, final-readiness, upstream evidence-flow closure, Phase 30 metadata cleanup, and milestone archival are complete; v1.3 now defines the cutover approval and reference-demotion trial.

| Phase 30-milestone-metadata-cleanup P01 | 16m | 3 tasks | 12 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- v1.2 uses continuous phase numbering and starts at Phase 23 because v1.1 ended at Phase 22.
- v1.2 scope is execution and acceptance only; it does not redefine v1.0 parity contracts or v1.1 gate schemas unless a failed evidence row forces follow-up work.
- Final readiness stays blocked by default unless every required evidence gate passes or has an explicit approved exception.
- Reference demotion remains a separate explicit maintainer approval and is not automatic.
- Phase 30 is requirement-neutral metadata cleanup; it does not create new requirement IDs or reopen the completed v1.2 requirement coverage.
- [Phase 30-milestone-metadata-cleanup]: Phase 30 remained requirement-neutral: no new requirement IDs, no REQUIREMENTS.md updates, and archival deferred to the milestone completion workflow.
- [Phase 30-milestone-metadata-cleanup]: Used repo-local dual summary frontmatter keys instead of editing the global GSD helper.
- [Phase 30-milestone-metadata-cleanup]: Recorded the v1.2 audit as workflow-equivalent local GSD audit commands because this executor cannot dispatch slash commands.
- [v1.2-complete]: Archived v1.2 roadmap, requirements, and audit artifacts under `.planning/milestones/`; live requirements will be removed so `/gsd-new-milestone` starts from a fresh scope.
- [v1.3-start]: Scope v1.3 as cutover approval and reference-demotion trial work: real evidence intake, blocker triage, maintainer decisions, final readiness, demotion dry-run behavior, and a go/no-go artifact.

### Pending Todos

- Define v1.3 requirements.
- Create the v1.3 roadmap beginning after Phase 30.

### Blockers/Concerns

- Real simulator, hardware, live-service, release, signing, upstream-result, retained-code, residual-risk, and maintainer-decision inputs must be supplied externally.
- Evidence artifacts must avoid private signing keys, tokens, certificates, service payloads, raw crash dumps, and other secret-bearing data.
- Hardware availability and failure-injection scope can block final readiness if required scenarios cannot be observed or exception-approved.
- Reference demotion stays blocked unless a valid explicit maintainer decision supplies approval after readiness is otherwise unblocked.
- v1.3 must avoid turning quick/default placeholder outputs into real proof.
- Post-cutover retained vendor/HAL replacement and long-run dashboards are deferred unless v1.3 evidence reveals a narrow decision-blocking defect.

## Session Continuity

Last session: 2026-07-02
Stopped at: Started v1.3 milestone planning
Resume file: None
