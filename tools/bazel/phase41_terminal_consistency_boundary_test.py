#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
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
    validation_signoff,
)
from phase41_terminal_consistency_policy import (
    MILESTONE_PHASES,
    evaluate_terminal_consistency,
    exit_code_for_violations,
)
from phase41_terminal_consistency_test_support import (
    coherent_snapshot,
    replace_at,
)


def valid_audit_text() -> str:
    flow_rows = "\n".join(f"| {identity} | complete | evidence |"
                          for identity in AUDIT_FLOW_IDENTITIES)
    nyquist_rows = "\n".join(f"| {phase} | compliant |"
                             for phase in range(31, 42))
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

    def validation_codes(self, phase: int, text: str) -> set[str]:
        parser = BoundaryParser(Path("."))
        path = f"{phase:02d}-VALIDATION.md"
        tasks = validation_tasks(parser, path, text)
        snapshot = coherent_snapshot()
        index = MILESTONE_PHASES.index(phase)
        validation = replace(
            snapshot.validations[index],
            task_identities=tuple(identity for identity, _ in tasks),
            task_statuses=tuple(status for _, status in tasks),
        )
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, index,
                                                 validation),
                          boundary_violations=tuple(parser.violations))
        violations = evaluate_terminal_consistency(mutated, "pre-archive")
        self.assertNotEqual(exit_code_for_violations(violations), 0)
        return {violation.code for violation in violations}

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
                      {item.code
                       for item in parser.violations})

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
                      {item.code
                       for item in parser.violations})

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
                      {item.code
                       for item in parser.violations})

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
                      {item.code
                       for item in parser.violations})

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
                              {item.code
                               for item in parser.violations})

    def test_missing_audit_rollup_fails_closed(self) -> None:
        # Arrange
        text = valid_audit_text().replace("| Runtime integration gaps | 0 |\n",
                                          "")

        # Act
        audit, parser = self.parse_audit_text(text)

        # Assert
        self.assertFalse(audit.parsed)
        self.assertIsNone(audit.integration_gaps)
        self.assertIn("P41_AUDIT_ROLLUP_MISSING",
                      {item.code
                       for item in parser.violations})

    def test_validation_status_grammar_rejects_negative_substrings(
            self) -> None:
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
        text = """## Per-Task Verification Map

| Label | Status |
| --- | --- |
| unrelated | green |
"""

        # Act
        parser = BoundaryParser(Path("."))
        tasks = validation_tasks(parser, "31-VALIDATION.md", text)

        # Assert
        self.assertEqual(tasks, ())
        self.assertIn("P41_TABLE_REQUIRED",
                      {item.code
                       for item in parser.violations})

    def test_empty_validation_task_status_is_unsupported(self) -> None:
        # Arrange
        text = """## Per-Task Verification Map

| Task ID | Status |
| --- | --- |
| 41-01-01 | |
"""

        # Act
        parser = BoundaryParser(Path("."))
        tasks = validation_tasks(parser, "41-VALIDATION.md", text)

        # Assert
        self.assertEqual(tasks, (("41-01-01", "unsupported"), ))

    def test_fabricated_validation_identity_fails_after_boundary_parse(
            self) -> None:
        # Arrange
        text = """## Per-Task Verification Map

| Task ID | Status |
| --- | --- |
| fabricated-row | green |
"""

        # Act
        codes = self.validation_codes(31, text)

        # Assert
        self.assertIn("P41_VALIDATION_TASK_IDENTITIES", codes)

    def test_valid_looking_validation_subset_fails_after_boundary_parse(
            self) -> None:
        # Arrange
        text = """## Per-Task Verification Map

| Task ID | Status |
| --- | --- |
| 31-W0-01 | green |
| 31-W0-02 | green |
| 31-W0-03 | green |
| 31-W0-04 | green |
"""

        # Act
        codes = self.validation_codes(31, text)

        # Assert
        self.assertIn("P41_VALIDATION_TASK_IDENTITIES", codes)

    def test_duplicate_validation_status_header_fails_closed(self) -> None:
        # Arrange
        text = """## Per-Task Verification Map

| Task ID | Status | status |
| --- | --- | --- |
| 31-W0-01 | red | green |
"""

        # Act
        codes = self.validation_codes(31, text)

        # Assert
        self.assertIn("P41_TABLE_HEADER_DUPLICATE", codes)

    def test_repeated_validation_table_and_sections_fail_closed(self) -> None:
        cases = {
            "table":
            """## Per-Task Verification Map

| Task ID | Status |
| --- | --- |
| 31-W0-01 | green |

contradictory evidence

| Task ID | Status |
| --- | --- |
| 31-W0-01 | red |
""",
            "verification-section":
            """## Per-Task Verification Map

| Task ID | Status |
| --- | --- |
| 31-W0-01 | green |

## Per-Task Verification Map

| Task ID | Status |
| --- | --- |
| 31-W0-01 | red |
""",
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                # Act
                codes = self.validation_codes(31, text)

                # Assert
                expected = ("P41_TABLE_REQUIRED"
                            if name == "table" else "P41_SECTION_REQUIRED")
                self.assertIn(expected, codes)

    def test_repeated_validation_signoff_fails_closed(self) -> None:
        # Arrange
        text = """## Validation Sign-Off

- [x] complete

## Validation Sign-Off

- [ ] incomplete
"""
        parser = BoundaryParser(Path("."))

        # Act
        complete = validation_signoff(parser, "31-VALIDATION.md", text)
        snapshot = replace(coherent_snapshot(),
                           boundary_violations=tuple(parser.violations))
        violations = evaluate_terminal_consistency(snapshot, "pre-archive")

        # Assert
        self.assertFalse(complete)
        self.assertIn("P41_SECTION_REQUIRED",
                      {item.code
                       for item in violations})
        self.assertNotEqual(exit_code_for_violations(violations), 0)

    def test_repeated_unrelated_prose_headings_remain_allowed(self) -> None:
        # Arrange
        text = """## Notes

first

## Per-Task Verification Map

| Task ID | Status |
| --- | --- |
| 31-W0-01 | green |

## Notes

second

## Validation Sign-Off

- [x] complete
"""
        parser = BoundaryParser(Path("."))

        # Act
        tasks = validation_tasks(parser, "31-VALIDATION.md", text)
        complete = validation_signoff(parser, "31-VALIDATION.md", text)

        # Assert
        self.assertEqual(tasks, (("31-W0-01", "green"), ))
        self.assertTrue(complete)
        self.assertEqual(parser.violations, [])

    def test_duplicate_audit_status_headers_fail_closed(self) -> None:
        cases = {
            "flow-status":
            valid_audit_text().replace(
                "| Flow | Status | Evidence |\n| --- | --- | --- |",
                "| Flow | Status | status | Evidence |\n"
                "| --- | --- | --- | --- |",
            ).replace(" | complete | evidence |",
                      " | incomplete | complete | evidence |"),
            "nyquist-classification":
            valid_audit_text().replace(
                "| Phase | Audit classification |\n| --- | --- |",
                "| Phase | Audit classification | audit CLASSIFICATION |\n"
                "| --- | --- | --- |",
            ).replace(" | compliant |", " | noncompliant | compliant |"),
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                # Act
                audit, parser = self.parse_audit_text(text)
                snapshot = replace(
                    coherent_snapshot(),
                    audit=audit,
                    boundary_violations=tuple(parser.violations),
                )
                violations = evaluate_terminal_consistency(
                    snapshot, "pre-archive")

                # Assert
                self.assertFalse(audit.parsed)
                self.assertIn("P41_TABLE_HEADER_DUPLICATE",
                              {item.code
                               for item in violations})
                self.assertNotEqual(exit_code_for_violations(violations), 0)

    def test_repeated_audit_sections_and_rollups_fail_closed(self) -> None:
        cases = {
            "flow-section":
            valid_audit_text() + """
## End-to-End Flows

| Flow | Status | Evidence |
| --- | --- | --- |
| Four-stream intake to canonical blocker register | incomplete | contradiction |
""",
            "nyquist-section":
            valid_audit_text() + """
## Nyquist Coverage

| Phase | Audit classification |
| --- | --- |
| 31 | noncompliant |
""",
            "rollup-row":
            valid_audit_text().replace(
                "| Runtime integration gaps | 0 |",
                "| Runtime integration gaps | 0 |\n"
                "| Runtime integration gaps | 1 |",
            ),
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                # Act
                audit, parser = self.parse_audit_text(text)
                snapshot = replace(
                    coherent_snapshot(),
                    audit=audit,
                    boundary_violations=tuple(parser.violations),
                )
                violations = evaluate_terminal_consistency(
                    snapshot, "pre-archive")

                # Assert
                self.assertFalse(audit.parsed)
                expected = ("P41_SECTION_REQUIRED" if name.endswith("section")
                            else "P41_AUDIT_ROLLUP_MISSING")
                self.assertIn(expected, {item.code for item in violations})
                self.assertNotEqual(exit_code_for_violations(violations), 0)

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
                          {item.code
                           for item in parser.violations})


if __name__ == "__main__":
    unittest.main()
