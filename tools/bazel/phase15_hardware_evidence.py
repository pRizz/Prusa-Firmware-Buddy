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
PHASE = "15-hardware-safety-and-media-qualification"
PHASE_LIFECYCLE_ID = "15-2026-06-17T22-53-45"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase15_hardware_evidence_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase15")
REQUIRED_REQUIREMENT_IDS = {"HARD-01", "HARD-02", "HARD-03"}
REQUIRED_SCENARIO_IDS = {
    "hard-supported-printer-smoke-coreone-xbuddy",
    "hard-supported-printer-smoke-mini-buddy",
    "hard-board-startup-readiness-mk4-xbuddy",
    "hard-board-startup-readiness-xl-xlbuddy-puppies",
    "hard-supported-printer-smoke-mk35-xbuddy",
    "hard-supported-printer-smoke-ix-xbuddy",
    "hard-supported-printer-smoke-xl-dev-kit-xlb",
    "hard-board-startup-readiness-dwarf",
    "hard-board-startup-readiness-modularbed",
    "hard-board-startup-readiness-xl-dev-kit-xlb",
    "hard-storage-usb-fatfs-removable-media",
    "hard-storage-internal-flash-littlefs",
    "hard-storage-bbf-littlefs-resource-image",
    "hard-storage-eeprom-config-store",
    "hard-storage-semihosting",
    "hard-storage-root-libsysbase-dispatch",
    "hard-ui-physical-input-encoder-touch",
    "hard-safety-watchdog-crash-recovery",
    "hard-safety-thermal-motion-emergency-stop",
    "hard-safe-output-fatal-redscreen-bsod",
    "hard-mmu-fault-handling",
    "hard-rs485-modbus-fault-handling",
    "hard-toolchanger-dock-offset-calibration",
    "hard-auxiliary-controller-combination-coreone-xbe",
    "hard-auxiliary-controller-combination-xl-dwarf-modularbed",
    "hard-contract-traceability-and-redaction-boundary",
}
REQUIRED_SUPPORTED_PRINTER_FAMILIES = {"COREONE", "MINI", "MK4", "MK3.5", "XL", "iX", "XL_DEV_KIT"}
REQUIRED_SUPPORTED_BOARDS = {
    "BUDDY",
    "XBUDDY",
    "XLBUDDY",
    "DWARF",
    "MODULARBED",
    "XL_DEV_KIT_XLB",
    "XBUDDY_EXTENSION",
}
REQUIRED_STORAGE_MEDIA_SURFACES = {
    "usb-fatfs-removable-media",
    "internal-littlefs",
    "bbf-littlefs",
    "eeprom-config-store",
    "semihosting",
    "root-libsysbase-dispatch",
}
STATUS_VOCABULARY = [
    "passed",
    "failed",
    "pending-hardware-input",
    "manual-hardware-required",
    "blocked-hardware-unavailable",
    "not-applicable",
    "source-contract-passed",
    "rejected-redaction",
    "rejected-overclaim",
]
HARDWARE_ALLOWED_STATUSES = {
    "pending-hardware-input",
    "manual-hardware-required",
    "blocked-hardware-unavailable",
    "not-applicable",
    "passed",
    "failed",
}
SOURCE_CONTRACT_ALLOWED_STATUSES = {"source-contract-passed", "failed", "rejected-redaction", "rejected-overclaim"}
REQUIRED_OPERATOR_FIELDS = [
    "device",
    "printer_family",
    "board",
    "firmware_build",
    "operator",
    "timestamp",
    "scenario_id",
    "result",
    "artifact_ref",
    "residual_risk",
]
REQUIRED_ARTIFACT_KINDS = {
    "machine-readable-run-manifest",
    "normalized-scenario-results",
    "redacted-hardware-summary",
    "source-contract-snapshot",
    "hardware-log-reference",
    "operator-evidence-input",
}
SOURCE_REF_MANIFESTS = [
    "tools/bazel/manifests/phase6_safety_gates.json",
    "tools/bazel/manifests/phase7_storage_media.json",
    "tools/bazel/manifests/phase8_gui_workflows.json",
    "tools/bazel/manifests/phase8_display_layouts.json",
    "tools/bazel/manifests/phase10_auxiliary_controllers.json",
    "tools/bazel/manifests/phase10_mmu_transport.json",
    "tools/bazel/manifests/phase10_modbus_rs485.json",
    "tools/bazel/manifests/phase10_toolchanger_dock_offsets.json",
    "tools/bazel/manifests/phase10_auxiliary_build_update.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json",
]
REQUIRED_SCENARIO_FIELDS = [
    "id",
    "title",
    "requirement_ids",
    "v1_requirement_ids",
    "source_contract_refs",
    "printer_family",
    "board",
    "media_surface",
    "auxiliary_surface",
    "proof_scope",
    "expected_pass_semantics",
    "expected_failure_semantics",
    "expected_artifact_path",
    "retained_artifact_kind",
    "allowed_statuses",
    "operator_metadata_required",
    "residual_risk_required",
    "unsupported_claims",
]
FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE),
    re.compile(
        r"\b(certificate[_-]?pem|password[_-]?value|token[_-]?value|certificate[_-]?bytes|private[_-]?key|signing[_-]?key[_-]?value|raw[_-]?crash[_-]?dump|firmware[_-]?payload)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bConnect token\b", re.IGNORECASE),
    re.compile(r"\bWi-Fi credential\b", re.IGNORECASE),
    re.compile(r"\bcredential value\b", re.IGNORECASE),
)
OVERCLAIM_STRINGS = {
    "hardware verified locally",
    "local hardware proof",
    "simulator passed locally",
    "live service passed locally",
    "release-candidate passed locally",
    "signing verified locally",
    "retained-code accepted by maintainer",
    "reference demotion approved",
    "reference removal complete",
    "cutover complete",
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
        if phrase.lower() in lowered:
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


def value_covers(required_value: str, actual_value: str, field: str) -> bool:
    if actual_value == required_value or actual_value == "all-supported":
        return True
    if field == "board" and actual_value == "all-master-boards":
        return required_value in {"BUDDY", "XBUDDY", "XLBUDDY", "XL_DEV_KIT_XLB"}
    return False


def covered_values(scenarios: list[dict[str, Any]], field: str, required_values: set[str]) -> set[str]:
    covered: set[str] = set()
    for scenario in scenarios:
        actual_value = scenario.get(field)
        if not isinstance(actual_value, str):
            continue
        for required_value in required_values:
            if value_covers(required_value, actual_value, field):
                covered.add(required_value)
    return covered


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
        errors.append("operator_input_schema required_fields must match required operator metadata fields")
    if set(allowed_results) != {"passed", "failed", "blocked-hardware-unavailable"}:
        errors.append("operator_input_schema allowed_results must be passed, failed, blocked-hardware-unavailable")
    if artifact_ref_root != DEFAULT_OUTPUT_DIR.as_posix():
        errors.append(f"operator_input_schema artifact_ref_root must be {DEFAULT_OUTPUT_DIR.as_posix()}")


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase15_hardware_evidence_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase15-hardware-evidence",
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
        errors.append("status_vocabulary does not match the Phase 15 vocabulary")
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
            require_string(scenario, "printer_family", row_name)
            require_string(scenario, "board", row_name)
            require_string(scenario, "media_surface", row_name)
            require_string(scenario, "auxiliary_surface", row_name)
            proof_scope = require_string(scenario, "proof_scope", row_name)
            require_string(scenario, "expected_pass_semantics", row_name)
            require_string(scenario, "expected_failure_semantics", row_name)
            artifact_path = require_string(scenario, "expected_artifact_path", row_name)
            retained_artifact_kind = require_string(scenario, "retained_artifact_kind", row_name)
            allowed_statuses = set(require_list_of_strings(scenario, "allowed_statuses", row_name))
            operator_metadata = require_list_of_strings(scenario, "operator_metadata_required", row_name)
            unsupported_claims = require_list_of_strings(scenario, "unsupported_claims", row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue

        if scenario_id != row_name:
            errors.append(f"{row_name} id mismatch")
        unknown_requirements = sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)
        if unknown_requirements:
            errors.append(f"{row_name} uses unknown requirement IDs: {', '.join(unknown_requirements)}")
        covered_requirements.update(requirement_ids)
        for source_ref in source_refs:
            try:
                resolve_source_ref(root, source_ref, row_name)
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
        if proof_scope == "hardware-observation":
            missing_statuses = sorted(HARDWARE_ALLOWED_STATUSES - allowed_statuses)
            if missing_statuses:
                errors.append(f"{row_name} hardware allowed_statuses missing: {', '.join(missing_statuses)}")
            default_status = scenario.get("default_status")
            if default_status == "passed":
                errors.append(f"{row_name} default_status cannot be passed without operator evidence")
        elif proof_scope == "source-contract":
            missing_statuses = sorted(SOURCE_CONTRACT_ALLOWED_STATUSES - allowed_statuses)
            if missing_statuses:
                errors.append(f"{row_name} source-contract allowed_statuses missing: {', '.join(missing_statuses)}")
        else:
            errors.append(f"{row_name} proof_scope must be hardware-observation or source-contract")
        if operator_metadata != REQUIRED_OPERATOR_FIELDS:
            errors.append(f"{row_name} operator metadata must include: {', '.join(REQUIRED_OPERATOR_FIELDS)}")
        if scenario.get("residual_risk_required") is not True:
            errors.append(f"{row_name} residual risk must be required")
        if not unsupported_claims:
            errors.append(f"{row_name} unsupported_claims must not be empty")

    missing_requirements = sorted(REQUIRED_REQUIREMENT_IDS - covered_requirements)
    if missing_requirements:
        errors.append("missing HARD requirement coverage: " + ", ".join(missing_requirements))
    coverage_checks = [
        ("printer_family", REQUIRED_SUPPORTED_PRINTER_FAMILIES),
        ("board", REQUIRED_SUPPORTED_BOARDS),
        ("media_surface", REQUIRED_STORAGE_MEDIA_SURFACES),
    ]
    for field, required_values in coverage_checks:
        missing_values = sorted(required_values - covered_values(scenarios, field, required_values))
        if missing_values:
            errors.append(f"missing required {field} coverage: {', '.join(missing_values)}")
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def iter_security_files(root: Path, output_dir: Path) -> list[Path]:
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
    phase15_manifest_srcs = [
        Path(path).relative_to("tools/bazel").as_posix()
        for path in SOURCE_REF_MANIFESTS
    ]
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase15_source_ref_manifests"',
                'name = "phase15_verify"',
                'name = "phase15_verify_tests"',
                "phase15_hardware_evidence.py",
                "phase15_hardware_evidence_test.py",
                "phase15_hardware_evidence_contract.json",
                ":phase15_source_ref_manifests",
                "//:phase15_hardware_evidence_docs",
                *phase15_manifest_srcs,
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase15_hardware_evidence_docs"',
                'name = "phase15_verify"',
                'name = "phase15_verify_tests"',
                ".planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md",
                ".planning/phases/15-hardware-safety-and-media-qualification/15-RESEARCH.md",
                ".planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md",
                ".planning/phases/15-hardware-safety-and-media-qualification/15-01-PLAN.md",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase15_verify)",
                "python3 tools/bazel/phase15_hardware_evidence.py --wiring-only",
                "python3 tools/bazel/phase15_hardware_evidence.py --quick",
                "phase15_verify_tests)",
                "python3 tools/bazel/phase15_hardware_evidence_test.py",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase15-verify:",
                "bazel run //tools/bazel:phase15_verify_tests",
                "bazel run //tools/bazel:phase15_verify",
            ],
        )
    )
    try:
        just_lines = [line.strip() for line in read_text(root, "justfile").splitlines()]
        just_tests_line = "bazel run //tools/bazel:phase15_verify_tests"
        just_verify_line = "bazel run //tools/bazel:phase15_verify"
        if just_tests_line not in just_lines:
            errors.append("justfile missing exact phase15_verify_tests recipe line")
        if just_verify_line not in just_lines:
            errors.append("justfile missing exact phase15_verify recipe line")
        if just_tests_line in just_lines and just_verify_line in just_lines:
            if just_lines.index(just_tests_line) > just_lines.index(just_verify_line):
                errors.append("justfile phase15-verify must run tests before verifier")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def load_operator_evidence_path(root: Path, path: str | None) -> tuple[Path | None, dict[str, Any] | None]:
    if not path:
        return None, None
    evidence_path = Path(path)
    full_path = evidence_path if evidence_path.is_absolute() else root / evidence_path
    if not full_path.exists():
        raise VerificationError(f"operator evidence file does not exist: {path}")
    try:
        data = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VerificationError(f"operator evidence is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError("operator evidence must contain a top-level object")
    return evidence_path, data


def validated_operator_rows(root: Path, contract: dict[str, Any], path: str | None) -> dict[str, dict[str, str]]:
    evidence_path, data = load_operator_evidence_path(root, path)
    if data is None:
        return {}
    scenarios_by_id = {scenario["id"]: scenario for scenario in contract_scenarios(contract)}
    rows = data.get("evidence_rows")
    if not isinstance(rows, list):
        raise VerificationError("operator evidence must contain an evidence_rows list")
    parsed_rows: dict[str, dict[str, str]] = {}
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
            artifact_ref = require_string(row, "artifact_ref", row_name)
            if scenario_id not in scenarios_by_id:
                raise VerificationError(f"{row_name} references unknown scenario: {scenario_id}")
            if result not in {"passed", "failed", "blocked-hardware-unavailable"}:
                raise VerificationError(f"{row_name} uses unsupported result: {result}")
            scenario = scenarios_by_id[scenario_id]
            allowed_statuses = set(require_list_of_strings(scenario, "allowed_statuses", scenario_id))
            if result not in allowed_statuses:
                raise VerificationError(f"{row_name} result {result} is not allowed for {scenario_id}")
            require_repo_relative_under(artifact_ref, DEFAULT_OUTPUT_DIR, row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue
        parsed_rows[str(row["scenario_id"])] = {field: str(row[field]) for field in REQUIRED_OPERATOR_FIELDS}
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
    return "pending-hardware-input"


def scenario_result_row(scenario: dict[str, Any], maybe_operator_row: dict[str, str] | None) -> dict[str, Any]:
    scenario_id = str(scenario["id"])
    status = default_status_for(scenario)
    artifact_ref = str(scenario["expected_artifact_path"])
    residual_risk = "Awaiting physical operator evidence." if status == "pending-hardware-input" else "Source contract boundary only."
    operator = ""
    timestamp = ""
    firmware_build = ""
    device = ""
    if maybe_operator_row is not None:
        status = maybe_operator_row["result"]
        artifact_ref = maybe_operator_row["artifact_ref"]
        residual_risk = maybe_operator_row["residual_risk"]
        operator = maybe_operator_row["operator"]
        timestamp = maybe_operator_row["timestamp"]
        firmware_build = maybe_operator_row["firmware_build"]
        device = maybe_operator_row["device"]
    return {
        "artifact_ref": artifact_ref,
        "auxiliary_surface": scenario["auxiliary_surface"],
        "board": scenario["board"],
        "device": device,
        "firmware_build": firmware_build,
        "id": scenario_id,
        "media_surface": scenario["media_surface"],
        "operator": operator,
        "printer_family": scenario["printer_family"],
        "proof_scope": scenario["proof_scope"],
        "requirement_ids": scenario["requirement_ids"],
        "residual_risk": residual_risk,
        "status": status,
        "timestamp": timestamp,
        "title": scenario["title"],
        "v1_requirement_ids": scenario["v1_requirement_ids"],
    }


def write_log(root: Path, output_dir: Path, result_row: dict[str, Any]) -> None:
    log_path = output_dir / "logs" / f"{result_row['id']}.log"
    lines = [
        f"scenario_id={result_row['id']}",
        f"status={result_row['status']}",
        f"proof_scope={result_row['proof_scope']}",
        f"printer_family={result_row['printer_family']}",
        f"board={result_row['board']}",
        f"artifact_ref={result_row['artifact_ref']}",
        f"residual_risk={result_row['residual_risk']}",
    ]
    full_path = root / log_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quick_artifacts(
    root: Path,
    contract: dict[str, Any],
    output_dir: Path,
    operator_rows: dict[str, dict[str, str]],
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
    run_manifest = {
        "artifact_name": contract["artifact_name"],
        "generated_at": generated_at,
        "output_root": output_dir.as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "scenarios": [
            {
                "artifact_ref": row["artifact_ref"],
                "id": row["id"],
                "proof_scope": row["proof_scope"],
                "status": row["status"],
            }
            for row in result_rows
        ],
        "status_counts": status_counts,
    }
    normalized_results = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "scenarios": result_rows,
    }
    redacted_summary = {
        "generated_at": generated_at,
        "operator_evidence_count": len(operator_rows),
        "pending_hardware_input": [
            row["id"] for row in result_rows if row["status"] == "pending-hardware-input"
        ],
        "redaction_boundary": "Phase 15 retains only sanitized references and operator metadata required by the contract.",
        "source_contract_rows": [
            row["id"] for row in result_rows if row["proof_scope"] == "source-contract"
        ],
        "status_counts": status_counts,
    }
    write_json(root, output_dir / "run-manifest.json", run_manifest)
    write_json(root, output_dir / "normalized-scenario-results.json", normalized_results)
    write_json(root, output_dir / "redacted-hardware-summary.json", redacted_summary)
    write_json(
        root,
        output_dir / "operator-evidence-input.json",
        {"evidence_rows": list(operator_rows.values())},
    )
    shutil.copy2(
        root / CONTRACT_MANIFEST,
        root / output_dir / "source-contract-snapshots" / CONTRACT_MANIFEST.name,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 15 hardware evidence contract")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 15 evidence contract")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 15 contract and generated artifacts")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel and just workflow wiring")
    parser.add_argument("--quick", action="store_true", help="write deterministic Phase 15 evidence artifacts")
    parser.add_argument("--operator-evidence", help="optional operator evidence JSON input")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 15 evidence output directory")
    args = parser.parse_args()
    selected_modes = [args.contract_only, args.security_only, args.wiring_only, args.quick]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    output_dir = Path(args.output_dir)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 15 hardware evidence contract passed")
        elif args.security_only:
            check_security(ROOT, output_dir)
            print("Phase 15 hardware evidence security scan passed")
        elif args.quick:
            contract = check_contract(ROOT)
            operator_rows = validated_operator_rows(ROOT, contract, args.operator_evidence)
            write_quick_artifacts(ROOT, contract, output_dir, operator_rows)
            check_security(ROOT, output_dir)
            print(f"Phase 15 hardware evidence written to {output_dir.as_posix()}")
        else:
            check_wiring(ROOT)
            print("Phase 15 hardware evidence wiring passed")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
