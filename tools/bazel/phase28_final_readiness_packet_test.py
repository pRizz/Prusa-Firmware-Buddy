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
PHASE18_CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
PHASE26_CONTRACT = "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
PHASE27_CONTRACT = "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
PHASE26_ROWS = "build/ci-evidence/phase26/upstream-result-row-table.json"
PHASE27_HANDOFF = "build/ci-evidence/phase27/phase28-handoff-manifest.json"
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase28"
WIRING_FILES = [
    "BUILD.bazel",
    "tools/bazel/BUILD.bazel",
    "tools/bazel/rust_workflow.sh",
    "justfile",
]
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


class Phase28FinalReadinessPacketTest(unittest.TestCase):
    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for path in [
            VERIFIER,
            ROOT / CONTRACT,
            ROOT / PHASE18_CONTRACT,
            ROOT / PHASE26_CONTRACT,
            ROOT / PHASE27_CONTRACT,
        ]:
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

    def write_json(self, root: Path, path: str, data: dict[str, object]) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def write_text(self, root: Path, path: str, text: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_wiring_files(self, root: Path) -> None:
        for path in WIRING_FILES:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, destination)

    def phase18_requirements(self, root: Path) -> dict[str, dict[str, object]]:
        contract = self.read_json(root, PHASE18_CONTRACT)
        return {row["criterion_id"]: row for row in contract["upstream_result_requirements"]}

    def phase26_rows(self, root: Path) -> list[dict[str, object]]:
        requirements = self.phase18_requirements(root)
        rows = []
        for criterion_id in REQUIRED_CRITERIA:
            requirement = requirements[criterion_id]
            status = "blocked" if criterion_id == "final-reference-demotion-allowed" else "passed"
            failure_reason = (
                "Reference demotion requires explicit Phase 28 maintainer input."
                if criterion_id == "final-reference-demotion-allowed"
                else "none"
            )
            rows.append(
                {
                    "criterion_id": criterion_id,
                    "evidence_family": requirement["evidence_family"],
                    "requirement_ids": requirement["requirement_ids"],
                    "source_requirement_ids": ["REV-01"],
                    "owning_phase": requirement["source_phase"],
                    "source_lifecycle_id": requirement["source_lifecycle_id"],
                    "source_lifecycle_status": "current",
                    "evidence_refs": requirement["required_manifest_refs"],
                    "artifact_refs": [
                        "build/ci-evidence/phase26/upstream-result-row-table.json",
                        "build/ci-evidence/phase26/upstream-result-manifest.json",
                    ],
                    "status": status,
                    "failure_reason": failure_reason,
                    "redaction_status": "passed",
                    "source_ref_status": "passed",
                    "exception_status": "none",
                    "maintainer_state": "blocked" if status == "blocked" else "not-required",
                    "generated_at_utc": "2026-06-25T04:00:00Z",
                }
            )
        return rows

    def consumed_phase26_rows(self, root: Path) -> list[dict[str, object]]:
        rows = self.phase26_rows(root)
        consumed_rows = {
            "final-simulator-evidence": {
                "artifact_refs": [
                    "external://phase23/simulator/startup-log.json",
                    "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                ],
                "evidence_refs": [
                    "build/ci-evidence/phase23/simulator-result-manifest.json",
                    "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                ],
                "requirement_ids": ["EVID-01", "ACPT-01"],
            },
            "final-hardware-safety-media-evidence": {
                "artifact_refs": [
                    "external://phase24/hardware/safety-report.json",
                    "build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json",
                ],
                "evidence_refs": [
                    "build/ci-evidence/phase24/hardware-media-safety-result-manifest.json",
                    "build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json",
                ],
                "requirement_ids": ["EVID-02", "ACPT-01"],
            },
            "final-live-network-transfer-evidence": {
                "artifact_refs": [
                    "external://phase25/live-service/connect-report.json",
                    "build/ci-evidence/phase25/upstream-live-service-result-row.json",
                ],
                "evidence_refs": [
                    "build/ci-evidence/phase25/live-service-result-manifest.json",
                    "build/ci-evidence/phase25/upstream-live-service-result-row.json",
                ],
                "requirement_ids": ["EVID-03", "ACPT-01"],
            },
        }
        for row in rows:
            maybe_consumed = consumed_rows.get(str(row["criterion_id"]))
            if maybe_consumed is not None:
                row.update(maybe_consumed)
        return rows

    def exception_metadata(self, criterion_id: str = "final-ci-evidence") -> dict[str, object]:
        return {
            "scope": f"phase28-test-{criterion_id}",
            "owner": "phase28-test-maintainer",
            "approver": "phase28-test-maintainer",
            "approver_role": "release-maintainer",
            "rationale": "A documented temporary exception covers this Phase 28 test row.",
            "affected_printer_or_release_surface": "supported-release-surface",
            "evidence_refs": [f"build/ci-evidence/phase27/exception-decision-register.json#{criterion_id}"],
            "residual_risk": "Exception residual risk is explicitly documented.",
            "mitigation_or_follow_up": "Review before final release signoff.",
            "expiry_or_review_trigger": "before-reference-demotion-decision",
        }

    def phase27_final_rows(self, phase26_rows: list[dict[str, object]]) -> list[dict[str, object]]:
        rows = []
        for row in phase26_rows:
            criterion_id = str(row["criterion_id"])
            status = "blocked" if criterion_id == "final-reference-demotion-allowed" else "passed"
            rows.append(
                {
                    "criterion_id": criterion_id,
                    "decision_id": f"phase27-final-readiness-{criterion_id}",
                    "decision": "pending" if status == "blocked" else "approve",
                    "status": status,
                    "demotion_authorization": "blocked",
                    "evidence_state": row["status"],
                    "evidence_refs": row["evidence_refs"],
                    "artifact_refs": row["artifact_refs"],
                    "exception": {"status": "none"},
                    "exception_state": "none",
                    "hard_failure_reasons": [],
                    "hard_failure_state": "none",
                    "maintainer_decision": "pending" if status == "blocked" else "approve",
                    "approver": "phase27-test-maintainer" if status == "passed" else "",
                    "approver_role": "release-maintainer" if status == "passed" else "",
                    "decision_timestamp": "2026-06-25T04:00:00Z" if status == "passed" else "",
                    "rationale": str(row["failure_reason"]),
                    "redaction_summary": "redaction_status=passed",
                    "residual_risk": "Reviewed by Phase 27 test fixture." if status == "passed" else "Pending Phase 28 demotion decision.",
                    "residual_risk_state": "reviewed" if status == "passed" else "unreviewed",
                }
            )
        return rows

    def write_phase_inputs(
        self,
        root: Path,
        phase26_rows: list[dict[str, object]] | None = None,
        phase27_rows: list[dict[str, object]] | None = None,
    ) -> None:
        phase26_rows = phase26_rows or self.phase26_rows(root)
        phase27_rows = phase27_rows or self.phase27_final_rows(phase26_rows)
        self.write_json(root, PHASE26_ROWS, {"rows": phase26_rows})
        self.write_json(
            root,
            PHASE27_HANDOFF,
            {
                "phase": "27-retained-code-and-maintainer-acceptance-decisions",
                "phase_lifecycle_id": "27-2026-06-25T01-06-06",
                "demotion_authorization": "blocked",
                "phase27_may_authorize_demotion": False,
                "phase28_required_decision": "explicit-maintainer-reference-demotion-decision",
                "blocked_criteria": ["final-reference-demotion-allowed"],
            },
        )
        residual_rows = [
            {
                "row_id": row["criterion_id"],
                "row_type": "final_readiness_decision",
                "owner": row.get("approver", ""),
                "residual_risk": row.get("residual_risk", "Pending review."),
                "residual_risk_state": row.get("residual_risk_state", "unreviewed"),
            }
            for row in phase27_rows
        ]
        exception_rows = [
            {
                "row_id": row["criterion_id"],
                "row_type": "final_readiness_decision",
                "owner": "phase28-test-maintainer",
                "exception": row["exception"],
            }
            for row in phase27_rows
            if row.get("exception_state") in {"approved-exception", "exception-approved"}
        ]
        self.write_json(root, "build/ci-evidence/phase27/final-readiness-decision-summary.json", {"rows": phase27_rows})
        self.write_json(root, "build/ci-evidence/phase27/residual-risk-register.json", {"rows": residual_rows})
        self.write_json(root, "build/ci-evidence/phase27/exception-decision-register.json", {"rows": exception_rows})
        self.write_json(
            root,
            "build/ci-evidence/phase27/artifact-reference-summary.json",
            {
                "phase26_upstream_rows": PHASE26_ROWS,
                "artifact_refs": [
                    {
                        "path": "build/ci-evidence/phase27/final-readiness-decision-summary.json",
                        "purpose": "phase27-final-readiness-decision-evidence",
                    }
                ],
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase27/decision-row-table.json",
            {
                "rows": [
                    {
                        "row_id": row["criterion_id"],
                        "row_type": "final_readiness_decision",
                        "decision": row["decision"],
                        "status": row["status"],
                        "demotion_authorization": "blocked",
                        "hard_failure_state": row["hard_failure_state"],
                        "maintainer_decision": row["maintainer_decision"],
                    }
                    for row in phase27_rows
                ]
            },
        )

    def demotion_decision(self, authorization: str = "approved") -> dict[str, object]:
        return {
            "phase": "28-final-readiness-packet-and-demotion-gate",
            "phase_lifecycle_id": "28-2026-06-25T03-31-49",
            "demotion_authorization": authorization,
            "approver": "phase28-test-maintainer",
            "approver_role": "release-maintainer",
            "decision_timestamp": "2026-06-25T05:00:00Z",
            "rationale": "Maintainer explicitly reviewed the Phase 28 packet.",
            "scope": "supported-printer-release-surface",
            "evidence_refs": ["build/ci-evidence/phase28/final-readiness-packet.json#reference-demotion-gate"],
        }

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

    def test_contract_rejects_phase18_authority_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase18_contract = self.read_json(root, PHASE18_CONTRACT)
            phase18_contract["upstream_result_requirements"] = [
                row
                for row in phase18_contract["upstream_result_requirements"]
                if row["criterion_id"] != "final-ci-evidence"
            ]
            self.write_json(root, PHASE18_CONTRACT, phase18_contract)

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

    def test_quick_generates_all_outputs_and_keeps_demotion_blocked_without_decision(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for artifact in GENERATED_ARTIFACTS:
                self.assertTrue((root / DEFAULT_OUTPUT_DIR / artifact).exists(), artifact)
            packet = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            self.assertEqual(packet["final_readiness_status"], "unblocked")
            self.assertEqual(packet["reference_demotion_authorization"], "blocked")
            self.assertFalse(packet["real_maintainer_demotion_approval_supplied"])
            self.assertEqual({row["criterion_id"] for row in packet["criteria"]}, set(REQUIRED_CRITERIA))
            self.assertIn("requirements", packet)

    def test_packet_carries_consumed_phase23_24_25_refs_from_phase26_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase26_rows = self.consumed_phase26_rows(root)
            phase27_rows = self.phase27_final_rows(phase26_rows)
            for row in phase27_rows:
                criterion_id = str(row["criterion_id"])
                if criterion_id in {
                    "final-simulator-evidence",
                    "final-hardware-safety-media-evidence",
                    "final-live-network-transfer-evidence",
                }:
                    row["evidence_refs"] = [f"build/ci-evidence/phase27/final-readiness-decision-summary.json#{criterion_id}"]
                    row["artifact_refs"] = [f"build/ci-evidence/phase27/decision-row-table.json#{criterion_id}"]
            self.write_phase_inputs(root, phase26_rows, phase27_rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            packet = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            criteria = {row["criterion_id"]: row for row in packet["criteria"]}
            expected_rows = {
                "final-simulator-evidence": {
                    "requirement_ids": ["EVID-01", "ACPT-01"],
                    "manifest_ref": "build/ci-evidence/phase23/simulator-result-manifest.json",
                    "input_row_ref": "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                    "external_ref": "external://phase23/simulator/startup-log.json",
                },
                "final-hardware-safety-media-evidence": {
                    "requirement_ids": ["EVID-02", "ACPT-01"],
                    "manifest_ref": "build/ci-evidence/phase24/hardware-media-safety-result-manifest.json",
                    "input_row_ref": "build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json",
                    "external_ref": "external://phase24/hardware/safety-report.json",
                },
                "final-live-network-transfer-evidence": {
                    "requirement_ids": ["EVID-03", "ACPT-01"],
                    "manifest_ref": "build/ci-evidence/phase25/live-service-result-manifest.json",
                    "input_row_ref": "build/ci-evidence/phase25/upstream-live-service-result-row.json",
                    "external_ref": "external://phase25/live-service/connect-report.json",
                },
            }
            for criterion_id, expected in expected_rows.items():
                with self.subTest(criterion_id=criterion_id):
                    row = criteria[criterion_id]
                    phase27_ref = f"build/ci-evidence/phase27/final-readiness-decision-summary.json#{criterion_id}"
                    self.assertEqual(row["requirement_ids"], expected["requirement_ids"])
                    self.assertIn(expected["manifest_ref"], row["source_refs"])
                    self.assertIn(expected["input_row_ref"], row["source_refs"])
                    self.assertIn(expected["manifest_ref"], row["evidence_refs"])
                    self.assertIn(expected["input_row_ref"], row["evidence_refs"])
                    self.assertIn(phase27_ref, row["evidence_refs"])
                    self.assertIn(expected["external_ref"], row["artifact_refs"])
                    self.assertIn(expected["input_row_ref"], row["artifact_refs"])

    def test_consumed_upstream_rows_do_not_authorize_reference_demotion_without_decision(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root, self.consumed_phase26_rows(root))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            packet = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            demotion_row = next(row for row in packet["criteria"] if row["criterion_id"] == "final-reference-demotion-allowed")
            self.assertEqual(packet["final_readiness_status"], "unblocked")
            self.assertEqual(packet["reference_demotion_authorization"], "blocked")
            self.assertFalse(packet["real_maintainer_demotion_approval_supplied"])
            self.assertEqual(demotion_row["readiness_effect"], "blocked-pending-explicit-demotion-decision")
            self.assertEqual(demotion_row["demotion_gate_effect"], "requires-explicit-phase28-decision")

    def test_missing_inputs_report_generation_commands(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase26_release_signing_upstream_evidence.py --quick", result.stdout)

    def test_hard_blocker_runs_before_exception_coverage(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase26_rows = self.phase26_rows(root)
            phase26_rows[0]["status"] = "failed"
            phase26_rows[0]["redaction_status"] = "failed"
            phase26_rows[0]["failure_reason"] = "redaction-failed while exception metadata exists"
            phase27_rows = self.phase27_final_rows(phase26_rows)
            phase27_rows[0]["status"] = "exception-approved"
            phase27_rows[0]["decision"] = "exception"
            phase27_rows[0]["exception_state"] = "approved-exception"
            phase27_rows[0]["exception"] = self.exception_metadata(str(phase26_rows[0]["criterion_id"]))
            self.write_phase_inputs(root, phase26_rows, phase27_rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            table = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/normalized-readiness-criteria-table.json")
            row = next(row for row in table["rows"] if row["criterion_id"] == "final-ci-evidence")
            self.assertEqual(row["readiness_effect"], "blocked-hard-failure")
            self.assertIn("redaction-failed", row["hard_failure_reasons"])

    def test_source_hard_blocker_status_fields_outrank_exception_coverage(self) -> None:
        cases = [
            ("overclaim_status", "failed", "overclaim-failed"),
            ("unsafe_ref_status", "failed", "unsafe-ref"),
        ]
        for field, value, expected_reason in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    phase26_rows = self.phase26_rows(root)
                    phase26_rows[0]["status"] = "failed"
                    phase26_rows[0][field] = value
                    phase26_rows[0]["failure_reason"] = "approved exception metadata must not cover hard blockers"
                    phase27_rows = self.phase27_final_rows(phase26_rows)
                    phase27_rows[0]["status"] = "exception-approved"
                    phase27_rows[0]["decision"] = "exception"
                    phase27_rows[0]["exception_state"] = "approved-exception"
                    phase27_rows[0]["exception"] = self.exception_metadata(str(phase26_rows[0]["criterion_id"]))
                    self.write_phase_inputs(root, phase26_rows, phase27_rows)

                    # Act
                    result = self.run_verifier(["--quick"], maybe_root=root)

                    # Assert
                    self.assertEqual(result.returncode, 0, result.stdout)
                    table = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/normalized-readiness-criteria-table.json")
                    row = next(row for row in table["rows"] if row["criterion_id"] == "final-ci-evidence")
                    self.assertEqual(row["readiness_effect"], "blocked-hard-failure")
                    self.assertIn(expected_reason, row["hard_failure_reasons"])

    def test_valid_exception_covers_coverable_failure(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase26_rows = self.phase26_rows(root)
            phase26_rows[0]["status"] = "failed"
            phase26_rows[0]["failure_reason"] = "Operator documented a coverable exception."
            phase27_rows = self.phase27_final_rows(phase26_rows)
            phase27_rows[0]["status"] = "exception-approved"
            phase27_rows[0]["decision"] = "exception"
            phase27_rows[0]["exception_state"] = "approved-exception"
            phase27_rows[0]["exception"] = self.exception_metadata(str(phase26_rows[0]["criterion_id"]))
            self.write_phase_inputs(root, phase26_rows, phase27_rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            table = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/normalized-readiness-criteria-table.json")
            row = next(row for row in table["rows"] if row["criterion_id"] == "final-ci-evidence")
            self.assertEqual(row["readiness_effect"], "exception-covered")
            self.assertEqual(row["exception_state"], "covered")

    def test_explicit_demotion_approval_is_rejected_when_readiness_blocked(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase26_rows = self.phase26_rows(root)
            phase26_rows[0]["status"] = "blocked"
            phase26_rows[0]["failure_reason"] = "CI remains blocked for test."
            phase27_rows = self.phase27_final_rows(phase26_rows)
            phase27_rows[0]["status"] = "blocked"
            self.write_phase_inputs(root, phase26_rows, phase27_rows)
            decision_path = self.write_json(root, "demotion-decision.json", self.demotion_decision("approved"))

            # Act
            result = self.run_verifier(["--quick", "--demotion-decision-input", decision_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("final_readiness_status unblocked", result.stdout)

    def test_lifecycle_and_source_ref_drift_are_rejected(self) -> None:
        cases = [
            ("source_lifecycle_status", "stale", "source_lifecycle_status must be current"),
            ("source_ref_status", "invalid", "source_ref_status must be passed"),
        ]
        for field, value, expected in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    phase26_rows = self.phase26_rows(root)
                    phase26_rows[0][field] = value
                    self.write_phase_inputs(root, phase26_rows)

                    # Act
                    result = self.run_verifier(["--quick"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_incomplete_demotion_metadata_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            decision = self.demotion_decision("blocked")
            del decision["approver"]
            decision_path = self.write_json(root, "demotion-decision.json", decision)

            # Act
            result = self.run_verifier(["--quick", "--demotion-decision-input", decision_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approver", result.stdout)

    def test_security_scan_accepts_approved_demotion_input_after_unblocked_packet(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            decision_path = self.write_json(root, "demotion-decision.json", self.demotion_decision("approved"))
            quick_result = self.run_verifier(["--quick", "--demotion-decision-input", decision_path], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            packet = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            self.assertEqual(packet["final_readiness_status"], "unblocked")
            self.assertEqual(packet["reference_demotion_authorization"], "approved")
            demotion_row = next(row for row in packet["criteria"] if row["criterion_id"] == "final-reference-demotion-allowed")
            self.assertEqual(demotion_row["readiness_effect"], "reference-demotion-authorized")
            self.assertEqual(demotion_row["demotion_gate_effect"], "explicit-phase28-decision-approved")
            blockers = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/blocker-summary.json")
            blocker_ids = {row["criterion_id"] for row in blockers["blockers"]}
            self.assertNotIn("final-reference-demotion-allowed", blocker_ids)
            report = (root / DEFAULT_OUTPUT_DIR / "redacted-readiness-report.md").read_text(encoding="utf-8")
            self.assertIn("final-reference-demotion-allowed -> reference-demotion-authorized", report)
            self.assertNotIn("blocked-pending-explicit-demotion-decision", report)

            # Act
            result = self.run_verifier(["--security-only", "--demotion-decision-input", decision_path], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_report_is_derived_from_packet_and_names_review_boundary(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            report = (root / DEFAULT_OUTPUT_DIR / "redacted-readiness-report.md").read_text(encoding="utf-8")
            packet = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            self.assertIn("Review material only", report)
            self.assertIn(f"final_readiness_status: {packet['final_readiness_status']}", report)
            self.assertIn("reference_demotion_authorization: blocked", report)

    def test_output_root_symlink_escape_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            outside = root / "outside-output"
            outside.mkdir()
            output_root = root / DEFAULT_OUTPUT_DIR
            output_root.parent.mkdir(parents=True, exist_ok=True)
            output_root.symlink_to(outside, target_is_directory=True)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink escape", result.stdout)

    def test_security_scan_rejects_secret_fields_and_generated_overclaims(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["private_key"] = "redacted-test-value"
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private_key", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            self.write_text(root, f"{DEFAULT_OUTPUT_DIR}/redacted-readiness-report.md", "reference demotion approved\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reference demotion approved", result.stdout)

    def test_security_scan_rejects_generated_demotion_overclaim_field(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            packet = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            packet["demotion_allowed"] = True
            self.write_json(root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json", packet)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("demotion_allowed", result.stdout)

    def test_verifier_does_not_use_shell_or_inline_interpreters(self) -> None:
        # Arrange
        source = VERIFIER.read_text(encoding="utf-8")

        # Act / Assert
        for forbidden in ["shell=True", "bash -c", "python -c", "node -e"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_wiring_only_validates_bazel_wrapper_and_just_targets(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_only_rejects_phase28_workflow_order_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            workflow = (root / "tools/bazel/rust_workflow.sh").read_text(encoding="utf-8")
            workflow = workflow.replace(
                "    python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only\n"
                "    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26\n",
                "    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26\n"
                "    python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only\n",
            )
            self.write_text(root, "tools/bazel/rust_workflow.sh", workflow)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase28_verify command order", result.stdout)

    def test_wiring_only_rejects_just_recipe_order_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            just_text = (root / "justfile").read_text(encoding="utf-8")
            just_text = just_text.replace(
                "phase28-verify:\n    bazel run //tools/bazel:phase28_verify_tests\n    bazel run //tools/bazel:phase28_verify\n",
                "phase28-verify:\n    bazel run //tools/bazel:phase28_verify\n    bazel run //tools/bazel:phase28_verify_tests\n",
            )
            self.write_text(root, "justfile", just_text)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must run tests before verifier", result.stdout)


if __name__ == "__main__":
    unittest.main()
