#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase19_aggregate_ci_evidence.py"
OUTPUT_DIR = ROOT / "build/ci-evidence/phase19"


class Phase19AggregateCiEvidenceTest(unittest.TestCase):
    def run_verifier(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", VERIFIER.as_posix(), *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def setUp(self) -> None:
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)

    def tearDown(self) -> None:
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)

    def test_contract_only_accepts_complete_contract(self) -> None:
        # Arrange / Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_workflow_and_wiring_checks_pass(self) -> None:
        # Arrange / Act
        workflow_result = self.run_verifier(["--workflow-only"])
        wiring_result = self.run_verifier(["--wiring-only"])

        # Assert
        self.assertEqual(workflow_result.returncode, 0, workflow_result.stdout)
        self.assertEqual(wiring_result.returncode, 0, wiring_result.stdout)

    def test_ci_manifest_retains_phase_14_through_18_outputs(self) -> None:
        # Arrange / Act
        result = self.run_verifier(["--ci", "--output-dir", "build/ci-evidence/phase19"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        manifest = json.loads((OUTPUT_DIR / "run-manifest.json").read_text(encoding="utf-8"))
        phases = {row["owning_phase"] for row in manifest["gates"]}
        self.assertIn("14-simulator-evidence-gates", phases)
        self.assertIn("15-hardware-safety-and-media-qualification", phases)
        self.assertIn("16-live-network-and-transfer-qualification", phases)
        self.assertIn("17-release-candidate-artifact-and-signing-gates", phases)
        self.assertIn("18-retained-code-acceptance-and-cutover-review", phases)
        for row in manifest["gates"]:
            self.assertIn("id", row)
            self.assertIn("requirement_ids", row)
            self.assertIn("owning_phase", row)
            self.assertIn("command", row)
            self.assertIn("artifact_path", row)
            self.assertIn("status", row)
            self.assertIn("failure_reason", row)
        for phase_dir in ["phase14", "phase15", "phase16", "phase17", "phase18"]:
            self.assertTrue((OUTPUT_DIR / "phase-artifacts" / phase_dir).exists(), phase_dir)

    def test_external_evidence_rows_remain_pending_without_inputs(self) -> None:
        # Arrange / Act
        result = self.run_verifier(["--ci", "--output-dir", "build/ci-evidence/phase19"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        manifest = json.loads((OUTPUT_DIR / "run-manifest.json").read_text(encoding="utf-8"))
        external_rows = [row for row in manifest["gates"] if row["evidence_input"]]
        self.assertGreaterEqual(len(external_rows), 5)
        self.assertTrue(
            any(
                row["status"]
                in {
                    "pending-simulator-input",
                    "pending-hardware-input",
                    "pending-live-input",
                    "pending-release-input",
                    "pending-maintainer-review",
                }
                for row in external_rows
            )
        )
        self.assertFalse(any(row["status"] == "passed" for row in external_rows))

    def test_manifest_covers_all_phase_19_requirements(self) -> None:
        # Arrange / Act
        result = self.run_verifier(["--ci", "--output-dir", "build/ci-evidence/phase19"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        summary = json.loads((OUTPUT_DIR / "redacted-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(summary["requirements_covered"]),
            {
                "CIEV-01",
                "CIEV-02",
                "CIEV-03",
                "SIM-01",
                "SIM-02",
                "HARD-01",
                "HARD-02",
                "HARD-03",
                "LIVE-01",
                "LIVE-02",
                "LIVE-03",
            },
        )

    def test_ci_rejects_missing_expected_source_artifact(self) -> None:
        # Arrange
        contract_path = ROOT / "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json"
        original_contract = contract_path.read_text(encoding="utf-8")
        contract = json.loads(original_contract)
        contract["phases"][0]["expected_artifacts"].append("missing-required-artifact.json")
        contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.addCleanup(lambda: contract_path.write_text(original_contract, encoding="utf-8"))

        # Act
        result = self.run_verifier(["--ci", "--output-dir", "build/ci-evidence/phase19"])

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing expected source artifact: build/ci-evidence/phase14/missing-required-artifact.json", result.stdout)

    def test_ci_rejects_output_directory_symlink_escape(self) -> None:
        # Arrange
        original_build = ROOT / "build"
        backup_build = ROOT / "build.phase19-test-backup"
        temp_dir = tempfile.TemporaryDirectory()
        with temp_dir:
            if original_build.exists() or original_build.is_symlink():
                if backup_build.exists():
                    shutil.rmtree(backup_build)
                original_build.rename(backup_build)
            try:
                original_build.symlink_to(Path(temp_dir.name), target_is_directory=True)

                # Act
                result = self.run_verifier(["--ci", "--output-dir", "build/ci-evidence/phase19"])

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("resolves outside build/ci-evidence/phase19", result.stdout)
            finally:
                if original_build.is_symlink():
                    original_build.unlink()
                if backup_build.exists():
                    backup_build.rename(original_build)


if __name__ == "__main__":
    unittest.main()
