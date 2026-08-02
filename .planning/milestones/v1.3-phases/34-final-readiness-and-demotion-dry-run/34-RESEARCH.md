# Phase 34: Final Readiness and Demotion Dry Run - Research

**Researched:** 2026-07-25
**Requirements:** READY-01, READY-02, READY-03
**Scope:** Planning guidance for a Phase 34-specific consumer of the Phase 33 handoff

## Summary

Phase 34 should be a new standard-library Python verifier and generator over the v1.3 Phase 33 downstream handoff. Phase 28 is the semantic precedent for fail-closed readiness and explicit demotion approval, but it is tied to Phase 26/27 inputs and should remain unchanged.

The core implementation should be a pure coverage-ledger transformation surrounded by a thin filesystem and validation shell:

1. Load and validate the Phase 33 handoff, its Phase 32/31 snapshots, decision registers, readiness handoff, and demotion handoff.
2. Derive the expected real-evidence row set from Phase 31 accepted-final receipts and consumed upstream row refs.
3. Join Phase 32 classification and Phase 33 decision coverage by exact row ref and affected gate.
4. Emit one canonical readiness coverage ledger, then derive the packet, blocker summary, demotion dry-run result, and redacted report from it.
5. Set the dry-run gate to `open` only for `readiness_unblocked && approval_valid && approval_explicitly_approve`.

## Recommended Implementation

### New Phase 34 boundary

Create:

- `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json`
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py`
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`

Modify:

- `tools/bazel/BUILD.bazel`
- `BUILD.bazel`
- `tools/bazel/rust_workflow.sh`
- `justfile`

Planning artifacts add:

- `.planning/phases/34-final-readiness-and-demotion-dry-run/34-VALIDATION.md`

The verifier should default to:

- Phase 33 input: `build/ci-evidence/phase33/downstream-handoff-manifest.json`
- Phase 34 output: `build/ci-evidence/phase34`
- Lifecycle: the lifecycle id locked in `34-CONTEXT.md`

### Functional core

Keep these decisions pure and directly unit-testable:

- expected-row derivation from accepted-final receipts
- exact row-ref and gate-scope joins
- coverage-state classification
- readiness status derivation
- demotion predicate evaluation
- stable reason-code aggregation
- packet/report projection from the canonical ledger

The imperative shell should own:

- path-root containment
- JSON loading and schema validation
- lifecycle and source-contract checks
- prohibited-field and prohibited-text scans
- snapshot copying
- atomic output-root replacement
- CLI modes and exit codes

### Coverage ledger

The canonical ledger needs enough fields to make READY-01 and READY-02 auditable without raw evidence:

- `row_id`
- `source_stream`
- `source_ref`
- `requirement_ids`
- `affected_gates`
- `proof_eligibility`
- `evidence_status`
- `row_problem_kind`
- `blocker_kind`
- `severity`
- `evidence_refs`
- `artifact_refs`
- `classification_ref`
- `retained_code_decision_refs`
- `residual_risk_decision_refs`
- `exception_decision_refs`
- `readiness_decision_refs`
- `coverage_state`
- `readiness_effect`
- `reason_codes`

Expected rows must come from Phase 31 accepted-final receipts, not the Phase 32 blocker register alone. Phase 32 intentionally emits blocker rows and therefore cannot prove the presence of clean passed rows.

Exact anti-joins must block readiness for:

- required row absent
- duplicate or dangling row ref
- failed or blocked evidence
- stale lifecycle
- malformed input
- redaction failure
- source-ref failure
- secret-tainted or unsafe ref
- local-only, smoke, quick, placeholder, prose, or row-only non-final proof
- missing or unknown classification
- uncovered exception request
- unmatched exception scope or affected gate
- unaccepted retained-code or residual-risk decision where required
- invalid or missing readiness decision

### Demotion dry-run

Retain separate fields:

- `readiness_state`: `blocked` or `unblocked`
- `approval_validation_state`: `missing`, `invalid`, or `valid`
- `approval_decision_state`: `missing`, `approve`, or `reject`
- `gate_state`: `blocked` or `open`
- `reason_codes`
- `source_refs`

The only open truth table row is:

| Readiness | Approval validation | Approval decision | Gate |
| --- | --- | --- | --- |
| unblocked | valid | approve | open |

Every other combination is blocked. Missing, malformed, stale, lifecycle-mismatched, or rejected approval must still produce a durable blocked JSON artifact. The command may also return nonzero for invalid input, but the retained blocked result is mandatory for the audit trail.

### Generated artifacts

Recommended contract bundle:

- `final-readiness-run-manifest.json`
- `readiness-coverage-ledger.json`
- `final-readiness-packet.json`
- `readiness-blocker-summary.json`
- `demotion-dry-run.json`
- `redacted-readiness-report.md`
- `contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json`
- safe Phase 33/32/31 contract and handoff snapshots required to audit the run

The default/quick path must remain visibly blocked and must never synthesize maintainer approval. An isolated test fixture should prove the open conjunction.

## Existing Patterns to Reuse

- `tools/bazel/phase33_maintainer_decision_inputs.py` provides Phase 32 handoff loading, exact source-row validation, exception coverage, residual-risk coverage, readiness handoff, demotion handoff, security scanning, output-root guards, and workflow checks.
- `tools/bazel/phase28_final_readiness_packet.py` provides the prior two-axis policy vocabulary, hard-blocker precedence, demotion approval conjunction, generated-output validation, snapshot handling, and redacted reporting.
- `tools/bazel/phase31_final_evidence_intake.py` and `tools/bazel/phase32_blocker_register_triage.py` define accepted-final receipts, proof eligibility, row problem kinds, and canonical blocker refs.
- `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` show the exact phase target and facade pattern.

Do not:

- modify Phase 28 to accept Phase 33 data
- translate Phase 33 inputs into Phase 26/27-shaped criteria
- create a second evidence classification policy
- infer clean passed rows from absence in the Phase 32 blocker register
- treat a verifier crash as the only record of a blocked demotion dry run

## Security Threat Model

| Threat | Boundary | Mitigation | Verification |
| --- | --- | --- | --- |
| Secret-bearing evidence copied into Phase 34 | Phase 33/31 refs to generated outputs | Consume only sanitized handoff artifacts; recursively reject forbidden fields/text; never read raw evidence payloads | Secret-key/token/certificate/crash-payload fixtures fail before trusted output |
| Path escape or symlink escape | CLI inputs and output root | Require repository-relative paths under exact phase roots; resolve containment; reject input inside output root | Traversal, absolute path, wrong-root, and symlink tests |
| Green evidence implies demotion | Readiness to authorization boundary | Orthogonal predicates; explicit approval required; prohibit inferred approval markers | Full readiness × approval truth table |
| Stale or cross-lifecycle approval | Phase 33 handoff and decision refs | Exact lifecycle and contract-id validation; stable source refs | Stale lifecycle and mismatched contract tests |
| Underclassified evidence disappears | Phase 31 expected rows to Phase 32 register | Exact anti-join; unknown/missing classification blocks | Missing classification and unknown-kind tests |
| Broad exception masks blockers | Phase 33 exception decisions | Exact blocker refs and affected-gate scope; hard blockers outrank normal exceptions | Mismatched ref/gate and hard-blocker tests |
| Human report overclaims machine state | JSON ledger to Markdown report | Generate report only from canonical ledger/packet; scan prohibited markers | Golden assertions for blocked/open report headings |

The plan should mark high-severity authorization, secret, path-containment, and lifecycle threats as blocking.

## Pitfalls

1. Phase 32 is not a complete evidence row catalog. It is a blocker register, so clean passed rows require Phase 31 lineage.
2. Phase 33 quick output contains no real maintainer approval. Workflow wiring must preserve that blocked default.
3. Validation errors and gate results are related but distinct. Invalid approval needs a blocked artifact even if the command exits nonzero.
4. Artifact refs are audit links, not permission. Presence of a ref must never make a row proof-eligible.
5. Avoid a single flattened enum that hides concurrent readiness and approval failures.
6. Keep generated artifacts out of the repository and under `build/ci-evidence/phase34`.

## Validation Architecture

### Test layers

1. **Pure evaluator unit tests**
   - expected-row derivation
   - exact joins and anti-joins
   - exception and residual-risk coverage
   - readiness status
   - complete demotion truth table

2. **Contract and input validation tests**
   - required contract ids, lifecycle ids, enums, generated artifact list
   - missing/malformed/stale Phase 33 handoff
   - wrong-root, traversal, absolute, and symlink paths
   - forbidden field names and secret text

3. **Generated bundle tests**
   - all declared artifacts exist
   - packet and report derive from the ledger
   - blocked defaults are explicit
   - open fixture requires valid explicit approval
   - source refs point only to safe retained artifacts

4. **Wiring tests**
   - `tools/bazel/BUILD.bazel` verifier/test targets
   - root aliases and docs filegroup
   - `phase34_verify` and `phase34_verify_tests` shell cases
   - `just phase34-verify`

### Focused behavioral matrix

- all real rows covered, readiness approved, demotion approved -> `open`
- all real rows covered, readiness approved, demotion missing -> `blocked`
- all real rows covered, readiness approved, demotion rejected -> `blocked`
- all real rows covered, readiness approved, demotion malformed/stale -> retained `blocked` result plus validation failure
- failed/stale/malformed/redaction-failed row -> readiness `blocked`
- required row missing from classification -> readiness `blocked`
- unknown/underclassified row -> readiness `blocked`
- exception exact row and gate match -> cover only allowed blocker
- exception mismatch or hard-blocker attempt -> readiness `blocked`
- quick/default Phase 31-33 artifacts -> readiness and demotion `blocked`

### Commands

```bash
python3 -m py_compile tools/bazel/phase34_final_readiness_demotion_dry_run.py tools/bazel/phase34_final_readiness_demotion_dry_run_test.py
python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q
python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --contract-only
python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --security-only
python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --wiring-only
python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --quick --phase33-handoff build/ci-evidence/phase33/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase34
bazel run //tools/bazel:phase34_verify_tests
bazel run //tools/bazel:phase34_verify
just phase34-verify
git diff --check
```

Because this repository contains `Cargo.toml`, final phase verification must also run:

```bash
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

## Planning Recommendation

Use one plan with three tasks:

1. Contract plus RED-first tests for coverage, authorization, security, and generated artifacts.
2. Phase 34 verifier implementation with a pure evaluator and thin I/O shell.
3. Bazel/root/workflow/just wiring, validation signoff, and full verification.

One plan keeps the contract, evaluator, and facade in a single lifecycle while retaining task-level atomic commits.
