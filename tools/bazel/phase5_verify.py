#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_MANIFEST = Path("tools/bazel/manifests/foreign_code_inventory.json")
UNSAFE_AUDIT_MANIFEST = Path("tools/bazel/manifests/unsafe_boundary_audit.json")
PHASE = "05-foreign-code-unsafe-and-runtime-boundary"

REQUIRED_INVENTORY_FIELDS = [
    "id",
    "path",
    "kind",
    "language",
    "source_version_evidence",
    "ownership_boundary",
    "retention_reason",
    "safe_facade",
    "replacement_posture",
    "risk_class",
    "evidence_required",
    "bazel_label",
    "requirements",
]

REQUIRED_UNSAFE_FIELDS = [
    "surface_id",
    "crate",
    "module",
    "source_path",
    "kind",
    "raw_operation",
    "invariant",
    "safe_facade",
    "test_or_static_check",
    "evidence_class",
    "review_status",
    "requirements",
]

REQUIRED_COMPONENT_IDS = [
    "cmake-reference-build-selection",
    "stm32f4-startup-linker",
    "stm32g0-startup-linker",
    "stm32h503-xbuddy-extension-startup-linker",
    "stm32-board-clock-tree",
    "stm32-hal-cmsis",
    "freertos-kernel",
    "freertos-task-queue-timer-runtime",
    "freertos-synchronization-wrappers",
    "buddy-master-runtime-shell",
    "auxiliary-runtime-shells",
    "marlin-reference-core",
    "wui-network-stack",
    "lwip-network-stack",
    "mbedtls-tls",
    "fatfs-media",
    "littlefs-internal",
    "tinyusb-device",
    "libsysbase-runtime",
    "crashcatcher-crashdump",
    "tmc-stepper-drivers",
    "prusa-mmu",
    "prusa-error-codes",
    "libbgcode",
    "lightmodbus",
    "esp-network-firmware",
    "generated-runtime-assets",
    "resource-translation-font-pipeline",
    "persistent-store-reference",
    "connect-transfer-reference",
    "puppy-auxiliary-runtime",
]

REQUIRED_UNSAFE_SURFACE_IDS = [
    "ffi-symbol-contracts",
    "linker-section-contracts",
    "startup-vector-contracts",
    "board-clock-tree-contracts",
    "mmio-register-contracts",
    "dma-buffer-contracts",
    "interrupt-registration-contracts",
    "static-task-memory-contracts",
    "allocator-heap-contracts",
    "panic-bsod-assert-boundary",
    "mutable-static-boundary",
    "crash-dump-memory-boundary",
    "task-dependency-readiness",
    "freertos-queue-contracts",
    "freertos-timer-contracts",
    "freertos-mutex-contracts",
    "freertos-binary-semaphore-contracts",
    "freertos-counting-semaphore-contracts",
    "freertos-event-group-contracts",
    "freertos-wait-condition-contracts",
    "watchdog-boundary",
]

REQUIRED_UNSAFE_KINDS = [
    "ffi",
    "mmio",
    "dma",
    "interrupt",
    "linker-symbol",
    "startup-vector",
    "clock-tree",
    "static-memory",
    "allocator",
    "panic-boundary",
    "mutable-static",
    "crash-dump-memory",
    "task-dependency",
    "queue",
    "timer",
    "mutex",
    "semaphore",
    "event-group",
    "wait-condition",
    "watchdog",
]

REQUIRED_ADAPTER_SOURCE_PATHS = [
    "rust/crates/board-adapter/src/mmio.rs",
    "rust/crates/board-adapter/src/dma.rs",
    "rust/crates/board-adapter/src/interrupt.rs",
    "rust/crates/board-adapter/src/ffi.rs",
    "rust/crates/board-adapter/src/clock.rs",
    "rust/crates/runtime-adapter/src/startup.rs",
    "rust/crates/runtime-adapter/src/linker.rs",
    "rust/crates/runtime-adapter/src/allocator.rs",
    "rust/crates/runtime-adapter/src/panic_boundary.rs",
    "rust/crates/runtime-adapter/src/static_memory.rs",
    "rust/crates/runtime-adapter/src/task.rs",
    "rust/crates/runtime-adapter/src/queue.rs",
    "rust/crates/runtime-adapter/src/timer.rs",
    "rust/crates/runtime-adapter/src/synchronization.rs",
]

ALLOWED_EVIDENCE_CLASSES = {
    "manifest-check",
    "static-source-audit",
    "rust-host-test",
    "bazel-query",
    "simulator-flow",
    "hardware-smoke",
    "manual-hardware-required",
}


class VerificationError(Exception):
    pass


def read_json(path: Path) -> dict[str, Any]:
    full_path = ROOT / path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {path}")

    try:
        data = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{path} is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise VerificationError(f"{path} must contain a top-level JSON object")
    return data


def require_top_level(data: dict[str, Any], path: Path, collection_name: str) -> list[dict[str, Any]]:
    if data.get("schema_version") != 1:
        raise VerificationError(f"{path} must set schema_version to 1")
    if data.get("phase") != PHASE:
        raise VerificationError(f"{path} must set phase to {PHASE}")

    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(f"{path} must contain a {collection_name} list")

    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{path} {collection_name}[{index}] must be an object")
        parsed_rows.append(row)
    return parsed_rows


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        raise VerificationError(f"{row_name} missing required fields: {', '.join(missing)}")

    empty = [field for field in fields if row[field] in ("", [], {}, None)]
    if empty:
        raise VerificationError(f"{row_name} has empty required fields: {', '.join(empty)}")


def require_unique(rows: list[dict[str, Any]], field: str, path: Path) -> set[str]:
    values: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str):
            raise VerificationError(f"{path} row has non-string {field}: {value!r}")
        if value in values:
            duplicates.add(value)
        values.add(value)

    if duplicates:
        raise VerificationError(f"{path} has duplicate {field} values: {', '.join(sorted(duplicates))}")
    return values


def require_ids(actual: set[str], required: list[str], label: str) -> None:
    missing = sorted(set(required) - actual)
    if missing:
        raise VerificationError(f"missing required {label}: {', '.join(missing)}")


def require_requirements(row: dict[str, Any], row_name: str, allowed: set[str]) -> None:
    requirements = row.get("requirements")
    if not isinstance(requirements, list) or not all(isinstance(item, str) for item in requirements):
        raise VerificationError(f"{row_name} requirements must be a list of strings")

    if not set(requirements).intersection(allowed):
        raise VerificationError(f"{row_name} requirements must include at least one of {', '.join(sorted(allowed))}")


def require_text(row: dict[str, Any], row_name: str, needles: list[str]) -> None:
    haystack = json.dumps(row, sort_keys=True)
    missing = [needle for needle in needles if needle not in haystack]
    if missing:
        raise VerificationError(f"{row_name} missing required evidence text: {', '.join(missing)}")


def check_inventory_manifest() -> None:
    data = read_json(INVENTORY_MANIFEST)
    rows = require_top_level(data, INVENTORY_MANIFEST, "components")
    ids = require_unique(rows, "id", INVENTORY_MANIFEST)
    require_ids(ids, REQUIRED_COMPONENT_IDS, "component IDs")

    by_id = {row["id"]: row for row in rows}
    for row in rows:
        row_name = f"{INVENTORY_MANIFEST} component {row.get('id', '<unknown>')}"
        require_fields(row, REQUIRED_INVENTORY_FIELDS, row_name)
        require_requirements(row, row_name, {"RUST-03", "CORE-01", "CORE-02"})

    require_text(
        by_id["stm32f4-startup-linker"],
        "stm32f4-startup-linker",
        [
            "src/device/stm32f4/startup/",
            "src/device/stm32f4/linker/",
            "src/device/stm32f4/cmsis.cpp",
            "src/device/stm32f4/core_init.cpp",
        ],
    )
    require_text(
        by_id["stm32g0-startup-linker"],
        "stm32g0-startup-linker",
        [
            "src/device/stm32g0/startup/",
            "src/device/stm32g0/linker/",
            "src/device/stm32g0/cmsis.cpp",
            "src/device/stm32g0/core_init.cpp",
        ],
    )
    require_text(
        by_id["stm32h503-xbuddy-extension-startup-linker"],
        "stm32h503-xbuddy-extension-startup-linker",
        [
            "src/puppy/xbuddy_extension/stm32h503.s",
            "src/puppy/xbuddy_extension/stm32h503.ld",
            "src/puppy/xbuddy_extension/stm32h503_boot.ld",
            "src/puppy/xbuddy_extension/stm32h503_noboot.ld",
            "src/puppy/xbuddy_extension/cmsis.cpp",
            "src/puppy/xbuddy_extension/hal_clock.cpp",
            "fpv5-sp-d16",
        ],
    )
    require_text(
        by_id["freertos-synchronization-wrappers"],
        "freertos-synchronization-wrappers",
        [
            "src/freertos/mutex.cpp",
            "src/freertos/binary_semaphore.cpp",
            "src/freertos/counting_semaphore.cpp",
            "src/freertos/wait_condition.cpp",
            "include/tasks.hpp",
            "src/common/tasks.cpp",
        ],
    )


def check_unsafe_audit_manifest() -> None:
    data = read_json(UNSAFE_AUDIT_MANIFEST)
    rows = require_top_level(data, UNSAFE_AUDIT_MANIFEST, "surfaces")
    surface_ids = require_unique(rows, "surface_id", UNSAFE_AUDIT_MANIFEST)
    require_ids(surface_ids, REQUIRED_UNSAFE_SURFACE_IDS, "unsafe surface IDs")

    kinds: set[str] = set()
    source_paths: set[str] = set()
    by_id = {row["surface_id"]: row for row in rows}
    for row in rows:
        row_name = f"{UNSAFE_AUDIT_MANIFEST} surface {row.get('surface_id', '<unknown>')}"
        require_fields(row, REQUIRED_UNSAFE_FIELDS, row_name)
        require_requirements(row, row_name, {"RUST-04", "CORE-01", "CORE-02"})

        kind = row["kind"]
        if not isinstance(kind, str):
            raise VerificationError(f"{row_name} kind must be a string")
        kinds.add(kind)

        source_path = row["source_path"]
        if not isinstance(source_path, str):
            raise VerificationError(f"{row_name} source_path must be a string")
        source_paths.add(source_path)

        evidence_class = row["evidence_class"]
        if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
            allowed = ", ".join(sorted(ALLOWED_EVIDENCE_CLASSES))
            raise VerificationError(f"{row_name} evidence_class must be one of: {allowed}")

    require_ids(kinds, REQUIRED_UNSAFE_KINDS, "unsafe kinds")
    require_ids(source_paths, REQUIRED_ADAPTER_SOURCE_PATHS, "adapter source paths")
    require_text(
        by_id["board-clock-tree-contracts"],
        "board-clock-tree-contracts",
        [
            "src/device/stm32f4/core_init.cpp",
            "src/device/stm32f4/cmsis.cpp",
            "src/device/stm32g0/core_init.cpp",
            "src/device/stm32g0/cmsis.cpp",
            "src/puppy/xbuddy_extension/cmsis.cpp",
            "src/puppy/xbuddy_extension/hal_clock.cpp",
            "configCPU_CLOCK_HZ",
            "fpv5-sp-d16",
        ],
    )
    require_text(
        by_id["static-task-memory-contracts"],
        "static-task-memory-contracts",
        ["rust/crates/runtime-adapter/src/static_memory.rs"],
    )
    require_text(
        by_id["allocator-heap-contracts"],
        "allocator-heap-contracts",
        ["rust/crates/runtime-adapter/src/allocator.rs"],
    )
    for surface_id in [
        "freertos-mutex-contracts",
        "freertos-binary-semaphore-contracts",
        "freertos-counting-semaphore-contracts",
        "freertos-event-group-contracts",
        "freertos-wait-condition-contracts",
    ]:
        require_text(
            by_id[surface_id],
            surface_id,
            [
                "src/freertos/mutex.cpp",
                "src/freertos/binary_semaphore.cpp",
                "src/freertos/counting_semaphore.cpp",
                "src/freertos/wait_condition.cpp",
                "include/tasks.hpp",
                "src/common/tasks.cpp",
            ],
        )


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
        raise VerificationError(f"command failed: {' '.join(command)}\n{result.stdout}")


def check_rust_toolchain() -> None:
    run(["cargo", "fmt", "--all", "--", "--check"])
    run(["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"])
    run(["cargo", "build", "--all-targets", "--all-features"])
    run(["cargo", "test", "--all-features"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 5 runtime boundary manifests")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Run inventory and unsafe-audit checks")
    mode.add_argument("--all", action="store_true", help="Run quick checks plus Cargo format, lint, build, and tests")
    mode.add_argument("--inventory-only", action="store_true", help="Run only retained foreign-code inventory checks")
    mode.add_argument("--audit-only", action="store_true", help="Run only unsafe/runtime-boundary audit checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if args.inventory_only:
            check_inventory_manifest()
        elif args.audit_only:
            check_unsafe_audit_manifest()
        else:
            check_inventory_manifest()
            check_unsafe_audit_manifest()
            if args.all:
                check_rust_toolchain()

        print("Phase 5 runtime boundary verification passed")
        return 0
    except VerificationError as error:
        print(f"Phase 5 runtime boundary verification failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
