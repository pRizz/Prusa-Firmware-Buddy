#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase8_verify.py"

PHASE = "08-local-interface-and-workflow-parity"
PHASE_LIFECYCLE_ID = "8-2026-06-13T16-58-45"
PHASE_DIR = ".planning/phases/08-local-interface-and-workflow-parity"

REQUIRED_WORKFLOW_ROW_IDS = [
    "screen-stack-home-bootstrap",
    "screen-stack-bounded-fixed-storage",
    "dialog-fsm-display-config",
    "menu-settings-and-home-entry",
    "print-preview-entry",
    "print-control-pause",
    "print-control-resume",
    "print-control-cancel-abort-request",
    "print-control-stop-confirmation",
    "print-control-reprint",
    "setup-selftest-calibration-wizards",
    "connect-registration-local-entry",
    "prusalink-credential-local-display",
    "warning-redscreen-error-surfaces",
]

SEMANTIC_ACTION_BY_WORKFLOW_ROW = {
    "print-preview-entry": "preview",
    "print-control-pause": "pause",
    "print-control-resume": "resume",
    "print-control-cancel-abort-request": "cancel",
    "print-control-stop-confirmation": "stop",
    "print-control-reprint": "reprint",
}

REQUIRED_LAYOUT_ROW_IDS = [
    "display-class-selectors",
    "mini-240x320-gui-defaults",
    "large-480x320-gui-defaults",
    "menu-layout-display-differences",
    "print-preview-layout-240x320",
    "print-preview-layout-480x320",
    "print-progress-layout-240x320",
    "print-progress-layout-480x320",
    "localized-text-font-contracts",
    "warning-dialog-layout",
    "redscreen-bsod-error-layout",
    "connect-registration-layout",
]

REQUIRED_CONCERN_ROW_IDS = [
    "concern-cl-008-home-screen-flash-start",
    "concern-cl-011-crash-dump-warning-surface",
    "concern-cl-003-generated-gui-resource-drift",
    "concern-cl-019-tracked-font-header-churn",
]

FORBIDDEN_MARKERS = [
    "password_value",
    "token_value",
    "certificate_bytes",
    "raw_dump",
    "ram_bytes",
    "BEGIN PRIVATE KEY",
    "eeprom_bytes",
]

RUST_API_STRINGS = [
    "DisplayClass",
    "GuiWorkflow",
    "GuiSurface",
    "GuiEvidenceClass",
    "GuiProofScope",
    "GuiParityRowId",
    "LocalizationSurface",
    "IntentionalDeltaStatus",
    "GuiSemanticAction",
    "GuiParityContract",
]

OVERCLAIM_STRINGS = [
    "hardware display verified locally",
    "physical LCD proof passed",
    "Connect TLS parity passed",
    "auxiliary runtime parity passed",
    "cutover evidence complete",
]


class Phase8VerifierTest(unittest.TestCase):
    def run_verifier(
        self,
        args: list[str],
        maybe_root: Path | None = None,
        maybe_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        root = maybe_root or ROOT
        verifier = root / "tools/bazel/phase8_verify.py"
        return subprocess.run(
            [sys.executable, verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=maybe_env,
        )

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        (root / "tools/bazel").mkdir(parents=True)
        if VERIFIER.exists():
            shutil.copy2(VERIFIER, root / "tools/bazel/phase8_verify.py")
        return temp_dir, root

    def write_file(self, root: Path, path: str, text: str = "") -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(text, encoding="utf-8")

    def write_source_paths(self, root: Path, paths: list[str]) -> None:
        for source_path in paths:
            if source_path.endswith("/"):
                (root / source_path).mkdir(parents=True, exist_ok=True)
                continue
            self.write_file(root, source_path, "// reference source")

    def workflow_row(self, root: Path, row_id: str) -> dict[str, object]:
        source_paths = [
            "src/gui/guimain.cpp",
            "src/gui/ScreenHandler.hpp",
            "src/gui/ScreenFactory.hpp",
            "src/gui/screen_home.cpp",
        ]
        self.write_source_paths(root, source_paths)
        row: dict[str, object] = {
            "id": row_id,
            "requirement_id": "IFCE-01",
            "reference_sources": source_paths,
            "reference_behavior": f"{row_id} source-backed GUI workflow behavior",
            "rust_surface": f"buddy-domain::gui::{row_id}",
            "display_classes": ["240x320", "480x320"],
            "evidence_class": "source-audit",
            "proof_scope": "local",
            "non_local_evidence": [
                "physical LCD refresh proof",
                "touch and encoder timing proof",
            ],
            "intentional_delta": "none",
        }
        maybe_action = SEMANTIC_ACTION_BY_WORKFLOW_ROW.get(row_id)
        if maybe_action is not None:
            row["semantic_action_id"] = maybe_action
        return row

    def write_gui_workflows_manifest(
        self,
        root: Path,
        maybe_rows: list[dict[str, object]] | None = None,
    ) -> None:
        rows = maybe_rows or [self.workflow_row(root, row_id) for row_id in REQUIRED_WORKFLOW_ROW_IDS]
        manifest = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "workflow_contracts": rows,
        }
        self.write_file(root, "tools/bazel/manifests/phase8_gui_workflows.json", json.dumps(manifest))

    def layout_row(self, root: Path, row_id: str) -> dict[str, object]:
        source_paths = [
            "include/guiconfig/GuiDefaults.hpp",
            "src/gui/fonts.hpp",
            "src/gui/resolution_240x320/screen_printing_layout.hpp",
            "src/gui/resolution_480x320/screen_printing_layout.hpp",
        ]
        self.write_source_paths(root, source_paths)
        display_classes = ["240x320", "480x320"]
        if "240x320" in row_id and "480x320" not in row_id:
            display_classes = ["240x320"]
        if "480x320" in row_id:
            display_classes = ["480x320"]
        if row_id == "display-class-selectors":
            display_classes = ["240x320", "480x320", "mock"]
        return {
            "id": row_id,
            "requirement_id": "IFCE-01",
            "reference_sources": source_paths,
            "reference_behavior": f"{row_id} display layout behavior",
            "rust_surface": f"buddy-domain::gui::{row_id}",
            "display_classes": display_classes,
            "layout_values": {
                "240x320": {"ScreenSize": "240x320"},
                "480x320": {"ScreenSize": "480x320"},
            },
            "evidence_class": "source-audit",
            "proof_scope": "local",
            "non_local_evidence": [
                "actual LCD rendering",
                "full translation overflow proof",
            ],
            "intentional_delta": "none",
        }

    def write_display_layouts_manifest(
        self,
        root: Path,
        maybe_rows: list[dict[str, object]] | None = None,
    ) -> None:
        rows = maybe_rows or [self.layout_row(root, row_id) for row_id in REQUIRED_LAYOUT_ROW_IDS]
        manifest = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "layout_contracts": rows,
        }
        self.write_file(root, "tools/bazel/manifests/phase8_display_layouts.json", json.dumps(manifest))

    def concern_row(self, root: Path, row_id: str) -> dict[str, object]:
        source_paths = [
            ".planning/phases/01-reference-baseline-and-safety-envelope/01-CONCERN-LEDGER.md",
            ".planning/codebase/CONCERNS.md",
            "src/gui/screen_home.cpp",
        ]
        self.write_source_paths(root, source_paths)
        concern_id = {
            "concern-cl-008-home-screen-flash-start": "CL-008",
            "concern-cl-011-crash-dump-warning-surface": "CL-011",
            "concern-cl-003-generated-gui-resource-drift": "CL-003",
            "concern-cl-019-tracked-font-header-churn": "CL-019",
        }[row_id]
        required_strings = ["phase7_resources.json", "phase7_generated_outputs.json", "src/gui/res/cc"]
        if concern_id == "CL-008":
            required_strings = ["no-op flash action", "event re-enable behavior", "src/gui/screen_home.cpp"]
        if concern_id == "CL-011":
            required_strings = [
                "Crash detected. Save it to USB?",
                "sensitive information",
                "no raw crash dump memory contents",
            ]
        return {
            "id": row_id,
            "concern_id": concern_id,
            "requirement_id": "IFCE-01",
            "reference_sources": source_paths,
            "disposition": "fix-during-rewrite" if concern_id != "CL-019" else "defer",
            "phase8_handling": f"{concern_id} handling keeps {' '.join(required_strings)} source-backed",
            "evidence_class": "source-audit" if concern_id in {"CL-008", "CL-011"} else "manifest-check",
            "proof_scope": "local",
            "intentional_delta": "none",
            "regression_guard": {
                "guard_type": "manifest-and-verifier-contract",
                "required_strings": required_strings,
                "expected_future_evidence": f"future evidence keeps {' '.join(required_strings)}",
            },
        }

    def write_concern_manifest(
        self,
        root: Path,
        maybe_rows: list[dict[str, object]] | None = None,
    ) -> None:
        rows = maybe_rows or [self.concern_row(root, row_id) for row_id in REQUIRED_CONCERN_ROW_IDS]
        manifest = {
            "schema_version": 1,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "concerns": rows,
        }
        self.write_file(root, "tools/bazel/manifests/phase8_concern_dispositions.json", json.dumps(manifest))

    def write_rust_api_surface(
        self,
        root: Path,
        gui_text: str | None = None,
        lib_text: str | None = None,
    ) -> None:
        self.write_file(
            root,
            "rust/crates/domain/src/gui.rs",
            gui_text
            or "\n".join(
                [
                    "pub enum DisplayClass {}",
                    "pub enum GuiWorkflow {}",
                    "pub enum GuiSurface {}",
                    "pub enum GuiEvidenceClass {}",
                    "pub enum GuiProofScope {}",
                    "pub struct GuiParityRowId;",
                    "pub enum LocalizationSurface {}",
                    "pub enum IntentionalDeltaStatus {}",
                    "pub enum GuiSemanticAction {}",
                    "pub struct GuiParityContract;",
                    'const COMMENT_ONLY: &str = "unsafe { unsafe fn";',
                    "// unsafe block should be ignored in comments",
                ]
            ),
        )
        self.write_file(
            root,
            "rust/crates/domain/src/lib.rs",
            lib_text
            or (
                "#![forbid(unsafe_code)]\n"
                "pub mod gui;\n"
                "pub use gui::{DisplayClass, GuiWorkflow, GuiSurface, GuiEvidenceClass, "
                "GuiProofScope, GuiParityRowId, LocalizationSurface, IntentionalDeltaStatus, "
                "GuiSemanticAction, GuiParityContract};\n"
            ),
        )

    def write_facade_files(self, root: Path) -> None:
        self.write_file(
            root,
            "BUILD.bazel",
            "\n".join(
                [
                    'filegroup(name = "phase8_local_interface_docs", srcs = [])',
                    'alias(name = "phase8_verify", actual = "//tools/bazel:phase8_verify")',
                    'alias(name = "phase8_verify_tests", actual = "//tools/bazel:phase8_verify_tests")',
                ]
            ),
        )
        self.write_file(
            root,
            "tools/bazel/BUILD.bazel",
            "\n".join(
                [
                    'shell_binary(name = "phase8_verify", src = "rust_workflow.sh", data = ["phase8_verify.py", "phase8_gui_workflows.json", "phase8_display_layouts.json", "phase8_concern_dispositions.json", "//:phase8_local_interface_docs", "//:rust_workspace_sources"])',
                    'shell_binary(name = "phase8_verify_tests", src = "rust_workflow.sh", data = ["phase8_verify.py", "phase8_verify_test.py"])',
                ]
            ),
        )
        self.write_file(
            root,
            "tools/bazel/rust_workflow.sh",
            "\n".join(
                [
                    'case "$command_name" in',
                    "  phase8_verify)",
                    "    python3 tools/bazel/phase8_verify.py --all",
                    "    ;;",
                    "  phase8_verify_tests)",
                    "    python3 tools/bazel/phase8_verify_test.py",
                    "    ;;",
                    "esac",
                    "",
                ]
            ),
        )
        self.write_file(
            root,
            "justfile",
            "phase8-verify:\n    bazel run //tools/bazel:phase8_verify_tests\n    bazel run //tools/bazel:phase8_verify\n",
        )

    def write_validation_contract(self, root: Path, extra_text: str = "") -> None:
        self.write_file(
            root,
            f"{PHASE_DIR}/08-VALIDATION.md",
            "\n".join(
                [
                    "---",
                    "status: complete",
                    "nyquist_compliant: true",
                    "wave_0_complete: true",
                    f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
                    "---",
                    "Quick run command",
                    "python3 tools/bazel/phase8_verify.py --quick",
                    "Full suite command",
                    "just phase8-verify",
                    "08-W0-01 Plan 01 green",
                    "08-W0-05 Plan 03 green",
                    "manual-hardware-required hardware-smoke simulator-flow remain non-local evidence",
                    extra_text,
                ]
            ),
        )

    def write_phase8_quick_surface(self, root: Path) -> None:
        self.write_gui_workflows_manifest(root)
        self.write_display_layouts_manifest(root)
        self.write_concern_manifest(root)
        self.write_rust_api_surface(root)
        self.write_facade_files(root)
        self.write_validation_contract(root)

    def test_requires_gui_semantic_action_ids(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [self.workflow_row(root, row_id) for row_id in REQUIRED_WORKFLOW_ROW_IDS]
            for row in rows:
                if row["id"] == "print-control-stop-confirmation":
                    row.pop("semantic_action_id")
            self.write_gui_workflows_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("print-control-stop-confirmation", result.stdout)
        self.assertIn("stop", result.stdout)

    def test_rejects_semantic_action_on_wrong_workflow(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [self.workflow_row(root, row_id) for row_id in REQUIRED_WORKFLOW_ROW_IDS]
            for row in rows:
                if row["id"] == "menu-settings-and-home-entry":
                    row["semantic_action_id"] = "pause"
            self.write_gui_workflows_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("menu-settings-and-home-entry", result.stdout)
        self.assertIn("print-control", result.stdout)

    def test_rejects_legacy_manifest_schema_fields(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [self.workflow_row(root, row_id) for row_id in REQUIRED_WORKFLOW_ROW_IDS]
            rows[0]["requirement"] = rows[0].pop("requirement_id")
            rows[0]["source_paths"] = rows[0].pop("reference_sources")
            self.write_gui_workflows_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requirement_id", result.stdout)
        self.assertIn("reference_sources", result.stdout)

    def test_rejects_display_layout_without_both_display_classes(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [self.layout_row(root, row_id) for row_id in REQUIRED_LAYOUT_ROW_IDS]
            for row in rows:
                if row["id"] == "menu-layout-display-differences":
                    row["display_classes"] = ["240x320"]
            self.write_display_layouts_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("menu-layout-display-differences", result.stdout)
        self.assertIn("480x320", result.stdout)

    def test_requires_cl008_and_crash_dump_concerns(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [
                self.concern_row(root, row_id)
                for row_id in REQUIRED_CONCERN_ROW_IDS
                if row_id != "concern-cl-008-home-screen-flash-start"
            ]
            for row in rows:
                if row["id"] == "concern-cl-011-crash-dump-warning-surface":
                    row["regression_guard"] = {
                        "guard_type": "sensitive-diagnostics-boundary",
                        "required_strings": ["Crash detected. Save it to USB?"],
                    }
            self.write_concern_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CL-008", result.stdout)
        self.assertIn("no raw crash dump memory contents", result.stdout)

    def test_rejects_secret_or_crash_dump_byte_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            self.write_validation_contract(root, extra_text=" ".join(FORBIDDEN_MARKERS))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("password_value", result.stdout)
        self.assertIn("BEGIN PRIVATE KEY", result.stdout)

    def test_requires_gui_rust_api_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            self.write_rust_api_surface(
                root,
                gui_text="pub enum GuiWorkflow {}\n",
                lib_text="#![forbid(unsafe_code)]\npub mod gui;\npub use gui::GuiWorkflow;\n",
            )

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        for needle in [
            "DisplayClass",
            "GuiParityRowId",
            "GuiEvidenceClass",
            "GuiParityContract",
            "GuiSemanticAction",
        ]:
            self.assertIn(needle, result.stdout)

    def test_rejects_phase8_overclaims(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            self.write_validation_contract(root, extra_text=" ".join(OVERCLAIM_STRINGS))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware display verified locally", result.stdout)
        self.assertIn("cutover evidence complete", result.stdout)

    def test_requires_bazel_and_just_wiring(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            self.write_file(root, "BUILD.bazel", 'alias(name = "phase8_verify")\n')
            self.write_file(root, "tools/bazel/BUILD.bazel", 'shell_binary(name = "phase8_verify")\n')
            self.write_file(root, "tools/bazel/rust_workflow.sh", 'case "$command_name" in esac\n')
            self.write_file(root, "justfile", "phase8-verify:\n    bazel run //tools/bazel:phase8_verify\n")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase8_verify_tests", result.stdout)
        self.assertIn("rust_workflow.sh", result.stdout)


if __name__ == "__main__":
    unittest.main()
