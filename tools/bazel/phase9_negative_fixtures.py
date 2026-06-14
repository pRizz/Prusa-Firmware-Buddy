#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "09-network-web-services-and-transfers"
PHASE_LIFECYCLE_ID = "9-2026-06-14T02-15-21"
DEFAULT_CASES = Path("tools/bazel/fixtures/phase9_negative_network_cases.json")

REQUIRED_NEGATIVE_CASE_IDS = [
    "custom-cert-valid-der-intentional-delta",
    "custom-cert-missing-der-preserved-defect",
    "custom-cert-invalid-der-rejected",
    "invalid-certificate-chain-rejected",
    "weak-signature-sha1-md5-dispositioned",
    "duplicate-connect-command-rejected",
    "large-websocket-command-rejected",
    "proxy-tls-only-no-auth-plain-leg-preserved",
    "stalled-network-transfer-timeout-classified",
]

REQUIRED_FIELDS = [
    "id",
    "requirement_id",
    "category",
    "reference_sources",
    "input_fixture",
    "expected_outcome",
    "evidence_class",
    "proof_scope",
    "secret_handling",
    "intentional_delta",
    "runnable_check",
    "phase_lifecycle_id",
]

ALLOWED_REQUIREMENTS = {"IFCE-02", "IFCE-03", "IFCE-02/IFCE-03"}
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
NON_LOCAL_EVIDENCE_CLASSES = {
    "simulator-flow",
    "hardware-smoke",
    "manual-hardware-required",
}
FORBIDDEN_SECRET_MARKERS = [
    "token_value",
    "password_value",
    "wifi_password",
    "certificate_bytes",
    "private_key",
    "BEGIN PRIVATE KEY",
    "raw_crash_dump",
    "crash_dump_payload",
]
FORBIDDEN_BINARY_MARKERS = [
    "-----BEGIN",
    "-----END",
    "der_bytes",
    "certificate_pem",
    "key_material",
]

CUSTOM_CERT_CASE_IDS = {
    "custom-cert-valid-der-intentional-delta",
    "custom-cert-missing-der-preserved-defect",
    "custom-cert-invalid-der-rejected",
}


class FixtureError(Exception):
    pass


def resolve_cases_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    full_path = resolve_cases_path(path)
    if not full_path.exists():
        raise FixtureError(f"missing negative fixture file: {path.as_posix()}")
    try:
        data = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise FixtureError(f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise FixtureError(f"{path.as_posix()} must contain a top-level JSON object")
    return data


def is_empty(value: object) -> bool:
    return value in ("", [], {}, None)


def row_blob(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True)


def require_top_level(data: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    if data.get("schema_version") != 1:
        raise FixtureError(f"{path.as_posix()} must set schema_version to 1")
    if data.get("phase") != PHASE:
        raise FixtureError(f"{path.as_posix()} must set phase to {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise FixtureError(f"{path.as_posix()} must set phase_lifecycle_id to {PHASE_LIFECYCLE_ID}")

    cases = data.get("negative_cases")
    if not isinstance(cases, list):
        raise FixtureError(f"{path.as_posix()} must contain a negative_cases list")

    parsed_cases: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise FixtureError(f"{path.as_posix()} negative_cases[{index}] must be an object")
        parsed_cases.append(case)
    return parsed_cases


def require_fields(case: dict[str, Any], case_name: str) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in case]
    empty = [field for field in REQUIRED_FIELDS if field in case and is_empty(case[field])]
    if missing or empty:
        details = []
        if missing:
            details.append(f"missing required fields: {', '.join(missing)}")
        if empty:
            details.append(f"empty required fields: {', '.join(empty)}")
        raise FixtureError(f"{case_name} " + "; ".join(details))


def require_string(case: dict[str, Any], field: str, case_name: str) -> str:
    value = case.get(field)
    if not isinstance(value, str) or not value:
        raise FixtureError(f"{case_name} {field} must be a non-empty string")
    return value


def require_dict(case: dict[str, Any], field: str, case_name: str) -> dict[str, Any]:
    value = case.get(field)
    if not isinstance(value, dict) or not value:
        raise FixtureError(f"{case_name} {field} must be a non-empty object")
    return value


def require_list_of_strings(case: dict[str, Any], field: str, case_name: str) -> list[str]:
    value = case.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise FixtureError(f"{case_name} {field} must be a non-empty list of strings")
    return value


def require_reference_sources(case: dict[str, Any], case_name: str) -> None:
    root = ROOT.resolve()
    for source_path in require_list_of_strings(case, "reference_sources", case_name):
        relative_path = Path(source_path)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise FixtureError(f"{case_name} reference source must be repo-relative: {source_path}")
        full_path = (root / relative_path).resolve()
        try:
            full_path.relative_to(root)
        except ValueError as error:
            raise FixtureError(f"{case_name} reference source escapes repo: {source_path}") from error
        if not full_path.exists():
            raise FixtureError(f"{case_name} references missing source path: {source_path}")


def require_no_forbidden_markers(case: dict[str, Any], case_name: str) -> None:
    blob = row_blob(case)
    forbidden_markers = [*FORBIDDEN_SECRET_MARKERS, *FORBIDDEN_BINARY_MARKERS]
    found = [marker for marker in forbidden_markers if marker in blob]
    if found:
        raise FixtureError(f"{case_name} contains forbidden markers: {', '.join(found)}")


def require_evidence_scope(case: dict[str, Any], case_name: str) -> None:
    evidence_class = require_string(case, "evidence_class", case_name)
    if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
        allowed = ", ".join(sorted(ALLOWED_EVIDENCE_CLASSES))
        raise FixtureError(f"{case_name} evidence_class must be one of: {allowed}")

    proof_scope = require_string(case, "proof_scope", case_name)
    if proof_scope not in {"local", "non-local"}:
        raise FixtureError(f"{case_name} proof_scope must be local or non-local")
    if proof_scope == "local" and evidence_class in NON_LOCAL_EVIDENCE_CLASSES:
        raise FixtureError(f"{case_name} proof_scope local cannot be paired with {evidence_class} evidence")


def require_common_case_shape(case: dict[str, Any]) -> None:
    case_id = str(case.get("id", "<unknown>"))
    case_name = f"negative case {case_id}"
    require_fields(case, case_name)
    if require_string(case, "requirement_id", case_name) not in ALLOWED_REQUIREMENTS:
        raise FixtureError(f"{case_name} requirement_id must be one of: {', '.join(sorted(ALLOWED_REQUIREMENTS))}")
    if require_string(case, "phase_lifecycle_id", case_name) != PHASE_LIFECYCLE_ID:
        raise FixtureError(f"{case_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
    if require_string(case, "secret_handling", case_name) not in {"none", "named-only-redacted"}:
        raise FixtureError(f"{case_name} secret_handling must be none or named-only-redacted")
    if require_string(case, "intentional_delta", case_name) not in {"none", "approved", "blocked"}:
        raise FixtureError(f"{case_name} intentional_delta must be none, approved, or blocked")
    require_string(case, "category", case_name)
    require_string(case, "runnable_check", case_name)
    require_dict(case, "input_fixture", case_name)
    require_dict(case, "expected_outcome", case_name)
    require_reference_sources(case, case_name)
    require_no_forbidden_markers(case, case_name)
    require_evidence_scope(case, case_name)


def require_text(case: dict[str, Any], needles: list[str], case_name: str) -> None:
    blob = row_blob(case)
    missing = [needle for needle in needles if needle not in blob]
    if missing:
        raise FixtureError(f"{case_name} missing required text: {', '.join(missing)}")


def require_case_specific_contracts(case_by_id: dict[str, dict[str, Any]]) -> None:
    errors: list[str] = []
    for case_id in CUSTOM_CERT_CASE_IDS:
        case_name = f"negative case {case_id}"
        try:
            require_text(case_by_id[case_id], ["/internal/connect/connect.der"], case_name)
            if case_by_id[case_id].get("secret_handling") != "named-only-redacted":
                raise FixtureError(f"{case_name} must keep custom certificate evidence named-only redacted")
        except FixtureError as error:
            errors.append(str(error))

    try:
        valid_der_case = case_by_id["custom-cert-valid-der-intentional-delta"]
        if valid_der_case.get("intentional_delta") != "approved":
            raise FixtureError("negative case custom-cert-valid-der-intentional-delta must be an approved intentional delta fixture")
        if valid_der_case.get("proof_scope") != "non-local":
            raise FixtureError("negative case custom-cert-valid-der-intentional-delta must remain non-local")
    except FixtureError as error:
        errors.append(str(error))

    checks = {
        "custom-cert-missing-der-preserved-defect": ["preserved-defect", "preserved_defect"],
        "custom-cert-invalid-der-rejected": ["rejected-invalid-der", "rejected"],
        "invalid-certificate-chain-rejected": ["MBEDTLS_SSL_VERIFY_REQUIRED", "rejected"],
        "weak-signature-sha1-md5-dispositioned": [
            "MBEDTLS_SHA1_C",
            "MBEDTLS_MD5_C",
            "not-accepted-runtime-policy",
        ],
        "duplicate-connect-command-rejected": ["duplicate command id", "Rejected"],
        "large-websocket-command-rejected": ["oversized command frame", "BrokenCommand"],
        "proxy-tls-only-no-auth-plain-leg-preserved": [
            "proxy-authentication-absent",
            "printer-to-proxy-leg-unencrypted",
            "proxy-active-only-when-connect_tls-true",
        ],
        "stalled-network-transfer-timeout-classified": [
            "stalled network transfer",
            "timeout-or-recovery",
            "non-local long-running proof required",
        ],
    }
    for case_id, needles in checks.items():
        try:
            require_text(case_by_id[case_id], needles, f"negative case {case_id}")
        except FixtureError as error:
            errors.append(str(error))

    stalled_case = case_by_id["stalled-network-transfer-timeout-classified"]
    if stalled_case.get("proof_scope") != "non-local":
        errors.append("negative case stalled-network-transfer-timeout-classified must remain non-local")

    if errors:
        raise FixtureError("\n".join(errors))


def validate_fixture(path: Path) -> None:
    data = read_json(path)
    cases = require_top_level(data, path)
    case_by_id: dict[str, dict[str, Any]] = {}
    duplicates: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str):
            raise FixtureError(f"{path.as_posix()} contains negative case with non-string id: {case_id!r}")
        if case_id in case_by_id:
            duplicates.add(case_id)
        case_by_id[case_id] = case

    if duplicates:
        raise FixtureError(f"{path.as_posix()} contains duplicate negative case IDs: {', '.join(sorted(duplicates))}")

    missing_cases = sorted(set(REQUIRED_NEGATIVE_CASE_IDS) - set(case_by_id))
    if missing_cases:
        raise FixtureError("missing required negative case IDs: " + ", ".join(missing_cases))

    errors: list[str] = []
    for case in cases:
        try:
            require_common_case_shape(case)
        except FixtureError as error:
            errors.append(str(error))

    try:
        require_case_specific_contracts(case_by_id)
    except FixtureError as error:
        errors.append(str(error))

    if errors:
        raise FixtureError("\n".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase 9 negative network fixture cases.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="negative case JSON file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        validate_fixture(args.cases)
    except FixtureError as error:
        print(f"Phase 9 negative network fixture validation failed:\n{error}", file=sys.stderr)
        return 1

    print("Phase 9 negative network fixture validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
