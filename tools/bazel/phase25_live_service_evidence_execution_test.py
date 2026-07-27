#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase25_execution_test_support import *


class Phase25LiveServiceEvidenceExecutionTest(Phase25ExecutionTestSupport,
                                              unittest.TestCase):

    def test_contract_only_accepts_complete_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_only_rejects_phase16_scenario_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["required_phase16_scenario_ids"] = contract[
                "required_phase16_scenario_ids"][:-1]
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must exactly match Phase 16 scenarios", result.stdout)

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
                f"{DEFAULT_OUTPUT_DIR}/live-service-result-manifest.json")

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(manifest["real_live_service_evidence_supplied"])
        self.assertEqual(manifest["status"], "blocked")
        self.assertEqual(manifest["scenario_count"], 20)
        self.assertEqual(manifest["status_counts"], {"blocked": 20})

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
                f"{DEFAULT_OUTPUT_DIR}/live-service-result-manifest.json")
            upstream = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/upstream-live-service-result-row.json")

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(manifest["real_live_service_evidence_supplied"])
        self.assertEqual(manifest["status"], "passed")
        self.assertEqual(manifest["status_counts"], {"passed": 20})
        self.assertEqual(upstream["criterion_id"],
                         "final-live-service-evidence")
        self.assertEqual(upstream["evidence_family"], "live-service")
        self.assertEqual(upstream["requirement_ids"], ["EVID-03"])

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
            "source_status is not allowed for this Phase 16 scenario",
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
            rows[0]["scenario_id"] = "live-unknown"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not resolve to a Phase 16 scenario", result.stdout)

    def test_evidence_input_rejects_invalid_phase25_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["status"] = "pending-live-input"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status is invalid", result.stdout)

    def test_evidence_input_rejects_blocking_source_status_as_passed(
            self) -> None:
        blocking_statuses = [
            "pending-live-input",
            "manual-live-service-required",
            "controlled-service-required",
            "blocked-credentials-unavailable",
            "blocked-endpoint-unavailable",
            "not-applicable-with-justification",
        ]
        for source_status in blocking_statuses:
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

    def test_evidence_input_rejects_service_surface_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["service_surface"] = "wrong-surface"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("service_surface must be", result.stdout)

    def test_evidence_input_rejects_wrong_pass_evidence_type(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["evidence_type"] = "source-contract-validation"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("live-service pass requires", result.stdout)

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
            rows[0]["artifact_refs"] = ["external://phase25/"]
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
            rows[0]["Api_Key"] = "secret"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contains forbidden evidence fields: Api_Key",
                      result.stdout)

    def test_evidence_input_rejects_forbidden_content_markers(self) -> None:
        for marker in [
                "-----BEGIN PRIVATE KEY-----",
                "Connect token",
                "PrusaLink password",
                "api_key",
                "production connect validated",
                "raw crash dump retained",
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
                    "live-service-result-manifest.json",
                    "normalized-live-service-results.json",
                    "redacted-live-service-summary.json",
                    "upstream-live-service-result-row.json",
                    "upstream-live-result-row.json",
                    "operator-live-service-template.json",
                    "operator-evidence-input-template.json",
                    "artifact-summaries/live-service-artifact-summary.json",
                    "contract-snapshots/phase16_live_network_evidence_contract.json",
                    "contract-snapshots/phase25_live_service_evidence_execution_contract.json",
            ]:
                self.assertTrue((root / DEFAULT_OUTPUT_DIR / path).exists(),
                                path)

    def test_wiring_only_accepts_phase25_entries(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase25_wiring(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_only_rejects_missing_just_recipe(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase25_wiring(root, maybe_justfile="")

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase25-verify:", result.stdout)


if __name__ == "__main__":
    unittest.main()
