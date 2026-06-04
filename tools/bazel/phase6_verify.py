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
PHASE = "06-printing-core-safety-and-feature-gates"
PHASE_LIFECYCLE_ID = "6-2026-06-04T09-48-48"

PRINTING_MANIFEST = Path("tools/bazel/manifests/phase6_printing_core.json")
SAFETY_MANIFEST = Path("tools/bazel/manifests/phase6_safety_gates.json")
FEATURE_MANIFEST = Path("tools/bazel/manifests/phase6_feature_gates.json")
CONCERN_MANIFEST = Path("tools/bazel/manifests/phase6_concern_dispositions.json")

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

REQUIRED_PRINTING_FIELDS = [
    "id",
    "requirement",
    "source_paths",
    "reference_behavior",
    "print_surface",
    "evidence_class",
    "rust_surface",
    "intentional_delta",
]

REQUIRED_SAFETY_FIELDS = [
    "id",
    "requirement",
    "source_paths",
    "safety_flow",
    "preserved_behavior",
    "evidence_class",
    "rust_surface",
    "non_local_evidence",
]

REQUIRED_FEATURE_FIELDS = [
    "id",
    "requirement",
    "source_paths",
    "gate",
    "profile_keys",
    "expected_state",
    "evidence_class",
    "rust_surface",
]

REQUIRED_CONCERN_FIELDS = [
    "id",
    "concern_id",
    "requirement",
    "source_paths",
    "disposition",
    "phase6_handling",
    "evidence_class",
    "intentional_delta",
]

REQUIRED_PRINTING_ROW_IDS = [
    "print-gcode-routing",
    "print-serial-start-pause-resume-cancel",
    "print-file-start-preview-stream-recovery",
    "print-planner-visible-flow",
    "print-buddy-gmcode-handlers",
]

REQUIRED_SAFETY_ROW_IDS = [
    "thermal-safety-transitions",
    "motion-safe-output-and-emergency-stop",
    "selftest-calibration-crash-recovery",
    "power-panic-recovery",
    "fatal-redscreen-bsod-assert",
    "watchdog-and-crash-dump-boundary",
    "probe-loadcell-classification",
]

REQUIRED_FEATURE_ROW_IDS = [
    "filament-sensor-gates",
    "tmc-motion-driver-gates",
    "precise-homing-gates",
    "input-shaper-gates",
    "phase-burst-stepping-gates",
    "loadcell-hx717-gates",
    "bed-chamber-door-gates",
    "mmu2-gates",
    "nfc-leds-gates",
    "toolchanger-xbuddy-extension-gates",
]

REQUIRED_CONCERN_ROW_IDS = [
    "concern-cl-007-probe-analysis",
    "concern-cl-008-home-screen-flash-start",
    "concern-cl-011-crash-dump-handling",
    "concern-cl-014-rng-fallback",
    "concern-cl-024-stm32g0-irq",
    "concern-cl-002-mmu-reporting",
    "concern-tmc-motion-driver-retention",
]

REQUIRED_CONCERN_IDS = [
    "CL-007",
    "CL-008",
    "CL-011",
    "CL-014",
    "CL-024",
    "CL-002",
    "phase6-tmc-motion-driver-retention",
]

REQUIRED_PRINTING_SOURCE_PATHS = [
    "lib/Marlin/",
    "lib/AddMarlin.cmake",
    "src/common/marlin_server.cpp",
    "src/common/marlin_client.cpp",
    "src/common/marlin_server_request.hpp",
    "src/common/marlin_client_queue.hpp",
    "src/common/marlin_vars.cpp",
    "src/common/serial_printing.cpp",
    "src/common/gcode/",
    "src/marlin_stubs/gcode.cpp",
]

REQUIRED_SAFETY_SOURCE_PATHS = [
    "src/common/safe_state.cpp",
    "src/common/feature/safety_timer/",
    "src/common/power_panic.cpp",
    "src/common/crash_dump/",
    "src/common/feature/emergency_stop/",
    "src/common/selftest/",
    "src/common/probe_analysis.cpp",
    "src/common/Pin.cpp",
    "src/common/random_hw.cpp",
    "src/common/wdt.cpp",
    "rust/crates/runtime-adapter/src/panic_boundary.rs",
]

REQUIRED_FEATURE_GATE_STRINGS = [
    "PRINTERS_WITH_FILAMENT_SENSOR_BINARY",
    "PRINTERS_WITH_FILAMENT_SENSOR_ADC",
    "HAS_SIDE_FSENSOR",
    "HAS_TRINAMIC",
    "HAS_ADC_SIDE_FSENSOR",
    "HAS_TMC_UART",
    "HAS_PRECISE_HOMING",
    "HAS_PRECISE_HOMING_COREXY",
    "HAS_INPUT_SHAPER_CALIBRATION",
    "HAS_PHASE_STEPPING",
    "HAS_PHASE_STEPPING_CALIBRATION",
    "HAS_BURST_STEPPING",
    "HAS_LOADCELL",
    "HAS_LOADCELL_HX717",
    "HAS_LOCAL_BED",
    "HAS_MODULAR_BED",
    "HAS_REMOTE_BED",
    "HAS_CHAMBER_API",
    "HAS_CHAMBER_FILTRATION_API",
    "HAS_DOOR_SENSOR",
    "HAS_MMU2",
    "HAS_MMU2_OVER_UART",
    "HAS_NFC",
    "HAS_LEDS",
    "HAS_SIDE_LEDS",
    "HAS_TOOLCHANGER",
    "HAS_XBUDDY_EXTENSION",
]

PHASE6_ARTIFACTS = [
    PRINTING_MANIFEST.as_posix(),
    SAFETY_MANIFEST.as_posix(),
    FEATURE_MANIFEST.as_posix(),
    CONCERN_MANIFEST.as_posix(),
]

VALIDATION_CONTRACT = Path(
    ".planning/phases/06-printing-core-safety-and-feature-gates/06-VALIDATION.md"
)

RUST_DOMAIN_LIB = Path("rust/crates/domain/src/lib.rs")
PHASE6_DOMAIN_RUST_FILES = [
    Path("rust/crates/domain/src/print.rs"),
    Path("rust/crates/domain/src/safety.rs"),
    Path("rust/crates/domain/src/feature.rs"),
]

REQUIRED_RUST_API_STRINGS = {
    Path("rust/crates/domain/src/print.rs"): [
        "FixtureId",
        "PrintJobState",
        "PrintSource",
        "PrintCommand",
        "PlannerFlowState",
        "CommandRoute",
        "route_gcode_mnemonic",
        "transition_print_state",
    ],
    Path("rust/crates/domain/src/safety.rs"): [
        "SafetyFlow",
        "SafetyAction",
        "EvidenceClass",
        "FatalPathPolicy",
        "SafetyPolicySurface",
        "classify_safety_flow",
    ],
    Path("rust/crates/domain/src/feature.rs"): [
        "Phase6FeatureGate",
        "Phase6FeatureGates",
        "BurstSteppingMode",
        "GateState",
        "HasAdcSideFilamentSensor",
        "HasChamberFiltrationApi",
        "HasLoadcellHx717",
        "HasMmu2OverUart",
        "OutOfScopePhase10",
    ],
}

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
    "network parity implemented",
    "auth implemented",
    "crypto implemented",
    "gui parity implemented",
    "storage parity implemented",
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


def is_empty_required_field(field: str, value: object) -> bool:
    if field == "intentional_delta" and value is None:
        return False
    return is_empty(value)


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
    if missing:
        raise VerificationError(f"{row_name} missing required fields: {', '.join(missing)}")

    empty = [field for field in fields if is_empty_required_field(field, row[field])]
    if empty:
        raise VerificationError(f"{row_name} has empty required fields: {', '.join(empty)}")


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


def require_evidence_class(row: dict[str, Any], row_name: str) -> None:
    evidence_class = require_string(row, "evidence_class", row_name)
    if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
        allowed = ", ".join(sorted(ALLOWED_EVIDENCE_CLASSES))
        raise VerificationError(f"{row_name} evidence_class must be one of: {allowed}")


def require_requirement(row: dict[str, Any], row_name: str, expected: str | set[str]) -> None:
    requirement = require_string(row, "requirement", row_name)
    if isinstance(expected, str):
        if requirement != expected:
            raise VerificationError(f"{row_name} requirement must be {expected}")
        return

    if requirement not in expected:
        allowed = ", ".join(sorted(expected))
        raise VerificationError(f"{row_name} requirement must be one of: {allowed}")


def require_source_coverage(source_paths: set[str], required_paths: list[str], label: str) -> None:
    missing = sorted(set(required_paths) - source_paths)
    if missing:
        raise VerificationError(f"missing required {label} source coverage: {', '.join(missing)}")


def require_text_coverage(rows: list[dict[str, Any]], required_text: list[str], label: str) -> None:
    haystack = json.dumps(rows, sort_keys=True)
    missing = [needle for needle in required_text if needle not in haystack]
    if missing:
        raise VerificationError(f"missing required {label}: {', '.join(missing)}")


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


def validate_manifest(
    path: Path,
    collection_name: str,
    fields: list[str],
    required_ids: list[str],
    expected_requirement: str | set[str],
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
        all_source_paths.update(require_existing_source_paths(row, row_name))
    return rows, all_source_paths


def check_printing_manifest() -> None:
    _, source_paths = validate_manifest(
        PRINTING_MANIFEST,
        "printing_contracts",
        REQUIRED_PRINTING_FIELDS,
        REQUIRED_PRINTING_ROW_IDS,
        "CORE-03",
    )
    require_source_coverage(source_paths, REQUIRED_PRINTING_SOURCE_PATHS, "printing")


def check_safety_manifest() -> None:
    rows, source_paths = validate_manifest(
        SAFETY_MANIFEST,
        "safety_gates",
        REQUIRED_SAFETY_FIELDS,
        REQUIRED_SAFETY_ROW_IDS,
        "CORE-04",
    )
    require_source_coverage(source_paths, REQUIRED_SAFETY_SOURCE_PATHS, "safety")
    require_text_coverage(rows, ["manual-hardware-required", "source-audit"], "safety evidence classes")


def check_feature_manifest() -> None:
    rows, _ = validate_manifest(
        FEATURE_MANIFEST,
        "feature_gates",
        REQUIRED_FEATURE_FIELDS,
        REQUIRED_FEATURE_ROW_IDS,
        "CORE-05",
    )
    for row in rows:
        row_name = f"{FEATURE_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        require_list_of_strings(row, "profile_keys", row_name)
    require_text_coverage(rows, REQUIRED_FEATURE_GATE_STRINGS, "feature gate strings")


def check_concern_manifest() -> None:
    rows, _ = validate_manifest(
        CONCERN_MANIFEST,
        "concerns",
        REQUIRED_CONCERN_FIELDS,
        REQUIRED_CONCERN_ROW_IDS,
        {"CORE-03", "CORE-04", "CORE-05"},
    )
    concern_ids = require_unique(rows, "concern_id", CONCERN_MANIFEST)
    require_ids(concern_ids, REQUIRED_CONCERN_IDS, "concern IDs")
    require_text_coverage(
        rows,
        [
            "preserve-temporarily",
            "src/common/probe_analysis.cpp",
            "src/common/crash_dump/dump.cpp",
            "src/common/crash_dump/crash_dump_distribute.cpp",
            "src/common/random_hw.cpp",
            "src/connect/tls/hardware_rng.cpp",
            "src/mmu2/mmu2_reporting.cpp",
            "lib/TMCStepper/",
            "lib/AddTMCStepper.cmake",
        ],
        "concern disposition text",
    )


def check_manifests() -> None:
    check_printing_manifest()
    check_safety_manifest()
    check_feature_manifest()
    check_concern_manifest()


def check_rust_api_surface() -> None:
    lib_text = read_text(RUST_DOMAIN_LIB)
    if "#![forbid(unsafe_code)]" not in lib_text:
        raise VerificationError(
            f"{RUST_DOMAIN_LIB.as_posix()} must contain #![forbid(unsafe_code)]"
        )

    findings: list[str] = []
    for path in PHASE6_DOMAIN_RUST_FILES:
        text = read_text(path)
        required_strings = REQUIRED_RUST_API_STRINGS[path]
        missing = [needle for needle in required_strings if needle not in text]
        if missing:
            findings.append(
                f"{path.as_posix()} missing required Rust API strings: {', '.join(missing)}"
            )
        findings.extend(unsafe_findings_for_file(path, text))

    if findings:
        raise VerificationError("Phase 6 Rust API surface check failed:\n" + "\n".join(findings))


def check_bazel_surface() -> None:
    root_build = read_text("BUILD.bazel")
    tools_build = read_text("tools/bazel/BUILD.bazel")
    workflow = read_text("tools/bazel/rust_workflow.sh")

    for needle in ["phase6_verify", "phase6_verify_tests", "phase6_printing_safety_docs"]:
        if needle not in root_build:
            raise VerificationError(f"BUILD.bazel missing {needle}")

    for needle in [
        "phase6_verify",
        "phase6_verify_tests",
        "phase6_verify.py",
        "phase6_verify_test.py",
        "phase6_printing_core.json",
        "phase6_safety_gates.json",
        "phase6_feature_gates.json",
        "phase6_concern_dispositions.json",
        "//:phase6_printing_safety_docs",
    ]:
        if needle not in tools_build:
            raise VerificationError(f"tools/bazel/BUILD.bazel missing {needle}")

    for needle in [
        "phase6_verify)",
        "python3 tools/bazel/phase6_verify.py --all",
        "phase6_verify_tests)",
        "python3 tools/bazel/phase6_verify_test.py",
    ]:
        if needle not in workflow:
            raise VerificationError(f"tools/bazel/rust_workflow.sh missing {needle}")


def check_just_surface() -> None:
    justfile = read_text("justfile")
    for needle in [
        "phase6-verify:",
        "bazel run //tools/bazel:phase6_verify_tests",
        "bazel run //tools/bazel:phase6_verify",
    ]:
        if needle not in justfile:
            raise VerificationError(f"justfile missing {needle}")


def check_validation_contract() -> None:
    validation = read_text(VALIDATION_CONTRACT)
    required_strings = [
        "Quick run command",
        "python3 tools/bazel/phase6_verify.py --quick",
        "Full suite command",
        "just phase6-verify",
    ]
    missing = [needle for needle in required_strings if needle not in validation]
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation contract text: "
            + ", ".join(missing)
        )


def check_no_phase6_overclaim() -> None:
    phase_dir = ROOT / ".planning/phases/06-printing-core-safety-and-feature-gates"
    paths = [
        *PHASE6_ARTIFACTS,
        *[
            path.relative_to(ROOT).as_posix()
            for path in phase_dir.glob("06-*-SUMMARY.md")
        ],
    ]
    findings: list[str] = []

    for path in paths:
        full_path = ROOT / path
        if not full_path.exists():
            continue

        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in OVERCLAIM_STRINGS:
            if phrase in text:
                findings.append(f"{path}: {phrase}")

    if findings:
        raise VerificationError(
            "Phase 6 artifacts overclaim local evidence:\n" + "\n".join(findings)
        )


def check_no_overclaim() -> None:
    check_no_phase6_overclaim()


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


def check_quick() -> None:
    check_manifests()
    check_rust_api_surface()
    check_bazel_surface()
    check_just_surface()
    check_validation_contract()
    check_no_phase6_overclaim()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 6 printing, safety, and feature-gate manifests")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Run manifest, source-path, lifecycle, Bazel/just, and overclaim checks")
    mode.add_argument("--all", action="store_true", help="Run quick checks plus Cargo format, lint, build, and tests")
    mode.add_argument("--manifests-only", action="store_true", help="Run only Phase 6 manifest checks")
    mode.add_argument("--printing-only", action="store_true", help="Run only CORE-03 printing manifest checks")
    mode.add_argument("--safety-only", action="store_true", help="Run only CORE-04 safety manifest checks")
    mode.add_argument("--features-only", action="store_true", help="Run only CORE-05 feature-gate manifest checks")
    mode.add_argument("--concerns-only", action="store_true", help="Run only Phase 6 concern disposition checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if args.printing_only:
            check_printing_manifest()
            check_no_phase6_overclaim()
        elif args.safety_only:
            check_safety_manifest()
            check_no_phase6_overclaim()
        elif args.features_only:
            check_feature_manifest()
            check_no_phase6_overclaim()
        elif args.concerns_only:
            check_concern_manifest()
            check_no_phase6_overclaim()
        elif args.manifests_only:
            check_manifests()
            check_no_phase6_overclaim()
        else:
            check_quick()
            if args.all:
                check_rust_toolchain()

        print("Phase 6 printing core safety and feature gate verification passed")
        return 0
    except VerificationError as error:
        print(
            f"Phase 6 printing core safety and feature gate verification failed: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
