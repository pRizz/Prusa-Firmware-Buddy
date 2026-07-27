#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase24_hardware_media_safety_evidence_execution.py"
CONTRACT = "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json"
PHASE15_CONTRACT = "tools/bazel/manifests/phase15_hardware_evidence_contract.json"
PHASE18_CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
PHASE19_CONTRACT = "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json"
PHASE23_CONTRACT = "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json"
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase24"


class Phase24ExecutionTestSupport:

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        shutil.copy2(
            VERIFIER, root /
            "tools/bazel/phase24_hardware_media_safety_evidence_execution.py")
        shutil.copy2(
            ROOT / "tools/bazel/phase24_execution_policy.py",
            root / "tools/bazel/phase24_execution_policy.py",
        )
        shutil.copy2(
            ROOT / "tools/bazel/phase24_execution_contract.py",
            root / "tools/bazel/phase24_execution_contract.py",
        )
        for path in [
                CONTRACT, PHASE15_CONTRACT, PHASE18_CONTRACT, PHASE19_CONTRACT,
                PHASE23_CONTRACT
        ]:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, destination)
        return temp_dir, root

    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase24_hardware_media_safety_evidence_execution.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def read_json(self, root: Path, path: str) -> dict[str, object]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    def write_json(self, root: Path, path: str, data: object) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def read_phase15_contract(self, root: Path) -> dict[str, object]:
        return self.read_json(root, PHASE15_CONTRACT)

    def write_evidence_input(
        self,
        root: Path,
        rows: list[dict[str, object]],
        path: str = "phase24-evidence-input.json",
        maybe_packet_updates: dict[str, object] | None = None,
    ) -> str:
        packet = {
            "hardware_media_safety_evidence_packet": {
                "completed_at": "2026-06-23T21:00:00Z",
                "evidence_run_id": "hardware-run-2026-06-23",
                "firmware_identity": {
                    "build_id": "fw-test-build",
                    "firmware_basename": "firmware.bin",
                },
                "operator": "maintainer",
                "phase": "24-hardware-media-and-safety-evidence-execution",
                "phase_lifecycle_id": "24-2026-06-23T19-52-32",
                "scenario_results": rows,
                "source_contract_ref": PHASE15_CONTRACT,
                "started_at": "2026-06-23T20:00:00Z",
            }
        }
        if maybe_packet_updates is not None:
            packet["hardware_media_safety_evidence_packet"].update(
                maybe_packet_updates)
        self.write_json(root, path, packet)
        return path

    def complete_rows(self, root: Path) -> list[dict[str, object]]:
        contract = self.read_phase15_contract(root)
        rows: list[dict[str, object]] = []
        for scenario in contract["scenarios"]:
            source_status = "passed" if "passed" in scenario[
                "allowed_statuses"] else "source-contract-passed"
            rows.append({
                "artifact_refs": [f"external://phase24/{scenario['id']}.log"],
                "auxiliary_surface":
                scenario["auxiliary_surface"],
                "board":
                scenario["board"],
                "device":
                f"device-{scenario['id']}",
                "failure_observations":
                "none observed",
                "firmware_build":
                "fw-test-build",
                "media_surface":
                scenario["media_surface"],
                "observed_behavior":
                "expected hardware/media/safety behavior observed",
                "operator":
                "maintainer",
                "printer_family":
                scenario["printer_family"],
                "redaction_status":
                "passed",
                "residual_risk":
                "known residual risk recorded",
                "scenario_id":
                scenario["id"],
                "source_ref_status":
                "passed",
                "source_status":
                source_status,
                "status":
                "passed",
                "status_reason":
                "real hardware/media/safety evidence passed",
                "timestamp":
                "2026-06-23T20:30:00Z",
            })
        return rows

    def storage_row_index(self, rows: list[dict[str, object]]) -> int:
        for index, row in enumerate(rows):
            if str(row["scenario_id"]).startswith("hard-storage-"):
                return index
        self.fail("expected a storage scenario")

    def safety_row_index(self, rows: list[dict[str, object]]) -> int:
        for index, row in enumerate(rows):
            if str(row["scenario_id"]).startswith("hard-safety-"):
                return index
        self.fail("expected a safety scenario")

    def traceability_row_index(self, rows: list[dict[str, object]]) -> int:
        for index, row in enumerate(rows):
            if row["scenario_id"] == "hard-contract-traceability-and-redaction-boundary":
                return index
        self.fail("expected the traceability boundary scenario")

    def write_phase24_wiring(
        self,
        root: Path,
        maybe_tools_build: str | None = None,
        maybe_root_build: str | None = None,
        maybe_workflow: str | None = None,
        maybe_justfile: str | None = None,
    ) -> None:
        tools_build = maybe_tools_build if maybe_tools_build is not None else """filegroup(
    name = "phase24_source_ref_manifests",
    srcs = [
        "manifests/phase15_hardware_evidence_contract.json",
        "manifests/phase18_cutover_review_contract.json",
        "manifests/phase19_aggregate_ci_evidence_contract.json",
        "manifests/phase23_simulator_evidence_execution_contract.json",
        "manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
    ],
)

shell_binary(
    name = "phase24_verify",
    src = "rust_workflow.sh",
    data = [
        "phase24_hardware_media_safety_evidence_execution.py",
        "manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
        ":phase24_source_ref_manifests",
        "//:phase24_hardware_media_safety_evidence_execution_docs",
    ],
)

shell_binary(
    name = "phase24_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase24_hardware_media_safety_evidence_execution.py",
        "phase24_hardware_media_safety_evidence_execution_test.py",
        "manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
        ":phase24_source_ref_manifests",
    ],
)
"""
        root_build = maybe_root_build if maybe_root_build is not None else """filegroup(
    name = "phase24_hardware_media_safety_evidence_execution_docs",
    srcs = [
        ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-CONTEXT.md",
        ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-RESEARCH.md",
        ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-VALIDATION.md",
        ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-UI-SPEC.md",
        ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-PLAN.md",
    ],
)

alias(
    name = "phase24_verify",
    actual = "//tools/bazel:phase24_verify",
)

alias(
    name = "phase24_verify_tests",
    actual = "//tools/bazel:phase24_verify_tests",
)
"""
        workflow = maybe_workflow if maybe_workflow is not None else """case "$command_name" in
  phase24_verify)
    python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --wiring-only
    python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --quick --output-dir build/ci-evidence/phase24
    ;;
  phase24_verify_tests)
    python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py
    ;;
esac
"""
        justfile = maybe_justfile if maybe_justfile is not None else """phase24-verify:
    bazel run //tools/bazel:phase24_verify_tests
    bazel run //tools/bazel:phase24_verify
"""
        self.write_file(root, "tools/bazel/BUILD.bazel", tools_build)
        self.write_file(root, "BUILD.bazel", root_build)
        self.write_file(root, "tools/bazel/rust_workflow.sh", workflow)
        self.write_file(root, "justfile", justfile)
