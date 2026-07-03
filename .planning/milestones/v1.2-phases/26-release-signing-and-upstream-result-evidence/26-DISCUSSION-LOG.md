# Phase 26: Release, Signing, and Upstream Result Evidence - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-24T13:36:46.286Z
**Phase:** 26-Release, Signing, and Upstream Result Evidence
**Mode:** Yolo
**Areas discussed:** Release evidence input model, signing/provenance secret handling, upstream row coverage, retained outputs and integration, verification

---

## Release Evidence Input Model

| Option | Description | Selected |
|--------|-------------|----------|
| Wrap Phase 17/20 contracts | Add a v1.2 execution wrapper around existing release/signing/provenance rows without redefining source IDs. | yes |
| Define a fresh Phase 26-only release schema | Faster to write initially, but risks drift from Phase 17/20 release gate contracts. | |
| Let the agent decide | Planner chooses the contract relationship later. | |

**User's choice:** Auto-selected the recommended contract-wrapping model.
**Notes:** Phase 26 should require complete release-manager rows and fail missing, duplicate, unknown, or drifted release evidence.

---

## Signing, Provenance, and Secret Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Reference-only signing identity | Retain fingerprints, authority names, certificate-chain refs, and external evidence refs while rejecting private material. | yes |
| Store signed payload samples | Would improve local inspection but violates secret/binary retention constraints. | |
| Let the agent decide | Planner chooses exact signing evidence semantics later. | |

**User's choice:** Auto-selected reference-only signing identity with hard secret rejection.
**Notes:** `approved-release-run` and `external-release-key-evidence` may pass. Template, smoke, pending, and blocked signing states cannot pass without allowed exception metadata.

---

## Upstream Result Row Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Validate every Phase 18 upstream gate family | Covers CI, simulator, hardware/media/safety, live-service, release/signing, retained-code, residual-risk, maintainer-decision/final-readiness, and reference-demotion rows. | yes |
| Only emit release upstream rows | Smaller phase, but does not satisfy ACPT-01 broad upstream row review. | |
| Let the agent decide | Planner determines row scope later. | |

**User's choice:** Auto-selected full Phase 18 upstream gate coverage.
**Notes:** Rows must include requirement IDs, owning phase/gate, lifecycle status, exception status, maintainer state, evidence refs, status, redaction/source-ref status, and generated timestamp. Later decision phases can leave retained-code/final-readiness rows blocked or pending, but Phase 26 should make them inspectable.

---

## Retained Outputs and Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Follow Phase 23-25 output convention | Use `build/ci-evidence/phase26`, safe tracked contracts/templates/tests, Bazel labels, rust workflow dispatch, and `just phase26-verify`. | yes |
| Reuse Phase 20 output directory | Simpler short-term, but mixes release production evidence with Phase 26 upstream-row review output. | |
| Let the agent decide | Planner chooses output locations later. | |

**User's choice:** Auto-selected Phase 23-25 output convention.
**Notes:** Generated evidence stays out of source control. Repo-tracked files are contracts, templates, verifier code, tests, and wiring.

---

## Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Focused Python verifier and tests | Test release row coverage, proof classes, redaction, upstream row schema, exception eligibility, retained outputs, and wiring. | yes |
| Manual review only | Too weak for release/signing and ACPT-01 machine-readable row requirements. | |
| Let the agent decide | Planner chooses verification depth later. | |

**User's choice:** Auto-selected focused verifier/test coverage.
**Notes:** Quick verification may pass only with safe fixtures and blocked placeholders; it must not claim real release-environment proof.

---

## the agent's Discretion

- Exact Phase 26 filenames and JSON field names.
- Whether to implement one cohesive verifier or split release evidence and upstream-row validation internally.
- Exact plan count, with a bias toward one cohesive plan unless research identifies a real dependency split.

## Deferred Ideas

- Retained-code acceptance, residual-risk rationale, exception approval, and maintainer final decision inputs belong to Phase 27.
- Final readiness packet generation and explicit reference-demotion approval belong to Phase 28.
