#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase28_final_readiness_packet.py"
CONTRACT = "tools/bazel/manifests/phase28_final_readiness_packet_contract.json"
REQUIRED_REQUIREMENTS = ["READ-01", "READ-02", "READ-03"]
REQUIRED_CRITERIA = [
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
GENERATED_ARTIFACTS = [
    "final-readiness-run-manifest.json",
    "final-readiness-packet.json",
    "normalized-readiness-criteria-table.json",
    "blocker-summary.json",
    "exception-residual-risk-summary.json",
    "reference-demotion-authorization-record.json",
    "demotion-decision-input-template.json",
    "redacted-readiness-report.md",
    "artifact-reference-summary.json",
    "contract-snapshots/phase18_cutover_review_contract.json",
    "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase26-upstream-result-row-table.json",
    "contract-snapshots/phase27-phase28-handoff-manifest.json",
]


class Phase28FinalReadinessPacketContractTest(unittest.TestCase):
    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for path in [VERIFIER, ROOT / CONTRACT]:
            destination = root / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        return temp_dir, root

    def run_verifier(self, args: list[str], maybe_root: Path | None = None) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase28_final_readiness_packet.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def read_json(self, root: Path, path: str) -> dict[str, object]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    def write_json(self, root: Path, path: str, data: dict[str, object]) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_contract_only_accepts_checked_in_contract(self) -> None:
        # Arrange
        args = ["--contract-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_declares_exact_requirements_criteria_and_outputs(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual([row["id"] for row in contract["requirements"]], REQUIRED_REQUIREMENTS)
        self.assertEqual(contract["readiness_policy"]["canonical_phase18_criteria"], REQUIRED_CRITERIA)
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)
        self.assertEqual(contract["top_level_verdicts"], ["final_readiness_status", "reference_demotion_authorization"])

    def test_contract_keeps_phase27_handoff_blocked(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(contract["phase27_handoff_policy"]["demotion_authorization"], "blocked")
        self.assertFalse(contract["phase27_handoff_policy"]["phase27_may_authorize_demotion"])

    def test_contract_requires_explicit_demotion_decision_metadata(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            contract["demotion_decision_schema"]["required_fields"],
            [
                "phase",
                "phase_lifecycle_id",
                "demotion_authorization",
                "approver",
                "approver_role",
                "decision_timestamp",
                "rationale",
                "scope",
                "evidence_refs",
            ],
        )

    def test_contract_rejects_canonical_criterion_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["readiness_policy"]["canonical_phase18_criteria"] = [
                row for row in contract["readiness_policy"]["canonical_phase18_criteria"] if row != "final-ci-evidence"
            ]
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical_phase18_criteria", result.stdout)

    def test_contract_rejects_generated_artifact_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["generated_artifacts"].append("unexpected-output.json")
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated_artifacts", result.stdout)

    def test_contract_does_not_authorize_demotion_from_evidence(self) -> None:
        # Arrange
        contract_text = (ROOT / CONTRACT).read_text(encoding="utf-8")
        test_text = Path(__file__).read_text(encoding="utf-8")
        approval_pair = '"demotion_authorization": ' + '"approved"'

        # Act / Assert
        self.assertNotIn(approval_pair, contract_text)
        self.assertNotIn(approval_pair, test_text)
        self.assertIn('"evidence_status_never_implies_approval": true', contract_text)


if __name__ == "__main__":
    unittest.main()
