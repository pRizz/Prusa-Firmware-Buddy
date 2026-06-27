# Roadmap: Prusa Firmware Buddy Rust Port

## Overview

v1.0 established the source-backed Rust+Bazel parity evidence foundation. v1.1 hardened the remaining cutover blockers into durable CI, simulator, hardware, live-service, release, retained-code, upstream-result, and maintainer-review gate capabilities. v1.2 executes those real external evidence and acceptance flows and produces a maintainer-reviewable final readiness packet.

The replacement firmware is not yet cut over. Final reference demotion remains blocked by default unless required evidence passes or receives explicit approved exceptions, and reference demotion remains a separate maintainer approval.

## Milestones

- **v1.0 Rust Port Evidence Foundation** - Phases 1-12, 38 plans, shipped 2026-06-15. Archives: [roadmap](milestones/v1.0-ROADMAP.md), [requirements](milestones/v1.0-REQUIREMENTS.md), [audit](milestones/v1.0-MILESTONE-AUDIT.md), [phase history](milestones/v1.0-phases/).
- **v1.1 Cutover Evidence Hardening** - Phases 13-22, 13 plans, shipped 2026-06-22. Archives: [roadmap](milestones/v1.1-ROADMAP.md), [requirements](milestones/v1.1-REQUIREMENTS.md), [audit](milestones/v1.1-MILESTONE-AUDIT.md).
- **v1.2 Cutover Evidence Execution and Acceptance** - Phases 23-30, active. Goal: execute real external evidence gates, record maintainer acceptance decisions, and produce a final readiness packet without automatic reference demotion.

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

### v1.2 Cutover Evidence Execution and Acceptance (Active)

**Milestone Goal:** Execute the real external evidence gates created in v1.1 and produce a maintainer-reviewable final readiness packet.

- [x] **Phase 23: Simulator Evidence Execution** - Maintainers supply and retain real simulator results for startup, G-code, GUI, storage, transfer, and selected failure flows. (completed 2026-06-23)
- [x] **Phase 24: Hardware, Media, and Safety Evidence Execution** - Maintainers supply and retain real hardware, storage-media, UI-input, auxiliary, and safety evidence. (completed 2026-06-23)
- [x] **Phase 25: Live-Service Evidence Execution** - Maintainers supply and retain real Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, and crash-dump evidence. (completed 2026-06-23)
- [x] **Phase 26: Release, Signing, and Upstream Result Evidence** - Release managers supply secret-safe release outputs while maintainers receive upstream result rows for every cutover gate. (completed 2026-06-24)
- [x] **Phase 27: Retained-Code and Maintainer Acceptance Decisions** - Maintainers record retained-code, residual-risk, exception, and final-readiness decisions as machine-readable inputs. (completed 2026-06-25)
- [x] **Phase 28: Final Readiness Packet and Demotion Gate** - Maintainers generate the final readiness packet while reference demotion stays blocked unless explicitly approved. (completed 2026-06-25)
- [x] **Phase 29: Upstream Evidence Flow Closure** - Phase 26 consumes Phase 23-25 upstream row artifacts, Phase 28 reflects real evidence flow, and audit metadata debt is reconciled. (completed 2026-06-25)
- [x] **Phase 30: Milestone Metadata Cleanup** - Refresh state, extraction, and verification-report metadata so v1.2 can be archived without contradictory planning artifacts. (completed 2026-06-27)

## Phase Details

### Phase 23: Simulator Evidence Execution
**Goal**: Maintainers can supply and retain real simulator results for startup, G-code, GUI, storage, transfer, and selected failure flows using the v1.1 simulator evidence contracts.
**Depends on**: Phase 22
**Requirements**: EVID-01
**Success Criteria** (what must be TRUE):
  1. Maintainer can submit a real simulator result packet with firmware identity, scenario outcomes, artifact refs, and operator/runtime metadata.
  2. Startup, G-code, GUI, storage, transfer, and selected failure-flow results each resolve to pass, fail, blocked, or exception-requested status.
  3. Simulator artifacts are retained with redacted logs and links back to the parity requirements they exercise.
  4. Hardware-only behaviors remain visibly outside simulator proof unless later hardware evidence covers them.
**Plans**: 1 (23-01 Phase 23 Simulator Evidence Execution)
**UI hint**: yes

### Phase 24: Hardware, Media, and Safety Evidence Execution
**Goal**: Maintainers can supply and retain real hardware, storage-media, UI-input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output evidence.
**Depends on**: Phase 23
**Requirements**: EVID-02
**Success Criteria** (what must be TRUE):
  1. Maintainer can submit hardware evidence packets covering supported printer families, storage media, devices, firmware builds, operators, and timestamps.
  2. Watchdog, thermal, motion, safe-output, UI-input, MMU, RS485, and toolchanger scenarios have explicit result status and artifact refs.
  3. Storage-media evidence identifies media type, filesystem/resource behavior, failure observations, and residual risk.
  4. Safety evidence cannot pass with missing scenario coverage, unredacted artifacts, or unresolved blocker rows.
**Plans**: 1 plan
Plans:
- [x] 24-01-PLAN.md - Phase 24 hardware/media/safety evidence execution wrapper
**UI hint**: yes

### Phase 25: Live-Service Evidence Execution
**Goal**: Maintainers can supply and retain real live-service evidence for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows.
**Depends on**: Phase 24
**Requirements**: EVID-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can submit live-service evidence packets for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows.
  2. Each service flow records service environment, firmware identity, sanitized result refs, and pass, fail, blocked, or exception-requested status.
  3. Secret-bearing inputs are redacted or externally referenced, and evidence validation rejects tokens, private certificates, credentials, and raw payloads.
  4. Live-service evidence links to acceptance rows consumed by final readiness.
Plans:
- [x] 25-01-PLAN.md - Phase 25 live-service evidence execution wrapper
**UI hint**: yes

### Phase 26: Release, Signing, and Upstream Result Evidence
**Goal**: Release managers and maintainers can supply secret-safe release/signing/provenance outputs and upstream result rows for every required cutover gate.
**Depends on**: Phase 25
**Requirements**: EVID-04, ACPT-01
**Success Criteria** (what must be TRUE):
  1. Release manager can provide release-environment outputs with artifact digests, signing identity, provenance, comparison refs, and no private keys or secrets.
  2. Maintainer can inspect upstream result rows for simulator, hardware/media/safety, live-service, release/signing, retained-code, and final-readiness gates.
  3. Every upstream row names requirement IDs, owning phase or gate, evidence ref, lifecycle status, exception status, and maintainer state.
  4. Missing, stale, failed, secret-tainted, or schema-invalid rows remain blocked until corrected or explicitly exception-approved.
Plans:
- [x] 26-01-PLAN.md - Phase 26 release/signing/upstream evidence wrapper

### Phase 27: Retained-Code and Maintainer Acceptance Decisions
**Goal**: Maintainers can record retained-code, residual-risk, exception, and final-readiness acceptance decisions as machine-readable inputs.
**Depends on**: Phase 26
**Requirements**: ACPT-02, ACPT-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can accept, reject, or exception each retained-code packet with residual-risk rationale and evidence refs.
  2. Maintainer can approve or block final-readiness criteria through machine-readable decision inputs, not prose-only notes.
  3. Exception approvals identify scope, owner, expiration or revisit condition, and why replacement or demotion can proceed or must stay blocked.
  4. Decision outputs distinguish evidence failures, accepted retained-code risks, unresolved residual risks, and demotion approval state.
**Plans**: 1 plan
Plans:
- [x] 27-01-PLAN.md - Phase 27 retained-code and maintainer acceptance decision wrapper

### Phase 28: Final Readiness Packet and Demotion Gate
**Goal**: Maintainers can generate the final cutover readiness packet and decide whether to keep reference demotion blocked or explicitly approve it.
**Depends on**: Phase 27
**Requirements**: READ-01, READ-02, READ-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can generate a final readiness packet linking all external evidence, upstream rows, retained-code decisions, exceptions, residual risks, and blockers.
  2. Final readiness reports blocked by default unless every required gate is passed or covered by explicit approved exception.
  3. Reference demotion is shown as a separate explicit maintainer decision, and it never becomes allowed only because evidence is green.
  4. The final packet is decision-ready, with requirement coverage, evidence status, exception rationale, and remaining blocker summary visible to maintainers.
**Plans**: 28-01

### Phase 29: Upstream Evidence Flow Closure
**Goal**: Real Phase 23, Phase 24, and Phase 25 upstream evidence rows can flow through Phase 26 into the Phase 28 final readiness packet while fail-closed quick behavior and reference-demotion separation remain intact.
**Depends on**: Phase 28
**Requirements**: ACPT-01, READ-01, READ-02
**Gap Closure**: Closes gaps from `.planning/v1.2-MILESTONE-AUDIT.md`: G1, F1, ACPT-01 partial, READ-01 partial, READ-02 partial, plus related traceability and validation metadata debt.
**Success Criteria** (what must be TRUE):
  1. Phase 26 accepts and validates Phase 23, Phase 24, and Phase 25 upstream row artifacts for criterion identity, requirement IDs, lifecycle/source refs, redaction status, source-ref status, artifact refs, and status vocabulary.
  2. Phase 26 uses consumed Phase 23-25 row status for simulator, hardware/media/safety, and live-service upstream rows instead of unconditional pending defaults, while absent real inputs still fail closed.
  3. Phase 28 final readiness packets reflect consumed Phase 26 evidence rows and preserve explicit blocked reference-demotion authorization unless a valid maintainer demotion decision is supplied.
  4. Machine-readable traceability carries EVID-01, EVID-02, and EVID-03 through Phase 26/28 rows, and summary plus Nyquist validation metadata is reconciled for phases 25-29.
**Plans**: 2 plans

### Phase 30: Milestone Metadata Cleanup
**Goal**: v1.2 planning metadata, helper extraction, and verification-report shapes are internally consistent so milestone archival does not preserve contradictory audit or state artifacts.
**Depends on**: Phase 29
**Requirements**: None - requirement coverage is already complete; this is audit metadata cleanup.
**Gap Closure**: Closes tech debt from `.planning/v1.2-MILESTONE-AUDIT.md`: TD-1 stale audit supersession, TD-2 stale `.planning/STATE.md` prose/metrics, TD-3 `summary-extract` requirements parsing drift, and TD-4 compact Phase 25 verification shape.
**Success Criteria** (what must be TRUE):
  1. `.planning/STATE.md` reports v1.2 progress, current position, and recent trend consistently with the roadmap and phase artifacts.
  2. The documented `summary-extract --fields requirements_completed` workflow returns the completed requirement IDs from current summary frontmatter or the milestone documents explicitly stop relying on that helper as the sole source.
  3. Phase 25 verification has requirement coverage evidence in the same audit-friendly shape as the other v1.2 phase verification reports, or the audit documents a durable local exception.
  4. A fresh milestone audit reports no critical gaps and no contradictory stale metadata before archival.
**Plans**: 1 plan
Plans:
- [x] 30-01-PLAN.md - Milestone metadata cleanup

## Requirement Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| EVID-01 | Phase 23 | Complete |
| EVID-02 | Phase 24 | Complete |
| EVID-03 | Phase 25 | Complete |
| EVID-04 | Phase 26 | Complete |
| ACPT-01 | Phase 29 | Complete |
| ACPT-02 | Phase 27 | Complete |
| ACPT-03 | Phase 27 | Complete |
| READ-01 | Phase 29 | Complete |
| READ-02 | Phase 29 | Complete |
| READ-03 | Phase 28 | Complete |

**Coverage:** 10/10 v1.2 requirements mapped. 10 complete, 0 pending gap closure. No orphaned requirements. No duplicate requirement mappings.

**Metadata gap closure:** Phase 30 is requirement-neutral and closes audit tech debt only; v1.2 requirement coverage remains 10/10 complete.

## Progress

**Execution Order:**
Phases execute in numeric order: 23 -> 24 -> 25 -> 26 -> 27 -> 28 -> 29 -> 30

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 23. Simulator Evidence Execution | v1.2 | 1/1 | Complete    | 2026-06-23 |
| 24. Hardware, Media, and Safety Evidence Execution | v1.2 | 1/1 | Complete    | 2026-06-23 |
| 25. Live-Service Evidence Execution | v1.2 | 1/1 | Complete    | 2026-06-23 |
| 26. Release, Signing, and Upstream Result Evidence | v1.2 | 1/1 | Complete    | 2026-06-24 |
| 27. Retained-Code and Maintainer Acceptance Decisions | v1.2 | 1/1 | Complete    | 2026-06-25 |
| 28. Final Readiness Packet and Demotion Gate | v1.2 | 1/1 | Complete    | 2026-06-25 |
| 29. Upstream Evidence Flow Closure | v1.2 | 2/2 | Complete    | 2026-06-25 |
| 30. Milestone Metadata Cleanup | v1.2 | 1/1 | Complete   | 2026-06-27 |
