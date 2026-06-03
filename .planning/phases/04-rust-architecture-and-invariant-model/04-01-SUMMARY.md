---
phase: 04-rust-architecture-and-invariant-model
plan: 01
subsystem: rust-architecture
tags: [rust, bazel, invariants, verification]
provides:
  - Rust Cargo workspace
  - Pure domain invariant model
  - Thin application and adapter boundary crates
  - Phase 4 Bazel/just verification surface
requirements-completed: [RUST-01, RUST-02, RUST-05, VERF-02]
generated_by: gsd-execute-plan
lifecycle_mode: yolo
phase_lifecycle_id: 4-2026-06-03T12-43-57
generated_at: 2026-06-03T12:43:57Z
completed: 2026-06-03
---

# Phase 4 Plan 01 Summary

## Accomplishments

- Added a root Cargo workspace with `buddy-domain`, `buddy-application`, `buddy-board-adapter`, and `buddy-runtime-adapter`.
- Added pure Rust domain invariants for supported printer/board/MCU/bootloader combinations, feature ownership, storage keys/schema migrations, artifact names/kinds, and Connect registration state transitions.
- Added focused Rust tests with Arrange/Act/Assert coverage for constructors, state-machine transitions, artifact parsing, migration policy, and application artifact policy.
- Replaced the Phase 2 `rust_firmware` placeholder with a real Rust build workflow and added individual Bazel labels for Rust format, lint, tests, docs, and build.
- Added `just` recipes for Phase 4 verification and individual Rust checks.

## Files Created/Modified

- `Cargo.toml`, `Cargo.lock`
- `rust/crates/domain/**`
- `rust/crates/application/**`
- `rust/crates/board-adapter/**`
- `rust/crates/runtime-adapter/**`
- `tools/bazel/rust_workflow.sh`
- `tools/bazel/phase4_verify.py`
- `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `justfile`, `.gitignore`

## Verification

- `cargo fmt --all -- --check`
- `cargo clippy --all-targets --all-features -- -D warnings`
- `cargo build --workspace --all-features`
- `cargo test --all-features`
- `cargo doc --workspace --all-features --no-deps`
- `python3 tools/bazel/phase4_verify.py --all`
- `bazel query "//tools/bazel:phase4_verify + //tools/bazel:rust_format_check + //tools/bazel:rust_lint + //tools/bazel:rust_unit_tests + //tools/bazel:rust_docs + //tools/bazel:rust_build + //tools/bazel:rust_firmware"`
- `just phase4-verify`

## Deferred

- Phase 5 owns unsafe, FFI, HAL, RTOS, linker, startup, retained-code inventory, and embedded target toolchain integration.

---

*Phase: 04-rust-architecture-and-invariant-model*
