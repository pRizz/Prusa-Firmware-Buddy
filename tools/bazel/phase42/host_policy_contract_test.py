import re
import unittest
from dataclasses import dataclass, replace
from pathlib import Path

HOST_POLICY_FIELDS = (
    "detected_os",
    "detected_arch",
    "qualifies",
    "diagnostic",
)
DARWIN_DIAGNOSTICS = {
    "x86_64":
    ("unsupported embedded qualification host: detected Darwin-x86_64; "
     "use canonical Linux x86_64 CI/container"),
    "arm64":
    ("unsupported embedded qualification host: detected Darwin-arm64; "
     "use canonical Linux x86_64 CI/container"),
}


@dataclass(frozen=True)
class HostPolicyInputs:
    host_policy: str
    toolchain_rule: str
    toolchain_build: str


def _workspace_file(relative_path: str) -> Path:
    return Path(__file__).resolve().parents[3] / relative_path


def _read(relative_path: str) -> str:
    return _workspace_file(relative_path).read_text(encoding="utf-8")


def _load_inputs() -> HostPolicyInputs:
    return HostPolicyInputs(
        host_policy=_read("tools/bazel/phase42/host_policy.bzl"),
        toolchain_rule=_read("tools/bazel/toolchains/embedded_toolchain.bzl"),
        toolchain_build=_read("tools/bazel/toolchains/BUILD.bazel"),
    )


def _provider_fields(source: str) -> tuple[str, ...]:
    maybe_match = re.search(
        r"HostPolicyInfo\s*=\s*provider\(\s*fields\s*=\s*\{(.*?)\}\s*,?\s*\)",
        source,
        re.DOTALL,
    )
    if maybe_match is None:
        return ()
    return tuple(
        re.findall(r'^\s*"([^"]+)"\s*:', maybe_match.group(1), re.MULTILINE))


def _function_block(source: str, name: str) -> str:
    maybe_match = re.search(
        rf"def {re.escape(name)}\([^)]*\):(.*?)(?=\ndef |\Z)", source,
        re.DOTALL)
    return maybe_match.group(0) if maybe_match is not None else ""


def validate_host_policy(inputs: HostPolicyInputs) -> list[str]:
    errors: list[str] = []
    if _provider_fields(inputs.host_policy) != HOST_POLICY_FIELDS:
        errors.append("HostPolicyInfo fields must match the exact contract")
    if "EmbeddedToolchainInfo" in inputs.host_policy:
        errors.append("host policy must not define or export embedded tools")

    linux_policy = _function_block(inputs.host_policy,
                                   "linux_x86_64_host_policy")
    for fragment in (
            'detected_os = "linux"',
            'detected_arch = "x86_64"',
            "qualifies = True",
    ):
        if fragment not in linux_policy:
            errors.append(f"Linux host policy is missing {fragment}")

    darwin_policy = _function_block(inputs.host_policy, "darwin_host_policy")
    for arch, diagnostic in DARWIN_DIAGNOSTICS.items():
        if f'"{arch}": "{diagnostic}"' not in inputs.host_policy:
            errors.append(f"Darwin {arch} diagnostic must be exact")
    for fragment in (
            'detected_os = "darwin"',
            "detected_arch = arch",
            "qualifies = False",
    ):
        if fragment not in darwin_policy:
            errors.append(f"Darwin host policy is missing {fragment}")

    consumer = _function_block(inputs.host_policy,
                               "require_embedded_toolchain")
    host_index = consumer.find("toolchain.host_policy")
    fail_index = consumer.find("fail(host_policy.diagnostic)")
    embedded_index = consumer.find("toolchain.embedded")
    if min(host_index, fail_index, embedded_index) < 0:
        errors.append(
            "consumer must inspect host policy, fail, then access tools")
    elif not host_index < fail_index < embedded_index:
        errors.append("consumer accesses embedded tools before host rejection")

    darwin_impl = _function_block(inputs.toolchain_rule,
                                  "_darwin_qualification_toolchain_impl")
    if "darwin_host_policy(ctx.attr.arch)" not in darwin_impl:
        errors.append("Darwin implementation must return detected host policy")
    if "EmbeddedToolchainInfo" in darwin_impl or "ctx.actions" in darwin_impl:
        errors.append("Darwin implementation must export no tools or actions")
    if "platform_common.ToolchainInfo(host_policy = host_policy)" not in darwin_impl:
        errors.append("Darwin toolchain must expose only host policy")

    for arch, cpu in (("x86_64", "x86_64"), ("arm64", "aarch64")):
        target_name = f"phase42_qualification_darwin_{arch}_toolchain"
        maybe_target = re.search(
            rf"toolchain\(\s*name\s*=\s*\"{target_name}\"(.*?)\n\)",
            inputs.toolchain_build,
            re.DOTALL,
        )
        target = maybe_target.group(0) if maybe_target is not None else ""
        for fragment in (
                '"@platforms//os:osx"',
                f'"@platforms//cpu:{cpu}"',
                "target_compatible_with = PHASE42_MINI_CONSTRAINTS",
        ):
            if fragment not in target:
                errors.append(
                    f"Darwin {arch} registration is missing {fragment}")
        if any(label in target
               for label in ("arm_gnu", "mini404", "rustc", "python3")):
            errors.append(f"Darwin {arch} registration reaches executables")

    return errors


class HostPolicyContractTest(unittest.TestCase):

    def setUp(self) -> None:
        self.inputs = _load_inputs()

    def test_committed_host_policies_match_exact_contract(self) -> None:
        # Arrange
        inputs = self.inputs

        # Act
        errors = validate_host_policy(inputs)

        # Assert
        self.assertEqual(errors, [])

    def test_darwin_diagnostic_mutation_is_rejected(self) -> None:
        for diagnostic in DARWIN_DIAGNOSTICS.values():
            with self.subTest(diagnostic=diagnostic):
                # Arrange
                mutated = replace(
                    self.inputs,
                    host_policy=self.inputs.host_policy.replace(
                        diagnostic, "unsupported host"),
                )

                # Act
                errors = validate_host_policy(mutated)

                # Assert
                self.assertTrue(errors)

    def test_darwin_embedded_provider_or_action_is_rejected(self) -> None:
        for mutation in ("EmbeddedToolchainInfo()", "ctx.actions.run()"):
            with self.subTest(mutation=mutation):
                # Arrange
                marker = "def _darwin_qualification_toolchain_impl(ctx):"
                mutated_rule = self.inputs.toolchain_rule.replace(
                    marker, f"{marker}\n    {mutation}", 1)
                mutated = replace(self.inputs, toolchain_rule=mutated_rule)

                # Act
                errors = validate_host_policy(mutated)

                # Assert
                self.assertTrue(errors)

    def test_consumer_access_before_host_rejection_is_rejected(self) -> None:
        # Arrange
        mutated_policy = self.inputs.host_policy.replace(
            "    host_policy = toolchain.host_policy",
            "    embedded = toolchain.embedded\n    host_policy = toolchain.host_policy",
            1,
        ).replace("    return toolchain.embedded", "    return embedded", 1)
        mutated = replace(self.inputs, host_policy=mutated_policy)

        # Act
        errors = validate_host_policy(mutated)

        # Assert
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
