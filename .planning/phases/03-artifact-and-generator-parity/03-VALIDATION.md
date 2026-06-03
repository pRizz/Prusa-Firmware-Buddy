---
phase: 03
slug: artifact-and-generator-parity
status: passed
nyquist_compliant: true
wave_0_complete: true
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
| **Quick run command** | `python3 tools/bazel/phase3_verify.py --quick` (stage-aware: missing helper files are Wave 0 pending until `artifact_packager.py`, `artifact_manifest.py`, `artifact_metadata_compare.py`, and `generated_drift.py` all exist; once all four exist, quick mode requires them and their self-tests) |
| **Smoke suite command** | `python3 tools/bazel/phase3_verify.py --quick && python3 tools/bazel/artifact_packager.py --self-test && python3 tools/bazel/artifact_manifest.py --self-test && python3 tools/bazel/artifact_metadata_compare.py --self-test && python3 tools/bazel/generated_drift.py --self-test && bazel query "//tools/bazel/... + //platforms/..." && bazel build //tools/bazel:representative_package_surface_smoke //tools/bazel:representative_reference_format_status && bazel run //tools/bazel:phase3_verify && bazel run //tools/bazel:reference_release_compare && just --list` |
| **Final suite command** | Smoke suite plus `before=$(git status --short) && bazel run //tools/bazel:generated_check && after=$(git status --short) && test "$before" = "$after" && git diff --check`; bootstrap/reference environments additionally run `bazel build //tools/bazel:representative_reference_format_artifacts` and `python3 tools/bazel/phase3_verify.py --require-reference-artifacts` |
| **Estimated runtime** | Quick: <30 seconds after Wave 0; smoke: ~60 seconds; final/read-only and bootstrap-dependent reference-format generation are final-only evidence |

---

## Sampling Rate

- **After every task commit:** Run `python3 tools/bazel/phase3_verify.py --quick` after Wave 0 creates it; quick mode is stage-aware and begins requiring `artifact_packager.py`, `artifact_manifest.py`, `artifact_metadata_compare.py`, and `generated_drift.py` only after all four files exist.
- **After every plan wave:** Run `bazel query "//tools/bazel/... + //platforms/..." && bazel run //tools/bazel:phase3_verify && just --list`; after Wave 2 also run `bazel build //tools/bazel:representative_package_surface_smoke //tools/bazel:representative_reference_format_status` and `python3 tools/bazel/phase3_verify.py --require-artifacts --require-reference-status --require-manifests`; after Wave 3 also run `bazel run //tools/bazel:reference_release_compare`. Keep before/after `generated_check` as final-only unless debugging read-only behavior.
- **Before `/gsd-verify-work`:** Run the final suite command, including `bazel run //tools/bazel:generated_check` with before/after `git status --short` evidence that tracked generated files did not mutate, plus `git diff --check`.
- **Max feedback latency:** 120 seconds for default local checks; bootstrap-dependent artifact/generator execution may be classified as CI/manual evidence.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | BAZL-03, BAZL-05 | T-03-01 / T-03-02 | Verifier rejects missing Phase 3 targets, source-writing check actions, and private signing key material in local fixtures. | verifier | `python3 tools/bazel/phase3_verify.py --quick` | yes | green |
| 03-01-02 | 01 | 1 | BAZL-03 | T-03-03 | Artifact packager and manifests derive stable fields from declared product metadata and output files, invoke `utils/pack_fw.py --no-sign` / `utils/dfu.py` for BBF/DFU reference formats when prerequisites exist, and classify missing prerequisites as `bootstrap-required` or `ci-only` status manifests rather than accepting non-reference local encoders. | unit/verifier | `python3 tools/bazel/artifact_packager.py --self-test && python3 tools/bazel/artifact_manifest.py --self-test && python3 tools/bazel/artifact_metadata_compare.py --self-test` | yes | green |
| 03-01-03 | 01 | 1 | BAZL-05 | T-03-02 | Drift checks register every BAZL-05 generator surface and never mutate tracked files during check mode. | unit/verifier | `python3 tools/bazel/generated_drift.py --self-test && python3 tools/bazel/generated_drift.py --list-checks` | yes | green |
| 03-02-01 | 02 | 2 | BAZL-03 | T-03-01 / T-03-03 | Representative artifact matrix and fixtures cover `.bin`, `.bbf`, `.dfu`, `.map`, provenance, resource package outputs, boot/noboot variants, and auxiliary manifest visibility without secrets. | manifest/fixture | `python3 -m json.tool tools/bazel/manifests/representative_products.json >/dev/null && rg -n "\\.bbf|\\.dfu|\\.map|provenance|resource\\.pkg|unsigned-local" tools/bazel/manifests/representative_products.json` | yes | green |
| 03-02-02 | 02 | 2 | BAZL-03 | T-03-03 | Bazel artifact labels produce declared local package-surface outputs and explicit `.bbf.status.json` / `.dfu.status.json` reference-format status manifests; real `.bbf`/`.dfu` outputs use `utils/pack_fw.py --no-sign` and `utils/dfu.py` only in the separate bootstrap/reference target. | Bazel/build | `bazel query "//tools/bazel:representative_package_surface_smoke + //tools/bazel:representative_reference_format_status + //tools/bazel:representative_reference_format_artifacts" && bazel build //tools/bazel:representative_package_surface_smoke //tools/bazel:representative_reference_format_status && python3 tools/bazel/phase3_verify.py --require-artifacts --require-reference-status --require-manifests` | yes | green |
| 03-03-01 | 03 | 3 | BAZL-05 | T-03-02 | Generator check/update labels cover product profiles, option data, resources, translations, fonts, WUI assets, ESP blobs, puppy/MMU descriptors, package metadata, and tracked generated outputs. | Bazel/query/verifier | `bazel query "//tools/bazel:generated_check + //tools/bazel:generated_update + //tools/bazel:generated_product_profiles_check + //tools/bazel:generated_product_profiles_update + //tools/bazel:generated_option_data_check + //tools/bazel:generated_option_data_update + //tools/bazel:generated_resources_check + //tools/bazel:generated_resources_update + //tools/bazel:generated_translations_check + //tools/bazel:generated_translations_update + //tools/bazel:generated_fonts_check + //tools/bazel:generated_fonts_update + //tools/bazel:generated_wui_assets_check + //tools/bazel:generated_wui_assets_update + //tools/bazel:generated_esp_blobs_check + //tools/bazel:generated_esp_blobs_update + //tools/bazel:generated_puppy_descriptors_check + //tools/bazel:generated_puppy_descriptors_update + //tools/bazel:generated_mmu_descriptors_check + //tools/bazel:generated_mmu_descriptors_update + //tools/bazel:generated_package_metadata_check + //tools/bazel:generated_package_metadata_update + //tools/bazel:tracked_generated_outputs_check + //tools/bazel:tracked_generated_outputs_update" && python3 tools/bazel/phase3_verify.py --require-drift-checks --require-update-targets` | yes | green |
| 03-03-02 | 03 | 3 | BAZL-03, BAZL-05 | T-03-04 | `just phase3-verify`, `generated-check`, `generated-update`, and `release-package` route through Phase 3 Bazel-owned targets without enabling guarded reference execution by default. | facade/verifier | `just --list && python3 tools/bazel/phase3_verify.py --require-facade` | yes | green |
| 03-03-03 | 03 | 3 | BAZL-05 | T-03-02 | Full local gate executes aggregate `generated_check` and proves it is read-only by comparing `git status --short` before and after the Bazel run. | Bazel/run/read-only | `before=$(git status --short) && bazel run //tools/bazel:generated_check && after=$(git status --short) && test "$before" = "$after"` | yes | green |

*Status: pending, green, red, flaky*

---

## Wave 0 Requirements

- [ ] `tools/bazel/phase3_verify.py` - checks required Phase 3 files, target queryability, representative artifact/generator labels, drift target behavior, and `just` facade wiring.
- [ ] `tools/bazel/artifact_packager.py` - produces deterministic package-surface `.bin`, `.map`, provenance, resource image, and resource package smoke outputs; invokes `utils/pack_fw.py --no-sign` / `utils/dfu.py` for BBF/DFU reference formats only in reference-format mode when prerequisites exist; emits explicit `.bbf.status.json` / `.dfu.status.json` `bootstrap-required` or `ci-only` status manifests instead of accepting non-reference local encoders when prerequisites are missing.
- [ ] `tools/bazel/artifact_manifest.py` - extracts and normalizes artifact/package metadata with a self-test.
- [ ] `tools/bazel/artifact_metadata_compare.py` - loads produced manifests and reference/status manifests plus Phase 1 baseline/capture docs, then compares actual semantic metadata values for product, printer, board, MCU, bootloader mode, artifact kind, filenames, package members, provenance, resource presence, evidence class, signing mode, and stable hashes when present.
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
