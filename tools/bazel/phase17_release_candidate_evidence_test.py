#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase17_release_candidate_evidence.py"
CONTRACT = "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json"
SOURCE_REF_FILES = [
    "tools/bazel/manifests/representative_products.json",
    "tools/bazel/manifests/phase7_generated_outputs.json",
    "tools/bazel/manifests/phase7_storage_media.json",
    "tools/bazel/manifests/phase10_auxiliary_build_update.json",
    "tools/bazel/manifests/phase10_auxiliary_controllers.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json",
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json",
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
RELEASE_WORKFLOW_OUTPUTS = [
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


class Phase17ReleaseCandidateEvidenceTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase17_release_candidate_evidence.py"
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
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase17_release_candidate_evidence.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_file(self, root: Path, path: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, full_path)

    def copy_source_ref_inputs(self, root: Path) -> None:
        for path in SOURCE_REF_FILES:
            self.copy_file(root, path)

    def copy_complete_surface(self, root: Path) -> None:
        self.copy_file(root, CONTRACT)
        self.copy_source_ref_inputs(root)

    def read_contract(self, root: Path) -> dict[str, object]:
        return json.loads((root / CONTRACT).read_text(encoding="utf-8"))

    def write_contract(self, root: Path, contract: dict[str, object]) -> None:
        self.write_file(root, CONTRACT, json.dumps(contract, indent=2, sort_keys=True) + "\n")

    def write_release_evidence(
        self,
        root: Path,
        rows: list[dict[str, object]],
        path: str = "release-evidence.json",
    ) -> str:
        self.write_file(root, path, json.dumps({"evidence_rows": rows}, indent=2, sort_keys=True) + "\n")
        return path

    def complete_release_row(
        self,
        row_id: str = "rel-bin-firmware-image",
        result: str = "passed",
        evidence_type: str = "approved-release-run",
        maybe_artifact_refs: list[str] | None = None,
        maybe_bazel_label: str | None = None,
    ) -> dict[str, object]:
        artifact_refs = maybe_artifact_refs or [
            f"build/ci-evidence/phase17/logs/{row_id}.log",
            f"external://phase17/{row_id}/artifact",
        ]
        return {
            "artifact_digest_sha256": "0" * 64,
            "artifact_outputs": RELEASE_WORKFLOW_OUTPUTS,
            "artifact_refs": artifact_refs,
            "artifact_surface": ".bin",
            "bazel_label": maybe_bazel_label or "//tools/bazel:phase17_release_candidate_artifacts",
            "build_input_identity": "git:phase17-test-build",
            "comparison_refs": ["external://phase17/comparisons/product-artifacts"],
            "evidence_type": evidence_type,
            "key_identity_ref": "release-key-fingerprint:sha256:phase17-test",
            "mismatch_class": "pass",
            "mismatch_reason": "Approved release comparison metadata matched the named reference surface.",
            "operator": "phase17-test-operator",
            "owner_phase": "17-release-candidate-artifact-and-signing-gates",
            "product_profile": "all-supported-release-products",
            "provenance_refs": ["external://phase17/provenance/product-artifacts"],
            "redaction_summary": "Only names, digests, and external refs are retained.",
            "release_command": "bazel build //tools/bazel:phase17_release_candidate_artifacts",
            "release_run_id": "phase17-approved-run-001",
            "release_run_required": True,
            "residual_risk": "Limited to supplied approved release-run metadata.",
            "result": result,
            "retention_path": "external://phase17/retention/product-artifacts",
            "signing_mode": "external-release-key",
            "timestamp": "2026-06-19T15:00:00Z",
            "verification_outcome": "approved-release-metadata",
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
    name = "phase17_release_candidate_artifacts",
    srcs = [],
)

filegroup(
    name = "phase17_representative_release_smoke",
    srcs = [":representative_release_artifacts"],
)

filegroup(
    name = "phase17_source_ref_manifests",
    srcs = [
{manifest_srcs}
    ],
)

shell_binary(
    name = "phase17_verify",
    src = "rust_workflow.sh",
    data = [
        "phase17_release_candidate_evidence.py",
        "manifests/phase17_release_candidate_evidence_contract.json",
        ":phase17_release_candidate_artifacts",
        ":phase17_representative_release_smoke",
        ":phase17_source_ref_manifests",
        "//:phase17_release_candidate_evidence_docs",
        "//:phase11_cutover_evidence_docs",
    ],
)

shell_binary(
    name = "phase17_verify_tests",
    src = "rust_workflow.sh",
    data = [
        "phase17_release_candidate_evidence.py",
        "phase17_release_candidate_evidence_test.py",
        "manifests/phase17_release_candidate_evidence_contract.json",
        ":phase17_release_candidate_artifacts",
        ":phase17_representative_release_smoke",
        ":phase17_source_ref_manifests",
    ],
)
"""
        root_build = maybe_root_build or """filegroup(
    name = "phase17_release_candidate_evidence_docs",
    srcs = [
        ".planning/phases/17-release-candidate-artifact-and-signing-gates/17-CONTEXT.md",
        ".planning/phases/17-release-candidate-artifact-and-signing-gates/17-RESEARCH.md",
        ".planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md",
        ".planning/phases/17-release-candidate-artifact-and-signing-gates/17-01-PLAN.md",
    ],
)

alias(
    name = "phase17_release_candidate_artifacts",
    actual = "//tools/bazel:phase17_release_candidate_artifacts",
)

alias(
    name = "phase17_verify",
    actual = "//tools/bazel:phase17_verify",
)

alias(
    name = "phase17_verify_tests",
    actual = "//tools/bazel:phase17_verify_tests",
)
"""
        workflow = maybe_workflow or """case "$command_name" in
  phase17_verify)
    python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only
    python3 tools/bazel/phase17_release_candidate_evidence.py --quick
    ;;
  phase17_verify_tests)
    python3 tools/bazel/phase17_release_candidate_evidence_test.py
    ;;
esac
"""
        justfile = maybe_justfile or """phase17-verify:
    bazel run //tools/bazel:phase17_verify_tests
    bazel run //tools/bazel:phase17_verify

phase17-release-artifacts-smoke:
    bazel build //tools/bazel:phase17_representative_release_smoke
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

    def test_contract_requires_all_release_rows(self) -> None:
        for row_id in REQUIRED_ROW_IDS:
            with self.subTest(row_id=row_id):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract["rows"] = [row for row in contract["rows"] if row["id"] != row_id]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(row_id, result.stdout)

    def test_contract_requires_rel_requirement_coverage(self) -> None:
        for requirement_id in ["REL-01", "REL-02", "REL-03"]:
            with self.subTest(requirement_id=requirement_id):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    for row in contract["rows"]:
                        row["requirement_ids"] = [
                            existing for existing in row["requirement_ids"] if existing != requirement_id
                        ]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(requirement_id, result.stdout)

    def test_contract_rejects_invalid_mismatch_class_and_passed_defaults(self) -> None:
        cases = [
            ("mismatch_class", "unclassified"),
            ("default_status", "passed"),
        ]
        for field, value in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract["rows"][0][field] = value
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(value, result.stdout)

    def test_contract_requires_release_workflow_fields_and_identity(self) -> None:
        cases = [
            ("bazel_label", None, "bazel_label"),
            ("release_command", None, "release_command"),
            ("artifact_outputs", None, "artifact_outputs"),
            ("release_run_required", None, "release_run_required"),
            ("bazel_label", "//tools/bazel:representative_release_artifacts", "representative_release_artifacts"),
        ]
        for field, value, expected in cases:
            with self.subTest(field=field, value=value):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    if value is None:
                        del contract["rows"][0][field]
                    else:
                        contract["rows"][0][field] = value
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_contract_requires_supported_products_and_boards(self) -> None:
        cases = [
            ("supported_release_products", "COREONE"),
            ("supported_release_products", "XL_DEV_KIT"),
            ("supported_release_boards", "DWARF"),
            ("supported_release_boards", "MODULARBED"),
            ("supported_release_boards", "XBUDDY_EXTENSION"),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract[field] = [existing for existing in contract[field] if existing != value]
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(value, result.stdout)

    def test_quick_writes_phase17_artifacts_and_pending_statuses(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)
            manifest = json.loads((root / "build/ci-evidence/phase17/run-manifest.json").read_text())
            normalized = json.loads((root / "build/ci-evidence/phase17/normalized-release-results.json").read_text())

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            for path in [
                "build/ci-evidence/phase17/run-manifest.json",
                "build/ci-evidence/phase17/normalized-release-results.json",
                "build/ci-evidence/phase17/redacted-signing-provenance-summary.json",
                "build/ci-evidence/phase17/comparison-classification-report.json",
                "build/ci-evidence/phase17/source-contract-snapshots/phase17_release_candidate_evidence_contract.json",
                "build/ci-evidence/phase17/release-operator-evidence-input.json",
                "build/ci-evidence/phase17/logs/rel-bin-firmware-image.log",
            ]:
                self.assertTrue((root / path).exists(), path)
            self.assertFalse(manifest["release_inputs_supplied"])
            statuses = {row["status"] for row in normalized["results"]}
            self.assertIn("pending-release-input", statuses)
            self.assertIn("external-signing-required", statuses)
            self.assertIn("source-contract-passed", statuses)

    def test_release_evidence_accepts_complete_redacted_pass(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            evidence_path = self.write_release_evidence(root, [self.complete_release_row()])

            # Act
            result = self.run_verifier(["--quick", "--release-evidence", evidence_path], maybe_root=root)
            normalized = json.loads((root / "build/ci-evidence/phase17/normalized-release-results.json").read_text())

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = {row["id"]: row for row in normalized["results"]}
        self.assertEqual(rows["rel-bin-firmware-image"]["status"], "passed")
        self.assertEqual(rows["rel-bin-firmware-image"]["key_identity_ref"], "release-key-fingerprint:sha256:phase17-test")

    def test_release_evidence_rejects_bad_paths_workflow_and_local_smoke_pass(self) -> None:
        cases = [
            ({"maybe_artifact_refs": ["../escape.log"]}, "cannot traverse"),
            ({"maybe_artifact_refs": ["artifact://phase17/not-explicit"]}, "external://phase17"),
            ({"maybe_bazel_label": "//tools/bazel:representative_release_artifacts"}, "representative_release_artifacts"),
            ({"evidence_type": "local-smoke"}, "approved-release"),
        ]
        for kwargs, expected in cases:
            with self.subTest(expected=expected):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    evidence_path = self.write_release_evidence(root, [self.complete_release_row(**kwargs)])

                    # Act
                    result = self.run_verifier(["--quick", "--release-evidence", evidence_path], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_security_rejects_forbidden_markers_without_leaking_values(self) -> None:
        cases = [
            ("-----BEGIN PRIVATE KEY-----", "private-key-block"),
            ("signing_key_value = super-secret-value", "signing-key-value"),
            ("firmware_payload", "payload-marker"),
            ("password: super-secret-value", "credential-assignment"),
            ("release-candidate passed locally", "release-candidate passed locally"),
            ("reference demotion approved", "reference demotion approved"),
        ]
        for marker, expected in cases:
            with self.subTest(expected=expected):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.write_file(root, "build/ci-evidence/phase17/leak.json", marker + "\n")

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout.lower())
                self.assertNotIn("super-secret-value", result.stdout)

    def test_verifier_does_not_embed_forbidden_subprocess_invocations(self) -> None:
        # Arrange
        source = VERIFIER.read_text(encoding="utf-8") if VERIFIER.exists() else ""

        # Act
        forbidden = [needle for needle in ["shell=True", "bash -c", "python -c", "node -e"] if needle in source]

        # Assert
        self.assertEqual(forbidden, [])

    def test_wiring_accepts_and_rejects_phase17_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)

            # Act
            accepted = self.run_verifier(["--wiring-only"], maybe_root=root)
            bad_justfile = """phase17-verify:
    bazel run //tools/bazel:phase17_verify
    bazel run //tools/bazel:phase17_verify_tests
"""
            self.write_wiring(root, maybe_justfile=bad_justfile)
            rejected = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(accepted.returncode, 0, accepted.stdout)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("tests before verifier", rejected.stdout)

    def test_wiring_rejects_missing_release_label(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(encoding="utf-8").replace(
                'name = "phase17_release_candidate_artifacts"',
                'name = "phase17_missing_release_candidate_artifacts"',
                1,
            )
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase17_release_candidate_artifacts", result.stdout)

    def test_wiring_rejects_release_candidate_target_wrapping_smoke_artifacts(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            bad_tools_build = """filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = [":representative_release_artifacts"],
)

filegroup(
    name = "phase17_representative_release_smoke",
    srcs = [":representative_release_artifacts"],
)
"""
            self.write_wiring(root, maybe_tools_build=bad_tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot wrap local smoke dependencies", result.stdout)


if __name__ == "__main__":
    unittest.main()
