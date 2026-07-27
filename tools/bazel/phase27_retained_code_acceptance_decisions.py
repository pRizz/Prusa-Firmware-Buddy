#!/usr/bin/env python3
from __future__ import annotations

from phase27_decision_normalization import *


def build_decision_rows(
        retained_rows: list[dict[str, Any]],
        final_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in retained_rows:
        rows.append({
            "row_type": "retained_code_decision",
            "row_id": row["packet_id"],
            "status": row["status"],
            "decision": row["decision"],
            "maintainer_decision": row["maintainer_decision"],
            "hard_failure_state": row["hard_failure_state"],
            "demotion_authorization": "blocked",
        })
    for row in final_rows:
        rows.append({
            "row_type": "final_readiness_decision",
            "row_id": row["criterion_id"],
            "decision_id": row["decision_id"],
            "status": row["status"],
            "decision": row["decision"],
            "maintainer_decision": row["maintainer_decision"],
            "hard_failure_state": row["hard_failure_state"],
            "demotion_authorization": "blocked",
        })
    return rows


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return counts


def write_contract_snapshots(root: Path, output_dir: Path,
                             phase26_rows_path: Path) -> None:
    snapshots_dir = root / output_dir / "contract-snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / PHASE18_CONTRACT,
                 snapshots_dir / PHASE18_CONTRACT.name)
    shutil.copy2(root / PHASE26_CONTRACT,
                 snapshots_dir / PHASE26_CONTRACT.name)
    shutil.copy2(root / phase26_rows_path,
                 snapshots_dir / "phase26-upstream-result-row-table.json")


def write_phase27_outputs(root: Path, output_dir: Path,
                          maybe_maintainer_input: str | None,
                          phase26_rows_arg: str) -> None:
    checked = check_contract(root)
    contract = checked["contract"]
    phase18_contract = checked["phase18_contract"]
    phase26_contract = checked["phase26_contract"]
    phase26_rows_path = repo_relative_path(phase26_rows_arg,
                                           "--phase26-upstream-rows")
    relative_output_dir = reset_output_root(root, output_dir)
    phase26_rows = load_phase26_upstream_rows(root, phase26_rows_path,
                                              phase18_contract,
                                              phase26_contract)
    maintainer_input = load_maintainer_input(root, maybe_maintainer_input)
    retained_rows = normalize_retained_decisions(phase18_contract, contract,
                                                 maintainer_input)
    final_rows = normalize_final_decisions(phase18_contract, contract,
                                           phase26_rows, maintainer_input)
    decision_rows = build_decision_rows(retained_rows, final_rows)
    generated_at = utc_now()
    source_refs = source_contract_refs(contract)
    template = maintainer_input_template(phase18_contract, contract)
    handoff_policy = require_dict(contract, "phase28_handoff_policy",
                                  "Phase 27 contract")
    exception_rows = [{
        "row_type":
        "retained_code_decision"
        if "packet_id" in row else "final_readiness_decision",
        "row_id":
        row.get("packet_id", row.get("criterion_id")),
        "exception":
        row["exception"],
        "residual_risk":
        row["residual_risk"],
        "owner":
        row["exception"].get("owner", row.get("approver", "")) if isinstance(
            row.get("exception"), dict) else "",
    } for row in [*retained_rows, *final_rows]
                      if isinstance(row.get("exception"), dict)
                      and row["exception"].get("status") != "none"]
    risk_rows = [{
        "row_type":
        "retained_code_decision"
        if "packet_id" in row else "final_readiness_decision",
        "row_id":
        row.get("packet_id", row.get("criterion_id")),
        "residual_risk":
        row["residual_risk"],
        "residual_risk_state":
        row["residual_risk_state"],
        "owner":
        row.get("approver",
                row.get("source_packet", {}).get("owner", "")),
    } for row in [*retained_rows, *final_rows]]
    artifact_refs = [{
        "path": (relative_output_dir / artifact).as_posix(),
        "purpose":
        "phase27-retained-code-acceptance-decision-evidence",
    } for artifact in GENERATED_ARTIFACTS]
    write_json(
        root,
        relative_output_dir / "acceptance-run-manifest.json",
        {
            "artifact_name": "phase27-retained-code-acceptance-decisions",
            "generated_at_utc": generated_at,
            "generated_artifacts": GENERATED_ARTIFACTS,
            "maintainer_input_supplied": maintainer_input is not None,
            "output_root": relative_output_dir.as_posix(),
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "retained_decision_count": len(retained_rows),
            "final_readiness_decision_count": len(final_rows),
            "source_contract_refs": source_refs,
        },
    )
    write_json(root,
               relative_output_dir / "normalized-retained-code-decisions.json",
               {"rows": retained_rows})
    write_json(root, relative_output_dir / "residual-risk-register.json",
               {"rows": risk_rows})
    write_json(root, relative_output_dir / "exception-decision-register.json",
               {"rows": exception_rows})
    write_json(
        root,
        relative_output_dir / "final-readiness-decision-summary.json",
        {
            "rows": final_rows,
            "status_counts": status_counts(final_rows),
            "phase27_may_authorize_demotion": False,
            "demotion_authorization": "blocked",
        },
    )
    write_json(
        root,
        relative_output_dir / "phase28-handoff-manifest.json",
        {
            "phase":
            PHASE,
            "phase_lifecycle_id":
            PHASE_LIFECYCLE_ID,
            "demotion_authorization":
            handoff_policy["demotion_authorization"],
            "phase27_may_authorize_demotion":
            handoff_policy["phase27_may_authorize_demotion"],
            "phase28_required_decision":
            handoff_policy["phase28_required_decision"],
            "blocked_criteria": ["final-reference-demotion-allowed"],
        },
    )
    write_json(root, relative_output_dir / "decision-row-table.json",
               {"rows": decision_rows})
    write_json(
        root,
        relative_output_dir / "maintainer-acceptance-input-template.json",
        template)
    write_json(
        root,
        relative_output_dir / "artifact-reference-summary.json",
        {
            "artifact_refs": artifact_refs,
            "source_contract_refs": source_refs,
            "phase26_upstream_rows": phase26_rows_path.as_posix(),
        },
    )
    write_contract_snapshots(root, relative_output_dir, phase26_rows_path)
    run_security_scan(root, maybe_maintainer_input, relative_output_dir)


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
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase27_retained_code_acceptance_decisions_docs"',
                'name = "phase27_verify"',
                'actual = "//tools/bazel:phase27_verify"',
                'name = "phase27_verify_tests"',
                'actual = "//tools/bazel:phase27_verify_tests"',
                *[f'"{doc}"' for doc in PHASE27_DOCS],
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase27_source_ref_manifests"',
                'name = "phase27_verify"',
                'name = "phase27_verify_tests"',
                "phase27_retained_code_acceptance_decisions.py",
                "phase27_retained_code_acceptance_decisions_test.py",
                "phase27_retained_code_acceptance_decisions_contract.json",
                "phase26_release_signing_upstream_evidence.py",
                "//:phase27_retained_code_acceptance_decisions_docs",
                *[
                    f'"{manifest}"'
                    for manifest in PHASE27_SOURCE_REF_MANIFESTS
                ],
            ],
        ))
    try:
        workflow_text = read_text(root, Path("tools/bazel/rust_workflow.sh"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        verify_commands = shell_case_commands(workflow_text, "phase27_verify")
        test_commands = shell_case_commands(workflow_text,
                                            "phase27_verify_tests")
        if verify_commands is None:
            errors.append(
                "tools/bazel/rust_workflow.sh phase27_verify case arm missing")
        else:
            errors.extend(
                missing_required_items(
                    "tools/bazel/rust_workflow.sh phase27_verify case arm",
                    verify_commands, PHASE27_VERIFY_COMMANDS))
            errors.extend(
                check_command_order(
                    "tools/bazel/rust_workflow.sh phase27_verify case arm",
                    verify_commands,
                    PHASE27_VERIFY_COMMANDS[0],
                    PHASE27_VERIFY_COMMANDS[1],
                    "must run --wiring-only before Phase 26 generation",
                ))
            errors.extend(
                check_command_order(
                    "tools/bazel/rust_workflow.sh phase27_verify case arm",
                    verify_commands,
                    PHASE27_VERIFY_COMMANDS[1],
                    PHASE27_VERIFY_COMMANDS[2],
                    "must run Phase 26 quick before Phase 27 quick",
                ))
        if test_commands is None:
            errors.append(
                "tools/bazel/rust_workflow.sh phase27_verify_tests case arm missing"
            )
        else:
            errors.extend(
                missing_required_items(
                    "tools/bazel/rust_workflow.sh phase27_verify_tests case arm",
                    test_commands, [PHASE27_TEST_COMMAND]))
    try:
        just_text = read_text(root, Path("justfile"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        just_commands = just_recipe_commands(just_text, "phase27-verify")
        test_line = "bazel run //tools/bazel:phase27_verify_tests"
        verify_line = "bazel run //tools/bazel:phase27_verify"
        if just_commands is None:
            errors.append("justfile phase27-verify recipe missing")
        else:
            errors.extend(
                missing_required_items("justfile phase27-verify recipe",
                                       just_commands,
                                       [test_line, verify_line]))
            errors.extend(
                check_command_order(
                    "justfile phase27-verify recipe",
                    just_commands,
                    test_line,
                    verify_line,
                    "must run tests before verifier",
                ))
    if errors:
        raise VerificationError("\n".join(errors))


def run_security_scan(root: Path,
                      maybe_maintainer_input: str | None = None,
                      maybe_output_dir: Path | None = None) -> None:
    errors: list[str] = []
    paths = [CONTRACT_MANIFEST]
    if maybe_maintainer_input is not None:
        paths.append(
            repo_relative_path(maybe_maintainer_input, "--maintainer-input"))
    output_dir = maybe_output_dir if maybe_output_dir is not None else DEFAULT_OUTPUT_DIR
    if (root / output_dir).exists():
        paths.extend(output_dir / artifact for artifact in GENERATED_ARTIFACTS
                     if (root / output_dir / artifact).exists())
    for path in paths:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_field_names(json.loads(text), path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Phase 27 retained-code acceptance decisions.")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 27 contract against Phase 18")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="scan Phase 27 contract and retained outputs")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel, workflow, and just wiring")
    parser.add_argument("--quick",
                        action="store_true",
                        help="write retained Phase 27 outputs")
    parser.add_argument(
        "--maintainer-input",
        help="optional Phase 27 maintainer decision input JSON")
    parser.add_argument("--phase26-upstream-rows",
                        default=PHASE26_UPSTREAM_ROWS.as_posix(),
                        help="Phase 26 upstream result row table")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 27 output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        check_contract(ROOT)
        if args.security_only:
            run_security_scan(ROOT)
            print(
                "Phase 27 retained-code acceptance decisions security scan passed"
            )
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            print("Phase 27 retained-code acceptance decisions wiring passed")
            return 0
        if args.quick:
            run_security_scan(ROOT, args.maintainer_input)
            write_phase27_outputs(ROOT, Path(args.output_dir),
                                  args.maintainer_input,
                                  args.phase26_upstream_rows)
            print(
                "Phase 27 retained-code acceptance decisions quick validation passed"
            )
            return 0
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    print("Phase 27 retained-code acceptance decisions contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
