#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase28_final_readiness_packet.py"
CONTRACT = "tools/bazel/manifests/phase28_final_readiness_packet_contract.json"
PHASE18_CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
PHASE26_CONTRACT = "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
PHASE27_CONTRACT = "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
PHASE26_ROWS = "build/ci-evidence/phase26/upstream-result-row-table.json"
PHASE27_HANDOFF = "build/ci-evidence/phase27/phase28-handoff-manifest.json"
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase28"
WIRING_FILES = [
    "BUILD.bazel",
    "tools/bazel/BUILD.bazel",
    "tools/bazel/rust_workflow.sh",
    "justfile",
]
REQUIRED_REQUIREMENTS = ["READ-01", "READ-02", "READ-03"]
REQUIRED_CRITERIA = [
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
GENERATED_ARTIFACTS = [
    "final-readiness-run-manifest.json",
    "final-readiness-packet.json",
    "normalized-readiness-criteria-table.json",
    "blocker-summary.json",
    "exception-residual-risk-summary.json",
    "reference-demotion-authorization-record.json",
    "demotion-decision-input-template.json",
    "redacted-readiness-report.md",
    "artifact-reference-summary.json",
    "contract-snapshots/phase18_cutover_review_contract.json",
    "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase26-upstream-result-row-table.json",
    "contract-snapshots/phase27-phase28-handoff-manifest.json",
]


class Phase28ReadinessTestSupport:

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for path in [
                VERIFIER,
                ROOT / "tools/bazel/phase28_readiness_contract.py",
                ROOT / "tools/bazel/phase28_readiness_policy.py",
                ROOT / CONTRACT,
                ROOT / PHASE18_CONTRACT,
                ROOT / PHASE26_CONTRACT,
                ROOT / PHASE27_CONTRACT,
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
        verifier = root / "tools/bazel/phase28_final_readiness_packet.py"
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
                                                           object]) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        return path

    def write_text(self, root: Path, path: str, text: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_wiring_files(self, root: Path) -> None:
        for path in WIRING_FILES:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, destination)

    def phase18_requirements(self, root: Path) -> dict[str, dict[str, object]]:
        contract = self.read_json(root, PHASE18_CONTRACT)
        return {
            row["criterion_id"]: row
            for row in contract["upstream_result_requirements"]
        }

    def phase26_rows(self, root: Path) -> list[dict[str, object]]:
        requirements = self.phase18_requirements(root)
        rows = []
        for criterion_id in REQUIRED_CRITERIA:
            requirement = requirements[criterion_id]
            status = "blocked" if criterion_id == "final-reference-demotion-allowed" else "passed"
            failure_reason = (
                "Reference demotion requires explicit Phase 28 maintainer input."
                if criterion_id == "final-reference-demotion-allowed" else
                "none")
            rows.append({
                "criterion_id":
                criterion_id,
                "evidence_family":
                requirement["evidence_family"],
                "requirement_ids":
                requirement["requirement_ids"],
                "source_requirement_ids": ["REV-01"],
                "owning_phase":
                requirement["source_phase"],
                "source_lifecycle_id":
                requirement["source_lifecycle_id"],
                "source_lifecycle_status":
                "current",
                "evidence_refs":
                requirement["required_manifest_refs"],
                "artifact_refs": [
                    "build/ci-evidence/phase26/upstream-result-row-table.json",
                    "build/ci-evidence/phase26/upstream-result-manifest.json",
                ],
                "status":
                status,
                "failure_reason":
                failure_reason,
                "redaction_status":
                "passed",
                "source_ref_status":
                "passed",
                "exception_status":
                "none",
                "maintainer_state":
                "blocked" if status == "blocked" else "not-required",
                "generated_at_utc":
                "2026-06-25T04:00:00Z",
            })
        return rows

    def consumed_phase26_rows(self, root: Path) -> list[dict[str, object]]:
        rows = self.phase26_rows(root)
        consumed_rows = {
            "final-simulator-evidence": {
                "artifact_refs": [
                    "external://phase23/simulator/startup-log.json",
                    "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                ],
                "evidence_refs": [
                    "build/ci-evidence/phase23/simulator-result-manifest.json",
                    "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                ],
                "requirement_ids": ["EVID-01", "ACPT-01"],
            },
            "final-hardware-safety-media-evidence": {
                "artifact_refs": [
                    "external://phase24/hardware/safety-report.json",
                    "build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json",
                ],
                "evidence_refs": [
                    "build/ci-evidence/phase24/hardware-media-safety-result-manifest.json",
                    "build/ci-evidence/phase24/upstream-hardware-media-safety-result-row.json",
                ],
                "requirement_ids": ["EVID-02", "ACPT-01"],
            },
            "final-live-network-transfer-evidence": {
                "artifact_refs": [
                    "external://phase25/live-service/connect-report.json",
                    "build/ci-evidence/phase25/upstream-live-service-result-row.json",
                ],
                "evidence_refs": [
                    "build/ci-evidence/phase25/live-service-result-manifest.json",
                    "build/ci-evidence/phase25/upstream-live-service-result-row.json",
                ],
                "requirement_ids": ["EVID-03", "ACPT-01"],
            },
        }
        for row in rows:
            maybe_consumed = consumed_rows.get(str(row["criterion_id"]))
            if maybe_consumed is not None:
                row.update(maybe_consumed)
        return rows

    def exception_metadata(
            self,
            criterion_id: str = "final-ci-evidence") -> dict[str, object]:
        return {
            "scope":
            f"phase28-test-{criterion_id}",
            "owner":
            "phase28-test-maintainer",
            "approver":
            "phase28-test-maintainer",
            "approver_role":
            "release-maintainer",
            "rationale":
            "A documented temporary exception covers this Phase 28 test row.",
            "affected_printer_or_release_surface":
            "supported-release-surface",
            "evidence_refs": [
                f"build/ci-evidence/phase27/exception-decision-register.json#{criterion_id}"
            ],
            "residual_risk":
            "Exception residual risk is explicitly documented.",
            "mitigation_or_follow_up":
            "Review before final release signoff.",
            "expiry_or_review_trigger":
            "before-reference-demotion-decision",
        }

    def phase27_final_rows(
            self, phase26_rows: list[dict[str,
                                          object]]) -> list[dict[str, object]]:
        rows = []
        for row in phase26_rows:
            criterion_id = str(row["criterion_id"])
            status = "blocked" if criterion_id == "final-reference-demotion-allowed" else "passed"
            rows.append({
                "criterion_id":
                criterion_id,
                "decision_id":
                f"phase27-final-readiness-{criterion_id}",
                "decision":
                "pending" if status == "blocked" else "approve",
                "status":
                status,
                "demotion_authorization":
                "blocked",
                "evidence_state":
                row["status"],
                "evidence_refs":
                row["evidence_refs"],
                "artifact_refs":
                row["artifact_refs"],
                "exception": {
                    "status": "none"
                },
                "exception_state":
                "none",
                "hard_failure_reasons": [],
                "hard_failure_state":
                "none",
                "maintainer_decision":
                "pending" if status == "blocked" else "approve",
                "approver":
                "phase27-test-maintainer" if status == "passed" else "",
                "approver_role":
                "release-maintainer" if status == "passed" else "",
                "decision_timestamp":
                "2026-06-25T04:00:00Z" if status == "passed" else "",
                "rationale":
                str(row["failure_reason"]),
                "redaction_summary":
                "redaction_status=passed",
                "residual_risk":
                "Reviewed by Phase 27 test fixture." if status == "passed" else
                "Pending Phase 28 demotion decision.",
                "residual_risk_state":
                "reviewed" if status == "passed" else "unreviewed",
            })
        return rows

    def write_phase_inputs(
        self,
        root: Path,
        phase26_rows: list[dict[str, object]] | None = None,
        phase27_rows: list[dict[str, object]] | None = None,
    ) -> None:
        phase26_rows = phase26_rows or self.phase26_rows(root)
        phase27_rows = phase27_rows or self.phase27_final_rows(phase26_rows)
        self.write_json(root, PHASE26_ROWS, {"rows": phase26_rows})
        self.write_json(
            root,
            PHASE27_HANDOFF,
            {
                "phase":
                "27-retained-code-and-maintainer-acceptance-decisions",
                "phase_lifecycle_id": "27-2026-06-25T01-06-06",
                "demotion_authorization": "blocked",
                "phase27_may_authorize_demotion": False,
                "phase28_required_decision":
                "explicit-maintainer-reference-demotion-decision",
                "blocked_criteria": ["final-reference-demotion-allowed"],
            },
        )
        residual_rows = [{
            "row_id":
            row["criterion_id"],
            "row_type":
            "final_readiness_decision",
            "owner":
            row.get("approver", ""),
            "residual_risk":
            row.get("residual_risk", "Pending review."),
            "residual_risk_state":
            row.get("residual_risk_state", "unreviewed"),
        } for row in phase27_rows]
        exception_rows = [{
            "row_id": row["criterion_id"],
            "row_type": "final_readiness_decision",
            "owner": "phase28-test-maintainer",
            "exception": row["exception"],
        } for row in phase27_rows if row.get("exception_state") in
                          {"approved-exception", "exception-approved"}]
        self.write_json(
            root,
            "build/ci-evidence/phase27/final-readiness-decision-summary.json",
            {"rows": phase27_rows})
        self.write_json(
            root, "build/ci-evidence/phase27/residual-risk-register.json",
            {"rows": residual_rows})
        self.write_json(
            root, "build/ci-evidence/phase27/exception-decision-register.json",
            {"rows": exception_rows})
        self.write_json(
            root,
            "build/ci-evidence/phase27/artifact-reference-summary.json",
            {
                "phase26_upstream_rows":
                PHASE26_ROWS,
                "artifact_refs": [{
                    "path":
                    "build/ci-evidence/phase27/final-readiness-decision-summary.json",
                    "purpose":
                    "phase27-final-readiness-decision-evidence",
                }],
            },
        )
        self.write_json(
            root,
            "build/ci-evidence/phase27/decision-row-table.json",
            {
                "rows": [{
                    "row_id": row["criterion_id"],
                    "row_type": "final_readiness_decision",
                    "decision": row["decision"],
                    "status": row["status"],
                    "demotion_authorization": "blocked",
                    "hard_failure_state": row["hard_failure_state"],
                    "maintainer_decision": row["maintainer_decision"],
                } for row in phase27_rows]
            },
        )

    def demotion_decision(self,
                          authorization: str = "approved"
                          ) -> dict[str, object]:
        return {
            "phase":
            "28-final-readiness-packet-and-demotion-gate",
            "phase_lifecycle_id":
            "28-2026-06-25T03-31-49",
            "demotion_authorization":
            authorization,
            "approver":
            "phase28-test-maintainer",
            "approver_role":
            "release-maintainer",
            "decision_timestamp":
            "2026-06-25T05:00:00Z",
            "rationale":
            "Maintainer explicitly reviewed the Phase 28 packet.",
            "scope":
            "supported-printer-release-surface",
            "evidence_refs": [
                "build/ci-evidence/phase28/final-readiness-packet.json#reference-demotion-gate"
            ],
        }
