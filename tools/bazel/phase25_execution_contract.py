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
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json"
)
PHASE16_CONTRACT = Path(
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json")
PHASE18_CONTRACT = Path(
    "tools/bazel/manifests/phase18_cutover_review_contract.json")
PHASE19_CONTRACT = Path(
    "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json")
PHASE23_CONTRACT = Path(
    "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json")
PHASE24_CONTRACT = Path(
    "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json"
)
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
LIVE_PASS_EVIDENCE_TYPES = {
    "live-service-observation", "controlled-service-observation"
}
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
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(root: Path, path: str | Path) -> str:
    relative_path = Path(path)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: str | Path) -> dict[str, Any]:
    relative_path = Path(path)
    try:
        data = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{relative_path.as_posix()} is not valid JSON: {error}"
        ) from error
    if not isinstance(data, dict):
        raise VerificationError(
            f"{relative_path.as_posix()} must contain a top-level object")
    return data


def write_json(root: Path, path: Path, data: Any) -> None:
    full_path = root / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_dict(row: dict[str, Any], field: str,
                 row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_non_empty_list_of_strings(row: dict[str, Any], field: str,
                                      row_name: str) -> list[str]:
    value = require_list_of_strings(row, field, row_name)
    if not value:
        raise VerificationError(
            f"{row_name} {field} must contain at least one item")
    return value


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields
        if field in row and row[field] in ("", None, {}, [])
    ]
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
            errors.append(
                f"{path.as_posix()} contains forbidden evidence marker: {match.group(0)}"
            )
    lowered = text.lower()
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase.lower() in lowered:
            errors.append(
                f"{path.as_posix()} contains non-local evidence overclaim: {phrase}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def sanitized_for_artifact(path: Path, text: str) -> tuple[str, list[str]]:
    errors: list[str] = []
    sanitized = text
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(sanitized):
            errors.append(
                f"{path.as_posix()} contained forbidden evidence content")
            sanitized = pattern.sub("[REDACTED-FORBIDDEN-EVIDENCE]", sanitized)
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase.lower() in sanitized.lower():
            errors.append(
                f"{path.as_posix()} contained non-local evidence overclaim wording"
            )
            sanitized = re.sub(re.escape(phrase),
                               "[REDACTED-NON-LOCAL-OVERCLAIM]",
                               sanitized,
                               flags=re.IGNORECASE)
    return sanitized, errors


def normalized_field_name(field_name: str) -> str:
    return field_name.replace("-", "_").casefold()


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(
            key for key in value
            if normalized_field_name(key) in FORBIDDEN_FIELD_NAMES)
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


def require_repo_relative_under(path_value: str | Path, output_root: Path,
                                row_name: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} path must be repo-relative and cannot traverse: {path_value}"
        )
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
            raise VerificationError(
                f"{row_name} artifact ref is unsafe: {ref}")
        return ref
    return require_repo_relative_under(ref, DEFAULT_OUTPUT_DIR,
                                       row_name).as_posix()


def validate_artifact_refs(row: dict[str, Any], row_name: str) -> list[str]:
    refs = require_non_empty_list_of_strings(row, "artifact_refs", row_name)
    return [validate_artifact_ref(ref, row_name) for ref in refs]


def phase16_scenarios(contract: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = contract.get("scenarios")
    if not isinstance(scenarios, list):
        raise VerificationError(
            f"{PHASE16_CONTRACT.as_posix()} must contain a scenarios list")
    parsed: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise VerificationError(
                f"{PHASE16_CONTRACT.as_posix()} scenarios[{index}] must be an object"
            )
        parsed.append(scenario)
    return parsed


def scenario_map(phase16: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        require_string(scenario, "id", "scenario"): scenario
        for scenario in phase16_scenarios(phase16)
    }


def source_status_vocabulary(phase16: dict[str, Any]) -> set[str]:
    return set(
        require_list_of_strings(phase16, "status_vocabulary",
                                "phase16 contract"))


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
    for source_contract in [
            PHASE18_CONTRACT, PHASE19_CONTRACT, PHASE23_CONTRACT,
            PHASE24_CONTRACT
    ]:
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
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    try:
        status_vocabulary = set(
            require_list_of_strings(contract, "status_vocabulary", "contract"))
        blocking_source_statuses = set(
            require_list_of_strings(contract, "blocking_source_statuses",
                                    "contract"))
        required_scenario_ids = require_list_of_strings(
            contract, "required_phase16_scenario_ids", "contract")
        required_artifact_kinds = set(
            require_list_of_strings(contract, "required_artifact_kinds",
                                    "contract"))
        allowed_artifact_roots = set(
            require_list_of_strings(contract, "allowed_artifact_roots",
                                    "contract"))
        contract_source_refs = set(
            require_list_of_strings(contract, "source_contracts", "contract"))
        packet_fields = set(
            require_list_of_strings(contract,
                                    "evidence_packet_required_fields",
                                    "contract"))
        row_fields = set(
            require_list_of_strings(contract,
                                    "scenario_result_required_fields",
                                    "contract"))
        conditional_fields = set(
            require_list_of_strings(contract,
                                    "scenario_result_conditional_fields",
                                    "contract"))
        exception_fields = set(
            require_list_of_strings(contract, "exception_required_fields",
                                    "contract"))
        requirement_ids = set(
            require_list_of_strings(contract, "requirement_ids", "contract"))
        upstream = require_dict(contract, "upstream_result_row", "contract")
        upstream_requirement_ids = set(
            require_list_of_strings(upstream, "requirement_ids",
                                    "upstream_result_row"))
        scenarios = phase16_scenarios(phase16)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if status_vocabulary != V1_2_STATUSES:
        errors.append(
            "status_vocabulary must match v1.2 live-service evidence statuses")
    if blocking_source_statuses != BLOCKING_SOURCE_STATUSES:
        errors.append(
            "blocking_source_statuses must match Phase 16 non-passing live-service statuses"
        )
    if requirement_ids != REQUIRED_REQUIREMENT_IDS or upstream_requirement_ids != REQUIRED_REQUIREMENT_IDS:
        errors.append(
            "requirement_ids and upstream_result_row requirement_ids must be EVID-03"
        )
    if contract_source_refs != source_contracts():
        errors.append(
            "source_contracts must name Phase 16, Phase 18, Phase 19, Phase 23, and Phase 24 contracts"
        )
    if allowed_artifact_roots != {
            DEFAULT_OUTPUT_DIR.as_posix() + "/", "external://phase25/"
    }:
        errors.append(
            "allowed_artifact_roots must be build/ci-evidence/phase25/ and external://phase25/"
        )
    missing_artifacts = sorted({
        "machine-readable-run-manifest",
        "normalized-scenario-results",
        "redacted-live-service-summary",
        "source-contract-snapshot",
        "live-log-reference",
        "operator-evidence-input",
        "external-artifact-reference",
        "artifact-summary",
        "upstream-result-row",
    } - required_artifact_kinds)
    if missing_artifacts:
        errors.append("missing required artifact kinds: " +
                      ", ".join(missing_artifacts))
    missing_packet_fields = sorted(set(REQUIRED_PACKET_FIELDS) - packet_fields)
    if missing_packet_fields:
        errors.append("missing required packet fields: " +
                      ", ".join(missing_packet_fields))
    missing_row_fields = sorted(set(REQUIRED_ROW_FIELDS) - row_fields)
    if missing_row_fields:
        errors.append("missing required scenario result fields: " +
                      ", ".join(missing_row_fields))
    missing_conditional_fields = sorted(
        set(CONDITIONAL_ROW_FIELDS) - conditional_fields)
    if missing_conditional_fields:
        errors.append("missing conditional scenario result fields: " +
                      ", ".join(missing_conditional_fields))
    if exception_fields != set(EXCEPTION_FIELDS):
        errors.append(
            "exception_required_fields must match owner, rationale, evidence_ref, and revisit_condition"
        )
    if upstream.get("criterion_id") != "final-live-service-evidence":
        errors.append(
            "upstream_result_row criterion_id must be final-live-service-evidence"
        )
    if upstream.get("evidence_family") != "live-service":
        errors.append(
            "upstream_result_row evidence_family must be live-service")
    scenario_ids = [
        require_string(scenario, "id", "scenario") for scenario in scenarios
    ]
    if sorted(required_scenario_ids) != sorted(scenario_ids):
        errors.append(
            "required_phase16_scenario_ids must exactly match Phase 16 scenarios"
        )
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("Phase 16 scenario IDs must be unique")
    phase16_statuses = source_status_vocabulary(phase16)
    for scenario in scenarios:
        row_name = f"scenario {scenario.get('id', '<missing>')}"
        try:
            require_fields(scenario, REQUIRED_SCENARIO_FIELDS, row_name)
            allowed_statuses = set(
                require_list_of_strings(scenario, "allowed_statuses",
                                        row_name))
            if not allowed_statuses <= phase16_statuses:
                errors.append(
                    f"{row_name} contains unknown Phase 16 allowed statuses")
            for source_ref in require_list_of_strings(scenario,
                                                      "source_contract_refs",
                                                      row_name):
                source_path = Path(source_ref.split("#", 1)[0])
                if "#" not in source_ref or source_path.is_absolute(
                ) or ".." in source_path.parts:
                    errors.append(
                        f"{row_name} source_contract_refs must be repo-relative file#row-id refs"
                    )
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract, phase16
