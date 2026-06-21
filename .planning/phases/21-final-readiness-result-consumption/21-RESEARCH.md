# Phase 21: Final Readiness Result Consumption - Research

**Researched:** 2026-06-21
**Domain:** Python stdlib verifier, JSON evidence contracts, Bazel/just verification, final cutover readiness gating
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

All bullets in this section are copied verbatim from `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

### Locked Decisions

## Implementation Decisions

### Upstream Result Authority

- **D-01:** Update the Phase 18 final review surface rather than creating a separate final-readiness policy engine. Phase 18 remains the authority for `demotion_allowed`, but Phase 21 adds upstream result consumption as a prerequisite for final criterion pass status.
- **D-02:** Add a machine-readable upstream result contract to Phase 18's checked-in review contract. Each final criterion that depends on upstream evidence should name its required result family, required manifest refs, acceptable statuses, freshness or lifecycle constraints, and redaction/source-ref expectations.
- **D-03:** Use Phase 19 aggregate CI result manifests for CI, simulator, hardware, live-service, and Phase 18 aggregate retention evidence. Use Phase 20 release result manifests for release-candidate artifact, signing, provenance, and comparison evidence. Retained-code, residual-risk, and maintainer-decision criteria continue to require Phase 18 decision input, but they must still appear in the final result summary with explicit upstream consumption state.
- **D-04:** The final review must not infer upstream pass status from contract rows, source refs, external URLs, or prose summaries. A decision ref can support human review, but only a validated upstream result manifest can satisfy upstream result proof.

### Gating Semantics

- **D-05:** `demotion_allowed` stays false when any required upstream result is missing, stale, malformed, has an unexpected lifecycle id, has unresolved source refs, contains redaction or overclaim failures, has `failed`, `blocked`, `pending-*`, `rejected-redaction`, or `rejected-overclaim` status, or is outside the approved artifact/ref root.
- **D-06:** Maintainer decisions may approve, reject, or exception a criterion only after the relevant upstream result rows have been validated. Approving a criterion with missing or failed upstream results should be rejected. Exception-approved or not-applicable decisions may coexist with non-passing upstream result rows only when the exception metadata explicitly cites the affected upstream result and mitigation.
- **D-07:** Generated final-demotion rows should carry both maintainer decision status and upstream result status. A final criterion passes only when the decision status allows cutover and every required upstream result is acceptable or covered by a valid exception.
- **D-08:** Redaction and overclaim failures are hard blockers. They cannot be converted to ordinary pass claims by maintainer decision input; they require corrected upstream artifacts or an explicit exception status that still keeps `demotion_allowed` false unless policy allows that exact exception outcome.

### Input and Artifact Model

- **D-09:** Add an explicit upstream result input path to the Phase 18 verifier, likely `--upstream-results`, rather than overloading `--decision-input` evidence refs. The input should be a repo-relative JSON packet under an ignored evidence directory or a validated external ref converted into machine-readable rows by the caller.
- **D-10:** The upstream result input should normalize each consumed row with criterion id, evidence family, owning phase, manifest path or external ref, source lifecycle id, status, failure reason, artifact refs, redaction status, source-ref validation result, generated-at timestamp if available, and covered requirement IDs.
- **D-11:** Quick mode without upstream results should continue to generate a deterministic blocked readiness report, but the report must now explain that upstream result evidence is missing. Quick mode with upstream results should write an upstream-result-consumption artifact and thread those statuses into `run-manifest.json`, `normalized-final-demotion-results.json`, and the redacted readiness report.
- **D-12:** Keep generated outputs under `build/ci-evidence/phase18` or an explicitly supplied output dir. Do not commit generated result manifests, logs, raw evidence, release payloads, crash dumps, credentials, tokens, certificates, signing keys, or private operator data.

### Traceability and Verification

- **D-13:** Add focused regression tests that prove approved maintainer decision input cannot make `demotion_allowed` true without valid upstream result manifests.
- **D-14:** Add tests for missing upstream result input, failed upstream result status, stale or wrong lifecycle id, redaction failure, path traversal/out-of-root refs, and exception-approved criteria that cite non-passing upstream results.
- **D-15:** Preserve existing Phase 18 contract-only, quick, security-only, and wiring-only modes. Extend them narrowly rather than refactoring the large Phase 18 verifier wholesale.
- **D-16:** Update planning, verification, and generated artifacts so REV-02 and REV-03 explicitly depend on machine-readable result consumption, not on contract/source row linkage alone.

### the agent's Discretion

- Exact JSON field names, helper function boundaries, acceptable-status vocabulary details, and artifact filenames are flexible if the result remains deterministic, source-backed, redacted, traceable, and hard to overclaim.
- Prefer a narrow Phase 18 verifier/contract extension plus tests over a new standalone verifier unless implementation evidence shows a separate module is materially cleaner.
- Keep current no-overclaim behavior intact: missing real external evidence should block final readiness, not become a local pass.

### Deferred Ideas (OUT OF SCOPE)

## Deferred Ideas

- Reconcile requirement checkboxes, validation metadata, roadmap progress, and milestone audit state after this functional gap closes in Phase 22.
- Broader refactoring of oversized Phase 18/20 verifier files remains non-blocking maintainer debt unless the Phase 21 change becomes unmanageably tangled.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REV-02 | Maintainer can approve or reject final reference-demotion criteria through an explicit checklist that links CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence. [VERIFIED: `.planning/REQUIREMENTS.md`] | Extend Phase 18 final criteria with explicit upstream result requirements and normalized upstream-consumption rows. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`] |
| REV-03 | Maintainer can produce a final cutover readiness report that marks reference demotion allowed only when all required gates pass or have documented maintainer-approved exceptions. [VERIFIED: `.planning/REQUIREMENTS.md`] | Gate `demotion_allowed` on both validated maintainer decision input and validated upstream result rows, and surface both statuses in generated reports. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`] |
</phase_requirements>

## Summary

Phase 21 should be planned as a narrow extension of the existing Phase 18 verifier and contract, not as a new policy engine. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] Phase 18 already owns final criteria, decision input validation, normalized final-demotion rows, redacted readiness artifacts, and `demotion_allowed`; the audit gap is that those criteria currently resolve checked-in contract/source refs and decision refs rather than validated upstream result manifests. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/manifests/phase18_cutover_review_contract.json`; `.planning/v1.1-MILESTONE-AUDIT.md`]

The planner should add an explicit `--upstream-results` JSON input to Phase 18, extend the Phase 18 contract with per-criterion upstream result requirements, normalize consumed rows into a new generated artifact, and make final criterion pass status require both maintainer decision permission and upstream result acceptance. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] Missing, pending, failed, stale lifecycle, malformed, path-escaped, redaction-failed, or overclaiming upstream results must keep `demotion_allowed=false`, including when a complete approving maintainer decision packet is supplied. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `tools/bazel/phase18_cutover_review_test.py`]

**Primary recommendation:** Extend `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`, and `tools/bazel/manifests/phase18_cutover_review_contract.json` to consume validated upstream result rows from Phase 19 and Phase 20 before any final criterion can pass. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `.planning/ROADMAP.md`]

## Project Constraints (from AGENTS.md)

- Read repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant standards pages before plan, review, implementation, or audit work. [VERIFIED: `AGENTS.md`; `AGENTS.bright-builds.md`]
- Bright Builds Rules apply, with no active local override in `standards-overrides.md`. [VERIFIED: `AGENTS.md`; `AGENTS.bright-builds.md`; `standards-overrides.md`]
- Use GSD workflow entrypoints for file-changing implementation work; direct edits outside GSD are disallowed unless the user explicitly bypasses the workflow. [VERIFIED: `AGENTS.md`]
- Keep Bazel authoritative and maintain `justfile` developer facades for common commands. [VERIFIED: `AGENTS.md`; `.planning/PROJECT.md` embedded in `AGENTS.md`]
- Preserve behavior parity and no-overclaim boundaries for safety-critical firmware evidence; external simulator, hardware, live-service, signing, and maintainer approval evidence cannot be claimed from local quick checks. [VERIFIED: `AGENTS.md`; `.planning/v1.1-MILESTONE-AUDIT.md`]
- Prefer functional core / imperative shell, parse raw input at boundaries, keep illegal states unrepresentable where practical, and unit test pure/business logic. [VERIFIED: `standards/core/architecture.md`; `standards/core/testing.md`]
- Prefer early returns, `maybe_` naming for internal optional values, and named helpers for large functions; Phase 18/20 files are already above Bright Builds size refactor triggers, so Phase 21 should be narrowly scoped and helper-oriented. [VERIFIED: `standards/core/code-shape.md`; `.planning/v1.1-MILESTONE-AUDIT.md`]
- Before committing, run relevant repo-native verification and do not commit if checks fail. [VERIFIED: `standards/core/verification.md`]
- No project skills were found under `.claude/skills/` or `.agents/skills/`. [VERIFIED: `ls .claude/skills`; `ls .agents/skills`]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|---|---:|---|---|
| Python stdlib `json`, `pathlib`, `datetime`, `re`, `unittest` | Python 3.14.4 available locally [VERIFIED: `python3 --version`] | Parse inputs, validate schemas, enforce path/ref guards, emit generated artifacts, and test verifier behavior. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase18_cutover_review_test.py`] | Phase 18/19/20 verifiers are stdlib Python scripts with direct `unittest` suites. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] |
| Checked-in JSON contracts | Schema version `1` in Phase 18/19/20 contracts [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`; `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`] | Make row IDs, status vocabularies, source refs, generated artifacts, and result requirements reviewable in source. [VERIFIED: same contract files] | Prior phases use contracts as the source of truth and generated manifests as ignored outputs. [VERIFIED: `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] |
| Bazel `shell_binary` wrappers | Bazel 9.1.1 available locally [VERIFIED: `bazel --version`] | Expose verifier and test labels through `//tools/bazel:*` and root aliases. [VERIFIED: `tools/bazel/BUILD.bazel`; `BUILD.bazel`] | Phase 18/19/20 verification targets already use this pattern. [VERIFIED: `tools/bazel/BUILD.bazel`] |
| `justfile` facade | just 1.48.0 available locally [VERIFIED: `just --version`] | Provide stable developer commands such as `phase18-verify`, `phase19-verify`, and `phase20-verify`. [VERIFIED: `justfile`] | Project constraints require a discoverable `justfile` for common Bazel/Rust workflows. [VERIFIED: `AGENTS.md`] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|---|---:|---|---|
| `jq` | 1.7.1 available locally [VERIFIED: `jq --version`] | Inspect generated JSON during planning/debugging. [VERIFIED: environment probe] | Use only for human inspection or shell assertions; do not make committed verifier logic depend on `jq`. [VERIFIED: Phase 18/19/20 verifiers use Python stdlib, not jq] |
| `git diff --check` | Git available via status probes [VERIFIED: `git status --short`] | Whitespace sanity check before completion. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] | Run after edits to docs/Python/JSON/wiring. [VERIFIED: `standards/core/verification.md`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Extending Phase 18 verifier [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] | New final-readiness policy engine | Rejected by locked decision D-01; it would duplicate Phase 18 `demotion_allowed` authority. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| Explicit `--upstream-results` input [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] | Overload `--decision-input` evidence refs | Rejected by locked decision D-09 and by the audit finding that decision refs alone are insufficient. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `.planning/v1.1-MILESTONE-AUDIT.md`] |
| Python stdlib validation [VERIFIED: Phase 18/19/20 verifier files] | Add JSON Schema or policy dependencies | Not needed for the narrow gap; existing repo pattern uses explicit constants and stdlib checks. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] |

**Installation:**

```bash
# No npm or new Python package install is recommended for Phase 21.
```

**Version verification:** No npm packages are recommended, so `npm view` is not applicable. [VERIFIED: Phase 21 context and prior verifier files]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
|-- phase18_cutover_review.py                  # Extend with upstream-result parsing, validation, normalization, and gating. [VERIFIED: file exists]
|-- phase18_cutover_review_test.py             # Extend with missing/failed/stale/redaction/path/exception result tests. [VERIFIED: file exists]
`-- manifests/
    `-- phase18_cutover_review_contract.json   # Add upstream result requirements and new generated artifact name. [VERIFIED: file exists]

build/ci-evidence/phase18/
|-- upstream-result-consumption.json           # New ignored generated normalized consumption artifact; exact filenames are discretionary. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
|-- run-manifest.json                          # Add upstream result supplied/valid/status counts. [VERIFIED: current artifact exists]
|-- normalized-final-demotion-results.json     # Add maintainer + upstream result status fields. [VERIFIED: current artifact exists]
`-- redacted-readiness-report.md               # Explain blocked/pending/failed/exception upstream rows. [VERIFIED: current artifact exists]
```

### Pattern 1: Parse Upstream Results at the Phase 18 Boundary

**What:** Add `--upstream-results` and parse a repo-relative JSON packet before normalizing final results. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**When to use:** Use for every quick/security run that needs final readiness status, including runs with and without maintainer decision input. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**Required normalized row fields:** `criterion_id`, `evidence_family`, `owning_phase`, `manifest_path` or `external_ref`, `source_lifecycle_id`, `status`, `failure_reason`, `artifact_refs`, `redaction_status`, `source_ref_status`, `generated_at_utc` when available, and `requirement_ids`. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**Planner implication:** Add a pure helper such as `validated_upstream_result_maps(...)` that returns normalized rows keyed by final criterion id, then call it from `write_quick_artifacts(...)`. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `standards/core/architecture.md`]

### Pattern 2: Make Final Criterion Pass Depend on Decision and Upstream Status

**What:** Preserve the existing decision-status rules, but make `demotion_status_allows_cutover` false unless required upstream result rows are acceptable or covered by a valid, row-citing exception. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**When to use:** Use in `normalize_final_results(...)` or a small helper called by it, because that function currently writes final row status, decision, evidence refs, blocking reason, and `demotion_status_allows_cutover`. [VERIFIED: `tools/bazel/phase18_cutover_review.py`]

**Important current behavior:** Existing tests prove a complete approving decision packet can make `demotion_allowed=true`; Phase 21 must change that behavior so the same packet still blocks without valid upstream results. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`]

### Pattern 3: Use Phase 19 for Aggregate/External Gate State and Phase 20 for Release State

**What:** Map CI, simulator, hardware, live-service, and Phase 18 retention rows to Phase 19 aggregate manifests, and map release artifact/signing/provenance/comparison rows to Phase 20 release manifests. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**When to use:** Use this mapping inside the Phase 18 contract, not as hardcoded ad hoc logic hidden only in Python. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

**Current observed generated status:** The local Phase 19 generated manifest has 25 `passed` local rows and five pending external rows, and the local Phase 20 generated manifest has 17 `pending-release-input` rows plus one `external-signing-required` row. [VERIFIED: `build/ci-evidence/phase19/run-manifest.json`; `build/ci-evidence/phase20/release-result-manifest.json`]

### Recommended Upstream Result Mapping

| Final Criterion | Required Upstream Source | Required Current Shape | Acceptable Status Policy |
|---|---|---|---|
| `final-ci-evidence` | Phase 19 aggregate `run-manifest.json` local gate and artifact-retention rows. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`] | `phase_lifecycle_id` equals `19-2026-06-21T01-07-45`, `gates[]` rows have safe artifact paths and no local failures. [VERIFIED: `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`] | `passed` only for required local CI/retention rows. [VERIFIED: Phase 19 status vocabulary] |
| `final-simulator-evidence` | Phase 19 row `phase14-real-simulator-input`. [VERIFIED: `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`] | Row includes owning phase, requirement IDs, status, artifact path, and failure reason. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`] | `passed` only, or explicit valid exception if contract marks it coverable; `pending-simulator-input` blocks. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| `final-hardware-safety-media-evidence` | Phase 19 row `phase15-hardware-operator-input`. [VERIFIED: `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`] | Same Phase 19 row shape. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`] | `passed` only, or explicit valid exception if coverable; `pending-hardware-input` and `blocked-*` block. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| `final-live-network-transfer-evidence` | Phase 19 row `phase16-live-service-operator-input`. [VERIFIED: `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`] | Same Phase 19 row shape. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`] | `passed` only, or explicit valid exception if coverable; `pending-live-input`, redaction failure, and credential blockers block. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| `final-release-artifact-signing-evidence` | Phase 20 `release-result-manifest.json` and `normalized-release-results.json`. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] | `phase_lifecycle_id` equals `20-2026-06-21T12-40-17`, 18 rows are present, release refs stay under `build/ci-evidence/phase20/` or `external://phase20/`. [VERIFIED: `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`; `tools/bazel/phase20_release_candidate_artifacts.py`] | `passed` only, with approved proof class; `source-contract-passed`, `template-only`, `pending-release-input`, `external-signing-required`, `release-run-required`, `failed`, and rejection statuses block. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| `final-retained-code-acceptance` | Phase 18 retained-code reviews plus explicit upstream-consumption state. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`] | All retained reviews exist and are accepted or deferred-approved-exception before this criterion can pass. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] | Existing accepted/deferred rules remain, but row should show upstream consumption state as decision-owned. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| `final-residual-risk-review` | Phase 18 decision input and residual-risk register. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] | Decision has rationale, evidence refs, exception metadata if applicable. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] | Existing decision rules remain, but generated row must include upstream consumption status. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| `final-maintainer-decision` | Phase 18 decision input. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] | Decision packet phase and lifecycle id must match Phase 18. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] | Existing decision rules remain; approving missing upstream rows is rejected. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| `final-reference-demotion-allowed` | Aggregate of all final criteria. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] | `demotion_allowed` is computed from normalized final rows. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] | True only when every row's combined decision/upstream gate allows cutover. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |

### Anti-Patterns to Avoid

- **Decision-only pass:** Do not let `complete_decision_input(...)` style fixtures make `demotion_allowed=true` unless upstream results are also valid. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
- **Contract refs as proof:** Do not treat `source_refs` or contract rows as upstream pass evidence. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
- **Release smoke as proof:** Do not use representative smoke artifacts or Phase 17 contract rows to satisfy final release readiness; Phase 20 result manifests are the release authority. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
- **Broad refactor:** Do not refactor Phase 18/20 wholesale during gap closure; both files are large, but locked decisions prefer a narrow extension. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `.planning/v1.1-MILESTONE-AUDIT.md`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Final readiness authority | New standalone policy engine | Phase 18 contract/verifier extension [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] | Phase 18 already owns final criteria and `demotion_allowed`. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] |
| Upstream input parsing | String-grep parsing of JSON artifacts | Python `json.loads` plus explicit row validators [VERIFIED: Phase 18/19/20 verifier files] | Existing verifier pattern already rejects malformed JSON and non-object/list shapes. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] |
| Path/ref safety | Ad hoc substring checks | Existing `Path`-based repo-relative/root helpers, extended for Phase 19/20 roots [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] | Existing tests cover path traversal and output containment patterns. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] |
| Secret/redaction checks | Prose-only review | Existing forbidden field/text scanners extended to upstream result inputs and generated consumption artifacts [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] | Phase 18 already scans decisions and generated artifacts for secrets and overclaim markers. [VERIFIED: `tools/bazel/phase18_cutover_review.py`] |
| Release result semantics | Phase 19 release interpretation | Phase 20 release-result manifest [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] | Phase 20 owns release rows, proof classes, signing/provenance fields, and comparison output. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`] |

**Key insight:** Phase 21 is an evidence-consumption hardening phase; it should make existing source-backed contracts consume generated result rows without inventing a broader release governance layer. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `.planning/v1.1-MILESTONE-AUDIT.md`]

## Common Pitfalls

### Pitfall 1: Approved Decision Input Masks Missing Upstream Results

**What goes wrong:** A complete maintainer decision packet can make all final rows allowed even when upstream results are absent. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`]

**Why it happens:** Current `normalize_final_results(...)` computes `demotion_status_allows_cutover` from decision status and evidence refs, not from upstream result rows. [VERIFIED: `tools/bazel/phase18_cutover_review.py`]

**How to avoid:** Require upstream result maps in the final-row normalization path and add a regression where complete approving decisions plus missing upstream results still yield `demotion_allowed=false`. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**Warning signs:** `run-manifest.json` shows `decision_inputs_supplied=true` and `demotion_allowed=true` while no upstream consumption artifact exists. [VERIFIED: current Phase 18 artifact schema]

### Pitfall 2: Pending External Rows Become Advisory Instead of Blocking

**What goes wrong:** Phase 19 rows such as `pending-simulator-input`, `pending-hardware-input`, and `pending-live-input` are shown in a report but do not block final readiness. [VERIFIED: `build/ci-evidence/phase19/run-manifest.json`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**Why it happens:** It is tempting to treat Phase 19 aggregate CI local rows as enough because the local verifier modes pass. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`]

**How to avoid:** Map local CI/retention rows separately from external evidence rows, and require the external rows to be `passed` or explicitly exception-covered where policy allows. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**Warning signs:** A final simulator/hardware/live criterion passes while the corresponding Phase 19 external placeholder row remains `pending-*`. [VERIFIED: `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`]

### Pitfall 3: Phase 20 Pending Release Inputs Are Treated as Release Proof

**What goes wrong:** Phase 20 quick output is machine-readable and present, but its rows are still `pending-release-input` or `external-signing-required`. [VERIFIED: `build/ci-evidence/phase20/release-result-manifest.json`]

**Why it happens:** Phase 20 intentionally writes result manifests even without approved release input, so presence of the manifest is not enough. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`]

**How to avoid:** Require each release row to be `passed` with an approved proof class, or require a row-specific valid exception where policy permits. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**Warning signs:** `final-release-artifact-signing-evidence` passes while `release_inputs_supplied=false`. [VERIFIED: `build/ci-evidence/phase20/release-result-manifest.json`]

### Pitfall 4: Reusing Phase 18 Evidence Ref Guards for Upstream Inputs

**What goes wrong:** Existing `require_phase18_artifact_ref(...)` intentionally rejects refs outside Phase 18, but upstream result manifests live under Phase 19/20 roots or approved external roots. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase18_cutover_review_test.py`]

**Why it happens:** Decision input evidence refs and upstream result manifest refs are different trust boundaries. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**How to avoid:** Add separate upstream-result ref validation that allows only configured roots such as `build/ci-evidence/phase19`, `build/ci-evidence/phase20`, `external://phase19/`, and `external://phase20/` where the contract permits. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; Phase 20 ref-guard pattern]

**Warning signs:** Tests have to put Phase 19 or Phase 20 paths into `decision_input["evidence_refs"]` to make the verifier accept upstream data. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`]

### Pitfall 5: Exceptions Hide Redaction or Overclaim Failures

**What goes wrong:** A maintainer exception converts `rejected-redaction` or `rejected-overclaim` into an allowed final row. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**Why it happens:** Existing `exception-approved` is an allowed demotion status when exception metadata is complete. [VERIFIED: `tools/bazel/phase18_cutover_review.py`]

**How to avoid:** Mark redaction, overclaim, malformed input, lifecycle mismatch, source-ref failure, and path/root failure as non-coverable hard blockers unless the Phase 18 contract explicitly defines a narrower exception outcome that still keeps `demotion_allowed=false`. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

**Warning signs:** A redaction or overclaim failure appears only in `residual_risk` text rather than in machine-readable upstream consumption status. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

## Code Examples

### Existing Decision-Only Demotion Gate to Extend

```python
def demotion_allowed(decision_inputs_supplied: bool, normalized_results: list[dict[str, Any]]) -> bool:
    if not decision_inputs_supplied:
        return False
    return all(bool(row["demotion_status_allows_cutover"]) for row in normalized_results)
```

Source: `tools/bazel/phase18_cutover_review.py`. [VERIFIED: `tools/bazel/phase18_cutover_review.py`]

### Existing Phase 19 Result Row Shape

```python
row = {
    "artifact_path": artifact_path.as_posix(),
    "command": command,
    "evidence_input": evidence_input,
    "failure_reason": failure_reason,
    "id": row_id,
    "owning_phase": owning_phase,
    "requirement_ids": requirement_ids,
    "status": status,
}
```

Source: `tools/bazel/phase19_aggregate_ci_evidence.py`. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`]

### Existing Phase 20 Release Result Writer

```python
result_manifest = {
    "artifact_name": contract["artifact_name"],
    "phase": PHASE,
    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
    "output_root": relative_output_dir.as_posix(),
    "release_inputs_supplied": release_inputs_supplied,
    "release_identity_label": RELEASE_IDENTITY_LABEL,
    "release_identity_command": RELEASE_IDENTITY_COMMAND,
    "rows": rows,
    "status_counts": status_counts,
}
```

Source: `tools/bazel/phase20_release_candidate_artifacts.py`. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`]

### Recommended Combined Gate Shape

```python
def final_result_allows_cutover(
    criterion: dict[str, Any],
    maybe_decision: dict[str, Any] | None,
    upstream_rows: list[dict[str, Any]],
) -> bool:
    decision_status = str(maybe_decision["status"]) if maybe_decision else str(criterion["default_status"])
    if not final_status_allows_demotion(decision_status, maybe_decision, criterion):
        return False
    return all(row["upstream_status_allows_cutover"] for row in upstream_rows)
```

This is a planning sketch that follows existing Phase 18 helper boundaries and the Phase 21 locked gating rule; exact names are discretionary. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Phase 18 final criteria link prior contracts and source refs. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`] | Phase 21 must require machine-readable upstream result consumption before criteria can pass. [VERIFIED: `.planning/ROADMAP.md`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] | Phase 21 planning date 2026-06-21. [VERIFIED: GSD init output] | Planner must add input parsing, contract mapping, generated consumption artifact, and demotion gating. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| Phase 19 retains Phase 14-18 quick artifacts and external placeholders. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`] | Phase 21 consumes Phase 19 aggregate rows as upstream result state for CI/simulator/hardware/live-service/retention criteria. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] | Phase 19 completed 2026-06-21. [VERIFIED: `.planning/ROADMAP.md`] | Pending external rows remain final readiness blockers. [VERIFIED: `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`] |
| Phase 17 release contract/identity was previously the release evidence reference surface. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`] | Phase 20 release-result manifests now own release artifact/signing/provenance/comparison status. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] | Phase 20 completed 2026-06-21. [VERIFIED: `.planning/ROADMAP.md`] | Phase 21 should use Phase 20 release rows, not Phase 17 contract rows, for final release readiness. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |

**Deprecated/outdated:**

- Treating `source_refs` as sufficient final proof is outdated for Phase 21. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
- Treating `external://phase18/...` decision refs as upstream result proof is outdated for Phase 21. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `tools/bazel/phase18_cutover_review.py`]
- Treating Phase 20 template-only release output as release pass evidence is invalid. [VERIFIED: `tools/bazel/phase20_release_candidate_artifacts.py`; `build/ci-evidence/phase20/release-result-manifest.json`]

## Assumptions Log

No claims in this research are intentionally tagged `[ASSUMED]`; recommendations are derived from the Phase 21 context, roadmap, milestone audit, and inspected verifier/contract code. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `.planning/ROADMAP.md`; `.planning/v1.1-MILESTONE-AUDIT.md`; `tools/bazel/phase18_cutover_review.py`]

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| None | No `[ASSUMED]` claims. | All | No user confirmation required for research claims. |

## Open Questions (RESOLVED)

1. **What exact filename should the upstream-consumption artifact use?**
   - What we know: Phase 21 requires an upstream-result-consumption artifact and allows exact artifact filenames to be chosen by the agent if deterministic and traceable. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
   - What's unclear: The context does not lock an exact filename. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
   - Recommendation: Use `upstream-result-consumption.json` and add it to Phase 18 `generated_artifacts`; exact artifact filenames are discretionary if deterministic and traceable. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
   - RESOLVED: Phase 21 uses `upstream-result-consumption.json` as the generated artifact name and adds it to Phase 18 `generated_artifacts`.

2. **Should non-redaction/non-overclaim upstream failures be exception-coverable?**
   - What we know: Phase 21 allows exception-approved decisions to coexist with non-passing upstream rows only when exception metadata cites the affected upstream result and mitigation. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
   - What's unclear: The context leaves exact acceptable-status vocabulary details to the agent. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
   - Recommendation: Add an explicit `exception_coverable` or `hard_blocker` flag per upstream requirement in the Phase 18 contract; make redaction, overclaim, malformed, lifecycle, source-ref, and path/root failures non-coverable. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
   - RESOLVED: Phase 21 adds explicit exception-coverable and hard-blocker policy to upstream result requirements. Redaction, overclaim, malformed input, lifecycle mismatch, source-ref failure, and path/root failure are non-coverable hard blockers.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---:|---|---|
| Python 3 | Phase 18 verifier/tests and generated artifact writer. [VERIFIED: Phase 18 files] | yes | 3.14.4 [VERIFIED: `python3 --version`] | None needed for local verifier. |
| Bazel | `//tools/bazel:phase18_verify*` and existing facade pattern. [VERIFIED: `tools/bazel/BUILD.bazel`] | yes | 9.1.1 [VERIFIED: `bazel --version`] | Direct `python3` commands can validate logic when Bazel cache/tooling is slow. [VERIFIED: Phase validation files] |
| just | Developer facade `phase18-verify`, `phase19-verify`, `phase20-verify`. [VERIFIED: `justfile`] | yes | 1.48.0 [VERIFIED: `just --version`] | Direct Bazel or Python commands. [VERIFIED: `tools/bazel/rust_workflow.sh`] |
| jq | Research/debugging JSON inspection. [VERIFIED: environment probe] | yes | 1.7.1-apple [VERIFIED: `jq --version`] | Python stdlib `json`; committed verifier should not depend on jq. [VERIFIED: Phase verifier files] |
| Existing generated Phase 19/20 artifacts | Test fixtures or local sanity checks. [VERIFIED: `find build/ci-evidence ...`] | yes | Generated before this research [VERIFIED: `build/ci-evidence/phase19/run-manifest.json`; `build/ci-evidence/phase20/release-result-manifest.json`] | Tests should build fixtures in temp roots, following existing Phase 18 test style. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`] |

**Missing dependencies with no fallback:** None for local Phase 21 planning and deterministic verifier work. [VERIFIED: environment probes]

**Missing dependencies with fallback:** Full simulator, hardware, live-service, and signing environments are not required for Phase 21 local verifier changes because this phase consumes result manifests and preserves pending/blocked external states. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`]

## Validation Architecture

Nyquist validation is enabled in `.planning/config.json`, so Phase 21 planning must include a validation section and requirement-to-test map. [VERIFIED: `.planning/config.json`]

### Test Framework

| Property | Value |
|---|---|
| Framework | Python stdlib `unittest` plus Bazel `shell_binary` wrappers. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`; `tools/bazel/BUILD.bazel`] |
| Config file | None for stdlib `unittest`; `pyproject.toml` only configures pytest integration tests. [VERIFIED: `pyproject.toml`; `.planning/phases/20-release-candidate-artifact-production/20-VALIDATION.md`] |
| Quick run command | `python3 tools/bazel/phase18_cutover_review_test.py && python3 tools/bazel/phase18_cutover_review.py --contract-only && python3 tools/bazel/phase18_cutover_review.py --quick` before wiring changes; add `--upstream-results` fixture runs after implementation. [VERIFIED: `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`] |
| Full suite command | `just phase18-verify`, plus direct Phase 19/20 commands if fixture generation is touched. [VERIFIED: `justfile`; Phase 19/20 validation files] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| REV-02 | Final criteria link to validated upstream result rows, not only contract/source rows or decision refs. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/v1.1-MILESTONE-AUDIT.md`] | unit / contract | `python3 tools/bazel/phase18_cutover_review_test.py` | yes, extend existing file [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`] |
| REV-02 | Missing, malformed, path-escaped, wrong-lifecycle, source-ref-failed, redaction-failed, and overclaiming upstream result input blocks criterion pass. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] | unit / security | `python3 tools/bazel/phase18_cutover_review_test.py && python3 tools/bazel/phase18_cutover_review.py --security-only --upstream-results <fixture>` | existing file, new mode args needed [VERIFIED: current parser lacks `--upstream-results`] |
| REV-03 | Complete approving decision input cannot make `demotion_allowed=true` without valid upstream result manifests. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] | unit | `python3 tools/bazel/phase18_cutover_review_test.py` | yes, extend existing file [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`] |
| REV-03 | Generated readiness artifacts explain maintainer status, upstream status, blockers, requirement IDs, and retained evidence refs. [VERIFIED: `.planning/ROADMAP.md`] | generated artifact / snapshot | `python3 tools/bazel/phase18_cutover_review.py --quick --upstream-results <fixture>` plus JSON assertions in tests | existing artifact writers, new artifact needed [VERIFIED: `tools/bazel/phase18_cutover_review.py`] |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase18_cutover_review_test.py` and the touched verifier mode. [VERIFIED: `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`]
- **Per wave merge:** Run `bazel run //tools/bazel:phase18_verify_tests`, `bazel run //tools/bazel:phase18_verify`, and `git diff --check`. [VERIFIED: `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`]
- **Phase gate:** Run `just phase18-verify`; if Phase 19/20 fixtures or contracts change, also run `just phase19-verify` and `just phase20-verify`. [VERIFIED: `justfile`; Phase 19/20 validation files]

### Wave 0 Gaps

- [ ] Extend `tools/bazel/manifests/phase18_cutover_review_contract.json` with upstream result requirements and `upstream-result-consumption.json`. [VERIFIED: current Phase 18 contract lacks upstream result requirements]
- [ ] Extend `tools/bazel/phase18_cutover_review.py` with `--upstream-results`, upstream input parsing, lifecycle/root/status/redaction/source-ref validation, normalized consumption output, and combined demotion gating. [VERIFIED: current parser lacks `--upstream-results`]
- [ ] Extend `tools/bazel/phase18_cutover_review_test.py` with positive and negative upstream result fixtures. [VERIFIED: current tests cover decision/ref/security behavior but not upstream result consumption]
- [ ] Update `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` only if new source/data files or command args require wiring changes. [VERIFIED: current Phase 18 wiring exists]

## Security Domain

Security enforcement is not disabled in `.planning/config.json`, so security analysis applies. [VERIFIED: `.planning/config.json`]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | Phase 21 does not authenticate users; it validates offline evidence inputs. [VERIFIED: Phase 21 context] |
| V3 Session Management | no | No sessions or cookies are introduced. [VERIFIED: Phase 21 context] |
| V4 Access Control | yes | Only approved artifact/ref roots and source lifecycle IDs may satisfy upstream result proof. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| V5 Input Validation | yes | Parse JSON at boundaries, require fields, validate status vocabularies, lifecycle IDs, timestamps, refs, and requirement IDs. [VERIFIED: `standards/core/architecture.md`; Phase 18/20 verifier patterns] |
| V6 Cryptography | no direct crypto | Phase 21 must not process private keys or raw signing payloads; release signing evidence is metadata-only from Phase 20. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |

### Known Threat Patterns for Phase 21

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Path traversal or absolute upstream result refs | Tampering | Use repo-relative `Path` checks and approved roots per result family. [VERIFIED: existing Phase 18/20 path guard patterns] |
| Stale lifecycle or wrong phase manifest | Spoofing / Tampering | Require source `phase` and `phase_lifecycle_id` to match Phase 19/20 contracts. [VERIFIED: Phase 18/20 lifecycle checks] |
| Secret-bearing upstream result fields | Information Disclosure | Extend forbidden field/text scans to upstream input and generated consumption artifacts. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| Pending/failed evidence overclaimed as passed | Elevation of Privilege | Make combined decision/upstream gate mandatory before `demotion_status_allows_cutover=true`. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |
| Exception metadata hides hard blockers | Repudiation / Tampering | Require row-citing exception metadata and make redaction/overclaim/malformed/path/lifecycle/source-ref failures non-coverable. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md` - locked Phase 21 decisions, discretion, deferred ideas, code context, and required tests. [VERIFIED: cat]
- `.planning/ROADMAP.md` - Phase 21 goal, dependencies, gap closure, and success criteria. [VERIFIED: cat]
- `.planning/REQUIREMENTS.md` - REV-02 and REV-03 definitions and Phase 21 traceability. [VERIFIED: cat]
- `.planning/v1.1-MILESTONE-AUDIT.md` - audit gap for Phase 18 contract/source refs and decision refs lacking upstream result proof. [VERIFIED: cat]
- `tools/bazel/phase18_cutover_review.py` - current final review verifier, decision validation, generated artifacts, security scan, and demotion computation. [VERIFIED: cat/rg/sed]
- `tools/bazel/phase18_cutover_review_test.py` - current Phase 18 regression coverage and decision-only demotion behavior. [VERIFIED: cat/rg/sed]
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - final criterion IDs, evidence families, source refs, status vocabulary, and generated artifacts. [VERIFIED: cat/jq]
- `tools/bazel/phase19_aggregate_ci_evidence.py` and contract - Phase 19 aggregate manifest shape, gate rows, status vocabulary, external placeholders, and output root. [VERIFIED: cat/jq/sed]
- `tools/bazel/phase20_release_candidate_artifacts.py` and contract - Phase 20 release result manifest shape, status/proof-class vocabulary, release input validation, and output root. [VERIFIED: cat/jq/sed]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/*.md` - repo and Bright Builds constraints. [VERIFIED: cat]

### Secondary (MEDIUM confidence)

- `build/ci-evidence/phase18/run-manifest.json`, `build/ci-evidence/phase19/run-manifest.json`, and `build/ci-evidence/phase20/release-result-manifest.json` - local generated artifact examples from prior phase verification. [VERIFIED: jq] These are useful shape examples but should not be treated as external pass evidence. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]

### Tertiary (LOW confidence)

- None. No web search or unverified external source was used because the phase scope is repo-local and all needed facts were available in checked-in context, contracts, and verifier code. [VERIFIED: source list above]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - Phase 18/19/20 already use Python stdlib, JSON contracts, Bazel shell wrappers, and just facades. [VERIFIED: verifier files; `tools/bazel/BUILD.bazel`; `justfile`]
- Architecture: HIGH - Phase 21 locked decisions explicitly choose Phase 18 extension and upstream result consumption. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-CONTEXT.md`]
- Pitfalls: HIGH - The milestone audit and current tests directly show the decision-ref/upstream-result gap. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `tools/bazel/phase18_cutover_review_test.py`]
- Environment: HIGH - Required local tools were probed in this session. [VERIFIED: `python3 --version`; `bazel --version`; `just --version`; `jq --version`]

**Research date:** 2026-06-21
**Valid until:** 2026-07-21 for repo-local contract/verifier patterns; re-check if Phase 18/19/20 contracts or generated manifest schemas change before planning. [VERIFIED: current date and inspected files]
