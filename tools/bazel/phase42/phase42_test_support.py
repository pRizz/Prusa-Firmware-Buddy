import os
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self) -> str:
        return f"{self.stdout}\n{self.stderr}"


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run_command(
    command: Sequence[str],
    *,
    cwd: Path,
    environment: Mapping[str, str] | None = None,
) -> CommandResult:
    process_environment = os.environ.copy()
    if environment is not None:
        process_environment.update(environment)
    completed = subprocess.run(
        list(command),
        capture_output=True,
        check=False,
        cwd=cwd,
        env=process_environment,
        text=True,
    )
    return CommandResult(
        command=tuple(command),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def bazel_command(
    output_base: Path,
    action: str,
    target: str,
    *options: str,
) -> tuple[str, ...]:
    return (
        "bazel",
        f"--output_base={output_base}",
        "--max_idle_secs=5",
        action,
        target,
        *options,
    )
