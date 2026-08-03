#!/usr/bin/env bash
set -euo pipefail

root="${BUILD_WORKSPACE_DIRECTORY:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
command_name="$(basename "$0")"

run_reference() {
  local description="$1"
  shift

  printf '%s\n' "$description"
  printf 'reference command:'
  printf ' %q' "$@"
  printf '\n'
  (cd "$root" && "$@")
}

print_reference_plan() {
  local description="$1"
  shift

  printf '%s\n' "$description"
  printf 'reference command:'
  printf ' %q' "$@"
  printf '\n'
}

require_simulator_firmware() {
  if [[ "$#" -ne 1 || -z "$1" ]]; then
    printf 'Usage: bazel run //tools/bazel:reference_simulator -- <firmware.bin>\n' >&2
    exit 2
  fi

  local firmware="$1"
  local resolved_firmware="$firmware"
  if [[ "$firmware" != /* ]]; then
    resolved_firmware="$root/$firmware"
  fi
  if [[ ! -f "$resolved_firmware" ]]; then
    printf 'Reference simulator firmware does not exist: %s\n' "$firmware" >&2
    exit 2
  fi
}

case "$command_name" in
  reference_build)
    run_reference "Execute the CMake/Python reference firmware build." python3 utils/build.py
    ;;
  reference_build_plan)
    print_reference_plan "Preview the CMake/Python reference firmware build." python3 utils/build.py
    ;;
  reference_test)
    run_reference "Execute the retained host-test reference workflow." sh -c 'mkdir -p build-tests && cd build-tests && cmake .. -DBOARD=BUDDY && make tests && ctest .'
    ;;
  reference_test_plan)
    print_reference_plan "Preview the retained host-test reference workflow." sh -c 'mkdir -p build-tests && cd build-tests && cmake .. -DBOARD=BUDDY && make tests && ctest .'
    ;;
  reference_package)
    run_reference "Execute the retained reference packaging workflow." python3 utils/build.py --generate-dfu
    ;;
  reference_package_plan)
    print_reference_plan "Preview the retained reference packaging workflow." python3 utils/build.py --generate-dfu
    ;;
  reference_simulator)
    require_simulator_firmware "$@"
    run_reference "Execute the retained simulator reference workflow." pytest tests/integration --firmware "$1"
    ;;
  reference_simulator_plan)
    print_reference_plan "Preview the retained simulator reference workflow." pytest tests/integration --firmware "<firmware.bin>"
    ;;
  *)
    printf 'Unknown Bazel reference contract target: %s\n' "$command_name" >&2
    exit 2
    ;;
esac
