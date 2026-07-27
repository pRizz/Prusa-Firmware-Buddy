from __future__ import annotations

from phase27_decision_test_support import *


class Phase27RetainedCodeAcceptanceDecisionsFailureTests:

    def test_contract_only_rejects_decision_axis_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_json(root, CONTRACT)
            contract["decision_axes"] = [
                axis for axis in contract["decision_axes"]
                if axis != "hard_failure_state"
            ]
            self.write_json(root, CONTRACT, contract)

            # Act
            result = self.run_verifier(["--contract-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_axes", result.stdout)

    def test_security_only_rejects_forbidden_contract_fields(self) -> None:
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

    def test_accepted_retained_decision_requires_evidence_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            retained_row = maintainer_input["retained_code_decisions"][0]
            retained_row["evidence_refs"] = []
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence_refs must not be empty", result.stdout)

    def test_passed_final_decision_requires_iso_utc_timestamp(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            final_row = maintainer_input["final_readiness_decisions"][0]
            final_row["decision_timestamp"] = "not-a-timestamp"
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_timestamp must be ISO UTC", result.stdout)

    def test_approved_exception_requires_evidence_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            retained_row = maintainer_input["retained_code_decisions"][2]
            retained_row["decision"] = "exception"
            retained_row["exception"] = {
                "scope":
                "phase27 test exception scope",
                "rationale":
                "Temporary exception is explicitly documented for maintainer review.",
                "approver":
                "phase27-test-maintainer",
                "approver_role":
                retained_row["approver_role"],
                "affected_printer_or_release_surface":
                "print core retained packet",
                "mitigation_or_follow_up":
                "Track exception in Phase 28 readiness review.",
                "expiry_or_review_trigger":
                "Phase 28 reference-demotion decision",
                "evidence_refs": [],
                "residual_risk":
                "Exception residual risk accepted for test input.",
            }
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exception evidence_refs must not be empty",
                      result.stdout)

    def test_final_decision_required_fields_include_decision_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            del maintainer_input["final_readiness_decisions"][0]["decision_id"]
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_id", result.stdout)

    def test_duplicate_final_decision_ids_are_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            duplicate = maintainer_input["final_readiness_decisions"][0][
                "decision_id"]
            maintainer_input["final_readiness_decisions"][1][
                "decision_id"] = duplicate
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate decision_id", result.stdout)

    def test_final_decision_reject_cannot_pass(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            final_row = maintainer_input["final_readiness_decisions"][0]
            final_row["decision"] = "reject"
            final_row["status"] = "passed"
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status passed requires decision approve", result.stdout)

    def test_final_decision_approve_requires_passed_status(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            final_row = maintainer_input["final_readiness_decisions"][0]
            final_row["decision"] = "approve"
            final_row["status"] = "failed"
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approve requires status passed", result.stdout)

    def test_maintainer_input_lifecycle_metadata_drift_is_rejected(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            maintainer_input["phase_lifecycle_id"] = "27-stale-lifecycle"
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase_lifecycle_id", result.stdout)

    def test_sensitive_role_mismatch_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            network_row = next(
                row for row in maintainer_input["final_readiness_decisions"] if
                row["criterion_id"] == "final-live-network-transfer-evidence")
            network_row["approver_role"] = "release-maintainer"
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sensitive_role_policy", result.stdout)

    def test_retained_packet_approver_role_must_match_phase18_packet(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            maintainer_input = self.complete_maintainer_input(root)
            runtime_row = next(
                row for row in maintainer_input["retained_code_decisions"]
                if row["packet_id"] == "packet-freertos-runtime")
            runtime_row["approver_role"] = "cutover-maintainer"
            input_path = self.write_maintainer_input(root, maintainer_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--maintainer-input", input_path], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approver_role must be runtime-maintainer",
                      result.stdout)

    def test_missing_phase26_row_table_reports_generation_command(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase26_release_signing_upstream_evidence.py --quick",
                      result.stdout)

    def test_output_root_symlink_escape_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
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

    def test_security_scan_rejects_no_demotion_output_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase26_rows(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            handoff = self.read_json(
                root, f"{DEFAULT_OUTPUT_DIR}/phase28-handoff-manifest.json")
            handoff["demotion_allowed"] = True
            self.write_json(
                root, f"{DEFAULT_OUTPUT_DIR}/phase28-handoff-manifest.json",
                handoff)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("demotion_allowed", result.stdout)

    def test_wiring_only_rejects_missing_phase26_precondition(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            workflow = (root / "tools/bazel/rust_workflow.sh").read_text(
                encoding="utf-8")
            workflow = workflow.replace(
                "  phase27_verify)\n"
                "    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --wiring-only\n"
                "    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26\n"
                "    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27\n",
                "  phase27_verify)\n"
                "    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --wiring-only\n"
                "    python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27\n",
            )
            self.write_text(root, "tools/bazel/rust_workflow.sh", workflow)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase26_release_signing_upstream_evidence.py --quick",
                      result.stdout)

    def test_wiring_only_rejects_just_recipe_order_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            just_text = (root / "justfile").read_text(encoding="utf-8")
            just_text = just_text.replace(
                "phase27-verify:\n    bazel run //tools/bazel:phase27_verify_tests\n    bazel run //tools/bazel:phase27_verify\n",
                "phase27-verify:\n    bazel run //tools/bazel:phase27_verify\n    bazel run //tools/bazel:phase27_verify_tests\n",
            )
            self.write_text(root, "justfile", just_text)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must run tests before verifier", result.stdout)
