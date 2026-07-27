#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase31_intake_test_support import *


class Phase31FinalEvidenceIntakeTest(Phase31FinalEvidenceIntakeTestBase):

    def test_contract_only_accepts_current_contract(self) -> None:
        # Arrange
        args = ["--contract-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_help_exposes_final_intake_flags(self) -> None:
        # Arrange
        expected_flags = [
            "--simulator-evidence-input",
            "--hardware-media-safety-evidence-input",
            "--live-service-evidence-input",
            "--release-input",
            "--phase23-retained-output",
            "--submitter-identity-ref",
        ]

        # Act
        result = self.run_verifier(["--help"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        for flag in expected_flags:
            self.assertIn(flag, result.stdout)

    def test_quick_writes_quarantined_non_final_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)
            manifest = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")
            rejected = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/rejected-submissions.json")

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 0)
        self.assertEqual(manifest["rejected_count"], 4)
        self.assertEqual(manifest["finality_status"], "quarantined-non-final")
        self.assertTrue(
            all(row["finality_status"] == "quarantined-non-final"
                for row in rejected["rejected_submissions"]))

    def test_raw_inputs_invoke_source_validators_and_write_receipts(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            simulator_input = self.write_json(
                root, "simulator-input.json",
                {"simulator_evidence_packet": {
                    "sanitized": True
                }})
            hardware_input = self.write_json(
                root, "hardware-input.json",
                {"hardware_media_safety_evidence_packet": {
                    "sanitized": True
                }})
            live_input = self.write_json(
                root, "live-input.json",
                {"live_service_evidence_packet": {
                    "sanitized": True
                }})
            release_input = self.write_json(
                root, "release-input.json",
                {"evidence_rows": [{
                    "id": "rel-bin-firmware-image"
                }]})

            # Act
            result = self.run_verifier(
                [
                    "--simulator-evidence-input",
                    simulator_input,
                    "--hardware-media-safety-evidence-input",
                    hardware_input,
                    "--live-service-evidence-input",
                    live_input,
                    "--release-input",
                    release_input,
                    "--submitter-identity-ref",
                    SUBMITTER,
                    "--output-dir",
                    DEFAULT_OUTPUT_DIR,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")
            invocations = [
                json.loads(line) for line in (
                    root /
                    "build/source-validator-invocations.jsonl").read_text(
                        encoding="utf-8").splitlines()
            ]
            release_invocation = invocations[-1]["argv"]

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 4)
        self.assertEqual([entry["phase"] for entry in invocations], [
            "23-simulator-evidence-execution",
            "24-hardware-media-and-safety-evidence-execution",
            "25-live-service-evidence-execution",
            "26-release-signing-and-upstream-result-evidence",
        ])
        self.assertIn("--phase23-simulator-row", release_invocation)
        self.assertIn("--phase24-hardware-media-safety-row",
                      release_invocation)
        self.assertIn("--phase25-live-service-row", release_invocation)

    def test_retained_output_registration_accepts_real_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root)

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
            receipt = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/stream-receipts/simulator-final-intake-receipt.json"
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 1)
        self.assertEqual(receipt["finality_status"], "accepted-final")
        self.assertEqual(receipt["submitter_identity_ref"], SUBMITTER)
        self.assertEqual(
            receipt["validator_command"],
            ["registered-retained-output", "build/ci-evidence/phase23"])
        self.assertNotIn("scenarios", receipt)

    def test_release_evidence_refs_are_containment_checked(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_json(
                root,
                "build/ci-evidence/phase26/release-upstream-run-manifest.json",
                {
                    "artifact_name":
                    "phase26-release-signing-upstream-evidence",
                    "output_root": "build/ci-evidence/phase26",
                    "phase": "26-release-signing-and-upstream-result-evidence",
                    "phase_lifecycle_id": "26-2026-06-24T13-36-46",
                    "real_release_evidence_supplied": True,
                    "release_status": "passed",
                },
            )
            self.write_json(
                root,
                "build/ci-evidence/phase26/upstream-result-row-table.json",
                {
                    "rows": [{
                        "artifact_refs":
                        ["external://phase26/artifacts/release.json"],
                        "criterion_id":
                        "final-release-artifact-signing-evidence",
                        "evidence_refs": ["/tmp/raw-release-log.txt"],
                        "redaction_status":
                        "passed",
                        "source_lifecycle_status":
                        "current",
                        "source_ref_status":
                        "passed",
                        "status":
                        "passed",
                    }]
                },
            )

            # Act
            result = self.run_verifier(
                [
                    "--phase26-retained-output",
                    "build/ci-evidence/phase26",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("evidence_refs ref must stay within allowed roots",
                      result.stdout)

    def test_release_row_table_accepts_consumed_phase23_to_phase25_refs(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_json(
                root,
                "build/ci-evidence/phase26/release-upstream-run-manifest.json",
                {
                    "artifact_name":
                    "phase26-release-signing-upstream-evidence",
                    "output_root": "build/ci-evidence/phase26",
                    "phase": "26-release-signing-and-upstream-result-evidence",
                    "phase_lifecycle_id": "26-2026-06-24T13-36-46",
                    "real_release_evidence_supplied": True,
                    "release_status": "passed",
                },
            )
            self.write_json(
                root,
                "build/ci-evidence/phase26/upstream-result-row-table.json",
                {
                    "rows": [
                        {
                            "artifact_refs":
                            ["external://phase23/logs/simulator.json"],
                            "criterion_id":
                            "final-simulator-evidence",
                            "evidence_refs":
                            ["external://phase23/evidence/simulator.json"],
                            "redaction_status":
                            "passed",
                            "source_lifecycle_status":
                            "current",
                            "source_ref_status":
                            "passed",
                            "status":
                            "passed",
                        },
                        {
                            "artifact_refs":
                            ["external://phase24/logs/hardware.json"],
                            "criterion_id":
                            "final-hardware-safety-media-evidence",
                            "evidence_refs":
                            ["external://phase24/evidence/hardware.json"],
                            "redaction_status":
                            "passed",
                            "source_lifecycle_status":
                            "current",
                            "source_ref_status":
                            "passed",
                            "status":
                            "passed",
                        },
                        {
                            "artifact_refs":
                            ["external://phase25/logs/live.json"],
                            "criterion_id":
                            "final-live-network-transfer-evidence",
                            "evidence_refs":
                            ["external://phase25/evidence/live.json"],
                            "redaction_status":
                            "passed",
                            "source_lifecycle_status":
                            "current",
                            "source_ref_status":
                            "passed",
                            "status":
                            "passed",
                        },
                        {
                            "artifact_refs":
                            ["external://phase26/artifacts/release.json"],
                            "criterion_id":
                            "final-release-artifact-signing-evidence",
                            "evidence_refs":
                            ["external://phase26/evidence/release.json"],
                            "redaction_status":
                            "passed",
                            "source_lifecycle_status":
                            "current",
                            "source_ref_status":
                            "passed",
                            "status":
                            "passed",
                        },
                    ]
                },
            )
            self.write_json(
                root,
                "build/ci-evidence/phase26/artifact-reference-summary.json",
                {
                    "artifact_refs":
                    ["external://phase20/artifacts/firmware.bbf"],
                    "digest_refs": [{
                        "artifact_ref":
                        "external://phase20/artifacts/firmware.bbf",
                        "sha256": "b" * 64,
                    }],
                },
            )

            # Act
            result = self.run_verifier(
                [
                    "--phase26-retained-output",
                    "build/ci-evidence/phase26",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 1)

    def test_wiring_only_accepts_current_wiring(self) -> None:
        # Arrange
        args = ["--wiring-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_requires_tests_before_verifier(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase31_wiring(
                root,
                maybe_justfile="""phase31-verify:
    bazel run //tools/bazel:phase31_verify
    bazel run //tools/bazel:phase31_verify_tests
""",
            )

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "justfile phase31-verify recipe must run tests before verifier",
            result.stdout)


from phase31_final_evidence_intake_failure_test import Phase31FinalEvidenceIntakeFailureTest

if __name__ == "__main__":
    unittest.main()
