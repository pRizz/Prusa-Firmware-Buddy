#!/usr/bin/env bash
set -euo pipefail

root="${BUILD_WORKSPACE_DIRECTORY:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
command_name="$(basename "$0")"
tmp_root="${TEST_TMPDIR:-${TMPDIR:-/tmp}}/buddy-phase3-generated-check"

surfaces=(
  product_profiles
  option_data
  resources
  translations
  fonts
  wui_assets
  esp_blobs
  puppy_descriptors
  mmu_descriptors
  package_metadata
  tracked_generated_outputs
)

check_labels=(
  generated_product_profiles_check
  generated_option_data_check
  generated_resources_check
  generated_translations_check
  generated_fonts_check
  generated_wui_assets_check
  generated_esp_blobs_check
  generated_puppy_descriptors_check
  generated_mmu_descriptors_check
  generated_package_metadata_check
  tracked_generated_outputs_check
)

update_labels=(
  generated_product_profiles_update
  generated_option_data_update
  generated_resources_update
  generated_translations_update
  generated_fonts_update
  generated_wui_assets_update
  generated_esp_blobs_update
  generated_puppy_descriptors_update
  generated_mmu_descriptors_update
  generated_package_metadata_update
  tracked_generated_outputs_update
)

surface_from_command() {
  local name="$1"
  name="${name#generated_}"
  name="${name%_check}"
  name="${name%_update}"
  printf '%s\n' "$name"
}

run_generated_check() {
  local surface="$1"
  python3 "$root/tools/bazel/generated_drift.py" \
    --workspace "$root" \
    --output-dir "$tmp_root/$surface" \
    --check "$surface"
}

run_generated_update() {
  local surface="$1"
  python3 "$root/tools/bazel/generated_drift.py" \
    --workspace "$root" \
    --update \
    --check "$surface"
}

run_generated_assets() {
  run_generated_check resources
  run_generated_check translations
  run_generated_check fonts
  run_generated_check wui_assets
}

run_reference_release_compare() {
  local manifest="$root/tools/bazel/manifests/representative_products.json"
  local capture="$root/.planning/phases/01-reference-baseline-and-safety-envelope/01-REFERENCE-CAPTURE.md"
  local matrix="$root/.planning/phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md"
  local bazel_out="$root/bazel-bin/tools/bazel"

  test -f "$manifest"
  test -f "$capture"
  test -f "$matrix"

  python3 "$root/tools/bazel/artifact_metadata_compare.py" \
    --representative-matrix "$manifest" \
    --manifest "$bazel_out/mini_boot_artifacts.manifest.json" \
    --manifest "$bazel_out/mini_noboot_artifacts.manifest.json" \
    --manifest "$bazel_out/mk4_boot_artifacts.manifest.json" \
    --manifest "$bazel_out/mini_resource_package_artifacts.manifest.json" \
    --status "$bazel_out/mini_boot_artifacts.bbf.status.json" \
    --status "$bazel_out/mini_boot_artifacts.dfu.status.json" \
    --status "$bazel_out/mini_noboot_artifacts.bbf.status.json" \
    --status "$bazel_out/mini_noboot_artifacts.dfu.status.json" \
    --status "$bazel_out/mk4_boot_artifacts.bbf.status.json" \
    --status "$bazel_out/mk4_boot_artifacts.dfu.status.json" \
    --status "$bazel_out/mini_resource_package_artifacts.bbf.status.json" \
    --status "$bazel_out/mini_resource_package_artifacts.dfu.status.json" \
    --reference-capture "$capture" \
    --baseline-matrix "$matrix"

  printf 'reference_release_compare: manifest field and evidence class surface compared against Phase 1 reference docs\n'
  printf 'inputs: tools/bazel/manifests/representative_products.json .planning/phases/01-reference-baseline-and-safety-envelope/01-REFERENCE-CAPTURE.md .planning/phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md\n'

  if [[ "${BUDDY_BAZEL_EXECUTE_REFERENCE:-0}" == "1" ]]; then
    printf 'BUDDY_BAZEL_EXECUTE_REFERENCE=1 set; live reference commands may run in CI-only contexts.\n'
    python3 "$root/utils/build.py" --help >/dev/null
  else
    printf 'BUDDY_BAZEL_EXECUTE_REFERENCE=1 is not set; skipping live CMake/Python reference commands.\n'
  fi
}

cd "$root"

case "$command_name" in
  generated_check)
    for surface in "${surfaces[@]}"; do
      run_generated_check "$surface"
    done
    ;;
  generated_update)
    for surface in "${surfaces[@]}"; do
      run_generated_update "$surface"
    done
    ;;
  generated_assets)
    run_generated_assets
    ;;
  generated_*_check|tracked_generated_outputs_check)
    run_generated_check "$(surface_from_command "$command_name")"
    ;;
  generated_*_update|tracked_generated_outputs_update)
    run_generated_update "$(surface_from_command "$command_name")"
    ;;
  phase3_verify)
    python3 tools/bazel/phase3_verify.py --all
    ;;
  release_package|release_packages)
    python3 tools/bazel/phase3_verify.py --require-artifacts --require-manifests
    printf 'release_package representative_release_artifacts evidence_class=local-smoke bootstrap-required ci-only reference-only\n'
    ;;
  artifact_manifest_smoke)
    python3 tools/bazel/phase3_verify.py --require-artifacts --require-manifests
    ;;
  reference_release_compare)
    run_reference_release_compare
    ;;
  *)
    printf 'Unknown Phase 3 workflow target: %s\n' "$command_name" >&2
    exit 2
    ;;
esac
