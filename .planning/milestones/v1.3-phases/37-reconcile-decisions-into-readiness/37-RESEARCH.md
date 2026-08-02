---
phase: 37-reconcile-decisions-into-readiness
generated_by: gsd-phase-researcher-fallback
lifecycle_mode: yolo
phase_lifecycle_id: 37-2026-07-26T06-52-46
generated_at: 2026-07-26T07:00:07.736Z
status: complete
---

# Phase 37 Research: Reconcile Decisions Into Readiness

## Research Summary

Phase 37 should repair the Phase 32/33-to-34 join, not weaken the existing fail-closed policy. Phase 36 already supplies the missing canonical primitives: every Phase 27/28 decision-domain blocker has an immutable `row_id` plus a separate `decision_axis` and `decision_subject_id`. The current Phase 34 evaluator discards that distinction because it builds expected rows only from Phase 31 receipts, matches evidence blockers by `(source_ref, affected_gate, source_stream)`, and converts every unmatched Phase 27/28 row into an unconditional `dangling-blocker`.

The smallest robust design is a dual-source typed ledger:

1. Keep Phase 31 receipts and required-stream specifications as the evidence-completeness authority.
2. Materialize canonical Phase 32 decision-domain rows as first-class ledger rows.
3. Bind Phase 33 decisions to those rows with explicit clear-text triples: `row_ref`, `decision_axis`, and `decision_subject_id`.
4. Require exact one-row matches and apply axis-specific approval values.
5. Preserve every invalid, stale, unmatched, duplicate, conflicting, rejected, or blocking decision as a blocking diagnostic.

This closes milestone-audit gap B1 while leaving Phase 38's stale-authority replacement and full Phase 31-35 workflow behavior out of scope.

## Current Implementation Findings

### Phase 32 identity is already sufficient

`tools/bazel/phase32_blocker_normalization.py` validates the supported decision axes and keeps `decision_axis`/`decision_subject_id` separate from the immutable source tuple used to derive `row_id`. `tools/bazel/phase32_blocker_register_triage.py` publishes those fields for actual Phase 27/28 producer rows. Phase 36 verification proves that retained-code, residual-risk, exception, readiness, and demotion identities survive real producer execution.

Phase 37 should consume these exact fields. It should not change Phase 32 identity derivation or add path/gate/prefix fallback matching.

### Phase 33 decisions lack per-target typed identity

`tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` currently requires `source_row_refs` and one top-level `decision_axis`, but not the canonical `decision_subject_id` for each referenced row. A decision can therefore carry row refs without proving that each target's axis and subject match.

Recommended contract extension:

```json
{
  "decision_targets": [
    {
      "row_ref": "build/ci-evidence/phase32/blocker-register.json#<row_id>",
      "decision_axis": "retained_code",
      "decision_subject_id": "<producer-subject>"
    }
  ]
}
```

Keep `source_row_refs` as a derived compatibility projection if existing downstream/report surfaces still need it, but validate that it is exactly the ordered or sorted projection of `decision_targets[*].row_ref`. Reject empty targets, duplicate target triples, duplicate row refs within a decision, conflicting decisions for the same target, and any target that matches zero or multiple canonical rows.

Phase 33 should normalize and publish these clear-text bindings because it owns the decision-input boundary. Phase 34 should revalidate them against its Phase 32 snapshot rather than trusting a copied identity.

### Phase 34 has one evidence-centric join and one dangling fallback

`tools/bazel/phase34_final_readiness_demotion_dry_run.py` currently:

- derives expected rows from Phase 31;
- indexes Phase 32 blockers by evidence join keys and row ID;
- evaluates evidence coverage through `coverage_for_row`;
- emits every unmatched Phase 32 row through `dangling_blocker_row`;
- checks dangling decisions primarily through row refs and affected gates.

That structure is correct for evidence completeness but incomplete for Phase 27/28 decision-domain rows. Do not overload `coverage_for_row` with all decision semantics. Extract a small pure reconciliation core that:

- parses a canonical decision-domain row into a typed structure;
- parses and indexes Phase 33 `decision_targets`;
- requires exact `(row_ref, decision_axis, decision_subject_id)` equality;
- rejects ambiguous cardinality and conflicts;
- maps axis/value pairs to `unblocked` or `blocked`;
- returns stable coverage state, decision refs, and reason codes for ledger serialization.

Suggested new files:

- `tools/bazel/phase34_decision_reconciliation.py`
- `tools/bazel/phase34_decision_reconciliation_test.py`
- `tools/bazel/phase34_decision_reconciliation_integration_test.py`

This avoids growing the already oversized Phase 34 verifier and keeps business rules in a pure, unit-testable core.

## Recommended Data Semantics

### First-class decision-domain ledger rows

For each canonical Phase 32 row with a supported non-evidence `decision_axis`, produce one ledger row that retains:

- canonical `row_id` and Phase 32 `classification_ref`;
- source domain, producer phase, producer artifact kind, source row kind, and source subject ID;
- `decision_axis` and `decision_subject_id`;
- affected gates and requirement IDs;
- blocker/problem/severity/proof-eligibility fields;
- matched normalized decision refs;
- `coverage_state`, `readiness_effect`, and stable reason codes.

Evidence rows remain sourced from Phase 31 and overlaid with matching Phase 32 classifications. Do not duplicate Phase 31 evidence rows merely because Phase 32 also references them.

### Axis-specific clearing values

Recommended clearing values:

| Axis | Clearing value(s) | Blocking values |
| --- | --- | --- |
| `retained_code` | `accept`, `exception_approve` when contract-allowed | `reject`, invalid, missing, conflict |
| `residual_risk` | `accept` | `reject`, invalid, missing, conflict |
| `exception` | `approve` with exact linked blocker/gate scope | `reject`, invalid, missing, conflict |
| `readiness` | `approve` only after all underlying rows are otherwise unblocked | `block`, invalid, missing, conflict |
| `reference_demotion` | Never clears readiness by itself; remains an independent authorization input | `reject`, invalid, missing, conflict |

Hard blocker kinds remain non-coverable. A decision target that references a hard blocker must remain blocking even if its value is normally approving.

### Fail-closed reason categories

Use stable, specific reason codes rather than collapsing failures into `dangling-row-ref`. Recommended categories:

- `decision-target-missing`
- `decision-target-row-mismatch`
- `decision-target-axis-mismatch`
- `decision-target-subject-mismatch`
- `decision-target-duplicate`
- `decision-target-conflict`
- `decision-lifecycle-stale`
- `decision-value-invalid`
- `decision-rejected`
- `decision-hard-blocker`

Existing `dangling-row-ref`, `duplicate-row`, and source-validation codes may remain for non-decision inputs.

## Integration Regression Strategy

Create one dedicated Phase 31-through-34 integration test. The fixture should execute or directly reuse the actual Phase 26/27/28 producers, feed them through the real Phase 31/32 outputs, create valid Phase 33 decisions using the production normalizer, and invoke the real Phase 34 CLI/loading/publication path.

The baseline must assert:

- all required Phase 31 evidence streams are present and valid;
- Phase 32 emits canonical decision-domain identities;
- Phase 33 normalized records carry exact typed target bindings;
- Phase 34 publishes the full retained bundle;
- no decision-domain row is an unconditional `dangling-blocker`;
- every exact valid decision is linked to its intended ledger row;
- `final-readiness-packet.json` reports `readiness_state: unblocked`.

Derive one-concern negative tests from the same fixture by mutating exactly one of:

- row ref;
- decision axis;
- decision subject;
- lifecycle ID/timestamp;
- decision value;
- duplicate binding;
- conflicting decision;
- omitted decision.

Each negative case must publish blocked readiness with the specific expected reason code. Phase 35 invocation, stale Phase 34/35 replacement, and production-cutover routing remain Phase 38 work.

## Likely File Changes

Core contract and implementation:

- `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json`
- `tools/bazel/phase33_maintainer_decision_inputs.py`
- `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json`
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py`
- `tools/bazel/phase34_decision_reconciliation.py` (new)

Focused and integration tests:

- `tools/bazel/phase33_maintainer_decision_inputs_test.py`
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
- `tools/bazel/phase34_decision_reconciliation_test.py` (new)
- `tools/bazel/phase34_decision_reconciliation_integration_test.py` (new)

Hermetic wiring:

- `tools/bazel/BUILD.bazel`
- `tools/bazel/rust_workflow.sh`

Root `BUILD.bazel` and `justfile` should not need new public aliases if the existing `phase34_verify_tests`, `phase34_verify`, and `just phase34-verify` surfaces are extended to cover the new modules and integration test.

## Risks and Mitigations

- **Copied identity drift:** Phase 33 target bindings repeat Phase 32 identity. Mitigate by exact revalidation against the Phase 32 snapshot at both Phase 33 normalization and Phase 34 consumption.
- **Decision flattening:** Each axis has different values and readiness effects. Mitigate with an explicit axis/value table and exhaustive focused tests.
- **Evidence double counting:** Phase 32 is sparse and Phase 31 is complete. Mitigate by keeping separate evidence and decision-domain constructors before merging into one ledger.
- **Multi-target ambiguity:** One decision can enumerate multiple rows. Mitigate by validating every target independently and rejecting duplicate/conflicting target coverage.
- **Scope capture:** A Phase 31-35 test would absorb Phase 38. Stop at Phase 34 retained artifacts.
- **Large-file growth:** Phase 33/34 files already exceed refactor triggers. Put new pure join logic and focused tests in new modules rather than expanding the existing mixed-responsibility files unnecessarily.
- **Secret/provenance regression:** Reuse the current safe-ref, path containment, snapshot, redaction, and security-scan boundaries; typed targets contain only canonical refs and non-secret identifiers.

## Standards Applied

- `standards/core/architecture.md`: parse typed target bindings at the boundary and keep reconciliation as pure data transformation behind the Phase 33/34 filesystem shell.
- `standards/core/code-shape.md`: use early returns and extract the new decision core rather than extending oversized files.
- `standards/core/testing.md`: one behavior per test with explicit Arrange, Act, Assert.
- `standards/core/verification.md`: extend the existing repo-owned Phase 34 verification entrypoint and run relevant Rust workspace checks before every commit as required by `AGENTS.md`.

## Validation Architecture

### Test layers

1. **Pure decision reconciliation unit tests**
   - Exact triple match clears only the intended row.
   - Every axis/value combination has one focused test.
   - Zero, multiple, duplicate, conflicting, stale, rejected, invalid, and hard-blocker cases remain blocked.

2. **Phase 33 boundary tests**
   - Contract requires `decision_targets`.
   - Normalizer validates each target against the canonical Phase 32 register.
   - `source_row_refs` exactly projects target row refs.
   - Generated handoff and redacted report retain safe typed identities.

3. **Phase 34 ledger tests**
   - Phase 31 evidence completeness remains unchanged.
   - Decision-domain rows are first-class ledger rows.
   - Exact decisions attach to only matching rows.
   - JSON packet, blocker summary, dry-run artifact, and Markdown report derive from the same ledger state.

4. **Real-producer integration test**
   - Actual Phase 31-33 outputs reach unblocked Phase 34 readiness only for the valid baseline.
   - One-concern negative mutations remain blocked with exact reason codes.

### Fast feedback commands

After reconciliation-core changes:

```bash
python3 tools/bazel/phase34_decision_reconciliation_test.py -q
```

After Phase 33 boundary changes:

```bash
python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q
```

After Phase 34 ledger changes:

```bash
python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q
```

After integration/wiring changes:

```bash
python3 tools/bazel/phase34_decision_reconciliation_integration_test.py -q
bash -n tools/bazel/rust_workflow.sh
```

### Full phase gate

```bash
just phase34-verify
```

The extended `phase34_verify_tests` target must run the Phase 33 suite, reconciliation unit suite, Phase 34 suite, and real-producer integration suite before the verifier publishes outputs.

Because the repository contains a Rust workspace and `AGENTS.md` requires the full Rust pre-commit sequence before any commit, run in order before every executor commit:

```bash
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

### Nyquist sampling

- After every implementation task: run the narrowest affected Python test command and the mandatory Rust pre-commit sequence.
- After the integration/wiring task: run the integration test, `bash -n`, and `just phase34-verify`.
- Before phase verification: run `git diff --check`, `just phase34-verify`, and the mandatory Rust sequence.
- No manual-only behavior is required; all Phase 37 acceptance criteria are deterministic CLI/JSON behavior.

## RESEARCH COMPLETE
