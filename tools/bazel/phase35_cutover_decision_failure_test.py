from __future__ import annotations

from phase35_test_support import (
    PHASE32_REGISTER,
    PHASE33_EXCEPTION_REGISTER,
    PHASE33_NORMALIZED_REGISTER,
    PHASE33_RESIDUAL_REGISTER,
    PHASE34_LEDGER,
    Path,
    json,
    phase35,
    tempfile,
)


class Phase35CutoverDecisionFailureMixin:
    def test_cutover_03_write_bundle_preserves_exception_covered_approval(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        blocker = self.blocker_row(blocker_kind="exception_request")
        exception = self.exception()
        unrelated_ref = f"{PHASE32_REGISTER}#unrelated"
        source = {
            "receipts": [{
                "receipt_ref": "external://phase31/sanitized-packet",
                "receipt": {
                    "submission_id": "submission-1"
                },
            }],
            "blockers": [blocker],
            "exceptions": [exception],
            "residuals": [{
                "decision_id":
                "risk-unrelated",
                "source_row_refs": [unrelated_ref],
                "linked_blocker_refs": [unrelated_ref],
                "follow_up_refs": ["external://phase33/risk-follow-up"],
                "affected_gates": ["other-gate"],
            }],
            "retained": [{
                "decision_id": "retained-unrelated",
                "source_row_refs": [unrelated_ref],
            }],
            "readiness_handoff": {
                "decision_id": "readiness-1"
            },
            "demotion_handoff":
            self.demotion_handoff(supplied=False),
            "packet": {
                "readiness_state": "unblocked",
                "reason_codes": [],
            },
            "dry_run":
            self.demotion_dry_run(
                readiness_state="unblocked",
                approval_validation_state="missing",
                approval_decision_state="missing",
                reason_codes=["approval-missing"],
            ),
            "ledger": {
                "rows": [{
                    **self.ledger_row(),
                    "coverage_state":
                    "exception-covered",
                    "readiness_effect":
                    "unblocked",
                    "reason_codes": [],
                    "exception_decision_refs":
                    [f"{PHASE33_NORMALIZED_REGISTER}#exception-1"],
                }]
            },
            "normalized": [],
        }
        self.write_audit_targets(root, source)
        contract = self.contract()
        phase34_contract = json.loads((
            root /
            "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json"
        ).read_text(encoding="utf-8"))

        # Act
        phase35.write_bundle(
            root,
            Path("build/ci-evidence/phase35"),
            contract,
            phase34_contract,
            {},
            source,
        )

        # Assert
        decision = json.loads(
            (root /
             "build/ci-evidence/phase35/cutover-decision.json").read_text(
                 encoding="utf-8"))
        route = json.loads(
            (root /
             "build/ci-evidence/phase35/next-milestone-route.json").read_text(
                 encoding="utf-8"))
        self.assertEqual(decision["cutover_verdict"],
                         "approved-with-exceptions")
        self.assertNotIn("route-scope-incomplete", decision["reason_codes"])
        self.assertEqual(len(route["follow_up_scope"]), 1)
        self.assertEqual(
            route["follow_up_scope"][0]["exception_refs"],
            [f"{PHASE33_EXCEPTION_REGISTER}#exception-1"],
        )

    def test_cutover_03_repair_scope_adds_exact_residual_risk_criteria(
            self) -> None:
        # Arrange
        blocker = self.blocker_row()
        residual = {
            "decision_id": "risk-1",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "follow_up_refs": ["external://phase33/risk-follow-up"],
            "affected_gates": ["final-simulator-evidence"],
        }
        ledger = {
            **self.ledger_row(), "residual_risk_decision_refs":
            [f"{PHASE33_NORMALIZED_REGISTER}#risk-1"]
        }

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [ledger], [],
                                                    [residual])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(
            scope[0]["exit_review_criterion_refs"][-2:],
            [
                f"{PHASE33_RESIDUAL_REGISTER}#risk-1/follow_up_refs",
                f"{PHASE33_RESIDUAL_REGISTER}#risk-1/affected_gates",
            ],
        )

    def test_cutover_03_repair_scope_covers_phase34_created_blocker(
            self) -> None:
        # Arrange
        ledger = {
            "row_id": "phase34-required-stream",
            "classification_ref": "",
            "source_stream": "simulator",
            "source_ref":
            "build/ci-evidence/phase23/upstream-simulator-result-row.json",
            "requirement_ids": ["INTAKE-01"],
            "affected_gates": ["final-simulator-evidence"],
            "reason_codes": ["required-row-missing"],
            "readiness_effect": "blocked",
        }

        # Act
        scope, reasons = phase35.build_repair_scope([], [ledger], [], [])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(len(scope), 1)
        self.assertEqual(
            scope[0]["blocker_refs"],
            [f"{PHASE34_LEDGER}#phase34-required-stream"],
        )
        self.assertEqual(
            scope[0]["required_action_ref"],
            f"{PHASE34_LEDGER}#phase34-required-stream/source_ref",
        )

    def test_cutover_03_unresolved_or_fabricated_scope_stays_blocked(
            self) -> None:
        cases = [
            ("missing-ledger", [], [], []),
            (
                "wrong-classification",
                [{
                    **self.ledger_row(), "classification_ref":
                    f"{PHASE32_REGISTER}#other"
                }],
                [],
                [],
            ),
            (
                "fabricated-exception",
                [{
                    **self.ledger_row(), "exception_decision_refs":
                    [f"{PHASE33_NORMALIZED_REGISTER}#exception-1"]
                }],
                [{
                    "decision_id": "exception-1",
                    "source_row_refs": [f"{PHASE32_REGISTER}#other"],
                    "linked_blocker_refs": [f"{PHASE32_REGISTER}#other"],
                    "expiry_or_review_trigger": "review",
                    "affected_gates": ["final-simulator-evidence"],
                }],
                [],
            ),
        ]
        for case_name, ledger, exceptions, residuals in cases:
            with self.subTest(case=case_name):
                # Arrange / Act
                scope, reasons = phase35.build_repair_scope(
                    [self.blocker_row()],
                    ledger,
                    exceptions,
                    residuals,
                )
                route = phase35.build_route("blocked", scope)

                # Assert
                self.assertIn("route-scope-incomplete", reasons)
                self.assertEqual(route["source_verdict"], "blocked")
                self.assertEqual(route["route"], "targeted-blocker-repair")

    def test_t_35_06_demotion_missing_is_not_collapsed(self) -> None:
        # Arrange
        handoff = self.demotion_handoff(supplied=False)
        dry_run = self.demotion_dry_run(
            approval_validation_state="missing",
            approval_decision_state="missing",
            reason_codes=["approval-missing"],
        )

        # Act
        projection = phase35.project_demotion(handoff, [], dry_run)

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"],
                         "missing")
        self.assertEqual(projection["demotion_decision_state"], "missing")
        self.assertEqual(projection["demotion_decision_source_refs"], [])
        self.assertEqual(projection["demotion_gate_state"], "blocked")
        self.assertEqual(projection["demotion_gate_reason_codes"],
                         ["approval-missing"])

    def test_t_35_06_demotion_malformed_stale_lifecycle_and_other_invalid_remain_distinct(
            self) -> None:
        cases = [
            ("malformed", {
                "phase": 3
            }, [], "malformed"),
            (
                "stale",
                self.demotion_handoff(),
                [
                    self.demotion_decision(
                        decision_timestamp="2020-01-01T00:00:00Z")
                ],
                "stale",
            ),
            (
                "lifecycle-mismatched",
                self.demotion_handoff(lifecycle="stale"),
                [self.demotion_decision(lifecycle="stale")],
                "lifecycle-mismatched",
            ),
            (
                "invalid",
                self.demotion_handoff(),
                [self.demotion_decision(decision_value="unknown")],
                "invalid",
            ),
        ]
        for case_name, handoff, records, expected_state in cases:
            with self.subTest(case=case_name):
                # Arrange
                dry_run = self.demotion_dry_run()

                # Act
                projection = phase35.project_demotion(handoff, records,
                                                      dry_run)

                # Assert
                self.assertEqual(
                    projection["demotion_decision_validation_state"],
                    expected_state)
                self.assertEqual(projection["demotion_gate_state"], "blocked")

    def test_t_35_06_valid_reject_is_valid_and_preserves_safe_source_refs(
            self) -> None:
        # Arrange
        handoff = self.demotion_handoff()
        records = [self.demotion_decision(decision_value="reject")]
        dry_run = self.demotion_dry_run(
            approval_decision_state="reject",
            reason_codes=["approval-rejected"],
        )

        # Act
        projection = phase35.project_demotion(handoff, records, dry_run)

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"],
                         "valid")
        self.assertEqual(projection["demotion_decision_state"], "reject")
        self.assertEqual(
            projection["demotion_decision_source_refs"],
            [f"{PHASE32_REGISTER}#blocker-1"],
        )
        self.assertEqual(projection["demotion_gate_reason_codes"],
                         ["approval-rejected"])

    def test_t_35_06_valid_approve_does_not_upgrade_cutover_or_gate(
            self) -> None:
        # Arrange
        handoff = self.demotion_handoff()
        records = [self.demotion_decision()]
        dry_run = self.demotion_dry_run(gate_state="blocked",
                                        reason_codes=["readiness-blocked"])

        # Act
        projection = phase35.project_demotion(handoff, records, dry_run)
        verdict = phase35.evaluate_verdict({
            "readiness_state":
            "blocked",
            "reason_codes": ["readiness-blocked"],
            "active_exception_ids": [],
            "exceptions": [],
        })

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"],
                         "valid")
        self.assertEqual(projection["demotion_decision_state"], "approve")
        self.assertEqual(projection["demotion_gate_state"], "blocked")
        self.assertEqual(verdict["cutover_verdict"], "blocked")

    def test_t_35_06_open_gate_does_not_upgrade_cutover_verdict(self) -> None:
        # Arrange
        dry_run = self.demotion_dry_run(gate_state="open", reason_codes=[])

        # Act
        projection = phase35.project_demotion(
            self.demotion_handoff(),
            [self.demotion_decision()],
            dry_run,
        )
        verdict = phase35.evaluate_verdict({
            "readiness_state":
            "blocked",
            "reason_codes": ["readiness-blocked"],
            "active_exception_ids": [],
            "exceptions": [],
        })

        # Assert
        self.assertEqual(projection["demotion_gate_state"], "open")
        self.assertEqual(verdict["cutover_verdict"], "blocked")

    def test_t_35_06_stale_approval_cannot_preserve_open_gate(self) -> None:
        # Arrange
        handoff = self.demotion_handoff()
        records = [
            self.demotion_decision(decision_timestamp="2020-01-01T00:00:00Z")
        ]
        dry_run = self.demotion_dry_run(
            gate_state="open",
            approval_validation_state="invalid",
            reason_codes=[],
        )

        # Act
        projection = phase35.project_demotion(handoff, records, dry_run)

        # Assert
        self.assertEqual(projection["demotion_decision_validation_state"],
                         "stale")
        self.assertEqual(projection["demotion_gate_state"], "blocked")
        self.assertIn("approval-invalid",
                      projection["demotion_gate_reason_codes"])

    def test_t_35_02_paths_reject_absolute_traversal_wrong_root_overlap_and_symlink_escape(
            self) -> None:
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside = root / "outside"
        outside.mkdir()
        symlink_output = root / "build/ci-evidence/phase35"
        symlink_output.parent.mkdir(parents=True)
        symlink_output.symlink_to(outside, target_is_directory=True)
        cases = [
            ("/tmp/phase34", "build/ci-evidence/phase35"),
            ("../phase34", "build/ci-evidence/phase35"),
            ("build/ci-evidence/phase30", "build/ci-evidence/phase35"),
            ("build/ci-evidence/phase34", "build/ci-evidence/phase34"),
            ("build/ci-evidence/phase34", "build/ci-evidence/phase35"),
        ]
        for phase34_dir, output_dir in cases:
            with self.subTest(phase34_dir=phase34_dir, output_dir=output_dir):
                # Arrange / Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.validate_paths(root, phase34_dir, output_dir)

    def test_t_35_02_source_artifact_file_symlink_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside_artifact = Path(outside_dir.name) / "manifest.json"
        outside_artifact.write_text(json.dumps({"sentinel": "outside"}),
                                    encoding="utf-8")
        relative_path = Path(
            "build/ci-evidence/phase34/final-readiness-run-manifest.json")
        source_path = root / relative_path
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.symlink_to(outside_artifact)

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "contains a symlink escape"):
            phase35.load_json(root, relative_path)

    def test_t_35_02_source_artifact_parent_symlink_is_rejected(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside_artifact = Path(outside_dir.name) / "snapshot.json"
        outside_artifact.write_text(json.dumps({"sentinel": "outside"}),
                                    encoding="utf-8")
        relative_path = Path(
            "build/ci-evidence/phase34/contract-snapshots/snapshot.json")
        symlinked_parent = root / relative_path.parent
        symlinked_parent.parent.mkdir(parents=True, exist_ok=True)
        symlinked_parent.symlink_to(Path(outside_dir.name),
                                    target_is_directory=True)

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "contains a symlink escape"):
            phase35.load_json(root, relative_path)

    def test_t_35_03_security_rejects_forbidden_fields_text_raw_payloads_and_unsafe_refs(
            self) -> None:
        cases = [
            {
                "token_value": "redacted"
            },
            {
                "nested": {
                    "private_key": "redacted"
                }
            },
            {
                "rationale": "production demotion complete"
            },
            {
                "raw_payload": {
                    "data": "not-allowed"
                }
            },
            {
                "source_refs": ["../unsafe.json"]
            },
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                # Arrange / Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.scan_security(payload)

    def test_t_35_03_external_refs_reject_traversal_and_malformed_uris(
            self) -> None:
        cases = [
            "external://phase31/../../private",
            "external://phase31/%2e%2e/private",
            "external://phase31/safe\\private",
            "external://phase31/safe%5c..%5cprivate",
            "external://phase31/safe%0aprivate",
            "external://phase31/safe#row%5c..%5cprivate",
            "external://phase31/safe%2",
            "external://phase99/safe",
            "external://phase31/safe?query=unsafe",
            "external://phase31/safe#",
            "external://phase31/safe#row/../private",
            "maintainer://owner/../private",
            "owner://phase34/safe\u0001",
        ]
        for ref in cases:
            with self.subTest(ref=ref):
                # Arrange / Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.validate_ref(ref)

    def test_t_35_03_external_refs_accept_contract_rooted_safe_uris(
            self) -> None:
        # Arrange
        refs = [
            "external://phase31/sanitized-packet",
            "maintainer://cutover-owner",
            "owner://phase34/simulator",
        ]

        # Act / Assert
        for ref in refs:
            phase35.validate_ref(ref)
