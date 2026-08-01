---
phase: 41-terminal-milestone-metadata-coherence
reviewed: 2026-08-01T18:17:10Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - BUILD.bazel
  - justfile
  - tools/bazel/BUILD.bazel
  - tools/bazel/shell_rules.bzl
  - tools/bazel/phase41_terminal_consistency.py
  - tools/bazel/phase41_terminal_consistency_policy.py
  - tools/bazel/phase41_terminal_consistency_test.py
findings:
  critical: 1
  warning: 3
  info: 0
  total: 4
status: issues_found
---

# Phase 41: Code Review Report

**Reviewed:** 2026-08-01T18:17:10Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

The Phase 41 policy core is deterministic and the focused test target passes, but the filesystem/Markdown boundary is not fully fail closed. The strict pre-archive gate can pass without the independent Phase 41 verification required by the phase contract, and malformed or omitted validation/audit evidence can normalize into green values. Duplicate ROADMAP identities are also collapsed before the policy can reject them.

Review judgments were informed by repo-local `AGENTS.md`, `AGENTS.bright-builds.md`, the absence of active `standards-overrides.md` exceptions, and the managed architecture, code-shape, verification, and testing standards. Verification performed during review: 38 direct Python tests passed; the Bazel test target passed; `git diff --check` passed; the managed Bright Builds checker reported zero findings. Adversarial parser probes reproduced all three warning-class fail-open paths below.

## Critical Issues

### CR-01: Pre-archive can pass without independent Phase 41 verification

**File:** `tools/bazel/phase41_terminal_consistency_policy.py:171-179`

**Issue:** `TerminalSnapshot` has no Phase 41 verification record, and `_evaluate_audit` at lines 491-527 checks only audit fields. The root runfiles list at `BUILD.bazel:293-311` likewise omits `41-VERIFICATION.md`. Consequently, the test fixture at `phase41_terminal_consistency_test.py:166-176` is considered coherent in `pre-archive` mode despite containing no verification evidence. This bypasses the explicitly required independent-verification gate and can authorize archival based only on mutable ROADMAP/STATE/VALIDATION/audit projections.

**Fix:** Add a normalized verification input, parse the exact Phase 41 verification artifact at the boundary, include it in Bazel runfiles, and require it to be present, parsed, passed, and no newer than the audit before pre-archive can succeed. Add missing, malformed, failed, and stale verification tests.

```python
@dataclass(frozen=True)
class VerificationRecord:
    path: str
    present: bool
    parsed: bool
    status: str
    verified_at: datetime | None

# In pre-archive evaluation:
if not verification.present or not verification.parsed:
    violations.append(_violation(verification.path, "P41_VERIFICATION_MISSING", ...))
elif verification.status != "passed":
    violations.append(_violation(verification.path, "P41_VERIFICATION_STATUS", ...))
```

## Warnings

### WR-01: Missing and negative validation statuses normalize as green

**File:** `tools/bazel/phase41_terminal_consistency.py:242-257`

**Issue:** `normalized_status` uses substring matching, so values such as `incomplete`, `not complete`, and `not passed` normalize to accepted statuses. Separately, an omitted or unparseable task-status table yields `task_statuses=()`, and the policy loop at `phase41_terminal_consistency_policy.py:418-433` emits no violation for an empty tuple. A validation file can therefore retain true frontmatter and checked sign-off bullets while deleting its campaign rows or using explicitly negative wording, and both modes accept it.

**Fix:** Parse a bounded, exact status grammar after removing only known presentation markers, preserve unknown/negative values as invalid, and require a non-empty set of expected task or campaign identities for every validation file.

```python
def normalized_status(value: str) -> str:
    normalized = strip_known_markers(value).strip().lower()
    if normalized not in {"pending", "red", "green", "pass", "passed", "complete"}:
        return "unsupported"
    return normalized

if not record.task_statuses:
    violations.append(_violation(path, "P41_VALIDATION_TASKS_MISSING", 0, ">= 1"))
```

### WR-02: Missing audit evidence is converted to zero gaps

**File:** `tools/bazel/phase41_terminal_consistency.py:358-400`

**Issue:** Missing `End-to-End Flows` and `Nyquist Coverage` tables produce empty lists whose sums are zero. Missing `Runtime integration gaps` and `Milestone archival blockers` rows also default directly to zero. The policy then treats all four zeroes as success. Removing those audit sections and rows reproduced an `AuditRecord` with `integration_gaps=0`, `flow_gaps=0`, `metadata_gaps=0`, and `nyquist_gaps=0`, so absent evidence is indistinguishable from an explicit zero-gap audit.

**Fix:** Represent missing fields as `None` or add explicit presence/shape flags, require exact expected row identities/counts before calculating gaps, and mark the audit malformed when any required section or summary row is absent.

```python
if not flow_rows or not nyquist_rows:
    parser.violation(AUDIT_PATH, "P41_AUDIT_SECTION_MISSING", ...)
if maybe_integration is None or maybe_metadata is None:
    parser.violation(AUDIT_PATH, "P41_AUDIT_ROLLUP_MISSING", ...)
```

### WR-03: Duplicate ROADMAP lifecycle and inventory rows are silently collapsed

**File:** `tools/bazel/phase41_terminal_consistency.py:169-210`

**Issue:** Duplicate phase headings and lifecycle rows are written into dictionaries keyed by phase, so later values overwrite earlier ones without a boundary violation. Roadmap plan entries are preserved initially, but `_evaluate_inventories` converts them to a set at `phase41_terminal_consistency_policy.py:339-341`, discarding duplicate identities. A probe with two Phase 31 lifecycle rows produced no boundary violation. This defeats the contract that ambiguous and duplicate input must fail closed and lets contradictory or repeated projections pass when the retained value matches expected state.

**Fix:** Count raw phase headings, lifecycle rows, progress/count fields, and roadmap plan basenames before normalization. Emit a duplicate violation unless every required identity occurs exactly once, then build the normalized dictionaries/sets only after uniqueness is established.

```python
phase_row_counts = Counter(int(phase) for _, phase in status_matches)
for phase, count in phase_row_counts.items():
    if count != 1:
        parser.violation(ROADMAP_PATH, "P41_ROADMAP_PHASE_DUPLICATE", phase, "one row")

plan_counts = Counter(roadmap_plans)
if any(count != 1 for count in plan_counts.values()):
    parser.violation(ROADMAP_PATH, "P41_ROADMAP_PLAN_DUPLICATE", ...)
```

***

_Reviewed: 2026-08-01T18:17:10Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
