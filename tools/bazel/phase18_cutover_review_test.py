#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase18_cutover_review.py"
CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
SOURCE_REF_FILES = [
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/foreign_code_inventory.json",
    "tools/bazel/manifests/unsafe_boundary_audit.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json",
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json",
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json",
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json",
]
WIRING_FILES = [
    "tools/bazel/BUILD.bazel",
    "BUILD.bazel",
    "tools/bazel/rust_workflow.sh",
    "justfile",
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
REQUIRED_FINAL_CRITERION_IDS = [
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
REQUIRED_FINAL_EVIDENCE_FAMILIES = [
    "ci",
    "simulator",
    "hardware",
    "live-service",
    "release",
    "retained-code",
    "residual-risk",
    "maintainer-decision",
]


class Phase18CutoverReviewTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase18_cutover_review.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase18_cutover_review.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_file(self, root: Path, path: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, full_path)

    def copy_source_ref_inputs(self, root: Path) -> None:
        for path in SOURCE_REF_FILES:
            self.copy_file(root, path)

    def copy_complete_surface(self, root: Path) -> None:
        self.copy_file(root, CONTRACT)
        self.copy_source_ref_inputs(root)

    def copy_wiring_files(self, root: Path) -> None:
        for path in WIRING_FILES:
            self.copy_file(root, path)

    def read_contract(self, root: Path) -> dict[str, object]:
        return json.loads((root / CONTRACT).read_text(encoding="utf-8"))

    def write_contract(self, root: Path, contract: dict[str, object]) -> None:
        self.write_file(root, CONTRACT, json.dumps(contract, indent=2, sort_keys=True) + "\n")

    def write_json(self, root: Path, path: str, data: dict[str, object]) -> None:
        self.write_file(root, path, json.dumps(data, indent=2, sort_keys=True) + "\n")

    def source_ids(self, path: str, collection: str, key: str) -> list[str]:
        data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        return [row[key] for row in data[collection]]

    def read_json(self, root: Path, path: str) -> dict[str, object]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    def complete_decision_input(self, root: Path, status: str = "passed", decision: str = "approve") -> dict[str, object]:
        contract = self.read_contract(root)
        exception = {
            "scope": "phase18-final-review",
            "rationale": "Exception metadata is complete for test coverage.",
            "approver": "release-maintainer",
            "approver_role": "release-maintainer",
            "affected_printer_or_release_surface": "all-supported-release-surfaces",
            "mitigation_or_follow_up": "Review at release cutover checkpoint.",
            "expiry_or_review_trigger": "before-reference-demotion",
            "evidence_refs": ["external://phase18/exception-evidence"],
        }
        retained_reviews = []
        for packet in contract["retained_code_acceptance_packets"]:
            retained_reviews.append(
                {
                    "packet_id": packet["id"],
                    "status": "accepted",
                    "approver": "release-maintainer",
                    "approver_role": packet["approver_role"],
                    "decision_timestamp": "2026-06-20T15:30:00Z",
                    "rationale": f"Reviewed retained packet {packet['id']}.",
                    "supplied_evidence_result_refs": [
                        f"external://phase18/retained/{packet['id']}",
                    ],
                    "residual_risk": "Reviewed and accepted for test decision input.",
                    "blocker_or_deferred_action": "none",
                    "exception_ref": "none",
                    "redaction_summary": "No sensitive material included.",
                }
            )
        final_decisions = []
        for criterion in contract["final_demotion_criteria"]:
            final_decisions.append(
                {
                    "decision_id": f"decision-{criterion['id']}",
                    "criterion_id": criterion["id"],
                    "decision": decision,
                    "status": status,
                    "approver": "release-maintainer",
                    "approver_role": "release-maintainer",
                    "decision_timestamp": "2026-06-20T15:30:00Z",
                    "rationale": f"Reviewed final criterion {criterion['id']}.",
                    "evidence_refs": [
                        f"external://phase18/final/{criterion['id']}",
                    ],
                    "residual_risk": "Reviewed and accepted for test decision input.",
                    "exception": exception,
                    "redaction_summary": "No sensitive material included.",
                }
            )
        return {
            "decision_packet": {
                "phase": "18-retained-code-acceptance-and-cutover-review",
                "phase_lifecycle_id": "18-2026-06-20T14-27-15",
            },
            "retained_code_reviews": retained_reviews,
            "final_criterion_decisions": final_decisions,
        }

    def test_contract_accepts_complete_phase18_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_requires_all_retained_packet_ids(self) -> None:
        for packet_id in REQUIRED_RETAINED_PACKET_IDS:
            with self.subTest(packet_id=packet_id):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract["retained_code_acceptance_packets"] = [
                        packet for packet in contract["retained_code_acceptance_packets"] if packet["id"] != packet_id
                    ]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(packet_id, result.stdout)

    def test_contract_requires_retained_surface_coverage(self) -> None:
        cases = [
            (
                "tools/bazel/manifests/phase11_retained_code_justifications.json",
                "retained_code_justifications",
                "id",
            ),
            ("tools/bazel/manifests/foreign_code_inventory.json", "components", "id"),
            ("tools/bazel/manifests/unsafe_boundary_audit.json", "surfaces", "surface_id"),
        ]
        for path, collection, key in cases:
            for row_id in self.source_ids(path, collection, key):
                source_ref = f"{path}#{row_id}"
                with self.subTest(source_ref=source_ref):
                    # Arrange
                    temp_dir, root = self.make_temp_root()
                    with temp_dir:
                        self.copy_complete_surface(root)
                        contract = self.read_contract(root)
                        for packet in contract["retained_code_acceptance_packets"]:
                            packet["retained_source_refs"] = [
                                ref for ref in packet.get("retained_source_refs", []) if ref != source_ref
                            ]
                        mappings = contract.get("coverage_mappings", {})
                        if isinstance(mappings, dict):
                            mappings.pop(source_ref, None)
                        self.write_contract(root, contract)

                        # Act
                        result = self.run_verifier(["--contract-only"], maybe_root=root)

                    # Assert
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(source_ref, result.stdout)

    def test_contract_requires_final_evidence_family_coverage(self) -> None:
        for family in REQUIRED_FINAL_EVIDENCE_FAMILIES:
            with self.subTest(family=family):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract["final_demotion_criteria"] = [
                        row for row in contract["final_demotion_criteria"] if row["evidence_family"] != family
                    ]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(family, result.stdout)

    def test_contract_rejects_unknown_retained_packet_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["retained_code_acceptance_packets"][0]["status"] = "almost-accepted"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("almost-accepted", result.stdout)

    def test_contract_rejects_unknown_final_criterion_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["final_demotion_criteria"][0]["default_status"] = "almost-passed"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("almost-passed", result.stdout)

    def test_contract_requires_rev_requirement_coverage_on_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["retained_code_acceptance_packets"][0]["requirement_ids"] = []
            contract["final_demotion_criteria"][0]["requirement_ids"] = []
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("REV-", result.stdout)

    def test_contract_rejects_unresolved_source_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["final_demotion_criteria"][0]["source_refs"] = [
                "tools/bazel/manifests/phase13_ci_evidence_contract.json#missing-row",
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing-row", result.stdout)

    def test_quick_without_decision_input_writes_artifacts_and_blocks_demotion(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for path in [
                "build/ci-evidence/phase18/run-manifest.json",
                "build/ci-evidence/phase18/normalized-final-demotion-results.json",
                "build/ci-evidence/phase18/retained-code-acceptance-summary.json",
                "build/ci-evidence/phase18/residual-risk-register.json",
                "build/ci-evidence/phase18/redacted-readiness-report.md",
                "build/ci-evidence/phase18/source-contract-snapshots/phase18_cutover_review_contract.json",
                "build/ci-evidence/phase18/maintainer-decision-input-template.json",
            ]:
                self.assertTrue((root / path).exists(), path)
            run_manifest = self.read_json(root, "build/ci-evidence/phase18/run-manifest.json")
            self.assertFalse(run_manifest["decision_inputs_supplied"])
            self.assertFalse(run_manifest["demotion_allowed"])

    def test_quick_custom_output_dir_uses_matching_manifest_paths_and_security_scan(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        custom_output = "build/ci-evidence/phase18/custom"
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            quick_result = self.run_verifier(["--quick", "--output-dir", custom_output], maybe_root=root)

            # Assert
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(root, f"{custom_output}/run-manifest.json")
            self.assertEqual(run_manifest["output_root"], custom_output)
            self.assertEqual(
                run_manifest["source_contract_snapshot_path"],
                f"{custom_output}/source-contract-snapshots/phase18_cutover_review_contract.json",
            )
            self.assertIn(f"{custom_output}/run-manifest.json", run_manifest["generated_artifacts"])

            # Act
            run_manifest["demotion_allowed"] = True
            self.write_json(root, f"{custom_output}/run-manifest.json", run_manifest)
            security_result = self.run_verifier(["--security-only", "--output-dir", custom_output], maybe_root=root)

        # Assert
        self.assertNotEqual(security_result.returncode, 0)
        self.assertIn("demotion_allowed", security_result.stdout)

    def test_decision_input_requires_complete_final_approval_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            del decision_input["final_criterion_decisions"][0]["approver"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approver", result.stdout)

    def test_decision_input_requires_decision_packet(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            del decision_input["decision_packet"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_packet", result.stdout)

    def test_decision_input_requires_current_phase(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["decision_packet"]["phase"] = "17-release-candidate-evidence"
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_packet phase", result.stdout)

    def test_decision_input_requires_current_phase_lifecycle_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["decision_packet"]["phase_lifecycle_id"] = "18-stale-lifecycle"
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_packet phase_lifecycle_id", result.stdout)

    def test_exception_approved_requires_complete_exception_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root, status="exception-approved", decision="exception")
            del decision_input["final_criterion_decisions"][0]["exception"]["scope"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scope", result.stdout)

    def test_passed_final_decision_rejects_reject_decision_with_empty_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["final_criterion_decisions"][0]["decision"] = "reject"
            decision_input["final_criterion_decisions"][0]["status"] = "passed"
            decision_input["final_criterion_decisions"][0]["evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status passed requires decision approve", result.stdout)

    def test_passed_final_decision_requires_evidence_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["final_criterion_decisions"][0]["evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence_refs must include at least one Phase 18 evidence ref", result.stdout)

    def test_exception_approved_final_decision_requires_evidence_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root, status="exception-approved", decision="exception")
            decision_input["final_criterion_decisions"][0]["evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence_refs must include at least one Phase 18 evidence ref", result.stdout)

    def test_not_applicable_final_decision_requires_evidence_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root, status="not-applicable", decision="exception")
            decision_input["final_criterion_decisions"][0]["evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence_refs must include at least one Phase 18 evidence ref", result.stdout)

    def test_exception_metadata_requires_evidence_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root, status="exception-approved", decision="exception")
            decision_input["final_criterion_decisions"][0]["exception"]["evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exception evidence_refs must include at least one Phase 18 evidence ref", result.stdout)

    def test_final_decision_requires_string_decision_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["final_criterion_decisions"][0]["decision_id"] = 123
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_id must be a non-empty string", result.stdout)

    def test_final_decision_rejects_duplicate_decision_ids(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["final_criterion_decisions"][1]["decision_id"] = decision_input["final_criterion_decisions"][0][
                "decision_id"
            ]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate final decision id", result.stdout)

    def test_exception_approved_final_decision_rejects_non_string_exception_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root, status="exception-approved", decision="exception")
            decision_input["final_criterion_decisions"][0]["exception"]["scope"] = ["phase18-final-review"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exception scope must be a non-empty string", result.stdout)

    def test_demotion_allowed_only_when_all_final_criteria_have_allowed_statuses(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            run_manifest = self.read_json(root, "build/ci-evidence/phase18/run-manifest.json")
            self.assertTrue(run_manifest["decision_inputs_supplied"])
            self.assertTrue(run_manifest["demotion_allowed"])

    def test_blocking_final_criterion_statuses_keep_demotion_false(self) -> None:
        for status in [
            "pending",
            "failed",
            "blocked",
            "exception-requested",
            "exception-rejected",
            "rejected-redaction",
            "rejected-overclaim",
        ]:
            with self.subTest(status=status):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    decision_input["final_criterion_decisions"][0]["status"] = status
                    self.write_json(root, "decision-input.json", decision_input)

                    # Act
                    result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

                    # Assert
                    self.assertEqual(result.returncode, 0, result.stdout)
                    run_manifest = self.read_json(root, "build/ci-evidence/phase18/run-manifest.json")
                    self.assertFalse(run_manifest["demotion_allowed"])

    def test_retained_packet_acceptance_requires_supplied_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["retained_code_reviews"][0]["supplied_evidence_result_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("supplied_evidence_result_refs", result.stdout)

    def test_deferred_approved_exception_retained_review_requires_supplied_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["retained_code_reviews"][0]["status"] = "deferred-approved-exception"
            decision_input["retained_code_reviews"][0]["supplied_evidence_result_refs"] = []
            decision_input["retained_code_reviews"][0]["exception_ref"] = "phase18-retained-exception"
            decision_input["retained_code_reviews"][0]["blocker_or_deferred_action"] = "Review exception before demotion."
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("supplied_evidence_result_refs must include at least one Phase 18 evidence ref", result.stdout)

    def test_retained_packet_acceptance_requires_contract_approver_role(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["retained_code_reviews"][0]["approver_role"] = "wrong-role"
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approver_role must be", result.stdout)

    def test_decision_input_rejects_paths_outside_phase18_output_or_external_refs(self) -> None:
        cases = ["/tmp/phase18-evidence.json", "../phase18-evidence.json", "build/ci-evidence/phase17/result.json"]
        for evidence_ref in cases:
            with self.subTest(evidence_ref=evidence_ref):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    decision_input["final_criterion_decisions"][0]["evidence_refs"] = [evidence_ref]
                    self.write_json(root, "decision-input.json", decision_input)

                    # Act
                    result = self.run_verifier(["--quick", "--decision-input", "decision-input.json"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(evidence_ref, result.stdout)

    def test_security_only_rejects_forbidden_contract_input_and_generated_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["private_key"] = "redacted-test-value"
            self.write_contract(root, contract)

            # Act
            contract_result = self.run_verifier(["--security-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(contract_result.returncode, 0)
            self.assertIn("private_key", contract_result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["password"] = "redacted-test-value"
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            input_result = self.run_verifier(["--security-only", "--decision-input", "decision-input.json"], maybe_root=root)

            # Assert
            self.assertNotEqual(input_result.returncode, 0)
            self.assertIn("password", input_result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            self.write_file(
                root,
                "build/ci-evidence/phase18/redacted-readiness-report.md",
                "raw crash dump",
            )

            # Act
            generated_result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(generated_result.returncode, 0)
        self.assertIn("raw crash dump", generated_result.stdout)

    def test_generated_report_names_review_material_boundary(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            report = (root / "build/ci-evidence/phase18/redacted-readiness-report.md").read_text(encoding="utf-8")
            self.assertIn(
                "Review material only; machine-readable gate rows and maintainer decision input determine final status.",
                report,
            )
            self.assertIn("demotion_allowed: false", report)

    def test_security_only_rejects_generated_local_proof_and_retained_acceptance_overclaims(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["demotion_allowed"] = True
            self.write_json(root, "build/ci-evidence/phase18/run-manifest.json", run_manifest)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("demotion_allowed", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            normalized = self.read_json(root, "build/ci-evidence/phase18/normalized-final-demotion-results.json")
            normalized["results"][0]["status"] = "passed"
            self.write_json(root, "build/ci-evidence/phase18/normalized-final-demotion-results.json", normalized)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("passed", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            summary = self.read_json(root, "build/ci-evidence/phase18/retained-code-acceptance-summary.json")
            summary["packets"][0]["status"] = "accepted"
            self.write_json(root, "build/ci-evidence/phase18/retained-code-acceptance-summary.json", summary)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("accepted", result.stdout)

    def test_security_only_rejects_non_boolean_generated_decision_input_flag(self) -> None:
        for value in ["false", None]:
            with self.subTest(value=value):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    quick_result = self.run_verifier(["--quick"], maybe_root=root)
                    self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
                    run_manifest = self.read_json(root, "build/ci-evidence/phase18/run-manifest.json")
                    if value is None:
                        del run_manifest["decision_inputs_supplied"]
                    else:
                        run_manifest["decision_inputs_supplied"] = value
                    run_manifest["demotion_allowed"] = True
                    self.write_json(root, "build/ci-evidence/phase18/run-manifest.json", run_manifest)

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("decision_inputs_supplied must be boolean", result.stdout)

    def test_security_only_rejects_generated_decision_input_claim_without_validated_input(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["decision_inputs_supplied"] = True
            run_manifest["demotion_allowed"] = True
            self.write_json(root, "build/ci-evidence/phase18/run-manifest.json", run_manifest)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("claims decision input without validated --decision-input", result.stdout)

    def test_security_only_rejects_normalized_top_level_demotion_overclaim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            normalized = self.read_json(root, "build/ci-evidence/phase18/normalized-final-demotion-results.json")
            normalized["demotion_allowed"] = True
            self.write_json(root, "build/ci-evidence/phase18/normalized-final-demotion-results.json", normalized)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("normalized-final-demotion-results.json cannot set demotion_allowed true", result.stdout)

    def test_verifier_does_not_use_shell_or_inline_interpreters(self) -> None:
        # Arrange
        source = VERIFIER.read_text(encoding="utf-8")

        # Act / Assert
        for forbidden in ["shell=True", "bash -c", "python -c", "node -e"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_wiring_only_accepts_complete_phase18_wiring(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.copy_wiring_files(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_only_rejects_missing_phase18_entries(self) -> None:
        cases = [
            ("tools/bazel/BUILD.bazel", 'name = "phase18_source_ref_manifests"'),
            ("tools/bazel/BUILD.bazel", "manifests/phase18_cutover_review_contract.json"),
            ("BUILD.bazel", 'name = "phase18_cutover_review_docs"'),
            ("BUILD.bazel", 'name = "phase18_verify_tests"'),
            ("tools/bazel/rust_workflow.sh", "phase18_verify)"),
            ("tools/bazel/rust_workflow.sh", "python3 tools/bazel/phase18_cutover_review.py --quick"),
            ("justfile", "phase18-verify:"),
            ("justfile", "bazel run //tools/bazel:phase18_verify_tests"),
        ]
        for path, required_text in cases:
            with self.subTest(path=path, required_text=required_text):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.copy_wiring_files(root)
                    target = root / path
                    target.write_text(target.read_text(encoding="utf-8").replace(required_text, ""), encoding="utf-8")

                    # Act
                    result = self.run_verifier(["--wiring-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(required_text, result.stdout)

    def test_just_phase18_verify_runs_tests_before_verifier(self) -> None:
        # Arrange
        justfile = (ROOT / "justfile").read_text(encoding="utf-8")

        # Act
        recipe_index = justfile.find("phase18-verify:")
        tests_index = justfile.find("\n    bazel run //tools/bazel:phase18_verify_tests\n", recipe_index)
        verify_index = justfile.find("\n    bazel run //tools/bazel:phase18_verify\n", recipe_index)

        # Assert
        self.assertNotEqual(recipe_index, -1)
        self.assertNotEqual(tests_index, -1)
        self.assertNotEqual(verify_index, -1)
        self.assertLess(tests_index, verify_index)


if __name__ == "__main__":
    unittest.main()
