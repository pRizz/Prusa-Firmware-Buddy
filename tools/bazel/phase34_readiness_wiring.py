from __future__ import annotations


def validate_output_security(
    full_output: Path,
    display_root: str,
) -> None:
    errors = []
    for artifact in NON_SNAPSHOT_OUTPUTS:
        candidate = full_output / artifact
        if not candidate.is_file():
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
            reject_forbidden_text(Path(artifact), text)
            if candidate.suffix == ".json":
                reject_forbidden_fields(
                    json.loads(text),
                    artifact,
                )
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    print(f"Phase 34 security scan passed for {display_root}")


def run_security_scan(root: Path,
                      output_arg: str | Path = DEFAULT_OUTPUT_DIR) -> None:
    ensure_no_publication_state(root)
    relative_output = path_under(output_arg, DEFAULT_OUTPUT_DIR,
                                 "--output-dir")
    full_output = root / relative_output
    if not full_output.exists():
        print(f"no Phase 34 outputs to scan at {relative_output.as_posix()}")
        return
    if full_output.is_symlink() or not full_output.is_dir():
        raise VerificationError(
            f"Phase 34 output root contains a symlink escape: {relative_output.as_posix()}"
        )
    validate_output_security(full_output, relative_output.as_posix())


def shell_case_commands(text: str, case_name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{case_name})":
            continue
        commands = []
        for body_line in lines[index + 1:]:
            stripped = body_line.strip()
            if stripped == ";;":
                return commands
            if stripped.startswith("python3 "):
                commands.append(stripped)
    return None


def just_recipe_commands(text: str, recipe_name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{recipe_name}:":
            continue
        commands = []
        for body_line in lines[index + 1:]:
            if body_line and not body_line[0].isspace():
                break
            if body_line.strip():
                commands.append(body_line.strip())
        return commands
    return None


def check_wiring(root: Path) -> None:
    required = {
        "tools/bazel/BUILD.bazel": [
            'name = "phase34_source_ref_manifests"',
            'name = "phase34_verify"',
            'name = "phase34_verify_tests"',
            '"phase34_decision_reconciliation.py"',
            '"phase34_decision_reconciliation_test.py"',
            '"phase34_decision_reconciliation_integration_test.py"',
            "//:phase34_final_readiness_demotion_dry_run_docs",
        ],
        "BUILD.bazel": [
            'name = "phase34_final_readiness_demotion_dry_run_docs"',
            'name = "phase34_verify"',
            'actual = "//tools/bazel:phase34_verify"',
            'name = "phase34_verify_tests"',
        ],
        "tools/bazel/rust_workflow.sh":
        ["phase34_verify)", "phase34_verify_tests)"],
        "justfile": [
            "phase34-verify:", "bazel run //tools/bazel:phase34_verify_tests",
            "bazel run //tools/bazel:phase34_verify"
        ],
    }
    errors = []
    texts: dict[str, str] = {}
    for relative_path, snippets in required.items():
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing required file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        texts[relative_path] = text
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{relative_path} missing {snippet}")
    workflow = texts.get("tools/bazel/rust_workflow.sh", "")
    if shell_case_commands(workflow,
                           "phase34_verify") != PHASE34_VERIFY_COMMANDS:
        errors.append(
            "tools/bazel/rust_workflow.sh phase34_verify command order is invalid"
        )
    if shell_case_commands(workflow, "phase34_verify_tests") != [
            "python3 tools/bazel/phase33_maintainer_decision_inputs_test.py",
            "python3 tools/bazel/phase34_decision_reconciliation_test.py",
            "python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py",
            "python3 tools/bazel/phase34_decision_reconciliation_integration_test.py",
    ]:
        errors.append(
            "tools/bazel/rust_workflow.sh phase34_verify_tests command is invalid"
        )
    if just_recipe_commands(texts.get("justfile", ""), "phase34-verify") != [
            "bazel run //tools/bazel:phase34_verify_tests",
            "bazel run //tools/bazel:phase34_verify",
    ]:
        errors.append("justfile phase34-verify must run tests before verifier")
    if errors:
        raise VerificationError("\n".join(errors))
    print("Phase 34 wiring passed")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Generate Phase 34 final readiness and demotion dry-run artifacts.")
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--phase31-output-dir",
                        default=DEFAULT_PHASE31_OUTPUT_DIR.as_posix())
    parser.add_argument("--phase33-handoff",
                        default=DEFAULT_PHASE33_HANDOFF.as_posix())
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.contract_only:
            contract = load_contract(ROOT)
            print(f"{contract['id']} ok")
            return 0
        if args.security_only:
            run_security_scan(ROOT, args.output_dir)
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            return 0
        if args.quick:
            maybe_error = run_quick(ROOT, args.phase31_output_dir,
                                    args.phase33_handoff, args.output_dir)
            if maybe_error is not None:
                raise VerificationError(maybe_error)
            print(
                "Phase 34 final readiness and demotion dry-run quick validation passed"
            )
            return 0
        raise VerificationError("no mode selected")
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
