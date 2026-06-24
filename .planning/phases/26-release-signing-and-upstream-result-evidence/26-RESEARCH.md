# Phase 26: Release, Signing, and Upstream Result Evidence - Research

**Researched:** 2026-06-24
**Domain:** Python/Bazel release evidence validation, secret-safe signing metadata, and upstream cutover row normalization
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

Copied verbatim from `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

### Locked Decisions

## Implementation Decisions

### Release Evidence Input Model
- **D-01:** Treat `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json`, `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`, and `tools/bazel/manifests/phase20_release_environment_inputs.template.json` as the canonical release/signing/provenance sources. Phase 26 may add a v1.2 execution wrapper/schema, but it must not silently redefine the Phase 17 or Phase 20 release row IDs.
- **D-02:** Require every Phase 20 release evidence row to be represented by the release-manager input packet. Missing, duplicate, unknown, or row-ID-drifted release evidence must fail validation or remain blocked.
- **D-03:** Accept release evidence as sanitized release metadata plus artifact references, not raw firmware payloads, signing payload bytes, private keys, private certificates, credentials, raw logs, or binary dumps.
- **D-04:** Passed release rows require artifact digests, build input identity, signing identity reference, provenance references, comparison references, retention references, verification outcome, operator, timestamp, and release run identity where the source contract requires those fields.

### Signing, Provenance, and Secret Handling
- **D-05:** Signing identity is reference-only: key fingerprint, signing authority, certificate chain reference, or external release key evidence may be retained, but private key material, raw key bytes, signing payload bytes, and credential values must be rejected.
- **D-06:** Treat `approved-release-run` and `external-release-key-evidence` as eligible proof classes for pass status. `template-only`, `local-smoke`, `pending-release-input`, `release-run-required`, `external-signing-required`, and `blocked-signing-key-unavailable` must not pass without explicit exception metadata.
- **D-07:** Reject or block secret-tainted evidence before writing retained outputs. Redaction failure is a hard blocker and cannot be converted into a normal exception approval.
- **D-08:** Keep release proof distinct from simulator, hardware/media/safety, live-service, retained-code, residual-risk, final readiness, and demotion approval. Release pass status must not imply those other gates are accepted.

### Upstream Result Row Coverage
- **D-09:** Treat `tools/bazel/manifests/phase18_cutover_review_contract.json` as the canonical upstream result requirement list for final cutover gate rows.
- **D-10:** Phase 26 should produce or validate upstream rows for every required gate family: CI, simulator, hardware/media/safety, live-service, release/signing, retained-code, residual-risk, maintainer-decision/final-readiness, and reference-demotion status where the Phase 18 contract expects a row.
- **D-11:** Every upstream row must name requirement IDs, owning phase or gate, source lifecycle ID or lifecycle status, evidence family, criterion ID, evidence refs, artifact refs, status, failure reason, redaction status, source-ref status, exception status, maintainer state, and generated timestamp.
- **D-12:** Missing, stale, lifecycle-mismatched, source-ref-invalid, failed, blocked, secret-tainted, schema-invalid, or overclaiming rows remain blocked until corrected or explicitly exception-approved where the source contract allows exceptions.
- **D-13:** Retained-code acceptance, residual-risk review, maintainer-decision, and reference-demotion rows can be present as blocked, pending, or not-required scaffolding for later phases, but Phase 26 must not approve those decisions.

### Retained Outputs and Integration
- **D-14:** Retained Phase 26 outputs should live under `build/ci-evidence/phase26`, following the Phase 23-25 execution conventions.
- **D-15:** Store a normalized release evidence summary, upstream result row table, release run manifest, redaction/provenance summary, source contract snapshot or refs, operator input template, artifact reference summary, and machine-readable upstream result manifest for later acceptance phases.
- **D-16:** Keep generated evidence under ignored build output directories. Repo-tracked artifacts should be source contracts, input templates, verifier code, tests, Bazel/just wiring, and GSD planning artifacts.

### Verification
- **D-17:** Add Phase 26 verification as a narrow extension around existing Bazel/Python evidence tooling, with root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` wiring consistent with Phases 20, 23, 24, and 25.
- **D-18:** Include focused Python tests for release row coverage, status/proof-class normalization, signing identity redaction, artifact digest requirements, provenance/comparison/retention metadata, upstream row schema, exception eligibility, stale/lifecycle/source-ref blockers, secret/overclaim guards, retained output writing, and wiring checks.
- **D-19:** Phase 26 quick verification should pass from checked-in safe fixtures and blocked placeholders while clearly distinguishing fixture/template evidence from real release-environment proof.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 26 release input template, release evidence manifest, upstream result manifest, normalized summaries, and row table, provided the names are explicit, tested, and stable for Phases 27 and 28.
- Decide whether Phase 26 should be one cohesive verifier or a thin orchestrator around Phase 20 plus a separate upstream-row validator. Prefer the smallest design that keeps release evidence and upstream row validation clear.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless research finds a real dependency split.

### Deferred Ideas (OUT OF SCOPE)

- Retained-code acceptance, residual-risk rationale, exception approval, and maintainer final decision inputs belong to Phase 27.
- Final cutover readiness packet generation, default blocked readiness, and explicit reference-demotion approval belong to Phase 28.
- Automatic reference demotion remains out of scope unless maintainers explicitly approve it in the final readiness phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| EVID-04 | Release manager can supply release/signing/provenance evidence from real release-environment outputs without exposing private keys or secrets. [VERIFIED: `.planning/REQUIREMENTS.md`] | Phase 20 already defines 18 release rows, required pass metadata, allowed ref roots, forbidden secret fields, and quick retained release artifacts that Phase 26 should reuse and tighten. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`] |
| ACPT-01 | Maintainer can review upstream result rows for every required cutover gate. [VERIFIED: `.planning/REQUIREMENTS.md`] | Phase 18 defines nine upstream result criteria and the row fields/status policies that Phase 26 must normalize into an inspectable table. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/phase18_cutover_review.py`] |
</phase_requirements>

## Summary

Phase 26 should be planned as one cohesive standard-library Python verifier with a new Phase 26 contract, focused unit tests, Bazel shell targets, `rust_workflow.sh` dispatch, and `just phase26-verify` facade. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/BUILD.bazel`; `justfile`] The verifier should load canonical Phase 17/20 release contracts and the Phase 18 upstream requirement list instead of redefining row IDs, status vocabularies, or final-gate criterion IDs. [VERIFIED: `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json`; `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

The release half should extend Phase 20 behavior, not replace it: require all 18 Phase 20 rows, reject missing/duplicate/unknown rows, require digest/provenance/comparison/retention metadata before pass, and scan inputs before retaining outputs. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase20_release_candidate_artifacts_test.py`] Phase 26 must add the user-locked stricter proof-class rule: only `approved-release-run` and `external-release-key-evidence` can satisfy Phase 26 pass semantics, even though the older Phase 20 verifier also treats `release-candidate` as an approved pass proof class. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts.py`]

The upstream half should normalize the Phase 18 criterion list into a Phase 26-owned row table. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`] Existing Phase 23-25 wrappers emit compact upstream rows, but those rows are not directly Phase 18-compatible because Phase 18 expects fields such as `owning_phase`, `source_lifecycle_id`, `failure_reason`, and `generated_at_utc`, and it uses `final-live-network-transfer-evidence` where Phase 25 emits `final-live-service-evidence`. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

**Primary recommendation:** Build `tools/bazel/phase26_release_signing_upstream_evidence.py` plus `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` as a thin, fail-closed normalizer over Phase 20 release evidence and Phase 18 upstream criteria, writing blocked quick outputs under `build/ci-evidence/phase26` and rejecting secret-tainted release inputs before any retained file is written. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review.py`]

## Project Constraints (from AGENTS.md)

- Planning and implementation must follow AGENTS.md, AGENTS.bright-builds.md, standards-overrides.md, and relevant managed standards pages before plan/review/implementation/audit work. [VERIFIED: `AGENTS.md`; `AGENTS.bright-builds.md`; `standards/index.md`]
- Bright Builds Rules apply with no active local override beyond the placeholder table in `standards-overrides.md`. [VERIFIED: `standards-overrides.md`]
- Use functional core / imperative shell for business logic: keep row normalization, status aggregation, secret detection, and schema checks as pure data-in/data-out helpers around thin file I/O. [VERIFIED: `standards/core/architecture.md`]
- Parse raw JSON evidence at boundaries into validated domain rows before deeper normalization. [VERIFIED: `standards/core/architecture.md`]
- Make illegal states unrepresentable where practical by normalizing explicit status/proof-class/ref-state combinations instead of passing loose dictionaries everywhere. [VERIFIED: `standards/core/architecture.md`]
- Prefer early returns and readable guard helpers; internal optional names should use a visible `maybe_` prefix when practical. [VERIFIED: `standards/core/code-shape.md`; `AGENTS.md`]
- Do not hide substantial shell or Python logic inside strings; checked-in scripts should be rerunnable and diagnostic. [VERIFIED: `standards/core/code-shape.md`; `tools/bazel/phase18_cutover_review_test.py`]
- Unit tests must cover pure/business logic, keep one concern per test, and clearly delineate Arrange/Act/Assert when non-trivial. [VERIFIED: `standards/core/testing.md`; `AGENTS.md`]
- Before commit, run relevant repo-native verification for changed paths and do not commit if those checks fail. [VERIFIED: `standards/core/verification.md`; `AGENTS.md`]
- Repo workflow requires GSD-managed planning artifacts before file-changing work unless explicitly bypassed. [VERIFIED: `AGENTS.md`]
- Generated evidence outputs must stay under ignored build directories; root `.gitignore` ignores `/build*`, and `git check-ignore` confirms `build/ci-evidence/phase26/release-result-manifest.json` is ignored. [VERIFIED: `.gitignore`; `git check-ignore -v build/ci-evidence/phase26/release-result-manifest.json`]

## Standard Stack

### Core

| Tool/Library | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| Python standard library | Python 3.14.4 available locally | JSON parsing, path validation, regex-based secret guards, deterministic file writing, and `unittest` tests. | Existing Phase 17/18/20/23/24/25 evidence tools are Python scripts using standard-library modules such as `argparse`, `json`, `re`, `shutil`, `sys`, `datetime`, `pathlib`, and `typing`. [VERIFIED: `python3 --version`; `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`] |
| Bazel `shell_binary` targets | Bazel 9.1.1 available locally | Repository-native execution surface for phase verifiers and test runners. | Existing Phase 20, 23, 24, and 25 verification targets are `shell_binary` rules that dispatch through `tools/bazel/rust_workflow.sh`. [VERIFIED: `bazel --version`; `tools/bazel/BUILD.bazel`; `tools/bazel/rust_workflow.sh`] |
| `just` recipes | Just 1.48.0 available locally | Developer-facing phase verification facade. | Existing `phase20-verify`, `phase23-verify`, `phase24-verify`, and `phase25-verify` recipes run Bazel test labels before verifier labels. [VERIFIED: `just --version`; `justfile`] |
| JSON manifest contracts | Repo-local schema files | Canonical release row, upstream criterion, status vocabulary, and output contract source. | Phase 26 locked decisions make Phase 17/20/18 manifests canonical, and existing tools validate contracts from JSON before writing outputs. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`; `tools/bazel/manifests/phase18_cutover_review_contract.json`] |

### Supporting

| Tool/Library | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| jq | jq 1.7.1 available locally | Research-time inspection of JSON contract shape and generated output samples. | Useful for planner diagnostics, but Phase 26 implementation should not depend on jq because existing verifiers use Python stdlib JSON parsing. [VERIFIED: `jq --version`; `tools/bazel/phase20_release_candidate_artifacts.py`] |
| Phase 20 release verifier behavior | Repo script | Release row validation model and retained release output format. | Reuse the Phase 20 contract and validation semantics for row coverage, digest requirements, ref bounds, and secret guards; add Phase 26-specific stricter pass policy. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |
| Phase 18 cutover review behavior | Repo script | Upstream row shape, final criterion list, exception coverage, and demotion blocking semantics. | Use Phase 18 as the canonical final-gate criterion/status source and as the reference for what stale, missing, redaction-failed, or source-ref-invalid rows mean. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/manifests/phase18_cutover_review_contract.json`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Python stdlib validators | External `jsonschema` package | Do not add it for Phase 26; existing phase verifiers already use local typed helper checks and no project dependency pins are needed. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review.py`; `requirements.txt`] |
| One Phase 26 verifier | Separate release verifier plus upstream verifier | Use one verifier because the user asked for the smallest design that keeps release evidence and upstream row validation clear, and the phase has one shared output root and one workflow target. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |
| Phase 18 contract rewrite | Phase 26 compatibility/normalization layer | Do not rewrite Phase 18; D-09 locks it as canonical and D-13 defers retained-code/final-decision approval to later phases. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |

**Installation:**

No new package installation is required for the recommended implementation. [VERIFIED: existing evidence scripts use Python stdlib; `python3`, `bazel`, and `just` are available locally]

**Version verification:**

```bash
python3 --version   # Python 3.14.4
bazel --version     # bazel 9.1.1
just --version      # just 1.48.0
jq --version        # jq-1.7.1-apple
```

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── manifests/
│   └── phase26_release_signing_upstream_evidence_contract.json
├── phase26_release_signing_upstream_evidence.py
└── phase26_release_signing_upstream_evidence_test.py

build/ci-evidence/phase26/
├── release-upstream-run-manifest.json
├── normalized-release-evidence-summary.json
├── upstream-result-row-table.json
├── upstream-result-manifest.json
├── redaction-provenance-summary.json
├── artifact-reference-summary.json
├── operator-release-input-template.json
└── contract-snapshots/
    ├── phase18_cutover_review_contract.json
    ├── phase20_release_candidate_artifacts_contract.json
    └── phase20_release_environment_inputs.template.json
```

The source files should follow the Phase 23-25 pattern: a contract JSON, one Python verifier, one Python `unittest` file, a `tools/bazel/BUILD.bazel` source-ref filegroup plus `phase26_verify` and `phase26_verify_tests`, root `BUILD.bazel` docs filegroup/aliases, `rust_workflow.sh` dispatch cases, and `just phase26-verify`. [VERIFIED: `tools/bazel/BUILD.bazel`; `BUILD.bazel`; `tools/bazel/rust_workflow.sh`; `justfile`; `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`]

### Pattern 1: Canonical Contract Loading

**What:** Load Phase 20 release rows and Phase 18 upstream criteria from existing manifests, and put any Phase 26 additions in a separate v1.2 contract. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

**When to use:** Use for all row IDs, status vocabularies, required release metadata, upstream criterion IDs, and approved ref roots. [VERIFIED: `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

**Example:**

```python
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json")
PHASE20_CONTRACT = Path("tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json")
PHASE18_CONTRACT = Path("tools/bazel/manifests/phase18_cutover_review_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase26")
```

Source pattern: Phase 23-25 wrappers define their own contract plus source contract constants and a phase-specific output root. [VERIFIED: `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`]

### Pattern 2: Functional Core, Thin I/O Shell

**What:** Implement pure helpers for release row validation, aggregate status calculation, proof-class normalization, source row mapping, and upstream row rendering; keep file reads/writes and CLI argument dispatch thin. [VERIFIED: `standards/core/architecture.md`; `tools/bazel/phase20_release_candidate_artifacts.py`]

**When to use:** Use for any row transformation that tests must cover without relying on Bazel, external release environments, or real hardware/service outputs. [VERIFIED: `standards/core/testing.md`; `tools/bazel/phase20_release_candidate_artifacts_test.py`; `tools/bazel/phase25_live_service_evidence_execution_test.py`]

**Example:**

```python
def aggregate_release_status(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row["status"]) for row in rows}
    if "rejected-redaction" in statuses:
        return "rejected-redaction"
    if "rejected-overclaim" in statuses:
        return "rejected-overclaim"
    if "failed" in statuses:
        return "failed"
    if "blocked-signing-key-unavailable" in statuses:
        return "blocked-signing-key-unavailable"
    if "external-signing-required" in statuses:
        return "external-signing-required"
    if "pending-release-input" in statuses:
        return "pending-release-input"
    if statuses == {"passed"}:
        return "passed"
    return "blocked"
```

Source pattern: Phase 23-25 wrappers use aggregate status helpers that fail closed to `failed`, `blocked`, or `exception-requested` before `passed`. [VERIFIED: `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`]

### Pattern 3: Release Input Packet Validation

**What:** Accept a release-manager input JSON packet with an `evidence_rows` list matching every Phase 20 row ID. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/manifests/phase20_release_environment_inputs.template.json`]

**When to use:** Use for `--release-input`; quick mode should copy or generate a safe operator template and keep statuses blocked/pending when real release input is absent. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

**Example:**

```python
def load_release_input(root: Path, maybe_path: str | None) -> list[dict[str, Any]]:
    if maybe_path is None:
        return []
    data = load_json(root, Path(maybe_path))
    rows = data.get("evidence_rows")
    if not isinstance(rows, list):
        raise VerificationError("release input must contain an evidence_rows list")
    return rows
```

Source pattern: Phase 20 requires `evidence_rows`, rejects unknown and duplicate row IDs, and reports missing required row IDs. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase20_release_candidate_artifacts_test.py`]

### Pattern 4: Upstream Row Normalization Table

**What:** Generate a Phase 26 table keyed by Phase 18 `criterion_id`, with fields for canonical Phase 18 requirement data plus Phase 26-required lifecycle status, exception status, maintainer state, evidence refs, artifact refs, status, failure reason, redaction status, source-ref status, and generated timestamp. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

**When to use:** Use to bridge Phase 20 release evidence, Phase 23-25 direct rows, existing Phase 18/19 placeholders, and later Phase 27/28 acceptance consumers without mutating old contracts. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`]

**Example row shape:**

```json
{
  "criterion_id": "final-release-artifact-signing-evidence",
  "evidence_family": "release",
  "owning_phase": "20-release-candidate-artifact-production",
  "source_lifecycle_id": "20-2026-06-21T12-40-17",
  "source_lifecycle_status": "current",
  "status": "pending-release-input",
  "failure_reason": "Release-manager evidence input was not supplied.",
  "artifact_refs": ["build/ci-evidence/phase26/normalized-release-evidence-summary.json"],
  "evidence_refs": ["build/ci-evidence/phase20/release-result-manifest.json"],
  "exception_status": "none",
  "maintainer_state": "pending",
  "redaction_status": "passed",
  "source_ref_status": "passed",
  "generated_at_utc": "2026-06-24T00:00:00Z",
  "requirement_ids": ["EVID-04", "ACPT-01"]
}
```

The row shape above is a recommended Phase 26 output shape derived from D-11 and Phase 18 required fields; exact names are discretionary but must be explicit and tested. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

### Anti-Patterns to Avoid

- **Redefining Phase 20 row IDs:** Phase 20 has 18 row IDs, and D-01/D-02 require Phase 26 to preserve them. [VERIFIED: `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]
- **Treating compact Phase 23-25 rows as Phase 18 rows:** Phase 23-25 upstream rows lack required Phase 18 fields, and Phase 25 uses a criterion ID that differs from the Phase 18 canonical live-service criterion. [VERIFIED: `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`; `tools/bazel/phase18_cutover_review.py`]
- **Using release proof as final readiness:** D-08 forbids release pass status from implying simulator, hardware, live-service, retained-code, residual-risk, final-readiness, or demotion acceptance. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]
- **Writing retained outputs before secret scanning:** D-07 requires secret-tainted evidence to be rejected or blocked before retained outputs are written. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts.py`]
- **Committing generated evidence:** D-16 requires generated evidence under ignored build output directories, and `/build*` ignores `build/ci-evidence/phase26`. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `.gitignore`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Release row catalog | New Phase 26 release row IDs or surfaces | Phase 20 `rows` plus Phase 17 source refs | D-01/D-02 lock Phase 17/20 rows, and Phase 20 already has 18 rows covering firmware images, packages, signing identity, build input identity, retention, and comparison. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`] |
| Upstream final gate list | New final gate names | Phase 18 `upstream_result_requirements` and `final_demotion_criteria` | D-09 locks Phase 18 as canonical, and Phase 18 currently defines nine upstream criteria. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`] |
| Signing | Key handling, signing, certificate parsing, payload signing, or private-key inspection | Reference-only signing identity fields and external evidence refs | D-05 makes signing identity reference-only and forbids private key material, raw key bytes, signing payload bytes, and credential values. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |
| Secret detection vocabulary | A new, smaller secret list | Union of Phase 20 release forbidden fields plus Phase 18/23/24/25 secret markers relevant to release/signing/live artifacts | Existing verifiers already reject private keys, tokens, credentials, payload bytes, crash dumps, and other sensitive markers. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase25_live_service_evidence_execution.py`] |
| Artifact ref containment | Ad hoc path string checks | Existing `require_repo_relative_under` / `validate_ref` style checks and explicit allowed roots | Phase 20 and Phase 23-25 reject absolute paths, traversal, unsafe external refs, and symlink escape output roots. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase20_release_candidate_artifacts_test.py`; `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`] |
| Final decision / demotion policy | Any Phase 26 approval logic | Blocked/pending/not-required scaffolding only | D-13 defers retained-code, residual-risk, maintainer-decision, and reference-demotion approvals to later phases. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |

**Key insight:** Phase 26 is a normalization and evidence-retention bridge, not a new release/signing authority or final readiness engine. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `.planning/ROADMAP.md`]

## Common Pitfalls

### Pitfall 1: Proof-Class Policy Drift

**What goes wrong:** A planner copies Phase 20's `APPROVED_PASS_PROOF_CLASSES` and lets `release-candidate` pass Phase 26. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`]

**Why it happens:** Phase 20 allows `release-candidate`, `approved-release-run`, and `external-release-key-evidence` for passed rows, while Phase 26 D-06 only names `approved-release-run` and `external-release-key-evidence` as eligible pass proof classes. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

**How to avoid:** Validate with Phase 20 semantics first, then apply a Phase 26 stricter pass filter before setting any release upstream row to `passed`. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

**Warning signs:** Tests only reject `local-smoke` and `template-only`, but do not test `release-candidate` under Phase 26. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts_test.py`]

### Pitfall 2: Upstream Criterion ID Mismatch

**What goes wrong:** Phase 26 treats `final-live-service-evidence` as canonical because Phase 25 emits it. [VERIFIED: `tools/bazel/phase25_live_service_evidence_execution.py`]

**Why it happens:** Phase 18 expects `final-live-network-transfer-evidence`, but Phase 25 writes `final-live-service-evidence`. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/phase25_live_service_evidence_execution.py`]

**How to avoid:** Build an explicit compatibility map from Phase 25's compact row to Phase 18's canonical criterion and test unknown or unmapped criterion IDs as blocked/schema-invalid. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`]

**Warning signs:** The Phase 26 upstream table has fewer than the nine Phase 18 criteria or has both live-service criterion names as separate passing gates. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`]

### Pitfall 3: Direct Phase 18 Compatibility Assumption

**What goes wrong:** The plan assumes Phase 23-25 compact upstream rows can be fed directly into Phase 18. [VERIFIED: `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`]

**Why it happens:** Phase 23-25 rows include `criterion_id`, `evidence_family`, `manifest_ref`, `status`, `redaction_status`, `source_ref_status`, and requirement IDs, but Phase 18 additionally requires `owning_phase`, `source_lifecycle_id`, `failure_reason`, `generated_at_utc`, and specific approved roots. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

**How to avoid:** Make Phase 26 own a normalized upstream row table and a separate machine-readable manifest for Phase 27/28, while preserving Phase 18 canonical criterion IDs. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

**Warning signs:** Phase 26 tests only check that compact prior rows exist, not that normalized rows include D-11 fields. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

### Pitfall 4: Secret-Tainted Retained Outputs

**What goes wrong:** A release input with a private key marker, token-like field name, raw firmware payload field, or signing payload bytes is copied into retained output before rejection. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

**Why it happens:** Release evidence naturally touches signing and provenance metadata, but D-03/D-05/D-07 allow only sanitized references. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

**How to avoid:** Run forbidden text and forbidden field checks on raw input text and parsed JSON before output directory creation or retained writes. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase23_simulator_evidence_execution.py`]

**Warning signs:** A test mutates generated output to include secrets but does not test input rejection before output writing. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`; `tools/bazel/phase20_release_candidate_artifacts_test.py`]

### Pitfall 5: Output Root Escape

**What goes wrong:** Quick mode deletes or writes outside `build/ci-evidence/phase26` through `..` or a symlinked output root. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts_test.py`]

**Why it happens:** Phase 20 and Phase 23-25 quick modes remove existing output roots before writing new files. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase25_live_service_evidence_execution.py`]

**How to avoid:** Use the Phase 20 resolved-output-dir pattern or Phase 23-25 repo-relative output guard and add symlink/traversal regression tests. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase20_release_candidate_artifacts_test.py`]

**Warning signs:** The verifier calls `shutil.rmtree(output_root)` before resolving and checking containment. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts_test.py`]

### Pitfall 6: Overclaiming Later Decisions

**What goes wrong:** Phase 26 outputs say retained code is accepted, final readiness is approved, or reference demotion is allowed. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

**Why it happens:** Phase 18/21/22 tooling already uses final-readiness/demotion language, and it is easy to confuse row availability with maintainer approval. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase22_metadata_reconciliation.py`]

**How to avoid:** Use maintainer fields such as `maintainer_state: pending` and `exception_status: none` for Phase 26 scaffolding, and reject local-proof or demotion-approval phrases in retained outputs. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase23_simulator_evidence_execution.py`]

**Warning signs:** Phase 26 quick output includes `demotion_allowed: true`, `final approval complete`, or accepted retained-code wording. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`]

## Code Examples

Verified patterns from repo sources:

### Safe Release Input Boundary

```python
def load_release_input(root: Path, maybe_path: str | None) -> list[dict[str, Any]]:
    if maybe_path is None:
        return []
    raw_text = read_text(root, Path(maybe_path))
    reject_forbidden_text(Path(maybe_path), raw_text)
    data = json.loads(raw_text)
    reject_forbidden_field_names(data, str(maybe_path))
    rows = data.get("evidence_rows")
    if not isinstance(rows, list):
        raise VerificationError("release input must contain an evidence_rows list")
    return rows
```

Source pattern: Phase 20 scans release input text and parsed JSON before validating `evidence_rows`. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`]

### Upstream Missing Row Fails Closed

```python
if not rows and requirement["result_required"] is False:
    rows = [synthetic_row("not-required", "decision-owned upstream result not required")]
elif not rows:
    rows = [synthetic_row("missing", "upstream result evidence is missing")]
```

Source pattern: Phase 18 synthesizes `missing` rows for required upstream results and `not-required` rows for decision-owned requirements. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `build/ci-evidence/phase18/upstream-result-consumption.json`]

### Quick Placeholder Is Blocked, Not Proof

```python
upstream_row = {
    "criterion_id": "final-simulator-evidence",
    "evidence_family": "simulator",
    "status": run_status,
    "redaction_status": "passed",
    "source_ref_status": "passed",
    "requirement_ids": ["EVID-01"],
}
```

Source pattern: Phase 23 quick mode writes blocked placeholder evidence with `real_simulator_evidence_supplied` false and redaction/source-ref status passed. [VERIFIED: `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase23_simulator_evidence_execution_test.py`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| v1.1 contracts described evidence capability and placeholders. | v1.2 wrappers accept real external evidence packets while quick mode emits blocked placeholders. | Phases 23-25 in v1.2. [VERIFIED: `.planning/ROADMAP.md`; `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`] | Phase 26 should follow the v1.2 wrapper style, not merely validate static v1.1 contracts. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |
| Phase 20 release production wrote Phase 20 retained release outputs. | Phase 26 should retain Phase 26 review/normalization outputs while using Phase 20 release contracts as sources. | Phase 26 context decision D-14/D-15. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] | Do not mix Phase 26 upstream row review artifacts into `build/ci-evidence/phase20`. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-DISCUSSION-LOG.md`] |
| Phase 18 consumed upstream rows only when supplied. | Phase 26 should make every required upstream row inspectable, including blocked or not-required scaffolding for later phases. | Phase 26 context decision D-10/D-13. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] | Planner must include row coverage tests for all nine Phase 18 criteria. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`] |

**Deprecated/outdated:**

- Treating local smoke/template evidence as passing release proof is out of scope for Phase 26 pass status. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts_test.py`]
- Assuming reference demotion follows from green evidence is explicitly out of scope. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | No unverified factual claims were intentionally included; recommendations are derived from repo contracts and context loaded in this research session. | All sections | — |

## Open Questions

1. **Should Phase 26 emit a Phase 18-compatible `upstream_result_packet` in addition to its Phase 26-native manifest?** [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]
   - What we know: Phase 18 requires `upstream_result_packet.phase` to equal `18-retained-code-acceptance-and-cutover-review`, requires the Phase 18 lifecycle ID, and validates artifact refs against roots from Phase 18 requirements. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]
   - What's unclear: Phase 26 is scoped to produce rows for Phase 27/28, but Phase 18's approved roots for simulator/hardware/live still point at Phase 19 aggregate outputs rather than Phase 23-25 v1.2 output roots. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]
   - Recommendation: Plan a Phase 26-native upstream manifest as the required output; add an optional compatibility view only if it can pass Phase 18 validation without lying about owning phase, lifecycle, or approved roots. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`]

2. **Should Phase 26 import Phase 20/18 verifier functions or duplicate only the minimal contract checks?** [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review.py`]
   - What we know: Existing tools are standalone scripts but have import-safe `if __name__ == "__main__"` guards. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review.py`]
   - What's unclear: The codebase does not currently expose these verifiers as a shared library package. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/BUILD.bazel`]
   - Recommendation: Prefer loading canonical JSON contracts and reusing small local helpers/patterns over importing the whole Phase 18 script; tests should prevent drift from Phase 18/20 contracts. [VERIFIED: `standards/core/architecture.md`; `tools/bazel/phase20_release_candidate_artifacts_test.py`; `tools/bazel/phase18_cutover_review_test.py`]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 26 verifier and tests | Yes | 3.14.4 | None needed; repo requires Python 3.8+ for tooling. [VERIFIED: `python3 --version`; `AGENTS.md`] |
| Bazel | `phase26_verify` / `phase26_verify_tests` targets | Yes | 9.1.1 | Direct `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` and verifier commands during local debugging. [VERIFIED: `bazel --version`; `tools/bazel/BUILD.bazel`] |
| just | Developer facade | Yes | 1.48.0 | Run Bazel labels directly. [VERIFIED: `just --version`; `justfile`] |
| jq | Research/debug inspection only | Yes | jq-1.7.1-apple | Python `json` module. [VERIFIED: `jq --version`; `tools/bazel/phase20_release_candidate_artifacts.py`] |

**Missing dependencies with no fallback:** None found for research/planning and the recommended local verification path. [VERIFIED: environment probes above]

**Missing dependencies with fallback:** None found. [VERIFIED: environment probes above]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` invoked as script. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts_test.py`; `tools/bazel/phase25_live_service_evidence_execution_test.py`] |
| Config file | None for these phase-tool unit tests; tests are plain Python files under `tools/bazel/`. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts_test.py`; `tools/bazel/BUILD.bazel`] |
| Quick run command | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` [VERIFIED: existing Phase 20/23/24/25 test command pattern in `tools/bazel/rust_workflow.sh`] |
| Full suite command | `just phase26-verify` after wiring. [VERIFIED: `justfile`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| EVID-04 | Complete release-manager input must cover all 18 Phase 20 rows and reject missing, duplicate, unknown, or row-ID-drifted release rows. [VERIFIED: `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] | unit | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - Wave 0 |
| EVID-04 | Passed release rows must include digests, build input identity, signing identity refs where required, provenance, comparison, retention, operator, timestamp, and release run identity. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts.py`] | unit | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - Wave 0 |
| EVID-04 | Secret-tainted release input must fail before retained outputs are written. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts_test.py`] | unit/security | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - Wave 0 |
| ACPT-01 | Upstream result row table must include every Phase 18 criterion and required D-11 fields. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] | unit | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - Wave 0 |
| ACPT-01 | Missing, stale, source-ref-invalid, failed, blocked, secret-tainted, schema-invalid, and overclaiming rows must remain blocked unless exception-coverable. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`] | unit/security | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - Wave 0 |
| EVID-04 / ACPT-01 | Bazel, rust workflow, and just wiring expose tests before verifier. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts_test.py`; `justfile`] | wiring | `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --wiring-only` | No - Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` plus the changed-path verifier mode, such as `--contract-only`, `--security-only`, or `--wiring-only`. [VERIFIED: `standards/core/verification.md`; existing phase plan patterns in `.planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-PLAN.md`]
- **Per wave merge:** `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26` and `just phase26-verify`. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/rust_workflow.sh`; `justfile`]
- **Phase gate:** `just phase26-verify` plus direct Python commands if Bazel is unavailable. [VERIFIED: environment probes; `justfile`]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` - defines Phase 26 output root, source contract refs, expected generated artifacts, release proof policy, and upstream row schema. [VERIFIED: no Phase 26 files currently exist under `tools/bazel`; `find tools/bazel -maxdepth 2 -type f -name '*phase26*'`]
- [ ] `tools/bazel/phase26_release_signing_upstream_evidence.py` - verifier/orchestrator with `--contract-only`, `--security-only`, `--wiring-only`, `--quick`, `--release-input`, and `--output-dir`. [VERIFIED: no Phase 26 files currently exist under `tools/bazel`]
- [ ] `tools/bazel/phase26_release_signing_upstream_evidence_test.py` - focused unit/wiring/security tests. [VERIFIED: no Phase 26 files currently exist under `tools/bazel`]
- [ ] Bazel/root/just/rust workflow entries for Phase 26. [VERIFIED: `rg -n "phase26|Phase 26" BUILD.bazel tools/bazel/BUILD.bazel tools/bazel/rust_workflow.sh justfile` found no Phase 26 wiring]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | No | Phase 26 does not authenticate users; it validates local/offline evidence packets. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |
| V3 Session Management | No | Phase 26 has no web session surface. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |
| V4 Access Control | Yes, for evidence refs and output roots | Accept only safe repo-relative refs under allowed output roots or explicit external refs; reject traversal and unsafe external roots. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`] |
| V5 Input Validation | Yes | Parse JSON at boundaries, require complete row sets, validate status/proof vocabularies, reject unknown IDs, and validate timestamps/refs. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review.py`] |
| V6 Cryptography | Yes, but reference-only | Never perform signing or retain private key material; require artifact SHA-256 digest metadata and signing identity references only. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts.py`] |

### Known Threat Patterns for Phase 26

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Private signing key or credential included in release input | Information Disclosure | Reject forbidden field names and private-key/token/credential text before retained output writes. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts.py`] |
| Path traversal or symlink output deletion | Tampering / Information Disclosure | Resolve output dir under `build/ci-evidence/phase26`, reject `..`, reject symlink escape, and test victim directories survive. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase20_release_candidate_artifacts_test.py`] |
| Local quick placeholder overclaims release approval | Spoofing / Elevation of Privilege | Quick mode writes blocked/pending statuses and redaction summaries; tests reject demotion/final-approval overclaim phrases. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase18_cutover_review_test.py`] |
| Upstream row lifecycle mismatch | Tampering | Preserve expected source lifecycle IDs and mark stale/mismatched rows blocked/schema-invalid. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`] |
| Exception laundering of redaction failure | Elevation of Privilege | Treat redaction failure as hard blocker that cannot become a normal exception approval. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md` - locked Phase 26 decisions, canonical refs, scope, outputs, and verification constraints.
- `.planning/REQUIREMENTS.md` - EVID-04 and ACPT-01 requirement definitions and traceability.
- `.planning/ROADMAP.md` - Phase 26 success criteria, dependency on Phase 25, and v1.2 milestone scope.
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/testing.md`, `standards/core/verification.md` - repo and Bright Builds planning/implementation constraints.
- `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` - Phase 20 release row IDs, status/proof vocabularies, pass metadata requirements, allowed ref roots, and release source refs.
- `tools/bazel/manifests/phase20_release_environment_inputs.template.json` - 18-row release-manager input template.
- `tools/bazel/phase20_release_candidate_artifacts.py` and `tools/bazel/phase20_release_candidate_artifacts_test.py` - existing release evidence validation, retained output, secret guard, output-root guard, and wiring test patterns.
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - canonical final cutover criteria and upstream result requirement list.
- `tools/bazel/phase18_cutover_review.py` and `tools/bazel/phase18_cutover_review_test.py` - upstream row validation, missing/not-required synthesis, exception coverage, final demotion blocking, and security-overclaim checks.
- `tools/bazel/phase23_simulator_evidence_execution.py`, `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`, and `tools/bazel/phase25_live_service_evidence_execution.py` - v1.2 evidence wrapper, quick placeholder, retained output, and compact upstream row patterns.
- `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - current verification wiring conventions.

### Secondary (MEDIUM confidence)

- `build/ci-evidence/phase18`, `build/ci-evidence/phase20`, `build/ci-evidence/phase23`, `build/ci-evidence/phase24`, and `build/ci-evidence/phase25` generated output samples - local retained output shape and quick-placeholder status examples.

### Tertiary (LOW confidence)

- None used.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - verified from local scripts, Bazel/just wiring, and local tool probes.
- Architecture: HIGH - follows repeated Phase 20/23/24/25 local patterns and locked Phase 26 decisions.
- Pitfalls: HIGH - derived from existing negative tests and mismatches found between Phase 18, Phase 20, and Phase 23-25 outputs.
- Upstream compatibility details: MEDIUM - Phase 18 and Phase 23-25 mismatches are verified, but the exact compatibility output shape remains a planner/user decision within D-11/D-15 discretion.

**Research date:** 2026-06-24
**Valid until:** 2026-07-24, unless Phase 18/20/23/24/25 contracts change first.
