---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 33-2026-07-04T01-36-41
generated_at: 2026-07-04T01:38:20.362Z
---

# Phase 33: Maintainer Decision Inputs - Context

**Gathered:** 2026-07-04
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 33 delivers explicit machine-readable maintainer decision inputs for retained-code acceptance, residual-risk acceptance, exception decisions, final-readiness approval or block, and reference-demotion approval or rejection.

The phase consumes Phase 32 handoff artifacts, including blocker rows, decision-impact indexes, exception request registers, residual-risk request registers, and downstream handoff manifests. It may also reuse v1.2 Phase 27 and Phase 28 decision vocabulary where that prevents schema drift. It does not collect new evidence, reclassify evidence rows, generate final readiness, run the reference-demotion dry run, or publish the cutover verdict. Those remain Phase 31, Phase 32, Phase 34, and Phase 35 responsibilities.

</domain>

<decisions>
## Implementation Decisions

### Decision Input Model
- **D-01:** Build Phase 33 as an explicit decision-input layer over Phase 32 handoff artifacts. Phase 32 remains the authority for blocker classification, proof eligibility, row problem kinds, owners, severity, and required next actions.
- **D-02:** Decision inputs should be machine-readable JSON templates and normalized output records, not prose-only approvals. Every accepted or rejected decision must include a stable decision id, decision type, source row refs, decision value, maintainer identity reference, timestamp, rationale, and evidence or artifact refs.
- **D-03:** Model retained-code acceptance, residual-risk acceptance, exception approval, final-readiness approval/block, and reference-demotion approval/rejection as separate axes. Do not infer one axis from another, and do not let green evidence rows create approval by themselves.
- **D-04:** Prefer a Phase 33-specific wrapper and manifest that reuse Phase 27/28 vocabulary for retained-code, residual-risk, exception, readiness, and demotion concepts while binding decisions to Phase 32's v1.3 handoff rows.
- **D-05:** Unknown decision types, missing required fields, stale lifecycle refs, unresolved source row refs, and malformed source refs must fail closed as invalid decision inputs.

### Retained-Code and Residual-Risk Decisions
- **D-06:** Retained-code rows can be accepted, rejected, or exception-approved only from explicit maintainer input with rationale and owner signoff. Evidence status and prior source-backed justifications remain supporting context, not acceptance.
- **D-07:** Residual-risk rows require explicit acceptance or rejection with owner signoff, rationale, affected gates, and follow-up refs where applicable.
- **D-08:** Redaction failures, unsafe refs, secret-tainted rows, lifecycle mismatches, and source-ref failures must not become accepted retained-code or accepted residual-risk decisions through a normal approval path. They remain blockers unless a later phase defines a narrow exception path that is itself explicitly approved and auditable.

### Exception Decisions
- **D-09:** Exception decisions should consume Phase 32 `exception_request` rows and require explicit scope, expiration or review trigger, affected requirements, affected gates, rationale, owner signoff, and linked blocker refs.
- **D-10:** Approved exceptions may cover a blocker for readiness only when the exception source row refs exactly match the blocker rows and the exception scope covers the affected gate. Broad or unmatched exceptions should remain invalid.
- **D-11:** Rejected exceptions should remain visible in Phase 33 outputs so Phase 34 and Phase 35 can explain why readiness or cutover remains blocked.

### Final-Readiness Decision Input
- **D-12:** Final-readiness approval or block is a separate maintainer decision input that consumes Phase 32 blockers plus approved exception and residual-risk decisions. It should not generate the final readiness packet itself.
- **D-13:** Readiness approval must be invalid when unresolved critical blockers remain without approved exception coverage or explicit residual-risk acceptance. Readiness block decisions should still be valid and should preserve the blocker refs and rationale for Phase 34 and Phase 35.
- **D-14:** The Phase 33 readiness decision output should be a handoff record for Phase 34, not a final readiness verdict.

### Reference-Demotion Decision Input
- **D-15:** Reference demotion requires a separate explicit decision input with `approve` or `reject` semantics. It must not be inferred from retained-code decisions, readiness decisions, approved exceptions, or green evidence.
- **D-16:** A demotion approval input should be retained as authorization data only. Phase 34 still owns proving that demotion opens only when readiness is otherwise unblocked and the explicit approval input is valid.
- **D-17:** A missing, malformed, rejected, stale, or out-of-scope demotion input must preserve fail-closed behavior for Phase 34.

### Generated Artifacts and Handoff
- **D-18:** Expected Phase 33 outputs should include a decision input template, normalized decision records, retained-code decision register, residual-risk decision register, exception decision register, readiness decision handoff, demotion decision handoff, decision validation report, downstream handoff manifest, redacted maintainer decision report, and contract snapshot artifacts.
- **D-19:** The downstream handoff should let Phase 34 generate final readiness and demotion dry-run outputs without rereading raw evidence packets or secret-bearing artifacts.
- **D-20:** The handoff should let Phase 35 link every blocker, exception, residual risk, retained-code decision, readiness decision, and demotion decision needed for the go/no-go artifact.

### the agent's Discretion
- The agent may choose the concrete Python module split and exact JSON filenames, provided the generated files are stable, documented in a manifest, and covered by tests.
- The agent may choose exact enum spellings where not already locked by Phase 27, Phase 28, or Phase 32 contracts, but all enum values must be documented in the Phase 33 contract and tested.
- The agent may choose whether to implement one script with subcommands or a verifier script plus helper functions.
- The agent may choose exact Bazel labels and `just` target names, but they should follow existing phase patterns such as `phase31_verify`, `phase32_verify`, and `phase33-verify`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements
- `.planning/PROJECT.md` - v1.3 cutover approval trial scope, explicit-demotion boundary, and out-of-scope constraints.
- `.planning/REQUIREMENTS.md` - DECIDE-01 through DECIDE-03 plus downstream READY and CUTOVER requirements.
- `.planning/ROADMAP.md` - Phase 33 goal, success criteria, dependency on Phase 32, and Phase 34/35 downstream expectations.
- `.planning/STATE.md` - Current milestone state, active blockers, and Phase 33 readiness.

### Immediate Upstream Phase 32 Inputs
- `.planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md` - Phase 32 handoff decisions and boundaries.
- `.planning/phases/32-blocker-register-and-evidence-triage/32-01-SUMMARY.md` - Delivered Phase 32 artifacts and residual risks.
- `.planning/phases/32-blocker-register-and-evidence-triage/32-VERIFICATION.md` - Verified Phase 32 behavior and lifecycle status.
- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` - Authoritative Phase 32 blocker, exception request, residual-risk request, and handoff contract.
- `tools/bazel/phase32_blocker_register_triage.py` - Phase 32 classifier and handoff generator.
- `tools/bazel/phase32_blocker_register_triage_test.py` - Regression examples for blocker kinds, proof eligibility, derived registers, and handoff outputs.

### Decision and Readiness Precedents
- `.planning/milestones/v1.2-phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md` - v1.2 retained-code, residual-risk, exception, and readiness decision input boundaries.
- `.planning/milestones/v1.2-phases/27-retained-code-and-maintainer-acceptance-decisions/27-01-SUMMARY.md` - Phase 27 generated decision artifacts, tests, and handoff behavior.
- `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json` - Existing decision contract vocabulary and generated artifact expectations.
- `tools/bazel/phase27_retained_code_acceptance_decisions.py` - Existing decision input validation and retained output patterns.
- `tools/bazel/phase27_retained_code_acceptance_decisions_test.py` - Regression examples for decision axes and no-demotion guarantees.
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md` - Final readiness and reference-demotion fail-closed boundaries.
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-01-SUMMARY.md` - Phase 28 generated artifacts and blocker/readiness behavior.
- `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` - Existing readiness and demotion decision schema, generated artifacts, and authorization policy.
- `tools/bazel/phase28_final_readiness_packet.py` - Existing readiness and reference-demotion consumer behavior that Phase 33 should feed later.

### Build and Workflow Wiring
- `tools/bazel/BUILD.bazel` - Existing phase verifier/test target patterns.
- `BUILD.bazel` - Root aliases for phase verifier/test targets.
- `tools/bazel/rust_workflow.sh` - Existing shell facade case-arm patterns.
- `justfile` - Developer-facing phase verify command patterns.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase32_blocker_register_triage.py`: Reuse Phase 32's handoff bundle, blocker refs, exception request refs, residual-risk request refs, and proof eligibility fields as input surfaces.
- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json`: Treat as the authoritative source for Phase 33 input row shapes and source refs.
- `tools/bazel/phase27_retained_code_acceptance_decisions.py`: Reuse decision-axis concepts, retained-code acceptance patterns, residual-risk handling, exception handling, and generated artifact naming where compatible.
- `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`: Reuse vocabulary where it prevents drift from the existing decision-input machinery.
- `tools/bazel/phase28_final_readiness_packet.py`: Reuse fail-closed readiness and demotion vocabulary for Phase 34 handoff fields.
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile`: Reuse phase verifier and test target wiring patterns.

### Established Patterns
- Evidence and decision phases use Python standard-library verifier scripts, manifest JSON contracts, and script-local regression tests.
- Quick/default outputs may exist for smoke checks, but they must remain visibly blocked or template-only until explicit maintainer inputs are supplied.
- Secret and unsafe-ref protection must happen before retained outputs feed downstream artifacts.
- Machine-readable handoff artifacts are required for cutover gates; prose reports are secondary.
- Final readiness and reference demotion remain fail-closed unless explicit maintainer decisions unblock the relevant axis.

### Integration Points
- Phase 33 should default to reading Phase 32 outputs under `build/ci-evidence/phase32`.
- Phase 33 should generate outputs under `build/ci-evidence/phase33`.
- Phase 33 outputs should be consumable by Phase 34 final readiness/demotion dry run and Phase 35 cutover decision artifact generation.
- Tests should cover retained-code accept/reject/exception decisions, residual-risk accept/reject decisions, exception coverage matching, readiness approval/block handoff, demotion approval/rejection handoff, missing or stale decision input rejection, unresolved blocker fail-closed behavior, no approval from green evidence alone, generated artifact completeness, and no-secret propagation.

</code_context>

<specifics>
## Specific Ideas

- Treat Phase 33 as a v1.3 decision-input wrapper over Phase 32, not a broad rewrite of Phase 27.
- Keep the normal no-input or quick/default run blocked and template-oriented so local verification cannot pretend maintainer approval exists.
- Make source refs explicit enough that maintainers can audit why each decision was valid, rejected, or still blocked.
- Preserve rejected decisions as first-class rows because Phase 35 needs to explain blocked verdicts as clearly as approved verdicts.

</specifics>

<deferred>
## Deferred Ideas

- Final readiness packet generation and reference-demotion dry-run behavior belong to Phase 34.
- The go/no-go cutover decision artifact belongs to Phase 35.
- Broad retained vendor/HAL replacement, new printer behavior, long-run dashboards, and production reference demotion remain future milestone work unless Phase 33 exposes a narrow decision-blocking defect.

</deferred>

*Phase: 33-maintainer-decision-inputs*
*Context gathered: 2026-07-04*
