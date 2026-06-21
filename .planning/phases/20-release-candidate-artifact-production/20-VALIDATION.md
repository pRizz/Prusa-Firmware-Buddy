---
phase: 20
slug: release-candidate-artifact-production
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-21
---

# Phase 20 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python stdlib `unittest` plus Bazel `shell_binary` wrappers |
| **Config file** | None for stdlib unittest; `pyproject.toml` configures pytest integration tests only |
| **Quick run command** | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py && python3 tools/bazel/phase20_release_candidate_artifacts.py --quick` |
| **Full suite command** | `just phase20-verify` |
| **Estimated runtime** | ~30 seconds for direct Python checks; Bazel facade runtime depends on local cache |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase20_release_candidate_artifacts_test.py`
- **After every plan wave:** Run `just phase20-verify`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds for direct Python checks

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 20-01-01 | 01 | 1 | REL-01 | T-20-01 | Release identity target is non-empty and rejects smoke labels | unit/wiring | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` | no W0 | pending |
| 20-01-02 | 01 | 1 | REL-01 | T-20-02 | Contract covers all required release artifact surfaces | contract | `python3 tools/bazel/phase20_release_candidate_artifacts.py --contract-only` | no W0 | pending |
| 20-01-03 | 01 | 1 | REL-02 | T-20-03 | Signing/provenance evidence rejects private key, payload, token, and credential markers | unit/security | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` | no W0 | pending |
| 20-01-04 | 01 | 1 | REL-03 | T-20-04 | Comparison rows require allowed mismatch classes with reasons and residual risk | unit/contract | `python3 tools/bazel/phase20_release_candidate_artifacts_test.py` | no W0 | pending |
| 20-01-05 | 01 | 1 | REL-01, REL-02, REL-03 | T-20-05 | Bazel, root aliases, workflow dispatch, and `just` run tests before verifier | integration/wiring | `just phase20-verify` | no W0 | pending |

---

## Wave 0 Requirements

- [ ] `tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json` - Phase 20 release identity, proof classes, result manifest, signing/provenance, retention, and comparison rows.
- [ ] `tools/bazel/manifests/phase20_release_environment_inputs.template.json` - explicit release-environment input template included in the production-safe release identity target.
- [ ] `tools/bazel/phase20_release_candidate_artifacts.py` - stdlib verifier and result writer with contract, wiring, security, and quick modes.
- [ ] `tools/bazel/phase20_release_candidate_artifacts_test.py` - regression tests for empty target, smoke target, placeholder, redaction, proof class, and comparison classification rejection.
- [ ] `tools/bazel/BUILD.bazel`, `BUILD.bazel`, `tools/bazel/rust_workflow.sh`, and `justfile` - Phase 20 labels, aliases, docs filegroup, dispatch, and facade.
- [ ] Phase 17 verifier/test fixtures updated if needed so Phase 17 still rejects smoke labels while Phase 20 makes the release target non-empty.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full production release signing with private release keys | REL-02 | Private keys and release environment are intentionally outside the repository | Supply explicit release-environment evidence input with key identity, artifact digests, retention refs, timestamp, operator or release-run ID, and verification outcome; verifier must validate metadata without storing private material |
| Full embedded firmware build for every supported product/board in release infrastructure | REL-01 | ARM toolchain, release infrastructure, and private signing inputs may not be available in local CI | Supply release-environment input refs for produced artifacts, or run the Bazel-owned release identity in a prepared release environment and retain the generated Phase 20 manifest |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all missing references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s for direct Python checks
- [ ] `nyquist_compliant: true` set in frontmatter after Wave 0 artifacts exist and direct checks pass

**Approval:** pending
