#!/usr/bin/env python3
from __future__ import annotations

from phase31_intake_test_support import *


class Phase31FinalEvidenceIntakeFailureTest(Phase31FinalEvidenceIntakeTestBase
                                            ):

    def test_contract_validation_rejects_missing_adapter_field(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["stream_adapters"][0].pop("validator")
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("simulator adapter missing validator", result.stdout)

    def test_quick_rejects_symlinked_output_parent(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        outside_dir = tempfile.TemporaryDirectory()
        with temp_dir, outside_dir:
            outside_root = Path(outside_dir.name)
            (root / "build").mkdir(parents=True)
            (root / "build/ci-evidence").symlink_to(outside_root,
                                                    target_is_directory=True)

            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("--output-dir cannot contain symlink path component",
                      result.stdout)
        self.assertFalse((outside_root / "phase31").exists())

    def test_retained_output_registration_rejects_quick_placeholder(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root, real=False)

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 0)
        self.assertEqual(manifest["rejected_count"], 1)
        self.assertIn("real_simulator_evidence_supplied must be true",
                      result.stdout)

    def test_secret_bearing_retained_output_is_rejected_before_acceptance(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(
                root,
                extra_manifest={
                    "access_token": "external secret should not be retained"
                })

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 0)
        self.assertIn("forbidden evidence fields", result.stdout)

    def test_symlinked_retained_output_root_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        outside_dir = tempfile.TemporaryDirectory()
        with temp_dir, outside_dir:
            outside_root = Path(outside_dir.name)
            self.write_json(
                outside_root,
                "simulator-result-manifest.json",
                {
                    "artifact_name": "phase23-simulator-evidence-execution",
                    "command_mode": "evidence-input",
                    "output_root": "build/ci-evidence/phase23",
                    "phase": "23-simulator-evidence-execution",
                    "phase_lifecycle_id": "23-2026-06-23T18-45-38",
                    "real_simulator_evidence_supplied": True,
                    "status": "passed",
                },
            )
            self.write_json(
                outside_root,
                "upstream-simulator-result-row.json",
                {
                    "artifact_refs": ["external://phase23/logs/run.json"],
                    "redaction_status": "passed",
                    "source_ref_status": "passed",
                },
            )
            (root / "build/ci-evidence").mkdir(parents=True)
            (root / "build/ci-evidence/phase23").symlink_to(
                outside_root, target_is_directory=True)

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("cannot contain symlink path component", result.stdout)

    def test_unsafe_artifact_ref_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root,
                                       artifact_ref="/tmp/raw-output.log")

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("ref must stay within allowed roots", result.stdout)

    def test_external_artifact_ref_traversal_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(
                root, artifact_ref="external://phase23/../raw-output.log")

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("ref must stay within allowed roots", result.stdout)

    def test_stale_lifecycle_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root, lifecycle="23-stale")

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("phase_lifecycle_id must be 23-2026-06-23T18-45-38",
                      result.stdout)

    def test_missing_submitter_identity_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root)

            # Act
            result = self.run_verifier(
                ["--phase23-retained-output", "build/ci-evidence/phase23"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("submitter_identity_ref is required", result.stdout)

    def test_row_only_retained_output_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_json(
                root,
                "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                {
                    "artifact_refs": ["external://phase23/logs/run.json"],
                    "redaction_status": "passed",
                    "source_ref_status": "passed",
                },
            )

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("missing required path", result.stdout)

    def test_prose_raw_submission_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            prose_input = self.write_file(
                root, "simulator-prose.txt",
                "Maintainer says the simulator passed.")

            # Act
            result = self.run_verifier(
                [
                    "--simulator-evidence-input",
                    prose_input,
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("is not valid JSON evidence", result.stdout)
        self.assertFalse(
            (root / "build/source-validator-invocations.jsonl").exists())
