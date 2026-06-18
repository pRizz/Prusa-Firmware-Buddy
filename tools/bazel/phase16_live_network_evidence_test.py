#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase16_live_network_evidence.py"
CONTRACT = "tools/bazel/manifests/phase16_live_network_evidence_contract.json"
SOURCE_REF_FILES = [
    "tools/bazel/manifests/phase9_connect_contracts.json",
    "tools/bazel/manifests/phase9_wui_contracts.json",
    "tools/bazel/manifests/phase9_network_service_contracts.json",
    "tools/bazel/manifests/phase9_transfer_contracts.json",
    "tools/bazel/manifests/phase9_network_concern_dispositions.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json",
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json",
]
DOC_REF_FILES = [
    "doc/proxy_support.md",
    "doc/metrics.md",
]


class Phase16LiveNetworkEvidenceTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase16_live_network_evidence.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        shutil.copy2(VERIFIER, root / "tools/bazel/phase16_live_network_evidence.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_file(self, root: Path, path: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, full_path)

    def read_contract(self, root: Path) -> dict[str, object]:
        return json.loads((root / CONTRACT).read_text(encoding="utf-8"))

    def write_contract(self, root: Path, contract: dict[str, object]) -> None:
        self.write_file(root, CONTRACT, json.dumps(contract, indent=2, sort_keys=True) + "\n")

    def copy_source_ref_inputs(self, root: Path) -> None:
        for path in SOURCE_REF_FILES + DOC_REF_FILES:
            self.copy_file(root, path)

    def copy_complete_surface(self, root: Path) -> None:
        self.copy_file(root, CONTRACT)
        self.copy_source_ref_inputs(root)

    def write_operator_evidence(
        self,
        root: Path,
        rows: list[dict[str, object]],
        path: str = "operator-evidence.json",
    ) -> str:
        self.write_file(root, path, json.dumps({"evidence_rows": rows}, indent=2, sort_keys=True) + "\n")
        return path

    def complete_operator_row(
        self,
        scenario_id: str = "live-connect-registration-token-fingerprint",
        result: str = "passed",
        artifact_refs: list[str] | None = None,
    ) -> dict[str, object]:
        maybe_artifact_refs = artifact_refs or [
            f"build/ci-evidence/phase16/logs/{scenario_id}.log",
            f"external://phase16/{scenario_id}",
        ]
        return {
            "artifact_refs": maybe_artifact_refs,
            "device": "network-bench-printer-01",
            "evidence_type": "controlled-service-observation",
            "firmware_build": "phase16-test-build",
            "mode": "live-or-controlled-service",
            "operator": "phase16-test-operator",
            "redaction_summary": "Credential and payload fields were replaced by redacted metadata classes.",
            "residual_risk": "Coverage is limited to the named controlled-service fixture.",
            "result": result,
            "scenario_id": scenario_id,
            "service_surface": "connect-registration",
            "timestamp": "2026-06-18T02:00:00Z",
        }

    def write_wiring(
        self,
        root: Path,
        maybe_tools_build: str | None = None,
        maybe_root_build: str | None = None,
        maybe_workflow: str | None = None,
        maybe_justfile: str | None = None,
    ) -> None:
        manifest_srcs = "\n".join(
            f'        "{Path(path).relative_to("tools/bazel").as_posix()}",'
            for path in SOURCE_REF_FILES
        )
        tools_build = maybe_tools_build or f"""filegroup(
    name = "phase16_source_ref_manifests",
    srcs = [
{manifest_srcs}
    ],
)

shell_binary(
    name = "phase16_verify",
    src = "rust_workflow.sh",
    data = [
        "phase16_live_network_evidence.py",
        "manifests/phase16_live_network_evidence_contract.json",
        ":phase16_source_ref_manifests",
        "//:phase16_live_network_evidence_docs",
        "//:phase11_cutover_evidence_docs",
    ],
)

shell_binary(
    name = "phase16_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase16_live_network_evidence.py",
        "phase16_live_network_evidence_test.py",
        "manifests/phase16_live_network_evidence_contract.json",
        ":phase16_source_ref_manifests",
    ],
)
"""
        root_build = maybe_root_build or """filegroup(
    name = "phase16_live_network_evidence_docs",
    srcs = [
        ".planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md",
        ".planning/phases/16-live-network-and-transfer-qualification/16-RESEARCH.md",
        ".planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md",
        ".planning/phases/16-live-network-and-transfer-qualification/16-01-PLAN.md",
    ],
)

alias(
    name = "phase16_verify",
    actual = "//tools/bazel:phase16_verify",
)

alias(
    name = "phase16_verify_tests",
    actual = "//tools/bazel:phase16_verify_tests",
)
"""
        workflow = maybe_workflow or """case "$command_name" in
  phase16_verify)
    python3 tools/bazel/phase16_live_network_evidence.py --wiring-only
    python3 tools/bazel/phase16_live_network_evidence.py --quick
    ;;
  phase16_verify_tests)
    python3 tools/bazel/phase16_live_network_evidence_test.py
    ;;
esac
"""
        justfile = maybe_justfile or """phase16-verify:
    bazel run //tools/bazel:phase16_verify_tests
    bazel run //tools/bazel:phase16_verify
"""
        self.write_file(root, "tools/bazel/BUILD.bazel", tools_build)
        self.write_file(root, "BUILD.bazel", root_build)
        self.write_file(root, "tools/bazel/rust_workflow.sh", workflow)
        self.write_file(root, "justfile", justfile)

    def test_contract_accepts_complete_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_requires_all_live_rows(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"] = [
                scenario
                for scenario in contract["scenarios"]
                if scenario["id"] != "live-connect-registration-token-fingerprint"
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("live-connect-registration-token-fingerprint", result.stdout)

    def test_contract_requires_live_requirements(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            for scenario in contract["scenarios"]:
                scenario["requirement_ids"] = [
                    requirement_id
                    for requirement_id in scenario["requirement_ids"]
                    if requirement_id != "LIVE-02"
                ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("LIVE-02", result.stdout)

    def test_contract_requires_surface_coverage(self) -> None:
        cases = [
            "connect-registration",
            "connect-telemetry-events",
            "connect-command-channel",
            "connect-proxy",
            "prusalink-api-v1",
            "wui-digest-auth",
            "wui-api-key-auth",
            "sntp-client",
            "mdns-responder",
            "syslog-and-metrics",
            "wui-upload-transfer",
            "connect-tls-policy",
            "wui-negative-protocol",
            "connect-long-transfer",
            "crash-dump-upload",
        ]
        for surface in cases:
            with self.subTest(surface=surface):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    for scenario in contract["scenarios"]:
                        if scenario["service_surface"] == surface:
                            scenario["service_surface"] = f"missing-{surface}"
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(surface, result.stdout)

    def test_contract_rejects_bad_source_ref(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["source_contract_refs"][0] = "../escape.json#missing-row"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source ref", result.stdout)
        self.assertIn("escape", result.stdout)

    def test_contract_rejects_passed_default_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["default_status"] = "passed"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("passed", result.stdout)

    def test_contract_requires_redaction_and_residual_gates(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["scenarios"][0]["redaction_required"] = False
            contract["scenarios"][0]["credential_boundary"] = ""
            contract["scenarios"][0]["residual_non_live_gates"] = []
            contract["scenarios"][0]["unsupported_claims"] = []
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("redaction_required", result.stdout)
        self.assertIn("credential_boundary", result.stdout)
        self.assertIn("residual_non_live_gates", result.stdout)
        self.assertIn("unsupported_claims", result.stdout)

    def test_quick_writes_phase16_artifacts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for path in [
                "build/ci-evidence/phase16/run-manifest.json",
                "build/ci-evidence/phase16/normalized-scenario-results.json",
                "build/ci-evidence/phase16/redacted-network-summary.json",
                "build/ci-evidence/phase16/source-contract-snapshots/phase16_live_network_evidence_contract.json",
                "build/ci-evidence/phase16/operator-evidence-input.json",
                "build/ci-evidence/phase16/logs/live-connect-registration-token-fingerprint.log",
            ]:
                self.assertTrue((root / path).exists(), path)

    def test_quick_keeps_live_rows_pending(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)
            manifest = json.loads(
                (root / "build/ci-evidence/phase16/run-manifest.json").read_text(encoding="utf-8")
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(manifest["live_inputs_supplied"])
        live_statuses = {
            row["status"]
            for row in manifest["scenarios"]
            if row["proof_scope"] == "live-service-observation"
        }
        source_statuses = {
            row["status"]
            for row in manifest["scenarios"]
            if row["proof_scope"] == "source-contract"
        }
        self.assertEqual(live_statuses, {"pending-live-input"})
        self.assertEqual(source_statuses, {"source-contract-passed"})

    def test_operator_evidence_accepts_complete_pass(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            operator_path = self.write_operator_evidence(root, [self.complete_operator_row()])

            # Act
            result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)
            normalized = json.loads(
                (root / "build/ci-evidence/phase16/normalized-scenario-results.json").read_text(
                    encoding="utf-8"
                )
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = {row["id"]: row for row in normalized["scenarios"]}
        scenario = rows["live-connect-registration-token-fingerprint"]
        self.assertEqual(scenario["status"], "passed")
        self.assertTrue(scenario["operator_metadata_present"])
        self.assertEqual(scenario["operator"], "phase16-test-operator")

    def test_operator_evidence_accepts_top_level_list(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            operator_path = "operator-evidence-list.json"
            self.write_file(
                root,
                operator_path,
                json.dumps([self.complete_operator_row()], indent=2, sort_keys=True) + "\n",
            )

            # Act
            result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)
            normalized = json.loads(
                (root / "build/ci-evidence/phase16/normalized-scenario-results.json").read_text(
                    encoding="utf-8"
                )
            )

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = {row["id"]: row for row in normalized["scenarios"]}
        self.assertEqual(rows["live-connect-registration-token-fingerprint"]["status"], "passed")

    def test_operator_evidence_rejects_missing_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            row = self.complete_operator_row()
            del row["operator"]
            operator_path = self.write_operator_evidence(root, [row])

            # Act
            result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("operator", result.stdout)

    def test_operator_evidence_rejects_unknown_scenario_or_status(self) -> None:
        cases = [
            (self.complete_operator_row(scenario_id="missing-scenario"), "missing-scenario"),
            (self.complete_operator_row(result="waived"), "waived"),
        ]
        for row, expected in cases:
            with self.subTest(expected=expected):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    operator_path = self.write_operator_evidence(root, [row])

                    # Act
                    result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_operator_evidence_rejects_artifact_path_traversal(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            row = self.complete_operator_row(artifact_refs=["../leak.log"])
            operator_path = self.write_operator_evidence(root, [row])

            # Act
            result = self.run_verifier(["--quick", "--operator-evidence", operator_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)

    def test_security_rejects_secret_markers(self) -> None:
        cases = [
            "-----BEGIN PRIVATE KEY-----",
            "-----BEGIN CERTIFICATE-----",
            "certificate_pem",
            "certificate_bytes",
            "private_key",
            "signing_key",
            "token_value",
            "connect_token",
            "Connect token",
            "registration_code",
            "registration code",
            "Fingerprint: 123456",
            "fingerprint_value",
            "wifi_password",
            "Wi-Fi credential",
            "PrusaLink password",
            "api_key",
            "x-api-key",
            "API key",
            "Authorization: Bearer redacted",
            "Cookie: session=redacted",
            "Set-Cookie: session=redacted",
            "raw_http_log",
            "raw_tls_log",
            "tls_keylog",
            "SSLKEYLOGFILE",
            "raw_crash_dump",
            "raw_ram_dump",
            "memory_dump",
            "raw_production_payload",
            "firmware_payload",
            "bbf_payload",
            "dfu_payload",
            ".bin payload",
            ".bbf payload",
            ".dfu payload",
        ]
        for marker in cases:
            with self.subTest(marker=marker):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.write_file(root, "build/ci-evidence/phase16/leak.json", marker + "\n")

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                expected_marker = marker.split()[0] if ":" in marker else marker
                self.assertIn(expected_marker, result.stdout)

    def test_security_rejects_overclaim_wording(self) -> None:
        cases = [
            "live service passed locally",
            "live network verified locally",
            "production Connect validated",
            "production PrusaLink validated",
            "tls proof complete without operator evidence",
            "proxy fully supported",
            "proxy authentication supported",
            "crash dump upload safe",
            "raw crash dump retained",
            "final cutover complete",
            "cutover complete",
            "release readiness proven",
            "release-candidate passed locally",
            "signing proof complete",
            "retained-code accepted by maintainer",
            "reference demotion approved",
            "reference removal complete",
        ]
        for phrase in cases:
            with self.subTest(phrase=phrase):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    baseline = self.run_verifier(["--security-only"], maybe_root=root)
                    self.write_file(root, "build/ci-evidence/phase16/overclaim.json", phrase + "\n")

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertEqual(baseline.returncode, 0, baseline.stdout)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(phrase.lower(), result.stdout.lower())

    def test_output_dir_rejects_traversal(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick", "--output-dir", "../escape"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot traverse", result.stdout)

    def test_wiring_accepts_phase16_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_rejects_missing_bazel_label(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(encoding="utf-8").replace(
                'name = "phase16_verify_tests"',
                'name = "phase16_missing_tests"',
            )
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase16_verify_tests", result.stdout)

    def test_wiring_rejects_missing_source_ref_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(encoding="utf-8").replace(
                '        "manifests/phase11_retained_code_justifications.json",\n',
                "",
            )
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase11_retained_code_justifications.json", result.stdout)

    def test_wiring_rejects_verifier_before_tests(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(
                root,
                maybe_justfile="""phase16-verify:
    bazel run //tools/bazel:phase16_verify
    bazel run //tools/bazel:phase16_verify_tests
""",
            )

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tests before verifier", result.stdout)


if __name__ == "__main__":
    unittest.main()
