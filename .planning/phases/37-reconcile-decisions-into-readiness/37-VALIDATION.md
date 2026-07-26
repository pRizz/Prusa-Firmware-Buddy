---
phase: "37"
slug: "reconcile-decisions-into-readiness"
status: draft
nyquist_compliant: true
wave_0_complete: true
created: "2026-07-26"
---

# Phase 37 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

______________________________________________________________________

## Test Infrastructure

| Property | Value |
| --- | --- |
| **Framework** | Python `unittest`, Bazel `sh_test`/`sh_binary`, shell syntax checks, Rust workspace checks |
| **Config file** | Existing `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and root `Cargo.toml` |
| **Quick run command** | `python3 tools/bazel/phase34_decision_reconciliation_test.py -q` |
| **Full suite command** | `just phase34-verify` |
| **Estimated runtime** | ~180 seconds plus the mandatory Rust workspace pre-commit sequence |

______________________________________________________________________

## Sampling Rate

- **After every task commit:** Run the task's narrow Python test plus the mandatory Rust pre-commit sequence.
- **After every plan wave:** Run `just phase34-verify`.
- **Before `/gsd-verify-work`:** `git diff --check`, `just phase34-verify`, and the Rust workspace sequence must be green.
- **Max feedback latency:** 300 seconds for the phase-local Python/Bazel gate; Rust workspace duration is recorded separately.

______________________________________________________________________

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37-01-01 | 01 | 1 | DECIDE-01, DECIDE-02 | T-37-01 | Typed target bindings reject mismatched, duplicate, stale, and conflicting targets without accepting unsafe refs. | boundary/unit | `python3 tools/bazel/phase33_maintainer_decision_inputs_test.py -q` | ✅ | ⬜ pending |
| 37-01-02 | 01 | 1 | DECIDE-01, DECIDE-02, READY-01 | T-37-02 | Exact triple matching and axis-specific values are fail-closed; hard blockers cannot be approved away. | unit | `python3 tools/bazel/phase34_decision_reconciliation_test.py -q` | ❌ W0 | ⬜ pending |
| 37-02-01 | 02 | 2 | READY-01 | T-37-03 | Phase 34 publishes one canonical ledger with first-class decision-domain rows and no implied demotion authority. | integration/unit | `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q` | ✅ | ⬜ pending |
| 37-02-02 | 02 | 2 | DECIDE-01, DECIDE-02, READY-01 | T-37-04 | Actual Phase 31-33 outputs reach unblocked readiness only for complete valid inputs; every one-concern mutation stays blocked. | real-producer integration | `python3 tools/bazel/phase34_decision_reconciliation_integration_test.py -q` | ❌ W0 | ⬜ pending |
| 37-02-03 | 02 | 2 | READY-01 | T-37-05 | Hermetic runfiles and the repo-owned gate execute all new tests before publishing Phase 34 outputs. | Bazel/shell | `bash -n tools/bazel/rust_workflow.sh && just phase34-verify` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

______________________________________________________________________

## Wave 0 Requirements

- [ ] `tools/bazel/phase34_decision_reconciliation.py` — pure typed binding and axis/value reconciliation core.
- [ ] `tools/bazel/phase34_decision_reconciliation_test.py` — focused one-concern reconciliation tests.
- [ ] `tools/bazel/phase34_decision_reconciliation_integration_test.py` — actual Phase 31-33 producer-chain regression.

Existing Python, Bazel, shell, and Rust infrastructure covers all other requirements.

______________________________________________________________________

## Manual-Only Verifications

All Phase 37 behaviors have automated verification.

______________________________________________________________________

## Mandatory Pre-Commit Sequence

Before every executor commit, run in order:

```bash
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

______________________________________________________________________

## Validation Sign-Off

- [x] All anticipated tasks have automated verification or explicit Wave 0 dependencies.
- [x] Sampling continuity: no three consecutive tasks lack automated verification.
- [x] Wave 0 covers all missing test/code references.
- [x] No watch-mode flags.
- [x] Feedback latency target is below 300 seconds for phase-local checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-07-26
