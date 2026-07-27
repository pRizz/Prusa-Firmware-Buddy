from __future__ import annotations

DEFAULT_OUTPUT_DIR = "build/ci-evidence/phase20"


class Phase20ReleaseCandidateArtifactsFailureTests:

    def test_quick_rejects_symlinked_output_root_before_deleting_target(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            victim_dir = root / "build/ci-evidence/phase20-victim"
            victim_dir.mkdir(parents=True)
            marker_path = victim_dir / "do-not-delete.txt"
            marker_path.write_text("victim target must survive\n",
                                   encoding="utf-8")
            output_root = root / DEFAULT_OUTPUT_DIR
            output_root.parent.mkdir(parents=True, exist_ok=True)
            output_root.symlink_to(victim_dir, target_is_directory=True)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--output-dir must stay under", result.stdout)
            self.assertTrue(output_root.is_symlink())
            self.assertTrue(victim_dir.is_dir())
            self.assertEqual(marker_path.read_text(encoding="utf-8"),
                             "victim target must survive\n")
            self.assertFalse(
                (victim_dir / "release-result-manifest.json").exists())

    def test_passed_result_rejects_local_smoke_and_template_only_proof(
            self) -> None:
        for proof_class in ["local-smoke", "template-only"]:
            with self.subTest(proof_class=proof_class):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows()
                    rows[0]["proof_class"] = proof_class
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(proof_class, result.stdout)

    def test_passed_release_input_requires_contract_declared_metadata(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            contract = self.read_contract(root)
            if contract is None:
                self.skipTest("contract fixture is unavailable")
            required_cases = self.required_metadata_cases(contract)

            for row_id, required_field in required_cases:
                with self.subTest(row_id=row_id,
                                  required_field=required_field):
                    rows = self.complete_release_rows(root)
                    target_row = next(row for row in rows
                                      if row["id"] == row_id)
                    target_row.pop(required_field, None)
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                    # Assert
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(required_field, result.stdout)

    def test_redaction_rejects_private_key_and_payload_fields(self) -> None:
        forbidden_fields = [
            "private_key",
            "raw_firmware_payload",
            "token",
            "password",
            "credential",
        ]
        for field_name in forbidden_fields:
            with self.subTest(field_name=field_name):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows()
                    rows[0][field_name] = "secret-material"
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field_name, result.stdout)

    def test_release_refs_reject_absolute_and_parent_traversal_paths(
            self) -> None:
        bad_refs = [
            "/tmp/phase20/artifact.bbf",
            "../phase20/artifact.bbf",
            "build/ci-evidence/phase19/release-result-manifest.json",
        ]
        for bad_ref in bad_refs:
            with self.subTest(bad_ref=bad_ref):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows()
                    rows[0]["artifact_refs"] = [bad_ref]
                    rows[0]["retention_refs"] = [bad_ref]
                    rows[0]["subject_digests"] = [{
                        "artifact_ref": bad_ref,
                        "sha256": "b" * 64
                    }]
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(bad_ref, result.stdout)

    def test_comparison_rows_require_exact_classification_metadata(
            self) -> None:
        required_fields = [
            "mismatch_class",
            "mismatch_reason",
            "owner_phase",
            "affected_artifact_surface",
            "residual_risk",
        ]
        for required_field in required_fields:
            with self.subTest(required_field=required_field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows()
                    rows[0].pop(required_field)
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(required_field, result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows()
            rows[0]["mismatch_class"] = "unclassified"
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(
                ["--quick", "--release-input", release_input], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unclassified", result.stdout)

    def test_passed_release_input_rejects_invalid_comparison_metadata_values(
            self) -> None:
        cases = [
            ("mismatch_class", "",
             "mismatch_class must be a non-empty string"),
            ("mismatch_reason", "",
             "mismatch_reason must be a non-empty string"),
            ("residual_risk", "", "residual_risk must be a non-empty string"),
            ("owner_phase", "19-aggregate-ci-evidence",
             "owner_phase must be 20-release-candidate-artifact-production"),
            ("affected_artifact_surface", "wrong-surface",
             "affected_artifact_surface must match contract row"),
        ]
        for field_name, bad_value, expected_message in cases:
            with self.subTest(field_name=field_name):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows(root)
                    rows[0][field_name] = bad_value
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_message, result.stdout)
