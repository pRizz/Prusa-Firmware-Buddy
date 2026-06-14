#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase9_verify.py"
NEGATIVE_RUNNER = ROOT / "tools/bazel/phase9_negative_fixtures.py"

PHASE = "09-network-web-services-and-transfers"
PHASE_LIFECYCLE_ID = "9-2026-06-14T02-15-21"
PHASE_DIR = ".planning/phases/09-network-web-services-and-transfers"

REQUIRED_CONNECT_ROW_IDS = [
    "connect-registration-token-fingerprint",
    "connect-config-host-token-proxy-tls",
    "connect-telemetry-events",
    "connect-command-polling-websocket",
    "connect-host-decompression-connection-reuse",
    "connect-tls-required-verification-policy",
    "connect-proxy-minimal-limitations",
    "connect-transfer-download-integration",
    "connect-sleep-backoff-shared-buffer-limits",
]

REQUIRED_WUI_ROW_IDS = [
    "wui-server-resource-model",
    "wui-static-assets",
    "prusalink-api-v1-status-job-files-transfer",
    "octoprint-compatible-api",
    "wui-digest-auth-nonce-stale",
    "wui-api-key-auth",
    "wui-usb-file-storage-paths",
    "wui-upload-transfer-renderer",
    "wui-unknown-request-error",
    "wui-responsive-static-ui-contract",
]

REQUIRED_TRANSFER_ROW_IDS = [
    "transfer-single-active-slot",
    "transfer-connect-command-initiation",
    "transfer-wui-upload-api-integration",
    "transfer-range-request",
    "transfer-encrypted-aes-ctr-payload",
    "transfer-partial-file-direct-sector",
    "transfer-recovery-and-changed-path",
    "transfer-error-outcome-mapping",
    "transfer-media-race-non-local",
]

REQUIRED_NETWORK_SERVICE_ROW_IDS = [
    "sntp-client-default-server",
    "mdns-optional-announcement",
    "dns-lwip-network-resolution",
    "metrics-runtime-config-udp",
    "metrics-line-protocol-throttling",
    "syslog-udp-destination",
    "network-feature-gates-wui-connect",
]

REQUIRED_CONCERN_ROW_IDS = [
    "concern-phase9-custom-der-cert-read",
    "concern-phase9-weak-digest-modules",
    "concern-phase9-proxy-limitations",
    "concern-phase9-stale-connect-module-tests",
    "concern-phase9-whole-response-shared-buffers",
    "concern-phase9-transfer-media-races",
    "concern-phase9-transfer-monitor-lock-order",
    "concern-phase9-crash-dump-upload-boundary",
    "concern-phase9-network-tls-coverage-gaps",
]

REQUIRED_NEGATIVE_CASE_IDS = [
    "custom-cert-valid-der-intentional-delta",
    "custom-cert-missing-der-preserved-defect",
    "custom-cert-invalid-der-rejected",
    "invalid-certificate-chain-rejected",
    "weak-signature-sha1-md5-dispositioned",
    "duplicate-connect-command-rejected",
    "large-websocket-command-rejected",
    "proxy-tls-only-no-auth-plain-leg-preserved",
    "stalled-network-transfer-timeout-classified",
]

RUST_API_STRINGS = [
    "NetworkEvidenceClass",
    "NetworkParityRowId",
    "SecretHandling",
    "ConnectCommandState",
    "ProxyMode",
    "WuiAuthMode",
    "TransferSlotState",
    "TransferRange",
    "EncryptedPayloadMetadata",
    "NetworkServiceContract",
    "NetworkParityContract",
    "NetworkServiceContractInput",
    "NetworkParityContractInput",
]

FORBIDDEN_MARKERS = [
    "token_value",
    "password_value",
    "wifi_password",
    "certificate_bytes",
    "private_key",
    "BEGIN PRIVATE KEY",
    "raw_crash_dump",
    "crash_dump_payload",
]

OVERCLAIM_STRINGS = [
    "cloud verified locally",
    "live Connect passed",
    "real TLS handshake passed",
    "physical Wi-Fi verified locally",
    "physical Ethernet verified locally",
    "USB media race passed locally",
    "long-running transfer verified locally",
    "simulator network flow passed locally",
    "raw crash dump upload approved",
    "cutover evidence complete",
]


class Phase9VerifierTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase9_verify.py"
        return subprocess.run(
            [sys.executable, verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel").mkdir(parents=True)
        (root / "tools/bazel/fixtures").mkdir(parents=True)
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase9_verify.py")
        if NEGATIVE_RUNNER.exists():
            shutil.copy2(NEGATIVE_RUNNER, root / "tools/bazel/phase9_negative_fixtures.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def write_source_paths(self, root: Path, paths: list[str]) -> None:
        for source_path in paths:
            if source_path.endswith("/"):
                (root / source_path).mkdir(parents=True, exist_ok=True)
                continue
            self.write_file(root, source_path, "// reference source")

    def base_contract_row(
        self,
        root: Path,
        row_id: str,
        requirement_id: str,
        reference_sources: list[str],
    ) -> dict[str, object]:
        self.write_source_paths(root, reference_sources)
        return {
            "id": row_id,
            "requirement_id": requirement_id,
            "surface": row_id,
            "reference_sources": reference_sources,
            "reference_behavior": f"{row_id} retained source-backed behavior",
            "rust_surface": f"buddy-domain::network::{row_id}",
            "auth_requirement": "none",
            "integration_point": "network",
            "evidence_class": "source-audit",
            "proof_scope": "local",
            "secret_handling": "none",
            "intentional_delta": "none",
            "non_local_evidence": ["runtime network proof remains non-local"],
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        }

    def connect_row(self, root: Path, row_id: str) -> dict[str, object]:
        sources_by_id = {
            "connect-registration-token-fingerprint": [
                "src/connect/registrator.cpp",
                "src/connect/connect.cpp",
                "src/connect/printer.hpp",
            ],
            "connect-tls-required-verification-policy": [
                "src/connect/tls/tls.cpp",
                "src/connect/tls/net_sockets.cpp",
            ],
            "connect-proxy-minimal-limitations": [
                "src/common/http/proxy.cpp",
                "doc/proxy_support.md",
            ],
            "connect-command-polling-websocket": [
                "src/connect/command.cpp",
                "src/common/http/websocket.cpp",
            ],
        }
        row = self.base_contract_row(
            root,
            row_id,
            "IFCE-02",
            sources_by_id.get(row_id, ["src/connect/connect.cpp"]),
        )
        row["auth_requirement"] = "connect-token"
        row["secret_handling"] = "named-only-redacted"
        row["protocol_headers"] = ["Token", "Fingerprint"]
        row["tls_policy"] = ["MBEDTLS_SSL_VERIFY_REQUIRED"]
        row["proxy_limitations"] = []
        if row_id == "connect-proxy-minimal-limitations":
            row["proxy_limitations"] = [
                "proxy-authentication-absent",
                "printer-to-proxy-leg-unencrypted",
                "proxy-active-only-when-connect_tls-true",
            ]
        return row

    def write_connect_manifest(
        self,
        root: Path,
        maybe_rows: list[dict[str, object]] | None = None,
    ) -> None:
        rows = maybe_rows or [self.connect_row(root, row_id) for row_id in REQUIRED_CONNECT_ROW_IDS]
        self.write_file(
            root,
            "tools/bazel/manifests/phase9_connect_contracts.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "phase": PHASE,
                    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
                    "connect_contracts": rows,
                }
            ),
        )

    def wui_row(self, root: Path, row_id: str) -> dict[str, object]:
        sources_by_id = {
            "wui-server-resource-model": ["lib/WUI/nhttp/server.cpp", "lib/WUI/nhttp/README.md"],
            "wui-digest-auth-nonce-stale": ["lib/WUI/nhttp/req_parser.cpp"],
            "wui-api-key-auth": ["lib/WUI/nhttp/headers.cpp"],
        }
        row = self.base_contract_row(
            root,
            row_id,
            "IFCE-03",
            sources_by_id.get(row_id, ["lib/WUI/link_content/prusa_link_api_v1.cpp"]),
        )
        row["endpoint_family"] = "PrusaLinkApiV1"
        row["methods"] = ["GET", "POST"]
        row["status_behavior"] = ["source-backed status behavior"]
        row["auth_modes"] = ["digest", "api-key"]
        row["resource_limits"] = ["shared-send-buffers"]
        return row

    def write_wui_manifest(
        self,
        root: Path,
        maybe_rows: list[dict[str, object]] | None = None,
    ) -> None:
        rows = maybe_rows or [self.wui_row(root, row_id) for row_id in REQUIRED_WUI_ROW_IDS]
        self.write_file(
            root,
            "tools/bazel/manifests/phase9_wui_contracts.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "phase": PHASE,
                    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
                    "wui_contracts": rows,
                }
            ),
        )

    def transfer_row(self, root: Path, row_id: str) -> dict[str, object]:
        row = self.base_contract_row(
            root,
            row_id,
            "IFCE-02/IFCE-03",
            ["src/transfers/transfer.cpp", "src/transfers/download.cpp"],
        )
        row["transfer_source"] = ["ConnectCommand", "WuiUpload"]
        row["slot_state"] = ["Reserved", "Downloading"]
        row["range_behavior"] = ["Range"]
        row["encryption_behavior"] = ["AES-CTR"]
        row["media_behavior"] = ["single-active-transfer-slot"]
        row["recovery_behavior"] = ["backup metadata"]
        row["error_mapping"] = ["source-backed mapping"]
        if row_id == "transfer-media-race-non-local":
            row["evidence_class"] = "manual-hardware-required"
            row["proof_scope"] = "non-local"
        return row

    def write_transfer_manifest(
        self,
        root: Path,
        maybe_rows: list[dict[str, object]] | None = None,
    ) -> None:
        rows = maybe_rows or [self.transfer_row(root, row_id) for row_id in REQUIRED_TRANSFER_ROW_IDS]
        self.write_file(
            root,
            "tools/bazel/manifests/phase9_transfer_contracts.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "phase": PHASE,
                    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
                    "transfer_contracts": rows,
                }
            ),
        )

    def network_service_row(self, root: Path, row_id: str) -> dict[str, object]:
        row = self.base_contract_row(
            root,
            row_id,
            "IFCE-03",
            ["src/common/metric.cpp", "include/buddy/lwipopts.h"],
        )
        row["service_family"] = "Metrics"
        row["feature_gate"] = ["Feature::WebUi"]
        row["build_gate"] = ["BUDDY_ENABLE_WUI()"]
        row["transport"] = ["UDP"]
        row["config_keys"] = ["enable_metrics"]
        row["runtime_defaults"] = ["source-backed defaults"]
        return row

    def write_network_service_manifest(
        self,
        root: Path,
        maybe_rows: list[dict[str, object]] | None = None,
    ) -> None:
        rows = maybe_rows or [
            self.network_service_row(root, row_id) for row_id in REQUIRED_NETWORK_SERVICE_ROW_IDS
        ]
        self.write_file(
            root,
            "tools/bazel/manifests/phase9_network_service_contracts.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "phase": PHASE,
                    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
                    "network_service_contracts": rows,
                }
            ),
        )

    def concern_row(self, root: Path, row_id: str) -> dict[str, object]:
        sources_by_id = {
            "concern-phase9-custom-der-cert-read": ["src/connect/tls/tls.cpp"],
            "concern-phase9-weak-digest-modules": ["include/mbedtls/cipher_config_ece.h"],
            "concern-phase9-proxy-limitations": ["doc/proxy_support.md"],
            "concern-phase9-crash-dump-upload-boundary": [
                ".planning/phases/09-network-web-services-and-transfers/09-UI-SPEC.md"
            ],
        }
        source_paths = sources_by_id.get(row_id, [".planning/codebase/CONCERNS.md"])
        self.write_source_paths(root, source_paths)
        concern_prefix = "concern-phase9-"
        concern_id = row_id[len(concern_prefix) :] if row_id.startswith(concern_prefix) else row_id
        row: dict[str, object] = {
            "id": row_id,
            "concern_id": concern_id,
            "requirement_id": "IFCE-02",
            "reference_sources": source_paths,
            "disposition": "preserve-with-explicit-risk",
            "phase9_handling": [f"{row_id} remains explicitly dispositioned"],
            "evidence_class": "source-audit",
            "proof_scope": "local",
            "intentional_delta": "none",
            "regression_guard": ["future work must keep the disposition explicit"],
            "secret_handling": "none",
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        }
        if row_id == "concern-phase9-custom-der-cert-read":
            row["regression_guard"] = [
                "valid DER",
                "missing DER",
                "invalid DER",
                "/internal/connect/connect.der",
            ]
            row["secret_handling"] = "named-only-redacted"
        if row_id == "concern-phase9-weak-digest-modules":
            row["phase9_handling"] = ["MBEDTLS_SHA1_C", "MBEDTLS_MD5_C"]
        if row_id == "concern-phase9-proxy-limitations":
            row["phase9_handling"] = [
                "proxy-authentication-absent",
                "printer-to-proxy-leg-unencrypted",
                "proxy-active-only-when-connect_tls-true",
            ]
        if row_id == "concern-phase9-crash-dump-upload-boundary":
            row["regression_guard"] = ["consent", "redaction", "no raw dump byte payloads"]
            row["secret_handling"] = "named-only-redacted"
        if row_id == "concern-phase9-transfer-media-races":
            row["evidence_class"] = "manual-hardware-required"
            row["proof_scope"] = "non-local"
        return row

    def write_concern_manifest(
        self,
        root: Path,
        maybe_rows: list[dict[str, object]] | None = None,
    ) -> None:
        rows = maybe_rows or [self.concern_row(root, row_id) for row_id in REQUIRED_CONCERN_ROW_IDS]
        self.write_file(
            root,
            "tools/bazel/manifests/phase9_network_concern_dispositions.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "phase": PHASE,
                    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
                    "concerns": rows,
                }
            ),
        )

    def write_rust_api_surface(
        self,
        root: Path,
        network_text: str | None = None,
        lib_text: str | None = None,
    ) -> None:
        self.write_file(
            root,
            "rust/crates/domain/src/network.rs",
            network_text
            or "\n".join(
                [
                    *(f"pub struct {api_string};" for api_string in RUST_API_STRINGS),
                    'const COMMENT_ONLY: &str = "unsafe { unsafe fn";',
                    "// unsafe impl should be ignored in comments",
                ]
            ),
        )
        self.write_file(
            root,
            "rust/crates/domain/src/lib.rs",
            lib_text
            or (
                "#![forbid(unsafe_code)]\n"
                "pub mod network;\n"
                "pub use network::{"
                + ", ".join(RUST_API_STRINGS)
                + "};\n"
            ),
        )

    def write_facade_files(self, root: Path) -> None:
        self.write_file(
            root,
            "BUILD.bazel",
            "\n".join(
                [
                    'filegroup(name = "phase9_network_web_services_docs", srcs = [])',
                    'alias(name = "phase9_verify", actual = "//tools/bazel:phase9_verify")',
                    'alias(name = "phase9_verify_tests", actual = "//tools/bazel:phase9_verify_tests")',
                ]
            ),
        )
        self.write_file(
            root,
            "tools/bazel/BUILD.bazel",
            "\n".join(
                [
                    'shell_binary(name = "phase9_verify", src = "rust_workflow.sh", data = ["phase9_verify.py", "phase9_verify_test.py", "phase9_negative_fixtures.py", "fixtures/phase9_negative_network_cases.json", "phase9_connect_contracts.json", "phase9_wui_contracts.json", "phase9_transfer_contracts.json", "phase9_network_service_contracts.json", "phase9_network_concern_dispositions.json", "//:phase9_network_web_services_docs", "//:rust_workspace_sources"])',
                    'shell_binary(name = "phase9_verify_tests", src = "rust_workflow.sh", data = ["phase9_verify.py", "phase9_verify_test.py", "phase9_negative_fixtures.py", "phase9_negative_fixtures_test.py", "fixtures/phase9_negative_network_cases.json"])',
                ]
            ),
        )
        self.write_file(
            root,
            "tools/bazel/rust_workflow.sh",
            "\n".join(
                [
                    'case "$command_name" in',
                    "  phase9_verify)",
                    "    python3 tools/bazel/phase9_verify.py --all",
                    "    ;;",
                    "  phase9_verify_tests)",
                    "    python3 tools/bazel/phase9_verify_test.py",
                    "    python3 tools/bazel/phase9_negative_fixtures_test.py",
                    "    ;;",
                    "esac",
                    "",
                ]
            ),
        )
        self.write_file(
            root,
            "justfile",
            "phase9-verify:\n    bazel run //tools/bazel:phase9_verify_tests\n    bazel run //tools/bazel:phase9_verify\n",
        )

    def write_validation_contract(self, root: Path, extra_text: str = "") -> None:
        self.write_file(
            root,
            f"{PHASE_DIR}/09-VALIDATION.md",
            "\n".join(
                [
                    "---",
                    "status: complete",
                    "nyquist_compliant: true",
                    "wave_0_complete: true",
                    f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
                    "---",
                    "Quick run command",
                    "python3 tools/bazel/phase9_verify.py --quick",
                    "Full suite command",
                    "just phase9-verify",
                    "09-W0-01 Plan 01 green",
                    "09-W0-05 Plan 04 pending facade wiring",
                    "manual-hardware-required hardware-smoke simulator-flow remain non-local evidence",
                    extra_text,
                ]
            ),
        )

    def negative_case(self, root: Path, case_id: str) -> dict[str, object]:
        row: dict[str, object] = {
            "id": case_id,
            "requirement_id": "IFCE-02",
            "category": "connect-command",
            "reference_sources": ["src/connect/connect.cpp", "src/connect/planner.cpp"],
            "input_fixture": {"condition": "metadata-only"},
            "expected_outcome": {"classification": "source-backed"},
            "evidence_class": "source-audit",
            "proof_scope": "local",
            "secret_handling": "named-only-redacted",
            "intentional_delta": "none",
            "runnable_check": "metadata-schema-only",
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        }
        if case_id == "custom-cert-valid-der-intentional-delta":
            row.update(
                {
                    "category": "custom-certificate",
                    "reference_sources": ["src/connect/tls/tls.cpp"],
                    "input_fixture": {
                        "custom_certificate_path": "/internal/connect/connect.der",
                        "certificate_material": "omitted",
                    },
                    "expected_outcome": {"classification": "intentional-delta-fixture"},
                    "evidence_class": "manual-hardware-required",
                    "proof_scope": "non-local",
                    "intentional_delta": "approved",
                }
            )
        elif case_id == "custom-cert-missing-der-preserved-defect":
            row.update(
                {
                    "category": "custom-certificate",
                    "reference_sources": ["src/connect/tls/tls.cpp"],
                    "input_fixture": {
                        "custom_certificate_path": "/internal/connect/connect.der",
                        "certificate_material": "omitted",
                    },
                    "expected_outcome": {
                        "classification": "preserved-defect",
                        "preserved_defect": True,
                    },
                }
            )
        elif case_id == "custom-cert-invalid-der-rejected":
            row.update(
                {
                    "category": "custom-certificate",
                    "reference_sources": ["src/connect/tls/tls.cpp"],
                    "input_fixture": {
                        "custom_certificate_path": "/internal/connect/connect.der",
                        "certificate_material": "omitted",
                    },
                    "expected_outcome": {
                        "classification": "rejected-invalid-der",
                        "rejected": True,
                    },
                }
            )
        elif case_id == "invalid-certificate-chain-rejected":
            row.update(
                {
                    "category": "tls-certificate-chain",
                    "reference_sources": ["src/connect/tls/tls.cpp"],
                    "input_fixture": {
                        "tls_policy": "MBEDTLS_SSL_VERIFY_REQUIRED",
                        "certificate_material": "omitted",
                    },
                    "expected_outcome": {"classification": "rejected-invalid-chain", "rejected": True},
                    "evidence_class": "manual-hardware-required",
                    "proof_scope": "non-local",
                }
            )
        elif case_id == "weak-signature-sha1-md5-dispositioned":
            row.update(
                {
                    "category": "tls-weak-signature",
                    "reference_sources": ["include/mbedtls/cipher_config_ece.h"],
                    "input_fixture": {
                        "retained_modules": ["MBEDTLS_SHA1_C", "MBEDTLS_MD5_C"],
                        "runtime_policy": "not-accepted-runtime-policy",
                    },
                    "expected_outcome": {"classification": "preserve-with-explicit-risk"},
                    "secret_handling": "none",
                }
            )
        elif case_id == "duplicate-connect-command-rejected":
            row["input_fixture"] = {"condition": "duplicate command id"}
            row["expected_outcome"] = {"event": "Rejected"}
        elif case_id == "large-websocket-command-rejected":
            row["input_fixture"] = {"condition": "oversized command frame"}
            row["expected_outcome"] = {"state": "BrokenCommand"}
        elif case_id == "proxy-tls-only-no-auth-plain-leg-preserved":
            row.update(
                {
                    "category": "connect-proxy",
                    "reference_sources": ["doc/proxy_support.md", "src/common/http/proxy.cpp"],
                    "input_fixture": {
                        "proxy_limitations": [
                            "proxy-authentication-absent",
                            "printer-to-proxy-leg-unencrypted",
                            "proxy-active-only-when-connect_tls-true",
                        ]
                    },
                    "expected_outcome": {"classification": "preserve-current-limitations"},
                }
            )
        elif case_id == "stalled-network-transfer-timeout-classified":
            row.update(
                {
                    "requirement_id": "IFCE-02/IFCE-03",
                    "category": "transfer-network-timeout",
                    "reference_sources": ["src/transfers/download.cpp", "src/transfers/transfer.cpp"],
                    "input_fixture": {"condition": "stalled network transfer"},
                    "expected_outcome": {
                        "classification": "timeout-or-recovery",
                        "recovery_behavior": "non-local long-running proof required",
                    },
                    "evidence_class": "manual-hardware-required",
                    "proof_scope": "non-local",
                    "secret_handling": "none",
                }
            )
        self.write_source_paths(root, row["reference_sources"])
        return row

    def write_negative_fixture_surface(self, root: Path) -> None:
        self.write_file(
            root,
            "tools/bazel/fixtures/phase9_negative_network_cases.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "phase": PHASE,
                    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
                    "negative_cases": [
                        self.negative_case(root, case_id) for case_id in REQUIRED_NEGATIVE_CASE_IDS
                    ],
                }
            ),
        )

    def write_phase9_quick_surface(self, root: Path) -> None:
        self.write_connect_manifest(root)
        self.write_wui_manifest(root)
        self.write_transfer_manifest(root)
        self.write_network_service_manifest(root)
        self.write_concern_manifest(root)
        self.write_negative_fixture_surface(root)
        self.write_rust_api_surface(root)
        self.write_facade_files(root)
        self.write_validation_contract(root)

    def test_requires_all_phase9_manifests(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            (root / "tools/bazel/manifests/phase9_wui_contracts.json").unlink()

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase9_wui_contracts.json", result.stdout)

    def test_requires_connect_tls_proxy_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.connect_row(root, row_id)
                for row_id in REQUIRED_CONNECT_ROW_IDS
                if row_id not in {
                    "connect-registration-token-fingerprint",
                    "connect-tls-required-verification-policy",
                    "connect-proxy-minimal-limitations",
                }
            ]
            self.write_connect_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("connect-registration-token-fingerprint", result.stdout)
        self.assertIn("connect-tls-required-verification-policy", result.stdout)
        self.assertIn("connect-proxy-minimal-limitations", result.stdout)

    def test_requires_wui_auth_and_resource_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.wui_row(root, row_id)
                for row_id in REQUIRED_WUI_ROW_IDS
                if row_id not in {
                    "wui-server-resource-model",
                    "wui-digest-auth-nonce-stale",
                    "wui-api-key-auth",
                }
            ]
            self.write_wui_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("wui-server-resource-model", result.stdout)
        self.assertIn("wui-digest-auth-nonce-stale", result.stdout)
        self.assertIn("wui-api-key-auth", result.stdout)

    def test_requires_transfer_single_slot_and_media_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.transfer_row(root, row_id)
                for row_id in REQUIRED_TRANSFER_ROW_IDS
                if row_id not in {
                    "transfer-single-active-slot",
                    "transfer-encrypted-aes-ctr-payload",
                    "transfer-media-race-non-local",
                }
            ]
            self.write_transfer_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("transfer-single-active-slot", result.stdout)
        self.assertIn("transfer-encrypted-aes-ctr-payload", result.stdout)
        self.assertIn("transfer-media-race-non-local", result.stdout)

    def test_requires_network_service_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.network_service_row(root, row_id)
                for row_id in REQUIRED_NETWORK_SERVICE_ROW_IDS
                if row_id not in {
                    "metrics-line-protocol-throttling",
                    "syslog-udp-destination",
                    "network-feature-gates-wui-connect",
                }
            ]
            self.write_network_service_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metrics-line-protocol-throttling", result.stdout)
        self.assertIn("syslog-udp-destination", result.stdout)
        self.assertIn("network-feature-gates-wui-connect", result.stdout)

    def test_requires_phase9_concern_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [
                self.concern_row(root, row_id)
                for row_id in REQUIRED_CONCERN_ROW_IDS
                if row_id not in {
                    "concern-phase9-custom-der-cert-read",
                    "concern-phase9-weak-digest-modules",
                    "concern-phase9-proxy-limitations",
                    "concern-phase9-crash-dump-upload-boundary",
                }
            ]
            self.write_concern_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("concern-phase9-custom-der-cert-read", result.stdout)
        self.assertIn("concern-phase9-weak-digest-modules", result.stdout)
        self.assertIn("concern-phase9-proxy-limitations", result.stdout)
        self.assertIn("concern-phase9-crash-dump-upload-boundary", result.stdout)

    def test_rejects_secret_value_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_validation_contract(root, extra_text=" ".join(FORBIDDEN_MARKERS))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token_value", result.stdout)
        self.assertIn("BEGIN PRIVATE KEY", result.stdout)
        self.assertIn("raw_crash_dump", result.stdout)

    def test_rejects_non_local_evidence_overclaims(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            rows = [self.transfer_row(root, row_id) for row_id in REQUIRED_TRANSFER_ROW_IDS]
            for row in rows:
                if row["id"] == "transfer-media-race-non-local":
                    row["proof_scope"] = "local"
            self.write_transfer_manifest(root, maybe_rows=rows)
            self.write_validation_contract(root, extra_text=" ".join(OVERCLAIM_STRINGS))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("transfer-media-race-non-local", result.stdout)
        self.assertIn("manual-hardware-required", result.stdout)
        self.assertIn("cloud verified locally", result.stdout)
        self.assertIn("cutover evidence complete", result.stdout)

    def test_requires_network_rust_api_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_rust_api_surface(
                root,
                network_text="pub enum NetworkEvidenceClass {}\n",
                lib_text="#![forbid(unsafe_code)]\npub mod network;\npub use network::NetworkEvidenceClass;\n",
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for needle in [
            "NetworkParityRowId",
            "SecretHandling",
            "ConnectCommandState",
            "ProxyMode",
            "WuiAuthMode",
            "TransferRange",
            "EncryptedPayloadMetadata",
            "NetworkServiceContract",
            "NetworkParityContract",
        ]:
            self.assertIn(needle, result.stdout)

    def test_rust_unsafe_scan_does_not_swallow_lifetimes(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            network_text = "\n".join(
                [
                    *(f"pub struct {api_string};" for api_string in RUST_API_STRINGS),
                    "pub fn lifetime_bound<'a>(value: &'a str) -> &'a str {",
                    "    unsafe { value }",
                    "}",
                ]
            )
            self.write_rust_api_surface(root, network_text=network_text)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe block", result.stdout)

    def test_requires_bazel_and_just_wiring(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_file(root, "BUILD.bazel", 'alias(name = "phase9_verify")\n')
            self.write_file(root, "tools/bazel/BUILD.bazel", 'shell_binary(name = "phase9_verify")\n')
            self.write_file(root, "tools/bazel/rust_workflow.sh", 'case "$command_name" in esac\n')
            self.write_file(root, "justfile", "phase9-verify:\n    bazel run //tools/bazel:phase9_verify\n")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase9_verify_tests", result.stdout)
        self.assertIn("rust_workflow.sh", result.stdout)
        self.assertIn("justfile", result.stdout)

    def test_just_wiring_rejects_verify_tests_prefix_only(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_file(
                root,
                "justfile",
                "phase9-verify:\n    bazel run //tools/bazel:phase9_verify_tests\n",
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bazel run //tools/bazel:phase9_verify", result.stdout)
        self.assertIn("justfile must run phase9_verify_tests before phase9_verify", result.stdout)

    def test_requires_validation_lifecycle_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)
            self.write_file(
                root,
                f"{PHASE_DIR}/09-VALIDATION.md",
                "\n".join(
                    [
                        "---",
                        "status: complete",
                        "wave_0_complete: true",
                        "---",
                        "Quick run command",
                        "python3 tools/bazel/phase9_verify.py --quick",
                    ]
                ),
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE_LIFECYCLE_ID, result.stdout)
        self.assertIn("nyquist_compliant: true", result.stdout)

    def test_requires_negative_fixture_runner_wiring(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase9_quick_surface(root)

            # Act
            focused_result = self.run_verifier(["--negative-fixtures-only"], maybe_root=root)

            # Assert
            self.assertEqual(focused_result.returncode, 0, focused_result.stdout)

            # Arrange
            (root / "tools/bazel/fixtures/phase9_negative_network_cases.json").unlink()

            # Act
            missing_cases_result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertNotEqual(missing_cases_result.returncode, 0)
            self.assertIn("phase9_negative_network_cases.json", missing_cases_result.stdout)

            # Arrange
            self.write_negative_fixture_surface(root)
            (root / "tools/bazel/phase9_negative_fixtures.py").unlink()

            # Act
            missing_runner_result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertNotEqual(missing_runner_result.returncode, 0)
            self.assertIn("phase9_negative_fixtures.py", missing_runner_result.stdout)


if __name__ == "__main__":
    unittest.main()
