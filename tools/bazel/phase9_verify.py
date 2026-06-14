#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
PHASE = "09-network-web-services-and-transfers"
PHASE_LIFECYCLE_ID = "9-2026-06-14T02-15-21"

CONNECT_MANIFEST = Path("tools/bazel/manifests/phase9_connect_contracts.json")
WUI_MANIFEST = Path("tools/bazel/manifests/phase9_wui_contracts.json")
TRANSFER_MANIFEST = Path("tools/bazel/manifests/phase9_transfer_contracts.json")
NETWORK_SERVICES_MANIFEST = Path("tools/bazel/manifests/phase9_network_service_contracts.json")
CONCERN_DISPOSITIONS_MANIFEST = Path(
    "tools/bazel/manifests/phase9_network_concern_dispositions.json"
)
VALIDATION_CONTRACT = Path(".planning/phases/09-network-web-services-and-transfers/09-VALIDATION.md")
NETWORK_RUST = Path("rust/crates/domain/src/network.rs")
RUST_DOMAIN_LIB = Path("rust/crates/domain/src/lib.rs")

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
        raise VerificationError(f"{path.as_posix()} is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise VerificationError(f"{path.as_posix()} must contain a top-level JSON object")
    return data


def read_text(path: str | Path) -> str:
    relative_path = Path(path)
    full_path = ROOT / relative_path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def is_empty(value: object) -> bool:
    return value in ("", [], {}, None)


def row_blob(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True)


def require_top_level(data: dict[str, Any], path: Path, collection_name: str) -> list[dict[str, Any]]:
    if data.get("schema_version") != 1:
        raise VerificationError(f"{path.as_posix()} must set schema_version to 1")
    if data.get("phase") != PHASE:
        raise VerificationError(f"{path.as_posix()} must set phase to {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"{path.as_posix()} must set phase_lifecycle_id to {PHASE_LIFECYCLE_ID}"
        )

    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(f"{path.as_posix()} must contain a {collection_name} list")

    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{path.as_posix()} {collection_name}[{index}] must be an object")
        parsed_rows.append(row)
    return parsed_rows


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and is_empty(row[field])]
    legacy = [field for field in ["requirement", "source_paths"] if field in row]
    details = []
    if missing:
        details.append(f"missing required fields: {', '.join(missing)}")
    if empty:
        details.append(f"empty required fields: {', '.join(empty)}")
    if legacy:
        details.append(
            "uses legacy manifest schema fields instead of canonical requirement_id/reference_sources: "
            + ", ".join(legacy)
        )
    if details:
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_unique(rows: list[dict[str, Any]], field: str, path: Path) -> set[str]:
    values: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str):
            raise VerificationError(f"{path.as_posix()} row has non-string {field}: {value!r}")
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
        raise VerificationError(f"missing required {label}: {', '.join(missing)}")


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a non-empty list of strings")
    return value


def require_string_or_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> None:
    value = row.get(field)
    if isinstance(value, str) and value:
        return
    if isinstance(value, list) and value and all(isinstance(item, str) and item for item in value):
        return
    raise VerificationError(f"{row_name} {field} must be a non-empty string or list of strings")


def require_existing_reference_sources(row: dict[str, Any], row_name: str) -> None:
    reference_sources = require_list_of_strings(row, "reference_sources", row_name)
    root = ROOT.resolve()
    for reference_source in reference_sources:
        relative_path = Path(reference_source)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise VerificationError(f"{row_name} reference source must be repo-relative: {reference_source}")

        full_path = (root / relative_path).resolve()
        try:
            full_path.relative_to(root)
        except ValueError as error:
            raise VerificationError(f"{row_name} reference source escapes repo: {reference_source}") from error

        if not full_path.exists():
            raise VerificationError(f"{row_name} references missing source path: {reference_source}")


def require_requirement_id(row: dict[str, Any], allowed_ids: set[str], row_name: str) -> None:
    requirement_id = require_string(row, "requirement_id", row_name)
    if requirement_id not in allowed_ids:
        allowed = ", ".join(sorted(allowed_ids))
        raise VerificationError(f"{row_name} requirement_id must be one of: {allowed}")


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
        raise VerificationError(f"{row_name} proof_scope must be local or non-local")
    if proof_scope == "local" and evidence_class in NON_LOCAL_EVIDENCE_CLASSES:
        raise VerificationError(
            f"{row_name} proof_scope local cannot be paired with {evidence_class} evidence"
        )


def require_secret_and_delta(row: dict[str, Any], row_name: str) -> None:
    secret_handling = require_string(row, "secret_handling", row_name)
    if secret_handling not in {"none", "named-only-redacted"}:
        raise VerificationError(f"{row_name} secret_handling must be none or named-only-redacted")

    intentional_delta = require_string(row, "intentional_delta", row_name)
    if intentional_delta not in {"none", "approved", "blocked"}:
        raise VerificationError(f"{row_name} intentional_delta must be none, approved, or blocked")


def require_phase_lifecycle(row: dict[str, Any], row_name: str) -> None:
    phase_lifecycle_id = require_string(row, "phase_lifecycle_id", row_name)
    if phase_lifecycle_id != PHASE_LIFECYCLE_ID:
        raise VerificationError(f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")


def require_row_text(row: dict[str, Any], required_text: list[str], row_name: str) -> None:
    blob = row_blob(row)
    missing = [needle for needle in required_text if needle not in blob]
    if missing:
        raise VerificationError(f"{row_name} missing required text: {', '.join(missing)}")


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


def check_connect_manifest() -> None:
    rows = validate_contract_rows(
        CONNECT_MANIFEST,
        "connect_contracts",
        CONNECT_FIELDS,
        REQUIRED_CONNECT_ROW_IDS,
        {"IFCE-02"},
    )
    row_by_id = {row["id"]: row for row in rows}
    errors: list[str] = []
    checks = {
        "connect-registration-token-fingerprint": ["Token", "Fingerprint"],
        "connect-tls-required-verification-policy": [
            "MBEDTLS_SSL_VERIFY_REQUIRED",
            "MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
            "/internal/connect/connect.der",
        ],
        "connect-proxy-minimal-limitations": [
            "proxy-authentication-absent",
            "printer-to-proxy-leg-unencrypted",
            "proxy-active-only-when-connect_tls-true",
        ],
    }
    for row_id, required_text in checks.items():
        try:
            require_row_text(row_by_id[row_id], required_text, f"{CONNECT_MANIFEST.as_posix()} row {row_id}")
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_wui_manifest() -> None:
    rows = validate_contract_rows(
        WUI_MANIFEST,
        "wui_contracts",
        WUI_FIELDS,
        REQUIRED_WUI_ROW_IDS,
        {"IFCE-03"},
    )
    errors: list[str] = []
    for row in rows:
        row_name = f"{WUI_MANIFEST.as_posix()} row {row['id']}"
        try:
            require_list_of_strings(row, "methods", row_name)
            require_list_of_strings(row, "status_behavior", row_name)
            require_list_of_strings(row, "auth_modes", row_name)
            require_list_of_strings(row, "resource_limits", row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_transfer_manifest() -> None:
    rows = validate_contract_rows(
        TRANSFER_MANIFEST,
        "transfer_contracts",
        TRANSFER_FIELDS,
        REQUIRED_TRANSFER_ROW_IDS,
        {"IFCE-02", "IFCE-03", "IFCE-02/IFCE-03"},
    )
    row_by_id = {row["id"]: row for row in rows}
    errors: list[str] = []
    checks = {
        "transfer-single-active-slot": ["single-active-transfer-slot"],
        "transfer-encrypted-aes-ctr-payload": ["AES-CTR"],
    }
    for row_id, required_text in checks.items():
        try:
            require_row_text(row_by_id[row_id], required_text, f"{TRANSFER_MANIFEST.as_posix()} row {row_id}")
        except VerificationError as error:
            errors.append(str(error))

    media_row = row_by_id["transfer-media-race-non-local"]
    if media_row.get("proof_scope") != "non-local" or media_row.get("evidence_class") not in NON_LOCAL_EVIDENCE_CLASSES:
        errors.append(
            f"{TRANSFER_MANIFEST.as_posix()} row transfer-media-race-non-local must remain non-local and use manual-hardware-required evidence"
        )
    if errors:
        raise VerificationError("\n".join(errors))


def check_network_services_manifest() -> None:
    rows = validate_contract_rows(
        NETWORK_SERVICES_MANIFEST,
        "network_service_contracts",
        NETWORK_SERVICE_FIELDS,
        REQUIRED_NETWORK_SERVICE_ROW_IDS,
        {"IFCE-03"},
    )
    errors: list[str] = []
    for row in rows:
        row_name = f"{NETWORK_SERVICES_MANIFEST.as_posix()} row {row['id']}"
        try:
            for field in ["feature_gate", "build_gate", "transport", "config_keys", "runtime_defaults"]:
                require_list_of_strings(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_concern_dispositions() -> None:
    data = read_json(CONCERN_DISPOSITIONS_MANIFEST)
    rows = require_top_level(data, CONCERN_DISPOSITIONS_MANIFEST, "concerns")
    row_ids = require_unique(rows, "id", CONCERN_DISPOSITIONS_MANIFEST)
    require_ids(row_ids, REQUIRED_CONCERN_ROW_IDS, "concern row IDs")

    errors: list[str] = []
    for row in rows:
        row_name = f"{CONCERN_DISPOSITIONS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, CONCERN_FIELDS, row_name)
            require_requirement_id(row, {"IFCE-02", "IFCE-03", "IFCE-02/IFCE-03"}, row_name)
            require_existing_reference_sources(row, row_name)
            require_evidence_and_scope(row, row_name)
            require_secret_and_delta(row, row_name)
            require_phase_lifecycle(row, row_name)
            require_string(row, "concern_id", row_name)
            require_string_or_list_of_strings(row, "phase9_handling", row_name)
            require_string_or_list_of_strings(row, "regression_guard", row_name)
        except VerificationError as error:
            errors.append(str(error))

    row_by_id = {row["id"]: row for row in rows}
    checks = {
        "concern-phase9-custom-der-cert-read": [
            "valid DER",
            "missing DER",
            "invalid DER",
            "/internal/connect/connect.der",
        ],
        "concern-phase9-weak-digest-modules": ["MBEDTLS_SHA1_C", "MBEDTLS_MD5_C"],
        "concern-phase9-proxy-limitations": [
            "proxy-authentication-absent",
            "printer-to-proxy-leg-unencrypted",
            "proxy-active-only-when-connect_tls-true",
        ],
        "concern-phase9-crash-dump-upload-boundary": ["redaction"],
    }
    for row_id, required_text in checks.items():
        try:
            require_row_text(
                row_by_id[row_id],
                required_text,
                f"{CONCERN_DISPOSITIONS_MANIFEST.as_posix()} row {row_id}",
            )
        except VerificationError as error:
            errors.append(str(error))

    if errors:
        raise VerificationError("\n".join(errors))


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
                if source[index : index + 2] == "/*":
                    depth += 1
                    index += 2
                elif source[index : index + 2] == "*/":
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

        if char == "'":
            index += 1
            escaped = False
            while index < length:
                current = source[index]
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == "'":
                    index += 1
                    break
                index += 1
            result.append("''")
            continue

        result.append(char)
        index += 1
    return "".join(result)


def check_network_rust_api_surface() -> None:
    network_text = read_text(NETWORK_RUST)
    lib_text = read_text(RUST_DOMAIN_LIB)
    sanitized_network = strip_rust_comments_and_strings(network_text)
    errors: list[str] = []

    if "pub mod network;" not in lib_text:
        errors.append(f"{RUST_DOMAIN_LIB.as_posix()} must export pub mod network;")
    if "#![forbid(unsafe_code)]" not in lib_text:
        errors.append(f"{RUST_DOMAIN_LIB.as_posix()} must retain #![forbid(unsafe_code)]")

    for api_string in RUST_API_STRINGS:
        if api_string not in network_text:
            errors.append(f"{NETWORK_RUST.as_posix()} missing Rust API surface: {api_string}")
        if api_string not in lib_text:
            errors.append(f"{RUST_DOMAIN_LIB.as_posix()} missing Rust API export: {api_string}")

    for label, pattern in UNSAFE_RUST_PATTERNS:
        if pattern in sanitized_network:
            errors.append(f"{NETWORK_RUST.as_posix()} contains {label}: {pattern}")

    if errors:
        raise VerificationError("\n".join(errors))


def artifact_texts(paths: list[Path]) -> list[tuple[Path, str]]:
    texts: list[tuple[Path, str]] = []
    for path in paths:
        texts.append((path, read_text(path)))
    phase_dir = ROOT / ".planning/phases/09-network-web-services-and-transfers"
    if phase_dir.exists():
        for summary_path in sorted(phase_dir.glob("09-*-SUMMARY.md")):
            relative_path = summary_path.relative_to(ROOT)
            texts.append((relative_path, summary_path.read_text(encoding="utf-8")))
    return texts


def check_secret_markers() -> None:
    errors: list[str] = []
    for path, text in artifact_texts(PHASE9_ARTIFACTS_FOR_SECURITY_SCAN):
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                errors.append(f"{path.as_posix()} contains forbidden secret marker: {marker}")
    if errors:
        raise VerificationError("\n".join(errors))


def check_no_phase9_overclaim() -> None:
    errors: list[str] = []
    for path, text in artifact_texts(PHASE9_ARTIFACTS_FOR_SECURITY_SCAN):
        lowered = text.lower()
        for phrase in OVERCLAIM_STRINGS:
            if phrase.lower() in lowered:
                errors.append(f"{path.as_posix()} contains non-local evidence overclaim: {phrase}")
    if errors:
        raise VerificationError("\n".join(errors))


def check_validation_contract() -> None:
    text = read_text(VALIDATION_CONTRACT)
    required_text = [
        "status: complete",
        "nyquist_compliant: true",
        "wave_0_complete: true",
        f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
        "python3 tools/bazel/phase9_verify.py --quick",
        "just phase9-verify",
        "09-W0-01",
        "09-W0-05",
        "manual-hardware-required",
        "hardware-smoke",
        "simulator-flow",
    ]
    missing = [needle for needle in required_text if needle not in text]
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation lifecycle contract text: "
            + ", ".join(missing)
        )


def require_file_text(path: str | Path, required_text: list[str]) -> None:
    text = read_text(path)
    missing = [needle for needle in required_text if needle not in text]
    if missing:
        relative_path = Path(path)
        raise VerificationError(
            f"{relative_path.as_posix()} missing required wiring text: " + ", ".join(missing)
        )


def check_bazel_surface() -> None:
    errors: list[str] = []
    checks = [
        (
            Path("BUILD.bazel"),
            [
                "phase9_network_web_services_docs",
                "phase9_verify",
                "phase9_verify_tests",
            ],
        ),
        (
            Path("tools/bazel/BUILD.bazel"),
            [
                "phase9_verify",
                "phase9_verify_tests",
                "phase9_verify.py",
                "phase9_verify_test.py",
                "phase9_connect_contracts.json",
                "phase9_wui_contracts.json",
                "phase9_transfer_contracts.json",
                "phase9_network_service_contracts.json",
                "phase9_network_concern_dispositions.json",
                "//:phase9_network_web_services_docs",
                "//:rust_workspace_sources",
            ],
        ),
        (
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase9_verify)",
                "python3 tools/bazel/phase9_verify.py --all",
                "phase9_verify_tests)",
                "python3 tools/bazel/phase9_verify_test.py",
            ],
        ),
    ]
    for path, required_text in checks:
        try:
            require_file_text(path, required_text)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_just_surface() -> None:
    text = read_text("justfile")
    required_text = [
        "phase9-verify:",
        "bazel run //tools/bazel:phase9_verify_tests",
        "bazel run //tools/bazel:phase9_verify",
    ]
    missing = [needle for needle in required_text if needle not in text]
    errors = [f"justfile missing required wiring text: {', '.join(missing)}"] if missing else []
    test_index = text.find("bazel run //tools/bazel:phase9_verify_tests")
    verify_index = text.find("bazel run //tools/bazel:phase9_verify")
    if test_index == -1 or verify_index == -1 or test_index > verify_index:
        errors.append("justfile must run phase9_verify_tests before phase9_verify")
    if errors:
        raise VerificationError("\n".join(errors))


def check_manifests() -> None:
    checks = [
        check_connect_manifest,
        check_wui_manifest,
        check_transfer_manifest,
        check_network_services_manifest,
        check_concern_dispositions,
    ]
    collect_errors(checks)


def check_security_contract() -> None:
    collect_errors([check_secret_markers, check_no_phase9_overclaim])


def check_quick() -> None:
    collect_errors(
        [
            check_connect_manifest,
            check_wui_manifest,
            check_transfer_manifest,
            check_network_services_manifest,
            check_concern_dispositions,
            check_network_rust_api_surface,
            check_validation_contract,
            check_bazel_surface,
            check_just_surface,
            check_secret_markers,
            check_no_phase9_overclaim,
        ]
    )


def run_command(command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        joined = " ".join(command)
        raise VerificationError(f"{joined} failed with exit code {result.returncode}\n{result.stdout}")


def check_all() -> None:
    check_quick()
    if shutil.which("cargo") is None:
        raise VerificationError("cargo is required for --all")
    run_command(["cargo", "fmt", "--all", "--check"])
    run_command(["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"])
    run_command(["cargo", "build", "--all-targets", "--all-features"])
    run_command(["cargo", "test", "--all-features"])


def collect_errors(checks: list[Callable[[], None]]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 9 network/web/transfer parity artifacts.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--quick", action="store_true", help="run local static Phase 9 verification")
    modes.add_argument("--all", action="store_true", help="run static verification plus Rust checks")
    modes.add_argument("--manifests-only", action="store_true", help="verify only Phase 9 manifests")
    modes.add_argument("--rust-only", action="store_true", help="verify only Rust domain API surface")
    modes.add_argument("--security-only", action="store_true", help="verify only secret and overclaim guards")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.all:
        check = check_all
    elif args.manifests_only:
        check = check_manifests
    elif args.rust_only:
        check = check_network_rust_api_surface
    elif args.security_only:
        check = check_security_contract
    else:
        check = check_quick

    try:
        check()
    except VerificationError as error:
        print(f"Phase 9 network web services and transfers verification failed:\n{error}", file=sys.stderr)
        return 1

    print("Phase 9 network web services and transfers verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
