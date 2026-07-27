from __future__ import annotations

from phase26_release_test_support import *


class Phase26ReleaseSigningUpstreamEvidenceFailureTests:

    def test_missing_release_row_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            release_input = self.write_release_input(root, rows[:-1])

            # Act
            result = self.run_verifier(
                ["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("release input missing rows", result.stdout)

    def test_duplicate_release_row_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            rows[-1] = dict(rows[0])
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(
                ["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("duplicates row id", result.stdout)

    def test_unknown_release_row_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            rows[-1]["id"] = "rel-unknown-artifact"
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(
                ["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("uses unknown row id: rel-unknown-artifact",
                          result.stdout)

    def test_passed_release_row_requires_phase26_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            del rows[0]["release_run_id"]
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(
                ["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("release_run_id must be a non-empty string",
                          result.stdout)

    def test_signing_rows_require_key_identity_and_signing_mode(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            for row in rows:
                if row["id"] == "rel-bbf-firmware-package":
                    del row["key_identity_ref"]
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(
                ["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("key_identity_ref must be a non-empty string",
                          result.stdout)

    def test_passed_redaction_boundary_requires_phase20_metadata(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            for row in rows:
                if row["id"] == "rel-contract-traceability-redaction-boundary":
                    del row["redaction_scan"]
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(
                ["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("redaction_scan must be a non-empty string",
                          result.stdout)

    def test_release_candidate_cannot_pass_phase26(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            for row in rows:
                row["proof_class"] = "release-candidate"
            release_input = self.write_release_input(root, rows)

            # Act
            result = self.run_verifier(
                ["--quick", "--release-input", release_input], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("release-candidate cannot pass Phase 26",
                          result.stdout)

    def test_local_smoke_and_template_only_cannot_pass_phase26(self) -> None:
        for proof_class in ["local-smoke", "template-only"]:
            with self.subTest(proof_class=proof_class):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    rows = self.complete_release_rows(root)
                    for row in rows:
                        row["proof_class"] = proof_class
                    release_input = self.write_release_input(root, rows)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--release-input", release_input],
                        maybe_root=root)

                    # Assert
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn("cannot pass with proof_class",
                                  result.stdout)

    def test_secret_tainted_input_aborts_before_output_root_exists(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            rows[0][
                "private_key"] = "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----"
            release_input = self.write_release_input(root, rows)
            output_root = root / DEFAULT_OUTPUT_DIR

            # Act
            result = self.run_verifier([
                "--quick", "--release-input", release_input, "--output-dir",
                DEFAULT_OUTPUT_DIR
            ],
                                       maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("forbidden release evidence marker", result.stdout)
            self.assertFalse(output_root.exists())

    def test_camel_case_forbidden_security_field_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            template = self.read_json(root, PHASE20_TEMPLATE)
            template["privateKey"] = "redacted-placeholder"
            self.write_json(root, PHASE20_TEMPLATE, template)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("privateKey", result.stdout)

    def test_unsupported_release_input_field_aborts_before_output_root_exists(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            rows[0]["apiToken"] = "operator-metadata-that-must-not-be-retained"
            release_input = self.write_release_input(root, rows)
            output_root = root / DEFAULT_OUTPUT_DIR

            # Act
            result = self.run_verifier([
                "--quick", "--release-input", release_input, "--output-dir",
                DEFAULT_OUTPUT_DIR
            ],
                                       maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn(
                "release input contains unsupported fields: apiToken",
                result.stdout)
            self.assertFalse(output_root.exists())

    def test_unsupported_subject_digest_field_aborts_before_output_root_exists(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            rows = self.complete_release_rows(root)
            subject_digests = rows[0]["subject_digests"]
            self.assertIsInstance(subject_digests, list)
            subject_digests[0][
                "apiToken"] = "operator-metadata-that-must-not-be-retained"
            release_input = self.write_release_input(root, rows)
            output_root = root / DEFAULT_OUTPUT_DIR

            # Act
            result = self.run_verifier([
                "--quick", "--release-input", release_input, "--output-dir",
                DEFAULT_OUTPUT_DIR
            ],
                                       maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn(
                "subject_digests[0] contains unsupported fields: apiToken",
                result.stdout)
            self.assertFalse(output_root.exists())

    def test_output_dir_rejects_absolute_parent_and_symlink_escapes(
            self) -> None:
        for bad_output_dir in ["/tmp/phase26", "../phase26"]:
            with self.subTest(output_dir=bad_output_dir):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    # Act
                    result = self.run_verifier(
                        ["--quick", "--output-dir", bad_output_dir],
                        maybe_root=root)

                    # Assert
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn("--output-dir must", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            outside = root / "outside-output"
            outside.mkdir()
            output_parent = root / "build/ci-evidence"
            output_parent.mkdir(parents=True)
            (output_parent / "phase26").symlink_to(outside,
                                                   target_is_directory=True)

            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("symlink escape risk", result.stdout)

    def test_output_dir_regular_file_is_rejected_without_traceback(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            output_root = root / DEFAULT_OUTPUT_DIR
            output_root.parent.mkdir(parents=True, exist_ok=True)
            output_root.write_text("not a directory\n", encoding="utf-8")

            # Act
            result = self.run_verifier(
                ["--quick", "--output-dir", DEFAULT_OUTPUT_DIR],
                maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("--output-dir exists and is not a directory",
                          result.stdout)
            self.assertNotIn("Traceback", result.stdout)

    def test_invalid_upstream_row_guards_block_or_reject(self) -> None:
        reject_cases = [
            ("criterion_id", "final-ci-evidence",
             "criterion_id must be final-simulator-evidence"),
            ("requirement_ids", ["EVID-02"],
             "requirement_ids must be ['EVID-01']"),
            ("phase", "24-hardware-media-and-safety-evidence-execution",
             "phase must be 23-simulator-evidence-execution"),
            ("phase_lifecycle_id", "",
             "phase_lifecycle_id must be a non-empty string"),
            ("status", "exception-requested", "status is invalid"),
            ("artifact_refs", ["../unsafe.json"], "ref escapes allowed roots"),
        ]
        for field, value, expected_message in reject_cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    row_paths = self.write_valid_upstream_rows(root)
                    row = self.read_json(root, row_paths["phase23"])
                    row[field] = value
                    self.write_json(root, row_paths["phase23"], row)

                    # Act
                    result = self.run_verifier(
                        [
                            "--quick", "--phase23-simulator-row",
                            row_paths["phase23"]
                        ],
                        maybe_root=root,
                    )

                    # Assert
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(expected_message, result.stdout)

        block_cases = [
            ("redaction_status", "failed", "redaction-failed"),
            ("source_ref_status", "failed", "source-ref-failed"),
        ]
        for field, value, expected_reason in block_cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    row_paths = self.write_valid_upstream_rows(root)
                    row = self.read_json(root, row_paths["phase23"])
                    row[field] = value
                    self.write_json(root, row_paths["phase23"], row)

                    # Act
                    result = self.run_verifier(
                        [
                            "--quick",
                            "--output-dir",
                            DEFAULT_OUTPUT_DIR,
                            "--phase23-simulator-row",
                            row_paths["phase23"],
                        ],
                        maybe_root=root,
                    )

                    # Assert
                    self.assertEqual(result.returncode, 0, result.stdout)
                    rows = self.read_json(
                        root,
                        f"{DEFAULT_OUTPUT_DIR}/upstream-result-row-table.json"
                    )["rows"]
                    simulator_row = next(
                        row for row in rows
                        if row["criterion_id"] == "final-simulator-evidence")
                    self.assertEqual(simulator_row["status"], "blocked")
                    self.assertIn(expected_reason,
                                  simulator_row["failure_reason"])

    def test_redaction_failure_is_hard_blocker(self) -> None:
        # Arrange
        module = self.load_verifier_module()
        requirement = {
            "acceptable_statuses": ["passed"],
            "exception_coverable_statuses": ["failed", "blocked"],
            "hard_blocking_statuses": ["rejected-redaction"],
        }
        row = {
            "criterion_id": "final-release-artifact-signing-evidence",
            "status": "passed",
            "redaction_status": "failed",
            "source_ref_status": "passed",
            "source_lifecycle_status": "current",
            "failure_reason": "none",
            "maintainer_state": "pending",
        }

        # Act
        normalized = module.normalize_upstream_row(row, requirement)

        # Assert
        self.assertEqual(normalized["status"], "blocked")
        self.assertIn("redaction-failed", normalized["failure_reason"])
        self.assertEqual(normalized["maintainer_state"], "blocked")

    def test_lifecycle_and_source_ref_failures_block_rows(self) -> None:
        module = self.load_verifier_module()
        requirement = {
            "acceptable_statuses": ["passed"],
            "exception_coverable_statuses": ["failed", "blocked"],
            "hard_blocking_statuses": ["rejected-redaction"],
        }
        cases = [
            ("source_ref_status", "invalid", "source-ref-failed"),
            ("source_lifecycle_status", "stale", "lifecycle-mismatch"),
        ]
        for field, value, expected_reason in cases:
            with self.subTest(field=field):
                # Arrange
                row = {
                    "criterion_id": "final-ci-evidence",
                    "status": "passed",
                    "redaction_status": "passed",
                    "source_ref_status": "passed",
                    "source_lifecycle_status": "current",
                    "failure_reason": "none",
                    "maintainer_state": "pending",
                }
                row[field] = value

                # Act
                normalized = module.normalize_upstream_row(row, requirement)

                # Assert
                self.assertEqual(normalized["status"], "blocked")
                self.assertIn(expected_reason, normalized["failure_reason"])
                self.assertEqual(normalized["maintainer_state"], "blocked")

    def test_exception_coverable_status_does_not_become_passed(self) -> None:
        # Arrange
        module = self.load_verifier_module()
        requirement = {
            "acceptable_statuses": ["passed"],
            "exception_coverable_statuses": ["failed"],
            "hard_blocking_statuses": ["rejected-redaction"],
        }
        row = {
            "criterion_id": "final-ci-evidence",
            "status": "failed",
            "redaction_status": "passed",
            "source_ref_status": "passed",
            "source_lifecycle_status": "current",
            "exception_status": "exception-approved",
            "failure_reason": "failed source row",
            "maintainer_state": "pending",
        }

        # Act
        normalized = module.normalize_upstream_row(row, requirement)

        # Assert
        self.assertEqual(normalized["status"], "failed")
        self.assertEqual(normalized["exception_status"], "exception-approved")
        self.assertNotEqual(normalized["status"], "passed")

    def test_wiring_only_rejects_missing_phase26_source_ref_filegroup(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(
                encoding="utf-8")
            self.write_file(
                root, "tools/bazel/BUILD.bazel",
                tools_build.replace('name = "phase26_source_ref_manifests"',
                                    'name = "phase26_source_refs_missing"'))

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("phase26_source_ref_manifests", result.stdout)

    def test_wiring_only_rejects_workflow_order_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            workflow = (root / "tools/bazel/rust_workflow.sh").read_text(
                encoding="utf-8")
            workflow = workflow.replace(
                "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --wiring-only\n    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26",
                "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26\n    python3 tools/bazel/phase26_release_signing_upstream_evidence.py --wiring-only",
            )
            self.write_file(root, "tools/bazel/rust_workflow.sh", workflow)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("must run --wiring-only before --quick",
                          result.stdout)

    def test_wiring_only_rejects_just_order_drift(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_wiring_files(root)
            justfile = (root / "justfile").read_text(encoding="utf-8")
            justfile = justfile.replace(
                "phase26-verify:\n    bazel run //tools/bazel:phase26_verify_tests\n    bazel run //tools/bazel:phase26_verify",
                "phase26-verify:\n    bazel run //tools/bazel:phase26_verify\n    bazel run //tools/bazel:phase26_verify_tests",
            )
            self.write_file(root, "justfile", justfile)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("must run tests before verifier", result.stdout)
