#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "16-live-network-and-transfer-qualification"
PHASE_LIFECYCLE_ID = "16-2026-06-18T01-09-34"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase16")
REQUIRED_REQUIREMENT_IDS = {"LIVE-01", "LIVE-02", "LIVE-03"}
REQUIRED_SCENARIO_IDS = {
    "live-connect-registration-token-fingerprint",
    "live-connect-telemetry-events",
    "live-connect-websocket-command-channel",
    "live-connect-proxy-limitation-tunnel",
    "live-connect-transfer-download-command",
    "live-wui-prusalink-api-v1",
    "live-wui-digest-auth",
    "live-wui-api-key-auth",
    "live-network-sntp-client",
    "live-network-mdns-announcement",
    "live-network-syslog-metrics-udp",
    "live-wui-upload-transfer",
    "live-tls-certificate-verification",
    "live-custom-ca-certificate-boundary",
    "live-negative-protocol-wui-http",
    "live-negative-protocol-connect-command",
    "live-long-transfer-connect-download",
    "live-long-transfer-wui-upload",
    "live-crash-dump-upload-redaction",
    "live-contract-traceability-redaction-boundary",
}
REQUIRED_SERVICE_SURFACES = {
    "connect-registration",
    "connect-telemetry-events",
    "connect-command-channel",
    "connect-proxy",
    "connect-transfer-download",
    "prusalink-api-v1",
    "wui-digest-auth",
    "wui-api-key-auth",
    "sntp-client",
    "mdns-responder",
    "syslog-and-metrics",
    "wui-upload-transfer",
    "connect-tls-policy",
    "custom-connect-ca",
    "wui-negative-protocol",
    "connect-negative-command",
    "connect-long-transfer",
    "wui-long-transfer",
    "crash-dump-upload",
    "contract-traceability-redaction",
}
STATUS_VOCABULARY = [
    "passed",
    "failed",
    "pending-live-input",
    "manual-live-service-required",
    "controlled-service-required",
    "blocked-credentials-unavailable",
    "blocked-endpoint-unavailable",
    "not-applicable-with-justification",
    "source-contract-passed",
    "rejected-redaction",
    "rejected-overclaim",
]
LIVE_ALLOWED_STATUSES = {
    "pending-live-input",
    "manual-live-service-required",
    "controlled-service-required",
    "blocked-credentials-unavailable",
    "blocked-endpoint-unavailable",
    "not-applicable-with-justification",
    "passed",
    "failed",
}
SOURCE_CONTRACT_ALLOWED_STATUSES = {
    "source-contract-passed",
    "failed",
    "rejected-redaction",
    "rejected-overclaim",
}
LIVE_PASS_EVIDENCE_TYPES = {
    "live-service-observation",
    "controlled-service-observation",
}
REQUIRED_OPERATOR_FIELDS = [
    "device",
    "firmware_build",
    "operator",
    "timestamp",
    "scenario_id",
    "result",
    "evidence_type",
    "service_surface",
    "mode",
    "artifact_refs",
    "redaction_summary",
    "residual_risk",
]
OPERATOR_ALLOWED_RESULTS = [
    "passed",
    "failed",
    "manual-live-service-required",
    "controlled-service-required",
    "blocked-credentials-unavailable",
    "blocked-endpoint-unavailable",
    "not-applicable-with-justification",
]
REQUIRED_ARTIFACT_KINDS = {
    "machine-readable-run-manifest",
    "normalized-scenario-results",
    "redacted-network-summary",
    "source-contract-snapshot",
    "live-log-reference",
    "operator-evidence-input",
    "external-artifact-reference",
}
REQUIRED_SCENARIO_FIELDS = [
    "id",
    "title",
    "requirement_ids",
    "v1_requirement_ids",
    "source_contract_refs",
    "source_doc_refs",
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
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-block",
     re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
    ("fingerprint-line", re.compile(r"\bFingerprint:\s*\S+", re.IGNORECASE)),
    (
        "forbidden-raw-field-name",
        re.compile(
            r"\b(certificate_pem|certificate_bytes|private_key|signing_key|token_value|connect_token|registration_code|fingerprint_value|wifi_password|prusalink_password|api_key|raw_http_log|raw_tls_log|tls_keylog|SSLKEYLOGFILE|raw_crash_dump|raw_ram_dump|memory_dump|raw_production_payload|firmware_payload|bbf_payload|dfu_payload)\b",
            re.IGNORECASE,
        ),
    ),
    ("connect-token-phrase", re.compile(r"\bConnect token\b", re.IGNORECASE)),
    ("registration-code-phrase",
     re.compile(r"\bregistration code\b", re.IGNORECASE)),
    ("wifi-credential-phrase",
     re.compile(r"\bWi-Fi credential\b", re.IGNORECASE)),
    ("prusalink-password-phrase",
     re.compile(r"\bPrusaLink password\b", re.IGNORECASE)),
    ("api-key-phrase", re.compile(r"\bAPI key\b", re.IGNORECASE)),
    (
        "credential-assignment",
        re.compile(
            r"(?:^|[\s,{])['\"]?"
            r"(api[-_]?key|(?:[A-Za-z0-9]+[-_])+(?:token|password|secret)|(?:token|password|secret)(?:[-_][A-Za-z0-9]+)?)"
            r"['\"]?\s*[:=]\s*['\"]?[^'\"\s,}]+",
            re.IGNORECASE,
        ),
    ),
    (
        "credential-header-assignment",
        re.compile(
            r"(?:^|[\s,{])['\"]?"
            r"((?:proxy[-_])?authorization(?:[-_]header)?|(?:set[-_])?cookie(?:[-_]header)?)"
            r"['\"]?\s*[:=]\s*['\"]?[^'\"\n,}]+",
            re.IGNORECASE,
        ),
    ),
    ("api-key-header", re.compile(r"\bx-api-key\b", re.IGNORECASE)),
    ("firmware-payload-marker",
     re.compile(r"\.(bin|bbf|dfu) payload\b", re.IGNORECASE)),
)
OVERCLAIM_STRINGS = {
    "live service passed locally",
    "live network verified locally",
    "production connect validated",
    "production prusalink validated",
    "tls proof complete without operator evidence",
    "proxy fully supported",
    "proxy authentication supported",
    "crash dump upload safe",
    "raw crash dump retained",
    "final cutover complete",
    "cutover complete",
    "release readiness proven",
    "release-candidate passed locally",
    "signing proof complete",
    "retained-code accepted by maintainer",
    "reference demotion approved",
    "reference removal complete",
}


class VerificationError(Exception):
    pass


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


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_iso_8601_utc_timestamp(row: dict[str, Any], field: str,
                                   row_name: str) -> str:
    timestamp_text = require_string(row, field, row_name)
    try:
        parsed_timestamp = datetime.fromisoformat(
            timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(
            f"{row_name} {field} must be ISO-8601 UTC") from error
    if parsed_timestamp.tzinfo is None or parsed_timestamp.utcoffset(
    ) != timezone.utc.utcoffset(parsed_timestamp):
        raise VerificationError(f"{row_name} {field} must be ISO-8601 UTC")
    return timestamp_text


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_dict(row: dict[str, Any], field: str,
                 row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields
        if field in row and row[field] in ("", None, [], {})
    ]
    if not missing and not empty:
        return
    details: list[str] = []
    if missing:
        details.append("missing required fields: " + ", ".join(missing))
    if empty:
        details.append("empty required fields: " + ", ".join(empty))
    raise VerificationError(f"{row_name} " + "; ".join(details))


def require_repo_relative_under(path_value: str | Path,
                                output_root: str | Path,
                                row_name: str) -> Path:
    relative_path = Path(path_value)
    expected_root = Path(output_root)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} path must be repo-relative and cannot traverse: {path_value}"
        )
    try:
        relative_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} path must stay under {expected_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


def contained_output_dir(root: Path, output_dir: str | Path) -> Path:
    relative_path = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR,
                                                "--output-dir")
    expected_root = root.resolve() / DEFAULT_OUTPUT_DIR
    full_output_dir = (root / relative_path).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return full_output_dir


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            errors.append(
                f"{path.as_posix()} contains forbidden evidence marker: {label}"
            )
    lowered = text.lower()
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase in lowered:
            errors.append(
                f"{path.as_posix()} contains non-local evidence overclaim: {phrase}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def contract_scenarios(contract: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = contract.get("scenarios")
    if not isinstance(scenarios, list):
        raise VerificationError(
            f"{CONTRACT_MANIFEST.as_posix()} must contain a scenarios list")
    parsed: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} scenarios[{index}] must be an object"
            )
        parsed.append(scenario)
    return parsed


def row_id_exists(data: Any, row_id: str) -> bool:
    if isinstance(data, dict):
        if data.get("id") == row_id:
            return True
        return any(row_id_exists(value, row_id) for value in data.values())
    if isinstance(data, list):
        return any(row_id_exists(value, row_id) for value in data)
    return False


def resolve_source_ref(root: Path, source_ref: str, row_name: str) -> None:
    if "#" not in source_ref:
        raise VerificationError(
            f"{row_name} source ref must use file#row-id: {source_ref}")
    path_text, row_id = source_ref.split("#", 1)
    if not path_text or not row_id:
        raise VerificationError(
            f"{row_name} source ref must include file and row ID: {source_ref}"
        )
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} source ref must be repo-relative: {source_ref}")
    data = load_json(root, relative_path)
    if not row_id_exists(data, row_id):
        raise VerificationError(
            f"{row_name} source ref row not found: {source_ref}")


def validate_doc_ref(root: Path, source_doc_ref: str, row_name: str) -> None:
    if "#" not in source_doc_ref:
        raise VerificationError(
            f"{row_name} source doc ref must use file#heading: {source_doc_ref}"
        )
    path_text, anchor = source_doc_ref.split("#", 1)
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} source doc ref must be repo-relative: {source_doc_ref}"
        )
    text = read_text(root, relative_path)
    if anchor and anchor.lower() not in text.lower():
        raise VerificationError(
            f"{row_name} source doc ref anchor not found: {source_doc_ref}")


def check_operator_schema(contract: dict[str, Any], errors: list[str]) -> None:
    try:
        schema = require_dict(contract, "operator_input_schema", "contract")
        required_fields = require_list_of_strings(schema, "required_fields",
                                                  "operator_input_schema")
        allowed_results = require_list_of_strings(schema, "allowed_results",
                                                  "operator_input_schema")
        artifact_ref_root = require_string(schema, "artifact_ref_root",
                                           "operator_input_schema")
    except VerificationError as error:
        errors.append(str(error))
        return
    if required_fields != REQUIRED_OPERATOR_FIELDS:
        errors.append(
            "operator_input_schema required_fields must match Phase 16 operator metadata fields"
        )
    if allowed_results != OPERATOR_ALLOWED_RESULTS:
        errors.append(
            "operator_input_schema allowed_results must match Phase 16 allowed operator results"
        )
    if artifact_ref_root != DEFAULT_OUTPUT_DIR.as_posix():
        errors.append(
            f"operator_input_schema artifact_ref_root must be {DEFAULT_OUTPUT_DIR.as_posix()}"
        )


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase16_live_network_evidence_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase16-live-network-evidence",
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    try:
        status_vocabulary = require_list_of_strings(contract,
                                                    "status_vocabulary",
                                                    "contract")
        artifact_kinds = set(
            require_list_of_strings(contract, "required_artifact_kinds",
                                    "contract"))
        scenarios = contract_scenarios(contract)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if status_vocabulary != STATUS_VOCABULARY:
        errors.append(
            "status_vocabulary does not match the Phase 16 vocabulary")
    missing_artifact_kinds = sorted(REQUIRED_ARTIFACT_KINDS - artifact_kinds)
    if missing_artifact_kinds:
        errors.append("missing required artifact kinds: " +
                      ", ".join(missing_artifact_kinds))
    check_operator_schema(contract, errors)

    scenario_ids = [str(scenario.get("id")) for scenario in scenarios]
    missing_scenarios = sorted(REQUIRED_SCENARIO_IDS - set(scenario_ids))
    extra_scenarios = sorted(set(scenario_ids) - REQUIRED_SCENARIO_IDS)
    if missing_scenarios:
        errors.append("missing required scenarios: " +
                      ", ".join(missing_scenarios))
    if extra_scenarios:
        errors.append("unexpected scenarios: " + ", ".join(extra_scenarios))
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("duplicate scenario IDs are not allowed")

    covered_requirements: set[str] = set()
    covered_surfaces: set[str] = set()
    for scenario in scenarios:
        row_name = str(scenario.get("id", "unknown scenario"))
        for field in REQUIRED_SCENARIO_FIELDS:
            if field not in scenario:
                errors.append(f"{row_name} missing required field: {field}")
        try:
            scenario_id = require_string(scenario, "id", row_name)
            require_string(scenario, "title", row_name)
            requirement_ids = set(
                require_list_of_strings(scenario, "requirement_ids", row_name))
            require_list_of_strings(scenario, "v1_requirement_ids", row_name)
            source_refs = require_list_of_strings(scenario,
                                                  "source_contract_refs",
                                                  row_name)
            source_doc_refs = require_list_of_strings(scenario,
                                                      "source_doc_refs",
                                                      row_name)
            service_surface = require_string(scenario, "service_surface",
                                             row_name)
            mode = require_string(scenario, "mode", row_name)
            require_string(scenario, "required_input_kind", row_name)
            proof_scope = require_string(scenario, "proof_scope", row_name)
            require_string(scenario, "expected_pass_semantics", row_name)
            require_string(scenario, "expected_failure_semantics", row_name)
            artifact_path = require_string(scenario, "expected_artifact_path",
                                           row_name)
            retained_artifact_kind = require_string(scenario,
                                                    "retained_artifact_kind",
                                                    row_name)
            allowed_statuses = set(
                require_list_of_strings(scenario, "allowed_statuses",
                                        row_name))
            operator_metadata = require_list_of_strings(
                scenario, "operator_metadata_required", row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue

        if scenario_id != row_name:
            errors.append(f"{row_name} id mismatch")
        unknown_requirements = sorted(requirement_ids -
                                      REQUIRED_REQUIREMENT_IDS)
        if unknown_requirements:
            errors.append(
                f"{row_name} uses unknown requirement IDs: {', '.join(unknown_requirements)}"
            )
        covered_requirements.update(requirement_ids)
        covered_surfaces.add(service_surface)
        for source_ref in source_refs:
            try:
                resolve_source_ref(root, source_ref, row_name)
            except VerificationError as error:
                errors.append(str(error))
        for source_doc_ref in source_doc_refs:
            try:
                validate_doc_ref(root, source_doc_ref, row_name)
            except VerificationError as error:
                errors.append(str(error))
        try:
            require_repo_relative_under(artifact_path, DEFAULT_OUTPUT_DIR,
                                        row_name)
        except VerificationError as error:
            errors.append(str(error))
        if retained_artifact_kind not in REQUIRED_ARTIFACT_KINDS:
            errors.append(
                f"{row_name} retained_artifact_kind is not declared: {retained_artifact_kind}"
            )
        if not allowed_statuses <= set(STATUS_VOCABULARY):
            errors.append(
                f"{row_name} allowed_statuses contains unknown statuses")
        if proof_scope == "live-service-observation":
            missing_statuses = sorted(LIVE_ALLOWED_STATUSES - allowed_statuses)
            if missing_statuses:
                errors.append(
                    f"{row_name} live-service allowed_statuses missing: {', '.join(missing_statuses)}"
                )
            if mode != "live-or-controlled-service":
                errors.append(
                    f"{row_name} live-service rows must use live-or-controlled-service mode"
                )
            if scenario.get("default_status") == "passed":
                errors.append(
                    f"{row_name} default_status cannot be passed without operator evidence"
                )
        elif proof_scope == "source-contract":
            missing_statuses = sorted(SOURCE_CONTRACT_ALLOWED_STATUSES -
                                      allowed_statuses)
            if missing_statuses:
                errors.append(
                    f"{row_name} source-contract allowed_statuses missing: {', '.join(missing_statuses)}"
                )
            if mode != "local-contract-validation":
                errors.append(
                    f"{row_name} source-contract rows must use local-contract-validation mode"
                )
        else:
            errors.append(
                f"{row_name} proof_scope must be live-service-observation or source-contract"
            )
        if operator_metadata != REQUIRED_OPERATOR_FIELDS:
            errors.append(
                f"{row_name} operator metadata must include: {', '.join(REQUIRED_OPERATOR_FIELDS)}"
            )
        if scenario.get("redaction_required") is not True:
            errors.append(f"{row_name} redaction_required must be true")
        credential_boundary = scenario.get("credential_boundary")
        residual_gates = scenario.get("residual_non_live_gates")
        unsupported_claims = scenario.get("unsupported_claims")
        if not credential_boundary:
            errors.append(f"{row_name} credential_boundary must not be empty")
        if not isinstance(residual_gates, list) or not residual_gates:
            errors.append(
                f"{row_name} residual_non_live_gates must not be empty")
        if not isinstance(unsupported_claims, list) or not unsupported_claims:
            errors.append(f"{row_name} unsupported_claims must not be empty")

    missing_requirements = sorted(REQUIRED_REQUIREMENT_IDS -
                                  covered_requirements)
    if missing_requirements:
        errors.append("missing LIVE requirement coverage: " +
                      ", ".join(missing_requirements))
    missing_surfaces = sorted(REQUIRED_SERVICE_SURFACES - covered_surfaces)
    if missing_surfaces:
        errors.append("missing required service surface coverage: " +
                      ", ".join(missing_surfaces))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract
