#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

INVENTORY_MANIFEST = Path("tools/bazel/manifests/foreign_code_inventory.json")
UNSAFE_AUDIT_MANIFEST = Path(
    "tools/bazel/manifests/unsafe_boundary_audit.json")
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

REQUIRED_AUDIT_SOURCE_PATHS = [
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

REQUIRED_ADAPTER_MODULE_FILES = [
    "rust/crates/board-adapter/src/mcu.rs",
    "rust/crates/board-adapter/src/clock.rs",
    "rust/crates/board-adapter/src/memory_region.rs",
    "rust/crates/board-adapter/src/dma.rs",
    "rust/crates/board-adapter/src/mmio.rs",
    "rust/crates/board-adapter/src/interrupt.rs",
    "rust/crates/board-adapter/src/ffi.rs",
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

PURE_UNSAFE_FREE_FILES = [
    "rust/crates/domain/src/lib.rs",
    "rust/crates/application/src/lib.rs",
]

REQUIRED_SYNC_SURFACE_IDS = [
    "board-clock-tree-contracts",
    "freertos-mutex-contracts",
    "freertos-binary-semaphore-contracts",
    "freertos-counting-semaphore-contracts",
    "freertos-event-group-contracts",
    "freertos-wait-condition-contracts",
]

REQUIRED_EXACT_AUDIT_SOURCE_ROWS = [
    ("rust/crates/runtime-adapter/src/allocator.rs",
     "allocator-heap-contracts"),
    ("rust/crates/runtime-adapter/src/static_memory.rs",
     "static-task-memory-contracts"),
]

UNSAFE_RUST_PATTERNS = [
    ("unsafe block", "unsafe {"),
    ("unsafe function", "unsafe fn"),
    ("unsafe trait", "unsafe trait"),
    ("unsafe impl", "unsafe impl"),
    ("unsafe extern", "unsafe extern"),
    ("unsafe attribute", "#[unsafe("),
    ("adapter unsafe allowance", "#![allow(unsafe_code)]"),
    ("adapter unsafe allowance", "#[allow(unsafe_code)]"),
]

HARDWARE_OVERCLAIM_STRINGS = [
    "hardware-safe",
    "hardware passed",
    "hardware verified locally",
    "locally passed hardware",
]

PHASE5_MARKDOWN_ARTIFACTS = [
    ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-FOREIGN-CODE-INVENTORY.md",
    ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-UNSAFE-BOUNDARY-AUDIT.md",
    ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-VALIDATION.md",
    ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-01-SUMMARY.md",
    ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-02-SUMMARY.md",
    ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-03-SUMMARY.md",
    ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-04-SUMMARY.md",
    ".planning/phases/05-foreign-code-unsafe-and-runtime-boundary/05-05-SUMMARY.md",
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


def blank_non_code(output: list[str], text: str) -> None:
    for character in text:
        output.append("\n" if character == "\n" else " ")


def raw_string_end_index(text: str, start: int) -> int | None:
    if text.startswith("br", start):
        marker_index = start + 2
    elif text.startswith("r", start):
        marker_index = start + 1
    else:
        return None

    while marker_index < len(text) and text[marker_index] == "#":
        marker_index += 1

    if marker_index >= len(text) or text[marker_index] != '"':
        return None

    hash_count = marker_index - start - (2 if text.startswith("br", start) else
                                         1)
    delimiter = '"' + ("#" * hash_count)
    maybe_end = text.find(delimiter, marker_index + 1)
    if maybe_end == -1:
        return len(text)
    return maybe_end + len(delimiter)


def quoted_string_end_index(text: str, start: int) -> int:
    index = start + 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == '"':
            return index + 1
        index += 1
    return len(text)


def rust_code_without_comments_or_strings(text: str) -> str:
    output: list[str] = []
    index = 0
    block_comment_depth = 0

    while index < len(text):
        if block_comment_depth > 0:
            if text.startswith("/*", index):
                blank_non_code(output, "/*")
                index += 2
                block_comment_depth += 1
                continue
            if text.startswith("*/", index):
                blank_non_code(output, "*/")
                index += 2
                block_comment_depth -= 1
                continue

            blank_non_code(output, text[index])
            index += 1
            continue

        maybe_raw_end = raw_string_end_index(text, index)
        if maybe_raw_end is not None:
            blank_non_code(output, text[index:maybe_raw_end])
            index = maybe_raw_end
            continue

        if text.startswith("//", index):
            line_end = text.find("\n", index)
            if line_end == -1:
                blank_non_code(output, text[index:])
                break

            blank_non_code(output, text[index:line_end])
            index = line_end
            continue

        if text.startswith("/*", index):
            blank_non_code(output, "/*")
            index += 2
            block_comment_depth = 1
            continue

        if text[index] == '"':
            string_end = quoted_string_end_index(text, index)
            blank_non_code(output, text[index:string_end])
            index = string_end
            continue

        output.append(text[index])
        index += 1

    return "".join(output)


def unsafe_findings_for_file(relative_path: Path, text: str) -> list[str]:
    findings: list[str] = []
    code = rust_code_without_comments_or_strings(text)
    for line_number, line in enumerate(code.splitlines(), start=1):
        if "#![forbid(unsafe_code)]" in line:
            continue

        for label, pattern in UNSAFE_RUST_PATTERNS:
            if pattern in line:
                findings.append(f"{relative_path}:{line_number}: {label}")
    return findings


def check_unsafe_scanner_regressions() -> None:
    harmless_text = "\n".join([
        "#![forbid(unsafe_code)]",
        "// unsafe { unsafe fn unsafe extern #[unsafe(no_mangle)]",
        'const MESSAGE: &str = "unsafe { unsafe fn unsafe extern #[unsafe(no_mangle)]";',
        'const RAW: &str = r#"unsafe { unsafe fn unsafe extern #[unsafe(no_mangle)]"#;',
        "/* unsafe {",
        "   /* unsafe fn */",
        "   unsafe extern",
        "*/",
        "fn safe() {}",
    ])
    harmless_findings = unsafe_findings_for_file(Path("scanner_harmless.rs"),
                                                 harmless_text)
    if harmless_findings:
        raise VerificationError(
            "unsafe scanner flagged harmless comments or strings:\n" +
            "\n".join(harmless_findings))

    unsafe_text = "\n".join([
        "fn audited() {",
        "    unsafe { core::ptr::read_volatile(0 as *const u32); }",
        "}",
        "unsafe fn audited_fn() {}",
        'unsafe extern "C" {',
        "    fn retained_symbol();",
        "}",
        "#[unsafe(no_mangle)]",
        'pub extern "C" fn exported() {}',
    ])
    findings = set(
        unsafe_findings_for_file(Path("scanner_unsafe.rs"), unsafe_text))
    expected_findings = {
        "scanner_unsafe.rs:2: unsafe block",
        "scanner_unsafe.rs:4: unsafe function",
        "scanner_unsafe.rs:5: unsafe extern",
        "scanner_unsafe.rs:8: unsafe attribute",
    }
    missing = sorted(expected_findings - findings)
    if missing:
        raise VerificationError("unsafe scanner missed real unsafe syntax:\n" +
                                "\n".join(missing))
