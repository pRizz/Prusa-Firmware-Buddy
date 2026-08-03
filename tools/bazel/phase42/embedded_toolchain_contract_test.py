import re
import unittest
from dataclasses import dataclass, replace
from pathlib import Path

CANONICAL_CONSTRAINTS = (
    "//platforms:runtime_embedded",
    "//platforms:printer_mini",
    "//platforms:board_buddy",
    "//platforms:mcu_stm32f407vg",
    "//platforms:thumbv7em_none_eabihf",
)
CANONICAL_PLATFORM_VALUES = tuple(
    value.replace("//platforms", "") for value in CANONICAL_CONSTRAINTS)
EMBEDDED_PROVIDER_FIELDS = (
    "rustc",
    "arm_gcc",
    "arm_objcopy",
    "arm_objdump",
    "arm_readelf",
    "arm_nm",
    "arm_size",
    "python",
    "mini404",
    "versions",
    "target_triple",
)
EXECUTABLE_LABELS = {
    "rustc": "@rust_linux_x86_64_thumbv7em_none_eabihf_tools//:rustc",
    "arm_gcc": "@arm_gnu_linux_x86_64//:bin/arm-none-eabi-gcc",
    "arm_objcopy": "@arm_gnu_linux_x86_64//:bin/arm-none-eabi-objcopy",
    "arm_objdump": "@arm_gnu_linux_x86_64//:bin/arm-none-eabi-objdump",
    "arm_readelf": "@arm_gnu_linux_x86_64//:bin/arm-none-eabi-readelf",
    "arm_nm": "@arm_gnu_linux_x86_64//:bin/arm-none-eabi-nm",
    "arm_size": "@arm_gnu_linux_x86_64//:bin/arm-none-eabi-size",
    "python": "@python_3_12_10//:python3",
    "mini404": "@mini404_linux_x86_64//:qemu-system-buddy",
}
VERSION_FRAGMENTS = (
    '"rust": "1.85.0"',
    '"arm_gnu": "13.2.Rel1"',
    '"python": "3.12.10"',
    '"mini404": "0.9.10"',
)


@dataclass(frozen=True)
class EmbeddedContractInputs:
    module: str
    platform: str
    platform_contract: str
    toolchain_build: str
    toolchain_rule: str
    reference_rule: str


def _workspace_file(relative_path: str) -> Path:
    return Path(__file__).resolve().parents[3] / relative_path


def _read(relative_path: str) -> str:
    return _workspace_file(relative_path).read_text(encoding="utf-8")


def _load_inputs() -> EmbeddedContractInputs:
    return EmbeddedContractInputs(
        module=_read("MODULE.bazel"),
        platform=_read("platforms/BUILD.bazel"),
        platform_contract=_read("tools/bazel/phase42/platform_contract.bzl"),
        toolchain_build=_read("tools/bazel/toolchains/BUILD.bazel"),
        toolchain_rule=_read("tools/bazel/toolchains/embedded_toolchain.bzl"),
        reference_rule=_read("tools/bazel/toolchains/reference_toolchain.bzl"),
    )


def _string_values(block: str) -> tuple[str, ...]:
    return tuple(re.findall(r'"([^"]+)"', block))


def _assigned_list(source: str, name: str) -> tuple[str, ...]:
    maybe_match = re.search(rf"{re.escape(name)}\s*=\s*\[(.*?)\]", source,
                            re.DOTALL)
    if maybe_match is None:
        return ()
    return _string_values(maybe_match.group(1))


def _named_call(source: str, function_name: str, name: str) -> str:
    maybe_match = re.search(
        rf"{re.escape(function_name)}\(\s*.*?name\s*=\s*\"{re.escape(name)}\"(.*?)\n\)",
        source,
        re.DOTALL,
    )
    return maybe_match.group(0) if maybe_match is not None else ""


def _provider_fields(source: str) -> tuple[str, ...]:
    maybe_match = re.search(
        r"EmbeddedToolchainInfo\s*=\s*provider\(\s*fields\s*=\s*\{(.*?)\}\s*,?\s*\)",
        source,
        re.DOTALL,
    )
    if maybe_match is None:
        return ()
    return tuple(
        re.findall(r'^\s*"([^"]+)"\s*:', maybe_match.group(1), re.MULTILINE))


def validate_embedded_contract(inputs: EmbeddedContractInputs) -> list[str]:
    errors: list[str] = []
    constraints = _assigned_list(inputs.platform_contract,
                                 "PHASE42_MINI_CONSTRAINTS")
    if constraints != CANONICAL_CONSTRAINTS:
        errors.append(
            "PHASE42_MINI_CONSTRAINTS must be the exact five-value tuple")

    required_platform_fragments = (
        'constraint_setting(name = "rust_target")',
        'name = "thumbv7em_none_eabihf"',
        'constraint_setting = ":rust_target"',
    )
    for fragment in required_platform_fragments:
        if fragment not in inputs.platform:
            errors.append(f"platform declaration is missing {fragment}")

    mini_platform = _named_call(inputs.platform, "platform",
                                "mini_buddy_stm32f407vg")
    maybe_values = re.search(r"constraint_values\s*=\s*\[(.*?)\]",
                             mini_platform, re.DOTALL)
    platform_values = (_string_values(maybe_values.group(1))
                       if maybe_values is not None else ())
    if platform_values != CANONICAL_PLATFORM_VALUES:
        errors.append(
            "canonical MINI platform must contain exactly five values")

    if _provider_fields(inputs.toolchain_rule) != EMBEDDED_PROVIDER_FIELDS:
        errors.append(
            "EmbeddedToolchainInfo fields must match the exact contract")

    for field_name in EXECUTABLE_LABELS:
        attr_pattern = re.compile(
            rf'"{field_name}"\s*:\s*attr\.label\((?=[^)]*executable\s*=\s*True)(?=[^)]*cfg\s*=\s*"exec")[^)]*\)',
            re.DOTALL,
        )
        if attr_pattern.search(inputs.toolchain_rule) is None:
            errors.append(
                f"{field_name} must be an executable exec-configured label")
        if f"ctx.attr.{field_name}[FilesToRunProvider]" not in inputs.toolchain_rule:
            errors.append(f"{field_name} must export its FilesToRunProvider")

    for field_name, label in EXECUTABLE_LABELS.items():
        if f'{field_name} = "{label}"' not in inputs.toolchain_build:
            errors.append(f"{field_name} must use declared label {label}")

    for fragment in VERSION_FRAGMENTS:
        if fragment not in inputs.toolchain_rule:
            errors.append(f"missing locked identity {fragment}")
    if 'target_triple = "thumbv7em-none-eabihf"' not in inputs.toolchain_rule:
        errors.append("missing hard-float target triple")

    linux_registration = _named_call(
        inputs.toolchain_build,
        "toolchain",
        "phase42_qualification_linux_x86_64_toolchain",
    )
    required_linux_fragments = (
        "target_compatible_with = PHASE42_MINI_CONSTRAINTS",
        '"@platforms//os:linux"',
        '"@platforms//cpu:x86_64"',
        'toolchain_type = ":phase42_qualification_toolchain_type"',
    )
    for fragment in required_linux_fragments:
        if fragment not in linux_registration:
            errors.append(f"Linux registration is missing {fragment}")

    module_fragments = (
        '"rust_linux_x86_64_thumbv7em_none_eabihf_tools"',
        '"//tools/bazel/toolchains:phase42_qualification_linux_x86_64_toolchain"',
        '"//tools/bazel/toolchains:phase42_qualification_darwin_x86_64_toolchain"',
        '"//tools/bazel/toolchains:phase42_qualification_darwin_arm64_toolchain"',
    )
    for fragment in module_fragments:
        if fragment not in inputs.module:
            errors.append(f"MODULE.bazel is missing registration {fragment}")

    forbidden_source = f"{inputs.platform_contract}\n{inputs.toolchain_rule}\n{inputs.toolchain_build}"
    for forbidden in (
            "soft_float",
            "thumbv7em_none_eabi\"",
            ".dependencies",
            "reference_toolchain(",
    ):
        if forbidden in forbidden_source:
            errors.append(f"forbidden qualification dependency {forbidden}")
    if "EmbeddedToolchainInfo" in inputs.reference_rule:
        errors.append(
            "reference provider must not export EmbeddedToolchainInfo")

    return errors


class EmbeddedToolchainContractTest(unittest.TestCase):

    def setUp(self) -> None:
        self.inputs = _load_inputs()

    def test_committed_platform_and_toolchain_match_exact_contract(
            self) -> None:
        # Arrange
        inputs = self.inputs

        # Act
        errors = validate_embedded_contract(inputs)

        # Assert
        self.assertEqual(errors, [])

    def test_partial_or_broadened_target_tuple_is_rejected(self) -> None:
        for mutation in (
                self.inputs.platform_contract.replace(
                    '    "//platforms:printer_mini",\n', "", 1),
                self.inputs.platform_contract.replace(
                    "]", '    "//platforms:printer_mk4",\n]', 1),
        ):
            with self.subTest(mutation=mutation):
                # Arrange
                mutated = replace(self.inputs, platform_contract=mutation)

                # Act
                errors = validate_embedded_contract(mutated)

                # Assert
                self.assertTrue(errors)

    def test_missing_or_replaced_executable_is_rejected(self) -> None:
        for field_name, label in EXECUTABLE_LABELS.items():
            with self.subTest(field_name=field_name):
                # Arrange
                mutated = replace(
                    self.inputs,
                    toolchain_build=self.inputs.toolchain_build.replace(
                        f'{field_name} = "{label}"',
                        f'{field_name} = "//tools/bazel:{field_name}"',
                        1,
                    ),
                )

                # Act
                errors = validate_embedded_contract(mutated)

                # Assert
                self.assertTrue(errors)

    def test_each_locked_identity_mutation_is_rejected(self) -> None:
        for exact_value in ("1.85.0", "13.2.Rel1", "3.12.10", "0.9.10",
                            "thumbv7em-none-eabihf"):
            with self.subTest(exact_value=exact_value):
                # Arrange
                mutated = replace(
                    self.inputs,
                    toolchain_rule=self.inputs.toolchain_rule.replace(
                        exact_value, "mutated-version"),
                )

                # Act
                errors = validate_embedded_contract(mutated)

                # Assert
                self.assertTrue(errors)

    def test_reference_provider_connection_is_rejected(self) -> None:
        # Arrange
        mutated = replace(
            self.inputs,
            reference_rule=(f"{self.inputs.reference_rule}\n"
                            "EmbeddedToolchainInfo = provider()\n"),
        )

        # Act
        errors = validate_embedded_contract(mutated)

        # Assert
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
