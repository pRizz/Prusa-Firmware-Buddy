from __future__ import annotations

from phase34_test_support import *

Phase34FinalReadinessDemotionDryRunTest = Phase34TestSupport


class Phase34PublicationStateSecurityTests(unittest.TestCase):

    ATTEMPT_ID = "a" * 32
    REASON_CODE = "phase31-input-invalid"

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.module = Phase34FinalReadinessDemotionDryRunTest().load_module()
        self.output = self.root / OUTPUT_DIR
        self.output.mkdir(parents=True)
        self.write_json(
            self.output / "final-readiness-packet.json",
            {
                "phase_lifecycle_id": self.module.PHASE_LIFECYCLE_ID,
                "readiness_state": "unblocked",
            },
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def write_json(path: Path, payload: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def publish(self) -> None:
        self.module.publish_publication_state(
            self.root,
            self.ATTEMPT_ID,
            self.REASON_CODE,
        )

    def assert_seeded_authority_blocked(self) -> None:
        with self.assertRaises(self.module.VerificationError) as raised:
            self.module.run_security_scan(self.root, OUTPUT_DIR)
        self.assertEqual(
            str(raised.exception),
            "Phase 34 publication state is blocking",
        )
        shell = self.root / self.module.PUBLICATION_STATE_SHELL
        self.assertTrue(
            shell.exists()
            or shell.is_symlink()
            or shell.parent.exists()
            or shell.parent.is_symlink()
        )
        self.assertNotIn(self.root.as_posix(), str(raised.exception))

    def test_payload_precreation_failure_leaves_blocking_shell(self) -> None:
        # Arrange
        with mock.patch.object(
            self.module,
            "write_publication_state_payload",
            side_effect=OSError("attacker-controlled-payload"),
        ):
            # Act
            with self.assertRaises(self.module.VerificationError):
                self.publish()

        # Assert
        self.assert_seeded_authority_blocked()

    def test_atomic_replacement_failure_leaves_blocking_shell(self) -> None:
        # Arrange
        with mock.patch.object(
            self.module,
            "replace_publication_state_payload",
            side_effect=OSError("attacker-controlled-path"),
        ):
            # Act
            with self.assertRaises(self.module.VerificationError):
                self.publish()

        # Assert
        self.assert_seeded_authority_blocked()

    def test_each_missing_required_field_is_blocking(self) -> None:
        for missing_field in self.module.PUBLICATION_STATE_FIELDS:
            with self.subTest(missing_field=missing_field):
                # Arrange
                shell = self.root / self.module.PUBLICATION_STATE_SHELL
                payload = self.module.publication_state_payload(
                    self.ATTEMPT_ID,
                    self.REASON_CODE,
                )
                payload.pop(missing_field)
                self.write_json(
                    shell / self.module.PUBLICATION_STATE_PAYLOAD_NAME,
                    payload,
                )

                # Act / Assert
                self.assert_seeded_authority_blocked()
                shutil.rmtree(shell)

    def test_malformed_json_is_blocking(self) -> None:
        # Arrange
        payload = (
            self.root
            / self.module.PUBLICATION_STATE_SHELL
            / self.module.PUBLICATION_STATE_PAYLOAD_NAME
        )
        payload.parent.mkdir(parents=True)
        payload.write_text("{", encoding="utf-8")

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_unreadable_payload_is_blocking(self) -> None:
        # Arrange
        self.publish()
        payload = (
            self.root
            / self.module.PUBLICATION_STATE_SHELL
            / self.module.PUBLICATION_STATE_PAYLOAD_NAME
        )
        original_read_text = Path.read_text

        def fail_payload_read(candidate: Path, *args, **kwargs):
            if candidate == payload:
                raise PermissionError("attacker-controlled-permission")
            return original_read_text(candidate, *args, **kwargs)

        # Act / Assert
        with mock.patch.object(Path, "read_text", fail_payload_read):
            self.assert_seeded_authority_blocked()

    def test_absolute_marker_ref_is_rejected(self) -> None:
        # Arrange
        marker_ref = Path("/tmp/phase34-publication-state")

        # Act / Assert
        with self.assertRaises(self.module.VerificationError):
            self.module.validate_publication_state_path(
                self.root,
                marker_ref,
            )

    def test_traversal_marker_ref_is_rejected(self) -> None:
        # Arrange
        marker_ref = Path("build/ci-evidence/../phase34-state")

        # Act / Assert
        with self.assertRaises(self.module.VerificationError):
            self.module.validate_publication_state_path(
                self.root,
                marker_ref,
            )

    def test_wrong_root_marker_ref_is_rejected(self) -> None:
        # Arrange
        marker_ref = Path("build/other/.phase34-publication-state")

        # Act / Assert
        with self.assertRaises(self.module.VerificationError):
            self.module.validate_publication_state_path(
                self.root,
                marker_ref,
            )

    def test_symlinked_marker_is_blocking(self) -> None:
        # Arrange
        outside = self.root / "outside-state"
        outside.mkdir()
        shell = self.root / self.module.PUBLICATION_STATE_SHELL
        shell.parent.mkdir(parents=True, exist_ok=True)
        shell.symlink_to(outside, target_is_directory=True)

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_symlinked_parent_is_blocking(self) -> None:
        # Arrange
        outside = self.root / "outside-parent"
        build = self.root / "build"
        build.rename(outside)
        build.symlink_to(outside, target_is_directory=True)

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_regular_file_shell_is_blocking(self) -> None:
        # Arrange
        shell = self.root / self.module.PUBLICATION_STATE_SHELL
        shell.parent.mkdir(parents=True, exist_ok=True)
        shell.write_text("not-a-directory", encoding="utf-8")

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_fifo_shell_is_blocking(self) -> None:
        # Arrange
        shell = self.root / self.module.PUBLICATION_STATE_SHELL
        shell.parent.mkdir(parents=True, exist_ok=True)
        os.mkfifo(shell)

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_non_directory_parent_is_blocking(self) -> None:
        # Arrange
        parent = self.root / self.module.PUBLICATION_STATE_SHELL.parent
        shutil.rmtree(parent)
        parent.parent.mkdir(parents=True, exist_ok=True)
        parent.write_text("not-a-directory", encoding="utf-8")

        # Act / Assert
        self.assert_seeded_authority_blocked()

    def test_cleanup_failure_keeps_publication_state_blocking(self) -> None:
        # Arrange
        self.publish()

        # Act
        with mock.patch.object(
            self.module,
            "remove_publication_state_shell",
            side_effect=OSError("attacker-controlled-cleanup"),
        ):
            with self.assertRaises(self.module.VerificationError):
                self.module.clear_publication_state(
                    self.root,
                    self.ATTEMPT_ID,
                )

        # Assert
        self.assert_seeded_authority_blocked()



__all__ = ["Phase34PublicationStateSecurityTests"]
