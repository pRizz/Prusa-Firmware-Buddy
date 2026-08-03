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


@dataclass(frozen=True)
class SmokeInputs:
    build: str
    rule: str
    rust: str
    linker: str
    host_policy: str


def _workspace_file(relative_path: str) -> Path:
    return Path(__file__).resolve().parents[3] / relative_path


def _read_or_empty(relative_path: str) -> str:
    candidate = _workspace_file(relative_path)
    if not candidate.is_file():
        return ""
    return candidate.read_text(encoding="utf-8")


def _load_inputs() -> SmokeInputs:
    return SmokeInputs(
        build=_read_or_empty("tools/bazel/phase42/BUILD.bazel"),
        rule=_read_or_empty("tools/bazel/phase42/arm_link_smoke.bzl"),
        rust=_read_or_empty("tools/bazel/phase42/arm_link_smoke.rs"),
        linker=_read_or_empty("tools/bazel/phase42/arm_link_smoke.ld"),
        host_policy=_read_or_empty("tools/bazel/phase42/host_policy.bzl"),
    )


def _require_fragments(source: str, fragments: tuple[str, ...],
                       context: str, errors: list[str]) -> None:
    for fragment in fragments:
        if fragment not in source:
            errors.append(f"{context} is missing {fragment}")


def validate_smoke_contract(inputs: SmokeInputs) -> list[str]:
    errors: list[str] = []
    _require_fragments(
        inputs.rust,
        (
            "#![no_std]",
            "#![no_main]",
            "#[unsafe(no_mangle)]",
            'extern "C" fn _phase42_smoke_entry() -> !',
            "#[panic_handler]",
            "core::hint::spin_loop()",
        ),
        "Rust smoke",
        errors,
    )
    _require_fragments(
        inputs.linker,
        (
            "ENTRY(_phase42_smoke_entry)",
            "MEMORY",
            "FLASH (rx)",
            "RAM (rwx)",
            "KEEP(*(.text._phase42_smoke_entry))",
        ),
        "linker contract",
        errors,
    )
    _require_fragments(
        inputs.rule,
        (
            'load("//tools/bazel/phase42:host_policy.bzl",',
            '"PHASE42_QUALIFICATION_TOOLCHAIN_TYPE"',
            '"require_embedded_toolchain"',
            "embedded = require_embedded_toolchain(ctx)",
            'ctx.actions.declare_file(ctx.label.name + ".elf")',
            'ctx.actions.declare_file(ctx.label.name + ".map")',
            'ctx.actions.declare_file(ctx.label.name + ".report.json")',
            '"--target=thumbv7em-none-eabihf"',
            '"--emit=obj=" + object_file.path',
            '"-Cpanic=abort"',
            '"-Copt-level=s"',
            '"-nostdlib"',
            '"-mthumb"',
            '"-mcpu=cortex-m4"',
            '"-mfloat-abi=hard"',
            '"-mfpu=fpv4-sp-d16"',
            '"-Wl,--gc-sections"',
            '"-Wl,-Map," + map_file.path',
            'mnemonic = "Phase42RustCompile"',
            'mnemonic = "Phase42ArmLink"',
            'mnemonic = "Phase42ArmReadelf"',
            'mnemonic = "Phase42ArmObjdump"',
            'mnemonic = "Phase42ArmNm"',
            'mnemonic = "Phase42ArmSize"',
            'mnemonic = "Phase42SmokeReport"',
            "embedded.arm_readelf",
            "embedded.arm_objdump",
            "embedded.arm_nm",
            "embedded.arm_size",
            "embedded.arm_toolchain_files",
            '"phase42-arm-link-smoke"',
            '"Rust 1.85.0"',
            '"Arm GNU 13.2.Rel1"',
            '"//platforms:mini_buddy_stm32f407vg"',
            'toolchains = [PHASE42_QUALIFICATION_TOOLCHAIN_TYPE]',
        ),
        "smoke rule",
        errors,
    )
    _require_fragments(
        inputs.build,
        (
            'load(":arm_link_smoke.bzl", "arm_link_smoke")',
            'name = "arm_link_smoke"',
            'src = "arm_link_smoke.rs"',
            'linker_script = "arm_link_smoke.ld"',
            "target_compatible_with = PHASE42_MINI_CONSTRAINTS",
            'name = "arm_link_smoke_tests"',
            'python_version = "PY3"',
        ),
        "BUILD target",
        errors,
    )
    _require_fragments(
        inputs.host_policy,
        (
            "host_policy = toolchain.host_policy",
            "fail(host_policy.diagnostic)",
            "return toolchain.embedded",
            "canonical Linux x86_64 CI/container",
        ),
        "host policy",
        errors,
    )

    rule_and_build = f"{inputs.rule}\n{inputs.build}".lower()
    for forbidden in (
            "cargo ",
            "cmake",
            ".dependencies",
            "fixture",
            "archive",
            "reference_contract",
            "ctx.actions.symlink",
    ):
        if forbidden in rule_and_build:
            errors.append(f"smoke graph contains forbidden provenance {forbidden}")

    for constraint in CANONICAL_CONSTRAINTS:
        if constraint not in _read_or_empty(
                "tools/bazel/phase42/platform_contract.bzl"):
            errors.append(f"canonical constraint is missing {constraint}")
    return errors


class ArmLinkSmokeContractTest(unittest.TestCase):

    def setUp(self) -> None:
        self.inputs = _load_inputs()

    def test_committed_smoke_matches_output_and_provenance_contract(
            self) -> None:
        # Arrange
        inputs = self.inputs

        # Act
        errors = validate_smoke_contract(inputs)

        # Assert
        self.assertEqual(errors, [])

    def test_missing_target_or_abi_flag_is_rejected(self) -> None:
        for fragment in (
                '"--target=thumbv7em-none-eabihf"',
                '"-mcpu=cortex-m4"',
                '"-mfloat-abi=hard"',
                '"-mfpu=fpv4-sp-d16"',
        ):
            with self.subTest(fragment=fragment):
                # Arrange
                mutated = replace(
                    self.inputs,
                    rule=self.inputs.rule.replace(fragment, "", 1),
                )

                # Act
                errors = validate_smoke_contract(mutated)

                # Assert
                self.assertTrue(errors)

    def test_missing_entry_symbol_is_rejected(self) -> None:
        # Arrange
        mutated = replace(
            self.inputs,
            rust=self.inputs.rust.replace("_phase42_smoke_entry", "entry", 1),
        )

        # Act
        errors = validate_smoke_contract(mutated)

        # Assert
        self.assertTrue(errors)

    def test_copy_or_reference_producer_is_rejected(self) -> None:
        for mutation in ("ctx.actions.symlink", "reference_contract"):
            with self.subTest(mutation=mutation):
                # Arrange
                mutated = replace(self.inputs,
                                  rule=f"{self.inputs.rule}\n{mutation}")

                # Act
                errors = validate_smoke_contract(mutated)

                # Assert
                self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
