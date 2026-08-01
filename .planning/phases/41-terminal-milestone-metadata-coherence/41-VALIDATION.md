---
phase: "41"
slug: "terminal-milestone-metadata-coherence"
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-08-01"
---

# Phase 41 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
| --- | --- |
| **Framework** | Python `unittest`, Bazel `py_test`/`py_binary`, GSD lifecycle CLI, managed Bun checker, Rust workspace checks |
| **Config file** | `tools/bazel/BUILD.bazel`, `justfile`, `.planning/config.json`, root `Cargo.toml` |
| **Quick run command** | `python3 tools/bazel/phase41_terminal_consistency_test.py -q` |
| **Full suite command** | `just phase41-verify` |
| **Estimated runtime** | ~30 seconds for Phase 41 gates plus the repository Rust sequence |

## Sampling Rate

- **After every task commit:** Run the narrowest Phase 41 unit test, `git diff --check`, and `bun scripts/bright-builds-check.ts all`.
- **After every plan wave:** Run `just phase41-verify` in the strictest currently satisfiable mode.
- **Before `/gsd-verify-work`:** Run the full Phase 41 gate, ordered Rust sequence, lifecycle verification, and exact changed-path review.
- **Terminal acceptance:** Require zero partial/missing Nyquist phases, passed Phase 41 verification, a fresh eleven-phase/sixteen-requirement audit, and green pre-archive mode.
- **Max feedback latency:** 60 seconds for focused/live metadata gates; broad Rust and audit gates are recorded separately.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 41-01-01 | 01 | 1 | INTAKE-01, INTAKE-02, INTAKE-03 | T-41-01, T-41-02 | Raw Markdown/frontmatter is parsed once into strict normalized evidence types; malformed or duplicate input fails closed. | boundary/unit | `python3 tools/bazel/phase41_terminal_consistency_test.py -q` | ❌ W0 | ⬜ pending |
| 41-01-02 | 01 | 1 | READY-02, READY-03, CUTOVER-01, CUTOVER-03 | T-41-03, T-41-04 | Pre-audit and pre-archive modes reject stale counts, identities, inventories, Nyquist state, audit scope, and lifecycle contradictions with deterministic exit codes. | policy/unit | `bazel test //tools/bazel:phase41_terminal_consistency_tests` | ❌ W0 | ⬜ pending |
| 41-01-03 | 01 | 1 | READY-02, CUTOVER-03 | T-41-05 | Repo-owned Bazel and `just` gates run independently of a user-local GSD installation and compose with the managed checker without modifying it. | wiring/integration | `just phase41-verify` | ❌ W0 | ⬜ pending |
| 41-02-01 | 02 | 2 | INTAKE-01, INTAKE-02, INTAKE-03 | T-41-02, T-41-06 | Exact Phase 36/37/39 plan inventories and all requirement projections agree with on-disk plan, summary, and passed-verification evidence. | live consistency | `just phase41-verify --pre-audit` | ❌ W0 | ⬜ pending |
| 41-02-02 | 02 | 2 | READY-02, READY-03, CUTOVER-01, CUTOVER-03 | T-41-02, T-41-04 | ROADMAP, REQUIREMENTS, and STATE mutations use supported GSD ownership or bounded asserted exceptions and cannot create cutover/demotion authority. | lifecycle/integration | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" verify lifecycle 41 --require-plans --raw` | ✅ | ⬜ pending |
| 41-03-01 | 03 | 3 | READY-02, READY-03 | T-41-07 | Phase 37/38/40 validation records reflect executed Wave 0/task/campaign evidence and Nyquist discovery has no partial or missing phase. | evidence/Nyquist | `just phase41-verify --pre-audit` | ❌ W0 | ⬜ pending |
| 41-03-02 | 03 | 3 | CUTOVER-01, CUTOVER-03 | T-41-04, T-41-08 | One fresh audit covers Phases 31–41 and sixteen coherent requirements, with zero integration/flow/Nyquist gap and no implied production or demotion authority. | terminal integration | `just phase41-verify --pre-archive` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

## Wave 0 Requirements

- [ ] `tools/bazel/phase41_terminal_consistency_policy.py` — pure normalized authority and comparison core.
- [ ] `tools/bazel/phase41_terminal_consistency.py` — thin read-only CLI with pre-audit/pre-archive modes and exit codes 0/1/2.
- [ ] `tools/bazel/phase41_terminal_consistency_test.py` — coherent fixture plus one-invariant fail-closed mutations.
- [ ] `tools/bazel/BUILD.bazel` — Phase 41 Bazel binary and test targets with declared planning inputs.
- [ ] `just phase41-verify` — focused tests, live checker, and managed checker composition.

## Manual-Only Verifications

All Phase 41 metadata behavior is automatable. Human review remains required only to confirm the fresh audit does not claim production cutover or reference-demotion authorization beyond existing explicit decision artifacts.

## Mandatory Pre-Commit Sequence

Before every executor commit, run in order:

```bash
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

Also run `bun scripts/bright-builds-check.ts all`, the task's focused Phase 41 command, and `git diff --check`.

## Validation Sign-Off

- [x] All anticipated tasks have automated verification or explicit Wave 0 dependencies.
- [x] Sampling continuity: no three consecutive tasks lack automated verification.
- [x] Wave 0 covers all missing checker, test, Bazel, and `just` references.
- [x] No watch-mode flags.
- [x] Focused feedback latency target is below 60 seconds.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-08-01
