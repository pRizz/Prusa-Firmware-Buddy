# Roadmap: Prusa Firmware Buddy Rust Port

## Overview

v1.0 established the source-backed Rust+Bazel parity evidence foundation. v1.1 hardened the remaining cutover blockers into durable CI, simulator, hardware, live-service, release, retained-code, upstream-result, and maintainer-review gate capabilities. v1.2 executed those external evidence and acceptance flows, closed upstream evidence flow into final readiness, and produced archival-ready milestone evidence. v1.3 consumes real sanitized maintainer/operator evidence packets, triages blockers, records explicit maintainer decisions, generates final readiness from real consumed rows, and produces a go/no-go cutover decision artifact.

The replacement firmware is not yet cut over. Final reference demotion remains blocked by default unless required evidence passes or receives explicit approved exceptions, and reference demotion remains a separate maintainer approval that cannot be inferred from green evidence alone.

## Milestones

- **v1.0 Rust Port Evidence Foundation** - Phases 1-12, 38 plans, shipped 2026-06-15. Archives: [roadmap](milestones/v1.0-ROADMAP.md), [requirements](milestones/v1.0-REQUIREMENTS.md), [audit](milestones/v1.0-MILESTONE-AUDIT.md), [phase history](milestones/v1.0-phases/).
- **v1.1 Cutover Evidence Hardening** - Phases 13-22, 13 plans, shipped 2026-06-22. Archives: [roadmap](milestones/v1.1-ROADMAP.md), [requirements](milestones/v1.1-REQUIREMENTS.md), [audit](milestones/v1.1-MILESTONE-AUDIT.md).
- **v1.2 Cutover Evidence Execution and Acceptance** - Phases 23-30, 9 plans, shipped 2026-07-02. Archives: [roadmap](milestones/v1.2-ROADMAP.md), [requirements](milestones/v1.2-REQUIREMENTS.md), [audit](milestones/v1.2-MILESTONE-AUDIT.md).
- **v1.3 Cutover Approval and Reference Demotion Trial** - Phases 31-35, active. Goal: consume real evidence packets, triage blockers, record maintainer decisions, prove reference demotion remains explicitly guarded, and produce the cutover decision artifact.

## Phases

<details>
<summary>v1.0 Rust Port Evidence Foundation (Phases 1-12) - SHIPPED 2026-06-15</summary>

- [x] Phase 1: Reference Baseline and Safety Envelope - completed 2026-06-02
- [x] Phase 2: Bazel Authority and Developer Facade - completed 2026-06-02
- [x] Phase 3: Artifact and Generator Parity - completed 2026-06-03
- [x] Phase 4: Rust Architecture and Invariant Model - completed 2026-06-03
- [x] Phase 5: Foreign Code, Unsafe, and Runtime Boundary - completed 2026-06-03
- [x] Phase 6: Printing Core, Safety, and Feature Gates - completed 2026-06-04
- [x] Phase 7: Persistence, Storage, and Resource Compatibility - completed 2026-06-06
- [x] Phase 8: Local Interface and Workflow Parity - completed 2026-06-13
- [x] Phase 9: Network, Web Services, and Transfers - completed 2026-06-14
- [x] Phase 10: Auxiliary Controllers and Expansion Ecosystem - completed 2026-06-14
- [x] Phase 11: Parity Pyramid and Cutover Evidence - completed 2026-06-14
- [x] Phase 12: Milestone Evidence Hygiene - completed 2026-06-15

Full phase details are archived in `.planning/milestones/v1.0-ROADMAP.md`.

</details>

<details>
<summary>v1.1 Cutover Evidence Hardening (Phases 13-22) - SHIPPED 2026-06-22</summary>

- [x] Phase 13: CI Evidence Orchestration - completed 2026-06-16
- [x] Phase 14: Simulator Evidence Gates - completed 2026-06-17
- [x] Phase 15: Hardware Safety and Media Qualification - completed 2026-06-18
- [x] Phase 16: Live Network and Transfer Qualification - completed 2026-06-18
- [x] Phase 17: Release Candidate Artifact and Signing Gates - completed 2026-06-19
- [x] Phase 18: Retained-Code Acceptance and Cutover Review - completed 2026-06-20
- [x] Phase 19: Aggregate Cutover Evidence CI - completed 2026-06-21
- [x] Phase 20: Release Candidate Artifact Production - completed 2026-06-21
- [x] Phase 21: Final Readiness Result Consumption - completed 2026-06-21
- [x] Phase 22: Evidence Metadata Reconciliation - completed 2026-06-21

Full phase details are archived in `.planning/milestones/v1.1-ROADMAP.md`.

</details>

<details>
<summary>v1.2 Cutover Evidence Execution and Acceptance (Phases 23-30) - SHIPPED 2026-07-02</summary>

- [x] **Phase 23: Simulator Evidence Execution** - Maintainers supply and retain real simulator results for startup, G-code, GUI, storage, transfer, and selected failure flows. (completed 2026-06-23)
- [x] **Phase 24: Hardware, Media, and Safety Evidence Execution** - Maintainers supply and retain real hardware, storage-media, UI-input, auxiliary, and safety evidence. (completed 2026-06-23)
- [x] **Phase 25: Live-Service Evidence Execution** - Maintainers supply and retain real Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, and crash-dump evidence. (completed 2026-06-23)
- [x] **Phase 26: Release, Signing, and Upstream Result Evidence** - Release managers supply secret-safe release outputs while maintainers receive upstream result rows for every cutover gate. (completed 2026-06-24)
- [x] **Phase 27: Retained-Code and Maintainer Acceptance Decisions** - Maintainers record retained-code, residual-risk, exception, and final-readiness decisions as machine-readable inputs. (completed 2026-06-25)
- [x] **Phase 28: Final Readiness Packet and Demotion Gate** - Maintainers generate the final readiness packet while reference demotion stays blocked unless explicitly approved. (completed 2026-06-25)
- [x] **Phase 29: Upstream Evidence Flow Closure** - Phase 26 consumes Phase 23-25 upstream row artifacts, Phase 28 reflects real evidence flow, and audit metadata debt is reconciled. (completed 2026-06-25)
- [x] **Phase 30: Milestone Metadata Cleanup** - Refresh state, extraction, and verification-report metadata so v1.2 can be archived without contradictory planning artifacts. (completed 2026-06-27)

Full phase details are archived in `.planning/milestones/v1.2-ROADMAP.md`.

</details>

### v1.3 Cutover Approval and Reference Demotion Trial (Active)

**Milestone Goal:** Turn the v1.2 executable evidence and decision machinery into a real cutover approval trial, producing a go/no-go decision while keeping reference demotion explicitly guarded.

- [x] **Phase 31: Final Evidence Intake** - Maintainers and release managers can submit final sanitized evidence packets for all cutover gates. (completed 2026-07-03)
- [x] **Phase 32: Blocker Register and Evidence Triage** - Maintainers can classify every failed, missing, stale, malformed, redaction-failed, placeholder, or exceptioned row into one blocker register. (completed 2026-07-03)
- [x] **Phase 33: Maintainer Decision Inputs** - Maintainers can record retained-code, residual-risk, exception, final-readiness, and demotion decisions as explicit machine-readable inputs. (completed 2026-07-04)
- [x] **Phase 34: Final Readiness and Demotion Dry Run** - Maintainers can generate readiness from real consumed rows and prove demotion stays blocked without valid explicit approval. (completed 2026-07-25)
- [x] **Phase 35: Cutover Decision Artifact** - Maintainers can publish an auditable approved, blocked, or approved-with-exceptions verdict that routes the next milestone. (completed 2026-07-26)
- [x] **Phase 36: Normalize Evidence and Blocker Rows** - Normalize release row tables and decision-domain blocker identities so downstream readiness consumes the real producer shapes. (completed 2026-07-26)
- [x] **Phase 37: Reconcile Decisions Into Readiness** - Join retained-code, residual-risk, exception, and readiness decisions into resolvable Phase 34 ledger rows. (completed 2026-07-26)
- [x] **Phase 38: Fail-Closed Cutover Workflow** - Make upstream failures replace stale authority and prove blocked, approved, and targeted-repair paths end to end. (completed 2026-07-27)
- [ ] **Phase 39: Milestone Metadata Reconciliation** - Restore requirement-completion metadata and reconcile roadmap plan details before re-audit.
- [ ] **Phase 40: File Length Refactoring** - Eliminate all temporary repo-owned file-length exceptions through ordered, behavior-preserving refactors while retaining only the exact approved permanent set. Independent of pending Phase 39 metadata reconciliation.

## Phase Details

### Phase 31: Final Evidence Intake
**Goal**: Maintainers and release managers can submit final sanitized real-run evidence packets for simulator, hardware/media/safety, live-service, and release/signing cutover gates.
**Depends on**: Phase 30
**Requirements**: INTAKE-01, INTAKE-02, INTAKE-03, INTAKE-04
**Success Criteria** (what must be TRUE):
  1. Maintainer can submit a final simulator evidence packet for startup, G-code, GUI, storage, transfer, and selected failure flows with real-run metadata and sanitized artifact refs.
  2. Maintainer can submit a final hardware/media/safety evidence packet for supported printer families, storage media, UI input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output scenarios.
  3. Maintainer can submit a final live-service evidence packet for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows.
  4. Release manager can submit final release/signing/provenance evidence from real release-environment outputs with sanitized artifact, digest, signing, provenance, and comparison refs.
  5. Evidence intake accepts only sanitized artifacts or external refs for private keys, tokens, certificates, service payloads, raw crash dumps, and other secret-bearing data.
**Plans**: 2/2 plans complete
Plans:
- [x] 34-01-PLAN.md - Final readiness coverage ledger, demotion dry run, generated evidence bundle, and workflow wiring.
- [x] 34-02-PLAN.md - Required-stream completeness gap closure and exception-bypass regressions.

### Phase 32: Blocker Register and Evidence Triage
**Goal**: Maintainers can see every consumed row's cutover-blocking state in one register with owner, severity, affected gate, next action, and decision impact.
**Depends on**: Phase 31
**Requirements**: TRIAGE-01, TRIAGE-02, TRIAGE-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can aggregate consumed simulator, hardware/media/safety, live-service, release/signing, upstream-result, retained-code, and readiness rows into one blocker register.
  2. Every failed, missing, stale, malformed, redaction-failed, or exceptioned row is classified with owner, severity, affected gate, required next action, and decision impact.
  3. Quick/default placeholder outputs, smoke fixtures, and local-only dry-run rows are visibly rejected as final cutover proof.
  4. The blocker register distinguishes repair items, exception requests, and unresolved decision blockers.
**Plans**: 2 plans
Plans:
- [x] 36-01-PLAN.md - Normalize actual Phase 26 release tables and add stable exact identities for Phase 27/28 decision-domain rows.
- [x] 36-02-PLAN.md - Preserve malformed and unsupported Phase 27/28 producer containers as canonical fail-closed blockers while continuing to publish the complete Phase 32 bundle.

### Phase 33: Maintainer Decision Inputs
**Goal**: Maintainers can record explicit machine-readable retained-code, residual-risk, exception, final-readiness, and reference-demotion decisions without inferring authorization from evidence status.
**Depends on**: Phase 32
**Requirements**: DECIDE-01, DECIDE-02, DECIDE-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can accept, reject, or exception retained-code packets with residual-risk rationale and owner signoff.
  2. Maintainer can approve or block final readiness through machine-readable inputs that consume triaged evidence rows and approved exceptions.
  3. Maintainer can approve or reject reference demotion as a separate explicit decision input.
  4. Green evidence alone does not create retained-code, readiness, exception, residual-risk, or demotion approval.
**Plans**: 1 plan
Plans:
- [x] 33-01-PLAN.md - Phase 33 decision-input contract, verifier, generated handoff bundle, and workflow wiring.

### Phase 34: Final Readiness and Demotion Dry Run
**Goal**: Maintainers can generate a final readiness packet from real consumed evidence and decisions, then prove reference demotion remains blocked unless readiness is unblocked and explicit demotion approval is valid.
**Depends on**: Phase 33
**Requirements**: READY-01, READY-02, READY-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can generate a final readiness packet linking real consumed evidence rows, retained-code decisions, approved exceptions, residual risks, blockers, and artifact refs.
  2. Final readiness is blocked when required evidence is absent, failed, stale, malformed, redaction-failed, underclassified, or not covered by an explicit approved exception.
  3. Reference-demotion dry run reports blocked when explicit demotion approval is missing or invalid, even when evidence rows are green.
  4. Reference-demotion dry run opens only when readiness is otherwise unblocked and the explicit demotion approval input is valid.
**Plans**: TBD

### Phase 35: Cutover Decision Artifact
**Goal**: Maintainers can produce an auditable go/no-go cutover artifact that routes the project to production cutover or targeted blocker repair.
**Depends on**: Phase 34
**Requirements**: CUTOVER-01, CUTOVER-02, CUTOVER-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can produce one explicit cutover verdict: approved, blocked, or approved with explicit exceptions.
  2. The decision artifact links every blocker, exception, residual risk, evidence packet, retained-code decision, readiness result, and demotion decision needed to audit the verdict.
  3. An approved verdict routes the next milestone to production cutover planning, while blocked or exception-bearing verdicts route to targeted blocker repair with named follow-up scope.
  4. The artifact preserves reference-demotion authorization as an explicit decision state rather than deriving it from green evidence or cutover approval alone.
**Plans**: 2 plans
Plans:
- [x] 35-01-PLAN.md - Contract-first auditable cutover verdict, canonical audit-link index, next-milestone routing, demotion-state separation, and verification wiring.
- [x] 35-02-PLAN.md - Durable fail-closed replacement of stale cutover approvals when source validation fails.

### Phase 36: Normalize Evidence and Blocker Rows
**Goal**: Phase 32 consumes the actual Phase 26 release row-table shape and emits canonical resolvable identities for Phase 27/28 decision-domain rows.
**Depends on**: Phase 35
**Requirements**: INTAKE-04, TRIAGE-01, TRIAGE-02
**Gap Closure**: Closes audit gap B2 and provides the canonical row foundation required by B1.
**Success Criteria** (what must be TRUE):
  1. An accepted all-passed Phase 26 release row table remains eligible when it flows through Phase 31 into Phase 32.
  2. Phase 32 preserves stable source-domain and decision-resolution identities for retained-code, residual-risk, exception, readiness, and demotion rows.
  3. Unknown or malformed table and row shapes still fail closed without collapsing valid row tables into `unknown_unclassified`.
  4. Focused regressions exercise actual Phase 26, Phase 27, and Phase 28 producer output shapes.
**Plans**: TBD

### Phase 37: Reconcile Decisions Into Readiness
**Goal**: Phase 34 resolves the real Phase 27/28 blocker population with explicit Phase 33 decisions and can produce unblocked readiness from complete valid inputs.
**Depends on**: Phase 36
**Requirements**: DECIDE-01, DECIDE-02, READY-01
**Gap Closure**: Closes audit gap B1 and the readiness portion of the broken complete-approved flow.
**Success Criteria** (what must be TRUE):
  1. Phase 34 includes canonical evidence and decision-domain rows without treating valid Phase 27/28 rows as unconditional dangling blockers.
  2. Phase 33 retained-code, residual-risk, exception, and readiness decisions resolve only their exact matching rows.
  3. Uncovered, mismatched, stale, or invalid decisions remain blocking.
  4. A regression using actual Phase 31–33 producer outputs reaches unblocked readiness only when all evidence and decisions are valid.
**Plans**: TBD

### Phase 38: Fail-Closed Cutover Workflow
**Goal**: The full Phase 31–35 workflow replaces stale authority for every upstream failure and reaches the correct blocked, approved, or targeted-repair route.
**Depends on**: Phase 37
**Requirements**: READY-02, READY-03, CUTOVER-01, CUTOVER-03
**Gap Closure**: Closes audit gap B3, completes the approved flow, and closes the partial stale-approval replacement flow.
**Success Criteria** (what must be TRUE):
  1. Every invalid Phase 31/33 source causes Phase 34 to publish a durable blocked replacement before returning failure.
  2. Workflow orchestration cannot exit while leaving prior Phase 34 or Phase 35 approval authoritative.
  3. End-to-end regressions cover default blocked, complete approved, targeted-repair, and upstream-source failure paths using real producer output shapes.
  4. Production-cutover planning is reachable only from a valid approved verdict, while demotion authority remains a separate explicit predicate.
  5. Failed staged installation restores a safe prior bundle or a validated blocked replacement without weakening fail-closed authority.
**Plans**: 3 plans
Plans:
- [x] 38-01-PLAN.md - Complete fail-closed Phase 34 source-failure publication and guarded recoverable Phase 35 installation.
- [x] 38-02-PLAN.md - Add the status-preserving production coordinator, actual-producer route matrix, and authoritative Phase 38 gate.
- [x] 38-03-PLAN.md - Close stale-authority gaps with durable attempt-correlated workflow and publication markers.

### Phase 39: Milestone Metadata Reconciliation
**Goal**: Requirement completion and roadmap metadata agree with the executed and gap-closure evidence before the milestone is re-audited.
**Depends on**: Phase 38
**Requirements**: INTAKE-01, INTAKE-02, INTAKE-03
**Gap Closure**: Closes the Phase 31 summary completion gaps and stale roadmap plan metadata identified by the v1.3 audit.
**Success Criteria** (what must be TRUE):
  1. Phase 31 summary frontmatter exposes INTAKE-01 through INTAKE-04 through the supported `requirements-completed` extraction path.
  2. Phase 31, Phase 32, and Phase 34 roadmap plan counts and plan lists match their on-disk artifacts.
  3. Requirement traceability, roadmap phase status, summary extraction, and phase verification metadata contain no contradictions.
  4. A fresh milestone audit can evaluate all sixteen requirements from all three required sources.
**Plans**: TBD

### Phase 40: File Length Refactoring
**Goal**: The managed file-length checker reports zero findings with exactly 841 authorized permanent paths, while all 92 refactored repo-owned files and every new source/test file are below 629 physical lines and all external interfaces, firmware behavior, persistence, and release artifacts remain compatible.
**Depends on**: Phase 38. Phase 40 is explicitly independent of pending Phase 39 metadata reconciliation and may execute before Phase 39 completes.
**Requirements**: D-01 through D-15 from `40-CONTEXT.md` (decision-driven phase; no new v1.3 milestone requirement IDs)
**Success Criteria** (what must be TRUE):
  1. The initial ledger classifies all 933 findings as exactly 838 frozen provenance/declarative permanent paths plus 95 shrink-only temporary owned paths without modifying the managed checker or CI workflow.
  2. All 92 refactor-owned originals and all newly created source/test files have fewer than 629 physical lines behind stable, concept-oriented façades; Rust/Python/C++ APIs, Bazel/just labels, persistence, firmware behavior, and release artifacts remain compatible.
  3. Exactly `src/guiapi/include/Rect16.h`, `src/connect/planner.cpp`, and `src/gui/screen_tools_mapping.cpp` convert to permanent-owned deletion-test reasons; no other owned path is reclassified.
  4. Firmware characterization tests split before production firmware work, print/safety work runs last, and `src/common/marlin_server.cpp` is the final production file refactored.
  5. Terminal reconciliation from a clean checkout reports exactly 841 permanent exceptions, zero temporary reasons, and `SUMMARY file-lengths ... findings=0`, with risk-tiered automated evidence and hardware-aware review complete.
**Plans**: 15 plans

Plans:
- [x] 40-01-PLAN.md — Seed the exact 933-row ledger and Wave 0 policy/verification gate.
- [x] 40-02-PLAN.md — Refactor the four Rust domain modules behind stable façades.
- [x] 40-03-PLAN.md — Refactor build and phase-stepping developer utilities.
- [x] 40-04-PLAN.md — Refactor Phase 5-11 Python verifiers and tests.
- [x] 40-05-PLAN.md — Refactor Phase 13-17 evidence producers and tests.
- [x] 40-06-PLAN.md — Refactor Phase 18-28 cutover, release, decision, and readiness tools.
- [x] 40-07-PLAN.md — Refactor Phase 31-38 finality and cutover tooling.
- [x] 40-08-PLAN.md — Split seven firmware characterization test sources in existing Catch targets.
- [x] 40-09-PLAN.md — Refactor parser/UI/protocol/WUI sources and convert two locked exceptions.
- [x] 40-10-PLAN.md — Refactor network/media sources and convert the locked planner exception.
- [ ] 40-11-PLAN.md — Refactor journal and config-store persistence implementation.
- [ ] 40-12-PLAN.md — Refactor hardware, display, and auxiliary-controller adapters.
- [ ] 40-13-PLAN.md — Refactor non-server print and safety lifecycle sources.
- [ ] 40-14-PLAN.md — Refactor `marlin_server.cpp` last and remove the final temporary row.
- [ ] 40-15-PLAN.md — Perform exact terminal reconciliation and hardware-aware approval.

## Requirement Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| INTAKE-01 | Phase 39 | Pending |
| INTAKE-02 | Phase 39 | Pending |
| INTAKE-03 | Phase 39 | Pending |
| INTAKE-04 | Phase 36 | Complete |
| TRIAGE-01 | Phase 36 | Complete |
| TRIAGE-02 | Phase 36 | Complete |
| TRIAGE-03 | Phase 32 | Complete |
| DECIDE-01 | Phase 37 | Complete |
| DECIDE-02 | Phase 37 | Complete |
| DECIDE-03 | Phase 33 | Complete |
| READY-01 | Phase 37 | Complete |
| READY-02 | Phase 38 | Pending |
| READY-03 | Phase 38 | Pending |
| CUTOVER-01 | Phase 38 | Pending |
| CUTOVER-02 | Phase 35 | Complete |
| CUTOVER-03 | Phase 38 | Pending |

**Coverage:** 16/16 v1.3 requirements mapped; 9 complete and 7 pending gap closure. No orphaned requirements. No duplicate requirement mappings.

## Progress

**Execution Order:**
Phases 31 through 38 execute in numeric order after Phase 30. Phase 39 remains the pending metadata-reconciliation branch. Phase 40 is explicitly authorized to proceed from completed Phase 38 independently of Phase 39: `38 -> 39` and `38 -> 40`.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-12. Rust Port Evidence Foundation | v1.0 | 38/38 | Shipped | 2026-06-15 |
| 13-22. Cutover Evidence Hardening | v1.1 | 13/13 | Shipped | 2026-06-22 |
| 23. Simulator Evidence Execution | v1.2 | 1/1 | Complete    | 2026-06-23 |
| 24. Hardware, Media, and Safety Evidence Execution | v1.2 | 1/1 | Complete    | 2026-06-23 |
| 25. Live-Service Evidence Execution | v1.2 | 1/1 | Complete    | 2026-06-23 |
| 26. Release, Signing, and Upstream Result Evidence | v1.2 | 1/1 | Complete    | 2026-06-24 |
| 27. Retained-Code and Maintainer Acceptance Decisions | v1.2 | 1/1 | Complete    | 2026-06-25 |
| 28. Final Readiness Packet and Demotion Gate | v1.2 | 1/1 | Complete    | 2026-06-25 |
| 29. Upstream Evidence Flow Closure | v1.2 | 2/2 | Complete    | 2026-06-25 |
| 30. Milestone Metadata Cleanup | v1.2 | 1/1 | Complete    | 2026-06-27 |
| 31. Final Evidence Intake | v1.3 | 1/1 | Complete    | 2026-07-03 |
| 32. Blocker Register and Evidence Triage | v1.3 | 1/1 | Complete    | 2026-07-03 |
| 33. Maintainer Decision Inputs | v1.3 | 1/1 | Complete    | 2026-07-04 |
| 34. Final Readiness and Demotion Dry Run | v1.3 | 2/2 | Complete    | 2026-07-25 |
| 35. Cutover Decision Artifact | v1.3 | 2/2 | Complete    | 2026-07-26 |
| 36. Normalize Evidence and Blocker Rows | v1.3 | 2/2 | Complete    | 2026-07-26 |
| 37. Reconcile Decisions Into Readiness | v1.3 | 2/2 | Complete    | 2026-07-26 |
| 38. Fail-Closed Cutover Workflow | v1.3 | 3/3 | Complete    | 2026-07-27 |
| 39. Milestone Metadata Reconciliation | v1.3 | 0/TBD | Pending | — |
| 40. File Length Refactoring | v1.3 | 10/15 | In Progress|  |
