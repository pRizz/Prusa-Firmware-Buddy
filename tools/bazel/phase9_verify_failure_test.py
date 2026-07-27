#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase9_verify_test import *  # noqa: F403


class Phase9VerifierFailureTest(Phase9VerifierFixture, unittest.TestCase):

    def negative_case(self, root: Path, case_id: str) -> dict[str, object]:
        row: dict[str, object] = {
            "id":
            case_id,
            "requirement_id":
            "IFCE-02",
            "category":
            "connect-command",
            "reference_sources":
            ["src/connect/connect.cpp", "src/connect/planner.cpp"],
            "input_fixture": {
                "condition": "metadata-only"
            },
            "expected_outcome": {
                "classification": "source-backed"
            },
            "evidence_class":
            "source-audit",
            "proof_scope":
            "local",
            "secret_handling":
            "named-only-redacted",
            "intentional_delta":
            "none",
            "runnable_check":
            "metadata-schema-only",
            "phase_lifecycle_id":
            PHASE_LIFECYCLE_ID,
        }
        if case_id == "custom-cert-valid-der-intentional-delta":
            row.update({
                "category": "custom-certificate",
                "reference_sources": ["src/connect/tls/tls.cpp"],
                "input_fixture": {
                    "custom_certificate_path": "/internal/connect/connect.der",
                    "certificate_material": "omitted",
                },
                "expected_outcome": {
                    "classification": "intentional-delta-fixture"
                },
                "evidence_class": "manual-hardware-required",
                "proof_scope": "non-local",
                "intentional_delta": "approved",
            })
        elif case_id == "custom-cert-missing-der-preserved-defect":
            row.update({
                "category": "custom-certificate",
                "reference_sources": ["src/connect/tls/tls.cpp"],
                "input_fixture": {
                    "custom_certificate_path": "/internal/connect/connect.der",
                    "certificate_material": "omitted",
                },
                "expected_outcome": {
                    "classification": "preserved-defect",
                    "preserved_defect": True,
                },
            })
        elif case_id == "custom-cert-invalid-der-rejected":
            row.update({
                "category": "custom-certificate",
                "reference_sources": ["src/connect/tls/tls.cpp"],
                "input_fixture": {
                    "custom_certificate_path": "/internal/connect/connect.der",
                    "certificate_material": "omitted",
                },
                "expected_outcome": {
                    "classification": "rejected-invalid-der",
                    "rejected": True,
                },
            })
        elif case_id == "invalid-certificate-chain-rejected":
            row.update({
                "category": "tls-certificate-chain",
                "reference_sources": ["src/connect/tls/tls.cpp"],
                "input_fixture": {
                    "tls_policy": "MBEDTLS_SSL_VERIFY_REQUIRED",
                    "certificate_material": "omitted",
                },
                "expected_outcome": {
                    "classification": "rejected-invalid-chain",
                    "rejected": True
                },
                "evidence_class": "manual-hardware-required",
                "proof_scope": "non-local",
            })
        elif case_id == "weak-signature-sha1-md5-dispositioned":
            row.update({
                "category":
                "tls-weak-signature",
                "reference_sources": ["include/mbedtls/cipher_config_ece.h"],
                "input_fixture": {
                    "retained_modules": ["MBEDTLS_SHA1_C", "MBEDTLS_MD5_C"],
                    "runtime_policy": "not-accepted-runtime-policy",
                },
                "expected_outcome": {
                    "classification": "preserve-with-explicit-risk"
                },
                "secret_handling":
                "none",
            })
        elif case_id == "duplicate-connect-command-rejected":
            row["input_fixture"] = {"condition": "duplicate command id"}
            row["expected_outcome"] = {"event": "Rejected"}
        elif case_id == "large-websocket-command-rejected":
            row["input_fixture"] = {"condition": "oversized command frame"}
            row["expected_outcome"] = {"state": "BrokenCommand"}
        elif case_id == "proxy-tls-only-no-auth-plain-leg-preserved":
            row.update({
                "category":
                "connect-proxy",
                "reference_sources":
                ["doc/proxy_support.md", "src/common/http/proxy.cpp"],
                "input_fixture": {
                    "proxy_limitations": [
                        "proxy-authentication-absent",
                        "printer-to-proxy-leg-unencrypted",
                        "proxy-active-only-when-connect_tls-true",
                    ]
                },
                "expected_outcome": {
                    "classification": "preserve-current-limitations"
                },
            })
        elif case_id == "stalled-network-transfer-timeout-classified":
            row.update({
                "requirement_id":
                "IFCE-02/IFCE-03",
                "category":
                "transfer-network-timeout",
                "reference_sources":
                ["src/transfers/download.cpp", "src/transfers/transfer.cpp"],
                "input_fixture": {
                    "condition": "stalled network transfer"
                },
                "expected_outcome": {
                    "classification": "timeout-or-recovery",
                    "recovery_behavior":
                    "non-local long-running proof required",
                },
                "evidence_class":
                "manual-hardware-required",
                "proof_scope":
                "non-local",
                "secret_handling":
                "none",
            })
        self.write_source_paths(root, row["reference_sources"])
        return row

    def write_negative_fixture_surface(self, root: Path) -> None:
        self.write_file(
            root,
            "tools/bazel/fixtures/phase9_negative_network_cases.json",
            json.dumps({
                "schema_version":
                1,
                "phase":
                PHASE,
                "phase_lifecycle_id":
                PHASE_LIFECYCLE_ID,
                "negative_cases": [
                    self.negative_case(root, case_id)
                    for case_id in REQUIRED_NEGATIVE_CASE_IDS
                ],
            }),
        )

    def test_requires_all_phase9_manifests(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            (root / "tools/bazel/manifests/phase9_wui_contracts.json").unlink()

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase9_wui_contracts.json", result.stdout)

    def test_requires_connect_tls_proxy_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.connect_row(root, row_id)
                for row_id in REQUIRED_CONNECT_ROW_IDS if row_id not in {
                    "connect-registration-token-fingerprint",
                    "connect-tls-required-verification-policy",
                    "connect-proxy-minimal-limitations",
                }
            ]
            self.write_connect_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("connect-registration-token-fingerprint", result.stdout)
        self.assertIn("connect-tls-required-verification-policy",
                      result.stdout)
        self.assertIn("connect-proxy-minimal-limitations", result.stdout)

    def test_requires_wui_auth_and_resource_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.wui_row(root, row_id) for row_id in REQUIRED_WUI_ROW_IDS
                if row_id not in {
                    "wui-server-resource-model",
                    "wui-digest-auth-nonce-stale",
                    "wui-api-key-auth",
                }
            ]
            self.write_wui_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("wui-server-resource-model", result.stdout)
        self.assertIn("wui-digest-auth-nonce-stale", result.stdout)
        self.assertIn("wui-api-key-auth", result.stdout)

    def test_requires_transfer_single_slot_and_media_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.transfer_row(root, row_id)
                for row_id in REQUIRED_TRANSFER_ROW_IDS if row_id not in {
                    "transfer-single-active-slot",
                    "transfer-encrypted-aes-ctr-payload",
                    "transfer-media-race-non-local",
                }
            ]
            self.write_transfer_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("transfer-single-active-slot", result.stdout)
        self.assertIn("transfer-encrypted-aes-ctr-payload", result.stdout)
        self.assertIn("transfer-media-race-non-local", result.stdout)

    def test_requires_network_service_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.network_service_row(root, row_id)
                for row_id in REQUIRED_NETWORK_SERVICE_ROW_IDS
                if row_id not in {
                    "metrics-line-protocol-throttling",
                    "syslog-udp-destination",
                    "network-feature-gates-wui-connect",
                }
            ]
            self.write_network_service_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metrics-line-protocol-throttling", result.stdout)
        self.assertIn("syslog-udp-destination", result.stdout)
        self.assertIn("network-feature-gates-wui-connect", result.stdout)

    def test_requires_phase9_concern_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.concern_row(root, row_id)
                for row_id in REQUIRED_CONCERN_ROW_IDS if row_id not in {
                    "concern-phase9-custom-der-cert-read",
                    "concern-phase9-weak-digest-modules",
                    "concern-phase9-proxy-limitations",
                    "concern-phase9-crash-dump-upload-boundary",
                }
            ]
            self.write_concern_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("concern-phase9-custom-der-cert-read", result.stdout)
        self.assertIn("concern-phase9-weak-digest-modules", result.stdout)
        self.assertIn("concern-phase9-proxy-limitations", result.stdout)
        self.assertIn("concern-phase9-crash-dump-upload-boundary",
                      result.stdout)

    def test_rejects_secret_value_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_validation_contract(
                root, extra_text=" ".join(FORBIDDEN_MARKERS))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token_value", result.stdout)
        self.assertIn("BEGIN PRIVATE KEY", result.stdout)
        self.assertIn("raw_crash_dump", result.stdout)

    def test_rejects_non_local_evidence_overclaims(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.transfer_row(root, row_id)
                for row_id in REQUIRED_TRANSFER_ROW_IDS
            ]
            for row in rows:
                if row["id"] == "transfer-media-race-non-local":
                    row["proof_scope"] = "local"
            self.write_transfer_manifest(root, maybe_rows=rows)
            self.write_validation_contract(
                root, extra_text=" ".join(OVERCLAIM_STRINGS))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("transfer-media-race-non-local", result.stdout)
        self.assertIn("manual-hardware-required", result.stdout)
        self.assertIn("cloud verified locally", result.stdout)
        self.assertIn("cutover evidence complete", result.stdout)

    def test_requires_network_rust_api_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_rust_api_surface(
                root,
                network_text="pub enum NetworkEvidenceClass {}\n",
                lib_text=
                "#![forbid(unsafe_code)]\npub mod network;\npub use network::NetworkEvidenceClass;\n",
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for needle in [
                "NetworkParityRowId",
                "SecretHandling",
                "ConnectCommandState",
                "ProxyMode",
                "WuiAuthMode",
                "TransferRange",
                "EncryptedPayloadMetadata",
                "NetworkServiceContract",
                "NetworkParityContract",
        ]:
            self.assertIn(needle, result.stdout)

    def test_rust_unsafe_scan_does_not_swallow_lifetimes(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            network_text = "\n".join([
                *(f"pub struct {api_string};"
                  for api_string in RUST_API_STRINGS),
                "pub fn lifetime_bound<'a>(value: &'a str) -> &'a str {",
                "    unsafe { value }",
                "}",
            ])
            self.write_rust_api_surface(root, network_text=network_text)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe block", result.stdout)

    def test_requires_bazel_and_just_wiring(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_file(root, "BUILD.bazel",
                            'alias(name = "phase9_verify")\n')
            self.write_file(root, "tools/bazel/BUILD.bazel",
                            'shell_binary(name = "phase9_verify")\n')
            self.write_file(root, "tools/bazel/rust_workflow.sh",
                            'case "$command_name" in esac\n')
            self.write_file(
                root, "justfile",
                "phase9-verify:\n    bazel run //tools/bazel:phase9_verify\n")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase9_verify_tests", result.stdout)
        self.assertIn("rust_workflow.sh", result.stdout)
        self.assertIn("justfile", result.stdout)

    def test_just_wiring_rejects_verify_tests_prefix_only(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_file(
                root,
                "justfile",
                "phase9-verify:\n    bazel run //tools/bazel:phase9_verify_tests\n",
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bazel run //tools/bazel:phase9_verify", result.stdout)
        self.assertIn(
            "justfile must run phase9_verify_tests before phase9_verify",
            result.stdout)

    def test_requires_validation_lifecycle_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_file(
                root,
                f"{PHASE_DIR}/09-VALIDATION.md",
                "\n".join([
                    "---",
                    "status: complete",
                    "wave_0_complete: true",
                    "---",
                    "Quick run command",
                    "python3 tools/bazel/phase9_verify.py --quick",
                ]),
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE_LIFECYCLE_ID, result.stdout)
        self.assertIn("nyquist_compliant: true", result.stdout)

    def test_requires_negative_fixture_runner_wiring(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)

            # Act
            focused_result = self.run_verifier(["--negative-fixtures-only"],
                                               maybe_root=root)

            # Assert
            self.assertEqual(focused_result.returncode, 0,
                             focused_result.stdout)

            # Arrange
            (root / "tools/bazel/fixtures/phase9_negative_network_cases.json"
             ).unlink()

            # Act
            missing_cases_result = self.run_verifier(["--quick"],
                                                     maybe_root=root)

            # Assert
            self.assertNotEqual(missing_cases_result.returncode, 0)
            self.assertIn("phase9_negative_network_cases.json",
                          missing_cases_result.stdout)

            # Arrange
            self.write_negative_fixture_surface(root)
            (root / "tools/bazel/phase9_negative_fixtures.py").unlink()

            # Act
            missing_runner_result = self.run_verifier(["--quick"],
                                                      maybe_root=root)

            # Assert
            self.assertNotEqual(missing_runner_result.returncode, 0)
            self.assertIn("phase9_negative_fixtures.py",
                          missing_runner_result.stdout)
