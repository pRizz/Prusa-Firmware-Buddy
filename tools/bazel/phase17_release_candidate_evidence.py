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
PHASE = "17-release-candidate-artifact-and-signing-gates"
PHASE_LIFECYCLE_ID = "17-2026-06-19T13-57-17"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase17_release_candidate_evidence_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase17")
REQUIRED_REQUIREMENT_IDS = {"REL-01", "REL-02", "REL-03"}
REQUIRED_ROW_IDS = {
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
}
REQUIRED_ARTIFACT_SURFACES = {
    ".bin",
    ".bbf",
    ".dfu",
    "map/provenance",
    "resource",
    "language",
    "wui",
    "esp",
    "mmu",
    "dwarf",
    "modularbed",
    "xbuddy-extension",
    "package-manifest",
    "signing-key-identity",
    "build-input-identity",
    "artifact-retention",
    "reference-comparison",
    "contract-traceability-redaction",
}
REQUIRED_RELEASE_PRODUCTS = {"COREONE", "MINI", "MK4", "MK3.5", "XL", "iX", "XL_DEV_KIT"}
REQUIRED_RELEASE_BOARDS = {
    "BUDDY",
    "XBUDDY",
    "XLBUDDY",
    "XL_DEV_KIT_XLB",
    "DWARF",
    "MODULARBED",
    "XBUDDY_EXTENSION",
}
RELEASE_WORKFLOW_IDENTITIES = {
    "phase17_release_candidate_artifacts": {
        "bazel_label": "//tools/bazel:phase17_release_candidate_artifacts",
        "release_command": "bazel build //tools/bazel:phase17_release_candidate_artifacts",
        "release_run_required": True,
    }
}
LOCAL_SMOKE_WORKFLOW_IDENTITIES = {
    "//tools/bazel:representative_release_artifacts",
    "//tools/bazel:representative_package_surface_smoke",
    "//tools/bazel:representative_reference_format_artifacts",
    "//tools/bazel:phase3_verify",
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
REQUIRED_ARTIFACT_KINDS = {
    "machine-readable-run-manifest",
    "normalized-release-results",
    "redacted-signing-provenance-summary",
    "comparison-classification-report",
    "source-contract-snapshot",
    "release-operator-evidence-input",
    "release-log-reference",
    "external-artifact-reference",
}
SOURCE_REF_MANIFESTS = [
    "tools/bazel/manifests/representative_products.json",
    "tools/bazel/manifests/phase7_generated_outputs.json",
    "tools/bazel/manifests/phase7_storage_media.json",
    "tools/bazel/manifests/phase10_auxiliary_build_update.json",
    "tools/bazel/manifests/phase10_auxiliary_controllers.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json",
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json",
]
REQUIRED_ROW_FIELDS = [
    "id",
    "title",
    "requirement_ids",
    "artifact_surface",
    "product_profile",
    "source_contract_refs",
    "source_doc_refs",
    "proof_scope",
    "required_input_kind",
    "bazel_label",
    "release_command",
    "artifact_outputs",
    "release_run_required",
    "expected_artifact_path",
    "retained_artifact_kind",
    "allowed_statuses",
    "release_metadata_required",
    "signing_metadata_required",
    "provenance_metadata_required",
    "comparison_metadata_required",
    "mismatch_class",
    "mismatch_reason_required",
    "owner_phase",
    "residual_cutover_gates",
    "unsupported_claims",
    "redaction_required",
]
REQUIRED_RELEASE_EVIDENCE_FIELDS = [
    "release_run_id",
    "artifact_surface",
    "product_profile",
    "build_input_identity",
    "operator",
    "timestamp",
    "result",
    "evidence_type",
    "bazel_label",
    "release_command",
    "artifact_outputs",
    "release_run_required",
    "signing_mode",
    "key_identity_ref",
    "artifact_digest_sha256",
    "artifact_refs",
    "provenance_refs",
    "comparison_refs",
    "retention_path",
    "verification_outcome",
    "mismatch_class",
    "mismatch_reason",
    "owner_phase",
    "residual_risk",
    "redaction_summary",
]
APPROVED_RELEASE_EVIDENCE_TYPES = {
    "approved-release-run",
    "approved-release-signing-evidence",
    "approved-release-comparison",
}
FORBIDDEN_FIELD_NAMES = {
    "private_key",
    "signing_key_value",
    "certificate_private_material",
    "raw_key_bytes",
    "certificate_pem",
    "certificate_bytes",
    "firmware_payload",
    "bbf_payload",
    "dfu_payload",
    "token",
    "password",
    "secret",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-private-material", re.compile(r"certificate[_ -]?private[_ -]?material", re.IGNORECASE)),
    (
        "signing-key-value",
        re.compile(r"\b(signing_key_value|private_key|raw_key_bytes|certificate_pem|certificate_bytes)\b", re.IGNORECASE),
    ),
    (
        "payload-marker",
        re.compile(r"\b(firmware_payload|raw_firmware_payload|bbf_payload|dfu_payload)\b|\.(bin|bbf|dfu) payload\b", re.IGNORECASE),
    ),
    (
        "credential-assignment",
        re.compile(
            r"(?:^|[\s,{])['\"]?([A-Za-z0-9_-]*(?:token|password|secret)[A-Za-z0-9_-]*)['\"]?\s*[:=]\s*['\"]?[^'\"\s,}]+",
            re.IGNORECASE,
        ),
    ),
)
OVERCLAIM_STRINGS = {
    "release readiness proven",
    "release-candidate passed locally",
    "production signing proof complete",
    "signing proof complete",
    "retained-code accepted by maintainer",
    "reference demotion approved",
    "final cutover complete",
}


class VerificationError(Exception):
    pass


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


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_dict(row: dict[str, Any], field: str, row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and row[field] in ("", None)]
    if missing or empty:
        details = []
        if missing:
            details.append("missing required fields: " + ", ".join(missing))
        if empty:
            details.append("empty required fields: " + ", ".join(empty))
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_repo_relative_under(path_value: str | Path, output_root: str | Path, row_name: str) -> Path:
    relative_path = Path(path_value)
    expected_root = Path(output_root)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} path must be repo-relative and cannot traverse: {path_value}")
    try:
        relative_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"{row_name} path must stay under {expected_root.as_posix()}: {relative_path.as_posix()}") from error
    return relative_path


def contained_output_dir(root: Path, output_dir: str | Path) -> Path:
    relative_path = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    full_output_dir = (root / relative_path).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_path.as_posix()}") from error
    return full_output_dir


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            errors.append(f"{path.as_posix()} contains forbidden evidence marker: {label}")
    lowered = text.lower()
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase in lowered:
            errors.append(f"{path.as_posix()} contains non-local evidence overclaim: {phrase}")
    if errors:
        raise VerificationError("\n".join(errors))


def contract_rows(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = contract.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} must contain a rows list")
    parsed: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} rows[{index}] must be an object")
        parsed.append(row)
    return parsed


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


def validate_doc_ref(root: Path, source_doc_ref: str, row_name: str) -> None:
    if "#" not in source_doc_ref:
        raise VerificationError(f"{row_name} source doc ref must use file#anchor: {source_doc_ref}")
    path_text, anchor = source_doc_ref.split("#", 1)
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} source doc ref must be repo-relative: {source_doc_ref}")
    text = read_text(root, relative_path)
    if anchor and anchor.lower() not in text.lower():
        raise VerificationError(f"{row_name} source doc ref anchor not found: {source_doc_ref}")


def validate_release_input_schema(contract: dict[str, Any], errors: list[str]) -> None:
    try:
        schema = require_dict(contract, "release_input_schema", "contract")
        required_fields = require_list_of_strings(schema, "required_fields", "release_input_schema")
        artifact_ref_root = require_string(schema, "artifact_ref_root", "release_input_schema")
    except VerificationError as error:
        errors.append(str(error))
        return
    if required_fields != REQUIRED_RELEASE_EVIDENCE_FIELDS:
        errors.append("release_input_schema required_fields must match Phase 17 release evidence metadata fields")
    if artifact_ref_root != DEFAULT_OUTPUT_DIR.as_posix():
        errors.append(f"release_input_schema artifact_ref_root must be {DEFAULT_OUTPUT_DIR.as_posix()}")


def validate_workflow_identities(contract: dict[str, Any], errors: list[str]) -> None:
    try:
        identities = require_dict(contract, "release_workflow_identities", "contract")
        local_smoke = require_dict(contract, "local_smoke_workflow_identities", "contract")
        release_identity = require_dict(identities, "phase17_release_candidate_artifacts", "release_workflow_identities")
    except VerificationError as error:
        errors.append(str(error))
        return
    expected = RELEASE_WORKFLOW_IDENTITIES["phase17_release_candidate_artifacts"]
    for field, value in expected.items():
        if release_identity.get(field) != value:
            errors.append(f"phase17_release_candidate_artifacts {field} must be {value!r}")
    outputs = release_identity.get("artifact_outputs")
    if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
        errors.append("phase17_release_candidate_artifacts artifact_outputs must be a list of strings")
    for label in sorted(LOCAL_SMOKE_WORKFLOW_IDENTITIES):
        entry = local_smoke.get(label)
        if not isinstance(entry, dict):
            errors.append(f"missing local smoke workflow identity: {label}")
            continue
        if entry.get("local_smoke_only") is not True or entry.get("release_run_required") is not False:
            errors.append(f"{label} must be local_smoke_only with release_run_required false")


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase17_release_candidate_evidence_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase17-release-candidate-evidence",
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    try:
        statuses = require_list_of_strings(contract, "status_vocabulary", "contract")
        mismatch_classes = require_list_of_strings(contract, "mismatch_class_vocabulary", "contract")
        artifact_kinds = set(require_list_of_strings(contract, "required_artifact_kinds", "contract"))
        products = set(require_list_of_strings(contract, "supported_release_products", "contract"))
        boards = set(require_list_of_strings(contract, "supported_release_boards", "contract"))
        rows = contract_rows(contract)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if statuses != STATUS_VOCABULARY:
        errors.append("status_vocabulary does not match the Phase 17 vocabulary")
    if mismatch_classes != MISMATCH_CLASS_VOCABULARY:
        errors.append("mismatch_class_vocabulary does not match the Phase 17 vocabulary")
    for missing in sorted(REQUIRED_ARTIFACT_KINDS - artifact_kinds):
        errors.append(f"missing required artifact kind: {missing}")
    for missing in sorted(REQUIRED_RELEASE_PRODUCTS - products):
        errors.append(f"missing required supported release product: {missing}")
    for missing in sorted(REQUIRED_RELEASE_BOARDS - boards):
        errors.append(f"missing required supported release board: {missing}")
    validate_release_input_schema(contract, errors)
    validate_workflow_identities(contract, errors)
    validate_rows(root, rows, artifact_kinds, errors)
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def validate_rows(root: Path, rows: list[dict[str, Any]], artifact_kinds: set[str], errors: list[str]) -> None:
    row_ids = [str(row.get("id")) for row in rows]
    for missing in sorted(REQUIRED_ROW_IDS - set(row_ids)):
        errors.append("missing required release row: " + missing)
    if len(row_ids) != len(set(row_ids)):
        errors.append("duplicate release row IDs are not allowed")
    covered_requirements: set[str] = set()
    covered_surfaces: set[str] = set()
    for row in rows:
        row_name = str(row.get("id", "unknown row"))
        try:
            validate_row_shape(root, row, row_name, artifact_kinds)
            covered_requirements.update(row["requirement_ids"])
            covered_surfaces.add(str(row["artifact_surface"]))
        except VerificationError as error:
            errors.append(str(error))
    for missing in sorted(REQUIRED_REQUIREMENT_IDS - covered_requirements):
        errors.append("missing REL requirement coverage: " + missing)
    for missing in sorted(REQUIRED_ARTIFACT_SURFACES - covered_surfaces):
        errors.append("missing required artifact surface coverage: " + missing)


def validate_row_shape(root: Path, row: dict[str, Any], row_name: str, artifact_kinds: set[str]) -> None:
    errors: list[str] = []
    try:
        require_fields(row, REQUIRED_ROW_FIELDS, row_name)
        requirement_ids = set(require_list_of_strings(row, "requirement_ids", row_name))
        source_refs = require_list_of_strings(row, "source_contract_refs", row_name)
        source_doc_refs = require_list_of_strings(row, "source_doc_refs", row_name)
        allowed_statuses = set(require_list_of_strings(row, "allowed_statuses", row_name))
        fallback_status = "source-contract-passed" if row.get("proof_scope") == "source-contract" else "pending-release-input"
        default_status = str(row.get("default_status", fallback_status))
        artifact_outputs = require_list_of_strings(row, "artifact_outputs", row_name)
        retained_artifact_kind = require_string(row, "retained_artifact_kind", row_name)
        artifact_path = require_string(row, "expected_artifact_path", row_name)
        mismatch_class = require_string(row, "mismatch_class", row_name)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    unknown_requirements = sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)
    if unknown_requirements:
        errors.append(f"{row_name} uses unknown requirement IDs: {', '.join(unknown_requirements)}")
    for source_ref in source_refs:
        try:
            resolve_source_ref(root, source_ref, row_name)
        except VerificationError as error:
            errors.append(str(error))
    for doc_ref in source_doc_refs:
        try:
            validate_doc_ref(root, doc_ref, row_name)
        except VerificationError as error:
            errors.append(str(error))
    try:
        require_repo_relative_under(artifact_path, DEFAULT_OUTPUT_DIR, row_name)
    except VerificationError as error:
        errors.append(str(error))
    if retained_artifact_kind not in artifact_kinds:
        errors.append(f"{row_name} retained_artifact_kind is not declared: {retained_artifact_kind}")
    if not allowed_statuses <= set(STATUS_VOCABULARY):
        errors.append(f"{row_name} allowed_statuses contains unknown statuses")
    if default_status not in STATUS_VOCABULARY:
        errors.append(f"{row_name} default_status is invalid: {default_status}")
    elif default_status not in allowed_statuses:
        errors.append(f"{row_name} default_status {default_status} is not allowed by allowed_statuses")
    if mismatch_class not in MISMATCH_CLASS_VOCABULARY:
        errors.append(f"{row_name} mismatch_class is invalid: {mismatch_class}")
    if default_status == "passed" and row.get("proof_scope") != "source-contract":
        errors.append(f"{row_name} default_status cannot be passed without approved release evidence")
    if row.get("release_run_required") is True:
        expected = RELEASE_WORKFLOW_IDENTITIES["phase17_release_candidate_artifacts"]
        if row.get("bazel_label") != expected["bazel_label"]:
            errors.append(f"{row_name} bazel_label must be {expected['bazel_label']!r}, not {row.get('bazel_label')!r}")
        if row.get("release_command") != expected["release_command"]:
            errors.append(f"{row_name} release_command must be {expected['release_command']!r}")
        if row.get("bazel_label") in LOCAL_SMOKE_WORKFLOW_IDENTITIES:
            errors.append(f"{row_name} representative smoke label cannot satisfy release_run_required")
    if row.get("release_run_required") is not True and row.get("release_run_required") is not False:
        errors.append(f"{row_name} release_run_required must be boolean")
    if not artifact_outputs:
        errors.append(f"{row_name} artifact_outputs must not be empty")
    for list_field in [
        "release_metadata_required",
        "signing_metadata_required",
        "provenance_metadata_required",
        "comparison_metadata_required",
        "residual_cutover_gates",
        "unsupported_claims",
    ]:
        if not isinstance(row.get(list_field), list):
            errors.append(f"{row_name} {list_field} must be a list")
    if row.get("redaction_required") is not True:
        errors.append(f"{row_name} redaction_required must be true")
    if errors:
        raise VerificationError("\n".join(errors))


def load_release_evidence_path(root: Path, path: str | None) -> tuple[Path | None, list[Any] | None]:
    if not path:
        return None, None
    evidence_path = Path(path)
    full_path = evidence_path if evidence_path.is_absolute() else root / evidence_path
    if not full_path.exists():
        raise VerificationError(f"release evidence file does not exist: {path}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(evidence_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"release evidence is not valid JSON: {error}") from error
    if isinstance(data, list):
        return evidence_path, data
    if isinstance(data, dict) and isinstance(data.get("evidence_rows"), list):
        return evidence_path, data["evidence_rows"]
    raise VerificationError("release evidence must contain an evidence_rows list or be a top-level list")


def validate_refs(refs: Any, row_name: str, field: str, require_nonempty: bool = True) -> list[str]:
    if not isinstance(refs, list) or (require_nonempty and not refs):
        raise VerificationError(f"{row_name} {field} must be a non-empty list")
    parsed: list[str] = []
    for index, ref in enumerate(refs):
        ref_name = f"{row_name} {field}[{index}]"
        if not isinstance(ref, str) or not ref:
            raise VerificationError(f"{ref_name} must be a non-empty string")
        if ref.startswith("external://phase17/"):
            parsed.append(ref)
            continue
        if ref.startswith("artifact://") or ref.startswith("external://"):
            raise VerificationError(f"{ref_name} must use repo-relative path or external://phase17/... reference")
        require_repo_relative_under(ref, DEFAULT_OUTPUT_DIR, ref_name)
        parsed.append(ref)
    return parsed


def require_iso_8601_utc(row: dict[str, Any], field: str, row_name: str) -> None:
    timestamp_text = require_string(row, field, row_name)
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(f"{row_name} {field} must be ISO-8601 UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise VerificationError(f"{row_name} {field} must be ISO-8601 UTC")


def matching_contract_row(rows: list[dict[str, Any]], evidence_row: dict[str, Any], row_name: str) -> dict[str, Any]:
    artifact_surface = evidence_row.get("artifact_surface")
    product_profile = evidence_row.get("product_profile")
    matches = [
        row for row in rows
        if row.get("artifact_surface") == artifact_surface and row.get("product_profile") == product_profile
    ]
    if len(matches) != 1:
        raise VerificationError(f"{row_name} does not match exactly one contract row")
    return matches[0]


def validated_release_rows(root: Path, contract: dict[str, Any], path: str | None) -> dict[str, dict[str, Any]]:
    evidence_path, rows = load_release_evidence_path(root, path)
    if rows is None:
        return {}
    contract_rows_by_match = contract_rows(contract)
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"release evidence row {index}"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        try:
            require_fields(row, REQUIRED_RELEASE_EVIDENCE_FIELDS, row_name)
            forbidden_keys = sorted(FORBIDDEN_FIELD_NAMES & set(row))
            if forbidden_keys:
                raise VerificationError(f"{row_name} contains forbidden evidence fields: {', '.join(forbidden_keys)}")
            reject_forbidden_text(evidence_path or Path("release-evidence"), json.dumps(row, sort_keys=True))
            require_iso_8601_utc(row, "timestamp", row_name)
            contract_row = matching_contract_row(contract_rows_by_match, row, row_name)
            contract_row_id = str(contract_row["id"])
            if contract_row_id in parsed_rows:
                raise VerificationError(f"{row_name} duplicates release evidence for {contract_row_id}")
            validate_release_row_against_contract(row, contract_row, row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue
        parsed_rows[contract_row_id] = dict(row)
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def validate_release_row_against_contract(row: dict[str, Any], contract_row: dict[str, Any], row_name: str) -> None:
    errors: list[str] = []
    for field in ["bazel_label", "release_command", "artifact_outputs", "release_run_required"]:
        if row.get(field) != contract_row.get(field):
            errors.append(f"{row_name} {field} {row.get(field)!r} does not match contract row {contract_row['id']}")
    result = require_string(row, "result", row_name)
    allowed_statuses = set(
        require_list_of_strings(contract_row, "allowed_statuses", str(contract_row["id"]))
    )
    if result not in STATUS_VOCABULARY:
        errors.append(f"{row_name} uses unsupported result: {result}")
    elif result not in allowed_statuses:
        errors.append(f"{row_name} result {result} is not allowed for {contract_row['id']}")
    evidence_type = require_string(row, "evidence_type", row_name)
    digest = require_string(row, "artifact_digest_sha256", row_name)
    if digest and not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append(f"{row_name} artifact_digest_sha256 must be lowercase SHA-256 hex")
    if not digest and contract_row.get("proof_scope") != "source-contract":
        errors.append(f"{row_name} artifact_digest_sha256 is required for release evidence")
    for field in ["artifact_refs", "provenance_refs", "comparison_refs"]:
        try:
            validate_refs(row[field], row_name, field, require_nonempty=result == "passed")
        except VerificationError as error:
            errors.append(str(error))
    if row.get("retention_path", "").startswith("external://"):
        if not str(row["retention_path"]).startswith("external://phase17/"):
            errors.append(f"{row_name} retention_path must use external://phase17/... reference")
    else:
        try:
            require_repo_relative_under(str(row["retention_path"]), DEFAULT_OUTPUT_DIR, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if row.get("mismatch_class") not in MISMATCH_CLASS_VOCABULARY:
        errors.append(f"{row_name} mismatch_class is invalid: {row.get('mismatch_class')}")
    if result == "passed" and contract_row.get("release_run_required") is True:
        expected = RELEASE_WORKFLOW_IDENTITIES["phase17_release_candidate_artifacts"]
        if evidence_type not in APPROVED_RELEASE_EVIDENCE_TYPES:
            errors.append(f"{row_name} passed release evidence must use approved-release evidence_type")
        if row.get("bazel_label") != expected["bazel_label"]:
            errors.append(f"{row_name} passed release evidence must use {expected['bazel_label']}")
        if row.get("release_command") != expected["release_command"]:
            errors.append(f"{row_name} passed release evidence must use {expected['release_command']}")
        if not all(str(row.get(field, "")) for field in ["key_identity_ref", "verification_outcome", "mismatch_reason", "owner_phase", "residual_risk"]):
            errors.append(f"{row_name} passed release evidence is missing required verification metadata")
    if row.get("bazel_label") in LOCAL_SMOKE_WORKFLOW_IDENTITIES and contract_row.get("release_run_required") is True:
        errors.append(f"{row_name} representative smoke labels cannot satisfy production release proof")
    if errors:
        raise VerificationError("\n".join(errors))


def default_status_for(row: dict[str, Any]) -> str:
    if row.get("proof_scope") == "source-contract":
        return "source-contract-passed"
    return str(row.get("default_status", "pending-release-input"))


def result_row(contract_row: dict[str, Any], maybe_release_row: dict[str, Any] | None) -> dict[str, Any]:
    status = default_status_for(contract_row)
    artifact_refs = [str(contract_row["expected_artifact_path"])]
    signing_mode = "external-release-key" if contract_row["signing_metadata_required"] else "not-applicable"
    row = {
        "artifact_digest_sha256": "",
        "artifact_refs": artifact_refs,
        "artifact_outputs": contract_row["artifact_outputs"],
        "artifact_surface": contract_row["artifact_surface"],
        "bazel_label": contract_row["bazel_label"],
        "comparison_refs": [],
        "id": contract_row["id"],
        "key_identity_ref": "",
        "mismatch_class": contract_row["mismatch_class"],
        "mismatch_reason": "Awaiting approved release comparison metadata.",
        "owner_phase": contract_row["owner_phase"],
        "product_profile": contract_row["product_profile"],
        "proof_scope": contract_row["proof_scope"],
        "provenance_refs": [],
        "release_command": contract_row["release_command"],
        "release_run_required": contract_row["release_run_required"],
        "residual_risk": "Awaiting approved release-run evidence." if status != "source-contract-passed" else "Source contract boundary only.",
        "retention_path": str(contract_row["expected_artifact_path"]),
        "signing_mode": signing_mode,
        "status": status,
        "verification_outcome": "pending-release-input",
    }
    if maybe_release_row is not None:
        row.update({
            "artifact_digest_sha256": maybe_release_row["artifact_digest_sha256"],
            "artifact_refs": maybe_release_row["artifact_refs"],
            "comparison_refs": maybe_release_row["comparison_refs"],
            "key_identity_ref": maybe_release_row["key_identity_ref"],
            "mismatch_class": maybe_release_row["mismatch_class"],
            "mismatch_reason": maybe_release_row["mismatch_reason"],
            "provenance_refs": maybe_release_row["provenance_refs"],
            "residual_risk": maybe_release_row["residual_risk"],
            "retention_path": maybe_release_row["retention_path"],
            "signing_mode": maybe_release_row["signing_mode"],
            "status": maybe_release_row["result"],
            "verification_outcome": maybe_release_row["verification_outcome"],
        })
    return row


def write_json(root: Path, relative_path: Path, data: dict[str, Any]) -> None:
    full_path = root / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_log(root: Path, output_dir: Path, row: dict[str, Any]) -> None:
    log_path = output_dir / "logs" / f"{row['id']}.log"
    lines = [
        f"row_id={row['id']}",
        f"status={row['status']}",
        f"proof_scope={row['proof_scope']}",
        f"artifact_surface={row['artifact_surface']}",
        f"bazel_label={row['bazel_label']}",
        f"release_run_required={str(row['release_run_required']).lower()}",
        f"artifact_refs={','.join(row['artifact_refs'])}",
        f"residual_risk={row['residual_risk']}",
    ]
    full_path = root / log_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quick_artifacts(root: Path, contract: dict[str, Any], output_dir: Path, release_rows: dict[str, dict[str, Any]]) -> None:
    relative_output_dir = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    full_output_dir = contained_output_dir(root, relative_output_dir)
    if full_output_dir.exists():
        shutil.rmtree(full_output_dir)
    (full_output_dir / "logs").mkdir(parents=True)
    (full_output_dir / "source-contract-snapshots").mkdir(parents=True)
    rows = [result_row(row, release_rows.get(str(row["id"]))) for row in contract_rows(contract)]
    for row in rows:
        write_log(root, relative_output_dir, row)
    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    snapshot_path = relative_output_dir / "source-contract-snapshots" / CONTRACT_MANIFEST.name
    run_manifest = {
        "artifact_name": contract["artifact_name"],
        "command_mode": "quick",
        "output_root": relative_output_dir.as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "release_inputs_supplied": bool(release_rows),
        "requirement_coverage": sorted(REQUIRED_REQUIREMENT_IDS),
        "row_summaries": [
            {key: row[key] for key in ["id", "artifact_surface", "proof_scope", "status", "bazel_label", "release_run_required"]}
            for row in rows
        ],
        "source_contract_snapshot_path": snapshot_path.as_posix(),
        "status_counts": status_counts,
    }
    normalized = {"phase": PHASE, "phase_lifecycle_id": PHASE_LIFECYCLE_ID, "results": rows}
    signing_summary = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "release_inputs_supplied": bool(release_rows),
        "rows": [
            {key: row[key] for key in ["id", "status", "signing_mode", "key_identity_ref", "artifact_digest_sha256", "retention_path", "verification_outcome"]}
            for row in rows
            if "REL-02" in next(contract_row["requirement_ids"] for contract_row in contract_rows(contract) if contract_row["id"] == row["id"])
        ],
    }
    comparison_report = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "comparisons": [
            {
                "artifact_refs": row["artifact_refs"],
                "artifact_surface": row["artifact_surface"],
                "mismatch_class": row["mismatch_class"],
                "mismatch_reason": row["mismatch_reason"],
                "normalized_fields_compared": [
                    "artifact-kind",
                    "product-profile",
                    "package-member-identities",
                    "signing-mode-name",
                    "provenance-metadata",
                ],
                "owner_phase": row["owner_phase"],
                "product_profile": row["product_profile"],
                "reference_source": "tools/bazel/manifests/phase11_reference_comparisons.json",
                "residual_risk": row["residual_risk"],
                "rust_bazel_surface": row["bazel_label"],
            }
            for row in rows
            if row["artifact_surface"] == "reference-comparison"
        ],
    }
    write_json(root, relative_output_dir / "run-manifest.json", run_manifest)
    write_json(root, relative_output_dir / "normalized-release-results.json", normalized)
    write_json(root, relative_output_dir / "redacted-signing-provenance-summary.json", signing_summary)
    write_json(root, relative_output_dir / "comparison-classification-report.json", comparison_report)
    write_json(root, relative_output_dir / "release-operator-evidence-input.json", {"evidence_rows": list(release_rows.values())})
    shutil.copy2(root / CONTRACT_MANIFEST, root / snapshot_path)


def iter_security_files(root: Path, output_dir: Path) -> list[Path]:
    relative_output_dir = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    full_output_dir = contained_output_dir(root, relative_output_dir)
    files = [CONTRACT_MANIFEST]
    if full_output_dir.exists():
        files.extend(sorted(path.relative_to(root) for path in full_output_dir.rglob("*") if path.is_file()))
    return files


def check_security(root: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    errors: list[str] = []
    check_contract(root)
    for relative_path in iter_security_files(root, output_dir):
        try:
            reject_forbidden_text(relative_path, read_text(root, relative_path))
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


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


def check_bazel_list_attr(block: str | None, location: str, attr: str, expected: list[str]) -> list[str]:
    if block is None:
        return [f"{location} missing required Bazel rule"]
    return missing_required_items(f"{location} {attr}", bazel_list_attr(block, attr), expected)


def check_bazel_string_attr(block: str | None, location: str, attr: str, expected: str) -> list[str]:
    if block is None:
        return [f"{location} missing required Bazel rule"]
    actual = bazel_string_attr(block, attr)
    if actual == expected:
        return []
    return [f"{location} {attr} must be {expected!r}, not {actual!r}"]


def check_release_candidate_artifact_target(text: str) -> list[str]:
    block = bazel_rule_block(text, "filegroup", "phase17_release_candidate_artifacts")
    if block is None:
        return ["tools/bazel/BUILD.bazel missing phase17_release_candidate_artifacts filegroup"]
    srcs = set(bazel_list_attr(block, "srcs"))
    forbidden_smoke_deps = {
        ":phase17_representative_release_smoke",
        ":representative_release_artifacts",
        "//tools/bazel:phase17_representative_release_smoke",
        "//tools/bazel:representative_release_artifacts",
    }
    wrapped_smoke = sorted(srcs & forbidden_smoke_deps)
    if not wrapped_smoke:
        return []
    return [
        "tools/bazel/BUILD.bazel phase17_release_candidate_artifacts cannot wrap local smoke dependencies: "
        + ", ".join(wrapped_smoke)
    ]


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


def check_tools_build_wiring(root: Path, manifest_srcs: list[str]) -> list[str]:
    path = Path("tools/bazel/BUILD.bazel")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors = check_release_candidate_artifact_target(text)
    smoke_block = bazel_rule_block(text, "filegroup", "phase17_representative_release_smoke")
    source_ref_block = bazel_rule_block(text, "filegroup", "phase17_source_ref_manifests")
    verify_block = bazel_rule_block(text, "shell_binary", "phase17_verify")
    verify_tests_block = bazel_rule_block(text, "shell_binary", "phase17_verify_tests")
    errors.extend(check_bazel_list_attr(
        smoke_block,
        "tools/bazel/BUILD.bazel filegroup phase17_representative_release_smoke",
        "srcs",
        [":representative_release_artifacts"],
    ))
    errors.extend(check_bazel_list_attr(
        source_ref_block,
        "tools/bazel/BUILD.bazel filegroup phase17_source_ref_manifests",
        "srcs",
        manifest_srcs,
    ))
    errors.extend(check_bazel_list_attr(
        verify_block,
        "tools/bazel/BUILD.bazel shell_binary phase17_verify",
        "data",
        [
            "phase17_release_candidate_evidence.py",
            "manifests/phase17_release_candidate_evidence_contract.json",
            ":phase17_release_candidate_artifacts",
            ":phase17_representative_release_smoke",
            ":phase17_source_ref_manifests",
            "//:phase17_release_candidate_evidence_docs",
            "//:phase11_cutover_evidence_docs",
        ],
    ))
    errors.extend(check_bazel_list_attr(
        verify_tests_block,
        "tools/bazel/BUILD.bazel shell_binary phase17_verify_tests",
        "data",
        [
            "phase17_release_candidate_evidence.py",
            "phase17_release_candidate_evidence_test.py",
            "manifests/phase17_release_candidate_evidence_contract.json",
            ":phase17_release_candidate_artifacts",
            ":phase17_representative_release_smoke",
            ":phase17_source_ref_manifests",
        ],
    ))
    return errors


def check_root_build_wiring(root: Path) -> list[str]:
    path = Path("BUILD.bazel")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors: list[str] = []
    docs_block = bazel_rule_block(text, "filegroup", "phase17_release_candidate_evidence_docs")
    if docs_block is None:
        errors.append("BUILD.bazel filegroup phase17_release_candidate_evidence_docs missing required Bazel rule")
    aliases = {
        "phase17_release_candidate_artifacts": "//tools/bazel:phase17_release_candidate_artifacts",
        "phase17_verify": "//tools/bazel:phase17_verify",
        "phase17_verify_tests": "//tools/bazel:phase17_verify_tests",
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
    verify_commands = shell_case_commands(text, "phase17_verify")
    verify_tests_commands = shell_case_commands(text, "phase17_verify_tests")
    if verify_commands is None:
        errors.append("tools/bazel/rust_workflow.sh phase17_verify case arm missing")
    else:
        errors.extend(missing_required_items(
            "tools/bazel/rust_workflow.sh phase17_verify case arm",
            verify_commands,
            [
                "python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only",
                "python3 tools/bazel/phase17_release_candidate_evidence.py --quick",
            ],
        ))
    if verify_tests_commands is None:
        errors.append("tools/bazel/rust_workflow.sh phase17_verify_tests case arm missing")
    else:
        errors.extend(missing_required_items(
            "tools/bazel/rust_workflow.sh phase17_verify_tests case arm",
            verify_tests_commands,
            ["python3 tools/bazel/phase17_release_candidate_evidence_test.py"],
        ))
    return errors


def check_just_wiring(root: Path) -> list[str]:
    path = Path("justfile")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors: list[str] = []
    verify_commands = just_recipe_commands(text, "phase17-verify")
    smoke_commands = just_recipe_commands(text, "phase17-release-artifacts-smoke")
    tests_line = "bazel run //tools/bazel:phase17_verify_tests"
    verify_line = "bazel run //tools/bazel:phase17_verify"
    if verify_commands is None:
        errors.append("justfile phase17-verify recipe missing")
    else:
        errors.extend(missing_required_items(
            "justfile phase17-verify recipe",
            verify_commands,
            [tests_line, verify_line],
        ))
        errors.extend(check_command_order("justfile phase17-verify recipe", verify_commands, tests_line, verify_line))
    if smoke_commands is None:
        errors.append("justfile phase17-release-artifacts-smoke recipe missing")
    else:
        errors.extend(missing_required_items(
            "justfile phase17-release-artifacts-smoke recipe",
            smoke_commands,
            ["bazel build //tools/bazel:phase17_representative_release_smoke"],
        ))
    return errors


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    manifest_srcs = [Path(path).relative_to("tools/bazel").as_posix() for path in SOURCE_REF_MANIFESTS]
    errors.extend(check_tools_build_wiring(root, manifest_srcs))
    errors.extend(check_root_build_wiring(root))
    errors.extend(check_rust_workflow_wiring(root))
    errors.extend(check_just_wiring(root))
    if errors:
        raise VerificationError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 17 release candidate evidence")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 17 evidence contract")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 17 contract and generated artifacts")
    parser.add_argument("--quick", action="store_true", help="write deterministic Phase 17 evidence artifacts")
    parser.add_argument("--release-evidence", help="optional release evidence JSON input")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel and just workflow wiring")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 17 evidence output directory")
    args = parser.parse_args()
    selected_modes = [args.contract_only, args.security_only, args.quick, args.wiring_only]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.release_evidence and not args.quick:
        parser.error("--release-evidence is only valid with --quick")
    output_dir = Path(args.output_dir)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 17 release candidate evidence contract passed")
        elif args.security_only:
            check_security(ROOT, output_dir)
            print("Phase 17 release candidate evidence security scan passed")
        elif args.quick:
            contract = check_contract(ROOT)
            release_rows = validated_release_rows(ROOT, contract, args.release_evidence)
            write_quick_artifacts(ROOT, contract, output_dir, release_rows)
            check_security(ROOT, output_dir)
            print(f"Phase 17 release candidate evidence written to {output_dir.as_posix()}")
        else:
            check_wiring(ROOT)
            print("Phase 17 release candidate evidence wiring passed")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
