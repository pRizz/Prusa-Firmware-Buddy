from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/bazel/phase18_cutover_review.py"


class Phase18CutoverReviewWiringTests:

    def test_verifier_does_not_use_shell_or_inline_interpreters(self) -> None:
        # Arrange
        source = VERIFIER.read_text(encoding="utf-8")

        # Act / Assert
        for forbidden in ["shell=True", "bash -c", "python -c", "node -e"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_wiring_only_accepts_complete_phase18_wiring(self) -> None:
        # Arrange
        temp_dir, root = self.make_temp_root()
        with temp_dir:
            self.copy_complete_surface(root)
            self.copy_wiring_files(root)

            # Act
            result = self.run_verifier(["--wiring-only"], maybe_root=root)

        # Assert
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_wiring_only_rejects_missing_phase18_entries(self) -> None:
        cases = [
            ("tools/bazel/BUILD.bazel",
             'name = "phase18_source_ref_manifests"'),
            ("tools/bazel/BUILD.bazel",
             "manifests/phase18_cutover_review_contract.json"),
            ("BUILD.bazel", 'name = "phase18_cutover_review_docs"'),
            ("BUILD.bazel", 'name = "phase18_verify_tests"'),
            ("tools/bazel/rust_workflow.sh", "phase18_verify)"),
            ("tools/bazel/rust_workflow.sh",
             "python3 tools/bazel/phase18_cutover_review.py --quick"),
            ("justfile", "phase18-verify:"),
            ("justfile", "bazel run //tools/bazel:phase18_verify_tests"),
        ]
        for path, required_text in cases:
            with self.subTest(path=path, required_text=required_text):
                # Arrange
                temp_dir, root = self.make_temp_root()
                with temp_dir:
                    self.copy_complete_surface(root)
                    self.copy_wiring_files(root)
                    target = root / path
                    target.write_text(target.read_text(
                        encoding="utf-8").replace(required_text, ""),
                                      encoding="utf-8")

                    # Act
                    result = self.run_verifier(["--wiring-only"],
                                               maybe_root=root)

                # Assert
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(required_text, result.stdout)

    def test_just_phase18_verify_runs_tests_before_verifier(self) -> None:
        # Arrange
        justfile = (ROOT / "justfile").read_text(encoding="utf-8")

        # Act
        recipe_index = justfile.find("phase18-verify:")
        tests_index = justfile.find(
            "\n    bazel run //tools/bazel:phase18_verify_tests\n",
            recipe_index)
        verify_index = justfile.find(
            "\n    bazel run //tools/bazel:phase18_verify\n", recipe_index)

        # Assert
        self.assertNotEqual(recipe_index, -1)
        self.assertNotEqual(tests_index, -1)
        self.assertNotEqual(verify_index, -1)
        self.assertLess(tests_index, verify_index)
