#!/usr/bin/env bash
set -euo pipefail

root="${BUILD_WORKSPACE_DIRECTORY:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
command_name="$(basename "$0")"

cd "$root"
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$root/target/rust}"

case "$command_name" in
  rust_format_check)
    cargo fmt --all -- --check
    ;;
  rust_lint)
    cargo clippy --all-targets --all-features -- -D warnings
    ;;
  rust_unit_tests)
    cargo test --all-features
    ;;
  rust_docs)
    cargo doc --workspace --all-features --no-deps
    ;;
  rust_build|rust_firmware)
    cargo build --workspace --all-features
    ;;
  phase4_verify)
    python3 tools/bazel/phase4_verify.py --all
    ;;
  phase5_verify)
    python3 tools/bazel/phase5_verify.py --all
    ;;
  phase6_verify)
    python3 tools/bazel/phase6_verify.py --all
    ;;
  phase6_verify_tests)
    python3 tools/bazel/phase6_verify_test.py
    ;;
  phase7_verify)
    python3 tools/bazel/phase7_verify.py --all
    ;;
  phase7_verify_tests)
    python3 tools/bazel/phase7_verify_test.py
    ;;
  phase8_verify)
    python3 tools/bazel/phase8_verify.py --all
    ;;
  phase8_verify_tests)
    python3 tools/bazel/phase8_verify_test.py
    ;;
  phase9_verify)
    python3 tools/bazel/phase9_verify.py --all
    ;;
  phase9_verify_tests)
    python3 tools/bazel/phase9_verify_test.py
    python3 tools/bazel/phase9_negative_fixtures_test.py
    ;;
  phase10_verify)
    python3 tools/bazel/phase10_verify.py --wiring-only
    python3 tools/bazel/phase10_verify.py --all
    ;;
  phase10_verify_tests)
    python3 tools/bazel/phase10_verify_test.py
    ;;
  phase11_verify)
    python3 tools/bazel/phase11_verify.py --wiring-only
    python3 tools/bazel/phase11_verify.py --quick
    ;;
  phase11_verify_tests)
    python3 tools/bazel/phase11_verify_test.py
    ;;
  phase13_verify)
    python3 tools/bazel/phase13_ci_evidence.py --wiring-only
    python3 tools/bazel/phase13_ci_evidence.py --quick
    ;;
  phase13_verify_tests)
    python3 tools/bazel/phase13_ci_evidence_test.py
    ;;
  phase14_verify)
    python3 tools/bazel/phase14_simulator_evidence.py --wiring-only
    python3 tools/bazel/phase14_simulator_evidence.py --quick
    ;;
  phase14_verify_tests)
    python3 tools/bazel/phase14_simulator_evidence_test.py
    ;;
  phase15_verify)
    python3 tools/bazel/phase15_hardware_evidence.py --wiring-only
    python3 tools/bazel/phase15_hardware_evidence.py --quick
    ;;
  phase15_verify_tests)
    python3 tools/bazel/phase15_hardware_evidence_test.py
    ;;
  phase16_verify)
    python3 tools/bazel/phase16_live_network_evidence.py --wiring-only
    python3 tools/bazel/phase16_live_network_evidence.py --quick
    ;;
  phase16_verify_tests)
    python3 tools/bazel/phase16_live_network_evidence_test.py
    ;;
  phase17_verify)
    python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only
    python3 tools/bazel/phase17_release_candidate_evidence.py --quick
    ;;
  phase17_verify_tests)
    python3 tools/bazel/phase17_release_candidate_evidence_test.py
    ;;
  phase18_verify)
    python3 tools/bazel/phase18_cutover_review.py --wiring-only
    python3 tools/bazel/phase18_cutover_review.py --quick
    ;;
  phase18_verify_tests)
    python3 tools/bazel/phase18_cutover_review_test.py
    ;;
  *)
    printf 'Unknown Rust workflow target: %s\n' "$command_name" >&2
    exit 2
    ;;
esac
