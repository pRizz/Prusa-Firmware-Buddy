#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from phase18_cutover_review_failure_test import Phase18CutoverReviewFailureTests
from phase18_cutover_review_security_test import Phase18CutoverReviewSecurityTests
from phase18_cutover_review_upstream_failure_test import Phase18CutoverReviewUpstreamFailureTests
from phase18_cutover_review_wiring_test import Phase18CutoverReviewWiringTests

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


class Phase18CutoverReviewTest(
        Phase18CutoverReviewFailureTests,
        Phase18CutoverReviewSecurityTests,
        Phase18CutoverReviewUpstreamFailureTests,
        Phase18CutoverReviewWiringTests,
        unittest.TestCase,
):

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
        phase_modules = [
            "phase18_cutover_artifacts.py",
            "phase18_cutover_contract.py",
            "phase18_cutover_policy.py",
            "phase18_cutover_review.py",
            "phase18_cutover_security.py",
            "phase18_cutover_source_refs.py",
            "phase18_cutover_upstream_policy.py",
            "phase18_cutover_validation.py",
        ]
        for module_name in phase_modules:
            source = ROOT / "tools/bazel" / module_name
            if source.exists():
                shutil.copy2(source, root / "tools/bazel" / module_name)
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
        self.write_file(root, CONTRACT,
                        json.dumps(contract, indent=2, sort_keys=True) + "\n")

    def write_json(self, root: Path, path: str, data: dict[str,
                                                           object]) -> None:
        self.write_file(root, path,
                        json.dumps(data, indent=2, sort_keys=True) + "\n")

    def source_ids(self, path: str, collection: str, key: str) -> list[str]:
        data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        return [row[key] for row in data[collection]]

    def read_json(self, root: Path, path: str) -> dict[str, object]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    def complete_decision_input(
            self,
            root: Path,
            status: str = "passed",
            decision: str = "approve") -> dict[str, object]:
        contract = self.read_contract(root)
        exception = {
            "scope": "phase18-final-review",
            "rationale": "Exception metadata is complete for test coverage.",
            "approver": "release-maintainer",
            "approver_role": "release-maintainer",
            "affected_printer_or_release_surface":
            "all-supported-release-surfaces",
            "mitigation_or_follow_up": "Review at release cutover checkpoint.",
            "expiry_or_review_trigger": "before-reference-demotion",
            "evidence_refs": ["external://phase18/exception-evidence"],
        }
        retained_reviews = []
        for packet in contract["retained_code_acceptance_packets"]:
            retained_reviews.append({
                "packet_id":
                packet["id"],
                "status":
                "accepted",
                "approver":
                "release-maintainer",
                "approver_role":
                packet["approver_role"],
                "decision_timestamp":
                "2026-06-20T15:30:00Z",
                "rationale":
                f"Reviewed retained packet {packet['id']}.",
                "supplied_evidence_result_refs": [
                    f"external://phase18/retained/{packet['id']}",
                ],
                "residual_risk":
                "Reviewed and accepted for test decision input.",
                "blocker_or_deferred_action":
                "none",
                "exception_ref":
                "none",
                "redaction_summary":
                "No sensitive material included.",
            })
        final_decisions = []
        for criterion in contract["final_demotion_criteria"]:
            final_decisions.append({
                "decision_id":
                f"decision-{criterion['id']}",
                "criterion_id":
                criterion["id"],
                "decision":
                decision,
                "status":
                status,
                "approver":
                "release-maintainer",
                "approver_role":
                "release-maintainer",
                "decision_timestamp":
                "2026-06-20T15:30:00Z",
                "rationale":
                f"Reviewed final criterion {criterion['id']}.",
                "evidence_refs": [
                    f"external://phase18/final/{criterion['id']}",
                ],
                "residual_risk":
                "Reviewed and accepted for test decision input.",
                "exception":
                exception,
                "redaction_summary":
                "No sensitive material included.",
            })
        return {
            "decision_packet": {
                "phase": "18-retained-code-acceptance-and-cutover-review",
                "phase_lifecycle_id": "18-2026-06-20T14-27-15",
            },
            "retained_code_reviews": retained_reviews,
            "final_criterion_decisions": final_decisions,
        }

    def complete_upstream_results(self,
                                  root: Path,
                                  status: str = "passed") -> dict[str, object]:
        contract = self.read_contract(root)
        rows = []
        for requirement in contract["upstream_result_requirements"]:
            if not requirement["result_required"]:
                continue
            failure_reason = "none" if status == "passed" else f"{status} injected by test fixture"
            rows.append({
                "criterion_id":
                requirement["criterion_id"],
                "evidence_family":
                requirement["evidence_family"],
                "owning_phase":
                requirement["source_phase"],
                "source_lifecycle_id":
                requirement["source_lifecycle_id"],
                "manifest_path":
                requirement["required_manifest_refs"][0],
                "status":
                status,
                "failure_reason":
                failure_reason,
                "artifact_refs": [requirement["required_manifest_refs"][0]],
                "redaction_status":
                "passed",
                "source_ref_status":
                "passed",
                "generated_at_utc":
                "2026-06-21T16:30:00Z",
                "requirement_ids":
                requirement["requirement_ids"],
            })
        return {
            "upstream_result_packet": {
                "phase": "18-retained-code-acceptance-and-cutover-review",
                "phase_lifecycle_id": "18-2026-06-20T14-27-15",
            },
            "upstream_results": rows,
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
                        packet for packet in
                        contract["retained_code_acceptance_packets"]
                        if packet["id"] != packet_id
                    ]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"],
                                               maybe_root=root)

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
            ("tools/bazel/manifests/foreign_code_inventory.json", "components",
             "id"),
            ("tools/bazel/manifests/unsafe_boundary_audit.json", "surfaces",
             "surface_id"),
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
                        for packet in contract[
                                "retained_code_acceptance_packets"]:
                            packet["retained_source_refs"] = [
                                ref for ref in packet.get(
                                    "retained_source_refs", [])
                                if ref != source_ref
                            ]
                        mappings = contract.get("coverage_mappings", {})
                        if isinstance(mappings, dict):
                            mappings.pop(source_ref, None)
                        self.write_contract(root, contract)

                        # Act
                        result = self.run_verifier(["--contract-only"],
                                                   maybe_root=root)

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
                        row for row in contract["final_demotion_criteria"]
                        if row["evidence_family"] != family
                    ]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(family, result.stdout)

    def test_contract_rejects_unknown_retained_packet_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["retained_code_acceptance_packets"][0][
                "status"] = "almost-accepted"
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
            contract["final_demotion_criteria"][0][
                "default_status"] = "almost-passed"
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
            contract["retained_code_acceptance_packets"][0][
                "requirement_ids"] = []
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

    def test_contract_rejects_extra_generated_artifacts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["generated_artifacts"].append(
                "unexpected-extra-output.json")
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected generated artifact", result.stdout)

    def test_contract_requires_upstream_result_requirements_for_final_criteria(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            removed = contract["upstream_result_requirements"][0][
                "criterion_id"]
            contract["upstream_result_requirements"] = [
                row for row in contract["upstream_result_requirements"]
                if row["criterion_id"] != removed
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(removed, result.stdout)

    def test_contract_requires_upstream_result_consumption_artifact(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["generated_artifacts"] = [
                artifact for artifact in contract["generated_artifacts"]
                if artifact != "upstream-result-consumption.json"
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("upstream-result-consumption.json", result.stdout)

    def test_contract_rejects_wrong_upstream_source_lifecycle_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["upstream_result_requirements"][0][
                "source_lifecycle_id"] = "19-stale-lifecycle"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source_lifecycle_id", result.stdout)

    def test_quick_without_decision_input_writes_artifacts_and_blocks_demotion(
            self) -> None:
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
                    "build/ci-evidence/phase18/upstream-result-consumption.json",
                    "build/ci-evidence/phase18/retained-code-acceptance-summary.json",
                    "build/ci-evidence/phase18/residual-risk-register.json",
                    "build/ci-evidence/phase18/redacted-readiness-report.md",
                    "build/ci-evidence/phase18/source-contract-snapshots/phase18_cutover_review_contract.json",
                    "build/ci-evidence/phase18/maintainer-decision-input-template.json",
            ]:
                self.assertTrue((root / path).exists(), path)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            self.assertFalse(run_manifest["decision_inputs_supplied"])
            self.assertFalse(run_manifest["upstream_results_supplied"])
            self.assertFalse(run_manifest["demotion_allowed"])
            self.assertEqual(run_manifest["upstream_result_status_counts"], {
                "missing": 6,
                "not-required": 3
            })

    def test_quick_custom_output_dir_uses_matching_manifest_paths_and_security_scan(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        custom_output = "build/ci-evidence/phase18/custom"
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            quick_result = self.run_verifier(
                ["--quick", "--output-dir", custom_output], maybe_root=root)

            # Assert
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(
                root, f"{custom_output}/run-manifest.json")
            self.assertEqual(run_manifest["output_root"], custom_output)
            self.assertEqual(
                run_manifest["source_contract_snapshot_path"],
                f"{custom_output}/source-contract-snapshots/phase18_cutover_review_contract.json",
            )
            self.assertIn(f"{custom_output}/run-manifest.json",
                          run_manifest["generated_artifacts"])

            # Act
            run_manifest["demotion_allowed"] = True
            self.write_json(root, f"{custom_output}/run-manifest.json",
                            run_manifest)
            security_result = self.run_verifier(
                ["--security-only", "--output-dir", custom_output],
                maybe_root=root)

        # Assert
        self.assertNotEqual(security_result.returncode, 0)
        self.assertIn("demotion_allowed", security_result.stdout)


if __name__ == "__main__":
    unittest.main()
