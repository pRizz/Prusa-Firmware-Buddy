---
phase: 28
slug: final-readiness-packet-and-demotion-gate
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-25T03:53:19Z
---

# Phase 28 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` invoked as a script |
| **Config file** | none - phase tool tests are plain Python files under `tools/bazel/` |
| **Quick run command** | `python3 tools/bazel/phase28_final_readiness_packet_test.py` |
| **Full suite command** | `just phase28-verify` |
| **Estimated runtime** | less than 60 seconds based on Phase 18 and Phase 23-27 verifier patterns |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase28_final_readiness_packet_test.py` plus the changed-path verifier mode such as `--contract-only`, `--security-only`, or `--wiring-only`.
- **After every plan wave:** Run Phase 26 quick, Phase 27 quick, Phase 28 quick, and `just phase28-verify`.
- **Before `/gsd-verify-work`:** `just phase28-verify`, `git diff --check`, and the repo-required Cargo sequence must be green.
- **Max feedback latency:** 60 seconds for the Python verifier/test loop; Bazel/just wrapper latency may be higher on cold cache.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 28-W0-01 | TBD | 1 | READ-01 | T-28-schema-drift | Phase 28 contract exact-matches Phase 18 final criteria and source-contract expectations for Phase 26 and Phase 27 inputs. | unit | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - W0 | pending |
| 28-W0-02 | TBD | 1 | READ-01 | T-28-traceability | Final packet emits one row per Phase 18 criterion and links Phase 26 upstream rows, Phase 27 decisions, exceptions, residual risks, blockers, and artifact refs. | unit | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - W0 | pending |
| 28-W0-03 | TBD | 1 | READ-01 | T-28-output-retention | Retained outputs are written only under `build/ci-evidence/phase28`, including packet, tables, summaries, demotion records, redacted report, artifact refs, and snapshots. | unit/wiring | `python3 tools/bazel/phase28_final_readiness_packet.py --quick --output-dir build/ci-evidence/phase28` | No - W0 | pending |
| 28-W0-04 | TBD | 1 | READ-02 | T-28-missing-inputs | Missing Phase 26 or Phase 27 inputs keep final readiness blocked and report actionable missing-input reasons. | unit | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - W0 | pending |
| 28-W0-05 | TBD | 1 | READ-02 | T-28-hard-blockers | Redaction failures, overclaim failures, unsafe refs, source-ref failures, lifecycle mismatches, and secret-tainted refs block before exception evaluation. | unit/security | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - W0 | pending |
| 28-W0-06 | TBD | 1 | READ-02 | T-28-exception-policy | Passed or exception-approved readiness requires no hard blockers and valid exception metadata for contract-coverable statuses only. | unit/security | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - W0 | pending |
| 28-W0-07 | TBD | 1 | READ-03 | T-28-no-implied-demotion | Green or exception-covered readiness does not authorize reference demotion without explicit Phase 28 demotion input. | unit/security | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - W0 | pending |
| 28-W0-08 | TBD | 1 | READ-03 | T-28-explicit-demotion-input | Explicit demotion approval is rejected when final readiness is blocked, lifecycle/source data drift, or approval metadata is incomplete. | unit/security | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | No - W0 | pending |
| 28-W0-09 | TBD | 1 | READ-01, READ-02, READ-03 | T-28-wiring-drift | Bazel, root aliases, workflow dispatch, and `just phase28-verify` run tests before verifier execution and preserve Phase 26/27 precondition order. | wiring | `python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only` | No - W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase28_final_readiness_packet_contract.json` - defines Phase 28 output root, source contracts, generated artifacts, readiness policy, demotion authorization policy, hard blockers, and input schemas.
- [ ] `tools/bazel/phase28_final_readiness_packet.py` - verifier/orchestrator with `--contract-only`, `--security-only`, `--wiring-only`, `--quick`, optional `--demotion-decision`, Phase 26/27 input paths, and output-root containment.
- [ ] `tools/bazel/phase28_final_readiness_packet_test.py` - focused unit, security, output, and wiring tests for READ-01, READ-02, and READ-03.
- [ ] Root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` entries for Phase 28.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real maintainer approval of exceptions and residual risks | READ-01, READ-02 | The repo can validate exception schema and precedence, but maintainers must supply real sanitized approval metadata and rationale. | Maintainer reviews the generated readiness packet, exception summary, residual-risk summary, and blocker summary before accepting any exception-covered readiness row. |
| Final reference demotion approval | READ-03 | The verifier can enforce explicit input and reject implied approval, but maintainers must decide whether reference demotion is authorized. | Maintainer supplies a sanitized Phase 28 demotion decision input with approver identity, role, timestamp, rationale, evidence refs, and scope after final readiness is unblocked. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all missing Phase 28 verifier/test/contract/wiring references.
- [ ] No watch-mode flags.
- [ ] Feedback latency under 60 seconds for direct Python tests.
- [ ] `nyquist_compliant: true` set in frontmatter after plans and automated evidence are green.

**Approval:** pending
