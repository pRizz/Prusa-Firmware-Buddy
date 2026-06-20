---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T17:20:27Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - tools/bazel/phase18_cutover_review.py
  - tools/bazel/phase18_cutover_review_test.py
  - tools/bazel/manifests/phase18_cutover_review_contract.json
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

**Reviewed:** 2026-06-20T17:20:27Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the requested Phase 18 implementation surfaces at HEAD `98f09938c3ac258478c158cf2bd7050616ffa96c`: verifier, tests, contract manifest, Bazel wiring, workflow shell wrapper, and just recipe. Material guidance applied: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` (no active overrides), and Bright Builds core architecture, code-shape, verification, and testing standards.

Repo-native verification passed:

```text
just phase18-verify
Ran 45 tests in 9.974s
OK
Phase 18 wiring passed
Phase 18 quick artifacts written; demotion_allowed=false
```

The latest fixes cover the prior normalized-field and row-flag overclaim findings. The remaining actionable issues are in redaction of narrative secret markers, per-row decision policy enforcement, and generated-artifact contract trust boundaries.

## Critical Issues

### CR-01: Narrative Secret Markers Can Pass Redaction And Be Written To Artifacts

**File:** `tools/bazel/phase18_cutover_review.py:190`
**Issue:** `reject_forbidden_text` only catches private-key markers, payload phrases, overclaim phrases, and `password=`, `token=`, or `secret=` assignments. Decision inputs also accept free-text fields such as `rationale`, `residual_risk`, `blocker_or_deferred_action`, and `redaction_summary`; those fields are later copied into generated JSON artifacts. A decision input containing `Authorization: Bearer secret-test-token` in retained-review `residual_risk` passed `--quick`, set `demotion_allowed=true`, and wrote the value into `build/ci-evidence/phase18/retained-code-acceptance-summary.json`.
**Fix:**

```python
FORBIDDEN_TEXT_PATTERNS = (
    # existing patterns...
    ("authorization-header", re.compile(r"\bauthorization\s*:\s*bearer\b", re.IGNORECASE)),
    ("bearer-token", re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE)),
    ("password-assignment", re.compile(r"\bpassword\s*[:=]", re.IGNORECASE)),
    ("token-assignment", re.compile(r"\btoken\s*[:=]", re.IGNORECASE)),
    ("secret-assignment", re.compile(r"\bsecret\s*[:=]", re.IGNORECASE)),
)
```

Add a regression test that puts `Authorization: Bearer ...`, `token: ...`, and `password: ...` inside allowed narrative fields and asserts both `--quick --decision-input` and `--security-only --decision-input` reject them before generated artifacts can retain the values.

## Warnings

### WR-01: Decision Inputs Do Not Enforce Criterion-Level Allowed Statuses

**File:** `tools/bazel/phase18_cutover_review.py:805`
**Issue:** `validate_final_decision` receives only the set of criterion IDs, so it validates a decision status against the global `FINAL_CRITERION_STATUS_VOCABULARY` but never checks that status against the target criterion's own `allowed_statuses` or `exception_allowed` policy. A temp-contract probe that narrowed one criterion to `allowed_statuses: ["pending"]` still accepted a decision input marking that row `passed` and produced `demotion_allowed=true`. The committed contract currently gives every criterion the broad status set, but the verifier defines row-level policy fields and should enforce them to avoid future overclaims.
**Fix:** Pass a `criteria_by_id` map into `validate_final_decision`, then reject statuses not present in that criterion's `allowed_statuses`. Also reject `exception-approved` and `not-applicable` when `exception_allowed` is false, and keep `final_status_allows_demotion` tied to the validated row policy.

Add tests that narrow one criterion's `allowed_statuses`, submit a disallowed `passed` decision, and assert `--quick --decision-input` fails instead of allowing demotion.

### WR-02: Extra Generated Artifacts Are Accepted But Not Written Or Scanned

**File:** `tools/bazel/phase18_cutover_review.py:590`
**Issue:** `validate_generated_artifacts` only verifies that required artifact names are present and repo-relative. It does not reject unexpected entries, and the writer/scanner uses the hard-coded `REQUIRED_GENERATED_ARTIFACTS` set instead of the contract list. A contract with `generated_artifacts += ["unexpected-extra-output.json"]` passed `--contract-only`, but `--quick` neither wrote nor scanned that listed artifact. That lets the contract claim a generated artifact outside the actual Phase 18 output and redaction boundary.
**Fix:** Treat `generated_artifacts` as an exact contract, or make the writer/scanner consume the validated contract list:

```python
artifacts = require_list_of_strings(contract, "generated_artifacts", "contract")
extra = set(artifacts) - REQUIRED_GENERATED_ARTIFACTS
if extra:
    errors.append("unexpected generated artifacts: " + ", ".join(sorted(extra)))
```

Add a regression test that appends an extra artifact name and expects `--contract-only` to fail.

---

_Reviewed: 2026-06-20T17:20:27Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
