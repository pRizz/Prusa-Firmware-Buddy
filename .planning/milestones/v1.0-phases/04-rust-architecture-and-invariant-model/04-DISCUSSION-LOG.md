---
generated_by: gsd-discuss-phase
lifecycle_mode: yolo
phase_lifecycle_id: 4-2026-06-03T12-43-57
generated_at: 2026-06-03T12:43:57.000Z
---

# Phase 4 Discussion Log

## Auto-Selected Gray Areas

- Rust workspace boundaries: selected dependency-free Cargo workspace with pure domain crate plus thin application, board adapter, and runtime adapter crates.
- Invariant scope: selected product/board/MCU/bootloader/feature, storage schema/migration, artifact name/kind, and protocol registration/connection invariants.
- Verification path: selected real Cargo checks routed through Bazel/`just`, with Phase 4 verifier as the aggregate command.

## Recommended Answers Applied

- Keep C/C++/CMake behavior as the reference source, but make Rust domain constructors the first place invalid combinations are rejected.
- Avoid adding `rules_rust` during this phase; the existing repo-owned shell rule is enough to expose Rust checks through Bazel without broad build-system churn.
- Treat adapter crates as typed boundaries only. They should not contain unsafe code, HAL calls, RTOS startup, or FFI until Phase 5.

## Deferred Ideas

- Embedded Rust target/toolchain integration.
- Retained foreign-code inventory and unsafe audit.
- Runtime boot, FreeRTOS task orchestration, simulator flows, and hardware evidence.

---

*Phase: 04-rust-architecture-and-invariant-model*
