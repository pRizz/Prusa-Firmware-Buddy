#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase20_release_candidate_artifacts.py"
CONTRACT = "tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json"
TEMPLATE = "tools/bazel/manifests/phase20_release_environment_inputs.template.json"
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase20"
SOURCE_REF_MANIFESTS = [
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json",
    "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json",
    CONTRACT,
    TEMPLATE,
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/representative_products.json",
]
REQUIRED_SURFACES = [
    ".bin",
    ".bbf",
    ".dfu",
    ".map",
    ".provenance.json",
    "resource-image",
    "resource-package",
    "language-bundle",
    "wui-assets",
    "esp-package",
    "mmu-package",
    "dwarf-firmware",
    "modularbed-firmware",
    "xbuddy-extension-firmware",
    "package-manifest",
    "signing-summary",
    "provenance-summary",
    "retention-manifest",
    "comparison-report",
]
REQUIRED_ROW_IDS = [
    "rel-bin-firmware-image",
    "rel-bbf-firmware-package",
    "rel-dfu-update-package",
    "rel-map-and-provenance",
    "rel-resource-image-package",
    "rel-language-bundles",
    "rel-wui-assets",
    "rel-esp-packages",
    "rel-mmu-package",
    "rel-auxiliary-dwarf-firmware",
    "rel-auxiliary-modularbed-firmware",
    "rel-auxiliary-xbuddy-extension-firmware",
    "rel-package-manifests",
    "rel-signing-key-identity",
    "rel-build-input-identity",
    "rel-artifact-retention",
    "rel-reference-comparison-report",
    "rel-contract-traceability-redaction-boundary",
]
PROOF_CLASSES = [
    "release-candidate",
    "approved-release-run",
    "external-release-key-evidence",
    "local-smoke",
    "template-only",
]
STATUS_VOCABULARY = [
    "pending-release-input",
    "release-run-required",
    "external-signing-required",
    "blocked-signing-key-unavailable",
    "source-contract-passed",
    "passed",
    "failed",
    "rejected-redaction",
    "rejected-overclaim",
]
MISMATCH_CLASSES = [
    "pass",
    "intentional-delta",
    "blocker",
    "deferred-retained-code-issue",
]


class Phase20ReleaseCandidateArtifactsTest(unittest.TestCase):
    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase20_release_candidate_artifacts.py")
        for path in SOURCE_REF_MANIFESTS:
            source = ROOT / path
            if source.exists():
                destination = root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        return temp_dir, root

    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase20_release_candidate_artifacts.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def read_contract(self, root: Path) -> dict[str, object] | None:
        contract_path = root / CONTRACT
        if not contract_path.exists():
            return None
        return json.loads(contract_path.read_text(encoding="utf-8"))

    def write_contract(self, root: Path, contract: dict[str, object]) -> None:
        contract_path = root / CONTRACT
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def write_phase20_wiring(
        self,
        root: Path,
        maybe_tools_build: str | None = None,
        maybe_root_build: str | None = None,
        maybe_workflow: str | None = None,
        maybe_justfile: str | None = None,
    ) -> None:
        tools_build = maybe_tools_build or """filegroup(
    name = "phase20_release_environment_input_manifest",
    srcs = ["manifests/phase20_release_environment_inputs.template.json"],
)

filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = [":phase20_release_environment_input_manifest"],
)

filegroup(
    name = "phase17_representative_release_smoke",
    srcs = [":representative_release_artifacts"],
)

filegroup(
    name = "phase20_source_ref_manifests",
    srcs = [
        "manifests/phase17_release_candidate_evidence_contract.json",
        "manifests/phase19_aggregate_ci_evidence_contract.json",
        "manifests/phase20_release_candidate_artifacts_contract.json",
        "manifests/phase20_release_environment_inputs.template.json",
        "manifests/phase11_reference_comparisons.json",
        "manifests/representative_products.json",
    ],
)

shell_binary(
    name = "phase20_verify",
    src = "rust_workflow.sh",
    data = [
        "phase20_release_candidate_artifacts.py",
        "manifests/phase20_release_candidate_artifacts_contract.json",
        "manifests/phase20_release_environment_inputs.template.json",
        ":phase20_source_ref_manifests",
        ":phase17_release_candidate_artifacts",
        ":phase17_representative_release_smoke",
        "//:phase20_release_candidate_artifacts_docs",
        "//:phase17_release_candidate_evidence_docs",
        "//:phase19_aggregate_ci_evidence_docs",
    ],
)

shell_binary(
    name = "phase20_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase20_release_candidate_artifacts.py",
        "phase20_release_candidate_artifacts_test.py",
        "manifests/phase20_release_candidate_artifacts_contract.json",
        "manifests/phase20_release_environment_inputs.template.json",
        ":phase20_source_ref_manifests",
        ":phase17_release_candidate_artifacts",
        ":phase17_representative_release_smoke",
    ],
)
"""
        root_build = maybe_root_build or """filegroup(
    name = "phase20_release_candidate_artifacts_docs",
    srcs = [
        ".planning/phases/20-release-candidate-artifact-production/20-CONTEXT.md",
        ".planning/phases/20-release-candidate-artifact-production/20-RESEARCH.md",
        ".planning/phases/20-release-candidate-artifact-production/20-VALIDATION.md",
        ".planning/phases/20-release-candidate-artifact-production/20-01-PLAN.md",
        ".planning/phases/20-release-candidate-artifact-production/20-02-PLAN.md",
    ],
)

alias(
    name = "phase20_verify",
    actual = "//tools/bazel:phase20_verify",
)

alias(
    name = "phase20_verify_tests",
    actual = "//tools/bazel:phase20_verify_tests",
)
"""
        workflow = maybe_workflow or """case "$command_name" in
  phase20_verify)
    python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only
    python3 tools/bazel/phase20_release_candidate_artifacts.py --quick
    ;;
  phase20_verify_tests)
    python3 tools/bazel/phase20_release_candidate_artifacts_test.py
    ;;
esac
"""
        justfile = maybe_justfile or """phase20-verify:
    bazel run //tools/bazel:phase20_verify_tests
    bazel run //tools/bazel:phase20_verify
"""
        self.write_file(root, "tools/bazel/BUILD.bazel", tools_build)
        self.write_file(root, "BUILD.bazel", root_build)
        self.write_file(root, "tools/bazel/rust_workflow.sh", workflow)
        self.write_file(root, "justfile", justfile)

    def write_release_input(
        self,
        root: Path,
        rows: list[dict[str, object]],
        path: str = "release-input.json",
    ) -> str:
        input_path = root / path
        input_path.write_text(json.dumps({"evidence_rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def complete_release_rows(self, maybe_root: Path | None = None) -> list[dict[str, object]]:
        root = maybe_root or ROOT
        contract = self.read_contract(root) or {}
        contract_rows = contract.get("rows", [])
        artifact_surfaces = {
            str(row.get("id")): str(row.get("artifact_surface"))
            for row in contract_rows
            if isinstance(row, dict) and row.get("id") and row.get("artifact_surface")
        }
        rows: list[dict[str, object]] = []
        for row_id in REQUIRED_ROW_IDS:
            artifact_ref = f"external://phase20/artifacts/{row_id}.json"
            rows.append(
                {
                    "id": row_id,
                    "artifact_refs": [artifact_ref],
                    "artifact_surface": artifact_surfaces.get(row_id, ".bbf"),
                    "build_input_identity": "git:phase20-test-build;bazel:phase17_release_candidate_artifacts",
                    "builder_command": "bazel build //tools/bazel:phase17_release_candidate_artifacts",
                    "contract_validation": "phase20-contract-validation-passed",
                    "key_identity_ref": "release-key-fingerprint:sha256:phase20-test",
                    "mismatch_class": "pass",
                    "mismatch_reason": "Approved release metadata matched the archived reference classification.",
                    "operator": "phase20-test-operator",
                    "owner_phase": "20-release-candidate-artifact-production",
                    "proof_class": "approved-release-run",
                    "redaction_scan": "phase20-redaction-scan-passed",
                    "release_run_id": "phase20-approved-run-001",
                    "residual_risk": "Limited to supplied release-environment evidence.",
                    "retention_refs": ["external://phase20/retention/phase20-approved-run-001"],
                    "signing_mode": "external-release-signing",
                    "status": "passed",
                    "subject_digests": [
                        {
                            "artifact_ref": artifact_ref,
                            "sha256": "a" * 64,
                        }
                    ],
                    "source_contract_snapshot": "phase20-source-contract-snapshot",
                    "timestamp": "2026-06-21T13:00:00Z",
                    "verification_outcome": "approved-release-metadata",
                    "affected_artifact_surface": artifact_surfaces.get(row_id, ".bbf"),
                }
            )
        return rows

    def required_metadata_cases(self, contract: dict[str, object]) -> list[tuple[str, str]]:
        rows = contract.get("rows", [])
        cases: list[tuple[str, str]] = []
        seen_fields: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_id = row.get("id")
            if not isinstance(row_id, str):
                continue
            for group in [
                "release_metadata_required",
                "signing_metadata_required",
                "provenance_metadata_required",
                "retention_metadata_required",
            ]:
                fields = row.get(group)
                if not isinstance(fields, list):
                    continue
                for field in fields:
                    if isinstance(field, str) and field not in seen_fields:
                        cases.append((row_id, field))
                        seen_fields.add(field)
        return cases

    def test_contract_lists_all_release_surfaces(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            if contract is None:
                # Act
                result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertEqual(result.returncode, 0, result.stdout)
                return

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(contract.get("required_artifact_outputs"), REQUIRED_SURFACES)
            self.assertEqual(contract.get("proof_class_vocabulary"), PROOF_CLASSES)
            self.assertEqual(contract.get("status_vocabulary"), STATUS_VOCABULARY)
            self.assertEqual(contract.get("mismatch_class_vocabulary"), MISMATCH_CLASSES)
            self.assertEqual(
                [row.get("id") for row in contract.get("rows", [])],
                REQUIRED_ROW_IDS,
            )
            for surface in REQUIRED_SURFACES:
                with self.subTest(surface=surface):
                    broken_contract = json.loads(json.dumps(contract))
                    broken_contract["required_artifact_outputs"] = [
                        existing for existing in REQUIRED_SURFACES if existing != surface
                    ]
                    self.write_contract(root, broken_contract)

                    # Act
                    broken_result = self.run_verifier(["--contract-only"], maybe_root=root)

                    # Assert
                    self.assertNotEqual(broken_result.returncode, 0)
                    self.assertIn(surface, broken_result.stdout)
            self.write_contract(root, contract)
            for row_id in REQUIRED_ROW_IDS:
                with self.subTest(row_id=row_id):
                    broken_contract = json.loads(json.dumps(contract))
                    broken_contract["rows"] = [
                        row for row in broken_contract["rows"] if row.get("id") != row_id
                    ]
                    self.write_contract(root, broken_contract)

                    # Act
                    broken_result = self.run_verifier(["--contract-only"], maybe_root=root)

                    # Assert
                    self.assertNotEqual(broken_result.returncode, 0)
                    self.assertIn(row_id, broken_result.stdout)

    def test_contract_rejects_source_refs_outside_approved_manifests(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_file(
                root,
                "tools/bazel/manifests/unapproved.json",
                json.dumps({"rows": [{"id": "rel-bin-firmware-image"}]}, indent=2, sort_keys=True) + "\n",
            )
            contract = self.read_contract(root)
            if contract is None:
                self.skipTest("contract fixture is unavailable")
            contract["rows"][0]["source_contract_refs"] = [
                "tools/bazel/manifests/unapproved.json#rel-bin-firmware-image",
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not an approved Phase 20 source manifest", result.stdout)

    def test_contract_rejects_missing_source_ref_row(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            if contract is None:
                self.skipTest("contract fixture is unavailable")
            contract["rows"][0]["source_contract_refs"] = [
                "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json#does-not-exist",
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("row not found in approved row collections", result.stdout)

    def test_contract_rejects_passed_default_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            if contract is None:
                self.skipTest("contract fixture is unavailable")
            contract["rows"][0]["default_status"] = "passed"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("default_status cannot be passed without approved release input", result.stdout)

    def test_quick_rejects_passed_default_status_from_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            if contract is None:
                self.skipTest("contract fixture is unavailable")
            contract["rows"][0]["default_status"] = "passed"
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("default_status cannot be passed without approved release input", result.stdout)

    def test_quick_without_release_input_writes_pending_result_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            output_dir = root / DEFAULT_OUTPUT_DIR

            # Act
            result = self.run_verifier(["--quick", "--output-dir", output_dir.as_posix()], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            manifest_path = output_dir / "release-result-manifest.json"
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertFalse(manifest["release_inputs_supplied"])
            for row in manifest["rows"]:
                self.assertNotEqual(row["status"], "passed")

    def test_quick_rejects_relative_output_dir_that_escapes_through_symlink(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        outside_temp_dir = tempfile.TemporaryDirectory()
        with temp_dir, outside_temp_dir:
            outside_dir = Path(outside_temp_dir.name)
            outside_target = outside_dir / "escaped"
            outside_target.mkdir()
            marker_path = outside_target / "do-not-delete.txt"
            marker_path.write_text("outside target must survive\n", encoding="utf-8")
            output_root = root / DEFAULT_OUTPUT_DIR
            output_root.mkdir(parents=True)
            (output_root / "link").symlink_to(outside_dir, target_is_directory=True)

            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", f"{DEFAULT_OUTPUT_DIR}/link/escaped"],
                maybe_root=root,
            )

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--output-dir must stay under", result.stdout)
            self.assertTrue(outside_target.is_dir())
            self.assertEqual(marker_path.read_text(encoding="utf-8"), "outside target must survive\n")
            self.assertFalse((outside_target / "release-result-manifest.json").exists())

    def test_quick_rejects_symlinked_output_root_before_deleting_target(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            victim_dir = root / "build/ci-evidence/phase20-victim"
            victim_dir.mkdir(parents=True)
            marker_path = victim_dir / "do-not-delete.txt"
            marker_path.write_text("victim target must survive\n", encoding="utf-8")
            output_root = root / DEFAULT_OUTPUT_DIR
            output_root.parent.mkdir(parents=True, exist_ok=True)
            output_root.symlink_to(victim_dir, target_is_directory=True)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--output-dir must stay under", result.stdout)
            self.assertTrue(output_root.is_symlink())
            self.assertTrue(victim_dir.is_dir())
            self.assertEqual(marker_path.read_text(encoding="utf-8"), "victim target must survive\n")
            self.assertFalse((victim_dir / "release-result-manifest.json").exists())

    def test_passed_result_rejects_local_smoke_and_template_only_proof(self) -> None:
        for proof_class in ["local-smoke", "template-only"]:
            with self.subTest(proof_class=proof_class):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows()
                    rows[0]["proof_class"] = proof_class
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(proof_class, result.stdout)

    def test_passed_release_input_requires_contract_declared_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            if contract is None:
                self.skipTest("contract fixture is unavailable")
            required_cases = self.required_metadata_cases(contract)

            for row_id, required_field in required_cases:
                with self.subTest(row_id=row_id, required_field=required_field):
                    rows = self.complete_release_rows(root)
                    target_row = next(row for row in rows if row["id"] == row_id)
                    target_row.pop(required_field, None)
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                    # Assert
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(required_field, result.stdout)

    def test_redaction_rejects_private_key_and_payload_fields(self) -> None:
        forbidden_fields = [
            "private_key",
            "raw_firmware_payload",
            "token",
            "password",
            "credential",
        ]
        for field_name in forbidden_fields:
            with self.subTest(field_name=field_name):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows()
                    rows[0][field_name] = "secret-material"
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field_name, result.stdout)

    def test_release_refs_reject_absolute_and_parent_traversal_paths(self) -> None:
        bad_refs = [
            "/tmp/phase20/artifact.bbf",
            "../phase20/artifact.bbf",
            "build/ci-evidence/phase19/release-result-manifest.json",
        ]
        for bad_ref in bad_refs:
            with self.subTest(bad_ref=bad_ref):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows()
                    rows[0]["artifact_refs"] = [bad_ref]
                    rows[0]["retention_refs"] = [bad_ref]
                    rows[0]["subject_digests"] = [{"artifact_ref": bad_ref, "sha256": "b" * 64}]
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(bad_ref, result.stdout)

    def test_comparison_rows_require_exact_classification_metadata(self) -> None:
        required_fields = [
            "mismatch_class",
            "mismatch_reason",
            "owner_phase",
            "affected_artifact_surface",
            "residual_risk",
        ]
        for required_field in required_fields:
            with self.subTest(required_field=required_field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows()
                    rows[0].pop(required_field)
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(required_field, result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows()
            rows[0]["mismatch_class"] = "unclassified"
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(["--quick", "--release-input", release_input], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unclassified", result.stdout)

    def test_passed_release_input_rejects_invalid_comparison_metadata_values(self) -> None:
        cases = [
            ("mismatch_class", "", "mismatch_class must be a non-empty string"),
            ("mismatch_reason", "", "mismatch_reason must be a non-empty string"),
            ("residual_risk", "", "residual_risk must be a non-empty string"),
            ("owner_phase", "19-aggregate-ci-evidence", "owner_phase must be 20-release-candidate-artifact-production"),
            ("affected_artifact_surface", "wrong-surface", "affected_artifact_surface must match contract row"),
        ]
        for field_name, bad_value, expected_message in cases:
            with self.subTest(field_name=field_name):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows(root)
                    rows[0][field_name] = bad_value
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_message, result.stdout)

    def test_wiring_requires_phase20_identity_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase20_wiring(root)

            # Act
            accepted = self.run_verifier(["--wiring-only"], maybe_root=root)
            bad_tools_build = (root / "tools/bazel/BUILD.bazel").read_text(encoding="utf-8").replace(
                'filegroup(\n    name = "phase20_release_environment_input_manifest",\n    srcs = ["manifests/phase20_release_environment_inputs.template.json"],\n)\n\n',
                "",
            )
            self.write_phase20_wiring(root, maybe_tools_build=bad_tools_build)
            rejected = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(accepted.returncode, 0, accepted.stdout)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("phase20_release_environment_input_manifest", rejected.stdout)

    def test_wiring_rejects_phase17_empty_release_target(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            bad_tools_build = """filegroup(
    name = "phase20_release_environment_input_manifest",
    srcs = ["manifests/phase20_release_environment_inputs.template.json"],
)

filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = [],
)
"""
            self.write_phase20_wiring(root, maybe_tools_build=bad_tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase17_release_candidate_artifacts", result.stdout)
        self.assertIn("phase20_release_environment_input_manifest", result.stdout)

    def test_wiring_rejects_smoke_release_target(self) -> None:
        for bad_label in [
            ":phase17_representative_release_smoke",
            ":representative_release_artifacts",
            "//tools/bazel:phase3_verify",
        ]:
            with self.subTest(bad_label=bad_label):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    bad_tools_build = f"""filegroup(
    name = "phase20_release_environment_input_manifest",
    srcs = ["manifests/phase20_release_environment_inputs.template.json"],
)

filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = ["{bad_label}"],
)
"""
                    self.write_phase20_wiring(root, maybe_tools_build=bad_tools_build)

                    # Act
                    result = self.run_verifier(["--wiring-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(bad_label, result.stdout)

    def test_just_phase20_verify_runs_tests_before_verifier(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase20_wiring(root)
            bad_justfile = """phase20-verify:
    bazel run //tools/bazel:phase20_verify
    bazel run //tools/bazel:phase20_verify_tests
"""
            self.write_phase20_wiring(root, maybe_justfile=bad_justfile)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tests before verifier", result.stdout)


if __name__ == "__main__":
    unittest.main()
