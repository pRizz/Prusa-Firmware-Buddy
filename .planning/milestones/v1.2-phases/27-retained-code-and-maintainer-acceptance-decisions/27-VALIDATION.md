---
phase: 27
slug: retained-code-and-maintainer-acceptance-decisions
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-25T01:06:35.730Z
---

# Phase 27 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` invoked as a script |
| **Config file** | none - phase tool tests are plain Python files under `tools/bazel/` |
| **Quick run command** | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` |
| **Full suite command** | `just phase27-verify` |
| **Estimated runtime** | less than 60 seconds based on Phase 18 and Phase 23-26 verifier patterns |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` plus the changed-path verifier mode such as `--contract-only`, `--security-only`, or `--wiring-only`.
- **After every plan wave:** Run `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --output-dir build/ci-evidence/phase27` and `just phase27-verify`.
- **Before `/gsd-verify-work`:** `just phase27-verify`, `git diff --check`, and the repo-required Cargo sequence must be green.
- **Max feedback latency:** 60 seconds for the Python verifier/test loop; Bazel/just wrapper latency may be higher on cold cache.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 27-W0-01 | TBD | 1 | ACPT-02 | T-27-schema-drift | Phase 27 contract exact-matches Phase 18 retained packet IDs, final criteria, vocabularies, required fields, and exception policy. | unit | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | No - W0 | pending |
| 27-W0-02 | TBD | 1 | ACPT-02 | T-27-retained-decision-input | Maintainer can accept, reject, block, or exception every retained-code packet only with approver, role, timestamp, rationale, residual risk, and evidence refs. | unit | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | No - W0 | pending |
| 27-W0-03 | TBD | 1 | ACPT-02, ACPT-03 | T-27-hard-blockers | Redaction failures, overclaim failures, unsafe refs, source-ref failures, and stale lifecycle evidence block before exception evaluation. | unit/security | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | No - W0 | pending |
| 27-W0-04 | TBD | 1 | ACPT-03 | T-27-final-decision-input | Final-readiness criteria are approved, blocked, or exceptioned through machine-readable decision rows, not prose-only notes. | unit | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | No - W0 | pending |
| 27-W0-05 | TBD | 1 | ACPT-03 | T-27-no-demotion | Phase 27 quick and maintainer-input outputs never set reference demotion as allowed; Phase 28 remains the explicit demotion gate. | unit/security | `python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py` | No - W0 | pending |
| 27-W0-06 | TBD | 1 | ACPT-02, ACPT-03 | T-27-output-retention | Retained outputs are written only under `build/ci-evidence/phase27` with source contract snapshots and a Phase 28 handoff manifest. | unit/wiring | `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --output-dir build/ci-evidence/phase27` | No - W0 | pending |
| 27-W0-07 | TBD | 1 | ACPT-02, ACPT-03 | T-27-wiring-drift | Bazel, rust workflow, and just wiring expose Phase 27 tests before verifier execution. | wiring | `python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --wiring-only` | No - W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json` - defines Phase 27 output root, source contract refs, expected generated artifacts, acceptance policy, decision axes, and Phase 28 handoff policy.
- [ ] `tools/bazel/phase27_retained_code_acceptance_decisions.py` - verifier/orchestrator with `--contract-only`, `--security-only`, `--wiring-only`, `--quick`, `--maintainer-input`, and `--output-dir`.
- [ ] `tools/bazel/phase27_retained_code_acceptance_decisions_test.py` - focused unit, wiring, and security tests for ACPT-02 and ACPT-03.
- [ ] Root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` entries for Phase 27.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real maintainer acceptance of retained-code packets | ACPT-02 | The repo can validate machine-readable inputs, but maintainers must supply actual acceptance, rejection, or exception decisions. | Maintainer supplies sanitized Phase 27 decision input with approver identity, role, timestamp, rationale, residual risk, evidence refs, and optional exception metadata. |
| Final readiness and reference demotion approval | ACPT-03 | Phase 27 creates decision inputs and handoff data; Phase 28 owns the final readiness packet and explicit demotion decision. | Verify Phase 27 handoff keeps demotion blocked/not-approved and Phase 28 consumes it before any final readiness or demotion claim. |

---

## Validation Sign-Off

- [x] All tasks have automated verify commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing Phase 27 verifier/test/contract/wiring references.
- [x] No watch-mode flags.
- [x] Feedback latency under 60 seconds for direct Python tests.
- [x] `nyquist_compliant: true` set in frontmatter after plans and automated evidence are green.

**Approval:** complete
