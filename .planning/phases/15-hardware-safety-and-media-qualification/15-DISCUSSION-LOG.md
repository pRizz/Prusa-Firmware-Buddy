# Phase 15: Hardware Safety and Media Qualification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `15-CONTEXT.md` - this log preserves the alternatives considered.

**Date:** 2026-06-17T22:53:45.617Z
**Phase:** 15-hardware-safety-and-media-qualification
**Mode:** Yolo
**Areas discussed:** Hardware Qualification Matrix, Safety and Fault Evidence, Artifact Capture and Redaction, Runner and Developer Workflow, Traceability and Prior Evidence

---

## Hardware Qualification Matrix

| Option | Description | Selected |
|--------|-------------|----------|
| Phase-owned row-level contract | Create a Phase 15 manifest that names each printer, board, media, auxiliary, and scenario row with requirements, artifacts, and residual risks. | yes |
| Umbrella hardware pass checklist | Use one broad checklist for hardware readiness. | |
| Reuse Phase 11/14 manifests directly | Mutate earlier evidence surfaces instead of owning a new Phase 15 contract. | |

**User's choice:** Phase-owned row-level contract (recommended default)
**Notes:** The workflow ran in yolo mode, so recommended decisions were auto-selected. The choice preserves prior evidence while giving Phase 15 clear ownership.

---

## Safety and Fault Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit physical safety rows | Cover watchdog, thermal/motion safety, emergency stop, safe output, crash recovery, UI input, MMU, RS485, and toolchanger fault scenarios separately. | yes |
| Source-backed safety only | Treat static manifests and verifier checks as enough for safety proof. | |
| Simulator-equivalent safety proof | Allow simulator results to satisfy physical safety rows. | |

**User's choice:** Explicit physical safety rows (recommended default)
**Notes:** This matches Phase 14's residual-risk boundary and Phase 11's no-overclaim decisions.

---

## Artifact Capture and Redaction

| Option | Description | Selected |
|--------|-------------|----------|
| Redacted generated evidence bundle | Generate run manifest, normalized results, redacted summary, contract snapshot, and log references under ignored `build/ci-evidence/phase15`. | yes |
| Commit raw hardware logs | Store all operator logs and crash outputs directly in source. | |
| Prose-only lab report | Capture evidence only in Markdown without machine-readable validation. | |

**User's choice:** Redacted generated evidence bundle (recommended default)
**Notes:** Operator metadata remains required, while raw crash dumps, secrets, firmware payloads, and unsafe operational data stay out of committed artifacts.

---

## Runner and Developer Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated stdlib Python verifier/collector | Add Phase 15 verifier, tests, manifest, Bazel labels, root aliases, rust_workflow dispatch, and `just phase15-verify`. | yes |
| Manual-only instructions | Write hardware steps without a machine-readable contract or local verifier. | |
| Broad firmware lab automation | Attempt full hardware automation before the evidence contract exists. | |

**User's choice:** Dedicated stdlib Python verifier/collector (recommended default)
**Notes:** This follows Phase 13 and Phase 14 patterns and keeps local verification deterministic when hardware is unavailable.

---

## Traceability and Prior Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Map every row to requirements and source evidence | Link rows to `HARD-*`, Phase 11 cutover evidence, and relevant Phase 7/8/10/13/14 artifacts. | yes |
| Roadmap-only traceability | Let roadmap phase completion stand in as proof. | |
| New standalone evidence taxonomy | Create a Phase 15 taxonomy disconnected from prior evidence rows. | |

**User's choice:** Map every row to requirements and source evidence (recommended default)
**Notes:** This keeps Phase 15 aligned with the v1.1 requirement surface and archived v1.0 evidence without redefining parity contracts.

---

## the agent's Discretion

- Exact row IDs, schema field order, status names, artifact filenames, helper boundaries, and dry-run output shape may be chosen during planning and implementation.
- The planner may use one integrated plan or task slices inside one plan if lifecycle and verification stay clean.

## Deferred Ideas

- Live network/TLS/transfer evidence remains Phase 16.
- Release-candidate artifact and signing evidence remains Phase 17.
- Retained-code acceptance and final demotion approval remains Phase 18.
- Long-run dashboards and broader lab automation remain future milestone work.
