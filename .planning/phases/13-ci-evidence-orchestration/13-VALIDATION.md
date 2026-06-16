---
phase: 13
slug: ci-evidence-orchestration
status: local-signoff
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-16
lifecycle_mode: yolo
phase_lifecycle_id: 13-2026-06-16T14-21-01
---

# Phase 13 - Validation Strategy

> Per-phase validation contract for CI evidence orchestration.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python standard-library `unittest`, Phase 13 verifier modes, Bazel shell_binary wiring, and `just` facade checks. |
| **Config file** | `.planning/config.json`, `.github/workflows/ci-evidence.yml`, `tools/bazel/manifests/phase13_ci_evidence_contract.json`, `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile`. |
| **Quick run command** | `python3 tools/bazel/phase13_ci_evidence.py --quick` |
| **Full suite command** | `just phase13-verify` |
| **Estimated runtime** | Under 90 seconds for Phase 13 verifier tests plus focused manifest/workflow/wiring checks. |

## Sampling Rate

- **After every task commit:** Run the focused verifier mode for the touched surface: `--contract-only`, `--workflow-only`, `--security-only`, or `--wiring-only`.
- **After every plan wave:** Run `python3 tools/bazel/phase13_ci_evidence_test.py` and `python3 tools/bazel/phase13_ci_evidence.py --quick`.
- **Before `/gsd-verify-work`:** Run `just phase13-verify`, `python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13`, `git diff --check`, and `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" verify lifecycle 13 --require-plans --require-verification --raw`.
- **Max feedback latency:** 90 seconds for focused verifier feedback; generated CI evidence output may add command runtime but must still write artifacts before returning failure.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 0 | CIEV-02 | T-13-01-01 | Checked-in CI evidence contract validates required gate fields, status vocabulary, repo-relative paths, lifecycle ID, and failure reason semantics. | unittest/verifier | `python3 tools/bazel/phase13_ci_evidence_test.py && python3 tools/bazel/phase13_ci_evidence.py --contract-only` | yes - W0 | green |
| 13-01-02 | 01 | 0 | CIEV-01, CIEV-03 | T-13-01-02 | Repo-owned workflow runs on PR path changes and manual dispatch, uses minimum permissions, uploads a non-hidden evidence directory with explicit retention, and leaves managed workflows untouched. | verifier | `python3 tools/bazel/phase13_ci_evidence.py --workflow-only --security-only` | yes - W0 | green |
| 13-01-03 | 01 | 0 | CIEV-01, CIEV-02, CIEV-03 | T-13-01-03 | Phase 13 verifier writes run evidence before failing, rejects secret markers and non-local overclaims, and records actionable gate failure ownership. | unittest/verifier | `python3 tools/bazel/phase13_ci_evidence_test.py && python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13` | yes - W0 | green |
| 13-01-04 | 01 | 0 | CIEV-01, CIEV-02, CIEV-03 | T-13-01-04 | Bazel/just wiring exposes Phase 13 tests and verifier through repo-owned entrypoints without hiding substantive logic in YAML. | verifier/build | `python3 tools/bazel/phase13_ci_evidence.py --wiring-only && just phase13-verify` | yes - W0 | green |

*Status: pending, green, red, flaky*

## Wave 0 Requirements

- [x] `tools/bazel/manifests/phase13_ci_evidence_contract.json` - source-backed gate/schema contract for `CIEV-01`, `CIEV-02`, and `CIEV-03`.
- [x] `tools/bazel/phase13_ci_evidence.py` - contract validator, workflow validator, security scan, wiring check, and CI run evidence writer.
- [x] `tools/bazel/phase13_ci_evidence_test.py` - regression tests for missing fields, hidden upload paths, overclaim strings, redaction markers, path filters, and failure manifest semantics.
- [x] `.github/workflows/ci-evidence.yml` - repo-owned PR/manual CI evidence workflow; managed Bright Builds workflow remains untouched.
- [x] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 13 verifier/test labels and `just phase13-verify`.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Branch protection adoption | CIEV-01 | Repository branch protection settings are external to source control and path-filtered checks can stay pending when skipped. | Do not make the path-filtered CI evidence workflow a universal required check unless a companion always-running check or branch protection policy handles skipped workflows. |
| Organization artifact retention cap | CIEV-03 | GitHub organization or enterprise retention settings are not visible from the repository. | If CI rejects the selected retention value, lower the explicit workflow retention days while keeping retention configured and verifier-covered. |
| Later non-local evidence acceptance | CIEV-02, CIEV-03 | Simulator, hardware, live-service, release-candidate, signing, retained-code, and maintainer-review evidence belongs to Phases 14-18. | Preserve `pending-non-local` classifications until later phases attach approved artifacts. |

## Validation Sign-Off

- [x] All planned task groups have automated verifier or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive task groups without automated verify.
- [x] Wave 0 covers all missing Phase 13 validation references.
- [x] No watch-mode flags.
- [x] Feedback latency target documented.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** local-signoff
