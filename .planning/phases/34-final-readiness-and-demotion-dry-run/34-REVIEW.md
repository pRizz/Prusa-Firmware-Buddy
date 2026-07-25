---
phase: 34-final-readiness-and-demotion-dry-run
reviewed: 2026-07-25T19:21:47Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json
  - tools/bazel/phase34_final_readiness_demotion_dry_run.py
  - tools/bazel/phase34_final_readiness_demotion_dry_run_test.py
  - tools/bazel/BUILD.bazel
  - BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - justfile
findings:
  critical: 2
  warning: 2
  info: 1
  total: 5
status: issues_found
---

# Phase 34: Code Review Report

**Reviewed:** 2026-07-25T19:21:47Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

The Phase 34 contract, verifier, tests, Bazel targets, shell workflow, and `just` facade were reviewed against the Phase 31-33 producer contracts and the repository's Bright Builds architecture, code-shape, verification, and testing standards. The baseline suite passes (`20` tests), as do Python compilation, contract validation, and wiring validation.

The pure demotion truth table is correct, but the I/O boundary can label an uncorroborated Phase 33 projection as valid approval and open the gate. Nested Phase 33 register paths can also escape through symlinks. Separate gaps prevent durable blocked output for missing/malformed approval files and omit the contract's exact/dangling overlay checks.

## Critical Issues

### CR-01: Uncorroborated Phase 33 projections can open the demotion gate

**File:** `/Users/peterryszkiewicz/Repos/Prusa-Firmware-Buddy/tools/bazel/phase34_final_readiness_demotion_dry_run.py:645-681`
**Issue:** `load_phase33` only checks that normalized rows are objects, while `approval_state` trusts the separate demotion handoff when it contains a current lifecycle, an approved state, and four nonblank strings. It does not require `decision_id` to identify a unique normalized `reference_demotion=approve` decision, compare identity/role/timestamp/source refs with that record, validate the timestamp, or verify the readiness projection against a normalized readiness decision. An isolated fixture with no normalized decisions, a nonexistent decision ID, and `decision_timestamp: "not-even-a-timestamp"` returned exit code `0` with `gate_state: open`. This bypasses the explicit-approval boundary even though the three-input truth table itself is correct.
**Fix:**
```python
def validate_handoff_decision(
    projection: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
    expected_type: str,
    expected_value: str,
) -> dict[str, Any]:
    decision_id = require_string(projection.get("decision_id"), "decision_id")
    decision = decisions_by_id.get(decision_id)
    if decision is None:
        raise VerificationError(f"unknown Phase 33 decision_id: {decision_id}")
    if decision.get("decision_type") != expected_type or decision.get("decision_value") != expected_value:
        raise VerificationError(f"{decision_id} does not authorize {expected_type}={expected_value}")
    for field in ("maintainer_identity_ref", "maintainer_role", "decision_timestamp", "source_row_refs"):
        if projection.get(field) != decision.get(field):
            raise VerificationError(f"{decision_id} projection mismatch for {field}")
    require_iso_utc(str(decision["decision_timestamp"]), f"{decision_id}.decision_timestamp")
    return decision
```

Build a duplicate-rejecting decision map, validate every normalized record against the Phase 33 schema/enums, and derive both readiness and demotion validation from matched normalized decisions rather than trusting projection fields independently. Add an end-to-end open fixture plus negative tests for missing IDs, duplicate IDs, wrong axes/values, mismatched metadata/refs, and malformed timestamps.

### CR-02: Nested register inputs can escape their allowed roots through symlinks

**File:** `/Users/peterryszkiewicz/Repos/Prusa-Firmware-Buddy/tools/bazel/phase34_final_readiness_demotion_dry_run.py:645-660`
**Issue:** The top-level Phase 33 handoff and Phase 31 receipt paths call `resolved_under`, but `load_register` performs only lexical `path_under` validation before `load_json`, and the fixed Phase 32 register is loaded without a resolved containment check. A symlink at `build/ci-evidence/phase33/demotion-decision-handoff.json` pointing outside the allowed root was followed successfully and the verifier returned `0`. This violates the contract's exact-root/symlink policy and permits arbitrary out-of-root JSON to enter trusted evaluation and snapshots.
**Fix:**
```python
register_path = path_under(value, PHASE33_OUTPUT_ROOT, f"register_refs.{name}")
resolved_under(root, register_path, PHASE33_OUTPUT_ROOT, f"register_refs.{name}")
payload = load_json(root, register_path)

phase32_path = Path(PHASE32_REGISTER_REF)
resolved_under(root, phase32_path, PHASE32_OUTPUT_ROOT, "Phase 32 blocker register")
blocker_register = load_json(root, phase32_path)
```

Apply resolved containment to every file opened or copied, not only CLI roots, and add separate symlink tests for each Phase 33 register and the Phase 32 register.

## Warnings

### WR-01: Missing or malformed approval files leave no durable blocked artifact

**File:** `/Users/peterryszkiewicz/Repos/Prusa-Firmware-Buddy/tools/bazel/phase34_final_readiness_demotion_dry_run.py:645-656`
**Issue:** Missing files, invalid JSON, non-object JSON, forbidden content, or unsafe refs in the demotion handoff raise during `load_register`, before `approval_state`, `evaluate_demotion`, or `write_bundle` run. Removing `demotion-decision-handoff.json` produced exit code `1` and no `demotion-dry-run.json`. The current durability test covers malformed in-memory fields only, not malformed or absent approval artifacts, so it does not enforce D-07's retained blocked result.
**Fix:** Separate approval loading from the rest of the validated evidence load. Convert approval-load/validation failures into `approval_validation_state: invalid` (or `missing` for an absent file), write a minimal deterministic blocked dry-run result and run manifest, then return the original nonzero validation error. Add subprocess tests for a missing file, invalid JSON, non-object JSON, unsafe ref, forbidden field/text, and symlink rejection, asserting both nonzero exit and a retained blocked artifact.

### WR-02: Sparse overlay matching ignores affected-gate and dangling references

**File:** `/Users/peterryszkiewicz/Repos/Prusa-Firmware-Buddy/tools/bazel/phase34_final_readiness_demotion_dry_run.py:544-559`
**Issue:** `evaluate_coverage` indexes Phase 32 rows only by `source_ref`, selects the first match, and emits ledger entries only for Phase 31 expected rows. It never performs the contract's `(source_ref, affected_gate)` exact join, and unmatched Phase 32 rows or Phase 33 decision refs are silently discarded. The declared `dangling-row-ref` reason code is unused. Consequently, a blocker or decision that cannot be joined to the expected lineage can disappear instead of blocking readiness.
**Fix:** Validate unique Phase 32 row IDs and Phase 33 decision IDs first, build explicit join keys containing both source ref and affected gate, and perform bidirectional anti-joins. Emit deterministic blocked ledger entries (or a top-level blocking validation result) for every unmatched/ambiguous blocker and decision ref with `dangling-row-ref` or `duplicate-row`. Add focused tests for wrong stream, wrong gate, extra blocker rows, nonexistent decision refs, duplicate blocker IDs, and duplicate decision IDs.

## Info

### IN-01: The verifier mixes several modules' responsibilities in one oversized file

**File:** `/Users/peterryszkiewicz/Repos/Prusa-Firmware-Buddy/tools/bazel/phase34_final_readiness_demotion_dry_run.py:1-1032`
**Issue:** At 1,032 lines, the verifier exceeds the repository's roughly 628-line refactor trigger and combines contract/schema validation, path and secret policy, pure coverage/authorization evaluation, Phase 31/33 adapters, artifact projection, security scanning, wiring parsing, and CLI dispatch. Individual functions are reasonably bounded, but the file-level cohesion makes boundary validation gaps harder to see and test.
**Fix:** Split stable responsibilities into modules such as `phase34_contract.py`, `phase34_inputs.py`, `phase34_evaluator.py`, and `phase34_artifacts.py`, leaving the existing script as a thin CLI. Keep pure evaluator tests separate from filesystem/security boundary tests.

***

_Reviewed: 2026-07-25T19:21:47Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
