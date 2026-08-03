import platform
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from phase42_test_support import bazel_command, run_command, workspace_root

SMOKE_TARGET = "//tools/bazel/phase42:arm_link_smoke"
EXACT_TARGET_OPTION = "--noskip_incompatible_explicit_targets"
MINI_CONFIG = "--config=mini"
LOCKFILE_OPTION = "--lockfile_mode=error"
CANONICAL_CONSTRAINTS = (
    "//platforms:runtime_embedded",
    "//platforms:printer_mini",
    "//platforms:board_buddy",
    "//platforms:mcu_stm32f407vg",
    "//platforms:thumbv7em_none_eabihf",
)
NON_MINI_PLATFORMS = (
    "//platforms:mk4_xbuddy_stm32f427zi",
    "//platforms:coreone_xbuddy_stm32f427zi",
    "//platforms:xl_xlbuddy_stm32f427zi",
    "//platforms:dwarf_stm32g070rbt6",
    "//platforms:modularbed_stm32g070rbt6",
    "//platforms:xbuddy_extension_stm32h503cbu7",
)
WRONG_TUPLE_PLATFORMS = (
    "//tools/bazel/phase42:wrong_printer_platform",
    "//tools/bazel/phase42:wrong_board_platform",
    "//tools/bazel/phase42:wrong_mcu_platform",
    "//tools/bazel/phase42:wrong_triple_platform",
    "//tools/bazel/phase42:soft_float_platform",
)
MISSING_CAPABILITY_TARGETS = (
    "//tools/bazel/phase42:missing_rust_capability",
    "//tools/bazel/phase42:missing_arm_capability",
    "//tools/bazel/phase42:missing_python_capability",
    "//tools/bazel/phase42:missing_mini404_capability",
)


@dataclass(frozen=True)
class NegativeCase:
    name: str
    target: str
    options: tuple[str, ...]
    expected_marker: str


def _read(relative_path: str) -> str:
    return (workspace_root() / relative_path).read_text(encoding="utf-8")


def _negative_cases() -> tuple[tuple[NegativeCase, ...], ...]:
    selection_cases = (
        NegativeCase("default platform", SMOKE_TARGET, (), SMOKE_TARGET),
        NegativeCase("host_tools", SMOKE_TARGET, ("--config=host",), SMOKE_TARGET),
    )
    product_cases = tuple(
        NegativeCase(
            platform_label.rsplit(":", 1)[-1],
            SMOKE_TARGET,
            (f"--platforms={platform_label}",),
            SMOKE_TARGET,
        ) for platform_label in NON_MINI_PLATFORMS
    )
    tuple_cases = tuple(
        NegativeCase(
            platform_label.rsplit(":", 1)[-1],
            SMOKE_TARGET,
            (f"--platforms={platform_label}",),
            SMOKE_TARGET,
        ) for platform_label in WRONG_TUPLE_PLATFORMS
    )
    capability_cases = tuple(
        NegativeCase(
            target.rsplit(":", 1)[-1],
            target,
            (MINI_CONFIG,),
            target.rsplit(":", 1)[-1].replace("_capability", "_toolchain_type"),
        ) for target in MISSING_CAPABILITY_TARGETS
    )
    return selection_cases, product_cases, tuple_cases, capability_cases


def _assert_negative(test: unittest.TestCase, result, case: NegativeCase) -> None:
    test.assertNotEqual(result.returncode, 0, msg=f"{case.name} unexpectedly passed\n{result.output}")
    lowered = result.output.lower()
    test.assertNotIn("build completed successfully", lowered)
    test.assertNotIn("target was skipped", lowered)
    test.assertIn(case.expected_marker.lower(), lowered)
    test.assertTrue(
        "error:" in lowered or "failed:" in lowered,
        msg=f"{case.name} did not emit a Bazel failure diagnostic\n{result.output}",
    )


class PlatformRejectionContractTest(unittest.TestCase):

    def test_matrix_declares_exact_target_fail_closed_cases(self) -> None:
        # Arrange
        source = _read("tools/bazel/phase42/platform_rejection_test.py")
        build = _read("tools/bazel/phase42/BUILD.bazel")
        platform_contract = _read("tools/bazel/phase42/platform_contract.bzl")

        # Act
        source_missing = [
            marker for marker in (
                EXACT_TARGET_OPTION,
                *NON_MINI_PLATFORMS,
                *WRONG_TUPLE_PLATFORMS,
                *MISSING_CAPABILITY_TARGETS,
            ) if marker not in source
        ]
        build_missing = [
            marker for marker in (
                'name = "thumbv7em_none_eabi"',
                'name = "wrong_triple"',
                'name = "wrong_printer_platform"',
                'name = "wrong_board_platform"',
                'name = "wrong_mcu_platform"',
                'name = "wrong_triple_platform"',
                'name = "soft_float_platform"',
                'name = "missing_rust_capability"',
                'name = "missing_arm_capability"',
                'name = "missing_python_capability"',
                'name = "missing_mini404_capability"',
            ) if marker not in build
        ]
        contract_missing = [
            constraint for constraint in CANONICAL_CONSTRAINTS
            if constraint not in platform_contract
        ]

        # Assert
        self.assertEqual(source_missing, [])
        self.assertEqual(build_missing, [])
        self.assertEqual(contract_missing, [])

    def test_support_preserves_subprocess_status_and_output(self) -> None:
        # Arrange
        support = _read("tools/bazel/phase42/phase42_test_support.py")

        # Act
        missing = [
            marker for marker in (
                "subprocess.run(",
                "check=False",
                "capture_output=True",
                "text=True",
                "completed.returncode",
                "completed.stdout",
                "completed.stderr",
            ) if marker not in support
        ]

        # Assert
        self.assertEqual(missing, [])


class PlatformRejectionExecutionTest(unittest.TestCase):
    output_base: Path
    temporary_directory: tempfile.TemporaryDirectory[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary_directory = tempfile.TemporaryDirectory(prefix="phase42-platform-")
        cls.output_base = Path(cls.temporary_directory.name) / "output-base"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary_directory.cleanup()

    def _run_bazel(self, target: str, *options: str):
        command = bazel_command(
            self.output_base,
            "build",
            target,
            *options,
            EXACT_TARGET_OPTION,
            LOCKFILE_OPTION,
        )
        return run_command(command, cwd=workspace_root())

    def _assert_positive_control(self) -> None:
        result = self._run_bazel(SMOKE_TARGET, MINI_CONFIG)
        self.assertEqual(result.returncode, 0, msg=result.output)
        self.assertNotIn("skipped", result.output.lower())

    def test_exact_platform_and_capability_matrix(self) -> None:
        detected_system = platform.system()
        detected_arch = platform.machine()
        if detected_system == "Darwin":
            # Arrange
            host_policy = _read("tools/bazel/phase42/host_policy.bzl")

            # Act
            expected = (
                "unsupported embedded qualification host: detected "
                f"Darwin-{'arm64' if detected_arch in ('arm64', 'aarch64') else 'x86_64'}; "
                "use canonical Linux x86_64 CI/container"
            )

            # Assert
            self.assertIn(expected, host_policy)
            self.assertNotIn("EmbeddedToolchainInfo", host_policy)
            return

        self.assertEqual((detected_system, detected_arch), ("Linux", "x86_64"))
        for group in _negative_cases():
            self._assert_positive_control()
            for case in group:
                with self.subTest(case=case.name):
                    result = self._run_bazel(case.target, *case.options)
                    _assert_negative(self, result, case)
            self._assert_positive_control()


if __name__ == "__main__":
    unittest.main()
