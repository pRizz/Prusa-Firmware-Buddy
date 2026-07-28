from __future__ import annotations

from phase35_test_support import (
    AUDIT_KINDS,
    PHASE32_REGISTER,
    VERDICTS,
    hashlib,
    json,
    phase35,
)


class Phase35CutoverDecisionSecurityMixin:
    def test_t_35_04_lifecycle_and_contract_drift_fail_closed(self) -> None:
        # Arrange
        contract = self.contract()
        manifest = {
            "artifact_name": "phase34-final-readiness-demotion-dry-run",
            "phase_lifecycle_id": "stale",
            "output_root": "build/ci-evidence/phase34",
            "raw_evidence_consumed": False,
            "generated_artifacts": [],
        }

        # Act / Assert
        with self.assertRaises(phase35.VerificationError):
            phase35.validate_phase34_manifest(contract, manifest)

    def test_t_35_03_snapshots_reject_secret_fields_and_uncontracted_fields(
            self) -> None:
        # Arrange
        contract = self.contract()
        secret_manifest = {
            "accepted_receipt_snapshot_ref":
            "build/ci-evidence/phase34/contract-snapshots/phase31-accepted-receipts.json",
            "artifact_name": "phase34-final-readiness-demotion-dry-run",
            "generated_artifacts": phase35.PHASE34_ARTIFACTS,
            "generated_at_utc": "2026-07-25T22:18:11Z",
            "output_root": "build/ci-evidence/phase34",
            "phase": "34-final-readiness-and-demotion-dry-run",
            "phase_lifecycle_id": phase35.PHASE34_LIFECYCLE_ID,
            "raw_evidence_consumed": False,
            "snapshot_refs": [],
            "source_refs": [],
            "token_value": "secret-bearing-value",
        }
        uncontracted_contract = {
            **contract, "unexpected": {
                "rationale": "not contracted"
            }
        }

        # Act / Assert
        with self.assertRaises(phase35.VerificationError):
            phase35.validate_phase34_manifest(contract, secret_manifest)
        with self.assertRaises(phase35.VerificationError):
            phase35.validate_snapshot(
                "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
                uncontracted_contract,
            )

    def test_t_35_03_snapshot_scan_permits_declared_contract_vocabulary(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        phase35.validate_snapshot(
            "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
            contract,
        )

        # Assert
        self.assertIn("production demotion complete",
                      contract["security"]["prohibited_text_markers"])

    def test_t_35_04_phase33_register_digest_rejects_post_phase34_mutation(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        register_ref = "build/ci-evidence/phase33/exception-decision-register.json"
        register_path = root / register_ref
        register_path.parent.mkdir(parents=True, exist_ok=True)
        original = {"rows": []}
        register_path.write_text(json.dumps(original), encoding="utf-8")
        digest = hashlib.sha256(phase35.canonical_json(original)).hexdigest()
        refs = {"exception_decision_register": register_ref}
        digests = {"exception_decision_register": digest}
        register_path.write_text(json.dumps(
            {"rows": [{
                "decision_id": "late"
            }]}),
                                 encoding="utf-8")

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "changed after Phase 34 validation"):
            phase35.reached_register(root, refs, digests,
                                     "exception_decision_register")

    def test_t_35_04_exception_projection_must_equal_normalized_decision(
            self) -> None:
        # Arrange
        normalized = [{
            "decision_id": "exception-1",
            "decision_type": "exception",
            "decision_value": "approve",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
        }]
        projection = [{
            **normalized[0],
            "decision_value": "reject",
            "scope": "exact",
            "expiry_or_review_trigger": "review-before-cutover",
            "affected_requirements": ["CUTOVER-01"],
            "affected_gates": ["final-simulator-evidence"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
        }]

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "projection differs"):
            phase35.validate_register_projection(projection, normalized,
                                                 "exception")

    def test_t_35_04_exception_projection_rejects_legacy_validation_fields(
            self) -> None:
        # Arrange
        normalized = [{
            "decision_id": "exception-1",
            "decision_type": "exception",
            "decision_value": "approve",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
        }]
        projection = [{
            **normalized[0],
            "scope": "exact",
            "expiry_or_review_trigger": "review-before-cutover",
            "affected_requirements": ["CUTOVER-01"],
            "affected_gates": ["final-simulator-evidence"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "validation_state": "valid",
            "active": True,
            "exact_scope": True,
        }]

        # Act / Assert
        with self.assertRaisesRegex(phase35.VerificationError,
                                    "forbidden legacy"):
            phase35.validate_register_projection(projection, normalized,
                                                 "exception")

    def test_t_35_05_caller_supplied_authority_flags_are_rejected(
            self) -> None:
        forbidden_options = [
            "--verdict",
            "--route",
            "--cutover-confirmation",
            "--demotion-approval",
            "--evidence-payload",
        ]

        # Arrange / Act
        parser = phase35.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }

        # Assert
        self.assertTrue(set(forbidden_options).isdisjoint(option_strings))

    def test_t_35_05_route_overclaims_are_impossible(self) -> None:
        for verdict in VERDICTS:
            with self.subTest(verdict=verdict):
                # Arrange / Act
                route = phase35.build_route(verdict, [])

                # Assert
                self.assertTrue(route["planning_only"])
                self.assertFalse(route["production_actions_authorized"])

    def test_t_35_03_markdown_and_json_use_one_shared_projection(self) -> None:
        # Arrange
        links = phase35.derive_audit_links(self.audit_sources())
        decision = {
            "cutover_verdict": "blocked",
            "reason_codes": ["readiness-blocked"],
            "readiness_state": "blocked",
            "active_exception_ids": [],
            "blocker_ids": ["blocker-1"],
            "audit_link_counts_by_kind": {
                kind: 1
                for kind in AUDIT_KINDS
            },
            "demotion_decision_validation_state": "missing",
            "demotion_decision_state": "missing",
            "demotion_decision_source_refs": [],
            "demotion_gate_state": "blocked",
            "demotion_gate_reason_codes": ["approval-missing"],
        }
        route = phase35.build_route("blocked", [])

        # Act
        report = phase35.render_report(decision, route, links)

        # Assert
        self.assertIn("cutover_verdict: blocked", report)
        self.assertIn("route: targeted-blocker-repair", report)
        self.assertIn("demotion_decision_validation_state: missing", report)
        self.assertIn("demotion_gate_state: blocked", report)
        for kind in AUDIT_KINDS:
            self.assertIn(f"{kind}: 1", report)

    def test_default_projection_is_blocked_repair_without_synthesized_authority(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        default = contract["default_behavior"]

        # Assert
        self.assertEqual(default["cutover_verdict"], "blocked")
        self.assertEqual(default["route"], "targeted-blocker-repair")
        self.assertEqual(default["demotion_decision_validation_state"],
                         "missing")
        self.assertEqual(default["demotion_decision_state"], "missing")
        self.assertEqual(default["demotion_decision_source_refs"], [])
        self.assertEqual(default["demotion_gate_state"], "blocked")
        self.assertFalse(default["synthesizes_evidence"])
        self.assertFalse(default["synthesizes_approval"])
        self.assertFalse(default["synthesizes_exception"])
        self.assertFalse(default["synthesizes_demotion_authorization"])

    def test_wiring_contract_requires_exact_bazel_workflow_and_just_strings(
            self) -> None:
        # Arrange
        expected = phase35.required_wiring_strings()

        # Act / Assert
        self.assertIn("phase35_source_ref_manifests", expected["tools_bazel"])
        self.assertIn("phase35_verify", expected["tools_bazel"])
        self.assertIn("phase35_verify_tests", expected["tools_bazel"])
        self.assertIn("phase35_cutover_decision_artifact_docs",
                      expected["root_bazel"])
        self.assertIn("phase35_verify_tests)", expected["workflow"])
        self.assertIn("phase35_verify)", expected["workflow"])
        self.assertEqual(
            expected["just"],
            [
                "phase35-verify:",
                "bazel run //tools/bazel:phase35_verify_tests",
                "bazel run //tools/bazel:phase35_verify",
            ],
        )
