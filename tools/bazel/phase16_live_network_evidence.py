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
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase16_live_network_evidence_contract.json")
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
SOURCE_REF_MANIFESTS = [
    "tools/bazel/manifests/phase9_connect_contracts.json",
    "tools/bazel/manifests/phase9_wui_contracts.json",
    "tools/bazel/manifests/phase9_network_service_contracts.json",
    "tools/bazel/manifests/phase9_transfer_contracts.json",
    "tools/bazel/manifests/phase9_network_concern_dispositions.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json",
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json",
]
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
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE),
    re.compile(r"\bFingerprint:\s*\S+", re.IGNORECASE),
    re.compile(
        r"\b(certificate_pem|certificate_bytes|private_key|signing_key|token_value|connect_token|registration_code|fingerprint_value|wifi_password|prusalink_password|api_key|raw_http_log|raw_tls_log|tls_keylog|SSLKEYLOGFILE|raw_crash_dump|raw_ram_dump|memory_dump|raw_production_payload|firmware_payload|bbf_payload|dfu_payload)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bConnect token\b", re.IGNORECASE),
    re.compile(r"\bregistration code\b", re.IGNORECASE),
    re.compile(r"\bWi-Fi credential\b", re.IGNORECASE),
    re.compile(r"\bPrusaLink password\b", re.IGNORECASE),
    re.compile(r"\bAPI key\b", re.IGNORECASE),
    re.compile(r"\bAuthorization:", re.IGNORECASE),
    re.compile(r"\bCookie:", re.IGNORECASE),
    re.compile(r"\bSet-Cookie:", re.IGNORECASE),
    re.compile(r"\bx-api-key\b", re.IGNORECASE),
    re.compile(r"\.(bin|bbf|dfu) payload\b", re.IGNORECASE),
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


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_dict(row: dict[str, Any], field: str, row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and row[field] in ("", None, [], {})]
    if not missing and not empty:
        return
    details: list[str] = []
    if missing:
        details.append("missing required fields: " + ", ".join(missing))
    if empty:
        details.append("empty required fields: " + ", ".join(empty))
    raise VerificationError(f"{row_name} " + "; ".join(details))


def require_repo_relative_under(path_value: str | Path, output_root: str | Path, row_name: str) -> Path:
    relative_path = Path(path_value)
    expected_root = Path(output_root)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} path must be repo-relative and cannot traverse: {path_value}")
    try:
        relative_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} path must stay under {expected_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            errors.append(f"{path.as_posix()} contains forbidden evidence marker: {match.group(0)}")
    lowered = text.lower()
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase in lowered:
            errors.append(f"{path.as_posix()} contains non-local evidence overclaim: {phrase}")
    if errors:
        raise VerificationError("\n".join(errors))


def contract_scenarios(contract: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = contract.get("scenarios")
    if not isinstance(scenarios, list):
        raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} must contain a scenarios list")
    parsed: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} scenarios[{index}] must be an object")
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
        raise VerificationError(f"{row_name} source ref must use file#row-id: {source_ref}")
    path_text, row_id = source_ref.split("#", 1)
    if not path_text or not row_id:
        raise VerificationError(f"{row_name} source ref must include file and row ID: {source_ref}")
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} source ref must be repo-relative: {source_ref}")
    data = load_json(root, relative_path)
    if not row_id_exists(data, row_id):
        raise VerificationError(f"{row_name} source ref row not found: {source_ref}")


def validate_doc_ref(root: Path, source_doc_ref: str, row_name: str) -> None:
    if "#" not in source_doc_ref:
        raise VerificationError(f"{row_name} source doc ref must use file#heading: {source_doc_ref}")
    path_text, anchor = source_doc_ref.split("#", 1)
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} source doc ref must be repo-relative: {source_doc_ref}")
    text = read_text(root, relative_path)
    if anchor and anchor.lower() not in text.lower():
        raise VerificationError(f"{row_name} source doc ref anchor not found: {source_doc_ref}")


def check_operator_schema(contract: dict[str, Any], errors: list[str]) -> None:
    try:
        schema = require_dict(contract, "operator_input_schema", "contract")
        required_fields = require_list_of_strings(schema, "required_fields", "operator_input_schema")
        allowed_results = require_list_of_strings(schema, "allowed_results", "operator_input_schema")
        artifact_ref_root = require_string(schema, "artifact_ref_root", "operator_input_schema")
    except VerificationError as error:
        errors.append(str(error))
        return
    if required_fields != REQUIRED_OPERATOR_FIELDS:
        errors.append("operator_input_schema required_fields must match Phase 16 operator metadata fields")
    if allowed_results != OPERATOR_ALLOWED_RESULTS:
        errors.append("operator_input_schema allowed_results must match Phase 16 allowed operator results")
    if artifact_ref_root != DEFAULT_OUTPUT_DIR.as_posix():
        errors.append(f"operator_input_schema artifact_ref_root must be {DEFAULT_OUTPUT_DIR.as_posix()}")


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
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    try:
        status_vocabulary = require_list_of_strings(contract, "status_vocabulary", "contract")
        artifact_kinds = set(require_list_of_strings(contract, "required_artifact_kinds", "contract"))
        scenarios = contract_scenarios(contract)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if status_vocabulary != STATUS_VOCABULARY:
        errors.append("status_vocabulary does not match the Phase 16 vocabulary")
    missing_artifact_kinds = sorted(REQUIRED_ARTIFACT_KINDS - artifact_kinds)
    if missing_artifact_kinds:
        errors.append("missing required artifact kinds: " + ", ".join(missing_artifact_kinds))
    check_operator_schema(contract, errors)

    scenario_ids = [str(scenario.get("id")) for scenario in scenarios]
    missing_scenarios = sorted(REQUIRED_SCENARIO_IDS - set(scenario_ids))
    extra_scenarios = sorted(set(scenario_ids) - REQUIRED_SCENARIO_IDS)
    if missing_scenarios:
        errors.append("missing required scenarios: " + ", ".join(missing_scenarios))
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
            requirement_ids = set(require_list_of_strings(scenario, "requirement_ids", row_name))
            require_list_of_strings(scenario, "v1_requirement_ids", row_name)
            source_refs = require_list_of_strings(scenario, "source_contract_refs", row_name)
            source_doc_refs = require_list_of_strings(scenario, "source_doc_refs", row_name)
            service_surface = require_string(scenario, "service_surface", row_name)
            mode = require_string(scenario, "mode", row_name)
            require_string(scenario, "required_input_kind", row_name)
            proof_scope = require_string(scenario, "proof_scope", row_name)
            require_string(scenario, "expected_pass_semantics", row_name)
            require_string(scenario, "expected_failure_semantics", row_name)
            artifact_path = require_string(scenario, "expected_artifact_path", row_name)
            retained_artifact_kind = require_string(scenario, "retained_artifact_kind", row_name)
            allowed_statuses = set(require_list_of_strings(scenario, "allowed_statuses", row_name))
            operator_metadata = require_list_of_strings(scenario, "operator_metadata_required", row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue

        if scenario_id != row_name:
            errors.append(f"{row_name} id mismatch")
        unknown_requirements = sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)
        if unknown_requirements:
            errors.append(f"{row_name} uses unknown requirement IDs: {', '.join(unknown_requirements)}")
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
            require_repo_relative_under(artifact_path, DEFAULT_OUTPUT_DIR, row_name)
        except VerificationError as error:
            errors.append(str(error))
        if retained_artifact_kind not in REQUIRED_ARTIFACT_KINDS:
            errors.append(f"{row_name} retained_artifact_kind is not declared: {retained_artifact_kind}")
        if not allowed_statuses <= set(STATUS_VOCABULARY):
            errors.append(f"{row_name} allowed_statuses contains unknown statuses")
        if proof_scope == "live-service-observation":
            missing_statuses = sorted(LIVE_ALLOWED_STATUSES - allowed_statuses)
            if missing_statuses:
                errors.append(f"{row_name} live-service allowed_statuses missing: {', '.join(missing_statuses)}")
            if mode != "live-or-controlled-service":
                errors.append(f"{row_name} live-service rows must use live-or-controlled-service mode")
            if scenario.get("default_status") == "passed":
                errors.append(f"{row_name} default_status cannot be passed without operator evidence")
        elif proof_scope == "source-contract":
            missing_statuses = sorted(SOURCE_CONTRACT_ALLOWED_STATUSES - allowed_statuses)
            if missing_statuses:
                errors.append(f"{row_name} source-contract allowed_statuses missing: {', '.join(missing_statuses)}")
            if mode != "local-contract-validation":
                errors.append(f"{row_name} source-contract rows must use local-contract-validation mode")
        else:
            errors.append(f"{row_name} proof_scope must be live-service-observation or source-contract")
        if operator_metadata != REQUIRED_OPERATOR_FIELDS:
            errors.append(f"{row_name} operator metadata must include: {', '.join(REQUIRED_OPERATOR_FIELDS)}")
        if scenario.get("redaction_required") is not True:
            errors.append(f"{row_name} redaction_required must be true")
        credential_boundary = scenario.get("credential_boundary")
        residual_gates = scenario.get("residual_non_live_gates")
        unsupported_claims = scenario.get("unsupported_claims")
        if not credential_boundary:
            errors.append(f"{row_name} credential_boundary must not be empty")
        if not isinstance(residual_gates, list) or not residual_gates:
            errors.append(f"{row_name} residual_non_live_gates must not be empty")
        if not isinstance(unsupported_claims, list) or not unsupported_claims:
            errors.append(f"{row_name} unsupported_claims must not be empty")

    missing_requirements = sorted(REQUIRED_REQUIREMENT_IDS - covered_requirements)
    if missing_requirements:
        errors.append("missing LIVE requirement coverage: " + ", ".join(missing_requirements))
    missing_surfaces = sorted(REQUIRED_SERVICE_SURFACES - covered_surfaces)
    if missing_surfaces:
        errors.append("missing required service surface coverage: " + ", ".join(missing_surfaces))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def iter_security_files(root: Path, output_dir: Path) -> list[Path]:
    require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    files = [CONTRACT_MANIFEST]
    full_output_dir = root / output_dir
    if full_output_dir.exists():
        files.extend(
            sorted(
                path.relative_to(root)
                for path in full_output_dir.rglob("*")
                if path.is_file()
            )
        )
    return files


def check_security(root: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    errors: list[str] = []
    check_contract(root)
    for relative_path in iter_security_files(root, output_dir):
        try:
            text = read_text(root, relative_path)
            reject_forbidden_text(relative_path, text)
        except UnicodeDecodeError as error:
            errors.append(f"{relative_path.as_posix()} is not UTF-8 text: {error}")
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
    phase16_manifest_srcs = [
        Path(path).relative_to("tools/bazel").as_posix()
        for path in SOURCE_REF_MANIFESTS
    ]
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase16_source_ref_manifests"',
                'name = "phase16_verify"',
                'name = "phase16_verify_tests"',
                "phase16_live_network_evidence.py",
                "phase16_live_network_evidence_test.py",
                "phase16_live_network_evidence_contract.json",
                ":phase16_source_ref_manifests",
                "//:phase16_live_network_evidence_docs",
                "//:phase11_cutover_evidence_docs",
                *phase16_manifest_srcs,
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase16_live_network_evidence_docs"',
                'name = "phase16_verify"',
                'name = "phase16_verify_tests"',
                ".planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md",
                ".planning/phases/16-live-network-and-transfer-qualification/16-RESEARCH.md",
                ".planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md",
                ".planning/phases/16-live-network-and-transfer-qualification/16-01-PLAN.md",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase16_verify)",
                "python3 tools/bazel/phase16_live_network_evidence.py --wiring-only",
                "python3 tools/bazel/phase16_live_network_evidence.py --quick",
                "phase16_verify_tests)",
                "python3 tools/bazel/phase16_live_network_evidence_test.py",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase16-verify:",
                "bazel run //tools/bazel:phase16_verify_tests",
                "bazel run //tools/bazel:phase16_verify",
            ],
        )
    )
    try:
        just_lines = [line.strip() for line in read_text(root, "justfile").splitlines()]
        just_tests_line = "bazel run //tools/bazel:phase16_verify_tests"
        just_verify_line = "bazel run //tools/bazel:phase16_verify"
        if just_tests_line not in just_lines:
            errors.append("justfile missing exact phase16_verify_tests recipe line")
        if just_verify_line not in just_lines:
            errors.append("justfile missing exact phase16_verify recipe line")
        if just_tests_line in just_lines and just_verify_line in just_lines:
            if just_lines.index(just_tests_line) > just_lines.index(just_verify_line):
                errors.append("justfile phase16-verify must run tests before verifier")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def load_operator_evidence_path(root: Path, path: str | None) -> tuple[Path | None, list[Any] | None]:
    if not path:
        return None, None
    evidence_path = Path(path)
    full_path = evidence_path if evidence_path.is_absolute() else root / evidence_path
    if not full_path.exists():
        raise VerificationError(f"operator evidence file does not exist: {path}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(evidence_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"operator evidence is not valid JSON: {error}") from error
    if isinstance(data, list):
        return evidence_path, data
    if isinstance(data, dict):
        rows = data.get("evidence_rows")
        if isinstance(rows, list):
            return evidence_path, rows
    raise VerificationError("operator evidence must contain an evidence_rows list or be a top-level list")


def validate_artifact_refs(artifact_refs: Any, row_name: str) -> list[str]:
    if not isinstance(artifact_refs, list) or not artifact_refs:
        raise VerificationError(f"{row_name} artifact_refs must be a non-empty list")
    parsed_refs: list[str] = []
    for index, artifact_ref in enumerate(artifact_refs):
        ref_name = f"{row_name} artifact_refs[{index}]"
        if not isinstance(artifact_ref, str) or not artifact_ref:
            raise VerificationError(f"{ref_name} must be a non-empty string")
        if artifact_ref.startswith(("external://", "artifact://")):
            parsed_refs.append(artifact_ref)
            continue
        require_repo_relative_under(artifact_ref, DEFAULT_OUTPUT_DIR, ref_name)
        parsed_refs.append(artifact_ref)
    return parsed_refs


def validated_operator_rows(root: Path, contract: dict[str, Any], path: str | None) -> dict[str, dict[str, Any]]:
    evidence_path, rows = load_operator_evidence_path(root, path)
    if rows is None:
        return {}
    schema = require_dict(contract, "operator_input_schema", "contract")
    allowed_results = set(require_list_of_strings(schema, "allowed_results", "operator_input_schema"))
    scenarios_by_id = {scenario["id"]: scenario for scenario in contract_scenarios(contract)}
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"operator evidence row {index}"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        try:
            require_fields(row, REQUIRED_OPERATOR_FIELDS, row_name)
            row_text = json.dumps(row, sort_keys=True)
            reject_forbidden_text(evidence_path or Path("operator-evidence"), row_text)
            scenario_id = require_string(row, "scenario_id", row_name)
            result = require_string(row, "result", row_name)
            service_surface = require_string(row, "service_surface", row_name)
            mode = require_string(row, "mode", row_name)
            if scenario_id not in scenarios_by_id:
                raise VerificationError(f"{row_name} references unknown scenario: {scenario_id}")
            if scenario_id in parsed_rows:
                raise VerificationError(f"{row_name} duplicates scenario evidence: {scenario_id}")
            if result not in allowed_results:
                raise VerificationError(f"{row_name} uses unsupported result: {result}")
            scenario = scenarios_by_id[scenario_id]
            allowed_statuses = set(require_list_of_strings(scenario, "allowed_statuses", scenario_id))
            if result not in allowed_statuses:
                raise VerificationError(f"{row_name} result {result} is not allowed for {scenario_id}")
            if service_surface != scenario["service_surface"]:
                raise VerificationError(f"{row_name} service_surface does not match {scenario_id}")
            if mode != scenario["mode"]:
                raise VerificationError(f"{row_name} mode does not match {scenario_id}")
            artifact_refs = validate_artifact_refs(row["artifact_refs"], row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue
        parsed = {field: row[field] for field in REQUIRED_OPERATOR_FIELDS}
        parsed["artifact_refs"] = artifact_refs
        parsed_rows[scenario_id] = parsed
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def write_json(root: Path, relative_path: Path, data: dict[str, Any]) -> None:
    full_path = root / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_status_for(scenario: dict[str, Any]) -> str:
    if scenario.get("proof_scope") == "source-contract":
        return "source-contract-passed"
    return "pending-live-input"


def scenario_result_row(scenario: dict[str, Any], maybe_operator_row: dict[str, Any] | None) -> dict[str, Any]:
    scenario_id = str(scenario["id"])
    status = default_status_for(scenario)
    artifact_refs = [str(scenario["expected_artifact_path"])]
    redaction_summary = "No operator evidence supplied; live/control-service evidence pending."
    residual_risk = "Awaiting approved live or controlled-service operator evidence."
    operator_metadata: dict[str, str] = {
        "device": "",
        "firmware_build": "",
        "operator": "",
        "timestamp": "",
        "evidence_type": "",
    }
    if scenario.get("proof_scope") == "source-contract":
        redaction_summary = "Source contract and redaction guard validation only."
        residual_risk = "Live/control-service rows still require operator evidence."
    if maybe_operator_row is not None:
        status = str(maybe_operator_row["result"])
        artifact_refs = [str(ref) for ref in maybe_operator_row["artifact_refs"]]
        redaction_summary = str(maybe_operator_row["redaction_summary"])
        residual_risk = str(maybe_operator_row["residual_risk"])
        operator_metadata = {
            "device": str(maybe_operator_row["device"]),
            "firmware_build": str(maybe_operator_row["firmware_build"]),
            "operator": str(maybe_operator_row["operator"]),
            "timestamp": str(maybe_operator_row["timestamp"]),
            "evidence_type": str(maybe_operator_row["evidence_type"]),
        }
    return {
        "artifact_refs": artifact_refs,
        "credential_boundary": scenario["credential_boundary"],
        "id": scenario_id,
        "mode": scenario["mode"],
        "operator_metadata_present": maybe_operator_row is not None,
        "proof_scope": scenario["proof_scope"],
        "redaction_summary": redaction_summary,
        "requirement_ids": scenario["requirement_ids"],
        "residual_risk": residual_risk,
        "scenario_id": scenario_id,
        "service_surface": scenario["service_surface"],
        "source_contract_refs": scenario["source_contract_refs"],
        "source_doc_refs": scenario["source_doc_refs"],
        "status": status,
        "title": scenario["title"],
        "unsupported_claims": scenario["unsupported_claims"],
        "v1_requirement_ids": scenario["v1_requirement_ids"],
        **operator_metadata,
    }


def write_log(root: Path, output_dir: Path, result_row: dict[str, Any]) -> None:
    log_path = output_dir / "logs" / f"{result_row['id']}.log"
    lines = [
        f"scenario_id={result_row['id']}",
        f"status={result_row['status']}",
        f"proof_scope={result_row['proof_scope']}",
        f"service_surface={result_row['service_surface']}",
        f"mode={result_row['mode']}",
        f"artifact_refs={','.join(result_row['artifact_refs'])}",
        f"redaction_summary={result_row['redaction_summary']}",
        f"residual_risk={result_row['residual_risk']}",
    ]
    if result_row["operator_metadata_present"]:
        lines.append("operator_evidence=accepted-redacted-reference-only")
    elif result_row["proof_scope"] == "source-contract":
        lines.append("operator_evidence=not-required-for-source-contract-row")
    else:
        lines.append("operator_evidence=pending-live-or-controlled-service-input")
    full_path = root / log_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quick_artifacts(
    root: Path,
    contract: dict[str, Any],
    output_dir: Path,
    operator_rows: dict[str, dict[str, Any]],
) -> None:
    require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    full_output_dir = root / output_dir
    if full_output_dir.exists():
        shutil.rmtree(full_output_dir)
    (full_output_dir / "logs").mkdir(parents=True)
    (full_output_dir / "source-contract-snapshots").mkdir(parents=True)

    scenarios = contract_scenarios(contract)
    result_rows = [
        scenario_result_row(scenario, operator_rows.get(str(scenario["id"])))
        for scenario in scenarios
    ]
    for row in result_rows:
        write_log(root, output_dir, row)

    status_counts: dict[str, int] = {}
    for row in result_rows:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    snapshot_path = output_dir / "source-contract-snapshots" / CONTRACT_MANIFEST.name
    run_manifest = {
        "artifact_name": contract["artifact_name"],
        "command_mode": "quick",
        "generated_at": generated_at,
        "live_inputs_supplied": bool(operator_rows),
        "output_root": output_dir.as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_coverage": sorted(REQUIRED_REQUIREMENT_IDS),
        "scenarios": [
            {
                "artifact_refs": row["artifact_refs"],
                "id": row["id"],
                "mode": row["mode"],
                "proof_scope": row["proof_scope"],
                "scenario_id": row["scenario_id"],
                "service_surface": row["service_surface"],
                "status": row["status"],
            }
            for row in result_rows
        ],
        "source_contract_snapshot_path": snapshot_path.as_posix(),
        "status_counts": status_counts,
    }
    normalized_results = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "scenarios": result_rows,
    }
    redacted_summary = {
        "credential_boundaries": {
            row["id"]: row["credential_boundary"]
            for row in result_rows
        },
        "generated_at": generated_at,
        "operator_evidence_summary": {
            "accepted_rows": sorted(operator_rows),
            "count": len(operator_rows),
        },
        "pending_live_input_rows": [
            row["id"] for row in result_rows if row["status"] == "pending-live-input"
        ],
        "redaction_boundary": "Phase 16 retains only redacted summaries, operator metadata, source snapshots, and artifact references.",
        "scenario_status": {
            row["id"]: row["status"]
            for row in result_rows
        },
        "status_counts": status_counts,
        "unsupported_claims": {
            row["id"]: row["unsupported_claims"]
            for row in result_rows
        },
    }
    write_json(root, output_dir / "run-manifest.json", run_manifest)
    write_json(root, output_dir / "normalized-scenario-results.json", normalized_results)
    write_json(root, output_dir / "redacted-network-summary.json", redacted_summary)
    write_json(
        root,
        output_dir / "operator-evidence-input.json",
        {"evidence_rows": list(operator_rows.values())},
    )
    shutil.copy2(root / CONTRACT_MANIFEST, root / snapshot_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 16 live network evidence contract")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 16 evidence contract")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 16 contract and generated artifacts")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel and just workflow wiring")
    parser.add_argument("--quick", action="store_true", help="write deterministic Phase 16 evidence artifacts")
    parser.add_argument("--operator-evidence", help="optional operator evidence JSON input")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 16 evidence output directory")
    args = parser.parse_args()
    selected_modes = [args.contract_only, args.security_only, args.wiring_only, args.quick]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.operator_evidence and not args.quick:
        parser.error("--operator-evidence is only valid with --quick")
    output_dir = Path(args.output_dir)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 16 live network evidence contract passed")
        elif args.security_only:
            check_security(ROOT, output_dir)
            print("Phase 16 live network evidence security scan passed")
        elif args.quick:
            contract = check_contract(ROOT)
            operator_rows = validated_operator_rows(ROOT, contract, args.operator_evidence)
            write_quick_artifacts(ROOT, contract, output_dir, operator_rows)
            check_security(ROOT, output_dir)
            print(f"Phase 16 live network evidence written to {output_dir.as_posix()}")
        else:
            check_wiring(ROOT)
            print("Phase 16 live network evidence wiring passed")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
