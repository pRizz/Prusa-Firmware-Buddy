---
phase: 21
slug: final-readiness-result-consumption
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-21
---

# Phase 21 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` plus Bazel `shell_binary` wrappers |
| **Config file** | None for stdlib unittest; `pyproject.toml` configures pytest integration tests only |
| **Quick run command** | `python3 tools/bazel/phase18_cutover_review_test.py && python3 tools/bazel/phase18_cutover_review.py --contract-only && python3 tools/bazel/phase18_cutover_review.py --quick` |
| **Full suite command** | `just phase18-verify` |
| **Estimated runtime** | ~30 seconds for direct Python checks; Bazel facade runtime depends on local cache |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase18_cutover_review_test.py`
- **After every plan wave:** Run `just phase18-verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds for direct Python checks

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 21-01-01 | 01 | 1 | REV-02 | T-21-01 | Phase 18 contract names required upstream result families, roots, lifecycle constraints, and generated consumption artifacts | contract | `python3 tools/bazel/phase18_cutover_review.py --contract-only` | yes | green |
| 21-01-02 | 01 | 1 | REV-02 | T-21-02 | Upstream result input rejects malformed rows, wrong lifecycle IDs, unsafe refs, redaction failures, source-ref failures, and overclaim failures | unit/security | `python3 tools/bazel/phase18_cutover_review_test.py` with a fixture-backed `--security-only --upstream-results` case | yes | green |
| 21-01-03 | 01 | 1 | REV-03 | T-21-03 | Complete approving maintainer decisions cannot set `demotion_allowed=true` without valid upstream result rows | unit | `python3 tools/bazel/phase18_cutover_review_test.py` | yes | green |
| 21-01-04 | 01 | 1 | REV-03 | T-21-04 | Generated readiness artifacts include maintainer status, upstream status, blockers, requirement IDs, and consumption summary | unit/generated artifact | `python3 tools/bazel/phase18_cutover_review_test.py && python3 tools/bazel/phase18_cutover_review.py --quick` | yes | green |
| 21-01-05 | 01 | 1 | REV-02, REV-03 | T-21-05 | Bazel and `just` facades continue to run Phase 18 tests and verifier modes after adding upstream result consumption | integration/wiring | `just phase18-verify` | yes | green |

---

## Wave 0 Requirements

- [x] `tools/bazel/manifests/phase18_cutover_review_contract.json` - add upstream result status vocabulary, per-criterion result requirements, and `upstream-result-consumption.json`.
- [x] `tools/bazel/phase18_cutover_review.py` - add `--upstream-results`, validated upstream parsing, consumption output, combined gating, and overclaim guards.
- [x] `tools/bazel/phase18_cutover_review_test.py` - add self-contained positive and negative upstream result fixtures for missing, failed, stale, unsafe, redaction/source-ref, exception, and `--security-only --upstream-results` cases.
- [x] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - inspect through `--wiring-only` and `just phase18-verify`; no wiring edits required.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real simulator, hardware, live-service, and release signing evidence reaches passed upstream status | REV-02, REV-03 | Those environments and private release inputs are intentionally outside local quick verification | Supply Phase 19 and Phase 20 result manifests with passed rows and run `python3 tools/bazel/phase18_cutover_review.py --quick --decision-input <maintainer-decisions.json> --upstream-results <upstream-results.json>`; `demotion_allowed` must remain false until every required row is passed or validly exception-covered |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 60s for direct Python checks
- [x] `nyquist_compliant: true` set in frontmatter after Wave 0 artifacts exist and direct checks pass

**Approval:** approved 2026-06-21
