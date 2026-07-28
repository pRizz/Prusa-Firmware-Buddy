from __future__ import annotations

from phase34_test_support import *


class Phase34FinalReadinessSourceFailureMixin:
    def test_missing_phase31_manifest_replaces_seeded_prior_authority(self) -> None:
        def remove_manifest(root: Path) -> None:
            (root / PHASE31_MANIFEST).unlink()

        self.assert_source_failure_replaces_prior_authority(
            remove_manifest,
            "phase31-input-invalid",
        )

    def test_malformed_phase31_receipt_replaces_seeded_prior_authority(self) -> None:
        def corrupt_receipt(root: Path) -> None:
            manifest = self.read_json(root, PHASE31_MANIFEST)
            receipt_ref = manifest["receipt_refs"][0]
            (root / receipt_ref).write_text("{", encoding="utf-8")

        self.assert_source_failure_replaces_prior_authority(
            corrupt_receipt,
            "phase31-input-invalid",
        )

    def test_invalid_utf8_phase31_manifest_replaces_seeded_prior_authority(
        self,
    ) -> None:
        def corrupt_manifest(root: Path) -> None:
            (root / PHASE31_MANIFEST).write_bytes(b"\xff")

        self.assert_source_failure_replaces_prior_authority(
            corrupt_manifest,
            "phase31-input-invalid",
        )

    def test_phase31_receipt_read_error_replaces_seeded_prior_authority(
        self,
    ) -> None:
        self.assert_injected_read_failure_replaces_prior_authority(
            "build/ci-evidence/phase31/stream-receipts/receipt-0.json",
            "phase31-input-invalid",
        )

    def test_malformed_phase33_handoff_replaces_seeded_prior_authority(self) -> None:
        def corrupt_handoff(root: Path) -> None:
            (root / PHASE33_HANDOFF).write_text("{", encoding="utf-8")

        self.assert_source_failure_replaces_prior_authority(
            corrupt_handoff,
            "phase33-handoff-invalid",
        )

    def test_invalid_utf8_phase33_handoff_replaces_seeded_prior_authority(
        self,
    ) -> None:
        def corrupt_handoff(root: Path) -> None:
            (root / PHASE33_HANDOFF).write_bytes(b"\xff")

        self.assert_source_failure_replaces_prior_authority(
            corrupt_handoff,
            "phase33-handoff-invalid",
        )

    def test_phase33_register_read_error_replaces_seeded_prior_authority(
        self,
    ) -> None:
        self.assert_injected_read_failure_replaces_prior_authority(
            "build/ci-evidence/phase33/normalized-decision-records.json",
            "phase33-normalized-decisions-invalid",
        )

    def test_invalid_normalized_decisions_replace_seeded_prior_authority(self) -> None:
        def invalidate_decisions(root: Path) -> None:
            self.write_json(
                root,
                "build/ci-evidence/phase33/normalized-decision-records.json",
                {"rows": [{"decision_id": "incomplete-decision"}]},
            )

        self.assert_source_failure_replaces_prior_authority(
            invalidate_decisions,
            "phase33-normalized-decisions-invalid",
        )

    def test_stale_readiness_input_replaces_seeded_prior_authority(self) -> None:
        def stale_readiness(root: Path) -> None:
            relative_path = (
                "build/ci-evidence/phase33/readiness-decision-handoff.json"
            )
            readiness = self.read_json(root, relative_path)
            readiness["phase_lifecycle_id"] = "stale-phase33-lifecycle"
            self.write_json(root, relative_path, readiness)

        self.assert_source_failure_replaces_prior_authority(
            stale_readiness,
            "phase33-readiness-input-invalid",
        )

    def test_invalid_register_digest_input_replaces_seeded_prior_authority(self) -> None:
        def corrupt_register(root: Path) -> None:
            (
                root
                / "build/ci-evidence/phase33/decision-validation-report.json"
            ).write_text("{", encoding="utf-8")

        self.assert_source_failure_replaces_prior_authority(
            corrupt_register,
            "phase33-register-invalid",
        )

    def test_malformed_phase32_register_replaces_seeded_prior_authority(self) -> None:
        def corrupt_register(root: Path) -> None:
            (root / PHASE32_REGISTER).write_text("{", encoding="utf-8")

        self.assert_source_failure_replaces_prior_authority(
            corrupt_register,
            "phase32-blocker-register-invalid",
        )

    def test_missing_demotion_handoff_replaces_seeded_prior_authority(self) -> None:
        def remove_demotion(root: Path) -> None:
            (
                root
                / "build/ci-evidence/phase33/demotion-decision-handoff.json"
            ).unlink()

        self.assert_source_failure_replaces_prior_authority(
            remove_demotion,
            "phase33-demotion-input-invalid",
        )

    def test_source_failure_publication_validates_stage_and_canonical_bundle(
        self,
    ) -> None:
        # Arrange
        module = self.load_module()
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        relative_output = Path(OUTPUT_DIR)
        full_output = root / relative_output

        # Act
        with (
            mock.patch.object(
                module,
                "validate_generated_outputs",
                wraps=module.validate_generated_outputs,
            ) as generated_validation,
            mock.patch.object(
                module,
                "validate_output_security",
                wraps=module.validate_output_security,
            ) as security_validation,
        ):
            module.publish_source_failure_bundle(
                root,
                relative_output,
                full_output,
                "phase31-input-invalid",
            )

        # Assert
        self.assertEqual(generated_validation.call_count, 2)
        self.assertEqual(security_validation.call_count, 2)
        self.assertTrue(
            (full_output / "final-readiness-run-manifest.json").is_file()
        )

    def test_source_failure_stage_rename_failure_keeps_seeded_prior_authority_guarded(
        self,
    ) -> None:
        # Arrange
        module = self.load_module()
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_fixture(root, self.required_stream_receipts(), [])
        self.seed_prior_phase34_authority(root)
        (root / PHASE31_MANIFEST).unlink()
        canonical = root / OUTPUT_DIR

        def fail_after_prior_move(
            full_output: Path,
            staging_output: Path,
        ) -> None:
            backup = full_output.with_name(
                f".{full_output.name}.source-failure-backup"
            )
            full_output.rename(backup)
            try:
                raise module.VerificationError(
                    "injected blocked stage rename failure"
                )
            finally:
                backup.rename(full_output)

        # Act
        with mock.patch.object(
            module,
            "replace_output_with_staging",
            side_effect=fail_after_prior_move,
        ):
            with self.assertRaises(module.VerificationError):
                module.run_quick(
                    root,
                    "build/ci-evidence/phase31",
                    PHASE33_HANDOFF,
                    OUTPUT_DIR,
                )

        # Assert
        self.assertTrue((canonical / "stale-prior-authority.json").is_file())
        state = module.load_publication_state(root)
        self.assertIsNotNone(state)
        self.assertEqual(state["authority_state"], "blocked")
        self.assertEqual(
            state["reason_category"],
            "phase31-input-invalid",
        )
        with self.assertRaises(module.VerificationError):
            module.run_security_scan(root, OUTPUT_DIR)

    def test_absolute_path_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(root, "--quick", "--phase31-output-dir", root.as_posix())

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase31-input-invalid", result.stdout)

    def test_parent_traversal_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(root, "--quick", "--phase33-handoff", "../phase33/handoff.json")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase33-handoff-invalid", result.stdout)

    def test_wrong_input_root_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(root, "--quick", "--phase31-output-dir", "build/ci-evidence/phase30")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase31-input-invalid", result.stdout)

    def test_input_output_overlap_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(
            root,
            "--quick",
            "--phase33-handoff",
            f"{OUTPUT_DIR}/downstream-handoff-manifest.json",
            "--output-dir",
            OUTPUT_DIR,
        )

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase33-handoff-invalid", result.stdout)

    def test_symlink_escape_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside = root / "outside"
        outside.mkdir()
        output = root / OUTPUT_DIR
        output.parent.mkdir(parents=True, exist_ok=True)
        output.symlink_to(outside, target_is_directory=True)

        # Act
        result = self.run_verifier(root, "--quick")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink escape", result.stdout)

    def test_nested_phase33_register_symlink_escapes_are_rejected(self) -> None:
        register_names = [
            "normalized-decision-records.json",
            "readiness-decision-handoff.json",
            "demotion-decision-handoff.json",
        ]
        for register_name in register_names:
            with self.subTest(register=register_name):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [])
                register_path = root / "build/ci-evidence/phase33" / register_name
                outside_path = root / "outside" / register_name
                outside_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(register_path, outside_path)
                register_path.unlink()
                register_path.symlink_to(outside_path)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                expected_reason = {
                    "normalized-decision-records.json":
                    "phase33-normalized-decisions-invalid",
                    "readiness-decision-handoff.json":
                    "phase33-readiness-input-invalid",
                    "demotion-decision-handoff.json":
                    "phase33-demotion-input-invalid",
                }[register_name]
                self.assertIn(expected_reason, result.stdout)

    def test_nested_phase32_register_symlink_escape_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [])
        register_path = root / PHASE32_REGISTER
        outside_path = root / "outside/blocker-register.json"
        outside_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(register_path, outside_path)
        register_path.unlink()
        register_path.symlink_to(outside_path)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase32-blocker-register-invalid", result.stdout)

    def test_security_rejects_secret_fields_unsafe_refs_and_overclaim_markers(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        receipt = self.receipt("simulator", source_ref)
        receipt["token_value"] = "redacted-test-token"
        self.write_fixture(root, [receipt], [])

        # Act
        secret_result = self.run_quick(root)
        self.write_text(root, f"{OUTPUT_DIR}/redacted-readiness-report.md", "cutover verdict approved\n")
        marker_result = self.run_verifier(root, "--security-only", "--output-dir", OUTPUT_DIR)

        # Assert
        self.assertNotEqual(secret_result.returncode, 0)
        self.assertIn("phase31-input-invalid", secret_result.stdout)
        self.assertNotEqual(marker_result.returncode, 0)
        self.assertIn("cutover-verdict", marker_result.stdout)

    def test_lifecycle_and_source_contract_mismatch_fail_closed(self) -> None:
        cases = [
            ("phase31", "phase_lifecycle_id", "stale"),
            ("phase33", "artifact_name", "wrong-contract"),
        ]
        for target, field, value in cases:
            with self.subTest(target=target):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [])
                relative_path = PHASE31_MANIFEST if target == "phase31" else PHASE33_HANDOFF
                payload = self.read_json(root, relative_path)
                payload[field] = value
                self.write_json(root, relative_path, payload)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)

    def test_generated_report_derives_from_packet_and_ledger(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [])

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        packet = self.read_json(root, f"{OUTPUT_DIR}/final-readiness-packet.json")
        ledger = self.read_json(root, f"{OUTPUT_DIR}/readiness-coverage-ledger.json")
        report = (root / OUTPUT_DIR / "redacted-readiness-report.md").read_text(encoding="utf-8")
        self.assertEqual(packet["ledger_rows"], ledger["rows"])
        self.assertIn(f"readiness_state: {packet['readiness_state']}", report)
        self.assertIn(f"gate_state: {packet['demotion_dry_run']['gate_state']}", report)

    def test_wiring_requires_bazel_root_workflow_and_just_entries(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        result = self.run_verifier(root, "--wiring-only")

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase34_verify", result.stdout)



__all__ = ["Phase34FinalReadinessSourceFailureMixin"]
