#!/usr/bin/env python3
from __future__ import annotations

from phase32_test_support import *


class Phase32BlockerRegisterTriageFailureTest(
        Phase32BlockerRegisterTriageTestBase):

    def test_contract_validation_rejects_missing_required_policy_values(
            self) -> None:
        # Arrange
        module = self.load_module()
        contract = self.read_contract()
        contract["enums"]["blocker_kind"].remove("repair_item")

        # Act / Assert
        with self.assertRaises(module.VerificationError):
            module.validate_contract(contract)

    def test_contract_validation_rejects_missing_generated_artifact(
            self) -> None:
        # Arrange
        module = self.load_module()
        contract = self.read_contract()
        contract["generated_artifacts"].remove("blocker-register.json")

        # Act / Assert
        with self.assertRaises(module.VerificationError):
            module.validate_contract(contract)

    def test_contract_validation_rejects_fail_closed_policy_mismatches(
            self) -> None:
        # Arrange
        module = self.load_module()
        cases = [
            ("recognized_invalid_shape", "severity", "high"),
            ("recognized_invalid_shape", "proof_eligibility", "eligible"),
            ("unsupported_envelope_row_kind_or_status", "severity", "high"),
            ("unsupported_envelope_row_kind_or_status", "proof_eligibility",
             "eligible"),
        ]

        for policy_name, field, mismatched_value in cases:
            with self.subTest(policy_name=policy_name, field=field):
                contract = self.read_contract()
                contract["fail_closed_shape_policy"][policy_name][
                    field] = mismatched_value

                # Act / Assert
                with self.assertRaises(module.VerificationError):
                    module.validate_contract(contract)

    def test_unknown_signals_fail_closed_as_critical_decision_blockers(
            self) -> None:
        # Arrange
        module = self.load_module()
        signal = {
            "source_stream": "unknown",
            "status": "new-unmapped-status",
            "failure_reason": "unmapped evidence state",
        }

        # Act
        classification = module.classify_signal(signal)

        # Assert
        self.assertEqual(classification["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(classification["blocker_kind"],
                         "unresolved_decision_blocker")
        self.assertEqual(classification["severity"], "critical")
        self.assertEqual(classification["proof_eligibility"], "ineligible")

    def test_quick_default_rejections_are_non_final_placeholders(self) -> None:
        # Arrange
        module = self.load_module()
        signal = {
            "source_stream":
            "simulator",
            "finality_status":
            "quarantined-non-final",
            "failure_reason":
            "quick/default placeholder output is not final proof",
        }

        # Act
        classification = module.classify_signal(signal)

        # Assert
        self.assert_ineligible_policy(classification, "non_final_placeholder",
                                      "repair_item")

    def test_explicit_security_and_source_statuses_override_reason_taxonomy(
            self) -> None:
        # Arrange
        module = self.load_module()
        cases = [
            ({
                "redaction_status": "failed"
            }, "redaction_failed"),
            ({
                "redaction_status": "secret-tainted"
            }, "secret_tainted"),
            ({
                "source_ref_status": "unsafe-ref"
            }, "unsafe_ref"),
            ({
                "source_ref_status": "source-ref-failed"
            }, "source_ref_failed"),
            ({
                "source_lifecycle_status": "stale"
            }, "lifecycle_mismatch"),
        ]

        for status_fields, expected_problem_kind in cases:
            with self.subTest(expected_problem_kind=expected_problem_kind):
                signal = {
                    "source_stream": "simulator",
                    "failure_reason":
                    "quick default placeholder local-only workflow",
                    **status_fields,
                }

                # Act
                classification = module.classify_signal(signal)

                # Assert
                self.assertEqual(classification["row_problem_kind"],
                                 expected_problem_kind)
                self.assertEqual(classification["proof_eligibility"],
                                 "ineligible")

    def test_phase31_receipts_and_rejections_remain_fail_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)

        # Act
        result = self.run_temp_verifier(
            root,
            [
                "--quick",
                "--phase31-output-dir",
                "build/ci-evidence/phase31",
                "--phase27-output-dir",
                "build/ci-evidence/phase27",
                "--phase28-output-dir",
                "build/ci-evidence/phase28",
                "--output-dir",
                "build/ci-evidence/phase32",
            ],
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        problem_kinds = {row["row_problem_kind"] for row in rows}
        self.assertIn("non_final_placeholder", problem_kinds)
        self.assertIn("failed", problem_kinds)
        self.assertIn("missing", problem_kinds)
        self.assertTrue(
            all(row["proof_eligibility"] == "ineligible" for row in rows))

    def test_phase31_accepted_receipt_keeps_stale_lifecycle_source_row(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)
        receipt_ref = "build/ci-evidence/phase31/stream-receipts/simulator-final-intake-receipt.json"
        stale_source_row_ref = "build/ci-evidence/phase23/stale-lifecycle-source-row.json"
        receipt = self.read_json(root, receipt_ref)
        receipt["consumed_upstream_row_refs"].append(stale_source_row_ref)
        self.write_json(root, receipt_ref, receipt)
        self.write_json(
            root,
            stale_source_row_ref,
            {
                "criterion_id": "final-simulator-evidence",
                "evidence_family": "simulator",
                "redaction_status": "passed",
                "requirement_ids": ["EVID-01"],
                "source_lifecycle_status": "stale",
                "source_ref_status": "passed",
                "status": "passed",
            },
        )

        # Act
        result = self.run_temp_verifier(
            root,
            [
                "--quick",
                "--phase31-output-dir",
                "build/ci-evidence/phase31",
                "--phase27-output-dir",
                "build/ci-evidence/phase27",
                "--phase28-output-dir",
                "build/ci-evidence/phase28",
                "--output-dir",
                "build/ci-evidence/phase32",
            ],
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        stale_rows = [
            row for row in rows if row["source_ref"] == stale_source_row_ref
        ]
        self.assertEqual(len(stale_rows), 1)
        self.assertEqual(stale_rows[0]["row_problem_kind"],
                         "lifecycle_mismatch")

    def test_phase28_known_pending_statuses_are_classified_as_missing(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)
        blocker_summary_path = "build/ci-evidence/phase28/blocker-summary.json"
        blocker_summary = self.read_json(root, blocker_summary_path)
        blocker_summary["blockers"] = [
            {
                "criterion_id": f"readiness-{status}",
                "phase27_status": status,
                "phase26_status": "passed",
                "readiness_effect": "blocked",
            } for status in
            ["pending-ci-input", "pending-simulator-input", "not-required"]
        ]
        self.write_json(root, blocker_summary_path, blocker_summary)

        # Act
        result = self.run_temp_verifier(
            root,
            [
                "--quick",
                "--phase31-output-dir",
                "build/ci-evidence/phase31",
                "--phase27-output-dir",
                "build/ci-evidence/phase27",
                "--phase28-output-dir",
                "build/ci-evidence/phase28",
                "--output-dir",
                "build/ci-evidence/phase32",
            ],
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        readiness_rows = [
            row for row in rows if row["source_ref"].startswith(
                f"{blocker_summary_path}#readiness-")
        ]
        self.assertEqual(len(readiness_rows), 3)
        self.assertEqual({row["row_problem_kind"]
                          for row in readiness_rows}, {"missing"})

    def test_security_only_rejects_secret_and_approval_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_text(root, "build/ci-evidence/phase32/leak.json",
                        '{"demotion_allowed": true}\n')

        # Act
        result = self.run_temp_verifier(
            root,
            [
                "--security-only",
                "--output-dir",
                "build/ci-evidence/phase32",
            ],
        )

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("demotion_allowed", result.stdout)
