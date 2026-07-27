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
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json")
RELEASE_INPUT_TEMPLATE = Path(
    "tools/bazel/manifests/phase20_release_environment_inputs.template.json")
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
PHASE20_SOURCE_REF_MANIFEST_PATHS = {
    Path("tools/bazel") / path
    for path in PHASE20_SOURCE_REF_MANIFESTS
}
PHASE20_SOURCE_REF_ROW_COLLECTIONS = {
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json":
    ["rows"],
    "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json":
    ["phases.external_input"],
    "tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json":
    ["rows"],
    "tools/bazel/manifests/phase20_release_environment_inputs.template.json":
    ["evidence_rows"],
    "tools/bazel/manifests/phase11_reference_comparisons.json":
    ["reference_comparisons"],
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
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
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
        raise VerificationError(
            f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(
            f"{path.as_posix()} must contain a top-level object")
    return data


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


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields if field in row and row[field] in ("", None)
    ]
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
        raise VerificationError(
            f"{CONTRACT_MANIFEST.as_posix()} must contain a rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} rows[{index}] must be an object"
            )
        parsed_rows.append(row)
    return parsed_rows


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        matches = sorted({
            match.group(1)
            for match in pattern.finditer(text) if match.lastindex
        })
        if matches:
            errors.append(
                f"{path.as_posix()} contains forbidden release evidence marker: {', '.join(matches)}"
            )
            continue
        if pattern.search(text):
            errors.append(
                f"{path.as_posix()} contains forbidden release evidence marker: {label}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(FORBIDDEN_FIELD_NAMES & set(value))
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


def validate_ref(ref: str, row_name: str, field: str) -> str:
    if not ref:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    if ref.startswith(ALLOWED_EXTERNAL_REF_ROOT):
        return ref
    relative_path = Path(ref)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} {field} ref escapes allowed roots: {ref}")
    try:
        relative_path.relative_to(DEFAULT_OUTPUT_DIR)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} {field} ref must stay under {DEFAULT_OUTPUT_DIR.as_posix()} or {ALLOWED_EXTERNAL_REF_ROOT}: {ref}"
        ) from error
    return ref


def validate_ref_list(row: dict[str, Any], field: str, row_name: str,
                      require_nonempty: bool) -> list[str]:
    values = require_list(row, field, row_name)
    if require_nonempty and not values:
        raise VerificationError(f"{row_name} {field} must be non-empty")
    refs: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str):
            raise VerificationError(
                f"{row_name} {field}[{index}] must be a string")
        refs.append(validate_ref(value, row_name, f"{field}[{index}]"))
    return refs


def resolved_output_dir(root: Path, output_dir: Path) -> tuple[Path, Path]:
    resolved_root = root.resolve(strict=False)
    expected_root = resolved_root / DEFAULT_OUTPUT_DIR
    if output_dir.is_absolute():
        candidate = output_dir
    else:
        if ".." in output_dir.parts:
            raise VerificationError(
                f"--output-dir must be contained by {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
            )
        candidate = resolved_root / output_dir
    full_output_dir = candidate.resolve(strict=False)
    try:
        relative_output_dir = full_output_dir.relative_to(resolved_root)
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        ) from error
    return relative_output_dir, full_output_dir


def source_ref_row_matches(data: Any, collection_names: list[str],
                           row_id: str) -> list[str]:
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
                if isinstance(external_input,
                              dict) and external_input.get("id") == row_id:
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
    if relative_path not in PHASE20_SOURCE_REF_MANIFEST_PATHS:
        raise VerificationError(
            f"{row_name} source ref path is not an approved Phase 20 source manifest: {source_ref}"
        )
    data = load_json(root, relative_path)
    collection_names = PHASE20_SOURCE_REF_ROW_COLLECTIONS.get(
        relative_path.as_posix(), [])
    if not collection_names:
        raise VerificationError(
            f"{row_name} source ref path has no approved row collections: {source_ref}"
        )
    matches = source_ref_row_matches(data, collection_names, row_id)
    if not matches:
        raise VerificationError(
            f"{row_name} source ref row not found in approved row collections: {source_ref}"
        )
    if len(matches) > 1:
        raise VerificationError(
            f"{row_name} source ref row matches multiple approved rows: {source_ref}"
        )


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
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    if contract.get("required_artifact_outputs") != REQUIRED_ARTIFACT_OUTPUTS:
        actual_outputs = contract.get("required_artifact_outputs")
        actual_set = set(actual_outputs) if isinstance(actual_outputs,
                                                       list) else set()
        for missing in REQUIRED_ARTIFACT_OUTPUTS:
            if missing not in actual_set:
                errors.append(f"missing required artifact output: {missing}")
        if not errors:
            errors.append(
                "required_artifact_outputs order must match Phase 20 contract")
    if contract.get("proof_class_vocabulary") != PROOF_CLASS_VOCABULARY:
        errors.append(
            "proof_class_vocabulary does not match Phase 20 vocabulary")
    if contract.get("status_vocabulary") != STATUS_VOCABULARY:
        errors.append("status_vocabulary does not match Phase 20 vocabulary")
    if contract.get("mismatch_class_vocabulary") != MISMATCH_CLASS_VOCABULARY:
        errors.append(
            "mismatch_class_vocabulary does not match Phase 20 vocabulary")
    try:
        rows = contract_rows(contract)
    except VerificationError as error:
        errors.append(str(error))
        rows = []
    validate_rows(root, rows, errors)
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def validate_rows(root: Path, rows: list[dict[str, Any]],
                  errors: list[str]) -> None:
    row_ids = [str(row.get("id")) for row in rows]
    if row_ids != REQUIRED_ROW_IDS:
        for missing in REQUIRED_ROW_IDS:
            if missing not in row_ids:
                errors.append(f"missing required release row: {missing}")
        duplicates = sorted(
            {row_id
             for row_id in row_ids if row_ids.count(row_id) > 1})
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
        errors.append(
            f"{row_name} uses unknown requirement IDs: {sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)}"
        )
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
        errors.append(
            f"{row_name} proof_class_allowed contains unknown proof classes")
    for source_ref in row["source_contract_refs"]:
        if not isinstance(source_ref, str):
            continue
        try:
            resolve_source_ref(root, source_ref, row_name)
        except VerificationError as error:
            errors.append(str(error))
    default_status = require_string(row, "default_status", row_name)
    if default_status not in STATUS_VOCABULARY:
        errors.append(
            f"{row_name} default_status is invalid: {default_status}")
    if default_status == "passed":
        errors.append(
            f"{row_name} default_status cannot be passed without approved release input"
        )
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
        relative_output_dir, full_output_dir = resolved_output_dir(
            root, maybe_output_dir)
        if full_output_dir.exists():
            for full_path in sorted(path for path in full_output_dir.rglob("*")
                                    if path.is_file()):
                relative_path = full_path.relative_to(root)
                try:
                    text = full_path.read_text(encoding="utf-8")
                    reject_forbidden_text(relative_path, text)
                    reject_forbidden_field_names(json.loads(text),
                                                 relative_path.as_posix())
                except json.JSONDecodeError:
                    continue
                except VerificationError as error:
                    errors.append(str(error))
        validate_ref(relative_output_dir.as_posix(), "generated output",
                     "output_dir")
    if errors:
        raise VerificationError("\n".join(errors))
