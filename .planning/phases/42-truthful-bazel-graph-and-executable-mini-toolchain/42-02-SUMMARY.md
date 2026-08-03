---
phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
plan: 02
subsystem: build-tooling
tags: [bazel, platforms, toolchains, rust, arm-gnu, host-policy, mini]
requires:
  - phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
    plan: 01
    provides: "Pinned checksum-backed Rust, Python, Arm GNU, and Mini404 repositories"
provides:
  - "Exact runtime/MINI/BUDDY/STM32F407VG/thumbv7em-none-eabihf platform contract"
  - "Linux x86_64 qualification provider backed by declared executable FilesToRunProviders"
  - "Deterministic Darwin x86_64/arm64 rejection through non-qualifying HostPolicyInfo with zero actions"
affects: [42-03-arm-link-smoke, 42-04-platform-rejection, 42-05-truthful-facade]
tech-stack:
  added: [platforms-1.1.0]
  patterns: [single qualification toolchain type, provider-first host rejection, exact five-value target allowlist]
key-files:
  created:
    - tools/bazel/toolchains/embedded_toolchain.bzl
    - tools/bazel/phase42/platform_contract.bzl
    - tools/bazel/phase42/host_policy.bzl
    - tools/bazel/phase42/embedded_toolchain_contract_test.py
    - tools/bazel/phase42/host_policy_contract_test.py
  modified:
    - MODULE.bazel
    - platforms/BUILD.bazel
    - tools/bazel/toolchains/BUILD.bazel
    - tools/bazel/phase42/BUILD.bazel
key-decisions:
  - "Centralize the authoritative Phase 42 target allowlist as exactly five hard-float MINI constraints and reuse it for every qualification toolchain registration."
  - "Expose embedded executables only from the Linux x86_64 implementation; Darwin implementations return HostPolicyInfo only and create no actions."
  - "Import the exact generated rules_rust Linux hard-float tools repository under a stable apparent name while keeping rules_python registration separate."
patterns-established:
  - "Consumers inspect HostPolicyInfo, fail with its diagnostic when non-qualifying, and only then access EmbeddedToolchainInfo."
  - "Executable provider fields come from executable exec-configured labels through DefaultInfo.files_to_run, never assembled path strings."
requirements-completed: [BUILD-03, TOOL-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 42-2026-08-03T19-34-09
generated_at: 2026-08-03T20:49:53Z
duration: 8min
completed: 2026-08-03
---

# Phase 42 Plan 02: Canonical MINI Qualification Toolchain Summary

**Bazel now models one exact hard-float MINI target tuple, a complete pinned Linux executable provider, and deterministic zero-action Darwin rejection without exporting embedded tools.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-08-03T20:41:50Z
- **Completed:** 2026-08-03T20:49:53Z
- **Tasks:** 1
- **Files modified:** 9

## Accomplishments

- Added the `rust_target` constraint setting and made `//platforms:mini_buddy_stm32f407vg` contain exactly embedded runtime, MINI, BUDDY, STM32F407VG, and `thumbv7em-none-eabihf` values.
- Added one Phase 42 qualification toolchain type whose Linux x86_64 implementation exposes all nine declared executables, locked identities, and the hard-float triple.
- Added Darwin x86_64 and arm64 implementations that expose only non-qualifying `HostPolicyInfo`, carry the exact detected-host/Linux-remedy diagnostic, and register no actions.
- Added focused mutation tests covering constraint narrowing/broadening, executable replacement, version drift, reference-provider leakage, Darwin tool leakage/actions, and consumer ordering.

## Task Commits

1. **Task 1 RED: Add failing qualification contracts** - `6af05f102` (test)
2. **Task 1 GREEN: Add canonical MINI qualification toolchain** - `958089de0` (feat)

## Files Created/Modified

- `MODULE.bazel` - imports the direct platforms module and stable rules_rust Linux tools alias, then registers all three qualification implementations.
- `platforms/BUILD.bazel` - adds the Rust target setting/value and the fifth canonical MINI constraint.
- `tools/bazel/toolchains/BUILD.bazel` - declares the qualification type, executable-backed Linux implementation, non-executable Darwin implementations, and exact compatibility constraints.
- `tools/bazel/toolchains/embedded_toolchain.bzl` - defines the complete embedded provider and Linux/Darwin toolchain implementations.
- `tools/bazel/phase42/platform_contract.bzl` - owns the exact five-value allowlist.
- `tools/bazel/phase42/host_policy.bzl` - defines host policy constructors and the provider-first consuming helper.
- `tools/bazel/phase42/BUILD.bazel` - exposes both rules_python contract test targets.
- `tools/bazel/phase42/embedded_toolchain_contract_test.py` - validates and mutation-tests the platform, executable, version, and reference boundaries.
- `tools/bazel/phase42/host_policy_contract_test.py` - validates and mutation-tests Linux qualification, Darwin rejection, zero actions, and consumer ordering.

## Decisions Made

- Used a single qualification toolchain type for all hosts so a Darwin consumer receives a structured host policy instead of a generic missing-toolchain error.
- Kept `HostPolicyInfo` separate from `EmbeddedToolchainInfo`; Darwin targets cannot represent an embedded provider at all.
- Used Bazel executable labels with `cfg = "exec"` and `DefaultInfo.files_to_run`, which is Bazel 9's supported accessor for the labels' `FilesToRunProvider`.

## Verification Evidence

- TDD RED: both declared Bazel tests failed because `platform_contract.bzl` and `host_policy.bzl` did not exist.
- TDD GREEN: `bazel test //tools/bazel/phase42:embedded_toolchain_contract_tests //tools/bazel/phase42:host_policy_contract_tests --nocache_test_results --lockfile_mode=error` passed.
- The Plan 01 provenance suite passed uncached after the module/toolchain registration changes.
- `bazel cquery` of the Linux implementation exposed qualifying `HostPolicyInfo` plus every `EmbeddedToolchainInfo` field with Rust 1.85.0, Arm GNU 13.2.Rel1, Python 3.12.10, Mini404 0.9.10, and `thumbv7em-none-eabihf`.
- `bazel cquery` of the Darwin arm64 implementation exposed only non-qualifying `HostPolicyInfo` with `unsupported embedded qualification host: detected Darwin-arm64; use canonical Linux x86_64 CI/container`; its `aquery` contained zero actions.
- This Darwin evidence is contract/rejection evidence only. It is not reported as positive embedded qualification; canonical Linux x86_64 execution remains the positive host boundary.
- Both new Python test actions resolved `rules_python++python+python_3_12_10_aarch64-apple-darwin/bin/python3`, with no `/usr/bin`, `/usr/local`, or Homebrew interpreter edge.
- `bazel mod graph --lockfile_mode=error`, `git diff --check`, and the unchanged `MODULE.bazel.lock` check passed.
- `bun scripts/bright-builds-check.ts all` reported `SUMMARY all findings=0`.
- The required Cargo sequence passed in order: format, Clippy with warnings denied, all-target/all-feature build, and all-feature tests.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Declared the direct platforms module dependency**

- **Found during:** Task 1 GREEN implementation
- **Issue:** Bazel could not resolve `@platforms//os:*` or `@platforms//cpu:*` from the root module because the transitive module was not directly visible.
- **Fix:** Added the already-selected `platforms` 1.1.0 module as a direct dependency and mutation-tested the declaration.
- **Files modified:** `MODULE.bazel`, `tools/bazel/phase42/embedded_toolchain_contract_test.py`
- **Verification:** Toolchain registration analysis and all focused tests pass with `--lockfile_mode=error`; `MODULE.bazel.lock` is unchanged.
- **Committed in:** `958089de0`

**2. [Rule 1 - Bug] Used Bazel's supported FilesToRunProvider accessor**

- **Found during:** Task 1 GREEN implementation
- **Issue:** Bazel 9 exposes executable labels through `DefaultInfo.files_to_run`; the `FilesToRunProvider` symbol itself is not directly defined in Starlark.
- **Fix:** Kept every attribute executable and exec-configured, then stored each label's `DefaultInfo.files_to_run` value in `EmbeddedToolchainInfo` and updated the focused contract assertion.
- **Files modified:** `tools/bazel/toolchains/embedded_toolchain.bzl`, `tools/bazel/phase42/embedded_toolchain_contract_test.py`
- **Verification:** `cquery` identifies every embedded field as a single-executable FilesToRunProvider and both focused suites pass.
- **Committed in:** `958089de0`

**3. [Rule 1 - Bug] Normalized generated roadmap progress formatting**

- **Found during:** Plan completion metadata update
- **Issue:** The roadmap updater emitted a malformed progress-table row with a missing separator space and blank completed-date cell.
- **Fix:** Restored the existing table shape with `2/5`, `In Progress`, and `-` values.
- **Files modified:** `.planning/ROADMAP.md`
- **Verification:** Markdown table structure and `git diff --check` pass.
- **Committed in:** Plan metadata commit

**Total deviations:** 3 auto-fixed (1 blocking dependency, 2 bugs)
**Impact on plan:** The implementation fixes were required for the planned Bazel contract, and the metadata fix preserves the established roadmap format; none broadens the supported host or target surface.

## Issues Encountered

- The initial contract parser crossed adjacent `platform(...)` blocks while selecting the canonical target. It was narrowed to inspect each call independently before the GREEN commit.

## Known Stubs

None. Empty diagnostic text is intentional for the qualifying Linux policy; empty error lists are validation accumulators, not runtime placeholders.

## User Setup Required

None - all toolchain inputs remain declared through Bazel/Bzlmod.

## Next Phase Readiness

- Plan 42-03 can consume `require_embedded_toolchain(ctx)` to reject Darwin before accessing tools and use the Linux executable provider for the real Cortex-M4 hard-float link smoke.
- Darwin remains intentionally non-qualifying, and no successful embedded compile/link claim was made on this host.

## Self-Check: PASSED

- All five created implementation/test files and this summary exist at their expected paths.
- TDD commits `6af05f102` and `958089de0` exist in repository history.
- Summary frontmatter has one opening/closing delimiter pair, and the committed implementation diff passes `git diff --check`.

***

*Phase: 42-truthful-bazel-graph-and-executable-mini-toolchain*
*Completed: 2026-08-03*
