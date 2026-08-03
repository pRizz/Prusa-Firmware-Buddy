import copy
import json
import os
import re
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path


ARM_GNU_URL = (
    "https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/"
    "arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz"
)
MINI404_URL = (
    "https://github.com/vintagepc/MINI404/releases/download/v0.9.10/"
    "Mini404-v0.9.10-linux.tar.bz2"
)
EXPECTED_ARCHIVES = {
    "arm_gnu_linux_x86_64": {
        "sha256": "6cd1bbc1d9ae57312bcd169ae283153a9572bd6a8e4eeae2fedfbc33b115fdbb",
        "strip_prefix": "arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi",
        "url": ARM_GNU_URL,
    },
    "mini404_linux_x86_64": {
        "sha256": "2709a43dbb6e64ea4597399d2f0e05be13e70a7b659a18ac61512498d320a5ba",
        "strip_prefix": "Mini404-v0.9.10-linux",
        "url": MINI404_URL,
    },
}
EXPECTED_MODULE_VERSIONS = {
    "rules_cc": "0.2.22",
    "rules_python": "2.2.0",
    "rules_rust": "0.71.3",
}
FORBIDDEN_DECLARATION_PATTERNS = {
    "archive output": r"(?i)(?:^|[/_-])archives?(?:[/_.-]|$)",
    "Cargo": r"(?i)\bcargo(?:\s+|_)(?:build|test|run)\b",
    "CMake output": r"(?i)(?:cmake-build|cmake\s+--build|utils/build\.py)",
    "Darwin archive": r"(?i)(?:darwin|macos|osx)",
    "fixture": r"(?i)(?:^|[/_-])fixtures?(?:[/_.-]|$)",
    "local repository": r"\b(?:new_)?local_repository\s*\(",
    "local tool directory": r"(?:^|[/])\.dependencies(?:[/]|$)",
    "PATH lookup": r"(?i)(?:repository_ctx\.which|ctx\.which|\bwhich\s+|\bPATH\b)",
    "planning artifact": r"(?:^|[/])\.planning(?:[/]|$)",
}


@dataclass(frozen=True)
class ProvenanceInputs:
    bazel_version: str
    lock: dict[str, object]
    module: str
    repositories: str


def _workspace_file(relative_path: str) -> Path:
    runfiles_root = Path(os.environ["TEST_SRCDIR"])
    workspace_name = os.environ["TEST_WORKSPACE"]
    return runfiles_root / workspace_name / relative_path


def _load_inputs() -> ProvenanceInputs:
    return ProvenanceInputs(
        bazel_version=_workspace_file(".bazelversion").read_text(encoding="utf-8"),
        lock=json.loads(
            _workspace_file("MODULE.bazel.lock").read_text(encoding="utf-8")
        ),
        module=_workspace_file("MODULE.bazel").read_text(encoding="utf-8"),
        repositories=_workspace_file(
            "tools/bazel/toolchains/embedded_repositories.bzl"
        ).read_text(encoding="utf-8"),
    )


def validate_provenance(inputs: ProvenanceInputs) -> list[str]:
    errors: list[str] = []
    if inputs.bazel_version != "9.2.0\n":
        errors.append("Bazel must be pinned exactly to 9.2.0")

    for module_name, expected_version in EXPECTED_MODULE_VERSIONS.items():
        declaration = re.compile(
            rf'bazel_dep\(\s*name\s*=\s*"{re.escape(module_name)}"\s*,\s*'
            rf'version\s*=\s*"{re.escape(expected_version)}"\s*,?\s*\)',
            re.MULTILINE,
        )
        if declaration.search(inputs.module) is None:
            errors.append(f"{module_name} must be pinned to {expected_version}")

    required_module_fragments = (
        'edition = "2024"',
        'extra_target_triples = ["thumbv7em-none-eabihf"]',
        'versions = ["1.85.0"]',
        'python_version = "3.12.10"',
        '"//tools/bazel/toolchains:embedded_repositories.bzl"',
        '"embedded_repositories"',
        '"arm_gnu_linux_x86_64"',
        '"mini404_linux_x86_64"',
    )
    for fragment in required_module_fragments:
        if fragment not in inputs.module:
            errors.append(f"MODULE.bazel is missing exact declaration: {fragment}")

    for repository_name, expected in EXPECTED_ARCHIVES.items():
        if f'name = "{repository_name}"' not in inputs.repositories:
            errors.append(f"missing repository {repository_name}")
        for field_name, value in expected.items():
            if f'{field_name} = "{value}"' not in inputs.repositories:
                errors.append(
                    f"{repository_name} has wrong {field_name}; expected {value}"
                )

    hash_values = re.findall(r'sha256\s*=\s*"([^"]*)"', inputs.repositories)
    if len(hash_values) != len(EXPECTED_ARCHIVES):
        errors.append("exactly two archive SHA-256 declarations are required")
    for hash_value in hash_values:
        if re.fullmatch(r"[0-9a-f]{64}", hash_value) is None:
            errors.append("archive SHA-256 must be a non-placeholder lowercase digest")
        elif len(set(hash_value)) == 1:
            errors.append("archive SHA-256 must not be a repeated placeholder digit")

    declaration_text = f"{inputs.module}\n{inputs.repositories}"
    for fallback_name, fallback_pattern in FORBIDDEN_DECLARATION_PATTERNS.items():
        if re.search(fallback_pattern, declaration_text) is not None:
            errors.append(f"forbidden {fallback_name} fallback")

    lock_text = json.dumps(inputs.lock, sort_keys=True)
    for required_lock_value in (
        "rules_cc",
        "rules_python",
        "rules_rust",
        "arm_gnu_linux_x86_64",
        "mini404_linux_x86_64",
    ):
        if required_lock_value not in lock_text:
            errors.append(f"MODULE.bazel.lock is missing {required_lock_value}")

    return errors


class ToolchainProvenanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = _load_inputs()

    def test_committed_declarations_match_exact_contract(self) -> None:
        # Arrange
        inputs = self.inputs

        # Act
        errors = validate_provenance(inputs)

        # Assert
        self.assertEqual(errors, [])

    def test_each_exact_version_mutation_is_rejected(self) -> None:
        for exact_version in (
            "9.2.0",
            "0.71.3",
            "1.85.0",
            "0.2.22",
            "2.2.0",
            "3.12.10",
            "0.9.10",
            "13.2.rel1",
            "thumbv7em-none-eabihf",
        ):
            with self.subTest(exact_version=exact_version):
                # Arrange
                mutated = ProvenanceInputs(
                    bazel_version=self.inputs.bazel_version.replace(
                        exact_version, "99.99.99"
                    ),
                    lock=self.inputs.lock,
                    module=self.inputs.module.replace(exact_version, "99.99.99"),
                    repositories=self.inputs.repositories.replace(
                        exact_version, "99.99.99"
                    ),
                )

                # Act
                errors = validate_provenance(mutated)

                # Assert
                self.assertTrue(errors)

    def test_each_archive_identity_mutation_is_rejected(self) -> None:
        for expected in EXPECTED_ARCHIVES.values():
            for field_name, exact_value in expected.items():
                with self.subTest(field_name=field_name, exact_value=exact_value):
                    # Arrange
                    mutated = ProvenanceInputs(
                        bazel_version=self.inputs.bazel_version,
                        lock=self.inputs.lock,
                        module=self.inputs.module,
                        repositories=self.inputs.repositories.replace(
                            exact_value, f"mutated-{field_name}"
                        ),
                    )

                    # Act
                    errors = validate_provenance(mutated)

                    # Assert
                    self.assertTrue(errors)

    def test_each_forbidden_fallback_class_is_rejected(self) -> None:
        forbidden_mutations = (
            'new_local_repository(name = "ambient")',
            'repository_ctx.which("arm-none-eabi-gcc")',
            'tool_path = "/tmp/.dependencies/arm-none-eabi-gcc"',
            'url = "https://example.invalid/tool-darwin.tar.xz"',
            'command = "cargo build"',
            'command = "cmake --build output"',
            'source = "tools/bazel/fixtures/firmware.bin"',
            'source = ".planning/archive/firmware.elf"',
            'source = "release/archives/firmware.elf"',
        )
        for mutation in forbidden_mutations:
            with self.subTest(mutation=mutation):
                # Arrange
                mutated = ProvenanceInputs(
                    bazel_version=self.inputs.bazel_version,
                    lock=self.inputs.lock,
                    module=f"{self.inputs.module}\n{mutation}\n",
                    repositories=self.inputs.repositories,
                )

                # Act
                errors = validate_provenance(mutated)

                # Assert
                self.assertTrue(errors)

    def test_placeholder_hashes_are_rejected(self) -> None:
        for placeholder_hash in ("", "0" * 64, "sha256-placeholder"):
            with self.subTest(placeholder_hash=placeholder_hash):
                # Arrange
                original_hash = EXPECTED_ARCHIVES["arm_gnu_linux_x86_64"]["sha256"]
                mutated = ProvenanceInputs(
                    bazel_version=self.inputs.bazel_version,
                    lock=self.inputs.lock,
                    module=self.inputs.module,
                    repositories=self.inputs.repositories.replace(
                        original_hash, placeholder_hash
                    ),
                )

                # Act
                errors = validate_provenance(mutated)

                # Assert
                self.assertTrue(errors)

    def test_declared_python_interpreter_is_exact_and_not_ambient(self) -> None:
        # Arrange
        interpreter_path = Path(sys.executable).as_posix()
        ambient_prefixes = ("/usr/bin/", "/usr/local/bin/", "/opt/homebrew/")

        # Act
        is_exact_version = sys.version_info[:3] == (3, 12, 10)
        is_ambient = interpreter_path.startswith(ambient_prefixes)

        # Assert
        self.assertTrue(is_exact_version, sys.version)
        self.assertFalse(is_ambient, interpreter_path)
        self.assertNotEqual(Path(interpreter_path).name, "python3")

    def test_lock_mutation_is_rejected(self) -> None:
        # Arrange
        mutated_lock = copy.deepcopy(self.inputs.lock)
        mutated_lock["moduleExtensions"] = {}
        mutated = ProvenanceInputs(
            bazel_version=self.inputs.bazel_version,
            lock=mutated_lock,
            module=self.inputs.module,
            repositories=self.inputs.repositories,
        )

        # Act
        errors = validate_provenance(mutated)

        # Assert
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
