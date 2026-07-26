#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import phase34_decision_reconciliation_integration_test as phase34_integration


ROOT = Path(__file__).resolve().parents[2]
PHASE31_MANIFEST = "build/ci-evidence/phase31/final-intake-manifest.json"
PHASE33_DECISIONS = "build/ci-evidence/phase33-inputs/approved-decisions.json"
PHASE33_HANDOFF = "build/ci-evidence/phase33/downstream-handoff-manifest.json"
PHASE33_NORMALIZED = "build/ci-evidence/phase33/normalized-decision-records.json"
PHASE34_PACKET = "build/ci-evidence/phase34/final-readiness-packet.json"
PHASE34_DEMOTION = "build/ci-evidence/phase34/demotion-dry-run.json"
PHASE35_DECISION = "build/ci-evidence/phase35/cutover-decision.json"
PHASE35_ROUTE = "build/ci-evidence/phase35/next-milestone-route.json"
RUNTIME_FILES = [
    "tools/bazel/phase35_cutover_decision_artifact.py",
    "tools/bazel/phase38_cutover_workflow.py",
    "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json",
]
DEFAULT_PRODUCER_COMMANDS = [
    [
        "python3",
        "tools/bazel/phase31_final_evidence_intake.py",
        "--quick",
        "--output-dir",
        "build/ci-evidence/phase31",
    ],
    [
        "python3",
        "tools/bazel/phase26_release_signing_upstream_evidence.py",
        "--quick",
        "--output-dir",
        "build/ci-evidence/phase26",
    ],
    [
        "python3",
        "tools/bazel/phase27_retained_code_acceptance_decisions.py",
        "--quick",
        "--phase26-upstream-rows",
        "build/ci-evidence/phase26/upstream-result-row-table.json",
        "--output-dir",
        "build/ci-evidence/phase27",
    ],
    [
        "python3",
        "tools/bazel/phase28_final_readiness_packet.py",
        "--quick",
        "--phase26-upstream-rows",
        "build/ci-evidence/phase26/upstream-result-row-table.json",
        "--phase27-handoff",
        "build/ci-evidence/phase27/phase28-handoff-manifest.json",
        "--output-dir",
        "build/ci-evidence/phase28",
    ],
    [
        "python3",
        "tools/bazel/phase32_blocker_register_triage.py",
        "--quick",
        "--phase31-output-dir",
        "build/ci-evidence/phase31",
        "--phase27-output-dir",
        "build/ci-evidence/phase27",
        "--phase28-output-dir",
        "build/ci-evidence/phase28",
        "--output-dir",
        "build/ci-evidence/phase32",
    ],
    [
        "python3",
        "tools/bazel/phase33_maintainer_decision_inputs.py",
        "--quick",
        "--phase32-handoff",
        "build/ci-evidence/phase32/downstream-handoff-manifest.json",
        "--output-dir",
        "build/ci-evidence/phase33",
    ],
]


class Phase38ActualProducerWorkflowTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.phase34_fixture = (
            phase34_integration.Phase34DecisionReconciliationIntegrationTest
        )
        cls.phase34_fixture.setUpClass()
        cls.baseline_root = cls.phase34_fixture.baseline_root
        for relative_path in RUNTIME_FILES:
            source = ROOT / relative_path
            destination = cls.baseline_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.phase34_fixture.doClassCleanups()

    def clone_baseline(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name).resolve()
        shutil.copytree(self.baseline_root, root, dirs_exist_ok=True)
        return root

    @staticmethod
    def run_command(
        root: Path,
        arguments: list[str],
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            arguments,
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def run_required(
        self,
        root: Path,
        arguments: list[str],
    ) -> subprocess.CompletedProcess[str]:
        result = self.run_command(root, arguments)
        self.assertEqual(result.returncode, 0, result.stdout)
        return result

    def run_coordinator(
        self,
        root: Path,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result = self.run_command(
            root,
            [
                "python3",
                "tools/bazel/phase38_cutover_workflow.py",
                "--quick",
            ],
        )
        output_lines = [
            line for line in result.stdout.splitlines() if line.strip()
        ]
        self.assertTrue(output_lines, result.stdout)
        status = json.loads(output_lines[-1])
        self.assertIsInstance(status, dict)
        return result, status

    @staticmethod
    def read_json(root: Path, relative_path: str) -> dict[str, object]:
        return json.loads(
            (root / relative_path).read_text(encoding="utf-8")
        )

    @staticmethod
    def write_json(
        root: Path,
        relative_path: str,
        value: object,
    ) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def assert_blocked_repair(self, root: Path) -> None:
        decision = self.read_json(root, PHASE35_DECISION)
        route = self.read_json(root, PHASE35_ROUTE)
        self.assertEqual(decision["cutover_verdict"], "blocked")
        self.assertEqual(route["route"], "targeted-blocker-repair")
        self.assertEqual(route["source_verdict"], "blocked")
        self.assertTrue(route["requires_fresh_cutover_decision"])
        self.assertFalse(route["production_actions_authorized"])

    def seed_prior_approval(self, root: Path) -> None:
        result = self.run_command(
            root,
            [
                "python3",
                "tools/bazel/phase35_cutover_decision_artifact.py",
                "--quick",
                "--phase34-output-dir",
                "build/ci-evidence/phase34",
                "--output-dir",
                "build/ci-evidence/phase35",
            ],
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        decision = self.read_json(root, PHASE35_DECISION)
        route = self.read_json(root, PHASE35_ROUTE)
        self.assertEqual(decision["cutover_verdict"], "approved")
        self.assertEqual(route["route"], "production-cutover-planning")

    def replace_demotion_decision(
        self,
        root: Path,
        maybe_value: str | None,
    ) -> None:
        payload = self.read_json(root, PHASE33_DECISIONS)
        decisions = payload["decisions"]
        self.assertIsInstance(decisions, list)
        retained = [
            decision
            for decision in decisions
            if isinstance(decision, dict)
            and decision.get("decision_type") != "reference_demotion"
        ]
        if maybe_value is not None:
            demotion = next(
                copy.deepcopy(decision)
                for decision in decisions
                if isinstance(decision, dict)
                and decision.get("decision_type") == "reference_demotion"
            )
            demotion["decision_value"] = maybe_value
            retained.append(demotion)
        payload["decisions"] = retained
        self.write_json(root, PHASE33_DECISIONS, payload)
        result = self.phase34_fixture.run_phase33(root)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_default_quick_actual_producers_publish_blocked_repair(
        self,
    ) -> None:
        # Arrange
        root = self.clone_baseline()
        for command in DEFAULT_PRODUCER_COMMANDS:
            self.run_required(root, command)

        # Act
        result, status = self.run_coordinator(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(status["status"], 0)
        self.assertFalse(status["production_cutover_planning"])
        self.assertFalse(status["reference_demotion_authorized"])
        self.assert_blocked_repair(root)

    def test_complete_actual_producers_publish_approved_production_planning(
        self,
    ) -> None:
        # Arrange
        root = self.clone_baseline()

        # Act
        result, status = self.run_coordinator(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        decision = self.read_json(root, PHASE35_DECISION)
        route = self.read_json(root, PHASE35_ROUTE)
        self.assertEqual(decision["cutover_verdict"], "approved")
        self.assertEqual(route["route"], "production-cutover-planning")
        self.assertTrue(status["production_cutover_planning"])
        self.assertTrue(status["reference_demotion_authorized"])

    def test_one_exact_decision_defect_routes_named_fresh_repair(
        self,
    ) -> None:
        # Arrange
        root = self.clone_baseline()
        normalized = self.read_json(root, PHASE33_NORMALIZED)
        decisions = normalized["rows"]
        self.assertIsInstance(decisions, list)
        decision = next(
            row
            for row in decisions
            if isinstance(row, dict)
            and row.get("decision_type") == "retained_code"
        )
        mismatched_ref = (
            "build/ci-evidence/phase32/blocker-register.json"
            "#phase38-targeted-repair-defect"
        )
        decision["decision_targets"][0]["row_ref"] = mismatched_ref
        decision["source_row_refs"] = [mismatched_ref]
        self.write_json(root, PHASE33_NORMALIZED, normalized)

        # Act
        result, status = self.run_coordinator(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(status["production_cutover_planning"])
        self.assert_blocked_repair(root)
        route = self.read_json(root, PHASE35_ROUTE)
        scope = route["follow_up_scope"]
        self.assertIsInstance(scope, list)
        self.assertTrue(scope)
        self.assertTrue(
            all(
                isinstance(row, dict)
                and str(row.get("scope_id", "")).startswith("repair-")
                for row in scope
            )
        )

    def assert_invalid_source_replaces_prior(
        self,
        root: Path,
        expected_phase34_reason: str,
    ) -> None:
        result, status = self.run_coordinator(root)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertNotEqual(status["status"], 0)
        self.assertEqual(
            status["reason_category"],
            expected_phase34_reason,
        )
        phase34_packet = self.read_json(root, PHASE34_PACKET)
        self.assertEqual(phase34_packet["readiness_state"], "blocked")
        self.assertEqual(
            phase34_packet["cutover_verdict_state"],
            "blocked",
        )
        self.assertEqual(
            phase34_packet["production_cutover_route_state"],
            "blocked",
        )
        self.assert_blocked_repair(root)
        published = "\n".join(
            path.read_text(encoding="utf-8")
            for output_root in (
                root / "build/ci-evidence/phase34",
                root / "build/ci-evidence/phase35",
            )
            for path in output_root.rglob("*")
            if path.is_file()
        )
        self.assertNotIn('"cutover_verdict": "approved"', published)
        self.assertNotIn('"route": "production-cutover-planning"', published)

    def test_invalid_phase31_replaces_seeded_phase34_and_phase35_approval(
        self,
    ) -> None:
        # Arrange
        root = self.clone_baseline()
        self.seed_prior_approval(root)
        manifest = self.read_json(root, PHASE31_MANIFEST)
        manifest["phase_lifecycle_id"] = "31-stale"
        self.write_json(root, PHASE31_MANIFEST, manifest)

        # Act / Assert
        self.assert_invalid_source_replaces_prior(
            root,
            "phase31-input-invalid",
        )

    def test_invalid_phase33_replaces_seeded_phase34_and_phase35_approval(
        self,
    ) -> None:
        # Arrange
        root = self.clone_baseline()
        self.seed_prior_approval(root)
        handoff = self.read_json(root, PHASE33_HANDOFF)
        handoff["phase_lifecycle_id"] = "33-stale"
        self.write_json(root, PHASE33_HANDOFF, handoff)

        # Act / Assert
        self.assert_invalid_source_replaces_prior(
            root,
            "phase33-handoff-invalid",
        )

    def test_approved_cutover_with_missing_demotion_stays_closed(self) -> None:
        # Arrange
        root = self.clone_baseline()
        self.replace_demotion_decision(root, None)

        # Act
        result, status = self.run_coordinator(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(status["production_cutover_planning"])
        self.assertFalse(status["reference_demotion_authorized"])
        decision = self.read_json(root, PHASE35_DECISION)
        self.assertEqual(
            decision["demotion_decision_validation_state"],
            "missing",
        )

    def test_approved_cutover_with_rejected_demotion_stays_closed(self) -> None:
        # Arrange
        root = self.clone_baseline()
        self.replace_demotion_decision(root, "reject")

        # Act
        result, status = self.run_coordinator(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(status["production_cutover_planning"])
        self.assertFalse(status["reference_demotion_authorized"])
        decision = self.read_json(root, PHASE35_DECISION)
        self.assertEqual(decision["demotion_decision_state"], "reject")

    def test_valid_demotion_with_blocked_readiness_stays_closed(self) -> None:
        # Arrange
        root = self.clone_baseline()
        normalized = self.read_json(root, PHASE33_NORMALIZED)
        decisions = normalized["rows"]
        self.assertIsInstance(decisions, list)
        readiness = next(
            row
            for row in decisions
            if isinstance(row, dict)
            and row.get("decision_type") == "readiness"
        )
        readiness["decision_value"] = "block"
        self.write_json(root, PHASE33_NORMALIZED, normalized)

        # Act
        result, status = self.run_coordinator(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(status["production_cutover_planning"])
        self.assertFalse(status["reference_demotion_authorized"])
        dry_run = self.read_json(root, PHASE34_DEMOTION)
        self.assertEqual(dry_run["gate_state"], "blocked")


if __name__ == "__main__":
    unittest.main()
