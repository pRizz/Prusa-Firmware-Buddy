---
phase: "39"
slug: "milestone-metadata-reconciliation"
status: draft
nyquist_compliant: true
wave_0_complete: true
created: "2026-07-28"
---

# Phase 39 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

______________________________________________________________________

## Test Infrastructure

| Property               | Value                                                                                                                                                            |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Framework**          | GSD structured CLI checks, Markdown/frontmatter inspection, and repository pre-commit gates                                                                      |
| **Config file**        | `.planning/config.json`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`                                                                                     |
| **Quick run command**  | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" summary-extract .planning/phases/31-final-evidence-intake/31-01-SUMMARY.md --fields requirements_completed` |
| **Full suite command** | Phase 39 layered metadata matrix plus `bun scripts/bright-builds-check.ts all` and the mandatory Rust sequence                                                   |
| **Estimated runtime**  | ~30 seconds for metadata checks; Rust workspace checks measured separately                                                                                       |

______________________________________________________________________

## Sampling Rate

- **After every task commit:** Run `git diff --check`, the task's focused GSD CLI assertion, and the mandatory Rust sequence.
- **After every plan wave:** Run the full Phase 39 metadata matrix and managed Bright Builds check.
- **Before `/gsd-verify-work`:** Phase 39 verification inputs and all pre-commit gates must be green.
- **Max feedback latency:** 60 seconds for metadata checks.

______________________________________________________________________

## Per-Task Verification Map

| Task ID  | Plan | Wave | Requirement                     | Threat Ref                | Secure Behavior                                                                                                                                    | Test Type           | Automated Command                                                                                                                                                | File Exists | Status     |
| -------- | ---- | ---- | ------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ---------- |
| 39-01-01 | 01   | 1    | INTAKE-01, INTAKE-02, INTAKE-03 | T-39-01, T-39-02, T-39-05 | Supported extraction returns all four Phase 31 intake IDs while original lifecycle metadata remains unchanged and no sensitive evidence is copied. | frontmatter/CLI     | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" summary-extract .planning/phases/31-final-evidence-intake/31-01-SUMMARY.md --fields requirements_completed` | ✅          | ⬜ pending |
| 39-01-02 | 01   | 1    | INTAKE-01, INTAKE-02, INTAKE-03 | T-39-03                   | Phase 31, 32, and 34 manual plan lists use exact phase-local filenames and match on-disk plan/summary counts.                                      | roadmap/CLI         | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze`                                                                                            | ✅          | ⬜ pending |
| 39-01-03 | 01   | 1    | INTAKE-01, INTAKE-02, INTAKE-03 | T-39-01, T-39-04          | All sixteen requirement rows agree across checkbox, traceability, summary extraction, and passed verification without changing evidence semantics. | cross-source matrix | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init milestone-op`                                                                                          | ✅          | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

______________________________________________________________________

## Wave 0 Requirements

Existing GSD CLI, Markdown/frontmatter, managed Bright Builds, and Rust workspace infrastructure covers all Phase 39 requirements.

______________________________________________________________________

## Manual-Only Verifications

All Phase 39 behaviors have automated verification.

______________________________________________________________________

## Mandatory Pre-Commit Sequence

Before every executor commit, run in order:

```bash
bun scripts/bright-builds-check.ts all
cargo fmt --all
cargo clippy --all-targets --all-features -- -D warnings
cargo build --all-targets --all-features
cargo test --all-features
```

______________________________________________________________________

## Validation Sign-Off

- [x] All anticipated tasks have automated verification.
- [x] Sampling continuity: no three consecutive tasks lack automated verification.
- [x] Existing infrastructure covers all references.
- [x] No watch-mode flags.
- [x] Feedback latency target is below 60 seconds for metadata checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-07-28
