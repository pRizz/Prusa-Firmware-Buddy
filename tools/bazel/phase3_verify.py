#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

HELPER_FILES = [
    "tools/bazel/artifact_packager.py",
    "tools/bazel/artifact_manifest.py",
    "tools/bazel/artifact_metadata_compare.py",
    "tools/bazel/generated_drift.py",
]

ARTIFACT_FILES = [
    "tools/bazel/artifact_rules.bzl",
    "tools/bazel/phase3_verify.sh",
    "tools/bazel/phase3_artifacts.sh",
    "tools/bazel/manifests/representative_products.json",
]

DRIFT_FILES = [
    "tools/bazel/generator_rules.bzl",
    "tools/bazel/phase3_workflow.sh",
]

PRIVATE_MATERIAL_MARKERS = [
    "BEGIN PRIVATE KEY",
    "BEGIN EC PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "SIGNING_KEY=",
]

ARTIFACT_LABELS = [
    "mini_boot_artifacts",
    "mini_noboot_artifacts",
    "mk4_boot_artifacts",
    "mini_resource_package_artifacts",
    "representative_package_surface_smoke",
    "representative_reference_format_status",
    "representative_reference_format_artifacts",
    "release_package",
    "release_packages",
    "representative_release_artifacts",
    "artifact_manifest_smoke",
]

GENERATOR_SURFACES = [
    "product_profiles",
    "option_data",
    "resources",
    "translations",
    "fonts",
    "wui_assets",
    "esp_blobs",
    "puppy_descriptors",
    "mmu_descriptors",
    "package_metadata",
    "tracked_generated_outputs",
]

UPDATE_LABELS = [f"generated_{surface}_update" for surface in GENERATOR_SURFACES[:-1]] + [
    "tracked_generated_outputs_update",
]

CHECK_LABELS = [f"generated_{surface}_check" for surface in GENERATOR_SURFACES[:-1]] + [
    "tracked_generated_outputs_check",
]

REFERENCE_COMPARISON_STRINGS = [
    "tools/bazel/manifests/representative_products.json",
    ".planning/phases/01-reference-baseline-and-safety-envelope/01-REFERENCE-CAPTURE.md",
    ".planning/phases/01-reference-baseline-and-safety-envelope/01-BASELINE-MATRIX.md",
    "BUDDY_BAZEL_EXECUTE_REFERENCE=1",
]

ARTIFACT_SUFFIXES = [
    ".bin",
    ".map",
    ".provenance.json",
    ".bbf",
    ".bbf.status.json",
    ".dfu",
    ".dfu.status.json",
    ".resource.img",
    ".resource.pkg",
    ".manifest.json",
]

ARTIFACT_WIRING_STRINGS = [
    "artifact_packager.py",
    "artifact_manifest.py",
    "utils/pack_fw.py",
    "--no-sign",
    "utils/dfu.py",
    "BOOTSTRAP_REQUIRED",
    "bootstrap-required",
    "ci-only",
    "BBF structural check",
    "DFU structural check",
]

FACADE_RECIPES = [
    "phase3-verify:",
    "generated-check:",
    "generated-update:",
    "release-package:",
]


def read(path: str) -> str:
    full_path = ROOT / path
    if not full_path.exists():
        raise AssertionError(f"missing required file: {path}")
    return full_path.read_text(encoding="utf-8")


def require_files(paths: list[str]) -> None:
    for path in paths:
        if not (ROOT / path).exists():
            raise AssertionError(f"missing required file: {path}")


def require_strings(path: str, needles: list[str]) -> None:
    text = read(path)
    for needle in needles:
        if needle not in text:
            raise AssertionError(f"{path} missing required text: {needle}")


def require_any_string(path: str, needles: list[str]) -> None:
    text = read(path)
    if not any(needle in text for needle in needles):
        raise AssertionError(f"{path} missing one of: {', '.join(needles)}")


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"command failed: {' '.join(command)}\n{result.stdout}")
    return result.stdout


def run_optional(command: list[str]) -> None:
    if not shutil.which(command[0]):
        print(f"Skipping optional check, {command[0]} not found: {' '.join(command)}")
        return
    run(command)


def helper_self_test(path: str, expected_line: str) -> None:
    output = run(["python3", path, "--self-test"])
    if expected_line not in output:
        raise AssertionError(f"{path} did not print expected self-test line: {expected_line}")


def scan_private_material() -> None:
    for directory in ["tools/bazel/fixtures", "tools/bazel/manifests"]:
        root = ROOT / directory
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in PRIVATE_MATERIAL_MARKERS:
                if marker in text:
                    raise AssertionError(f"{path.relative_to(ROOT)} contains private material marker: {marker}")


def quick() -> None:
    compileall = ["python3", "-m", "py_compile", "tools/bazel/phase3_verify.py"]
    existing_helpers = [path for path in HELPER_FILES if (ROOT / path).exists()]
    run(compileall + existing_helpers)
    scan_private_material()

    missing_helpers = [path for path in HELPER_FILES if not (ROOT / path).exists()]
    if missing_helpers:
        print(f"Wave 0 pending helpers: {', '.join(missing_helpers)}")
    else:
        helper_self_test("tools/bazel/artifact_packager.py", "artifact packager self-test passed")
        helper_self_test("tools/bazel/artifact_manifest.py", "artifact manifest self-test passed")
        helper_self_test("tools/bazel/artifact_metadata_compare.py", "artifact metadata compare self-test passed")
        helper_self_test("tools/bazel/generated_drift.py", "generated drift self-test passed")

    print("Phase 3 quick verification passed")


def require_artifacts() -> None:
    require_files(ARTIFACT_FILES)
    require_strings("tools/bazel/artifact_rules.bzl", ["phase3_release_artifacts"] + ARTIFACT_WIRING_STRINGS)
    require_strings("tools/bazel/phase3_artifacts.sh", ["representative_release_artifacts", "phase3_verify.py"])
    require_strings("tools/bazel/BUILD.bazel", ARTIFACT_LABELS)
    for suffix in ARTIFACT_SUFFIXES:
        require_any_string("tools/bazel/artifact_rules.bzl", [suffix])
        require_any_string("tools/bazel/BUILD.bazel", [suffix, "representative_release_artifacts"])

    rules_text = read("tools/bazel/artifact_rules.bzl").lower()
    forbidden = [
        "local bbf encoder",
        "local dfu encoder",
        "non-reference bbf",
        "non-reference dfu",
    ]
    for needle in forbidden:
        if needle in rules_text and "must not satisfy" not in rules_text:
            raise AssertionError(f"artifact rules contain unsafe reference-format wording: {needle}")


def require_manifests() -> None:
    require_files([
        "tools/bazel/artifact_manifest.py",
        "tools/bazel/artifact_metadata_compare.py",
        "tools/bazel/manifests/representative_products.json",
    ])
    require_strings(
        "tools/bazel/artifact_manifest.py",
        [
            "schema_version",
            "bootloader_mode",
            "artifact_kind",
            "package_members",
            "version_provenance",
            "resource_presence",
            "signing_mode",
            "unsigned-local",
            "external-release-key",
            "sha256",
            "resolve",
            "..",
        ],
    )
    require_strings(
        "tools/bazel/manifests/representative_products.json",
        [
            "mini_boot",
            "mini_noboot",
            "mk4_boot",
            "resource-package",
            "auxiliary-manifest-only",
            "unsigned-local",
            "reference-only",
            ".bbf.status.json",
            ".dfu.status.json",
        ],
    )
    require_strings(
        "tools/bazel/artifact_metadata_compare.py",
        ["product", "printer", "board", "mcu", "bootloader_mode", "artifact_kind", "evidence_class", "signing_mode", "sha256"],
    )


def require_reference_status() -> None:
    require_files(["tools/bazel/artifact_packager.py", "tools/bazel/artifact_rules.bzl"])
    require_strings("tools/bazel/artifact_packager.py", [".bbf.status.json", ".dfu.status.json", "bootstrap-required", "ci-only"])
    require_strings("tools/bazel/artifact_rules.bzl", [".bbf.status.json", ".dfu.status.json"])
    require_strings("tools/bazel/BUILD.bazel", ["representative_reference_format_status", "representative_package_surface_smoke"])


def require_reference_artifacts() -> None:
    require_files(["tools/bazel/artifact_packager.py", "tools/bazel/artifact_rules.bzl"])
    require_strings("tools/bazel/artifact_packager.py", ["utils/pack_fw.py", "--no-sign", "utils/dfu.py", "reference_generator"])
    require_strings("tools/bazel/BUILD.bazel", ["representative_reference_format_artifacts"])


def require_drift_checks() -> None:
    require_files(["tools/bazel/generated_drift.py"] + DRIFT_FILES)
    require_strings("tools/bazel/generated_drift.py", ["DRIFT:", "--update", "--output-dir"] + GENERATOR_SURFACES)
    require_strings("tools/bazel/generator_rules.bzl", ["phase3_generated_surface", "phase3_generated_check", "phase3_generated_update"] + GENERATOR_SURFACES)
    require_strings("tools/bazel/phase3_workflow.sh", ["generated_check", "generated_update"] + CHECK_LABELS + UPDATE_LABELS)
    require_strings("tools/bazel/BUILD.bazel", ["generated_check", "generated_update"] + CHECK_LABELS)


def require_update_targets() -> None:
    require_files(DRIFT_FILES)
    require_strings("tools/bazel/BUILD.bazel", UPDATE_LABELS)
    require_strings("tools/bazel/phase3_workflow.sh", ["--update"] + UPDATE_LABELS)
    require_strings("tools/bazel/phase3_workflow.sh", REFERENCE_COMPARISON_STRINGS)


def require_facade() -> None:
    require_strings("justfile", FACADE_RECIPES)
    require_strings(
        "justfile",
        [
            "bazel run //tools/bazel:phase3_verify",
            "bazel run //tools/bazel:generated_check",
            "bazel run //tools/bazel:generated_update",
            "bazel build //tools/bazel:representative_release_artifacts",
        ],
    )
    require_strings("tools/bazel/BUILD.bazel", ["phase3_verify", "release_package", "release_packages", "reference_release_compare"])
    require_strings("tools/bazel/phase3_workflow.sh", REFERENCE_COMPARISON_STRINGS)


def require_all() -> None:
    require_files(HELPER_FILES + ARTIFACT_FILES + DRIFT_FILES)
    quick()
    require_artifacts()
    require_reference_status()
    require_reference_artifacts()
    require_manifests()
    require_drift_checks()
    require_update_targets()
    require_facade()
    run_optional(["just", "--list"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify Phase 3 artifact and generator parity surfaces.")
    parser.add_argument("--quick", action="store_true", help="Run helper-safe smoke checks.")
    parser.add_argument("--require-artifacts", action="store_true", help="Require representative artifact wiring.")
    parser.add_argument("--require-reference-status", action="store_true", help="Require reference-format status manifests.")
    parser.add_argument("--require-reference-artifacts", action="store_true", help="Require guarded reference-format artifact target.")
    parser.add_argument("--require-manifests", action="store_true", help="Require normalized manifest wiring.")
    parser.add_argument("--require-drift-checks", action="store_true", help="Require generated drift check surfaces.")
    parser.add_argument("--require-update-targets", action="store_true", help="Require generated update surfaces.")
    parser.add_argument("--require-facade", action="store_true", help="Require just/Bazel facade labels.")
    parser.add_argument("--all", action="store_true", help="Run every Phase 3 verification.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not any(vars(args).values()):
        args.all = True

    try:
        if args.quick:
            quick()
        if args.require_artifacts:
            require_artifacts()
        if args.require_reference_status:
            require_reference_status()
        if args.require_reference_artifacts:
            require_reference_artifacts()
        if args.require_manifests:
            require_manifests()
        if args.require_drift_checks:
            require_drift_checks()
        if args.require_update_targets:
            require_update_targets()
        if args.require_facade:
            require_facade()
        if args.all:
            require_all()
    except AssertionError as error:
        print(f"Phase 3 verification failed: {error}", file=sys.stderr)
        return 1

    if args.all:
        print("Phase 3 full verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
