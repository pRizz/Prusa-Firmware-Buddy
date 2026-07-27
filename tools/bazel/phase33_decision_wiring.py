from __future__ import annotations


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
            if stripped.startswith("python3 "):
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
            if stripped:
                commands.append(stripped)
        return commands
    return None


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    required_text = {
        Path("tools/bazel/BUILD.bazel"): [
            'name = "phase33_source_ref_manifests"',
            'name = "phase33_verify"',
            'name = "phase33_verify_tests"',
            '"phase33_maintainer_decision_inputs.py"',
            '"phase33_maintainer_decision_inputs_test.py"',
            '"manifests/phase33_maintainer_decision_inputs_contract.json"',
            "//:phase33_maintainer_decision_inputs_docs",
        ],
        Path("BUILD.bazel"): [
            'name = "phase33_maintainer_decision_inputs_docs"',
            'name = "phase33_verify"',
            'actual = "//tools/bazel:phase33_verify"',
            'name = "phase33_verify_tests"',
            'actual = "//tools/bazel:phase33_verify_tests"',
        ],
        Path("tools/bazel/rust_workflow.sh"): [
            "phase33_verify)",
            "phase33_verify_tests)",
            "python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only",
        ],
        Path("justfile"): [
            "phase33-verify:",
            "bazel run //tools/bazel:phase33_verify_tests",
            "bazel run //tools/bazel:phase33_verify",
        ],
    }
    for path, snippets in required_text.items():
        try:
            text = read_text(root, path)
        except VerificationError as error:
            errors.append(str(error))
            continue
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{path.as_posix()} missing {snippet}")
    try:
        workflow_text = read_text(root, "tools/bazel/rust_workflow.sh")
        verify_commands = shell_case_commands(workflow_text, "phase33_verify")
        test_commands = shell_case_commands(workflow_text,
                                            "phase33_verify_tests")
        if verify_commands != PHASE33_VERIFY_COMMANDS:
            errors.append(
                "tools/bazel/rust_workflow.sh phase33_verify command order is invalid"
            )
        if test_commands != [
                "python3 tools/bazel/phase33_maintainer_decision_inputs_test.py"
        ]:
            errors.append(
                "tools/bazel/rust_workflow.sh phase33_verify_tests command is invalid"
            )
    except VerificationError as error:
        errors.append(str(error))
    try:
        just_commands = just_recipe_commands(read_text(root, "justfile"),
                                             "phase33-verify")
        if just_commands != [
                "bazel run //tools/bazel:phase33_verify_tests",
                "bazel run //tools/bazel:phase33_verify",
        ]:
            errors.append(
                "justfile phase33-verify must run tests before verifier")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    print("Phase 33 wiring passed")


def contract_only(root: Path = ROOT) -> None:
    contract = load_contract(root)
    print(f"{contract['id']} ok")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Phase 33 maintainer decision inputs.")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 33 contract")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="write Phase 33 maintainer decision handoff artifacts")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="scan Phase 33 inputs and generated artifacts")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel, workflow, and just wiring")
    parser.add_argument(
        "--maintainer-decisions",
        help="optional explicit maintainer decision input JSON")
    parser.add_argument("--phase32-handoff",
                        default=DEFAULT_PHASE32_HANDOFF.as_posix(),
                        help="Phase 32 downstream handoff manifest")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 33 output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.contract_only:
            contract_only(ROOT)
            return 0
        if args.security_only:
            run_security_scan(ROOT, args.maintainer_decisions, args.output_dir)
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            return 0
        if args.quick:
            run_security_scan(ROOT,
                              args.maintainer_decisions,
                              args.output_dir,
                              scan_existing_outputs=False)
            run_quick(ROOT, args.phase32_handoff, args.output_dir,
                      args.maintainer_decisions)
            return 0
        raise VerificationError("no mode selected")
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
