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
REQUIRED_COMPARISON_FIELDS = [
    "mismatch_class",
    "mismatch_reason",
    "owner_phase",
    "affected_artifact_surface",
    "residual_risk",
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
    if output_dir.is_absolute():
        full_output_dir = output_dir.resolve(strict=False)
        expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
        try:
            relative_output_dir = full_output_dir.relative_to(root.resolve(strict=False))
            full_output_dir.relative_to(expected_root)
        except ValueError as error:
            raise VerificationError(f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}") from error
        return relative_output_dir, full_output_dir
    if output_dir.is_absolute() or ".." in output_dir.parts:
        raise VerificationError(f"--output-dir must be contained by {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}")
    try:
        output_dir.relative_to(DEFAULT_OUTPUT_DIR)
    except ValueError as error:
        raise VerificationError(f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}") from error
    return output_dir, root / output_dir


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
    validate_rows(rows, errors)
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def validate_rows(rows: list[dict[str, Any]], errors: list[str]) -> None:
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
            validate_row(row, row_name)
            covered_requirements.update(row["requirement_ids"])
        except VerificationError as error:
            errors.append(str(error))
    for missing in sorted(REQUIRED_REQUIREMENT_IDS - covered_requirements):
        errors.append(f"missing REL requirement coverage: {missing}")


def validate_row(row: dict[str, Any], row_name: str) -> None:
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
    default_status = require_string(row, "default_status", row_name)
    if default_status not in STATUS_VOCABULARY:
        errors.append(f"{row_name} default_status is invalid: {default_status}")
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
    for field in REQUIRED_COMPARISON_FIELDS:
        if status == "passed" and field not in row:
            errors.append(f"{row_name} missing required comparison metadata: {field}")
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
    if errors:
        raise VerificationError("\n".join(errors))


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
        "subject_digests": [],
        "build_input_identity": "",
        "key_identity_ref": "",
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
        "subject_digests",
        "build_input_identity",
        "key_identity_ref",
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
                "key_identity_ref": row["key_identity_ref"],
                "subject_digests": row["subject_digests"],
                "retention_refs": row["retention_refs"],
                "verification_outcome": row["verification_outcome"],
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 20 release candidate artifacts")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 20 contract")
    parser.add_argument("--security-only", action="store_true", help="scan checked-in Phase 20 contract/template files")
    parser.add_argument("--quick", action="store_true", help="write deterministic Phase 20 quick artifacts")
    parser.add_argument("--release-input", help="optional approved release input JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 20 evidence output directory")
    args = parser.parse_args()
    selected_modes = [args.contract_only, args.security_only, args.quick]
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
