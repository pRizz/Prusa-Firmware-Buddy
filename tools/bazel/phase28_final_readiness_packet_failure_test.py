from __future__ import annotations

from phase28_readiness_test_support import *


class Phase28FinalReadinessPacketFailureTests:

    def test_contract_rejects_canonical_criterion_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["readiness_policy"]["canonical_phase18_criteria"] = [
                row for row in contract["readiness_policy"]
                ["canonical_phase18_criteria"] if row != "final-ci-evidence"
            ]
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical_phase18_criteria", result.stdout)

    def test_contract_rejects_phase18_authority_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase18_contract = self.read_json(root, PHASE18_CONTRACT)
            phase18_contract["upstream_result_requirements"] = [
                row for row in phase18_contract["upstream_result_requirements"]
                if row["criterion_id"] != "final-ci-evidence"
            ]
            self.write_json(root, PHASE18_CONTRACT, phase18_contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical_phase18_criteria", result.stdout)

    def test_contract_rejects_generated_artifact_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["generated_artifacts"].append("unexpected-output.json")
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated_artifacts", result.stdout)

    def test_missing_inputs_report_generation_commands(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase26_release_signing_upstream_evidence.py --quick",
                      result.stdout)

    def test_hard_blocker_runs_before_exception_coverage(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase26_rows = self.phase26_rows(root)
            phase26_rows[0]["status"] = "failed"
            phase26_rows[0]["redaction_status"] = "failed"
            phase26_rows[0][
                "failure_reason"] = "redaction-failed while exception metadata exists"
            phase27_rows = self.phase27_final_rows(phase26_rows)
            phase27_rows[0]["status"] = "exception-approved"
            phase27_rows[0]["decision"] = "exception"
            phase27_rows[0]["exception_state"] = "approved-exception"
            phase27_rows[0]["exception"] = self.exception_metadata(
                str(phase26_rows[0]["criterion_id"]))
            self.write_phase_inputs(root, phase26_rows, phase27_rows)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            table = self.read_json(
                root,
                f"{DEFAULT_OUTPUT_DIR}/normalized-readiness-criteria-table.json"
            )
            row = next(row for row in table["rows"]
                       if row["criterion_id"] == "final-ci-evidence")
            self.assertEqual(row["readiness_effect"], "blocked-hard-failure")
            self.assertIn("redaction-failed", row["hard_failure_reasons"])

    def test_source_hard_blocker_status_fields_outrank_exception_coverage(
            self) -> None:
        cases = [
            ("overclaim_status", "failed", "overclaim-failed"),
            ("unsafe_ref_status", "failed", "unsafe-ref"),
        ]
        for field, value, expected_reason in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    phase26_rows = self.phase26_rows(root)
                    phase26_rows[0]["status"] = "failed"
                    phase26_rows[0][field] = value
                    phase26_rows[0][
                        "failure_reason"] = "approved exception metadata must not cover hard blockers"
                    phase27_rows = self.phase27_final_rows(phase26_rows)
                    phase27_rows[0]["status"] = "exception-approved"
                    phase27_rows[0]["decision"] = "exception"
                    phase27_rows[0]["exception_state"] = "approved-exception"
                    phase27_rows[0]["exception"] = self.exception_metadata(
                        str(phase26_rows[0]["criterion_id"]))
                    self.write_phase_inputs(root, phase26_rows, phase27_rows)

                    # Act
                    result = self.run_verifier(["--quick"], maybe_root=root)

                    # Assert
                    self.assertEqual(result.returncode, 0, result.stdout)
                    table = self.read_json(
                        root,
                        f"{DEFAULT_OUTPUT_DIR}/normalized-readiness-criteria-table.json"
                    )
                    row = next(row for row in table["rows"]
                               if row["criterion_id"] == "final-ci-evidence")
                    self.assertEqual(row["readiness_effect"],
                                     "blocked-hard-failure")
                    self.assertIn(expected_reason, row["hard_failure_reasons"])

    def test_explicit_demotion_approval_is_rejected_when_readiness_blocked(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            phase26_rows = self.phase26_rows(root)
            phase26_rows[0]["status"] = "blocked"
            phase26_rows[0]["failure_reason"] = "CI remains blocked for test."
            phase27_rows = self.phase27_final_rows(phase26_rows)
            phase27_rows[0]["status"] = "blocked"
            self.write_phase_inputs(root, phase26_rows, phase27_rows)
            decision_path = self.write_json(root, "demotion-decision.json",
                                            self.demotion_decision("approved"))

            # Act
            result = self.run_verifier(
                ["--quick", "--demotion-decision-input", decision_path],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("final_readiness_status unblocked", result.stdout)

    def test_lifecycle_and_source_ref_drift_are_rejected(self) -> None:
        cases = [
            ("source_lifecycle_status", "stale",
             "source_lifecycle_status must be current"),
            ("source_ref_status", "invalid",
             "source_ref_status must be passed"),
        ]
        for field, value, expected in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    phase26_rows = self.phase26_rows(root)
                    phase26_rows[0][field] = value
                    self.write_phase_inputs(root, phase26_rows)

                    # Act
                    result = self.run_verifier(["--quick"], maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_incomplete_demotion_metadata_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            decision = self.demotion_decision("blocked")
            del decision["approver"]
            decision_path = self.write_json(root, "demotion-decision.json",
                                            decision)

            # Act
            result = self.run_verifier(
                ["--quick", "--demotion-decision-input", decision_path],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approver", result.stdout)

    def test_output_root_symlink_escape_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            outside = root / "outside-output"
            outside.mkdir()
            output_root = root / DEFAULT_OUTPUT_DIR
            output_root.parent.mkdir(parents=True, exist_ok=True)
            output_root.symlink_to(outside, target_is_directory=True)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink escape", result.stdout)

    def test_output_root_regular_file_is_rejected_without_traceback(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            output_root = root / DEFAULT_OUTPUT_DIR
            output_root.parent.mkdir(parents=True, exist_ok=True)
            output_root.write_text("not a directory\n", encoding="utf-8")

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--output-dir exists and is not a directory",
                      result.stdout)
        self.assertNotIn("Traceback", result.stdout)

    def test_security_scan_rejects_secret_fields_and_generated_overclaims(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["private_key"] = "redacted-test-value"
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private_key", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            self.write_text(
                root, f"{DEFAULT_OUTPUT_DIR}/redacted-readiness-report.md",
                "reference demotion approved\n")

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reference demotion approved", result.stdout)

    def test_security_scan_rejects_generated_demotion_overclaim_field(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase_inputs(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            packet = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json")
            packet["demotion_allowed"] = True
            self.write_json(
                root, f"{DEFAULT_OUTPUT_DIR}/final-readiness-packet.json",
                packet)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("demotion_allowed", result.stdout)

    def test_verifier_does_not_use_shell_or_inline_interpreters(self) -> None:
        # Arrange
        source = VERIFIER.read_text(encoding="utf-8")

        # Act / Assert
        for forbidden in ["shell=True", "bash -c", "python -c", "node -e"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_wiring_only_rejects_phase28_workflow_order_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            workflow = (root / "tools/bazel/rust_workflow.sh").read_text(
                encoding="utf-8")
            workflow = workflow.replace(
                "    python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only\n"
                "    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26\n",
                "    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26\n"
                "    python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only\n",
            )
            self.write_text(root, "tools/bazel/rust_workflow.sh", workflow)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase28_verify command order", result.stdout)

    def test_wiring_only_rejects_just_recipe_order_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            just_text = (root / "justfile").read_text(encoding="utf-8")
            just_text = just_text.replace(
                "phase28-verify:\n    bazel run //tools/bazel:phase28_verify_tests\n    bazel run //tools/bazel:phase28_verify\n",
                "phase28-verify:\n    bazel run //tools/bazel:phase28_verify\n    bazel run //tools/bazel:phase28_verify_tests\n",
            )
            self.write_text(root, "justfile", just_text)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must run tests before verifier", result.stdout)
