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
VERIFIER = ROOT / "tools/bazel/phase6_verify.py"

REQUIRED_PRINTING_ROW_IDS = [
    "print-gcode-routing",
    "print-serial-start-pause-resume-cancel",
    "print-file-start-preview-stream-recovery",
    "print-planner-visible-flow",
    "print-buddy-gmcode-handlers",
]

REQUIRED_PRINTING_SOURCE_PATHS = [
    "lib/Marlin/",
    "lib/AddMarlin.cmake",
    "src/common/marlin_server.cpp",
    "src/common/marlin_client.cpp",
    "src/common/marlin_server_request.hpp",
    "src/common/marlin_client_queue.hpp",
    "src/common/marlin_vars.cpp",
    "src/common/serial_printing.cpp",
    "src/common/gcode/",
    "src/marlin_stubs/gcode.cpp",
]


class Phase6VerifierTest(unittest.TestCase):
    def run_verifier(self, args: list[str], maybe_root: Path | None = None) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase6_verify.py"
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
        shutil.copy2(VERIFIER, root / "tools/bazel/phase6_verify.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def write_printing_manifest(
        self,
        root: Path,
        evidence_class: str = "source-audit",
        intentional_delta: str | None = "none",
    ) -> None:
        for source_path in REQUIRED_PRINTING_SOURCE_PATHS:
            if source_path.endswith("/"):
                (root / source_path).mkdir(parents=True, exist_ok=True)
            else:
                self.write_file(root, source_path, "// reference source")

        rows = [
            {
                "id": row_id,
                "requirement": "CORE-03",
                "source_paths": REQUIRED_PRINTING_SOURCE_PATHS,
                "reference_behavior": f"reference behavior for {row_id}",
                "print_surface": f"print surface for {row_id}",
                "evidence_class": evidence_class,
                "rust_surface": f"buddy-domain::{row_id}",
                "intentional_delta": intentional_delta,
            }
            for row_id in REQUIRED_PRINTING_ROW_IDS
        ]
        manifest = {
            "schema_version": 1,
            "phase": "06-printing-core-safety-and-feature-gates",
            "phase_lifecycle_id": "6-2026-06-04T09-48-48",
            "printing_contracts": rows,
        }
        self.write_file(
            root,
            "tools/bazel/manifests/phase6_printing_core.json",
            json.dumps(manifest),
        )

    def test_help_lists_phase6_modes(self) -> None:
        result = self.run_verifier(["--help"])

        self.assertEqual(result.returncode, 0, msg=result.stdout)
        for flag in [
            "--quick",
            "--all",
            "--manifests-only",
            "--printing-only",
            "--safety-only",
            "--features-only",
            "--concerns-only",
        ]:
            self.assertIn(flag, result.stdout)

    def test_manifests_only_reports_missing_manifest(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            result = self.run_verifier(["--manifests-only"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required file: tools/bazel/manifests/phase6_printing_core.json", result.stdout)

    def test_printing_only_rejects_invalid_evidence_class(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_printing_manifest(root, evidence_class="hardware passed")

            result = self.run_verifier(["--printing-only"], maybe_root=root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence_class", result.stdout)

    def test_printing_only_accepts_null_intentional_delta(self) -> None:
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_printing_manifest(root, intentional_delta=None)

            result = self.run_verifier(["--printing-only"], maybe_root=root)

        self.assertEqual(result.returncode, 0, msg=result.stdout)


if __name__ == "__main__":
    unittest.main()
