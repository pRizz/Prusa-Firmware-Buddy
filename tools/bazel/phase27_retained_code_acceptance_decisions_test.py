#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase27_retained_code_acceptance_decisions_failure_test import *
from phase27_decision_test_support import *


class Phase27RetainedCodeAcceptanceDecisionsTest(
        Phase27RetainedCodeAcceptanceDecisionsFailureTests,
        Phase27DecisionTestSupport, unittest.TestCase):

    def test_contract_only_exact_matches_phase18_canonical_surfaces(
            self) -> None:
        # Arrange
        module = self.load_verifier_module()
        phase18_contract = self.read_json(ROOT, PHASE18_CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])
        surfaces = module.check_phase18_surfaces(phase18_contract)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(surfaces["retained_packet_ids"],
                         REQUIRED_RETAINED_PACKET_IDS)
        self.assertEqual(surfaces["upstream_criterion_ids"],
                         REQUIRED_UPSTREAM_CRITERION_IDS)
        self.assertEqual(
            surfaces["retained_required_fields"],
            phase18_contract["retained_code_acceptance_packet_schema"]
            ["required_fields"],
        )
        self.assertEqual(
            surfaces["final_decision_required_fields"],
            phase18_contract["final_decision_schema"]["required_fields"],
        )
        self.assertEqual(
            surfaces["exception_required_fields"],
            phase18_contract["final_decision_schema"]["exception"]
            ["required_fields"],
        )
        self.assertEqual(surfaces["retained_packet_status_vocabulary"],
                         phase18_contract["retained_packet_status_vocabulary"])
        self.assertEqual(surfaces["final_criterion_status_vocabulary"],
                         phase18_contract["final_criterion_status_vocabulary"])
        self.assertEqual(surfaces["review_decision_vocabulary"],
                         phase18_contract["review_decision_vocabulary"])
        self.assertEqual(
            surfaces["hard_blocker_reasons"],
            phase18_contract["upstream_result_requirements"][0]
            ["hard_blocker_reasons"],
        )

    def test_contract_declares_exact_decision_axes(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(contract["decision_axes"], DECISION_AXES)

    def test_contract_declares_generated_artifacts(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)

    def test_contract_keeps_phase27_demotion_authorization_blocked(
            self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        handoff_policy = contract["phase28_handoff_policy"]
        self.assertEqual(handoff_policy["demotion_authorization"], "blocked")
        self.assertFalse(handoff_policy["phase27_may_authorize_demotion"])

    def test_verifier_does_not_use_shell_or_inline_interpreters(self) -> None:
        # Arrange
        source = VERIFIER.read_text(encoding="utf-8")

        # Act / Assert
        for forbidden in ["shell=True", "bash -c", "python -c", "node -e"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_quick_generates_template_and_all_expected_artifacts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for artifact in GENERATED_ARTIFACTS:
                self.assertTrue(
                    (root / DEFAULT_OUTPUT_DIR / artifact).exists(), artifact)
            template = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/maintainer-acceptance-input-template.json"
            )
            self.assertEqual(len(template["retained_code_decisions"]),
                             len(REQUIRED_RETAINED_PACKET_IDS))
            self.assertEqual(len(template["final_readiness_decisions"]),
                             len(REQUIRED_UPSTREAM_CRITERION_IDS))
            decision_table = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/decision-row-table.json")
            self.assertEqual(
                len(decision_table["rows"]),
                len(REQUIRED_RETAINED_PACKET_IDS) +
                len(REQUIRED_UPSTREAM_CRITERION_IDS))
            handoff = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/phase28-handoff-manifest.json")
            self.assertEqual(handoff["demotion_authorization"], "blocked")
            self.assertFalse(handoff["phase27_may_authorize_demotion"])
            self.assertNotIn("demotion_allowed", json.dumps(handoff))

    def test_quick_rejects_phase26_lifecycle_identity_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            phase26_rows = self.read_json(root, PHASE26_ROWS)
            phase26_rows["rows"][0][
                "source_lifecycle_id"] = "stale-phase-lifecycle"
            self.write_json(root, PHASE26_ROWS, phase26_rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source_lifecycle_id must match Phase 18", result.stdout)

    def test_quick_normalizes_approve_reject_and_exception_decisions(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            retained_rows = maintainer_input["retained_code_decisions"]
            retained_rows[1]["decision"] = "reject"
            retained_rows[1][
                "rationale"] = "Maintainer rejected this retained-code packet for Phase 27 test input."
            retained_rows[2]["decision"] = "exception"
            retained_rows[2]["exception"] = {
                "scope":
                "phase27 test exception scope",
                "rationale":
                "Temporary exception is explicitly documented for maintainer review.",
                "approver":
                "phase27-test-maintainer",
                "approver_role":
                retained_rows[2]["approver_role"],
                "affected_printer_or_release_surface":
                "print core retained packet",
                "mitigation_or_follow_up":
                "Track exception in Phase 28 readiness review.",
                "expiry_or_review_trigger":
                "Phase 28 reference-demotion decision",
                "evidence_refs":
                retained_rows[2]["evidence_refs"],
                "residual_risk":
                "Exception residual risk accepted for test input.",
            }
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            normalized = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/normalized-retained-code-decisions.json"
            )
            by_id = {row["packet_id"]: row for row in normalized["rows"]}
            self.assertEqual(by_id["packet-hal-cmsis-startup-asm"]["status"],
                             "accepted")
            self.assertEqual(by_id["packet-freertos-runtime"]["status"],
                             "rejected")
            self.assertEqual(
                by_id["packet-marlin-cpp-print-core-oracle"]["status"],
                "deferred-approved-exception")
            exceptions = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/exception-decision-register.json")
            self.assertEqual(len(exceptions["rows"]), 1)
            self.assertEqual(exceptions["rows"][0]["owner"],
                             "phase27-test-maintainer")

    def test_hard_blocker_runs_before_exception_handling(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            retained_row = maintainer_input["retained_code_decisions"][0]
            retained_row["decision"] = "exception"
            retained_row["hard_failure_reasons"] = ["redaction-failed"]
            retained_row["exception"] = {
                "scope": "phase27 test exception scope",
                "rationale":
                "Exception would otherwise be valid, but hard blockers win.",
                "approver": "phase27-test-maintainer",
                "approver_role": retained_row["approver_role"],
                "affected_printer_or_release_surface":
                "startup retained packet",
                "mitigation_or_follow_up": "Fix redaction first.",
                "expiry_or_review_trigger": "redaction pass",
                "evidence_refs": retained_row["evidence_refs"],
                "residual_risk":
                "Residual risk cannot be accepted while redaction is blocked.",
                "owner": "phase27-test-maintainer",
            }
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            normalized = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/normalized-retained-code-decisions.json"
            )
            first_row = normalized["rows"][0]
            self.assertEqual(first_row["status"], "rejected-redaction")
            self.assertEqual(first_row["exception_state"],
                             "blocked-by-hard-failure")

    def test_wiring_only_validates_bazel_wrapper_and_just_targets(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
