#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from phase41_terminal_consistency import (
    AUDIT_FLOW_IDENTITIES,
    AUDIT_PATH,
    VERIFICATION_PATH,
    BoundaryParser,
    latest_phase41_summary_time,
    parse_audit,
    parse_verification,
)


class Phase41TimestampBoundaryTest(unittest.TestCase):

    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        (root / VERIFICATION_PATH).parent.mkdir(parents=True)
        return temp_dir, root

    def write_summary(self, root: Path, name: str,
                      maybe_timestamp: str | None) -> None:
        timestamp_line = (f"generated_at: {maybe_timestamp}\n"
                          if maybe_timestamp is not None else "")
        (root / VERIFICATION_PATH).parent.joinpath(name).write_text(
            f"---\n{timestamp_line}---\n",
            encoding="utf-8",
        )

    def write_audit(self, root: Path,
                    maybe_timestamp: str | None) -> None:
        timestamp_line = (f"audited: {maybe_timestamp}\n"
                          if maybe_timestamp is not None else "")
        flow_rows = "\n".join(
            f"| {identity} | complete | evidence |"
            for identity in AUDIT_FLOW_IDENTITIES)
        nyquist_rows = "\n".join(
            f"| {phase} | compliant |" for phase in range(31, 42))
        audit_path = root / AUDIT_PATH
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text(
            f"""---
{timestamp_line}status: passed
---

## Scope

| Item | Result |
| --- | --- |
| Phases | 31 through 41 |
| Requirements | 16 |
| Fully coherent | 16 / 16 |
| Runtime integration gaps | 0 |
| Metadata gaps | 0 |
| Nyquist gaps | 0 |
| Milestone archival blockers | 0 |

## End-to-End Flows

| Flow | Status | Evidence |
| --- | --- | --- |
{flow_rows}

## Nyquist Coverage

| Phase | Audit classification |
| --- | --- |
{nyquist_rows}
""",
            encoding="utf-8",
        )

    def write_verification(self, root: Path,
                           maybe_timestamp: str | None) -> None:
        timestamp_line = (f"verified: {maybe_timestamp}\n"
                          if maybe_timestamp is not None else "")
        (root / VERIFICATION_PATH).write_text(
            f"---\n{timestamp_line}status: passed\n---\n",
            encoding="utf-8",
        )

    def test_summary_timestamp_errors_fail_closed(self) -> None:
        for label, maybe_timestamp in (
            ("missing", None),
            ("invalid", "not-a-timestamp"),
            ("naive", "2026-08-01T18:00:00"),
        ):
            with self.subTest(label=label):
                # Arrange
                _, root = self.make_root()
                self.write_summary(root, "41-01-SUMMARY.md", maybe_timestamp)
                parser = BoundaryParser(root)

                # Act
                maybe_latest = latest_phase41_summary_time(parser)

                # Assert
                self.assertIsNone(maybe_latest)
                self.assertEqual(
                    [item.code for item in parser.violations],
                    ["P41_TIMESTAMP_INVALID"],
                )

    def test_one_invalid_summary_poisons_freshness_cutoff(self) -> None:
        # Arrange
        _, root = self.make_root()
        self.write_summary(root, "41-01-SUMMARY.md",
                           "2026-08-01T17:00:00Z")
        self.write_summary(root, "41-02-SUMMARY.md", None)
        self.write_verification(root, "2026-08-01T19:00:00Z")
        parser = BoundaryParser(root)

        # Act
        verification = parse_verification(parser)

        # Assert
        self.assertFalse(verification.fresh)
        self.assertIn("P41_TIMESTAMP_INVALID",
                      {item.code for item in parser.violations})

    def test_audit_and_verification_timestamp_errors_fail_closed(self) -> None:
        for artifact, maybe_timestamp in (
            ("audit-missing", None),
            ("audit-invalid", "invalid"),
            ("audit-naive", "2026-08-01T19:00:00"),
            ("verification-missing", None),
            ("verification-invalid", "invalid"),
            ("verification-naive", "2026-08-01T18:00:00"),
        ):
            with self.subTest(artifact=artifact):
                # Arrange
                _, root = self.make_root()
                self.write_summary(root, "41-01-SUMMARY.md",
                                   "2026-08-01T17:00:00Z")
                parser = BoundaryParser(root)
                if artifact.startswith("audit"):
                    self.write_audit(root, maybe_timestamp)
                else:
                    self.write_verification(root, maybe_timestamp)

                # Act
                record = (parse_audit(parser) if artifact.startswith("audit")
                          else parse_verification(parser))

                # Assert
                self.assertFalse(record.fresh)
                self.assertFalse(record.parsed)
                self.assertIn("P41_TIMESTAMP_INVALID",
                              {item.code for item in parser.violations})

    def test_all_naive_timestamps_fail_closed_without_throwing(self) -> None:
        # Arrange
        _, root = self.make_root()
        self.write_summary(root, "41-01-SUMMARY.md",
                           "2026-08-01T17:00:00")
        self.write_audit(root, "2026-08-01T19:00:00")
        self.write_verification(root, "2026-08-01T18:00:00")
        parser = BoundaryParser(root)

        # Act
        audit = parse_audit(parser)
        verification = parse_verification(parser)

        # Assert
        self.assertFalse(audit.fresh)
        self.assertFalse(verification.fresh)
        self.assertIsNone(audit.audited_at)
        self.assertIsNone(verification.verified_at)
        self.assertEqual(
            sum(item.code == "P41_TIMESTAMP_INVALID"
                for item in parser.violations),
            3,
        )

    def test_mixed_zone_timestamps_normalize_to_utc(self) -> None:
        # Arrange
        _, root = self.make_root()
        self.write_summary(root, "41-01-SUMMARY.md",
                           "2026-08-01T13:00:00-05:00")
        self.write_audit(root, "2026-08-01T14:00:00-05:00")
        self.write_verification(root, "2026-08-01T20:00:00+02:00")
        parser = BoundaryParser(root)

        # Act
        audit = parse_audit(parser)
        verification = parse_verification(parser)

        # Assert
        self.assertTrue(audit.fresh)
        self.assertTrue(audit.parsed)
        self.assertTrue(verification.fresh)
        self.assertEqual(audit.audited_at,
                         datetime(2026, 8, 1, 19, tzinfo=timezone.utc))
        self.assertEqual(verification.verified_at,
                         datetime(2026, 8, 1, 18, tzinfo=timezone.utc))
        self.assertNotIn("P41_TIMESTAMP_INVALID",
                         {item.code for item in parser.violations})


if __name__ == "__main__":
    unittest.main()
