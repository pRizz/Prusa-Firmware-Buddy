#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase22_metadata_reconciliation.py"
CONTRACT = "tools/bazel/manifests/phase22_metadata_reconciliation_contract.json"


class Phase22MetadataReconciliationTest(unittest.TestCase):
    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase22_metadata_reconciliation.py")
        if (ROOT / CONTRACT).exists():
            shutil.copy2(ROOT / CONTRACT, root / CONTRACT)
        return temp_dir, root

    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase22_metadata_reconciliation.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def read_contract(self, root: Path) -> dict[str, object]:
        return json.loads((root / CONTRACT).read_text(encoding="utf-8"))

    def write_contract(self, root: Path, contract: dict[str, object]) -> None:
        contract_path = root / CONTRACT
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_missing_correction_source_refs_names_row_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            row = contract["metadata_corrections"][0]
            row_id = str(row["id"])
            row.pop("source_refs", None)
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(row_id, result.stdout)
        self.assertIn("source_refs", result.stdout)

    def test_non_blocking_debt_requires_owner_rationale_follow_up_and_source_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            contract["non_blocking_debt"] = [{"id": "debt-without-required-fields"}]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("debt-without-required-fields", result.stdout)
        for field in ["owner", "rationale", "follow_up_or_expiry", "source_refs"]:
            self.assertIn(field, result.stdout)

    def test_generated_artifacts_must_stay_under_phase22_output_root(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            contract["generated_artifacts"] = [
                "metadata-reconciliation-report.json",
                "../phase22-escape/audit-rerun-readiness.json",
                "/tmp/redacted-summary.md",
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated_artifacts", result.stdout)
        self.assertIn("../phase22-escape/audit-rerun-readiness.json", result.stdout)
        self.assertIn("/tmp/redacted-summary.md", result.stdout)

    def test_contract_rows_reject_sensitive_and_overclaim_markers(self) -> None:
        markers = [
            "private key",
            "token",
            "credential",
            "raw payload",
            "crash dump",
            "hardware verified locally",
            "reference demotion approved",
            "cutover complete",
            "signing verified locally",
        ]
        for marker in markers:
            with self.subTest(marker=marker):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    contract = self.read_contract(root)
                    contract["metadata_corrections"][0]["no_overclaim_rationale"] = marker
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(marker, result.stdout)


if __name__ == "__main__":
    unittest.main()
