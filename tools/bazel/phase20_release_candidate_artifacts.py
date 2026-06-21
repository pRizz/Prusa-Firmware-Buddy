#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "20-release-candidate-artifact-production"
PHASE_LIFECYCLE_ID = "20-2026-06-21T12-40-17"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json")
RELEASE_INPUT_TEMPLATE = Path("tools/bazel/manifests/phase20_release_environment_inputs.template.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase20")
RELEASE_IDENTITY_LABEL = "//tools/bazel:phase17_release_candidate_artifacts"
RELEASE_IDENTITY_COMMAND = "bazel build //tools/bazel:phase17_release_candidate_artifacts"
ALLOWED_EXTERNAL_REF_ROOT = "external://phase20/"
REQUIRED_ARTIFACT_OUTPUTS = [
    ".bin",
    ".bbf",
    ".dfu",
    ".map",
    ".provenance.json",
    "resource-image",
    "resource-package",
    "language-bundle",
    "wui-assets",
    "esp-package",
    "mmu-package",
    "dwarf-firmware",
    "modularbed-firmware",
    "xbuddy-extension-firmware",
    "package-manifest",
    "signing-summary",
    "provenance-summary",
    "retention-manifest",
    "comparison-report",
]
REQUIRED_ROW_IDS = [
    "rel-bin-firmware-image",
    "rel-bbf-firmware-package",
    "rel-dfu-update-package",
    "rel-map-and-provenance",
    "rel-resource-image-package",
    "rel-language-bundles",
    "rel-wui-assets",
    "rel-esp-packages",
    "rel-mmu-package",
    "rel-auxiliary-dwarf-firmware",
    "rel-auxiliary-modularbed-firmware",
    "rel-auxiliary-xbuddy-extension-firmware",
    "rel-package-manifests",
    "rel-signing-key-identity",
    "rel-build-input-identity",
    "rel-artifact-retention",
    "rel-reference-comparison-report",
    "rel-contract-traceability-redaction-boundary",
]
REQUIRED_REQUIREMENT_IDS = {"REL-01", "REL-02", "REL-03"}
PHASE20_SOURCE_REF_MANIFESTS = [
    "manifests/phase17_release_candidate_evidence_contract.json",
    "manifests/phase19_aggregate_ci_evidence_contract.json",
    "manifests/phase20_release_candidate_artifacts_contract.json",
    "manifests/phase20_release_environment_inputs.template.json",
    "manifests/phase11_reference_comparisons.json",
    "manifests/representative_products.json",
]
PHASE20_SOURCE_REF_MANIFEST_PATHS = {Path("tools/bazel") / path for path in PHASE20_SOURCE_REF_MANIFESTS}
PHASE20_SOURCE_REF_ROW_COLLECTIONS = {
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json": ["rows"],
    "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json": ["phases.external_input"],
    "tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json": ["rows"],
    "tools/bazel/manifests/phase20_release_environment_inputs.template.json": ["evidence_rows"],
    "tools/bazel/manifests/phase11_reference_comparisons.json": ["reference_comparisons"],
    "tools/bazel/manifests/representative_products.json": ["entries"],
}
PHASE20_DOCS = [
    ".planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md",
    ".planning/phases/20-release-candidate-artifact-production/20-RESEARCH.md",
    ".planning/phases/20-release-candidate-artifact-production/20-VALIDATION.md",
    ".planning/phases/20-release-candidate-artifact-production/20-01-PLAN.md",
    ".planning/phases/20-release-candidate-artifact-production/20-02-PLAN.md",
]
PROOF_CLASS_VOCABULARY = [
    "release-candidate",
    "approved-release-run",
    "external-release-key-evidence",
    "local-smoke",
    "template-only",
]
APPROVED_PASS_PROOF_CLASSES = {
    "release-candidate",
    "approved-release-run",
    "external-release-key-evidence",
}
STATUS_VOCABULARY = [
    "pending-release-input",
    "release-run-required",
    "external-signing-required",
    "blocked-signing-key-unavailable",
    "source-contract-passed",
    "passed",
    "failed",
    "rejected-redaction",
    "rejected-overclaim",
]
MISMATCH_CLASS_VOCABULARY = [
    "pass",
    "intentional-delta",
    "blocker",
    "deferred-retained-code-issue",
]
REQUIRED_ROW_FIELDS = [
    "id",
    "title",
    "requirement_ids",
    "artifact_surface",
    "artifact_outputs",
    "proof_class_allowed",
    "default_status",
    "required_input_kind",
    "release_metadata_required",
    "signing_metadata_required",
    "provenance_metadata_required",
    "comparison_metadata_required",
    "retention_metadata_required",
    "source_contract_refs",
    "owner_phase",
    "residual_cutover_gates",
]
REQUIRED_PASS_FIELDS = [
    "subject_digests",
    "build_input_identity",
    "retention_refs",
    "verification_outcome",
]
FORBIDDEN_FIELD_NAMES = {
    "private_key",
    "signing_key_value",
    "raw_key_bytes",
    "private_certificate",
    "token",
    "password",
    "credential",
    "raw_firmware_payload",
    "firmware_payload_bytes",
    "signing_payload_bytes",
    "crash_dump_bytes",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    (
        "forbidden-field-marker",
        re.compile(
            r"\b(private_key|signing_key_value|raw_key_bytes|private_certificate|token|password|credential|raw_firmware_payload|firmware_payload_bytes|signing_payload_bytes|crash_dump_bytes)\b",
            re.IGNORECASE,
        ),
    ),
)


class VerificationError(Exception):
    pass


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


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and row[field] in ("", None)]
    if missing or empty:
        details: list[str] = []
        if missing:
            details.append("missing required fields: " + ", ".join(missing))
        if empty:
            details.append("empty required fields: " + ", ".join(empty))
        raise VerificationError(f"{row_name} " + "; ".join(details))


def contract_rows(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = contract.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} must contain a rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} rows[{index}] must be an object")
        parsed_rows.append(row)
    return parsed_rows


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        matches = sorted({match.group(1) for match in pattern.finditer(text) if match.lastindex})
        if matches:
            errors.append(f"{path.as_posix()} contains forbidden release evidence marker: {', '.join(matches)}")
            continue
        if pattern.search(text):
            errors.append(f"{path.as_posix()} contains forbidden release evidence marker: {label}")
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(FORBIDDEN_FIELD_NAMES & set(value))
        if forbidden:
            raise VerificationError(f"{path} contains forbidden evidence fields: {', '.join(forbidden)}")
        for key, child in value.items():
            reject_forbidden_field_names(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden_field_names(child, f"{path}[{index}]")


def validate_ref(ref: str, row_name: str, field: str) -> str:
    if not ref:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    if ref.startswith(ALLOWED_EXTERNAL_REF_ROOT):
        return ref
    relative_path = Path(ref)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} {field} ref escapes allowed roots: {ref}")
    try:
        relative_path.relative_to(DEFAULT_OUTPUT_DIR)
    except ValueError as error:
        raise VerificationError(f"{row_name} {field} ref must stay under {DEFAULT_OUTPUT_DIR.as_posix()} or {ALLOWED_EXTERNAL_REF_ROOT}: {ref}") from error
    return ref


def validate_ref_list(row: dict[str, Any], field: str, row_name: str, require_nonempty: bool) -> list[str]:
    values = require_list(row, field, row_name)
    if require_nonempty and not values:
        raise VerificationError(f"{row_name} {field} must be non-empty")
    refs: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str):
            raise VerificationError(f"{row_name} {field}[{index}] must be a string")
        refs.append(validate_ref(value, row_name, f"{field}[{index}]"))
    return refs


def resolved_output_dir(root: Path, output_dir: Path) -> tuple[Path, Path]:
    resolved_root = root.resolve(strict=False)
    expected_root = (resolved_root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    if output_dir.is_absolute():
        candidate = output_dir
    else:
        if ".." in output_dir.parts:
            raise VerificationError(f"--output-dir must be contained by {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}")
        candidate = resolved_root / output_dir
    full_output_dir = candidate.resolve(strict=False)
    try:
        relative_output_dir = full_output_dir.relative_to(resolved_root)
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}") from error
    return relative_output_dir, full_output_dir


def source_ref_row_matches(data: Any, collection_names: list[str], row_id: str) -> list[str]:
    if not isinstance(data, dict):
        return []
    matches: list[str] = []
    for collection_name in collection_names:
        if collection_name == "phases.external_input":
            phases = data.get("phases")
            if not isinstance(phases, list):
                continue
            for index, phase in enumerate(phases):
                if not isinstance(phase, dict):
                    continue
                external_input = phase.get("external_input")
                if isinstance(external_input, dict) and external_input.get("id") == row_id:
                    matches.append(f"phases[{index}].external_input")
            continue
        rows = data.get(collection_name)
        if not isinstance(rows, list):
            continue
        for index, row in enumerate(rows):
            if isinstance(row, dict) and row.get("id") == row_id:
                matches.append(f"{collection_name}[{index}]")
    return matches


def resolve_source_ref(root: Path, source_ref: str, row_name: str) -> None:
    if "#" not in source_ref:
        raise VerificationError(f"{row_name} source ref must use file#row-id: {source_ref}")
    path_text, row_id = source_ref.split("#", 1)
    if not path_text or not row_id:
        raise VerificationError(f"{row_name} source ref must include file and row ID: {source_ref}")
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} source ref must be repo-relative: {source_ref}")
    if relative_path not in PHASE20_SOURCE_REF_MANIFEST_PATHS:
        raise VerificationError(f"{row_name} source ref path is not an approved Phase 20 source manifest: {source_ref}")
    data = load_json(root, relative_path)
    collection_names = PHASE20_SOURCE_REF_ROW_COLLECTIONS.get(relative_path.as_posix(), [])
    if not collection_names:
        raise VerificationError(f"{row_name} source ref path has no approved row collections: {source_ref}")
    matches = source_ref_row_matches(data, collection_names, row_id)
    if not matches:
        raise VerificationError(f"{row_name} source ref row not found in approved row collections: {source_ref}")
    if len(matches) > 1:
        raise VerificationError(f"{row_name} source ref row matches multiple approved rows: {source_ref}")


def check_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "release_identity_label": RELEASE_IDENTITY_LABEL,
        "release_identity_command": RELEASE_IDENTITY_COMMAND,
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    if contract.get("required_artifact_outputs") != REQUIRED_ARTIFACT_OUTPUTS:
        actual_outputs = contract.get("required_artifact_outputs")
        actual_set = set(actual_outputs) if isinstance(actual_outputs, list) else set()
        for missing in REQUIRED_ARTIFACT_OUTPUTS:
            if missing not in actual_set:
                errors.append(f"missing required artifact output: {missing}")
        if not errors:
            errors.append("required_artifact_outputs order must match Phase 20 contract")
    if contract.get("proof_class_vocabulary") != PROOF_CLASS_VOCABULARY:
        errors.append("proof_class_vocabulary does not match Phase 20 vocabulary")
    if contract.get("status_vocabulary") != STATUS_VOCABULARY:
        errors.append("status_vocabulary does not match Phase 20 vocabulary")
    if contract.get("mismatch_class_vocabulary") != MISMATCH_CLASS_VOCABULARY:
        errors.append("mismatch_class_vocabulary does not match Phase 20 vocabulary")
    try:
        rows = contract_rows(contract)
    except VerificationError as error:
        errors.append(str(error))
        rows = []
    validate_rows(root, rows, errors)
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def validate_rows(root: Path, rows: list[dict[str, Any]], errors: list[str]) -> None:
    row_ids = [str(row.get("id")) for row in rows]
    if row_ids != REQUIRED_ROW_IDS:
        for missing in REQUIRED_ROW_IDS:
            if missing not in row_ids:
                errors.append(f"missing required release row: {missing}")
        duplicates = sorted({row_id for row_id in row_ids if row_ids.count(row_id) > 1})
        for duplicate in duplicates:
            errors.append(f"duplicate release row: {duplicate}")
        if not errors:
            errors.append("release row order must match Phase 20 contract")
    covered_requirements: set[str] = set()
    for row in rows:
        row_name = str(row.get("id", "unknown-row"))
        try:
            validate_row(root, row, row_name)
            covered_requirements.update(row["requirement_ids"])
        except VerificationError as error:
            errors.append(str(error))
    for missing in sorted(REQUIRED_REQUIREMENT_IDS - covered_requirements):
        errors.append(f"missing REL requirement coverage: {missing}")


def validate_row(root: Path, row: dict[str, Any], row_name: str) -> None:
    require_fields(row, REQUIRED_ROW_FIELDS, row_name)
    errors: list[str] = []
    requirement_ids = set(require_list(row, "requirement_ids", row_name))
    if not requirement_ids <= REQUIRED_REQUIREMENT_IDS:
        errors.append(f"{row_name} uses unknown requirement IDs: {sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)}")
    for field in [
        "artifact_outputs",
        "proof_class_allowed",
        "release_metadata_required",
        "signing_metadata_required",
        "provenance_metadata_required",
        "comparison_metadata_required",
        "retention_metadata_required",
        "source_contract_refs",
        "residual_cutover_gates",
    ]:
        values = require_list(row, field, row_name)
        if not all(isinstance(value, str) and value for value in values):
            errors.append(f"{row_name} {field} must contain non-empty strings")
    artifact_outputs = set(row["artifact_outputs"])
    if not artifact_outputs <= set(REQUIRED_ARTIFACT_OUTPUTS):
        errors.append(f"{row_name} artifact_outputs contains unknown outputs")
    proof_classes = set(row["proof_class_allowed"])
    if not proof_classes <= set(PROOF_CLASS_VOCABULARY):
        errors.append(f"{row_name} proof_class_allowed contains unknown proof classes")
    for source_ref in row["source_contract_refs"]:
        if not isinstance(source_ref, str):
            continue
        try:
            resolve_source_ref(root, source_ref, row_name)
        except VerificationError as error:
            errors.append(str(error))
    default_status = require_string(row, "default_status", row_name)
    if default_status not in STATUS_VOCABULARY:
        errors.append(f"{row_name} default_status is invalid: {default_status}")
    if default_status == "passed":
        errors.append(f"{row_name} default_status cannot be passed without approved release input")
    if require_string(row, "owner_phase", row_name) != PHASE:
        errors.append(f"{row_name} owner_phase must be {PHASE}")
    if errors:
        raise VerificationError("\n".join(errors))


def check_security(root: Path, maybe_output_dir: Path | None = None) -> None:
    errors: list[str] = []
    for path in [CONTRACT_MANIFEST, RELEASE_INPUT_TEMPLATE]:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_field_names(json.loads(text), path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if maybe_output_dir is not None:
        relative_output_dir, full_output_dir = resolved_output_dir(root, maybe_output_dir)
        if full_output_dir.exists():
            for full_path in sorted(path for path in full_output_dir.rglob("*") if path.is_file()):
                relative_path = full_path.relative_to(root)
                try:
                    text = full_path.read_text(encoding="utf-8")
                    reject_forbidden_text(relative_path, text)
                    reject_forbidden_field_names(json.loads(text), relative_path.as_posix())
                except json.JSONDecodeError:
                    continue
                except VerificationError as error:
                    errors.append(str(error))
        validate_ref(relative_output_dir.as_posix(), "generated output", "output_dir")
    if errors:
        raise VerificationError("\n".join(errors))


def load_release_input(root: Path, maybe_path: str | None) -> list[dict[str, Any]]:
    if maybe_path is None:
        return []
    input_path = Path(maybe_path)
    full_path = input_path if input_path.is_absolute() else root / input_path
    if not full_path.exists():
        raise VerificationError(f"release input file does not exist: {maybe_path}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"release input is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    rows = data.get("evidence_rows") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise VerificationError("release input must contain an evidence_rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"release input row {index} must be an object")
        parsed_rows.append(row)
    return parsed_rows


def validated_release_rows(root: Path, contract: dict[str, Any], maybe_path: str | None) -> dict[str, dict[str, Any]]:
    rows = load_release_input(root, maybe_path)
    if not rows:
        return {}
    contract_by_id = {str(row["id"]): row for row in contract_rows(contract)}
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"release input row {index}"
        try:
            row_id = require_string(row, "id", row_name)
            if row_id not in contract_by_id:
                raise VerificationError(f"{row_name} uses unknown row id: {row_id}")
            if row_id in parsed_rows:
                raise VerificationError(f"{row_name} duplicates row id: {row_id}")
            validate_release_row(row, contract_by_id[row_id], row_name)
            parsed_rows[row_id] = dict(row)
        except VerificationError as error:
            errors.append(str(error))
    missing = [row_id for row_id in REQUIRED_ROW_IDS if row_id not in parsed_rows]
    if missing:
        errors.append("release input missing rows: " + ", ".join(missing))
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def validate_release_row(row: dict[str, Any], contract_row: dict[str, Any], row_name: str) -> None:
    errors: list[str] = []
    status = require_string(row, "status", row_name)
    proof_class = require_string(row, "proof_class", row_name)
    if status not in STATUS_VOCABULARY:
        errors.append(f"{row_name} status is invalid: {status}")
    if proof_class not in PROOF_CLASS_VOCABULARY:
        errors.append(f"{row_name} proof_class is invalid: {proof_class}")
    if row.get("artifact_surface") and row.get("artifact_surface") != contract_row["artifact_surface"]:
        errors.append(f"{row_name} artifact_surface does not match contract row {contract_row['id']}")
    for field in ["artifact_refs", "retention_refs"]:
        try:
            validate_ref_list(row, field, row_name, require_nonempty=status == "passed")
        except VerificationError as error:
            errors.append(str(error))
    if status == "passed":
        for field in contract_row["comparison_metadata_required"]:
            try:
                value = require_string(row, field, row_name)
            except VerificationError as error:
                errors.append(str(error))
                continue
            if field == "owner_phase" and value != PHASE:
                errors.append(f"{row_name} owner_phase must be {PHASE}")
            if field == "affected_artifact_surface" and value != contract_row["artifact_surface"]:
                errors.append(f"{row_name} affected_artifact_surface must match contract row {contract_row['id']}")
    mismatch_class = row.get("mismatch_class")
    if mismatch_class is not None and mismatch_class not in MISMATCH_CLASS_VOCABULARY:
        errors.append(f"{row_name} mismatch_class is invalid: {mismatch_class}")
    if status == "passed":
        if proof_class not in APPROVED_PASS_PROOF_CLASSES:
            errors.append(f"{row_name} cannot pass with proof_class={proof_class!r}")
        for field in REQUIRED_PASS_FIELDS:
            try:
                if field in ["subject_digests", "retention_refs"]:
                    require_non_empty_list(row, field, row_name)
                else:
                    require_string(row, field, row_name)
            except VerificationError as error:
                errors.append(str(error))
        validate_subject_digests(row, row_name, errors)
        validate_required_metadata(row, contract_row, row_name, errors)
    if errors:
        raise VerificationError("\n".join(errors))


def validate_required_metadata(row: dict[str, Any], contract_row: dict[str, Any], row_name: str, errors: list[str]) -> None:
    metadata_fields = [
        *contract_row["release_metadata_required"],
        *contract_row["signing_metadata_required"],
        *contract_row["provenance_metadata_required"],
        *contract_row["retention_metadata_required"],
    ]
    for field in dict.fromkeys(metadata_fields):
        try:
            if field in {"artifact_refs", "retention_refs"}:
                validate_ref_list(row, field, row_name, require_nonempty=True)
            elif field == "subject_digests":
                validate_subject_digests(row, row_name, errors)
            else:
                require_string(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))


def validate_subject_digests(row: dict[str, Any], row_name: str, errors: list[str]) -> None:
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
                validate_ref(artifact_ref, digest_name, "artifact_ref")
            except VerificationError as error:
                errors.append(str(error))
        sha256 = digest_row.get("sha256")
        if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
            errors.append(f"{digest_name} sha256 must be lowercase SHA-256 hex")


def quick_result_row(contract_row: dict[str, Any], maybe_release_row: dict[str, Any] | None) -> dict[str, Any]:
    row = {
        "id": contract_row["id"],
        "title": contract_row["title"],
        "requirement_ids": contract_row["requirement_ids"],
        "artifact_surface": contract_row["artifact_surface"],
        "artifact_outputs": contract_row["artifact_outputs"],
        "proof_class": "template-only",
        "status": contract_row["default_status"],
        "artifact_refs": [],
        "release_run_id": "",
        "timestamp": "",
        "operator": "",
        "subject_digests": [],
        "build_input_identity": "",
        "key_identity_ref": "",
        "signing_mode": "",
        "contract_validation": "",
        "redaction_scan": "",
        "source_contract_snapshot": "",
        "retention_refs": [],
        "verification_outcome": "pending-release-input",
        "mismatch_class": "blocker",
        "mismatch_reason": "Awaiting approved release comparison metadata.",
        "owner_phase": PHASE,
        "affected_artifact_surface": contract_row["artifact_surface"],
        "residual_risk": "Awaiting approved release-run evidence.",
    }
    if maybe_release_row is None:
        return row
    for field in [
        "proof_class",
        "status",
        "artifact_refs",
        "release_run_id",
        "timestamp",
        "operator",
        "subject_digests",
        "build_input_identity",
        "key_identity_ref",
        "signing_mode",
        "contract_validation",
        "redaction_scan",
        "source_contract_snapshot",
        "retention_refs",
        "verification_outcome",
        "mismatch_class",
        "mismatch_reason",
        "owner_phase",
        "affected_artifact_surface",
        "residual_risk",
    ]:
        if field in maybe_release_row:
            row[field] = maybe_release_row[field]
    return row


def write_json(root: Path, relative_path: Path, data: dict[str, Any]) -> None:
    full_path = root / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_quick_artifacts(root: Path, contract: dict[str, Any], output_dir: Path, release_rows: dict[str, dict[str, Any]]) -> None:
    relative_output_dir, full_output_dir = resolved_output_dir(root, output_dir)
    if full_output_dir.exists():
        shutil.rmtree(full_output_dir)
    (full_output_dir / "logs").mkdir(parents=True)
    rows = [quick_result_row(row, release_rows.get(str(row["id"]))) for row in contract_rows(contract)]
    release_inputs_supplied = bool(release_rows)
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    result_manifest = {
        "artifact_name": contract["artifact_name"],
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": relative_output_dir.as_posix(),
        "release_inputs_supplied": release_inputs_supplied,
        "release_identity_label": RELEASE_IDENTITY_LABEL,
        "release_identity_command": RELEASE_IDENTITY_COMMAND,
        "rows": rows,
        "status_counts": status_counts,
    }
    normalized = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "rows": rows,
    }
    signing_summary = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "release_inputs_supplied": release_inputs_supplied,
        "rows": [
            {
                "id": row["id"],
                "status": row["status"],
                "proof_class": row["proof_class"],
                "release_run_id": row["release_run_id"],
                "timestamp": row["timestamp"],
                "operator": row["operator"],
                "build_input_identity": row["build_input_identity"],
                "key_identity_ref": row["key_identity_ref"],
                "signing_mode": row["signing_mode"],
                "subject_digests": row["subject_digests"],
                "retention_refs": row["retention_refs"],
                "verification_outcome": row["verification_outcome"],
                "contract_validation": row["contract_validation"],
                "redaction_scan": row["redaction_scan"],
                "source_contract_snapshot": row["source_contract_snapshot"],
            }
            for row in rows
        ],
    }
    comparison_report = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "rows": [
            {
                "id": row["id"],
                "artifact_surface": row["artifact_surface"],
                "mismatch_class": row["mismatch_class"],
                "mismatch_reason": row["mismatch_reason"],
                "owner_phase": row["owner_phase"],
                "affected_artifact_surface": row["affected_artifact_surface"],
                "residual_risk": row["residual_risk"],
            }
            for row in rows
        ],
    }
    target_snapshot = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "release_identity_label": RELEASE_IDENTITY_LABEL,
        "release_identity_command": RELEASE_IDENTITY_COMMAND,
        "contract_manifest": CONTRACT_MANIFEST.as_posix(),
        "release_input_template": RELEASE_INPUT_TEMPLATE.as_posix(),
        "required_artifact_outputs": REQUIRED_ARTIFACT_OUTPUTS,
    }
    write_json(root, relative_output_dir / "release-result-manifest.json", result_manifest)
    write_json(root, relative_output_dir / "normalized-release-results.json", normalized)
    write_json(root, relative_output_dir / "redacted-signing-provenance-summary.json", signing_summary)
    write_json(root, relative_output_dir / "comparison-classification-report.json", comparison_report)
    write_json(root, relative_output_dir / "target-source-snapshot.json", target_snapshot)
    shutil.copy2(root / RELEASE_INPUT_TEMPLATE, root / relative_output_dir / "release-environment-input-template.json")
    log_path = root / relative_output_dir / "logs/phase20-release-candidate-artifacts.log"
    log_path.write_text(
        "\n".join(
            [
                f"phase={PHASE}",
                f"release_inputs_supplied={str(release_inputs_supplied).lower()}",
                f"rows={len(rows)}",
                f"output_root={relative_output_dir.as_posix()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def iter_bazel_call_blocks(text: str, call_name: str) -> list[str]:
    blocks: list[str] = []
    for match in re.finditer(rf"(?m)^\s*{re.escape(call_name)}\(", text):
        depth = 0
        in_comment = False
        maybe_string_quote: str | None = None
        escaped = False
        for index in range(match.start(), len(text)):
            char = text[index]
            if in_comment:
                if char == "\n":
                    in_comment = False
                continue
            if maybe_string_quote is not None:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == maybe_string_quote:
                    maybe_string_quote = None
                continue
            if char == "#":
                in_comment = True
                continue
            if char in {'"', "'"}:
                maybe_string_quote = char
                continue
            if char == "(":
                depth += 1
                continue
            if char != ")":
                continue
            depth -= 1
            if depth == 0:
                blocks.append(text[match.start():index + 1])
                break
    return blocks


def bazel_string_attr(block: str, attr: str) -> str | None:
    match = re.search(rf'(?m)^\s*{re.escape(attr)}\s*=\s*"([^"]*)"', block)
    if match is None:
        return None
    return match.group(1)


def bazel_list_attr(block: str, attr: str) -> list[str]:
    match = re.search(rf"(?ms)^\s*{re.escape(attr)}\s*=\s*\[(.*?)\]", block)
    if match is None:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def bazel_rule_block(text: str, rule_kind: str, name: str) -> str | None:
    for block in iter_bazel_call_blocks(text, rule_kind):
        if bazel_string_attr(block, "name") == name:
            return block
    return None


def missing_required_items(location: str, actual: list[str], expected: list[str]) -> list[str]:
    actual_values = set(actual)
    return [f"{location} missing required wiring item: {item}" for item in expected if item not in actual_values]


def check_exact_bazel_list(block: str | None, location: str, attr: str, expected: list[str]) -> list[str]:
    if block is None:
        return [f"{location} missing required Bazel rule"]
    actual = bazel_list_attr(block, attr)
    if actual == expected:
        return []
    missing = missing_required_items(f"{location} {attr}", actual, expected)
    extra = [f"{location} {attr} has unexpected wiring item: {item}" for item in actual if item not in expected]
    if missing or extra:
        return missing + extra
    return [f"{location} {attr} order must match Phase 20 wiring"]


def check_bazel_string_attr(block: str | None, location: str, attr: str, expected: str) -> list[str]:
    if block is None:
        return [f"{location} missing required Bazel rule"]
    actual = bazel_string_attr(block, attr)
    if actual == expected:
        return []
    return [f"{location} {attr} must be {expected!r}, not {actual!r}"]


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


def check_command_order(location: str, commands: list[str], first: str, second: str) -> list[str]:
    if first not in commands or second not in commands:
        return []
    if commands.index(first) <= commands.index(second):
        return []
    return [f"{location} must run tests before verifier"]


def check_phase20_release_identity_target(text: str) -> list[str]:
    manifest_block = bazel_rule_block(text, "filegroup", "phase20_release_environment_input_manifest")
    release_block = bazel_rule_block(text, "filegroup", "phase17_release_candidate_artifacts")
    errors = check_exact_bazel_list(
        manifest_block,
        "tools/bazel/BUILD.bazel filegroup phase20_release_environment_input_manifest",
        "srcs",
        [RELEASE_INPUT_TEMPLATE.relative_to("tools/bazel").as_posix()],
    )
    expected_srcs = [":phase20_release_environment_input_manifest"]
    if release_block is None:
        errors.append("tools/bazel/BUILD.bazel missing phase17_release_candidate_artifacts filegroup")
        return errors
    srcs = bazel_list_attr(release_block, "srcs")
    forbidden_smoke_deps = {
        ":phase17_representative_release_smoke",
        ":representative_release_artifacts",
        "//tools/bazel:phase17_representative_release_smoke",
        "//tools/bazel:representative_release_artifacts",
        "//tools/bazel:phase3_verify",
    }
    wrapped_smoke = sorted(set(srcs) & forbidden_smoke_deps)
    if wrapped_smoke:
        errors.append(
            "tools/bazel/BUILD.bazel phase17_release_candidate_artifacts cannot wrap local smoke dependencies: "
            + ", ".join(wrapped_smoke)
        )
    if srcs != expected_srcs:
        errors.extend(check_exact_bazel_list(
            release_block,
            "tools/bazel/BUILD.bazel filegroup phase17_release_candidate_artifacts",
            "srcs",
            expected_srcs,
        ))
    return errors


def check_tools_build_wiring(root: Path) -> list[str]:
    path = Path("tools/bazel/BUILD.bazel")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors = check_phase20_release_identity_target(text)
    source_refs_block = bazel_rule_block(text, "filegroup", "phase20_source_ref_manifests")
    smoke_block = bazel_rule_block(text, "filegroup", "phase17_representative_release_smoke")
    verify_block = bazel_rule_block(text, "shell_binary", "phase20_verify")
    verify_tests_block = bazel_rule_block(text, "shell_binary", "phase20_verify_tests")
    errors.extend(check_exact_bazel_list(
        smoke_block,
        "tools/bazel/BUILD.bazel filegroup phase17_representative_release_smoke",
        "srcs",
        [":representative_release_artifacts"],
    ))
    errors.extend(check_exact_bazel_list(
        source_refs_block,
        "tools/bazel/BUILD.bazel filegroup phase20_source_ref_manifests",
        "srcs",
        PHASE20_SOURCE_REF_MANIFESTS,
    ))
    errors.extend(check_exact_bazel_list(
        verify_block,
        "tools/bazel/BUILD.bazel shell_binary phase20_verify",
        "data",
        [
            "phase20_release_candidate_artifacts.py",
            "manifests/phase20_release_candidate_artifacts_contract.json",
            "manifests/phase20_release_environment_inputs.template.json",
            ":phase20_source_ref_manifests",
            ":phase17_release_candidate_artifacts",
            ":phase17_representative_release_smoke",
            "//:phase20_release_candidate_artifacts_docs",
            "//:phase17_release_candidate_evidence_docs",
            "//:phase19_aggregate_ci_evidence_docs",
        ],
    ))
    errors.extend(check_exact_bazel_list(
        verify_tests_block,
        "tools/bazel/BUILD.bazel shell_binary phase20_verify_tests",
        "data",
        [
            "phase20_release_candidate_artifacts.py",
            "phase20_release_candidate_artifacts_test.py",
            "manifests/phase20_release_candidate_artifacts_contract.json",
            "manifests/phase20_release_environment_inputs.template.json",
            ":phase20_source_ref_manifests",
            ":phase17_release_candidate_artifacts",
            ":phase17_representative_release_smoke",
        ],
    ))
    return errors


def check_root_build_wiring(root: Path) -> list[str]:
    path = Path("BUILD.bazel")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors = check_exact_bazel_list(
        bazel_rule_block(text, "filegroup", "phase20_release_candidate_artifacts_docs"),
        "BUILD.bazel filegroup phase20_release_candidate_artifacts_docs",
        "srcs",
        PHASE20_DOCS,
    )
    aliases = {
        "phase20_verify": "//tools/bazel:phase20_verify",
        "phase20_verify_tests": "//tools/bazel:phase20_verify_tests",
    }
    for name, actual in aliases.items():
        errors.extend(check_bazel_string_attr(
            bazel_rule_block(text, "alias", name),
            f"BUILD.bazel alias {name}",
            "actual",
            actual,
        ))
    return errors


def check_rust_workflow_wiring(root: Path) -> list[str]:
    path = Path("tools/bazel/rust_workflow.sh")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors: list[str] = []
    verify_commands = shell_case_commands(text, "phase20_verify")
    verify_tests_commands = shell_case_commands(text, "phase20_verify_tests")
    if verify_commands is None:
        errors.append("tools/bazel/rust_workflow.sh phase20_verify case arm missing")
    else:
        expected_verify_commands = [
            "python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only",
            "python3 tools/bazel/phase20_release_candidate_artifacts.py --quick",
        ]
        errors.extend(missing_required_items(
            "tools/bazel/rust_workflow.sh phase20_verify case arm",
            verify_commands,
            expected_verify_commands,
        ))
        errors.extend(check_command_order(
            "tools/bazel/rust_workflow.sh phase20_verify case arm",
            verify_commands,
            expected_verify_commands[0],
            expected_verify_commands[1],
        ))
    if verify_tests_commands is None:
        errors.append("tools/bazel/rust_workflow.sh phase20_verify_tests case arm missing")
    else:
        errors.extend(missing_required_items(
            "tools/bazel/rust_workflow.sh phase20_verify_tests case arm",
            verify_tests_commands,
            ["python3 tools/bazel/phase20_release_candidate_artifacts_test.py"],
        ))
    return errors


def check_just_wiring(root: Path) -> list[str]:
    path = Path("justfile")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    verify_commands = just_recipe_commands(text, "phase20-verify")
    tests_line = "bazel run //tools/bazel:phase20_verify_tests"
    verify_line = "bazel run //tools/bazel:phase20_verify"
    if verify_commands is None:
        return ["justfile phase20-verify recipe missing"]
    errors = missing_required_items("justfile phase20-verify recipe", verify_commands, [tests_line, verify_line])
    errors.extend(check_command_order("justfile phase20-verify recipe", verify_commands, tests_line, verify_line))
    return errors


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    errors.extend(check_tools_build_wiring(root))
    errors.extend(check_root_build_wiring(root))
    errors.extend(check_rust_workflow_wiring(root))
    errors.extend(check_just_wiring(root))
    if errors:
        raise VerificationError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 20 release candidate artifacts")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 20 contract")
    parser.add_argument("--security-only", action="store_true", help="scan checked-in Phase 20 contract/template files")
    parser.add_argument("--quick", action="store_true", help="write deterministic Phase 20 quick artifacts")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel and just workflow wiring")
    parser.add_argument("--release-input", help="optional approved release input JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 20 evidence output directory")
    args = parser.parse_args()
    selected_modes = [args.contract_only, args.security_only, args.quick, args.wiring_only]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.release_input and not args.quick:
        parser.error("--release-input is only valid with --quick")
    output_dir = Path(args.output_dir)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 20 release candidate artifact contract passed")
        elif args.security_only:
            check_contract(ROOT)
            check_security(ROOT)
            print("Phase 20 release candidate artifact security scan passed")
        else:
            if args.wiring_only:
                check_wiring(ROOT)
                print("Phase 20 release candidate artifact wiring passed")
                return 0
            contract = check_contract(ROOT)
            release_rows = validated_release_rows(ROOT, contract, args.release_input)
            write_quick_artifacts(ROOT, contract, output_dir, release_rows)
            check_security(ROOT, output_dir)
            print(f"Phase 20 release candidate artifacts written to {output_dir.as_posix()}")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
