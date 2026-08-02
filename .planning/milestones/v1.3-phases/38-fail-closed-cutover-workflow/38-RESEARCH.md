---
phase: 38-fail-closed-cutover-workflow
generated_by: gsd-phase-researcher-fallback
lifecycle_mode: yolo
phase_lifecycle_id: 38-2026-07-26T16-29-23
generated_at: 2026-07-26T16:42:00.000Z
status: complete
---

# Phase 38 Research: Fail-Closed Cutover Workflow

## Research Summary

Phase 38 should close the orchestration and publication gap identified as B3 without redefining readiness, verdict, or demotion semantics. Phases 36 and 37 already make the complete real-producer path reach unblocked Phase 34 readiness. The remaining failure is operational: Phase 34 loads several Phase 31/33 artifacts before its narrow invalid-demotion fallback, while `tools/bazel/rust_workflow.sh` runs Phase 34 before Phase 35 under `set -euo pipefail`. An early Phase 34 failure can therefore leave older Phase 34 and Phase 35 approval artifacts authoritative.

The smallest robust implementation is:

1. Expand Phase 34 failure publication to cover every untrusted Phase 31/33 loading and validation boundary.
2. Introduce a thin production coordinator that captures Phase 34 status, always runs Phase 35 finalization, and preserves a nonzero overall status after durable blocked publication.
3. Harden Phase 35 staged installation with a durable blocking authority guard and compensating restore.
4. Extend the actual-producer Phase 31-through-34 integration baseline through Phase 35 and add focused fault-injection tests for publication recovery.

This preserves the current fixed output directories and contracts while making failure reporting occur after authority replacement instead of instead of authority replacement.

## Current Implementation Findings

### Phase 34 fallback coverage starts too late

`run_quick` in `tools/bazel/phase34_final_readiness_demotion_dry_run.py` performs these operations before entering the existing demotion-handoff `try` block:

- validates the Phase 34 contract and required-stream contract;
- validates Phase 31 paths and loads the Phase 31 manifest, receipts, and accepted rows;
- validates and loads the Phase 33 handoff;
- loads normalized decisions, readiness input, register refs, and the Phase 32 blocker register.

Failures at any of those boundaries propagate directly and leave the prior Phase 34 bundle untouched. Only demotion-register loading currently calls `write_invalid_approval_artifacts`.

Recommended change: move untrusted input loading behind one publication boundary. Convert every `VerificationError` from Phase 31/33 loading, register digest validation, blocker-register loading, and decision normalization into a contract-defined blocked source-failure bundle, install it through the same staged publication helper used by successful output, run the security scan, then return or re-raise the original safe failure category.

Do not collapse all failures into a generic success. The command should still return nonzero after the blocked replacement is validated.

### Shell `set -e` prevents downstream finalization

The `phase35_verify` arm in `tools/bazel/rust_workflow.sh` invokes Phase 34 and then Phase 35 as ordinary commands. With `set -euo pipefail`, a nonzero Phase 34 status exits the script before Phase 35 can consume the newly blocked readiness bundle and replace a prior approved cutover artifact.

Recommended change: move Phase 34-to-35 finalization into a small standard-library Python coordinator and call that coordinator from the shell. The coordinator should:

- invoke Phase 34 with explicit arguments;
- retain the Phase 34 exit status and safe diagnostic category;
- invoke Phase 35 whenever Phase 34 produced a validated canonical bundle, including a blocked replacement;
- validate the final Phase 34 and Phase 35 authority states;
- return nonzero if either operational step failed, but only after final authority is blocked;
- never infer or copy demotion authorization.

The shell should remain a thin dispatcher and should not duplicate the coordinator's status truth table.

### Phase 35 staged installation deletes recoverable state

`install_staged_bundle` in `tools/bazel/phase35_cutover_decision_artifact.py` renames the canonical directory to a backup and then renames the stage into place. If the second rename fails, it deletes the backup instead of restoring it.

Restoring the backup unconditionally is unsafe because the backup may contain the stale approval that the new blocked stage was meant to replace. A two-rename directory swap is not a transaction across the failure window.

Recommended change: add a durable authority guard adjacent to the Phase 35 output root:

- write and validate a blocking guard before moving the canonical bundle;
- keep the guard authoritative while the old bundle is backed up, the stage is installed, and canonical validation runs;
- restore the backup on install failure for availability, but keep the guard blocking;
- clear the guard only after the installed canonical bundle passes generated-output, security, and authority validation;
- fail closed if guard cleanup, restore, or post-install validation fails.

Phase 35 readers and the workflow coordinator must reject or treat as blocked any canonical bundle when the guard is present or malformed. A guard that ordinary consumers can ignore does not satisfy the phase goal.

### The real-producer integration fixture is the right baseline

`tools/bazel/phase34_decision_reconciliation_integration_test.py` already executes real Phase 31, Phase 32, Phase 33, and Phase 34 producers. Its complete valid baseline reaches `readiness_state: unblocked`, and focused one-concern mutations prove exact typed decision failures stay blocked.

Extend that fixture through the real Phase 35 loading/publication boundary. Avoid handwritten snapshot-only inputs because B3 is specifically a producer/orchestrator integration defect.

Recommended primary cases:

| Case | Phase 34 | Phase 35 | Route | Demotion |
| --- | --- | --- | --- | --- |
| Default quick inputs | blocked | blocked | targeted blocker repair | blocked |
| Complete valid inputs | unblocked | approved | production-cutover planning | independent |
| One exact evidence/decision defect | blocked with exact reason | blocked | named targeted repair requiring fresh decision | blocked or independent as applicable |
| Invalid Phase 31 source after seeded approval | durable blocked replacement, nonzero | durable blocked replacement | targeted repair | blocked |
| Invalid Phase 33 source after seeded approval | durable blocked replacement, nonzero | durable blocked replacement | targeted repair | blocked |

Keep demotion as a separate focused truth table:

- approved cutover plus missing/rejected demotion remains closed;
- valid demotion approval plus blocked readiness remains closed;
- only unblocked readiness plus valid explicit demotion approval opens the dry run.

## Recommended Module and File Boundaries

Likely new files:

- `tools/bazel/phase38_cutover_workflow.py` — thin production coordinator and final authority validation.
- `tools/bazel/phase38_cutover_workflow_test.py` — coordinator status, stale-authority replacement, and route matrix tests.
- `tools/bazel/phase38_cutover_workflow_integration_test.py` — actual-producer Phase 31-through-35 paths.

Likely modified files:

- `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json`
- `tools/bazel/phase34_final_readiness_demotion_dry_run.py`
- `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py`
- `tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json`
- `tools/bazel/phase35_cutover_decision_artifact.py`
- `tools/bazel/phase35_cutover_decision_artifact_test.py`
- `tools/bazel/BUILD.bazel`
- `tools/bazel/rust_workflow.sh`
- `BUILD.bazel`
- `justfile`

Keep pure decisions separate from filesystem effects:

- pure: exit-status aggregation, final authority truth table, safe reason mapping, guard-state interpretation;
- imperative: subprocess calls, path validation, staging, rename/restore, security scan, and artifact writes.

Do not add test-only authority flags accepted by production entrypoints. Fault injection should use explicit callable filesystem seams or controlled mocks around rename/write operations.

## Security and Threat Boundaries

### T-38-01: Stale approval replay

An invalid Phase 31/33 source must not leave a prior `approved` Phase 35 artifact or production-cutover route authoritative. Seed prior approval in regressions and assert it is replaced.

### T-38-02: Guard bypass

A canonical Phase 35 bundle must be treated as blocked whenever the authority guard exists, is malformed, has an unexpected lifecycle, or cannot be read safely. Every production reader introduced or touched in this phase must enforce the guard.

### T-38-03: Symlink and path substitution

Guard, stage, backup, canonical output, and restored bundle paths must reject symlink escapes, absolute paths, traversal, wrong-root paths, and non-directory replacements before mutation.

### T-38-04: Partial publication and rollback failure

Each mutation boundary must preserve either a validated canonical bundle or an observable blocking guard. Cleanup failure must not clear authority protection.

### T-38-05: Diagnostic data leakage

Fallback and coordinator results may retain only safe reason categories, booleans, counts, lifecycle IDs, and sanitized refs. They must not copy raw packets, keys, tokens, certificates, crash dumps, or service payloads.

No high-severity threat may remain open in the final plans. Each plan needs a `<threat-model>` block and focused tests for the threats it changes.

## Pitfalls to Avoid

- Catching exceptions without publishing and validating a blocked replacement.
- Returning success merely because a fallback bundle was written.
- Running Phase 35 only when Phase 34 exits zero.
- Restoring any prior bundle without an active blocking guard.
- Clearing the guard before post-install validation and security scanning complete.
- Keeping coordinator semantics only in shell code where they are hard to unit test.
- Building a snapshot-only integration suite that never executes actual producers.
- Folding demotion authorization into cutover verdict or route state.
- Broadly refactoring all oversized Phase 32-35 files instead of splitting only touched Phase 38 seams.

## Validation Architecture

### Test layers

1. **Pure coordinator tests**
   - Phase 34 success/failure and Phase 35 success/failure combinations produce one final status.
   - Operational failure remains nonzero after blocked finalization.
   - Approved route requires a valid approved Phase 35 verdict.
   - Demotion state never upgrades cutover verdict or route.

2. **Phase 34 fallback tests**
   - Each Phase 31/33 loading and validation boundary replaces seeded prior approval with a blocked bundle.
   - Blocked artifacts retain safe exact reason codes and pass security/output validation.

3. **Phase 35 publication recovery tests**
   - Fault injection covers guard write, prior rename, stage rename, post-install validation, restore, and cleanup.
   - Every fault leaves either a validated blocked bundle or a blocking guard plus recoverable canonical data.
   - Prior approved authority is never revived.

4. **Real-producer Phase 31-through-35 integration**
   - Default blocked, complete approved, targeted repair, invalid Phase 31, and invalid Phase 33 paths execute actual producer shapes.
   - Seeded prior Phase 34/35 approval is durably replaced on source failure.
   - JSON verdict, route, readiness, demotion, and redacted report projections agree.

5. **Hermetic wiring**
   - Bazel includes coordinator, focused suites, producer runfiles, and integration suite.
   - `rust_workflow.sh` calls the coordinator rather than relying on `set -e` sequencing.
   - `just phase38-verify` runs tests before publication.

### Fast feedback commands

After Phase 34 changes:

```bash
python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q
```

After Phase 35 guard/install changes:

```bash
python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q
```

After coordinator changes:

```bash
python3 tools/bazel/phase38_cutover_workflow_test.py -q
bash -n tools/bazel/rust_workflow.sh
```

After end-to-end changes:

```bash
python3 tools/bazel/phase38_cutover_workflow_integration_test.py -q
```

### Full phase gate

```bash
just phase38-verify
```

The phase gate should run all focused Phase 34, Phase 35, Phase 38 coordinator, and real-producer integration tests before publishing the default blocked workflow bundle.

Because the repository contains `Cargo.toml`, every executor commit must also run the required sequence in order:

```bash
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

### Nyquist sampling

- After every implementation task: run the narrowest affected Python suite plus the mandatory Rust sequence.
- After coordinator/wiring work: run `bash -n`, the Phase 38 coordinator test, and the full `just phase38-verify` gate.
- Before phase verification: run `git diff --check`, `just phase38-verify`, the mandatory Rust sequence, and lifecycle validation.
- No manual-only behavior is required; all Phase 38 outcomes are deterministic CLI, filesystem, JSON, and Markdown behavior.

### Wave 0 gaps

- Add `tools/bazel/phase38_cutover_workflow_test.py` before coordinator implementation if the planner separates test scaffolding from implementation.
- Add focused rename/restore/guard failure fixtures before modifying `install_staged_bundle`.
- Add `tools/bazel/phase38_cutover_workflow_integration_test.py` before wiring the authoritative Phase 38 gate.
- Existing Python `unittest`, Bazel, shell syntax, and Rust verification infrastructure otherwise cover the phase.

## RESEARCH COMPLETE
