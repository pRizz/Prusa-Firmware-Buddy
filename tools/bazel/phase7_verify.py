#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "07-persistence-storage-and-resource-compatibility"
PHASE_LIFECYCLE_ID = "7-2026-06-06T04-24-25"

CONFIG_MANIFEST = Path("tools/bazel/manifests/phase7_config_store.json")
STORAGE_MANIFEST = Path("tools/bazel/manifests/phase7_storage_media.json")
RESOURCES_MANIFEST = Path("tools/bazel/manifests/phase7_resources.json")
GENERATED_MANIFEST = Path("tools/bazel/manifests/phase7_generated_outputs.json")
CONCERN_MANIFEST = Path("tools/bazel/manifests/phase7_concern_dispositions.json")
MIGRATION_CATALOG = Path("tools/bazel/fixtures/phase7_storage/redacted_migration_catalog.json")
VALIDATION_CONTRACT = Path(".planning/phases/07-persistence-storage-and-resource-compatibility/07-VALIDATION.md")

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

OLD_EEPROM_VERSIONS = ["v4", "v6", "v7", "v9", "v10", "v11", "v12", "v22", "v32787", "v32789"]

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

REQUIRED_UPDATE_LABELS = [label.removesuffix("_check") + "_update" for label in REQUIRED_CHECK_LABELS]

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
        raise VerificationError(f"{path.as_posix()} is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise VerificationError(f"{path.as_posix()} must contain a top-level JSON object")
    return data


def read_text(path: str | Path) -> str:
    relative_path = Path(path)
    full_path = ROOT / relative_path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def is_empty(value: object) -> bool:
    return value in ("", [], {}, None)


def require_top_level(data: dict[str, Any], path: Path, collection_name: str) -> list[dict[str, Any]]:
    if data.get("schema_version") != 1:
        raise VerificationError(f"{path.as_posix()} must set schema_version to 1")
    if data.get("phase") != PHASE:
        raise VerificationError(f"{path.as_posix()} must set phase to {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"{path.as_posix()} must set phase_lifecycle_id to {PHASE_LIFECYCLE_ID}"
        )

    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(f"{path.as_posix()} must contain a {collection_name} list")

    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{path.as_posix()} {collection_name}[{index}] must be an object")
        parsed_rows.append(row)
    return parsed_rows


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and is_empty(row[field])]
    if missing or empty:
        details = []
        if missing:
            details.append(f"missing required fields: {', '.join(missing)}")
        if empty:
            details.append(f"empty required fields: {', '.join(empty)}")
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_unique(rows: list[dict[str, Any]], field: str, path: Path) -> set[str]:
    values: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str):
            raise VerificationError(f"{path.as_posix()} row has non-string {field}: {value!r}")
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
        raise VerificationError(f"missing required {label}: {', '.join(missing)}")


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str):
        raise VerificationError(f"{row_name} {field} must be a string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a non-empty list of strings")
    return value


def require_existing_source_paths(row: dict[str, Any], row_name: str) -> set[str]:
    source_paths = require_list_of_strings(row, "source_paths", row_name)
    existing_paths: set[str] = set()
    for source_path in source_paths:
        if not (ROOT / source_path).exists():
            raise VerificationError(f"{row_name} references missing source path: {source_path}")
        existing_paths.add(source_path)
    return existing_paths


def require_requirement(row: dict[str, Any], row_name: str, expected: str | set[str]) -> None:
    requirement = require_string(row, "requirement", row_name)
    if isinstance(expected, str):
        if requirement != expected:
            raise VerificationError(f"{row_name} requirement must be {expected}")
        return

    if requirement not in expected:
        allowed = ", ".join(sorted(expected))
        raise VerificationError(f"{row_name} requirement must be one of: {allowed}")


def require_evidence_class(row: dict[str, Any], row_name: str) -> None:
    evidence_class = require_string(row, "evidence_class", row_name)
    if evidence_class not in PHASE7_MANIFEST_EVIDENCE_CLASSES:
        allowed = ", ".join(sorted(ALLOWED_EVIDENCE_CLASSES))
        raise VerificationError(
            f"{row_name} evidence_class {evidence_class!r} must be one of: {allowed}"
        )


def require_text_coverage(rows: list[dict[str, Any]], required_text: list[str], label: str) -> None:
    haystack = json.dumps(rows, sort_keys=True)
    missing = [needle for needle in required_text if needle not in haystack]
    if missing:
        raise VerificationError(f"missing required {label}: {', '.join(missing)}")


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
            all_source_paths.update(require_existing_source_paths(row, row_name))
        else:
            source_paths = require_list_of_strings(row, source_field, row_name)
            for source_path in source_paths:
                if not (ROOT / source_path).exists():
                    raise VerificationError(f"{row_name} references missing source path: {source_path}")
                all_source_paths.add(source_path)
    return rows, all_source_paths


def check_config_store_manifest() -> None:
    rows, _ = validate_rows(CONFIG_MANIFEST, "config_contracts", CONFIG_FIELDS, CONFIG_ROW_IDS, "IFCE-04")
    require_text_coverage(rows, CONFIG_REQUIRED_TEXT, "config-store compatibility text")
    reject_markers(CONFIG_MANIFEST, SECRET_MARKERS, "credential or byte material")


def check_storage_migration_catalog() -> None:
    rows, _ = validate_rows(MIGRATION_CATALOG, "fixtures", CATALOG_FIELDS, [], "IFCE-04")
    row_ids = {row["id"] for row in rows}
    missing_rows = sorted(set(CATALOG_ROW_IDS) - row_ids)
    haystack = json.dumps(rows, sort_keys=True)
    missing_text = [needle for needle in CATALOG_REQUIRED_TEXT if needle not in haystack]
    if missing_rows or missing_text:
        raise VerificationError(
            "missing required storage migration catalog coverage: "
            + ", ".join([*missing_rows, *missing_text, *CATALOG_REQUIRED_TEXT])
        )
    reject_markers(MIGRATION_CATALOG, SECRET_MARKERS, "credential or byte material")


def check_storage_media_manifest() -> None:
    rows, _ = validate_rows(STORAGE_MANIFEST, "storage_surfaces", STORAGE_FIELDS, STORAGE_ROW_IDS, "IFCE-04")
    require_text_coverage(rows, STORAGE_REQUIRED_TEXT, "storage media runtime paths")
    for row in rows:
        row_name = f"{STORAGE_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        evidence_class = require_string(row, "evidence_class", row_name)
        proof_scope = require_string(row, "proof_scope", row_name)
        non_local = require_string(row, "non_local_evidence", row_name)
        is_source_only = proof_scope.startswith("source-audit") and evidence_class in {"source-audit", "static-source-audit"}
        is_storage_media = row.get("runtime_path") in {"/usb", "/internal", "/bbf", "/semihosting", "EEPROM/internal flash"}
        if is_storage_media and not is_source_only and evidence_class not in {"manual-hardware-required", "hardware-smoke", "simulator-flow"}:
            raise VerificationError(f"{row_name} uses invalid hardware/media evidence_class: {evidence_class}")


def check_resources_manifest() -> None:
    rows, _ = validate_rows(RESOURCES_MANIFEST, "resource_surfaces", RESOURCE_FIELDS, RESOURCE_ROW_IDS, "IFCE-05")
    require_text_coverage(rows, RESOURCE_REQUIRED_TEXT, "resource compatibility text")
    for row in rows:
        row_name = f"{RESOURCES_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        label = require_string(row, "generated_label", row_name)
        if not label.endswith("_check"):
            raise VerificationError(f"{row_name} generated label must end in _check: {label}")


def check_generated_outputs_manifest() -> None:
    rows, _ = validate_rows(
        GENERATED_MANIFEST,
        "generated_surfaces",
        GENERATED_FIELDS,
        [],
        {"IFCE-04", "IFCE-05", "IFCE-04,IFCE-05"},
        source_field="declared_sources",
    )
    row_ids = {row["id"] for row in rows}
    check_labels: set[str] = set()
    update_labels: set[str] = set()
    for row in rows:
        row_name = f"{GENERATED_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        check_label = require_string(row, "check_label", row_name)
        update_label = require_string(row, "update_label", row_name)
        if not check_label.endswith("_check"):
            raise VerificationError(f"{row_name} check_label must end in _check: {check_label}")
        if not update_label.endswith("_update"):
            raise VerificationError(f"{row_name} update_label must end in _update: {update_label}")
        check_labels.add(check_label)
        update_labels.add(update_label)
    missing_row_ids = sorted(set(GENERATED_ROW_IDS) - row_ids)
    missing_check_labels = sorted(set(REQUIRED_CHECK_LABELS) - check_labels)
    missing_update_labels = sorted(set(REQUIRED_UPDATE_LABELS) - update_labels)
    if missing_row_ids or missing_check_labels or missing_update_labels:
        raise VerificationError(
            "missing required generated-output coverage: "
            + ", ".join([*missing_row_ids, *missing_check_labels, *missing_update_labels])
        )


def check_concern_manifest() -> None:
    rows, _ = validate_rows(CONCERN_MANIFEST, "concerns", CONCERN_FIELDS, CONCERN_ROW_IDS, {"IFCE-04", "IFCE-05"})
    concern_ids = require_unique(rows, "concern_id", CONCERN_MANIFEST)
    require_ids(concern_ids, CONCERN_IDS, "D-11 concern IDs")
    for row in rows:
        intentional_delta = row.get("intentional_delta")
        if intentional_delta == "none" and row.get("disposition") != "preserve-with-explicit-risk":
            raise VerificationError(
                f"{CONCERN_MANIFEST.as_posix()} row {row.get('id')} must use preserve-with-explicit-risk unless intentional_delta is not none"
            )


def blank_non_code(output: list[str], text: str) -> None:
    for character in text:
        output.append("\n" if character == "\n" else " ")


def raw_string_end_index(text: str, start: int) -> int | None:
    if text.startswith("br", start):
        marker_index = start + 2
    elif text.startswith("r", start):
        marker_index = start + 1
    else:
        return None

    while marker_index < len(text) and text[marker_index] == "#":
        marker_index += 1
    if marker_index >= len(text) or text[marker_index] != '"':
        return None

    hash_count = marker_index - start - (2 if text.startswith("br", start) else 1)
    delimiter = '"' + ("#" * hash_count)
    maybe_end = text.find(delimiter, marker_index + 1)
    if maybe_end == -1:
        return len(text)
    return maybe_end + len(delimiter)


def quoted_string_end_index(text: str, start: int) -> int:
    index = start + 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == '"':
            return index + 1
        index += 1
    return len(text)


def rust_code_without_comments_or_strings(text: str) -> str:
    output: list[str] = []
    index = 0
    block_comment_depth = 0

    while index < len(text):
        if block_comment_depth > 0:
            if text.startswith("/*", index):
                blank_non_code(output, "/*")
                index += 2
                block_comment_depth += 1
                continue
            if text.startswith("*/", index):
                blank_non_code(output, "*/")
                index += 2
                block_comment_depth -= 1
                continue
            blank_non_code(output, text[index])
            index += 1
            continue

        maybe_raw_end = raw_string_end_index(text, index)
        if maybe_raw_end is not None:
            blank_non_code(output, text[index:maybe_raw_end])
            index = maybe_raw_end
            continue
        if text.startswith("//", index):
            line_end = text.find("\n", index)
            if line_end == -1:
                blank_non_code(output, text[index:])
                break
            blank_non_code(output, text[index:line_end])
            index = line_end
            continue
        if text.startswith("/*", index):
            blank_non_code(output, "/*")
            index += 2
            block_comment_depth = 1
            continue
        if text[index] == '"':
            string_end = quoted_string_end_index(text, index)
            blank_non_code(output, text[index:string_end])
            index = string_end
            continue
        output.append(text[index])
        index += 1

    return "".join(output)


def unsafe_findings_for_file(relative_path: Path, text: str) -> list[str]:
    findings: list[str] = []
    code = rust_code_without_comments_or_strings(text)
    for line_number, line in enumerate(code.splitlines(), start=1):
        for label, pattern in UNSAFE_RUST_PATTERNS:
            if pattern in line:
                findings.append(f"{relative_path.as_posix()}:{line_number}: {label}")
    return findings


def check_rust_api_surface() -> None:
    lib_text = read_text(RUST_DOMAIN_LIB)
    if "#![forbid(unsafe_code)]" not in lib_text:
        raise VerificationError(f"{RUST_DOMAIN_LIB.as_posix()} must contain #![forbid(unsafe_code)]")

    findings: list[str] = []
    for path, required_strings in [(STORAGE_RUST, STORAGE_API_STRINGS), (RESOURCE_RUST, RESOURCE_API_STRINGS)]:
        text = read_text(path)
        missing = [needle for needle in required_strings if needle not in text]
        if missing:
            findings.append(f"{path.as_posix()} missing required Rust API strings: {', '.join(missing)}")
        findings.extend(unsafe_findings_for_file(path, text))

    if findings:
        raise VerificationError("Phase 7 Rust API surface check failed:\n" + "\n".join(findings))


def check_bazel_surface() -> None:
    tools_build = read_text("tools/bazel/BUILD.bazel")
    if "phase7_verify" in tools_build:
        for needle in ["phase7_verify", "phase7_verify_tests", "phase7_verify.py", "phase7_verify_test.py"]:
            if needle not in tools_build:
                raise VerificationError(f"tools/bazel/BUILD.bazel missing {needle}")
        return

    for label in REQUIRED_CHECK_LABELS:
        target = label.split(":", 1)[1]
        if target not in tools_build:
            raise VerificationError(f"tools/bazel/BUILD.bazel missing generated label {target}")


def check_just_surface() -> None:
    justfile = read_text("justfile")
    if "phase7-verify:" in justfile:
        for needle in ["phase7-verify:", "phase7_verify_tests", "phase7_verify"]:
            if needle not in justfile:
                raise VerificationError(f"justfile missing {needle}")
        return
    for needle in ["generated-check:", "rust-test:", "phase6-verify:"]:
        if needle not in justfile:
            raise VerificationError(f"justfile missing expected verification facade {needle}")


def check_validation_contract() -> None:
    validation = read_text(VALIDATION_CONTRACT)
    required_strings = [
        "Quick run command",
        "python3 tools/bazel/phase7_verify.py --quick",
        "Full suite command",
        "just phase7-verify",
    ]
    missing = [needle for needle in required_strings if needle not in validation]
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation contract text: "
            + ", ".join(missing)
        )


def check_no_phase7_overclaim() -> None:
    phase_dir = ROOT / ".planning/phases/07-persistence-storage-and-resource-compatibility"
    paths = [
        CONFIG_MANIFEST,
        STORAGE_MANIFEST,
        RESOURCES_MANIFEST,
        GENERATED_MANIFEST,
        CONCERN_MANIFEST,
        MIGRATION_CATALOG,
        *[path.relative_to(ROOT) for path in phase_dir.glob("07-*-SUMMARY.md")],
    ]
    findings: list[str] = []
    for path in paths:
        full_path = ROOT / path
        if not full_path.exists():
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in OVERCLAIM_STRINGS:
            if phrase in text:
                findings.append(f"{path.as_posix()}: {phrase}")
    if findings:
        raise VerificationError("Phase 7 artifacts overclaim local evidence:\n" + "\n".join(findings))


def check_manifests() -> None:
    check_config_store_manifest()
    check_storage_media_manifest()
    check_storage_migration_catalog()
    check_resources_manifest()
    check_generated_outputs_manifest()
    check_concern_manifest()


def check_quick() -> None:
    check_manifests()
    check_rust_api_surface()
    check_bazel_surface()
    check_just_surface()
    check_validation_contract()
    check_no_phase7_overclaim()


def run(command: list[str]) -> None:
    if not shutil.which(command[0]):
        raise VerificationError(f"required command not found: {command[0]}")
    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise VerificationError(f"command failed: {' '.join(command)}\n{result.stdout}")


def check_rust_toolchain() -> None:
    run(["cargo", "fmt", "--all", "--", "--check"])
    run(["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"])
    run(["cargo", "build", "--all-targets", "--all-features"])
    run(["cargo", "test", "--all-features"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 7 persistence storage and resource compatibility surfaces")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Run static Phase 7 manifest, source, Rust API, facade, and overclaim checks")
    mode.add_argument("--all", action="store_true", help="Run quick checks plus Cargo format, lint, build, and tests")
    mode.add_argument("--manifests-only", action="store_true", help="Run only Phase 7 manifest and redacted catalog checks")
    mode.add_argument("--config-only", action="store_true", help="Run only config-store manifest checks")
    mode.add_argument("--storage-only", action="store_true", help="Run only storage media and migration catalog checks")
    mode.add_argument("--resources-only", action="store_true", help="Run only resource manifest checks")
    mode.add_argument("--generated-only", action="store_true", help="Run only generated-output manifest checks")
    mode.add_argument("--concerns-only", action="store_true", help="Run only concern disposition checks")
    mode.add_argument("--rust-only", action="store_true", help="Run only Rust storage/resource API checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.config_only:
            check_config_store_manifest()
        elif args.storage_only:
            check_storage_media_manifest()
            check_storage_migration_catalog()
        elif args.resources_only:
            check_resources_manifest()
        elif args.generated_only:
            check_generated_outputs_manifest()
        elif args.concerns_only:
            check_concern_manifest()
        elif args.rust_only:
            check_rust_api_surface()
        elif args.manifests_only:
            check_manifests()
        else:
            check_quick()
            if args.all:
                check_rust_toolchain()

        print("Phase 7 persistence storage and resource compatibility verification passed")
        return 0
    except VerificationError as error:
        print(
            f"Phase 7 persistence storage and resource compatibility verification failed: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
