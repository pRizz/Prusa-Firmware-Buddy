#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "25-live-service-evidence-execution"
PHASE_LIFECYCLE_ID = "25-2026-06-23T21-12-42"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json")
PHASE16_CONTRACT = Path("tools/bazel/manifests/phase16_live_network_evidence_contract.json")
PHASE18_CONTRACT = Path("tools/bazel/manifests/phase18_cutover_review_contract.json")
PHASE19_CONTRACT = Path("tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json")
PHASE23_CONTRACT = Path("tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json")
PHASE24_CONTRACT = Path("tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase25")
REQUIRED_REQUIREMENT_IDS = {"EVID-03"}
V1_2_STATUSES = {"passed", "failed", "blocked", "exception-requested"}
BLOCKING_SOURCE_STATUSES = {
    "pending-live-input",
    "manual-live-service-required",
    "controlled-service-required",
    "blocked-credentials-unavailable",
    "blocked-endpoint-unavailable",
    "not-applicable-with-justification",
}
EXCEPTION_FIELDS = ["owner", "rationale", "evidence_ref", "revisit_condition"]
LIVE_PASS_EVIDENCE_TYPES = {"live-service-observation", "controlled-service-observation"}
SOURCE_CONTRACT_PASS_EVIDENCE_TYPES = {"source-contract-validation"}
FORBIDDEN_FIELD_NAMES = {
    "api_key",
    "api_key_header",
    "authorization_header",
    "bbf_payload",
    "bbf_payload_bytes",
    "certificate_bytes",
    "certificate_pem",
    "connect_token",
    "cookie_header",
    "credential",
    "credential_value",
    "dfu_payload",
    "dfu_payload_bytes",
    "fingerprint_value",
    "firmware_payload",
    "firmware_payload_bytes",
    "password",
    "password_value",
    "private_key",
    "proxy_authorization_header",
    "prusalink_password",
    "raw_crash_dump",
    "raw_http_log",
    "raw_production_payload",
    "raw_ram_dump",
    "raw_tls_log",
    "registration_code",
    "signing_key",
    "signing_key_value",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE),
    re.compile(
        r"\b(api_key(?:_header)?|authorization_header|certificate_(?:pem|bytes)|connect_token|cookie_header|credential_value|fingerprint_value|private_key|proxy_authorization_header|prusalink_password|raw_(?:crash_dump|http_log|production_payload|ram_dump|tls_log)|registration_code|signing_key(?:_value)?|tls_keylog|token_value|wifi_(?:credential|password)|firmware_payload(?:_bytes)?|bbf_payload(?:_bytes)?|dfu_payload(?:_bytes)?)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bConnect token\b", re.IGNORECASE),
    re.compile(r"\bregistration code\b", re.IGNORECASE),
    re.compile(r"\bWi-Fi credential\b", re.IGNORECASE),
    re.compile(r"\bPrusaLink password\b", re.IGNORECASE),
    re.compile(r"\bAPI key\b", re.IGNORECASE),
    re.compile(r"\bx-api-key\b", re.IGNORECASE),
    re.compile(r"\.(bin|bbf|dfu) payload\b", re.IGNORECASE),
)
OVERCLAIM_STRINGS = {
    "crash dump upload safe",
    "cutover complete",
    "final cutover complete",
    "live network verified locally",
    "live service passed locally",
    "production connect validated",
    "production prusalink validated",
    "proxy authentication supported",
    "proxy fully supported",
    "raw crash dump retained",
    "reference demotion approved",
    "reference removal complete",
    "release readiness proven",
    "release-candidate passed locally",
    "retained-code accepted by maintainer",
    "signing proof complete",
    "tls proof complete without operator evidence",
}
REQUIRED_SCENARIO_FIELDS = [
    "id",
    "title",
    "requirement_ids",
    "v1_requirement_ids",
    "source_contract_refs",
    "service_surface",
    "mode",
    "required_input_kind",
    "proof_scope",
    "expected_pass_semantics",
    "expected_failure_semantics",
    "expected_artifact_path",
    "retained_artifact_kind",
    "allowed_statuses",
    "operator_metadata_required",
    "redaction_required",
    "credential_boundary",
    "residual_non_live_gates",
    "unsupported_claims",
]
REQUIRED_PACKET_FIELDS = [
    "evidence_run_id",
    "phase_lifecycle_id",
    "firmware_identity",
    "operator",
    "started_at",
    "completed_at",
    "source_contract_ref",
    "scenario_results",
]
REQUIRED_ROW_FIELDS = [
    "scenario_id",
    "status",
    "source_status",
    "status_reason",
    "artifact_refs",
    "redaction_status",
    "source_ref_status",
    "device",
    "firmware_build",
    "operator",
    "timestamp",
    "residual_risk",
    "evidence_type",
    "service_surface",
    "mode",
    "redaction_summary",
]
CONDITIONAL_ROW_FIELDS = ["exception_request", "runtime_metadata"]


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(root: Path, path: str | Path) -> str:
    relative_path = Path(path)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: str | Path) -> dict[str, Any]:
    relative_path = Path(path)
    try:
        data = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{relative_path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(f"{relative_path.as_posix()} must contain a top-level object")
    return data


def write_json(root: Path, path: Path, data: Any) -> None:
    full_path = root / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_dict(row: dict[str, Any], field: str, row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_non_empty_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = require_list_of_strings(row, field, row_name)
    if not value:
        raise VerificationError(f"{row_name} {field} must contain at least one item")
    return value


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and row[field] in ("", None, {}, [])]
    if not missing and not empty:
        return
    parts: list[str] = []
    if missing:
        parts.append("missing required fields: " + ", ".join(missing))
    if empty:
        parts.append("empty required fields: " + ", ".join(empty))
    raise VerificationError(f"{row_name} " + "; ".join(parts))


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            errors.append(f"{path.as_posix()} contains forbidden evidence marker: {match.group(0)}")
    lowered = text.lower()
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase.lower() in lowered:
            errors.append(f"{path.as_posix()} contains non-local evidence overclaim: {phrase}")
    if errors:
        raise VerificationError("\n".join(errors))


def sanitized_for_artifact(path: Path, text: str) -> tuple[str, list[str]]:
    errors: list[str] = []
    sanitized = text
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(sanitized):
            errors.append(f"{path.as_posix()} contained forbidden evidence content")
            sanitized = pattern.sub("[REDACTED-FORBIDDEN-EVIDENCE]", sanitized)
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase.lower() in sanitized.lower():
            errors.append(f"{path.as_posix()} contained non-local evidence overclaim wording")
            sanitized = re.sub(re.escape(phrase), "[REDACTED-NON-LOCAL-OVERCLAIM]", sanitized, flags=re.IGNORECASE)
    return sanitized, errors


def normalized_field_name(field_name: str) -> str:
    return field_name.replace("-", "_").casefold()


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(key for key in value if normalized_field_name(key) in FORBIDDEN_FIELD_NAMES)
        if forbidden:
            forbidden_fields = ", ".join(forbidden)
            raise VerificationError(
                f"{path} contains forbidden evidence fields: {forbidden_fields}; contains forbidden evidence marker: {forbidden_fields}"
            )
        for key, child in value.items():
            reject_forbidden_field_names(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden_field_names(child, f"{path}[{index}]")


def require_repo_relative_under(path_value: str | Path, output_root: Path, row_name: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} path must be repo-relative and cannot traverse: {path_value}")
    try:
        relative_path.relative_to(output_root)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} path must stay under {output_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


def validate_artifact_ref(ref: str, row_name: str) -> str:
    if ref.startswith("external://phase25/"):
        if ref == "external://phase25/" or ".." in ref or ref.endswith("/"):
            raise VerificationError(f"{row_name} artifact ref is unsafe: {ref}")
        return ref
    return require_repo_relative_under(ref, DEFAULT_OUTPUT_DIR, row_name).as_posix()


def validate_artifact_refs(row: dict[str, Any], row_name: str) -> list[str]:
    refs = require_non_empty_list_of_strings(row, "artifact_refs", row_name)
    return [validate_artifact_ref(ref, row_name) for ref in refs]


def phase16_scenarios(contract: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = contract.get("scenarios")
    if not isinstance(scenarios, list):
        raise VerificationError(f"{PHASE16_CONTRACT.as_posix()} must contain a scenarios list")
    parsed: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise VerificationError(f"{PHASE16_CONTRACT.as_posix()} scenarios[{index}] must be an object")
        parsed.append(scenario)
    return parsed


def scenario_map(phase16: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {require_string(scenario, "id", "scenario"): scenario for scenario in phase16_scenarios(phase16)}


def source_status_vocabulary(phase16: dict[str, Any]) -> set[str]:
    return set(require_list_of_strings(phase16, "status_vocabulary", "phase16 contract"))


def source_contracts() -> set[str]:
    return {
        PHASE16_CONTRACT.as_posix(),
        PHASE18_CONTRACT.as_posix(),
        PHASE19_CONTRACT.as_posix(),
        PHASE23_CONTRACT.as_posix(),
        PHASE24_CONTRACT.as_posix(),
    }


def check_contract(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(root, CONTRACT_MANIFEST)
    phase16 = load_json(root, PHASE16_CONTRACT)
    for source_contract in [PHASE18_CONTRACT, PHASE19_CONTRACT, PHASE23_CONTRACT, PHASE24_CONTRACT]:
        load_json(root, source_contract)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase25_live_service_evidence_execution_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase25-live-service-evidence-execution",
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    try:
        status_vocabulary = set(require_list_of_strings(contract, "status_vocabulary", "contract"))
        blocking_source_statuses = set(require_list_of_strings(contract, "blocking_source_statuses", "contract"))
        required_scenario_ids = require_list_of_strings(contract, "required_phase16_scenario_ids", "contract")
        required_artifact_kinds = set(require_list_of_strings(contract, "required_artifact_kinds", "contract"))
        allowed_artifact_roots = set(require_list_of_strings(contract, "allowed_artifact_roots", "contract"))
        contract_source_refs = set(require_list_of_strings(contract, "source_contracts", "contract"))
        packet_fields = set(require_list_of_strings(contract, "evidence_packet_required_fields", "contract"))
        row_fields = set(require_list_of_strings(contract, "scenario_result_required_fields", "contract"))
        conditional_fields = set(require_list_of_strings(contract, "scenario_result_conditional_fields", "contract"))
        exception_fields = set(require_list_of_strings(contract, "exception_required_fields", "contract"))
        requirement_ids = set(require_list_of_strings(contract, "requirement_ids", "contract"))
        upstream = require_dict(contract, "upstream_result_row", "contract")
        upstream_requirement_ids = set(require_list_of_strings(upstream, "requirement_ids", "upstream_result_row"))
        scenarios = phase16_scenarios(phase16)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if status_vocabulary != V1_2_STATUSES:
        errors.append("status_vocabulary must match v1.2 live-service evidence statuses")
    if blocking_source_statuses != BLOCKING_SOURCE_STATUSES:
        errors.append("blocking_source_statuses must match Phase 16 non-passing live-service statuses")
    if requirement_ids != REQUIRED_REQUIREMENT_IDS or upstream_requirement_ids != REQUIRED_REQUIREMENT_IDS:
        errors.append("requirement_ids and upstream_result_row requirement_ids must be EVID-03")
    if contract_source_refs != source_contracts():
        errors.append("source_contracts must name Phase 16, Phase 18, Phase 19, Phase 23, and Phase 24 contracts")
    if allowed_artifact_roots != {DEFAULT_OUTPUT_DIR.as_posix() + "/", "external://phase25/"}:
        errors.append("allowed_artifact_roots must be build/ci-evidence/phase25/ and external://phase25/")
    missing_artifacts = sorted(
        {
            "machine-readable-run-manifest",
            "normalized-scenario-results",
            "redacted-live-service-summary",
            "source-contract-snapshot",
            "live-log-reference",
            "operator-evidence-input",
            "external-artifact-reference",
            "artifact-summary",
            "upstream-result-row",
        }
        - required_artifact_kinds
    )
    if missing_artifacts:
        errors.append("missing required artifact kinds: " + ", ".join(missing_artifacts))
    missing_packet_fields = sorted(set(REQUIRED_PACKET_FIELDS) - packet_fields)
    if missing_packet_fields:
        errors.append("missing required packet fields: " + ", ".join(missing_packet_fields))
    missing_row_fields = sorted(set(REQUIRED_ROW_FIELDS) - row_fields)
    if missing_row_fields:
        errors.append("missing required scenario result fields: " + ", ".join(missing_row_fields))
    missing_conditional_fields = sorted(set(CONDITIONAL_ROW_FIELDS) - conditional_fields)
    if missing_conditional_fields:
        errors.append("missing conditional scenario result fields: " + ", ".join(missing_conditional_fields))
    if exception_fields != set(EXCEPTION_FIELDS):
        errors.append("exception_required_fields must match owner, rationale, evidence_ref, and revisit_condition")
    if upstream.get("criterion_id") != "final-live-service-evidence":
        errors.append("upstream_result_row criterion_id must be final-live-service-evidence")
    if upstream.get("evidence_family") != "live-service":
        errors.append("upstream_result_row evidence_family must be live-service")
    scenario_ids = [require_string(scenario, "id", "scenario") for scenario in scenarios]
    if sorted(required_scenario_ids) != sorted(scenario_ids):
        errors.append("required_phase16_scenario_ids must exactly match Phase 16 scenarios")
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("Phase 16 scenario IDs must be unique")
    phase16_statuses = source_status_vocabulary(phase16)
    for scenario in scenarios:
        row_name = f"scenario {scenario.get('id', '<missing>')}"
        try:
            require_fields(scenario, REQUIRED_SCENARIO_FIELDS, row_name)
            allowed_statuses = set(require_list_of_strings(scenario, "allowed_statuses", row_name))
            if not allowed_statuses <= phase16_statuses:
                errors.append(f"{row_name} contains unknown Phase 16 allowed statuses")
            for source_ref in require_list_of_strings(scenario, "source_contract_refs", row_name):
                source_path = Path(source_ref.split("#", 1)[0])
                if "#" not in source_ref or source_path.is_absolute() or ".." in source_path.parts:
                    errors.append(f"{row_name} source_contract_refs must be repo-relative file#row-id refs")
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract, phase16


def validate_exception_request(row: dict[str, Any], row_name: str) -> dict[str, Any]:
    exception = require_dict(row, "exception_request", row_name)
    require_fields(exception, EXCEPTION_FIELDS, f"{row_name} exception_request")
    validate_artifact_ref(require_string(exception, "evidence_ref", f"{row_name} exception_request"), row_name)
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
        raise VerificationError(f"{row_name} source_status is not a Phase 16 status: {source_status}")
    allowed_source_statuses = set(require_list_of_strings(source_scenario, "allowed_statuses", row_name))
    if source_status not in allowed_source_statuses:
        raise VerificationError(f"{row_name} source_status is not allowed for this Phase 16 scenario: {source_status}")
    redaction_status = require_string(row, "redaction_status", row_name)
    source_ref_status = require_string(row, "source_ref_status", row_name)
    if status == "passed" and source_status not in {"passed", "source-contract-passed"}:
        raise VerificationError(f"{row_name} cannot pass with source_status={source_status}")
    if status == "passed" and redaction_status != "passed":
        raise VerificationError(f"{row_name} passed status requires redaction_status=passed")
    if status == "passed" and source_ref_status != "passed":
        raise VerificationError(f"{row_name} passed status requires source_ref_status=passed")
    proof_scope = require_string(source_scenario, "proof_scope", row_name)
    evidence_type = require_string(row, "evidence_type", row_name)
    if status == "passed" and proof_scope == "source-contract" and evidence_type not in SOURCE_CONTRACT_PASS_EVIDENCE_TYPES:
        raise VerificationError(f"{row_name} source-contract pass requires source-contract-validation evidence_type")
    if status == "passed" and proof_scope != "source-contract" and evidence_type not in LIVE_PASS_EVIDENCE_TYPES:
        raise VerificationError(f"{row_name} live-service pass requires live or controlled service observation evidence_type")
    service_surface = require_string(row, "service_surface", row_name)
    mode = require_string(row, "mode", row_name)
    expected_service_surface = require_string(source_scenario, "service_surface", row_name)
    expected_mode = require_string(source_scenario, "mode", row_name)
    if service_surface != expected_service_surface:
        raise VerificationError(f"{row_name} service_surface must be {expected_service_surface}")
    if mode != expected_mode:
        raise VerificationError(f"{row_name} mode must be {expected_mode}")
    exception_request = None
    if status == "exception-requested":
        exception_request = validate_exception_request(row, row_name)
    artifact_refs = validate_artifact_refs(row, row_name)
    runtime_metadata = row.get("runtime_metadata", {})
    if not isinstance(runtime_metadata, dict):
        raise VerificationError(f"{row_name} runtime_metadata must be an object when present")
    return {
        "artifact_refs": artifact_refs,
        "credential_boundary": require_string(source_scenario, "credential_boundary", row_name),
        "device": require_string(row, "device", row_name),
        "evidence_type": evidence_type,
        "exception_request": exception_request,
        "firmware_build": require_string(row, "firmware_build", row_name),
        "live_requirement_ids": require_list_of_strings(source_scenario, "requirement_ids", row_name),
        "mode": mode,
        "operator": require_string(row, "operator", row_name),
        "phase16_source_contract_refs": require_list_of_strings(source_scenario, "source_contract_refs", row_name),
        "proof_scope": proof_scope,
        "redaction_status": redaction_status,
        "redaction_summary": require_string(row, "redaction_summary", row_name),
        "requirement_ids": ["EVID-03"],
        "residual_non_live_gates": require_list_of_strings(source_scenario, "residual_non_live_gates", row_name),
        "residual_risk": require_string(row, "residual_risk", row_name),
        "retained_artifact_kind": require_string(source_scenario, "retained_artifact_kind", row_name),
        "runtime_metadata": runtime_metadata,
        "scenario_id": scenario_id,
        "service_surface": service_surface,
        "source_ref_status": source_ref_status,
        "source_status": source_status,
        "status": status,
        "status_reason": require_string(row, "status_reason", row_name),
        "timestamp": require_string(row, "timestamp", row_name),
        "title": require_string(source_scenario, "title", row_name),
        "unsupported_claims": require_list_of_strings(source_scenario, "unsupported_claims", row_name),
        "v1_requirement_ids": require_list_of_strings(source_scenario, "v1_requirement_ids", row_name),
    }


def load_evidence_rows(root: Path, input_path: Path, phase16: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if input_path.is_absolute() or ".." in input_path.parts:
        raise VerificationError("--evidence-input must be repo-relative and cannot traverse")
    input_text = read_text(root, input_path)
    try:
        data = json.loads(input_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"{input_path.as_posix()} is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    reject_forbidden_text(input_path, input_text)
    if not isinstance(data, dict):
        raise VerificationError("--evidence-input must contain a top-level object")
    packet = require_dict(data, "live_service_evidence_packet", "--evidence-input")
    require_fields(packet, REQUIRED_PACKET_FIELDS, "live_service_evidence_packet")
    require_dict(packet, "firmware_identity", "live_service_evidence_packet")
    if packet.get("phase") not in (None, PHASE):
        raise VerificationError(f"live_service_evidence_packet phase must be {PHASE}")
    if packet.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(f"live_service_evidence_packet phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
    if packet.get("source_contract_ref") != PHASE16_CONTRACT.as_posix():
        raise VerificationError(f"live_service_evidence_packet source_contract_ref must be {PHASE16_CONTRACT.as_posix()}")
    raw_rows = packet.get("scenario_results")
    if not isinstance(raw_rows, list):
        raise VerificationError("live_service_evidence_packet scenario_results must be a list")
    sources = scenario_map(phase16)
    expected_ids = set(sources)
    seen_ids: set[str] = set()
    rows: list[dict[str, Any]] = []
    for index, raw_row in enumerate(raw_rows):
        if not isinstance(raw_row, dict):
            raise VerificationError(f"scenario_results[{index}] must be an object")
        scenario_id = str(raw_row.get("scenario_id", ""))
        row_name = f"scenario_results[{index}] {scenario_id or '<missing>'}"
        if scenario_id not in sources:
            raise VerificationError(f"{row_name} does not resolve to a Phase 16 scenario")
        if scenario_id in seen_ids:
            raise VerificationError(f"duplicate scenario result: {scenario_id}")
        seen_ids.add(scenario_id)
        rows.append(validate_scenario_result(raw_row, row_name, source_status_vocabulary(phase16), sources[scenario_id]))
    missing = sorted(expected_ids - seen_ids)
    if missing:
        raise VerificationError("missing scenario results: " + ", ".join(missing))
    return packet, rows


def quick_rows(root: Path, output_dir: Path, phase16: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    logs_dir = root / output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    for scenario in phase16_scenarios(phase16):
        scenario_id = require_string(scenario, "id", "scenario")
        log_ref = output_dir / "logs" / f"{scenario_id}.log"
        allowed_source_statuses = require_list_of_strings(scenario, "allowed_statuses", "scenario")
        source_status = "pending-live-input" if "pending-live-input" in allowed_source_statuses else allowed_source_statuses[0]
        log_text = (
            f"phase: {PHASE}\n"
            f"scenario: {scenario_id}\n"
            "mode: quick-placeholder\n"
            "status: blocked\n"
            "reason: real live-service evidence input was not supplied.\n"
        )
        sanitized_log, redaction_errors = sanitized_for_artifact(log_ref, log_text)
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        (root / log_ref).write_text(sanitized_log, encoding="utf-8")
        rows.append(
            {
                "artifact_refs": [log_ref.as_posix()],
                "credential_boundary": require_string(scenario, "credential_boundary", "scenario"),
                "device": "quick-placeholder",
                "evidence_type": "source-contract-validation"
                if require_string(scenario, "proof_scope", "scenario") == "source-contract"
                else "controlled-service-observation",
                "exception_request": None,
                "firmware_build": "quick-placeholder",
                "live_requirement_ids": require_list_of_strings(scenario, "requirement_ids", "scenario"),
                "mode": require_string(scenario, "mode", "scenario"),
                "operator": "quick-placeholder",
                "phase16_source_contract_refs": require_list_of_strings(scenario, "source_contract_refs", "scenario"),
                "proof_scope": require_string(scenario, "proof_scope", "scenario"),
                "redaction_status": "passed",
                "redaction_summary": "quick placeholder retained no service secrets, credentials, payloads, or raw dumps",
                "requirement_ids": ["EVID-03"],
                "residual_non_live_gates": require_list_of_strings(scenario, "residual_non_live_gates", "scenario"),
                "residual_risk": "real live-service evidence input was not supplied",
                "retained_artifact_kind": require_string(scenario, "retained_artifact_kind", "scenario"),
                "runtime_metadata": {},
                "scenario_id": scenario_id,
                "service_surface": require_string(scenario, "service_surface", "scenario"),
                "source_ref_status": "passed",
                "source_status": source_status,
                "status": "blocked",
                "status_reason": "real live-service evidence input was not supplied",
                "timestamp": utc_now(),
                "title": require_string(scenario, "title", "scenario"),
                "unsupported_claims": require_list_of_strings(scenario, "unsupported_claims", "scenario"),
                "v1_requirement_ids": require_list_of_strings(scenario, "v1_requirement_ids", "scenario"),
            }
        )
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


def write_snapshot(root: Path, output_dir: Path, snapshot: Path) -> None:
    snapshot_text = read_text(root, snapshot)
    snapshot_path = output_dir / "contract-snapshots" / snapshot.name
    snapshot_digest = hashlib.sha256(snapshot_text.encode("utf-8")).hexdigest()
    write_json(
        root,
        snapshot_path,
        {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "source_contract_ref": snapshot.as_posix(),
            "source_sha256": snapshot_digest,
            "snapshot_kind": "source-contract-hash",
        },
    )


def write_retained_outputs(
    root: Path,
    output_dir: Path,
    rows: list[dict[str, Any]],
    command_mode: str,
    real_input_supplied: bool,
    maybe_packet: dict[str, Any] | None = None,
) -> None:
    output_root = root / output_dir
    (output_root / "logs").mkdir(parents=True, exist_ok=True)
    (output_root / "artifact-summaries").mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    status_summary = status_counts(rows)
    run_status = aggregate_status(rows)
    live_requirement_ids = sorted({requirement for row in rows for requirement in row["live_requirement_ids"]})
    requirement_coverage = {
        "EVID-03": sorted(str(row["scenario_id"]) for row in rows),
        **{
            requirement: sorted(str(row["scenario_id"]) for row in rows if requirement in row["live_requirement_ids"])
            for requirement in live_requirement_ids
        },
    }
    manifest = {
        "artifact_name": "phase25-live-service-evidence-execution",
        "command_mode": command_mode,
        "evidence_run_id": maybe_packet.get("evidence_run_id", "") if maybe_packet else "",
        "firmware_identity": maybe_packet.get("firmware_identity", {}) if maybe_packet else {},
        "generated_at": generated_at,
        "operator": maybe_packet.get("operator", "") if maybe_packet else "",
        "output_root": output_dir.as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "real_live_service_evidence_supplied": real_input_supplied,
        "requirement_coverage": requirement_coverage,
        "scenario_count": len(rows),
        "scenarios": rows,
        "source_contract_ref": PHASE16_CONTRACT.as_posix(),
        "status": run_status,
        "status_counts": status_summary,
    }
    normalized = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "real_live_service_evidence_supplied": real_input_supplied,
        "scenarios": [
            {
                "artifact_refs": row["artifact_refs"],
                "evidence_type": row["evidence_type"],
                "live_requirement_ids": row["live_requirement_ids"],
                "mode": row["mode"],
                "redaction_status": row["redaction_status"],
                "requirement_ids": row["requirement_ids"],
                "scenario_id": row["scenario_id"],
                "service_surface": row["service_surface"],
                "source_status": row["source_status"],
                "status": row["status"],
                "status_reason": row["status_reason"],
                "v1_requirement_ids": row["v1_requirement_ids"],
            }
            for row in rows
        ],
    }
    redacted_summary = {
        "generated_at": generated_at,
        "phase": PHASE,
        "real_live_service_evidence_supplied": real_input_supplied,
        "scenario_status": [
            {
                "mode": row["mode"],
                "scenario_id": row["scenario_id"],
                "service_surface": row["service_surface"],
                "source_status": row["source_status"],
                "status": row["status"],
                "status_reason": row["status_reason"],
            }
            for row in rows
        ],
        "status": run_status,
        "status_counts": status_summary,
        "unsupported_boundaries": sorted({claim for row in rows for claim in row["unsupported_claims"]}),
    }
    upstream_row = {
        "artifact_refs": [
            (output_dir / "normalized-live-service-results.json").as_posix(),
            (output_dir / "redacted-live-service-summary.json").as_posix(),
        ],
        "criterion_id": "final-live-service-evidence",
        "evidence_family": "live-service",
        "manifest_ref": (output_dir / "live-service-result-manifest.json").as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "real_live_service_evidence_supplied": real_input_supplied,
        "redaction_status": "passed",
        "requirement_ids": ["EVID-03"],
        "scenario_status_counts": status_summary,
        "source_ref_status": "passed",
        "status": run_status,
    }
    operator_template = {
        "live_service_evidence_packet": {
            "completed_at": "",
            "evidence_run_id": "",
            "firmware_identity": {
                "build_id": "",
                "firmware_basename": "",
            },
            "operator": "",
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "scenario_results": [
                {
                    "artifact_refs": [],
                    "device": "",
                    "evidence_type": "",
                    "firmware_build": "",
                    "mode": row["mode"],
                    "operator": "",
                    "redaction_status": "",
                    "redaction_summary": "",
                    "residual_risk": "",
                    "scenario_id": row["scenario_id"],
                    "service_surface": row["service_surface"],
                    "source_ref_status": "",
                    "source_status": "",
                    "status": "",
                    "status_reason": "",
                    "timestamp": "",
                }
                for row in rows
            ],
            "source_contract_ref": PHASE16_CONTRACT.as_posix(),
            "started_at": "",
        }
    }
    artifact_summary = {
        "allowed_artifact_roots": [DEFAULT_OUTPUT_DIR.as_posix() + "/", "external://phase25/"],
        "generated_at": generated_at,
        "phase": PHASE,
        "retained_files": [
            (output_dir / "live-service-result-manifest.json").as_posix(),
            (output_dir / "normalized-live-service-results.json").as_posix(),
            (output_dir / "redacted-live-service-summary.json").as_posix(),
            (output_dir / "upstream-live-service-result-row.json").as_posix(),
            (output_dir / "operator-live-service-template.json").as_posix(),
        ],
        "scenario_count": len(rows),
        "status": run_status,
    }
    write_json(root, output_dir / "live-service-result-manifest.json", manifest)
    write_json(root, output_dir / "normalized-live-service-results.json", normalized)
    write_json(root, output_dir / "redacted-live-service-summary.json", redacted_summary)
    write_json(root, output_dir / "upstream-live-service-result-row.json", upstream_row)
    write_json(root, output_dir / "upstream-live-result-row.json", upstream_row)
    write_json(root, output_dir / "operator-live-service-template.json", operator_template)
    write_json(root, output_dir / "operator-evidence-input-template.json", operator_template)
    write_json(root, output_dir / "artifact-summaries" / "live-service-artifact-summary.json", artifact_summary)
    for snapshot in [CONTRACT_MANIFEST, PHASE16_CONTRACT]:
        write_snapshot(root, output_dir, snapshot)
    check_security(root)


def security_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    output_root = root / DEFAULT_OUTPUT_DIR
    if output_root.exists():
        paths.extend(path.relative_to(root) for path in sorted(output_root.rglob("*")) if path.is_file())
    return [path for path in paths if (root / path).exists()]


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in security_paths(root):
        try:
            reject_forbidden_text(path, read_text(root, path))
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def require_file_contains(root: Path, path: Path, needles: list[str]) -> list[str]:
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    return [f"{path.as_posix()} missing required wiring text: {needle}" for needle in needles if needle not in text]


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase25_source_ref_manifests"',
                'name = "phase25_verify"',
                'name = "phase25_verify_tests"',
                "phase25_live_service_evidence_execution.py",
                "phase25_live_service_evidence_execution_test.py",
                "phase25_live_service_evidence_execution_contract.json",
                "//:phase25_live_service_evidence_execution_docs",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase25_live_service_evidence_execution_docs"',
                'name = "phase25_verify"',
                'name = "phase25_verify_tests"',
                ".planning/phases/25-live-service-evidence-execution/25-01-PLAN.md",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase25_verify)",
                "python3 tools/bazel/phase25_live_service_evidence_execution.py --wiring-only",
                "python3 tools/bazel/phase25_live_service_evidence_execution.py --quick --output-dir build/ci-evidence/phase25",
                "phase25_verify_tests)",
                "python3 tools/bazel/phase25_live_service_evidence_execution_test.py",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase25-verify:",
                "bazel run //tools/bazel:phase25_verify_tests",
                "bazel run //tools/bazel:phase25_verify",
            ],
        )
    )
    if errors:
        raise VerificationError("\n".join(errors))


def reset_output_root(root: Path, output_dir: Path) -> Path:
    output_relative = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    output_root = root / output_relative
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    return output_relative


def run_or_raise(args: argparse.Namespace) -> None:
    root = ROOT
    contract, phase16 = check_contract(root)
    output_dir = Path(args.output_dir)
    if args.contract_only:
        return
    if args.security_only:
        check_security(root)
        return
    if args.wiring_only:
        check_wiring(root)
        return
    if args.quick:
        output_relative = reset_output_root(root, output_dir)
        rows = quick_rows(root, output_relative, phase16)
        write_retained_outputs(root, output_relative, rows, "quick-placeholder", False)
        return
    if args.evidence_input:
        output_relative = reset_output_root(root, output_dir)
        packet, rows = load_evidence_rows(root, Path(args.evidence_input), phase16)
        write_retained_outputs(root, output_relative, rows, "evidence-input", True, packet)
        return
    check_security(root)
    check_wiring(root)
    _ = contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and retain Phase 25 live-service evidence execution results.")
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--evidence-input")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args()


def main() -> int:
    try:
        run_or_raise(parse_args())
    except VerificationError as error:
        print(f"Phase 25 live-service evidence execution verification failed:\n{error}", file=sys.stderr)
        return 1
    print("Phase 25 live-service evidence execution verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
