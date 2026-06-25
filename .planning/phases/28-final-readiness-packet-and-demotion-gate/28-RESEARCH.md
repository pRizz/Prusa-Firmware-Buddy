# Phase 28: Final Readiness Packet and Demotion Gate - Research

**Researched:** 2026-06-25 [VERIFIED: system date and `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]
**Domain:** Bazel-backed Python evidence verifier, final readiness aggregation, and explicit reference-demotion authorization [VERIFIED: `.planning/ROADMAP.md`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]
**Confidence:** HIGH [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase27_retained_code_acceptance_decisions.py`; local verifier tests]

<user_constraints>
## User Constraints (from CONTEXT.md)

> The following subsections are copied verbatim from `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]

### Locked Decisions

## Implementation Decisions

### Packet Composition and Traceability
- **D-01:** Build the final packet as a criteria-centric, link-first readiness record. Use one row per Phase 18 final criterion and link each row to READ-01, READ-02, READ-03, Phase 26 upstream rows, Phase 27 decision outputs, exception records, residual-risk entries, hard blockers, and retained artifact refs.
- **D-02:** Treat the machine-readable packet as the source of truth. A redacted human-readable readiness report may be generated as a derived view, but it must not become the only approval surface or drift from the machine rows.
- **D-03:** Keep raw evidence, signing material, credentials, production payloads, crash dumps, firmware binaries, and secret-bearing details out of the packet. Retain sanitized metadata and artifact references only.

### Readiness and Exception Semantics
- **D-04:** Use a two-verdict fail-closed model: final readiness status starts blocked and can resolve only when required gates pass or are covered by explicit approved exceptions; reference demotion remains a separate authorization verdict.
- **D-05:** Hard blockers outrank exceptions. Redaction failure, overclaim failure, lifecycle mismatch, source-ref failure, unsafe refs, or secret-tainted evidence must stay blocked and cannot be converted into normal accepted residual risk.
- **D-06:** Valid exceptions may cover only contract-allowed evidence statuses and must include scope, owner or approver, approver role, rationale, affected printer or release surface, evidence refs, residual risk, mitigation or follow-up, and expiry or review trigger.

### Reference Demotion Authorization
- **D-07:** Preserve reference demotion as a separate explicit maintainer decision. Green or exception-covered readiness evidence is a prerequisite, not automatic demotion approval.
- **D-08:** Default demotion authorization remains `blocked`. Phase 28 may expose an approval input or authorization record, but the verifier must reject any implied approval from evidence status alone.
- **D-09:** Keep the Phase 18 `final-reference-demotion-allowed` criterion and Phase 27 `phase28-handoff-manifest.json` aligned: the handoff supplies the blocked starting state, and Phase 28 owns the final explicit decision gate.

### Retained Outputs and Verification
- **D-10:** Implement Phase 28 as an aggregate final-readiness gate over retained Phase 26 and Phase 27 outputs, not as another producer that redefines simulator, hardware, live-service, release, upstream, retained-code, or residual-risk evidence.
- **D-11:** Retained Phase 28 outputs should live under `build/ci-evidence/phase28` and include a run manifest, final readiness packet, normalized criteria table, blocker summary, exception and residual-risk summary, demotion decision input or authorization record, redacted readiness report, artifact-reference summary, and contract/source snapshots.
- **D-12:** Add Bazel root aliases, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `just phase28-verify` wiring consistent with Phases 23-27. Verification should cover contract/schema drift, input presence and provenance, blocked-by-default behavior, exception precedence, hard-blocker rejection, no-implied-demotion behavior, secret/overclaim guards, retained output writing, and wiring.

### the agent's Discretion
- Choose exact filenames and JSON field names for the Phase 28 contract, readiness packet, decision input, normalized criteria table, summaries, and report, provided they are explicit, tested, stable, and do not fork Phase 18 or Phase 27 policy.
- Decide whether to implement Phase 28 as a thin wrapper around existing Phase 18/26/27 helper code or as a standalone verifier with shared constants. Prefer the smallest approach that avoids schema drift and makes readiness versus demotion status unambiguous.
- Choose the smallest useful number of plans. Prefer a single cohesive plan unless research finds a real dependency split.

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| READ-01 | Maintainer can generate a final cutover readiness packet that links all external evidence, acceptance decisions, exceptions, and residual risks. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use a Phase 28 criteria table with exactly the nine Phase 18 final criteria, linked to Phase 26 upstream rows and Phase 27 retained outputs. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json`; `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`] |
| READ-02 | Final readiness remains blocked by default unless all required evidence passes or has explicit approved exceptions. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use Phase 18 allowed status and exception-coverable status policies, Phase 26 redaction/source/lifecycle blockers, and Phase 27 hard-block-before-exception behavior as the aggregation rules. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase27_retained_code_acceptance_decisions.py`] |
| READ-03 | Reference demotion remains a separate explicit maintainer approval and is not automatic. [VERIFIED: `.planning/REQUIREMENTS.md`] | Keep `final_readiness_status` and `reference_demotion_authorization` as separate top-level verdicts; require an explicit Phase 28 demotion decision input for authorization and reject approval inferred from green evidence. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`] |
</phase_requirements>

## Summary

Phase 28 should be planned as a new standard-library Python verifier plus JSON contract, not as firmware code. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase27_retained_code_acceptance_decisions.py`] The verifier should consume retained Phase 26 and Phase 27 outputs, produce a criteria-centric machine-readable readiness packet, and write a derived redacted report under `build/ci-evidence/phase28`. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `build/ci-evidence/phase26/upstream-result-row-table.json`; `build/ci-evidence/phase27/phase28-handoff-manifest.json`]

The central design constraint is the two-verdict model. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`] `final_readiness_status` should aggregate required evidence, decisions, exceptions, hard blockers, and residual risks; `reference_demotion_authorization` should remain blocked unless an explicit Phase 28 demotion input authorizes it and readiness is not blocked. [VERIFIED: `.planning/REQUIREMENTS.md`; `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`; `tools/bazel/phase18_cutover_review.py`]

The planner should prefer one cohesive plan with three implementation tasks: contract/tests, verifier/output generation, and workflow wiring. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md`; `.planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-01-SUMMARY.md`] This matches the Phase 26 and Phase 27 execution pattern of adding a contract, Python verifier/test suite, then Bazel/root/just wiring. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence_test.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`; `BUILD.bazel`; `tools/bazel/BUILD.bazel`; `justfile`]

**Primary recommendation:** Implement `tools/bazel/phase28_final_readiness_packet.py`, `tools/bazel/phase28_final_readiness_packet_test.py`, and `tools/bazel/manifests/phase28_final_readiness_packet_contract.json`, then wire `//tools/bazel:phase28_verify`, `//tools/bazel:phase28_verify_tests`, and `just phase28-verify`. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 26/27 wiring in `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile`]

## Project Constraints (from AGENTS.md)

- Use `AGENTS.md` as the repo-local instruction entrypoint, then `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant `standards/` pages before planning or implementation. [VERIFIED: `AGENTS.md`; `AGENTS.bright-builds.md`]
- Keep Phase 28 in the GSD workflow and do not make direct repo edits outside GSD unless explicitly bypassed. [VERIFIED: `AGENTS.md`]
- Use Bazel as the authoritative build workflow and keep a discoverable `justfile` wrapper for common commands. [VERIFIED: `AGENTS.md`; `.planning/PROJECT.md`]
- Follow Bright Builds functional-core/imperative-shell guidance: pure decision logic should be separated from file I/O, CLI parsing, and workflow dispatch. [VERIFIED: `standards/core/architecture.md`; `AGENTS.bright-builds.md`]
- Prefer early returns, shallow control flow, and explicit `maybe_` naming for absence-like internals where practical. [VERIFIED: `standards/core/code-shape.md`; `standards/languages/rust.md`]
- Unit-test pure/business logic and structure non-trivial unit tests with Arrange, Act, Assert comments. [VERIFIED: `standards/core/testing.md`; Phase 26/27 tests]
- Do not hide substantial foreign code in strings; checked-in scripts should remain rerunnable and diagnosable. [VERIFIED: `standards/core/code-shape.md`]
- For commits in this Rust repo, run `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` before committing. [VERIFIED: user-provided `AGENTS.md` instructions]
- No project-local skill directories were present under `.claude/skills/` or `.agents/skills/`. [VERIFIED: `find .claude/skills .agents/skills -mindepth 1 -maxdepth 1 -type d`]

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Python standard library | Python 3.14.4 locally | Implement contract loading, JSON normalization, security scans, output writing, and `unittest` tests. | Existing Phase 18, 23, 24, 25, 26, and 27 verifiers are Python standard-library scripts under `tools/bazel/`. [VERIFIED: `python3 --version`; `rg --files tools/bazel -g '*_test.py'`; existing verifier scripts] |
| Bazel `shell_binary` | Bazel 9.1.1 locally | Expose `//tools/bazel:phase28_verify` and `//tools/bazel:phase28_verify_tests`. | Phase 23-27 verification labels use `shell_binary` with `tools/bazel/rust_workflow.sh`. [VERIFIED: `bazel --version`; `tools/bazel/BUILD.bazel`] |
| `just` | just 1.48.0 locally | Expose `just phase28-verify` as the developer-facing workflow. | Phase 23-27 have `just phaseXX-verify` recipes that run tests before verifier targets. [VERIFIED: `just --version`; `justfile`] |
| JSON manifests | n/a | Define Phase 28 policy, generated artifacts, source contracts, and input schemas. | Phase 18, 26, and 27 use tracked JSON contracts as canonical policy and generated outputs under `build/ci-evidence`. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json`; `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`] |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| Cargo | 1.91.1 locally | Required Rust-project pre-commit verification sequence. | Run before committing the Phase 28 research or implementation commit. [VERIFIED: `cargo --version`; user-provided `AGENTS.md`] |
| jq | 1.7.1 locally | Inspect generated JSON during development and tests. | Optional for developer inspection; the verifier should not require jq. [VERIFIED: `jq --version`; existing Python verifier style] |
| Git | 2.53.0 locally | Commit the research artifact when `commit_docs` is enabled. | Use GSD commit helper or non-interactive git commands; commit only Phase 28 research unless planner changes later files. [VERIFIED: `git --version`; `node ... gsd-tools.cjs init phase-op 28`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Python standard-library verifier | Reuse Phase 18 verifier as an imported module | Phase 18 is 2095 lines and already owns its own demotion semantics; direct import risks coupling Phase 28 to Phase 18 output names rather than a small aggregate wrapper. [VERIFIED: `wc -l tools/bazel/phase18_cutover_review.py`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`] |
| JSON contract + unittest | Ad hoc Markdown report | Markdown-only output violates the Phase 28 decision that the machine-readable packet is the source of truth. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`] |
| Explicit demotion input | Boolean inferred from all-green rows | Implied approval violates READ-03 and Phase 27 tests already reject demotion overclaims. [VERIFIED: `.planning/REQUIREMENTS.md`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`] |

**Installation:**

```bash
# No new packages should be installed for Phase 28.
```

No npm package version verification is needed because Phase 28 should use only local Python, Bazel, just, and JSON tooling. [VERIFIED: existing Phase 26/27 implementation pattern; `node ... gsd-tools.cjs init phase-op 28`]

## Architecture Patterns

### Recommended Project Structure

```text
tools/bazel/
├── manifests/
│   └── phase28_final_readiness_packet_contract.json
├── phase28_final_readiness_packet.py
└── phase28_final_readiness_packet_test.py

build/ci-evidence/phase28/
├── final-readiness-run-manifest.json
├── final-readiness-packet.json
├── normalized-readiness-criteria-table.json
├── blocker-summary.json
├── exception-residual-risk-summary.json
├── reference-demotion-authorization-record.json
├── demotion-decision-input-template.json
├── redacted-readiness-report.md
├── artifact-reference-summary.json
└── contract-snapshots/
    ├── phase18_cutover_review_contract.json
    ├── phase26_release_signing_upstream_evidence_contract.json
    ├── phase27_retained_code_acceptance_decisions_contract.json
    ├── phase26-upstream-result-row-table.json
    └── phase27-phase28-handoff-manifest.json
```

Use these filenames unless implementation discovers a collision; they satisfy D-11 and keep Phase 28 names distinct from Phase 18's `normalized-final-demotion-results.json`. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

### Pattern 1: Contract-First Aggregate Verifier

**What:** Add a Phase 28 contract that names source contracts, generated artifacts, required input paths, canonical Phase 18 criteria, hard-blocker reasons, exception fields, and demotion authorization policy. [VERIFIED: Phase 26/27 contracts]

**When to use:** Use for all Phase 28 readiness packet behavior. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]

**Example:**

```json
{
  "id": "phase28_final_readiness_packet_contract",
  "phase": "28-final-readiness-packet-and-demotion-gate",
  "output_root": "build/ci-evidence/phase28",
  "source_contracts": [
    "tools/bazel/manifests/phase18_cutover_review_contract.json",
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json",
    "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
  ],
  "readiness_policy": {
    "canonical_phase18_criteria": "phase18.upstream_result_requirements[].criterion_id",
    "hard_blocker_reasons": [
      "redaction-failed",
      "overclaim-failed",
      "lifecycle-mismatch",
      "source-ref-failed",
      "unsafe-ref"
    ],
    "default_final_readiness_status": "blocked"
  },
  "demotion_authorization_policy": {
    "default": "blocked",
    "approval_requires_explicit_phase28_input": true,
    "evidence_status_never_implies_approval": true
  }
}
```

This example is a recommended Phase 28 contract shape derived from the existing contract pattern, not an existing file. [VERIFIED: `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json`; `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]

### Pattern 2: Two Verdicts, One Criteria Table

**What:** Emit one row per Phase 18 final criterion, but derive two top-level verdicts: `final_readiness_status` and `reference_demotion_authorization`. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `tools/bazel/manifests/phase18_cutover_review_contract.json`]

**When to use:** Use when processing `final-reference-demotion-allowed`: include it in the table, but use it for the demotion verdict instead of letting it make readiness and demotion circular. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `.planning/REQUIREMENTS.md`]

**Example:**

```python
packet = {
    "final_readiness_status": readiness_status,
    "reference_demotion_authorization": demotion_status,
    "criteria": normalized_rows,
}
```

This shape makes READ-02 and READ-03 independently testable. [VERIFIED: `.planning/REQUIREMENTS.md`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

### Pattern 3: Hard Blockers Before Exceptions

**What:** Evaluate redaction, overclaim, lifecycle, source-ref, unsafe-ref, and secret-taint blockers before accepting any exception metadata. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase27_retained_code_acceptance_decisions.py`]

**When to use:** Use for every Phase 26 upstream row and Phase 27 retained/final decision row before calculating readiness. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence_test.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

**Example:**

```python
if hard_failure_reasons:
    status = status_for_hard_failure(hard_failure_reasons)
    exception_state = "blocked-by-hard-failure"
elif exception_is_valid:
    status = "exception-approved"
```

The precedence mirrors Phase 27's hard-block-first normalization. [VERIFIED: `tools/bazel/phase27_retained_code_acceptance_decisions.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

### Pattern 4: Workflow Dispatch Order

**What:** `phase28_verify` should run Phase 28 wiring validation first, then generate Phase 26 quick outputs, generate Phase 27 quick outputs from the Phase 26 table, and finally generate Phase 28 quick outputs. [VERIFIED: Phase 27 `rust_workflow.sh` dispatch order; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]

**When to use:** Use for `tools/bazel/rust_workflow.sh` and enforce order in `phase28_final_readiness_packet_test.py`. [VERIFIED: `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

**Example:**

```bash
python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only
python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26
python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27
python3 tools/bazel/phase28_final_readiness_packet.py --quick --output-dir build/ci-evidence/phase28
```

This extends the Phase 27 precondition order by one aggregate step. [VERIFIED: `tools/bazel/rust_workflow.sh`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

### Anti-Patterns to Avoid

- **Markdown as authority:** Do not make `redacted-readiness-report.md` the approval surface; derive it from `final-readiness-packet.json`. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]
- **Criteria copied into Python constants without drift checks:** Load Phase 18 criteria and compare exact IDs in contract/tests. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]
- **Demotion boolean reuse:** Do not revive Phase 18 `demotion_allowed` as the Phase 28 authorization field; use `reference_demotion_authorization` or `demotion_authorization` and reject implied approval. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `tools/bazel/phase27_retained_code_acceptance_decisions.py`]
- **Raw evidence retention:** Do not store secrets, firmware binaries, crash dumps, payloads, or raw logs in the packet. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 26/27 forbidden field guards]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Canonical criterion list | A new Phase 28 list of cutover gates | Load and verify Phase 18 `upstream_result_requirements` / `final_demotion_criteria` | Phase 26 and 27 already guard exact Phase 18 criteria identity. [VERIFIED: `tools/bazel/manifests/phase18_cutover_review_contract.json`; `tools/bazel/phase26_release_signing_upstream_evidence_test.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`] |
| Upstream evidence status normalization | Re-parse raw simulator, hardware, live-service, or release evidence | Consume Phase 26 `upstream-result-row-table.json` | Phase 28 is an aggregate gate over retained Phase 26/27 outputs, not another evidence producer. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`] |
| Retained-code and residual-risk decisions | New retained-code decision semantics | Consume Phase 27 `normalized-retained-code-decisions.json`, `exception-decision-register.json`, `residual-risk-register.json`, and `final-readiness-decision-summary.json` | Phase 27 already validates retained decisions, exception metadata, residual risk, role policy, and hard blockers. [VERIFIED: `tools/bazel/phase27_retained_code_acceptance_decisions.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`] |
| Demotion authorization | Automatic approval based on green evidence | Explicit Phase 28 demotion decision input plus blocked default | READ-03 and D-07 prohibit automatic demotion. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`] |
| Secret/overclaim scanning | A Phase 28-only regex set with weaker coverage | Start from Phase 26/27 forbidden field and text-pattern policies and add Phase 28 report strings | Prior phases reject secret markers, forbidden fields, and demotion overclaim markers. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase27_retained_code_acceptance_decisions.py`] |
| Build integration | Manual shell instructions only | Bazel `shell_binary`, root aliases, `rust_workflow.sh`, and `just phase28-verify` | Phase 23-27 all expose verifier and test targets through this wiring pattern. [VERIFIED: `BUILD.bazel`; `tools/bazel/BUILD.bazel`; `tools/bazel/rust_workflow.sh`; `justfile`] |

**Key insight:** Phase 28 should aggregate and reconcile existing authority surfaces; custom proof engines or raw evidence processors would increase drift risk and contradict D-10. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 26/27 contracts]

## Common Pitfalls

### Pitfall 1: Readiness And Demotion Collapse Into One Boolean

**What goes wrong:** A green criteria table sets demotion to approved without a Phase 28 maintainer authorization record. [VERIFIED: Phase 27 no-demotion tests; `.planning/REQUIREMENTS.md`]
**Why it happens:** Phase 18 uses `demotion_allowed`, while Phase 28 requires a two-verdict model. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]
**How to avoid:** Emit separate top-level `final_readiness_status` and `reference_demotion_authorization` fields and write tests where all non-demotion criteria pass but demotion stays blocked without explicit input. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]
**Warning signs:** Output contains `demotion_allowed: true`, `demotion_authorization: "allowed"`, or report language like "final readiness approved" in quick mode. [VERIFIED: `tools/bazel/phase27_retained_code_acceptance_decisions.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

### Pitfall 2: Hard Blockers Treated As Residual Risk

**What goes wrong:** Redaction, lifecycle, source-ref, unsafe-ref, overclaim, or secret-taint failures become exception-approved rows. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 26/27 tests]
**Why it happens:** Exception handling is easier to implement as a later override than as a policy-constrained branch. [VERIFIED: Phase 27 hard-block-before-exception test]
**How to avoid:** Normalize hard blockers before exception coverage and keep a `hard_blocker_summary.json` or `blocker-summary.json` with blocking reasons. [VERIFIED: `tools/bazel/phase27_retained_code_acceptance_decisions.py`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]
**Warning signs:** A row has `exception_state: approved-exception` and a hard-blocker reason in the same normalized object. [VERIFIED: `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

### Pitfall 3: Contract Drift From Phase 18 And Phase 27

**What goes wrong:** Phase 28 uses a criteria list or exception fields that no longer match Phase 18, or accepts a handoff that no longer matches Phase 27. [VERIFIED: Phase 26/27 contract drift tests]
**Why it happens:** Copying JSON fields into constants looks simpler than checking source contracts on every run. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase27_retained_code_acceptance_decisions.py`]
**How to avoid:** Load Phase 18 and Phase 27 contracts, assert exact expected IDs and required fields, and snapshot source contracts into `build/ci-evidence/phase28/contract-snapshots`. [VERIFIED: Phase 26/27 generated artifact lists]
**Warning signs:** Tests only check that output exists, not that row IDs and required fields exactly match source contracts. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence_test.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

### Pitfall 4: Report Drift From Packet

**What goes wrong:** Human-readable readiness Markdown says something that differs from the machine-readable packet. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]
**Why it happens:** The Phase 28 context explicitly warns that a report can drift if it becomes the only approval surface instead of a derived view. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]
**How to avoid:** Build report rows directly from `final-readiness-packet.json` and test report content against packet status counts and demotion authorization. [VERIFIED: Phase 18 report generation pattern in `tools/bazel/phase18_cutover_review.py`]
**Warning signs:** Report generation accepts raw inputs instead of normalized packet rows. [VERIFIED: Phase 18 report derives from normalized rows]

### Pitfall 5: Quick Mode Overclaims Real Evidence

**What goes wrong:** Local quick fixtures appear to prove real release signing, hardware, live-service, or maintainer approval. [VERIFIED: Phase 26 quick-mode residual risk; `.planning/PROJECT.md`]
**Why it happens:** Quick mode is convenient for local verification but cannot supply non-local evidence. [VERIFIED: `.planning/phases/26-release-signing-and-upstream-result-evidence/26-01-SUMMARY.md`; `.planning/PROJECT.md`]
**How to avoid:** In quick mode, generate blocked/pending placeholders and explicit `real_*_supplied: false` or equivalent provenance. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence_test.py`; Phase 27 quick outputs]
**Warning signs:** Quick output reports `passed` for release/signing, retained-code acceptance, final demotion, or maintainer approval without input files. [VERIFIED: Phase 26/27 tests]

## Code Examples

### Load Canonical Criteria From Phase 18

```python
def canonical_criteria(phase18_contract: dict[str, object]) -> list[str]:
    requirements = phase18_contract["upstream_result_requirements"]
    return [str(row["criterion_id"]) for row in requirements]
```

Use this pattern and assert it equals the Phase 28 contract's declared criteria. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`]

### Derive Packet Rows From Source Outputs

```python
row = {
    "criterion_id": criterion_id,
    "requirement_ids": phase26_row["requirement_ids"],
    "upstream_status": phase26_row["status"],
    "final_decision_status": phase27_row["status"],
    "exception_state": phase27_row["exception_state"],
    "hard_failure_reasons": hard_failure_reasons,
    "readiness_effect": readiness_effect,
}
```

Keep this as a pure transformation function and unit-test it without filesystem access. [VERIFIED: `standards/core/architecture.md`; Phase 27 normalization functions]

### Explicit Demotion Input Shape

```json
{
  "phase": "28-final-readiness-packet-and-demotion-gate",
  "phase_lifecycle_id": "28-2026-06-25T03-31-49",
  "demotion_authorization": "blocked",
  "approver": "",
  "approver_role": "",
  "decision_timestamp": "",
  "rationale": "Reference demotion remains blocked until explicit maintainer approval.",
  "evidence_refs": []
}
```

Quick mode should write a blocked template like this; approval mode should require non-empty approver, role, ISO UTC timestamp, rationale, evidence refs, and a non-blocked readiness verdict. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 27 decision input validation]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Prose readiness report | Machine-readable gate rows plus derived redacted report | Phase 18 and reinforced by Phase 28 decisions | Planner should make JSON packet the authority. [VERIFIED: `tools/bazel/phase18_cutover_review.py`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`] |
| Local quick outputs as pass evidence | Quick outputs are safe placeholders unless real non-local inputs are supplied | Phase 23-27 v1.2 execution phases | Planner should test blocked-by-default quick mode. [VERIFIED: Phase 23-27 verifier tests and summaries] |
| Single demotion boolean | Separate readiness status and demotion authorization | Phase 27 handoff and Phase 28 context | Planner should reject implied demotion approval. [VERIFIED: `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json`; `.planning/REQUIREMENTS.md`] |
| Evidence rows can be exceptioned generically | Hard blockers outrank exceptions | Phase 26/27 policy and Phase 28 D-05 | Planner should place hard-block tests before exception success tests. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence_test.py`; `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`] |

**Deprecated/outdated:**

- Treating `build/ci-evidence/phase18/normalized-final-demotion-results.json` as the Phase 28 packet is outdated for this phase; Phase 28 needs `build/ci-evidence/phase28` retained outputs and a separate demotion authorization surface. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 18 generated artifact list]
- Using Phase 26 upstream rows alone as acceptance is outdated for READ-01/READ-02; Phase 28 must also consume Phase 27 decisions, exceptions, residual risks, and handoff. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 27 generated artifacts]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|

All claims in this research are tagged as verified or cited from local files, command outputs, or official OWASP documentation. [VERIFIED: this research source log]

## Open Questions

1. **Should Phase 28 accept an explicit approval input in the first implementation or only emit the blocked authorization template?**
   - What we know: D-08 says Phase 28 may expose approval input or authorization record, while READ-03 requires explicit approval and default blocked behavior. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; `.planning/REQUIREMENTS.md`]
   - What's unclear: The context does not require that a real approval path be exercised during local quick verification. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`]
   - Recommendation: Implement both `--demotion-decision` validation and a blocked quick template, but keep quick mode blocked unless the explicit input is supplied and readiness is not blocked. [VERIFIED: D-08 discretion and Phase 27 maintainer-input pattern]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | Phase 28 verifier and tests | yes | 3.14.4 | Blocking if missing because Phase 18/26/27 verifiers are Python. [VERIFIED: `python3 --version`; existing scripts] |
| Bazel | `//tools/bazel:phase28_verify*` targets | yes | 9.1.1 | Direct Python commands can verify locally, but Bazel wiring still must exist. [VERIFIED: `bazel --version`; Phase 26/27 wiring] |
| just | Developer workflow wrapper | yes | 1.48.0 | Direct Bazel commands are fallback, but project requires `justfile` recipes. [VERIFIED: `just --version`; `AGENTS.md`] |
| Cargo | Pre-commit checks in Rust repo | yes | 1.91.1 | No fallback before committing in this repo. [VERIFIED: `cargo --version`; user-provided `AGENTS.md`] |
| jq | Research and developer inspection | yes | 1.7.1 | Python `json` module in verifier. [VERIFIED: `jq --version`; existing verifier style] |

**Missing dependencies with no fallback:** None found. [VERIFIED: local command probes]

**Missing dependencies with fallback:** None found. [VERIFIED: local command probes]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Python `unittest` invoked as a script. [VERIFIED: `tools/bazel/*_test.py`; Phase 26/27 validation docs] |
| Config file | none for phase verifier tests. [VERIFIED: `.planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-VALIDATION.md`] |
| Quick run command | `python3 tools/bazel/phase28_final_readiness_packet_test.py` [VERIFIED: recommended from Phase 26/27 naming pattern] |
| Full suite command | `just phase28-verify` [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 23-27 just recipes] |

### Phase Requirements To Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| READ-01 | Packet includes one row per Phase 18 criterion and links Phase 26 upstream rows, Phase 27 decisions, exceptions, residual risks, blockers, and artifact refs. [VERIFIED: `.planning/REQUIREMENTS.md`; `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`] | unit + quick smoke | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - Wave 0 |
| READ-01 | Generated outputs include run manifest, packet, normalized criteria table, blocker summary, exception/residual-risk summary, demotion record/template, redacted report, artifact summary, and contract snapshots. [VERIFIED: D-11] | unit + filesystem smoke | `python3 tools/bazel/phase28_final_readiness_packet.py --quick --output-dir build/ci-evidence/phase28` | No - Wave 0 |
| READ-02 | Missing Phase 26 or Phase 27 inputs keep final readiness blocked and report actionable missing-input reasons. [VERIFIED: Phase 27 missing Phase 26 row-table test; D-04] | unit | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - Wave 0 |
| READ-02 | Passed or exception-approved readiness requires no hard blockers and valid exception metadata for coverable statuses only. [VERIFIED: Phase 18/26/27 policies] | unit/security | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - Wave 0 |
| READ-02 | Hard blockers outrank exceptions and produce blocked readiness. [VERIFIED: D-05; Phase 26/27 tests] | unit/security | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - Wave 0 |
| READ-03 | Green or exception-covered readiness does not authorize demotion without explicit Phase 28 input. [VERIFIED: `.planning/REQUIREMENTS.md`; D-07/D-08] | unit/security | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - Wave 0 |
| READ-03 | Explicit demotion approval is rejected when final readiness is blocked, when handoff lifecycle/source data drift, or when approval metadata is incomplete. [VERIFIED: D-07/D-09; Phase 27 handoff policy] | unit/security | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - Wave 0 |
| READ-01 / READ-02 / READ-03 | Bazel, root aliases, workflow dispatch, and `just phase28-verify` run tests before verifier and regenerate Phase 26/27 preconditions in order. [VERIFIED: D-12; Phase 27 wiring test pattern] | wiring | `python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only` | No - Wave 0 |

### Sampling Rate

- **Per task commit:** Run `python3 tools/bazel/phase28_final_readiness_packet_test.py` plus the changed-path verifier mode such as `--contract-only`, `--security-only`, or `--wiring-only`. [VERIFIED: Phase 26/27 validation docs]
- **Per wave merge:** Run Phase 26 quick, Phase 27 quick, Phase 28 quick, and `just phase28-verify`. [VERIFIED: Phase 27 workflow dependency pattern; Phase 28 D-12]
- **Phase gate:** Run `just phase28-verify`, `git diff --check`, and the repo-required Cargo sequence before commit or `/gsd-verify-work`. [VERIFIED: `AGENTS.md`; `standards/core/verification.md`]

### Wave 0 Gaps

- [ ] `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` - Phase 28 contract, source contracts, generated artifacts, readiness policy, demotion authorization policy, hard blockers, and input schemas. [VERIFIED: no current phase28 file under `tools/bazel/`]
- [ ] `tools/bazel/phase28_final_readiness_packet.py` - verifier with `--contract-only`, `--security-only`, `--wiring-only`, `--quick`, optional `--demotion-decision`, Phase 26/27 input paths, and output-root containment. [VERIFIED: Phase 26/27 CLI patterns]
- [ ] `tools/bazel/phase28_final_readiness_packet_test.py` - unit, security, output, and wiring tests for READ-01, READ-02, and READ-03. [VERIFIED: no current phase28 test under `tools/bazel/`]
- [ ] Root `BUILD.bazel` docs filegroup and aliases for `phase28_verify` and `phase28_verify_tests`. [VERIFIED: Phase 23-27 root wiring]
- [ ] `tools/bazel/BUILD.bazel` `phase28_source_ref_manifests`, `phase28_verify`, and `phase28_verify_tests` targets. [VERIFIED: Phase 26/27 target pattern]
- [ ] `tools/bazel/rust_workflow.sh` `phase28_verify` and `phase28_verify_tests` cases. [VERIFIED: current script has Phase 27 as latest v1.2 case]
- [ ] `justfile` `phase28-verify` recipe with tests before verifier. [VERIFIED: `justfile` currently has Phase 27 as latest v1.2 recipe]

## Security Domain

Security enforcement is enabled because `.planning/config.json` does not set `security_enforcement` to `false`. [VERIFIED: `.planning/config.json`]

OWASP ASVS is a verification standard for application security controls, and official OWASP/GitHub documentation lists 5.0.0 as the latest stable version dated May 2025. [CITED: https://owasp.org/www-project-application-security-verification-standard/; https://github.com/OWASP/ASVS] The project template uses V2-V6 category labels; this research maps those labels to the Phase 28 verifier surface while using versioned ASVS references where new requirement IDs are later needed. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no direct user authentication | Phase 28 records approver identity and role as evidence metadata, but does not authenticate users. [VERIFIED: Phase 27 decision schema; Phase 28 context] |
| V3 Session Management | no | No sessions are introduced by a command-line verifier. [VERIFIED: proposed Python CLI architecture; Phase 26/27 verifier pattern] |
| V4 Access Control | yes | Enforce maintainer/release/safety/network role fields and reject demotion approval without explicit authorized input. [VERIFIED: Phase 27 sensitive role policy; READ-03] |
| V5 Input Validation | yes | Parse JSON input at boundaries, enforce required fields, allowed statuses, exact criteria, lifecycle IDs, source refs, and output-root containment. [VERIFIED: Phase 18/26/27 verifier patterns; `standards/core/architecture.md`] |
| V6 Cryptography | no new cryptography | Retain signing identity refs and artifact refs only; do not handle private keys or raw signing payloads. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 26 secret policy] |

### Known Threat Patterns for Phase 28

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Forged demotion approval through green evidence rows | Elevation of Privilege | Separate `reference_demotion_authorization` from `final_readiness_status` and require explicit Phase 28 demotion input. [VERIFIED: READ-03; D-07/D-08] |
| Secret-bearing evidence embedded in packet or report | Information Disclosure | Reject forbidden fields/text and write sanitized refs only. [VERIFIED: D-03; Phase 26/27 security scans] |
| Lifecycle or source-ref drift | Tampering | Validate Phase 26 row `source_lifecycle_id`, Phase 27 handoff lifecycle, approved roots, and contract snapshots. [VERIFIED: Phase 18/26/27 tests] |
| Exception used to bypass a hard blocker | Tampering / Elevation of Privilege | Evaluate hard-block reasons before exception coverage and keep hard blockers blocked. [VERIFIED: D-05; Phase 27 hard-block test] |
| Report overclaim | Repudiation / Information Disclosure | Derive Markdown report from machine packet and scan for overclaim terms. [VERIFIED: D-02; Phase 18/27 overclaim tests] |
| Output-root symlink escape | Tampering | Reuse contained output-root checks from prior verifiers and test symlink escape. [VERIFIED: Phase 27 symlink escape test] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md` - locked Phase 28 decisions, output expectations, source refs, and wiring requirements.
- `.planning/REQUIREMENTS.md` - READ-01, READ-02, READ-03 requirement text and traceability.
- `.planning/ROADMAP.md` - Phase 28 goal, success criteria, dependency, and requirement mapping.
- `.planning/STATE.md` and `.planning/PROJECT.md` - milestone state and blocked-by-default demotion posture.
- `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, `standards/core/architecture.md`, `standards/core/code-shape.md`, `standards/core/testing.md`, `standards/core/verification.md`, `standards/languages/rust.md` - repo-local and Bright Builds constraints.
- `tools/bazel/manifests/phase18_cutover_review_contract.json` - final criteria, status vocabularies, exception fields, upstream requirements, generated artifacts.
- `tools/bazel/phase18_cutover_review.py` and `tools/bazel/phase18_cutover_review_test.py` - upstream consumption, demotion blocking, exception coverage, report generation, and overclaim guards.
- `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` - Phase 26 upstream row schema, canonical criteria, release proof policy, generated artifacts.
- `tools/bazel/phase26_release_signing_upstream_evidence.py` and `tools/bazel/phase26_release_signing_upstream_evidence_test.py` - upstream row generation, blocker normalization, secret and overclaim tests.
- `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json` - decision axes, exception policy, hard-blocker policy, Phase 28 handoff policy.
- `tools/bazel/phase27_retained_code_acceptance_decisions.py` and `tools/bazel/phase27_retained_code_acceptance_decisions_test.py` - retained decisions, final-readiness summary, residual-risk/exception outputs, no-demotion tests.
- `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile` - v1.2 verifier wiring pattern.
- Local command probes: `python3 --version`, `bazel --version`, `just --version`, `cargo --version`, `jq --version`, `git --version`.

### Secondary (MEDIUM confidence)

- OWASP ASVS official site and GitHub README - current ASVS purpose, latest stable version, and versioned requirement reference guidance. [CITED: https://owasp.org/www-project-application-security-verification-standard/; https://github.com/OWASP/ASVS]

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Phase 18/23/24/25/26/27 all use the same Python/Bazel/just verifier architecture, and local tools are installed. [VERIFIED: existing files and command probes]
- Architecture: HIGH - Phase 28 decisions directly name source contracts, retained outputs, and wiring; Phase 26/27 provide the implementation template. [VERIFIED: `.planning/phases/28-final-readiness-packet-and-demotion-gate/28-CONTEXT.md`; Phase 26/27 summaries]
- Pitfalls: HIGH - Most pitfalls are already covered by Phase 18/26/27 tests and Phase 28 locked decisions. [VERIFIED: local tests and context]
- Security: MEDIUM - Local threat patterns are verified, and ASVS high-level source is official; exact ASVS requirement IDs should be selected during implementation only if the planner needs requirement-level mapping. [CITED: OWASP ASVS official site; VERIFIED: Phase 26/27 security tests]

**Research date:** 2026-06-25 [VERIFIED: system date]
**Valid until:** 2026-07-02 for ASVS/security taxonomy and local tooling versions; local repo contracts remain valid until edited. [CITED: OWASP ASVS current-source check; VERIFIED: local repo state]
