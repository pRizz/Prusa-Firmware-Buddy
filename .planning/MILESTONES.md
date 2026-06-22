# Project Milestones: Prusa Firmware Buddy Rust Port

## v1.1 Cutover Evidence Hardening (Shipped: 2026-06-22)

**Delivered:** Durable cutover-evidence gate capability across CI, simulator, hardware, live-service, release-candidate, retained-code, upstream-result, and maintainer-review surfaces without promoting external proof or final demotion before valid inputs exist.

**Phases completed:** 10 phases, 13 plans, 30 tasks

**Key accomplishments:**

- Added repo-owned CI evidence workflow, machine-readable manifest output, artifact retention, and Bazel/just verifier facades for aggregate cutover gates.
- Made simulator, hardware/safety/media, live network/TLS/WUI/transfer/proxy, and release-candidate evidence reviewable through phase-owned contracts, input templates, verifiers, and redaction/path guards.
- Replaced the empty release-candidate identity target with Phase-20-backed release-environment input and result-manifest flows while rejecting smoke fixtures, template rows, secrets, path escapes, and underclassified proof.
- Hardened retained-code acceptance and final cutover review so reference demotion consumes machine-readable upstream results and remains blocked without valid evidence and maintainer decisions.
- Closed v1.1 audit gaps with Phase 19 aggregate evidence, Phase 21 upstream-result consumption, Phase 22 metadata reconciliation, validation signoff, verification dossier, and a passed milestone audit rerun.

**Stats:**

- 290 files changed
- 41,905 inserted lines across planning artifacts, verifier scripts, manifests, Bazel/just wiring, and evidence contracts
- 10 phases, 13 plans, 30 tasks
- 7 days from first v1.1 phase work to archive (2026-06-16 -> 2026-06-22)

**Git range:** `174a92850` -> `b1b57af47`

**What's next:** Start the next milestone from a clean requirements surface. The likely next decision is whether to execute and accept the external evidence packets and maintainer approvals needed for final cutover readiness, or to scope another hardening milestone first.

---

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
