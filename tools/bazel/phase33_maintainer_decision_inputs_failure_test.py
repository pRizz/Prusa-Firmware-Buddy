from __future__ import annotations
class Phase33MaintainerDecisionInputsFailureMixin:
    def test_decision_type_must_match_phase32_decision_impact(self) -> None:
        cases = [
            ("retained_code", "reject", "residual_risk_decision_required", {}),
            ("residual_risk", "reject", "retained_code_decision_required", {"affected_gates": [], "follow_up_refs": []}),
            ("exception", "reject", "final_readiness_blocked", {}),
            ("readiness", "block", "residual_risk_decision_required", {}),
            ("reference_demotion", "reject", "final_readiness_blocked", {}),
        ]

        for decision_type, decision_value, decision_impact, extra in cases:
            with self.subTest(decision_type=decision_type):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                row_id = f"{decision_type}-row"
                self.write_phase32_fixture(root, [self.blocker_row(row_id, decision_impact=decision_impact)])
                decisions_path = self.write_decisions(
                    root,
                    [
                        self.decision(
                            f"wrong-axis-{decision_type}",
                            decision_type,
                            decision_value,
                            [self.blocker_ref(row_id)],
                            **extra,
                        )
                    ],
                )

                # Act
                result = self.run_quick(root, decisions_path)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("decision target axis mismatch", result.stdout)

    def test_hard_blocker_problem_kinds_reject_normal_acceptance(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        rows = [
            self.blocker_row("hard-retained", row_problem_kind="secret_tainted", decision_impact="retained_code_decision_required", source_stream="retained-code"),
            self.blocker_row("hard-risk", row_problem_kind="redaction_failed", decision_impact="residual_risk_decision_required"),
            self.blocker_row("hard-exception", row_problem_kind="unsafe_ref", blocker_kind="exception_request", decision_impact="exception_decision_required"),
        ]
        self.write_phase32_fixture(root, rows)
        decisions_path = self.write_decisions(
            root,
            [
                self.decision("hard-retained-accept", "retained_code", "accept", [self.blocker_ref("hard-retained")], residual_risk_rationale="Risk rationale."),
                self.decision("hard-risk-accept", "residual_risk", "accept", [self.blocker_ref("hard-risk")], affected_gates=["final-simulator-evidence"], follow_up_refs=["external://ticket/risk"]),
                self.decision(
                    "hard-exception-approve",
                    "exception",
                    "approve",
                    [self.blocker_ref("hard-exception")],
                    scope="narrow",
                    expiry_or_review_trigger="next release",
                    affected_requirements=["DECIDE-02"],
                    affected_gates=["final-simulator-evidence"],
                    linked_blocker_refs=[self.blocker_ref("hard-exception")],
                ),
            ],
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hard blocker", result.stdout.casefold())

    def test_hard_blocker_problem_kinds_reject_readiness_and_demotion_approval(self) -> None:
        cases = [
            ("readiness", "redaction_failed", "final_readiness_blocked", "final-simulator-evidence"),
            ("readiness", "secret_tainted", "final_readiness_blocked", "final-simulator-evidence"),
            ("reference_demotion", "lifecycle_mismatch", "demotion_decision_required", "final-reference-demotion-allowed"),
            ("reference_demotion", "unsafe_ref", "demotion_decision_required", "final-reference-demotion-allowed"),
        ]

        for decision_type, row_problem_kind, decision_impact, affected_gate in cases:
            with self.subTest(decision_type=decision_type, row_problem_kind=row_problem_kind):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                row_id = f"{decision_type}-{row_problem_kind}"
                self.write_phase32_fixture(
                    root,
                    [
                        self.blocker_row(
                            row_id,
                            row_problem_kind=row_problem_kind,
                            severity="warning",
                            decision_impact=decision_impact,
                            affected_gate=affected_gate,
                        )
                    ],
                )
                decisions_path = self.write_decisions(
                    root,
                    [self.decision(f"approve-{row_id}", decision_type, "approve", [self.blocker_ref(row_id)])],
                )

                # Act
                result = self.run_quick(root, decisions_path)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("hard blocker", result.stdout.casefold())

    def test_readiness_approval_rejects_remaining_noncritical_hard_blocker(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        normal_readiness = self.blocker_row(
            "normal-readiness-row",
            row_problem_kind="failed",
            severity="warning",
            decision_impact="final_readiness_blocked",
        )
        warning_hard_blocker = self.blocker_row(
            "warning-hard-blocker",
            row_problem_kind="redaction_failed",
            severity="warning",
            decision_impact="final_readiness_blocked",
        )
        self.write_phase32_fixture(root, [normal_readiness, warning_hard_blocker])
        decisions_path = self.write_decisions(root, [self.decision("approve-readiness", "readiness", "approve", [self.blocker_ref("normal-readiness-row")])])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hard blocker", result.stdout.casefold())
        self.assertIn(self.blocker_ref("warning-hard-blocker"), result.stdout)

    def test_exception_approval_requires_exact_row_ref_and_gate_match(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        exception_row = self.blocker_row(
            "exception-row",
            row_problem_kind="exception_requested",
            blocker_kind="exception_request",
            decision_impact="exception_decision_required",
            affected_gate="final-live-network-transfer-evidence",
        )
        self.write_phase32_fixture(root, [exception_row])
        invalid_path = self.write_decisions(
            root,
            [
                self.decision(
                    "bad-exception-gate",
                    "exception",
                    "approve",
                    [self.blocker_ref("exception-row")],
                    scope="live transfer only",
                    expiry_or_review_trigger="phase35 review",
                    affected_requirements=["DECIDE-02"],
                    affected_gates=["final-simulator-evidence"],
                    linked_blocker_refs=[self.blocker_ref("exception-row")],
                )
            ],
        )
        valid_path = self.write_decisions(
            root,
            [
                self.decision(
                    "good-exception-gate",
                    "exception",
                    "approve",
                    [self.blocker_ref("exception-row")],
                    scope="live transfer only",
                    expiry_or_review_trigger="phase35 review",
                    affected_requirements=["DECIDE-02"],
                    affected_gates=["final-live-network-transfer-evidence"],
                    linked_blocker_refs=[self.blocker_ref("exception-row")],
                )
            ],
        )

        # Act
        invalid_result = self.run_quick(root, invalid_path)
        valid_result = self.run_quick(root, valid_path)

        # Assert
        self.assertNotEqual(invalid_result.returncode, 0)
        self.assertIn("affected_gate", invalid_result.stdout)
        self.assertEqual(valid_result.returncode, 0, valid_result.stdout)
        register = self.read_json(root, "build/ci-evidence/phase33/exception-decision-register.json")
        self.assertEqual(register["rows"][0]["coverage_state"], "approved-exception")
        self.assertEqual(register["rows"][0]["scope"], "live transfer only")
        self.assertEqual(register["rows"][0]["expiry_or_review_trigger"], "phase35 review")
        self.assertEqual(register["rows"][0]["affected_requirements"], ["DECIDE-02"])
        self.assertEqual(register["rows"][0]["affected_gates"], ["final-live-network-transfer-evidence"])
        self.assertEqual(register["rows"][0]["linked_blocker_refs"], [self.blocker_ref("exception-row")])

    def test_decision_source_traceability_refs_must_be_non_empty(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        exception_row = self.blocker_row(
            "exception-row",
            row_problem_kind="exception_requested",
            blocker_kind="exception_request",
            decision_impact="exception_decision_required",
        )
        self.write_phase32_fixture(root, [exception_row])
        empty_source_refs_path = self.write_decisions(root, [self.decision("empty-source-refs", "readiness", "block", [])])
        empty_linked_refs_path = self.write_decisions(
            root,
            [
                self.decision(
                    "empty-linked-refs",
                    "exception",
                    "approve",
                    [self.blocker_ref("exception-row")],
                    scope="narrow",
                    expiry_or_review_trigger="phase35 review",
                    affected_requirements=["DECIDE-02"],
                    affected_gates=["final-simulator-evidence"],
                    linked_blocker_refs=[],
                )
            ],
        )

        # Act
        empty_source_result = self.run_quick(root, empty_source_refs_path)
        empty_linked_result = self.run_quick(root, empty_linked_refs_path)

        # Assert
        self.assertNotEqual(empty_source_result.returncode, 0)
        self.assertIn("empty-source-refs.source_row_refs must contain at least one entry", empty_source_result.stdout)
        self.assertNotEqual(empty_linked_result.returncode, 0)
        self.assertIn("empty-linked-refs.linked_blocker_refs must contain at least one entry", empty_linked_result.stdout)

    def test_rejected_exception_remains_in_exception_register(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(
            root,
            [
                self.blocker_row(
                    "exception-row",
                    row_problem_kind="exception_requested",
                    blocker_kind="exception_request",
                    decision_impact="exception_decision_required",
                )
            ],
        )
        decisions_path = self.write_decisions(root, [self.decision("reject-exception", "exception", "reject", [self.blocker_ref("exception-row")])])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        register = self.read_json(root, "build/ci-evidence/phase33/exception-decision-register.json")
        self.assertEqual(register["rows"][0]["decision_value"], "reject")
        self.assertEqual(register["rows"][0]["coverage_state"], "rejected")

    def test_readiness_approval_rejects_uncovered_critical_blocker(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("critical-readiness-blocker", severity="critical")])
        decisions_path = self.write_decisions(root, [self.decision("approve-readiness", "readiness", "approve", [self.blocker_ref("critical-readiness-blocker")])])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("uncovered critical blocker", result.stdout.casefold())

    def test_readiness_approval_counts_accepted_retained_code_coverage(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        retained_row = self.blocker_row(
            "critical-retained-row",
            severity="critical",
            decision_impact="retained_code_decision_required",
            source_stream="retained-code",
        )
        readiness_row = self.blocker_row(
            "warning-readiness-row",
            severity="warning",
            decision_impact="final_readiness_blocked",
        )
        self.write_phase32_fixture(root, [retained_row, readiness_row])
        decisions_path = self.write_decisions(
            root,
            [
                self.decision(
                    "accept-retained-row",
                    "retained_code",
                    "accept",
                    [self.blocker_ref("critical-retained-row")],
                    residual_risk_rationale="Accepted retained code with explicit owner signoff.",
                ),
                self.decision("approve-readiness", "readiness", "approve", [self.blocker_ref("warning-readiness-row")]),
            ],
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        handoff = self.read_json(root, "build/ci-evidence/phase33/readiness-decision-handoff.json")
        self.assertEqual(handoff["handoff_state"], "approval-input-recorded")

    def test_invalid_decision_id_type_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        decision = self.decision("invalid-id", "readiness", "block", [self.blocker_ref("known-row")])
        decision["decision_id"] = ["invalid-id"]
        decisions_path = self.write_decisions(root, [decision])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_id must be a non-blank string", result.stdout)
        self.assertNotIn("Traceback", result.stdout)

    def test_readiness_block_handoff_preserves_blocker_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("critical-readiness-blocker", severity="critical")])
        decisions_path = self.write_decisions(
            root,
            [
                self.decision(
                    "block-readiness",
                    "readiness",
                    "block",
                    [self.blocker_ref("critical-readiness-blocker")],
                    blocked_source_row_refs=[self.blocker_ref("critical-readiness-blocker")],
                )
            ],
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        handoff = self.read_json(root, "build/ci-evidence/phase33/readiness-decision-handoff.json")
        self.assertEqual(handoff["handoff_state"], "blocked-by-maintainer-input")
        self.assertEqual(handoff["blocked_source_row_refs"], [self.blocker_ref("critical-readiness-blocker")])

    def test_readiness_block_validates_blocked_source_row_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        cases = [
            self.write_decisions(
                root,
                [
                    self.decision(
                        "blocked-malformed-ref",
                        "readiness",
                        "block",
                        [self.blocker_ref("known-row")],
                        blocked_source_row_refs=["build/ci-evidence/phase32/../secret.json#known-row"],
                    )
                ],
            ),
            self.write_decisions(
                root,
                [
                    self.decision(
                        "blocked-unresolved-ref",
                        "readiness",
                        "block",
                        [self.blocker_ref("known-row")],
                        blocked_source_row_refs=[self.blocker_ref("missing-row")],
                    )
                ],
            ),
        ]

        for decisions_path in cases:
            with self.subTest(decisions_path=decisions_path):
                # Act
                result = self.run_quick(root, decisions_path)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("blocked_source_row_refs", result.stdout)

__all__ = ["Phase33MaintainerDecisionInputsFailureMixin"]
