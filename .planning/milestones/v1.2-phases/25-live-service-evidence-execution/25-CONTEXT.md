---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 25-2026-06-23T21-12-42
generated_at: 2026-06-23T21:12:46.652Z
---

# Phase 25: Live-Service Evidence Execution - Context

**Gathered:** 2026-06-23
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 25 executes the real live-service evidence path that v1.1 made contract-ready. It should let maintainers supply, validate, retain, and summarize real live-service result packets for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows using the Phase 16 live-network evidence contract as the source of truth.

This phase does not redesign the v1.0 parity contracts, does not treat simulator or hardware proof as live-service proof, does not collect release/signing evidence, and does not allow final reference demotion. It turns real live-service evidence inputs into secret-safe, traceable, machine-readable retained outputs for later cutover acceptance phases.

</domain>

<decisions>
## Implementation Decisions

### Evidence Input Model
- **D-01:** Treat `tools/bazel/manifests/phase16_live_network_evidence_contract.json` as the canonical scenario catalog for Phase 25. The Phase 25 implementation may add a v1.2 result packet/schema around it, but it must not fork, rename, or silently redefine Phase 16 scenario IDs.
- **D-02:** Require every Phase 16 live-service scenario to be represented by the real evidence packet. Missing, duplicate, or unknown scenarios must fail validation.
- **D-03:** Accept real live-service evidence as sanitized operator metadata plus artifact references, not raw service payloads, credentials, tokens, private certificates, raw HTTP/TLS logs, crash dumps, or firmware payloads.

### Status and Acceptance Semantics
- **D-04:** Normalize each Phase 25 scenario to the v1.2 status set required by the roadmap: `passed`, `failed`, `blocked`, or `exception-requested`.
- **D-05:** Preserve Phase 16 source statuses as source context, but do not let `pending-live-input`, `manual-live-service-required`, `controlled-service-required`, `blocked-credentials-unavailable`, `blocked-endpoint-unavailable`, or `not-applicable-with-justification` count as a Phase 25 pass.
- **D-06:** Keep simulator-only, hardware/media/safety, release/signing, retained-code, maintainer-review, and demotion boundaries visible in retained outputs. Live-service pass status must not claim release readiness, retained-code acceptance, final readiness, or reference demotion approval.

### Live-Service Coverage and Redaction
- **D-07:** Require scenario rows to preserve Phase 16 `service_surface`, `mode`, evidence type, firmware build, operator, timestamp, artifact references, redaction summary, and residual risk.
- **D-08:** Connect, WUI, TLS, proxy, transfer, negative-protocol, long-transfer, and crash-dump rows must remain distinct. The retained summary must not collapse them into one generic network pass.
- **D-09:** Passed live-service rows require passed source refs and passed redaction status. Source-contract rows may pass only with source-contract validation evidence.

### Retained Artifacts and Integration
- **D-10:** Retained Phase 25 outputs should live under `build/ci-evidence/phase25`, following the Phase 23 and Phase 24 execution conventions.
- **D-11:** Reject private keys, certificates, tokens, registration codes, fingerprints, passwords, API keys, raw HTTP/TLS logs, raw production payloads, raw crash dumps, firmware payload bytes, and non-local overclaim phrases.
- **D-12:** Store a normalized scenario summary, redacted live-service summary, run manifest, source contract snapshot or contract reference, operator input template, artifact summary, and upstream-consumable result row for later acceptance phases.

### Verification
- **D-13:** Add Phase 25 verification as a narrow extension around existing Bazel/Python evidence tooling, with root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring consistent with Phases 16, 23, and 24.
- **D-14:** Include focused Python tests for scenario coverage, status normalization, exception metadata, artifact reference bounds, service-surface drift, evidence-type requirements, redaction/secret guards, retained output writing, upstream result rows, and wiring checks.
- **D-15:** Phase 25 verification should pass from checked-in safe fixtures and blocked placeholders, while clearly distinguishing fixture/smoke evidence from real live-service proof.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 25 input template, result manifest, normalized summary, retained artifact summary, and upstream row output, provided they are explicit, tested, and stable for later phases.
- Decide whether to implement Phase 25 as a new `phase25_*` Python verifier, a wrapper around Phase 16 tooling, or both, as long as it avoids schema drift and preserves Phase 16 as the v1.1 source contract.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless planning finds a real dependency split.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 25 Scope
- `.planning/ROADMAP.md` - Phase 25 goal, success criteria, dependency, and active milestone scope.
- `.planning/REQUIREMENTS.md` - EVID-03 requirement and v1.2 traceability table.
- `.planning/PROJECT.md` - Current milestone posture, non-local evidence constraints, and key decisions about live-service proof and demotion blocking.
- `.planning/phases/23-simulator-evidence-execution/23-CONTEXT.md` - Prior decision that simulator proof stays separate from live-service proof.
- `.planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md` - Prior decision that hardware/media/safety proof stays separate from live-service proof.

### v1.1 Live-Service Contract
- `tools/bazel/manifests/phase16_live_network_evidence_contract.json` - Canonical live-service scenario catalog, service surfaces, modes, source refs, status vocabulary, artifact kinds, and residual non-live gates.
- `tools/bazel/phase16_live_network_evidence.py` - Existing live-network evidence verifier, quick artifact writer, source contract checks, redaction guards, and no-overclaim checks.
- `tools/bazel/phase16_live_network_evidence_test.py` - Test patterns for contract validation, operator evidence input, negative fixtures, redaction, and wiring.
- `tools/bazel/fixtures/phase9_negative_network_cases.json` - Negative protocol cases relevant to WUI/Connect scenario rows.
- `doc/proxy_support.md` - Proxy limitation source doc referenced by the Phase 16 contract.
- `doc/metrics.md` - Metrics/syslog source doc referenced by the Phase 16 contract.

### Aggregate and Acceptance Consumers
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - Final review schema, retained-code packets, live-service evidence criterion, residual risk refs, and upstream-result expectations.
- `tools/bazel/phase18_cutover_review.py` - Upstream-result consumption, final-demotion blocking, exception coverage, and redaction/overclaim policy.
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - Aggregate evidence gate model and external-input placeholders for live-service evidence.
- `tools/bazel/phase19_aggregate_ci_evidence.py` - Aggregate evidence retention and external-input placeholder behavior.
- `tools/bazel/phase23_simulator_evidence_execution.py` - v1.2 execution-phase pattern for wrapping a v1.1 evidence contract with real evidence submission and retention semantics.
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` - Current v1.2 hardware execution analogue for contract wrapping, retained outputs, and upstream row generation.

### Build and Workflow Wiring
- `BUILD.bazel` - Root filegroups and aliases for phase evidence docs and verification labels.
- `tools/bazel/BUILD.bazel` - Evidence verifier targets, data dependencies, and shell binary wiring.
- `tools/bazel/rust_workflow.sh` - Dispatch cases for phase verification commands.
- `justfile` - Developer-facing phase verification recipes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase16_live_network_evidence.py` already validates the Phase 16 live-network contract, writes quick placeholder artifacts, validates operator evidence rows, enforces source-ref coverage, and rejects secret or overclaim content.
- `tools/bazel/manifests/phase16_live_network_evidence_contract.json` already names Connect, WUI, TLS, proxy, transfer, negative-protocol, long-transfer, crash-dump, telemetry, mDNS, SNTP, syslog, and contract traceability scenarios.
- `tools/bazel/phase23_simulator_evidence_execution.py` and `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` show the v1.2 pattern for adding real evidence execution semantics around a v1.1 contract without redefining the source scenario catalog.

### Established Patterns
- Phase evidence tools are Python scripts under `tools/bazel/`, with matching `*_test.py` unit tests, manifest JSON under `tools/bazel/manifests/`, Bazel shell targets, root aliases, `rust_workflow.sh` dispatch, and a `just phaseXX-verify` facade.
- Evidence output roots use `build/ci-evidence/phaseXX`, keep generated artifacts out of source control, and retain safe planning/source manifests in the repo.
- Existing verification favors fail-closed schema checks, explicit source refs, repo-relative or `external://phaseXX/` artifact refs, secret redaction, and phrase-based guards against non-local proof overclaims.

### Integration Points
- Phase 25 should add new Bazel/just labels without breaking existing Phase 16, Phase 19, Phase 23, or Phase 24 labels.
- Later v1.2 phases need Phase 25 outputs as upstream-consumable rows or retained references; keep the output schema machine-readable and stable enough for Phase 26-28 to consume.
- `.planning/phases/25-live-service-evidence-execution/` owns Phase 25 lifecycle artifacts, while generated evidence remains under ignored build output directories.

</code_context>

<specifics>
## Specific Ideas

No user-supplied examples beyond the v1.2 roadmap. Use the v1.1 Phase 16 live-network evidence contract and the Phase 23/24 evidence-execution wrapper style as concrete models.

</specifics>

<deferred>
## Deferred Ideas

- Release/signing/provenance and broad upstream result evidence belongs to Phase 26.
- Retained-code, residual-risk, exception, and final maintainer acceptance decisions belong to Phase 27 and Phase 28.
- Automatic reference demotion remains out of scope unless maintainers explicitly approve it in the final readiness phase.

</deferred>

---

*Phase: 25-live-service-evidence-execution*
*Context gathered: 2026-06-23*
