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
PYRAMID_MANIFEST = "tools/bazel/manifests/phase11_parity_pyramid.json"

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

    def write_source_paths(self, root: Path, source_paths: list[str]) -> None:
        for source_path in source_paths:
            relative_path = Path(source_path)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                continue
            if (root / source_path).exists():
                continue
            self.write_file(root, source_path, "source-backed fixture\n")

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


if __name__ == "__main__":
    unittest.main()
