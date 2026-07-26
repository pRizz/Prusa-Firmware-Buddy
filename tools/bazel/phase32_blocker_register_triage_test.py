#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase32_blocker_register_triage.py"
NORMALIZATION = ROOT / "tools/bazel/phase32_blocker_normalization.py"
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
PRODUCER_MODULES = [
    "tools/bazel/phase26_release_signing_upstream_evidence.py",
    "tools/bazel/phase27_retained_code_acceptance_decisions.py",
    "tools/bazel/phase28_final_readiness_packet.py",
    "tools/bazel/phase31_final_evidence_intake.py",
]
PRODUCER_INPUTS = [
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/foreign_code_inventory.json",
    "tools/bazel/manifests/unsafe_boundary_audit.json",
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json",
    "tools/bazel/manifests/phase18_cutover_review_contract.json",
    "tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json",
    "tools/bazel/manifests/phase20_release_environment_inputs.template.json",
]
REQUIRED_ROW_FIELDS = {
    "row_id",
    "source_domain",
    "producer_phase",
    "producer_artifact_kind",
    "source_row_kind",
    "source_subject_id",
    "decision_axis",
    "decision_subject_id",
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
        spec = importlib.util.spec_from_file_location(
            "phase32_blocker_register_triage", VERIFIER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_verifier(self,
                     args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", VERIFIER.as_posix(), *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def run_temp_verifier(self, root: Path,
                          args: list[str]) -> subprocess.CompletedProcess[str]:
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

    def write_json(self, root: Path, path: str, data: dict[str,
                                                           object]) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        return path

    def write_text(self, root: Path, path: str, text: str) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")
        return path

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for source in [
                VERIFIER,
                NORMALIZATION,
                CONTRACT,
                *[
                    ROOT / source_contract
                    for source_contract in SOURCE_CONTRACTS
                ],
        ]:
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
                "rejected_submissions_ref":
                "build/ci-evidence/phase31/rejected-submissions.json",
                "streams": ["simulator"],
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase31/rejected-submissions.json",
            {
                "generated_at_utc":
                "2026-07-03T03:17:26Z",
                "phase":
                "31-final-evidence-intake",
                "phase_lifecycle_id":
                "31-2026-07-03T02-04-07",
                "rejected_submissions": [{
                    "finality_status": "quarantined-non-final",
                    "reason":
                    "quick/default Phase 31 execution is a workflow smoke check and is quarantined as non-final evidence",
                    "receipt_generated_at_utc": "2026-07-03T03:17:26Z",
                    "requirement_ids": ["INTAKE-01"],
                    "stream": "simulator",
                    "submission_id": "phase31-simulator-rejected-fa00b2c0532a",
                    "submitter_identity_ref": "",
                }],
            },
        )
        self.write_json(
            root,
            receipt_ref,
            {
                "consumed_upstream_row_refs":
                [source_row_ref, missing_source_row_ref],
                "failure_reason":
                "",
                "finality_status":
                "accepted-final",
                "redaction_status":
                "passed",
                "requirement_ids": ["INTAKE-01"],
                "source_ref_status":
                "passed",
                "stream":
                "simulator",
                "submission_id":
                "phase31-simulator-accepted",
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
                "rows": [{
                    "owner": "runtime-maintainer",
                    "residual_risk":
                    "Scheduler behavior remains pending maintainer review.",
                    "residual_risk_state": "unreviewed",
                    "row_id": "packet-freertos-runtime",
                    "row_type": "retained_code_decision",
                }]
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase27/exception-decision-register.json",
            {
                "rows": [{
                    "exception": {
                        "affected_printer_or_release_surface":
                        "live network transfer",
                        "owner": "network-security-maintainer",
                        "status": "exception-requested",
                    },
                    "owner": "network-security-maintainer",
                    "residual_risk":
                    "Live network transfer evidence exception needs maintainer routing.",
                    "row_id": "final-live-network-transfer-evidence",
                    "row_type": "final_readiness_decision",
                }]
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase27/phase28-handoff-manifest.json",
            {
                "blocked_criteria": ["final-reference-demotion-allowed"],
                "demotion_authorization":
                "blocked",
                "phase27_may_authorize_demotion":
                False,
                "phase28_required_decision":
                "explicit-maintainer-reference-demotion-decision",
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase28/blocker-summary.json",
            {
                "blockers": [{
                    "criterion_id": "final-readiness-review",
                    "hard_failure_reasons": [],
                    "phase26_status": "pending",
                    "phase27_status": "pending",
                    "rationale":
                    "Maintainer final readiness decision is pending.",
                    "readiness_effect": "blocked",
                }],
                "final_readiness_status":
                "blocked",
                "reference_demotion_authorization":
                "blocked",
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase28/exception-residual-risk-summary.json",
            {
                "rows": [{
                    "criterion_id":
                    "final-residual-risk-review",
                    "exception_refs": [],
                    "exception_state":
                    "none",
                    "residual_risk":
                    "Pending Phase 27 maintainer decision input.",
                    "residual_risk_refs": [
                        "build/ci-evidence/phase27/residual-risk-register.json#final-residual-risk-review"
                    ],
                }]
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase28/reference-demotion-authorization-record.json",
            {
                "authorization_source": "no-phase28-demotion-decision-input",
                "evidence_refs": [],
                "rationale":
                "Reference demotion requires an explicit Phase 28 maintainer decision.",
                "real_maintainer_demotion_approval_supplied": False,
                "reference_demotion_authorization": "blocked",
            },
        )

    def assert_ineligible_policy(self, classification: dict[str, object],
                                 problem_kind: str, blocker_kind: str) -> None:
        self.assertEqual(classification["row_problem_kind"], problem_kind)
        self.assertEqual(classification["blocker_kind"], blocker_kind)
        self.assertEqual(classification["proof_eligibility"], "ineligible")
        self.assertIn(classification["severity"],
                      {"critical", "high", "medium"})
        self.assertIsInstance(classification["owner_ref"], str)
        self.assertIsInstance(classification["required_next_action"], str)
        self.assertTrue(classification["owner_ref"])
        self.assertTrue(classification["required_next_action"])

    def test_contract_only_accepts_complete_phase32_contract(self) -> None:
        # Arrange / Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("phase32_blocker_register_triage_contract",
                      result.stdout)

    def test_contract_validation_rejects_missing_required_policy_values(
            self) -> None:
        # Arrange
        module = self.load_module()
        contract = self.read_contract()
        contract["enums"]["blocker_kind"].remove("repair_item")

        # Act / Assert
        with self.assertRaises(module.VerificationError):
            module.validate_contract(contract)

    def test_contract_validation_rejects_missing_generated_artifact(
            self) -> None:
        # Arrange
        module = self.load_module()
        contract = self.read_contract()
        contract["generated_artifacts"].remove("blocker-register.json")

        # Act / Assert
        with self.assertRaises(module.VerificationError):
            module.validate_contract(contract)

    def test_contract_validation_rejects_fail_closed_policy_mismatches(
            self) -> None:
        # Arrange
        module = self.load_module()
        cases = [
            ("recognized_invalid_shape", "severity", "high"),
            ("recognized_invalid_shape", "proof_eligibility", "eligible"),
            ("unsupported_envelope_row_kind_or_status", "severity", "high"),
            ("unsupported_envelope_row_kind_or_status", "proof_eligibility",
             "eligible"),
        ]

        for policy_name, field, mismatched_value in cases:
            with self.subTest(policy_name=policy_name, field=field):
                contract = self.read_contract()
                contract["fail_closed_shape_policy"][policy_name][
                    field] = mismatched_value

                # Act / Assert
                with self.assertRaises(module.VerificationError):
                    module.validate_contract(contract)

    def test_unknown_signals_fail_closed_as_critical_decision_blockers(
            self) -> None:
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
        self.assertEqual(classification["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(classification["blocker_kind"],
                         "unresolved_decision_blocker")
        self.assertEqual(classification["severity"], "critical")
        self.assertEqual(classification["proof_eligibility"], "ineligible")

    def test_quick_default_rejections_are_non_final_placeholders(self) -> None:
        # Arrange
        module = self.load_module()
        signal = {
            "source_stream":
            "simulator",
            "finality_status":
            "quarantined-non-final",
            "failure_reason":
            "quick/default placeholder output is not final proof",
        }

        # Act
        classification = module.classify_signal(signal)

        # Assert
        self.assert_ineligible_policy(classification, "non_final_placeholder",
                                      "repair_item")

    def test_non_final_reason_taxonomy_remains_proof_ineligible(self) -> None:
        # Arrange
        module = self.load_module()
        cases = [
            ("smoke fixture from local workflow", "smoke_fixture"),
            ("local-only dry run output", "local_dry_run"),
            ("prose-only maintainer attestation", "prose_attestation"),
            ("upstream-row-only submission without source packet",
             "row_only_submission"),
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
                self.assert_ineligible_policy(classification,
                                              expected_problem_kind,
                                              "repair_item")

    def test_explicit_security_and_source_statuses_override_reason_taxonomy(
            self) -> None:
        # Arrange
        module = self.load_module()
        cases = [
            ({
                "redaction_status": "failed"
            }, "redaction_failed"),
            ({
                "redaction_status": "secret-tainted"
            }, "secret_tainted"),
            ({
                "source_ref_status": "unsafe-ref"
            }, "unsafe_ref"),
            ({
                "source_ref_status": "source-ref-failed"
            }, "source_ref_failed"),
            ({
                "source_lifecycle_status": "stale"
            }, "lifecycle_mismatch"),
        ]

        for status_fields, expected_problem_kind in cases:
            with self.subTest(expected_problem_kind=expected_problem_kind):
                signal = {
                    "source_stream": "simulator",
                    "failure_reason":
                    "quick default placeholder local-only workflow",
                    **status_fields,
                }

                # Act
                classification = module.classify_signal(signal)

                # Assert
                self.assertEqual(classification["row_problem_kind"],
                                 expected_problem_kind)
                self.assertEqual(classification["proof_eligibility"],
                                 "ineligible")

    def test_quick_writes_canonical_register_and_handoff_artifacts(
            self) -> None:
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
            self.assertTrue(
                (root / "build/ci-evidence/phase32" / path).exists(), path)
        register = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")
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
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        problem_kinds = {row["row_problem_kind"] for row in rows}
        self.assertIn("non_final_placeholder", problem_kinds)
        self.assertIn("failed", problem_kinds)
        self.assertIn("missing", problem_kinds)
        self.assertTrue(
            all(row["proof_eligibility"] == "ineligible" for row in rows))

    def test_phase31_accepted_receipt_keeps_stale_lifecycle_source_row(
            self) -> None:
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
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        stale_rows = [
            row for row in rows if row["source_ref"] == stale_source_row_ref
        ]
        self.assertEqual(len(stale_rows), 1)
        self.assertEqual(stale_rows[0]["row_problem_kind"],
                         "lifecycle_mismatch")

    def test_phase31_accepted_receipt_skips_clean_lifecycle_source_rows(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)
        receipt_ref = "build/ci-evidence/phase31/stream-receipts/simulator-final-intake-receipt.json"
        clean_source_refs = [
            "build/ci-evidence/phase23/current-lifecycle-source-row.json",
            "build/ci-evidence/phase23/not-required-lifecycle-source-row.json",
        ]
        receipt = self.read_json(root, receipt_ref)
        receipt["consumed_upstream_row_refs"].extend(clean_source_refs)
        self.write_json(root, receipt_ref, receipt)
        for source_ref, lifecycle_status in zip(clean_source_refs,
                                                ["current", "not-required"]):
            self.write_json(
                root,
                source_ref,
                {
                    "criterion_id": "final-simulator-evidence",
                    "evidence_family": "simulator",
                    "redaction_status": "passed",
                    "requirement_ids": ["EVID-01"],
                    "source_lifecycle_status": lifecycle_status,
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
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        emitted_refs = {row["source_ref"] for row in rows}
        self.assertTrue(
            all(source_ref not in emitted_refs
                for source_ref in clean_source_refs))

    def test_phase27_and_phase28_handoff_rows_are_included_without_approval_semantics(
            self) -> None:
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
        register_text = (
            root /
            "build/ci-evidence/phase32/blocker-register.json").read_text(
                encoding="utf-8")
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        self.assertIn("retained-code", {row["source_stream"] for row in rows})
        self.assertIn("readiness", {row["source_stream"] for row in rows})
        self.assertNotIn("demotion_allowed", register_text)
        self.assertNotIn("final_readiness_status", register_text)
        self.assertNotIn("cutover verdict approved", register_text.casefold())

    def test_phase27_final_readiness_exception_keeps_original_affected_gate(
            self) -> None:
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
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        exception_rows = [
            row for row in rows if row["source_ref"] == expected_ref
        ]
        self.assertEqual(len(exception_rows), 1)
        self.assertEqual(exception_rows[0]["source_stream"], "readiness")
        self.assertEqual(exception_rows[0]["affected_gate"],
                         "final-live-network-transfer-evidence")

    def test_phase28_known_pending_statuses_are_classified_as_missing(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_quick_fixture(root)
        blocker_summary_path = "build/ci-evidence/phase28/blocker-summary.json"
        blocker_summary = self.read_json(root, blocker_summary_path)
        blocker_summary["blockers"] = [
            {
                "criterion_id": f"readiness-{status}",
                "phase27_status": status,
                "phase26_status": "passed",
                "readiness_effect": "blocked",
            } for status in
            ["pending-ci-input", "pending-simulator-input", "not-required"]
        ]
        self.write_json(root, blocker_summary_path, blocker_summary)

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
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        readiness_rows = [
            row for row in rows if row["source_ref"].startswith(
                f"{blocker_summary_path}#readiness-")
        ]
        self.assertEqual(len(readiness_rows), 3)
        self.assertEqual({row["row_problem_kind"]
                          for row in readiness_rows}, {"missing"})

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
        register_rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        register_ids = {row["row_id"] for row in register_rows}
        for path in [
                "decision-impact-index.json",
                "exception-request-register.json",
                "residual-risk-request-register.json",
        ]:
            rows = self.read_json(root,
                                  f"build/ci-evidence/phase32/{path}")["rows"]
            self.assertTrue(rows, path)
            self.assertTrue(all(row["row_id"] in register_ids for row in rows),
                            path)

    def test_security_only_rejects_secret_and_approval_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_text(root, "build/ci-evidence/phase32/leak.json",
                        '{"demotion_allowed": true}\n')

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


class Phase32ProducerShapeTest(unittest.TestCase):

    def read_json(self, root: Path, path: str) -> dict[str, object]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    def write_json(self, root: Path, path: str, data: dict[str,
                                                           object]) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")

    def load_producer(self, root: Path, module_name: str) -> ModuleType:
        module_path = root / f"tools/bazel/{module_name}.py"
        spec = importlib.util.spec_from_file_location(
            f"phase32_producer_fixture_{module_name}", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def make_producer_root(
            self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name).resolve()
        relative_paths = {
            VERIFIER.relative_to(ROOT),
            NORMALIZATION.relative_to(ROOT),
            CONTRACT.relative_to(ROOT),
            *[Path(path) for path in SOURCE_CONTRACTS],
            *[Path(path) for path in PRODUCER_MODULES],
            *[Path(path) for path in PRODUCER_INPUTS],
        }
        for relative_path in relative_paths:
            destination = root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative_path, destination)
        return temp_dir, root

    def phase26_all_passed_output(self, root: Path,
                                  phase26: ModuleType) -> str:
        phase26.check_contract(root)
        phase18 = self.read_json(
            root, "tools/bazel/manifests/phase18_cutover_review_contract.json")
        generated_at = "2026-07-26T01:00:00Z"
        consumed_rows = {}
        for requirement in phase26.phase18_upstream_requirements(phase18):
            criterion_id = str(requirement["criterion_id"])
            consumed_rows[criterion_id] = {
                "artifact_refs":
                [f"external://phase26/artifacts/{criterion_id}.json"],
                "criterion_id":
                criterion_id,
                "evidence_family":
                requirement["evidence_family"],
                "evidence_refs":
                [f"external://phase26/evidence/{criterion_id}.json"],
                "exception_status":
                "none",
                "failure_reason":
                "none",
                "generated_at_utc":
                generated_at,
                "maintainer_state":
                "accepted",
                "owning_phase":
                requirement["source_phase"],
                "redaction_status":
                "passed",
                "requirement_ids":
                list(requirement["requirement_ids"]),
                "source_lifecycle_id":
                requirement["source_lifecycle_id"],
                "source_lifecycle_status":
                "current",
                "source_ref_status":
                "passed",
                "source_requirement_ids":
                list(requirement["requirement_ids"]),
                "status":
                "passed",
            }
        output_dir = Path("build/ci-evidence/phase26")
        upstream_rows = phase26.build_upstream_rows(
            root,
            output_dir,
            {},
            True,
            generated_at,
            consumed_rows,
        )
        table_path = output_dir / "upstream-result-row-table.json"
        phase26.write_json(root, table_path, {"rows": upstream_rows})
        phase26.write_json(
            root,
            output_dir / "release-upstream-run-manifest.json",
            {
                "artifact_name": "phase26-release-signing-upstream-evidence",
                "generated_at_utc": generated_at,
                "output_root": output_dir.as_posix(),
                "phase": phase26.PHASE,
                "phase_lifecycle_id": phase26.PHASE_LIFECYCLE_ID,
                "real_release_evidence_supplied": True,
                "release_status": "passed",
                "upstream_criteria_count": len(upstream_rows),
            },
        )
        return table_path.as_posix()

    def phase31_accept_release_output(self, root: Path,
                                      phase31: ModuleType) -> None:
        contract = self.read_json(
            root,
            "tools/bazel/manifests/phase31_final_evidence_intake_contract.json"
        )
        adapter = phase31.contract_adapters(contract)["release-signing"]
        receipt, _ = phase31.validate_stream_output(
            root,
            adapter,
            Path("build/ci-evidence/phase26"),
            "external://phase31/submitters/release-maintainer",
            ["producer-fixture", "phase26"],
            "a" * 64,
        )
        output_dir = phase31.reset_output_root(
            root, Path("build/ci-evidence/phase31"))
        phase31.write_phase31_outputs(root, output_dir, [receipt], [])

    def phase27_maintainer_input(self, root: Path,
                                 phase27: ModuleType) -> dict[str, object]:
        checked = phase27.check_contract(root)
        phase18 = checked["phase18_contract"]
        contract = checked["contract"]
        maintainer_input = phase27.maintainer_input_template(phase18, contract)
        retained_rows = maintainer_input["retained_code_decisions"]
        for index, row in enumerate(retained_rows):
            row["decision"] = "exception" if index == 0 else "approve"
            row["approver"] = "phase32-producer-fixture-maintainer"
            row["decision_timestamp"] = "2026-07-26T01:05:00Z"
            row["rationale"] = "Producer-shaped retained-code review completed."
            row["residual_risk"] = "Bounded residual risk remains documented."
            row["redaction_summary"] = "Reference-only evidence; scan passed."
            if index != 0:
                continue
            exception = row["exception"]
            exception.update({
                "scope": row["packet_id"],
                "rationale": "A bounded retained-code exception is required.",
                "approver": row["approver"],
                "approver_role": row["approver_role"],
                "affected_printer_or_release_surface":
                "retained runtime compatibility boundary",
                "mitigation_or_follow_up":
                "Review the retained boundary at the next release gate.",
                "expiry_or_review_trigger": "Next release-candidate review",
                "evidence_refs": list(row["evidence_refs"]),
                "residual_risk": row["residual_risk"],
                "owner": row["approver"],
            })

        for row in maintainer_input["final_readiness_decisions"]:
            criterion_id = str(row["criterion_id"])
            is_blocked = criterion_id in {
                "final-maintainer-decision",
                "final-reference-demotion-allowed",
            }
            row["decision"] = "reject" if is_blocked else "approve"
            row["status"] = "blocked" if is_blocked else "passed"
            row["approver"] = "phase32-producer-fixture-maintainer"
            row["approver_role"] = self.final_role_for_criterion(criterion_id)
            row["decision_timestamp"] = "2026-07-26T01:05:00Z"
            row["rationale"] = "Producer-shaped final criterion review completed."
            row["evidence_refs"] = [
                f"external://phase26/evidence/{criterion_id}.json"
            ]
            row["residual_risk"] = "Bounded residual risk remains documented."
            row["redaction_summary"] = "Reference-only evidence; scan passed."
        return maintainer_input

    def final_role_for_criterion(self, criterion_id: str) -> str:
        if criterion_id == "final-hardware-safety-media-evidence":
            return "safety-maintainer"
        if criterion_id == "final-live-network-transfer-evidence":
            return "network-security-maintainer"
        if criterion_id in {
                "final-release-artifact-signing-evidence",
                "final-reference-demotion-allowed",
        }:
            return "release-maintainer"
        return "cutover-maintainer"

    def generate_producer_fixture(
        self, ) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir, root = self.make_producer_root()
        phase26 = self.load_producer(
            root, "phase26_release_signing_upstream_evidence")
        phase27 = self.load_producer(
            root, "phase27_retained_code_acceptance_decisions")
        phase28 = self.load_producer(root, "phase28_final_readiness_packet")
        phase31 = self.load_producer(root, "phase31_final_evidence_intake")

        table_path = self.phase26_all_passed_output(root, phase26)
        self.phase31_accept_release_output(root, phase31)

        maintainer_input = self.phase27_maintainer_input(root, phase27)
        maintainer_input_path = "build/ci-evidence/phase27-maintainer-input.json"
        phase27.write_json(root, Path(maintainer_input_path), maintainer_input)
        phase27.write_phase27_outputs(
            root,
            Path("build/ci-evidence/phase27"),
            maintainer_input_path,
            table_path,
        )

        phase26_path, phase26_rows = phase28.load_phase26_rows(
            root, table_path)
        phase27_path, handoff, phase27_bundle = phase28.load_phase27_bundle(
            root, "build/ci-evidence/phase27/phase28-handoff-manifest.json")
        phase28.write_phase28_outputs(
            root,
            phase28.check_contract(root),
            phase26_path,
            phase26_rows,
            phase27_path,
            handoff,
            phase27_bundle,
            None,
            "build/ci-evidence/phase28",
        )
        return temp_dir, root

    def run_phase32(self, root: Path) -> subprocess.CompletedProcess[str]:
        verifier = root / "tools/bazel/phase32_blocker_register_triage.py"
        return subprocess.run(
            [
                "python3",
                verifier.as_posix(),
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
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def test_all_passed_phase26_table_crosses_phase31_without_release_blocker(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        phase26_rows = self.read_json(
            root,
            "build/ci-evidence/phase26/upstream-result-row-table.json")["rows"]
        receipt = self.read_json(
            root,
            "build/ci-evidence/phase31/stream-receipts/release-signing-final-intake-receipt.json"
        )
        register_rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        self.assertTrue(all(row["status"] == "passed" for row in phase26_rows))
        self.assertEqual(receipt["finality_status"], "accepted-final")
        self.assertEqual(
            receipt["consumed_upstream_row_refs"],
            ["build/ci-evidence/phase26/upstream-result-row-table.json"],
        )
        self.assertFalse([
            row for row in register_rows
            if row["source_domain"] == "release_signing"
        ])

    def test_release_receipt_rejects_same_basename_outside_phase26_path(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        expected_table_path = (
            "build/ci-evidence/phase26/upstream-result-row-table.json")
        attacker_table_path = (
            "arbitrary/attacker/upstream-result-row-table.json")
        self.write_json(
            root,
            attacker_table_path,
            self.read_json(root, expected_table_path),
        )
        receipt_path = (
            "build/ci-evidence/phase31/stream-receipts/"
            "release-signing-final-intake-receipt.json")
        receipt = self.read_json(root, receipt_path)
        receipt["consumed_upstream_row_refs"] = [attacker_table_path]
        receipt["validator_output_refs"] = [
            attacker_table_path
            if ref == expected_table_path else ref
            for ref in receipt["validator_output_refs"]
        ]
        self.write_json(root, receipt_path, receipt)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        release_rows = [
            row for row in rows
            if row["source_domain"] == "release_signing"
        ]
        self.assertEqual(len(release_rows), 1)
        self.assertEqual(release_rows[0]["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(release_rows[0]["severity"], "critical")

    def test_malformed_phase26_table_emits_critical_blocker(self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        table_path = (
            "build/ci-evidence/phase26/upstream-result-row-table.json")
        self.write_json(root, table_path, {"rows": []})

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        malformed_rows = [
            row for row in rows if row["source_domain"] == "release_signing"
            and row["row_problem_kind"] == "malformed"
        ]
        self.assertEqual(len(malformed_rows), 1)
        self.assertEqual(malformed_rows[0]["severity"], "critical")

    def test_phase27_unknown_demotion_authorization_is_critical_blocker(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        handoff_path = (
            "build/ci-evidence/phase27/phase28-handoff-manifest.json")
        handoff = self.read_json(root, handoff_path)
        handoff["demotion_authorization"] = "unexpected-new-state"
        self.write_json(root, handoff_path, handoff)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        demotion_rows = [
            row for row in rows if row["producer_artifact_kind"]
            == "phase27_phase28_handoff_manifest"
        ]
        self.assertEqual(len(demotion_rows), 1)
        self.assertEqual(demotion_rows[0]["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(demotion_rows[0]["severity"], "critical")

    def test_phase28_unknown_demotion_authorization_is_critical_blocker(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)
        demotion_path = (
            "build/ci-evidence/phase28/"
            "reference-demotion-authorization-record.json")
        demotion = self.read_json(root, demotion_path)
        demotion["reference_demotion_authorization"] = (
            "unexpected-new-state")
        self.write_json(root, demotion_path, demotion)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        demotion_rows = [
            row for row in rows if row["producer_artifact_kind"]
            == "phase28_reference_demotion_authorization_record"
        ]
        self.assertEqual(len(demotion_rows), 1)
        self.assertEqual(demotion_rows[0]["row_problem_kind"],
                         "unknown_unclassified")
        self.assertEqual(demotion_rows[0]["severity"], "critical")

    def test_phase27_and_phase28_producers_preserve_all_decision_identities(
            self) -> None:
        # Arrange
        temp_dir, root = self.generate_producer_fixture()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_phase32(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        register_path = "build/ci-evidence/phase32/blocker-register.json"
        rows = self.read_json(root, register_path)["rows"]
        decision_rows = [
            row for row in rows
            if row["producer_phase"] in {"phase27", "phase28"}
        ]
        self.assertEqual(
            {row["decision_axis"]
             for row in decision_rows},
            {
                "retained_code",
                "residual_risk",
                "exception",
                "readiness",
                "demotion",
            },
        )
        self.assertTrue(
            any(row["decision_axis"] == "retained_code"
                and row["source_subject_id"].startswith("packet-")
                for row in decision_rows))
        self.assertTrue(
            any(row["decision_axis"] == "exception"
                and row["source_subject_id"].startswith("packet-")
                for row in decision_rows))
        self.assertTrue(
            any(row["decision_axis"] == "readiness"
                and row["source_subject_id"] == "final-maintainer-decision"
                for row in decision_rows))
        demotion_rows = [
            row for row in decision_rows if row["decision_axis"] == "demotion"
        ]
        self.assertTrue(demotion_rows)
        self.assertEqual(
            {row["decision_subject_id"]
             for row in demotion_rows},
            {"final-reference-demotion-allowed"},
        )
        register_text = (root / register_path).read_text(encoding="utf-8")
        self.assertNotIn("demotion_allowed", register_text)
        self.assertNotIn("final readiness approved", register_text.casefold())
        self.assertTrue(
            all(row["proof_eligibility"] == "ineligible"
                for row in decision_rows))

        before_ids = {
            (row["producer_artifact_kind"], row["source_subject_id"]):
            row["row_id"]
            for row in decision_rows if row["decision_axis"] == "retained_code"
        }
        residual_path = "build/ci-evidence/phase27/residual-risk-register.json"
        residual_register = self.read_json(root, residual_path)
        residual_register["rows"][0]["owner"] = "changed-owner"
        residual_register["rows"][0][
            "residual_risk"] = "Changed mutable risk wording."
        self.write_json(root, residual_path, residual_register)
        rerun = self.run_phase32(root)
        self.assertEqual(rerun.returncode, 0, rerun.stdout)
        rerun_rows = self.read_json(root, register_path)["rows"]
        after_ids = {
            (row["producer_artifact_kind"], row["source_subject_id"]):
            row["row_id"]
            for row in rerun_rows
            if row["producer_phase"] in {"phase27", "phase28"}
            and row["decision_axis"] == "retained_code"
        }
        self.assertEqual(before_ids, after_ids)


if __name__ == "__main__":
    unittest.main()
