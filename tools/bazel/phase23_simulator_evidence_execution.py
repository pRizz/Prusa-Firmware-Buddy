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
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json")
PHASE14_CONTRACT = Path("tools/bazel/manifests/phase14_simulator_evidence_contract.json")
PHASE19_CONTRACT = Path("tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json")
PHASE18_CONTRACT = Path("tools/bazel/manifests/phase18_cutover_review_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase23")
REQUIRED_REQUIREMENT_IDS = {"EVID-01"}
V1_2_STATUSES = {"passed", "failed", "blocked", "exception-requested"}
PENDING_SOURCE_STATUSES = {"pending-simulator-input", "pending-simulator-dependency"}
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


def require_dict(row: dict[str, Any], field: str, row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_non_empty_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = require_list_of_strings(row, field, row_name)
    if not value:
        raise VerificationError(f"{row_name} {field} must contain at least one item")
    return value


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and row[field] in ("", None, {})]
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


def sanitized_for_artifact(path: Path, text: str) -> tuple[str, list[str]]:
    errors: list[str] = []
    sanitized = text
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(sanitized):
            errors.append(f"{path.as_posix()} contained forbidden evidence content")
            sanitized = pattern.sub("[REDACTED-FORBIDDEN-EVIDENCE]", sanitized)
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase.lower() in sanitized.lower():
            errors.append(f"{path.as_posix()} contained non-local evidence overclaim wording")
            sanitized = re.sub(re.escape(phrase), "[REDACTED-NON-LOCAL-OVERCLAIM]", sanitized, flags=re.IGNORECASE)
    return sanitized, errors


def require_repo_relative_under(path_value: str | Path, output_root: Path, row_name: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} path must be repo-relative and cannot traverse: {path_value}")
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
            raise VerificationError(f"{row_name} artifact ref is unsafe: {ref}")
        return ref
    return require_repo_relative_under(ref, DEFAULT_OUTPUT_DIR, row_name).as_posix()


def validate_artifact_refs(row: dict[str, Any], row_name: str) -> list[str]:
    refs = require_non_empty_list_of_strings(row, "artifact_refs", row_name)
    return [validate_artifact_ref(ref, row_name) for ref in refs]


def phase14_scenarios(contract: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = contract.get("scenarios")
    if not isinstance(scenarios, list):
        raise VerificationError(f"{PHASE14_CONTRACT.as_posix()} must contain a scenarios list")
    parsed: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise VerificationError(f"{PHASE14_CONTRACT.as_posix()} scenarios[{index}] must be an object")
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
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    try:
        status_vocabulary = set(require_list_of_strings(contract, "status_vocabulary", "contract"))
        required_scenario_ids = require_list_of_strings(contract, "required_phase14_scenario_ids", "contract")
        required_artifact_kinds = set(require_list_of_strings(contract, "required_artifact_kinds", "contract"))
        source_contracts = set(require_list_of_strings(contract, "source_contracts", "contract"))
        upstream = require_dict(contract, "upstream_result_row", "contract")
        requirement_ids = set(require_list_of_strings(upstream, "requirement_ids", "upstream_result_row"))
        scenarios = phase14_scenarios(phase14)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if status_vocabulary != V1_2_STATUSES:
        errors.append("status_vocabulary must match v1.2 simulator statuses")
    if requirement_ids != REQUIRED_REQUIREMENT_IDS:
        errors.append("upstream_result_row requirement_ids must be EVID-01")
    expected_source_contracts = {PHASE14_CONTRACT.as_posix(), PHASE19_CONTRACT.as_posix(), PHASE18_CONTRACT.as_posix()}
    if source_contracts != expected_source_contracts:
        errors.append("source_contracts must name Phase 14, Phase 19, and Phase 18 contracts")
    missing_artifacts = sorted(
        {
            "machine-readable-run-manifest",
            "normalized-scenario-summary",
            "redacted-evidence-summary",
            "upstream-result-row",
            "contract-snapshot",
            "simulator-log-reference",
        }
        - required_artifact_kinds
    )
    if missing_artifacts:
        errors.append("missing required artifact kinds: " + ", ".join(missing_artifacts))
    scenario_ids = [require_string(scenario, "id", "scenario") for scenario in scenarios]
    if sorted(required_scenario_ids) != sorted(scenario_ids):
        errors.append("required_phase14_scenario_ids must exactly match Phase 14 scenarios")
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("Phase 14 scenario IDs must be unique")
    phase14_statuses = set(require_list_of_strings(phase14, "status_vocabulary", "phase14 contract"))
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
            allowed_statuses = set(require_list_of_strings(scenario, "allowed_statuses", row_name))
            if not allowed_statuses <= phase14_statuses:
                errors.append(f"{row_name} contains unknown Phase 14 allowed statuses")
            for source_ref in require_list_of_strings(scenario, "phase11_source_refs", row_name):
                resolve_source_ref(root, source_ref, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract, phase14


def source_status_vocabulary(phase14: dict[str, Any]) -> set[str]:
    return set(require_list_of_strings(phase14, "status_vocabulary", "phase14 contract"))


def scenario_map(phase14: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {require_string(scenario, "id", "scenario"): scenario for scenario in phase14_scenarios(phase14)}


def validate_exception_request(row: dict[str, Any], row_name: str) -> dict[str, Any]:
    exception = require_dict(row, "exception_request", row_name)
    require_fields(exception, EXCEPTION_FIELDS, f"{row_name} exception_request")
    validate_artifact_ref(require_string(exception, "evidence_ref", f"{row_name} exception_request"), row_name)
    return exception


def validate_scenario_result(
    row: dict[str, Any],
    row_name: str,
    source_statuses: set[str],
    source_scenario: dict[str, Any],
) -> dict[str, Any]:
    require_fields(
        row,
        [
            "scenario_id",
            "status",
            "source_status",
            "status_reason",
            "artifact_refs",
            "redaction_status",
            "source_ref_status",
        ],
        row_name,
    )
    scenario_id = require_string(row, "scenario_id", row_name)
    status = require_string(row, "status", row_name)
    source_status = require_string(row, "source_status", row_name)
    if status not in V1_2_STATUSES:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    if source_status not in source_statuses:
        raise VerificationError(f"{row_name} source_status is not a Phase 14 status: {source_status}")
    if status == "passed" and source_status in PENDING_SOURCE_STATUSES:
        raise VerificationError(f"{row_name} cannot pass with source_status={source_status}")
    redaction_status = require_string(row, "redaction_status", row_name)
    source_ref_status = require_string(row, "source_ref_status", row_name)
    if status == "passed" and redaction_status != "passed":
        raise VerificationError(f"{row_name} passed status requires redaction_status=passed")
    if status == "passed" and source_ref_status != "passed":
        raise VerificationError(f"{row_name} passed status requires source_ref_status=passed")
    exception_request = None
    if status == "exception-requested":
        exception_request = validate_exception_request(row, row_name)
    artifact_refs = validate_artifact_refs(row, row_name)
    runtime_metadata = row.get("runtime_metadata", {})
    if not isinstance(runtime_metadata, dict):
        raise VerificationError(f"{row_name} runtime_metadata must be an object when present")
    return {
        "artifact_refs": artifact_refs,
        "exception_request": exception_request,
        "phase11_source_refs": require_list_of_strings(source_scenario, "phase11_source_refs", row_name),
        "proof_scope": require_string(source_scenario, "proof_scope", row_name),
        "pytest_node_ids": require_list_of_strings(source_scenario, "pytest_node_ids", row_name),
        "requirement_ids": ["EVID-01"],
        "runtime_metadata": runtime_metadata,
        "scenario_id": scenario_id,
        "simulator_requirement_ids": require_list_of_strings(source_scenario, "requirement_ids", row_name),
        "source_ref_status": source_ref_status,
        "source_status": source_status,
        "status": status,
        "status_reason": require_string(row, "status_reason", row_name),
        "title": require_string(source_scenario, "title", row_name),
        "redaction_status": redaction_status,
        "residual_non_simulator_gates": require_list_of_strings(
            source_scenario, "residual_non_simulator_gates", row_name
        ),
        "unsupported_claims": require_list_of_strings(source_scenario, "unsupported_claims", row_name),
        "v1_requirement_ids": require_list_of_strings(source_scenario, "v1_requirement_ids", row_name),
    }


def load_evidence_rows(root: Path, input_path: Path, phase14: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if input_path.is_absolute() or ".." in input_path.parts:
        raise VerificationError("--evidence-input must be repo-relative and cannot traverse")
    input_text = read_text(root, input_path)
    reject_forbidden_text(input_path, input_text)
    try:
        data = json.loads(input_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"{input_path.as_posix()} is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    if not isinstance(data, dict):
        raise VerificationError("--evidence-input must contain a top-level object")
    packet = require_dict(data, "simulator_evidence_packet", "--evidence-input")
    require_fields(
        packet,
        [
            "evidence_run_id",
            "firmware_identity",
            "simulator_identity",
            "operator",
            "started_at",
            "completed_at",
            "scenario_results",
        ],
        "simulator_evidence_packet",
    )
    require_dict(packet, "firmware_identity", "simulator_evidence_packet")
    require_dict(packet, "simulator_identity", "simulator_evidence_packet")
    if packet.get("phase") not in (None, PHASE):
        raise VerificationError(f"simulator_evidence_packet phase must be {PHASE}")
    raw_rows = packet.get("scenario_results")
    if not isinstance(raw_rows, list):
        raise VerificationError("simulator_evidence_packet scenario_results must be a list")
    sources = scenario_map(phase14)
    expected_ids = set(sources)
    seen_ids: set[str] = set()
    rows: list[dict[str, Any]] = []
    for index, raw_row in enumerate(raw_rows):
        if not isinstance(raw_row, dict):
            raise VerificationError(f"scenario_results[{index}] must be an object")
        scenario_id = str(raw_row.get("scenario_id", ""))
        row_name = f"scenario_results[{index}] {scenario_id or '<missing>'}"
        if scenario_id not in sources:
            raise VerificationError(f"{row_name} does not resolve to a Phase 14 scenario")
        if scenario_id in seen_ids:
            raise VerificationError(f"duplicate scenario result: {scenario_id}")
        seen_ids.add(scenario_id)
        rows.append(validate_scenario_result(raw_row, row_name, source_status_vocabulary(phase14), sources[scenario_id]))
    missing = sorted(expected_ids - seen_ids)
    extra = sorted(seen_ids - expected_ids)
    if missing or extra:
        parts: list[str] = []
        if missing:
            parts.append("missing scenario results: " + ", ".join(missing))
        if extra:
            parts.append("unexpected scenario results: " + ", ".join(extra))
        raise VerificationError("; ".join(parts))
    return packet, rows


def quick_rows(root: Path, output_dir: Path, phase14: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    logs_dir = root / output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    for scenario in phase14_scenarios(phase14):
        scenario_id = require_string(scenario, "id", "scenario")
        log_ref = output_dir / "logs" / f"{scenario_id}.log"
        source_status = "passed" if scenario_id == "sim-traceability-non-simulator-boundaries" else "pending-simulator-input"
        log_text = (
            f"phase: {PHASE}\n"
            f"scenario: {scenario_id}\n"
            "mode: quick-placeholder\n"
            "status: blocked\n"
            "reason: real simulator evidence input was not supplied.\n"
        )
        sanitized_log, redaction_errors = sanitized_for_artifact(log_ref, log_text)
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        (root / log_ref).write_text(sanitized_log, encoding="utf-8")
        rows.append(
            {
                "artifact_refs": [log_ref.as_posix()],
                "exception_request": None,
                "phase11_source_refs": require_list_of_strings(scenario, "phase11_source_refs", "scenario"),
                "proof_scope": require_string(scenario, "proof_scope", "scenario"),
                "pytest_node_ids": require_list_of_strings(scenario, "pytest_node_ids", "scenario"),
                "requirement_ids": ["EVID-01"],
                "runtime_metadata": {},
                "scenario_id": scenario_id,
                "simulator_requirement_ids": require_list_of_strings(scenario, "requirement_ids", "scenario"),
                "source_ref_status": "passed",
                "source_status": source_status,
                "status": "blocked",
                "status_reason": "real simulator evidence input was not supplied",
                "title": require_string(scenario, "title", "scenario"),
                "redaction_status": "passed",
                "residual_non_simulator_gates": require_list_of_strings(
                    scenario, "residual_non_simulator_gates", "scenario"
                ),
                "unsupported_claims": require_list_of_strings(scenario, "unsupported_claims", "scenario"),
                "v1_requirement_ids": require_list_of_strings(scenario, "v1_requirement_ids", "scenario"),
            }
        )
    return rows


def aggregate_status(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row["status"]) for row in rows}
    if "failed" in statuses:
        return "failed"
    if "blocked" in statuses:
        return "blocked"
    if "exception-requested" in statuses:
        return "exception-requested"
    return "passed"


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return counts


def write_retained_outputs(
    root: Path,
    output_dir: Path,
    rows: list[dict[str, Any]],
    command_mode: str,
    real_input_supplied: bool,
    maybe_packet: dict[str, Any] | None = None,
) -> None:
    output_root = root / output_dir
    snapshots_dir = output_root / "contract-snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    if not (output_root / "logs").exists():
        (output_root / "logs").mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    status_summary = status_counts(rows)
    run_status = aggregate_status(rows)
    requirement_coverage = {
        "EVID-01": sorted(str(row["scenario_id"]) for row in rows),
        "SIM-01": sorted(
            str(row["scenario_id"]) for row in rows if "SIM-01" in row["simulator_requirement_ids"]
        ),
        "SIM-02": sorted(
            str(row["scenario_id"]) for row in rows if "SIM-02" in row["simulator_requirement_ids"]
        ),
        "SIM-03": sorted(
            str(row["scenario_id"]) for row in rows if "SIM-03" in row["simulator_requirement_ids"]
        ),
    }
    manifest = {
        "artifact_name": "phase23-simulator-evidence-execution",
        "command_mode": command_mode,
        "evidence_run_id": maybe_packet.get("evidence_run_id", "") if maybe_packet else "",
        "firmware_identity": maybe_packet.get("firmware_identity", {}) if maybe_packet else {},
        "generated_at": generated_at,
        "operator": maybe_packet.get("operator", "") if maybe_packet else "",
        "output_root": output_dir.as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "real_simulator_evidence_supplied": real_input_supplied,
        "requirement_coverage": requirement_coverage,
        "scenario_count": len(rows),
        "scenarios": rows,
        "simulator_identity": maybe_packet.get("simulator_identity", {}) if maybe_packet else {},
        "status": run_status,
        "status_counts": status_summary,
    }
    normalized = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "real_simulator_evidence_supplied": real_input_supplied,
        "scenarios": [
            {
                "artifact_refs": row["artifact_refs"],
                "requirement_ids": row["requirement_ids"],
                "residual_non_simulator_gates": row["residual_non_simulator_gates"],
                "scenario_id": row["scenario_id"],
                "simulator_requirement_ids": row["simulator_requirement_ids"],
                "source_status": row["source_status"],
                "status": row["status"],
                "status_reason": row["status_reason"],
                "v1_requirement_ids": row["v1_requirement_ids"],
            }
            for row in rows
        ],
    }
    redacted_summary = {
        "generated_at": generated_at,
        "phase": PHASE,
        "real_simulator_evidence_supplied": real_input_supplied,
        "scenario_status": [
            {
                "scenario_id": row["scenario_id"],
                "source_status": row["source_status"],
                "status": row["status"],
                "status_reason": row["status_reason"],
            }
            for row in rows
        ],
        "status": run_status,
        "status_counts": status_summary,
        "unsupported_boundaries": sorted({claim for row in rows for claim in row["unsupported_claims"]}),
    }
    upstream_row = {
        "artifact_refs": [
            (output_dir / "normalized-simulator-results.json").as_posix(),
            (output_dir / "redacted-evidence-summary.json").as_posix(),
        ],
        "criterion_id": "final-simulator-evidence",
        "evidence_family": "simulator",
        "manifest_ref": (output_dir / "simulator-result-manifest.json").as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "real_simulator_evidence_supplied": real_input_supplied,
        "redaction_status": "passed",
        "requirement_ids": ["EVID-01"],
        "scenario_status_counts": status_summary,
        "source_ref_status": "passed",
        "status": run_status,
    }
    write_json(root, output_dir / "simulator-result-manifest.json", manifest)
    write_json(root, output_dir / "normalized-simulator-results.json", normalized)
    write_json(root, output_dir / "redacted-evidence-summary.json", redacted_summary)
    write_json(root, output_dir / "upstream-simulator-result-row.json", upstream_row)
    for snapshot in [CONTRACT_MANIFEST, PHASE14_CONTRACT]:
        snapshot_text = read_text(root, snapshot)
        sanitized_snapshot, redaction_errors = sanitized_for_artifact(snapshot, snapshot_text)
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        (root / snapshots_dir / snapshot.name).write_text(sanitized_snapshot, encoding="utf-8")
    check_security(root)


def security_paths(root: Path) -> list[Path]:
    paths = [CONTRACT_MANIFEST]
    output_root = root / DEFAULT_OUTPUT_DIR
    if output_root.exists():
        paths.extend(path.relative_to(root) for path in sorted(output_root.rglob("*")) if path.is_file())
    return [path for path in paths if (root / path).exists()]


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in security_paths(root):
        try:
            reject_forbidden_text(path, read_text(root, path))
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
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase23_source_ref_manifests"',
                'name = "phase23_verify"',
                'name = "phase23_verify_tests"',
                "phase23_simulator_evidence_execution.py",
                "phase23_simulator_evidence_execution_test.py",
                "phase23_simulator_evidence_execution_contract.json",
                "//:phase23_simulator_evidence_execution_docs",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase23_simulator_evidence_execution_docs"',
                'name = "phase23_verify"',
                'name = "phase23_verify_tests"',
                ".planning/phases/23-simulator-evidence-execution/23-01-PLAN.md",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase23_verify)",
                "python3 tools/bazel/phase23_simulator_evidence_execution.py --wiring-only",
                "python3 tools/bazel/phase23_simulator_evidence_execution.py --quick --output-dir build/ci-evidence/phase23",
                "phase23_verify_tests)",
                "python3 tools/bazel/phase23_simulator_evidence_execution_test.py",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase23-verify:",
                "bazel run //tools/bazel:phase23_verify_tests",
                "bazel run //tools/bazel:phase23_verify",
            ],
        )
    )
    if errors:
        raise VerificationError("\n".join(errors))


def reset_output_root(root: Path, output_dir: Path) -> Path:
    output_relative = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    output_root = root / output_relative
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    return output_relative


def run_or_raise(args: argparse.Namespace) -> None:
    root = ROOT
    contract, phase14 = check_contract(root)
    output_dir = Path(args.output_dir)
    if args.contract_only:
        return
    if args.security_only:
        check_security(root)
        return
    if args.wiring_only:
        check_wiring(root)
        return
    if args.quick:
        output_relative = reset_output_root(root, output_dir)
        rows = quick_rows(root, output_relative, phase14)
        write_retained_outputs(root, output_relative, rows, "quick-placeholder", False)
        return
    if args.evidence_input:
        output_relative = reset_output_root(root, output_dir)
        packet, rows = load_evidence_rows(root, Path(args.evidence_input), phase14)
        write_retained_outputs(root, output_relative, rows, "evidence-input", True, packet)
        return
    check_security(root)
    check_wiring(root)
    _ = contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and retain Phase 23 simulator evidence execution results.")
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--evidence-input")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args()


def main() -> int:
    try:
        run_or_raise(parse_args())
    except VerificationError as error:
        print(f"Phase 23 simulator evidence execution verification failed:\n{error}", file=sys.stderr)
        return 1
    print("Phase 23 simulator evidence execution verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
