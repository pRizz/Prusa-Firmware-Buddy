#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
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
WIRING_FILES = [
    "BUILD.bazel", "tools/bazel/BUILD.bazel", "tools/bazel/rust_workflow.sh",
    "justfile"
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


class Phase27DecisionTestSupport:

    @classmethod
    def load_verifier_module(cls) -> ModuleType:
        spec = importlib.util.spec_from_file_location(
            "phase27_retained_code_acceptance_decisions", VERIFIER)
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
                ROOT / "tools/bazel/phase27_decision_contract.py",
                ROOT / "tools/bazel/phase27_decision_policy.py",
                ROOT / "tools/bazel/phase27_decision_normalization.py",
                ROOT / CONTRACT,
                ROOT / PHASE18_CONTRACT,
                ROOT / PHASE26_CONTRACT,
                *[ROOT / source_ref for source_ref in SOURCE_REF_FILES],
        ]:
            destination = root / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        return temp_dir, root

    def run_verifier(
            self,
            args: list[str],
            maybe_root: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
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

    def write_json(self, root: Path, path: str, data: dict[str,
                                                           object]) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")

    def write_text(self, root: Path, path: str, text: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_wiring_files(self, root: Path) -> None:
        for path in WIRING_FILES:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, destination)

    def write_phase26_rows(self, root: Path) -> None:
        phase18_contract = self.read_json(root, PHASE18_CONTRACT)
        rows = []
        for requirement in phase18_contract["upstream_result_requirements"]:
            criterion_id = str(requirement["criterion_id"])
            status = "blocked" if criterion_id == "final-reference-demotion-allowed" else "passed"
            rows.append({
                "artifact_refs":
                [f"build/ci-evidence/phase26/{criterion_id}.json"],
                "criterion_id":
                criterion_id,
                "evidence_family":
                requirement["evidence_family"],
                "evidence_refs":
                list(requirement["required_manifest_refs"]),
                "exception_status":
                "none",
                "failure_reason":
                "phase27 test upstream row",
                "generated_at_utc":
                "2026-06-25T01:30:00Z",
                "maintainer_state":
                "blocked" if status == "blocked" else "pending",
                "owning_phase":
                requirement["source_phase"],
                "redaction_status":
                "passed",
                "requirement_ids":
                list(requirement["requirement_ids"]),
                "source_lifecycle_id":
                requirement["source_lifecycle_id"],
                "source_lifecycle_status":
                "current",
                "source_ref_status":
                "passed",
                "source_requirement_ids":
                list(requirement["requirement_ids"]),
                "status":
                status,
            })
        self.write_json(root, PHASE26_ROWS, {"rows": rows})

    def final_role_for_criterion(self, criterion_id: str) -> str:
        if criterion_id == "final-hardware-safety-media-evidence":
            return "safety-maintainer"
        if criterion_id == "final-live-network-transfer-evidence":
            return "network-security-maintainer"
        if criterion_id in {
                "final-release-artifact-signing-evidence",
                "final-reference-demotion-allowed"
        }:
            return "release-maintainer"
        return "cutover-maintainer"

    def complete_maintainer_input(self, root: Path) -> dict[str, object]:
        phase18_contract = self.read_json(root, PHASE18_CONTRACT)
        retained_rows = []
        for packet in phase18_contract["retained_code_acceptance_packets"]:
            retained_rows.append({
                "packet_id":
                packet["id"],
                "decision":
                "approve",
                "approver":
                "phase27-test-maintainer",
                "approver_role":
                packet["approver_role"],
                "decision_timestamp":
                "2026-06-25T01:45:00Z",
                "rationale":
                "Maintainer reviewed the retained-code packet evidence and residual risk.",
                "evidence_refs":
                list(packet["required_evidence_refs"]),
                "residual_risk":
                "Residual risk accepted for Phase 27 test input.",
                "redaction_summary":
                "name-only references; redaction checks passed",
                "hard_failure_reasons": [],
                "exception": {},
            })
        final_rows = []
        for requirement in phase18_contract["upstream_result_requirements"]:
            criterion_id = str(requirement["criterion_id"])
            status = "blocked" if criterion_id == "final-reference-demotion-allowed" else "passed"
            decision = "reject" if criterion_id == "final-reference-demotion-allowed" else "approve"
            final_rows.append({
                "decision_id":
                f"phase27-final-readiness-{criterion_id}",
                "criterion_id":
                criterion_id,
                "decision":
                decision,
                "status":
                status,
                "approver":
                "phase27-test-maintainer",
                "approver_role":
                self.final_role_for_criterion(criterion_id),
                "decision_timestamp":
                "2026-06-25T01:45:00Z",
                "rationale":
                "Maintainer reviewed the upstream criterion evidence for Phase 27.",
                "evidence_refs":
                list(requirement["required_manifest_refs"]),
                "residual_risk":
                "Residual risk accepted for Phase 27 test input.",
                "exception": {},
                "redaction_summary":
                "name-only references; redaction checks passed",
                "hard_failure_reasons": [],
            })
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

    def write_maintainer_input(
            self,
            root: Path,
            data: dict[str, object],
            path: str = "phase27-maintainer-input.json") -> str:
        self.write_json(root, path, data)
        return path
