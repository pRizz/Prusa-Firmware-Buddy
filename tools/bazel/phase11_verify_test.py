#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase11_verify.py"

PHASE = "11-parity-pyramid-and-cutover-evidence"
PHASE_LIFECYCLE_ID = "11-2026-06-14T18-48-49"
PHASE_DIR = ".planning/phases/11-parity-pyramid-and-cutover-evidence"
PYRAMID_MANIFEST = "tools/bazel/manifests/phase11_parity_pyramid.json"
REQUIREMENT_MANIFEST = "tools/bazel/manifests/phase11_requirement_evidence.json"
COMPARISON_MANIFEST = "tools/bazel/manifests/phase11_reference_comparisons.json"
CUTOVER_MANIFEST = "tools/bazel/manifests/phase11_cutover_readiness.json"
RETAINED_MANIFEST = "tools/bazel/manifests/phase11_retained_code_justifications.json"

MANIFEST_COLLECTIONS = {
    PYRAMID_MANIFEST: "parity_pyramid",
    REQUIREMENT_MANIFEST: "requirement_evidence",
    COMPARISON_MANIFEST: "reference_comparisons",
    CUTOVER_MANIFEST: "cutover_criteria",
    RETAINED_MANIFEST: "retained_code_justifications",
}

REQUIRED_PYRAMID_ROW_IDS = [
    "pyramid-rust-unit-tests",
    "pyramid-adapter-domain-contract-tests",
    "pyramid-generated-drift-checks",
    "pyramid-reference-fixture-comparisons",
    "pyramid-simulator-flows",
    "pyramid-network-tls-api-checks",
    "pyramid-release-artifact-checks",
    "pyramid-hardware-smoke-manual-gates",
    "pyramid-retained-code-justifications",
]


class Phase11VerifierTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase11_verify.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
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
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase11_verify.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def copy_file(self, root: Path, path: str) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, full_path)

    def write_source_paths(self, root: Path, source_paths: list[str]) -> None:
        for source_path in source_paths:
            relative_path = Path(source_path)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                continue
            if (root / source_path).exists():
                continue
            self.write_file(root, source_path, "source-backed fixture\n")

    def manifest_rows(self, root: Path, path: str) -> list[dict[str, object]]:
        data = json.loads((root / path).read_text(encoding="utf-8"))
        rows = data[MANIFEST_COLLECTIONS[path]]
        self.assertIsInstance(rows, list)
        return rows

    def write_manifest_rows(
        self,
        root: Path,
        path: str,
        rows: list[dict[str, object]],
    ) -> None:
        data = json.loads((root / path).read_text(encoding="utf-8"))
        data[MANIFEST_COLLECTIONS[path]] = rows
        self.write_file(root, path, json.dumps(data, indent=2))

    def reconcile_requirement_fixture(self, root: Path) -> None:
        rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
        for row in rows:
            if row["id"] == "req-verf-03":
                row["source_artifacts"] = [
                    f"{PHASE_DIR}/11-03-SUMMARY.md",
                    COMPARISON_MANIFEST,
                    "rust/crates/domain/src/cutover.rs",
                ]
                row["verifier_command_or_evidence_class"] = (
                    "python3 tools/bazel/phase11_verify.py --comparison-only; "
                    "python3 tools/bazel/phase11_verify.py --rust-only"
                )
                row["current_status"] = "source-backed-local-passed"
                row["cutover_status"] = "pending-non-local-reference-comparison-evidence"
                row["intentional_delta_status"] = "normalized-reference-comparisons-source-backed"
                row["retained_code_justification"] = (
                    "Reference comparison proof is source-backed by Plan 11-03 while CMake/C++ "
                    "stays the guarded reference oracle until all non-local evidence is accepted."
                )
                row["required_non_local_evidence"] = [
                    "Simulator, hardware, live network/TLS, storage media, release-candidate, MMU, RS485, and toolchanger proof remains required where reference comparison rows name those gates."
                ]
                row["cutover_blocker"] = (
                    "Reference comparison rows are locally valid, but non-local comparison gates remain open."
                )
            if row["id"] == "req-verf-05":
                row["source_artifacts"] = [
                    f"{PHASE_DIR}/11-04-SUMMARY.md",
                    CUTOVER_MANIFEST,
                    RETAINED_MANIFEST,
                ]
                row["verifier_command_or_evidence_class"] = (
                    "python3 tools/bazel/phase11_verify.py --cutover-only"
                )
                row["current_status"] = "source-backed-local-passed"
                row["cutover_status"] = "not-cutover-ready"
                row["intentional_delta_status"] = "cutover-readiness-contract-source-backed"
                row["retained_code_justification"] = (
                    "Cutover readiness and retained-code justifications are source-backed, while "
                    "criteria-reference-demotion-blocked remains the active demotion gate."
                )
                row["required_non_local_evidence"] = [
                    "Simulator, hardware-smoke, manual-hardware-required, live network/TLS, storage media, release-candidate, signing, MMU, RS485, toolchanger, and maintainer acceptance evidence remain required before demotion."
                ]
                row["cutover_blocker"] = (
                    "criteria-reference-demotion-blocked keeps demotion unavailable until all non-local evidence gates are attached and accepted."
                )
        self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

    def copy_phase11_surface(self, root: Path, reconcile_requirements: bool = True) -> None:
        self.copy_file(root, ".planning/REQUIREMENTS.md")
        self.write_file(root, f"{PHASE_DIR}/11-VALIDATION.md", "local validation fixture\n")
        for path in [
            f"{PHASE_DIR}/11-01-SUMMARY.md",
            f"{PHASE_DIR}/11-02-SUMMARY.md",
            f"{PHASE_DIR}/11-03-SUMMARY.md",
            f"{PHASE_DIR}/11-04-SUMMARY.md",
        ]:
            self.write_file(root, path, "source-backed summary fixture\n")
        for manifest_path in MANIFEST_COLLECTIONS:
            self.copy_file(root, manifest_path)
            for row in self.manifest_rows(root, manifest_path):
                source_artifacts = row.get("source_artifacts")
                if isinstance(source_artifacts, list):
                    self.write_source_paths(root, [str(item) for item in source_artifacts])
            if manifest_path == CUTOVER_MANIFEST:
                data = json.loads((root / manifest_path).read_text(encoding="utf-8"))
                known_concern_rows = data.get("known_concern_dispositions")
                if isinstance(known_concern_rows, list):
                    for row in known_concern_rows:
                        if not isinstance(row, dict):
                            continue
                        source_artifacts = row.get("source_artifacts")
                        if isinstance(source_artifacts, list):
                            self.write_source_paths(root, [str(item) for item in source_artifacts])
        self.copy_file(root, "rust/crates/domain/src/cutover.rs")
        self.copy_file(root, "rust/crates/domain/src/lib.rs")
        if reconcile_requirements:
            self.reconcile_requirement_fixture(root)

    def pyramid_row(
        self,
        row_id: str,
        proof_scope: str = "local",
        evidence_class: str = "static-verifier",
        local_status: str = "passed-local",
        source_artifacts: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "id": row_id,
            "layer": row_id.removeprefix("pyramid-"),
            "requirement_id": "VERF-01",
            "proof_scope": proof_scope,
            "evidence_class": evidence_class,
            "local_status": local_status,
            "cutover_status": "pending-cutover",
            "source_artifacts": source_artifacts or [
                ".planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md"
            ],
            "verifier_commands": ["python3 tools/bazel/phase11_verify.py --pyramid-only"],
            "required_non_local_evidence": (
                ["non-local artifact required"] if proof_scope != "local" else []
            ),
            "secret_handling": "name-only-or-redacted",
            "overclaim_guard": "enforced-by-phase11-verifier",
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        }

    def write_complete_pyramid_manifest(
        self,
        root: Path,
        rows: list[dict[str, object]] | None = None,
    ) -> None:
        default_rows = [
            self.pyramid_row(
                "pyramid-rust-unit-tests",
                evidence_class="rust-unit-test",
            ),
            self.pyramid_row(
                "pyramid-adapter-domain-contract-tests",
                evidence_class="adapter-contract-test",
            ),
            self.pyramid_row(
                "pyramid-generated-drift-checks",
                evidence_class="generated-drift-check",
            ),
            self.pyramid_row(
                "pyramid-reference-fixture-comparisons",
                evidence_class="reference-fixture-comparison",
            ),
            self.pyramid_row(
                "pyramid-simulator-flows",
                proof_scope="simulator",
                evidence_class="simulator-flow",
                local_status="pending-simulator",
            ),
            self.pyramid_row(
                "pyramid-network-tls-api-checks",
                proof_scope="ci",
                evidence_class="network-tls-api-check",
                local_status="pending-ci",
            ),
            self.pyramid_row(
                "pyramid-release-artifact-checks",
                proof_scope="ci",
                evidence_class="release-artifact-check",
                local_status="pending-ci",
            ),
            self.pyramid_row(
                "pyramid-hardware-smoke-manual-gates",
                proof_scope="manual-hardware-required",
                evidence_class="manual-hardware-required",
                local_status="manual-hardware-required",
            ),
            self.pyramid_row(
                "pyramid-retained-code-justifications",
                proof_scope="retained-code-justification",
                evidence_class="retained-code-justification",
                local_status="accepted-retained-code",
            ),
        ]
        manifest_rows = rows if rows is not None else default_rows
        for row in manifest_rows:
            source_artifacts = row.get("source_artifacts")
            if isinstance(source_artifacts, list):
                self.write_source_paths(root, [str(item) for item in source_artifacts])
        self.write_file(
            root,
            PYRAMID_MANIFEST,
            json.dumps(
                {
                    "schema_version": "1",
                    "phase": PHASE,
                    "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
                    "parity_pyramid": manifest_rows,
                },
                indent=2,
            ),
        )

    def test_pyramid_only_accepts_complete_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_complete_pyramid_manifest(root)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_pyramid_only_rejects_local_hardware_overclaim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = [
                self.pyramid_row(row_id)
                for row_id in REQUIRED_PYRAMID_ROW_IDS
                if row_id != "pyramid-hardware-smoke-manual-gates"
            ]
            rows.append(
                self.pyramid_row(
                    "pyramid-hardware-smoke-manual-gates",
                    proof_scope="hardware-smoke",
                    evidence_class="manual-hardware-required",
                    local_status="passed-local",
                )
            )
            self.write_complete_pyramid_manifest(root, rows=rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pyramid-hardware-smoke-manual-gates", result.stdout)
        self.assertIn("passed-local", result.stdout)

    def test_pyramid_only_rejects_source_path_escape(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = [self.pyramid_row(row_id) for row_id in REQUIRED_PYRAMID_ROW_IDS]
            rows[0]["source_artifacts"] = ["../outside"]
            self.write_complete_pyramid_manifest(root, rows=rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("../outside", result.stdout)
        self.assertIn("repo-relative", result.stdout)

    def test_pyramid_only_rejects_path_confusing_row_ids(self) -> None:
        # Arrange
        invalid_row_ids = {
            "pyramid rust unit tests": "id must be printable ASCII",
            "pyramid-rust..unit-tests": "id must be path-free",
        }

        for invalid_row_id, expected_message in invalid_row_ids.items():
            with self.subTest(invalid_row_id=invalid_row_id):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = [self.pyramid_row(row_id) for row_id in REQUIRED_PYRAMID_ROW_IDS]
                    rows[0]["id"] = invalid_row_id
                    self.write_complete_pyramid_manifest(root, rows=rows)

                    # Act
                    result = self.run_verifier(["--pyramid-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(invalid_row_id, result.stdout)
                self.assertIn(expected_message, result.stdout)

    def test_pyramid_only_rejects_secret_marker(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = [self.pyramid_row(row_id) for row_id in REQUIRED_PYRAMID_ROW_IDS]
            rows[0]["secret_handling"] = "token_value"
            rows[1]["cutover_status"] = "byte-identical firmware"
            self.write_complete_pyramid_manifest(root, rows=rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token_value", result.stdout)
        self.assertIn("byte-identical firmware", result.stdout)

    def test_pyramid_only_rejects_missing_required_row(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = [
                self.pyramid_row(row_id)
                for row_id in REQUIRED_PYRAMID_ROW_IDS
                if row_id != "pyramid-retained-code-justifications"
            ]
            self.write_complete_pyramid_manifest(root, rows=rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pyramid-retained-code-justifications", result.stdout)

    def test_pyramid_only_rejects_empty_non_local_evidence_list(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_complete_pyramid_manifest(root)
            rows = self.manifest_rows(root, PYRAMID_MANIFEST)
            for row in rows:
                if row["id"] == "pyramid-simulator-flows":
                    row["required_non_local_evidence"] = []
            self.write_manifest_rows(root, PYRAMID_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pyramid-simulator-flows", result.stdout)
        self.assertIn("required_non_local_evidence", result.stdout)

    def test_pyramid_only_rejects_stale_requires_plan_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, PYRAMID_MANIFEST)
            for row in rows:
                if row["id"] == "pyramid-reference-fixture-comparisons":
                    row["cutover_status"] = "requires-plan-11-03-reference-comparison-rows"
                if row["id"] == "pyramid-retained-code-justifications":
                    row["cutover_status"] = "requires-plan-11-04-retained-code-review"
            self.write_manifest_rows(root, PYRAMID_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires-plan-11-03-reference-comparison-rows", result.stdout)
        self.assertIn("requires-plan-11-04-retained-code-review", result.stdout)

    def test_requirements_only_reports_missing_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_file(root, ".planning/REQUIREMENTS.md", "# Requirements\n")

            # Act
            result = self.run_verifier(["--requirements-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase11_requirement_evidence.json", result.stdout)

    def test_comparison_only_reports_missing_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase11_reference_comparisons.json", result.stdout)

    def test_cutover_only_reports_missing_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase11_cutover_readiness.json", result.stdout)
        self.assertIn("phase11_retained_code_justifications.json", result.stdout)

    def test_rust_only_reports_missing_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_file(root, "rust/crates/domain/src/lib.rs", "#![forbid(unsafe_code)]\n")

            # Act
            result = self.run_verifier(["--rust-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rust/crates/domain/src/cutover.rs", result.stdout)

    def test_requirements_only_rejects_missing_v1_requirement(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = [
                row
                for row in self.manifest_rows(root, REQUIREMENT_MANIFEST)
                if row["id"] != "req-verf-05"
            ]
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("req-verf-05", result.stdout)

    def test_requirements_only_rejects_roadmap_only_proof(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            self.write_file(root, ".planning/ROADMAP.md", "roadmap fixture\n")
            rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
            for row in rows:
                if row["id"] == "req-verf-04":
                    row["source_artifacts"] = [".planning/ROADMAP.md"]
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("roadmap-only", result.stdout)

    def test_requirements_only_rejects_empty_non_local_evidence_list(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
            for row in rows:
                if row["id"] == "req-base-02":
                    row["required_non_local_evidence"] = []
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("req-base-02", result.stdout)
        self.assertIn("required_non_local_evidence", result.stdout)

    def test_requirements_only_rejects_stale_not_created_yet_blocker(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
            for row in rows:
                if row["id"] == "req-rust-03":
                    row["cutover_blocker"] = (
                        "Plan 11-04 retained-code acceptance rows are not created yet."
                    )
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not created yet", result.stdout)

    def test_comparison_only_rejects_byte_identity_without_fixture(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-release-metadata":
                    row["comparison_kind"] = "byte-identity-with-fixture"
                    row["byte_identity_claim"] = True
                    row.pop("reference_fixture", None)
                    row["normalization_rule"] = "normalize release metadata"
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-release-metadata", result.stdout)
        self.assertIn("byte_identity_claim", result.stdout)

    def test_comparison_only_rejects_unknown_comparison_kind(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-release-metadata":
                    row["comparison_kind"] = "normalized-semantics"
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-release-metadata", result.stdout)
        self.assertIn("comparison_kind is not allowed", result.stdout)

    def test_comparison_only_rejects_normalized_byte_identity_claim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-release-metadata":
                    row["comparison_kind"] = "normalized-semantic"
                    row["byte_identity_claim"] = True
                    row["reference_fixture"] = "release-candidate-metadata"
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-release-metadata", result.stdout)
        self.assertIn("normalized comparisons must not claim byte identity", result.stdout)

    def test_comparison_only_rejects_byte_identity_kind_without_claim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-release-metadata":
                    row["comparison_kind"] = "byte-identity-with-fixture"
                    row["byte_identity_claim"] = False
                    row["reference_fixture"] = "release-candidate-metadata"
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-release-metadata", result.stdout)
        self.assertIn("byte identity comparisons must set byte_identity_claim true", result.stdout)

    def test_comparison_only_rejects_empty_non_local_evidence_list(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, COMPARISON_MANIFEST)
            for row in rows:
                if row["id"] == "ref-product-artifacts":
                    row["required_non_local_evidence"] = []
            self.write_manifest_rows(root, COMPARISON_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--comparison-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ref-product-artifacts", result.stdout)
        self.assertIn("required_non_local_evidence", result.stdout)

    def test_cutover_only_rejects_non_string_cutover_lists(self) -> None:
        # Arrange
        invalid_fields = ["required_evidence", "verifier_commands"]

        for invalid_field in invalid_fields:
            with self.subTest(invalid_field=invalid_field):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_phase11_surface(root)
                    rows = self.manifest_rows(root, CUTOVER_MANIFEST)
                    for row in rows:
                        if row["id"] == "criteria-all-v1-requirements-mapped":
                            row[invalid_field] = [123]
                    self.write_manifest_rows(root, CUTOVER_MANIFEST, rows)

                    # Act
                    result = self.run_verifier(["--cutover-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("criteria-all-v1-requirements-mapped", result.stdout)
                self.assertIn(invalid_field, result.stdout)
                self.assertIn("list of strings", result.stdout)

    def test_cutover_only_rejects_non_string_retained_required_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, RETAINED_MANIFEST)
            for row in rows:
                if row["id"] == "retained-hal-cmsis-vendor":
                    row["required_evidence"] = [123]
            self.write_manifest_rows(root, RETAINED_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("retained-hal-cmsis-vendor", result.stdout)
        self.assertIn("required_evidence", result.stdout)
        self.assertIn("list of strings", result.stdout)

    def test_cutover_only_rejects_demote_reference_true(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, CUTOVER_MANIFEST)
            for row in rows:
                if row["id"] == "criteria-local-verifier-passed":
                    row["status"] = "pending-aggregate-verifier"
                    row["demotion_allowed"] = True
            self.write_manifest_rows(root, CUTOVER_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("criteria-local-verifier-passed", result.stdout)
        self.assertIn("demotion_allowed", result.stdout)

    def test_cutover_only_rejects_ready_reference_demotion_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            rows = self.manifest_rows(root, CUTOVER_MANIFEST)
            for row in rows:
                if row["id"] == "criteria-reference-demotion-blocked":
                    row["status"] = "passed-local"
            self.write_manifest_rows(root, CUTOVER_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("criteria-reference-demotion-blocked", result.stdout)
        self.assertIn("status must remain not-cutover-ready", result.stdout)

    def test_cutover_only_rejects_known_concern_source_path_escape(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            data = json.loads((root / CUTOVER_MANIFEST).read_text(encoding="utf-8"))
            rows = data["known_concern_dispositions"]
            self.assertIsInstance(rows, list)
            rows[0]["source_artifacts"] = ["../outside"]
            self.write_file(root, CUTOVER_MANIFEST, json.dumps(data, indent=2))

            # Act
            result = self.run_verifier(["--cutover-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("known concern", result.stdout)
        self.assertIn("../outside", result.stdout)
        self.assertIn("repo-relative", result.stdout)

    def test_security_only_rejects_secret_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            self.write_file(root, f"{PHASE_DIR}/11-VALIDATION.md", "token_value\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("token_value", result.stdout)

    def test_security_only_rejects_context_and_research_secret_markers(self) -> None:
        # Arrange
        phase_doc_paths = [
            f"{PHASE_DIR}/11-CONTEXT.md",
            f"{PHASE_DIR}/11-RESEARCH.md",
        ]

        for phase_doc_path in phase_doc_paths:
            with self.subTest(phase_doc_path=phase_doc_path):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_phase11_surface(root)
                    self.write_file(root, phase_doc_path, "token_value\n")

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(phase_doc_path, result.stdout)
                self.assertIn("token_value", result.stdout)

    def test_security_only_rejects_private_key_header_variants(self) -> None:
        # Arrange
        private_key_headers = [
            "-----BEGIN RSA PRIVATE KEY-----",
            "-----BEGIN EC PRIVATE KEY-----",
            "-----BEGIN OPENSSH PRIVATE KEY-----",
        ]

        for private_key_header in private_key_headers:
            with self.subTest(private_key_header=private_key_header):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_phase11_surface(root)
                    self.write_file(root, f"{PHASE_DIR}/11-VALIDATION.md", private_key_header)

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(private_key_header, result.stdout)

    def test_security_only_rejects_mixed_case_secret_field_names(self) -> None:
        # Arrange
        secret_field_names = [
            "Certificate-Pem",
            "Password_Value",
            "Token-Value",
            "Private_Key",
        ]

        for secret_field_name in secret_field_names:
            with self.subTest(secret_field_name=secret_field_name):
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_phase11_surface(root)
                    self.write_file(root, f"{PHASE_DIR}/11-VALIDATION.md", secret_field_name)

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(secret_field_name, result.stdout)

    def test_security_only_rejects_cutover_overclaim(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            self.write_file(root, f"{PHASE_DIR}/11-01-SUMMARY.md", "hardware verified locally\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware verified locally", result.stdout)

    def test_rust_only_rejects_unsafe_cutover_contract(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)
            cutover_path = root / "rust/crates/domain/src/cutover.rs"
            cutover_path.write_text(
                cutover_path.read_text(encoding="utf-8") + "\nunsafe fn unsound() {}\n",
                encoding="utf-8",
            )

            # Act
            result = self.run_verifier(["--rust-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe function", result.stdout)

    def test_requirements_only_rejects_stale_pending_plan_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root, reconcile_requirements=False)
            rows = self.manifest_rows(root, REQUIREMENT_MANIFEST)
            for row in rows:
                if row["id"] == "req-verf-03":
                    row["current_status"] = "pending-plan-11-03"
                if row["id"] == "req-verf-05":
                    row["current_status"] = "pending-plan-11-04"
            self.write_manifest_rows(root, REQUIREMENT_MANIFEST, rows)

            # Act
            result = self.run_verifier(["--requirements-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pending-plan-11-03", result.stdout)
        self.assertIn("pending-plan-11-04", result.stdout)

    def test_quick_accepts_complete_phase11_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
