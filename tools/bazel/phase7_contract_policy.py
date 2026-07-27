#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "07-persistence-storage-and-resource-compatibility"
PHASE_LIFECYCLE_ID = "7-2026-06-06T04-24-25"

CONFIG_MANIFEST = Path("tools/bazel/manifests/phase7_config_store.json")
STORAGE_MANIFEST = Path("tools/bazel/manifests/phase7_storage_media.json")
RESOURCES_MANIFEST = Path("tools/bazel/manifests/phase7_resources.json")
GENERATED_MANIFEST = Path(
    "tools/bazel/manifests/phase7_generated_outputs.json")
CONCERN_MANIFEST = Path(
    "tools/bazel/manifests/phase7_concern_dispositions.json")
MIGRATION_CATALOG = Path(
    "tools/bazel/fixtures/phase7_storage/redacted_migration_catalog.json")
VALIDATION_CONTRACT = Path(
    ".planning/phases/07-persistence-storage-and-resource-compatibility/07-VALIDATION.md"
)

RUST_DOMAIN_LIB = Path("rust/crates/domain/src/lib.rs")
STORAGE_RUST = Path("rust/crates/domain/src/storage.rs")
RESOURCE_RUST = Path("rust/crates/domain/src/resource.rs")

ALLOWED_EVIDENCE_CLASSES = {
    "manifest-check",
    "source-audit",
    "static-source-audit",
    "host-test",
    "rust-host-test",
    "simulator-flow",
    "hardware-smoke",
    "manual-hardware-required",
}

PHASE7_MANIFEST_EVIDENCE_CLASSES = ALLOWED_EVIDENCE_CLASSES | {
    "source-backed-manifest",
    "local-smoke",
    "ci-only",
    "reference-only",
    "manifest-and-label-coverage",
}

CONFIG_FIELDS = [
    "id",
    "requirement",
    "source_paths",
    "reference_surface",
    "rust_surface",
    "evidence_class",
    "proof_scope",
    "credential_policy",
    "intentional_delta",
]

CATALOG_FIELDS = [
    "id",
    "requirement",
    "source_paths",
    "fixture_identity",
    "reference_surface",
    "rust_surface",
    "evidence_class",
    "proof_scope",
    "redaction_policy",
    "credential_policy",
    "byte_material_policy",
    "intentional_delta",
]

STORAGE_FIELDS = [
    "id",
    "requirement",
    "source_paths",
    "mount_name",
    "runtime_path",
    "reference_surface",
    "rust_surface",
    "evidence_class",
    "proof_scope",
    "non_local_evidence",
]

RESOURCE_FIELDS = [
    "id",
    "requirement",
    "source_paths",
    "declared_inputs",
    "runtime_paths",
    "reference_surface",
    "rust_surface",
    "evidence_class",
    "proof_scope",
    "generated_label",
]

GENERATED_FIELDS = [
    "id",
    "requirement",
    "ownership",
    "tracked_outputs",
    "declared_sources",
    "check_label",
    "update_label",
    "evidence_class",
    "writes_source_tree",
    "proof_scope",
]

CONCERN_FIELDS = [
    "id",
    "concern_id",
    "requirement",
    "source_paths",
    "disposition",
    "phase7_handling",
    "evidence_class",
    "intentional_delta",
    "regression_guard",
]

CONFIG_ROW_IDS = [
    "current-config-store-schema-v5",
    "current-config-items-and-defaults",
    "deprecated-store-hashed-ids",
    "old-eeprom-version-chain",
    "old-eeprom-last-migration",
    "config-store-runtime-migrations",
    "credential-bearing-config-keys",
    "settings-import-export-keys",
    "selftest-calibration-state",
    "journal-hash-generation",
    "journal-backend-crc-bank-selection",
    "generated-struct-reflection",
]

OLD_EEPROM_VERSIONS = [
    "v4", "v6", "v7", "v9", "v10", "v11", "v12", "v22", "v32787", "v32789"
]

CATALOG_ROW_IDS = [
    *[f"old-eeprom-{version}-migration" for version in OLD_EEPROM_VERSIONS],
    "current-schema-v5",
    "settings-import-export",
    "credential-redaction",
    "selftest-calibration-state",
    "journal-hash-facts",
]

STORAGE_ROW_IDS = [
    "storage-driver-eeprom",
    "filesystem-usb-fatfs",
    "filesystem-internal-littlefs",
    "filesystem-bbf-littlefs",
    "filesystem-semihosting",
    "filesystem-root-listing",
    "libsysbase-devoptab-dispatch",
    "block-device-test-randomness",
]

RESOURCE_ROW_IDS = [
    "resource-standard-image",
    "resource-bootloader-image",
    "resource-esp32-blobs",
    "resource-esp8266-blobs",
    "resource-wui-static-assets",
    "resource-qoi-data",
    "resource-language-packs",
    "resource-font-assets",
    "resource-mmu-firmware",
    "resource-hash-and-revision",
    "resource-runtime-bootstrap",
]

GENERATED_ROW_IDS = [
    "product-profiles",
    "option-data",
    "resource-assets",
    "translation-pot",
    "font-assets",
    "wui-assets",
    "esp-blobs",
    "puppy-descriptors",
    "mmu-descriptors",
    "package-metadata",
    "tracked-generated-outputs",
]

CONCERN_ROW_IDS = [
    "concern-generated-file-drift",
    "concern-translation-font-shell-safety",
    "concern-unencrypted-credential-storage",
    "concern-config-schema-hash-fragility",
    "concern-journal-hash-space-limit",
    "concern-block-device-randomness",
    "concern-littlefs-python-dependency-drift",
    "concern-tracked-font-header-churn",
]

CONCERN_IDS = [
    "phase7-generated-file-drift",
    "phase7-unsafe-translation-font-shell-scripts",
    "phase7-unencrypted-credential-storage",
    "phase7-config-schema-hash-fragility",
    "phase7-journal-hash-space-limit",
    "phase7-block-device-randomness",
    "phase7-littlefs-python-dependency-drift",
    "phase7-tracked-font-header-churn",
]

CONFIG_REQUIRED_TEXT = [
    "CurrentStore::newest_config_version = 5",
    "WIFI AP Password",
    "Connect Token",
    "name-only-redacted",
    "DeprecatedStore",
    "selftest-calibration-state",
    "Selftest Result",
    "selftest_result",
    "calibration",
    "selftest",
    "0x3FFF",
    *OLD_EEPROM_VERSIONS,
    "current",
]

CATALOG_REQUIRED_TEXT = [
    "Selftest Result",
    "selftest_result",
    "calibration",
    "selftest",
    "CurrentStore::newest_config_version = 5",
    "journal::hash",
    "0x3FFF",
    "duplicate detection",
    "synthetic-redacted",
    "name-only-redacted",
    "byte_material_policy",
]

STORAGE_REQUIRED_TEXT = [
    "/usb",
    "/internal",
    "/bbf",
    "/semihosting",
    "/",
    "POSIX-like devoptab",
    "EEPROM/internal flash",
]

RESOURCE_REQUIRED_TEXT = [
    "/web/index.html",
    "/esp/uart_wifi.bin",
    "qoi.data",
    "/lang",
    "//tools/bazel:generated_resources_check",
]

REQUIRED_CHECK_LABELS = [
    "//tools/bazel:generated_product_profiles_check",
    "//tools/bazel:generated_option_data_check",
    "//tools/bazel:generated_resources_check",
    "//tools/bazel:generated_translations_check",
    "//tools/bazel:generated_fonts_check",
    "//tools/bazel:generated_wui_assets_check",
    "//tools/bazel:generated_esp_blobs_check",
    "//tools/bazel:generated_puppy_descriptors_check",
    "//tools/bazel:generated_mmu_descriptors_check",
    "//tools/bazel:generated_package_metadata_check",
    "//tools/bazel:tracked_generated_outputs_check",
]

REQUIRED_UPDATE_LABELS = [
    label.removesuffix("_check") + "_update" for label in REQUIRED_CHECK_LABELS
]

STORAGE_API_STRINGS = [
    "ReferenceHashName",
    "JournalHashFact",
    "CredentialRedactionPolicy",
    "EvidenceClass",
    "FilesystemSurface",
    "StorageCompatibilitySurface",
    "FixtureIdentity",
]

RESOURCE_API_STRINGS = [
    "ResourceRuntimePath",
    "ResourceSurface",
    "GeneratedOutputOwnership",
    "BazelLabel",
    "GeneratedSurface",
]

SECRET_MARKERS = [
    "password_value",
    "token_value",
    "secret_value",
    "BEGIN PRIVATE KEY",
    "certificate_bytes",
    "raw_eeprom",
    "byte_array",
    "eeprom_bytes",
]

UNSAFE_RUST_PATTERNS = [
    ("unsafe block", "unsafe {"),
    ("unsafe function", "unsafe fn"),
    ("unsafe trait", "unsafe trait"),
    ("unsafe impl", "unsafe impl"),
    ("unsafe extern", "unsafe extern"),
    ("unsafe attribute", "#[unsafe("),
    ("unsafe allowance", "#![allow(unsafe_code)]"),
    ("unsafe allowance", "#[allow(unsafe_code)]"),
]

OVERCLAIM_STRINGS = [
    "hardware-safe",
    "hardware passed",
    "hardware verified locally",
    "locally passed hardware",
    "byte-for-byte firmware parity",
    "full release artifact parity",
    "gui parity implemented",
    "wui api implemented",
    "connect tls implemented",
    "auxiliary runtime parity implemented",
    "cutover evidence complete",
]


class VerificationError(Exception):
    pass


def read_json(path: Path) -> dict[str, Any]:
    full_path = ROOT / path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {path.as_posix()}")

    try:
        data = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{path.as_posix()} is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise VerificationError(
            f"{path.as_posix()} must contain a top-level JSON object")
    return data


def read_text(path: str | Path) -> str:
    relative_path = Path(path)
    full_path = ROOT / relative_path
    if not full_path.exists():
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def is_empty(value: object) -> bool:
    return value in ("", [], {}, None)


def require_top_level(data: dict[str, Any], path: Path,
                      collection_name: str) -> list[dict[str, Any]]:
    if data.get("schema_version") != 1:
        raise VerificationError(
            f"{path.as_posix()} must set schema_version to 1")
    if data.get("phase") != PHASE:
        raise VerificationError(f"{path.as_posix()} must set phase to {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"{path.as_posix()} must set phase_lifecycle_id to {PHASE_LIFECYCLE_ID}"
        )

    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(
            f"{path.as_posix()} must contain a {collection_name} list")

    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(
                f"{path.as_posix()} {collection_name}[{index}] must be an object"
            )
        parsed_rows.append(row)
    return parsed_rows


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields if field in row and is_empty(row[field])
    ]
    if missing or empty:
        details = []
        if missing:
            details.append(f"missing required fields: {', '.join(missing)}")
        if empty:
            details.append(f"empty required fields: {', '.join(empty)}")
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_unique(rows: list[dict[str, Any]], field: str,
                   path: Path) -> set[str]:
    values: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str):
            raise VerificationError(
                f"{path.as_posix()} row has non-string {field}: {value!r}")
        if value in values:
            duplicates.add(value)
        values.add(value)

    if duplicates:
        raise VerificationError(
            f"{path.as_posix()} has duplicate {field} values: {', '.join(sorted(duplicates))}"
        )
    return values


def require_ids(actual: set[str], required: list[str], label: str) -> None:
    missing = sorted(set(required) - actual)
    if missing:
        raise VerificationError(
            f"missing required {label}: {', '.join(missing)}")


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str):
        raise VerificationError(f"{row_name} {field} must be a string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a non-empty list of strings")
    return value


def require_existing_source_paths(row: dict[str, Any],
                                  row_name: str) -> set[str]:
    source_paths = require_list_of_strings(row, "source_paths", row_name)
    existing_paths: set[str] = set()
    for source_path in source_paths:
        if not (ROOT / source_path).exists():
            raise VerificationError(
                f"{row_name} references missing source path: {source_path}")
        existing_paths.add(source_path)
    return existing_paths


def require_requirement(row: dict[str, Any], row_name: str,
                        expected: str | set[str]) -> None:
    requirement = require_string(row, "requirement", row_name)
    if isinstance(expected, str):
        if requirement != expected:
            raise VerificationError(
                f"{row_name} requirement must be {expected}")
        return

    if requirement not in expected:
        allowed = ", ".join(sorted(expected))
        raise VerificationError(
            f"{row_name} requirement must be one of: {allowed}")


def require_evidence_class(row: dict[str, Any], row_name: str) -> None:
    evidence_class = require_string(row, "evidence_class", row_name)
    if evidence_class not in PHASE7_MANIFEST_EVIDENCE_CLASSES:
        allowed = ", ".join(sorted(ALLOWED_EVIDENCE_CLASSES))
        raise VerificationError(
            f"{row_name} evidence_class {evidence_class!r} must be one of: {allowed}"
        )


def require_text_coverage(rows: list[dict[str, Any]], required_text: list[str],
                          label: str) -> None:
    haystack = json.dumps(rows, sort_keys=True)
    missing = [needle for needle in required_text if needle not in haystack]
    if missing:
        raise VerificationError(
            f"missing required {label}: {', '.join(missing)}")


def reject_markers(path: Path, markers: list[str], label: str) -> None:
    text = read_text(path)
    findings = [marker for marker in markers if marker in text]
    if findings:
        raise VerificationError(
            f"{path.as_posix()} contains forbidden {label} marker(s): {', '.join(findings)}"
        )


def validate_rows(
    path: Path,
    collection_name: str,
    fields: list[str],
    required_ids: list[str],
    expected_requirement: str | set[str],
    source_field: str = "source_paths",
) -> tuple[list[dict[str, Any]], set[str]]:
    data = read_json(path)
    rows = require_top_level(data, path, collection_name)
    row_ids = require_unique(rows, "id", path)
    require_ids(row_ids, required_ids, f"{collection_name} row IDs")

    all_source_paths: set[str] = set()
    for row in rows:
        row_name = f"{path.as_posix()} row {row.get('id', '<unknown>')}"
        require_fields(row, fields, row_name)
        require_requirement(row, row_name, expected_requirement)
        require_evidence_class(row, row_name)
        if source_field == "source_paths":
            all_source_paths.update(
                require_existing_source_paths(row, row_name))
        else:
            source_paths = require_list_of_strings(row, source_field, row_name)
            for source_path in source_paths:
                if not (ROOT / source_path).exists():
                    raise VerificationError(
                        f"{row_name} references missing source path: {source_path}"
                    )
                all_source_paths.add(source_path)
    return rows, all_source_paths


def check_config_store_manifest() -> None:
    rows, _ = validate_rows(CONFIG_MANIFEST, "config_contracts", CONFIG_FIELDS,
                            CONFIG_ROW_IDS, "IFCE-04")
    require_text_coverage(rows, CONFIG_REQUIRED_TEXT,
                          "config-store compatibility text")
    reject_markers(CONFIG_MANIFEST, SECRET_MARKERS,
                   "credential or byte material")


def check_storage_migration_catalog() -> None:
    rows, _ = validate_rows(MIGRATION_CATALOG, "fixtures", CATALOG_FIELDS, [],
                            "IFCE-04")
    row_ids = {row["id"] for row in rows}
    missing_rows = sorted(set(CATALOG_ROW_IDS) - row_ids)
    haystack = json.dumps(rows, sort_keys=True)
    missing_text = [
        needle for needle in CATALOG_REQUIRED_TEXT if needle not in haystack
    ]
    if missing_rows or missing_text:
        raise VerificationError(
            "missing required storage migration catalog coverage: " +
            ", ".join([*missing_rows, *missing_text, *CATALOG_REQUIRED_TEXT]))
    reject_markers(MIGRATION_CATALOG, SECRET_MARKERS,
                   "credential or byte material")


def check_storage_media_manifest() -> None:
    rows, _ = validate_rows(STORAGE_MANIFEST, "storage_surfaces",
                            STORAGE_FIELDS, STORAGE_ROW_IDS, "IFCE-04")
    require_text_coverage(rows, STORAGE_REQUIRED_TEXT,
                          "storage media runtime paths")
    for row in rows:
        row_name = f"{STORAGE_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        evidence_class = require_string(row, "evidence_class", row_name)
        proof_scope = require_string(row, "proof_scope", row_name)
        non_local = require_string(row, "non_local_evidence", row_name)
        is_source_only = proof_scope.startswith(
            "source-audit") and evidence_class in {
                "source-audit", "static-source-audit"
            }
        is_storage_media = row.get("runtime_path") in {
            "/usb", "/internal", "/bbf", "/semihosting",
            "EEPROM/internal flash"
        }
        if is_storage_media and not is_source_only and evidence_class not in {
                "manual-hardware-required", "hardware-smoke", "simulator-flow"
        }:
            raise VerificationError(
                f"{row_name} uses invalid hardware/media evidence_class: {evidence_class}"
            )


def check_resources_manifest() -> None:
    rows, _ = validate_rows(RESOURCES_MANIFEST, "resource_surfaces",
                            RESOURCE_FIELDS, RESOURCE_ROW_IDS, "IFCE-05")
    require_text_coverage(rows, RESOURCE_REQUIRED_TEXT,
                          "resource compatibility text")
    for row in rows:
        row_name = f"{RESOURCES_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        label = require_string(row, "generated_label", row_name)
        if not label.endswith("_check"):
            raise VerificationError(
                f"{row_name} generated label must end in _check: {label}")
