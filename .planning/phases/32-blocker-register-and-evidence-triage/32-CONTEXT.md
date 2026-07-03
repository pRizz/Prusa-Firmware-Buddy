---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 32-2026-07-03T14-13-51
generated_at: 2026-07-03T14:13:51.406Z
---

# Phase 32: Blocker Register and Evidence Triage - Context

**Gathered:** 2026-07-03
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 32 delivers the blocker register and triage handoff over consumed final-intake evidence. Maintainers must be able to see every cutover-blocking row in one machine-readable register with owner, severity, affected gate, required next action, and decision impact.

The phase consumes Phase 31 final-intake manifests, accepted receipts, rejected submissions, quarantined non-final rows, and the Phase 23-26 upstream rows referenced by Phase 31. It does not collect new evidence, redefine source evidence schemas, approve exceptions, accept retained code, authorize reference demotion, generate final readiness, or publish the cutover verdict. Those remain Phase 31 and Phases 33-35 responsibilities.

</domain>

<decisions>
## Implementation Decisions

### Register Input Model
- **D-01:** Use a small Phase 32 adapter layer over Phase 31 outputs and referenced source rows. Phase 31 remains the authoritative finality and provenance boundary.
- **D-02:** The adapter should read Phase 31 `final-intake-manifest.json`, `rejected-submissions.json`, and accepted stream receipts first, then follow each accepted receipt's `consumed_upstream_row_refs` to gather row-level evidence detail from Phase 23-26 outputs.
- **D-03:** Do not normalize Phase 23-26 upstream rows independently from Phase 31. Bypassing Phase 31 would duplicate stale-lifecycle, placeholder, redaction, source-ref, and secret checks.
- **D-04:** Do not treat direct Phase 31 receipt consumption alone as sufficient if it loses row-level status, criterion, artifact, or failure detail needed for TRIAGE-01 and TRIAGE-02.
- **D-05:** Treat retained-code and readiness rows as register inputs only through existing v1.2 and v1.3 handoff artifacts; do not invent a new retained-code or readiness decision schema in Phase 32.

### Canonical Blocker Taxonomy
- **D-06:** Build one canonical blocker register with orthogonal fields instead of one overloaded status. Required row fields should include `row_id`, `source_stream`, `source_ref`, `requirement_ids`, `affected_gate`, `row_problem_kind`, `blocker_kind`, `severity`, `owner_ref`, `required_next_action`, `decision_impact`, `proof_eligibility`, and `evidence_refs`.
- **D-07:** `blocker_kind` must be exactly one of `repair_item`, `exception_request`, or `unresolved_decision_blocker`. Derived queue-style outputs may group by those kinds, but the canonical register is the source of truth.
- **D-08:** Keep specific causes in `row_problem_kind`, with explicit values for failed, missing, stale, malformed, redaction_failed, source_ref_failed, secret_tainted, lifecycle_mismatch, unsafe_ref, exception_requested, non_final_placeholder, smoke_fixture, local_dry_run, prose_attestation, row_only_submission, and unknown_unclassified.
- **D-09:** Unknown or unmapped problem kinds must fail closed as unresolved decision blockers with critical severity until the policy map is updated or an explicit exception path is created in a later phase.
- **D-10:** Severity and owner defaults may be policy-derived, but generated rows must keep `owner_ref` and `required_next_action` explicit so maintainers can assign and audit work without reading raw evidence.

### Placeholder and Non-Final Proof Rejection
- **D-11:** Phase 32 should make Phase 31 rejected and quarantined submissions visible in the blocker register, but they must never satisfy proof eligibility.
- **D-12:** Only `accepted-final` Phase 31 receipts may be proof-eligible, and only after the referenced upstream row detail is loaded and classified.
- **D-13:** Quick/default placeholders, smoke fixtures, local-only dry runs, prose-only attestations, upstream-row-only submissions, stale lifecycle rows, redaction/source-ref failures, unsafe refs, and secret-bearing submissions should map to blocker rows with `proof_eligibility: ineligible`.
- **D-14:** Preserve the distinction between "visible for triage" and "accepted as final proof" in generated artifacts and redacted reports. Non-final rows are audit evidence of blockers, not cutover evidence.
- **D-15:** Do not reopen Phase 31 solely to add rejection codes unless Phase 32 cannot classify an actual final-intake rejection from existing reason text and finality metadata.

### Downstream Handoff Bundle
- **D-16:** Emit a normalized Phase 32 handoff bundle rather than only a human-readable report. Expected artifacts are `blocker-register.json`, `decision-impact-index.json`, `exception-request-register.json`, `residual-risk-request-register.json`, `downstream-handoff-manifest.json`, `redacted-blocker-register-report.md`, and contract snapshots.
- **D-17:** The handoff bundle should let Phase 33 consume exception requests, retained-code follow-ups, residual-risk prompts, and unresolved decision blockers without rereading raw evidence or secret-bearing packets.
- **D-18:** The handoff bundle should let Phase 34 final readiness consume blocker state, approved exception references, residual-risk references, and proof eligibility while preserving fail-closed reference demotion.
- **D-19:** The handoff bundle should let Phase 35 link blockers, exceptions, residual risks, evidence packets, retained-code decisions, readiness results, and demotion decisions in the go/no-go artifact.
- **D-20:** Derived per-kind views are allowed for maintainer ergonomics only if they are generated from the canonical register and include stable row ids back to the canonical rows.

### the agent's Discretion
- The agent may choose the concrete Python module split, provided Phase 32 remains a thin adapter plus classifier over Phase 31 and existing v1.2/v1.3 artifacts.
- The agent may choose exact enum spellings where not specified above, but the spellings must be documented in the Phase 32 contract and covered by tests.
- The agent may choose whether to generate one script with subcommands or one verifier script plus helper functions.
- The agent may choose exact Bazel labels and `just` target names, but they should follow existing patterns such as `phase31_verify`, `phase31_verify_tests`, and `phase32-verify`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements
- `.planning/PROJECT.md` - v1.3 cutover approval trial scope, out-of-scope boundaries, and current project decisions.
- `.planning/REQUIREMENTS.md` - TRIAGE-01 through TRIAGE-03 and downstream DECIDE, READY, and CUTOVER requirements.
- `.planning/ROADMAP.md` - Phase 32 goal, success criteria, dependency on Phase 31, and Phase 33-35 downstream handoff expectations.
- `.planning/STATE.md` - Current milestone state, active blockers, and evidence-sanitization concerns.

### Immediate Upstream Phase 31 Inputs
- `.planning/phases/31-final-evidence-intake/31-CONTEXT.md` - Final-intake decisions, including the Phase 32 handoff boundary.
- `.planning/phases/31-final-evidence-intake/31-01-SUMMARY.md` - Phase 31 delivered files, accepted receipt behavior, rejected-submission behavior, and residual risks.
- `.planning/phases/31-final-evidence-intake/31-VERIFICATION.md` - Verified Phase 31 truths, receipt fields, finality statuses, and quick-output behavior.
- `tools/bazel/manifests/phase31_final_evidence_intake_contract.json` - Authoritative Phase 31 stream adapter, receipt, finality, and generated artifact contract.
- `tools/bazel/phase31_final_evidence_intake.py` - Phase 31 manifest, receipt, rejection, retained-output, lifecycle, redaction, and source-ref implementation.
- `tools/bazel/phase31_final_evidence_intake_test.py` - Regression examples for placeholder, prose, row-only, stale, unsafe-ref, and secret-bearing rejection.

### Source Evidence Machinery
- `.planning/milestones/v1.2-phases/23-simulator-evidence-execution/23-CONTEXT.md` - Simulator evidence execution scope and boundaries.
- `.planning/milestones/v1.2-phases/23-simulator-evidence-execution/23-01-SUMMARY.md` - Phase 23 retained outputs, upstream row, and verifier wiring.
- `.planning/milestones/v1.2-phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md` - Hardware/media/safety evidence boundaries.
- `.planning/milestones/v1.2-phases/24-hardware-media-and-safety-evidence-execution/24-01-SUMMARY.md` - Phase 24 retained outputs, upstream row, and verifier wiring.
- `.planning/milestones/v1.2-phases/25-live-service-evidence-execution/25-CONTEXT.md` - Live-service evidence and secret/overclaim boundaries.
- `.planning/milestones/v1.2-phases/25-live-service-evidence-execution/25-01-SUMMARY.md` - Phase 25 retained outputs, upstream row, and verifier wiring.
- `.planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md` - Release/signing/upstream row decisions.
- `.planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md` - Phase 26 row table, retained outputs, and verifier wiring.
- `tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json` - Simulator evidence execution contract.
- `tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json` - Hardware/media/safety evidence execution contract.
- `tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json` - Live-service evidence execution contract.
- `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` - Release/signing/upstream evidence contract.

### Downstream Consumers
- `.planning/milestones/v1.2-phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md` - Retained-code, residual-risk, and exception decision input boundaries.
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md` - Final readiness and reference-demotion fail-closed boundaries.
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-01-SUMMARY.md` - Phase 28 generated artifacts and blocker/readiness behavior.
- `.planning/milestones/v1.2-phases/29-upstream-evidence-flow-closure/29-01-SUMMARY.md` - Upstream row flow into final readiness.
- `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` - Downstream readiness and demotion gate contract.
- `tools/bazel/phase28_final_readiness_packet.py` - Existing blocker summary, exception/residual-risk, and demotion authorization behavior that Phase 32 should feed later.

### Build and Workflow Wiring
- `tools/bazel/BUILD.bazel` - Existing phase verifier/test target patterns.
- `BUILD.bazel` - Root aliases for phase verifier/test targets.
- `tools/bazel/rust_workflow.sh` - Existing shell facade case-arm patterns.
- `justfile` - Developer-facing phase verify command patterns.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase31_final_evidence_intake.py`: Reuse final-intake manifest, receipt, finality, rejection, retained-output, and security policy fields as input surfaces.
- `tools/bazel/manifests/phase31_final_evidence_intake_contract.json`: Use as the authoritative list of streams, receipt fields, generated artifacts, finality policy, and deferred responsibilities.
- `tools/bazel/phase28_final_readiness_packet.py`: Reuse vocabulary around hard blockers, exception-covered rows, residual-risk refs, and fail-closed demotion behavior when designing downstream handoff fields.
- Existing Phase 23-26 contracts and verifier scripts: Treat source evidence schemas as authoritative; Phase 32 adapts their rows, it does not replace them.
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile`: Reuse existing target and command wiring patterns.

### Established Patterns
- Evidence phases use Python standard-library verifier scripts, manifest JSON contracts, and script-local regression tests.
- Quick/default outputs are allowed for workflow smoke checks but must stay visibly blocked or non-final.
- Secret and unsafe-ref checks happen before retained outputs feed downstream artifacts.
- Machine-readable handoff artifacts are preferred over prose-only summaries for cutover gates.
- Final readiness and reference demotion remain fail-closed unless downstream maintainer decisions explicitly unblock them.

### Integration Points
- Phase 32 should default to reading `build/ci-evidence/phase31/final-intake-manifest.json` and related Phase 31 outputs.
- Phase 32 should generate outputs under `build/ci-evidence/phase32`.
- Phase 32 outputs should be consumable by future Phase 33 decision inputs, Phase 34 final readiness/demotion dry run, and Phase 35 go/no-go artifact generation.
- Tests should cover accepted-final rows, rejected-final rows, quarantined-non-final rows, unknown row/problem kinds, placeholder rejection, owner/action/severity requirements, derived queue consistency, and no-secret propagation.

</code_context>

<specifics>
## Specific Ideas

- Model the canonical register as one row per consumed blocking condition, not one row per source artifact.
- Include stable row ids that can be linked from derived queues, redacted reports, downstream handoff manifests, and future go/no-go artifacts.
- Make quick/default placeholder rows show up as blockers so maintainers can see why final proof is absent.
- Keep maintainer approval semantics out of Phase 32. Phase 32 says what blocks and what action is needed; Phase 33 and later record decisions.

</specifics>

<deferred>
## Deferred Ideas

- Actual exception approval, retained-code acceptance, residual-risk acceptance, final-readiness approval, and reference-demotion decisions belong to Phase 33 and Phase 34.
- Final readiness packet generation and demotion dry-run behavior belong to Phase 34.
- The go/no-go cutover decision artifact belongs to Phase 35.
- Broad retained vendor/HAL replacement, new printer behavior, and long-run dashboards remain future milestone work unless Phase 32 reveals a narrow decision-blocking defect.

</deferred>

*Phase: 32-blocker-register-and-evidence-triage*
*Context gathered: 2026-07-03*
