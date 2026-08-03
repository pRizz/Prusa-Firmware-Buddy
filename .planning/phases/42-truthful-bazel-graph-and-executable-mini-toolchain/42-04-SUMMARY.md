---
phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
plan: 04
subsystem: build-tooling
tags: [bazel, platforms, toolchains, cquery, aquery, rules-python, provenance]
requires:
  - phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
    plan: 02
    provides: "Exact hard-float MINI platform and Linux-only executable qualification provider"
  - phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
    plan: 03
    provides: "Genuine Cortex-M4 hard-float ARM link smoke and inspection graph"
provides:
  - "Exact-target rejection matrix for every unsupported platform tuple and missing embedded capability"
  - "Configured, action, provider, and Python provenance audit for the canonical MINI smoke graph"
  - "Status-preserving rules_python subprocess support with bounded isolated Bazel servers"
affects: [42-05-truthful-facade, 46-first-safe-boot-link, 49-canonical-qualification]
tech-stack:
  added: []
  patterns: [positive-bracketed rejection matrix, configured-and-action graph audit, execution-surface provenance filtering]
key-files:
  created:
    - tools/bazel/phase42/phase42_test_support.py
    - tools/bazel/phase42/platform_rejection_test.py
    - tools/bazel/phase42/graph_isolation_test.py
  modified:
    - tools/bazel/phase42/BUILD.bazel
key-decisions:
  - "Model missing Rust, Arm, Python, and Mini404 capabilities as analysis-time select failures with explicit owner/remedy diagnostics."
  - "Bracket each negative platform category with a passing exact MINI control so harness failure cannot masquerade as rejection evidence."
  - "Audit rules_python execution provenance while excluding TemplateExpand source and substitution metadata that is not an executed interpreter edge."
patterns-established:
  - "Every exact negative invokes --noskip_incompatible_explicit_targets, preserves the real Bazel status/output, and rejects skip-only success."
  - "Canonical Linux graph evidence is collected in one isolated Bazel server with set-based cquery/aquery expressions."
requirements-completed: [BUILD-03, TOOL-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 42-2026-08-03T19-34-09
generated_at: 2026-08-03T22:26:59Z
duration: 37min
completed: 2026-08-03
---

# Phase 42 Plan 04: Platform Rejection and Graph Isolation Summary

**Exact-target platform negatives and configured/action provenance checks now prove that only the canonical Linux x86_64 MINI tuple reaches the declared Rust/Arm graph.**

## Performance

- **Duration:** 37 min
- **Started:** 2026-08-03T21:49:42Z
- **Completed:** 2026-08-03T22:26:59Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added 17 exact negative cases across default/host, six non-MINI products, five wrong tuple values, and four missing capabilities, bracketed by eight successful exact MINI controls on canonical Linux x86_64.
- Added configured and action graph audits covering five canonical constraints, five locked identities, seven named embedded actions, three required outputs, and sixteen forbidden fallback/provenance classes.
- Proved that reference and fixture surfaces do not export `EmbeddedToolchainInfo`, and that all six Phase 42 Python test actions resolve through the pinned rules_python 3.12.10 repository.
- Preserved deterministic native Darwin expected rejection without claiming a positive embedded qualification row.

## Task Commits

1. **Task 1 RED: Add failing platform rejection matrix** - `0526ea1bf` (test)
2. **Task 1 GREEN: Enforce exact MINI platform rejection** - `56471cbbd` (feat)
3. **Task 2 RED: Add failing graph isolation audit** - `ff0141938` (test)
4. **Task 2 GREEN: Audit embedded graph isolation** - `3097a6d36` (feat)

## Files Created/Modified

- `tools/bazel/phase42/BUILD.bazel` - Test-only wrong tuple platforms, missing-capability analysis gates, shared Python support, and both Plan 04 test targets.
- `tools/bazel/phase42/phase42_test_support.py` - Declared-Python subprocess helper preserving command, stdout, stderr, and nonzero status through one isolated Bazel server.
- `tools/bazel/phase42/platform_rejection_test.py` - Exact-target positive/negative matrix with incompatible-target skipping disabled.
- `tools/bazel/phase42/graph_isolation_test.py` - Pure provenance matchers plus real Linux cquery/aquery/provider/Python closure verification.

## Decisions Made

- Used analysis-time `select()` failure targets for missing capabilities because native rule `toolchains` attributes do not by themselves require resolution.
- Reused one temporary Bazel output base per test process with `--max_idle_secs=5`; this preserves isolation without paying per-command server startup cost.
- Batched provider and Python target sets into single graph queries, reducing the real graph audit from thirteen Bazel subprocesses to four while preserving every target assertion.
- Treated rules_python TemplateExpand `template_content` and `substitutions` fields as generator metadata, not executable provenance; action owners, paths, arguments, environment, symlink targets, and the pinned interpreter repository remain audited.

## Verification Evidence

### Canonical Linux x86_64 positive qualification

- A disposable `linux/amd64` container running Bazel 9.2.0 passed the exact combined command for `//tools/bazel/phase42:platform_rejection_tests` and `//tools/bazel/phase42:graph_isolation_tests` with uncached results and lockfile error mode.
- The combined run completed in 129.646 seconds: graph isolation passed in 71.1 seconds and the platform rejection matrix passed in 100.1 seconds.
- The matrix executed 17 nonzero exact-target negatives and eight passing `--config=mini` controls, with `--noskip_incompatible_explicit_targets` applied throughout.
- The graph audit found all five canonical constraints and locked Rust 1.85.0, Arm GNU 13.2.Rel1, Python 3.12.10, Mini404 0.9.10, and `thumbv7em-none-eabihf` identities.
- The action audit found `Phase42RustCompile`, `Phase42ArmLink`, four Arm inspections, `Phase42SmokeReport`, and the ELF/map/report outputs without any forbidden fallback edge.

### Native Darwin arm64 expected rejection

- The exact combined Plan 04 Bazel suite passed natively as expected-rejection contract evidence.
- Darwin verifies the detected-host `HostPolicyInfo` diagnostic and absence of `EmbeddedToolchainInfo`; it does not configure or report a positive embedded graph.

### Repository and regression gates

- `git diff --check` passed and Plan 04 made no change to `platforms/BUILD.bazel` or `tools/bazel/phase42/platform_contract.bzl`.
- `MODULE.bazel.lock` remained at SHA-256 `5b18570e4fa8283ef15c861a3d3a8d5a5d94f1e8b41baf6594e3c3bc16e3d4c9`.
- `bun scripts/bright-builds-check.ts all` passed with zero findings.
- The required Rust sequence passed in order before each implementation commit: formatting, Clippy for all targets/features with warnings denied, all-target/all-feature build, and all-feature tests.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Made missing-capability fixtures fail during analysis**

- **Found during:** Task 1 GREEN canonical Linux matrix
- **Issue:** Native rule `toolchains` declarations did not force the missing Rust/Arm/Python/Mini404 fixtures to fail, so all four negative labels returned success.
- **Fix:** Replaced them with exact analysis-time `select()` gates whose `no_match_error` diagnostics identify the missing capability owner and remedy.
- **Files modified:** `tools/bazel/phase42/BUILD.bazel`
- **Verification:** All four missing-capability exact labels fail nonzero between passing MINI controls on canonical Linux.
- **Committed in:** `56471cbbd`

**2. [Rule 3 - Blocking] Reused a bounded isolated Bazel server for the rejection matrix**

- **Found during:** Task 1 GREEN canonical Linux matrix
- **Issue:** Starting every nested command with `--batch` exhausted the test timeout before the complete matrix could finish.
- **Fix:** Reused a per-test temporary output base with `--max_idle_secs=5`, retaining isolation and bounded cleanup while avoiding repeated server startup.
- **Files modified:** `tools/bazel/phase42/phase42_test_support.py`
- **Verification:** The full rejection matrix passed in 100.1 seconds in the combined canonical Linux run.
- **Committed in:** `56471cbbd`

**3. [Rule 3 - Blocking] Batched redundant graph queries**

- **Found during:** Task 2 GREEN canonical Linux graph audit
- **Issue:** Thirteen sequential nested cquery/aquery calls hit Bazel's 300-second test bound without producing an assertion failure.
- **Fix:** Combined configured/provider/Python targets with set-based query expressions, reducing the evidence collection to four real Bazel calls.
- **Files modified:** `tools/bazel/phase42/graph_isolation_test.py`
- **Verification:** The same graph evidence passed in 71.1 seconds in the combined canonical Linux run.
- **Committed in:** `3097a6d36`

**4. [Rule 1 - Bug] Distinguished rules_python generator metadata from execution provenance**

- **Found during:** Task 2 GREEN canonical Linux graph audit
- **Issue:** Full textproto scanning interpreted rules_python's generated `#!/usr/bin/env python3` TemplateExpand substitution as an ambient executed interpreter even though the action symlink resolved to the pinned Python repository.
- **Fix:** Excluded only `template_content` and `substitutions` metadata from the execution surface, retained all execution-field scans, and added a focused regression test.
- **Files modified:** `tools/bazel/phase42/graph_isolation_test.py`
- **Verification:** Ambient/local interpreter mutation cases still fail, while all six real Python action owners pass with `rules_python++python+python_3_12_10` provenance.
- **Committed in:** `3097a6d36`

**5. [Rule 1 - Bug] Normalized generated roadmap progress formatting**

- **Found during:** Plan completion metadata update
- **Issue:** The roadmap updater emitted a malformed progress row with a missing separator space and an empty completed-date cell.
- **Fix:** Restored the established table shape with `4/5`, `In Progress`, and `-` values.
- **Files modified:** `.planning/ROADMAP.md`
- **Verification:** Markdown table structure and `git diff --check` pass.
- **Committed in:** Plan metadata commit

**Total deviations:** 5 auto-fixed (3 bugs, 2 blocking performance issues)
**Impact on plan:** The implementation fixes make the planned negative and provenance evidence truthful and bounded without broadening the canonical platform, changing locked inputs, or adding production behavior; the metadata fix only restores the established roadmap format.

## Issues Encountered

- The first Linux graph audit correctly exposed that reference/fixture provider text contains its own provenance markers and that rules_python graph text contains generator source. The audit was narrowed to the planned trust boundaries: forbidden closure on the configured embedded target, absence of embedded-provider leakage on reference/fixture targets, and pinned execution provenance on Python actions.

## Known Stubs

None. Empty error lists are validation accumulators, and the wrong-platform/missing-capability labels are deliberate negative test fixtures.

## User Setup Required

None - canonical positive qualification is self-contained in the declared Linux x86_64 Bazel/container route.

## Next Phase Readiness

- Plan 42-05 can aggregate the proven platform rejection and graph isolation labels into the canonical Phase 42 verifier.
- The one permitted embedded tuple remains MINI/BUDDY/STM32F407VG hard-float; reference, fixture, archive, host-Cargo/CMake, and ambient Python routes cannot satisfy qualification.

## Self-Check: PASSED

- All four Plan 04 implementation files and this summary exist at their expected paths.
- TDD commits `0526ea1bf`, `56471cbbd`, `ff0141938`, and `3097a6d36` exist in repository history.
- The combined canonical Linux matrix/graph suite, native Darwin rejection-only suite, lockfile hash, platform immutability check, Bright Builds checks, Rust gates, and `git diff --check` all passed.
- The generated roadmap row was normalized to the established four-column format and reports 4/5 plans in progress.
- Summary frontmatter uses one opening/closing delimiter pair; body separators use headings or `***`.

***

*Phase: 42-truthful-bazel-graph-and-executable-mini-toolchain*
*Completed: 2026-08-03*
