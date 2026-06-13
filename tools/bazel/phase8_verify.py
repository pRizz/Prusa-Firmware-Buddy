#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
PHASE = "08-local-interface-and-workflow-parity"
PHASE_LIFECYCLE_ID = "8-2026-06-13T16-58-45"

GUI_WORKFLOWS_MANIFEST = Path("tools/bazel/manifests/phase8_gui_workflows.json")
DISPLAY_LAYOUTS_MANIFEST = Path("tools/bazel/manifests/phase8_display_layouts.json")
CONCERN_DISPOSITIONS_MANIFEST = Path("tools/bazel/manifests/phase8_concern_dispositions.json")
VALIDATION_CONTRACT = Path(".planning/phases/08-local-interface-and-workflow-parity/08-VALIDATION.md")
GUI_RUST = Path("rust/crates/domain/src/gui.rs")
RUST_DOMAIN_LIB = Path("rust/crates/domain/src/lib.rs")

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

COMMON_FIELDS = [
    "id",
    "requirement_id",
    "reference_sources",
    "reference_behavior",
    "rust_surface",
    "display_classes",
    "evidence_class",
    "proof_scope",
    "non_local_evidence",
    "intentional_delta",
]

LAYOUT_FIELDS = [
    *COMMON_FIELDS,
    "layout_values",
]

CONCERN_FIELDS = [
    "id",
    "concern_id",
    "requirement_id",
    "reference_sources",
    "disposition",
    "phase8_handling",
    "evidence_class",
    "proof_scope",
    "intentional_delta",
    "regression_guard",
]

WORKFLOW_ROW_IDS = [
    "screen-stack-home-bootstrap",
    "screen-stack-bounded-fixed-storage",
    "dialog-fsm-display-config",
    "menu-settings-and-home-entry",
    "print-preview-entry",
    "print-control-pause",
    "print-control-resume",
    "print-control-cancel-abort-request",
    "print-control-stop-confirmation",
    "print-control-reprint",
    "setup-selftest-calibration-wizards",
    "connect-registration-local-entry",
    "prusalink-credential-local-display",
    "warning-redscreen-error-surfaces",
]

LAYOUT_ROW_IDS = [
    "display-class-selectors",
    "mini-240x320-gui-defaults",
    "large-480x320-gui-defaults",
    "menu-layout-display-differences",
    "print-preview-layout-240x320",
    "print-preview-layout-480x320",
    "print-progress-layout-240x320",
    "print-progress-layout-480x320",
    "localized-text-font-contracts",
    "warning-dialog-layout",
    "redscreen-bsod-error-layout",
    "connect-registration-layout",
]

BOTH_DISPLAY_CLASS_LAYOUT_ROWS = {
    "display-class-selectors",
    "menu-layout-display-differences",
    "localized-text-font-contracts",
    "warning-dialog-layout",
    "redscreen-bsod-error-layout",
    "connect-registration-layout",
}

CONCERN_ROW_IDS = [
    "concern-cl-008-home-screen-flash-start",
    "concern-cl-011-crash-dump-warning-surface",
    "concern-cl-003-generated-gui-resource-drift",
    "concern-cl-019-tracked-font-header-churn",
]

CONCERN_IDS = [
    "CL-008",
    "CL-011",
    "CL-003",
    "CL-019",
]

SEMANTIC_ACTION_BY_WORKFLOW_ROW = {
    "print-preview-entry": "preview",
    "print-control-pause": "pause",
    "print-control-resume": "resume",
    "print-control-cancel-abort-request": "cancel",
    "print-control-stop-confirmation": "stop",
    "print-control-reprint": "reprint",
}

PRINT_CONTROL_SEMANTIC_ACTIONS = {
    "pause",
    "resume",
    "cancel",
    "stop",
    "reprint",
}

CONCERN_REQUIRED_TEXT = [
    "CL-008",
    "no-op flash action",
    "event re-enable behavior",
    "CL-011",
    "Crash detected. Save it to USB?",
    "sensitive information",
    "no raw crash dump memory contents",
]

CONCERN_REQUIRED_STRINGS_BY_ID = {
    "CL-008": [
        "no-op flash action",
        "event re-enable behavior",
        "src/gui/screen_home.cpp",
    ],
    "CL-011": [
        "Crash detected. Save it to USB?",
        "sensitive information",
        "no raw crash dump memory contents",
    ],
}

RUST_API_STRINGS = [
    "DisplayClass",
    "GuiWorkflow",
    "GuiSurface",
    "GuiEvidenceClass",
    "GuiProofScope",
    "GuiParityRowId",
    "LocalizationSurface",
    "IntentionalDeltaStatus",
    "GuiSemanticAction",
    "GuiParityContract",
]

SECRET_MARKERS = [
    "password_value",
    "token_value",
    "certificate_bytes",
    "raw_dump",
    "ram_bytes",
    "BEGIN PRIVATE KEY",
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
    "hardware display verified locally",
    "physical lcd proof passed",
    "physical touch proof passed",
    "touch proof passed",
    "full simulator proof passed",
    "simulator display proof passed",
    "network service parity passed",
    "connect tls parity passed",
    "tls parity passed",
    "transfer parity passed",
    "auxiliary runtime parity passed",
    "cutover evidence complete",
]

PHASE8_ARTIFACTS_FOR_MARKER_SCAN = [
    GUI_WORKFLOWS_MANIFEST,
    DISPLAY_LAYOUTS_MANIFEST,
    CONCERN_DISPOSITIONS_MANIFEST,
    VALIDATION_CONTRACT,
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
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a non-empty list of strings")
    return value


def require_existing_reference_sources(row: dict[str, Any], row_name: str) -> set[str]:
    reference_sources = require_list_of_strings(row, "reference_sources", row_name)
    existing_paths: set[str] = set()
    root = ROOT.resolve()
    for reference_source in reference_sources:
        relative_path = Path(reference_source)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise VerificationError(f"{row_name} reference source must be repo-relative: {reference_source}")

        full_path = (root / relative_path).resolve()
        try:
            full_path.relative_to(root)
        except ValueError as error:
            raise VerificationError(f"{row_name} reference source escapes repo: {reference_source}") from error

        if not full_path.exists():
            raise VerificationError(f"{row_name} references missing source path: {reference_source}")
        existing_paths.add(reference_source)
    return existing_paths


def require_requirement_id(row: dict[str, Any], row_name: str) -> None:
    requirement_id = require_string(row, "requirement_id", row_name)
    if requirement_id != "IFCE-01":
        raise VerificationError(f"{row_name} requirement_id must be IFCE-01")


def require_evidence_and_scope(row: dict[str, Any], row_name: str) -> None:
    evidence_class = require_string(row, "evidence_class", row_name)
    if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
        allowed = ", ".join(sorted(ALLOWED_EVIDENCE_CLASSES))
        raise VerificationError(
            f"{row_name} evidence_class {evidence_class!r} must be one of: {allowed}"
        )

    proof_scope = require_string(row, "proof_scope", row_name)
    if proof_scope not in {"local", "non-local"}:
        raise VerificationError(f"{row_name} proof_scope must be local or non-local")
    if proof_scope == "local" and evidence_class in NON_LOCAL_EVIDENCE_CLASSES:
        raise VerificationError(
            f"{row_name} proof_scope local cannot be paired with {evidence_class} evidence"
        )


def require_display_classes(row: dict[str, Any], row_name: str) -> set[str]:
    display_classes = set(require_list_of_strings(row, "display_classes", row_name))
    allowed = {"240x320", "480x320", "mock"}
    invalid = sorted(display_classes - allowed)
    if invalid:
        raise VerificationError(f"{row_name} contains invalid display_classes: {', '.join(invalid)}")
    return display_classes


def validate_rows(
    path: Path,
    collection_name: str,
    fields: list[str],
    required_ids: list[str],
) -> list[dict[str, Any]]:
    data = read_json(path)
    rows = require_top_level(data, path, collection_name)
    row_ids = require_unique(rows, "id", path)
    require_ids(row_ids, required_ids, f"{collection_name} row IDs")

    errors: list[str] = []
    for row in rows:
        row_name = f"{path.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, fields, row_name)
            require_requirement_id(row, row_name)
            require_existing_reference_sources(row, row_name)
            require_evidence_and_scope(row, row_name)
            require_display_classes(row, row_name)
        except VerificationError as error:
            errors.append(str(error))

    if errors:
        raise VerificationError("\n".join(errors))
    return rows


def check_gui_workflows_manifest() -> None:
    rows = validate_rows(GUI_WORKFLOWS_MANIFEST, "workflow_contracts", COMMON_FIELDS, WORKFLOW_ROW_IDS)
    row_by_id = {row["id"]: row for row in rows}
    errors: list[str] = []

    for row_id, expected_action in SEMANTIC_ACTION_BY_WORKFLOW_ROW.items():
        row = row_by_id[row_id]
        actual_action = row.get("semantic_action_id")
        if actual_action != expected_action:
            errors.append(f"{GUI_WORKFLOWS_MANIFEST.as_posix()} row {row_id} must set semantic_action_id to {expected_action}")

    action_to_row = {
        row.get("semantic_action_id"): row["id"]
        for row in rows
        if isinstance(row.get("semantic_action_id"), str)
    }
    for action in [*sorted(PRINT_CONTROL_SEMANTIC_ACTIONS), "preview"]:
        if action not in action_to_row:
            errors.append(f"missing GUI semantic_action_id coverage: {action}")

    for row in rows:
        row_id = row["id"]
        maybe_action = row.get("semantic_action_id")
        if maybe_action is None:
            continue
        if not isinstance(maybe_action, str):
            errors.append(f"{GUI_WORKFLOWS_MANIFEST.as_posix()} row {row_id} semantic_action_id must be a string")
            continue
        if maybe_action == "preview" and row_id != "print-preview-entry":
            errors.append(
                f"{GUI_WORKFLOWS_MANIFEST.as_posix()} row {row_id} binds preview but only print-preview-entry may use it"
            )
        if maybe_action in PRINT_CONTROL_SEMANTIC_ACTIONS and not row_id.startswith("print-control-"):
            errors.append(
                f"{GUI_WORKFLOWS_MANIFEST.as_posix()} row {row_id} binds {maybe_action} but print-control actions must appear only on print-control-* workflow rows"
            )
        if maybe_action not in PRINT_CONTROL_SEMANTIC_ACTIONS and maybe_action != "preview":
            errors.append(f"{GUI_WORKFLOWS_MANIFEST.as_posix()} row {row_id} has unknown semantic_action_id {maybe_action}")

    if errors:
        raise VerificationError("\n".join(errors))


def check_display_layout_manifest() -> None:
    rows = validate_rows(DISPLAY_LAYOUTS_MANIFEST, "layout_contracts", LAYOUT_FIELDS, LAYOUT_ROW_IDS)
    errors: list[str] = []
    all_display_classes: set[str] = set()
    expected_warning_text_rects = {
        "240x320": {"x": 6, "y": 112, "width": 228, "height": 168},
        "480x320": {"x": 26, "y": 182, "width": 428, "height": 100},
    }
    for row in rows:
        row_id = row["id"]
        row_name = f"{DISPLAY_LAYOUTS_MANIFEST.as_posix()} row {row_id}"
        display_classes = set(row["display_classes"])
        all_display_classes.update(display_classes)
        if row_id in BOTH_DISPLAY_CLASS_LAYOUT_ROWS and not {"240x320", "480x320"}.issubset(display_classes):
            errors.append(f"{row_name} must include both 240x320 and 480x320 display_classes")
        if row_id == "warning-dialog-layout":
            layout_values = row.get("layout_values")
            if not isinstance(layout_values, dict):
                errors.append(f"{row_name} layout_values must be an object")
                continue
            for display_class, expected_rect in expected_warning_text_rects.items():
                display_layout = layout_values.get(display_class)
                if not isinstance(display_layout, dict):
                    errors.append(f"{row_name} layout_values must include {display_class}")
                    continue
                if "WarningDlgDescriptionRect" in display_layout:
                    errors.append(f"{row_name} {display_class} must use active WarningDlgTextRect, not stale WarningDlgDescriptionRect")
                if display_layout.get("WarningDlgTextRect") != expected_rect:
                    errors.append(f"{row_name} {display_class} WarningDlgTextRect must match GuiDefaults active text geometry")

    for display_class in ["240x320", "480x320"]:
        if display_class not in all_display_classes:
            errors.append(f"{DISPLAY_LAYOUTS_MANIFEST.as_posix()} missing aggregate display class coverage: {display_class}")

    if errors:
        raise VerificationError("\n".join(errors))


def check_concern_dispositions() -> None:
    data = read_json(CONCERN_DISPOSITIONS_MANIFEST)
    rows = require_top_level(data, CONCERN_DISPOSITIONS_MANIFEST, "concerns")
    row_ids = require_unique(rows, "id", CONCERN_DISPOSITIONS_MANIFEST)
    concern_ids = require_unique(rows, "concern_id", CONCERN_DISPOSITIONS_MANIFEST)

    errors: list[str] = []
    missing_rows = sorted(set(CONCERN_ROW_IDS) - row_ids)
    if missing_rows:
        missing_labels = [
            "CL-008" if "cl-008" in row_id else "CL-011" if "cl-011" in row_id else row_id
            for row_id in missing_rows
        ]
        errors.append("missing required concern rows: " + ", ".join(missing_labels))
    missing_concerns = sorted(set(CONCERN_IDS) - concern_ids)
    if missing_concerns:
        errors.append("missing required concern IDs: " + ", ".join(missing_concerns))

    for row in rows:
        row_name = f"{CONCERN_DISPOSITIONS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, CONCERN_FIELDS, row_name)
            require_requirement_id(row, row_name)
            require_existing_reference_sources(row, row_name)
            require_evidence_and_scope(row, row_name)
            concern_id = require_string(row, "concern_id", row_name)
            guard = row.get("regression_guard")
            if not isinstance(guard, dict):
                raise VerificationError(f"{row_name} regression_guard must be an object")
            guard_strings = guard.get("required_strings")
            if not isinstance(guard_strings, list) or not all(isinstance(item, str) for item in guard_strings):
                raise VerificationError(f"{row_name} regression_guard.required_strings must be a list of strings")
            missing_guard_strings = [
                needle
                for needle in CONCERN_REQUIRED_STRINGS_BY_ID.get(concern_id, [])
                if needle not in guard_strings
            ]
            if missing_guard_strings:
                raise VerificationError(
                    f"{row_name} missing regression_guard.required_strings: "
                    + ", ".join(missing_guard_strings)
                )
        except VerificationError as error:
            errors.append(str(error))

    haystack = json.dumps(rows, sort_keys=True)
    for needle in CONCERN_REQUIRED_TEXT:
        if needle not in haystack:
            errors.append(f"{CONCERN_DISPOSITIONS_MANIFEST.as_posix()} missing required concern text: {needle}")

    if errors:
        raise VerificationError("\n".join(errors))


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
    gui_text = read_text(GUI_RUST)
    errors: list[str] = []

    if "#![forbid(unsafe_code)]" not in lib_text:
        errors.append(f"{RUST_DOMAIN_LIB.as_posix()} must contain #![forbid(unsafe_code)]")

    missing_gui = [needle for needle in RUST_API_STRINGS if needle not in gui_text]
    if missing_gui:
        errors.append(f"{GUI_RUST.as_posix()} missing required Rust API strings: {', '.join(missing_gui)}")

    missing_lib = [needle for needle in RUST_API_STRINGS if needle not in lib_text]
    if missing_lib:
        errors.append(f"{RUST_DOMAIN_LIB.as_posix()} missing required GUI exports: {', '.join(missing_lib)}")

    unsafe_findings = unsafe_findings_for_file(GUI_RUST, gui_text)
    if unsafe_findings:
        errors.append("Phase 8 GUI Rust module unsafe check failed:\n" + "\n".join(unsafe_findings))

    if errors:
        raise VerificationError("\n".join(errors))


def require_text_contains(path_label: str, text: str, needles: list[str]) -> list[str]:
    return [f"{path_label} missing {needle}" for needle in needles if needle not in text]


def find_exact_line(text: str, expected: str) -> int | None:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == expected:
            return index
    return None


def check_bazel_surface() -> None:
    root_build = read_text("BUILD.bazel")
    tools_build = read_text("tools/bazel/BUILD.bazel")
    rust_workflow = read_text("tools/bazel/rust_workflow.sh")
    errors: list[str] = []

    errors.extend(
        require_text_contains(
            "tools/bazel/BUILD.bazel",
            tools_build,
            [
                "phase8_verify",
                "phase8_verify_tests",
                "phase8_verify.py",
                "phase8_verify_test.py",
                "phase8_gui_workflows.json",
                "phase8_display_layouts.json",
                "phase8_concern_dispositions.json",
                "//:phase8_local_interface_docs",
                "//:rust_workspace_sources",
            ],
        )
    )
    errors.extend(
        require_text_contains(
            "BUILD.bazel",
            root_build,
            [
                "phase8_local_interface_docs",
                "phase8_verify",
                "phase8_verify_tests",
            ],
        )
    )
    errors.extend(
        require_text_contains(
            "tools/bazel/rust_workflow.sh",
            rust_workflow,
            [
                "phase8_verify)",
                "python3 tools/bazel/phase8_verify.py --all",
                "phase8_verify_tests)",
                "python3 tools/bazel/phase8_verify_test.py",
            ],
        )
    )

    if errors:
        raise VerificationError("\n".join(errors))


def check_just_surface() -> None:
    justfile = read_text("justfile")
    errors = require_text_contains(
        "justfile",
        justfile,
        [
            "phase8-verify:",
            "bazel run //tools/bazel:phase8_verify_tests",
            "bazel run //tools/bazel:phase8_verify",
        ],
    )
    tests_index = find_exact_line(justfile, "bazel run //tools/bazel:phase8_verify_tests")
    verify_index = find_exact_line(justfile, "bazel run //tools/bazel:phase8_verify")
    if tests_index is None or verify_index is None or tests_index > verify_index:
        errors.append("justfile must run phase8_verify_tests before phase8_verify")
    if errors:
        raise VerificationError("\n".join(errors))


def check_validation_contract() -> None:
    validation = read_text(VALIDATION_CONTRACT)
    required_strings = [
        "status: complete",
        "nyquist_compliant: true",
        "wave_0_complete: true",
        f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
        "Quick run command",
        "python3 tools/bazel/phase8_verify.py --quick",
        "Full suite command",
        "just phase8-verify",
        "08-W0-01",
        "08-W0-05",
        "manual-hardware-required",
        "hardware-smoke",
        "simulator-flow",
    ]
    missing = [needle for needle in required_strings if needle not in validation]
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation contract text: "
            + ", ".join(missing)
        )


def check_secret_markers() -> None:
    findings: list[str] = []
    for path in PHASE8_ARTIFACTS_FOR_MARKER_SCAN:
        text = read_text(path)
        markers = [marker for marker in SECRET_MARKERS if marker in text]
        if markers:
            findings.append(
                f"{path.as_posix()} contains forbidden secret or crash dump byte marker(s): "
                + ", ".join(markers)
            )
    if findings:
        raise VerificationError("\n".join(findings))


def check_no_phase8_overclaim() -> None:
    phase_dir = ROOT / ".planning/phases/08-local-interface-and-workflow-parity"
    paths = [
        GUI_WORKFLOWS_MANIFEST,
        DISPLAY_LAYOUTS_MANIFEST,
        CONCERN_DISPOSITIONS_MANIFEST,
        VALIDATION_CONTRACT,
        *[path.relative_to(ROOT) for path in phase_dir.glob("08-*-SUMMARY.md")],
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
        raise VerificationError("Phase 8 artifacts overclaim local evidence:\n" + "\n".join(findings))


def collect(checks: list[Callable[[], None]]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))


def check_quick() -> None:
    collect(
        [
            check_gui_workflows_manifest,
            check_display_layout_manifest,
            check_concern_dispositions,
            check_rust_api_surface,
            check_validation_contract,
            check_bazel_surface,
            check_just_surface,
            check_secret_markers,
            check_no_phase8_overclaim,
        ]
    )


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
    parser = argparse.ArgumentParser(description="Verify Phase 8 local interface and workflow parity surfaces")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Run static Phase 8 manifest, Rust API, facade, validation, secret, and overclaim checks")
    mode.add_argument("--all", action="store_true", help="Run quick checks plus Cargo format, lint, build, and tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        check_quick()
        if args.all:
            check_rust_toolchain()

        print("Phase 8 local interface and workflow parity verification passed")
        return 0
    except VerificationError as error:
        print(
            f"Phase 8 local interface and workflow parity verification failed: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
