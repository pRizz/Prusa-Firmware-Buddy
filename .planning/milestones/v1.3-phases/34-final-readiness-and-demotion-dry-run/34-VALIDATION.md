---
phase: "34"
slug: "final-readiness-and-demotion-dry-run"
status: verified
nyquist_compliant: true
wave_0_complete: true
created: "2026-07-25"
---

# Phase 34 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

______________________________________________________________________

## Test Infrastructure

| Property | Value |
| --- | --- |
| **Framework** | Python standard-library `unittest` plus Bazel wrappers |
| **Config file** | `tools/bazel/BUILD.bazel` |
| **Quick run command** | `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q` |
| **Full suite command** | `just phase34-verify` |
| **Estimated runtime** | ~30 seconds |

______________________________________________________________________

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q`
- **After every plan wave:** Run `just phase34-verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

______________________________________________________________________

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 34-01-01 | 01 | 1 | READY-01, READY-02, READY-03 | T-34-01 through T-34-06 | RED tests cover exact lineage, sparse blocker overlays, explicit approval, absolute/traversal/wrong-root/input-output-overlap/symlink path rejection, lifecycle guards, and secret rejection | unit | `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q` | ✅ W0 | ✅ green |
| 34-01-02 | 01 | 1 | READY-01, READY-02, READY-03 | T-34-01 through T-34-06 | Verifier generates one canonical ledger and blocks every non-open authorization state | unit/integration | `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q && python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --contract-only && python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --security-only` | ✅ W0 | ✅ green |
| 34-01-03 | 01 | 1 | READY-01, READY-02, READY-03 | T-34-01 through T-34-06 | Bazel and `just` regenerate prerequisites without synthesizing approval and verify the complete blocked-default bundle | integration | `just phase34-verify` | ✅ W0 | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

______________________________________________________________________

## Wave 0 Requirements

- [x] `tools/bazel/phase34_final_readiness_demotion_dry_run_test.py` — focused fixtures and RED tests for READY-01, READY-02, READY-03, including all five T-34-02 path-boundary cases
- [x] `tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json` — lifecycle, artifact, reason-code, security, and authorization contract
- [x] Existing Python `unittest`, Bazel, and `just` infrastructure covers all other phase requirements

______________________________________________________________________

## Manual-Only Verifications

All phase behaviors have automated verification. Real external evidence and real maintainer approvals remain non-local inputs; local tests use sanitized isolated fixtures and never claim those inputs exist in repository defaults.

______________________________________________________________________

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-07-25
