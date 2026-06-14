---
phase: 11-parity-pyramid-and-cutover-evidence
plan: "03"
phase_name: "Parity Pyramid and Cutover Evidence"
plan_name: "Reference Comparison Manifest and Cutover Evidence Contracts"
subsystem: "verification"
status: "complete"
lifecycle_mode: "yolo"
execution_mode: "yolo/autonomous"
phase_lifecycle_id: "11-2026-06-14T18-48-49"
plan_generated_at: "2026-06-14T19:05:56Z"
generated_at: "2026-06-14T20:33:41Z"
requirements_completed:
  - VERF-01
  - VERF-03
tags:
  - bazel
  - rust
  - parity
  - cutover
  - evidence
dependency_graph:
  requires:
    - "11-01"
  provides:
    - "phase11_reference_comparisons"
    - "cutover_evidence_domain_contracts"
  affects:
    - "tools/bazel/manifests/phase11_reference_comparisons.json"
    - "rust/crates/domain/src/cutover.rs"
    - "rust/crates/domain/src/lib.rs"
tech_stack:
  added:
    - "Phase 11 reference comparison JSON manifest"
    - "Pure Rust cutover evidence domain contracts"
  patterns:
    - "Guarded reference-only comparison claims"
    - "TDD for domain invariant contracts"
key_files:
  created:
    - "tools/bazel/manifests/phase11_reference_comparisons.json"
    - "rust/crates/domain/src/cutover.rs"
    - ".planning/phases/11-parity-pyramid-and-cutover-evidence/11-03-SUMMARY.md"
  modified:
    - "rust/crates/domain/src/lib.rs"
decisions:
  - "Represent every VERF-03 comparison row as normalized semantic evidence with guarded reference-only execution."
  - "Keep byte-identity claims available only through an explicit Rust contract requiring fixture and normalization data."
  - "Classify simulator, hardware, manual, and retained-code evidence as non-local so local cutover proofs cannot overclaim."
metrics:
  duration: "8m12s"
  completed_date: "2026-06-14"
  tasks_completed: 2
  files_changed: 4
---

# Phase 11 Plan 03: Reference Comparison Manifest and Cutover Evidence Contracts Summary

Nine guarded reference-comparison rows plus pure Rust cutover contracts for evidence scope, comparison claims, and retained-code disposition.

## Accomplishments

- Created `tools/bazel/manifests/phase11_reference_comparisons.json` with exactly nine VERF-03 reference comparison rows covering product artifacts, generated resources, storage migrations, protocol traces, G-code behavior fixtures, UI display-state fixtures, network/TLS/API behavior, auxiliary-controller flows, and release metadata.
- Kept all reference comparison claims normalized and guarded with `reference-only-guarded`, `BUDDY_BAZEL_EXECUTE_REFERENCE=1`, `byte_identity_claim: false`, name-only/redacted secret handling, and explicit non-local evidence requirements.
- Added `rust/crates/domain/src/cutover.rs` with pure Rust contracts for cutover evidence row IDs, proof scopes, evidence classes, cutover status, reference comparison kinds, reference comparison contracts, cutover criteria, and retained-code disposition.
- Exported the cutover module from `rust/crates/domain/src/lib.rs` and added invariant errors for invalid cutover IDs, proof scopes, and overclaiming comparison contracts.

## Task Commits

| Task | Commit | Description |
| ---- | ------ | ----------- |
| 1 | `c8cc54b58` | `feat(11-03): add reference comparison manifest` |
| 2 RED | `1e6754bd8` | `test(11-03): add failing tests for cutover evidence contracts` |
| 2 GREEN | `ff34af3ec` | `feat(11-03): implement cutover evidence contracts` |

## Verification

| Command | Result |
| ------- | ------ |
| `python3 tools/bazel/phase11_verify.py --comparison-only` | Passed: `Phase 11 parity/cutover verification passed` |
| `cargo fmt --all -- --check` | Passed |
| `cargo clippy --all-targets --all-features -- -D warnings` | Passed |
| `cargo build --all-targets --all-features` | Passed |
| `cargo test --all-features` | Passed: 136 tests across Rust crates and doc-test harnesses |
| `python3 tools/bazel/phase11_verify.py --rust-only` | Passed: `Phase 11 parity/cutover verification passed` |

## Acceptance Evidence

- `rust/crates/domain/src/cutover.rs` exists and exposes all plan-required public types.
- `rust/crates/domain/src/lib.rs` exports `pub mod cutover;`.
- Optional fixture and normalization fields use `maybe_fixture_id` and `maybe_normalization_rule`.
- No unsafe code markers were found in `rust/crates/domain/src/cutover.rs`.
- The reference comparison manifest contains all nine required row IDs and all required guarded comparison fields.

## Deviations from Plan

None - plan executed exactly as written.

## Auth Gates

None.

## Known Stubs

None detected.

## Threat Flags

None. This plan introduced a JSON comparison manifest and pure Rust domain contracts only; it did not add network endpoints, auth paths, file-access patterns, or schema trust boundaries.

## Residual Risk

Reference demotion remains blocked by design until later Plan 11 work supplies simulator, hardware, live-network, release-candidate, retained-code, and final cutover decision evidence.

## Self-Check: PASSED

- Found created files: `tools/bazel/manifests/phase11_reference_comparisons.json`, `rust/crates/domain/src/cutover.rs`, and `.planning/phases/11-parity-pyramid-and-cutover-evidence/11-03-SUMMARY.md`.
- Found task commits: `c8cc54b58`, `1e6754bd8`, and `ff34af3ec`.
