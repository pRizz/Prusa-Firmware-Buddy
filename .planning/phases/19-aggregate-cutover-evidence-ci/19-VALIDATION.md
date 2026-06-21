---
phase: 19
slug: aggregate-cutover-evidence-ci
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-21
---

# Phase 19 - Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | Python `unittest` |
| Config file | none |
| Quick run command | `python3 tools/bazel/phase19_aggregate_ci_evidence_test.py` |
| Full suite command | `python3 tools/bazel/phase19_aggregate_ci_evidence_test.py && python3 tools/bazel/phase19_aggregate_ci_evidence.py --ci --output-dir build/ci-evidence/phase19` |
| Estimated runtime | ~20 seconds |

## Sampling Rate

- After every task commit: run `python3 tools/bazel/phase19_aggregate_ci_evidence_test.py`.
- After every plan wave: run the full suite command.
- Before `/gsd-verify-work`: full suite plus `bazel run //tools/bazel:phase19_verify_tests` and `bazel run //tools/bazel:phase19_verify` must pass when Bazel is available.
- Max feedback latency: 60 seconds for Python-only checks.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | CIEV-01, CIEV-02, CIEV-03 | T-19-01 | CI artifacts are redacted and repo-relative | unit | `python3 tools/bazel/phase19_aggregate_ci_evidence_test.py` | yes | pending |
| 19-01-02 | 01 | 1 | SIM-01, SIM-02, HARD-01, HARD-02, HARD-03, LIVE-01, LIVE-02, LIVE-03 | T-19-02 | External evidence remains pending or blocked without inputs | verifier | `python3 tools/bazel/phase19_aggregate_ci_evidence.py --ci --output-dir build/ci-evidence/phase19` | yes | pending |
| 19-01-03 | 01 | 1 | CIEV-01, CIEV-02, CIEV-03 | T-19-03 | Workflow upload path retains Phase 19 bundle only | unit | `python3 tools/bazel/phase19_aggregate_ci_evidence_test.py` | yes | pending |

## Wave 0 Requirements

Existing Python `unittest`, Bazel `shell_binary`, root aliases, and `just` verification infrastructure cover this phase.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub downloadable artifact retention | CIEV-03 | Requires GitHub Actions execution | After merge or PR run, confirm the `phase19-ci-evidence-*` artifact contains `run-manifest.json`, `redacted-summary.json`, logs, snapshots, and `phase-artifacts/`. |

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies.
- [x] Sampling continuity has no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing references.
- [x] No watch-mode flags.
- [x] Feedback latency < 60 seconds for Python-only checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-21
