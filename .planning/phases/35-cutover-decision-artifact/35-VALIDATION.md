---
phase: "35"
slug: "cutover-decision-artifact"
status: verified
nyquist_compliant: true
wave_0_complete: true
created: "2026-07-25"
---

# Phase 35 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

______________________________________________________________________

## Test Infrastructure

| Property | Value |
| --- | --- |
| **Framework** | Python standard-library `unittest` plus Bazel wrappers |
| **Config file** | `tools/bazel/BUILD.bazel` |
| **Quick run command** | `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q` |
| **Full suite command** | `just phase35-verify` |
| **Estimated runtime** | ~45 seconds |

______________________________________________________________________

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q`
- **After every plan wave:** Run `just phase35-verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 45 seconds

______________________________________________________________________

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 35-01-01 | 01 | 1 | CUTOVER-01, CUTOVER-02, CUTOVER-03 | T-35-01 through T-35-06 | RED tests cover closed verdict/route truth tables, exact audit-link sets, independent demotion state, unsafe paths/refs, lifecycle guards, and secret rejection | unit | `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q` | ✅ existing | ✅ green |
| 35-01-02 | 01 | 1 | CUTOVER-01, CUTOVER-02, CUTOVER-03 | T-35-01 through T-35-06 | The verifier derives one canonical link index, blocks incomplete or invalid inputs, emits exactly one route, and never infers demotion approval | unit/integration | `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q && python3 tools/bazel/phase35_cutover_decision_artifact.py --contract-only && python3 tools/bazel/phase35_cutover_decision_artifact.py --security-only` | ✅ existing | ✅ green |
| 35-01-03 | 01 | 1 | CUTOVER-01, CUTOVER-02, CUTOVER-03 | T-35-01 through T-35-06 | Bazel and `just` regenerate blocked prerequisites without synthesizing evidence, approval, exceptions, or demotion authorization | integration | `just phase35-verify` | ✅ existing | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

______________________________________________________________________

## Wave 0 Requirements

- [x] `tools/bazel/phase35_cutover_decision_artifact_test.py` — focused fixtures and RED tests for CUTOVER-01, CUTOVER-02, and CUTOVER-03
- [x] `tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json` — lifecycle, artifact, verdict, route, audit-link, security, and demotion-separation contract
- [x] Existing Python `unittest`, Bazel, and `just` infrastructure covers all other phase requirements

______________________________________________________________________

## Manual-Only Verifications

All phase behaviors have automated verification. Real external evidence and real maintainer decisions remain non-local inputs; local tests use sanitized isolated fixtures and the default workflow must remain blocked.

______________________________________________________________________

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 45s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** verified
