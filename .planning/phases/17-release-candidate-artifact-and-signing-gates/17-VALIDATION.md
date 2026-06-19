---
phase: 17
slug: release-candidate-artifact-and-signing-gates
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-19
lifecycle_mode: yolo
phase_lifecycle_id: 17-2026-06-19T13-57-17
---

# Phase 17 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` |
| **Config file** | none - Phase 17 verifier tests run directly |
| **Quick run command** | `python3 tools/bazel/phase17_release_candidate_evidence_test.py && python3 tools/bazel/phase17_release_candidate_evidence.py --quick` |
| **Full suite command** | `just phase17-verify` |
| **Estimated runtime** | ~30 seconds after Wave 0 files exist |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase17_release_candidate_evidence_test.py && python3 tools/bazel/phase17_release_candidate_evidence.py --quick`
- **After every plan wave:** Run `bazel run //tools/bazel:phase17_verify_tests`, `bazel run //tools/bazel:phase17_verify`, and `git diff --check`
- **Before `/gsd-verify-work`:** `just phase17-verify` and lifecycle validation must be green
- **Max feedback latency:** 60 seconds for local contract/dry-run checks

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 1 | REL-01 | T-17-01 | Required rows cover `.bin`, `.bbf`, `.dfu`, map/provenance, resource, language, WUI, ESP, MMU, and auxiliary firmware surfaces without treating local smoke as release proof. | unit / contract | `python3 tools/bazel/phase17_release_candidate_evidence_test.py` | no - Wave 0 creates file | pending |
| 17-01-02 | 01 | 1 | REL-02 | T-17-02 | Signing and provenance rows require key identity, signing mode, build input identity, artifact digest, timestamp, retention path, and verification outcome while rejecting private keys and payload markers. | unit / security | `python3 tools/bazel/phase17_release_candidate_evidence.py --security-only` | no - Wave 0 creates file | pending |
| 17-01-03 | 01 | 1 | REL-03 | T-17-03 | Comparison rows cite archived v1.0/Phase 11 refs and classify every mismatch as `pass`, `intentional-delta`, `blocker`, or `deferred-retained-code-issue`. | unit / contract | `python3 tools/bazel/phase17_release_candidate_evidence.py --contract-only` | no - Wave 0 creates file | pending |
| 17-01-04 | 01 | 1 | REL-01,REL-02,REL-03 | T-17-04 | Bazel, `rust_workflow.sh`, root aliases, and `just phase17-verify` execute the verifier tests before the verifier. | integration / wiring | `just phase17-verify` | no - Wave 0 creates file | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase17_release_candidate_evidence_contract.json` - checked-in row-level release artifact, signing/provenance, and comparison evidence contract.
- [ ] `tools/bazel/phase17_release_candidate_evidence.py` - contract, security, wiring, quick, and release evidence validation for `REL-01`, `REL-02`, and `REL-03`.
- [ ] `tools/bazel/phase17_release_candidate_evidence_test.py` - stdlib tests for required rows, source refs, statuses, path guards, signing metadata, secrets, overclaims, mismatch classifications, generated artifacts, and wiring.
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 17 labels, root aliases, docs filegroup, dispatch, and facade.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Approved release-candidate artifact run | REL-01,REL-03 | Full firmware/resource/auxiliary release outputs require release environment dependencies and artifact retention outside source control. | Supply release evidence JSON naming artifact surface, product/profile, build identity, artifact refs, result, mismatch class, and residual risk. |
| External release signing proof | REL-02 | Private signing keys must stay outside the repository and planning artifacts. | Supply signing evidence JSON with key identity/fingerprint, signing mode, artifact digest, timestamp, verification outcome, and external artifact refs only. |
| Archived v1.0 reference comparison | REL-03 | Real release comparison artifacts may be produced by CI or release managers after the local contract exists. | Supply comparison evidence JSON with reference source, Rust/Bazel artifact ref, normalized fields, classification, owner phase, and residual risk. |

---

## Validation Sign-Off

- [x] All planned tasks must have automated verifier commands or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing local verification files
- [x] No watch-mode flags
- [x] Feedback latency target is below 60 seconds for local checks
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-19
