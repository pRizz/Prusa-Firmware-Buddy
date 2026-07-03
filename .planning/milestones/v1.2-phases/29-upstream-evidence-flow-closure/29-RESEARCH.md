# Phase 29: Upstream Evidence Flow Closure - Research

**Researched:** 2026-06-25 [VERIFIED: system date and `.planning/phases/29-upstream-evidence-flow-closure/29-CONTEXT.md`]
**Domain:** Python evidence verifiers, JSON evidence row contracts, Bazel/just verification wiring, and GSD milestone metadata [VERIFIED: `.planning/ROADMAP.md`; `.planning/v1.2-MILESTONE-AUDIT.md`]
**Confidence:** HIGH [VERIFIED: `tools/bazel/phase23_simulator_evidence_execution.py`; `tools/bazel/phase24_hardware_media_safety_evidence_execution.py`; `tools/bazel/phase25_live_service_evidence_execution.py`; `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase28_final_readiness_packet.py`]

<user_constraints>
## User Constraints (from CONTEXT.md)

Phase 29 must close the v1.2 audit gap by making real Phase 23, Phase 24, and Phase 25 upstream evidence rows flow through Phase 26 into the Phase 28 final readiness packet. It must preserve fail-closed quick behavior, secret-safe artifact references, source-ref and lifecycle validation, and the separate reference-demotion decision boundary. [VERIFIED: `.planning/phases/29-upstream-evidence-flow-closure/29-CONTEXT.md`]

Locked decisions:

- Phase 26 accepts explicit upstream row inputs for Phase 23 simulator, Phase 24 hardware/media/safety, and Phase 25 live-service evidence. [VERIFIED: `29-CONTEXT.md` D-01]
- Phase 26 validates criterion identity, requirement IDs, source phase, lifecycle/source refs, redaction status, source-ref status, artifact refs, and status vocabulary before using those rows. [VERIFIED: `29-CONTEXT.md` D-01]
- Absent real upstream row inputs keep fail-closed pending/blocked placeholders. [VERIFIED: `29-CONTEXT.md` D-02]
- Phase 25's `final-live-service-evidence` row must map explicitly to Phase 18's canonical `final-live-network-transfer-evidence` criterion. [VERIFIED: `29-CONTEXT.md` D-03; `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json`]
- Phase 28 remains a consumer of Phase 26 row tables and Phase 27 handoff outputs. [VERIFIED: `29-CONTEXT.md` D-07]
- Reference demotion remains separate and cannot be inferred from evidence status. [VERIFIED: `29-CONTEXT.md` D-08; `tools/bazel/phase28_final_readiness_packet.py`]
- Summary requirement metadata and Nyquist validation metadata must be reconciled after verification. [VERIFIED: `29-CONTEXT.md` D-09]
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ACPT-01 | All v1.2 replacement acceptance criteria have machine-readable pass/fail/exception rows tied to retained artifacts. [VERIFIED: `.planning/REQUIREMENTS.md`] | Phase 26 is the authoritative row-table producer for Phase 18 final criteria; add consumed upstream rows there rather than bypassing it in Phase 28. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase28_final_readiness_packet.py`] |
| READ-01 | Maintainers can generate a final cutover readiness packet that links external evidence, acceptance decisions, exceptions, and residual risks. [VERIFIED: `.planning/REQUIREMENTS.md`] | Phase 28 already copies Phase 26 `requirement_ids`, `evidence_refs`, and `artifact_refs` into final packet rows; once Phase 26 carries consumed Phase 23-25 refs, Phase 28 can expose them with minimal changes. [VERIFIED: `tools/bazel/phase28_final_readiness_packet.py`] |
| READ-02 | Final readiness remains blocked by default unless required evidence passes or has explicit approved exceptions. [VERIFIED: `.planning/REQUIREMENTS.md`] | Preserve Phase 26 default pending/blocked rows when upstream inputs are absent and preserve Phase 28 hard-block/demotion behavior. [VERIFIED: `tools/bazel/phase26_release_signing_upstream_evidence.py`; `tools/bazel/phase28_final_readiness_packet.py`] |
</phase_requirements>

## Summary

The audit gap is concentrated in Phase 26 ingestion. Phase 23, 24, and 25 already write compact upstream row artifacts, but `tools/bazel/phase26_release_signing_upstream_evidence.py` currently builds all non-release rows from default placeholder status via `default_upstream_status(...)` and `phase26_requirement_ids(...)`. [VERIFIED: producer row writers; `build_upstream_rows(...)` in Phase 26]

Phase 28 should not become a cross-phase raw evidence collector. Its `load_phase26_rows(...)` and `normalize_readiness_criteria(...)` paths already copy Phase 26 row `requirement_ids`, `evidence_refs`, `artifact_refs`, `status`, and hard-block metadata into the final packet. [VERIFIED: `tools/bazel/phase28_final_readiness_packet.py`] Therefore the smallest robust fix is to parse and validate optional upstream row inputs at Phase 26, use them for the matching canonical Phase 18 criteria, then add Phase 28 regression coverage that the propagated fields appear in the packet. [VERIFIED: `.planning/phases/29-upstream-evidence-flow-closure/29-CONTEXT.md`]

**Primary recommendation:** Extend Phase 26 with optional row-input flags named `--phase23-simulator-row`, `--phase24-hardware-media-safety-row`, and `--phase25-live-service-row`; parse each into a canonical upstream row only when the flag is supplied; and keep current fail-closed quick defaults when a flag is absent. [VERIFIED: current Phase 26 CLI only accepts `--release-input`; current workflow quick command has no Phase 23-25 inputs]

## Project Constraints

- Read and honor `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md`, and relevant standards pages before planning and implementation. [VERIFIED: files read in this session]
- Use functional-core/imperative-shell style: keep row parsing and normalization in pure helper functions; keep CLI parsing, JSON I/O, and output writing in the shell. [VERIFIED: `standards/core/architecture.md`]
- Prefer early returns and shallow control flow. [VERIFIED: `standards/core/code-shape.md`]
- Test pure/business logic with focused unit tests and Arrange, Act, Assert comments. [VERIFIED: `standards/core/testing.md`]
- Before committing in this Rust repo, run `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`. [VERIFIED: user-provided AGENTS instructions]
- No repo-local `.claude/skills` or `.agents/skills` directories were present. [VERIFIED: `find .claude/skills .agents/skills -maxdepth 2 -name SKILL.md`]

## Existing Evidence Flow

### Phase 23

`tools/bazel/phase23_simulator_evidence_execution.py` writes `build/ci-evidence/phase23/upstream-simulator-result-row.json` with:

- `criterion_id`: `final-simulator-evidence`
- `evidence_family`: `simulator`
- `phase`: `23-simulator-evidence-execution`
- `phase_lifecycle_id`: `23-...`
- `requirement_ids`: `["EVID-01"]`
- `artifact_refs`: normalized and redacted simulator outputs
- `redaction_status`, `source_ref_status`, and `status` [VERIFIED: lines around upstream row writer]

### Phase 24

`tools/bazel/phase24_hardware_media_safety_evidence_execution.py` writes `upstream-hardware-media-safety-result-row.json` with:

- `criterion_id`: `final-hardware-safety-media-evidence`
- `evidence_family`: `hardware`
- `phase`: `24-hardware-media-and-safety-evidence-execution`
- `requirement_ids`: `["EVID-02"]`
- artifact, redaction, source-ref, and status fields [VERIFIED: upstream row writer]

### Phase 25

`tools/bazel/phase25_live_service_evidence_execution.py` writes `upstream-live-service-result-row.json` and `upstream-live-result-row.json` with:

- `criterion_id`: `final-live-service-evidence`
- `evidence_family`: `live-service`
- `phase`: `25-live-service-evidence-execution`
- `requirement_ids`: `["EVID-03"]`
- artifact, redaction, source-ref, and status fields [VERIFIED: upstream row writer]

The Phase 26 contract already documents the required compatibility mapping from `final-live-service-evidence` to `final-live-network-transfer-evidence`, but the implementation does not consume Phase 25 rows yet. [VERIFIED: `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json`; `tools/bazel/phase26_release_signing_upstream_evidence.py`]

## Implementation Pattern

### Pattern 1: Parse Upstream Inputs at Phase 26 Boundary

Add a small input descriptor table for the three upstream producers:

| CLI flag | Source path expectation | Source criterion | Canonical criterion | Requirement IDs |
|----------|-------------------------|------------------|---------------------|-----------------|
| `--phase23-simulator-row` | `build/ci-evidence/phase23/upstream-simulator-result-row.json` | `final-simulator-evidence` | `final-simulator-evidence` | `EVID-01`, `ACPT-01` |
| `--phase24-hardware-media-safety-row` | `build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json` | `final-hardware-safety-media-evidence` | `final-hardware-safety-media-evidence` | `EVID-02`, `ACPT-01` |
| `--phase25-live-service-row` | `build/ci-evidence/phase25/upstream-live-service-result-row.json` | `final-live-service-evidence` | `final-live-network-transfer-evidence` | `EVID-03`, `ACPT-01` |

Only supplied flags should be loaded. Missing optional flags must not fail quick mode; they should leave existing pending placeholders intact. [VERIFIED: Phase 29 D-02]

### Pattern 2: Canonicalize Compact Rows Into Phase 26 Rows

Convert a compact producer row into the Phase 26 upstream row schema:

- `criterion_id`: canonical Phase 18 criterion
- `evidence_family`: Phase 18 requirement evidence family
- `requirement_ids`: producer EVID ID plus `ACPT-01`
- `source_requirement_ids`: Phase 18 requirement IDs
- `owning_phase`: Phase 18 source phase
- `source_lifecycle_id`: Phase 18 source lifecycle ID
- `source_lifecycle_status`: `current` only when producer `phase_lifecycle_id` is non-empty and source metadata is accepted
- `evidence_refs`: include producer `manifest_ref` and generated row path when available
- `artifact_refs`: producer artifact refs plus the supplied row input path
- `status`: producer status if in the Phase 18 vocabulary
- `failure_reason`: `none` for passed rows, otherwise a precise upstream reason
- `redaction_status`, `source_ref_status`, `exception_status`, `maintainer_state`, `generated_at_utc`: normalized into the Phase 26 schema [VERIFIED: Phase 26 `UPSTREAM_RESULT_ROW_FIELDS` and `normalize_upstream_row(...)`]

Then run the existing `normalize_upstream_row(row, requirement)` hard-block logic. [VERIFIED: Phase 26 test coverage for redaction/source/lifecycle blockers]

### Pattern 3: Keep Phase 28 Thin

Phase 28 should only need focused regression tests unless implementation discovers a packet omission:

- `final-readiness-packet.json` criteria row for simulator includes `EVID-01` and the Phase 23 artifact refs.
- hardware/media/safety row includes `EVID-02` and the Phase 24 artifact refs.
- live-network row includes `EVID-03` and the Phase 25 artifact refs.
- `reference_demotion_authorization` remains `blocked` when no demotion decision input is supplied. [VERIFIED: `tools/bazel/phase28_final_readiness_packet.py`; Phase 29 D-07/D-08]

## Edge Cases to Test

- Valid Phase 23, 24, and 25 rows are consumed and replace the matching default pending rows. [VERIFIED: Phase 29 success criterion 2]
- Absent rows preserve the current pending/blocked defaults. [VERIFIED: Phase 29 D-02]
- Phase 25 compact criterion `final-live-service-evidence` maps to `final-live-network-transfer-evidence`. [VERIFIED: Phase 26 contract compatibility mapping]
- Wrong criterion IDs are rejected. [VERIFIED: Phase 29 D-01]
- Wrong or missing producer `requirement_ids` are rejected. [VERIFIED: Phase 29 D-01/D-05]
- Missing producer `phase_lifecycle_id` blocks or rejects the row. [VERIFIED: Phase 29 D-01/D-06]
- `redaction_status != passed` and `source_ref_status != passed` are hard blockers. [VERIFIED: existing Phase 26 hard-block logic]
- Unsupported producer status values are rejected before row-table output. [VERIFIED: Phase 18 upstream status vocabulary]
- Unsafe artifact refs outside `build/ci-evidence/phase23/`, `build/ci-evidence/phase24/`, `build/ci-evidence/phase25/`, or explicit `external://phase23/24/25/` forms are rejected. [VERIFIED: Phase 29 D-01 and secret-safe evidence policy]

## Validation Architecture

Phase 29 should use a single cohesive plan with four validation layers:

1. Focused Phase 26 Python unit tests:
   - `test_consumed_upstream_rows_replace_default_pending_rows`
   - `test_absent_upstream_rows_keep_fail_closed_defaults`
   - `test_phase25_compact_live_service_row_maps_to_phase18_live_network_criterion`
   - table-driven invalid-row tests for criterion, requirement ID, lifecycle, source-ref, redaction, status vocabulary, and artifact-ref guards
2. Focused Phase 28 Python unit tests:
   - a packet generated from Phase 26 rows containing Phase 23-25 refs carries `EVID-01`, `EVID-02`, and `EVID-03`
   - reference demotion remains blocked without explicit Phase 28 demotion input
3. Repo-native phase verification:
   - `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py`
   - `python3 tools/bazel/phase28_final_readiness_packet_test.py`
   - `just phase26-verify`
   - `just phase28-verify`
4. Rust-project pre-commit verification:
   - `cargo fmt --all`
   - `cargo clippy --all-targets --all-features -- -D warnings`
   - `cargo build --all-targets --all-features`
   - `cargo test --all-features`

The Nyquist validation artifact should explicitly map ACPT-01, READ-01, and READ-02 to the focused tests and phase verification commands. [VERIFIED: Phase 29 success criterion 4]

## Planning Recommendation

Use one plan, `29-01-PLAN.md`, with these task boundaries:

1. Extend Phase 26 contract/CLI/input validation and tests for consumed upstream rows.
2. Add Phase 28 propagation tests and minimal implementation changes only if tests reveal a packet omission.
3. Reconcile GSD requirement/summary/validation metadata for Phases 25-29.
4. Run focused and full required verification, then write Phase 29 summary and verification artifacts.

This plan is cohesive because Phase 28 already consumes Phase 26 rows; splitting Phase 26 ingestion from Phase 28 propagation would create unnecessary intermediate incomplete states. [VERIFIED: `tools/bazel/phase28_final_readiness_packet.py`]

