from __future__ import annotations

from phase34_test_support import *


class Phase34FinalReadinessDemotionFailureMixin:
    def test_missing_failed_stale_malformed_redaction_and_underclassified_rows_block(self) -> None:
        module = self.load_module()
        cases = [
            ("missing", "required-row-missing"),
            ("failed", "evidence-failed"),
            ("stale", "evidence-stale"),
            ("malformed", "evidence-malformed"),
            ("redaction_failed", "redaction-failed"),
            ("unknown_unclassified", "unknown-classification"),
        ]
        for problem_kind, expected_reason in cases:
            with self.subTest(problem_kind=problem_kind):
                # Arrange
                source_ref = f"external://fixture/{problem_kind}"
                receipt = self.receipt("simulator", source_ref, evidence_status="failed")
                blocker = self.blocker_row(problem_kind, source_ref, row_problem_kind=problem_kind)

                # Act
                ledger = module.evaluate_coverage([receipt], [blocker], [])

                # Assert
                self.assertEqual(ledger[0]["readiness_effect"], "blocked")
                self.assertIn(expected_reason, ledger[0]["reason_codes"])

    def test_exception_requires_exact_row_and_gate_coverage(self) -> None:
        # Arrange
        module = self.load_module()
        source_ref = "external://fixture/exception"
        receipt = self.receipt("simulator", source_ref, evidence_status="failed", exception_status="exception-requested")
        blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
        blocker_ref = f"{PHASE32_REGISTER}#exception-row"
        exact = self.decision("approve-exact", "exception", "approve", blocker_ref)
        wrong_gate = self.decision("approve-wrong", "exception", "approve", blocker_ref, affected_gate="final-live-network-transfer-evidence")

        # Act
        covered = module.evaluate_coverage([receipt], [blocker], [exact])
        uncovered = module.evaluate_coverage([receipt], [blocker], [wrong_gate])

        # Assert
        self.assertEqual(covered[0]["coverage_state"], "exception-covered")
        self.assertEqual(covered[0]["readiness_effect"], "unblocked")
        self.assertEqual(uncovered[0]["coverage_state"], "exception-uncovered")
        self.assertEqual(uncovered[0]["readiness_effect"], "blocked")

    def test_green_rows_without_explicit_demotion_approval_stay_blocked(self) -> None:
        # Arrange
        module = self.load_module()

        # Act
        result = module.evaluate_demotion("unblocked", "missing", "missing", [])

        # Assert
        self.assertEqual(result["gate_state"], "blocked")
        self.assertIn("approval-missing", result["reason_codes"])

    def test_demotion_truth_table_opens_only_for_unblocked_valid_approve(self) -> None:
        module = self.load_module()
        for readiness in ["blocked", "unblocked"]:
            for validation in ["missing", "invalid", "valid"]:
                for decision in ["missing", "approve", "reject"]:
                    with self.subTest(readiness=readiness, validation=validation, decision=decision):
                        # Arrange / Act
                        result = module.evaluate_demotion(readiness, validation, decision, [])

                        # Assert
                        expected = "open" if (readiness, validation, decision) == ("unblocked", "valid", "approve") else "blocked"
                        self.assertEqual(result["gate_state"], expected)

    def test_open_gate_requires_corroborated_readiness_and_demotion_decisions(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
        blocker_ref = f"{PHASE32_REGISTER}#exception-row"
        decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
        decisions.append(self.decision("approve-exception", "exception", "approve", blocker_ref))
        receipts = self.required_stream_receipts()
        receipts[0] = self.receipt(
            "simulator",
            source_ref,
            evidence_status="failed",
            exception_status="exception-requested",
        )
        self.write_fixture(root, receipts, [blocker], decisions, readiness, demotion)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)
        dry_run = self.read_json(root, f"{OUTPUT_DIR}/demotion-dry-run.json")
        self.assertEqual(dry_run["gate_state"], "open")

    def test_each_absent_required_stream_blocks_otherwise_valid_demotion(self) -> None:
        for missing_stream in REQUIRED_STREAM_SOURCE_REFS:
            with self.subTest(missing_stream=missing_stream):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                exception_stream = "hardware-media-safety" if missing_stream == "simulator" else "simulator"
                exception_source_ref = REQUIRED_STREAM_SOURCE_REFS[exception_stream]
                affected_gate = EXPECTED_GATE_BY_STREAM[exception_stream]
                blocker = self.blocker_row(
                    "exception-row",
                    exception_source_ref,
                    row_problem_kind="exception_requested",
                    affected_gate=affected_gate,
                )
                blocker["source_stream"] = exception_stream
                blocker_ref = f"{PHASE32_REGISTER}#exception-row"
                decisions, readiness, demotion = self.approved_projection_fixture(
                    blocker_ref,
                    affected_gate,
                )
                decisions.append(
                    self.decision(
                        "approve-exception",
                        "exception",
                        "approve",
                        blocker_ref,
                        affected_gate=affected_gate,
                    )
                )
                missing_source_ref = REQUIRED_STREAM_SOURCE_REFS[missing_stream]
                missing_gate = EXPECTED_GATE_BY_STREAM[missing_stream]
                missing_blocker = self.blocker_row(
                    "missing-stream-row",
                    missing_source_ref,
                    row_problem_kind="missing",
                    affected_gate=missing_gate,
                )
                missing_blocker["source_stream"] = missing_stream
                missing_blocker_ref = f"{PHASE32_REGISTER}#missing-stream-row"
                decisions.append(
                    self.decision(
                        "approve-missing-stream-exception",
                        "exception",
                        "approve",
                        missing_blocker_ref,
                        affected_gate=missing_gate,
                    )
                )
                receipts = [
                    receipt
                    for receipt in self.required_stream_receipts()
                    if receipt["stream"] != missing_stream
                ]
                for index, receipt in enumerate(receipts):
                    if receipt["stream"] == exception_stream:
                        receipts[index] = self.receipt(
                            exception_stream,
                            exception_source_ref,
                            evidence_status="failed",
                            exception_status="exception-requested",
                        )
                self.write_fixture(
                    root,
                    receipts,
                    [blocker, missing_blocker],
                    decisions,
                    readiness,
                    demotion,
                )

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertEqual(result.returncode, 0, result.stdout)
                dry_run = self.read_json(root, f"{OUTPUT_DIR}/demotion-dry-run.json")
                ledger = self.read_json(root, f"{OUTPUT_DIR}/readiness-coverage-ledger.json")
                missing_rows = [
                    row
                    for row in ledger["rows"]
                    if row["source_stream"] == missing_stream
                ]
                self.assertEqual(dry_run["readiness_state"], "blocked")
                self.assertEqual(dry_run["gate_state"], "blocked")
                self.assertEqual(len(missing_rows), 1)
                self.assertEqual(missing_rows[0]["coverage_state"], "required-row-missing")
                self.assertEqual(missing_rows[0]["reason_codes"], ["required-row-missing"])

    def test_unknown_projection_decision_ids_are_rejected(self) -> None:
        for projection_name in ["readiness", "demotion"]:
            with self.subTest(projection=projection_name):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
                blocker_ref = f"{PHASE32_REGISTER}#exception-row"
                decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
                decisions.append(self.decision("approve-exception", "exception", "approve", blocker_ref))
                target = readiness if projection_name == "readiness" else demotion
                target["decision_id"] = "unknown-decision"
                receipt = self.receipt(
                    "simulator",
                    source_ref,
                    evidence_status="failed",
                    exception_status="exception-requested",
                )
                self.write_fixture(root, [receipt], [blocker], decisions, readiness, demotion)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                expected_reason = (
                    "phase33-readiness-input-invalid"
                    if projection_name == "readiness"
                    else "phase33-demotion-input-invalid"
                )
                self.assertIn(expected_reason, result.stdout)

    def test_duplicate_normalized_decision_ids_are_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
        blocker_ref = f"{PHASE32_REGISTER}#exception-row"
        decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
        duplicate = self.decision("approve-demotion", "reference_demotion", "approve", blocker_ref)
        decisions.append(duplicate)
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [blocker], decisions, readiness, demotion)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "phase33-normalized-decisions-invalid",
            result.stdout,
        )

    def test_projection_decision_axis_and_value_must_authorize_projection(self) -> None:
        cases = [
            ("decision_type", "readiness"),
            ("decision_value", "reject"),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
                blocker_ref = f"{PHASE32_REGISTER}#exception-row"
                decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
                demotion_decision = decisions[1]
                demotion_decision[field] = value
                decision_axis = (
                    "demotion"
                    if demotion_decision["decision_type"] == "reference_demotion"
                    else demotion_decision["decision_type"]
                )
                demotion_decision["decision_axis"] = decision_axis
                demotion_decision["decision_targets"][0][
                    "decision_axis"
                ] = decision_axis
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [blocker], decisions, readiness, demotion)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "phase33-demotion-input-invalid",
                    result.stdout,
                )

    def test_projection_metadata_and_source_refs_must_match_normalized_decision(self) -> None:
        cases = [
            ("maintainer_role", "different-role"),
            ("source_row_refs", [f"{PHASE32_REGISTER}#different-row"]),
        ]
        for field, value in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
                blocker_ref = f"{PHASE32_REGISTER}#exception-row"
                decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
                demotion[field] = value
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [blocker], decisions, readiness, demotion)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "phase33-demotion-input-invalid",
                    result.stdout,
                )

    def test_normalized_decision_timestamp_must_be_iso_utc(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
        blocker = self.blocker_row("exception-row", source_ref, row_problem_kind="exception_requested")
        blocker_ref = f"{PHASE32_REGISTER}#exception-row"
        decisions, readiness, demotion = self.approved_projection_fixture(blocker_ref)
        decisions[1]["decision_timestamp"] = "not-even-a-timestamp"
        demotion["decision_timestamp"] = "not-even-a-timestamp"
        self.write_fixture(root, [self.receipt("simulator", source_ref)], [blocker], decisions, readiness, demotion)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "phase33-normalized-decisions-invalid",
            result.stdout,
        )

    def test_missing_invalid_stale_and_rejected_approval_write_durable_blocked_result(self) -> None:
        cases = [
            (None, "missing"),
            ({"phase_lifecycle_id": "stale", "authorization_state": "approved-input-recorded"}, "invalid"),
            ({"phase_lifecycle_id": "33-2026-07-04T01-36-41", "authorization_state": "unexpected"}, "invalid"),
            ({"phase_lifecycle_id": "33-2026-07-04T01-36-41", "authorization_state": "rejected"}, "valid"),
        ]
        for demotion, expected_validation in cases:
            with self.subTest(demotion=demotion):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                readiness = {
                    "phase": "33-maintainer-decision-inputs",
                    "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                    "handoff_state": "blocked-pending-maintainer-input",
                    "readiness_input_supplied": False,
                    "blocked_source_row_refs": [],
                }
                blocker_rows = []
                decisions = []
                if demotion and demotion.get("authorization_state") == "rejected":
                    blocker = self.blocker_row("demotion-row", source_ref)
                    blocker_rows.append(blocker)
                    blocker_ref = f"{PHASE32_REGISTER}#demotion-row"
                    decision = self.decision("reject-demotion", "reference_demotion", "reject", blocker_ref)
                    decisions.append(decision)
                    demotion.update(
                        {
                            "decision_id": decision["decision_id"],
                            "source_row_refs": decision["source_row_refs"],
                            "rationale": decision["rationale"],
                        }
                    )
                self.write_fixture(
                    root,
                    [self.receipt("simulator", source_ref)],
                    blocker_rows,
                    decisions,
                    readiness,
                    demotion,
                )

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertTrue((root / OUTPUT_DIR / "demotion-dry-run.json").exists())
                dry_run = self.read_json(root, f"{OUTPUT_DIR}/demotion-dry-run.json")
                self.assertEqual(dry_run["gate_state"], "blocked")
                self.assertEqual(dry_run["approval_validation_state"], expected_validation)
                if expected_validation == "invalid":
                    self.assertNotEqual(result.returncode, 0)

    def test_unreadable_approval_inputs_retain_minimal_blocked_artifacts(self) -> None:
        cases = [
            ("missing", "missing"),
            ("invalid-json", "invalid"),
            ("non-object", "invalid"),
            ("unsafe-ref", "invalid"),
            ("forbidden-field", "invalid"),
            ("forbidden-text", "invalid"),
            ("symlink", "invalid"),
        ]
        for failure_kind, expected_validation in cases:
            with self.subTest(failure_kind=failure_kind):
                # Arrange
                temp_dir, root = self.make_temp_root()
                self.addCleanup(temp_dir.cleanup)
                source_ref = "build/ci-evidence/phase23/upstream-simulator-result-row.json"
                self.write_fixture(root, [self.receipt("simulator", source_ref)], [])
                approval_path = root / "build/ci-evidence/phase33/demotion-decision-handoff.json"
                if failure_kind == "missing":
                    approval_path.unlink()
                elif failure_kind == "invalid-json":
                    approval_path.write_text("{", encoding="utf-8")
                elif failure_kind == "non-object":
                    approval_path.write_text("[]\n", encoding="utf-8")
                elif failure_kind == "symlink":
                    outside_path = root / "outside/demotion-decision-handoff.json"
                    outside_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(approval_path, outside_path)
                    approval_path.unlink()
                    approval_path.symlink_to(outside_path)
                else:
                    approval = self.read_json(root, "build/ci-evidence/phase33/demotion-decision-handoff.json")
                    if failure_kind == "unsafe-ref":
                        approval["source_row_refs"] = ["../unsafe-approval.json"]
                    elif failure_kind == "forbidden-field":
                        approval["token_value"] = "redacted-fixture-value"
                    else:
                        approval["rationale"] = "production demotion complete"
                    self.write_json(root, "build/ci-evidence/phase33/demotion-decision-handoff.json", approval)

                # Act
                result = self.run_quick(root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue((root / OUTPUT_DIR / "final-readiness-run-manifest.json").is_file())
                self.assertTrue((root / OUTPUT_DIR / "demotion-dry-run.json").is_file())
                manifest = self.read_json(root, f"{OUTPUT_DIR}/final-readiness-run-manifest.json")
                dry_run = self.read_json(root, f"{OUTPUT_DIR}/demotion-dry-run.json")
                self.assertEqual(manifest["run_state"], "blocked-source-failure")
                self.assertEqual(
                    manifest["source_failure_reason_code"],
                    "phase33-demotion-input-invalid",
                )
                self.assertEqual(dry_run["gate_state"], "blocked")
                self.assertEqual(dry_run["approval_validation_state"], expected_validation)


__all__ = ["Phase34FinalReadinessDemotionFailureMixin"]
