from __future__ import annotations


class Phase18CutoverReviewUpstreamFailureTests:

    def test_demotion_allowed_only_when_decisions_and_upstream_results_pass(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            upstream_results = self.complete_upstream_results(root)
            self.write_json(root, "decision-input.json", decision_input)
            self.write_json(root, "upstream-results.json", upstream_results)

            # Act
            result = self.run_verifier(
                [
                    "--quick", "--decision-input", "decision-input.json",
                    "--upstream-results", "upstream-results.json"
                ],
                maybe_root=root,
            )

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            self.assertTrue(run_manifest["decision_inputs_supplied"])
            self.assertTrue(run_manifest["upstream_results_supplied"])
            self.assertTrue(run_manifest["demotion_allowed"])
            self.assertEqual(run_manifest["upstream_result_status_counts"], {
                "not-required": 3,
                "passed": 6
            })

    def test_non_passing_upstream_result_keeps_demotion_false(self) -> None:
        for status in [
                "failed", "pending-simulator-input", "rejected-redaction",
                "rejected-overclaim"
        ]:
            with self.subTest(status=status):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    upstream_results = self.complete_upstream_results(root)
                    upstream_results["upstream_results"][0]["status"] = status
                    upstream_results["upstream_results"][0][
                        "failure_reason"] = f"{status} fixture"
                    self.write_json(root, "decision-input.json",
                                    decision_input)
                    self.write_json(root, "upstream-results.json",
                                    upstream_results)

                    # Act
                    result = self.run_verifier(
                        [
                            "--quick", "--decision-input",
                            "decision-input.json", "--upstream-results",
                            "upstream-results.json"
                        ],
                        maybe_root=root,
                    )

                    # Assert
                    self.assertEqual(result.returncode, 0, result.stdout)
                    run_manifest = self.read_json(
                        root, "build/ci-evidence/phase18/run-manifest.json")
                    self.assertFalse(run_manifest["demotion_allowed"])
                    consumption = self.read_json(
                        root,
                        "build/ci-evidence/phase18/upstream-result-consumption.json"
                    )
                    self.assertEqual(
                        consumption["results"][0]["upstream_result_status"],
                        status)

    def test_missing_required_upstream_result_keeps_demotion_false(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            upstream_results = self.complete_upstream_results(root)
            missing_id = upstream_results["upstream_results"][0][
                "criterion_id"]
            upstream_results["upstream_results"] = [
                row for row in upstream_results["upstream_results"]
                if row["criterion_id"] != missing_id
            ]
            self.write_json(root, "decision-input.json", decision_input)
            self.write_json(root, "upstream-results.json", upstream_results)

            # Act
            result = self.run_verifier(
                [
                    "--quick", "--decision-input", "decision-input.json",
                    "--upstream-results", "upstream-results.json"
                ],
                maybe_root=root,
            )

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            self.assertFalse(run_manifest["demotion_allowed"])
            consumption = self.read_json(
                root,
                "build/ci-evidence/phase18/upstream-result-consumption.json")
            row = next(row for row in consumption["results"]
                       if row["criterion_id"] == missing_id)
            self.assertEqual(row["upstream_result_status"], "missing")

    def test_upstream_results_reject_wrong_lifecycle_and_unsafe_refs(
            self) -> None:
        cases = [
            ("source_lifecycle_id", "19-stale-lifecycle",
             "source_lifecycle_id"),
            ("manifest_path", "../phase19/run-manifest.json",
             "../phase19/run-manifest.json"),
            ("manifest_path", "build/ci-evidence/phase17/run-manifest.json",
             "build/ci-evidence/phase17/run-manifest.json"),
        ]
        for field, value, expected in cases:
            with self.subTest(field=field, value=value):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    upstream_results = self.complete_upstream_results(root)
                    upstream_results["upstream_results"][0][field] = value
                    self.write_json(root, "decision-input.json",
                                    decision_input)
                    self.write_json(root, "upstream-results.json",
                                    upstream_results)

                    # Act
                    result = self.run_verifier(
                        [
                            "--quick", "--decision-input",
                            "decision-input.json", "--upstream-results",
                            "upstream-results.json"
                        ],
                        maybe_root=root,
                    )

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_redaction_and_source_ref_failures_block_upstream_results(
            self) -> None:
        cases = [("redaction_status", "failed"),
                 ("source_ref_status", "failed")]
        for field, value in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    upstream_results = self.complete_upstream_results(root)
                    upstream_results["upstream_results"][0][field] = value
                    self.write_json(root, "decision-input.json",
                                    decision_input)
                    self.write_json(root, "upstream-results.json",
                                    upstream_results)

                    # Act
                    result = self.run_verifier(
                        [
                            "--quick", "--decision-input",
                            "decision-input.json", "--upstream-results",
                            "upstream-results.json"
                        ],
                        maybe_root=root,
                    )

                    # Assert
                    self.assertEqual(result.returncode, 0, result.stdout)
                    run_manifest = self.read_json(
                        root, "build/ci-evidence/phase18/run-manifest.json")
                    self.assertFalse(run_manifest["demotion_allowed"])
                    consumption = self.read_json(
                        root,
                        "build/ci-evidence/phase18/upstream-result-consumption.json"
                    )
                    self.assertIn(
                        field, " ".join(consumption["results"][0]
                                        ["upstream_blocking_reasons"]))

    def test_exception_approved_decision_can_cover_coverable_upstream_failure(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            upstream_results = self.complete_upstream_results(root)
            criterion_id = upstream_results["upstream_results"][0][
                "criterion_id"]
            upstream_results["upstream_results"][0]["status"] = "failed"
            upstream_results["upstream_results"][0][
                "failure_reason"] = "Operator accepted a documented exception."
            for decision in decision_input["final_criterion_decisions"]:
                if decision["criterion_id"] == criterion_id:
                    decision["decision"] = "exception"
                    decision["status"] = "exception-approved"
                    decision["exception"]["evidence_refs"] = [
                        f"build/ci-evidence/phase18/upstream-result-consumption.json#{criterion_id}",
                    ]
            self.write_json(root, "decision-input.json", decision_input)
            self.write_json(root, "upstream-results.json", upstream_results)

            # Act
            result = self.run_verifier(
                [
                    "--quick", "--decision-input", "decision-input.json",
                    "--upstream-results", "upstream-results.json"
                ],
                maybe_root=root,
            )

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            self.assertTrue(run_manifest["demotion_allowed"])

    def test_blocking_final_criterion_statuses_keep_demotion_false(
            self) -> None:
        for status in [
                "pending",
                "failed",
                "blocked",
                "exception-requested",
                "exception-rejected",
                "rejected-redaction",
                "rejected-overclaim",
        ]:
            with self.subTest(status=status):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    decision_input["final_criterion_decisions"][0][
                        "status"] = status
                    self.write_json(root, "decision-input.json",
                                    decision_input)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--decision-input", "decision-input.json"],
                        maybe_root=root)

                    # Assert
                    self.assertEqual(result.returncode, 0, result.stdout)
                    run_manifest = self.read_json(
                        root, "build/ci-evidence/phase18/run-manifest.json")
                    self.assertFalse(run_manifest["demotion_allowed"])
