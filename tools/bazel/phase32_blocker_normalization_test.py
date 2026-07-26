#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from phase32_blocker_normalization import (
    NormalizationError,
    adapt_phase26_table,
    canonical_row_id,
    canonical_source_identity,
    decision_identity,
    validate_identity_bindings,
)

EXPECTED_CRITERIA = {
    "final-ci-evidence",
    "final-simulator-evidence",
}
REQUIRED_ROW_FIELDS = {
    "artifact_refs",
    "criterion_id",
    "evidence_family",
    "evidence_refs",
    "exception_status",
    "failure_reason",
    "generated_at_utc",
    "maintainer_state",
    "owning_phase",
    "redaction_status",
    "requirement_ids",
    "source_lifecycle_id",
    "source_lifecycle_status",
    "source_ref_status",
    "source_requirement_ids",
    "status",
}
ALLOWED_STATUSES = {"blocked", "failed", "passed"}
RECEIPT_REF = "build/ci-evidence/phase31/stream-receipts/release-signing-final-intake-receipt.json"
TABLE_REF = "build/ci-evidence/phase26/upstream-result-row-table.json"


def source_identity(subject: str = "final-ci-evidence") -> dict[str, str]:
    return canonical_source_identity(
        source_domain="release_signing",
        producer_phase="phase26",
        producer_artifact_kind="phase26_upstream_result_row_table",
        source_row_kind="upstream_result_criterion",
        source_subject_id=subject,
    )


def phase26_row(criterion_id: str,
                status: str = "passed") -> dict[str, object]:
    return {
        "artifact_refs": ["external://phase26/release/artifact.json"],
        "criterion_id": criterion_id,
        "evidence_family": "release",
        "evidence_refs": ["external://phase26/release/evidence.json"],
        "exception_status": "none",
        "failure_reason": "",
        "generated_at_utc": "2026-07-26T00:00:00Z",
        "maintainer_state": "accepted",
        "owning_phase": "26-release-signing-and-upstream-result-evidence",
        "redaction_status": "passed",
        "requirement_ids": ["INTAKE-04"],
        "source_lifecycle_id": "26-2026-06-24T13-36-46",
        "source_lifecycle_status": "current",
        "source_ref_status": "passed",
        "source_requirement_ids": ["EVID-04"],
        "status": status,
    }


def valid_table() -> dict[str, object]:
    return {
        "artifact_name":
        "phase26-release-signing-upstream-evidence",
        "rows": [
            phase26_row(criterion_id)
            for criterion_id in sorted(EXPECTED_CRITERIA)
        ],
    }


def adapt(table: dict[str, object]) -> list[dict[str, object]]:
    return adapt_phase26_table(
        table,
        expected_criteria=EXPECTED_CRITERIA,
        required_row_fields=REQUIRED_ROW_FIELDS,
        allowed_statuses=ALLOWED_STATUSES,
        receipt_ref=RECEIPT_REF,
        table_ref=TABLE_REF,
    )


class Phase32BlockerNormalizationTest(unittest.TestCase):

    def test_all_passed_phase26_table_preserves_complete_lineage(self) -> None:
        # Arrange
        table = valid_table()

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual({signal["source_subject_id"]
                          for signal in signals}, EXPECTED_CRITERIA)
        self.assertTrue(all(signal["status"] == "passed"
                            for signal in signals))
        self.assertTrue(
            all(signal["receipt_ref"] == RECEIPT_REF for signal in signals))
        self.assertTrue(
            all(signal["table_ref"] == TABLE_REF for signal in signals))

    def test_missing_rows_is_one_atomic_malformed_signal(self) -> None:
        # Arrange
        table = valid_table()
        del table["rows"]

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"], "malformed")

    def test_non_list_rows_is_one_atomic_malformed_signal(self) -> None:
        # Arrange
        table = valid_table()
        table["rows"] = {}

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"], "malformed")

    def test_empty_rows_is_one_atomic_malformed_signal(self) -> None:
        # Arrange
        table = valid_table()
        table["rows"] = []

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"], "malformed")

    def test_non_object_row_is_one_atomic_malformed_signal(self) -> None:
        # Arrange
        table = valid_table()
        table["rows"][0] = "not-an-object"

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"], "malformed")

    def test_missing_required_field_is_one_atomic_malformed_signal(
            self) -> None:
        # Arrange
        table = valid_table()
        del table["rows"][0]["maintainer_state"]

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"], "malformed")

    def test_mistyped_required_field_is_one_atomic_malformed_signal(
            self) -> None:
        # Arrange
        table = valid_table()
        table["rows"][0]["criterion_id"] = 42

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"], "malformed")

    def test_duplicate_criterion_is_one_atomic_malformed_signal(self) -> None:
        # Arrange
        table = valid_table()
        table["rows"][1]["criterion_id"] = table["rows"][0]["criterion_id"]

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"], "malformed")

    def test_unknown_criterion_is_one_atomic_malformed_signal(self) -> None:
        # Arrange
        table = valid_table()
        table["rows"][0]["criterion_id"] = "unknown-criterion"

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"], "malformed")

    def test_unsupported_envelope_is_one_atomic_unknown_signal(self) -> None:
        # Arrange
        table = valid_table()
        table["artifact_name"] = "unsupported-release-envelope"

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"],
                         "unknown_unclassified")

    def test_unsupported_status_is_one_atomic_unknown_signal(self) -> None:
        # Arrange
        table = valid_table()
        table["rows"][0]["status"] = "new-release-status"

        # Act
        signals = adapt(table)

        # Assert
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["adapter_problem_kind"],
                         "unknown_unclassified")

    def test_row_id_depends_only_on_five_field_source_identity(self) -> None:
        # Arrange
        identity = source_identity()

        # Act
        row_id = canonical_row_id(identity)

        # Assert
        self.assertTrue(row_id.startswith("blocker-"))
        self.assertEqual(
            row_id, canonical_row_id(dict(reversed(list(identity.items())))))

    def test_mutable_blocker_metadata_does_not_change_row_id(self) -> None:
        # Arrange
        first = {
            **source_identity(),
            "owner_ref": "release-maintainer",
            "status": "failed",
            "evidence_refs": ["external://phase26/first.json"],
            "generated_at_utc": "2026-07-26T00:00:00Z",
            "required_next_action": "Repair the release.",
        }
        second = {
            **source_identity(),
            "owner_ref": "cutover-maintainer",
            "status": "blocked",
            "evidence_refs": ["external://phase26/second.json"],
            "generated_at_utc": "2026-07-26T01:00:00Z",
            "required_next_action": "Route an explicit decision.",
        }

        # Act
        first_row_id = canonical_row_id(first)
        second_row_id = canonical_row_id(second)

        # Assert
        self.assertEqual(first_row_id, second_row_id)

    def test_distinct_source_subjects_have_distinct_row_ids(self) -> None:
        # Arrange
        first = source_identity("final-ci-evidence")
        second = source_identity("final-simulator-evidence")

        # Act
        first_row_id = canonical_row_id(first)
        second_row_id = canonical_row_id(second)

        # Assert
        self.assertNotEqual(first_row_id, second_row_id)

    def test_identical_subjects_on_different_axes_are_distinct_decisions(
            self) -> None:
        # Arrange
        subject = "final-retained-code-acceptance"

        # Act
        retained = decision_identity(decision_axis="retained_code",
                                     decision_subject_id=subject)
        readiness = decision_identity(decision_axis="readiness",
                                      decision_subject_id=subject)

        # Assert
        self.assertNotEqual(retained, readiness)

    def test_duplicate_source_tuple_is_rejected(self) -> None:
        # Arrange
        identity = source_identity()
        rows = [
            {
                **identity,
                **decision_identity(decision_axis="readiness",
                                    decision_subject_id="final-ci-evidence")
            },
            {
                **identity,
                **decision_identity(decision_axis="readiness",
                                    decision_subject_id="final-ci-evidence")
            },
        ]

        # Act / Assert
        with self.assertRaises(NormalizationError):
            validate_identity_bindings(rows)

    def test_incompatible_source_remapping_is_rejected_without_row_id_churn(
            self) -> None:
        # Arrange
        identity = source_identity()
        row_id = canonical_row_id(identity)
        rows = [
            {
                **identity,
                **decision_identity(decision_axis="readiness",
                                    decision_subject_id="final-ci-evidence"),
            },
            {
                **copy.deepcopy(identity),
                **decision_identity(decision_axis="exception",
                                    decision_subject_id="final-ci-evidence"),
            },
        ]

        # Act / Assert
        with self.assertRaises(NormalizationError):
            validate_identity_bindings(rows)
        self.assertEqual(row_id, canonical_row_id(identity))


if __name__ == "__main__":
    unittest.main()
