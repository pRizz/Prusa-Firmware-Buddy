#!/usr/bin/env python3
from __future__ import annotations

import unittest
from dataclasses import replace

from phase41_terminal_consistency_policy import (
    CANONICAL_REQUIREMENTS,
    INVOCATION_ERROR_EXIT_CODE,
    MILESTONE_PHASES,
    AuditRecord,
    MilestoneProjection,
    PhaseLifecycle,
    PlanInventory,
    RequirementRecord,
    TerminalSnapshot,
    ValidationRecord,
    evaluate_terminal_consistency,
    exit_code_for_violations,
)

PLAN_COUNTS = {
    31: 1,
    32: 1,
    33: 1,
    34: 2,
    35: 2,
    36: 2,
    37: 2,
    38: 3,
    39: 1,
    40: 18,
    41: 3,
}


def plan_names(phase: int) -> tuple[str, ...]:
    return tuple(f"{phase:02d}-{plan:02d}-PLAN.md"
                 for plan in range(1, PLAN_COUNTS[phase] + 1))


def summary_names(phase: int) -> tuple[str, ...]:
    return tuple(
        name.replace("-PLAN.md", "-SUMMARY.md") for name in plan_names(phase))


def coherent_snapshot() -> TerminalSnapshot:
    requirements = tuple(
        RequirementRecord(
            requirement_id=requirement_id,
            semantic_text=semantic_text,
            checklist_count=1,
            checked=True,
            requirements_phase=phase,
            requirements_status="Complete",
            roadmap_phase=phase,
            roadmap_status="Complete",
        )
        for requirement_id, (phase,
                             semantic_text) in CANONICAL_REQUIREMENTS.items())
    phases = tuple(
        PhaseLifecycle(
            phase=phase,
            directory_present=True,
            roadmap_listed=True,
            roadmap_status="Complete",
        ) for phase in MILESTONE_PHASES)
    inventories = tuple(
        PlanInventory(
            phase=phase,
            plans=plan_names(phase),
            summaries=summary_names(phase),
            roadmap_plans=plan_names(phase),
            roadmap_completed=PLAN_COUNTS[phase],
            roadmap_total=PLAN_COUNTS[phase],
        ) for phase in MILESTONE_PHASES)
    validations = tuple(
        ValidationRecord(
            phase=phase,
            path=
            f".planning/phases/{phase:02d}-example/{phase:02d}-VALIDATION.md",
            present=True,
            parsed=True,
            nyquist_compliant=True,
            wave_0_complete=True,
            task_statuses=("green", ),
            signoff_complete=True,
        ) for phase in MILESTONE_PHASES)
    total_plans = sum(PLAN_COUNTS.values())
    milestone = MilestoneProjection(
        roadmap_status="Complete",
        roadmap_total_phases=len(MILESTONE_PHASES),
        roadmap_completed_phases=len(MILESTONE_PHASES),
        roadmap_total_plans=total_plans,
        roadmap_completed_plans=total_plans,
        state_status="complete",
        state_milestone_status="complete",
        state_total_phases=len(MILESTONE_PHASES),
        state_completed_phases=len(MILESTONE_PHASES),
        state_total_plans=total_plans,
        state_completed_plans=total_plans,
        state_current_phase=41,
        state_current_plan=3,
        state_narrative_terminal=True,
    )
    audit = AuditRecord(
        path=".planning/v1.3-MILESTONE-AUDIT.md",
        present=True,
        parsed=True,
        status="passed",
        fresh=True,
        phase_numbers=MILESTONE_PHASES,
        requirement_count=len(CANONICAL_REQUIREMENTS),
        coherent_requirement_count=len(CANONICAL_REQUIREMENTS),
        integration_gaps=0,
        flow_gaps=0,
        metadata_gaps=0,
        nyquist_gaps=0,
    )
    return TerminalSnapshot(requirements, phases, inventories, validations,
                            milestone, audit)


def active_pre_audit_snapshot() -> TerminalSnapshot:
    snapshot = coherent_snapshot()
    phase_index = MILESTONE_PHASES.index(41)
    phase = replace(snapshot.phases[phase_index], roadmap_status="Planned")
    inventory = replace(
        snapshot.inventories[phase_index],
        summaries=("41-01-SUMMARY.md", ),
        roadmap_completed=1,
    )
    completed_plans = sum(PLAN_COUNTS.values()) - 2
    milestone = replace(
        snapshot.milestone,
        roadmap_status="Active",
        roadmap_completed_phases=len(MILESTONE_PHASES) - 1,
        roadmap_completed_plans=completed_plans,
        state_status="executing",
        state_milestone_status="active",
        state_completed_phases=len(MILESTONE_PHASES) - 1,
        state_completed_plans=completed_plans,
        state_current_plan=2,
        state_narrative_terminal=False,
    )
    return replace(
        snapshot,
        phases=replace_at(snapshot.phases, phase_index, phase),
        inventories=replace_at(snapshot.inventories, phase_index, inventory),
        milestone=milestone,
    )


def replace_at(values: tuple[object, ...], index: int,
               replacement: object) -> tuple[object, ...]:
    return (*values[:index], replacement, *values[index + 1:])


class Phase41TerminalConsistencyTest(unittest.TestCase):

    def assert_has_code(self, snapshot: TerminalSnapshot, mode: str,
                        code: str) -> None:
        violations = evaluate_terminal_consistency(snapshot, mode)
        self.assertIn(code, {violation.code for violation in violations})

    def test_coherent_snapshot_passes_both_modes(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()

        # Act
        pre_audit = evaluate_terminal_consistency(snapshot, "pre-audit")
        pre_archive = evaluate_terminal_consistency(snapshot, "pre-archive")

        # Assert
        self.assertEqual(pre_audit, ())
        self.assertEqual(pre_archive, ())

    def test_active_phase41_snapshot_passes_pre_audit(self) -> None:
        # Arrange
        snapshot = active_pre_audit_snapshot()

        # Act
        violations = evaluate_terminal_consistency(snapshot, "pre-audit")

        # Assert
        self.assertEqual(violations, ())

    def test_active_phase41_snapshot_fails_pre_archive(self) -> None:
        # Arrange
        snapshot = active_pre_audit_snapshot()

        # Act
        violations = evaluate_terminal_consistency(snapshot, "pre-archive")
        codes = {violation.code for violation in violations}

        # Assert
        self.assertIn("P41_PHASE_STATUS", codes)
        self.assertIn("P41_PLAN_WITHOUT_SUMMARY", codes)
        self.assertIn("P41_MILESTONE_PROJECTION", codes)

    def test_missing_requirement_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        mutated = replace(snapshot, requirements=snapshot.requirements[1:])

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_REQUIREMENT_MISSING")

    def test_duplicate_requirement_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        mutated = replace(snapshot,
                          requirements=(*snapshot.requirements,
                                        snapshot.requirements[0]))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_REQUIREMENT_DUPLICATE")

    def test_extra_requirement_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        extra = replace(snapshot.requirements[0], requirement_id="EXTRA-01")
        mutated = replace(snapshot,
                          requirements=(*snapshot.requirements, extra))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_REQUIREMENT_EXTRA")

    def test_unchecked_requirement_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        record = replace(snapshot.requirements[0], checked=False)
        mutated = replace(snapshot,
                          requirements=replace_at(snapshot.requirements, 0,
                                                  record))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_REQUIREMENT_UNCHECKED")

    def test_non_complete_requirement_projection_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        record = replace(snapshot.requirements[0],
                         requirements_status="Pending")
        mutated = replace(snapshot,
                          requirements=replace_at(snapshot.requirements, 0,
                                                  record))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_REQUIREMENT_STATUS")

    def test_changed_requirement_semantics_fail_without_echoing_payload(
            self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        sensitive_payload = "private key token certificate raw crash dump"
        record = replace(snapshot.requirements[0],
                         semantic_text=sensitive_payload)
        mutated = replace(snapshot,
                          requirements=replace_at(snapshot.requirements, 0,
                                                  record))

        # Act
        violations = evaluate_terminal_consistency(mutated, "pre-audit")
        rendered = "\n".join(str(violation) for violation in violations)

        # Assert
        self.assertIn("P41_REQUIREMENT_SEMANTICS", rendered)
        self.assertNotIn(sensitive_payload, rendered)

    def test_wrong_requirement_owner_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        record = replace(snapshot.requirements[0], requirements_phase=39)
        mutated = replace(snapshot,
                          requirements=replace_at(snapshot.requirements, 0,
                                                  record))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_REQUIREMENT_OWNER")

    def test_roadmap_disk_phase_mismatch_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        phase = replace(snapshot.phases[0], roadmap_listed=False)
        mutated = replace(snapshot,
                          phases=replace_at(snapshot.phases, 0, phase))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_PHASE_PROJECTION")

    def test_wrong_milestone_phase_count_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        milestone = replace(snapshot.milestone, roadmap_total_phases=10)
        mutated = replace(snapshot, milestone=milestone)

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_MILESTONE_PROJECTION")

    def test_wrong_milestone_plan_count_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        milestone = replace(snapshot.milestone, state_total_plans=35)
        mutated = replace(snapshot, milestone=milestone)

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_MILESTONE_PROJECTION")

    def test_count_only_inventory_spoofing_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        inventory = snapshot.inventories[5]
        spoofed = replace(inventory,
                          roadmap_plans=("36-99-PLAN.md",
                                         inventory.roadmap_plans[1]))
        mutated = replace(snapshot,
                          inventories=replace_at(snapshot.inventories, 5,
                                                 spoofed))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_INVENTORY_IDENTITY")

    def test_plan_without_summary_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        inventory = replace(snapshot.inventories[0], summaries=())
        mutated = replace(snapshot,
                          inventories=replace_at(snapshot.inventories, 0,
                                                 inventory))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_PLAN_WITHOUT_SUMMARY")

    def test_summary_without_plan_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        inventory = snapshot.inventories[0]
        extra = (*inventory.summaries, "31-99-SUMMARY.md")
        mutated_inventory = replace(inventory, summaries=extra)
        mutated = replace(snapshot,
                          inventories=replace_at(snapshot.inventories, 0,
                                                 mutated_inventory))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_SUMMARY_WITHOUT_PLAN")

    def test_state_counter_mismatch_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        milestone = replace(snapshot.milestone, state_completed_plans=35)
        mutated = replace(snapshot, milestone=milestone)

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_MILESTONE_PROJECTION")

    def test_state_narrative_mismatch_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        milestone = replace(snapshot.milestone, state_narrative_terminal=False)
        mutated = replace(snapshot, milestone=milestone)

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_MILESTONE_PROJECTION")

    def test_missing_validation_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        validation = replace(snapshot.validations[0], present=False)
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, 0,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_VALIDATION_MISSING")

    def test_malformed_validation_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        validation = replace(snapshot.validations[0], parsed=False)
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, 0,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_VALIDATION_MALFORMED")

    def test_false_nyquist_compliance_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        validation = replace(snapshot.validations[0], nyquist_compliant=False)
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, 0,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_NYQUIST_FALSE")

    def test_false_wave_zero_completion_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        validation = replace(snapshot.validations[0], wave_0_complete=False)
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, 0,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_WAVE_ZERO_FALSE")

    def test_pending_validation_tasks_follow_mode_boundary(self) -> None:
        # Arrange
        phase41_index = MILESTONE_PHASES.index(41)
        cases = (
            (coherent_snapshot(), 0, "pre-audit", ("pending", ), True),
            (active_pre_audit_snapshot(), phase41_index, "pre-audit",
             ("green", "pending"), False),
            (active_pre_audit_snapshot(), phase41_index, "pre-audit",
             ("green", "pending", "pending"), True),
            (coherent_snapshot(), phase41_index, "pre-archive",
             ("green", "pending"), True),
        )
        # Act / Assert
        for snapshot, index, mode, statuses, should_fail in cases:
            with self.subTest(phase=snapshot.validations[index].phase,
                              mode=mode,
                              statuses=statuses):
                validation = replace(snapshot.validations[index],
                                     task_statuses=statuses)
                mutated = replace(
                    snapshot,
                    validations=replace_at(snapshot.validations, index,
                                           validation),
                )
                codes = {
                    violation.code
                    for violation in evaluate_terminal_consistency(mutated,
                                                                    mode)
                }
                self.assertEqual("P41_VALIDATION_TASK_STATUS" in codes,
                                 should_fail)
    def test_red_validation_campaign_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        validation = replace(snapshot.validations[0], task_statuses=("red", ))
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, 0,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit",
                             "P41_VALIDATION_TASK_STATUS")

    def test_incomplete_validation_signoff_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        validation = replace(snapshot.validations[0], signoff_complete=False)
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, 0,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_VALIDATION_SIGNOFF")

    def test_phase37_partial_nyquist_state_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        index = MILESTONE_PHASES.index(37)
        validation = replace(snapshot.validations[index],
                             task_statuses=("pending", ))
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, index,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit",
                             "P41_VALIDATION_TASK_STATUS")

    def test_phase38_partial_nyquist_state_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        index = MILESTONE_PHASES.index(38)
        validation = replace(snapshot.validations[index],
                             task_statuses=("pending", ))
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, index,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit",
                             "P41_VALIDATION_TASK_STATUS")

    def test_phase40_partial_nyquist_state_fails_closed(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        index = MILESTONE_PHASES.index(40)
        validation = replace(snapshot.validations[index],
                             wave_0_complete=False)
        mutated = replace(snapshot,
                          validations=replace_at(snapshot.validations, index,
                                                 validation))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_WAVE_ZERO_FALSE")

    def test_malformed_audit_fails_closed_in_pre_audit(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        mutated = replace(snapshot,
                          audit=replace(snapshot.audit, parsed=False))

        # Act / Assert
        self.assert_has_code(mutated, "pre-audit", "P41_AUDIT_MALFORMED")

    def test_stale_audit_fails_closed_in_pre_archive(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        mutated = replace(snapshot, audit=replace(snapshot.audit, fresh=False))

        # Act / Assert
        self.assert_has_code(mutated, "pre-archive", "P41_AUDIT_STALE")

    def test_pre_archive_requires_phases_31_through_41(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        audit = replace(snapshot.audit, phase_numbers=MILESTONE_PHASES[:-1])
        mutated = replace(snapshot, audit=audit)

        # Act / Assert
        self.assert_has_code(mutated, "pre-archive", "P41_AUDIT_PHASE_SCOPE")

    def test_pre_archive_requires_sixteen_coherent_requirements(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        audit = replace(snapshot.audit, coherent_requirement_count=15)
        mutated = replace(snapshot, audit=audit)

        # Act / Assert
        self.assert_has_code(mutated, "pre-archive",
                             "P41_AUDIT_REQUIREMENT_COHERENCE")

    def test_pre_archive_requires_zero_integration_gaps(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        audit = replace(snapshot.audit, integration_gaps=1)
        mutated = replace(snapshot, audit=audit)

        # Act / Assert
        self.assert_has_code(mutated, "pre-archive",
                             "P41_AUDIT_INTEGRATION_GAPS")

    def test_pre_archive_requires_zero_flow_gaps(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        audit = replace(snapshot.audit, flow_gaps=1)
        mutated = replace(snapshot, audit=audit)

        # Act / Assert
        self.assert_has_code(mutated, "pre-archive", "P41_AUDIT_FLOW_GAPS")

    def test_pre_archive_requires_zero_nyquist_gaps(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        audit = replace(snapshot.audit, nyquist_gaps=1)
        mutated = replace(snapshot, audit=audit)

        # Act / Assert
        self.assert_has_code(mutated, "pre-archive", "P41_AUDIT_NYQUIST_GAPS")

    def test_audit_cannot_make_unchecked_requirement_coherent(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        requirement = replace(snapshot.requirements[0], checked=False)
        mutated = replace(snapshot,
                          requirements=replace_at(snapshot.requirements, 0,
                                                  requirement))

        # Act
        violations = evaluate_terminal_consistency(mutated, "pre-archive")

        # Assert
        self.assertIn("P41_REQUIREMENT_UNCHECKED",
                      {violation.code
                       for violation in violations})

    def test_violations_have_stable_path_code_observed_order(self) -> None:
        # Arrange
        snapshot = coherent_snapshot()
        requirement = replace(snapshot.requirements[0], checked=False)
        validation = replace(snapshot.validations[0], wave_0_complete=False)
        mutated = replace(
            snapshot,
            requirements=replace_at(snapshot.requirements, 0, requirement),
            validations=replace_at(snapshot.validations, 0, validation),
        )

        # Act
        first = evaluate_terminal_consistency(mutated, "pre-audit")
        second = evaluate_terminal_consistency(mutated, "pre-audit")

        # Assert
        self.assertEqual(first, second)
        self.assertEqual(
            list(first),
            sorted(first,
                   key=lambda item: (item.path, item.code, item.observed)))

    def test_exit_category_mapping_is_exact(self) -> None:
        # Arrange
        coherent = evaluate_terminal_consistency(coherent_snapshot(),
                                                 "pre-audit")
        broken = evaluate_terminal_consistency(
            replace(coherent_snapshot(),
                    audit=replace(coherent_snapshot().audit, parsed=False)),
            "pre-audit",
        )

        # Act
        success_code = exit_code_for_violations(coherent)
        violation_code = exit_code_for_violations(broken)

        # Assert
        self.assertEqual(success_code, 0)
        self.assertEqual(violation_code, 1)
        self.assertEqual(INVOCATION_ERROR_EXIT_CODE, 2)


if __name__ == "__main__":
    unittest.main()
