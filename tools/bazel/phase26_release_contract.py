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
PHASE = "26-release-signing-and-upstream-result-evidence"
PHASE_LIFECYCLE_ID = "26-2026-06-24T13-36-46"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
)
PHASE17_CONTRACT = Path(
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json")
PHASE18_CONTRACT = Path(
    "tools/bazel/manifests/phase18_cutover_review_contract.json")
PHASE20_CONTRACT = Path(
    "tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json")
PHASE20_RELEASE_INPUT_TEMPLATE = Path(
    "tools/bazel/manifests/phase20_release_environment_inputs.template.json")
PHASE23_CONTRACT = Path(
    "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json")
PHASE24_CONTRACT = Path(
    "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json"
)
PHASE25_CONTRACT = Path(
    "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json"
)
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase26")
UPSTREAM_RESULT_ROW_FIELDS = [
    "criterion_id",
    "evidence_family",
    "requirement_ids",
    "source_requirement_ids",
    "owning_phase",
    "source_lifecycle_id",
    "source_lifecycle_status",
    "evidence_refs",
    "artifact_refs",
    "status",
    "failure_reason",
    "redaction_status",
    "source_ref_status",
    "exception_status",
    "maintainer_state",
    "generated_at_utc",
]
CANONICAL_PHASE18_CRITERIA = [
    "final-ci-evidence",
    "final-simulator-evidence",
    "final-hardware-safety-media-evidence",
    "final-live-network-transfer-evidence",
    "final-release-artifact-signing-evidence",
    "final-retained-code-acceptance",
    "final-residual-risk-review",
    "final-maintainer-decision",
    "final-reference-demotion-allowed",
]
GENERATED_ARTIFACTS = [
    "release-upstream-run-manifest.json",
    "normalized-release-evidence-summary.json",
    "upstream-result-row-table.json",
    "upstream-result-manifest.json",
    "redaction-provenance-summary.json",
    "artifact-reference-summary.json",
    "operator-release-input-template.json",
    "contract-snapshots/phase17_release_candidate_evidence_contract.json",
    "contract-snapshots/phase18_cutover_review_contract.json",
    "contract-snapshots/phase20_release_candidate_artifacts_contract.json",
    "contract-snapshots/phase20_release_environment_inputs.template.json",
]
SNAPSHOT_CONTRACTS = [
    PHASE17_CONTRACT, PHASE18_CONTRACT, PHASE20_CONTRACT,
    PHASE20_RELEASE_INPUT_TEMPLATE
]
UPSTREAM_ROW_INPUTS = [
    {
        "flag": "--phase23-simulator-row",
        "arg_name": "phase23_simulator_row",
        "source_contract": PHASE23_CONTRACT.as_posix(),
        "source_phase": "23-simulator-evidence-execution",
        "source_criterion_id": "final-simulator-evidence",
        "canonical_criterion_id": "final-simulator-evidence",
        "producer_requirement_ids": ["EVID-01"],
        "input_root": "build/ci-evidence/phase23/",
        "external_root": "external://phase23/",
    },
    {
        "flag": "--phase24-hardware-media-safety-row",
        "arg_name": "phase24_hardware_media_safety_row",
        "source_contract": PHASE24_CONTRACT.as_posix(),
        "source_phase": "24-hardware-media-and-safety-evidence-execution",
        "source_criterion_id": "final-hardware-safety-media-evidence",
        "canonical_criterion_id": "final-hardware-safety-media-evidence",
        "producer_requirement_ids": ["EVID-02"],
        "input_root": "build/ci-evidence/phase24/",
        "external_root": "external://phase24/",
    },
    {
        "flag": "--phase25-live-service-row",
        "arg_name": "phase25_live_service_row",
        "source_contract": PHASE25_CONTRACT.as_posix(),
        "source_phase": "25-live-service-evidence-execution",
        "source_criterion_id": "final-live-service-evidence",
        "canonical_criterion_id": "final-live-network-transfer-evidence",
        "producer_requirement_ids": ["EVID-03"],
        "input_root": "build/ci-evidence/phase25/",
        "external_root": "external://phase25/",
    },
]
PHASE26_DOCS = [
    ".planning/phases/26-release-signing-and-upstream-result-evidence/26-CONTEXT.md",
    ".planning/phases/26-release-signing-and-upstream-result-evidence/26-RESEARCH.md",
    ".planning/phases/26-release-signing-and-upstream-result-evidence/26-VALIDATION.md",
    ".planning/phases/26-release-signing-and-upstream-result-evidence/26-01-PLAN.md",
]
PHASE26_SOURCE_REF_MANIFESTS = [
    "manifests/phase17_release_candidate_evidence_contract.json",
    "manifests/phase18_cutover_review_contract.json",
    "manifests/phase19_aggregate_ci_evidence_contract.json",
    "manifests/phase20_release_candidate_artifacts_contract.json",
    "manifests/phase20_release_environment_inputs.template.json",
    "manifests/phase23_simulator_evidence_execution_contract.json",
    "manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
    "manifests/phase25_live_service_evidence_execution_contract.json",
    "manifests/phase26_release_signing_upstream_evidence_contract.json",
]
PHASE26_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --wiring-only",
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26",
]
PHASE26_TEST_COMMAND = "python3 tools/bazel/phase26_release_signing_upstream_evidence_test.py"
PASS_CAPABLE_PROOF_CLASSES = {
    "approved-release-run", "external-release-key-evidence"
}
NON_PASS_PROOF_CLASSES = {
    "template-only",
    "local-smoke",
    "pending-release-input",
    "release-run-required",
    "external-signing-required",
    "blocked-signing-key-unavailable",
    "release-candidate",
}
REQUIRED_PASS_METADATA = [
    "release_run_id",
    "artifact_refs",
    "operator",
    "timestamp",
    "subject_digests",
    "build_input_identity",
    "retention_refs",
    "verification_outcome",
    "mismatch_class",
    "mismatch_reason",
    "owner_phase",
    "affected_artifact_surface",
    "residual_risk",
]
REQUIRED_SIGNING_METADATA = ["key_identity_ref", "signing_mode"]
PHASE20_REQUIRED_METADATA_GROUPS = [
    "release_metadata_required",
    "signing_metadata_required",
    "provenance_metadata_required",
    "retention_metadata_required",
]
PHASE20_OPTIONAL_METADATA_GROUPS = [
    "comparison_metadata_required",
]
DIGEST_FIELDS = {"artifact_ref", "sha256"}
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
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-block",
     re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
    (
        "forbidden-release-evidence-marker",
        re.compile(
            r"\b(private[_-]?key|private[_-]?certificate|raw[_-]?key[_-]?bytes|signing[_-]?key[_-]?value|"
            r"signing[_-]?payload[_-]?bytes|raw[_-]?firmware[_-]?payload|firmware[_-]?payload[_-]?bytes|"
            r"raw[_-]?logs?|binary[_-]?dump|token[_-]?value|password[_-]?value|credential[_-]?value|secret[_-]?value)\b",
            re.IGNORECASE,
        ),
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


def require_non_empty_list(row: dict[str, Any], field: str,
                           row_name: str) -> list[Any]:
    values = require_list(row, field, row_name)
    if not values:
        raise VerificationError(f"{row_name} {field} must be non-empty")
    return values


def normalized_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", field_name.casefold())


FORBIDDEN_NORMALIZED_FIELD_NAMES = {
    normalized_field_name(field_name)
    for field_name in FORBIDDEN_FIELD_NAMES
}


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            marker = match.group(0) if match.group(0) else label
            errors.append(
                f"{path.as_posix()} contains forbidden release evidence marker: {marker}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(
            key for key in value
            if normalized_field_name(key) in FORBIDDEN_NORMALIZED_FIELD_NAMES)
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


def contract_rows(contract: dict[str, Any],
                  path: Path) -> list[dict[str, Any]]:
    rows = contract.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{path.as_posix()} must contain a rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(
                f"{path.as_posix()} rows[{index}] must be an object")
        parsed_rows.append(row)
    return parsed_rows


def phase20_release_row_ids(phase20_contract: dict[str, Any]) -> list[str]:
    row_ids: list[str] = []
    for row in contract_rows(phase20_contract, PHASE20_CONTRACT):
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise VerificationError(
                f"{PHASE20_CONTRACT.as_posix()} contains a release row without an id"
            )
        row_ids.append(row_id)
    return row_ids


def phase20_status_vocabulary(phase20_contract: dict[str, Any]) -> set[str]:
    values = phase20_contract.get("status_vocabulary")
    if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values):
        raise VerificationError(
            f"{PHASE20_CONTRACT.as_posix()} status_vocabulary must contain strings"
        )
    return set(values)


def phase20_proof_class_vocabulary(
        phase20_contract: dict[str, Any]) -> set[str]:
    values = phase20_contract.get("proof_class_vocabulary")
    if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values):
        raise VerificationError(
            f"{PHASE20_CONTRACT.as_posix()} proof_class_vocabulary must contain strings"
        )
    return set(values)


def phase18_upstream_requirements(
        phase18_contract: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = phase18_contract.get("upstream_result_requirements")
    if not isinstance(requirements, list):
        raise VerificationError(
            f"{PHASE18_CONTRACT.as_posix()} must contain upstream_result_requirements"
        )
    parsed: list[dict[str, Any]] = []
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            raise VerificationError(
                f"{PHASE18_CONTRACT.as_posix()} upstream_result_requirements[{index}] must be an object"
            )
        parsed.append(requirement)
    return parsed


def phase18_upstream_status_vocabulary(
        phase18_contract: dict[str, Any]) -> set[str]:
    values = phase18_contract.get("upstream_result_status_vocabulary")
    if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values):
        raise VerificationError(
            f"{PHASE18_CONTRACT.as_posix()} upstream_result_status_vocabulary must contain strings"
        )
    return set(values)


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    reject_forbidden_field_names(contract, CONTRACT_MANIFEST.as_posix())
    phase20_contract = load_json(root, PHASE20_CONTRACT)
    phase18_contract = load_json(root, PHASE18_CONTRACT)
    phase20_row_ids = phase20_release_row_ids(phase20_contract)
    phase18_criteria = [
        str(row.get("criterion_id"))
        for row in phase18_upstream_requirements(phase18_contract)
    ]
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase26_release_signing_upstream_evidence_contract",
        "artifact_name": "phase26-release-signing-upstream-evidence",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    source_contracts = contract.get("source_contracts")
    if not isinstance(source_contracts, list):
        errors.append(
            f"{CONTRACT_MANIFEST.as_posix()} source_contracts must be a list")
    else:
        source_paths = set()
        for index, source_contract in enumerate(source_contracts):
            if not isinstance(source_contract, dict):
                errors.append(f"source_contracts[{index}] must be an object")
                continue
            source_path = source_contract.get("path")
            if not isinstance(source_path, str) or not source_path:
                errors.append(
                    f"source_contracts[{index}] path must be a non-empty string"
                )
                continue
            relative_path = Path(source_path)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                errors.append(
                    f"source_contracts[{index}] path must be repo-relative: {source_path}"
                )
                continue
            if not (root / relative_path).exists():
                errors.append(
                    f"source_contracts[{index}] path does not exist: {source_path}"
                )
            source_paths.add(source_path)
        for descriptor in UPSTREAM_ROW_INPUTS:
            source_contract = str(descriptor["source_contract"])
            if source_contract not in source_paths:
                errors.append(
                    f"source_contracts must include upstream row source contract: {source_contract}"
                )
    release_policy = contract.get("release_policy")
    if not isinstance(release_policy, dict):
        errors.append(
            f"{CONTRACT_MANIFEST.as_posix()} release_policy must be an object")
    else:
        if release_policy.get(
                "canonical_phase20_release_row_ids") != phase20_row_ids:
            errors.append(
                "release_policy canonical_phase20_release_row_ids must match Phase 20 rows exactly"
            )
        if set(release_policy.get("pass_capable_proof_classes",
                                  [])) != PASS_CAPABLE_PROOF_CLASSES:
            errors.append(
                "release_policy pass_capable_proof_classes must be Phase 26 pass-capable classes"
            )
        non_pass = set(release_policy.get("non_pass_proof_classes", []))
        for proof_class in NON_PASS_PROOF_CLASSES:
            if proof_class not in non_pass:
                errors.append(
                    f"release_policy non_pass_proof_classes missing {proof_class}"
                )
        if release_policy.get(
                "required_pass_metadata") != REQUIRED_PASS_METADATA:
            errors.append(
                "release_policy required_pass_metadata must match Phase 26 pass metadata"
            )
        if release_policy.get(
                "required_signing_metadata_when_phase20_requires_signing"
        ) != REQUIRED_SIGNING_METADATA:
            errors.append(
                "release_policy required signing metadata must require key_identity_ref and signing_mode"
            )
    upstream_policy = contract.get("upstream_policy")
    if not isinstance(upstream_policy, dict):
        errors.append(
            f"{CONTRACT_MANIFEST.as_posix()} upstream_policy must be an object"
        )
    else:
        if upstream_policy.get(
                "phase18_contract") != PHASE18_CONTRACT.as_posix():
            errors.append(
                "upstream_policy phase18_contract must name the Phase 18 contract"
            )
        if upstream_policy.get(
                "canonical_phase18_criteria") != phase18_criteria:
            errors.append(
                "upstream_policy canonical_phase18_criteria must match Phase 18 upstream criteria exactly"
            )
        if upstream_policy.get(
                "row_required_fields") != UPSTREAM_RESULT_ROW_FIELDS:
            errors.append(
                "upstream_policy row_required_fields must match the Phase 26 upstream row schema"
            )
        if upstream_policy.get("release_requirement_ids") != [
                "EVID-04", "ACPT-01"
        ]:
            errors.append(
                "upstream_policy release_requirement_ids must be EVID-04 and ACPT-01"
            )
        if upstream_policy.get("default_requirement_ids") != ["ACPT-01"]:
            errors.append(
                "upstream_policy default_requirement_ids must be ACPT-01")
        mappings = upstream_policy.get("compatibility_mappings")
        phase25_mapping = mappings.get(
            "phase25_compact_criterion_id") if isinstance(mappings,
                                                          dict) else None
        if not isinstance(phase25_mapping, dict) or phase25_mapping.get(
                "to") != "final-live-network-transfer-evidence":
            errors.append(
                "upstream_policy must map Phase 25 compact live-service rows to the Phase 18 live-network criterion"
            )
        if upstream_policy.get("upstream_row_inputs") != UPSTREAM_ROW_INPUTS:
            errors.append(
                "upstream_policy upstream_row_inputs must declare Phase 23, Phase 24, and Phase 25 input rows exactly"
            )
    if contract.get("generated_artifacts") != GENERATED_ARTIFACTS:
        errors.append(
            "generated_artifacts must list the Phase 26 retained output files exactly"
        )
    if errors:
        raise VerificationError("\n".join(errors))
    return contract
