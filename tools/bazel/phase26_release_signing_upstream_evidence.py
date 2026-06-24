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
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json")
PHASE17_CONTRACT = Path("tools/bazel/manifests/phase17_release_candidate_evidence_contract.json")
PHASE18_CONTRACT = Path("tools/bazel/manifests/phase18_cutover_review_contract.json")
PHASE20_CONTRACT = Path("tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json")
PHASE20_RELEASE_INPUT_TEMPLATE = Path("tools/bazel/manifests/phase20_release_environment_inputs.template.json")
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
SNAPSHOT_CONTRACTS = [PHASE17_CONTRACT, PHASE18_CONTRACT, PHASE20_CONTRACT, PHASE20_RELEASE_INPUT_TEMPLATE]
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
PASS_CAPABLE_PROOF_CLASSES = {"approved-release-run", "external-release-key-evidence"}
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
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-block", re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
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


def require_non_empty_list(row: dict[str, Any], field: str, row_name: str) -> list[Any]:
    values = require_list(row, field, row_name)
    if not values:
        raise VerificationError(f"{row_name} {field} must be non-empty")
    return values


def normalized_field_name(field_name: str) -> str:
    return field_name.replace("-", "_").casefold()


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            marker = match.group(0) if match.group(0) else label
            errors.append(f"{path.as_posix()} contains forbidden release evidence marker: {marker}")
    if errors:
        raise VerificationError("\n".join(errors))


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


def contract_rows(contract: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    rows = contract.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{path.as_posix()} must contain a rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{path.as_posix()} rows[{index}] must be an object")
        parsed_rows.append(row)
    return parsed_rows


def phase20_release_row_ids(phase20_contract: dict[str, Any]) -> list[str]:
    row_ids: list[str] = []
    for row in contract_rows(phase20_contract, PHASE20_CONTRACT):
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise VerificationError(f"{PHASE20_CONTRACT.as_posix()} contains a release row without an id")
        row_ids.append(row_id)
    return row_ids


def phase20_status_vocabulary(phase20_contract: dict[str, Any]) -> set[str]:
    values = phase20_contract.get("status_vocabulary")
    if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
        raise VerificationError(f"{PHASE20_CONTRACT.as_posix()} status_vocabulary must contain strings")
    return set(values)


def phase20_proof_class_vocabulary(phase20_contract: dict[str, Any]) -> set[str]:
    values = phase20_contract.get("proof_class_vocabulary")
    if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
        raise VerificationError(f"{PHASE20_CONTRACT.as_posix()} proof_class_vocabulary must contain strings")
    return set(values)


def phase18_upstream_requirements(phase18_contract: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = phase18_contract.get("upstream_result_requirements")
    if not isinstance(requirements, list):
        raise VerificationError(f"{PHASE18_CONTRACT.as_posix()} must contain upstream_result_requirements")
    parsed: list[dict[str, Any]] = []
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            raise VerificationError(f"{PHASE18_CONTRACT.as_posix()} upstream_result_requirements[{index}] must be an object")
        parsed.append(requirement)
    return parsed


def phase18_upstream_status_vocabulary(phase18_contract: dict[str, Any]) -> set[str]:
    values = phase18_contract.get("upstream_result_status_vocabulary")
    if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
        raise VerificationError(f"{PHASE18_CONTRACT.as_posix()} upstream_result_status_vocabulary must contain strings")
    return set(values)


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    reject_forbidden_field_names(contract, CONTRACT_MANIFEST.as_posix())
    phase20_contract = load_json(root, PHASE20_CONTRACT)
    phase18_contract = load_json(root, PHASE18_CONTRACT)
    phase20_row_ids = phase20_release_row_ids(phase20_contract)
    phase18_criteria = [str(row.get("criterion_id")) for row in phase18_upstream_requirements(phase18_contract)]
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
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    source_contracts = contract.get("source_contracts")
    if not isinstance(source_contracts, list):
        errors.append(f"{CONTRACT_MANIFEST.as_posix()} source_contracts must be a list")
    else:
        for index, source_contract in enumerate(source_contracts):
            if not isinstance(source_contract, dict):
                errors.append(f"source_contracts[{index}] must be an object")
                continue
            source_path = source_contract.get("path")
            if not isinstance(source_path, str) or not source_path:
                errors.append(f"source_contracts[{index}] path must be a non-empty string")
                continue
            relative_path = Path(source_path)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                errors.append(f"source_contracts[{index}] path must be repo-relative: {source_path}")
                continue
            if not (root / relative_path).exists():
                errors.append(f"source_contracts[{index}] path does not exist: {source_path}")
    release_policy = contract.get("release_policy")
    if not isinstance(release_policy, dict):
        errors.append(f"{CONTRACT_MANIFEST.as_posix()} release_policy must be an object")
    else:
        if release_policy.get("canonical_phase20_release_row_ids") != phase20_row_ids:
            errors.append("release_policy canonical_phase20_release_row_ids must match Phase 20 rows exactly")
        if set(release_policy.get("pass_capable_proof_classes", [])) != PASS_CAPABLE_PROOF_CLASSES:
            errors.append("release_policy pass_capable_proof_classes must be Phase 26 pass-capable classes")
        non_pass = set(release_policy.get("non_pass_proof_classes", []))
        for proof_class in NON_PASS_PROOF_CLASSES:
            if proof_class not in non_pass:
                errors.append(f"release_policy non_pass_proof_classes missing {proof_class}")
        if release_policy.get("required_pass_metadata") != REQUIRED_PASS_METADATA:
            errors.append("release_policy required_pass_metadata must match Phase 26 pass metadata")
        if release_policy.get("required_signing_metadata_when_phase20_requires_signing") != REQUIRED_SIGNING_METADATA:
            errors.append("release_policy required signing metadata must require key_identity_ref and signing_mode")
    upstream_policy = contract.get("upstream_policy")
    if not isinstance(upstream_policy, dict):
        errors.append(f"{CONTRACT_MANIFEST.as_posix()} upstream_policy must be an object")
    else:
        if upstream_policy.get("phase18_contract") != PHASE18_CONTRACT.as_posix():
            errors.append("upstream_policy phase18_contract must name the Phase 18 contract")
        if upstream_policy.get("canonical_phase18_criteria") != phase18_criteria:
            errors.append("upstream_policy canonical_phase18_criteria must match Phase 18 upstream criteria exactly")
        if upstream_policy.get("row_required_fields") != UPSTREAM_RESULT_ROW_FIELDS:
            errors.append("upstream_policy row_required_fields must match the Phase 26 upstream row schema")
        if upstream_policy.get("release_requirement_ids") != ["EVID-04", "ACPT-01"]:
            errors.append("upstream_policy release_requirement_ids must be EVID-04 and ACPT-01")
        if upstream_policy.get("default_requirement_ids") != ["ACPT-01"]:
            errors.append("upstream_policy default_requirement_ids must be ACPT-01")
        mappings = upstream_policy.get("compatibility_mappings")
        phase25_mapping = mappings.get("phase25_compact_criterion_id") if isinstance(mappings, dict) else None
        if not isinstance(phase25_mapping, dict) or phase25_mapping.get("to") != "final-live-network-transfer-evidence":
            errors.append("upstream_policy must map Phase 25 compact live-service rows to the Phase 18 live-network criterion")
    if contract.get("generated_artifacts") != GENERATED_ARTIFACTS:
        errors.append("generated_artifacts must list the Phase 26 retained output files exactly")
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


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


def validate_ref(ref: str, allowed_roots: list[str], row_name: str, field: str) -> str:
    if not ref:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    for allowed_root in allowed_roots:
        if allowed_root.startswith("external://") and ref.startswith(allowed_root):
            if ".." in ref or ref.endswith("/"):
                raise VerificationError(f"{row_name} {field} ref is unsafe: {ref}")
            return ref
        if not allowed_root.startswith("external://"):
            relative_path = Path(ref)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise VerificationError(f"{row_name} {field} ref escapes allowed roots: {ref}")
            try:
                relative_path.relative_to(Path(allowed_root))
                return ref
            except ValueError:
                continue
    raise VerificationError(f"{row_name} {field} ref must stay under allowed release roots: {ref}")


def validate_ref_list(
    row: dict[str, Any],
    field: str,
    row_name: str,
    allowed_roots: list[str],
    require_nonempty: bool,
) -> list[str]:
    values = require_list(row, field, row_name)
    if require_nonempty and not values:
        raise VerificationError(f"{row_name} {field} must be non-empty")
    refs: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str):
            raise VerificationError(f"{row_name} {field}[{index}] must be a string")
        refs.append(validate_ref(value, allowed_roots, row_name, f"{field}[{index}]"))
    return refs


def validate_subject_digests(row: dict[str, Any], row_name: str, allowed_roots: list[str], errors: list[str]) -> None:
    subject_digests = row.get("subject_digests")
    if not isinstance(subject_digests, list) or not subject_digests:
        errors.append(f"{row_name} subject_digests must be non-empty")
        return
    for index, digest_row in enumerate(subject_digests):
        digest_name = f"{row_name} subject_digests[{index}]"
        if not isinstance(digest_row, dict):
            errors.append(f"{digest_name} must be an object")
            continue
        artifact_ref = digest_row.get("artifact_ref")
        if not isinstance(artifact_ref, str):
            errors.append(f"{digest_name} artifact_ref must be a string")
        else:
            try:
                validate_ref(artifact_ref, allowed_roots, digest_name, "artifact_ref")
            except VerificationError as error:
                errors.append(str(error))
        sha256 = digest_row.get("sha256")
        if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
            errors.append(f"{digest_name} sha256 must be lowercase SHA-256 hex")


def phase20_required_metadata_fields(contract_row: dict[str, Any]) -> list[str]:
    fields: list[str] = []
    row_id = contract_row.get("id", "<unknown>")
    for group in PHASE20_REQUIRED_METADATA_GROUPS:
        values = contract_row.get(group, [])
        if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
            raise VerificationError(f"Phase 20 row {row_id} {group} must contain strings")
        fields.extend(values)
    return list(dict.fromkeys(fields))


def phase20_allowed_metadata_fields(contract_row: dict[str, Any]) -> list[str]:
    fields = [
        "id",
        "artifact_surface",
        "proof_class",
        "status",
        "mismatch_class",
        *REQUIRED_PASS_METADATA,
        *phase20_required_metadata_fields(contract_row),
    ]
    row_id = contract_row.get("id", "<unknown>")
    for group in PHASE20_OPTIONAL_METADATA_GROUPS:
        values = contract_row.get(group, [])
        if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
            raise VerificationError(f"Phase 20 row {row_id} {group} must contain strings")
        fields.extend(values)
    return list(dict.fromkeys(fields))


def sanitized_release_row(row: dict[str, Any], contract_row: dict[str, Any]) -> dict[str, Any]:
    allowed_fields = set(phase20_allowed_metadata_fields(contract_row))
    extra_fields = sorted(set(row) - allowed_fields)
    if extra_fields:
        raise VerificationError("release input contains unsupported fields: " + ", ".join(extra_fields))
    return {field: row[field] for field in phase20_allowed_metadata_fields(contract_row) if field in row}


def validate_required_phase20_metadata(
    row: dict[str, Any],
    contract_row: dict[str, Any],
    row_name: str,
    allowed_roots: list[str],
    errors: list[str],
) -> None:
    try:
        metadata_fields = phase20_required_metadata_fields(contract_row)
    except VerificationError as error:
        errors.append(str(error))
        return
    for field in metadata_fields:
        try:
            if field in {"artifact_refs", "retention_refs"}:
                validate_ref_list(row, field, row_name, allowed_roots, require_nonempty=True)
            elif field == "subject_digests":
                validate_subject_digests(row, row_name, allowed_roots, errors)
            else:
                require_string(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))


def release_input_rows(root: Path, maybe_path: str | None) -> list[dict[str, Any]]:
    input_path = Path(maybe_path) if maybe_path is not None else PHASE20_RELEASE_INPUT_TEMPLATE
    full_path = input_path if input_path.is_absolute() else root / input_path
    if not full_path.exists():
        raise VerificationError(f"release input file does not exist: {input_path.as_posix()}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"release input is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    rows = data.get("evidence_rows") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise VerificationError("release input must contain an evidence_rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"release input row {index} must be an object")
        parsed_rows.append(row)
    return parsed_rows


def validate_release_row(
    row: dict[str, Any],
    contract_row: dict[str, Any],
    row_name: str,
    status_vocabulary: set[str],
    proof_class_vocabulary: set[str],
    allowed_roots: list[str],
) -> None:
    errors: list[str] = []
    status = require_string(row, "status", row_name)
    proof_class = require_string(row, "proof_class", row_name)
    if status not in status_vocabulary:
        errors.append(f"{row_name} status is invalid: {status}")
    if proof_class not in proof_class_vocabulary and proof_class not in NON_PASS_PROOF_CLASSES:
        errors.append(f"{row_name} proof_class is invalid: {proof_class}")
    if row.get("artifact_surface") and row.get("artifact_surface") != contract_row.get("artifact_surface"):
        errors.append(f"{row_name} artifact_surface does not match contract row {contract_row.get('id')}")
    for field in ["artifact_refs", "retention_refs"]:
        try:
            validate_ref_list(row, field, row_name, allowed_roots, require_nonempty=status == "passed")
        except VerificationError as error:
            errors.append(str(error))
    if status == "passed":
        if proof_class not in PASS_CAPABLE_PROOF_CLASSES:
            errors.append(f"{row_name} cannot pass with proof_class={proof_class!r}; release-candidate cannot pass Phase 26")
        for field in REQUIRED_PASS_METADATA:
            try:
                if field in {"artifact_refs", "retention_refs"}:
                    validate_ref_list(row, field, row_name, allowed_roots, require_nonempty=True)
                elif field == "subject_digests":
                    validate_subject_digests(row, row_name, allowed_roots, errors)
                else:
                    require_string(row, field, row_name)
            except VerificationError as error:
                errors.append(str(error))
        validate_required_phase20_metadata(row, contract_row, row_name, allowed_roots, errors)
    mismatch_class = row.get("mismatch_class")
    mismatch_values = {"pass", "intentional-delta", "blocker", "deferred-retained-code-issue"}
    if mismatch_class is not None and mismatch_class not in mismatch_values:
        errors.append(f"{row_name} mismatch_class is invalid: {mismatch_class}")
    if errors:
        raise VerificationError("\n".join(errors))


def validate_release_input(root: Path, maybe_path: str | None) -> dict[str, dict[str, Any]]:
    phase20_contract = load_json(root, PHASE20_CONTRACT)
    contract_by_id = {str(row["id"]): row for row in contract_rows(phase20_contract, PHASE20_CONTRACT)}
    expected_ids = phase20_release_row_ids(phase20_contract)
    status_vocabulary = phase20_status_vocabulary(phase20_contract)
    proof_class_vocabulary = phase20_proof_class_vocabulary(phase20_contract)
    release_input_schema = phase20_contract.get("release_input_schema")
    if not isinstance(release_input_schema, dict):
        raise VerificationError(f"{PHASE20_CONTRACT.as_posix()} release_input_schema must be an object")
    allowed_roots = release_input_schema.get("allowed_ref_roots")
    if not isinstance(allowed_roots, list) or not all(isinstance(root_value, str) and root_value for root_value in allowed_roots):
        raise VerificationError("Phase 20 release_input_schema allowed_ref_roots must contain strings")
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(release_input_rows(root, maybe_path)):
        row_name = f"release input row {index}"
        try:
            row_id = require_string(row, "id", row_name)
            if row_id not in contract_by_id:
                raise VerificationError(f"{row_name} uses unknown row id: {row_id}")
            if row_id in parsed_rows:
                raise VerificationError(f"{row_name} duplicates row id: {row_id}")
            validate_release_row(
                row,
                contract_by_id[row_id],
                row_name,
                status_vocabulary,
                proof_class_vocabulary,
                allowed_roots,
            )
            parsed_rows[row_id] = sanitized_release_row(row, contract_by_id[row_id])
        except VerificationError as error:
            errors.append(str(error))
    missing = [row_id for row_id in expected_ids if row_id not in parsed_rows]
    if missing:
        errors.append("release input missing rows: " + ", ".join(missing))
    ordered_ids = list(parsed_rows)
    if not missing and ordered_ids != expected_ids:
        errors.append("release input row order must match Phase 20 canonical rows")
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def release_status_counts(rows: dict[str, dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows.values():
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return counts


def aggregate_release_status(rows: dict[str, dict[str, Any]]) -> str:
    statuses = {str(row["status"]) for row in rows.values()}
    for status in [
        "rejected-redaction",
        "rejected-overclaim",
        "failed",
        "blocked",
        "blocked-signing-key-unavailable",
        "external-signing-required",
        "release-run-required",
        "pending-release-input",
        "source-contract-passed",
    ]:
        if status in statuses:
            return status
    if statuses == {"passed"}:
        return "passed"
    return "blocked"


def release_failure_reason(status: str, real_release_evidence_supplied: bool) -> str:
    if status == "passed":
        return "none"
    if not real_release_evidence_supplied:
        return "Release-manager evidence input was not supplied; quick mode used the checked-in Phase 20 template."
    return f"Release evidence aggregate status is {status}; all Phase 20 rows must pass with Phase 26-approved proof classes."


def phase26_requirement_ids(criterion_id: str) -> list[str]:
    if criterion_id == "final-release-artifact-signing-evidence":
        return ["EVID-04", "ACPT-01"]
    return ["ACPT-01"]


def default_upstream_status(criterion_id: str, release_status: str) -> str:
    return {
        "final-ci-evidence": "pending-ci-input",
        "final-simulator-evidence": "pending-simulator-input",
        "final-hardware-safety-media-evidence": "pending-hardware-input",
        "final-live-network-transfer-evidence": "pending-live-input",
        "final-release-artifact-signing-evidence": release_status,
        "final-retained-code-acceptance": "blocked",
        "final-residual-risk-review": "not-required",
        "final-maintainer-decision": "pending",
        "final-reference-demotion-allowed": "blocked",
    }[criterion_id]


def default_maintainer_state(criterion_id: str) -> str:
    if criterion_id in {"final-retained-code-acceptance", "final-reference-demotion-allowed"}:
        return "blocked"
    if criterion_id == "final-residual-risk-review":
        return "not-required"
    return "pending"


def default_failure_reason(criterion_id: str, status: str, release_reason: str) -> str:
    if criterion_id == "final-release-artifact-signing-evidence":
        return release_reason
    if criterion_id == "final-ci-evidence":
        return "Aggregate CI cutover evidence is outside Phase 26 quick input and remains pending."
    if criterion_id == "final-simulator-evidence":
        return "Simulator evidence is owned by Phase 23 and remains pending for final cutover review."
    if criterion_id == "final-hardware-safety-media-evidence":
        return "Hardware, media, and safety evidence is owned by Phase 24 and remains pending for final cutover review."
    if criterion_id == "final-live-network-transfer-evidence":
        return "Live-service evidence is owned by Phase 25 and maps to the Phase 18 live-network criterion."
    if criterion_id == "final-retained-code-acceptance":
        return "Retained-code acceptance is deferred to Phase 27 and cannot be approved by Phase 26."
    if criterion_id == "final-residual-risk-review":
        return "Residual-risk review is not required in Phase 26; Phase 27 owns acceptance input."
    if criterion_id == "final-maintainer-decision":
        return "Maintainer final readiness decision is pending and belongs to Phase 28."
    if criterion_id == "final-reference-demotion-allowed":
        return "Reference demotion requires explicit Phase 28 maintainer approval and is blocked by default."
    return f"Upstream criterion remains {status}."


def evidence_refs_for_criterion(criterion_id: str) -> list[str]:
    return {
        "final-ci-evidence": [
            ".planning/phases/23-simulator-evidence-execution/23-01-SUMMARY.md",
            ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-SUMMARY.md",
            ".planning/phases/25-live-service-evidence-execution/25-01-SUMMARY.md",
        ],
        "final-simulator-evidence": [
            ".planning/phases/23-simulator-evidence-execution/23-01-SUMMARY.md",
            "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json",
        ],
        "final-hardware-safety-media-evidence": [
            ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-SUMMARY.md",
            "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
        ],
        "final-live-network-transfer-evidence": [
            ".planning/phases/25-live-service-evidence-execution/25-01-SUMMARY.md",
            "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json",
        ],
        "final-release-artifact-signing-evidence": [
            (DEFAULT_OUTPUT_DIR / "normalized-release-evidence-summary.json").as_posix(),
            (DEFAULT_OUTPUT_DIR / "redaction-provenance-summary.json").as_posix(),
        ],
        "final-retained-code-acceptance": [
            "tools/bazel/manifests/phase18_cutover_review_contract.json#final-retained-code-acceptance",
        ],
        "final-residual-risk-review": [
            "tools/bazel/manifests/phase18_cutover_review_contract.json#final-residual-risk-review",
        ],
        "final-maintainer-decision": [
            "tools/bazel/manifests/phase18_cutover_review_contract.json#final-maintainer-decision",
        ],
        "final-reference-demotion-allowed": [
            "tools/bazel/manifests/phase18_cutover_review_contract.json#final-reference-demotion-allowed",
        ],
    }[criterion_id]


def artifact_refs_for_criterion(output_dir: Path, criterion_id: str) -> list[str]:
    if criterion_id == "final-release-artifact-signing-evidence":
        return [
            (output_dir / "normalized-release-evidence-summary.json").as_posix(),
            (output_dir / "artifact-reference-summary.json").as_posix(),
        ]
    return [
        (output_dir / "upstream-result-row-table.json").as_posix(),
        (output_dir / "upstream-result-manifest.json").as_posix(),
    ]


def normalize_upstream_row(row: dict[str, Any], requirement: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    status = require_string(normalized, "status", f"upstream row {row.get('criterion_id', '<missing>')}")
    exception_coverable = set(requirement.get("exception_coverable_statuses", []))
    hard_blocking_statuses = set(requirement.get("hard_blocking_statuses", []))
    acceptable_statuses = set(requirement.get("acceptable_statuses", []))
    if normalized.get("redaction_status") != "passed":
        normalized["status"] = "blocked"
        normalized["failure_reason"] = "redaction-failed: redaction_status must be passed before upstream review"
        normalized["maintainer_state"] = "blocked"
    elif normalized.get("source_ref_status") != "passed":
        normalized["status"] = "blocked"
        normalized["failure_reason"] = "source-ref-failed: source_ref_status must be passed before upstream review"
        normalized["maintainer_state"] = "blocked"
    elif normalized.get("source_lifecycle_status") not in {"current", "not-required"}:
        normalized["status"] = "blocked"
        normalized["failure_reason"] = "lifecycle-mismatch: source lifecycle is not current"
        normalized["maintainer_state"] = "blocked"
    elif status in hard_blocking_statuses:
        normalized["maintainer_state"] = "blocked"
    elif status not in acceptable_statuses and status not in exception_coverable:
        normalized["maintainer_state"] = "blocked"
    return normalized


def build_upstream_rows(
    root: Path,
    output_dir: Path,
    release_rows: dict[str, dict[str, Any]],
    real_release_evidence_supplied: bool,
    generated_at: str,
) -> list[dict[str, Any]]:
    phase18_contract = load_json(root, PHASE18_CONTRACT)
    status_vocabulary = phase18_upstream_status_vocabulary(phase18_contract)
    release_status = aggregate_release_status(release_rows)
    release_reason = release_failure_reason(release_status, real_release_evidence_supplied)
    rows: list[dict[str, Any]] = []
    for requirement in phase18_upstream_requirements(phase18_contract):
        criterion_id = require_string(requirement, "criterion_id", "upstream_result_requirement")
        status = default_upstream_status(criterion_id, release_status)
        if status not in status_vocabulary:
            raise VerificationError(f"{criterion_id} produced unknown upstream status: {status}")
        row = {
            "artifact_refs": artifact_refs_for_criterion(output_dir, criterion_id),
            "criterion_id": criterion_id,
            "evidence_family": require_string(requirement, "evidence_family", criterion_id),
            "evidence_refs": evidence_refs_for_criterion(criterion_id),
            "exception_status": "none",
            "failure_reason": default_failure_reason(criterion_id, status, release_reason),
            "generated_at_utc": generated_at,
            "maintainer_state": default_maintainer_state(criterion_id),
            "owning_phase": require_string(requirement, "source_phase", criterion_id),
            "redaction_status": "passed",
            "requirement_ids": phase26_requirement_ids(criterion_id),
            "source_lifecycle_id": require_string(requirement, "source_lifecycle_id", criterion_id),
            "source_lifecycle_status": "current",
            "source_ref_status": "passed",
            "source_requirement_ids": require_list(requirement, "requirement_ids", criterion_id),
            "status": status,
        }
        normalized = normalize_upstream_row(row, requirement)
        missing = [field for field in UPSTREAM_RESULT_ROW_FIELDS if field not in normalized]
        if missing:
            raise VerificationError(f"{criterion_id} normalized upstream row missing fields: {', '.join(missing)}")
        rows.append(normalized)
    row_ids = [str(row["criterion_id"]) for row in rows]
    if row_ids != CANONICAL_PHASE18_CRITERIA:
        raise VerificationError("normalized upstream rows must match the nine canonical Phase 18 criteria")
    return rows


def write_operator_template(root: Path, output_dir: Path, phase20_contract: dict[str, Any]) -> None:
    rows = []
    for row in contract_rows(phase20_contract, PHASE20_CONTRACT):
        row_id = require_string(row, "id", "phase20 row")
        row_template = {
            "id": row_id,
            "artifact_refs": [],
            "artifact_surface": row.get("artifact_surface", ""),
            "build_input_identity": "",
            "mismatch_class": "",
            "mismatch_reason": "",
            "operator": "",
            "owner_phase": "20-release-candidate-artifact-production",
            "proof_class": "",
            "release_run_id": "",
            "residual_risk": "",
            "retention_refs": [],
            "status": "",
            "subject_digests": [],
            "timestamp": "",
            "verification_outcome": "",
            "affected_artifact_surface": row.get("artifact_surface", ""),
        }
        for field in phase20_required_metadata_fields(row):
            if field not in row_template:
                row_template[field] = [] if field in {"artifact_refs", "retention_refs", "subject_digests"} else ""
        rows.append(row_template)
    write_json(
        root,
        output_dir / "operator-release-input-template.json",
        {
            "schema_version": "1",
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "evidence_rows": rows,
        },
    )


def write_contract_snapshots(root: Path, output_dir: Path) -> None:
    snapshots_dir = root / output_dir / "contract-snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    for snapshot in SNAPSHOT_CONTRACTS:
        shutil.copy2(root / snapshot, snapshots_dir / snapshot.name)


def reset_output_root(root: Path, output_dir: Path) -> Path:
    relative_output_dir, full_output_dir = validate_output_dir(root, output_dir)
    if full_output_dir.exists():
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)
    return relative_output_dir


def write_retained_outputs(
    root: Path,
    output_dir: Path,
    release_rows: dict[str, dict[str, Any]],
    real_release_evidence_supplied: bool,
) -> None:
    generated_at = utc_now()
    phase20_contract = load_json(root, PHASE20_CONTRACT)
    upstream_rows = build_upstream_rows(root, output_dir, release_rows, real_release_evidence_supplied, generated_at)
    release_status = aggregate_release_status(release_rows)
    release_counts = release_status_counts(release_rows)
    release_summary = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generated_at_utc": generated_at,
        "real_release_evidence_supplied": real_release_evidence_supplied,
        "release_status": release_status,
        "status_counts": release_counts,
        "row_count": len(release_rows),
        "rows": list(release_rows.values()),
    }
    artifact_refs = sorted(
        {
            ref
            for row in release_rows.values()
            for field in ["artifact_refs", "retention_refs"]
            for ref in row.get(field, [])
            if isinstance(ref, str) and ref
        }
    )
    digest_refs = [
        digest
        for row in release_rows.values()
        for digest in row.get("subject_digests", [])
        if isinstance(digest, dict)
    ]
    write_json(
        root,
        output_dir / "release-upstream-run-manifest.json",
        {
            "artifact_name": "phase26-release-signing-upstream-evidence",
            "generated_at_utc": generated_at,
            "output_root": output_dir.as_posix(),
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "real_release_evidence_supplied": real_release_evidence_supplied,
            "release_status": release_status,
            "upstream_criteria_count": len(upstream_rows),
            "generated_artifacts": GENERATED_ARTIFACTS,
        },
    )
    write_json(root, output_dir / "normalized-release-evidence-summary.json", release_summary)
    write_json(root, output_dir / "upstream-result-row-table.json", {"rows": upstream_rows})
    write_json(
        root,
        output_dir / "upstream-result-manifest.json",
        {
            "generated_at_utc": generated_at,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "rows": upstream_rows,
            "source_contract": PHASE18_CONTRACT.as_posix(),
        },
    )
    write_json(
        root,
        output_dir / "redaction-provenance-summary.json",
        {
            "generated_at_utc": generated_at,
            "phase": PHASE,
            "redaction_status": "passed",
            "retained_private_key_material": False,
            "retained_raw_payloads": False,
            "retained_credentials": False,
            "signing_identity_mode": "reference-only",
        },
    )
    write_json(
        root,
        output_dir / "artifact-reference-summary.json",
        {
            "artifact_refs": artifact_refs,
            "digest_refs": digest_refs,
            "generated_at_utc": generated_at,
            "phase": PHASE,
            "real_release_evidence_supplied": real_release_evidence_supplied,
        },
    )
    write_operator_template(root, output_dir, phase20_contract)
    write_contract_snapshots(root, output_dir)


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in [CONTRACT_MANIFEST, PHASE20_RELEASE_INPUT_TEMPLATE]:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_field_names(json.loads(text), path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


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
                'name = "phase26_release_signing_upstream_evidence_docs"',
                'name = "phase26_verify"',
                'actual = "//tools/bazel:phase26_verify"',
                'name = "phase26_verify_tests"',
                'actual = "//tools/bazel:phase26_verify_tests"',
                *[f'"{doc}"' for doc in PHASE26_DOCS],
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase26_source_ref_manifests"',
                'name = "phase26_verify"',
                'name = "phase26_verify_tests"',
                "phase26_release_signing_upstream_evidence.py",
                "phase26_release_signing_upstream_evidence_test.py",
                "phase26_release_signing_upstream_evidence_contract.json",
                "//:phase26_release_signing_upstream_evidence_docs",
                *[f'"{manifest}"' for manifest in PHASE26_SOURCE_REF_MANIFESTS],
            ],
        )
    )
    try:
        workflow_text = read_text(root, Path("tools/bazel/rust_workflow.sh"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        verify_commands = shell_case_commands(workflow_text, "phase26_verify")
        test_commands = shell_case_commands(workflow_text, "phase26_verify_tests")
        if verify_commands is None:
            errors.append("tools/bazel/rust_workflow.sh phase26_verify case arm missing")
        else:
            errors.extend(missing_required_items("tools/bazel/rust_workflow.sh phase26_verify case arm", verify_commands, PHASE26_VERIFY_COMMANDS))
            errors.extend(
                check_command_order(
                    "tools/bazel/rust_workflow.sh phase26_verify case arm",
                    verify_commands,
                    PHASE26_VERIFY_COMMANDS[0],
                    PHASE26_VERIFY_COMMANDS[1],
                    "must run --wiring-only before --quick",
                )
            )
        if test_commands is None:
            errors.append("tools/bazel/rust_workflow.sh phase26_verify_tests case arm missing")
        else:
            errors.extend(missing_required_items("tools/bazel/rust_workflow.sh phase26_verify_tests case arm", test_commands, [PHASE26_TEST_COMMAND]))
    try:
        just_text = read_text(root, Path("justfile"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        just_commands = just_recipe_commands(just_text, "phase26-verify")
        test_line = "bazel run //tools/bazel:phase26_verify_tests"
        verify_line = "bazel run //tools/bazel:phase26_verify"
        if just_commands is None:
            errors.append("justfile phase26-verify recipe missing")
        else:
            errors.extend(missing_required_items("justfile phase26-verify recipe", just_commands, [test_line, verify_line]))
            errors.extend(
                check_command_order(
                    "justfile phase26-verify recipe",
                    just_commands,
                    test_line,
                    verify_line,
                    "must run tests before verifier",
                )
            )
    if errors:
        raise VerificationError("\n".join(errors))


def run_quick(root: Path, output_dir: Path, maybe_release_input: str | None) -> None:
    check_contract(root)
    check_security(root)
    release_rows = validate_release_input(root, maybe_release_input)
    relative_output_dir = reset_output_root(root, output_dir)
    write_retained_outputs(root, relative_output_dir, release_rows, maybe_release_input is not None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 26 release signing and upstream result evidence")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 26 contract")
    parser.add_argument("--security-only", action="store_true", help="scan checked-in Phase 26 evidence inputs")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel and just workflow wiring")
    parser.add_argument("--quick", action="store_true", help="validate quick Phase 26 inputs and output containment")
    parser.add_argument("--release-input", help="optional sanitized release-manager input JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 26 evidence output directory")
    args = parser.parse_args()
    selected_modes = [args.contract_only, args.security_only, args.wiring_only, args.quick]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.release_input and not args.quick:
        parser.error("--release-input is only valid with --quick")
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 26 release signing upstream evidence contract passed")
        elif args.security_only:
            check_contract(ROOT)
            check_security(ROOT)
            print("Phase 26 release signing upstream evidence security scan passed")
        elif args.wiring_only:
            check_wiring(ROOT)
        else:
            run_quick(ROOT, Path(args.output_dir), args.release_input)
            print("Phase 26 release signing upstream evidence quick validation passed")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
