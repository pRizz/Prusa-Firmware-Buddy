#!/usr/bin/env bash
set -euo pipefail

root="${BUILD_WORKSPACE_DIRECTORY:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
command_name="$(basename "$0")"

run_or_print() {
  local description="$1"
  shift

  printf '%s\n' "$description"
  printf 'reference command:'
  printf ' %q' "$@"
  printf '\n'

  if [[ "${BUDDY_BAZEL_EXECUTE_REFERENCE:-0}" == "1" ]]; then
    (cd "$root" && "$@")
  fi
}

case "$command_name" in
  bootstrap)
    run_or_print "Bootstrap current reference dependencies." python3 utils/bootstrap.py
    ;;
  build_firmware)
    run_or_print "Build firmware through the current reference contract." python3 utils/build.py
    ;;
  rust_firmware)
    run_or_print "Build Rust firmware authority target; Phase 4 owns crate implementation while this target preserves the product build contract." python3 tools/bazel/phase2_verify.py
    ;;
  retained_foreign_code)
    run_or_print "Validate retained C, C++, ASM, generated, and vendor boundary inputs for the Bazel authority graph." python3 tools/bazel/phase2_verify.py
    ;;
  generated_assets)
    run_or_print "Check generated asset reference contracts." sh -c 'python3 utils/build.py --generate-cmake-presets && python3 utils/logging/generate_overview.py'
    ;;
  host_tools)
    run_or_print "Build host tools through the current reference contract." python3 utils/build.py --help
    ;;
  test_host)
    run_or_print "Run host test reference contract." sh -c 'mkdir -p build-tests && cd build-tests && cmake .. -DBOARD=BUDDY && make tests && ctest .'
    ;;
  unit_tests)
    run_or_print "Run unit test reference contract." sh -c 'mkdir -p build-tests && cd build-tests && cmake .. -DBOARD=BUDDY && make tests && ctest .'
    ;;
  simulator_inputs)
    run_or_print "Validate simulator input reference contract." sh -c 'pytest tests/integration --firmware <firmware.bin>'
    ;;
  format)
    run_or_print "Run formatting reference contract." pre-commit run cmake-format yapf clang-format
    ;;
  lint)
    run_or_print "Run lint/reference static checks." python3 tools/bazel/phase2_verify.py
    ;;
  generated_check)
    run_or_print "Check generated-file reference contracts." sh -c 'python3 utils/build.py --generate-cmake-presets && python3 utils/logging/generate_overview.py'
    ;;
  simulator_parity)
    run_or_print "Run simulator parity reference contract." sh -c 'pytest tests/integration --firmware <firmware.bin>'
    ;;
  release_package)
    run_or_print "Run release package reference contract." python3 utils/build.py --generate-dfu
    ;;
  release_packages)
    run_or_print "Run release package reference contract." python3 utils/build.py --generate-dfu
    ;;
  *)
    printf 'Unknown Bazel reference contract target: %s\n' "$command_name" >&2
    exit 2
    ;;
esac
