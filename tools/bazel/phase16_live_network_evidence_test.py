#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase16_live_network_evidence.py"
CONTRACT = "tools/bazel/manifests/phase16_live_network_evidence_contract.json"
SOURCE_REF_FILES = [
    "tools/bazel/manifests/phase9_connect_contracts.json",
    "tools/bazel/manifests/phase9_wui_contracts.json",
    "tools/bazel/manifests/phase9_network_service_contracts.json",
    "tools/bazel/manifests/phase9_transfer_contracts.json",
    "tools/bazel/manifests/phase9_network_concern_dispositions.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json",
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json",
]
DOC_REF_FILES = [
    "doc/proxy_support.md",
    "doc/metrics.md",
]


class Phase16LiveNetworkEvidenceTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase16_live_network_evidence.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        shutil.copy2(VERIFIER, root / "tools/bazel/phase16_live_network_evidence.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_file(self, root: Path, path: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, full_path)

    def read_contract(self, root: Path) -> dict[str, object]:
        return json.loads((root / CONTRACT).read_text(encoding="utf-8"))

    def write_contract(self, root: Path, contract: dict[str, object]) -> None:
        self.write_file(root, CONTRACT, json.dumps(contract, indent=2, sort_keys=True) + "\n")

    def copy_source_ref_inputs(self, root: Path) -> None:
        for path in SOURCE_REF_FILES + DOC_REF_FILES:
            self.copy_file(root, path)

    def copy_complete_surface(self, root: Path) -> None:
        self.copy_file(root, CONTRACT)
        self.copy_source_ref_inputs(root)

    def test_contract_accepts_complete_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_requires_all_live_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"] = [
                scenario
                for scenario in contract["scenarios"]
                if scenario["id"] != "live-connect-registration-token-fingerprint"
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("live-connect-registration-token-fingerprint", result.stdout)

    def test_contract_requires_live_requirements(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            for scenario in contract["scenarios"]:
                scenario["requirement_ids"] = [
                    requirement_id
                    for requirement_id in scenario["requirement_ids"]
                    if requirement_id != "LIVE-02"
                ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("LIVE-02", result.stdout)

    def test_contract_requires_surface_coverage(self) -> None:
        cases = [
            "connect-registration",
            "connect-telemetry-events",
            "connect-command-channel",
            "connect-proxy",
            "prusalink-api-v1",
            "wui-digest-auth",
            "wui-api-key-auth",
            "sntp-client",
            "mdns-responder",
            "syslog-and-metrics",
            "wui-upload-transfer",
            "connect-tls-policy",
            "wui-negative-protocol",
            "connect-long-transfer",
            "crash-dump-upload",
        ]
        for surface in cases:
            with self.subTest(surface=surface):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    for scenario in contract["scenarios"]:
                        if scenario["service_surface"] == surface:
                            scenario["service_surface"] = f"missing-{surface}"
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(surface, result.stdout)

    def test_contract_rejects_bad_source_ref(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["source_contract_refs"][0] = "../escape.json#missing-row"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source ref", result.stdout)
        self.assertIn("escape", result.stdout)

    def test_contract_rejects_passed_default_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["default_status"] = "passed"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("passed", result.stdout)

    def test_contract_requires_redaction_and_residual_gates(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["redaction_required"] = False
            contract["scenarios"][0]["credential_boundary"] = ""
            contract["scenarios"][0]["residual_non_live_gates"] = []
            contract["scenarios"][0]["unsupported_claims"] = []
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("redaction_required", result.stdout)
        self.assertIn("credential_boundary", result.stdout)
        self.assertIn("residual_non_live_gates", result.stdout)
        self.assertIn("unsupported_claims", result.stdout)


if __name__ == "__main__":
    unittest.main()
