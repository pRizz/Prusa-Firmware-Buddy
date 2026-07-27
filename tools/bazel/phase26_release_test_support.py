#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
import shutil
import subprocess
import tempfile
from types import ModuleType
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase26_release_signing_upstream_evidence.py"
CONTRACT = "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
PHASE17_CONTRACT = "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json"
PHASE18_CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
PHASE20_CONTRACT = "tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json"
PHASE20_TEMPLATE = "tools/bazel/manifests/phase20_release_environment_inputs.template.json"
PHASE23_CONTRACT = "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json"
PHASE24_CONTRACT = "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json"
PHASE25_CONTRACT = "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json"
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase26"
REQUIRED_UPSTREAM_CRITERIA = {
    "final-ci-evidence",
    "final-simulator-evidence",
    "final-hardware-safety-media-evidence",
    "final-live-network-transfer-evidence",
    "final-release-artifact-signing-evidence",
    "final-retained-code-acceptance",
    "final-residual-risk-review",
    "final-maintainer-decision",
    "final-reference-demotion-allowed",
}
REQUIRED_UPSTREAM_FIELDS = {
    "criterion_id",
    "evidence_family",
    "requirement_ids",
    "source_requirement_ids",
    "owning_phase",
    "source_lifecycle_id",
    "source_lifecycle_status",
    "evidence_refs",
    "artifact_refs",
    "status",
    "failure_reason",
    "redaction_status",
    "source_ref_status",
    "exception_status",
    "maintainer_state",
    "generated_at_utc",
}
RETAINED_OUTPUTS = [
    "release-upstream-run-manifest.json",
    "normalized-release-evidence-summary.json",
    "upstream-result-row-table.json",
    "upstream-result-manifest.json",
    "redaction-provenance-summary.json",
    "artifact-reference-summary.json",
    "operator-release-input-template.json",
    "contract-snapshots/phase17_release_candidate_evidence_contract.json",
    "contract-snapshots/phase18_cutover_review_contract.json",
    "contract-snapshots/phase20_release_candidate_artifacts_contract.json",
    "contract-snapshots/phase20_release_environment_inputs.template.json",
]
WIRING_FILES = [
    "BUILD.bazel", "tools/bazel/BUILD.bazel", "tools/bazel/rust_workflow.sh",
    "justfile"
]
REQUIRED_ROW_IDS = [
    "rel-bin-firmware-image",
    "rel-bbf-firmware-package",
    "rel-dfu-update-package",
    "rel-map-and-provenance",
    "rel-resource-image-package",
    "rel-language-bundles",
    "rel-wui-assets",
    "rel-esp-packages",
    "rel-mmu-package",
    "rel-auxiliary-dwarf-firmware",
    "rel-auxiliary-modularbed-firmware",
    "rel-auxiliary-xbuddy-extension-firmware",
    "rel-package-manifests",
    "rel-signing-key-identity",
    "rel-build-input-identity",
    "rel-artifact-retention",
    "rel-reference-comparison-report",
    "rel-contract-traceability-redaction-boundary",
]


class Phase26ReleaseTestSupport:

    @classmethod
    def load_verifier_module(cls) -> ModuleType:
        spec = importlib.util.spec_from_file_location(
            "phase26_release_signing_upstream_evidence", VERIFIER)
        if spec is None or spec.loader is None:
            raise RuntimeError("failed to load Phase 26 verifier module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for path in [
                VERIFIER,
                ROOT / "tools/bazel/phase26_release_contract.py",
                ROOT / "tools/bazel/phase26_release_policy.py",
                ROOT / "tools/bazel/phase26_upstream_policy.py",
                ROOT / CONTRACT,
                ROOT / PHASE17_CONTRACT,
                ROOT / PHASE18_CONTRACT,
                ROOT / PHASE20_CONTRACT,
                ROOT / PHASE20_TEMPLATE,
                ROOT / PHASE23_CONTRACT,
                ROOT / PHASE24_CONTRACT,
                ROOT / PHASE25_CONTRACT,
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
        verifier = root / "tools/bazel/phase26_release_signing_upstream_evidence.py"
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

    def write_release_input(self,
                            root: Path,
                            rows: list[dict[str, object]],
                            path: str = "release-input.json") -> str:
        input_path = root / path
        input_path.write_text(
            json.dumps({"evidence_rows": rows}, indent=2, sort_keys=True) +
            "\n",
            encoding="utf-8")
        return path

    def write_json(self, root: Path, path: str, data: dict[str,
                                                           object]) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        return path

    def write_file(self, root: Path, path: str, text: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_wiring_files(self, root: Path) -> None:
        for path in WIRING_FILES:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, destination)

    def phase20_required_metadata_fields(
            self, contract_row: dict[str, object]) -> list[str]:
        fields: list[str] = []
        for group in [
                "release_metadata_required",
                "signing_metadata_required",
                "provenance_metadata_required",
                "retention_metadata_required",
        ]:
            values = contract_row.get(group, [])
            if isinstance(values, list):
                fields.extend(str(value) for value in values)
        return list(dict.fromkeys(fields))

    def release_metadata_value(self, field: str, row_id: str,
                               artifact_ref: str) -> object:
        if field == "artifact_refs":
            return [artifact_ref]
        if field == "retention_refs":
            return ["external://phase20/retention/phase26-approved-run-001"]
        if field == "subject_digests":
            return [{
                "artifact_ref": artifact_ref,
                "sha256": "a" * 64,
            }]
        if field == "key_identity_ref":
            return "release-key-fingerprint:sha256:phase26-test"
        if field == "signing_mode":
            return "external-release-signing"
        return f"phase26-test-{field.replace('_', '-')}:{row_id}"

    def complete_release_rows(self, root: Path) -> list[dict[str, object]]:
        contract = self.read_json(root, PHASE20_CONTRACT)
        contract_rows = contract["rows"]
        contract_by_id = {
            str(row["id"]): row
            for row in contract_rows if isinstance(row, dict)
        }
        rows: list[dict[str, object]] = []
        for row_id in REQUIRED_ROW_IDS:
            contract_row = contract_by_id[row_id]
            artifact_ref = f"external://phase20/artifacts/{row_id}.json"
            artifact_surface = str(contract_row["artifact_surface"])
            row = {
                "id":
                row_id,
                "artifact_refs": [artifact_ref],
                "artifact_surface":
                artifact_surface,
                "affected_artifact_surface":
                artifact_surface,
                "build_input_identity":
                "git:phase26-test-build;bazel:phase17_release_candidate_artifacts",
                "mismatch_class":
                "pass",
                "mismatch_reason":
                "Approved release metadata matched the archived reference classification.",
                "operator":
                "phase26-test-operator",
                "owner_phase":
                "20-release-candidate-artifact-production",
                "proof_class":
                "approved-release-run",
                "release_run_id":
                "phase26-approved-run-001",
                "residual_risk":
                "Limited to supplied release-environment evidence.",
                "retention_refs":
                ["external://phase20/retention/phase26-approved-run-001"],
                "status":
                "passed",
                "subject_digests": [{
                    "artifact_ref": artifact_ref,
                    "sha256": "a" * 64,
                }],
                "timestamp":
                "2026-06-24T14:00:00Z",
                "verification_outcome":
                "approved-release-metadata",
            }
            for field in self.phase20_required_metadata_fields(contract_row):
                if field not in row:
                    row[field] = self.release_metadata_value(
                        field, row_id, artifact_ref)
            rows.append(row)
        return rows

    def upstream_row(self, phase: str, criterion_id: str, requirement_id: str,
                     output_root: str, artifact_ref: str) -> dict[str, object]:
        evidence_family = {
            "EVID-01": "simulator",
            "EVID-02": "hardware",
            "EVID-03": "live-service",
        }[requirement_id]
        return {
            "artifact_refs": [artifact_ref],
            "criterion_id": criterion_id,
            "evidence_family": evidence_family,
            "manifest_ref": f"{output_root}/result-manifest.json",
            "phase": phase,
            "phase_lifecycle_id": f"{phase}-test-lifecycle",
            "redaction_status": "passed",
            "requirement_ids": [requirement_id],
            "source_ref_status": "passed",
            "status": "passed",
        }

    def write_valid_upstream_rows(self, root: Path) -> dict[str, str]:
        return {
            "phase23":
            self.write_json(
                root,
                "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                self.upstream_row(
                    "23-simulator-evidence-execution",
                    "final-simulator-evidence",
                    "EVID-01",
                    "build/ci-evidence/phase23",
                    "external://phase23/simulator/startup-log.json",
                ),
            ),
            "phase24":
            self.write_json(
                root,
                "build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json",
                self.upstream_row(
                    "24-hardware-media-and-safety-evidence-execution",
                    "final-hardware-safety-media-evidence",
                    "EVID-02",
                    "build/ci-evidence/phase24",
                    "external://phase24/hardware/safety-report.json",
                ),
            ),
            "phase25":
            self.write_json(
                root,
                "build/ci-evidence/phase25/upstream-live-service-result-row.json",
                self.upstream_row(
                    "25-live-service-evidence-execution",
                    "final-live-service-evidence",
                    "EVID-03",
                    "build/ci-evidence/phase25",
                    "external://phase25/live-service/connect-report.json",
                ),
            ),
        }
