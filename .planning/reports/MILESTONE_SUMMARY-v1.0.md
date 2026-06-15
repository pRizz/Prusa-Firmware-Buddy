# Milestone v1.0 - Project Summary

**Generated:** 2026-06-15
**Purpose:** Team onboarding and project review

---

## 1. Project Overview

Milestone v1.0 established the control plane for a behavior-parity Rust+Bazel rewrite of
Prusa-Firmware-Buddy. The existing C/C++/CMake firmware remains the reference oracle, while
the new Rust+Bazel surface now has product matrices, typed domain contracts, retained-code
boundaries, deterministic verifiers, and cutover evidence manifests.

The milestone did not claim final production cutover. Instead, it created the evidence
structure needed to decide whether cutover is allowed. Local deterministic evidence is marked
separately from simulator, hardware, live network, release-candidate, storage-media, signing,
MMU, RS485, toolchanger, and manual proof that still requires non-local validation.

Final state:

| Metric | Value |
| --- | --- |
| Milestone | v1.0 |
| Status | Complete |
| Phases | 11 / 11 complete |
| Plans | 37 / 37 complete |
| v1 requirements mapped | 30 / 30 |
| v1 requirements marked complete | 30 / 30 |
| Verification reports | 11 / 11 passed |

## 2. Architecture and Technical Decisions

- **Bazel became the authoritative planned build graph.** `MODULE.bazel`, `.bazelrc`,
  `BUILD.bazel`, platform labels, toolchain labels, and `tools/bazel/` workflows now model
  firmware products, generated assets, retained code, verifiers, and facade commands.
- **`justfile` became the developer facade.** Common workflows are exposed through stable
  commands such as phase verifier entrypoints and Rust workflow dispatch.
- **Rust was introduced as a typed firmware model layer.** The workspace under `rust/` has
  `domain`, `board-adapter`, `runtime-adapter`, and `application` crates.
- **Functional core / imperative shell is the governing structure.** Pure product, artifact,
  safety, printing, storage, resource, GUI, network, auxiliary, and cutover contracts live in
  Rust domain types; hardware, RTOS, FFI, MMIO, DMA, linker, allocator, panic, and tasking
  surfaces stay behind adapter contracts.
- **Retained foreign code is explicit.** C, C++, ASM, generated, vendor, HAL, RTOS, network,
  filesystem, and release surfaces are inventoried with retention reasons, ownership
  boundaries, and replacement posture.
- **No local proof overclaims physical behavior.** Thermal, motion, watchdog, crash recovery,
  physical display, touch/encoder, media, live TLS, RS485, MMU, toolchanger, and production
  release proof are classified as non-local evidence gates.
- **Known defects and fragile areas became tracked dispositions.** Concern ledgers and
  phase-specific disposition manifests keep known issues visible instead of silently carrying
  or fixing them.

## 3. Phases Delivered

| Phase | Name | Status | Delivered |
| --- | --- | --- | --- |
| 1 | Reference Baseline and Safety Envelope | Complete | Supported matrix, reference-capture catalog, concern ledger, safety envelope, and phase-local verifier. |
| 2 | Bazel Authority and Developer Facade | Complete | Root Bazel module/config, product platforms, reference toolchain labels, `justfile`, and Phase 2 verifier. |
| 3 | Artifact and Generator Parity | Complete | Artifact packaging scaffolding, representative outputs, generator/drift helpers, comparison tooling, and Bazel/just workflows. |
| 4 | Rust Architecture and Invariant Model | Complete | Rust workspace, domain/application/adapter crates, typed product/artifact/protocol invariants, and Rust verification wiring. |
| 5 | Foreign Code, Unsafe, and Runtime Boundary | Complete | Foreign-code inventory, unsafe-boundary audit, board/runtime/FreeRTOS contracts, and aggregate verifier. |
| 6 | Printing Core, Safety, and Feature Gates | Complete | Printing, safety/recovery/fatal, and product feature-gate manifests plus typed Rust contracts and verifier tests. |
| 7 | Persistence, Storage, and Resource Compatibility | Complete | Config store, storage media, generated resource, redacted fixture, credential-redaction, and resource domain contracts. |
| 8 | Local Interface and Workflow Parity | Complete | GUI workflow/layout manifests, display and UI evidence contracts, UI spec, verifier tests, and `phase8-verify`. |
| 9 | Network, Web Services, and Transfers | Complete | Connect, WUI/PrusaLink, transfer, TLS/secret, proxy, telemetry, negative network fixtures, and verifier wiring. |
| 10 | Auxiliary Controllers and Expansion Ecosystem | Complete | Puppy, Dwarf, ModularBed, xBuddy Extension, MMU, Modbus/RS485, toolchanger, build/update manifests, and Rust auxiliary contracts. |
| 11 | Parity Pyramid and Cutover Evidence | Complete | Parity pyramid, requirement evidence, reference comparison, cutover readiness, retained-code justification manifests, and aggregate sign-off. |

## 4. Requirements Coverage

The milestone mapped all 30 v1 requirements to phase evidence.

- **BASE-01 through BASE-04:** Complete through Phase 1 baseline, reference capture,
  intentional-delta, and safety envelope artifacts.
- **BAZL-01, BAZL-02, BAZL-04:** Complete through Phase 2 Bazel authority and `just`
  facade work.
- **BAZL-03 and BAZL-05:** Covered by Phase 3 artifact/generator parity scaffolding and
  drift/reference comparison gates. Final release-candidate byte parity remains a non-local
  cutover gate, not a local Phase 3 claim.
- **RUST-01 through RUST-05:** Complete through the Rust workspace, typed invariant model,
  retained-code inventory, unsafe audit, and Rust verification commands.
- **CORE-01 through CORE-05:** Complete as source-backed runtime, FreeRTOS, printing,
  safety, and feature-gate contracts. Physical printer behavior remains gated by later
  simulator/hardware evidence.
- **IFCE-01 through IFCE-06:** Complete as source-backed GUI, Connect, WUI, transfer,
  persistence, resource, and auxiliary-controller contracts, with live/hardware proof
  preserved as non-local evidence.
- **VERF-01 through VERF-05:** Complete through Phase 11 evidence manifests, reference
  comparison rows, cutover readiness policy, retained-code justifications, Bazel/just
  aliases, and aggregate verification.

## 5. Key Decisions Log

- **Big Bang migration posture.** The roadmap leads to a full replacement cutover rather
  than incremental production dual ownership.
- **Behavior parity is the acceptance baseline.** Current supported printers, release
  artifacts, generated resources, tests, network behavior, storage, and safety-critical
  behavior remain in scope unless explicitly descoped.
- **Bazel primary now.** CMake can remain as reference/comparison input, but not the
  authoritative target state.
- **No silent retained-code islands.** Foreign/vendor/generated/runtime code must have named
  boundaries, reasons, and evidence strategy.
- **No silent defect drift.** Known concerns are either preserved temporarily, fixed with
  evidence, or deferred explicitly.
- **Typed Rust contracts first.** Invalid product, feature, safety, storage, network,
  auxiliary, and cutover states should be rejected by constructors and enums rather than
  revalidated as unchecked primitives.
- **Local verification is deterministic and bounded.** Phase verifiers prove manifests,
  source links, Rust contracts, Bazel labels, and facade wiring; they do not substitute for
  hardware labs or live-service certification.
- **Cutover is still blocked until non-local proof exists.** Phase 11 deliberately keeps
  reference demotion unavailable until simulator, hardware, live network/TLS, release,
  signing, storage media, MMU, RS485, and toolchanger gates have evidence.

## 6. Tech Debt and Deferred Items

- Simulator and hardware smoke gates still need real execution evidence.
- Live Prusa Connect, WebSocket, TLS, transfer, proxy, telemetry, and WUI behavior need
  environment-backed validation.
- Release artifact byte identity, signing, `.bbf` / `.dfu` / map/provenance parity, and
  generated resource parity need release-candidate proof.
- Storage migration, USB/internal media, flash wear, semihosting, and credentials handling
  need hardware or simulator-backed proof.
- MMU, RS485, Dwarf, ModularBed, xBuddy Extension, toolchanger, dock/tool offset, flashing,
  and long-running update flows need physical or high-fidelity simulator evidence.
- Several retained-code islands are accepted or deferred rather than replaced. They remain
  explicit cutover evidence inputs.
- The roadmap progress table contains a stale Phase 9 progress row, while `gsd-tools`
  progress, phase artifacts, summaries, and verification reports show Phase 9 complete.
  This is documentation drift worth cleaning before starting v2.

## 7. Getting Started

Good entry points for a new contributor:

- **Project intent:** `.planning/PROJECT.md`
- **Scope and traceability:** `.planning/REQUIREMENTS.md`
- **Phase map:** `.planning/ROADMAP.md`
- **Current state:** `.planning/STATE.md`
- **Architecture map:** `.planning/codebase/ARCHITECTURE.md`
- **Known concerns:** `.planning/codebase/CONCERNS.md`
- **Rust domain model:** `rust/crates/domain/src/`
- **Board/runtime boundaries:** `rust/crates/board-adapter/src/` and
  `rust/crates/runtime-adapter/src/`
- **Verifier entrypoints and manifests:** `tools/bazel/`
- **Developer facade:** `justfile`

Useful local checks from the completed milestone include:

- `just phase11-verify`
- `python3 tools/bazel/phase11_verify.py --quick`
- `python3 tools/bazel/phase11_verify_test.py`
- `cargo fmt --all -- --check`
- `cargo clippy --all-targets --all-features -- -D warnings`
- `cargo build --all-targets --all-features`
- `cargo test --all-features`

## Recommended Next Milestone

The sensible v2 direction is:

**Milestone v2.0 - Evidence Execution and Cutover Hardening**

Goal: convert the v1 evidence framework from source-backed contracts into executed,
auditable proof for the riskiest non-local gates.

Suggested phases:

1. **Documentation drift and evidence hygiene.** Fix stale roadmap/status rows, archive or
   baseline v1 artifacts, and make cutover blockers queryable from one report.
2. **Simulator parity execution.** Run the parity pyramid against simulator flows for
   startup, G-code, GUI states, storage migrations, transfers, and selected failure paths.
3. **Hardware smoke gate harness.** Define and run a small supported-printer hardware matrix
   for startup, watchdog, thermal/motion safe states, media, UI input, and crash recovery.
4. **Live network and TLS qualification.** Validate Connect, WUI, TLS, telemetry, transfers,
   proxy limits, and negative network fixtures against controlled environments.
5. **Release-candidate artifact qualification.** Produce signed artifacts, generated
   resource bundles, auxiliary packages, provenance, and reference comparisons with explicit
   pass/fail deltas.

This direction is stronger than starting broad feature work because v1 already built the
contracts. The next bottleneck is evidence: proving the contracts under simulator, hardware,
live service, and release conditions.

---

## Stats

- **Timeline:** 2026-06-02 to 2026-06-14
- **Phases:** 11 / 11 complete
- **Plans:** 37 / 37 complete
- **Commits since 2026-06-02:** 254
- **Diff since 2026-06-02:** 276 files changed, 64047 insertions
- **Contributors:** Peter Ryszkiewicz
