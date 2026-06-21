# Roadmap: Prusa Firmware Buddy Rust Port

## Overview

The v1.0 milestone established the Rust+Bazel rewrite evidence foundation: source-backed baseline, Bazel authority, typed Rust contracts, subsystem parity manifests, aggregate verification, and clean archival metadata. The v1.1 milestone turns the remaining non-local cutover blockers into durable CI, simulator, hardware, live-service, release-candidate, and maintainer-review gates.

## Milestones

- **v1.0 Rust Port Evidence Foundation** — Phases 1-12, 38 plans, shipped 2026-06-15. Archives: [roadmap](milestones/v1.0-ROADMAP.md), [requirements](milestones/v1.0-REQUIREMENTS.md), [audit](milestones/v1.0-MILESTONE-AUDIT.md), [phase history](milestones/v1.0-phases/).
- **v1.1 Cutover Evidence Hardening** — Phases 13-22, in gap closure. Goal: move from locally evidenced cutover readiness to release-governed and enforceable approval workflows.

## v1.1 Cutover Evidence Hardening

## Phases

<details>
<summary>v1.0 Rust Port Evidence Foundation (Phases 1-12) — SHIPPED 2026-06-15</summary>

- [x] Phase 1: Reference Baseline and Safety Envelope (1/1 plans) — completed 2026-06-02
- [x] Phase 2: Bazel Authority and Developer Facade (1/1 plans) — completed 2026-06-02
- [x] Phase 3: Artifact and Generator Parity (3/3 plans) — completed 2026-06-03
- [x] Phase 4: Rust Architecture and Invariant Model (1/1 plans) — completed 2026-06-03
- [x] Phase 5: Foreign Code, Unsafe, and Runtime Boundary (5/5 plans) — completed 2026-06-03
- [x] Phase 6: Printing Core, Safety, and Feature Gates (5/5 plans) — completed 2026-06-04
- [x] Phase 7: Persistence, Storage, and Resource Compatibility (5/5 plans) — completed 2026-06-06
- [x] Phase 8: Local Interface and Workflow Parity (3/3 plans) — completed 2026-06-13
- [x] Phase 9: Network, Web Services, and Transfers (4/4 plans) — completed 2026-06-14
- [x] Phase 10: Auxiliary Controllers and Expansion Ecosystem (4/4 plans) — completed 2026-06-14
- [x] Phase 11: Parity Pyramid and Cutover Evidence (5/5 plans) — completed 2026-06-14
- [x] Phase 12: Milestone Evidence Hygiene (1/1 plans) — completed 2026-06-15

Full phase details are archived in `.planning/milestones/v1.0-ROADMAP.md`.

</details>

- [x] **Phase 13: CI Evidence Orchestration** - Make aggregate cutover evidence run in CI with retained machine-readable artifacts and clear failure ownership. (completed 2026-06-16)
- [x] **Phase 14: Simulator Evidence Gates** - Convert simulator-only cutover blockers into runnable simulator evidence flows with requirement traceability. (completed 2026-06-17)
- [x] **Phase 15: Hardware Safety and Media Qualification** - Define and capture hardware, safety, storage-media, UI-input, MMU, RS485, and toolchanger cutover evidence. (completed 2026-06-18)
- [x] **Phase 16: Live Network and Transfer Qualification** - Capture live or controlled-service evidence for Connect, WUI, TLS, telemetry, proxy behavior, and transfers. (completed 2026-06-18)
- [x] **Phase 17: Release Candidate Artifact and Signing Gates** - Prove release-candidate artifacts, signing, provenance, resources, and auxiliary packages through Bazel-owned workflows. (completed 2026-06-19)
- [x] **Phase 18: Retained-Code Acceptance and Cutover Review** - Make retained-code acceptance, final reference-demotion criteria, and maintainer approval explicit and auditable. (completed 2026-06-20)
- [x] **Phase 19: Aggregate Cutover Evidence CI** - Run and retain Phase 14-18 cutover gate evidence through a single CI-owned manifest and artifact bundle. (completed 2026-06-21)
- [x] **Phase 20: Release Candidate Artifact Production** - Replace the empty release-candidate artifact identity target with real Bazel-owned release outputs and retained signing/provenance/comparison evidence. (completed 2026-06-21)
- [ ] **Phase 21: Final Readiness Result Consumption** - Require final cutover review to consume machine-readable upstream result manifests before any demotion decision can pass.
- [ ] **Phase 22: Evidence Metadata Reconciliation** - Reconcile requirement traceability, validation metadata, roadmap progress, and milestone audit state after functional gap closure.

## Phase Details

### Phase 13: CI Evidence Orchestration

**Goal**: Maintainers can rely on CI, not local workspaces, for aggregate cutover gate execution and evidence retention.
**Depends on**: v1.0 archive
**Requirements**: CIEV-01, CIEV-02, CIEV-03
**Success Criteria** (what must be TRUE):

1. CI runs the aggregate cutover verifier for pull requests that affect Rust, Bazel, verifier, manifest, or release-evidence surfaces.
1. CI writes a machine-readable evidence manifest with gate status, command, owner, artifact path, and failure reason for each cutover gate.
1. CI retains verifier logs, manifest snapshots, normalized comparison outputs, and redacted evidence summaries as downloadable artifacts.
1. Maintainers can identify which requirement or evidence gate failed without rerunning local commands.
   **Plans**: Not created yet.

### Phase 14: Simulator Evidence Gates

**Goal**: Maintainers can review simulator evidence for startup, G-code, GUI, storage, transfer, and selected failure flows without confusing simulator proof for hardware proof.
**Depends on**: Phase 13
**Requirements**: SIM-01, SIM-02, SIM-03
**Success Criteria** (what must be TRUE):

1. Simulator flows cover startup, task readiness, watchdog-visible startup behavior, and representative G-code execution.
1. Simulator flows cover GUI navigation, storage/resource access, transfers, and selected failure behavior with reference-compatible pass/fail semantics.
1. Simulator results map back to v1.0 requirement IDs and v1.1 cutover criteria.
1. Hardware-only behavior remains explicitly classified outside simulator proof.
   **Plans**: Not created yet.

### Phase 15: Hardware Safety and Media Qualification

**Goal**: Maintainers can evaluate hardware, safety, storage-media, UI-input, MMU, RS485, and toolchanger evidence required for cutover readiness.
**Depends on**: Phase 14
**Requirements**: HARD-01, HARD-02, HARD-03
**Success Criteria** (what must be TRUE):

1. Hardware smoke matrix identifies supported printer families, boards, storage media, and auxiliary-controller combinations required before cutover.
1. Safety evidence covers watchdog, thermal/motion safety, emergency stop, safe-output, crash recovery, UI input, MMU, RS485, and toolchanger scenarios.
1. Hardware evidence records device, firmware build, operator, timestamp, scenario, result, and residual risk.
1. Evidence artifacts avoid secrets, private service payloads, and unsafe operational data.
   **Plans**: 1 plan

Plans:
- [x] 15-01-PLAN.md - Hardware evidence contract, verifier/collector, operator evidence validation, and Bazel/just gate.

### Phase 16: Live Network and Transfer Qualification

**Goal**: Maintainers can review live or controlled-service evidence for Connect, PrusaLink/WUI, TLS, telemetry, proxy behavior, and transfers with secret-safe artifacts.
**Depends on**: Phase 13, Phase 14
**Requirements**: LIVE-01, LIVE-02, LIVE-03
**Success Criteria** (what must be TRUE):

1. Evidence covers Prusa Connect registration, telemetry, WebSocket commands, token/fingerprint behavior, and proxy limitations.
1. Evidence covers PrusaLink/WUI HTTP API, digest/API-key auth, SNTP, mDNS, syslog, metrics, and transfer behavior.
1. TLS, certificate, credential-redaction, negative protocol, long-transfer, and crash-dump upload evidence is captured.
1. No secrets, tokens, or private certificates are committed to the repository or planning artifacts.
   **Plans**: 1 plan

Plans:
- [x] 16-01-PLAN.md - Live network evidence contract, verifier/collector, operator evidence validation, and Bazel/just gate.

### Phase 17: Release Candidate Artifact and Signing Gates

**Goal**: Release managers can build and verify release-candidate firmware, resources, signing, provenance, and auxiliary packages through Bazel-owned workflows.
**Depends on**: Phase 13, Phase 15, Phase 16
**Requirements**: REL-01, REL-02, REL-03
**Success Criteria** (what must be TRUE):

1. Bazel-owned workflows produce release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, and auxiliary firmware artifacts.
1. Signing evidence verifies key identity, build input identity, artifact retention, and provenance while keeping private keys outside the repository.
1. Release-candidate artifact surfaces compare against archived v1.0 reference evidence.
1. Every artifact mismatch is classified as pass, intentional delta, blocker, or deferred retained-code issue.
   **Plans**: 1 plan

Plans:
- [x] 17-01-PLAN.md - Release candidate evidence contract, verifier, redaction/path guards, comparison classification, and Bazel/just gate.

### Phase 18: Retained-Code Acceptance and Cutover Review

**Goal**: Maintainers can approve or reject reference demotion through explicit retained-code acceptance packets, final gate evidence, and residual-risk review.
**Depends on**: Phase 13, Phase 14, Phase 15, Phase 16, Phase 17
**Requirements**: REV-01, REV-02, REV-03
**Success Criteria** (what must be TRUE):

1. Retained-code acceptance packets exist for every C, C++, ASM, generated, vendor, HAL, RTOS, network, filesystem, and signing surface that remains at cutover.
1. Final reference-demotion checklist links CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence.
1. Maintainers can approve, reject, or exception each final-demotion criterion with an auditable rationale.
1. Final cutover readiness allows reference demotion only when all required gates pass or have maintainer-approved exceptions.
   **Plans**: 1 plan

Plans:
- [x] 18-01-PLAN.md - Retained-code acceptance packets, final-demotion decision gate, verifier, Bazel labels, and just facade.

### Phase 19: Aggregate Cutover Evidence CI

**Goal**: Maintainers can review one CI-owned aggregate cutover evidence bundle that runs or ingests Phase 14-18 gate results, reports requirement-level status, and retains every required manifest without overclaiming external evidence.
**Depends on**: Phase 13, Phase 14, Phase 15, Phase 16, Phase 17, Phase 18
**Requirements**: CIEV-01, CIEV-02, CIEV-03, SIM-01, SIM-02, HARD-01, HARD-02, HARD-03, LIVE-01, LIVE-02, LIVE-03
**Gap Closure**: Closes v1.1 audit findings for aggregate CI stopping at Phase 13, missing Phase 14-18 retained artifacts, and incomplete milestone evidence download flow.
**Success Criteria** (what must be TRUE):

1. CI runs every locally runnable Phase 14-18 verifier mode needed for cutover evidence when relevant source, manifest, release, or planning surfaces change.
1. CI produces one machine-readable aggregate manifest with gate status, owning phase, command or evidence input, artifact path, requirement IDs, and failure reason for Phase 14-18 gates.
1. CI retains Phase 14-18 verifier logs, generated manifests, normalized result files, redacted summaries, and external-input placeholders as downloadable artifacts.
1. Simulator, hardware, live-service, signing, release, and maintainer-decision rows that still require external evidence remain pending or blocked, never locally passed by CI.
   **Plans**: Not created yet.

### Phase 20: Release Candidate Artifact Production

**Goal**: Release managers can produce release-candidate firmware, resource, signing, provenance, and comparison outputs through the Bazel-owned release artifact identity target instead of an empty placeholder.
**Depends on**: Phase 17, Phase 19
**Requirements**: REL-01, REL-02, REL-03
**Gap Closure**: Closes v1.1 audit findings for the empty `phase17_release_candidate_artifacts` target and missing real release output flow into final review.
**Success Criteria** (what must be TRUE):

1. `//tools/bazel:phase17_release_candidate_artifacts` resolves to real release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, and auxiliary package outputs or explicit release-environment inputs.
1. Representative smoke fixtures remain separate from release proof and cannot satisfy production release evidence rows.
1. Signing and provenance evidence records key identity, build input identity, artifact digests, retention refs, and verification outcomes without private keys or payload leakage.
1. Release-candidate comparison outputs classify every archived-reference mismatch as pass, intentional delta, blocker, or deferred retained-code issue.
   **Plans**: 2 plans

Plans:
- [x] 20-01-PLAN.md - Phase 20 contract, release input template, verifier, result manifest writer, and no-overclaim tests.
- [x] 20-02-PLAN.md - Bazel/root/just wiring, non-empty release identity target, and Phase 17 compatibility hardening.

### Phase 21: Final Readiness Result Consumption

**Goal**: Maintainers can approve final cutover only when Phase 18 consumes machine-readable upstream gate results for CI, simulator, hardware, live-service, release, retained-code, residual-risk, and maintainer-decision evidence.
**Depends on**: Phase 19, Phase 20
**Requirements**: REV-02, REV-03
**Gap Closure**: Closes v1.1 audit findings for Phase 18 linking contracts instead of generated gate result manifests and allowing decision refs without independently proving upstream results passed.
**Success Criteria** (what must be TRUE):

1. Phase 18 final criteria require machine-readable upstream result manifests for Phase 14-17 gates instead of only contract/source rows.
1. `demotion_allowed` remains false when required upstream manifests are missing, failed, stale, redaction-failed, or not covered by approved exceptions.
1. Maintainer decision input can approve, reject, or exception criteria only after upstream result status and evidence refs have passed schema, lifecycle, source-ref, and redaction checks.
1. Final readiness artifacts explain every blocked, pending, failed, exception-approved, and passed criterion with requirement IDs and retained evidence refs.
   **Plans**: Not created yet.

### Phase 22: Evidence Metadata Reconciliation

**Goal**: Maintainers can rerun the milestone audit against synchronized roadmap, requirement, validation, and audit metadata after gap closure work lands.
**Depends on**: Phase 19, Phase 20, Phase 21
**Requirements**: Metadata debt from v1.1 audit
**Gap Closure**: Closes v1.1 audit metadata debt for stale requirement statuses, incomplete Phase 14-18 Wave 0 validation metadata, roadmap progress, and audit rerun readiness.
**Success Criteria** (what must be TRUE):

1. `.planning/REQUIREMENTS.md` checkboxes and traceability rows match the actual gap-closure phase evidence.
1. Phase 14-18 validation files no longer show incomplete Wave 0 metadata after their verified work is complete, or they document a deliberate exception.
1. ROADMAP progress, phase details, and phase directories are internally consistent with Phases 19-22.
1. A rerun milestone audit reports `passed` or only deliberate, documented non-blocking debt.
   **Plans**: Not created yet.

## Progress

**Execution Order:**
Phases execute in numeric order: 13 -> 14 -> 15 -> 16 -> 17 -> 18 -> 19 -> 20 -> 21 -> 22

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 13. CI Evidence Orchestration | v1.1 | 1/1 | Complete    | 2026-06-16 |
| 14. Simulator Evidence Gates | v1.1 | 1/1 | Complete    | 2026-06-17 |
| 15. Hardware Safety and Media Qualification | v1.1 | 1/1 | Complete    | 2026-06-18 |
| 16. Live Network and Transfer Qualification | v1.1 | 1/1 | Complete    | 2026-06-18 |
| 17. Release Candidate Artifact and Signing Gates | v1.1 | 1/1 | Complete    | 2026-06-19 |
| 18. Retained-Code Acceptance and Cutover Review | v1.1 | 1/1 | Complete    | 2026-06-20 |
| 19. Aggregate Cutover Evidence CI | v1.1 | 1/1 | Complete    | 2026-06-21 |
| 20. Release Candidate Artifact Production | v1.1 | 2/2 | Complete    | 2026-06-21 |
| 21. Final Readiness Result Consumption | v1.1 | 0/0 | Planned    | - |
| 22. Evidence Metadata Reconciliation | v1.1 | 0/0 | Planned    | - |
