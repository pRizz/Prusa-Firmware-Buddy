from __future__ import annotations

from phase34_test_support import *


class Phase34FinalReadinessCasesMixin:
    def test_contract_declares_complete_ledger_gate_and_artifacts(self) -> None:
        # Arrange
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

        # Act
        open_requires = contract["demotion_dry_run_schema"]["open_requires"]

        # Assert
        self.assertEqual(contract["id"], "phase34_final_readiness_demotion_dry_run_contract")
        self.assertEqual(contract["requirement_ids"], ["READY-01", "READY-02", "READY-03"])
        self.assertEqual(contract["ledger_schema"]["required_fields"], LEDGER_FIELDS)
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)
        self.assertEqual(
            open_requires,
            {
                "readiness_state": "unblocked",
                "approval_validation_state": "valid",
                "approval_decision_state": "approve",
            },
        )
        self.assertTrue(contract["sparse_blocker_overlay_policy"]["clean_row_may_omit_phase32_classification"])
        self.assertEqual(
            contract["sparse_blocker_overlay_policy"]["required_streams_from"],
            "phase31 contract stream_adapters",
        )
        self.assertEqual(
            contract["sparse_blocker_overlay_policy"]["absent_required_stream_state"],
            "required-row-missing",
        )
        self.assertFalse(contract["source_inputs"]["raw_evidence_consumed"])
        self.assertEqual(
            contract["ledger_schema"]["row_kinds"],
            ["evidence", "decision-domain"],
        )
        self.assertEqual(
            contract["decision_domain_policy"]["canonical_rows_from"],
            "phase32 canonical Phase 27/28 decision-domain rows",
        )
        self.assertEqual(
            contract["source_failure_policy"]["reason_codes"],
            [
                "phase31-input-invalid",
                "phase33-handoff-invalid",
                "phase33-normalized-decisions-invalid",
                "phase33-readiness-input-invalid",
                "phase33-register-invalid",
                "phase32-blocker-register-invalid",
                "phase33-demotion-input-invalid",
            ],
        )
        self.assertEqual(
            contract["source_failure_policy"]["blocked_authority_fields"],
            {
                "readiness_state": "blocked",
                "cutover_verdict_state": "blocked",
                "production_cutover_route_state": "blocked",
                "demotion_gate_state": "blocked",
            },
        )
        self.assertFalse(
            contract["source_failure_policy"]["copies_source_payloads"]
        )
        self.assertTrue(
            {
                "decision-target-missing",
                "decision-target-row-mismatch",
                "decision-target-axis-mismatch",
                "decision-target-subject-mismatch",
                "decision-target-duplicate",
                "decision-target-conflict",
                "decision-lifecycle-stale",
                "decision-value-invalid",
            }.issubset(contract["blocked_reason_codes"])
        )

    def test_valid_decision_domain_row_is_first_class_and_not_dangling(self) -> None:
        # Arrange
        module = self.load_module()
        source_ref = REQUIRED_STREAM_SOURCE_REFS["simulator"]
        canonical_row = self.decision_domain_row(
            "canonical-retained-row",
            "retained_code",
            "retained-component",
        )
        row_ref = f"{PHASE32_REGISTER}#canonical-retained-row"
        decision = self.decision(
            "accept-retained",
            "retained_code",
            "accept",
            row_ref,
            decision_subject_id="retained-component",
        )

        # Act
        ledger = module.evaluate_coverage(
            [self.receipt("simulator", source_ref)],
            [canonical_row],
            [decision],
        )

        # Assert
        decision_rows = [
            row for row in ledger if row["ledger_row_kind"] == "decision-domain"
        ]
        self.assertEqual(len(decision_rows), 1)
        self.assertEqual(decision_rows[0]["row_id"], "canonical-retained-row")
        self.assertEqual(decision_rows[0]["decision_axis"], "retained_code")
        self.assertEqual(
            decision_rows[0]["decision_subject_id"],
            "retained-component",
        )
        self.assertEqual(decision_rows[0]["coverage_state"], "covered")
        self.assertEqual(decision_rows[0]["readiness_effect"], "unblocked")
        self.assertEqual(
            decision_rows[0]["retained_code_decision_refs"],
            [
                "build/ci-evidence/phase33/"
                "normalized-decision-records.json#accept-retained"
            ],
        )
        self.assertFalse(
            any(row["coverage_state"] == "dangling-blocker" for row in ledger)
        )

    def test_uncovered_decision_domain_row_preserves_specific_reason(self) -> None:
        # Arrange
        module = self.load_module()
        canonical_row = self.decision_domain_row(
            "canonical-risk-row",
            "residual_risk",
            "risk-component",
        )

        # Act
        ledger = module.evaluate_coverage([], [canonical_row], [])

        # Assert
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]["ledger_row_kind"], "decision-domain")
        self.assertEqual(ledger[0]["coverage_state"], "blocked")
        self.assertEqual(
            ledger[0]["reason_codes"],
            ["decision-target-missing"],
        )

    def test_demotion_only_diagnostic_does_not_block_readiness_row(self) -> None:
        # Arrange
        module = self.load_module()
        readiness_row = self.decision_domain_row(
            "canonical-readiness-row",
            "readiness",
            "final-readiness",
            producer_phase="phase28",
            source_domain="readiness",
            source_stream="readiness",
        )
        demotion_row = self.decision_domain_row(
            "canonical-demotion-row",
            "demotion",
            "reference-demotion",
            producer_phase="phase28",
            source_domain="readiness",
            source_stream="readiness",
        )
        readiness_ref = f"{PHASE32_REGISTER}#canonical-readiness-row"
        demotion_ref = f"{PHASE32_REGISTER}#canonical-demotion-row"
        readiness_decision = self.decision(
            "approve-readiness",
            "readiness",
            "approve",
            readiness_ref,
            affected_gate="final-readiness",
            decision_subject_id="final-readiness",
        )
        demotion_decision = self.decision(
            "approve-demotion",
            "reference_demotion",
            "approve",
            demotion_ref,
            affected_gate="final-reference-demotion-allowed",
            decision_subject_id="reference-demotion",
        )
        demotion_decision["decision_targets"][0]["row_ref"] = (
            f"{PHASE32_REGISTER}#missing-demotion-row"
        )
        demotion_decision["source_row_refs"] = [
            f"{PHASE32_REGISTER}#missing-demotion-row"
        ]

        # Act
        ledger = module.evaluate_coverage(
            [],
            [readiness_row, demotion_row],
            [readiness_decision, demotion_decision],
        )

        # Assert
        retained_readiness = next(
            row
            for row in ledger
            if row["row_id"] == "canonical-readiness-row"
        )
        demotion_diagnostics = [
            row
            for row in ledger
            if "decision-target-row-mismatch" in row["reason_codes"]
        ]
        self.assertEqual(retained_readiness["readiness_effect"], "unblocked")
        self.assertTrue(demotion_diagnostics)
        self.assertTrue(
            all(
                row["readiness_effect"] == "independent"
                for row in demotion_diagnostics
            )
        )

    def test_retained_bundle_preserves_dual_source_ledger_identity(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        retained_row = self.decision_domain_row(
            "canonical-retained-row",
            "retained_code",
            "retained-component",
        )
        readiness_row = self.decision_domain_row(
            "canonical-readiness-row",
            "readiness",
            "final-readiness",
            producer_phase="phase28",
            source_domain="readiness",
            source_stream="readiness",
        )
        retained_ref = f"{PHASE32_REGISTER}#canonical-retained-row"
        readiness_ref = f"{PHASE32_REGISTER}#canonical-readiness-row"
        retained_decision = self.decision(
            "accept-retained",
            "retained_code",
            "accept",
            retained_ref,
            decision_subject_id="retained-component",
        )
        readiness_decision = self.decision(
            "approve-readiness",
            "readiness",
            "approve",
            readiness_ref,
            affected_gate="final-readiness",
            decision_subject_id="final-readiness",
        )
        readiness = {
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "handoff_state": "approval-input-recorded",
            "readiness_input_supplied": True,
            "decision_id": "approve-readiness",
            "source_row_refs": [readiness_ref],
            "phase34_must_generate_final_readiness": True,
            "rationale": readiness_decision["rationale"],
        }
        self.write_fixture(
            root,
            self.required_stream_receipts(),
            [retained_row, readiness_row],
            [retained_decision, readiness_decision],
            readiness,
        )

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        packet = self.read_json(root, f"{OUTPUT_DIR}/final-readiness-packet.json")
        ledger = self.read_json(
            root,
            f"{OUTPUT_DIR}/readiness-coverage-ledger.json",
        )
        report = (
            root / OUTPUT_DIR / "redacted-readiness-report.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(packet["readiness_state"], "unblocked")
        self.assertEqual(packet["ledger_rows"], ledger["rows"])
        self.assertEqual(
            {row["ledger_row_kind"] for row in ledger["rows"]},
            {"evidence", "decision-domain"},
        )
        retained = next(
            row
            for row in ledger["rows"]
            if row["row_id"] == "canonical-retained-row"
        )
        self.assertEqual(retained["source_subject_id"], "retained-component")
        self.assertIn("canonical-retained-row", report)

    def test_quick_default_writes_blocked_packet_and_dry_run(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [])

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        dry_run = self.read_json(root, f"{OUTPUT_DIR}/demotion-dry-run.json")
        packet = self.read_json(root, f"{OUTPUT_DIR}/final-readiness-packet.json")
        manifest = self.read_json(
            root, f"{OUTPUT_DIR}/final-readiness-run-manifest.json")
        self.assertEqual(dry_run["gate_state"], "blocked")
        self.assertEqual(dry_run["approval_validation_state"], "missing")
        self.assertEqual(packet["readiness_state"], "blocked")
        self.assertEqual(
            set(manifest["phase33_register_digests"]),
            {
                "decision_validation_report",
                "demotion_decision_handoff",
                "exception_decision_register",
                "normalized_decision_records",
                "readiness_decision_handoff",
                "residual_risk_decision_register",
                "retained_code_decision_register",
            },
        )
        for digest in manifest["phase33_register_digests"].values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_expected_rows_come_from_phase31_accepted_final_receipts(self) -> None:
        # Arrange
        module = self.load_module()
        receipts = [
            self.receipt("simulator", "build/ci-evidence/phase23/upstream-simulator-result-row.json"),
            self.receipt("live-service", "build/ci-evidence/phase25/upstream-live-service-result-row.json"),
        ]

        # Act
        rows = module.derive_expected_rows(receipts)

        # Assert
        self.assertEqual([row["source_stream"] for row in rows], ["live-service", "simulator"])
        self.assertEqual(len(rows), 2)

    def test_required_stream_specs_come_from_validated_phase31_contract(self) -> None:
        # Arrange
        module = self.load_module()
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)

        # Act
        specifications = module.load_phase31_required_streams(root)

        # Assert
        self.assertEqual(set(specifications), set(REQUIRED_STREAM_SOURCE_REFS))
        for stream, source_ref in REQUIRED_STREAM_SOURCE_REFS.items():
            self.assertEqual(specifications[stream]["expected_source_ref"], source_ref)
            self.assertEqual(specifications[stream]["expected_gate"], EXPECTED_GATE_BY_STREAM[stream])

    def test_phase31_required_stream_contract_rejects_duplicate_and_unsafe_adapters(self) -> None:
        cases = ["duplicate", "unsafe-output-root"]
        for case in cases:
            with self.subTest(case=case):
                # Arrange
                module = self.load_module()
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                contract_path = root / "tools/bazel/manifests/phase31_final_evidence_intake_contract.json"
                contract = json.loads(contract_path.read_text(encoding="utf-8"))
                if case == "duplicate":
                    contract["stream_adapters"].append(dict(contract["stream_adapters"][0]))
                else:
                    contract["stream_adapters"][0]["output_root"] = "/tmp/phase31-escape"
                contract_path.write_text(
                    json.dumps(contract, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

                # Act / Assert
                with self.assertRaises(module.VerificationError):
                    module.load_phase31_required_streams(root)

    def test_clean_final_passed_row_needs_no_phase32_blocker(self) -> None:
        # Arrange
        module = self.load_module()
        receipts = [self.receipt("simulator", "build/ci-evidence/phase23/upstream-simulator-result-row.json")]

        # Act
        ledger = module.evaluate_coverage(receipts, [], [])

        # Assert
        self.assertEqual(ledger[0]["coverage_state"], "clean-no-blocker")
        self.assertEqual(ledger[0]["readiness_effect"], "unblocked")
        self.assertEqual(ledger[0]["classification_ref"], "")

    def test_sparse_overlay_requires_exact_stream_and_affected_gate(self) -> None:
        cases = [
            ("wrong-stream", "live-service", "final-simulator-evidence"),
            ("wrong-gate", "simulator", "final-live-network-transfer-evidence"),
        ]
        for case_name, source_stream, affected_gate in cases:
            with self.subTest(case=case_name):
                # Arrange
                module = self.load_module()
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                receipt = self.receipt("simulator", source_ref)
                blocker = self.blocker_row("wrong-overlay", source_ref, affected_gate=affected_gate)
                blocker["source_stream"] = source_stream

                # Act
                ledger = module.evaluate_coverage([receipt], [blocker], [])

                # Assert
                self.assertEqual(ledger[0]["coverage_state"], "clean-no-blocker")
                dangling_rows = [row for row in ledger if "dangling-row-ref" in row["reason_codes"]]
                self.assertEqual(len(dangling_rows), 1)
                self.assertEqual(dangling_rows[0]["readiness_effect"], "blocked")

    def test_extra_phase32_blocker_row_is_retained_as_dangling(self) -> None:
        # Arrange
        module = self.load_module()
        expected_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        extra_ref = "build/ci-evidence/phase25/upstream-live-service-result-row.json"
        receipt = self.receipt("simulator", expected_ref)
        blocker = self.blocker_row("extra-blocker", extra_ref)

        # Act
        ledger = module.evaluate_coverage([receipt], [blocker], [])

        # Assert
        self.assertEqual(ledger[0]["coverage_state"], "clean-no-blocker")
        self.assertTrue(any(row["classification_ref"].endswith("#extra-blocker") for row in ledger))
        self.assertTrue(any("dangling-row-ref" in row["reason_codes"] for row in ledger))

    def test_nonexistent_and_wrong_gate_decision_refs_are_dangling(self) -> None:
        cases = [
            ("nonexistent", f"{PHASE32_REGISTER}#missing-row", "final-simulator-evidence"),
            ("wrong-gate", f"{PHASE32_REGISTER}#exception-row", "final-live-network-transfer-evidence"),
        ]
        for case_name, decision_ref, affected_gate in cases:
            with self.subTest(case=case_name):
                # Arrange
                module = self.load_module()
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                receipt = self.receipt(
                    "simulator",
                    source_ref,
                    evidence_status="failed",
                    exception_status="exception-requested",
                )
                blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
                blocker_ref = f"{PHASE32_REGISTER}#exception-row"
                decisions = [
                    self.decision("approve-exception", "exception", "approve", blocker_ref),
                    self.decision("dangling-decision", "readiness", "block", decision_ref, affected_gate=affected_gate),
                ]

                # Act
                ledger = module.evaluate_coverage([receipt], [blocker], decisions)

                # Assert
                self.assertEqual(ledger[0]["coverage_state"], "exception-covered")
                dangling_rows = [row for row in ledger if row["coverage_state"] == "dangling-decision"]
                self.assertEqual(len(dangling_rows), 1)
                self.assertIn("dangling-row-ref", dangling_rows[0]["reason_codes"])

    def test_duplicate_phase32_row_ids_block_readiness(self) -> None:
        # Arrange
        module = self.load_module()
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        receipt = self.receipt("simulator", source_ref, evidence_status="failed")
        blocker = self.blocker_row("duplicate-blocker", source_ref)

        # Act
        ledger = module.evaluate_coverage([receipt], [blocker, dict(blocker)], [])

        # Assert
        self.assertEqual(ledger[0]["readiness_effect"], "blocked")
        self.assertIn("duplicate-row", ledger[0]["reason_codes"])

    def test_problem_row_without_phase32_classification_is_underclassified(self) -> None:
        # Arrange
        module = self.load_module()
        receipts = [
            self.receipt(
                "simulator",
                "build/ci-evidence/phase23/upstream-simulator-result-row.json",
                evidence_status="failed",
            )
        ]

        # Act
        ledger = module.evaluate_coverage(receipts, [], [])

        # Assert
        self.assertEqual(ledger[0]["coverage_state"], "underclassified")
        self.assertEqual(ledger[0]["readiness_effect"], "blocked")
        self.assertIn("underclassified", ledger[0]["reason_codes"])

    def test_packet_links_rows_classifications_decisions_blockers_and_artifact_refs(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        blocker = self.blocker_row("failed-simulator", source_ref)
        blocker_ref = f"{PHASE32_REGISTER}#failed-simulator"
        decisions = [self.decision("block-readiness", "readiness", "block", blocker_ref)]
        self.write_fixture(root, [self.receipt("simulator", source_ref, evidence_status="failed")], [blocker], decisions)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        packet = self.read_json(root, f"{OUTPUT_DIR}/final-readiness-packet.json")
        row = next(
            ledger_row
            for ledger_row in packet["ledger_rows"]
            if ledger_row["source_stream"] == "simulator"
        )
        self.assertEqual(row["classification_ref"], blocker_ref)
        self.assertIn("external://simulator/sanitized-report.json", row["artifact_refs"])
        self.assertTrue(row["readiness_decision_refs"])
        self.assertEqual(packet["readiness_state"], "blocked")


__all__ = ["Phase34FinalReadinessCasesMixin"]
