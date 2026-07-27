#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase25_live_service_evidence_execution.py"
CONTRACT = "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json"
PHASE16_CONTRACT = "tools/bazel/manifests/phase16_live_network_evidence_contract.json"
PHASE18_CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
PHASE19_CONTRACT = "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json"
PHASE23_CONTRACT = "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json"
PHASE24_CONTRACT = "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json"
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase25"


class Phase25ExecutionTestSupport:

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        shutil.copy2(
            VERIFIER,
            root / "tools/bazel/phase25_live_service_evidence_execution.py")
        shutil.copy2(
            ROOT / "tools/bazel/phase25_execution_policy.py",
            root / "tools/bazel/phase25_execution_policy.py",
        )
        shutil.copy2(
            ROOT / "tools/bazel/phase25_execution_contract.py",
            root / "tools/bazel/phase25_execution_contract.py",
        )
        for path in [
                CONTRACT, PHASE16_CONTRACT, PHASE18_CONTRACT, PHASE19_CONTRACT,
                PHASE23_CONTRACT, PHASE24_CONTRACT
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
        verifier = root / "tools/bazel/phase25_live_service_evidence_execution.py"
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

    def read_phase16_contract(self, root: Path) -> dict[str, object]:
        return self.read_json(root, PHASE16_CONTRACT)

    def write_evidence_input(
        self,
        root: Path,
        rows: list[dict[str, object]],
        path: str = "phase25-evidence-input.json",
        maybe_packet_updates: dict[str, object] | None = None,
    ) -> str:
        packet = {
            "live_service_evidence_packet": {
                "completed_at": "2026-06-23T22:00:00Z",
                "evidence_run_id": "live-service-run-2026-06-23",
                "firmware_identity": {
                    "build_id": "fw-test-build",
                    "firmware_basename": "firmware.bin",
                },
                "operator": "maintainer",
                "phase": "25-live-service-evidence-execution",
                "phase_lifecycle_id": "25-2026-06-23T21-12-42",
                "scenario_results": rows,
                "source_contract_ref": PHASE16_CONTRACT,
                "started_at": "2026-06-23T21:00:00Z",
            }
        }
        if maybe_packet_updates is not None:
            packet["live_service_evidence_packet"].update(maybe_packet_updates)
        self.write_json(root, path, packet)
        return path

    def complete_rows(self, root: Path) -> list[dict[str, object]]:
        contract = self.read_phase16_contract(root)
        rows: list[dict[str, object]] = []
        for scenario in contract["scenarios"]:
            source_status = "passed" if "passed" in scenario[
                "allowed_statuses"] else "source-contract-passed"
            proof_scope = str(scenario["proof_scope"])
            rows.append({
                "artifact_refs": [f"external://phase25/{scenario['id']}.log"],
                "device":
                f"device-{scenario['id']}",
                "evidence_type":
                "source-contract-validation" if proof_scope
                == "source-contract" else "controlled-service-observation",
                "firmware_build":
                "fw-test-build",
                "mode":
                scenario["mode"],
                "operator":
                "maintainer",
                "redaction_status":
                "passed",
                "redaction_summary":
                "Credentials, payloads, and raw service logs were redacted into metadata classes.",
                "residual_risk":
                "known residual risk recorded",
                "scenario_id":
                scenario["id"],
                "service_surface":
                scenario["service_surface"],
                "source_ref_status":
                "passed",
                "source_status":
                source_status,
                "status":
                "passed",
                "status_reason":
                "real live-service evidence passed",
                "timestamp":
                "2026-06-23T21:30:00Z",
            })
        return rows

    def traceability_row_index(self, rows: list[dict[str, object]]) -> int:
        for index, row in enumerate(rows):
            if row["scenario_id"] == "live-contract-traceability-redaction-boundary":
                return index
        self.fail("expected the traceability boundary scenario")

    def write_phase25_wiring(
        self,
        root: Path,
        maybe_tools_build: str | None = None,
        maybe_root_build: str | None = None,
        maybe_workflow: str | None = None,
        maybe_justfile: str | None = None,
    ) -> None:
        tools_build = maybe_tools_build if maybe_tools_build is not None else """filegroup(
    name = "phase25_source_ref_manifests",
    srcs = [
        "manifests/phase16_live_network_evidence_contract.json",
        "manifests/phase18_cutover_review_contract.json",
        "manifests/phase19_aggregate_ci_evidence_contract.json",
        "manifests/phase23_simulator_evidence_execution_contract.json",
        "manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
        "manifests/phase25_live_service_evidence_execution_contract.json",
    ],
)

shell_binary(
    name = "phase25_verify",
    src = "rust_workflow.sh",
    data = [
        "phase25_live_service_evidence_execution.py",
        "manifests/phase25_live_service_evidence_execution_contract.json",
        ":phase25_source_ref_manifests",
        "//:phase25_live_service_evidence_execution_docs",
    ],
)

shell_binary(
    name = "phase25_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase25_live_service_evidence_execution.py",
        "phase25_live_service_evidence_execution_test.py",
        "manifests/phase25_live_service_evidence_execution_contract.json",
        ":phase25_source_ref_manifests",
    ],
)
"""
        root_build = maybe_root_build if maybe_root_build is not None else """filegroup(
    name = "phase25_live_service_evidence_execution_docs",
    srcs = [
        ".planning/phases/25-live-service-evidence-execution/25-CONTEXT.md",
        ".planning/phases/25-live-service-evidence-execution/25-RESEARCH.md",
        ".planning/phases/25-live-service-evidence-execution/25-VALIDATION.md",
        ".planning/phases/25-live-service-evidence-execution/25-01-PLAN.md",
    ],
)

alias(
    name = "phase25_verify",
    actual = "//tools/bazel:phase25_verify",
)

alias(
    name = "phase25_verify_tests",
    actual = "//tools/bazel:phase25_verify_tests",
)
"""
        workflow = maybe_workflow if maybe_workflow is not None else """case "$command_name" in
  phase25_verify)
    python3 tools/bazel/phase25_live_service_evidence_execution.py --wiring-only
    python3 tools/bazel/phase25_live_service_evidence_execution.py --quick --output-dir build/ci-evidence/phase25
    ;;
  phase25_verify_tests)
    python3 tools/bazel/phase25_live_service_evidence_execution_test.py
    ;;
esac
"""
        justfile = maybe_justfile if maybe_justfile is not None else """phase25-verify:
    bazel run //tools/bazel:phase25_verify_tests
    bazel run //tools/bazel:phase25_verify
"""
        self.write_file(root, "tools/bazel/BUILD.bazel", tools_build)
        self.write_file(root, "BUILD.bazel", root_build)
        self.write_file(root, "tools/bazel/rust_workflow.sh", workflow)
        self.write_file(root, "justfile", justfile)
