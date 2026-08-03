import importlib.util
import re
import unittest
from pathlib import Path

from phase42_test_support import CommandResult, workspace_root


LINUX_REMEDY = "canonical Linux x86_64 CI/container"
PHASE42_TESTS = (
    "toolchain_provenance_tests",
    "embedded_toolchain_contract_tests",
    "host_policy_contract_tests",
    "arm_link_smoke_tests",
    "platform_rejection_tests",
    "graph_isolation_tests",
    "facade_contract_tests",
    "reference_separation_tests",
    "phase42_verify_contract_tests",
)
PHASE42_RECIPES = {
    "phase42-toolchain-resolution":
        "bazel test //tools/bazel/phase42:phase42_toolchain_resolution",
    "phase42-arm-link-smoke":
        "bazel build //tools/bazel/phase42:phase42_arm_link_smoke --config=mini --noskip_incompatible_explicit_targets",
    "phase42-platform-negatives":
        "bazel test //tools/bazel/phase42:phase42_platform_negatives",
    "phase42-host-check":
        "bazel run //tools/bazel/phase42:phase42_host_check",
    "phase42-verify":
        "bazel run //tools/bazel/phase42:phase42_verify",
}
STABLE_RECIPES = {
    "build":
        "bazel run //tools/bazel:build_firmware --config=mini --noskip_incompatible_explicit_targets",
    "test":
        "bazel run //tools/bazel:test_firmware --config=mini --noskip_incompatible_explicit_targets",
    "release-package":
        "bazel run //tools/bazel:release_package --config=mini --noskip_incompatible_explicit_targets",
    "simulator-parity":
        "bazel run //tools/bazel:simulator_parity --config=mini --noskip_incompatible_explicit_targets",
}


def _read(relative_path: str) -> str:
    return (workspace_root() / relative_path).read_text(encoding="utf-8")


def _recipe_body(justfile: str, recipe: str) -> str:
    maybe_match = re.search(
        rf"(?m)^{re.escape(recipe)}:\n(?P<body>(?:    .*\n)+)",
        justfile,
    )
    return maybe_match.group("body").strip() if maybe_match else ""


def validate_aggregate_sources(build: str, justfile: str, verifier: str) -> list[str]:
    errors: list[str] = []
    for target in (
        "phase42_toolchain_resolution",
        "phase42_arm_link_smoke",
        "phase42_platform_negatives",
        "phase42_host_check",
        "phase42_verify",
        "phase42_verifier_tests",
    ):
        if f'name = "{target}"' not in build:
            errors.append(f"missing Phase 42 target {target}")
    for test_target in PHASE42_TESTS:
        if f'":{test_target}"' not in build:
            errors.append(f"aggregate omits {test_target}")
    for recipe, expected_body in (*PHASE42_RECIPES.items(), *STABLE_RECIPES.items()):
        body = _recipe_body(justfile, recipe)
        if body != expected_body:
            errors.append(f"{recipe} must be the exact status-preserving Bazel invocation")
        if any(fallback in body for fallback in ("||", "python3", "cargo ", "cmake")):
            errors.append(f"{recipe} contains a fallback or ambient command")
    for marker in (
        "canonical Linux x86_64",
        "MODULE.bazel.lock",
        "3.12.10",
        "arm_link_smoke.elf",
        "arm_link_smoke.map",
        "arm_link_smoke.report.json",
        "toolchain_provenance_tests",
        "platform_rejection_tests",
        "graph_isolation_tests",
        "facade_contract_tests",
        "reference_separation_tests",
    ):
        if marker not in verifier:
            errors.append(f"aggregate verifier is missing {marker}")
    for forbidden in ("phase2_verify.py", "cargo build", "cmake --build"):
        if forbidden in verifier:
            errors.append(f"aggregate verifier contains forbidden route {forbidden}")
    return errors


def _load_verifier():
    verifier_path = workspace_root() / "tools/bazel/phase42/phase42_verify.py"
    maybe_spec = importlib.util.spec_from_file_location("phase42_verify", verifier_path)
    if maybe_spec is None or maybe_spec.loader is None:
        raise AssertionError("unable to load phase42 verifier")
    module = importlib.util.module_from_spec(maybe_spec)
    maybe_spec.loader.exec_module(module)
    return module


class AggregateDefinitionTests(unittest.TestCase):
    def test_targets_recipes_and_verifier_have_one_truthful_contract(self) -> None:
        # Arrange
        inputs = (
            _read("tools/bazel/phase42/BUILD.bazel"),
            _read("justfile"),
            _read("tools/bazel/phase42/phase42_verify.py"),
        )

        # Act
        errors = validate_aggregate_sources(*inputs)

        # Assert
        self.assertEqual([], errors)

    def test_false_success_recipe_mutations_are_rejected(self) -> None:
        # Arrange
        build = _read("tools/bazel/phase42/BUILD.bazel")
        justfile = _read("justfile")
        verifier = _read("tools/bazel/phase42/phase42_verify.py")
        mutations = (
            justfile.replace(STABLE_RECIPES["build"], "python3 utils/build.py", 1),
            justfile.replace(STABLE_RECIPES["release-package"],
                             "bazel build //tools/bazel:phase3_fixture_release_artifacts", 1),
            justfile.replace(PHASE42_RECIPES["phase42-verify"],
                             f'{PHASE42_RECIPES["phase42-verify"]} || true', 1),
        )

        # Act
        mutation_errors = [
            validate_aggregate_sources(build, mutation, verifier)
            for mutation in mutations
        ]

        # Assert
        self.assertTrue(all(errors for errors in mutation_errors))


class AggregateHostPolicyTests(unittest.TestCase):
    def test_darwin_aggregate_stops_before_positive_commands(self) -> None:
        # Arrange
        verifier = _load_verifier()
        calls: list[tuple[str, ...]] = []

        def runner(command, *, cwd):
            calls.append(tuple(command))
            return CommandResult(tuple(command), 0, "", "")

        # Act
        result = verifier.verify(
            mode="aggregate",
            system="Darwin",
            machine="arm64",
            runner=runner,
            maybe_root=Path("/workspace"),
        )

        # Assert
        self.assertEqual(1, result.returncode)
        self.assertEqual([], calls)
        self.assertIn("detected Darwin-arm64", result.output)
        self.assertIn(LINUX_REMEDY, result.output)
        self.assertIn("no positive evidence is possible here", result.output)

    def test_darwin_host_check_proves_every_rejection_route(self) -> None:
        # Arrange
        verifier = _load_verifier()
        diagnostic = (
            "unsupported embedded qualification host: detected Darwin-x86_64; "
            f"use {LINUX_REMEDY}"
        )
        calls: list[tuple[str, ...]] = []

        def runner(command, *, cwd):
            calls.append(tuple(command))
            return CommandResult(tuple(command), 1, "", diagnostic)

        # Act
        result = verifier.verify(
            mode="host-check",
            system="Darwin",
            machine="x86_64",
            runner=runner,
            maybe_root=Path("/workspace"),
        )

        # Assert
        self.assertEqual(0, result.returncode, result.output)
        rendered = [" ".join(command) for command in calls]
        for marker in (
            "arm_link_smoke",
            "build_firmware",
            "test_firmware",
            "release_package",
            "simulator_parity",
            "just build",
            "just test",
            "just release-package",
            "just simulator-parity",
            "phase42:phase42_verify",
        ):
            self.assertTrue(any(marker in command for command in rendered), marker)


if __name__ == "__main__":
    unittest.main()
