# Project Milestones: Prusa Firmware Buddy Rust Port

## v1.0 Rust Port Evidence Foundation (Shipped: 2026-06-15)

**Delivered:** Source-backed Rust+Bazel rewrite evidence foundation with clean v1.0 archival metadata and explicit non-local cutover gates preserved.

**Phases completed:** 1-12 (38 plans, 81 tasks)

**Key accomplishments:**

- Froze the existing firmware reference surface through supported-matrix, reference-capture, safety-envelope, and concern-ledger evidence.
- Made Bazel and `just` the authoritative Rust-port workflow surface for builds, generator checks, verifier labels, and release-facing artifact scaffolding.
- Added typed Rust contracts for product profiles, board/runtime/FreeRTOS boundaries, printing, safety, storage/resources, GUI, network, and auxiliary-controller parity domains.
- Built deterministic verifier scripts, regression tests, Bazel labels, and `just` facades for each subsystem evidence slice through Phase 11 aggregate verification.
- Mapped all 30 v1 requirements to source-backed evidence, retained-code posture, reference-comparison rows, and explicit cutover blockers.
- Closed milestone metadata drift in Phase 12 so v1.0 can be archived with a passed audit and no local evidence overclaims.

**Stats:**

- 299 files changed
- 66,737 inserted lines across planning artifacts, verifier scripts, manifests, Bazel/just wiring, and Rust evidence contracts
- 12 phases, 38 plans, 81 tasks
- 14 days from initial project setup to archive (2026-06-02 → 2026-06-15)

**Git range:** `067108c37` → `174a92850`

**What's next:** v1.1 Cutover Evidence Hardening should turn the remaining non-local gates into durable CI, simulator, hardware, release-candidate, signing, retained-code acceptance, and maintainer-review workflows.

---
