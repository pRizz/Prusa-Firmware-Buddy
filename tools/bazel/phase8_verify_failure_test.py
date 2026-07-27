#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase8_verify_test import *  # noqa: F403


class Phase8VerifierFailureTest(Phase8VerifierFixture, unittest.TestCase):

    def test_rejects_semantic_action_on_wrong_workflow(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [
                self.workflow_row(root, row_id)
                for row_id in REQUIRED_WORKFLOW_ROW_IDS
            ]
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
            rows = [
                self.workflow_row(root, row_id)
                for row_id in REQUIRED_WORKFLOW_ROW_IDS
            ]
            rows[0]["requirement"] = rows[0].pop("requirement_id")
            rows[0]["source_paths"] = rows[0].pop("reference_sources")
            self.write_gui_workflows_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requirement_id", result.stdout)
        self.assertIn("reference_sources", result.stdout)

    def test_rejects_absolute_reference_source_paths(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [
                self.workflow_row(root, row_id)
                for row_id in REQUIRED_WORKFLOW_ROW_IDS
            ]
            absolute_source = (root / "src/gui/guimain.cpp").as_posix()
            rows[0]["reference_sources"] = [absolute_source]
            self.write_gui_workflows_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reference source must be repo-relative", result.stdout)
        self.assertIn(absolute_source, result.stdout)

    def test_rejects_parent_traversal_reference_source_paths(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [
                self.workflow_row(root, row_id)
                for row_id in REQUIRED_WORKFLOW_ROW_IDS
            ]
            traversal_source = "src/gui/../gui/guimain.cpp"
            rows[0]["reference_sources"] = [traversal_source]
            self.write_gui_workflows_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reference source must be repo-relative", result.stdout)
        self.assertIn(traversal_source, result.stdout)

    def test_rejects_display_layout_without_both_display_classes(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [
                self.layout_row(root, row_id)
                for row_id in REQUIRED_LAYOUT_ROW_IDS
            ]
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

    def test_rejects_stale_warning_dialog_description_rect(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase8_quick_surface(root)
            rows = [
                self.layout_row(root, row_id)
                for row_id in REQUIRED_LAYOUT_ROW_IDS
            ]
            for row in rows:
                if row["id"] == "warning-dialog-layout":
                    row["layout_values"] = {
                        "240x320": {
                            "WarningDlgDescriptionRect": {
                                "x": 6,
                                "y": 112,
                                "width": 228,
                                "height": 268,
                            },
                        },
                        "480x320": {
                            "WarningDlgDescriptionRect": {
                                "x": 26,
                                "y": 182,
                                "width": 428,
                                "height": 256,
                            },
                        },
                    }
            self.write_display_layouts_manifest(root, maybe_rows=rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("warning-dialog-layout", result.stdout)
        self.assertIn("WarningDlgTextRect", result.stdout)

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
                        "required_strings":
                        ["Crash detected. Save it to USB?"],
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
            self.write_validation_contract(
                root, extra_text=" ".join(FORBIDDEN_MARKERS))

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
                lib_text=
                "#![forbid(unsafe_code)]\npub mod gui;\npub use gui::GuiWorkflow;\n",
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
            self.write_validation_contract(
                root, extra_text=" ".join(OVERCLAIM_STRINGS))

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hardware display verified locally", result.stdout)
        self.assertIn("cutover evidence complete", result.stdout)
