---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 35-2026-07-25T21-06-10
generated_at: 2026-07-25T21:06:10.103Z
---

# Phase 35: Cutover Decision Artifact - Context

**Gathered:** 2026-07-25
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 35 produces one auditable cutover decision artifact with exactly one verdict: `approved`, `blocked`, or `approved-with-exceptions`. It consumes the Phase 34 row-complete readiness bundle and the explicit Phase 33 decision lineage, links every input needed to audit the result, preserves reference-demotion authorization as an independent state, and emits one next-milestone route.

The phase publishes a decision and planning route only. It does not collect or reclassify evidence, create maintainer decisions, repair blockers, perform production cutover, demote the C/C++ reference, change release policy, replace retained vendor/HAL code, or expand firmware behavior.

</domain>

<decisions>
## Implementation Decisions

### Verdict Derivation
- **D-01:** Implement verdict selection as a closed, typed, pure truth-table reducer over validated Phase 34 and Phase 33 inputs. The reducer must return exactly one contract-defined verdict and default to `blocked`.
- **D-02:** Any missing, malformed, stale, duplicate, dangling, lifecycle-mismatched, redaction-failed, source-ref-failed, secret-tainted, unknown, underclassified, coverage-incomplete, or readiness-blocking input must produce `blocked`.
- **D-03:** Emit `approved-with-exceptions` only when readiness is unblocked and the exact validated set of active approved exceptions is nonempty. Broad, unmatched, rejected, expired, stale, or invalid exception records remain blocking.
- **D-04:** Emit `approved` only when readiness is unblocked and no active approved exceptions affect the cutover decision.
- **D-05:** Do not add a second cutover confirmation input in Phase 35. Existing explicit Phase 33 maintainer decisions and Phase 34 readiness evaluation remain authoritative; Phase 35 is an auditable projection rather than a duplicate approval authority.

### Canonical Audit-Link Index
- **D-06:** Generate one canonical normalized audit-link index and derive the machine-readable verdict, route artifact, and redacted Markdown report from that same index.
- **D-07:** Derive the expected link set from authoritative Phase 31-34 artifacts rather than accepting self-declared links from the decision document. Cover every blocker, exception, residual risk, evidence packet/receipt, retained-code decision, readiness result, readiness decision, demotion decision, and demotion dry-run result required by CUTOVER-02.
- **D-08:** Each link should carry a stable link id, category/kind, target semantic id, target ref, source phase lifecycle id, verdict effect, and a digest only for sanitized local targets. Use existing `submission_id`, `row_id`, and `decision_id` values where available.
- **D-09:** Fail closed on missing, extra, duplicate, dangling, lifecycle-mismatched, category-mismatched, or digest-mismatched links. Exact-set anti-joins and cross-reference validation must be tested.
- **D-10:** Never copy raw evidence packets, private keys, tokens, certificates, service payloads, raw crash dumps, raw release logs, or other secret-bearing material. Retain only validated sanitized local refs, safe digests, and approved `external://phaseXX/` refs.

### Next-Milestone Routing
- **D-11:** Use strict exclusive tri-state routing. `approved` routes to production-cutover planning; `blocked` and `approved-with-exceptions` route to targeted blocker repair.
- **D-12:** A repair route must name exact blocker, exception, residual-risk, requirement, affected-gate, owner, required-action, and exit/review-criterion refs from upstream artifacts. It must not create free-form repair scope that cannot be traced to the decision inputs.
- **D-13:** Completing repair scope requires a fresh cutover decision. Phase 35 must not auto-upgrade a prior exception-bearing or blocked verdict after follow-up work changes.
- **D-14:** A production-cutover-planning route authorizes planning only. It does not authorize production reference demotion, branch mutation, release-policy changes, or firmware rollout.

### Reference-Demotion Separation
- **D-15:** Project the Phase 33 demotion input validation state, explicit decision value, and source refs separately from the Phase 34 demotion dry-run gate state and reason codes.
- **D-16:** Keep `cutover_verdict`, `demotion_decision_state`, and `demotion_gate_state` as independent fields. Never infer demotion approval or an open demotion gate from `approved`, green evidence, unblocked readiness, accepted retained code, accepted residual risk, or approved exceptions.
- **D-17:** Preserve blocked, missing, malformed, stale, rejected, and lifecycle-mismatched demotion states in the final artifact even when the cutover verdict can otherwise be approved for planning.
- **D-18:** Production reference demotion remains POST-01 and must require its own valid authorization and execution workflow.

### Generated Outputs and Verification Boundary
- **D-19:** Add a Phase 35 JSON contract, standard-library Python verifier/generator, focused regression suite, Bazel verifier/test targets, root aliases, `rust_workflow.sh` case arms, and a `just phase35-verify` facade consistent with Phases 31-34.
- **D-20:** Write generated outputs under `build/ci-evidence/phase35`, including a run manifest, canonical audit-link index, cutover decision artifact, next-milestone route, redacted decision report, and sanitized contract/source snapshots.
- **D-21:** The normal quick/default path must generate a durable `blocked` decision and targeted-repair route. It must never synthesize real evidence, maintainer approval, exception approval, or demotion authorization.
- **D-22:** Regression fixtures must prove all three verdicts, every fail-closed boundary, exact audit-link completeness, strict route mapping, independent demotion-state truth tables, secret/unsafe-ref rejection, and consistency between JSON and Markdown projections.

### the agent's Discretion
- The agent may choose exact JSON filenames, internal helper boundaries, and stable reason-code spellings when they remain contract-defined and exhaustively tested.
- The agent may choose whether source artifact loading and normalized link construction live in one verifier file or a small repo-owned helper module.
- The agent may choose exact Bazel label names and report formatting while following the existing phase verifier and `just` patterns.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements
- `.planning/PROJECT.md` — v1.3 cutover approval trial scope, core value, explicit demotion boundary, and deferred production actions.
- `.planning/REQUIREMENTS.md` — CUTOVER-01 through CUTOVER-03, out-of-scope boundaries, and future POST-01 execution.
- `.planning/ROADMAP.md` — Phase 35 goal, success criteria, dependency on Phase 34, and next-milestone routing contract.
- `.planning/STATE.md` — current milestone state, active blockers, and evidence-sanitization constraints.

### v1.3 Decision Lineage
- `.planning/phases/31-final-evidence-intake/31-CONTEXT.md` — accepted-final evidence provenance, safe-reference, and non-final rejection boundaries.
- `.planning/phases/31-final-evidence-intake/31-01-SUMMARY.md` — delivered Phase 31 receipts, manifests, verifier, and workflow behavior.
- `.planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md` — canonical blocker taxonomy, proof eligibility, decision impact, and downstream link requirements.
- `.planning/phases/32-blocker-register-and-evidence-triage/32-01-SUMMARY.md` — delivered blocker register and handoff artifacts.
- `.planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md` — independent decision axes, exact exception coverage, readiness input, and demotion input.
- `.planning/phases/33-maintainer-decision-inputs/33-01-SUMMARY.md` — delivered decision registers, handoff manifest, verifier, and tests.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-CONTEXT.md` — row-complete readiness ledger, fail-closed predicates, and orthogonal demotion dry-run decisions.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-01-SUMMARY.md` — delivered Phase 34 contract, artifacts, verifier, workflow wiring, and verification evidence.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-02-SUMMARY.md` — required-stream completeness hardening and missing-stream regressions.

### Active Contracts and Verifiers
- `tools/bazel/manifests/phase31_final_evidence_intake_contract.json` — required stream adapters, accepted-final receipts, lifecycle, and safe source refs.
- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` — blocker rows, proof eligibility, problem kinds, owner/action fields, and decision-impact handoff.
- `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` — retained-code, residual-risk, exception, readiness, and demotion decision records.
- `tools/bazel/phase33_maintainer_decision_inputs.py` — current explicit decision and downstream handoff producer.
- `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json` — canonical Phase 35 input artifact list, ledger schema, reason codes, and readiness/demotion semantics.
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py` — row-complete readiness bundle and demotion dry-run generator.
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py` — regression examples for completeness, sparse overlays, fail-closed readiness, demotion separation, security, and output consistency.

### Build, Code Shape, Testing, and Verification
- `AGENTS.md` — repository constraints, project architecture, generated-file ownership, and GSD workflow requirements.
- `AGENTS.bright-builds.md` — Bright Builds defaults applied to this phase.
- `standards-overrides.md` — no active local exception to the relevant standards.
- `standards/core/architecture.md` — functional-core/imperative-shell guidance for verdict and route evaluation.
- `standards/core/code-shape.md` — early-return, naming, and module-size guidance.
- `standards/core/testing.md` — focused Arrange/Act/Assert unit-test requirements.
- `standards/core/verification.md` — repo-native verification and commit gate expectations.
- `tools/bazel/BUILD.bazel` — phase verifier/test target patterns.
- `BUILD.bazel` — root phase aliases and planning-doc filegroups.
- `tools/bazel/rust_workflow.sh` — phase orchestration case-arm patterns.
- `justfile` — developer-facing verification facade.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py`: Reuse its validated Phase 34 run manifest, canonical coverage ledger, readiness packet, blocker summary, and demotion dry-run outputs as the immediate source boundary.
- `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json`: Reuse generated-artifact identities, reason-code vocabulary, lifecycle refs, and security prohibitions.
- `tools/bazel/phase33_maintainer_decision_inputs.py`: Reuse stable decision ids and explicit independent readiness/demotion decision records for audit linking.
- Existing Phase 31-34 tests: Reuse standard-library `unittest` fixture, path-boundary, lifecycle, prohibited-marker, source-ref, wiring, and generated-artifact consistency patterns.

### Established Patterns
- Evidence and decision phases use JSON contracts, standard-library Python verifiers, focused script-local tests, Bazel `sh_binary` targets, root aliases, `rust_workflow.sh` arms, and `just` facades.
- Canonical machine-readable artifacts are authoritative; redacted Markdown reports are derived projections.
- Quick/default verification writes blocked or template-only artifacts and never claims real maintainer authorization.
- Security and unsafe-ref checks run before generated outputs become trusted downstream inputs.

### Integration Points
- Phase 35 should consume `build/ci-evidence/phase34/final-readiness-run-manifest.json` and only the validated artifacts referenced by that manifest, following safe refs back to Phase 31-33 when required for complete audit linkage.
- Phase 35 should write its generated bundle under `build/ci-evidence/phase35`.
- Bazel and `just` verification should regenerate prerequisite quick artifacts deterministically while preserving their blocked state.

</code-context>

<specifics>
## Specific Ideas

- Prefer a thin Phase 35 projection over the canonical Phase 34 bundle rather than a new evidence or maintainer-decision schema.
- Keep the verdict reducer pure and total, then isolate filesystem validation, security scanning, artifact loading, and writes in the imperative shell.
- Make the redacted report show the verdict, every blocking predicate, active exception, repair scope, independent demotion state, and exact safe refs from the same canonical data used by JSON outputs.

</specifics>

<deferred>
## Deferred Ideas

- Production cutover execution and reference demotion belong to POST-01 after an approved decision and separate valid authorization.
- Targeted blocker repair occurs in the next milestone named by a blocked or exception-bearing route, followed by a fresh cutover decision.
- Content-addressed attestations, signing/trust-root policy, concurrent repair-and-cutover tracks, retained vendor/HAL replacement, long-run dashboards, and expanded firmware behavior remain future work.

</deferred>

*Phase: 35-cutover-decision-artifact*
*Context gathered: 2026-07-25*
