#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from phase41_terminal_consistency import (
    AUDIT_FLOW_IDENTITIES,
    AUDIT_PATH,
    VERIFICATION_PATH,
    BoundaryParser,
    normalized_status,
    parse_audit,
    parse_phases_and_inventories,
    parse_verification,
    validation_tasks,
)


def valid_audit_text() -> str:
    flow_rows = "\n".join(
        f"| {identity} | complete | evidence |"
        for identity in AUDIT_FLOW_IDENTITIES)
    nyquist_rows = "\n".join(
        f"| {phase} | compliant |" for phase in range(31, 42))
    return f"""---
audited: 2026-08-01T19:00:00Z
status: passed
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
"""


class Phase41BoundaryParserTest(unittest.TestCase):

    def parse_roadmap(self, text: str):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        parser = BoundaryParser(Path(temp_dir.name))
        parse_phases_and_inventories(parser, text)
        return parser

    def test_duplicate_roadmap_lifecycle_rows_fail_closed(self) -> None:
        # Arrange
        text = """- [x] **Phase 31: First**
- [x] **Phase 31: Duplicate**
"""

        # Act
        parser = self.parse_roadmap(text)

        # Assert
        self.assertIn("P41_ROADMAP_PHASE_DUPLICATE",
                      {item.code for item in parser.violations})

    def test_duplicate_roadmap_phase_headings_fail_closed(self) -> None:
        # Arrange
        text = """### Phase 31: First
**Plans**: 1 plans
- [x] 31-01-PLAN.md
### Phase 31: Duplicate
**Plans**: 1 plans
- [x] 31-01-PLAN.md
"""

        # Act
        parser = self.parse_roadmap(text)

        # Assert
        self.assertIn("P41_ROADMAP_PHASE_DUPLICATE",
                      {item.code for item in parser.violations})

    def test_duplicate_roadmap_plan_rows_fail_closed(self) -> None:
        # Arrange
        text = """### Phase 31: First
**Plans**: 1 plans
- [x] 31-01-PLAN.md
- [x] 31-01-PLAN.md
"""

        # Act
        parser = self.parse_roadmap(text)

        # Assert
        self.assertIn("P41_ROADMAP_PLAN_DUPLICATE",
                      {item.code for item in parser.violations})

    def test_duplicate_roadmap_plan_progress_rows_fail_closed(self) -> None:
        # Arrange
        text = """### Phase 31: First
**Plans**: 1 plans
**Plans**: 1/1 plans complete
- [x] 31-01-PLAN.md
"""

        # Act
        parser = self.parse_roadmap(text)

        # Assert
        self.assertIn("P41_ROADMAP_PLAN_PROGRESS_DUPLICATE",
                      {item.code for item in parser.violations})

    def parse_audit_text(self, text: str):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        audit_path = root / AUDIT_PATH
        audit_path.parent.mkdir(parents=True)
        audit_path.write_text(text, encoding="utf-8")
        parser = BoundaryParser(root)
        return parse_audit(parser), parser

    def test_missing_audit_sections_fail_closed(self) -> None:
        for heading in ("End-to-End Flows", "Nyquist Coverage"):
            with self.subTest(heading=heading):
                # Arrange
                text = valid_audit_text().replace(f"## {heading}",
                                                  f"## Missing {heading}")

                # Act
                audit, parser = self.parse_audit_text(text)

                # Assert
                self.assertFalse(audit.parsed)
                self.assertIn("P41_AUDIT_SECTION_MISSING",
                              {item.code for item in parser.violations})

    def test_missing_audit_rollup_fails_closed(self) -> None:
        # Arrange
        text = valid_audit_text().replace(
            "| Runtime integration gaps | 0 |\n", "")

        # Act
        audit, parser = self.parse_audit_text(text)

        # Assert
        self.assertFalse(audit.parsed)
        self.assertIsNone(audit.integration_gaps)
        self.assertIn("P41_AUDIT_ROLLUP_MISSING",
                      {item.code for item in parser.violations})

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
