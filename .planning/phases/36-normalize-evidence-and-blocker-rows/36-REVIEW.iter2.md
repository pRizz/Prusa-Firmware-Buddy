---
phase: 36-normalize-evidence-and-blocker-rows
reviewed: 2026-07-26T01:51:38Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - tools/bazel/BUILD.bazel
  - tools/bazel/manifests/phase32_blocker_register_triage_contract.json
  - tools/bazel/phase32_blocker_normalization.py
  - tools/bazel/phase32_blocker_normalization_test.py
  - tools/bazel/phase32_blocker_register_triage.py
  - tools/bazel/phase32_blocker_register_triage_test.py
  - tools/bazel/rust_workflow.sh
findings:
  critical: 2
  warning: 2
  info: 0
  total: 4
status: issues_found
---

# Phase 36: Code Review Report

**Reviewed:** 2026-07-26T01:51:38Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

The seven scoped Phase 36 files were reviewed for correctness, security, regressions, and maintainability. The pure identity core and producer-backed tests are generally clear, and the focused suites pass, but the Phase 32 input boundary still permits a release/signing provenance bypass and silently drops unsupported demotion states. Two additional paths contradict the contract's requirement that malformed and unknown shapes remain critical.

Repository guidance materially applied from `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and the architecture, code-shape, testing, and verification standards. In particular, the review treated producer JSON as boundary data, required fail-closed handling, and checked the Phase 36 threat model's provenance and authorization boundaries.

Verification performed:

- `python3 tools/bazel/phase32_blocker_normalization_test.py -q` — 17 tests passed.
- `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` — 18 tests passed.
- `python3 tools/bazel/phase32_blocker_register_triage.py --contract-only` — passed.
- `bash -n tools/bazel/rust_workflow.sh` — passed.
- `git diff --check 0cff91321..HEAD` — passed.
- Targeted negative probes reproduced all four findings.

## Critical Issues

### CR-01: Release adapter trusts any matching basename instead of the contracted Phase 26 artifact

**File:** `tools/bazel/phase32_blocker_register_triage.py:831-832`

**Issue:** The release/signing adapter selects a consumed artifact when its basename is `upstream-result-row-table.json`, but it never requires the exact contract path `build/ci-evidence/phase26/upstream-result-row-table.json` or binds the currently loaded table to the accepted Phase 31 receipt. A modified receipt can point at `arbitrary/attacker/upstream-result-row-table.json`; when that table contains all-passed rows, Phase 32 exits successfully and emits zero release blockers. This bypasses the contract-keyed provenance boundary and can turn an unvalidated table into proof-eligible absence of blockers.

**Fix:**

```python
phase32_contract = load_contract(root)
adapter = require_dict(
    require_dict(phase32_contract["producer_adapters"], "producer_adapters").get(
        "phase26_release_signing_table"
    ),
    "producer_adapters.phase26_release_signing_table",
)
expected_table_path = Path(
    require_string(
        adapter.get("expected_artifact_path"),
        "producer_adapters.phase26_release_signing_table.expected_artifact_path",
    )
)
if consumed_path != expected_table_path:
    rows.append(build_unknown_release_artifact_blocker(...))
    continue
```

Also validate the accepted receipt's required provenance fields and add a regression that rewrites `consumed_upstream_row_refs` to a same-basename path and expects one critical `unknown_unclassified` blocker.

### CR-02: Unsupported demotion authorization values disappear from the blocker register

**File:** `tools/bazel/phase32_blocker_register_triage.py:1107-1138, 1254-1287`

**Issue:** Phase 27 and Phase 28 demotion records emit a blocker only when their authorization equals `"blocked"`. Any unsupported value is silently ignored; a targeted probe using `"unexpected-new-state"` for both producer artifacts completed successfully and neither artifact appeared in the canonical register. This violates the explicit fail-closed rule for unknown statuses and removes the very demotion decision identity later phases need to reconcile.

**Fix:**

```python
authorization = demotion.get("reference_demotion_authorization")
if authorization == "approved":
    pass
elif authorization == "blocked":
    rows.append(build_blocked_demotion_row(...))
else:
    rows.append(
        build_blocker_row(
            ...,
            signal={
                "adapter_problem_kind": "unknown_unclassified",
                "failure_reason": (
                    "unsupported Phase 28 demotion authorization: "
                    f"{authorization}"
                ),
            },
        )
    )
```

Apply the same explicit status dispatch to the Phase 27 handoff, where `"blocked"` is the only contracted value, and add one-concern regressions for both artifacts.

## Warnings

### WR-01: Malformed Phase 26 tables are classified as high instead of critical

**File:** `tools/bazel/manifests/phase32_blocker_register_triage_contract.json:257-262`

**Issue:** `fail_closed_shape_policy.recognized_invalid_shape` declares malformed input critical, and the Phase 36 plan requires one critical malformed blocker, but `policy_map.malformed.severity` is `"high"`. `classify_signal()` reads `policy_map`, so the runtime result is high severity. The contract validator does not cross-check these two declarations, allowing `--contract-only` and all tests to pass with the contradiction.

**Fix:** Change `policy_map.malformed.severity` to `"critical"`, validate that both fail-closed policy entries exactly match their corresponding policy-map severity and proof eligibility, and extend the malformed integration assertion to check critical severity.

### WR-02: Unconditional policy overrides downgrade unknown Phase 27/28 inputs

**File:** `tools/bazel/phase32_blocker_register_triage.py:1035-1046, 1189-1200`

**Issue:** The Phase 27 residual adapter correctly sets `adapter_problem_kind="unknown_unclassified"` for an unsupported `row_type`, but its unconditional override changes severity from critical to medium. A targeted probe produced an `unknown_unclassified` row with medium severity. The Phase 28 blocker adapter similarly forces every unknown status to high. Both contradict the contract's critical fail-closed policy and can under-prioritize schema drift or tampering.

**Fix:** Apply the domain-specific override only after the row kind/status has been validated as supported. For unknown inputs, preserve the classification returned by `blocker_policy_for("unknown_unclassified", ...)`. Add regressions that assert critical severity for an unsupported Phase 27 residual `row_type` and an unsupported Phase 28 readiness status.

______________________________________________________________________

_Reviewed: 2026-07-26T01:51:38Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
