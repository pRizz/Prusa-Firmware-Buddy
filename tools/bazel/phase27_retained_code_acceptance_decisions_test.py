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


if __name__ == "__main__":
    unittest.main()
