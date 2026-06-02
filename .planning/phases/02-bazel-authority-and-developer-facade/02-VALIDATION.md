---
generated_by: gsd-plan-phase
lifecycle_mode: yolo
phase_lifecycle_id: 2-2026-06-02T20-31-42
generated_at: 2026-06-02T20:31:42.861Z
---

# Phase 2 Validation

## Requirement Mapping

| Requirement | Validation |
|-------------|------------|
| BAZL-01 | `MODULE.bazel` exists, `.bazelrc` exposes product configs, registered toolchain labels exist for Rust, C/C++, ASM, and assets, and product platforms are queryable. |
| BAZL-02 | Bazel target labels exist for Rust firmware, retained foreign code, generated assets, host tools, unit tests, simulator inputs, and release packages. The targets are dry-run reference contracts in this phase. |
| BAZL-04 | Root `justfile` recipes exist for bootstrap, build, test, format, lint, generated-file checks, simulator/parity checks, release packaging, and Phase 2 verification. |

## Automated Checks

- `python3 tools/bazel/phase2_verify.py`
- `bazel query "//tools/bazel/... + //platforms/..."`
- `just --list`
- `git diff --check`

## Acceptance Criteria

- Required root Bazel files exist.
- Toolchain labels are registered in `MODULE.bazel`.
- Host and embedded platform labels can be queried.
- Workflow category labels can be queried.
- `just --list` shows the required recipes.
- Heavy reference commands are opt-in behind `BUDDY_BAZEL_EXECUTE_REFERENCE=1`.

## Explicit Non-Goals

- No firmware binary, release package, or simulator parity output is required from Phase 2.
- No real Rust firmware crate is required from Phase 2.
- No hardware validation is required from Phase 2.
