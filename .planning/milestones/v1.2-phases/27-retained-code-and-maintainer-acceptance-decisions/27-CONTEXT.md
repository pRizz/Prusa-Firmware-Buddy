---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 27-2026-06-25T01-06-06
generated_at: 2026-06-25T01:06:35.730Z
---

# Phase 27: Retained-Code and Maintainer Acceptance Decisions - Context

**Gathered:** 2026-06-25
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 27 delivers machine-readable maintainer acceptance inputs for retained code, residual risk, exceptions, and final-readiness criteria. It consumes the Phase 18 retained-code/final-decision contract and Phase 26 upstream-result placeholders, records Phase 27-owned decisions, and prepares Phase 28 to generate the final readiness packet. It must not approve reference demotion; demotion remains a separate explicit Phase 28 decision.

</domain>

<decisions>
## Implementation Decisions

### Acceptance Source Coverage
- **D-01:** Build Phase 27 as a phase-owned wrapper around `tools/bazel/manifests/phase18_cutover_review_contract.json` and Phase 26 upstream-row outputs, not as a new standalone acceptance schema.
- **D-02:** Treat Phase 18 as canonical for retained packet schema, final decision schema, exception fields, status vocabularies, upstream criteria, and demotion blocking rules. Phase 27 may project those into v1.2 outputs but must not fork or silently redefine them.
- **D-03:** The Phase 27 verifier should assert exact coverage for the Phase 18 retained packet and upstream criterion surfaces, including retained-code acceptance, residual-risk review, maintainer-decision, and reference-demotion rows.

### Decision and Status Semantics
- **D-04:** Model evidence state, maintainer decision, exception state, residual-risk state, hard-failure state, and demotion authorization as separate axes, then derive Phase 18-compatible output status from those axes.
- **D-05:** Redaction failures, overclaim failures, unsafe refs, source-ref failures, and stale lifecycle evidence must hard-block acceptance. They must not be transformed into accepted retained-code risk by maintainer exception.
- **D-06:** Retained-code acceptance can become accepted, rejected, blocked, or deferred-approved-exception only from explicit maintainer decision input with rationale and evidence refs. Green evidence alone is not acceptance.
- **D-07:** Reference demotion authorization stays blocked or not approved in Phase 27. Phase 27 may emit a handoff row explaining what Phase 28 still needs, but it must not set demotion as allowed.

### Exception and Residual-Risk Policy
- **D-08:** Use a typed exception gate based on Phase 18's exception fields: scope, rationale, approver, approver_role, affected_printer_or_release_surface, mitigation_or_follow_up, expiry_or_review_trigger, and evidence_refs.
- **D-09:** Require every exception approval to name owner or approver, affected scope, rationale, evidence refs, residual risk, mitigation or follow-up, and an expiration or revisit trigger.
- **D-10:** Distinguish unresolved evidence blockers from accepted residual risks. A blocked evidence row remains a blocker unless the Phase 18 criterion explicitly allows an exception and the exception metadata is complete.
- **D-11:** For safety-, release-, signing-, TLS-, credential-, crash-dump-, and hardware-adjacent surfaces, planning should prefer stricter reviewer-role checks rather than broad "maintainer accepted" wording.

### Retained Outputs and Integration
- **D-12:** Write retained Phase 27 outputs under `build/ci-evidence/phase27`, following the Phase 23-26 execution-wrapper convention.
- **D-13:** Expected retained outputs should include an acceptance run manifest, normalized retained-code decisions, residual-risk register, exception decision register or summary, final-readiness decision summary, Phase 28 handoff manifest, decision row table, safe maintainer input template, artifact reference summary, and source contract snapshots.
- **D-14:** Phase 27 should consume Phase 26 upstream rows without replaying or copying unrelated evidence statuses. It should emit Phase 27-owned decision deltas and a clear precedence/handoff model for Phase 28.
- **D-15:** Add focused tests for Phase 18 schema/vocabulary exact-match checks, Phase 26 upstream-row consumption, retained packet coverage, exception metadata completeness, redaction/overclaim hard blockers, no-demotion guarantees, retained output writing, and Bazel/just wiring.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 27 contract, input template, decision manifests, summaries, and handoff manifest, provided they are explicit, tested, and stable for Phase 28.
- Decide whether to share helper functions with Phase 18/26 or keep a thin standalone Phase 27 verifier. Prefer the smallest approach that avoids schema drift and keeps the acceptance projection readable.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless research finds a real dependency split.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 27 Scope
- `.planning/ROADMAP.md` - Phase 27 goal, dependency, success criteria, and Phase 28 demotion boundary.
- `.planning/REQUIREMENTS.md` - ACPT-02 and ACPT-03 requirements and v1.2 traceability.
- `.planning/PROJECT.md` - v1.2 posture, explicit-demotion decision, secret-safe evidence constraints, and retained-code acceptance context.
- `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md` - Prior decision that Phase 26 emits upstream rows but does not approve retained-code, residual-risk, maintainer-decision, or demotion gates.

### Canonical Acceptance Contracts
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - Retained packet schema, final decision schema, exception fields, status vocabularies, upstream criteria, and demotion blocking rules.
- `tools/bazel/phase18_cutover_review.py` - Existing validation logic for retained packets, final criteria, upstream result requirements, redaction/overclaim hard blockers, generated artifacts, and demotion policy.
- `tools/bazel/phase18_cutover_review_test.py` - Regression patterns for retained-code acceptance, upstream result validation, exception coverage, and demotion blocking.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` - Retained-code justification rows that Phase 27 acceptance must cover.
- `tools/bazel/manifests/foreign_code_inventory.json` - Foreign-code inventory source refs for retained packet decisions.
- `tools/bazel/manifests/unsafe_boundary_audit.json` - Unsafe/runtime boundary source refs for retained packet decisions.
- `tools/bazel/manifests/phase11_cutover_readiness.json` - Final readiness and demotion-blocking source criteria.

### Upstream Result Producers
- `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` - Phase 26 upstream policy, canonical Phase 18 criteria list, row required fields, and generated artifact list.
- `tools/bazel/phase26_release_signing_upstream_evidence.py` - Existing upstream row generation, placeholder statuses for Phase 27-owned criteria, hard-block normalization, and output conventions.
- `tools/bazel/phase26_release_signing_upstream_evidence_test.py` - Tests for Phase 18 criteria coverage, redaction/source lifecycle blockers, exception-coverable status behavior, and no-overclaim output checks.
- `tools/bazel/phase23_simulator_evidence_execution.py` - v1.2 execution-wrapper pattern for retained outputs and upstream rows.
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` - v1.2 hardware/media/safety execution wrapper pattern.
- `tools/bazel/phase25_live_service_evidence_execution.py` - v1.2 live-service execution wrapper pattern.

### Build and Workflow Wiring
- `BUILD.bazel` - Root filegroups and aliases for phase evidence docs and verification labels.
- `tools/bazel/BUILD.bazel` - Evidence verifier targets, data dependencies, source-ref filegroups, and shell binary wiring.
- `tools/bazel/rust_workflow.sh` - Dispatch cases for phase verification commands.
- `justfile` - Developer-facing phase verification recipes.

### Standards
- `AGENTS.md` - Local project guidance and GSD workflow requirement.
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
- `tools/bazel/phase18_cutover_review.py`: reusable validation concepts for retained packet fields, final decision fields, upstream result requirements, hard blockers, generated artifact expectations, and demotion blocking.
- `tools/bazel/phase26_release_signing_upstream_evidence.py`: current Phase 18 upstream-row projection and placeholder behavior for Phase 27-owned criteria.
- `tools/bazel/manifests/phase11_retained_code_justifications.json`: eight retained-code justification rows that give Phase 27 concrete packet coverage.
- `tools/bazel/manifests/phase18_cutover_review_contract.json`: canonical schemas and vocabularies for Phase 27 to reference or exact-match.

### Established Patterns
- Phases 23-26 use Python verifier plus tests, a manifest under `tools/bazel/manifests`, retained outputs under `build/ci-evidence/phaseXX`, contract snapshots or refs, Bazel labels, root aliases, shell dispatch, and `just phaseXX-verify`.
- Quick verification passes from checked-in safe fixtures or placeholders while preserving blocked/pending status for real external evidence or maintainer approval.
- Redaction failures, source-ref failures, lifecycle mismatches, unsafe refs, and overclaim phrases are treated as blockers before maintainer acceptance is considered.

### Integration Points
- Phase 27 should add phase-specific source-ref filegroups and verifier targets in `tools/bazel/BUILD.bazel`, root doc/verify aliases in `BUILD.bazel`, `phase27_verify` and `phase27_verify_tests` cases in `tools/bazel/rust_workflow.sh`, and a `phase27-verify` recipe in `justfile`.
- Phase 27 generated outputs should be ignored build artifacts. Tracked files should be source contracts, input templates when safe, verifier code, tests, Bazel/just wiring, and planning artifacts.
- Phase 28 should consume Phase 27 handoff outputs rather than deriving retained-code acceptance from Phase 26 placeholders or raw prose.

</code_context>

<specifics>
## Specific Ideas

Advisor comparison favored: Phase 27-specific wrapper around Phase 18/26, orthogonal decision axes with a Phase 18-compatible projection, typed exception gate with hard evidence prechecks, and a Phase 28 handoff manifest.

</specifics>

<deferred>
## Deferred Ideas

- Signed attestation-style maintainer approvals may be useful later, but they are broader than Phase 27 unless a future phase explicitly adds signed cross-party approval infrastructure.
- External issue-tracker risk registers may be useful if exceptions become numerous or need lifecycle tracking beyond checked-in evidence artifacts.

</deferred>

---

*Phase: 27-retained-code-and-maintainer-acceptance-decisions*
*Context gathered: 2026-06-25*
