#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase26_release_signing_upstream_evidence.py"
CONTRACT = "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
PHASE17_CONTRACT = "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json"
PHASE18_CONTRACT = "tools/bazel/manifests/phase18_cutover_review_contract.json"
PHASE20_CONTRACT = "tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json"
PHASE20_TEMPLATE = "tools/bazel/manifests/phase20_release_environment_inputs.template.json"
DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase26"
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


class Phase26ReleaseSigningUpstreamEvidenceTest(unittest.TestCase):
    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for path in [VERIFIER, ROOT / CONTRACT, ROOT / PHASE17_CONTRACT, ROOT / PHASE18_CONTRACT, ROOT / PHASE20_CONTRACT, ROOT / PHASE20_TEMPLATE]:
            destination = root / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        return temp_dir, root

    def run_verifier(self, args: list[str], maybe_root: Path | None = None) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase26_release_signing_upstream_evidence.py"
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

    def write_release_input(self, root: Path, rows: list[dict[str, object]], path: str = "release-input.json") -> str:
        input_path = root / path
        input_path.write_text(json.dumps({"evidence_rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def complete_release_rows(self, root: Path) -> list[dict[str, object]]:
        contract = self.read_json(root, PHASE20_CONTRACT)
        contract_rows = contract["rows"]
        artifact_surfaces = {
            str(row["id"]): str(row["artifact_surface"])
            for row in contract_rows
            if isinstance(row, dict)
        }
        rows: list[dict[str, object]] = []
        for row_id in REQUIRED_ROW_IDS:
            artifact_ref = f"external://phase20/artifacts/{row_id}.json"
            rows.append(
                {
                    "id": row_id,
                    "artifact_refs": [artifact_ref],
                    "artifact_surface": artifact_surfaces[row_id],
                    "affected_artifact_surface": artifact_surfaces[row_id],
                    "build_input_identity": "git:phase26-test-build;bazel:phase17_release_candidate_artifacts",
                    "key_identity_ref": "release-key-fingerprint:sha256:phase26-test",
                    "mismatch_class": "pass",
                    "mismatch_reason": "Approved release metadata matched the archived reference classification.",
                    "operator": "phase26-test-operator",
                    "owner_phase": "20-release-candidate-artifact-production",
                    "proof_class": "approved-release-run",
                    "release_run_id": "phase26-approved-run-001",
                    "residual_risk": "Limited to supplied release-environment evidence.",
                    "retention_refs": ["external://phase20/retention/phase26-approved-run-001"],
                    "signing_mode": "external-release-signing",
                    "status": "passed",
                    "subject_digests": [
                        {
                            "artifact_ref": artifact_ref,
                            "sha256": "a" * 64,
                        }
                    ],
                    "timestamp": "2026-06-24T14:00:00Z",
                    "verification_outcome": "approved-release-metadata",
                }
            )
        return rows

    def test_contract_lists_phase26_policy_and_phase20_rows(self) -> None:
        # Arrange
        contract = self.read_json(ROOT, CONTRACT)

        # Act
        result = self.run_verifier(["--contract-only"])

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(contract["id"], "phase26_release_signing_upstream_evidence_contract")
        self.assertEqual(contract["output_root"], DEFAULT_OUTPUT_DIR)
        release_policy = contract["release_policy"]
        self.assertEqual(release_policy["canonical_phase20_release_row_ids"], REQUIRED_ROW_IDS)
        self.assertIn("approved-release-run", release_policy["pass_capable_proof_classes"])
        self.assertIn("external-release-key-evidence", release_policy["pass_capable_proof_classes"])

    def test_security_only_accepts_checked_in_safe_inputs(self) -> None:
        # Arrange
        args = ["--security-only"]

        # Act
        result = self.run_verifier(args)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_release_row_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            release_input = self.write_release_input(root, rows[:-1])

            # Act
            result = self.run_verifier(["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("release input missing rows", result.stdout)

    def test_duplicate_release_row_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            rows[-1] = dict(rows[0])
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("duplicates row id", result.stdout)

    def test_unknown_release_row_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            rows[-1]["id"] = "rel-unknown-artifact"
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("uses unknown row id: rel-unknown-artifact", result.stdout)

    def test_passed_release_row_requires_phase26_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            del rows[0]["release_run_id"]
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("release_run_id must be a non-empty string", result.stdout)

    def test_signing_rows_require_key_identity_and_signing_mode(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            for row in rows:
                if row["id"] == "rel-bbf-firmware-package":
                    del row["key_identity_ref"]
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("key_identity_ref must be a non-empty string", result.stdout)

    def test_release_candidate_cannot_pass_phase26(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            for row in rows:
                row["proof_class"] = "release-candidate"
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("release-candidate cannot pass Phase 26", result.stdout)

    def test_local_smoke_and_template_only_cannot_pass_phase26(self) -> None:
        for proof_class in ["local-smoke", "template-only"]:
            with self.subTest(proof_class=proof_class):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows(root)
                    for row in rows:
                        row["proof_class"] = proof_class
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(["--quick", "--release-input", release_input], maybe_root=root)

                    # Assert
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn("cannot pass with proof_class", result.stdout)

    def test_secret_tainted_input_aborts_before_output_root_exists(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            rows[0]["private_key"] = "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----"
            release_input = self.write_release_input(root, rows)
            output_root = root / DEFAULT_OUTPUT_DIR

            # Act
            result = self.run_verifier(["--quick", "--release-input", release_input, "--output-dir", DEFAULT_OUTPUT_DIR], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("forbidden release evidence marker", result.stdout)
            self.assertFalse(output_root.exists())

    def test_output_dir_rejects_absolute_parent_and_symlink_escapes(self) -> None:
        for bad_output_dir in ["/tmp/phase26", "../phase26"]:
            with self.subTest(output_dir=bad_output_dir):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    # Act
                    result = self.run_verifier(["--quick", "--output-dir", bad_output_dir], maybe_root=root)

                    # Assert
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn("--output-dir must", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            outside = root / "outside-output"
            outside.mkdir()
            output_parent = root / "build/ci-evidence"
            output_parent.mkdir(parents=True)
            (output_parent / "phase26").symlink_to(outside, target_is_directory=True)

            # Act
            result = self.run_verifier(["--quick", "--output-dir", DEFAULT_OUTPUT_DIR], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("symlink escape risk", result.stdout)


if __name__ == "__main__":
    unittest.main()
