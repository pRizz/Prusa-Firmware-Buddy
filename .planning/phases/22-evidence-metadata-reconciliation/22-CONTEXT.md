---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 22-2026-06-21T16-59-18
generated_at: 2026-06-21T16:59:18.640Z
---

# Phase 22: Evidence Metadata Reconciliation - Context

**Gathered:** 2026-06-21
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 22 reconciles the v1.1 milestone metadata after the functional gap-closure phases have landed. It updates requirement status, traceability, validation metadata, roadmap progress, phase directory consistency, state, and audit rerun readiness so maintainers can rerun the milestone audit against synchronized source-backed records.

This phase must not create new firmware behavior, new external evidence, new release outputs, or final reference-demotion approval. It records and verifies metadata truth. Missing hardware, live-service, release, maintainer-approval, or upstream result inputs stay explicit pending or blocked evidence, not local pass claims.

</domain>

<decisions>
## Implementation Decisions

### Requirements and Traceability Reconciliation

- **D-01:** Use evidence-qualified completion for requirement rows whose gate capability has been implemented and verified, while preserving result-level pending or blocked states for external evidence inputs.
- **D-02:** `SIM-03` should be reconciled as satisfied by Phase 14/19 traceability and no-overclaim boundaries only if the row text makes clear that hardware-only behavior is not simulator-proven.
- **D-03:** `REV-02` and `REV-03` should be reconciled as satisfied by Phase 21's upstream-result consumption gate only if the row text makes clear that `demotion_allowed` remains blocked without valid upstream results and maintainer decisions.
- **D-04:** Avoid unqualified "complete means all real-world evidence passed" wording. Requirement metadata should distinguish verified gate/capability from supplied external evidence outcome.

### Validation Metadata Reconciliation

- **D-05:** Reconcile Phase 14-18 validation files in place when local Wave 0 infrastructure now exists and passed verification.
- **D-06:** Set Wave 0 metadata and task-row file-existence/status fields from actual files and verification evidence, not from original planning placeholders.
- **D-07:** Preserve non-local evidence boundaries in each validation file. Physical simulator inputs, hardware/operator evidence, live-service credentials, release artifacts/signing evidence, retained-code maintainer decisions, and final demotion approval remain manual/external evidence paths unless validated inputs exist.
- **D-08:** If a validation file cannot honestly be marked complete, document a deliberate exception with owner, rationale, follow-up, and source refs instead of leaving stale placeholder metadata.

### Roadmap, Phase Directories, and State

- **D-09:** Use tool-anchored targeted reconciliation. Derive counts and statuses from phase directories, summaries, verification reports, and `gsd-tools` analysis before editing roadmap/state text.
- **D-10:** ROADMAP should reflect completed Phase 19, Phase 20, and Phase 21 work, including Phase 21's 1/1 plan and passed verification. Phase 22 should remain pending until its own plan and verification exist.
- **D-11:** STATE should be updated through GSD-owned workflow commands where available. If manual edits are unavoidable, keep them surgical and verify them with roadmap analysis and lifecycle checks.
- **D-12:** Do not add hot counters or broad generated summaries that require frequent hand maintenance when a derived tool check can validate the same fact.

### Milestone Audit Rerun Readiness

- **D-13:** Add a source-backed Phase 22 reconciliation contract or manifest plus verifier rather than relying on prose-only checkbox edits.
- **D-14:** The verifier should reject stale requirement statuses, validation frontmatter drift, mismatched roadmap/phase directory counts, missing source refs, unsafe generated artifact paths, secret-bearing refs, and overclaim wording.
- **D-15:** Generated audit rerun artifacts, logs, normalized reports, and snapshots should live under an ignored evidence root such as `build/ci-evidence/phase22/`.
- **D-16:** The source-backed reconciliation model may allow deliberate `non_blocking_debt` only with owner, rationale, follow-up or expiry trigger, and source refs. Broad or silent exceptions should fail verification.

### the agent's Discretion

- Exact manifest file names, schema field order, status wording, helper boundaries, and generated artifact names are flexible if the result is deterministic, source-backed, redacted, traceable, and hard to overclaim.
- Prefer standard-library Python, JSON manifests, focused tests, Bazel/just wiring, and localized planning metadata edits over broad audit framework rewrites.
- The planner may choose one integrated plan if it keeps the change cohesive. Split only if requirements/status edits and verifier implementation become too large for one safe execution pass.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Audit Debt

- `.planning/ROADMAP.md` - Phase 22 goal, dependencies, success criteria, and v1.1 progress table.
- `.planning/REQUIREMENTS.md` - v1.1 requirement checkboxes and traceability rows that Phase 22 reconciles.
- `.planning/STATE.md` - current milestone state, stale Phase 21 position, and accumulated evidence decisions.
- `.planning/v1.1-MILESTONE-AUDIT.md` - original audit findings, metadata debt, recommended gap closure, and rerun instruction.
- `.planning/RETROSPECTIVE.md` - prior lessons about requirement, roadmap, validation, and manifest metadata drift.

### Validation Metadata Inputs

- `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md` - stale Wave 0 metadata and simulator/no-overclaim validation contract.
- `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md` - stale Wave 0 metadata and hardware/manual evidence boundaries.
- `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md` - stale Wave 0 metadata and live-service/secret-safe evidence boundaries.
- `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md` - stale Wave 0 metadata and release/signing evidence boundaries.
- `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md` - stale Wave 0 metadata and maintainer/final-demotion boundaries.

### Gap-Closure Evidence

- `.planning/phases/19-aggregate-cutover-evidence-ci/19-CONTEXT.md` - aggregate evidence CI decisions that Phase 22 should preserve.
- `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md` - passed Phase 19 verification evidence.
- `.planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md` - release artifact identity and production proof boundary.
- `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md` - passed Phase 20 verification evidence.
- `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md` - upstream-result consumption decisions for final readiness.
- `.planning/phases/21-final-readiness-result-consumption/21-01-SUMMARY.md` - Phase 21 files modified, requirements completed, and verification commands.
- `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md` - passed Phase 21 verification evidence and remaining metadata reconciliation note.

### Source-Backed Evidence Tooling

- `tools/bazel/manifests/phase18_cutover_review_contract.json` - final review contract extended by Phase 21.
- `tools/bazel/phase18_cutover_review.py` - upstream result consumption, final demotion gate, generated artifacts, and security checks.
- `tools/bazel/phase18_cutover_review_test.py` - regression tests proving decision-only approval cannot demote the reference.
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - aggregate evidence contract pattern and Phase 14-18 result retention surface.
- `tools/bazel/phase19_aggregate_ci_evidence.py` - aggregate evidence verifier/runner pattern.
- `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` - release result manifest and release proof boundary.
- `tools/bazel/phase20_release_candidate_artifacts.py` - release result verifier/collector pattern.

### Standards

- `AGENTS.md` - local Bright Builds/GSD project guidance and generated-file ownership.
- `AGENTS.bright-builds.md` - Bright Builds default workflow and verification expectations.
- `standards-overrides.md` - no active local override for this phase.
- `standards/core/architecture.md` - source-backed domain contracts, parse at boundaries, illegal states unrepresentable.
- `standards/core/code-shape.md` - early returns, optional naming, function/file size triggers.
- `standards/core/testing.md` - focused unit tests and Arrange/Act/Assert.
- `standards/core/verification.md` - sync-first and repo-native verification before commit.
- `standards/languages/rust.md` - Rust guidance if Phase 22 touches Rust surfaces.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `gsd-tools.cjs` provides phase, roadmap, lifecycle, timestamp, state, and commit helpers. Use it for read/validation checks and state updates where supported.
- Phase 19 and Phase 20 Python verifiers provide the nearest source-backed manifest plus ignored generated-output pattern.
- Phase 18/21 verifier changes provide the nearest final-readiness no-overclaim and upstream-result validation pattern.
- Phase 14-18 validation files already contain the rows to reconcile; they should be edited in place instead of replaced wholesale.

### Established Patterns

- Checked-in JSON contracts and Python stdlib verifiers define policy; generated runtime evidence lives under ignored `build/ci-evidence/phaseXX`.
- Bazel labels, `tools/bazel/rust_workflow.sh`, and `just phaseXX-verify` expose phase verification.
- Missing external evidence is represented with explicit pending/blocked statuses. Local contract or quick checks do not become hardware, live-service, release, signing, or maintainer proof.
- Planning artifacts use lifecycle frontmatter. Phase 22 artifacts must carry `phase_lifecycle_id: 22-2026-06-21T16-59-18`.

### Integration Points

- `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` are the human-readable milestone state that the audit checks.
- `.planning/phases/14-.../14-VALIDATION.md` through `.planning/phases/18-.../18-VALIDATION.md` are the validation metadata records called out by the audit.
- `.planning/v1.1-MILESTONE-AUDIT.md` is the stale audit finding source; Phase 22 should either update or supersede its findings through a rerun artifact, not leave contradictions unexplained.
- Phase 22 verification should include direct metadata checks plus the relevant existing phase verifiers, especially Phase 18/19/20 surfaces that drive final readiness.

</code_context>

<specifics>
## Specific Ideas

- Maintainers should be able to answer "which requirement row changed, which phase evidence justifies it, and which result-level evidence is still pending" from source-backed metadata.
- Validation metadata should stop saying "Wave 0 creates file" when the file exists and the phase verifier passed.
- A Phase 22 reconciliation manifest should identify each metadata correction with old state, new state, source refs, no-overclaim rationale, and verification command.
- A milestone audit rerun should produce a concise passed report or a structured list of deliberate non-blocking debt, not a stale copy of the pre-gap-closure audit.

</specifics>

<deferred>
## Deferred Ideas

- Tamper-evident artifact attestations or digest indexes for generated release evidence may be useful later, but Phase 22 should not introduce a new attestation trust root unless the local source-backed verifier requires it.
- Derived dashboard or long-lived audit-preflight automation may be useful if metadata drift recurs across milestones. For this phase, keep the verifier focused on v1.1 reconciliation.

</deferred>

---

*Phase: 22-evidence-metadata-reconciliation*
*Context gathered: 2026-06-21*
