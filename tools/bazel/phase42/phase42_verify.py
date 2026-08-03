import argparse
import hashlib
import json
import platform
import shlex
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import NamedTuple

from phase42_test_support import CommandResult, run_command, workspace_root


SMOKE_TARGET = "//tools/bazel/phase42:arm_link_smoke"
MINI_OPTIONS = ("--config=mini", "--noskip_incompatible_explicit_targets")
LOCK_OPTION = "--lockfile_mode=error"
LINUX_REMEDY = "canonical Linux x86_64 CI/container"
EXPECTED_OUTPUTS = (
    "arm_link_smoke.elf",
    "arm_link_smoke.map",
    "arm_link_smoke.report.json",
)
EXPECTED_IDENTITIES = (
    "Bazel 9.2.0",
    "Rust 1.85.0",
    "Arm GNU 13.2.Rel1",
    "Python 3.12.10",
    "Mini404 0.9.10",
    "thumbv7em-none-eabihf",
)
LINUX_STEPS = (
    (
        "toolchain resolution",
        (
            "bazel",
            "test",
            "//tools/bazel/phase42:toolchain_provenance_tests",
            "//tools/bazel/phase42:embedded_toolchain_contract_tests",
            "//tools/bazel/phase42:host_policy_contract_tests",
            "//tools/bazel/phase42:arm_link_smoke_tests",
            LOCK_OPTION,
        ),
    ),
    (
        "initial Arm link smoke",
        ("bazel", "build", SMOKE_TARGET, *MINI_OPTIONS, LOCK_OPTION),
    ),
    (
        "platform negatives and graph isolation",
        (
            "bazel",
            "test",
            "//tools/bazel/phase42:platform_rejection_tests",
            "//tools/bazel/phase42:graph_isolation_tests",
            LOCK_OPTION,
        ),
    ),
    (
        "authority facade contract",
        ("bazel", "test", "//tools/bazel/phase42:facade_contract_tests", LOCK_OPTION),
    ),
    (
        "reference separation contract",
        ("bazel", "test", "//tools/bazel/phase42:reference_separation_tests", LOCK_OPTION),
    ),
    (
        "aggregate contract",
        ("bazel", "test", "//tools/bazel/phase42:phase42_verify_contract_tests", LOCK_OPTION),
    ),
    (
        "final Arm link smoke",
        ("bazel", "build", SMOKE_TARGET, *MINI_OPTIONS, LOCK_OPTION),
    ),
)


class Host(NamedTuple):
    system: str
    machine: str


class VerificationResult(NamedTuple):
    returncode: int
    output: str


Runner = Callable[..., CommandResult]


def _normalize_host(system: str, machine: str) -> Host:
    normalized_machine = machine
    if system == "Darwin" and machine == "aarch64":
        normalized_machine = "arm64"
    if system == "Linux" and machine == "amd64":
        normalized_machine = "x86_64"
    return Host(system, normalized_machine)


def _unsupported_host_message(host: Host) -> str:
    return (
        f"unsupported embedded qualification host: detected {host.system}-{host.machine}; "
        f"use {LINUX_REMEDY}; no positive evidence is possible here; "
        "run canonical Linux x86_64 CI/container: just phase42-verify"
    )


def _darwin_rejection_commands() -> tuple[tuple[str, ...], ...]:
    direct_targets = (
        ("build", "//tools/bazel/phase42:arm_link_smoke"),
        ("build", "//tools/bazel:build_firmware"),
        ("build", "//tools/bazel:test_firmware"),
        ("build", "//tools/bazel:release_package"),
        ("build", "//tools/bazel:simulator_parity"),
    )
    direct = tuple(
        ("bazel", action, target, *MINI_OPTIONS, LOCK_OPTION)
        for action, target in direct_targets
    )
    recipes = tuple(
        ("just", recipe)
        for recipe in ("build", "test", "release-package", "simulator-parity")
    )
    aggregate = (("bazel", "run", "//tools/bazel/phase42:phase42_verify", LOCK_OPTION),)
    return (*direct, *recipes, *aggregate)


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_linux(runner: Runner, root: Path) -> VerificationResult:
    lines: list[str] = []
    if sys.version_info[:3] != (3, 12, 10):
        return VerificationResult(1, f"rules_python interpreter mismatch: {sys.version}")
    interpreter = Path(sys.executable).as_posix()
    if interpreter.startswith(("/usr/bin/", "/usr/local/bin/", "/opt/homebrew/")):
        return VerificationResult(1, f"ambient Python is forbidden: {interpreter}")

    lock_path = root / "MODULE.bazel.lock"
    initial_lock_hash = _hash_file(lock_path)
    lines.append(f"rules_python interpreter: {interpreter}")
    lines.append(f"MODULE.bazel.lock sha256: {initial_lock_hash}")

    for step, command in LINUX_STEPS:
        result = runner(command, cwd=root)
        if result.returncode != 0:
            return VerificationResult(
                result.returncode,
                "\n".join((*lines, f"FAILED {step}: {shlex.join(command)}", result.output)),
            )
        lines.append(f"PASS {step}: {shlex.join(command)}")

    output_query = (
        "bazel",
        "cquery",
        SMOKE_TARGET,
        *MINI_OPTIONS,
        LOCK_OPTION,
        "--output=files",
    )
    output_result = runner(output_query, cwd=root)
    if output_result.returncode != 0:
        return VerificationResult(output_result.returncode, output_result.output)

    resolved_outputs: dict[str, Path] = {}
    for line in output_result.stdout.splitlines():
        candidate = Path(line.strip())
        for expected in EXPECTED_OUTPUTS:
            if candidate.name == expected:
                resolved_outputs[expected] = candidate if candidate.is_absolute() else root / candidate
    missing = [name for name in EXPECTED_OUTPUTS if name not in resolved_outputs]
    if missing:
        return VerificationResult(1, f"smoke cquery omitted outputs: {', '.join(missing)}")
    for name, output_path in resolved_outputs.items():
        if not output_path.is_file() or output_path.stat().st_size == 0:
            return VerificationResult(1, f"missing genuine smoke output {name}: {output_path}")

    report_path = resolved_outputs["arm_link_smoke.report.json"]
    report = json.loads(report_path.read_text(encoding="utf-8"))
    required_report = {
        "arm_gnu": "Arm GNU 13.2.Rel1",
        "platform": "//platforms:mini_buddy_stm32f407vg",
        "rust": "Rust 1.85.0",
        "target_triple": "thumbv7em-none-eabihf",
    }
    for field, expected in required_report.items():
        if report.get(field) != expected:
            return VerificationResult(1, f"smoke report {field} mismatch: {report.get(field)!r}")

    final_lock_hash = _hash_file(lock_path)
    if final_lock_hash != initial_lock_hash:
        return VerificationResult(1, "MODULE.bazel.lock changed during qualification")

    bazel_version = (root / ".bazelversion").read_text(encoding="utf-8").strip()
    identities = (
        f"Bazel {bazel_version}",
        report["rust"],
        report["arm_gnu"],
        f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "Mini404 0.9.10",
        report["target_triple"],
    )
    if identities != EXPECTED_IDENTITIES:
        return VerificationResult(1, f"tool identity mismatch: {identities!r}")
    lines.extend(f"identity: {identity}" for identity in identities)
    lines.extend(f"output: {name}={path}" for name, path in resolved_outputs.items())
    lines.append(f"MODULE.bazel.lock stable sha256: {final_lock_hash}")
    lines.append("Phase 42 canonical Linux x86_64 qualification PASSED")
    return VerificationResult(0, "\n".join(lines))


def _run_darwin_host_check(host: Host, runner: Runner, root: Path) -> VerificationResult:
    expected = (
        f"unsupported embedded qualification host: detected Darwin-{host.machine}; "
        f"use {LINUX_REMEDY}"
    )
    lines: list[str] = []
    for command in _darwin_rejection_commands():
        result = runner(command, cwd=root)
        if result.returncode == 0:
            return VerificationResult(1, f"Darwin route unexpectedly passed: {shlex.join(command)}")
        if expected not in result.output:
            return VerificationResult(
                1,
                f"Darwin route omitted HostPolicyInfo diagnostic: {shlex.join(command)}\n{result.output}",
            )
        lines.append(f"PASS rejected: {shlex.join(command)}")
    lines.append(f"Phase 42 Darwin host-check PASSED for detected Darwin-{host.machine}")
    return VerificationResult(0, "\n".join(lines))


def verify(
    *,
    mode: str,
    system: str,
    machine: str,
    runner: Runner = run_command,
    maybe_root: Path | None = None,
) -> VerificationResult:
    host = _normalize_host(system, machine)
    verification_root = maybe_root if maybe_root is not None else workspace_root()
    if mode == "host-check":
        if host.system != "Darwin":
            return VerificationResult(1, f"host-check requires Darwin, detected {host.system}-{host.machine}")
        return _run_darwin_host_check(host, runner, verification_root)
    if host != Host("Linux", "x86_64"):
        return VerificationResult(1, _unsupported_host_message(host))
    return _run_linux(runner, verification_root)


def main(maybe_argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 42 embedded toolchain qualification")
    parser.add_argument("--host-check", action="store_true")
    arguments = parser.parse_args(maybe_argv)
    result = verify(
        mode="host-check" if arguments.host_check else "aggregate",
        system=platform.system(),
        machine=platform.machine(),
    )
    stream = sys.stdout if result.returncode == 0 else sys.stderr
    print(result.output, file=stream)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
