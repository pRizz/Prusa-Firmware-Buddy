---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 28-2026-06-25T03-31-49
generated_at: 2026-06-25T03:38:04.282Z
---

# Phase 28: Final Readiness Packet and Demotion Gate - Context

**Gathered:** 2026-06-25
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 28 produces the final cutover readiness packet from the v1.2 execution and acceptance artifacts. It consumes external evidence rows, retained-code decisions, exceptions, residual risks, blocker state, and the Phase 27 handoff, then gives maintainers a decision-ready view while keeping reference demotion blocked unless maintainers explicitly approve the separate demotion authorization.

</domain>

<decisions>
## Implementation Decisions

### Packet Composition and Traceability
- **D-01:** Build the final packet as a criteria-centric, link-first readiness record. Use one row per Phase 18 final criterion and link each row to READ-01, READ-02, READ-03, Phase 26 upstream rows, Phase 27 decision outputs, exception records, residual-risk entries, hard blockers, and retained artifact refs.
- **D-02:** Treat the machine-readable packet as the source of truth. A redacted human-readable readiness report may be generated as a derived view, but it must not become the only approval surface or drift from the machine rows.
- **D-03:** Keep raw evidence, signing material, credentials, production payloads, crash dumps, firmware binaries, and secret-bearing details out of the packet. Retain sanitized metadata and artifact references only.

### Readiness and Exception Semantics
- **D-04:** Use a two-verdict fail-closed model: final readiness status starts blocked and can resolve only when required gates pass or are covered by explicit approved exceptions; reference demotion remains a separate authorization verdict.
- **D-05:** Hard blockers outrank exceptions. Redaction failure, overclaim failure, lifecycle mismatch, source-ref failure, unsafe refs, or secret-tainted evidence must stay blocked and cannot be converted into normal accepted residual risk.
- **D-06:** Valid exceptions may cover only contract-allowed evidence statuses and must include scope, owner or approver, approver role, rationale, affected printer or release surface, evidence refs, residual risk, mitigation or follow-up, and expiry or review trigger.

### Reference Demotion Authorization
- **D-07:** Preserve reference demotion as a separate explicit maintainer decision. Green or exception-covered readiness evidence is a prerequisite, not automatic demotion approval.
- **D-08:** Default demotion authorization remains `blocked`. Phase 28 may expose an approval input or authorization record, but the verifier must reject any implied approval from evidence status alone.
- **D-09:** Keep the Phase 18 `final-reference-demotion-allowed` criterion and Phase 27 `phase28-handoff-manifest.json` aligned: the handoff supplies the blocked starting state, and Phase 28 owns the final explicit decision gate.

### Retained Outputs and Verification
- **D-10:** Implement Phase 28 as an aggregate final-readiness gate over retained Phase 26 and Phase 27 outputs, not as another producer that redefines simulator, hardware, live-service, release, upstream, retained-code, or residual-risk evidence.
- **D-11:** Retained Phase 28 outputs should live under `build/ci-evidence/phase28` and include a run manifest, final readiness packet, normalized criteria table, blocker summary, exception and residual-risk summary, demotion decision input or authorization record, redacted readiness report, artifact-reference summary, and contract/source snapshots.
- **D-12:** Add Bazel root aliases, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `just phase28-verify` wiring consistent with Phases 23-27. Verification should cover contract/schema drift, input presence and provenance, blocked-by-default behavior, exception precedence, hard-blocker rejection, no-implied-demotion behavior, secret/overclaim guards, retained output writing, and wiring.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 28 contract, readiness packet, decision input, normalized criteria table, summaries, and report, provided they are explicit, tested, stable, and do not fork Phase 18 or Phase 27 policy.
- Decide whether to implement Phase 28 as a thin wrapper around existing Phase 18/26/27 helper code or as a standalone verifier with shared constants. Prefer the smallest approach that avoids schema drift and makes readiness versus demotion status unambiguous.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless research finds a real dependency split.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 28 Scope
- `.planning/ROADMAP.md` - Phase 28 goal, dependency, success criteria, READ-01/02/03 mapping, and blocked-by-default demotion posture.
- `.planning/REQUIREMENTS.md` - READ-01, READ-02, READ-03 requirements and v1.2 traceability table.
- `.planning/PROJECT.md` - Current milestone posture, non-local evidence constraints, secret-safe evidence policy, and final demotion decisions.
- `.planning/STATE.md` - Current v1.2 progress and Phase 28 ready-to-plan state.

### Prior Phase Decisions
- `.planning/phases/23-simulator-evidence-execution/23-CONTEXT.md` - Simulator evidence execution boundaries, status normalization, retained outputs, and upstream row pattern.
- `.planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md` - Hardware/media/safety execution boundaries, residual-risk handling, and retained output pattern.
- `.planning/phases/25-live-service-evidence-execution/25-CONTEXT.md` - Live-service evidence execution boundaries, redaction policy, and retained output pattern.
- `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md` - Release/signing evidence and Phase 18 upstream row production policy.
- `.planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md` - Retained-code decision axes, exception policy, Phase 28 handoff, and no-demotion guarantee.

### Canonical Cutover and Acceptance Contracts
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - Canonical retained packet schema, final decision schema, exception fields, status vocabularies, upstream criteria, hard blockers, and demotion blocking rules.
- `tools/bazel/phase18_cutover_review.py` - Existing upstream-result consumption, final demotion blocking, exception coverage, redaction/overclaim policy, and readiness report behavior.
- `tools/bazel/phase18_cutover_review_test.py` - Regression patterns for upstream result manifests, exceptions, and demotion blocking.
- `tools/bazel/manifests/phase11_cutover_readiness.json` - Source cutover criteria, including reference-demotion-blocked policy.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` - Retained-code justification rows referenced by final packet decisions.
- `tools/bazel/manifests/foreign_code_inventory.json` - Foreign and retained source inventory refs.
- `tools/bazel/manifests/unsafe_boundary_audit.json` - Unsafe/runtime boundary refs for retained-code and hard-blocker decisions.

### Upstream and Decision Producers
- `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` - Phase 26 upstream policy, canonical Phase 18 criteria list, row required fields, and generated artifact list.
- `tools/bazel/phase26_release_signing_upstream_evidence.py` - Existing upstream row generation, placeholder statuses, hard-block normalization, and output conventions.
- `tools/bazel/phase26_release_signing_upstream_evidence_test.py` - Tests for Phase 18 criteria coverage, redaction/source lifecycle blockers, exception-coverable status behavior, and no-overclaim checks.
- `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json` - Phase 27 source contracts, decision axes, hard-blocker policy, exception policy, sensitive-role policy, generated artifacts, and Phase 28 handoff policy.
- `tools/bazel/phase27_retained_code_acceptance_decisions.py` - Existing retained-code decision normalization, final-readiness decision summary, residual-risk/exception outputs, and Phase 28 handoff manifest.
- `tools/bazel/phase27_retained_code_acceptance_decisions_test.py` - Tests for exact Phase 18 surface matching, no-demotion behavior, hard blockers, exception metadata, retained outputs, and wiring.

### v1.2 Evidence Execution Producers
- `tools/bazel/phase23_simulator_evidence_execution.py` - v1.2 simulator execution pattern for retained outputs and upstream rows.
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` - v1.2 hardware/media/safety execution pattern.
- `tools/bazel/phase25_live_service_evidence_execution.py` - v1.2 live-service execution pattern.
- `tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json` - Simulator execution contract and generated output convention.
- `tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json` - Hardware/media/safety execution contract and generated output convention.
- `tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json` - Live-service execution contract and generated output convention.

### Build and Workflow Wiring
- `BUILD.bazel` - Root filegroups and aliases for phase evidence docs and verification labels.
- `tools/bazel/BUILD.bazel` - Evidence verifier targets, source-ref filegroups, data dependencies, and shell binary wiring.
- `tools/bazel/rust_workflow.sh` - Dispatch cases for phase verification commands.
- `justfile` - Developer-facing phase verification recipes.

### Standards
- `AGENTS.md` - Local project guidance, GSD workflow requirement, and repo conventions.
- `AGENTS.bright-builds.md` - Bright Builds workflow, verification, code-shape, and Rust guidance summary.
- `standards/core/architecture.md` - Functional-core/imperative-shell and typed domain-boundary guidance.
- `standards/core/code-shape.md` - Control-flow, optional naming, and file/function size guidance.
- `standards/core/testing.md` - Unit-test expectations and Arrange/Act/Assert structure.
- `standards/core/verification.md` - Sync and repo-native verification requirements.
- `standards/languages/rust.md` - Rust-specific module, optional naming, invariant, and test guidance.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase18_cutover_review.py`: Existing final-review policy and demotion blocking logic that Phase 28 should preserve or wrap rather than redefine.
- `tools/bazel/phase26_release_signing_upstream_evidence.py`: Existing canonical upstream row table generation for Phase 18 criteria.
- `tools/bazel/phase27_retained_code_acceptance_decisions.py`: Existing retained-code decisions, residual-risk/exception registers, final-readiness decision summary, and Phase 28 handoff manifest.
- `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`: Existing Phase 28 handoff policy with demotion authorization blocked and explicit Phase 28 required decision.

### Established Patterns
- v1.2 evidence execution phases use Python verifiers, JSON contracts under `tools/bazel/manifests/`, retained generated outputs under ignored `build/ci-evidence/phaseXX`, focused Python tests, Bazel labels, root aliases, `rust_workflow.sh` dispatch, and `just phaseXX-verify` recipes.
- Prior phases keep source contracts in tracked files and generated evidence in ignored build directories. Phase 28 should follow that split.
- Tests use direct Python unit tests for verifier behavior and wiring, with explicit Arrange/Act/Assert comments in new tests.

### Integration Points
- Phase 28 should consume `build/ci-evidence/phase26/upstream-result-row-table.json` and `build/ci-evidence/phase27/phase28-handoff-manifest.json` when real or quick inputs are available.
- Phase 28 should link back to Phase 18 criteria and Phase 27 decisions rather than replaying raw external evidence.
- New workflow wiring belongs in root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile`.

</code_context>

<specifics>
## Specific Ideas

- The packet should make the distinction between `final_readiness_status` and `reference_demotion_authorization` impossible to miss.
- The redacted report should be generated from the same machine rows as the packet and should show requirement coverage, evidence family status, exception rationale, residual risk, hard blockers, and demotion decision state.
- Phase 28 should be able to run with safe fixtures or blocked placeholders for local verification while preserving clear language that real demotion approval is non-local maintainer evidence.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 28-final-readiness-packet-and-demotion-gate*
*Context gathered: 2026-06-25*
