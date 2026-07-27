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
PHASE = "23-simulator-evidence-execution"
PHASE_LIFECYCLE_ID = "23-2026-06-23T18-45-38"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json")
PHASE14_CONTRACT = Path(
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json")
PHASE19_CONTRACT = Path(
    "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json")
PHASE18_CONTRACT = Path(
    "tools/bazel/manifests/phase18_cutover_review_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase23")
REQUIRED_REQUIREMENT_IDS = {"EVID-01"}
V1_2_STATUSES = {"passed", "failed", "blocked", "exception-requested"}
PENDING_SOURCE_STATUSES = {
    "pending-simulator-input", "pending-simulator-dependency"
}
EXCEPTION_FIELDS = ["owner", "rationale", "evidence_ref", "revisit_condition"]
FORBIDDEN_FIELD_NAMES = {
    "certificate_bytes",
    "certificate_pem",
    "credential",
    "credential_value",
    "firmware_payload",
    "firmware_payload_bytes",
    "password",
    "password_value",
    "private_key",
    "raw_crash_dump",
    "signing_key_value",
    "token",
    "token_value",
}
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
    "cutover complete",
    "hardware verified locally",
    "live service passed locally",
    "local hardware proof",
    "reference demotion approved",
    "reference removal complete",
    "release-candidate passed locally",
    "retained-code accepted by maintainer",
    "signing verified locally",
}


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
        if field in row and row[field] in ("", None, {})
    ]
    if missing or empty:
        parts: list[str] = []
        if missing:
            parts.append("missing required fields: " + ", ".join(missing))
        if empty:
            parts.append("empty required fields: " + ", ".join(empty))
        raise VerificationError(f"{row_name} " + "; ".join(parts))


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


def normalized_field_name(field_name: str) -> str:
    return field_name.replace("-", "_").casefold()


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(
            key for key in value
            if normalized_field_name(key) in FORBIDDEN_FIELD_NAMES)
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
    if ref.startswith("external://phase23/"):
        if ".." in ref or ref.endswith("/"):
            raise VerificationError(
                f"{row_name} artifact ref is unsafe: {ref}")
        return ref
    return require_repo_relative_under(ref, DEFAULT_OUTPUT_DIR,
                                       row_name).as_posix()


def validate_artifact_refs(row: dict[str, Any], row_name: str) -> list[str]:
    refs = require_non_empty_list_of_strings(row, "artifact_refs", row_name)
    return [validate_artifact_ref(ref, row_name) for ref in refs]


def phase14_scenarios(contract: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = contract.get("scenarios")
    if not isinstance(scenarios, list):
        raise VerificationError(
            f"{PHASE14_CONTRACT.as_posix()} must contain a scenarios list")
    parsed: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise VerificationError(
                f"{PHASE14_CONTRACT.as_posix()} scenarios[{index}] must be an object"
            )
        parsed.append(scenario)
    return parsed


def check_contract(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    phase14 = load_json(root, PHASE14_CONTRACT)
    load_json(root, PHASE19_CONTRACT)
    load_json(root, PHASE18_CONTRACT)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase23_simulator_evidence_execution_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase23-simulator-evidence-execution",
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    try:
        status_vocabulary = set(
            require_list_of_strings(contract, "status_vocabulary", "contract"))
        required_scenario_ids = require_list_of_strings(
            contract, "required_phase14_scenario_ids", "contract")
        required_artifact_kinds = set(
            require_list_of_strings(contract, "required_artifact_kinds",
                                    "contract"))
        source_contracts = set(
            require_list_of_strings(contract, "source_contracts", "contract"))
        upstream = require_dict(contract, "upstream_result_row", "contract")
        requirement_ids = set(
            require_list_of_strings(upstream, "requirement_ids",
                                    "upstream_result_row"))
        scenarios = phase14_scenarios(phase14)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if status_vocabulary != V1_2_STATUSES:
        errors.append("status_vocabulary must match v1.2 simulator statuses")
    if requirement_ids != REQUIRED_REQUIREMENT_IDS:
        errors.append("upstream_result_row requirement_ids must be EVID-01")
    expected_source_contracts = {
        PHASE14_CONTRACT.as_posix(),
        PHASE19_CONTRACT.as_posix(),
        PHASE18_CONTRACT.as_posix()
    }
    if source_contracts != expected_source_contracts:
        errors.append(
            "source_contracts must name Phase 14, Phase 19, and Phase 18 contracts"
        )
    missing_artifacts = sorted({
        "machine-readable-run-manifest",
        "normalized-scenario-summary",
        "redacted-evidence-summary",
        "upstream-result-row",
        "contract-snapshot",
        "simulator-log-reference",
    } - required_artifact_kinds)
    if missing_artifacts:
        errors.append("missing required artifact kinds: " +
                      ", ".join(missing_artifacts))
    scenario_ids = [
        require_string(scenario, "id", "scenario") for scenario in scenarios
    ]
    if sorted(required_scenario_ids) != sorted(scenario_ids):
        errors.append(
            "required_phase14_scenario_ids must exactly match Phase 14 scenarios"
        )
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("Phase 14 scenario IDs must be unique")
    phase14_statuses = set(
        require_list_of_strings(phase14, "status_vocabulary",
                                "phase14 contract"))
    for scenario in scenarios:
        row_name = f"scenario {scenario.get('id', '<missing>')}"
        try:
            require_fields(
                scenario,
                [
                    "id",
                    "title",
                    "requirement_ids",
                    "v1_requirement_ids",
                    "phase11_source_refs",
                    "expected_artifact_path",
                    "pytest_node_ids",
                    "residual_non_simulator_gates",
                    "unsupported_claims",
                ],
                row_name,
            )
            allowed_statuses = set(
                require_list_of_strings(scenario, "allowed_statuses",
                                        row_name))
            if not allowed_statuses <= phase14_statuses:
                errors.append(
                    f"{row_name} contains unknown Phase 14 allowed statuses")
            for source_ref in require_list_of_strings(scenario,
                                                      "phase11_source_refs",
                                                      row_name):
                resolve_source_ref(root, source_ref, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract, phase14
