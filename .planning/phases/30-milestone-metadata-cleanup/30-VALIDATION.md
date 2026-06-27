---
phase: 30
slug: milestone-metadata-cleanup
status: green
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-26
---

# Phase 30 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | GSD metadata commands, shell checks, and repo-local Rust verification |
| **Config file** | `.planning/config.json` |
| **Quick run command** | `git diff --check && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze` |
| **Per-task feedback target** | Under 30 seconds for metadata checks |
| **Phase/commit closure command** | `git diff --check && cargo fmt --all && cargo clippy --all-targets --all-features -- -D warnings && cargo build --all-targets --all-features && cargo test --all-features` |
| **Estimated closure runtime** | ~120 seconds with warm caches; reserved for phase/commit closure, not per-task sampling |

---

## Sampling Rate

- **After every task commit:** Run the task's quick metadata assertions plus `git diff --check`; keep feedback under 30 seconds.
- **After every plan wave:** Run the Phase 30 metadata extraction checks, Phase 25 focused verification commands if `25-VERIFICATION.md` changed, and the fresh milestone audit workflow.
- **Before `/gsd-verify-work` or commit:** Run `/gsd-audit-milestone`, `git diff --check`, and the full Rust Cargo gate.
- **Max feedback latency:** 30 seconds for per-task metadata checks; the full Cargo gate is intentionally reserved for phase/commit closure.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 30-01-01 | 01 | 1 | Metadata cleanup | T-30-01 | State metadata remains source-backed and does not claim external evidence was supplied. | docs/check | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze` plus stale/current STATE `rg` checks | Yes - W0 | green |
| 30-01-02 | 01 | 1 | Metadata cleanup | T-30-02 | Current v1.2 requirement-bearing summaries are extractable by `summary-extract --fields requirements_completed`. | docs/check | `summary-extract --fields requirements_completed --pick requirements_completed` plus direct Python frontmatter assertion | Yes - W0 | green |
| 30-01-03 | 01 | 1 | Metadata cleanup | T-30-03 | Phase 25 verification includes explicit `EVID-03` requirement coverage while preserving the passed status and blocked live-service boundary. | docs/check | Phase 25 `rg` assertions, `python3 tools/bazel/phase25_live_service_evidence_execution_test.py -q`, and `just phase25-verify` | Yes - W0 | green |
| 30-01-04 | 01 | 1 | Metadata cleanup | T-30-04 | Fresh audit records no critical gaps and no contradictory stale metadata before archival. | audit | `/gsd-audit-milestone v1.2` equivalent local audit commands plus audit closure `rg` assertions | Yes - W0 | green |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [x] Existing `.planning/` artifacts cover all Phase 30 metadata checks.
- [x] Existing `gsd-tools.cjs` commands cover roadmap and summary extraction sampling.
- [x] Existing Cargo workspace verification covers the Rust project commit gate.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Milestone archival | Metadata cleanup | Archival is intentionally deferred to `/gsd-complete-milestone` after Phase 30. | Review fresh audit output, then run the milestone completion workflow separately. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies, backed by `roadmap analyze`, `summary-extract`, Phase 25 commands, audit `rg`, `git diff --check`, and Cargo commands.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify, backed by per-task metadata assertions and Phase 25 focused checks.
- [x] Wave 0 covers all missing references, backed by existing `.planning/` artifacts and current GSD helper commands.
- [x] No watch-mode flags, backed by one-shot `rg`, `python3`, `just`, `git diff --check`, and Cargo invocations.
- [x] Per-task metadata feedback latency < 30s, backed by focused metadata checks; the full Cargo gate was intentionally reserved for commit closure.
- [x] Full Cargo gate reserved for phase/commit closure, backed by `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo build --all-targets --all-features`, and `cargo test --all-features`.
- [x] `nyquist_compliant: true` set in frontmatter after the required checks passed.

**Approval:** green
