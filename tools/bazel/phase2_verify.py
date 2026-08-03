#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RETIRED_REFERENCE_SWITCH = "BUDDY_BAZEL_EXECUTE_REFERENCE"

REQUIRED_FILES = [
    "MODULE.bazel",
    "MODULE.bazel.lock",
    ".bazelrc",
    ".gitignore",
    "BUILD.bazel",
    "platforms/BUILD.bazel",
    "tools/bazel/BUILD.bazel",
    "tools/bazel/shell_rules.bzl",
    "tools/bazel/reference_contract.sh",
    "tools/bazel/phase2_verify.sh",
    "tools/bazel/phase2_verify.py",
    "tools/bazel/toolchains/BUILD.bazel",
    "tools/bazel/toolchains/reference_toolchain.bzl",
    "justfile",
]

REQUIRED_STRINGS = {
    "MODULE.bazel": [
        "module(",
        "register_toolchains(",
        "//tools/bazel/toolchains:rust_firmware_toolchain",
        "//tools/bazel/toolchains:cc_firmware_toolchain",
        "//tools/bazel/toolchains:asm_firmware_toolchain",
        "//tools/bazel/toolchains:asset_generator_toolchain",
    ],
    ".bazelrc": [
        "build:host --platforms=//platforms:host_tools",
        "build:mini --platforms=//platforms:mini_buddy_stm32f407vg",
        "build:mk4 --platforms=//platforms:mk4_xbuddy_stm32f427zi",
        "build:coreone --platforms=//platforms:coreone_xbuddy_stm32f427zi",
        "build:xl --platforms=//platforms:xl_xlbuddy_stm32f427zi",
        "build:xbuddy_extension --platforms=//platforms:xbuddy_extension_stm32h503cbu7",
    ],
    ".gitignore": [
        "/bazel-*",
    ],
    "platforms/BUILD.bazel": [
        "constraint_setting(name = \"runtime\")",
        "constraint_setting(name = \"printer\")",
        "constraint_setting(name = \"board\")",
        "constraint_setting(name = \"mcu\")",
        "platform(",
        "mini_buddy_stm32f407vg",
        "xbuddy_extension_stm32h503cbu7",
    ],
    "tools/bazel/toolchains/BUILD.bazel": [
        "toolchain_type(name = \"rust_firmware_toolchain_type\")",
        "toolchain_type(name = \"cc_firmware_toolchain_type\")",
        "toolchain_type(name = \"asm_firmware_toolchain_type\")",
        "toolchain_type(name = \"asset_generator_toolchain_type\")",
        "rust_firmware_toolchain",
        "cc_firmware_toolchain",
        "asm_firmware_toolchain",
        "asset_generator_toolchain",
    ],
    "tools/bazel/BUILD.bazel": [
        "phase2_verify",
        "build_firmware",
        "test_firmware",
        "test_host",
        "simulator_parity",
        "release_package",
        "release_packages",
        "unavailable_capability",
        "reference_build",
        "reference_build_plan",
        "reference_test",
        "reference_test_plan",
        "reference_package",
        "reference_package_plan",
        "reference_simulator",
        "reference_simulator_plan",
        "//tools/bazel/toolchains:cc_firmware_info",
    ],
    "tools/bazel/reference_contract.sh": [
        "python3 utils/build.py",
        "reference_build)",
        "reference_build_plan)",
        "reference_test)",
        "reference_test_plan)",
        "reference_package)",
        "reference_package_plan)",
        "reference_simulator)",
        "reference_simulator_plan)",
        "pytest tests/integration --firmware <firmware.bin>",
    ],
    "justfile": [
        "phase2-verify:",
        "reference-build:",
        "reference-build-plan:",
        "reference-test:",
        "reference-test-plan:",
        "reference-package:",
        "reference-package-plan:",
        "reference-simulator:",
        "reference-simulator-plan:",
    ],
}

FORBIDDEN_STRINGS = {
    ".bazelrc": [RETIRED_REFERENCE_SWITCH],
    "tools/bazel/BUILD.bazel": [RETIRED_REFERENCE_SWITCH],
    "tools/bazel/reference_contract.sh": [RETIRED_REFERENCE_SWITCH],
}


def read(path: str) -> str:
    full_path = ROOT / path
    if not full_path.exists():
        raise AssertionError(f"missing required file: {path}")
    return full_path.read_text(encoding="utf-8")


def require_strings() -> None:
    for path, needles in REQUIRED_STRINGS.items():
        text = read(path)
        for needle in needles:
            if needle not in text:
                raise AssertionError(f"{path} missing required text: {needle}")


def reject_forbidden_strings() -> None:
    for path, needles in FORBIDDEN_STRINGS.items():
        text = read(path)
        for needle in needles:
            if needle in text:
                raise AssertionError(f"{path} retains forbidden text: {needle}")


def require_files() -> None:
    for path in REQUIRED_FILES:
        if not (ROOT / path).exists():
            raise AssertionError(f"missing required file: {path}")


def run_optional(command: list[str]) -> None:
    if not shutil.which(command[0]):
        print(f"Skipping optional check, {command[0]} not found: {' '.join(command)}")
        return

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


def main() -> int:
    try:
        require_files()
        require_strings()
        reject_forbidden_strings()
        run_optional([
            "bazel",
            "query",
            "//tools/bazel:phase2_verify + //tools/bazel:reference_build + //tools/bazel:reference_build_plan + //tools/bazel:reference_test + //tools/bazel:reference_test_plan + //tools/bazel:reference_package + //tools/bazel:reference_package_plan + //tools/bazel:reference_simulator + //tools/bazel:reference_simulator_plan + //platforms:host_tools + //tools/bazel/toolchains:rust_firmware_toolchain",
        ])
        run_optional(["just", "--list"])
    except AssertionError as error:
        print(f"Phase 2 verification failed: {error}", file=sys.stderr)
        return 1

    print("Phase 2 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
