---
phase: 33
slug: maintainer-decision-inputs
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-04
---

# Phase 33 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` plus Bazel `shell_binary` wrappers |
| **Config file** | none - direct phase verifier test script |
| **Quick run command** | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` |
| **Full suite command** | `just phase33-verify` |
| **Estimated runtime** | ~60 seconds after Bazel cache warmup |

## Sampling Rate

- **After every task commit:** Run `python3 -m py_compile tools/bazel/phase33_maintainer_decision_inputs.py tools/bazel/phase33_maintainer_decision_inputs_test.py` and `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q`.
- **After every plan wave:** Run `bazel run //tools/bazel:phase33_verify_tests` and `bazel run //tools/bazel:phase33_verify`.
- **Before `/gsd-verify-work`:** `just phase33-verify`, `python3 tools/bazel/phase33_maintainer_decision_inputs.py --security-only`, `python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only`, `git diff --check`, and the required Rust pre-commit sequence must be green.
- **Max feedback latency:** 120 seconds for Python checks; Bazel/just may take longer on cold cache.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 33-01-01 | 01 | 1 | DECIDE-01 | T-33-01 | Retained-code accept/reject/exception decisions require explicit maintainer metadata, residual-risk rationale, owner signoff, valid source row refs, and hard-blocker rejection. | unit + integration | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` | no - Wave 0 | pending |
| 33-01-02 | 01 | 1 | DECIDE-02 | T-33-02 | Readiness approve/block handoff consumes Phase 32 rows and approved exception/residual-risk decisions; approval fails with unresolved uncovered blockers. | unit + integration | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` | no - Wave 0 | pending |
| 33-01-03 | 01 | 1 | DECIDE-03 | T-33-03 | Demotion approve/reject handoff is separate and cannot be inferred from evidence, readiness, exceptions, or retained-code decisions. | unit + integration | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` | no - Wave 0 | pending |
| 33-01-04 | 01 | 1 | DECIDE-01, DECIDE-02, DECIDE-03 | T-33-04 | Generated outputs contain no secret-bearing fields, approval-overclaim markers, path traversal refs, or `demotion_allowed` fields. | security + wiring | `python3 tools/bazel/phase33_maintainer_decision_inputs.py --security-only` and `python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only` | no - Wave 0 | pending |

*Status: pending / green / red / flaky*

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json` - contract covering DECIDE-01, DECIDE-02, DECIDE-03, generated artifacts, source contracts, decision enums, and verification commands.
- [ ] `tools/bazel/phase33_maintainer_decision_inputs.py` - verifier implementation with contract, quick, security, and wiring modes.
- [ ] `tools/bazel/phase33_maintainer_decision_inputs_test.py` - focused unit and integration tests for all Phase 33 decision axes.
- [ ] `tools/bazel/BUILD.bazel`, root `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - `phase33_verify`, `phase33_verify_tests`, and `phase33-verify` wiring.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real maintainer signoff authenticity | DECIDE-01, DECIDE-02, DECIDE-03 | Phase 33 records maintainer identity refs but does not authenticate humans or external approval systems. | Maintainers must review identity refs outside local verifier execution before treating real decision packets as authoritative. |

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all missing references.
- [ ] No watch-mode flags.
- [ ] Feedback latency target documented.
- [ ] `nyquist_compliant: true` set in frontmatter after implementation evidence passes.

**Approval:** pending
