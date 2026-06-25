---
phase: 29
slug: upstream-evidence-flow-closure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-25
---

# Phase 29 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest`, Bazel/just workflow wrappers, Cargo workspace checks |
| **Config file** | none — existing repo verifier scripts and `justfile` recipes |
| **Quick run command** | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py && python3 tools/bazel/phase28_final_readiness_packet_test.py` |
| **Full suite command** | `just phase26-verify && just phase28-verify && cargo fmt --all && cargo clippy --all-targets --all-features -- -D warnings && cargo build --all-targets --all-features && cargo test --all-features` |
| **Estimated runtime** | ~180 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py && python3 tools/bazel/phase28_final_readiness_packet_test.py`
- **After every plan wave:** Run `just phase26-verify && just phase28-verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 300 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 29-01-01 | 01 | 1 | ACPT-01 | T-29-01 | Invalid upstream row identity, requirement, lifecycle, source-ref, redaction, status, and artifact refs cannot become passing Phase 26 rows. | unit | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | ✅ | ⬜ pending |
| 29-01-02 | 01 | 1 | READ-01 | T-29-02 | Phase 28 packet rows expose Phase 23-25 requirement IDs, evidence refs, and artifact refs only through consumed Phase 26 rows. | unit | `python3 tools/bazel/phase28_final_readiness_packet_test.py` | ✅ | ⬜ pending |
| 29-02-01 | 02 | 2 | ACPT-01, READ-01, READ-02 | T-29-05 / T-29-06 | GSD summary, requirements, validation, and verification metadata reconcile only after focused tests, phase verification, diff check, and Cargo verification pass. | docs/check | `git diff --check && rg -n "ACPT-01|READ-01|READ-02" .planning/phases/29-upstream-evidence-flow-closure .planning/REQUIREMENTS.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All Phase 29 behaviors have automated verification. Real external evidence acquisition and maintainer demotion approval remain non-local inputs and are intentionally outside Phase 29.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 300s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
