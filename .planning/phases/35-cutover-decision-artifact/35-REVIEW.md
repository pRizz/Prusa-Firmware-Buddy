---
phase: 35-cutover-decision-artifact
reviewed: 2026-07-25T23:07:36Z
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
  critical: 1
  warning: 0
  info: 1
  total: 2
status: issues_found
---

# Phase 35: Code Review Report

**Reviewed:** 2026-07-25T23:07:36Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

The persisted seven-file Phase 35 scope was re-reviewed after the iteration-2 fixes. The review applied the repo-local guidance, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the Bright Builds architecture, code-shape, testing, and verification standards.

The prior CR-02, WR-04, and WR-05 cases are resolved. Focused adversarial tests confirm that stale canonical exceptions cannot be upgraded by legacy `validation_state`/`active`/`exact_scope` fields, percent-encoded backslashes and controls are rejected, and a valid exception-covered readiness bundle remains `approved-with-exceptions` with a targeted follow-up scope.

One new critical containment issue was reproduced: validation rejects a symlinked Phase 34 root but does not inspect individual source artifacts, and the common JSON loader follows a nested artifact symlink outside the repository. The existing oversized-module maintainability item also remains open.

The 45 focused Python tests, bytecode compilation, contract check, wiring check, existing-output security scan, shell syntax check, scoped diff check, Bazel target query, Bazel test target, and full Bazel Phase 35 verification chain pass. Bazel upgraded `MODULE.bazel.lock` metadata during verification; that side effect was restored.

## Critical Issues

### CR-01: Nested source-artifact symlinks bypass the declared containment boundary

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:239-255`
**Issue:** `validate_paths` checks only the components of the Phase 34 root and Phase 35 output root at lines 414-436. `load_json` then calls `is_file()` and `read_text()` on every nested artifact without rejecting a symlink or verifying the resolved file remains under the repository root. A temporary Phase 34 directory containing `final-readiness-run-manifest.json` as a symlink to an outside JSON file passed `validate_paths`, and `load_json` read the outside sentinel value. The same loader is used for the manifest, packet, ledger, register, snapshot, and audit-link targets, so this violates the contract's `resolved-root-contained` and `no-symlink-escape` requirements and can move cutover authority inputs outside the contracted source roots.
**Fix:**

```python
def resolve_source_file(root: Path, relative_path: Path) -> Path:
    current = root
    for part in relative_path.parts:
        current /= part
        if current.is_symlink():
            raise VerificationError(
                f"source artifact contains a symlink escape: {relative_path}"
            )

    resolved_root = root.resolve(strict=True)
    resolved = (root / relative_path).resolve(strict=True)
    if resolved_root not in resolved.parents:
        raise VerificationError(
            f"source artifact escapes repository root: {relative_path}"
        )
    if not resolved.is_file():
        raise VerificationError(f"source artifact missing: {relative_path}")
    return resolved
```

Use this helper in `load_json` before reading and add a regression with a real Phase 34 directory plus a symlinked nested manifest or audit target that must raise `VerificationError`.

## Info

### IN-01: The verifier remains far beyond the repository's module-size refactor trigger

**File:** `tools/bazel/phase35_cutover_decision_artifact.py:1`
**Issue:** The 1,674-line generator combines contract parsing, security and URI policy, source validation, decision logic, audit resolution, repair routing, demotion projection, rendering, output mutation, and wiring inspection. This remains beyond the Bright Builds roughly 628-line refactor trigger; the 1,397-line test module mirrors the same concentration.
**Fix:** Split boundary validation, pure verdict/route/demotion reducers, audit-link resolution, and the filesystem/CLI shell into focused modules, with correspondingly focused tests.

***

_Reviewed: 2026-07-25T23:07:36Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
