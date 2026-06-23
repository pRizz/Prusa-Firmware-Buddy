# Phase 24: Hardware, Media, and Safety Evidence Execution - Research

**Researched:** 2026-06-23 [VERIFIED: environment current_date]
**Domain:** Python/Bazel evidence execution wrapper around existing hardware/media/safety contracts [CITED: .planning/ROADMAP.md]
**Confidence:** HIGH [VERIFIED: Phase 15 and Phase 23 verifier/test commands passed locally on 2026-06-23]

<user_constraints>
## User Constraints (from CONTEXT.md) [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)

- Live Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump proof belongs to Phase 25.
- Release/signing/provenance and broad upstream result evidence belongs to Phase 26.
- Retained-code, residual-risk, exception, and final maintainer acceptance decisions belong to Phase 27 and Phase 28.
- Automatic reference demotion remains out of scope unless maintainers explicitly approve it in the final readiness phase.
</user_constraints>

<phase_requirements>
## Phase Requirements [CITED: .planning/REQUIREMENTS.md]

| ID | Description | Research Support |
|----|-------------|------------------|
| EVID-02 | Maintainer can supply real hardware/media/safety evidence for supported printer families, storage media, UI input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output scenarios. | Use the Phase 15 scenario catalog exactly, add Phase 24 v1.2 status normalization, require complete packet coverage, retain redacted summaries and upstream rows, and test failure paths for missing coverage, secret content, and unresolved blockers. [CITED: .planning/REQUIREMENTS.md] [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json] |
</phase_requirements>

## Summary

Implement Phase 24 as a new `phase24_hardware_media_safety_evidence_execution.py` verifier plus `phase24_hardware_media_safety_evidence_execution_contract.json`, not as edits to the Phase 15 contract. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] The wrapper should import and validate the Phase 15 catalog, require all 26 Phase 15 scenario IDs in every real packet, normalize statuses to `passed`, `failed`, `blocked`, or `exception-requested`, and write retained outputs under `build/ci-evidence/phase24`. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json] [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json]

The smallest robust implementation is to mirror Phase 23's v1.2 execution pattern: contract check, security check, wiring check, quick blocked-placeholder generation, real evidence packet validation, retained manifest/normalized/redacted/upstream-row outputs, and focused `unittest` coverage. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py] Phase 15 already verifies source-ref resolution, hardware scenario coverage, operator metadata fields, storage surface coverage, and forbidden content markers, so Phase 24 should call or copy only the necessary local helpers while keeping Phase 15 as the v1.1 source of truth. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: python3 tools/bazel/phase15_hardware_evidence_test.py]

**Primary recommendation:** Build one cohesive Phase 24 wrapper plan that adds the new contract, verifier, tests, Bazel/root aliases, `rust_workflow.sh` cases, and `just phase24-verify`; do not split the phase unless implementation uncovers a real dependency boundary. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: BUILD.bazel, tools/bazel/BUILD.bazel, tools/bazel/rust_workflow.sh, justfile]

## Project Constraints (from AGENTS.md)

- Use repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant standards pages before planning or implementation. [CITED: AGENTS.md] [CITED: AGENTS.bright-builds.md]
- Prefer Bright Builds functional-core/imperative-shell structure: pure decision logic should be separated from file I/O and command-line orchestration. [CITED: standards/core/architecture.md]
- Parse raw boundary data into domain-like validated structures before deeper processing; do not pass unchecked JSON primitives through the verifier. [CITED: standards/core/architecture.md]
- Prefer early returns and guard-style extraction to keep verifier flow shallow. [CITED: standards/core/code-shape.md]
- Unit tests must cover pure/business logic, each unit test should cover one concern, and tests should use Arrange/Act/Assert structure when non-trivial. [CITED: standards/core/testing.md]
- Use repo-owned verification entrypoints where possible, and run relevant verification before completion. [CITED: standards/core/verification.md]
- Python code should use lowercase `snake_case` functions and fixtures; existing evidence scripts under `tools/bazel/` follow this pattern. [CITED: AGENTS.md] [VERIFIED: tools/bazel/phase15_hardware_evidence.py]
- Shell scripts should use `#!/usr/bin/env bash` and `set -euo pipefail`; `tools/bazel/rust_workflow.sh` already follows this pattern. [CITED: AGENTS.md] [VERIFIED: tools/bazel/rust_workflow.sh]
- Generated evidence belongs under ignored build output directories; `.gitignore` ignores `/build*`, so `build/ci-evidence/phase24` will be untracked generated output. [VERIFIED: .gitignore]
- The user explicitly requested no commit for this research task, so do not commit `24-RESEARCH.md`. [CITED: user objective/additional_context]
- No project-local skill directories were found at `.claude/skills/` or `.agents/skills/`. [VERIFIED: find .claude/skills .agents/skills]

## Standard Stack

### Core

| Library / Surface | Version | Purpose | Why Standard |
|-------------------|---------|---------|--------------|
| Python 3 stdlib (`argparse`, `json`, `pathlib`, `re`, `shutil`, `unittest`) | Python 3.14.4 available locally | Implement the verifier and tests without adding dependencies. | Existing Phase 15 and Phase 23 evidence tools use Python stdlib scripts and stdlib `unittest`. [VERIFIED: command output] [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py] |
| Phase 15 hardware evidence contract | schema_version `1` | Canonical hardware/media/safety scenario catalog. | The Phase 15 contract has 26 scenario IDs, required operator fields, required artifact kinds, and storage/safety/auxiliary source refs already validated by the Phase 15 verifier. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json] [VERIFIED: python3 tools/bazel/phase15_hardware_evidence.py --contract-only] |
| Phase 23 simulator evidence execution wrapper | schema_version `1` | Local v1.2 wrapper pattern for real evidence packet validation and retained outputs. | Phase 23 already implements v1.2 status vocabulary, exception metadata, artifact-ref policy, blocked quick placeholders, redacted summaries, and upstream result rows. [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Bazel `shell_binary` via `tools/bazel/rust_workflow.sh` | Bazel 9.1.1 available locally | Provide runnable labels for verifier and verifier tests. | Existing phases expose evidence verification through `tools/bazel/BUILD.bazel` shell targets and root aliases. [VERIFIED: command output] [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] |
| `justfile` facade | just 1.48.0 available locally | Provide the maintainer-facing `just phase24-verify` command. | Existing phase recipes run `phaseXX_verify_tests` before `phaseXX_verify`. [VERIFIED: command output] [VERIFIED: justfile] |

### Supporting

| Library / Surface | Version | Purpose | When to Use |
|-------------------|---------|---------|-------------|
| Phase 18 cutover review contract/verifier | contract schema present in repo | Check downstream upstream-row expectations and hard-blocker semantics. | Use to keep Phase 24 row fields adaptable to final acceptance consumers. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json] [VERIFIED: tools/bazel/phase18_cutover_review.py] |
| Phase 19 aggregate evidence contract/verifier | contract schema present in repo | Understand existing aggregate placeholder behavior for hardware evidence. | Use to preserve the distinction between Phase 15/19 placeholders and Phase 24 real hardware execution. [VERIFIED: tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json] [VERIFIED: tools/bazel/phase19_aggregate_ci_evidence.py] |
| Source manifests from Phases 6, 7, 8, and 10 | JSON manifests in repo | Explain storage, UI, safety, MMU, RS485, toolchanger, and auxiliary source rows. | Use only through Phase 15 source refs unless a test needs to assert a specific source row exists. [VERIFIED: tools/bazel/manifests/phase6_safety_gates.json] [VERIFIED: tools/bazel/manifests/phase7_storage_media.json] [VERIFIED: tools/bazel/manifests/phase8_gui_workflows.json] [VERIFIED: tools/bazel/manifests/phase10_modbus_rs485.json] |
| `jq` | jq-1.7.1-apple available locally | Research-time JSON inspection. | Useful for manual audits, but implementation should use Python stdlib JSON. [VERIFIED: command output] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| New Phase 24 wrapper around Phase 15 | Modify `phase15_hardware_evidence.py` directly | Avoid modifying Phase 15 because the context locks Phase 15 as the v1.1 source contract and Phase 23 proves the wrapper approach. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Phase 23-style packet schema | Reuse Phase 15 `operator_evidence` row list directly | Phase 15 rows only allow `passed`, `failed`, and `blocked-hardware-unavailable`, while Phase 24 requires v1.2 statuses and exception metadata. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] |
| Sanitized refs and summaries | Retain raw logs, firmware images, or crash dumps | Raw payload retention conflicts with the Phase 24 redaction decision and existing secret guards. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |

**Installation:** No new packages are required for the recommended implementation. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

**Version verification:** Recommended external commands were verified locally with `python3 --version`, `bazel --version`, `just --version`, `jq --version`, `git --version`, and `bash --version`; no npm package version checks apply. [VERIFIED: command output]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── phase24_hardware_media_safety_evidence_execution.py        # Phase 24 verifier/writer. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]
├── phase24_hardware_media_safety_evidence_execution_test.py   # Focused unittest coverage. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]
└── manifests/
    └── phase24_hardware_media_safety_evidence_execution_contract.json

build/ci-evidence/phase24/
├── hardware-media-safety-result-manifest.json
├── normalized-hardware-media-safety-results.json
├── redacted-hardware-media-safety-summary.json
├── upstream-hardware-result-row.json
├── operator-evidence-input-template.json
├── contract-snapshots/
└── artifact-summaries/
```

This structure follows the local Phase 23 execution wrapper and the Phase 15/23 evidence-root convention. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] [VERIFIED: tools/bazel/phase15_hardware_evidence.py]

### Pattern 1: Source Contract Import, Not Scenario Redefinition

**What:** Phase 24 should load `phase15_hardware_evidence_contract.json`, validate it with existing Phase 15 semantics, and assert that its required Phase 24 scenario list exactly matches the Phase 15 scenario IDs. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json]

**When to use:** Use this for `--contract-only`, `--quick`, and `--evidence-input` paths before accepting any evidence packet. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

**Example:**

```python
# Source: tools/bazel/phase23_simulator_evidence_execution.py and tools/bazel/phase15_hardware_evidence.py [VERIFIED]
phase15_contract = load_json(root, PHASE15_CONTRACT)
phase15.check_contract(root)
expected_ids = {scenario["id"] for scenario in phase15.contract_scenarios(phase15_contract)}
if set(contract["required_phase15_scenario_ids"]) != expected_ids:
    raise VerificationError("required_phase15_scenario_ids must exactly match Phase 15 scenarios")
```

### Pattern 2: Boundary-Parse the Phase 24 Evidence Packet

**What:** Accept one top-level `hardware_media_safety_evidence_packet` object with packet metadata and a full `scenario_results` list. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] Required packet fields should include `evidence_run_id`, `firmware_identity`, `operator`, `started_at`, `completed_at`, and `scenario_results`, mirroring Phase 23 while adding hardware-specific row requirements. [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json] [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]

**When to use:** Use this for real maintainer-supplied input, not for quick placeholder generation. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

**Recommended scenario row fields:** `scenario_id`, `status`, `source_status`, `status_reason`, `artifact_refs`, `redaction_status`, `source_ref_status`, `device`, `printer_family`, `board`, `firmware_build`, `operator`, `timestamp`, `media_surface`, `auxiliary_surface`, `residual_risk`, `failure_observations`, and optional `exception_request`. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json]

### Pattern 3: Explicit Status Normalization

**What:** Preserve Phase 15 status in `source_status`, but emit only `passed`, `failed`, `blocked`, or `exception-requested` as Phase 24 `status`. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]

**When to use:** Use during both real packet validation and quick placeholder generation. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

**Example:**

```python
# Source: Phase 24 context D-04/D-05 and Phase 15 status vocabulary [CITED/VERIFIED]
def normalize_status(source_status: str, requested_status: str, has_exception: bool) -> str:
    if requested_status not in {"passed", "failed", "blocked", "exception-requested"}:
        raise VerificationError(f"Phase 24 status is invalid: {requested_status}")
    if requested_status == "passed" and source_status in {
        "pending-hardware-input",
        "manual-hardware-required",
        "blocked-hardware-unavailable",
    }:
        raise VerificationError(f"cannot pass with source_status={source_status}")
    if requested_status == "exception-requested" and not has_exception:
        raise VerificationError("exception-requested requires exception_request")
    return requested_status
```

### Pattern 4: Retained Outputs Are Safe, Machine-Readable Summaries

**What:** Write a run manifest, normalized results, redacted summary, upstream row, contract snapshots, and template/input reference under `build/ci-evidence/phase24`. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]

**When to use:** Use after quick placeholder generation or validated real evidence input. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

**Output rule:** Generated rows should include status counts, complete scenario coverage, `real_hardware_evidence_supplied`, artifact refs, residual risks, and unsupported boundary claims. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]

### Pattern 5: Wiring Mirrors Existing Evidence Phases

**What:** Add `phase24_source_ref_manifests`, `phase24_verify`, and `phase24_verify_tests` in `tools/bazel/BUILD.bazel`; add root docs filegroup and aliases in `BUILD.bazel`; add `phase24_verify` and `phase24_verify_tests` cases to `rust_workflow.sh`; add `phase24-verify` to `justfile`. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] [VERIFIED: tools/bazel/rust_workflow.sh] [VERIFIED: justfile]

**When to use:** Use in the same plan as the verifier and tests because existing verifiers check wiring as part of their own contract. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

### Anti-Patterns to Avoid

- **Forking Phase 15 scenario IDs:** This violates the locked context and breaks traceability to the v1.1 contract. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]
- **Counting placeholders as hardware proof:** Phase 15 quick rows default physical rows to `pending-hardware-input`, and Phase 24 quick rows should default to blocked. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]
- **Collapsing storage media into one row:** Phase 15 has separate rows for USB FatFs, internal LittleFS, BBF LittleFS, EEPROM config store, semihosting, and root libsysbase dispatch. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json]
- **Raw artifact retention:** Existing guards reject private keys, certificates, tokens, Wi-Fi credentials, raw dumps, firmware payloads, BBF payloads, DFU payloads, and overclaim phrases. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Hardware/media/safety scenario catalog | A new Phase 24 scenario list with renamed IDs | Import Phase 15 scenario IDs exactly | Phase 15 already contains 26 canonical scenarios and validates supported families, boards, media surfaces, source refs, and required operator metadata. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json] [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| Source-ref traversal | A separate ad hoc lookup algorithm | Reuse or mirror `row_id_exists` and `resolve_source_ref` from Phase 15/23 | Existing verifiers already enforce repo-relative `file#row-id` refs and row existence. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Secret scanning | A new incomplete denylist | Reuse Phase 15/23 forbidden text and forbidden field-name patterns, extending only for Phase 24-specific terms | Existing guards cover keys, certificates, token/password values, Wi-Fi credentials, raw dumps, firmware/BBF/DFU payloads, and overclaim phrases. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Artifact path containment | String prefix checks | Use path parsing and `relative_to`-style root containment | Existing verifiers reject absolute paths and `..` traversal before accepting artifact refs. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Status aggregation | A prose-only summary | Use explicit status counts and deterministic aggregate logic | Phase 23 writes status counts and aggregate status in retained JSON outputs. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Exception metadata | Free-form notes | Require `owner`, `rationale`, `evidence_ref`, and `revisit_condition` | Phase 23 contract and verifier already enforce these exception fields. [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |

**Key insight:** Phase 24's complexity is evidence integrity, not hardware control; the verifier should validate externally supplied sanitized facts and artifact refs, not attempt to drive hardware or parse raw logs. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

## Common Pitfalls

### Pitfall 1: Schema Drift from Phase 15

**What goes wrong:** Phase 24 accepts scenario IDs or fields that do not resolve to Phase 15. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]  
**Why it happens:** A new wrapper can accidentally become a second scenario catalog. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]  
**How to avoid:** Assert exact set equality between Phase 24 `required_phase15_scenario_ids` and Phase 15 `scenarios[].id`. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json]  
**Warning signs:** Tests only check a few representative rows instead of full catalog coverage. [VERIFIED: tools/bazel/phase15_hardware_evidence_test.py]

### Pitfall 2: Pending Hardware Input Becomes a Pass

**What goes wrong:** `pending-hardware-input`, `manual-hardware-required`, or `blocked-hardware-unavailable` is presented as a Phase 24 `passed` result. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]  
**Why it happens:** Phase 15 allowed placeholders for v1.1 gate readiness, while Phase 24 executes real evidence. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [CITED: .planning/PROJECT.md]  
**How to avoid:** Reject `status=passed` when `source_status` is one of the Phase 15 pending/blocking hardware statuses. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]  
**Warning signs:** Quick mode has `real_hardware_evidence_supplied=true` or a passed aggregate status. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]

### Pitfall 3: Missing Rows Hidden by Aggregate Wording

**What goes wrong:** A packet omits one of the 26 Phase 15 scenarios but the summary still says hardware evidence is complete. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json] [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]  
**Why it happens:** Aggregates can be built from present rows only. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]  
**How to avoid:** Use `expected_ids - seen_ids` and fail with a specific missing scenario list. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]  
**Warning signs:** Tests do not remove one scenario and assert failure. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py]

### Pitfall 4: Storage Evidence Loses Media-Specific Risk

**What goes wrong:** USB FatFs, internal LittleFS, BBF/resource image, EEPROM/config store, semihosting, and root libsysbase dispatch are summarized as one storage pass. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]  
**Why it happens:** Storage scenarios share requirement themes but differ by media surface. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json]  
**How to avoid:** Require `media_surface`, `failure_observations`, and `residual_risk` per storage row and preserve scenario IDs in summaries. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]  
**Warning signs:** Summary has `storage: passed` without row-level media surfaces. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json]

### Pitfall 5: Unbounded Artifact References

**What goes wrong:** Evidence input points at absolute paths, `..` traversal, or unrelated build roots. [VERIFIED: tools/bazel/phase15_hardware_evidence_test.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py]  
**Why it happens:** Artifact refs are strings unless parsed and bounded. [CITED: standards/core/architecture.md]  
**How to avoid:** Allow only `build/ci-evidence/phase24/...` and `external://phase24/...` refs, and reject empty ref lists. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]  
**Warning signs:** Tests only check one happy-path ref. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py]

### Pitfall 6: Case-Variant Secret Fields

**What goes wrong:** `Token`, `Private-Key`, or similar mixed-case fields bypass text-only scanning. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py]  
**Why it happens:** JSON key names can carry sensitive payload semantics even when values are redacted. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]  
**How to avoid:** Normalize field names with dash-to-underscore and case-folding before comparing against forbidden field names. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]  
**Warning signs:** Secret tests only scan document text and do not scan nested keys. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py]

### Pitfall 7: Upstream Row Consumer Mismatch

**What goes wrong:** Phase 24 emits an upstream row that future phases cannot adapt to final acceptance. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]  
**Why it happens:** Phase 18 currently models upstream rows from Phase 19 aggregate output, while Phase 23 emits a slimmer v1.2 direct row. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]  
**How to avoid:** Mirror Phase 23's direct v1.2 row and include stable fields that can be adapted later: `criterion_id`, `evidence_family`, `requirement_ids`, `status`, `manifest_ref`, `artifact_refs`, `redaction_status`, `source_ref_status`, `phase`, `phase_lifecycle_id`, and real-evidence boolean. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] [VERIFIED: tools/bazel/phase18_cutover_review.py]  
**Warning signs:** The row lacks `criterion_id=final-hardware-safety-media-evidence` or does not identify hardware evidence family. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json]

## Code Examples

Verified patterns from local sources:

### Complete Scenario Coverage

```python
# Source: tools/bazel/phase23_simulator_evidence_execution.py [VERIFIED]
expected_ids = set(sources)
seen_ids: set[str] = set()
for index, raw_row in enumerate(raw_rows):
    scenario_id = str(raw_row.get("scenario_id", ""))
    if scenario_id not in sources:
        raise VerificationError(f"scenario_results[{index}] does not resolve to a Phase 15 scenario")
    if scenario_id in seen_ids:
        raise VerificationError(f"duplicate scenario result: {scenario_id}")
    seen_ids.add(scenario_id)
missing = sorted(expected_ids - seen_ids)
if missing:
    raise VerificationError("missing scenario results: " + ", ".join(missing))
```

### Artifact Ref Bounds

```python
# Source: tools/bazel/phase23_simulator_evidence_execution.py [VERIFIED]
def validate_artifact_ref(ref: str, row_name: str) -> str:
    if ref.startswith("external://phase24/"):
        if ".." in ref or ref.endswith("/"):
            raise VerificationError(f"{row_name} artifact ref is unsafe: {ref}")
        return ref
    return require_repo_relative_under(ref, Path("build/ci-evidence/phase24"), row_name).as_posix()
```

### Retained Upstream Row

```python
# Source: tools/bazel/phase23_simulator_evidence_execution.py and phase18 upstream row fields [VERIFIED]
upstream_row = {
    "artifact_refs": [
        "build/ci-evidence/phase24/normalized-hardware-media-safety-results.json",
        "build/ci-evidence/phase24/redacted-hardware-media-safety-summary.json",
    ],
    "criterion_id": "final-hardware-safety-media-evidence",
    "evidence_family": "hardware",
    "manifest_ref": "build/ci-evidence/phase24/hardware-media-safety-result-manifest.json",
    "phase": "24-hardware-media-and-safety-evidence-execution",
    "phase_lifecycle_id": "24-2026-06-23T19-52-32",
    "real_hardware_evidence_supplied": real_input_supplied,
    "redaction_status": "passed",
    "requirement_ids": ["EVID-02"],
    "source_ref_status": "passed",
    "status": run_status,
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 15 v1.1 hardware gate can write quick artifacts with physical rows pending. | Phase 24 should execute real evidence packets and normalize every row to v1.2 statuses. | Phase 15 completed 2026-06-18 and Phase 24 is pending in v1.2. [CITED: .planning/ROADMAP.md] | The planner must add a wrapper and tests instead of treating Phase 15 quick output as Phase 24 proof. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| Phase 19 aggregate output retains placeholders for hardware evidence. | Phase 24 should retain direct hardware/media/safety execution outputs under `build/ci-evidence/phase24`. | Phase 19 completed in v1.1 and Phase 24 is the v1.2 hardware execution phase. [CITED: .planning/ROADMAP.md] | The planner must keep Phase 19 placeholder semantics separate from Phase 24 real evidence submission. [VERIFIED: tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json] |
| Phase 18 upstream requirements currently expect Phase 19 aggregate rows for final hardware evidence. | Phase 23 introduced a v1.2 direct evidence upstream row pattern for later phases. | Phase 23 completed 2026-06-23. [CITED: .planning/PROJECT.md] | Phase 24 should mirror Phase 23 and keep enough stable fields for later Phase 26-28 aggregation. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |

**Deprecated/outdated:**
- Treating Phase 15 `pending-hardware-input` as acceptable Phase 24 proof is outdated for v1.2 execution. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: tools/bazel/phase15_hardware_evidence.py]
- Using raw logs, dumps, firmware payloads, certificates, credentials, or keys as retained evidence is disallowed by the Phase 24 decisions and existing guards. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: tools/bazel/phase15_hardware_evidence.py]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The research remains valid until 2026-07-23 unless Phase 25-28 changes upstream result row contracts sooner. [ASSUMED] | Metadata | Planner might rely on stale upstream-row recommendations if later phases change the acceptance contract earlier. |

One planning-horizon estimate is intentionally marked `[ASSUMED]`; all implementation-critical stack, architecture, and pitfall claims are verified from local files, command output, or cited planning context. [VERIFIED: research source audit]

## Open Questions (RESOLVED)

1. **No separate Phase 21 upstream-results manifest is present in this checkout.** [VERIFIED: rg --files tools/bazel/manifests | rg 'phase21|upstream']
   - What we know: Phase 18 contains the current upstream result vocabulary and validation logic. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json] [VERIFIED: tools/bazel/phase18_cutover_review.py]
   - RESOLVED: Phase 24 will use the Phase 23 direct upstream row pattern, with `criterion_id=final-hardware-safety-media-evidence`, `evidence_family=hardware`, and `requirement_ids=["EVID-02"]`. Later Phase 26-28 aggregation can consume that row without changing Phase 24's retained packet contract. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] [VERIFIED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-PLAN.md]
2. **Exact Phase 24 JSON filenames and field names are delegated to implementation.** [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]
   - What we know: Phase 23 output filenames are stable and machine-readable. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]
   - RESOLVED: Phase 24 will use explicit `hardware-media-safety-*` retained filenames and lock them with tests: `hardware-media-safety-result-manifest.json`, `normalized-hardware-media-safety-results.json`, `redacted-hardware-media-safety-summary.json`, `upstream-hardware-media-safety-result-row.json`, and `operator-hardware-media-safety-template.json`. [VERIFIED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-PLAN.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Verifier and `unittest` tests | Yes | 3.14.4 | None needed. [VERIFIED: command output] |
| Bazel | `//tools/bazel:phase24_verify*` labels | Yes | 9.1.1 | Direct `python3` commands can validate locally, but repo workflow should still wire Bazel. [VERIFIED: command output] [VERIFIED: tools/bazel/BUILD.bazel] |
| just | Maintainer facade `just phase24-verify` | Yes | 1.48.0 | Direct `bazel run` commands. [VERIFIED: command output] [VERIFIED: justfile] |
| Bash | `tools/bazel/rust_workflow.sh` shell target dispatch | Yes | GNU bash 3.2.57 | None needed. [VERIFIED: command output] [VERIFIED: tools/bazel/rust_workflow.sh] |
| jq | Research-time JSON inspection | Yes | jq-1.7.1-apple | Python stdlib JSON for implementation. [VERIFIED: command output] |
| git | Diff/status review | Yes | 2.53.0 | None needed. [VERIFIED: command output] |

**Missing dependencies with no fallback:** None found for the recommended Phase 24 implementation path. [VERIFIED: environment audit commands]

**Missing dependencies with fallback:** None found for implementation; `jq` is optional because Python stdlib JSON is enough. [VERIFIED: command output] [VERIFIED: tools/bazel/phase15_hardware_evidence.py]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` via Python 3.14.4. [VERIFIED: command output] |
| Config file | None for these evidence tests; Phase 15 and Phase 23 tests run directly with `python3`. [VERIFIED: python3 tools/bazel/phase15_hardware_evidence_test.py] [VERIFIED: python3 tools/bazel/phase23_simulator_evidence_execution_test.py] |
| Quick run command | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` followed by `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --contract-only`. [VERIFIED: Phase 15/23 test pattern] |
| Full suite command | `just phase24-verify`. [VERIFIED: justfile pattern] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| EVID-02 | Complete Phase 15 scenario coverage is required and missing/duplicate/unknown rows fail. | unit | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` | No - Wave 0 creates file. [VERIFIED: current file listing] |
| EVID-02 | Phase 15 pending/manual/blocked source statuses cannot normalize to Phase 24 pass. | unit | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` | No - Wave 0 creates file. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] |
| EVID-02 | Exception-requested rows require owner, rationale, evidence ref, and revisit condition. | unit | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` | No - Wave 0 creates file. [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json] |
| EVID-02 | Operator metadata fields and residual risk are required for hardware/media/safety rows. | unit | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` | No - Wave 0 creates file. [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json] |
| EVID-02 | Storage evidence preserves media surface, resource/config behavior, failure observations, and residual risk per storage scenario. | unit | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` | No - Wave 0 creates file. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] |
| EVID-02 | Secret fields/text and overclaim phrases are rejected before output retention. | unit/security | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` | No - Wave 0 creates file. [VERIFIED: tools/bazel/phase15_hardware_evidence_test.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py] |
| EVID-02 | Quick mode writes blocked placeholders and does not claim real hardware proof. | unit/smoke | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --quick --output-dir build/ci-evidence/phase24` | No - Wave 0 creates file. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| EVID-02 | Bazel/root/just wiring exists and tests run before verifier in `just phase24-verify`. | wiring | `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --wiring-only` | No - Wave 0 creates file. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` and `python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --contract-only`. [VERIFIED: Phase 15/23 direct test pattern]
- **Per wave merge:** Run `just phase24-verify`. [VERIFIED: justfile pattern]
- **Phase gate:** Run `just phase24-verify` plus direct evidence-input negative fixtures if Bazel output caching obscures local failure reproduction. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json` - declares Phase 24 schema, v1.2 statuses, required Phase 15 IDs, allowed artifact roots, and upstream row identity. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]
- [ ] `tools/bazel/phase24_hardware_media_safety_evidence_execution.py` - implements contract/security/wiring/quick/evidence-input modes. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py]
- [ ] `tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py` - covers EVID-02 behaviors listed above. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]
- [ ] `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring entries. [VERIFIED: existing wiring files]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | No | Phase 24 validates evidence packets and does not authenticate users. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] |
| V3 Session Management | No | Phase 24 has no session model. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] |
| V4 Access Control | Limited | Bound artifact refs to `build/ci-evidence/phase24/` or `external://phase24/` and reject path traversal. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| V5 Input Validation | Yes | Parse JSON into required packet/row fields, validate scenario IDs, statuses, artifact refs, source refs, and exception metadata before output. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| V6 Cryptography | No direct crypto | Never retain keys, certificates, signing material, or firmware payload bytes; this is redaction policy rather than cryptographic processing. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md] [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |

### Known Threat Patterns for Phase 24

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Secret-bearing evidence fields or raw payload markers | Information Disclosure | Reject forbidden field names and forbidden text before writing retained artifacts. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Artifact path traversal | Tampering / Information Disclosure | Require repo-relative refs under the output root or vetted `external://phase24/` refs. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Evidence overclaim wording | Spoofing / Repudiation | Reject phrases that claim local hardware proof, release readiness, maintainer acceptance, final cutover, or reference demotion. [VERIFIED: tools/bazel/phase15_hardware_evidence.py] |
| Missing scenario rows hidden in aggregate status | Repudiation | Enforce exact scenario coverage and write status counts plus explicit missing-row failures. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |
| Redaction or source-ref failure counted as pass | Tampering | Require `redaction_status=passed` and `source_ref_status=passed` for any passed row. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md` - locked Phase 24 decisions, discretion, deferred scope, and canonical refs. [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]
- `.planning/REQUIREMENTS.md` - EVID-02 requirement and v1.2 traceability. [CITED: .planning/REQUIREMENTS.md]
- `.planning/ROADMAP.md` - Phase 24 goal, dependency, success criteria, and milestone sequencing. [CITED: .planning/ROADMAP.md]
- `.planning/PROJECT.md` and `.planning/STATE.md` - milestone posture and prior Phase 23 completion. [CITED: .planning/PROJECT.md] [CITED: .planning/STATE.md]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, `standards/core/testing.md`, and `standards/languages/rust.md` - repo workflow and standards constraints. [CITED: AGENTS.md] [CITED: AGENTS.bright-builds.md]
- `tools/bazel/manifests/phase15_hardware_evidence_contract.json` - canonical Phase 15 scenario catalog and metadata requirements. [VERIFIED: file read]
- `tools/bazel/phase15_hardware_evidence.py` and `tools/bazel/phase15_hardware_evidence_test.py` - existing Phase 15 validation, output, security, and test patterns. [VERIFIED: file read]
- `tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json`, `tools/bazel/phase23_simulator_evidence_execution.py`, and `tools/bazel/phase23_simulator_evidence_execution_test.py` - v1.2 wrapper contract, implementation, and tests. [VERIFIED: file read]
- `tools/bazel/manifests/phase18_cutover_review_contract.json` and `tools/bazel/phase18_cutover_review.py` - current upstream result vocabulary and consumer behavior. [VERIFIED: file read]
- `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json` and `tools/bazel/phase19_aggregate_ci_evidence.py` - aggregate placeholder behavior. [VERIFIED: file read]
- `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - local wiring pattern. [VERIFIED: file read]
- Local command results: Phase 15 contract/wiring checks passed; Phase 23 contract/wiring checks passed; Phase 15 tests ran 21 passing tests; Phase 23 tests ran 13 passing tests. [VERIFIED: command output]

### Secondary (MEDIUM confidence)

- None used; this phase is local-repo constrained and did not require web search. [VERIFIED: research tool log]

### Tertiary (LOW confidence)

- None. [VERIFIED: research source audit]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - existing local Python/Bazel/just evidence patterns are present and verified with direct commands. [VERIFIED: command output]
- Architecture: HIGH - Phase 23 provides the v1.2 wrapper pattern and Phase 15 provides the canonical hardware/media/safety catalog. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py] [VERIFIED: tools/bazel/manifests/phase15_hardware_evidence_contract.json]
- Pitfalls: HIGH - pitfalls map directly to existing regression tests and locked Phase 24 decisions. [VERIFIED: tools/bazel/phase15_hardware_evidence_test.py] [VERIFIED: tools/bazel/phase23_simulator_evidence_execution_test.py] [CITED: .planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md]

**Research date:** 2026-06-23 [VERIFIED: environment current_date]
**Valid until:** 2026-07-23, unless Phase 25-28 changes upstream result row contracts sooner. [ASSUMED]
