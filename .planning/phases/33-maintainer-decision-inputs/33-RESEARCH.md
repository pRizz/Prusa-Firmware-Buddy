# Phase 33: Maintainer Decision Inputs - Research

**Researched:** 2026-07-04
**Domain:** Python/JSON/Bazel maintained decision-input verifier over Phase 32 blocker handoff artifacts
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### Decision Input Model
- **D-01:** Build Phase 33 as an explicit decision-input layer over Phase 32 handoff artifacts. Phase 32 remains the authority for blocker classification, proof eligibility, row problem kinds, owners, severity, and required next actions.
- **D-02:** Decision inputs should be machine-readable JSON templates and normalized output records, not prose-only approvals. Every accepted or rejected decision must include a stable decision id, decision type, source row refs, decision value, maintainer identity reference, timestamp, rationale, and evidence or artifact refs.
- **D-03:** Model retained-code acceptance, residual-risk acceptance, exception approval, final-readiness approval/block, and reference-demotion approval/rejection as separate axes. Do not infer one axis from another, and do not let green evidence rows create approval by themselves.
- **D-04:** Prefer a Phase 33-specific wrapper and manifest that reuse Phase 27/28 vocabulary for retained-code, residual-risk, exception, readiness, and demotion concepts while binding decisions to Phase 32's v1.3 handoff rows.
- **D-05:** Unknown decision types, missing required fields, stale lifecycle refs, unresolved source row refs, and malformed source refs must fail closed as invalid decision inputs.

### Retained-Code and Residual-Risk Decisions
- **D-06:** Retained-code rows can be accepted, rejected, or exception-approved only from explicit maintainer input with rationale and owner signoff. Evidence status and prior source-backed justifications remain supporting context, not acceptance.
- **D-07:** Residual-risk rows require explicit acceptance or rejection with owner signoff, rationale, affected gates, and follow-up refs where applicable.
- **D-08:** Redaction failures, unsafe refs, secret-tainted rows, lifecycle mismatches, and source-ref failures must not become accepted retained-code or accepted residual-risk decisions through a normal approval path. They remain blockers unless a later phase defines a narrow exception path that is itself explicitly approved and auditable.

### Exception Decisions
- **D-09:** Exception decisions should consume Phase 32 `exception_request` rows and require explicit scope, expiration or review trigger, affected requirements, affected gates, rationale, owner signoff, and linked blocker refs.
- **D-10:** Approved exceptions may cover a blocker for readiness only when the exception source row refs exactly match the blocker rows and the exception scope covers the affected gate. Broad or unmatched exceptions should remain invalid.
- **D-11:** Rejected exceptions should remain visible in Phase 33 outputs so Phase 34 and Phase 35 can explain why readiness or cutover remains blocked.

### Final-Readiness Decision Input
- **D-12:** Final-readiness approval or block is a separate maintainer decision input that consumes Phase 32 blockers plus approved exception and residual-risk decisions. It should not generate the final readiness packet itself.
- **D-13:** Readiness approval must be invalid when unresolved critical blockers remain without approved exception coverage or explicit residual-risk acceptance. Readiness block decisions should still be valid and should preserve the blocker refs and rationale for Phase 34 and Phase 35.
- **D-14:** The Phase 33 readiness decision output should be a handoff record for Phase 34, not a final readiness verdict.

### Reference-Demotion Decision Input
- **D-15:** Reference demotion requires a separate explicit decision input with `approve` or `reject` semantics. It must not be inferred from retained-code decisions, readiness decisions, approved exceptions, or green evidence.
- **D-16:** A demotion approval input should be retained as authorization data only. Phase 34 still owns proving that demotion opens only when readiness is otherwise unblocked and the explicit approval input is valid.
- **D-17:** A missing, malformed, rejected, stale, or out-of-scope demotion input must preserve fail-closed behavior for Phase 34.

### Generated Artifacts and Handoff
- **D-18:** Expected Phase 33 outputs should include a decision input template, normalized decision records, retained-code decision register, residual-risk decision register, exception decision register, readiness decision handoff, demotion decision handoff, decision validation report, downstream handoff manifest, redacted maintainer decision report, and contract snapshot artifacts.
- **D-19:** The downstream handoff should let Phase 34 generate final readiness and demotion dry-run outputs without rereading raw evidence packets or secret-bearing artifacts.
- **D-20:** The handoff should let Phase 35 link every blocker, exception, residual risk, retained-code decision, readiness decision, and demotion decision needed for the go/no-go artifact.

### the agent's Discretion
- The agent may choose the concrete Python module split and exact JSON filenames, provided the generated files are stable, documented in a manifest, and covered by tests.
- The agent may choose exact enum spellings where not already locked by Phase 27, Phase 28, or Phase 32 contracts, but all enum values must be documented in the Phase 33 contract and tested.
- The agent may choose whether to implement one script with subcommands or a verifier script plus helper functions.
- The agent may choose exact Bazel labels and `just` target names, but they should follow existing phase patterns such as `phase31_verify`, `phase32_verify`, and `phase33-verify`.

### Deferred Ideas (OUT OF SCOPE)
- Final readiness packet generation and reference-demotion dry-run behavior belong to Phase 34.
- The go/no-go cutover decision artifact belongs to Phase 35.
- Broad retained vendor/HAL replacement, new printer behavior, long-run dashboards, and production reference demotion remain future milestone work unless Phase 33 exposes a narrow decision-blocking defect.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DECIDE-01 | Maintainer can record retained-code acceptance, rejection, or approved exception decisions with residual-risk rationale and owner signoff. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse Phase 27 retained-code decision fields and hard-blocker precedence, but bind decisions to Phase 32 `retained_code_decision_required` rows. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase32_blocker_register_triage.py] |
| DECIDE-02 | Maintainer can record final-readiness approval or block decisions using machine-readable inputs that consume the triaged evidence rows and approved exceptions. [VERIFIED: .planning/REQUIREMENTS.md] | Consume Phase 32 blocker rows and approved exception/residual-risk outputs; emit a Phase 34 handoff, not the final readiness packet. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; tools/bazel/manifests/phase32_blocker_register_triage_contract.json] |
| DECIDE-03 | Maintainer can record reference-demotion approval or rejection as a separate explicit decision that cannot be inferred from green evidence alone. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse Phase 28 demotion input metadata and fail-closed policy, but store authorization data only for Phase 34 to evaluate. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py; tools/bazel/manifests/phase28_final_readiness_packet_contract.json] |
</phase_requirements>

## Summary

Phase 33 should be implemented as a local Python standard-library verifier that consumes Phase 32 generated artifacts under `build/ci-evidence/phase32`, validates explicit maintainer decision JSON, and writes a normalized Phase 33 handoff bundle under `build/ci-evidence/phase33`. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; tools/bazel/phase32_blocker_register_triage.py] The phase should not collect evidence, reclassify blockers, generate the final readiness packet, run a demotion dry run, or publish a cutover verdict. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; .planning/ROADMAP.md]

The strongest implementation pattern is the existing phase verifier pattern: checked-in JSON contract under `tools/bazel/manifests/`, Python verifier and `unittest` regression file under `tools/bazel/`, generated evidence under ignored `build/ci-evidence/phaseXX`, Bazel `shell_binary` targets, root aliases, `rust_workflow.sh` dispatch, and a `just phase33-verify` facade that runs tests before the verifier. [VERIFIED: tools/bazel/BUILD.bazel; BUILD.bazel; tools/bazel/rust_workflow.sh; justfile]

**Primary recommendation:** Build one Phase 33 verifier script plus one contract and one test file; keep Phase 33 as a decision-input normalizer over Phase 32 rows, with explicit fail-closed validation for stale lifecycle refs, unresolved row refs, missing decision metadata, invalid exception coverage, secret markers, and any attempt to infer approval from evidence status. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py; tools/bazel/phase32_blocker_register_triage.py]

## Project Constraints (from AGENTS.md)

- Read repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant standards before plan/review/implementation/audit work. [VERIFIED: AGENTS.md; AGENTS.bright-builds.md]
- Bazel is authoritative for this Rust port effort, and common developer workflows must have discoverable `justfile` wrappers. [VERIFIED: AGENTS.md; .planning/PROJECT.md]
- Use Bright Builds architecture, code-shape, verification, and testing standards unless a narrow override is documented; `standards-overrides.md` has no active real override. [VERIFIED: AGENTS.md; standards-overrides.md]
- Prefer functional core / imperative shell: keep decision rules pure and I/O in thin adapters. [VERIFIED: standards/core/architecture.md]
- Parse boundary JSON into trusted domain-like records early, and make illegal states unrepresentable where practical. [VERIFIED: standards/core/architecture.md]
- Prefer early returns and visible optional `maybe_` naming for internal optional values. [VERIFIED: standards/core/code-shape.md]
- Treat functions over roughly 161 lines and files over roughly 628 lines as refactor triggers, not hard caps. [VERIFIED: standards/core/code-shape.md]
- Do not hide substantial foreign-language logic inside strings; keep checked-in scripts rerunnable and diagnosable. [VERIFIED: standards/core/code-shape.md]
- Pure decision logic must have focused unit tests, and unit tests should use Arrange / Act / Assert structure. [VERIFIED: standards/core/testing.md]
- Before committing, run relevant repo-native verification and do not commit if checks fail. [VERIFIED: standards/core/verification.md]
- Use GSD planning artifacts/workflows for repo edits unless explicitly bypassed. [VERIFIED: AGENTS.md]
- Do not use standalone `---` body separators in frontmatter-parsed Markdown. [VERIFIED: user-provided AGENTS.md instructions]
- Python source in this repo is formatted through YAPF/pre-commit, and no mypy/ruff root config is detected in repo instructions. [VERIFIED: AGENTS.md]
- Rust-project pre-commit sequence is `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` before commits. [VERIFIED: user-provided AGENTS.md instructions]
- No project-local skills were found under `.claude/skills/` or `.agents/skills/`. [VERIFIED: find .claude/skills .agents/skills]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|---|---:|---|---|
| Python standard library | Python 3.14.4 available; repo requires Python 3.8+ | CLI verifier, JSON parsing, path validation, hashing, timestamps, `unittest` tests. | Existing Phase 27, 28, 31, and 32 verifiers are Python standard-library scripts with no new package dependency. [VERIFIED: python3 --version; tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py; tools/bazel/phase32_blocker_register_triage.py] |
| JSON contract manifest | n/a | Checked-in machine-readable Phase 33 schema, enum, artifact, source-contract, and verification-command contract. | Existing phase contracts live in `tools/bazel/manifests/` and are validated by `--contract-only`. [VERIFIED: tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json; tools/bazel/manifests/phase28_final_readiness_packet_contract.json; tools/bazel/manifests/phase32_blocker_register_triage_contract.json] |
| Bazel `shell_binary` | Bazel 9.1.1 available | Phase verifier and test targets under `//tools/bazel`. | Existing phase verifier targets use `shell_binary` data dependencies and root aliases. [VERIFIED: bazel --version; tools/bazel/BUILD.bazel; BUILD.bazel] |
| `just` | 1.48.0 available | Developer facade `phase33-verify`. | Adjacent phases expose `phase31-verify` and `phase32-verify` recipes that run tests before verifier targets. [VERIFIED: just --version; justfile] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|---|---:|---|---|
| `unittest` | Python stdlib | Regression tests for contract drift, input validation, generated artifacts, security scan, and wiring. | Use for `tools/bazel/phase33_maintainer_decision_inputs_test.py`, matching adjacent phase tests. [VERIFIED: tools/bazel/phase32_blocker_register_triage_test.py] |
| `hashlib` | Python stdlib | Stable row/decision IDs when source refs and payloads need deterministic identifiers. | Use for derived decision ids if maintainer input lacks only a derived row id, but do not replace explicit decision ids required by user constraints. [VERIFIED: tools/bazel/phase32_blocker_register_triage.py] |
| `pathlib` / symlink checks | Python stdlib | Repo-relative input/output containment. | Use for maintainer input, Phase 32 handoff paths, output root, and snapshot paths. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py] |
| `re` | Python stdlib | Secret/overclaim marker scanning and timestamp/source-ref validation. | Use for forbidden markers, ISO UTC timestamps, and source ref format checks. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py; tools/bazel/phase32_blocker_register_triage.py] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Python stdlib JSON validation | `jsonschema` or Pydantic | Do not add a dependency; repo precedent validates contracts with explicit Python helpers and avoids new package churn for phase verifiers. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; requirements.txt] |
| One verifier script | Multi-module Python package | A split could reduce file size, but existing phase wiring and Bazel data targets expect one script/test pair; use small pure helper functions inside one script unless implementation becomes materially harder to review. [VERIFIED: tools/bazel/BUILD.bazel; standards/core/code-shape.md] |
| Raw Phase 31/23/24/25 evidence reread | Phase 32 handoff artifacts | Do not reread raw evidence; Phase 33 is explicitly constrained to consume Phase 32 handoff rows so it does not bypass triage or secret-safety boundaries. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md] |

**Installation:**

No new package installation is recommended. [VERIFIED: existing phase verifiers use Python standard library; requirements.txt]

**Version verification:** `python3 --version` returned Python 3.14.4, `bazel --version` returned Bazel 9.1.1, `just --version` returned just 1.48.0, `cargo --version` returned cargo 1.91.1, and `git --version` returned git 2.53.0. [VERIFIED: command availability audit]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── manifests/
│   └── phase33_maintainer_decision_inputs_contract.json
├── phase33_maintainer_decision_inputs.py
└── phase33_maintainer_decision_inputs_test.py

build/ci-evidence/phase33/
├── maintainer-decision-input-template.json
├── normalized-decision-records.json
├── retained-code-decision-register.json
├── residual-risk-decision-register.json
├── exception-decision-register.json
├── readiness-decision-handoff.json
├── demotion-decision-handoff.json
├── decision-validation-report.json
├── downstream-handoff-manifest.json
├── redacted-maintainer-decision-report.md
└── contract-snapshots/
```

This structure mirrors existing phase verifier/contract/output layout and uses the artifact set locked in Phase 33 context. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; tools/bazel/phase32_blocker_register_triage.py]

### Pattern 1: Phase 32 Handoff as Input Boundary

**What:** Load `downstream-handoff-manifest.json`, resolve its `canonical_register_ref`, then load `blocker-register.json`, `decision-impact-index.json`, `exception-request-register.json`, and `residual-risk-request-register.json` from `build/ci-evidence/phase32`. [VERIFIED: build/ci-evidence/phase32/downstream-handoff-manifest.json; tools/bazel/phase32_blocker_register_triage.py]

**When to use:** Always for Phase 33 decision normalization; do not bypass Phase 32 by rereading raw evidence packets. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]

**Example:**

```python
def load_phase32_handoff(root: Path, handoff_arg: str) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    handoff_path = require_repo_relative_under(handoff_arg, Path("build/ci-evidence/phase32"), "--phase32-handoff")
    handoff = load_json_input(root, handoff_path, "--phase32-handoff")
    if handoff.get("phase_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError("--phase32-handoff phase_lifecycle_id is stale")
    register_path = require_repo_relative_under(handoff["canonical_register_ref"], Path("build/ci-evidence/phase32"), "canonical_register_ref")
    register = load_json_input(root, register_path, "Phase 32 blocker register")
    rows = require_rows(register, "Phase 32 blocker register")
    return handoff_path, handoff, rows
```

Source: local Phase 27/28/32 input loading and lifecycle validation patterns. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py; tools/bazel/phase32_blocker_register_triage.py]

### Pattern 2: Orthogonal Decision Axes

**What:** Normalize each decision into explicit axes: `decision_type`, `decision_value`, `source_row_refs`, `coverage_state`, `residual_risk_state`, `exception_state`, `readiness_decision_state`, and `demotion_decision_state`. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json]

**When to use:** Use for every retained-code, residual-risk, exception, readiness, and demotion decision so Phase 34/35 can consume only the axis they need. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]

### Pattern 3: Fail-Closed Hard Blockers Before Approval

**What:** Evaluate hard blockers such as `redaction_failed`, `secret_tainted`, `source_ref_failed`, `lifecycle_mismatch`, and `unsafe_ref` before accepting retained-code or residual-risk decisions. [VERIFIED: tools/bazel/manifests/phase32_blocker_register_triage_contract.json; tools/bazel/phase27_retained_code_acceptance_decisions.py]

**When to use:** Use before normal approval/exceptions, because Phase 27 and Phase 28 both treat redaction/source/lifecycle/unsafe failures as higher-priority blockers than exception coverage. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions_test.py; tools/bazel/phase28_final_readiness_packet_test.py]

### Pattern 4: Machine Rows First, Redacted Report Second

**What:** Generate JSON as source of truth and derive Markdown only from those rows. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py; tools/bazel/phase32_blocker_register_triage.py]

**When to use:** Use for the redacted maintainer decision report so it cannot become a prose-only approval surface. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]

### Anti-Patterns to Avoid

- **Inferring approval from green evidence:** Green evidence rows cannot create retained-code, residual-risk, exception, readiness, or demotion approval. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; .planning/ROADMAP.md]
- **Treating Phase 32 as approval authority:** Phase 32 explicitly prohibits exception approval, retained-code acceptance, residual-risk acceptance, final-readiness approval, reference-demotion authorization, and cutover verdicts. [VERIFIED: tools/bazel/manifests/phase32_blocker_register_triage_contract.json]
- **Broad exception coverage:** An approved exception must match exact blocker/source row refs and affected gate scope. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
- **Demotion in readiness decision:** Demotion approval/rejection must stay a separate decision input and handoff record. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; tools/bazel/manifests/phase28_final_readiness_packet_contract.json]
- **Secret-bearing raw evidence in Phase 33:** Maintainer input and generated outputs must use sanitized refs, digests, or external refs only. [VERIFIED: .planning/REQUIREMENTS.md; tools/bazel/phase32_blocker_register_triage.py]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| JSON parsing and writing | Custom parser or ad hoc string manipulation | Python `json` with explicit helper validation | Existing verifiers use structured JSON and fail on malformed top-level shapes. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py] |
| Path safety | Raw string concatenation | `pathlib` plus repo-relative, expected-root, and symlink checks | Existing verifiers reject parent traversal, absolute paths, and symlink output escapes. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py] |
| Stable ids | Random ids or timestamps | Deterministic ids from explicit decision id plus stable source refs, with duplicate checks | Phase 32 uses stable hashes for row ids and tests duplicate handling in decision inputs. [VERIFIED: tools/bazel/phase32_blocker_register_triage.py; tools/bazel/phase27_retained_code_acceptance_decisions_test.py] |
| Approval authorization | Derived flags from evidence or status fields | Explicit maintainer decision rows with required metadata | Requirement DECIDE-03 and Phase 28 prohibit evidence-implied demotion approval. [VERIFIED: .planning/REQUIREMENTS.md; tools/bazel/manifests/phase28_final_readiness_packet_contract.json] |
| Secret scanning | Trust maintainer inputs | Reuse forbidden field/text marker scanning patterns | Phase 27, 28, and 32 all scan inputs/outputs for forbidden secret and overclaim markers. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py; tools/bazel/phase32_blocker_register_triage.py] |
| Workflow integration | One-off shell command outside Bazel/just | Bazel `shell_binary`, root aliases, `rust_workflow.sh`, and `just phase33-verify` | Adjacent phases use this exact workflow surface. [VERIFIED: tools/bazel/BUILD.bazel; BUILD.bazel; tools/bazel/rust_workflow.sh; justfile] |

**Key insight:** The hard part is not generating JSON; it is preserving authorization boundaries so no evidence state, derived report, exception metadata, or quick/default artifact can become implicit approval. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; .planning/STATE.md]

## Common Pitfalls

### Pitfall 1: Reclassifying Phase 32 Rows

**What goes wrong:** Phase 33 recomputes `blocker_kind`, `row_problem_kind`, owner, severity, proof eligibility, or required action. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
**Why it happens:** It is tempting to decide coverage from source evidence status instead of Phase 32's canonical register. [VERIFIED: tools/bazel/phase32_blocker_register_triage.py]
**How to avoid:** Treat Phase 32 rows as authoritative and validate decisions only against row ids, source refs, gates, and decision impacts. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
**Warning signs:** New Phase 33 code has a problem-kind classifier or reads Phase 31/23/24/25 raw evidence directly. [VERIFIED: tools/bazel/phase32_blocker_register_triage.py]

### Pitfall 2: Accepting Hard-Blocked Rows Through Normal Approval

**What goes wrong:** Redaction failures, unsafe refs, secret-tainted rows, lifecycle mismatches, or source-ref failures become accepted risk. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
**Why it happens:** Exception/residual-risk approval logic runs before hard-block validation. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py]
**How to avoid:** Implement a `hard_blockers_for_source_rows()` guard and reject normal accept/exception decisions when source rows have hard blocker problem kinds. [VERIFIED: tools/bazel/manifests/phase32_blocker_register_triage_contract.json]
**Warning signs:** Tests approve rows with `row_problem_kind` in `redaction_failed`, `source_ref_failed`, `secret_tainted`, `lifecycle_mismatch`, or `unsafe_ref`. [VERIFIED: tools/bazel/phase32_blocker_register_triage_test.py]

### Pitfall 3: Readiness Approval Becomes Final Readiness Packet

**What goes wrong:** Phase 33 emits `final_readiness_status: unblocked` or otherwise acts as Phase 34. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
**Why it happens:** Phase 28 precedent has a final packet generator, but Phase 33 is only the v1.3 input layer. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py; .planning/ROADMAP.md]
**How to avoid:** Name the artifact `readiness-decision-handoff.json` and keep final readiness terms out of generated approval markers except as explicit blocked/decision handoff state. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
**Warning signs:** Phase 33 security scan sees `final_readiness_status: "unblocked"` or a report says final readiness approved. [VERIFIED: tools/bazel/phase32_blocker_register_triage.py]

### Pitfall 4: Demotion Approval Leaks Into Other Axes

**What goes wrong:** Readiness approval, exception approval, or retained-code acceptance implicitly authorizes reference demotion. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
**Why it happens:** Demotion is often represented as another readiness criterion in older artifacts. [VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json]
**How to avoid:** Emit a separate `demotion-decision-handoff.json` with `approved`, `rejected`, `blocked`, or invalid state and let Phase 34 enforce readiness prerequisites. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py]
**Warning signs:** `retained-code-decision-register.json` or `readiness-decision-handoff.json` contains `demotion_allowed`. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase32_blocker_register_triage.py]

### Pitfall 5: Missing Rejected Decisions

**What goes wrong:** Only accepted decisions are retained, so Phase 35 cannot explain blocked cutover. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
**Why it happens:** Registers are treated as approval lists rather than full decision records. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py]
**How to avoid:** Keep rejected exception, retained-code, residual-risk, readiness, and demotion decisions in normalized decision records and typed registers. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
**Warning signs:** Test fixtures reject an exception/demotion but no output row preserves that rejection. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]

## Code Examples

### Decision Record Shape

```json
{
  "decision_id": "phase33-retained-code-packet-freertos-runtime",
  "decision_type": "retained_code",
  "decision_value": "accept",
  "source_row_refs": [
    "build/ci-evidence/phase32/blocker-register.json#phase27-residual-risk-retained-code-..."
  ],
  "maintainer_identity_ref": "maintainer://retained-code-owner",
  "decision_timestamp": "2026-07-04T00:00:00Z",
  "rationale": "Explicit maintainer rationale for retaining this code with named residual risk.",
  "evidence_refs": [
    "build/ci-evidence/phase32/blocker-register.json#phase27-residual-risk-retained-code-..."
  ],
  "artifact_refs": []
}
```

Source: fields locked by Phase 33 context and metadata precedent from Phase 27/28. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py]

### Exact Exception Coverage Guard

```python
def validate_exception_coverage(decision: dict[str, Any], blocker_rows_by_id: dict[str, dict[str, Any]]) -> None:
    source_row_refs = require_non_empty_string_list(decision, "source_row_refs", "exception decision")
    for row_ref in source_row_refs:
        row = blocker_rows_by_id.get(row_ref_fragment(row_ref))
        if row is None:
            raise VerificationError(f"exception decision references unresolved blocker row: {row_ref}")
        if row["blocker_kind"] != "exception_request":
            raise VerificationError(f"exception decision cannot cover non-exception row: {row_ref}")
        if decision["affected_gate"] != row["affected_gate"]:
            raise VerificationError(f"exception decision scope does not cover affected gate: {row['affected_gate']}")
```

Source: exact source-row matching required by Phase 33 context and canonical row fields from Phase 32 contract. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; tools/bazel/manifests/phase32_blocker_register_triage_contract.json]

### Security Scan Pattern

```python
def run_security_scan(root: Path, output_dir: Path, maybe_input_path: str | None = None) -> None:
    paths = [CONTRACT_MANIFEST]
    if maybe_input_path:
        paths.append(require_repo_relative(maybe_input_path, "--maintainer-decisions"))
    if (root / output_dir).exists():
        paths.extend(path.relative_to(root) for path in sorted((root / output_dir).rglob("*")) if path.is_file())
    for path in paths:
        text = read_text(root, path)
        reject_forbidden_text(path, text)
        if path.suffix == ".json":
            reject_forbidden_json_fields(json.loads(text), path.as_posix())
```

Source: Phase 27/28/32 security scan helpers. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py; tools/bazel/phase32_blocker_register_triage.py]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Prose or evidence-status approval | Machine-readable maintainer input with explicit decision ids, owner identity, timestamp, rationale, refs, and typed decision axis | Phase 27 and reinforced by Phase 33 context | Planner should create tasks around JSON schema/normalization, not prose reports. [VERIFIED: .planning/milestones/v1.2-phases/27-retained-code-and-maintainer-acceptance-decisions/27-01-SUMMARY.md; .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md] |
| Phase 28 consumes Phase 26/27 directly | Phase 33 consumes Phase 32 v1.3 blocker handoff first | Phase 32 completed 2026-07-03 | Planner should wire Phase 31/26/27/28 quick chain before Phase 32, then Phase 33 reads Phase 32 only for decision inputs. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-VERIFICATION.md] |
| Demotion as a final readiness side effect | Demotion as separate explicit authorization data evaluated later | Phase 28 and v1.3 requirements | Phase 33 may record demotion approval/rejection, but Phase 34 proves whether it opens. [VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json; .planning/REQUIREMENTS.md] |

**Deprecated/outdated:**
- Any `demotion_allowed` output marker in Phase 33 generated artifacts is unsafe and should be rejected. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase32_blocker_register_triage.py]
- Human-readable reports as the only approval surface are out of scope; JSON records are authoritative. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|

All claims in this research were verified against local project files or command output; no user-confirmation-only assumptions are required before planning. [VERIFIED: sources listed below]

## Open Questions (RESOLVED)

1. **Exact Phase 33 enum spellings**
   - What we know: The user allowed the agent to choose exact enum spellings where not already locked by Phase 27/28/32 contracts. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
   - Resolution: Exact enum spelling will be defined in the Phase 33 contract and RED tests before implementation logic. The contract is the checked-in authority for `decision_type`, `decision_value`, invalid states, and generated artifact names. [VERIFIED: adjacent contract-first pattern in Phase 27/28/32 tests]

2. **One script or split helpers**
   - What we know: The user allows either one script with subcommands or a verifier plus helper functions. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md]
   - Resolution: Implementation starts as one verifier script with named pure helpers for contract validation, source-ref parsing, decision normalization, security scanning, artifact writing, and wiring checks. Split into helper modules only if reviewability requires it after those named helpers exist. [VERIFIED: tools/bazel/BUILD.bazel pattern; standards/core/code-shape.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---:|---|---|
| Python 3 | Phase 33 verifier/tests | yes | 3.14.4 | None needed; repo requires Python 3.8+. [VERIFIED: python3 --version; AGENTS.md] |
| Bazel | `//tools/bazel:phase33_verify*` targets | yes | 9.1.1 | Direct Python commands can validate while wiring is being added. [VERIFIED: bazel --version; tools/bazel/BUILD.bazel] |
| `just` | `just phase33-verify` developer facade | yes | 1.48.0 | Bazel labels can run directly. [VERIFIED: just --version; justfile] |
| Cargo | Rust pre-commit sequence if committing | yes | 1.91.1 | None for commit gate; Phase 33 code itself is Python. [VERIFIED: cargo --version; user-provided AGENTS.md instructions] |
| Git | status/diff/commit and GSD commit helper | yes | 2.53.0 | None. [VERIFIED: git --version] |

**Missing dependencies with no fallback:** None. [VERIFIED: command availability audit]

**Missing dependencies with fallback:** None. [VERIFIED: command availability audit]

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | Python `unittest` plus Bazel `shell_binary` and `just` wrappers. [VERIFIED: tools/bazel/phase32_blocker_register_triage_test.py; tools/bazel/BUILD.bazel; justfile] |
| Config file | No dedicated Python unit-test config for phase verifier tests; direct test scripts are invoked by `rust_workflow.sh`. [VERIFIED: tools/bazel/rust_workflow.sh] |
| Quick run command | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` after test file exists. [VERIFIED: adjacent phase test command pattern] |
| Full suite command | `just phase33-verify` after wiring exists. [VERIFIED: adjacent just recipe pattern] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| DECIDE-01 | Retained-code accept/reject/exception decisions require explicit maintainer metadata, residual-risk rationale, owner signoff, valid source row refs, and hard-blocker rejection. | unit + integration | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` | No; Wave 0. [VERIFIED: no phase33 test file found] |
| DECIDE-02 | Readiness approve/block handoff consumes Phase 32 rows and approved exception/residual-risk decisions; approval fails with unresolved uncovered blockers. | unit + integration | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` | No; Wave 0. [VERIFIED: no phase33 test file found] |
| DECIDE-03 | Demotion approve/reject handoff is separate and cannot be inferred from evidence, readiness, exceptions, or retained-code decisions. | unit + integration | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` | No; Wave 0. [VERIFIED: no phase33 test file found] |

### Sampling Rate

- **Per task commit:** `python3 -m py_compile tools/bazel/phase33_maintainer_decision_inputs.py tools/bazel/phase33_maintainer_decision_inputs_test.py` and `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q`. [VERIFIED: Phase 32 summary verification commands]
- **Per wave merge:** `bazel run //tools/bazel:phase33_verify_tests` and `bazel run //tools/bazel:phase33_verify`. [VERIFIED: tools/bazel/BUILD.bazel adjacent pattern]
- **Phase gate:** `just phase33-verify`, `python3 tools/bazel/phase33_maintainer_decision_inputs.py --security-only`, `python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only`, `git diff --check`, and Rust pre-commit sequence before any commit. [VERIFIED: Phase 32 summary; user-provided AGENTS.md instructions]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` - covers DECIDE-01, DECIDE-02, DECIDE-03. [VERIFIED: no phase33 contract exists]
- [ ] `tools/bazel/phase33_maintainer_decision_inputs.py` - verifier implementation. [VERIFIED: no phase33 verifier exists]
- [ ] `tools/bazel/phase33_maintainer_decision_inputs_test.py` - unit/integration regression coverage. [VERIFIED: no phase33 test exists]
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring for `phase33_verify`, `phase33_verify_tests`, and `phase33-verify`. [VERIFIED: current files contain phase32 but no phase33 wiring]

## Security Domain

Security enforcement is enabled by default because `.planning/config.json` does not set `security_enforcement: false`. [VERIFIED: .planning/config.json]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---:|---|
| V2 Authentication | no | Phase 33 stores maintainer identity references, but it does not implement authentication. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md] |
| V3 Session Management | no | No sessions, cookies, or network service are introduced. [VERIFIED: phase scope and existing local verifier pattern] |
| V4 Access Control | yes | Require explicit decision type/source row matching and owner/maintainer identity refs before recording accepted decisions. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md] |
| V5 Input Validation | yes | Strict JSON object/list/string validation, enum validation, ISO UTC timestamps, repo-relative refs, lifecycle checks, duplicate id checks, and fail-closed unknown values. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py; tools/bazel/phase32_blocker_register_triage.py] |
| V6 Cryptography | no | Phase 33 should not implement cryptography; it should preserve evidence/artifact refs and avoid private key/token material. [VERIFIED: .planning/REQUIREMENTS.md] |

### Known Threat Patterns for Phase 33

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Secret leakage through maintainer input fields or text | Information Disclosure | Scan JSON field names and text for tokens, private keys, raw dumps, raw service payloads, and signing material. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase32_blocker_register_triage.py] |
| Path traversal or symlink output escape | Tampering | Enforce repo-relative paths under expected roots and reject symlink output directories. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; tools/bazel/phase28_final_readiness_packet.py] |
| Stale lifecycle or wrong source row replay | Spoofing / Tampering | Validate Phase 32 handoff lifecycle id and resolve every source row ref against canonical Phase 32 row ids. [VERIFIED: tools/bazel/phase32_blocker_register_triage.py; .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md] |
| Approval overclaim in generated reports | Repudiation / Elevation of Privilege | Make JSON rows authoritative, derive Markdown from rows, and scan for forbidden approval markers such as `demotion_allowed`. [VERIFIED: tools/bazel/phase32_blocker_register_triage.py; tools/bazel/phase28_final_readiness_packet.py] |
| Broad exception covers unrelated blockers | Elevation of Privilege | Require exact source row refs and affected gate coverage for approved exceptions. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md` - locked Phase 33 decisions, scope, artifacts, and discretion. [VERIFIED]
- `.planning/REQUIREMENTS.md` - DECIDE-01, DECIDE-02, DECIDE-03 and v1.3 scope. [VERIFIED]
- `.planning/ROADMAP.md` - Phase 33 success criteria and Phase 34/35 boundaries. [VERIFIED]
- `.planning/STATE.md` - current milestone state and fail-closed demotion decisions. [VERIFIED]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/index.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/verification.md`, `standards/core/testing.md`, `standards/core/operability.md`, `standards/core/local-guidance.md`, `standards/languages/rust.md` - repo and Bright Builds constraints. [VERIFIED]
- `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json` and `tools/bazel/phase27_retained_code_acceptance_decisions.py` - retained-code/residual-risk/exception decision precedent. [VERIFIED]
- `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` and `tools/bazel/phase28_final_readiness_packet.py` - readiness/demotion fail-closed precedent. [VERIFIED]
- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` and `tools/bazel/phase32_blocker_register_triage.py` - Phase 32 blocker handoff contract and implementation. [VERIFIED]
- `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`, `tools/bazel/phase28_final_readiness_packet_test.py`, `tools/bazel/phase32_blocker_register_triage_test.py` - regression examples. [VERIFIED]
- `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - build/test/developer workflow wiring patterns. [VERIFIED]

### Secondary (MEDIUM confidence)

- `.planning/phases/32-blocker-register-and-evidence-triage/32-01-SUMMARY.md` and `32-VERIFICATION.md` - executed Phase 32 behavior and verified generated outputs. [VERIFIED]
- `.planning/milestones/v1.2-phases/27-retained-code-and-maintainer-acceptance-decisions/27-01-SUMMARY.md` - executed Phase 27 output summary. [VERIFIED]
- `.planning/milestones/v1.2-phases/28-final-readiness-packet-and-demotion-gate/28-01-SUMMARY.md` - executed Phase 28 output summary. [VERIFIED]
- `build/ci-evidence/phase32/*` - current generated handoff shape and row counts from prior verification. [VERIFIED]

### Tertiary (LOW confidence)

- None. No external web or unverified ecosystem sources were needed because this phase is codebase-only implementation research. [VERIFIED: thinking-models-research.md codebase-only guidance]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - based on checked-in adjacent verifier scripts and local tool availability. [VERIFIED: tools/bazel/*phase27*; tools/bazel/*phase28*; tools/bazel/*phase32*; command availability audit]
- Architecture: HIGH - Phase 33 context locks the Phase 32 handoff boundary, and adjacent phases provide the exact verifier/contract/wiring pattern. [VERIFIED: .planning/phases/33-maintainer-decision-inputs/33-CONTEXT.md; tools/bazel/BUILD.bazel]
- Pitfalls: HIGH - pitfalls are directly encoded in Phase 27/28/32 contracts and tests. [VERIFIED: phase27/28/32 contract and test files]

**Research date:** 2026-07-04
**Valid until:** 2026-08-03 for local codebase patterns; re-check if Phase 34/35 contracts are implemented before Phase 33 planning resumes. [VERIFIED: current roadmap state]
