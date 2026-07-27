#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "31-final-evidence-intake"
PHASE_LIFECYCLE_ID = "31-2026-07-03T02-04-07"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase31_final_evidence_intake_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase31")
STREAM_ORDER = [
    "simulator", "hardware-media-safety", "live-service", "release-signing"
]
REQUIRED_STREAMS = set(STREAM_ORDER)
REQUIRED_REQUIREMENT_IDS = {"INTAKE-01", "INTAKE-02", "INTAKE-03", "INTAKE-04"}
SOURCE_CONTRACTS = [
    "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json",
    "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
    "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json",
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json",
]
PHASE31_DOCS = [
    ".planning/phases/31-final-evidence-intake/31-CONTEXT.md",
    ".planning/phases/31-final-evidence-intake/31-RESEARCH.md",
    ".planning/phases/31-final-evidence-intake/31-VALIDATION.md",
    ".planning/phases/31-final-evidence-intake/31-01-PLAN.md",
]
PHASE31_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase31_final_evidence_intake.py --wiring-only",
    "python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31",
]
PHASE31_TEST_COMMAND = "python3 tools/bazel/phase31_final_evidence_intake_test.py"
REF_LIST_FIELDS = {
    "artifact_refs", "evidence_refs", "retention_refs", "validator_output_refs"
}
REF_STRING_FIELDS = {"artifact_ref", "manifest_ref"}
PHASE31_ALLOWED_SOURCE_REF_ROOTS = [
    "build/ci-evidence/phase20/",
    "build/ci-evidence/phase23/",
    "build/ci-evidence/phase24/",
    "build/ci-evidence/phase25/",
    "build/ci-evidence/phase26/",
    "external://phase20/",
    "external://phase23/",
    "external://phase24/",
    "external://phase25/",
    "external://phase26/",
]
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api_key",
    "api_key_value",
    "auth_header",
    "authorization_header",
    "binary_dump",
    "binary_dump_bytes",
    "certificate_bytes",
    "certificate_pem",
    "client_secret",
    "connect_token",
    "cookie_header",
    "credential",
    "credential_value",
    "crash_dump_bytes",
    "firmware_payload",
    "firmware_payload_bytes",
    "password",
    "password_value",
    "private_certificate",
    "private_certificate_pem",
    "private_key",
    "raw_crash_dump",
    "raw_firmware_payload",
    "raw_key_bytes",
    "raw_log",
    "raw_log_bytes",
    "raw_logs",
    "secret",
    "secret_value",
    "service_payload",
    "service_payload_bytes",
    "signing_key_value",
    "signing_payload_bytes",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-block",
     re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
    (
        "forbidden-evidence-marker",
        re.compile(
            r"\b(access[_-]?token|api[_-]?key[_-]?value|auth(?:orization)?[_-]?header|"
            r"certificate[_-]?pem|client[_-]?secret|connect[_-]?token|cookie[_-]?header|"
            r"credential[_-]?value|password[_-]?value|"
            r"private[_-]?certificate|private[_-]?key|raw[_-]?crash[_-]?dump|raw[_-]?logs?|"
            r"secret[_-]?value|service[_-]?payload|signing[_-]?key[_-]?value|"
            r"signing[_-]?payload[_-]?bytes|tls[_-]?keylog|token[_-]?value|"
            r"wi[-_ ]?fi credential|wifi[_-]?password)\b",
            re.IGNORECASE,
        ),
    ),
)


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


def require_bool(row: dict[str, Any], field: str, row_name: str) -> bool:
    value = row.get(field)
    if not isinstance(value, bool):
        raise VerificationError(f"{row_name} {field} must be a boolean")
    return value


def require_list(row: dict[str, Any], field: str, row_name: str) -> list[Any]:
    value = row.get(field)
    if not isinstance(value, list):
        raise VerificationError(f"{row_name} {field} must be a list")
    return value


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = require_list(row, field, row_name)
    if not all(isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_dict(row: dict[str, Any], field: str,
                 row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_repo_relative_path(path_value: str | Path, row_name: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} must be repo-relative and cannot traverse: {path_value}"
        )
    return relative_path


def require_path_under(path_value: str | Path, root_path: Path,
                       row_name: str) -> Path:
    relative_path = require_repo_relative_path(path_value, row_name)
    try:
        relative_path.relative_to(root_path)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} must stay under {root_path.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


def require_no_symlink_components(root: Path, relative_path: Path,
                                  row_name: str) -> None:
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(
                f"{row_name} cannot contain symlink path component: {relative_path.as_posix()}"
            )


def require_resolved_under(root: Path, path_value: str | Path,
                           allowed_root: Path, row_name: str) -> Path:
    if allowed_root == Path("."):
        relative_path = require_repo_relative_path(path_value, row_name)
    else:
        relative_path = require_path_under(path_value, allowed_root, row_name)
    require_no_symlink_components(root, relative_path, row_name)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(
            f"missing required path: {relative_path.as_posix()}")
    try:
        resolved_path = full_path.resolve(strict=True)
        resolved_root = (root / allowed_root).resolve(strict=True)
    except FileNotFoundError as error:
        raise VerificationError(
            f"missing required path: {relative_path.as_posix()}") from error
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} resolves outside {allowed_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


def require_existing_file_under(root: Path, path_value: str | Path,
                                allowed_root: Path, row_name: str) -> Path:
    relative_path = require_resolved_under(root, path_value, allowed_root,
                                           row_name)
    if not (root / relative_path).is_file():
        raise VerificationError(
            f"{row_name} file not found: {relative_path.as_posix()}")
    return relative_path


def require_existing_file(root: Path, path_value: str | Path,
                          row_name: str) -> Path:
    return require_existing_file_under(root, path_value, Path("."), row_name)


def require_existing_dir_under(root: Path, path_value: str | Path,
                               allowed_root: Path, row_name: str) -> Path:
    relative_path = require_resolved_under(root, path_value, allowed_root,
                                           row_name)
    if not (root / relative_path).is_dir():
        raise VerificationError(
            f"{row_name} directory not found: {relative_path.as_posix()}")
    return relative_path


def output_dir_under_default(path_value: str | Path) -> Path:
    relative_path = require_path_under(path_value, DEFAULT_OUTPUT_DIR,
                                       "--output-dir")
    return relative_path


def reset_output_root(root: Path, output_dir: Path) -> Path:
    relative_output_dir = output_dir_under_default(output_dir)
    require_no_symlink_components(root, relative_output_dir, "--output-dir")
    current = root
    for part in relative_output_dir.parent.parts:
        current = current / part
        if current.exists():
            if current.is_symlink() or not current.is_dir():
                raise VerificationError(
                    f"--output-dir parent is not a normal directory: {relative_output_dir.parent.as_posix()}"
                )
            continue
        current.mkdir()
    resolved_parent = (root / relative_output_dir.parent).resolve(strict=True)
    resolved_allowed_parent = (root /
                               DEFAULT_OUTPUT_DIR.parent).resolve(strict=True)
    try:
        resolved_parent.relative_to(resolved_allowed_parent)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}"
        ) from error
    full_output_dir = root / relative_output_dir
    if full_output_dir.exists():
        if full_output_dir.is_symlink() or not full_output_dir.is_dir():
            raise VerificationError(
                f"--output-dir exists and is not a normal directory: {relative_output_dir.as_posix()}"
            )
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)
    return relative_output_dir


def normalized_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", field_name.casefold())


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted({
            key
            for key in value
            for forbidden_name in FORBIDDEN_FIELD_NAMES
            if normalized_field_name(key) == normalized_field_name(
                forbidden_name) or normalized_field_name(forbidden_name) in
            normalized_field_name(key)
        })
        if forbidden:
            raise VerificationError(
                f"{path} contains forbidden evidence fields: {', '.join(forbidden)}"
            )
        for key, child in value.items():
            reject_forbidden_field_names(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden_field_names(child, f"{path}[{index}]")


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            errors.append(
                f"{path.as_posix()} contains forbidden evidence marker: {label}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def reject_secret_bearing_json(path: Path, value: Any) -> None:
    reject_forbidden_field_names(value, path.as_posix())
    reject_forbidden_text(path, json.dumps(value, sort_keys=True))


def file_sha256(root: Path, path: Path) -> str:
    digest = hashlib.sha256()
    digest.update((root / path).read_bytes())
    return digest.hexdigest()


def paths_sha256(root: Path, paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update((root / path).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def validate_artifact_ref(ref: str, adapter: dict[str, Any],
                          row_name: str) -> None:
    allowed_roots = require_list_of_strings(adapter, "allowed_ref_roots",
                                            f"{adapter['stream']} adapter")
    for allowed_root in allowed_roots:
        if allowed_root.startswith("external://"):
            if ref.startswith(allowed_root):
                suffix = ref[len(allowed_root):]
                suffix_parts = PurePosixPath(suffix).parts
                if suffix and ".." not in suffix_parts and not suffix.startswith(
                        "/"):
                    return
            continue
        if ref.startswith(allowed_root):
            relative_ref = require_repo_relative_path(ref, row_name)
            require_path_under(relative_ref, Path(allowed_root), row_name)
            return
    raise VerificationError(
        f"{row_name} ref must stay within allowed roots {allowed_roots}: {ref}"
    )


def adapter_with_allowed_ref_roots(adapter: dict[str, Any],
                                   allowed_roots: list[str]) -> dict[str, Any]:
    scoped_adapter = dict(adapter)
    scoped_adapter["allowed_ref_roots"] = allowed_roots
    return scoped_adapter


def validate_refs_in_json(value: Any, adapter: dict[str, Any],
                          row_name: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REF_LIST_FIELDS:
                if not isinstance(child, list) or not all(
                        isinstance(item, str) and item for item in child):
                    raise VerificationError(
                        f"{row_name} {key} must be a list of non-empty strings"
                    )
                for ref in child:
                    validate_artifact_ref(ref, adapter, f"{row_name} {key}")
            elif key in REF_STRING_FIELDS and isinstance(child, str) and child:
                validate_artifact_ref(child, adapter, f"{row_name} {key}")
            else:
                validate_refs_in_json(child, adapter, row_name)
        return
    if isinstance(value, list):
        for item in value:
            validate_refs_in_json(item, adapter, row_name)


def contract_adapters(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    adapters = require_list(contract, "stream_adapters", "contract")
    by_stream: dict[str, dict[str, Any]] = {}
    for adapter in adapters:
        if not isinstance(adapter, dict):
            raise VerificationError(
                "contract stream_adapters entries must be objects")
        stream = require_string(adapter, "stream", "stream_adapter")
        if stream in by_stream:
            raise VerificationError(f"duplicate stream adapter: {stream}")
        by_stream[stream] = adapter
    return by_stream


def check_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    if contract.get("id") != "phase31_final_evidence_intake_contract":
        errors.append(
            "contract id must be phase31_final_evidence_intake_contract")
    if contract.get("artifact_name") != "phase31-final-evidence-intake":
        errors.append("artifact_name must be phase31-final-evidence-intake")
    if contract.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}")
    if contract.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        errors.append(f"phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
    if contract.get("output_root") != DEFAULT_OUTPUT_DIR.as_posix():
        errors.append(f"output_root must be {DEFAULT_OUTPUT_DIR.as_posix()}")
    if set(require_list_of_strings(contract, "requirement_ids",
                                   "contract")) != REQUIRED_REQUIREMENT_IDS:
        errors.append("requirement_ids must cover INTAKE-01 through INTAKE-04")
    try:
        adapters_by_stream = contract_adapters(contract)
    except VerificationError as error:
        adapters_by_stream = {}
        errors.append(str(error))
    if set(adapters_by_stream) != REQUIRED_STREAMS:
        errors.append(f"stream_adapters must cover {', '.join(STREAM_ORDER)}")
    source_contract_paths = {
        require_string(source_contract, "path", "source_contract")
        for source_contract in require_list(contract, "source_contracts",
                                            "contract")
        if isinstance(source_contract, dict)
    }
    for source_contract in SOURCE_CONTRACTS:
        if source_contract not in source_contract_paths:
            errors.append(
                f"missing source contract reference: {source_contract}")
        elif not (root / source_contract).is_file():
            errors.append(f"source contract file not found: {source_contract}")
    for stream in STREAM_ORDER:
        adapter = adapters_by_stream.get(stream)
        if adapter is None:
            continue
        for field in [
                "requirement_ids",
                "source_phase",
                "source_lifecycle_id",
                "source_contract",
                "validator",
                "raw_input_flag",
                "source_validator_input_flag",
                "retained_output_flag",
                "output_root",
                "allowed_ref_roots",
                "manifest",
                "real_evidence_flag",
                "receipt_name",
        ]:
            if field not in adapter:
                errors.append(f"{stream} adapter missing {field}")
        source_contract = adapter.get("source_contract")
        if isinstance(source_contract,
                      str) and source_contract not in SOURCE_CONTRACTS:
            errors.append(
                f"{stream} adapter source_contract is not a Phase 23-26 source contract"
            )
        validator = adapter.get("validator")
        if isinstance(validator, str) and not (root / validator).is_file():
            errors.append(
                f"{stream} adapter validator file not found: {validator}")
        output_root = adapter.get("output_root")
        if isinstance(output_root, str):
            expected_local_root = output_root.rstrip("/") + "/"
            allowed_roots = adapter.get("allowed_ref_roots", [])
            if expected_local_root not in allowed_roots:
                errors.append(
                    f"{stream} adapter allowed_ref_roots must include {expected_local_root}"
                )
        if stream == "release-signing":
            if "upstream_row_table" not in adapter:
                errors.append(
                    "release-signing adapter missing upstream_row_table")
        elif "upstream_row" not in adapter:
            errors.append(f"{stream} adapter missing upstream_row")
    generated = set(
        require_list_of_strings(contract, "generated_artifacts", "contract"))
    for artifact in [
            "final-intake-manifest.json",
            "rejected-submissions.json",
            "stream-receipts/simulator-final-intake-receipt.json",
            "stream-receipts/hardware-media-safety-final-intake-receipt.json",
            "stream-receipts/live-service-final-intake-receipt.json",
            "stream-receipts/release-signing-final-intake-receipt.json",
    ]:
        if artifact not in generated:
            errors.append(f"generated_artifacts missing {artifact}")
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def check_security(root: Path) -> None:
    check_contract(root)
    contract_text = read_text(root, CONTRACT_MANIFEST)
    for label, pattern in FORBIDDEN_TEXT_PATTERNS[:2]:
        if pattern.search(contract_text):
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} contains forbidden evidence marker: {label}"
            )
