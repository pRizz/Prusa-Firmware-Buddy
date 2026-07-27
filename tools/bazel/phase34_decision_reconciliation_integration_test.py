#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

import phase32_blocker_register_triage_test as phase32_test


ROOT = Path(__file__).resolve().parents[2]
PHASE32_REGISTER = "build/ci-evidence/phase32/blocker-register.json"
PHASE32_HANDOFF = "build/ci-evidence/phase32/downstream-handoff-manifest.json"
PHASE33_DECISIONS = "build/ci-evidence/phase33-inputs/approved-decisions.json"
PHASE33_HANDOFF = "build/ci-evidence/phase33/downstream-handoff-manifest.json"
PHASE33_NORMALIZED = "build/ci-evidence/phase33/normalized-decision-records.json"
PHASE34_OUTPUT = "build/ci-evidence/phase34"
RUNTIME_FILES = [
    "tools/bazel/phase33_maintainer_decision_inputs.py",
    "tools/bazel/phase33_decision_policy.py",
    "tools/bazel/phase33_decision_validation.py",
    "tools/bazel/phase33_decision_outputs.py",
    "tools/bazel/phase33_decision_wiring.py",
    "tools/bazel/phase34_decision_reconciliation.py",
    "tools/bazel/phase34_final_readiness_demotion_dry_run.py",
    "tools/bazel/phase34_publication_state.py",
    "tools/bazel/phase34_source_validation.py",
    "tools/bazel/phase34_decision_validation.py",
    "tools/bazel/phase34_readiness_policy.py",
    "tools/bazel/phase34_coverage_diagnostics.py",
    "tools/bazel/phase34_bundle_publication.py",
    "tools/bazel/phase34_readiness_wiring.py",
    "tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json",
    "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json",
]
EXPECTED_PHASE34_ARTIFACTS = [
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
NON_RELEASE_STREAMS = {
    "simulator": {
        "phase_number": "23",
        "criterion_id": "final-simulator-evidence",
        "evidence_family": "simulator",
        "requirement_id": "EVID-01",
    },
    "hardware-media-safety": {
        "phase_number": "24",
        "criterion_id": "final-hardware-safety-media-evidence",
        "evidence_family": "hardware",
        "requirement_id": "EVID-02",
    },
    "live-service": {
        "phase_number": "25",
        "criterion_id": "final-live-network-transfer-evidence",
        "evidence_family": "live-service",
        "requirement_id": "EVID-03",
    },
}
DECISION_TYPES = {
    "retained_code": "retained_code",
    "residual_risk": "residual_risk",
    "exception": "exception",
    "readiness": "readiness",
    "demotion": "reference_demotion",
}
APPROVING_VALUES = {
    "retained_code": "accept",
    "residual_risk": "accept",
    "exception": "approve",
    "readiness": "approve",
    "demotion": "approve",
}


class Phase34DecisionReconciliationIntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.producer_helper = phase32_test.Phase32ProducerShapeTest(
            methodName="runTest")
        cls.baseline_temp, cls.baseline_root = (
            cls.producer_helper.generate_producer_fixture())
        cls.addClassCleanup(cls.baseline_temp.cleanup)
        cls.copy_runtime_files()
        cls.write_complete_phase31_output()

        phase32_result = cls.producer_helper.run_phase32(cls.baseline_root)
        if phase32_result.returncode != 0:
            raise AssertionError(phase32_result.stdout)

        cls.write_phase33_decisions()
        phase33_result = cls.run_phase33(cls.baseline_root)
        if phase33_result.returncode != 0:
            raise AssertionError(phase33_result.stdout)

        phase34_result = cls.run_phase34(cls.baseline_root)
        if phase34_result.returncode != 0:
            raise AssertionError(phase34_result.stdout)

    @classmethod
    def copy_runtime_files(cls) -> None:
        for relative_path in RUNTIME_FILES:
            source = ROOT / relative_path
            destination = cls.baseline_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    @classmethod
    def load_module(cls, module_name: str) -> ModuleType:
        module_path = cls.baseline_root / f"tools/bazel/{module_name}.py"
        spec = importlib.util.spec_from_file_location(
            f"phase34_integration_{module_name}",
            module_path,
        )
        if spec is None or spec.loader is None:
            raise AssertionError(f"unable to load {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @classmethod
    def read_json(cls, root: Path, relative_path: str) -> dict[str, object]:
        return json.loads(
            (root / relative_path).read_text(encoding="utf-8"))

    @classmethod
    def write_json(cls, root: Path, relative_path: str,
                   value: object) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def write_complete_phase31_output(cls) -> None:
        phase31 = cls.load_module("phase31_final_evidence_intake")
        contract = cls.read_json(
            cls.baseline_root,
            "tools/bazel/manifests/phase31_final_evidence_intake_contract.json",
        )
        adapters = phase31.contract_adapters(contract)
        receipts = []
        for stream, stream_specification in NON_RELEASE_STREAMS.items():
            adapter = adapters[stream]
            output_dir = Path(adapter["output_root"])
            manifest_path = output_dir / adapter["manifest"]
            upstream_path = output_dir / adapter["upstream_row"]
            cls.write_json(
                cls.baseline_root,
                manifest_path.as_posix(),
                {
                    "artifact_name": adapter["source_phase"],
                    "command_mode": "evidence-input",
                    "generated_at": "2026-07-26T02:00:00Z",
                    "output_root": output_dir.as_posix(),
                    "phase": adapter["source_phase"],
                    "phase_lifecycle_id": adapter["source_lifecycle_id"],
                    adapter["real_evidence_flag"]: True,
                    "status": "passed",
                },
            )
            cls.write_json(
                cls.baseline_root,
                upstream_path.as_posix(),
                {
                    "artifact_refs": [
                        f"external://phase{stream_specification['phase_number']}/"
                        f"{stream}/sanitized-results.json"
                    ],
                    "criterion_id": stream_specification["criterion_id"],
                    "evidence_family":
                    stream_specification["evidence_family"],
                    "exception_status": "none",
                    "failure_reason": "",
                    "manifest_ref": manifest_path.as_posix(),
                    "phase": adapter["source_phase"],
                    "phase_lifecycle_id": adapter["source_lifecycle_id"],
                    adapter["real_evidence_flag"]: True,
                    "redaction_status": "passed",
                    "requirement_ids": [
                        stream_specification["requirement_id"]
                    ],
                    "source_ref_status": "passed",
                    "status": "passed",
                },
            )
            receipt, _upstream_path = phase31.validate_stream_output(
                cls.baseline_root,
                adapter,
                output_dir,
                f"maintainer://phase34-integration/{stream}",
                ["producer-fixture", stream],
                str(len(receipts) + 1) * 64,
            )
            receipts.append(receipt)

        release_adapter = adapters["release-signing"]
        release_receipt, _release_path = phase31.validate_stream_output(
            cls.baseline_root,
            release_adapter,
            Path(release_adapter["output_root"]),
            "maintainer://phase34-integration/release-signing",
            ["producer-fixture", "release-signing"],
            "4" * 64,
        )
        receipts.append(release_receipt)
        output_dir = phase31.reset_output_root(
            cls.baseline_root,
            Path("build/ci-evidence/phase31"),
        )
        phase31.write_phase31_outputs(
            cls.baseline_root,
            output_dir,
            receipts,
            [],
        )

    @classmethod
    def decision_for_row(cls, row: dict[str, object],
                         index: int) -> dict[str, object]:
        axis = str(row["decision_axis"])
        decision_type = DECISION_TYPES[axis]
        row_ref = f"{PHASE32_REGISTER}#{row['row_id']}"
        decision_id = f"approve-{axis}-{index:02d}"
        decision = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "decision_value": APPROVING_VALUES[axis],
            "decision_targets": [{
                "row_ref":
                row_ref,
                "decision_axis":
                axis,
                "decision_subject_id":
                row["decision_subject_id"],
            }],
            "source_row_refs": [row_ref],
            "maintainer_identity_ref":
            "maintainer://phase34-integration/alice",
            "maintainer_role":
            "cutover-maintainer",
            "owner_signoff_ref":
            "owner://phase34-integration/alice",
            "decision_timestamp":
            f"2026-07-26T02:01:{index:02d}Z",
            "rationale":
            f"Exact typed integration decision for {row['row_id']}.",
            "evidence_refs": [row_ref],
            "artifact_refs":
            ["external://phase33/integration/decision-record.json"],
        }
        if axis == "retained_code":
            decision["residual_risk_rationale"] = (
                "The retained boundary has bounded, reviewed residual risk.")
        elif axis == "residual_risk":
            decision["affected_gates"] = [row["affected_gate"]]
            decision["follow_up_refs"] = [
                "external://phase33/integration/residual-risk-follow-up"
            ]
        elif axis == "exception":
            decision.update({
                "scope":
                str(row["decision_subject_id"]),
                "expiry_or_review_trigger":
                "next retained-boundary review",
                "affected_requirements":
                list(row["requirement_ids"]),
                "affected_gates": [row["affected_gate"]],
                "linked_blocker_refs": [row_ref],
            })
        return decision

    @classmethod
    def write_phase33_decisions(cls) -> None:
        register = cls.read_json(cls.baseline_root, PHASE32_REGISTER)
        rows = register["rows"]
        if not isinstance(rows, list):
            raise AssertionError("Phase 32 rows must be a list")
        decisions = [
            cls.decision_for_row(row, index)
            for index, row in enumerate(rows)
            if isinstance(row, dict)
        ]
        cls.write_json(
            cls.baseline_root,
            PHASE33_DECISIONS,
            {
                "schema_version": "1",
                "phase": "33-maintainer-decision-inputs",
                "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                "decisions": decisions,
            },
        )

    @staticmethod
    def run_command(root: Path,
                    arguments: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            arguments,
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    @classmethod
    def run_phase33(cls, root: Path) -> subprocess.CompletedProcess[str]:
        return cls.run_command(
            root,
            [
                "python3",
                "tools/bazel/phase33_maintainer_decision_inputs.py",
                "--quick",
                "--phase32-handoff",
                PHASE32_HANDOFF,
                "--maintainer-decisions",
                PHASE33_DECISIONS,
                "--output-dir",
                "build/ci-evidence/phase33",
            ],
        )

    @classmethod
    def run_phase34(cls, root: Path) -> subprocess.CompletedProcess[str]:
        return cls.run_command(
            root,
            [
                "python3",
                "tools/bazel/phase34_final_readiness_demotion_dry_run.py",
                "--quick",
                "--phase31-output-dir",
                "build/ci-evidence/phase31",
                "--phase33-handoff",
                PHASE33_HANDOFF,
                "--output-dir",
                PHASE34_OUTPUT,
            ],
        )

    def clone_baseline(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name).resolve()
        shutil.copytree(self.baseline_root, root, dirs_exist_ok=True)
        return root

    def retained_decision(self,
                          payload: dict[str, object]) -> dict[str, object]:
        rows = payload["rows"]
        self.assertIsInstance(rows, list)
        return next(
            row for row in rows
            if isinstance(row, dict)
            and row.get("decision_type") == "retained_code")

    def assert_mutation_blocks(self, mutation,
                               expected_reason: str) -> None:
        # Arrange
        root = self.clone_baseline()
        normalized = self.read_json(root, PHASE33_NORMALIZED)
        mutation(normalized)
        self.write_json(root, PHASE33_NORMALIZED, normalized)

        # Act
        result = self.run_phase34(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        packet = self.read_json(
            root,
            f"{PHASE34_OUTPUT}/final-readiness-packet.json",
        )
        ledger = self.read_json(
            root,
            f"{PHASE34_OUTPUT}/readiness-coverage-ledger.json",
        )
        reasons = {
            reason
            for row in ledger["rows"]
            for reason in row["reason_codes"]
        }
        self.assertEqual(packet["readiness_state"], "blocked")
        self.assertIn(expected_reason, reasons)

    def test_complete_real_producer_chain_publishes_unblocked_bundle(
            self) -> None:
        # Arrange
        root = self.baseline_root

        # Act
        packet = self.read_json(
            root,
            f"{PHASE34_OUTPUT}/final-readiness-packet.json",
        )
        ledger = self.read_json(
            root,
            f"{PHASE34_OUTPUT}/readiness-coverage-ledger.json",
        )

        # Assert
        self.assertEqual(packet["readiness_state"], "unblocked")
        self.assertEqual(packet["ledger_rows"], ledger["rows"])
        self.assertEqual(
            {row["ledger_row_kind"] for row in ledger["rows"]},
            {"evidence", "decision-domain"},
        )
        decision_rows = [
            row for row in ledger["rows"]
            if row["ledger_row_kind"] == "decision-domain"
        ]
        self.assertTrue(decision_rows)
        self.assertTrue(
            all(row["coverage_state"] != "dangling-blocker"
                for row in decision_rows))
        for artifact in EXPECTED_PHASE34_ARTIFACTS:
            self.assertTrue((root / PHASE34_OUTPUT / artifact).is_file(),
                            artifact)

    def test_omitted_binding_blocks_with_specific_diagnostic(self) -> None:

        def omit(payload):
            payload["rows"].remove(self.retained_decision(payload))

        self.assert_mutation_blocks(omit, "decision-target-missing")

    def test_row_ref_mismatch_blocks_with_specific_diagnostic(self) -> None:

        def mismatch(payload):
            decision = self.retained_decision(payload)
            mismatched_ref = f"{PHASE32_REGISTER}#missing-row"
            decision["decision_targets"][0]["row_ref"] = mismatched_ref
            decision["source_row_refs"] = [mismatched_ref]

        self.assert_mutation_blocks(mismatch,
                                    "decision-target-row-mismatch")

    def test_axis_mismatch_blocks_with_specific_diagnostic(self) -> None:

        def mismatch(payload):
            decision = self.retained_decision(payload)
            decision["decision_targets"][0][
                "decision_axis"] = "residual_risk"

        self.assert_mutation_blocks(mismatch,
                                    "decision-target-axis-mismatch")

    def test_subject_mismatch_blocks_with_specific_diagnostic(self) -> None:

        def mismatch(payload):
            decision = self.retained_decision(payload)
            decision["decision_targets"][0][
                "decision_subject_id"] = "different-subject"

        self.assert_mutation_blocks(mismatch,
                                    "decision-target-subject-mismatch")

    def test_stale_lifecycle_blocks_with_specific_diagnostic(self) -> None:

        def stale(payload):
            self.retained_decision(
                payload)["phase_lifecycle_id"] = "stale-phase33-lifecycle"

        self.assert_mutation_blocks(stale, "decision-lifecycle-stale")

    def test_invalid_value_blocks_with_specific_diagnostic(self) -> None:

        def invalidate(payload):
            self.retained_decision(
                payload)["decision_value"] = "unexpected-value"

        self.assert_mutation_blocks(invalidate, "decision-value-invalid")

    def test_duplicate_binding_blocks_with_specific_diagnostic(self) -> None:

        def duplicate(payload):
            duplicated = copy.deepcopy(self.retained_decision(payload))
            duplicated["decision_id"] = "duplicate-retained-binding"
            payload["rows"].append(duplicated)

        self.assert_mutation_blocks(duplicate, "decision-target-duplicate")

    def test_conflicting_binding_blocks_with_specific_diagnostic(self) -> None:

        def conflict(payload):
            conflicting = copy.deepcopy(self.retained_decision(payload))
            conflicting["decision_id"] = "conflicting-retained-binding"
            conflicting["decision_value"] = "reject"
            payload["rows"].append(conflicting)

        self.assert_mutation_blocks(conflict, "decision-target-conflict")


if __name__ == "__main__":
    unittest.main()
