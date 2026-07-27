#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "tools/bazel").as_posix())

import phase38_cutover_workflow as workflow
from phase38_test_support import approved_authority, blocked_authority


class FinalStatusTests(unittest.TestCase):

    def test_successful_producers_preserve_blocked_targeted_repair(self) -> None:
        # Arrange
        authority = blocked_authority()

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 0)
        self.assertFalse(result.production_cutover_planning)
        self.assertEqual(result.route, "targeted-blocker-repair")

    def test_phase34_failure_remains_nonzero_after_safe_phase35_finalization(
        self,
    ) -> None:
        # Arrange
        authority = blocked_authority()

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(7, "phase31-input-invalid"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 7)
        self.assertEqual(result.reason_category, "phase31-input-invalid")
        self.assertFalse(result.production_cutover_planning)

    def test_phase35_failure_is_preserved_when_phase34_succeeds(self) -> None:
        # Arrange
        authority = blocked_authority()

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(9, "source-artifact-malformed"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 9)
        self.assertEqual(result.reason_category, "source-artifact-malformed")

    def test_phase34_failure_revokes_otherwise_open_authority(self) -> None:
        # Arrange
        authority = approved_authority(
            demotion_validation_state="valid",
            demotion_decision_state="approve",
            demotion_gate_state="open",
        )

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(7, "phase34-operation-failed"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 7)
        self.assertFalse(result.final_authority_available)
        self.assertFalse(result.production_cutover_planning)
        self.assertFalse(result.reference_demotion_authorized)

    def test_phase35_failure_revokes_otherwise_open_authority(self) -> None:
        # Arrange
        authority = approved_authority(
            demotion_validation_state="valid",
            demotion_decision_state="approve",
            demotion_gate_state="open",
        )

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(9, "phase35-operation-failed"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 9)
        self.assertFalse(result.final_authority_available)
        self.assertFalse(result.production_cutover_planning)
        self.assertFalse(result.reference_demotion_authorized)

    def test_first_nonzero_phase34_status_wins_when_both_producers_fail(
        self,
    ) -> None:
        # Arrange
        authority = blocked_authority()

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(5, "phase33-handoff-invalid"),
            workflow.CommandOutcome(8, "source-artifact-malformed"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 5)
        self.assertEqual(result.reason_category, "phase33-handoff-invalid")

    def test_missing_final_authority_fails_closed(self) -> None:
        # Arrange
        authority = workflow.FinalAuthority.unavailable(
            "phase35-authority-missing"
        )

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 1)
        self.assertEqual(result.reason_category, "phase35-authority-missing")

    def test_approved_authority_opens_only_production_cutover_planning(
        self,
    ) -> None:
        # Arrange
        authority = approved_authority()

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 0)
        self.assertTrue(result.production_cutover_planning)
        self.assertFalse(result.reference_demotion_authorized)

    def test_approved_verdict_with_targeted_repair_route_fails_closed(
        self,
    ) -> None:
        # Arrange
        authority = workflow.FinalAuthority(
            **{
                **approved_authority().__dict__,
                "route": "targeted-blocker-repair",
                "requires_fresh_cutover_decision": True,
            }
        )

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertEqual(result.status, 1)
        self.assertFalse(result.production_cutover_planning)
        self.assertEqual(
            result.reason_category,
            "phase35-authority-contradictory",
        )


class DemotionAuthorityTests(unittest.TestCase):

    def test_approved_cutover_with_missing_demotion_stays_closed(self) -> None:
        # Arrange
        authority = approved_authority()

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertFalse(result.reference_demotion_authorized)

    def test_approved_cutover_with_rejected_demotion_stays_closed(self) -> None:
        # Arrange
        authority = approved_authority(
            demotion_validation_state="valid",
            demotion_decision_state="reject",
        )

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertFalse(result.reference_demotion_authorized)

    def test_valid_demotion_with_blocked_readiness_stays_closed(self) -> None:
        # Arrange
        authority = workflow.FinalAuthority(
            **{
                **blocked_authority().__dict__,
                "demotion_validation_state": "valid",
                "demotion_decision_state": "approve",
                "demotion_gate_state": "open",
            }
        )

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertFalse(result.reference_demotion_authorized)

    def test_valid_approval_and_unblocked_readiness_open_demotion(self) -> None:
        # Arrange
        authority = approved_authority(
            demotion_validation_state="valid",
            demotion_decision_state="approve",
            demotion_gate_state="open",
        )

        # Act
        result = workflow.evaluate_final_status(
            workflow.CommandOutcome(0, "none"),
            workflow.CommandOutcome(0, "none"),
            authority,
        )

        # Assert
        self.assertTrue(result.reference_demotion_authorized)


class WiringTests(unittest.TestCase):

    def read_repo_file(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_tools_bazel_exposes_phase38_targets_and_runfiles(self) -> None:
        # Arrange
        build = self.read_repo_file("tools/bazel/BUILD.bazel")
        required = [
            'name = "phase38_actual_producer_runfiles"',
            'name = "phase38_verify"',
            'name = "phase38_verify_tests"',
            '"phase38_cutover_workflow.py"',
            '"phase38_cutover_workflow_test.py"',
            '"phase38_cutover_workflow_failure_test.py"',
            '"phase38_cutover_workflow_integration_test.py"',
            '"phase38_workflow_policy.py"',
            '"phase34_decision_reconciliation_integration_test.py"',
            '"phase35_cutover_decision_artifact_test.py"',
            '":phase38_actual_producer_runfiles"',
        ]

        # Act
        missing = [snippet for snippet in required if snippet not in build]

        # Assert
        self.assertEqual(missing, [])

    def test_phase38_runfiles_include_actual_producer_dependencies(
        self,
    ) -> None:
        # Arrange
        build = self.read_repo_file("tools/bazel/BUILD.bazel")
        required = [
            '"phase23_simulator_evidence_execution.py"',
            '"phase24_hardware_media_safety_evidence_execution.py"',
            '"phase25_live_service_evidence_execution.py"',
            '"phase26_release_signing_upstream_evidence.py"',
            '"phase27_retained_code_acceptance_decisions.py"',
            '"phase28_final_readiness_packet.py"',
            '"phase31_final_evidence_intake.py"',
            '"phase32_blocker_register_triage.py"',
            '"phase33_maintainer_decision_inputs.py"',
            '"phase34_final_readiness_demotion_dry_run.py"',
            '"phase35_cutover_decision_artifact.py"',
            '"manifests/phase35_cutover_decision_artifact_contract.json"',
        ]

        # Act
        missing = [snippet for snippet in required if snippet not in build]

        # Assert
        self.assertEqual(missing, [])

    def test_shell_uses_one_coordinator_with_explicit_status_propagation(
        self,
    ) -> None:
        # Arrange
        shell = self.read_repo_file("tools/bazel/rust_workflow.sh")
        required = [
            "run_phase38_coordinator() {",
            "if python3 tools/bazel/phase38_cutover_workflow.py --quick; then",
            "phase38_status=$?",
            'return "$phase38_status"',
            "python3 tools/bazel/phase38_cutover_workflow_failure_test.py",
            "phase38_verify)",
            "phase38_verify_tests)",
        ]

        # Act
        missing = [snippet for snippet in required if snippet not in shell]

        # Assert
        self.assertEqual(missing, [])
        phase35_body = shell.split("  phase35_verify)", 1)[1].split(
            "    ;;",
            1,
        )[0]
        self.assertEqual(
            phase35_body.count("run_phase38_coordinator"),
            1,
        )
        self.assertNotIn(
            "phase34_final_readiness_demotion_dry_run.py --quick",
            phase35_body,
        )
        self.assertNotIn(
            "phase35_cutover_decision_artifact.py --quick",
            phase35_body,
        )

    def test_root_bazel_exposes_phase38_aliases(self) -> None:
        # Arrange
        build = self.read_repo_file("BUILD.bazel")

        # Act / Assert
        self.assertIn(
            'name = "phase38_verify",\n'
            '    actual = "//tools/bazel:phase38_verify",',
            build,
        )
        self.assertIn(
            'name = "phase38_verify_tests",\n'
            '    actual = "//tools/bazel:phase38_verify_tests",',
            build,
        )

    def test_just_phase38_runs_tests_before_publication(self) -> None:
        # Arrange
        justfile = self.read_repo_file("justfile")
        expected_recipe = (
            "phase38-verify:\n"
            "    bazel run //tools/bazel:phase38_verify_tests\n"
            "    bazel run //tools/bazel:phase38_verify\n"
        )

        # Act
        maybe_recipe_index = justfile.find(expected_recipe)

        # Assert
        self.assertNotEqual(maybe_recipe_index, -1)


if __name__ == "__main__":
    unittest.main()
