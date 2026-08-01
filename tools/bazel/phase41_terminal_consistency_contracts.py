#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

MILESTONE_PHASES = tuple(range(31, 42))
EXPECTED_AUDIT_INTEGRATION_CONNECTED = 15
EXPECTED_AUDIT_FLOW_COMPLETE = 7
EXPECTED_ROADMAP_EXECUTION_EDGES = (
    ((38, ), 39),
    ((38, ), 40),
    ((39, 40), 41),
)
REPOSITORY_VIOLATION_EXIT_CODE = 1
INVOCATION_ERROR_EXIT_CODE = 2

CANONICAL_REQUIREMENTS = {
    "INTAKE-01":
    (41,
     "Maintainer can supply final simulator evidence packets for startup, G-code, GUI, storage, transfer, and selected failure flows using sanitized real-run inputs."
     ),
    "INTAKE-02":
    (41,
     "Maintainer can supply final hardware/media/safety evidence packets for supported printer families, storage media, UI input, MMU, RS485, toolchanger, watchdog, thermal, motion, and safe-output scenarios."
     ),
    "INTAKE-03":
    (41,
     "Maintainer can supply final live-service evidence packets for Connect, PrusaLink/WUI, TLS, telemetry, proxy, transfer, negative-protocol, long-transfer, and crash-dump flows."
     ),
    "INTAKE-04":
    (36,
     "Release manager can supply final release/signing/provenance evidence from real release-environment outputs without exposing private keys, tokens, certificates, service payloads, raw crash dumps, or other secret-bearing data."
     ),
    "TRIAGE-01":
    (36,
     "Maintainer can aggregate all consumed simulator, hardware/media/safety, live-service, release/signing, upstream-result, retained-code, and readiness rows into a single blocker register."
     ),
    "TRIAGE-02":
    (36,
     "Maintainer can classify each failed, missing, stale, malformed, redaction-failed, or exceptioned row with owner, severity, affected gate, required next action, and decision impact."
     ),
    "TRIAGE-03":
    (32,
     "Maintainer can prove quick/default placeholder outputs, smoke fixtures, and local-only dry-run rows are rejected as final cutover proof."
     ),
    "DECIDE-01":
    (37,
     "Maintainer can record retained-code acceptance, rejection, or approved exception decisions with residual-risk rationale and owner signoff."
     ),
    "DECIDE-02":
    (37,
     "Maintainer can record final-readiness approval or block decisions using machine-readable inputs that consume the triaged evidence rows and approved exceptions."
     ),
    "DECIDE-03":
    (33,
     "Maintainer can record reference-demotion approval or rejection as a separate explicit decision that cannot be inferred from green evidence alone."
     ),
    "READY-01":
    (37,
     "Maintainer can generate a final readiness packet from real consumed evidence rows, retained-code decisions, approved exceptions, residual risks, blockers, and artifact references."
     ),
    "READY-02":
    (41,
     "Final readiness remains blocked when required evidence is absent, failed, stale, malformed, redaction-failed, underclassified, or not covered by an explicit approved exception."
     ),
    "READY-03":
    (41,
     "Reference-demotion dry run proves demotion remains blocked without a valid explicit demotion approval and opens only when readiness is otherwise unblocked and the approval input is valid."
     ),
    "CUTOVER-01":
    (41,
     "Maintainer can produce a cutover decision artifact with one explicit verdict: approved, blocked, or approved with explicit exceptions."
     ),
    "CUTOVER-02":
    (35,
     "Cutover decision artifact links every blocker, exception, residual risk, evidence packet, retained-code decision, readiness result, and demotion decision needed to audit the verdict."
     ),
    "CUTOVER-03":
    (41,
     "Cutover decision artifact routes the next milestone to production cutover when approved, or to targeted blocker repair when blocked or approved with exceptions that require follow-up."
     ),
}


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
    task_identities: tuple[str, ...]
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
class RequirementsCoverageProjection:
    total_requirements: int
    mapped_requirements: int
    behavior_evidenced_complete: int
    behavior_evidenced_total: int
    phase41_owned: int
    phase41_ownership_total: int
    phase41_ownership_state: str
    unmapped: int
    duplicate_mappings: int


@dataclass(frozen=True)
class RoadmapProgressRow:
    phase: int
    completed_plans: int
    total_plans: int
    status: str


@dataclass(frozen=True)
class RoadmapProgressProjection:
    rows: tuple[RoadmapProgressRow, ...]
    execution_edges: tuple[tuple[tuple[int, ...], int], ...]
    milestone_completed_phases: int
    milestone_total_phases: int
    milestone_completed_plans: int
    milestone_total_plans: int
    milestone_status: str


@dataclass(frozen=True)
class AuditFrontmatterProjection:
    scores_requirements: str
    scores_phases: str
    scores_integration: str
    scores_flows: str
    integration_status: str
    integration_connected: int
    integration_partial: int
    integration_broken: int
    flow_complete: int
    flow_partial: int
    flow_broken: int
    runtime_safety_gaps: int
    metadata_gaps: int
    archival_blockers: int
    compliant_phases: tuple[int, ...]
    partial_phases: tuple[int, ...]
    missing_phases: tuple[int, ...]
    nyquist_overall: str


@dataclass(frozen=True)
class AuditRecord:
    path: str
    present: bool
    parsed: bool
    status: str
    fresh: bool
    audited_at: datetime | None
    phase_numbers: tuple[int, ...]
    requirement_count: int | None
    coherent_requirement_count: int | None
    integration_gaps: int | None
    flow_gaps: int | None
    metadata_gaps: int | None
    nyquist_gaps: int | None
    reported_nyquist_gaps: int | None
    archival_blockers: int | None
    frontmatter_projection: AuditFrontmatterProjection | None = None


@dataclass(frozen=True)
class VerificationRecord:
    path: str
    present: bool
    parsed: bool
    status: str
    fresh: bool
    verified_at: datetime | None


@dataclass(frozen=True)
class TerminalSnapshot:
    requirements: tuple[RequirementRecord, ...]
    phases: tuple[PhaseLifecycle, ...]
    inventories: tuple[PlanInventory, ...]
    validations: tuple[ValidationRecord, ...]
    milestone: MilestoneProjection
    audit: AuditRecord
    verification: VerificationRecord
    requirements_coverage: RequirementsCoverageProjection | None = None
    roadmap_progress: RoadmapProgressProjection | None = None
    boundary_violations: tuple[Violation, ...] = ()


def normalize_semantic_text(text: str) -> str:
    return " ".join(text.split())


def semantic_digest(text: str) -> str:
    normalized = normalize_semantic_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def exit_code_for_violations(violations: tuple[Violation, ...]) -> int:
    return REPOSITORY_VIOLATION_EXIT_CODE if violations else 0


def bounded(value: object, limit: int = 160) -> str:
    rendered = str(value).replace("\n", " ").replace("\r", " ")
    return rendered if len(rendered) <= limit else f"{rendered[:limit - 3]}..."


# Frozen from the approved Phase 31-41 VALIDATION.md contracts. Runtime
# validation rows are observations and must never define their own expected set.
EXPECTED_VALIDATION_IDENTITIES = {
    31: (
        "31-W0-01",
        "31-W0-02",
        "31-W0-03",
        "31-W0-04",
        "31-W0-05",
    ),
    32: (
        "32-01-01",
        "32-01-02",
        "32-01-03",
        "32-01-04",
    ),
    33: (
        "33-01-01",
        "33-01-02",
        "33-01-03",
        "33-01-04",
    ),
    34: (
        "34-01-01",
        "34-01-02",
        "34-01-03",
    ),
    35: (
        "35-01-01",
        "35-01-02",
        "35-01-03",
    ),
    36: (
        "36-01-01",
        "36-01-02",
        "36-01-03",
        "36-02-01",
        "36-02-02",
    ),
    37: (
        "37-01-01",
        "37-01-02",
        "37-02-01",
        "37-02-02",
        "37-02-03",
    ),
    38: (
        "38-01-01",
        "38-01-02",
        "38-02-01",
        "38-02-02",
        "38-02-03",
    ),
    39: (
        "39-01-01",
        "39-01-02",
        "39-01-03",
    ),
    40: (
        "Baseline",
        "Rust domain",
        "Utilities",
        "Phases 5–11",
        "Phases 13–17",
        "Phases 18–28",
        "Phases 31–38",
        "Firmware tests",
        "Parser/UI/WUI",
        "Network/media",
        "Persistent storage",
        "Hardware/auxiliary",
        "Print/safety",
        "Terminal reconciliation",
    ),
    41: (
        "41-01-01",
        "41-01-02",
        "41-01-03",
        "41-02-01",
        "41-02-02",
        "41-03-01",
        "41-03-02",
    ),
}
