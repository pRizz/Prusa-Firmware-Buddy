---
phase: 18
slug: retained-code-acceptance-and-cutover-review
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-20
lifecycle_mode: yolo
phase_lifecycle_id: 18-2026-06-20T14-27-15
---

# Phase 18 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` |
| **Config file** | none - Phase 18 verifier tests run directly |
| **Quick run command** | `python3 tools/bazel/phase18_cutover_review_test.py && python3 tools/bazel/phase18_cutover_review.py --contract-only && python3 tools/bazel/phase18_cutover_review.py --quick` |
| **Full suite command** | `just phase18-verify` |
| **Estimated runtime** | ~30 seconds after Wave 0 files exist |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase18_cutover_review_test.py` plus the touched verifier mode.
- **After every plan wave:** Run `bazel run //tools/bazel:phase18_verify_tests`, `bazel run //tools/bazel:phase18_verify`, and `git diff --check`.
- **Before `/gsd-verify-work`:** `just phase18-verify` and lifecycle validation must be green.
- **Max feedback latency:** 60 seconds for local deterministic checks.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 18-01-01 | 01 | 1 | REV-01 | T-18-01 | Retained-code packet rows cover required retained surfaces or explicit mappings from Phase 11 retained rows, foreign-code inventory, and unsafe-boundary audit inputs. | unit / contract | `python3 tools/bazel/phase18_cutover_review_test.py` | yes - Wave 0 files exist | green |
| 18-01-02 | 01 | 1 | REV-02 | T-18-02 | Final-demotion evidence rows link CI, simulator, hardware, live-service, release, retained-code, and residual-risk evidence without upgrading pending evidence to approval. | unit / contract | `python3 tools/bazel/phase18_cutover_review.py --contract-only` | yes - Wave 0 files exist | green |
| 18-01-03 | 01 | 1 | REV-03 | T-18-03 | `demotion_allowed` stays false unless every criterion is `passed`, `exception-approved`, or validly `not-applicable` from validated decision input. | unit | `python3 tools/bazel/phase18_cutover_review_test.py` | yes - Wave 0 files exist | green |
| 18-01-04 | 01 | 1 | REV-01,REV-02,REV-03 | T-18-04 | Redaction, path containment, source-ref, approval metadata, exception rationale, and overclaim guards reject unsafe readiness or reference-demotion claims. | unit / security | `python3 tools/bazel/phase18_cutover_review.py --security-only` | yes - Wave 0 files exist | green |
| 18-01-05 | 01 | 1 | REV-01,REV-02,REV-03 | T-18-05 | Bazel, `rust_workflow.sh`, root aliases, docs filegroup, and `just phase18-verify` execute tests before the verifier. | integration / wiring | `just phase18-verify` | yes - Wave 0 files exist | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [x] `tools/bazel/manifests/phase18_cutover_review_contract.json` - checked-in retained-code acceptance and final-demotion review contract.
- [x] `tools/bazel/phase18_cutover_review.py` - contract, decision-input, quick artifact, security, path guard, source-ref, demotion computation, and wiring verifier.
- [x] `tools/bazel/phase18_cutover_review_test.py` - stdlib tests for required rows, retained-surface coverage, final evidence links, decision semantics, generated artifacts, secrets, overclaims, source refs, and workflow wiring.
- [x] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 18 Bazel labels, root aliases, docs filegroup, dispatch, and facade.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Maintainer retained-code acceptance | REV-01 | Human review is required to approve, reject, or exception retained surfaces. | Supply maintainer decision JSON with approver role, timestamp, rationale, status, evidence refs, residual risk, and exception metadata where applicable. |
| Final reference-demotion approval | REV-02,REV-03 | Local quick verification can validate policy and artifacts, but cannot approve reference demotion. | Supply final decision input that links every criterion to passed evidence or approved exception records. The verifier must keep `demotion_allowed` false when this input is absent. |
| Residual-risk exception approval | REV-02,REV-03 | Exceptions require maintainer judgment and scoped rationale. | Supply exception records with affected surface, mitigation/follow-up, expiry or review trigger, approver, and evidence links. |

---

## Validation Sign-Off

- [x] All planned tasks must have automated verifier commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing local verification files.
- [x] No watch-mode flags.
- [x] Feedback latency target is below 60 seconds for local checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-20
