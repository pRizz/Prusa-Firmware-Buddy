#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase14_simulator_evidence.py"
CONTRACT = "tools/bazel/manifests/phase14_simulator_evidence_contract.json"
PHASE11_FILES = [
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
]


class Phase14SimulatorEvidenceTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase14_simulator_evidence.py"
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
        shutil.copy2(VERIFIER, root / "tools/bazel/phase14_simulator_evidence.py")
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

    def copy_phase11_inputs(self, root: Path) -> None:
        for path in PHASE11_FILES:
            self.copy_file(root, path)

    def write_wiring(
        self,
        root: Path,
        maybe_justfile: str | None = None,
        maybe_build: str | None = None,
        maybe_root_build: str | None = None,
        maybe_workflow: str | None = None,
    ) -> None:
        self.write_file(
            root,
            "tools/bazel/BUILD.bazel",
            maybe_build
            or """load(":shell_rules.bzl", "shell_binary")

filegroup(
    name = "phase14_phase11_source_ref_manifests",
    srcs = [
        "manifests/phase11_cutover_readiness.json",
        "manifests/phase11_parity_pyramid.json",
        "manifests/phase11_reference_comparisons.json",
        "manifests/phase11_requirement_evidence.json",
    ],
)

shell_binary(
    name = "phase14_verify",
    src = "rust_workflow.sh",
    data = [
        "phase14_simulator_evidence.py",
        "manifests/phase14_simulator_evidence_contract.json",
        ":phase14_phase11_source_ref_manifests",
        "//:phase14_simulator_evidence_docs",
        "//:phase11_cutover_evidence_docs",
    ],
)

shell_binary(
    name = "phase14_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase14_simulator_evidence.py",
        "phase14_simulator_evidence_test.py",
        "manifests/phase14_simulator_evidence_contract.json",
        ":phase14_phase11_source_ref_manifests",
    ],
)
""",
        )
        self.write_file(
            root,
            "BUILD.bazel",
            maybe_root_build
            or """filegroup(
    name = "phase14_simulator_evidence_docs",
    srcs = [
        ".planning/phases/14-simulator-evidence-gates/14-CONTEXT.md",
        ".planning/phases/14-simulator-evidence-gates/14-RESEARCH.md",
        ".planning/phases/14-simulator-evidence-gates/14-VALIDATION.md",
        ".planning/phases/14-simulator-evidence-gates/14-01-PLAN.md",
    ],
)

filegroup(
    name = "phase11_cutover_evidence_docs",
    srcs = [],
)

alias(
    name = "phase14_verify",
    actual = "//tools/bazel:phase14_verify",
)

alias(
    name = "phase14_verify_tests",
    actual = "//tools/bazel:phase14_verify_tests",
)
""",
        )
        self.write_file(
            root,
            "tools/bazel/rust_workflow.sh",
            maybe_workflow
            or """case "$command_name" in
  phase14_verify)
    python3 tools/bazel/phase14_simulator_evidence.py --wiring-only
    python3 tools/bazel/phase14_simulator_evidence.py --quick
    ;;
  phase14_verify_tests)
    python3 tools/bazel/phase14_simulator_evidence_test.py
    ;;
esac
""",
        )
        self.write_file(
            root,
            "justfile",
            maybe_justfile
            or """phase14-verify:
    bazel run //tools/bazel:phase14_verify_tests
    bazel run //tools/bazel:phase14_verify
""",
        )

    def copy_complete_surface(self, root: Path) -> None:
        self.copy_file(root, CONTRACT)
        self.copy_phase11_inputs(root)
        self.write_wiring(root)

    def test_contract_only_accepts_complete_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_only_rejects_missing_required_scenario(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"] = [
                scenario
                for scenario in contract["scenarios"]
                if scenario["id"] != "sim-gcode-file-print-telemetry"
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sim-gcode-file-print-telemetry", result.stdout)

    def test_contract_only_rejects_missing_source_ref_row(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["phase11_source_refs"][0] = (
                "tools/bazel/manifests/phase11_requirement_evidence.json#missing-row"
            )
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing-row", result.stdout)

    def test_contract_only_rejects_empty_requirement_ids(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["requirement_ids"] = []
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SIM requirement ID", result.stdout)

    def test_contract_only_rejects_empty_phase11_source_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["phase11_source_refs"] = []
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Phase 11 source ref", result.stdout)

    def test_contract_only_rejects_active_hardware_proof_scope(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["proof_scope"] = "hardware"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("proof_scope must be 'simulator'", result.stdout)

    def test_contract_only_rejects_path_traversal_artifact_path(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["expected_artifact_path"] = "../phase14.log"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)

    def test_contract_only_rejects_skipped_pass_nodes(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["skipped_pytest_node_ids"] = list(
                contract["scenarios"][0]["pytest_node_ids"]
            )
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skipped nodes as pass evidence", result.stdout)

    def test_security_only_rejects_secret_marker_in_generated_artifact(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_file(root, "build/ci-evidence/phase14/redacted-summary.json", "token_value\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token_value", result.stdout)

    def test_security_only_rejects_non_local_overclaim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_file(root, "build/ci-evidence/phase14/redacted-summary.json", "hardware verified locally\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware verified locally", result.stdout)

    def test_quick_writes_artifacts_and_preserves_pending_inputs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            output_dir = "build/ci-evidence/phase14"

            # Act
            result = self.run_verifier(["--quick", "--output-dir", output_dir], maybe_root=root)
            manifest = json.loads((root / output_dir / "run-manifest.json").read_text(encoding="utf-8"))
            summary = json.loads((root / output_dir / "redacted-summary.json").read_text(encoding="utf-8"))
            active_statuses = {
                row["scenario_id"]: row["status"]
                for row in manifest["scenarios"]
                if row["scenario_id"] != "sim-traceability-non-simulator-boundaries"
            }

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertTrue((root / output_dir / "normalized-scenarios.json").exists())
            self.assertTrue(
                (root / output_dir / "contract-snapshots/phase14_simulator_evidence_contract.json").exists()
            )
            self.assertTrue((root / output_dir / "logs/sim-gcode-file-print-telemetry.log").exists())
            self.assertEqual(set(active_statuses.values()), {"pending-simulator-input"})
            self.assertIn("firmware_bin", summary["external_input_names"])
            self.assertIn("mini404_qemu", summary["external_input_names"])

    def test_real_mode_requires_firmware(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--run-simulator"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--firmware", result.stdout)

    def test_real_command_is_argument_list(self) -> None:
        # Arrange
        spec = importlib.util.spec_from_file_location("phase14_simulator_evidence", VERIFIER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Act
        command = module.build_pytest_command(
            Path("firmware.bin"),
            Path("mini404"),
            ["tests/integration/test_prusa_link.py::test_idle_version"],
        )

        # Assert
        self.assertIsInstance(command, list)
        self.assertIn("-m", command)
        self.assertIn("pytest", command)
        self.assertIn("--firmware", command)
        self.assertIn("--simulator", command)
        self.assertNotIn("bash -c", " ".join(command))
        self.assertNotIn("python -c", " ".join(command))

    def test_redacted_command_for_log_uses_basenames_for_input_paths(self) -> None:
        # Arrange
        spec = importlib.util.spec_from_file_location("phase14_simulator_evidence", VERIFIER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        command = [
            "python3",
            "-m",
            "pytest",
            "tests/integration/test_prusa_link.py::test_idle_version",
            "--firmware",
            "/tmp/token_value/firmware.bin",
            "--simulator",
            "/tmp/private_key/simulator",
        ]

        # Act
        redacted = module.redacted_command_for_log(command)

        # Assert
        self.assertIn("firmware.bin", redacted)
        self.assertIn("simulator", redacted)
        self.assertNotIn("/tmp/token_value/firmware.bin", redacted)
        self.assertNotIn("/tmp/private_key/simulator", redacted)

    def test_real_mode_log_redacts_command_path_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            firmware_dir = root / "token_value"
            firmware_dir.mkdir()
            firmware = firmware_dir / "firmware.bin"
            firmware.write_bytes(b"firmware")
            firmware.with_suffix(".bbf").write_bytes(b"bbf")
            output_dir = "build/ci-evidence/phase14"

            # Act
            result = self.run_verifier(
                ["--run-simulator", "--firmware", firmware.as_posix(), "--output-dir", output_dir],
                maybe_root=root,
            )
            retained_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (root / output_dir / "logs").rglob("*")
                if path.is_file()
            )

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("token_value", retained_text)
        self.assertIn("firmware.bin", retained_text)

    def test_generated_outputs_are_redacted(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            output_dir = "build/ci-evidence/phase14"

            # Act
            result = self.run_verifier(["--quick", "--output-dir", output_dir], maybe_root=root)
            retained_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (root / output_dir).rglob("*")
                if path.is_file()
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("token_value", retained_text)
        self.assertNotIn("hardware verified locally", retained_text)
        self.assertNotIn("cutover complete", retained_text)

    def test_wiring_only_accepts_phase14_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_only_rejects_missing_just_recipe(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(
                root,
                maybe_justfile="""phase14-verify:
    bazel run //tools/bazel:phase14_verify_tests
""",
            )

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase14_verify recipe", result.stdout)

    def test_wiring_only_rejects_missing_bazel_labels(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            build_text = (root / "tools/bazel/BUILD.bazel").read_text(encoding="utf-8").replace(
                'name = "phase14_verify_tests"',
                'name = "phase14_tests_missing"',
            )
            self.write_wiring(root, maybe_build=build_text)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase14_verify_tests", result.stdout)

    def test_wiring_only_rejects_verifier_before_tests(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(
                root,
                maybe_justfile="""phase14-verify:
    bazel run //tools/bazel:phase14_verify
    bazel run //tools/bazel:phase14_verify_tests
""",
            )

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tests before verifier", result.stdout)


if __name__ == "__main__":
    unittest.main()
