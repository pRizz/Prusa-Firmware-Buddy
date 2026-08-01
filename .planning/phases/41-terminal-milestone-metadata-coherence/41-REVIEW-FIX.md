---
phase: 41-terminal-milestone-metadata-coherence
fixed_at: 2026-08-01T19:20:10Z
review_path: .planning/phases/41-terminal-milestone-metadata-coherence/41-REVIEW.md
iteration: 3
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 41: Code Review Fix Report

**Fixed at:** 2026-08-01T19:20:10Z
**Source review:** `.planning/phases/41-terminal-milestone-metadata-coherence/41-REVIEW.md`
**Iterations completed:** 3

**Summary:**

- Findings in scope: 7
- Fixed: 7
- Skipped: 0

## Fixed Issues

### Iteration 1

#### CR-01: Pre-archive can pass without independent Phase 41 verification

**Status:** fixed: requires human verification
**Files modified:** `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/phase41_terminal_consistency.py`, `tools/bazel/phase41_terminal_consistency_policy.py`, `tools/bazel/phase41_terminal_consistency_test.py`, `tools/bazel/phase41_terminal_consistency_archive_test.py`, `tools/bazel/phase41_terminal_consistency_boundary_test.py`, `tools/bazel/phase41_terminal_consistency_test_support.py`
**Commit:** c18cc6b02
**Applied fix:** Added an exact optional Phase 41 verification boundary record and made pre-archive require present, parsed, passed verification whose timestamp is at least as new as the latest Phase 41 summary and no newer than the audit. Pre-audit still accepts the artifact's absence. An allow-empty exact Bazel glob represents the absent-before-verification and present-after-verification runfiles lifecycle without analysis failure. Policy, boundary, malformed, failed, missing, stale, ordering, and missing-timestamp regressions were added, with shared test support split below the managed file-length limit.

#### WR-01: Missing and negative validation statuses normalize as green

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase41_terminal_consistency.py`, `tools/bazel/phase41_terminal_consistency_policy.py`, `tools/bazel/phase41_terminal_consistency_test.py`, `tools/bazel/phase41_terminal_consistency_boundary_test.py`, `tools/bazel/phase41_terminal_consistency_test_support.py`
**Commit:** 5dea74e90
**Applied fix:** Replaced substring matching with a bounded exact status grammar after stripping one known presentation marker. Validation evidence must contain recognized task or campaign identities with matching statuses; empty, identity-less, duplicate, negative, blank, and unknown evidence fails closed. Adversarial parser and policy regressions cover `incomplete`, `not complete`, `not passed`, blank values, unrelated status tables, empty evidence, and unsupported values.

#### WR-02: Missing audit evidence is converted to zero gaps

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase41_terminal_consistency.py`, `tools/bazel/phase41_terminal_consistency_policy.py`, `tools/bazel/phase41_terminal_consistency_test.py`, `tools/bazel/phase41_terminal_consistency_boundary_test.py`, `tools/bazel/phase41_terminal_consistency_test_support.py`
**Commit:** d2e9d49eb
**Applied fix:** Audit gap and rollup fields now preserve absence as `None`. Parsing requires one explicit scope, requirements, coherence, integration, metadata, Nyquist, and archival-blocker rollup plus the exact seven flow identities and Phase 31–41 Nyquist identities. Missing or malformed structure marks the audit unparsed and emits explicit boundary violations. Regression tests remove each required section class and a required rollup and prove fail-closed behavior.

#### WR-03: Duplicate ROADMAP lifecycle and inventory rows are silently collapsed

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/phase41_terminal_consistency.py`, `tools/bazel/phase41_terminal_consistency_boundary_test.py`
**Commit:** c3353f21a
**Applied fix:** Counted raw ROADMAP lifecycle rows, phase headings, per-phase plan-progress rows, and plan basenames before building normalized projections. Duplicate phase and plan identities now emit boundary violations and are not silently retained through dictionary or set normalization. Focused regressions cover duplicate lifecycle rows, headings, plans, and progress fields.

### Iteration 2

#### WR-01: Fabricated validation identities still satisfy the terminal gate

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/BUILD.bazel`, `tools/bazel/phase41_terminal_consistency_contracts.py`, `tools/bazel/phase41_terminal_consistency_policy.py`, `tools/bazel/phase41_terminal_consistency_test.py`, `tools/bazel/phase41_terminal_consistency_boundary_test.py`, `tools/bazel/phase41_terminal_consistency_test_support.py`
**Commit:** 94d9e69a6
**Applied fix:** Froze the exact task or campaign identity inventory for every Phase 31–41 validation contract in an independent contract module. Policy now compares observed and expected identities as multisets before status evaluation, so fabricated, missing, extra, duplicate, and valid-looking subset rows fail closed. Policy and boundary regressions cover all five adversarial identity classes while coherent fixtures use the complete trusted inventories.

#### WR-02: Summary timestamp omissions can bypass freshness and mixed timezones crash parsing

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/BUILD.bazel`, `tools/bazel/phase41_terminal_consistency.py`, `tools/bazel/phase41_terminal_consistency_timestamp_test.py`
**Commit:** c48ffeedc
**Applied fix:** Centralized timestamp parsing at the filesystem boundary, requiring timezone-aware ISO-8601 values for every Phase 41 summary and every present Phase 41 verification plus the milestone audit. Accepted timestamps normalize to UTC. Any missing, invalid, or naive timestamp emits `P41_TIMESTAMP_INVALID`; one invalid summary poisons the cached freshness cutoff, and audit or verification freshness becomes false without raising mixed-naive/aware comparison errors. Focused regressions cover missing, invalid, naive, all-naive, mixed-naive/aware, and mixed-zone inputs.

### Iteration 3

#### WR-01: Ambiguous Markdown tables and sections can bypass terminal evidence checks

**Status:** fixed: requires human verification
**Files modified:** `tools/bazel/BUILD.bazel`, `tools/bazel/phase41_terminal_consistency.py`, `tools/bazel/phase41_terminal_consistency_markdown.py`, `tools/bazel/phase41_terminal_consistency_boundary_test.py`
**Commit:** 540dd9d70
**Applied fix:** Extracted the shared path-aware Markdown boundary parser and made ROADMAP/REQUIREMENTS traceability, every Phase 31–41 validation record, and milestone audit scope/flow/Nyquist consumers require exactly one named level-two section and exactly one matching contiguous table. The parser rejects duplicate case-normalized or empty headers before exposing row dictionaries, rejects ambiguous table blocks and row widths, and marks validation/audit records malformed when their boundary structure is contradictory. Required-heading matching ignores repeated unrelated prose headings and fenced examples. Adversarial pre-archive regressions cover red-to-green duplicate `Status`, duplicate `Audit classification`, repeated validation maps/tables/sign-offs, repeated audit flow/Nyquist sections, and contradictory duplicate audit rollup rows.

## Verification Evidence

Before each finding commit, the required Rust sequence passed in order: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features` (136 Rust tests). Iteration 1 retained its four independently verified commits. Iteration 2 additionally passed 67 direct Python tests before WR-01 and 72 before WR-02, the corresponding uncached Bazel targets, `bun scripts/bright-builds-check.ts all` with zero findings, and scoped `git diff --check` runs.

Iteration 3 passed scoped YAPF and Python compilation, 78 direct Python tests, all four uncached Phase 41 Bazel test targets, and Bright Builds with zero findings. The final source files are 568, 230, and 537 lines, below the managed 629-line threshold. The scoped and whole-worktree `git diff --check` runs passed, Bazel-generated `MODULE.bazel.lock` drift was restored, and the atomic commit contains only the four listed source/test/build files. `.planning/config.json`, `41-REVIEW.md`, and this report were preserved outside the source commit; `.planning/config.json` was never staged.

***

_Fixed: 2026-08-01T19:20:10Z_
_Fixer: the agent (gsd-code-fixer)_
_Iterations: 3_
