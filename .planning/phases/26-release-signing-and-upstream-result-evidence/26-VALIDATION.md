---
phase: 26
slug: release-signing-and-upstream-result-evidence
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-24T13:36:46.286Z
---

# Phase 26 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` invoked as a script |
| **Config file** | none - phase tool tests are plain Python files under `tools/bazel/` |
| **Quick run command** | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` |
| **Full suite command** | `just phase26-verify` |
| **Estimated runtime** | less than 60 seconds based on Phase 20 and Phase 23-25 verifier patterns |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` plus the changed-path verifier mode such as `--contract-only`, `--security-only`, or `--wiring-only`.
- **After every plan wave:** Run `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26` and `just phase26-verify`.
- **Before `/gsd-verify-work`:** `just phase26-verify` must be green.
- **Max feedback latency:** 60 seconds for the Python verifier/test loop; Bazel/just wrapper latency may be higher on cold cache.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 26-W0-01 | TBD | 1 | EVID-04 | T-26-secret-release-input | Secret-tainted release evidence is rejected before retained output writes. | unit/security | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - W0 | pending |
| 26-W0-02 | TBD | 1 | EVID-04 | T-26-release-row-coverage | Complete release-manager input covers all Phase 20 rows and rejects missing, duplicate, unknown, or drifted row IDs. | unit | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - W0 | pending |
| 26-W0-03 | TBD | 1 | EVID-04 | T-26-proof-class-overclaim | Only approved release-run or external release-key evidence may satisfy Phase 26 pass semantics. | unit/security | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - W0 | pending |
| 26-W0-04 | TBD | 1 | ACPT-01 | T-26-upstream-row-schema | Upstream result table includes every Phase 18 criterion and required Phase 26 row fields. | unit | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - W0 | pending |
| 26-W0-05 | TBD | 1 | ACPT-01 | T-26-lifecycle-source-ref-blockers | Missing, stale, lifecycle-mismatched, source-ref-invalid, failed, blocked, redaction-failed, and overclaiming rows stay blocked unless exception-coverable. | unit/security | `python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py` | No - W0 | pending |
| 26-W0-06 | TBD | 1 | EVID-04, ACPT-01 | T-26-wiring-drift | Bazel, rust workflow, and just wiring expose Phase 26 tests before verifier execution. | wiring | `python3 tools/bazel/phase26_release_signing_upstream_evidence.py --wiring-only` | No - W0 | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json` - defines Phase 26 output root, source contract refs, expected generated artifacts, release proof policy, and upstream row schema.
- [ ] `tools/bazel/phase26_release_signing_upstream_evidence.py` - verifier/orchestrator with `--contract-only`, `--security-only`, `--wiring-only`, `--quick`, `--release-input`, and `--output-dir`.
- [ ] `tools/bazel/phase26_release_signing_upstream_evidence_test.py` - focused unit, wiring, and security tests.
- [ ] Root `BUILD.bazel`, `tools/bazel/BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` entries for Phase 26.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real release-environment execution and signing approval | EVID-04 | Private signing key access and approved release operation happen outside the repo and must not be automated or retained locally. | Release manager supplies sanitized Phase 26 release input with external artifact refs, digests, signing identity refs, provenance refs, and comparison refs. |
| Maintainer acceptance of exception and final readiness decisions | ACPT-01 | Phase 26 exposes rows; Phase 27 and Phase 28 own retained-code, residual-risk, final approval, and demotion decisions. | Maintainer reviews Phase 26 upstream row manifest and later supplies decision inputs in the owning acceptance phases. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify commands or Wave 0 dependencies.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all missing Phase 26 verifier/test/wiring references.
- [ ] No watch-mode flags.
- [ ] Feedback latency under 60 seconds for direct Python tests.
- [ ] `nyquist_compliant: true` set in frontmatter after plans and automated evidence are green.

**Approval:** pending
