---
phase: 32
slug: blocker-register-and-evidence-triage
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-03
---

# Phase 32 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python standard-library `unittest` style, matching recent `tools/bazel/phase*_test.py` files |
| **Config file** | `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` |
| **Quick run command** | `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` |
| **Full suite command** | `just phase32-verify` |
| **Estimated runtime** | ~60 seconds after Wave 0 files exist |

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase32_blocker_register_triage_test.py -q`
- **After every plan wave:** Run `just phase32-verify`
- **Before phase verification:** Full suite must be green
- **Max feedback latency:** 60 seconds

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 32-01-01 | 01 | 0 | TRIAGE-01 | T-32-01 | Phase 31 finality remains authoritative before source-row classification | unit/integration | `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` | no W0 | pending |
| 32-01-02 | 01 | 0 | TRIAGE-02 | T-32-02 | Unknown or unmapped row signals fail closed as critical unresolved decision blockers | unit | `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` | no W0 | pending |
| 32-01-03 | 01 | 0 | TRIAGE-03 | T-32-03 | Non-final, placeholder, smoke, local dry-run, prose-only, row-only, stale, redaction-failed, and secret-tainted inputs are proof-ineligible blockers | unit/security | `python3 tools/bazel/phase32_blocker_register_triage_test.py -q` | no W0 | pending |
| 32-01-04 | 01 | 1 | TRIAGE-01, TRIAGE-02, TRIAGE-03 | T-32-04 | Derived queues and reports are generated from canonical `blocker-register.json` row ids | integration | `just phase32-verify` | no W0 | pending |

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase32_blocker_register_triage_contract.json` - Phase 32 schema, source refs, policy map, output list, and verification commands.
- [ ] `tools/bazel/phase32_blocker_register_triage.py` - CLI, boundary parsing, pure classifier, output writer, security scan, and wiring check.
- [ ] `tools/bazel/phase32_blocker_register_triage_test.py` - tests for accepted-final rows, rejected-final rows, quarantined non-final rows, unknown policy fail-closed behavior, placeholder rejection, owner/action/severity requirements, derived-view consistency, no-secret propagation, and wiring order.

## Manual-Only Verifications

All phase behaviors should have automated verification. Real operator evidence collection remains outside Phase 32; this phase verifies classification and handoff behavior over sanitized generated artifacts and fixtures.

## Validation Sign-Off

- [ ] All tasks have automated verify commands or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all missing references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60 seconds
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 evidence passes

**Approval:** pending
