from phase34_test_contract import *


class Phase34TestSupport(unittest.TestCase):

    def load_module(self):
        spec = importlib.util.spec_from_file_location(
            "phase34_final_readiness_demotion_dry_run", VERIFIER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def write_json(self, root: Path, relative_path: str, value: object) -> str:
        full_path = root / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(value, indent=2, sort_keys=True) +
                             "\n",
                             encoding="utf-8")
        return relative_path

    def write_text(self, root: Path, relative_path: str, value: str) -> None:
        full_path = root / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(value, encoding="utf-8")

    def read_json(self, root: Path, relative_path: str) -> dict[str, object]:
        return json.loads((root / relative_path).read_text(encoding="utf-8"))

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for relative_path in [
                "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json",
                "tools/bazel/manifests/phase31_final_evidence_intake_contract.json",
                "tools/bazel/manifests/phase32_blocker_register_triage_contract.json",
                "tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json",
                "tools/bazel/manifests/phase28_final_readiness_packet_contract.json",
                "tools/bazel/phase34_decision_reconciliation.py",
                "tools/bazel/phase34_publication_state.py",
                "tools/bazel/phase34_source_validation.py",
                "tools/bazel/phase34_decision_validation.py",
                "tools/bazel/phase34_readiness_policy.py",
                "tools/bazel/phase34_coverage_diagnostics.py",
                "tools/bazel/phase34_bundle_publication.py",
                "tools/bazel/phase34_readiness_wiring.py",
        ]:
            source = ROOT / relative_path
            destination = root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        if VERIFIER.exists():
            destination = root / VERIFIER.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(VERIFIER, destination)
        self.write_text(root, "BUILD.bazel", "")
        self.write_text(root, "tools/bazel/BUILD.bazel", "")
        self.write_text(root, "tools/bazel/rust_workflow.sh",
                        "#!/usr/bin/env bash\n")
        self.write_text(root, "justfile", "")
        return temp_dir, root

    def receipt(
        self,
        stream: str,
        source_ref: str,
        *,
        evidence_status: str = "passed",
        redaction_status: str = "passed",
        source_ref_status: str = "passed",
        exception_status: str = "none",
    ) -> dict[str, object]:
        return {
            "artifact_reference_summary": {
                "artifact_refs":
                [f"external://{stream}/sanitized-report.json"],
            },
            "consumed_upstream_row_refs": [source_ref],
            "evidence_status": evidence_status,
            "exception_status": exception_status,
            "failure_reason":
            "" if evidence_status == "passed" else f"{stream} evidence failed",
            "finality_status": "accepted-final",
            "packet_sha256": "a" * 64,
            "receipt_generated_at_utc": "2026-07-25T18:30:00Z",
            "redaction_status": redaction_status,
            "requirement_ids": ["READY-01"],
            "source_contract": f"tools/bazel/manifests/{stream}_contract.json",
            "source_phase": f"{stream}-evidence",
            "source_ref_status": source_ref_status,
            "stream": stream,
            "submission_id": f"phase31-{stream}-fixture",
            "submitter_identity_ref": "maintainer://phase34-test",
            "validator_command": ["python3", "sanitized-validator.py"],
            "validator_output_refs": [source_ref],
        }

    def required_stream_receipts(self) -> list[dict[str, object]]:
        return [
            self.receipt(stream, source_ref)
            for stream, source_ref in REQUIRED_STREAM_SOURCE_REFS.items()
        ]

    def blocker_row(
        self,
        row_id: str,
        source_ref: str,
        *,
        row_problem_kind: str = "failed",
        affected_gate: str = "final-simulator-evidence",
    ) -> dict[str, object]:
        return {
            "row_id":
            row_id,
            "source_stream":
            "simulator",
            "source_ref":
            source_ref,
            "requirement_ids": ["READY-01"],
            "affected_gate":
            affected_gate,
            "row_problem_kind":
            row_problem_kind,
            "blocker_kind":
            "exception_request"
            if row_problem_kind == "exception_requested" else "repair_item",
            "severity":
            "critical"
            if row_problem_kind != "exception_requested" else "medium",
            "owner_ref":
            "maintainer://phase34-test",
            "required_next_action":
            "Resolve before readiness.",
            "decision_impact":
            "exception_decision_required" if row_problem_kind
            == "exception_requested" else "final_readiness_blocked",
            "proof_eligibility":
            "ineligible",
            "evidence_refs": [source_ref],
        }

    def decision_domain_row(
        self,
        row_id: str,
        decision_axis: str,
        decision_subject_id: str,
        *,
        producer_phase: str = "phase27",
        source_domain: str = "retained_code",
        source_stream: str = "retained-code",
    ) -> dict[str, object]:
        return {
            "row_id":
            row_id,
            "source_domain":
            source_domain,
            "producer_phase":
            producer_phase,
            "producer_artifact_kind":
            f"{producer_phase}_{decision_axis}_register",
            "source_row_kind":
            f"{decision_axis}_decision",
            "source_subject_id":
            decision_subject_id,
            "decision_axis":
            decision_axis,
            "decision_subject_id":
            decision_subject_id,
            "source_stream":
            source_stream,
            "source_ref":
            (f"build/ci-evidence/{producer_phase}/"
             f"{decision_axis}-register.json#{decision_subject_id}"),
            "requirement_ids": ["READY-01"],
            "affected_gate":
            "final-readiness",
            "row_problem_kind":
            "missing",
            "blocker_kind":
            "unresolved_decision_blocker",
            "severity":
            "medium",
            "owner_ref":
            "maintainer://phase34-test",
            "required_next_action":
            "Record an exact typed maintainer decision.",
            "decision_impact":
            f"{decision_axis}_decision_required",
            "proof_eligibility":
            "ineligible",
            "evidence_refs": [
                f"build/ci-evidence/{producer_phase}/{decision_axis}-register.json"
            ],
        }

    def decision(
        self,
        decision_id: str,
        decision_type: str,
        decision_value: str,
        blocker_ref: str,
        *,
        affected_gate: str = "final-simulator-evidence",
        decision_subject_id: str | None = None,
    ) -> dict[str, object]:
        decision_axis = ("demotion" if decision_type == "reference_demotion"
                         else decision_type)
        maybe_subject_id = decision_subject_id or blocker_ref.rsplit("#",
                                                                     1)[-1]
        row = {
            "decision_id":
            decision_id,
            "decision_type":
            decision_type,
            "decision_value":
            decision_value,
            "source_row_refs": [blocker_ref],
            "decision_targets": [{
                "row_ref": blocker_ref,
                "decision_axis": decision_axis,
                "decision_subject_id": maybe_subject_id,
            }],
            "maintainer_identity_ref":
            "maintainer://phase34-test",
            "maintainer_role":
            "firmware-maintainer",
            "owner_signoff_ref":
            "maintainer://phase34-owner",
            "decision_timestamp":
            "2026-07-25T18:45:00Z",
            "rationale":
            f"Phase 34 fixture decision for {decision_id}.",
            "artifact_refs": ["external://phase33/sanitized-decision.json"],
            "evidence_refs": [blocker_ref],
            "phase":
            "33-maintainer-decision-inputs",
            "phase_lifecycle_id":
            "33-2026-07-04T01-36-41",
            "source_row_ids": [blocker_ref.rsplit("#", 1)[-1]],
            "affected_gates": [affected_gate],
            "decision_axis":
            decision_axis,
        }
        if decision_type == "exception":
            row["linked_blocker_refs"] = [blocker_ref]
            row["coverage_state"] = "approved-exception" if decision_value == "approve" else "rejected"
        return row

    def approved_projection_fixture(
        self,
        blocker_ref: str,
        affected_gate: str = "final-simulator-evidence",
    ) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object]]:
        readiness_decision = self.decision(
            "approve-readiness",
            "readiness",
            "approve",
            blocker_ref,
            affected_gate=affected_gate,
        )
        demotion_decision = self.decision(
            "approve-demotion",
            "reference_demotion",
            "approve",
            blocker_ref,
            affected_gate=affected_gate,
        )
        readiness = {
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "handoff_state": "approval-input-recorded",
            "readiness_input_supplied": True,
            "decision_id": readiness_decision["decision_id"],
            "source_row_refs": readiness_decision["source_row_refs"],
            "phase34_must_generate_final_readiness": True,
            "rationale": readiness_decision["rationale"],
        }
        demotion = {
            "phase": "33-maintainer-decision-inputs",
            "phase_lifecycle_id": "33-2026-07-04T01-36-41",
            "authorization_state": "approved-input-recorded",
            "demotion_input_supplied": True,
            "decision_id": demotion_decision["decision_id"],
            "source_row_refs": demotion_decision["source_row_refs"],
            "maintainer_identity_ref":
            demotion_decision["maintainer_identity_ref"],
            "maintainer_role": demotion_decision["maintainer_role"],
            "decision_timestamp": demotion_decision["decision_timestamp"],
            "phase34_must_validate_readiness": True,
            "rationale": demotion_decision["rationale"],
        }
        return [readiness_decision, demotion_decision], readiness, demotion

    def write_fixture(
        self,
        root: Path,
        receipts: list[dict[str, object]],
        blocker_rows: list[dict[str, object]],
        decisions: list[dict[str, object]] | None = None,
        readiness: dict[str, object] | None = None,
        demotion: dict[str, object] | None = None,
    ) -> None:
        receipt_refs = []
        for index, receipt in enumerate(receipts):
            receipt_ref = f"build/ci-evidence/phase31/stream-receipts/receipt-{index}.json"
            receipt_refs.append(self.write_json(root, receipt_ref, receipt))
        self.write_json(
            root,
            PHASE31_MANIFEST,
            {
                "accepted_count":
                len(receipts),
                "artifact_name":
                "phase31-final-evidence-intake",
                "finality_status":
                "accepted-final" if receipts else "quarantined-non-final",
                "output_root":
                "build/ci-evidence/phase31",
                "phase":
                "31-final-evidence-intake",
                "phase_lifecycle_id":
                "31-2026-07-03T02-04-07",
                "receipt_refs":
                receipt_refs,
                "rejected_count":
                0,
                "streams": [{
                    "finality_status": receipt["finality_status"],
                    "receipt_ref": receipt_refs[index],
                    "stream": receipt["stream"],
                    "submission_id": receipt["submission_id"],
                } for index, receipt in enumerate(receipts)],
            },
        )
        self.write_json(
            root,
            PHASE32_REGISTER,
            {
                "artifact_name": "phase32-blocker-register-triage",
                "phase": "32-blocker-register-and-evidence-triage",
                "phase_lifecycle_id": "32-2026-07-03T14-13-51",
                "rows": blocker_rows,
            },
        )
        phase33_dir = "build/ci-evidence/phase33"
        registers = {
            "normalized_decision_records":
            f"{phase33_dir}/normalized-decision-records.json",
            "retained_code_decision_register":
            f"{phase33_dir}/retained-code-decision-register.json",
            "residual_risk_decision_register":
            f"{phase33_dir}/residual-risk-decision-register.json",
            "exception_decision_register":
            f"{phase33_dir}/exception-decision-register.json",
            "readiness_decision_handoff":
            f"{phase33_dir}/readiness-decision-handoff.json",
            "demotion_decision_handoff":
            f"{phase33_dir}/demotion-decision-handoff.json",
            "decision_validation_report":
            f"{phase33_dir}/decision-validation-report.json",
        }
        decision_rows = decisions or []
        self.write_json(root, registers["normalized_decision_records"],
                        {"rows": decision_rows})
        for key, decision_type in [
            ("retained_code_decision_register", "retained_code"),
            ("residual_risk_decision_register", "residual_risk"),
            ("exception_decision_register", "exception"),
        ]:
            self.write_json(
                root,
                registers[key],
                {
                    "rows": [
                        row for row in decision_rows
                        if row["decision_type"] == decision_type
                    ]
                },
            )
        self.write_json(
            root,
            registers["readiness_decision_handoff"],
            readiness or {
                "phase": "33-maintainer-decision-inputs",
                "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                "handoff_state": "blocked-pending-maintainer-input",
                "readiness_input_supplied": False,
                "blocked_source_row_refs": [],
            },
        )
        self.write_json(
            root,
            registers["demotion_decision_handoff"],
            demotion or {
                "phase": "33-maintainer-decision-inputs",
                "phase_lifecycle_id": "33-2026-07-04T01-36-41",
                "authorization_state": "blocked",
                "demotion_input_supplied": False,
                "phase34_must_validate_readiness": True,
            },
        )
        self.write_json(root, registers["decision_validation_report"],
                        {"validation_state": "valid"})
        self.write_json(
            root,
            PHASE33_HANDOFF,
            {
                "phase":
                "33-maintainer-decision-inputs",
                "phase_lifecycle_id":
                "33-2026-07-04T01-36-41",
                "artifact_name":
                "phase33-maintainer-decision-inputs",
                "output_root":
                phase33_dir,
                "raw_evidence_consumed":
                False,
                "source_inputs": {
                    "phase32_canonical_register_ref": PHASE32_REGISTER,
                    "raw_evidence_consumed": False,
                },
                "register_refs":
                registers,
                "downstream_consumers":
                ["phase34-final-readiness-and-demotion-dry-run"],
            },
        )

    def run_verifier(self, root: Path, *args:
                     str) -> subprocess.CompletedProcess[str]:
        verifier = root / "tools/bazel/phase34_final_readiness_demotion_dry_run.py"
        return subprocess.run(
            ["python3", verifier.as_posix(), *args],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def run_quick(self, root: Path, *extra:
                  str) -> subprocess.CompletedProcess[str]:
        return self.run_verifier(
            root,
            "--quick",
            "--phase31-output-dir",
            "build/ci-evidence/phase31",
            "--phase33-handoff",
            PHASE33_HANDOFF,
            "--output-dir",
            OUTPUT_DIR,
            *extra,
        )

    def seed_prior_phase34_authority(self, root: Path) -> None:
        self.write_json(
            root,
            f"{OUTPUT_DIR}/final-readiness-packet.json",
            {
                "readiness_state": "unblocked",
                "cutover_verdict_state": "approved",
                "production_cutover_route_state": "open",
            },
        )
        self.write_json(
            root,
            f"{OUTPUT_DIR}/demotion-dry-run.json",
            {
                "readiness_state": "unblocked",
                "gate_state": "open",
            },
        )
        self.write_json(
            root,
            f"{OUTPUT_DIR}/stale-prior-authority.json",
            {
                "cutover_verdict": "approved",
                "route": "production-cutover-planning",
            },
        )

    def assert_source_failure_replaces_prior_authority(
        self,
        mutate_source,
        expected_reason_code: str,
    ) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_fixture(root, self.required_stream_receipts(), [])
        self.seed_prior_phase34_authority(root)
        mutate_source(root)

        # Act
        result = self.run_quick(root)

        # Assert
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected_reason_code, result.stdout)
        self.assert_blocked_source_failure_bundle(
            root,
            expected_reason_code,
        )

    def assert_injected_read_failure_replaces_prior_authority(
        self,
        target_ref: str,
        expected_reason_code: str,
    ) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.write_fixture(root, self.required_stream_receipts(), [])
        self.seed_prior_phase34_authority(root)
        module = self.load_module()
        target = root / target_ref
        original_read_text = Path.read_text

        def fail_target_read(
            candidate: Path,
            *args,
            **kwargs,
        ) -> str:
            if candidate == target:
                raise PermissionError("injected read failure")
            return original_read_text(candidate, *args, **kwargs)

        # Act
        with mock.patch.object(Path, "read_text", fail_target_read):
            reason_code = module.run_quick(
                root,
                "build/ci-evidence/phase31",
                PHASE33_HANDOFF,
                OUTPUT_DIR,
            )

        # Assert
        self.assertEqual(reason_code, expected_reason_code)
        self.assert_blocked_source_failure_bundle(
            root,
            expected_reason_code,
        )

    def assert_blocked_source_failure_bundle(
        self,
        root: Path,
        expected_reason_code: str,
    ) -> None:
        self.assertFalse(
            (root / OUTPUT_DIR / "stale-prior-authority.json").exists())
        for artifact in GENERATED_ARTIFACTS:
            self.assertTrue((root / OUTPUT_DIR / artifact).is_file(), artifact)
        manifest = self.read_json(
            root,
            f"{OUTPUT_DIR}/final-readiness-run-manifest.json",
        )
        packet = self.read_json(
            root,
            f"{OUTPUT_DIR}/final-readiness-packet.json",
        )
        demotion = self.read_json(
            root,
            f"{OUTPUT_DIR}/demotion-dry-run.json",
        )
        self.assertEqual(
            manifest["source_failure_reason_code"],
            expected_reason_code,
        )
        self.assertEqual(manifest["run_state"], "blocked-source-failure")
        self.assertEqual(packet["readiness_state"], "blocked")
        self.assertEqual(packet["cutover_verdict_state"], "blocked")
        self.assertEqual(
            packet["production_cutover_route_state"],
            "blocked",
        )
        self.assertEqual(demotion["readiness_state"], "blocked")
        self.assertEqual(demotion["gate_state"], "blocked")
        combined_output = "\n".join(
            (root / OUTPUT_DIR / artifact).read_text(encoding="utf-8")
            for artifact in GENERATED_ARTIFACTS
            if not artifact.startswith("contract-snapshots/"))
        self.assertNotIn("production-cutover-planning", combined_output)
        self.assertNotIn('"cutover_verdict": "approved"', combined_output)
