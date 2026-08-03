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
    run_reference "Execute the retained simulator reference workflow." sh -c 'pytest tests/integration --firmware <firmware.bin>'
    ;;
  reference_simulator_plan)
    print_reference_plan "Preview the retained simulator reference workflow." sh -c 'pytest tests/integration --firmware <firmware.bin>'
    ;;
  *)
    printf 'Unknown Bazel reference contract target: %s\n' "$command_name" >&2
    exit 2
    ;;
esac
