# Phase 17: Release Candidate Artifact and Signing Gates - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-19T13:57:17.951Z
**Phase:** 17-Release Candidate Artifact and Signing Gates
**Mode:** Yolo
**Areas discussed:** Release artifact matrix, Signing and provenance hygiene, Reference comparison and mismatch classification, Artifact retention and CI integration, Runner and developer workflow, Traceability and prior evidence

---

## Release Artifact Matrix

| Option | Description | Selected |
|--------|-------------|----------|
| Phase-owned contract | Add a new Phase 17 release evidence contract with row-level artifact coverage. | yes |
| Mutate prior manifests | Extend Phase 11/13/15/16 manifests directly with release evidence. | |
| Prose checklist only | Document release checks without machine-readable contract rows. | |

**User's choice:** the agent's yolo recommendation: Phase-owned contract.
**Notes:** Prior phases consistently use phase-owned contracts and preserve non-local proof boundaries. Phase 17 should follow the same pattern.

---

## Signing and Provenance Hygiene

| Option | Description | Selected |
|--------|-------------|----------|
| Name/fingerprint only | Record key identity, signing mode, input identity, digests, and verification outcome without key material. | yes |
| Local test key as release proof | Treat fixture/test-key signing as enough for production release evidence. | |
| Raw release payload retention | Retain raw package bytes or signing-sensitive payloads in source/planning artifacts. | |

**User's choice:** the agent's yolo recommendation: Name/fingerprint only.
**Notes:** `REL-02` requires signing evidence without private keys in the repository or planning artifacts.

---

## Reference Comparison and Mismatch Classification

| Option | Description | Selected |
|--------|-------------|----------|
| Strict four-class mismatch model | Classify every mismatch as pass, intentional delta, blocker, or deferred retained-code issue. | yes |
| Freeform reviewer notes | Allow unstructured mismatch explanations. | |
| Byte identity only | Require byte-for-byte comparison for all outputs in local verification. | |

**User's choice:** the agent's yolo recommendation: Strict four-class mismatch model.
**Notes:** This directly matches Phase 17 success criteria and Phase 11's normalized comparison approach.

---

## Artifact Retention and CI Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Ignored generated output root | Keep generated release evidence under `build/ci-evidence/phase17` plus external artifact refs. | yes |
| Commit generated artifacts | Commit generated manifests, logs, or package outputs. | |
| CI pass implies release proof | Treat CI dry-runs as release-candidate evidence. | |

**User's choice:** the agent's yolo recommendation: Ignored generated output root.
**Notes:** This preserves the Phase 13 through Phase 16 pattern and prevents overclaiming release readiness.

---

## Runner and Developer Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| Standard-library Python verifier | Add focused Python verifier/tests with Bazel labels and `just phase17-verify`. | yes |
| Broad release automation rewrite | Replace release build/signing workflows as part of this phase. | |
| Manual-only process | Depend on release-manager checklist outside repo-owned verification. | |

**User's choice:** the agent's yolo recommendation: Standard-library Python verifier.
**Notes:** Prior phase evidence runners provide a stable template and keep orchestration auditable.

---

## Traceability and Prior Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Cite archived and phase contracts | Map each row to REL IDs plus Phase 3/7/10/11/13/15/16 evidence. | yes |
| Redefine parity contracts | Recreate v1.0 artifact parity definitions inside Phase 17. | |
| Skip older references | Only use the current roadmap and requirements. | |

**User's choice:** the agent's yolo recommendation: Cite archived and phase contracts.
**Notes:** v1.1 is evidence hardening, not parity redesign. Phase 17 layers release proof on existing contracts.

---

## the agent's Discretion

- Exact scenario IDs, schema field order, status names, generated artifact file names, helper boundaries, and dry-run output shape.
- Whether planning uses one integrated plan or a small number of tasks within one roadmap-level plan.

## Deferred Ideas

- Retained-code maintainer acceptance and final reference-demotion approval remain Phase 18 work.
- Production release approval and post-cutover release dashboards remain future milestone work.
