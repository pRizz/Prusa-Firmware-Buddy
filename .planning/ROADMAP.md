# Roadmap: Prusa Firmware Buddy Rust Port

## Overview

v1.0 established the source-backed Rust+Bazel parity evidence foundation. v1.1 hardened the remaining cutover blockers into durable CI, simulator, hardware, live-service, release, retained-code, upstream-result, and maintainer-review gate capabilities. v1.2 executes those real external evidence and acceptance flows and produces a maintainer-reviewable final readiness packet.

The replacement firmware is not yet cut over. Final reference demotion remains blocked by default unless required evidence passes or receives explicit approved exceptions, and reference demotion remains a separate maintainer approval.

## Milestones

- **v1.0 Rust Port Evidence Foundation** - Phases 1-12, 38 plans, shipped 2026-06-15. Archives: [roadmap](milestones/v1.0-ROADMAP.md), [requirements](milestones/v1.0-REQUIREMENTS.md), [audit](milestones/v1.0-MILESTONE-AUDIT.md), [phase history](milestones/v1.0-phases/).
- **v1.1 Cutover Evidence Hardening** - Phases 13-22, 13 plans, shipped 2026-06-22. Archives: [roadmap](milestones/v1.1-ROADMAP.md), [requirements](milestones/v1.1-REQUIREMENTS.md), [audit](milestones/v1.1-MILESTONE-AUDIT.md).
- **v1.2 Cutover Evidence Execution and Acceptance** - Phases 23-28, active. Goal: execute real external evidence gates, record maintainer acceptance decisions, and produce a final readiness packet without automatic reference demotion.

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
- [ ] **Phase 24: Hardware, Media, and Safety Evidence Execution** - Maintainers supply and retain real hardware, storage-media, UI-input, auxiliary, and safety evidence.
- [ ] **Phase 25: Live-Service Evidence Execution** - Maintainers supply and retain real Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, and crash-dump evidence.
- [ ] **Phase 26: Release, Signing, and Upstream Result Evidence** - Release managers supply secret-safe release outputs while maintainers receive upstream result rows for every cutover gate.
- [ ] **Phase 27: Retained-Code and Maintainer Acceptance Decisions** - Maintainers record retained-code, residual-risk, exception, and final-readiness decisions as machine-readable inputs.
- [ ] **Phase 28: Final Readiness Packet and Demotion Gate** - Maintainers generate the final readiness packet while reference demotion stays blocked unless explicitly approved.

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
**Plans**: TBD
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
**Plans**: TBD
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
**Plans**: TBD

### Phase 27: Retained-Code and Maintainer Acceptance Decisions
**Goal**: Maintainers can record retained-code, residual-risk, exception, and final-readiness acceptance decisions as machine-readable inputs.
**Depends on**: Phase 26
**Requirements**: ACPT-02, ACPT-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can accept, reject, or exception each retained-code packet with residual-risk rationale and evidence refs.
  2. Maintainer can approve or block final-readiness criteria through machine-readable decision inputs, not prose-only notes.
  3. Exception approvals identify scope, owner, expiration or revisit condition, and why replacement or demotion can proceed or must stay blocked.
  4. Decision outputs distinguish evidence failures, accepted retained-code risks, unresolved residual risks, and demotion approval state.
**Plans**: TBD

### Phase 28: Final Readiness Packet and Demotion Gate
**Goal**: Maintainers can generate the final cutover readiness packet and decide whether to keep reference demotion blocked or explicitly approve it.
**Depends on**: Phase 27
**Requirements**: READ-01, READ-02, READ-03
**Success Criteria** (what must be TRUE):
  1. Maintainer can generate a final readiness packet linking all external evidence, upstream rows, retained-code decisions, exceptions, residual risks, and blockers.
  2. Final readiness reports blocked by default unless every required gate is passed or covered by explicit approved exception.
  3. Reference demotion is shown as a separate explicit maintainer decision, and it never becomes allowed only because evidence is green.
  4. The final packet is decision-ready, with requirement coverage, evidence status, exception rationale, and remaining blocker summary visible to maintainers.
**Plans**: TBD

## Requirement Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| EVID-01 | Phase 23 | Complete |
| EVID-02 | Phase 24 | Pending |
| EVID-03 | Phase 25 | Pending |
| EVID-04 | Phase 26 | Pending |
| ACPT-01 | Phase 26 | Pending |
| ACPT-02 | Phase 27 | Pending |
| ACPT-03 | Phase 27 | Pending |
| READ-01 | Phase 28 | Pending |
| READ-02 | Phase 28 | Pending |
| READ-03 | Phase 28 | Pending |

**Coverage:** 10/10 v1.2 requirements mapped. No orphaned requirements. No duplicate requirement mappings.

## Progress

**Execution Order:**
Phases execute in numeric order: 23 -> 24 -> 25 -> 26 -> 27 -> 28

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 23. Simulator Evidence Execution | v1.2 | 1/1 | Complete    | 2026-06-23 |
| 24. Hardware, Media, and Safety Evidence Execution | v1.2 | 0/TBD | Not started | - |
| 25. Live-Service Evidence Execution | v1.2 | 0/TBD | Not started | - |
| 26. Release, Signing, and Upstream Result Evidence | v1.2 | 0/TBD | Not started | - |
| 27. Retained-Code and Maintainer Acceptance Decisions | v1.2 | 0/TBD | Not started | - |
| 28. Final Readiness Packet and Demotion Gate | v1.2 | 0/TBD | Not started | - |
