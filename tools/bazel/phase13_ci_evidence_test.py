#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase13_ci_evidence.py"

CONTRACT = "tools/bazel/manifests/phase13_ci_evidence_contract.json"
WORKFLOW = ".github/workflows/ci-evidence.yml"
VALIDATION = ".planning/phases/13-ci-evidence-orchestration/13-VALIDATION.md"
PHASE11_VERIFICATION = (
    ".planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md"
)
PHASE11_REQUIREMENTS = "tools/bazel/manifests/phase11_requirement_evidence.json"
PHASE11_CUTOVER = "tools/bazel/manifests/phase11_cutover_readiness.json"
PHASE11_RETAINED = "tools/bazel/manifests/phase11_retained_code_justifications.json"
PHASE11_COMPARISONS = "tools/bazel/manifests/phase11_reference_comparisons.json"


class Phase13CiEvidenceTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase13_ci_evidence.py"
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
        shutil.copy2(VERIFIER, root / "tools/bazel/phase13_ci_evidence.py")
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
        self.write_file(root, CONTRACT, json.dumps(contract, indent=2) + "\n")

    def write_workflow(self, root: Path, maybe_text: str | None = None) -> None:
        workflow = maybe_text or """name: CI Evidence

on:
  pull_request:
    paths:
      - .github/workflows/ci-evidence.yml
      - .github/workflows/**
      - BUILD.bazel
      - MODULE.bazel
      - .bazelrc
      - platforms/**
      - tools/bazel/**
      - tools/bazel/manifests/**
      - Cargo.toml
      - Cargo.lock
      - rust/**
      - .planning/PROJECT.md
      - .planning/ROADMAP.md
      - .planning/REQUIREMENTS.md
      - .planning/STATE.md
      - .planning/phases/**
      - .planning/milestones/**
      - CMakeLists.txt
      - ProjectOptions.cmake
      - cmake/**
      - utils/build.py
      - utils/pack_fw.py
      - utils/dfu.py
      - utils/presets/**
      - src/resources/**
      - src/lang/**
      - lib/Add*.cmake
  workflow_dispatch:

permissions:
  contents: read

jobs:
  phase13-ci-evidence:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
      - name: Write CI evidence
        run: python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13
      - name: Upload CI evidence
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: phase13-ci-evidence-${{ github.run_id }}-${{ github.run_attempt }}
          path: build/ci-evidence/phase13/
          retention-days: 30
          if-no-files-found: error
"""
        self.write_file(root, WORKFLOW, workflow)

    def write_wiring(self, root: Path, maybe_justfile: str | None = None, maybe_workflow: str | None = None) -> None:
        self.write_file(
            root,
            "tools/bazel/BUILD.bazel",
            """shell_binary(
    name = "phase13_verify",
    src = "rust_workflow.sh",
    data = [
        "phase13_ci_evidence.py",
        "manifests/phase13_ci_evidence_contract.json",
        "//:phase13_ci_evidence_docs",
    ],
)

shell_binary(
    name = "phase13_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase13_ci_evidence.py",
        "phase13_ci_evidence_test.py",
        "manifests/phase13_ci_evidence_contract.json",
    ],
)
""",
        )
        self.write_file(
            root,
            "tools/bazel/rust_workflow.sh",
            maybe_workflow
            or """case "$command_name" in
  phase13_verify)
    python3 tools/bazel/phase13_ci_evidence.py --wiring-only
    python3 tools/bazel/phase13_ci_evidence.py --quick
    ;;
  phase13_verify_tests)
    python3 tools/bazel/phase13_ci_evidence_test.py
    ;;
esac
""",
        )
        self.write_file(
            root,
            "BUILD.bazel",
            """filegroup(
    name = "phase13_ci_evidence_docs",
    srcs = [
        ".planning/phases/13-ci-evidence-orchestration/13-CONTEXT.md",
        ".planning/phases/13-ci-evidence-orchestration/13-RESEARCH.md",
        ".planning/phases/13-ci-evidence-orchestration/13-VALIDATION.md",
        ".planning/phases/13-ci-evidence-orchestration/13-01-PLAN.md",
        ".github/workflows/ci-evidence.yml",
    ],
)

alias(
    name = "phase13_verify",
    actual = "//tools/bazel:phase13_verify",
)

alias(
    name = "phase13_verify_tests",
    actual = "//tools/bazel:phase13_verify_tests",
)
""",
        )
        self.write_file(
            root,
            "justfile",
            maybe_justfile
            or """phase13-verify:
    bazel run //tools/bazel:phase13_verify_tests
    bazel run //tools/bazel:phase13_verify
""",
        )

    def write_phase11_verifier(self, root: Path, returncode: int = 0) -> None:
        self.write_file(
            root,
            "tools/bazel/phase11_verify.py",
            f"""#!/usr/bin/env python3
import sys

print("phase11 quick fixture")
sys.exit({returncode})
""",
        )

    def copy_required_phase11_inputs(self, root: Path) -> None:
        self.write_file(root, PHASE11_VERIFICATION, "phase 11 verification fixture\n")
        for path in [
            PHASE11_REQUIREMENTS,
            PHASE11_CUTOVER,
            PHASE11_RETAINED,
            PHASE11_COMPARISONS,
        ]:
            self.copy_file(root, path)

    def copy_complete_surface(self, root: Path, phase11_returncode: int = 0) -> None:
        self.copy_file(root, CONTRACT)
        self.copy_required_phase11_inputs(root)
        self.write_file(root, VALIDATION, "local validation fixture\n")
        self.write_workflow(root)
        self.write_wiring(root)
        self.write_phase11_verifier(root, phase11_returncode)

    def test_contract_only_accepts_complete_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_only_rejects_missing_required_gate(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["gates"] = [
                gate
                for gate in contract["gates"]
                if gate["id"] != "ciev-03-redacted-summary"
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ciev-03-redacted-summary", result.stdout)

    def test_contract_only_rejects_path_traversal_artifact_path(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["gates"][0]["expected_artifact_path"] = "../phase13-workflow.log"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)

    def test_contract_only_rejects_unknown_requirement_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["gates"][0]["requirement_id"] = "UNKNOWN-01"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("UNKNOWN-01", result.stdout)

    def test_contract_only_rejects_unsupported_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["gates"][0]["allowed_statuses"] = ["passed", "waived"]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("waived", result.stdout)

    def test_security_only_rejects_secret_marker(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_file(root, VALIDATION, "password_value\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("password_value", result.stdout)

    def test_security_only_rejects_non_local_overclaim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_file(root, VALIDATION, "hardware verified locally\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware verified locally", result.stdout)

    def test_workflow_only_accepts_ci_evidence_workflow(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--workflow-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_workflow_only_rejects_missing_artifact_upload(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            workflow = (root / WORKFLOW).read_text(encoding="utf-8").replace(
                "actions/upload-artifact@v7", "actions/cache@v4"
            )
            self.write_workflow(root, workflow)

            # Act
            result = self.run_verifier(["--workflow-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("actions/upload-artifact@v7", result.stdout)

    def test_workflow_only_rejects_write_permissions(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            workflow = (root / WORKFLOW).read_text(encoding="utf-8").replace(
                "contents: read", "contents: write"
            )
            self.write_workflow(root, workflow)

            # Act
            result = self.run_verifier(["--workflow-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contents: write", result.stdout)

    def test_workflow_only_rejects_hidden_planning_upload_path(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            workflow = (root / WORKFLOW).read_text(encoding="utf-8").replace(
                "path: build/ci-evidence/phase13/", "path: .planning/"
            )
            self.write_workflow(root, workflow)

            # Act
            result = self.run_verifier(["--workflow-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hidden planning", result.stdout)

    def test_workflow_only_rejects_inline_shell_logic(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            workflow = (root / WORKFLOW).read_text(encoding="utf-8") + "\n      - run: |\n          echo bad\n"
            self.write_workflow(root, workflow)

            # Act
            result = self.run_verifier(["--workflow-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("run: |", result.stdout)

    def test_ci_writes_manifest_logs_snapshots_and_redacted_summary(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            output_dir = "build/ci-evidence/phase13"

            # Act
            result = self.run_verifier(["--ci", "--output-dir", output_dir], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertTrue((root / output_dir / "run-manifest.json").exists())
            self.assertTrue((root / output_dir / "redacted-summary.json").exists())
            self.assertTrue((root / output_dir / "logs/phase11-quick.log").exists())
            self.assertTrue(
                (root / output_dir / "manifest-snapshots/phase13_ci_evidence_contract.json").exists()
            )
            self.assertTrue(
                (root / output_dir / "normalized-comparisons/phase11_reference_comparisons.json").exists()
            )

    def test_ci_manifest_records_failed_gate_after_logs_are_written(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root, phase11_returncode=7)
            output_dir = "build/ci-evidence/phase13"

            # Act
            result = self.run_verifier(["--ci", "--output-dir", output_dir], maybe_root=root)
            manifest = json.loads((root / output_dir / "run-manifest.json").read_text(encoding="utf-8"))
            aggregate_gate = next(
                gate
                for gate in manifest["gates"]
                if gate["id"] == "ciev-01-aggregate-cutover-verifier"
            )
            log_exists = (root / output_dir / "logs/phase11-quick.log").exists()

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(log_exists)
        self.assertEqual(aggregate_gate["status"], "failed")
        self.assertIn("exit code 7", aggregate_gate["failure_reason"])

    def test_ci_manifest_records_missing_contract_gate_after_logs_are_written(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["gates"] = [
                gate
                for gate in contract["gates"]
                if gate["id"] != "ciev-02-run-manifest"
            ]
            self.write_contract(root, contract)
            output_dir = "build/ci-evidence/phase13"

            # Act
            result = self.run_verifier(["--ci", "--output-dir", output_dir], maybe_root=root)
            manifest = json.loads((root / output_dir / "run-manifest.json").read_text(encoding="utf-8"))
            contract_gate = next(gate for gate in manifest["gates"] if gate["id"] == "ciev-02-run-manifest")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(contract_gate["status"], "failed")
        self.assertIn("exit code", contract_gate["failure_reason"])

    def test_ci_redacts_forbidden_snapshot_before_writing_artifacts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_file(root, PHASE11_REQUIREMENTS, "token_value\n")
            output_dir = "build/ci-evidence/phase13"

            # Act
            result = self.run_verifier(["--ci", "--output-dir", output_dir], maybe_root=root)
            retained_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (root / output_dir).rglob("*")
                if path.is_file()
            )
            manifest = json.loads((root / output_dir / "run-manifest.json").read_text(encoding="utf-8"))
            redacted_gate = next(gate for gate in manifest["gates"] if gate["id"] == "ciev-03-redacted-summary")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("token_value", retained_text)
        self.assertEqual(redacted_gate["status"], "failed")

    def test_ci_manifest_preserves_pending_non_local_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            output_dir = "build/ci-evidence/phase13"

            # Act
            result = self.run_verifier(["--ci", "--output-dir", output_dir], maybe_root=root)
            summary = json.loads((root / output_dir / "redacted-summary.json").read_text(encoding="utf-8"))

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            summary["pending_non_local_evidence"],
            [
                "simulator evidence (Phase 14)",
                "hardware safety and media evidence (Phase 15)",
                "live network and transfer evidence (Phase 16)",
                "release-candidate artifact and signing evidence (Phase 17)",
                "retained-code acceptance and cutover review evidence (Phase 18)",
            ],
        )

    def test_wiring_only_accepts_phase13_bazel_and_just_surface(self) -> None:
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
            self.write_wiring(root, maybe_justfile="phase12-verify:\n    true\n")

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase13-verify:", result.stdout)

    def test_wiring_only_rejects_missing_rust_workflow_dispatch(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root, maybe_workflow="case \"$command_name\" in\n  phase12_verify) true ;;\nesac\n")

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase13_verify)", result.stdout)


if __name__ == "__main__":
    unittest.main()
