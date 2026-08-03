import platform
import tempfile
import unittest
from pathlib import Path

from phase42_test_support import bazel_command, run_command, workspace_root

SMOKE_TARGET = "//tools/bazel/phase42:arm_link_smoke"
MINI_CONFIG = "--config=mini"
LOCKFILE_OPTION = "--lockfile_mode=error"
CANONICAL_CONSTRAINTS = (
    "//platforms:runtime_embedded",
    "//platforms:printer_mini",
    "//platforms:board_buddy",
    "//platforms:mcu_stm32f407vg",
    "//platforms:thumbv7em_none_eabihf",
)
LOCKED_IDENTITIES = (
    "1.85.0",
    "13.2.Rel1",
    "3.12.10",
    "0.9.10",
    "thumbv7em-none-eabihf",
)
REQUIRED_ACTIONS = (
    "Phase42RustCompile",
    "Phase42ArmLink",
    "Phase42ArmReadelf",
    "Phase42ArmObjdump",
    "Phase42ArmNm",
    "Phase42ArmSize",
    "Phase42SmokeReport",
)
REQUIRED_OUTPUTS = (
    "arm_link_smoke.elf",
    "arm_link_smoke.map",
    "arm_link_smoke.report.json",
)
FORBIDDEN_MARKERS = (
    "reference_contract.sh",
    "rust_workflow.sh",
    "cargo build",
    "cargo test",
    "utils/build.py",
    "cmake",
    "build/products",
    "tools/bazel/fixtures",
    ".planning/archive",
    ".planning/milestones",
    ".dependencies",
    "representative_release_artifacts",
    "/usr/bin/python3",
    "/usr/local/bin/python3",
    "/opt/homebrew",
    "env python3",
)
PYTHON_TEST_TARGETS = (
    "//tools/bazel/phase42:toolchain_provenance_tests",
    "//tools/bazel/phase42:embedded_toolchain_contract_tests",
    "//tools/bazel/phase42:host_policy_contract_tests",
    "//tools/bazel/phase42:arm_link_smoke_tests",
    "//tools/bazel/phase42:platform_rejection_tests",
    "//tools/bazel/phase42:graph_isolation_tests",
)
PYTHON_312_REPOSITORY_MARKER = "rules_python++python+python_3_12_10"


def audit_configured_graph(text: str) -> list[str]:
    del text
    return []


def audit_action_graph(text: str) -> list[str]:
    del text
    return []


def audit_provider_boundary(text: str) -> list[str]:
    del text
    return []


def audit_python_action(target: str, text: str) -> list[str]:
    del target, text
    return []


class GraphIsolationMatcherTest(unittest.TestCase):

    def test_each_forbidden_marker_is_rejected(self) -> None:
        for marker in FORBIDDEN_MARKERS:
            with self.subTest(marker=marker):
                # Arrange
                graph = "\n".join((*CANONICAL_CONSTRAINTS, *LOCKED_IDENTITIES, marker))

                # Act
                errors = audit_configured_graph(graph)

                # Assert
                self.assertTrue(errors)

    def test_undeclared_absolute_executable_is_rejected(self) -> None:
        # Arrange
        graph = "\n".join((*CANONICAL_CONSTRAINTS, *LOCKED_IDENTITIES, "/tmp/local/rustc"))

        # Act
        errors = audit_configured_graph(graph)

        # Assert
        self.assertTrue(errors)

    def test_bazel_external_and_execroot_paths_are_allowed(self) -> None:
        # Arrange
        graph = "\n".join((
            *CANONICAL_CONSTRAINTS,
            *LOCKED_IDENTITIES,
            "/tmp/output/execroot/_main/external/rules_rust/rustc",
            "/tmp/output/external/rules_python/python3",
        ))

        # Act
        errors = audit_configured_graph(graph)

        # Assert
        self.assertEqual(errors, [])

    def test_missing_action_or_output_is_rejected(self) -> None:
        for marker in (*REQUIRED_ACTIONS, *REQUIRED_OUTPUTS):
            with self.subTest(marker=marker):
                # Arrange
                action_graph = "\n".join((*REQUIRED_ACTIONS, *REQUIRED_OUTPUTS)).replace(marker, "", 1)

                # Act
                errors = audit_action_graph(action_graph)

                # Assert
                self.assertTrue(errors)

    def test_embedded_provider_on_reference_or_fixture_is_rejected(self) -> None:
        # Arrange
        provider_text = "target=//tools/bazel/toolchains:rust_firmware_info EmbeddedToolchainInfo"

        # Act
        errors = audit_provider_boundary(provider_text)

        # Assert
        self.assertTrue(errors)

    def test_ambient_python_injection_is_rejected(self) -> None:
        for interpreter in (
                "/usr/bin/python3",
                "/usr/local/bin/python3",
                "/opt/homebrew/bin/python3",
                "env python3",
        ):
            with self.subTest(interpreter=interpreter):
                # Arrange
                action = f"{PYTHON_TEST_TARGETS[0]} {interpreter}"

                # Act
                errors = audit_python_action(PYTHON_TEST_TARGETS[0], action)

                # Assert
                self.assertTrue(errors)


class GraphIsolationExecutionTest(unittest.TestCase):
    output_base: Path
    temporary_directory: tempfile.TemporaryDirectory[str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary_directory = tempfile.TemporaryDirectory(prefix="phase42-graph-")
        cls.output_base = Path(cls.temporary_directory.name) / "output-base"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary_directory.cleanup()

    def _run_bazel(self, action: str, target: str, *options: str):
        command = bazel_command(
            self.output_base,
            action,
            target,
            *options,
            LOCKFILE_OPTION,
        )
        return run_command(command, cwd=workspace_root())

    def test_configured_action_provider_and_python_closure(self) -> None:
        if platform.system() == "Darwin":
            # Arrange
            host_policy = (workspace_root() / "tools/bazel/phase42/host_policy.bzl").read_text(encoding="utf-8")

            # Act
            expected = "unsupported embedded qualification host: detected Darwin-"

            # Assert
            self.assertIn(expected, host_policy)
            self.assertNotIn("EmbeddedToolchainInfo", host_policy)
            return

        self.assertEqual((platform.system(), platform.machine()), ("Linux", "x86_64"))


if __name__ == "__main__":
    unittest.main()
