---
phase: 40-file-length-refactoring
plan: 02
subsystem: rust-domain
tags: [rust, domain-model, module-facades, file-lengths, bazel]
requires:
  - phase: 40-01
    provides: Canonical shrink-only file-length ledger and Phase 40 policy gate
provides:
  - Stable network and auxiliary façades over cohesive private concept modules
  - Feature and GUI production modules with private extracted characterization suites
  - Four retired Rust-domain temporary exceptions with 91 temporary paths remaining
  - Shrink-aware Phase 40 regressions and split-aware Phase 10 API verification
affects: [40-03, 40-04, rust-domain, phase10-verification, file-length-verification]
tech-stack:
  added: []
  patterns:
    - stable public foo.rs façade over private concept-oriented child modules
    - test-only extraction when production code is already cohesive
    - verifier discovery of declared private Rust module surfaces
key-files:
  created:
    - rust/crates/domain/src/network/identity.rs
    - rust/crates/domain/src/network/transfer.rs
    - rust/crates/domain/src/network/service.rs
    - rust/crates/domain/src/network/tests.rs
    - rust/crates/domain/src/auxiliary/identity.rs
    - rust/crates/domain/src/auxiliary/transport.rs
    - rust/crates/domain/src/auxiliary/controller.rs
    - rust/crates/domain/src/auxiliary/tests.rs
    - rust/crates/domain/src/feature/tests.rs
    - rust/crates/domain/src/gui/tests.rs
  modified:
    - .bright-builds-rules-checks.tsv
    - rust/crates/domain/src/network.rs
    - rust/crates/domain/src/auxiliary.rs
    - rust/crates/domain/src/feature.rs
    - rust/crates/domain/src/gui.rs
    - tools/bazel/phase10_verify.py
    - tools/bazel/phase10_verify_test.py
    - tools/bazel/phase40_file_length_policy_test.py
key-decisions:
  - "Network and auxiliary retain their existing public module paths through explicit façade re-exports; child modules remain private."
  - "Feature and GUI keep cohesive production code in place and move only cfg(test) suites into private children."
  - "Phase 10 verification resolves implementations from private children declared by auxiliary.rs instead of requiring dead façade shims."
patterns-established:
  - "Split domain implementations by identity, transport/transfer, and service/controller policy while preserving the public façade."
  - "Policy regressions derive expectations from the active valid temporary subset while immutable original and terminal sets remain authoritative."
requirements-completed: [D-05, D-06, D-08, D-09, D-11, D-12, D-13]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T18:40:02Z
duration: 13m
completed: 2026-07-27
---

# Phase 40 Plan 02: Rust Domain Module Refactoring Summary

Stable network and auxiliary façades now front ten cohesive private implementation/test modules, while feature and GUI retain unchanged production APIs with extracted test suites and no Rust-domain length exceptions.

## Performance

- **Duration:** 13 minutes
- **Started:** 2026-07-27T18:26:38Z
- **Completed:** 2026-07-27T18:40:02Z
- **Tasks:** 2
- **Files modified:** 18

## Accomplishments

- Replaced the 1,278-line network module with a 20-line stable façade over identity, transfer, service, and test children ranging from 181 to 472 lines.
- Replaced the 1,117-line auxiliary module with a 19-line stable façade over identity, transport, controller, and test children ranging from 190 to 377 lines.
- Reduced feature and GUI production modules to 323 and 521 lines by moving only their existing characterization suites into 348-line and 215-line private test children.
- Removed all four Rust-domain temporary ledger rows, leaving the policy at 838 permanent and 91 temporary paths.
- Preserved the public type inventories, unchanged `lib.rs` exports, all 89 buddy-domain tests, all-feature builds, and affected Phase 8-10 contracts.

## Task Commits

1. **Task 1: Deepen network and auxiliary domain modules** - `cd2c11626`
2. **Task 2: Extract cohesive feature and GUI tests** - `714876cd6`

## Files Created/Modified

- `rust/crates/domain/src/network.rs` and `rust/crates/domain/src/network/` - Stable public façade with private identity, transfer, service, and test modules.
- `rust/crates/domain/src/auxiliary.rs` and `rust/crates/domain/src/auxiliary/` - Stable public façade with private identity, transport, controller, and test modules.
- `rust/crates/domain/src/feature.rs` and `rust/crates/domain/src/feature/tests.rs` - Unchanged production implementation with extracted Phase 6 feature-gate tests.
- `rust/crates/domain/src/gui.rs` and `rust/crates/domain/src/gui/tests.rs` - Unchanged production implementation with extracted GUI invariant tests.
- `.bright-builds-rules-checks.tsv` - Removed the four completed Rust-domain temporary exceptions.
- `tools/bazel/phase10_verify.py` - Resolves the auxiliary API surface from the façade and its declared private implementation children.
- `tools/bazel/phase10_verify_test.py` - Copies split auxiliary sources and proves private-child API resolution.
- `tools/bazel/phase40_file_length_policy_test.py` - Derives live shrink expectations and covers arbitrary valid temporary subsets.

## Decisions Made

- Explicit façade re-exports preserve public module paths without exposing private implementation structure.
- Feature and GUI required no production abstraction; test-only extraction met the threshold without shallow pass-through modules.
- Verifiers follow real source ownership so refactoring does not require compatibility code that exists only for textual scanners.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] Made Phase 40 regression expectations shrink-aware**

- **Found during:** Task 1
- **Issue:** Policy tests hard-coded the original 95-row temporary count, so the planned valid ledger shrink failed before the policy verifier could evaluate it.
- **Fix:** Derived active counts from the live ledger, preserved the immutable original and terminal sets, and added an arbitrary-valid-subset regression.
- **Files modified:** `tools/bazel/phase40_file_length_policy_test.py`
- **Verification:** 14 focused policy tests and `just phase40-verify` passed at both 93 and 91 temporary rows.
- **Committed in:** `cd2c11626`

**2. [Rule 3 - Blocking Issue] Taught Phase 10 verification to follow private Rust children**

- **Found during:** Task 1
- **Issue:** The Phase 10 verifier textually required auxiliary implementations in `auxiliary.rs`, conflicting with the planned stable façade and private child structure.
- **Fix:** Resolved declared private non-test children, scanned the combined implementation surface, copied those children into test fixtures, and added a split-surface regression.
- **Files modified:** `tools/bazel/phase10_verify.py`, `tools/bazel/phase10_verify_test.py`
- **Verification:** 14 Phase 10 verifier tests, `just phase10-verify`, and the full Rust suite passed.
- **Committed in:** `cd2c11626`

**Total deviations:** 2 auto-fixed blocking issues.
**Impact on plan:** Both fixes were required for the existing fail-closed verification system to accept the planned module and ledger shrink; no product behavior or public API scope changed.

## Issues Encountered

- Archived Phase 1 and Phase 5-10 planning artifacts are no longer present at their legacy active paths, while affected historical verifiers still read those paths. Exact temporary symlinks to `.planning/milestones/v1.0-phases/` were used only to run the Phase 8-10 gates and were removed before both commits.
- Targeted pre-commit runs refreshed `MODULE.bazel.lock` incidentally. The unrelated lockfile change was restored before each commit.

## Known Stubs

None. The created and modified production modules, tests, and verifiers contain no placeholder or unwired data paths.

## Threat Flags

None. This refactor introduced no network endpoint, authentication path, schema boundary, or new file-access surface; the verifier reads only private Rust children declared by the existing façade.

## Verification

- Exact ordered Cargo sequence before each task commit: `cargo fmt --all`; `cargo clippy --all-targets --all-features -- -D warnings`; `cargo build --all-targets --all-features`; `cargo test --all-features` — passed.
- Focused tests: `cargo test -p buddy-domain network`, `auxiliary`, `feature`, and `gui` — passed with unchanged cases and assertions.
- Public contract evidence: pre/post public struct and enum inventories matched, `rust/crates/domain/src/lib.rs` remained unchanged, and `cargo doc -p buddy-domain --no-deps` passed.
- `just rust-format`, `just rust-lint`, `just rust-build`, and `just rust-test` — passed.
- `just phase8-verify`, `just phase9-verify`, and `just phase10-verify` — passed using the temporary archived-artifact links described above.
- `just phase40-verify` — 14 policy regressions passed; active policy reports 838 permanent, 91 temporary, and 929 total paths.
- `bun scripts/bright-builds-check.ts all` — zero findings across 7,227 scanned files with 929 exceptions.
- Targeted `.venv/bin/pre-commit run --files ...` — passed.
- Physical line checks — all façades and child files are below 629 lines.
- `git diff --check` — passed.

## Self-Check: PASSED

- All 18 implementation, test, verifier, and ledger files and this summary exist.
- Task commits `cd2c11626` and `714876cd6` exist in repository history.
- Four planned Rust-domain temporary exception rows are absent, with the immutable permanent policy boundary unchanged.
