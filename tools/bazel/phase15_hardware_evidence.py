#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 15 hardware evidence contract")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 15 evidence contract")
    args = parser.parse_args()
    if not args.contract_only:
        parser.error("currently only --contract-only is implemented")
    try:
        check_contract(ROOT)
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    print("Phase 15 hardware evidence contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
