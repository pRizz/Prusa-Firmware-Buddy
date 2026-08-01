#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

maybe_bazel_module_dir = Path(
    f"{Path(__file__).resolve()}.runfiles") / "_main/tools/bazel"
if maybe_bazel_module_dir.is_dir():
    sys.path.insert(0, str(maybe_bazel_module_dir))

from phase41_terminal_consistency_policy import (
    CANONICAL_REQUIREMENTS,
    MILESTONE_PHASES,
    AuditRecord,
    MilestoneProjection,
    PhaseLifecycle,
    PlanInventory,
    RequirementRecord,
    TerminalSnapshot,
    ValidationRecord,
    Violation,
    evaluate_terminal_consistency,
    exit_code_for_violations,
)

ROADMAP_PATH = ".planning/ROADMAP.md"
REQUIREMENTS_PATH = ".planning/REQUIREMENTS.md"
STATE_PATH = ".planning/STATE.md"
AUDIT_PATH = ".planning/v1.3-MILESTONE-AUDIT.md"


class BoundaryParser:

    def __init__(self, root: Path) -> None:
        self.root = root
        self.violations: list[Violation] = []

    def violation(self, path: str, code: str, observed: object,
                  expected: object) -> None:
        self.violations.append(
            Violation(path, code,
                      str(observed)[:160],
                      str(expected)[:160]))

    def read_text(self, relative_path: str) -> str | None:
        try:
            return (self.root / relative_path).read_text(encoding="utf-8")
        except (FileNotFoundError, OSError, UnicodeError):
            self.violation(relative_path, "P41_BOUNDARY_READ", "unreadable",
                           "readable UTF-8 file")
            return None

    def frontmatter(self, path: str,
                    text: str | None) -> dict[str, str] | None:
        if text is None:
            return None
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            self.violation(path, "P41_FRONTMATTER_MALFORMED",
                           "missing opening delimiter", "YAML frontmatter")
            return None
        try:
            closing = lines.index("---", 1)
        except ValueError:
            self.violation(path, "P41_FRONTMATTER_MALFORMED",
                           "missing closing delimiter", "YAML frontmatter")
            return None
        values: dict[str, str] = {}
        for line in lines[1:closing]:
            if not line or line[0].isspace() or ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            if key in values:
                self.violation(path, "P41_FRONTMATTER_DUPLICATE", key,
                               "unique top-level keys")
                return None
            values[key] = raw_value.strip().strip('"').strip("'")
        return values


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"(?m)^##+\s+{re.escape(heading)}\s*$")
    match = pattern.search(text)
    if match is None:
        return ""
    remainder = text[match.end():]
    next_heading = re.search(r"(?m)^##+\s+", remainder)
    return remainder[:next_heading.start()] if next_heading else remainder


def table_rows(text: str) -> list[dict[str, str]]:
    lines = [
        line.strip() for line in text.splitlines() if line.startswith("|")
    ]
    rows: list[dict[str, str]] = []
    index = 0
    while index + 1 < len(lines):
        header = [cell.strip() for cell in lines[index].strip("|").split("|")]
        separator = lines[index + 1]
        if not all(
                re.fullmatch(r":?-{3,}:?", cell.strip())
                for cell in separator.strip("|").split("|")):
            index += 1
            continue
        index += 2
        while index < len(lines):
            cells = [
                cell.strip() for cell in lines[index].strip("|").split("|")
            ]
            if len(cells) != len(header):
                break
            rows.append(dict(zip(header, cells)))
            index += 1
    return rows


def parse_phase(value: str) -> int:
    maybe_match = re.search(r"\bPhase\s+(\d+)\b", value)
    return int(maybe_match.group(1)) if maybe_match else 0


def unique_projection(rows: list[dict[str, str]], requirement_id: str,
                      phase_column: str,
                      status_column: str) -> tuple[int, str]:
    matches = [row for row in rows if row.get("Requirement") == requirement_id]
    if len(matches) != 1:
        return 0, f"duplicate:{len(matches)}"
    return parse_phase(matches[0].get(phase_column, "")), matches[0].get(
        status_column, "missing")


def parse_requirements(parser: BoundaryParser, requirements_text: str,
                       roadmap_text: str) -> tuple[RequirementRecord, ...]:
    checklist_pattern = re.compile(
        r"(?m)^- \[([ xX])\] \*\*([A-Z]+-\d+)\*\*:\s*(.+)$")
    checklist_rows = checklist_pattern.findall(requirements_text)
    counts = {
        requirement_id: sum(row[1] == requirement_id for row in checklist_rows)
        for requirement_id in {row[1]
                               for row in checklist_rows}
    }
    requirement_trace = table_rows(section(requirements_text, "Traceability"))
    roadmap_trace = table_rows(section(roadmap_text, "Requirement Coverage"))
    records: list[RequirementRecord] = []
    for marker, requirement_id, semantic_text in checklist_rows:
        requirements_phase, requirements_status = unique_projection(
            requirement_trace, requirement_id, "Phase", "Status")
        roadmap_phase, roadmap_status = unique_projection(
            roadmap_trace, requirement_id, "Phase", "Status")
        records.append(
            RequirementRecord(
                requirement_id=requirement_id,
                semantic_text=semantic_text,
                checklist_count=counts[requirement_id],
                checked=marker.lower() == "x",
                requirements_phase=requirements_phase,
                requirements_status=requirements_status,
                roadmap_phase=roadmap_phase,
                roadmap_status=roadmap_status,
            ))
    return tuple(records)


def roadmap_phase_sections(roadmap_text: str) -> dict[int, str]:
    matches = list(re.finditer(r"(?m)^### Phase (\d+):[^\n]*$", roadmap_text))
    sections: dict[int, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(
            roadmap_text)
        sections[int(match.group(1))] = roadmap_text[match.end():end]
    return sections


def phase_directories(root: Path, phase: int) -> list[Path]:
    return sorted((root / ".planning/phases").glob(f"{phase:02d}-*"))


def parse_phases_and_inventories(
    parser: BoundaryParser,
    roadmap_text: str,
) -> tuple[tuple[PhaseLifecycle, ...], tuple[PlanInventory, ...]]:
    status_matches = re.findall(r"(?m)^- \[([ xX])\] \*\*Phase (\d+):",
                                roadmap_text)
    status_by_phase = {
        int(phase): "Complete" if marker.lower() == "x" else "Planned"
        for marker, phase in status_matches
    }
    sections = roadmap_phase_sections(roadmap_text)
    phases: list[PhaseLifecycle] = []
    inventories: list[PlanInventory] = []
    for phase in MILESTONE_PHASES:
        directories = phase_directories(parser.root, phase)
        if len(directories) != 1:
            parser.violation(".planning/phases", "P41_PHASE_DIRECTORY_COUNT",
                             f"Phase {phase}:{len(directories)}", "one")
        maybe_directory = directories[0] if directories else None
        plans = tuple(
            sorted(path.name for path in maybe_directory.glob(
                "*-PLAN.md"))) if maybe_directory else ()
        summaries = tuple(
            sorted(path.name for path in maybe_directory.glob(
                "*-SUMMARY.md"))) if maybe_directory else ()
        detail = sections.get(phase, "")
        roadmap_plans = tuple(
            re.findall(r"(?m)^- \[[ xX]\]\s+(\d+-\d+-PLAN\.md)\b", detail))
        maybe_fraction = re.search(r"\*\*Plans\*\*:\s*(\d+)/(\d+)", detail)
        maybe_count = re.search(r"\*\*Plans\*\*:\s*(\d+)\s+plans?\b", detail)
        roadmap_total = int(maybe_fraction.group(2)) if maybe_fraction else (
            int(maybe_count.group(1)) if maybe_count else 0)
        roadmap_completed = int(
            maybe_fraction.group(1)) if maybe_fraction else sum(
                bool(marker) for marker in re.findall(
                    r"(?m)^- \[([xX])\]\s+\d+-\d+-PLAN\.md\b", detail))
        phases.append(
            PhaseLifecycle(
                phase=phase,
                directory_present=maybe_directory is not None,
                roadmap_listed=phase in status_by_phase,
                roadmap_status=status_by_phase.get(phase, "missing"),
            ))
        inventories.append(
            PlanInventory(
                phase=phase,
                plans=plans,
                summaries=summaries,
                roadmap_plans=roadmap_plans,
                roadmap_completed=roadmap_completed,
                roadmap_total=roadmap_total,
            ))
    return tuple(phases), tuple(inventories)


def scalar_bool(values: dict[str, str] | None, key: str) -> bool:
    return values is not None and values.get(key, "").lower() == "true"


def normalized_status(value: str) -> str:
    lowered = value.lower()
    for status in ("pending", "red", "green", "passed", "pass", "complete"):
        if status in lowered:
            return status
    return lowered[:80]


def validation_statuses(text: str) -> tuple[str, ...]:
    statuses: list[str] = []
    for row in table_rows(text):
        maybe_status_key = next(
            (key for key in row if key.lower() == "status"), None)
        if maybe_status_key is not None:
            statuses.append(normalized_status(row[maybe_status_key]))
    return tuple(statuses)


def validation_signoff(text: str) -> bool:
    signoff = section(text, "Validation Sign-Off")
    bullets = re.findall(r"(?m)^- \[([ xX])\]", signoff)
    return bool(bullets) and all(marker.lower() == "x" for marker in bullets)


def parse_validations(parser: BoundaryParser) -> tuple[ValidationRecord, ...]:
    records: list[ValidationRecord] = []
    for phase in MILESTONE_PHASES:
        directories = phase_directories(parser.root, phase)
        maybe_directory = directories[0] if len(directories) == 1 else None
        relative_path = (
            f".planning/phases/{maybe_directory.name}/"
            f"{phase:02d}-VALIDATION.md" if maybe_directory else
            f".planning/phases/{phase:02d}-missing/{phase:02d}-VALIDATION.md")
        text = parser.read_text(relative_path)
        values = parser.frontmatter(relative_path, text)
        records.append(
            ValidationRecord(
                phase=phase,
                path=relative_path,
                present=text is not None,
                parsed=values is not None,
                nyquist_compliant=scalar_bool(values, "nyquist_compliant"),
                wave_0_complete=scalar_bool(values, "wave_0_complete"),
                task_statuses=validation_statuses(text or ""),
                signoff_complete=validation_signoff(text or ""),
            ))
    return tuple(records)


def integer_value(text: str, key: str) -> int:
    maybe_match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(\d+)\s*$", text)
    return int(maybe_match.group(1)) if maybe_match else 0


def parse_milestone(
        parser: BoundaryParser, roadmap_text: str, state_text: str,
        phases: tuple[PhaseLifecycle,
                      ...], inventories: tuple[PlanInventory,
                                               ...]) -> MilestoneProjection:
    milestone_line = next(
        (line for line in roadmap_text.splitlines() if "**v1.3 " in line), "")
    roadmap_status = "Complete" if "shipped" in milestone_line.lower(
    ) else "Active" if "active" in milestone_line.lower() else "missing"
    roadmap_total_plans = sum(item.roadmap_total for item in inventories)
    roadmap_completed_plans = sum(item.roadmap_completed
                                  for item in inventories)
    maybe_phase = re.search(r"(?m)^Phase:\s*(\d+)", state_text)
    maybe_plan = re.search(r"(?m)^Plan:\s*(\d+)\s+of\s+\d+", state_text)
    maybe_milestone = re.search(r"(?m)^Milestone:.*-\s*([^\n]+)$", state_text)
    state_values = parser.frontmatter(STATE_PATH, state_text)
    state_status = (state_values or {}).get("status", "missing")
    state_milestone_status = maybe_milestone.group(
        1).strip().lower() if maybe_milestone else "missing"
    return MilestoneProjection(
        roadmap_status=roadmap_status,
        roadmap_total_phases=len(phases),
        roadmap_completed_phases=sum(item.roadmap_status == "Complete"
                                     for item in phases),
        roadmap_total_plans=roadmap_total_plans,
        roadmap_completed_plans=roadmap_completed_plans,
        state_status=state_status,
        state_milestone_status=state_milestone_status,
        state_total_phases=integer_value(state_text, "total_phases"),
        state_completed_phases=integer_value(state_text, "completed_phases"),
        state_total_plans=integer_value(state_text, "total_plans"),
        state_completed_plans=integer_value(state_text, "completed_plans"),
        state_current_phase=int(maybe_phase.group(1)) if maybe_phase else 0,
        state_current_plan=int(maybe_plan.group(1)) if maybe_plan else 0,
        state_narrative_terminal=(state_status == "complete"
                                  and state_milestone_status == "complete"
                                  and bool(maybe_phase)
                                  and int(maybe_phase.group(1)) == 41),
    )


def parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def latest_phase41_summary_time(parser: BoundaryParser) -> datetime | None:
    directories = phase_directories(parser.root, 41)
    if len(directories) != 1:
        return None
    times: list[datetime] = []
    for summary_path in directories[0].glob("41-*-SUMMARY.md"):
        relative = summary_path.relative_to(parser.root).as_posix()
        values = parser.frontmatter(relative, parser.read_text(relative))
        maybe_time = parse_iso((values or {}).get("generated_at", ""))
        if maybe_time is not None:
            times.append(maybe_time)
    return max(times) if times else None


def parse_audit(parser: BoundaryParser) -> AuditRecord:
    text = parser.read_text(AUDIT_PATH)
    values = parser.frontmatter(AUDIT_PATH, text)
    body = text or ""
    maybe_scope = re.search(r"\|\s*Phases\s*\|\s*(\d+)\s+through\s+(\d+)",
                            body)
    phase_numbers = tuple(
        range(int(maybe_scope.group(1)),
              int(maybe_scope.group(2)) + 1)) if maybe_scope else ()
    requirement_count = next((
        int(match.group(1))
        for match in [re.search(r"\|\s*Requirements\s*\|\s*(\d+)\s*\|", body)]
        if match), 0)
    maybe_coherent = re.search(r"\|\s*Fully coherent\s*\|\s*(\d+)", body)
    flow_rows = table_rows(section(body, "End-to-End Flows"))
    flow_gaps = sum(
        row.get("Status", "").lower() != "complete" for row in flow_rows)
    nyquist_rows = table_rows(section(body, "Nyquist Coverage"))
    nyquist_gaps = sum(
        row.get("Audit classification", "").lower() != "compliant"
        for row in nyquist_rows)
    maybe_integration = re.search(
        r"\|\s*Runtime integration gaps\s*\|\s*(\d+)", body)
    maybe_metadata = re.search(
        r"\|\s*Milestone archival blockers\s*\|\s*(\d+)", body)
    audited = parse_iso((values or {}).get("audited", ""))
    latest_summary = latest_phase41_summary_time(parser)
    fresh = audited is not None and latest_summary is not None and audited >= latest_summary
    return AuditRecord(
        path=AUDIT_PATH,
        present=text is not None,
        parsed=values is not None,
        status=(values or {}).get("status", "missing"),
        fresh=fresh,
        phase_numbers=phase_numbers,
        requirement_count=requirement_count,
        coherent_requirement_count=int(maybe_coherent.group(1))
        if maybe_coherent else 0,
        integration_gaps=int(maybe_integration.group(1))
        if maybe_integration else 0,
        flow_gaps=flow_gaps,
        metadata_gaps=int(maybe_metadata.group(1)) if maybe_metadata else 0,
        nyquist_gaps=nyquist_gaps,
    )


def load_snapshot(root: Path) -> TerminalSnapshot:
    parser = BoundaryParser(root)
    requirements_text = parser.read_text(REQUIREMENTS_PATH) or ""
    roadmap_text = parser.read_text(ROADMAP_PATH) or ""
    state_text = parser.read_text(STATE_PATH) or ""
    requirements = parse_requirements(parser, requirements_text, roadmap_text)
    phases, inventories = parse_phases_and_inventories(parser, roadmap_text)
    validations = parse_validations(parser)
    milestone = parse_milestone(parser, roadmap_text, state_text, phases,
                                inventories)
    audit = parse_audit(parser)
    return TerminalSnapshot(
        requirements=requirements,
        phases=phases,
        inventories=inventories,
        validations=validations,
        milestone=milestone,
        audit=audit,
        boundary_violations=tuple(parser.violations),
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check terminal v1.3 milestone metadata coherence.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("BUILD_WORKSPACE_DIRECTORY", ".")),
    )
    parser.add_argument("--mode",
                        choices=("pre-audit", "pre-archive"),
                        required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    snapshot = load_snapshot(args.root.resolve())
    violations = evaluate_terminal_consistency(snapshot, args.mode)
    for violation in violations:
        print(f"{violation.code} path={violation.path} "
              f"observed={violation.observed} expected={violation.expected}")
    if not violations:
        print(f"phase41 terminal consistency passed mode={args.mode}")
    return exit_code_for_violations(violations)


if __name__ == "__main__":
    sys.exit(main())
