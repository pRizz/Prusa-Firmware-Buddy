#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase32_blocker_register_triage.py"
CONTRACT = ROOT / "tools/bazel/manifests/phase32_blocker_register_triage_contract.json"


class Phase32BlockerRegisterTriageTest(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location("phase32_blocker_register_triage", VERIFIER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_verifier(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", VERIFIER.as_posix(), *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def read_contract(self) -> dict[str, object]:
        return json.loads(CONTRACT.read_text(encoding="utf-8"))

    def assert_ineligible_policy(self, classification: dict[str, object], problem_kind: str, blocker_kind: str) -> None:
        self.assertEqual(classification["row_problem_kind"], problem_kind)
        self.assertEqual(classification["blocker_kind"], blocker_kind)
        self.assertEqual(classification["proof_eligibility"], "ineligible")
        self.assertIn(classification["severity"], {"critical", "high", "medium"})
        self.assertIsInstance(classification["owner_ref"], str)
        self.assertIsInstance(classification["required_next_action"], str)
        self.assertTrue(classification["owner_ref"])
        self.assertTrue(classification["required_next_action"])

    def test_contract_only_accepts_complete_phase32_contract(self) -> None:
        # Arrange / Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("phase32_blocker_register_triage_contract", result.stdout)

    def test_contract_validation_rejects_missing_required_policy_values(self) -> None:
        # Arrange
        module = self.load_module()
        contract = self.read_contract()
        contract["enums"]["blocker_kind"].remove("repair_item")

        # Act / Assert
        with self.assertRaises(module.VerificationError):
            module.validate_contract(contract)

    def test_contract_validation_rejects_missing_generated_artifact(self) -> None:
        # Arrange
        module = self.load_module()
        contract = self.read_contract()
        contract["generated_artifacts"].remove("blocker-register.json")

        # Act / Assert
        with self.assertRaises(module.VerificationError):
            module.validate_contract(contract)

    def test_unknown_signals_fail_closed_as_critical_decision_blockers(self) -> None:
        # Arrange
        module = self.load_module()
        signal = {
            "source_stream": "unknown",
            "status": "new-unmapped-status",
            "failure_reason": "unmapped evidence state",
        }

        # Act
        classification = module.classify_signal(signal)

        # Assert
        self.assertEqual(classification["row_problem_kind"], "unknown_unclassified")
        self.assertEqual(classification["blocker_kind"], "unresolved_decision_blocker")
        self.assertEqual(classification["severity"], "critical")
        self.assertEqual(classification["proof_eligibility"], "ineligible")

    def test_quick_default_rejections_are_non_final_placeholders(self) -> None:
        # Arrange
        module = self.load_module()
        signal = {
            "source_stream": "simulator",
            "finality_status": "quarantined-non-final",
            "failure_reason": "quick/default placeholder output is not final proof",
        }

        # Act
        classification = module.classify_signal(signal)

        # Assert
        self.assert_ineligible_policy(classification, "non_final_placeholder", "repair_item")

    def test_non_final_reason_taxonomy_remains_proof_ineligible(self) -> None:
        # Arrange
        module = self.load_module()
        cases = [
            ("smoke fixture from local workflow", "smoke_fixture"),
            ("local-only dry run output", "local_dry_run"),
            ("prose-only maintainer attestation", "prose_attestation"),
            ("upstream-row-only submission without source packet", "row_only_submission"),
            ("stale lifecycle id from older phase", "lifecycle_mismatch"),
        ]

        for reason, expected_problem_kind in cases:
            with self.subTest(reason=reason):
                signal = {
                    "source_stream": "release-signing",
                    "finality_status": "rejected-final",
                    "failure_reason": reason,
                }

                # Act
                classification = module.classify_signal(signal)

                # Assert
                self.assert_ineligible_policy(classification, expected_problem_kind, "repair_item")


if __name__ == "__main__":
    unittest.main()
