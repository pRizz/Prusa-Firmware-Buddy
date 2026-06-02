---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 2-2026-06-02T20-31-42
generated_at: 2026-06-02T20:31:42.861Z
---

# Phase 2: Bazel Authority and Developer Facade - Discussion Log

> **Audit trail only.** Decisions are captured in `02-CONTEXT.md`.

**Date:** 2026-06-02T20:31:42.861Z
**Phase:** 2-Bazel Authority and Developer Facade
**Mode:** Yolo
**Areas discussed:** Bazel root, platforms, toolchains, workflow targets, `justfile`, verification

---

## Bazel Root

| Option | Description | Selected |
|--------|-------------|----------|
| Root Bazel workspace now | Add root `MODULE.bazel`, `.bazelrc`, and `BUILD.bazel`. | yes |
| Keep Bazel vendored-only | Leave Bazel files only inside third-party directories. | |
| Delay Bazel until Rust crates exist | Wait for Phase 4 before adding root Bazel. | |

**User's choice:** Auto-selected root Bazel workspace now.
**Notes:** This matches the project decision that Bazel is primary from the start.

## Product Platforms

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit constraint platforms | Model runtime, printer, board, and MCU constraints. | yes |
| One generic embedded platform | Use a single embedded platform until compiler integration exists. | |
| Reuse CMake presets only | Keep product selection outside Bazel. | |

**User's choice:** Auto-selected explicit constraint platforms.
**Notes:** The labels make host versus embedded targets visible immediately.

## Toolchains

| Option | Description | Selected |
|--------|-------------|----------|
| Registered metadata toolchains | Register Rust, C/C++, ASM, and asset-generator toolchain types with placeholder metadata. | yes |
| Full compiler toolchains now | Wire all ARM/Rust compilers and linkers in Phase 2. | |
| No toolchains until Rust phase | Defer all toolchain labels to Phase 4. | |

**User's choice:** Auto-selected registered metadata toolchains.
**Notes:** The contract exists now; concrete compiler integration belongs to later phases.

## Workflow Targets

| Option | Description | Selected |
|--------|-------------|----------|
| Bazel-owned workflow labels | Add explicit labels for bootstrap, build, tests, generated checks, simulator/parity, and release packages. | yes |
| Only `just` recipes | Put all workflow names only in `justfile`. | |
| Only reference scripts | Keep direct Python/CMake commands as the developer entrypoint. | |

**User's choice:** Auto-selected Bazel-owned workflow labels.
**Notes:** `just` wraps Bazel; it does not replace the Bazel graph.

## `justfile`

| Option | Description | Selected |
|--------|-------------|----------|
| Checked facade | Add root recipes that call Bazel labels. | yes |
| Shell-only facade | Add recipes that call Python/CMake directly. | |
| No facade | Require developers to remember Bazel labels. | |

**User's choice:** Auto-selected checked facade.
**Notes:** This satisfies the project-level `justfile` requirement without duplicating command logic.

## Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Lightweight graph checks | Verify required files, strings, Bazel queryability, `just --list`, and whitespace. | yes |
| Full firmware build | Run all current firmware builds through Bazel. | |
| Documentation only | Add files with no automated check. | |

**User's choice:** Auto-selected lightweight graph checks.
**Notes:** Heavy builds and artifact parity remain downstream work.
