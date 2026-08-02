# Roadmap: Prusa Firmware Buddy Rust Port

## Overview

v1.0 established the source-backed Rust+Bazel parity evidence foundation. v1.1 hardened the remaining cutover blockers into durable CI, simulator, hardware, live-service, release, retained-code, upstream-result, and maintainer-review gate capabilities. v1.2 executed those external evidence and acceptance flows, closed upstream evidence flow into final readiness, and produced archival-ready milestone evidence. v1.3 consumes real sanitized maintainer/operator evidence packets, triages blockers, records explicit maintainer decisions, generates final readiness from real consumed rows, and produces a go/no-go cutover decision artifact.

The replacement firmware is not yet cut over. Final reference demotion remains blocked by default unless required evidence passes or receives explicit approved exceptions, and reference demotion remains a separate maintainer approval that cannot be inferred from green evidence alone.

## Milestones

- **v1.0 Rust Port Evidence Foundation** - Phases 1-12, 38 plans, shipped 2026-06-15. Archives: [roadmap](milestones/v1.0-ROADMAP.md), [requirements](milestones/v1.0-REQUIREMENTS.md), [audit](milestones/v1.0-MILESTONE-AUDIT.md), [phase history](milestones/v1.0-phases/).
- **v1.1 Cutover Evidence Hardening** - Phases 13-22, 13 plans, shipped 2026-06-22. Archives: [roadmap](milestones/v1.1-ROADMAP.md), [requirements](milestones/v1.1-REQUIREMENTS.md), [audit](milestones/v1.1-MILESTONE-AUDIT.md).
- **v1.2 Cutover Evidence Execution and Acceptance** - Phases 23-30, 9 plans, shipped 2026-07-02. Archives: [roadmap](milestones/v1.2-ROADMAP.md), [requirements](milestones/v1.2-REQUIREMENTS.md), [audit](milestones/v1.2-MILESTONE-AUDIT.md).
- **v1.3 Cutover Approval and Reference Demotion Trial** - Phases 31-41, 37 plans, shipped 2026-08-02. Archives: [roadmap](milestones/v1.3-ROADMAP.md), [requirements](milestones/v1.3-REQUIREMENTS.md), [audit](milestones/v1.3-MILESTONE-AUDIT.md), [phase history](milestones/v1.3-phases/).

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

<details>
<summary>v1.3 Cutover Approval and Reference Demotion Trial (Phases 31-41) - SHIPPED 2026-08-02</summary>

- [x] Phase 31: Final Evidence Intake - completed 2026-07-03
- [x] Phase 32: Blocker Register and Evidence Triage - completed 2026-07-03
- [x] Phase 33: Maintainer Decision Inputs - completed 2026-07-04
- [x] Phase 34: Final Readiness and Demotion Dry Run - completed 2026-07-25
- [x] Phase 35: Cutover Decision Artifact - completed 2026-07-26
- [x] Phase 36: Normalize Evidence and Blocker Rows - completed 2026-07-26
- [x] Phase 37: Reconcile Decisions Into Readiness - completed 2026-07-26
- [x] Phase 38: Fail-Closed Cutover Workflow - completed 2026-07-27
- [x] Phase 39: Milestone Metadata Reconciliation - completed 2026-07-29
- [x] Phase 40: File Length Refactoring - completed 2026-07-28
- [x] Phase 41: Terminal Milestone Metadata Coherence - completed 2026-08-01

Full phase details are archived in `.planning/milestones/v1.3-ROADMAP.md`; requirements, audit evidence, and execution history are archived beside it.

</details>

## Next Milestone

No active milestone is defined. Run `/gsd-new-milestone` to create fresh requirements and a roadmap from the v1.3 cutover decision route.
