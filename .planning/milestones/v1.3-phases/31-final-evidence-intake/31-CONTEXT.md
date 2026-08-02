---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 31-2026-07-03T02-04-07
generated_at: 2026-07-03T02:10:15.699Z
---

# Phase 31: Final Evidence Intake - Context

**Gathered:** 2026-07-03
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 31 delivers the final evidence intake surface for sanitized real-run simulator, hardware/media/safety, live-service, and release/signing packets. It should consume the v1.2 evidence machinery, preserve the existing Phase 23-26 schemas and status vocabulary, and create v1.3-owned intake provenance that downstream triage can consume.

Phase 31 does not own blocker triage, retained-code or residual-risk decisions, final readiness, reference-demotion authorization, or the cutover verdict. Those remain Phase 32 through Phase 35 responsibilities.

</domain>

<decisions>
## Implementation Decisions

### Shared Final-Intake Gate
- **D-01:** Build Phase 31 as a shared fail-closed final-intake gate over the existing Phase 23, Phase 24, Phase 25, and Phase 26 contracts. Do not create a new evidence schema, status vocabulary, or proof class unless a real final packet exposes a narrow decision-blocking defect that the existing contract cannot represent.
- **D-02:** Phase 31 may add thin intake receipts or a final intake manifest with v1.3 provenance fields such as submission id, packet hash, operator/release-manager identity reference, timestamp, validator command, validator output refs, and consumed upstream row refs. Receipts must not duplicate stream scenario fields or become a second evidence schema.
- **D-03:** Preserve stream-specific validators as authoritative. The shared gate should call or revalidate through the existing Phase 23-26 scripts instead of reimplementing simulator, hardware, live-service, or release-specific rules.
- **D-04:** Accepted final evidence must retain enough canonical row data for Phase 32 to classify missing, stale, failed, redaction-failed, malformed, blocked, and exception-requested rows without rereading raw secret-bearing payloads.

### Simulator Evidence Intake
- **D-05:** Simulator intake should reuse the unchanged Phase 23 real-input path and require real-run metadata, exact Phase 14 scenario coverage, Phase 23 retained outputs, and the Phase 26-compatible upstream simulator result row.
- **D-06:** If separate Phase 31 simulator provenance is needed, add only a thin receipt over the validated Phase 23 packet. Do not add final-only simulator scenario fields or statuses.

### Hardware, Media, and Safety Evidence Intake
- **D-07:** Hardware/media/safety intake should preserve Phase 24 as the authority for required Phase 15 scenarios, status normalization, storage and safety metadata, artifact refs, secret guards, overclaim guards, retained outputs, and upstream rows.
- **D-08:** Phase 31 can either invoke Phase 24 for raw final packets or register Phase 24 retained outputs, but it must enforce real hardware evidence provenance and reject stale, quick, or placeholder outputs as final proof.

### Live-Service Evidence Intake
- **D-09:** Live-service intake should be a thin wrapper around the Phase 25 evidence-input path, preserving exact Phase 16 scenario coverage for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative protocol, long transfer, and crash-dump flows.
- **D-10:** No local smoke output, quick/default output, manually written prose attestation, or summary-only upstream row should pass as final live-service proof unless the underlying Phase 25 retained packet and manifest are revalidated.

### Release, Signing, and Provenance Evidence Intake
- **D-11:** Release/signing/provenance intake should reuse Phase 26 release/signing/upstream evidence validation and retain sanitized manifests, external refs, digests, redaction/provenance summaries, artifact-reference summaries, and normalized upstream rows.
- **D-12:** Raw private keys, tokens, certificates, service payloads, raw crash dumps, raw release logs, and other secret-bearing material must stay outside retained artifacts. Signing identity and provenance should be represented as references and digests, not copied secret material.

### Sanitization and Non-Final Outputs
- **D-13:** Accepted refs should stay within each stream's allowed local output root or `external://phaseXX/` reference namespace. Phase 31 should preserve `redaction_status`, `source_ref_status`, `exception_status`, `failure_reason`, lifecycle/provenance signals, and artifact-reference summaries.
- **D-14:** Quick/default placeholders, local-only dry-run rows, template rows, and local smoke fixtures are useful for workflow checks but must be marked non-final and rejected as cutover proof.
- **D-15:** A quarantine or rejected-submissions report is acceptable only if names make clear that quarantined rows are not accepted final evidence. Quarantined data must not feed final readiness as proof.

### the agent's Discretion
- The agent may choose the concrete file shape for Phase 31 receipts and aggregate manifests, provided the schema remains a wrapper over Phase 23-26 outputs.
- The agent may choose whether to implement one shared script with stream-specific adapters or a small shared policy module plus a Phase 31 verifier script.
- The agent may choose exact Bazel labels and `just` target names, but they should follow existing phase naming patterns such as `phase23_verify`, `phase24_verify`, `phase25_verify`, and `phase26_verify`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope and Requirements
- `.planning/PROJECT.md` - Milestone v1.3 scope, core constraints, and current project decisions.
- `.planning/REQUIREMENTS.md` - INTAKE-01 through INTAKE-04 and out-of-scope boundaries.
- `.planning/ROADMAP.md` - Phase 31 goal, success criteria, dependencies, and requirement mapping.
- `.planning/STATE.md` - Current milestone state and active blockers/concerns.

### Prior Evidence Machinery
- `.planning/milestones/v1.2-phases/23-simulator-evidence-execution/23-CONTEXT.md` - Simulator execution decisions and Phase 23 scope.
- `.planning/milestones/v1.2-phases/23-simulator-evidence-execution/23-01-SUMMARY.md` - Phase 23 outputs, tests, and verifier wiring.
- `.planning/milestones/v1.2-phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md` - Hardware/media/safety decisions and evidence boundaries.
- `.planning/milestones/v1.2-phases/24-hardware-media-and-safety-evidence-execution/24-01-SUMMARY.md` - Phase 24 outputs, tests, and verifier wiring.
- `.planning/milestones/v1.2-phases/25-live-service-evidence-execution/25-CONTEXT.md` - Live-service decisions and secret/overclaim boundaries.
- `.planning/milestones/v1.2-phases/25-live-service-evidence-execution/25-01-SUMMARY.md` - Phase 25 outputs, tests, and verifier wiring.
- `.planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md` - Release/signing/upstream evidence decisions.
- `.planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md` - Phase 26 outputs, upstream rows, tests, and verifier wiring.
- `.planning/milestones/v1.2-phases/29-upstream-evidence-flow-closure/29-01-SUMMARY.md` - Phase 26 to Phase 28 consumed-row flow and residual risks.
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md` - Final readiness and demotion gate consumption constraints.
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-01-SUMMARY.md` - Phase 28 generated artifacts and fail-closed readiness behavior.

### Active Contracts and Verifiers
- `tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json` - Simulator evidence execution contract.
- `tools/bazel/phase23_simulator_evidence_execution.py` - Phase 23 validator and retained artifact writer.
- `tools/bazel/phase23_simulator_evidence_execution_test.py` - Phase 23 regression coverage.
- `tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json` - Hardware/media/safety evidence execution contract.
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` - Phase 24 validator and retained artifact writer.
- `tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` - Phase 24 regression coverage.
- `tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json` - Live-service evidence execution contract.
- `tools/bazel/phase25_live_service_evidence_execution.py` - Phase 25 validator and retained artifact writer.
- `tools/bazel/phase25_live_service_evidence_execution_test.py` - Phase 25 regression coverage.
- `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` - Release/signing/upstream evidence contract.
- `tools/bazel/phase26_release_signing_upstream_evidence.py` - Phase 26 validator, release evidence writer, and upstream row normalizer.
- `tools/bazel/phase26_release_signing_upstream_evidence_test.py` - Phase 26 regression coverage.
- `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` - Downstream final-readiness consumer contract.
- `tools/bazel/phase28_final_readiness_packet.py` - Final readiness packet generator that Phase 31 outputs must eventually feed through Phase 32-34.
- `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Existing Bazel/root alias and developer workflow wiring patterns.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase23_simulator_evidence_execution.py`: Reuse for simulator packet validation and retained outputs.
- `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`: Reuse for hardware/media/safety packet validation and retained outputs.
- `tools/bazel/phase25_live_service_evidence_execution.py`: Reuse for live-service packet validation and retained outputs.
- `tools/bazel/phase26_release_signing_upstream_evidence.py`: Reuse for release/signing/provenance validation and upstream row handling.
- Existing `tools/bazel/manifests/phase2*_*.json` contracts: Treat as authoritative stream schemas and policy sources.
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile`: Reuse phase verifier/test target wiring patterns.

### Established Patterns
- Evidence phases use Python standard-library verifier scripts plus manifest JSON contracts and script-local regression tests.
- Quick/default mode writes blocked placeholders for workflow smoke checks, while real evidence modes require explicit input packets and retained sanitized outputs.
- Secret and overclaim protection belongs before retained writes.
- Status vocabulary for v1.2 evidence streams is `passed`, `failed`, `blocked`, and `exception-requested`; Phase 31 should not invent additional final statuses.
- Downstream readiness consumes normalized upstream rows, not prose-only reports.

### Integration Points
- Phase 31 outputs should feed Phase 32's blocker register with stream, requirement id, scenario or row id, status, finality, artifact refs, exception state, redaction/source-ref state, and failure reason.
- Phase 31 should preserve compatibility with Phase 26 and Phase 28 upstream row shapes so final readiness can remain result-consuming and fail-closed.
- New tests should cover all INTAKE-01 through INTAKE-04 streams, placeholder rejection, secret rejection, stale or mismatched lifecycle refs, and artifact-ref root enforcement.

</code_context>

<specifics>
## Specific Ideas

- Prefer a single Phase 31 final intake command or verifier that reads stream-specific packets or retained outputs and emits one final intake manifest plus per-stream receipts.
- Use thin receipts to provide v1.3 auditability without duplicating existing stream packet schemas.
- Keep rejected or quarantined submissions visibly separate from accepted final evidence so Phase 32 can triage them without Phase 34 treating them as proof.

</specifics>

<deferred>
## Deferred Ideas

- Blocker register grouping, ownership, severity, next action, and decision impact belong to Phase 32.
- Retained-code, exception, residual-risk, final-readiness, and demotion decisions belong to Phase 33.
- Final readiness packet generation and reference-demotion dry-run behavior belong to Phase 34.
- Cutover verdict publication belongs to Phase 35.
- Broad retained vendor/HAL replacement, new printer behavior, and long-run dashboards remain future milestone work unless Phase 31 reveals a narrow decision-blocking defect.

</deferred>

*Phase: 31-final-evidence-intake*
*Context gathered: 2026-07-03*
