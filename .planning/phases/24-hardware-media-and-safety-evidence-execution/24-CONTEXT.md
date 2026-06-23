---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 24-2026-06-23T19-52-32
generated_at: 2026-06-23T19:52:32.454Z
---

# Phase 24: Hardware, Media, and Safety Evidence Execution - Context

**Gathered:** 2026-06-23
**Status:** Ready for planning
**Mode:** Yolo

<domain>
## Phase Boundary

Phase 24 executes the real hardware, storage-media, UI-input, auxiliary, and safety evidence path that v1.1 made contract-ready. It should let maintainers supply, validate, retain, and summarize real hardware evidence packets for supported printer families, storage media, UI input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output scenarios using the Phase 15 hardware evidence contract as the source of truth.

This phase does not redesign the v1.0 parity contracts, does not treat simulator proof as physical hardware proof, does not collect live-service or release/signing evidence, and does not allow final reference demotion. It turns real hardware/media/safety evidence inputs into secret-safe, traceable, machine-readable retained outputs for later cutover acceptance phases.

</domain>

<decisions>
## Implementation Decisions

### Evidence Input Model
- **D-01:** Treat `tools/bazel/manifests/phase15_hardware_evidence_contract.json` as the canonical scenario catalog for Phase 24. The Phase 24 implementation may add a v1.2 result packet/schema around it, but it must not fork, rename, or silently redefine Phase 15 scenario IDs.
- **D-02:** Require every Phase 15 hardware/media/safety scenario to be represented by the real evidence packet. Missing scenarios must remain blocked or failed; aggregate wording cannot hide missing coverage.
- **D-03:** Accept real hardware evidence as sanitized operator metadata plus artifact references, not raw logs, crash dumps, firmware payloads, certificates, credentials, or private data. Device, printer family, board, firmware build, operator, timestamp, scenario status, artifact refs, and residual risk are required fields.

### Status and Acceptance Semantics
- **D-04:** Normalize each Phase 24 scenario to the v1.2 status set required by the roadmap: `passed`, `failed`, `blocked`, or `exception-requested`.
- **D-05:** Preserve Phase 15 source statuses as source context, but do not let `pending-hardware-input`, `manual-hardware-required`, or `blocked-hardware-unavailable` count as a Phase 24 pass. They should normalize to `blocked` unless a maintainer supplies an explicit exception request.
- **D-06:** Keep simulator-only, live-service, release/signing, retained-code, and maintainer-review boundaries visible in retained outputs. Hardware evidence pass status must not claim live Connect/WUI behavior, release readiness, retained-code acceptance, final readiness, or reference demotion approval.

### Hardware Coverage and Residual Risk
- **D-07:** Require scenario rows to name the supported printer family, board, media surface, auxiliary surface, firmware build, operator, timestamp, artifact reference, and residual risk where the Phase 15 contract requires those fields.
- **D-08:** Storage-media evidence must identify media type or filesystem surface, resource/config behavior observed, failure observations, and residual risk. It must not collapse USB FatFs, internal littlefs, BBF/resource image, EEPROM/config store, semihosting, and root devoptab dispatch into one generic storage pass.
- **D-09:** Safety evidence must fail or block when watchdog, crash recovery, thermal, motion, emergency-stop, safe-output, fatal redscreen/BSOD, MMU, RS485, toolchanger, or auxiliary-controller coverage is missing or unresolved.

### Retained Artifacts and Redaction
- **D-10:** Retained Phase 24 outputs should live under `build/ci-evidence/phase24`, following the Phase 23 and Phase 15 evidence-root convention unless planning finds a stronger local pattern.
- **D-11:** Reject private keys, certificates, tokens, Wi-Fi credentials, raw crash dumps, raw RAM dumps, firmware payload bytes, BBF/DFU payloads, and non-local overclaim phrases using the existing Phase 15/18/19/23 guard style.
- **D-12:** Store a normalized scenario summary, redacted hardware/media/safety summary, run manifest, source contract snapshot or contract reference, operator evidence reference, and upstream-consumable result row(s) for later acceptance phases.

### Integration and Verification
- **D-13:** Add Phase 24 verification as a narrow extension around existing Bazel/Python evidence tooling, with root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring consistent with Phases 15, 18, 19, 21, and 23.
- **D-14:** Include focused Python tests for scenario coverage, status normalization, exception metadata, artifact reference bounds, required operator fields, media/safety residual-risk handling, redaction/secret guards, overclaim guards, retained output writing, upstream result rows, and wiring checks.
- **D-15:** Phase 24 verification should pass from checked-in safe fixtures and blocked placeholders, while clearly distinguishing fixture/smoke evidence from real hardware proof.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 24 input template, result manifest, normalized summary, retained artifact summary, and upstream row output, provided they are explicit, documented by tests, and stable for later phases.
- Decide whether to implement Phase 24 as a new `phase24_*` Python verifier, a wrapper around Phase 15 tooling, or both, as long as it avoids schema drift and preserves Phase 15 as the v1.1 source contract.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless the planner finds a real dependency split.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 24 Scope
- `.planning/ROADMAP.md` - Phase 24 goal, success criteria, dependency, and active milestone scope.
- `.planning/REQUIREMENTS.md` - EVID-02 requirement and v1.2 traceability table.
- `.planning/PROJECT.md` - Current milestone posture, non-local evidence constraints, and key decisions about hardware proof and demotion blocking.
- `.planning/phases/23-simulator-evidence-execution/23-CONTEXT.md` - Prior decision that simulator proof stays separate from hardware/media/safety proof.

### v1.1 Hardware Contract
- `tools/bazel/manifests/phase15_hardware_evidence_contract.json` - Canonical hardware/media/safety scenario catalog, source refs, operator metadata requirements, artifact kinds, and unsupported claims.
- `tools/bazel/phase15_hardware_evidence.py` - Existing hardware evidence verifier, quick artifact writer, source contract checks, redaction guards, and no-overclaim checks.
- `tools/bazel/phase15_hardware_evidence_test.py` - Test patterns for contract validation, operator evidence input, negative fixtures, redaction, and wiring.
- `tools/bazel/manifests/phase6_safety_gates.json` - Safety gate source rows for watchdog, thermal, motion, emergency stop, and safe-output boundaries.
- `tools/bazel/manifests/phase7_storage_media.json` - Storage/media source rows for USB, internal flash, resources, EEPROM/config store, semihosting, and root filesystem dispatch.
- `tools/bazel/manifests/phase8_gui_workflows.json` - Local GUI workflow source rows relevant to physical UI-input evidence.
- `tools/bazel/manifests/phase8_display_layouts.json` - Display/input source rows relevant to UI-input hardware proof.
- `tools/bazel/manifests/phase10_auxiliary_controllers.json` - Auxiliary-controller source rows for Dwarf, ModularBed, xBuddy Extension, and puppy runtime evidence.
- `tools/bazel/manifests/phase10_mmu_transport.json` - MMU transport source rows for fault-handling evidence.
- `tools/bazel/manifests/phase10_modbus_rs485.json` - RS485/Modbus source rows for auxiliary fault-handling evidence.
- `tools/bazel/manifests/phase10_toolchanger_dock_offsets.json` - Toolchanger, dock, and offset source rows.
- `tools/bazel/manifests/phase10_auxiliary_build_update.json` - Auxiliary build/update source rows.

### Aggregate and Acceptance Consumers
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - Final review schema, retained-code packets, hardware evidence criterion, residual risk refs, and upstream-result expectations.
- `tools/bazel/phase18_cutover_review.py` - Upstream-result consumption, final-demotion blocking, exception coverage, and redaction/overclaim policy.
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` - Aggregate evidence gate model and external-input placeholders for hardware/media/safety evidence.
- `tools/bazel/phase19_aggregate_ci_evidence.py` - Aggregate evidence retention and external-input placeholder behavior.
- `tools/bazel/manifests/phase21_final_readiness_upstream_results.json` - Upstream-result row model consumed by final readiness.
- `tools/bazel/phase23_simulator_evidence_execution.py` - Current v1.2 execution-phase pattern for wrapping a v1.1 evidence contract with real evidence submission/retention semantics.
- `tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json` - Current v1.2 execution contract pattern and output root conventions.

### Build and Workflow Wiring
- `BUILD.bazel` - Root filegroups and aliases for phase evidence docs and verification labels.
- `tools/bazel/BUILD.bazel` - Evidence verifier targets, data dependencies, and shell binary wiring.
- `tools/bazel/rust_workflow.sh` - Dispatch cases for phase verification commands.
- `justfile` - Developer-facing phase verification recipes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/bazel/phase15_hardware_evidence.py` already validates the Phase 15 hardware/media/safety contract, writes quick placeholder artifacts, validates operator evidence rows, enforces source-ref coverage, and rejects secret or overclaim content.
- `tools/bazel/manifests/phase15_hardware_evidence_contract.json` already names hardware, media, UI-input, safety, MMU, RS485, toolchanger, and auxiliary scenarios plus required operator metadata and expected artifact references.
- `tools/bazel/phase23_simulator_evidence_execution.py` already shows the v1.2 pattern for adding real evidence execution semantics around a v1.1 contract without redefining the source scenario catalog.
- `tools/bazel/phase18_cutover_review.py` and `tools/bazel/phase19_aggregate_ci_evidence.py` already model downstream result consumption, exception coverage, external placeholders, and final demotion blocking.

### Established Patterns
- Phase evidence tools are Python scripts under `tools/bazel/`, with matching `*_test.py` unit tests, manifest JSON under `tools/bazel/manifests/`, Bazel shell targets, root aliases, `rust_workflow.sh` dispatch, and a `just phaseXX-verify` facade.
- Evidence output roots use `build/ci-evidence/phaseXX`, keep generated artifacts out of source control, and retain safe planning/source manifests in the repo.
- Existing verification favors fail-closed schema checks, explicit source refs, repo-relative or `external://phaseXX/` artifact refs, secret redaction, and phrase-based guards against non-local proof overclaims.

### Integration Points
- Phase 24 should add new Bazel/just labels without breaking existing Phase 15, Phase 19, or Phase 23 labels.
- Later v1.2 phases need Phase 24 outputs as upstream-consumable rows or retained references; keep the output schema machine-readable and stable enough for Phase 26-28 to consume.
- `.planning/phases/24-hardware-media-and-safety-evidence-execution/` owns Phase 24 lifecycle artifacts, while generated evidence remains under ignored build output directories.

</code_context>

<specifics>
## Specific Ideas

No user-supplied examples beyond the v1.2 roadmap. Use the v1.1 Phase 15 hardware evidence contract and the Phase 23 evidence-execution wrapper style as concrete models.

</specifics>

<deferred>
## Deferred Ideas

- Live Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump proof belongs to Phase 25.
- Release/signing/provenance and broad upstream result evidence belongs to Phase 26.
- Retained-code, residual-risk, exception, and final maintainer acceptance decisions belong to Phase 27 and Phase 28.
- Automatic reference demotion remains out of scope unless maintainers explicitly approve it in the final readiness phase.

</deferred>

---

*Phase: 24-hardware-media-and-safety-evidence-execution*
*Context gathered: 2026-06-23*
