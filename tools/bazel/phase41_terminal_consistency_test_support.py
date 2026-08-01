from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from phase41_terminal_consistency_policy import (
    CANONICAL_REQUIREMENTS,
    EXPECTED_ROADMAP_EXECUTION_EDGES,
    EXPECTED_VALIDATION_IDENTITIES,
    MILESTONE_PHASES,
    AuditFrontmatterProjection,
    AuditRecord,
    MilestoneProjection,
    PhaseLifecycle,
    PlanInventory,
    RequirementRecord,
    RequirementsCoverageProjection,
    RoadmapProgressProjection,
    RoadmapProgressRow,
    TerminalSnapshot,
    ValidationRecord,
    VerificationRecord,
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
    41: 4,
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
            task_identities=EXPECTED_VALIDATION_IDENTITIES[phase],
            task_statuses=("green", ) *
            len(EXPECTED_VALIDATION_IDENTITIES[phase]),
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
        state_current_plan=4,
        state_narrative_terminal=True,
    )
    audited_at = datetime(2026, 8, 1, 18, tzinfo=timezone.utc)
    audit = AuditRecord(
        path=".planning/v1.3-MILESTONE-AUDIT.md",
        present=True,
        parsed=True,
        status="passed",
        fresh=True,
        audited_at=audited_at,
        phase_numbers=MILESTONE_PHASES,
        requirement_count=len(CANONICAL_REQUIREMENTS),
        coherent_requirement_count=len(CANONICAL_REQUIREMENTS),
        integration_gaps=0,
        flow_gaps=0,
        metadata_gaps=0,
        nyquist_gaps=0,
        reported_nyquist_gaps=0,
        archival_blockers=0,
        frontmatter_projection=coherent_audit_projection(),
    )
    verification = VerificationRecord(
        path=(".planning/phases/41-terminal-milestone-metadata-coherence/"
              "41-VERIFICATION.md"),
        present=True,
        parsed=True,
        status="passed",
        fresh=True,
        verified_at=datetime(2026, 8, 1, 17, tzinfo=timezone.utc),
    )
    requirements_coverage = RequirementsCoverageProjection(
        total_requirements=16,
        mapped_requirements=16,
        behavior_evidenced_complete=16,
        behavior_evidenced_total=16,
        phase41_owned=7,
        phase41_ownership_total=16,
        phase41_ownership_state="complete",
        unmapped=0,
        duplicate_mappings=0,
    )
    roadmap_progress = coherent_roadmap_progress(inventories)
    return TerminalSnapshot(
        requirements,
        phases,
        inventories,
        validations,
        milestone,
        audit,
        verification,
        requirements_coverage=requirements_coverage,
        roadmap_progress=roadmap_progress,
    )


def active_pre_audit_snapshot() -> TerminalSnapshot:
    snapshot = coherent_snapshot()
    phase_index = MILESTONE_PHASES.index(41)
    phase = replace(snapshot.phases[phase_index], roadmap_status="Planned")
    inventory = replace(
        snapshot.inventories[phase_index],
        summaries=summary_names(41)[:-1],
        roadmap_completed=PLAN_COUNTS[41] - 1,
    )
    completed_plans = sum(PLAN_COUNTS.values()) - 1
    milestone = replace(
        snapshot.milestone,
        roadmap_status="Active",
        roadmap_completed_phases=len(MILESTONE_PHASES) - 1,
        roadmap_completed_plans=completed_plans,
        state_status="executing",
        state_milestone_status="active",
        state_completed_phases=len(MILESTONE_PHASES) - 1,
        state_completed_plans=completed_plans,
        state_current_plan=4,
        state_narrative_terminal=False,
    )
    progress_rows = (*snapshot.roadmap_progress.rows[:-1],
                     RoadmapProgressRow(41, 3, 4, "In Progress"))
    roadmap_progress = replace(
        snapshot.roadmap_progress,
        rows=progress_rows,
        milestone_completed_phases=10,
        milestone_completed_plans=completed_plans,
        milestone_status="Active",
    )
    requirements_coverage = replace(
        snapshot.requirements_coverage,
        phase41_ownership_state="pending",
    )
    return replace(
        snapshot,
        phases=replace_at(snapshot.phases, phase_index, phase),
        inventories=replace_at(snapshot.inventories, phase_index, inventory),
        milestone=milestone,
        requirements_coverage=requirements_coverage,
        roadmap_progress=roadmap_progress,
        verification=replace(snapshot.verification,
                             present=False,
                             parsed=False,
                             status="missing",
                             fresh=False,
                             verified_at=None),
    )


def coherent_audit_projection() -> AuditFrontmatterProjection:
    return AuditFrontmatterProjection(
        scores_requirements="16/16 coherent",
        scores_phases="11/11 evaluated",
        scores_integration="15/15 connected; 0 gaps",
        scores_flows="7/7 complete; 0 gaps",
        integration_status="passed",
        integration_connected=15,
        integration_partial=0,
        integration_broken=0,
        flow_complete=7,
        flow_partial=0,
        flow_broken=0,
        runtime_safety_gaps=0,
        metadata_gaps=0,
        archival_blockers=0,
        compliant_phases=MILESTONE_PHASES,
        partial_phases=(),
        missing_phases=(),
        nyquist_overall="compliant",
    )


def coherent_roadmap_progress(
    inventories: tuple[PlanInventory, ...], ) -> RoadmapProgressProjection:
    rows = tuple(
        RoadmapProgressRow(record.phase, len(record.summaries),
                           len(record.plans), "Complete")
        for record in inventories)
    total_plans = sum(len(record.plans) for record in inventories)
    return RoadmapProgressProjection(
        rows=rows,
        execution_edges=EXPECTED_ROADMAP_EXECUTION_EDGES,
        milestone_completed_phases=len(MILESTONE_PHASES),
        milestone_total_phases=len(MILESTONE_PHASES),
        milestone_completed_plans=total_plans,
        milestone_total_plans=total_plans,
        milestone_status="Complete",
    )


def replace_at(values: tuple[object, ...], index: int,
               replacement: object) -> tuple[object, ...]:
    return (*values[:index], replacement, *values[index + 1:])
