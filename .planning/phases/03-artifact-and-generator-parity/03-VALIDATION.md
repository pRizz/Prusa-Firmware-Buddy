---
phase: 03
slug: artifact-and-generator-parity
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-02
---

# Phase 03 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Standard-library Python verifier plus Bazel query/run checks |
| **Config file** | `.bazelrc`, `tools/bazel/BUILD.bazel`, `justfile` |
| **Quick run command** | `python3 tools/bazel/phase3_verify.py --quick` |
| **Full suite command** | `bazel query "//tools/bazel/... + //platforms/..." && bazel run //tools/bazel:phase3_verify && just --list` |
| **Estimated runtime** | ~60 seconds after Wave 0; longer only when bootstrap-dependent generator actions are explicitly enabled |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase3_verify.py --quick` after Wave 0 creates it.
- **After every plan wave:** Run `bazel query "//tools/bazel/... + //platforms/..." && bazel run //tools/bazel:phase3_verify && just --list`.
- **Before `/gsd-verify-work`:** Run the full Phase 3 verifier plus `git diff --check`.
- **Max feedback latency:** 120 seconds for default local checks; bootstrap-dependent artifact/generator execution may be classified as CI/manual evidence.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | BAZL-03, BAZL-05 | T-03-01 / T-03-02 | Verifier rejects missing Phase 3 targets, source-writing check actions, and private signing key material in local fixtures. | verifier | `python3 tools/bazel/phase3_verify.py --quick` | no - Wave 0 creates | pending |
| 03-01-02 | 01 | 1 | BAZL-03 | T-03-03 | Artifact manifests derive stable fields from declared product metadata and output files, not unchecked strings alone. | unit/verifier | `python3 tools/bazel/artifact_manifest.py --self-test` | no - Wave 0 creates | pending |
| 03-01-03 | 01 | 1 | BAZL-05 | T-03-02 | Drift checks regenerate into temporary/output directories and never mutate tracked files during check mode. | unit/verifier | `python3 tools/bazel/generated_drift.py --self-test` | no - Wave 0 creates | pending |
| 03-02-01 | 02 | 1 | BAZL-03, BAZL-05 | T-03-04 | Bazel labels are queryable and guarded reference targets do not execute heavy reference commands by default. | Bazel/query | `bazel query "//tools/bazel/... + //platforms/..." && bazel run //tools/bazel:phase3_verify` | partial - Phase 2 labels exist | pending |
| 03-02-02 | 02 | 1 | BAZL-03, BAZL-05 | T-03-04 | `just generated-check` and `just release-package` route through Phase 3 Bazel-owned targets. | facade/verifier | `just --list && python3 tools/bazel/phase3_verify.py --require-facade` | partial - recipes exist | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/phase3_verify.py` - checks required Phase 3 files, target queryability, representative artifact/generator labels, drift target behavior, and `just` facade wiring.
- [ ] `tools/bazel/artifact_manifest.py` - extracts and normalizes artifact/package metadata with a self-test.
- [ ] `tools/bazel/generated_drift.py` - regenerates temporary outputs and compares tracked generated files with a self-test.
- [ ] `tools/bazel/artifact_rules.bzl` and/or `tools/bazel/generator_rules.bzl` - declares Phase 3 outputs, inputs, runfiles, and helper tools.
- [ ] `tools/bazel/phase3_verify.sh` - Bazel executable wrapper for the verifier.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full product-matrix artifact generation | BAZL-03 | Full firmware matrix depends on bootstrap/toolchain availability and may be CI-heavy. | Run the documented CI/manual release artifact target after bootstrap; compare generated manifests against Phase 1 reference metadata. |
| Signing-sensitive package parity | BAZL-03 | Private signing keys must not be committed or required for local checks. | Use unsigned/test-key local package mode; run real signing only in the approved release environment and record manifest evidence without key material. |
| Simulator, hardware, and firmware behavior parity | BAZL-03, BAZL-05 | Phase 3 covers artifacts/generators, not runtime behavior. | Defer to later phase gates; record these as not claimed by Phase 3 verification. |

---

## Validation Sign-Off

- [x] All tasks have automated verify commands or Wave 0 dependencies.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing verifier/helper references.
- [x] No watch-mode flags.
- [x] Feedback latency target is below 120 seconds for default local checks.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-02
