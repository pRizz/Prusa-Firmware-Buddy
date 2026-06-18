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

    def write_operator_evidence(
        self,
        root: Path,
        rows: list[dict[str, str]],
        path: str = "operator-evidence.json",
    ) -> str:
        self.write_file(root, path, json.dumps({"evidence_rows": rows}, indent=2, sort_keys=True) + "\n")
        return path

    def complete_operator_row(
        self,
        scenario_id: str = "hard-storage-usb-fatfs-removable-media",
        result: str = "passed",
        artifact_ref: str | None = None,
    ) -> dict[str, str]:
        artifact_ref = artifact_ref or f"build/ci-evidence/phase15/logs/{scenario_id}.log"
        return {
            "device": "bench-printer-01",
            "printer_family": "MINI",
            "board": "BUDDY",
            "firmware_build": "phase15-test-build",
            "operator": "phase15-test-operator",
            "timestamp": "2026-06-17T23:30:00Z",
            "scenario_id": scenario_id,
            "result": result,
            "artifact_ref": artifact_ref,
            "residual_risk": "Physical coverage is limited to the named bench setup.",
        }

    def write_wiring(
        self,
        root: Path,
        maybe_tools_build: str | None = None,
        maybe_root_build: str | None = None,
        maybe_workflow: str | None = None,
        maybe_justfile: str | None = None,
    ) -> None:
        manifest_srcs = "\n".join(
            f'        "{Path(path).relative_to("tools/bazel").as_posix()}",'
            for path in SOURCE_REF_FILES
        )
        tools_build = maybe_tools_build or f"""filegroup(
    name = "phase15_source_ref_manifests",
    srcs = [
{manifest_srcs}
    ],
)

shell_binary(
    name = "phase15_verify",
    src = "rust_workflow.sh",
    data = [
        "phase15_hardware_evidence.py",
        "manifests/phase15_hardware_evidence_contract.json",
        ":phase15_source_ref_manifests",
        "//:phase15_hardware_evidence_docs",
    ],
)

shell_binary(
    name = "phase15_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase15_hardware_evidence.py",
        "phase15_hardware_evidence_test.py",
        "manifests/phase15_hardware_evidence_contract.json",
        ":phase15_source_ref_manifests",
    ],
)
"""
        root_build = maybe_root_build or """filegroup(
    name = "phase15_hardware_evidence_docs",
    srcs = [
        ".planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md",
        ".planning/phases/15-hardware-safety-and-media-qualification/15-RESEARCH.md",
        ".planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md",
        ".planning/phases/15-hardware-safety-and-media-qualification/15-01-PLAN.md",
    ],
)

alias(
    name = "phase15_verify",
    actual = "//tools/bazel:phase15_verify",
)

alias(
    name = "phase15_verify_tests",
    actual = "//tools/bazel:phase15_verify_tests",
)
"""
        workflow = maybe_workflow or """case "$command_name" in
  phase15_verify)
    python3 tools/bazel/phase15_hardware_evidence.py --wiring-only
    python3 tools/bazel/phase15_hardware_evidence.py --quick
    ;;
  phase15_verify_tests)
    python3 tools/bazel/phase15_hardware_evidence_test.py
    ;;
esac
"""
        justfile = maybe_justfile or """phase15-verify:
    bazel run //tools/bazel:phase15_verify_tests
    bazel run //tools/bazel:phase15_verify
"""
        self.write_file(root, "tools/bazel/BUILD.bazel", tools_build)
        self.write_file(root, "BUILD.bazel", root_build)
        self.write_file(root, "tools/bazel/rust_workflow.sh", workflow)
        self.write_file(root, "justfile", justfile)

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

    def test_quick_writes_expected_artifacts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for path in [
                "build/ci-evidence/phase15/run-manifest.json",
                "build/ci-evidence/phase15/normalized-scenario-results.json",
                "build/ci-evidence/phase15/redacted-hardware-summary.json",
                "build/ci-evidence/phase15/source-contract-snapshots/phase15_hardware_evidence_contract.json",
                "build/ci-evidence/phase15/logs/hard-storage-usb-fatfs-removable-media.log",
            ]:
                self.assertTrue((root / path).exists(), path)

    def test_quick_keeps_physical_rows_pending_without_operator_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)
            normalized = json.loads(
                (root / "build/ci-evidence/phase15/normalized-scenario-results.json").read_text(
                    encoding="utf-8"
                )
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = {row["id"]: row for row in normalized["scenarios"]}
        self.assertEqual(rows["hard-storage-usb-fatfs-removable-media"]["status"], "pending-hardware-input")
        self.assertEqual(
            rows["hard-contract-traceability-and-redaction-boundary"]["status"],
            "source-contract-passed",
        )

    def test_operator_evidence_updates_matching_scenario(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            operator_path = self.write_operator_evidence(root, [self.complete_operator_row()])

            # Act
            result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)
            normalized = json.loads(
                (root / "build/ci-evidence/phase15/normalized-scenario-results.json").read_text(
                    encoding="utf-8"
                )
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = {row["id"]: row for row in normalized["scenarios"]}
        scenario = rows["hard-storage-usb-fatfs-removable-media"]
        self.assertEqual(scenario["status"], "passed")
        self.assertEqual(scenario["operator"], "phase15-test-operator")
        self.assertEqual(scenario["artifact_ref"], "build/ci-evidence/phase15/logs/hard-storage-usb-fatfs-removable-media.log")

    def test_operator_evidence_rejects_missing_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            row = self.complete_operator_row()
            del row["operator"]
            operator_path = self.write_operator_evidence(root, [row])

            # Act
            result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("operator", result.stdout)

    def test_operator_evidence_rejects_unknown_scenario_and_status(self) -> None:
        cases = [
            (self.complete_operator_row(scenario_id="missing-scenario"), "missing-scenario"),
            (self.complete_operator_row(result="waived"), "waived"),
        ]
        for row, expected in cases:
            with self.subTest(expected=expected):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    operator_path = self.write_operator_evidence(root, [row])

                    # Act
                    result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_security_rejects_forbidden_generated_artifact_text(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_file(root, "build/ci-evidence/phase15/leak.json", "password_value\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("password_value", result.stdout)

    def test_security_rejects_non_local_overclaim_text(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_file(root, "build/ci-evidence/phase15/overclaim.json", "hardware verified locally\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware verified locally", result.stdout)

    def test_operator_evidence_rejects_artifact_path_traversal(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            row = self.complete_operator_row(artifact_ref="../leak.log")
            operator_path = self.write_operator_evidence(root, [row])

            # Act
            result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)

    def test_wiring_accepts_phase15_surface(self) -> None:
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
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(encoding="utf-8").replace(
                'name = "phase15_verify_tests"',
                'name = "phase15_missing_tests"',
            )
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase15_verify_tests", result.stdout)

    def test_wiring_rejects_missing_source_ref_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(encoding="utf-8").replace(
                '"manifests/phase10_toolchanger_dock_offsets.json",\n',
                "",
            )
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase10_toolchanger_dock_offsets.json", result.stdout)

    def test_wiring_rejects_verifier_before_tests(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(
                root,
                maybe_justfile="""phase15-verify:
    bazel run //tools/bazel:phase15_verify
    bazel run //tools/bazel:phase15_verify_tests
""",
            )

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tests before verifier", result.stdout)


if __name__ == "__main__":
    unittest.main()
