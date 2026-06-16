---
phase: 1
slug: reference-baseline-and-safety-envelope
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-02
---

# Phase 1 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python 3 standard library |
| **Config file** | none - phase-local script |
| **Quick run command** | `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py` |
| **Full suite command** | `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py && git diff --check` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py`
- **After every plan wave:** Run `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py && git diff --check`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | BASE-01 | - | No secrets copied into baseline matrix | structure | `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py` | yes | pending |
| 1-01-02 | 01 | 1 | BASE-02 | - | Reference capture declares credential-sensitive outputs as paths/classes only | structure | `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py` | yes | pending |
| 1-01-03 | 01 | 1 | BASE-03 | - | Concern ledger preserves intentional-delta classification | structure | `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py` | yes | pending |
| 1-01-04 | 01 | 1 | BASE-04 | - | Safety envelope records hardware/manual evidence debt explicitly | structure | `python3 .planning/phases/01-reference-baseline-and-safety-envelope/01-VERIFY.py` | yes | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

Existing infrastructure covers this phase. The phase-local Python verification script is created by the execution plan before it is first run.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Physical printer safety smoke for startup, watchdog, motion, thermal, power panic, and auxiliary controllers | BASE-04 | Requires supported printer hardware and controlled failure injection | Use `01-SAFETY-ENVELOPE.md` manual-hardware-required rows as the checklist for later hardware qualification. |
| Full reference firmware release capture across all supported products | BASE-02 | Requires full toolchain/bootstrap time and CI/hardware resources | Use `01-REFERENCE-CAPTURE.md` commands and evidence classes to run selected captures locally or in CI. |

---

## Validation Sign-Off

- [x] All tasks have automated verify or documented manual evidence dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-02
