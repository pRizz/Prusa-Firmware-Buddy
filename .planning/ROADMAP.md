# Roadmap: Prusa Firmware Buddy Rust Port

## Overview

The Rust+Bazel rewrite planning is between milestones. v1.0 established the source-backed parity evidence foundation, and v1.1 hardened the remaining cutover approval blockers into CI, simulator, hardware, live-service, release-candidate, retained-code, and maintainer-review gate capabilities.

The replacement firmware is not yet cut over. Final reference demotion remains blocked until the validated external evidence inputs, upstream result packets, release artifacts, and maintainer decisions required by the v1.1 contracts are supplied and accepted.

## Milestones

- **v1.0 Rust Port Evidence Foundation** — Phases 1-12, 38 plans, shipped 2026-06-15. Archives: [roadmap](milestones/v1.0-ROADMAP.md), [requirements](milestones/v1.0-REQUIREMENTS.md), [audit](milestones/v1.0-MILESTONE-AUDIT.md), [phase history](milestones/v1.0-phases/).
- **v1.1 Cutover Evidence Hardening** — Phases 13-22, 13 plans, shipped 2026-06-22. Archives: [roadmap](milestones/v1.1-ROADMAP.md), [requirements](milestones/v1.1-REQUIREMENTS.md), [audit](milestones/v1.1-MILESTONE-AUDIT.md).

## Phases

<details>
<summary>v1.0 Rust Port Evidence Foundation (Phases 1-12) — SHIPPED 2026-06-15</summary>

- [x] Phase 1: Reference Baseline and Safety Envelope — completed 2026-06-02
- [x] Phase 2: Bazel Authority and Developer Facade — completed 2026-06-02
- [x] Phase 3: Artifact and Generator Parity — completed 2026-06-03
- [x] Phase 4: Rust Architecture and Invariant Model — completed 2026-06-03
- [x] Phase 5: Foreign Code, Unsafe, and Runtime Boundary — completed 2026-06-03
- [x] Phase 6: Printing Core, Safety, and Feature Gates — completed 2026-06-04
- [x] Phase 7: Persistence, Storage, and Resource Compatibility — completed 2026-06-06
- [x] Phase 8: Local Interface and Workflow Parity — completed 2026-06-13
- [x] Phase 9: Network, Web Services, and Transfers — completed 2026-06-14
- [x] Phase 10: Auxiliary Controllers and Expansion Ecosystem — completed 2026-06-14
- [x] Phase 11: Parity Pyramid and Cutover Evidence — completed 2026-06-14
- [x] Phase 12: Milestone Evidence Hygiene — completed 2026-06-15

Full phase details are archived in `.planning/milestones/v1.0-ROADMAP.md`.

</details>

<details>
<summary>v1.1 Cutover Evidence Hardening (Phases 13-22) — SHIPPED 2026-06-22</summary>

- [x] Phase 13: CI Evidence Orchestration — completed 2026-06-16
- [x] Phase 14: Simulator Evidence Gates — completed 2026-06-17
- [x] Phase 15: Hardware Safety and Media Qualification — completed 2026-06-18
- [x] Phase 16: Live Network and Transfer Qualification — completed 2026-06-18
- [x] Phase 17: Release Candidate Artifact and Signing Gates — completed 2026-06-19
- [x] Phase 18: Retained-Code Acceptance and Cutover Review — completed 2026-06-20
- [x] Phase 19: Aggregate Cutover Evidence CI — completed 2026-06-21
- [x] Phase 20: Release Candidate Artifact Production — completed 2026-06-21
- [x] Phase 21: Final Readiness Result Consumption — completed 2026-06-21
- [x] Phase 22: Evidence Metadata Reconciliation — completed 2026-06-21

Full phase details are archived in `.planning/milestones/v1.1-ROADMAP.md`.

</details>

## Progress

No active milestone is defined. Start the next milestone with `/gsd-new-milestone` so the next roadmap and requirements begin from a clean scope.
