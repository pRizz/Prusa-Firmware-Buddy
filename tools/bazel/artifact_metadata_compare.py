#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


REQUIRED_ENTRY_FIELDS = [
    "product",
    "printer",
    "board",
    "mcu",
    "bootloader_mode",
    "artifact_outputs",
    "evidence_class",
    "signing_mode",
]

REQUIRED_MANIFEST_FIELDS = [
    "product",
    "printer",
    "board",
    "mcu",
    "bootloader_mode",
    "artifact_kind",
    "filename",
    "package_members",
    "version_provenance",
    "resource_presence",
    "evidence_class",
    "signing_mode",
    "sha256",
]

REFERENCE_STATUSES = ["available", "bootstrap-required", "ci-only"]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def require_text(path: Path, needle: str) -> None:
    if needle not in path.read_text(encoding="utf-8", errors="ignore"):
        raise AssertionError(f"{path} missing reference text: {needle}")


def compare_representative_matrix(path: Path) -> None:
    data = load_json(path)
    entries = data.get("entries", []) if isinstance(data, dict) else []
    if not entries:
        raise AssertionError("representative matrix has no entries")
    for entry in entries:
        for field in REQUIRED_ENTRY_FIELDS:
            if field not in entry:
                raise AssertionError(f"representative entry {entry.get('id', '<unknown>')} missing {field}")


def compare_manifest(path: Path) -> None:
    data = load_json(path)
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in data:
            raise AssertionError(f"{path} missing manifest field {field}")


def compare_status(path: Path) -> None:
    data = load_json(path)
    status = data.get("status")
    if status not in REFERENCE_STATUSES:
        raise AssertionError(f"{path} has invalid reference status: {status}")
    for field in ["artifact_kind", "evidence_class", "reference_generator", "structural_check", "signing_mode"]:
        if field not in data:
            raise AssertionError(f"{path} missing status field {field}")


def run_compare(args: argparse.Namespace) -> None:
    if not args.manifest and not args.status:
        raise AssertionError("at least one manifest or status file is required")
    compare_representative_matrix(Path(args.representative_matrix))
    for manifest in args.manifest:
        compare_manifest(Path(manifest))
    for status in args.status:
        compare_status(Path(status))
    require_text(Path(args.reference_capture), "reference")
    require_text(Path(args.baseline_matrix), "artifact")
    print("artifact metadata compare passed")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        matrix = root / "representative_products.json"
        manifest = root / "artifact.manifest.json"
        status = root / "artifact.bbf.status.json"
        capture = root / "01-REFERENCE-CAPTURE.md"
        baseline = root / "01-BASELINE-MATRIX.md"
        matrix.write_text(
            json.dumps(
                {
                    "entries": [
                        {
                            "id": "mini_boot",
                            "product": "MINI",
                            "printer": "MINI",
                            "board": "BUDDY",
                            "mcu": "STM32F407VG",
                            "bootloader_mode": "boot",
                            "artifact_outputs": [".bin", ".bbf.status.json"],
                            "evidence_class": "local-smoke",
                            "signing_mode": "unsigned-local",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        manifest.write_text(
            json.dumps(
                {
                    "product": "MINI",
                    "printer": "MINI",
                    "board": "BUDDY",
                    "mcu": "STM32F407VG",
                    "bootloader_mode": "boot",
                    "artifact_kind": "bin",
                    "filename": "mini.bin",
                    "package_members": ["mini.bin"],
                    "version_provenance": ["mini.provenance.json"],
                    "resource_presence": {"has_resource": False, "resources": []},
                    "evidence_class": "local-smoke",
                    "signing_mode": "unsigned-local",
                    "sha256": "0" * 64,
                }
            ),
            encoding="utf-8",
        )
        status.write_text(
            json.dumps(
                {
                    "artifact_kind": "bbf",
                    "status": "bootstrap-required",
                    "evidence_class": "bootstrap-required",
                    "reference_generator": "utils/pack_fw.py --no-sign",
                    "structural_check": "BBF structural check",
                    "signing_mode": "unsigned-local",
                }
            ),
            encoding="utf-8",
        )
        capture.write_text("reference artifact capture\n", encoding="utf-8")
        baseline.write_text("artifact baseline matrix\n", encoding="utf-8")
        args = argparse.Namespace(
            representative_matrix=str(matrix),
            manifest=[str(manifest)],
            status=[str(status)],
            reference_capture=str(capture),
            baseline_matrix=str(baseline),
        )
        run_compare(args)
    print("artifact metadata compare self-test passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare Phase 3 artifact metadata surfaces.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--representative-matrix")
    parser.add_argument("--manifest", action="append", default=[])
    parser.add_argument("--status", action="append", default=[])
    parser.add_argument("--reference-capture")
    parser.add_argument("--baseline-matrix")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        required = ["representative_matrix", "reference_capture", "baseline_matrix"]
        missing = [name for name in required if not getattr(args, name)]
        if missing:
            raise AssertionError(f"missing required args: {', '.join(missing)}")
        run_compare(args)
    except AssertionError as error:
        print(f"artifact metadata compare failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
