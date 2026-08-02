---
phase: 35-cutover-decision-artifact
plan: "01"
subsystem: cutover-decision
tags:
  - python
  - json
  - bazel
  - just
  - cutover
  - audit
  - fail-closed
requirements-completed:
  - CUTOVER-01
  - CUTOVER-02
  - CUTOVER-03
dependency_graph:
  requires:
    - phase31-final-evidence-intake
    - phase32-blocker-register-and-evidence-triage
    - phase33-maintainer-decision-inputs
    - phase34-final-readiness-and-demotion-dry-run
  provides:
    - closed cutover verdict artifact
    - exact nine-kind audit-link index
    - planning-only next-milestone route
    - independent demotion decision and gate projection
  affects:
    - tools/bazel
    - justfile
    - ci-evidence
tech_stack:
  added:
    - Python unittest cutover-decision verifier
    - Bazel shell_binary verification wrappers
    - just phase35-verify facade
  patterns:
    - one canonical audit index drives JSON and Markdown projections
    - exact-set anti-joins fail closed on audit-link drift
    - repair criteria resolve to exact upstream field references
    - cutover and reference-demotion authority remain orthogonal
key_files:
  created:
    - tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json
    - tools/bazel/phase35_cutover_decision_artifact.py
    - tools/bazel/phase35_cutover_decision_artifact_test.py
  modified:
    - tools/bazel/BUILD.bazel
    - BUILD.bazel
    - tools/bazel/rust_workflow.sh
    - justfile
    - .planning/phases/35-cutover-decision-artifact/35-VALIDATION.md
decisions:
  - Phase 35 derives verdict JSON, route JSON, and Markdown from one exact nine-kind canonical audit-link index.
  - Blocked and approved-with-exceptions verdicts route to targeted repair and require a fresh cutover decision.
  - Phase 33 demotion decision validation/value/source and the Phase 34 demotion gate remain independent from the cutover verdict.
metrics:
  started_at: 2026-07-25T21:58:12Z
  completed_at: 2026-07-25T22:18:54Z
  duration: 20m42s
  tasks_completed: 3
  commits_created: 3
generated_by: gsd-execute-plan
generated_at: 2026-07-25T22:18:54Z
lifecycle_mode: yolo
phase_lifecycle_id: 35-2026-07-25T21-06-10
---

# Phase 35 Plan 01: Cutover Decision Artifact Summary

A fail-closed cutover decision bundle now links every Phase 31–34 evidence, blocker, exception, risk, readiness, and demotion input to an exact planning-only route without synthesizing production authority.

## What Changed

- Added a lifecycle-bound contract with closed verdict and route enums, twenty-two blocking reasons, exact output schemas, nine audit-link categories, security boundaries, and separate demotion decision/gate states.
- Added thirty-one RED-first regression tests covering verdict truth tables, exact-set audit anti-joins, canonical digests, exact repair criteria, non-collapsing demotion states, path containment, lifecycle drift, secret rejection, and JSON/Markdown consistency.
- Added the Phase 35 verifier with contract, quick, security, and wiring modes; deterministic safe snapshots; exact eight-artifact output validation; and a durable blocked/repair default.
- Added Bazel targets and root aliases plus exact-order workflow regeneration and `just phase35-verify`, preserving all Phase 34 prerequisite arguments.
- Marked the Phase 35 validation strategy verified only after focused, Bazel, developer-facade, regression, pre-commit, diff, and Rust gates passed.

## Task Commits

| Task | Name | Commit | Files |
| --- | --- | --- | --- |
| 1 | Contract and RED-first regressions | `eac72886d` | Phase 35 contract and unittest suite |
| 2 | Canonical audit, verdict, route, and bundle generator | `5ce6ed808` | Phase 35 verifier |
| 3 | Bazel/workflow/just wiring and validation | `389177fb5` | Bazel files, workflow, justfile, verifier wiring check, formatted tests, validation |

## Verification

- Task 1 RED discovered thirty-one tests and failed only because the Phase 35 verifier module did not exist.
- `python3 -m py_compile tools/bazel/phase35_cutover_decision_artifact.py tools/bazel/phase35_cutover_decision_artifact_test.py`
- `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q` — thirty-one tests passed.
- Contract-only, security-only, wiring-only, and quick generation modes passed.
- Quick output asserted `blocked`, `targeted-blocker-repair`, fresh-decision required, no production authorization, and missing/blocked demotion state.
- `bazel run //tools/bazel:phase35_verify_tests`, `bazel run //tools/bazel:phase35_verify`, and `just phase35-verify` passed.
- Phase 28 and Phase 31–35 regression suites passed: 162 tests total.
- Scoped `pre-commit run --files ...` passed after applying repository YAPF formatting.
- `git diff --check` and the scoped diff review passed; generated evidence remained ignored and unrelated `.planning/config.json` was preserved.
- `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` passed in the required order.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Accepted Phase 34 missing-row sentinels**

- **Found during:** Task 2 quick generation
- **Issue:** Phase 34 intentionally emits blank `classification_ref` values for `required-row-missing` ledger sentinels, but the initial generic source security scan treated every blank `*_ref` as malformed.
- **Fix:** Kept strict validation for emitted audit links while allowing blank upstream source refs to reach the fail-closed coverage projection.
- **Files modified:** `tools/bazel/phase35_cutover_decision_artifact.py`
- **Commit:** `5ce6ed808`

**2. [Rule 1 - Bug] Preserved Phase 32 owner labels**

- **Found during:** Task 2 quick generation
- **Issue:** Phase 32 `owner_ref` values are accountable-owner labels such as `safety-maintainer`, not repository paths, and the initial generic path-ref scan rejected them.
- **Fix:** Excluded `owner_ref` labels from filesystem reference validation while retaining them in exact repair scope.
- **Files modified:** `tools/bazel/phase35_cutover_decision_artifact.py`
- **Commit:** `5ce6ed808`

**3. [Rule 3 - Blocking] Provisioned the missing pre-commit runner**

- **Found during:** Task 3 final verification
- **Issue:** The host had no `pre-commit` executable.
- **Fix:** Installed `pre-commit` in an isolated temporary virtual environment and ran the exact scoped hook command without changing repository dependencies.
- **Files modified:** None

## Auth Gates

None.

## Known Stubs

None. Empty lists and dictionaries found by the stub scan are internal accumulators, explicit fail-closed defaults, or test fixture builders; none flow to the UI or substitute for a required data source.

## Deferred Issues

None.

## Self-Check: PASSED

- Summary exists at `.planning/phases/35-cutover-decision-artifact/35-01-SUMMARY.md`.
- The Phase 35 contract, verifier, test, Bazel targets, workflow arms, `just` recipe, and verified validation file exist.
- Task commits `eac72886d`, `5ce6ed808`, and `389177fb5` are reachable in git history.
- Summary frontmatter uses only the opening and closing `---` delimiters.
