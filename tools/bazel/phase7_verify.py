#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from phase7_contract_policy import *  # noqa: F403


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

    hash_count = marker_index - start - (2 if text.startswith("br", start) else
                                         1)
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
                findings.append(
                    f"{relative_path.as_posix()}:{line_number}: {label}")
    return findings


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
            raise VerificationError(
                f"{row_name} check_label must end in _check: {check_label}")
        if not update_label.endswith("_update"):
            raise VerificationError(
                f"{row_name} update_label must end in _update: {update_label}")
        check_labels.add(check_label)
        update_labels.add(update_label)
    missing_row_ids = sorted(set(GENERATED_ROW_IDS) - row_ids)
    missing_check_labels = sorted(set(REQUIRED_CHECK_LABELS) - check_labels)
    missing_update_labels = sorted(set(REQUIRED_UPDATE_LABELS) - update_labels)
    if missing_row_ids or missing_check_labels or missing_update_labels:
        raise VerificationError(
            "missing required generated-output coverage: " + ", ".join([
                *missing_row_ids, *missing_check_labels, *missing_update_labels
            ]))


def check_concern_manifest() -> None:
    rows, _ = validate_rows(CONCERN_MANIFEST, "concerns", CONCERN_FIELDS,
                            CONCERN_ROW_IDS, {"IFCE-04", "IFCE-05"})
    concern_ids = require_unique(rows, "concern_id", CONCERN_MANIFEST)
    require_ids(concern_ids, CONCERN_IDS, "D-11 concern IDs")
    for row in rows:
        intentional_delta = row.get("intentional_delta")
        if intentional_delta == "none" and row.get(
                "disposition") != "preserve-with-explicit-risk":
            raise VerificationError(
                f"{CONCERN_MANIFEST.as_posix()} row {row.get('id')} must use preserve-with-explicit-risk unless intentional_delta is not none"
            )


def check_rust_api_surface() -> None:
    lib_text = read_text(RUST_DOMAIN_LIB)
    if "#![forbid(unsafe_code)]" not in lib_text:
        raise VerificationError(
            f"{RUST_DOMAIN_LIB.as_posix()} must contain #![forbid(unsafe_code)]"
        )

    findings: list[str] = []
    for path, required_strings in [(STORAGE_RUST, STORAGE_API_STRINGS),
                                   (RESOURCE_RUST, RESOURCE_API_STRINGS)]:
        text = read_text(path)
        missing = [needle for needle in required_strings if needle not in text]
        if missing:
            findings.append(
                f"{path.as_posix()} missing required Rust API strings: {', '.join(missing)}"
            )
        findings.extend(unsafe_findings_for_file(path, text))

    if findings:
        raise VerificationError("Phase 7 Rust API surface check failed:\n" +
                                "\n".join(findings))


def check_bazel_surface() -> None:
    tools_build = read_text("tools/bazel/BUILD.bazel")
    if "phase7_verify" in tools_build:
        for needle in [
                "phase7_verify", "phase7_verify_tests", "phase7_verify.py",
                "phase7_verify_test.py"
        ]:
            if needle not in tools_build:
                raise VerificationError(
                    f"tools/bazel/BUILD.bazel missing {needle}")
        return

    for label in REQUIRED_CHECK_LABELS:
        target = label.split(":", 1)[1]
        if target not in tools_build:
            raise VerificationError(
                f"tools/bazel/BUILD.bazel missing generated label {target}")


def check_just_surface() -> None:
    justfile = read_text("justfile")
    if "phase7-verify:" in justfile:
        for needle in [
                "phase7-verify:", "phase7_verify_tests", "phase7_verify"
        ]:
            if needle not in justfile:
                raise VerificationError(f"justfile missing {needle}")
        return
    for needle in ["generated-check:", "rust-test:", "phase6-verify:"]:
        if needle not in justfile:
            raise VerificationError(
                f"justfile missing expected verification facade {needle}")


def check_validation_contract() -> None:
    validation = read_text(VALIDATION_CONTRACT)
    required_strings = [
        "Quick run command",
        "python3 tools/bazel/phase7_verify.py --quick",
        "Full suite command",
        "just phase7-verify",
    ]
    missing = [
        needle for needle in required_strings if needle not in validation
    ]
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation contract text: "
            + ", ".join(missing))


def check_no_phase7_overclaim() -> None:
    phase_dir = ROOT / ".planning/phases/07-persistence-storage-and-resource-compatibility"
    paths = [
        CONFIG_MANIFEST,
        STORAGE_MANIFEST,
        RESOURCES_MANIFEST,
        GENERATED_MANIFEST,
        CONCERN_MANIFEST,
        MIGRATION_CATALOG,
        *[
            path.relative_to(ROOT)
            for path in phase_dir.glob("07-*-SUMMARY.md")
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
                findings.append(f"{path.as_posix()}: {phrase}")
    if findings:
        raise VerificationError(
            "Phase 7 artifacts overclaim local evidence:\n" +
            "\n".join(findings))


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
        raise VerificationError(
            f"command failed: {' '.join(command)}\n{result.stdout}")


def check_rust_toolchain() -> None:
    run(["cargo", "fmt", "--all", "--", "--check"])
    run([
        "cargo", "clippy", "--all-targets", "--all-features", "--", "-D",
        "warnings"
    ])
    run(["cargo", "build", "--all-targets", "--all-features"])
    run(["cargo", "test", "--all-features"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Verify Phase 7 persistence storage and resource compatibility surfaces"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--quick",
        action="store_true",
        help=
        "Run static Phase 7 manifest, source, Rust API, facade, and overclaim checks"
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Run quick checks plus Cargo format, lint, build, and tests")
    mode.add_argument(
        "--manifests-only",
        action="store_true",
        help="Run only Phase 7 manifest and redacted catalog checks")
    mode.add_argument("--config-only",
                      action="store_true",
                      help="Run only config-store manifest checks")
    mode.add_argument(
        "--storage-only",
        action="store_true",
        help="Run only storage media and migration catalog checks")
    mode.add_argument("--resources-only",
                      action="store_true",
                      help="Run only resource manifest checks")
    mode.add_argument("--generated-only",
                      action="store_true",
                      help="Run only generated-output manifest checks")
    mode.add_argument("--concerns-only",
                      action="store_true",
                      help="Run only concern disposition checks")
    mode.add_argument("--rust-only",
                      action="store_true",
                      help="Run only Rust storage/resource API checks")
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

        print(
            "Phase 7 persistence storage and resource compatibility verification passed"
        )
        return 0
    except VerificationError as error:
        print(
            f"Phase 7 persistence storage and resource compatibility verification failed: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
