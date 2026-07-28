from __future__ import annotations

from phase33_maintainer_decision_inputs_cases_test import PHASE32_REGISTER_REF
class Phase33MaintainerDecisionInputsSecurityMixin:
    def test_demotion_decision_is_separate_from_readiness_and_evidence(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("demotion-row", decision_impact="demotion_decision_required", affected_gate="final-reference-demotion-allowed")])
        decisions_path = self.write_decisions(root, [self.decision("approve-demotion", "reference_demotion", "approve", [self.blocker_ref("demotion-row")])])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        demotion = self.read_json(root, "build/ci-evidence/phase33/demotion-decision-handoff.json")
        readiness_text = (root / "build/ci-evidence/phase33/readiness-decision-handoff.json").read_text(encoding="utf-8")
        manifest_text = (root / "build/ci-evidence/phase33/downstream-handoff-manifest.json").read_text(encoding="utf-8")
        self.assertEqual(demotion["authorization_state"], "approved-input-recorded")
        self.assertTrue(demotion["phase34_must_validate_readiness"])
        self.assertNotIn("demotion_allowed", readiness_text)
        self.assertNotIn("final_readiness_status", manifest_text)

    def test_conflicting_readiness_and_demotion_targets_fail_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(
            root,
            [
                self.blocker_row("readiness-row", severity="warning"),
                self.blocker_row(
                    "demotion-row",
                    decision_impact="demotion_decision_required",
                    affected_gate="final-reference-demotion-allowed",
                ),
            ],
        )
        newer_readiness_block = self.decision(
            "newer-readiness-block",
            "readiness",
            "block",
            [self.blocker_ref("readiness-row")],
            blocked_source_row_refs=[self.blocker_ref("readiness-row")],
        )
        newer_readiness_block["decision_timestamp"] = "2026-07-04T03:00:00Z"
        older_readiness_approve = self.decision("older-readiness-approve", "readiness", "approve", [self.blocker_ref("readiness-row")])
        older_readiness_approve["decision_timestamp"] = "2026-07-04T01:00:00Z"
        newer_demotion_reject = self.decision("newer-demotion-reject", "reference_demotion", "reject", [self.blocker_ref("demotion-row")])
        newer_demotion_reject["decision_timestamp"] = "2026-07-04T03:00:00Z"
        older_demotion_approve = self.decision("older-demotion-approve", "reference_demotion", "approve", [self.blocker_ref("demotion-row")])
        older_demotion_approve["decision_timestamp"] = "2026-07-04T01:00:00Z"
        decisions_path = self.write_decisions(
            root,
            [
                newer_readiness_block,
                newer_demotion_reject,
                older_readiness_approve,
                older_demotion_approve,
            ],
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conflicts with decision target", result.stdout)

    def test_green_evidence_does_not_create_any_approval(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [])

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        normalized = self.read_json(root, "build/ci-evidence/phase33/normalized-decision-records.json")
        readiness = self.read_json(root, "build/ci-evidence/phase33/readiness-decision-handoff.json")
        demotion = self.read_json(root, "build/ci-evidence/phase33/demotion-decision-handoff.json")
        self.assertEqual(normalized["rows"], [])
        self.assertEqual(readiness["handoff_state"], "blocked-pending-maintainer-input")
        self.assertEqual(demotion["authorization_state"], "blocked")

    def test_stale_lifecycle_unknown_type_unresolved_ref_and_malformed_ref_fail_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        cases = [
            self.write_decisions(root, [self.decision("stale-lifecycle", "readiness", "block", [self.blocker_ref("known-row")])], phase_lifecycle_id="stale"),
            self.write_decisions(root, [self.decision("unknown-type", "surprise", "approve", [self.blocker_ref("known-row")])]),
            self.write_decisions(root, [self.decision("unresolved-ref", "readiness", "block", [self.blocker_ref("missing-row")])]),
            self.write_decisions(root, [self.decision("malformed-ref", "readiness", "block", ["build/ci-evidence/phase32/../secret.json#known-row"])]),
        ]

        for decisions_path in cases:
            with self.subTest(decisions_path=decisions_path):
                # Act
                result = self.run_quick(root, decisions_path)

                # Assert
                self.assertNotEqual(result.returncode, 0)

    def test_custom_output_dir_manifest_paths_use_custom_root(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])

        # Act
        result = self.run_quick(root, output_dir="build/ci-evidence/phase33/retry")

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        manifest = self.read_json(root, "build/ci-evidence/phase33/retry/downstream-handoff-manifest.json")
        self.assertEqual(manifest["output_root"], "build/ci-evidence/phase33/retry")
        self.assertEqual(
            manifest["register_refs"]["normalized_decision_records"],
            "build/ci-evidence/phase33/retry/normalized-decision-records.json",
        )
        self.assertTrue((root / "build/ci-evidence/phase33/retry/readiness-decision-handoff.json").exists())

    def test_security_scan_rejects_secret_fields_path_traversal_and_approval_overclaims(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        secret_input = self.write_decisions(root, [self.decision("secret-input", "readiness", "block", [self.blocker_ref("known-row")])])
        secret_payload = self.read_json(root, secret_input)
        secret_payload["token_value"] = "redacted-test-token"
        self.write_json(root, secret_input, secret_payload)
        self.write_text(root, "build/ci-evidence/phase33/downstream-handoff-manifest.json", '{"demotion_allowed": true}\n')

        # Act
        input_result = self.run_quick(root, secret_input)
        output_result = self.run_temp_verifier(root, ["--security-only", "--output-dir", "build/ci-evidence/phase33"])
        path_result = self.run_temp_verifier(root, ["--quick", "--phase32-handoff", "../phase32/downstream-handoff-manifest.json"])

        # Assert
        self.assertNotEqual(input_result.returncode, 0)
        self.assertIn("token_value", input_result.stdout)
        self.assertNotEqual(output_result.returncode, 0)
        self.assertIn("demotion-allowed", output_result.stdout)
        self.assertNotEqual(path_result.returncode, 0)

    def test_security_scan_redacts_matched_bearer_text(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        secret_value = "Bearer ABCDEFGHIJK12345"
        decisions_path = self.write_decisions(
            root,
            [
                self.decision(
                    "bearer-secret",
                    "readiness",
                    "block",
                    [self.blocker_ref("known-row")],
                    rationale=f"Do not leak {secret_value}",
                )
            ],
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bearer-token", result.stdout)
        self.assertNotIn(secret_value, result.stdout)

    def test_security_scan_contract_allowlist_skips_contract_snapshots(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        quick_result = self.run_quick(root)
        module = self.load_module()
        snapshot = root / "build/ci-evidence/phase33/contract-snapshots/phase33_maintainer_decision_inputs_contract.json"

        # Act
        scan_result = self.run_temp_verifier(root, ["--security-only", "--output-dir", "build/ci-evidence/phase33"])

        # Assert
        self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
        self.assertIn("demotion_allowed", snapshot.read_text(encoding="utf-8"))
        self.assertNotIn("contract-snapshots/phase33_maintainer_decision_inputs_contract.json", module.EMITTED_OUTPUT_SCAN_ARTIFACTS)
        self.assertIn("downstream-handoff-manifest.json", module.EMITTED_OUTPUT_SCAN_ARTIFACTS)
        self.assertEqual(scan_result.returncode, 0, scan_result.stdout)

    def test_security_scan_checks_copied_phase32_data_snapshots(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        register = self.read_json(root, PHASE32_REGISTER_REF)
        register["token_value"] = "redacted-test-token"
        self.write_json(root, PHASE32_REGISTER_REF, register)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE32_REGISTER_REF, result.stdout)
        self.assertIn("token_value", result.stdout)
        self.assertFalse((root / "build/ci-evidence/phase33/contract-snapshots/phase32-blocker-register.json").exists())

    def test_quick_resets_stale_outputs_before_output_security_scan(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        self.write_text(root, "build/ci-evidence/phase33/downstream-handoff-manifest.json", '{"demotion_allowed": true}\n')

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        manifest = self.read_json(root, "build/ci-evidence/phase33/downstream-handoff-manifest.json")
        self.assertNotIn("demotion_allowed", manifest)

    def test_redacted_report_escapes_markdown_table_cells(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        decision = self.decision(
            "decision|line\n<b>html</b>",
            "readiness",
            "block",
            [self.blocker_ref("known-row")],
            blocked_source_row_refs=[self.blocker_ref("known-row")],
        )
        decisions_path = self.write_json(
            root,
            "build/ci-evidence/phase33-inputs/markdown-cells.json",
            {
                "schema_version": "1",
                "phase": "33-maintainer-decision-inputs",
                "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                "decisions": [decision],
            },
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        report = (root / "build/ci-evidence/phase33/redacted-maintainer-decision-report.md").read_text(encoding="utf-8")
        self.assertIn("decision\\|line &lt;b&gt;html&lt;/b&gt;", report)
        self.assertNotIn("<b>html</b>", report)

    def test_wiring_requires_bazel_root_workflow_and_just_entries(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_temp_verifier(root, ["--wiring-only"])

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase33_verify", result.stdout)


__all__ = ["Phase33MaintainerDecisionInputsSecurityMixin"]
