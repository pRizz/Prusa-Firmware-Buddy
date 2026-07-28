from __future__ import annotations

from phase35_test_support import (
    AUDIT_KINDS,
    DECISION_FIELDS,
    ROOT,
    ROUTE_FIELDS,
    SOURCE_FAILURE_ARTIFACTS,
    SOURCE_FAILURE_MANIFEST_FIELDS,
    Callable,
    Path,
    io,
    json,
    mock,
    phase35,
    redirect_stderr,
    shutil,
    tempfile,
    unittest,
)

class Phase35SourceFailureReplacementTest(unittest.TestCase):

    def make_temp_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        for relative_path in [
                "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json",
                "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json",
        ]:
            source = ROOT / relative_path
            destination = root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return temp_dir, root

    def phase34_manifest(self) -> dict[str, object]:
        return {
            "accepted_receipt_snapshot_ref":
            "build/ci-evidence/phase34/contract-snapshots/phase31-accepted-receipts.json",
            "artifact_name": "phase34-final-readiness-demotion-dry-run",
            "generated_artifacts": phase35.PHASE34_ARTIFACTS,
            "generated_at_utc": "2026-07-25T22:18:11Z",
            "output_root": "build/ci-evidence/phase34",
            "phase": "34-final-readiness-and-demotion-dry-run",
            "phase_lifecycle_id": phase35.PHASE34_LIFECYCLE_ID,
            "phase33_register_digests": {
                name: "0" * 64
                for name in phase35.PHASE33_REGISTER_NAMES
            },
            "raw_evidence_consumed": False,
            "snapshot_refs": [],
            "source_refs": [],
        }

    def seed_prior_approved(self, root: Path) -> None:
        output = root / "build/ci-evidence/phase35"
        snapshots = output / "contract-snapshots"
        snapshots.mkdir(parents=True, exist_ok=True)
        phase35.write_json(
            output / "cutover-decision-run-manifest.json",
            {"prior_approved": True},
        )
        phase35.write_json(
            output / "cutover-audit-link-index.json",
            {"prior_approved": True},
        )
        phase35.write_json(
            output / "cutover-decision.json",
            {
                "cutover_verdict": "approved",
                "prior_approved": True
            },
        )
        phase35.write_json(
            output / "next-milestone-route.json",
            {
                "route": "production-cutover-planning",
                "prior_approved": True
            },
        )
        (output / "redacted-cutover-decision-report.md").write_text(
            "prior_approved\n", encoding="utf-8")
        phase35.write_json(snapshots / "prior-approved.json",
                           {"prior_approved": True})

    def write_manifest(self, root: Path, manifest: dict[str, object]) -> Path:
        manifest_path = root / (
            "build/ci-evidence/phase34/final-readiness-run-manifest.json")
        phase35.write_json(manifest_path, manifest)
        return manifest_path

    def write_later_source_fixture(self, root: Path) -> None:
        dry_run = {
            "approval_decision_state": "missing",
            "approval_validation_state": "missing",
            "gate_state": "blocked",
            "readiness_state": "blocked",
            "reason_codes": ["approval-missing"],
            "source_refs": [],
        }
        artifacts = {
            "build/ci-evidence/phase34/readiness-coverage-ledger.json": {
                "phase_lifecycle_id": phase35.PHASE34_LIFECYCLE_ID,
                "rows": [],
            },
            "build/ci-evidence/phase34/final-readiness-packet.json": {
                "phase_lifecycle_id": phase35.PHASE34_LIFECYCLE_ID,
                "ledger_rows": [],
                "demotion_dry_run": dry_run,
            },
            "build/ci-evidence/phase34/readiness-blocker-summary.json": {},
            "build/ci-evidence/phase34/demotion-dry-run.json": dry_run,
            "build/ci-evidence/phase34/contract-snapshots/phase33-downstream-handoff-manifest.json":
            {
                "artifact_name": "phase33-maintainer-decision-inputs",
                "phase_lifecycle_id": phase35.PHASE33_LIFECYCLE_ID,
                "register_refs": {
                    name: "build/ci-evidence/phase34/wrong-source-root.json"
                    for name in phase35.PHASE33_REGISTER_NAMES
                },
            },
            "build/ci-evidence/phase34/contract-snapshots/phase32-blocker-register.json":
            {
                "rows": []
            },
            "build/ci-evidence/phase34/contract-snapshots/phase31-accepted-receipts.json":
            {
                "receipts": []
            },
        }
        for relative_path, payload in artifacts.items():
            phase35.write_json(root / relative_path, payload)

    def invoke_quick(self, root: Path) -> tuple[int, str]:
        stderr = io.StringIO()
        try:
            with mock.patch.object(phase35, "ROOT", root):
                with redirect_stderr(stderr):
                    result = phase35.main(["--quick"])
        except Exception as error:  # Intentional RED boundary assertion.
            self.fail(f"main --quick raised instead of returning 1: {error!r}")
        return result, stderr.getvalue()

    def assert_failure_replacement(self, root: Path, expected_reason: str,
                                   stderr: str) -> None:
        output = root / "build/ci-evidence/phase35"
        actual = sorted(
            path.relative_to(output).as_posix() for path in output.rglob("*")
            if path.is_file())
        self.assertEqual(actual, SOURCE_FAILURE_ARTIFACTS)
        manifest = json.loads(
            (output /
             "cutover-decision-run-manifest.json").read_text(encoding="utf-8"))
        decision = json.loads(
            (output / "cutover-decision.json").read_text(encoding="utf-8"))
        route = json.loads(
            (output / "next-milestone-route.json").read_text(encoding="utf-8"))
        contract = json.loads((
            root /
            "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json"
        ).read_text(encoding="utf-8"))
        behavior = contract["source_failure_behavior"]

        self.assertEqual(list(manifest), SOURCE_FAILURE_MANIFEST_FIELDS)
        self.assertEqual(list(decision), DECISION_FIELDS)
        self.assertEqual(list(route), ROUTE_FIELDS)
        self.assertEqual(manifest["generation_state"], "blocked-source-error")
        self.assertEqual(manifest["generated_artifacts"],
                         SOURCE_FAILURE_ARTIFACTS)
        self.assertEqual(manifest["source_failure_reason_codes"],
                         [expected_reason])
        self.assertIn(expected_reason, behavior["safe_reason_codes"])
        self.assertEqual(decision["cutover_verdict"], "blocked")
        self.assertEqual(
            decision["reason_codes"],
            sorted([expected_reason, "route-scope-incomplete"]),
        )
        self.assertEqual(decision["readiness_state"], "blocked")
        self.assertEqual(decision["readiness_result_ref"], "")
        self.assertEqual(decision["active_exception_ids"], [])
        self.assertEqual(decision["blocker_ids"], [])
        self.assertEqual(decision["audit_link_index_ref"], "")
        self.assertEqual(
            decision["audit_link_counts_by_kind"],
            {kind: 0
             for kind in AUDIT_KINDS},
        )
        self.assertEqual(decision["demotion_decision_validation_state"],
                         "invalid")
        self.assertEqual(decision["demotion_decision_state"], "missing")
        self.assertEqual(decision["demotion_decision_source_refs"], [])
        self.assertEqual(decision["demotion_gate_state"], "blocked")
        self.assertEqual(decision["demotion_gate_reason_codes"],
                         [expected_reason])
        self.assertEqual(route["route"], "targeted-blocker-repair")
        self.assertEqual(route["source_verdict"], "blocked")
        self.assertEqual(route["follow_up_scope"], [])
        self.assertTrue(route["requires_fresh_cutover_decision"])
        self.assertTrue(route["planning_only"])
        self.assertFalse(route["production_actions_authorized"])
        self.assertFalse(manifest["raw_evidence_consumed"])
        self.assertFalse(decision["raw_evidence_consumed"])
        published = "\n".join(
            path.read_text(encoding="utf-8") for path in output.rglob("*")
            if path.is_file())
        self.assertNotIn("prior_approved", published)
        self.assertNotIn("production-cutover-planning", published)
        self.assertNotIn("BEGIN PRIVATE KEY", published)
        self.assertNotIn("BEGIN PRIVATE KEY", stderr)

    def run_failure_case(
        self,
        mutate: Callable[[Path], None],
        expected_reason: str,
    ) -> None:
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        self.seed_prior_approved(root)
        mutate(root)

        # Act
        result, stderr = self.invoke_quick(root)

        # Assert
        self.assertEqual(result, 1)
        self.assert_failure_replacement(root, expected_reason, stderr)

    def test_prior_approved_is_replaced_when_phase34_manifest_is_missing(
            self) -> None:
        # Arrange / Act / Assert
        self.run_failure_case(lambda root: None, "source-artifact-missing")

    def test_prior_approved_is_replaced_when_phase34_manifest_json_is_malformed(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest_path = self.write_manifest(root, self.phase34_manifest())
            manifest_path.write_text("{", encoding="utf-8")

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-artifact-malformed")

    def test_prior_approved_is_replaced_when_phase34_manifest_utf8_is_unreadable(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest_path = self.write_manifest(root, self.phase34_manifest())
            manifest_path.write_bytes(b"\xff\xfe\x00")

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-artifact-malformed")

    def test_prior_approved_is_replaced_when_phase34_manifest_is_stale(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest = self.phase34_manifest()
            manifest["generated_at_utc"] = "2020-01-01T00:00:00Z"
            self.write_manifest(root, manifest)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-artifact-stale")

    def test_prior_approved_is_replaced_when_phase34_lifecycle_is_mismatched(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest = self.phase34_manifest()
            manifest["phase_lifecycle_id"] = "stale-lifecycle"
            self.write_manifest(root, manifest)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-artifact-lifecycle-mismatched")

    def test_prior_approved_is_replaced_when_phase34_manifest_is_secret_tainted(
            self) -> None:

        def mutate(root: Path) -> None:
            manifest = self.phase34_manifest()
            manifest["phase"] = "-----BEGIN PRIVATE KEY-----"
            self.write_manifest(root, manifest)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "secret-tainted")

    def test_prior_approved_is_replaced_when_source_manifest_is_a_symlink(
            self) -> None:

        def mutate(root: Path) -> None:
            outside_dir = tempfile.TemporaryDirectory()
            self.addCleanup(outside_dir.cleanup)
            outside_manifest = Path(
                outside_dir.name) / "final-readiness-run-manifest.json"
            outside_manifest.write_text(json.dumps(self.phase34_manifest()),
                                        encoding="utf-8")
            manifest_path = root / (
                "build/ci-evidence/phase34/final-readiness-run-manifest.json")
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.symlink_to(outside_manifest)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-ref-failed")

    def test_prior_approved_is_replaced_when_later_reached_source_is_unsafe(
            self) -> None:

        def mutate(root: Path) -> None:
            self.write_manifest(root, self.phase34_manifest())
            self.write_later_source_fixture(root)

        # Arrange / Act / Assert
        self.run_failure_case(mutate, "source-ref-failed")

    def test_output_symlink_is_rejected_without_touching_target(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        self.addCleanup(temp_dir.cleanup)
        outside_dir = tempfile.TemporaryDirectory()
        self.addCleanup(outside_dir.cleanup)
        outside = Path(outside_dir.name)
        marker = outside / "prior_approved"
        marker.write_text("unchanged", encoding="utf-8")
        output = root / "build/ci-evidence/phase35"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.symlink_to(outside, target_is_directory=True)

        # Act
        result, stderr = self.invoke_quick(root)

        # Assert
        self.assertEqual(result, 1)
        self.assertTrue(output.is_symlink())
        self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")
        self.assertEqual(sorted(path.name for path in outside.iterdir()),
                         ["prior_approved"])
        self.assertNotIn("unchanged", stderr)
