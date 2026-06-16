---
generated_by: gsd-research-phase
lifecycle_mode: yolo
phase_lifecycle_id: 2-2026-06-02T20-31-42
generated_at: 2026-06-02T20:31:42.861Z
---

# Phase 2 Research: Bazel Authority and Developer Facade

## Findings

- The repository had no root `MODULE.bazel`, `.bazelrc`, or root-owned Bazel graph before this phase.
- Existing current-source build truth is CMake/Python: `CMakeLists.txt`, `ProjectOptions.cmake`, `CMakePresets.json`, `utils/presets/presets.json`, and `utils/build.py`.
- Phase 1 already captured the supported printer/board/MCU/artifact matrix and reference command catalog; Phase 2 should project that matrix into Bazel labels.
- Local tools available for verification: `bazel`, `bazelisk`, and `just`.
- `buildifier` is not available locally.
- Bazel 9.1 does not provide native `sh_binary`; a repo-local Starlark executable rule avoids adding an external dependency just to bootstrap shell targets.

## Phase 2 Shape

The smallest useful authority surface is:

- Root Bzlmod entrypoint: `MODULE.bazel` plus generated `MODULE.bazel.lock`.
- Bazel config: `.bazelrc` with host and product configs.
- Root build entrypoint: `BUILD.bazel` for reference-source filegroups and top-level aliases.
- Platforms: `platforms/BUILD.bazel` with runtime, printer, board, and MCU constraints.
- Toolchains: `tools/bazel/toolchains/BUILD.bazel` and `reference_toolchain.bzl` with Rust, C/C++, ASM, and asset-generator toolchain types.
- Workflows: `tools/bazel/BUILD.bazel` and `reference_contract.sh` for bootstrap, firmware build, Rust firmware, retained foreign code, generated assets, host tools, unit tests, simulator inputs, simulator parity, release packages, format, lint, generated checks, and phase verification.
- Developer facade: root `justfile` calling Bazel labels.

## Deferred Work

- Real Rust crate graph and compiler toolchain integration: Phase 4.
- Deterministic release packages, generator ownership, and artifact drift checks: Phase 3.
- Retained C/C++/ASM/vendor safe boundary wrappers: Phase 5.
- Full simulator, hardware, and cutover evidence: Phase 11.

## Verification Implications

Phase 2 verification should be graph and facade focused. It should not run heavy reference commands by default, and it should not mark release artifact parity as complete.
