---
phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
plan: 05
subsystem: build-infrastructure
tags: [bazel, rules-python, embedded-toolchain, host-policy, developer-facade]

requires:
  - phase: 42-04
    provides: Canonical MINI platform matrix, genuine Arm link smoke, and configured/action graph isolation
provides:
  - Analysis-time capability gates for unavailable firmware build, test, package, and simulator authority
  - Eight fixed reference execution/preview labels with descriptive non-qualifying provenance
  - Canonical Linux x86_64 aggregate verifier and route-complete Darwin rejection check
affects: [phase-43, phase-46, phase-47, phase-48, build-authority, developer-workflow]

tech-stack:
  added: []
  patterns: [analysis-time capability gate, fixed-semantics reference labels, host-gated aggregate verification]

key-files:
  created:
    - tools/bazel/phase42/capability_gate.bzl
    - tools/bazel/phase42/facade_contract_test.py
    - tools/bazel/phase42/reference_separation_test.py
    - tools/bazel/phase42/phase42_verify.py
    - tools/bazel/phase42/phase42_verify_test.py
  modified:
    - .bazelrc
    - justfile
    - tools/bazel/BUILD.bazel
    - tools/bazel/phase2_verify.py
    - tools/bazel/phase42/BUILD.bazel
    - tools/bazel/phase42/graph_isolation_test.py
    - tools/bazel/reference_contract.sh

key-decisions:
  - "Unavailable public capabilities fail from rule analysis after resolving HostPolicyInfo and publish no actions, outputs, DefaultInfo, or qualification providers."
  - "Reference execution and preview semantics are fixed by eight label basenames; environment values cannot switch a label between preview and execution."
  - "Only Linux x86_64 may return a successful Phase 42 aggregate; Darwin host-check proves every public rejection route without producing positive evidence."

patterns-established:
  - "Truthful facade: stable developer verbs route to analysis-time capability gates until their owning phases supply real authority."
  - "Reference oracle isolation: retained CMake/Python work uses explicit reference_* names and descriptive reference provenance only."
  - "Canonical aggregate: snapshot lock, prove declared interpreter, run ordered evidence, inspect genuine outputs, and recheck lock before success."

requirements-completed: [BUILD-02, BUILD-03, BUILD-04, TOOL-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 42-2026-08-03T19-34-09
generated_at: 2026-08-03T23:04:25Z

duration: 34min
completed: 2026-08-03
---

# Phase 42 Plan 05: Truthful Facade and Canonical Aggregate Summary

**Analysis-time authority gates, fixed reference execution/previews, and a rules_python aggregate now make canonical Linux x86_64 the only positive Phase 42 qualification path.**

## Performance

- **Duration:** 34 min
- **Started:** 2026-08-03T22:30:48Z
- **Completed:** 2026-08-03T23:04:25Z
- **Tasks:** 3 TDD tasks
- **Files modified:** 12

## Accomplishments

- Replaced fixture-backed, print-only, runtime-error, and host-workflow firmware facades with analysis-time gates that name the owning phase and an exact working Phase 42 remedy.
- Split the retained oracle into four always-executing reference labels and four print-only plan labels, removed the active environment switch, and proved their closure cannot expose embedded qualification.
- Added five thin Phase 42 recipes/targets plus a declared Python 3.12.10 aggregate that reproduces prior false-positive routes, inspects the genuine ELF/map/report outputs, and checks lock stability.
- Proved all smoke, direct authority, stable recipe, and aggregate routes reject Darwin with one detected-host/Linux-remedy contract while canonical Linux x86_64 completes successfully.

## Task Commits

Each TDD task was committed atomically:

1. **Task 1 RED: Truthful facade regression contract** - `f1bcced30` (test)
2. **Task 1 GREEN: Analysis-time capability gates** - `c7cb7be89` (feat)
3. **Task 2 RED: Reference separation contract** - `39cb546d1` (test)
4. **Task 2 GREEN: Fixed reference execution and previews** - `a44260313` (feat)
5. **Task 3 RED: Canonical aggregate contract** - `ca3a69cc0` (test)
6. **Task 3 GREEN: Canonical verifier and stable recipes** - `e202999f3` (feat)

## Files Created/Modified

- `.bazelrc` - Removed the active reference-execution environment switch.
- `justfile` - Added five Phase 42 recipes, eight reference recipes, and truthful stable authority routing.
- `tools/bazel/BUILD.bazel` - Added capability gates and the eight isolated reference targets; renamed historical package fixtures explicitly.
- `tools/bazel/phase2_verify.py` - Revised legacy checks for current gates/reference labels and forbidden switched semantics.
- `tools/bazel/reference_contract.sh` - Dispatches fixed execution or preview behavior solely from the exact label basename.
- `tools/bazel/phase42/BUILD.bazel` - Declares rules_python contracts, verifier binaries, focused suites, and the aggregate suite.
- `tools/bazel/phase42/capability_gate.bzl` - Fails unavailable public capabilities during analysis through HostPolicyInfo.
- `tools/bazel/phase42/facade_contract_test.py` - Reproduces build/run/just false-positive and Darwin policy routes.
- `tools/bazel/phase42/reference_separation_test.py` - Proves execution status, preview output, provider closure, actions, and runfiles isolation.
- `tools/bazel/phase42/phase42_verify.py` - Runs the canonical Linux evidence sequence and Darwin rejection-only host check.
- `tools/bazel/phase42/phase42_verify_test.py` - Guards aggregate ordering, recipe purity, host injection, and false-success mutations.
- `tools/bazel/phase42/graph_isolation_test.py` - Uses the explicitly renamed historical Phase 3 fixture target.

## Decisions Made

- Kept `unavailable_capability` declared executable so `bazel run` reaches the same analysis implementation as `bazel build`; the implementation itself creates no action, output, executable provider, or qualification provider.
- Kept `tools/bazel/phase2_verify.py` directly runnable only as a legacy non-qualifying check; the aggregate consumes its revised contract through rules_python tests, never its ambient-host result.
- Rewired `format` and `lint` to the existing Rust workflow labels and removed the dangling generic bootstrap recipe after the old switched reference targets were retired.
- Buffered successful aggregate subprocess output and emitted concise ordered PASS records, pinned identities, genuine artifact paths, and the stable lock digest at completion.

## Verification Evidence

- `bazel test //tools/bazel/phase42:phase42_verifier_tests --nocache_test_results --test_output=errors` passed all nine declared-Python suites on Darwin.
- `just phase42-host-check` rejected smoke, four direct authority labels, four stable recipes, and the aggregate with detected `Darwin-arm64` and the canonical Linux remedy; `just phase42-verify` remained nonzero.
- Canonical `Linux-x86_64` ran `just phase42-verify` successfully in the Bazel 9.2.0 amd64 container against the final source.
- The aggregate emitted Bazel 9.2.0, Rust 1.85.0, Arm GNU 13.2.Rel1, Python 3.12.10, Mini404 0.9.10, `thumbv7em-none-eabihf`, and genuine `arm_link_smoke.elf`, `.map`, and `.report.json` paths.
- `MODULE.bazel.lock` remained at SHA-256 `5b18570e4fa8283ef15c861a3d3a8d5a5d94f1e8b41baf6594e3c3bc16e3d4c9` throughout qualification.
- `cargo fmt --all`, strict Clippy, all-target/all-feature build, all-feature tests, Bright Builds checks, and `git diff --check` passed before the implementation commit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated graph isolation for the explicit historical fixture name**

- **Found during:** Task 1 GREEN
- **Issue:** Renaming the fixture authority left the existing graph audit pointed at the obsolete generic target.
- **Fix:** Updated both provider-boundary references to `phase3_fixture_release_artifacts`.
- **Files modified:** `tools/bazel/phase42/graph_isolation_test.py`
- **Verification:** Facade and graph-isolation suites both passed.
- **Committed in:** `c7cb7be89`

**2. [Rule 1 - Bug] Corrected preview assertions for shell-escaped exact commands**

- **Found during:** Task 2 GREEN
- **Issue:** The RED test compared unescaped substrings even though the contract requires exact shell-quoted previews.
- **Fix:** Asserted the escaped marker and retained the no-execution assertion for both retired switch values.
- **Files modified:** `tools/bazel/phase42/reference_separation_test.py`
- **Verification:** Reference separation, four plan recipes, and the legacy Phase 2 verifier passed.
- **Committed in:** `a44260313`

______________________________________________________________________

**Total deviations:** 2 auto-fixed bugs.
**Impact on plan:** Both fixes were required to keep existing verification accurate; no architectural or product scope changed.

## Issues Encountered

- A final stability rerun initially failed before Bazel analysis because a named Docker cache volume was not writable by the image's default user. The final bounded attempt used explicit root HOME/cache ownership and completed the exact canonical aggregate successfully. No source change was required.

## Known Stubs

None. Empty collections found by the stub scan are test/result accumulators, not user-facing or qualification data placeholders.

## User Setup Required

None - no external service configuration required.

## Self-Check: PASSED

- All five created implementation/test files and this summary exist.
- All six TDD task commits resolve as commits in repository history.
- Canonical Linux evidence and the unchanged lock digest are recorded above.

## Next Phase Readiness

- Phase 43 can consume the truthful test gate and canonical aggregate without inheriting false host/reference success.
- Phases 46-48 have exact public capability gates and working Phase 42 remedies until real build, package, and simulator authority replaces them.
- No Phase 42 blocker remains; Darwin is intentionally rejection-only and Linux x86_64 is the positive qualification host.

______________________________________________________________________

*Phase: 42-truthful-bazel-graph-and-executable-mini-toolchain*
*Completed: 2026-08-03*
