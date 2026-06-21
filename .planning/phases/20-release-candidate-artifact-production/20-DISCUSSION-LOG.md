# Phase 20: Release Candidate Artifact Production - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-21T12:45:35.072Z
**Phase:** 20-release-candidate-artifact-production
**Mode:** Yolo
**Areas discussed:** Artifact identity target, Production-vs-smoke proof boundary, Signing/provenance/comparison metadata, Phase 19 and final-review integration

---

## Artifact Identity Target

| Option | Description | Selected |
|--------|-------------|----------|
| Native Bazel release-product graph | Durable Bazel-owned release graph with declared outputs for every release surface. Highest closure but broadest implementation surface. | |
| Bazel-wrapped current release builder | Reuse current release tooling behind Bazel for fastest real artifact production. Transitional and less hermetic. | |
| Explicit release-environment input bundle | Use release-environment metadata/input artifacts when signing or production infrastructure cannot run locally. Honest but weaker as a local producer. | |
| Hybrid Bazel identity plus external signing inputs | Bazel owns locally producible artifact identity while private signing/provenance inputs remain explicit release-environment evidence. | yes |

**User's choice:** Auto-selected hybrid Bazel identity plus explicit release-environment signing/provenance inputs.
**Notes:** This best matches Phase 20's "real outputs or explicit release-environment inputs" scope while preserving private key hygiene and avoiding a premature full native release graph rewrite.

## Production-vs-smoke Proof Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Contract-enforced proof classes | Use a Phase 20 verifier/contract to distinguish approved release evidence from local smoke or placeholder evidence. | yes |
| Bazel target/provider boundary | Make the target graph itself prevent smoke dependencies from satisfying production release identity. | yes |
| External release-evidence bundle ingestion | Accept operator/release-supplied outputs with validated metadata and redaction checks. | yes |
| Aggregate-only final gate enforcement | Let aggregate/final workflows catch proof gaps later. Useful only as a secondary guard. | |

**User's choice:** Auto-selected layered enforcement: contract proof classes, target-level smoke separation, and external release-evidence ingestion when needed.
**Notes:** Aggregate and final-review checks should remain defense-in-depth, not the first place release proof ambiguity is detected.

## Signing, Provenance, and Comparison Metadata

| Option | Description | Selected |
|--------|-------------|----------|
| Repo-native JSON contract with attestation-shaped fields | Keep current JSON/stdlib verifier authority while using clear fields for subject digests, build inputs, key identity, retention refs, and outcomes. | yes |
| Native external attestations as canonical evidence | Make external in-toto/SLSA-style attestations the trust root. Strong interoperability but more policy/tooling complexity. | |
| Bazel-native build identity bundle | Use Bazel build metadata plus digest manifests for build input identity. Good supplement but incomplete for signing/comparison. | |
| SBOM/inventory-first contract | Useful for inventory and compliance, but not primary release proof. | |

**User's choice:** Auto-selected repo-native JSON evidence with attestation-shaped metadata fields.
**Notes:** This keeps the existing Phase 17 evidence model authoritative, avoids introducing external signing/attestation tooling as a new trust root, and leaves SBOM or native attestation exports as later additions.

## Phase 19 and Final-Review Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 20-owned release result manifest, Phase 19 indexes/retains it, Phase 21 consumes both | Preserves release proof ownership and gives final readiness machine-readable upstream evidence. | yes |
| Extend Phase 19 aggregate manifest to include Phase 20 release rows | Single CI bundle, but risks making aggregate CI look like release-proof authority. | |
| Upgrade Phase 17 target/output only | Minimal scope, but final readiness discovery remains weaker unless Phase 21 wires direct consumption. | |
| External release-environment attestation/input bridge | Good for private signing, but should feed Phase 20 rather than replace it. | |

**User's choice:** Auto-selected Phase 20-owned release result manifest with Phase 19 retention/indexing and Phase 21 consumption.
**Notes:** Phase 19 should not own release pass/fail semantics. Phase 21 should validate Phase 20 result manifests before final readiness can pass.

## the agent's Discretion

- Exact schema field order, status spelling, helper boundaries, and generated file names.
- Whether Phase 20 uses one integrated plan or splits into smaller execution tasks.
- Whether the first implementation uses wrapped current release tooling, explicit release inputs, or a small production-safe Bazel rule, provided the proof boundaries above hold.

## Deferred Ideas

- Full native Rust/Bazel release graph.
- External attestation tooling or SBOM export as a first-class trust root.
- Final reference-demotion policy and upstream manifest consumption rules beyond Phase 20 release evidence.
