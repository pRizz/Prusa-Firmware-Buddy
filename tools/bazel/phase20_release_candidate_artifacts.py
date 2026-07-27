#!/usr/bin/env python3
from __future__ import annotations

from phase20_artifact_contract import *
from phase20_artifact_policy import *


def write_json(root: Path, relative_path: Path, data: dict[str, Any]) -> None:
    full_path = root / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")


def write_quick_artifacts(root: Path, contract: dict[str,
                                                     Any], output_dir: Path,
                          release_rows: dict[str, dict[str, Any]]) -> None:
    relative_output_dir, full_output_dir = resolved_output_dir(
        root, output_dir)
    if full_output_dir.exists():
        shutil.rmtree(full_output_dir)
    (full_output_dir / "logs").mkdir(parents=True)
    rows = [
        quick_result_row(row, release_rows.get(str(row["id"])))
        for row in contract_rows(contract)
    ]
    release_inputs_supplied = bool(release_rows)
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    result_manifest = {
        "artifact_name": contract["artifact_name"],
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": relative_output_dir.as_posix(),
        "release_inputs_supplied": release_inputs_supplied,
        "release_identity_label": RELEASE_IDENTITY_LABEL,
        "release_identity_command": RELEASE_IDENTITY_COMMAND,
        "rows": rows,
        "status_counts": status_counts,
    }
    normalized = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "rows": rows,
    }
    signing_summary = {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "release_inputs_supplied":
        release_inputs_supplied,
        "rows": [{
            "id": row["id"],
            "status": row["status"],
            "proof_class": row["proof_class"],
            "release_run_id": row["release_run_id"],
            "timestamp": row["timestamp"],
            "operator": row["operator"],
            "build_input_identity": row["build_input_identity"],
            "key_identity_ref": row["key_identity_ref"],
            "signing_mode": row["signing_mode"],
            "subject_digests": row["subject_digests"],
            "retention_refs": row["retention_refs"],
            "verification_outcome": row["verification_outcome"],
            "contract_validation": row["contract_validation"],
            "redaction_scan": row["redaction_scan"],
            "source_contract_snapshot": row["source_contract_snapshot"],
        } for row in rows],
    }
    comparison_report = {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "rows": [{
            "id": row["id"],
            "artifact_surface": row["artifact_surface"],
            "mismatch_class": row["mismatch_class"],
            "mismatch_reason": row["mismatch_reason"],
            "owner_phase": row["owner_phase"],
            "affected_artifact_surface": row["affected_artifact_surface"],
            "residual_risk": row["residual_risk"],
        } for row in rows],
    }
    target_snapshot = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "release_identity_label": RELEASE_IDENTITY_LABEL,
        "release_identity_command": RELEASE_IDENTITY_COMMAND,
        "contract_manifest": CONTRACT_MANIFEST.as_posix(),
        "release_input_template": RELEASE_INPUT_TEMPLATE.as_posix(),
        "required_artifact_outputs": REQUIRED_ARTIFACT_OUTPUTS,
    }
    write_json(root, relative_output_dir / "release-result-manifest.json",
               result_manifest)
    write_json(root, relative_output_dir / "normalized-release-results.json",
               normalized)
    write_json(
        root, relative_output_dir / "redacted-signing-provenance-summary.json",
        signing_summary)
    write_json(root,
               relative_output_dir / "comparison-classification-report.json",
               comparison_report)
    write_json(root, relative_output_dir / "target-source-snapshot.json",
               target_snapshot)
    shutil.copy2(
        root / RELEASE_INPUT_TEMPLATE,
        root / relative_output_dir / "release-environment-input-template.json")
    log_path = root / relative_output_dir / "logs/phase20-release-candidate-artifacts.log"
    log_path.write_text(
        "\n".join([
            f"phase={PHASE}",
            f"release_inputs_supplied={str(release_inputs_supplied).lower()}",
            f"rows={len(rows)}",
            f"output_root={relative_output_dir.as_posix()}",
        ]) + "\n",
        encoding="utf-8",
    )


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


def check_exact_bazel_list(block: str | None, location: str, attr: str,
                           expected: list[str]) -> list[str]:
    if block is None:
        return [f"{location} missing required Bazel rule"]
    actual = bazel_list_attr(block, attr)
    if actual == expected:
        return []
    missing = missing_required_items(f"{location} {attr}", actual, expected)
    extra = [
        f"{location} {attr} has unexpected wiring item: {item}"
        for item in actual if item not in expected
    ]
    if missing or extra:
        return missing + extra
    return [f"{location} {attr} order must match Phase 20 wiring"]


def check_bazel_string_attr(block: str | None, location: str, attr: str,
                            expected: str) -> list[str]:
    if block is None:
        return [f"{location} missing required Bazel rule"]
    actual = bazel_string_attr(block, attr)
    if actual == expected:
        return []
    return [f"{location} {attr} must be {expected!r}, not {actual!r}"]


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


def check_phase20_release_identity_target(text: str) -> list[str]:
    manifest_block = bazel_rule_block(
        text, "filegroup", "phase20_release_environment_input_manifest")
    release_block = bazel_rule_block(text, "filegroup",
                                     "phase17_release_candidate_artifacts")
    errors = check_exact_bazel_list(
        manifest_block,
        "tools/bazel/BUILD.bazel filegroup phase20_release_environment_input_manifest",
        "srcs",
        [RELEASE_INPUT_TEMPLATE.relative_to("tools/bazel").as_posix()],
    )
    expected_srcs = [":phase20_release_environment_input_manifest"]
    if release_block is None:
        errors.append(
            "tools/bazel/BUILD.bazel missing phase17_release_candidate_artifacts filegroup"
        )
        return errors
    srcs = bazel_list_attr(release_block, "srcs")
    forbidden_smoke_deps = {
        ":phase17_representative_release_smoke",
        ":representative_release_artifacts",
        "//tools/bazel:phase17_representative_release_smoke",
        "//tools/bazel:representative_release_artifacts",
        "//tools/bazel:phase3_verify",
    }
    wrapped_smoke = sorted(set(srcs) & forbidden_smoke_deps)
    if wrapped_smoke:
        errors.append(
            "tools/bazel/BUILD.bazel phase17_release_candidate_artifacts cannot wrap local smoke dependencies: "
            + ", ".join(wrapped_smoke))
    if srcs != expected_srcs:
        errors.extend(
            check_exact_bazel_list(
                release_block,
                "tools/bazel/BUILD.bazel filegroup phase17_release_candidate_artifacts",
                "srcs",
                expected_srcs,
            ))
    return errors


def check_tools_build_wiring(root: Path) -> list[str]:
    path = Path("tools/bazel/BUILD.bazel")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors = check_phase20_release_identity_target(text)
    source_refs_block = bazel_rule_block(text, "filegroup",
                                         "phase20_source_ref_manifests")
    smoke_block = bazel_rule_block(text, "filegroup",
                                   "phase17_representative_release_smoke")
    verify_block = bazel_rule_block(text, "shell_binary", "phase20_verify")
    verify_tests_block = bazel_rule_block(text, "shell_binary",
                                          "phase20_verify_tests")
    errors.extend(
        check_exact_bazel_list(
            smoke_block,
            "tools/bazel/BUILD.bazel filegroup phase17_representative_release_smoke",
            "srcs",
            [":representative_release_artifacts"],
        ))
    errors.extend(
        check_exact_bazel_list(
            source_refs_block,
            "tools/bazel/BUILD.bazel filegroup phase20_source_ref_manifests",
            "srcs",
            PHASE20_SOURCE_REF_MANIFESTS,
        ))
    errors.extend(
        check_exact_bazel_list(
            verify_block,
            "tools/bazel/BUILD.bazel shell_binary phase20_verify",
            "data",
            [
                "phase20_artifact_contract.py",
                "phase20_artifact_policy.py",
                "phase20_release_candidate_artifacts.py",
                "manifests/phase20_release_candidate_artifacts_contract.json",
                "manifests/phase20_release_environment_inputs.template.json",
                ":phase20_source_ref_manifests",
                ":phase17_release_candidate_artifacts",
                ":phase17_representative_release_smoke",
                "//:phase20_release_candidate_artifacts_docs",
                "//:phase17_release_candidate_evidence_docs",
                "//:phase19_aggregate_ci_evidence_docs",
            ],
        ))
    errors.extend(
        check_exact_bazel_list(
            verify_tests_block,
            "tools/bazel/BUILD.bazel shell_binary phase20_verify_tests",
            "data",
            [
                "phase20_artifact_contract.py",
                "phase20_artifact_policy.py",
                "phase20_release_candidate_artifacts.py",
                "phase20_release_candidate_artifacts_failure_test.py",
                "phase20_release_candidate_artifacts_test.py",
                "phase20_release_candidate_artifacts_wiring_test.py",
                "manifests/phase20_release_candidate_artifacts_contract.json",
                "manifests/phase20_release_environment_inputs.template.json",
                ":phase20_source_ref_manifests",
                ":phase17_release_candidate_artifacts",
                ":phase17_representative_release_smoke",
            ],
        ))
    return errors


def check_root_build_wiring(root: Path) -> list[str]:
    path = Path("BUILD.bazel")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    errors = check_exact_bazel_list(
        bazel_rule_block(text, "filegroup",
                         "phase20_release_candidate_artifacts_docs"),
        "BUILD.bazel filegroup phase20_release_candidate_artifacts_docs",
        "srcs",
        PHASE20_DOCS,
    )
    aliases = {
        "phase20_verify": "//tools/bazel:phase20_verify",
        "phase20_verify_tests": "//tools/bazel:phase20_verify_tests",
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
    verify_commands = shell_case_commands(text, "phase20_verify")
    verify_tests_commands = shell_case_commands(text, "phase20_verify_tests")
    if verify_commands is None:
        errors.append(
            "tools/bazel/rust_workflow.sh phase20_verify case arm missing")
    else:
        expected_verify_commands = [
            "python3 tools/bazel/phase20_release_candidate_artifacts.py --wiring-only",
            "python3 tools/bazel/phase20_release_candidate_artifacts.py --quick",
        ]
        errors.extend(
            missing_required_items(
                "tools/bazel/rust_workflow.sh phase20_verify case arm",
                verify_commands,
                expected_verify_commands,
            ))
        errors.extend(
            check_command_order(
                "tools/bazel/rust_workflow.sh phase20_verify case arm",
                verify_commands,
                expected_verify_commands[0],
                expected_verify_commands[1],
            ))
    if verify_tests_commands is None:
        errors.append(
            "tools/bazel/rust_workflow.sh phase20_verify_tests case arm missing"
        )
    else:
        errors.extend(
            missing_required_items(
                "tools/bazel/rust_workflow.sh phase20_verify_tests case arm",
                verify_tests_commands,
                [
                    "python3 tools/bazel/phase20_release_candidate_artifacts_test.py"
                ],
            ))
    return errors


def check_just_wiring(root: Path) -> list[str]:
    path = Path("justfile")
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    verify_commands = just_recipe_commands(text, "phase20-verify")
    tests_line = "bazel run //tools/bazel:phase20_verify_tests"
    verify_line = "bazel run //tools/bazel:phase20_verify"
    if verify_commands is None:
        return ["justfile phase20-verify recipe missing"]
    errors = missing_required_items("justfile phase20-verify recipe",
                                    verify_commands, [tests_line, verify_line])
    errors.extend(
        check_command_order("justfile phase20-verify recipe", verify_commands,
                            tests_line, verify_line))
    return errors


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    errors.extend(check_tools_build_wiring(root))
    errors.extend(check_root_build_wiring(root))
    errors.extend(check_rust_workflow_wiring(root))
    errors.extend(check_just_wiring(root))
    if errors:
        raise VerificationError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 20 release candidate artifacts")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 20 contract")
    parser.add_argument(
        "--security-only",
        action="store_true",
        help="scan checked-in Phase 20 contract/template files")
    parser.add_argument("--quick",
                        action="store_true",
                        help="write deterministic Phase 20 quick artifacts")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel and just workflow wiring")
    parser.add_argument("--release-input",
                        help="optional approved release input JSON")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 20 evidence output directory")
    args = parser.parse_args()
    selected_modes = [
        args.contract_only, args.security_only, args.quick, args.wiring_only
    ]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.release_input and not args.quick:
        parser.error("--release-input is only valid with --quick")
    output_dir = Path(args.output_dir)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 20 release candidate artifact contract passed")
        elif args.security_only:
            check_contract(ROOT)
            check_security(ROOT)
            print("Phase 20 release candidate artifact security scan passed")
        else:
            if args.wiring_only:
                check_wiring(ROOT)
                print("Phase 20 release candidate artifact wiring passed")
                return 0
            contract = check_contract(ROOT)
            release_rows = validated_release_rows(ROOT, contract,
                                                  args.release_input)
            write_quick_artifacts(ROOT, contract, output_dir, release_rows)
            check_security(ROOT, output_dir)
            print(
                f"Phase 20 release candidate artifacts written to {output_dir.as_posix()}"
            )
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
