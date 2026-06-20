---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T16:32:00Z
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
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-06-20T16:32:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Re-reviewed the listed Phase 18 verifier, contract manifest, tests, Bazel wiring, shell workflow, and just recipe at standard depth after fix `39c351cdb`. This review used `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and Bright Builds architecture, code-shape, verification, and testing standards. No project-local skills were present under `.claude/skills/` or `.agents/skills/`.

Fix `39c351cdb` correctly rejects non-boolean generated `decision_inputs_supplied` values, and the scoped verifier tests pass. Two generated-artifact overclaim gaps remain in the same guard area.

Verification performed:

- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 37 tests.
- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.
- Targeted tamper check reproduced CR-01: after a no-decision quick run, changing `run-manifest.json` to `decision_inputs_supplied: true` and `demotion_allowed: true` still made `--security-only` pass.
- Targeted tamper check reproduced WR-01: after a no-decision quick run, changing `normalized-final-demotion-results.json` to `demotion_allowed: true` still made `--security-only` pass.

## Critical Issues

### CR-01: Generated decision-input flag is trusted as proof of maintainer input

**File:** `tools/bazel/phase18_cutover_review.py:1279`
**Issue:** `validate_generated_overclaim_guards` returns as soon as the generated `run-manifest.json` says `decision_inputs_supplied` is boolean `True`. The security scan does not require a validated `--decision-input` for that branch, so a no-decision artifact can be tampered from `false` to `true`, set `demotion_allowed: true`, and pass `--security-only`. That bypasses the Phase 18 rule that reference demotion needs explicit maintainer decision input rather than local generated proof.
**Fix:**
```python
def run_security_scan(
    root: Path,
    maybe_decision_input_path: str | None,
    output_dir: Path | None = None,
) -> None:
    decision_input_validated = False
    if maybe_decision_input_path:
        load_decision_input(root, maybe_decision_input_path)
        decision_input_validated = True
    ...
    validate_generated_overclaim_guards(root, errors, output_dir, decision_input_validated)

def validate_generated_overclaim_guards(
    root: Path,
    errors: list[str],
    output_dir: Path | None = None,
    decision_input_validated: bool = False,
) -> None:
    ...
    if decision_inputs_supplied and not decision_input_validated:
        errors.append("generated run-manifest.json claims decision input without validated --decision-input")
        return
    if decision_inputs_supplied:
        return
```
Add a regression test that runs `--quick` without decision input, flips `decision_inputs_supplied` to `True` with `demotion_allowed: true`, and expects `--security-only` to fail unless a matching decision input was supplied and validated.

## Warnings

### WR-01: Normalized final results can overclaim demotion in no-decision artifacts

**File:** `tools/bazel/phase18_cutover_review.py:1283`
**Issue:** The no-decision guard checks `run-manifest.json` for `demotion_allowed: true` and checks individual normalized row statuses, but it does not check the top-level `demotion_allowed` field in `normalized-final-demotion-results.json`. A generated artifact can therefore claim `{"demotion_allowed": true}` in that machine-readable file while every row remains pending and the security scan still passes.
**Fix:**
```python
normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
if isinstance(normalized, dict) and normalized.get("demotion_allowed") is True:
    errors.append(
        "generated no-decision normalized-final-demotion-results.json cannot set demotion_allowed true"
    )
results = normalized.get("results") if isinstance(normalized, dict) else None
```
Add a regression test that mutates only `normalized-final-demotion-results.json["demotion_allowed"]` after a no-decision quick run and expects `--security-only` to fail.

---

_Reviewed: 2026-06-20T16:32:00Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
