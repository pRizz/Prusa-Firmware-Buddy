from __future__ import annotations

from phase24_execution_contract import *


def validate_exception_request(row: dict[str, Any],
                               row_name: str) -> dict[str, Any]:
    exception = require_dict(row, "exception_request", row_name)
    require_fields(exception, EXCEPTION_FIELDS,
                   f"{row_name} exception_request")
    validate_artifact_ref(
        require_string(exception, "evidence_ref",
                       f"{row_name} exception_request"), row_name)
    return exception


def is_storage_scenario(source_scenario: dict[str, Any]) -> bool:
    return require_string(source_scenario, "id",
                          "scenario").startswith("hard-storage-")


def validate_scenario_result(
    row: dict[str, Any],
    row_name: str,
    source_statuses: set[str],
    source_scenario: dict[str, Any],
) -> dict[str, Any]:
    require_fields(row, REQUIRED_ROW_FIELDS, row_name)
    scenario_id = require_string(row, "scenario_id", row_name)
    status = require_string(row, "status", row_name)
    source_status = require_string(row, "source_status", row_name)
    if status not in V1_2_STATUSES:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    if source_status not in source_statuses:
        raise VerificationError(
            f"{row_name} source_status is not a Phase 15 status: {source_status}"
        )
    allowed_source_statuses = set(
        require_list_of_strings(source_scenario, "allowed_statuses", row_name))
    if source_status not in allowed_source_statuses:
        raise VerificationError(
            f"{row_name} source_status is not allowed for this Phase 15 scenario: {source_status}"
        )
    if status == "passed" and source_status not in {
            "passed", "source-contract-passed"
    }:
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
    printer_family = require_string(row, "printer_family", row_name)
    board = require_string(row, "board", row_name)
    media_surface = require_string(row, "media_surface", row_name)
    auxiliary_surface = require_string(row, "auxiliary_surface", row_name)
    expected_printer_family = require_string(source_scenario, "printer_family",
                                             row_name)
    expected_board = require_string(source_scenario, "board", row_name)
    expected_media_surface = require_string(source_scenario, "media_surface",
                                            row_name)
    expected_auxiliary_surface = require_string(source_scenario,
                                                "auxiliary_surface", row_name)
    if printer_family != expected_printer_family:
        raise VerificationError(
            f"{row_name} printer_family must be {expected_printer_family}")
    if board != expected_board:
        raise VerificationError(f"{row_name} board must be {expected_board}")
    if media_surface != expected_media_surface:
        raise VerificationError(
            f"{row_name} media_surface must be {expected_media_surface}")
    if auxiliary_surface != expected_auxiliary_surface:
        raise VerificationError(
            f"{row_name} auxiliary_surface must be {expected_auxiliary_surface}"
        )
    if is_storage_scenario(source_scenario):
        require_string(row, "observed_behavior", row_name)
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
        "auxiliary_surface":
        auxiliary_surface,
        "board":
        board,
        "device":
        require_string(row, "device", row_name),
        "exception_request":
        exception_request,
        "failure_observations":
        require_string(row, "failure_observations", row_name),
        "firmware_build":
        require_string(row, "firmware_build", row_name),
        "hardware_requirement_ids":
        require_list_of_strings(source_scenario, "requirement_ids", row_name),
        "media_surface":
        media_surface,
        "observed_behavior":
        row.get("observed_behavior", ""),
        "operator":
        require_string(row, "operator", row_name),
        "phase15_source_contract_refs":
        require_list_of_strings(source_scenario, "source_contract_refs",
                                row_name),
        "printer_family":
        printer_family,
        "proof_scope":
        require_string(source_scenario, "proof_scope", row_name),
        "redaction_status":
        redaction_status,
        "requirement_ids": ["EVID-02"],
        "residual_risk":
        require_string(row, "residual_risk", row_name),
        "retained_artifact_kind":
        require_string(source_scenario, "retained_artifact_kind", row_name),
        "runtime_metadata":
        runtime_metadata,
        "scenario_id":
        scenario_id,
        "source_ref_status":
        source_ref_status,
        "source_status":
        source_status,
        "status":
        status,
        "status_reason":
        require_string(row, "status_reason", row_name),
        "timestamp":
        require_string(row, "timestamp", row_name),
        "title":
        require_string(source_scenario, "title", row_name),
        "unsupported_claims":
        require_list_of_strings(source_scenario, "unsupported_claims",
                                row_name),
        "v1_requirement_ids":
        require_list_of_strings(source_scenario, "v1_requirement_ids",
                                row_name),
    }


def load_evidence_rows(
        root: Path, input_path: Path,
        phase15: dict[str,
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
    packet = require_dict(data, "hardware_media_safety_evidence_packet",
                          "--evidence-input")
    require_fields(packet, REQUIRED_PACKET_FIELDS,
                   "hardware_media_safety_evidence_packet")
    require_dict(packet, "firmware_identity",
                 "hardware_media_safety_evidence_packet")
    if packet.get("phase") not in (None, PHASE):
        raise VerificationError(
            f"hardware_media_safety_evidence_packet phase must be {PHASE}")
    if packet.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"hardware_media_safety_evidence_packet phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
        )
    if packet.get("source_contract_ref") != PHASE15_CONTRACT.as_posix():
        raise VerificationError(
            f"hardware_media_safety_evidence_packet source_contract_ref must be {PHASE15_CONTRACT.as_posix()}"
        )
    raw_rows = packet.get("scenario_results")
    if not isinstance(raw_rows, list):
        raise VerificationError(
            "hardware_media_safety_evidence_packet scenario_results must be a list"
        )
    sources = scenario_map(phase15)
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
                f"{row_name} does not resolve to a Phase 15 scenario")
        if scenario_id in seen_ids:
            raise VerificationError(
                f"duplicate scenario result: {scenario_id}")
        seen_ids.add(scenario_id)
        rows.append(
            validate_scenario_result(raw_row, row_name,
                                     source_status_vocabulary(phase15),
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
