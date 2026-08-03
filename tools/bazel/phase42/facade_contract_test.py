import platform
import re
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from phase42_test_support import bazel_command, run_command, workspace_root


MINI_OPTIONS = ("--config=mini", "--noskip_incompatible_explicit_targets")
LINUX_REMEDY = "use canonical Linux x86_64 CI/container"


@dataclass(frozen=True)
class Capability:
    label: str
    owning_phase: str
    available_command: str


CAPABILITIES = (
    Capability(
        "build_firmware",
        "Phase 46",
        "bazel build //tools/bazel/phase42:arm_link_smoke --config=mini --noskip_incompatible_explicit_targets",
    ),
    Capability(
        "test_firmware",
        "Phase 43/46",
        "bazel test //tools/bazel/phase42:phase42_verifier_tests --config=mini --noskip_incompatible_explicit_targets",
    ),
    Capability(
        "release_package",
        "Phase 47",
        "bazel build //tools/bazel/phase42:arm_link_smoke --config=mini --noskip_incompatible_explicit_targets",
    ),
    Capability(
        "release_packages",
        "Phase 47",
        "bazel build //tools/bazel/phase42:arm_link_smoke --config=mini --noskip_incompatible_explicit_targets",
    ),
    Capability(
        "simulator_parity",
        "Phase 48",
        "bazel test //tools/bazel/phase42:phase42_verifier_tests --config=mini --noskip_incompatible_explicit_targets",
    ),
)


def _read(relative_path: str) -> str:
    return (workspace_root() / relative_path).read_text(encoding="utf-8")


def _rule_block(source: str, rule_kind: str, name: str) -> str:
    pattern = re.compile(
        rf"{re.escape(rule_kind)}\(\s*name\s*=\s*\"{re.escape(name)}\".*?\n\)",
        re.DOTALL,
    )
    maybe_match = pattern.search(source)
    return maybe_match.group(0) if maybe_match else ""


def validate_authority_definitions(build_source: str, gate_source: str) -> list[str]:
    errors: list[str] = []
    if 'load("//tools/bazel/phase42:capability_gate.bzl", "unavailable_capability")' not in build_source:
        errors.append("authority BUILD must load unavailable_capability")

    for capability in CAPABILITIES:
        block = _rule_block(build_source, "unavailable_capability", capability.label)
        if not block:
            errors.append(f"{capability.label} must be an unavailable_capability")
            continue
        if f'owning_phase = "{capability.owning_phase}"' not in block:
            errors.append(f"{capability.label} must name {capability.owning_phase}")
        if f'available_command = "{capability.available_command}"' not in block:
            errors.append(f"{capability.label} must name its exact Phase 42 remedy")

    if _rule_block(build_source, "filegroup", "release_package"):
        errors.append("release_package must not be a fixture-backed filegroup")
    if 'name = "phase3_fixture_release_artifacts"' not in build_source:
        errors.append("historical package fixtures need an explicit phase3_fixture name")
    for forbidden in (
        "ctx.actions",
        "DefaultInfo",
        "OutputGroupInfo",
        "EmbeddedToolchainInfo",
    ):
        if forbidden in gate_source:
            errors.append(f"capability gate must not expose {forbidden}")
    for required in (
        "def unavailable_capability(",
        "host_policy = toolchain.host_policy",
        "fail(",
        "capability unavailable",
    ):
        if required not in gate_source:
            errors.append(f"capability gate is missing {required}")
    return errors


class FacadeDefinitionTests(unittest.TestCase):
    def test_authority_definitions_are_analysis_time_gates(self) -> None:
        # Arrange
        build_source = _read("tools/bazel/BUILD.bazel")
        gate_path = workspace_root() / "tools/bazel/phase42/capability_gate.bzl"
        gate_source = gate_path.read_text(encoding="utf-8") if gate_path.exists() else ""

        # Act
        errors = validate_authority_definitions(build_source, gate_source)

        # Assert
        self.assertEqual([], errors)

    def test_runtime_or_fixture_mutations_are_rejected(self) -> None:
        # Arrange
        build_source = _read("tools/bazel/BUILD.bazel")
        gate_path = workspace_root() / "tools/bazel/phase42/capability_gate.bzl"
        if not gate_path.exists():
            self.skipTest("capability gate implementation does not exist yet")
        gate_source = gate_path.read_text(encoding="utf-8")
        mutations = (
            build_source.replace(
                'unavailable_capability(\n    name = "build_firmware"',
                'shell_binary(\n    name = "build_firmware"',
                1,
            ),
            build_source.replace(
                'unavailable_capability(\n    name = "release_package"',
                'filegroup(\n    name = "release_package"',
                1,
            ),
        )

        # Act
        mutation_errors = [
            validate_authority_definitions(mutation, gate_source) for mutation in mutations
        ]

        # Assert
        self.assertTrue(all(errors for errors in mutation_errors))


class FacadeCommandTests(unittest.TestCase):
    def test_darwin_smoke_uses_the_host_policy_diagnostic(self) -> None:
        # Arrange
        if platform.system() != "Darwin":
            self.skipTest("Darwin host-policy route only")
        root = workspace_root()

        with tempfile.TemporaryDirectory(prefix="phase42-smoke-host-") as temporary:
            output_base = Path(temporary) / "output-base"
            command = bazel_command(
                output_base,
                "build",
                "//tools/bazel/phase42:arm_link_smoke",
                *MINI_OPTIONS,
            )

            # Act
            result = run_command(command, cwd=root)

            # Assert
            self.assertNotEqual(0, result.returncode, result.output)
            self.assertIn("unsupported embedded qualification host", result.output)
            self.assertIn(f"detected Darwin-{platform.machine()}", result.output)
            self.assertIn(LINUX_REMEDY, result.output)
            self.assertNotIn("No matching toolchains", result.output)

    def test_build_and_run_fail_during_analysis_with_exact_diagnostics(self) -> None:
        # Arrange
        root = workspace_root()
        host = f"{platform.system()}-{platform.machine()}"

        with tempfile.TemporaryDirectory(prefix="phase42-facade-") as temporary:
            output_base = Path(temporary) / "output-base"
            for capability in CAPABILITIES:
                for action in ("build", "run"):
                    with self.subTest(label=capability.label, action=action, host=host):
                        command = bazel_command(
                            output_base,
                            action,
                            f"//tools/bazel:{capability.label}",
                            *MINI_OPTIONS,
                        )

                        # Act
                        result = run_command(command, cwd=root)

                        # Assert
                        self.assertNotEqual(0, result.returncode, result.output)
                        self.assertIn(capability.owning_phase, result.output)
                        self.assertIn(capability.available_command, result.output)
                        if platform.system() == "Darwin":
                            self.assertIn("unsupported embedded qualification host", result.output)
                            self.assertIn(f"detected Darwin-{platform.machine()}", result.output)
                            self.assertIn(LINUX_REMEDY, result.output)
                        else:
                            self.assertIn("capability unavailable", result.output)
                        self.assertNotIn("command succeeded", result.output.lower())

    def test_test_host_is_a_nonzero_migration_gate(self) -> None:
        # Arrange
        root = workspace_root()

        with tempfile.TemporaryDirectory(prefix="phase42-test-host-") as temporary:
            output_base = Path(temporary) / "output-base"
            command = bazel_command(
                output_base,
                "build",
                "//tools/bazel:test_host",
                *MINI_OPTIONS,
            )

            # Act
            result = run_command(command, cwd=root)

            # Assert
            self.assertNotEqual(0, result.returncode, result.output)
            self.assertIn("test_firmware", result.output)
            self.assertIn("reference_test", result.output)


if __name__ == "__main__":
    unittest.main()
