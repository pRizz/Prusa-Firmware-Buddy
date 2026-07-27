#!/usr/bin/env python3
from __future__ import annotations

import importlib
import importlib.util
import textwrap
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
    "tools/bazel/phase33_decision_policy.py",
    "tools/bazel/phase33_decision_validation.py",
    "tools/bazel/phase33_decision_outputs.py",
    "tools/bazel/phase33_decision_wiring.py",
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
DECISION_TYPE_AXES = {
    "retained_code": "retained_code",
    "residual_risk": "residual_risk",
    "exception": "exception",
    "readiness": "readiness",
    "reference_demotion": "demotion",
}


class Phase33MaintainerDecisionInputsTest(unittest.TestCase):

    def load_module(self):
        spec = importlib.util.spec_from_file_location(
            "phase33_maintainer_decision_inputs", VERIFIER)
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
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        return path

    def write_text(self, root: Path, path: str, text: str) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")
        return path

    def replace_with_external_symlink(self, root: Path,
                                      relative_path: str) -> None:
        source = root / relative_path
        external_dir = tempfile.TemporaryDirectory()
        self.addCleanup(external_dir.cleanup)
        external_path = Path(external_dir.name) / source.name
        shutil.copy2(source, external_path)
        source.unlink()
        source.symlink_to(external_path)

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
        self.write_text(root, "tools/bazel/rust_workflow.sh",
                        "#!/usr/bin/env bash\n")
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
        decision_axis: str | None = None,
        decision_subject_id: str | None = None,
    ) -> dict[str, object]:
        maybe_decision_axis = decision_axis
        if maybe_decision_axis is None:
            maybe_decision_axis = {
                "retained_code_decision_required": "retained_code",
                "residual_risk_decision_required": "residual_risk",
                "exception_decision_required": "exception",
                "final_readiness_blocked": "readiness",
                "demotion_decision_required": "demotion",
            }[decision_impact]
        return {
            "row_id": row_id,
            "decision_axis": maybe_decision_axis,
            "decision_subject_id": decision_subject_id or row_id,
            "source_stream": source_stream,
            "source_ref": f"external://phase32/{row_id}",
            "requirement_ids": ["DECIDE-01"],
            "affected_gate": affected_gate,
            "row_problem_kind": row_problem_kind,
            "blocker_kind": blocker_kind,
            "severity": severity,
            "owner_ref": "maintainer://owner",
            "required_next_action":
            "Provide explicit maintainer decision input.",
            "decision_impact": decision_impact,
            "proof_eligibility": "ineligible",
            "evidence_refs": [f"external://evidence/{row_id}"],
        }

    def write_phase32_fixture(self, root: Path,
                              rows: list[dict[str, object]]) -> None:
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
        decision_axis = DECISION_TYPE_AXES.get(decision_type, decision_type)
        decision_targets = [{
            "row_ref":
            source_row_ref,
            "decision_axis":
            decision_axis,
            "decision_subject_id":
            source_row_ref.rsplit("#", 1)[-1],
        } for source_row_ref in source_row_refs]
        data: dict[str, object] = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "decision_value": decision_value,
            "decision_targets": decision_targets,
            "source_row_refs": source_row_refs,
            "maintainer_identity_ref": "maintainer://alice",
            "maintainer_role": "cutover-maintainer",
            "owner_signoff_ref": "owner://signoff/alice",
            "decision_timestamp": "2026-07-04T02:00:00Z",
            "rationale":
            "Explicit maintainer decision for Phase 33 test fixture.",
            "evidence_refs": source_row_refs,
            "artifact_refs": ["external://artifact/phase33-test"],
        }
        data.update(extra)
        return data

    def write_decisions(self, root: Path, decisions: list[dict[str, object]],
                        **extra: object) -> str:
        payload: dict[str, object] = {
            "schema_version": "1",
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "decisions": decisions,
        }
        payload.update(extra)
        decision_id = "empty"
        if decisions:
            decision_id = str(decisions[0].get("decision_id", "decision"))
        return self.write_json(
            root, f"build/ci-evidence/phase33-inputs/{decision_id}.json",
            payload)

    def run_quick(
        self,
        root: Path,
        decisions_path: str | None = None,
        output_dir: str = "build/ci-evidence/phase33"
    ) -> subprocess.CompletedProcess[str]:
        args = [
            "--quick",
            "--phase32-handoff",
            "build/ci-evidence/phase32/downstream-handoff-manifest.json",
            "--output-dir",
            output_dir,
        ]
        if decisions_path is not None:
            args.extend(["--maintainer-decisions", decisions_path])
        return self.run_temp_verifier(root, args)

    for _module_name in (
            "phase33_maintainer_decision_inputs_cases_test",
            "phase33_maintainer_decision_inputs_failure_test",
            "phase33_maintainer_decision_inputs_security_test",
    ):
        _module = importlib.import_module(_module_name)
        exec(textwrap.dedent(_module.TEST_METHODS), globals(), locals())


if __name__ == "__main__":
    unittest.main()
