#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase32_producer_test_support import *


class Phase32BlockerRegisterTriageTest(Phase32BlockerRegisterTriageTestBase):

    def test_contract_only_accepts_complete_phase32_contract(self) -> None:
        # Arrange / Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("phase32_blocker_register_triage_contract",
                      result.stdout)

    def test_non_final_reason_taxonomy_remains_proof_ineligible(self) -> None:
        # Arrange
        module = self.load_module()
        cases = [
            ("smoke fixture from local workflow", "smoke_fixture"),
            ("local-only dry run output", "local_dry_run"),
            ("prose-only maintainer attestation", "prose_attestation"),
            ("upstream-row-only submission without source packet",
             "row_only_submission"),
            ("stale lifecycle id from older phase", "lifecycle_mismatch"),
        ]

        for reason, expected_problem_kind in cases:
            with self.subTest(reason=reason):
                signal = {
                    "source_stream": "release-signing",
                    "finality_status": "rejected-final",
                    "failure_reason": reason,
                }

                # Act
                classification = module.classify_signal(signal)

                # Assert
                self.assert_ineligible_policy(classification,
                                              expected_problem_kind,
                                              "repair_item")

    def test_quick_writes_canonical_register_and_handoff_artifacts(
            self) -> None:
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
        for path in [
                "blocker-register.json",
                "decision-impact-index.json",
                "exception-request-register.json",
                "residual-risk-request-register.json",
                "downstream-handoff-manifest.json",
                "redacted-blocker-register-report.md",
                "contract-snapshots/phase32_blocker_register_triage_contract.json",
                "contract-snapshots/phase31_final_evidence_intake_contract.json",
                "contract-snapshots/phase23_simulator_evidence_execution_contract.json",
                "contract-snapshots/phase24_hardware_media_safety_evidence_execution_contract.json",
                "contract-snapshots/phase25_live_service_evidence_execution_contract.json",
                "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json",
                "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
                "contract-snapshots/phase28_final_readiness_packet_contract.json",
        ]:
            self.assertTrue(
                (root / "build/ci-evidence/phase32" / path).exists(), path)
        register = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")
        rows = register["rows"]
        self.assertTrue(rows)
        self.assertTrue(all(REQUIRED_ROW_FIELDS <= set(row) for row in rows))

    def test_phase31_accepted_receipt_skips_clean_lifecycle_source_rows(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)
        receipt_ref = "build/ci-evidence/phase31/stream-receipts/simulator-final-intake-receipt.json"
        clean_source_refs = [
            "build/ci-evidence/phase23/current-lifecycle-source-row.json",
            "build/ci-evidence/phase23/not-required-lifecycle-source-row.json",
        ]
        receipt = self.read_json(root, receipt_ref)
        receipt["consumed_upstream_row_refs"].extend(clean_source_refs)
        self.write_json(root, receipt_ref, receipt)
        for source_ref, lifecycle_status in zip(clean_source_refs,
                                                ["current", "not-required"]):
            self.write_json(
                root,
                source_ref,
                {
                    "criterion_id": "final-simulator-evidence",
                    "evidence_family": "simulator",
                    "redaction_status": "passed",
                    "requirement_ids": ["EVID-01"],
                    "source_lifecycle_status": lifecycle_status,
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
        emitted_refs = {row["source_ref"] for row in rows}
        self.assertTrue(
            all(source_ref not in emitted_refs
                for source_ref in clean_source_refs))

    def test_phase27_and_phase28_handoff_rows_are_included_without_approval_semantics(
            self) -> None:
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
        register_text = (
            root /
            "build/ci-evidence/phase32/blocker-register.json").read_text(
                encoding="utf-8")
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        self.assertIn("retained-code", {row["source_stream"] for row in rows})
        self.assertIn("readiness", {row["source_stream"] for row in rows})
        self.assertNotIn("demotion_allowed", register_text)
        self.assertNotIn("final_readiness_status", register_text)
        self.assertNotIn("cutover verdict approved", register_text.casefold())

    def test_phase27_final_readiness_exception_keeps_original_affected_gate(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)
        expected_ref = "build/ci-evidence/phase27/exception-decision-register.json#final-live-network-transfer-evidence"

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
        exception_rows = [
            row for row in rows if row["source_ref"] == expected_ref
        ]
        self.assertEqual(len(exception_rows), 1)
        self.assertEqual(exception_rows[0]["source_stream"], "readiness")
        self.assertEqual(exception_rows[0]["affected_gate"],
                         "final-live-network-transfer-evidence")

    def test_derived_views_reference_canonical_row_ids(self) -> None:
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
        register_rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        register_ids = {row["row_id"] for row in register_rows}
        for path in [
                "decision-impact-index.json",
                "exception-request-register.json",
                "residual-risk-request-register.json",
        ]:
            rows = self.read_json(root,
                                  f"build/ci-evidence/phase32/{path}")["rows"]
            self.assertTrue(rows, path)
            self.assertTrue(all(row["row_id"] in register_ids for row in rows),
                            path)


class Phase32ProducerShapeTest(Phase32ProducerShapeTestBase):

    def test_phase27_residual_empty_rows_remain_valid(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase27/residual-risk-register.json")
        residual = self.read_json(root, artifact_path)
        residual["rows"] = []
        self.write_json(root, artifact_path, residual)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_empty_collection_publication(root, artifact_path)

    def test_phase27_exception_empty_rows_remain_valid(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase27/exception-decision-register.json")
        exceptions = self.read_json(root, artifact_path)
        exceptions["rows"] = []
        self.write_json(root, artifact_path, exceptions)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_empty_collection_publication(root, artifact_path)

    def test_phase28_blocker_empty_blockers_remain_valid(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = "build/ci-evidence/phase28/blocker-summary.json"
        blocker_summary = self.read_json(root, artifact_path)
        blocker_summary["blockers"] = []
        self.write_json(root, artifact_path, blocker_summary)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_empty_collection_publication(root, artifact_path)

    def test_phase28_residual_empty_rows_remain_valid(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase28/exception-residual-risk-summary.json")
        residual = self.read_json(root, artifact_path)
        residual["rows"] = []
        self.write_json(root, artifact_path, residual)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_empty_collection_publication(root, artifact_path)

    def test_nested_phase27_bundle_preserves_canonical_semantics(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        baseline_result = self.run_phase32(root)
        self.assertEqual(baseline_result.returncode, 0, baseline_result.stdout)
        baseline_rows = self.assert_phase32_bundle(root)
        baseline_semantics = self.canonical_phase_semantics(
            baseline_rows, "phase27")
        nested_output_dir = self.nest_output_dir(root,
                                                 "build/ci-evidence/phase27")

        # Act
        result = self.run_phase32(root, phase27_output_dir=nested_output_dir)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        nested_rows = self.assert_phase32_bundle(root)
        self.assertEqual(
            self.canonical_phase_semantics(nested_rows, "phase27"),
            baseline_semantics,
        )
        self.assertTrue(
            all(row["source_ref"].startswith(f"{nested_output_dir}/")
                for row in nested_rows if row["producer_phase"] == "phase27"))

    def test_nested_phase28_bundle_preserves_canonical_semantics(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        baseline_result = self.run_phase32(root)
        self.assertEqual(baseline_result.returncode, 0, baseline_result.stdout)
        baseline_rows = self.assert_phase32_bundle(root)
        baseline_semantics = self.canonical_phase_semantics(
            baseline_rows, "phase28")
        nested_output_dir = self.nest_output_dir(root,
                                                 "build/ci-evidence/phase28")

        # Act
        result = self.run_phase32(root, phase28_output_dir=nested_output_dir)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        nested_rows = self.assert_phase32_bundle(root)
        self.assertEqual(
            self.canonical_phase_semantics(nested_rows, "phase28"),
            baseline_semantics,
        )
        self.assertTrue(
            all(row["source_ref"].startswith(f"{nested_output_dir}/")
                for row in nested_rows if row["producer_phase"] == "phase28"))

    def test_all_passed_phase26_table_crosses_phase31_without_release_blocker(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        phase26_rows = self.read_json(
            root,
            "build/ci-evidence/phase26/upstream-result-row-table.json")["rows"]
        receipt = self.read_json(
            root,
            "build/ci-evidence/phase31/stream-receipts/release-signing-final-intake-receipt.json"
        )
        register_rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        self.assertTrue(all(row["status"] == "passed" for row in phase26_rows))
        self.assertEqual(receipt["finality_status"], "accepted-final")
        self.assertEqual(
            receipt["consumed_upstream_row_refs"],
            ["build/ci-evidence/phase26/upstream-result-row-table.json"],
        )
        self.assertFalse([
            row for row in register_rows
            if row["source_domain"] == "release_signing"
        ])

    def test_phase27_and_phase28_producers_preserve_all_decision_identities(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        register_path = "build/ci-evidence/phase32/blocker-register.json"
        rows = self.read_json(root, register_path)["rows"]
        decision_rows = [
            row for row in rows
            if row["producer_phase"] in {"phase27", "phase28"}
        ]
        self.assertEqual(
            {row["decision_axis"]
             for row in decision_rows},
            {
                "retained_code",
                "residual_risk",
                "exception",
                "readiness",
                "demotion",
            },
        )
        self.assertTrue(
            any(row["decision_axis"] == "retained_code"
                and row["source_subject_id"].startswith("packet-")
                for row in decision_rows))
        self.assertTrue(
            any(row["decision_axis"] == "exception"
                and row["source_subject_id"].startswith("packet-")
                for row in decision_rows))
        self.assertTrue(
            any(row["decision_axis"] == "readiness"
                and row["source_subject_id"] == "final-maintainer-decision"
                for row in decision_rows))
        demotion_rows = [
            row for row in decision_rows if row["decision_axis"] == "demotion"
        ]
        self.assertTrue(demotion_rows)
        self.assertEqual(
            {row["decision_subject_id"]
             for row in demotion_rows},
            {"final-reference-demotion-allowed"},
        )
        register_text = (root / register_path).read_text(encoding="utf-8")
        self.assertNotIn("demotion_allowed", register_text)
        self.assertNotIn("final readiness approved", register_text.casefold())
        self.assertTrue(
            all(row["proof_eligibility"] == "ineligible"
                for row in decision_rows))

        before_ids = {
            (row["producer_artifact_kind"], row["source_subject_id"]):
            row["row_id"]
            for row in decision_rows if row["decision_axis"] == "retained_code"
        }
        residual_path = "build/ci-evidence/phase27/residual-risk-register.json"
        residual_register = self.read_json(root, residual_path)
        residual_register["rows"][0]["owner"] = "changed-owner"
        residual_register["rows"][0][
            "residual_risk"] = "Changed mutable risk wording."
        self.write_json(root, residual_path, residual_register)
        rerun = self.run_phase32(root)
        self.assertEqual(rerun.returncode, 0, rerun.stdout)
        rerun_rows = self.read_json(root, register_path)["rows"]
        after_ids = {
            (row["producer_artifact_kind"], row["source_subject_id"]):
            row["row_id"]
            for row in rerun_rows
            if row["producer_phase"] in {"phase27", "phase28"}
            and row["decision_axis"] == "retained_code"
        }
        self.assertEqual(before_ids, after_ids)


from phase32_blocker_register_triage_failure_test import Phase32BlockerRegisterTriageFailureTest
from phase32_blocker_register_triage_producer_failure_test import Phase32ProducerShapeFailureTest

if __name__ == "__main__":
    unittest.main()
