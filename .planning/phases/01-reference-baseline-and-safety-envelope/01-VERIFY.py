#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


PHASE_DIR = Path(__file__).resolve().parent

ARTIFACTS = {
    "BASE-01": PHASE_DIR / "01-BASELINE-MATRIX.md",
    "BASE-02": PHASE_DIR / "01-REFERENCE-CAPTURE.md",
    "BASE-03": PHASE_DIR / "01-CONCERN-LEDGER.md",
    "BASE-04": PHASE_DIR / "01-SAFETY-ENVELOPE.md",
}

REQUIRED_STRINGS = {
    "BASE-01": [
        "ProjectOptions.cmake",
        "utils/presets/presets.json",
        "CMakePresets.json",
        "CMakeLists.txt",
        "utils/build.py",
        "COREONE",
        "MINI",
        "MK4",
        "MK3.5",
        "XL",
        "iX",
        "XL_DEV_KIT",
        "BUDDY",
        "XBUDDY",
        "XLBUDDY",
        "DWARF",
        "MODULARBED",
        "XL_DEV_KIT_XLB",
        "XBUDDY_EXTENSION",
        "STM32F407VG",
        "STM32F429VI",
        "STM32F427ZI",
        "STM32G070RBT6",
        "STM32H503CBU7",
        ".bin",
        ".bbf",
        ".dfu",
        ".map",
    ],
    "BASE-02": [
        "local-smoke",
        "ci-only",
        "simulator-flow",
        "hardware-smoke",
        "manual-hardware-required",
        "reference-contract",
        "python3 utils/build.py --generate-cmake-presets",
        "pytest tests/integration --firmware <firmware.bin>",
    ],
    "BASE-03": [
        "preserve-temporarily",
        "fix-during-rewrite",
        "defer",
        "src/connect/tls/tls.cpp",
        "src/common/probe_analysis.cpp",
        "src/gui/screen_home.cpp",
        "src/transfers/partial_file.cpp",
    ],
    "BASE-04": [
        "source-audit",
        "host-test",
        "simulator-flow",
        "hardware-smoke",
        "manual-hardware-required",
        "src/buddy/main.cpp",
        "src/common/Pin.cpp",
        "src/common/crash_dump/dump.cpp",
        "src/persistent_stores/store_instances/config_store/store_definition.hpp",
    ],
}

ALLOWED_DISPOSITIONS = {"preserve-temporarily", "fix-during-rewrite", "defer"}


def read_text(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"missing artifact: {path}")
    return path.read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, path: Path) -> None:
    if needle not in text:
        raise AssertionError(f"{path} missing required text: {needle}")


def verify_artifact(requirement: str, path: Path) -> None:
    text = read_text(path)
    assert_contains(text, requirement, path)

    for needle in REQUIRED_STRINGS[requirement]:
        assert_contains(text, needle, path)


def verify_dispositions(path: Path) -> None:
    text = read_text(path)
    dispositions = re.findall(r"\|\s*(preserve-temporarily|fix-during-rewrite|defer)\s*\|", text)
    if len(dispositions) < 10:
        raise AssertionError(f"{path} has too few disposition markers")

    explicit_markers = re.findall(r"disposition:\s*([a-z-]+)", text)
    bad_markers = [marker for marker in explicit_markers if marker not in ALLOWED_DISPOSITIONS]
    if bad_markers:
        raise AssertionError(f"{path} has invalid disposition markers: {bad_markers}")


def main() -> int:
    try:
        for requirement, path in ARTIFACTS.items():
            verify_artifact(requirement, path)
        verify_dispositions(ARTIFACTS["BASE-03"])
    except AssertionError as error:
        print(f"Phase 1 verification failed: {error}", file=sys.stderr)
        return 1

    print("Phase 1 verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
