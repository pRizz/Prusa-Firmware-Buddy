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
PHASE = "33-maintainer-decision-inputs"
PHASE_LIFECYCLE_ID = "33-2026-07-04T01-36-41"
PHASE32_LIFECYCLE_ID = "32-2026-07-03T14-13-51"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json")
DEFAULT_PHASE32_HANDOFF = Path("build/ci-evidence/phase32/downstream-handoff-manifest.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase33")
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
PHASE32_OUTPUT_ROOT = Path("build/ci-evidence/phase32")
SOURCE_CONTRACT_SNAPSHOTS = {
    "phase33_maintainer_decision_inputs_contract.json": CONTRACT_MANIFEST,
    "phase32_blocker_register_triage_contract.json": Path("tools/bazel/manifests/phase32_blocker_register_triage_contract.json"),
    "phase27_retained_code_acceptance_decisions_contract.json": Path(
        "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
    ),
    "phase28_final_readiness_packet_contract.json": Path("tools/bazel/manifests/phase28_final_readiness_packet_contract.json"),
}
REQUIRED_REQUIREMENT_IDS = ["DECIDE-01", "DECIDE-02", "DECIDE-03"]
REQUIRED_SOURCE_CONTRACT_IDS = [
    "phase32_blocker_register_triage_contract",
    "phase27_retained_code_acceptance_decisions_contract",
    "phase28_final_readiness_packet_contract",
]
REQUIRED_DECISION_FIELDS = [
    "decision_id",
    "decision_type",
    "decision_value",
    "source_row_refs",
    "maintainer_identity_ref",
    "maintainer_role",
    "owner_signoff_ref",
    "decision_timestamp",
    "rationale",
    "evidence_refs",
    "artifact_refs",
]
DECISION_VALUE_ENUMS = {
    "retained_code": ["accept", "reject", "exception_approve"],
    "residual_risk": ["accept", "reject"],
    "exception": ["approve", "reject"],
    "readiness": ["approve", "block"],
    "reference_demotion": ["approve", "reject"],
}
DECISION_TYPES = list(DECISION_VALUE_ENUMS)
DECISION_TYPE_IMPACTS = {
    "retained_code": {"retained_code_decision_required"},
    "residual_risk": {"residual_risk_decision_required"},
    "exception": {"exception_decision_required"},
    "readiness": {"final_readiness_blocked"},
    "reference_demotion": {"demotion_decision_required"},
}
APPROVAL_DECISION_VALUES = {
    "retained_code": {"accept", "exception_approve"},
    "residual_risk": {"accept"},
    "exception": {"approve"},
    "readiness": {"approve"},
    "reference_demotion": {"approve"},
}
HARD_BLOCKER_PROBLEM_KINDS = {
    "redaction_failed",
    "source_ref_failed",
    "secret_tainted",
    "lifecycle_mismatch",
    "unsafe_ref",
}
SECURITY_SCAN_CONTRACT_ALLOWLIST = {
    CONTRACT_MANIFEST.as_posix(),
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase32_blocker_register_triage_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase28_final_readiness_packet_contract.json",
    "contract-snapshots/phase32-downstream-handoff-manifest.json",
    "contract-snapshots/phase32-blocker-register.json",
}
GENERATED_ARTIFACTS = [
    "maintainer-decision-input-template.json",
    "normalized-decision-records.json",
    "retained-code-decision-register.json",
    "residual-risk-decision-register.json",
    "exception-decision-register.json",
    "readiness-decision-handoff.json",
    "demotion-decision-handoff.json",
    "decision-validation-report.json",
    "downstream-handoff-manifest.json",
    "redacted-maintainer-decision-report.md",
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase32_blocker_register_triage_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase28_final_readiness_packet_contract.json",
    "contract-snapshots/phase32-downstream-handoff-manifest.json",
    "contract-snapshots/phase32-blocker-register.json",
]
EMITTED_OUTPUT_SCAN_ARTIFACTS = [
    artifact
    for artifact in GENERATED_ARTIFACTS
    if artifact not in SECURITY_SCAN_CONTRACT_ALLOWLIST
]
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api_key",
    "authorization_header",
    "certificate_private_material",
    "client_secret",
    "connect_token",
    "credential_value",
    "demotion_allowed",
    "password",
    "private_key",
    "raw_crash_dump",
    "raw_release_log",
    "secret",
    "secret_value",
    "service_payload",
    "signing_key_value",
    "signing_payload_bytes",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("bearer-token", re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE)),
    ("certificate-private-material", re.compile(r"\bcertificate[_ -]?private[_ -]?material\b", re.IGNORECASE)),
    ("service-payload", re.compile(r"\bservice[_ -]?payload\b", re.IGNORECASE)),
    ("raw-crash-dump", re.compile(r"\braw[_ -]?crash[_ -]?dump\b", re.IGNORECASE)),
    ("raw-release-log", re.compile(r"\braw[_ -]?release[_ -]?log\b", re.IGNORECASE)),
    ("tls-keylog", re.compile(r"\btls[_ -]?keylog\b", re.IGNORECASE)),
    ("wifi-credential", re.compile(r"\bwi[-_ ]?fi[_ -]?credential\b", re.IGNORECASE)),
    ("demotion-allowed", re.compile(r'"?demotion_allowed"?\s*:\s*(true|false|"[^"]*")', re.IGNORECASE)),
    ("reference-demotion-approved", re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("final-readiness-approved", re.compile(r"\bfinal readiness approved\b", re.IGNORECASE)),
    ("final-readiness-unblocked", re.compile(r'"?final_readiness_status"?\s*:\s*"unblocked"', re.IGNORECASE)),
    ("cutover-verdict-approved", re.compile(r"\bcutover verdict approved\b", re.IGNORECASE)),
    ("accepted-by-evidence-alone", re.compile(r"\baccepted by evidence alone\b", re.IGNORECASE)),
)
PHASE33_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31",
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26",
    (
        "python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick "
        "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
        "--output-dir build/ci-evidence/phase27"
    ),
    (
        "python3 tools/bazel/phase28_final_readiness_packet.py --quick "
        "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
        "--phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json "
        "--output-dir build/ci-evidence/phase28"
    ),
    (
        "python3 tools/bazel/phase32_blocker_register_triage.py --quick "
        "--phase31-output-dir build/ci-evidence/phase31 "
        "--phase27-output-dir build/ci-evidence/phase27 "
        "--phase28-output-dir build/ci-evidence/phase28 "
        "--output-dir build/ci-evidence/phase32"
    ),
    "python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only",
    (
        "python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick "
        "--phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json "
        "--output-dir build/ci-evidence/phase33"
    ),
]


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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{field} must be an object")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError(f"{field} must be a list")
    return value


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{field} must be a non-empty string")
    return value


def require_string_list(value: Any, field: str) -> list[str]:
    values = require_list(value, field)
    if not all(isinstance(item, str) and item for item in values):
        raise VerificationError(f"{field} must contain non-empty strings")
    return values


def require_non_empty_string_list(value: Any, field: str) -> list[str]:
    values = require_string_list(value, field)
    if not values:
        raise VerificationError(f"{field} must contain at least one entry")
    return values


def require_iso_utc(timestamp_text: str, field: str) -> None:
    if not timestamp_text.endswith("Z"):
        raise VerificationError(f"{field} must be ISO UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(f"{field} must be ISO UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise VerificationError(f"{field} must be ISO UTC")


def repo_relative_path(value: str | Path, field: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise VerificationError(f"{field} must be repo-relative without traversal: {path.as_posix()}")
    return path


def path_under(value: str | Path, expected_root: Path, field: str) -> Path:
    path = repo_relative_path(value, field)
    try:
        path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"{field} must be under {expected_root.as_posix()}: {path.as_posix()}") from error
    return path


def path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def output_dir_path(root: Path, output_dir: str | Path) -> tuple[Path, Path]:
    relative_output_dir = path_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    current = root
    for part in relative_output_dir.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(f"--output-dir contains a symlink component: {relative_output_dir.as_posix()}")
    full_output_dir = (root / relative_output_dir).resolve(strict=False)
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_output_dir.as_posix()}") from error
    return relative_output_dir, full_output_dir


def reset_output_root(full_output_dir: Path) -> None:
    if full_output_dir.exists():
        if full_output_dir.is_symlink() or not full_output_dir.is_dir():
            raise VerificationError(f"--output-dir exists and is not a normal directory: {full_output_dir.as_posix()}")
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)


def reject_decisions_inside_output(root: Path, maybe_decisions_path: str | None, full_output_dir: Path) -> None:
    if maybe_decisions_path is None:
        return
    decisions_path = (root / repo_relative_path(maybe_decisions_path, "--maintainer-decisions")).resolve(strict=False)
    if path_is_under(decisions_path, full_output_dir.resolve(strict=False)):
        raise VerificationError("--maintainer-decisions must be outside the generated --output-dir")


def repo_relative_output_dir(output_dir: Path) -> Path:
    if not output_dir.is_absolute():
        return output_dir
    try:
        return output_dir.relative_to(ROOT)
    except ValueError as error:
        raise VerificationError(f"output directory is outside repo: {output_dir.as_posix()}") from error


def normalized_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", field_name.casefold())


FORBIDDEN_NORMALIZED_FIELD_NAMES = {normalized_field_name(field_name) for field_name in FORBIDDEN_FIELD_NAMES}


def reject_forbidden_field_names(value: Any, source_name: str, path: str = "$") -> None:
    errors: list[str] = []

    def walk(candidate: Any, candidate_path: str) -> None:
        if isinstance(candidate, dict):
            for key, nested in candidate.items():
                nested_path = f"{candidate_path}.{key}"
                if normalized_field_name(str(key)) in FORBIDDEN_NORMALIZED_FIELD_NAMES:
                    errors.append(f"{source_name} contains forbidden field {key} at {nested_path}")
                walk(nested, nested_path)
            return
        if isinstance(candidate, list):
            for index, nested in enumerate(candidate):
                walk(nested, f"{candidate_path}[{index}]")

    walk(value, path)
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            errors.append(f"{path.as_posix()} contains forbidden marker {label}")
    if errors:
        raise VerificationError("\n".join(errors))


def validate_reference_text(value: str, field: str) -> None:
    if value.startswith("external://") or value.startswith("maintainer://") or value.startswith("owner://"):
        return
    path_part = value.split("#", 1)[0]
    repo_relative_path(path_part, field)


def validate_contract(contract: dict[str, Any]) -> None:
    expected_top_level = {
        "schema_version": "1",
        "id": "phase33_maintainer_decision_inputs_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase33-maintainer-decision-inputs",
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    if require_string_list(contract.get("requirement_ids"), "requirement_ids") != REQUIRED_REQUIREMENT_IDS:
        raise VerificationError("requirement_ids must be DECIDE-01, DECIDE-02, DECIDE-03")
    source_contracts = require_list(contract.get("source_contracts"), "source_contracts")
    source_ids = [require_string(require_dict(item, "source_contracts[]").get("id"), "source_contracts[].id") for item in source_contracts]
    if source_ids != REQUIRED_SOURCE_CONTRACT_IDS:
        raise VerificationError("source_contracts must list Phase 32, Phase 27, and Phase 28 contracts in order")
    source_inputs = require_dict(contract.get("source_inputs"), "source_inputs")
    if source_inputs.get("phase32_handoff") != DEFAULT_PHASE32_HANDOFF.as_posix():
        raise VerificationError("source_inputs.phase32_handoff must point to the Phase 32 handoff")
    if source_inputs.get("phase32_canonical_register") != PHASE32_REGISTER_REF:
        raise VerificationError("source_inputs.phase32_canonical_register must point to the Phase 32 register")
    if source_inputs.get("phase32_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError("source_inputs.phase32_lifecycle_id must match Phase 32")
    if source_inputs.get("raw_evidence_consumed") is not False:
        raise VerificationError("source_inputs.raw_evidence_consumed must be false")
    decision_schema = require_dict(contract.get("decision_record_schema"), "decision_record_schema")
    if require_string_list(decision_schema.get("required_fields"), "decision_record_schema.required_fields") != REQUIRED_DECISION_FIELDS:
        raise VerificationError("decision_record_schema.required_fields must match Phase 33 required fields")
    enums = require_dict(contract.get("enums"), "enums")
    if require_string_list(enums.get("decision_type"), "enums.decision_type") != DECISION_TYPES:
        raise VerificationError("enums.decision_type must match Phase 33 decision axes")
    values = require_dict(enums.get("decision_value"), "enums.decision_value")
    for decision_type, expected_values in DECISION_VALUE_ENUMS.items():
        if require_string_list(values.get(decision_type), f"enums.decision_value.{decision_type}") != expected_values:
            raise VerificationError(f"enums.decision_value.{decision_type} is invalid")
    if set(require_string_list(contract.get("hard_blocker_problem_kinds"), "hard_blocker_problem_kinds")) != HARD_BLOCKER_PROBLEM_KINDS:
        raise VerificationError("hard_blocker_problem_kinds must match Phase 33 fail-closed policy")
    exception_policy = require_dict(contract.get("exception_policy"), "exception_policy")
    if exception_policy.get("exact_source_row_ref_match") is not True or exception_policy.get("affected_gate_must_match") is not True:
        raise VerificationError("exception_policy must require exact row and gate matching")
    generated_artifacts = require_string_list(contract.get("generated_artifacts"), "generated_artifacts")
    if generated_artifacts != GENERATED_ARTIFACTS:
        raise VerificationError("generated_artifacts must list the Phase 33 output bundle exactly")
    markers = require_string_list(contract.get("prohibited_output_markers"), "prohibited_output_markers")
    if "demotion_allowed" not in markers:
        raise VerificationError("prohibited_output_markers must include demotion_allowed")


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    validate_contract(contract)
    return contract


def load_phase32_handoff(root: Path, handoff_arg: str | Path) -> tuple[Path, dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    handoff_path = path_under(handoff_arg, PHASE32_OUTPUT_ROOT, "--phase32-handoff")
    handoff = load_json(root, handoff_path)
    if handoff.get("phase_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError(f"--phase32-handoff phase_lifecycle_id must be {PHASE32_LIFECYCLE_ID}")
    register_ref = require_string(handoff.get("canonical_register_ref"), "canonical_register_ref")
    if register_ref != PHASE32_REGISTER_REF:
        raise VerificationError(f"canonical_register_ref must be {PHASE32_REGISTER_REF}")
    register_path = path_under(register_ref, PHASE32_OUTPUT_ROOT, "canonical_register_ref")
    register = load_json(root, register_path)
    if register.get("phase_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError(f"Phase 32 canonical register phase_lifecycle_id must be {PHASE32_LIFECYCLE_ID}")
    row_map: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(require_list(register.get("rows"), "Phase 32 register rows")):
        row_dict = require_dict(row, f"Phase 32 register row {index}")
        row_id = require_string(row_dict.get("row_id"), f"Phase 32 register row {index}.row_id")
        if row_id in row_map:
            raise VerificationError(f"duplicate Phase 32 row_id: {row_id}")
        row_map[row_id] = row_dict
    return handoff_path, handoff, row_map, register


def source_ref_row_id(source_ref: str, field: str = "source_row_refs") -> str:
    prefix = f"{PHASE32_REGISTER_REF}#"
    if not source_ref.startswith(prefix):
        raise VerificationError(f"{field} must use {prefix}<row_id>: {source_ref}")
    row_id = source_ref[len(prefix):]
    if not row_id or "/" in row_id or ".." in row_id:
        raise VerificationError(f"{field} contains malformed row id: {source_ref}")
    return row_id


def validate_source_row_refs(decision_id: str, field: str, source_refs: list[str], row_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    source_rows: list[dict[str, Any]] = []
    for source_ref in source_refs:
        row_id = source_ref_row_id(source_ref, field)
        maybe_row = row_map.get(row_id)
        if maybe_row is None:
            raise VerificationError(f"{decision_id}.{field} references unresolved Phase 32 row: {source_ref}")
        source_rows.append(maybe_row)
    return source_rows


def scan_json_payload(data: Any, path: Path) -> None:
    reject_forbidden_field_names(data, path.as_posix())
    reject_forbidden_text(path, json.dumps(data, sort_keys=True))


def load_maintainer_decisions(root: Path, maybe_decisions_path: str | None, row_map: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
    if maybe_decisions_path is None:
        return [], False
    decisions_path = repo_relative_path(maybe_decisions_path, "--maintainer-decisions")
    data = load_json(root, decisions_path)
    scan_json_payload(data, decisions_path)
    if data.get("schema_version") != "1":
        raise VerificationError("maintainer decisions schema_version must be 1")
    if data.get("phase") != PHASE:
        raise VerificationError(f"maintainer decisions phase must be {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(f"maintainer decisions phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
    raw_decisions = require_list(data.get("decisions"), "decisions")
    decision_ids: set[str] = set()
    parsed: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, raw_decision in enumerate(raw_decisions):
        try:
            decision = validate_decision(require_dict(raw_decision, f"decisions[{index}]"), row_map)
            decision_id = decision["decision_id"]
            if decision_id in decision_ids:
                raise VerificationError(f"duplicate decision_id: {decision_id}")
            decision_ids.add(decision_id)
            parsed.append(decision)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed, True


def validate_decision(raw_decision: dict[str, Any], row_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    decision_id = require_string(raw_decision.get("decision_id"), "decision_id")
    for field in REQUIRED_DECISION_FIELDS:
        if field not in raw_decision:
            raise VerificationError(f"{decision_id} missing required field: {field}")
    decision_type = require_string(raw_decision.get("decision_type"), f"{decision_id}.decision_type")
    if decision_type not in DECISION_VALUE_ENUMS:
        raise VerificationError(f"{decision_id} unknown decision_type: {decision_type}")
    decision_value = require_string(raw_decision.get("decision_value"), f"{decision_id}.decision_value")
    if decision_value not in DECISION_VALUE_ENUMS[decision_type]:
        raise VerificationError(f"{decision_id} invalid decision_value for {decision_type}: {decision_value}")
    source_row_refs = require_non_empty_string_list(raw_decision.get("source_row_refs"), f"{decision_id}.source_row_refs")
    source_rows = validate_source_row_refs(decision_id, "source_row_refs", source_row_refs, row_map)
    for field in ("maintainer_identity_ref", "maintainer_role", "owner_signoff_ref", "rationale"):
        require_string(raw_decision.get(field), f"{decision_id}.{field}")
    require_iso_utc(require_string(raw_decision.get("decision_timestamp"), f"{decision_id}.decision_timestamp"), f"{decision_id}.decision_timestamp")
    for field in ("evidence_refs", "artifact_refs"):
        refs = require_string_list(raw_decision.get(field), f"{decision_id}.{field}")
        for ref in refs:
            validate_reference_text(ref, f"{decision_id}.{field}")
    decision = dict(raw_decision)
    decision["decision_id"] = decision_id
    decision["decision_type"] = decision_type
    decision["decision_value"] = decision_value
    decision["source_row_refs"] = source_row_refs
    decision["source_rows"] = source_rows
    validate_axis_specific_decision(decision, row_map)
    return decision


def validate_axis_specific_decision(decision: dict[str, Any], row_map: dict[str, dict[str, Any]]) -> None:
    decision_id = str(decision["decision_id"])
    decision_type = str(decision["decision_type"])
    decision_value = str(decision["decision_value"])
    source_rows = list(decision["source_rows"])
    validate_decision_axis_rows(decision_id, decision_type, source_rows)
    if decision_value in APPROVAL_DECISION_VALUES[decision_type]:
        reject_hard_blocker_acceptance(decision_id, source_rows)
    if decision_type == "retained_code":
        if decision_value in {"accept", "exception_approve"}:
            require_string(decision.get("residual_risk_rationale"), f"{decision_id}.residual_risk_rationale")
        return
    if decision_type == "residual_risk":
        require_string_list(decision.get("affected_gates"), f"{decision_id}.affected_gates")
        require_string_list(decision.get("follow_up_refs"), f"{decision_id}.follow_up_refs")
        return
    if decision_type == "exception":
        if decision_value == "approve":
            validate_exception_approval(decision, source_rows)
        return
    if decision_type == "readiness":
        if decision_value == "block" and "blocked_source_row_refs" in decision:
            blocked_source_refs = require_string_list(decision.get("blocked_source_row_refs"), f"{decision_id}.blocked_source_row_refs")
            validate_source_row_refs(decision_id, "blocked_source_row_refs", blocked_source_refs, row_map)
            decision["blocked_source_row_refs"] = blocked_source_refs
        return
    if decision_type == "reference_demotion":
        return
    raise VerificationError(f"{decision_id} unknown decision_type: {decision_type}")


def validate_decision_axis_rows(decision_id: str, decision_type: str, source_rows: list[dict[str, Any]]) -> None:
    allowed_impacts = DECISION_TYPE_IMPACTS[decision_type]
    for row in source_rows:
        decision_impact = row.get("decision_impact")
        if decision_impact not in allowed_impacts:
            raise VerificationError(
                f"{decision_id} {decision_type} decision cannot reference "
                f"{row.get('row_id')} with decision_impact={decision_impact}"
            )


def reject_hard_blocker_acceptance(decision_id: str, source_rows: list[dict[str, Any]]) -> None:
    hard_rows = [
        str(row["row_id"])
        for row in source_rows
        if row.get("row_problem_kind") in HARD_BLOCKER_PROBLEM_KINDS
    ]
    if hard_rows:
        raise VerificationError(f"{decision_id} cannot accept hard blocker rows: {', '.join(hard_rows)}")


def validate_exception_approval(decision: dict[str, Any], source_rows: list[dict[str, Any]]) -> None:
    decision_id = str(decision["decision_id"])
    for field in [
        "scope",
        "expiry_or_review_trigger",
        "affected_requirements",
        "affected_gates",
        "linked_blocker_refs",
    ]:
        if field in {"scope", "expiry_or_review_trigger"}:
            require_string(decision.get(field), f"{decision_id}.{field}")
        elif field == "linked_blocker_refs":
            decision[field] = require_non_empty_string_list(decision.get(field), f"{decision_id}.{field}")
        else:
            require_string_list(decision.get(field), f"{decision_id}.{field}")
    require_string(decision.get("rationale"), f"{decision_id}.rationale")
    require_string(decision.get("owner_signoff_ref"), f"{decision_id}.owner_signoff_ref")
    reject_hard_blocker_acceptance(decision_id, source_rows)
    source_refs = list(decision["source_row_refs"])
    if list(decision["linked_blocker_refs"]) != source_refs:
        raise VerificationError(f"{decision_id} linked_blocker_refs must exactly match source_row_refs")
    affected_gates = set(decision["affected_gates"])
    for row in source_rows:
        if row.get("blocker_kind") != "exception_request":
            raise VerificationError(f"{decision_id} exception approval source row is not an exception_request: {row.get('row_id')}")
        affected_gate = require_string(row.get("affected_gate"), f"{decision_id}.affected_gate")
        if affected_gate not in affected_gates:
            raise VerificationError(f"{decision_id} affected_gate mismatch for {affected_gate}")


def normalized_decision_record(decision: dict[str, Any]) -> dict[str, Any]:
    row = {
        field: decision[field]
        for field in REQUIRED_DECISION_FIELDS
    }
    row["phase"] = PHASE
    row["phase_lifecycle_id"] = PHASE_LIFECYCLE_ID
    row["source_row_ids"] = [source_ref_row_id(ref) for ref in decision["source_row_refs"]]
    row["affected_gates"] = sorted({str(source_row.get("affected_gate", "")) for source_row in decision["source_rows"] if source_row.get("affected_gate")})
    row["decision_axis"] = decision["decision_type"]
    return row


def decision_records_by_type(decisions: list[dict[str, Any]], decision_type: str) -> list[dict[str, Any]]:
    return [normalized_decision_record(decision) for decision in decisions if decision["decision_type"] == decision_type]


def exception_register_rows(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for decision in decisions:
        if decision["decision_type"] != "exception":
            continue
        row = normalized_decision_record(decision)
        row["coverage_state"] = "approved-exception" if decision["decision_value"] == "approve" else "rejected"
        rows.append(row)
    return rows


def approved_exception_covered_refs(decisions: list[dict[str, Any]]) -> set[str]:
    refs: set[str] = set()
    for decision in decisions:
        if decision["decision_type"] == "exception" and decision["decision_value"] == "approve":
            refs.update(decision["source_row_refs"])
    return refs


def accepted_residual_risk_covered_refs(decisions: list[dict[str, Any]]) -> set[str]:
    refs: set[str] = set()
    for decision in decisions:
        if decision["decision_type"] == "residual_risk" and decision["decision_value"] == "accept":
            refs.update(decision["source_row_refs"])
    return refs


def accepted_retained_code_covered_refs(decisions: list[dict[str, Any]]) -> set[str]:
    refs: set[str] = set()
    for decision in decisions:
        if decision["decision_type"] == "retained_code" and decision["decision_value"] in {"accept", "exception_approve"}:
            refs.update(decision["source_row_refs"])
    return refs


def readiness_uncovered_blocker_refs(row_map: dict[str, dict[str, Any]], covered_refs: set[str]) -> list[str]:
    uncovered = []
    for row_id, row in row_map.items():
        row_ref = f"{PHASE32_REGISTER_REF}#{row_id}"
        if row_ref in covered_refs:
            continue
        if row.get("severity") == "critical" or row.get("row_problem_kind") in HARD_BLOCKER_PROBLEM_KINDS:
            uncovered.append(row_ref)
    return sorted(uncovered)


def readiness_handoff(decisions: list[dict[str, Any]], row_map: dict[str, dict[str, Any]], maintainer_input_supplied: bool) -> dict[str, Any]:
    readiness_decisions = [decision for decision in decisions if decision["decision_type"] == "readiness"]
    if not readiness_decisions:
        return {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "handoff_state": "blocked-pending-maintainer-input",
            "readiness_input_supplied": False,
            "blocked_source_row_refs": [],
            "rationale": "No explicit Phase 33 readiness decision input was supplied.",
        }
    latest = readiness_decisions[-1]
    if latest["decision_value"] == "approve":
        covered = (
            approved_exception_covered_refs(decisions)
            | accepted_residual_risk_covered_refs(decisions)
            | accepted_retained_code_covered_refs(decisions)
        )
        uncovered = readiness_uncovered_blocker_refs(row_map, covered)
        if uncovered:
            raise VerificationError("readiness approval has uncovered critical blocker or hard blocker rows: " + ", ".join(uncovered))
        return {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "handoff_state": "approval-input-recorded",
            "readiness_input_supplied": maintainer_input_supplied,
            "decision_id": latest["decision_id"],
            "source_row_refs": latest["source_row_refs"],
            "phase34_must_generate_final_readiness": True,
            "rationale": latest["rationale"],
        }
    blocked_refs = latest.get("blocked_source_row_refs", latest["source_row_refs"])
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "handoff_state": "blocked-by-maintainer-input",
        "readiness_input_supplied": maintainer_input_supplied,
        "decision_id": latest["decision_id"],
        "blocked_source_row_refs": blocked_refs,
        "rationale": latest["rationale"],
    }


def demotion_handoff(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    demotion_decisions = [decision for decision in decisions if decision["decision_type"] == "reference_demotion"]
    if not demotion_decisions:
        return {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "authorization_state": "blocked",
            "demotion_input_supplied": False,
            "phase34_must_validate_readiness": True,
            "rationale": "Reference demotion requires a separate explicit Phase 33 decision input.",
        }
    latest = demotion_decisions[-1]
    if latest["decision_value"] == "approve":
        return {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "authorization_state": "approved-input-recorded",
            "demotion_input_supplied": True,
            "decision_id": latest["decision_id"],
            "source_row_refs": latest["source_row_refs"],
            "maintainer_identity_ref": latest["maintainer_identity_ref"],
            "maintainer_role": latest["maintainer_role"],
            "decision_timestamp": latest["decision_timestamp"],
            "phase34_must_validate_readiness": True,
            "rationale": latest["rationale"],
        }
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "authorization_state": "rejected",
        "demotion_input_supplied": True,
        "decision_id": latest["decision_id"],
        "source_row_refs": latest["source_row_refs"],
        "phase34_must_validate_readiness": True,
        "rationale": latest["rationale"],
    }


def maintainer_input_template(row_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    maybe_first_row_ref = ""
    if row_map:
        maybe_first_row_ref = f"{PHASE32_REGISTER_REF}#{next(iter(sorted(row_map)))}"
    return {
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "decisions": [
            {
                "decision_id": "phase33-example-decision",
                "decision_type": "readiness",
                "decision_value": "block",
                "source_row_refs": [maybe_first_row_ref] if maybe_first_row_ref else [],
                "maintainer_identity_ref": "maintainer://name-or-group",
                "maintainer_role": "cutover-maintainer",
                "owner_signoff_ref": "owner://signoff/ref",
                "decision_timestamp": "2026-07-04T00:00:00Z",
                "rationale": "Explicit maintainer rationale goes here.",
                "evidence_refs": [],
                "artifact_refs": [],
            }
        ],
    }


def validation_report(decisions: list[dict[str, Any]], maintainer_input_supplied: bool) -> dict[str, Any]:
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "maintainer_input_supplied": maintainer_input_supplied,
        "decision_count": len(decisions),
        "decision_counts_by_type": {
            decision_type: sum(1 for decision in decisions if decision["decision_type"] == decision_type)
            for decision_type in DECISION_TYPES
        },
        "validation_state": "passed",
    }


def redacted_report(records: list[dict[str, Any]], readiness: dict[str, Any], demotion: dict[str, Any]) -> str:
    lines = [
        "# Phase 33 Maintainer Decision Input Report",
        "",
        "Machine-readable JSON records are authoritative. This report summarizes explicit decision inputs only.",
        "",
        f"phase: {PHASE}",
        f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
        f"decision_count: {len(records)}",
        f"readiness_handoff_state: {readiness['handoff_state']}",
        f"reference_demotion_authorization_state: {demotion['authorization_state']}",
        "",
        "| Decision ID | Type | Value | Source Rows |",
        "| ----------- | ---- | ----- | ----------- |",
    ]
    for record in records:
        lines.append(
            f"| {record['decision_id']} | {record['decision_type']} | {record['decision_value']} | {len(record['source_row_refs'])} |"
        )
    return "\n".join(lines) + "\n"


def copy_contract_snapshots(root: Path, output_dir: Path, phase32_handoff_path: Path, phase32_register: dict[str, Any], phase32_register_ref: str) -> list[str]:
    snapshot_dir = output_dir / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    refs: list[str] = []
    for snapshot_name, source in SOURCE_CONTRACT_SNAPSHOTS.items():
        source_path = root / source
        if not source_path.exists():
            raise VerificationError(f"missing snapshot source: {source.as_posix()}")
        destination = snapshot_dir / snapshot_name
        shutil.copy2(source_path, destination)
        refs.append((output_dir.relative_to(root) / "contract-snapshots" / snapshot_name).as_posix())
    shutil.copy2(root / phase32_handoff_path, snapshot_dir / "phase32-downstream-handoff-manifest.json")
    write_json(snapshot_dir / "phase32-blocker-register.json", phase32_register)
    refs.append((output_dir.relative_to(root) / "contract-snapshots/phase32-downstream-handoff-manifest.json").as_posix())
    refs.append((output_dir.relative_to(root) / "contract-snapshots/phase32-blocker-register.json").as_posix())
    if phase32_register_ref != PHASE32_REGISTER_REF:
        raise VerificationError(f"Phase 33 source row refs require canonical Phase 32 register {PHASE32_REGISTER_REF}")
    return refs


def downstream_handoff_manifest(
    output_dir: Path,
    phase32_handoff_ref: Path,
    maintainer_input_supplied: bool,
    snapshot_refs: list[str],
) -> dict[str, Any]:
    relative_output_dir = repo_relative_output_dir(output_dir)
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase33-maintainer-decision-inputs",
        "generated_at_utc": utc_now(),
        "output_root": relative_output_dir.as_posix(),
        "maintainer_input_supplied": maintainer_input_supplied,
        "raw_evidence_consumed": False,
        "source_inputs": {
            "phase32_handoff_ref": phase32_handoff_ref.as_posix(),
            "phase32_canonical_register_ref": PHASE32_REGISTER_REF,
            "raw_evidence_consumed": False,
        },
        "register_refs": {
            "normalized_decision_records": (relative_output_dir / "normalized-decision-records.json").as_posix(),
            "retained_code_decision_register": (relative_output_dir / "retained-code-decision-register.json").as_posix(),
            "residual_risk_decision_register": (relative_output_dir / "residual-risk-decision-register.json").as_posix(),
            "exception_decision_register": (relative_output_dir / "exception-decision-register.json").as_posix(),
            "readiness_decision_handoff": (relative_output_dir / "readiness-decision-handoff.json").as_posix(),
            "demotion_decision_handoff": (relative_output_dir / "demotion-decision-handoff.json").as_posix(),
            "decision_validation_report": (relative_output_dir / "decision-validation-report.json").as_posix(),
        },
        "contract_snapshot_refs": snapshot_refs,
        "downstream_consumers": [
            "phase34-final-readiness-and-demotion-dry-run",
            "phase35-cutover-decision-artifact",
        ],
    }


def write_phase33_outputs(
    root: Path,
    output_dir_arg: str | Path,
    handoff_path: Path,
    row_map: dict[str, dict[str, Any]],
    phase32_register: dict[str, Any],
    decisions: list[dict[str, Any]],
    maintainer_input_supplied: bool,
) -> None:
    relative_output_dir, full_output_dir = output_dir_path(root, output_dir_arg)
    reset_output_root(full_output_dir)
    records = [normalized_decision_record(decision) for decision in decisions]
    readiness = readiness_handoff(decisions, row_map, maintainer_input_supplied)
    demotion = demotion_handoff(decisions)
    snapshot_refs = copy_contract_snapshots(root, full_output_dir, handoff_path, phase32_register, PHASE32_REGISTER_REF)
    write_json(full_output_dir / "maintainer-decision-input-template.json", maintainer_input_template(row_map))
    write_json(full_output_dir / "normalized-decision-records.json", {"rows": records})
    write_json(full_output_dir / "retained-code-decision-register.json", {"rows": decision_records_by_type(decisions, "retained_code")})
    write_json(full_output_dir / "residual-risk-decision-register.json", {"rows": decision_records_by_type(decisions, "residual_risk")})
    write_json(full_output_dir / "exception-decision-register.json", {"rows": exception_register_rows(decisions)})
    write_json(full_output_dir / "readiness-decision-handoff.json", readiness)
    write_json(full_output_dir / "demotion-decision-handoff.json", demotion)
    write_json(full_output_dir / "decision-validation-report.json", validation_report(decisions, maintainer_input_supplied))
    manifest = downstream_handoff_manifest(relative_output_dir, handoff_path, maintainer_input_supplied, snapshot_refs)
    write_json(full_output_dir / "downstream-handoff-manifest.json", manifest)
    (full_output_dir / "redacted-maintainer-decision-report.md").write_text(redacted_report(records, readiness, demotion), encoding="utf-8")
    run_security_scan(root, output_dir=relative_output_dir)


def run_quick(root: Path, phase32_handoff: str | Path, output_dir: str | Path, maybe_decisions_path: str | None) -> None:
    load_contract(root)
    _relative_output_dir, full_output_dir = output_dir_path(root, output_dir)
    reject_decisions_inside_output(root, maybe_decisions_path, full_output_dir)
    handoff_path, _handoff, row_map, phase32_register = load_phase32_handoff(root, phase32_handoff)
    decisions, maintainer_input_supplied = load_maintainer_decisions(root, maybe_decisions_path, row_map)
    write_phase33_outputs(root, output_dir, handoff_path, row_map, phase32_register, decisions, maintainer_input_supplied)
    print(f"Phase 33 maintainer decision inputs quick validation passed; decision_count={len(decisions)}")


def run_security_scan(root: Path, maybe_decisions_path: str | None = None, output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> None:
    errors: list[str] = []
    if maybe_decisions_path is not None:
        try:
            decisions_path = repo_relative_path(maybe_decisions_path, "--maintainer-decisions")
            data = load_json(root, decisions_path)
            scan_json_payload(data, decisions_path)
        except VerificationError as error:
            errors.append(str(error))
    relative_output_dir = path_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    full_output_dir = root / relative_output_dir
    if full_output_dir.exists():
        if full_output_dir.is_symlink() or not full_output_dir.is_dir():
            errors.append(f"Phase 33 output root is not a normal directory: {relative_output_dir.as_posix()}")
        else:
            for artifact in EMITTED_OUTPUT_SCAN_ARTIFACTS:
                path = full_output_dir / artifact
                if not path.exists() or path.is_dir():
                    continue
                relative_path = path.relative_to(root)
                try:
                    text = path.read_text(encoding="utf-8")
                    reject_forbidden_text(relative_path, text)
                    if path.suffix == ".json":
                        reject_forbidden_field_names(json.loads(text), relative_path.as_posix())
                except (json.JSONDecodeError, VerificationError) as error:
                    errors.append(str(error))
    else:
        print(f"no Phase 33 outputs to scan at {relative_output_dir.as_posix()}")
    if errors:
        raise VerificationError("\n".join(errors))
    print(f"Phase 33 security scan passed for {relative_output_dir.as_posix()}")


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
            if stripped.startswith("python3 "):
                commands.append(stripped)
        return commands
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
            if stripped:
                commands.append(stripped)
        return commands
    return None


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    required_text = {
        Path("tools/bazel/BUILD.bazel"): [
            'name = "phase33_source_ref_manifests"',
            'name = "phase33_verify"',
            'name = "phase33_verify_tests"',
            '"phase33_maintainer_decision_inputs.py"',
            '"phase33_maintainer_decision_inputs_test.py"',
            '"manifests/phase33_maintainer_decision_inputs_contract.json"',
            "//:phase33_maintainer_decision_inputs_docs",
        ],
        Path("BUILD.bazel"): [
            'name = "phase33_maintainer_decision_inputs_docs"',
            'name = "phase33_verify"',
            'actual = "//tools/bazel:phase33_verify"',
            'name = "phase33_verify_tests"',
            'actual = "//tools/bazel:phase33_verify_tests"',
        ],
        Path("tools/bazel/rust_workflow.sh"): [
            "phase33_verify)",
            "phase33_verify_tests)",
            "python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only",
        ],
        Path("justfile"): [
            "phase33-verify:",
            "bazel run //tools/bazel:phase33_verify_tests",
            "bazel run //tools/bazel:phase33_verify",
        ],
    }
    for path, snippets in required_text.items():
        try:
            text = read_text(root, path)
        except VerificationError as error:
            errors.append(str(error))
            continue
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{path.as_posix()} missing {snippet}")
    try:
        workflow_text = read_text(root, "tools/bazel/rust_workflow.sh")
        verify_commands = shell_case_commands(workflow_text, "phase33_verify")
        test_commands = shell_case_commands(workflow_text, "phase33_verify_tests")
        if verify_commands != PHASE33_VERIFY_COMMANDS:
            errors.append("tools/bazel/rust_workflow.sh phase33_verify command order is invalid")
        if test_commands != ["python3 tools/bazel/phase33_maintainer_decision_inputs_test.py"]:
            errors.append("tools/bazel/rust_workflow.sh phase33_verify_tests command is invalid")
    except VerificationError as error:
        errors.append(str(error))
    try:
        just_commands = just_recipe_commands(read_text(root, "justfile"), "phase33-verify")
        if just_commands != [
            "bazel run //tools/bazel:phase33_verify_tests",
            "bazel run //tools/bazel:phase33_verify",
        ]:
            errors.append("justfile phase33-verify must run tests before verifier")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    print("Phase 33 wiring passed")


def contract_only(root: Path = ROOT) -> None:
    contract = load_contract(root)
    print(f"{contract['id']} ok")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase 33 maintainer decision inputs.")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 33 contract")
    parser.add_argument("--quick", action="store_true", help="write Phase 33 maintainer decision handoff artifacts")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 33 inputs and generated artifacts")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel, workflow, and just wiring")
    parser.add_argument("--maintainer-decisions", help="optional explicit maintainer decision input JSON")
    parser.add_argument("--phase32-handoff", default=DEFAULT_PHASE32_HANDOFF.as_posix(), help="Phase 32 downstream handoff manifest")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 33 output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.contract_only:
            contract_only(ROOT)
            return 0
        if args.security_only:
            run_security_scan(ROOT, args.maintainer_decisions, args.output_dir)
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            return 0
        if args.quick:
            run_security_scan(ROOT, args.maintainer_decisions, args.output_dir)
            run_quick(ROOT, args.phase32_handoff, args.output_dir, args.maintainer_decisions)
            return 0
        raise VerificationError("no mode selected")
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
