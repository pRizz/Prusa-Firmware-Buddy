# Phase 35: Cutover Decision Artifact - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the alternatives considered.

**Date:** 2026-07-25
**Phase:** 35-cutover-decision-artifact
**Mode:** Yolo
**Areas discussed:** Verdict derivation, audit-link completeness, next-milestone routing, reference-demotion separation

## Verdict Derivation

| Option | Description | Selected |
| --- | --- | --- |
| Closed typed truth-table reducer | Pure total reducer over validated Phase 34/33 inputs with default-blocked semantics and exhaustive finite-state tests. | ✓ |
| Derived candidate plus explicit final confirmation | Add another maintainer cutover confirmation bound to a computed candidate. | |
| OPA/Rego deny-overrides policy | Express the decision policy in a new declarative policy runtime. | |

**Selected:** Closed typed truth-table reducer.
**Rationale:** Phase 34 already supplies the canonical readiness facts and Phase 33 supplies explicit maintainer decisions. A pure reducer avoids duplicate authority and matches existing standard-library Python patterns.

## Audit-Link Completeness

| Option | Description | Selected |
| --- | --- | --- |
| Canonical normalized audit-link index | Derive a uniform exact-set link index from authoritative Phase 31-34 artifacts and project both JSON and Markdown from it. | ✓ |
| Category-specific reference manifest | Keep separate arrays and validation logic for each audit category. | |
| Content-addressed attestation bundle | Introduce a new provenance/attestation and signing model. | |

**Selected:** Canonical normalized audit-link index.
**Rationale:** It extends the existing canonical-ledger pattern, supports cross-category completeness checks, and keeps raw secret-bearing inputs outside the artifact.

## Next-Milestone Routing

| Option | Description | Selected |
| --- | --- | --- |
| Strict exclusive tri-state routing | `approved` routes to production-cutover planning; `blocked` and `approved-with-exceptions` route to named blocker repair. | ✓ |
| Follow-up-aware exception routing | Let some exception-bearing verdicts route to cutover planning based on a new follow-up discriminator. | |
| Dual-track exception routing | Permit cutover planning and repair to proceed concurrently under a hold. | |

**Selected:** Strict exclusive tri-state routing.
**Rationale:** It matches the roadmap literally, keeps routing deterministic, and prevents exception-bearing outcomes from becoming an implicit cutover authorization.

## Reference-Demotion Separation

| Option | Description | Selected |
| --- | --- | --- |
| Independent demotion decision and gate projection | Retain Phase 33 decision validity/value and Phase 34 dry-run gate state as separate explicit fields. | ✓ |
| Demotion approval as a verdict precondition | Couple cutover approval to an open demotion gate. | |
| Composite cutover-and-demotion enum | Collapse cutover and demotion into one combined status vocabulary. | |

**Selected:** Independent demotion decision and gate projection.
**Rationale:** The project has repeatedly locked readiness, cutover, and demotion as orthogonal decisions. Keeping them separate preserves auditability and avoids authorizing POST-01 work by implication.

## the agent's Discretion

- Exact output filenames, helper boundaries, reason-code spellings, Bazel labels, and report formatting may follow established Phase 31-34 patterns.

## Deferred Ideas

- Production cutover and reference demotion execution.
- Content-addressed or signed attestations and trust-root policy.
- Concurrent repair and production-cutover planning tracks.
- Retained vendor/HAL replacement and long-run dashboards.
