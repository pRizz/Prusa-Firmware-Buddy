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
VERIFIER = ROOT / "tools/bazel/phase33_maintainer_decision_inputs.py"
CONTRACT = ROOT / "tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json"
SOURCE_FILES = [
    "tools/bazel/phase33_maintainer_decision_inputs.py",
    "tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json",
    "tools/bazel/manifests/phase32_blocker_register_triage_contract.json",
    "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json",
    "tools/bazel/manifests/phase28_final_readiness_packet_contract.json",
]
GENERATED_ARTIFACTS = [
    "maintainer-decision-input-template.json",
    "normalized-decision-records.json",
    "retained-code-decision-register.json",
    "residual-risk-decision-register.json",
    "exception-decision-register.json",
    "readiness-decision-handoff.json",
    "demotion-decision-handoff.json",
    "decision-validation-report.json",
    "downstream-handoff-manifest.json",
    "redacted-maintainer-decision-report.md",
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase32_blocker_register_triage_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase28_final_readiness_packet_contract.json",
    "contract-snapshots/phase32-downstream-handoff-manifest.json",
    "contract-snapshots/phase32-blocker-register.json",
]
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"


class Phase33MaintainerDecisionInputsTest(unittest.TestCase):
    def load_module(self):
        spec = importlib.util.spec_from_file_location("phase33_maintainer_decision_inputs", VERIFIER)
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
        verifier = root / "tools/bazel/phase33_maintainer_decision_inputs.py"
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

    def write_json(self, root: Path, path: str, data: object) -> str:
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
        for source in SOURCE_FILES:
            source_path = ROOT / source
            destination = root / source
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination)
        self.write_text(root, "BUILD.bazel", "")
        self.write_text(root, "tools/bazel/BUILD.bazel", "")
        self.write_text(root, "tools/bazel/rust_workflow.sh", "#!/usr/bin/env bash\n")
        self.write_text(root, "justfile", "")
        return temp_dir, root

    def blocker_ref(self, row_id: str) -> str:
        return f"{PHASE32_REGISTER_REF}#{row_id}"

    def blocker_row(
        self,
        row_id: str,
        *,
        row_problem_kind: str = "failed",
        blocker_kind: str = "repair_item",
        severity: str = "critical",
        decision_impact: str = "final_readiness_blocked",
        affected_gate: str = "final-simulator-evidence",
        source_stream: str = "simulator",
    ) -> dict[str, object]:
        return {
            "row_id": row_id,
            "source_stream": source_stream,
            "source_ref": f"external://phase32/{row_id}",
            "requirement_ids": ["DECIDE-01"],
            "affected_gate": affected_gate,
            "row_problem_kind": row_problem_kind,
            "blocker_kind": blocker_kind,
            "severity": severity,
            "owner_ref": "maintainer://owner",
            "required_next_action": "Provide explicit maintainer decision input.",
            "decision_impact": decision_impact,
            "proof_eligibility": "ineligible",
            "evidence_refs": [f"external://evidence/{row_id}"],
        }

    def write_phase32_fixture(self, root: Path, rows: list[dict[str, object]]) -> None:
        self.write_json(
            root,
            PHASE32_REGISTER_REF,
            {
                "artifact_name": "phase32-blocker-register-triage",
                "phase": "32-blocker-register-and-evidence-triage",
                "phase_lifecycle_id": "32-2026-07-03T14-13-51",
                "rows": rows,
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase32/downstream-handoff-manifest.json",
            {
                "artifact_name": "phase32-blocker-register-triage",
                "canonical_register_ref": PHASE32_REGISTER_REF,
                "phase": "32-blocker-register-and-evidence-triage",
                "phase_lifecycle_id": "32-2026-07-03T14-13-51",
                "downstream_consumers": ["phase33-maintainer-decisions"],
            },
        )

    def decision(
        self,
        decision_id: str,
        decision_type: str,
        decision_value: str,
        source_row_refs: list[str],
        **extra: object,
    ) -> dict[str, object]:
        data: dict[str, object] = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "decision_value": decision_value,
            "source_row_refs": source_row_refs,
            "maintainer_identity_ref": "maintainer://alice",
            "maintainer_role": "cutover-maintainer",
            "owner_signoff_ref": "owner://signoff/alice",
            "decision_timestamp": "2026-07-04T02:00:00Z",
            "rationale": "Explicit maintainer decision for Phase 33 test fixture.",
            "evidence_refs": source_row_refs,
            "artifact_refs": ["external://artifact/phase33-test"],
        }
        data.update(extra)
        return data

    def write_decisions(self, root: Path, decisions: list[dict[str, object]], **extra: object) -> str:
        payload: dict[str, object] = {
            "schema_version": "1",
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "decisions": decisions,
        }
        payload.update(extra)
        return self.write_json(root, "build/ci-evidence/phase33/maintainer-decisions.json", payload)

    def run_quick(self, root: Path, decisions_path: str | None = None) -> subprocess.CompletedProcess[str]:
        args = [
            "--quick",
            "--phase32-handoff",
            "build/ci-evidence/phase32/downstream-handoff-manifest.json",
            "--output-dir",
            "build/ci-evidence/phase33",
        ]
        if decisions_path is not None:
            args.extend(["--maintainer-decisions", decisions_path])
        return self.run_temp_verifier(root, args)

    def test_contract_lists_all_decision_axes_and_artifacts(self) -> None:
        # Arrange
        contract = self.read_contract()

        # Act
        decision_types = contract["enums"]["decision_type"]

        # Assert
        self.assertEqual(contract["id"], "phase33_maintainer_decision_inputs_contract")
        self.assertEqual(contract["phase"], "33-maintainer-decision-inputs")
        self.assertEqual(contract["phase_lifecycle_id"], "33-2026-07-04T01-36-41")
        self.assertEqual(contract["output_root"], "build/ci-evidence/phase33")
        self.assertEqual(contract["requirement_ids"], ["DECIDE-01", "DECIDE-02", "DECIDE-03"])
        self.assertEqual(
            decision_types,
            ["retained_code", "residual_risk", "exception", "readiness", "reference_demotion"],
        )
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)
        self.assertIn("demotion_allowed", contract["prohibited_output_markers"])
        self.assertIn("just phase33-verify", contract["verification_commands"])

    def test_quick_without_maintainer_input_writes_template_and_blocked_handoffs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("critical-readiness-blocker")])

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        for artifact in GENERATED_ARTIFACTS:
            self.assertTrue((root / "build/ci-evidence/phase33" / artifact).exists(), artifact)
        manifest = self.read_json(root, "build/ci-evidence/phase33/downstream-handoff-manifest.json")
        readiness = self.read_json(root, "build/ci-evidence/phase33/readiness-decision-handoff.json")
        demotion = self.read_json(root, "build/ci-evidence/phase33/demotion-decision-handoff.json")
        self.assertIs(manifest["maintainer_input_supplied"], False)
        self.assertIs(manifest["source_inputs"]["raw_evidence_consumed"], False)
        self.assertEqual(readiness["handoff_state"], "blocked-pending-maintainer-input")
        self.assertEqual(demotion["authorization_state"], "blocked")

    def test_retained_and_residual_decisions_require_explicit_metadata_and_owner_signoff(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        retained = self.blocker_row("retained-row", decision_impact="retained_code_decision_required", source_stream="retained-code")
        residual = self.blocker_row("risk-row", decision_impact="residual_risk_decision_required", affected_gate="final-residual-risk-review")
        self.write_phase32_fixture(root, [retained, residual])
        missing_signoff = self.decision("missing-owner-signoff", "retained_code", "accept", [self.blocker_ref("retained-row")])
        missing_signoff.pop("owner_signoff_ref")
        invalid_path = self.write_decisions(root, [missing_signoff])
        valid_path = self.write_decisions(
            root,
            [
                self.decision("accept-retained", "retained_code", "accept", [self.blocker_ref("retained-row")], residual_risk_rationale="Accepted with owner signoff."),
                self.decision(
                    "accept-risk",
                    "residual_risk",
                    "accept",
                    [self.blocker_ref("risk-row")],
                    affected_gates=["final-residual-risk-review"],
                    follow_up_refs=["external://ticket/risk-review"],
                ),
            ],
        )

        # Act
        invalid_result = self.run_quick(root, invalid_path)
        valid_result = self.run_quick(root, valid_path)

        # Assert
        self.assertNotEqual(invalid_result.returncode, 0)
        self.assertIn("owner_signoff_ref", invalid_result.stdout)
        self.assertEqual(valid_result.returncode, 0, valid_result.stdout)
        retained_register = self.read_json(root, "build/ci-evidence/phase33/retained-code-decision-register.json")
        residual_register = self.read_json(root, "build/ci-evidence/phase33/residual-risk-decision-register.json")
        self.assertEqual(retained_register["rows"][0]["decision_value"], "accept")
        self.assertEqual(residual_register["rows"][0]["decision_value"], "accept")

    def test_hard_blocker_problem_kinds_reject_normal_acceptance(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        rows = [
            self.blocker_row("hard-retained", row_problem_kind="secret_tainted", decision_impact="retained_code_decision_required", source_stream="retained-code"),
            self.blocker_row("hard-risk", row_problem_kind="redaction_failed", decision_impact="residual_risk_decision_required"),
            self.blocker_row("hard-exception", row_problem_kind="unsafe_ref", blocker_kind="exception_request", decision_impact="exception_decision_required"),
        ]
        self.write_phase32_fixture(root, rows)
        decisions_path = self.write_decisions(
            root,
            [
                self.decision("hard-retained-accept", "retained_code", "accept", [self.blocker_ref("hard-retained")], residual_risk_rationale="Risk rationale."),
                self.decision("hard-risk-accept", "residual_risk", "accept", [self.blocker_ref("hard-risk")], affected_gates=["final-simulator-evidence"], follow_up_refs=["external://ticket/risk"]),
                self.decision(
                    "hard-exception-approve",
                    "exception",
                    "approve",
                    [self.blocker_ref("hard-exception")],
                    scope="narrow",
                    expiry_or_review_trigger="next release",
                    affected_requirements=["DECIDE-02"],
                    affected_gates=["final-simulator-evidence"],
                    linked_blocker_refs=[self.blocker_ref("hard-exception")],
                ),
            ],
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hard blocker", result.stdout.casefold())

    def test_exception_approval_requires_exact_row_ref_and_gate_match(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        exception_row = self.blocker_row(
            "exception-row",
            row_problem_kind="exception_requested",
            blocker_kind="exception_request",
            decision_impact="exception_decision_required",
            affected_gate="final-live-network-transfer-evidence",
        )
        self.write_phase32_fixture(root, [exception_row])
        invalid_path = self.write_decisions(
            root,
            [
                self.decision(
                    "bad-exception-gate",
                    "exception",
                    "approve",
                    [self.blocker_ref("exception-row")],
                    scope="live transfer only",
                    expiry_or_review_trigger="phase35 review",
                    affected_requirements=["DECIDE-02"],
                    affected_gates=["final-simulator-evidence"],
                    linked_blocker_refs=[self.blocker_ref("exception-row")],
                )
            ],
        )
        valid_path = self.write_decisions(
            root,
            [
                self.decision(
                    "good-exception-gate",
                    "exception",
                    "approve",
                    [self.blocker_ref("exception-row")],
                    scope="live transfer only",
                    expiry_or_review_trigger="phase35 review",
                    affected_requirements=["DECIDE-02"],
                    affected_gates=["final-live-network-transfer-evidence"],
                    linked_blocker_refs=[self.blocker_ref("exception-row")],
                )
            ],
        )

        # Act
        invalid_result = self.run_quick(root, invalid_path)
        valid_result = self.run_quick(root, valid_path)

        # Assert
        self.assertNotEqual(invalid_result.returncode, 0)
        self.assertIn("affected_gate", invalid_result.stdout)
        self.assertEqual(valid_result.returncode, 0, valid_result.stdout)
        register = self.read_json(root, "build/ci-evidence/phase33/exception-decision-register.json")
        self.assertEqual(register["rows"][0]["coverage_state"], "approved-exception")

    def test_rejected_exception_remains_in_exception_register(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(
            root,
            [
                self.blocker_row(
                    "exception-row",
                    row_problem_kind="exception_requested",
                    blocker_kind="exception_request",
                    decision_impact="exception_decision_required",
                )
            ],
        )
        decisions_path = self.write_decisions(root, [self.decision("reject-exception", "exception", "reject", [self.blocker_ref("exception-row")])])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        register = self.read_json(root, "build/ci-evidence/phase33/exception-decision-register.json")
        self.assertEqual(register["rows"][0]["decision_value"], "reject")
        self.assertEqual(register["rows"][0]["coverage_state"], "rejected")

    def test_readiness_approval_rejects_uncovered_critical_blocker(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("critical-readiness-blocker", severity="critical")])
        decisions_path = self.write_decisions(root, [self.decision("approve-readiness", "readiness", "approve", [self.blocker_ref("critical-readiness-blocker")])])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("uncovered critical blocker", result.stdout.casefold())

    def test_readiness_block_handoff_preserves_blocker_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("critical-readiness-blocker", severity="critical")])
        decisions_path = self.write_decisions(
            root,
            [
                self.decision(
                    "block-readiness",
                    "readiness",
                    "block",
                    [self.blocker_ref("critical-readiness-blocker")],
                    blocked_source_row_refs=[self.blocker_ref("critical-readiness-blocker")],
                )
            ],
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        handoff = self.read_json(root, "build/ci-evidence/phase33/readiness-decision-handoff.json")
        self.assertEqual(handoff["handoff_state"], "blocked-by-maintainer-input")
        self.assertEqual(handoff["blocked_source_row_refs"], [self.blocker_ref("critical-readiness-blocker")])

    def test_demotion_decision_is_separate_from_readiness_and_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("demotion-row", decision_impact="demotion_decision_required", affected_gate="final-reference-demotion-allowed")])
        decisions_path = self.write_decisions(root, [self.decision("approve-demotion", "reference_demotion", "approve", [self.blocker_ref("demotion-row")])])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        demotion = self.read_json(root, "build/ci-evidence/phase33/demotion-decision-handoff.json")
        readiness_text = (root / "build/ci-evidence/phase33/readiness-decision-handoff.json").read_text(encoding="utf-8")
        manifest_text = (root / "build/ci-evidence/phase33/downstream-handoff-manifest.json").read_text(encoding="utf-8")
        self.assertEqual(demotion["authorization_state"], "approved-input-recorded")
        self.assertTrue(demotion["phase34_must_validate_readiness"])
        self.assertNotIn("demotion_allowed", readiness_text)
        self.assertNotIn("final_readiness_status", manifest_text)

    def test_green_evidence_does_not_create_any_approval(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [])

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        normalized = self.read_json(root, "build/ci-evidence/phase33/normalized-decision-records.json")
        readiness = self.read_json(root, "build/ci-evidence/phase33/readiness-decision-handoff.json")
        demotion = self.read_json(root, "build/ci-evidence/phase33/demotion-decision-handoff.json")
        self.assertEqual(normalized["rows"], [])
        self.assertEqual(readiness["handoff_state"], "blocked-pending-maintainer-input")
        self.assertEqual(demotion["authorization_state"], "blocked")

    def test_stale_lifecycle_unknown_type_unresolved_ref_and_malformed_ref_fail_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        cases = [
            self.write_decisions(root, [self.decision("stale-lifecycle", "readiness", "block", [self.blocker_ref("known-row")])], phase_lifecycle_id="stale"),
            self.write_decisions(root, [self.decision("unknown-type", "surprise", "approve", [self.blocker_ref("known-row")])]),
            self.write_decisions(root, [self.decision("unresolved-ref", "readiness", "block", [self.blocker_ref("missing-row")])]),
            self.write_decisions(root, [self.decision("malformed-ref", "readiness", "block", ["build/ci-evidence/phase32/../secret.json#known-row"])]),
        ]

        for decisions_path in cases:
            with self.subTest(decisions_path=decisions_path):
                # Act
                result = self.run_quick(root, decisions_path)

                # Assert
                self.assertNotEqual(result.returncode, 0)

    def test_security_scan_rejects_secret_fields_path_traversal_and_approval_overclaims(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        secret_input = self.write_decisions(root, [self.decision("secret-input", "readiness", "block", [self.blocker_ref("known-row")])])
        secret_payload = self.read_json(root, secret_input)
        secret_payload["token_value"] = "redacted-test-token"
        self.write_json(root, secret_input, secret_payload)
        self.write_text(root, "build/ci-evidence/phase33/downstream-handoff-manifest.json", '{"demotion_allowed": true}\n')

        # Act
        input_result = self.run_quick(root, secret_input)
        output_result = self.run_temp_verifier(root, ["--security-only", "--output-dir", "build/ci-evidence/phase33"])
        path_result = self.run_temp_verifier(root, ["--quick", "--phase32-handoff", "../phase32/downstream-handoff-manifest.json"])

        # Assert
        self.assertNotEqual(input_result.returncode, 0)
        self.assertIn("token_value", input_result.stdout)
        self.assertNotEqual(output_result.returncode, 0)
        self.assertIn("demotion_allowed", output_result.stdout)
        self.assertNotEqual(path_result.returncode, 0)

    def test_wiring_requires_bazel_root_workflow_and_just_entries(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_temp_verifier(root, ["--wiring-only"])

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase33_verify", result.stdout)


if __name__ == "__main__":
    unittest.main()
