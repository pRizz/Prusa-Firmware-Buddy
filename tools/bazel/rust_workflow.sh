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
  phase19_verify)
    python3 tools/bazel/phase19_aggregate_ci_evidence.py --wiring-only
    python3 tools/bazel/phase19_aggregate_ci_evidence.py --ci --output-dir build/ci-evidence/phase19
    ;;
  phase19_verify_tests)
    python3 tools/bazel/phase19_aggregate_ci_evidence_test.py
    ;;
  phase20_verify)
    python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only
    python3 tools/bazel/phase20_release_candidate_artifacts.py --quick
    ;;
  phase20_verify_tests)
    python3 tools/bazel/phase20_release_candidate_artifacts_test.py
    ;;
  phase22_verify)
    python3 tools/bazel/phase22_metadata_reconciliation.py --wiring-only
    python3 tools/bazel/phase22_metadata_reconciliation.py --quick --output-dir build/ci-evidence/phase22
    ;;
  phase22_verify_tests)
    python3 tools/bazel/phase22_metadata_reconciliation_test.py
    ;;
  phase23_verify)
    python3 tools/bazel/phase23_simulator_evidence_execution.py --wiring-only
    python3 tools/bazel/phase23_simulator_evidence_execution.py --quick --output-dir build/ci-evidence/phase23
    ;;
  phase23_verify_tests)
    python3 tools/bazel/phase23_simulator_evidence_execution_test.py
    ;;
  phase24_verify)
    python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --wiring-only
    python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --quick --output-dir build/ci-evidence/phase24
    ;;
  phase24_verify_tests)
    python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py
    ;;
  phase25_verify)
    python3 tools/bazel/phase25_live_service_evidence_execution.py --wiring-only
    python3 tools/bazel/phase25_live_service_evidence_execution.py --quick --output-dir build/ci-evidence/phase25
    ;;
  phase25_verify_tests)
    python3 tools/bazel/phase25_live_service_evidence_execution_test.py
    ;;
  phase26_verify)
    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --wiring-only
    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26
    ;;
  phase26_verify_tests)
    python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py
    ;;
  phase27_verify)
    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --wiring-only
    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26
    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27
    ;;
  phase27_verify_tests)
    python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py
    ;;
  phase28_verify)
    python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only
    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26
    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27
    python3 tools/bazel/phase28_final_readiness_packet.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json --output-dir build/ci-evidence/phase28
    ;;
  phase28_verify_tests)
    python3 tools/bazel/phase28_final_readiness_packet_test.py
    ;;
  phase31_verify)
    python3 tools/bazel/phase31_final_evidence_intake.py --wiring-only
    python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31
    ;;
  phase31_verify_tests)
    python3 tools/bazel/phase31_final_evidence_intake_test.py
    ;;
  phase32_verify)
    python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31
    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26
    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27
    python3 tools/bazel/phase28_final_readiness_packet.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json --output-dir build/ci-evidence/phase28
    python3 tools/bazel/phase32_blocker_register_triage.py --wiring-only
    python3 tools/bazel/phase32_blocker_register_triage.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase27-output-dir build/ci-evidence/phase27 --phase28-output-dir build/ci-evidence/phase28 --output-dir build/ci-evidence/phase32
    ;;
  phase32_verify_tests)
    python3 tools/bazel/phase32_blocker_normalization_test.py
    python3 tools/bazel/phase32_blocker_register_triage_test.py
    ;;
  phase33_verify)
    python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31
    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26
    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27
    python3 tools/bazel/phase28_final_readiness_packet.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json --output-dir build/ci-evidence/phase28
    python3 tools/bazel/phase32_blocker_register_triage.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase27-output-dir build/ci-evidence/phase27 --phase28-output-dir build/ci-evidence/phase28 --output-dir build/ci-evidence/phase32
    python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only
    python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick --phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase33
    ;;
  phase33_verify_tests)
    python3 tools/bazel/phase33_maintainer_decision_inputs_test.py
    ;;
  phase34_verify)
    python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31
    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26
    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27
    python3 tools/bazel/phase28_final_readiness_packet.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json --output-dir build/ci-evidence/phase28
    python3 tools/bazel/phase32_blocker_register_triage.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase27-output-dir build/ci-evidence/phase27 --phase28-output-dir build/ci-evidence/phase28 --output-dir build/ci-evidence/phase32
    python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick --phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase33
    python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --wiring-only
    python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase33-handoff build/ci-evidence/phase33/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase34
    ;;
  phase34_verify_tests)
    python3 tools/bazel/phase33_maintainer_decision_inputs_test.py
    python3 tools/bazel/phase34_decision_reconciliation_test.py
    python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py
    python3 tools/bazel/phase34_decision_reconciliation_integration_test.py
    ;;
  phase35_verify)
    python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31
    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26
    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27
    python3 tools/bazel/phase28_final_readiness_packet.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json --output-dir build/ci-evidence/phase28
    python3 tools/bazel/phase32_blocker_register_triage.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase27-output-dir build/ci-evidence/phase27 --phase28-output-dir build/ci-evidence/phase28 --output-dir build/ci-evidence/phase32
    python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick --phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase33
    python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --wiring-only
    python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase33-handoff build/ci-evidence/phase33/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase34
    python3 tools/bazel/phase35_cutover_decision_artifact.py --wiring-only
    python3 tools/bazel/phase35_cutover_decision_artifact.py --quick --phase34-output-dir build/ci-evidence/phase34 --output-dir build/ci-evidence/phase35
    ;;
  phase35_verify_tests)
    python3 tools/bazel/phase35_cutover_decision_artifact_test.py
    ;;
  *)
    printf 'Unknown Rust workflow target: %s\n' "$command_name" >&2
    exit 2
    ;;
esac
