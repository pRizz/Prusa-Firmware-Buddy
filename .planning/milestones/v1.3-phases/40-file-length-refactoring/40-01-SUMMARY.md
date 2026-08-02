---
phase: 40-file-length-refactoring
plan: 01
subsystem: repository-policy
tags: [file-lengths, fail-closed, bazel, bright-builds, refactoring]
requires: []
provides:
  - Canonical 933-row exact-path file-length exception ledger
  - Shrink-only policy enforcement for 95 temporary campaign paths
  - Exact terminal reconciliation for 838 frozen paths and three locked owned conversions
affects: [40-02, 40-03, 40-04, 40-05, 40-06, file-length-verification]
tech-stack:
  added: []
  patterns:
    - immutable baseline sets with shrink-only active authority
    - strict TSV boundary parsing
    - one-command Bazel and managed-checker campaign gate
key-files:
  created:
    - .bright-builds-rules-checks.tsv
    - doc/file_length_policy.md
    - tools/bazel/phase40_file_length_policy.py
    - tools/bazel/phase40_file_length_policy_test.py
  modified:
    - tools/bazel/BUILD.bazel
    - BUILD.bazel
    - justfile
key-decisions:
  - "The checker-consumed TSV is the sole active exception authority; embedded sets define immutable policy boundaries only."
  - "Temporary membership may only shrink, while owned permanence is restricted to the three locked deletion-test conversions."
  - "Terminal mode requires exactly the frozen 838 paths plus all three locked owned paths and no temporary reasons."
patterns-established:
  - "Validate syntax, sort order, uniqueness, reasons, set membership, and terminal equality before accepting the ledger."
  - "Use `just phase40-verify` as the serial policy-test, active-ledger, and managed-checker gate."
requirements-completed: [D-01, D-02, D-03, D-04, D-09, D-12]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 40-2026-07-27T16-44-56
generated_at: 2026-07-27T18:21:52Z
duration: 11m
completed: 2026-07-27
---

# Phase 40 Plan 01: File-Length Baseline and Policy Gate Summary

The managed checker now accepts an exact 933-path baseline while a tested fail-closed gate prevents temporary debt growth, provenance weakening, unauthorized permanence, and incomplete terminal reconciliation.

## Performance

- **Duration:** 11 minutes
- **Started:** 2026-07-27T18:10:57Z
- **Completed:** 2026-07-27T18:21:52Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Classified the live 933 findings into exactly 838 frozen permanent provenance/declarative paths and 95 shrink-only temporary campaign paths.
- Documented approved permanent reasons, campaign evidence, atomic removal, and the exact three owned deletion-test conversions.
- Added a standard-library verifier with strict TSV parsing, immutable policy sets, shrink-only validation, and exact terminal mode.
- Added 13 focused regressions for malformed rows, duplicates, reasons, growth, reclassification, unauthorized permanence, shrinkage, and terminal equality.
- Exposed the verifier and tests through Bazel aliases and the authoritative `just phase40-verify` command without changing managed checker or workflow code.

## Task Commits

1. **Task 1: Seed the exact baseline ledger** - `0f495e069`
2. **Task 2: Add the fail-closed Phase 40 policy gate** - `f6bbbd448`

## Files Created/Modified

- `.bright-builds-rules-checks.tsv` - Canonical sorted 933-row exception authority.
- `doc/file_length_policy.md` - Reason, deletion-test, campaign, and evidence contract.
- `tools/bazel/phase40_file_length_policy.py` - Shrink-only and terminal policy verifier.
- `tools/bazel/phase40_file_length_policy_test.py` - Thirteen fail-closed policy regressions.
- `tools/bazel/BUILD.bazel` - Runnable verifier and test targets.
- `BUILD.bazel` - Root aliases and exported ledger source.
- `justfile` - Single serial Phase 40 verification recipe.

## Decisions Made

- The immutable sets protect the original classification boundary; only the TSV controls active checker exceptions.
- Provenance/declarative permanence is frozen at 838 paths, so it cannot grow or be weakened into temporary debt.
- The initial ledger must fail terminal mode until all 95 temporary paths are removed and the three locked owned paths have completed their documented conversions.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] Used the repository shell rule for Python policy targets**

- **Found during:** Task 2
- **Issue:** Native `py_binary` and `py_test` rules were unavailable in the repository's Bazel configuration.
- **Fix:** Used the existing `shell_binary` rule for the executable Python verifier and test runner, exported the root ledger as Bazel data, and retained root aliases.
- **Files modified:** `tools/bazel/BUILD.bazel`, `BUILD.bazel`
- **Commit:** `f6bbbd448`

## Known Stubs

None. The created verifier and tests contain no placeholder, TODO, mock-data, or unwired-data stubs.

## Verification

- `bazel run //:phase40_file_length_policy_test` — 13 passed
- `bazel run //:phase40_file_length_policy` — passed with 838 permanent, 95 temporary, and 933 total paths
- `bazel run //:phase40_file_length_policy -- --terminal` — intentionally rejected the initial baseline with 95 temporary paths
- `just phase40-verify` — passed policy tests, active-ledger validation, and all managed checks
- `bun scripts/bright-builds-check.ts all` — zero findings with 933 exceptions
- `.venv/bin/pre-commit run --files ...` — passed, including YAPF
- `cargo fmt --all` — passed
- `cargo clippy --all-targets --all-features -- -D warnings` — passed
- `cargo build --all-targets --all-features` — passed
- `cargo test --all-features` — passed
- `git diff --check` — passed
- Managed checker and workflow source diffs — empty

## Self-Check: PASSED

- All seven implementation, policy, and ledger files and this summary exist.
- Task commits `0f495e069` and `f6bbbd448` exist in repository history.
- No unplanned network, authentication, schema, generated-output, or external file-access threat surface was introduced.
