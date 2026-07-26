---
phase: "38"
slug: "fail-closed-cutover-workflow"
status: draft
nyquist_compliant: true
wave_0_complete: true
created: "2026-07-26"
---

# Phase 38 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

______________________________________________________________________

## Test Infrastructure

| Property | Value |
| --- | --- |
| **Framework** | Python `unittest`, Bazel `sh_test`/`sh_binary`, shell syntax checks, Rust workspace checks |
| **Config file** | Existing `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and root `Cargo.toml` |
| **Quick run command** | `python3 tools/bazel/phase38_cutover_workflow_test.py -q` |
| **Full suite command** | `just phase38-verify` |
| **Estimated runtime** | ~300 seconds plus the mandatory Rust workspace pre-commit sequence |

______________________________________________________________________

## Sampling Rate

- **After every task commit:** Run the narrowest affected Python test plus the mandatory Rust pre-commit sequence.
- **After every plan wave:** Run `just phase38-verify`.
- **Before `/gsd-verify-work`:** `git diff --check`, `just phase38-verify`, and the Rust workspace sequence must be green.
- **Max feedback latency:** 420 seconds for the phase-local Python/Bazel gate; Rust workspace duration is recorded separately.

______________________________________________________________________

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38-01-01 | 01 | 1 | READY-02, READY-03 | T-38-01, T-38-03, T-38-05 | Every invalid Phase 31/33 source publishes a sanitized blocked Phase 34 replacement before nonzero return. | boundary/unit | `python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py -q` | ✅ | ⬜ pending |
| 38-01-02 | 01 | 1 | READY-03, CUTOVER-01 | T-38-02, T-38-03, T-38-04 | Phase 35 publication faults retain a blocking guard; absolute, traversal, symlink-escape, wrong-root, and non-directory targets fail before mutation; canonical data remains recoverable without reviving stale approval. | fault-injection unit | `python3 tools/bazel/phase35_cutover_decision_artifact_test.py -q` | ✅ | ⬜ pending |
| 38-02-01 | 02 | 2 | READY-02, READY-03, CUTOVER-01, CUTOVER-03 | T-38-01, T-38-02 | The production coordinator finalizes Phase 35, preserves nonzero operational failure, and rejects present, malformed, unreadable, lifecycle-stale, and unsafe-path guards. | coordinator unit | `python3 tools/bazel/phase38_cutover_workflow_test.py -q` | ❌ W0 | ⬜ pending |
| 38-02-02 | 02 | 2 | READY-02, READY-03, CUTOVER-01, CUTOVER-03 | T-38-01, T-38-05 | Actual Phase 31-35 producer paths cover blocked, approved, targeted-repair, and invalid-source replacement while demotion remains independent. | real-producer integration | `python3 tools/bazel/phase38_cutover_workflow_integration_test.py -q` | ❌ W0 | ⬜ pending |
| 38-02-03 | 02 | 2 | READY-02, READY-03, CUTOVER-01, CUTOVER-03 | T-38-01, T-38-02 | Owned coordinator wiring assertions prove hermetic runfiles and the repo-owned gate execute all focused and integration tests before default blocked publication. | wiring/shell unit | `python3 tools/bazel/phase38_cutover_workflow_test.py -q && bash -n tools/bazel/rust_workflow.sh` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

______________________________________________________________________

## Wave 0 Requirements

- [ ] `tools/bazel/phase38_cutover_workflow.py` — production coordinator and final authority validation.
- [ ] `tools/bazel/phase38_cutover_workflow_test.py` — focused coordinator and route/status tests.
- [ ] `tools/bazel/phase38_cutover_workflow_integration_test.py` — actual Phase 31-through-35 workflow regression.
- [ ] Phase 35 fault-injection fixture — controlled guard/write/rename/restore/cleanup failures without a production test-only authority flag.

Existing Python, Bazel, shell, and Rust infrastructure covers all other requirements.

______________________________________________________________________

## Manual-Only Verifications

All Phase 38 behaviors have automated verification.

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
- [x] Feedback latency target is below 420 seconds for phase-local checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-07-26
