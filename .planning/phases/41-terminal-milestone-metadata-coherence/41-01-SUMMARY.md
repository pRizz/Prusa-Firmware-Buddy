---
phase: 41-terminal-milestone-metadata-coherence
plan: 01
subsystem: testing
tags: [python, bazel, metadata, nyquist, fail-closed]
requires:
  - phase: 39-milestone-metadata-reconciliation
    provides: "Frozen reconciliation semantics and exact milestone inventory requirements"
  - phase: 40-file-length-refactoring
    provides: "Managed file-length policy and terminal validation surfaces"
provides:
  - "Pure immutable terminal-consistency policy for v1.3 metadata, inventories, validation, and audit authority"
  - "Read-only pre-audit and pre-archive CLI with deterministic bounded diagnostics"
  - "Focused 36-test Python/Bazel suite and phase41-verify just facade"
affects: [41-02-metadata-repair, 41-03-audit-refresh, milestone-audit, milestone-archive]
tech-stack:
  added: []
  patterns: [pure policy core with thin I/O shell, exact-identity inventory checks, fail-closed boundary parsing]
key-files:
  created:
    - tools/bazel/phase41_terminal_consistency_policy.py
    - tools/bazel/phase41_terminal_consistency.py
    - tools/bazel/phase41_terminal_consistency_test.py
  modified:
    - BUILD.bazel
    - justfile
    - tools/bazel/BUILD.bazel
    - tools/bazel/shell_rules.bzl
key-decisions:
  - "Treat the milestone audit as a checked input consumed only in pre-archive mode, never as authority for the facts being audited."
  - "Compare exact plan and summary identities rather than trusting declared counts, and reject malformed or unreadable Markdown boundaries."
  - "Keep diagnostics deterministic, bounded, and secret-safe by reporting normalized metadata or semantic digests instead of source content."
patterns-established:
  - "Terminal metadata gates evaluate frozen immutable records in a pure policy module; filesystem and Markdown parsing stay in a thin read-only CLI."
  - "Bazel-run workspace checks resolve the live checkout through BUILD_WORKSPACE_DIRECTORY while still declaring planning inputs as runfiles data."
requirements-completed: [INTAKE-01, INTAKE-02, INTAKE-03, READY-02, READY-03, CUTOVER-01, CUTOVER-03]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 41-2026-08-01T16-27-53
generated_at: 2026-08-01T17:27:26Z
duration: 21min
completed: 2026-08-01
---

# Phase 41 Plan 01: Terminal Consistency Checker Summary

**A pure fail-closed policy and read-only Bazel/just facade now detect terminal v1.3 requirement, inventory, validation, state, and audit incoherence before metadata repair or archive.**

## Performance

- **Duration:** 21 min
- **Started:** 2026-08-01T17:06:08Z
- **Completed:** 2026-08-01T17:27:26Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Defined immutable records for all 16 v1.3 requirements, Phase 31-41 lifecycle/inventory state, validation evidence, milestone projection, and audit freshness with deterministic `P41_*` violations.
- Added 36 focused tests covering every frozen inconsistency class, malformed boundaries, count spoofing, partial Phase 37/38/40 evidence, circular audit authority, stable ordering, exit semantics, and secret-safe output.
- Added a thin read-only CLI with `pre-audit` and `pre-archive` modes, a Bazel test/run surface, and `just phase41-verify` composition.
- Proved the current live tree fails with exit 1 for the intended pre-repair surfaces while invalid invocation fails with exit 2.

## Task Commits

1. **Task 1: Build the pure terminal consistency policy and exhaustive tests** - `31db384f4` (feat)
2. **Task 2: Add the read-only CLI plus Bazel and just integration** - `77f9403d9` (feat)

## Files Created/Modified

- `tools/bazel/phase41_terminal_consistency_policy.py` - frozen terminal models, canonical requirement semantics, pure evaluators, deterministic diagnostics, and exit mapping.
- `tools/bazel/phase41_terminal_consistency_test.py` - 36 behavior-focused policy tests with coherent fixtures and explicit fail-closed mutations.
- `tools/bazel/phase41_terminal_consistency.py` - strict read-only Markdown/filesystem adapter and CLI for live pre-audit/pre-archive checks.
- `BUILD.bazel` - phase-scoped planning-data filegroup for global metadata, audit, and Phase 31-41 validation inputs.
- `tools/bazel/BUILD.bazel` - focused checker binary and test targets.
- `tools/bazel/shell_rules.bzl` - minimal local Python-backed test rule for Bazel 8.
- `justfile` - stable `phase41-verify` developer facade.

## Decisions Made

- Kept all evaluation decisions in the pure policy module; the CLI only parses bounded sources, assembles a snapshot, evaluates once, and renders violations.
- Required exact on-disk plan/summary identity and pairing, preventing stale counts from masquerading as a coherent inventory.
- Used semantic digests for requirement-text mismatches so diagnostics prove inequality without disclosing raw planning content.
- Preserved the intentional pre-repair baseline: requirement traceability remains pending for Plan 02 rather than being mutated by this checker plan.

## Verification Evidence

- Direct focused suite: 36 tests passed.
- Bazel focused suite: `//tools/bazel:phase41_terminal_consistency_tests` passed.
- Live direct and Bazel pre-audit: exit 1 with diagnostics naming pending REQUIREMENTS, missing Phase 36/37/39/41 ROADMAP inventory, nonterminal STATE, and partial Phase 37/38/40 validation evidence.
- Invalid invocation: exit 2.
- `just phase41-verify --mode pre-audit`: focused Bazel tests pass before the intentional live exit 1.
- Managed checks: `bun scripts/bright-builds-check.ts all` reported `SUMMARY all findings=0`.
- Required pre-commit sequence passed in order: Cargo format, Clippy with warnings denied, all-target/all-feature build, and all-feature tests.
- YAPF, `git diff --check`, and the managed-checker immutability assertion passed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added a minimal local Bazel test rule**

- **Found during:** Task 2 (Bazel integration)
- **Issue:** Bazel 8 no longer exposed native `sh_test`, and the repository had no rules_shell or rules_python dependency, so the required focused Bazel test target could not load.
- **Fix:** Added `shell_test` beside the existing local `shell_binary` rule; it creates a strict Bash launcher that executes the declared Python test from runfiles.
- **Files modified:** `tools/bazel/shell_rules.bzl`, `tools/bazel/BUILD.bazel`
- **Verification:** The required `bazel test //tools/bazel:phase41_terminal_consistency_tests` target passed all 36 tests.
- **Committed in:** `77f9403d9`

**2. [Rule 3 - Blocking] Exported the checker planning inputs from the root Bazel package**

- **Found during:** Task 2 (live Bazel execution)
- **Issue:** Phase 36-41 validation documents existed on disk but were not exported by the root package, so direct runfiles labels failed Bazel analysis.
- **Fix:** Added the phase-scoped `phase41_terminal_consistency_docs` filegroup containing only the global metadata/audit files and Phase 31-41 validations the checker reads.
- **Files modified:** `BUILD.bazel`, `tools/bazel/BUILD.bazel`
- **Verification:** The live Bazel target analyzed, ran against the checkout, and returned the expected fail-closed exit 1 with all known surfaces named.
- **Committed in:** `77f9403d9`

**Total deviations:** 2 auto-fixed blocking issues
**Impact on plan:** Both changes were narrow integration support required by the planned Bazel acceptance surface; neither changes checker policy or milestone metadata.

## Issues Encountered

- Bazel rewrote `MODULE.bazel.lock` while loading the local targets. The tooling-only drift was restored exactly after final Bazel verification and was not committed.

## Known Stubs

None. Empty tuple defaults model an absence of parser violations or fixture mutations and do not feed user-interface output.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02 can repair REQUIREMENTS, ROADMAP, STATE, and historical validations against a frozen executable oracle.
- Plan 03 can refresh the v1.3 milestone audit and then run the stricter pre-archive mode without relying on circular audit authority.
- The current exit 1 is intentional evidence of the known pre-repair baseline, not an implementation failure.

## Self-Check: PASSED

- The Plan 01 summary and all three created checker files exist at the expected paths.
- Task commits `31db384f4` and `77f9403d9` exist in repository history.
- `MODULE.bazel.lock` has no diff, and the known pre-existing config/audit worktree edits remain unstaged.

***

*Phase: 41-terminal-milestone-metadata-coherence*
*Completed: 2026-08-01*
