#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from phase6_contract_policy import *  # noqa: F403


def check_printing_manifest() -> None:
    _, source_paths = validate_manifest(
        PRINTING_MANIFEST,
        "printing_contracts",
        REQUIRED_PRINTING_FIELDS,
        REQUIRED_PRINTING_ROW_IDS,
        "CORE-03",
    )
    require_source_coverage(source_paths, REQUIRED_PRINTING_SOURCE_PATHS,
                            "printing")


def check_safety_manifest() -> None:
    rows, source_paths = validate_manifest(
        SAFETY_MANIFEST,
        "safety_gates",
        REQUIRED_SAFETY_FIELDS,
        REQUIRED_SAFETY_ROW_IDS,
        "CORE-04",
    )
    require_source_coverage(source_paths, REQUIRED_SAFETY_SOURCE_PATHS,
                            "safety")
    require_text_coverage(rows, ["manual-hardware-required", "source-audit"],
                          "safety evidence classes")


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
    require_text_coverage(rows, REQUIRED_FEATURE_GATE_STRINGS,
                          "feature gate strings")


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
        raise VerificationError("Phase 6 Rust API surface check failed:\n" +
                                "\n".join(findings))


def check_bazel_surface() -> None:
    root_build = read_text("BUILD.bazel")
    tools_build = read_text("tools/bazel/BUILD.bazel")
    workflow = read_text("tools/bazel/rust_workflow.sh")

    for needle in [
            "phase6_verify", "phase6_verify_tests",
            "phase6_printing_safety_docs"
    ]:
        if needle not in root_build:
            raise VerificationError(f"BUILD.bazel missing {needle}")

    for needle in [
            "phase6_verify",
            "phase6_verify_tests",
            "phase6_verify.py",
            "phase6_contract_policy.py",
            "phase6_verify_test.py",
            "phase6_printing_core.json",
            "phase6_safety_gates.json",
            "phase6_feature_gates.json",
            "phase6_concern_dispositions.json",
            "//:phase6_printing_safety_docs",
    ]:
        if needle not in tools_build:
            raise VerificationError(
                f"tools/bazel/BUILD.bazel missing {needle}")

    for needle in [
            "phase6_verify)",
            "python3 tools/bazel/phase6_verify.py --all",
            "phase6_verify_tests)",
            "python3 tools/bazel/phase6_verify_test.py",
    ]:
        if needle not in workflow:
            raise VerificationError(
                f"tools/bazel/rust_workflow.sh missing {needle}")


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
    missing = [
        needle for needle in required_strings if needle not in validation
    ]
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation contract text: "
            + ", ".join(missing))


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
            "Phase 6 artifacts overclaim local evidence:\n" +
            "\n".join(findings))


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


def check_quick() -> None:
    check_manifests()
    check_rust_api_surface()
    check_bazel_surface()
    check_just_surface()
    check_validation_contract()
    check_no_phase6_overclaim()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Verify Phase 6 printing, safety, and feature-gate manifests")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--quick",
        action="store_true",
        help=
        "Run manifest, source-path, lifecycle, Bazel/just, and overclaim checks"
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Run quick checks plus Cargo format, lint, build, and tests")
    mode.add_argument("--manifests-only",
                      action="store_true",
                      help="Run only Phase 6 manifest checks")
    mode.add_argument("--printing-only",
                      action="store_true",
                      help="Run only CORE-03 printing manifest checks")
    mode.add_argument("--safety-only",
                      action="store_true",
                      help="Run only CORE-04 safety manifest checks")
    mode.add_argument("--features-only",
                      action="store_true",
                      help="Run only CORE-05 feature-gate manifest checks")
    mode.add_argument("--concerns-only",
                      action="store_true",
                      help="Run only Phase 6 concern disposition checks")
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

        print(
            "Phase 6 printing core safety and feature gate verification passed"
        )
        return 0
    except VerificationError as error:
        print(
            f"Phase 6 printing core safety and feature gate verification failed: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
