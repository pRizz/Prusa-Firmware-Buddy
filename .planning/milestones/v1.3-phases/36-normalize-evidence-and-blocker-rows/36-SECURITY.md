---
phase: 36-normalize-evidence-and-blocker-rows
slug: normalize-evidence-and-blocker-rows
status: verified
threats_open: 0
asvs_level: 1
created: 2026-07-26
generated_by: gsd-secure-phase
lifecycle_mode: yolo
phase_lifecycle_id: 36-2026-07-26T00-27-52
---

# Phase 36 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

## Trust Boundaries

| Boundary | Description | Data Crossing |
| --- | --- | --- |
| Phase 31 receipt → Phase 26 table | Only an accepted-final receipt may make the exact contracted producer table eligible for adaptation. | Receipt provenance and release/signing evidence refs |
| Producer JSON → normalized signal | Malformed or unknown data must become visible critical blockers without partial eligibility. | Phase 26-28 producer JSON |
| Source identity → canonical row ID | Mutable or attacker-controlled classification data must not churn or collide IDs. | Typed producer identity tuple |
| Canonical row → decision identity | Similar criteria across decision domains must never cross-resolve. | Decision axis and producer-native subject |
| Adapter output → report/handoff | Secret-bearing fields, unsafe refs, and authority overclaims must not propagate. | Generated Phase 32 register, views, report, and handoff |

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| T-36-01 | Spoofing / Tampering | Phase 26 table envelope | mitigate | Exact contracted table path, accepted-final receipt provenance validation, and same-basename substitution regression | closed |
| T-36-02 | Tampering / Elevation of Privilege | Partial table validity | mitigate | Complete-table validation followed by one critical malformed signal on any structural failure | closed |
| T-36-03 | Spoofing / Tampering | Canonical row identity | mitigate | Source-only five-field hashing with duplicate tuple, duplicate row ID, incompatible remapping, and metadata-stability checks | closed |
| T-36-04 | Elevation of Privilege | Decision-domain matching | mitigate | Separate validated decision axis/subject identity and explicit prohibition of fuzzy fallback joins | closed |
| T-36-05 | Information Disclosure | Producer metadata and refs | mitigate | Path-containment checks, shape-specific ref extraction, and recursive secret/overclaim scans | closed |
| T-36-06 | Elevation of Privilege | Readiness/demotion projection | mitigate | Contract and reports disclaim approval/readiness/demotion authority; proof remains ineligible pending later phases | closed |
| T-36-07 | Repudiation | Producer-shaped regression evidence | mitigate | Actual Phase 26-28/31 producers run through hermetic Phase 32 boundary tests with lineage assertions | closed |

## Accepted Risks Log

No accepted risks.

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
| --- | --- | --- | --- | --- |
| 2026-07-26 | 7 | 7 | 0 | gsd-security-auditor |
| 2026-07-26 | 7 | 7 | 0 | gsd-security-auditor (gap-closure re-audit) |

The initial audit included 17 normalization tests, 8 producer-shaped tests, 25 full Phase 32 tests, contract validation, the Phase 32 security scan, shell syntax validation, and direct inspection of the seven changed implementation/test files.

The gap-closure re-audit included 17 normalization tests, 39 Phase 32 integration tests, 27 Phase 27 producer tests, 28 Phase 28 producer tests, contract/wiring/security checks, nested-path containment probes, canonical container identity checks, and full output-bundle publication assertions. All seven threats remain closed.

## Sign-Off

- [x] All threats have a disposition.
- [x] Accepted risks documented.
- [x] `threats_open: 0` confirmed.
- [x] `status: verified` set in frontmatter.

**Approval:** verified 2026-07-26
