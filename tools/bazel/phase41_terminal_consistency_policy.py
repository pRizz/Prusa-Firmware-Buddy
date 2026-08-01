#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from enum import Enum

from phase41_terminal_consistency_contracts import (
    CANONICAL_REQUIREMENTS,
    EXPECTED_AUDIT_FLOW_COMPLETE,
    EXPECTED_AUDIT_INTEGRATION_CONNECTED,
    EXPECTED_ROADMAP_EXECUTION_EDGES,
    EXPECTED_VALIDATION_IDENTITIES,
    INVOCATION_ERROR_EXIT_CODE,
    MILESTONE_PHASES,
    REPOSITORY_VIOLATION_EXIT_CODE,
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
    Violation,
    bounded,
    exit_code_for_violations,
    normalize_semantic_text,
    semantic_digest,
)


class ConsistencyMode(str, Enum):
    PRE_AUDIT = "pre-audit"
    PRE_ARCHIVE = "pre-archive"


def _violation(
    path: str,
    code: str,
    observed: object,
    expected: object,
) -> Violation:
    return Violation(path, code, bounded(observed), bounded(expected))


def _terminal_active(snapshot: TerminalSnapshot,
                     mode: ConsistencyMode) -> bool:
    if mode is not ConsistencyMode.PRE_AUDIT:
        return False
    terminal_phase = MILESTONE_PHASES[-1]
    maybe_inventory = next(
        (record
         for record in snapshot.inventories if record.phase == terminal_phase),
        None)
    has_incomplete_inventory = (maybe_inventory is not None and len(
        maybe_inventory.summaries) < len(maybe_inventory.plans))
    has_active_phase = any(
        record.phase == terminal_phase and record.roadmap_status == "Planned"
        for record in snapshot.phases)
    return has_incomplete_inventory or has_active_phase


def _evaluate_requirements(snapshot: TerminalSnapshot) -> list[Violation]:
    path = ".planning/REQUIREMENTS.md"
    violations: list[Violation] = []
    counts = Counter(record.requirement_id for record in snapshot.requirements)
    expected_ids = set(CANONICAL_REQUIREMENTS)
    observed_ids = set(counts)

    for requirement_id in sorted(expected_ids - observed_ids):
        violations.append(
            _violation(path, "P41_REQUIREMENT_MISSING", requirement_id,
                       "exactly one canonical row"))
    for requirement_id in sorted(observed_ids - expected_ids):
        violations.append(
            _violation(path, "P41_REQUIREMENT_EXTRA", requirement_id,
                       "no extra requirement IDs"))
    for requirement_id, count in sorted(counts.items()):
        if count != 1:
            violations.append(
                _violation(path, "P41_REQUIREMENT_DUPLICATE",
                           f"{requirement_id}:{count}", "one row"))

    for record in snapshot.requirements:
        canonical = CANONICAL_REQUIREMENTS.get(record.requirement_id)
        if canonical is None:
            continue
        expected_phase, expected_semantic = canonical
        if record.checklist_count != 1:
            violations.append(
                _violation(
                    path, "P41_REQUIREMENT_CHECKLIST_COUNT",
                    f"{record.requirement_id}:{record.checklist_count}",
                    "one checklist row"))
        if not record.checked:
            violations.append(
                _violation(path, "P41_REQUIREMENT_UNCHECKED",
                           record.requirement_id, "checked"))
        if record.requirements_status != "Complete":
            violations.append(
                _violation(
                    path, "P41_REQUIREMENT_STATUS",
                    f"{record.requirement_id}:{record.requirements_status}",
                    "Complete"))
        if record.roadmap_status != "Complete":
            violations.append(
                _violation(".planning/ROADMAP.md",
                           "P41_ROADMAP_REQUIREMENT_STATUS",
                           f"{record.requirement_id}:{record.roadmap_status}",
                           "Complete"))
        if record.requirements_phase != expected_phase:
            violations.append(
                _violation(
                    path, "P41_REQUIREMENT_OWNER",
                    f"{record.requirement_id}:Phase {record.requirements_phase}",
                    f"Phase {expected_phase}"))
        if record.roadmap_phase != expected_phase:
            violations.append(
                _violation(
                    ".planning/ROADMAP.md", "P41_ROADMAP_REQUIREMENT_OWNER",
                    f"{record.requirement_id}:Phase {record.roadmap_phase}",
                    f"Phase {expected_phase}"))
        if normalize_semantic_text(
                record.semantic_text) != normalize_semantic_text(
                    expected_semantic):
            violations.append(
                _violation(
                    path, "P41_REQUIREMENT_SEMANTICS",
                    f"{record.requirement_id}:sha256={semantic_digest(record.semantic_text)}",
                    f"sha256={semantic_digest(expected_semantic)}"))
    return violations


def _evaluate_requirements_coverage(
    snapshot: TerminalSnapshot,
    mode: ConsistencyMode,
) -> list[Violation]:
    path = ".planning/REQUIREMENTS.md"
    projection = snapshot.requirements_coverage
    if projection is None:
        return [
            _violation(path, "P41_REQUIREMENTS_COVERAGE_MISSING", "missing",
                       "exact six-field coverage rollup")
        ]
    total = len(CANONICAL_REQUIREMENTS)
    phase41_owned = sum(phase == 41
                        for phase, _ in CANONICAL_REQUIREMENTS.values())
    state = "pending" if _terminal_active(snapshot, mode) else "complete"
    checks = (
        (projection.total_requirements == total,
         "P41_REQUIREMENTS_COVERAGE_TOTAL", projection.total_requirements,
         total),
        (projection.mapped_requirements == total,
         "P41_REQUIREMENTS_COVERAGE_MAPPED", projection.mapped_requirements,
         total),
        ((projection.behavior_evidenced_complete,
          projection.behavior_evidenced_total) == (total, total),
         "P41_REQUIREMENTS_COVERAGE_BEHAVIOR",
         (projection.behavior_evidenced_complete,
          projection.behavior_evidenced_total), (total, total)),
        ((projection.phase41_owned,
          projection.phase41_ownership_total) == (phase41_owned, total),
         "P41_REQUIREMENTS_COVERAGE_PHASE41_OWNERSHIP",
         (projection.phase41_owned,
          projection.phase41_ownership_total), (phase41_owned, total)),
        (projection.phase41_ownership_state == state,
         "P41_REQUIREMENTS_COVERAGE_PHASE41_STATE",
         projection.phase41_ownership_state, state),
        (projection.unmapped == 0, "P41_REQUIREMENTS_COVERAGE_UNMAPPED",
         projection.unmapped, 0),
        (projection.duplicate_mappings == 0,
         "P41_REQUIREMENTS_COVERAGE_DUPLICATE_MAPPINGS",
         projection.duplicate_mappings, 0),
    )
    return [
        _violation(path, code, observed, expected)
        for passed, code, observed, expected in checks if not passed
    ]


def _evaluate_roadmap_progress(
    snapshot: TerminalSnapshot,
    mode: ConsistencyMode,
) -> list[Violation]:
    path = ".planning/ROADMAP.md"
    projection = snapshot.roadmap_progress
    if projection is None:
        return [
            _violation(path, "P41_ROADMAP_PROGRESS_MISSING", "missing",
                       "exact Progress projection")
        ]
    active = _terminal_active(snapshot, mode)
    inventory_by_phase = {
        record.phase: record
        for record in snapshot.inventories
    }
    expected_rows = tuple(
        RoadmapProgressRow(
            phase,
            len(inventory_by_phase[phase].summaries),
            len(inventory_by_phase[phase].plans),
            "In Progress" if active and phase == 41 else "Complete",
        ) for phase in MILESTONE_PHASES if phase in inventory_by_phase)
    violations: list[Violation] = []
    if tuple(row.phase for row in projection.rows) != MILESTONE_PHASES:
        violations.append(
            _violation(path, "P41_ROADMAP_PROGRESS_PHASE_IDENTITIES",
                       tuple(row.phase for row in projection.rows),
                       MILESTONE_PHASES))
    observed_by_phase = {row.phase: row for row in projection.rows}
    for expected_row in expected_rows:
        observed = observed_by_phase.get(expected_row.phase)
        if observed != expected_row:
            violations.append(
                _violation(path,
                           f"P41_ROADMAP_PROGRESS_PHASE_{expected_row.phase}",
                           observed, expected_row))
    completed_plans = sum(
        len(record.summaries) for record in snapshot.inventories)
    total_plans = sum(len(record.plans) for record in snapshot.inventories)
    total_phases = len(MILESTONE_PHASES)
    expected_completed_phases = total_phases - 1 if active else total_phases
    checks = (
        ((projection.milestone_completed_phases,
          projection.milestone_total_phases) == (expected_completed_phases,
                                                 total_phases),
         "P41_ROADMAP_PROGRESS_MILESTONE_PHASES",
         (projection.milestone_completed_phases,
          projection.milestone_total_phases), (expected_completed_phases,
                                               total_phases)),
        ((projection.milestone_completed_plans,
          projection.milestone_total_plans) == (completed_plans, total_plans),
         "P41_ROADMAP_PROGRESS_MILESTONE_PLANS",
         (projection.milestone_completed_plans,
          projection.milestone_total_plans), (completed_plans, total_plans)),
        (projection.milestone_status == ("Active" if active else "Complete"),
         "P41_ROADMAP_PROGRESS_MILESTONE_STATUS", projection.milestone_status,
         "Active" if active else "Complete"),
        (projection.execution_edges == EXPECTED_ROADMAP_EXECUTION_EDGES,
         "P41_ROADMAP_EXECUTION_PROJECTION", projection.execution_edges,
         EXPECTED_ROADMAP_EXECUTION_EDGES),
    )
    violations.extend(
        _violation(path, code, observed, expected)
        for passed, code, observed, expected in checks if not passed)
    return violations


def _evaluate_audit_frontmatter(snapshot: TerminalSnapshot) -> list[Violation]:
    audit = snapshot.audit
    if not audit.present or not audit.parsed:
        return []
    projection = audit.frontmatter_projection
    if projection is None:
        return [
            _violation(audit.path, "P41_AUDIT_PROJECTION_MISSING", "missing",
                       "scores, integration_checker, nyquist")
        ]
    total = len(CANONICAL_REQUIREMENTS)
    score_checks = (
        (projection.scores_requirements == f"{total}/{total} coherent",
         "P41_AUDIT_SCORE_REQUIREMENTS", projection.scores_requirements,
         f"{total}/{total} coherent"),
        (projection.scores_phases == "11/11 evaluated",
         "P41_AUDIT_SCORE_PHASES", projection.scores_phases,
         "11/11 evaluated"),
        (projection.scores_integration == "15/15 connected; 0 gaps",
         "P41_AUDIT_SCORE_INTEGRATION", projection.scores_integration,
         "15/15 connected; 0 gaps"),
        (projection.scores_flows == "7/7 complete; 0 gaps",
         "P41_AUDIT_SCORE_FLOWS", projection.scores_flows,
         "7/7 complete; 0 gaps"),
    )
    integration_observed = (
        projection.integration_status,
        projection.integration_connected,
        projection.integration_partial,
        projection.integration_broken,
        projection.flow_complete,
        projection.flow_partial,
        projection.flow_broken,
        projection.runtime_safety_gaps,
        projection.metadata_gaps,
        projection.archival_blockers,
    )
    integration_expected = ("passed", EXPECTED_AUDIT_INTEGRATION_CONNECTED, 0,
                            0, EXPECTED_AUDIT_FLOW_COMPLETE, 0, 0, 0, 0, 0)
    nyquist_observed = (projection.compliant_phases, projection.partial_phases,
                        projection.missing_phases, projection.nyquist_overall)
    nyquist_expected = (MILESTONE_PHASES, (), (), "compliant")
    checks = (*score_checks, (integration_observed == integration_expected,
                              "P41_AUDIT_INTEGRATION_PROJECTION",
                              integration_observed, integration_expected),
              (nyquist_observed == nyquist_expected,
               "P41_AUDIT_NYQUIST_PROJECTION", nyquist_observed,
               nyquist_expected))
    return [
        _violation(audit.path, code, observed, expected)
        for passed, code, observed, expected in checks if not passed
    ]


def _evaluate_phases(snapshot: TerminalSnapshot,
                     mode: ConsistencyMode) -> list[Violation]:
    violations: list[Violation] = []
    counts = Counter(record.phase for record in snapshot.phases)
    observed = set(counts)
    expected = set(MILESTONE_PHASES)
    for phase in sorted(expected - observed):
        violations.append(
            _violation(".planning/phases", "P41_PHASE_MISSING", phase,
                       "phase directory and roadmap row"))
    for phase in sorted(observed - expected):
        violations.append(
            _violation(".planning/phases", "P41_PHASE_EXTRA", phase,
                       "phases 31 through 41"))
    for phase, count in sorted(counts.items()):
        if count != 1:
            violations.append(
                _violation(".planning/phases", "P41_PHASE_DUPLICATE",
                           f"{phase}:{count}", "one phase record"))
    for record in snapshot.phases:
        if not record.directory_present or not record.roadmap_listed:
            violations.append(
                _violation(
                    ".planning/ROADMAP.md", "P41_PHASE_PROJECTION",
                    f"{record.phase}:disk={record.directory_present},roadmap={record.roadmap_listed}",
                    "present in both"))
        expected_statuses = (
            {"Planned", "Complete"} if mode is ConsistencyMode.PRE_AUDIT
            and record.phase == MILESTONE_PHASES[-1] else {"Complete"})
        if record.roadmap_status not in expected_statuses:
            violations.append(
                _violation(".planning/ROADMAP.md", "P41_PHASE_STATUS",
                           f"{record.phase}:{record.roadmap_status}",
                           "/".join(sorted(expected_statuses))))
    return violations


def _evaluate_inventories(snapshot: TerminalSnapshot,
                          mode: ConsistencyMode) -> list[Violation]:
    violations: list[Violation] = []
    terminal_phase = MILESTONE_PHASES[-1]
    terminal_active = _terminal_active(snapshot, mode)
    counts = Counter(record.phase for record in snapshot.inventories)
    for phase in MILESTONE_PHASES:
        count = counts.get(phase, 0)
        if count != 1:
            violations.append(
                _violation(".planning/ROADMAP.md",
                           "P41_INVENTORY_RECORD_COUNT", f"{phase}:{count}",
                           "one inventory record"))
    for inventory in snapshot.inventories:
        path = f".planning/phases/{inventory.phase}"
        plans = set(inventory.plans)
        summaries = set(inventory.summaries)
        roadmap_plans = set(inventory.roadmap_plans)
        plan_prefix = f"{inventory.phase:02d}-"
        for name in sorted(plans | roadmap_plans):
            if not name.startswith(plan_prefix) or not name.endswith(
                    "-PLAN.md"):
                violations.append(
                    _violation(path, "P41_PLAN_IDENTITY", name,
                               f"{plan_prefix}*-PLAN.md"))
        for name in sorted(summaries):
            if not name.startswith(plan_prefix) or not name.endswith(
                    "-SUMMARY.md"):
                violations.append(
                    _violation(path, "P41_SUMMARY_IDENTITY", name,
                               f"{plan_prefix}*-SUMMARY.md"))
        expected_summaries = {
            name.replace("-PLAN.md", "-SUMMARY.md")
            for name in plans
        }
        if plans != roadmap_plans:
            violations.append(
                _violation(".planning/ROADMAP.md", "P41_INVENTORY_IDENTITY",
                           f"Phase {inventory.phase}:{sorted(roadmap_plans)}",
                           sorted(plans)))
        if not terminal_active or inventory.phase != terminal_phase:
            for name in sorted(expected_summaries - summaries):
                violations.append(
                    _violation(path, "P41_PLAN_WITHOUT_SUMMARY", name,
                               "matching SUMMARY"))
        for name in sorted(summaries - expected_summaries):
            violations.append(
                _violation(path, "P41_SUMMARY_WITHOUT_PLAN", name,
                           "matching PLAN"))
        if inventory.roadmap_total != len(plans):
            violations.append(
                _violation(
                    ".planning/ROADMAP.md", "P41_PLAN_TOTAL",
                    f"Phase {inventory.phase}:{inventory.roadmap_total}",
                    len(plans)))
        if inventory.roadmap_completed != len(summaries):
            violations.append(
                _violation(
                    ".planning/ROADMAP.md", "P41_PLAN_COMPLETED",
                    f"Phase {inventory.phase}:{inventory.roadmap_completed}",
                    len(summaries)))
    return violations


def _evaluate_validations(
    snapshot: TerminalSnapshot,
    mode: ConsistencyMode,
) -> list[Violation]:
    violations: list[Violation] = []
    counts = Counter(record.phase for record in snapshot.validations)
    for phase in MILESTONE_PHASES:
        count = counts.get(phase, 0)
        if count != 1:
            violations.append(
                _violation(".planning/phases", "P41_VALIDATION_RECORD_COUNT",
                           f"{phase}:{count}", "one validation record"))
    for record in snapshot.validations:
        path = record.path
        if not record.present:
            violations.append(
                _violation(path, "P41_VALIDATION_MISSING", record.phase,
                           "VALIDATION.md present"))
            continue
        if not record.parsed:
            violations.append(
                _violation(path, "P41_VALIDATION_MALFORMED", record.phase,
                           "valid frontmatter and tables"))
            continue
        if not record.nyquist_compliant:
            violations.append(
                _violation(path, "P41_NYQUIST_FALSE", record.phase, "true"))
        if not record.wave_0_complete:
            violations.append(
                _violation(path, "P41_WAVE_ZERO_FALSE", record.phase, "true"))
        if (not record.task_identities
                or len(record.task_identities) != len(record.task_statuses)):
            violations.append(
                _violation(path, "P41_VALIDATION_TASKS_MISSING",
                           len(record.task_identities),
                           ">= 1 task/campaign row"))
        identity_counts = Counter(record.task_identities)
        expected_identity_counts = Counter(
            EXPECTED_VALIDATION_IDENTITIES.get(record.phase, ()))
        if identity_counts != expected_identity_counts:
            violations.append(
                _violation(
                    path,
                    "P41_VALIDATION_TASK_IDENTITIES",
                    tuple(sorted(identity_counts.items())),
                    tuple(sorted(expected_identity_counts.items())),
                ))
        for identity, count in sorted(identity_counts.items()):
            if count != 1:
                violations.append(
                    _violation(path, "P41_VALIDATION_TASK_DUPLICATE",
                               f"{identity}:{count}", "one row"))
        normalized_statuses = tuple(status.lower()
                                    for status in record.task_statuses)
        allows_in_flight_audit = (mode is ConsistencyMode.PRE_AUDIT
                                  and record.phase == 41 and
                                  normalized_statuses.count("pending") == 1)
        for status in sorted(normalized_statuses):
            status_is_green = status in {"green", "pass", "passed", "complete"}
            if status_is_green or (allows_in_flight_audit
                                   and status == "pending"):
                continue
            violations.append(
                _violation(path, "P41_VALIDATION_TASK_STATUS",
                           f"Phase {record.phase}:{status}",
                           "green/pass/passed/complete"))
        if not record.signoff_complete:
            violations.append(
                _violation(path, "P41_VALIDATION_SIGNOFF", record.phase,
                           "complete sign-off"))
    return violations


def _evaluate_milestone(snapshot: TerminalSnapshot,
                        mode: ConsistencyMode) -> list[Violation]:
    milestone = snapshot.milestone
    total_phases = len(MILESTONE_PHASES)
    total_plans = sum(
        len(inventory.plans) for inventory in snapshot.inventories)
    completed_plans = sum(
        len(inventory.summaries) for inventory in snapshot.inventories)
    terminal_phase = MILESTONE_PHASES[-1]
    active = _terminal_active(snapshot, mode)
    terminal_inventory = next((inventory for inventory in snapshot.inventories
                               if inventory.phase == terminal_phase), None)
    terminal_summary_count = len(
        terminal_inventory.summaries) if terminal_inventory else 0
    terminal_plan_count = len(
        terminal_inventory.plans) if terminal_inventory else 0
    active_plan = min(terminal_summary_count +
                      1, terminal_plan_count) if terminal_plan_count else 0
    expected = {
        "roadmap_status": "Active" if active else "Complete",
        "roadmap_total_phases": total_phases,
        "roadmap_completed_phases":
        total_phases - 1 if active else total_phases,
        "roadmap_total_plans": total_plans,
        "roadmap_completed_plans": completed_plans,
        "state_status": "executing" if active else "complete",
        "state_milestone_status": "active" if active else "complete",
        "state_total_phases": total_phases,
        "state_completed_phases": total_phases - 1 if active else total_phases,
        "state_total_plans": total_plans,
        "state_completed_plans": completed_plans,
        "state_current_phase": terminal_phase,
        "state_current_plan": active_plan if active else terminal_plan_count,
        "state_narrative_terminal": not active,
    }
    violations: list[Violation] = []
    for field, expected_value in expected.items():
        observed = getattr(milestone, field)
        if observed == expected_value:
            continue
        path = ".planning/ROADMAP.md" if field.startswith(
            "roadmap_") else ".planning/STATE.md"
        violations.append(
            _violation(path, "P41_MILESTONE_PROJECTION", f"{field}={observed}",
                       f"{field}={expected_value}"))
    return violations


def _evaluate_audit(snapshot: TerminalSnapshot,
                    mode: ConsistencyMode) -> list[Violation]:
    audit = snapshot.audit
    if not audit.present:
        if mode is ConsistencyMode.PRE_ARCHIVE:
            return [
                _violation(audit.path, "P41_AUDIT_MISSING", "missing",
                           "fresh passed audit")
            ]
        return []
    if not audit.parsed:
        return [
            _violation(audit.path, "P41_AUDIT_MALFORMED", "unparseable",
                       "valid audit frontmatter")
        ]
    if mode is ConsistencyMode.PRE_AUDIT:
        return []

    verification = snapshot.verification
    verification_checks = [
        (verification.present
         and verification.parsed, "P41_VERIFICATION_MISSING",
         f"present={verification.present},parsed={verification.parsed}",
         "present and parsed Phase 41 verification"),
    ]
    if verification.present and verification.parsed:
        verification_checks.extend([
            (verification.status == "passed", "P41_VERIFICATION_STATUS",
             verification.status, "passed"),
            (verification.verified_at
             is not None, "P41_VERIFICATION_TIMESTAMP",
             verification.verified_at, "valid verified timestamp"),
            (verification.fresh, "P41_VERIFICATION_STALE", verification.fresh,
             True),
            (verification.verified_at is not None
             and audit.audited_at is not None
             and verification.verified_at <= audit.audited_at,
             "P41_AUDIT_PREDATES_VERIFICATION",
             f"verification={verification.verified_at},audit={audit.audited_at}",
             "verification timestamp no newer than audit timestamp"),
        ])

    checks = [
        (audit.status == "passed", "P41_AUDIT_STATUS", audit.status, "passed"),
        (audit.fresh, "P41_AUDIT_STALE", audit.fresh, True),
        (audit.phase_numbers == MILESTONE_PHASES, "P41_AUDIT_PHASE_SCOPE",
         audit.phase_numbers, MILESTONE_PHASES),
        (audit.requirement_count == len(CANONICAL_REQUIREMENTS),
         "P41_AUDIT_REQUIREMENT_COUNT", audit.requirement_count,
         len(CANONICAL_REQUIREMENTS)),
        (audit.coherent_requirement_count == len(CANONICAL_REQUIREMENTS),
         "P41_AUDIT_REQUIREMENT_COHERENCE", audit.coherent_requirement_count,
         len(CANONICAL_REQUIREMENTS)),
        (audit.integration_gaps == 0, "P41_AUDIT_INTEGRATION_GAPS",
         audit.integration_gaps, 0),
        (audit.flow_gaps == 0, "P41_AUDIT_FLOW_GAPS", audit.flow_gaps, 0),
        (audit.metadata_gaps == 0, "P41_AUDIT_METADATA_GAPS",
         audit.metadata_gaps, 0),
        (audit.nyquist_gaps == 0, "P41_AUDIT_NYQUIST_GAPS", audit.nyquist_gaps,
         0),
        (audit.reported_nyquist_gaps == 0, "P41_AUDIT_NYQUIST_ROLLUP",
         audit.reported_nyquist_gaps, 0),
        (audit.archival_blockers == 0, "P41_AUDIT_ARCHIVAL_BLOCKERS",
         audit.archival_blockers, 0),
    ]
    return [
        _violation(audit.path, code, observed, expected)
        for passed, code, observed, expected in checks if not passed
    ] + [
        _violation(verification.path, code, observed, expected)
        for passed, code, observed, expected in verification_checks
        if not passed
    ]


def evaluate_terminal_consistency(
    snapshot: TerminalSnapshot,
    mode: str | ConsistencyMode,
) -> tuple[Violation, ...]:
    selected_mode = ConsistencyMode(mode)
    violations = [
        *snapshot.boundary_violations,
        *_evaluate_requirements(snapshot),
        *_evaluate_requirements_coverage(snapshot, selected_mode),
        *_evaluate_phases(snapshot, selected_mode),
        *_evaluate_inventories(snapshot, selected_mode),
        *_evaluate_validations(snapshot, selected_mode),
        *_evaluate_milestone(snapshot, selected_mode),
        *_evaluate_roadmap_progress(snapshot, selected_mode),
        *_evaluate_audit_frontmatter(snapshot),
        *_evaluate_audit(snapshot, selected_mode),
    ]
    return tuple(
        sorted(violations,
               key=lambda item: (item.path, item.code, item.observed)))
