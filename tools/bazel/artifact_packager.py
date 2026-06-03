#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PREFIX = "BUDDY_PHASE3_PACKAGE_SURFACE_FIXTURE"

PRINTER_TYPES = {
    "COREONE": 7,
    "MINI": 2,
    "MK4": 1,
    "MK3.5": 5,
    "XL": 3,
    "iX": 4,
    "XL_DEV_KIT": 3,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes(path: Path) -> bytes:
    if not path.exists():
        raise AssertionError(f"missing input file: {path}")
    return path.read_bytes()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def deterministic_payload(args: argparse.Namespace) -> bytes:
    payload = read_bytes(Path(args.payload))
    metadata = {
        "board": args.board,
        "bootloader_mode": args.bootloader_mode,
        "evidence_class": args.evidence_class,
        "mcu": args.mcu,
        "name": args.name,
        "printer": args.printer,
        "product": args.product,
        "signing_mode": args.signing_mode,
    }
    header = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return FIXTURE_PREFIX.encode("utf-8") + b"\n" + header + b"\n" + payload


def write_package_surface(args: argparse.Namespace, output_dir: Path) -> dict[str, Path]:
    payload = deterministic_payload(args)
    resource_seed = read_bytes(Path(args.resource_seed)) if args.resource_seed else b""
    resource = FIXTURE_PREFIX.encode("utf-8") + b"\nresource\n" + resource_seed
    paths = {
        "bin": output_dir / f"{args.name}.bin",
        "map": output_dir / f"{args.name}.map",
        "provenance": output_dir / f"{args.name}.provenance.json",
        "resource_img": output_dir / f"{args.name}.resource.img",
        "resource_pkg": output_dir / f"{args.name}.resource.pkg",
        "bbf": output_dir / f"{args.name}.bbf",
        "dfu": output_dir / f"{args.name}.dfu",
        "bbf_status": output_dir / f"{args.name}.bbf.status.json",
        "dfu_status": output_dir / f"{args.name}.dfu.status.json",
    }

    write_bytes(paths["bin"], payload)
    write_text(
        paths["map"],
        "\n".join([
            f"{FIXTURE_PREFIX}_MAP",
            f"name={args.name}",
            f"payload_sha256={sha256(payload)}",
            "",
        ]),
    )
    write_text(
        paths["provenance"],
        json.dumps(
            {
                "schema_version": 1,
                "name": args.name,
                "product": args.product,
                "printer": args.printer,
                "board": args.board,
                "mcu": args.mcu,
                "bootloader_mode": args.bootloader_mode,
                "evidence_class": args.evidence_class,
                "signing_mode": args.signing_mode,
                "payload_sha256": sha256(payload),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write_bytes(paths["resource_img"], resource)
    write_bytes(paths["resource_pkg"], resource + b"\npackage\n" + sha256(resource).encode("utf-8"))
    write_reference_format_status(args, paths)
    return paths


def has_pack_fw_prerequisites() -> bool:
    if not (ROOT / "utils/pack_fw.py").exists():
        return False
    if not shutil.which("python3"):
        return False
    result = subprocess.run(
        ["python3", "-c", "import ecdsa"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def run_pack_fw(args: argparse.Namespace, bin_path: Path, bbf_path: Path) -> bool:
    if not has_pack_fw_prerequisites():
        return False
    command = [
        "python3",
        "utils/pack_fw.py",
        str(bin_path),
        "--version",
        "6.0.0+1",
        "--no-sign",
        "--printer-type",
        str(PRINTER_TYPES.get(args.product, 2)),
        "--printer-version",
        "1",
        "--printer-subversion",
        "0",
    ]
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    produced = bin_path.with_suffix(".bbf")
    if result.returncode == 0 and produced.exists():
        if produced.resolve() != bbf_path.resolve():
            shutil.copyfile(produced, bbf_path)
        return True
    return False


def run_dfu(bin_path: Path, dfu_path: Path) -> bool:
    if not (ROOT / "utils/dfu.py").exists():
        return False
    command = [
        "python3",
        "utils/dfu.py",
        "create",
        f"0x08000000:{bin_path}",
        str(dfu_path),
    ]
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    return result.returncode == 0 and dfu_path.exists()


def write_reference_format_status(args: argparse.Namespace, paths: dict[str, Path]) -> None:
    if run_pack_fw(args, paths["bin"], paths["bbf"]):
        write_status_manifest(args, paths["bbf_status"], "bbf", "available", "reference-only", "utils/pack_fw.py --no-sign", "BBF structural check")
    else:
        write_text(
            paths["bbf"],
            "\n".join([
                "BOOTSTRAP_REQUIRED: BAZL-03 reference-format generation requires utils/pack_fw.py --no-sign prerequisites.",
                "evidence_class=bootstrap-required",
                "BBF structural check: bootstrap-required; no non-reference local BBF encoder was used.",
                "",
            ]),
        )
        write_status_manifest(args, paths["bbf_status"], "bbf", "bootstrap-required", "bootstrap-required", "utils/pack_fw.py --no-sign", "BBF structural check")

    if run_dfu(paths["bin"], paths["dfu"]):
        write_status_manifest(args, paths["dfu_status"], "dfu", "available", "reference-only", "utils/dfu.py", "DFU structural check")
    else:
        write_text(
            paths["dfu"],
            "\n".join([
                "BOOTSTRAP_REQUIRED: BAZL-03 reference-format generation requires utils/dfu.py prerequisites.",
                "evidence_class=ci-only",
                "DFU structural check: ci-only; no non-reference local DFU encoder was used.",
                "",
            ]),
        )
        write_status_manifest(args, paths["dfu_status"], "dfu", "ci-only", "ci-only", "utils/dfu.py", "DFU structural check")


def write_status_manifest(
        args: argparse.Namespace,
        path: Path,
        artifact_kind: str,
        status: str,
        evidence_class: str,
        reference_generator: str,
        structural_check: str) -> None:
    write_text(
        path,
        json.dumps(
            {
                "schema_version": 1,
                "name": args.name,
                "product": args.product,
                "printer": args.printer,
                "board": args.board,
                "mcu": args.mcu,
                "bootloader_mode": args.bootloader_mode,
                "artifact_kind": artifact_kind,
                "status": status,
                "evidence_class": evidence_class,
                "signing_mode": args.signing_mode,
                "reference_generator": reference_generator,
                "structural_check": structural_check,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def bbf_structural_check(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"BOOTSTRAP_REQUIRED"):
        return "BBF structural check: bootstrap-required"
    if len(data) < 512:
        raise AssertionError("BBF structural check failed: expected header/schema/TLV metadata surface")
    return "BBF structural check: passed"


def dfu_structural_check(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"BOOTSTRAP_REQUIRED"):
        return "DFU structural check: ci-only"
    if not data.startswith(b"DfuSe"):
        raise AssertionError("DFU structural check failed: missing DfuSe prefix")
    if len(data) < 16 or b"Target" not in data:
        raise AssertionError("DFU structural check failed: missing target/suffix/CRC surface")
    expected_crc = int.from_bytes(data[-4:], "little")
    actual_crc = 0xFFFFFFFF & -zlib.crc32(data[:-4]) - 1
    if data[-8:-5] != b"UFD" or data[-5] != 16 or expected_crc != actual_crc:
        raise AssertionError("DFU structural check failed: invalid suffix/CRC surface")
    return "DFU structural check: passed"


def write_mode(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    paths = write_package_surface(args, output_dir)
    print(bbf_structural_check(paths["bbf"]))
    print(dfu_structural_check(paths["dfu"]))


def self_test() -> None:
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        payload = Path(first) / "payload.txt"
        resource = Path(first) / "resource.txt"
        payload.write_text(f"{FIXTURE_PREFIX}\npayload\n", encoding="utf-8")
        resource.write_text(f"{FIXTURE_PREFIX}\nresource\n", encoding="utf-8")

        base_args = argparse.Namespace(
            output_dir=first,
            name="selftest",
            product="MINI",
            printer="MINI",
            board="BUDDY",
            mcu="STM32F407VG",
            bootloader_mode="boot",
            payload=str(payload),
            resource_seed=str(resource),
            evidence_class="local-smoke",
            signing_mode="unsigned-local",
        )
        first_paths = write_package_surface(base_args, Path(first))
        second_args = argparse.Namespace(**{**vars(base_args), "output_dir": second})
        second_paths = write_package_surface(second_args, Path(second))

        for key in ["bin", "map", "provenance", "resource_img", "resource_pkg"]:
            if first_paths[key].read_bytes() != second_paths[key].read_bytes():
                raise AssertionError(f"non-deterministic package surface output: {key}")
        print(bbf_structural_check(first_paths["bbf"]))
        print(dfu_structural_check(first_paths["dfu"]))

    print("artifact packager self-test passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create deterministic Phase 3 package-surface artifacts.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output-dir")
    parser.add_argument("--name")
    parser.add_argument("--product")
    parser.add_argument("--printer")
    parser.add_argument("--board")
    parser.add_argument("--mcu")
    parser.add_argument("--bootloader-mode")
    parser.add_argument("--payload")
    parser.add_argument("--resource-seed")
    parser.add_argument("--evidence-class", default="local-smoke")
    parser.add_argument("--signing-mode", default="unsigned-local")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        required = ["output_dir", "name", "product", "printer", "board", "mcu", "bootloader_mode", "payload"]
        missing = [name for name in required if not getattr(args, name)]
        if missing:
            raise AssertionError(f"missing required write-mode args: {', '.join(missing)}")
        write_mode(args)
    except AssertionError as error:
        print(f"artifact packager failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
