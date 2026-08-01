#!/usr/bin/env python3
from __future__ import annotations

import unittest
from dataclasses import replace

from phase41_terminal_consistency_policy import (
    AuditFrontmatterProjection,
    RequirementsCoverageProjection,
    RoadmapProgressProjection,
    evaluate_terminal_consistency,
)
from phase41_terminal_consistency_test_support import (
    active_pre_audit_snapshot,
    coherent_snapshot,
)


class Phase41ProjectionPolicyTest(unittest.TestCase):

    def assert_projection_code(self,
                               snapshot,
                               code: str,
                               mode: str = "pre-audit") -> None:
        # Act
        violations = evaluate_terminal_consistency(snapshot, mode)

        # Assert
        matches = [
            violation for violation in violations if violation.code == code
        ]
        self.assertEqual(len(matches), 1)

    def test_coherent_projections_pass_both_modes(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()

        # Act
        pre_audit = evaluate_terminal_consistency(snapshot, "pre-audit")
        pre_archive = evaluate_terminal_consistency(snapshot, "pre-archive")

        # Assert
        self.assertEqual(pre_audit, ())
        self.assertEqual(pre_archive, ())

    def test_active_projection_passes_pre_audit_and_remains_nonterminal(
            self) -> None:
        # Arrange
        snapshot = active_pre_audit_snapshot()

        # Act
        pre_audit = evaluate_terminal_consistency(snapshot, "pre-audit")
        pre_archive = evaluate_terminal_consistency(snapshot, "pre-archive")

        # Assert
        self.assertEqual(pre_audit, ())
        self.assertNotEqual(pre_archive, ())

    def test_each_requirements_coverage_field_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        projection = snapshot.requirements_coverage
        self.assertIsInstance(projection, RequirementsCoverageProjection)
        cases = (
            ("total_requirements", 15, "P41_REQUIREMENTS_COVERAGE_TOTAL"),
            ("mapped_requirements", 15, "P41_REQUIREMENTS_COVERAGE_MAPPED"),
            ("behavior_evidenced_complete", 15,
             "P41_REQUIREMENTS_COVERAGE_BEHAVIOR"),
            ("behavior_evidenced_total", 15,
             "P41_REQUIREMENTS_COVERAGE_BEHAVIOR"),
            ("phase41_owned", 6,
             "P41_REQUIREMENTS_COVERAGE_PHASE41_OWNERSHIP"),
            ("phase41_ownership_total", 15,
             "P41_REQUIREMENTS_COVERAGE_PHASE41_OWNERSHIP"),
            ("phase41_ownership_state", "pending",
             "P41_REQUIREMENTS_COVERAGE_PHASE41_STATE"),
            ("unmapped", 1, "P41_REQUIREMENTS_COVERAGE_UNMAPPED"),
            ("duplicate_mappings", 1,
             "P41_REQUIREMENTS_COVERAGE_DUPLICATE_MAPPINGS"),
        )

        # Act / Assert
        for field, value, code in cases:
            with self.subTest(field=field):
                mutated_projection = replace(projection, **{field: value})
                mutated = replace(snapshot,
                                  requirements_coverage=mutated_projection)
                self.assert_projection_code(mutated, code)

    def test_active_requirements_projection_requires_pending_state(
            self) -> None:
        # Arrange
        snapshot = active_pre_audit_snapshot()
        projection = snapshot.requirements_coverage
        self.assertIsInstance(projection, RequirementsCoverageProjection)
        mutated = replace(
            snapshot,
            requirements_coverage=replace(projection,
                                          phase41_ownership_state="complete"),
        )

        # Act / Assert
        self.assert_projection_code(mutated,
                                    "P41_REQUIREMENTS_COVERAGE_PHASE41_STATE")

    def test_each_roadmap_progress_field_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        projection = snapshot.roadmap_progress
        self.assertIsInstance(projection, RoadmapProgressProjection)
        cases = (
            ("milestone_completed_phases", 10,
             "P41_ROADMAP_PROGRESS_MILESTONE_PHASES"),
            ("milestone_total_phases", 10,
             "P41_ROADMAP_PROGRESS_MILESTONE_PHASES"),
            ("milestone_completed_plans", 36,
             "P41_ROADMAP_PROGRESS_MILESTONE_PLANS"),
            ("milestone_total_plans", 36,
             "P41_ROADMAP_PROGRESS_MILESTONE_PLANS"),
            ("milestone_status", "Active",
             "P41_ROADMAP_PROGRESS_MILESTONE_STATUS"),
        )

        # Act / Assert
        for field, value, code in cases:
            with self.subTest(field=field):
                mutated_projection = replace(projection, **{field: value})
                mutated = replace(snapshot,
                                  roadmap_progress=mutated_projection)
                self.assert_projection_code(mutated, code)

    def test_phase41_progress_row_fields_fail_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        projection = snapshot.roadmap_progress
        self.assertIsInstance(projection, RoadmapProgressProjection)
        phase41_row = projection.rows[-1]
        cases = (
            ("completed_plans", phase41_row.completed_plans - 1),
            ("total_plans", phase41_row.total_plans - 1),
            ("status", "Planned"),
        )

        # Act / Assert
        for field, value in cases:
            with self.subTest(field=field):
                mutated_row = replace(phase41_row, **{field: value})
                mutated_projection = replace(
                    projection,
                    rows=(*projection.rows[:-1], mutated_row),
                )
                mutated = replace(snapshot,
                                  roadmap_progress=mutated_projection)
                self.assert_projection_code(mutated,
                                            "P41_ROADMAP_PROGRESS_PHASE_41")

    def test_execution_projection_requires_exact_edges(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        projection = snapshot.roadmap_progress
        self.assertIsInstance(projection, RoadmapProgressProjection)
        mutations = (
            projection.execution_edges[:-1],
            (*projection.execution_edges, ((41, ), 39)),
            (((39, ), 38), *projection.execution_edges[1:]),
        )

        # Act / Assert
        for edges in mutations:
            with self.subTest(edges=edges):
                mutated = replace(
                    snapshot,
                    roadmap_progress=replace(projection,
                                             execution_edges=edges),
                )
                self.assert_projection_code(
                    mutated, "P41_ROADMAP_EXECUTION_PROJECTION")

    def test_each_audit_score_field_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        projection = snapshot.audit.frontmatter_projection
        self.assertIsInstance(projection, AuditFrontmatterProjection)
        cases = (
            ("scores_requirements", "15/16 coherent",
             "P41_AUDIT_SCORE_REQUIREMENTS"),
            ("scores_phases", "10/11 evaluated", "P41_AUDIT_SCORE_PHASES"),
            ("scores_integration", "14/15 connected; 1 gaps",
             "P41_AUDIT_SCORE_INTEGRATION"),
            ("scores_flows", "6/7 complete; 1 gaps", "P41_AUDIT_SCORE_FLOWS"),
        )

        # Act / Assert
        for field, value, code in cases:
            with self.subTest(field=field):
                mutated_projection = replace(projection, **{field: value})
                mutated = replace(
                    snapshot,
                    audit=replace(snapshot.audit,
                                  frontmatter_projection=mutated_projection),
                )
                self.assert_projection_code(mutated, code)

    def test_each_integration_projection_field_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        projection = snapshot.audit.frontmatter_projection
        self.assertIsInstance(projection, AuditFrontmatterProjection)
        cases = (
            ("integration_status", "failed"),
            ("integration_connected", 14),
            ("integration_partial", 1),
            ("integration_broken", 1),
            ("flow_complete", 6),
            ("flow_partial", 1),
            ("flow_broken", 1),
            ("runtime_safety_gaps", 1),
            ("metadata_gaps", 1),
            ("archival_blockers", 1),
        )

        # Act / Assert
        for field, value in cases:
            with self.subTest(field=field):
                mutated_projection = replace(projection, **{field: value})
                mutated = replace(
                    snapshot,
                    audit=replace(snapshot.audit,
                                  frontmatter_projection=mutated_projection),
                )
                self.assert_projection_code(
                    mutated, "P41_AUDIT_INTEGRATION_PROJECTION")

    def test_each_nyquist_projection_field_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        projection = snapshot.audit.frontmatter_projection
        self.assertIsInstance(projection, AuditFrontmatterProjection)
        cases = (
            ("compliant_phases", projection.compliant_phases[:-1]),
            ("partial_phases", (41, )),
            ("missing_phases", (41, )),
            ("nyquist_overall", "partial"),
        )

        # Act / Assert
        for field, value in cases:
            with self.subTest(field=field):
                mutated_projection = replace(projection, **{field: value})
                mutated = replace(
                    snapshot,
                    audit=replace(snapshot.audit,
                                  frontmatter_projection=mutated_projection),
                )
                self.assert_projection_code(mutated,
                                            "P41_AUDIT_NYQUIST_PROJECTION")


if __name__ == "__main__":
    unittest.main()
