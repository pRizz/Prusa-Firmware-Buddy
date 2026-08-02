# Phase 32: Blocker Register and Evidence Triage - Research

**Researched:** 2026-07-03  
**Domain:** Blocker-register classifier and handoff bundle over Phase 31 final-intake evidence and existing v1.2 row artifacts. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase31_final_evidence_intake_contract.json; VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json]  
**Confidence:** HIGH. Phase 32 is tightly constrained by locked decisions and existing Phase 23-31 evidence machinery. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: .planning/phases/31-final-evidence-intake/31-VERIFICATION.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]

<user_constraints>
## User Constraints (from CONTEXT.md)

Source for this copied constraint section: [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

### Locked Decisions

## Implementation Decisions

### Register Input Model
- **D-01:** Use a small Phase 32 adapter layer over Phase 31 outputs and referenced source rows. Phase 31 remains the authoritative finality and provenance boundary.
- **D-02:** The adapter should read Phase 31 `final-intake-manifest.json`, `rejected-submissions.json`, and accepted stream receipts first, then follow each accepted receipt's `consumed_upstream_row_refs` to gather row-level evidence detail from Phase 23-26 outputs.
- **D-03:** Do not normalize Phase 23-26 upstream rows independently from Phase 31. Bypassing Phase 31 would duplicate stale-lifecycle, placeholder, redaction, source-ref, and secret checks.
- **D-04:** Do not treat direct Phase 31 receipt consumption alone as sufficient if it loses row-level status, criterion, artifact, or failure detail needed for TRIAGE-01 and TRIAGE-02.
- **D-05:** Treat retained-code and readiness rows as register inputs only through existing v1.2 and v1.3 handoff artifacts; do not invent a new retained-code or readiness decision schema in Phase 32.

### Canonical Blocker Taxonomy
- **D-06:** Build one canonical blocker register with orthogonal fields instead of one overloaded status. Required row fields should include `row_id`, `source_stream`, `source_ref`, `requirement_ids`, `affected_gate`, `row_problem_kind`, `blocker_kind`, `severity`, `owner_ref`, `required_next_action`, `decision_impact`, `proof_eligibility`, and `evidence_refs`.
- **D-07:** `blocker_kind` must be exactly one of `repair_item`, `exception_request`, or `unresolved_decision_blocker`. Derived queue-style outputs may group by those kinds, but the canonical register is the source of truth.
- **D-08:** Keep specific causes in `row_problem_kind`, with explicit values for failed, missing, stale, malformed, redaction_failed, source_ref_failed, secret_tainted, lifecycle_mismatch, unsafe_ref, exception_requested, non_final_placeholder, smoke_fixture, local_dry_run, prose_attestation, row_only_submission, and unknown_unclassified.
- **D-09:** Unknown or unmapped problem kinds must fail closed as unresolved decision blockers with critical severity until the policy map is updated or an explicit exception path is created in a later phase.
- **D-10:** Severity and owner defaults may be policy-derived, but generated rows must keep `owner_ref` and `required_next_action` explicit so maintainers can assign and audit work without reading raw evidence.

### Placeholder and Non-Final Proof Rejection
- **D-11:** Phase 32 should make Phase 31 rejected and quarantined submissions visible in the blocker register, but they must never satisfy proof eligibility.
- **D-12:** Only `accepted-final` Phase 31 receipts may be proof-eligible, and only after the referenced upstream row detail is loaded and classified.
- **D-13:** Quick/default placeholders, smoke fixtures, local-only dry runs, prose-only attestations, upstream-row-only submissions, stale lifecycle rows, redaction/source-ref failures, unsafe refs, and secret-bearing submissions should map to blocker rows with `proof_eligibility: ineligible`.
- **D-14:** Preserve the distinction between "visible for triage" and "accepted as final proof" in generated artifacts and redacted reports. Non-final rows are audit evidence of blockers, not cutover evidence.
- **D-15:** Do not reopen Phase 31 solely to add rejection codes unless Phase 32 cannot classify an actual final-intake rejection from existing reason text and finality metadata.

### Downstream Handoff Bundle
- **D-16:** Emit a normalized Phase 32 handoff bundle rather than only a human-readable report. Expected artifacts are `blocker-register.json`, `decision-impact-index.json`, `exception-request-register.json`, `residual-risk-request-register.json`, `downstream-handoff-manifest.json`, `redacted-blocker-register-report.md`, and contract snapshots.
- **D-17:** The handoff bundle should let Phase 33 consume exception requests, retained-code follow-ups, residual-risk prompts, and unresolved decision blockers without rereading raw evidence or secret-bearing packets.
- **D-18:** The handoff bundle should let Phase 34 final readiness consume blocker state, approved exception references, residual-risk references, and proof eligibility while preserving fail-closed reference demotion.
- **D-19:** The handoff bundle should let Phase 35 link blockers, exceptions, residual risks, evidence packets, retained-code decisions, readiness results, and demotion decisions in the go/no-go artifact.
- **D-20:** Derived per-kind views are allowed for maintainer ergonomics only if they are generated from the canonical register and include stable row ids back to the canonical rows.

### the agent's Discretion
- The agent may choose the concrete Python module split, provided Phase 32 remains a thin adapter plus classifier over Phase 31 and existing v1.2/v1.3 artifacts.
- The agent may choose exact enum spellings where not specified above, but the spellings must be documented in the Phase 32 contract and covered by tests.
- The agent may choose whether to generate one script with subcommands or one verifier script plus helper functions.
- The agent may choose exact Bazel labels and `just` target names, but they should follow existing patterns such as `phase31_verify`, `phase31_verify_tests`, and `phase32-verify`.

### Deferred Ideas (OUT OF SCOPE)

- Actual exception approval, retained-code acceptance, residual-risk acceptance, final-readiness approval, and reference-demotion decisions belong to Phase 33 and Phase 34.
- Final readiness packet generation and demotion dry-run behavior belong to Phase 34.
- The go/no-go cutover decision artifact belongs to Phase 35.
- Broad retained vendor/HAL replacement, new printer behavior, and long-run dashboards remain future milestone work unless Phase 32 reveals a narrow decision-blocking defect.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TRIAGE-01 | Maintainer can aggregate all consumed simulator, hardware/media/safety, live-service, release/signing, upstream-result, retained-code, and readiness rows into a single blocker register. [VERIFIED: .planning/REQUIREMENTS.md] | Read Phase 31 manifest/rejections/receipts first, follow receipt `consumed_upstream_row_refs`, and add retained-code/readiness rows from Phase 27/28 handoffs. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| TRIAGE-02 | Maintainer can classify each failed, missing, stale, malformed, redaction-failed, or exceptioned row with owner, severity, affected gate, required next action, and decision impact. [VERIFIED: .planning/REQUIREMENTS.md] | Use a Phase 32-owned policy map from status/finality/reason fields to `row_problem_kind`, `blocker_kind`, `severity`, `owner_ref`, `required_next_action`, and `decision_impact`; unknowns fail closed. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| TRIAGE-03 | Maintainer can prove quick/default placeholder outputs, smoke fixtures, and local-only dry-run rows are rejected as final cutover proof. [VERIFIED: .planning/REQUIREMENTS.md] | Preserve Phase 31 `quarantined-non-final` and `rejected-final` rows as visible blockers with `proof_eligibility: ineligible`; accepted-final receipts are proof-eligible only after upstream detail loads. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: build/ci-evidence/phase31/final-intake-manifest.json; VERIFIED: build/ci-evidence/phase31/rejected-submissions.json] |
</phase_requirements>

## Summary

Phase 32 should be implemented as a standard-library Python verifier plus JSON contract that adapts Phase 31 outputs and existing v1.2/v1.3 evidence rows into one canonical blocker register. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] The core implementation should classify rows with a Phase 32-owned policy map while preserving Phase 31 as the finality/provenance boundary and preserving Phase 23-28 as source-row authorities. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase31_final_evidence_intake_contract.json; VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json]

The canonical register should be the only source of truth for blocker state, and derived artifacts should be generated from it by stable `row_id`. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] The classifier should keep `row_problem_kind` separate from `blocker_kind`, because redaction/source-ref/secret/lifecycle failures, exception requests, and placeholder proof failures need different downstream actions. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

Phase 32 must not approve exceptions, accept retained code, decide final readiness, authorize demotion, or publish the cutover verdict. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: .planning/ROADMAP.md] Its outputs should be a secret-safe handoff bundle under `build/ci-evidence/phase32`, with redacted markdown as a derived view only. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: .gitignore]

**Primary recommendation:** Build `tools/bazel/phase32_blocker_register_triage.py`, `tools/bazel/phase32_blocker_register_triage_test.py`, and `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` as a thin adapter plus pure classifier over Phase 31/27/28 artifacts, then wire `phase32_verify`, `phase32_verify_tests`, and `just phase32-verify` following the Phase 31 pattern. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]

## Project Constraints (from AGENTS.md)

- Read `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant `standards/` pages before plan, review, implementation, or audit work. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md; VERIFIED: standards/index.md]
- `standards-overrides.md` exists and contains no active task-specific exception beyond placeholder table content. [VERIFIED: standards-overrides.md]
- Keep Bright Builds managed files unedited unless the task is upstream rule maintenance; repo-specific deviations belong in `standards-overrides.md`. [VERIFIED: AGENTS.md; VERIFIED: AGENTS.bright-builds.md]
- Use `rg` for text searches, and prefer semantic/LSP tools when available. [VERIFIED: AGENTS.md]
- No project-local skill directories were found under `.claude/skills` or `.agents/skills`. [VERIFIED: `find .claude/skills .agents/skills -maxdepth 2 -name SKILL.md`]
- Bazel is the authoritative build system for planned work, and a `justfile` developer facade is required. [VERIFIED: AGENTS.md; VERIFIED: .planning/PROJECT.md]
- Before creating a git commit in this Rust-containing repository, run `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`. [VERIFIED: AGENTS.md; VERIFIED: Cargo.toml]
- Prefer functional core / imperative shell for business logic: pure classifier functions should take parsed rows and return register rows, while file I/O and output writes stay in the CLI shell. [VERIFIED: standards/core/architecture.md; VERIFIED: AGENTS.bright-builds.md]
- Parse boundary JSON into domain-shaped records early, then classify checked rows rather than passing unchecked dictionaries through all policy logic. [VERIFIED: standards/core/architecture.md]
- Prefer early returns, shallow control flow, and `maybe_` prefixes for internal absence-like values where practical. [VERIFIED: standards/core/code-shape.md; VERIFIED: AGENTS.bright-builds.md]
- Unit-test pure/business logic, keep each unit test focused on one concern, and delineate Arrange, Act, and Assert in non-trivial tests. [VERIFIED: standards/core/testing.md; VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py]
- Run repo-native verification before completion; for Phase 32 this should include the focused Python test, contract/security/wiring modes, `just phase32-verify`, and `git diff --check` after implementation. [VERIFIED: standards/core/verification.md; VERIFIED: justfile; VERIFIED: tools/bazel/rust_workflow.sh]
- Do not use standalone `---` body separators in GSD Markdown artifacts because repo tooling parses YAML frontmatter delimiters specially. [VERIFIED: AGENTS.md]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python standard library | Python 3.14.4 available locally | Implement the verifier CLI, JSON loading/writing, row classification, hashing, path validation, and `unittest` tests. | Phase 23-31 evidence verifiers use standard-library Python scripts with direct test files. [VERIFIED: `python3 --version`; VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py] |
| JSON contracts under `tools/bazel/manifests/` | Repo-current tracked files | Document Phase 32 schema, policy map, generated artifacts, and source contract refs. | Phase 23-31 verifier behavior is governed by tracked JSON contracts in this directory. [VERIFIED: tools/bazel/manifests/phase31_final_evidence_intake_contract.json; VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json] |
| Bazel `shell_binary` targets | Bazel 9.1.1 available locally | Expose `phase32_verify` and `phase32_verify_tests`. | Existing phase verifiers are exposed as Bazel `shell_binary` targets and root aliases. [VERIFIED: `bazel --version`; VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel] |
| `just` facade | just 1.48.0 available locally | Provide `just phase32-verify`. | Existing phase recipes run tests before the verifier. [VERIFIED: `just --version`; VERIFIED: justfile] |
| Existing Phase 31 verifier and contract | Repo-current tracked files | Treat finality, receipts, rejected submissions, provenance, and accepted upstream-row refs as the Phase 32 input boundary. | Phase 32 decisions require Phase 31 to remain authoritative for finality and provenance. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| Existing Phase 27/28 retained-code/readiness outputs | Repo-current generated output shape | Include retained-code, residual-risk, exception, readiness, and demotion-blocking rows without inventing new approval schemas. | Phase 32 decisions require retained-code and readiness inputs only through existing handoff artifacts. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| `jq` | jq-1.7.1-apple available locally | Inspect JSON artifacts during development and debug contract snapshots. | Use as a developer aid only; implementation should use Python JSON parsing. [VERIFIED: `jq --version`; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| Git | git 2.53.0 available locally | Review diffs and verify only intended files changed. | Use before final handoff; current worktree has an unrelated `.planning/config.json` modification that Phase 32 research must not revert. [VERIFIED: `git --version`; VERIFIED: `git status --short`] |
| Cargo | cargo 1.91.1 available locally | Rust pre-commit sequence if a commit is created or Rust files are touched. | Phase 32 implementation should not need Rust edits, but repo instructions require Cargo checks before commits in this Rust project. [VERIFIED: `cargo --version`; VERIFIED: AGENTS.md] |
| Bash | GNU bash 3.2.57 available locally | Existing `tools/bazel/rust_workflow.sh` facade. | Use through Bazel `shell_binary`; do not add complex foreign-language logic inside shell strings. [VERIFIED: `bash --version`; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: standards/core/code-shape.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Phase 32 adapter over Phase 31 plus referenced rows | Direct Phase 23-26 normalization | Rejected by D-03 because it bypasses Phase 31 finality/provenance checks and duplicates lifecycle, placeholder, redaction, source-ref, and secret checks. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Canonical blocker register plus derived views | Separate independent repair/exception/decision queues | Rejected by D-20 unless derived views come from stable canonical register rows. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Explicit orthogonal fields | One overloaded status string | Rejected by D-06 and D-07 because problem kind, blocker kind, severity, affected gate, next action, and decision impact have different downstream meanings. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Secret-safe machine-readable handoff bundle | Human-readable report only | Rejected by D-16 through D-19 because Phase 33-35 must consume structured blocker, exception, residual-risk, proof, and decision-impact data. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Phase 32 approval semantics | Approve exceptions, retained code, readiness, demotion, or cutover verdict in Phase 32 | Rejected by the Phase boundary and deferred ideas. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: .planning/ROADMAP.md] |

**Installation:** No new packages are required. [VERIFIED: existing Phase 23-31 scripts use Python standard-library imports; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]

**Version verification:** Local tool versions were verified with these commands. [VERIFIED: environment audit commands]

```bash
python3 --version
bazel --version
just --version
jq --version
git --version
cargo --version
```

No `npm view` verification applies because Phase 32 should not add npm packages. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
+-- manifests/
|   `-- phase32_blocker_register_triage_contract.json  # Phase 32 schema, policy map, generated artifacts, source refs. [VERIFIED: tools/bazel/manifests/phase31_final_evidence_intake_contract.json]
+-- phase32_blocker_register_triage.py                 # Thin CLI shell plus pure blocker classifier. [VERIFIED: standards/core/architecture.md; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]
`-- phase32_blocker_register_triage_test.py            # unittest coverage with Arrange/Act/Assert comments. [VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py]

build/ci-evidence/phase32/
+-- blocker-register.json                              # Canonical source of truth for blocker rows. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
+-- decision-impact-index.json                         # Derived from canonical register rows. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
+-- exception-request-register.json                    # Derived exception-request view keyed by canonical row_id. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
+-- residual-risk-request-register.json                # Derived residual-risk view keyed by canonical row_id. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
+-- downstream-handoff-manifest.json                   # Phase 33-35 input manifest. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
+-- redacted-blocker-register-report.md                # Human-readable derived report, not source of truth. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
`-- contract-snapshots/
    +-- phase32_blocker_register_triage_contract.json
    +-- phase31_final_evidence_intake_contract.json
    +-- phase27_retained_code_acceptance_decisions_contract.json
    `-- phase28_final_readiness_packet_contract.json
```

### Pattern 1: Phase 31 First, Then Referenced Row Detail

**What:** Load `build/ci-evidence/phase31/final-intake-manifest.json`, `build/ci-evidence/phase31/rejected-submissions.json`, and each accepted receipt before loading any Phase 23-26 source row. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]

**When to use:** Use for every simulator, hardware/media/safety, live-service, release/signing, and upstream-result blocker input. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

**Implementation guidance:** Rejected or quarantined Phase 31 rows become visible blocker rows with `proof_eligibility: ineligible`, while accepted receipts are followed through `consumed_upstream_row_refs` for row-level status, criterion, artifact, and failure detail. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]

### Pattern 2: Pure Classifier Over Checked Input Rows

**What:** Parse boundary JSON once, then call pure functions such as `classify_problem_kind(...)`, `blocker_policy_for(...)`, and `build_blocker_row(...)` to transform checked rows into canonical register rows. [VERIFIED: standards/core/architecture.md; VERIFIED: standards/core/testing.md]

**When to use:** Use for row-level classification, derived register generation, and tests that exercise problem-kind and blocker-kind rules without filesystem setup. [VERIFIED: standards/core/architecture.md; VERIFIED: tools/bazel/phase28_final_readiness_packet_test.py]

**Required policy:** Unknown or unmapped problem kinds must produce `row_problem_kind: unknown_unclassified`, `blocker_kind: unresolved_decision_blocker`, `severity: critical`, and `proof_eligibility: ineligible`. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

### Pattern 3: Orthogonal Taxonomy, Not Status Reuse

**What:** Preserve source `status`, `finality_status`, `redaction_status`, `source_ref_status`, `exception_status`, and lifecycle fields in evidence metadata, but derive separate Phase 32 fields for problem kind, blocker kind, severity, owner, action, and decision impact. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

**When to use:** Use whenever a source status such as `blocked`, `pending-live-input`, `exception-requested`, `quarantined-non-final`, or `rejected-redaction` would otherwise hide the exact remediation path. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json; VERIFIED: build/ci-evidence/phase31/rejected-submissions.json; VERIFIED: build/ci-evidence/phase28/blocker-summary.json]

### Pattern 4: Generated Views From Canonical Register

**What:** Generate `decision-impact-index.json`, `exception-request-register.json`, `residual-risk-request-register.json`, and `redacted-blocker-register-report.md` from `blocker-register.json`. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

**When to use:** Use after canonical register rows have stable IDs and complete owner/action/severity fields. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

**Invariant:** Derived rows must include canonical `row_id` references so downstream phases can audit that no derived view drifted from the source register. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

### Recommended Classifier Policy Surface

| Source signal | `row_problem_kind` | `blocker_kind` | Default severity | Proof eligibility | Action pattern |
|---------------|--------------------|----------------|------------------|-------------------|----------------|
| `finality_status` is `quarantined-non-final` with quick/default reason | `non_final_placeholder` | `repair_item` | high | `ineligible` | Supply real final evidence through Phase 31. [VERIFIED: build/ci-evidence/phase31/rejected-submissions.json; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Reason contains smoke/local-only proof markers | `smoke_fixture` or `local_dry_run` | `repair_item` | high | `ineligible` | Replace with sanitized real-run evidence. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase26_release_signing_upstream_evidence.py] |
| Reason indicates prose-only or row-only submission | `prose_attestation` or `row_only_submission` | `repair_item` | high | `ineligible` | Re-submit through the source validator and Phase 31. [VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py] |
| Required manifest, receipt, source row, or supporting artifact is absent | `missing` | `repair_item` | high | `ineligible` | Regenerate or supply the missing upstream artifact. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| Source lifecycle mismatch or stale lifecycle text | `stale` or `lifecycle_mismatch` | `repair_item` | critical | `ineligible` | Re-run evidence with current lifecycle or fix stale handoff. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| JSON parse/type/required-field failure | `malformed` | `repair_item` | high | `ineligible` | Repair the submitted artifact schema. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py] |
| `redaction_status` failed or rejected-redaction | `redaction_failed` | `repair_item` | critical | `ineligible` | Re-sanitize evidence before any exception path. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| `source_ref_status` failed | `source_ref_failed` | `repair_item` | critical | `ineligible` | Fix refs before downstream use. [VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| Forbidden secret field/text marker found | `secret_tainted` | `repair_item` | critical | `ineligible` | Remove secret material and retain only external refs/digests. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| Unsafe artifact ref or symlink/path escape | `unsafe_ref` | `repair_item` | critical | `ineligible` | Move artifact refs under allowed roots or external namespace. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet_test.py] |
| Source row status is `exception-requested` | `exception_requested` | `exception_request` | medium | `ineligible` until later approval | Route to Phase 33 exception decision input. [VERIFIED: tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json; VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json; VERIFIED: .planning/ROADMAP.md] |
| Source row status is `failed` or non-passing blocked/pending status | `failed` or `missing` | `repair_item` unless exception metadata is present | high | `ineligible` | Repair evidence or create an explicit exception request. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json; VERIFIED: build/ci-evidence/phase28/blocker-summary.json] |
| Source signal does not match any policy branch | `unknown_unclassified` | `unresolved_decision_blocker` | critical | `ineligible` | Update Phase 32 policy map or route to later explicit decision. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |

### Anti-Patterns to Avoid

- **Bypassing Phase 31:** Do not scan Phase 23-26 generated rows directly as the primary intake source. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
- **Embedding approval semantics:** Do not mark exceptions, retained code, readiness, demotion, or cutover approved in Phase 32 outputs. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: .planning/ROADMAP.md]
- **Report-only triage:** Do not make `redacted-blocker-register-report.md` the only output because Phase 33-35 need machine-readable rows. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
- **Independent derived queues:** Do not hand-edit exception/residual-risk queues independently from the canonical register. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
- **Accepting non-final rows as proof:** Do not let quick/default, smoke, local dry-run, prose, row-only, stale, redaction-failed, source-ref-failed, unsafe-ref, or secret-tainted rows become proof-eligible. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Stream-specific evidence validation | New simulator/hardware/live/release schema checks inside Phase 32 | Phase 31 receipts plus Phase 23-26 referenced rows | Locked decisions keep Phase 31 and Phase 23-26 authoritative. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Finality/proof boundary | A Phase 32 finality evaluator over raw source outputs | Phase 31 `finality_status`, receipts, and rejected/quarantined submissions | Phase 31 already enforces finality, real-evidence flags, redaction, source-ref, lifecycle, allowed refs, and secret checks. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: .planning/phases/31-final-evidence-intake/31-VERIFICATION.md] |
| Exception approval | `exception_request` rows that become approved in Phase 32 | Phase 33 decision inputs | Phase 32 only classifies and hands off exception requests. [VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Retained-code acceptance | A new retained-code decision schema | Phase 27/Phase 33 retained-code handoff/decision artifacts | Phase 32 decisions prohibit inventing a retained-code schema. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json] |
| Final readiness and demotion | A readiness verdict or demotion authorization in Phase 32 | Phase 34 final readiness/demotion dry run | Roadmap assigns readiness/demotion to Phase 34 and keeps demotion explicit. [VERIFIED: .planning/ROADMAP.md; VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json] |
| Secret scanning from scratch | A brand-new secret vocabulary that diverges from prior phases | Reuse existing forbidden field/text patterns or centralize copied patterns in Phase 32 tests | Phase 31/27/28 already reject private keys, certs, tokens, raw crash dumps, raw logs, payloads, and credential markers. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase27_retained_code_acceptance_decisions.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| Build workflow | One-off shell commands outside Bazel/just | Bazel `shell_binary`, root aliases, and `just phase32-verify` | Existing phase workflows expose tests and verifier through Bazel and `just`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: justfile] |

**Key insight:** Phase 32's hard part is taxonomy and traceable handoff, not evidence validation. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] Custom validation or approval logic would duplicate upstream gates and increase the chance that non-final or secret-tainted evidence is promoted incorrectly. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

## Common Pitfalls

### Pitfall 1: Losing Row-Level Detail Behind Receipts

**What goes wrong:** The register contains only Phase 31 receipt rows and cannot classify scenario/criterion failures. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Why it happens:** Receipts are provenance wrappers and may not carry enough source status, criterion, artifact, or failure detail for TRIAGE-01 and TRIAGE-02. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]  
**How to avoid:** Follow `consumed_upstream_row_refs` for accepted receipts and classify loaded source rows; keep rejected/quarantined submissions as direct non-proof blockers. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Warning signs:** `blocker-register.json` has one row per stream but no criterion/source row references. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

### Pitfall 2: Treating Quarantined Rows as Cutover Evidence

**What goes wrong:** Quick/default smoke output is visible and accidentally counted as proof. [VERIFIED: build/ci-evidence/phase31/final-intake-manifest.json; VERIFIED: build/ci-evidence/phase31/rejected-submissions.json]  
**Why it happens:** Triage visibility and proof eligibility are not modeled as separate fields. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**How to avoid:** Always set `proof_eligibility: ineligible` for rejected, quarantined, placeholder, smoke, local dry-run, prose, row-only, stale, redaction/source-ref failed, unsafe, and secret-tainted rows. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Warning signs:** A derived report says a stream was "seen" or "present" without saying proof is ineligible. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

### Pitfall 3: Collapsing Problem Kind and Blocker Kind

**What goes wrong:** A redaction failure, stale row, exception request, and missing proof all look like the same generic blocker. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Why it happens:** The implementation reuses source `status` as the only triage field. [VERIFIED: tools/bazel/manifests/phase18_cutover_review_contract.json]  
**How to avoid:** Derive `row_problem_kind` and `blocker_kind` independently from source fields and policy map. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Warning signs:** `exception_requested` rows appear in the same queue as `redaction_failed` rows without different next actions. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json]

### Pitfall 4: Underclassifying Unknown Statuses

**What goes wrong:** A new source status or rejection reason is silently treated as medium severity or repairable proof absence. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Why it happens:** The policy map defaults to a benign fallback. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**How to avoid:** Fail closed as `unknown_unclassified`, `unresolved_decision_blocker`, `critical`, and `ineligible`. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Warning signs:** Tests do not include an unknown status/reason fixture. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

### Pitfall 5: Secret or Unsafe Ref Propagation Into Reports

**What goes wrong:** The redacted report copies raw reason text, artifact paths, or payload snippets that contain secrets or unsafe references. [VERIFIED: .planning/STATE.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]  
**Why it happens:** The human-readable report is generated from raw evidence instead of the sanitized canonical register. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**How to avoid:** Generate markdown only from canonical rows, use sanitized refs/digests, and run a `--security-only` scan over generated outputs. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]  
**Warning signs:** Report generation reads raw Phase 23-26 evidence packets or service payloads. [VERIFIED: .planning/STATE.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

### Pitfall 6: Reopening Phase 31 for Better Rejection Codes Too Early

**What goes wrong:** Phase 32 planning expands into Phase 31 schema churn instead of classifying existing reason/finality metadata. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Why it happens:** Classifier policy is designed around ideal structured rejection codes that do not yet exist for every rejection path. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py]  
**How to avoid:** Map actual Phase 31 reason text and finality metadata first, and reopen Phase 31 only if an actual final-intake rejection cannot be classified. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]  
**Warning signs:** The Phase 32 plan includes Phase 31 implementation edits before demonstrating an unclassifiable real rejection. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

## Code Examples

Verified patterns from local source:

### Boundary Load Order

```python
# Source: tools/bazel/phase31_final_evidence_intake.py and Phase 32 D-02.
def load_phase31_inputs(root: Path, phase31_dir: Path) -> Phase31Inputs:
    manifest = load_json(root, phase31_dir / "final-intake-manifest.json")
    rejected = load_json(root, phase31_dir / "rejected-submissions.json")
    receipt_paths = require_string_list(manifest, "receipt_refs", "final-intake-manifest")
    receipts = [load_json(root, Path(receipt_path)) for receipt_path in receipt_paths]
    return Phase31Inputs(manifest=manifest, rejected=rejected, receipts=receipts)
```

This pattern keeps Phase 31 finality and provenance as the first boundary before any Phase 23-26 source-row detail is loaded. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py]

### Fail-Closed Problem Classification

```python
# Source: Phase 32 D-08/D-09 and Phase 28 hard-blocker pattern.
def classify_problem_kind(source: CheckedSourceRow) -> str:
    if source.finality_status in {"rejected-final", "quarantined-non-final"}:
        return classify_non_final_reason(source.reason)
    if source.redaction_status != "passed":
        return "redaction_failed"
    if source.source_ref_status != "passed":
        return "source_ref_failed"
    if source.status == "exception-requested":
        return "exception_requested"
    if source.status in {"failed", "blocked"}:
        return "failed"
    return "unknown_unclassified"
```

The final fallback must be `unknown_unclassified` rather than a passing or repairable default. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase28_final_readiness_packet.py]

### Derived Views From Canonical Rows

```python
# Source: Phase 32 D-16/D-20.
def exception_request_rows(register_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": [
            {
                "row_id": row["row_id"],
                "source_ref": row["source_ref"],
                "owner_ref": row["owner_ref"],
                "required_next_action": row["required_next_action"],
                "decision_impact": row["decision_impact"],
            }
            for row in register_rows
            if row["blocker_kind"] == "exception_request"
        ]
    }
```

Derived views should not add independent blocker semantics that are absent from `blocker-register.json`. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Local quick/smoke evidence could be useful workflow proof but not final proof. [VERIFIED: tools/bazel/phase23_simulator_evidence_execution.py; VERIFIED: tools/bazel/phase24_hardware_media_safety_evidence_execution.py] | Phase 31 final intake quarantines quick/default output as non-final and writes rejected submissions. [VERIFIED: .planning/phases/31-final-evidence-intake/31-VERIFICATION.md; VERIFIED: build/ci-evidence/phase31/rejected-submissions.json] | Phase 31 completed 2026-07-03. [VERIFIED: .planning/phases/31-final-evidence-intake/31-01-SUMMARY.md] | Phase 32 can use Phase 31 finality as the proof boundary. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Phase 26 quick rows could default to blocked/pending without real Phase 23-25 compact inputs. [VERIFIED: .planning/milestones/v1.2-phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md] | Phase 29 added explicit Phase 23/24/25 compact upstream row input flow into Phase 26 and Phase 28 evidence refs. [VERIFIED: .planning/milestones/v1.2-phases/29-upstream-evidence-flow-closure/29-01-SUMMARY.md] | Phase 29 completed 2026-06-25. [VERIFIED: .planning/ROADMAP.md] | Phase 32 should look for consumed upstream rows rather than assuming default quick rows are final evidence. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Phase 28 blocker summary is readiness-centric and compact. [VERIFIED: build/ci-evidence/phase28/blocker-summary.json] | Phase 32 needs a fuller canonical blocker register with owner, severity, affected gate, next action, decision impact, proof eligibility, and evidence refs. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] | Phase 32 current scope. [VERIFIED: .planning/ROADMAP.md] | Do not reuse Phase 28 `blocker-summary.json` as the Phase 32 register; use its vocabulary as downstream context only. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| Phase 27 produced retained-code/residual-risk/exception handoff artifacts for v1.2. [VERIFIED: tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json] | Phase 32 must treat retained-code and readiness rows as inputs only through existing v1.2 and v1.3 handoff artifacts. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] | Phase 27 completed 2026-06-25. [VERIFIED: .planning/ROADMAP.md] | Register rows can link retained-code and residual-risk items without approving them. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |

**Deprecated/outdated:**

- Prose-only, row-only, local-smoke, template-only, quick/default, and local dry-run evidence are not acceptable as final cutover proof. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py]
- Green evidence alone must not imply reference demotion approval. [VERIFIED: .planning/ROADMAP.md; VERIFIED: tools/bazel/manifests/phase28_final_readiness_packet_contract.json]
- Hard blockers such as redaction/source-ref/lifecycle/unsafe/secret failures must not be transformed into accepted risk by Phase 32 classification. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| - | No `[ASSUMED]` claims were used. | All sections | No user confirmation needed from this research alone. |

## Open Questions (RESOLVED)

1. **Should Phase 32 add structured rejection codes back to Phase 31?**
   - What we know: Phase 32 D-15 says not to reopen Phase 31 unless actual final-intake rejection reason text and finality metadata cannot be classified. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
   - Resolution: Plan Phase 32 without Phase 31 edits. Classify current Phase 31 reason text and finality metadata first, and include a fail-closed unknown-rejection fixture. Reopen Phase 31 only if an actual final-intake rejection cannot be classified from existing reason/finality metadata. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: standards/core/testing.md]

2. **What exact `owner_ref` strings should the policy map emit?**
   - What we know: Phase 27 has owner strings for retained-code residual-risk rows, and Phase 27 contract has sensitive-role values including `safety-maintainer`, `release-maintainer`, and `network-security-maintainer`. [VERIFIED: build/ci-evidence/phase27/residual-risk-register.json; VERIFIED: tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json]
   - Resolution: Define the owner policy in `phase32_blocker_register_triage_contract.json`, use existing Phase 27 owner values when present, and use these Phase 32 stream/gate defaults for Phase 31 and upstream rows: `simulator -> simulator-maintainer`, `hardware-media-safety -> safety-maintainer`, `live-service -> network-security-maintainer`, `release-signing -> release-maintainer`, `upstream-result -> release-maintainer`, `retained-code -> retained-code-maintainer`, `readiness -> readiness-maintainer`, and `unknown -> cutover-maintainer`. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: build/ci-evidence/phase27/residual-risk-register.json]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 32 verifier and tests | yes | 3.14.4 | Blocking if unavailable because existing phase verifiers use Python. [VERIFIED: `python3 --version`; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| Bazel | `phase32_verify` / `phase32_verify_tests` targets | yes | 9.1.1 | Direct Python commands can run during development, but final workflow should wire Bazel. [VERIFIED: `bazel --version`; VERIFIED: tools/bazel/BUILD.bazel] |
| `just` | Developer facade `just phase32-verify` | yes | 1.48.0 | Bazel labels can run directly, but project constraints require `justfile` workflow. [VERIFIED: `just --version`; VERIFIED: AGENTS.md; VERIFIED: justfile] |
| Bash | Existing `rust_workflow.sh` dispatch | yes | 3.2.57 | No fallback needed for current shell facade. [VERIFIED: `bash --version`; VERIFIED: tools/bazel/rust_workflow.sh] |
| Git | Diff review and optional commit workflow | yes | 2.53.0 | None for repository workflow. [VERIFIED: `git --version`] |
| Cargo | Required before commits in Rust project; required if Rust files are touched | yes | 1.91.1 | Avoid Rust edits for Phase 32; if committing, follow AGENTS sequence. [VERIFIED: `cargo --version`; VERIFIED: AGENTS.md] |
| `jq` | Developer inspection only | yes | 1.7.1-apple | Python JSON parsing. [VERIFIED: `jq --version`; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| pre-commit | Optional repo hook command, not required by Phase 32 pattern | no | - | Use repo-native phase tests and `git diff --check`; do not install tooling solely for research. [VERIFIED: `command -v pre-commit`; VERIFIED: standards/core/verification.md] |

**Missing dependencies with no fallback:** None found for Phase 32 implementation-critical paths. [VERIFIED: environment audit commands]

**Missing dependencies with fallback:** `pre-commit` is not available locally, but Phase 32 can rely on direct Python/Bazel/just verification and `git diff --check` unless local implementation changes require hook-specific checks. [VERIFIED: `command -v pre-commit`; VERIFIED: standards/core/verification.md]

## Validation Architecture

Nyquist validation applies because `.planning/config.json` explicitly sets `workflow.nyquist_validation` to `true`. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` direct test script plus Bazel `shell_binary` wrapper. [VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py; VERIFIED: tools/bazel/BUILD.bazel] |
| Config file | `pyproject.toml` has pytest integration-test settings, but phase verifier tests run as direct Python scripts. [VERIFIED: pyproject.toml; VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py] |
| Quick run command | `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` after Wave 0 creates the file. [VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py] |
| Full suite command | `just phase32-verify` after Bazel/root/just wiring. [VERIFIED: justfile; VERIFIED: tools/bazel/rust_workflow.sh] |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| TRIAGE-01 | Aggregates Phase 31 rejected/quarantined rows, accepted receipts with consumed upstream row refs, Phase 26 row table detail, Phase 27 retained-code/residual-risk/exception rows, and Phase 28 readiness blockers into one canonical register. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] | unit/integration wrapper | `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` | No, Wave 0 required. [VERIFIED: `find .planning/phases/32-blocker-register-and-evidence-triage -maxdepth 1 -type f`] |
| TRIAGE-02 | Classifies failed, missing, stale, malformed, redaction-failed, source-ref-failed, unsafe, secret-tainted, exception-requested, and unknown rows with explicit owner, severity, affected gate, next action, and decision impact. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] | unit classifier | `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` | No, Wave 0 required. [VERIFIED: `rg -n "phase32_blocker" tools/bazel .planning/phases/32-blocker-register-and-evidence-triage`] |
| TRIAGE-03 | Rejects quick/default placeholders, smoke fixtures, local dry runs, prose-only, and row-only inputs as final proof while keeping them visible as blockers. [VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: build/ci-evidence/phase31/rejected-submissions.json] | unit/security/contract | `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` | No, Wave 0 required. [VERIFIED: `rg -n "phase32_blocker" tools/bazel .planning/phases/32-blocker-register-and-evidence-triage`] |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` plus the touched verifier mode such as `--contract-only`, `--security-only`, `--wiring-only`, or `--quick`. [VERIFIED: standards/core/testing.md; VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py]
- **Per wave merge:** Run `just phase32-verify` after wiring exists. [VERIFIED: standards/core/verification.md; VERIFIED: justfile]
- **Phase gate:** Run `python3 -m py_compile tools/bazel/phase32_blocker_register_triage.py tools/bazel/phase32_blocker_register_triage_test.py`, the focused test file, `--contract-only`, `--security-only`, `--wiring-only`, `--quick --output-dir build/ci-evidence/phase32`, `bazel run //tools/bazel:phase32_verify_tests`, `bazel run //tools/bazel:phase32_verify`, `just phase32-verify`, and `git diff --check`; run the Cargo sequence before commit if committing in this Rust repo. [VERIFIED: .planning/phases/31-final-evidence-intake/31-VERIFICATION.md; VERIFIED: AGENTS.md]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` - Phase 32 schema, source refs, policy map, output list, and verification commands. [VERIFIED: no existing Phase 32 implementation from `rg -n "phase32_blocker" tools/bazel`]
- [ ] `tools/bazel/phase32_blocker_register_triage.py` - CLI, boundary parsing, pure classifier, output writer, security scan, and wiring check. [VERIFIED: no existing Phase 32 implementation from `rg -n "phase32_blocker" tools/bazel`]
- [ ] `tools/bazel/phase32_blocker_register_triage_test.py` - tests for accepted-final rows, rejected-final rows, quarantined non-final rows, unknown policy fail-closed behavior, placeholder rejection, owner/action/severity requirements, derived-view consistency, no-secret propagation, and wiring order. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
- [ ] Root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` entries for `phase32_verify` and `phase32_verify_tests`. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: BUILD.bazel; VERIFIED: tools/bazel/rust_workflow.sh; VERIFIED: justfile]
- [ ] `.planning/phases/32-blocker-register-and-evidence-triage/32-VALIDATION.md` - Nyquist metadata after implementation evidence exists. [VERIFIED: .planning/config.json; VERIFIED: .planning/phases/31-final-evidence-intake/31-VALIDATION.md]

## Security Domain

OWASP currently identifies ASVS as a basis for testing web application technical security controls and lists ASVS 5.0.0 as the latest stable version. [CITED: https://owasp.org/www-project-application-security-verification-standard/] The OWASP Cheat Sheet ASVS index says it is based on ASVS 5.0.x and lists the 5.0 category names used below. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

### Applicable ASVS Categories

| ASVS 5.0 Category | Applies | Standard Control |
|-------------------|---------|------------------|
| V1 Encoding and Sanitization | yes | Reject forbidden field/text patterns and generate reports from sanitized canonical rows only. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| V2 Validation and Business Logic | yes | Parse JSON at boundaries, enforce policy-map classification, and fail closed on unknown problem kinds. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: standards/core/architecture.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| V3 Web Frontend Security | no | Phase 32 is a local CLI/generated-artifact workflow with no web frontend. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| V4 API and Web Service | no direct network API | Phase 32 has no service endpoint and reads local/generated JSON evidence. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| V5 File Handling | yes | Restrict inputs/outputs to repo-relative evidence roots, reject traversal/symlink escapes, and retain external refs instead of raw payloads. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet.py] |
| V6 Authentication | no direct authentication | Phase 32 should classify owner/action fields but not authenticate users or approvers. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| V7 Session Management | no | Phase 32 has no sessions. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| V8 Authorization | limited | Do not infer maintainer authorization, exception approval, retained-code acceptance, readiness approval, demotion, or cutover verdict from evidence state. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| V9 Self-contained Tokens | indirect | Reject token-like secret fields/text and never retain token material. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| V10 OAuth and OIDC | no direct OAuth/OIDC flow | Phase 32 only handles redacted evidence references, not OAuth/OIDC protocol flows. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| V11 Cryptography | yes for digests/refs, no key handling | Preserve digests/refs and reject private keys, certificate private material, signing payload bytes, and raw key values. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: .planning/STATE.md] |
| V12 Secure Communication | indirect | Preserve live-service/TLS evidence status and refs without copying TLS keylogs, tokens, or service payloads. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: tools/bazel/phase25_live_service_evidence_execution.py; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| V13 Configuration | yes | Keep secret-bearing environment/config values out of retained artifacts and reports. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/STATE.md; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| V14 Data Protection | yes | Retain sanitized refs, hashes, statuses, and decision-impact metadata rather than raw crash dumps, service payloads, release logs, or credentials. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/REQUIREMENTS.md; VERIFIED: .planning/STATE.md] |
| V15 Secure Coding and Architecture | yes | Use functional core / imperative shell, parse-at-boundary patterns, and unit-tested pure policy logic. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: standards/core/architecture.md; VERIFIED: standards/core/testing.md] |
| V16 Security Logging and Error Handling | yes | Write rejected/quarantined blocker rows and reports with non-secret reasons and explicit proof ineligibility. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: build/ci-evidence/phase31/rejected-submissions.json; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| V17 WebRTC | no | Phase 32 has no WebRTC surface. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |

### Known Threat Patterns for Phase 32

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Non-final proof is promoted because it is visible in triage | Spoofing / Elevation of Privilege | Separate visibility from `proof_eligibility`, and mark rejected/quarantined/non-final rows ineligible. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md; VERIFIED: build/ci-evidence/phase31/rejected-submissions.json] |
| Secret-bearing reason or artifact data enters the report | Information Disclosure | Generate reports from canonical sanitized rows and run a security-only scan over generated outputs. [VERIFIED: tools/bazel/phase28_final_readiness_packet.py; VERIFIED: tools/bazel/phase31_final_evidence_intake.py] |
| Unknown source status maps to benign repair work | Tampering / Elevation of Privilege | Unknown/unmapped inputs fail closed as critical unresolved decision blockers. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Derived exception/residual-risk queue drifts from canonical register | Repudiation / Tampering | Generate derived queues from canonical register rows and include stable `row_id` backreferences. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Phase 32 implies approvals that belong to later phases | Elevation of Privilege | Keep Phase 32 outputs to blocker classification and handoff; defer exception, retained-code, readiness, demotion, and cutover decisions. [VERIFIED: .planning/ROADMAP.md; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md] |
| Unsafe refs or symlink/path escapes are copied into outputs | Tampering / Information Disclosure | Preserve allowed-root checks from existing verifier patterns and reject output-root symlink escapes. [VERIFIED: tools/bazel/phase31_final_evidence_intake.py; VERIFIED: tools/bazel/phase28_final_readiness_packet_test.py] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md` - locked decisions, scope, canonical refs, artifact expectations, and test expectations. [VERIFIED: file read]
- `.planning/REQUIREMENTS.md` - TRIAGE-01 through TRIAGE-03 and v1.3 out-of-scope boundaries. [VERIFIED: file read]
- `.planning/ROADMAP.md` - Phase 32 goal, success criteria, dependency on Phase 31, and downstream Phase 33-35 responsibilities. [VERIFIED: file read]
- `.planning/STATE.md` - current focus, active blockers, and evidence-sanitization concerns. [VERIFIED: file read]
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/testing.md`, and `standards/core/verification.md` - local and managed workflow constraints. [VERIFIED: file read]
- `tools/bazel/manifests/phase31_final_evidence_intake_contract.json`, `tools/bazel/phase31_final_evidence_intake.py`, and `tools/bazel/phase31_final_evidence_intake_test.py` - finality boundary, receipt fields, rejected/quarantined behavior, and existing wiring/test patterns. [VERIFIED: file read and grep]
- `build/ci-evidence/phase31/final-intake-manifest.json` and `build/ci-evidence/phase31/rejected-submissions.json` - actual Phase 31 quick output shape. [VERIFIED: file read]
- `tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json`, `tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json`, `tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json`, and `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` - source row status vocabulary, required fields, output names, and generated artifacts. [VERIFIED: file read]
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - upstream status vocabulary, hard-blocker reasons, exception-coverable statuses, and decision vocabulary. [VERIFIED: file read]
- `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`, `tools/bazel/phase27_retained_code_acceptance_decisions.py`, and generated Phase 27 artifacts - retained-code, residual-risk, exception, decision-row, and Phase 28 handoff shapes. [VERIFIED: file read]
- `tools/bazel/manifests/phase28_final_readiness_packet_contract.json`, `tools/bazel/phase28_final_readiness_packet.py`, and generated Phase 28 artifacts - readiness blocker vocabulary, hard-blocker precedence, exception/residual-risk summary, and demotion separation. [VERIFIED: file read]
- `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - existing verifier wiring patterns. [VERIFIED: file read and grep]
- Local environment probes - Python, Bazel, `just`, Bash, Git, Cargo, jq, and pre-commit availability. [VERIFIED: environment audit commands]

### Secondary (MEDIUM confidence)

- OWASP ASVS project page - ASVS purpose and latest stable version note. [CITED: https://owasp.org/www-project-application-security-verification-standard/]
- OWASP Cheat Sheet ASVS index - ASVS 5.0.x category names. [CITED: https://cheatsheetseries.owasp.org/IndexASVS.html]

### Tertiary (LOW confidence)

- None used. [VERIFIED: source log above]

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - all recommended tools and patterns already exist in Phase 23-31 or were locally probed. [VERIFIED: tools/bazel/BUILD.bazel; VERIFIED: justfile; VERIFIED: environment audit commands]
- Architecture: HIGH - locked decisions constrain Phase 32 to a thin adapter plus classifier over Phase 31 and existing v1.2/v1.3 artifacts. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
- Pitfalls: HIGH - placeholder, finality, secret, source-ref, redaction, lifecycle, unsafe-ref, no-demotion, and derived-view drift risks are all present in existing tests/contracts. [VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py; VERIFIED: tools/bazel/phase28_final_readiness_packet_test.py; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
- Validation architecture: HIGH - `.planning/config.json` enables Nyquist, and the existing phase verifier test pattern is consistent across Phase 23-31. [VERIFIED: .planning/config.json; VERIFIED: tools/bazel/phase31_final_evidence_intake_test.py]
- Security mapping: MEDIUM - ASVS categories were verified from current OWASP pages, and local controls map to CLI/generated-artifact behavior rather than a formal web-app security requirement set. [CITED: https://owasp.org/www-project-application-security-verification-standard/; CITED: https://cheatsheetseries.owasp.org/IndexASVS.html; VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]

**Research date:** 2026-07-03  
**Valid until:** Re-run this research if Phase 31 final-intake artifacts, Phase 27/28 handoff schemas, or Phase 33-35 requirements change. [VERIFIED: .planning/phases/32-blocker-register-and-evidence-triage/32-CONTEXT.md]
