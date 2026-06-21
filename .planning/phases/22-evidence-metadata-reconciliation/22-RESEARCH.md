# Phase 22: Evidence Metadata Reconciliation - Research

**Researched:** 2026-06-21
**Domain:** GSD metadata reconciliation, Python stdlib verifiers, JSON evidence contracts, Bazel/just verification, milestone audit readiness
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

All bullets in this section are copied verbatim from `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

### Locked Decisions

## Implementation Decisions

### Requirements and Traceability Reconciliation

- **D-01:** Use evidence-qualified completion for requirement rows whose gate capability has been implemented and verified, while preserving result-level pending or blocked states for external evidence inputs.
- **D-02:** `SIM-03` should be reconciled as satisfied by Phase 14/19 traceability and no-overclaim boundaries only if the row text makes clear that hardware-only behavior is not simulator-proven.
- **D-03:** `REV-02` and `REV-03` should be reconciled as satisfied by Phase 21's upstream-result consumption gate only if the row text makes clear that `demotion_allowed` remains blocked without valid upstream results and maintainer decisions.
- **D-04:** Avoid unqualified "complete means all real-world evidence passed" wording. Requirement metadata should distinguish verified gate/capability from supplied external evidence outcome.

### Validation Metadata Reconciliation

- **D-05:** Reconcile Phase 14-18 validation files in place when local Wave 0 infrastructure now exists and passed verification.
- **D-06:** Set Wave 0 metadata and task-row file-existence/status fields from actual files and verification evidence, not from original planning placeholders.
- **D-07:** Preserve non-local evidence boundaries in each validation file. Physical simulator inputs, hardware/operator evidence, live-service credentials, release artifacts/signing evidence, retained-code maintainer decisions, and final demotion approval remain manual/external evidence paths unless validated inputs exist.
- **D-08:** If a validation file cannot honestly be marked complete, document a deliberate exception with owner, rationale, follow-up, and source refs instead of leaving stale placeholder metadata.

### Roadmap, Phase Directories, and State

- **D-09:** Use tool-anchored targeted reconciliation. Derive counts and statuses from phase directories, summaries, verification reports, and `gsd-tools` analysis before editing roadmap/state text.
- **D-10:** ROADMAP should reflect completed Phase 19, Phase 20, and Phase 21 work, including Phase 21's 1/1 plan and passed verification. Phase 22 should remain pending until its own plan and verification exist.
- **D-11:** STATE should be updated through GSD-owned workflow commands where available. If manual edits are unavoidable, keep them surgical and verify them with roadmap analysis and lifecycle checks.
- **D-12:** Do not add hot counters or broad generated summaries that require frequent hand maintenance when a derived tool check can validate the same fact.

### Milestone Audit Rerun Readiness

- **D-13:** Add a source-backed Phase 22 reconciliation contract or manifest plus verifier rather than relying on prose-only checkbox edits.
- **D-14:** The verifier should reject stale requirement statuses, validation frontmatter drift, mismatched roadmap/phase directory counts, missing source refs, unsafe generated artifact paths, secret-bearing refs, and overclaim wording.
- **D-15:** Generated audit rerun artifacts, logs, normalized reports, and snapshots should live under an ignored evidence root such as `build/ci-evidence/phase22/`.
- **D-16:** The source-backed reconciliation model may allow deliberate `non_blocking_debt` only with owner, rationale, follow-up or expiry trigger, and source refs. Broad or silent exceptions should fail verification.

### the agent's Discretion

- Exact manifest file names, schema field order, status wording, helper boundaries, and generated artifact names are flexible if the result is deterministic, source-backed, redacted, traceable, and hard to overclaim.
- Prefer standard-library Python, JSON manifests, focused tests, Bazel/just wiring, and localized planning metadata edits over broad audit framework rewrites.
- The planner may choose one integrated plan if it keeps the change cohesive. Split only if requirements/status edits and verifier implementation become too large for one safe execution pass.

### Deferred Ideas (OUT OF SCOPE)

## Deferred Ideas

- Tamper-evident artifact attestations or digest indexes for generated release evidence may be useful later, but Phase 22 should not introduce a new attestation trust root unless the local source-backed verifier requires it.
- Derived dashboard or long-lived audit-preflight automation may be useful if metadata drift recurs across milestones. For this phase, keep the verifier focused on v1.1 reconciliation.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| Metadata debt from v1.1 audit | Reconcile stale requirement statuses, incomplete Phase 14-18 Wave 0 validation metadata, roadmap progress, and audit rerun readiness. [VERIFIED: `.planning/ROADMAP.md`; `.planning/v1.1-MILESTONE-AUDIT.md`] | Use a Phase 22 source-backed reconciliation manifest plus stdlib verifier to prove each metadata correction is supported by phase summaries, verification reports, existing verifiers, lifecycle data, and no-overclaim boundaries. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review.py`] |
</phase_requirements>

## Summary

Phase 22 should be planned as a targeted metadata reconciliation and verification phase, not a firmware behavior phase. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.planning/ROADMAP.md`] The primary stale surfaces are `.planning/REQUIREMENTS.md` rows for `SIM-03`, `REV-02`, and `REV-03`; Phase 14-18 `*-VALIDATION.md` Wave 0 metadata; roadmap/state progress for Phase 21; and the v1.1 audit findings that still describe pre-gap-closure functional gaps. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`; `.planning/ROADMAP.md`; `.planning/STATE.md`; `.planning/v1.1-MILESTONE-AUDIT.md`]

The implementation should add a checked-in Phase 22 JSON contract and stdlib Python verifier that treats every metadata change as a source-backed correction with old state, new state, source refs, no-overclaim rationale, and verification command. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] This matches the established Phase 18/19/20 pattern: checked-in JSON policy, stdlib Python validation, generated artifacts under `build/ci-evidence/phaseXX`, Bazel labels, and `just` facades. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/BUILD.bazel`; `justfile`]

**Primary recommendation:** Create `tools/bazel/manifests/phase22_metadata_reconciliation_contract.json`, `tools/bazel/phase22_metadata_reconciliation.py`, and `tools/bazel/phase22_metadata_reconciliation_test.py`; wire them through Bazel/root aliases, `tools/bazel/rust_workflow.sh`, and `just phase22-verify`; then make surgical edits to the required planning metadata and prove them with the new verifier plus existing Phase 18/19/20 verifier modes. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review.py`; `justfile`]

## Project Constraints (from AGENTS.md)

- Read `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant standards pages before plan, review, implementation, or audit work. [VERIFIED: `AGENTS.md`; `AGENTS.bright-builds.md`; `standards/index.md`]
- Bright Builds Rules apply, and `standards-overrides.md` contains no active project-specific override for this phase. [VERIFIED: `AGENTS.md`; `AGENTS.bright-builds.md`; `standards-overrides.md`]
- Use GSD workflow entrypoints for file-changing implementation work unless the user explicitly bypasses the workflow. [VERIFIED: `AGENTS.md`]
- Keep Bazel authoritative and keep `justfile` as the developer facade for common Bazel/Rust verification commands. [VERIFIED: `AGENTS.md`; `justfile`]
- Preserve behavior parity and no-overclaim boundaries; external simulator, hardware, live-service, signing, release, and maintainer approval evidence cannot be converted into local pass claims. [VERIFIED: `AGENTS.md`; `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
- Prefer standard-library Python and repo-native Bazel/just verification for this metadata verifier, because Phase 18/19/20 use that pattern and Phase 22 context prefers it. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`]
- Keep generated evidence under ignored `build/ci-evidence/...` roots and avoid broad generated-output commits. [VERIFIED: `AGENTS.md`; `.gitignore`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
- Prefer functional core / imperative shell, parse raw input at boundaries, make illegal states unrepresentable where practical, and unit test pure/business logic. [VERIFIED: `standards/core/architecture.md`; `standards/core/testing.md`]
- Prefer early returns, clear helper names, and `maybe_` for internal optional names when practical. [VERIFIED: `standards/core/code-shape.md`]
- Before committing, run relevant repo-native verification and do not commit if checks fail. [VERIFIED: `standards/core/verification.md`; `AGENTS.md`]
- No project-local skills were found under `.claude/skills/` or `.agents/skills/`. [VERIFIED: `find .claude/skills .agents/skills -maxdepth 2 -type f -name SKILL.md -print`]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|---|---:|---|---|
| Python stdlib `json`, `pathlib`, `datetime`, `re`, `unittest`, `subprocess` | Python 3.14.4 [VERIFIED: `python3 --version`] | Parse the reconciliation contract, validate known metadata files, run/inspect source-backed verifier outputs, and unit test negative cases. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`; `tools/bazel/phase18_cutover_review_test.py`] | Existing Phase 18/19/20 verifiers are stdlib Python scripts with direct stdlib `unittest` suites. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] |
| Checked-in JSON contract | Schema version should be explicit; Phase 18/20 contracts use `"schema_version": "1"`. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`] | Make metadata corrections, source refs, status vocabularies, and allowed `non_blocking_debt` reviewable in source. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] | Prior evidence gates use checked-in JSON as policy and generated JSON as runtime evidence. [VERIFIED: `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`] |
| Bazel `shell_binary` labels | Bazel 9.1.1 [VERIFIED: `bazel --version`] | Expose `phase22_verify` and `phase22_verify_tests` through `//tools/bazel:*` and root aliases. [VERIFIED: `tools/bazel/BUILD.bazel`; `BUILD.bazel`] | Phase 14-20 verifier labels already use this facade. [VERIFIED: `tools/bazel/BUILD.bazel`; `BUILD.bazel`] |
| `justfile` recipe | just 1.48.0 [VERIFIED: `just --version`] | Provide a stable `just phase22-verify` command that runs tests before the verifier. [VERIFIED: `justfile`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] | Existing phase recipes run Bazel test labels before verifier labels. [VERIFIED: `justfile`] |
| `gsd-tools.cjs` | Available through `/Users/peterryszkiewicz/.codex/get-shit-done/bin/gsd-tools.cjs`. [VERIFIED: `node /Users/peterryszkiewicz/.codex/get-shit-done/bin/gsd-tools.cjs`] | Initialize phase context, inspect lifecycle, read state, and commit research/docs through GSD helpers. [VERIFIED: `gsd-tools init phase-op 22`; `gsd-tools state`; `gsd-tools verify lifecycle 22`] | Phase 22 context explicitly requires tool-anchored reconciliation and GSD-owned state updates where available. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|---|---:|---|---|
| Git | 2.53.0 [VERIFIED: `git --version`] | Detect dirty worktree, run `git diff --check`, and keep commits scoped. [VERIFIED: `git status --short`; `standards/core/verification.md`] | Use before/after edits and before any commit. [VERIFIED: `AGENTS.md`; `standards/core/verification.md`] |
| Node.js | v24.13.0 [VERIFIED: `node --version`] | Run `gsd-tools.cjs` for phase init, state, lifecycle, and commit helper calls. [VERIFIED: `gsd-tools init phase-op 22`; `gsd-tools state`] | Use for GSD-owned workflow metadata, not for Phase 22 verifier implementation. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| `jq` | Available at `/usr/bin/jq`. [VERIFIED: `command -v jq`] | Human inspection of generated JSON during debugging. [VERIFIED: `command -v jq`] | Do not make committed verifier logic depend on `jq`; existing verifiers use Python stdlib. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Phase 22 JSON contract plus verifier [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] | Prose-only checklist edits | Rejected by locked decision D-13 because prose-only edits cannot enforce stale status, source-ref, path, secret, or overclaim failures. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| Targeted metadata checks over known files [VERIFIED: `.planning/ROADMAP.md`; `.planning/REQUIREMENTS.md`] | Full Markdown AST/audit framework rewrite | Rejected by locked discretion to keep the verifier focused on v1.1 reconciliation and avoid broad audit framework rewrites. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| Existing GSD audit workflow plus Phase 22 preflight [VERIFIED: `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`] | A separate long-lived dashboard | Deferred by Phase 22 context; dashboards are out of scope. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| Python stdlib validation [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] | Add YAML/JSON Schema/Markdown parser dependencies | Not recommended because existing phase verifiers use stdlib and the context prefers standard-library Python. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`] |

**Installation:**

```bash
# No npm or Python package installation is recommended for Phase 22.
```

**Version verification:** No npm packages are recommended, so `npm view` is not applicable. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
|-- phase22_metadata_reconciliation.py              # Stdlib verifier, artifact writer, and wiring checks. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`]
|-- phase22_metadata_reconciliation_test.py         # Stdlib unit tests for stale status, source-ref, path, secret, and overclaim failures. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`; `tools/bazel/phase19_aggregate_ci_evidence_test.py`; `tools/bazel/phase20_release_candidate_artifacts_test.py`]
`-- manifests/
    `-- phase22_metadata_reconciliation_contract.json
                                                     # Source-backed correction manifest. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

build/ci-evidence/phase22/
|-- metadata-reconciliation-report.json             # Generated status and correction report. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
|-- audit-rerun-readiness.json                      # Generated rerun readiness or non-blocking debt report. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
|-- redacted-summary.md                             # Human summary without secrets or overclaims. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
`-- source-snapshots/                               # Optional source snapshots when useful and redacted. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`]
```

### Pattern 1: Manifest-Driven Metadata Corrections

**What:** Each metadata change should be represented by a contract row with target file, old-state evidence, intended new state, source refs, no-overclaim rationale, verification command, and optional `non_blocking_debt`. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

**When to use:** Use for requirements rows, validation file frontmatter/tasks, roadmap progress, STATE position, and audit readiness closure rows. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/ROADMAP.md`; `.planning/STATE.md`; `.planning/v1.1-MILESTONE-AUDIT.md`]

**Example:**

```json
{
  "id": "requirements-sim-03",
  "target_file": ".planning/REQUIREMENTS.md",
  "old_state": "unchecked and Pending",
  "new_state": "evidence-qualified complete with hardware-only behavior still not simulator-proven",
  "source_refs": [
    ".planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md#SIM-03",
    ".planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md#SIM-02"
  ],
  "no_overclaim_rationale": "Marks traceability capability satisfied while preserving hardware-only proof outside simulator evidence.",
  "verification_command": "python3 tools/bazel/phase22_metadata_reconciliation.py --quick"
}
```

This row shape is a recommended Phase 22 schema, not an existing file. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

### Pattern 2: Evidence-Qualified Requirement Status

**What:** Requirement checkboxes may move to checked only when their implemented gate/capability is verified and the adjacent traceability text preserves pending external evidence outcomes. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

**When to use:** Use for `SIM-03`, `REV-02`, and `REV-03`, which are currently unchecked or pending in `.planning/REQUIREMENTS.md` despite Phase 14/21 verification evidence. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`]

**Planner rule:** Do not use unqualified `Complete` for rows whose real-world result evidence remains pending; use wording such as `Complete - gate verified; external result evidence remains pending/blocked unless validated inputs pass`. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

### Pattern 3: Validation Metadata Reconciliation In Place

**What:** Phase 14-18 validation files should be edited in place so `wave_0_complete`, per-task `File Exists`, per-task status, and Wave 0 checklist items reflect actual files and passed verification. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`]

**When to use:** Use for the five files that still contain `wave_0_complete: false`, pending task rows, and unchecked Wave 0 items even though their referenced verifier files exist. [VERIFIED: `rg -n 'wave_0_complete|pending|no - Wave 0|\\[ \\] \`tools/bazel' .planning/phases/{14..18}*/??-VALIDATION.md`; `ls tools/bazel/...phase14...phase18...`]

**Planner rule:** Preserve manual-only sections that say physical simulator inputs, hardware/operator evidence, live-service credentials, release artifacts/signing evidence, retained-code maintainer decisions, and final demotion approval remain external evidence. [VERIFIED: `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

### Pattern 4: Rerun Readiness Artifact, Not Audit Theater

**What:** The Phase 22 verifier should generate a readiness report mapping each original v1.1 audit gap or metadata debt row to `closed`, `still_blocking`, or `non_blocking_debt` with source refs. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

**When to use:** Use before rerunning `/gsd-audit-milestone`, so the rerun is against synchronized source-backed records rather than hand-edited prose. [VERIFIED: `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`; `.planning/ROADMAP.md`]

**Planner rule:** Do not overwrite missing hardware, live-service, signing, release, upstream-result, maintainer-decision, or final demotion evidence as passed unless the validated upstream inputs exist. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase20_release_candidate_artifacts.py`]

### Anti-Patterns to Avoid

- **Prose-only reconciliation:** Fails D-13 and cannot be checked by the milestone audit rerun. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
- **Checkbox overclaiming:** Checking `REV-02` or `REV-03` without saying `demotion_allowed` remains blocked without valid upstream results and maintainer decisions violates D-03/D-04. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.planning/REQUIREMENTS.md`]
- **Replacing validation files wholesale:** Phase 14-18 validation files already contain manual-only evidence boundaries; wholesale rewrites risk losing those boundaries. [VERIFIED: `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`]
- **Committing generated audit/rerun artifacts:** `build/ci-evidence/phase22/` is intended as ignored runtime output, and `.gitignore` ignores `/build*`. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.gitignore`]
- **Broad state rewrites:** STATE has stale focus/current-position data, but D-11 requires GSD-owned or surgical updates. [VERIFIED: `.planning/STATE.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Milestone audit engine | A second full audit framework | Existing `/gsd-audit-milestone` workflow plus Phase 22 preflight verifier [VERIFIED: `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`] | The GSD audit already defines requirement cross-reference, integration, flow, and Nyquist discovery rules. [VERIFIED: `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`] |
| Evidence policy storage | Prose-only tables | Checked-in JSON contract plus stdlib verifier [VERIFIED: `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] | JSON rows make corrections deterministic and reviewable. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json`; `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json`] |
| Secret detection | Ad hoc manual review only | Reuse explicit forbidden-marker scans used by Phase 18/19/20 verifiers. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] | Phase 22 context requires verifier rejection of secret-bearing refs. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| Generated artifact retention | Committed logs/snapshots | Ignored `build/ci-evidence/phase22/` outputs. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.gitignore`] | Existing evidence phases keep generated runtime artifacts under ignored `build/ci-evidence/phaseXX`. [VERIFIED: `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] |
| Roadmap/state counts | Hot counters maintained by hand | Derive and validate from phase directories, summaries, verification reports, and GSD lifecycle tools. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `gsd-tools init phase-op 22`; `gsd-tools verify lifecycle 22`] | D-09/D-12 explicitly require tool-anchored reconciliation and discourage hot counters. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |

**Key insight:** Phase 22's risk is not missing code capability; it is metadata saying more or less than the verified evidence supports. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`]

## Metadata Drift Inventory

| Surface | Current State | Required Phase 22 Treatment |
|---|---|---|
| `.planning/REQUIREMENTS.md` `SIM-03` | Checkbox is unchecked and traceability status is `Pending`. [VERIFIED: `.planning/REQUIREMENTS.md:20`; `.planning/REQUIREMENTS.md:79`] | Mark evidence-qualified complete only with wording that hardware-only behavior is not simulator-proven. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md`] |
| `.planning/REQUIREMENTS.md` `REV-02` and `REV-03` | Checkboxes are unchecked and traceability statuses are `Pending`. [VERIFIED: `.planning/REQUIREMENTS.md:43`; `.planning/REQUIREMENTS.md:44`; `.planning/REQUIREMENTS.md:90`; `.planning/REQUIREMENTS.md:91`] | Mark evidence-qualified complete only with wording that final demotion remains blocked without valid upstream results and maintainer decisions. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`] |
| Phase 14-18 validation files | Each has `wave_0_complete: false`, pending task rows, and unchecked Wave 0 items. [VERIFIED: `rg -n 'wave_0_complete|pending|no - Wave 0|No - Wave 0|\\[ \\] \`tools/bazel' .planning/phases/14-simulator-evidence-gates/14-VALIDATION.md .planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md .planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md .planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md .planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`] | Edit in place to reflect existing files and passed local validation, while preserving manual-only evidence boundaries. [VERIFIED: `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VERIFICATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VERIFICATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VERIFICATION.md`; `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| Phase 21 roadmap progress | ROADMAP top list and progress table still show Phase 21 planned with `0/0` plans. [VERIFIED: `.planning/ROADMAP.md:44`; `.planning/ROADMAP.md:214`] | Update Phase 21 to complete with `1/1` plan and passed verification evidence. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-01-SUMMARY.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| STATE progress/current position | STATE says current focus Phase 20 and current position Phase 21 ready for verification, while Phase 21 verification is passed. [VERIFIED: `.planning/STATE.md:24`; `.planning/STATE.md:28`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`] | Update through GSD tooling if available; otherwise make a surgical source-backed edit and verify with lifecycle/state checks. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `gsd-tools state`; `gsd-tools verify lifecycle 22`] |
| v1.1 milestone audit | Audit file still has `status: gaps_found` and pre-Phase-19/20/21 functional gaps. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`] | Add Phase 22 readiness mapping and rerun audit after reconciliation; missing external result evidence remains pending/non-blocking debt only with source-backed rationale. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`] |
| Phase 20 validation file | `20-VALIDATION.md` currently says `nyquist_compliant: false`, `wave_0_complete: false`, and pending rows despite Phase 20 passed verification. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VALIDATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] | Treat as adjacent phase-directory drift; either include it in Phase 22's phase-directory consistency checks or document it as deliberate `non_blocking_debt` if the planner keeps validation cleanup strictly to Phase 14-18. [VERIFIED: `.planning/ROADMAP.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |

## Common Pitfalls

### Pitfall 1: Requirement Checkbox Overclaim

**What goes wrong:** A row is checked as complete without preserving that real simulator, hardware, live-service, release, signing, upstream-result, maintainer-decision, or final demotion evidence may still be pending. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

**Why it happens:** The GSD audit status matrix treats checked requirements, summary frontmatter, and verification tables as independent sources, but the human wording can collapse gate capability and result evidence into one word. [VERIFIED: `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`; `.planning/REQUIREMENTS.md`]

**How to avoid:** Require Phase 22 contract rows to include `no_overclaim_rationale` and verifier checks for forbidden phrases such as `cutover complete`, `reference demotion approved`, or `hardware verified locally`. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`]

**Warning signs:** Traceability says only `Complete`, generated reports set pass states without source refs, or `demotion_allowed` is discussed without upstream results and maintainer decisions. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`]

### Pitfall 2: Validation Frontmatter Updated But Task Rows Stay Stale

**What goes wrong:** `wave_0_complete` is changed to true while task rows still say `no - Wave 0 creates file` or `pending`. [VERIFIED: `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`; `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`]

**Why it happens:** Nyquist discovery parses frontmatter and task rows, so partial edits still classify a phase as partial. [VERIFIED: `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`]

**How to avoid:** Make the verifier check frontmatter, every per-task status, every file-existence cell, and every Wave 0 checklist item for Phase 14-18. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`]

**Warning signs:** `nyquist_compliant: true` paired with `wave_0_complete: false`, unchecked Wave 0 bullets, or `pending` in the verification map. [VERIFIED: `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`]

### Pitfall 3: Audit File Contradictions

**What goes wrong:** `.planning/v1.1-MILESTONE-AUDIT.md` continues to say the release identity is empty or final review consumes only contracts after Phase 20/21 have changed those facts. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`]

**Why it happens:** The audit was generated before functional gap closure and is not automatically rewritten by later phases. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`]

**How to avoid:** Generate a Phase 22 audit-rerun-readiness artifact and then rerun `/gsd-audit-milestone`; do not silently edit old findings into a passed result without a source-backed rerun. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`]

**Warning signs:** Old audit gaps are deleted rather than mapped to source refs, or `non_blocking_debt` lacks owner/rationale/follow-up/source refs. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

### Pitfall 4: Expanding Scope Into New Evidence Production

**What goes wrong:** Phase 22 starts generating new hardware, live-service, release signing, or maintainer approval evidence. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

**Why it happens:** Metadata reconciliation can make pending external evidence look like an implementation gap. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`]

**How to avoid:** Treat missing external inputs as pending/blocked/non-blocking debt only when the contract row records owner, rationale, follow-up or expiry trigger, and source refs. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

**Warning signs:** Any Phase 22 artifact claims physical printer proof, live service proof, signing proof, maintainer approval, or reference demotion approval from local quick checks. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`]

## Code Examples

Verified patterns from local sources:

### Stdlib Contract Loader And Error Type

```python
class VerificationError(Exception):
    pass

def load_json(root: Path, path: str | Path) -> dict[str, Any]:
    relative_path = Path(path)
    try:
        data = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{relative_path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(f"{relative_path.as_posix()} must contain a top-level JSON object")
    return data
```

Source: `tools/bazel/phase19_aggregate_ci_evidence.py`. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`]

### Generated Artifact Pattern

```python
run_manifest = {
    "artifact_name": "phase19-ci-evidence",
    "generated_at_utc": generated_at_utc,
    "phase": PHASE,
    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
    "schema_version": "1",
}
write_json(output_root / "run-manifest.json", run_manifest)
```

Source: `tools/bazel/phase19_aggregate_ci_evidence.py`; Phase 22 should use the same shape with Phase 22 names and lifecycle id. [VERIFIED: `tools/bazel/phase19_aggregate_ci_evidence.py`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

### Verification Command Ordering In `justfile`

```make
phase20-verify:
    bazel run //tools/bazel:phase20_verify_tests
    bazel run //tools/bazel:phase20_verify
```

Source: `justfile`; Phase 22 should add the analogous `phase22-verify` recipe. [VERIFIED: `justfile`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Phase-local contracts and prose summaries without one aggregate Phase 14-18 CI bundle. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`] | Phase 19 aggregate CI verifier runs/retains Phase 14-18 local verifier outputs and external-input placeholders. [VERIFIED: `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`] | 2026-06-21 in Phase 19. [VERIFIED: `.planning/phases/19-aggregate-cutover-evidence-ci/19-SUMMARY.md`] | Requirements `CIEV-*`, `SIM-01/02`, `HARD-*`, and `LIVE-*` can be reconciled as gate-capability complete while external result rows remain pending. [VERIFIED: `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`] |
| Empty `phase17_release_candidate_artifacts` target. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`] | Phase 20 release identity points to `:phase20_release_environment_input_manifest` and rejects smoke labels as release proof. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`; `tools/bazel/phase20_release_candidate_artifacts.py`] | 2026-06-21 in Phase 20. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] | Requirements `REL-01/02/03` can stay complete with quick output pending approved release inputs. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`] |
| Phase 18 final criteria linked contracts and decision refs without independently validated upstream result rows. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`] | Phase 21 extended Phase 18 with upstream result requirements and `--upstream-results`; `demotion_allowed` requires valid decisions and valid upstream rows. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`; `tools/bazel/phase18_cutover_review.py`] | 2026-06-21 in Phase 21. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-01-SUMMARY.md`] | Requirements `REV-02/03` can be reconciled as gate-capability complete while final demotion remains blocked without validated upstream results and maintainer decisions. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |

**Deprecated/outdated:**

- Treating old audit gaps as current truth after Phases 19-21 is outdated; the old audit should be rerun or superseded by a source-backed readiness artifact. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
- Treating Wave 0 placeholders in Phase 14-18 validation files as current truth is outdated because the referenced files exist and phase verifications passed. [VERIFIED: `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`; `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VERIFICATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VERIFICATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VERIFICATION.md`; `ls tools/bazel/manifests/phase14_simulator_evidence_contract.json tools/bazel/phase14_simulator_evidence.py tools/bazel/phase14_simulator_evidence_test.py tools/bazel/manifests/phase15_hardware_evidence_contract.json tools/bazel/phase15_hardware_evidence.py tools/bazel/phase15_hardware_evidence_test.py tools/bazel/manifests/phase16_live_network_evidence_contract.json tools/bazel/phase16_live_network_evidence.py tools/bazel/phase16_live_network_evidence_test.py tools/bazel/manifests/phase17_release_candidate_evidence_contract.json tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py tools/bazel/manifests/phase18_cutover_review_contract.json tools/bazel/phase18_cutover_review.py tools/bazel/phase18_cutover_review_test.py`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|

**All claims in this research were verified from local repository files or command probes in this session; no `[ASSUMED]` claims are intentionally included.** [VERIFIED: `## Sources` section in this file]

## Open Questions

1. **Should Phase 20 validation drift be included in Phase 22 cleanup?**
   - What we know: Phase 20 validation currently has `nyquist_compliant: false`, `wave_0_complete: false`, pending rows, and unchecked Wave 0 items, while Phase 20 verification passed. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VALIDATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`]
   - What's unclear: Phase 22 locked decisions name Phase 14-18 validation cleanup, while roadmap success criteria also require Phase 19-22 phase-directory consistency. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `.planning/ROADMAP.md`]
   - Recommendation: The planner should include Phase 20 in the Phase 22 verifier's phase-directory consistency scan and either reconcile it if in scope or record explicit `non_blocking_debt` with owner, rationale, follow-up, and source refs. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

2. **Should the original audit file be overwritten or superseded?**
   - What we know: The current audit file records pre-Phase-19/20/21 gaps and the audit workflow writes `.planning/v{version}-MILESTONE-AUDIT.md`. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`]
   - What's unclear: Phase 22 context allows updating or superseding findings through a rerun artifact, but does not require hand-editing the old audit before rerun. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
   - Recommendation: Keep the original audit's historical findings intact until an actual rerun; Phase 22 should add a generated readiness artifact and then run the audit workflow so the updated audit is tool-produced. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---:|---|---|
| Python 3 | Phase 22 verifier and tests | yes [VERIFIED: `python3 --version`] | 3.14.4 | None needed |
| Bazel | Phase 22 labels and repo-native verification | yes [VERIFIED: `bazel --version`] | 9.1.1 | Direct Python verifier commands can cover local logic if Bazel is unavailable during debugging, but final repo-native verification should use Bazel. [VERIFIED: `standards/core/verification.md`; `justfile`] |
| just | Developer facade | yes [VERIFIED: `just --version`] | 1.48.0 | Run Bazel labels directly if `just` is unavailable. [VERIFIED: `justfile`; `tools/bazel/BUILD.bazel`] |
| Node.js | `gsd-tools.cjs` | yes [VERIFIED: `node --version`] | v24.13.0 | Manual surgical edits plus Python verifier if a GSD helper lacks a state update subcommand. [VERIFIED: `gsd-tools state`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| Git | Diff, status, commit, whitespace checks | yes [VERIFIED: `git --version`; `git status --short`] | 2.53.0 | None |
| jq | Optional local JSON inspection | yes [VERIFIED: `command -v jq`] | system `jq` | Use `python3 -m json.tool` or verifier tests. [VERIFIED: Python availability] |

**Missing dependencies with no fallback:** None identified for Phase 22 metadata/verifier work. [VERIFIED: `python3 --version`; `bazel --version`; `just --version`; `node --version`; `git --version`; `command -v jq`]

**Missing dependencies with fallback:** None identified. [VERIFIED: `python3 --version`; `bazel --version`; `just --version`; `node --version`; `git --version`; `command -v jq`]

## Validation Architecture

Nyquist validation is enabled in `.planning/config.json`. [VERIFIED: `.planning/config.json`]

### Test Framework

| Property | Value |
|---|---|
| Framework | Python stdlib `unittest` plus Bazel `shell_binary` wrappers. [VERIFIED: `tools/bazel/phase18_cutover_review_test.py`; `tools/bazel/phase19_aggregate_ci_evidence_test.py`; `tools/bazel/phase20_release_candidate_artifacts_test.py`; `tools/bazel/BUILD.bazel`] |
| Config file | `tools/bazel/manifests/phase22_metadata_reconciliation_contract.json` should be the Phase 22 source contract. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| Quick run command | `python3 tools/bazel/phase22_metadata_reconciliation_test.py && python3 tools/bazel/phase22_metadata_reconciliation.py --quick` should be the direct local command. [VERIFIED: `tools/bazel/rust_workflow.sh`; `justfile`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] |
| Full suite command | `just phase22-verify` should run Bazel tests before the verifier. [VERIFIED: `justfile`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| Metadata debt from v1.1 audit | Requirements checkboxes/traceability match Phase 14/19/21 evidence and no-overclaim wording. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`] | unit/contract | `python3 tools/bazel/phase22_metadata_reconciliation_test.py` | no - Wave 0 creates it [VERIFIED: `ls .planning/phases/22-evidence-metadata-reconciliation`; `ls tools/bazel/phase22_metadata_reconciliation.py tools/bazel/phase22_metadata_reconciliation_test.py tools/bazel/manifests/phase22_metadata_reconciliation_contract.json` would fail before Wave 0] |
| Metadata debt from v1.1 audit | Phase 14-18 validation frontmatter, task rows, file-existence cells, and Wave 0 checklists match actual files and verification evidence. [VERIFIED: `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`; `.planning/phases/14-simulator-evidence-gates/14-VERIFICATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VERIFICATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VERIFICATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VERIFICATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VERIFICATION.md`; `ls tools/bazel/manifests/phase14_simulator_evidence_contract.json tools/bazel/phase14_simulator_evidence.py tools/bazel/phase14_simulator_evidence_test.py tools/bazel/manifests/phase15_hardware_evidence_contract.json tools/bazel/phase15_hardware_evidence.py tools/bazel/phase15_hardware_evidence_test.py tools/bazel/manifests/phase16_live_network_evidence_contract.json tools/bazel/phase16_live_network_evidence.py tools/bazel/phase16_live_network_evidence_test.py tools/bazel/manifests/phase17_release_candidate_evidence_contract.json tools/bazel/phase17_release_candidate_evidence.py tools/bazel/phase17_release_candidate_evidence_test.py tools/bazel/manifests/phase18_cutover_review_contract.json tools/bazel/phase18_cutover_review.py tools/bazel/phase18_cutover_review_test.py`] | unit/metadata | `python3 tools/bazel/phase22_metadata_reconciliation.py --validation-only` | no - Wave 0 creates it [VERIFIED: `ls .planning/phases/22-evidence-metadata-reconciliation`] |
| Metadata debt from v1.1 audit | ROADMAP and STATE reflect completed Phase 19/20/21 and pending Phase 22 boundaries. [VERIFIED: `.planning/ROADMAP.md`; `.planning/STATE.md`; `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`; `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`; `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`] | unit/metadata | `python3 tools/bazel/phase22_metadata_reconciliation.py --roadmap-state-only` | no - Wave 0 creates it [VERIFIED: `ls .planning/phases/22-evidence-metadata-reconciliation`] |
| Metadata debt from v1.1 audit | Generated audit readiness report closes old functional gaps or lists only source-backed `non_blocking_debt`. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] | generated artifact/security | `python3 tools/bazel/phase22_metadata_reconciliation.py --quick --output-dir build/ci-evidence/phase22` | no - Wave 0 creates it [VERIFIED: `ls .planning/phases/22-evidence-metadata-reconciliation`] |
| Metadata debt from v1.1 audit | Secret-bearing refs, unsafe generated artifact paths, missing source refs, and overclaim wording are rejected. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] | security negative | `python3 tools/bazel/phase22_metadata_reconciliation_test.py` | no - Wave 0 creates it [VERIFIED: `ls .planning/phases/22-evidence-metadata-reconciliation`] |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase22_metadata_reconciliation_test.py` plus the touched verifier mode. [VERIFIED: `.planning/phases/21-final-readiness-result-consumption/21-VALIDATION.md`]
- **Per wave merge:** Run `just phase22-verify` and `git diff --check`. [VERIFIED: `justfile`; `standards/core/verification.md`]
- **Phase gate:** Run `just phase22-verify`, existing Phase 18/19/20 contract modes, lifecycle validation, and `/gsd-audit-milestone` or an equivalent audit rerun after metadata edits. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md`]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase22_metadata_reconciliation_contract.json` - source-backed correction rows and allowed debt schema. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `ls .planning/phases/22-evidence-metadata-reconciliation`]
- [ ] `tools/bazel/phase22_metadata_reconciliation.py` - stdlib verifier, generated report writer, source-ref/path/secret/overclaim checks, and wiring checks. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `ls .planning/phases/22-evidence-metadata-reconciliation`]
- [ ] `tools/bazel/phase22_metadata_reconciliation_test.py` - focused unit tests for stale requirement rows, validation drift, roadmap/state mismatch, non-blocking debt schema, generated artifact path guards, and overclaim rejection. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `ls .planning/phases/22-evidence-metadata-reconciliation`]
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 22 labels, root aliases, dispatch, and facade. [VERIFIED: `tools/bazel/BUILD.bazel`; `BUILD.bazel`; `tools/bazel/rust_workflow.sh`; `justfile`]

## Security Domain

Security enforcement is not explicitly disabled in `.planning/config.json`, so include security controls for Phase 22. [VERIFIED: `.planning/config.json`; research instructions]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | Phase 22 does not add an authentication surface. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| V3 Session Management | no | Phase 22 does not add session state. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| V4 Access Control | no | Phase 22 is local metadata/verifier work, not a runtime authorization path. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| V5 Input Validation | yes | Parse the JSON contract and metadata file contents at verifier boundaries; reject missing source refs, invalid statuses, unsafe paths, and malformed debt rows. [VERIFIED: `standards/core/architecture.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |
| V6 Cryptography | limited | Do not implement cryptography; reject private signing keys, tokens, certificates, raw payloads, and secret-bearing refs in metadata and generated artifacts. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] |

### Known Threat Patterns for Phase 22 Metadata

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Secret-bearing evidence refs in planning metadata | Information Disclosure | Forbidden-marker scans over checked-in contract, target metadata, and generated artifacts. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`] |
| Path traversal or generated artifact outside ignored root | Tampering / Information Disclosure | Require repo-relative refs under approved roots such as `build/ci-evidence/phase22/` or approved external schemes. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase20_release_candidate_artifacts.py`] |
| Overclaim wording for cutover, demotion, hardware, live service, signing, or release proof | Spoofing / Repudiation | Reject known overclaim strings unless a validated source row supports the claim, and keep external inputs pending/blocked. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`] |
| Silent non-blocking debt | Repudiation | Require owner, rationale, follow-up or expiry trigger, and source refs for every `non_blocking_debt` row. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md` - locked user decisions, scope, canonical refs, implementation ideas, no-overclaim constraints. [VERIFIED: initial required read]
- `.planning/REQUIREMENTS.md` - current v1.1 checkboxes and traceability rows. [VERIFIED: initial required read and `nl -ba`]
- `.planning/ROADMAP.md` - Phase 22 goal, success criteria, and stale Phase 21/22 progress table. [VERIFIED: initial required read and `nl -ba`]
- `.planning/STATE.md` - current state and stale current-focus/current-position metadata. [VERIFIED: initial required read and `nl -ba`]
- `.planning/v1.1-MILESTONE-AUDIT.md` - original audit findings and metadata debt. [VERIFIED: initial required read]
- Phase 14-18 `*-VALIDATION.md`, `*-SUMMARY.md`, and `*-VERIFICATION.md` - validation drift and source evidence for reconciliation. [VERIFIED: `sed -n` reads of those files; `rg -n 'wave_0_complete|pending|no - Wave 0|No - Wave 0|\\[ \\] \`tools/bazel' ...`]
- Phase 19/20/21 summaries and verification reports - functional gap closure evidence. [VERIFIED: `sed -n` reads of `.planning/phases/19-aggregate-cutover-evidence-ci/19-VERIFICATION.md`, `.planning/phases/20-release-candidate-artifact-production/20-VERIFICATION.md`, and `.planning/phases/21-final-readiness-result-consumption/21-VERIFICATION.md`]
- `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase19_aggregate_ci_evidence.py`, `tools/bazel/phase20_release_candidate_artifacts.py`, and their manifests/tests - existing verifier/contract patterns. [VERIFIED: `sed -n` reads and `python3 tools/bazel/phase18_cutover_review.py --contract-only`; `python3 tools/bazel/phase19_aggregate_ci_evidence.py --contract-only`; `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only`]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/testing.md`, `standards/core/verification.md` - repo and Bright Builds constraints. [VERIFIED: `cat` and `sed -n` reads of those files]
- `/Users/peterryszkiewicz/.codex/get-shit-done/workflows/audit-milestone.md` - milestone audit status matrix and Nyquist discovery rules. [VERIFIED: file read]

### Secondary (MEDIUM confidence)

- `gsd-tools.cjs` command probes for `init`, `state`, and lifecycle verification. [VERIFIED: command outputs]
- Local environment probes for Python, Bazel, just, Node, Git, and jq. [VERIFIED: command outputs]

### Tertiary (LOW confidence)

- None. [VERIFIED: no web or unverified third-party sources were used]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - verified from local tool versions and existing Phase 18/19/20 verifier files. [VERIFIED: `python3 --version`; `bazel --version`; `just --version`; `node --version`; `git --version`; `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase19_aggregate_ci_evidence.py`; `tools/bazel/phase20_release_candidate_artifacts.py`]
- Architecture: HIGH - based on locked Phase 22 decisions and repeated local Phase 18/19/20 patterns. [VERIFIED: `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`; `tools/bazel/*phase18*`; `tools/bazel/*phase19*`; `tools/bazel/*phase20*`]
- Pitfalls: HIGH - directly grounded in the v1.1 audit findings, current stale files, and no-overclaim decisions. [VERIFIED: `.planning/v1.1-MILESTONE-AUDIT.md`; `.planning/REQUIREMENTS.md`; `.planning/phases/14-simulator-evidence-gates/14-VALIDATION.md`; `.planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md`; `.planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md`; `.planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md`; `.planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md`]
- Open questions: MEDIUM - Phase 20 validation drift is verified, but whether to include it in Phase 22 cleanup is a scope decision for the planner/user because locked decisions name Phase 14-18 validation files. [VERIFIED: `.planning/phases/20-release-candidate-artifact-production/20-VALIDATION.md`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]

**Research date:** 2026-06-21
**Valid until:** 2026-06-28, because roadmap/state/audit metadata is fast-moving during active GSD phase execution. [VERIFIED: system-provided date `2026-06-21`; `.planning/phases/22-evidence-metadata-reconciliation/22-CONTEXT.md`]
