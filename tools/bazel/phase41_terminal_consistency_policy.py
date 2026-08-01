#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from enum import Enum

MILESTONE_PHASES = tuple(range(31, 42))

CANONICAL_REQUIREMENTS = {
    "INTAKE-01": (
        41,
        "Maintainer can supply final simulator evidence packets for startup, G-code, GUI, storage, transfer, and selected failure flows using sanitized real-run inputs.",
    ),
    "INTAKE-02": (
        41,
        "Maintainer can supply final hardware/media/safety evidence packets for supported printer families, storage media, UI input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output scenarios.",
    ),
    "INTAKE-03": (
        41,
        "Maintainer can supply final live-service evidence packets for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows.",
    ),
    "INTAKE-04": (
        36,
        "Release manager can supply final release/signing/provenance evidence from real release-environment outputs without exposing private keys, tokens, certificates, service payloads, raw crash dumps, or other secret-bearing data.",
    ),
    "TRIAGE-01": (
        36,
        "Maintainer can aggregate all consumed simulator, hardware/media/safety, live-service, release/signing, upstream-result, retained-code, and readiness rows into a single blocker register.",
    ),
    "TRIAGE-02": (
        36,
        "Maintainer can classify each failed, missing, stale, malformed, redaction-failed, or exceptioned row with owner, severity, affected gate, required next action, and decision impact.",
    ),
    "TRIAGE-03": (
        32,
        "Maintainer can prove quick/default placeholder outputs, smoke fixtures, and local-only dry-run rows are rejected as final cutover proof.",
    ),
    "DECIDE-01": (
        37,
        "Maintainer can record retained-code acceptance, rejection, or approved exception decisions with residual-risk rationale and owner signoff.",
    ),
    "DECIDE-02": (
        37,
        "Maintainer can record final-readiness approval or block decisions using machine-readable inputs that consume the triaged evidence rows and approved exceptions.",
    ),
    "DECIDE-03": (
        33,
        "Maintainer can record reference-demotion approval or rejection as a separate explicit decision that cannot be inferred from green evidence alone.",
    ),
    "READY-01": (
        37,
        "Maintainer can generate a final readiness packet from real consumed evidence rows, retained-code decisions, approved exceptions, residual risks, blockers, and artifact references.",
    ),
    "READY-02": (
        41,
        "Final readiness remains blocked when required evidence is absent, failed, stale, malformed, redaction-failed, underclassified, or not covered by an explicit approved exception.",
    ),
    "READY-03": (
        41,
        "Reference-demotion dry run proves demotion remains blocked without a valid explicit demotion approval and opens only when readiness is otherwise unblocked and the approval input is valid.",
    ),
    "CUTOVER-01": (
        41,
        "Maintainer can produce a cutover decision artifact with one explicit verdict: approved, blocked, or approved with explicit exceptions.",
    ),
    "CUTOVER-02": (
        35,
        "Cutover decision artifact links every blocker, exception, residual risk, evidence packet, retained-code decision, readiness result, and demotion decision needed to audit the verdict.",
    ),
    "CUTOVER-03": (
        41,
        "Cutover decision artifact routes the next milestone to production cutover when approved, or to targeted blocker repair when blocked or approved with exceptions that require follow-up.",
    ),
}

REPOSITORY_VIOLATION_EXIT_CODE = 1
INVOCATION_ERROR_EXIT_CODE = 2


class ConsistencyMode(str, Enum):
    PRE_AUDIT = "pre-audit"
    PRE_ARCHIVE = "pre-archive"


@dataclass(frozen=True, order=True)
class Violation:
    path: str
    code: str
    observed: str
    expected: str


@dataclass(frozen=True)
class RequirementRecord:
    requirement_id: str
    semantic_text: str
    checklist_count: int
    checked: bool
    requirements_phase: int
    requirements_status: str
    roadmap_phase: int
    roadmap_status: str


@dataclass(frozen=True)
class PhaseLifecycle:
    phase: int
    directory_present: bool
    roadmap_listed: bool
    roadmap_status: str


@dataclass(frozen=True)
class PlanInventory:
    phase: int
    plans: tuple[str, ...]
    summaries: tuple[str, ...]
    roadmap_plans: tuple[str, ...]
    roadmap_completed: int
    roadmap_total: int


@dataclass(frozen=True)
class ValidationRecord:
    phase: int
    path: str
    present: bool
    parsed: bool
    nyquist_compliant: bool
    wave_0_complete: bool
    task_statuses: tuple[str, ...]
    signoff_complete: bool


@dataclass(frozen=True)
class MilestoneProjection:
    roadmap_status: str
    roadmap_total_phases: int
    roadmap_completed_phases: int
    roadmap_total_plans: int
    roadmap_completed_plans: int
    state_status: str
    state_milestone_status: str
    state_total_phases: int
    state_completed_phases: int
    state_total_plans: int
    state_completed_plans: int
    state_current_phase: int
    state_current_plan: int
    state_narrative_terminal: bool


@dataclass(frozen=True)
class AuditRecord:
    path: str
    present: bool
    parsed: bool
    status: str
    fresh: bool
    phase_numbers: tuple[int, ...]
    requirement_count: int
    coherent_requirement_count: int
    integration_gaps: int
    flow_gaps: int
    metadata_gaps: int
    nyquist_gaps: int


@dataclass(frozen=True)
class TerminalSnapshot:
    requirements: tuple[RequirementRecord, ...]
    phases: tuple[PhaseLifecycle, ...]
    inventories: tuple[PlanInventory, ...]
    validations: tuple[ValidationRecord, ...]
    milestone: MilestoneProjection
    audit: AuditRecord
    boundary_violations: tuple[Violation, ...] = ()


def normalize_semantic_text(text: str) -> str:
    return " ".join(text.split())


def semantic_digest(text: str) -> str:
    normalized = normalize_semantic_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def exit_code_for_violations(violations: tuple[Violation, ...]) -> int:
    if violations:
        return REPOSITORY_VIOLATION_EXIT_CODE
    return 0


def _bounded(value: object, limit: int = 160) -> str:
    rendered = str(value).replace("\n", " ").replace("\r", " ")
    if len(rendered) <= limit:
        return rendered
    return f"{rendered[:limit - 3]}..."


def _violation(
    path: str,
    code: str,
    observed: object,
    expected: object,
) -> Violation:
    return Violation(path, code, _bounded(observed), _bounded(expected))


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
        expected_statuses = ({"Planned", "Complete"}
                             if mode is ConsistencyMode.PRE_AUDIT
                             and record.phase == MILESTONE_PHASES[-1] else
                             {"Complete"})
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
    terminal_active = mode is ConsistencyMode.PRE_AUDIT and any(
        record.phase == terminal_phase and record.roadmap_status == "Planned"
        for record in snapshot.phases)
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


def _evaluate_validations(snapshot: TerminalSnapshot) -> list[Violation]:
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
        for status in sorted(record.task_statuses):
            if status.lower() not in {"green", "pass", "passed", "complete"}:
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
    active = mode is ConsistencyMode.PRE_AUDIT and any(
        record.phase == terminal_phase and record.roadmap_status == "Planned"
        for record in snapshot.phases)
    terminal_inventory = next(
        (inventory for inventory in snapshot.inventories
         if inventory.phase == terminal_phase), None)
    terminal_summary_count = len(
        terminal_inventory.summaries) if terminal_inventory else 0
    terminal_plan_count = len(
        terminal_inventory.plans) if terminal_inventory else 0
    active_plan = min(terminal_summary_count + 1,
                      terminal_plan_count) if terminal_plan_count else 0
    expected = {
        "roadmap_status": "Active" if active else "Complete",
        "roadmap_total_phases": total_phases,
        "roadmap_completed_phases": total_phases - 1 if active else total_phases,
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
    ]
    return [
        _violation(audit.path, code, observed, expected)
        for passed, code, observed, expected in checks if not passed
    ]


def evaluate_terminal_consistency(
    snapshot: TerminalSnapshot,
    mode: str | ConsistencyMode,
) -> tuple[Violation, ...]:
    selected_mode = ConsistencyMode(mode)
    violations = [
        *snapshot.boundary_violations,
        *_evaluate_requirements(snapshot),
        *_evaluate_phases(snapshot, selected_mode),
        *_evaluate_inventories(snapshot, selected_mode),
        *_evaluate_validations(snapshot),
        *_evaluate_milestone(snapshot, selected_mode),
        *_evaluate_audit(snapshot, selected_mode),
    ]
    return tuple(
        sorted(violations,
               key=lambda item: (item.path, item.code, item.observed)))
