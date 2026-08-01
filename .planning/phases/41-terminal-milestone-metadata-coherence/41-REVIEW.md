---
phase: 41-terminal-milestone-metadata-coherence
reviewed: 2026-08-01T19:05:04Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/shell_rules.bzl
  - tools/bazel/phase41_terminal_consistency.py
  - tools/bazel/phase41_terminal_consistency_archive_test.py
  - tools/bazel/phase41_terminal_consistency_boundary_test.py
  - tools/bazel/phase41_terminal_consistency_contracts.py
  - tools/bazel/phase41_terminal_consistency_policy.py
  - tools/bazel/phase41_terminal_consistency_test.py
  - tools/bazel/phase41_terminal_consistency_test_support.py
  - tools/bazel/phase41_terminal_consistency_timestamp_test.py
  - .planning/phases/41-terminal-milestone-metadata-coherence/41-REVIEW.md
  - .planning/phases/41-terminal-milestone-metadata-coherence/41-REVIEW-FIX.md
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Phase 41: Code Review Report

**Reviewed:** 2026-08-01T19:05:04Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

All six previously recorded findings are closed for their stated direct cases. Pre-archive now requires independent passed verification in summary-to-verification-to-audit timestamp order; validation statuses use an exact grammar; audit absence remains absent and required rollups/sections are explicit; duplicate ROADMAP identities fail before normalization; validation identities match frozen exact Phase 31–41 inventories; and every relevant timestamp must be timezone-aware and is normalized to UTC. The frozen identity inventories also exactly match all eleven live validation documents.

One broader boundary ambiguity still fails open. The generic Markdown parser silently collapses duplicate table headers and selects only the first matching section. This permits contradictory validation or audit evidence to be normalized as green and can produce a zero-violation pre-archive result. The terminal checker therefore does not yet meet its malformed-or-ambiguous-input fail-closed contract.

Review judgments were informed by repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, the absence of active `standards-overrides.md` exceptions, and the managed architecture, code-shape, verification, and testing standards. Verification performed during this final review: 72 direct Python tests passed; all four uncached Bazel test targets passed; the managed Bright Builds checker reported zero findings; the scoped `git diff --check` passed; and focused adversarial probes reproduced WR-01 below. The live direct pre-audit command reached the checker and reported the expected transitional ROADMAP/STATE lifecycle mismatches because Phase 41 remains in verification rather than terminal completion; this is phase-state evidence, not a source-code regression. Bazel-generated `MODULE.bazel.lock` drift was restored, and the pre-existing `.planning/config.json` modification was preserved.

## Warnings

### WR-01: Ambiguous Markdown tables and sections can bypass terminal evidence checks

**File:** `tools/bazel/phase41_terminal_consistency.py:112-145`
**Issue:** `section()` returns the first matching heading without detecting another section with the same required identity, while `table_rows()` creates each row with `dict(zip(header, cells))` without rejecting duplicate normalized header names. Python retains only the last value for a duplicate key. A validation table with exact Phase 31 identities and headers `Task ID | Status | Status`, whose rows contain `red | green`, is therefore parsed as an exact all-green inventory and produces no pre-audit violation. The same construction with audit `Status` and `Audit classification` columns converts explicit `incomplete | complete` and `noncompliant | compliant` values into zero gaps; combined with a coherent snapshot it produced no pre-archive violation. Repeating a required audit heading also leaves a later contradictory section unexamined. This reopens the malformed-input fail-closed boundary even though the six specific prior cases are fixed.
**Fix:** Make required-section and table parsing path-aware and uniqueness-enforcing. Reject repeated required headings, reject duplicate case-normalized header names before constructing row dictionaries, and parse tables as distinct contiguous blocks rather than flattening every pipe-prefixed line in a section. Add boundary regressions proving duplicate `Status`, duplicate `Audit classification`, and repeated required audit/validation sections yield a stable boundary violation and nonzero pre-archive result.

```python
normalized_headers = tuple(cell.strip().casefold() for cell in header)
if len(set(normalized_headers)) != len(normalized_headers):
    parser.violation(path, "P41_TABLE_HEADER_DUPLICATE", header,
                     "unique case-normalized columns")
    return []
```

***

_Reviewed: 2026-08-01T19:05:04Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
