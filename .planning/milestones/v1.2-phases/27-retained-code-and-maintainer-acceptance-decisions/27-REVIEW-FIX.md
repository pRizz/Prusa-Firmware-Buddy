---
phase: 27-retained-code-and-maintainer-acceptance-decisions
fixed_at: 2026-06-25T02:46:00Z
review_path: .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 27: Code Review Fix Report

**Fixed at:** 2026-06-25T02:46:00Z
**Source review:** .planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5
- Fixed: 5
- Skipped: 0

## Fixed Issues

### WR-01: Phase 26 Row Identity Is Not Revalidated Against Phase 18

**Files modified:** `tools/bazel/phase27_retained_code_acceptance_decisions.py`, `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
**Commit:** f27cb10db
**Applied fix:** Revalidated Phase 26 upstream row `evidence_family`, `owning_phase`, and `source_lifecycle_id` against the canonical Phase 18 upstream requirement, with a regression for stale lifecycle IDs.

### WR-02: Maintainer Input Phase Metadata Is Ignored

**Files modified:** `tools/bazel/phase27_retained_code_acceptance_decisions.py`, `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
**Commit:** a3e7597c2
**Applied fix:** Validated maintainer input schema version, phase, lifecycle ID, and blocked reference-demotion metadata, with a stale lifecycle regression.

### WR-03: Final Decision Status And Decision Can Contradict Each Other

**Files modified:** `tools/bazel/phase27_retained_code_acceptance_decisions.py`, `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
**Commit:** 116feb51d
**Applied fix:** Added final readiness decision/status compatibility validation before normalization, with regressions for `reject` + `passed` and `approve` + `failed`.

### WR-04: Accepted Decisions Can Omit Evidence Refs And Use Invalid Timestamps

**Files modified:** `tools/bazel/phase27_retained_code_acceptance_decisions.py`, `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
**Commit:** dcfd257f1
**Applied fix:** Required ISO UTC decision timestamps and non-empty evidence refs for accepted retained decisions, passed final decisions, and approved exceptions, with regressions for each path.

### WR-05: Retained Packet Approver Roles Are Not Enforced

**Files modified:** `tools/bazel/phase27_retained_code_acceptance_decisions.py`, `tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
**Commit:** 763b78588
**Applied fix:** Enforced each retained packet's Phase 18 `approver_role` before the existing sensitive-role policy, with a regression for the FreeRTOS runtime packet.

## Verification

- `python3 -m py_compile tools/bazel/phase27_retained_code_acceptance_decisions.py tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
- `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py`
- `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --wiring-only`
- `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26`
- `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27`
- `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --security-only`
- Before each source commit: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, `cargo test --all-features`

---

_Fixed: 2026-06-25T02:46:00Z_
_Fixer: the agent (gsd-code-fixer)_
_Iteration: 1_
