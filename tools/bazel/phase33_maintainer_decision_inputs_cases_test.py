from __future__ import annotations

GENERATED_ARTIFACTS = ['maintainer-decision-input-template.json', 'normalized-decision-records.json', 'retained-code-decision-register.json', 'residual-risk-decision-register.json', 'exception-decision-register.json', 'readiness-decision-handoff.json', 'demotion-decision-handoff.json', 'decision-validation-report.json', 'downstream-handoff-manifest.json', 'redacted-maintainer-decision-report.md', 'contract-snapshots/phase33_maintainer_decision_inputs_contract.json', 'contract-snapshots/phase32_blocker_register_triage_contract.json', 'contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json', 'contract-snapshots/phase28_final_readiness_packet_contract.json', 'contract-snapshots/phase32-downstream-handoff-manifest.json', 'contract-snapshots/phase32-blocker-register.json']
PHASE32_REGISTER_REF = 'build/ci-evidence/phase32/blocker-register.json'
class Phase33MaintainerDecisionInputsCasesMixin:
    def test_contract_lists_all_decision_axes_and_artifacts(self) -> None:
        # Arrange
        contract = self.read_contract()

        # Act
        decision_types = contract["enums"]["decision_type"]

        # Assert
        self.assertEqual(contract["id"], "phase33_maintainer_decision_inputs_contract")
        self.assertEqual(contract["phase"], "33-maintainer-decision-inputs")
        self.assertEqual(contract["phase_lifecycle_id"], "33-2026-07-04T01-36-41")
        self.assertEqual(contract["output_root"], "build/ci-evidence/phase33")
        self.assertEqual(contract["requirement_ids"], ["DECIDE-01", "DECIDE-02", "DECIDE-03"])
        self.assertEqual(
            decision_types,
            ["retained_code", "residual_risk", "exception", "readiness", "reference_demotion"],
        )
        self.assertIn("decision_targets", contract["decision_record_schema"]["required_fields"])
        self.assertEqual(
            contract["decision_target_schema"]["required_fields"],
            ["row_ref", "decision_axis", "decision_subject_id"],
        )
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)
        self.assertIn("demotion_allowed", contract["prohibited_output_markers"])
        self.assertIn("just phase33-verify", contract["verification_commands"])

    def test_exact_typed_targets_are_preserved_in_normalized_handoff(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        row = self.blocker_row(
            "retained-row",
            decision_impact="retained_code_decision_required",
            source_stream="retained-code",
            decision_subject_id="retained-subject",
        )
        self.write_phase32_fixture(root, [row])
        decision = self.decision(
            "accept-retained",
            "retained_code",
            "accept",
            [self.blocker_ref("retained-row")],
            residual_risk_rationale="Accepted with explicit residual-risk rationale.",
        )
        decision["decision_targets"][0]["decision_subject_id"] = "retained-subject"
        decisions_path = self.write_decisions(root, [decision])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        normalized = self.read_json(root, "build/ci-evidence/phase33/normalized-decision-records.json")
        record = normalized["rows"][0]
        self.assertEqual(
            record["decision_targets"],
            [
                {
                    "row_ref": self.blocker_ref("retained-row"),
                    "decision_axis": "retained_code",
                    "decision_subject_id": "retained-subject",
                }
            ],
        )
        self.assertEqual(
            record["source_row_refs"],
            [target["row_ref"] for target in record["decision_targets"]],
        )

    def test_typed_target_requires_all_identity_fields(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("readiness-row")])
        decision = self.decision(
            "missing-target-subject",
            "readiness",
            "block",
            [self.blocker_ref("readiness-row")],
        )
        decision["decision_targets"][0].pop("decision_subject_id")
        decisions_path = self.write_decisions(root, [decision])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("decision_targets[0].decision_subject_id", result.stdout)

    def test_typed_target_projection_must_equal_source_row_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(
            root,
            [self.blocker_row("first-readiness-row"), self.blocker_row("second-readiness-row")],
        )
        decision = self.decision(
            "mismatched-projection",
            "readiness",
            "block",
            [self.blocker_ref("first-readiness-row")],
        )
        decision["source_row_refs"] = [self.blocker_ref("second-readiness-row")]
        decisions_path = self.write_decisions(root, [decision])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source_row_refs must exactly project decision_targets", result.stdout)

    def test_typed_targets_reject_duplicate_triples(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("readiness-row")])
        decision = self.decision(
            "duplicate-triple",
            "readiness",
            "block",
            [self.blocker_ref("readiness-row"), self.blocker_ref("readiness-row")],
        )
        decisions_path = self.write_decisions(root, [decision])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate decision target triple", result.stdout)

    def test_typed_targets_reject_duplicate_row_refs_with_colliding_identity(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("readiness-row")])
        decision = self.decision(
            "duplicate-row-ref",
            "readiness",
            "block",
            [self.blocker_ref("readiness-row"), self.blocker_ref("readiness-row")],
        )
        decision["decision_targets"][1]["decision_subject_id"] = "colliding-subject"
        decisions_path = self.write_decisions(root, [decision])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate decision target row_ref", result.stdout)

    def test_typed_targets_reject_axis_subject_and_row_mismatches_without_fallback(self) -> None:
        cases = [
            ("axis", {"decision_axis": "readiness"}, "decision target axis mismatch"),
            ("subject", {"decision_subject_id": "similar-subject"}, "decision target subject mismatch"),
            (
                "row",
                {"row_ref": self.blocker_ref("missing-row")},
                "decision target row mismatch",
            ),
        ]

        for label, mutation, expected in cases:
            with self.subTest(label=label):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                self.write_phase32_fixture(
                    root,
                    [
                        self.blocker_row(
                            "risk-row",
                            decision_impact="residual_risk_decision_required",
                            decision_subject_id="risk-subject",
                        )
                    ],
                )
                decision = self.decision(
                    f"{label}-mismatch",
                    "residual_risk",
                    "reject",
                    [self.blocker_ref("risk-row")],
                    affected_gates=[],
                    follow_up_refs=[],
                )
                decision["decision_targets"][0]["decision_subject_id"] = "risk-subject"
                decision["decision_targets"][0].update(mutation)
                decision["source_row_refs"] = [
                    target["row_ref"] for target in decision["decision_targets"]
                ]
                decisions_path = self.write_decisions(root, [decision])

                # Act
                result = self.run_quick(root, decisions_path)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_quick_without_maintainer_input_writes_template_and_blocked_handoffs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("critical-readiness-blocker")])

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        for artifact in GENERATED_ARTIFACTS:
            self.assertTrue((root / "build/ci-evidence/phase33" / artifact).exists(), artifact)
        manifest = self.read_json(root, "build/ci-evidence/phase33/downstream-handoff-manifest.json")
        readiness = self.read_json(root, "build/ci-evidence/phase33/readiness-decision-handoff.json")
        demotion = self.read_json(root, "build/ci-evidence/phase33/demotion-decision-handoff.json")
        self.assertIs(manifest["maintainer_input_supplied"], False)
        self.assertIs(manifest["source_inputs"]["raw_evidence_consumed"], False)
        self.assertEqual(readiness["handoff_state"], "blocked-pending-maintainer-input")
        self.assertEqual(demotion["authorization_state"], "blocked")

    def test_phase32_handoff_must_reference_canonical_register(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        row = self.blocker_row("known-row")
        alternate_register_ref = "build/ci-evidence/phase32/alternate-register.json"
        self.write_phase32_fixture(root, [row])
        self.write_json(
            root,
            alternate_register_ref,
            {
                "artifact_name": "phase32-blocker-register-triage",
                "phase": "32-blocker-register-and-evidence-triage",
                "phase_lifecycle_id": "32-2026-07-03T14-13-51",
                "rows": [row],
            },
        )
        handoff = self.read_json(root, "build/ci-evidence/phase32/downstream-handoff-manifest.json")
        handoff["canonical_register_ref"] = alternate_register_ref
        self.write_json(root, "build/ci-evidence/phase32/downstream-handoff-manifest.json", handoff)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"canonical_register_ref must be {PHASE32_REGISTER_REF}", result.stdout)
        self.assertFalse((root / "build/ci-evidence/phase33").exists())

    def test_quick_rejects_symlinked_phase32_handoff_before_writing_outputs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        self.replace_with_external_symlink(
            root,
            "build/ci-evidence/phase32/downstream-handoff-manifest.json",
        )

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--phase32-handoff contains a symlink escape", result.stdout)
        self.assertFalse((root / "build/ci-evidence/phase33").exists())

    def test_quick_rejects_symlinked_phase32_register_before_writing_outputs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        self.replace_with_external_symlink(root, PHASE32_REGISTER_REF)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical_register_ref contains a symlink escape", result.stdout)
        self.assertFalse((root / "build/ci-evidence/phase33").exists())

    def test_quick_rejects_symlinked_maintainer_decisions_before_writing_outputs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        decisions_path = self.write_decisions(
            root,
            [
                self.decision(
                    "block-readiness",
                    "readiness",
                    "block",
                    [self.blocker_ref("known-row")],
                )
            ],
        )
        self.replace_with_external_symlink(root, decisions_path)

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--maintainer-decisions contains a symlink escape", result.stdout)
        self.assertFalse((root / "build/ci-evidence/phase33").exists())

    def test_quick_rejects_maintainer_input_inside_output_root_without_deleting_it(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        payload = {
            "schema_version": "1",
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "decisions": [self.decision("unsafe-input-location", "readiness", "block", [self.blocker_ref("known-row")])],
        }
        unsafe_path = self.write_json(root, "build/ci-evidence/phase33/unsafe-input-location.json", payload)

        # Act
        result = self.run_quick(root, unsafe_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--maintainer-decisions must be outside", result.stdout)
        self.assertTrue((root / unsafe_path).exists())

    def test_retained_and_residual_decisions_require_explicit_metadata_and_owner_signoff(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        retained = self.blocker_row("retained-row", decision_impact="retained_code_decision_required", source_stream="retained-code")
        residual = self.blocker_row("risk-row", decision_impact="residual_risk_decision_required", affected_gate="final-residual-risk-review")
        self.write_phase32_fixture(root, [retained, residual])
        missing_signoff = self.decision("missing-owner-signoff", "retained_code", "accept", [self.blocker_ref("retained-row")])
        missing_signoff.pop("owner_signoff_ref")
        invalid_path = self.write_decisions(root, [missing_signoff])
        valid_path = self.write_decisions(
            root,
            [
                self.decision("accept-retained", "retained_code", "accept", [self.blocker_ref("retained-row")], residual_risk_rationale="Accepted with owner signoff."),
                self.decision(
                    "accept-risk",
                    "residual_risk",
                    "accept",
                    [self.blocker_ref("risk-row")],
                    affected_gates=["final-residual-risk-review"],
                    follow_up_refs=["external://ticket/risk-review"],
                ),
            ],
        )

        # Act
        invalid_result = self.run_quick(root, invalid_path)
        valid_result = self.run_quick(root, valid_path)

        # Assert
        self.assertNotEqual(invalid_result.returncode, 0)
        self.assertIn("owner_signoff_ref", invalid_result.stdout)
        self.assertEqual(valid_result.returncode, 0, valid_result.stdout)
        retained_register = self.read_json(root, "build/ci-evidence/phase33/retained-code-decision-register.json")
        residual_register = self.read_json(root, "build/ci-evidence/phase33/residual-risk-decision-register.json")
        self.assertEqual(retained_register["rows"][0]["decision_value"], "accept")
        self.assertEqual(retained_register["rows"][0]["residual_risk_rationale"], "Accepted with owner signoff.")
        self.assertEqual(residual_register["rows"][0]["decision_value"], "accept")
        self.assertEqual(residual_register["rows"][0]["affected_gates"], ["final-residual-risk-review"])
        self.assertEqual(residual_register["rows"][0]["follow_up_refs"], ["external://ticket/risk-review"])

    def test_maintainer_metadata_must_be_non_blank(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(root, [self.blocker_row("known-row")])
        decision = self.decision("blank-metadata", "readiness", "block", [self.blocker_ref("known-row")])
        decision["maintainer_identity_ref"] = "   "
        decision["owner_signoff_ref"] = "\t"
        decision["rationale"] = "\n"
        decisions_path = self.write_decisions(root, [decision])

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be a non-blank string", result.stdout)

    def test_contradictory_source_row_decisions_fail_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_phase32_fixture(
            root,
            [
                self.blocker_row(
                    "risk-row",
                    severity="critical",
                    decision_impact="residual_risk_decision_required",
                    affected_gate="final-residual-risk-review",
                ),
                self.blocker_row("readiness-row", severity="warning"),
            ],
        )
        decisions_path = self.write_decisions(
            root,
            [
                self.decision(
                    "accept-risk",
                    "residual_risk",
                    "accept",
                    [self.blocker_ref("risk-row")],
                    affected_gates=["final-residual-risk-review"],
                    follow_up_refs=["external://ticket/risk-review"],
                ),
                self.decision(
                    "reject-risk",
                    "residual_risk",
                    "reject",
                    [self.blocker_ref("risk-row")],
                    affected_gates=[],
                    follow_up_refs=[],
                ),
                self.decision("approve-readiness", "readiness", "approve", [self.blocker_ref("readiness-row")]),
            ],
        )

        # Act
        result = self.run_quick(root, decisions_path)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conflicts with decision target", result.stdout)

__all__ = [
    "GENERATED_ARTIFACTS",
    "PHASE32_REGISTER_REF",
    "Phase33MaintainerDecisionInputsCasesMixin",
]
