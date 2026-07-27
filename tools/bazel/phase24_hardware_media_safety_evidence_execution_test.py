#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase24_execution_test_support import *


class Phase24HardwareMediaSafetyEvidenceExecutionTest(
        Phase24ExecutionTestSupport, unittest.TestCase):

    def test_contract_only_accepts_complete_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_only_rejects_phase15_scenario_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["required_phase15_scenario_ids"] = contract[
                "required_phase15_scenario_ids"][:-1]
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must exactly match Phase 15 scenarios", result.stdout)

    def test_quick_writes_blocked_placeholder_outputs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)
            manifest = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/hardware-media-safety-result-manifest.json"
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(manifest["real_hardware_evidence_supplied"])
        self.assertEqual(manifest["status"], "blocked")
        self.assertEqual(manifest["scenario_count"], 26)
        self.assertEqual(manifest["status_counts"], {"blocked": 26})

    def test_quick_source_statuses_match_phase15_allowed_statuses(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)
            manifest = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/hardware-media-safety-result-manifest.json"
            )
            phase15 = self.read_phase15_contract(root)
            allowed_by_id = {
                scenario["id"]: set(scenario["allowed_statuses"])
                for scenario in phase15["scenarios"]
            }

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        for row in manifest["scenarios"]:
            self.assertIn(row["source_status"],
                          allowed_by_id[row["scenario_id"]])

    def test_evidence_input_accepts_complete_packet(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            input_path = self.write_evidence_input(root,
                                                   self.complete_rows(root))

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)
            manifest = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/hardware-media-safety-result-manifest.json"
            )
            upstream = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/upstream-hardware-media-safety-result-row.json"
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(manifest["real_hardware_evidence_supplied"])
        self.assertEqual(manifest["status"], "passed")
        self.assertEqual(manifest["status_counts"], {"passed": 26})
        self.assertEqual(upstream["criterion_id"],
                         "final-hardware-safety-media-evidence")
        self.assertEqual(upstream["requirement_ids"], ["EVID-02"])

    def test_traceability_boundary_accepts_source_contract_pass(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[self.traceability_row_index(
                rows)]["source_status"] = "source-contract-passed"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_traceability_boundary_rejects_generic_source_pass(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[self.traceability_row_index(rows)]["source_status"] = "passed"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "source_status is not allowed for this Phase 15 scenario",
            result.stdout)

    def test_evidence_input_rejects_missing_scenario(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            input_path = self.write_evidence_input(
                root,
                self.complete_rows(root)[:-1])

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing scenario results", result.stdout)

    def test_evidence_input_rejects_duplicate_scenario(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[-1] = rows[0].copy()
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate scenario result", result.stdout)

    def test_evidence_input_rejects_unknown_scenario(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["scenario_id"] = "hard-unknown"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not resolve to a Phase 15 scenario", result.stdout)

    def test_evidence_input_rejects_invalid_phase24_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["status"] = "pending-hardware-input"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status is invalid", result.stdout)

    def test_evidence_input_rejects_blocking_source_status_as_passed(
            self) -> None:
        for source_status in [
                "pending-hardware-input", "manual-hardware-required",
                "blocked-hardware-unavailable"
        ]:
            # Arrange
            temp_dir, root = self.make_temp_root()
            with temp_dir, self.subTest(source_status=source_status):
                rows = self.complete_rows(root)
                rows[0]["source_status"] = source_status
                input_path = self.write_evidence_input(root, rows)

                # Act
                result = self.run_verifier(["--evidence-input", input_path],
                                           maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"cannot pass with source_status={source_status}",
                          result.stdout)

    def test_exception_requested_requires_exception_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["status"] = "exception-requested"
            rows[0]["source_status"] = "failed"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exception_request", result.stdout)

    def test_evidence_input_rejects_missing_operator_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            del rows[0]["device"]
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required fields: device", result.stdout)

    def test_storage_row_requires_specific_media_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[self.storage_row_index(rows)]["media_surface"] = "wrong-media"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("media_surface must be", result.stdout)

    def test_storage_row_requires_observed_behavior(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            del rows[self.storage_row_index(rows)]["observed_behavior"]
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("observed_behavior must be a non-empty string",
                      result.stdout)

    def test_storage_row_requires_failure_observations_and_residual_risk(
            self) -> None:
        for field in ["failure_observations", "residual_risk"]:
            # Arrange
            temp_dir, root = self.make_temp_root()
            with temp_dir, self.subTest(field=field):
                rows = self.complete_rows(root)
                rows[self.storage_row_index(rows)][field] = ""
                input_path = self.write_evidence_input(root, rows)

                # Act
                result = self.run_verifier(["--evidence-input", input_path],
                                           maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(field, result.stdout)

    def test_safety_row_requires_artifact_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[self.safety_row_index(rows)]["artifact_refs"] = []
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("empty required fields: artifact_refs", result.stdout)

    def test_evidence_input_rejects_artifact_path_traversal(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["artifact_refs"] = ["../secret.log"]
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)

    def test_evidence_input_rejects_bare_external_artifact_ref(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["artifact_refs"] = ["external://phase24/"]
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact ref is unsafe", result.stdout)

    def test_evidence_input_rejects_forbidden_secret_fields(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["token_value"] = "secret"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden evidence marker", result.stdout)

    def test_evidence_input_rejects_mixed_case_forbidden_secret_fields(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["Token"] = "secret"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contains forbidden evidence fields: Token",
                      result.stdout)

    def test_evidence_input_rejects_forbidden_content_markers(self) -> None:
        for marker in [
                "-----BEGIN PRIVATE KEY-----",
                "Wi-Fi credential",
                "raw_ram_dump",
                ".bbf payload",
                "firmware_payload_bytes",
                "hardware verified locally",
        ]:
            # Arrange
            temp_dir, root = self.make_temp_root()
            with temp_dir, self.subTest(marker=marker):
                rows = self.complete_rows(root)
                rows[0]["status_reason"] = marker
                input_path = self.write_evidence_input(root, rows)

                # Act
                result = self.run_verifier(["--evidence-input", input_path],
                                           maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(
                "forbidden evidence marker" in result.stdout
                or "non-local evidence overclaim" in result.stdout,
                result.stdout,
            )

    def test_retained_outputs_include_required_files(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            input_path = self.write_evidence_input(root,
                                                   self.complete_rows(root))

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for path in [
                    "hardware-media-safety-result-manifest.json",
                    "normalized-hardware-media-safety-results.json",
                    "redacted-hardware-media-safety-summary.json",
                    "upstream-hardware-media-safety-result-row.json",
                    "upstream-hardware-result-row.json",
                    "operator-hardware-media-safety-template.json",
                    "operator-evidence-input-template.json",
                    "artifact-summaries/hardware-media-safety-artifact-summary.json",
                    "contract-snapshots/phase15_hardware_evidence_contract.json",
                    "contract-snapshots/phase24_hardware_media_safety_evidence_execution_contract.json",
            ]:
                self.assertTrue((root / DEFAULT_OUTPUT_DIR / path).exists(),
                                path)

    def test_wiring_only_accepts_phase24_entries(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase24_wiring(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_only_rejects_missing_just_recipe(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase24_wiring(root, maybe_justfile="")

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase24-verify:", result.stdout)


if __name__ == "__main__":
    unittest.main()
