---
gsd_state_version: "1.0"
milestone: v1.3
milestone_name: Cutover Approval and Reference Demotion Trial
status: complete
stopped_at: Phase 41 verified complete; pre-archive confirmation passed
last_updated: "2026-08-01T20:33:54.717Z"
last_activity: "2026-08-01"
progress:
  total_phases: 11
  completed_phases: 11
  total_plans: 37
  completed_plans: 37
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-27)

**Core value:** Deliver a Rust+Bazel firmware replacement that preserves existing printer behavior and release outputs while making the firmware safer to evolve, test, and verify.
**Current focus:** Phase 41 complete — terminal milestone metadata coherent

## Current Position

Milestone: v1.3 Cutover Approval and Reference Demotion Trial - complete
Phase: 41
Plan: 4 of 4
Status: Complete
Last activity: 2026-08-01

Progress: [##########] 100% (11/11 v1.3 phases complete)

## Performance Metrics

**Velocity:**

- v1.3 plans completed: 37/37
- v1.3 phases completed: 11/11
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
| 39 | 1 | - | - |
| 40. File Length Refactoring | 18/18 | - | - |
| 41 | 4 | - | - |

**Recent Trend:**

- Last 5 completed plans: Phase 39 P01, Phase 41 P01, Phase 41 P02, Phase 41 P03, Phase 41 P04
- Trend: Phase 41 passed 7/7 verification after closing terminal metadata, Nyquist, audit, and fail-closed projection gaps.

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
| Phase 40 P04 | 23m | 3 tasks | 27 files |
| Phase 40 P05 | 27m | 2 tasks | 22 files |
| Phase 40 P06 | 40m | 3 tasks | 60 files |
| Phase 40-file-length-refactoring P07 | 40m | 3 tasks | 64 files |
| Phase 40-file-length-refactoring P08 | 27m | 3 tasks | 22 files |
| Phase 40 P09 | 66m | 3 tasks | 36 files |
| Phase 40 P10 | 24m | 3 tasks | 18 files |
| Phase 40 P11 | 17m | 2 tasks | 8 files |
| Phase 40 P12 | 57min | 2 tasks | 26 files |
| Phase 40 P13 | 44min | 2 tasks | 19 files |
| Phase 40 P14 | 40min | 2 tasks | 11 files |
| Phase 40 P15 | 20min | 2 tasks | 3 files |
| Phase 41 P01 | 21min | 2 tasks | 7 files |
| Phase 41 P02 | 13min | 2 tasks | 6 files |
| Phase 41 P03 | 15min | 2 tasks | 8 files |
| Phase 41 P04 | 23min | 2 tasks | 9 files |

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
- [Phase 40]: Keep each Phase 5-11 verifier and Bazel label as the stable public facade over phase-local policy modules.
- [Phase 40]: Load phase-local failure suites through existing test entrypoints so public Bazel test labels remain unchanged.
- [Phase 40]: Copy extracted policy modules into isolated verifier test roots to preserve direct-script and runfiles behavior.
- [Phase 40]: Each Phase 13-17 evidence script keeps its original filename and Bazel label as the public CLI and artifact façade.
- [Phase 40]: Security, signing, provenance, and release-input rules remain phase-local; no shared cross-phase evidence framework was introduced.
- [Phase 40]: Phase 17 separates core contract policy, release-input policy, and artifact publication so each trust-boundary module stays below 629 lines.
- [Phase 40]: Each Phase 18-28 public script and Bazel label remains the stable CLI or test façade over phase-prefixed modules.
- [Phase 40]: Contract, policy, security, normalization, publication, and test-support seams stay phase-local; no cross-phase evidence framework was introduced.
- [Phase 40]: Final readiness and explicit reference-demotion authorization remain separate fail-closed predicates.
- [Phase 40-file-length-refactoring]: Phase 31-38 public scripts and Bazel labels remain stable facades over phase-local helpers.
- [Phase 40-file-length-refactoring]: Phase 34 readiness, Phase 35 cutover, and reference demotion remain independent fail-closed authorities.
- [Phase 40-file-length-refactoring]: Phase 38 extracts only pure final-status policy while marker, guard, and producer sequencing remain in the coordinator.
- [Phase 40-file-length-refactoring]: Each extracted firmware characterization source remains in its original Catch executable so target names and host-test routing stay stable.
- [Phase 40-file-length-refactoring]: Complete sorted Catch --list-tests output proves discovered case names, tags, and multiplicity remain exact across translation-unit splits.
- [Phase 40-file-length-refactoring]: HTTP digest error coverage explicitly resets its mocked clock to the asserted zero-time precondition, eliminating test-order leakage.
- [Phase 40]: Keep public firmware surfaces stable and place extracted behavior in named private implementation modules owned by existing targets.
- [Phase 40]: Retain MItem_tools.hpp as the complete tools-menu API while composing a cohesive information-declaration subheader.
- [Phase 40]: Convert only Rect16.h and screen_tools_mapping.cpp to approved owned deep modules with byte-identical source content.
- [Phase 40]: Keep filesystem, prefetch, Connect, Marlin, and transfer effects in stable adapters while extracting cohesive policy modules.
- [Phase 40]: Place transfer download-order decisions in the existing recovery translation unit and complete its focused PartialFile test interface.
- [Phase 40]: Retain planner.cpp byte-for-byte as the final authorized owned deep module and record its path-specific deletion test.
- [Phase 40]: Keep EEPROM access, recovery mutation, synchronization, initialization, and public journal lifetime behavior in backend.cpp while moving deterministic bank, CRC, and transaction policy.
- [Phase 40]: Treat ordered config migrations and legacy indexed persisted-field adapters as one compatibility seam while leaving the declarative registry and public header unchanged.
- [Phase 40]: Keep HAL, RCC, MMIO, wire I/O, exported callbacks, and fatal paths in original effect adapters.
- [Phase 40]: Use exact source-order comparisons and representative board links without claiming unavailable physical-hardware evidence.
- [Phase 40]: Keep lifecycle effects in existing public facades while private policy and transition modules own decisions.
- [Phase 40]: Split pause by load state, unload state, and motion because a single extraction cannot satisfy the 629-line limit.
- [Phase 40]: Keep marlin_server.cpp and public headers stable while private concept modules own lifecycle, request, event, media, print, and safety state knowledge.
- [Phase 40]: Use synthetic immutable-original temporary fixtures so shrink-only tests remain valid after the active ledger reaches zero temporary entries.
- [Phase 40]: Approved the structural campaign while retaining explicit simulator, physical-hardware, archived-artifact, and macOS-host limitations.
- [Phase 40]: Terminal authority is exactly the frozen 838 provenance/declarative paths plus the three locked owned deletion-test paths.
- [Phase 41]: Terminal consistency evaluation remains a pure immutable policy; filesystem and Markdown access stay in a thin read-only CLI.
- [Phase 41]: Exact plan and summary identities, not declared counts, are authoritative for terminal inventory coherence.
- [Phase 41]: The milestone audit is consumed only by pre-archive mode and never authorizes the facts it audits.
- [Phase 41]: Pre-audit accepts a truthful active Phase 41 projection, while pre-archive continues to require terminal completion and exact PLAN/SUMMARY pairing.
- [Phase 41]: Behavior-evidenced requirement completion is reported separately from the seven terminal-projection ownership rows assigned to active Phase 41.
- [Phase 41]: Exact phase-local PLAN and SUMMARY identities remain authoritative over declared counts.
- [Phase 41]: Pre-audit may contain exactly one in-flight Phase 41 validation task; all other pending validation states fail closed.
- [Phase 41]: The terminal audit remains a consumer-only candidate and grants no cutover, demotion, verification, or archival authority.
- [Phase 41]: Independent verification and a fresh successful pre-archive gate remain orchestrator-owned prerequisites.
- [Phase 41]: Derive active and terminal projection expectations from exact on-disk plan/summary inventory instead of stale declared totals.
- [Phase 41]: Keep filesystem and Markdown parsing in bounded adapters while immutable projection records feed the pure consistency policy.
- [Phase 41]: Parse only the YAML mapping, scalar, and inline-integer-list subset required by the audit projection and reject malformed nesting or case-normalized duplicates.

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

Last session: 2026-08-01T20:33:54.717Z
Stopped at: Phase 41 verified complete; pre-archive confirmation passed
Resume file: None
