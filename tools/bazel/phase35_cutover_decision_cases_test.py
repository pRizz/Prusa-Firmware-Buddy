from __future__ import annotations

from phase35_test_support import (
    AUDIT_KINDS,
    AUDIT_REQUIRED_FIELDS,
    BLOCKED_REASONS,
    DECISION_FIELDS,
    GENERATED_ARTIFACTS,
    PHASE32_REGISTER,
    PHASE33_EXCEPTION_REGISTER,
    PHASE33_NORMALIZED_REGISTER,
    PHASE34_LEDGER,
    ROUTES,
    ROUTE_FIELDS,
    SOURCE_FAILURE_ARTIFACTS,
    SOURCE_FAILURE_MANIFEST_FIELDS,
    VERDICTS,
    Path,
    copy,
    hashlib,
    json,
    phase35,
    tempfile,
)


class Phase35CutoverDecisionCasesMixin:
    def test_cutover_01_contract_identity_lifecycle_and_closed_verdict_enum(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        identity = (
            contract["id"],
            contract["phase"],
            contract["phase_lifecycle_id"],
            contract["output_root"],
        )

        # Assert
        self.assertEqual(
            identity,
            (
                "phase35_cutover_decision_artifact_contract",
                "35-cutover-decision-artifact",
                "35-2026-07-25T21-06-10",
                "build/ci-evidence/phase35",
            ),
        )
        self.assertEqual(contract["requirement_ids"],
                         ["CUTOVER-01", "CUTOVER-02", "CUTOVER-03"])
        self.assertEqual(contract["verdict_enum"], VERDICTS)

    def test_cutover_02_contract_declares_exact_nine_kind_audit_schema(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        schema = contract["audit_link_schema"]

        # Assert
        self.assertEqual(schema["kinds"], AUDIT_KINDS)
        self.assertEqual(schema["required_fields"], AUDIT_REQUIRED_FIELDS)
        self.assertEqual(schema["optional_fields"], ["digest"])
        self.assertTrue(schema["exact_set_required"])

    def test_cutover_03_contract_declares_routes_artifacts_and_no_authority(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        authority = contract["authority_boundaries"]

        # Assert
        self.assertEqual(contract["route_enum"], ROUTES)
        self.assertEqual(contract["generated_artifacts"], GENERATED_ARTIFACTS)
        self.assertFalse(authority["accepts_caller_supplied_verdict"])
        self.assertFalse(authority["accepts_cutover_confirmation"])
        self.assertFalse(authority["accepts_demotion_approval"])
        self.assertFalse(authority["production_actions_authorized"])
        self.assertEqual(authority["reference_demotion_requirement"],
                         "POST-01")

    def test_contract_declares_exact_blocked_reasons_and_output_fields(
            self) -> None:
        # Arrange
        contract = self.contract()

        # Act / Assert
        self.assertEqual(contract["blocked_reason_codes"], BLOCKED_REASONS)
        self.assertEqual(contract["cutover_decision_fields"], DECISION_FIELDS)
        self.assertEqual(
            contract["demotion_projection"]["decision_validation_states"],
            [
                "missing", "malformed", "stale", "lifecycle-mismatched",
                "invalid", "valid"
            ],
        )
        self.assertEqual(
            contract["demotion_projection"]["decision_states"],
            ["missing", "approve", "reject"],
        )
        self.assertEqual(contract["demotion_projection"]["gate_states"],
                         ["blocked", "open"])

    def test_contract_declares_exact_source_failure_bundle(self) -> None:
        # Arrange
        contract = self.contract()

        # Act
        behavior = contract["source_failure_behavior"]

        # Assert
        self.assertEqual(behavior["generated_artifacts"],
                         SOURCE_FAILURE_ARTIFACTS)
        self.assertEqual(behavior["manifest_fields"],
                         SOURCE_FAILURE_MANIFEST_FIELDS)
        self.assertEqual(behavior["decision_fields"], DECISION_FIELDS)
        self.assertEqual(behavior["route_fields"], ROUTE_FIELDS)
        self.assertEqual(behavior["generation_state"], "blocked-source-error")
        self.assertEqual(behavior["cutover_verdict"], "blocked")
        self.assertEqual(behavior["route"], "targeted-blocker-repair")
        self.assertEqual(behavior["audit_link_counts_by_kind"],
                         {kind: 0
                          for kind in AUDIT_KINDS})
        self.assertEqual(behavior["repair_scope"], [])
        self.assertEqual(behavior["repair_scope_reason_code"],
                         "route-scope-incomplete")
        self.assertEqual(behavior["demotion_decision_validation_state"],
                         "invalid")
        self.assertEqual(behavior["demotion_decision_state"], "missing")
        self.assertEqual(behavior["demotion_decision_source_refs"], [])
        self.assertEqual(behavior["demotion_gate_state"], "blocked")
        self.assertTrue(behavior["requires_fresh_cutover_decision"])
        self.assertTrue(behavior["planning_only"])
        self.assertFalse(behavior["production_actions_authorized"])
        self.assertFalse(behavior["raw_evidence_consumed"])

    def test_cutover_01_truth_table_approves_only_unblocked_without_exceptions(
            self) -> None:
        # Arrange
        facts = self.valid_facts()

        # Act
        result = phase35.evaluate_verdict(facts)

        # Assert
        self.assertEqual(result["cutover_verdict"], "approved")
        self.assertEqual(result["reason_codes"], [])
        self.assertEqual(result["active_exception_ids"], [])

    def test_cutover_01_truth_table_approves_with_exact_active_exceptions(
            self) -> None:
        # Arrange
        facts = self.valid_facts()
        facts["active_exception_ids"] = ["exception-1"]
        facts["exceptions"] = [self.exception()]

        # Act
        result = phase35.evaluate_verdict(facts)

        # Assert
        self.assertEqual(result["cutover_verdict"], "approved-with-exceptions")
        self.assertEqual(result["active_exception_ids"], ["exception-1"])

    def test_cutover_01_truth_table_blocks_readiness_and_all_invalid_families(
            self) -> None:
        for reason_code in BLOCKED_REASONS:
            with self.subTest(reason_code=reason_code):
                # Arrange
                facts = self.valid_facts()
                facts["reason_codes"] = [reason_code]

                # Act
                result = phase35.evaluate_verdict(facts)

                # Assert
                self.assertEqual(result["cutover_verdict"], "blocked")
                self.assertIn(reason_code, result["reason_codes"])

    def test_cutover_01_truth_table_blocks_unknown_or_incomplete_fact_shapes(
            self) -> None:
        cases = [
            {},
            {
                "readiness_state": "unknown",
                "reason_codes": [],
                "active_exception_ids": [],
                "exceptions": []
            },
            {
                "readiness_state": "blocked",
                "reason_codes": [],
                "active_exception_ids": [],
                "exceptions": []
            },
            {
                "readiness_state": "unblocked",
                "reason_codes": [],
                "active_exception_ids": ["missing"],
                "exceptions": []
            },
        ]
        for facts in cases:
            with self.subTest(facts=facts):
                # Arrange / Act
                result = phase35.evaluate_verdict(facts)

                # Assert
                self.assertEqual(result["cutover_verdict"], "blocked")

    def test_cutover_reasons_ignore_independent_demotion_diagnostics(
            self) -> None:
        # Arrange
        ledger = [{
            "readiness_effect": "independent",
            "reason_codes": ["approval-missing"],
        }]

        # Act
        reasons = phase35.cutover_reason_codes("unblocked", ledger)

        # Assert
        self.assertEqual(reasons, [])

    def test_cutover_reasons_fail_closed_for_blocked_readiness_without_rows(
            self) -> None:
        # Arrange
        ledger: list[dict[str, object]] = []

        # Act
        reasons = phase35.cutover_reason_codes("blocked", ledger)

        # Assert
        self.assertEqual(reasons, ["readiness-input-invalid"])

    def test_cutover_01_exception_boundaries_fail_closed(self) -> None:
        canonical = self.exception()
        cases = [
            ("broad", {
                **canonical, "linked_blocker_refs":
                [f"{PHASE32_REGISTER}#other"]
            }),
            ("unmatched", self.exception(decision_id="other")),
            ("rejected", self.exception(decision_value="reject")),
            ("expired", {
                **canonical, "expiry_or_review_trigger": ""
            }),
            ("stale",
             self.exception(decision_timestamp="2020-01-01T00:00:00Z")),
            ("invalid", {
                **canonical, "owner_signoff_ref": ""
            }),
        ]
        for case_name, exception in cases:
            with self.subTest(case=case_name):
                # Arrange
                facts = self.valid_facts()
                facts["active_exception_ids"] = ["exception-1"]
                facts["exceptions"] = [exception]

                # Act
                result = phase35.evaluate_verdict(facts)

                # Assert
                self.assertEqual(result["cutover_verdict"], "blocked")
                self.assertIn("exception-invalid", result["reason_codes"])

    def test_cutover_01_legacy_fields_cannot_override_canonical_validation(
            self) -> None:
        # Arrange
        facts = self.valid_facts()
        facts["active_exception_ids"] = ["exception-1"]
        facts["exceptions"] = [{
            **self.exception(decision_timestamp="2020-01-01T00:00:00Z"),
            "validation_state":
            "valid",
            "active":
            True,
            "exact_scope":
            True,
        }]

        # Act
        result = phase35.evaluate_verdict(facts)

        # Assert
        self.assertEqual(result["cutover_verdict"], "blocked")
        self.assertIn("exception-invalid", result["reason_codes"])

    def test_cutover_01_phase34_ledger_is_the_active_exception_authority(
            self) -> None:
        # Arrange
        ledger = [{
            "coverage_state":
            "exception-covered",
            "exception_decision_refs": [
                "build/ci-evidence/phase33/normalized-decision-records.json#exception-1"
            ],
        }, {
            "coverage_state":
            "exception-uncovered",
            "exception_decision_refs": [
                "build/ci-evidence/phase33/normalized-decision-records.json#exception-2"
            ],
        }]

        # Act
        active_ids = phase35.active_exception_ids_from_ledger(ledger)

        # Assert
        self.assertEqual(active_ids, ["exception-1"])

    def test_cutover_03_route_truth_table_is_exclusive_and_planning_only(
            self) -> None:
        expected = {
            "approved": ("production-cutover-planning", False),
            "blocked": ("targeted-blocker-repair", True),
            "approved-with-exceptions": ("targeted-blocker-repair", True),
        }
        for verdict, (route_name, requires_fresh) in expected.items():
            with self.subTest(verdict=verdict):
                # Arrange / Act
                route = phase35.build_route(verdict, [])

                # Assert
                self.assertEqual(route["route"], route_name)
                self.assertEqual(route["source_verdict"], verdict)
                self.assertEqual(route["requires_fresh_cutover_decision"],
                                 requires_fresh)
                self.assertTrue(route["planning_only"])
                self.assertFalse(route["production_actions_authorized"])

    def test_t_35_01_audit_links_cover_all_nine_categories_deterministically(
            self) -> None:
        # Arrange
        sources = list(reversed(self.audit_sources()))

        # Act
        first = phase35.derive_audit_links(sources)
        second = phase35.derive_audit_links(copy.deepcopy(sources))

        # Assert
        self.assertEqual(first, second)
        self.assertEqual([link["kind"] for link in first], AUDIT_KINDS)
        self.assertEqual({link["kind"] for link in first}, set(AUDIT_KINDS))
        for link in first:
            self.assertEqual(list(link)[:6], AUDIT_REQUIRED_FIELDS)
            self.assertRegex(link["link_id"], r"^audit-[a-z0-9-]+$")
            self.assertRegex(link["digest"], r"^[0-9a-f]{64}$")

    def test_t_35_01_external_audit_refs_omit_digest(self) -> None:
        # Arrange
        sources = self.audit_sources()
        sources[0]["target_ref"] = "external://phase31/sanitized-packet"

        # Act
        links = phase35.derive_audit_links(sources)
        external_link = next(link for link in links
                             if link["kind"] == "evidence-packet")

        # Assert
        self.assertNotIn("digest", external_link)

    def test_t_35_01_exact_set_anti_join_blocks_every_mismatch(self) -> None:
        expected = phase35.derive_audit_links(self.audit_sources())
        mutations = {}
        mutations["audit-link-missing"] = expected[1:]
        mutations["audit-link-extra"] = expected + [{
            **expected[0],
            "link_id": "audit-extra",
            "target_id": "extra",
        }]
        mutations["audit-link-duplicate"] = expected + [dict(expected[0])]
        dangling = copy.deepcopy(expected)
        dangling[0]["target_ref"] = "build/ci-evidence/phase34/missing.json"
        mutations["audit-link-dangling"] = dangling
        lifecycle = copy.deepcopy(expected)
        lifecycle[0]["source_phase_lifecycle_id"] = "stale"
        mutations["audit-link-lifecycle-mismatched"] = lifecycle
        category = copy.deepcopy(expected)
        category[0]["kind"] = "blocker"
        mutations["audit-link-category-mismatched"] = category
        digest = copy.deepcopy(expected)
        digest[0]["digest"] = "0" * 64
        mutations["audit-link-digest-mismatched"] = digest

        for expected_reason, emitted in mutations.items():
            with self.subTest(expected_reason=expected_reason):
                # Arrange / Act
                reasons = phase35.validate_audit_links(expected, emitted)

                # Assert
                self.assertIn(expected_reason, reasons)

    def test_t_35_01_link_digest_uses_canonical_sanitized_projection(
            self) -> None:
        # Arrange
        source = self.audit_sources()[0]
        canonical = json.dumps(source["digest_source"],
                               sort_keys=True,
                               separators=(",", ":")).encode()

        # Act
        link = phase35.derive_audit_links([source])[0]

        # Assert
        self.assertEqual(link["digest"], hashlib.sha256(canonical).hexdigest())

    def test_t_35_01_local_audit_links_resolve_targets_and_fragments(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        target_ref = "build/ci-evidence/phase34/rows.json#row-1"
        target = {"row_id": "row-1", "value": "sanitized"}
        target_path = root / target_ref.split("#", 1)[0]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps({"rows": [target]}),
                               encoding="utf-8")
        link = {
            "target_ref": target_ref,
            "digest":
            hashlib.sha256(phase35.canonical_json(target)).hexdigest(),
        }

        # Act
        reasons = phase35.validate_resolved_audit_links(root, [link])

        # Assert
        self.assertEqual(reasons, [])

    def test_t_35_01_dangling_local_audit_link_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        link = {
            "target_ref": "build/ci-evidence/phase34/does-not-exist.json",
            "digest": "0" * 64,
        }

        # Act
        reasons = phase35.validate_resolved_audit_links(root, [link])

        # Assert
        self.assertEqual(reasons, ["audit-link-dangling"])

    def test_t_35_01_symlinked_local_audit_target_fails_closed(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside_target = Path(outside_dir.name) / "rows.json"
        target = {"row_id": "row-1", "value": "outside"}
        outside_target.write_text(json.dumps({"rows": [target]}),
                                  encoding="utf-8")
        target_ref = "build/ci-evidence/phase34/rows.json#row-1"
        target_path = root / target_ref.split("#", 1)[0]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.symlink_to(outside_target)
        link = {
            "target_ref": target_ref,
            "digest":
            hashlib.sha256(phase35.canonical_json(target)).hexdigest(),
        }

        # Act
        reasons = phase35.validate_resolved_audit_links(root, [link])

        # Assert
        self.assertEqual(reasons, ["audit-link-dangling"])

    def test_cutover_03_repair_scope_uses_exact_ordinary_exit_review_refs(
            self) -> None:
        # Arrange
        blocker = self.blocker_row()
        ledger = self.ledger_row()

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [ledger], [],
                                                    [])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(len(scope), 1)
        self.assertEqual(
            scope[0]["required_action_ref"],
            f"{PHASE32_REGISTER}#blocker-1/required_next_action",
        )
        self.assertEqual(
            scope[0]["exit_review_criterion_refs"],
            [
                f"{PHASE32_REGISTER}#blocker-1/affected_gate",
                f"{PHASE32_REGISTER}#blocker-1/required_next_action",
                f"{PHASE34_LEDGER}#ledger-1/reason_codes",
                f"{PHASE34_LEDGER}#ledger-1/readiness_effect",
            ],
        )

    def test_cutover_03_repair_scope_adds_exact_exception_criteria(
            self) -> None:
        # Arrange
        blocker = self.blocker_row(blocker_kind="exception_request")
        exception = {
            "decision_id": "exception-1",
            "source_row_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "linked_blocker_refs": [f"{PHASE32_REGISTER}#blocker-1"],
            "expiry_or_review_trigger": "review-before-cutover",
            "affected_gates": ["final-simulator-evidence"],
        }
        ledger = {
            **self.ledger_row(), "exception_decision_refs":
            [f"{PHASE33_NORMALIZED_REGISTER}#exception-1"]
        }

        # Act
        scope, reasons = phase35.build_repair_scope([blocker], [ledger],
                                                    [exception], [])

        # Assert
        self.assertEqual(reasons, [])
        self.assertEqual(
            scope[0]["exit_review_criterion_refs"][-2:],
            [
                f"{PHASE33_EXCEPTION_REGISTER}#exception-1/expiry_or_review_trigger",
                f"{PHASE33_EXCEPTION_REGISTER}#exception-1/affected_gates",
            ],
        )
