#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase22_metadata_reconciliation.py"
CONTRACT = "tools/bazel/manifests/phase22_metadata_reconciliation_contract.json"


class Phase22MetadataReconciliationTest(unittest.TestCase):
    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel/manifests").mkdir(parents=True)
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase22_metadata_reconciliation.py")
        test_path = ROOT / "tools/bazel/phase22_metadata_reconciliation_test.py"
        if test_path.exists():
            shutil.copy2(test_path, root / "tools/bazel/phase22_metadata_reconciliation_test.py")
        if (ROOT / CONTRACT).exists():
            shutil.copy2(ROOT / CONTRACT, root / CONTRACT)
        return temp_dir, root

    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase22_metadata_reconciliation.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def read_contract(self, root: Path) -> dict[str, object]:
        return json.loads((root / CONTRACT).read_text(encoding="utf-8"))

    def write_contract(self, root: Path, contract: dict[str, object]) -> None:
        contract_path = root / CONTRACT
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_text(self, root: Path, path: str, text: str) -> None:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def write_clean_validation_files(self, root: Path) -> None:
        clean_validation = """---
phase: phase
nyquist_compliant: true
wave_0_complete: true
---

## Wave 0 Requirements

- [x] Contract exists

| Task | Status |
| --- | --- |
| Task 1 | pass |
"""
        for phase in [14, 15, 16, 17, 18, 20]:
            self.write_text(
                root,
                f".planning/phases/{phase:02d}-example/{phase:02d}-VALIDATION.md",
                clean_validation,
            )

    def write_quick_ready_metadata(self, root: Path) -> None:
        self.write_text(
            root,
            ".planning/REQUIREMENTS.md",
            """
- [x] **SIM-03** Simulator evidence gates
- [x] **REV-02** Upstream result consumption
- [x] **REV-03** Demotion safeguards

| ID | Phase | Status |
| --- | --- | --- |
| SIM-03 | Phase 14 | Complete - hardware-only behavior is not simulator-proven |
| REV-02 | Phase 21 | Complete - demotion_allowed remains blocked without valid upstream results and maintainer decisions |
| REV-03 | Phase 21 | Complete - demotion_allowed remains blocked without valid upstream results and maintainer decisions |
""",
        )
        self.write_text(
            root,
            ".planning/ROADMAP.md",
            """
| Phase | Version | Plans | Status |
| --- | --- | --- | --- |
| 21. Final Readiness Result Consumption | v1.1 | 1/1 | Complete |
| 22. Evidence Metadata Reconciliation | v1.1 | 3/3 | Complete |
""",
        )
        self.write_text(
            root,
            ".planning/STATE.md",
            """
Current focus: Phase 22 evidence metadata reconciliation
Current position: Phase 22 Plan 3 of 3 completed
""",
        )
        self.write_clean_validation_files(root)
        validation_paths = [
            ".planning/phases/14-simulator-evidence-gates/14-VALIDATION.md",
            ".planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md",
            ".planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md",
            ".planning/phases/17-release-candidate-artifact-and-signing-gates/17-VALIDATION.md",
            ".planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md",
            ".planning/phases/20-release-candidate-artifact-production/20-VALIDATION.md",
        ]
        clean_validation = (root / ".planning/phases/14-example/14-VALIDATION.md").read_text(encoding="utf-8")
        for path in validation_paths:
            self.write_text(root, path, clean_validation)

    def test_missing_correction_source_refs_names_row_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            row = contract["metadata_corrections"][0]
            row_id = str(row["id"])
            row.pop("source_refs", None)
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(row_id, result.stdout)
        self.assertIn("source_refs", result.stdout)

    def test_non_blocking_debt_requires_owner_rationale_follow_up_and_source_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            contract["non_blocking_debt"] = [{"id": "debt-without-required-fields"}]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("debt-without-required-fields", result.stdout)
        for field in ["owner", "rationale", "follow_up_or_expiry", "source_refs"]:
            self.assertIn(field, result.stdout)

    def test_generated_artifacts_must_stay_under_phase22_output_root(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            contract["generated_artifacts"] = [
                "metadata-reconciliation-report.json",
                "../phase22-escape/audit-rerun-readiness.json",
                "/tmp/redacted-summary.md",
            ]
            self.write_contract(root, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated_artifacts", result.stdout)
        self.assertIn("../phase22-escape/audit-rerun-readiness.json", result.stdout)
        self.assertIn("/tmp/redacted-summary.md", result.stdout)

    def test_contract_rows_reject_sensitive_and_overclaim_markers(self) -> None:
        markers = [
            "private key",
            "token",
            "credential",
            "raw payload",
            "crash dump",
            "hardware verified locally",
            "reference demotion approved",
            "cutover complete",
            "signing verified locally",
        ]
        for marker in markers:
            with self.subTest(marker=marker):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    contract = self.read_contract(root)
                    contract["metadata_corrections"][0]["no_overclaim_rationale"] = marker
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--security-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(marker, result.stdout)

    def test_requirements_only_rejects_unchecked_and_complete_without_caveat(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_text(
                root,
                ".planning/REQUIREMENTS.md",
                """
- [ ] **SIM-03** Simulator evidence gates
- [ ] **REV-02** Upstream result consumption
- [ ] **REV-03** Demotion safeguards

| ID | Status |
| --- | --- |
| SIM-03 | Pending |
| REV-02 | Pending |
| REV-03 | Pending |
""",
            )

            # Act
            result = self.run_verifier(["--requirements-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for requirement_id in ["SIM-03", "REV-02", "REV-03"]:
            self.assertIn(requirement_id, result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_text(
                root,
                ".planning/REQUIREMENTS.md",
                """
- [x] **SIM-03** Simulator evidence gates
- [x] **REV-02** Upstream result consumption
- [x] **REV-03** Demotion safeguards

| ID | Status |
| --- | --- |
| SIM-03 | Complete |
| REV-02 | Complete |
| REV-03 | Complete |
""",
            )

            # Act
            result = self.run_verifier(["--requirements-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware-only behavior is not simulator-proven", result.stdout)
        self.assertIn("demotion_allowed remains blocked", result.stdout)

    def test_validation_only_rejects_wave_zero_placeholders_and_pending_rows(self) -> None:
        cases = {
            "wave_0_complete: false": "wave_0_complete",
            "nyquist_compliant: false": "nyquist_compliant",
            "no - Wave 0": "Wave 0",
            "No - Wave 0": "Wave 0",
            "no W0": "W0",
            "- [ ] Contract exists": "unchecked Wave 0",
            "| Task 1 | pending |": "pending",
        }
        for bad_text, expected in cases.items():
            with self.subTest(bad_text=bad_text):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.write_clean_validation_files(root)
                    self.write_text(
                        root,
                        ".planning/phases/14-example/14-VALIDATION.md",
                        f"""---
phase: phase
nyquist_compliant: true
wave_0_complete: true
---

## Wave 0 Requirements

{bad_text}
""",
                    )

                    # Act
                    result = self.run_verifier(["--validation-only"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_roadmap_state_only_rejects_stale_phase21_and_state_focus(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_text(
                root,
                ".planning/ROADMAP.md",
                """
| Phase | Version | Plans | Status |
| --- | --- | --- | --- |
| 21. Final Readiness Result Consumption | v1.1 | 0/0 | Planned |
""",
            )
            self.write_text(
                root,
                ".planning/STATE.md",
                """
Current focus: Phase 21 final readiness
Current position: Phase 21 awaiting verification
""",
            )

            # Act
            result = self.run_verifier(["--roadmap-state-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Phase 21", result.stdout)
        self.assertIn("STATE", result.stdout)

    def test_security_only_rejects_output_dir_escape(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--security-only", "--output-dir", "../phase22"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("output", result.stdout)

    def test_quick_writes_reports_and_readiness_passed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_quick_ready_metadata(root)
            output_dir = root / "build/ci-evidence/phase22"

            # Act
            result = self.run_verifier(["--quick", "--output-dir", "build/ci-evidence/phase22"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            report = json.loads((output_dir / "metadata-reconciliation-report.json").read_text(encoding="utf-8"))
            readiness = json.loads((output_dir / "audit-rerun-readiness.json").read_text(encoding="utf-8"))
            summary = (output_dir / "redacted-summary.md").read_text(encoding="utf-8")
            self.assertEqual(report["artifact_name"], "phase22-metadata-reconciliation")
            self.assertEqual(report["phase_lifecycle_id"], "22-2026-06-21T16-59-18")
            self.assertEqual(report["correction_count"], 13)
            self.assertEqual(readiness["status"], "passed")
            self.assertIn("Phase 22 reconciles metadata only", summary)
            self.assertTrue((output_dir / "sanitized-source-snapshots/.planning/REQUIREMENTS.md").is_file())

    def test_audit_readiness_maps_gaps_to_allowed_statuses(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_quick_ready_metadata(root)

            # Act
            result = self.run_verifier(["--quick", "--output-dir", "build/ci-evidence/phase22"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            readiness = json.loads(
                (root / "build/ci-evidence/phase22/audit-rerun-readiness.json").read_text(encoding="utf-8")
            )
            statuses = {row["status"] for row in readiness["audit_gap_mappings"]}
            self.assertEqual(readiness["status"], "passed")
            self.assertLessEqual(statuses, {"closed", "still_blocking", "non_blocking_debt"})
            self.assertIn("requirements-status-gap", {row["id"] for row in readiness["audit_gap_mappings"]})

    def test_generated_artifact_secret_or_overclaim_fails_security_scan(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_quick_ready_metadata(root)
            output_dir = root / "build/ci-evidence/phase22"
            quick_result = self.run_verifier(["--quick", "--output-dir", "build/ci-evidence/phase22"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            self.write_text(root, "build/ci-evidence/phase22/redacted-summary.md", "private key\ncutover complete\n")

            # Act
            result = self.run_verifier(["--security-only", "--output-dir", "build/ci-evidence/phase22"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private key", result.stdout)
        self.assertIn("cutover complete", result.stdout)

    def test_quick_rejects_symlink_before_deleting_output(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_quick_ready_metadata(root)
            output_dir = root / "build/ci-evidence/phase22"
            output_dir.mkdir(parents=True)
            self.write_text(root, "build/ci-evidence/phase22/keep.txt", "keep\n")
            (output_dir / "linked").symlink_to(root)

            # Act
            result = self.run_verifier(["--quick", "--output-dir", "build/ci-evidence/phase22"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stdout)
            self.assertTrue((output_dir / "keep.txt").is_file())


if __name__ == "__main__":
    unittest.main()
