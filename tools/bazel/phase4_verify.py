#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Cargo.toml",
    "rust/crates/domain/Cargo.toml",
    "rust/crates/domain/src/lib.rs",
    "rust/crates/domain/src/product.rs",
    "rust/crates/domain/src/feature.rs",
    "rust/crates/domain/src/artifact.rs",
    "rust/crates/domain/src/storage.rs",
    "rust/crates/domain/src/protocol.rs",
    "rust/crates/application/Cargo.toml",
    "rust/crates/application/src/lib.rs",
    "rust/crates/board-adapter/Cargo.toml",
    "rust/crates/board-adapter/src/lib.rs",
    "rust/crates/runtime-adapter/Cargo.toml",
    "rust/crates/runtime-adapter/src/lib.rs",
    "tools/bazel/rust_workflow.sh",
]

PRODUCT_INVARIANT_STRINGS = [
    "pub struct ProductProfile",
    "UnsupportedHardwareCombination",
    "UnsupportedFeature",
]

STORAGE_INVARIANT_STRINGS = [
    "StorageSchemaVersion",
    "MigrationWindow",
]

ARTIFACT_INVARIANT_STRINGS = [
    "ArtifactFileName",
    "ArtifactSuffixMismatch",
]

PROTOCOL_INVARIANT_STRINGS = [
    "RegistrationCode",
    "Disconnected",
    "Registered",
    "Connected",
]

BOUNDARY_STRINGS = [
    "rust/crates/domain",
    "rust/crates/application",
    "rust/crates/board-adapter",
    "rust/crates/runtime-adapter",
]

BAZEL_LABEL_STRINGS = [
    "phase4_verify",
    "rust_format_check",
    "rust_lint",
    "rust_unit_tests",
    "rust_docs",
    "rust_build",
    "rust_firmware",
]

JUST_RECIPE_STRINGS = [
    "phase4-verify:",
    "rust-format:",
    "rust-lint:",
    "rust-test:",
    "rust-doc:",
    "rust-build:",
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


def run(command: list[str]) -> str:
    if not shutil.which(command[0]):
        raise AssertionError(f"required command not found: {command[0]}")

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


def check_static_surface() -> None:
    require_files(REQUIRED_FILES)
    require_strings("Cargo.toml", BOUNDARY_STRINGS)
    require_strings("rust/crates/domain/Cargo.toml", ["buddy-domain"])
    require_strings("rust/crates/application/Cargo.toml", ["buddy-application"])
    require_strings("rust/crates/board-adapter/Cargo.toml", ["buddy-board-adapter"])
    require_strings("rust/crates/runtime-adapter/Cargo.toml", ["buddy-runtime-adapter"])
    require_strings("rust/crates/domain/src/lib.rs", ["#![forbid(unsafe_code)]"])
    require_strings("rust/crates/application/src/lib.rs", ["#![forbid(unsafe_code)]"])
    require_strings("rust/crates/board-adapter/src/lib.rs", ["#![forbid(unsafe_code)]"])
    require_strings("rust/crates/runtime-adapter/src/lib.rs", ["#![forbid(unsafe_code)]"])
    require_strings("rust/crates/domain/src/product.rs", PRODUCT_INVARIANT_STRINGS)
    require_strings("rust/crates/domain/src/storage.rs", STORAGE_INVARIANT_STRINGS)
    require_strings("rust/crates/domain/src/artifact.rs", ARTIFACT_INVARIANT_STRINGS)
    require_strings("rust/crates/domain/src/protocol.rs", PROTOCOL_INVARIANT_STRINGS)
    require_strings("tools/bazel/BUILD.bazel", BAZEL_LABEL_STRINGS)
    require_strings("BUILD.bazel", ["rust_workspace_sources", "phase4_verify"])
    require_strings("justfile", JUST_RECIPE_STRINGS)


def check_rust_toolchain() -> None:
    run(["cargo", "fmt", "--all", "--", "--check"])
    run(["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"])
    run(["cargo", "build", "--workspace", "--all-features"])
    run(["cargo", "test", "--all-features"])
    run(["cargo", "doc", "--workspace", "--all-features", "--no-deps"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Phase 4 Rust architecture work")
    parser.add_argument("--quick", action="store_true", help="Run static Phase 4 checks only")
    parser.add_argument("--all", action="store_true", help="Run static and Rust toolchain checks")
    args = parser.parse_args()

    if not args.quick and not args.all:
        args.quick = True

    check_static_surface()
    if args.all:
        check_rust_toolchain()

    print("Phase 4 Rust architecture verification passed")


if __name__ == "__main__":
    main()
