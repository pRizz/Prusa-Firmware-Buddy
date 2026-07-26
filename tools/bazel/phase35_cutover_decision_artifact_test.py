#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from collections.abc import Callable
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

import phase35_cutover_decision_artifact as phase35

ROOT = Path(__file__).resolve().parents[2]
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

    def test_cutover_01_contract_identity_lifecycle_and_closed_verdict_enum(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        identity = (
            contract["id"],
            contract["phase"],
            contract["phase_lifecycle_id"],
            contract["output_root"],
        )

        # Assert
        self.assertEqual(
            identity,
            (
                "phase35_cutover_decision_artifact_contract",
                "35-cutover-decision-artifact",
                "35-2026-07-25T21-06-10",
                "build/ci-evidence/phase35",
            ),
        )
        self.assertEqual(contract["requirement_ids"],
                         ["CUTOVER-01", "CUTOVER-02", "CUTOVER-03"])
        self.assertEqual(contract["verdict_enum"], VERDICTS)

    def test_cutover_02_contract_declares_exact_nine_kind_audit_schema(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        schema = contract["audit_link_schema"]

        # Assert
        self.assertEqual(schema["kinds"], AUDIT_KINDS)
        self.assertEqual(schema["required_fields"], AUDIT_REQUIRED_FIELDS)
        self.assertEqual(schema["optional_fields"], ["digest"])
        self.assertTrue(schema["exact_set_required"])

    def test_cutover_03_contract_declares_routes_artifacts_and_no_authority(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        authority = contract["authority_boundaries"]

        # Assert
        self.assertEqual(contract["route_enum"], ROUTES)
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)
        self.assertFalse(authority["accepts_caller_supplied_verdict"])
        self.assertFalse(authority["accepts_cutover_confirmation"])
        self.assertFalse(authority["accepts_demotion_approval"])
        self.assertFalse(authority["production_actions_authorized"])
        self.assertEqual(authority["reference_demotion_requirement"],
                         "POST-01")

    def test_contract_declares_exact_blocked_reasons_and_output_fields(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act / Assert
        self.assertEqual(contract["blocked_reason_codes"], BLOCKED_REASONS)
        self.assertEqual(contract["cutover_decision_fields"], DECISION_FIELDS)
        self.assertEqual(
            contract["demotion_projection"]["decision_validation_states"],
            [
                "missing", "malformed", "stale", "lifecycle-mismatched",
                "invalid", "valid"
            ],
        )
        self.assertEqual(
            contract["demotion_projection"]["decision_states"],
            ["missing", "approve", "reject"],
        )
        self.assertEqual(contract["demotion_projection"]["gate_states"],
                         ["blocked", "open"])

    def test_contract_declares_exact_source_failure_bundle(self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        behavior = contract["source_failure_behavior"]

        # Assert
        self.assertEqual(behavior["generated_artifacts"],
                         SOURCE_FAILURE_ARTIFACTS)
        self.assertEqual(behavior["manifest_fields"],
                         SOURCE_FAILURE_MANIFEST_FIELDS)
        self.assertEqual(behavior["decision_fields"], DECISION_FIELDS)
        self.assertEqual(behavior["route_fields"], ROUTE_FIELDS)
        self.assertEqual(behavior["generation_state"], "blocked-source-error")
        self.assertEqual(behavior["cutover_verdict"], "blocked")
        self.assertEqual(behavior["route"], "targeted-blocker-repair")
        self.assertEqual(behavior["audit_link_counts_by_kind"],
                         {kind: 0
                          for kind in AUDIT_KINDS})
        self.assertEqual(behavior["repair_scope"], [])
        self.assertEqual(behavior["repair_scope_reason_code"],
                         "route-scope-incomplete")
        self.assertEqual(behavior["demotion_decision_validation_state"],
                         "invalid")
        self.assertEqual(behavior["demotion_decision_state"], "missing")
        self.assertEqual(behavior["demotion_decision_source_refs"], [])
        self.assertEqual(behavior["demotion_gate_state"], "blocked")
        self.assertTrue(behavior["requires_fresh_cutover_decision"])
        self.assertTrue(behavior["planning_only"])
        self.assertFalse(behavior["production_actions_authorized"])
        self.assertFalse(behavior["raw_evidence_consumed"])

    def test_cutover_01_truth_table_approves_only_unblocked_without_exceptions(
            self) -> None:
        # Arrange
        facts = self.valid_facts()

        # Act
        result = phase35.evaluate_verdict(facts)

        # Assert
        self.assertEqual(result["cutover_verdict"], "approved")
        self.assertEqual(result["reason_codes"], [])
        self.assertEqual(result["active_exception_ids"], [])

    def test_cutover_01_truth_table_approves_with_exact_active_exceptions(
            self) -> None:
        # Arrange
        facts = self.valid_facts()
        facts["active_exception_ids"] = ["exception-1"]
        facts["exceptions"] = [self.exception()]

        # Act
        result = phase35.evaluate_verdict(facts)

        # Assert
        self.assertEqual(result["cutover_verdict"], "approved-with-exceptions")
        self.assertEqual(result["active_exception_ids"], ["exception-1"])

    def test_cutover_01_truth_table_blocks_readiness_and_all_invalid_families(
            self) -> None:
        for reason_code in BLOCKED_REASONS:
            with self.subTest(reason_code=reason_code):
                # Arrange
                facts = self.valid_facts()
                facts["reason_codes"] = [reason_code]

                # Act
                result = phase35.evaluate_verdict(facts)

                # Assert
                self.assertEqual(result["cutover_verdict"], "blocked")
                self.assertIn(reason_code, result["reason_codes"])

    def test_cutover_01_truth_table_blocks_unknown_or_incomplete_fact_shapes(
            self) -> None:
        cases = [
            {},
            {
                "readiness_state": "unknown",
                "reason_codes": [],
                "active_exception_ids": [],
                "exceptions": []
            },
            {
                "readiness_state": "blocked",
                "reason_codes": [],
                "active_exception_ids": [],
                "exceptions": []
            },
            {
                "readiness_state": "unblocked",
                "reason_codes": [],
                "active_exception_ids": ["missing"],
                "exceptions": []
            },
        ]
        for facts in cases:
            with self.subTest(facts=facts):
                # Arrange / Act
                result = phase35.evaluate_verdict(facts)

                # Assert
                self.assertEqual(result["cutover_verdict"], "blocked")

    def test_cutover_01_exception_boundaries_fail_closed(self) -> None:
        canonical = self.exception()
        cases = [
            ("broad", {
                **canonical, "linked_blocker_refs":
                [f"{PHASE32_REGISTER}#other"]
            }),
            ("unmatched", self.exception(decision_id="other")),
            ("rejected", self.exception(decision_value="reject")),
            ("expired", {
                **canonical, "expiry_or_review_trigger": ""
            }),
            ("stale",
             self.exception(decision_timestamp="2020-01-01T00:00:00Z")),
            ("invalid", {
                **canonical, "owner_signoff_ref": ""
            }),
        ]
        for case_name, exception in cases:
            with self.subTest(case=case_name):
                # Arrange
                facts = self.valid_facts()
                facts["active_exception_ids"] = ["exception-1"]
                facts["exceptions"] = [exception]

                # Act
                result = phase35.evaluate_verdict(facts)

                # Assert
                self.assertEqual(result["cutover_verdict"], "blocked")
                self.assertIn("exception-invalid", result["reason_codes"])

    def test_cutover_01_legacy_fields_cannot_override_canonical_validation(
            self) -> None:
        # Arrange
        facts = self.valid_facts()
        facts["active_exception_ids"] = ["exception-1"]
        facts["exceptions"] = [{
            **self.exception(decision_timestamp="2020-01-01T00:00:00Z"),
            "validation_state":
            "valid",
            "active":
            True,
            "exact_scope":
            True,
        }]

        # Act
        result = phase35.evaluate_verdict(facts)

        # Assert
        self.assertEqual(result["cutover_verdict"], "blocked")
        self.assertIn("exception-invalid", result["reason_codes"])

    def test_cutover_01_phase34_ledger_is_the_active_exception_authority(
            self) -> None:
        # Arrange
        ledger = [{
            "coverage_state":
            "exception-covered",
            "exception_decision_refs": [
                "build/ci-evidence/phase33/normalized-decision-records.json#exception-1"
            ],
        }, {
            "coverage_state":
            "exception-uncovered",
            "exception_decision_refs": [
                "build/ci-evidence/phase33/normalized-decision-records.json#exception-2"
            ],
        }]

        # Act
        active_ids = phase35.active_exception_ids_from_ledger(ledger)

        # Assert
        self.assertEqual(active_ids, ["exception-1"])

    def test_cutover_03_route_truth_table_is_exclusive_and_planning_only(
            self) -> None:
        expected = {
            "approved": ("production-cutover-planning", False),
            "blocked": ("targeted-blocker-repair", True),
            "approved-with-exceptions": ("targeted-blocker-repair", True),
        }
        for verdict, (route_name, requires_fresh) in expected.items():
            with self.subTest(verdict=verdict):
                # Arrange / Act
                route = phase35.build_route(verdict, [])

                # Assert
                self.assertEqual(route["route"], route_name)
                self.assertEqual(route["source_verdict"], verdict)
                self.assertEqual(route["requires_fresh_cutover_decision"],
                                 requires_fresh)
                self.assertTrue(route["planning_only"])
                self.assertFalse(route["production_actions_authorized"])

    def test_t_35_01_audit_links_cover_all_nine_categories_deterministically(
            self) -> None:
        # Arrange
        sources = list(reversed(self.audit_sources()))

        # Act
        first = phase35.derive_audit_links(sources)
        second = phase35.derive_audit_links(copy.deepcopy(sources))

        # Assert
        self.assertEqual(first, second)
        self.assertEqual([link["kind"] for link in first], AUDIT_KINDS)
        self.assertEqual({link["kind"] for link in first}, set(AUDIT_KINDS))
        for link in first:
            self.assertEqual(list(link)[:6], AUDIT_REQUIRED_FIELDS)
            self.assertRegex(link["link_id"], r"^audit-[a-z0-9-]+$")
            self.assertRegex(link["digest"], r"^[0-9a-f]{64}$")

    def test_t_35_01_external_audit_refs_omit_digest(self) -> None:
        # Arrange
        sources = self.audit_sources()
        sources[0]["target_ref"] = "external://phase31/sanitized-packet"

        # Act
        links = phase35.derive_audit_links(sources)
        external_link = next(link for link in links
                             if link["kind"] == "evidence-packet")

        # Assert
        self.assertNotIn("digest", external_link)

    def test_t_35_01_exact_set_anti_join_blocks_every_mismatch(self) -> None:
        expected = phase35.derive_audit_links(self.audit_sources())
        mutations = {}
        mutations["audit-link-missing"] = expected[1:]
        mutations["audit-link-extra"] = expected + [{
            **expected[0],
            "link_id": "audit-extra",
            "target_id": "extra",
        }]
        mutations["audit-link-duplicate"] = expected + [dict(expected[0])]
        dangling = copy.deepcopy(expected)
        dangling[0]["target_ref"] = "build/ci-evidence/phase34/missing.json"
        mutations["audit-link-dangling"] = dangling
        lifecycle = copy.deepcopy(expected)
        lifecycle[0]["source_phase_lifecycle_id"] = "stale"
        mutations["audit-link-lifecycle-mismatched"] = lifecycle
        category = copy.deepcopy(expected)
        category[0]["kind"] = "blocker"
        mutations["audit-link-category-mismatched"] = category
        digest = copy.deepcopy(expected)
        digest[0]["digest"] = "0" * 64
        mutations["audit-link-digest-mismatched"] = digest

        for expected_reason, emitted in mutations.items():
            with self.subTest(expected_reason=expected_reason):
                # Arrange / Act
                reasons = phase35.validate_audit_links(expected, emitted)

                # Assert
                self.assertIn(expected_reason, reasons)

    def test_t_35_01_link_digest_uses_canonical_sanitized_projection(
            self) -> None:
        # Arrange
        source = self.audit_sources()[0]
        canonical = json.dumps(source["digest_source"],
                               sort_keys=True,
                               separators=(",", ":")).encode()

        # Act
        link = phase35.derive_audit_links([source])[0]

        # Assert
        self.assertEqual(link["digest"], hashlib.sha256(canonical).hexdigest())

    def test_t_35_01_local_audit_links_resolve_targets_and_fragments(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        target_ref = "build/ci-evidence/phase34/rows.json#row-1"
        target = {"row_id": "row-1", "value": "sanitized"}
        target_path = root / target_ref.split("#", 1)[0]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps({"rows": [target]}),
                               encoding="utf-8")
        link = {
            "target_ref": target_ref,
            "digest":
            hashlib.sha256(phase35.canonical_json(target)).hexdigest(),
        }

        # Act
        reasons = phase35.validate_resolved_audit_links(root, [link])

        # Assert
        self.assertEqual(reasons, [])

    def test_t_35_01_dangling_local_audit_link_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        link = {
            "target_ref": "build/ci-evidence/phase34/does-not-exist.json",
            "digest": "0" * 64,
        }

        # Act
        reasons = phase35.validate_resolved_audit_links(root, [link])

        # Assert
        self.assertEqual(reasons, ["audit-link-dangling"])

    def test_t_35_01_symlinked_local_audit_target_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside_target = Path(outside_dir.name) / "rows.json"
        target = {"row_id": "row-1", "value": "outside"}
        outside_target.write_text(json.dumps({"rows": [target]}),
                                  encoding="utf-8")
        target_ref = "build/ci-evidence/phase34/rows.json#row-1"
        target_path = root / target_ref.split("#", 1)[0]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.symlink_to(outside_target)
        link = {
            "target_ref": target_ref,
            "digest":
            hashlib.sha256(phase35.canonical_json(target)).hexdigest(),
        }

        # Act
        reasons = phase35.validate_resolved_audit_links(root, [link])

        # Assert
        self.assertEqual(reasons, ["audit-link-dangling"])

    def test_cutover_03_repair_scope_uses_exact_ordinary_exit_review_refs(
            self) -> None:
        # Arrange
        blocker = self.blocker_row()
        ledger = self.ledger_row()

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [ledger], [],
                                                    [])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(len(scope), 1)
        self.assertEqual(
            scope[0]["required_action_ref"],
            f"{PHASE32_REGISTER}#blocker-1/required_next_action",
        )
        self.assertEqual(
            scope[0]["exit_review_criterion_refs"],
            [
                f"{PHASE32_REGISTER}#blocker-1/affected_gate",
                f"{PHASE32_REGISTER}#blocker-1/required_next_action",
                f"{PHASE34_LEDGER}#ledger-1/reason_codes",
                f"{PHASE34_LEDGER}#ledger-1/readiness_effect",
            ],
        )

    def test_cutover_03_repair_scope_adds_exact_exception_criteria(
            self) -> None:
        # Arrange
        blocker = self.blocker_row(blocker_kind="exception_request")
        exception = {
            "decision_id": "exception-1",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "expiry_or_review_trigger": "review-before-cutover",
            "affected_gates": ["final-simulator-evidence"],
        }
        ledger = {
            **self.ledger_row(), "exception_decision_refs":
            [f"{PHASE33_NORMALIZED_REGISTER}#exception-1"]
        }

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [ledger],
                                                    [exception], [])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(
            scope[0]["exit_review_criterion_refs"][-2:],
            [
                f"{PHASE33_EXCEPTION_REGISTER}#exception-1/expiry_or_review_trigger",
                f"{PHASE33_EXCEPTION_REGISTER}#exception-1/affected_gates",
            ],
        )

    def test_cutover_03_write_bundle_preserves_exception_covered_approval(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        blocker = self.blocker_row(blocker_kind="exception_request")
        exception = self.exception()
        unrelated_ref = f"{PHASE32_REGISTER}#unrelated"
        source = {
            "receipts": [{
                "receipt_ref": "external://phase31/sanitized-packet",
                "receipt": {
                    "submission_id": "submission-1"
                },
            }],
            "blockers": [blocker],
            "exceptions": [exception],
            "residuals": [{
                "decision_id":
                "risk-unrelated",
                "source_row_refs": [unrelated_ref],
                "linked_blocker_refs": [unrelated_ref],
                "follow_up_refs": ["external://phase33/risk-follow-up"],
                "affected_gates": ["other-gate"],
            }],
            "retained": [{
                "decision_id": "retained-unrelated",
                "source_row_refs": [unrelated_ref],
            }],
            "readiness_handoff": {
                "decision_id": "readiness-1"
            },
            "demotion_handoff":
            self.demotion_handoff(supplied=False),
            "packet": {
                "readiness_state": "unblocked",
                "reason_codes": [],
            },
            "dry_run":
            self.demotion_dry_run(
                readiness_state="unblocked",
                approval_validation_state="missing",
                approval_decision_state="missing",
                reason_codes=["approval-missing"],
            ),
            "ledger": {
                "rows": [{
                    **self.ledger_row(),
                    "coverage_state":
                    "exception-covered",
                    "readiness_effect":
                    "unblocked",
                    "reason_codes": [],
                    "exception_decision_refs":
                    [f"{PHASE33_NORMALIZED_REGISTER}#exception-1"],
                }]
            },
            "normalized": [],
        }
        self.write_audit_targets(root, source)
        contract = self.contract()
        phase34_contract = json.loads((
            root /
            "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json"
        ).read_text(encoding="utf-8"))

        # Act
        phase35.write_bundle(
            root,
            Path("build/ci-evidence/phase35"),
            contract,
            phase34_contract,
            {},
            source,
        )

        # Assert
        decision = json.loads(
            (root /
             "build/ci-evidence/phase35/cutover-decision.json").read_text(
                 encoding="utf-8"))
        route = json.loads(
            (root /
             "build/ci-evidence/phase35/next-milestone-route.json").read_text(
                 encoding="utf-8"))
        self.assertEqual(decision["cutover_verdict"],
                         "approved-with-exceptions")
        self.assertNotIn("route-scope-incomplete", decision["reason_codes"])
        self.assertEqual(len(route["follow_up_scope"]), 1)
        self.assertEqual(
            route["follow_up_scope"][0]["exception_refs"],
            [f"{PHASE33_EXCEPTION_REGISTER}#exception-1"],
        )

    def test_cutover_03_repair_scope_adds_exact_residual_risk_criteria(
            self) -> None:
        # Arrange
        blocker = self.blocker_row()
        residual = {
            "decision_id": "risk-1",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "follow_up_refs": ["external://phase33/risk-follow-up"],
            "affected_gates": ["final-simulator-evidence"],
        }
        ledger = {
            **self.ledger_row(), "residual_risk_decision_refs":
            [f"{PHASE33_NORMALIZED_REGISTER}#risk-1"]
        }

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [ledger], [],
                                                    [residual])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(
            scope[0]["exit_review_criterion_refs"][-2:],
            [
                f"{PHASE33_RESIDUAL_REGISTER}#risk-1/follow_up_refs",
                f"{PHASE33_RESIDUAL_REGISTER}#risk-1/affected_gates",
            ],
        )

    def test_cutover_03_repair_scope_covers_phase34_created_blocker(
            self) -> None:
        # Arrange
        ledger = {
            "row_id": "phase34-required-stream",
            "classification_ref": "",
            "source_stream": "simulator",
            "source_ref":
            "build/ci-evidence/phase23/upstream-simulator-result-row.json",
            "requirement_ids": ["INTAKE-01"],
            "affected_gates": ["final-simulator-evidence"],
            "reason_codes": ["required-row-missing"],
            "readiness_effect": "blocked",
        }

        # Act
        scope, reasons = phase35.build_repair_scope([], [ledger], [], [])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(len(scope), 1)
        self.assertEqual(
            scope[0]["blocker_refs"],
            [f"{PHASE34_LEDGER}#phase34-required-stream"],
        )
        self.assertEqual(
            scope[0]["required_action_ref"],
            f"{PHASE34_LEDGER}#phase34-required-stream/source_ref",
        )

    def test_cutover_03_unresolved_or_fabricated_scope_stays_blocked(
            self) -> None:
        cases = [
            ("missing-ledger", [], [], []),
            (
                "wrong-classification",
                [{
                    **self.ledger_row(), "classification_ref":
                    f"{PHASE32_REGISTER}#other"
                }],
                [],
                [],
            ),
            (
                "fabricated-exception",
                [{
                    **self.ledger_row(), "exception_decision_refs":
                    [f"{PHASE33_NORMALIZED_REGISTER}#exception-1"]
                }],
                [{
                    "decision_id": "exception-1",
                    "source_row_refs": [f"{PHASE32_REGISTER}#other"],
                    "linked_blocker_refs": [f"{PHASE32_REGISTER}#other"],
                    "expiry_or_review_trigger": "review",
                    "affected_gates": ["final-simulator-evidence"],
                }],
                [],
            ),
        ]
        for case_name, ledger, exceptions, residuals in cases:
            with self.subTest(case=case_name):
                # Arrange / Act
                scope, reasons = phase35.build_repair_scope(
                    [self.blocker_row()],
                    ledger,
                    exceptions,
                    residuals,
                )
                route = phase35.build_route("blocked", scope)

                # Assert
                self.assertIn("route-scope-incomplete", reasons)
                self.assertEqual(route["source_verdict"], "blocked")
                self.assertEqual(route["route"], "targeted-blocker-repair")

    def test_t_35_06_demotion_missing_is_not_collapsed(self) -> None:
        # Arrange
        handoff = self.demotion_handoff(supplied=False)
        dry_run = self.demotion_dry_run(
            approval_validation_state="missing",
            approval_decision_state="missing",
            reason_codes=["approval-missing"],
        )

        # Act
        projection = phase35.project_demotion(handoff, [], dry_run)

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"],
                         "missing")
        self.assertEqual(projection["demotion_decision_state"], "missing")
        self.assertEqual(projection["demotion_decision_source_refs"], [])
        self.assertEqual(projection["demotion_gate_state"], "blocked")
        self.assertEqual(projection["demotion_gate_reason_codes"],
                         ["approval-missing"])

    def test_t_35_06_demotion_malformed_stale_lifecycle_and_other_invalid_remain_distinct(
            self) -> None:
        cases = [
            ("malformed", {
                "phase": 3
            }, [], "malformed"),
            (
                "stale",
                self.demotion_handoff(),
                [
                    self.demotion_decision(
                        decision_timestamp="2020-01-01T00:00:00Z")
                ],
                "stale",
            ),
            (
                "lifecycle-mismatched",
                self.demotion_handoff(lifecycle="stale"),
                [self.demotion_decision(lifecycle="stale")],
                "lifecycle-mismatched",
            ),
            (
                "invalid",
                self.demotion_handoff(),
                [self.demotion_decision(decision_value="unknown")],
                "invalid",
            ),
        ]
        for case_name, handoff, records, expected_state in cases:
            with self.subTest(case=case_name):
                # Arrange
                dry_run = self.demotion_dry_run()

                # Act
                projection = phase35.project_demotion(handoff, records,
                                                      dry_run)

                # Assert
                self.assertEqual(
                    projection["demotion_decision_validation_state"],
                    expected_state)
                self.assertEqual(projection["demotion_gate_state"], "blocked")

    def test_t_35_06_valid_reject_is_valid_and_preserves_safe_source_refs(
            self) -> None:
        # Arrange
        handoff = self.demotion_handoff()
        records = [self.demotion_decision(decision_value="reject")]
        dry_run = self.demotion_dry_run(
            approval_decision_state="reject",
            reason_codes=["approval-rejected"],
        )

        # Act
        projection = phase35.project_demotion(handoff, records, dry_run)

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"],
                         "valid")
        self.assertEqual(projection["demotion_decision_state"], "reject")
        self.assertEqual(
            projection["demotion_decision_source_refs"],
            [f"{PHASE32_REGISTER}#blocker-1"],
        )
        self.assertEqual(projection["demotion_gate_reason_codes"],
                         ["approval-rejected"])

    def test_t_35_06_valid_approve_does_not_upgrade_cutover_or_gate(
            self) -> None:
        # Arrange
        handoff = self.demotion_handoff()
        records = [self.demotion_decision()]
        dry_run = self.demotion_dry_run(gate_state="blocked",
                                        reason_codes=["readiness-blocked"])

        # Act
        projection = phase35.project_demotion(handoff, records, dry_run)
        verdict = phase35.evaluate_verdict({
            "readiness_state":
            "blocked",
            "reason_codes": ["readiness-blocked"],
            "active_exception_ids": [],
            "exceptions": [],
        })

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"],
                         "valid")
        self.assertEqual(projection["demotion_decision_state"], "approve")
        self.assertEqual(projection["demotion_gate_state"], "blocked")
        self.assertEqual(verdict["cutover_verdict"], "blocked")

    def test_t_35_06_open_gate_does_not_upgrade_cutover_verdict(self) -> None:
        # Arrange
        dry_run = self.demotion_dry_run(gate_state="open", reason_codes=[])

        # Act
        projection = phase35.project_demotion(
            self.demotion_handoff(),
            [self.demotion_decision()],
            dry_run,
        )
        verdict = phase35.evaluate_verdict({
            "readiness_state":
            "blocked",
            "reason_codes": ["readiness-blocked"],
            "active_exception_ids": [],
            "exceptions": [],
        })

        # Assert
        self.assertEqual(projection["demotion_gate_state"], "open")
        self.assertEqual(verdict["cutover_verdict"], "blocked")

    def test_t_35_06_stale_approval_cannot_preserve_open_gate(self) -> None:
        # Arrange
        handoff = self.demotion_handoff()
        records = [
            self.demotion_decision(decision_timestamp="2020-01-01T00:00:00Z")
        ]
        dry_run = self.demotion_dry_run(
            gate_state="open",
            approval_validation_state="invalid",
            reason_codes=[],
        )

        # Act
        projection = phase35.project_demotion(handoff, records, dry_run)

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"],
                         "stale")
        self.assertEqual(projection["demotion_gate_state"], "blocked")
        self.assertIn("approval-invalid",
                      projection["demotion_gate_reason_codes"])

    def test_t_35_02_paths_reject_absolute_traversal_wrong_root_overlap_and_symlink_escape(
            self) -> None:
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside = root / "outside"
        outside.mkdir()
        symlink_output = root / "build/ci-evidence/phase35"
        symlink_output.parent.mkdir(parents=True)
        symlink_output.symlink_to(outside, target_is_directory=True)
        cases = [
            ("/tmp/phase34", "build/ci-evidence/phase35"),
            ("../phase34", "build/ci-evidence/phase35"),
            ("build/ci-evidence/phase30", "build/ci-evidence/phase35"),
            ("build/ci-evidence/phase34", "build/ci-evidence/phase34"),
            ("build/ci-evidence/phase34", "build/ci-evidence/phase35"),
        ]
        for phase34_dir, output_dir in cases:
            with self.subTest(phase34_dir=phase34_dir, output_dir=output_dir):
                # Arrange / Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.validate_paths(root, phase34_dir, output_dir)

    def test_t_35_02_source_artifact_file_symlink_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside_artifact = Path(outside_dir.name) / "manifest.json"
        outside_artifact.write_text(json.dumps({"sentinel": "outside"}),
                                    encoding="utf-8")
        relative_path = Path(
            "build/ci-evidence/phase34/final-readiness-run-manifest.json")
        source_path = root / relative_path
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.symlink_to(outside_artifact)

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "contains a symlink escape"):
            phase35.load_json(root, relative_path)

    def test_t_35_02_source_artifact_parent_symlink_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside_artifact = Path(outside_dir.name) / "snapshot.json"
        outside_artifact.write_text(json.dumps({"sentinel": "outside"}),
                                    encoding="utf-8")
        relative_path = Path(
            "build/ci-evidence/phase34/contract-snapshots/snapshot.json")
        symlinked_parent = root / relative_path.parent
        symlinked_parent.parent.mkdir(parents=True, exist_ok=True)
        symlinked_parent.symlink_to(Path(outside_dir.name),
                                    target_is_directory=True)

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "contains a symlink escape"):
            phase35.load_json(root, relative_path)

    def test_t_35_03_security_rejects_forbidden_fields_text_raw_payloads_and_unsafe_refs(
            self) -> None:
        cases = [
            {
                "token_value": "redacted"
            },
            {
                "nested": {
                    "private_key": "redacted"
                }
            },
            {
                "rationale": "production demotion complete"
            },
            {
                "raw_payload": {
                    "data": "not-allowed"
                }
            },
            {
                "source_refs": ["../unsafe.json"]
            },
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                # Arrange / Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.scan_security(payload)

    def test_t_35_03_external_refs_reject_traversal_and_malformed_uris(
            self) -> None:
        cases = [
            "external://phase31/../../private",
            "external://phase31/%2e%2e/private",
            "external://phase31/safe\\private",
            "external://phase31/safe%5c..%5cprivate",
            "external://phase31/safe%0aprivate",
            "external://phase31/safe#row%5c..%5cprivate",
            "external://phase31/safe%2",
            "external://phase99/safe",
            "external://phase31/safe?query=unsafe",
            "external://phase31/safe#",
            "external://phase31/safe#row/../private",
            "maintainer://owner/../private",
            "owner://phase34/safe\u0001",
        ]
        for ref in cases:
            with self.subTest(ref=ref):
                # Arrange / Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.validate_ref(ref)

    def test_t_35_03_external_refs_accept_contract_rooted_safe_uris(
            self) -> None:
        # Arrange
        refs = [
            "external://phase31/sanitized-packet",
            "maintainer://cutover-owner",
            "owner://phase34/simulator",
        ]

        # Act / Assert
        for ref in refs:
            phase35.validate_ref(ref)

    def test_t_35_04_lifecycle_and_contract_drift_fail_closed(self) -> None:
        # Arrange
        contract = self.contract()
        manifest = {
            "artifact_name": "phase34-final-readiness-demotion-dry-run",
            "phase_lifecycle_id": "stale",
            "output_root": "build/ci-evidence/phase34",
            "raw_evidence_consumed": False,
            "generated_artifacts": [],
        }

        # Act / Assert
        with self.assertRaises(phase35.VerificationError):
            phase35.validate_phase34_manifest(contract, manifest)

    def test_t_35_03_snapshots_reject_secret_fields_and_uncontracted_fields(
            self) -> None:
        # Arrange
        contract = self.contract()
        secret_manifest = {
            "accepted_receipt_snapshot_ref":
            "build/ci-evidence/phase34/contract-snapshots/phase31-accepted-receipts.json",
            "artifact_name": "phase34-final-readiness-demotion-dry-run",
            "generated_artifacts": phase35.PHASE34_ARTIFACTS,
            "generated_at_utc": "2026-07-25T22:18:11Z",
            "output_root": "build/ci-evidence/phase34",
            "phase": "34-final-readiness-and-demotion-dry-run",
            "phase_lifecycle_id": phase35.PHASE34_LIFECYCLE_ID,
            "raw_evidence_consumed": False,
            "snapshot_refs": [],
            "source_refs": [],
            "token_value": "secret-bearing-value",
        }
        uncontracted_contract = {
            **contract, "unexpected": {
                "rationale": "not contracted"
            }
        }

        # Act / Assert
        with self.assertRaises(phase35.VerificationError):
            phase35.validate_phase34_manifest(contract, secret_manifest)
        with self.assertRaises(phase35.VerificationError):
            phase35.validate_snapshot(
                "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
                uncontracted_contract,
            )

    def test_t_35_03_snapshot_scan_permits_declared_contract_vocabulary(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        phase35.validate_snapshot(
            "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
            contract,
        )

        # Assert
        self.assertIn("production demotion complete",
                      contract["security"]["prohibited_text_markers"])

    def test_t_35_04_phase33_register_digest_rejects_post_phase34_mutation(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        register_ref = "build/ci-evidence/phase33/exception-decision-register.json"
        register_path = root / register_ref
        register_path.parent.mkdir(parents=True, exist_ok=True)
        original = {"rows": []}
        register_path.write_text(json.dumps(original), encoding="utf-8")
        digest = hashlib.sha256(phase35.canonical_json(original)).hexdigest()
        refs = {"exception_decision_register": register_ref}
        digests = {"exception_decision_register": digest}
        register_path.write_text(json.dumps(
            {"rows": [{
                "decision_id": "late"
            }]}),
                                 encoding="utf-8")

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "changed after Phase 34 validation"):
            phase35.reached_register(root, refs, digests,
                                     "exception_decision_register")

    def test_t_35_04_exception_projection_must_equal_normalized_decision(
            self) -> None:
        # Arrange
        normalized = [{
            "decision_id": "exception-1",
            "decision_type": "exception",
            "decision_value": "approve",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
        }]
        projection = [{
            **normalized[0],
            "decision_value": "reject",
            "scope": "exact",
            "expiry_or_review_trigger": "review-before-cutover",
            "affected_requirements": ["CUTOVER-01"],
            "affected_gates": ["final-simulator-evidence"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
        }]

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "projection differs"):
            phase35.validate_register_projection(projection, normalized,
                                                 "exception")

    def test_t_35_04_exception_projection_rejects_legacy_validation_fields(
            self) -> None:
        # Arrange
        normalized = [{
            "decision_id": "exception-1",
            "decision_type": "exception",
            "decision_value": "approve",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
        }]
        projection = [{
            **normalized[0],
            "scope": "exact",
            "expiry_or_review_trigger": "review-before-cutover",
            "affected_requirements": ["CUTOVER-01"],
            "affected_gates": ["final-simulator-evidence"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "validation_state": "valid",
            "active": True,
            "exact_scope": True,
        }]

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "forbidden legacy"):
            phase35.validate_register_projection(projection, normalized,
                                                 "exception")

    def test_t_35_05_caller_supplied_authority_flags_are_rejected(
            self) -> None:
        forbidden_options = [
            "--verdict",
            "--route",
            "--cutover-confirmation",
            "--demotion-approval",
            "--evidence-payload",
        ]

        # Arrange / Act
        parser = phase35.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }

        # Assert
        self.assertTrue(set(forbidden_options).isdisjoint(option_strings))

    def test_t_35_05_route_overclaims_are_impossible(self) -> None:
        for verdict in VERDICTS:
            with self.subTest(verdict=verdict):
                # Arrange / Act
                route = phase35.build_route(verdict, [])

                # Assert
                self.assertTrue(route["planning_only"])
                self.assertFalse(route["production_actions_authorized"])

    def test_t_35_03_markdown_and_json_use_one_shared_projection(self) -> None:
        # Arrange
        links = phase35.derive_audit_links(self.audit_sources())
        decision = {
            "cutover_verdict": "blocked",
            "reason_codes": ["readiness-blocked"],
            "readiness_state": "blocked",
            "active_exception_ids": [],
            "blocker_ids": ["blocker-1"],
            "audit_link_counts_by_kind": {
                kind: 1
                for kind in AUDIT_KINDS
            },
            "demotion_decision_validation_state": "missing",
            "demotion_decision_state": "missing",
            "demotion_decision_source_refs": [],
            "demotion_gate_state": "blocked",
            "demotion_gate_reason_codes": ["approval-missing"],
        }
        route = phase35.build_route("blocked", [])

        # Act
        report = phase35.render_report(decision, route, links)

        # Assert
        self.assertIn("cutover_verdict: blocked", report)
        self.assertIn("route: targeted-blocker-repair", report)
        self.assertIn("demotion_decision_validation_state: missing", report)
        self.assertIn("demotion_gate_state: blocked", report)
        for kind in AUDIT_KINDS:
            self.assertIn(f"{kind}: 1", report)

    def test_default_projection_is_blocked_repair_without_synthesized_authority(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        default = contract["default_behavior"]

        # Assert
        self.assertEqual(default["cutover_verdict"], "blocked")
        self.assertEqual(default["route"], "targeted-blocker-repair")
        self.assertEqual(default["demotion_decision_validation_state"],
                         "missing")
        self.assertEqual(default["demotion_decision_state"], "missing")
        self.assertEqual(default["demotion_decision_source_refs"], [])
        self.assertEqual(default["demotion_gate_state"], "blocked")
        self.assertFalse(default["synthesizes_evidence"])
        self.assertFalse(default["synthesizes_approval"])
        self.assertFalse(default["synthesizes_exception"])
        self.assertFalse(default["synthesizes_demotion_authorization"])

    def test_wiring_contract_requires_exact_bazel_workflow_and_just_strings(
            self) -> None:
        # Arrange
        expected = phase35.required_wiring_strings()

        # Act / Assert
        self.assertIn("phase35_source_ref_manifests", expected["tools_bazel"])
        self.assertIn("phase35_verify", expected["tools_bazel"])
        self.assertIn("phase35_verify_tests", expected["tools_bazel"])
        self.assertIn("phase35_cutover_decision_artifact_docs",
                      expected["root_bazel"])
        self.assertIn("phase35_verify_tests)", expected["workflow"])
        self.assertIn("phase35_verify)", expected["workflow"])
        self.assertEqual(
            expected["just"],
            [
                "phase35-verify:",
                "bazel run //tools/bazel:phase35_verify_tests",
                "bazel run //tools/bazel:phase35_verify",
            ],
        )


class Phase35GuardedPublicationTest(unittest.TestCase):

    def make_install_fixture(
        self
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        canonical = root / phase35.DEFAULT_OUTPUT
        canonical.mkdir(parents=True)
        phase35.write_json(canonical / "decision.json",
                           {"cutover_verdict": "approved"})
        stage = Path(
            tempfile.mkdtemp(prefix=".phase35-stage-",
                             dir=canonical.parent))
        phase35.write_json(stage / "decision.json",
                           {"cutover_verdict": "blocked"})
        return temp_dir, root, canonical, stage

    def assert_guard_blocks(self, root: Path) -> None:
        guard = root / phase35.AUTHORITY_GUARD
        self.assertTrue(guard.exists() or guard.is_symlink())
        with self.assertRaises(phase35.VerificationError):
            phase35.ensure_canonical_authority(root, phase35.DEFAULT_OUTPUT)

    def test_authority_guard_contract_is_exact_and_cannot_grant_approval(
            self) -> None:
        # Arrange
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

        # Act
        guard = contract["authority_guard"]

        # Assert
        self.assertEqual(
            guard, {
                "artifact":
                "build/ci-evidence/.phase35-authority-guard.json",
                "required_fields": [
                    "phase",
                    "phase_lifecycle_id",
                    "authority_state",
                    "reason_code",
                    "attempted_output_root",
                ],
                "phase_lifecycle_id":
                phase35.PHASE_LIFECYCLE_ID,
                "authority_state":
                "blocked",
                "safe_reason_code":
                "publication-in-progress",
                "attempted_output_root":
                phase35.DEFAULT_OUTPUT.as_posix(),
            })
        self.assertTrue({
            "approved",
            "approval",
            "verdict",
            "route",
            "production_actions_authorized",
        }.isdisjoint(guard["required_fields"]))

    def test_guard_write_failure_blocks_prior_authority_before_rename(
            self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)

        def fail_after_guard_creation(path: Path,
                                      payload: dict[str, object]) -> None:
            del path, payload
            raise OSError("injected guard write failure")

        # Act / Assert
        with mock.patch.object(phase35,
                               "write_guard_payload",
                               side_effect=fail_after_guard_creation):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(
                    root,
                    stage,
                    canonical,
                    lambda _: None,
                )
        self.assertTrue(canonical.exists())
        self.assertTrue(stage.exists())
        self.assert_guard_blocks(root)

    def test_prior_to_backup_rename_failure_retains_guard_and_prior(
            self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        original_rename = phase35.rename_path

        def fail_prior_rename(source: Path, target: Path) -> None:
            if source == canonical:
                raise OSError("injected prior rename failure")
            original_rename(source, target)

        # Act / Assert
        with mock.patch.object(phase35,
                               "rename_path",
                               side_effect=fail_prior_rename):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        self.assertTrue(canonical.exists())
        self.assert_guard_blocks(root)

    def test_stage_rename_failure_restores_prior_under_guard(self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        original_rename = phase35.rename_path

        def fail_stage_rename(source: Path, target: Path) -> None:
            if source == stage:
                raise OSError("injected stage rename failure")
            original_rename(source, target)

        # Act / Assert
        with mock.patch.object(phase35,
                               "rename_path",
                               side_effect=fail_stage_rename):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        prior = json.loads(
            (canonical / "decision.json").read_text(encoding="utf-8"))
        self.assertEqual(prior["cutover_verdict"], "approved")
        self.assert_guard_blocks(root)

    def test_post_install_validation_failure_restores_prior_under_guard(
            self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)

        def fail_validation(_: Path) -> None:
            raise phase35.VerificationError(
                "injected post-install validation failure")

        # Act / Assert
        with self.assertRaises(phase35.VerificationError):
            phase35.install_staged_bundle(root, stage, canonical,
                                          fail_validation)
        prior = json.loads(
            (canonical / "decision.json").read_text(encoding="utf-8"))
        self.assertEqual(prior["cutover_verdict"], "approved")
        self.assert_guard_blocks(root)

    def test_restore_failure_retains_recoverable_backup_and_guard(self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        original_rename = phase35.rename_path

        def fail_stage_and_restore(source: Path, target: Path) -> None:
            if source == stage or source.name == ".phase35-previous":
                raise OSError("injected rename failure")
            original_rename(source, target)

        # Act / Assert
        with mock.patch.object(phase35,
                               "rename_path",
                               side_effect=fail_stage_and_restore):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        self.assertTrue(
            (root / phase35.PREVIOUS_OUTPUT).is_dir())
        self.assert_guard_blocks(root)

    def test_backup_cleanup_failure_leaves_valid_canonical_blocked(
            self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        original_remove = phase35.remove_directory

        def fail_backup_cleanup(path: Path) -> None:
            if path.name == ".phase35-previous":
                raise OSError("injected backup cleanup failure")
            original_remove(path)

        # Act / Assert
        with mock.patch.object(phase35,
                               "remove_directory",
                               side_effect=fail_backup_cleanup):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        current = json.loads(
            (canonical / "decision.json").read_text(encoding="utf-8"))
        self.assertEqual(current["cutover_verdict"], "blocked")
        self.assertTrue((root / phase35.PREVIOUS_OUTPUT).exists())
        self.assert_guard_blocks(root)

    def test_guard_cleanup_failure_leaves_valid_canonical_blocked(self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)

        # Act / Assert
        with mock.patch.object(phase35,
                               "remove_guard",
                               side_effect=OSError(
                                   "injected guard cleanup failure")):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        current = json.loads(
            (canonical / "decision.json").read_text(encoding="utf-8"))
        self.assertEqual(current["cutover_verdict"], "blocked")
        self.assertFalse((root / phase35.PREVIOUS_OUTPUT).exists())
        self.assert_guard_blocks(root)

    def test_guard_presence_or_invalidity_blocks_every_touched_reader(
            self) -> None:
        cases = {
            "valid": {
                "phase": phase35.PHASE,
                "phase_lifecycle_id": phase35.PHASE_LIFECYCLE_ID,
                "authority_state": "blocked",
                "reason_code": "publication-in-progress",
                "attempted_output_root": phase35.DEFAULT_OUTPUT.as_posix(),
            },
            "malformed": {
                "authority_state": "blocked"
            },
            "stale": {
                "phase": phase35.PHASE,
                "phase_lifecycle_id": "stale",
                "authority_state": "blocked",
                "reason_code": "publication-in-progress",
                "attempted_output_root": phase35.DEFAULT_OUTPUT.as_posix(),
            },
        }
        for name, payload in cases.items():
            with self.subTest(name=name):
                # Arrange
                temp_dir = tempfile.TemporaryDirectory()
                self.addCleanup(temp_dir.cleanup)
                root = Path(temp_dir.name)
                guard = root / phase35.AUTHORITY_GUARD
                phase35.write_json(guard, payload)

                # Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.ensure_canonical_authority(
                        root, phase35.DEFAULT_OUTPUT)
                with self.assertRaises(phase35.VerificationError):
                    phase35.run_security_scan(root)

    def assert_target_substitutions_rejected(self, target_name: str,
                                             expected: Path,
                                             expect_directory: bool) -> None:
        substitutions = [
            ("absolute", Path("/tmp/phase35-substitution")),
            ("parent-traversal", Path("build/ci-evidence/../escape")),
            ("wrong-root", Path("build/other/phase35-substitution")),
        ]
        for name, actual in substitutions:
            with self.subTest(target=target_name, substitution=name):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    with self.assertRaises(phase35.VerificationError):
                        phase35.validate_mutation_target(
                            root,
                            actual,
                            expected,
                            target_name,
                            expect_directory=expect_directory,
                            allow_missing=True,
                        )

        with self.subTest(target=target_name, substitution="symlink-escape"):
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                outside = root / "outside"
                outside.mkdir()
                (root / "build").mkdir()
                (root / "build/ci-evidence").symlink_to(
                    outside, target_is_directory=True)
                with self.assertRaises(phase35.VerificationError):
                    phase35.validate_mutation_target(
                        root,
                        expected,
                        expected,
                        target_name,
                        expect_directory=expect_directory,
                        allow_missing=True,
                    )

        with self.subTest(target=target_name,
                          substitution="non-directory"):
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                target = root / expected
                if expect_directory:
                    target.parent.mkdir(parents=True)
                    target.write_text("not a directory", encoding="utf-8")
                else:
                    target.parent.parent.mkdir(parents=True)
                    target.parent.write_text("not a directory",
                                             encoding="utf-8")
                with self.assertRaises(phase35.VerificationError):
                    phase35.validate_mutation_target(
                        root,
                        expected,
                        expected,
                        target_name,
                        expect_directory=expect_directory,
                        allow_missing=False,
                    )

    def test_guard_target_substitutions_are_rejected(self) -> None:
        self.assert_target_substitutions_rejected(
            "guard",
            phase35.AUTHORITY_GUARD,
            expect_directory=False,
        )

    def test_stage_target_substitutions_are_rejected(self) -> None:
        self.assert_target_substitutions_rejected(
            "stage",
            Path("build/ci-evidence/.phase35-stage-test"),
            expect_directory=True,
        )

    def test_backup_target_substitutions_are_rejected(self) -> None:
        self.assert_target_substitutions_rejected(
            "backup",
            phase35.PREVIOUS_OUTPUT,
            expect_directory=True,
        )

    def test_canonical_target_substitutions_are_rejected(self) -> None:
        self.assert_target_substitutions_rejected(
            "canonical",
            phase35.DEFAULT_OUTPUT,
            expect_directory=True,
        )


class Phase35SourceFailureReplacementTest(unittest.TestCase):

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

    def phase34_manifest(self) -> dict[str, object]:
        return {
            "accepted_receipt_snapshot_ref":
            "build/ci-evidence/phase34/contract-snapshots/phase31-accepted-receipts.json",
            "artifact_name": "phase34-final-readiness-demotion-dry-run",
            "generated_artifacts": phase35.PHASE34_ARTIFACTS,
            "generated_at_utc": "2026-07-25T22:18:11Z",
            "output_root": "build/ci-evidence/phase34",
            "phase": "34-final-readiness-and-demotion-dry-run",
            "phase_lifecycle_id": phase35.PHASE34_LIFECYCLE_ID,
            "phase33_register_digests": {
                name: "0" * 64
                for name in phase35.PHASE33_REGISTER_NAMES
            },
            "raw_evidence_consumed": False,
            "snapshot_refs": [],
            "source_refs": [],
        }

    def seed_prior_approved(self, root: Path) -> None:
        output = root / "build/ci-evidence/phase35"
        snapshots = output / "contract-snapshots"
        snapshots.mkdir(parents=True, exist_ok=True)
        phase35.write_json(
            output / "cutover-decision-run-manifest.json",
            {"prior_approved": True},
        )
        phase35.write_json(
            output / "cutover-audit-link-index.json",
            {"prior_approved": True},
        )
        phase35.write_json(
            output / "cutover-decision.json",
            {
                "cutover_verdict": "approved",
                "prior_approved": True
            },
        )
        phase35.write_json(
            output / "next-milestone-route.json",
            {
                "route": "production-cutover-planning",
                "prior_approved": True
            },
        )
        (output / "redacted-cutover-decision-report.md").write_text(
            "prior_approved\n", encoding="utf-8")
        phase35.write_json(snapshots / "prior-approved.json",
                           {"prior_approved": True})

    def write_manifest(self, root: Path, manifest: dict[str, object]) -> Path:
        manifest_path = root / (
            "build/ci-evidence/phase34/final-readiness-run-manifest.json")
        phase35.write_json(manifest_path, manifest)
        return manifest_path

    def write_later_source_fixture(self, root: Path) -> None:
        dry_run = {
            "approval_decision_state": "missing",
            "approval_validation_state": "missing",
            "gate_state": "blocked",
            "readiness_state": "blocked",
            "reason_codes": ["approval-missing"],
            "source_refs": [],
        }
        artifacts = {
            "build/ci-evidence/phase34/readiness-coverage-ledger.json": {
                "phase_lifecycle_id": phase35.PHASE34_LIFECYCLE_ID,
                "rows": [],
            },
            "build/ci-evidence/phase34/final-readiness-packet.json": {
                "phase_lifecycle_id": phase35.PHASE34_LIFECYCLE_ID,
                "ledger_rows": [],
                "demotion_dry_run": dry_run,
            },
            "build/ci-evidence/phase34/readiness-blocker-summary.json": {},
            "build/ci-evidence/phase34/demotion-dry-run.json": dry_run,
            "build/ci-evidence/phase34/contract-snapshots/phase33-downstream-handoff-manifest.json":
            {
                "artifact_name": "phase33-maintainer-decision-inputs",
                "phase_lifecycle_id": phase35.PHASE33_LIFECYCLE_ID,
                "register_refs": {
                    name: "build/ci-evidence/phase34/wrong-source-root.json"
                    for name in phase35.PHASE33_REGISTER_NAMES
                },
            },
            "build/ci-evidence/phase34/contract-snapshots/phase32-blocker-register.json":
            {
                "rows": []
            },
            "build/ci-evidence/phase34/contract-snapshots/phase31-accepted-receipts.json":
            {
                "receipts": []
            },
        }
        for relative_path, payload in artifacts.items():
            phase35.write_json(root / relative_path, payload)

    def invoke_quick(self, root: Path) -> tuple[int, str]:
        stderr = io.StringIO()
        try:
            with mock.patch.object(phase35, "ROOT", root):
                with redirect_stderr(stderr):
                    result = phase35.main(["--quick"])
        except Exception as error:  # Intentional RED boundary assertion.
            self.fail(f"main --quick raised instead of returning 1: {error!r}")
        return result, stderr.getvalue()

    def assert_failure_replacement(self, root: Path, expected_reason: str,
                                   stderr: str) -> None:
        output = root / "build/ci-evidence/phase35"
        actual = sorted(
            path.relative_to(output).as_posix() for path in output.rglob("*")
            if path.is_file())
        self.assertEqual(actual, SOURCE_FAILURE_ARTIFACTS)
        manifest = json.loads(
            (output /
             "cutover-decision-run-manifest.json").read_text(encoding="utf-8"))
        decision = json.loads(
            (output / "cutover-decision.json").read_text(encoding="utf-8"))
        route = json.loads(
            (output / "next-milestone-route.json").read_text(encoding="utf-8"))
        contract = json.loads((
            root /
            "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json"
        ).read_text(encoding="utf-8"))
        behavior = contract["source_failure_behavior"]

        self.assertEqual(list(manifest), SOURCE_FAILURE_MANIFEST_FIELDS)
        self.assertEqual(list(decision), DECISION_FIELDS)
        self.assertEqual(list(route), ROUTE_FIELDS)
        self.assertEqual(manifest["generation_state"], "blocked-source-error")
        self.assertEqual(manifest["generated_artifacts"],
                         SOURCE_FAILURE_ARTIFACTS)
        self.assertEqual(manifest["source_failure_reason_codes"],
                         [expected_reason])
        self.assertIn(expected_reason, behavior["safe_reason_codes"])
        self.assertEqual(decision["cutover_verdict"], "blocked")
        self.assertEqual(
            decision["reason_codes"],
            sorted([expected_reason, "route-scope-incomplete"]),
        )
        self.assertEqual(decision["readiness_state"], "blocked")
        self.assertEqual(decision["readiness_result_ref"], "")
        self.assertEqual(decision["active_exception_ids"], [])
        self.assertEqual(decision["blocker_ids"], [])
        self.assertEqual(decision["audit_link_index_ref"], "")
        self.assertEqual(
            decision["audit_link_counts_by_kind"],
            {kind: 0
             for kind in AUDIT_KINDS},
        )
        self.assertEqual(decision["demotion_decision_validation_state"],
                         "invalid")
        self.assertEqual(decision["demotion_decision_state"], "missing")
        self.assertEqual(decision["demotion_decision_source_refs"], [])
        self.assertEqual(decision["demotion_gate_state"], "blocked")
        self.assertEqual(decision["demotion_gate_reason_codes"],
                         [expected_reason])
        self.assertEqual(route["route"], "targeted-blocker-repair")
        self.assertEqual(route["source_verdict"], "blocked")
        self.assertEqual(route["follow_up_scope"], [])
        self.assertTrue(route["requires_fresh_cutover_decision"])
        self.assertTrue(route["planning_only"])
        self.assertFalse(route["production_actions_authorized"])
        self.assertFalse(manifest["raw_evidence_consumed"])
        self.assertFalse(decision["raw_evidence_consumed"])
        published = "\n".join(
            path.read_text(encoding="utf-8") for path in output.rglob("*")
            if path.is_file())
        self.assertNotIn("prior_approved", published)
        self.assertNotIn("production-cutover-planning", published)
        self.assertNotIn("BEGIN PRIVATE KEY", published)
        self.assertNotIn("BEGIN PRIVATE KEY", stderr)

    def run_failure_case(
        self,
        mutate: Callable[[Path], None],
        expected_reason: str,
    ) -> None:
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.seed_prior_approved(root)
        mutate(root)

        # Act
        result, stderr = self.invoke_quick(root)

        # Assert
        self.assertEqual(result, 1)
        self.assert_failure_replacement(root, expected_reason, stderr)

    def test_prior_approved_is_replaced_when_phase34_manifest_is_missing(
            self) -> None:
        # Arrange / Act / Assert
        self.run_failure_case(lambda root: None, "source-artifact-missing")

    def test_prior_approved_is_replaced_when_phase34_manifest_json_is_malformed(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest_path = self.write_manifest(root, self.phase34_manifest())
            manifest_path.write_text("{", encoding="utf-8")

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-artifact-malformed")

    def test_prior_approved_is_replaced_when_phase34_manifest_utf8_is_unreadable(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest_path = self.write_manifest(root, self.phase34_manifest())
            manifest_path.write_bytes(b"\xff\xfe\x00")

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-artifact-malformed")

    def test_prior_approved_is_replaced_when_phase34_manifest_is_stale(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest = self.phase34_manifest()
            manifest["generated_at_utc"] = "2020-01-01T00:00:00Z"
            self.write_manifest(root, manifest)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-artifact-stale")

    def test_prior_approved_is_replaced_when_phase34_lifecycle_is_mismatched(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest = self.phase34_manifest()
            manifest["phase_lifecycle_id"] = "stale-lifecycle"
            self.write_manifest(root, manifest)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-artifact-lifecycle-mismatched")

    def test_prior_approved_is_replaced_when_phase34_manifest_is_secret_tainted(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest = self.phase34_manifest()
            manifest["phase"] = "-----BEGIN PRIVATE KEY-----"
            self.write_manifest(root, manifest)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "secret-tainted")

    def test_prior_approved_is_replaced_when_source_manifest_is_a_symlink(
            self) -> None:

        def mutate(root: Path) -> None:
            outside_dir = tempfile.TemporaryDirectory()
            self.addCleanup(outside_dir.cleanup)
            outside_manifest = Path(
                outside_dir.name) / "final-readiness-run-manifest.json"
            outside_manifest.write_text(json.dumps(self.phase34_manifest()),
                                        encoding="utf-8")
            manifest_path = root / (
                "build/ci-evidence/phase34/final-readiness-run-manifest.json")
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.symlink_to(outside_manifest)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-ref-failed")

    def test_prior_approved_is_replaced_when_later_reached_source_is_unsafe(
            self) -> None:

        def mutate(root: Path) -> None:
            self.write_manifest(root, self.phase34_manifest())
            self.write_later_source_fixture(root)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-ref-failed")

    def test_output_symlink_is_rejected_without_touching_target(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside = Path(outside_dir.name)
        marker = outside / "prior_approved"
        marker.write_text("unchanged", encoding="utf-8")
        output = root / "build/ci-evidence/phase35"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.symlink_to(outside, target_is_directory=True)

        # Act
        result, stderr = self.invoke_quick(root)

        # Assert
        self.assertEqual(result, 1)
        self.assertTrue(output.is_symlink())
        self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")
        self.assertEqual(sorted(path.name for path in outside.iterdir()),
                         ["prior_approved"])
        self.assertNotIn("unchanged", stderr)


if __name__ == "__main__":
    unittest.main()
