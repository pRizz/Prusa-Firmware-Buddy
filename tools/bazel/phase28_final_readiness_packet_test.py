#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase28_final_readiness_packet_failure_test import *
from phase28_readiness_test_support import *


class Phase28FinalReadinessPacketTest(Phase28FinalReadinessPacketFailureTests,
                                      Phase28ReadinessTestSupport,
                                      unittest.TestCase):

    def test_contract_only_accepts_checked_in_contract(self) -> None:
        # Arrange
        args = ["--contract-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_declares_exact_requirements_criteria_and_outputs(
            self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual([row["id"] for row in contract["requirements"]],
                         REQUIRED_REQUIREMENTS)
        self.assertEqual(
            contract["readiness_policy"]["canonical_phase18_criteria"],
            REQUIRED_CRITERIA)
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)
        self.assertEqual(
            contract["top_level_verdicts"],
            ["final_readiness_status", "reference_demotion_authorization"])

    def test_contract_keeps_phase27_handoff_blocked(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            contract["phase27_handoff_policy"]["demotion_authorization"],
            "blocked")
        self.assertFalse(contract["phase27_handoff_policy"]
                         ["phase27_may_authorize_demotion"])

    def test_contract_requires_explicit_demotion_decision_metadata(
            self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            contract["demotion_decision_schema"]["required_fields"],
            [
                "phase",
                "phase_lifecycle_id",
                "demotion_authorization",
                "approver",
                "approver_role",
                "decision_timestamp",
                "rationale",
                "scope",
                "evidence_refs",
            ],
        )

    def test_contract_does_not_authorize_demotion_from_evidence(self) -> None:
        # Arrange
        contract_text = (ROOT / CONTRACT).read_text(encoding="utf-8")
        test_text = Path(__file__).read_text(encoding="utf-8")
        approval_pair = '"demotion_authorization": ' + '"approved"'

        # Act / Assert
        self.assertNotIn(approval_pair, contract_text)
        self.assertNotIn(approval_pair, test_text)
        self.assertIn('"evidence_status_never_implies_approval": true',
                      contract_text)

    def test_quick_generates_all_outputs_and_keeps_demotion_blocked_without_decision(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for artifact in GENERATED_ARTIFACTS:
                self.assertTrue(
                    (root / DEFAULT_OUTPUT_DIR / artifact).exists(), artifact)
            packet = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            self.assertEqual(packet["final_readiness_status"], "unblocked")
            self.assertEqual(packet["reference_demotion_authorization"],
                             "blocked")
            self.assertFalse(
                packet["real_maintainer_demotion_approval_supplied"])
            self.assertEqual(
                {row["criterion_id"]
                 for row in packet["criteria"]}, set(REQUIRED_CRITERIA))
            self.assertIn("requirements", packet)

    def test_packet_carries_consumed_phase23_24_25_refs_from_phase26_rows(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase26_rows = self.consumed_phase26_rows(root)
            phase27_rows = self.phase27_final_rows(phase26_rows)
            for row in phase27_rows:
                criterion_id = str(row["criterion_id"])
                if criterion_id in {
                        "final-simulator-evidence",
                        "final-hardware-safety-media-evidence",
                        "final-live-network-transfer-evidence",
                }:
                    row["evidence_refs"] = [
                        f"build/ci-evidence/phase27/final-readiness-decision-summary.json#{criterion_id}"
                    ]
                    row["artifact_refs"] = [
                        f"build/ci-evidence/phase27/decision-row-table.json#{criterion_id}"
                    ]
            self.write_phase_inputs(root, phase26_rows, phase27_rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            packet = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            criteria = {row["criterion_id"]: row for row in packet["criteria"]}
            expected_rows = {
                "final-simulator-evidence": {
                    "requirement_ids": ["EVID-01", "ACPT-01"],
                    "manifest_ref":
                    "build/ci-evidence/phase23/simulator-result-manifest.json",
                    "input_row_ref":
                    "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                    "external_ref":
                    "external://phase23/simulator/startup-log.json",
                },
                "final-hardware-safety-media-evidence": {
                    "requirement_ids": ["EVID-02", "ACPT-01"],
                    "manifest_ref":
                    "build/ci-evidence/phase24/hardware-media-safety-result-manifest.json",
                    "input_row_ref":
                    "build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json",
                    "external_ref":
                    "external://phase24/hardware/safety-report.json",
                },
                "final-live-network-transfer-evidence": {
                    "requirement_ids": ["EVID-03", "ACPT-01"],
                    "manifest_ref":
                    "build/ci-evidence/phase25/live-service-result-manifest.json",
                    "input_row_ref":
                    "build/ci-evidence/phase25/upstream-live-service-result-row.json",
                    "external_ref":
                    "external://phase25/live-service/connect-report.json",
                },
            }
            for criterion_id, expected in expected_rows.items():
                with self.subTest(criterion_id=criterion_id):
                    row = criteria[criterion_id]
                    phase27_ref = f"build/ci-evidence/phase27/final-readiness-decision-summary.json#{criterion_id}"
                    self.assertEqual(row["requirement_ids"],
                                     expected["requirement_ids"])
                    self.assertIn(expected["manifest_ref"], row["source_refs"])
                    self.assertIn(expected["input_row_ref"],
                                  row["source_refs"])
                    self.assertIn(expected["manifest_ref"],
                                  row["evidence_refs"])
                    self.assertIn(expected["input_row_ref"],
                                  row["evidence_refs"])
                    self.assertIn(phase27_ref, row["evidence_refs"])
                    self.assertIn(expected["external_ref"],
                                  row["artifact_refs"])
                    self.assertIn(expected["input_row_ref"],
                                  row["artifact_refs"])

    def test_consumed_upstream_rows_do_not_authorize_reference_demotion_without_decision(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root, self.consumed_phase26_rows(root))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            packet = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            demotion_row = next(
                row for row in packet["criteria"]
                if row["criterion_id"] == "final-reference-demotion-allowed")
            self.assertEqual(packet["final_readiness_status"], "unblocked")
            self.assertEqual(packet["reference_demotion_authorization"],
                             "blocked")
            self.assertFalse(
                packet["real_maintainer_demotion_approval_supplied"])
            self.assertEqual(demotion_row["readiness_effect"],
                             "blocked-pending-explicit-demotion-decision")
            self.assertEqual(demotion_row["demotion_gate_effect"],
                             "requires-explicit-phase28-decision")

    def test_valid_exception_covers_coverable_failure(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase26_rows = self.phase26_rows(root)
            phase26_rows[0]["status"] = "failed"
            phase26_rows[0][
                "failure_reason"] = "Operator documented a coverable exception."
            phase27_rows = self.phase27_final_rows(phase26_rows)
            phase27_rows[0]["status"] = "exception-approved"
            phase27_rows[0]["decision"] = "exception"
            phase27_rows[0]["exception_state"] = "approved-exception"
            phase27_rows[0]["exception"] = self.exception_metadata(
                str(phase26_rows[0]["criterion_id"]))
            self.write_phase_inputs(root, phase26_rows, phase27_rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            table = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/normalized-readiness-criteria-table.json"
            )
            row = next(row for row in table["rows"]
                       if row["criterion_id"] == "final-ci-evidence")
            self.assertEqual(row["readiness_effect"], "exception-covered")
            self.assertEqual(row["exception_state"], "covered")

    def test_security_scan_accepts_approved_demotion_input_after_unblocked_packet(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            decision_path = self.write_json(root, "demotion-decision.json",
                                            self.demotion_decision("approved"))
            quick_result = self.run_verifier(
                ["--quick", "--demotion-decision-input", decision_path],
                maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            packet = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            self.assertEqual(packet["final_readiness_status"], "unblocked")
            self.assertEqual(packet["reference_demotion_authorization"],
                             "approved")
            demotion_row = next(
                row for row in packet["criteria"]
                if row["criterion_id"] == "final-reference-demotion-allowed")
            self.assertEqual(demotion_row["readiness_effect"],
                             "reference-demotion-authorized")
            self.assertEqual(demotion_row["demotion_gate_effect"],
                             "explicit-phase28-decision-approved")
            blockers = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/blocker-summary.json")
            blocker_ids = {row["criterion_id"] for row in blockers["blockers"]}
            self.assertNotIn("final-reference-demotion-allowed", blocker_ids)
            report = (root / DEFAULT_OUTPUT_DIR /
                      "redacted-readiness-report.md").read_text(
                          encoding="utf-8")
            self.assertIn(
                "final-reference-demotion-allowed -> reference-demotion-authorized",
                report)
            self.assertNotIn("blocked-pending-explicit-demotion-decision",
                             report)

            # Act
            result = self.run_verifier([
                "--security-only", "--demotion-decision-input", decision_path
            ],
                                       maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_report_is_derived_from_packet_and_names_review_boundary(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            report = (root / DEFAULT_OUTPUT_DIR /
                      "redacted-readiness-report.md").read_text(
                          encoding="utf-8")
            packet = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            self.assertIn("Review material only", report)
            self.assertIn(
                f"final_readiness_status: {packet['final_readiness_status']}",
                report)
            self.assertIn("reference_demotion_authorization: blocked", report)

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
