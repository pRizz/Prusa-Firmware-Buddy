---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 36-2026-07-26T00-27-52
generated_at: 2026-07-26T00:33:39.346Z
---

# Phase 36: Normalize Evidence and Blocker Rows - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 36 repairs the producer-to-consumer boundary at Phase 32. It makes Phase 32 consume the actual Phase 26 release row-table shape referenced by Phase 31 and emit stable, resolvable identities for the retained-code, residual-risk, exception, readiness, and demotion rows produced by Phases 27 and 28.

This phase closes milestone-audit gap B2 and provides the canonical row foundation needed to close B1. It does not make Phase 34 resolve decisions into readiness, prove the approved cutover path, or repair stale-authority replacement across the full workflow; those remain Phase 37 and Phase 38 responsibilities.

</domain>

<decisions>
## Implementation Decisions

### Release Row-Table Normalization

- **D-01:** Add an explicit Phase 32 adapter for the canonical Phase 26 `{"rows": [...]}` release/signing table. Invoke it only for the release/signing table referenced by an `accepted-final` Phase 31 receipt; Phase 31 remains the finality and provenance authority.
- **D-02:** Validate the Phase 26 table atomically before classifying any contained row. A missing, non-list, or empty `rows` value, a non-object entry, a duplicate or unknown criterion, or a missing required decision-bearing field makes the table ineligible and produces a critical malformed-table blocker rather than partially accepting valid-looking entries.
- **D-03:** A valid all-passed Phase 26 table emits no release blocker and remains proof-eligible. A valid non-passed row emits a criterion-addressed blocker while retaining lineage to the Phase 31 receipt, the table ref, and the producer criterion.
- **D-04:** Do not change the Phase 26 or Phase 31 producer contracts and do not add a generic recursive flattener. Producer-specific adapters must carry domain meaning and stable lineage.

### Canonical Blocker Identity

- **D-05:** Every normalized Phase 27/28 row must expose the typed immutable source fields `source_domain`, `producer_phase`, `producer_artifact_kind`, `source_row_kind`, and `source_subject_id`.
- **D-06:** Derive `row_id` only from that immutable source tuple. Mutable owner, status, evidence, timestamps, paths, and required-next-action values must not change a row's identity.
- **D-07:** Preserve producer-native subjects when mapping rows: Phase 27 `packet_id` or producer `row_id`, Phase 28 `criterion_id`, and the fixed `final-reference-demotion-allowed` subject for the demotion record.
- **D-08:** Keep later resolution semantics separate through explicit `decision_axis` and `decision_subject_id` fields. Retained-code, residual-risk, exception, readiness, and demotion are distinct axes even when they refer to similar criteria.
- **D-09:** Downstream matching must require exact canonical row-ref equality plus matching `decision_axis` and `decision_subject_id`. Gate names, stream names, path similarity, or prefixes are validation context only and must never be fallback join keys.
- **D-10:** One decision may resolve multiple blocker rows only when it explicitly enumerates every canonical row ref. Duplicate, missing, mismatched, or colliding identities fail closed.

### Fail-Closed Shape Policy

- **D-11:** Use contract-keyed, required-core adapters selected by the Phase 31 stream and the expected Phase 26/27/28 artifact identity.
- **D-12:** Validate required decision-bearing fields, types, row discriminators, and enums while allowing additive non-semantic producer metadata. When an optional field becomes authoritative for identity or resolution, promote it into the required-core contract and tests.
- **D-13:** A recognized container or row with invalid required structure becomes a `malformed` blocker. An unsupported envelope, row discriminator, or status remains `unknown_unclassified`. Both outcomes are critical, proof-ineligible, and visible in the canonical register.
- **D-14:** Never collapse a recognized, valid producer table into `unknown_unclassified`, and never silently drop an unrecognized or malformed row.

### Producer-Shaped Regression Boundary

- **D-15:** Focused positive regressions must execute or reuse actual Phase 26 output through Phase 31 into Phase 32 and actual Phase 27/28 producer outputs into Phase 32. Handwritten single-row substitutes are insufficient for the producer-consumer boundary.
- **D-16:** Add one-concern negative regressions for missing or mistyped `rows`, non-object entries, missing or mistyped required fields, duplicate identities, unknown row kinds or statuses, unsupported envelopes, and identity collisions.
- **D-17:** Phase 36 verification stops at the Phase 32 canonical register and downstream handoff. Phase 34 decision reconciliation and full Phase 31-35 authority flows are explicitly out of scope.

### the agent's Discretion

- Choose the smallest clear module split for adapter dispatch, required-core validation, identity construction, and classification while respecting the repository's file/function refactor triggers.
- Choose exact internal helper names and whether focused regressions invoke producer functions directly or through existing Bazel/runfiles wiring, provided the tests exercise real producer output shapes and the repo-native verification command covers them.
- Additive metadata fields may pass through or be ignored when they are neither authoritative nor secret-bearing; required identity, resolution, provenance, and proof-eligibility fields may not be ignored.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Audit Findings

- `.planning/ROADMAP.md` — Phase 36 goal, dependency, requirements, audit-gap mapping, and success criteria.
- `.planning/REQUIREMENTS.md` — `INTAKE-04`, `TRIAGE-01`, and `TRIAGE-02` requirements and Phase 36 traceability.
- `.planning/STATE.md` — Current fail-closed, evidence-sanitization, and demotion-authority decisions.
- `.planning/v1.3-MILESTONE-AUDIT.md` — Integration gaps B1 and B2, broken approved-path evidence, exact source locations, and phase-boundary routing.

### Existing Phase 32 Contract

- `.planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md` — Locked Phase 32 adapter, taxonomy, proof-eligibility, and stable-row decisions.
- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` — Current canonical register, problem-kind, output, and downstream handoff contract.
- `tools/bazel/phase32_blocker_register_triage.py` — Current source loading, single-row classification, blocker identity, and output generation.
- `tools/bazel/phase32_blocker_register_triage_test.py` — Existing Phase 32 classification and handoff regression patterns.

### Actual Producer Shapes

- `.planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md` — Release/signing row-table, upstream criterion, lineage, and secret-handling decisions.
- `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` — Canonical Phase 26 row-table criteria and required fields.
- `tools/bazel/phase26_release_signing_upstream_evidence.py` — Actual `{"rows": [...]}` producer and retained output behavior.
- `tools/bazel/phase26_release_signing_upstream_evidence_test.py` — Producer-shaped release and upstream-row fixtures.
- `.planning/milestones/v1.2-phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md` — Retained-code, residual-risk, exception, and readiness decision axes.
- `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json` — Canonical Phase 27 packet, row, exception, and Phase 28 handoff fields.
- `tools/bazel/phase27_retained_code_acceptance_decisions.py` — Actual Phase 27 row types, packet IDs, row IDs, and decision projections.
- `tools/bazel/phase27_retained_code_acceptance_decisions_test.py` — Producer-shaped retained-code and decision fixtures.
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md` — Readiness, residual-risk, and separate demotion authorization decisions.
- `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` — Canonical Phase 28 criterion and demotion shapes.
- `tools/bazel/phase28_final_readiness_packet.py` — Actual readiness, residual-risk, and demotion output rows.
- `tools/bazel/phase28_final_readiness_packet_test.py` — Producer-shaped readiness and demotion fixtures.

### Phase 31 Provenance Boundary

- `.planning/phases/31-final-evidence-intake/31-CONTEXT.md` — Finality, provenance, accepted-receipt, and Phase 32 handoff decisions.
- `tools/bazel/manifests/phase31_final_evidence_intake_contract.json` — Accepted stream and consumed upstream ref contract.
- `tools/bazel/phase31_final_evidence_intake.py` — Phase 26 table validation and receipt-reference behavior.
- `tools/bazel/phase31_final_evidence_intake_test.py` — Accepted, rejected, malformed, unsafe-ref, and secret-bearing intake regressions.

### Downstream Compatibility

- `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` — Current explicit blocker-row reference and decision-input fields.
- `tools/bazel/phase33_maintainer_decision_inputs.py` — Current Phase 33 decision normalization and blocker ref validation.
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py` — Downstream consumer whose B1 reconciliation remains Phase 37 scope.

### Standards and Verification

- `AGENTS.md` — Repository instructions, GSD workflow enforcement, conventions, and project constraints.
- `AGENTS.bright-builds.md` — Bright Builds architecture, code-shape, verification, and testing defaults.
- `standards/core/architecture.md` — Parse boundary data into domain types and keep adapters thin around a pure core.
- `standards/core/code-shape.md` — Early returns, explicit optional naming, and function/file refactor triggers.
- `standards/core/testing.md` — Behavior-focused, one-concern, Arrange/Act/Assert unit tests.
- `standards/core/verification.md` — Repo-native verification, sync, and pre-commit evidence requirements.
- `tools/bazel/BUILD.bazel` — Phase verifier/test targets and runfiles.
- `BUILD.bazel` — Root aliases for phase verification.
- `tools/bazel/rust_workflow.sh` — Workflow dispatch and producer/consumer orchestration.
- `justfile` — Developer-facing phase verification recipes.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase31_final_evidence_intake.py` already validates individual Phase 26 entries while preserving a reference to the enclosing table; Phase 32 can reuse those accepted-final invariants without moving authority upstream or downstream.
- `tools/bazel/phase32_blocker_register_triage.py` already centralizes blocker classification and output generation; Phase 36 should deepen its input adapters and identity model rather than create a second register.
- Phase 26, 27, and 28 producer functions and tests already create authoritative shapes suitable for focused integration fixtures.
- Phase 33 already requires explicit `blocker-register.json#row_id` references; stable Phase 32 IDs can preserve that explicit-ref posture while adding typed decision axes.

### Established Patterns

- Evidence and decision phases use Python standard-library verifiers, JSON contracts, focused script-local tests, Bazel labels, ignored retained outputs under `build/ci-evidence/phaseXX`, shell dispatch, and `just phaseXX-verify`.
- Source contracts remain authoritative; consumers use small adapters instead of rewriting upstream schemas.
- Unknown, malformed, redaction-failed, lifecycle-mismatched, unsafe, or secret-bearing evidence fails closed before it can become proof-eligible.
- Final readiness, cutover approval, and reference demotion are separate authorities and must not be inferred from normalized green evidence.

### Integration Points

- Adapter dispatch and canonical identity construction belong at the Phase 32 source-loading boundary before blocker classification.
- The Phase 32 contract and handoff outputs must expose stable source and decision identities for Phase 37 without implementing Phase 37 matching.
- Bazel/runfiles and `just phase32-verify` must cover the actual Phase 26-through-31 table path and Phase 27/28 producer-shaped inputs.

</code-context>

<specifics>
## Specific Ideas

- Treat the canonical identity as two linked concepts: immutable source identity determines `row_id`; explicit decision identity determines what later approval or rejection may resolve.
- Preserve lineage as structured fields rather than baking mutable artifact paths or evidence details into a hash.
- Make table validity atomic: a malformed Phase 26 container never yields a partially eligible subset.
- Keep positive producer-shape regressions and negative one-concern mutations at the Phase 32 boundary so Phase 36 stays narrow and diagnostic.

</specifics>

<deferred>
## Deferred Ideas

- Phase 34 exact decision reconciliation, including how Phase 33 decisions clear canonical Phase 27/28 blocker rows, belongs to Phase 37.
- Full Phase 31-35 approved, blocked, targeted-repair, and upstream-failure authority flows belong to Phase 38.
- Milestone summary metadata and stale roadmap plan details belong to Phase 39.
- A broad persistent identity registry is unnecessary unless producer-native keys later prove unstable.

</deferred>

***

*Phase: 36-normalize-evidence-and-blocker-rows*
*Context gathered: 2026-07-26*
