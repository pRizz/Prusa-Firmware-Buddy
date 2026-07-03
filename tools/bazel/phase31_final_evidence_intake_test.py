#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase31_final_evidence_intake.py"
CONTRACT = "tools/bazel/manifests/phase31_final_evidence_intake_contract.json"
SOURCE_CONTRACTS = [
    "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json",
    "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
    "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json",
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json",
]
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase31"
SUBMITTER = "external://identity/phase31-maintainer"
WIRING_FILES = ["BUILD.bazel", "tools/bazel/BUILD.bazel", "tools/bazel/rust_workflow.sh", "justfile"]


class Phase31FinalEvidenceIntakeTest(unittest.TestCase):
    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for path in [VERIFIER, ROOT / CONTRACT, *[ROOT / source_contract for source_contract in SOURCE_CONTRACTS]]:
            destination = root / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        self.write_source_validator_stubs(root)
        return temp_dir, root

    def run_verifier(self, args: list[str], maybe_root: Path | None = None) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase31_final_evidence_intake.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def read_json(self, root: Path, path: str) -> dict[str, object]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    def write_json(self, root: Path, path: str, data: dict[str, object]) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def write_file(self, root: Path, path: str, text: str) -> str:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")
        return path

    def write_source_validator_stubs(self, root: Path) -> None:
        self.write_file(
            root,
            "tools/bazel/phase23_simulator_evidence_execution.py",
            self.source_validator_stub(
                phase="23-simulator-evidence-execution",
                lifecycle="23-2026-06-23T18-45-38",
                manifest_name="simulator-result-manifest.json",
                row_name="upstream-simulator-result-row.json",
                real_flag="real_simulator_evidence_supplied",
                criterion_id="final-simulator-evidence",
                evidence_family="simulator",
                requirement_id="EVID-01",
                raw_flag="--evidence-input",
            ),
        )
        self.write_file(
            root,
            "tools/bazel/phase24_hardware_media_safety_evidence_execution.py",
            self.source_validator_stub(
                phase="24-hardware-media-and-safety-evidence-execution",
                lifecycle="24-2026-06-23T19-52-32",
                manifest_name="hardware-media-safety-result-manifest.json",
                row_name="upstream-hardware-media-safety-result-row.json",
                real_flag="real_hardware_evidence_supplied",
                criterion_id="final-hardware-safety-media-evidence",
                evidence_family="hardware",
                requirement_id="EVID-02",
                raw_flag="--evidence-input",
            ),
        )
        self.write_file(
            root,
            "tools/bazel/phase25_live_service_evidence_execution.py",
            self.source_validator_stub(
                phase="25-live-service-evidence-execution",
                lifecycle="25-2026-06-23T21-12-42",
                manifest_name="live-service-result-manifest.json",
                row_name="upstream-live-service-result-row.json",
                real_flag="real_live_service_evidence_supplied",
                criterion_id="final-live-service-evidence",
                evidence_family="live-service",
                requirement_id="EVID-03",
                raw_flag="--evidence-input",
            ),
        )
        self.write_file(root, "tools/bazel/phase26_release_signing_upstream_evidence.py", self.release_validator_stub())

    def source_validator_stub(
        self,
        *,
        phase: str,
        lifecycle: str,
        manifest_name: str,
        row_name: str,
        real_flag: str,
        criterion_id: str,
        evidence_family: str,
        requirement_id: str,
        raw_flag: str,
    ) -> str:
        return textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import argparse
            import json
            import sys
            from pathlib import Path

            PHASE = {phase!r}
            LIFECYCLE = {lifecycle!r}
            MANIFEST_NAME = {manifest_name!r}
            ROW_NAME = {row_name!r}
            REAL_FLAG = {real_flag!r}
            CRITERION_ID = {criterion_id!r}
            EVIDENCE_FAMILY = {evidence_family!r}
            REQUIREMENT_ID = {requirement_id!r}
            RAW_FLAG = {raw_flag!r}

            parser = argparse.ArgumentParser()
            parser.add_argument(RAW_FLAG)
            parser.add_argument("--output-dir", required=True)
            args = parser.parse_args()
            root = Path.cwd()
            output_dir = Path(args.output_dir)
            (root / output_dir).mkdir(parents=True, exist_ok=True)
            log_path = root / "build/source-validator-invocations.jsonl"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({{"phase": PHASE, "argv": sys.argv[1:]}}) + "\\n")
            manifest = {{
                "artifact_name": PHASE,
                "command_mode": "evidence-input",
                "generated_at": "2026-07-03T02:00:00Z",
                "output_root": output_dir.as_posix(),
                "phase": PHASE,
                "phase_lifecycle_id": LIFECYCLE,
                REAL_FLAG: True,
                "status": "passed",
            }}
            row = {{
                "artifact_refs": [
                    (output_dir / "normalized-results.json").as_posix(),
                    (output_dir / "redacted-summary.json").as_posix(),
                ],
                "criterion_id": CRITERION_ID,
                "evidence_family": EVIDENCE_FAMILY,
                "manifest_ref": (output_dir / MANIFEST_NAME).as_posix(),
                "phase": PHASE,
                "phase_lifecycle_id": LIFECYCLE,
                REAL_FLAG: True,
                "redaction_status": "passed",
                "requirement_ids": [REQUIREMENT_ID],
                "source_ref_status": "passed",
                "status": "passed",
            }}
            (root / output_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
            (root / output_dir / ROW_NAME).write_text(json.dumps(row, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
            """
        )

    def release_validator_stub(self) -> str:
        return textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import argparse
            import json
            import sys
            from pathlib import Path

            parser = argparse.ArgumentParser()
            parser.add_argument("--quick", action="store_true")
            parser.add_argument("--release-input")
            parser.add_argument("--phase23-simulator-row")
            parser.add_argument("--phase24-hardware-media-safety-row")
            parser.add_argument("--phase25-live-service-row")
            parser.add_argument("--output-dir", required=True)
            args = parser.parse_args()
            if not args.quick or not args.release_input:
                raise SystemExit(2)
            root = Path.cwd()
            output_dir = Path(args.output_dir)
            (root / output_dir).mkdir(parents=True, exist_ok=True)
            log_path = root / "build/source-validator-invocations.jsonl"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({"phase": "26-release-signing-and-upstream-result-evidence", "argv": sys.argv[1:]}) + "\\n")
            manifest = {
                "artifact_name": "phase26-release-signing-upstream-evidence",
                "generated_at_utc": "2026-07-03T02:00:00Z",
                "output_root": output_dir.as_posix(),
                "phase": "26-release-signing-and-upstream-result-evidence",
                "phase_lifecycle_id": "26-2026-06-24T13-36-46",
                "real_release_evidence_supplied": True,
                "release_status": "passed",
            }
            rows = [
                {
                    "artifact_refs": [(output_dir / "normalized-release-evidence-summary.json").as_posix()],
                    "criterion_id": "final-release-artifact-signing-evidence",
                    "evidence_family": "release",
                    "evidence_refs": ["external://phase26/release-run"],
                    "exception_status": "none",
                    "failure_reason": "",
                    "generated_at_utc": "2026-07-03T02:00:00Z",
                    "maintainer_state": "pending",
                    "owning_phase": "26-release-signing-and-upstream-result-evidence",
                    "redaction_status": "passed",
                    "requirement_ids": ["EVID-04"],
                    "source_lifecycle_id": "26-2026-06-24T13-36-46",
                    "source_lifecycle_status": "current",
                    "source_ref_status": "passed",
                    "source_requirement_ids": ["EVID-04"],
                    "status": "passed",
                }
            ]
            artifact_summary = {
                "artifact_refs": ["external://phase26/artifacts/release-run.json"],
                "digest_refs": [
                    {
                        "artifact_ref": "external://phase26/artifacts/firmware.bbf",
                        "sha256": "a" * 64,
                    }
                ],
                "generated_at_utc": "2026-07-03T02:00:00Z",
                "phase": "26-release-signing-and-upstream-result-evidence",
                "real_release_evidence_supplied": True,
            }
            (root / output_dir / "release-upstream-run-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
            (root / output_dir / "upstream-result-row-table.json").write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
            (root / output_dir / "artifact-reference-summary.json").write_text(json.dumps(artifact_summary, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
            """
        )

    def write_retained_stream(
        self,
        root: Path,
        *,
        output_dir: str = "build/ci-evidence/phase23",
        lifecycle: str = "23-2026-06-23T18-45-38",
        real: bool = True,
        artifact_ref: str = "external://phase23/logs/run.json",
        source_ref_status: str = "passed",
        redaction_status: str = "passed",
        extra_manifest: dict[str, object] | None = None,
    ) -> None:
        manifest = {
            "artifact_name": "phase23-simulator-evidence-execution",
            "command_mode": "evidence-input",
            "generated_at": "2026-07-03T02:00:00Z",
            "output_root": output_dir,
            "phase": "23-simulator-evidence-execution",
            "phase_lifecycle_id": lifecycle,
            "real_simulator_evidence_supplied": real,
            "status": "passed" if real else "blocked",
        }
        if extra_manifest is not None:
            manifest.update(extra_manifest)
        row = {
            "artifact_refs": [artifact_ref],
            "criterion_id": "final-simulator-evidence",
            "evidence_family": "simulator",
            "manifest_ref": f"{output_dir}/simulator-result-manifest.json",
            "phase": "23-simulator-evidence-execution",
            "phase_lifecycle_id": lifecycle,
            "real_simulator_evidence_supplied": real,
            "redaction_status": redaction_status,
            "requirement_ids": ["EVID-01"],
            "source_ref_status": source_ref_status,
            "status": "passed" if real else "blocked",
        }
        self.write_json(root, f"{output_dir}/simulator-result-manifest.json", manifest)
        self.write_json(root, f"{output_dir}/upstream-simulator-result-row.json", row)

    def write_phase31_wiring(
        self,
        root: Path,
        *,
        maybe_justfile: str | None = None,
        maybe_workflow: str | None = None,
    ) -> None:
        root_build = """filegroup(
    name = "phase31_final_evidence_intake_docs",
    srcs = [
        ".planning/phases/31-final-evidence-intake/31-CONTEXT.md",
        ".planning/phases/31-final-evidence-intake/31-RESEARCH.md",
        ".planning/phases/31-final-evidence-intake/31-VALIDATION.md",
        ".planning/phases/31-final-evidence-intake/31-01-PLAN.md",
    ],
)

alias(
    name = "phase31_verify",
    actual = "//tools/bazel:phase31_verify",
)

alias(
    name = "phase31_verify_tests",
    actual = "//tools/bazel:phase31_verify_tests",
)
"""
        tools_build = """filegroup(
    name = "phase31_source_ref_manifests",
    srcs = [
        "manifests/phase23_simulator_evidence_execution_contract.json",
        "manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
        "manifests/phase25_live_service_evidence_execution_contract.json",
        "manifests/phase26_release_signing_upstream_evidence_contract.json",
        "manifests/phase31_final_evidence_intake_contract.json",
    ],
)

shell_binary(
    name = "phase31_verify",
    src = "rust_workflow.sh",
    data = [
        "phase31_final_evidence_intake.py",
        "manifests/phase31_final_evidence_intake_contract.json",
        ":phase31_source_ref_manifests",
        "//:phase31_final_evidence_intake_docs",
    ],
)

shell_binary(
    name = "phase31_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase31_final_evidence_intake.py",
        "phase31_final_evidence_intake_test.py",
        "manifests/phase31_final_evidence_intake_contract.json",
        ":phase31_source_ref_manifests",
    ],
)
"""
        workflow = maybe_workflow if maybe_workflow is not None else """case "$command_name" in
  phase31_verify)
    python3 tools/bazel/phase31_final_evidence_intake.py --wiring-only
    python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31
    ;;
  phase31_verify_tests)
    python3 tools/bazel/phase31_final_evidence_intake_test.py
    ;;
esac
"""
        justfile = maybe_justfile if maybe_justfile is not None else """phase31-verify:
    bazel run //tools/bazel:phase31_verify_tests
    bazel run //tools/bazel:phase31_verify
"""
        self.write_file(root, "BUILD.bazel", root_build)
        self.write_file(root, "tools/bazel/BUILD.bazel", tools_build)
        self.write_file(root, "tools/bazel/rust_workflow.sh", workflow)
        self.write_file(root, "justfile", justfile)

    def test_contract_only_accepts_current_contract(self) -> None:
        # Arrange
        args = ["--contract-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_contract_validation_rejects_missing_adapter_field(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["stream_adapters"][0].pop("validator")
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("simulator adapter missing validator", result.stdout)

    def test_help_exposes_final_intake_flags(self) -> None:
        # Arrange
        expected_flags = [
            "--simulator-evidence-input",
            "--hardware-media-safety-evidence-input",
            "--live-service-evidence-input",
            "--release-input",
            "--phase23-retained-output",
            "--submitter-identity-ref",
        ]

        # Act
        result = self.run_verifier(["--help"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        for flag in expected_flags:
            self.assertIn(flag, result.stdout)

    def test_quick_writes_quarantined_non_final_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--quick", "--output-dir", DEFAULT_OUTPUT_DIR], maybe_root=root)
            manifest = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")
            rejected = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/rejected-submissions.json")

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 0)
        self.assertEqual(manifest["rejected_count"], 4)
        self.assertEqual(manifest["finality_status"], "quarantined-non-final")
        self.assertTrue(all(row["finality_status"] == "quarantined-non-final" for row in rejected["rejected_submissions"]))

    def test_quick_rejects_symlinked_output_parent(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        outside_dir = tempfile.TemporaryDirectory()
        with temp_dir, outside_dir:
            outside_root = Path(outside_dir.name)
            (root / "build").mkdir(parents=True)
            (root / "build/ci-evidence").symlink_to(outside_root, target_is_directory=True)

            # Act
            result = self.run_verifier(["--quick", "--output-dir", DEFAULT_OUTPUT_DIR], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("--output-dir cannot contain symlink path component", result.stdout)
        self.assertFalse((outside_root / "phase31").exists())

    def test_raw_inputs_invoke_source_validators_and_write_receipts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            simulator_input = self.write_json(root, "simulator-input.json", {"simulator_evidence_packet": {"sanitized": True}})
            hardware_input = self.write_json(root, "hardware-input.json", {"hardware_media_safety_evidence_packet": {"sanitized": True}})
            live_input = self.write_json(root, "live-input.json", {"live_service_evidence_packet": {"sanitized": True}})
            release_input = self.write_json(root, "release-input.json", {"evidence_rows": [{"id": "rel-bin-firmware-image"}]})

            # Act
            result = self.run_verifier(
                [
                    "--simulator-evidence-input",
                    simulator_input,
                    "--hardware-media-safety-evidence-input",
                    hardware_input,
                    "--live-service-evidence-input",
                    live_input,
                    "--release-input",
                    release_input,
                    "--submitter-identity-ref",
                    SUBMITTER,
                    "--output-dir",
                    DEFAULT_OUTPUT_DIR,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")
            invocations = [
                json.loads(line)
                for line in (root / "build/source-validator-invocations.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            release_invocation = invocations[-1]["argv"]

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 4)
        self.assertEqual([entry["phase"] for entry in invocations], [
            "23-simulator-evidence-execution",
            "24-hardware-media-and-safety-evidence-execution",
            "25-live-service-evidence-execution",
            "26-release-signing-and-upstream-result-evidence",
        ])
        self.assertIn("--phase23-simulator-row", release_invocation)
        self.assertIn("--phase24-hardware-media-safety-row", release_invocation)
        self.assertIn("--phase25-live-service-row", release_invocation)

    def test_retained_output_registration_accepts_real_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root)

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")
            receipt = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/stream-receipts/simulator-final-intake-receipt.json")

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 1)
        self.assertEqual(receipt["finality_status"], "accepted-final")
        self.assertEqual(receipt["submitter_identity_ref"], SUBMITTER)
        self.assertEqual(receipt["validator_command"], ["registered-retained-output", "build/ci-evidence/phase23"])
        self.assertNotIn("scenarios", receipt)

    def test_retained_output_registration_rejects_quick_placeholder(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root, real=False)

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 0)
        self.assertEqual(manifest["rejected_count"], 1)
        self.assertIn("real_simulator_evidence_supplied must be true", result.stdout)

    def test_secret_bearing_retained_output_is_rejected_before_acceptance(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root, extra_manifest={"access_token": "external secret should not be retained"})

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 0)
        self.assertIn("forbidden evidence fields", result.stdout)

    def test_symlinked_retained_output_root_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        outside_dir = tempfile.TemporaryDirectory()
        with temp_dir, outside_dir:
            outside_root = Path(outside_dir.name)
            self.write_json(
                outside_root,
                "simulator-result-manifest.json",
                {
                    "artifact_name": "phase23-simulator-evidence-execution",
                    "command_mode": "evidence-input",
                    "output_root": "build/ci-evidence/phase23",
                    "phase": "23-simulator-evidence-execution",
                    "phase_lifecycle_id": "23-2026-06-23T18-45-38",
                    "real_simulator_evidence_supplied": True,
                    "status": "passed",
                },
            )
            self.write_json(
                outside_root,
                "upstream-simulator-result-row.json",
                {
                    "artifact_refs": ["external://phase23/logs/run.json"],
                    "redaction_status": "passed",
                    "source_ref_status": "passed",
                },
            )
            (root / "build/ci-evidence").mkdir(parents=True)
            (root / "build/ci-evidence/phase23").symlink_to(outside_root, target_is_directory=True)

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("cannot contain symlink path component", result.stdout)

    def test_unsafe_artifact_ref_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root, artifact_ref="/tmp/raw-output.log")

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("ref must stay within allowed roots", result.stdout)

    def test_external_artifact_ref_traversal_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root, artifact_ref="external://phase23/../raw-output.log")

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("ref must stay within allowed roots", result.stdout)

    def test_release_evidence_refs_are_containment_checked(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_json(
                root,
                "build/ci-evidence/phase26/release-upstream-run-manifest.json",
                {
                    "artifact_name": "phase26-release-signing-upstream-evidence",
                    "output_root": "build/ci-evidence/phase26",
                    "phase": "26-release-signing-and-upstream-result-evidence",
                    "phase_lifecycle_id": "26-2026-06-24T13-36-46",
                    "real_release_evidence_supplied": True,
                    "release_status": "passed",
                },
            )
            self.write_json(
                root,
                "build/ci-evidence/phase26/upstream-result-row-table.json",
                {
                    "rows": [
                        {
                            "artifact_refs": ["external://phase26/artifacts/release.json"],
                            "criterion_id": "final-release-artifact-signing-evidence",
                            "evidence_refs": ["/tmp/raw-release-log.txt"],
                            "redaction_status": "passed",
                            "source_lifecycle_status": "current",
                            "source_ref_status": "passed",
                            "status": "passed",
                        }
                    ]
                },
            )

            # Act
            result = self.run_verifier(
                [
                    "--phase26-retained-output",
                    "build/ci-evidence/phase26",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("evidence_refs ref must stay within allowed roots", result.stdout)

    def test_release_row_table_accepts_consumed_phase23_to_phase25_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_json(
                root,
                "build/ci-evidence/phase26/release-upstream-run-manifest.json",
                {
                    "artifact_name": "phase26-release-signing-upstream-evidence",
                    "output_root": "build/ci-evidence/phase26",
                    "phase": "26-release-signing-and-upstream-result-evidence",
                    "phase_lifecycle_id": "26-2026-06-24T13-36-46",
                    "real_release_evidence_supplied": True,
                    "release_status": "passed",
                },
            )
            self.write_json(
                root,
                "build/ci-evidence/phase26/upstream-result-row-table.json",
                {
                    "rows": [
                        {
                            "artifact_refs": ["external://phase23/logs/simulator.json"],
                            "criterion_id": "final-simulator-evidence",
                            "evidence_refs": ["external://phase23/evidence/simulator.json"],
                            "redaction_status": "passed",
                            "source_lifecycle_status": "current",
                            "source_ref_status": "passed",
                            "status": "passed",
                        },
                        {
                            "artifact_refs": ["external://phase24/logs/hardware.json"],
                            "criterion_id": "final-hardware-safety-media-evidence",
                            "evidence_refs": ["external://phase24/evidence/hardware.json"],
                            "redaction_status": "passed",
                            "source_lifecycle_status": "current",
                            "source_ref_status": "passed",
                            "status": "passed",
                        },
                        {
                            "artifact_refs": ["external://phase25/logs/live.json"],
                            "criterion_id": "final-live-network-transfer-evidence",
                            "evidence_refs": ["external://phase25/evidence/live.json"],
                            "redaction_status": "passed",
                            "source_lifecycle_status": "current",
                            "source_ref_status": "passed",
                            "status": "passed",
                        },
                        {
                            "artifact_refs": ["external://phase26/artifacts/release.json"],
                            "criterion_id": "final-release-artifact-signing-evidence",
                            "evidence_refs": ["external://phase26/evidence/release.json"],
                            "redaction_status": "passed",
                            "source_lifecycle_status": "current",
                            "source_ref_status": "passed",
                            "status": "passed",
                        },
                    ]
                },
            )
            self.write_json(
                root,
                "build/ci-evidence/phase26/artifact-reference-summary.json",
                {
                    "artifact_refs": ["external://phase20/artifacts/firmware.bbf"],
                    "digest_refs": [
                        {
                            "artifact_ref": "external://phase20/artifacts/firmware.bbf",
                            "sha256": "b" * 64,
                        }
                    ],
                },
            )

            # Act
            result = self.run_verifier(
                [
                    "--phase26-retained-output",
                    "build/ci-evidence/phase26",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )
            manifest = self.read_json(root, f"{DEFAULT_OUTPUT_DIR}/final-intake-manifest.json")

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(manifest["accepted_count"], 1)

    def test_stale_lifecycle_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root, lifecycle="23-stale")

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("phase_lifecycle_id must be 23-2026-06-23T18-45-38", result.stdout)

    def test_missing_submitter_identity_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_retained_stream(root)

            # Act
            result = self.run_verifier(["--phase23-retained-output", "build/ci-evidence/phase23"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("submitter_identity_ref is required", result.stdout)

    def test_row_only_retained_output_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_json(
                root,
                "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                {
                    "artifact_refs": ["external://phase23/logs/run.json"],
                    "redaction_status": "passed",
                    "source_ref_status": "passed",
                },
            )

            # Act
            result = self.run_verifier(
                [
                    "--phase23-retained-output",
                    "build/ci-evidence/phase23",
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("missing required path", result.stdout)

    def test_prose_raw_submission_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            prose_input = self.write_file(root, "simulator-prose.txt", "Maintainer says the simulator passed.")

            # Act
            result = self.run_verifier(
                [
                    "--simulator-evidence-input",
                    prose_input,
                    "--submitter-identity-ref",
                    SUBMITTER,
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("is not valid JSON evidence", result.stdout)
        self.assertFalse((root / "build/source-validator-invocations.jsonl").exists())

    def test_wiring_only_accepts_current_wiring(self) -> None:
        # Arrange
        args = ["--wiring-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_requires_tests_before_verifier(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase31_wiring(
                root,
                maybe_justfile="""phase31-verify:
    bazel run //tools/bazel:phase31_verify
    bazel run //tools/bazel:phase31_verify_tests
""",
            )

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("justfile phase31-verify recipe must run tests before verifier", result.stdout)


if __name__ == "__main__":
    unittest.main()
