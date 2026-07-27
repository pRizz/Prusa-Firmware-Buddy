from __future__ import annotations

from phase23_execution_contract import *


def source_status_vocabulary(phase14: dict[str, Any]) -> set[str]:
    return set(
        require_list_of_strings(phase14, "status_vocabulary",
                                "phase14 contract"))


def scenario_map(phase14: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        require_string(scenario, "id", "scenario"): scenario
        for scenario in phase14_scenarios(phase14)
    }


def validate_exception_request(row: dict[str, Any],
                               row_name: str) -> dict[str, Any]:
    exception = require_dict(row, "exception_request", row_name)
    require_fields(exception, EXCEPTION_FIELDS,
                   f"{row_name} exception_request")
    validate_artifact_ref(
        require_string(exception, "evidence_ref",
                       f"{row_name} exception_request"), row_name)
    return exception


def validate_scenario_result(
    row: dict[str, Any],
    row_name: str,
    source_statuses: set[str],
    source_scenario: dict[str, Any],
) -> dict[str, Any]:
    require_fields(
        row,
        [
            "scenario_id",
            "status",
            "source_status",
            "status_reason",
            "artifact_refs",
            "redaction_status",
            "source_ref_status",
        ],
        row_name,
    )
    scenario_id = require_string(row, "scenario_id", row_name)
    status = require_string(row, "status", row_name)
    source_status = require_string(row, "source_status", row_name)
    if status not in V1_2_STATUSES:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    if source_status not in source_statuses:
        raise VerificationError(
            f"{row_name} source_status is not a Phase 14 status: {source_status}"
        )
    if status == "passed" and source_status in PENDING_SOURCE_STATUSES:
        raise VerificationError(
            f"{row_name} cannot pass with source_status={source_status}")
    redaction_status = require_string(row, "redaction_status", row_name)
    source_ref_status = require_string(row, "source_ref_status", row_name)
    if status == "passed" and redaction_status != "passed":
        raise VerificationError(
            f"{row_name} passed status requires redaction_status=passed")
    if status == "passed" and source_ref_status != "passed":
        raise VerificationError(
            f"{row_name} passed status requires source_ref_status=passed")
    exception_request = None
    if status == "exception-requested":
        exception_request = validate_exception_request(row, row_name)
    artifact_refs = validate_artifact_refs(row, row_name)
    runtime_metadata = row.get("runtime_metadata", {})
    if not isinstance(runtime_metadata, dict):
        raise VerificationError(
            f"{row_name} runtime_metadata must be an object when present")
    return {
        "artifact_refs":
        artifact_refs,
        "exception_request":
        exception_request,
        "phase11_source_refs":
        require_list_of_strings(source_scenario, "phase11_source_refs",
                                row_name),
        "proof_scope":
        require_string(source_scenario, "proof_scope", row_name),
        "pytest_node_ids":
        require_list_of_strings(source_scenario, "pytest_node_ids", row_name),
        "requirement_ids": ["EVID-01"],
        "runtime_metadata":
        runtime_metadata,
        "scenario_id":
        scenario_id,
        "simulator_requirement_ids":
        require_list_of_strings(source_scenario, "requirement_ids", row_name),
        "source_ref_status":
        source_ref_status,
        "source_status":
        source_status,
        "status":
        status,
        "status_reason":
        require_string(row, "status_reason", row_name),
        "title":
        require_string(source_scenario, "title", row_name),
        "redaction_status":
        redaction_status,
        "residual_non_simulator_gates":
        require_list_of_strings(source_scenario,
                                "residual_non_simulator_gates", row_name),
        "unsupported_claims":
        require_list_of_strings(source_scenario, "unsupported_claims",
                                row_name),
        "v1_requirement_ids":
        require_list_of_strings(source_scenario, "v1_requirement_ids",
                                row_name),
    }


def load_evidence_rows(
        root: Path, input_path: Path,
        phase14: dict[str,
                      Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if input_path.is_absolute() or ".." in input_path.parts:
        raise VerificationError(
            "--evidence-input must be repo-relative and cannot traverse")
    input_text = read_text(root, input_path)
    reject_forbidden_text(input_path, input_text)
    try:
        data = json.loads(input_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{input_path.as_posix()} is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    if not isinstance(data, dict):
        raise VerificationError(
            "--evidence-input must contain a top-level object")
    packet = require_dict(data, "simulator_evidence_packet",
                          "--evidence-input")
    require_fields(
        packet,
        [
            "evidence_run_id",
            "firmware_identity",
            "simulator_identity",
            "operator",
            "started_at",
            "completed_at",
            "scenario_results",
        ],
        "simulator_evidence_packet",
    )
    require_dict(packet, "firmware_identity", "simulator_evidence_packet")
    require_dict(packet, "simulator_identity", "simulator_evidence_packet")
    if packet.get("phase") not in (None, PHASE):
        raise VerificationError(
            f"simulator_evidence_packet phase must be {PHASE}")
    raw_rows = packet.get("scenario_results")
    if not isinstance(raw_rows, list):
        raise VerificationError(
            "simulator_evidence_packet scenario_results must be a list")
    sources = scenario_map(phase14)
    expected_ids = set(sources)
    seen_ids: set[str] = set()
    rows: list[dict[str, Any]] = []
    for index, raw_row in enumerate(raw_rows):
        if not isinstance(raw_row, dict):
            raise VerificationError(
                f"scenario_results[{index}] must be an object")
        scenario_id = str(raw_row.get("scenario_id", ""))
        row_name = f"scenario_results[{index}] {scenario_id or '<missing>'}"
        if scenario_id not in sources:
            raise VerificationError(
                f"{row_name} does not resolve to a Phase 14 scenario")
        if scenario_id in seen_ids:
            raise VerificationError(
                f"duplicate scenario result: {scenario_id}")
        seen_ids.add(scenario_id)
        rows.append(
            validate_scenario_result(raw_row, row_name,
                                     source_status_vocabulary(phase14),
                                     sources[scenario_id]))
    missing = sorted(expected_ids - seen_ids)
    extra = sorted(seen_ids - expected_ids)
    if missing or extra:
        parts: list[str] = []
        if missing:
            parts.append("missing scenario results: " + ", ".join(missing))
        if extra:
            parts.append("unexpected scenario results: " + ", ".join(extra))
        raise VerificationError("; ".join(parts))
    return packet, rows


def quick_rows(root: Path, output_dir: Path,
               phase14: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    logs_dir = root / output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    for scenario in phase14_scenarios(phase14):
        scenario_id = require_string(scenario, "id", "scenario")
        log_ref = output_dir / "logs" / f"{scenario_id}.log"
        source_status = "passed" if scenario_id == "sim-traceability-non-simulator-boundaries" else "pending-simulator-input"
        log_text = (
            f"phase: {PHASE}\n"
            f"scenario: {scenario_id}\n"
            "mode: quick-placeholder\n"
            "status: blocked\n"
            "reason: real simulator evidence input was not supplied.\n")
        sanitized_log, redaction_errors = sanitized_for_artifact(
            log_ref, log_text)
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        (root / log_ref).write_text(sanitized_log, encoding="utf-8")
        rows.append({
            "artifact_refs": [log_ref.as_posix()],
            "exception_request":
            None,
            "phase11_source_refs":
            require_list_of_strings(scenario, "phase11_source_refs",
                                    "scenario"),
            "proof_scope":
            require_string(scenario, "proof_scope", "scenario"),
            "pytest_node_ids":
            require_list_of_strings(scenario, "pytest_node_ids", "scenario"),
            "requirement_ids": ["EVID-01"],
            "runtime_metadata": {},
            "scenario_id":
            scenario_id,
            "simulator_requirement_ids":
            require_list_of_strings(scenario, "requirement_ids", "scenario"),
            "source_ref_status":
            "passed",
            "source_status":
            source_status,
            "status":
            "blocked",
            "status_reason":
            "real simulator evidence input was not supplied",
            "title":
            require_string(scenario, "title", "scenario"),
            "redaction_status":
            "passed",
            "residual_non_simulator_gates":
            require_list_of_strings(scenario, "residual_non_simulator_gates",
                                    "scenario"),
            "unsupported_claims":
            require_list_of_strings(scenario, "unsupported_claims",
                                    "scenario"),
            "v1_requirement_ids":
            require_list_of_strings(scenario, "v1_requirement_ids",
                                    "scenario"),
        })
    return rows


def aggregate_status(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row["status"]) for row in rows}
    if "failed" in statuses:
        return "failed"
    if "blocked" in statuses:
        return "blocked"
    if "exception-requested" in statuses:
        return "exception-requested"
    return "passed"


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return counts
