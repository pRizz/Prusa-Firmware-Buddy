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
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "31-final-evidence-intake"
PHASE_LIFECYCLE_ID = "31-2026-07-03T02-04-07"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase31_final_evidence_intake_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase31")
STREAM_ORDER = ["simulator", "hardware-media-safety", "live-service", "release-signing"]
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
REF_LIST_FIELDS = {"artifact_refs", "retention_refs", "validator_output_refs"}
REF_STRING_FIELDS = {"artifact_ref", "manifest_ref"}
FORBIDDEN_FIELD_NAMES = {
    "api_key",
    "api_key_value",
    "binary_dump",
    "binary_dump_bytes",
    "certificate_bytes",
    "certificate_pem",
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
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-block", re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
    (
        "forbidden-evidence-marker",
        re.compile(
            r"\b(api[_-]?key[_-]?value|certificate[_-]?pem|credential[_-]?value|password[_-]?value|"
            r"private[_-]?certificate|private[_-]?key|raw[_-]?crash[_-]?dump|raw[_-]?logs?|"
            r"secret[_-]?value|service[_-]?payload|signing[_-]?key[_-]?value|"
            r"signing[_-]?payload[_-]?bytes|tls[_-]?keylog|token[_-]?value|wi[-_ ]?fi credential)\b",
            re.IGNORECASE,
        ),
    ),
)


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


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = require_list(row, field, row_name)
    if not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_dict(row: dict[str, Any], field: str, row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_repo_relative_path(path_value: str | Path, row_name: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} must be repo-relative and cannot traverse: {path_value}")
    return relative_path


def require_path_under(path_value: str | Path, root_path: Path, row_name: str) -> Path:
    relative_path = require_repo_relative_path(path_value, row_name)
    try:
        relative_path.relative_to(root_path)
    except ValueError as error:
        raise VerificationError(f"{row_name} must stay under {root_path.as_posix()}: {relative_path.as_posix()}") from error
    return relative_path


def require_existing_file(root: Path, path_value: str | Path, row_name: str) -> Path:
    relative_path = require_repo_relative_path(path_value, row_name)
    if not (root / relative_path).is_file():
        raise VerificationError(f"{row_name} file not found: {relative_path.as_posix()}")
    return relative_path


def output_dir_under_default(path_value: str | Path) -> Path:
    relative_path = require_path_under(path_value, DEFAULT_OUTPUT_DIR, "--output-dir")
    return relative_path


def reset_output_root(root: Path, output_dir: Path) -> Path:
    relative_output_dir = output_dir_under_default(output_dir)
    full_output_dir = root / relative_output_dir
    if full_output_dir.exists():
        if full_output_dir.is_symlink() or not full_output_dir.is_dir():
            raise VerificationError(f"--output-dir exists and is not a normal directory: {relative_output_dir.as_posix()}")
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)
    return relative_output_dir


def normalized_field_name(field_name: str) -> str:
    return field_name.replace("-", "_").casefold()


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(key for key in value if normalized_field_name(key) in FORBIDDEN_FIELD_NAMES)
        if forbidden:
            raise VerificationError(f"{path} contains forbidden evidence fields: {', '.join(forbidden)}")
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
            errors.append(f"{path.as_posix()} contains forbidden evidence marker: {label}")
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


def validate_artifact_ref(ref: str, adapter: dict[str, Any], row_name: str) -> None:
    allowed_roots = require_list_of_strings(adapter, "allowed_ref_roots", f"{adapter['stream']} adapter")
    for allowed_root in allowed_roots:
        if allowed_root.startswith("external://"):
            if ref.startswith(allowed_root) and len(ref) > len(allowed_root):
                return
            continue
        if ref.startswith(allowed_root):
            relative_ref = require_repo_relative_path(ref, row_name)
            require_path_under(relative_ref, Path(allowed_root), row_name)
            return
    raise VerificationError(f"{row_name} ref must stay within allowed roots {allowed_roots}: {ref}")


def validate_refs_in_json(value: Any, adapter: dict[str, Any], row_name: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REF_LIST_FIELDS:
                if not isinstance(child, list) or not all(isinstance(item, str) and item for item in child):
                    raise VerificationError(f"{row_name} {key} must be a list of non-empty strings")
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
            raise VerificationError("contract stream_adapters entries must be objects")
        stream = require_string(adapter, "stream", "stream_adapter")
        if stream in by_stream:
            raise VerificationError(f"duplicate stream adapter: {stream}")
        by_stream[stream] = adapter
    return by_stream


def check_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    if contract.get("id") != "phase31_final_evidence_intake_contract":
        errors.append("contract id must be phase31_final_evidence_intake_contract")
    if contract.get("artifact_name") != "phase31-final-evidence-intake":
        errors.append("artifact_name must be phase31-final-evidence-intake")
    if contract.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}")
    if contract.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        errors.append(f"phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
    if contract.get("output_root") != DEFAULT_OUTPUT_DIR.as_posix():
        errors.append(f"output_root must be {DEFAULT_OUTPUT_DIR.as_posix()}")
    if set(require_list_of_strings(contract, "requirement_ids", "contract")) != REQUIRED_REQUIREMENT_IDS:
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
        for source_contract in require_list(contract, "source_contracts", "contract")
        if isinstance(source_contract, dict)
    }
    for source_contract in SOURCE_CONTRACTS:
        if source_contract not in source_contract_paths:
            errors.append(f"missing source contract reference: {source_contract}")
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
        if isinstance(source_contract, str) and source_contract not in SOURCE_CONTRACTS:
            errors.append(f"{stream} adapter source_contract is not a Phase 23-26 source contract")
        validator = adapter.get("validator")
        if isinstance(validator, str) and not (root / validator).is_file():
            errors.append(f"{stream} adapter validator file not found: {validator}")
        output_root = adapter.get("output_root")
        if isinstance(output_root, str):
            expected_local_root = output_root.rstrip("/") + "/"
            allowed_roots = adapter.get("allowed_ref_roots", [])
            if expected_local_root not in allowed_roots:
                errors.append(f"{stream} adapter allowed_ref_roots must include {expected_local_root}")
        if stream == "release-signing":
            if "upstream_row_table" not in adapter:
                errors.append("release-signing adapter missing upstream_row_table")
        elif "upstream_row" not in adapter:
            errors.append(f"{stream} adapter missing upstream_row")
    generated = set(require_list_of_strings(contract, "generated_artifacts", "contract"))
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
            raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} contains forbidden evidence marker: {label}")


def require_file_contains(root: Path, path: Path, needles: list[str]) -> list[str]:
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    return [f"{path.as_posix()} missing required wiring text: {needle}" for needle in needles if needle not in text]


def shell_case_commands(text: str, case_name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{case_name})":
            continue
        commands: list[str] = []
        for body_line in lines[index + 1:]:
            stripped = body_line.strip()
            if stripped == ";;":
                return commands
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
        return None
    return None


def just_recipe_commands(text: str, recipe_name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{recipe_name}:":
            continue
        commands: list[str] = []
        for body_line in lines[index + 1:]:
            if body_line and not body_line[0].isspace():
                break
            stripped = body_line.strip()
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
        return commands
    return None


def missing_required_items(location: str, actual: list[str], expected: list[str]) -> list[str]:
    actual_values = set(actual)
    return [f"{location} missing required wiring item: {item}" for item in expected if item not in actual_values]


def check_command_order(location: str, commands: list[str], first: str, second: str, message: str) -> list[str]:
    if first not in commands or second not in commands:
        return []
    if commands.index(first) <= commands.index(second):
        return []
    return [f"{location} {message}"]


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    tools_manifest_refs = [
        Path(manifest).relative_to("tools/bazel").as_posix()
        for manifest in [*SOURCE_CONTRACTS, CONTRACT_MANIFEST.as_posix()]
    ]
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase31_final_evidence_intake_docs"',
                'name = "phase31_verify"',
                'actual = "//tools/bazel:phase31_verify"',
                'name = "phase31_verify_tests"',
                'actual = "//tools/bazel:phase31_verify_tests"',
                *[f'"{doc}"' for doc in PHASE31_DOCS],
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase31_source_ref_manifests"',
                'name = "phase31_verify"',
                'name = "phase31_verify_tests"',
                "phase31_final_evidence_intake.py",
                "phase31_final_evidence_intake_test.py",
                "phase31_final_evidence_intake_contract.json",
                "//:phase31_final_evidence_intake_docs",
                *[f'"{manifest}"' for manifest in tools_manifest_refs],
            ],
        )
    )
    try:
        workflow_text = read_text(root, Path("tools/bazel/rust_workflow.sh"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        verify_commands = shell_case_commands(workflow_text, "phase31_verify")
        test_commands = shell_case_commands(workflow_text, "phase31_verify_tests")
        if verify_commands is None:
            errors.append("tools/bazel/rust_workflow.sh phase31_verify case arm missing")
        else:
            errors.extend(missing_required_items("tools/bazel/rust_workflow.sh phase31_verify case arm", verify_commands, PHASE31_VERIFY_COMMANDS))
            errors.extend(
                check_command_order(
                    "tools/bazel/rust_workflow.sh phase31_verify case arm",
                    verify_commands,
                    PHASE31_VERIFY_COMMANDS[0],
                    PHASE31_VERIFY_COMMANDS[1],
                    "must run --wiring-only before --quick",
                )
            )
        if test_commands is None:
            errors.append("tools/bazel/rust_workflow.sh phase31_verify_tests case arm missing")
        else:
            errors.extend(missing_required_items("tools/bazel/rust_workflow.sh phase31_verify_tests case arm", test_commands, [PHASE31_TEST_COMMAND]))
    try:
        just_text = read_text(root, Path("justfile"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        just_commands = just_recipe_commands(just_text, "phase31-verify")
        test_line = "bazel run //tools/bazel:phase31_verify_tests"
        verify_line = "bazel run //tools/bazel:phase31_verify"
        if just_commands is None:
            errors.append("justfile phase31-verify recipe missing")
        else:
            errors.extend(missing_required_items("justfile phase31-verify recipe", just_commands, [test_line, verify_line]))
            errors.extend(
                check_command_order(
                    "justfile phase31-verify recipe",
                    just_commands,
                    test_line,
                    verify_line,
                    "must run tests before verifier",
                )
            )
    if errors:
        raise VerificationError("\n".join(errors))


def validate_raw_input(root: Path, path_value: str, row_name: str) -> tuple[Path, str]:
    relative_path = require_existing_file(root, path_value, row_name)
    text = read_text(root, relative_path)
    reject_forbidden_text(relative_path, text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"{relative_path.as_posix()} is not valid JSON evidence: {error}") from error
    reject_secret_bearing_json(relative_path, data)
    return relative_path, file_sha256(root, relative_path)


def run_source_validator(root: Path, adapter: dict[str, Any], raw_input_path: Path, maybe_upstream_rows: dict[str, Path]) -> list[str]:
    validator = require_string(adapter, "validator", f"{adapter['stream']} adapter")
    validator_path = root / validator
    output_root = require_string(adapter, "output_root", f"{adapter['stream']} adapter")
    if adapter["stream"] == "release-signing":
        command = [
            sys.executable,
            validator_path.as_posix(),
            "--quick",
            "--release-input",
            raw_input_path.as_posix(),
            "--output-dir",
            output_root,
        ]
        row_flags = [
            ("phase23_simulator_row", "--phase23-simulator-row"),
            ("phase24_hardware_media_safety_row", "--phase24-hardware-media-safety-row"),
            ("phase25_live_service_row", "--phase25-live-service-row"),
        ]
        for key, flag in row_flags:
            maybe_path = maybe_upstream_rows.get(key)
            if maybe_path is not None:
                command.extend([flag, maybe_path.as_posix()])
    else:
        command = [
            sys.executable,
            validator_path.as_posix(),
            require_string(adapter, "source_validator_input_flag", f"{adapter['stream']} adapter"),
            raw_input_path.as_posix(),
            "--output-dir",
            output_root,
        ]
    result = subprocess.run(
        command,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        raise VerificationError(
            f"{adapter['stream']} source validator failed with exit {result.returncode}:\n{result.stdout.strip()}"
        )
    return [
        "python3",
        validator,
        *command[2:],
    ]


def retained_output_dir(root: Path, adapter: dict[str, Any], path_value: str | Path) -> Path:
    output_root = Path(require_string(adapter, "output_root", f"{adapter['stream']} adapter"))
    relative_path = require_path_under(path_value, output_root, f"{adapter['stream']} retained output")
    if not (root / relative_path).is_dir():
        raise VerificationError(f"{adapter['stream']} retained output directory not found: {relative_path.as_posix()}")
    return relative_path


def status_field(rows: list[dict[str, Any]], field: str, default: str) -> str:
    values = sorted({str(row.get(field, default)) for row in rows if row.get(field, default) not in ("", None)})
    if not values:
        return default
    if len(values) == 1:
        return values[0]
    return "mixed"


def collect_artifact_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REF_LIST_FIELDS and isinstance(child, list):
                refs.extend(str(item) for item in child if isinstance(item, str) and item)
            elif key in REF_STRING_FIELDS and isinstance(child, str) and child:
                refs.append(child)
            else:
                refs.extend(collect_artifact_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(collect_artifact_refs(child))
    return list(dict.fromkeys(refs))


def validate_source_row(row: dict[str, Any], adapter: dict[str, Any], row_name: str) -> tuple[str, str, str]:
    reject_secret_bearing_json(Path(row_name), row)
    validate_refs_in_json(row, adapter, row_name)
    if row.get("redaction_status") != "passed":
        raise VerificationError(f"{row_name} redaction_status must be passed")
    if row.get("source_ref_status") != "passed":
        raise VerificationError(f"{row_name} source_ref_status must be passed")
    maybe_lifecycle_status = row.get("source_lifecycle_status")
    if maybe_lifecycle_status not in (None, "current", "not-required"):
        raise VerificationError(f"{row_name} source_lifecycle_status must be current or not-required")
    return (
        str(row.get("redaction_status", "passed")),
        str(row.get("source_ref_status", "passed")),
        str(row.get("exception_status", "none")),
    )


def validate_stream_output(
    root: Path,
    adapter: dict[str, Any],
    output_dir: Path,
    submitter_identity_ref: str,
    validator_command: list[str],
    packet_sha256: str,
) -> tuple[dict[str, Any], Path]:
    stream = require_string(adapter, "stream", "adapter")
    manifest_path = output_dir / require_string(adapter, "manifest", f"{stream} adapter")
    manifest = load_json(root, manifest_path)
    reject_secret_bearing_json(manifest_path, manifest)
    validate_refs_in_json(manifest, adapter, f"{stream} manifest")
    expected_lifecycle_id = require_string(adapter, "source_lifecycle_id", f"{stream} adapter")
    if manifest.get("phase_lifecycle_id") != expected_lifecycle_id:
        raise VerificationError(f"{stream} manifest phase_lifecycle_id must be {expected_lifecycle_id}")
    real_evidence_flag = require_string(adapter, "real_evidence_flag", f"{stream} adapter")
    if not require_bool(manifest, real_evidence_flag, f"{stream} manifest"):
        raise VerificationError(f"{stream} manifest {real_evidence_flag} must be true for final intake")
    if str(manifest.get("command_mode", "")).casefold() in {"quick-placeholder", "default-placeholder", "local-smoke"}:
        raise VerificationError(f"{stream} manifest command_mode is non-final: {manifest.get('command_mode')}")

    if stream == "release-signing":
        upstream_path = output_dir / require_string(adapter, "upstream_row_table", f"{stream} adapter")
        row_table = load_json(root, upstream_path)
        rows = require_list(row_table, "rows", "release-signing upstream row table")
        if not rows or not all(isinstance(row, dict) for row in rows):
            raise VerificationError("release-signing upstream row table rows must contain objects")
        for row in rows:
            validate_source_row(row, adapter, f"{stream} upstream row {row.get('criterion_id', '<missing>')}")
        redaction_status = status_field(rows, "redaction_status", "passed")
        source_ref_status = status_field(rows, "source_ref_status", "passed")
        exception_status = status_field(rows, "exception_status", "none")
        failure_reason = "; ".join(
            str(row.get("failure_reason"))
            for row in rows
            if isinstance(row, dict) and row.get("status") not in {"passed", "not-required"} and row.get("failure_reason")
        )
        artifact_reference_summary_path = output_dir / "artifact-reference-summary.json"
        if (root / artifact_reference_summary_path).is_file():
            artifact_reference_summary = load_json(root, artifact_reference_summary_path)
            reject_secret_bearing_json(artifact_reference_summary_path, artifact_reference_summary)
            validate_refs_in_json(artifact_reference_summary, adapter, "release-signing artifact reference summary")
        else:
            artifact_reference_summary = {"artifact_refs": collect_artifact_refs(rows)}
    else:
        upstream_path = output_dir / require_string(adapter, "upstream_row", f"{stream} adapter")
        row = load_json(root, upstream_path)
        redaction_status, source_ref_status, exception_status = validate_source_row(row, adapter, f"{stream} upstream row")
        failure_reason = str(row.get("failure_reason", ""))
        artifact_reference_summary = {"artifact_refs": collect_artifact_refs(row)}

    receipt = {
        "artifact_reference_summary": artifact_reference_summary,
        "consumed_upstream_row_refs": [upstream_path.as_posix()],
        "exception_status": exception_status,
        "failure_reason": failure_reason,
        "finality_status": "accepted-final",
        "packet_sha256": packet_sha256,
        "receipt_generated_at_utc": utc_now(),
        "redaction_status": redaction_status,
        "requirement_ids": require_list_of_strings(adapter, "requirement_ids", f"{stream} adapter"),
        "source_contract": require_string(adapter, "source_contract", f"{stream} adapter"),
        "source_phase": require_string(adapter, "source_phase", f"{stream} adapter"),
        "source_ref_status": source_ref_status,
        "stream": stream,
        "submission_id": f"phase31-{stream}-{packet_sha256[:12]}",
        "submitter_identity_ref": submitter_identity_ref,
        "validator_command": validator_command,
        "validator_output_refs": [manifest_path.as_posix(), upstream_path.as_posix()],
    }
    return receipt, upstream_path


def rejection(stream: str, reason: str, submitter_identity_ref: str = "") -> dict[str, Any]:
    reason_digest = hashlib.sha256(reason.encode("utf-8")).hexdigest()[:12]
    return {
        "finality_status": "rejected-final",
        "reason": reason,
        "receipt_generated_at_utc": utc_now(),
        "stream": stream,
        "submission_id": f"phase31-{stream}-rejected-{reason_digest}",
        "submitter_identity_ref": submitter_identity_ref,
    }


def quick_rejections(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for stream in STREAM_ORDER:
        adapter = contract_adapters(contract)[stream]
        row = rejection(
            stream,
            "quick/default Phase 31 execution is a workflow smoke check and is quarantined as non-final evidence",
        )
        row["finality_status"] = "quarantined-non-final"
        row["requirement_ids"] = require_list_of_strings(adapter, "requirement_ids", f"{stream} adapter")
        rows.append(row)
    return rows


def copy_contract_snapshots(root: Path, output_dir: Path) -> None:
    snapshots_dir = root / output_dir / "contract-snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    for snapshot in [CONTRACT_MANIFEST, *[Path(path) for path in SOURCE_CONTRACTS]]:
        shutil.copy2(root / snapshot, snapshots_dir / snapshot.name)


def write_phase31_outputs(root: Path, output_dir: Path, receipts: list[dict[str, Any]], rejected: list[dict[str, Any]]) -> None:
    receipt_refs: list[str] = []
    receipts_dir = output_dir / "stream-receipts"
    for receipt in receipts:
        stream = require_string(receipt, "stream", "receipt")
        receipt_name = {
            "simulator": "simulator-final-intake-receipt.json",
            "hardware-media-safety": "hardware-media-safety-final-intake-receipt.json",
            "live-service": "live-service-final-intake-receipt.json",
            "release-signing": "release-signing-final-intake-receipt.json",
        }[stream]
        receipt_path = receipts_dir / receipt_name
        write_json(root, receipt_path, receipt)
        receipt_refs.append(receipt_path.as_posix())
    rejected_path = output_dir / "rejected-submissions.json"
    write_json(
        root,
        rejected_path,
        {
            "generated_at_utc": utc_now(),
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "rejected_submissions": rejected,
        },
    )
    copy_contract_snapshots(root, output_dir)
    finality_status = "accepted-final" if receipts and not rejected else "quarantined-non-final"
    if rejected and any(row.get("finality_status") == "rejected-final" for row in rejected):
        finality_status = "rejected-final"
    manifest = {
        "accepted_count": len(receipts),
        "artifact_name": "phase31-final-evidence-intake",
        "finality_status": finality_status,
        "generated_at_utc": utc_now(),
        "output_root": output_dir.as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "receipt_refs": receipt_refs,
        "rejected_count": len(rejected),
        "rejected_submissions_ref": rejected_path.as_posix(),
        "streams": [
            {
                "finality_status": receipt["finality_status"],
                "receipt_ref": receipt_refs[index],
                "stream": receipt["stream"],
                "submission_id": receipt["submission_id"],
            }
            for index, receipt in enumerate(receipts)
        ],
    }
    write_json(root, output_dir / "final-intake-manifest.json", manifest)


def run_quick(root: Path, output_dir: Path) -> None:
    contract = check_contract(root)
    check_security(root)
    relative_output_dir = reset_output_root(root, output_dir)
    write_phase31_outputs(root, relative_output_dir, [], quick_rejections(contract))


def process_submission(root: Path, args: argparse.Namespace) -> None:
    contract = check_contract(root)
    check_security(root)
    adapters = contract_adapters(contract)
    relative_output_dir = reset_output_root(root, Path(args.output_dir))
    submitter_identity_ref = str(args.submitter_identity_ref or "")
    raw_by_stream = {
        "simulator": args.simulator_evidence_input,
        "hardware-media-safety": args.hardware_media_safety_evidence_input,
        "live-service": args.live_service_evidence_input,
        "release-signing": args.release_input,
    }
    retained_by_stream = {
        "simulator": args.phase23_retained_output,
        "hardware-media-safety": args.phase24_retained_output,
        "live-service": args.phase25_retained_output,
        "release-signing": args.phase26_retained_output,
    }
    upstream_rows: dict[str, Path] = {}
    for key, path_value in [
        ("phase23_simulator_row", args.phase23_simulator_row),
        ("phase24_hardware_media_safety_row", args.phase24_hardware_media_safety_row),
        ("phase25_live_service_row", args.phase25_live_service_row),
    ]:
        if path_value:
            upstream_rows[key] = require_existing_file(root, path_value, key)

    receipts: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for stream in STREAM_ORDER:
        adapter = adapters[stream]
        raw_path_value = raw_by_stream[stream]
        retained_path_value = retained_by_stream[stream]
        if not raw_path_value and not retained_path_value:
            continue
        if raw_path_value and retained_path_value:
            rejected.append(rejection(stream, "raw input and retained output registration are mutually exclusive", submitter_identity_ref))
            continue
        if not submitter_identity_ref:
            rejected.append(rejection(stream, "submitter_identity_ref is required for final evidence intake"))
            continue
        try:
            if raw_path_value:
                raw_path, packet_hash = validate_raw_input(root, raw_path_value, f"{stream} raw input")
                command = run_source_validator(root, adapter, raw_path, upstream_rows)
                source_output_dir = Path(require_string(adapter, "output_root", f"{stream} adapter"))
            else:
                source_output_dir = retained_output_dir(root, adapter, retained_path_value)
                manifest_path = source_output_dir / require_string(adapter, "manifest", f"{stream} adapter")
                if stream == "release-signing":
                    row_path = source_output_dir / require_string(adapter, "upstream_row_table", f"{stream} adapter")
                else:
                    row_path = source_output_dir / require_string(adapter, "upstream_row", f"{stream} adapter")
                for required_path in [manifest_path, row_path]:
                    if not (root / required_path).is_file():
                        raise VerificationError(f"missing required file: {required_path.as_posix()}")
                packet_hash = paths_sha256(root, [manifest_path, row_path])
                command = ["registered-retained-output", source_output_dir.as_posix()]
            receipt, upstream_path = validate_stream_output(root, adapter, source_output_dir, submitter_identity_ref, command, packet_hash)
            receipts.append(receipt)
            if stream == "simulator":
                upstream_rows["phase23_simulator_row"] = upstream_path
            elif stream == "hardware-media-safety":
                upstream_rows["phase24_hardware_media_safety_row"] = upstream_path
            elif stream == "live-service":
                upstream_rows["phase25_live_service_row"] = upstream_path
        except VerificationError as error:
            rejected.append(rejection(stream, str(error), submitter_identity_ref))
    write_phase31_outputs(root, relative_output_dir, receipts, rejected)
    if rejected:
        reasons = "\n".join(f"- {row['stream']}: {row['reason']}" for row in rejected)
        raise VerificationError(f"Phase 31 rejected final submissions:\n{reasons}")


def submission_requested(args: argparse.Namespace) -> bool:
    return any(
        [
            args.simulator_evidence_input,
            args.hardware_media_safety_evidence_input,
            args.live_service_evidence_input,
            args.release_input,
            args.phase23_retained_output,
            args.phase24_retained_output,
            args.phase25_retained_output,
            args.phase26_retained_output,
        ]
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase 31 final evidence intake receipts over Phase 23-26 outputs.")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 31 wrapper contract")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 31 checked-in policy for raw secret blocks")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel, rust workflow, and just wiring")
    parser.add_argument("--quick", action="store_true", help="write quarantined non-final smoke outputs")
    parser.add_argument("--simulator-evidence-input", help="sanitized final simulator evidence packet for Phase 23")
    parser.add_argument("--hardware-media-safety-evidence-input", help="sanitized final hardware/media/safety packet for Phase 24")
    parser.add_argument("--live-service-evidence-input", help="sanitized final live-service packet for Phase 25")
    parser.add_argument("--release-input", help="sanitized final release/signing/provenance packet for Phase 26")
    parser.add_argument("--phase23-retained-output", help="repo-relative Phase 23 retained output directory")
    parser.add_argument("--phase24-retained-output", help="repo-relative Phase 24 retained output directory")
    parser.add_argument("--phase25-retained-output", help="repo-relative Phase 25 retained output directory")
    parser.add_argument("--phase26-retained-output", help="repo-relative Phase 26 retained output directory")
    parser.add_argument("--phase23-simulator-row", help="optional Phase 23 upstream row for release intake")
    parser.add_argument("--phase24-hardware-media-safety-row", help="optional Phase 24 upstream row for release intake")
    parser.add_argument("--phase25-live-service-row", help="optional Phase 25 upstream row for release intake")
    parser.add_argument("--submitter-identity-ref", help="opaque non-secret identity reference recorded as provenance")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 31 output directory")
    args = parser.parse_args(argv)
    explicit_mode_count = sum(bool(mode) for mode in [args.contract_only, args.security_only, args.wiring_only, args.quick])
    requested_submission = submission_requested(args)
    if explicit_mode_count + int(requested_submission) != 1:
        parser.error("select exactly one mode: contract/security/wiring/quick or final evidence submission")
    upstream_rows_requested = any([args.phase23_simulator_row, args.phase24_hardware_media_safety_row, args.phase25_live_service_row])
    if upstream_rows_requested and not args.release_input:
        parser.error("Phase 23-25 upstream row flags are only valid with --release-input")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 31 final evidence intake contract passed")
        elif args.security_only:
            check_security(ROOT)
            print("Phase 31 final evidence intake security scan passed")
        elif args.wiring_only:
            check_wiring(ROOT)
            print("Phase 31 final evidence intake wiring passed")
        elif args.quick:
            run_quick(ROOT, Path(args.output_dir))
            print("Phase 31 final evidence intake quick validation passed")
        else:
            process_submission(ROOT, args)
            print("Phase 31 final evidence intake accepted final submissions")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
