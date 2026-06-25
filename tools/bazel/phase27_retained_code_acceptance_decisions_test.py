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
VERIFIER = ROOT / "tools/bazel/phase27_retained_code_acceptance_decisions.py"
CONTRACT = "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
PHASE18_CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
PHASE26_CONTRACT = "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
SOURCE_REF_FILES = [
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/foreign_code_inventory.json",
    "tools/bazel/manifests/unsafe_boundary_audit.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
]
REQUIRED_RETAINED_PACKET_IDS = [
    "packet-hal-cmsis-startup-asm",
    "packet-freertos-runtime",
    "packet-marlin-cpp-print-core-oracle",
    "packet-network-lwip-mbedtls-wui",
    "packet-filesystem-fatfs-littlefs-libsysbase",
    "packet-usb-tinyusb-and-media",
    "packet-generated-assets-resource-pipeline",
    "packet-release-signing-and-packaging",
    "packet-mmu-modbus-auxiliary-controllers",
    "packet-runtime-safety-crashdump-watchdog",
]
REQUIRED_UPSTREAM_CRITERION_IDS = [
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
DECISION_AXES = [
    "evidence_state",
    "maintainer_decision",
    "exception_state",
    "residual_risk_state",
    "hard_failure_state",
    "demotion_authorization",
]
GENERATED_ARTIFACTS = [
    "acceptance-run-manifest.json",
    "normalized-retained-code-decisions.json",
    "residual-risk-register.json",
    "exception-decision-register.json",
    "final-readiness-decision-summary.json",
    "phase28-handoff-manifest.json",
    "decision-row-table.json",
    "maintainer-acceptance-input-template.json",
    "artifact-reference-summary.json",
    "contract-snapshots/phase18_cutover_review_contract.json",
    "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json",
    "contract-snapshots/phase26-upstream-result-row-table.json",
]
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase27"
PHASE26_ROWS = "build/ci-evidence/phase26/upstream-result-row-table.json"


class Phase27RetainedCodeAcceptanceDecisionsTest(unittest.TestCase):
    @classmethod
    def load_verifier_module(cls) -> ModuleType:
        spec = importlib.util.spec_from_file_location("phase27_retained_code_acceptance_decisions", VERIFIER)
        if spec is None or spec.loader is None:
            raise RuntimeError("failed to load Phase 27 verifier module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for path in [
            VERIFIER,
            ROOT / CONTRACT,
            ROOT / PHASE18_CONTRACT,
            ROOT / PHASE26_CONTRACT,
            *[ROOT / source_ref for source_ref in SOURCE_REF_FILES],
        ]:
            destination = root / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        return temp_dir, root

    def run_verifier(self, args: list[str], maybe_root: Path | None = None) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase27_retained_code_acceptance_decisions.py"
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

    def write_phase26_rows(self, root: Path) -> None:
        phase18_contract = self.read_json(root, PHASE18_CONTRACT)
        rows = []
        for requirement in phase18_contract["upstream_result_requirements"]:
            criterion_id = str(requirement["criterion_id"])
            status = "blocked" if criterion_id == "final-reference-demotion-allowed" else "passed"
            rows.append(
                {
                    "artifact_refs": [f"build/ci-evidence/phase26/{criterion_id}.json"],
                    "criterion_id": criterion_id,
                    "evidence_family": requirement["evidence_family"],
                    "evidence_refs": list(requirement["required_manifest_refs"]),
                    "exception_status": "none",
                    "failure_reason": "phase27 test upstream row",
                    "generated_at_utc": "2026-06-25T01:30:00Z",
                    "maintainer_state": "blocked" if status == "blocked" else "pending",
                    "owning_phase": requirement["source_phase"],
                    "redaction_status": "passed",
                    "requirement_ids": list(requirement["requirement_ids"]),
                    "source_lifecycle_id": requirement["source_lifecycle_id"],
                    "source_lifecycle_status": "current",
                    "source_ref_status": "passed",
                    "source_requirement_ids": list(requirement["requirement_ids"]),
                    "status": status,
                }
            )
        self.write_json(root, PHASE26_ROWS, {"rows": rows})

    def final_role_for_criterion(self, criterion_id: str) -> str:
        if criterion_id == "final-hardware-safety-media-evidence":
            return "safety-maintainer"
        if criterion_id == "final-live-network-transfer-evidence":
            return "network-security-maintainer"
        if criterion_id in {"final-release-artifact-signing-evidence", "final-reference-demotion-allowed"}:
            return "release-maintainer"
        return "cutover-maintainer"

    def complete_maintainer_input(self, root: Path) -> dict[str, object]:
        phase18_contract = self.read_json(root, PHASE18_CONTRACT)
        retained_rows = []
        for packet in phase18_contract["retained_code_acceptance_packets"]:
            retained_rows.append(
                {
                    "packet_id": packet["id"],
                    "decision": "approve",
                    "approver": "phase27-test-maintainer",
                    "approver_role": packet["approver_role"],
                    "decision_timestamp": "2026-06-25T01:45:00Z",
                    "rationale": "Maintainer reviewed the retained-code packet evidence and residual risk.",
                    "evidence_refs": list(packet["required_evidence_refs"]),
                    "residual_risk": "Residual risk accepted for Phase 27 test input.",
                    "redaction_summary": "name-only references; redaction checks passed",
                    "hard_failure_reasons": [],
                    "exception": {},
                }
            )
        final_rows = []
        for requirement in phase18_contract["upstream_result_requirements"]:
            criterion_id = str(requirement["criterion_id"])
            status = "blocked" if criterion_id == "final-reference-demotion-allowed" else "passed"
            decision = "reject" if criterion_id == "final-reference-demotion-allowed" else "approve"
            final_rows.append(
                {
                    "decision_id": f"phase27-final-readiness-{criterion_id}",
                    "criterion_id": criterion_id,
                    "decision": decision,
                    "status": status,
                    "approver": "phase27-test-maintainer",
                    "approver_role": self.final_role_for_criterion(criterion_id),
                    "decision_timestamp": "2026-06-25T01:45:00Z",
                    "rationale": "Maintainer reviewed the upstream criterion evidence for Phase 27.",
                    "evidence_refs": list(requirement["required_manifest_refs"]),
                    "residual_risk": "Residual risk accepted for Phase 27 test input.",
                    "exception": {},
                    "redaction_summary": "name-only references; redaction checks passed",
                    "hard_failure_reasons": [],
                }
            )
        return {
            "schema_version": "1",
            "phase": "27-retained-code-and-maintainer-acceptance-decisions",
            "phase_lifecycle_id": "27-2026-06-25T01-06-06",
            "retained_code_decisions": retained_rows,
            "final_readiness_decisions": final_rows,
            "reference_demotion_decision": {
                "demotion_authorization": "blocked",
                "phase27_may_authorize_demotion": False,
            },
        }

    def write_maintainer_input(self, root: Path, data: dict[str, object], path: str = "phase27-maintainer-input.json") -> str:
        self.write_json(root, path, data)
        return path

    def test_contract_only_exact_matches_phase18_canonical_surfaces(self) -> None:
        # Arrange
        module = self.load_verifier_module()
        phase18_contract = self.read_json(ROOT, PHASE18_CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])
        surfaces = module.check_phase18_surfaces(phase18_contract)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(surfaces["retained_packet_ids"], REQUIRED_RETAINED_PACKET_IDS)
        self.assertEqual(surfaces["upstream_criterion_ids"], REQUIRED_UPSTREAM_CRITERION_IDS)
        self.assertEqual(
            surfaces["retained_required_fields"],
            phase18_contract["retained_code_acceptance_packet_schema"]["required_fields"],
        )
        self.assertEqual(
            surfaces["final_decision_required_fields"],
            phase18_contract["final_decision_schema"]["required_fields"],
        )
        self.assertEqual(
            surfaces["exception_required_fields"],
            phase18_contract["final_decision_schema"]["exception"]["required_fields"],
        )
        self.assertEqual(surfaces["retained_packet_status_vocabulary"], phase18_contract["retained_packet_status_vocabulary"])
        self.assertEqual(surfaces["final_criterion_status_vocabulary"], phase18_contract["final_criterion_status_vocabulary"])
        self.assertEqual(surfaces["review_decision_vocabulary"], phase18_contract["review_decision_vocabulary"])
        self.assertEqual(
            surfaces["hard_blocker_reasons"],
            phase18_contract["upstream_result_requirements"][0]["hard_blocker_reasons"],
        )

    def test_contract_declares_exact_decision_axes(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(contract["decision_axes"], DECISION_AXES)

    def test_contract_declares_generated_artifacts(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)

    def test_contract_keeps_phase27_demotion_authorization_blocked(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        handoff_policy = contract["phase28_handoff_policy"]
        self.assertEqual(handoff_policy["demotion_authorization"], "blocked")
        self.assertFalse(handoff_policy["phase27_may_authorize_demotion"])

    def test_contract_only_rejects_decision_axis_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["decision_axes"] = [axis for axis in contract["decision_axes"] if axis != "hard_failure_state"]
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_axes", result.stdout)

    def test_security_only_rejects_forbidden_contract_fields(self) -> None:
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

    def test_verifier_does_not_use_shell_or_inline_interpreters(self) -> None:
        # Arrange
        source = VERIFIER.read_text(encoding="utf-8")

        # Act / Assert
        for forbidden in ["shell=True", "bash -c", "python -c", "node -e"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_quick_generates_template_and_all_expected_artifacts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for artifact in GENERATED_ARTIFACTS:
                self.assertTrue((root / DEFAULT_OUTPUT_DIR / artifact).exists(), artifact)
            template = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/maintainer-acceptance-input-template.json")
            self.assertEqual(len(template["retained_code_decisions"]), len(REQUIRED_RETAINED_PACKET_IDS))
            self.assertEqual(len(template["final_readiness_decisions"]), len(REQUIRED_UPSTREAM_CRITERION_IDS))
            decision_table = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/decision-row-table.json")
            self.assertEqual(len(decision_table["rows"]), len(REQUIRED_RETAINED_PACKET_IDS) + len(REQUIRED_UPSTREAM_CRITERION_IDS))
            handoff = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/phase28-handoff-manifest.json")
            self.assertEqual(handoff["demotion_authorization"], "blocked")
            self.assertFalse(handoff["phase27_may_authorize_demotion"])
            self.assertNotIn("demotion_allowed", json.dumps(handoff))

    def test_quick_normalizes_approve_reject_and_exception_decisions(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            retained_rows = maintainer_input["retained_code_decisions"]
            retained_rows[1]["decision"] = "reject"
            retained_rows[1]["rationale"] = "Maintainer rejected this retained-code packet for Phase 27 test input."
            retained_rows[2]["decision"] = "exception"
            retained_rows[2]["exception"] = {
                "scope": "phase27 test exception scope",
                "rationale": "Temporary exception is explicitly documented for maintainer review.",
                "approver": "phase27-test-maintainer",
                "approver_role": retained_rows[2]["approver_role"],
                "affected_printer_or_release_surface": "print core retained packet",
                "mitigation_or_follow_up": "Track exception in Phase 28 readiness review.",
                "expiry_or_review_trigger": "Phase 28 reference-demotion decision",
                "evidence_refs": retained_rows[2]["evidence_refs"],
                "residual_risk": "Exception residual risk accepted for test input.",
            }
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(["--quick", "--maintainer-input", input_path], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            normalized = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/normalized-retained-code-decisions.json")
            by_id = {row["packet_id"]: row for row in normalized["rows"]}
            self.assertEqual(by_id["packet-hal-cmsis-startup-asm"]["status"], "accepted")
            self.assertEqual(by_id["packet-freertos-runtime"]["status"], "rejected")
            self.assertEqual(by_id["packet-marlin-cpp-print-core-oracle"]["status"], "deferred-approved-exception")
            exceptions = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/exception-decision-register.json")
            self.assertEqual(len(exceptions["rows"]), 1)
            self.assertEqual(exceptions["rows"][0]["owner"], "phase27-test-maintainer")

    def test_final_decision_required_fields_include_decision_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            del maintainer_input["final_readiness_decisions"][0]["decision_id"]
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_id", result.stdout)

    def test_duplicate_final_decision_ids_are_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            duplicate = maintainer_input["final_readiness_decisions"][0]["decision_id"]
            maintainer_input["final_readiness_decisions"][1]["decision_id"] = duplicate
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate decision_id", result.stdout)

    def test_sensitive_role_mismatch_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            network_row = next(row for row in maintainer_input["retained_code_decisions"] if row["packet_id"] == "packet-network-lwip-mbedtls-wui")
            network_row["approver_role"] = "release-maintainer"
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sensitive_role_policy", result.stdout)

    def test_hard_blocker_runs_before_exception_handling(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            retained_row = maintainer_input["retained_code_decisions"][0]
            retained_row["decision"] = "exception"
            retained_row["hard_failure_reasons"] = ["redaction-failed"]
            retained_row["exception"] = {
                "scope": "phase27 test exception scope",
                "rationale": "Exception would otherwise be valid, but hard blockers win.",
                "approver": "phase27-test-maintainer",
                "approver_role": retained_row["approver_role"],
                "affected_printer_or_release_surface": "startup retained packet",
                "mitigation_or_follow_up": "Fix redaction first.",
                "expiry_or_review_trigger": "redaction pass",
                "evidence_refs": retained_row["evidence_refs"],
                "residual_risk": "Residual risk cannot be accepted while redaction is blocked.",
                "owner": "phase27-test-maintainer",
            }
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(["--quick", "--maintainer-input", input_path], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            normalized = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/normalized-retained-code-decisions.json")
            first_row = normalized["rows"][0]
            self.assertEqual(first_row["status"], "rejected-redaction")
            self.assertEqual(first_row["exception_state"], "blocked-by-hard-failure")

    def test_missing_phase26_row_table_reports_generation_command(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase26_release_signing_upstream_evidence.py --quick", result.stdout)

    def test_output_root_symlink_escape_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
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

    def test_security_scan_rejects_no_demotion_output_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            handoff = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/phase28-handoff-manifest.json")
            handoff["demotion_allowed"] = True
            self.write_json(root, f"{DEFAULT_OUTPUT_DIR}/phase28-handoff-manifest.json", handoff)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("demotion_allowed", result.stdout)


if __name__ == "__main__":
    unittest.main()
