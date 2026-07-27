#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from phase9_contract_policy import *  # noqa: F403


def check_connect_manifest() -> None:
    rows = validate_contract_rows(
        CONNECT_MANIFEST,
        "connect_contracts",
        CONNECT_FIELDS,
        REQUIRED_CONNECT_ROW_IDS,
        {"IFCE-02"},
    )
    row_by_id = {row["id"]: row for row in rows}
    errors: list[str] = []
    checks = {
        "connect-registration-token-fingerprint": ["Token", "Fingerprint"],
        "connect-tls-required-verification-policy": [
            "MBEDTLS_SSL_VERIFY_REQUIRED",
            "MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
            "/internal/connect/connect.der",
        ],
        "connect-proxy-minimal-limitations": [
            "proxy-authentication-absent",
            "printer-to-proxy-leg-unencrypted",
            "proxy-active-only-when-connect_tls-true",
        ],
    }
    for row_id, required_text in checks.items():
        try:
            require_row_text(row_by_id[row_id], required_text,
                             f"{CONNECT_MANIFEST.as_posix()} row {row_id}")
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_wui_manifest() -> None:
    rows = validate_contract_rows(
        WUI_MANIFEST,
        "wui_contracts",
        WUI_FIELDS,
        REQUIRED_WUI_ROW_IDS,
        {"IFCE-03"},
    )
    errors: list[str] = []
    for row in rows:
        row_name = f"{WUI_MANIFEST.as_posix()} row {row['id']}"
        try:
            require_list_of_strings(row, "methods", row_name)
            require_list_of_strings(row, "status_behavior", row_name)
            require_list_of_strings(row, "auth_modes", row_name)
            require_list_of_strings(row, "resource_limits", row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_transfer_manifest() -> None:
    rows = validate_contract_rows(
        TRANSFER_MANIFEST,
        "transfer_contracts",
        TRANSFER_FIELDS,
        REQUIRED_TRANSFER_ROW_IDS,
        {"IFCE-02", "IFCE-03", "IFCE-02/IFCE-03"},
    )
    row_by_id = {row["id"]: row for row in rows}
    errors: list[str] = []
    checks = {
        "transfer-single-active-slot": ["single-active-transfer-slot"],
        "transfer-encrypted-aes-ctr-payload": ["AES-CTR"],
    }
    for row_id, required_text in checks.items():
        try:
            require_row_text(row_by_id[row_id], required_text,
                             f"{TRANSFER_MANIFEST.as_posix()} row {row_id}")
        except VerificationError as error:
            errors.append(str(error))

    media_row = row_by_id["transfer-media-race-non-local"]
    if media_row.get("proof_scope") != "non-local" or media_row.get(
            "evidence_class") not in NON_LOCAL_EVIDENCE_CLASSES:
        errors.append(
            f"{TRANSFER_MANIFEST.as_posix()} row transfer-media-race-non-local must remain non-local and use manual-hardware-required evidence"
        )
    if errors:
        raise VerificationError("\n".join(errors))


def check_network_services_manifest() -> None:
    rows = validate_contract_rows(
        NETWORK_SERVICES_MANIFEST,
        "network_service_contracts",
        NETWORK_SERVICE_FIELDS,
        REQUIRED_NETWORK_SERVICE_ROW_IDS,
        {"IFCE-03"},
    )
    errors: list[str] = []
    for row in rows:
        row_name = f"{NETWORK_SERVICES_MANIFEST.as_posix()} row {row['id']}"
        try:
            for field in [
                    "feature_gate", "build_gate", "transport", "config_keys",
                    "runtime_defaults"
            ]:
                require_list_of_strings(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_concern_dispositions() -> None:
    data = read_json(CONCERN_DISPOSITIONS_MANIFEST)
    rows = require_top_level(data, CONCERN_DISPOSITIONS_MANIFEST, "concerns")
    row_ids = require_unique(rows, "id", CONCERN_DISPOSITIONS_MANIFEST)
    require_ids(row_ids, REQUIRED_CONCERN_ROW_IDS, "concern row IDs")

    errors: list[str] = []
    for row in rows:
        row_name = f"{CONCERN_DISPOSITIONS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, CONCERN_FIELDS, row_name)
            require_requirement_id(row,
                                   {"IFCE-02", "IFCE-03", "IFCE-02/IFCE-03"},
                                   row_name)
            require_existing_reference_sources(row, row_name)
            require_evidence_and_scope(row, row_name)
            require_secret_and_delta(row, row_name)
            require_phase_lifecycle(row, row_name)
            require_string(row, "concern_id", row_name)
            require_string_or_list_of_strings(row, "phase9_handling", row_name)
            require_string_or_list_of_strings(row, "regression_guard",
                                              row_name)
        except VerificationError as error:
            errors.append(str(error))

    row_by_id = {row["id"]: row for row in rows}
    checks = {
        "concern-phase9-custom-der-cert-read": [
            "valid DER",
            "missing DER",
            "invalid DER",
            "/internal/connect/connect.der",
        ],
        "concern-phase9-weak-digest-modules":
        ["MBEDTLS_SHA1_C", "MBEDTLS_MD5_C"],
        "concern-phase9-proxy-limitations": [
            "proxy-authentication-absent",
            "printer-to-proxy-leg-unencrypted",
            "proxy-active-only-when-connect_tls-true",
        ],
        "concern-phase9-crash-dump-upload-boundary": ["redaction"],
    }
    for row_id, required_text in checks.items():
        try:
            require_row_text(
                row_by_id[row_id],
                required_text,
                f"{CONCERN_DISPOSITIONS_MANIFEST.as_posix()} row {row_id}",
            )
        except VerificationError as error:
            errors.append(str(error))

    if errors:
        raise VerificationError("\n".join(errors))


def check_network_rust_api_surface() -> None:
    network_text = read_text(NETWORK_RUST)
    lib_text = read_text(RUST_DOMAIN_LIB)
    sanitized_network = strip_rust_comments_and_strings(network_text)
    errors: list[str] = []

    if "pub mod network;" not in lib_text:
        errors.append(
            f"{RUST_DOMAIN_LIB.as_posix()} must export pub mod network;")
    if "#![forbid(unsafe_code)]" not in lib_text:
        errors.append(
            f"{RUST_DOMAIN_LIB.as_posix()} must retain #![forbid(unsafe_code)]"
        )

    for api_string in RUST_API_STRINGS:
        if api_string not in network_text:
            errors.append(
                f"{NETWORK_RUST.as_posix()} missing Rust API surface: {api_string}"
            )
        if api_string not in lib_text:
            errors.append(
                f"{RUST_DOMAIN_LIB.as_posix()} missing Rust API export: {api_string}"
            )

    for label, pattern in UNSAFE_RUST_PATTERNS:
        if pattern in sanitized_network:
            errors.append(
                f"{NETWORK_RUST.as_posix()} contains {label}: {pattern}")

    if errors:
        raise VerificationError("\n".join(errors))


def artifact_texts(paths: list[Path]) -> list[tuple[Path, str]]:
    texts: list[tuple[Path, str]] = []
    for path in paths:
        texts.append((path, read_text(path)))
    phase_dir = ROOT / ".planning/phases/09-network-web-services-and-transfers"
    if phase_dir.exists():
        for summary_path in sorted(phase_dir.glob("09-*-SUMMARY.md")):
            relative_path = summary_path.relative_to(ROOT)
            texts.append(
                (relative_path, summary_path.read_text(encoding="utf-8")))
    return texts


def check_secret_markers() -> None:
    errors: list[str] = []
    for path, text in artifact_texts(PHASE9_ARTIFACTS_FOR_SECURITY_SCAN):
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                errors.append(
                    f"{path.as_posix()} contains forbidden secret marker: {marker}"
                )
    if errors:
        raise VerificationError("\n".join(errors))


def check_no_phase9_overclaim() -> None:
    errors: list[str] = []
    for path, text in artifact_texts(PHASE9_ARTIFACTS_FOR_SECURITY_SCAN):
        lowered = text.lower()
        for phrase in OVERCLAIM_STRINGS:
            if phrase.lower() in lowered:
                errors.append(
                    f"{path.as_posix()} contains non-local evidence overclaim: {phrase}"
                )
    if errors:
        raise VerificationError("\n".join(errors))


def check_validation_contract() -> None:
    text = read_text(VALIDATION_CONTRACT)
    required_text = [
        "status: complete",
        "nyquist_compliant: true",
        "wave_0_complete: true",
        f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
        "python3 tools/bazel/phase9_verify.py --quick",
        "just phase9-verify",
        "09-W0-01",
        "09-W0-05",
        "manual-hardware-required",
        "hardware-smoke",
        "simulator-flow",
    ]
    missing = [needle for needle in required_text if needle not in text]
    if missing:
        raise VerificationError(
            f"{VALIDATION_CONTRACT.as_posix()} missing validation lifecycle contract text: "
            + ", ".join(missing))


def require_file_text(path: str | Path, required_text: list[str]) -> None:
    text = read_text(path)
    missing = [needle for needle in required_text if needle not in text]
    if missing:
        relative_path = Path(path)
        raise VerificationError(
            f"{relative_path.as_posix()} missing required wiring text: " +
            ", ".join(missing))


def require_exact_lines(path: str | Path, required_lines: list[str]) -> None:
    lines = {line.strip() for line in read_text(path).splitlines()}
    missing = [line for line in required_lines if line not in lines]
    if missing:
        relative_path = Path(path)
        raise VerificationError(
            f"{relative_path.as_posix()} missing required lines: " +
            ", ".join(missing))


def require_file_patterns(path: str | Path,
                          required_patterns: list[tuple[str, str]]) -> None:
    text = read_text(path)
    missing = [
        description for pattern, description in required_patterns
        if re.search(pattern, text, re.MULTILINE) is None
    ]
    if missing:
        relative_path = Path(path)
        raise VerificationError(
            f"{relative_path.as_posix()} missing required wiring patterns: " +
            ", ".join(missing))


def check_bazel_surface() -> None:
    errors: list[str] = []
    pattern_checks = [
        (
            Path("BUILD.bazel"),
            [
                (r'name\s*=\s*"phase9_network_web_services_docs"',
                 "phase9_network_web_services_docs"),
                (r'name\s*=\s*"phase9_verify"', "phase9_verify"),
                (r'actual\s*=\s*"//tools/bazel:phase9_verify"',
                 "//tools/bazel:phase9_verify"),
                (r'name\s*=\s*"phase9_verify_tests"', "phase9_verify_tests"),
                (
                    r'actual\s*=\s*"//tools/bazel:phase9_verify_tests"',
                    "//tools/bazel:phase9_verify_tests",
                ),
            ],
        ),
        (
            Path("tools/bazel/BUILD.bazel"),
            [
                (r'name\s*=\s*"phase9_verify"', "phase9_verify"),
                (r'name\s*=\s*"phase9_verify_tests"', "phase9_verify_tests"),
                (r'"phase9_verify\.py"', "phase9_verify.py"),
                (r'"phase9_verify_test\.py"', "phase9_verify_test.py"),
                (r'"phase9_negative_fixtures\.py"',
                 "phase9_negative_fixtures.py"),
                (r'"phase9_negative_fixtures_test\.py"',
                 "phase9_negative_fixtures_test.py"),
                (r'"(?:manifests/)?phase9_connect_contracts\.json"',
                 "phase9_connect_contracts.json"),
                (r'"(?:manifests/)?phase9_wui_contracts\.json"',
                 "phase9_wui_contracts.json"),
                (r'"(?:manifests/)?phase9_transfer_contracts\.json"',
                 "phase9_transfer_contracts.json"),
                (
                    r'"(?:manifests/)?phase9_network_service_contracts\.json"',
                    "phase9_network_service_contracts.json",
                ),
                (
                    r'"(?:manifests/)?phase9_network_concern_dispositions\.json"',
                    "phase9_network_concern_dispositions.json",
                ),
                (r'"//:phase9_network_web_services_docs"',
                 "//:phase9_network_web_services_docs"),
                (r'"//:rust_workspace_sources"', "//:rust_workspace_sources"),
            ],
        ),
    ]
    for path, required_patterns in pattern_checks:
        try:
            require_file_patterns(path, required_patterns)
        except VerificationError as error:
            errors.append(str(error))
    try:
        require_exact_lines(
            "tools/bazel/rust_workflow.sh",
            [
                "phase9_verify)",
                "python3 tools/bazel/phase9_verify.py --all",
                "phase9_verify_tests)",
                "python3 tools/bazel/phase9_verify_test.py",
                "python3 tools/bazel/phase9_negative_fixtures_test.py",
            ],
        )
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_just_surface() -> None:
    lines = [line.strip() for line in read_text("justfile").splitlines()]
    required_lines = [
        "phase9-verify:",
        "bazel run //tools/bazel:phase9_verify_tests",
        "bazel run //tools/bazel:phase9_verify",
    ]
    missing = [line for line in required_lines if line not in lines]
    errors = [f"justfile missing required lines: {', '.join(missing)}"
              ] if missing else []
    test_index = lines.index(
        "bazel run //tools/bazel:phase9_verify_tests") if not missing else -1
    verify_index = lines.index(
        "bazel run //tools/bazel:phase9_verify") if not missing else -1
    if test_index == -1 or verify_index == -1 or test_index > verify_index:
        errors.append(
            "justfile must run phase9_verify_tests before phase9_verify")
    if errors:
        raise VerificationError("\n".join(errors))


def check_manifests() -> None:
    checks = [
        check_connect_manifest,
        check_wui_manifest,
        check_transfer_manifest,
        check_network_services_manifest,
        check_concern_dispositions,
    ]
    collect_errors(checks)


def check_security_contract() -> None:
    collect_errors([
        check_secret_markers, check_no_phase9_overclaim,
        check_negative_fixtures
    ])


def check_quick() -> None:
    collect_errors([
        check_connect_manifest,
        check_wui_manifest,
        check_transfer_manifest,
        check_network_services_manifest,
        check_concern_dispositions,
        check_network_rust_api_surface,
        check_validation_contract,
        check_bazel_surface,
        check_just_surface,
        check_secret_markers,
        check_no_phase9_overclaim,
        check_negative_fixtures,
    ])


def run_command(command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        joined = " ".join(command)
        raise VerificationError(
            f"{joined} failed with exit code {result.returncode}\n{result.stdout}"
        )


def check_negative_fixtures() -> None:
    run_command([
        sys.executable,
        NEGATIVE_FIXTURE_RUNNER.as_posix(),
        "--cases",
        NEGATIVE_FIXTURE_CASES.as_posix(),
    ])


def check_all() -> None:
    check_quick()
    if shutil.which("cargo") is None:
        raise VerificationError("cargo is required for --all")
    run_command(["cargo", "fmt", "--all", "--check"])
    run_command([
        "cargo", "clippy", "--all-targets", "--all-features", "--", "-D",
        "warnings"
    ])
    run_command(["cargo", "build", "--all-targets", "--all-features"])
    run_command(["cargo", "test", "--all-features"])


def collect_errors(checks: list[Callable[[], None]]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify Phase 9 network/web/transfer parity artifacts.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--quick",
                       action="store_true",
                       help="run local static Phase 9 verification")
    modes.add_argument("--all",
                       action="store_true",
                       help="run static verification plus Rust checks")
    modes.add_argument("--manifests-only",
                       action="store_true",
                       help="verify only Phase 9 manifests")
    modes.add_argument("--rust-only",
                       action="store_true",
                       help="verify only Rust domain API surface")
    modes.add_argument("--security-only",
                       action="store_true",
                       help="verify only secret and overclaim guards")
    modes.add_argument(
        "--negative-fixtures-only",
        action="store_true",
        help="verify only Phase 9 negative protocol/TLS fixtures",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.all:
        check = check_all
    elif args.manifests_only:
        check = check_manifests
    elif args.rust_only:
        check = check_network_rust_api_surface
    elif args.security_only:
        check = check_security_contract
    elif args.negative_fixtures_only:
        check = check_negative_fixtures
    else:
        check = check_quick

    try:
        check()
    except VerificationError as error:
        print(
            f"Phase 9 network web services and transfers verification failed:\n{error}",
            file=sys.stderr)
        return 1

    print("Phase 9 network web services and transfers verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
