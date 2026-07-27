from __future__ import annotations


class Phase18CutoverReviewSecurityTests:

    def test_security_only_rejects_forbidden_contract_input_and_generated_markers(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["private_key"] = "redacted-test-value"
            self.write_contract(root, contract)

            # Act
            contract_result = self.run_verifier(["--security-only"],
                                                maybe_root=root)

            # Assert
            self.assertNotEqual(contract_result.returncode, 0)
            self.assertIn("private_key", contract_result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["password"] = "redacted-test-value"
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            input_result = self.run_verifier(
                ["--security-only", "--decision-input", "decision-input.json"],
                maybe_root=root)

            # Assert
            self.assertNotEqual(input_result.returncode, 0)
            self.assertIn("password", input_result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            self.write_file(
                root,
                "build/ci-evidence/phase18/redacted-readiness-report.md",
                "raw crash dump",
            )

            # Act
            generated_result = self.run_verifier(["--security-only"],
                                                 maybe_root=root)

        # Assert
        self.assertNotEqual(generated_result.returncode, 0)
        self.assertIn("raw crash dump", generated_result.stdout)

    def test_security_only_rejects_common_api_key_fields(self) -> None:
        for field in [
                "api_key",
                "access_token",
                "apiKey",
                "accessToken",
                "authorizationHeader",
                "signingKeyValue",
                "certificatePrivateMaterial",
                "rawFirmwarePayload",
                "rawCrashDump",
                "wifiPassword",
                "prusalinkPassword",
        ]:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    decision_input[field] = "redacted-test-value"
                    self.write_json(root, "decision-input.json",
                                    decision_input)

                    # Act
                    result = self.run_verifier([
                        "--security-only", "--decision-input",
                        "decision-input.json"
                    ],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field, result.stdout)

    def test_security_only_validates_upstream_results(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            upstream_results = self.complete_upstream_results(root)
            self.write_json(root, "upstream-results.json", upstream_results)

            # Act
            valid_result = self.run_verifier([
                "--security-only", "--upstream-results",
                "upstream-results.json"
            ],
                                             maybe_root=root)

            # Assert
            self.assertEqual(valid_result.returncode, 0, valid_result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            upstream_results = self.complete_upstream_results(root)
            upstream_results["api_key"] = "redacted-test-value"
            self.write_json(root, "upstream-results.json", upstream_results)

            # Act
            invalid_result = self.run_verifier([
                "--security-only", "--upstream-results",
                "upstream-results.json"
            ],
                                               maybe_root=root)

        # Assert
        self.assertNotEqual(invalid_result.returncode, 0)
        self.assertIn("api_key", invalid_result.stdout)

    def test_security_only_rejects_generated_camel_case_secret_fields(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["apiKey"] = "redacted-test-value"
            self.write_json(root,
                            "build/ci-evidence/phase18/run-manifest.json",
                            run_manifest)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("apiKey", result.stdout)

    def test_decision_input_rejects_narrative_secret_markers(self) -> None:
        cases = [
            "Authorization: Bearer redacted-test-value",
            "token: redacted-test-value",
            "password: redacted-test-value",
            "api_key: sk_test_redacted_value_123456",
            "api-key: sk_test_redacted_value_123456",
            "api key: sk_test_redacted_value_123456",
            "access_token: redacted-test-value",
            "credential value: redacted-test-value",
            "wifi_password: redacted-test-value",
        ]
        for marker in cases:
            with self.subTest(marker=marker):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    decision_input["retained_code_reviews"][0][
                        "residual_risk"] = marker
                    self.write_json(root, "decision-input.json",
                                    decision_input)

                    # Act
                    quick_result = self.run_verifier(
                        ["--quick", "--decision-input", "decision-input.json"],
                        maybe_root=root)
                    security_result = self.run_verifier(
                        [
                            "--security-only", "--decision-input",
                            "decision-input.json"
                        ],
                        maybe_root=root,
                    )
                    generated_retained_summary = (
                        root /
                        "build/ci-evidence/phase18/retained-code-acceptance-summary.json"
                    ).exists()

                    # Assert
                    self.assertNotEqual(quick_result.returncode, 0)
                    self.assertIn("forbidden marker", quick_result.stdout)
                    self.assertNotEqual(security_result.returncode, 0)
                    self.assertIn("forbidden marker", security_result.stdout)
                    self.assertFalse(generated_retained_summary)

    def test_generated_report_names_review_material_boundary(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            report = (root /
                      "build/ci-evidence/phase18/redacted-readiness-report.md"
                      ).read_text(encoding="utf-8")
            self.assertIn(
                "Review material only; machine-readable gate rows and maintainer decision input determine final status.",
                report,
            )
            self.assertIn("demotion_allowed: false", report)

    def test_security_only_rejects_generated_local_proof_and_retained_acceptance_overclaims(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["demotion_allowed"] = True
            self.write_json(root,
                            "build/ci-evidence/phase18/run-manifest.json",
                            run_manifest)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("demotion_allowed", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            normalized = self.read_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json"
            )
            normalized["results"][0]["status"] = "passed"
            self.write_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json",
                normalized)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("passed", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            normalized = self.read_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json"
            )
            normalized["results"][0]["demotion_status_allows_cutover"] = True
            self.write_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json",
                normalized)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("demotion_status_allows_cutover true", result.stdout)

        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            summary = self.read_json(
                root,
                "build/ci-evidence/phase18/retained-code-acceptance-summary.json"
            )
            summary["packets"][0]["status"] = "accepted"
            self.write_json(
                root,
                "build/ci-evidence/phase18/retained-code-acceptance-summary.json",
                summary)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("accepted", result.stdout)

    def test_security_only_rejects_non_boolean_generated_decision_input_flag(
            self) -> None:
        for value in ["false", None]:
            with self.subTest(value=value):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    quick_result = self.run_verifier(["--quick"],
                                                     maybe_root=root)
                    self.assertEqual(quick_result.returncode, 0,
                                     quick_result.stdout)
                    run_manifest = self.read_json(
                        root, "build/ci-evidence/phase18/run-manifest.json")
                    if value is None:
                        del run_manifest["decision_inputs_supplied"]
                    else:
                        run_manifest["decision_inputs_supplied"] = value
                    run_manifest["demotion_allowed"] = True
                    self.write_json(
                        root, "build/ci-evidence/phase18/run-manifest.json",
                        run_manifest)

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("decision_inputs_supplied must be boolean",
                              result.stdout)

    def test_security_only_rejects_generated_decision_input_claim_without_validated_input(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["decision_inputs_supplied"] = True
            run_manifest["demotion_allowed"] = True
            self.write_json(root,
                            "build/ci-evidence/phase18/run-manifest.json",
                            run_manifest)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "claims decision input without validated --decision-input",
            result.stdout)

    def test_security_only_rejects_generated_upstream_result_claim_without_validated_input(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["upstream_results_supplied"] = True
            run_manifest["demotion_allowed"] = True
            self.write_json(root,
                            "build/ci-evidence/phase18/run-manifest.json",
                            run_manifest)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "claims upstream results without validated --upstream-results",
            result.stdout)

    def test_security_only_rejects_generated_demotion_claim_without_complete_decision_input(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["decision_inputs_supplied"] = True
            run_manifest["demotion_allowed"] = True
            self.write_json(root,
                            "build/ci-evidence/phase18/run-manifest.json",
                            run_manifest)
            self.write_json(
                root,
                "decision-input.json",
                {
                    "decision_packet": {
                        "phase":
                        "18-retained-code-acceptance-and-cutover-review",
                        "phase_lifecycle_id": "18-2026-06-20T14-27-15",
                    },
                    "retained_code_reviews": [],
                    "final_criterion_decisions": [],
                },
            )

            # Act
            result = self.run_verifier(
                ["--security-only", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "demotion_allowed true requires complete decision input and upstream results",
            result.stdout)

    def test_security_only_rejects_generated_demotion_when_retained_reviews_block(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["decision_inputs_supplied"] = True
            run_manifest["demotion_allowed"] = True
            self.write_json(root,
                            "build/ci-evidence/phase18/run-manifest.json",
                            run_manifest)
            normalized = self.read_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json"
            )
            normalized["demotion_allowed"] = True
            self.write_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json",
                normalized)
            decision_input = self.complete_decision_input(root)
            for retained_review in decision_input["retained_code_reviews"]:
                retained_review["status"] = "blocked"
                retained_review[
                    "rationale"] = "Retained review remains blocked."
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--security-only", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "final-retained-code-acceptance has non-accepted retained reviews",
            result.stdout)

    def test_security_only_rejects_final_row_demotion_flag_mismatch_with_decision_input(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            upstream_results = self.complete_upstream_results(root)
            self.write_json(root, "decision-input.json", decision_input)
            self.write_json(root, "upstream-results.json", upstream_results)
            quick_result = self.run_verifier(
                [
                    "--quick", "--decision-input", "decision-input.json",
                    "--upstream-results", "upstream-results.json"
                ],
                maybe_root=root,
            )
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            normalized = self.read_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json"
            )
            normalized["results"][0]["demotion_status_allows_cutover"] = False
            self.write_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json",
                normalized)

            # Act
            result = self.run_verifier(
                [
                    "--security-only", "--decision-input",
                    "decision-input.json", "--upstream-results",
                    "upstream-results.json"
                ],
                maybe_root=root,
            )

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated final criterion demotion flag mismatch",
                      result.stdout)

    def test_security_only_rejects_retained_row_status_mismatch_with_decision_input(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            run_manifest["decision_inputs_supplied"] = True
            run_manifest["demotion_allowed"] = False
            self.write_json(root,
                            "build/ci-evidence/phase18/run-manifest.json",
                            run_manifest)
            summary = self.read_json(
                root,
                "build/ci-evidence/phase18/retained-code-acceptance-summary.json"
            )
            summary["packets"][0]["status"] = "accepted"
            self.write_json(
                root,
                "build/ci-evidence/phase18/retained-code-acceptance-summary.json",
                summary)
            decision_input = self.complete_decision_input(root)
            for retained_review in decision_input["retained_code_reviews"]:
                retained_review["status"] = "blocked"
                retained_review[
                    "rationale"] = "Retained review remains blocked."
            for final_decision in decision_input["final_criterion_decisions"]:
                if final_decision[
                        "criterion_id"] == "final-retained-code-acceptance":
                    final_decision["status"] = "blocked"
                    final_decision[
                        "rationale"] = "Retained-code acceptance remains blocked."
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--security-only", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated retained-code packet status mismatch",
                      result.stdout)

    def test_security_only_rejects_normalized_top_level_demotion_overclaim(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            quick_result = self.run_verifier(["--quick"], maybe_root=root)
            self.assertEqual(quick_result.returncode, 0, quick_result.stdout)
            normalized = self.read_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json"
            )
            normalized["demotion_allowed"] = True
            self.write_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json",
                normalized)

            # Act
            result = self.run_verifier(["--security-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "normalized-final-demotion-results.json cannot set demotion_allowed true",
            result.stdout)
