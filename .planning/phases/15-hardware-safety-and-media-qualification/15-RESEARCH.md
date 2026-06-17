# Phase 15: Hardware Safety and Media Qualification - Research

**Researched:** 2026-06-17 [VERIFIED: system current date]
**Domain:** Hardware evidence contracts, firmware safety qualification, storage-media qualification, and redacted operator evidence [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
**Confidence:** HIGH for repo-local architecture and verifier patterns; MEDIUM for future lab execution details because physical device availability was not present in this session [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tool availability audit]

<user_constraints>
## User Constraints (from CONTEXT.md)

All bullets in this section are copied from `.planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md` and should be treated as locked planning constraints unless they appear under "the agent's Discretion" or "Deferred Ideas". [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

### Locked Decisions

#### Hardware Qualification Matrix

- **D-01:** Add a Phase 15-owned hardware evidence contract instead of mutating Phase 11, Phase 13, or Phase 14 manifests. The contract should name the required supported printer families, boards, storage media, auxiliary-controller combinations, and cutover requirement IDs covered by each row.
- **D-02:** Use row-level qualification rather than an umbrella hardware pass. Every row should name device/printer family, board, firmware build identity, media or auxiliary surface when applicable, scenario, requirement mapping, artifact path, expected result semantics, operator metadata requirements, and residual risk.
- **D-03:** Cover the roadmap-required families: supported-printer smoke, board startup/readiness, storage media, UI input, MMU, RS485/Modbus, toolchanger/dock/offset, and auxiliary-controller combinations.
- **D-04:** Hardware availability is a first-class status. Rows without physical execution should use explicit statuses such as `pending-hardware-input`, `manual-hardware-required`, or `blocked-hardware-unavailable`, never `passed`.

#### Safety and Fault Evidence

- **D-05:** Safety rows must cover watchdog behavior, thermal safety, motion safety, emergency stop, safe-output behavior, crash recovery, physical UI input, MMU fault handling, RS485/Modbus faults, and toolchanger fault or calibration scenarios.
- **D-06:** The evidence model should distinguish observed physical behavior from source-backed contract checks. Source checks can validate schema, references, redaction, and overclaim guards; only operator-supplied hardware artifacts can satisfy physical safety rows.
- **D-07:** Crash-dump and fault evidence must be redacted or summarized. Do not commit raw crash dumps, RAM dumps, credential regions, printer identifiers that should stay private, Wi-Fi credentials, Connect tokens, certificates, signing keys, or unsafe operational payloads.
- **D-08:** Safety evidence should preserve residual risk. A pass row still records what was not covered, such as long-run soak, environmental extremes, unsupported media, unavailable auxiliary boards, or maintainer approval still owned by Phase 18.

#### Artifact Capture and Redaction

- **D-09:** Generated Phase 15 runtime artifacts should live under an ignored directory such as `build/ci-evidence/phase15`, mirroring the Phase 13 and Phase 14 pattern. Checked-in files define contracts, schemas, verifier logic, and dry-run examples only.
- **D-10:** Generated artifacts should include a machine-readable run manifest, normalized scenario results, redacted hardware summaries, source contract snapshot, and log references. The generated manifest should be useful to maintainers without requiring reruns.
- **D-11:** Operator metadata is required for hardware evidence: device or printer family, board, firmware build, operator identity or role, timestamp, scenario, result, artifact reference, and residual risk.
- **D-12:** Add verifier guards that reject secret markers, raw payload markers, and overclaim wording such as local hardware proof, final cutover completion, release readiness, signing proof, or reference demotion.

#### Runner and Developer Workflow

- **D-13:** Add a dedicated Phase 15 Python verifier/collector using the standard-library pattern from Phase 13 and Phase 14, with deterministic local modes for contract, security, wiring, and dry-run artifact validation.
- **D-14:** Expose Phase 15 through `tools/bazel/phase15_hardware_evidence.py`, `tools/bazel/phase15_hardware_evidence_test.py`, `tools/bazel/manifests/phase15_hardware_evidence_contract.json`, Bazel `phase15_verify` / `phase15_verify_tests` labels, root aliases/docs filegroups, `tools/bazel/rust_workflow.sh`, and `just phase15-verify`.
- **D-15:** Real hardware capture may be a manual/operator JSON input or a command mode that validates supplied evidence files. Local verification should be deterministic and should pass only contract/dry-run validation when hardware inputs are absent.
- **D-16:** Keep the workflow small and auditable: prefer JSON contracts, explicit status vocabularies, path guards, `subprocess.run` without shell execution when commands are needed, and focused stdlib tests over broad firmware build or lab automation rewrites.

#### Traceability and Prior Evidence

- **D-17:** Every Phase 15 row must map to `HARD-01`, `HARD-02`, and/or `HARD-03` plus relevant v1.0/Phase 11 evidence rows. Rows should cite Phase 7 storage/media, Phase 8 UI, Phase 10 auxiliary, Phase 11 parity/cutover, Phase 13 CI, and Phase 14 simulator contracts where applicable.
- **D-18:** Preserve the Phase 14 boundary: simulator-visible proof may support readiness but cannot satisfy physical safety, media, UI input, RS485, MMU, or toolchanger evidence.
- **D-19:** Preserve Phase 13's artifact-retention model. CI may validate the contract and retain generated summaries, but CI without lab hardware does not become hardware proof.
- **D-20:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 15-2026-06-17T22-53-45`.

### the agent's Discretion

- Exact scenario IDs, schema field order, status names, generated artifact file names, helper function boundaries, and dry-run output shape are flexible if the result remains deterministic, source-backed, redacted, traceable, and hard to overclaim.
- The planner may choose one integrated implementation plan or several tasks inside one plan, but the roadmap expects one completed plan for this phase.
- Prefer explicit contracts and verifier tests over prose-only checklists. Operator-facing instructions are useful only when backed by machine-readable artifacts and verifier checks.

### Deferred Ideas (OUT OF SCOPE)

- Live Connect, WUI, TLS, telemetry, proxy, long-transfer, and crash-dump upload evidence belongs to Phase 16.
- Release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resources, signing, WUI, ESP, MMU, and auxiliary package proof belongs to Phase 17.
- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.
- Long-run soak dashboards, trend analytics, broader hardware lab automation, and post-cutover vendor/HAL replacement belong to future milestones after the basic Phase 15 evidence contract exists.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HARD-01 | Maintainer can execute a hardware smoke matrix for supported printer families, boards, storage media, and auxiliary-controller combinations required for cutover readiness. [VERIFIED: .planning/REQUIREMENTS.md] | Use a checked-in Phase 15 contract with row-level printer, board, media, auxiliary, scenario, requirement, source-ref, expected-result, status, artifact, and residual-risk fields. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py] |
| HARD-02 | Maintainer can record hardware safety evidence for watchdog, thermal/motion safety, emergency stop, safe-output, crash recovery, UI input, MMU, RS485, and toolchanger scenarios. [VERIFIED: .planning/REQUIREMENTS.md] | Use Phase 6 safety rows plus Phase 8 UI and Phase 10 auxiliary rows as source-backed contracts, while physical results remain operator-supplied evidence. [VERIFIED: tools/bazel/manifests/phase6_safety_gates.json; VERIFIED: tools/bazel/manifests/phase8_gui_workflows.json; VERIFIED: tools/bazel/manifests/phase10_mmu_transport.json; VERIFIED: tools/bazel/manifests/phase10_modbus_rs485.json; VERIFIED: tools/bazel/manifests/phase10_toolchanger_dock_offsets.json] |
| HARD-03 | Maintainer can review hardware evidence artifacts that identify device, firmware build, operator, timestamp, scenario, result, and residual risk without exposing secrets or unsafe operational data. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse Phase 13/14 redaction, path containment, generated manifest, and overclaim-guard patterns, extended with required operator metadata fields and hardware-specific forbidden markers. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py] |
</phase_requirements>

## Summary

Phase 15 should implement a repo-owned hardware evidence contract plus a Python stdlib verifier/collector, not a prose checklist or a broad lab automation rewrite. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py] The contract should be checked in under `tools/bazel/manifests/phase15_hardware_evidence_contract.json`, while generated dry-run and later operator evidence summaries should stay under ignored `build/ci-evidence/phase15`. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: .gitignore]

The key planning constraint is proof-scope separation: local verification can pass contract completeness, source-reference resolution, security scanning, wiring, and dry-run artifact shape, but it cannot claim physical hardware safety, media, UI input, MMU, RS485, or toolchanger proof without operator-supplied hardware evidence. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: .planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md] This mirrors Phase 14, where quick mode writes artifacts but active scenario rows remain pending real input. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md]

**Primary recommendation:** Build `phase15_hardware_evidence.py` as a contract validator, dry-run artifact writer, optional operator JSON validator, redaction scanner, and Bazel/just wiring checker over a row-level hardware evidence manifest. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py]

## Project Constraints (from AGENTS.md)

- `AGENTS.md` requires reading `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant `standards/` pages before planning, implementation, review, or audit work. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md]
- Bright Builds standards apply with no active local override beyond placeholder rows in `standards-overrides.md`. [VERIFIED: standards-overrides.md]
- The project target is a Big Bang Rust+Bazel replacement preserving supported-printer behavior parity, with Bazel authoritative from the start and `justfile` required for developer workflows. [VERIFIED: AGENTS.md]
- Safety-critical embedded behavior must be validated with tests, hardware-aware review, simulator flows, or explicit evidence before replacement is considered complete. [VERIFIED: AGENTS.md]
- Before repo-changing implementation work, the standards prefer fetching/syncing remote state and using repo-native bootstrap/verification paths when safe; this research did not perform implementation sync because it only creates planning research and the worktree already had a user modification to `.planning/config.json`. [VERIFIED: standards/core/verification.md; VERIFIED: git status --short]
- Changed paths should be verified through repo-native commands before commit, with scope proportional to the change. [VERIFIED: standards/core/verification.md]
- Business logic should use functional-core / imperative-shell structure, parse boundary data early, and make invalid states unrepresentable where practical. [VERIFIED: standards/core/architecture.md]
- New unit tests for pure or business logic must test one concern and clearly delineate Arrange, Act, and Assert unless trivially obvious. [VERIFIED: standards/core/testing.md]
- Code shape guidance prefers early returns, visible `maybe_` names for internal optional values, rerunnable scripts with diagnosable output, and refactoring triggers around long functions or oversized files. [VERIFIED: standards/core/code-shape.md]
- Project skill directories `.claude/skills/` and `.agents/skills/` were not present in this checkout. [VERIFIED: find .claude .agents]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|---|---:|---|---|
| Python stdlib (`argparse`, `json`, `pathlib`, `re`, `shutil`, `subprocess`, `unittest`) | Python 3.14.4 available locally | Implement contract validation, dry-run artifact generation, optional operator JSON validation, redaction scans, and focused tests. | Phase 13 and Phase 14 verifiers already use stdlib Python with no new dependency surface. [VERIFIED: python3 --version; VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py] |
| JSON manifest | n/a | Store the Phase 15 hardware evidence contract and later normalized operator evidence. | Prior phase evidence contracts are checked-in JSON manifests under `tools/bazel/manifests/`. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json; VERIFIED: tools/bazel/manifests/phase14_simulator_evidence_contract.json] |
| Bazel `shell_binary` via existing `tools/bazel/rust_workflow.sh` dispatch | Bazel 9.1.1 available locally | Expose `phase15_verify` and `phase15_verify_tests` labels. | Phase 13 and Phase 14 already use this label and dispatch pattern. [VERIFIED: bazel --version; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh] |
| `just` facade | just 1.48.0 available locally | Expose `just phase15-verify` for maintainers. | The project requires a `justfile`, and Phase 13/14 recipes run tests before verifiers. [VERIFIED: just --version; VERIFIED: AGENTS.md; VERIFIED: justfile] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|---|---:|---|---|
| `jq` | jq-1.7.1-apple available locally | Inspect generated JSON artifacts during manual debugging. | Useful for verification spot checks, but Phase 15 implementation should not require `jq` in Python tests. [VERIFIED: jq --version] |
| Node GSD tooling | Node v24.13.0 available locally | Lifecycle init, commit, and roadmap context tools. | Use for GSD workflow metadata and optional research commit, not for the Phase 15 verifier itself. [VERIFIED: node --version; VERIFIED: gsd init output] |
| Git | git 2.53.0 available locally | Commit planning artifact and inspect diff. | Use only scoped commits so existing user changes such as `.planning/config.json` remain untouched. [VERIFIED: git --version; VERIFIED: git status --short] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Python stdlib verifier | pytest-based verifier | Adds dependency expectations for the verifier itself and diverges from Phase 13/14 stdlib regression pattern. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py; VERIFIED: tools/bazel/phase14_simulator_evidence_test.py] |
| Checked-in JSON contract | Markdown checklist only | Markdown cannot enforce required row fields, source refs, path guards, status vocabulary, or redaction checks. [VERIFIED: tools/bazel/phase14_simulator_evidence.py] |
| Operator JSON input validation | Direct lab automation now | Lab automation would require physical devices that were not available in this session and would exceed the Phase 15 locked decision to keep the workflow small and auditable. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: environment availability audit] |

**Installation:** No new package installation is recommended for Phase 15. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py]

**Version verification:** Tool versions were verified with `python3 --version`, `bazel --version`, `bazelisk version`, `just --version`, `node --version`, `git --version`, and `jq --version`; no npm package versions apply because no npm dependency is recommended. [VERIFIED: tool availability audit]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── phase15_hardware_evidence.py                 # verifier, dry-run writer, optional operator input validator
├── phase15_hardware_evidence_test.py            # stdlib unittest regression suite
├── manifests/
│   └── phase15_hardware_evidence_contract.json  # checked-in hardware evidence contract
├── BUILD.bazel                                  # phase15_verify and phase15_verify_tests labels
└── rust_workflow.sh                             # dispatch cases for the Bazel shell_binary labels

BUILD.bazel                                      # phase15 docs filegroup and root aliases
justfile                                         # phase15-verify recipe
build/ci-evidence/phase15/                       # ignored generated dry-run/operator summaries
```

This structure follows the Phase 14 implementation surface and keeps generated evidence under `/build*`, which is ignored by `.gitignore`. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile; VERIFIED: .gitignore]

### Pattern 1: Phase-Owned Evidence Contract

**What:** Store the row-level hardware evidence matrix in `tools/bazel/manifests/phase15_hardware_evidence_contract.json` with fixed lifecycle metadata, status vocabulary, required artifact kinds, external/operator input model, scenario rows, source refs, and generated output root. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase14_simulator_evidence_contract.json]

**When to use:** Use this for every HARD-01/HARD-02/HARD-03 row instead of editing Phase 11, Phase 13, or Phase 14 manifests. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

**Required top-level fields:** `schema_version`, `id`, `phase`, `phase_lifecycle_id`, `output_root`, `artifact_name`, `status_vocabulary`, `required_artifact_kinds`, `operator_input_schema`, and `scenarios`. [VERIFIED: tools/bazel/manifests/phase14_simulator_evidence_contract.json; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

**Recommended scenario fields:** `id`, `title`, `requirement_ids`, `v1_requirement_ids`, `phase11_source_refs`, `source_contract_refs`, `printer_family`, `board`, `media_surface`, `auxiliary_surface`, `proof_scope`, `expected_pass_semantics`, `expected_failure_semantics`, `expected_artifact_path`, `retained_artifact_kind`, `allowed_statuses`, `operator_metadata_required`, `residual_risk_required`, and `unsupported_claims`. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

Example contract row:

```json
{
  "id": "hard-coreone-xbuddy-emergency-stop-door-open",
  "title": "COREONE xBuddy emergency-stop physical door-open behavior",
  "requirement_ids": ["HARD-02", "HARD-03"],
  "v1_requirement_ids": ["CORE-04"],
  "phase11_source_refs": [
    "tools/bazel/manifests/phase11_requirement_evidence.json#req-core-04",
    "tools/bazel/manifests/phase11_parity_pyramid.json#pyramid-hardware-smoke-manual-gates"
  ],
  "source_contract_refs": [
    "tools/bazel/manifests/phase6_safety_gates.json#motion-safe-output-and-emergency-stop"
  ],
  "printer_family": "COREONE",
  "board": "XBUDDY",
  "proof_scope": "manual-hardware-required",
  "expected_artifact_path": "build/ci-evidence/phase15/logs/hard-coreone-xbuddy-emergency-stop-door-open.log",
  "allowed_statuses": ["passed", "failed", "manual-hardware-required", "pending-hardware-input"],
  "operator_metadata_required": ["device", "firmware_build", "operator", "timestamp", "scenario", "result", "artifact_ref", "residual_risk"],
  "unsupported_claims": ["cutover complete", "reference demotion approved", "release readiness"]
}
```

The example uses existing source-reference resolution conventions from Phase 14 and hardcodes no raw physical result. [VERIFIED: tools/bazel/phase14_simulator_evidence.py]

### Pattern 2: Deterministic Local Modes

**What:** Implement `--contract-only`, `--security-only`, `--wiring-only`, `--quick`, and an optional hardware input mode such as `--operator-evidence <path>`. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

**When to use:** Local `just phase15-verify` should run tests and quick verification without requiring physical hardware, while all physical rows remain `pending-hardware-input` or `manual-hardware-required` unless operator JSON is supplied. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py]

**Implementation rule:** Use `subprocess.run([...], shell=False)` only if Phase 15 needs to call another repo-owned command, and keep command builders returning argument lists so tests can reject `bash -c`, `python -c`, and inline shell logic. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: standards/core/code-shape.md]

### Pattern 3: Operator Evidence as Boundary Data

**What:** Treat hardware evidence files as boundary input parsed into stricter internal dictionaries before status decisions are made. [VERIFIED: standards/core/architecture.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py]

**When to use:** Use this when a maintainer supplies lab evidence after running a printer, storage medium, MMU, RS485, or toolchanger scenario. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

**Required validation:** The verifier should reject evidence input that lacks device/printer family, board, firmware build, operator identity or role, timestamp, scenario ID, result/status, artifact reference, and residual risk. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

### Pattern 4: Source-Ref Resolution Across Phase Manifests

**What:** Reuse the recursive `row_id_exists` / `resolve_source_ref` pattern from Phase 14 so `file.json#row-id` references fail if the row disappears. [VERIFIED: tools/bazel/phase14_simulator_evidence.py]

**When to use:** Use this for all Phase 6 safety, Phase 7 storage, Phase 8 UI, Phase 10 auxiliary, Phase 11 cutover, Phase 13 CI, and Phase 14 simulator references. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase6_safety_gates.json; VERIFIED: tools/bazel/manifests/phase7_storage_media.json; VERIFIED: tools/bazel/manifests/phase8_gui_workflows.json; VERIFIED: tools/bazel/manifests/phase10_auxiliary_controllers.json]

### Anti-Patterns to Avoid

- **Umbrella hardware pass:** One global `hardware passed` flag would hide which printer, board, medium, or auxiliary controller blocks cutover. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
- **Treating dry-run evidence as hardware proof:** Dry-run output proves contract mechanics only and must not change physical rows to `passed`. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py]
- **Committing raw crash dumps or firmware payloads:** Raw dumps and firmware packages can contain sensitive or unsafe operational data and are explicitly outside committed evidence. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md]
- **Inline lab scripts in workflow strings:** Bright Builds code-shape guidance discourages hiding substantial foreign logic in YAML or shell strings. [VERIFIED: standards/core/code-shape.md]

## Recommended Hardware Scenario Rows

| Scenario Family | Minimum Row IDs To Plan | Source Contracts To Cite | Requirement Coverage |
|---|---|---|---|
| Supported-printer smoke matrix | `hard-mini-buddy-startup-ready`, `hard-mk4-xbuddy-startup-ready`, `hard-mk35-xbuddy-startup-ready`, `hard-coreone-xbuddy-startup-ready`, `hard-xl-xlbuddy-startup-ready`, `hard-ix-xbuddy-startup-ready`, `hard-xl-dev-kit-xlb-startup-ready` | `ProjectOptions.cmake`, `utils/presets/presets.json`, `tools/bazel/manifests/phase11_requirement_evidence.json#req-base-01`, `tools/bazel/manifests/phase11_parity_pyramid.json#pyramid-hardware-smoke-manual-gates` | HARD-01, HARD-03 [VERIFIED: ProjectOptions.cmake; VERIFIED: utils/presets/presets.json; VERIFIED: tools/bazel/manifests/phase11_parity_pyramid.json] |
| Board startup/readiness | `hard-board-buddy-startup`, `hard-board-xbuddy-startup`, `hard-board-xlbuddy-startup`, `hard-board-dwarf-startup`, `hard-board-modularbed-startup`, `hard-board-xbuddy-extension-startup` | `ProjectOptions.cmake`, `include/device/board.h`, `tools/bazel/manifests/phase11_retained_code_justifications.json#retained-hal-cmsis-vendor` | HARD-01, HARD-02, HARD-03 [VERIFIED: ProjectOptions.cmake; VERIFIED: include/device/board.h; VERIFIED: tools/bazel/manifests/phase11_retained_code_justifications.json] |
| Storage media | `hard-usb-fatfs-media`, `hard-internal-littlefs-media`, `hard-bbf-littlefs-media`, `hard-eeprom-config-store`, `hard-semihosting-debug-media`, `hard-root-libsysbase-dispatch` | `tools/bazel/manifests/phase7_storage_media.json#filesystem-usb-fatfs`, `#filesystem-internal-littlefs`, `#filesystem-bbf-littlefs`, `#storage-driver-eeprom`, `#filesystem-semihosting`, `#filesystem-root-listing`, `#libsysbase-devoptab-dispatch` | HARD-01, HARD-03 [VERIFIED: tools/bazel/manifests/phase7_storage_media.json] |
| Watchdog and crash recovery | `hard-watchdog-reset-visible`, `hard-crash-dump-redacted-summary`, `hard-power-panic-recovery` | `tools/bazel/manifests/phase6_safety_gates.json#watchdog-and-crash-dump-boundary`, `#power-panic-recovery`, `tools/bazel/manifests/phase8_gui_workflows.json#warning-redscreen-error-surfaces` | HARD-02, HARD-03 [VERIFIED: tools/bazel/manifests/phase6_safety_gates.json; VERIFIED: tools/bazel/manifests/phase8_gui_workflows.json] |
| Thermal and motion safety | `hard-thermal-safety-transition`, `hard-motion-safe-output`, `hard-emergency-stop-coreone` | `tools/bazel/manifests/phase6_safety_gates.json#thermal-safety-transitions`, `#motion-safe-output-and-emergency-stop`, `ProjectOptions.cmake` `HAS_EMERGENCY_STOP` | HARD-02, HARD-03 [VERIFIED: tools/bazel/manifests/phase6_safety_gates.json; VERIFIED: ProjectOptions.cmake] |
| Physical UI input | `hard-ui-knob-navigation`, `hard-ui-touch-input`, `hard-ui-error-screen-input` | `tools/bazel/manifests/phase8_gui_workflows.json#screen-stack-home-bootstrap`, `#menu-settings-and-home-entry`, `#warning-redscreen-error-surfaces`, `tools/bazel/manifests/phase8_display_layouts.json#display-class-selectors` | HARD-01, HARD-02, HARD-03 [VERIFIED: tools/bazel/manifests/phase8_gui_workflows.json; VERIFIED: tools/bazel/manifests/phase8_display_layouts.json] |
| MMU | `hard-mmu-uart-mk4-mk35-coreone`, `hard-mmu-xbuddy-extension-bridge` | `tools/bazel/manifests/phase10_mmu_transport.json#mmu2-uart-transport`, `#mmu2-puppy-modbus-bridge`, `tools/bazel/manifests/phase10_modbus_rs485.json#xbuddy-extension-mmu-read-write-query-command` | HARD-01, HARD-02, HARD-03 [VERIFIED: tools/bazel/manifests/phase10_mmu_transport.json; VERIFIED: tools/bazel/manifests/phase10_modbus_rs485.json; VERIFIED: ProjectOptions.cmake] |
| RS485 / Modbus | `hard-rs485-retry-timeout`, `hard-rs485-flow-control-contention`, `hard-modbus-register-block-limits` | `tools/bazel/manifests/phase10_modbus_rs485.json#puppy-modbus-master-request-retry-timeout`, `#puppy-rs485-flow-control`, `#puppy-modbus-register-block-limits` | HARD-01, HARD-02, HARD-03 [VERIFIED: tools/bazel/manifests/phase10_modbus_rs485.json] |
| Toolchanger / dock / offsets | `hard-xl-toolchanger-dwarf-update-loop`, `hard-xl-dock-identity`, `hard-tool-offset-calibration` | `tools/bazel/manifests/phase10_toolchanger_dock_offsets.json#toolchanger-dwarf-update-loop`, `#toolchanger-dock-identity-dwarf1-6`, `#tool-offset-selftest-flow` | HARD-01, HARD-02, HARD-03 [VERIFIED: tools/bazel/manifests/phase10_toolchanger_dock_offsets.json] |
| Auxiliary controllers | `hard-dwarf-runtime-fifo-loadcell`, `hard-modularbed-bedlet-faults`, `hard-xbuddy-extension-startup-mmu` | `tools/bazel/manifests/phase10_auxiliary_controllers.json#dwarf-runtime-fifo-loadcell-toolhead`, `#modular-bed-runtime-bedlet-faults`, `#xbuddy-extension-runtime-h503-special` | HARD-01, HARD-02, HARD-03 [VERIFIED: tools/bazel/manifests/phase10_auxiliary_controllers.json] |

The exact row IDs may change during planning, but the row families should remain because they correspond directly to Phase 15 locked decisions and the roadmap success criteria. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: roadmap get-phase 15]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Evidence schema validation | A prose-only checklist | Python stdlib validation over a JSON contract | Existing phase verifiers already enforce required fields, source refs, status vocabularies, and path guards. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py] |
| Source traceability | Ad hoc text references | `file.json#row-id` source refs with recursive row lookup | Phase 14 already proves this pattern can fail missing rows deterministically. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence_test.py] |
| Secret and overclaim scanning | Human review only | Existing forbidden-pattern and overclaim regex guard model | Phase 13/14 tests reject `token_value`, private key markers, raw dump markers, and local proof overclaims. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py; VERIFIED: tools/bazel/phase14_simulator_evidence_test.py] |
| Hardware execution status | A single pass/fail status | Explicit row statuses such as `passed`, `failed`, `pending-hardware-input`, `manual-hardware-required`, `blocked-hardware-unavailable` | Locked decisions require hardware availability to be first-class and forbid unavailable rows from passing. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |
| Generated artifact storage | Checked-in runtime logs | Ignored `build/ci-evidence/phase15` output tree | Phase 13/14 use ignored `build/ci-evidence/phase*` output and `.gitignore` ignores `/build*`. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .gitignore] |
| Lab automation | New broad hardware lab framework | Operator JSON validation plus durable evidence contract | Phase 15 scope is evidence qualification and capture, while broad lab automation is deferred. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |

**Key insight:** The hard problem is preventing evidence overclaim and secret leakage, not running local code; the contract must make missing physical evidence visible and reviewable without pretending it passed. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: .planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md]

## Common Pitfalls

### Pitfall 1: Passing Pending Hardware Rows

**What goes wrong:** A dry-run or source-only validation marks physical rows as `passed`. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
**Why it happens:** Contract validation and hardware execution both produce machine-readable artifacts, so the planner may conflate structural validity with physical success. [VERIFIED: tools/bazel/phase14_simulator_evidence.py]
**How to avoid:** In quick mode, mark physical scenarios `pending-hardware-input` or `manual-hardware-required`; only `--operator-evidence` with complete metadata may produce `passed` or `failed`. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
**Warning signs:** Generated summaries contain phrases like `local hardware proof`, `hardware verified locally`, `cutover complete`, or `reference demotion approved`. [VERIFIED: tools/bazel/phase14_simulator_evidence.py]

### Pitfall 2: Raw Crash Dump or Credential Leakage

**What goes wrong:** Crash dumps, RAM regions, Wi-Fi credentials, Connect tokens, certificates, private keys, signing-key values, or private printer identifiers enter committed artifacts. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md]
**Why it happens:** Firmware crash dump flows can capture RAM/CCMRAM, and config storage includes network and service credentials. [VERIFIED: .planning/codebase/CONCERNS.md]
**How to avoid:** Store only redacted summaries, basenames, artifact references, and operator-provided risk notes; reject forbidden markers in contracts and generated artifacts. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py]
**Warning signs:** Artifact text includes `raw_crash_dump`, `firmware_payload`, `token_value`, `password_value`, certificate PEM headers, or full local paths containing secret markers. [VERIFIED: tools/bazel/phase14_simulator_evidence.py]

### Pitfall 3: Source References That Do Not Resolve

**What goes wrong:** A scenario cites a prior evidence row that has been renamed, archived, or never existed. [VERIFIED: tools/bazel/phase14_simulator_evidence_test.py]
**Why it happens:** Several prior manifests use different top-level collection names, so string-only references are easy to mistype. [VERIFIED: tools/bazel/manifests/phase6_safety_gates.json; VERIFIED: tools/bazel/manifests/phase10_modbus_rs485.json]
**How to avoid:** Implement recursive source-ref resolution that searches nested JSON objects for the referenced `id`. [VERIFIED: tools/bazel/phase14_simulator_evidence.py]
**Warning signs:** Contract rows contain paths without `#row-id` fragments or reference only `.planning/ROADMAP.md` as proof. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py]

### Pitfall 4: Matrix Too Narrow For Supported Hardware

**What goes wrong:** The matrix covers only one happy-path printer and misses boards, storage media, MMU, RS485, toolchanger, or auxiliary-controller combinations. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
**Why it happens:** Supported printer presets and board options are split across `ProjectOptions.cmake`, `utils/presets/presets.json`, and source manifests. [VERIFIED: ProjectOptions.cmake; VERIFIED: utils/presets/presets.json]
**How to avoid:** Include all supported printer families `COREONE`, `MINI`, `MK4`, `MK3.5`, `XL`, `iX`, and `XL_DEV_KIT`, and all board families `BUDDY`, `XBUDDY`, `XLBUDDY`, `DWARF`, `MODULARBED`, `XL_DEV_KIT_XLB`, and `XBUDDY_EXTENSION` as either active rows or explicitly not-applicable/pending rows. [VERIFIED: ProjectOptions.cmake; VERIFIED: include/device/board.h]
**Warning signs:** No rows mention `DWARF`, `MODULARBED`, `XBUDDY_EXTENSION`, `XL_DEV_KIT_XLB`, `/usb`, or `HAS_EMERGENCY_STOP`. [VERIFIED: ProjectOptions.cmake; VERIFIED: include/device/board.h; VERIFIED: tools/bazel/manifests/phase7_storage_media.json]

### Pitfall 5: Operator Evidence Without Residual Risk

**What goes wrong:** A pass row omits unavailable media, environmental extremes, long-run soak, unavailable auxiliary boards, or Phase 18 maintainer approval status. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
**Why it happens:** Pass/fail result fields tend to hide what was not tested. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
**How to avoid:** Require `residual_risk` on every operator row, including passed rows. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
**Warning signs:** Operator JSON has `result: "passed"` with no `residual_risk` or `artifact_ref`. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

## Code Examples

### Contract Loader and Source-Ref Check

```python
# Source pattern: tools/bazel/phase14_simulator_evidence.py
def resolve_source_ref(root: Path, source_ref: str, row_name: str) -> None:
    if "#" not in source_ref:
        raise VerificationError(f"{row_name} source ref must use file#row-id: {source_ref}")
    path_text, row_id = source_ref.split("#", 1)
    data = load_json(root, Path(path_text))
    if not row_id_exists(data, row_id):
        raise VerificationError(f"{row_name} source ref row not found: {source_ref}")
```

This pattern is appropriate because Phase 15 must cite Phase 6/7/8/10/11/13/14 evidence rows without mutating them. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

### Quick Mode Status Decision

```python
# Source pattern: tools/bazel/phase14_simulator_evidence.py; adapted for Phase 15.
def scenario_status_for_quick(scenario: dict[str, Any]) -> str:
    if scenario["proof_scope"] == "source-contract":
        return "passed"
    return "pending-hardware-input"
```

Phase 15 quick mode should pass only structural/source-contract rows and preserve physical rows as pending hardware input. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py]

### Operator Evidence Required Fields

```python
# Phase 15 recommendation derived from D-11.
OPERATOR_REQUIRED_FIELDS = [
    "device",
    "board",
    "firmware_build",
    "operator",
    "timestamp",
    "scenario",
    "result",
    "artifact_ref",
    "residual_risk",
]
```

The field list is required by the Phase 15 context and supports HARD-03 reviewability. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: .planning/REQUIREMENTS.md]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| v1.0 local source-backed evidence plus non-local blockers | v1.1 converts CI, simulator, hardware, live-service, release, and review blockers into phase-owned evidence gates | v1.1 requirements defined 2026-06-15 | Phase 15 should execute the hardware/safety/media gate layer rather than recasting v1.0 local evidence as cutover proof. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/STATE.md; VERIFIED: .planning/milestones/v1.0-MILESTONE-AUDIT.md] |
| Phase 11 named hardware smoke/manual gates as blockers | Phase 15 owns row-level hardware matrix and operator evidence capture | Phase 15 context gathered 2026-06-17 | Planning should add a new contract, not mutate archived Phase 11 artifacts. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: .planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md] |
| Phase 13 retained CI evidence artifacts | Phase 15 should retain redacted summaries and manifests under `build/ci-evidence/phase15` | Phase 13 verified 2026-06-16 | CI can validate/retain the contract but cannot become hardware proof without operator input. [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-VERIFICATION.md; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |
| Phase 14 simulator quick mode leaves active rows pending input | Phase 15 quick mode should leave physical rows pending hardware input | Phase 14 verified 2026-06-17 | Local verification remains deterministic without lab hardware and avoids overclaim. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py] |

**Deprecated/outdated:** Treating simulator proof as hardware evidence is explicitly out of scope for Phase 15 planning. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| None | All substantive recommendations in this research are backed by repo files, command probes, or cited official documentation. | All sections | No user confirmation needed for assumed technical facts. [VERIFIED: research source list] |

## Open Questions (RESOLVED)

1. **RESOLVED: Which physical devices and operators are available for later real hardware runs?** [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
   - What we know: Local Phase 15 verification should not require lab hardware and missing rows must remain pending. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
   - RESOLVED: Unknown lab availability is accepted for planning; it must not reduce the contract matrix. The contract must require every supported printer family, board family, and storage-media surface as a row until operator evidence is supplied, with unavailable combinations represented as `pending-hardware-input`, `blocked-hardware-unavailable`, or explicit not-applicable rows that still preserve residual risk. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: ProjectOptions.cmake; VERIFIED: include/device/board.h]
   - Recommendation: Plan a deterministic contract/dry-run implementation first, with `--operator-evidence` validation ready for maintainers to attach later evidence. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

2. **RESOLVED: How granular should storage-media variants be?** [VERIFIED: tools/bazel/manifests/phase7_storage_media.json]
   - What we know: Phase 7 identifies EEPROM/internal flash, USB FatFs, internal littlefs, BBF littlefs, semihosting, root listing, and libsysbase dispatch surfaces. [VERIFIED: tools/bazel/manifests/phase7_storage_media.json]
   - RESOLVED: The checked-in contract must include explicit storage rows for USB FatFs removable media, internal littlefs, BBF littlefs, EEPROM config store, semihosting, and root/libsysbase dispatch when relevant. Specific removable-media brands, capacities, filesystem variants, and degradation cases remain operator metadata and residual risk, not reasons to omit the required storage-surface rows. [VERIFIED: tools/bazel/manifests/phase7_storage_media.json; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
   - Recommendation: Make the contract require a `media_surface` and allow operator-provided `media_identity` metadata without requiring exhaustive brand/capacity enumeration in the checked-in source contract. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

3. **RESOLVED: Should `blocked-hardware-unavailable` be separate from `manual-hardware-required`?** [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
   - What we know: The context explicitly permits `pending-hardware-input`, `manual-hardware-required`, and `blocked-hardware-unavailable`. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
   - RESOLVED: Keep all three statuses with distinct semantics. `manual-hardware-required` means the row is expected to be physically run; `pending-hardware-input` means no operator evidence has been supplied yet; `blocked-hardware-unavailable` means the row is known to be impossible to run in the current lab cycle. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
   - Recommendation: Use all three statuses: `manual-hardware-required` for expected physical rows, `pending-hardware-input` for not-yet-supplied operator evidence, and `blocked-hardware-unavailable` when the row is known to be impossible to run in the current lab cycle. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---:|---|---|
| Python 3 | Phase 15 verifier and tests | yes | 3.14.4 | None needed. [VERIFIED: python3 --version] |
| Bazel | `phase15_verify` / `phase15_verify_tests` labels | yes | 9.1.1 | Use direct `python3` commands if Bazel is temporarily unavailable during development. [VERIFIED: bazel --version] |
| Bazelisk | Bazel launcher compatibility | yes | 9.1.1 output | Use `bazel` directly because it is also available. [VERIFIED: bazelisk version; VERIFIED: bazel --version] |
| just | Developer facade | yes | 1.48.0 | Use `bazel run //tools/bazel:phase15_verify_tests` and `bazel run //tools/bazel:phase15_verify` directly. [VERIFIED: just --version] |
| Node | GSD lifecycle and commit tooling | yes | v24.13.0 | Use existing GSD command path from repo workflow. [VERIFIED: node --version] |
| git | Scoped research commit | yes | 2.53.0 | No fallback needed. [VERIFIED: git --version] |
| jq | Manual JSON inspection | yes | jq-1.7.1-apple | Python `json` module for implementation and tests. [VERIFIED: jq --version] |
| Physical supported printers, boards, media, MMU, RS485, and toolchanger hardware | Real HARD-01/HARD-02 evidence execution | not locally probed | n/a | Keep rows pending and validate operator JSON later. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |

**Missing dependencies with no fallback:**
- Physical lab devices and operator runs are required for real hardware pass claims; local deterministic verification must not replace them. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

**Missing dependencies with fallback:**
- No local hardware inventory is needed to implement the contract and dry-run verifier; pending statuses and `--operator-evidence` validation are the fallback. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | Python stdlib `unittest`, matching Phase 13 and Phase 14 verifier tests. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py; VERIFIED: tools/bazel/phase14_simulator_evidence_test.py] |
| Config file | None for Phase verifier tests; tests run directly through `python3 tools/bazel/phase15_hardware_evidence_test.py`. [VERIFIED: tools/bazel/phase14_simulator_evidence_test.py] |
| Quick run command | `python3 tools/bazel/phase15_hardware_evidence_test.py && python3 tools/bazel/phase15_hardware_evidence.py --quick` [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence_test.py] |
| Full suite command | `just phase15-verify` after Bazel and just wiring exist. [VERIFIED: justfile; VERIFIED: tools/bazel/rust_workflow.sh] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| HARD-01 | Contract contains row-level hardware smoke matrix across supported printer families, boards, storage media, and auxiliary combinations. [VERIFIED: .planning/REQUIREMENTS.md] | unit / contract | `python3 tools/bazel/phase15_hardware_evidence_test.py Phase15HardwareEvidenceTest.test_contract_only_accepts_complete_contract` | no - Wave 0 creates file. [VERIFIED: find tools/bazel] |
| HARD-02 | Contract and verifier preserve physical safety rows for watchdog, thermal/motion safety, emergency stop, safe-output, crash recovery, UI input, MMU, RS485, and toolchanger scenarios. [VERIFIED: .planning/REQUIREMENTS.md] | unit / contract | `python3 tools/bazel/phase15_hardware_evidence.py --contract-only` | no - Wave 0 creates file. [VERIFIED: find tools/bazel] |
| HARD-03 | Generated manifest and operator input validation require device, build, operator, timestamp, scenario, result, artifact, residual risk, and reject secrets/unsafe data. [VERIFIED: .planning/REQUIREMENTS.md] | unit / security | `python3 tools/bazel/phase15_hardware_evidence.py --security-only` | no - Wave 0 creates file. [VERIFIED: find tools/bazel] |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase15_hardware_evidence_test.py` and `python3 tools/bazel/phase15_hardware_evidence.py --quick`. [VERIFIED: tools/bazel/phase14_simulator_evidence_test.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py]
- **Per wave merge:** Run `bazel run //tools/bazel:phase15_verify_tests`, `bazel run //tools/bazel:phase15_verify`, and `git diff --check`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: .planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md]
- **Phase gate:** Run `just phase15-verify`, generated artifact spot checks, security-only scan after quick output, and GSD lifecycle validation before `/gsd-verify-work`. [VERIFIED: justfile; VERIFIED: .planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md]

### Wave 0 Gaps

- [ ] `tools/bazel/phase15_hardware_evidence.py` - implements contract/security/wiring/quick/operator validation for HARD-01/HARD-02/HARD-03. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
- [ ] `tools/bazel/phase15_hardware_evidence_test.py` - covers missing rows, bad source refs, unsupported statuses, path traversal, missing metadata, secret markers, overclaim wording, generated artifacts, and wiring order. [VERIFIED: tools/bazel/phase14_simulator_evidence_test.py]
- [ ] `tools/bazel/manifests/phase15_hardware_evidence_contract.json` - checked-in row-level matrix and source refs. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md]
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 15 labels, aliases, docs filegroup, dispatch, and facade. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]

## Security Domain

OWASP ASVS is a web application and service security verification standard, and the latest stable version identified during research is 5.0.0 dated May 2025; ASVS recommends versioned requirement IDs because identifiers can change. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://github.com/OWASP/ASVS]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | Phase 15 does not add authentication; operator identity is metadata, not auth enforcement. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |
| V3 Session Management | no | Phase 15 does not create sessions or web/API state. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |
| V4 Access Control | no | Phase 15 local verifier reads repo files and optional operator JSON; it does not authorize users. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |
| V5 Input Validation | yes | Parse operator JSON and contract rows at the boundary; reject missing fields, invalid statuses, path traversal, unknown row refs, secret markers, and overclaim wording. [VERIFIED: standards/core/architecture.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py] |
| V6 Cryptography | limited | Do not implement cryptography; reject private keys, certificates, signing-key values, and credential-bearing payloads from evidence artifacts. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/phase13_ci_evidence.py] |

### Known Threat Patterns for Phase 15 Evidence

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Evidence overclaim turns pending hardware into cutover proof | Spoofing / Repudiation | Status vocabulary, unsupported-claim list, and overclaim scanner reject local hardware, release, signing, retained-code, demotion, and cutover claims. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |
| Secret leakage through crash dumps, config values, paths, or logs | Information Disclosure | Store only redacted summaries and artifact references; scan contract and generated files for private key, certificate, token, password, raw dump, and firmware payload markers. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: .planning/codebase/CONCERNS.md] |
| Path traversal writes evidence outside `build/ci-evidence/phase15` | Tampering | Use repo-relative path guards matching `require_repo_relative_under`. [VERIFIED: tools/bazel/phase14_simulator_evidence.py] |
| Inline shell or string-built commands execute unintended code | Elevation of Privilege / Tampering | Prefer no external commands; if needed, build argument lists and call `subprocess.run` without shell execution. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: standards/core/code-shape.md] |
| Malformed operator JSON omits residual risk or artifact reference | Repudiation | Require metadata fields and fail validation before producing passed rows. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md] |

## Sources

### Primary (HIGH Confidence)

- `.planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md` - locked Phase 15 decisions, discretion, deferred scope, lifecycle ID, required files, and implementation surface. [VERIFIED: file read]
- `.planning/REQUIREMENTS.md` - HARD-01, HARD-02, HARD-03 acceptance requirements and v1.1 traceability. [VERIFIED: file read]
- `.planning/STATE.md` - milestone state, prior decisions, and current blockers. [VERIFIED: file read]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, `standards/core/testing.md` - repo and Bright Builds constraints. [VERIFIED: file read]
- `tools/bazel/phase14_simulator_evidence.py`, `tools/bazel/phase14_simulator_evidence_test.py`, `tools/bazel/manifests/phase14_simulator_evidence_contract.json`, `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md` - nearest verifier, test, contract, and boundary template. [VERIFIED: file read]
- `tools/bazel/phase13_ci_evidence.py`, `tools/bazel/phase13_ci_evidence_test.py`, `tools/bazel/manifests/phase13_ci_evidence_contract.json`, `.planning/phases/13-ci-evidence-orchestration/13-VERIFICATION.md` - artifact retention and security scan template. [VERIFIED: file read]
- `tools/bazel/manifests/phase6_safety_gates.json`, `phase7_storage_media.json`, `phase8_gui_workflows.json`, `phase8_display_layouts.json`, `phase10_auxiliary_controllers.json`, `phase10_mmu_transport.json`, `phase10_modbus_rs485.json`, `phase10_toolchanger_dock_offsets.json`, `phase10_auxiliary_build_update.json`, and Phase 11 manifests - source-backed evidence rows Phase 15 should cite. [VERIFIED: file read]
- `ProjectOptions.cmake`, `utils/presets/presets.json`, `include/printers.h`, `include/device/board.h` - supported printer, board, feature, and preset vocabulary. [VERIFIED: file read]
- `.planning/codebase/TESTING.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/CONCERNS.md` - test surfaces, integration surfaces, and security/fragility concerns. [VERIFIED: file read]

### Secondary (MEDIUM Confidence)

- OWASP ASVS official project page and GitHub README - latest stable ASVS version and versioned requirement ID guidance. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://github.com/OWASP/ASVS]

### Tertiary (LOW Confidence)

- None. [VERIFIED: research process]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Phase 13/14 local implementations and tool versions were inspected directly. [VERIFIED: tools/bazel/phase13_ci_evidence.py; VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: tool availability audit]
- Architecture: HIGH - Phase 15 locked decisions and Phase 14 implementation converge on the same contract/verifier/wiring pattern. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: tools/bazel/phase14_simulator_evidence.py]
- Pitfalls: HIGH - Prior verifiers already encode redaction, overclaim, source-ref, path, and proof-scope failure modes. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py; VERIFIED: tools/bazel/phase14_simulator_evidence_test.py]
- Hardware execution details: MEDIUM - required hardware scenario families are source-backed, but physical lab inventory and operator availability were not available in this session. [VERIFIED: .planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md; VERIFIED: environment availability audit]

**Research date:** 2026-06-17 [VERIFIED: system current date]
**Valid until:** 2026-07-17 for repo-local contract patterns; re-check sooner if Phase 13/14 verifier APIs or supported printer/board presets change. [VERIFIED: tools/bazel/phase14_simulator_evidence.py; VERIFIED: ProjectOptions.cmake]
