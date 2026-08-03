---
phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
plan: 01
subsystem: build-tooling
tags: [bazel, bzlmod, rust, python, arm-gnu, mini404, provenance]
requires:
  - phase: 41-canonical-linux-host-boundary-and-truthful-darwin-routing
    provides: "Host-local Darwin scope and canonical Linux qualification boundary"
provides:
  - "Exact Bazel 9.2.0, Rust 1.85.0, Python 3.12.10, and rules module declarations"
  - "Checksum-backed Linux x86_64 Arm GNU 13.2.Rel1 and Mini404 0.9.10 repositories"
  - "Fail-closed provenance mutations, hermetic interpreter proof, and byte-stable Bzlmod lock evidence"
affects: [42-02-executable-toolchains, 42-03-rust-crate-builds, 42-04-firmware-linking, 42-05-verification]
tech-stack:
  added: [bazel-9.2.0, rules_rust-0.71.3, rules_cc-0.2.22, rules_python-2.2.0, rust-1.85.0, python-3.12.10]
  patterns: [checksum-backed http archives, exact Bzlmod pins, mutation-tested provenance, stable lockfile boundary]
key-files:
  created:
    - .bazelversion
    - tools/bazel/toolchains/embedded_repositories.bzl
  modified:
    - MODULE.bazel
    - MODULE.bazel.lock
    - tools/bazel/phase42/BUILD.bazel
    - tools/bazel/phase42/toolchain_provenance_test.py
key-decisions:
  - "Use only checksum-backed Linux x86_64 archives for Arm GNU and Mini404; provide no Darwin, PATH, local repository, or .dependencies substitute."
  - "Supply rules_python 2.2.0 with checksum-pinned Python 3.12.10 standalone archives for Darwin arm64 host validation and canonical Linux x86_64 execution."
  - "Keep embedded executable toolchain registration and canonical platform selection out of Plan 01 for Plan 02 ownership."
patterns-established:
  - "Tool provenance is an executable contract: exact declarations pass while every version, archive identity, placeholder hash, and forbidden fallback mutation fails."
  - "Ordinary qualification runs with lockfile_mode=error and must leave MODULE.bazel.lock byte-for-byte unchanged."
requirements-completed: [TOOL-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 42-2026-08-03T19-34-09
generated_at: 2026-08-03T20:39:00Z
duration: 13min
completed: 2026-08-03
---

# Phase 42 Plan 01: Toolchain Provenance Summary

**Bazel now resolves exact, checksum-backed Rust, Python, Arm GNU, and Mini404 inputs behind a mutation-tested provenance contract and a byte-stable Bzlmod lock.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-08-03T20:26:31Z
- **Completed:** 2026-08-03T20:39:00Z
- **Tasks:** 1
- **Files modified:** 6

## Accomplishments

- Pinned Bazel 9.2.0, rules_rust 0.71.3 with Rust 1.85.0/edition 2024/`thumbv7em-none-eabihf`, rules_cc 0.2.22, and rules_python 2.2.0 with Python 3.12.10.
- Added exact official Linux x86_64 Arm GNU 13.2.Rel1 and Mini404 0.9.10 repositories with verified SHA-256 digests and fixed strip prefixes.
- Added seven focused provenance tests that reject version drift, archive identity drift, placeholder hashes, Darwin embedded archives, local/PATH/.dependencies fallbacks, Cargo/CMake outputs, fixtures, archives, planning artifacts, ambient Python, and incomplete lock state.
- Regenerated `MODULE.bazel.lock` once explicitly, then proved repeated uncached ordinary tests preserve its SHA-256 exactly.

## Task Commits

1. **Task 1 RED: Add failing toolchain provenance contract** - `6fd9ce003` (test)
2. **Task 1 GREEN: Pin hermetic toolchain provenance** - `6c5ea05e4` (feat)

## Files Created/Modified

- `.bazelversion` - exact Bazel 9.2.0 launcher pin.
- `MODULE.bazel` - exact rules, Rust target, Python standalone archive, and embedded repository extension declarations.
- `MODULE.bazel.lock` - intentionally updated Bzlmod resolution and module-extension lock state.
- `tools/bazel/toolchains/embedded_repositories.bzl` - official checksum-backed Arm GNU and Mini404 Linux x86_64 archives.
- `tools/bazel/phase42/BUILD.bazel` - private rules_python provenance test target.
- `tools/bazel/phase42/toolchain_provenance_test.py` - exact declaration, mutation, interpreter, and lock audits.

## Decisions Made

- Restricted embedded compiler and simulator acquisition to the two declared Linux x86_64 archives. Darwin remains unable to positively qualify embedded runtime execution.
- Used a rules_python `single_version_override` because rules_python 2.2.0 does not carry built-in metadata for Python 3.12.10; both supported host archives are exact and checksum-pinned.
- Kept Plan 01 confined to its six declared files. The provenance test follows its source runfile symlink to validate live checkout declarations without changing Plan 02-owned toolchain BUILD surfaces.

## Verification Evidence

- TDD RED failed because `@rules_python` was undeclared before implementation; the same target passes after the declarations were added.
- `bazel test //tools/bazel/phase42:toolchain_provenance_tests --nocache_test_results` passed repeatedly under Python 3.12.10.
- Lock SHA-256 remained `a1f4066675568f8b24ee2f734ab54f825e68f9650134baadb71e6ff09d3c3320` before, between, and after two uncached ordinary test runs.
- `bazel aquery` identified `rules_python++python+python_3_12_10_aarch64-apple-darwin/bin/python3` as the actual interpreter and contained no `/usr/bin/python3`, `/usr/local/bin/python3`, or Homebrew Python edge.
- `bazel query` resolved both `@arm_gnu_linux_x86_64//:all_files` and `@mini404_linux_x86_64//:runtime_files`, exercising each archive checksum.
- `bazel mod graph --lockfile_mode=error` succeeded with the committed lock state.
- `bun scripts/bright-builds-check.ts all` reported `SUMMARY all findings=0`.
- Required Rust pre-commit sequence passed in order: Cargo format, Clippy with warnings denied, all-target/all-feature build, and all-feature tests.
- YAPF 0.40.2, focused Bazel tests, and `git diff --check` passed after final formatting.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added checksum metadata for Python 3.12.10**

- **Found during:** Task 1 GREEN implementation
- **Issue:** rules_python 2.2.0 rejected Python 3.12.10 because that patch version is absent from its built-in standalone-interpreter metadata.
- **Fix:** Added a `single_version_override` using the official python-build-standalone 20250409 URL template and exact SHA-256 values for Darwin arm64 and Linux x86_64.
- **Files modified:** `MODULE.bazel`, `MODULE.bazel.lock`, `tools/bazel/phase42/toolchain_provenance_test.py`
- **Verification:** The focused test ran as Python 3.12.10, and aquery selected the declared rules_python repository rather than ambient Python.
- **Committed in:** `6c5ea05e4`

**Total deviations:** 1 auto-fixed blocking issue
**Impact on plan:** The override is the narrow compatibility mechanism needed to satisfy the exact Python contract; it adds checksum assurance without changing the planned versions or host boundary.

## Issues Encountered

- The repository `.venv/bin/pre-commit` launcher references a removed Homebrew Python 3.14 dylib. The exact configured YAPF 0.40.2 formatter was run through `uvx`, and every other required check completed normally; the stale local virtualenv was not modified.

## Known Stubs

None. Empty collections and placeholder strings occur only as negative mutation inputs or validation accumulators and do not provide runtime behavior.

## User Setup Required

None - Bazel resolves all declared inputs from checksum-backed repositories.

## Next Phase Readiness

- Plan 02 can consume the locked Arm GNU and Mini404 repositories to define executable toolchains and the canonical Linux platform.
- Darwin host validation proves declarations and interpreter provenance only; it does not claim embedded compiler or Mini404 runtime qualification.

## Self-Check: PASSED

- All six Plan 01 implementation files and this summary exist at their expected paths.
- TDD commits `6fd9ce003` and `6c5ea05e4` exist in repository history.
- Plan 02-owned toolchain BUILD files have no diff, and the orchestrator-owned `.planning/config.json` change remains unstaged.

***

*Phase: 42-truthful-bazel-graph-and-executable-mini-toolchain*
*Completed: 2026-08-03*
