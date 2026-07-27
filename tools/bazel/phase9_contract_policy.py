#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "09-network-web-services-and-transfers"
PHASE_LIFECYCLE_ID = "9-2026-06-14T02-15-21"

CONNECT_MANIFEST = Path("tools/bazel/manifests/phase9_connect_contracts.json")
WUI_MANIFEST = Path("tools/bazel/manifests/phase9_wui_contracts.json")
TRANSFER_MANIFEST = Path(
    "tools/bazel/manifests/phase9_transfer_contracts.json")
NETWORK_SERVICES_MANIFEST = Path(
    "tools/bazel/manifests/phase9_network_service_contracts.json")
CONCERN_DISPOSITIONS_MANIFEST = Path(
    "tools/bazel/manifests/phase9_network_concern_dispositions.json")
VALIDATION_CONTRACT = Path(
    ".planning/phases/09-network-web-services-and-transfers/09-VALIDATION.md")
NETWORK_RUST = Path("rust/crates/domain/src/network.rs")
RUST_DOMAIN_LIB = Path("rust/crates/domain/src/lib.rs")
NEGATIVE_FIXTURE_CASES = Path(
    "tools/bazel/fixtures/phase9_negative_network_cases.json")
NEGATIVE_FIXTURE_RUNNER = Path("tools/bazel/phase9_negative_fixtures.py")

ALLOWED_EVIDENCE_CLASSES = {
    "manifest-check",
    "source-audit",
    "static-source-audit",
    "host-test",
    "rust-host-test",
    "simulator-flow",
    "hardware-smoke",
    "manual-hardware-required",
}

COMPATIBLE_LOCAL_EVIDENCE_CLASSES = {
    # 09-01 manifests were committed before this verifier and use this
    # source-backed class for rows guarded by existing host tests.
    "unit-test-backed",
}

NON_LOCAL_EVIDENCE_CLASSES = {
    "simulator-flow",
    "hardware-smoke",
    "manual-hardware-required",
}

COMMON_FIELDS = [
    "id",
    "requirement_id",
    "surface",
    "reference_sources",
    "reference_behavior",
    "rust_surface",
    "auth_requirement",
    "integration_point",
    "evidence_class",
    "proof_scope",
    "secret_handling",
    "intentional_delta",
    "non_local_evidence",
    "phase_lifecycle_id",
]

CONNECT_FIELDS = [
    *COMMON_FIELDS,
]

WUI_FIELDS = [
    *COMMON_FIELDS,
    "endpoint_family",
    "methods",
    "status_behavior",
    "auth_modes",
    "resource_limits",
]

TRANSFER_FIELDS = [
    *COMMON_FIELDS,
    "transfer_source",
    "slot_state",
    "range_behavior",
    "encryption_behavior",
    "media_behavior",
    "recovery_behavior",
    "error_mapping",
]

NETWORK_SERVICE_FIELDS = [
    "id",
    "requirement_id",
    "surface",
    "reference_sources",
    "reference_behavior",
    "rust_surface",
    "evidence_class",
    "proof_scope",
    "secret_handling",
    "intentional_delta",
    "non_local_evidence",
    "phase_lifecycle_id",
    "service_family",
    "feature_gate",
    "build_gate",
    "transport",
    "config_keys",
    "runtime_defaults",
]

CONCERN_FIELDS = [
    "id",
    "concern_id",
    "requirement_id",
    "reference_sources",
    "disposition",
    "phase9_handling",
    "evidence_class",
    "proof_scope",
    "intentional_delta",
    "regression_guard",
    "secret_handling",
    "phase_lifecycle_id",
]

REQUIRED_CONNECT_ROW_IDS = [
    "connect-registration-token-fingerprint",
    "connect-config-host-token-proxy-tls",
    "connect-telemetry-events",
    "connect-command-polling-websocket",
    "connect-host-decompression-connection-reuse",
    "connect-tls-required-verification-policy",
    "connect-proxy-minimal-limitations",
    "connect-transfer-download-integration",
    "connect-sleep-backoff-shared-buffer-limits",
]

REQUIRED_WUI_ROW_IDS = [
    "wui-server-resource-model",
    "wui-static-assets",
    "prusalink-api-v1-status-job-files-transfer",
    "octoprint-compatible-api",
    "wui-digest-auth-nonce-stale",
    "wui-api-key-auth",
    "wui-usb-file-storage-paths",
    "wui-upload-transfer-renderer",
    "wui-unknown-request-error",
    "wui-responsive-static-ui-contract",
]

REQUIRED_TRANSFER_ROW_IDS = [
    "transfer-single-active-slot",
    "transfer-connect-command-initiation",
    "transfer-wui-upload-api-integration",
    "transfer-range-request",
    "transfer-encrypted-aes-ctr-payload",
    "transfer-partial-file-direct-sector",
    "transfer-recovery-and-changed-path",
    "transfer-error-outcome-mapping",
    "transfer-media-race-non-local",
]

REQUIRED_NETWORK_SERVICE_ROW_IDS = [
    "sntp-client-default-server",
    "mdns-optional-announcement",
    "dns-lwip-network-resolution",
    "metrics-runtime-config-udp",
    "metrics-line-protocol-throttling",
    "syslog-udp-destination",
    "network-feature-gates-wui-connect",
]

REQUIRED_CONCERN_ROW_IDS = [
    "concern-phase9-custom-der-cert-read",
    "concern-phase9-weak-digest-modules",
    "concern-phase9-proxy-limitations",
    "concern-phase9-stale-connect-module-tests",
    "concern-phase9-whole-response-shared-buffers",
    "concern-phase9-transfer-media-races",
    "concern-phase9-transfer-monitor-lock-order",
    "concern-phase9-crash-dump-upload-boundary",
    "concern-phase9-network-tls-coverage-gaps",
]

RUST_API_STRINGS = [
    "NetworkEvidenceClass",
    "NetworkParityRowId",
    "SecretHandling",
    "ConnectCommandState",
    "ProxyMode",
    "WuiAuthMode",
    "TransferSlotState",
    "TransferRange",
    "EncryptedPayloadMetadata",
    "NetworkServiceContract",
    "NetworkParityContract",
    "NetworkServiceContractInput",
    "NetworkParityContractInput",
]

FORBIDDEN_MARKERS = [
    "token_value",
    "password_value",
    "wifi_password",
    "certificate_bytes",
    "private_key",
    "BEGIN PRIVATE KEY",
    "raw_crash_dump",
    "crash_dump_payload",
]

UNSAFE_RUST_PATTERNS = [
    ("unsafe block", "unsafe {"),
    ("unsafe function", "unsafe fn"),
    ("unsafe trait", "unsafe trait"),
    ("unsafe impl", "unsafe impl"),
    ("unsafe extern", "unsafe extern"),
    ("unsafe attribute", "#[unsafe("),
    ("unsafe allowance", "#![allow(unsafe_code)]"),
    ("unsafe allowance", "#[allow(unsafe_code)]"),
]

OVERCLAIM_STRINGS = [
    "cloud verified locally",
    "live Connect passed",
    "real TLS handshake passed",
    "physical Wi-Fi verified locally",
    "physical Ethernet verified locally",
    "USB media race passed locally",
    "long-running transfer verified locally",
    "simulator network flow passed locally",
    "raw crash dump upload approved",
    "cutover evidence complete",
]

PHASE9_ARTIFACTS_FOR_SECURITY_SCAN = [
    CONNECT_MANIFEST,
    WUI_MANIFEST,
    TRANSFER_MANIFEST,
    NETWORK_SERVICES_MANIFEST,
    CONCERN_DISPOSITIONS_MANIFEST,
    NEGATIVE_FIXTURE_CASES,
    VALIDATION_CONTRACT,
]


class VerificationError(Exception):
    pass


def read_json(path: Path) -> dict[str, Any]:
    full_path = ROOT / path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {path.as_posix()}")

    try:
        data = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{path.as_posix()} is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise VerificationError(
            f"{path.as_posix()} must contain a top-level JSON object")
    return data


def read_text(path: str | Path) -> str:
    relative_path = Path(path)
    full_path = ROOT / relative_path
    if not full_path.exists():
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def is_empty(value: object) -> bool:
    return value in ("", [], {}, None)


def row_blob(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True)


def require_top_level(data: dict[str, Any], path: Path,
                      collection_name: str) -> list[dict[str, Any]]:
    if data.get("schema_version") != 1:
        raise VerificationError(
            f"{path.as_posix()} must set schema_version to 1")
    if data.get("phase") != PHASE:
        raise VerificationError(f"{path.as_posix()} must set phase to {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"{path.as_posix()} must set phase_lifecycle_id to {PHASE_LIFECYCLE_ID}"
        )

    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(
            f"{path.as_posix()} must contain a {collection_name} list")

    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(
                f"{path.as_posix()} {collection_name}[{index}] must be an object"
            )
        parsed_rows.append(row)
    return parsed_rows


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields if field in row and is_empty(row[field])
    ]
    legacy = [
        field for field in ["requirement", "source_paths"] if field in row
    ]
    details = []
    if missing:
        details.append(f"missing required fields: {', '.join(missing)}")
    if empty:
        details.append(f"empty required fields: {', '.join(empty)}")
    if legacy:
        details.append(
            "uses legacy manifest schema fields instead of canonical requirement_id/reference_sources: "
            + ", ".join(legacy))
    if details:
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_unique(rows: list[dict[str, Any]], field: str,
                   path: Path) -> set[str]:
    values: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str):
            raise VerificationError(
                f"{path.as_posix()} row has non-string {field}: {value!r}")
        if value in values:
            duplicates.add(value)
        values.add(value)

    if duplicates:
        raise VerificationError(
            f"{path.as_posix()} has duplicate {field} values: {', '.join(sorted(duplicates))}"
        )
    return values


def require_ids(actual: set[str], required: list[str], label: str) -> None:
    missing = sorted(set(required) - actual)
    if missing:
        raise VerificationError(
            f"missing required {label}: {', '.join(missing)}")


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a non-empty list of strings")
    return value


def require_string_or_list_of_strings(row: dict[str, Any], field: str,
                                      row_name: str) -> None:
    value = row.get(field)
    if isinstance(value, str) and value:
        return
    if isinstance(value, list) and value and all(
            isinstance(item, str) and item for item in value):
        return
    raise VerificationError(
        f"{row_name} {field} must be a non-empty string or list of strings")


def require_existing_reference_sources(row: dict[str, Any],
                                       row_name: str) -> None:
    reference_sources = require_list_of_strings(row, "reference_sources",
                                                row_name)
    root = ROOT.resolve()
    for reference_source in reference_sources:
        relative_path = Path(reference_source)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise VerificationError(
                f"{row_name} reference source must be repo-relative: {reference_source}"
            )

        full_path = (root / relative_path).resolve()
        try:
            full_path.relative_to(root)
        except ValueError as error:
            raise VerificationError(
                f"{row_name} reference source escapes repo: {reference_source}"
            ) from error

        if not full_path.exists():
            raise VerificationError(
                f"{row_name} references missing source path: {reference_source}"
            )


def require_requirement_id(row: dict[str, Any], allowed_ids: set[str],
                           row_name: str) -> None:
    requirement_id = require_string(row, "requirement_id", row_name)
    if requirement_id not in allowed_ids:
        allowed = ", ".join(sorted(allowed_ids))
        raise VerificationError(
            f"{row_name} requirement_id must be one of: {allowed}")


def require_evidence_and_scope(row: dict[str, Any], row_name: str) -> None:
    evidence_class = require_string(row, "evidence_class", row_name)
    allowed_evidence = ALLOWED_EVIDENCE_CLASSES | COMPATIBLE_LOCAL_EVIDENCE_CLASSES
    if evidence_class not in allowed_evidence:
        allowed = ", ".join(sorted(ALLOWED_EVIDENCE_CLASSES))
        raise VerificationError(
            f"{row_name} evidence_class {evidence_class!r} must be one of: {allowed}"
        )

    proof_scope = require_string(row, "proof_scope", row_name)
    if proof_scope not in {"local", "non-local"}:
        raise VerificationError(
            f"{row_name} proof_scope must be local or non-local")
    if proof_scope == "local" and evidence_class in NON_LOCAL_EVIDENCE_CLASSES:
        raise VerificationError(
            f"{row_name} proof_scope local cannot be paired with {evidence_class} evidence"
        )


def require_secret_and_delta(row: dict[str, Any], row_name: str) -> None:
    secret_handling = require_string(row, "secret_handling", row_name)
    if secret_handling not in {"none", "named-only-redacted"}:
        raise VerificationError(
            f"{row_name} secret_handling must be none or named-only-redacted")

    intentional_delta = require_string(row, "intentional_delta", row_name)
    if intentional_delta not in {"none", "approved", "blocked"}:
        raise VerificationError(
            f"{row_name} intentional_delta must be none, approved, or blocked")


def require_phase_lifecycle(row: dict[str, Any], row_name: str) -> None:
    phase_lifecycle_id = require_string(row, "phase_lifecycle_id", row_name)
    if phase_lifecycle_id != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")


def require_row_text(row: dict[str, Any], required_text: list[str],
                     row_name: str) -> None:
    blob = row_blob(row)
    missing = [needle for needle in required_text if needle not in blob]
    if missing:
        raise VerificationError(
            f"{row_name} missing required text: {', '.join(missing)}")


def validate_contract_rows(
    path: Path,
    collection_name: str,
    fields: list[str],
    required_ids: list[str],
    allowed_requirement_ids: set[str],
) -> list[dict[str, Any]]:
    data = read_json(path)
    rows = require_top_level(data, path, collection_name)
    row_ids = require_unique(rows, "id", path)
    require_ids(row_ids, required_ids, f"{collection_name} row IDs")

    errors: list[str] = []
    for row in rows:
        row_name = f"{path.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, fields, row_name)
            require_requirement_id(row, allowed_requirement_ids, row_name)
            require_existing_reference_sources(row, row_name)
            require_evidence_and_scope(row, row_name)
            require_secret_and_delta(row, row_name)
            require_phase_lifecycle(row, row_name)
            require_list_of_strings(row, "non_local_evidence", row_name)
        except VerificationError as error:
            errors.append(str(error))

    if errors:
        raise VerificationError("\n".join(errors))
    return rows


def strip_rust_comments_and_strings(source: str) -> str:
    result: list[str] = []
    index = 0
    length = len(source)
    while index < length:
        char = source[index]
        next_char = source[index + 1] if index + 1 < length else ""

        if char == "/" and next_char == "/":
            index += 2
            while index < length and source[index] != "\n":
                index += 1
            result.append("\n")
            continue

        if char == "/" and next_char == "*":
            index += 2
            depth = 1
            while index < length and depth > 0:
                if source[index:index + 2] == "/*":
                    depth += 1
                    index += 2
                elif source[index:index + 2] == "*/":
                    depth -= 1
                    index += 2
                else:
                    if source[index] == "\n":
                        result.append("\n")
                    index += 1
            continue

        if char == "r":
            raw_match = re.match(r'r(#*)"', source[index:])
            if raw_match:
                hashes = raw_match.group(1)
                terminator = '"' + hashes
                index += len(raw_match.group(0))
                end_index = source.find(terminator, index)
                if end_index == -1:
                    break
                result.append('""')
                index = end_index + len(terminator)
                continue

        if char == '"':
            index += 1
            escaped = False
            while index < length:
                current = source[index]
                if current == "\n":
                    result.append("\n")
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == '"':
                    index += 1
                    break
                index += 1
            result.append('""')
            continue

        result.append(char)
        index += 1
    return "".join(result)
