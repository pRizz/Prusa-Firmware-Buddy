#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools/bazel/phase34_decision_reconciliation.py"
PHASE32_LIFECYCLE_ID = "32-2026-07-03T14-13-51"
PHASE33_LIFECYCLE_ID = "33-2026-07-04T01-36-41"
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"


class Phase34DecisionReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location(
            "phase34_decision_reconciliation",
            MODULE_PATH,
        )
        if spec is None or spec.loader is None:
            raise AssertionError("unable to load reconciliation module")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def row_ref(self, row_id: str) -> str:
        return f"{PHASE32_REGISTER_REF}#{row_id}"

    def canonical_row(
        self,
        row_id: str = "canonical-row",
        *,
        decision_axis: str = "retained_code",
        decision_subject_id: str = "decision-subject",
        row_problem_kind: str = "exception_requested",
        blocker_kind: str = "exception_request",
    ) -> dict[str, object]:
        return {
            "row_id": row_id,
            "row_ref": self.row_ref(row_id),
            "phase_lifecycle_id": PHASE32_LIFECYCLE_ID,
            "decision_axis": decision_axis,
            "decision_subject_id": decision_subject_id,
            "row_problem_kind": row_problem_kind,
            "blocker_kind": blocker_kind,
        }

    def decision(
        self,
        decision_value: str,
        *,
        decision_id: str = "decision-1",
        decision_axis: str = "retained_code",
        row_ref: str | None = None,
        decision_subject_id: str = "decision-subject",
        phase_lifecycle_id: str = PHASE33_LIFECYCLE_ID,
    ) -> dict[str, object]:
        return {
            "decision_id": decision_id,
            "decision_ref": f"phase33://decision/{decision_id}",
            "phase_lifecycle_id": phase_lifecycle_id,
            "decision_axis": decision_axis,
            "decision_value": decision_value,
            "decision_targets": [
                {
                    "row_ref": row_ref or self.row_ref("canonical-row"),
                    "decision_axis": decision_axis,
                    "decision_subject_id": decision_subject_id,
                }
            ],
        }

    def reconcile(
        self,
        rows: list[dict[str, object]],
        decisions: list[dict[str, object]],
        *,
        readiness_prerequisites_unblocked: bool = True,
    ) -> dict[str, object]:
        return self.module.reconcile_decision_rows(
            rows,
            decisions,
            expected_phase32_lifecycle_id=PHASE32_LIFECYCLE_ID,
            expected_phase33_lifecycle_id=PHASE33_LIFECYCLE_ID,
            readiness_prerequisites_unblocked=readiness_prerequisites_unblocked,
        )

    def test_exact_typed_binding_resolves_one_canonical_row(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision("accept")

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["rows"],
            [
                {
                    "row_id": "canonical-row",
                    "row_ref": self.row_ref("canonical-row"),
                    "decision_axis": "retained_code",
                    "decision_subject_id": "decision-subject",
                    "coverage_state": "covered",
                    "readiness_effect": "unblocked",
                    "linked_decision_refs": ["phase33://decision/decision-1"],
                    "reason_codes": [],
                }
            ],
        )
        self.assertEqual(result["diagnostics"], [])
        self.assertEqual(result["readiness_state"], "unblocked")

    def test_each_readiness_axis_uses_its_explicit_approving_value(self) -> None:
        cases = [
            ("retained_code", "accept"),
            ("retained_code", "exception_approve"),
            ("residual_risk", "accept"),
            ("exception", "approve"),
            ("readiness", "approve"),
        ]

        for index, (decision_axis, decision_value) in enumerate(cases):
            with self.subTest(decision_axis=decision_axis, decision_value=decision_value):
                # Arrange
                row_id = f"row-{index}"
                row = self.canonical_row(
                    row_id,
                    decision_axis=decision_axis,
                )
                decision = self.decision(
                    decision_value,
                    decision_axis=decision_axis,
                    row_ref=self.row_ref(row_id),
                )

                # Act
                result = self.reconcile([row], [decision])

                # Assert
                self.assertEqual(result["rows"][0]["coverage_state"], "covered")
                self.assertEqual(result["rows"][0]["readiness_effect"], "unblocked")
                self.assertEqual(result["rows"][0]["reason_codes"], [])

    def test_reference_demotion_approval_never_clears_readiness(self) -> None:
        # Arrange
        row = self.canonical_row(
            decision_axis="demotion",
        )
        decision = self.decision(
            "approve",
            decision_axis="demotion",
        )

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(result["rows"][0]["coverage_state"], "authorization-recorded")
        self.assertEqual(result["rows"][0]["readiness_effect"], "independent")
        self.assertEqual(result["rows"][0]["reason_codes"], [])

    def test_readiness_approval_never_grants_demotion_authorization(self) -> None:
        # Arrange
        row = self.canonical_row(decision_axis="readiness")
        decision = self.decision("approve", decision_axis="readiness")

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(result["rows"][0]["coverage_state"], "covered")
        self.assertNotEqual(result["rows"][0]["coverage_state"], "authorization-recorded")
        self.assertEqual(result["rows"][0]["readiness_effect"], "unblocked")

    def test_missing_decision_target_remains_blocked(self) -> None:
        # Arrange
        row = self.canonical_row()

        # Act
        result = self.reconcile([row], [])

        # Assert
        self.assertEqual(result["rows"][0]["coverage_state"], "blocked")
        self.assertEqual(result["rows"][0]["reason_codes"], ["decision-target-missing"])

    def test_zero_match_target_reports_row_mismatch_without_fallback(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision(
            "accept",
            row_ref=self.row_ref("missing-row"),
        )

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(result["rows"][0]["reason_codes"], ["decision-target-missing"])
        self.assertEqual(
            result["diagnostics"][0]["reason_code"],
            "decision-target-row-mismatch",
        )

    def test_same_row_ref_with_wrong_axis_reports_axis_mismatch(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision(
            "approve",
            decision_axis="readiness",
        )

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-target-axis-mismatch"],
        )

    def test_copied_decision_axis_mismatch_remains_blocked(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision("accept")
        decision["decision_axis"] = "readiness"

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-target-axis-mismatch"],
        )

    def test_same_row_ref_with_wrong_subject_reports_subject_mismatch(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision(
            "accept",
            decision_subject_id="similar-subject",
        )

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-target-subject-mismatch"],
        )

    def test_duplicate_exact_bindings_remain_blocked(self) -> None:
        # Arrange
        row = self.canonical_row()
        decisions = [
            self.decision("accept", decision_id="decision-1"),
            self.decision("accept", decision_id="decision-2"),
        ]

        # Act
        result = self.reconcile([row], decisions)

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-target-duplicate"],
        )
        self.assertEqual(
            result["rows"][0]["linked_decision_refs"],
            [
                "phase33://decision/decision-1",
                "phase33://decision/decision-2",
            ],
        )

    def test_conflicting_exact_bindings_remain_blocked(self) -> None:
        # Arrange
        row = self.canonical_row()
        decisions = [
            self.decision("accept", decision_id="decision-1"),
            self.decision("reject", decision_id="decision-2"),
        ]

        # Act
        result = self.reconcile([row], decisions)

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-target-conflict"],
        )

    def test_stale_decision_lifecycle_remains_blocked(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision(
            "accept",
            phase_lifecycle_id="stale-phase33-lifecycle",
        )

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-lifecycle-stale"],
        )

    def test_invalid_axis_value_remains_blocked(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision("approve")

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-value-invalid"],
        )

    def test_explicit_rejection_remains_linked_and_blocked(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision("reject")

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-rejected"],
        )
        self.assertEqual(
            result["rows"][0]["linked_decision_refs"],
            ["phase33://decision/decision-1"],
        )

    def test_hard_blocker_cannot_be_approved_away(self) -> None:
        # Arrange
        row = self.canonical_row(
            row_problem_kind="secret_tainted",
            blocker_kind="repair_item",
        )
        decision = self.decision("accept")

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-hard-blocker"],
        )

    def test_duplicate_canonical_exact_identity_reports_multi_match(self) -> None:
        # Arrange
        row = self.canonical_row()
        duplicate_row = dict(row)
        decision = self.decision("accept")

        # Act
        result = self.reconcile([row, duplicate_row], [decision])

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-target-multi-match"],
        )
        self.assertEqual(
            result["rows"][1]["reason_codes"],
            ["decision-target-multi-match"],
        )

    def test_readiness_approval_requires_unblocked_prerequisites(self) -> None:
        # Arrange
        row = self.canonical_row(decision_axis="readiness")
        decision = self.decision("approve", decision_axis="readiness")

        # Act
        result = self.reconcile(
            [row],
            [decision],
            readiness_prerequisites_unblocked=False,
        )

        # Assert
        self.assertEqual(
            result["rows"][0]["reason_codes"],
            ["decision-readiness-prerequisites-blocked"],
        )

    def test_malformed_target_emits_stable_diagnostic(self) -> None:
        # Arrange
        row = self.canonical_row()
        decision = self.decision("accept")
        decision["decision_targets"][0].pop("decision_subject_id")

        # Act
        result = self.reconcile([row], [decision])

        # Assert
        self.assertEqual(
            result["diagnostics"][0]["reason_code"],
            "decision-target-malformed",
        )
        self.assertEqual(result["rows"][0]["reason_codes"], ["decision-target-missing"])
        self.assertEqual(result["readiness_state"], "blocked")


if __name__ == "__main__":
    unittest.main()
