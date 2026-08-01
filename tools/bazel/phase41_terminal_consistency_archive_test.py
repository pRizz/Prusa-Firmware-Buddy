#!/usr/bin/env python3
from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from phase41_terminal_consistency_policy import evaluate_terminal_consistency
from phase41_terminal_consistency_test_support import coherent_snapshot


class Phase41ArchiveVerificationTest(unittest.TestCase):

    def assert_has_code(self, code: str, **verification_changes: object) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        verification = replace(snapshot.verification, **verification_changes)

        # Act
        violations = evaluate_terminal_consistency(
            replace(snapshot, verification=verification), "pre-archive")

        # Assert
        self.assertIn(code, {violation.code for violation in violations})

    def test_pre_audit_allows_absent_verification(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        verification = replace(snapshot.verification,
                               present=False,
                               parsed=False,
                               status="missing",
                               fresh=False,
                               verified_at=None)

        # Act
        violations = evaluate_terminal_consistency(
            replace(snapshot, verification=verification), "pre-audit")

        # Assert
        self.assertEqual(violations, ())

    def test_pre_archive_rejects_missing_verification(self) -> None:
        self.assert_has_code("P41_VERIFICATION_MISSING",
                             present=False,
                             parsed=False,
                             status="missing",
                             fresh=False,
                             verified_at=None)

    def test_pre_archive_rejects_malformed_verification(self) -> None:
        self.assert_has_code("P41_VERIFICATION_MISSING", parsed=False)

    def test_pre_archive_rejects_failed_verification(self) -> None:
        self.assert_has_code("P41_VERIFICATION_STATUS", status="gaps_found")

    def test_pre_archive_rejects_verification_older_than_phase_summary(
            self) -> None:
        self.assert_has_code("P41_VERIFICATION_STALE", fresh=False)

    def test_pre_archive_rejects_audit_older_than_verification(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        verified_at = datetime(2026, 8, 1, 19, tzinfo=timezone.utc)
        verification = replace(snapshot.verification,
                               verified_at=verified_at)
        audit = replace(snapshot.audit,
                        audited_at=verified_at - timedelta(seconds=1))

        # Act
        violations = evaluate_terminal_consistency(
            replace(snapshot, verification=verification, audit=audit),
            "pre-archive")

        # Assert
        self.assertIn("P41_AUDIT_PREDATES_VERIFICATION",
                      {violation.code
                       for violation in violations})

    def test_pre_archive_rejects_missing_verification_timestamp(self) -> None:
        self.assert_has_code("P41_VERIFICATION_TIMESTAMP", verified_at=None)


if __name__ == "__main__":
    unittest.main()
