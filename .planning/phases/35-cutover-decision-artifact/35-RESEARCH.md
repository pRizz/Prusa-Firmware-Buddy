---
generated_by: gsd-phase-researcher
phase: 35
phase_name: cutover-decision-artifact
lifecycle_mode: yolo
phase_lifecycle_id: 35-2026-07-25T21-06-10
generated_at: 2026-07-25T21:42:00Z
status: complete
---

# Phase 35: Cutover Decision Artifact - Research

## Research Question

What does the planner need to know to implement Phase 35 as the smallest robust projection of the Phase 31-34 evidence and decision machinery while satisfying CUTOVER-01 through CUTOVER-03?

## Recommendation

Build Phase 35 as one contract-driven standard-library Python verifier/generator plus one focused `unittest` module and the established Bazel/root/workflow/`just` wiring. Reuse the Phase 34 artifact-loading, path-containment, lifecycle, prohibited-field, prohibited-text, safe-reference, wiring, and generated-output validation patterns. Do not introduce a new evidence schema, maintainer-decision input, policy runtime, signing model, or production action.

The implementation should have a functional core with four total transformations:

1. Normalize and validate the Phase 34 readiness bundle and the Phase 33 decision lineage it references.
2. Derive the exact canonical audit-link set required by CUTOVER-02.
3. Reduce validated facts to one `approved`, `blocked`, or `approved-with-exceptions` verdict.
4. Derive exactly one next-milestone route plus an independent demotion-state projection.

Filesystem loading, containment checks, security scanning, artifact writes, contract snapshotting, and command-line handling should stay in the imperative shell.

## Immediate Upstream Boundary

Phase 34 already writes the authoritative immediate inputs under `build/ci-evidence/phase34`:

- `final-readiness-run-manifest.json`
- `readiness-coverage-ledger.json`
- `final-readiness-packet.json`
- `readiness-blocker-summary.json`
- `demotion-dry-run.json`
- `redacted-readiness-report.md`
- sanitized contract and source snapshots

The Phase 35 loader should start from `final-readiness-run-manifest.json`, verify its lifecycle and contract identity, and follow only the safe refs declared by that manifest. It should not search the filesystem for alternate artifacts or accept a caller-supplied verdict.

Phase 34's code already provides the patterns Phase 35 needs:

- `load_json`, `require_list`, `require_string`, and `require_iso_utc`
- forbidden-field and forbidden-text scans
- `repo_relative_path`, `path_under`, `resolved_under`, and symlink containment
- `validate_ref` and `validate_refs`
- contract identity and lifecycle checks
- pure gate evaluators followed by one `write_bundle`
- `validate_generated_outputs`
- wiring inspection for Bazel, shell workflow, and `just`
- durable blocked artifacts on invalid or missing authorization inputs

The planner should reference these patterns concretely rather than requesting generic consistency with Phase 34.

## Proposed Phase 35 Contract

Create `tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json` with:

- `id`, `phase`, `phase_lifecycle_id`, `schema_version`, and `requirement_ids`
- exact Phase 34 source contract/lifecycle and immediate input refs
- exact generated artifact names
- verdict enum: `approved`, `blocked`, `approved-with-exceptions`
- route enum: `production-cutover-planning`, `targeted-blocker-repair`
- audit-link categories and required fields
- blocked reason codes
- verdict truth table and route truth table
- independent demotion projection fields
- output root `build/ci-evidence/phase35`
- prohibited field names, text markers, semantics, and unsafe refs
- verification commands and wiring expectations

Recommended audit-link row fields:

- `link_id`
- `kind`
- `target_id`
- `target_ref`
- `source_phase_lifecycle_id`
- `verdict_effect`
- `digest` for sanitized local targets, omitted for opaque external refs

Recommended categories:

- `evidence-packet`
- `blocker`
- `exception`
- `residual-risk`
- `retained-code-decision`
- `readiness-decision`
- `readiness-result`
- `demotion-decision`
- `demotion-dry-run`

The contract should require exact-set equality between expected and generated semantic IDs. Unknown categories or fields must fail closed.

## Proposed Generated Bundle

Write under `build/ci-evidence/phase35`:

- `cutover-decision-run-manifest.json`
- `cutover-audit-link-index.json`
- `cutover-decision.json`
- `next-milestone-route.json`
- `redacted-cutover-decision-report.md`
- `contract-snapshots/phase35_cutover_decision_artifact_contract.json`
- `contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json`
- `contract-snapshots/phase34-final-readiness-run-manifest.json`

`cutover-decision.json` should contain at least:

- phase and lifecycle identity
- exactly one `cutover_verdict`
- deterministic reason codes
- readiness state and source refs
- active valid exception IDs
- blocker IDs
- audit-link index ref and counts by category
- independent `demotion_decision_state`
- independent `demotion_gate_state`
- route ref

`next-milestone-route.json` should contain:

- exactly one route
- source verdict
- named follow-up scope for repair routes
- owner, required action, affected gate, requirement IDs, and exit/review criteria
- an explicit `requires_fresh_cutover_decision` boolean
- an explicit planning-only/no-production-action statement for the approved route

The Markdown report must be generated from the same canonical structures as the JSON outputs.

## Verdict and Route Semantics

Use one total pure reducer:

| Input state | Verdict |
| --- | --- |
| Any invalid, missing, unknown, underclassified, incomplete, unsafe, or readiness-blocking input | `blocked` |
| Readiness unblocked and one or more exact valid active approved exceptions | `approved-with-exceptions` |
| Readiness unblocked and no active approved exceptions | `approved` |

Route deterministically:

| Verdict | Route |
| --- | --- |
| `approved` | `production-cutover-planning` |
| `blocked` | `targeted-blocker-repair` |
| `approved-with-exceptions` | `targeted-blocker-repair` |

Demotion state is not an input that silently upgrades the cutover verdict and the cutover verdict never upgrades demotion. Project the Phase 33 decision validity/value and Phase 34 dry-run gate state separately.

## File Plan

Expected created files:

- `tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json`
- `tools/bazel/phase35_cutover_decision_artifact.py`
- `tools/bazel/phase35_cutover_decision_artifact_test.py`

Expected modified files:

- `tools/bazel/BUILD.bazel`
- `BUILD.bazel`
- `tools/bazel/rust_workflow.sh`
- `justfile`
- `.planning/phases/35-cutover-decision-artifact/35-VALIDATION.md`

One plan with three tasks is the best fit:

1. Contract plus RED-first tests.
2. Verifier/generator implementation and generated-bundle validation.
3. Bazel/root/workflow/`just` wiring, validation signoff, and full verification.

This mirrors the successful Phase 34 shape and keeps task-level commits focused.

## Testing Strategy

The test module should use focused `unittest` cases with Arrange/Act/Assert sections when the shape is not trivial. Cover:

- contract identity, lifecycle, requirements, artifacts, fields, enums, and truth tables
- default quick path emits `blocked` and targeted repair
- all three verdicts
- exact route mapping for all three verdicts
- every Phase 34 readiness blocker and invalid-input family remains blocked
- exact valid exception set produces only `approved-with-exceptions`
- unmatched, broad, rejected, expired, stale, or invalid exceptions remain blocked
- exact audit-link set and per-category completeness
- missing, extra, duplicate, dangling, lifecycle-mismatched, category-mismatched, and digest-mismatched links
- stable IDs and deterministic output order
- independent demotion decision and gate truth tables
- approved cutover never implies demotion approval
- repair route contains named owners, actions, gates, requirements, and exit/review criteria
- approved route is planning-only
- unsafe absolute/traversal/wrong-root/overlapping/symlink paths
- forbidden fields, secret patterns, unsafe refs, and overclaim markers
- JSON/Markdown consistency
- Bazel/root/workflow/`just` wiring

## Security and Privacy

Keep Phase 35 inside the established sanitized boundary:

- consume validated summaries, ledgers, decision records, and refs only
- never read raw evidence payloads for report generation
- allow repository-relative refs under contract-defined output roots
- allow already-approved `external://phaseXX/` refs without dereferencing them
- reject absolute paths, traversal, output/input overlap, wrong roots, and symlink escapes
- reject forbidden secret-bearing field names and text patterns before writes
- snapshot only safe contracts and manifests
- do not claim signing, attestation, production approval, rollout, or demotion execution

## Pitfalls to Avoid

1. Deriving completeness from only blocker rows. Phase 32 is intentionally sparse; clean passed rows still matter to the audit link set.
2. Treating Phase 34's redacted Markdown report as authoritative. Machine-readable artifacts are the source of truth.
3. Accepting links declared by `cutover-decision.json` instead of deriving expected links independently.
4. Hashing volatile generated timestamps and creating nondeterministic digests. Digest stable sanitized targets or a canonical stable projection.
5. Coupling cutover approval to demotion approval or treating approved cutover as execution authority.
6. Routing `approved-with-exceptions` to production planning contrary to the locked Phase 35 context and roadmap.
7. Letting quick fixtures synthesize real maintainer decisions or final evidence.
8. Adding OPA, attestation signing, dashboards, or post-cutover execution to this milestone.

## Validation Architecture

### Layer 1: Contract and Syntax

- `python3 -m py_compile tools/bazel/phase35_cutover_decision_artifact.py tools/bazel/phase35_cutover_decision_artifact_test.py`
- `python3 tools/bazel/phase35_cutover_decision_artifact.py --contract-only`

### Layer 2: Focused Unit and Truth-Table Tests

- `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q`
- Verify every verdict, route, audit-link failure, and demotion-separation branch.

### Layer 3: Security and Reference Boundaries

- `python3 tools/bazel/phase35_cutover_decision_artifact.py --security-only`
- Exercise absolute path, traversal, wrong root, overlap, symlink escape, forbidden field, secret text, unsafe ref, and overclaim failures in the unit suite.

### Layer 4: Wiring

- `python3 tools/bazel/phase35_cutover_decision_artifact.py --wiring-only`
- Assert exact `phase35_verify` and `phase35_verify_tests` targets/aliases, `rust_workflow.sh` arms, and `just phase35-verify`.

### Layer 5: Quick Generated Bundle

- Run the Phase 34 quick prerequisite.
- Run Phase 35 quick generation against `build/ci-evidence/phase34`.
- Assert `cutover_verdict == "blocked"`.
- Assert route is `targeted-blocker-repair`.
- Assert demotion fields remain separate and blocked.
- Validate every generated artifact and JSON/Markdown projection.

### Layer 6: Bazel and Developer Facade

- `bazel run //tools/bazel:phase35_verify_tests`
- `bazel run //tools/bazel:phase35_verify`
- `just phase35-verify`

### Layer 7: Relevant Regression

- Run Phase 28 and Phase 31-35 Python regression suites or the repo-owned aggregate command if the new workflow facade includes them.
- Confirm Phase 34 default artifacts remain blocked and unchanged in meaning.

### Layer 8: Repository Commit Gate

The repository contains `Cargo.toml`, so before the final commit run in order:

1. `cargo fmt --all`
2. `cargo clippy --all-targets --all-features -- -D warnings`
3. `cargo build --all-targets --all-features`
4. `cargo test --all-features`

Also run `git diff --check` and review the final diff for unintended generated or unrelated changes.

## Planning Conclusion

Phase 35 is suitable for one three-task plan. The highest-risk work is not code volume; it is proving that audit links are complete and that the three independent concepts—readiness, cutover verdict, and demotion authorization—never collapse into one implicit approval. The plan should make those truth tables and anti-joins explicit before implementation begins.
