#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, (ROOT / "tools/bazel").as_posix())

import phase38_cutover_workflow as workflow
from phase38_test_support import blocked_authority


class GuardStateTests(unittest.TestCase):

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.guard = self.root / workflow.AUTHORITY_GUARD
        self.guard.parent.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def assert_guard_blocked(
        self,
        maybe_guard_ref: Path | None = None,
    ) -> None:
        with self.assertRaises(workflow.WorkflowError) as raised:
            workflow.require_clear_authority_guard(
                self.root,
                maybe_guard_ref or workflow.AUTHORITY_GUARD,
            )
        self.assertEqual(
            raised.exception.reason_category,
            "phase35-authority-guard-blocking",
        )

    def test_present_valid_guard_is_blocking(self) -> None:
        # Arrange
        self.guard.write_text(
            json.dumps(workflow.authority_guard_payload()),
            encoding="utf-8",
        )

        # Act / Assert
        self.assert_guard_blocked()

    def test_malformed_guard_is_blocking(self) -> None:
        # Arrange
        self.guard.write_text("{", encoding="utf-8")

        # Act / Assert
        self.assert_guard_blocked()

    def test_unreadable_guard_is_blocking(self) -> None:
        # Arrange
        self.guard.write_text("{}", encoding="utf-8")

        # Act / Assert
        with patch.object(Path, "read_text", side_effect=PermissionError):
            self.assert_guard_blocked()

    def test_lifecycle_stale_guard_is_blocking(self) -> None:
        # Arrange
        payload = workflow.authority_guard_payload()
        payload["phase_lifecycle_id"] = "35-stale"
        self.guard.write_text(json.dumps(payload), encoding="utf-8")

        # Act / Assert
        self.assert_guard_blocked()

    def test_absolute_guard_path_is_blocking(self) -> None:
        # Arrange
        absolute_guard = self.root / "absolute-guard.json"

        # Act / Assert
        self.assert_guard_blocked(absolute_guard)

    def test_traversal_guard_path_is_blocking(self) -> None:
        # Arrange
        traversal_guard = Path("build/ci-evidence/../guard.json")

        # Act / Assert
        self.assert_guard_blocked(traversal_guard)

    def test_symlink_escape_guard_is_blocking(self) -> None:
        # Arrange
        external = self.root / "external.json"
        external.write_text("{}", encoding="utf-8")
        self.guard.symlink_to(external)

        # Act / Assert
        self.assert_guard_blocked()

    def test_wrong_root_guard_is_blocking(self) -> None:
        # Arrange
        wrong_root = Path("build/other/.phase35-authority-guard.json")

        # Act / Assert
        self.assert_guard_blocked(wrong_root)

    def test_non_directory_guard_parent_is_blocking(self) -> None:
        # Arrange
        self.guard.parent.rmdir()
        (self.root / "build/ci-evidence").write_text(
            "not-a-directory",
            encoding="utf-8",
        )

        # Act / Assert
        self.assert_guard_blocked()


class CoordinatorTests(unittest.TestCase):

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_phase35_runs_after_nonzero_phase34_with_valid_blocked_bundle(
        self,
    ) -> None:
        # Arrange
        calls: list[str] = []

        def publish_attempt(_root: Path, _attempt_id: str) -> None:
            calls.append("publish-workflow-attempt")

        def publish_guard(_root: Path) -> None:
            calls.append("publish-phase35-guard")

        def run_phase34(
            _root: Path,
            _attempt_id: str,
        ) -> workflow.CommandOutcome:
            calls.append("phase34")
            return workflow.CommandOutcome(4, "phase31-input-invalid")

        def validate_phase34(
            _root: Path,
            _attempt_id: str,
            _outcome: workflow.CommandOutcome,
        ) -> bool:
            calls.append("validate-phase34")
            return True

        def run_phase35(
            _root: Path,
            _outcome: workflow.CommandOutcome,
        ) -> workflow.CommandOutcome:
            calls.append("phase35")
            return workflow.CommandOutcome(0, "none")

        def clear_attempt(_root: Path, _attempt_id: str) -> None:
            calls.append("clear-workflow-attempt")

        # Act
        with (
            patch.object(
                workflow,
                "publish_workflow_attempt_marker",
                side_effect=publish_attempt,
            ),
            patch.object(
                workflow.phase35,
                "publish_authority_guard",
                side_effect=publish_guard,
            ),
            patch.object(workflow, "_run_phase34", side_effect=run_phase34),
            patch.object(
                workflow,
                "_phase34_effective_authority_is_valid",
                side_effect=validate_phase34,
            ),
            patch.object(workflow, "_run_phase35", side_effect=run_phase35),
            patch.object(
                workflow,
                "_load_candidate_final_authority",
                return_value=blocked_authority(),
            ),
            patch.object(
                workflow,
                "clear_workflow_attempt_marker",
                side_effect=clear_attempt,
            ),
            patch.object(
                workflow,
                "load_final_authority",
                return_value=blocked_authority(),
            ),
        ):
            result = workflow.coordinate_workflow(self.root)

        # Assert
        self.assertEqual(
            calls,
            [
                "publish-workflow-attempt",
                "publish-phase35-guard",
                "phase34",
                "validate-phase34",
                "phase35",
                "clear-workflow-attempt",
            ],
        )
        self.assertEqual(result.status, 4)

    def test_phase35_source_failure_preserves_nonzero_status_and_blocked_authority(
        self,
    ) -> None:
        # Arrange
        def publish_blocked_source_error(
            root: Path,
            _phase34_output: str,
            _phase35_output: str,
        ) -> None:
            workflow.phase35.publish_failed_phase34_bundle(root)
            raise workflow.phase35.VerificationError(
                "Phase 35 source validation failed",
                "source-artifact-malformed",
            )

        # Act
        with (
            patch.object(
                workflow,
                "_run_phase34",
                return_value=workflow.CommandOutcome(0, "none"),
            ),
            patch.object(
                workflow,
                "_phase34_effective_authority_is_valid",
                return_value=True,
            ),
            patch.object(
                workflow.phase35,
                "run_quick",
                side_effect=publish_blocked_source_error,
            ),
        ):
            result = workflow.coordinate_workflow(self.root)

        # Assert
        candidate = workflow._load_candidate_final_authority(self.root)
        self.assertTrue(candidate.available)
        self.assertEqual(candidate.verdict, "blocked")
        self.assertEqual(candidate.readiness_state, "blocked")
        self.assertEqual(result.phase35_status, 1)
        self.assertEqual(result.status, 1)
        self.assertEqual(
            result.reason_category,
            "source-artifact-malformed",
        )
        self.assertFalse(result.final_authority_available)
        self.assertFalse(result.production_cutover_planning)
        self.assertFalse(result.reference_demotion_authorized)

    def test_phase35_does_not_run_when_phase34_bundle_is_invalid(self) -> None:
        # Arrange
        phase35 = unittest.mock.Mock()

        # Act
        with (
            patch.object(
                workflow,
                "_run_phase34",
                return_value=workflow.CommandOutcome(
                    4,
                    "phase31-input-invalid",
                ),
            ),
            patch.object(
                workflow,
                "_phase34_effective_authority_is_valid",
                return_value=False,
            ),
            patch.object(workflow, "_run_phase35", phase35),
        ):
            result = workflow.coordinate_workflow(self.root)

        # Assert
        phase35.assert_not_called()
        self.assertNotEqual(result.status, 0)
        self.assertEqual(
            result.reason_category,
            "phase34-authority-invalid",
        )
        with self.assertRaises(workflow.WorkflowError):
            workflow.require_clear_authority_guard(self.root)

    def test_guard_publication_failure_skips_both_producers(self) -> None:
        # Arrange
        phase34 = unittest.mock.Mock()
        phase35 = unittest.mock.Mock()

        # Act
        with (
            patch.object(
                workflow.phase35,
                "publish_authority_guard",
                side_effect=workflow.phase35.VerificationError(
                    "injected guard failure",
                ),
            ),
            patch.object(workflow, "_run_phase34", phase34),
            patch.object(workflow, "_run_phase35", phase35),
        ):
            result = workflow.coordinate_workflow(self.root)

        # Assert
        phase34.assert_not_called()
        phase35.assert_not_called()
        self.assertNotEqual(result.status, 0)
        self.assertEqual(
            result.reason_category,
            "phase35-authority-guard-blocking",
        )
        self.assertFalse(result.final_authority_available)

    def test_guard_precreation_failure_keeps_seeded_prior_authority_persistently_blocked(
        self,
    ) -> None:
        # Arrange
        output = self.root / workflow.PHASE35_OUTPUT
        output.mkdir(parents=True)
        WorkflowAttemptMarkerSecurityTests.write_json(
            output / "cutover-decision-run-manifest.json",
            {"generation_state": "complete"},
        )
        WorkflowAttemptMarkerSecurityTests.write_json(
            output / "cutover-decision.json",
            {
                "phase_lifecycle_id": workflow.phase35.PHASE_LIFECYCLE_ID,
                "cutover_verdict": "approved",
            },
        )
        WorkflowAttemptMarkerSecurityTests.write_json(
            output / "next-milestone-route.json",
            {
                "phase_lifecycle_id": workflow.phase35.PHASE_LIFECYCLE_ID,
                "source_verdict": "approved",
                "route": "production-cutover-planning",
            },
        )

        # Act
        with patch.object(
            workflow.phase35,
            "touch_guard",
            side_effect=OSError("injected pre-create failure"),
        ):
            result = workflow.coordinate_workflow(self.root)

        # Assert
        self.assertNotEqual(result.status, 0)
        self.assertFalse((self.root / workflow.AUTHORITY_GUARD).exists())
        marker = workflow.load_workflow_attempt_marker(self.root)
        self.assertIsNotNone(marker)
        self.assertEqual(marker["authority_state"], "blocked")
        authority = workflow.load_final_authority(self.root)
        self.assertFalse(authority.available)
        self.assertEqual(
            authority.reason_category,
            "workflow-attempt-blocking",
        )


class WorkflowAttemptMarkerSecurityTests(unittest.TestCase):

    ATTEMPT_ID = "b" * 32

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.output = self.root / workflow.PHASE35_OUTPUT
        self.output.mkdir(parents=True)
        self.write_json(
            self.output / "cutover-decision-run-manifest.json",
            {"generation_state": "complete"},
        )
        self.write_json(
            self.output / "cutover-decision.json",
            {
                "phase_lifecycle_id": workflow.phase35.PHASE_LIFECYCLE_ID,
                "cutover_verdict": "approved",
                "readiness_state": "unblocked",
                "demotion_decision_validation_state": "missing",
                "demotion_decision_state": "missing",
                "demotion_gate_state": "blocked",
            },
        )
        self.write_json(
            self.output / "next-milestone-route.json",
            {
                "phase_lifecycle_id": workflow.phase35.PHASE_LIFECYCLE_ID,
                "source_verdict": "approved",
                "route": "production-cutover-planning",
                "requires_fresh_cutover_decision": False,
            },
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def write_json(path: Path, payload: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def publish(self) -> None:
        workflow.publish_workflow_attempt_marker(
            self.root,
            self.ATTEMPT_ID,
        )

    def assert_seeded_authority_blocked(self) -> None:
        authority = workflow.load_final_authority(self.root)
        self.assertFalse(authority.available)
        self.assertEqual(
            authority.reason_category,
            "workflow-attempt-blocking",
        )
        shell = self.root / workflow.WORKFLOW_ATTEMPT_SHELL
        self.assertTrue(
            shell.exists()
            or shell.is_symlink()
            or shell.parent.exists()
            or shell.parent.is_symlink()
        )
        self.assertNotIn(self.root.as_posix(), authority.reason_category)

    def test_payload_precreation_failure_leaves_blocking_shell(self) -> None:
        # Arrange
        with patch.object(
            workflow,
            "write_workflow_attempt_payload",
            side_effect=OSError("attacker-controlled-payload"),
        ):
            # Act
            with self.assertRaises(workflow.WorkflowError):
                self.publish()

        # Assert
        self.assert_seeded_authority_blocked()

    def test_atomic_replacement_failure_leaves_blocking_shell(self) -> None:
        # Arrange
        with patch.object(
            workflow,
            "replace_workflow_attempt_payload",
            side_effect=OSError("attacker-controlled-path"),
        ):
            # Act
            with self.assertRaises(workflow.WorkflowError):
                self.publish()

        # Assert
        self.assert_seeded_authority_blocked()

    def test_each_missing_required_field_is_blocking(self) -> None:
        for missing_field in workflow.WORKFLOW_ATTEMPT_FIELDS:
            with self.subTest(missing_field=missing_field):
                # Arrange
                shell = self.root / workflow.WORKFLOW_ATTEMPT_SHELL
                payload = workflow.workflow_attempt_payload(self.ATTEMPT_ID)
                payload.pop(missing_field)
                self.write_json(
                    shell / workflow.WORKFLOW_ATTEMPT_PAYLOAD_NAME,
                    payload,
                )

                # Act / Assert
                self.assert_seeded_authority_blocked()
                shutil.rmtree(shell)

    def test_malformed_json_is_blocking(self) -> None:
        # Arrange
        payload = (
            self.root
            / workflow.WORKFLOW_ATTEMPT_SHELL
            / workflow.WORKFLOW_ATTEMPT_PAYLOAD_NAME
        )
        payload.parent.mkdir(parents=True)
        payload.write_text("{", encoding="utf-8")

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_unreadable_payload_is_blocking(self) -> None:
        # Arrange
        self.publish()
        payload = (
            self.root
            / workflow.WORKFLOW_ATTEMPT_SHELL
            / workflow.WORKFLOW_ATTEMPT_PAYLOAD_NAME
        )
        original_read_text = Path.read_text

        def fail_payload_read(candidate: Path, *args, **kwargs):
            if candidate == payload:
                raise PermissionError("attacker-controlled-permission")
            return original_read_text(candidate, *args, **kwargs)

        # Act / Assert
        with patch.object(Path, "read_text", fail_payload_read):
            self.assert_seeded_authority_blocked()

    def test_absolute_marker_ref_is_rejected(self) -> None:
        # Arrange
        marker_ref = Path("/tmp/phase38-workflow-attempt")

        # Act / Assert
        with self.assertRaises(workflow.WorkflowError):
            workflow.validate_workflow_attempt_path(self.root, marker_ref)

    def test_traversal_marker_ref_is_rejected(self) -> None:
        # Arrange
        marker_ref = Path("build/ci-evidence/../phase38-attempt")

        # Act / Assert
        with self.assertRaises(workflow.WorkflowError):
            workflow.validate_workflow_attempt_path(self.root, marker_ref)

    def test_wrong_root_marker_ref_is_rejected(self) -> None:
        # Arrange
        marker_ref = Path("build/other/.phase38-workflow-attempt")

        # Act / Assert
        with self.assertRaises(workflow.WorkflowError):
            workflow.validate_workflow_attempt_path(self.root, marker_ref)

    def test_symlinked_marker_is_blocking(self) -> None:
        # Arrange
        outside = self.root / "outside-state"
        outside.mkdir()
        shell = self.root / workflow.WORKFLOW_ATTEMPT_SHELL
        shell.parent.mkdir(parents=True, exist_ok=True)
        shell.symlink_to(outside, target_is_directory=True)

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_symlinked_parent_is_blocking(self) -> None:
        # Arrange
        outside = self.root / "outside-parent"
        build = self.root / "build"
        build.rename(outside)
        build.symlink_to(outside, target_is_directory=True)

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_regular_file_shell_is_blocking(self) -> None:
        # Arrange
        shell = self.root / workflow.WORKFLOW_ATTEMPT_SHELL
        shell.parent.mkdir(parents=True, exist_ok=True)
        shell.write_text("not-a-directory", encoding="utf-8")

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_fifo_shell_is_blocking(self) -> None:
        # Arrange
        shell = self.root / workflow.WORKFLOW_ATTEMPT_SHELL
        shell.parent.mkdir(parents=True, exist_ok=True)
        os.mkfifo(shell)

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_non_directory_parent_is_blocking(self) -> None:
        # Arrange
        parent = self.root / workflow.WORKFLOW_ATTEMPT_SHELL.parent
        shutil.rmtree(parent)
        parent.parent.mkdir(parents=True, exist_ok=True)
        parent.write_text("not-a-directory", encoding="utf-8")

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_cleanup_failure_keeps_workflow_marker_blocking(self) -> None:
        # Arrange
        self.publish()

        # Act
        with patch.object(
            workflow,
            "remove_workflow_attempt_shell",
            side_effect=OSError("attacker-controlled-cleanup"),
        ):
            with self.assertRaises(workflow.WorkflowError):
                workflow.clear_workflow_attempt_marker(
                    self.root,
                    self.ATTEMPT_ID,
                )

        # Assert
        self.assert_seeded_authority_blocked()


if __name__ == "__main__":
    unittest.main()
