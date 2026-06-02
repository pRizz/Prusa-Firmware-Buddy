#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

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
        "bootstrap",
        "build_firmware",
        "rust_firmware",
        "retained_foreign_code",
        "generated_assets",
        "host_tools",
        "test_host",
        "unit_tests",
        "simulator_inputs",
        "format",
        "lint",
        "generated_check",
        "simulator_parity",
        "release_package",
        "release_packages",
    ],
    "tools/bazel/reference_contract.sh": [
        "BUDDY_BAZEL_EXECUTE_REFERENCE",
        "python3 utils/build.py",
        "python3 utils/build.py --generate-cmake-presets",
        "rust_firmware",
        "retained_foreign_code",
        "generated_assets",
        "host_tools",
        "unit_tests",
        "simulator_inputs",
        "release_packages",
        "pytest tests/integration --firmware <firmware.bin>",
    ],
    "justfile": [
        "bootstrap:",
        "build:",
        "test:",
        "format:",
        "lint:",
        "generated-check:",
        "simulator-parity:",
        "release-package:",
        "phase2-verify:",
    ],
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
        run_optional([
            "bazel",
            "query",
            "//tools/bazel:phase2_verify + //platforms:host_tools + //tools/bazel/toolchains:rust_firmware_toolchain",
        ])
        run_optional(["just", "--list"])
    except AssertionError as error:
        print(f"Phase 2 verification failed: {error}", file=sys.stderr)
        return 1

    print("Phase 2 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
