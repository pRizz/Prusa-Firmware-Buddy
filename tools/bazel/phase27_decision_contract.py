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
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
)
PHASE18_CONTRACT = Path(
    "tools/bazel/manifests/phase18_cutover_review_contract.json")
PHASE26_CONTRACT = Path(
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
)
PHASE11_RETAINED_CODE = Path(
    "tools/bazel/manifests/phase11_retained_code_justifications.json")
FOREIGN_CODE_INVENTORY = Path(
    "tools/bazel/manifests/foreign_code_inventory.json")
UNSAFE_BOUNDARY_AUDIT = Path(
    "tools/bazel/manifests/unsafe_boundary_audit.json")
PHASE11_CUTOVER_READINESS = Path(
    "tools/bazel/manifests/phase11_cutover_readiness.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase27")
PHASE26_UPSTREAM_ROWS = Path(
    "build/ci-evidence/phase26/upstream-result-row-table.json")
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
    ("python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick "
     "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
     "--output-dir build/ci-evidence/phase27"),
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
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("private-certificate-block",
     re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
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
    ("reference-demotion-approved",
     re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("demotion-allowed", re.compile(r"\bdemotion allowed\b", re.IGNORECASE)),
    ("final-readiness-approved",
     re.compile(r"\bfinal readiness approved\b", re.IGNORECASE)),
    (
        "evidence-alone-acceptance",
        re.compile(r"\bretained[- ]code accepted by evidence alone\b",
                   re.IGNORECASE),
    ),
)


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(root: Path, path: Path) -> str:
    full_path = root / path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read_text(root, path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(
            f"{path.as_posix()} must contain a top-level object")
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


def require_list(row: dict[str, Any], field: str, row_name: str) -> list[Any]:
    value = row.get(field)
    if not isinstance(value, list):
        raise VerificationError(f"{row_name} {field} must be a list")
    return value


def require_string_list(row: dict[str, Any], field: str,
                        row_name: str) -> list[str]:
    values = require_list(row, field, row_name)
    if not all(isinstance(value, str) and value for value in values):
        raise VerificationError(
            f"{row_name} {field} must contain non-empty strings")
    return values


def require_dict(row: dict[str, Any], field: str,
                 row_name: str) -> dict[str, Any]:
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
            errors.append(
                f"{path.as_posix()} contains forbidden marker {label}: {match.group(0)}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_field_names(value: Any, path: str) -> None:
    normalized_forbidden = {
        normalized_field_name(field_name)
        for field_name in FORBIDDEN_FIELD_NAMES
    }

    def walk(candidate: Any, candidate_path: str, errors: list[str]) -> None:
        if isinstance(candidate, dict):
            for key, child in candidate.items():
                child_path = f"{candidate_path}.{key}"
                if normalized_field_name(str(key)) in normalized_forbidden:
                    errors.append(
                        f"{path} contains forbidden field {key} at {child_path}"
                    )
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
        raise VerificationError(
            f"{option_name} must be repo-relative without parent traversal: {value}"
        )
    return path


def validate_output_dir(root: Path, output_dir: Path) -> tuple[Path, Path]:
    if output_dir.is_absolute() or ".." in output_dir.parts:
        raise VerificationError(
            f"--output-dir must be repo-relative under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        )
    try:
        output_dir.relative_to(DEFAULT_OUTPUT_DIR)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        ) from error
    current = root
    for part in output_dir.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(
                f"--output-dir contains a symlink escape risk: {output_dir.as_posix()}"
            )
    full_output_dir = (root / output_dir).resolve(strict=False)
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir must resolve under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        ) from error
    return output_dir, full_output_dir


def reset_output_root(root: Path, output_dir: Path) -> Path:
    relative_output_dir, full_output_dir = validate_output_dir(
        root, output_dir)
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


def phase18_retained_packets(
        phase18_contract: dict[str, Any]) -> list[dict[str, Any]]:
    packets = require_list(phase18_contract,
                           "retained_code_acceptance_packets",
                           "Phase 18 contract")
    parsed_packets: list[dict[str, Any]] = []
    for index, packet in enumerate(packets):
        if not isinstance(packet, dict):
            raise VerificationError(
                f"Phase 18 retained_code_acceptance_packets[{index}] must be an object"
            )
        require_string(packet, "id",
                       f"Phase 18 retained_code_acceptance_packets[{index}]")
        parsed_packets.append(packet)
    return parsed_packets


def phase18_upstream_requirements(
        phase18_contract: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = require_list(phase18_contract,
                                "upstream_result_requirements",
                                "Phase 18 contract")
    parsed_requirements: list[dict[str, Any]] = []
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            raise VerificationError(
                f"Phase 18 upstream_result_requirements[{index}] must be an object"
            )
        require_string(requirement, "criterion_id",
                       f"Phase 18 upstream_result_requirements[{index}]")
        parsed_requirements.append(requirement)
    return parsed_requirements


def phase18_upstream_criterion_ids(
        phase18_contract: dict[str, Any]) -> list[str]:
    requirements = phase18_upstream_requirements(phase18_contract)
    ids: list[str] = []
    for requirement in requirements:
        ids.append(
            require_string(requirement, "criterion_id",
                           "Phase 18 upstream requirement"))
    if len(ids) != len(set(ids)):
        raise VerificationError(
            "Phase 18 upstream criterion IDs must be unique")
    return ids


def phase18_hard_blocker_reasons(
        phase18_contract: dict[str, Any]) -> list[str]:
    requirements = phase18_upstream_requirements(phase18_contract)
    maybe_reasons: list[str] | None = None
    for index, requirement in enumerate(requirements):
        reasons = require_string_list(
            requirement, "hard_blocker_reasons",
            f"Phase 18 upstream_result_requirements[{index}]")
        if maybe_reasons is None:
            maybe_reasons = reasons
        elif reasons != maybe_reasons:
            raise VerificationError(
                "Phase 18 upstream hard blocker reasons must be consistent across criteria"
            )
    if maybe_reasons is None:
        raise VerificationError(
            "Phase 18 upstream_result_requirements must not be empty")
    return maybe_reasons


def check_phase18_surfaces(phase18_contract: dict[str, Any]) -> dict[str, Any]:
    retained_schema = require_dict(phase18_contract,
                                   "retained_code_acceptance_packet_schema",
                                   "Phase 18 contract")
    final_schema = require_dict(phase18_contract, "final_decision_schema",
                                "Phase 18 contract")
    exception_schema = require_dict(final_schema, "exception",
                                    "Phase 18 final_decision_schema")
    return {
        "retained_packet_ids":
        phase18_retained_packet_ids(phase18_contract),
        "upstream_criterion_ids":
        phase18_upstream_criterion_ids(phase18_contract),
        "retained_required_fields":
        require_string_list(retained_schema, "required_fields",
                            "Phase 18 retained packet schema"),
        "final_decision_required_fields":
        require_string_list(final_schema, "required_fields",
                            "Phase 18 final decision schema"),
        "exception_required_fields":
        require_string_list(exception_schema, "required_fields",
                            "Phase 18 exception schema"),
        "retained_packet_status_vocabulary":
        require_string_list(
            phase18_contract,
            "retained_packet_status_vocabulary",
            "Phase 18 contract",
        ),
        "final_criterion_status_vocabulary":
        require_string_list(
            phase18_contract,
            "final_criterion_status_vocabulary",
            "Phase 18 contract",
        ),
        "review_decision_vocabulary":
        require_string_list(
            phase18_contract,
            "review_decision_vocabulary",
            "Phase 18 contract",
        ),
        "hard_blocker_reasons":
        phase18_hard_blocker_reasons(phase18_contract),
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
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    source_contracts = require_list(contract, "source_contracts",
                                    "Phase 27 contract")
    source_paths = []
    for index, source_contract in enumerate(source_contracts):
        if not isinstance(source_contract, dict):
            errors.append(f"source_contracts[{index}] must be an object")
            continue
        source_path = source_contract.get("path")
        if not isinstance(source_path, str) or not source_path:
            errors.append(
                f"source_contracts[{index}] path must be a non-empty string")
            continue
        source_paths.append(Path(source_path))
        if Path(source_path).is_absolute() or ".." in Path(source_path).parts:
            errors.append(
                f"source_contracts[{index}] path must be repo-relative: {source_path}"
            )
        elif not (root / source_path).exists():
            errors.append(
                f"source_contracts[{index}] path does not exist: {source_path}"
            )
    if source_paths != SOURCE_CONTRACT_PATHS:
        errors.append(
            "source_contracts must list the exact Phase 27 source contracts in plan order"
        )
    canonical_policy = require_dict(contract, "canonical_policy",
                                    "Phase 27 contract")
    if canonical_policy.get("phase18_contract") != PHASE18_CONTRACT.as_posix():
        errors.append(
            "canonical_policy phase18_contract must point to the Phase 18 contract"
        )
    surfaces = check_phase18_surfaces(phase18_contract)
    if contract.get("decision_axes") != DECISION_AXES:
        errors.append(
            "decision_axes must exactly match the Phase 27 orthogonal axes")
    hard_blocker_policy = require_dict(contract, "hard_blocker_policy",
                                       "Phase 27 contract")
    if hard_blocker_policy.get("evaluate_before_exception") is not True:
        errors.append(
            "hard_blocker_policy evaluate_before_exception must be true")
    if hard_blocker_policy.get("reasons") != surfaces["hard_blocker_reasons"]:
        errors.append(
            "hard_blocker_policy reasons must match Phase 18 hard blocker reasons exactly"
        )
    exception_policy = require_dict(contract, "exception_policy",
                                    "Phase 27 contract")
    if exception_policy.get("phase18_required_fields"
                            ) != surfaces["exception_required_fields"]:
        errors.append(
            "exception_policy phase18_required_fields must match Phase 18 exception fields"
        )
    phase27_exception_fields = exception_policy.get("phase27_required_fields")
    if not isinstance(phase27_exception_fields, list):
        errors.append(
            "exception_policy phase27_required_fields must be a list")
    else:
        for field in [
                *surfaces["exception_required_fields"], "residual_risk",
                "owner"
        ]:
            if field not in phase27_exception_fields:
                errors.append(
                    f"exception_policy phase27_required_fields missing {field}"
                )
    handoff_policy = require_dict(contract, "phase28_handoff_policy",
                                  "Phase 27 contract")
    if handoff_policy.get("demotion_authorization") != "blocked":
        errors.append(
            "phase28_handoff_policy demotion_authorization must be blocked")
    if handoff_policy.get("phase27_may_authorize_demotion") is not False:
        errors.append(
            "phase28_handoff_policy phase27_may_authorize_demotion must be false"
        )
    generated_artifacts = require_string_list(contract, "generated_artifacts",
                                              "Phase 27 contract")
    if generated_artifacts != GENERATED_ARTIFACTS:
        errors.append(
            "generated_artifacts must list the Phase 27 retained output files exactly"
        )
    if errors:
        raise VerificationError("\n".join(errors))
    return {
        "contract": contract,
        "phase18_contract": phase18_contract,
        "phase26_contract": load_json(root, PHASE26_CONTRACT),
        "phase18_surfaces": surfaces,
    }
