---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 16-2026-06-18T01-09-34
generated_at: 2026-06-18T01:10:50.460Z
---

# Phase 16: Live Network and Transfer Qualification - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 16 turns the live-service and controlled-network blockers for Connect, PrusaLink/WUI, TLS, telemetry, proxy behavior, and transfers into durable, secret-safe evidence. It should define a phase-owned evidence contract, provide runnable or operator-supplied capture flows, validate generated artifacts, and expose local deterministic checks through the existing Bazel/just verification surface.

This phase does not prove release-candidate packaging or signing, retained-code maintainer acceptance, final reference demotion, or physical hardware safety. It also must not treat unavailable live service credentials or production endpoints as local pass claims. Missing live inputs should remain explicit pending live-service evidence with scenario, command, artifact, credential boundary, and residual risk named.

</domain>

<decisions>
## Implementation Decisions

### Live Evidence Contract

- **D-01:** Add a Phase 16-owned live network evidence contract instead of mutating Phase 11, Phase 13, Phase 14, or Phase 15 manifests. The contract should name each Connect, WUI, TLS, telemetry, proxy, transfer, and crash-dump evidence row with requirement mapping and proof scope.
- **D-02:** Use row-level qualification rather than one umbrella live-network pass. Every row should name scenario ID, service surface, controlled/live mode, required input kind, expected artifact path, pass/fail semantics, redaction requirements, source evidence refs, and residual non-live gates.
- **D-03:** Cover the roadmap-required families: Connect registration, telemetry, WebSocket commands, token/fingerprint behavior, proxy limitations, PrusaLink/WUI HTTP API, digest/API-key auth, SNTP, mDNS, syslog, metrics, transfers, TLS/certificate handling, negative protocol behavior, long transfers, and crash-dump upload handling.
- **D-04:** Live service availability is a first-class status. Rows without supplied service credentials, endpoint fixtures, or controlled-service artifacts should use explicit statuses such as `pending-live-input`, `manual-live-service-required`, `controlled-service-required`, or `blocked-credentials-unavailable`, never `passed`.

### Secret-Safe Artifact Model

- **D-05:** Generated Phase 16 runtime artifacts should live under an ignored directory such as `build/ci-evidence/phase16`, following the Phase 13, Phase 14, and Phase 15 pattern. Checked-in files define contracts, schema, verifier logic, redaction guards, and dry-run examples only.
- **D-06:** Generated artifacts should include a machine-readable run manifest, normalized scenario results, redacted request/response or log summaries, source contract snapshot, and references to any external artifacts. Generated output should let a maintainer diagnose what failed without exposing tokens or payload secrets.
- **D-07:** Secret-bearing material must stay out of committed source and planning artifacts: Connect tokens, registration codes, printer fingerprints when private, Wi-Fi credentials, PrusaLink passwords/API keys, private certificates, signing keys, raw crash dumps, raw production payloads, and unredacted HTTP/TLS logs.
- **D-08:** Verifier guards should reject committed artifacts or generated summaries containing secret markers, raw credential fields, private key/certificate material, raw crash-dump markers, and overclaim wording such as final cutover complete, release signed, hardware proven, or reference demotion allowed.

### Runner and Developer Workflow

- **D-09:** Add a dedicated Phase 16 standard-library Python verifier/collector over a checked-in JSON contract, mirroring the Phase 14 and Phase 15 runner shape while keeping live-service execution optional and explicitly input-driven.
- **D-10:** Expose Phase 16 through `tools/bazel/phase16_live_network_evidence.py`, `tools/bazel/phase16_live_network_evidence_test.py`, `tools/bazel/manifests/phase16_live_network_evidence_contract.json`, Bazel `phase16_verify` / `phase16_verify_tests` labels, root aliases/docs filegroups, `tools/bazel/rust_workflow.sh`, and `just phase16-verify`.
- **D-11:** Local phase verification should be deterministic: validate contract schema, source refs, wiring, dry-run generated artifacts, redaction, path guards, and overclaim guards without requiring live credentials. Real live/controlled-service capture should be available through explicit input files or command flags and should validate supplied evidence rather than inventing pass data.
- **D-12:** Keep orchestration thin and auditable: prefer JSON contracts, explicit status vocabularies, small Python helpers, `subprocess.run` without shell execution when external commands are needed, and focused stdlib tests over broad live-service automation rewrites.

### Traceability and Prior Evidence

- **D-13:** Every Phase 16 row must map to `LIVE-01`, `LIVE-02`, and/or `LIVE-03` plus relevant archived v1.0 and Phase 11 evidence rows. Rows should cite Phase 9 network/transfer/TLS source-backed contracts, Phase 13 CI retention, Phase 14 simulator boundaries, and Phase 15 hardware boundaries where applicable.
- **D-14:** Preserve Phase 14 and Phase 15 boundaries: simulator and hardware evidence may support readiness, but they do not satisfy live Connect, WUI, TLS, telemetry, proxy, or transfer service proof.
- **D-15:** Preserve Phase 13's artifact-retention model. CI may validate the contract and retain generated redacted summaries, but CI without live-service inputs should not become live network proof.
- **D-16:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 16-2026-06-18T01-09-34`.

### the agent's Discretion

- Exact scenario IDs, schema field order, status names, generated artifact names, helper boundaries, and dry-run output shape are flexible if the result remains deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated implementation plan or several tasks inside one plan, but the roadmap expects one completed plan for this phase.
- Prefer contract-backed evidence and verifier tests over prose-only checklists. Operator-facing instructions are useful only when backed by machine-readable artifacts and verifier checks.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements

- `.planning/ROADMAP.md` - Phase 16 goal, dependency, success criteria, and v1.1 roadmap position.
- `.planning/REQUIREMENTS.md` - `LIVE-01`, `LIVE-02`, and `LIVE-03` acceptance requirements.
- `.planning/STATE.md` - current milestone state, blockers, and Phase 16 starting point.
- `.planning/PROJECT.md` - Big Bang, Behavior Parity, Bazel Primary Now, justfile, safety, and Bright Builds constraints.
- `.planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md` - CI evidence contract, artifact retention, and non-local proof boundaries.
- `.planning/phases/13-ci-evidence-orchestration/13-VERIFICATION.md` - passed Phase 13 local verification boundary.
- `.planning/phases/14-simulator-evidence-gates/14-CONTEXT.md` - simulator evidence contract, dry-run artifact, transfer/WUI simulator boundary, and non-live proof limits.
- `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md` - passed Phase 14 verification and residual live-network risks.
- `.planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md` - hardware evidence contract, operator metadata, redaction, and non-live proof limits.
- `.planning/phases/15-hardware-safety-and-media-qualification/15-VERIFICATION.md` - passed Phase 15 verification and residual live-service risks.

### Archived v1.0 cutover and network evidence

- `.planning/milestones/v1.0-REQUIREMENTS.md` - archived v1.0 requirement surface that Phase 16 must not redefine.
- `.planning/milestones/v1.0-ROADMAP.md` - archived v1.0 phase history and evidence foundation.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` - v1.0 audit outcome and preserved non-local gates.
- `.planning/milestones/v1.0-phases/09-network-web-services-and-transfers/09-CONTEXT.md` - source-backed Connect, WUI, transfer, TLS, proxy, telemetry, and negative-fixture decisions.
- `.planning/milestones/v1.0-phases/09-network-web-services-and-transfers/09-VERIFICATION.md` - passed Phase 9 local evidence boundary and deferred live-service proof.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md` - parity pyramid, live network/TLS proof, retained-code, reference comparison, and overclaim decisions.
- `.planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md` - passed Phase 11 local evidence boundary.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-CONTEXT.md` - metadata hygiene and no-overclaim constraints for archived evidence.
- `.planning/milestones/v1.0-phases/12-milestone-evidence-hygiene/12-VERIFICATION.md` - v1.0 archive-clean verification record.

### Existing verifier, manifest, and evidence patterns

- `tools/bazel/phase15_hardware_evidence.py` - closest runner/verifier template for contracts, dry-run artifacts, operator input validation, path guards, security scans, and wiring checks.
- `tools/bazel/phase15_hardware_evidence_test.py` - latest stdlib regression-test pattern for evidence contract behavior.
- `tools/bazel/manifests/phase15_hardware_evidence_contract.json` - checked-in contract schema, status vocabulary, scenario rows, external-input model, source refs, and generated artifact shape to mirror.
- `tools/bazel/phase14_simulator_evidence.py` - simulator evidence verifier and real-input validation pattern.
- `tools/bazel/phase14_simulator_evidence_test.py` - simulator evidence regression-test pattern.
- `tools/bazel/manifests/phase14_simulator_evidence_contract.json` - scenario, status, and generated artifact model.
- `tools/bazel/phase13_ci_evidence.py` - CI evidence writer, artifact sanitizer, and overclaim scan pattern.
- `tools/bazel/phase13_ci_evidence_test.py` - CI evidence regression-test pattern.
- `tools/bazel/manifests/phase13_ci_evidence_contract.json` - artifact-retention and generated-output contract shape.
- `tools/bazel/phase11_verify.py` - aggregate cutover verifier, proof-scope taxonomy, and no-overclaim guard pattern.
- `tools/bazel/phase11_verify_test.py` - Phase 11 verifier regression-test pattern.
- `tools/bazel/manifests/phase11_parity_pyramid.json` - live-service layer row and cutover proof-scope taxonomy.
- `tools/bazel/manifests/phase11_cutover_readiness.json` - reference-demotion blocker and non-local evidence model.
- `tools/bazel/manifests/phase11_reference_comparisons.json` - normalized comparison rows for transfer, protocol, WUI, telemetry, and network flows.
- `tools/bazel/manifests/phase11_requirement_evidence.json` - requirement-to-evidence mapping pattern.
- `tools/bazel/manifests/phase11_retained_code_justifications.json` - retained-code evidence requirements for network, TLS, filesystem, and transfer surfaces.

### Network, transfer, TLS, and service source evidence

- `tools/bazel/manifests/phase9_connect_contracts.json` - Connect registration, telemetry, command-channel, TLS/secret, proxy, and evidence rows.
- `tools/bazel/manifests/phase9_wui_contracts.json` - WUI/PrusaLink HTTP, auth, API, and local service rows.
- `tools/bazel/manifests/phase9_network_service_contracts.json` - network service, SNTP, mDNS, metrics, syslog, and service startup rows.
- `tools/bazel/manifests/phase9_transfer_contracts.json` - transfer, download, encryption, range, and media interaction rows.
- `tools/bazel/manifests/phase9_network_concern_dispositions.json` - negative protocol, redaction, and known network concern disposition contract.
- `.planning/codebase/INTEGRATIONS.md` - Connect, WUI, transfer, TLS, proxy, metrics/syslog, SNTP, mDNS, credentials, crash dumps, CI, and artifact context.
- `.planning/codebase/TESTING.md` - simulator, pytest, CTest, WUI, transfer, integration, and CI verification surfaces.
- `.planning/codebase/CONCERNS.md` - network/TLS, transfer, crash-dump, credential, proxy, and coverage concerns that Phase 16 must keep visible.
- `doc/proxy_support.md` - current proxy behavior and limitations.
- `doc/metrics.md` - metrics/syslog behavior and collector context.
- `doc/prusa_printer_settings.ini` - settings-key names for Connect, WUI, credentials, metrics, syslog, and proxy configuration.
- `src/connect/` - Connect registration, telemetry, events, WebSocket command channel, token/fingerprint, host, and proxy integration.
- `src/connect/tls/` - TLS, certificate, socket, hardware entropy, and custom CA behavior.
- `src/transfers/` - transfer and download behavior, range handling, encrypted downloads, partial-file behavior, and crash/transfer interactions.
- `src/common/http/` - HTTP client, proxy, parser, and transfer support.
- `lib/WUI/` - PrusaLink/WUI HTTP service, auth, API, SNTP, mDNS, static assets, and local service startup.
- `src/syslog/` and `src/common/metric.cpp` - syslog and metrics transport behavior.

### Repo and standards guidance

- `AGENTS.md` - repo-local GSD workflow and Bright Builds routing rules.
- `AGENTS.bright-builds.md` - managed Bright Builds workflow, sync, verification, and standards-routing rules.
- `standards-overrides.md` - confirms no active local Bright Builds override.
- `standards/core/architecture.md` - functional-core/imperative-shell and domain modeling guidance.
- `standards/core/code-shape.md` - early returns, `maybe_`, and size guidance.
- `standards/core/verification.md` - sync, hook, and pre-commit verification rules.
- `standards/core/testing.md` - focused unit-test and Arrange/Act/Assert expectations.
- `standards/languages/rust.md` - Rust standards if Phase 16 adds or changes Rust domain types.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `tools/bazel/phase15_hardware_evidence.py` and `tools/bazel/phase15_hardware_evidence_test.py` provide the nearest template for a phase-owned evidence contract, deterministic quick mode, external evidence validation, path traversal guard, security/overclaim scan, generated artifacts, Bazel labels, and `just` facade wiring.
- `tools/bazel/phase14_simulator_evidence.py`, `tools/bazel/phase14_simulator_evidence_test.py`, and `tools/bazel/manifests/phase14_simulator_evidence_contract.json` provide the simulator and transfer/WUI scenario contract pattern that Phase 16 should extend into live or controlled-service evidence.
- `tools/bazel/phase13_ci_evidence.py`, `tools/bazel/phase13_ci_evidence_test.py`, and `tools/bazel/manifests/phase13_ci_evidence_contract.json` provide artifact retention, generated manifest, redacted summary, and CI-safe contract models.
- `tools/bazel/manifests/phase11_*.json` identify live-service proof as a cutover blocker and provide proof-scope, retained-code, reference-comparison, and final-demotion taxonomy.
- `tools/bazel/manifests/phase9_*` provide source-backed network, WUI, TLS, transfer, proxy, telemetry, and negative-fixture contracts that Phase 16 should cite instead of rediscovering behavior.
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` already expose phase verifiers through the established Bazel and developer-command pattern.

### Established Patterns

- Checked-in JSON manifests define durable evidence contracts; generated run manifests, log references, normalized outputs, and redacted summaries live under ignored `build/` paths.
- Phase verifiers use explicit constants for required IDs, required fields, source refs, generated output roots, forbidden markers, lifecycle IDs, status values, and wiring strings.
- Prior phases strictly separate local deterministic checks from simulator, hardware, live-service, release, signing, retained-code, and maintainer-review proof.
- Python verifier tests use stdlib `unittest`, temporary roots, explicit fixture writes/copies, and Arrange/Act/Assert comments.
- Network secrets and credential material are already called out as high-risk in codebase concerns; Phase 16 should make redaction a verifier-enforced behavior, not prose guidance.

### Integration Points

- Add Phase 16 live network evidence contract under `tools/bazel/manifests/`.
- Add Phase 16 verifier/collector and tests under `tools/bazel/`.
- Add Bazel labels in `tools/bazel/BUILD.bazel`, root aliases/docs filegroups in `BUILD.bazel`, dispatch cases in `tools/bazel/rust_workflow.sh`, and `just phase16-verify`.
- Use `.planning/phases/16-live-network-and-transfer-qualification/` for research, plan, summary, verification, and lifecycle artifacts.
- Keep generated Phase 16 evidence under `build/ci-evidence/phase16/` or another ignored `build/` subdirectory.

</code_context>

<specifics>
## Specific Ideas

- Maintainers should be able to answer "which service scenario failed, which requirement does it block, which artifact proves it, which credential/input was required, and what residual risk remains" from the generated manifest alone.
- Phase 16 should provide controlled-service or operator-supplied evidence input modes so real Connect/WUI/TLS/transfer runs can be supplied later without changing the contract.
- The local `just phase16-verify` path should validate contracts, generated dry-run artifacts, redaction, overclaim guards, source refs, and wiring, while clearly marking live rows as pending live input when no service artifact is supplied.
- Do not mutate archived v1.0 artifacts. Cite archived evidence and layer Phase 16 live-network proof on top.
- Keep raw crash dumps, unredacted HTTP/TLS logs, raw production payloads, private keys, certificates, tokens, Wi-Fi credentials, PrusaLink passwords, API keys, Connect tokens, registration codes, and sensitive printer identifiers out of committed source and planning artifacts.

</specifics>

<deferred>
## Deferred Ideas

- Release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resources, signing, WUI, ESP, MMU, and auxiliary package proof belongs to Phase 17.
- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.
- Long-run soak dashboards, service-level trend analytics, broader lab automation, and post-cutover network hardening belong to future milestones after the basic Phase 16 evidence contract exists.

</deferred>

---

*Phase: 16-live-network-and-transfer-qualification*
*Context gathered: 2026-06-18*
