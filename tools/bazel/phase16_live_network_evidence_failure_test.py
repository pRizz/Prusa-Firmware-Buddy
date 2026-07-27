#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from phase16_live_network_evidence_test import Phase16LiveNetworkEvidenceFixture


class Phase16LiveNetworkEvidenceFailureTest(Phase16LiveNetworkEvidenceFixture,
                                            unittest.TestCase):

    def test_security_rejects_secret_markers(self) -> None:
        cases = [
            "-----BEGIN PRIVATE KEY-----",
            "-----BEGIN CERTIFICATE-----",
            "certificate_pem",
            "certificate_bytes",
            "private_key",
            "signing_key",
            "token_value",
            "connect_token",
            "Connect token",
            "registration_code",
            "registration code",
            "Fingerprint: 123456",
            "fingerprint_value",
            "wifi_password",
            "Wi-Fi credential",
            "PrusaLink password",
            "api_key",
            "x-api-key",
            "API key",
            "Authorization: Bearer redacted",
            "Cookie: session=redacted",
            "Set-Cookie: session=redacted",
            "raw_http_log",
            "raw_tls_log",
            "tls_keylog",
            "SSLKEYLOGFILE",
            "raw_crash_dump",
            "raw_ram_dump",
            "memory_dump",
            "raw_production_payload",
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
                    self.write_file(root,
                                    "build/ci-evidence/phase16/leak.json",
                                    marker + "\n")

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("contains forbidden evidence marker",
                              result.stdout)

    def test_security_rejects_secret_assignment_forms(self) -> None:
        cases = [
            ("api-key: super-secret-value", "credential-assignment"),
            ("token=super-secret-value", "credential-assignment"),
            ("password: super-secret-value", "credential-assignment"),
            ('"api-key": "super-secret-value"', "credential-assignment"),
            ('"token": "super-secret-value"', "credential-assignment"),
            ('"access_token": "super-secret-value"', "credential-assignment"),
            ('"refresh_token": "super-secret-value"', "credential-assignment"),
            ('"auth_token": "super-secret-value"', "credential-assignment"),
            ('"password": "super-secret-value"', "credential-assignment"),
            ('"secret": "super-secret-value"', "credential-assignment"),
            ('"client_secret": "super-secret-value"', "credential-assignment"),
            ("Authorization = Bearer super-secret-value",
             "credential-header-assignment"),
            ('"Authorization": "Bearer super-secret-value"',
             "credential-header-assignment"),
            ('"Proxy-Authorization": "Bearer super-secret-value"',
             "credential-header-assignment"),
            ('"proxy_authorization": "Bearer super-secret-value"',
             "credential-header-assignment"),
            ('"Cookie": "session=super-secret-value"',
             "credential-header-assignment"),
            ('"Set-Cookie": "session=super-secret-value"',
             "credential-header-assignment"),
            ('"set_cookie": "session=super-secret-value"',
             "credential-header-assignment"),
            ('"cookie_header": "session=super-secret-value"',
             "credential-header-assignment"),
        ]
        for marker, expected_label in cases:
            with self.subTest(marker=marker):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.write_file(root,
                                    "build/ci-evidence/phase16/leak.json",
                                    marker + "\n")

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_label, result.stdout)
                self.assertNotIn("super-secret-value", result.stdout)

    def test_security_rejects_overclaim_wording(self) -> None:
        cases = [
            "live service passed locally",
            "live network verified locally",
            "production Connect validated",
            "production PrusaLink validated",
            "tls proof complete without operator evidence",
            "proxy fully supported",
            "proxy authentication supported",
            "crash dump upload safe",
            "raw crash dump retained",
            "final cutover complete",
            "cutover complete",
            "release readiness proven",
            "release-candidate passed locally",
            "signing proof complete",
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
                    baseline = self.run_verifier(["--security-only"],
                                                 maybe_root=root)
                    self.write_file(
                        root, "build/ci-evidence/phase16/overclaim.json",
                        phrase + "\n")

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertEqual(baseline.returncode, 0, baseline.stdout)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(phrase.lower(), result.stdout.lower())

    def test_output_dir_rejects_traversal(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", "../escape"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)

    def test_quick_rejects_symlinked_output_parent(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        outside_dir = tempfile.TemporaryDirectory()
        with temp_dir, outside_dir:
            outside_root = Path(outside_dir.name)
            self.copy_complete_surface(root)
            (root / "build").mkdir()
            (root / "build/ci-evidence").symlink_to(outside_root,
                                                    target_is_directory=True)
            (outside_root / "sentinel.txt").write_text("keep\n",
                                                       encoding="utf-8")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("resolves outside", result.stdout)
            self.assertFalse(
                (outside_root / "phase16/run-manifest.json").exists())
            self.assertEqual(
                (outside_root / "sentinel.txt").read_text(encoding="utf-8"),
                "keep\n")

    def test_wiring_accepts_phase16_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_rejects_missing_bazel_label(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(
                encoding="utf-8").replace(
                    'name = "phase16_verify_tests"',
                    'name = "phase16_missing_tests"',
                )
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase16_verify_tests", result.stdout)

    def test_wiring_rejects_missing_source_ref_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)
            tools_build = (
                root / "tools/bazel/BUILD.bazel"
            ).read_text(encoding="utf-8").replace(
                '        "manifests/phase11_retained_code_justifications.json",\n',
                "",
            )
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase11_retained_code_justifications.json",
                      result.stdout)

    def test_wiring_rejects_verifier_before_tests(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(
                root,
                maybe_justfile="""phase16-verify:
    bazel run //tools/bazel:phase16_verify
    bazel run //tools/bazel:phase16_verify_tests
""",
            )

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tests before verifier", result.stdout)
