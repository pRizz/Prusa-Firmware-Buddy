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
| **Quick run command** | `python3 tools/bazel/phase3_verify.py --quick` (stage-aware: missing helper files are Wave 0 pending until `artifact_packager.py`, `artifact_manifest.py`, and `generated_drift.py` all exist; once all three exist, quick mode requires them and their self-tests) |
| **Full suite command** | `python3 tools/bazel/phase3_verify.py --quick && python3 tools/bazel/artifact_packager.py --self-test && python3 tools/bazel/artifact_manifest.py --self-test && python3 tools/bazel/generated_drift.py --self-test && bazel query "//tools/bazel/... + //platforms/..." && bazel build //tools/bazel:representative_release_artifacts && bazel run //tools/bazel:phase3_verify && just --list` |
| **Estimated runtime** | ~60 seconds after Wave 0; longer only when bootstrap-dependent generator actions are explicitly enabled |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase3_verify.py --quick` after Wave 0 creates it; quick mode is stage-aware and begins requiring `artifact_packager.py`, `artifact_manifest.py`, and `generated_drift.py` only after all three files exist.
- **After every plan wave:** Run `bazel query "//tools/bazel/... + //platforms/..." && bazel run //tools/bazel:phase3_verify && just --list`; after Wave 2 also run `bazel build //tools/bazel:representative_release_artifacts`.
- **Before `/gsd-verify-work`:** Run the full Phase 3 verifier plus `git diff --check`.
- **Max feedback latency:** 120 seconds for default local checks; bootstrap-dependent artifact/generator execution may be classified as CI/manual evidence.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | BAZL-03, BAZL-05 | T-03-01 / T-03-02 | Verifier rejects missing Phase 3 targets, source-writing check actions, and private signing key material in local fixtures. | verifier | `python3 tools/bazel/phase3_verify.py --quick` | no - Wave 0 creates | pending |
| 03-01-02 | 01 | 1 | BAZL-03 | T-03-03 | Artifact packager and manifests derive stable fields from declared product metadata and output files, not unchecked strings alone. | unit/verifier | `python3 tools/bazel/artifact_packager.py --self-test && python3 tools/bazel/artifact_manifest.py --self-test` | no - Wave 0 creates | pending |
| 03-01-03 | 01 | 1 | BAZL-05 | T-03-02 | Drift checks register every BAZL-05 generator surface and never mutate tracked files during check mode. | unit/verifier | `python3 tools/bazel/generated_drift.py --self-test && python3 tools/bazel/generated_drift.py --list-checks` | no - Wave 0 creates | pending |
| 03-02-01 | 02 | 2 | BAZL-03 | T-03-01 / T-03-03 | Representative artifact matrix and fixtures cover `.bin`, `.bbf`, `.dfu`, `.map`, provenance, resource package outputs, boot/noboot variants, and auxiliary manifest visibility without secrets. | manifest/fixture | `python3 -m json.tool tools/bazel/manifests/representative_products.json >/dev/null && rg -n "\\.bbf|\\.dfu|\\.map|provenance|resource\\.pkg|unsigned-local" tools/bazel/manifests/representative_products.json` | no - Plan 02 creates | pending |
| 03-02-02 | 02 | 2 | BAZL-03 | T-03-03 | Bazel artifact labels produce declared output files rather than only generating manifests. | Bazel/build | `bazel query "//tools/bazel:representative_release_artifacts" && bazel build //tools/bazel:representative_release_artifacts && python3 tools/bazel/phase3_verify.py --require-artifacts --require-manifests` | partial - Phase 2 labels exist | pending |
| 03-03-01 | 03 | 3 | BAZL-05 | T-03-02 | Generator check/update labels cover product profiles, option data, resources, translations, fonts, WUI assets, ESP blobs, puppy/MMU descriptors, package metadata, and tracked generated outputs. | Bazel/query/verifier | `bazel query "//tools/bazel:generated_check + //tools/bazel:generated_update + //tools/bazel:generated_product_profiles_check + //tools/bazel:generated_product_profiles_update + //tools/bazel:generated_option_data_check + //tools/bazel:generated_option_data_update + //tools/bazel:generated_resources_check + //tools/bazel:generated_resources_update + //tools/bazel:generated_translations_check + //tools/bazel:generated_translations_update + //tools/bazel:generated_fonts_check + //tools/bazel:generated_fonts_update + //tools/bazel:generated_wui_assets_check + //tools/bazel:generated_wui_assets_update + //tools/bazel:generated_esp_blobs_check + //tools/bazel:generated_esp_blobs_update + //tools/bazel:generated_puppy_descriptors_check + //tools/bazel:generated_puppy_descriptors_update + //tools/bazel:generated_mmu_descriptors_check + //tools/bazel:generated_mmu_descriptors_update + //tools/bazel:generated_package_metadata_check + //tools/bazel:generated_package_metadata_update + //tools/bazel:tracked_generated_outputs_check + //tools/bazel:tracked_generated_outputs_update" && python3 tools/bazel/phase3_verify.py --require-drift-checks --require-update-targets` | no - Plan 03 creates | pending |
| 03-03-02 | 03 | 3 | BAZL-03, BAZL-05 | T-03-04 | `just phase3-verify`, `generated-check`, `generated-update`, and `release-package` route through Phase 3 Bazel-owned targets without enabling guarded reference execution by default. | facade/verifier | `just --list && python3 tools/bazel/phase3_verify.py --require-facade` | partial - recipes exist | pending |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/phase3_verify.py` - checks required Phase 3 files, target queryability, representative artifact/generator labels, drift target behavior, and `just` facade wiring.
- [ ] `tools/bazel/artifact_packager.py` - produces deterministic package-surface `.bin`, `.map`, provenance, `.bbf`, `.dfu`, resource image, and resource package outputs with a self-test.
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
