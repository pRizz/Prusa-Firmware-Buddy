#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from phase8_contract_policy import *  # noqa: F403


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


def check_rust_api_surface() -> None:
    lib_text = read_text(RUST_DOMAIN_LIB)
    gui_text = read_text(GUI_RUST)
    errors: list[str] = []

    if "#![forbid(unsafe_code)]" not in lib_text:
        errors.append(
            f"{RUST_DOMAIN_LIB.as_posix()} must contain #![forbid(unsafe_code)]"
        )

    missing_gui = [
        needle for needle in RUST_API_STRINGS if needle not in gui_text
    ]
    if missing_gui:
        errors.append(
            f"{GUI_RUST.as_posix()} missing required Rust API strings: {', '.join(missing_gui)}"
        )

    missing_lib = [
        needle for needle in RUST_API_STRINGS if needle not in lib_text
    ]
    if missing_lib:
        errors.append(
            f"{RUST_DOMAIN_LIB.as_posix()} missing required GUI exports: {', '.join(missing_lib)}"
        )

    unsafe_findings = unsafe_findings_for_file(GUI_RUST, gui_text)
    if unsafe_findings:
        errors.append("Phase 8 GUI Rust module unsafe check failed:\n" +
                      "\n".join(unsafe_findings))

    if errors:
        raise VerificationError("\n".join(errors))


def require_text_contains(path_label: str, text: str,
                          needles: list[str]) -> list[str]:
    return [
        f"{path_label} missing {needle}" for needle in needles
        if needle not in text
    ]


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
                "phase8_contract_policy.py",
                "phase8_verify_test.py",
                "phase8_verify_failure_test.py",
                "phase8_gui_workflows.json",
                "phase8_display_layouts.json",
                "phase8_concern_dispositions.json",
                "//:phase8_local_interface_docs",
                "//:rust_workspace_sources",
            ],
        ))
    errors.extend(
        require_text_contains(
            "BUILD.bazel",
            root_build,
            [
                "phase8_local_interface_docs",
                "phase8_verify",
                "phase8_verify_tests",
            ],
        ))
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
        ))

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
    tests_index = find_exact_line(
        justfile, "bazel run //tools/bazel:phase8_verify_tests")
    verify_index = find_exact_line(justfile,
                                   "bazel run //tools/bazel:phase8_verify")
    if tests_index is None or verify_index is None or tests_index > verify_index:
        errors.append(
            "justfile must run phase8_verify_tests before phase8_verify")
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
    missing = [
        needle for needle in required_strings if needle not in validation
    ]
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation contract text: "
            + ", ".join(missing))


def check_secret_markers() -> None:
    findings: list[str] = []
    for path in PHASE8_ARTIFACTS_FOR_MARKER_SCAN:
        text = read_text(path)
        markers = [marker for marker in SECRET_MARKERS if marker in text]
        if markers:
            findings.append(
                f"{path.as_posix()} contains forbidden secret or crash dump byte marker(s): "
                + ", ".join(markers))
    if findings:
        raise VerificationError("\n".join(findings))


def check_no_phase8_overclaim() -> None:
    phase_dir = ROOT / ".planning/phases/08-local-interface-and-workflow-parity"
    paths = [
        GUI_WORKFLOWS_MANIFEST,
        DISPLAY_LAYOUTS_MANIFEST,
        CONCERN_DISPOSITIONS_MANIFEST,
        VALIDATION_CONTRACT,
        *[
            path.relative_to(ROOT)
            for path in phase_dir.glob("08-*-SUMMARY.md")
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
            "Phase 8 artifacts overclaim local evidence:\n" +
            "\n".join(findings))


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
    collect([
        check_gui_workflows_manifest,
        check_display_layout_manifest,
        check_concern_dispositions,
        check_rust_api_surface,
        check_validation_contract,
        check_bazel_surface,
        check_just_surface,
        check_secret_markers,
        check_no_phase8_overclaim,
    ])


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
        "Verify Phase 8 local interface and workflow parity surfaces")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--quick",
        action="store_true",
        help=
        "Run static Phase 8 manifest, Rust API, facade, validation, secret, and overclaim checks"
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Run quick checks plus Cargo format, lint, build, and tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        check_quick()
        if args.all:
            check_rust_toolchain()

        print(
            "Phase 8 local interface and workflow parity verification passed")
        return 0
    except VerificationError as error:
        print(
            f"Phase 8 local interface and workflow parity verification failed: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
