# Phase 31: Final Evidence Intake - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-07-03T02:10:15.699Z
**Phase:** 31-Final Evidence Intake
**Mode:** Yolo
**Areas discussed:** Final simulator evidence intake, Final hardware/media/safety evidence intake, Final live-service evidence intake, Final release/signing/provenance evidence intake, Cross-stream sanitization and final-evidence boundary

## Final Simulator Evidence Intake

| Option | Description | Selected |
|--------|-------------|----------|
| Direct Phase 23 real-input reuse | Reuse Phase 23 `--evidence-input` directly with no schema change. | |
| Phase 31 intake receipt over unchanged Phase 23 packet | Add v1.3 provenance while keeping Phase 23 packet authoritative. | yes |
| Phase 26 upstream-row-first intake | Accept compact upstream rows after trusted Phase 23 retention. | |

**User's choice:** Auto-selected the recommended wrapper/receipt approach.
**Notes:** Phase 23 remains authoritative for simulator scenarios, statuses, secret guards, retained outputs, and upstream row compatibility. Phase 31 receipt fields are provenance only.

## Final Hardware/Media/Safety Evidence Intake

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 31 pass-through wrapper over Phase 24 `--evidence-input` | Invoke or share Phase 24 validation for raw final packets. | yes |
| Phase 31 intake manifest referencing Phase 24 retained outputs | Register already-produced Phase 24 outputs after real-evidence checks. | yes |
| Extend Phase 24 with a final-intake mode | Modify Phase 24 directly for final intake. | |
| New Phase 31 hardware/media/safety schema | Create a new Phase 31 packet schema. | |

**User's choice:** Auto-selected the recommended Phase 24-authoritative wrapper/register approach.
**Notes:** Phase 31 must preserve Phase 24 scenario coverage, redaction, overclaim, artifact-root, and upstream-row rules. It may support both raw packet validation and retained-output registration when real hardware evidence provenance is present.

## Final Live-Service Evidence Intake

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 31 wrapper re-validates full Phase 25 evidence packet | Reuse Phase 25 validation and retained packet details. | yes |
| Phase 31 accepts only Phase 25 upstream result row | Accept compact rows after separate retained packet validation. | |
| New Phase 31 final live-service schema | Create new final live-service schema fields. | |
| Manual sanitized attestation with external links | Use prose or external references without machine validation. | |

**User's choice:** Auto-selected the recommended Phase 25 wrapper approach.
**Notes:** Final live-service proof requires exact Phase 16 scenario coverage and real evidence. Local smoke, quick/default output, and prose attestations are not final proof.

## Final Release/Signing/Provenance Evidence Intake

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 31 wrapper manifest over existing v1.2 packets | One final intake entrypoint preserving Phase 20/26 release rows and refs. | yes |
| Direct Phase 26 release-input pass-through | Keep only the smallest INTAKE-04 surface. | |
| External release evidence registry with retained pointer/digest rows only | Store references and digests when release policy forbids local derived files. | yes |
| Narrow Phase 20/26 schema patch | Patch existing schema only for a real blocker. | |

**User's choice:** Auto-selected the recommended wrapper/pass-through approach with reference-and-digest retention.
**Notes:** Private signing keys, tokens, certificates, service payloads, raw crash dumps, raw release logs, and other secret-bearing data must stay outside retained artifacts.

## Cross-Stream Sanitization and Final-Evidence Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Shared final-intake gate over existing Phase 23-26 contracts | Centralize finality policy while keeping stream validators authoritative. | yes |
| Per-stream finality checks inside each existing validator | Duplicate finality checks in each prior validator. | |
| Phase 26-only promotion boundary | Rely on upstream rows after stream-level acceptance elsewhere. | |
| Quarantine-then-promote intake | Store malformed/non-final submissions separately before promotion. | |

**User's choice:** Auto-selected the shared final-intake gate.
**Notes:** The final gate should preserve `redaction_status`, `source_ref_status`, `exception_status`, `failure_reason`, and lifecycle signals. Quick/default/local-smoke/template rows are non-final. Quarantine is allowed only if it cannot be mistaken for accepted final evidence.

## the agent's Discretion

- Concrete receipt and manifest file names.
- Whether Phase 31 is one verifier script with stream adapters or a shared policy module plus verifier.
- Exact Bazel and `just` labels, as long as they follow existing phase workflow patterns.

## Deferred Ideas

- Blocker register and owner/severity/next-action triage.
- Retained-code, exception, residual-risk, final-readiness, and demotion decisions.
- Final readiness packet and reference-demotion dry run.
- Cutover verdict artifact.
- Broad retained-code replacement and long-run dashboards.
