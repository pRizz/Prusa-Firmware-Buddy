---
phase: 30
slug: milestone-metadata-cleanup
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| **Full suite command** | `git diff --check && cargo fmt --all --check && cargo clippy --all-targets --all-features -- -D warnings && cargo build --all-targets --all-features && cargo test --all-features` |
| **Estimated runtime** | ~120 seconds with warm caches |

---

## Sampling Rate

- **After every task commit:** Run `git diff --check && node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" roadmap analyze`
- **After every plan wave:** Run the full suite command plus the Phase 30 metadata extraction checks.
- **Before `/gsd-verify-work`:** Full suite and milestone audit must be green.
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 30-01-01 | 01 | 1 | Metadata cleanup | T-30-01 | State metadata remains source-backed and does not claim external evidence was supplied. | docs/check | `rg -n "Phase 30|100%|ready for archival|external evidence" .planning/STATE.md .planning/ROADMAP.md .planning/v1.2-MILESTONE-AUDIT.md` | Yes - W0 | pending |
| 30-01-02 | 01 | 1 | Metadata cleanup | T-30-02 | Current v1.2 requirement-bearing summaries are extractable by `summary-extract --fields requirements_completed`. | docs/check | `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" summary-extract .planning/phases/25-live-service-evidence-execution/25-01-SUMMARY.md --fields requirements_completed` | Yes - W0 | pending |
| 30-01-03 | 01 | 1 | Metadata cleanup | T-30-03 | Phase 25 verification includes explicit `EVID-03` requirement coverage while preserving the passed status and blocked live-service boundary. | docs/check | `rg -n "status: passed|Requirements Coverage|EVID-03|blocked placeholder|live-service" .planning/phases/25-live-service-evidence-execution/25-VERIFICATION.md` | Yes - W0 | pending |
| 30-01-04 | 01 | 1 | Metadata cleanup | T-30-04 | Fresh audit records no critical gaps and no contradictory stale metadata before archival. | audit | `rg -n "status: passed|critical_gaps: 0|TD-1|TD-2|TD-3|TD-4" .planning/v1.2-MILESTONE-AUDIT.md` | Yes - W0 | pending |

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

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all missing references
- [ ] No watch-mode flags
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
