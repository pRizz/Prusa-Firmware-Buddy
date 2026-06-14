---
generated_by: gsd-phase-researcher
lifecycle_mode: yolo
phase_lifecycle_id: 11-2026-06-14T18-48-49
generated_at: 2026-06-14
---

# Phase 11: Parity Pyramid and Cutover Evidence - Research

**Researched:** 2026-06-14  
**Domain:** Firmware parity evidence, requirement traceability, reference comparison, cutover gates  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

The following constraints are copied verbatim from `.planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md`. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

### Locked Decisions

### Parity Pyramid Shape

- **D-01:** Build a source-backed parity pyramid manifest that names every required verification layer: Rust unit tests, adapter/domain contract tests, generated drift checks, reference fixture comparisons, simulator flows, network/TLS/API checks, release artifact checks, and hardware smoke or manual gates.
- **D-02:** Classify each evidence row by proof scope: `local`, `ci`, `simulator`, `hardware-smoke`, `manual-hardware-required`, or `retained-code-justification`. Local verification may only mark deterministic checks green.
- **D-03:** Keep non-local proof honest. Simulator, hardware, media, long-running network, physical UI/touch, RS485, MMU, toolchanger, and final release-candidate proof must remain explicit pending/non-local evidence unless an actual runnable command or artifact exists.
- **D-04:** Preserve the existing phase verifier pattern: add a repo-owned `tools/bazel/phase11_verify.py`, `phase11_verify_test.py`, Bazel labels, and a `just phase11-verify` facade instead of burying final qualification in ad hoc documentation.

### Requirement Traceability

- **D-05:** Create a requirement-to-evidence manifest that covers every v1 requirement from `.planning/REQUIREMENTS.md`, including previously completed requirements and the Phase 11 requirements `VERF-01`, `VERF-03`, `VERF-04`, and `VERF-05`.
- **D-06:** Each requirement row must name the owning phase, phase artifacts, verifier command or evidence class, current status, intentional-delta status, residual retained-code justification when applicable, and any required non-local evidence before cutover approval.
- **D-07:** Do not treat the roadmap checkbox alone as evidence. Completed phases are inputs, but Phase 11 must cross-check actual artifacts such as `*-VERIFICATION.md`, manifests, Rust domain contracts, and Bazel/just labels.
- **D-08:** Requirements still marked pending in `.planning/REQUIREMENTS.md` must be resolved by the Phase 11 evidence manifest or intentionally kept pending with a named cutover blocker. No silent pass-through is allowed.

### Reference Output Comparison

- **D-09:** Add explicit reference-comparison rows for product artifacts, generated resources, storage migrations, protocol traces, G-code behavior fixtures, UI/display-state fixtures, network/TLS/API behavior, auxiliary-controller flows, and release metadata.
- **D-10:** Use normalized semantic comparisons where byte identity is not yet a valid local contract. Byte-for-byte claims require a named reference fixture, normalization rule, or generated output known to be deterministic.
- **D-11:** CMake/C++ remains the reference oracle for final comparison, but Bazel remains the developer authority. Any command that invokes CMake/Python reference tooling must be labeled reference-only and guarded from default local execution if it is heavy, hardware-bound, or signing-sensitive.
- **D-12:** Secret-bearing and sensitive evidence remains name-only or redacted. Do not store Wi-Fi passwords, PrusaLink passwords, Connect tokens, certificate bytes, signing key values, raw crash dumps, or firmware payload bytes in Phase 11 manifests.

### Cutover Criteria

- **D-13:** Add a cutover-readiness contract that states the minimum criteria for demoting the CMake/C++ reference path: all v1 requirements mapped, local verifier passed, non-local gates identified, retained-code justifications accepted, intentional deltas documented, and no overclaim wording present.
- **D-14:** Keep the final CMake/C++ demotion itself gated. Phase 11 may add criteria and evidence, but should not delete or demote the reference path unless the evidence contract can prove the criteria are satisfied and the plan explicitly owns that transition.
- **D-15:** Represent residual retained C/C++/ASM/vendor islands as accepted, blocked, or deferred with owners and evidence. A retained island is acceptable only when it has a named boundary and justification from the earlier phase artifacts.
- **D-16:** Known defects from `.planning/codebase/CONCERNS.md` and phase-specific concern disposition manifests must appear in the cutover evidence as preserved temporarily, fixed with tests, accepted retained behavior, or blocked.

### Verification And Lifecycle

- **D-17:** Relevant local verification should include the Phase 11 verifier tests, the Phase 11 verifier, Rust format/lint/build/test checks through existing Bazel/just labels, and lifecycle validation.
- **D-18:** The Phase 11 verifier must check for overclaim language that asserts hardware proof from local-only evidence, final cutover completion, or firmware byte identity when the evidence is only manifest, CI, simulator, hardware/manual, or retained-code justification.
- **D-19:** Lifecycle validation must stay clean: context, research, plans, summaries, verification, and phase artifacts should carry `phase_lifecycle_id: 11-2026-06-14T18-48-49`.

### the agent's Discretion

- Exact manifest names, row IDs, schema field order, Rust type names, and verifier helper structure are flexible if they remain source-backed, reviewable, deterministic, and covered by tests.
- The planner may split Phase 11 into focused plans by parity pyramid manifest, requirement traceability, reference comparison and cutover evidence, Rust domain contracts, and aggregate verifier/facade wiring.
- Prefer small standard-library Python helpers and pure Rust domain types over broad build-system rewrites. The final evidence layer should be auditable, not clever.

### Deferred Ideas (OUT OF SCOPE)

- Actual production cutover, deletion, or demotion of the CMake/C++ reference path is deferred unless the Phase 11 plan can prove all cutover criteria and explicitly owns that transition.
- New firmware features, improved proxy/TLS capabilities, transfer concurrency redesign, retained-vendor replacement, and hardware-lab dashboards remain v2 scope from `.planning/REQUIREMENTS.md`.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VERF-01 | Developer can run a parity test pyramid covering pure Rust unit tests, adapter contract tests, generated drift checks, reference fixture comparisons, simulator flows, network/TLS/API tests, release artifact checks, and hardware smoke gates. [VERIFIED: .planning/REQUIREMENTS.md] | Use a `phase11_parity_pyramid.json` manifest plus `phase11_verify.py` modes that aggregate existing Rust, generated, verifier, simulator, network, release, and hardware/manual evidence classes. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: justfile; VERIFIED: tools/bazel/BUILD.bazel] |
| VERF-03 | Developer can compare Rust outputs against reference firmware for product artifacts, generated resources, storage migrations, protocol traces, G-code behavior fixtures, UI state fixtures, and release metadata. [VERIFIED: .planning/REQUIREMENTS.md] | Use a `phase11_reference_comparisons.json` manifest that cites Phase 1 capture docs, Phase 3 artifact metadata compare, Phase 7 storage/resource manifests, Phase 8 GUI fixtures, Phase 9 network fixtures, and Phase 10 auxiliary manifests. [VERIFIED: .planning/phases/01-reference-baseline-and-safety-envelope/01-REFERENCE-CAPTURE.md; VERIFIED: tools/bazel/artifact_metadata_compare.py; VERIFIED: tools/bazel/manifests/phase7_generated_outputs.json; VERIFIED: tools/bazel/manifests/phase8_gui_workflows.json; VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: tools/bazel/manifests/phase10_auxiliary_controllers.json] |
| VERF-04 | Maintainer can review cutover evidence showing every v1 requirement mapped to passing tests, simulator or hardware evidence, intentional deltas, and residual retained-code justifications. [VERIFIED: .planning/REQUIREMENTS.md] | Use a `phase11_requirement_evidence.json` manifest covering all 30 v1 requirements and cross-check it against `*-VERIFICATION.md`, manifests, Rust domain exports, Bazel labels, and `just` recipes. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/*/*-VERIFICATION.md; VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: justfile] |
| VERF-05 | Maintainer can remove or demote the CMake/C++ reference path only after the Rust+Bazel build satisfies all parity gates and documented cutover criteria. [VERIFIED: .planning/REQUIREMENTS.md] | Add a `phase11_cutover_readiness.json` contract that keeps demotion blocked until every requirement row is mapped, local gates pass, non-local gates are named, retained-code justifications are accepted, and overclaim scans are clean. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: .bazelrc; VERIFIED: tools/bazel/reference_contract.sh] |

</phase_requirements>

## Summary

Phase 11 should be planned as the final auditable evidence layer, not as new firmware feature work. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] The existing repo already has source-backed manifests, typed Rust domain contracts, deterministic Python verifiers, Bazel `shell_binary` labels, `just` facade recipes, validation files, and phase verification reports through Phase 10. [VERIFIED: tools/bazel/manifests; VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile; VERIFIED: .planning/phases/*/*-VERIFICATION.md]

The main planning risk is overclaiming: prior phases intentionally defer hardware, simulator, live network/TLS, full release byte parity, physical UI/touch, RS485/MMU/toolchanger, storage media timing, and final release-candidate proof to Phase 11. [VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-VERIFICATION.md; VERIFIED: .planning/phases/06-printing-core-safety-and-feature-gates/06-VERIFICATION.md; VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-VERIFICATION.md; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-VERIFICATION.md; VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-VERIFICATION.md; VERIFIED: .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md]

**Primary recommendation:** Split Phase 11 into five plans: parity pyramid manifest, requirement traceability manifest, reference-comparison manifest plus pure Rust cutover/evidence contracts, cutover readiness/retained-code/concern evidence, and aggregate verifier/Bazel/`just`/validation sign-off. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: tools/bazel/phase10_verify_test.py]

## Project Constraints (from AGENTS.md)

- Repo guidance requires reading `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant Bright Builds canonical standards before planning, review, implementation, or audit work. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md; VERIFIED: standards-overrides.md]
- This project is a full Rust rewrite preserving current supported firmware behavior, with Bazel authoritative and C/C++/CMake retained as reference, comparison, or compatibility where necessary. [VERIFIED: AGENTS.md]
- Big Bang replacement, Behavior Parity, Bazel Primary Now, `justfile` workflows, Bright Builds standards, hardware-aware evidence, and named retained third-party/vendor code are project constraints. [VERIFIED: AGENTS.md]
- No active Bright Builds override is recorded because `standards-overrides.md` only contains placeholder template rows. [VERIFIED: standards-overrides.md]
- Bright Builds requires functional-core/imperative-shell architecture, parsing boundary data into domain types, making illegal states unrepresentable, testing pure business logic, one-concern unit tests, Arrange/Act/Assert test shape, repo-owned verification entrypoints, and Rust newtypes/enums for invariants. [CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/testing.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/verification.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]
- Root `AGENTS.md` states no project skills are installed, and local skill directories were absent during this research. [VERIFIED: AGENTS.md; VERIFIED: local `find .claude/skills .agents/skills .cursor/skills .github/skills` probes on 2026-06-14]
- GSD workflow guidance says not to edit repo files outside a GSD workflow unless explicitly asked; this research artifact is explicitly requested by the GSD phase workflow. [VERIFIED: AGENTS.md; VERIFIED: user request]

## Standard Stack

### Core

| Library/Surface | Version | Purpose | Why Standard |
|-----------------|---------|---------|--------------|
| Python stdlib verifier | Python 3.14.4 available locally; project requires Python 3.8+ for tooling. [VERIFIED: local `python3 --version` probe on 2026-06-14; VERIFIED: AGENTS.md] | Implement `tools/bazel/phase11_verify.py` and `phase11_verify_test.py` with `argparse`, `json`, `pathlib`, `subprocess`, `tempfile`, and `unittest`. [VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: tools/bazel/phase10_verify_test.py] | Phase 6 through Phase 10 verifiers use repo-owned standard-library Python and run through Bazel/`just`. [VERIFIED: tools/bazel/phase6_verify.py; VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: justfile] |
| Bazel `shell_binary` via `tools/bazel/shell_rules.bzl` | Bazel 9.1.1 available locally. [VERIFIED: local `bazel --version` probe on 2026-06-14; VERIFIED: tools/bazel/BUILD.bazel] | Expose `//tools/bazel:phase11_verify` and `//tools/bazel:phase11_verify_tests` plus root aliases. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel] | Existing phase verifiers and Rust workflow labels are wired this way. [VERIFIED: tools/bazel/BUILD.bazel] |
| `justfile` facade | just 1.48.0 available locally. [VERIFIED: local `just --version` probe on 2026-06-14; VERIFIED: justfile] | Add `phase11-verify` that runs verifier tests before aggregate verifier. [VERIFIED: justfile] | Prior phase recipes use `just phaseN-verify` as the developer entrypoint. [VERIFIED: justfile] |
| Rust `buddy-domain` crate | Workspace edition 2024, `rust-version = 1.85`; local rustc/cargo are 1.91.1. [VERIFIED: Cargo.toml; VERIFIED: rust/crates/domain/Cargo.toml; VERIFIED: local `rustc --version` and `cargo --version` probes on 2026-06-14] | Add pure cutover/evidence domain types only if manifest schemas need typed invariants beyond Python verification. [VERIFIED: rust/crates/domain/src/lib.rs; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] | Existing phases model parity rows, proof scopes, evidence classes, and product constraints in pure Rust modules. [VERIFIED: rust/crates/domain/src/gui.rs; VERIFIED: rust/crates/domain/src/network.rs; VERIFIED: rust/crates/domain/src/auxiliary.rs] |
| Existing Phase 1-10 artifacts | Phase artifacts are present for Phases 1 through 10. [VERIFIED: local `find .planning/phases -name '*-VERIFICATION.md'` probe on 2026-06-14] | Serve as the source corpus for requirement evidence, deferred non-local proof, retained-code justification, and comparison surfaces. [VERIFIED: .planning/phases/*/*-VERIFICATION.md] | Phase 11 is explicitly an aggregate, hardening, and audit layer over prior phase evidence. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |

### Supporting

| Library/Surface | Version | Purpose | When to Use |
|-----------------|---------|---------|-------------|
| `jq` | jq 1.7.1 available locally. [VERIFIED: local `jq --version` probe on 2026-06-14] | Optional developer inspection of JSON manifests. [VERIFIED: local manifest inspection during research] | Do not make jq required by Phase 11 verifier because existing verifiers use Python stdlib JSON. [VERIFIED: tools/bazel/phase10_verify.py] |
| Cargo Rust checks | cargo/rustc 1.91.1 available locally; workspace minimum is 1.85. [VERIFIED: Cargo.toml; VERIFIED: local command probes on 2026-06-14] | Full `--all` verification should run format, clippy, build, and tests through existing Rust workflow labels. [VERIFIED: tools/bazel/rust_workflow.sh] | Use under `--all` or `just phase11-verify`; keep quick mode static and deterministic. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/phase10_verify.py] |
| Phase 3 artifact/generator helpers | Repo-owned Python and Starlark helpers. [VERIFIED: tools/bazel/artifact_manifest.py; VERIFIED: tools/bazel/artifact_metadata_compare.py; VERIFIED: tools/bazel/generated_drift.py; VERIFIED: tools/bazel/artifact_rules.bzl] | Support reference-comparison rows for release metadata and generated drift labels. [VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md] | Use for semantic metadata checks; do not claim full firmware byte identity without deterministic reference fixtures. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md] |
| `BUDDY_BAZEL_EXECUTE_REFERENCE` guard | Default value is `0` in `.bazelrc`. [VERIFIED: .bazelrc] | Prevent default local execution of heavy CMake/Python reference commands. [VERIFIED: tools/bazel/reference_contract.sh; VERIFIED: tools/bazel/phase3_workflow.sh] | Keep CMake/C++ reference comparisons labeled `reference-only`, `ci`, or manual unless the guard is explicitly enabled in an approved environment. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Source-backed JSON manifests plus Python verifier | Prose-only cutover report | Prose-only evidence would violate D-04 and would not allow deterministic checks for missing rows, source paths, lifecycle IDs, overclaims, or secret markers. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: tools/bazel/phase10_verify.py] |
| Normalized semantic comparisons | Byte-for-byte comparisons everywhere | Byte identity is only valid when a deterministic fixture and normalization rule exist; Phase 11 D-10 forbids byte-for-byte claims without that basis. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |
| Guarded reference-only CMake/Python commands | Default local CMake reference execution | Default reference execution would conflict with Bazel Primary Now and the existing `BUDDY_BAZEL_EXECUTE_REFERENCE=0` guard. [VERIFIED: AGENTS.md; VERIFIED: .bazelrc; VERIFIED: tools/bazel/reference_contract.sh] |
| Pure Rust evidence/cutover types only where helpful | Broad Rust build-system rewrite | D-04 and D-17 require preserving the verifier/facade pattern, and D-11 keeps CMake/C++ as reference oracle rather than deleting it through research/planning alone. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |

**Installation:** No new external dependency should be added for Phase 11 planning. [VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: Cargo.toml; VERIFIED: MODULE.bazel]

**Version verification:** Local versions verified on 2026-06-14 were Python 3.14.4, Bazel 9.1.1, just 1.48.0, cargo 1.91.1, rustc 1.91.1, CMake 3.27.9, Ninja 1.13.2, jq 1.7.1, node v24.13.0, git 2.53.0, and ripgrep 15.1.0. [VERIFIED: local command probes on 2026-06-14]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
|-- phase11_verify.py
|-- phase11_verify_test.py
`-- manifests/
    |-- phase11_parity_pyramid.json
    |-- phase11_requirement_evidence.json
    |-- phase11_reference_comparisons.json
    |-- phase11_cutover_readiness.json
    `-- phase11_retained_code_justifications.json

rust/crates/domain/src/
|-- cutover.rs          # optional, only if typed cutover/evidence invariants are added
`-- lib.rs             # exports cutover types if added

.planning/phases/11-parity-pyramid-and-cutover-evidence/
|-- 11-VALIDATION.md
`-- 11-VERIFICATION.md
```

This structure follows the Phase 6 through Phase 10 pattern of source-backed manifests, Python verifier/tests, Bazel labels, root aliases, and `just` recipes. [VERIFIED: tools/bazel/manifests; VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: tools/bazel/phase10_verify_test.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile]

### Recommended Phase Split

| Plan | Focus | Primary Artifacts | Verification Hook |
|------|-------|-------------------|-------------------|
| 11-01 | Parity pyramid manifest and evidence taxonomy | `phase11_parity_pyramid.json` | `python3 tools/bazel/phase11_verify.py --pyramid-only` |
| 11-02 | Requirement-to-evidence traceability for all 30 v1 requirements | `phase11_requirement_evidence.json` | `python3 tools/bazel/phase11_verify.py --requirements-only` |
| 11-03 | Reference output comparison rows and optional Rust cutover/evidence types | `phase11_reference_comparisons.json`, optional `cutover.rs` | `python3 tools/bazel/phase11_verify.py --comparison-only --rust-only` |
| 11-04 | Cutover readiness, retained-code justifications, known-concern dispositions, overclaim/security guards | `phase11_cutover_readiness.json`, `phase11_retained_code_justifications.json` | `python3 tools/bazel/phase11_verify.py --cutover-only --security-only` |
| 11-05 | Aggregate verifier regression tests, Bazel/root aliases, `just`, validation sign-off | `phase11_verify.py`, `phase11_verify_test.py`, `11-VALIDATION.md` | `just phase11-verify` |

The split is recommended because the context explicitly permits splitting by parity pyramid manifest, requirement traceability, reference comparison/cutover evidence, Rust contracts, and aggregate verifier/facade wiring. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

### Pattern 1: Evidence Rows Are Source-Backed, Not Status-Backed

**What:** Every Phase 11 row should reference concrete repo artifacts such as prior verification files, manifests, Rust domain modules, Bazel labels, just recipes, validation files, or comparison fixtures. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

**When to use:** Use this for all parity pyramid, requirement evidence, reference comparison, retained-code justification, and cutover readiness rows. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

**Example:**

```json
{
  "id": "req-ifce-06-auxiliary-controllers",
  "requirement_id": "IFCE-06",
  "owning_phase": "10",
  "source_artifacts": [
    ".planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md",
    "tools/bazel/manifests/phase10_auxiliary_controllers.json",
    "tools/bazel/manifests/phase10_mmu_transport.json",
    "tools/bazel/manifests/phase10_modbus_rs485.json",
    "rust/crates/domain/src/auxiliary.rs"
  ],
  "evidence_class": "retained-code-justification",
  "proof_scope": "retained-code-justification",
  "local_status": "passed",
  "cutover_status": "pending-non-local-evidence",
  "required_non_local_evidence": [
    "RS485 hardware-smoke or simulator-flow artifact",
    "live MMU transport evidence",
    "toolchanger hardware-smoke evidence"
  ],
  "intentional_delta": "none",
  "retained_code_justification": "accepted-source-backed-boundary"
}
```

The example uses fields required by D-02, D-05, D-06, D-09, D-13, and D-15. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

### Pattern 2: Normalize Requirement IDs Across Legacy Schemas

**What:** Existing manifests use both `requirement` and `requirement_id`, and Phase 11 should normalize both forms into one internal requirement ID set before checking coverage. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/phase8_verify.py; VERIFIED: tools/bazel/phase10_verify.py]

**When to use:** Use this when aggregating Phase 6/7 older manifests and Phase 8-10 newer manifests. [VERIFIED: tools/bazel/manifests/phase7_config_store.json; VERIFIED: tools/bazel/manifests/phase10_auxiliary_controllers.json]

**Example:**

```python
def row_requirement_ids(row: dict[str, object]) -> set[str]:
    raw = row.get("requirement_id", row.get("requirement"))
    if not isinstance(raw, str) or not raw:
        raise VerificationError("row is missing requirement_id/requirement")
    return {part.strip() for part in raw.replace("/", ",").split(",") if part.strip()}
```

This follows the verifier pattern of parsing JSON rows and raising `VerificationError` for invalid schema data. [VERIFIED: tools/bazel/phase10_verify.py]

### Pattern 3: Treat Non-Local Evidence as First-Class

**What:** Phase 11 should have explicit statuses such as `passed-local`, `pending-ci`, `pending-simulator`, `pending-hardware-smoke`, `manual-hardware-required`, `accepted-retained-code`, `blocked`, and `not-cutover-ready`. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

**When to use:** Use this for simulator flows, hardware smoke, storage media, long-running network, physical UI/touch, RS485, MMU, toolchanger, release-candidate, signing-sensitive, and retained-code surfaces. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-VERIFICATION.md; VERIFIED: .planning/phases/08-local-interface-and-workflow-parity/08-VERIFICATION.md; VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-VERIFICATION.md; VERIFIED: .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md]

### Pattern 4: Cutover Contract Is a Gate, Not a Claim

**What:** `phase11_cutover_readiness.json` should allow the verifier to report "not ready" while still passing local static checks when non-local gates are honestly named. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

**When to use:** Use this to satisfy VERF-05 without deleting or demoting CMake/C++ unless all criteria are proven and the implementation plan explicitly owns that transition. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

### Anti-Patterns to Avoid

- **Roadmap checkbox as proof:** Do not map a requirement as satisfied from `.planning/ROADMAP.md` alone; cross-check actual artifacts. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]
- **Hardware proof from local-only evidence:** Do not write that hardware, simulator, live TLS, RS485, MMU, toolchanger, physical UI, media timing, or release-candidate proof passed locally unless a command/artifact exists. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: tools/bazel/phase10_verify.py]
- **Byte identity without fixture basis:** Do not claim firmware byte identity without a deterministic reference fixture or normalization rule. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]
- **Secret-bearing evidence:** Do not store Wi-Fi passwords, PrusaLink passwords, Connect tokens, certificate bytes, signing key values, raw crash dumps, or firmware payload bytes in Phase 11 manifests. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]
- **Default reference execution:** Do not make local `just phase11-verify` run heavy CMake/Python reference tooling by default. [VERIFIED: .bazelrc; VERIFIED: tools/bazel/reference_contract.sh]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| BBF/DFU reference packaging | A new local BBF/DFU encoder | Existing `utils/pack_fw.py --no-sign`, `utils/dfu.py`, and Phase 3 status manifests | Phase 3 explicitly routes reference formats through existing tools and classifies missing prerequisites as `bootstrap-required` or `ci-only`. [VERIFIED: tools/bazel/artifact_rules.bzl; VERIFIED: tools/bazel/artifact_packager.py; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md] |
| Generated drift registry | New ad hoc generator runner | `tools/bazel/generated_drift.py` and generated check/update labels | Existing registry already covers product profiles, options, resources, translations, fonts, WUI, ESP blobs, descriptors, package metadata, and tracked outputs. [VERIFIED: tools/bazel/generated_drift.py; VERIFIED: tools/bazel/manifests/phase7_generated_outputs.json] |
| Requirement coverage parsing | A prose table without enforcement | `phase11_requirement_evidence.json` checked by `phase11_verify.py` | D-05 through D-08 require every v1 requirement and pending requirement to be mapped or blocked. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |
| Non-local proof | Fake local commands or green placeholders | Explicit `simulator`, `hardware-smoke`, `manual-hardware-required`, `ci`, and `retained-code-justification` scopes | Prior verification files defer these categories to Phase 11 and Phase 11 D-02/D-03 makes them first-class. [VERIFIED: .planning/phases/*/*-VERIFICATION.md; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |
| TLS/network semantics | New TLS/client behavior during evidence phase | Phase 9 manifests, negative fixtures, and retained source references | Phase 11 does not add product behavior; Phase 9 owns local network contracts and defers live TLS/cloud proof. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-VERIFICATION.md] |
| Modbus/MMU/toolchanger semantics | New protocol implementations | Phase 10 source-backed auxiliary manifests and retained-code justifications | Phase 10 explicitly retains these as source-backed contracts and defers live transport/hardware proof. [VERIFIED: .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md] |

**Key insight:** Phase 11 should verify and organize evidence, not invent new proof mechanisms for firmware formats, hardware buses, TLS, simulators, or release signing. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md; VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-VERIFICATION.md; VERIFIED: .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md]

## Common Pitfalls

### Pitfall 1: Local Green Means Cutover Ready
**What goes wrong:** The local verifier passes and the report implies final production cutover is approved. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
**Why it happens:** Prior phase verifiers intentionally pass static/source-backed checks while deferring hardware, simulator, live service, and release proof. [VERIFIED: .planning/phases/07-persistence-storage-and-resource-compatibility/07-VERIFICATION.md; VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-VERIFICATION.md; VERIFIED: .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VERIFICATION.md]  
**How to avoid:** Make the cutover contract report `not-cutover-ready` until all required non-local evidence is attached or accepted. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
**Warning signs:** Phrases that mark cutover evidence as final, assert hardware passed from local-only evidence, or claim firmware byte identity appear without artifacts. [VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

### Pitfall 2: Pending Requirement Drift
**What goes wrong:** `.planning/REQUIREMENTS.md` still marks BAZL-03, BAZL-05, VERF-01, VERF-03, VERF-04, and VERF-05 as pending, and Phase 11 silently ignores the non-VERF pending rows. [VERIFIED: .planning/REQUIREMENTS.md]  
**Why it happens:** Phase 3 verification reports BAZL-03 and BAZL-05 as passed, but the requirements file still has them unchecked. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md]  
**How to avoid:** The requirement evidence manifest should either resolve each pending row with source-backed evidence or mark it as a named cutover blocker. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
**Warning signs:** Requirement rows use `completed` only from roadmap status and do not cite phase verification files or manifests. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

### Pitfall 3: Schema Fragmentation Across Phases
**What goes wrong:** Phase 11 fails to aggregate evidence because older manifests use `requirement` while newer manifests use `requirement_id`, or because proof scopes use older Phase 7 values. [VERIFIED: tools/bazel/manifests/phase7_config_store.json; VERIFIED: tools/bazel/manifests/phase10_auxiliary_controllers.json]  
**Why it happens:** The manifest schema evolved across phases. [VERIFIED: tools/bazel/phase7_verify.py; VERIFIED: tools/bazel/phase10_verify.py]  
**How to avoid:** Normalize legacy fields in Phase 11 verifier code and require new Phase 11 manifests to use the D-02 proof scope vocabulary. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
**Warning signs:** The verifier only recognizes one field spelling or only accepts `local/non-local`. [VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

### Pitfall 4: Secret and Payload Leakage
**What goes wrong:** Cutover evidence includes certificate bytes, token values, signing key material, firmware payload bytes, or raw crash dumps. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
**Why it happens:** Release, TLS, crash dump, credential, and firmware payload surfaces are evidence-rich but sensitive. [VERIFIED: .planning/codebase/CONCERNS.md; VERIFIED: .planning/codebase/INTEGRATIONS.md]  
**How to avoid:** Enforce forbidden marker scans and name-only/redacted policies in Phase 11 manifests and validation docs. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/phase10_verify.py]  
**Warning signs:** Manifest fields that store token values, password values, certificate bytes, private key material, signing key values, firmware payload bytes, or raw crash dumps. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/phase10_verify.py]

### Pitfall 5: Reference Path Demotion Inside Evidence Work
**What goes wrong:** A plan removes or demotes CMake/C++ before all parity gates are satisfied. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
**Why it happens:** Phase 11 success criteria mention demotion, but D-14 gates the actual transition. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
**How to avoid:** Keep demotion as a readiness contract unless a plan explicitly proves and owns all criteria. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
**Warning signs:** `reference_contract.sh`, CMake, or source oracle paths are deleted before `phase11_cutover_readiness.json` proves full readiness. [VERIFIED: tools/bazel/reference_contract.sh; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

## Code Examples

### Verifier Mode Dispatch

```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 11 cutover evidence.")
    parser.add_argument("--repo-root", default=None)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--quick", action="store_true")
    modes.add_argument("--all", action="store_true")
    modes.add_argument("--pyramid-only", action="store_true")
    modes.add_argument("--requirements-only", action="store_true")
    modes.add_argument("--comparison-only", action="store_true")
    modes.add_argument("--cutover-only", action="store_true")
    modes.add_argument("--security-only", action="store_true")
    modes.add_argument("--wiring-only", action="store_true")
    return parser.parse_args()
```

This mode shape follows Phase 10 verifier dispatch while adapting checks to Phase 11 evidence domains. [VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

### Requirement Coverage Check

```python
V1_REQUIREMENTS = {
    "BASE-01", "BASE-02", "BASE-03", "BASE-04",
    "BAZL-01", "BAZL-02", "BAZL-03", "BAZL-04", "BAZL-05",
    "RUST-01", "RUST-02", "RUST-03", "RUST-04", "RUST-05",
    "CORE-01", "CORE-02", "CORE-03", "CORE-04", "CORE-05",
    "IFCE-01", "IFCE-02", "IFCE-03", "IFCE-04", "IFCE-05", "IFCE-06",
    "VERF-01", "VERF-02", "VERF-03", "VERF-04", "VERF-05",
}

def check_requirement_coverage(rows: list[dict[str, object]]) -> None:
    covered = {require_string(row, "requirement_id", "requirement row") for row in rows}
    missing = sorted(V1_REQUIREMENTS - covered)
    if missing:
        raise VerificationError("missing v1 requirement evidence: " + ", ".join(missing))
```

The v1 requirement set is derived from `.planning/REQUIREMENTS.md`, which lists 30 mapped v1 requirements. [VERIFIED: .planning/REQUIREMENTS.md]

### Overclaim Guard

```python
OVERCLAIM_STRINGS = [
    "hardware verified from local-only evidence",
    "simulator marked passed locally",
    "firmware byte identity claimed",
    "cutover marked complete without evidence",
    "reference path deletion claimed",
    "signing key material recorded",
]
```

This guard extends Phase 9 and Phase 10 overclaim scans to the final cutover language required by D-18. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 1 prose baseline and capture docs | Phase 6-10 source-backed manifests plus aggregate verifiers | Phases 6-10 [VERIFIED: .planning/ROADMAP.md; VERIFIED: tools/bazel/manifests] | Phase 11 can aggregate machine-checkable evidence instead of manually reading prose. [VERIFIED: tools/bazel/phase10_verify.py] |
| CMake as build authority | Bazel as authority with guarded CMake/C++ reference paths | Phase 2 [VERIFIED: .planning/phases/02-bazel-authority-and-developer-facade/02-VERIFICATION.md; VERIFIED: .bazelrc] | Phase 11 should keep reference commands guarded and never make CMake the default local gate. [VERIFIED: tools/bazel/reference_contract.sh] |
| One local/non-local split | Explicit proof scopes: `local`, `ci`, `simulator`, `hardware-smoke`, `manual-hardware-required`, `retained-code-justification` | Phase 11 decision D-02 [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] | Final evidence can pass local checks while still showing cutover blockers honestly. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |
| Artifact smoke outputs only | Semantic artifact metadata comparisons through Phase 3 helpers | Phase 3 [VERIFIED: tools/bazel/artifact_metadata_compare.py; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md] | Phase 11 can cite semantic comparison rows without claiming full byte parity. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |

**Deprecated/outdated:** Treating `tests/module/Connect` as an active integration suite is outdated because `.planning/codebase/TESTING.md` and `.planning/codebase/CONCERNS.md` identify it as stale/disabled. [VERIFIED: .planning/codebase/TESTING.md; VERIFIED: .planning/codebase/CONCERNS.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 11 verifier/tests | yes | 3.14.4 | None needed for local static verifier. [VERIFIED: local probe on 2026-06-14] |
| Bazel | `//tools/bazel:phase11_verify` and query checks | yes | 9.1.1 | Direct `python3 tools/bazel/phase11_verify.py --quick` can be used before Bazel wiring exists. [VERIFIED: local probe on 2026-06-14; VERIFIED: tools/bazel/phase10_verify.py] |
| just | `just phase11-verify` facade | yes | 1.48.0 | Direct Bazel labels can be used while the recipe is being added. [VERIFIED: local probe on 2026-06-14; VERIFIED: justfile] |
| cargo/rustc | Rust cutover/evidence domain checks | yes | cargo 1.91.1, rustc 1.91.1 | Skip Rust-only plan if no new Rust domain types are added; otherwise use existing Rust workflow labels. [VERIFIED: local probe on 2026-06-14; VERIFIED: tools/bazel/rust_workflow.sh] |
| CMake | Reference-only comparison context | yes | 3.27.9 | Guard reference execution behind `BUDDY_BAZEL_EXECUTE_REFERENCE=1`; do not require it for quick local Phase 11 evidence. [VERIFIED: local probe on 2026-06-14; VERIFIED: .bazelrc; VERIFIED: tools/bazel/reference_contract.sh] |
| Ninja | CMake reference tests when explicitly run | yes | 1.13.2 | Same guarded reference-only path. [VERIFIED: local probe on 2026-06-14; VERIFIED: .planning/codebase/TESTING.md] |
| pytest | Simulator/network integration flows | no | not on `PATH` | Classify simulator/pytest flows as `simulator`, `ci`, or `manual-hardware-required` unless bootstrap installs requirements. [VERIFIED: local probe on 2026-06-14; VERIFIED: .planning/codebase/TESTING.md] |
| pre-commit | Hook-managed formatting/generated checks | no | not on `PATH` | Use existing Bazel/generated check evidence locally; classify hook-specific checks as bootstrap-required/CI unless installed. [VERIFIED: local probe on 2026-06-14; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VALIDATION.md] |
| Physical printer/hardware lab | hardware smoke gates | no verified local attachment | unknown | Keep as `hardware-smoke` or `manual-hardware-required` evidence until artifacts/logs exist. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |
| Mini404/simulator assets | simulator flows | no `.dependencies` assets listed locally | unknown | Keep simulator proof non-local unless bootstrap produces runnable simulator artifacts. [VERIFIED: local `.dependencies` probe on 2026-06-14; VERIFIED: .planning/codebase/TESTING.md] |

**Missing dependencies with no fallback:** None for the local static Phase 11 research/manifest/verifier plan. [VERIFIED: local environment probes on 2026-06-14]

**Missing dependencies with fallback:** `pytest`, `pre-commit`, simulator assets, and physical hardware are missing or not verified locally; fallback is explicit `ci`, `simulator`, `hardware-smoke`, or `manual-hardware-required` evidence classification. [VERIFIED: local environment probes on 2026-06-14; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python stdlib verifier tests plus Bazel `shell_binary` labels plus existing Rust workflow checks. [VERIFIED: tools/bazel/phase10_verify_test.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh] |
| Config file | `.planning/config.json`, `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `justfile`, `Cargo.toml`. [VERIFIED: .planning/config.json; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile; VERIFIED: Cargo.toml] |
| Quick run command | `python3 tools/bazel/phase11_verify.py --quick` [VERIFIED: pattern from tools/bazel/phase10_verify.py] |
| Full suite command | `just phase11-verify` [VERIFIED: pattern from justfile] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| VERF-01 | Parity pyramid covers Rust unit tests, adapter contracts, drift checks, reference comparisons, simulator, network/TLS/API, release artifacts, and hardware/manual gates. [VERIFIED: .planning/REQUIREMENTS.md] | manifest/verifier | `python3 tools/bazel/phase11_verify.py --pyramid-only` | no - Wave 0 |
| VERF-03 | Reference comparison rows cover artifacts, resources, storage migrations, protocol traces, G-code fixtures, UI fixtures, and release metadata. [VERIFIED: .planning/REQUIREMENTS.md] | manifest/verifier | `python3 tools/bazel/phase11_verify.py --comparison-only` | no - Wave 0 |
| VERF-04 | Every v1 requirement maps to phase artifacts, passing local evidence or non-local/manual evidence, intentional deltas, and retained-code justifications. [VERIFIED: .planning/REQUIREMENTS.md] | manifest/verifier | `python3 tools/bazel/phase11_verify.py --requirements-only` | no - Wave 0 |
| VERF-05 | CMake/C++ demotion remains blocked unless all parity gates and cutover criteria are satisfied. [VERIFIED: .planning/REQUIREMENTS.md] | cutover contract/verifier | `python3 tools/bazel/phase11_verify.py --cutover-only` | no - Wave 0 |

### Sampling Rate

- **Per task commit:** Run the most focused mode for the touched manifest or verifier path. [VERIFIED: pattern from .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VALIDATION.md]
- **Per wave merge:** Run `python3 tools/bazel/phase11_verify_test.py`, `python3 tools/bazel/phase11_verify.py --quick`, and any affected Rust checks when `rust/crates/domain` changes. [VERIFIED: pattern from .planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VALIDATION.md; VERIFIED: tools/bazel/rust_workflow.sh]
- **Phase gate:** Run `bazel run //tools/bazel:phase11_verify_tests`, `bazel run //tools/bazel:phase11_verify`, `just phase11-verify`, lifecycle validation, and relevant existing Rust/Bazel labels before `/gsd-verify-work`. [VERIFIED: justfile; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: .planning/config.json]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase11_parity_pyramid.json` - covers VERF-01 evidence layers. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]
- [ ] `tools/bazel/manifests/phase11_requirement_evidence.json` - covers all 30 v1 requirements and pending requirement handling. [VERIFIED: .planning/REQUIREMENTS.md]
- [ ] `tools/bazel/manifests/phase11_reference_comparisons.json` - covers VERF-03 comparison surfaces. [VERIFIED: .planning/REQUIREMENTS.md]
- [ ] `tools/bazel/manifests/phase11_cutover_readiness.json` - covers VERF-05 demotion criteria and cutover blockers. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]
- [ ] `tools/bazel/manifests/phase11_retained_code_justifications.json` - covers accepted/blocked/deferred retained islands. [VERIFIED: .planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-VERIFICATION.md; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]
- [ ] `tools/bazel/phase11_verify.py` and `tools/bazel/phase11_verify_test.py` - enforce schema, source paths, coverage, overclaims, secrets, wiring, lifecycle, and validation text. [VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: tools/bazel/phase10_verify_test.py]
- [ ] Bazel labels, root aliases, `rust_workflow.sh` dispatch, and `just phase11-verify`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]
- [ ] `11-VALIDATION.md` - nyquist-compliant validation contract because `.planning/config.json` has `workflow.nyquist_validation: true`. [VERIFIED: .planning/config.json]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | yes for evidence surfaces, no new auth behavior | Preserve Phase 9 Connect/PrusaLink auth evidence and name-only secret handling; do not store token/password values. [VERIFIED: .planning/phases/09-network-web-services-and-transfers/09-VERIFICATION.md; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |
| V3 Session Management | limited | Phase 11 should cite WUI/Connect command/session evidence from Phase 9 rather than introduce session behavior. [VERIFIED: tools/bazel/manifests/phase9_connect_contracts.json; VERIFIED: tools/bazel/manifests/phase9_wui_contracts.json] |
| V4 Access Control | limited | Cutover approval access is process evidence; the verifier should block demotion criteria when requirements or non-local gates are incomplete. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |
| V5 Input Validation | yes | Validate JSON schemas, repo-relative source paths, row IDs, proof scopes, statuses, lifecycle IDs, and requirement IDs in `phase11_verify.py`. [VERIFIED: tools/bazel/phase10_verify.py] |
| V6 Cryptography | yes for evidence handling | Do not record signing keys, certificate bytes, token values, or raw crash dumps; keep TLS/signing evidence redacted and reference-only. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: .planning/codebase/CONCERNS.md] |

### Known Threat Patterns for Phase 11 Evidence

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Secret values in manifests | Information Disclosure | Forbidden marker scan and name-only/redacted policies. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/phase10_verify.py] |
| Reference-path demotion before proof | Tampering / Elevation of Privilege | `phase11_cutover_readiness.json` must keep demotion blocked until all gates are satisfied. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md] |
| Local overclaim of non-local proof | Spoofing / Repudiation | Overclaim string scan and proof-scope validation. [VERIFIED: tools/bazel/phase10_verify.py] |
| Source path escape in manifests | Tampering | Reject absolute paths and `..` components, following existing verifier path checks. [VERIFIED: tools/bazel/phase10_verify.py] |
| Byte-identity claim without fixture | Tampering / Repudiation | Require named fixtures, normalization rules, or semantic comparison status. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: tools/bazel/artifact_metadata_compare.py] |

## Open Questions (RESOLVED)

1. **Which non-local evidence artifacts will maintainers accept for cutover?**  
   What we know: prior phases list simulator, hardware-smoke, manual-hardware-required, CI, and retained-code evidence categories. [VERIFIED: .planning/phases/*/*-VALIDATION.md]  
   Resolution basis: the repo does not define a final hardware-lab, simulator, release-candidate, or live network/TLS artifact format in the artifacts read during research. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
   **RESOLVED:** Phase 11 will not invent a new acceptance format or mark those gates locally passed. The manifests must name required non-local artifact IDs/classes for simulator flows, hardware smoke/manual gates, live network/TLS/API proof, storage media, release-candidate proof, RS485/MMU/toolchanger proof, and final demotion approval, and `phase11_cutover_readiness.json` must keep cutover blocked until maintainers attach or approve those artifacts. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

2. **Are BAZL-03 and BAZL-05 pending statuses stale or current blockers?**  
   What we know: `.planning/REQUIREMENTS.md` marks BAZL-03 and BAZL-05 pending, while Phase 3 verification reports both passed for scoped artifact/generator parity. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md]  
   Resolution basis: the revision instructions prohibit updating `.planning/REQUIREMENTS.md`, and D-08 requires pending requirements to be resolved by Phase 11 evidence or kept pending with named cutover blockers. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]  
   **RESOLVED:** Phase 11 will preserve `.planning/REQUIREMENTS.md` as-is and make `phase11_requirement_evidence.json` the source-backed resolution layer: BAZL-03 and BAZL-05 cite Phase 3 verification as scoped local evidence, but remain cutover-blocked for full release-candidate artifact/signing-sensitive proof where that evidence is not attached locally. [VERIFIED: .planning/phases/03-artifact-and-generator-parity/03-VERIFICATION.md; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]

3. **Should Phase 11 add Rust cutover domain types?**  
   What we know: prior phases add pure Rust types when evidence invariants benefit from type-level checks. [VERIFIED: rust/crates/domain/src/gui.rs; VERIFIED: rust/crates/domain/src/network.rs; VERIFIED: rust/crates/domain/src/auxiliary.rs]  
   Resolution basis: Phase 11 plans include a Rust-only verifier surface, and Bright Builds architecture/Rust guidance favors typed domain contracts when they make invalid proof-scope, status, and comparison states harder to represent. [CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/core/architecture.md; CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/languages/rust.md]  
   **RESOLVED:** Plan 11-03 will add `rust/crates/domain/src/cutover.rs` and export it from `lib.rs` as pure, unsafe-free evidence contracts. The Python verifier remains authoritative for checked-in manifests; the Rust module adds focused domain invariants and tests for proof scopes, comparison contracts, cutover statuses, retained-code dispositions, and row IDs. [VERIFIED: rust/crates/domain/src/gui.rs; VERIFIED: rust/crates/domain/src/network.rs; VERIFIED: rust/crates/domain/src/auxiliary.rs; VERIFIED: tools/bazel/phase10_verify.py]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| - | None. All factual claims in this research are sourced to repo files, local command probes, or cited Bright Builds canonical standards. [VERIFIED: this research process] | - | - |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md` - locked Phase 11 decisions, discretion, and deferred scope. [VERIFIED: local file read]
- `.planning/REQUIREMENTS.md` - v1 requirement IDs, descriptions, pending status, and traceability. [VERIFIED: local file read]
- `.planning/STATE.md` and `.planning/ROADMAP.md` - phase position, dependencies, success criteria, and current project state. [VERIFIED: local file read]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` - repo-local and Bright Builds workflow constraints. [VERIFIED: local file read]
- Phase 1-10 `*-VERIFICATION.md` and `*-VALIDATION.md` files - prior evidence, deferred non-local proof, lifecycle metadata, and validation patterns. [VERIFIED: local file reads and `rg` scans]
- `tools/bazel/phase10_verify.py`, `tools/bazel/phase10_verify_test.py`, `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - latest verifier/facade pattern. [VERIFIED: local file reads]
- `tools/bazel/manifests/*.json` - existing source-backed parity manifest schema and row coverage. [VERIFIED: local file reads and `jq` scans]
- `rust/crates/domain/src/lib.rs`, `gui.rs`, `network.rs`, `auxiliary.rs`, `storage.rs`, `resource.rs` - Rust domain contract patterns. [VERIFIED: local file reads and `rg` scans]

### Secondary (MEDIUM confidence)

- Bright Builds canonical standards at commit `05f8d7a6c9c2e157ec4f922a05273e72dab97676` for architecture, code shape, verification, testing, and Rust. [CITED: https://raw.githubusercontent.com/bright-builds-llc/bright-builds-rules/05f8d7a6c9c2e157ec4f922a05273e72dab97676/standards/index.md]

### Tertiary (LOW confidence)

- None. [VERIFIED: source review scope]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - based on existing repo verifier, Rust, Bazel, and `just` patterns plus local tool probes. [VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: local command probes on 2026-06-14]
- Architecture: HIGH - Phase 11 decisions explicitly require manifests/verifier/facade and prior phases provide direct patterns. [VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md; VERIFIED: tools/bazel/phase10_verify.py]
- Pitfalls: HIGH - overclaim, redaction, reference guard, and non-local proof pitfalls are encoded in prior verifiers and Phase 11 decisions. [VERIFIED: tools/bazel/phase9_verify.py; VERIFIED: tools/bazel/phase10_verify.py; VERIFIED: .planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md]
- Environment: MEDIUM - local command probes are current for this machine, but hardware/simulator lab availability is not established. [VERIFIED: local command probes on 2026-06-14; VERIFIED: .planning/codebase/TESTING.md]

**Research date:** 2026-06-14  
**Valid until:** 2026-07-14 for local codebase patterns; re-check local tool availability and any newly added Phase 11 artifacts before planning or execution. [VERIFIED: local research date]
