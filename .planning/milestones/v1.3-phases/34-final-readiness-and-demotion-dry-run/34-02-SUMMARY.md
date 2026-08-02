---
phase: 34-final-readiness-and-demotion-dry-run
plan: "02"
subsystem: final-readiness-and-demotion
tags:
  - python
  - json
  - readiness
  - fail-closed
  - gap-closure
requirements-completed:
  - READY-02
  - READY-03
dependency_graph:
  requires:
    - phase31-final-evidence-intake
    - phase34-final-readiness-and-demotion-dry-run
  provides:
    - contract-driven required-stream completeness
    - explicit missing-stream ledger rows
  affects:
    - tools/bazel
key_files:
  modified:
    - tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json
    - tools/bazel/phase34_final_readiness_demotion_dry_run.py
    - tools/bazel/phase34_final_readiness_demotion_dry_run_test.py
decisions:
  - Required evidence completeness derives from the validated Phase 31 stream adapters, never from only the submitted receipt set.
  - Missing streams become direct required-row-missing ledger rows and do not depend on a Phase 32 blocker classification.
metrics:
  completed_at: 2026-07-25T20:11:00Z
  tasks_completed: 2
  commits_created: 2
generated_by: gsd-execute-plan
generated_at: 2026-07-25T20:11:00Z
lifecycle_mode: yolo
phase_lifecycle_id: 34-2026-07-25T18-18-48
---

# Phase 34 Plan 02: Required-Stream Completeness Gap Closure

Phase 34 now measures final-evidence completeness against all four required Phase 31 stream adapters. A partial accepted-final intake produces explicit blocked ledger rows and cannot open the reference-demotion dry run.

## What Changed

- Extended the Phase 34 contract with a Phase 31 `stream_adapters` required-set source and the `required-row-missing` absent-stream state.
- Added strict Phase 31 contract identity, lifecycle, adapter uniqueness, stream-set, and repository-relative path validation.
- Added deterministic missing-stream ledger rows with critical, ineligible, blocked semantics.
- Updated the isolated open fixture to provide all four required streams.
- Added per-stream omission regressions and contract tampering tests.

## Task Commit

| Task | Commit | Files |
| --- | --- | --- |
| Required-stream completeness and regressions | `71e213418` | Phase 34 contract, verifier, and tests |
| Missing-stream exception hardening | `27cc6603f` | Phase 34 verifier and tests |

## Verification

- `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q` — 36 tests passed.
- Phase 28 and Phase 31–34 regression suites — 131 tests passed.
- Contract-only, security-only, and wiring-only checks passed.
- `bazel run //tools/bazel:phase34_verify_tests` passed.
- `bazel run //tools/bazel:phase34_verify` passed.
- `just phase34-verify` passed.
- `git diff --check` passed.
- `cargo fmt --all` passed.
- `cargo clippy --all-targets --all-features -- -D warnings` passed.
- `cargo build --all-targets --all-features` passed.
- `cargo test --all-features` passed.

## Deviations from Plan

The delegated executor completed its required reads but stalled twice before editing. Per the repository two-attempt rule, the orchestrator applied the already checked plan directly in the main worktree. Scope and verification remained unchanged.

## Self-Check: PASSED

- Gap plan and summary exist.
- Implementation commits `71e213418` and `27cc6603f` are reachable.
- The previously failing partial-intake counterexample is covered for every required stream.
