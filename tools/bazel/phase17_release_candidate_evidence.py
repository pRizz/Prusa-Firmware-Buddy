#!/usr/bin/env python3
from __future__ import annotations

from phase17_evidence_artifacts import *


def iter_security_files(root: Path, output_dir: Path) -> list[Path]:
    relative_output_dir = require_repo_relative_under(output_dir,
                                                      DEFAULT_OUTPUT_DIR,
                                                      "--output-dir")
    full_output_dir = contained_output_dir(root, relative_output_dir)
    files = [CONTRACT_MANIFEST]
    if full_output_dir.exists():
        files.extend(
            sorted(
                path.relative_to(root) for path in full_output_dir.rglob("*")
                if path.is_file()))
    return files


def check_security(root: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    errors: list[str] = []
    check_contract(root)
    for relative_path in iter_security_files(root, output_dir):
        try:
            reject_forbidden_text(relative_path,
                                  read_text(root, relative_path))
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def iter_bazel_call_blocks(text: str, call_name: str) -> list[str]:
    blocks: list[str] = []
    for match in re.finditer(rf"(?m)^\s*{re.escape(call_name)}\(", text):
        depth = 0
        in_comment = False
        maybe_string_quote: str | None = None
        escaped = False
        for index in range(match.start(), len(text)):
            char = text[index]
            if in_comment:
                if char == "\n":
                    in_comment = False
                continue
            if maybe_string_quote is not None:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == maybe_string_quote:
                    maybe_string_quote = None
                continue
            if char == "#":
                in_comment = True
                continue
            if char in {'"', "'"}:
                maybe_string_quote = char
                continue
            if char == "(":
                depth += 1
                continue
            if char != ")":
                continue
            depth -= 1
            if depth == 0:
                blocks.append(text[match.start():index + 1])
                break
    return blocks


def bazel_string_attr(block: str, attr: str) -> str | None:
    match = re.search(rf'(?m)^\s*{re.escape(attr)}\s*=\s*"([^"]*)"', block)
    if match is None:
        return None
    return match.group(1)


def bazel_list_attr(block: str, attr: str) -> list[str]:
    match = re.search(rf"(?ms)^\s*{re.escape(attr)}\s*=\s*\[(.*?)\]", block)
    if match is None:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


def bazel_rule_block(text: str, rule_kind: str, name: str) -> str | None:
    for block in iter_bazel_call_blocks(text, rule_kind):
        if bazel_string_attr(block, "name") == name:
            return block
    return None


def missing_required_items(location: str, actual: list[str],
                           expected: list[str]) -> list[str]:
    actual_values = set(actual)
    return [
        f"{location} missing required wiring item: {item}" for item in expected
        if item not in actual_values
    ]


def check_bazel_list_attr(block: str | None, location: str, attr: str,
                          expected: list[str]) -> list[str]:
    if block is None:
        return [f"{location} missing required Bazel rule"]
    return missing_required_items(f"{location} {attr}",
                                  bazel_list_attr(block, attr), expected)


def check_bazel_string_attr(block: str | None, location: str, attr: str,
                            expected: str) -> list[str]:
    if block is None:
        return [f"{location} missing required Bazel rule"]
    actual = bazel_string_attr(block, attr)
    if actual == expected:
        return []
    return [f"{location} {attr} must be {expected!r}, not {actual!r}"]


def check_release_candidate_artifact_target(text: str) -> list[str]:
    block = bazel_rule_block(text, "filegroup",
                             "phase17_release_candidate_artifacts")
    if block is None:
        return [
            "tools/bazel/BUILD.bazel missing phase17_release_candidate_artifacts filegroup"
        ]
    srcs = set(bazel_list_attr(block, "srcs"))
    expected_release_identity_srcs = {
        ":phase20_release_environment_input_manifest"
    }
    forbidden_smoke_deps = {
        ":phase17_representative_release_smoke",
        ":representative_release_artifacts",
        "//tools/bazel:phase17_representative_release_smoke",
        "//tools/bazel:representative_release_artifacts",
        "//tools/bazel:phase3_verify",
    }
    errors: list[str] = []
    wrapped_smoke = sorted(srcs & forbidden_smoke_deps)
    if wrapped_smoke:
        errors.append(
            "tools/bazel/BUILD.bazel phase17_release_candidate_artifacts cannot wrap local smoke dependencies: "
            + ", ".join(wrapped_smoke))
    if srcs != expected_release_identity_srcs:
        actual = ", ".join(sorted(srcs)) if srcs else "<empty>"
        errors.append(
            "tools/bazel/BUILD.bazel phase17_release_candidate_artifacts must use "
            ":phase20_release_environment_input_manifest, not " + actual)
    return errors


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
        return commands
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


def check_command_order(location: str, commands: list[str], first: str,
                        second: str) -> list[str]:
    if first not in commands or second not in commands:
        return []
    if commands.index(first) <= commands.index(second):
        return []
    return [f"{location} must run tests before verifier"]


def check_tools_build_wiring(root: Path,
                             manifest_srcs: list[str]) -> list[str]:
    path = Path("tools/bazel/BUILD.bazel")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors = check_release_candidate_artifact_target(text)
    smoke_block = bazel_rule_block(text, "filegroup",
                                   "phase17_representative_release_smoke")
    source_ref_block = bazel_rule_block(text, "filegroup",
                                        "phase17_source_ref_manifests")
    verify_block = bazel_rule_block(text, "shell_binary", "phase17_verify")
    verify_tests_block = bazel_rule_block(text, "shell_binary",
                                          "phase17_verify_tests")
    errors.extend(
        check_bazel_list_attr(
            smoke_block,
            "tools/bazel/BUILD.bazel filegroup phase17_representative_release_smoke",
            "srcs",
            [":representative_release_artifacts"],
        ))
    errors.extend(
        check_bazel_list_attr(
            source_ref_block,
            "tools/bazel/BUILD.bazel filegroup phase17_source_ref_manifests",
            "srcs",
            manifest_srcs,
        ))
    errors.extend(
        check_bazel_list_attr(
            verify_block,
            "tools/bazel/BUILD.bazel shell_binary phase17_verify",
            "data",
            [
                "phase17_release_candidate_evidence.py",
                "manifests/phase17_release_candidate_evidence_contract.json",
                ":phase17_release_candidate_artifacts",
                ":phase17_representative_release_smoke",
                ":phase17_source_ref_manifests",
                "//:phase17_release_candidate_evidence_docs",
                "//:phase11_cutover_evidence_docs",
            ],
        ))
    errors.extend(
        check_bazel_list_attr(
            verify_tests_block,
            "tools/bazel/BUILD.bazel shell_binary phase17_verify_tests",
            "data",
            [
                "phase17_release_candidate_evidence.py",
                "phase17_release_candidate_evidence_test.py",
                "manifests/phase17_release_candidate_evidence_contract.json",
                ":phase17_release_candidate_artifacts",
                ":phase17_representative_release_smoke",
                ":phase17_source_ref_manifests",
            ],
        ))
    return errors


def check_root_build_wiring(root: Path) -> list[str]:
    path = Path("BUILD.bazel")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors: list[str] = []
    docs_block = bazel_rule_block(text, "filegroup",
                                  "phase17_release_candidate_evidence_docs")
    if docs_block is None:
        errors.append(
            "BUILD.bazel filegroup phase17_release_candidate_evidence_docs missing required Bazel rule"
        )
    aliases = {
        "phase17_release_candidate_artifacts":
        "//tools/bazel:phase17_release_candidate_artifacts",
        "phase17_verify": "//tools/bazel:phase17_verify",
        "phase17_verify_tests": "//tools/bazel:phase17_verify_tests",
    }
    for name, actual in aliases.items():
        errors.extend(
            check_bazel_string_attr(
                bazel_rule_block(text, "alias", name),
                f"BUILD.bazel alias {name}",
                "actual",
                actual,
            ))
    return errors


def check_rust_workflow_wiring(root: Path) -> list[str]:
    path = Path("tools/bazel/rust_workflow.sh")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors: list[str] = []
    verify_commands = shell_case_commands(text, "phase17_verify")
    verify_tests_commands = shell_case_commands(text, "phase17_verify_tests")
    if verify_commands is None:
        errors.append(
            "tools/bazel/rust_workflow.sh phase17_verify case arm missing")
    else:
        errors.extend(
            missing_required_items(
                "tools/bazel/rust_workflow.sh phase17_verify case arm",
                verify_commands,
                [
                    "python3 tools/bazel/phase17_release_candidate_evidence.py --wiring-only",
                    "python3 tools/bazel/phase17_release_candidate_evidence.py --quick",
                ],
            ))
    if verify_tests_commands is None:
        errors.append(
            "tools/bazel/rust_workflow.sh phase17_verify_tests case arm missing"
        )
    else:
        errors.extend(
            missing_required_items(
                "tools/bazel/rust_workflow.sh phase17_verify_tests case arm",
                verify_tests_commands,
                [
                    "python3 tools/bazel/phase17_release_candidate_evidence_test.py"
                ],
            ))
    return errors


def check_just_wiring(root: Path) -> list[str]:
    path = Path("justfile")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors: list[str] = []
    verify_commands = just_recipe_commands(text, "phase17-verify")
    smoke_commands = just_recipe_commands(text,
                                          "phase17-release-artifacts-smoke")
    tests_line = "bazel run //tools/bazel:phase17_verify_tests"
    verify_line = "bazel run //tools/bazel:phase17_verify"
    if verify_commands is None:
        errors.append("justfile phase17-verify recipe missing")
    else:
        errors.extend(
            missing_required_items(
                "justfile phase17-verify recipe",
                verify_commands,
                [tests_line, verify_line],
            ))
        errors.extend(
            check_command_order("justfile phase17-verify recipe",
                                verify_commands, tests_line, verify_line))
    if smoke_commands is None:
        errors.append(
            "justfile phase17-release-artifacts-smoke recipe missing")
    else:
        errors.extend(
            missing_required_items(
                "justfile phase17-release-artifacts-smoke recipe",
                smoke_commands,
                [
                    "bazel build //tools/bazel:phase17_representative_release_smoke"
                ],
            ))
    return errors


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    manifest_srcs = [
        Path(path).relative_to("tools/bazel").as_posix()
        for path in SOURCE_REF_MANIFESTS
    ]
    errors.extend(check_tools_build_wiring(root, manifest_srcs))
    errors.extend(check_root_build_wiring(root))
    errors.extend(check_rust_workflow_wiring(root))
    errors.extend(check_just_wiring(root))
    if errors:
        raise VerificationError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 17 release candidate evidence")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 17 evidence contract")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="scan Phase 17 contract and generated artifacts")
    parser.add_argument("--quick",
                        action="store_true",
                        help="write deterministic Phase 17 evidence artifacts")
    parser.add_argument("--release-evidence",
                        help="optional release evidence JSON input")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel and just workflow wiring")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 17 evidence output directory")
    args = parser.parse_args()
    selected_modes = [
        args.contract_only, args.security_only, args.quick, args.wiring_only
    ]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.release_evidence and not args.quick:
        parser.error("--release-evidence is only valid with --quick")
    output_dir = Path(args.output_dir)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 17 release candidate evidence contract passed")
        elif args.security_only:
            check_security(ROOT, output_dir)
            print("Phase 17 release candidate evidence security scan passed")
        elif args.quick:
            contract = check_contract(ROOT)
            release_rows = validated_release_rows(ROOT, contract,
                                                  args.release_evidence)
            write_quick_artifacts(ROOT, contract, output_dir, release_rows)
            check_security(ROOT, output_dir)
            print(
                f"Phase 17 release candidate evidence written to {output_dir.as_posix()}"
            )
        else:
            check_wiring(ROOT)
            print("Phase 17 release candidate evidence wiring passed")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
