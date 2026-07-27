#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib
import textwrap
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from collections.abc import Callable
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "tools/bazel").as_posix())

import phase35_cutover_decision_artifact as phase35
import phase38_cutover_workflow as workflow

CONTRACT = ROOT / "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json"
PHASE32_REGISTER = "build/ci-evidence/phase32/blocker-register.json"
PHASE33_NORMALIZED_REGISTER = "build/ci-evidence/phase33/normalized-decision-records.json"
PHASE33_EXCEPTION_REGISTER = "build/ci-evidence/phase33/exception-decision-register.json"
PHASE33_RESIDUAL_REGISTER = "build/ci-evidence/phase33/residual-risk-decision-register.json"
PHASE34_LEDGER = "build/ci-evidence/phase34/readiness-coverage-ledger.json"

VERDICTS = ["approved", "blocked", "approved-with-exceptions"]
ROUTES = ["production-cutover-planning", "targeted-blocker-repair"]
AUDIT_KINDS = [
    "evidence-packet",
    "blocker",
    "exception",
    "residual-risk",
    "retained-code-decision",
    "readiness-decision",
    "readiness-result",
    "demotion-decision",
    "demotion-dry-run",
]
AUDIT_REQUIRED_FIELDS = [
    "link_id",
    "kind",
    "target_id",
    "target_ref",
    "source_phase_lifecycle_id",
    "verdict_effect",
]
BLOCKED_REASONS = [
    "source-artifact-missing",
    "source-artifact-malformed",
    "source-artifact-stale",
    "source-artifact-duplicate",
    "source-artifact-lifecycle-mismatched",
    "redaction-failed",
    "source-ref-failed",
    "secret-tainted",
    "unsafe-ref",
    "unknown-input",
    "underclassified",
    "coverage-incomplete",
    "readiness-blocked",
    "exception-invalid",
    "audit-link-missing",
    "audit-link-extra",
    "audit-link-duplicate",
    "audit-link-dangling",
    "audit-link-lifecycle-mismatched",
    "audit-link-category-mismatched",
    "audit-link-digest-mismatched",
    "route-scope-incomplete",
]
GENERATED_ARTIFACTS = [
    "cutover-decision-run-manifest.json",
    "cutover-audit-link-index.json",
    "cutover-decision.json",
    "next-milestone-route.json",
    "redacted-cutover-decision-report.md",
    "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
    "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
    "contract-snapshots/phase34-final-readiness-run-manifest.json",
]
DECISION_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "requirement_ids",
    "cutover_verdict",
    "reason_codes",
    "readiness_state",
    "readiness_result_ref",
    "active_exception_ids",
    "blocker_ids",
    "audit_link_index_ref",
    "audit_link_counts_by_kind",
    "demotion_decision_validation_state",
    "demotion_decision_state",
    "demotion_decision_source_refs",
    "demotion_gate_state",
    "demotion_gate_reason_codes",
    "route_ref",
    "raw_evidence_consumed",
]
SOURCE_FAILURE_ARTIFACTS = [
    "cutover-decision-run-manifest.json",
    "cutover-decision.json",
    "next-milestone-route.json",
]
SOURCE_FAILURE_MANIFEST_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "generation_state",
    "output_root",
    "generated_artifacts",
    "source_manifest_ref",
    "source_failure_reason_codes",
    "raw_evidence_consumed",
]
ROUTE_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "route",
    "source_verdict",
    "follow_up_scope",
    "requires_fresh_cutover_decision",
    "planning_only",
    "production_actions_authorized",
]


class Phase35CutoverDecisionArtifactTest(unittest.TestCase):

    def contract(self) -> dict[str, object]:
        return json.loads(CONTRACT.read_text(encoding="utf-8"))

    def valid_facts(self) -> dict[str, object]:
        return {
            "readiness_state": "unblocked",
            "reason_codes": [],
            "active_exception_ids": [],
            "exceptions": [],
        }

    def exception(
        self,
        decision_id: str = "exception-1",
        *,
        decision_value: str = "approve",
        decision_timestamp: str = "2026-07-25T20:00:00Z",
        lifecycle: str = "33-2026-07-04T01-36-41",
    ) -> dict[str, object]:
        source_row_refs = [f"{PHASE32_REGISTER}#blocker-1"]
        return {
            "decision_id": decision_id,
            "decision_type": "exception",
            "decision_value": decision_value,
            "source_row_refs": source_row_refs,
            "maintainer_identity_ref": "maintainer://alice",
            "maintainer_role": "cutover-maintainer",
            "owner_signoff_ref": "owner://signoff/alice",
            "decision_timestamp": decision_timestamp,
            "phase_lifecycle_id": lifecycle,
            "scope": "exact",
            "expiry_or_review_trigger": "review-before-cutover",
            "affected_gates": ["final-simulator-evidence"],
            "linked_blocker_refs": source_row_refs,
        }

    def audit_sources(self) -> list[dict[str, object]]:
        sources = []
        lifecycle_by_kind = {
            "evidence-packet": "31-2026-07-03T02-04-07",
            "blocker": "32-2026-07-03T14-13-51",
            "exception": "33-2026-07-04T01-36-41",
            "residual-risk": "33-2026-07-04T01-36-41",
            "retained-code-decision": "33-2026-07-04T01-36-41",
            "readiness-decision": "33-2026-07-04T01-36-41",
            "readiness-result": "34-2026-07-25T18-18-48",
            "demotion-decision": "33-2026-07-04T01-36-41",
            "demotion-dry-run": "34-2026-07-25T18-18-48",
        }
        for index, kind in enumerate(AUDIT_KINDS):
            sources.append({
                "kind":
                kind,
                "target_id":
                f"target-{index}",
                "target_ref":
                f"build/ci-evidence/phase34/sanitized-{index}.json",
                "source_phase_lifecycle_id":
                lifecycle_by_kind[kind],
                "verdict_effect":
                "supports" if kind == "evidence-packet" else "blocks",
                "digest_source": {
                    "kind": kind,
                    "target": index
                },
            })
        return sources

    def demotion_decision(
        self,
        *,
        decision_value: str = "approve",
        decision_timestamp: str = "2026-07-25T20:00:00Z",
        lifecycle: str = "33-2026-07-04T01-36-41",
    ) -> dict[str, object]:
        return {
            "decision_id": "demotion-1",
            "decision_type": "reference_demotion",
            "decision_value": decision_value,
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "decision_timestamp": decision_timestamp,
            "phase_lifecycle_id": lifecycle,
        }

    def demotion_handoff(
        self,
        *,
        supplied: bool = True,
        lifecycle: str = "33-2026-07-04T01-36-41",
    ) -> dict[str, object]:
        return {
            "phase":
            "33-maintainer-decision-inputs",
            "phase_lifecycle_id":
            lifecycle,
            "demotion_input_supplied":
            supplied,
            "decision_id":
            "demotion-1" if supplied else "",
            "source_row_refs":
            [f"{PHASE32_REGISTER}#blocker-1"] if supplied else [],
        }

    def demotion_dry_run(
        self,
        *,
        readiness_state: str = "unblocked",
        gate_state: str = "blocked",
        approval_validation_state: str = "valid",
        approval_decision_state: str = "approve",
        reason_codes: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "readiness_state": readiness_state,
            "gate_state": gate_state,
            "reason_codes":
            ["readiness-blocked"] if reason_codes is None else reason_codes,
            "approval_validation_state": approval_validation_state,
            "approval_decision_state": approval_decision_state,
            "source_refs": [f"{PHASE32_REGISTER}#blocker-1"],
        }

    def blocker_row(
        self,
        *,
        blocker_kind: str = "repair_item",
        row_id: str = "blocker-1",
    ) -> dict[str, object]:
        return {
            "row_id": row_id,
            "blocker_kind": blocker_kind,
            "owner_ref": "maintainer://cutover-owner",
            "required_next_action": "Repair the source-backed blocker.",
            "requirement_ids": ["CUTOVER-01"],
            "affected_gate": "final-simulator-evidence",
        }

    def ledger_row(self, row_id: str = "ledger-1") -> dict[str, object]:
        return {
            "row_id": row_id,
            "classification_ref": f"{PHASE32_REGISTER}#blocker-1",
            "requirement_ids": ["CUTOVER-01"],
            "affected_gates": ["final-simulator-evidence"],
            "reason_codes": ["evidence-failed"],
            "readiness_effect": "blocked",
            "exception_decision_refs": [],
            "residual_risk_decision_refs": [],
        }

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for relative_path in [
                "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json",
                "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json",
        ]:
            source = ROOT / relative_path
            destination = root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return temp_dir, root

    def write_audit_targets(self, root: Path, source: dict[str,
                                                           object]) -> None:
        payloads: dict[str, object] = {}
        for audit_source in phase35.audit_sources_from_bundle(source):
            target_ref = str(audit_source["target_ref"])
            if target_ref.startswith("external://"):
                continue
            target_path, separator, _ = target_ref.partition("#")
            digest_source = audit_source["digest_source"]
            if separator:
                payload = payloads.setdefault(target_path, {"rows": []})
                self.assertIsInstance(payload, dict)
                payload["rows"].append(digest_source)
            else:
                self.assertNotIn(target_path, payloads)
                payloads[target_path] = digest_source
        for target_path, payload in payloads.items():
            phase35.write_json(root / target_path, payload)

    for _module_name in (
            "phase35_cutover_decision_cases_test",
            "phase35_cutover_decision_failure_test",
            "phase35_cutover_decision_security_test",
    ):
        _module = importlib.import_module(_module_name)
        exec(textwrap.dedent(_module.TEST_METHODS), globals(), locals())


for _module_name in (
        "phase35_guarded_publication_test",
        "phase35_source_failure_replacement_test",
):
    _module = importlib.import_module(_module_name)
    exec(_module.TEST_CLASSES, globals())

if __name__ == "__main__":
    unittest.main()
