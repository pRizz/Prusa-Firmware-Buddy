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
VERIFIER = ROOT / "tools/bazel/phase34_final_readiness_demotion_dry_run.py"
CONTRACT = ROOT / "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json"
PHASE31_MANIFEST = "build/ci-evidence/phase31/final-intake-manifest.json"
PHASE32_REGISTER = "build/ci-evidence/phase32/blocker-register.json"
PHASE33_HANDOFF = "build/ci-evidence/phase33/downstream-handoff-manifest.json"
OUTPUT_DIR = "build/ci-evidence/phase34"
LEDGER_FIELDS = [
    "row_id",
    "source_stream",
    "source_ref",
    "requirement_ids",
    "affected_gates",
    "proof_eligibility",
    "evidence_status",
    "row_problem_kind",
    "blocker_kind",
    "severity",
    "evidence_refs",
    "artifact_refs",
    "classification_ref",
    "retained_code_decision_refs",
    "residual_risk_decision_refs",
    "exception_decision_refs",
    "readiness_decision_refs",
    "coverage_state",
    "readiness_effect",
    "reason_codes",
]
GENERATED_ARTIFACTS = [
    "final-readiness-run-manifest.json",
    "readiness-coverage-ledger.json",
    "final-readiness-packet.json",
    "readiness-blocker-summary.json",
    "demotion-dry-run.json",
    "redacted-readiness-report.md",
    "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase33-downstream-handoff-manifest.json",
    "contract-snapshots/phase32-blocker-register.json",
    "contract-snapshots/phase31-final-intake-manifest.json",
    "contract-snapshots/phase31-accepted-receipts.json",
]


class Phase34FinalReadinessDemotionDryRunTest(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location("phase34_final_readiness_demotion_dry_run", VERIFIER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def write_json(self, root: Path, relative_path: str, value: object) -> str:
        full_path = root / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return relative_path

    def write_text(self, root: Path, relative_path: str, value: str) -> None:
        full_path = root / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(value, encoding="utf-8")

    def read_json(self, root: Path, relative_path: str) -> dict[str, object]:
        return json.loads((root / relative_path).read_text(encoding="utf-8"))

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for relative_path in [
            "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json",
            "tools/bazel/manifests/phase31_final_evidence_intake_contract.json",
            "tools/bazel/manifests/phase32_blocker_register_triage_contract.json",
            "tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json",
            "tools/bazel/manifests/phase28_final_readiness_packet_contract.json",
        ]:
            source = ROOT / relative_path
            destination = root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        if VERIFIER.exists():
            destination = root / VERIFIER.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(VERIFIER, destination)
        self.write_text(root, "BUILD.bazel", "")
        self.write_text(root, "tools/bazel/BUILD.bazel", "")
        self.write_text(root, "tools/bazel/rust_workflow.sh", "#!/usr/bin/env bash\n")
        self.write_text(root, "justfile", "")
        return temp_dir, root

    def receipt(
        self,
        stream: str,
        source_ref: str,
        *,
        evidence_status: str = "passed",
        redaction_status: str = "passed",
        source_ref_status: str = "passed",
        exception_status: str = "none",
    ) -> dict[str, object]:
        return {
            "artifact_reference_summary": {
                "artifact_refs": [f"external://{stream}/sanitized-report.json"],
            },
            "consumed_upstream_row_refs": [source_ref],
            "evidence_status": evidence_status,
            "exception_status": exception_status,
            "failure_reason": "" if evidence_status == "passed" else f"{stream} evidence failed",
            "finality_status": "accepted-final",
            "packet_sha256": "a" * 64,
            "receipt_generated_at_utc": "2026-07-25T18:30:00Z",
            "redaction_status": redaction_status,
            "requirement_ids": ["READY-01"],
            "source_contract": f"tools/bazel/manifests/{stream}_contract.json",
            "source_phase": f"{stream}-evidence",
            "source_ref_status": source_ref_status,
            "stream": stream,
            "submission_id": f"phase31-{stream}-fixture",
            "submitter_identity_ref": "maintainer://phase34-test",
            "validator_command": ["python3", "sanitized-validator.py"],
            "validator_output_refs": [source_ref],
        }

    def blocker_row(
        self,
        row_id: str,
        source_ref: str,
        *,
        row_problem_kind: str = "failed",
        affected_gate: str = "final-simulator-evidence",
    ) -> dict[str, object]:
        return {
            "row_id": row_id,
            "source_stream": "simulator",
            "source_ref": source_ref,
            "requirement_ids": ["READY-01"],
            "affected_gate": affected_gate,
            "row_problem_kind": row_problem_kind,
            "blocker_kind": "exception_request" if row_problem_kind == "exception_requested" else "repair_item",
            "severity": "critical" if row_problem_kind != "exception_requested" else "medium",
            "owner_ref": "maintainer://phase34-test",
            "required_next_action": "Resolve before readiness.",
            "decision_impact": "exception_decision_required" if row_problem_kind == "exception_requested" else "final_readiness_blocked",
            "proof_eligibility": "ineligible",
            "evidence_refs": [source_ref],
        }

    def decision(
        self,
        decision_id: str,
        decision_type: str,
        decision_value: str,
        blocker_ref: str,
        *,
        affected_gate: str = "final-simulator-evidence",
    ) -> dict[str, object]:
        row = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "decision_value": decision_value,
            "source_row_refs": [blocker_ref],
            "maintainer_identity_ref": "maintainer://phase34-test",
            "maintainer_role": "firmware-maintainer",
            "owner_signoff_ref": "maintainer://phase34-owner",
            "decision_timestamp": "2026-07-25T18:45:00Z",
            "rationale": f"Phase 34 fixture decision for {decision_id}.",
            "artifact_refs": ["external://phase33/sanitized-decision.json"],
            "evidence_refs": [blocker_ref],
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "source_row_ids": [blocker_ref.rsplit("#", 1)[-1]],
            "affected_gates": [affected_gate],
            "decision_axis": decision_type,
        }
        if decision_type == "exception":
            row["linked_blocker_refs"] = [blocker_ref]
            row["coverage_state"] = "approved-exception" if decision_value == "approve" else "rejected"
        return row

    def approved_projection_fixture(
        self,
        blocker_ref: str,
    ) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object]]:
        readiness_decision = self.decision("approve-readiness", "readiness", "approve", blocker_ref)
        demotion_decision = self.decision("approve-demotion", "reference_demotion", "approve", blocker_ref)
        readiness = {
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "handoff_state": "approval-input-recorded",
            "readiness_input_supplied": True,
            "decision_id": readiness_decision["decision_id"],
            "source_row_refs": readiness_decision["source_row_refs"],
            "phase34_must_generate_final_readiness": True,
            "rationale": readiness_decision["rationale"],
        }
        demotion = {
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "authorization_state": "approved-input-recorded",
            "demotion_input_supplied": True,
            "decision_id": demotion_decision["decision_id"],
            "source_row_refs": demotion_decision["source_row_refs"],
            "maintainer_identity_ref": demotion_decision["maintainer_identity_ref"],
            "maintainer_role": demotion_decision["maintainer_role"],
            "decision_timestamp": demotion_decision["decision_timestamp"],
            "phase34_must_validate_readiness": True,
            "rationale": demotion_decision["rationale"],
        }
        return [readiness_decision, demotion_decision], readiness, demotion

    def write_fixture(
        self,
        root: Path,
        receipts: list[dict[str, object]],
        blocker_rows: list[dict[str, object]],
        decisions: list[dict[str, object]] | None = None,
        readiness: dict[str, object] | None = None,
        demotion: dict[str, object] | None = None,
    ) -> None:
        receipt_refs = []
        for index, receipt in enumerate(receipts):
            receipt_ref = f"build/ci-evidence/phase31/stream-receipts/receipt-{index}.json"
            receipt_refs.append(self.write_json(root, receipt_ref, receipt))
        self.write_json(
            root,
            PHASE31_MANIFEST,
            {
                "accepted_count": len(receipts),
                "artifact_name": "phase31-final-evidence-intake",
                "finality_status": "accepted-final" if receipts else "quarantined-non-final",
                "output_root": "build/ci-evidence/phase31",
                "phase": "31-final-evidence-intake",
                "phase_lifecycle_id": "31-2026-07-03T02-04-07",
                "receipt_refs": receipt_refs,
                "rejected_count": 0,
                "streams": [
                    {
                        "finality_status": receipt["finality_status"],
                        "receipt_ref": receipt_refs[index],
                        "stream": receipt["stream"],
                        "submission_id": receipt["submission_id"],
                    }
                    for index, receipt in enumerate(receipts)
                ],
            },
        )
        self.write_json(
            root,
            PHASE32_REGISTER,
            {
                "artifact_name": "phase32-blocker-register-triage",
                "phase": "32-blocker-register-and-evidence-triage",
                "phase_lifecycle_id": "32-2026-07-03T14-13-51",
                "rows": blocker_rows,
            },
        )
        phase33_dir = "build/ci-evidence/phase33"
        registers = {
            "normalized_decision_records": f"{phase33_dir}/normalized-decision-records.json",
            "retained_code_decision_register": f"{phase33_dir}/retained-code-decision-register.json",
            "residual_risk_decision_register": f"{phase33_dir}/residual-risk-decision-register.json",
            "exception_decision_register": f"{phase33_dir}/exception-decision-register.json",
            "readiness_decision_handoff": f"{phase33_dir}/readiness-decision-handoff.json",
            "demotion_decision_handoff": f"{phase33_dir}/demotion-decision-handoff.json",
            "decision_validation_report": f"{phase33_dir}/decision-validation-report.json",
        }
        decision_rows = decisions or []
        self.write_json(root, registers["normalized_decision_records"], {"rows": decision_rows})
        for key, decision_type in [
            ("retained_code_decision_register", "retained_code"),
            ("residual_risk_decision_register", "residual_risk"),
            ("exception_decision_register", "exception"),
        ]:
            self.write_json(
                root,
                registers[key],
                {"rows": [row for row in decision_rows if row["decision_type"] == decision_type]},
            )
        self.write_json(
            root,
            registers["readiness_decision_handoff"],
            readiness
            or {
                "phase": "33-maintainer-decision-inputs",
                "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                "handoff_state": "blocked-pending-maintainer-input",
                "readiness_input_supplied": False,
                "blocked_source_row_refs": [],
            },
        )
        self.write_json(
            root,
            registers["demotion_decision_handoff"],
            demotion
            or {
                "phase": "33-maintainer-decision-inputs",
                "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                "authorization_state": "blocked",
                "demotion_input_supplied": False,
                "phase34_must_validate_readiness": True,
            },
        )
        self.write_json(root, registers["decision_validation_report"], {"validation_state": "valid"})
        self.write_json(
            root,
            PHASE33_HANDOFF,
            {
                "phase": "33-maintainer-decision-inputs",
                "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                "artifact_name": "phase33-maintainer-decision-inputs",
                "output_root": phase33_dir,
                "raw_evidence_consumed": False,
                "source_inputs": {
                    "phase32_canonical_register_ref": PHASE32_REGISTER,
                    "raw_evidence_consumed": False,
                },
                "register_refs": registers,
                "downstream_consumers": ["phase34-final-readiness-and-demotion-dry-run"],
            },
        )

    def run_verifier(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        verifier = root / "tools/bazel/phase34_final_readiness_demotion_dry_run.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def run_quick(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return self.run_verifier(
            root,
            "--quick",
            "--phase31-output-dir",
            "build/ci-evidence/phase31",
            "--phase33-handoff",
            PHASE33_HANDOFF,
            "--output-dir",
            OUTPUT_DIR,
            *extra,
        )

    def test_contract_declares_complete_ledger_gate_and_artifacts(self) -> None:
        # Arrange
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

        # Act
        open_requires = contract["demotion_dry_run_schema"]["open_requires"]

        # Assert
        self.assertEqual(contract["id"], "phase34_final_readiness_demotion_dry_run_contract")
        self.assertEqual(contract["requirement_ids"], ["READY-01", "READY-02", "READY-03"])
        self.assertEqual(contract["ledger_schema"]["required_fields"], LEDGER_FIELDS)
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)
        self.assertEqual(
            open_requires,
            {
                "readiness_state": "unblocked",
                "approval_validation_state": "valid",
                "approval_decision_state": "approve",
            },
        )
        self.assertTrue(contract["sparse_blocker_overlay_policy"]["clean_row_may_omit_phase32_classification"])
        self.assertFalse(contract["source_inputs"]["raw_evidence_consumed"])

    def test_quick_default_writes_blocked_packet_and_dry_run(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [])

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        dry_run = self.read_json(root, f"{OUTPUT_DIR}/demotion-dry-run.json")
        packet = self.read_json(root, f"{OUTPUT_DIR}/final-readiness-packet.json")
        self.assertEqual(dry_run["gate_state"], "blocked")
        self.assertEqual(dry_run["approval_validation_state"], "missing")
        self.assertEqual(packet["readiness_state"], "blocked")

    def test_expected_rows_come_from_phase31_accepted_final_receipts(self) -> None:
        # Arrange
        module = self.load_module()
        receipts = [
            self.receipt("simulator", "build/ci-evidence/phase23/upstream-simulator-result-row.json"),
            self.receipt("live-service", "build/ci-evidence/phase25/upstream-live-service-result-row.json"),
        ]

        # Act
        rows = module.derive_expected_rows(receipts)

        # Assert
        self.assertEqual([row["source_stream"] for row in rows], ["live-service", "simulator"])
        self.assertEqual(len(rows), 2)

    def test_clean_final_passed_row_needs_no_phase32_blocker(self) -> None:
        # Arrange
        module = self.load_module()
        receipts = [self.receipt("simulator", "build/ci-evidence/phase23/upstream-simulator-result-row.json")]

        # Act
        ledger = module.evaluate_coverage(receipts, [], [])

        # Assert
        self.assertEqual(ledger[0]["coverage_state"], "clean-no-blocker")
        self.assertEqual(ledger[0]["readiness_effect"], "unblocked")
        self.assertEqual(ledger[0]["classification_ref"], "")

    def test_problem_row_without_phase32_classification_is_underclassified(self) -> None:
        # Arrange
        module = self.load_module()
        receipts = [
            self.receipt(
                "simulator",
                "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                evidence_status="failed",
            )
        ]

        # Act
        ledger = module.evaluate_coverage(receipts, [], [])

        # Assert
        self.assertEqual(ledger[0]["coverage_state"], "underclassified")
        self.assertEqual(ledger[0]["readiness_effect"], "blocked")
        self.assertIn("underclassified", ledger[0]["reason_codes"])

    def test_packet_links_rows_classifications_decisions_blockers_and_artifact_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        blocker = self.blocker_row("failed-simulator", source_ref)
        blocker_ref = f"{PHASE32_REGISTER}#failed-simulator"
        decisions = [self.decision("block-readiness", "readiness", "block", blocker_ref)]
        self.write_fixture(root, [self.receipt("simulator", source_ref, evidence_status="failed")], [blocker], decisions)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        packet = self.read_json(root, f"{OUTPUT_DIR}/final-readiness-packet.json")
        row = packet["ledger_rows"][0]
        self.assertEqual(row["classification_ref"], blocker_ref)
        self.assertIn("external://simulator/sanitized-report.json", row["artifact_refs"])
        self.assertTrue(row["readiness_decision_refs"])
        self.assertEqual(packet["readiness_state"], "blocked")

    def test_missing_failed_stale_malformed_redaction_and_underclassified_rows_block(self) -> None:
        module = self.load_module()
        cases = [
            ("missing", "required-row-missing"),
            ("failed", "evidence-failed"),
            ("stale", "evidence-stale"),
            ("malformed", "evidence-malformed"),
            ("redaction_failed", "redaction-failed"),
            ("unknown_unclassified", "unknown-classification"),
        ]
        for problem_kind, expected_reason in cases:
            with self.subTest(problem_kind=problem_kind):
                # Arrange
                source_ref = f"external://fixture/{problem_kind}"
                receipt = self.receipt("simulator", source_ref, evidence_status="failed")
                blocker = self.blocker_row(problem_kind, source_ref, row_problem_kind=problem_kind)

                # Act
                ledger = module.evaluate_coverage([receipt], [blocker], [])

                # Assert
                self.assertEqual(ledger[0]["readiness_effect"], "blocked")
                self.assertIn(expected_reason, ledger[0]["reason_codes"])

    def test_exception_requires_exact_row_and_gate_coverage(self) -> None:
        # Arrange
        module = self.load_module()
        source_ref = "external://fixture/exception"
        receipt = self.receipt("simulator", source_ref, evidence_status="failed", exception_status="exception-requested")
        blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
        blocker_ref = f"{PHASE32_REGISTER}#exception-row"
        exact = self.decision("approve-exact", "exception", "approve", blocker_ref)
        wrong_gate = self.decision("approve-wrong", "exception", "approve", blocker_ref, affected_gate="final-live-network-transfer-evidence")

        # Act
        covered = module.evaluate_coverage([receipt], [blocker], [exact])
        uncovered = module.evaluate_coverage([receipt], [blocker], [wrong_gate])

        # Assert
        self.assertEqual(covered[0]["coverage_state"], "exception-covered")
        self.assertEqual(covered[0]["readiness_effect"], "unblocked")
        self.assertEqual(uncovered[0]["coverage_state"], "exception-uncovered")
        self.assertEqual(uncovered[0]["readiness_effect"], "blocked")

    def test_green_rows_without_explicit_demotion_approval_stay_blocked(self) -> None:
        # Arrange
        module = self.load_module()

        # Act
        result = module.evaluate_demotion("unblocked", "missing", "missing", [])

        # Assert
        self.assertEqual(result["gate_state"], "blocked")
        self.assertIn("approval-missing", result["reason_codes"])

    def test_demotion_truth_table_opens_only_for_unblocked_valid_approve(self) -> None:
        module = self.load_module()
        for readiness in ["blocked", "unblocked"]:
            for validation in ["missing", "invalid", "valid"]:
                for decision in ["missing", "approve", "reject"]:
                    with self.subTest(readiness=readiness, validation=validation, decision=decision):
                        # Arrange / Act
                        result = module.evaluate_demotion(readiness, validation, decision, [])

                        # Assert
                        expected = "open" if (readiness, validation, decision) == ("unblocked", "valid", "approve") else "blocked"
                        self.assertEqual(result["gate_state"], expected)

    def test_open_gate_requires_corroborated_readiness_and_demotion_decisions(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
        blocker_ref = f"{PHASE32_REGISTER}#exception-row"
        decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
        decisions.append(self.decision("approve-exception", "exception", "approve", blocker_ref))
        receipt = self.receipt("simulator", source_ref, evidence_status="failed", exception_status="exception-requested")
        self.write_fixture(root, [receipt], [blocker], decisions, readiness, demotion)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        dry_run = self.read_json(root, f"{OUTPUT_DIR}/demotion-dry-run.json")
        self.assertEqual(dry_run["gate_state"], "open")

    def test_unknown_projection_decision_ids_are_rejected(self) -> None:
        for projection_name in ["readiness", "demotion"]:
            with self.subTest(projection=projection_name):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
                blocker_ref = f"{PHASE32_REGISTER}#exception-row"
                decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
                decisions.append(self.decision("approve-exception", "exception", "approve", blocker_ref))
                target = readiness if projection_name == "readiness" else demotion
                target["decision_id"] = "unknown-decision"
                receipt = self.receipt(
                    "simulator",
                    source_ref,
                    evidence_status="failed",
                    exception_status="exception-requested",
                )
                self.write_fixture(root, [receipt], [blocker], decisions, readiness, demotion)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unknown Phase 33 decision_id", result.stdout)

    def test_duplicate_normalized_decision_ids_are_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
        blocker_ref = f"{PHASE32_REGISTER}#exception-row"
        decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
        duplicate = self.decision("approve-demotion", "reference_demotion", "approve", blocker_ref)
        decisions.append(duplicate)
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [blocker], decisions, readiness, demotion)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate Phase 33 decision_id", result.stdout)

    def test_projection_decision_axis_and_value_must_authorize_projection(self) -> None:
        cases = [
            ("decision_type", "readiness"),
            ("decision_value", "reject"),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
                blocker_ref = f"{PHASE32_REGISTER}#exception-row"
                decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
                demotion_decision = decisions[1]
                demotion_decision[field] = value
                demotion_decision["decision_axis"] = demotion_decision["decision_type"]
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [blocker], decisions, readiness, demotion)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("does not authorize reference_demotion=approve", result.stdout)

    def test_projection_metadata_and_source_refs_must_match_normalized_decision(self) -> None:
        cases = [
            ("maintainer_role", "different-role"),
            ("source_row_refs", [f"{PHASE32_REGISTER}#different-row"]),
        ]
        for field, value in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
                blocker_ref = f"{PHASE32_REGISTER}#exception-row"
                decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
                demotion[field] = value
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [blocker], decisions, readiness, demotion)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(f"projection mismatch for {field}", result.stdout)

    def test_normalized_decision_timestamp_must_be_iso_utc(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
        blocker_ref = f"{PHASE32_REGISTER}#exception-row"
        decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
        decisions[1]["decision_timestamp"] = "not-even-a-timestamp"
        demotion["decision_timestamp"] = "not-even-a-timestamp"
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [blocker], decisions, readiness, demotion)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be ISO UTC", result.stdout)

    def test_missing_invalid_stale_and_rejected_approval_write_durable_blocked_result(self) -> None:
        cases = [
            (None, "missing"),
            ({"phase_lifecycle_id": "stale", "authorization_state": "approved-input-recorded"}, "invalid"),
            ({"phase_lifecycle_id": "33-2026-07-04T01-36-41", "authorization_state": "unexpected"}, "invalid"),
            ({"phase_lifecycle_id": "33-2026-07-04T01-36-41", "authorization_state": "rejected"}, "valid"),
        ]
        for demotion, expected_validation in cases:
            with self.subTest(demotion=demotion):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                readiness = {
                    "phase": "33-maintainer-decision-inputs",
                    "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                    "handoff_state": "approval-input-recorded",
                    "readiness_input_supplied": True,
                    "decision_id": "approve-readiness",
                    "source_row_refs": [],
                }
                blocker_rows = []
                decisions = []
                if demotion and demotion.get("authorization_state") == "rejected":
                    blocker = self.blocker_row("demotion-row", source_ref)
                    blocker_rows.append(blocker)
                    blocker_ref = f"{PHASE32_REGISTER}#demotion-row"
                    decision = self.decision("reject-demotion", "reference_demotion", "reject", blocker_ref)
                    decisions.append(decision)
                    demotion.update(
                        {
                            "decision_id": decision["decision_id"],
                            "source_row_refs": decision["source_row_refs"],
                            "rationale": decision["rationale"],
                        }
                    )
                self.write_fixture(
                    root,
                    [self.receipt("simulator", source_ref)],
                    blocker_rows,
                    decisions,
                    readiness,
                    demotion,
                )

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertTrue((root / OUTPUT_DIR / "demotion-dry-run.json").exists())
                dry_run = self.read_json(root, f"{OUTPUT_DIR}/demotion-dry-run.json")
                self.assertEqual(dry_run["gate_state"], "blocked")
                self.assertEqual(dry_run["approval_validation_state"], expected_validation)
                if expected_validation == "invalid":
                    self.assertNotEqual(result.returncode, 0)

    def test_absolute_path_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(root, "--quick", "--phase31-output-dir", root.as_posix())

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("repo-relative", result.stdout)

    def test_parent_traversal_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(root, "--quick", "--phase33-handoff", "../phase33/handoff.json")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("parent traversal", result.stdout)

    def test_wrong_input_root_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(root, "--quick", "--phase31-output-dir", "build/ci-evidence/phase30")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("build/ci-evidence/phase31", result.stdout)

    def test_input_output_overlap_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(
            root,
            "--quick",
            "--phase33-handoff",
            f"{OUTPUT_DIR}/downstream-handoff-manifest.json",
            "--output-dir",
            OUTPUT_DIR,
        )

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside", result.stdout)

    def test_symlink_escape_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside = root / "outside"
        outside.mkdir()
        output = root / OUTPUT_DIR
        output.parent.mkdir(parents=True, exist_ok=True)
        output.symlink_to(outside, target_is_directory=True)

        # Act
        result = self.run_verifier(root, "--quick")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink escape", result.stdout)

    def test_nested_phase33_register_symlink_escapes_are_rejected(self) -> None:
        register_names = [
            "normalized-decision-records.json",
            "readiness-decision-handoff.json",
            "demotion-decision-handoff.json",
        ]
        for register_name in register_names:
            with self.subTest(register=register_name):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [])
                register_path = root / "build/ci-evidence/phase33" / register_name
                outside_path = root / "outside" / register_name
                outside_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(register_path, outside_path)
                register_path.unlink()
                register_path.symlink_to(outside_path)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("symlink escape", result.stdout)

    def test_nested_phase32_register_symlink_escape_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [])
        register_path = root / PHASE32_REGISTER
        outside_path = root / "outside/blocker-register.json"
        outside_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(register_path, outside_path)
        register_path.unlink()
        register_path.symlink_to(outside_path)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink escape", result.stdout)

    def test_security_rejects_secret_fields_unsafe_refs_and_overclaim_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        receipt = self.receipt("simulator", source_ref)
        receipt["token_value"] = "redacted-test-token"
        self.write_fixture(root, [receipt], [])

        # Act
        secret_result = self.run_quick(root)
        self.write_text(root, f"{OUTPUT_DIR}/redacted-readiness-report.md", "cutover verdict approved\n")
        marker_result = self.run_verifier(root, "--security-only", "--output-dir", OUTPUT_DIR)

        # Assert
        self.assertNotEqual(secret_result.returncode, 0)
        self.assertIn("token_value", secret_result.stdout)
        self.assertNotEqual(marker_result.returncode, 0)
        self.assertIn("cutover-verdict", marker_result.stdout)

    def test_lifecycle_and_source_contract_mismatch_fail_closed(self) -> None:
        cases = [
            ("phase31", "phase_lifecycle_id", "stale"),
            ("phase33", "artifact_name", "wrong-contract"),
        ]
        for target, field, value in cases:
            with self.subTest(target=target):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [])
                relative_path = PHASE31_MANIFEST if target == "phase31" else PHASE33_HANDOFF
                payload = self.read_json(root, relative_path)
                payload[field] = value
                self.write_json(root, relative_path, payload)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)

    def test_generated_report_derives_from_packet_and_ledger(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [])

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        packet = self.read_json(root, f"{OUTPUT_DIR}/final-readiness-packet.json")
        ledger = self.read_json(root, f"{OUTPUT_DIR}/readiness-coverage-ledger.json")
        report = (root / OUTPUT_DIR / "redacted-readiness-report.md").read_text(encoding="utf-8")
        self.assertEqual(packet["ledger_rows"], ledger["rows"])
        self.assertIn(f"readiness_state: {packet['readiness_state']}", report)
        self.assertIn(f"gate_state: {packet['demotion_dry_run']['gate_state']}", report)

    def test_wiring_requires_bazel_root_workflow_and_just_entries(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(root, "--wiring-only")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase34_verify", result.stdout)


if __name__ == "__main__":
    unittest.main()
