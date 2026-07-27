from __future__ import annotations

from phase25_execution_contract import *


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
    require_fields(row, REQUIRED_ROW_FIELDS, row_name)
    scenario_id = require_string(row, "scenario_id", row_name)
    status = require_string(row, "status", row_name)
    source_status = require_string(row, "source_status", row_name)
    if status not in V1_2_STATUSES:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    if source_status not in source_statuses:
        raise VerificationError(
            f"{row_name} source_status is not a Phase 16 status: {source_status}"
        )
    allowed_source_statuses = set(
        require_list_of_strings(source_scenario, "allowed_statuses", row_name))
    if source_status not in allowed_source_statuses:
        raise VerificationError(
            f"{row_name} source_status is not allowed for this Phase 16 scenario: {source_status}"
        )
    redaction_status = require_string(row, "redaction_status", row_name)
    source_ref_status = require_string(row, "source_ref_status", row_name)
    if status == "passed" and source_status not in {
            "passed", "source-contract-passed"
    }:
        raise VerificationError(
            f"{row_name} cannot pass with source_status={source_status}")
    if status == "passed" and redaction_status != "passed":
        raise VerificationError(
            f"{row_name} passed status requires redaction_status=passed")
    if status == "passed" and source_ref_status != "passed":
        raise VerificationError(
            f"{row_name} passed status requires source_ref_status=passed")
    proof_scope = require_string(source_scenario, "proof_scope", row_name)
    evidence_type = require_string(row, "evidence_type", row_name)
    if status == "passed" and proof_scope == "source-contract" and evidence_type not in SOURCE_CONTRACT_PASS_EVIDENCE_TYPES:
        raise VerificationError(
            f"{row_name} source-contract pass requires source-contract-validation evidence_type"
        )
    if status == "passed" and proof_scope != "source-contract" and evidence_type not in LIVE_PASS_EVIDENCE_TYPES:
        raise VerificationError(
            f"{row_name} live-service pass requires live or controlled service observation evidence_type"
        )
    service_surface = require_string(row, "service_surface", row_name)
    mode = require_string(row, "mode", row_name)
    expected_service_surface = require_string(source_scenario,
                                              "service_surface", row_name)
    expected_mode = require_string(source_scenario, "mode", row_name)
    if service_surface != expected_service_surface:
        raise VerificationError(
            f"{row_name} service_surface must be {expected_service_surface}")
    if mode != expected_mode:
        raise VerificationError(f"{row_name} mode must be {expected_mode}")
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
        "credential_boundary":
        require_string(source_scenario, "credential_boundary", row_name),
        "device":
        require_string(row, "device", row_name),
        "evidence_type":
        evidence_type,
        "exception_request":
        exception_request,
        "firmware_build":
        require_string(row, "firmware_build", row_name),
        "live_requirement_ids":
        require_list_of_strings(source_scenario, "requirement_ids", row_name),
        "mode":
        mode,
        "operator":
        require_string(row, "operator", row_name),
        "phase16_source_contract_refs":
        require_list_of_strings(source_scenario, "source_contract_refs",
                                row_name),
        "proof_scope":
        proof_scope,
        "redaction_status":
        redaction_status,
        "redaction_summary":
        require_string(row, "redaction_summary", row_name),
        "requirement_ids": ["EVID-03"],
        "residual_non_live_gates":
        require_list_of_strings(source_scenario, "residual_non_live_gates",
                                row_name),
        "residual_risk":
        require_string(row, "residual_risk", row_name),
        "retained_artifact_kind":
        require_string(source_scenario, "retained_artifact_kind", row_name),
        "runtime_metadata":
        runtime_metadata,
        "scenario_id":
        scenario_id,
        "service_surface":
        service_surface,
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
        phase16: dict[str,
                      Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if input_path.is_absolute() or ".." in input_path.parts:
        raise VerificationError(
            "--evidence-input must be repo-relative and cannot traverse")
    input_text = read_text(root, input_path)
    try:
        data = json.loads(input_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{input_path.as_posix()} is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    reject_forbidden_text(input_path, input_text)
    if not isinstance(data, dict):
        raise VerificationError(
            "--evidence-input must contain a top-level object")
    packet = require_dict(data, "live_service_evidence_packet",
                          "--evidence-input")
    require_fields(packet, REQUIRED_PACKET_FIELDS,
                   "live_service_evidence_packet")
    require_dict(packet, "firmware_identity", "live_service_evidence_packet")
    if packet.get("phase") not in (None, PHASE):
        raise VerificationError(
            f"live_service_evidence_packet phase must be {PHASE}")
    if packet.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"live_service_evidence_packet phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
        )
    if packet.get("source_contract_ref") != PHASE16_CONTRACT.as_posix():
        raise VerificationError(
            f"live_service_evidence_packet source_contract_ref must be {PHASE16_CONTRACT.as_posix()}"
        )
    raw_rows = packet.get("scenario_results")
    if not isinstance(raw_rows, list):
        raise VerificationError(
            "live_service_evidence_packet scenario_results must be a list")
    sources = scenario_map(phase16)
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
                f"{row_name} does not resolve to a Phase 16 scenario")
        if scenario_id in seen_ids:
            raise VerificationError(
                f"duplicate scenario result: {scenario_id}")
        seen_ids.add(scenario_id)
        rows.append(
            validate_scenario_result(raw_row, row_name,
                                     source_status_vocabulary(phase16),
                                     sources[scenario_id]))
    missing = sorted(expected_ids - seen_ids)
    if missing:
        raise VerificationError("missing scenario results: " +
                                ", ".join(missing))
    return packet, rows
