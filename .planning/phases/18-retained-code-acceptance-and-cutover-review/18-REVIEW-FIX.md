---
phase: 18-retained-code-acceptance-and-cutover-review
fixed_at: "2026-06-20T16:42:09Z"
review_path: .planning/phases/18-retained-code-acceptance-and-cutover-review/18-REVIEW.md
iteration: 6
findings_in_scope: 1
fixed: 1
skipped: 0
status: all_fixed
---

# Phase 18: Code Review Fix Report

**Fixed at:** 2026-06-20T16:42:09Z
**Source review:** .planning/phases/18-retained-code-acceptance-and-cutover-review/18-REVIEW.md
**Iteration:** 6

**Summary:**
- Findings in scope: 1
- Fixed: 1
- Skipped: 0

## Fixed Issues

### CR-01: Security-only accepts tampered demotion claims with any validated decision packet

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 7b725fe84
**Applied fix:** `--security-only --decision-input` now recomputes expected demotion from the supplied decision input and rejects generated `demotion_allowed: true` artifacts unless the input contains complete approving decisions. Added a regression test for a tampered no-decision artifact paired with an otherwise valid but empty decision packet.

### CR-01: Generated decision-input flag is trusted as proof of maintainer input

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 64515085a
**Applied fix:** Security scanning now tracks whether a `--decision-input` file was actually loaded and validated before trusting generated `decision_inputs_supplied: true` artifacts. Quick-mode scans carry through the already-validated decision-input state. Added a regression test proving a no-decision artifact cannot self-attest decision input and `demotion_allowed: true`.

### WR-01: Normalized final results can overclaim demotion in no-decision artifacts

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 64515085a
**Applied fix:** Generated overclaim validation now rejects top-level `normalized-final-demotion-results.json` `demotion_allowed: true` in no-decision artifacts. Added a regression test for that tamper path.

### WR-01: No-decision overclaim guard can be bypassed with a non-boolean manifest flag

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 39c351cdb
**Applied fix:** Generated overclaim validation now rejects missing or non-boolean `decision_inputs_supplied` before skipping no-decision checks. Added a regression test for string and missing generated flags combined with `demotion_allowed: true`.

### CR-01: Retained packet approvals do not enforce the contract approver role

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 7e9d00a46
**Applied fix:** Retained review validation now compares each review's `approver_role` with the packet's contract-required `approver_role`. Added a regression test proving a retained packet review with the wrong role is rejected.

### WR-01: Custom output directories produce misleading artifact paths and skip the matching scan target

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 7e9d00a46
**Applied fix:** Quick-mode manifests now use the actual selected output directory for `output_root`, `source_contract_snapshot_path`, and `generated_artifacts`. Security scanning and generated overclaim guards now scan the same selected output directory, including custom `--output-dir` paths. Added a regression test proving a custom-output overclaim is caught by `--security-only --output-dir`.

### WR-02: Final decision IDs are not type-checked or de-duplicated

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 7e9d00a46
**Applied fix:** Final decision validation now requires `decision_id` to be a non-empty string and rejects duplicate decision IDs across final criterion decisions. Added regression tests for non-string and duplicate decision IDs.

### Prior WR-01: Deferred retained-code exceptions can pass without evidence

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** d8778a906
**Applied fix:** Retained review validation now requires non-empty `supplied_evidence_result_refs` for both `accepted` and `deferred-approved-exception` statuses, while preserving the existing requirement that deferred approved exceptions include non-`none` exception and blocker/action fields. Added a regression test proving a deferred approved exception with empty supplied evidence is rejected.

### Prior WR-02: Exception metadata fields are not type-checked

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase18_cutover_review.py`, `tools/bazel/phase18_cutover_review_test.py`
**Commit:** 4d2af3bce
**Applied fix:** Exception metadata validation now type-checks every required non-`evidence_refs` exception field as a non-empty string. `evidence_refs` remains a non-empty list of Phase 18 artifact references. Added a regression test proving an `exception-approved` final decision with a non-string exception metadata field is rejected.

## Verification

- `python3 tools/bazel/phase18_cutover_review_test.py` passed: 40 tests.
- `python3 tools/bazel/phase18_cutover_review.py --contract-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --quick` passed.
- `python3 tools/bazel/phase18_cutover_review.py --security-only` passed.
- `python3 tools/bazel/phase18_cutover_review.py --wiring-only` passed.

---

_Fixed: 2026-06-20T16:42:09Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 6_
