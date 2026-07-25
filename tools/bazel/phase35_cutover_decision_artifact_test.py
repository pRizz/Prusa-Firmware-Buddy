#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import phase35_cutover_decision_artifact as phase35


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json"
PHASE32_REGISTER = "build/ci-evidence/phase32/blocker-register.json"
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
        validation_state: str = "valid",
        active: bool = True,
        exact_scope: bool = True,
    ) -> dict[str, object]:
        return {
            "decision_id": decision_id,
            "decision_value": decision_value,
            "validation_state": validation_state,
            "active": active,
            "exact_scope": exact_scope,
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
            sources.append(
                {
                    "kind": kind,
                    "target_id": f"target-{index}",
                    "target_ref": f"build/ci-evidence/phase34/sanitized-{index}.json",
                    "source_phase_lifecycle_id": lifecycle_by_kind[kind],
                    "verdict_effect": "supports" if kind == "evidence-packet" else "blocks",
                    "digest_source": {"kind": kind, "target": index},
                }
            )
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
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": lifecycle,
            "demotion_input_supplied": supplied,
            "decision_id": "demotion-1" if supplied else "",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"] if supplied else [],
        }

    def demotion_dry_run(
        self,
        *,
        gate_state: str = "blocked",
        approval_validation_state: str = "valid",
        approval_decision_state: str = "approve",
        reason_codes: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "gate_state": gate_state,
            "reason_codes": reason_codes or ["readiness-blocked"],
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
            "reason_codes": ["evidence-failed"],
            "readiness_effect": "blocked",
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

    def test_cutover_01_contract_identity_lifecycle_and_closed_verdict_enum(self) -> None:
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
        self.assertEqual(contract["requirement_ids"], ["CUTOVER-01", "CUTOVER-02", "CUTOVER-03"])
        self.assertEqual(contract["verdict_enum"], VERDICTS)

    def test_cutover_02_contract_declares_exact_nine_kind_audit_schema(self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        schema = contract["audit_link_schema"]

        # Assert
        self.assertEqual(schema["kinds"], AUDIT_KINDS)
        self.assertEqual(schema["required_fields"], AUDIT_REQUIRED_FIELDS)
        self.assertEqual(schema["optional_fields"], ["digest"])
        self.assertTrue(schema["exact_set_required"])

    def test_cutover_03_contract_declares_routes_artifacts_and_no_authority(self) -> None:
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
        self.assertEqual(authority["reference_demotion_requirement"], "POST-01")

    def test_contract_declares_exact_blocked_reasons_and_output_fields(self) -> None:
        # Arrange
        contract = self.contract()

        # Act / Assert
        self.assertEqual(contract["blocked_reason_codes"], BLOCKED_REASONS)
        self.assertEqual(contract["cutover_decision_fields"], DECISION_FIELDS)
        self.assertEqual(
            contract["demotion_projection"]["decision_validation_states"],
            ["missing", "malformed", "stale", "lifecycle-mismatched", "invalid", "valid"],
        )
        self.assertEqual(
            contract["demotion_projection"]["decision_states"],
            ["missing", "approve", "reject"],
        )
        self.assertEqual(contract["demotion_projection"]["gate_states"], ["blocked", "open"])

    def test_cutover_01_truth_table_approves_only_unblocked_without_exceptions(self) -> None:
        # Arrange
        facts = self.valid_facts()

        # Act
        result = phase35.evaluate_verdict(facts)

        # Assert
        self.assertEqual(result["cutover_verdict"], "approved")
        self.assertEqual(result["reason_codes"], [])
        self.assertEqual(result["active_exception_ids"], [])

    def test_cutover_01_truth_table_approves_with_exact_active_exceptions(self) -> None:
        # Arrange
        facts = self.valid_facts()
        facts["active_exception_ids"] = ["exception-1"]
        facts["exceptions"] = [self.exception()]

        # Act
        result = phase35.evaluate_verdict(facts)

        # Assert
        self.assertEqual(result["cutover_verdict"], "approved-with-exceptions")
        self.assertEqual(result["active_exception_ids"], ["exception-1"])

    def test_cutover_01_truth_table_blocks_readiness_and_all_invalid_families(self) -> None:
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

    def test_cutover_01_truth_table_blocks_unknown_or_incomplete_fact_shapes(self) -> None:
        cases = [
            {},
            {"readiness_state": "unknown", "reason_codes": [], "active_exception_ids": [], "exceptions": []},
            {"readiness_state": "blocked", "reason_codes": [], "active_exception_ids": [], "exceptions": []},
            {"readiness_state": "unblocked", "reason_codes": [], "active_exception_ids": ["missing"], "exceptions": []},
        ]
        for facts in cases:
            with self.subTest(facts=facts):
                # Arrange / Act
                result = phase35.evaluate_verdict(facts)

                # Assert
                self.assertEqual(result["cutover_verdict"], "blocked")

    def test_cutover_01_exception_boundaries_fail_closed(self) -> None:
        cases = [
            ("broad", self.exception(exact_scope=False)),
            ("unmatched", self.exception(decision_id="other")),
            ("rejected", self.exception(decision_value="reject")),
            ("expired", self.exception(active=False)),
            ("stale", self.exception(validation_state="stale")),
            ("invalid", self.exception(validation_state="invalid")),
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

    def test_cutover_03_route_truth_table_is_exclusive_and_planning_only(self) -> None:
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
                self.assertEqual(route["requires_fresh_cutover_decision"], requires_fresh)
                self.assertTrue(route["planning_only"])
                self.assertFalse(route["production_actions_authorized"])

    def test_t_35_01_audit_links_cover_all_nine_categories_deterministically(self) -> None:
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
        external_link = next(link for link in links if link["kind"] == "evidence-packet")

        # Assert
        self.assertNotIn("digest", external_link)

    def test_t_35_01_exact_set_anti_join_blocks_every_mismatch(self) -> None:
        expected = phase35.derive_audit_links(self.audit_sources())
        mutations = {}
        mutations["audit-link-missing"] = expected[1:]
        mutations["audit-link-extra"] = expected + [
            {
                **expected[0],
                "link_id": "audit-extra",
                "target_id": "extra",
            }
        ]
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

    def test_t_35_01_link_digest_uses_canonical_sanitized_projection(self) -> None:
        # Arrange
        source = self.audit_sources()[0]
        canonical = json.dumps(source["digest_source"], sort_keys=True, separators=(",", ":")).encode()

        # Act
        link = phase35.derive_audit_links([source])[0]

        # Assert
        self.assertEqual(link["digest"], hashlib.sha256(canonical).hexdigest())

    def test_cutover_03_repair_scope_uses_exact_ordinary_exit_review_refs(self) -> None:
        # Arrange
        blocker = self.blocker_row()
        ledger = self.ledger_row()

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [ledger], [], [])

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

    def test_cutover_03_repair_scope_adds_exact_exception_criteria(self) -> None:
        # Arrange
        blocker = self.blocker_row(blocker_kind="exception_request")
        exception = {
            "decision_id": "exception-1",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "expiry_or_review_trigger": "review-before-cutover",
            "affected_gates": ["final-simulator-evidence"],
        }

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [self.ledger_row()], [exception], [])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(
            scope[0]["exit_review_criterion_refs"][-2:],
            [
                f"{PHASE33_EXCEPTION_REGISTER}#exception-1/expiry_or_review_trigger",
                f"{PHASE33_EXCEPTION_REGISTER}#exception-1/affected_gates",
            ],
        )

    def test_cutover_03_repair_scope_adds_exact_residual_risk_criteria(self) -> None:
        # Arrange
        blocker = self.blocker_row()
        residual = {
            "decision_id": "risk-1",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "follow_up_refs": ["external://phase33/risk-follow-up"],
            "affected_gates": ["final-simulator-evidence"],
        }

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [self.ledger_row()], [], [residual])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(
            scope[0]["exit_review_criterion_refs"][-2:],
            [
                f"{PHASE33_RESIDUAL_REGISTER}#risk-1/follow_up_refs",
                f"{PHASE33_RESIDUAL_REGISTER}#risk-1/affected_gates",
            ],
        )

    def test_cutover_03_unresolved_or_fabricated_scope_stays_blocked(self) -> None:
        cases = [
            ("missing-ledger", [], [], []),
            (
                "wrong-classification",
                [{**self.ledger_row(), "classification_ref": f"{PHASE32_REGISTER}#other"}],
                [],
                [],
            ),
            (
                "fabricated-exception",
                [self.ledger_row()],
                [
                    {
                        "decision_id": "exception-1",
                        "source_row_refs": [f"{PHASE32_REGISTER}#other"],
                        "linked_blocker_refs": [f"{PHASE32_REGISTER}#other"],
                        "expiry_or_review_trigger": "review",
                        "affected_gates": ["final-simulator-evidence"],
                    }
                ],
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
        self.assertEqual(projection["demotion_decision_validation_state"], "missing")
        self.assertEqual(projection["demotion_decision_state"], "missing")
        self.assertEqual(projection["demotion_decision_source_refs"], [])
        self.assertEqual(projection["demotion_gate_state"], "blocked")
        self.assertEqual(projection["demotion_gate_reason_codes"], ["approval-missing"])

    def test_t_35_06_demotion_malformed_stale_lifecycle_and_other_invalid_remain_distinct(self) -> None:
        cases = [
            ("malformed", {"phase": 3}, [], "malformed"),
            (
                "stale",
                self.demotion_handoff(),
                [self.demotion_decision(decision_timestamp="2020-01-01T00:00:00Z")],
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
                projection = phase35.project_demotion(handoff, records, dry_run)

                # Assert
                self.assertEqual(projection["demotion_decision_validation_state"], expected_state)
                self.assertEqual(projection["demotion_gate_state"], "blocked")

    def test_t_35_06_valid_reject_is_valid_and_preserves_safe_source_refs(self) -> None:
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
        self.assertEqual(projection["demotion_decision_validation_state"], "valid")
        self.assertEqual(projection["demotion_decision_state"], "reject")
        self.assertEqual(
            projection["demotion_decision_source_refs"],
            [f"{PHASE32_REGISTER}#blocker-1"],
        )
        self.assertEqual(projection["demotion_gate_reason_codes"], ["approval-rejected"])

    def test_t_35_06_valid_approve_does_not_upgrade_cutover_or_gate(self) -> None:
        # Arrange
        handoff = self.demotion_handoff()
        records = [self.demotion_decision()]
        dry_run = self.demotion_dry_run(gate_state="blocked", reason_codes=["readiness-blocked"])

        # Act
        projection = phase35.project_demotion(handoff, records, dry_run)
        verdict = phase35.evaluate_verdict(
            {
                "readiness_state": "blocked",
                "reason_codes": ["readiness-blocked"],
                "active_exception_ids": [],
                "exceptions": [],
            }
        )

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"], "valid")
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
        verdict = phase35.evaluate_verdict(
            {
                "readiness_state": "blocked",
                "reason_codes": ["readiness-blocked"],
                "active_exception_ids": [],
                "exceptions": [],
            }
        )

        # Assert
        self.assertEqual(projection["demotion_gate_state"], "open")
        self.assertEqual(verdict["cutover_verdict"], "blocked")

    def test_t_35_02_paths_reject_absolute_traversal_wrong_root_overlap_and_symlink_escape(self) -> None:
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

    def test_t_35_03_security_rejects_forbidden_fields_text_raw_payloads_and_unsafe_refs(self) -> None:
        cases = [
            {"token_value": "redacted"},
            {"nested": {"private_key": "redacted"}},
            {"rationale": "production demotion complete"},
            {"raw_payload": {"data": "not-allowed"}},
            {"source_refs": ["../unsafe.json"]},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                # Arrange / Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.scan_security(payload)

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

    def test_t_35_05_caller_supplied_authority_flags_are_rejected(self) -> None:
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
            "audit_link_counts_by_kind": {kind: 1 for kind in AUDIT_KINDS},
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

    def test_default_projection_is_blocked_repair_without_synthesized_authority(self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        default = contract["default_behavior"]

        # Assert
        self.assertEqual(default["cutover_verdict"], "blocked")
        self.assertEqual(default["route"], "targeted-blocker-repair")
        self.assertEqual(default["demotion_decision_validation_state"], "missing")
        self.assertEqual(default["demotion_decision_state"], "missing")
        self.assertEqual(default["demotion_decision_source_refs"], [])
        self.assertEqual(default["demotion_gate_state"], "blocked")
        self.assertFalse(default["synthesizes_evidence"])
        self.assertFalse(default["synthesizes_approval"])
        self.assertFalse(default["synthesizes_exception"])
        self.assertFalse(default["synthesizes_demotion_authorization"])

    def test_wiring_contract_requires_exact_bazel_workflow_and_just_strings(self) -> None:
        # Arrange
        expected = phase35.required_wiring_strings()

        # Act / Assert
        self.assertIn("phase35_source_ref_manifests", expected["tools_bazel"])
        self.assertIn("phase35_verify", expected["tools_bazel"])
        self.assertIn("phase35_verify_tests", expected["tools_bazel"])
        self.assertIn("phase35_cutover_decision_artifact_docs", expected["root_bazel"])
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


if __name__ == "__main__":
    unittest.main()
