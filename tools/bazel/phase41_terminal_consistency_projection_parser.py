#!/usr/bin/env python3
from __future__ import annotations

import re

from phase41_terminal_consistency_contracts import (
    AuditFrontmatterProjection,
    MILESTONE_PHASES,
    RequirementsCoverageProjection,
    RoadmapProgressProjection,
    RoadmapProgressRow,
)
from phase41_terminal_consistency_markdown import BoundaryParser

REQUIREMENTS_PATH = ".planning/REQUIREMENTS.md"
ROADMAP_PATH = ".planning/ROADMAP.md"
AUDIT_PATH = ".planning/v1.3-MILESTONE-AUDIT.md"


def parse_requirements_coverage(
    parser: BoundaryParser,
    text: str,
) -> RequirementsCoverageProjection | None:
    block = parser.required_labeled_block(REQUIREMENTS_PATH, text, "Coverage")
    if not block:
        return None
    lines = tuple(line.strip() for line in block.splitlines()
                  if line.strip().startswith("- "))
    patterns = (
        r"- v1\.3 requirements: (\d+) total",
        r"- Mapped to phases: (\d+)",
        r"- Behavior-evidenced complete: (\d+)/(\d+)",
        r"- Phase 41 terminal-projection ownership rows (pending phase completion|complete): (\d+)/(\d+)",
        r"- Unmapped: (\d+)",
        r"- Duplicate mappings: (\d+)",
    )
    if len(lines) != len(patterns):
        parser.violation(REQUIREMENTS_PATH, "P41_REQUIREMENTS_COVERAGE_SHAPE",
                         f"{len(lines)} fields",
                         "exact six-field coverage rollup")
        return None
    matches = tuple(
        re.fullmatch(pattern, line) for pattern, line in zip(patterns, lines))
    if not all(matches):
        parser.violation(REQUIREMENTS_PATH, "P41_REQUIREMENTS_COVERAGE_SHAPE",
                         lines,
                         "exact ordered coverage labels and scalar shapes")
        return None
    total, mapped, behavior, ownership, unmapped, duplicates = matches
    assert total and mapped and behavior and ownership and unmapped and duplicates
    ownership_state = "pending" if ownership.group(1).startswith(
        "pending") else "complete"
    return RequirementsCoverageProjection(
        total_requirements=int(total.group(1)),
        mapped_requirements=int(mapped.group(1)),
        behavior_evidenced_complete=int(behavior.group(1)),
        behavior_evidenced_total=int(behavior.group(2)),
        phase41_owned=int(ownership.group(2)),
        phase41_ownership_total=int(ownership.group(3)),
        phase41_ownership_state=ownership_state,
        unmapped=int(unmapped.group(1)),
        duplicate_mappings=int(duplicates.group(1)),
    )


def _cell(row: dict[str, str], name: str) -> str:
    return next(
        (value
         for key, value in row.items() if key.casefold() == name.casefold()),
        "")


def _execution_edges(
        parser: BoundaryParser,
        progress: str) -> tuple[tuple[tuple[int, ...], int], ...] | None:
    block = parser.required_labeled_block(ROADMAP_PATH, progress,
                                          "Execution Order")
    expressions = re.findall(r"`([^`]+)`", block)
    edges: list[tuple[tuple[int, ...], int]] = []
    for expression in expressions:
        maybe_edge = re.fullmatch(
            r"\s*(\d+)(?:\s*\+\s*(\d+))?\s*->\s*(\d+)\s*", expression)
        if maybe_edge is None:
            parser.violation(ROADMAP_PATH, "P41_ROADMAP_EXECUTION_SHAPE",
                             expression, "integer source edge")
            return None
        sources = tuple(
            int(value) for value in maybe_edge.groups()[:2]
            if value is not None)
        edges.append((sources, int(maybe_edge.group(3))))
    if not block or len(edges) != 3:
        parser.violation(ROADMAP_PATH, "P41_ROADMAP_EXECUTION_SHAPE",
                         f"{len(edges)} edges", "exact three execution edges")
        return None
    return tuple(edges)


def parse_roadmap_progress(parser: BoundaryParser,
                           text: str) -> RoadmapProgressProjection | None:
    section = parser.required_section(ROADMAP_PATH, text, "Progress")
    if not section:
        return None
    table_rows = parser.required_table(
        ROADMAP_PATH,
        section,
        ("Phase", "Milestone", "Plans Complete", "Status"),
        "roadmap progress",
    )
    edges = _execution_edges(parser, section)
    if not table_rows or edges is None:
        return None
    rows: list[RoadmapProgressRow] = []
    v13_rows = [row for row in table_rows if _cell(row, "Milestone") == "v1.3"]
    for table_row in v13_rows:
        maybe_phase = re.fullmatch(r"(\d+)\..+", _cell(table_row, "Phase"))
        maybe_plans = re.fullmatch(r"(\d+)/(\d+)",
                                   _cell(table_row, "Plans Complete"))
        milestone = _cell(table_row, "Milestone")
        status = _cell(table_row, "Status")
        if maybe_phase is None or maybe_plans is None or milestone != "v1.3" or status not in {
                "Complete", "In Progress"
        }:
            parser.violation(
                ROADMAP_PATH, "P41_ROADMAP_PROGRESS_SHAPE", table_row,
                "v1.3 phase row with plan fraction and supported status")
            return None
        rows.append(
            RoadmapProgressRow(
                phase=int(maybe_phase.group(1)),
                completed_plans=int(maybe_plans.group(1)),
                total_plans=int(maybe_plans.group(2)),
                status=status,
            ))
    return RoadmapProgressProjection(
        rows=tuple(rows),
        execution_edges=edges,
        milestone_completed_phases=sum(row.status == "Complete"
                                       for row in rows),
        milestone_total_phases=len(rows),
        milestone_completed_plans=sum(row.completed_plans for row in rows),
        milestone_total_plans=sum(row.total_plans for row in rows),
        milestone_status=("Complete"
                          if rows and all(row.status == "Complete"
                                          for row in rows) else "Active"),
    )


def _mapping(parent: dict[str, object], key: str) -> dict[str, object] | None:
    value = parent.get(key)
    return value if isinstance(value, dict) else None


def _string(parent: dict[str, object], key: str) -> str | None:
    value = parent.get(key)
    return value if isinstance(value, str) else None


def _integer(parent: dict[str, object], key: str) -> int | None:
    value = parent.get(key)
    return value if isinstance(value,
                               int) and not isinstance(value, bool) else None


def _integer_tuple(parent: dict[str, object],
                   key: str) -> tuple[int, ...] | None:
    value = parent.get(key)
    return value if isinstance(value, tuple) and all(
        isinstance(item, int) for item in value) else None


def parse_audit_frontmatter(parser: BoundaryParser,
                            text: str) -> AuditFrontmatterProjection | None:
    values = parser.nested_frontmatter(AUDIT_PATH, text)
    if values is None:
        return None
    scores = _mapping(values, "scores")
    integration = _mapping(values, "integration_checker")
    nyquist = _mapping(values, "nyquist")
    if scores is None or integration is None or nyquist is None:
        parser.violation(AUDIT_PATH, "P41_AUDIT_FRONTMATTER_SHAPE",
                         "missing nested projection",
                         "scores, integration_checker, nyquist mappings")
        return None
    integration_score = _string(integration, "integration_score") or ""
    flow_score = _string(integration, "flow_score") or ""
    maybe_integration = re.fullmatch(
        r"(\d+) connected / (\d+) partial / (\d+) broken", integration_score)
    maybe_flow = re.fullmatch(r"(\d+) complete / (\d+) partial / (\d+) broken",
                              flow_score)
    fields = {
        "scores_requirements": _string(scores, "requirements"),
        "scores_phases": _string(scores, "phases"),
        "scores_integration": _string(scores, "integration"),
        "scores_flows": _string(scores, "flows"),
        "integration_status": _string(integration, "status"),
        "runtime_safety_gaps": _integer(integration, "runtime_safety_gaps"),
        "metadata_gaps": _integer(integration, "metadata_gaps"),
        "archival_blockers": _integer(integration, "archival_blockers"),
        "compliant_phases": _integer_tuple(nyquist, "compliant_phases"),
        "partial_phases": _integer_tuple(nyquist, "partial_phases"),
        "missing_phases": _integer_tuple(nyquist, "missing_phases"),
        "nyquist_overall": _string(nyquist, "overall"),
    }
    if (maybe_integration is None or maybe_flow is None
            or any(value is None for value in fields.values())):
        parser.violation(AUDIT_PATH, "P41_AUDIT_FRONTMATTER_SHAPE",
                         "malformed scalar or list",
                         "complete typed audit projection")
        return None
    return AuditFrontmatterProjection(
        **fields,
        integration_connected=int(maybe_integration.group(1)),
        integration_partial=int(maybe_integration.group(2)),
        integration_broken=int(maybe_integration.group(3)),
        flow_complete=int(maybe_flow.group(1)),
        flow_partial=int(maybe_flow.group(2)),
        flow_broken=int(maybe_flow.group(3)),
    )
