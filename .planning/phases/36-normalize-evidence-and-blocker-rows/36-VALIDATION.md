---
phase: "36"
slug: "normalize-evidence-and-blocker-rows"
status: draft
nyquist_compliant: true
wave_0_complete: true
created: "2026-07-26"
---

# Phase 36 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

______________________________________________________________________

## Test Infrastructure

| Property | Value |
| --- | --- |
| **Framework** | Python standard-library `unittest` plus Bazel wrappers |
| **Config file** | `tools/bazel/BUILD.bazel` |
| **Quick run command** | `python3 tools/bazel/phase32_blocker_normalization_test.py -q` |
| **Full suite command** | `just phase32-verify` |
| **Estimated runtime** | ~25 seconds quick / ~60 seconds full |

______________________________________________________________________

## Sampling Rate

- **After every task commit:** Run the focused command in the per-task map below
- **After every plan wave:** Run `just phase32-verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds for task sampling

______________________________________________________________________

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36-01-01 | 01 | 1 | INTAKE-04, TRIAGE-01, TRIAGE-02 | T-36-01 through T-36-05 | Atomic Phase 26 table validation prevents partial proof eligibility; malformed and unknown inputs remain visible critical blockers | unit | `python3 tools/bazel/phase32_blocker_normalization_test.py -q` | ❌ W0 | ⬜ pending |
| 36-01-02 | 01 | 1 | TRIAGE-01, TRIAGE-02 | T-36-02 through T-36-06 | Immutable source tuples produce stable collision-checked row IDs while decision axes stay exact and separate | unit/integration | `python3 tools/bazel/phase32_blocker_normalization_test.py -q` | ❌ W0 | ⬜ pending |
| 36-01-03 | 01 | 1 | INTAKE-04, TRIAGE-01, TRIAGE-02 | T-36-01 through T-36-07 | Real Phase 26 output flows through Phase 31 and real Phase 27/28 outputs reach Phase 32 without provenance bypass, secret propagation, or authority overclaim | integration | `python3 tools/bazel/phase32_blocker_register_triage_test.py Phase32ProducerShapeTest -q` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

______________________________________________________________________

## Wave 0 Requirements

- [x] `tools/bazel/phase32_blocker_register_triage_test.py` — existing focused Phase 32 test harness to extend with producer-shaped and identity regressions
- [x] `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` — existing canonical register contract to extend
- [x] `tools/bazel/phase32_blocker_normalization_test.py` — planned fast pure adapter/identity test module split from the oversized Phase 32 integration suite
- [x] Existing Phase 26, 27, 28, and 31 producer tests and Python/Bazel/`just` infrastructure cover all phase requirements

______________________________________________________________________

## Manual-Only Verifications

All Phase 36 behaviors have automated verification. Real external release evidence remains non-local; producer-shaped tests use sanitized isolated outputs while preserving Phase 31 finality and secret-safety rules.

______________________________________________________________________

## Validation Sign-Off

- [x] All tasks have `<automated>` verification or existing Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verification
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Task feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-07-26
