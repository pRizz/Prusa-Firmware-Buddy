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

from phase32_blocker_normalization import (
    canonical_row_id,
    canonical_source_identity,
)

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase32_blocker_register_triage.py"
NORMALIZATION = ROOT / "tools/bazel/phase32_blocker_normalization.py"
CONTRACT = ROOT / "tools/bazel/manifests/phase32_blocker_register_triage_contract.json"
TRIAGE_MODULES = [
    "tools/bazel/phase32_triage_contract.py",
    "tools/bazel/phase32_triage_policy.py",
    "tools/bazel/phase32_phase31_adapter.py",
    "tools/bazel/phase32_phase27_adapter.py",
    "tools/bazel/phase32_phase28_adapter.py",
]
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
    "tools/bazel/phase26_release_contract.py",
    "tools/bazel/phase26_release_policy.py",
    "tools/bazel/phase26_release_signing_upstream_evidence.py",
    "tools/bazel/phase26_upstream_policy.py",
    "tools/bazel/phase27_decision_contract.py",
    "tools/bazel/phase27_decision_normalization.py",
    "tools/bazel/phase27_decision_policy.py",
    "tools/bazel/phase27_retained_code_acceptance_decisions.py",
    "tools/bazel/phase28_readiness_contract.py",
    "tools/bazel/phase28_readiness_policy.py",
    "tools/bazel/phase28_final_readiness_packet.py",
    "tools/bazel/phase31_final_evidence_intake.py",
    "tools/bazel/phase31_intake_policy.py",
    "tools/bazel/phase31_intake_receipts.py",
    "tools/bazel/phase31_intake_wiring.py",
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
PHASE32_OUTPUT_BUNDLE = [
    "blocker-register.json",
    "decision-impact-index.json",
    "exception-request-register.json",
    "residual-risk-request-register.json",
    "downstream-handoff-manifest.json",
    "redacted-blocker-register-report.md",
]
PRODUCER_CONTAINER_MAPPINGS = {
    "build/ci-evidence/phase27/residual-risk-register.json": {
        "source_domain": "retained_code",
        "producer_phase": "phase27",
        "producer_artifact_kind": "phase27_residual_risk_register",
        "source_row_kind": "residual_risk",
        "source_subject_id": "phase27-residual-risk-register-container",
        "decision_axis": "residual_risk",
        "decision_subject_id": "phase27-residual-risk-register-container",
        "source_stream": "retained-code",
        "affected_gate": "final-retained-code-acceptance",
    },
    "build/ci-evidence/phase27/exception-decision-register.json": {
        "source_domain": "retained_code",
        "producer_phase": "phase27",
        "producer_artifact_kind": "phase27_exception_decision_register",
        "source_row_kind": "exception_request",
        "source_subject_id": "phase27-exception-decision-register-container",
        "decision_axis": "exception",
        "decision_subject_id": "phase27-exception-decision-register-container",
        "source_stream": "retained-code",
        "affected_gate": "final-retained-code-acceptance",
    },
    "build/ci-evidence/phase28/blocker-summary.json": {
        "source_domain": "readiness",
        "producer_phase": "phase28",
        "producer_artifact_kind": "phase28_blocker_summary",
        "source_row_kind": "readiness_blocker",
        "source_subject_id": "phase28-blocker-summary-container",
        "decision_axis": "readiness",
        "decision_subject_id": "phase28-blocker-summary-container",
        "source_stream": "readiness",
        "affected_gate": "final-readiness",
    },
    "build/ci-evidence/phase28/exception-residual-risk-summary.json": {
        "source_domain": "readiness",
        "producer_phase": "phase28",
        "producer_artifact_kind": "phase28_exception_residual_risk_summary",
        "source_row_kind": "residual_risk",
        "source_subject_id":
        "phase28-exception-residual-risk-summary-container",
        "decision_axis": "residual_risk",
        "decision_subject_id":
        "phase28-exception-residual-risk-summary-container",
        "source_stream": "readiness",
        "affected_gate": "final-readiness",
    },
}


class Phase32BlockerRegisterTriageTestBase(unittest.TestCase):

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
                *[ROOT / module for module in TRIAGE_MODULES],
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
