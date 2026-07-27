from __future__ import annotations


class Phase18CutoverReviewFailureTests:

    def test_decision_input_requires_complete_final_approval_metadata(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            del decision_input["final_criterion_decisions"][0]["approver"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approver", result.stdout)

    def test_decision_input_requires_decision_packet(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            del decision_input["decision_packet"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_packet", result.stdout)

    def test_decision_input_requires_current_phase(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["decision_packet"][
                "phase"] = "17-release-candidate-evidence"
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_packet phase", result.stdout)

    def test_decision_input_requires_current_phase_lifecycle_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["decision_packet"][
                "phase_lifecycle_id"] = "18-stale-lifecycle"
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_packet phase_lifecycle_id", result.stdout)

    def test_exception_approved_requires_complete_exception_metadata(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(
                root, status="exception-approved", decision="exception")
            del decision_input["final_criterion_decisions"][0]["exception"][
                "scope"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scope", result.stdout)

    def test_passed_final_decision_rejects_reject_decision_with_empty_evidence(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["final_criterion_decisions"][0][
                "decision"] = "reject"
            decision_input["final_criterion_decisions"][0]["status"] = "passed"
            decision_input["final_criterion_decisions"][0][
                "evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status passed requires decision approve", result.stdout)

    def test_passed_final_decision_requires_evidence_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["final_criterion_decisions"][0][
                "evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "evidence_refs must include at least one Phase 18 evidence ref",
            result.stdout)

    def test_exception_approved_final_decision_requires_evidence_refs(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(
                root, status="exception-approved", decision="exception")
            decision_input["final_criterion_decisions"][0][
                "evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "evidence_refs must include at least one Phase 18 evidence ref",
            result.stdout)

    def test_not_applicable_final_decision_requires_evidence_refs(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(
                root, status="not-applicable", decision="exception")
            decision_input["final_criterion_decisions"][0][
                "evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "evidence_refs must include at least one Phase 18 evidence ref",
            result.stdout)

    def test_exception_metadata_requires_evidence_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(
                root, status="exception-approved", decision="exception")
            decision_input["final_criterion_decisions"][0]["exception"][
                "evidence_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "exception evidence_refs must include at least one Phase 18 evidence ref",
            result.stdout)

    def test_final_decision_requires_string_decision_id(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["final_criterion_decisions"][0]["decision_id"] = 123
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_id must be a non-empty string", result.stdout)

    def test_final_decision_rejects_duplicate_decision_ids(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["final_criterion_decisions"][1][
                "decision_id"] = decision_input["final_criterion_decisions"][
                    0]["decision_id"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate final decision id", result.stdout)

    def test_final_decision_rejects_status_outside_criterion_policy(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["final_demotion_criteria"][0]["allowed_statuses"] = [
                "pending"
            ]
            self.write_contract(root, contract)
            decision_input = self.complete_decision_input(root)
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status passed is not allowed by criterion policy",
                      result.stdout)

    def test_final_decision_rejects_exception_status_when_criterion_disallows_exceptions(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            contract = self.read_contract(root)
            contract["final_demotion_criteria"][0]["exception_allowed"] = False
            self.write_contract(root, contract)
            decision_input = self.complete_decision_input(
                root, status="exception-approved", decision="exception")
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "status exception-approved is not allowed by criterion policy",
            result.stdout)

    def test_exception_approved_final_decision_rejects_non_string_exception_metadata(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(
                root, status="exception-approved", decision="exception")
            decision_input["final_criterion_decisions"][0]["exception"][
                "scope"] = ["phase18-final-review"]
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exception scope must be a non-empty string",
                      result.stdout)

    def test_complete_decision_input_without_upstream_results_keeps_demotion_false(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

            # Assert
            self.assertEqual(result.returncode, 0, result.stdout)
            run_manifest = self.read_json(
                root, "build/ci-evidence/phase18/run-manifest.json")
            self.assertTrue(run_manifest["decision_inputs_supplied"])
            self.assertFalse(run_manifest["upstream_results_supplied"])
            self.assertFalse(run_manifest["demotion_allowed"])
            normalized = self.read_json(
                root,
                "build/ci-evidence/phase18/normalized-final-demotion-results.json"
            )
            self.assertEqual(
                normalized["results"][0]["upstream_result_status"], "missing")

    def test_retained_packet_acceptance_requires_supplied_evidence(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["retained_code_reviews"][0][
                "supplied_evidence_result_refs"] = []
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("supplied_evidence_result_refs", result.stdout)

    def test_deferred_approved_exception_retained_review_requires_supplied_evidence(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["retained_code_reviews"][0][
                "status"] = "deferred-approved-exception"
            decision_input["retained_code_reviews"][0][
                "supplied_evidence_result_refs"] = []
            decision_input["retained_code_reviews"][0][
                "exception_ref"] = "phase18-retained-exception"
            decision_input["retained_code_reviews"][0][
                "blocker_or_deferred_action"] = "Review exception before demotion."
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "supplied_evidence_result_refs must include at least one Phase 18 evidence ref",
            result.stdout)

    def test_retained_packet_acceptance_requires_contract_approver_role(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            decision_input = self.complete_decision_input(root)
            decision_input["retained_code_reviews"][0][
                "approver_role"] = "wrong-role"
            self.write_json(root, "decision-input.json", decision_input)

            # Act
            result = self.run_verifier(
                ["--quick", "--decision-input", "decision-input.json"],
                maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approver_role must be", result.stdout)

    def test_decision_input_rejects_paths_outside_phase18_output_or_external_refs(
            self) -> None:
        cases = [
            "/tmp/phase18-evidence.json", "../phase18-evidence.json",
            "build/ci-evidence/phase17/result.json"
        ]
        for evidence_ref in cases:
            with self.subTest(evidence_ref=evidence_ref):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    decision_input = self.complete_decision_input(root)
                    decision_input["final_criterion_decisions"][0][
                        "evidence_refs"] = [evidence_ref]
                    self.write_json(root, "decision-input.json",
                                    decision_input)

                    # Act
                    result = self.run_verifier(
                        ["--quick", "--decision-input", "decision-input.json"],
                        maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(evidence_ref, result.stdout)
