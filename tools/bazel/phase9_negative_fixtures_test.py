#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools/bazel/phase9_negative_fixtures.py"
PHASE = "09-network-web-services-and-transfers"
PHASE_LIFECYCLE_ID = "9-2026-06-14T02-15-21"

REQUIRED_NEGATIVE_CASE_IDS = [
    "custom-cert-valid-der-intentional-delta",
    "custom-cert-missing-der-preserved-defect",
    "custom-cert-invalid-der-rejected",
    "invalid-certificate-chain-rejected",
    "weak-signature-sha1-md5-dispositioned",
    "duplicate-connect-command-rejected",
    "large-websocket-command-rejected",
    "proxy-tls-only-no-auth-plain-leg-preserved",
    "stalled-network-transfer-timeout-classified",
]

FORBIDDEN_SECRET_MARKERS = [
    "token_value",
    "password_value",
    "wifi_password",
    "certificate_bytes",
    "private_key",
    "BEGIN PRIVATE KEY",
    "raw_crash_dump",
    "crash_dump_payload",
]


class Phase9NegativeFixturesTest(unittest.TestCase):
    def run_runner(self, cases_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, RUNNER.as_posix(), "--cases", cases_path.as_posix()],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def base_case(self, case_id: str) -> dict[str, object]:
        case: dict[str, object] = {
            "id": case_id,
            "requirement_id": "IFCE-02",
            "category": "connect-command",
            "reference_sources": [
                "src/connect/connect.cpp",
                "src/connect/planner.cpp",
            ],
            "input_fixture": {"condition": "metadata-only"},
            "expected_outcome": {"classification": "source-backed"},
            "evidence_class": "source-audit",
            "proof_scope": "local",
            "secret_handling": "named-only-redacted",
            "intentional_delta": "none",
            "runnable_check": "metadata-schema-only",
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        }
        if case_id == "custom-cert-valid-der-intentional-delta":
            case.update(
                {
                    "category": "custom-certificate",
                    "reference_sources": ["src/connect/tls/tls.cpp"],
                    "input_fixture": {
                        "custom_certificate_path": "/internal/connect/connect.der",
                        "certificate_material": "omitted",
                    },
                    "expected_outcome": {"classification": "intentional-delta-fixture"},
                    "evidence_class": "manual-hardware-required",
                    "proof_scope": "non-local",
                    "intentional_delta": "approved",
                }
            )
        elif case_id == "custom-cert-missing-der-preserved-defect":
            case.update(
                {
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
                }
            )
        elif case_id == "custom-cert-invalid-der-rejected":
            case.update(
                {
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
                }
            )
        elif case_id == "invalid-certificate-chain-rejected":
            case.update(
                {
                    "category": "tls-certificate-chain",
                    "reference_sources": ["src/connect/tls/tls.cpp"],
                    "input_fixture": {
                        "tls_policy": "MBEDTLS_SSL_VERIFY_REQUIRED",
                        "certificate_material": "omitted",
                    },
                    "expected_outcome": {"classification": "rejected-invalid-chain", "rejected": True},
                    "evidence_class": "manual-hardware-required",
                    "proof_scope": "non-local",
                }
            )
        elif case_id == "weak-signature-sha1-md5-dispositioned":
            case.update(
                {
                    "category": "tls-weak-signature",
                    "reference_sources": ["include/mbedtls/cipher_config_ece.h"],
                    "input_fixture": {
                        "retained_modules": ["MBEDTLS_SHA1_C", "MBEDTLS_MD5_C"],
                        "runtime_policy": "not-accepted-runtime-policy",
                    },
                    "expected_outcome": {"classification": "preserve-with-explicit-risk"},
                    "secret_handling": "none",
                }
            )
        elif case_id == "duplicate-connect-command-rejected":
            case["input_fixture"] = {"condition": "duplicate command id"}
            case["expected_outcome"] = {"event": "Rejected"}
        elif case_id == "large-websocket-command-rejected":
            case["input_fixture"] = {"condition": "oversized command frame"}
            case["expected_outcome"] = {"state": "BrokenCommand"}
        elif case_id == "proxy-tls-only-no-auth-plain-leg-preserved":
            case.update(
                {
                    "category": "connect-proxy",
                    "reference_sources": ["doc/proxy_support.md", "src/common/http/proxy.cpp"],
                    "input_fixture": {
                        "proxy_limitations": [
                            "proxy-authentication-absent",
                            "printer-to-proxy-leg-unencrypted",
                            "proxy-active-only-when-connect_tls-true",
                        ]
                    },
                    "expected_outcome": {"classification": "preserve-current-limitations"},
                }
            )
        elif case_id == "stalled-network-transfer-timeout-classified":
            case.update(
                {
                    "requirement_id": "IFCE-02/IFCE-03",
                    "category": "transfer-network-timeout",
                    "reference_sources": ["src/transfers/download.cpp", "src/transfers/transfer.cpp"],
                    "input_fixture": {"condition": "stalled network transfer"},
                    "expected_outcome": {
                        "classification": "timeout-or-recovery",
                        "recovery_behavior": "non-local long-running proof required",
                    },
                    "evidence_class": "manual-hardware-required",
                    "proof_scope": "non-local",
                    "secret_handling": "none",
                }
            )
        return case

    def fixture_payload(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "negative_cases": [self.base_case(case_id) for case_id in REQUIRED_NEGATIVE_CASE_IDS],
        }

    def write_fixture(self, payload: dict[str, object]) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "negative_cases.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_accepts_complete_fixture_set(self) -> None:
        # Arrange
        fixture_path = self.write_fixture(self.fixture_payload())

        # Act
        result = self.run_runner(fixture_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("validation passed", result.stdout)

    def test_rejects_missing_required_case(self) -> None:
        # Arrange
        payload = self.fixture_payload()
        payload["negative_cases"] = [
            case
            for case in payload["negative_cases"]
            if case["id"] != "custom-cert-invalid-der-rejected"
        ]
        fixture_path = self.write_fixture(payload)

        # Act
        result = self.run_runner(fixture_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("custom-cert-invalid-der-rejected", result.stdout)

    def test_rejects_invalid_lifecycle_id(self) -> None:
        # Arrange
        payload = self.fixture_payload()
        payload["phase_lifecycle_id"] = "wrong-lifecycle"
        fixture_path = self.write_fixture(payload)

        # Act
        result = self.run_runner(fixture_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE_LIFECYCLE_ID, result.stdout)

    def test_rejects_local_proof_for_non_local_evidence(self) -> None:
        # Arrange
        payload = self.fixture_payload()
        cases = copy.deepcopy(payload["negative_cases"])
        for case in cases:
            if case["id"] == "stalled-network-transfer-timeout-classified":
                case["proof_scope"] = "local"
        payload["negative_cases"] = cases
        fixture_path = self.write_fixture(payload)

        # Act
        result = self.run_runner(fixture_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stalled-network-transfer-timeout-classified", result.stdout)
        self.assertIn("manual-hardware-required", result.stdout)

    def test_rejects_forbidden_secret_and_binary_markers(self) -> None:
        # Arrange
        payload = self.fixture_payload()
        cases = copy.deepcopy(payload["negative_cases"])
        for case in cases:
            if case["id"] == "custom-cert-invalid-der-rejected":
                case["expected_outcome"] = {
                    "classification": "rejected-invalid-der",
                    "forbidden": " ".join(FORBIDDEN_SECRET_MARKERS),
                }
        payload["negative_cases"] = cases
        fixture_path = self.write_fixture(payload)

        # Act
        result = self.run_runner(fixture_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token_value", result.stdout)
        self.assertIn("BEGIN PRIVATE KEY", result.stdout)


if __name__ == "__main__":
    unittest.main()
