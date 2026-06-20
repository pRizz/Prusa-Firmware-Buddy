---
phase: 18-retained-code-acceptance-and-cutover-review
reviewed: 2026-06-20T17:30:03Z
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
  warning: 0
  info: 0
  total: 1
status: issues_found
---

# Phase 18: Code Review Report

**Reviewed:** 2026-06-20T17:30:03Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the requested Phase 18 implementation surfaces at HEAD `e46bfe548adb49b4729a8c7cbdf9ec82a7a65f03`: verifier, tests, contract manifest, Bazel wiring, workflow shell wrapper, and just recipe. Material guidance applied: `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` (no active overrides), and Bright Builds core code-shape, verification, and testing standards.

Repo-native verification passed:

```text
just phase18-verify
Ran 49 tests in 10.035s
OK
Phase 18 wiring passed
Phase 18 quick artifacts written; demotion_allowed=false
```

The prior findings for criterion-level policy enforcement, generated artifact exactness, custom output directory scanning, generated row demotion flags, and retained-code acceptance overclaim checks are addressed. One actionable redaction gap remains in narrative secret marker handling.

## Critical Issues

### CR-01: API-Key Narrative Markers Pass Redaction And Are Written To Artifacts

**File:** `tools/bazel/phase18_cutover_review.py:196`
**Issue:** `FORBIDDEN_TEXT_PATTERNS` now rejects bearer headers and `password:`, `token:`, or `secret:` narrative assignments, but it still does not reject API-key style assignments such as `api_key: ...`, `api-key: ...`, `api key: ...`, or `access_token: ...`. Decision input values in narrative fields are copied into generated artifacts; an adversarial probe with `retained_code_reviews[0].residual_risk = "api_key: sk_test_redacted_value_123456"` passed `--quick --decision-input`, set `demotion_allowed=true`, and wrote the marker into `build/ci-evidence/phase18/retained-code-acceptance-summary.json`.
**Fix:**
```python
FORBIDDEN_TEXT_PATTERNS = (
    # existing patterns...
    ("api-key-assignment", re.compile(r"\bapi[\s_-]?key\s*[:=]", re.IGNORECASE)),
    ("access-token-assignment", re.compile(r"\baccess[\s_-]?token\s*[:=]", re.IGNORECASE)),
    ("credential-assignment", re.compile(r"\bcredential(?:[\s_-]?value)?\s*[:=]", re.IGNORECASE)),
    ("wifi-password-assignment", re.compile(r"\bwifi[\s_-]?password\s*[:=]", re.IGNORECASE)),
)
```

Extend `test_decision_input_rejects_narrative_secret_markers` in `tools/bazel/phase18_cutover_review_test.py:875` to cover API-key and access-token narrative assignments for both `--quick --decision-input` and `--security-only --decision-input`, and assert no generated retained summary is written.

---

_Reviewed: 2026-06-20T17:30:03Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
