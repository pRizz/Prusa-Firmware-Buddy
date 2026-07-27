#!/usr/bin/env python3
from __future__ import annotations

from phase32_producer_test_support import *


class Phase32ProducerShapeFailureTest(Phase32ProducerShapeTestBase):

    def test_phase27_residual_missing_rows_is_malformed(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase27/residual-risk-register.json")
        residual = self.read_json(root, artifact_path)
        del residual["rows"]
        self.write_json(root, artifact_path, residual)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_container_problem(root, artifact_path, "malformed")

    def test_phase27_residual_non_object_envelope_is_unknown(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase27/residual-risk-register.json")
        self.write_json(root, artifact_path, [])

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_container_problem(root, artifact_path,
                                      "unknown_unclassified")

    def test_phase27_exception_mistyped_rows_is_malformed(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase27/exception-decision-register.json")
        exceptions = self.read_json(root, artifact_path)
        exceptions["rows"] = {}
        self.write_json(root, artifact_path, exceptions)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_container_problem(root, artifact_path, "malformed")

    def test_phase27_exception_incompatible_discriminator_is_unknown(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase27/exception-decision-register.json")
        exceptions = self.read_json(root, artifact_path)
        exceptions["producer_artifact_kind"] = "phase27_residual_risk_register"
        self.write_json(root, artifact_path, exceptions)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_container_problem(root, artifact_path,
                                      "unknown_unclassified")

    def test_phase28_blocker_missing_blockers_is_malformed(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = "build/ci-evidence/phase28/blocker-summary.json"
        blocker_summary = self.read_json(root, artifact_path)
        del blocker_summary["blockers"]
        self.write_json(root, artifact_path, blocker_summary)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_container_problem(root, artifact_path, "malformed")

    def test_phase28_blocker_non_object_envelope_is_unknown(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = "build/ci-evidence/phase28/blocker-summary.json"
        self.write_json(root, artifact_path, [])

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_container_problem(root, artifact_path,
                                      "unknown_unclassified")

    def test_phase28_residual_non_object_member_is_atomic_malformed(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase28/exception-residual-risk-summary.json")
        residual = self.read_json(root, artifact_path)
        self.assertTrue(residual["rows"])
        residual["rows"].append("not-an-object")
        self.write_json(root, artifact_path, residual)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        container_row = self.assert_container_problem(root, artifact_path,
                                                      "malformed")
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        ordinary_rows = [
            row for row in rows if row["producer_artifact_kind"] ==
            "phase28_exception_residual_risk_summary"
            and row["row_id"] != container_row["row_id"]
        ]
        self.assertFalse(ordinary_rows)

    def test_phase28_residual_incompatible_discriminator_is_unknown(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        artifact_path = (
            "build/ci-evidence/phase28/exception-residual-risk-summary.json")
        residual = self.read_json(root, artifact_path)
        residual["producer_artifact_kind"] = "phase28_blocker_summary"
        self.write_json(root, artifact_path, residual)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assert_container_problem(root, artifact_path,
                                      "unknown_unclassified")

    def test_release_receipt_rejects_same_basename_outside_phase26_path(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        expected_table_path = (
            "build/ci-evidence/phase26/upstream-result-row-table.json")
        attacker_table_path = (
            "arbitrary/attacker/upstream-result-row-table.json")
        self.write_json(
            root,
            attacker_table_path,
            self.read_json(root, expected_table_path),
        )
        receipt_path = ("build/ci-evidence/phase31/stream-receipts/"
                        "release-signing-final-intake-receipt.json")
        receipt = self.read_json(root, receipt_path)
        receipt["consumed_upstream_row_refs"] = [attacker_table_path]
        receipt["validator_output_refs"] = [
            attacker_table_path if ref == expected_table_path else ref
            for ref in receipt["validator_output_refs"]
        ]
        self.write_json(root, receipt_path, receipt)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        release_rows = [
            row for row in rows if row["source_domain"] == "release_signing"
        ]
        self.assertEqual(len(release_rows), 1)
        self.assertEqual(release_rows[0]["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(release_rows[0]["severity"], "critical")

    def test_malformed_phase26_table_emits_critical_blocker(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        table_path = (
            "build/ci-evidence/phase26/upstream-result-row-table.json")
        self.write_json(root, table_path, {"rows": []})

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        malformed_rows = [
            row for row in rows if row["source_domain"] == "release_signing"
            and row["row_problem_kind"] == "malformed"
        ]
        self.assertEqual(len(malformed_rows), 1)
        self.assertEqual(malformed_rows[0]["severity"], "critical")

    def test_phase27_unknown_demotion_authorization_is_critical_blocker(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        handoff_path = (
            "build/ci-evidence/phase27/phase28-handoff-manifest.json")
        handoff = self.read_json(root, handoff_path)
        handoff["demotion_authorization"] = "unexpected-new-state"
        self.write_json(root, handoff_path, handoff)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        demotion_rows = [
            row for row in rows if row["producer_artifact_kind"] ==
            "phase27_phase28_handoff_manifest"
        ]
        self.assertEqual(len(demotion_rows), 1)
        self.assertEqual(demotion_rows[0]["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(demotion_rows[0]["severity"], "critical")

    def test_phase28_unknown_demotion_authorization_is_critical_blocker(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        demotion_path = ("build/ci-evidence/phase28/"
                         "reference-demotion-authorization-record.json")
        demotion = self.read_json(root, demotion_path)
        demotion["reference_demotion_authorization"] = ("unexpected-new-state")
        self.write_json(root, demotion_path, demotion)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        demotion_rows = [
            row for row in rows if row["producer_artifact_kind"] ==
            "phase28_reference_demotion_authorization_record"
        ]
        self.assertEqual(len(demotion_rows), 1)
        self.assertEqual(demotion_rows[0]["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(demotion_rows[0]["severity"], "critical")

    def test_phase27_unknown_residual_row_type_remains_critical(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        residual_path = (
            "build/ci-evidence/phase27/residual-risk-register.json")
        residual = self.read_json(root, residual_path)
        residual["rows"][0]["row_type"] = "unexpected-new-row-type"
        self.write_json(root, residual_path, residual)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        residual_rows = [
            row for row in rows if
            row["producer_artifact_kind"] == "phase27_residual_risk_register"
            and row["source_subject_id"] == residual["rows"][0]["row_id"]
        ]
        self.assertEqual(len(residual_rows), 1)
        self.assertEqual(residual_rows[0]["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(residual_rows[0]["severity"], "critical")

    def test_phase28_unknown_readiness_status_remains_critical(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        blocker_path = "build/ci-evidence/phase28/blocker-summary.json"
        blocker_summary = self.read_json(root, blocker_path)
        criterion_id = blocker_summary["blockers"][0]["criterion_id"]
        blocker_summary["blockers"][0]["phase27_status"] = (
            "unexpected-new-status")
        self.write_json(root, blocker_path, blocker_summary)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        readiness_rows = [
            row for row in rows
            if row["producer_artifact_kind"] == "phase28_blocker_summary"
            and row["source_subject_id"] == criterion_id
        ]
        self.assertEqual(len(readiness_rows), 1)
        self.assertEqual(readiness_rows[0]["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(readiness_rows[0]["severity"], "critical")
