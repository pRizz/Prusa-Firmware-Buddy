#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


PRODUCTS = ["COREONE", "MINI", "MK4", "MK3.5", "XL", "iX", "XL_DEV_KIT"]
BOARDS = ["BUDDY", "XBUDDY", "XLBUDDY", "DWARF", "MODULARBED", "XL_DEV_KIT_XLB", "XBUDDY_EXTENSION"]
MCUS = ["STM32F407VG", "STM32F429VI", "STM32F427ZI", "STM32G070RBT6", "STM32H503CBU7"]
BOOTLOADER_MODES = ["boot", "noboot", "auxiliary"]
ARTIFACT_KINDS = ["bin", "map", "bbf", "dfu", "resource-image", "resource-package", "provenance", "auxiliary-manifest"]
EVIDENCE_CLASSES = ["local-smoke", "bootstrap-required", "ci-only", "reference-only", "manual-hardware-required", "release-candidate"]
SIGNING_MODES = ["unsigned-local", "test-key", "external-release-key", "not-applicable"]


def validate_enum(value: str, allowed: list[str], field: str) -> None:
    if value not in allowed:
        raise AssertionError(f"invalid {field}: {value}")


def resolve_input(raw_path: str) -> Path:
    path = Path(raw_path)
    if ".." in path.parts:
        raise AssertionError(f"path traversal rejected: {raw_path}")
    resolved = path.resolve()
    if not resolved.exists():
        raise AssertionError(f"missing input file: {raw_path}")
    return resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(args: argparse.Namespace) -> None:
    validate_enum(args.product, PRODUCTS, "product")
    validate_enum(args.board, BOARDS, "board")
    validate_enum(args.mcu, MCUS, "mcu")
    validate_enum(args.bootloader_mode, BOOTLOADER_MODES, "bootloader_mode")
    validate_enum(args.artifact_kind, ARTIFACT_KINDS, "artifact_kind")
    validate_enum(args.evidence_class, EVIDENCE_CLASSES, "evidence_class")
    validate_enum(args.signing_mode, SIGNING_MODES, "signing_mode")

    artifact = resolve_input(args.artifact)
    resource_paths = [resolve_input(path) for path in args.resource]
    package_members = [str(resolve_input(path).name) for path in args.package_member]
    provenance_paths = [resolve_input(path) for path in args.provenance]
    data = {
        "schema_version": 1,
        "product": args.product,
        "printer": args.printer,
        "board": args.board,
        "mcu": args.mcu,
        "bootloader_mode": args.bootloader_mode,
        "artifact_kind": args.artifact_kind,
        "filename": artifact.name,
        "size": artifact.stat().st_size,
        "sha256": sha256_file(artifact),
        "package_members": sorted(package_members),
        "version_provenance": [path.name for path in provenance_paths],
        "resource_presence": {
            "has_resource": bool(resource_paths),
            "resources": [path.name for path in resource_paths],
        },
        "evidence_class": args.evidence_class,
        "signing_mode": args.signing_mode,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        artifact = root / "selftest.bin"
        resource = root / "selftest.resource.pkg"
        provenance = root / "selftest.provenance.json"
        output = root / "selftest.manifest.json"
        artifact.write_bytes(b"BUDDY_PHASE3_PACKAGE_SURFACE_FIXTURE\nartifact\n")
        resource.write_bytes(b"BUDDY_PHASE3_PACKAGE_SURFACE_FIXTURE\nresource\n")
        provenance.write_text('{"schema_version": 1}\n', encoding="utf-8")
        args = argparse.Namespace(
            output=str(output),
            product="MINI",
            printer="MINI",
            board="BUDDY",
            mcu="STM32F407VG",
            bootloader_mode="boot",
            artifact_kind="bin",
            artifact=str(artifact),
            resource=[str(resource)],
            package_member=[str(artifact), str(resource)],
            provenance=[str(provenance)],
            evidence_class="local-smoke",
            signing_mode="unsigned-local",
        )
        write_manifest(args)
        data = json.loads(output.read_text(encoding="utf-8"))
        expected_keys = {
            "schema_version",
            "product",
            "printer",
            "board",
            "mcu",
            "bootloader_mode",
            "artifact_kind",
            "filename",
            "size",
            "sha256",
            "package_members",
            "version_provenance",
            "resource_presence",
            "evidence_class",
            "signing_mode",
        }
        if set(data) != expected_keys:
            raise AssertionError(f"manifest keys mismatch: {sorted(data)}")
        if data["sha256"] != sha256_file(artifact):
            raise AssertionError("manifest did not derive sha256 from artifact file")

    print("artifact manifest self-test passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write normalized Phase 3 artifact manifests.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--product")
    parser.add_argument("--printer")
    parser.add_argument("--board")
    parser.add_argument("--mcu")
    parser.add_argument("--bootloader-mode")
    parser.add_argument("--artifact-kind")
    parser.add_argument("--artifact")
    parser.add_argument("--resource", action="append", default=[])
    parser.add_argument("--package-member", action="append", default=[])
    parser.add_argument("--provenance", action="append", default=[])
    parser.add_argument("--evidence-class")
    parser.add_argument("--signing-mode")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        required = [
            "output",
            "product",
            "printer",
            "board",
            "mcu",
            "bootloader_mode",
            "artifact_kind",
            "artifact",
            "evidence_class",
            "signing_mode",
        ]
        missing = [name for name in required if not getattr(args, name)]
        if missing:
            raise AssertionError(f"missing required write-mode args: {', '.join(missing)}")
        write_manifest(args)
    except AssertionError as error:
        print(f"artifact manifest failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
