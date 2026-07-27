from __future__ import annotations

from phase32_test_support import *


class Phase32ProducerShapeTestBase(unittest.TestCase):

    def read_json(self, root: Path, path: str) -> dict[str, object]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    def write_json(self, root: Path, path: str, data: object) -> None:
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")

    def load_producer(self, root: Path, module_name: str) -> ModuleType:
        module_path = root / f"tools/bazel/{module_name}.py"
        spec = importlib.util.spec_from_file_location(
            f"phase32_producer_fixture_{module_name}", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def make_producer_root(
            self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name).resolve()
        relative_paths = {
            VERIFIER.relative_to(ROOT),
            NORMALIZATION.relative_to(ROOT),
            CONTRACT.relative_to(ROOT),
            *[Path(path) for path in TRIAGE_MODULES],
            *[Path(path) for path in SOURCE_CONTRACTS],
            *[Path(path) for path in PRODUCER_MODULES],
            *[Path(path) for path in PRODUCER_INPUTS],
        }
        for relative_path in relative_paths:
            destination = root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative_path, destination)
        return temp_dir, root

    def phase26_all_passed_output(self, root: Path,
                                  phase26: ModuleType) -> str:
        phase26.check_contract(root)
        phase18 = self.read_json(
            root, "tools/bazel/manifests/phase18_cutover_review_contract.json")
        generated_at = "2026-07-26T01:00:00Z"
        consumed_rows = {}
        for requirement in phase26.phase18_upstream_requirements(phase18):
            criterion_id = str(requirement["criterion_id"])
            consumed_rows[criterion_id] = {
                "artifact_refs":
                [f"external://phase26/artifacts/{criterion_id}.json"],
                "criterion_id":
                criterion_id,
                "evidence_family":
                requirement["evidence_family"],
                "evidence_refs":
                [f"external://phase26/evidence/{criterion_id}.json"],
                "exception_status":
                "none",
                "failure_reason":
                "none",
                "generated_at_utc":
                generated_at,
                "maintainer_state":
                "accepted",
                "owning_phase":
                requirement["source_phase"],
                "redaction_status":
                "passed",
                "requirement_ids":
                list(requirement["requirement_ids"]),
                "source_lifecycle_id":
                requirement["source_lifecycle_id"],
                "source_lifecycle_status":
                "current",
                "source_ref_status":
                "passed",
                "source_requirement_ids":
                list(requirement["requirement_ids"]),
                "status":
                "passed",
            }
        output_dir = Path("build/ci-evidence/phase26")
        upstream_rows = phase26.build_upstream_rows(
            root,
            output_dir,
            {},
            True,
            generated_at,
            consumed_rows,
        )
        table_path = output_dir / "upstream-result-row-table.json"
        phase26.write_json(root, table_path, {"rows": upstream_rows})
        phase26.write_json(
            root,
            output_dir / "release-upstream-run-manifest.json",
            {
                "artifact_name": "phase26-release-signing-upstream-evidence",
                "generated_at_utc": generated_at,
                "output_root": output_dir.as_posix(),
                "phase": phase26.PHASE,
                "phase_lifecycle_id": phase26.PHASE_LIFECYCLE_ID,
                "real_release_evidence_supplied": True,
                "release_status": "passed",
                "upstream_criteria_count": len(upstream_rows),
            },
        )
        return table_path.as_posix()

    def phase31_accept_release_output(self, root: Path,
                                      phase31: ModuleType) -> None:
        contract = self.read_json(
            root,
            "tools/bazel/manifests/phase31_final_evidence_intake_contract.json"
        )
        adapter = phase31.contract_adapters(contract)["release-signing"]
        receipt, _ = phase31.validate_stream_output(
            root,
            adapter,
            Path("build/ci-evidence/phase26"),
            "external://phase31/submitters/release-maintainer",
            ["producer-fixture", "phase26"],
            "a" * 64,
        )
        output_dir = phase31.reset_output_root(
            root, Path("build/ci-evidence/phase31"))
        phase31.write_phase31_outputs(root, output_dir, [receipt], [])

    def phase27_maintainer_input(self, root: Path,
                                 phase27: ModuleType) -> dict[str, object]:
        checked = phase27.check_contract(root)
        phase18 = checked["phase18_contract"]
        contract = checked["contract"]
        maintainer_input = phase27.maintainer_input_template(phase18, contract)
        retained_rows = maintainer_input["retained_code_decisions"]
        for index, row in enumerate(retained_rows):
            row["decision"] = "exception" if index == 0 else "approve"
            row["approver"] = "phase32-producer-fixture-maintainer"
            row["decision_timestamp"] = "2026-07-26T01:05:00Z"
            row["rationale"] = "Producer-shaped retained-code review completed."
            row["residual_risk"] = "Bounded residual risk remains documented."
            row["redaction_summary"] = "Reference-only evidence; scan passed."
            if index != 0:
                continue
            exception = row["exception"]
            exception.update({
                "scope": row["packet_id"],
                "rationale": "A bounded retained-code exception is required.",
                "approver": row["approver"],
                "approver_role": row["approver_role"],
                "affected_printer_or_release_surface":
                "retained runtime compatibility boundary",
                "mitigation_or_follow_up":
                "Review the retained boundary at the next release gate.",
                "expiry_or_review_trigger": "Next release-candidate review",
                "evidence_refs": list(row["evidence_refs"]),
                "residual_risk": row["residual_risk"],
                "owner": row["approver"],
            })

        for row in maintainer_input["final_readiness_decisions"]:
            criterion_id = str(row["criterion_id"])
            is_blocked = criterion_id in {
                "final-maintainer-decision",
                "final-reference-demotion-allowed",
            }
            row["decision"] = "reject" if is_blocked else "approve"
            row["status"] = "blocked" if is_blocked else "passed"
            row["approver"] = "phase32-producer-fixture-maintainer"
            row["approver_role"] = self.final_role_for_criterion(criterion_id)
            row["decision_timestamp"] = "2026-07-26T01:05:00Z"
            row["rationale"] = "Producer-shaped final criterion review completed."
            row["evidence_refs"] = [
                f"external://phase26/evidence/{criterion_id}.json"
            ]
            row["residual_risk"] = "Bounded residual risk remains documented."
            row["redaction_summary"] = "Reference-only evidence; scan passed."
        return maintainer_input

    def final_role_for_criterion(self, criterion_id: str) -> str:
        if criterion_id == "final-hardware-safety-media-evidence":
            return "safety-maintainer"
        if criterion_id == "final-live-network-transfer-evidence":
            return "network-security-maintainer"
        if criterion_id in {
                "final-release-artifact-signing-evidence",
                "final-reference-demotion-allowed",
        }:
            return "release-maintainer"
        return "cutover-maintainer"

    def generate_producer_fixture(
        self, ) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir, root = self.make_producer_root()
        phase26 = self.load_producer(
            root, "phase26_release_signing_upstream_evidence")
        phase27 = self.load_producer(
            root, "phase27_retained_code_acceptance_decisions")
        phase28 = self.load_producer(root, "phase28_final_readiness_packet")
        phase31 = self.load_producer(root, "phase31_final_evidence_intake")

        table_path = self.phase26_all_passed_output(root, phase26)
        self.phase31_accept_release_output(root, phase31)

        maintainer_input = self.phase27_maintainer_input(root, phase27)
        maintainer_input_path = "build/ci-evidence/phase27-maintainer-input.json"
        phase27.write_json(root, Path(maintainer_input_path), maintainer_input)
        phase27.write_phase27_outputs(
            root,
            Path("build/ci-evidence/phase27"),
            maintainer_input_path,
            table_path,
        )

        phase26_path, phase26_rows = phase28.load_phase26_rows(
            root, table_path)
        phase27_path, handoff, phase27_bundle = phase28.load_phase27_bundle(
            root, "build/ci-evidence/phase27/phase28-handoff-manifest.json")
        phase28.write_phase28_outputs(
            root,
            phase28.check_contract(root),
            phase26_path,
            phase26_rows,
            phase27_path,
            handoff,
            phase27_bundle,
            None,
            "build/ci-evidence/phase28",
        )
        return temp_dir, root

    def run_phase32(
        self,
        root: Path,
        phase27_output_dir: str = "build/ci-evidence/phase27",
        phase28_output_dir: str = "build/ci-evidence/phase28",
    ) -> subprocess.CompletedProcess[str]:
        verifier = root / "tools/bazel/phase32_blocker_register_triage.py"
        return subprocess.run(
            [
                "python3",
                verifier.as_posix(),
                "--quick",
                "--phase31-output-dir",
                "build/ci-evidence/phase31",
                "--phase27-output-dir",
                phase27_output_dir,
                "--phase28-output-dir",
                phase28_output_dir,
                "--output-dir",
                "build/ci-evidence/phase32",
            ],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            shell=False,
        )

    def nest_output_dir(self, root: Path, output_dir: str) -> str:
        source_dir = root / output_dir
        source_entries = list(source_dir.iterdir())
        nested_dir = source_dir / "nested"
        nested_dir.mkdir()
        for source_entry in source_entries:
            shutil.move(source_entry, nested_dir / source_entry.name)
        return nested_dir.relative_to(root).as_posix()

    def canonical_phase_semantics(
        self,
        rows: list[dict[str, object]],
        producer_phase: str,
    ) -> list[dict[str, object]]:
        return sorted(
            [{
                key: value
                for key, value in row.items()
                if key not in {"source_ref", "evidence_refs"}
            } for row in rows if row["producer_phase"] == producer_phase],
            key=lambda row: str(row["row_id"]),
        )

    def expected_container_row_id(self, artifact_path: str) -> str:
        mapping = PRODUCER_CONTAINER_MAPPINGS[artifact_path]
        return canonical_row_id(
            canonical_source_identity(
                source_domain=mapping["source_domain"],
                producer_phase=mapping["producer_phase"],
                producer_artifact_kind=mapping["producer_artifact_kind"],
                source_row_kind=mapping["source_row_kind"],
                source_subject_id=mapping["source_subject_id"],
            ))

    def assert_phase32_bundle(
        self,
        root: Path,
        *,
        included_row_id: str | None = None,
        excluded_row_id: str | None = None,
    ) -> list[dict[str, object]]:
        output_dir = root / "build/ci-evidence/phase32"
        for filename in PHASE32_OUTPUT_BUNDLE:
            self.assertTrue((output_dir / filename).exists(), filename)
        rows = self.read_json(
            root, "build/ci-evidence/phase32/blocker-register.json")["rows"]
        handoff = self.read_json(
            root, "build/ci-evidence/phase32/downstream-handoff-manifest.json")
        handoff_row_ids = {
            identity["row_id"]
            for identity in handoff["row_identities"]
        }
        self.assertEqual(handoff["row_count"], len(rows))
        if included_row_id is not None:
            self.assertIn(included_row_id, handoff_row_ids)
        if excluded_row_id is not None:
            self.assertNotIn(excluded_row_id, handoff_row_ids)
        return rows

    def assert_container_problem(
        self,
        root: Path,
        artifact_path: str,
        expected_problem_kind: str,
    ) -> dict[str, object]:
        mapping = PRODUCER_CONTAINER_MAPPINGS[artifact_path]
        expected_row_id = self.expected_container_row_id(artifact_path)
        rows = self.assert_phase32_bundle(root,
                                          included_row_id=expected_row_id)
        container_rows = [
            row for row in rows if
            row["producer_artifact_kind"] == mapping["producer_artifact_kind"]
            and row["source_subject_id"] == mapping["source_subject_id"]
        ]
        self.assertEqual(len(container_rows), 1)
        row = container_rows[0]
        expected_source_ref = f"{artifact_path}#container"
        expected_decision_impact = ("repair_required_before_cutover"
                                    if expected_problem_kind == "malformed"
                                    else "cutover_verdict_blocked")
        for field in [
                "source_domain",
                "producer_phase",
                "producer_artifact_kind",
                "source_row_kind",
                "source_subject_id",
                "decision_axis",
                "decision_subject_id",
                "source_stream",
                "affected_gate",
        ]:
            self.assertEqual(row[field], mapping[field], field)
        self.assertEqual(row["row_id"], expected_row_id)
        self.assertEqual(row["row_problem_kind"], expected_problem_kind)
        self.assertEqual(row["severity"], "critical")
        self.assertEqual(row["proof_eligibility"], "ineligible")
        self.assertTrue(row["owner_ref"])
        self.assertTrue(row["required_next_action"])
        self.assertEqual(row["decision_impact"], expected_decision_impact)
        self.assertEqual(row["source_ref"], expected_source_ref)
        self.assertIn(artifact_path, row["evidence_refs"])
        self.assertIn(expected_source_ref, row["evidence_refs"])
        return row

    def assert_empty_collection_publication(self, root: Path,
                                            artifact_path: str) -> None:
        mapping = PRODUCER_CONTAINER_MAPPINGS[artifact_path]
        expected_row_id = self.expected_container_row_id(artifact_path)
        rows = self.assert_phase32_bundle(root,
                                          excluded_row_id=expected_row_id)
        self.assertFalse([
            row for row in rows
            if row["source_subject_id"] == mapping["source_subject_id"]
        ])
        self.assertFalse([
            row for row in rows if row["producer_artifact_kind"] ==
            mapping["producer_artifact_kind"]
        ])
