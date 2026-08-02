---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 38-2026-07-26T16-29-23
generated_at: 2026-07-26T16:29:23.658Z
---

# Phase 38: Fail-Closed Cutover Workflow - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 38 makes the full Phase 31-through-35 cutover workflow fail closed as one operational path. Every invalid Phase 31 or Phase 33 source must replace prior Phase 34 readiness and Phase 35 cutover authority with durable blocked artifacts before the workflow returns failure. Valid complete inputs must reach the correct approved production-cutover-planning route, blocked inputs must retain an exact targeted-repair route, and reference-demotion authority must remain a separate explicit predicate.

The phase also closes the staged-install recovery gap in Phase 35 and proves the workflow through real producer-shaped end-to-end regressions. It does not perform production cutover, demote the C/C++ reference, broaden evidence schemas, repair unrelated blockers, or reconcile milestone metadata reserved for Phase 39.

</domain>

<decisions>
## Implementation Decisions

### Durable authority replacement

- **D-01:** Keep the existing Phase 34 readiness bundle and Phase 35 cutover bundle as the public authority surfaces. Do not introduce a new generation-pointer publication model in this phase.
- **D-02:** Extend Phase 34 source-failure handling so every invalid or unreadable Phase 31 or Phase 33 input produces a contract-defined durable blocked Phase 34 replacement before the command returns nonzero. The fallback must cover failures that currently occur before demotion-handoff loading.
- **D-03:** Replace implicit `set -e` sequencing with explicit workflow finalization. The production coordinator must capture Phase 34 status, invoke Phase 35 against the newly published Phase 34 result even when Phase 34 failed, and return nonzero only after Phase 35 has durably replaced stale cutover authority.
- **D-04:** Preserve the original failure status and safe diagnostic category after fallback publication. A blocked artifact is required authority state, not permission to hide the operational failure.
- **D-05:** Blocked replacements must clear or supersede prior approved readiness, cutover verdicts, production-cutover routes, and open demotion-gate projections. Readiness approval, cutover approval, and demotion authorization remain separate states.

### Safe staged installation

- **D-06:** Add a durable fail-closed authority guard around Phase 35 staged installation. The guard becomes blocking before any canonical-bundle mutation and remains authoritative through rename, validation, cleanup, rollback, and recovery failures.
- **D-07:** On staged-install failure, restore the prior bundle for availability only while the blocking guard remains in force. Never restore a stale approved bundle as current authority merely because the staged rename failed.
- **D-08:** Clear or commit the guard only after the installed canonical bundle is revalidated as a safe complete result. If validation or guard cleanup fails, the externally observable authority remains blocked and the command returns nonzero.
- **D-09:** Recovery must end with either a validated blocked replacement or a restored safe prior bundle governed by the blocking guard. Deleting the prior backup without restoration is not acceptable.
- **D-10:** Fault-injection regressions must cover guard publication, prior-bundle move, staged rename, post-install validation, compensating restore, and cleanup/recovery boundaries as focused concerns.

### End-to-end workflow and routing matrix

- **D-11:** Extract or reuse one small production workflow coordinator that is called by `tools/bazel/rust_workflow.sh` and directly exercised by the integration suite. The shell remains a thin dispatch surface rather than the only place where failure-finalization semantics live.
- **D-12:** Extend the existing actual-producer Phase 31-through-34 baseline through Phase 35. Do not replace real producer outputs with handwritten snapshot-only fixtures.
- **D-13:** The end-to-end matrix must prove four primary paths: default blocked to targeted repair, complete valid inputs to approved production-cutover planning, one exact invalid input to named targeted repair with a fresh decision required, and each relevant Phase 31/33 source failure replacing seeded prior Phase 34/35 approval before nonzero exit.
- **D-14:** Keep demotion checks orthogonal to cutover routing: approved cutover with missing or rejected demotion stays closed; valid demotion approval with blocked readiness stays closed; only unblocked readiness plus valid explicit demotion approval opens the dry run.
- **D-15:** Use one canonical real-producer baseline with small one-concern mutations and separate staged-install fault tests. Avoid a large Cartesian-product shell suite.

### the agent's Discretion

- Choose the exact coordinator module name, guard artifact name, stable safe reason codes, and minimal helper boundaries.
- Choose whether Phase 34 and Phase 35 share a small publication helper or retain phase-local adapters over a common policy core.
- Choose the fault-injection seam and test helper structure, provided production code has no hidden test-only authority path and every test remains focused.
- Split oversized verifier or test files only where required for the Phase 38 implementation boundary; broad cleanup remains out of scope.

</decisions>

<canonical-refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and audit gap

- `.planning/PROJECT.md` — v1.3 cutover-approval scope, explicit demotion boundary, and out-of-scope production actions.
- `.planning/REQUIREMENTS.md` — `READY-02`, `READY-03`, `CUTOVER-01`, and `CUTOVER-03` acceptance requirements.
- `.planning/ROADMAP.md` — Phase 38 goal, dependency, gap-closure scope, and five success criteria.
- `.planning/STATE.md` — Current phase position, fail-closed authority decisions, and milestone continuity.
- `.planning/v1.3-MILESTONE-AUDIT.md` — B3 stale-authority defect, broken/partial flows, staged-install recovery debt, and source evidence.

### Locked upstream decisions

- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-CONTEXT.md` — Canonical readiness ledger, durable blocked dry-run requirement, and orthogonal demotion predicate.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-01-SUMMARY.md` — Phase 34 implementation and publication boundary.
- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-02-SUMMARY.md` — Required-stream completeness hardening.
- `.planning/phases/35-cutover-decision-artifact/35-CONTEXT.md` — Closed verdict truth table, fail-closed source handling, strict routing, and demotion separation.
- `.planning/phases/35-cutover-decision-artifact/35-01-SUMMARY.md` — Phase 35 verdict and audit-link implementation.
- `.planning/phases/35-cutover-decision-artifact/35-02-SUMMARY.md` — Existing source-failure replacement and staged publication behavior.
- `.planning/phases/37-reconcile-decisions-into-readiness/37-CONTEXT.md` — Exact typed decision reconciliation and Phase 38 workflow boundary.
- `.planning/phases/37-reconcile-decisions-into-readiness/37-02-SUMMARY.md` — Real Phase 31-through-34 producer baseline and focused mutation pattern.
- `.planning/phases/37-reconcile-decisions-into-readiness/37-VERIFICATION.md` — Passed readiness integration evidence and remaining Phase 35 boundary.

### Active implementation and verification surfaces

- `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json` — Phase 34 output, reason-code, readiness, and demotion contract.
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py` — Current early source-loading and narrow fallback behavior to harden.
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py` — Focused Phase 34 fallback, authority, and security regressions.
- `tools/bazel/phase34_decision_reconciliation_integration_test.py` — Existing actual-producer Phase 31-through-34 baseline.
- `tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json` — Phase 35 verdict, route, fallback, and generated-output contract.
- `tools/bazel/phase35_cutover_decision_artifact.py` — Current staged install, source-failure bundle, verdict, and routing implementation.
- `tools/bazel/phase35_cutover_decision_artifact_test.py` — Existing verdict matrix, source-failure replacement, security, and wiring regressions.
- `tools/bazel/rust_workflow.sh` — Current `set -euo pipefail` Phase 34-before-35 orchestration boundary.
- `tools/bazel/BUILD.bazel` — Hermetic verifier and test target wiring.
- `BUILD.bazel` — Root aliases and planning-document filegroups.
- `justfile` — Repository-owned verification facade.

### Required repository standards

- `AGENTS.md` — Repository instructions, GSD workflow enforcement, project constraints, and generated-file ownership.
- `AGENTS.bright-builds.md` — Bright Builds workflow, architecture, code-shape, verification, and testing defaults.
- `standards-overrides.md` — No active local exception to the applicable standards.
- `standards/core/architecture.md` — Functional-core/imperative-shell and boundary parsing guidance.
- `standards/core/code-shape.md` — Early returns, thin orchestration, and file/function refactor triggers.
- `standards/core/testing.md` — One-concern, behavior-focused Arrange/Act/Assert test requirements.
- `standards/core/verification.md` — Sync-first and repo-native verification requirements.

</canonical-refs>

<code-context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase34_decision_reconciliation_integration_test.py`: Reuse its real Phase 31, Phase 32, Phase 33, and Phase 34 producer baseline, then extend the same fixture through Phase 35.
- `tools/bazel/phase35_cutover_decision_artifact.py`: Reuse its staged bundle creation, validated blocked source-failure bundle, total verdict reducer, route projection, and output validation.
- `tools/bazel/phase35_cutover_decision_artifact_test.py`: Reuse seeded prior-approval fixtures and one-source-failure mutation patterns.
- Phase 34 and Phase 35 JSON contracts: Extend existing authority surfaces instead of inventing a parallel cutover schema.

### Established Patterns

- Evidence phases use standard-library Python verifiers with pure evaluators, thin filesystem shells, contract-defined JSON, focused `unittest` suites, Bazel targets, `rust_workflow.sh` dispatch, and `just` facades.
- The default quick path remains blocked and never synthesizes maintainer authorization.
- Machine-readable bundles are authoritative; Markdown reports are derived views.
- Operational failures may return nonzero after publishing a durable blocked result.

### Integration Points

- Phase 34 consumes Phase 31 final-intake outputs and the Phase 33 downstream handoff, then publishes under `build/ci-evidence/phase34`.
- Phase 35 consumes the Phase 34 bundle and publishes the cutover decision and route under `build/ci-evidence/phase35`.
- `rust_workflow.sh` currently sequences those commands under `set -euo pipefail`; Phase 38 must make that path invoke fail-closed finalization explicitly.
- Bazel and `just phase35-verify` must run the real-producer workflow matrix and focused install-fault suite before publication.

</code-context>

<specifics>
## Specific Ideas

- Treat blocked artifact publication as authority revocation that must complete before failure is reported.
- Keep a compact coordinator result containing Phase 34 status, Phase 35 status, final authority state, and safe reason categories without copying raw evidence.
- Seed an approved Phase 34/35 bundle before every upstream-failure regression so the test proves replacement rather than merely observing an already-blocked workspace.
- Make the blocking guard impossible for ordinary readers to ignore by validating it at the same boundary that loads the canonical Phase 35 bundle.

</specifics>

<deferred>
## Deferred Ideas

- Immutable multi-generation authority directories and an atomic active-generation pointer remain a possible post-cutover operability design, but are not required for this narrow gap closure.
- Production cutover and reference demotion remain POST-01 after an approved decision and separate valid authorization.
- Phase 39 owns milestone requirement and roadmap metadata reconciliation.

</deferred>

*Phase: 38-fail-closed-cutover-workflow*
*Context gathered: 2026-07-26*
