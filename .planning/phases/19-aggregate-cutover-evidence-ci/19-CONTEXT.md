---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 19-2026-06-21T01-07-45
generated_at: 2026-06-21T01:10:55.937Z
---

# Phase 19 Context: Aggregate Cutover Evidence CI

## Goal

Create one CI-owned aggregate cutover evidence bundle that runs or ingests Phase 14-18 gate results, reports requirement-level status, and retains every required manifest without claiming locally unavailable external evidence as passed.

## Source Inputs

- `.planning/ROADMAP.md` Phase 19: aggregate cutover evidence CI.
- `.planning/REQUIREMENTS.md`: CIEV-01, CIEV-02, CIEV-03, SIM-01, SIM-02, HARD-01, HARD-02, HARD-03, LIVE-01, LIVE-02, LIVE-03.
- `.planning/v1.1-MILESTONE-AUDIT.md`: gap findings for Phase 13-only CI, missing Phase 14-18 artifact retention, and incomplete milestone evidence download flow.
- `.planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md` and `13-VERIFICATION.md`: current CI evidence style and retention contract.
- `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md`: simulator evidence boundary and no-overclaim behavior.
- `.planning/phases/15-hardware-safety-and-media-qualification/15-VERIFICATION.md`: hardware/operator evidence contract and external-input boundary.
- `.planning/phases/16-live-network-and-transfer-qualification/16-VERIFICATION.md`: live-service evidence contract and secret-safety boundary.
- `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md`: release-candidate evidence contract and current placeholder limitation.
- `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VERIFICATION.md`: final review contract and upstream-result gap.

## Decisions

### Aggregate Gate Coverage

- Create a Phase 19 aggregate evidence contract/runner instead of expanding Phase 13 in place.
- Include Phase 14, 15, 16, 17, and 18 gate rows with requirement IDs, owning phase, command or evidence input, artifact path, status, and failure reason.
- Run locally deterministic verifier modes for those phases where available, and represent simulator, hardware, live-service, release, and maintainer-decision evidence inputs as explicit pending or blocked rows when CI cannot supply them.
- Treat Phase 19 as a milestone-integration gate, not as proof that external hardware, live-service, release, or maintainer approval evidence already exists.

### Evidence Retention

- Write aggregate evidence under `build/ci-evidence/phase19/`.
- Preserve per-phase subdirectories for captured manifests, logs, normalized results, redacted summaries, and external-input placeholders.
- Upload the entire Phase 19 evidence bundle from CI.
- Keep the Phase 13 pattern of machine-readable manifest first, logs before failing, and redaction/overclaim checks before artifact retention.

### No-Overclaim Semantics

- Missing external inputs must become `pending-*` or `blocked-*`, never `passed`.
- The aggregate source/contract readiness check may pass while final cutover remains blocked by external evidence.
- Generated artifacts must make the blocked rows obvious to maintainers without requiring local reruns.

### Workflow Wiring

- Expose the Phase 19 runner and tests through Bazel labels, the root Bazel facade, `tools/bazel/rust_workflow.sh`, and `just`.
- Keep GitHub Actions YAML thin; substantive behavior belongs in repo-owned Python.
- Update the CI evidence workflow from Phase 13-only artifact retention to Phase 19 aggregate retention.

## Agent Discretion

- Choose the exact JSON schema shape as long as it records requirement IDs, owning phase, command or evidence input, artifact path, status, and failure reason.
- Reuse existing helper patterns from Phase 13-18 where they reduce risk; avoid broad refactors outside the evidence pipeline.
- Add focused tests that prove the manifest contract, artifact layout, workflow wiring, and no-overclaim behavior.
- Keep generated runtime evidence ignored under `build/ci-evidence/`.

## Out of Scope

- Real release-candidate artifact production belongs to Phase 20.
- Final readiness consumption of upstream result manifests belongs to Phase 21.
- Requirement and validation metadata reconciliation belongs to Phase 22.
- This phase must not mark simulator, hardware, live-service, signing, release, or maintainer-decision rows as complete unless the required external artifacts are actually supplied and validated.
