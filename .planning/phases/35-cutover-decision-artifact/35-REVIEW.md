---
phase: 35-cutover-decision-artifact
reviewed: 2026-07-25T22:26:42Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json
  - tools/bazel/phase35_cutover_decision_artifact.py
  - tools/bazel/phase35_cutover_decision_artifact_test.py
  - tools/bazel/BUILD.bazel
  - BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - justfile
findings:
  critical: 2
  warning: 4
  info: 1
  total: 7
status: issues_found
---

# Phase 35: Code Review Report

**Reviewed:** 2026-07-25T22:26:42Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

The Phase 35 contract, generator, tests, Bazel targets, shell workflow, and `just` facade were reviewed against the repo-local guidance, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the Bright Builds architecture, code-shape, testing, and verification standards.

The 31 focused Python tests, bytecode compilation, contract check, wiring check, and existing-output security scan pass. Adversarial checks nevertheless confirmed that unvalidated snapshot content can escape the security scan, mutable Phase 33 registers can change the decision after Phase 34 validation, dangling audit links pass the production self-check, stale demotion approval can retain an open gate, and unsafe external refs are accepted. The current generated blocked route also covers only 43 of the 47 blocked Phase 34 ledger rows.

## Critical Issues

### CR-01: Secret-tainted source snapshots bypass every security scan

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:797-802`
**Issue:** The Phase 34 run manifest and contract are validated only for a small required subset, then copied verbatim at lines 1069-1076. `run_security_scan` explicitly skips every `contract-snapshots/` artifact at lines 1102-1104. Extra forbidden fields or text therefore enter the supposedly sanitized Phase 35 bundle undetected. An adversarial manifest containing `token_value` passed `validate_phase34_manifest`.
**Fix:**

```python
manifest = load_json(root, manifest_path)
scan_security(manifest, manifest_path.as_posix())
validate_exact_fields(manifest, PHASE34_MANIFEST_FIELDS)

phase34_contract = load_json(root, PHASE34_CONTRACT_PATH)
scan_security(phase34_contract, PHASE34_CONTRACT_PATH.as_posix())
validate_phase34_contract(phase34_contract)
```

Scan all emitted snapshots as well, using a snapshot-aware policy that permits contract vocabulary such as prohibited-field names but rejects secret-bearing values and uncontracted fields.

### CR-02: Mutable Phase 33 registers can change an already validated cutover decision

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:839-850`
**Issue:** Phase 35 follows register refs from the snapshotted Phase 33 handoff back to live `build/ci-evidence/phase33` files without a digest or exact projection binding them to the Phase 34 run. Those files can be regenerated or edited while retaining the static lifecycle ID. The verdict path then labels every approving exception `valid` and `exact_scope` at lines 984-991 instead of validating its lifecycle, timestamp, scope, and identity. Removing an exception after Phase 34 used it can turn an exception-bearing decision into clean `approved`; adding or altering one can produce `approved-with-exceptions` without Phase 34 ever validating that exact set.
**Fix:** Snapshot the exact Phase 33 registers consumed by Phase 34, or record and verify their canonical digests in the Phase 34 manifest. Derive the active exception set from the Phase 34 canonical ledger and require exact equality with fully revalidated Phase 33 exception rows. Never synthesize `validation_state` or `exact_scope`.

## Warnings

### WR-01: Production audit-link validation compares the index with itself

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:959-960`
**Issue:** Both production checks call `validate_audit_links(links, links)` (also lines 940-942), so missing, extra, dangling, lifecycle, category, and digest mismatches cannot be discovered independently. `derive_audit_links` also does not resolve local targets or fragments. A link to nonexistent `build/ci-evidence/phase34/does-not-exist.json` returned no validation reasons in an adversarial check.
**Fix:** Independently derive the expected semantic link set from validated source artifacts, separately construct the emitted index, resolve every local file/fragment, recompute digests from the resolved sanitized target, and compare the two sets.

### WR-02: Targeted repair scope omits Phase 34-created blockers

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:1001-1005`
**Issue:** Repair scope and `blocker_ids` are built only from the snapshotted Phase 32 register, while the loaded Phase 34 `readiness-blocker-summary.json` is never used. In the current quick artifacts, Phase 34 has 47 blocked ledger rows but Phase 35 emits only 43 repair scopes, omitting the four required-stream rows that produced `coverage-incomplete`.
**Fix:** Derive blockers from the Phase 34 blocker summary/canonical blocked ledger rows. Map every row to source-backed owner/action/criterion refs, and add `route-scope-incomplete` when any blocked row cannot be represented.

### WR-03: A stale or invalid demotion approval can retain an open gate

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:691-705`
**Issue:** The gate is blocked only when the projected validation/value disagrees with the dry-run fields. A stale approval paired with `approval_validation_state: invalid`, `approval_decision_state: approve`, and `gate_state: open` is emitted as stale/approve/open. This contradicts the fail-closed demotion boundary.
**Fix:** Require `validation_state == "valid"`, `decision_state == "approve"`, unblocked matching readiness, and no blocking gate reasons before preserving `open`; otherwise force `blocked` and add a source-artifact or approval reason.

### WR-04: External refs bypass traversal and separator validation

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:244-250`
**Issue:** `validate_ref` returns immediately for `external://`, `maintainer://`, and `owner://`. Values such as `external://phase31/../../private` are accepted even though the contract requires no parent traversal and safe refs.
**Fix:** Parse allowed URI schemes, require the exact permitted authority/path prefix, and reject dot segments, backslashes, control characters, and malformed fragments before returning.

## Info

### IN-01: The verifier has crossed the repository's module-size refactor trigger

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:1`
**Issue:** The 1,246-line file combines contract parsing, path and security policy, verdict logic, audit indexing, repair routing, demotion projection, rendering, output I/O, CLI parsing, and wiring inspection. This exceeds the Bright Builds roughly 628-line refactor trigger and makes boundary-validation omissions harder to see.
**Fix:** Split pure verdict/route/demotion reducers, source-schema validation, audit-link validation, and the filesystem/CLI shell into focused modules while retaining the current public entrypoint.

***

_Reviewed: 2026-07-25T22:26:42Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
