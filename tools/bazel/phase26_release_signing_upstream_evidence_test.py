#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase26_release_signing_upstream_evidence_failure_test import *
from phase26_release_test_support import *


class Phase26ReleaseSigningUpstreamEvidenceTest(
        Phase26ReleaseSigningUpstreamEvidenceFailureTests,
        Phase26ReleaseTestSupport, unittest.TestCase):

    def test_contract_lists_phase26_policy_and_phase20_rows(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(contract["id"],
                         "phase26_release_signing_upstream_evidence_contract")
        self.assertEqual(contract["output_root"], DEFAULT_OUTPUT_DIR)
        release_policy = contract["release_policy"]
        self.assertEqual(release_policy["canonical_phase20_release_row_ids"],
                         REQUIRED_ROW_IDS)
        self.assertIn("approved-release-run",
                      release_policy["pass_capable_proof_classes"])
        self.assertIn("external-release-key-evidence",
                      release_policy["pass_capable_proof_classes"])
        self.assertEqual(
            set(contract["upstream_policy"]["canonical_phase18_criteria"]),
            REQUIRED_UPSTREAM_CRITERIA)
        self.assertEqual(
            set(contract["upstream_policy"]["row_required_fields"]),
            REQUIRED_UPSTREAM_FIELDS)

    def test_security_only_accepts_checked_in_safe_inputs(self) -> None:
        # Arrange
        args = ["--security-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_quick_writes_retained_outputs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            output_root = root / DEFAULT_OUTPUT_DIR

            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for retained_output in RETAINED_OUTPUTS:
                self.assertTrue((output_root / retained_output).exists(),
                                retained_output)

    def test_quick_upstream_rows_cover_phase18_schema(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)
            self.assertEqual(result.returncode, 0, result.stdout)

            # Act
            rows = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/upstream-result-row-table.json")["rows"]

            # Assert
            self.assertEqual({row["criterion_id"]
                              for row in rows}, REQUIRED_UPSTREAM_CRITERIA)
            self.assertTrue(
                all(REQUIRED_UPSTREAM_FIELDS <= set(row) for row in rows))
            release_row = next(row for row in rows if row["criterion_id"] ==
                               "final-release-artifact-signing-evidence")
            self.assertEqual(release_row["requirement_ids"],
                             ["EVID-04", "ACPT-01"])
            self.assertTrue(
                all(row["requirement_ids"] == ["ACPT-01"] for row in rows
                    if row["criterion_id"] !=
                    "final-release-artifact-signing-evidence"))
            self.assertTrue(
                all(row["maintainer_state"] in
                    {"pending", "blocked", "not-required"} for row in rows))

    def test_consumed_upstream_rows_replace_default_pending_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            row_paths = self.write_valid_upstream_rows(root)

            # Act
            result = self.run_verifier(
                [
                    "--quick",
                    "--output-dir",
                    DEFAULT_OUTPUT_DIR,
                    "--phase23-simulator-row",
                    row_paths["phase23"],
                    "--phase24-hardware-media-safety-row",
                    row_paths["phase24"],
                    "--phase25-live-service-row",
                    row_paths["phase25"],
                ],
                maybe_root=root,
            )

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            rows = {
                row["criterion_id"]: row
                for row in self.read_json(
                    root,
                    f"{DEFAULT_OUTPUT_DIR}/upstream-result-row-table.json")
                ["rows"]
            }
            self.assertEqual(rows["final-simulator-evidence"]["status"],
                             "passed")
            self.assertEqual(
                rows["final-simulator-evidence"]["requirement_ids"],
                ["EVID-01", "ACPT-01"])
            self.assertIn(row_paths["phase23"],
                          rows["final-simulator-evidence"]["artifact_refs"])
            self.assertEqual(
                rows["final-hardware-safety-media-evidence"]["status"],
                "passed")
            self.assertEqual(
                rows["final-hardware-safety-media-evidence"]
                ["requirement_ids"], ["EVID-02", "ACPT-01"])
            self.assertIn(
                row_paths["phase24"],
                rows["final-hardware-safety-media-evidence"]["artifact_refs"])
            self.assertEqual(
                rows["final-live-network-transfer-evidence"]["status"],
                "passed")
            self.assertEqual(
                rows["final-live-network-transfer-evidence"]
                ["requirement_ids"], ["EVID-03", "ACPT-01"])
            self.assertIn(
                row_paths["phase25"],
                rows["final-live-network-transfer-evidence"]["artifact_refs"])

    def test_absent_upstream_rows_keep_fail_closed_defaults(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)
            self.assertEqual(result.returncode, 0, result.stdout)

            # Act
            rows = {
                row["criterion_id"]: row
                for row in self.read_json(
                    root,
                    f"{DEFAULT_OUTPUT_DIR}/upstream-result-row-table.json")
                ["rows"]
            }

            # Assert
            self.assertEqual(rows["final-simulator-evidence"]["status"],
                             "pending-simulator-input")
            self.assertEqual(
                rows["final-hardware-safety-media-evidence"]["status"],
                "pending-hardware-input")
            self.assertEqual(
                rows["final-live-network-transfer-evidence"]["status"],
                "pending-live-input")
            self.assertEqual(
                rows["final-simulator-evidence"]["requirement_ids"],
                ["ACPT-01"])

    def test_phase25_compact_live_service_row_maps_to_phase18_live_network_criterion(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            row_paths = self.write_valid_upstream_rows(root)

            # Act
            result = self.run_verifier(
                [
                    "--quick",
                    "--output-dir",
                    DEFAULT_OUTPUT_DIR,
                    "--phase25-live-service-row",
                    row_paths["phase25"],
                ],
                maybe_root=root,
            )

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            rows = {
                row["criterion_id"]: row
                for row in self.read_json(
                    root,
                    f"{DEFAULT_OUTPUT_DIR}/upstream-result-row-table.json")
                ["rows"]
            }
            self.assertNotIn("final-live-service-evidence", rows)
            live_row = rows["final-live-network-transfer-evidence"]
            self.assertEqual(live_row["status"], "passed")
            self.assertEqual(live_row["requirement_ids"],
                             ["EVID-03", "ACPT-01"])
            self.assertIn(row_paths["phase25"], live_row["evidence_refs"])

    def test_quick_marks_real_release_evidence_as_not_supplied(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)
            self.assertEqual(result.returncode, 0, result.stdout)

            # Act
            manifest = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/release-upstream-run-manifest.json")
            rows = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/upstream-result-row-table.json")["rows"]

            # Assert
            self.assertFalse(manifest["real_release_evidence_supplied"])
            release_row = next(row for row in rows if row["criterion_id"] ==
                               "final-release-artifact-signing-evidence")
            self.assertEqual(release_row["status"], "pending-release-input")
            self.assertEqual(release_row["exception_status"], "none")
            self.assertEqual(release_row["maintainer_state"], "pending")

    def test_quick_outputs_do_not_overclaim_later_acceptance(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)
            self.assertEqual(result.returncode, 0, result.stdout)
            combined_output = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted((root /
                                    DEFAULT_OUTPUT_DIR).rglob("*.json")))

            # Act
            lower_output = combined_output.lower()

            # Assert
            self.assertNotIn("demotion_allowed\": true", lower_output)
            self.assertNotIn("final approval complete", lower_output)
            self.assertNotIn("retained-code accepted", lower_output)
            self.assertNotIn("accepted retained-code", lower_output)

    def test_wiring_only_accepts_checked_in_phase26_wiring(self) -> None:
        # Arrange
        args = ["--wiring-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
