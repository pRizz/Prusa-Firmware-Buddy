---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 13-2026-06-16T14-21-01
generated_at: 2026-06-16T14:21:01.122Z
---

# Phase 13: CI Evidence Orchestration - Context

**Gathered:** 2026-06-16
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 13 makes aggregate cutover evidence runnable and reviewable from CI rather than from a local workspace. It covers PR-triggered execution for Rust, Bazel, verifier, manifest, planning, and release-evidence surfaces; machine-readable gate manifests; retained CI artifacts; and failure ownership back to v1.1 requirements and evidence gates.

This phase does not redefine v1.0 parity contracts, add simulator/hardware/live-service/release proof, demote the CMake/C++ reference path, or treat non-local evidence as passed. Later v1.1 phases attach the actual simulator, hardware, live network, release-candidate, retained-code, and maintainer-approval evidence.

</domain>

<decisions>
## Implementation Decisions

### CI Ownership and Triggering

- **D-01:** Add a new repo-owned CI evidence workflow instead of editing managed Bright Builds workflows. Existing `.github/workflows/bright-builds-auto-update.yml` remains upstream-managed and out of scope.
- **D-02:** The CI evidence workflow should run on pull requests that affect Rust, Bazel, verifier, manifest, planning, workflow, or release-evidence surfaces, and should also support manual `workflow_dispatch` runs.
- **D-03:** Main firmware Jenkins/Holly remains the existing firmware build/test pipeline. Phase 13 may cite it as current CI context, but the new cutover evidence gate should be self-contained and reviewable from repo-owned workflow files.
- **D-04:** CI commands must use repo-owned entrypoints such as Bazel labels, `just` recipes, or phase verifier scripts. Do not hide substantive logic in workflow YAML strings.

### Evidence Manifest Contract

- **D-05:** Add a Phase 13 CI evidence manifest contract that records each gate with requirement ID, owning phase, command, proof scope, expected artifact path, retained artifact kind, status vocabulary, and failure reason semantics.
- **D-06:** CI should generate a run-specific machine-readable evidence manifest under a deterministic ignored output directory, then upload it as an artifact. The checked-in manifest should define the schema and required gates; generated run outputs should stay out of source control.
- **D-07:** Gate rows must map directly to `CIEV-01`, `CIEV-02`, and `CIEV-03`, and should preserve links back to archived v1.0 evidence rows rather than creating roadmap-only claims.
- **D-08:** Failure rows must be actionable: each failed or skipped gate identifies the command, requirement or evidence row, owner phase, artifact path, and failure reason without requiring maintainers to rerun local commands.

### Artifact Retention and Redaction

- **D-09:** CI artifacts should include verifier logs, manifest snapshots, normalized comparison outputs where available, and redacted evidence summaries. The plan may use placeholder or dry-run outputs for non-local gates only when explicitly labeled as pending/non-local.
- **D-10:** Artifact names and paths may be committed as contracts, but generated logs, run manifests, firmware packages, raw crash dumps, private certificates, signing keys, Connect tokens, Wi-Fi credentials, and credential values must not be committed.
- **D-11:** Artifact retention should be visible in the CI workflow through the platform artifact-upload step and should avoid relying on local workspace state after the job exits.
- **D-12:** If a gate cannot run locally in CI yet, the manifest should record a pending or non-local status with the required later evidence, not a pass claim.

### Verification and Failure Ownership

- **D-13:** Add a Phase 13 verifier and regression tests following the Phase 11 standard-library Python pattern. It should validate the CI evidence manifest, workflow trigger/path coverage, artifact upload wiring, redaction/overclaim guards, Bazel/just exposure, and lifecycle metadata.
- **D-14:** Expose Phase 13 verification through Bazel and `just phase13-verify`, and keep the command narrow enough to run as the Phase 13 local verification gate.
- **D-15:** The workflow should run the aggregate cutover verifier or an explicit Phase 13 wrapper around it, but must keep non-local simulator, hardware, live-service, release-candidate, signing, storage-media, MMU, RS485, toolchanger, retained-code, and maintainer approval evidence classified as pending until later phases attach artifacts.
- **D-16:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 13-2026-06-16T14-21-01`.

### the agent's Discretion

- Exact workflow file name, checked-in manifest file name, output directory, artifact names, retention days, row IDs, helper function boundaries, and schema field order are flexible if the surface remains deterministic, source-backed, redacted, covered by tests, and easy for maintainers to inspect.
- The planner may choose whether Phase 13 has one integrated implementation plan or a small number of sub-tasks inside one plan, but the roadmap expects a single completed plan for the phase.
- Prefer small standard-library Python helpers, JSON manifests, Bazel/just wrappers, and concise workflow steps over broad CI rewrites or firmware build-system changes.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` - Phase 13 goal, dependency, success criteria, and v1.1 roadmap position.
- `.planning/REQUIREMENTS.md` - `CIEV-01`, `CIEV-02`, and `CIEV-03` acceptance requirements.
- `.planning/STATE.md` - current milestone state and Phase 13 starting point.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, safety, and Bright Builds constraints.

### Archived v1.0 cutover evidence

- `.planning/milestones/v1.0-REQUIREMENTS.md` - archived v1.0 requirement surface that v1.1 must not redefine.
- `.planning/milestones/v1.0-ROADMAP.md` - archived v1.0 phase history and evidence foundation.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` - v1.0 audit outcome and preserved non-local gates.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md` - parity pyramid, non-local proof, requirement traceability, reference comparison, retained-code, and overclaim decisions.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md` - passed Phase 11 local evidence boundary.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-CONTEXT.md` - metadata hygiene and no-overclaim constraints for archived evidence.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-VERIFICATION.md` - v1.0 archive-clean verification record.

### Existing verifier, manifest, and workflow patterns

- `tools/bazel/phase11_verify.py` - latest aggregate cutover verifier and overclaim/security scan pattern.
- `tools/bazel/phase11_verify_test.py` - latest verifier regression-test pattern.
- `tools/bazel/manifests/phase11_parity_pyramid.json` - proof-scope and evidence-class row pattern.
- `tools/bazel/manifests/phase11_requirement_evidence.json` - requirement-to-evidence manifest pattern.
- `tools/bazel/manifests/phase11_reference_comparisons.json` - normalized comparison evidence pattern.
- `tools/bazel/manifests/phase11_cutover_readiness.json` - final demotion gate and non-local blocker pattern.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` - retained-code acceptance evidence pattern.
- `tools/bazel/BUILD.bazel` - Bazel shell_binary wiring for phase verifiers.
- `tools/bazel/rust_workflow.sh` - Rust/phase verifier dispatch pattern.
- `justfile` - developer facade recipes and existing phase verification entrypoints.

### CI and artifact context

- `.github/workflows/bright-builds-auto-update.yml` - managed workflow that must not be edited for Phase 13.
- `.github/workflows/stale.yml` - existing GitHub Actions style in the repo.
- `utils/holly/build-pr.jenkins` - existing Jenkins/Holly firmware CI, build artifact archiving, and CTest log archiving pattern.
- `.planning/codebase/INTEGRATIONS.md` - CI/CD, Jenkins, GitHub Actions, artifact, credential, and service integration context.
- `.planning/codebase/TESTING.md` - repo-native test and simulator/integration verification surfaces.
- `.planning/codebase/CONCERNS.md` - known concerns that cutover evidence must keep visible.
- `standards/core/verification.md` - sync, hook, and pre-commit verification rules.
- `standards/core/testing.md` - focused unit test and Arrange/Act/Assert expectations.
- `standards/core/code-shape.md` - control-flow, `maybe_`, and code-size guidance.
- `standards/languages/rust.md` - Rust standards if Phase 13 adds or changes Rust domain types.
- `AGENTS.md` and `AGENTS.bright-builds.md` - repo-local GSD and Bright Builds workflow rules.
- `standards-overrides.md` - confirms no active local Bright Builds override.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase11_verify.py` and `tools/bazel/phase11_verify_test.py` provide the current standard-library Python verifier/test structure for manifest validation, security scans, source-path checks, and overclaim guards.
- `tools/bazel/manifests/phase11_*.json` already define cutover evidence rows, proof scopes, non-local evidence requirements, retained-code justifications, and reference-demotion blockers that Phase 13 can aggregate into CI evidence.
- `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` already expose phase verifiers through Bazel and stable developer recipes.
- `utils/holly/build-pr.jenkins` demonstrates existing artifact retention with `archiveArtifacts`, but GitHub Actions workflow files are the repo-owned surface available for a new PR evidence gate.

### Established Patterns

- Phase verifiers prefer explicit constants for required row IDs, required fields, forbidden markers, lifecycle IDs, allowed status values, and command-line modes.
- Planning and verifier artifacts separate local deterministic checks from CI, simulator, hardware, manual, release, and retained-code evidence.
- Checked-in manifests carry source-backed contracts; generated run outputs and large evidence artifacts stay in ignored build/output directories.
- Managed Bright Builds workflow blocks are not edited downstream.

### Integration Points

- Add Phase 13 CI evidence manifest(s) under `tools/bazel/manifests/`.
- Add Phase 13 verifier and tests under `tools/bazel/`.
- Add Bazel labels to `tools/bazel/BUILD.bazel` and a `just phase13-verify` recipe.
- Add a new repo-owned CI workflow file under `.github/workflows/` for cutover evidence orchestration.
- Use `.planning/phases/13-ci-evidence-orchestration/` for research, plan, summary, verification, and lifecycle artifacts.

</code_context>

<specifics>
## Specific Ideas

- The Phase 13 workflow should make missing or failed evidence easy to diagnose from downloaded artifacts: a maintainer should see the gate, requirement, command, owner phase, artifact path, and failure reason in one manifest.
- Do not modify `.github/workflows/bright-builds-auto-update.yml`; it is managed upstream.
- Keep all secret-bearing or signing-sensitive evidence name-only or redacted.
- Treat CI as an orchestration and retention layer for existing local verifiers and future non-local gates, not as proof that simulator, hardware, live-service, signing, or release evidence has already passed.
- Use Phase 13 to create the CI evidence contract that later phases can append to or satisfy.

</specifics>

<deferred>
## Deferred Ideas

- Actual simulator flow implementation belongs to Phase 14.
- Hardware, safety, media, UI input, MMU, RS485, and toolchanger evidence execution belongs to Phase 15.
- Live Connect, WUI, TLS, telemetry, proxy, and transfer evidence belongs to Phase 16.
- Release-candidate artifact, signing, provenance, resource, WUI, ESP, MMU, and auxiliary package proof belongs to Phase 17.
- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.

</deferred>

---

*Phase: 13-ci-evidence-orchestration*
*Context gathered: 2026-06-16*
