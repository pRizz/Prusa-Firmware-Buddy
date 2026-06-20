#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase18_cutover_review.py"
CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
SOURCE_REF_FILES = [
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/foreign_code_inventory.json",
    "tools/bazel/manifests/unsafe_boundary_audit.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json",
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json",
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json",
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json",
]
REQUIRED_RETAINED_PACKET_IDS = [
    "packet-hal-cmsis-startup-asm",
    "packet-freertos-runtime",
    "packet-marlin-cpp-print-core-oracle",
    "packet-network-lwip-mbedtls-wui",
    "packet-filesystem-fatfs-littlefs-libsysbase",
    "packet-usb-tinyusb-and-media",
    "packet-generated-assets-resource-pipeline",
    "packet-release-signing-and-packaging",
    "packet-mmu-modbus-auxiliary-controllers",
    "packet-runtime-safety-crashdump-watchdog",
]
REQUIRED_FINAL_CRITERION_IDS = [
    "final-ci-evidence",
    "final-simulator-evidence",
    "final-hardware-safety-media-evidence",
    "final-live-network-transfer-evidence",
    "final-release-artifact-signing-evidence",
    "final-retained-code-acceptance",
    "final-residual-risk-review",
    "final-maintainer-decision",
    "final-reference-demotion-allowed",
]
REQUIRED_FINAL_EVIDENCE_FAMILIES = [
    "ci",
    "simulator",
    "hardware",
    "live-service",
    "release",
    "retained-code",
    "residual-risk",
    "maintainer-decision",
]


class Phase18CutoverReviewTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase18_cutover_review.py"
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
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase18_cutover_review.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_file(self, root: Path, path: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, full_path)

    def copy_source_ref_inputs(self, root: Path) -> None:
        for path in SOURCE_REF_FILES:
            self.copy_file(root, path)

    def copy_complete_surface(self, root: Path) -> None:
        self.copy_file(root, CONTRACT)
        self.copy_source_ref_inputs(root)

    def read_contract(self, root: Path) -> dict[str, object]:
        return json.loads((root / CONTRACT).read_text(encoding="utf-8"))

    def write_contract(self, root: Path, contract: dict[str, object]) -> None:
        self.write_file(root, CONTRACT, json.dumps(contract, indent=2, sort_keys=True) + "\n")

    def source_ids(self, path: str, collection: str, key: str) -> list[str]:
        data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        return [row[key] for row in data[collection]]

    def test_contract_accepts_complete_phase18_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_requires_all_retained_packet_ids(self) -> None:
        for packet_id in REQUIRED_RETAINED_PACKET_IDS:
            with self.subTest(packet_id=packet_id):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract["retained_code_acceptance_packets"] = [
                        packet for packet in contract["retained_code_acceptance_packets"] if packet["id"] != packet_id
                    ]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(packet_id, result.stdout)

    def test_contract_requires_retained_surface_coverage(self) -> None:
        cases = [
            (
                "tools/bazel/manifests/phase11_retained_code_justifications.json",
                "retained_code_justifications",
                "id",
            ),
            ("tools/bazel/manifests/foreign_code_inventory.json", "components", "id"),
            ("tools/bazel/manifests/unsafe_boundary_audit.json", "surfaces", "surface_id"),
        ]
        for path, collection, key in cases:
            for row_id in self.source_ids(path, collection, key):
                source_ref = f"{path}#{row_id}"
                with self.subTest(source_ref=source_ref):
                    # Arrange
                    temp_dir, root = self.make_temp_root()
                    with temp_dir:
                        self.copy_complete_surface(root)
                        contract = self.read_contract(root)
                        for packet in contract["retained_code_acceptance_packets"]:
                            packet["retained_source_refs"] = [
                                ref for ref in packet.get("retained_source_refs", []) if ref != source_ref
                            ]
                        mappings = contract.get("coverage_mappings", {})
                        if isinstance(mappings, dict):
                            mappings.pop(source_ref, None)
                        self.write_contract(root, contract)

                        # Act
                        result = self.run_verifier(["--contract-only"], maybe_root=root)

                    # Assert
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(source_ref, result.stdout)

    def test_contract_requires_final_evidence_family_coverage(self) -> None:
        for family in REQUIRED_FINAL_EVIDENCE_FAMILIES:
            with self.subTest(family=family):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract["final_demotion_criteria"] = [
                        row for row in contract["final_demotion_criteria"] if row["evidence_family"] != family
                    ]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(family, result.stdout)

    def test_contract_rejects_unknown_retained_packet_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["retained_code_acceptance_packets"][0]["status"] = "almost-accepted"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("almost-accepted", result.stdout)

    def test_contract_rejects_unknown_final_criterion_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["final_demotion_criteria"][0]["default_status"] = "almost-passed"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("almost-passed", result.stdout)

    def test_contract_requires_rev_requirement_coverage_on_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["retained_code_acceptance_packets"][0]["requirement_ids"] = []
            contract["final_demotion_criteria"][0]["requirement_ids"] = []
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("REV-", result.stdout)

    def test_contract_rejects_unresolved_source_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["final_demotion_criteria"][0]["source_refs"] = [
                "tools/bazel/manifests/phase13_ci_evidence_contract.json#missing-row",
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing-row", result.stdout)


if __name__ == "__main__":
    unittest.main()
