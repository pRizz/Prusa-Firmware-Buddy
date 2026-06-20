---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T16:45:51Z
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

**Reviewed:** 2026-06-20T16:45:51Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Re-reviewed the listed Phase 18 verifier, contract manifest, tests, Bazel wiring, shell workflow, and just recipe at standard depth after fix `7b725fe84`. This review used `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and Bright Builds architecture, code-shape, verification, and testing standards. No project-local skills were present under `.claude/skills/` or `.agents/skills/`.

Fix `7b725fe84` closes the empty-decision-input demotion overclaim reported in the prior review. One security-only regression remains: the scan recomputes expected demotion from final criterion decisions but does not re-apply the retained-packet acceptance coupling that `--quick` enforces before writing artifacts.

Verification performed:

- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 40 tests.
- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.
- Targeted isolated repro: after a no-decision quick run, changing generated `run-manifest.json` and `normalized-final-demotion-results.json` to `demotion_allowed: true`, then supplying a decision input where all final criteria are `passed` but every retained packet review is `blocked`, still makes `--security-only --decision-input decision-input.json` pass.

## Critical Issues

### CR-01: Security-only demotion check ignores retained-packet review status

**File:** `tools/bazel/phase18_cutover_review.py:1263`
**Issue:** `run_security_scan` discards `retained_reviews` when validating supplied decision input and computes `expected_demotion_allowed` only from final criterion decisions. That misses the consistency rule in `write_quick_artifacts`: `final-retained-code-acceptance` cannot pass unless every retained-code packet review is `accepted` or `deferred-approved-exception`. A tampered generated artifact can therefore claim `demotion_allowed: true` when the decision input marks all final criteria as `passed` but leaves retained packets `blocked` or `rejected`.
**Fix:**
```python
def validate_retained_acceptance_consistency(
    packets: list[dict[str, Any]],
    retained_reviews: dict[str, dict[str, Any]],
    final_decisions: dict[str, dict[str, Any]],
) -> None:
    retained_acceptance_decision = final_decisions.get("final-retained-code-acceptance")
    if not retained_acceptance_decision or not final_status_allows_demotion(
        str(retained_acceptance_decision["status"]),
        retained_acceptance_decision,
    ):
        return

    packet_ids = {str(packet["id"]) for packet in packets}
    missing_reviews = packet_ids - set(retained_reviews)
    bad_statuses = [
        f"{packet_id}:{review['status']}"
        for packet_id, review in sorted(retained_reviews.items())
        if review["status"] not in {"accepted", "deferred-approved-exception"}
    ]
    if missing_reviews or bad_statuses:
        raise VerificationError(
            "final-retained-code-acceptance cannot pass without accepted retained reviews"
        )
```
Call this helper from both `write_quick_artifacts` and `run_security_scan` immediately after `validated_decision_maps(...)`. Add a regression test where final criteria all pass but retained reviews are `blocked`, and assert `--security-only --decision-input` rejects generated `demotion_allowed: true`.

---

_Reviewed: 2026-06-20T16:45:51Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
