---
generated_by: gsd-phase-researcher
phase: 36
phase_name: normalize-evidence-and-blocker-rows
lifecycle_mode: yolo
phase_lifecycle_id: 36-2026-07-26T00-27-52
generated_at: 2026-07-26T00:44:00Z
status: complete
---

# Phase 36: Normalize Evidence and Blocker Rows - Research

## Research Question

What does the planner need to know to repair the real Phase 26-through-32 table boundary and give Phase 27/28 decision rows stable, resolvable identities without implementing Phase 37 readiness reconciliation?

## Recommendation

Keep the change centered in Phase 32. Extend `tools/bazel/phase32_blocker_register_triage.py` with contract-keyed input adapters and a typed canonical identity builder, update the Phase 32 contract, and deepen the Phase 32 tests so they generate real Phase 26, 27, and 28 outputs. Do not change Phase 26, Phase 27, Phase 28, or Phase 31 producer schemas.

Use a functional-core/imperative-shell split:

1. The shell loads Phase 31 receipts and the exact producer artifacts they reference.
2. Adapter functions validate known container and row shapes into typed normalized signals.
3. A pure identity function derives stable source and decision identities.
4. Existing classification and artifact projection consume those normalized signals.
5. The shell writes the existing Phase 32 bundle and runs the existing security scan.

This is one cohesive implementation plan unless the planner identifies a real dependency that requires splitting contract/adapter work from producer-shaped regressions.

## Current Failure Mechanism

`load_phase31_rows` in `tools/bazel/phase32_blocker_register_triage.py` follows `consumed_upstream_row_refs`, loads each referenced JSON value, and sends the top-level object through single-row status classification. The actual Phase 26 artifact is a table object with `rows`, not a row with top-level `status`. `classify_problem_kind` therefore falls through to `unknown_unclassified` even when every contained Phase 26 row passed.

The same module constructs blocker IDs through:

- `stable_sha12`
- `stable_row_id`
- `build_blocker_row`

The current hash input includes `source_ref` plus the entire mutable signal. Owner, evidence, status, timestamps, paths, or action text can therefore alter `row_id`. Phase 27 and Phase 28 also project overlapping criteria through different decision domains, so criterion or gate alone is not a safe identity.

`load_phase27_rows` and `load_phase28_rows` already locate the relevant producer outputs, but their existing tests primarily use handcrafted objects. Those tests prove local classification, not compatibility with the producer functions and contracts that caused the milestone integration gap.

## Recommended Architecture

### Contract-Keyed Adapter Dispatch

Add a small dispatch layer before classification. Dispatch must use trusted context:

- Phase 31 stream identity
- expected artifact kind/path from the Phase 31/32 contracts
- known Phase 26, 27, or 28 producer contract

Do not recursively search arbitrary JSON for row-like dictionaries.

Recommended normalized result model:

- zero or more valid normalized signals
- zero or more explicit fail-closed adapter problems
- provenance fields retained separately from classification fields

A recognized malformed container should return a `malformed` problem. An unsupported envelope, row discriminator, or status should return `unknown_unclassified`. Neither should raise an unhandled exception that prevents the canonical blocker register from recording the problem.

### Atomic Phase 26 Table Validation

The Phase 26 adapter should accept only the canonical `{"rows": [...]}` table referenced by an `accepted-final` Phase 31 receipt. Validate the whole table before returning any proof-eligible normalized row.

Reject atomically when:

- `rows` is absent, not a list, or empty
- an entry is not an object
- a required decision-bearing field is missing or has the wrong type
- a criterion is duplicate or unknown
- canonical required criterion coverage is incomplete

On success:

- passed rows produce no blocker
- failed or blocked rows produce criterion-addressed normalized signals
- lineage retains the Phase 31 receipt ref, Phase 26 table ref, and criterion ID

### Typed Canonical Identity

Extend canonical blocker rows with:

- `source_domain`
- `producer_phase`
- `producer_artifact_kind`
- `source_row_kind`
- `source_subject_id`
- `decision_axis`
- `decision_subject_id`

Derive `row_id` from only the immutable source tuple:

```text
source_domain
producer_phase
producer_artifact_kind
source_row_kind
source_subject_id
```

Do not include status, owner, severity, next action, evidence refs, timestamps, or storage paths in the identity payload.

Recommended source subjects:

- Phase 26: canonical `criterion_id`
- Phase 27 retained packets: `packet_id`
- Phase 27 projected rows: producer `row_id` or `criterion_id`, according to the producer contract
- Phase 28 readiness/residual-risk rows: `criterion_id`
- Phase 28 demotion record: fixed `final-reference-demotion-allowed`

Recommended decision axes:

- `retained_code`
- `residual_risk`
- `exception`
- `readiness`
- `demotion`

The exact enum spelling should be declared in the Phase 32 contract and tested. Gate names and artifact paths may validate context but must not become fallback join keys.

### Existing Output Compatibility

Keep the existing generated artifact set:

- `blocker-register.json`
- `decision-impact-index.json`
- `exception-request-register.json`
- `residual-risk-request-register.json`
- `downstream-handoff-manifest.json`
- `redacted-blocker-register-report.md`
- contract snapshots

Derived views must continue to reference canonical `row_id` values. Add the new identity fields to the canonical register and any handoff surface Phase 37 will consume. Phase 36 must not add decision resolution, approval, or readiness-opening logic.

## Exact Files and Seams

### Primary Implementation

- `tools/bazel/phase32_blocker_register_triage.py`
  - replace mutable-signal hashing in `stable_row_id`
  - add typed source/decision identity construction
  - add Phase 26 table adapter at the `load_phase31_rows` boundary
  - normalize Phase 27/28 rows before `build_blocker_row`
  - extend `validate_register_rows` for required identity fields and collisions
  - keep `build_derived_views`, `write_report`, and security scanning driven by the canonical register

- `tools/bazel/manifests/phase32_blocker_register_triage_contract.json`
  - declare new required row fields
  - declare source-domain, artifact-kind, source-row-kind, and decision-axis enums
  - declare Phase 26 table adapter and atomic validity requirements
  - keep unknown/malformed policy fail-closed

### Focused Tests

- `tools/bazel/phase32_blocker_register_triage_test.py`
  - generate real Phase 26 output, route it through Phase 31, then consume it in Phase 32
  - generate real Phase 27 and Phase 28 outputs and consume their actual artifacts
  - prove stable `row_id` under changes to mutable owner/status/evidence metadata
  - prove distinct decision axes cannot collide
  - mutate one malformed/unknown concern per test

### Wiring Only If Required

- `tools/bazel/BUILD.bazel`
- `BUILD.bazel`
- `tools/bazel/rust_workflow.sh`
- `justfile`

The current Phase 32 targets and recipe should be extended rather than creating a Phase 36-only verifier command. Update runfiles/data dependencies only when producer-shaped tests need additional contracts or producer modules.

## Security and Fail-Closed Risks

### Partial Table Acceptance

The highest-integrity risk is accepting valid-looking rows from a malformed table. Validate the complete Phase 26 table before returning any eligible signal.

### Identity Collision or Instability

Hashing mutable payloads invalidates explicit decisions when evidence changes; hashing only criterion or gate can merge distinct domains. Validate source-tuple uniqueness and separate decision identity from source identity.

### Provenance Bypass

Do not let direct Phase 26 files become proof-eligible without an `accepted-final` Phase 31 receipt. Phase 31 remains the finality, lifecycle, redaction, source-ref, and secret-safety boundary.

### Unsupported Shape Disappearance

Unknown envelopes and row kinds must become visible critical blockers. Do not skip them, default them to passed, or catch and suppress validation errors.

### Secret and Unsafe-Reference Expansion

Generic recursive flattening would traverse unrelated metadata and could widen the secret-bearing surface. Shape-specific adapters should retain only contract-approved fields and preserve the existing Phase 32 security scan.

### Authority Overclaim

The new identity fields enable later decisions; they do not approve anything. Generated reports and handoffs must not claim readiness, cutover approval, or reference demotion.

## Planning Guidance

Prefer one plan with three atomic tasks:

1. Contract and pure adapter/identity core, with focused unit tests for atomic table handling and stable identities.
2. Integrate normalized signals into Phase 31/27/28 loaders and canonical outputs, with compatibility and collision tests.
3. Add producer-shaped boundary regressions and update Bazel/runfiles/`just` verification only as required.

Every task should read the current Phase 32 implementation, contract, and tests before editing. Acceptance criteria should name exact fields, enum values, and commands. The plan must cover `INTAKE-04`, `TRIAGE-01`, and `TRIAGE-02`.

The plan threat model should include:

- forged or malformed producer envelopes
- partial-table proof eligibility
- source or decision identity collision
- mutable-data identity churn
- provenance bypass around Phase 31
- secret-field or unsafe-ref propagation
- readiness/demotion authority overclaim

## Validation Architecture

### Test Layers

| Layer | Purpose | Command |
| --- | --- | --- |
| Phase 32 unit/regression suite | Adapter dispatch, atomic table validity, identity stability/collisions, unknown/malformed fail-closed behavior | `python tools/bazel/phase32_blocker_register_triage_test.py` |
| Producer suites | Confirm Phase 26/27/28 fixtures remain valid producer outputs | `python tools/bazel/phase26_release_signing_upstream_evidence_test.py && python tools/bazel/phase27_retained_code_acceptance_decisions_test.py && python tools/bazel/phase28_final_readiness_packet_test.py` |
| Intake boundary suite | Confirm Phase 31 still validates and references the Phase 26 table without contract drift | `python tools/bazel/phase31_final_evidence_intake_test.py` |
| Bazel target | Confirm runfiles and target data include real producer contracts/modules | `bazel test //tools/bazel:phase32_blocker_register_triage_test` |
| Repo-native phase gate | Confirm tests run before the verifier and security/wiring checks remain active | `just phase32-verify` |
| Shell syntax | Confirm workflow edits remain syntactically valid if wiring changes | `bash -n tools/bazel/rust_workflow.sh` |

### Required Positive Scenarios

1. Real all-passed Phase 26 output flows through an accepted Phase 31 receipt and produces no release blocker.
2. Real failed/blocked Phase 26 rows produce criterion-addressed blockers with receipt and table lineage.
3. Real Phase 27 retained-code, residual-risk, exception, and readiness outputs receive distinct stable source and decision identities.
4. Real Phase 28 readiness, residual-risk, and demotion outputs receive distinct stable source and decision identities.
5. Derived views reference only canonical register `row_id` values.

### Required Negative Scenarios

Use one behavior per test with clear Arrange, Act, Assert sections:

1. missing, non-list, or empty Phase 26 `rows`
2. non-object Phase 26 entry
3. missing or mistyped required field
4. duplicate or unknown criterion
5. unknown Phase 27/28 row discriminator or status
6. duplicate immutable source tuple
7. decision-axis/source-subject collision
8. attempted proof eligibility without accepted-final Phase 31 provenance

### Nyquist Sampling

Run the focused Python suites after each adapter/identity task. Run the Bazel target and `just phase32-verify` after integration and before phase verification. If workflow wiring changes, run `bash -n` before the repo-native phase gate.

## Planning Conclusion

Phase 36 should deepen Phase 32's input boundary, not redistribute authority among producers. The smallest robust outcome is explicit table adaptation, immutable source identity, separate exact decision identity, and producer-shaped regression coverage through the Phase 32 handoff.
