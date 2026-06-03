#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DriftCheck:
    check_id: str
    tracked_outputs: tuple[str, ...]
    declared_sources: tuple[str, ...]
    update_command: tuple[str, ...]
    check_strategy: str
    evidence_class: str
    writes_source_tree: bool


REGISTRY: dict[str, DriftCheck] = {
    "product_profiles": DriftCheck("product_profiles", ("tools/bazel/manifests/representative_products.json",), ("ProjectOptions.cmake",), ("python3", "tools/bazel/generated_drift.py", "--update", "--check", "product_profiles"), "normalized-json", "local-smoke", True),
    "option_data": DriftCheck("option_data", ("CMakePresets.json",), ("utils/presets/presets.json",), ("python3", "utils/build.py", "--generate-cmake-presets"), "normalized-json", "local-smoke", True),
    "resources": DriftCheck("resources", ("src/gui/res/cc",), ("src/resources/CMakeLists.txt",), ("python3", "utils/build.py", "--generate-resources"), "bytes", "ci-only", True),
    "translations": DriftCheck("translations", ("src/lang/po/Prusa-Firmware-Buddy.pot",), ("src/lang/CMakeLists.txt",), ("bash", "utils/translations_and_fonts/generate_pot.sh"), "text-lf", "ci-only", True),
    "fonts": DriftCheck("fonts", ("src/gui/res/fnt_png",), ("utils/translations_and_fonts/generate_all_fonts.sh",), ("bash", "utils/translations_and_fonts/generate_all_fonts.sh"), "bytes", "ci-only", True),
    "wui_assets": DriftCheck("wui_assets", ("lib/WUI",), ("lib/WUI",), ("python3", "utils/build.py", "--generate-wui-assets"), "bytes", "ci-only", True),
    "esp_blobs": DriftCheck("esp_blobs", ("lib/esp32-nic", "lib/esp8266-nic"), ("utils/gen_esp_parts.py",), ("python3", "utils/gen_esp_parts.py"), "bytes", "reference-only", True),
    "puppy_descriptors": DriftCheck("puppy_descriptors", ("src/puppies",), ("utils/gen_puppies_descriptor.py",), ("python3", "utils/gen_puppies_descriptor.py"), "text-lf", "reference-only", True),
    "mmu_descriptors": DriftCheck("mmu_descriptors", ("lib/Prusa-Firmware-MMU",), ("lib/AddMMU2.cmake",), ("python3", "utils/gen_puppies_descriptor.py", "--mmu"), "text-lf", "reference-only", True),
    "package_metadata": DriftCheck("package_metadata", ("tools/bazel/manifests/representative_products.json",), ("tools/bazel/artifact_manifest.py",), ("python3", "tools/bazel/generated_drift.py", "--update", "--check", "package_metadata"), "normalized-json", "local-smoke", True),
    "tracked_generated_outputs": DriftCheck("tracked_generated_outputs", ("CMakePresets.json", "doc/logging_components.md", "include/common/visit_all_struct_fields.hpp"), ("utils/build.py", "utils/logging/generate_overview.py", "utils/persistent_stores/visit_all_struct_fields_generator.py"), ("pre-commit", "run", "--all-files"), "mixed", "local-smoke", True),
    "cmake_presets": DriftCheck("cmake_presets", ("CMakePresets.json",), ("utils/presets/presets.json",), ("python3", "utils/build.py", "--generate-cmake-presets"), "normalized-json", "local-smoke", True),
    "logging_components": DriftCheck("logging_components", ("doc/logging_components.md",), ("utils/logging/generate_overview.py",), ("python3", "utils/logging/generate_overview.py"), "text-lf", "local-smoke", True),
    "visit_all_struct_fields": DriftCheck("visit_all_struct_fields", ("include/common/visit_all_struct_fields.hpp",), ("utils/persistent_stores/visit_all_struct_fields_generator.py",), ("python3", "utils/persistent_stores/visit_all_struct_fields_generator.py"), "text-lf", "local-smoke", True),
    "translation_pot": DriftCheck("translation_pot", ("src/lang/po/Prusa-Firmware-Buddy.pot",), ("utils/translations_and_fonts/generate_pot.sh",), ("bash", "utils/translations_and_fonts/generate_pot.sh"), "text-lf", "ci-only", True),
    "font_resources": DriftCheck("font_resources", ("src/gui/res/fnt_png",), ("utils/translations_and_fonts/generate_all_fonts.sh",), ("bash", "utils/translations_and_fonts/generate_all_fonts.sh"), "bytes", "ci-only", True),
    "resource_headers": DriftCheck("resource_headers", ("src/gui/res/cc",), ("src/resources/CMakeLists.txt",), ("python3", "utils/build.py", "--generate-resources"), "bytes", "ci-only", True),
}


def normalize_json(path: Path) -> str:
    return json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2, sort_keys=True) + "\n"


def normalize_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def compare_files(expected: Path, actual: Path, strategy: str) -> list[str]:
    if not actual.exists():
        return [f"DRIFT: missing generated output {actual}"]
    if strategy == "normalized-json":
        if normalize_json(expected) != normalize_json(actual):
            return [f"DRIFT: normalized JSON differs for {expected}"]
        return []
    if strategy == "text-lf":
        if normalize_text(expected) != normalize_text(actual):
            return [f"DRIFT: normalized text differs for {expected}"]
        return []
    if not filecmp.cmp(expected, actual, shallow=False):
        return [f"DRIFT: bytes differ for {expected}"]
    return []


def selected_checks(args: argparse.Namespace) -> list[DriftCheck]:
    ids = args.check or list(REGISTRY)
    missing = [check_id for check_id in ids if check_id not in REGISTRY]
    if missing:
        raise AssertionError(f"unknown generated drift check(s): {', '.join(missing)}")
    return [REGISTRY[check_id] for check_id in ids]


def list_checks() -> None:
    for check in REGISTRY.values():
        print(f"{check.check_id}\t{check.evidence_class}\t{check.check_strategy}\twrites_source_tree={str(check.writes_source_tree).lower()}")


def check_surface(check: DriftCheck, workspace: Path, output_dir: Path, update: bool) -> list[str]:
    print(f"{check.check_id}: evidence_class={check.evidence_class}; strategy={check.check_strategy}")
    if update:
        if not check.update_command:
            raise AssertionError(f"{check.check_id} has no explicit update_command")
        print(f"{check.check_id}: update command declared: {' '.join(check.update_command)}")
        if check.evidence_class != "local-smoke":
            print(f"{check.check_id}: {check.evidence_class} update is not executed by default local generated_update")
            return []
        if "tools/bazel/generated_drift.py" in check.update_command:
            normalize_self_managed_outputs(check, workspace)
            return []
        result = subprocess.run(check.update_command, cwd=workspace, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        if result.returncode != 0:
            raise AssertionError(f"{check.check_id} update command failed:\n{result.stdout}")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    drift: list[str] = []
    for tracked in check.tracked_outputs:
        tracked_path = workspace / tracked
        if not tracked_path.exists() or tracked_path.is_dir():
            print(f"{check.check_id}: tracked output {tracked} is {check.evidence_class}; no local source-tree write in check mode")
            continue
        generated_path = output_dir / tracked
        generated_path.parent.mkdir(parents=True, exist_ok=True)
        if not generated_path.exists():
            shutil.copyfile(tracked_path, generated_path)
        drift.extend(compare_files(tracked_path, generated_path, check.check_strategy))
    return drift


def normalize_self_managed_outputs(check: DriftCheck, workspace: Path) -> None:
    for tracked in check.tracked_outputs:
        path = workspace / tracked
        if not path.exists() or path.is_dir():
            continue
        if check.check_strategy == "normalized-json":
            path.write_text(normalize_json(path), encoding="utf-8")
            print(f"{check.check_id}: normalized {tracked}")


def run_checks(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace).resolve() if args.workspace else ROOT
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = Path(tempfile.mkdtemp(prefix="buddy-phase3-generated-check-"))
    drift: list[str] = []
    for check in selected_checks(args):
        drift.extend(check_surface(check, workspace, output_dir, args.update))
    if drift:
        raise AssertionError("\n".join(drift))


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        workspace = root / "workspace"
        output = root / "out"
        workspace.mkdir()
        tracked = workspace / "tracked.json"
        generated = output / "tracked.json"
        tracked.write_text('{"b": 2, "a": 1}\n', encoding="utf-8")
        generated.parent.mkdir()
        generated.write_text('{"a": 1, "b": 2}\n', encoding="utf-8")
        if compare_files(tracked, generated, "normalized-json"):
            raise AssertionError("normalized JSON comparison should pass")
        generated.write_text('{"a": 1, "b": 3}\n', encoding="utf-8")
        drift = compare_files(tracked, generated, "normalized-json")
        if not drift or "DRIFT:" not in drift[0]:
            raise AssertionError("changed content should report DRIFT")
    print("generated drift self-test passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check or update tracked generated outputs.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--workspace")
    parser.add_argument("--output-dir")
    parser.add_argument("--check", action="append")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--list-checks", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        if args.list_checks:
            list_checks()
            return 0
        run_checks(args)
    except AssertionError as error:
        print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
