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
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json")
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
REQUIRED_RELEASE_PRODUCTS = {
    "COREONE", "MINI", "MK4", "MK3.5", "XL", "iX", "XL_DEV_KIT"
}
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
        "release_command":
        "bazel build //tools/bazel:phase17_release_candidate_artifacts",
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
SOURCE_REF_MANIFEST_PATHS = {Path(path) for path in SOURCE_REF_MANIFESTS}
SOURCE_REF_ROW_COLLECTIONS = {
    "tools/bazel/manifests/representative_products.json": ["entries"],
    "tools/bazel/manifests/phase7_generated_outputs.json":
    ["generated_surfaces"],
    "tools/bazel/manifests/phase7_storage_media.json": ["storage_surfaces"],
    "tools/bazel/manifests/phase10_auxiliary_build_update.json":
    ["auxiliary_build_update_contracts"],
    "tools/bazel/manifests/phase10_auxiliary_controllers.json":
    ["auxiliary_controller_contracts"],
    "tools/bazel/manifests/phase11_cutover_readiness.json":
    ["cutover_criteria", "known_concern_dispositions"],
    "tools/bazel/manifests/phase11_parity_pyramid.json": ["parity_pyramid"],
    "tools/bazel/manifests/phase11_reference_comparisons.json":
    ["reference_comparisons"],
    "tools/bazel/manifests/phase11_requirement_evidence.json":
    ["requirement_evidence"],
    "tools/bazel/manifests/phase11_retained_code_justifications.json":
    ["retained_code_justifications"],
    "tools/bazel/manifests/phase13_ci_evidence_contract.json": ["gates"],
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json":
    ["scenarios"],
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json":
    ["scenarios"],
}
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
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-private-material",
     re.compile(r"certificate[_ -]?private[_ -]?material", re.IGNORECASE)),
    (
        "signing-key-value",
        re.compile(
            r"\b(signing_key_value|private_key|raw_key_bytes|certificate_pem|certificate_bytes)\b",
            re.IGNORECASE),
    ),
    (
        "payload-marker",
        re.compile(
            r"\b(firmware_payload|raw_firmware_payload|bbf_payload|dfu_payload)\b|\.(bin|bbf|dfu) payload\b",
            re.IGNORECASE),
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
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: str | Path) -> dict[str, Any]:
    relative_path = Path(path)
    try:
        data = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{relative_path.as_posix()} is not valid JSON: {error}"
        ) from error
    if not isinstance(data, dict):
        raise VerificationError(
            f"{relative_path.as_posix()} must contain a top-level object")
    return data


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_dict(row: dict[str, Any], field: str,
                 row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields if field in row and row[field] in ("", None)
    ]
    if missing or empty:
        details = []
        if missing:
            details.append("missing required fields: " + ", ".join(missing))
        if empty:
            details.append("empty required fields: " + ", ".join(empty))
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_repo_relative_under(path_value: str | Path,
                                output_root: str | Path,
                                row_name: str) -> Path:
    relative_path = Path(path_value)
    expected_root = Path(output_root)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} path must be repo-relative and cannot traverse: {path_value}"
        )
    try:
        relative_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} path must stay under {expected_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


def contained_output_dir(root: Path, output_dir: str | Path) -> Path:
    relative_path = require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR,
                                                "--output-dir")
    resolved_root = root.resolve(strict=False)
    expected_root = resolved_root / DEFAULT_OUTPUT_DIR
    full_output_dir = (resolved_root / relative_path).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return full_output_dir


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            errors.append(
                f"{path.as_posix()} contains forbidden evidence marker: {label}"
            )
    lowered = text.lower()
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase in lowered:
            errors.append(
                f"{path.as_posix()} contains non-local evidence overclaim: {phrase}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def contract_rows(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = contract.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(
            f"{CONTRACT_MANIFEST.as_posix()} must contain a rows list")
    parsed: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} rows[{index}] must be an object"
            )
        parsed.append(row)
    return parsed


def source_ref_row_matches(data: Any, collection_names: list[str],
                           row_id: str) -> list[str]:
    if not isinstance(data, dict):
        return []
    matches: list[str] = []
    for collection_name in collection_names:
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
    if relative_path not in SOURCE_REF_MANIFEST_PATHS:
        raise VerificationError(
            f"{row_name} source ref path is not an approved Phase 17 source manifest: {source_ref}"
        )
    data = load_json(root, relative_path)
    collection_names = SOURCE_REF_ROW_COLLECTIONS.get(relative_path.as_posix(),
                                                      [])
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


def validate_doc_ref(root: Path, source_doc_ref: str, row_name: str) -> None:
    if "#" not in source_doc_ref:
        raise VerificationError(
            f"{row_name} source doc ref must use file#anchor: {source_doc_ref}"
        )
    path_text, anchor = source_doc_ref.split("#", 1)
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} source doc ref must be repo-relative: {source_doc_ref}"
        )
    text = read_text(root, relative_path)
    if anchor and anchor.lower() not in text.lower():
        raise VerificationError(
            f"{row_name} source doc ref anchor not found: {source_doc_ref}")


def validate_release_input_schema(contract: dict[str, Any],
                                  errors: list[str]) -> None:
    try:
        schema = require_dict(contract, "release_input_schema", "contract")
        required_fields = require_list_of_strings(schema, "required_fields",
                                                  "release_input_schema")
        artifact_ref_root = require_string(schema, "artifact_ref_root",
                                           "release_input_schema")
    except VerificationError as error:
        errors.append(str(error))
        return
    if required_fields != REQUIRED_RELEASE_EVIDENCE_FIELDS:
        errors.append(
            "release_input_schema required_fields must match Phase 17 release evidence metadata fields"
        )
    if artifact_ref_root != DEFAULT_OUTPUT_DIR.as_posix():
        errors.append(
            f"release_input_schema artifact_ref_root must be {DEFAULT_OUTPUT_DIR.as_posix()}"
        )


def validate_workflow_identities(contract: dict[str, Any],
                                 errors: list[str]) -> None:
    try:
        identities = require_dict(contract, "release_workflow_identities",
                                  "contract")
        local_smoke = require_dict(contract, "local_smoke_workflow_identities",
                                   "contract")
        release_identity = require_dict(identities,
                                        "phase17_release_candidate_artifacts",
                                        "release_workflow_identities")
    except VerificationError as error:
        errors.append(str(error))
        return
    expected = RELEASE_WORKFLOW_IDENTITIES[
        "phase17_release_candidate_artifacts"]
    for field, value in expected.items():
        if release_identity.get(field) != value:
            errors.append(
                f"phase17_release_candidate_artifacts {field} must be {value!r}"
            )
    outputs = release_identity.get("artifact_outputs")
    if not isinstance(outputs, list) or not all(
            isinstance(item, str) for item in outputs):
        errors.append(
            "phase17_release_candidate_artifacts artifact_outputs must be a list of strings"
        )
    for label in sorted(LOCAL_SMOKE_WORKFLOW_IDENTITIES):
        entry = local_smoke.get(label)
        if not isinstance(entry, dict):
            errors.append(f"missing local smoke workflow identity: {label}")
            continue
        if entry.get("local_smoke_only") is not True or entry.get(
                "release_run_required") is not False:
            errors.append(
                f"{label} must be local_smoke_only with release_run_required false"
            )
