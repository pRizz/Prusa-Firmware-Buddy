#!/usr/bin/env python3
from __future__ import annotations

from phase35_test_support import (
    AUDIT_KINDS,
    CONTRACT,
    PHASE32_REGISTER,
    ROOT,
    Path,
    json,
    phase35,
    shutil,
    tempfile,
    unittest,
)

class Phase35TestSupport(unittest.TestCase):

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

from phase35_cutover_decision_cases_test import (
    Phase35CutoverDecisionCasesMixin,
)
from phase35_cutover_decision_failure_test import (
    Phase35CutoverDecisionFailureMixin,
)
from phase35_cutover_decision_security_test import (
    Phase35CutoverDecisionSecurityMixin,
)


class Phase35CutoverDecisionArtifactTest(
        Phase35CutoverDecisionCasesMixin,
        Phase35CutoverDecisionFailureMixin,
        Phase35CutoverDecisionSecurityMixin,
        Phase35TestSupport):
    pass


from phase35_guarded_publication_test import Phase35GuardedPublicationTest
from phase35_source_failure_replacement_test import (
    Phase35SourceFailureReplacementTest,
)

if __name__ == "__main__":
    unittest.main()
