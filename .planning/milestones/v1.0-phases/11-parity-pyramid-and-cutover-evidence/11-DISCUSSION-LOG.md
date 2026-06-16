# Phase 11: Parity Pyramid and Cutover Evidence - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-14T18:48:49.708Z
**Phase:** 11-Parity Pyramid and Cutover Evidence
**Mode:** Yolo
**Areas discussed:** Parity pyramid shape, requirement traceability, reference output comparison, cutover criteria, verification and lifecycle

---

## Parity Pyramid Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Source-backed manifest pyramid | Use explicit rows for unit, adapter, generator, reference, simulator, network, release, and hardware evidence classes. | yes |
| Prose-only cutover checklist | Summarize prior phase evidence without machine-checkable rows. | |
| Single aggregate test command only | Treat one final command as the complete pyramid. | |

**User's choice:** Source-backed manifest pyramid.
**Notes:** Auto-selected because prior phases consistently use source-backed manifests and verifier scripts.

---

## Requirement Traceability

| Option | Description | Selected |
|--------|-------------|----------|
| Every v1 requirement mapped to evidence | Cover all requirements from `.planning/REQUIREMENTS.md`, including completed and pending IDs. | yes |
| Only Phase 11 requirement IDs | Cover `VERF-01`, `VERF-03`, `VERF-04`, and `VERF-05` directly and trust prior checkboxes for the rest. | |
| Roadmap-status-only traceability | Use roadmap completion rows as proof. | |

**User's choice:** Every v1 requirement mapped to evidence.
**Notes:** Auto-selected because final cutover evidence must prove coverage, not just phase completion.

---

## Reference Output Comparison

| Option | Description | Selected |
|--------|-------------|----------|
| Normalized semantic comparison with explicit byte-identity exceptions | Use byte equality only where deterministic and otherwise compare manifests, metadata, fixtures, and normalized outputs. | yes |
| Byte-for-byte everywhere | Require all firmware and generated outputs to be byte-identical locally. | |
| No reference comparison | Rely only on Rust tests and domain contracts. | |

**User's choice:** Normalized semantic comparison with explicit byte-identity exceptions.
**Notes:** Auto-selected because prior phase context says firmware byte parity, hardware proof, and signing-sensitive checks require explicit fixtures or non-local gates.

---

## Cutover Criteria

| Option | Description | Selected |
|--------|-------------|----------|
| Criteria and readiness contract first | Add machine-checkable criteria for demoting the CMake/C++ reference path, without deleting it prematurely. | yes |
| Demote reference path immediately | Remove or demote CMake/C++ as part of Phase 11 implementation. | |
| Leave cutover decision informal | Document evidence but keep demotion criteria outside the repo. | |

**User's choice:** Criteria and readiness contract first.
**Notes:** Auto-selected to respect Big Bang cutover while keeping the final demotion gated by evidence.

---

## Verification And Lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| Phase verifier plus lifecycle validation | Add `phase11_verify.py`, tests, Bazel/just wiring, overclaim checks, and lifecycle ID enforcement. | yes |
| Manual review only | Let maintainers inspect artifacts without a deterministic local gate. | |
| CI-only final verification | Put all final evidence checks outside local developer workflows. | |

**User's choice:** Phase verifier plus lifecycle validation.
**Notes:** Auto-selected because every recent phase uses deterministic phase verifier scripts plus lifecycle provenance.

---

## the agent's Discretion

- Exact manifest names, row IDs, schema field order, verifier helper factoring, and Rust type names.
- Whether to introduce new Rust parity/cutover domain types or keep Phase 11 as manifests plus Python verifier, as long as the plan remains source-backed and test-covered.
- Plan split and wave structure.

## Deferred Ideas

- Actual deletion or demotion of CMake/C++ reference files unless the Phase 11 plan explicitly proves the cutover criteria.
- New firmware behavior or v2 feature work.
