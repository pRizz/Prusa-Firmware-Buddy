---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T16:15:33Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - tools/bazel/manifests/phase18_cutover_review_contract.json
  - tools/bazel/phase18_cutover_review.py
  - tools/bazel/phase18_cutover_review_test.py
  - tools/bazel/BUILD.bazel
  - BUILD.bazel
  - tools/bazel/rust_workflow.sh
  - justfile
findings:
  critical: 1
  warning: 2
  info: 0
  total: 3
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-06-20T16:15:33Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the listed Phase 18 verifier, contract manifest, tests, Bazel wiring, shell workflow, and just recipe at standard depth. This review used the repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and Bright Builds architecture, code-shape, verification, and testing standards. No project-local skills were present under `.claude/skills/` or `.agents/skills/`.

The existing happy path passes, but the verifier can still accept malformed decision input that undermines the retained-code approval gate and traceability. Targeted temp-root probes reproduced the findings below.

Verification performed:

- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.
- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 32 tests.
- Targeted temp-root probes reproduced CR-01, WR-01, and WR-02.

## Critical Issues

### CR-01: Retained packet approvals do not enforce the contract approver role

**File:** `tools/bazel/phase18_cutover_review.py:838`
**Issue:** `validate_retained_review` only checks that `approver_role` is a non-empty string. It receives only `packet_ids`, so it cannot compare the review role with the packet's required `approver_role` from the contract. A decision input can mark every retained packet `accepted` with `approver_role: "wrong-role"` and still generate `demotion_allowed=true` when the final criteria pass. That bypasses the Phase 18 retained-code maintainer-role gate.
**Fix:**
```python
def validate_retained_review(row: Any, packets_by_id: dict[str, dict[str, Any]], row_index: int) -> dict[str, Any]:
    ...
    packet = packets_by_id.get(packet_id)
    if packet is None:
        raise VerificationError(f"{row_name} packet_id does not resolve: {packet_id}")
    approver_role = require_string(row, "approver_role", row_name)
    expected_role = require_string(packet, "approver_role", packet_id)
    if approver_role != expected_role:
        raise VerificationError(f"{row_name} approver_role must be {expected_role}")
```
Update `validated_decision_maps` to pass a `packets_by_id` map, and add a regression test where one retained review uses the wrong role while all final criteria otherwise pass; the verifier should reject it and never write `demotion_allowed=true`.

## Warnings

### WR-01: Custom output directories produce misleading artifact paths and skip the matching scan target

**File:** `tools/bazel/phase18_cutover_review.py:1191`
**Issue:** `write_quick_artifacts` accepts `--output-dir`, but `run_manifest["source_contract_snapshot_path"]`, `run_manifest["generated_artifacts"]`, `generated_artifacts_to_scan`, and `validate_generated_overclaim_guards` still use `DEFAULT_OUTPUT_DIR`. A run with `--output-dir build/ci-evidence/phase18/custom` writes `custom/run-manifest.json` while the manifest points at `build/ci-evidence/phase18/...`, and the post-write scan targets the default directory instead of the actual output directory.
**Fix:**
```python
output_dir_relative = output_dir.relative_to(root)
run_manifest["source_contract_snapshot_path"] = (output_dir_relative / snapshot_relative).as_posix()
run_manifest["generated_artifacts"] = [
    (output_dir_relative / artifact).as_posix() for artifact in sorted(REQUIRED_GENERATED_ARTIFACTS)
]
run_security_scan(root, None, output_dir)
```
Thread `output_dir` through `generated_artifacts_to_scan` and `validate_generated_overclaim_guards`, or remove `--output-dir` if Phase 18 artifacts must always be written to the default root.

### WR-02: Final decision IDs are not type-checked or de-duplicated

**File:** `tools/bazel/phase18_cutover_review.py:794`
**Issue:** `decision_id` is listed in the required final-decision schema, but validation only checks that the field exists. Non-string and duplicate `decision_id` values still pass, and a temp-root probe with `decision_id: 123` on every final criterion generated `demotion_allowed=true`. That weakens maintainer decision traceability for the final demotion gate.
**Fix:**
```python
decision_id = require_string(row, "decision_id", row_name)
```
Track seen decision IDs in `validated_decision_maps` and reject duplicates across `final_criterion_decisions`. Add regression tests for non-string and duplicate decision IDs.

---

_Reviewed: 2026-06-20T16:15:33Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
