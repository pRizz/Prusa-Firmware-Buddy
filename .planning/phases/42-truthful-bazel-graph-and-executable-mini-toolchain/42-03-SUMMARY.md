---
phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
plan: 03
subsystem: build-tooling
tags: [bazel, rust, arm-gnu, cortex-m4, hard-float, elf, toolchains]
requires:
  - phase: 42-truthful-bazel-graph-and-executable-mini-toolchain
    plan: 02
    provides: "Exact MINI hard-float platform and Linux-only executable qualification provider"
provides:
  - "Genuine no_std Rust object linked into a Cortex-M4 hard-float ARM ELF"
  - "Bazel-declared ELF, GNU map, JSON report, and four pinned Arm inspection actions"
  - "Deterministic Darwin analysis rejection with no embedded target actions"
affects: [42-04-platform-rejection, 42-05-truthful-facade, 46-first-safe-boot-link]
tech-stack:
  added: []
  patterns: [resolved-toolchain action graph, inspection-gated report, link-only Arm runtime inputs]
key-files:
  created:
    - tools/bazel/phase42/arm_link_smoke.bzl
    - tools/bazel/phase42/arm_link_smoke.ld
    - tools/bazel/phase42/arm_link_smoke.rs
  modified:
    - MODULE.bazel.lock
    - tools/bazel/phase42/BUILD.bazel
    - tools/bazel/phase42/arm_link_smoke_test.py
    - tools/bazel/phase42/embedded_toolchain_contract_test.py
    - tools/bazel/toolchains/BUILD.bazel
    - tools/bazel/toolchains/embedded_repositories.bzl
    - tools/bazel/toolchains/embedded_toolchain.bzl
key-decisions:
  - "Expose the complete checksum-backed Arm archive runtime through EmbeddedToolchainInfo, but add it only to the GCC link action inputs."
  - "Require readelf, objdump, nm, and size inspections to succeed before writing the phase42-arm-link-smoke report."
  - "Treat native Darwin output solely as expected-failure host-policy evidence; Linux x86_64 remains the only positive qualification host."
patterns-established:
  - "Target work flows Rust compile -> Arm GCC link -> four Arm inspections -> non-empty JSON report."
  - "The report names the smoke evidence class, exact target tuple, tool versions, and Bazel output paths without claiming firmware acceptance."
requirements-completed: [BUILD-03, TOOL-01]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 42-2026-08-03T19-34-09
generated_at: 2026-08-03T21:46:06Z
duration: 47min
completed: 2026-08-03
---

# Phase 42 Plan 03: Genuine Cortex-M4 Hard-Float Link Smoke Summary

**Resolved Rust 1.85.0 and Arm GNU 13.2.Rel1 actions now produce and inspect a real ELF32 ARM hard-float link smoke for the exact MINI platform.**

## Performance

- **Duration:** 47 min
- **Started:** 2026-08-03T20:59:23Z
- **Completed:** 2026-08-03T21:46:06Z
- **Tasks:** 1
- **Files modified:** 10

## Accomplishments

- Added an allocation-free `no_std`/`no_main` Rust entrypoint and dedicated FLASH/RAM linker contract for `_phase42_smoke_entry`.
- Added seven distinct Bazel action classes: Rust compile, Arm GCC link, readelf, objdump, nm, size, and the final non-empty report.
- Proved on canonical Linux x86_64 that the outputs are ELF32 ARM, EABI hard-float, ARMv7E-M, VFPv4-D16, use VFP register arguments, and contain the required entry symbol.
- Preserved deterministic native Darwin rejection during Bazel analysis, before any target action or positive artifact exists.

## Task Commits

1. **Task 1 RED: Add failing ARM link smoke contract** - `0bfd7099e` (test)
2. **Task 1 GREEN: Add genuine ARM link smoke** - `006604fc1` (feat)

## Files Created/Modified

- `tools/bazel/phase42/arm_link_smoke.rs` - Allocation-free Rust smoke entry and panic spin loop.
- `tools/bazel/phase42/arm_link_smoke.ld` - Cortex-M4 FLASH/RAM layout with an explicit entry symbol.
- `tools/bazel/phase42/arm_link_smoke.bzl` - Resolved compile, link, inspection, and report actions.
- `tools/bazel/phase42/BUILD.bazel` - Canonical MINI smoke target and rules_python contract test.
- `tools/bazel/phase42/arm_link_smoke_test.py` - Output, ABI, action, provenance, runtime-file, and mutation contracts.
- `tools/bazel/phase42/embedded_toolchain_contract_test.py` - Regression proof for the Arm runtime provider field and declared archive source.
- `tools/bazel/toolchains/embedded_toolchain.bzl` - Complete Arm archive runtime exported only by the Linux qualification implementation.
- `tools/bazel/toolchains/BUILD.bazel` - Checksum-backed Arm runtime filegroup wired into the Linux toolchain.
- `tools/bazel/toolchains/embedded_repositories.bzl` - File-only recursive Arm archive glob.
- `MODULE.bazel.lock` - Stable lock record for the corrected external repository declaration.

## Decisions Made

- Kept the Rust compile action isolated from the Arm runtime and supplied the complete archive only to the GCC driver link action, minimizing declared inputs while allowing the driver to find its internal linker and support files.
- Made all four binary inspections prerequisites of the report action so metadata cannot be emitted when ABI or symbol proof fails.
- Exposed only ELF, map, and report as default outputs; inspection text remains a named output group and the artifact class stays `phase42-arm-link-smoke`, not firmware or accepted ELF.

## Verification Evidence

### Canonical Linux x86_64 positive qualification

- A disposable `linux/amd64` container running Bazel 9.2.0 built `//tools/bazel/phase42:arm_link_smoke` with `--config=mini --noskip_incompatible_explicit_targets --lockfile_mode=error`.
- Logical output paths:
  - `bazel-out/k8-fastbuild/bin/tools/bazel/phase42/arm_link_smoke.elf` (4,708 bytes)
  - `bazel-out/k8-fastbuild/bin/tools/bazel/phase42/arm_link_smoke.map` (2,769 bytes)
  - `bazel-out/k8-fastbuild/bin/tools/bazel/phase42/arm_link_smoke.report.json` (815 bytes)
- Container output root: `/tmp/phase42-bazel/eab0d61a99b6696edb3d2aff87b585e8/execroot/_main/bazel-out/k8-fastbuild/bin/tools/bazel/phase42/`.
- The report identifies `Rust 1.85.0`, `Arm GNU 13.2.Rel1`, `thumbv7em-none-eabihf`, and `//platforms:mini_buddy_stm32f407vg`.
- `readelf` proves `ELF32`, machine `ARM`, Version5 EABI hard-float, `Tag_CPU_arch: v7E-M`, `Tag_FP_arch: VFPv4-D16`, and `Tag_ABI_VFP_args: VFP registers`.
- `objdump` proves `elf32-littlearm`, architecture `armv7e-m`, and disassembly at `_phase42_smoke_entry`; `nm` places the symbol at `08000000`; `size` reports a non-empty `.text` section.
- `aquery` reports `Phase42RustCompile`, `Phase42ArmLink`, `Phase42ArmReadelf`, `Phase42ArmObjdump`, `Phase42ArmNm`, `Phase42ArmSize`, and `Phase42SmokeReport`.

### Native Darwin arm64 expected-failure rejection

- The user ran the exact smoke build natively in macOS Terminal; it reached Bazel analysis and exited 1 with `unsupported embedded qualification host: detected Darwin-arm64; use canonical Linux x86_64 CI/container`.
- No target action ran: Bazel reported a 0.02-second critical path and one internal process only.
- This is expected-failure host-policy evidence, not positive embedded qualification.

### Repository and regression gates

- `bazel test //tools/bazel/phase42:arm_link_smoke_tests --nocache_test_results --lockfile_mode=error` passed.
- The Plan 01 provenance and Plan 02 embedded-toolchain/host-policy suites passed uncached with lockfile error mode.
- `MODULE.bazel.lock` stayed at SHA-256 `5b18570e4fa8283ef15c861a3d3a8d5a5d94f1e8b41baf6594e3c3bc16e3d4c9` across ordinary focused verification.
- `git diff --check` and `bun scripts/bright-builds-check.ts all` passed with zero findings.
- The required Rust sequence passed in order: `cargo fmt --all`, Clippy for all targets/features with warnings denied, all-target/all-feature build, and all-feature tests.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Exported the complete checksum-backed Arm archive runtime**

- **Found during:** Task 1 GREEN canonical Linux link
- **Issue:** Declaring only `arm-none-eabi-gcc` made the driver executable available but not its internal linker, libraries, specs, and support files, so the real link could not execute hermetically.
- **Fix:** Added `arm_toolchain_files` to the Linux embedded provider and supplied its depset only to `Phase42ArmLink`.
- **Files modified:** `tools/bazel/toolchains/embedded_toolchain.bzl`, `tools/bazel/toolchains/BUILD.bazel`, `tools/bazel/phase42/arm_link_smoke.bzl`, `tools/bazel/phase42/embedded_toolchain_contract_test.py`, `tools/bazel/phase42/arm_link_smoke_test.py`
- **Verification:** Canonical Linux linked and inspected the genuine ELF; focused mutation contracts require the provider, declared filegroup, and link-only input edge.
- **Committed in:** `006604fc1`

**2. [Rule 1 - Bug] Excluded directories from the Plan 01 Arm archive filegroup**

- **Found during:** Task 1 GREEN canonical Linux link
- **Issue:** `glob(["**"], exclude_directories = 0)` admitted directory entries into the runtime filegroup; Bazel action inputs must be files for stable sandboxed compiler-driver execution.
- **Fix:** Changed the checksum-backed repository declaration to `exclude_directories = 1`, updated its lock digest, and added regression coverage.
- **Files modified:** `tools/bazel/toolchains/embedded_repositories.bzl`, `MODULE.bazel.lock`, `tools/bazel/phase42/arm_link_smoke_test.py`
- **Verification:** Focused contracts pass, Bazel lock error mode accepts the committed declaration, the lock hash remains stable, and canonical Linux completes all seven target actions.
- **Committed in:** `006604fc1`

**3. [Rule 1 - Bug] Normalized generated roadmap progress formatting**

- **Found during:** Plan completion metadata update
- **Issue:** The roadmap updater emitted a malformed progress row with a missing separator space and an empty completed-date cell.
- **Fix:** Restored the established table shape with `3/5`, `In Progress`, and `-` values.
- **Files modified:** `.planning/ROADMAP.md`
- **Verification:** Markdown table structure and `git diff --check` pass.
- **Committed in:** Plan metadata commit

**Total deviations:** 3 auto-fixed (1 blocking runtime-input issue, 2 bugs)
**Impact on plan:** The two implementation changes are necessary for the planned hermetic GCC link and preserve the checksum, tool version, Linux-only host boundary, and exact MINI target tuple; the metadata fix only restores the established roadmap format.

## Issues Encountered

- The first Bright Builds run found that the existing untracked negative-host lesson used noncanonical field labels. That single lesson block was normalized so the checker could pass, and `.codex/tasks/lessons.md` remained unstaged as required.

## Known Stubs

None. Empty Python error lists are validation accumulators, not unwired runtime or UI data.

## User Setup Required

None - all positive qualification inputs resolve through Bazel/Bzlmod, while unsupported Darwin is rejected with its prescribed Linux remedy.

## Next Phase Readiness

- Plan 42-04 can build its fail-closed platform matrix around a proven genuine positive MINI control and the existing no-action Darwin host-policy boundary.
- The smoke remains intentionally distinct from the accepted safe-boot firmware ELF owned by Phase 46.

## Self-Check: PASSED

- All ten implementation/deviation files and this summary exist at their expected paths.
- TDD commits `0bfd7099e` and `006604fc1` exist in repository history.
- Summary frontmatter has one opening/closing delimiter pair, and the documentation diff passes `git diff --check`.

***

*Phase: 42-truthful-bazel-graph-and-executable-mini-toolchain*
*Completed: 2026-08-03*
