#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from phase41_terminal_consistency import (
    VERIFICATION_PATH,
    BoundaryParser,
    normalized_status,
    parse_verification,
    validation_tasks,
)


class Phase41BoundaryParserTest(unittest.TestCase):

    def test_validation_status_grammar_rejects_negative_substrings(self) -> None:
        # Arrange
        values = ("incomplete", "not complete", "not passed", "")

        # Act
        statuses = tuple(normalized_status(value) for value in values)

        # Assert
        self.assertEqual(statuses, ("unsupported", ) * len(values))

    def test_validation_status_grammar_strips_one_known_marker(self) -> None:
        # Arrange / Act / Assert
        self.assertEqual(normalized_status("✅ green"), "green")
        self.assertEqual(normalized_status("❌ red"), "red")
        self.assertEqual(normalized_status("⬜ pending"), "pending")

    def test_validation_tasks_require_task_or_campaign_identity(self) -> None:
        # Arrange
        text = """| Label | Status |
| --- | --- |
| unrelated | green |
"""

        # Act / Assert
        self.assertEqual(validation_tasks(text), ())

    def test_empty_validation_task_status_is_unsupported(self) -> None:
        # Arrange
        text = """| Task ID | Status |
| --- | --- |
| 41-01-01 | |
"""

        # Act / Assert
        self.assertEqual(validation_tasks(text),
                         (("41-01-01", "unsupported"), ))

    def test_absent_verification_is_optional_at_parse_boundary(self) -> None:
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            parser = BoundaryParser(Path(temp_dir))

            # Act
            verification = parse_verification(parser)

            # Assert
            self.assertFalse(verification.present)
            self.assertFalse(verification.parsed)
            self.assertEqual(parser.violations, [])

    def test_present_verification_parses_exact_artifact(self) -> None:
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            verification_path = root / VERIFICATION_PATH
            verification_path.parent.mkdir(parents=True)
            verification_path.write_text(
                "---\nverified: 2026-08-01T19:00:00Z\nstatus: passed\n---\n",
                encoding="utf-8",
            )
            (verification_path.parent / "41-03-SUMMARY.md").write_text(
                "---\ngenerated_at: 2026-08-01T18:00:00Z\n---\n",
                encoding="utf-8",
            )
            parser = BoundaryParser(root)

            # Act
            verification = parse_verification(parser)

            # Assert
            self.assertTrue(verification.present)
            self.assertTrue(verification.parsed)
            self.assertTrue(verification.fresh)
            self.assertEqual(verification.status, "passed")
            self.assertEqual(parser.violations, [])

    def test_malformed_verification_fails_at_parse_boundary(self) -> None:
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            verification_path = root / VERIFICATION_PATH
            verification_path.parent.mkdir(parents=True)
            verification_path.write_text("status: passed\n", encoding="utf-8")
            parser = BoundaryParser(root)

            # Act
            verification = parse_verification(parser)

            # Assert
            self.assertTrue(verification.present)
            self.assertFalse(verification.parsed)
            self.assertIn("P41_FRONTMATTER_MALFORMED",
                          {item.code for item in parser.violations})


if __name__ == "__main__":
    unittest.main()
