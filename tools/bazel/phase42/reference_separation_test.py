import os
import re
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from phase42_test_support import bazel_command, run_command, workspace_root


RETIRED_SWITCH = "BUDDY_BAZEL_EXECUTE_REFERENCE"
REFERENCE_PROVIDER = "//tools/bazel/toolchains:cc_firmware_info"


@dataclass(frozen=True)
class ReferenceRoute:
    label: str
    command_marker: str

    @property
    def plan_label(self) -> str:
        return f"{self.label}_plan"


REFERENCE_ROUTES = (
    ReferenceRoute("reference_build", "utils/build.py"),
    ReferenceRoute("reference_test", "cmake .. -DBOARD=BUDDY"),
    ReferenceRoute("reference_package", "--generate-dfu"),
    ReferenceRoute("reference_simulator", "pytest tests/integration"),
)
FORBIDDEN_QUALIFICATION_EDGES = (
    "EmbeddedToolchainInfo",
    "phase42_qualification",
    "arm_link_smoke",
    "phase42_verify",
)


def _read(relative_path: str) -> str:
    return (workspace_root() / relative_path).read_text(encoding="utf-8")


def _rule_block(source: str, name: str) -> str:
    pattern = re.compile(
        rf"shell_binary\(\s*name\s*=\s*\"{re.escape(name)}\".*?\n\)",
        re.DOTALL,
    )
    maybe_match = pattern.search(source)
    return maybe_match.group(0) if maybe_match else ""


def validate_reference_sources(
    bazelrc: str,
    build_source: str,
    dispatcher: str,
    justfile: str,
    phase2_verifier: str,
) -> list[str]:
    errors: list[str] = []
    for path, source in (
        (".bazelrc", bazelrc),
        ("tools/bazel/BUILD.bazel", build_source),
        ("tools/bazel/reference_contract.sh", dispatcher),
    ):
        if RETIRED_SWITCH in source:
            errors.append(f"{path} retains {RETIRED_SWITCH}")

    for route in REFERENCE_ROUTES:
        for label in (route.label, route.plan_label):
            block = _rule_block(build_source, label)
            if not block:
                errors.append(f"missing explicit reference label {label}")
                continue
            if 'src = "reference_contract.sh"' not in block:
                errors.append(f"{label} must use the fixed reference dispatcher")
            if REFERENCE_PROVIDER not in block:
                errors.append(f"{label} must carry descriptive reference provenance")

            recipe = label.replace("_", "-")
            if label == "reference_simulator":
                recipe_pattern = re.compile(
                    r"(?m)^reference-simulator firmware:\n"
                    r"    bazel run //tools/bazel:reference_simulator -- \{\{quote\(firmware\)\}\}$"
                )
            else:
                recipe_pattern = re.compile(
                    rf"(?m)^{re.escape(recipe)}:\n    bazel run //tools/bazel:{re.escape(label)}$"
                )
            if not recipe_pattern.search(justfile):
                errors.append(f"{recipe} must be one thin bazel run recipe")

        if f"{route.label})" not in dispatcher:
            errors.append(f"dispatcher is missing executable route {route.label}")
        if f"{route.plan_label})" not in dispatcher:
            errors.append(f"dispatcher is missing preview route {route.plan_label}")

    for required in (
        "reference_build_plan",
        "reference_test_plan",
        "reference_package_plan",
        "reference_simulator_plan",
        "unavailable_capability",
        RETIRED_SWITCH,
    ):
        if required not in phase2_verifier:
            errors.append(f"phase2 verifier must assert current contract for {required}")
    if "FORBIDDEN_STRINGS" not in phase2_verifier:
        errors.append("phase2 verifier must reject retired semantics")
    return errors


class ReferenceDefinitionTests(unittest.TestCase):
    def test_explicit_reference_labels_recipes_and_phase2_contract(self) -> None:
        # Arrange
        inputs = (
            _read(".bazelrc"),
            _read("tools/bazel/BUILD.bazel"),
            _read("tools/bazel/reference_contract.sh"),
            _read("justfile"),
            _read("tools/bazel/phase2_verify.py"),
        )

        # Act
        errors = validate_reference_sources(*inputs)

        # Assert
        self.assertEqual([], errors)

    def test_switched_or_authority_provider_mutations_are_rejected(self) -> None:
        # Arrange
        inputs = (
            _read(".bazelrc"),
            _read("tools/bazel/BUILD.bazel"),
            _read("tools/bazel/reference_contract.sh"),
            _read("justfile"),
            _read("tools/bazel/phase2_verify.py"),
        )
        switched = list(inputs)
        switched[2] += f'\nif [[ "${{{RETIRED_SWITCH}:-0}}" == "1" ]]; then true; fi\n'
        embedded = list(inputs)
        embedded[1] = embedded[1].replace(
            REFERENCE_PROVIDER,
            "//tools/bazel/toolchains:phase42_qualification_linux_x86_64",
            1,
        )

        # Act
        mutation_errors = (
            validate_reference_sources(*switched),
            validate_reference_sources(*embedded),
        )

        # Assert
        self.assertTrue(all(errors for errors in mutation_errors))


class ReferenceExecutionTests(unittest.TestCase):
    def _fake_environment(self, temporary: Path, switch_value: str) -> dict[str, str]:
        fake_bin = temporary / "bin"
        fake_bin.mkdir(exist_ok=True)
        fake_command = "#!/usr/bin/env bash\nprintf 'reference-executed:%s\\n' \"$*\" >&2\nexit 23\n"
        for command in ("python3", "pytest", "sh"):
            fake_path = fake_bin / command
            fake_path.write_text(fake_command, encoding="utf-8")
            fake_path.chmod(0o755)
        return {
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            RETIRED_SWITCH: switch_value,
        }

    def test_execution_and_plan_labels_have_fixed_semantics(self) -> None:
        # Arrange
        root = workspace_root()
        with tempfile.TemporaryDirectory(prefix="phase42-reference-") as temporary_name:
            temporary = Path(temporary_name)
            output_base = temporary / "output-base"
            firmware = temporary / "reference firmware.bin"
            firmware.write_bytes(b"firmware")

            for switch_value in ("0", "1"):
                environment = self._fake_environment(temporary, switch_value)
                for route in REFERENCE_ROUTES:
                    with self.subTest(route=route.label, switch=switch_value):
                        execute_command = bazel_command(
                            output_base,
                            "run",
                            f"//tools/bazel:{route.label}",
                            *(("--", str(firmware)) if route.label == "reference_simulator" else ()),
                        )
                        plan_command = bazel_command(
                            output_base,
                            "run",
                            f"//tools/bazel:{route.plan_label}",
                        )

                        # Act
                        execute_result = run_command(
                            execute_command,
                            cwd=root,
                            environment=environment,
                        )
                        plan_result = run_command(
                            plan_command,
                            cwd=root,
                            environment=environment,
                        )

                        # Assert
                        self.assertEqual(23, execute_result.returncode, execute_result.output)
                        self.assertIn("reference-executed:", execute_result.output)
                        self.assertIn(route.command_marker, execute_result.output)
                        self.assertEqual(0, plan_result.returncode, plan_result.output)
                        self.assertIn("reference command:", plan_result.output)
                        if route.label == "reference_simulator":
                            self.assertIn(route.command_marker, plan_result.output)
                        else:
                            escaped_marker = route.command_marker.replace(" ", "\\ ")
                            self.assertIn(escaped_marker, plan_result.output)
                        self.assertNotIn("reference-executed:", plan_result.output)

    def test_simulator_executes_pytest_with_exact_firmware_argument(self) -> None:
        # Arrange
        root = workspace_root()
        with tempfile.TemporaryDirectory(prefix="phase42-reference-simulator-") as temporary_name:
            temporary = Path(temporary_name)
            output_base = temporary / "output-base"
            firmware = temporary / "firmware with spaces.bin"
            firmware.write_bytes(b"firmware")
            fake_bin = temporary / "bin"
            fake_bin.mkdir()
            fake_pytest = fake_bin / "pytest"
            fake_pytest.write_text(
                "#!/usr/bin/env bash\nprintf 'pytest-arg:<%s>\\n' \"$@\" >&2\nexit 23\n",
                encoding="utf-8",
            )
            fake_pytest.chmod(0o755)
            environment = {"PATH": f"{fake_bin}:{os.environ['PATH']}"}
            command = bazel_command(
                output_base,
                "run",
                "//tools/bazel:reference_simulator",
                "--",
                str(firmware),
            )

            # Act
            result = run_command(command, cwd=root, environment=environment)

            # Assert
            self.assertEqual(23, result.returncode, result.output)
            self.assertIn("pytest-arg:<tests/integration>", result.output)
            self.assertIn("pytest-arg:<--firmware>", result.output)
            self.assertIn(f"pytest-arg:<{firmware}>", result.output)

    def test_simulator_rejects_missing_or_nonexistent_firmware(self) -> None:
        # Arrange
        root = workspace_root()
        with tempfile.TemporaryDirectory(prefix="phase42-reference-simulator-invalid-") as temporary_name:
            output_base = Path(temporary_name) / "output-base"
            commands = (
                bazel_command(output_base, "run", "//tools/bazel:reference_simulator"),
                bazel_command(
                    output_base,
                    "run",
                    "//tools/bazel:reference_simulator",
                    "--",
                    "missing-firmware.bin",
                ),
            )

            # Act
            results = [run_command(command, cwd=root) for command in commands]

            # Assert
            self.assertTrue(all(result.returncode == 2 for result in results))
            self.assertIn("Usage:", results[0].output)
            self.assertIn("does not exist", results[1].output)

    def test_reference_closure_actions_and_runfiles_are_non_qualifying(self) -> None:
        # Arrange
        labels = [
            f"//tools/bazel:{label}"
            for route in REFERENCE_ROUTES
            for label in (route.label, route.plan_label)
        ]
        target_set = f"set({' '.join(labels)})"
        root = workspace_root()
        with tempfile.TemporaryDirectory(prefix="phase42-reference-graph-") as temporary_name:
            output_base = Path(temporary_name) / "output-base"

            # Act
            closure = run_command(
                bazel_command(output_base, "query", f"deps({target_set})"),
                cwd=root,
            )
            actions = run_command(
                bazel_command(output_base, "aquery", f"deps({target_set})"),
                cwd=root,
            )
            runfiles = run_command(
                bazel_command(
                    output_base,
                    "cquery",
                    target_set,
                    "--output=starlark",
                    "--starlark:expr=str(target.default_runfiles.files.to_list())",
                ),
                cwd=root,
            )

            # Assert
            for result in (closure, actions, runfiles):
                self.assertEqual(0, result.returncode, result.output)
                for forbidden in FORBIDDEN_QUALIFICATION_EDGES:
                    self.assertNotIn(forbidden, result.stdout)
            self.assertIn(REFERENCE_PROVIDER, closure.stdout)
            self.assertIn("//tools/bazel:reference_contract.sh", closure.stdout)
            self.assertIn("tools/bazel/reference_contract.sh", runfiles.stdout)

    def test_unknown_dispatch_name_exits_two(self) -> None:
        # Arrange
        root = workspace_root()
        with tempfile.TemporaryDirectory(prefix="phase42-reference-unknown-") as temporary_name:
            unknown = Path(temporary_name) / "reference_unknown"
            unknown.symlink_to(root / "tools/bazel/reference_contract.sh")

            # Act
            result = run_command(("bash", str(unknown)), cwd=root)

            # Assert
            self.assertEqual(2, result.returncode, result.output)
            self.assertIn("Unknown Bazel reference contract target", result.output)


if __name__ == "__main__":
    unittest.main()
