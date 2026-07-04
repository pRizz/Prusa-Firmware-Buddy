---
phase: 33-maintainer-decision-inputs
plan: "01"
subsystem: cutover-decision-inputs
tags:
  - python
  - json
  - bazel
  - just
  - maintainer-decisions
  - fail-closed
requirements-completed:
  - DECIDE-01
  - DECIDE-02
  - DECIDE-03
dependency_graph:
  requires:
    - phase32-blocker-register-and-evidence-triage
    - phase27-retained-code-acceptance-decisions
    - phase28-final-readiness-packet-and-demotion-gate
  provides:
    - phase33-maintainer-decision-inputs
    - phase34-final-readiness-and-demotion-dry-run handoff
    - phase35-maintainer-decision-audit handoff
  affects:
    - tools/bazel
    - justfile
    - ci-evidence
tech_stack:
  added:
    - Python unittest verifier coverage
    - Bazel shell_binary wrappers
    - just phase33-verify facade
  patterns:
    - fail-closed JSON contract validation
    - secret-safe generated handoff bundle
    - explicit maintainer authorization axes
key_files:
  created:
    - tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json
    - tools/bazel/phase33_maintainer_decision_inputs.py
    - tools/bazel/phase33_maintainer_decision_inputs_test.py
  modified:
    - tools/bazel/BUILD.bazel
    - BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - justfile
    - .planning/phases/33-maintainer-decision-inputs/33-VALIDATION.md
decisions:
  - Phase 33 consumes Phase 32 blocker rows and existing Phase 27/28 vocabulary without reclassifying evidence.
  - Readiness, retained-code, residual-risk, exception, and reference-demotion decisions remain independent explicit maintainer inputs.
  - The workflow facade regenerates upstream evidence inputs before writing the Phase 33 handoff bundle.
metrics:
  started_at: 2026-07-04T02:24:04Z
  completed_at: 2026-07-04T02:39:34Z
  duration: 15m30s
  tasks_completed: 3
  commits_created: 3
lifecycle_mode: yolo
phase_lifecycle_id: 33-2026-07-04T01-36-41
---

# Phase 33 Plan 01: Maintainer Decision Inputs Summary

Phase 33 now has a fail-closed maintainer decision-input contract, verifier, tests, and developer workflow facade for producing the Phase 34/35 handoff bundle from Phase 32 blocker rows.

## What Changed

- Added the Phase 33 contract manifest covering DECIDE-01, DECIDE-02, DECIDE-03, decision enums, generated artifacts, source contracts, and security prohibitions.
- Added `phase33_maintainer_decision_inputs.py` with contract, quick, security, and wiring modes.
- Added RED-first `unittest` coverage for retained-code, residual-risk, exception, readiness, reference-demotion, lifecycle, source-ref, security, and wiring behavior.
- Wired Bazel labels, root aliases, `rust_workflow.sh`, and `just phase33-verify`.
- Updated `33-VALIDATION.md` to `status: verified`, `nyquist_compliant: true`, and `wave_0_complete: true` after verification passed.

## Task Commits

| Task | Name | Commit | Files |
| --- | --- | --- | --- |
| 1 | Contract and RED tests | `ff2284da6` | `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json`, `tools/bazel/phase33_maintainer_decision_inputs_test.py` |
| 2 | Verifier implementation | `112f7b5db` | `tools/bazel/phase33_maintainer_decision_inputs.py`, `tools/bazel/phase33_maintainer_decision_inputs_test.py` |
| 3 | Workflow wiring and validation sign-off | `dafe12a46` | `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, `justfile`, `33-VALIDATION.md` |

## Verification

- Task 1 RED: `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` failed as expected before the verifier existed.
- `python3 -m py_compile tools/bazel/phase33_maintainer_decision_inputs.py tools/bazel/phase33_maintainer_decision_inputs_test.py`
- `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q`
- `python3 tools/bazel/phase33_maintainer_decision_inputs.py --contract-only`
- `python3 tools/bazel/phase33_maintainer_decision_inputs.py --security-only`
- `python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only`
- `python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick --phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase33`
- `bazel run //tools/bazel:phase33_verify_tests`
- `bazel run //tools/bazel:phase33_verify`
- `just phase33-verify`
- `git diff --check`
- `cargo fmt --all`
- `cargo clippy --all-targets --all-features -- -D warnings`
- `cargo build --all-targets --all-features`
- `cargo test --all-features`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed RED test fixture path overwrite**

- **Found during:** Task 2
- **Issue:** The test helper wrote every maintainer-decision fixture to the same `maintainer-decisions.json` path, so later invalid/valid fixtures could overwrite earlier cases inside one test root.
- **Fix:** Derived fixture paths from the first `decision_id`, keeping each decision packet isolated.
- **Files modified:** `tools/bazel/phase33_maintainer_decision_inputs_test.py`
- **Commit:** `112f7b5db`

## Auth Gates

None.

## Known Stubs

None. The stub scan found only internal accumulator defaults and an intentionally empty generated maintainer-decision template when no maintainer packet is supplied.

## Deferred Issues

None.

## Self-Check: PASSED

- Summary file exists at `.planning/phases/33-maintainer-decision-inputs/33-01-SUMMARY.md`.
- Created Phase 33 contract, verifier, and test files exist.
- Task commits `ff2284da6`, `112f7b5db`, and `dafe12a46` are reachable in git history.
- Summary frontmatter uses only the opening and closing `---` delimiters.
