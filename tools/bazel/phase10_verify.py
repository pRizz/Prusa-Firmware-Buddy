#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
PHASE = "10-auxiliary-controllers-and-expansion-ecosystem"
PHASE_LIFECYCLE_ID = "10-2026-06-14T15-08-30"

VALIDATION_CONTRACT = Path(
    ".planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VALIDATION.md"
)
AUXILIARY_RUST = Path("rust/crates/domain/src/auxiliary.rs")
RUST_DOMAIN_LIB = Path("rust/crates/domain/src/lib.rs")

AUXILIARY_CONTROLLERS_MANIFEST = Path("tools/bazel/manifests/phase10_auxiliary_controllers.json")
MMU_TRANSPORT_MANIFEST = Path("tools/bazel/manifests/phase10_mmu_transport.json")
MODBUS_RS485_MANIFEST = Path("tools/bazel/manifests/phase10_modbus_rs485.json")
TOOLCHANGER_DOCK_OFFSETS_MANIFEST = Path(
    "tools/bazel/manifests/phase10_toolchanger_dock_offsets.json"
)
AUXILIARY_BUILD_UPDATE_MANIFEST = Path(
    "tools/bazel/manifests/phase10_auxiliary_build_update.json"
)
CONCERN_DISPOSITIONS_MANIFEST = Path("tools/bazel/manifests/phase10_concern_dispositions.json")

MANIFESTS: dict[Path, str] = {
    AUXILIARY_CONTROLLERS_MANIFEST: "auxiliary_controller_contracts",
    MMU_TRANSPORT_MANIFEST: "mmu_transport_contracts",
    MODBUS_RS485_MANIFEST: "modbus_rs485_contracts",
    TOOLCHANGER_DOCK_OFFSETS_MANIFEST: "toolchanger_dock_offset_contracts",
    AUXILIARY_BUILD_UPDATE_MANIFEST: "auxiliary_build_update_contracts",
    CONCERN_DISPOSITIONS_MANIFEST: "concerns",
}

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

NON_LOCAL_EVIDENCE_CLASSES = {
    "simulator-flow",
    "hardware-smoke",
    "manual-hardware-required",
}

CONTRACT_ROW_FIELDS = [
    "id",
    "requirement_id",
    "reference_sources",
    "reference_behavior",
    "rust_surface",
    "evidence_class",
    "proof_scope",
    "update_build_surface",
    "intentional_delta",
    "phase_lifecycle_id",
]

CONCERN_FIELDS = [
    "id",
    "concern_id",
    "requirement_id",
    "reference_sources",
    "disposition",
    "phase10_handling",
    "evidence_class",
    "proof_scope",
    "intentional_delta",
    "regression_guard",
    "secret_handling",
    "phase_lifecycle_id",
]

REQUIRED_ROW_IDS_BY_MANIFEST = {
    AUXILIARY_CONTROLLERS_MANIFEST: [
        "aux-controller-family-dwarf",
        "aux-controller-family-modular-bed",
        "aux-controller-family-xbuddy-extension",
        "dwarf-runtime-fifo-loadcell-toolhead",
        "modular-bed-runtime-bedlet-faults",
        "xbuddy-extension-runtime-h503-special",
        "aux-runtime-state-contract",
    ],
    MMU_TRANSPORT_MANIFEST: [
        "mmu2-availability-reporting-stub",
        "mmu2-usemmu-config-runtime-state",
        "mmu2-bootloader-update-manager",
        "mmu2-uart-transport",
        "mmu2-puppy-modbus-bridge",
        "mmu-firmware-runtime-resource",
    ],
    MODBUS_RS485_MANIFEST: [
        "lightmodbus-retained-dependency",
        "puppy-modbus-master-request-retry-timeout",
        "puppy-rs485-flow-control",
        "puppy-modbus-register-block-limits",
        "xbuddy-extension-mmu-read-write-query-command",
        "xbuddy-extension-mmu-speculative-accepted",
        "xbuddy-extension-mmu-response-timeout-window",
    ],
    TOOLCHANGER_DOCK_OFFSETS_MANIFEST: [
        "toolchanger-dwarf-update-loop",
        "toolchanger-dock-identity-dwarf1-6",
        "toolchanger-dock-identity-modular-bed-xbe",
        "toolchanger-dock-settings-ui",
        "tool-offset-nozzle-settings-ui",
        "tool-offset-selftest-flow",
    ],
    AUXILIARY_BUILD_UPDATE_MANIFEST: [
        "aux-build-dwarf-external-project",
        "aux-build-modularbed-external-project",
        "aux-build-xbuddy-extension-external-project",
        "aux-firmware-descriptor-generation",
        "aux-puppy-resource-runtime-paths",
        "mmu-firmware-resource-conversion",
        "prebuilt-binary-paths-dwarf-modularbed-xbe",
        "puppy-skip-flash-mode",
        "startup-flashing-bootloader-gates",
        "puppy-crash-dump-download",
    ],
    CONCERN_DISPOSITIONS_MANIFEST: [
        "concern-phase10-mmu-availability-reporting",
        "concern-phase10-xbuddy-extension-h503-special",
        "concern-phase10-xbe-mmu-bridge-timing",
        "concern-phase10-buddyheaders-error-codes-coupling",
        "concern-phase10-credential-payload-leakage",
        "concern-phase10-non-local-hardware-proof",
        "concern-phase10-ix-xbuddy-extension-branch",
    ],
}

RUST_API_STRINGS = [
    "AuxiliaryControllerKind",
    "AuxiliaryRuntimeState",
    "FirmwareImageSource",
    "AuxiliaryUpdateMode",
    "ModbusUnitIdentity",
    "ModbusRequestKind",
    "BusEvidenceClass",
    "AuxiliaryProofScope",
    "MmuTransportState",
    "MmuTransportSurface",
    "DockIdentity",
    "ToolOffsetAxis",
    "ToolOffsetIdentity",
    "ControllerFaultClass",
    "AuxiliaryParityRowId",
    "AuxiliaryParityContract",
    "AuxiliaryControllerContract",
]

INVARIANT_ERROR_STRINGS = [
    "EmptyAuxiliaryParityRowId",
    "InvalidAuxiliaryParityRowId",
    "InvalidAuxiliaryControllerKind",
    "InvalidAuxiliaryRuntimeState",
    "InvalidFirmwareImageSource",
    "InvalidAuxiliaryUpdateMode",
    "InvalidModbusUnitIdentity",
    "InvalidModbusRequestKind",
    "InvalidBusEvidenceClass",
    "InvalidAuxiliaryProofScope",
    "InvalidMmuTransportState",
    "InvalidMmuTransportSurface",
    "InvalidDockIdentity",
    "InvalidToolOffsetIdentity",
    "InvalidControllerFaultClass",
    "InvalidAuxiliaryParityContract",
    "UnsupportedAuxiliaryController",
]

REQUIRED_MMU_TRANSPORT_STATES = {
    "disabled",
    "unavailable",
    "bootloader",
    "stopped",
    "active",
    "updating",
    "update-failed",
    "communication-fault",
}

REQUIRED_MMU_TRANSPORT_SURFACES = {
    "direct-uart": "MmuTransportSurface::Uart",
    "puppy-modbus-bridge": "MmuTransportSurface::PuppyModbusBridge",
}

PACKAGE_UPDATE_STRINGS = [
    "DWARF_BINARY_PATH",
    "MODULARBED_BINARY_PATH",
    "XBUDDY_EXTENSION_BINARY_PATH",
    "/puppies/fw-dwarf.bin",
    "/puppies/fw-modularbed.bin",
    "/puppies/fw-xbuddy-extension.bin",
    "/mmu/fw.bin",
    "utils/gen_puppies_descriptor.py",
    "descriptor-generation",
    "startup-flashing",
    "PUPPY_SKIP_FLASH_FW",
    "mmu-firmware-resource",
    "crash-dump",
    "puppy-crash-dump-download",
    "//tools/bazel:phase10_auxiliary_build_update_manifest",
    "//tools/bazel:phase10_verify",
    "//:phase10_verify",
]

FORBIDDEN_MARKERS = [
    "firmware_payload",
    "payload_bytes",
    "hex_bytes",
    "credential_value",
    "private_key",
    "SIGNING_KEY_VALUE",
    "raw_crash_dump",
    "crash_dump_payload",
    "BEGIN PRIVATE KEY",
]

OVERCLAIM_STRINGS = [
    "RS485 hardware verified locally",
    "physical toolchanger verified locally",
    "live MMU transport passed",
    "long-run update passed locally",
    "simulator auxiliary flow passed locally",
    "cutover evidence complete",
    "firmware bytes embedded",
    "signing key value recorded",
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


class VerificationError(Exception):
    pass


def read_text(root: Path, path: str | Path) -> str:
    relative_path = Path(path)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def read_json(root: Path, path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read_text(root, path))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{path.as_posix()} is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise VerificationError(f"{path.as_posix()} must contain a top-level JSON object")
    return data


def is_empty(value: object) -> bool:
    return value in ("", [], {}, None)


def row_blob(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True)


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a non-empty list of strings")
    return value


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and is_empty(row[field])]
    legacy = [field for field in ["requirement", "source_paths"] if field in row]
    details = []
    if missing:
        details.append(f"missing required fields: {', '.join(missing)}")
    if empty:
        details.append(f"empty required fields: {', '.join(empty)}")
    if legacy:
        details.append(
            "uses legacy manifest schema fields instead of canonical requirement_id/reference_sources: "
            + ", ".join(legacy)
        )
    if details:
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_top_level(root: Path, path: Path, collection_name: str) -> list[dict[str, Any]]:
    data = read_json(root, path)
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


def require_unique_ids(rows: list[dict[str, Any]], path: Path) -> set[str]:
    values: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get("id")
        if not isinstance(value, str):
            raise VerificationError(f"{path.as_posix()} row has non-string id: {value!r}")
        if value in values:
            duplicates.add(value)
        values.add(value)
    if duplicates:
        raise VerificationError(
            f"{path.as_posix()} has duplicate id values: {', '.join(sorted(duplicates))}"
        )
    return values


def require_row_ids(rows: list[dict[str, Any]], path: Path) -> None:
    actual_ids = require_unique_ids(rows, path)
    missing = sorted(set(REQUIRED_ROW_IDS_BY_MANIFEST[path]) - actual_ids)
    if missing:
        raise VerificationError(f"{path.as_posix()} missing required row IDs: {', '.join(missing)}")


def require_reference_sources(root: Path, row: dict[str, Any], row_name: str) -> None:
    reference_sources = require_list_of_strings(row, "reference_sources", row_name)
    resolved_root = root.resolve()
    for reference_source in reference_sources:
        relative_path = Path(reference_source)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise VerificationError(f"{row_name} reference source must be repo-relative: {reference_source}")

        full_path = (resolved_root / relative_path).resolve()
        try:
            full_path.relative_to(resolved_root)
        except ValueError as error:
            raise VerificationError(f"{row_name} reference source escapes repo: {reference_source}") from error

        if not full_path.exists():
            raise VerificationError(f"{row_name} references missing source path: {reference_source}")


def extract_parse_strings(rust_source: str, type_name: str) -> set[str]:
    sanitized_source = strip_rust_comments(rust_source)
    impl_marker = f"impl {type_name}"
    impl_start = sanitized_source.find(impl_marker)
    if impl_start == -1:
        raise VerificationError(f"{AUXILIARY_RUST.as_posix()} missing impl {type_name}")

    next_impl = sanitized_source.find("\nimpl ", impl_start + len(impl_marker))
    impl_body = sanitized_source[impl_start:] if next_impl == -1 else sanitized_source[impl_start:next_impl]
    parse_marker = "pub fn parse"
    parse_start = impl_body.find(parse_marker)
    if parse_start == -1:
        raise VerificationError(f"{AUXILIARY_RUST.as_posix()} missing {type_name}::parse")

    parse_body = impl_body[parse_start:]
    return set(re.findall(r'"([^"]+)"\s*=>\s*Ok\(Self::', parse_body))


def require_mmu_transport_contracts(root: Path, rows: list[dict[str, Any]]) -> None:
    auxiliary_text = read_text(root, AUXILIARY_RUST)
    accepted_states = extract_parse_strings(auxiliary_text, "MmuTransportState")
    accepted_surfaces = extract_parse_strings(auxiliary_text, "MmuTransportSurface")
    errors: list[str] = []

    missing_required_states = sorted(REQUIRED_MMU_TRANSPORT_STATES - accepted_states)
    if missing_required_states:
        errors.append(
            f"{AUXILIARY_RUST.as_posix()} MmuTransportState::parse missing manifest states: "
            + ", ".join(missing_required_states)
        )

    missing_required_surfaces = sorted(set(REQUIRED_MMU_TRANSPORT_SURFACES) - accepted_surfaces)
    if missing_required_surfaces:
        errors.append(
            f"{AUXILIARY_RUST.as_posix()} MmuTransportSurface::parse missing manifest surfaces: "
            + ", ".join(missing_required_surfaces)
        )

    for row in rows:
        row_name = f"{MMU_TRANSPORT_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        state_values = row.get("mmu_transport_state")
        if not isinstance(state_values, list) or not state_values:
            errors.append(f"{row_name} mmu_transport_state must be a non-empty list")
            continue
        for state in state_values:
            if not isinstance(state, str):
                errors.append(f"{row_name} mmu_transport_state contains non-string value: {state!r}")
            elif state not in accepted_states:
                errors.append(f"{row_name} mmu_transport_state {state!r} is not accepted by MmuTransportState::parse")

        rust_surface = row.get("rust_surface")
        transport_surface = row.get("transport_surface")
        expected_surface = REQUIRED_MMU_TRANSPORT_SURFACES.get(str(transport_surface))
        if expected_surface is not None and rust_surface != f"buddy-domain::auxiliary::{expected_surface}":
            errors.append(
                f"{row_name} transport_surface {transport_surface!r} must use rust_surface "
                f"buddy-domain::auxiliary::{expected_surface}"
            )

    if errors:
        raise VerificationError("\n".join(errors))


def require_requirement_lifecycle_evidence(row: dict[str, Any], row_name: str) -> None:
    requirement_id = require_string(row, "requirement_id", row_name)
    if requirement_id != "IFCE-06":
        raise VerificationError(f"{row_name} requirement_id must be IFCE-06")

    phase_lifecycle_id = require_string(row, "phase_lifecycle_id", row_name)
    if phase_lifecycle_id != PHASE_LIFECYCLE_ID:
        raise VerificationError(f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")

    evidence_class = require_string(row, "evidence_class", row_name)
    if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
        allowed = ", ".join(sorted(ALLOWED_EVIDENCE_CLASSES))
        raise VerificationError(f"{row_name} evidence_class {evidence_class!r} must be one of: {allowed}")

    proof_scope = require_string(row, "proof_scope", row_name)
    if proof_scope not in {"local", "non-local"}:
        raise VerificationError(f"{row_name} proof_scope must be local or non-local")
    if evidence_class in NON_LOCAL_EVIDENCE_CLASSES and proof_scope != "non-local":
        raise VerificationError(
            f"{row_name} proof_scope must be non-local for {evidence_class} evidence"
        )

    intentional_delta = require_string(row, "intentional_delta", row_name)
    if intentional_delta not in {"none", "approved", "blocked"}:
        raise VerificationError(f"{row_name} intentional_delta must be none, approved, or blocked")


def validate_manifest(root: Path, path: Path) -> list[dict[str, Any]]:
    collection_name = MANIFESTS[path]
    rows = require_top_level(root, path, collection_name)
    errors: list[str] = []
    try:
        require_row_ids(rows, path)
    except VerificationError as error:
        errors.append(str(error))

    fields = CONCERN_FIELDS if path == CONCERN_DISPOSITIONS_MANIFEST else CONTRACT_ROW_FIELDS
    for row in rows:
        row_name = f"{path.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, fields, row_name)
            require_requirement_lifecycle_evidence(row, row_name)
            require_reference_sources(root, row, row_name)
            if path != CONCERN_DISPOSITIONS_MANIFEST:
                require_string(row, "update_build_surface", row_name)
                require_string(row, "rust_surface", row_name)
            if path == CONCERN_DISPOSITIONS_MANIFEST:
                secret_handling = require_string(row, "secret_handling", row_name)
                if secret_handling not in {"none", "named-only-redacted"}:
                    raise VerificationError(f"{row_name} secret_handling must be none or named-only-redacted")
        except VerificationError as error:
            errors.append(str(error))

    if path == MMU_TRANSPORT_MANIFEST:
        try:
            require_mmu_transport_contracts(root, rows)
        except VerificationError as error:
            errors.append(str(error))

    if errors:
        raise VerificationError("\n".join(errors))
    return rows


def check_manifests(root: Path) -> None:
    collect_errors([lambda path=path: validate_manifest(root, path) for path in MANIFESTS])


def all_manifest_rows(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows: list[tuple[Path, dict[str, Any]]] = []
    for path in MANIFESTS:
        for row in validate_manifest(root, path):
            rows.append((path, row))
    return rows


def strip_rust_comments_and_strings(source: str) -> str:
    result: list[str] = []
    index = 0
    length = len(source)
    while index < length:
        char = source[index]
        next_char = source[index + 1] if index + 1 < length else ""

        if char == "/" and next_char == "/":
            index += 2
            while index < length and source[index] != "\n":
                index += 1
            result.append("\n")
            continue

        if char == "/" and next_char == "*":
            index += 2
            depth = 1
            while index < length and depth > 0:
                if source[index : index + 2] == "/*":
                    depth += 1
                    index += 2
                    continue
                if source[index : index + 2] == "*/":
                    depth -= 1
                    index += 2
                    continue
                if source[index] == "\n":
                    result.append("\n")
                index += 1
            continue

        raw_match = re.match(r'r(#*)"', source[index:])
        if raw_match:
            hashes = raw_match.group(1)
            terminator = '"' + hashes
            index += len(raw_match.group(0))
            end_index = source.find(terminator, index)
            if end_index == -1:
                break
            result.append('""')
            index = end_index + len(terminator)
            continue

        if char == '"':
            index += 1
            escaped = False
            while index < length:
                current = source[index]
                if current == "\n":
                    result.append("\n")
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == '"':
                    index += 1
                    break
                index += 1
            result.append('""')
            continue

        result.append(char)
        index += 1
    return "".join(result)


def strip_rust_comments(source: str) -> str:
    result: list[str] = []
    index = 0
    length = len(source)
    while index < length:
        char = source[index]
        next_char = source[index + 1] if index + 1 < length else ""

        if char == "/" and next_char == "/":
            index += 2
            while index < length and source[index] != "\n":
                index += 1
            result.append("\n")
            continue

        if char == "/" and next_char == "*":
            index += 2
            depth = 1
            while index < length and depth > 0:
                if source[index : index + 2] == "/*":
                    depth += 1
                    index += 2
                    continue
                if source[index : index + 2] == "*/":
                    depth -= 1
                    index += 2
                    continue
                if source[index] == "\n":
                    result.append("\n")
                index += 1
            continue

        raw_match = re.match(r'r(#*)"', source[index:])
        if raw_match:
            hashes = raw_match.group(1)
            terminator = '"' + hashes
            raw_start = index
            index += len(raw_match.group(0))
            end_index = source.find(terminator, index)
            if end_index == -1:
                result.append(source[raw_start:])
                break
            index = end_index + len(terminator)
            result.append(source[raw_start:index])
            continue

        if char == '"':
            result.append(char)
            index += 1
            escaped = False
            while index < length:
                current = source[index]
                result.append(current)
                index += 1
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == '"':
                    break
            continue

        result.append(char)
        index += 1
    return "".join(result)


def check_rust_api_surface(root: Path) -> None:
    auxiliary_text = read_text(root, AUXILIARY_RUST)
    lib_text = read_text(root, RUST_DOMAIN_LIB)
    sanitized_auxiliary = strip_rust_comments_and_strings(auxiliary_text)
    errors: list[str] = []

    if "pub mod auxiliary;" not in lib_text:
        errors.append(f"{RUST_DOMAIN_LIB.as_posix()} must export pub mod auxiliary;")
    if "#![forbid(unsafe_code)]" not in lib_text:
        errors.append(f"{RUST_DOMAIN_LIB.as_posix()} must retain #![forbid(unsafe_code)]")

    for api_string in RUST_API_STRINGS:
        if api_string not in auxiliary_text:
            errors.append(f"{AUXILIARY_RUST.as_posix()} missing Rust API surface: {api_string}")
        if api_string not in lib_text:
            errors.append(f"{RUST_DOMAIN_LIB.as_posix()} missing Rust API export: {api_string}")

    for invariant_error in INVARIANT_ERROR_STRINGS:
        if invariant_error not in lib_text:
            errors.append(f"{RUST_DOMAIN_LIB.as_posix()} missing Phase 10 invariant error: {invariant_error}")

    for label, pattern in UNSAFE_RUST_PATTERNS:
        if pattern in sanitized_auxiliary:
            errors.append(f"{AUXILIARY_RUST.as_posix()} contains {label}: {pattern}")

    if errors:
        raise VerificationError("\n".join(errors))


def check_package_update(root: Path) -> None:
    rows = validate_manifest(root, AUXILIARY_BUILD_UPDATE_MANIFEST)
    blob = json.dumps(rows, sort_keys=True)
    errors = [needle for needle in PACKAGE_UPDATE_STRINGS if needle not in blob]

    runtime_paths = set()
    prebuilt_path_variables = set()
    update_build_surfaces = set()
    descriptor_commands = set()
    skip_flash_options = set()
    for row in rows:
        runtime_paths.update(str(item) for item in row.get("runtime_paths", []) if isinstance(item, str))
        prebuilt_path_variables.update(
            str(item) for item in row.get("prebuilt_path_variables", []) if isinstance(item, str)
        )
        update_build_surface = row.get("update_build_surface")
        if isinstance(update_build_surface, str):
            update_build_surfaces.add(update_build_surface)
        descriptor_command = row.get("descriptor_command")
        if isinstance(descriptor_command, str):
            descriptor_commands.add(descriptor_command)
        skip_flash_option = row.get("skip_flash_option")
        if isinstance(skip_flash_option, str):
            skip_flash_options.add(skip_flash_option)

    required_runtime_paths = {
        "/puppies/fw-dwarf.bin",
        "/puppies/fw-modularbed.bin",
        "/puppies/fw-xbuddy-extension.bin",
        "/mmu/fw.bin",
    }
    required_prebuilt_paths = {
        "DWARF_BINARY_PATH",
        "MODULARBED_BINARY_PATH",
        "XBUDDY_EXTENSION_BINARY_PATH",
    }
    required_surfaces = {
        "descriptor-generation",
        "resource-path",
        "prebuilt-path",
        "startup-flashing",
        "mmu-firmware-resource",
        "crash-dump",
    }

    errors.extend(sorted(required_runtime_paths - runtime_paths))
    errors.extend(sorted(required_prebuilt_paths - prebuilt_path_variables))
    errors.extend(sorted(required_surfaces - update_build_surfaces))
    if not any("utils/gen_puppies_descriptor.py" in command for command in descriptor_commands):
        errors.append("utils/gen_puppies_descriptor.py")
    if "PUPPY_SKIP_FLASH_FW" not in skip_flash_options:
        errors.append("PUPPY_SKIP_FLASH_FW")

    if errors:
        raise VerificationError(
            f"{AUXILIARY_BUILD_UPDATE_MANIFEST.as_posix()} missing package/update coverage: "
            + ", ".join(errors)
        )


def artifact_texts(root: Path) -> list[tuple[Path, str]]:
    paths = [*MANIFESTS.keys(), VALIDATION_CONTRACT]
    return [(path, read_text(root, path)) for path in paths]


def check_secret_markers(root: Path) -> None:
    errors: list[str] = []
    for path, text in artifact_texts(root):
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                errors.append(f"{path.as_posix()} contains forbidden payload or secret marker: {marker}")
    if errors:
        raise VerificationError("\n".join(errors))


def check_overclaims(root: Path) -> None:
    errors: list[str] = []
    for path, text in artifact_texts(root):
        lowered = text.lower()
        for phrase in OVERCLAIM_STRINGS:
            if phrase.lower() in lowered:
                errors.append(f"{path.as_posix()} contains non-local evidence overclaim: {phrase}")
    if errors:
        raise VerificationError("\n".join(errors))


def check_evidence_scope(root: Path) -> None:
    errors: list[str] = []
    try:
        all_manifest_rows(root)
    except VerificationError as error:
        errors.append(str(error))

    try:
        check_overclaims(root)
    except VerificationError as error:
        errors.append(str(error))

    try:
        check_validation_contract(root)
    except VerificationError as error:
        errors.append(str(error))

    if errors:
        raise VerificationError("\n".join(errors))


def check_validation_contract(root: Path) -> None:
    text = read_text(root, VALIDATION_CONTRACT)
    required_text = [
        PHASE_LIFECYCLE_ID,
        "Wave 0",
        "python3 tools/bazel/phase10_verify.py --quick",
        "phase10-verify",
        "hardware-smoke",
        "RS485",
        "Toolchanger",
        "MMU behavior over live transport",
        "Long-running",
    ]
    missing = [needle for needle in required_text if needle not in text]
    grouped_requirements = {
        "manual-hardware-required": ["manual-hardware-required", "Manual-Only Verifications"],
        "simulator-flow": ["simulator-flow", "simulator"],
    }
    for label, options in grouped_requirements.items():
        if not any(option in text for option in options):
            missing.append(label)
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation lifecycle contract text: "
            + ", ".join(missing)
        )


def require_file_contains(root: Path, path: Path, needles: list[str]) -> list[str]:
    text = read_text(root, path)
    return [f"{path.as_posix()} missing required wiring text: {needle}" for needle in needles if needle not in text]


def check_wiring(root: Path) -> None:
    required_files = [
        Path("tools/bazel/BUILD.bazel"),
        Path("BUILD.bazel"),
        Path("tools/bazel/rust_workflow.sh"),
        Path("justfile"),
    ]
    errors: list[str] = []
    for path in required_files:
        try:
            read_text(root, path)
        except VerificationError as error:
            errors.append(str(error))

    if errors:
        raise VerificationError("\n".join(errors))

    aggregate_text = "\n".join(read_text(root, path) for path in required_files)
    for needle in [
        "phase10_verify",
        "phase10_verify_tests",
        "phase10_auxiliary_controller_docs",
        "phase10_auxiliary_build_update_manifest",
        "phase10-verify:",
    ]:
        if needle not in aggregate_text:
            errors.append(f"Phase 10 wiring missing required text: {needle}")

    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase10-verify:",
                "bazel run //tools/bazel:phase10_verify_tests",
                "bazel run //tools/bazel:phase10_verify",
            ],
        )
    )
    if errors:
        raise VerificationError("\n".join(errors))


def check_security(root: Path) -> None:
    collect_errors([lambda: check_secret_markers(root), lambda: check_overclaims(root)])


def check_quick(root: Path) -> None:
    collect_errors(
        [
            lambda: check_manifests(root),
            lambda: check_rust_api_surface(root),
            lambda: check_package_update(root),
            lambda: check_evidence_scope(root),
            lambda: check_security(root),
            lambda: check_validation_contract(root),
        ]
    )


def run_command(root: Path, command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise VerificationError(
            f"{' '.join(command)} failed with exit code {result.returncode}\n{result.stdout}"
        )


def check_all(root: Path) -> None:
    check_quick(root)
    run_command(root, ["cargo", "fmt", "--all", "--", "--check"])
    run_command(root, ["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"])
    run_command(root, ["cargo", "build", "--all-targets", "--all-features"])
    run_command(root, ["cargo", "test", "--all-features"])


def collect_errors(checks: list[Callable[[], object]]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 10 auxiliary-controller parity artifacts.")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to inspect; useful for Plan 10-04 wiring fixtures.",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--quick", action="store_true", help="run local static Phase 10 verification")
    modes.add_argument("--all", action="store_true", help="run static verification plus Rust checks")
    modes.add_argument("--manifests-only", action="store_true", help="verify only Phase 10 manifests")
    modes.add_argument("--rust-only", action="store_true", help="verify only Rust auxiliary API surface")
    modes.add_argument(
        "--package-update-only",
        action="store_true",
        help="verify only auxiliary build/package/update coverage",
    )
    modes.add_argument("--evidence-only", action="store_true", help="verify only proof-scope evidence guards")
    modes.add_argument("--security-only", action="store_true", help="verify only payload and overclaim guards")
    modes.add_argument(
        "--wiring-only",
        action="store_true",
        help="verify only Phase 10 Bazel/just wiring strings against --repo-root",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else ROOT

    if args.all:
        check = lambda: check_all(root)
    elif args.manifests_only:
        check = lambda: check_manifests(root)
    elif args.rust_only:
        check = lambda: check_rust_api_surface(root)
    elif args.package_update_only:
        check = lambda: check_package_update(root)
    elif args.evidence_only:
        check = lambda: check_evidence_scope(root)
    elif args.security_only:
        check = lambda: check_security(root)
    elif args.wiring_only:
        check = lambda: check_wiring(root)
    else:
        check = lambda: check_quick(root)

    try:
        check()
    except VerificationError as error:
        print(f"Phase 10 auxiliary-controller verification failed:\n{error}", file=sys.stderr)
        return 1

    print("Phase 10 auxiliary-controller verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
