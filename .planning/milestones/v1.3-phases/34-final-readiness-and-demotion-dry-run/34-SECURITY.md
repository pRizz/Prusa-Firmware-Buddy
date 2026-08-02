---
phase: "34"
slug: "final-readiness-and-demotion-dry-run"
status: verified
threats_open: 0
asvs_level: 1
created: "2026-07-25"
---

# Phase 34 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

______________________________________________________________________

## Trust Boundaries

| Boundary | Description | Data Crossing |
| ---------- | ------------- | ------------------------- |
| Phase 31 intake to Phase 34 | Loads accepted-final receipts and consumed upstream row references from the exact Phase 31 evidence root. | Sanitized evidence metadata, row references, artifact references |
| Phase 31 contract to required-set ledger | Derives the complete required evidence-stream set from validated Phase 31 stream adapters independently of submitted receipts. | Required stream identities, expected source references, requirement IDs, affected gates |
| Phase 32/33 handoff to Phase 34 | Loads the canonical blocker register and normalized maintainer-decision handoffs from fixed evidence roots. | Blocker classifications, decision records, readiness and demotion inputs |
| CLI filesystem boundary | Resolves repository-relative input and output paths beneath declared roots before reading or writing. | Paths to generated evidence artifacts |
| Canonical ledger to reports | Projects the machine-readable packet, blocker summary, demotion result, and redacted Markdown report from one ledger. | Readiness rows, reason codes, authorization state |

______________________________________________________________________

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
| --------- | ----------------- | ----------- | ------------------------------ | ---------------------- | ------ |
| T-34-01 | Spoofing / Information Disclosure | Phase 33/31 refs into Phase 34 | mitigate | Recursive forbidden-field and forbidden-text rejection is applied while loading sanitized Phase 31, Phase 32, and Phase 33 inputs; raw evidence consumption is explicitly rejected (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:269`, `:288`, `:958`, `:1001`). Covered by the secret/overclaim regression at `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:1164`. | closed |
| T-34-02 | Tampering | CLI paths and output root | mitigate | Repository-relative root containment rejects absolute paths, parent traversal, wrong roots, symlink components, and Phase 33 input/output overlap (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:304`, `:313`, `:322`, `:1001`). Focused path regressions begin at `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:1045`. | closed |
| T-34-03 | Elevation of Privilege | Readiness to demotion authorization | mitigate | Readiness, approval validation, and approval decision remain separate predicates; the dry run opens only for `unblocked + valid + approve`, and approval projections must match a normalized Phase 33 decision (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:928`, `:1043`, `:1086`). Truth-table and corroborated-approval tests are at `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:692` and `:705`. | closed |
| T-34-04 | Spoofing / Tampering | Phase lifecycle and source contracts | mitigate | The Phase 34 contract validates exact source contract IDs and lifecycle identity; Phase 31-33 loaders validate canonical artifact/lifecycle identities and stable references, and snapshot generation fails if declared source artifacts cannot be resolved (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:366`, `:419`, `:958`, `:1001`, `:1152`). Lifecycle/source mismatch coverage is at `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:1184`. | closed |
| T-34-05 | Tampering | Phase 31 expected rows to Phase 32 classifications | mitigate | Expected rows derive from Phase 31 accepted-final consumed refs; the sparse overlay uses exact stream, source-ref, and gate matching, while duplicate, dangling, unknown, missing, and underclassified states block readiness (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:484`, `:632`, `:748`, `:1086`). Duplicate and underclassified regressions are at `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:578` and `:592`. | closed |
| T-34-06 | Tampering / Repudiation | Phase 33 exception coverage | mitigate | Exception decisions require the exact blocker reference, linked blocker reference, and affected gate; hard blocker problem kinds forcibly disable ordinary decision or exception coverage (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:545`, `:632`). Exact row-and-gate coverage is tested at `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:661`. | closed |
| T-34-07 | Tampering | JSON packet to Markdown report | mitigate | Packet, blocker summary, demotion artifact, and Markdown are generated from the canonical ledger, then checked for ledger, blocker, demotion, and report-state consistency (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:1181`, `:1206`, `:1277`). Projection consistency is tested at `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:1207`. | closed |
| T-34-08 | Tampering | Phase 31 required-set completeness | mitigate | The verifier loads the authoritative Phase 31 contract, requires its exact ID and lifecycle, validates unique known repository-relative stream adapters, and requires the complete four-stream set before deriving coverage (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:419`, `:458`, `:1297`). Contract derivation and tampering regressions are at `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:456` and `:471`. | closed |
| T-34-09 | Tampering / Elevation of Privilege | Missing-stream projection | mitigate | Every absent required stream receives a deterministic secret-free missing row, and `problem_kind == "missing"` takes precedence over any Phase 32 blocker or exception overlay with critical, ineligible, blocked `required-row-missing` semantics (`tools/bazel/phase34_final_readiness_demotion_dry_run.py:520`, `:632`). The per-stream omission regression attempts an approved missing-stream exception and still requires blocked readiness and gate state (`tools/bazel/phase34_final_readiness_demotion_dry_run_test.py:731`). | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

______________________________________________________________________

## Accepted Risks Log

No accepted risks.

______________________________________________________________________

## Unregistered Flags

None. Neither `34-01-SUMMARY.md` nor `34-02-SUMMARY.md` contains `## Threat Flags` entries.

______________________________________________________________________

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
| ------------ | ------------- | ------ | ---- | -------------- |
| 2026-07-25 | 7 | 7 | 0 | gsd-security-auditor |
| 2026-07-25 | 9 | 9 | 0 | gsd-security-auditor |

Verification evidence:

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q` — 36 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --contract-only` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --wiring-only` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --security-only` — passed.
- Phase 28 and Phase 31–34 regression suites — 131 tests passed; Bazel, `just phase34-verify`, and mandatory Cargo verification passed as recorded in `34-02-SUMMARY.md`.

Audit basis: repository guidance in `AGENTS.md`, the managed workflow sidecar in `AGENTS.bright-builds.md`, `standards/core/verification.md`, and the absence of an active local override in `standards-overrides.md`.

______________________________________________________________________

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-25
