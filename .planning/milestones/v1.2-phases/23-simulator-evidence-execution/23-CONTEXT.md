---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 23-2026-06-23T18-45-38
generated_at: 2026-06-23T18:45:38Z
---

# Phase 23: Simulator Evidence Execution - Context

**Gathered:** 2026-06-23
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 23 executes the real simulator evidence path that v1.1 made contract-ready. It should let maintainers supply, validate, retain, and summarize real simulator result packets for startup, G-code, GUI, storage, transfer, and selected failure flows using the Phase 14 simulator evidence contract as the source of truth.

This phase does not redesign the v1.0 parity contracts, does not promote simulator proof into hardware proof, and does not allow final reference demotion. It turns real simulator evidence inputs into secret-safe, traceable, machine-readable retained outputs for later cutover acceptance phases.

</domain>

<decisions>
## Implementation Decisions

### Evidence Input Model
- **D-01:** Treat `tools/bazel/manifests/phase14_simulator_evidence_contract.json` as the canonical scenario catalog for Phase 23. The Phase 23 implementation may add a v1.2 result packet/schema around it, but it must not fork or silently redefine the Phase 14 scenario IDs.
- **D-02:** Require every Phase 14 simulator scenario to be represented by the real evidence packet. Missing scenarios must remain blocked or failed; they cannot be hidden by aggregate pass wording.
- **D-03:** Accept real simulator evidence as sanitized metadata plus artifact references, not as raw simulator payload dumps. Firmware identity, simulator identity, command/runtime metadata, scenario status, artifact refs, operator, and timestamp are required fields.

### Status and Acceptance Semantics
- **D-04:** Normalize each scenario to the v1.2 status set required by the roadmap: `passed`, `failed`, `blocked`, or `exception-requested`.
- **D-05:** Preserve Phase 14 pending and residual statuses as source context, but do not let `pending-simulator-input` or `pending-simulator-dependency` count as a Phase 23 pass. They should normalize to `blocked` unless a maintainer supplies an explicit exception request.
- **D-06:** Keep hardware-only, live-service, release, and maintainer-review boundaries visible in the retained output. Simulator pass status must not claim physical timing, thermal/motion safety, storage-media behavior, live service behavior, release readiness, or demotion approval.

### Retained Artifacts and Redaction
- **D-07:** Retained Phase 23 outputs should live under a Phase 23 evidence root, expected to follow the existing `build/ci-evidence/phaseXX` convention unless planning finds a stronger local pattern.
- **D-08:** Reject or redact private keys, certificates, tokens, Wi-Fi credentials, raw crash dumps, firmware payload bytes, and non-local overclaim phrases using the existing Phase 14/18/19 guard style.
- **D-09:** Store a normalized scenario summary, redacted evidence summary, run manifest, contract snapshot or contract reference, and upstream-consumable result row(s) for later acceptance phases.

### Integration and Verification
- **D-10:** Add Phase 23 verification as a narrow extension around existing Bazel/Python evidence tooling, with root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring consistent with Phases 14, 18, 19, 20, and 21.
- **D-11:** Include focused Python tests for schema validation, status normalization, missing scenario rejection, redaction/secret guards, non-local overclaim guards, and wiring checks.
- **D-12:** Phase 23 verification should pass from checked-in safe fixtures and blocked placeholders, while clearly distinguishing fixture/smoke evidence from real simulator proof.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 23 input template, result manifest, normalized summary, and upstream row output, provided they are explicit, documented by tests, and stable for later phases.
- Decide whether to implement Phase 23 as a new `phase23_*` Python verifier, a wrapper around Phase 14 tooling, or both, as long as it avoids schema drift and preserves Phase 14 as the v1.1 source contract.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless the planner finds a real dependency split.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 23 Scope
- `.planning/ROADMAP.md` - Phase 23 goal, success criteria, dependency, and active milestone scope.
- `.planning/REQUIREMENTS.md` - EVID-01 requirement and v1.2 traceability table.
- `.planning/PROJECT.md` - Current milestone posture, non-local evidence constraints, and key decisions about simulator proof and demotion blocking.

### v1.1 Simulator Contract
- `.planning/milestones/v1.1-ROADMAP.md` - Phase 14 simulator evidence gate intent and completed v1.1 evidence-hardening context.
- `tools/bazel/manifests/phase14_simulator_evidence_contract.json` - Canonical simulator scenario catalog, source refs, status vocabulary, required artifact kinds, and residual non-simulator boundaries.
- `tools/bazel/phase14_simulator_evidence.py` - Existing simulator evidence verifier, quick artifact writer, real-run path, redaction guards, and no-overclaim checks.
- `tools/bazel/phase14_simulator_evidence_test.py` - Test patterns for contract validation, negative fixtures, redaction, and wiring.

### Aggregate and Acceptance Consumers
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - Existing aggregate evidence gate model and external-input placeholder for real simulator evidence.
- `tools/bazel/phase19_aggregate_ci_evidence.py` - Aggregate evidence retention and external-input placeholder behavior.
- `tools/bazel/phase18_cutover_review.py` - Upstream-result consumption, final-demotion blocking, exception coverage, and redaction/overclaim policy.
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - Final review schema and upstream-result requirement references consumed by later acceptance phases.

### Build and Workflow Wiring
- `BUILD.bazel` - Root filegroups and aliases for phase evidence docs and verification labels.
- `tools/bazel/BUILD.bazel` - Evidence verifier targets, data dependencies, and shell binary wiring.
- `tools/bazel/rust_workflow.sh` - Dispatch cases for phase verification commands.
- `justfile` - Developer-facing phase verification recipes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase14_simulator_evidence.py` already validates the simulator contract, writes quick placeholder artifacts, runs real simulator pytest nodes when supplied a firmware binary, and rejects secret/overclaim content.
- `tools/bazel/phase14_simulator_evidence_contract.json` already names every simulator scenario, its pytest node IDs, retained artifact kind, v1 requirement IDs, and residual non-simulator gates.
- `tools/bazel/phase19_aggregate_ci_evidence.py` already models how locally runnable gate evidence and external-input placeholders are retained in aggregate CI.
- `tools/bazel/phase18_cutover_review.py` already validates upstream result rows, exception coverage, and demotion blocking when upstream evidence is missing, failed, stale, redaction-failed, or not exception-approved.

### Established Patterns
- Phase evidence tools are Python scripts under `tools/bazel/`, with matching `*_test.py` unit tests, manifest JSON under `tools/bazel/manifests/`, Bazel shell targets, root aliases, `rust_workflow.sh` dispatch, and a `just phaseXX-verify` facade.
- Evidence output roots use `build/ci-evidence/phaseXX`, keep generated artifacts out of source control, and retain safe planning/source manifests in the repo.
- Existing verification favors fail-closed schema checks, explicit source refs, repo-relative artifact paths, and phrase-based guards against non-local proof overclaims.

### Integration Points
- Phase 23 should add new Bazel/just labels without breaking existing Phase 14/19 labels.
- Later v1.2 phases need Phase 23 outputs as upstream-consumable rows or retained references; keep the output schema machine-readable and stable enough for Phase 26-28 to consume.
- `.planning/phases/23-simulator-evidence-execution/` owns Phase 23 lifecycle artifacts, while generated evidence remains under ignored build output directories.

</code_context>

<specifics>
## Specific Ideas

No user-supplied examples beyond the v1.2 roadmap. Use the v1.1 Phase 14 contract and existing evidence verifier style as the concrete model.

</specifics>

<deferred>
## Deferred Ideas

- Hardware, storage-media, UI-input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output proof belongs to Phase 24.
- Live Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump proof belongs to Phase 25.
- Release/signing/provenance and broad upstream result evidence belongs to Phase 26.
- Retained-code, residual-risk, exception, and final maintainer acceptance decisions belong to Phase 27 and Phase 28.

</deferred>

---

*Phase: 23-simulator-evidence-execution*
*Context gathered: 2026-06-23*
