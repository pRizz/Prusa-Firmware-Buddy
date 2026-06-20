---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T16:39:01Z
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
  warning: 0
  info: 0
  total: 1
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-06-20T16:39:01Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Re-reviewed the listed Phase 18 verifier, contract manifest, tests, Bazel wiring, shell workflow, and just recipe at standard depth after fix `64515085a`. This review used `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and Bright Builds architecture, code-shape, verification, and testing standards. No project-local skills were present under `.claude/skills/` or `.agents/skills/`.

Fix `64515085a` closes the previous no-decision artifact gaps for a missing decision input and for top-level normalized demotion overclaims. One decision-input binding gap remains in `--security-only`: a syntactically valid but empty decision packet can still bless tampered generated demotion claims because the security scan does not compare generated artifacts to the supplied decision input.

Verification performed:

- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 39 tests.
- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.
- Targeted isolated repro: after a no-decision quick run, changing `run-manifest.json` to `decision_inputs_supplied: true` and `demotion_allowed: true`, then supplying a minimal decision packet with empty review/decision lists, still makes `--security-only --decision-input decision-input.json` pass.

## Critical Issues

### CR-01: Security-only accepts tampered demotion claims with any validated decision packet

**File:** `tools/bazel/phase18_cutover_review.py:1290`
**Issue:** `run_security_scan` treats `load_decision_input(...)` success as enough proof that generated artifacts with `decision_inputs_supplied: true` are legitimate. But `load_decision_input` accepts a packet containing only the correct `decision_packet` phase/lifecycle plus empty `retained_code_reviews` and `final_criterion_decisions`, and `validate_generated_overclaim_guards` returns immediately when `decision_inputs_supplied` is true. As a result, a no-decision quick artifact can be manually changed to `decision_inputs_supplied: true` and `demotion_allowed: true`; `--security-only --decision-input` then reports success without proving the generated files were produced from that input or contain complete approving decisions. That keeps the Phase 18 reference-demotion gate bypassable in post-generation security checks.
**Fix:**
```python
def run_security_scan(
    root: Path,
    maybe_decision_input_path: str | None,
    contract: dict[str, Any],
    output_dir: Path | None = None,
) -> None:
    decision_input = load_decision_input(root, maybe_decision_input_path)
    packets = contract_packets(contract)
    criteria = contract_final_criteria(contract)
    retained_reviews, final_decisions = validated_decision_maps(decision_input, packets, criteria)
    expected_final_results = normalize_final_results(criteria, final_decisions)
    expected_retained_rows = normalize_retained_reviews(packets, retained_reviews)
    expected_allowed = demotion_allowed(decision_input is not None, expected_final_results)
    validate_generated_overclaim_guards(
        root,
        errors,
        output_dir,
        expected_final_results,
        expected_retained_rows,
        expected_allowed,
    )
```
Then remove the early return for `decision_inputs_supplied`, compare `run-manifest.json`, `normalized-final-demotion-results.json`, and `retained-code-acceptance-summary.json` against the recomputed values, and fail if generated `demotion_allowed` is true while the supplied decisions do not fully support it. Add a regression test using a minimal empty decision packet against tampered no-decision artifacts.

---

_Reviewed: 2026-06-20T16:39:01Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
