#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from phase41_terminal_consistency import load_snapshot
from phase41_terminal_consistency_contracts import (
    CANONICAL_REQUIREMENTS,
    EXPECTED_VALIDATION_IDENTITIES,
    MILESTONE_PHASES,
)
from phase41_terminal_consistency_policy import evaluate_terminal_consistency
from phase41_terminal_consistency_projection_parser import (
    parse_audit_frontmatter,
    parse_requirements_coverage,
    parse_roadmap_progress,
)
from phase41_terminal_consistency_markdown import BoundaryParser
from phase41_terminal_consistency_test_support import PLAN_COUNTS


class Phase41ProjectionBoundaryTest(unittest.TestCase):

    def make_root(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        self.write_fixture(root)
        return root

    def write_fixture(self, root: Path) -> None:
        planning = root / ".planning"
        planning.mkdir()
        (planning / "REQUIREMENTS.md").write_text(self.requirements_text(),
                                                  encoding="utf-8")
        (planning / "ROADMAP.md").write_text(self.roadmap_text(),
                                             encoding="utf-8")
        (planning / "STATE.md").write_text(self.state_text(), encoding="utf-8")
        (planning / "v1.3-MILESTONE-AUDIT.md").write_text(self.audit_text(),
                                                          encoding="utf-8")
        phases_root = planning / "phases"
        for phase in MILESTONE_PHASES:
            slug = ("terminal-milestone-metadata-coherence"
                    if phase == 41 else "example")
            phase_dir = phases_root / f"{phase:02d}-{slug}"
            phase_dir.mkdir(parents=True)
            for plan in range(1, PLAN_COUNTS[phase] + 1):
                prefix = f"{phase:02d}-{plan:02d}"
                (phase_dir / f"{prefix}-PLAN.md").write_text(
                    "---\nphase: fixture\n---\n", encoding="utf-8")
                (phase_dir / f"{prefix}-SUMMARY.md").write_text(
                    "---\ngenerated_at: 2026-08-01T18:00:00Z\n---\n",
                    encoding="utf-8",
                )
            (phase_dir / f"{phase:02d}-VALIDATION.md").write_text(
                self.validation_text(phase), encoding="utf-8")
        verification = phases_root / (
            "41-terminal-milestone-metadata-coherence/41-VERIFICATION.md")
        verification.write_text(
            "---\nverified: 2026-08-01T19:00:00Z\nstatus: passed\n---\n",
            encoding="utf-8",
        )

    def requirements_text(self) -> str:
        checklist = "\n".join(
            f"- [x] **{identity}**: {semantic}"
            for identity, (_, semantic) in CANONICAL_REQUIREMENTS.items())
        traceability = "\n".join(
            f"| {identity} | Phase {phase} | Complete |"
            for identity, (phase, _) in CANONICAL_REQUIREMENTS.items())
        return f"""# Requirements

{checklist}

## Traceability

| Requirement | Phase | Status |
| --- | --- | --- |
{traceability}

**Coverage:**

- v1.3 requirements: 16 total
- Mapped to phases: 16
- Behavior-evidenced complete: 16/16
- Phase 41 terminal-projection ownership rows complete: 7/16
- Unmapped: 0
- Duplicate mappings: 0
"""

    def roadmap_text(self) -> str:
        lifecycle = "\n".join(f"- [x] **Phase {phase}: Example** - complete."
                              for phase in MILESTONE_PHASES)
        details = []
        for phase in MILESTONE_PHASES:
            plans = "\n".join(f"- [x] {phase:02d}-{plan:02d}-PLAN.md"
                              for plan in range(1, PLAN_COUNTS[phase] + 1))
            details.append(f"""### Phase {phase}: Example
**Plans**: {PLAN_COUNTS[phase]}/{PLAN_COUNTS[phase]} plans complete
Plans:
{plans}
""")
        traceability = "\n".join(
            f"| {identity} | Phase {phase} | Complete |"
            for identity, (phase, _) in CANONICAL_REQUIREMENTS.items())
        progress = "\n".join(
            f"| {phase}. Example | v1.3 | {PLAN_COUNTS[phase]}/{PLAN_COUNTS[phase]} | Complete | 2026-08-01 |"
            for phase in MILESTONE_PHASES)
        return f"""# Roadmap

## Milestones

- **v1.3 Cutover Approval and Reference Demotion Trial** - Phases 31-41, complete 2026-08-01.

## Phases

{lifecycle}

## Phase Details

{''.join(details)}
## Requirement Coverage

| Requirement | Phase | Status |
| --- | --- | --- |
{traceability}

## Progress

**Execution Order:**
`38 -> 39`, `38 -> 40`, then `39 + 40 -> 41`.

| Phase | Milestone | Plans Complete | Status | Completed |
| --- | --- | --- | --- | --- |
{progress}
"""

    def state_text(self) -> str:
        total_plans = sum(PLAN_COUNTS.values())
        return f"""---
status: complete
progress:
  total_phases: 11
  completed_phases: 11
  total_plans: {total_plans}
  completed_plans: {total_plans}
---

Milestone: v1.3 Cutover Approval and Reference Demotion Trial - complete
Phase: 41 (terminal-milestone-metadata-coherence) — COMPLETE
Plan: 4 of 4
"""

    def validation_text(self, phase: int) -> str:
        rows = "\n".join(f"| {identity} | green |"
                         for identity in EXPECTED_VALIDATION_IDENTITIES[phase])
        identity_header = "Campaign" if phase == 40 else "Task ID"
        return f"""---
status: complete
nyquist_compliant: true
wave_0_complete: true
---

## {'Per-Campaign' if phase == 40 else 'Per-Task'} Verification Map

| {identity_header} | Status |
| --- | --- |
{rows}

## Validation Sign-Off

- [x] complete
"""

    def audit_text(self) -> str:
        flow_names = (
            "Four-stream intake to canonical blocker register",
            "Typed maintainer decisions to readiness ledger",
            "Complete approved path",
            "Default and targeted-repair paths",
            "Source/publication fault replacement",
            "Terminal metadata reconciliation",
            "Audit and Nyquist handoff",
        )
        flow_rows = "\n".join(f"| {flow} | complete | evidence |"
                              for flow in flow_names)
        nyquist_rows = "\n".join(f"| {phase} | compliant |"
                                 for phase in MILESTONE_PHASES)
        return f"""---
audited: 2026-08-01T20:00:00Z
status: passed
scores:
  requirements: "16/16 coherent"
  phases: "11/11 evaluated"
  integration: "15/15 connected; 0 gaps"
  flows: "7/7 complete; 0 gaps"
integration_checker:
  status: passed
  integration_score: "15 connected / 0 partial / 0 broken"
  flow_score: "7 complete / 0 partial / 0 broken"
  runtime_safety_gaps: 0
  metadata_gaps: 0
  archival_blockers: 0
nyquist:
  compliant_phases: [31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]
  partial_phases: []
  missing_phases: []
  overall: compliant
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

    def assert_isolated_mutation(self, relative_path: str, old: str, new: str,
                                 expected_code: str) -> None:
        # Arrange
        root = self.make_root()
        baseline = evaluate_terminal_consistency(load_snapshot(root),
                                                 "pre-archive")
        target = root / relative_path
        original = target.read_text(encoding="utf-8")
        self.assertEqual(original.count(old), 1)
        target.write_text(original.replace(old, new), encoding="utf-8")

        # Act
        mutated = evaluate_terminal_consistency(load_snapshot(root),
                                                "pre-archive")

        # Assert
        self.assertEqual(baseline, ())
        self.assertNotEqual(mutated, baseline)
        added = set(mutated) - set(baseline)
        self.assertIn(expected_code, {violation.code for violation in added})

    def test_requirements_total_mutation_changes_output(self) -> None:
        self.assert_isolated_mutation(".planning/REQUIREMENTS.md",
                                      "v1.3 requirements: 16 total",
                                      "v1.3 requirements: 15 total",
                                      "P41_REQUIREMENTS_COVERAGE_TOTAL")

    def test_phase41_progress_mutation_changes_output(self) -> None:
        self.assert_isolated_mutation(
            ".planning/ROADMAP.md", "| 41. Example | v1.3 | 4/4 | Complete |",
            "| 41. Example | v1.3 | 3/4 | In Progress |",
            "P41_ROADMAP_PROGRESS_PHASE_41")

    def test_execution_edge_mutation_changes_output(self) -> None:
        self.assert_isolated_mutation(".planning/ROADMAP.md", "`38 -> 39`",
                                      "`39 -> 38`",
                                      "P41_ROADMAP_EXECUTION_PROJECTION")

    def test_audit_score_mutation_changes_output(self) -> None:
        self.assert_isolated_mutation(".planning/v1.3-MILESTONE-AUDIT.md",
                                      'requirements: "16/16 coherent"',
                                      'requirements: "15/16 coherent"',
                                      "P41_AUDIT_SCORE_REQUIREMENTS")

    def test_audit_integration_mutation_changes_output(self) -> None:
        self.assert_isolated_mutation(
            ".planning/v1.3-MILESTONE-AUDIT.md",
            'integration_score: "15 connected / 0 partial / 0 broken"',
            'integration_score: "14 connected / 1 partial / 0 broken"',
            "P41_AUDIT_INTEGRATION_PROJECTION")

    def test_audit_nyquist_mutation_changes_output(self) -> None:
        self.assert_isolated_mutation(".planning/v1.3-MILESTONE-AUDIT.md",
                                      "partial_phases: []",
                                      "partial_phases: [41]",
                                      "P41_AUDIT_NYQUIST_PROJECTION")

    def test_missing_or_duplicate_projection_boundaries_fail_closed(
            self) -> None:
        # Arrange / Act / Assert
        root = self.make_root()
        cases = (
            ("requirements", parse_requirements_coverage,
             self.requirements_text().replace("**Coverage:**", "**Other:**")),
            ("progress", parse_roadmap_progress,
             self.roadmap_text() + "\n## Progress\n\ncontradiction\n"),
            ("audit", parse_audit_frontmatter, self.audit_text().replace(
                "  requirements:", "  REQUIREMENTS: bad\n  requirements:")),
        )
        for name, parser_fn, text in cases:
            with self.subTest(name=name):
                parser = BoundaryParser(root)
                projection = parser_fn(parser, text)
                self.assertIsNone(projection)
                self.assertTrue(parser.violations)

    def test_malformed_projection_shapes_fail_closed(self) -> None:
        # Arrange / Act / Assert
        root = self.make_root()
        cases = (
            ("requirements", parse_requirements_coverage,
             self.requirements_text().replace("Mapped to phases: 16",
                                              "Mapped to phases: sixteen")),
            ("progress", parse_roadmap_progress,
             self.roadmap_text().replace("| 41. Example | v1.3 | 4/4 |",
                                         "| 41. Example | v1.3 | four |")),
            ("audit", parse_audit_frontmatter,
             self.audit_text().replace("  partial_phases: []",
                                       "   partial_phases: []")),
        )
        for name, parser_fn, text in cases:
            with self.subTest(name=name):
                parser = BoundaryParser(root)
                projection = parser_fn(parser, text)
                self.assertIsNone(projection)
                self.assertTrue(parser.violations)


if __name__ == "__main__":
    unittest.main()
