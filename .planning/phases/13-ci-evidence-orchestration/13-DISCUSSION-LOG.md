# Phase 13: CI Evidence Orchestration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-16T14:21:01.122Z
**Phase:** 13-CI Evidence Orchestration
**Mode:** Yolo
**Areas discussed:** CI ownership and triggering, Evidence manifest contract, Artifact retention and redaction, Verification and failure ownership

---

## CI Ownership and Triggering

| Option | Description | Selected |
|--------|-------------|----------|
| New repo-owned GitHub Actions workflow | Add a dedicated cutover evidence workflow with PR path filters and manual dispatch; leave managed Bright Builds workflows untouched. | Yes |
| Extend Jenkins/Holly only | Use `utils/holly/build-pr.jenkins` as the sole CI surface and avoid GitHub Actions changes. | |
| Documentation-only CI contract | Record the CI expectation without adding a runnable workflow in this phase. | |

**User's choice:** New repo-owned GitHub Actions workflow.
**Notes:** Selected because Phase 13 needs reviewable workflow ownership and artifact retention in source without editing managed Bright Builds automation. Jenkins/Holly remains important context, but the phase needs a dedicated cutover evidence gate.

---

## Evidence Manifest Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Checked-in schema plus generated run manifest | Keep required gate definitions source-backed, generate per-run status manifests in an ignored output directory, and upload the generated manifest from CI. | Yes |
| Logs only | Rely on CI step logs and artifact names without a machine-readable manifest. | |
| One static checked-in manifest only | Commit gate definitions and status values but skip generated per-run evidence. | |

**User's choice:** Checked-in schema plus generated run manifest.
**Notes:** Selected to satisfy `CIEV-02` while preserving source control hygiene. The generated manifest should include gate status, command, owner phase, artifact path, and failure reason, but generated outputs stay out of the repo.

---

## Artifact Retention and Redaction

| Option | Description | Selected |
|--------|-------------|----------|
| Upload a deterministic evidence bundle | Upload verifier logs, manifest snapshots, normalized comparison outputs when present, and redacted summaries from a deterministic output directory. | Yes |
| Upload only failing logs | Retain artifacts only on failure to reduce storage. | |
| Store evidence in planning files | Commit run logs or artifact snapshots into `.planning/`. | |

**User's choice:** Upload a deterministic evidence bundle.
**Notes:** Selected because maintainers must inspect retained artifacts without relying on the local workspace. Secret-bearing material, firmware payload bytes, signing keys, raw crash dumps, tokens, certificates, and credential values remain forbidden in committed files.

---

## Verification and Failure Ownership

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 13 verifier and regression tests | Add a verifier/test pair that checks the CI evidence manifest, workflow wiring, artifact upload, redaction guards, Bazel/just exposure, and lifecycle metadata. | Yes |
| Reuse Phase 11 verifier only | Run the existing Phase 11 verifier from CI without adding Phase 13-specific validation. | |
| Manual review checklist | Make maintainers inspect the workflow and artifacts manually without local automated validation. | |

**User's choice:** Phase 13 verifier and regression tests.
**Notes:** Selected to match the Phase 11 pattern and keep CI orchestration itself verifiable. Failure ownership must be visible in both local verifier output and generated CI evidence manifests.

---

## the agent's Discretion

- Exact workflow file name, row IDs, output directory, artifact names, retention days, helper structure, and schema order may be chosen during planning and implementation.
- The implementation may choose a dry-run or pending status for non-local gates only when the status explicitly says later evidence is still required.

## Deferred Ideas

- Simulator evidence flows are Phase 14.
- Hardware/safety/media evidence is Phase 15.
- Live network and transfer evidence is Phase 16.
- Release-candidate artifact and signing gates are Phase 17.
- Retained-code acceptance and final cutover review are Phase 18.
