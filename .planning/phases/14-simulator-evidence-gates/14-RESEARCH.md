# Phase 14: Simulator Evidence Gates - Research

**Researched:** 2026-06-17  
**Domain:** Simulator evidence contracts, firmware parity gates, Bazel/just verification workflow  
**Confidence:** HIGH - Phase scope, source evidence, workflow patterns, simulator substrate, and local environment availability were verified from checked-in files and local probes. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: tests/integration/conftest.py] [VERIFIED: local command 2026-06-17]

<user_constraints>
## User Constraints (from CONTEXT.md)

The following locked decisions, discretion areas, and deferred ideas are copied from Phase 14 context. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

### Locked Decisions

### Simulator Proof Scope

- **D-01:** Use a flow-by-flow simulator proof matrix rather than one umbrella simulator pass. Each simulator row should name its scenario, proof scope, `SIM-01`/`SIM-02`/`SIM-03` requirement mapping, source evidence refs, generated artifact path, expected pass/fail semantics, and residual non-simulator gates.
- **D-02:** Cover the roadmap-mandated scenario families: startup and task readiness, watchdog-visible startup behavior, representative G-code execution, GUI navigation, storage/resource access, transfers, and selected failure flows.
- **D-03:** Treat "watchdog-visible startup behavior" as simulator-observable startup/reset/readiness evidence, not physical watchdog timing or safety proof.
- **D-04:** Scenario rows should cite the relevant Phase 11 parity pyramid and reference-comparison rows so simulator proof layers on top of archived v1.0 evidence instead of rewriting it.

### Traceability and Artifact Contract

- **D-05:** Add a Phase 14-owned simulator evidence contract instead of mutating Phase 11 manifests or extending Phase 13's CI contract directly.
- **D-06:** The checked-in contract should mirror the Phase 13 pattern: stable schema, phase lifecycle metadata, status vocabulary, required artifact kinds, gate rows, source evidence refs, and generated output root under `build/ci-evidence/phase14`.
- **D-07:** Generated run artifacts should include a machine-readable run manifest, simulator log references, normalized scenario/result summaries, and redacted evidence summaries. Generated outputs stay ignored under `build/ci-evidence/phase14`.
- **D-08:** Every simulator gate must map to v1.1 requirements (`SIM-01`, `SIM-02`, `SIM-03`) and to relevant v1.0 requirement evidence, reference comparisons, parity-pyramid/cutover criteria, or retained-code rows.

### Runner and Developer Workflow

- **D-09:** Add a dedicated Phase 14 Python runner/verifier over existing simulator and pytest surfaces rather than a thin local-only wrapper or a broad Phase 13 retrofit.
- **D-10:** Expose Phase 14 through `tools/bazel/phase14_simulator_evidence.py`, `tools/bazel/phase14_simulator_evidence_test.py`, `tools/bazel/manifests/phase14_simulator_evidence_contract.json`, Bazel `phase14_verify` / `phase14_verify_tests` labels, and `just phase14-verify`.
- **D-11:** Prefer a deterministic dry-run/contract verification mode for local phase verification, with real simulator execution represented as a required runnable command and artifact contract when local Mini404/QEMU firmware inputs are unavailable.
- **D-12:** Keep existing `tests/integration/` and `utils/simulator/` as the simulator execution substrate; do not force full Bazel-native simulator tests in this phase unless the planner finds an existing hermetic path.

### Overclaim and Safety Boundaries

- **D-13:** Verifier guards must reject simulator rows or generated summaries that claim hardware proof, live service proof, release-candidate proof, signing proof, retained-code maintainer acceptance, final reference demotion, or cutover completion.
- **D-14:** Hardware-only scenarios should be represented with explicit residual statuses or classifications such as `manual-hardware-required`, `pending-hardware`, `pending-live-service`, `pending-release`, or `pending-review`, not as simulator passes.
- **D-15:** Evidence artifacts must remain secret-safe: no raw crash dumps, private certificates, signing keys, Connect tokens, Wi-Fi credentials, credential values, or firmware packages should be committed.
- **D-16:** Phase 14 may update the Phase 13 CI evidence surface only as a separate integration point if needed; simulator proof ownership stays in Phase 14 artifacts and lifecycle metadata.

### the agent's Discretion

- Exact simulator scenario IDs, artifact file names, schema field order, status vocabulary names, dry-run output shape, and verifier helper boundaries are flexible if the result remains deterministic, source-backed, traceable, redacted, and hard to overclaim.
- The planner may choose whether Phase 14 has one integrated plan or multiple sub-tasks inside one plan, but the roadmap expects one completed plan for this phase.
- Prefer standard-library Python, JSON manifests, small verifier helpers, Bazel/just wiring, and concise generated summaries over broad simulator framework rewrites.

### Deferred Ideas (OUT OF SCOPE)

- Physical hardware smoke, thermal/motion safety, emergency stop, safe-output, physical UI input, physical storage media, MMU, RS485, and toolchanger evidence belongs to Phase 15.
- Live Connect, WUI, TLS, telemetry, proxy, long-transfer, and crash-dump upload evidence belongs to Phase 16.
- Release-candidate `.bin`, `.bbf`, `.dfu`, map/provenance, resources, signing, WUI, ESP, MMU, and auxiliary package proof belongs to Phase 17.
- Retained-code maintainer acceptance and final reference-demotion approval belongs to Phase 18.
- Fully hermetic Bazel-native simulator test targets can be revisited after Phase 14 establishes the runner and evidence contract.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SIM-01 | Run simulator evidence flows for startup, task readiness, watchdog-visible startup behavior, and representative G-code execution against the Rust+Bazel evidence surface. [VERIFIED: .planning/REQUIREMENTS.md] | Use Phase 14 scenario rows for startup/bootstrap readiness, task readiness, simulator-observable watchdog/reset readiness, and file-print/G-code telemetry; cite `CORE-01`, `CORE-02`, `CORE-03`, and `BASE-04` source evidence without claiming hardware watchdog proof. [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] [VERIFIED: tests/integration/actions/utils.py] [VERIFIED: tests/integration/test_prusa_link.py] |
| SIM-02 | Run simulator flows for GUI navigation, storage/resource access, transfers, and selected failure flows with reference-compatible pass/fail semantics. [VERIFIED: .planning/REQUIREMENTS.md] | Use scenario rows over existing pytest simulator flows for file browser, PrusaLink file listing/deletion/conflict/unauthorized upload, and selected non-skipped thermal failure tests; skipped transfer nodes must remain residual or pending, not passed. [VERIFIED: tests/integration/test_basic_examples.py] [VERIFIED: tests/integration/test_prusa_link.py] [VERIFIED: tests/integration/test_safety.py] |
| SIM-03 | Map simulator evidence back to v1.0 requirement IDs and cutover criteria without marking hardware-only behavior simulator-proven. [VERIFIED: .planning/REQUIREMENTS.md] | Add contract-required mappings to Phase 11 parity-pyramid, requirement-evidence, reference-comparison, and cutover-readiness IDs; preserve residual statuses for hardware, live service, release, retained-code, and final demotion gates. [VERIFIED: tools/bazel/manifests/phase11_parity_pyramid.json] [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json] [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json] |
</phase_requirements>

## Summary

Phase 14 should be planned as a Phase-14-owned evidence contract and Python verifier/runner that layers simulator proof on top of archived v1.0 evidence instead of mutating Phase 11 or Phase 13 artifacts. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] The closest implementation template is Phase 13: a checked-in JSON contract, a standard-library Python verifier, generated ignored artifacts under `build/ci-evidence/<phase>`, regression tests, Bazel labels, workflow dispatch, and a `just` facade. [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json] [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: justfile]

The simulator substrate already exists through `tests/integration/`, `tests/integration/conftest.py`, and `utils/simulator/simulator.py`. [VERIFIED: tests/integration/README.md] [VERIFIED: tests/integration/conftest.py] [VERIFIED: utils/simulator/simulator.py] Existing tests cover representative startup/UI readiness, file browser, selected thermal failure behavior, PrusaLink API status/list/delete/conflict/unauthorized upload, and print telemetry from `box.gcode`; some upload/download/thumbnail flows are explicitly skipped and must not be counted as passed evidence. [VERIFIED: tests/integration/test_basic_examples.py] [VERIFIED: tests/integration/test_safety.py] [VERIFIED: tests/integration/test_prusa_link.py]

Local verification should default to deterministic contract/dry-run behavior because this checkout currently has Python, Bazel, and `just`, but does not have active pytest dependencies, the Mini404 `qemu-system-buddy` binary, or a runnable firmware image under `build/`. [VERIFIED: local command 2026-06-17] The real simulator command should still be represented in the contract and runner so maintainers can supply firmware and simulator inputs when available. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**Primary recommendation:** Implement `tools/bazel/phase14_simulator_evidence.py`, `tools/bazel/phase14_simulator_evidence_test.py`, and `tools/bazel/manifests/phase14_simulator_evidence_contract.json` by mirroring Phase 13 verifier architecture while sourcing scenario rows from Phase 11 evidence and existing simulator pytest nodes. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json]

## Project Constraints (from AGENTS.md)

- The project is a Rust+Bazel firmware replacement effort where the existing C/C++/CMake firmware remains the behavioral reference implementation. [VERIFIED: AGENTS.md]
- Big Bang migration, behavior parity, Bazel Primary Now, a required `justfile`, Bright Builds standards, and explicit safety evidence constraints apply to planning and implementation. [VERIFIED: AGENTS.md]
- Phase 14 must preserve hardware-aware review boundaries: simulator evidence can contribute proof, but safety-critical replacement is not complete without appropriate tests, hardware-aware review, simulator flows, or explicit evidence. [VERIFIED: AGENTS.md] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]
- Bright Builds routing required this research to load `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant `standards/` pages before planning recommendations. [VERIFIED: AGENTS.md] [VERIFIED: AGENTS.bright-builds.md]
- No active Bright Builds local override was found in `standards-overrides.md`; the placeholder table states no active override. [VERIFIED: standards-overrides.md]
- Architecture guidance favors functional-core/imperative-shell structure, parsing and validation at boundaries, and making invalid states difficult to represent. [VERIFIED: standards/core/architecture.md]
- Code-shape guidance favors early returns, small focused functions, visible absence naming such as `maybe_` where practical, and standard library over dependencies when reasonable. [VERIFIED: standards/core/code-shape.md]
- Testing guidance expects one concern per unit test and Arrange/Act/Assert structure when it improves clarity. [VERIFIED: standards/core/testing.md]
- Verification guidance requires evidence before marking work done and warns against hidden failures. [VERIFIED: standards/core/verification.md]
- Rust standards apply if Rust files are added or changed, but the Phase 14 context recommends standard-library Python and JSON manifests for this phase. [VERIFIED: standards/languages/rust.md] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]
- No project-local `.claude/skills/` or `.agents/skills/` directory was found during research. [VERIFIED: local command 2026-06-17]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python stdlib | Python 3.14.4 available locally; repo bootstrap requires Python 3.8+. [VERIFIED: local command 2026-06-17] [VERIFIED: utils/bootstrap.py] | Contract verification, JSON parsing, subprocess execution, artifact writing, redaction, and unit tests. [VERIFIED: tools/bazel/phase13_ci_evidence.py] | Phase 13 already uses stdlib Python for evidence contracts and tests, and Phase 14 context explicitly prefers standard-library Python. [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| JSON manifests | Existing schema style in Phase 11 and Phase 13 manifests. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json] [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] | Checked-in contract describing scenario gates, status vocabulary, required artifacts, output root, lifecycle, source refs, and residual proof boundaries. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Prior phase evidence is already represented as durable JSON contracts and manifests. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json] [VERIFIED: tools/bazel/manifests/phase11_parity_pyramid.json] |
| Bazel shell labels | Bazel 9.1.1 available locally. [VERIFIED: local command 2026-06-17] | `phase14_verify` and `phase14_verify_tests` labels in `tools/bazel/BUILD.bazel`, plus root aliases/filegroups. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/BUILD.bazel] | Existing phase verifier entrypoints use Bazel labels and `tools/bazel/rust_workflow.sh` dispatch. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: tools/bazel/rust_workflow.sh] |
| `just` facade | just 1.48.0 available locally. [VERIFIED: local command 2026-06-17] | Developer-facing `just phase14-verify` command. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | The repo requires `justfile` workflows and already exposes phase verifier recipes. [VERIFIED: AGENTS.md] [VERIFIED: justfile] |
| Existing simulator pytest substrate | Pytest is declared as `pytest~=7.3.2`; active Python environment is missing pytest. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | Real simulator execution using `tests/integration` node IDs, Mini404/QEMU, firmware input, screen/OCR helpers, WUI, and storage fixtures. [VERIFIED: tests/integration/README.md] [VERIFIED: tests/integration/conftest.py] | Phase 14 context requires existing `tests/integration/` and `utils/simulator/` as the substrate. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| Mini404 / `qemu-system-buddy` | Bootstrap downloads Mini404 0.9.10; binary is missing locally. [VERIFIED: utils/bootstrap.py] [VERIFIED: local command 2026-06-17] | Run real firmware simulator scenarios. [VERIFIED: tests/integration/conftest.py] [VERIFIED: utils/simulator/simulator.py] | Use only in real simulator mode when firmware and simulator binary are available; dry-run mode should not require it. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| EasyOCR | `easyocr~=1.7` in requirements; active environment is missing it. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | Screen text detection for simulator UI readiness and navigation helpers. [VERIFIED: tests/integration/actions/screen.py] | Use through existing pytest helpers, not directly in the Phase 14 contract verifier. [VERIFIED: tests/integration/actions/screen.py] |
| aiohttp / requests | `aiohttp~=3.8` and `requests==2.32.3` in requirements; active environment is missing them. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | PrusaLink/WUI client flows and bootstrap downloads. [VERIFIED: tests/integration/test_prusa_link.py] [VERIFIED: utils/bootstrap.py] | Use through existing integration tests and bootstrap only. [VERIFIED: tests/integration/test_prusa_link.py] |
| littlefs-python / Pillow | `littlefs-python==0.8` and `pillow~=10.4` in requirements; active environment is missing them. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | Existing integration and resource/storage tooling dependencies. [VERIFIED: requirements.txt] | Treat as real-simulator prerequisites, not Phase 14 verifier dependencies. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Phase-14-owned contract | Mutate Phase 11 manifests | Rejected by locked decision D-05 because Phase 14 must layer evidence on top of archived v1.0 artifacts instead of rewriting them. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| Standard-library Python verifier | New simulator framework or broad pytest plugin | Rejected by locked decisions D-09 and D-12; the phase should use a dedicated runner/verifier over existing simulator and pytest surfaces. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| Deterministic dry-run plus optional real simulator mode | Require local Mini404, pytest deps, and firmware image for phase verification | Rejected by locked decision D-11 because local Mini404/QEMU firmware inputs may be unavailable and the phase still needs deterministic verification. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: local command 2026-06-17] |
| Existing `simulator-parity` label only | Wrap `pytest tests/integration --firmware <firmware.bin>` | Insufficient because the existing script only prints or executes a generic command and does not provide Phase 14 traceability, residual statuses, redaction, or scenario-by-scenario mapping. [VERIFIED: tools/bazel/reference_contract.sh] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |

**Installation:** No new package installation should be planned for deterministic Phase 14 verification; real simulator execution should use existing bootstrap and requirements. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: requirements.txt] [VERIFIED: utils/bootstrap.py]

```bash
python3 utils/bootstrap.py
pytest tests/integration --firmware <firmware.bin>
```

**Version verification:** Package and tool versions were verified from repo requirements, bootstrap configuration, and local command probes rather than external registries because Phase 14 should not add new third-party dependencies. [VERIFIED: requirements.txt] [VERIFIED: utils/bootstrap.py] [VERIFIED: local command 2026-06-17]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── phase14_simulator_evidence.py          # stdlib verifier, dry-run writer, optional simulator runner
├── phase14_simulator_evidence_test.py     # unittest regression tests for contract, artifacts, wiring, redaction, overclaim guards
├── manifests/
│   └── phase14_simulator_evidence_contract.json
├── BUILD.bazel                            # phase14_verify and phase14_verify_tests labels
└── rust_workflow.sh                       # dispatch cases for the new phase labels

BUILD.bazel                                # root filegroup/aliases for Phase 14 evidence tooling
justfile                                   # phase14-verify recipe
build/ci-evidence/phase14/                 # ignored generated run manifest, logs, summaries, redacted evidence
```

This structure mirrors existing phase verifier and artifact patterns while keeping generated evidence under ignored `build/` paths. [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: .gitignore] [VERIFIED: justfile]

### Pattern 1: Checked-In Contract, Generated Evidence

**What:** Put durable scenario definitions, allowed statuses, required artifact kinds, output root, lifecycle metadata, and source refs in `tools/bazel/manifests/phase14_simulator_evidence_contract.json`; write run-specific evidence under `build/ci-evidence/phase14`. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json]

**When to use:** Use this pattern for every Phase 14 simulator scenario because maintainers need reviewable evidence without treating generated local output as source. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**Example contract fields:** [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json] [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json]

```json
{
  "schema_version": 1,
  "phase": 14,
  "phase_lifecycle_id": "14-2026-06-17T16-11-34",
  "output_root": "build/ci-evidence/phase14",
  "status_vocabulary": [
    "passed",
    "failed",
    "skipped",
    "pending-simulator-input",
    "pending-simulator-dependency",
    "manual-hardware-required",
    "pending-hardware",
    "pending-live-service",
    "pending-release",
    "pending-review"
  ],
  "required_artifact_kinds": [
    "machine-readable-run-manifest",
    "simulator-log-reference",
    "normalized-scenario-summary",
    "redacted-evidence-summary",
    "contract-snapshot"
  ],
  "scenarios": []
}
```

### Pattern 2: Functional Core, Imperative Shell

**What:** Keep JSON loading, schema validation, status classification, source-ref validation, redaction checks, and normalized summary creation in pure helper functions; keep filesystem writes and optional pytest subprocess execution in a narrow shell. [VERIFIED: standards/core/architecture.md] [VERIFIED: tools/bazel/phase13_ci_evidence.py]

**When to use:** Use this pattern for the runner/verifier so tests can validate failure modes without invoking Mini404/QEMU or writing outside a temporary root. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**Example:** [VERIFIED: tools/bazel/phase13_ci_evidence.py]

```python
def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_statuses(contract: dict[str, object]) -> list[str]:
    errors: list[str] = []
    allowed = set(contract.get("status_vocabulary", []))
    for scenario in contract.get("scenarios", []):
        for status in scenario.get("allowed_statuses", []):
            if status not in allowed:
                errors.append(f"{scenario.get('id')}: unsupported status {status}")
    return errors
```

### Pattern 3: Scenario Rows with Source Evidence and Residual Gates

**What:** Each row should name one scenario family, v1.1 requirement IDs, v1.0 requirement IDs, Phase 11 source rows, pytest node IDs or dry-run command, pass/fail semantics, artifacts, residual non-simulator gates, and hardware-only classification. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json]

**When to use:** Use this for all simulator proof so maintainers can answer which scenario failed, which requirement it blocks, which artifact supports it, and which later phase still owns non-simulator proof. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**Recommended scenario rows:** [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] [VERIFIED: tests/integration/test_prusa_link.py]

| Scenario ID | SIM IDs | v1.0 refs | Existing evidence substrate | Residual classification |
|-------------|---------|-----------|-----------------------------|-------------------------|
| `sim-startup-bootstrap-ready` | SIM-01 | `CORE-01`, `CORE-02` | `wait_for_bootstrap` waits for simulator screen readiness cues. [VERIFIED: tests/integration/actions/utils.py] | Physical startup timing and hardware reset proof remain pending hardware. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| `sim-task-readiness-home-wui` | SIM-01 | `CORE-02`, `IFCE-03` | Home screen readiness and PrusaLink `/api/printer` idle/status flows. [VERIFIED: tests/integration/actions/utils.py] [VERIFIED: tests/integration/test_prusa_link.py] | Hardware task scheduling and real network readiness remain non-simulator proof. [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] |
| `sim-watchdog-visible-startup-reset` | SIM-01 | `BASE-04`, `CORE-01`, `CORE-04` | Simulator-observable startup/reset/readiness/log evidence only. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Physical watchdog timing and safety are manual hardware gates. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| `sim-gcode-file-print-telemetry` | SIM-01 | `CORE-03`, `VERF-03` | `test_printing_telemetry` starts `box.gcode` and checks printing telemetry. [VERIFIED: tests/integration/test_prusa_link.py] | Full print quality, motion, and thermal hardware behavior remain pending hardware. [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] |
| `sim-gui-filebrowser-navigation` | SIM-02 | `IFCE-01`, `ref-ui-display-state-fixtures` | `test_filebrowser_shows_files` enters file browser and observes known file. [VERIFIED: tests/integration/test_basic_examples.py] [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json] | Physical UI input/display proof remains pending hardware. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| `sim-storage-resource-wui-list-delete` | SIM-02 | `IFCE-03`, `IFCE-04`, `ref-storage-migrations` | PrusaLink file list and delete scenarios cover storage/resource access over simulator-backed flash. [VERIFIED: tests/integration/test_prusa_link.py] [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json] | Physical USB/media timing and failure behavior remain hardware-only. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| `sim-transfer-negative-and-conflict` | SIM-02 | `IFCE-02`, `IFCE-03` | Unauthorized upload and delete-while-printing conflict scenarios are non-skipped transfer/error flows. [VERIFIED: tests/integration/test_prusa_link.py] | Skipped successful upload/download/thumbnail transfer flows remain pending, not passed. [VERIFIED: tests/integration/test_prusa_link.py] |
| `sim-selected-thermal-failures` | SIM-02 | `CORE-04`, `VERF-05` | Non-skipped `test_safety.py` min/max/runaway/preheat failure flows provide selected simulator-visible failure evidence. [VERIFIED: tests/integration/test_safety.py] | Hardware thermal and motion safety remain manual hardware gates. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| `sim-traceability-non-simulator-boundaries` | SIM-03 | `VERF-01`, `VERF-03`, `VERF-05`, cutover readiness rows | Contract-only row validates source refs and residual statuses. [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json] | Final reference demotion, release, retained-code, live service, and hardware gates remain pending. [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json] |

### Anti-Patterns to Avoid

- **Umbrella simulator pass:** A single pass/fail bit loses scenario, artifact, requirement, and residual-gate traceability required by D-01. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]
- **Counting skipped pytest nodes as evidence:** `test_prusa_link.py` has skipped upload/download/thumbnail flows, so the runner must preserve them as skipped or pending instead of passed. [VERIFIED: tests/integration/test_prusa_link.py]
- **Claiming physical watchdog or safety proof from simulator logs:** D-03 and D-13 explicitly prohibit treating simulator-observable startup/reset behavior as hardware watchdog timing or safety proof. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]
- **Embedding raw firmware, raw crash dumps, or credentials in artifacts:** D-15 prohibits those artifact classes, and Phase 11/13 verifiers already scan for secret and overclaim markers. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: tools/bazel/phase13_ci_evidence.py]
- **Retrofitting Phase 13 as simulator ownership:** D-16 allows a separate integration point only if needed; Phase 14 artifacts and lifecycle metadata own simulator proof. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Simulator process control | A new QEMU/Mini404 launcher | Existing `utils/simulator/simulator.py` and pytest fixtures. [VERIFIED: utils/simulator/simulator.py] [VERIFIED: tests/integration/conftest.py] | The existing wrapper already handles machine type, kernel, scriptio, pflash, xflash, USB storage, HTTP forwarding, and graphical/headless options. [VERIFIED: utils/simulator/simulator.py] |
| Screen/OCR readiness | New screenshot/OCR polling logic in Phase 14 | Existing `tests/integration/actions/screen.py` and `wait_for_bootstrap`. [VERIFIED: tests/integration/actions/screen.py] [VERIFIED: tests/integration/actions/utils.py] | Existing helpers already poll screenshots, extract OCR text, and handle bootstrap menu paths. [VERIFIED: tests/integration/actions/screen.py] [VERIFIED: tests/integration/actions/utils.py] |
| PrusaLink/WUI client flows | New HTTP client suite | Existing `tests/integration/test_prusa_link.py` scenarios. [VERIFIED: tests/integration/test_prusa_link.py] | Existing tests already exercise root/auth/version/printer/job/list/delete/conflict/unauthorized upload paths. [VERIFIED: tests/integration/test_prusa_link.py] |
| Evidence contract framework | New schema language or dependency | Plain JSON plus stdlib validation helpers. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json] [VERIFIED: tools/bazel/phase13_ci_evidence.py] | Phase 13 already established this repo-local pattern and Phase 14 explicitly prefers standard-library Python. [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| Phase command entrypoints | New top-level command system | Existing Bazel labels, `rust_workflow.sh`, root aliases, and `justfile`. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: tools/bazel/rust_workflow.sh] [VERIFIED: BUILD.bazel] [VERIFIED: justfile] | Prior phase verifiers already use this workflow surface. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: justfile] |

**Key insight:** The hard part is not launching the simulator; it is preserving traceability and proof boundaries so simulator evidence is reviewable without becoming a false hardware, live-service, release, signing, or cutover claim. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json]

## Common Pitfalls

### Pitfall 1: Simulator Evidence Overclaim

**What goes wrong:** Generated summaries imply hardware proof, final cutover readiness, signing proof, release proof, live service proof, or retained-code acceptance. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**Why it happens:** Simulator logs and passing pytest nodes can look like broad parity proof unless scenario rows carry explicit residual classifications. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**How to avoid:** Require residual gate fields and scan contracts/generated summaries for forbidden overclaim markers, following Phase 11 and Phase 13 verifier patterns. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: tools/bazel/phase13_ci_evidence.py]

**Warning signs:** Phrases such as `cutover complete`, `hardware verified locally`, `byte-identical firmware`, `reference path removed`, or `simulator passed locally` appear in checked-in manifests or generated summaries. [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: tools/bazel/phase13_ci_evidence.py]

### Pitfall 2: Treating Missing Simulator Inputs as Failure or Pass

**What goes wrong:** Local verification fails hard because pytest, Mini404, or firmware inputs are missing, or worse, marks real simulator evidence as passed without running it. [VERIFIED: local command 2026-06-17]

**Why it happens:** Real simulator flows require bootstrapped Python dependencies, Mini404/QEMU, and a firmware image, but Phase 14 also needs deterministic local verification. [VERIFIED: tests/integration/README.md] [VERIFIED: tests/integration/conftest.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**How to avoid:** Implement separate contract/dry-run mode and real simulator mode; missing real prerequisites should produce `pending-simulator-input` or `pending-simulator-dependency`, not pass. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**Warning signs:** The verifier imports pytest or EasyOCR at module import time, or `just phase14-verify` requires a firmware image in the default path. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17]

### Pitfall 3: Using Skipped Integration Tests as Positive Evidence

**What goes wrong:** Contract rows claim transfer coverage from pytest nodes that are currently marked skipped. [VERIFIED: tests/integration/test_prusa_link.py]

**Why it happens:** The file contains both runnable and skipped transfer-related scenarios. [VERIFIED: tests/integration/test_prusa_link.py]

**How to avoid:** Require each scenario row to declare whether the source pytest node is active, skipped, pending, or residual; the verifier should reject skipped nodes in `pass_evidence_nodes`. [VERIFIED: tests/integration/test_prusa_link.py]

**Warning signs:** Rows for successful upload/download/thumbnail transfer flows carry `passed` status without a non-skipped source node. [VERIFIED: tests/integration/test_prusa_link.py]

### Pitfall 4: Losing v1.0 Traceability

**What goes wrong:** Simulator scenarios only map to `SIM-*` IDs and do not cite archived Phase 11 evidence rows. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**Why it happens:** The new v1.1 simulator requirements are narrower than the archived v1.0 evidence surface, so a simple SIM-only matrix omits cutover blockers. [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json]

**How to avoid:** Validate every scenario has `requirement_ids`, `v1_requirement_ids`, and `source_evidence_refs` that resolve to Phase 11 manifest rows or v1.0 requirements. [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] [VERIFIED: tools/bazel/manifests/phase11_reference_comparisons.json]

**Warning signs:** A scenario row lacks Phase 11 parity/reference/cutover IDs, or a SIM-03 row does not mention hardware-only exclusions. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

### Pitfall 5: Artifact Secret Leakage

**What goes wrong:** Raw crash dumps, certificates, signing keys, tokens, Wi-Fi credentials, credential values, or firmware packages are written into source or planning artifacts. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

**Why it happens:** Simulator and network flows can emit logs around credentials, firmware payloads, or crash content. [VERIFIED: .planning/codebase/CONCERNS.md]

**How to avoid:** Write only log references, normalized summaries, and redacted summaries; scan generated outputs and checked-in contracts for forbidden markers and file extensions. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase13_ci_evidence.py]

**Warning signs:** Generated evidence includes `.bin`, `.bbf`, `.dfu`, private key text, certificate bodies, raw dumps, tokens, passwords, or complete firmware payload paths intended for commit. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase13_ci_evidence.py]

## Code Examples

Verified patterns from checked-in sources:

### Contract Loading and Validation Boundary

Use standard-library JSON loading and return structured errors rather than exiting deep in helper functions. [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: standards/core/architecture.md]

```python
def read_contract(contract_path: Path) -> dict[str, object]:
    with contract_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_required_fields(contract: dict[str, object], required_fields: set[str]) -> list[str]:
    errors: list[str] = []
    for field in sorted(required_fields):
        if field not in contract:
            errors.append(f"contract missing required field: {field}")
    return errors
```

### Repo-Relative Path Guard

Phase 13 tests cover path traversal and output placement; Phase 14 should use equivalent guards for `build/ci-evidence/phase14` artifacts. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

```python
def require_repo_relative(path_text: str) -> str:
    path = PurePosixPath(path_text)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"path must be repo-relative and non-traversing: {path_text}")
    return path_text
```

### Optional Real Simulator Invocation

Real execution should be isolated behind a mode that receives firmware and optional simulator paths, then stores stdout/stderr as log references and normalized scenario status. [VERIFIED: tests/integration/README.md] [VERIFIED: tests/integration/conftest.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

```python
def build_pytest_command(firmware: Path, maybe_simulator: Path | None, node_ids: list[str]) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests/integration",
        "--firmware",
        str(firmware),
    ]
    if maybe_simulator is not None:
        command.extend(["--simulator", str(maybe_simulator)])
    command.extend(node_ids)
    return command
```

### Scenario Summary Shape

The generated manifest should be sufficient for review without opening raw logs. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

```json
{
  "scenario_id": "sim-gcode-file-print-telemetry",
  "status": "pending-simulator-input",
  "requirement_ids": ["SIM-01"],
  "v1_requirement_ids": ["CORE-03", "VERF-03"],
  "source_evidence_refs": [
    "phase11_requirement_evidence:CORE-03",
    "phase11_reference_comparisons:ref-gcode-behavior-fixtures"
  ],
  "artifact_refs": [
    "build/ci-evidence/phase14/logs/sim-gcode-file-print-telemetry.log"
  ],
  "residual_non_simulator_gates": ["pending-hardware", "pending-release"]
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Generic simulator command wrapper such as `simulator-parity` | Phase-owned evidence contract with scenario rows, source refs, residual statuses, and redacted generated summaries. [VERIFIED: tools/bazel/reference_contract.sh] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Phase 14 planning on 2026-06-17. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Planner should build traceability and overclaim guards first, then optional real simulator execution. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| Phase 11 archived cutover evidence as the latest local evidence surface | Phase 14 layers simulator evidence on top while preserving archived v1.0 rows. [VERIFIED: tools/bazel/manifests/phase11_requirement_evidence.json] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | v1.1 Phase 14 scope. [VERIFIED: .planning/ROADMAP.md] | Scenario rows must cite Phase 11 manifests instead of redefining v1.0 requirements. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| Phase 13 CI evidence orchestration as broad CI proof | Separate Phase 14 simulator proof ownership, with Phase 13 integration only if needed. [VERIFIED: tools/bazel/manifests/phase13_ci_evidence_contract.json] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Phase 14 locked decision D-16. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Planner should not extend Phase 13 as the main implementation path. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |

**Deprecated/outdated:** Treating `tests/integration/README.md`'s Python 3.7 statement as the effective minimum is outdated for this repo because `utils/bootstrap.py` asserts Python 3.8+. [VERIFIED: tests/integration/README.md] [VERIFIED: utils/bootstrap.py]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|

All claims in this research were verified from checked-in project files or local command probes; no `[ASSUMED]` claims are intentionally used. [VERIFIED: local command 2026-06-17]

## Open Questions

1. **Which firmware artifact should real simulator mode use by default?**  
   - What we know: The integration README documents `pytest tests/integration --firmware <firmware.bin>` and says the currently supported firmware is MK4 noboot. [VERIFIED: tests/integration/README.md]  
   - What's unclear: No runnable firmware image was found under local `build/`, so the exact default Phase 14 real-run artifact path must be chosen during implementation or supplied by maintainers. [VERIFIED: local command 2026-06-17]  
   - Recommendation: Make `--firmware` required for real simulator mode and report `pending-simulator-input` in dry-run/contract mode. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

2. **Should Phase 14 execute all non-skipped `test_safety.py` nodes or a curated representative subset?**  
   - What we know: `test_safety.py` includes several non-skipped min/max/runaway/preheat flows and one skipped nozzle max-temp limitation. [VERIFIED: tests/integration/test_safety.py]  
   - What's unclear: Phase 14 only requires selected failure behavior, so the planner can choose a representative subset if runtime becomes high. [VERIFIED: .planning/REQUIREMENTS.md]  
   - Recommendation: Include at least one min-temp, one max-temp, one runaway, and one preheat failure row, and keep skipped nodes as residual limitations. [VERIFIED: tests/integration/test_safety.py]

3. **Should Phase 14 write a generated `14-VALIDATION.md` summary during verifier execution?**  
   - What we know: Nyquist validation is enabled in `.planning/config.json`, and prior phases have validation/verification artifacts in phase directories. [VERIFIED: .planning/config.json] [VERIFIED: .planning/phases/13-ci-evidence-orchestration/13-VERIFICATION.md]  
   - What's unclear: The Phase 14 context explicitly names generated outputs under `build/ci-evidence/phase14`, not a checked-in generated validation document. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]  
   - Recommendation: Plan checked-in validation documentation separately from generated simulator artifacts; do not make the runner mutate planning docs by default. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | Phase 14 verifier/dry-run and repo bootstrap | Yes | 3.14.4 locally; bootstrap requires 3.8+. [VERIFIED: local command 2026-06-17] [VERIFIED: utils/bootstrap.py] | None needed for dry-run. |
| Bazel | `phase14_verify` / `phase14_verify_tests` labels | Yes | 9.1.1. [VERIFIED: local command 2026-06-17] | Run Python script directly if Bazel wiring is being debugged. |
| `just` | `just phase14-verify` facade | Yes | 1.48.0. [VERIFIED: local command 2026-06-17] | Run Bazel labels directly. |
| pytest | Real simulator execution | No in active Python env | Declared as `pytest~=7.3.2`; import probe failed. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | Dry-run/contract mode; bootstrap environment before real simulator mode. |
| pytest-asyncio | Integration pytest async support | No in active Python env | Declared as `pytest-asyncio~=0.21`. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | Dry-run/contract mode. |
| aiohttp / requests | PrusaLink/WUI integration tests and bootstrap | No in active Python env | `aiohttp~=3.8`, `requests==2.32.3`. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | Dry-run/contract mode. |
| EasyOCR / Pillow | Screen/OCR integration helpers | No in active Python env | `easyocr~=1.7`, `pillow~=10.4`. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | Dry-run/contract mode. |
| littlefs-python | Storage/resource-related tooling dependency | No in active Python env | `littlefs-python==0.8`. [VERIFIED: requirements.txt] [VERIFIED: local command 2026-06-17] | Dry-run/contract mode. |
| Mini404 / `qemu-system-buddy` | Real simulator process | No | Bootstrap config uses Mini404 0.9.10; local binary missing. [VERIFIED: utils/bootstrap.py] [VERIFIED: local command 2026-06-17] | Dry-run/contract mode; run `utils/bootstrap.py` before real mode. |
| Firmware `.bin` for simulator | Real simulator pytest command | No local runnable build artifact found | Not available under `build/`; tracked ESP resource blobs are not simulator firmware. [VERIFIED: local command 2026-06-17] | Require `--firmware` for real mode and emit `pending-simulator-input` otherwise. |

**Missing dependencies with no fallback:** None for deterministic Phase 14 contract verification because Python, Bazel, and `just` are available. [VERIFIED: local command 2026-06-17]

**Missing dependencies with fallback:** Active pytest dependencies, Mini404/QEMU, and firmware inputs are missing locally; dry-run/contract mode is the fallback and real simulator mode remains pending until bootstrap and firmware artifacts are available. [VERIFIED: local command 2026-06-17] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib `unittest` for verifier tests; optional pytest only for real simulator execution. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py] [VERIFIED: tests/integration/README.md] |
| Config file | `.planning/config.json` enables Nyquist validation; Phase 14 contract should be `tools/bazel/manifests/phase14_simulator_evidence_contract.json`. [VERIFIED: .planning/config.json] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| Quick run command | `python3 tools/bazel/phase14_simulator_evidence.py --quick` should validate the contract and deterministic dry-run artifacts. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| Full suite command | `just phase14-verify` should run the Phase 14 tests before the Phase 14 verifier. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: justfile] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| SIM-01 | Contract includes startup, task readiness, watchdog-visible startup behavior, and representative G-code scenario rows with v1.0 refs and residual hardware classifications. [VERIFIED: .planning/REQUIREMENTS.md] | Unit/contract | `python3 tools/bazel/phase14_simulator_evidence_test.py -k sim01` | No - Wave 0 creates `tools/bazel/phase14_simulator_evidence_test.py`. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| SIM-01 | Real simulator command shape exists for startup/G-code rows without requiring local execution by default. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Unit/command-builder | `python3 tools/bazel/phase14_simulator_evidence_test.py -k command` | No - Wave 0. |
| SIM-02 | Contract includes GUI, storage/resource, transfer, and selected failure rows, and rejects skipped tests as pass evidence. [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: tests/integration/test_prusa_link.py] | Unit/contract | `python3 tools/bazel/phase14_simulator_evidence_test.py -k sim02` | No - Wave 0. |
| SIM-02 | Dry-run writer produces normalized scenario summary, run manifest, log refs, and redacted summary under `build/ci-evidence/phase14`. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Unit/tempdir artifact | `python3 tools/bazel/phase14_simulator_evidence_test.py -k artifacts` | No - Wave 0. |
| SIM-03 | Every scenario maps to `SIM-*`, v1.0 refs, Phase 11 source refs, and explicit residual statuses for non-simulator gates. [VERIFIED: .planning/REQUIREMENTS.md] [VERIFIED: tools/bazel/manifests/phase11_cutover_readiness.json] | Unit/contract | `python3 tools/bazel/phase14_simulator_evidence_test.py -k sim03` | No - Wave 0. |
| SIM-03 | Verifier rejects overclaim, secret markers, raw firmware packages, raw crash dumps, path traversal, and unknown source refs. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: tools/bazel/phase13_ci_evidence.py] | Unit/security | `python3 tools/bazel/phase14_simulator_evidence_test.py -k guards` | No - Wave 0. |
| SIM-01/SIM-02/SIM-03 | Bazel and `just` expose Phase 14 verifier/test entrypoints. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] | Unit/wiring | `python3 tools/bazel/phase14_simulator_evidence_test.py -k wiring` | No - Wave 0. |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase14_simulator_evidence_test.py` and `python3 tools/bazel/phase14_simulator_evidence.py --quick` after touching Phase 14 verifier, contract, or wiring. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]
- **Per wave merge:** Run `just phase14-verify` once Bazel/just wiring exists. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: justfile]
- **Phase gate:** Run `just phase14-verify` and record that real simulator execution remains pending unless firmware, pytest deps, and Mini404/QEMU are provided. [VERIFIED: local command 2026-06-17] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase14_simulator_evidence_contract.json` - defines Phase 14 simulator scenarios, statuses, artifact kinds, source refs, and output root. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]
- [ ] `tools/bazel/phase14_simulator_evidence.py` - validates contract, writes deterministic dry-run artifacts, optionally invokes real simulator pytest nodes, redacts summaries, and rejects overclaims/secrets. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]
- [ ] `tools/bazel/phase14_simulator_evidence_test.py` - regression tests for SIM coverage, source refs, skipped-node handling, artifacts, wiring, path guards, and security scans. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py]
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 14 labels, aliases, dispatch, and developer recipe. [VERIFIED: tools/bazel/BUILD.bazel] [VERIFIED: BUILD.bazel] [VERIFIED: tools/bazel/rust_workflow.sh] [VERIFIED: justfile]
- [ ] Phase 14 validation/verification documentation - should record dry-run evidence and explicit non-local simulator/hardware/live/release boundaries. [VERIFIED: .planning/config.json] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | Limited | Phase 14 does not implement authentication, but PrusaLink simulator scenarios include authenticated and unauthorized API flows; artifacts must not expose API keys or credential values. [VERIFIED: tests/integration/test_prusa_link.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| V3 Session Management | No | Phase 14 only records simulator evidence and should not add session handling. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| V4 Access Control | Limited | Unauthorized upload evidence can be recorded, but the phase must not claim complete access-control proof. [VERIFIED: tests/integration/test_prusa_link.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| V5 Input Validation | Yes | Validate JSON fields, status vocabulary, source refs, repo-relative paths, artifact kinds, and command modes with stdlib helpers. [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: tools/bazel/phase13_ci_evidence_test.py] |
| V6 Cryptography | Limited | Phase 14 does not implement cryptography; verifier must reject private certificates, signing keys, tokens, and credential-bearing values in artifacts. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |

### Known Threat Patterns for Phase 14

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Evidence overclaim | Spoofing / Repudiation | Reject forbidden proof claims and require residual classifications for hardware, live service, release, signing, retained-code, and final demotion gates. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase11_verify.py] |
| Artifact path traversal | Tampering | Require repo-relative non-traversing paths and output root under `build/ci-evidence/phase14`. [VERIFIED: tools/bazel/phase13_ci_evidence_test.py] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |
| Secret leakage in logs/summaries | Information Disclosure | Write log references and redacted summaries; scan for private key, certificate, password, token, Wi-Fi credential, raw crash dump, and firmware package markers. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: .planning/codebase/CONCERNS.md] |
| Command injection in simulator mode | Elevation of Privilege | Build subprocess commands as argument lists from validated firmware/simulator paths and known pytest node IDs. [VERIFIED: tests/integration/README.md] [VERIFIED: standards/core/code-shape.md] |
| False pass from missing dependencies | Tampering / Repudiation | Missing pytest, Mini404/QEMU, or firmware must become pending statuses, not pass statuses. [VERIFIED: local command 2026-06-17] [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/14-simulator-evidence-gates/14-CONTEXT.md` - locked decisions, phase boundary, canonical refs, scenario families, artifact contract, workflow expectations, overclaim boundaries.
- `.planning/REQUIREMENTS.md` - `SIM-01`, `SIM-02`, `SIM-03` requirement definitions.
- `.planning/ROADMAP.md` - Phase 14 goal, dependencies, and success criteria.
- `.planning/STATE.md` - milestone state and Phase 14 starting point.
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/index.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, `standards/core/testing.md`, `standards/languages/rust.md` - repo and Bright Builds constraints.
- `tools/bazel/phase13_ci_evidence.py`, `tools/bazel/phase13_ci_evidence_test.py`, `tools/bazel/manifests/phase13_ci_evidence_contract.json` - closest evidence-contract and verifier pattern.
- `tools/bazel/phase11_verify.py`, `tools/bazel/manifests/phase11_parity_pyramid.json`, `tools/bazel/manifests/phase11_requirement_evidence.json`, `tools/bazel/manifests/phase11_reference_comparisons.json`, `tools/bazel/manifests/phase11_cutover_readiness.json` - v1.0 source evidence and residual gate taxonomy.
- `tests/integration/README.md`, `tests/integration/conftest.py`, `tests/integration/actions/screen.py`, `tests/integration/actions/utils.py`, `tests/integration/test_basic_examples.py`, `tests/integration/test_safety.py`, `tests/integration/test_prusa_link.py`, `utils/simulator/simulator.py` - simulator execution substrate and available scenario coverage.
- `requirements.txt`, `utils/bootstrap.py`, `.gitignore`, `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - dependencies, ignored output roots, and workflow wiring.
- Local command probes on 2026-06-17 - Python 3.14.4, Bazel 9.1.1, just 1.48.0 available; pytest deps, Mini404/QEMU, and firmware artifact unavailable in active environment.

### Secondary (MEDIUM confidence)

- None. No external web or secondary source was needed because Phase 14 is constrained by checked-in project artifacts. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md]

### Tertiary (LOW confidence)

- None. No unverified source was used. [VERIFIED: local command 2026-06-17]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - locked Phase 14 decisions and existing Phase 13 patterns specify Python stdlib, JSON manifests, Bazel labels, `just`, and existing simulator pytest substrate. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase13_ci_evidence.py]
- Architecture: HIGH - source files show established contract/verifier/artifact/wiring patterns and existing simulator fixtures. [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: tests/integration/conftest.py]
- Pitfalls: HIGH - overclaim, secret, non-local proof, skipped-test, and missing-dependency risks are explicitly visible in Phase 14 context, Phase 11/13 verifiers, existing tests, and local probes. [VERIFIED: .planning/phases/14-simulator-evidence-gates/14-CONTEXT.md] [VERIFIED: tools/bazel/phase11_verify.py] [VERIFIED: tools/bazel/phase13_ci_evidence.py] [VERIFIED: local command 2026-06-17]
- Environment: HIGH - tool availability and missing dependencies were checked locally on 2026-06-17. [VERIFIED: local command 2026-06-17]

**Research date:** 2026-06-17  
**Valid until:** 2026-07-17 for contract and architecture guidance; re-check environment availability and integration-test skip status before implementation. [VERIFIED: local command 2026-06-17] [VERIFIED: tests/integration/test_prusa_link.py]
