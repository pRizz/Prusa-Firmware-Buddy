#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase23_simulator_evidence_execution.py"
CONTRACT = "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json"
PHASE14_CONTRACT = "tools/bazel/manifests/phase14_simulator_evidence_contract.json"
PHASE19_CONTRACT = "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json"
PHASE18_CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
PHASE11_FILES = [
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
]
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase23"


class Phase23SimulatorEvidenceExecutionTest(unittest.TestCase):

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        shutil.copy2(
            VERIFIER,
            root / "tools/bazel/phase23_simulator_evidence_execution.py")
        shutil.copy2(
            ROOT / "tools/bazel/phase23_execution_policy.py",
            root / "tools/bazel/phase23_execution_policy.py",
        )
        shutil.copy2(
            ROOT / "tools/bazel/phase23_execution_contract.py",
            root / "tools/bazel/phase23_execution_contract.py",
        )
        for path in [
                CONTRACT, PHASE14_CONTRACT, PHASE19_CONTRACT, PHASE18_CONTRACT,
                *PHASE11_FILES
        ]:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, destination)
        return temp_dir, root

    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase23_simulator_evidence_execution.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def read_phase14_contract(self, root: Path) -> dict[str, object]:
        return json.loads(
            (root / PHASE14_CONTRACT).read_text(encoding="utf-8"))

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def write_evidence_input(
        self,
        root: Path,
        rows: list[dict[str, object]],
        path: str = "phase23-evidence-input.json",
        maybe_packet_updates: dict[str, object] | None = None,
    ) -> str:
        packet = {
            "simulator_evidence_packet": {
                "completed_at": "2026-06-23T20:00:00Z",
                "evidence_run_id": "sim-run-2026-06-23",
                "firmware_identity": {
                    "build_id": "fw-test-build",
                    "firmware_basename": "firmware.bin"
                },
                "operator": "maintainer",
                "phase": "23-simulator-evidence-execution",
                "scenario_results": rows,
                "simulator_identity": {
                    "name": "mini404",
                    "version": "test"
                },
                "started_at": "2026-06-23T19:00:00Z"
            }
        }
        if maybe_packet_updates is not None:
            packet["simulator_evidence_packet"].update(maybe_packet_updates)
        self.write_file(root, path,
                        json.dumps(packet, indent=2, sort_keys=True) + "\n")
        return path

    def complete_rows(self, root: Path) -> list[dict[str, object]]:
        contract = self.read_phase14_contract(root)
        return [{
            "artifact_refs": [f"external://phase23/{scenario['id']}.log"],
            "redaction_status": "passed",
            "scenario_id": scenario["id"],
            "source_ref_status": "passed",
            "source_status": "passed",
            "status": "passed",
            "status_reason": "real simulator scenario passed",
        } for scenario in contract["scenarios"]]

    def write_phase23_wiring(
        self,
        root: Path,
        maybe_tools_build: str | None = None,
        maybe_root_build: str | None = None,
        maybe_workflow: str | None = None,
        maybe_justfile: str | None = None,
    ) -> None:
        tools_build = maybe_tools_build if maybe_tools_build is not None else """filegroup(
    name = "phase23_source_ref_manifests",
    srcs = [
        "manifests/phase14_simulator_evidence_contract.json",
        "manifests/phase18_cutover_review_contract.json",
        "manifests/phase19_aggregate_ci_evidence_contract.json",
        "manifests/phase23_simulator_evidence_execution_contract.json",
    ],
)

shell_binary(
    name = "phase23_verify",
    src = "rust_workflow.sh",
    data = [
        "phase23_simulator_evidence_execution.py",
        "manifests/phase23_simulator_evidence_execution_contract.json",
        ":phase23_source_ref_manifests",
        "//:phase23_simulator_evidence_execution_docs",
    ],
)

shell_binary(
    name = "phase23_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase23_simulator_evidence_execution.py",
        "phase23_simulator_evidence_execution_test.py",
        "manifests/phase23_simulator_evidence_execution_contract.json",
        ":phase23_source_ref_manifests",
    ],
)
"""
        root_build = maybe_root_build if maybe_root_build is not None else """filegroup(
    name = "phase23_simulator_evidence_execution_docs",
    srcs = [
        ".planning/phases/23-simulator-evidence-execution/23-CONTEXT.md",
        ".planning/phases/23-simulator-evidence-execution/23-RESEARCH.md",
        ".planning/phases/23-simulator-evidence-execution/23-VALIDATION.md",
        ".planning/phases/23-simulator-evidence-execution/23-01-PLAN.md",
    ],
)

alias(
    name = "phase23_verify",
    actual = "//tools/bazel:phase23_verify",
)

alias(
    name = "phase23_verify_tests",
    actual = "//tools/bazel:phase23_verify_tests",
)
"""
        workflow = maybe_workflow if maybe_workflow is not None else """case "$command_name" in
  phase23_verify)
    python3 tools/bazel/phase23_simulator_evidence_execution.py --wiring-only
    python3 tools/bazel/phase23_simulator_evidence_execution.py --quick --output-dir build/ci-evidence/phase23
    ;;
  phase23_verify_tests)
    python3 tools/bazel/phase23_simulator_evidence_execution_test.py
    ;;
esac
"""
        justfile = maybe_justfile if maybe_justfile is not None else """phase23-verify:
    bazel run //tools/bazel:phase23_verify_tests
    bazel run //tools/bazel:phase23_verify
"""
        self.write_file(root, "tools/bazel/BUILD.bazel", tools_build)
        self.write_file(root, "BUILD.bazel", root_build)
        self.write_file(root, "tools/bazel/rust_workflow.sh", workflow)
        self.write_file(root, "justfile", justfile)

    def test_contract_only_accepts_complete_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_quick_writes_blocked_placeholder_outputs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)
            manifest = json.loads(
                (root / DEFAULT_OUTPUT_DIR /
                 "simulator-result-manifest.json").read_text())

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(manifest["real_simulator_evidence_supplied"])
        self.assertEqual(manifest["status"], "blocked")
        self.assertEqual(manifest["status_counts"], {"blocked": 9})

    def test_evidence_input_accepts_complete_packet(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            input_path = self.write_evidence_input(root,
                                                   self.complete_rows(root))

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)
            manifest = json.loads(
                (root / DEFAULT_OUTPUT_DIR /
                 "simulator-result-manifest.json").read_text())

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(manifest["real_simulator_evidence_supplied"])
        self.assertEqual(manifest["status"], "passed")
        self.assertEqual(manifest["status_counts"], {"passed": 9})

    def test_evidence_input_rejects_missing_scenario(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)[:-1]
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing scenario results", result.stdout)

    def test_evidence_input_rejects_pending_source_status_as_passed(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["source_status"] = "pending-simulator-input"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot pass with source_status=pending-simulator-input",
                      result.stdout)

    def test_exception_requested_requires_exception_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["status"] = "exception-requested"
            rows[0]["source_status"] = "failed"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exception_request", result.stdout)

    def test_evidence_input_rejects_forbidden_secret_fields(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["token_value"] = "secret"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden evidence marker", result.stdout)

    def test_evidence_input_rejects_mixed_case_forbidden_secret_fields(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["Token"] = "secret"
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contains forbidden evidence fields: Token",
                      result.stdout)

    def test_evidence_input_rejects_empty_artifact_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["artifact_refs"] = []
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact_refs must contain at least one item",
                      result.stdout)

    def test_evidence_input_rejects_malformed_identity_fields(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            input_path = self.write_evidence_input(
                root,
                self.complete_rows(root),
                maybe_packet_updates={"firmware_identity": "fw-test-build"},
            )

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("firmware_identity must be an object", result.stdout)

    def test_evidence_input_rejects_artifact_path_traversal(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_rows(root)
            rows[0]["artifact_refs"] = ["../secret.log"]
            input_path = self.write_evidence_input(root, rows)

            # Act
            result = self.run_verifier(["--evidence-input", input_path],
                                       maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)

    def test_wiring_only_accepts_phase23_entries(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase23_wiring(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_only_rejects_missing_just_recipe(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase23_wiring(root, maybe_justfile="")

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase23-verify:", result.stdout)


if __name__ == "__main__":
    unittest.main()
