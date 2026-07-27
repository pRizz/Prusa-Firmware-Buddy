#!/usr/bin/env python3
from __future__ import annotations

import unittest

from phase17_release_candidate_evidence_test import (
    DEFAULT_OUTPUT_DIR,
    VERIFIER,
    Phase17ReleaseCandidateEvidenceFixture,
)


class Phase17ReleaseCandidateEvidenceFailureTest(
        Phase17ReleaseCandidateEvidenceFixture, unittest.TestCase):

    def test_contract_rejects_invalid_mismatch_class_and_passed_defaults(
            self) -> None:
        cases = [
            ("mismatch_class", "unclassified"),
            ("default_status", "passed"),
            ("default_status", "unsupported-status"),
            ("default_status", "source-contract-passed"),
        ]
        for field, value in cases:
            with self.subTest(field=field):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    contract = self.read_contract(root)
                    contract["rows"][0][field] = value
                    self.write_contract(root, contract)

                    # Act
                    result = self.run_verifier(["--contract-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(value, result.stdout)

    def test_quick_rejects_symlinked_output_root_before_deleting_target(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            victim_dir = root / "build/ci-evidence/phase17-victim"
            victim_dir.mkdir(parents=True)
            marker_path = victim_dir / "do-not-delete.txt"
            marker_path.write_text("victim target must survive\n",
                                   encoding="utf-8")
            output_root = root / DEFAULT_OUTPUT_DIR
            output_root.parent.mkdir(parents=True, exist_ok=True)
            output_root.symlink_to(victim_dir, target_is_directory=True)

            # Act
            result = self.run_verifier(["--quick"], maybe_root=root)

            # Assert
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--output-dir resolves outside", result.stdout)
            self.assertTrue(output_root.is_symlink())
            self.assertTrue(victim_dir.is_dir())
            self.assertEqual(marker_path.read_text(encoding="utf-8"),
                             "victim target must survive\n")
            self.assertFalse((victim_dir / "run-manifest.json").exists())

    def test_security_rejects_forbidden_markers_without_leaking_values(
            self) -> None:
        cases = [
            ("-----BEGIN PRIVATE KEY-----", "private-key-block"),
            ("signing_key_value = super-secret-value", "signing-key-value"),
            ("firmware_payload", "payload-marker"),
            ("password: super-secret-value", "credential-assignment"),
            ("release-candidate passed locally",
             "release-candidate passed locally"),
            ("reference demotion approved", "reference demotion approved"),
        ]
        for marker, expected in cases:
            with self.subTest(expected=expected):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.write_file(root,
                                    "build/ci-evidence/phase17/leak.json",
                                    marker + "\n")

                    # Act
                    result = self.run_verifier(["--security-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout.lower())
                self.assertNotIn("super-secret-value", result.stdout)

    def test_verifier_does_not_embed_forbidden_subprocess_invocations(
            self) -> None:
        # Arrange
        source = VERIFIER.read_text(
            encoding="utf-8") if VERIFIER.exists() else ""

        # Act
        forbidden = [
            needle
            for needle in ["shell=True", "bash -c", "python -c", "node -e"]
            if needle in source
        ]

        # Assert
        self.assertEqual(forbidden, [])

    def test_wiring_accepts_and_rejects_phase17_surface(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)

            # Act
            accepted = self.run_verifier(["--wiring-only"], maybe_root=root)
            bad_justfile = """phase17-verify:
    bazel run //tools/bazel:phase17_verify
    bazel run //tools/bazel:phase17_verify_tests
"""
            self.write_wiring(root, maybe_justfile=bad_justfile)
            rejected = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(accepted.returncode, 0, accepted.stdout)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("tests before verifier", rejected.stdout)

    def test_wiring_rejects_missing_release_label(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(
                encoding="utf-8").replace(
                    'name = "phase17_release_candidate_artifacts"',
                    'name = "phase17_missing_release_candidate_artifacts"',
                    1,
                )
            tools_build = '# name = "phase17_release_candidate_artifacts"\n' + tools_build
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase17_release_candidate_artifacts", result.stdout)

    def test_wiring_rejects_workflow_commands_outside_phase17_case_arms(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            bad_workflow = """case "$command_name" in
  phase17_verify)
    python3 tools/bazel/phase17_release_candidate_evidence.py --quick
    ;;
  unrelated_verify)
    python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only
    python3 tools/bazel/phase17_release_candidate_evidence_test.py
    ;;
  phase17_verify_tests)
    # python3 tools/bazel/phase17_release_candidate_evidence_test.py
    ;;
esac
"""
            self.write_wiring(root, maybe_workflow=bad_workflow)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase17_verify case arm missing required wiring item",
                      result.stdout)
        self.assertIn(
            "phase17_verify_tests case arm missing required wiring item",
            result.stdout)

    def test_wiring_rejects_just_commands_outside_phase17_recipes(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            bad_justfile = """unrelated:
    bazel run //tools/bazel:phase17_verify_tests
    bazel run //tools/bazel:phase17_verify
    bazel build //tools/bazel:phase17_representative_release_smoke

phase17-verify:
    # bazel run //tools/bazel:phase17_verify_tests
    bazel run //tools/bazel:phase17_verify

phase17-release-artifacts-smoke:
    # bazel build //tools/bazel:phase17_representative_release_smoke
"""
            self.write_wiring(root, maybe_justfile=bad_justfile)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase17-verify recipe missing required wiring item",
                      result.stdout)
        self.assertIn(
            "phase17-release-artifacts-smoke recipe missing required wiring item",
            result.stdout)

    def test_wiring_rejects_release_candidate_target_wrapping_smoke_artifacts(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            bad_tools_build = """filegroup(
    name = "phase17_release_candidate_artifacts",
    srcs = [":representative_release_artifacts"],
)

filegroup(
    name = "phase17_representative_release_smoke",
    srcs = [":representative_release_artifacts"],
)
"""
            self.write_wiring(root, maybe_tools_build=bad_tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot wrap local smoke dependencies", result.stdout)

    def test_release_candidate_target_rejects_empty_filegroup(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)
            tools_build = (root / "tools/bazel/BUILD.bazel").read_text(
                encoding="utf-8").replace(
                    'srcs = [":phase20_release_environment_input_manifest"]',
                    "srcs = []",
                    1,
                )
            self.write_wiring(root, maybe_tools_build=tools_build)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("phase20_release_environment_input_manifest",
                      result.stdout)

    def test_release_candidate_target_accepts_phase20_release_input_manifest(
            self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.write_wiring(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_release_candidate_target_rejects_representative_smoke_wrapping(
            self) -> None:
        for bad_label in [
                ":phase17_representative_release_smoke",
                ":representative_release_artifacts",
                "//tools/bazel:phase17_representative_release_smoke",
                "//tools/bazel:representative_release_artifacts",
                "//tools/bazel:phase3_verify",
        ]:
            with self.subTest(bad_label=bad_label):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.write_wiring(root)
                    tools_build = (
                        root / "tools/bazel/BUILD.bazel"
                    ).read_text(encoding="utf-8").replace(
                        'srcs = [":phase20_release_environment_input_manifest"]',
                        f'srcs = ["{bad_label}"]',
                        1,
                    )
                    self.write_wiring(root, maybe_tools_build=tools_build)

                    # Act
                    result = self.run_verifier(["--wiring-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(bad_label, result.stdout)
