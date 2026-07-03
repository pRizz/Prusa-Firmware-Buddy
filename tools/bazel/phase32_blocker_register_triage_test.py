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
VERIFIER = ROOT / "tools/bazel/phase32_blocker_register_triage.py"
CONTRACT = ROOT / "tools/bazel/manifests/phase32_blocker_register_triage_contract.json"
SOURCE_CONTRACTS = [
    "tools/bazel/manifests/phase31_final_evidence_intake_contract.json",
    "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json",
    "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
    "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json",
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json",
    "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json",
    "tools/bazel/manifests/phase28_final_readiness_packet_contract.json",
]
REQUIRED_ROW_FIELDS = {
    "row_id",
    "source_stream",
    "source_ref",
    "requirement_ids",
    "affected_gate",
    "row_problem_kind",
    "blocker_kind",
    "severity",
    "owner_ref",
    "required_next_action",
    "decision_impact",
    "proof_eligibility",
    "evidence_refs",
}


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

    def run_temp_verifier(self, root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
        verifier = root / "tools/bazel/phase32_blocker_register_triage.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def read_contract(self) -> dict[str, object]:
        return json.loads(CONTRACT.read_text(encoding="utf-8"))

    def read_json(self, root: Path, path: str) -> dict[str, object]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    def write_json(self, root: Path, path: str, data: dict[str, object]) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def write_text(self, root: Path, path: str, text: str) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")
        return path

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for source in [VERIFIER, CONTRACT, *[ROOT / source_contract for source_contract in SOURCE_CONTRACTS]]:
            destination = root / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return temp_dir, root

    def write_phase32_quick_fixture(self, root: Path) -> None:
        receipt_ref = "build/ci-evidence/phase31/stream-receipts/simulator-final-intake-receipt.json"
        source_row_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        missing_source_row_ref = "build/ci-evidence/phase23/missing-row.json"
        self.write_json(
            root,
            "build/ci-evidence/phase31/final-intake-manifest.json",
            {
                "accepted_count": 1,
                "artifact_name": "phase31-final-evidence-intake",
                "finality_status": "quarantined-non-final",
                "generated_at_utc": "2026-07-03T03:17:26Z",
                "output_root": "build/ci-evidence/phase31",
                "phase": "31-final-evidence-intake",
                "phase_lifecycle_id": "31-2026-07-03T02-04-07",
                "receipt_refs": [receipt_ref],
                "rejected_count": 1,
                "rejected_submissions_ref": "build/ci-evidence/phase31/rejected-submissions.json",
                "streams": ["simulator"],
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase31/rejected-submissions.json",
            {
                "generated_at_utc": "2026-07-03T03:17:26Z",
                "phase": "31-final-evidence-intake",
                "phase_lifecycle_id": "31-2026-07-03T02-04-07",
                "rejected_submissions": [
                    {
                        "finality_status": "quarantined-non-final",
                        "reason": "quick/default Phase 31 execution is a workflow smoke check and is quarantined as non-final evidence",
                        "receipt_generated_at_utc": "2026-07-03T03:17:26Z",
                        "requirement_ids": ["INTAKE-01"],
                        "stream": "simulator",
                        "submission_id": "phase31-simulator-rejected-fa00b2c0532a",
                        "submitter_identity_ref": "",
                    }
                ],
            },
        )
        self.write_json(
            root,
            receipt_ref,
            {
                "consumed_upstream_row_refs": [source_row_ref, missing_source_row_ref],
                "failure_reason": "",
                "finality_status": "accepted-final",
                "redaction_status": "passed",
                "requirement_ids": ["INTAKE-01"],
                "source_ref_status": "passed",
                "stream": "simulator",
                "submission_id": "phase31-simulator-accepted",
                "validator_output_refs": [source_row_ref],
            },
        )
        self.write_json(
            root,
            source_row_ref,
            {
                "artifact_refs": ["external://phase23/simulator/failure.json"],
                "criterion_id": "final-simulator-evidence",
                "evidence_family": "simulator",
                "failure_reason": "simulator startup failed",
                "redaction_status": "passed",
                "requirement_ids": ["EVID-01"],
                "source_ref_status": "passed",
                "status": "failed",
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase27/residual-risk-register.json",
            {
                "rows": [
                    {
                        "owner": "runtime-maintainer",
                        "residual_risk": "Scheduler behavior remains pending maintainer review.",
                        "residual_risk_state": "unreviewed",
                        "row_id": "packet-freertos-runtime",
                        "row_type": "retained_code_decision",
                    }
                ]
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase27/exception-decision-register.json",
            {
                "rows": [
                    {
                        "exception": {
                            "affected_printer_or_release_surface": "live network transfer",
                            "owner": "network-security-maintainer",
                            "status": "exception-requested",
                        },
                        "owner": "network-security-maintainer",
                        "residual_risk": "Live network transfer evidence exception needs maintainer routing.",
                        "row_id": "final-live-network-transfer-evidence",
                        "row_type": "final_readiness_decision",
                    }
                ]
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase27/phase28-handoff-manifest.json",
            {
                "blocked_criteria": ["final-reference-demotion-allowed"],
                "demotion_authorization": "blocked",
                "phase27_may_authorize_demotion": False,
                "phase28_required_decision": "explicit-maintainer-reference-demotion-decision",
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase28/blocker-summary.json",
            {
                "blockers": [
                    {
                        "criterion_id": "final-readiness-review",
                        "hard_failure_reasons": [],
                        "phase26_status": "pending",
                        "phase27_status": "pending",
                        "rationale": "Maintainer final readiness decision is pending.",
                        "readiness_effect": "blocked",
                    }
                ],
                "final_readiness_status": "blocked",
                "reference_demotion_authorization": "blocked",
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase28/exception-residual-risk-summary.json",
            {
                "rows": [
                    {
                        "criterion_id": "final-residual-risk-review",
                        "exception_refs": [],
                        "exception_state": "none",
                        "residual_risk": "Pending Phase 27 maintainer decision input.",
                        "residual_risk_refs": ["build/ci-evidence/phase27/residual-risk-register.json#final-residual-risk-review"],
                    }
                ]
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase28/reference-demotion-authorization-record.json",
            {
                "authorization_source": "no-phase28-demotion-decision-input",
                "evidence_refs": [],
                "rationale": "Reference demotion requires an explicit Phase 28 maintainer decision.",
                "real_maintainer_demotion_approval_supplied": False,
                "reference_demotion_authorization": "blocked",
            },
        )

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

    def test_quick_writes_canonical_register_and_handoff_artifacts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)

        # Act
        result = self.run_temp_verifier(
            root,
            [
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
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        for path in [
            "blocker-register.json",
            "decision-impact-index.json",
            "exception-request-register.json",
            "residual-risk-request-register.json",
            "downstream-handoff-manifest.json",
            "redacted-blocker-register-report.md",
            "contract-snapshots/phase32_blocker_register_triage_contract.json",
            "contract-snapshots/phase31_final_evidence_intake_contract.json",
            "contract-snapshots/phase23_simulator_evidence_execution_contract.json",
            "contract-snapshots/phase24_hardware_media_safety_evidence_execution_contract.json",
            "contract-snapshots/phase25_live_service_evidence_execution_contract.json",
            "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json",
            "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
            "contract-snapshots/phase28_final_readiness_packet_contract.json",
        ]:
            self.assertTrue((root / "build/ci-evidence/phase32" / path).exists(), path)
        register = self.read_json(root, "build/ci-evidence/phase32/blocker-register.json")
        rows = register["rows"]
        self.assertTrue(rows)
        self.assertTrue(all(REQUIRED_ROW_FIELDS <= set(row) for row in rows))

    def test_phase31_receipts_and_rejections_remain_fail_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)

        # Act
        result = self.run_temp_verifier(
            root,
            [
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
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        problem_kinds = {row["row_problem_kind"] for row in rows}
        self.assertIn("non_final_placeholder", problem_kinds)
        self.assertIn("failed", problem_kinds)
        self.assertIn("missing", problem_kinds)
        self.assertTrue(all(row["proof_eligibility"] == "ineligible" for row in rows))

    def test_phase31_accepted_receipt_keeps_stale_lifecycle_source_row(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)
        receipt_ref = "build/ci-evidence/phase31/stream-receipts/simulator-final-intake-receipt.json"
        stale_source_row_ref = "build/ci-evidence/phase23/stale-lifecycle-source-row.json"
        receipt = self.read_json(root, receipt_ref)
        receipt["consumed_upstream_row_refs"].append(stale_source_row_ref)
        self.write_json(root, receipt_ref, receipt)
        self.write_json(
            root,
            stale_source_row_ref,
            {
                "criterion_id": "final-simulator-evidence",
                "evidence_family": "simulator",
                "redaction_status": "passed",
                "requirement_ids": ["EVID-01"],
                "source_lifecycle_status": "stale",
                "source_ref_status": "passed",
                "status": "passed",
            },
        )

        # Act
        result = self.run_temp_verifier(
            root,
            [
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
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        stale_rows = [row for row in rows if row["source_ref"] == stale_source_row_ref]
        self.assertEqual(len(stale_rows), 1)
        self.assertEqual(stale_rows[0]["row_problem_kind"], "lifecycle_mismatch")

    def test_phase27_and_phase28_handoff_rows_are_included_without_approval_semantics(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)

        # Act
        result = self.run_temp_verifier(
            root,
            [
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
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        register_text = (root / "build/ci-evidence/phase32/blocker-register.json").read_text(encoding="utf-8")
        rows = self.read_json(root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        self.assertIn("retained-code", {row["source_stream"] for row in rows})
        self.assertIn("readiness", {row["source_stream"] for row in rows})
        self.assertNotIn("demotion_allowed", register_text)
        self.assertNotIn("final_readiness_status", register_text)
        self.assertNotIn("cutover verdict approved", register_text.casefold())

    def test_phase27_final_readiness_exception_keeps_original_affected_gate(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)
        expected_ref = "build/ci-evidence/phase27/exception-decision-register.json#final-live-network-transfer-evidence"

        # Act
        result = self.run_temp_verifier(
            root,
            [
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
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        exception_rows = [row for row in rows if row["source_ref"] == expected_ref]
        self.assertEqual(len(exception_rows), 1)
        self.assertEqual(exception_rows[0]["source_stream"], "readiness")
        self.assertEqual(exception_rows[0]["affected_gate"], "final-live-network-transfer-evidence")

    def test_derived_views_reference_canonical_row_ids(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)

        # Act
        result = self.run_temp_verifier(
            root,
            [
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
        )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        register_rows = self.read_json(root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        register_ids = {row["row_id"] for row in register_rows}
        for path in [
            "decision-impact-index.json",
            "exception-request-register.json",
            "residual-risk-request-register.json",
        ]:
            rows = self.read_json(root, f"build/ci-evidence/phase32/{path}")["rows"]
            self.assertTrue(rows, path)
            self.assertTrue(all(row["row_id"] in register_ids for row in rows), path)

    def test_security_only_rejects_secret_and_approval_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_text(root, "build/ci-evidence/phase32/leak.json", '{"demotion_allowed": true}\n')

        # Act
        result = self.run_temp_verifier(
            root,
            [
                "--security-only",
                "--output-dir",
                "build/ci-evidence/phase32",
            ],
        )

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("demotion_allowed", result.stdout)


if __name__ == "__main__":
    unittest.main()
