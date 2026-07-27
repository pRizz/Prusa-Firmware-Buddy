from __future__ import annotations


class Phase20ReleaseCandidateArtifactsWiringTests:

    def test_wiring_requires_phase20_identity_manifest(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase20_wiring(root)

            # Act
            accepted = self.run_verifier(["--wiring-only"], maybe_root=root)
            bad_tools_build = (
                root / "tools/bazel/BUILD.bazel"
            ).read_text(encoding="utf-8").replace(
                'filegroup(\n    name = "phase20_release_environment_input_manifest",\n    srcs = ["manifests/phase20_release_environment_inputs.template.json"],\n)\n\n',
                "",
            )
            self.write_phase20_wiring(root, maybe_tools_build=bad_tools_build)
            rejected = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(accepted.returncode, 0, accepted.stdout)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("phase20_release_environment_input_manifest",
                      rejected.stdout)

    def test_wiring_rejects_phase17_empty_release_target(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            bad_tools_build = """filegroup(
    name = "phase20_release_environment_input_manifest",
    srcs = ["manifests/phase20_release_environment_inputs.template.json"],
)

filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = [],
)
"""
            self.write_phase20_wiring(root, maybe_tools_build=bad_tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase17_release_candidate_artifacts", result.stdout)
        self.assertIn("phase20_release_environment_input_manifest",
                      result.stdout)

    def test_wiring_rejects_smoke_release_target(self) -> None:
        for bad_label in [
                ":phase17_representative_release_smoke",
                ":representative_release_artifacts",
                "//tools/bazel:phase3_verify",
        ]:
            with self.subTest(bad_label=bad_label):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    bad_tools_build = f"""filegroup(
    name = "phase20_release_environment_input_manifest",
    srcs = ["manifests/phase20_release_environment_inputs.template.json"],
)

filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = ["{bad_label}"],
)
"""
                    self.write_phase20_wiring(
                        root, maybe_tools_build=bad_tools_build)

                    # Act
                    result = self.run_verifier(["--wiring-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(bad_label, result.stdout)

    def test_just_phase20_verify_runs_tests_before_verifier(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.write_phase20_wiring(root)
            bad_justfile = """phase20-verify:
    bazel run //tools/bazel:phase20_verify
    bazel run //tools/bazel:phase20_verify_tests
"""
            self.write_phase20_wiring(root, maybe_justfile=bad_justfile)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tests before verifier", result.stdout)
