#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "10-auxiliary-controllers-and-expansion-ecosystem"
PHASE_LIFECYCLE_ID = "10-2026-06-14T15-08-30"

VALIDATION_CONTRACT = Path(
    ".planning/phases/10-auxiliary-controllers-and-expansion-ecosystem/10-VALIDATION.md"
)
AUXILIARY_RUST = Path("rust/crates/domain/src/auxiliary.rs")
AUXILIARY_MODULE_DIR = Path("rust/crates/domain/src/auxiliary")
RUST_DOMAIN_LIB = Path("rust/crates/domain/src/lib.rs")

AUXILIARY_CONTROLLERS_MANIFEST = Path(
    "tools/bazel/manifests/phase10_auxiliary_controllers.json")
MMU_TRANSPORT_MANIFEST = Path(
    "tools/bazel/manifests/phase10_mmu_transport.json")
MODBUS_RS485_MANIFEST = Path("tools/bazel/manifests/phase10_modbus_rs485.json")
TOOLCHANGER_DOCK_OFFSETS_MANIFEST = Path(
    "tools/bazel/manifests/phase10_toolchanger_dock_offsets.json")
AUXILIARY_BUILD_UPDATE_MANIFEST = Path(
    "tools/bazel/manifests/phase10_auxiliary_build_update.json")
CONCERN_DISPOSITIONS_MANIFEST = Path(
    "tools/bazel/manifests/phase10_concern_dispositions.json")

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
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def read_json(root: Path, path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read_text(root, path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{path.as_posix()} is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise VerificationError(
            f"{path.as_posix()} must contain a top-level JSON object")
    return data


def is_empty(value: object) -> bool:
    return value in ("", [], {}, None)


def row_blob(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True)


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a non-empty list of strings")
    return value


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields if field in row and is_empty(row[field])
    ]
    legacy = [
        field for field in ["requirement", "source_paths"] if field in row
    ]
    details = []
    if missing:
        details.append(f"missing required fields: {', '.join(missing)}")
    if empty:
        details.append(f"empty required fields: {', '.join(empty)}")
    if legacy:
        details.append(
            "uses legacy manifest schema fields instead of canonical requirement_id/reference_sources: "
            + ", ".join(legacy))
    if details:
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_top_level(root: Path, path: Path,
                      collection_name: str) -> list[dict[str, Any]]:
    data = read_json(root, path)
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


def require_unique_ids(rows: list[dict[str, Any]], path: Path) -> set[str]:
    values: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get("id")
        if not isinstance(value, str):
            raise VerificationError(
                f"{path.as_posix()} row has non-string id: {value!r}")
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
        raise VerificationError(
            f"{path.as_posix()} missing required row IDs: {', '.join(missing)}"
        )


def require_reference_sources(root: Path, row: dict[str, Any],
                              row_name: str) -> None:
    reference_sources = require_list_of_strings(row, "reference_sources",
                                                row_name)
    resolved_root = root.resolve()
    for reference_source in reference_sources:
        relative_path = Path(reference_source)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise VerificationError(
                f"{row_name} reference source must be repo-relative: {reference_source}"
            )

        full_path = (resolved_root / relative_path).resolve()
        try:
            full_path.relative_to(resolved_root)
        except ValueError as error:
            raise VerificationError(
                f"{row_name} reference source escapes repo: {reference_source}"
            ) from error

        if not full_path.exists():
            raise VerificationError(
                f"{row_name} references missing source path: {reference_source}"
            )


def extract_parse_strings(rust_source: str, type_name: str) -> set[str]:
    sanitized_source = strip_rust_comments(rust_source)
    impl_marker = f"impl {type_name}"
    impl_start = sanitized_source.find(impl_marker)
    if impl_start == -1:
        raise VerificationError(
            f"{AUXILIARY_RUST.as_posix()} missing impl {type_name}")

    next_impl = sanitized_source.find("\nimpl ", impl_start + len(impl_marker))
    impl_body = sanitized_source[
        impl_start:] if next_impl == -1 else sanitized_source[
            impl_start:next_impl]
    parse_marker = "pub fn parse"
    parse_start = impl_body.find(parse_marker)
    if parse_start == -1:
        raise VerificationError(
            f"{AUXILIARY_RUST.as_posix()} missing {type_name}::parse")

    parse_body = impl_body[parse_start:]
    return set(re.findall(r'"([^"]+)"\s*=>\s*Ok\(Self::', parse_body))


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
                if source[index:index + 2] == "/*":
                    depth += 1
                    index += 2
                    continue
                if source[index:index + 2] == "*/":
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
                if source[index:index + 2] == "/*":
                    depth += 1
                    index += 2
                    continue
                if source[index:index + 2] == "*/":
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


def collect_errors(checks: list[Callable[[], object]]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))
