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
PHASE = "27-retained-code-and-maintainer-acceptance-decisions"
PHASE_LIFECYCLE_ID = "27-2026-06-25T01-06-06"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json")
PHASE18_CONTRACT = Path("tools/bazel/manifests/phase18_cutover_review_contract.json")
PHASE26_CONTRACT = Path("tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json")
PHASE11_RETAINED_CODE = Path("tools/bazel/manifests/phase11_retained_code_justifications.json")
FOREIGN_CODE_INVENTORY = Path("tools/bazel/manifests/foreign_code_inventory.json")
UNSAFE_BOUNDARY_AUDIT = Path("tools/bazel/manifests/unsafe_boundary_audit.json")
PHASE11_CUTOVER_READINESS = Path("tools/bazel/manifests/phase11_cutover_readiness.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase27")
PHASE26_UPSTREAM_ROWS = Path("build/ci-evidence/phase26/upstream-result-row-table.json")
PHASE26_GENERATION_COMMAND = (
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26"
)
PHASE27_DOCS = [
    ".planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-CONTEXT.md",
    ".planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-RESEARCH.md",
    ".planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-VALIDATION.md",
    ".planning/phases/27-retained-code-and-maintainer-acceptance-decisions/27-01-PLAN.md",
]
PHASE27_SOURCE_REF_MANIFESTS = [
    "manifests/phase11_cutover_readiness.json",
    "manifests/phase11_retained_code_justifications.json",
    "manifests/foreign_code_inventory.json",
    "manifests/unsafe_boundary_audit.json",
    "manifests/phase18_cutover_review_contract.json",
    "manifests/phase26_release_signing_upstream_evidence_contract.json",
    "manifests/phase27_retained_code_acceptance_decisions_contract.json",
]
PHASE27_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --wiring-only",
    PHASE26_GENERATION_COMMAND,
    (
        "python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick "
        "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
        "--output-dir build/ci-evidence/phase27"
    ),
]
PHASE27_TEST_COMMAND = "python3 tools/bazel/phase27_retained_code_acceptance_decisions_test.py"
DECISION_AXES = [
    "evidence_state",
    "maintainer_decision",
    "exception_state",
    "residual_risk_state",
    "hard_failure_state",
    "demotion_authorization",
]
GENERATED_ARTIFACTS = [
    "acceptance-run-manifest.json",
    "normalized-retained-code-decisions.json",
    "residual-risk-register.json",
    "exception-decision-register.json",
    "final-readiness-decision-summary.json",
    "phase28-handoff-manifest.json",
    "decision-row-table.json",
    "maintainer-acceptance-input-template.json",
    "artifact-reference-summary.json",
    "contract-snapshots/phase18_cutover_review_contract.json",
    "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json",
    "contract-snapshots/phase26-upstream-result-row-table.json",
]
SOURCE_CONTRACT_PATHS = [
    PHASE18_CONTRACT,
    PHASE26_CONTRACT,
    PHASE11_RETAINED_CODE,
    FOREIGN_CODE_INVENTORY,
    UNSAFE_BOUNDARY_AUDIT,
    PHASE11_CUTOVER_READINESS,
]
FORBIDDEN_FIELD_NAMES = {
    "binary_dump",
    "binary_dump_bytes",
    "credential",
    "credential_value",
    "crash_dump_bytes",
    "firmware_payload_bytes",
    "password",
    "password_value",
    "private_certificate",
    "private_certificate_pem",
    "private_key",
    "raw_firmware_payload",
    "raw_key_bytes",
    "raw_log",
    "raw_log_bytes",
    "raw_logs",
    "secret",
    "secret_value",
    "signing_key_value",
    "signing_payload_bytes",
    "token",
    "token_value",
    "demotion_allowed",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("private-certificate-block", re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
    (
        "forbidden-sensitive-marker",
        re.compile(
            r"\b(private[_-]?key|private[_-]?certificate|raw[_-]?key[_-]?bytes|signing[_-]?key[_-]?value|"
            r"signing[_-]?payload[_-]?bytes|raw[_-]?firmware[_-]?payload|firmware[_-]?payload[_-]?bytes|"
            r"raw[_-]?logs?|binary[_-]?dump|crash[_-]?dump[_-]?bytes|token[_-]?value|password[_-]?value|"
            r"credential[_-]?value|secret[_-]?value)\b",
            re.IGNORECASE,
        ),
    ),
    ("reference-demotion-approved", re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("demotion-allowed", re.compile(r"\bdemotion allowed\b", re.IGNORECASE)),
    ("final-readiness-approved", re.compile(r"\bfinal readiness approved\b", re.IGNORECASE)),
    (
        "evidence-alone-acceptance",
        re.compile(r"\bretained[- ]code accepted by evidence alone\b", re.IGNORECASE),
    ),
)


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(root: Path, path: Path) -> str:
    full_path = root / path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read_text(root, path))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(f"{path.as_posix()} must contain a top-level object")
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


def require_list(row: dict[str, Any], field: str, row_name: str) -> list[Any]:
    value = row.get(field)
    if not isinstance(value, list):
        raise VerificationError(f"{row_name} {field} must be a list")
    return value


def require_string_list(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    values = require_list(row, field, row_name)
    if not all(isinstance(value, str) and value for value in values):
        raise VerificationError(f"{row_name} {field} must contain non-empty strings")
    return values


def require_dict(row: dict[str, Any], field: str, row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def normalized_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", field_name.casefold())


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            errors.append(f"{path.as_posix()} contains forbidden marker {label}: {match.group(0)}")
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_field_names(value: Any, path: str) -> None:
    normalized_forbidden = {normalized_field_name(field_name) for field_name in FORBIDDEN_FIELD_NAMES}

    def walk(candidate: Any, candidate_path: str, errors: list[str]) -> None:
        if isinstance(candidate, dict):
            for key, child in candidate.items():
                child_path = f"{candidate_path}.{key}"
                if normalized_field_name(str(key)) in normalized_forbidden:
                    errors.append(f"{path} contains forbidden field {key} at {child_path}")
                walk(child, child_path, errors)
            return
        if isinstance(candidate, list):
            for index, child in enumerate(candidate):
                walk(child, f"{candidate_path}[{index}]", errors)

    errors: list[str] = []
    walk(value, "$", errors)
    if errors:
        raise VerificationError("\n".join(errors))


def repo_relative_path(value: str, option_name: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise VerificationError(f"{option_name} must be repo-relative without parent traversal: {value}")
    return path


def validate_output_dir(root: Path, output_dir: Path) -> tuple[Path, Path]:
    if output_dir.is_absolute() or ".." in output_dir.parts:
        raise VerificationError(f"--output-dir must be repo-relative under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}")
    try:
        output_dir.relative_to(DEFAULT_OUTPUT_DIR)
    except ValueError as error:
        raise VerificationError(f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}") from error
    current = root
    for part in output_dir.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(f"--output-dir contains a symlink escape risk: {output_dir.as_posix()}")
    full_output_dir = (root / output_dir).resolve(strict=False)
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"--output-dir must resolve under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}") from error
    return output_dir, full_output_dir


def reset_output_root(root: Path, output_dir: Path) -> Path:
    relative_output_dir, full_output_dir = validate_output_dir(root, output_dir)
    if full_output_dir.exists():
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)
    return relative_output_dir


def phase18_retained_packet_ids(phase18_contract: dict[str, Any]) -> list[str]:
    packets = phase18_retained_packets(phase18_contract)
    ids: list[str] = []
    for packet in packets:
        ids.append(require_string(packet, "id", "Phase 18 retained packet"))
    if len(ids) != len(set(ids)):
        raise VerificationError("Phase 18 retained packet IDs must be unique")
    return ids


def phase18_retained_packets(phase18_contract: dict[str, Any]) -> list[dict[str, Any]]:
    packets = require_list(phase18_contract, "retained_code_acceptance_packets", "Phase 18 contract")
    parsed_packets: list[dict[str, Any]] = []
    for index, packet in enumerate(packets):
        if not isinstance(packet, dict):
            raise VerificationError(f"Phase 18 retained_code_acceptance_packets[{index}] must be an object")
        require_string(packet, "id", f"Phase 18 retained_code_acceptance_packets[{index}]")
        parsed_packets.append(packet)
    return parsed_packets


def phase18_upstream_requirements(phase18_contract: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = require_list(phase18_contract, "upstream_result_requirements", "Phase 18 contract")
    parsed_requirements: list[dict[str, Any]] = []
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            raise VerificationError(f"Phase 18 upstream_result_requirements[{index}] must be an object")
        require_string(requirement, "criterion_id", f"Phase 18 upstream_result_requirements[{index}]")
        parsed_requirements.append(requirement)
    return parsed_requirements


def phase18_upstream_criterion_ids(phase18_contract: dict[str, Any]) -> list[str]:
    requirements = phase18_upstream_requirements(phase18_contract)
    ids: list[str] = []
    for requirement in requirements:
        ids.append(require_string(requirement, "criterion_id", "Phase 18 upstream requirement"))
    if len(ids) != len(set(ids)):
        raise VerificationError("Phase 18 upstream criterion IDs must be unique")
    return ids


def phase18_hard_blocker_reasons(phase18_contract: dict[str, Any]) -> list[str]:
    requirements = phase18_upstream_requirements(phase18_contract)
    maybe_reasons: list[str] | None = None
    for index, requirement in enumerate(requirements):
        reasons = require_string_list(requirement, "hard_blocker_reasons", f"Phase 18 upstream_result_requirements[{index}]")
        if maybe_reasons is None:
            maybe_reasons = reasons
        elif reasons != maybe_reasons:
            raise VerificationError("Phase 18 upstream hard blocker reasons must be consistent across criteria")
    if maybe_reasons is None:
        raise VerificationError("Phase 18 upstream_result_requirements must not be empty")
    return maybe_reasons


def check_phase18_surfaces(phase18_contract: dict[str, Any]) -> dict[str, Any]:
    retained_schema = require_dict(phase18_contract, "retained_code_acceptance_packet_schema", "Phase 18 contract")
    final_schema = require_dict(phase18_contract, "final_decision_schema", "Phase 18 contract")
    exception_schema = require_dict(final_schema, "exception", "Phase 18 final_decision_schema")
    return {
        "retained_packet_ids": phase18_retained_packet_ids(phase18_contract),
        "upstream_criterion_ids": phase18_upstream_criterion_ids(phase18_contract),
        "retained_required_fields": require_string_list(retained_schema, "required_fields", "Phase 18 retained packet schema"),
        "final_decision_required_fields": require_string_list(final_schema, "required_fields", "Phase 18 final decision schema"),
        "exception_required_fields": require_string_list(exception_schema, "required_fields", "Phase 18 exception schema"),
        "retained_packet_status_vocabulary": require_string_list(
            phase18_contract,
            "retained_packet_status_vocabulary",
            "Phase 18 contract",
        ),
        "final_criterion_status_vocabulary": require_string_list(
            phase18_contract,
            "final_criterion_status_vocabulary",
            "Phase 18 contract",
        ),
        "review_decision_vocabulary": require_string_list(
            phase18_contract,
            "review_decision_vocabulary",
            "Phase 18 contract",
        ),
        "hard_blocker_reasons": phase18_hard_blocker_reasons(phase18_contract),
    }


def check_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    phase18_contract = load_json(root, PHASE18_CONTRACT)
    load_json(root, PHASE26_CONTRACT)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase27_retained_code_acceptance_decisions_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase27-retained-code-acceptance-decisions",
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "phase26_upstream_rows_path": PHASE26_UPSTREAM_ROWS.as_posix(),
        "phase26_generation_command": PHASE26_GENERATION_COMMAND,
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    source_contracts = require_list(contract, "source_contracts", "Phase 27 contract")
    source_paths = []
    for index, source_contract in enumerate(source_contracts):
        if not isinstance(source_contract, dict):
            errors.append(f"source_contracts[{index}] must be an object")
            continue
        source_path = source_contract.get("path")
        if not isinstance(source_path, str) or not source_path:
            errors.append(f"source_contracts[{index}] path must be a non-empty string")
            continue
        source_paths.append(Path(source_path))
        if Path(source_path).is_absolute() or ".." in Path(source_path).parts:
            errors.append(f"source_contracts[{index}] path must be repo-relative: {source_path}")
        elif not (root / source_path).exists():
            errors.append(f"source_contracts[{index}] path does not exist: {source_path}")
    if source_paths != SOURCE_CONTRACT_PATHS:
        errors.append("source_contracts must list the exact Phase 27 source contracts in plan order")
    canonical_policy = require_dict(contract, "canonical_policy", "Phase 27 contract")
    if canonical_policy.get("phase18_contract") != PHASE18_CONTRACT.as_posix():
        errors.append("canonical_policy phase18_contract must point to the Phase 18 contract")
    surfaces = check_phase18_surfaces(phase18_contract)
    if contract.get("decision_axes") != DECISION_AXES:
        errors.append("decision_axes must exactly match the Phase 27 orthogonal axes")
    hard_blocker_policy = require_dict(contract, "hard_blocker_policy", "Phase 27 contract")
    if hard_blocker_policy.get("evaluate_before_exception") is not True:
        errors.append("hard_blocker_policy evaluate_before_exception must be true")
    if hard_blocker_policy.get("reasons") != surfaces["hard_blocker_reasons"]:
        errors.append("hard_blocker_policy reasons must match Phase 18 hard blocker reasons exactly")
    exception_policy = require_dict(contract, "exception_policy", "Phase 27 contract")
    if exception_policy.get("phase18_required_fields") != surfaces["exception_required_fields"]:
        errors.append("exception_policy phase18_required_fields must match Phase 18 exception fields")
    phase27_exception_fields = exception_policy.get("phase27_required_fields")
    if not isinstance(phase27_exception_fields, list):
        errors.append("exception_policy phase27_required_fields must be a list")
    else:
        for field in [*surfaces["exception_required_fields"], "residual_risk", "owner"]:
            if field not in phase27_exception_fields:
                errors.append(f"exception_policy phase27_required_fields missing {field}")
    handoff_policy = require_dict(contract, "phase28_handoff_policy", "Phase 27 contract")
    if handoff_policy.get("demotion_authorization") != "blocked":
        errors.append("phase28_handoff_policy demotion_authorization must be blocked")
    if handoff_policy.get("phase27_may_authorize_demotion") is not False:
        errors.append("phase28_handoff_policy phase27_may_authorize_demotion must be false")
    generated_artifacts = require_string_list(contract, "generated_artifacts", "Phase 27 contract")
    if generated_artifacts != GENERATED_ARTIFACTS:
        errors.append("generated_artifacts must list the Phase 27 retained output files exactly")
    if errors:
        raise VerificationError("\n".join(errors))
    return {
        "contract": contract,
        "phase18_contract": phase18_contract,
        "phase26_contract": load_json(root, PHASE26_CONTRACT),
        "phase18_surfaces": surfaces,
    }


def source_contract_refs(contract: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for source_contract in require_list(contract, "source_contracts", "Phase 27 contract"):
        if not isinstance(source_contract, dict):
            raise VerificationError("Phase 27 source_contracts entries must be objects")
        refs.append(
            {
                "id": require_string(source_contract, "id", "Phase 27 source contract"),
                "path": require_string(source_contract, "path", "Phase 27 source contract"),
            }
        )
    return refs


def phase26_required_row_fields(phase26_contract: dict[str, Any]) -> list[str]:
    upstream_policy = require_dict(phase26_contract, "upstream_policy", "Phase 26 contract")
    return require_string_list(upstream_policy, "row_required_fields", "Phase 26 upstream policy")


def load_phase26_upstream_rows(root: Path, path: Path, phase18_contract: dict[str, Any], phase26_contract: dict[str, Any]) -> list[dict[str, Any]]:
    if not (root / path).exists():
        raise VerificationError(
            f"missing Phase 26 upstream result row table: {path.as_posix()}\n"
            f"Generate it first with: {PHASE26_GENERATION_COMMAND}"
        )
    text = read_text(root, path)
    reject_forbidden_text(path, text)
    data = json.loads(text)
    reject_forbidden_field_names(data, path.as_posix())
    if not isinstance(data, dict):
        raise VerificationError(f"{path.as_posix()} must contain a top-level object")
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{path.as_posix()} must contain a rows list")
    required_fields = phase26_required_row_fields(phase26_contract)
    expected_ids = phase18_upstream_criterion_ids(phase18_contract)
    parsed_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"Phase 26 upstream row {index}"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        missing = [field for field in required_fields if field not in row]
        if missing:
            errors.append(f"{row_name} missing required fields: {', '.join(missing)}")
        try:
            require_string(row, "criterion_id", row_name)
            require_string(row, "status", row_name)
            require_string(row, "redaction_status", row_name)
            require_string(row, "source_ref_status", row_name)
            require_string(row, "source_lifecycle_status", row_name)
        except VerificationError as error:
            errors.append(str(error))
        parsed_rows.append(row)
    ids = [str(row.get("criterion_id")) for row in parsed_rows]
    if ids != expected_ids:
        errors.append("Phase 26 upstream rows must match the nine Phase 18 criteria in canonical order")
    if len(ids) != len(set(ids)):
        errors.append("Phase 26 upstream rows must not duplicate criterion_id")
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def maintainer_input_template(phase18_contract: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    retained_rows = []
    for packet in phase18_retained_packets(phase18_contract):
        retained_rows.append(
            {
                "packet_id": require_string(packet, "id", "retained packet"),
                "decision": "",
                "approver": "",
                "approver_role": packet.get("approver_role", ""),
                "decision_timestamp": "",
                "rationale": "",
                "evidence_refs": list(packet.get("required_evidence_refs", [])),
                "residual_risk": "",
                "redaction_summary": "",
                "hard_failure_reasons": [],
                "exception": {
                    "scope": "",
                    "rationale": "",
                    "approver": "",
                    "approver_role": "",
                    "affected_printer_or_release_surface": "",
                    "mitigation_or_follow_up": "",
                    "expiry_or_review_trigger": "",
                    "evidence_refs": [],
                    "residual_risk": "",
                    "owner": "",
                },
            }
        )
    final_rows = []
    for requirement in phase18_upstream_requirements(phase18_contract):
        criterion_id = require_string(requirement, "criterion_id", "upstream requirement")
        final_rows.append(
            {
                "decision_id": f"phase27-final-readiness-{criterion_id}",
                "criterion_id": criterion_id,
                "decision": "",
                "status": "pending",
                "approver": "",
                "approver_role": "",
                "decision_timestamp": "",
                "rationale": "",
                "evidence_refs": [],
                "residual_risk": "",
                "exception": {},
                "redaction_summary": "",
                "hard_failure_reasons": [],
            }
        )
    handoff_policy = require_dict(contract, "phase28_handoff_policy", "Phase 27 contract")
    return {
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "retained_code_decisions": retained_rows,
        "final_readiness_decisions": final_rows,
        "reference_demotion_decision": {
            "demotion_authorization": handoff_policy["demotion_authorization"],
            "phase27_may_authorize_demotion": handoff_policy["phase27_may_authorize_demotion"],
            "phase28_required_decision": handoff_policy["phase28_required_decision"],
        },
    }


def load_maintainer_input(root: Path, maybe_path: str | None) -> dict[str, Any] | None:
    if maybe_path is None:
        return None
    path = repo_relative_path(maybe_path, "--maintainer-input")
    text = read_text(root, path)
    reject_forbidden_text(path, text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"{path.as_posix()} is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, path.as_posix())
    if not isinstance(data, dict):
        raise VerificationError("--maintainer-input must contain a top-level object")
    return data


def detect_hard_failure_reasons(row: dict[str, Any], allowed_reasons: list[str], row_name: str) -> list[str]:
    reasons: list[str] = []
    explicit_reasons = row.get("hard_failure_reasons")
    if explicit_reasons is not None:
        if not isinstance(explicit_reasons, list) or not all(isinstance(reason, str) and reason for reason in explicit_reasons):
            raise VerificationError(f"{row_name} hard_failure_reasons must contain non-empty strings")
        for reason in explicit_reasons:
            if reason not in allowed_reasons:
                raise VerificationError(f"{row_name} hard_failure_reasons contains unknown reason: {reason}")
            reasons.append(reason)

    def add(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    status = row.get("status")
    if status == "rejected-redaction":
        add("redaction-failed")
    if status == "rejected-overclaim":
        add("overclaim-failed")
    redaction_status = row.get("redaction_status")
    if isinstance(redaction_status, str) and redaction_status not in {"passed", "not-required"}:
        add("redaction-failed")
    overclaim_status = row.get("overclaim_status")
    if isinstance(overclaim_status, str) and overclaim_status not in {"passed", "not-required"}:
        add("overclaim-failed")
    source_ref_status = row.get("source_ref_status")
    if isinstance(source_ref_status, str) and source_ref_status not in {"passed", "not-required"}:
        add("source-ref-failed")
    source_lifecycle_status = row.get("source_lifecycle_status")
    if isinstance(source_lifecycle_status, str) and source_lifecycle_status not in {"current", "not-required"}:
        add("lifecycle-mismatch")
    unsafe_ref_status = row.get("unsafe_ref_status")
    if isinstance(unsafe_ref_status, str) and unsafe_ref_status not in {"passed", "not-required"}:
        add("unsafe-ref")
    return reasons


def status_for_hard_failure(reasons: list[str]) -> str:
    if "redaction-failed" in reasons:
        return "rejected-redaction"
    if "overclaim-failed" in reasons:
        return "rejected-overclaim"
    return "blocked"


def subject_text(*values: Any) -> str:
    parts: list[str] = []
    for value in values:
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value is not None:
            parts.append(str(value))
    return " ".join(parts).casefold()


def validate_sensitive_role(contract: dict[str, Any], text: str, approver_role: str, row_name: str) -> None:
    role_policy = require_dict(contract, "sensitive_role_policy", "Phase 27 contract")
    for role, tokens in role_policy.items():
        if not isinstance(role, str) or not isinstance(tokens, list):
            raise VerificationError("sensitive_role_policy must map role names to token lists")
        for token in tokens:
            if not isinstance(token, str):
                continue
            token_pattern = re.compile(rf"(?<![a-z0-9]){re.escape(token.casefold())}(?![a-z0-9])")
            if token_pattern.search(text) and approver_role != role:
                raise VerificationError(
                    f"{row_name} violates sensitive_role_policy: token {token!r} requires approver_role {role!r}"
                )


def normalize_exception(row: dict[str, Any], contract: dict[str, Any], row_name: str) -> dict[str, Any]:
    exception = row.get("exception")
    if not isinstance(exception, dict):
        raise VerificationError(f"{row_name} exception must be an object for exception decisions")
    normalized = dict(exception)
    required_fields = list(require_dict(contract, "exception_policy", "Phase 27 contract")["phase18_required_fields"])
    errors: list[str] = []
    for field in required_fields:
        try:
            if field == "evidence_refs":
                require_string_list(normalized, field, f"{row_name} exception")
            else:
                require_string(normalized, field, f"{row_name} exception")
        except VerificationError as error:
            errors.append(str(error))
    if not isinstance(normalized.get("residual_risk"), str) or not normalized["residual_risk"]:
        residual_risk = row.get("residual_risk")
        if isinstance(residual_risk, str) and residual_risk:
            normalized["residual_risk"] = residual_risk
        else:
            errors.append(f"{row_name} exception residual_risk must be a non-empty string")
    if not isinstance(normalized.get("owner"), str) or not normalized["owner"]:
        approver = normalized.get("approver") or row.get("approver")
        if isinstance(approver, str) and approver:
            normalized["owner"] = approver
        else:
            errors.append(f"{row_name} exception owner must be a non-empty string or default from approver")
    if errors:
        raise VerificationError("\n".join(errors))
    normalized["status"] = "approved-exception"
    return normalized


def validate_decision_common(row: dict[str, Any], row_name: str, require_status: bool = False) -> None:
    fields = ["decision", "approver", "approver_role", "decision_timestamp", "rationale", "residual_risk", "redaction_summary"]
    if require_status:
        fields.append("status")
    errors: list[str] = []
    for field in fields:
        try:
            require_string(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))
    try:
        require_string_list(row, "evidence_refs", row_name)
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def normalize_retained_decisions(
    phase18_contract: dict[str, Any],
    contract: dict[str, Any],
    maintainer_input: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    packets = phase18_retained_packets(phase18_contract)
    packet_by_id = {require_string(packet, "id", "Phase 18 retained packet"): packet for packet in packets}
    allowed_decisions = set(check_phase18_surfaces(phase18_contract)["review_decision_vocabulary"])
    allowed_hard_reasons = require_string_list(require_dict(contract, "hard_blocker_policy", "Phase 27 contract"), "reasons", "hard blocker policy")
    if maintainer_input is None:
        return [
            {
                "packet_id": packet_id,
                "title": packet.get("title", ""),
                "status": "pending-maintainer-review",
                "decision": "pending",
                "evidence_state": str(packet.get("status", "pending-evidence")),
                "maintainer_decision": "pending",
                "exception_state": "none",
                "residual_risk_state": "unreviewed",
                "hard_failure_state": "none",
                "hard_failure_reasons": [],
                "demotion_authorization": "blocked",
                "residual_risk": packet.get("residual_risk", ""),
                "evidence_refs": packet.get("required_evidence_refs", []),
                "source_packet": packet,
            }
            for packet_id, packet in packet_by_id.items()
        ]

    rows = maintainer_input.get("retained_code_decisions")
    if not isinstance(rows, list):
        raise VerificationError("maintainer input must contain retained_code_decisions list")
    parsed: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"retained_code_decisions[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        try:
            packet_id = require_string(row, "packet_id", row_name)
            if packet_id not in packet_by_id:
                raise VerificationError(f"{row_name} uses unknown packet_id: {packet_id}")
            if packet_id in parsed:
                raise VerificationError(f"{row_name} duplicates packet_id: {packet_id}")
            decision = require_string(row, "decision", row_name)
            if decision not in allowed_decisions:
                raise VerificationError(f"{row_name} decision is invalid: {decision}")
            validate_decision_common(row, row_name)
            packet = packet_by_id[packet_id]
            maybe_exception = row.get("exception")
            exception_surface = maybe_exception.get("affected_printer_or_release_surface") if isinstance(maybe_exception, dict) else ""
            validate_sensitive_role(
                contract,
                subject_text(packet_id, packet.get("title"), packet.get("taxonomy_tags"), exception_surface),
                require_string(row, "approver_role", row_name),
                row_name,
            )
            hard_reasons = detect_hard_failure_reasons(row, allowed_hard_reasons, row_name)
            maybe_exception = normalize_exception(row, contract, row_name) if decision == "exception" and not hard_reasons else {"status": "none"}
            if hard_reasons:
                status = status_for_hard_failure(hard_reasons)
                maintainer_decision = "blocked-by-hard-failure"
                exception_state = "blocked-by-hard-failure"
                residual_risk_state = "blocked"
                hard_failure_state = "blocked"
            elif decision == "approve":
                status = "accepted"
                maintainer_decision = "accepted"
                exception_state = "none"
                residual_risk_state = "accepted-with-risk"
                hard_failure_state = "none"
            elif decision == "reject":
                status = "rejected"
                maintainer_decision = "rejected"
                exception_state = "none"
                residual_risk_state = "rejected"
                hard_failure_state = "none"
            else:
                status = "deferred-approved-exception"
                maintainer_decision = "deferred-approved-exception"
                exception_state = "approved-exception"
                residual_risk_state = "owner-assigned"
                hard_failure_state = "none"
            parsed[packet_id] = {
                "packet_id": packet_id,
                "title": packet.get("title", ""),
                "status": status,
                "decision": decision,
                "approver": row["approver"],
                "approver_role": row["approver_role"],
                "decision_timestamp": row["decision_timestamp"],
                "rationale": row["rationale"],
                "evidence_refs": row["evidence_refs"],
                "redaction_summary": row["redaction_summary"],
                "evidence_state": "linked",
                "maintainer_decision": maintainer_decision,
                "exception_state": exception_state,
                "residual_risk_state": residual_risk_state,
                "hard_failure_state": hard_failure_state,
                "hard_failure_reasons": hard_reasons,
                "demotion_authorization": "blocked",
                "residual_risk": row["residual_risk"],
                "exception": maybe_exception,
                "source_packet": packet,
            }
        except VerificationError as error:
            errors.append(str(error))
    missing = [packet_id for packet_id in packet_by_id if packet_id not in parsed]
    if missing:
        errors.append("maintainer input missing retained packet decisions: " + ", ".join(missing))
    if errors:
        raise VerificationError("\n".join(errors))
    return [parsed[packet_id] for packet_id in packet_by_id]


def phase26_rows_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {require_string(row, "criterion_id", "Phase 26 row"): row for row in rows}


def normalize_default_final_decisions(
    phase18_contract: dict[str, Any],
    phase26_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    upstream_by_id = phase26_rows_by_id(phase26_rows)
    final_rows: list[dict[str, Any]] = []
    for requirement in phase18_upstream_requirements(phase18_contract):
        criterion_id = require_string(requirement, "criterion_id", "Phase 18 upstream requirement")
        upstream_row = upstream_by_id[criterion_id]
        status = str(upstream_row.get("status", "blocked"))
        if criterion_id in {"final-retained-code-acceptance", "final-maintainer-decision", "final-reference-demotion-allowed"}:
            status = "blocked" if criterion_id != "final-maintainer-decision" else "pending"
        final_rows.append(
            {
                "decision_id": f"phase27-final-readiness-{criterion_id}",
                "criterion_id": criterion_id,
                "decision": "pending",
                "status": status,
                "approver": "",
                "approver_role": "",
                "decision_timestamp": "",
                "rationale": upstream_row.get("failure_reason", "Pending maintainer final readiness decision."),
                "evidence_refs": upstream_row.get("evidence_refs", []),
                "artifact_refs": upstream_row.get("artifact_refs", []),
                "residual_risk": "Pending Phase 27 maintainer decision input.",
                "exception": {"status": "none"},
                "redaction_summary": f"redaction_status={upstream_row.get('redaction_status', 'unknown')}",
                "evidence_state": status,
                "maintainer_decision": "pending",
                "exception_state": "none",
                "residual_risk_state": "unreviewed",
                "hard_failure_state": "none",
                "hard_failure_reasons": [],
                "demotion_authorization": "blocked",
            }
        )
    return final_rows


def normalize_final_decisions(
    phase18_contract: dict[str, Any],
    contract: dict[str, Any],
    phase26_rows: list[dict[str, Any]],
    maintainer_input: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if maintainer_input is None:
        return normalize_default_final_decisions(phase18_contract, phase26_rows)
    surfaces = check_phase18_surfaces(phase18_contract)
    requirements = phase18_upstream_requirements(phase18_contract)
    requirement_by_id = {require_string(requirement, "criterion_id", "Phase 18 upstream requirement"): requirement for requirement in requirements}
    upstream_by_id = phase26_rows_by_id(phase26_rows)
    allowed_decisions = set(surfaces["review_decision_vocabulary"])
    allowed_statuses = set(surfaces["final_criterion_status_vocabulary"])
    allowed_hard_reasons = require_string_list(require_dict(contract, "hard_blocker_policy", "Phase 27 contract"), "reasons", "hard blocker policy")
    rows = maintainer_input.get("final_readiness_decisions")
    if not isinstance(rows, list):
        raise VerificationError("maintainer input must contain final_readiness_decisions list")
    parsed: dict[str, dict[str, Any]] = {}
    decision_ids: set[str] = set()
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"final_readiness_decisions[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        try:
            missing = [field for field in surfaces["final_decision_required_fields"] if field not in row]
            if missing:
                raise VerificationError(f"{row_name} missing required final decision fields: {', '.join(missing)}")
            criterion_id = require_string(row, "criterion_id", row_name)
            decision_id = require_string(row, "decision_id", row_name)
            if decision_id in decision_ids:
                raise VerificationError(f"{row_name} duplicate decision_id: {decision_id}")
            decision_ids.add(decision_id)
            if criterion_id not in requirement_by_id:
                raise VerificationError(f"{row_name} uses unknown criterion_id: {criterion_id}")
            if criterion_id in parsed:
                raise VerificationError(f"{row_name} duplicates criterion_id: {criterion_id}")
            decision = require_string(row, "decision", row_name)
            status = require_string(row, "status", row_name)
            if decision not in allowed_decisions:
                raise VerificationError(f"{row_name} decision is invalid: {decision}")
            if status not in allowed_statuses:
                raise VerificationError(f"{row_name} status is invalid: {status}")
            if criterion_id == "final-reference-demotion-allowed" and (decision == "approve" or status in {"passed", "exception-approved"}):
                raise VerificationError(f"{row_name} cannot approve reference demotion in Phase 27")
            validate_decision_common(row, row_name, require_status=True)
            validate_sensitive_role(
                contract,
                subject_text(criterion_id, requirement_by_id[criterion_id].get("evidence_family"), row.get("rationale")),
                require_string(row, "approver_role", row_name),
                row_name,
            )
            upstream_row = upstream_by_id[criterion_id]
            hard_reasons = detect_hard_failure_reasons(upstream_row, allowed_hard_reasons, row_name)
            hard_reasons.extend(reason for reason in detect_hard_failure_reasons(row, allowed_hard_reasons, row_name) if reason not in hard_reasons)
            maybe_exception = normalize_exception(row, contract, row_name) if decision == "exception" and not hard_reasons else {"status": "none"}
            if hard_reasons:
                normalized_status = status_for_hard_failure(hard_reasons)
                maintainer_decision = "blocked-by-hard-failure"
                exception_state = "blocked-by-hard-failure"
                residual_risk_state = "blocked"
                hard_failure_state = "blocked"
            elif decision == "approve":
                normalized_status = status
                maintainer_decision = "accepted"
                exception_state = "none"
                residual_risk_state = "accepted-with-risk"
                hard_failure_state = "none"
            elif decision == "reject":
                normalized_status = status
                maintainer_decision = "rejected"
                exception_state = "none"
                residual_risk_state = "rejected"
                hard_failure_state = "none"
            else:
                normalized_status = "exception-approved"
                maintainer_decision = "deferred-approved-exception"
                exception_state = "approved-exception"
                residual_risk_state = "owner-assigned"
                hard_failure_state = "none"
            parsed[criterion_id] = {
                "decision_id": decision_id,
                "criterion_id": criterion_id,
                "decision": decision,
                "status": normalized_status,
                "approver": row["approver"],
                "approver_role": row["approver_role"],
                "decision_timestamp": row["decision_timestamp"],
                "rationale": row["rationale"],
                "evidence_refs": row["evidence_refs"],
                "artifact_refs": upstream_row.get("artifact_refs", []),
                "residual_risk": row["residual_risk"],
                "exception": maybe_exception,
                "redaction_summary": row["redaction_summary"],
                "evidence_state": str(upstream_row.get("status", "unknown")),
                "maintainer_decision": maintainer_decision,
                "exception_state": exception_state,
                "residual_risk_state": residual_risk_state,
                "hard_failure_state": hard_failure_state,
                "hard_failure_reasons": hard_reasons,
                "demotion_authorization": "blocked",
            }
        except VerificationError as error:
            errors.append(str(error))
    missing = [criterion_id for criterion_id in requirement_by_id if criterion_id not in parsed]
    if missing:
        errors.append("maintainer input missing final readiness decisions: " + ", ".join(missing))
    if errors:
        raise VerificationError("\n".join(errors))
    return [parsed[criterion_id] for criterion_id in requirement_by_id]


def build_decision_rows(retained_rows: list[dict[str, Any]], final_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in retained_rows:
        rows.append(
            {
                "row_type": "retained_code_decision",
                "row_id": row["packet_id"],
                "status": row["status"],
                "decision": row["decision"],
                "maintainer_decision": row["maintainer_decision"],
                "hard_failure_state": row["hard_failure_state"],
                "demotion_authorization": "blocked",
            }
        )
    for row in final_rows:
        rows.append(
            {
                "row_type": "final_readiness_decision",
                "row_id": row["criterion_id"],
                "decision_id": row["decision_id"],
                "status": row["status"],
                "decision": row["decision"],
                "maintainer_decision": row["maintainer_decision"],
                "hard_failure_state": row["hard_failure_state"],
                "demotion_authorization": "blocked",
            }
        )
    return rows


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return counts


def write_contract_snapshots(root: Path, output_dir: Path, phase26_rows_path: Path) -> None:
    snapshots_dir = root / output_dir / "contract-snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / PHASE18_CONTRACT, snapshots_dir / PHASE18_CONTRACT.name)
    shutil.copy2(root / PHASE26_CONTRACT, snapshots_dir / PHASE26_CONTRACT.name)
    shutil.copy2(root / phase26_rows_path, snapshots_dir / "phase26-upstream-result-row-table.json")


def write_phase27_outputs(root: Path, output_dir: Path, maybe_maintainer_input: str | None, phase26_rows_arg: str) -> None:
    checked = check_contract(root)
    contract = checked["contract"]
    phase18_contract = checked["phase18_contract"]
    phase26_contract = checked["phase26_contract"]
    phase26_rows_path = repo_relative_path(phase26_rows_arg, "--phase26-upstream-rows")
    relative_output_dir = reset_output_root(root, output_dir)
    phase26_rows = load_phase26_upstream_rows(root, phase26_rows_path, phase18_contract, phase26_contract)
    maintainer_input = load_maintainer_input(root, maybe_maintainer_input)
    retained_rows = normalize_retained_decisions(phase18_contract, contract, maintainer_input)
    final_rows = normalize_final_decisions(phase18_contract, contract, phase26_rows, maintainer_input)
    decision_rows = build_decision_rows(retained_rows, final_rows)
    generated_at = utc_now()
    source_refs = source_contract_refs(contract)
    template = maintainer_input_template(phase18_contract, contract)
    handoff_policy = require_dict(contract, "phase28_handoff_policy", "Phase 27 contract")
    exception_rows = [
        {
            "row_type": "retained_code_decision" if "packet_id" in row else "final_readiness_decision",
            "row_id": row.get("packet_id", row.get("criterion_id")),
            "exception": row["exception"],
            "residual_risk": row["residual_risk"],
            "owner": row["exception"].get("owner", row.get("approver", "")) if isinstance(row.get("exception"), dict) else "",
        }
        for row in [*retained_rows, *final_rows]
        if isinstance(row.get("exception"), dict) and row["exception"].get("status") != "none"
    ]
    risk_rows = [
        {
            "row_type": "retained_code_decision" if "packet_id" in row else "final_readiness_decision",
            "row_id": row.get("packet_id", row.get("criterion_id")),
            "residual_risk": row["residual_risk"],
            "residual_risk_state": row["residual_risk_state"],
            "owner": row.get("approver", row.get("source_packet", {}).get("owner", "")),
        }
        for row in [*retained_rows, *final_rows]
    ]
    artifact_refs = [
        {
            "path": (relative_output_dir / artifact).as_posix(),
            "purpose": "phase27-retained-code-acceptance-decision-evidence",
        }
        for artifact in GENERATED_ARTIFACTS
    ]
    write_json(
        root,
        relative_output_dir / "acceptance-run-manifest.json",
        {
            "artifact_name": "phase27-retained-code-acceptance-decisions",
            "generated_at_utc": generated_at,
            "generated_artifacts": GENERATED_ARTIFACTS,
            "maintainer_input_supplied": maintainer_input is not None,
            "output_root": relative_output_dir.as_posix(),
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "retained_decision_count": len(retained_rows),
            "final_readiness_decision_count": len(final_rows),
            "source_contract_refs": source_refs,
        },
    )
    write_json(root, relative_output_dir / "normalized-retained-code-decisions.json", {"rows": retained_rows})
    write_json(root, relative_output_dir / "residual-risk-register.json", {"rows": risk_rows})
    write_json(root, relative_output_dir / "exception-decision-register.json", {"rows": exception_rows})
    write_json(
        root,
        relative_output_dir / "final-readiness-decision-summary.json",
        {
            "rows": final_rows,
            "status_counts": status_counts(final_rows),
            "phase27_may_authorize_demotion": False,
            "demotion_authorization": "blocked",
        },
    )
    write_json(
        root,
        relative_output_dir / "phase28-handoff-manifest.json",
        {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "demotion_authorization": handoff_policy["demotion_authorization"],
            "phase27_may_authorize_demotion": handoff_policy["phase27_may_authorize_demotion"],
            "phase28_required_decision": handoff_policy["phase28_required_decision"],
            "blocked_criteria": ["final-reference-demotion-allowed"],
        },
    )
    write_json(root, relative_output_dir / "decision-row-table.json", {"rows": decision_rows})
    write_json(root, relative_output_dir / "maintainer-acceptance-input-template.json", template)
    write_json(
        root,
        relative_output_dir / "artifact-reference-summary.json",
        {
            "artifact_refs": artifact_refs,
            "source_contract_refs": source_refs,
            "phase26_upstream_rows": phase26_rows_path.as_posix(),
        },
    )
    write_contract_snapshots(root, relative_output_dir, phase26_rows_path)
    run_security_scan(root, maybe_maintainer_input, relative_output_dir)


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
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase27_retained_code_acceptance_decisions_docs"',
                'name = "phase27_verify"',
                'actual = "//tools/bazel:phase27_verify"',
                'name = "phase27_verify_tests"',
                'actual = "//tools/bazel:phase27_verify_tests"',
                *[f'"{doc}"' for doc in PHASE27_DOCS],
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase27_source_ref_manifests"',
                'name = "phase27_verify"',
                'name = "phase27_verify_tests"',
                "phase27_retained_code_acceptance_decisions.py",
                "phase27_retained_code_acceptance_decisions_test.py",
                "phase27_retained_code_acceptance_decisions_contract.json",
                "phase26_release_signing_upstream_evidence.py",
                "//:phase27_retained_code_acceptance_decisions_docs",
                *[f'"{manifest}"' for manifest in PHASE27_SOURCE_REF_MANIFESTS],
            ],
        )
    )
    try:
        workflow_text = read_text(root, Path("tools/bazel/rust_workflow.sh"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        verify_commands = shell_case_commands(workflow_text, "phase27_verify")
        test_commands = shell_case_commands(workflow_text, "phase27_verify_tests")
        if verify_commands is None:
            errors.append("tools/bazel/rust_workflow.sh phase27_verify case arm missing")
        else:
            errors.extend(missing_required_items("tools/bazel/rust_workflow.sh phase27_verify case arm", verify_commands, PHASE27_VERIFY_COMMANDS))
            errors.extend(
                check_command_order(
                    "tools/bazel/rust_workflow.sh phase27_verify case arm",
                    verify_commands,
                    PHASE27_VERIFY_COMMANDS[0],
                    PHASE27_VERIFY_COMMANDS[1],
                    "must run --wiring-only before Phase 26 generation",
                )
            )
            errors.extend(
                check_command_order(
                    "tools/bazel/rust_workflow.sh phase27_verify case arm",
                    verify_commands,
                    PHASE27_VERIFY_COMMANDS[1],
                    PHASE27_VERIFY_COMMANDS[2],
                    "must run Phase 26 quick before Phase 27 quick",
                )
            )
        if test_commands is None:
            errors.append("tools/bazel/rust_workflow.sh phase27_verify_tests case arm missing")
        else:
            errors.extend(missing_required_items("tools/bazel/rust_workflow.sh phase27_verify_tests case arm", test_commands, [PHASE27_TEST_COMMAND]))
    try:
        just_text = read_text(root, Path("justfile"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        just_commands = just_recipe_commands(just_text, "phase27-verify")
        test_line = "bazel run //tools/bazel:phase27_verify_tests"
        verify_line = "bazel run //tools/bazel:phase27_verify"
        if just_commands is None:
            errors.append("justfile phase27-verify recipe missing")
        else:
            errors.extend(missing_required_items("justfile phase27-verify recipe", just_commands, [test_line, verify_line]))
            errors.extend(
                check_command_order(
                    "justfile phase27-verify recipe",
                    just_commands,
                    test_line,
                    verify_line,
                    "must run tests before verifier",
                )
            )
    if errors:
        raise VerificationError("\n".join(errors))


def run_security_scan(root: Path, maybe_maintainer_input: str | None = None, maybe_output_dir: Path | None = None) -> None:
    errors: list[str] = []
    paths = [CONTRACT_MANIFEST]
    if maybe_maintainer_input is not None:
        paths.append(repo_relative_path(maybe_maintainer_input, "--maintainer-input"))
    output_dir = maybe_output_dir if maybe_output_dir is not None else DEFAULT_OUTPUT_DIR
    if (root / output_dir).exists():
        paths.extend(output_dir / artifact for artifact in GENERATED_ARTIFACTS if (root / output_dir / artifact).exists())
    for path in paths:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_field_names(json.loads(text), path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase 27 retained-code acceptance decisions.")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 27 contract against Phase 18")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 27 contract and retained outputs")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel, workflow, and just wiring")
    parser.add_argument("--quick", action="store_true", help="write retained Phase 27 outputs")
    parser.add_argument("--maintainer-input", help="optional Phase 27 maintainer decision input JSON")
    parser.add_argument("--phase26-upstream-rows", default=PHASE26_UPSTREAM_ROWS.as_posix(), help="Phase 26 upstream result row table")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 27 output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        check_contract(ROOT)
        if args.security_only:
            run_security_scan(ROOT)
            print("Phase 27 retained-code acceptance decisions security scan passed")
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            print("Phase 27 retained-code acceptance decisions wiring passed")
            return 0
        if args.quick:
            run_security_scan(ROOT, args.maintainer_input)
            write_phase27_outputs(ROOT, Path(args.output_dir), args.maintainer_input, args.phase26_upstream_rows)
            print("Phase 27 retained-code acceptance decisions quick validation passed")
            return 0
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    print("Phase 27 retained-code acceptance decisions contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
