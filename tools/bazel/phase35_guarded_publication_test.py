from __future__ import annotations

from phase35_test_support import (
    CONTRACT,
    Path,
    json,
    mock,
    phase35,
    tempfile,
    unittest,
    workflow,
)

class Phase35GuardedPublicationTest(unittest.TestCase):

    def make_install_fixture(
        self
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        canonical = root / phase35.DEFAULT_OUTPUT
        canonical.mkdir(parents=True)
        phase35.write_json(canonical / "decision.json",
                           {"cutover_verdict": "approved"})
        stage = Path(
            tempfile.mkdtemp(prefix=".phase35-stage-",
                             dir=canonical.parent))
        phase35.write_json(stage / "decision.json",
                           {"cutover_verdict": "blocked"})
        return temp_dir, root, canonical, stage

    def assert_guard_blocks(self, root: Path) -> None:
        guard = root / phase35.AUTHORITY_GUARD
        self.assertTrue(guard.exists() or guard.is_symlink())
        with self.assertRaises(phase35.VerificationError):
            phase35.ensure_canonical_authority(root, phase35.DEFAULT_OUTPUT)

    def test_authority_guard_contract_is_exact_and_cannot_grant_approval(
            self) -> None:
        # Arrange
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

        # Act
        guard = contract["authority_guard"]

        # Assert
        self.assertEqual(
            guard, {
                "artifact":
                "build/ci-evidence/.phase35-authority-guard.json",
                "required_fields": [
                    "phase",
                    "phase_lifecycle_id",
                    "authority_state",
                    "reason_code",
                    "attempted_output_root",
                ],
                "phase_lifecycle_id":
                phase35.PHASE_LIFECYCLE_ID,
                "authority_state":
                "blocked",
                "safe_reason_code":
                "publication-in-progress",
                "attempted_output_root":
                phase35.DEFAULT_OUTPUT.as_posix(),
            })
        self.assertTrue({
            "approved",
            "approval",
            "verdict",
            "route",
            "production_actions_authorized",
        }.isdisjoint(guard["required_fields"]))

    def test_guard_write_failure_blocks_prior_authority_before_rename(
            self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)

        def fail_after_guard_creation(path: Path,
                                      payload: dict[str, object]) -> None:
            del path, payload
            raise OSError("injected guard write failure")

        # Act / Assert
        with mock.patch.object(phase35,
                               "write_guard_payload",
                               side_effect=fail_after_guard_creation):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(
                    root,
                    stage,
                    canonical,
                    lambda _: None,
                )
        self.assertTrue(canonical.exists())
        self.assertTrue(stage.exists())
        self.assert_guard_blocks(root)

    def test_guard_creation_interruption_leaves_presence_blocking(self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)

        def interrupt_guard_creation(path: Path) -> None:
            path.touch()
            raise OSError("injected guard creation interruption")

        # Act / Assert
        with mock.patch.object(phase35,
                               "touch_guard",
                               side_effect=interrupt_guard_creation):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        self.assertTrue(canonical.exists())
        self.assert_guard_blocks(root)

    def test_guard_precreation_failure_blocks_seeded_prior_authority_for_all_readers(
        self,
    ) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        attempt_id = "c" * 32
        workflow.publish_workflow_attempt_marker(root, attempt_id)

        # Act
        with mock.patch.object(
            phase35,
            "touch_guard",
            side_effect=OSError("injected pre-create failure"),
        ):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(
                    root,
                    stage,
                    canonical,
                    lambda _: None,
                )

        # Assert
        self.assertFalse((root / phase35.AUTHORITY_GUARD).exists())
        self.assertEqual(
            workflow.load_workflow_attempt_marker(root)["attempt_id"],
            attempt_id,
        )
        with self.assertRaises(phase35.VerificationError):
            phase35.ensure_canonical_authority(
                root,
                phase35.DEFAULT_OUTPUT,
            )
        with self.assertRaises(phase35.VerificationError):
            phase35.run_security_scan(root)
        authority = workflow.load_final_authority(root)
        self.assertFalse(authority.available)
        self.assertEqual(
            authority.reason_category,
            "workflow-attempt-blocking",
        )

    def test_prior_to_backup_rename_failure_retains_guard_and_prior(
            self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        original_rename = phase35.rename_path

        def fail_prior_rename(source: Path, target: Path) -> None:
            if source == canonical:
                raise OSError("injected prior rename failure")
            original_rename(source, target)

        # Act / Assert
        with mock.patch.object(phase35,
                               "rename_path",
                               side_effect=fail_prior_rename):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        self.assertTrue(canonical.exists())
        self.assert_guard_blocks(root)

    def test_stage_rename_failure_restores_prior_under_guard(self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        original_rename = phase35.rename_path

        def fail_stage_rename(source: Path, target: Path) -> None:
            if source == stage:
                raise OSError("injected stage rename failure")
            original_rename(source, target)

        # Act / Assert
        with mock.patch.object(phase35,
                               "rename_path",
                               side_effect=fail_stage_rename):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        prior = json.loads(
            (canonical / "decision.json").read_text(encoding="utf-8"))
        self.assertEqual(prior["cutover_verdict"], "approved")
        self.assert_guard_blocks(root)

    def test_post_install_validation_failure_restores_prior_under_guard(
            self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)

        def fail_validation(_: Path) -> None:
            raise phase35.VerificationError(
                "injected post-install validation failure")

        # Act / Assert
        with self.assertRaises(phase35.VerificationError):
            phase35.install_staged_bundle(root, stage, canonical,
                                          fail_validation)
        prior = json.loads(
            (canonical / "decision.json").read_text(encoding="utf-8"))
        self.assertEqual(prior["cutover_verdict"], "approved")
        self.assert_guard_blocks(root)

    def test_restore_failure_retains_recoverable_backup_and_guard(self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        original_rename = phase35.rename_path

        def fail_stage_and_restore(source: Path, target: Path) -> None:
            if source == stage or source.name == ".phase35-previous":
                raise OSError("injected rename failure")
            original_rename(source, target)

        # Act / Assert
        with mock.patch.object(phase35,
                               "rename_path",
                               side_effect=fail_stage_and_restore):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        self.assertTrue(
            (root / phase35.PREVIOUS_OUTPUT).is_dir())
        self.assert_guard_blocks(root)

    def test_backup_cleanup_failure_leaves_valid_canonical_blocked(
            self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)
        original_remove = phase35.remove_directory

        def fail_backup_cleanup(path: Path) -> None:
            if path.name == ".phase35-previous":
                raise OSError("injected backup cleanup failure")
            original_remove(path)

        # Act / Assert
        with mock.patch.object(phase35,
                               "remove_directory",
                               side_effect=fail_backup_cleanup):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        current = json.loads(
            (canonical / "decision.json").read_text(encoding="utf-8"))
        self.assertEqual(current["cutover_verdict"], "blocked")
        self.assertTrue((root / phase35.PREVIOUS_OUTPUT).exists())
        self.assert_guard_blocks(root)

    def test_guard_cleanup_failure_leaves_valid_canonical_blocked(self) -> None:
        # Arrange
        temp_dir, root, canonical, stage = self.make_install_fixture()
        self.addCleanup(temp_dir.cleanup)

        # Act / Assert
        with mock.patch.object(phase35,
                               "remove_guard",
                               side_effect=OSError(
                                   "injected guard cleanup failure")):
            with self.assertRaises(phase35.VerificationError):
                phase35.install_staged_bundle(root, stage, canonical,
                                              lambda _: None)
        current = json.loads(
            (canonical / "decision.json").read_text(encoding="utf-8"))
        self.assertEqual(current["cutover_verdict"], "blocked")
        self.assertFalse((root / phase35.PREVIOUS_OUTPUT).exists())
        self.assert_guard_blocks(root)

    def test_guard_presence_or_invalidity_blocks_every_touched_reader(
            self) -> None:
        cases = {
            "valid": {
                "phase": phase35.PHASE,
                "phase_lifecycle_id": phase35.PHASE_LIFECYCLE_ID,
                "authority_state": "blocked",
                "reason_code": "publication-in-progress",
                "attempted_output_root": phase35.DEFAULT_OUTPUT.as_posix(),
            },
            "malformed": {
                "authority_state": "blocked"
            },
            "stale": {
                "phase": phase35.PHASE,
                "phase_lifecycle_id": "stale",
                "authority_state": "blocked",
                "reason_code": "publication-in-progress",
                "attempted_output_root": phase35.DEFAULT_OUTPUT.as_posix(),
            },
        }
        for name, payload in cases.items():
            with self.subTest(name=name):
                # Arrange
                temp_dir = tempfile.TemporaryDirectory()
                self.addCleanup(temp_dir.cleanup)
                root = Path(temp_dir.name)
                guard = root / phase35.AUTHORITY_GUARD
                phase35.write_json(guard, payload)

                # Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.ensure_canonical_authority(
                        root, phase35.DEFAULT_OUTPUT)
                with self.assertRaises(phase35.VerificationError):
                    phase35.run_security_scan(root)

        for name, create_guard in {
                "unsafe":
                lambda guard, outside: guard.symlink_to(outside),
                "unreadable":
                lambda guard, _: guard.mkdir(parents=True),
        }.items():
            with self.subTest(name=name):
                # Arrange
                temp_dir = tempfile.TemporaryDirectory()
                self.addCleanup(temp_dir.cleanup)
                root = Path(temp_dir.name)
                guard = root / phase35.AUTHORITY_GUARD
                guard.parent.mkdir(parents=True)
                outside = root / "outside-guard.json"
                outside.write_text("{}", encoding="utf-8")
                create_guard(guard, outside)

                # Act / Assert
                with self.assertRaises(phase35.VerificationError):
                    phase35.ensure_canonical_authority(
                        root, phase35.DEFAULT_OUTPUT)
                with self.assertRaises(phase35.VerificationError):
                    phase35.run_security_scan(root)

    def assert_target_substitutions_rejected(self, target_name: str,
                                             expected: Path,
                                             expect_directory: bool) -> None:
        substitutions = [
            ("absolute", Path("/tmp/phase35-substitution")),
            ("parent-traversal", Path("build/ci-evidence/../escape")),
            ("wrong-root", Path("build/other/phase35-substitution")),
        ]
        for name, actual in substitutions:
            with self.subTest(target=target_name, substitution=name):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    with self.assertRaises(phase35.VerificationError):
                        phase35.validate_mutation_target(
                            root,
                            actual,
                            expected,
                            target_name,
                            expect_directory=expect_directory,
                            allow_missing=True,
                        )

        with self.subTest(target=target_name, substitution="symlink-escape"):
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                outside = root / "outside"
                outside.mkdir()
                (root / "build").mkdir()
                (root / "build/ci-evidence").symlink_to(
                    outside, target_is_directory=True)
                with self.assertRaises(phase35.VerificationError):
                    phase35.validate_mutation_target(
                        root,
                        expected,
                        expected,
                        target_name,
                        expect_directory=expect_directory,
                        allow_missing=True,
                    )

        with self.subTest(target=target_name,
                          substitution="non-directory"):
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                target = root / expected
                if expect_directory:
                    target.parent.mkdir(parents=True)
                    target.write_text("not a directory", encoding="utf-8")
                else:
                    target.parent.parent.mkdir(parents=True)
                    target.parent.write_text("not a directory",
                                             encoding="utf-8")
                with self.assertRaises(phase35.VerificationError):
                    phase35.validate_mutation_target(
                        root,
                        expected,
                        expected,
                        target_name,
                        expect_directory=expect_directory,
                        allow_missing=False,
                    )

    def test_guard_target_substitutions_are_rejected(self) -> None:
        self.assert_target_substitutions_rejected(
            "guard",
            phase35.AUTHORITY_GUARD,
            expect_directory=False,
        )

    def test_stage_target_substitutions_are_rejected(self) -> None:
        self.assert_target_substitutions_rejected(
            "stage",
            Path("build/ci-evidence/.phase35-stage-test"),
            expect_directory=True,
        )

    def test_backup_target_substitutions_are_rejected(self) -> None:
        self.assert_target_substitutions_rejected(
            "backup",
            phase35.PREVIOUS_OUTPUT,
            expect_directory=True,
        )

    def test_canonical_target_substitutions_are_rejected(self) -> None:
        self.assert_target_substitutions_rejected(
            "canonical",
            phase35.DEFAULT_OUTPUT,
            expect_directory=True,
        )
