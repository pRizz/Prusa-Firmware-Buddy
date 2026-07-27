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
ARCHIVED_PHASE_DIR = ".planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence"
PYRAMID_MANIFEST = "tools/bazel/manifests/phase11_parity_pyramid.json"
REQUIREMENT_MANIFEST = "tools/bazel/manifests/phase11_requirement_evidence.json"
COMPARISON_MANIFEST = "tools/bazel/manifests/phase11_reference_comparisons.json"
CUTOVER_MANIFEST = "tools/bazel/manifests/phase11_cutover_readiness.json"
RETAINED_MANIFEST = "tools/bazel/manifests/phase11_retained_code_justifications.json"
ARCHIVED_REQUIREMENTS = ".planning/milestones/v1.0-REQUIREMENTS.md"

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


class Phase11VerifierFixture:

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
            shutil.copy2(
                ROOT / "tools/bazel/phase11_contract_policy.py",
                root / "tools/bazel/phase11_contract_policy.py",
            )
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
                    "python3 tools/bazel/phase11_verify.py --rust-only")
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
                    "python3 tools/bazel/phase11_verify.py --cutover-only")
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

    def copy_phase11_surface(self,
                             root: Path,
                             reconcile_requirements: bool = True) -> None:
        if (ROOT / ARCHIVED_REQUIREMENTS).exists():
            self.copy_file(root, ARCHIVED_REQUIREMENTS)
        else:
            self.copy_file(root, ".planning/REQUIREMENTS.md")
        self.write_file(root, f"{PHASE_DIR}/11-VALIDATION.md",
                        "local validation fixture\n")
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
                    self.write_source_paths(
                        root, [str(item) for item in source_artifacts])
            if manifest_path == CUTOVER_MANIFEST:
                data = json.loads(
                    (root / manifest_path).read_text(encoding="utf-8"))
                known_concern_rows = data.get("known_concern_dispositions")
                if isinstance(known_concern_rows, list):
                    for row in known_concern_rows:
                        if not isinstance(row, dict):
                            continue
                        source_artifacts = row.get("source_artifacts")
                        if isinstance(source_artifacts, list):
                            self.write_source_paths(
                                root, [str(item) for item in source_artifacts])
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
            "id":
            row_id,
            "layer":
            row_id.removeprefix("pyramid-"),
            "requirement_id":
            "VERF-01",
            "proof_scope":
            proof_scope,
            "evidence_class":
            evidence_class,
            "local_status":
            local_status,
            "cutover_status":
            "pending-cutover",
            "source_artifacts":
            source_artifacts or [
                ".planning/phases/11-parity-pyramid-and-cutover-evidence/11-CONTEXT.md"
            ],
            "verifier_commands":
            ["python3 tools/bazel/phase11_verify.py --pyramid-only"],
            "required_non_local_evidence": (["non-local artifact required"]
                                            if proof_scope != "local" else []),
            "secret_handling":
            "name-only-or-redacted",
            "overclaim_guard":
            "enforced-by-phase11-verifier",
            "phase_lifecycle_id":
            PHASE_LIFECYCLE_ID,
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
                self.write_source_paths(
                    root, [str(item) for item in source_artifacts])
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


class Phase11VerifierTest(Phase11VerifierFixture, unittest.TestCase):

    def test_quick_accepts_complete_phase11_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_phase11_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_pyramid_only_accepts_complete_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_complete_pyramid_manifest(root)

            # Act
            result = self.run_verifier(["--pyramid-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    import phase11_verify_failure_test

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(Phase11VerifierTest)
    suite.addTests(
        loader.loadTestsFromTestCase(
            phase11_verify_failure_test.Phase11VerifierFailureTest))
    result = unittest.TextTestRunner().run(suite)
    raise SystemExit(not result.wasSuccessful())
