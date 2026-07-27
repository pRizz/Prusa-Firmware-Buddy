from __future__ import annotations

from pathlib import Path

from phase31_intake_policy import *


def require_file_contains(root: Path, path: Path,
                          needles: list[str]) -> list[str]:
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    return [
        f"{path.as_posix()} missing required wiring text: {needle}"
        for needle in needles if needle not in text
    ]


def shell_case_commands(text: str, case_name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{case_name})":
            continue
        commands: list[str] = []
        for body_line in lines[index + 1:]:
            stripped = body_line.strip()
            if stripped == ";;":
                return commands
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
        return None
    return None


def just_recipe_commands(text: str, recipe_name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{recipe_name}:":
            continue
        commands: list[str] = []
        for body_line in lines[index + 1:]:
            if body_line and not body_line[0].isspace():
                break
            stripped = body_line.strip()
            if stripped and not stripped.startswith("#"):
                commands.append(stripped)
        return commands
    return None


def missing_required_items(location: str, actual: list[str],
                           expected: list[str]) -> list[str]:
    actual_values = set(actual)
    return [
        f"{location} missing required wiring item: {item}" for item in expected
        if item not in actual_values
    ]


def check_command_order(location: str, commands: list[str], first: str,
                        second: str, message: str) -> list[str]:
    if first not in commands or second not in commands:
        return []
    if commands.index(first) <= commands.index(second):
        return []
    return [f"{location} {message}"]


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    tools_manifest_refs = [
        Path(manifest).relative_to("tools/bazel").as_posix()
        for manifest in [*SOURCE_CONTRACTS,
                         CONTRACT_MANIFEST.as_posix()]
    ]
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase31_final_evidence_intake_docs"',
                'name = "phase31_verify"',
                'actual = "//tools/bazel:phase31_verify"',
                'name = "phase31_verify_tests"',
                'actual = "//tools/bazel:phase31_verify_tests"',
                *[f'"{doc}"' for doc in PHASE31_DOCS],
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase31_source_ref_manifests"',
                'name = "phase31_verify"',
                'name = "phase31_verify_tests"',
                "phase31_final_evidence_intake.py",
                "phase31_final_evidence_intake_test.py",
                "phase31_final_evidence_intake_contract.json",
                "//:phase31_final_evidence_intake_docs",
                *[f'"{manifest}"' for manifest in tools_manifest_refs],
            ],
        ))
    try:
        workflow_text = read_text(root, Path("tools/bazel/rust_workflow.sh"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        verify_commands = shell_case_commands(workflow_text, "phase31_verify")
        test_commands = shell_case_commands(workflow_text,
                                            "phase31_verify_tests")
        if verify_commands is None:
            errors.append(
                "tools/bazel/rust_workflow.sh phase31_verify case arm missing")
        else:
            errors.extend(
                missing_required_items(
                    "tools/bazel/rust_workflow.sh phase31_verify case arm",
                    verify_commands, PHASE31_VERIFY_COMMANDS))
            errors.extend(
                check_command_order(
                    "tools/bazel/rust_workflow.sh phase31_verify case arm",
                    verify_commands,
                    PHASE31_VERIFY_COMMANDS[0],
                    PHASE31_VERIFY_COMMANDS[1],
                    "must run --wiring-only before --quick",
                ))
        if test_commands is None:
            errors.append(
                "tools/bazel/rust_workflow.sh phase31_verify_tests case arm missing"
            )
        else:
            errors.extend(
                missing_required_items(
                    "tools/bazel/rust_workflow.sh phase31_verify_tests case arm",
                    test_commands, [PHASE31_TEST_COMMAND]))
    try:
        just_text = read_text(root, Path("justfile"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        just_commands = just_recipe_commands(just_text, "phase31-verify")
        test_line = "bazel run //tools/bazel:phase31_verify_tests"
        verify_line = "bazel run //tools/bazel:phase31_verify"
        if just_commands is None:
            errors.append("justfile phase31-verify recipe missing")
        else:
            errors.extend(
                missing_required_items("justfile phase31-verify recipe",
                                       just_commands,
                                       [test_line, verify_line]))
            errors.extend(
                check_command_order(
                    "justfile phase31-verify recipe",
                    just_commands,
                    test_line,
                    verify_line,
                    "must run tests before verifier",
                ))
    if errors:
        raise VerificationError("\n".join(errors))
