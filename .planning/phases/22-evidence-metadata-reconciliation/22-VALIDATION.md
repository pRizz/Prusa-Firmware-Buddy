---
phase: 22
slug: evidence-metadata-reconciliation
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-21
lifecycle_mode: yolo
phase_lifecycle_id: 22-2026-06-21T16-59-18
---

# Phase 22 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` plus Bazel `shell_binary` wrappers |
| **Config file** | `tools/bazel/manifests/phase22_metadata_reconciliation_contract.json` |
| **Quick run command** | `python3 tools/bazel/phase22_metadata_reconciliation_test.py && python3 tools/bazel/phase22_metadata_reconciliation.py --quick` |
| **Full suite command** | `just phase22-verify` |
| **Estimated runtime** | ~30 seconds after Wave 0 files exist |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase22_metadata_reconciliation_test.py` plus the touched verifier mode.
- **After every plan wave:** Run `just phase22-verify` and `git diff --check`.
- **Before `/gsd-verify-work`:** Run `just phase22-verify`, lifecycle validation, and the milestone audit rerun or Phase 22 audit-readiness equivalent.
- **Max feedback latency:** 60 seconds for local deterministic checks.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 22-01-01 | 01 | 1 | Metadata debt from v1.1 audit | T-22-01 | Requirement checkboxes and traceability rows match Phase 14/19/21 evidence without claiming hardware-only simulator proof or final demotion approval. | unit / contract | `python3 tools/bazel/phase22_metadata_reconciliation_test.py` | yes - Wave 0 files exist | green |
| 22-01-02 | 01 | 1 | Metadata debt from v1.1 audit | T-22-02 | Phase 14-18 validation metadata reflects existing verifier files and passed local verification while preserving manual/external evidence boundaries. | unit / metadata | `python3 tools/bazel/phase22_metadata_reconciliation.py --validation-only` | yes - Wave 0 files exist | green |
| 22-01-03 | 01 | 1 | Metadata debt from v1.1 audit | T-22-03 | ROADMAP and STATE reflect completed Phase 19/20/21 and pending Phase 22 boundaries using source-backed counts. | unit / metadata | `python3 tools/bazel/phase22_metadata_reconciliation.py --roadmap-state-only` | yes - Wave 0 files exist | green |
| 22-01-04 | 01 | 1 | Metadata debt from v1.1 audit | T-22-04 | Generated audit-readiness output closes old functional gaps or lists only source-backed `non_blocking_debt`. | artifact / security | `python3 tools/bazel/phase22_metadata_reconciliation.py --quick --output-dir build/ci-evidence/phase22` | yes - Wave 0 files exist | green |
| 22-01-05 | 01 | 1 | Metadata debt from v1.1 audit | T-22-05 | Secret-bearing refs, unsafe generated artifact paths, missing source refs, and overclaim wording are rejected. | unit / security | `python3 tools/bazel/phase22_metadata_reconciliation_test.py` | yes - Wave 0 files exist | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [x] `tools/bazel/manifests/phase22_metadata_reconciliation_contract.json` - source-backed correction rows and allowed debt schema.
- [x] `tools/bazel/phase22_metadata_reconciliation.py` - stdlib verifier, generated report writer, source-ref/path/secret/overclaim checks, and wiring checks.
- [x] `tools/bazel/phase22_metadata_reconciliation_test.py` - focused tests for stale requirement rows, validation drift, roadmap/state mismatch, non-blocking debt schema, generated artifact path guards, and overclaim rejection.
- [x] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 22 labels, root aliases, dispatch, and facade.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Final milestone audit rerun review | Metadata debt from v1.1 audit | The verifier can prepare and validate audit-readiness metadata, but maintainers still need to inspect the rerun result before milestone archival. | Run the documented milestone audit flow after Phase 22 verification. The result must report `passed` or only deliberate documented non-blocking debt. |
| External evidence result acceptance | Metadata debt from v1.1 audit | Phase 22 reconciles metadata; it does not execute hardware, live-service, release, signing, upstream-result, maintainer-decision, or final demotion evidence. | Keep any absent external evidence represented as pending/blocked or deliberate non-blocking debt with owner, rationale, follow-up, and source refs. |

---

## Validation Sign-Off

- [x] All planned tasks have automated verifier commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing local verification files.
- [x] No watch-mode flags.
- [x] Feedback latency target is below 60 seconds for local checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-21 after Phase 22 verifier, Bazel, just, lifecycle, and audit-readiness checks passed; external evidence remains governed by validated upstream inputs.
