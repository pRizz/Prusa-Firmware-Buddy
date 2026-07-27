#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest

from phase15_hardware_evidence_test import Phase15HardwareEvidenceFixture


class Phase15HardwareEvidenceFailureTest(
        Phase15HardwareEvidenceFixture,
        unittest.TestCase,
):

    def test_operator_evidence_rejects_forbidden_full_document_markers(
            self) -> None:
        cases = [
            (
                {
                    "evidence_rows": [self.complete_operator_row()],
                    "raw_crash_dump": "redacted test value",
                },
                "raw_crash_dump",
            ),
            (
                {
                    "evidence_rows": [self.complete_operator_row()],
                    "metadata": {
                        "note": "local hardware proof"
                    },
                },
                "local hardware proof",
            ),
        ]
        for payload, expected in cases:
            with self.subTest(expected=expected):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    operator_path = "operator-evidence-extra.json"
                    self.write_file(
                        root,
                        operator_path,
                        json.dumps(payload, indent=2, sort_keys=True) + "\n",
                    )

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--operator-evidence", operator_path],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_security_rejects_secret_markers(self) -> None:
        cases = [
            "-----BEGIN PRIVATE KEY-----",
            "-----BEGIN CERTIFICATE-----",
            "token_value",
            "password_value",
            "wifi_password",
            "Wi-Fi credential",
            "Connect token",
            "certificate_bytes",
            "private_key",
            "signing_key",
            "raw_crash_dump",
            "raw_ram_dump",
            "memory_dump",
            "firmware_payload",
            "bbf_payload",
            "dfu_payload",
            ".bin payload",
            ".bbf payload",
            ".dfu payload",
        ]
        for marker in cases:
            with self.subTest(marker=marker):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.write_file(
                        root,
                        "build/ci-evidence/phase15/leak.json",
                        marker + "\n",
                    )

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(marker, result.stdout)

    def test_security_rejects_overclaim_wording(self) -> None:
        cases = [
            "hardware verified locally",
            "local hardware proof",
            "hardware qualification passed locally",
            "final cutover complete",
            "cutover complete",
            "release readiness proven",
            "release-candidate passed locally",
            "signing proof complete",
            "signing verified locally",
            "retained-code accepted by maintainer",
            "reference demotion approved",
            "reference removal complete",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.write_file(
                        root,
                        "build/ci-evidence/phase15/overclaim.json",
                        phrase + "\n",
                    )

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(phrase, result.stdout)

    def test_operator_evidence_rejects_artifact_path_traversal(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            row = self.complete_operator_row(artifact_ref="../leak.log")
            operator_path = self.write_operator_evidence(root, [row])

            # Act
            result = self.run_verifier(
                ["--quick", "--operator-evidence", operator_path],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)
