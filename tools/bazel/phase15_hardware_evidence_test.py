#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase15_hardware_evidence.py"
CONTRACT = "tools/bazel/manifests/phase15_hardware_evidence_contract.json"
SOURCE_REF_FILES = [
    "tools/bazel/manifests/phase6_safety_gates.json",
    "tools/bazel/manifests/phase7_storage_media.json",
    "tools/bazel/manifests/phase8_gui_workflows.json",
    "tools/bazel/manifests/phase8_display_layouts.json",
    "tools/bazel/manifests/phase10_auxiliary_controllers.json",
    "tools/bazel/manifests/phase10_mmu_transport.json",
    "tools/bazel/manifests/phase10_modbus_rs485.json",
    "tools/bazel/manifests/phase10_toolchanger_dock_offsets.json",
    "tools/bazel/manifests/phase10_auxiliary_build_update.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json",
]


class Phase15HardwareEvidenceTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase15_hardware_evidence.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        shutil.copy2(VERIFIER, root / "tools/bazel/phase15_hardware_evidence.py")
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
        for path in SOURCE_REF_FILES:
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

    def test_contract_requires_all_hardware_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"] = [
                scenario
                for scenario in contract["scenarios"]
                if scenario["id"] != "hard-safety-watchdog-crash-recovery"
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hard-safety-watchdog-crash-recovery", result.stdout)

    def test_contract_requires_supported_family_surface_coverage(self) -> None:
        cases = [
            ("printer_family", {"COREONE", "all-supported"}, "COREONE"),
            ("board", {"DWARF", "all-supported"}, "DWARF"),
            ("media_surface", {"semihosting"}, "semihosting"),
        ]
        for field, removed_values, expected in cases:
            with self.subTest(field=field, expected=expected):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract["scenarios"] = [
                        scenario
                        for scenario in contract["scenarios"]
                        if scenario.get(field) not in removed_values
                    ]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_contract_requires_all_hard_requirements(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            for scenario in contract["scenarios"]:
                scenario["requirement_ids"] = [
                    requirement_id
                    for requirement_id in scenario["requirement_ids"]
                    if requirement_id != "HARD-02"
                ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("HARD-02", result.stdout)

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

    def test_contract_rejects_invalid_pass_status_without_operator_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["default_status"] = "passed"
            contract["scenarios"][0]["operator_metadata_required"] = [
                field
                for field in contract["scenarios"][0]["operator_metadata_required"]
                if field != "operator"
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("passed", result.stdout)
        self.assertIn("operator", result.stdout)

    def test_contract_rejects_missing_residual_risk(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["residual_risk_required"] = False
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("residual risk", result.stdout)


if __name__ == "__main__":
    unittest.main()
