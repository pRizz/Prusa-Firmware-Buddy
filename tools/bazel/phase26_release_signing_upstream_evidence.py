#!/usr/bin/env python3
from __future__ import annotations

from phase26_upstream_policy import *


def write_operator_template(root: Path, output_dir: Path,
                            phase20_contract: dict[str, Any]) -> None:
    rows = []
    for row in contract_rows(phase20_contract, PHASE20_CONTRACT):
        row_id = require_string(row, "id", "phase20 row")
        row_template = {
            "id": row_id,
            "artifact_refs": [],
            "artifact_surface": row.get("artifact_surface", ""),
            "build_input_identity": "",
            "mismatch_class": "",
            "mismatch_reason": "",
            "operator": "",
            "owner_phase": "20-release-candidate-artifact-production",
            "proof_class": "",
            "release_run_id": "",
            "residual_risk": "",
            "retention_refs": [],
            "status": "",
            "subject_digests": [],
            "timestamp": "",
            "verification_outcome": "",
            "affected_artifact_surface": row.get("artifact_surface", ""),
        }
        for field in phase20_required_metadata_fields(row):
            if field not in row_template:
                row_template[field] = [] if field in {
                    "artifact_refs", "retention_refs", "subject_digests"
                } else ""
        rows.append(row_template)
    write_json(
        root,
        output_dir / "operator-release-input-template.json",
        {
            "schema_version": "1",
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "evidence_rows": rows,
        },
    )


def write_contract_snapshots(root: Path, output_dir: Path) -> None:
    snapshots_dir = root / output_dir / "contract-snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    for snapshot in SNAPSHOT_CONTRACTS:
        shutil.copy2(root / snapshot, snapshots_dir / snapshot.name)


def reset_output_root(root: Path, output_dir: Path) -> Path:
    relative_output_dir, full_output_dir = validate_output_dir(
        root, output_dir)
    if full_output_dir.exists():
        if not full_output_dir.is_dir():
            raise VerificationError(
                f"--output-dir exists and is not a directory: {relative_output_dir.as_posix()}"
            )
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)
    return relative_output_dir


def write_retained_outputs(
    root: Path,
    output_dir: Path,
    release_rows: dict[str, dict[str, Any]],
    real_release_evidence_supplied: bool,
    maybe_upstream_paths: dict[str, str | None],
) -> None:
    generated_at = utc_now()
    phase18_contract = load_json(root, PHASE18_CONTRACT)
    requirements_by_id = {
        require_string(requirement, "criterion_id", "upstream_result_requirement"):
        requirement
        for requirement in phase18_upstream_requirements(phase18_contract)
    }
    consumed_rows = consumed_upstream_rows(
        root,
        maybe_upstream_paths,
        requirements_by_id,
        generated_at,
        phase18_upstream_status_vocabulary(phase18_contract),
    )
    phase20_contract = load_json(root, PHASE20_CONTRACT)
    upstream_rows = build_upstream_rows(root, output_dir, release_rows,
                                        real_release_evidence_supplied,
                                        generated_at, consumed_rows)
    release_status = aggregate_release_status(release_rows)
    release_counts = release_status_counts(release_rows)
    release_summary = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generated_at_utc": generated_at,
        "real_release_evidence_supplied": real_release_evidence_supplied,
        "release_status": release_status,
        "status_counts": release_counts,
        "row_count": len(release_rows),
        "rows": list(release_rows.values()),
    }
    artifact_refs = sorted({
        ref
        for row in release_rows.values()
        for field in ["artifact_refs", "retention_refs"]
        for ref in row.get(field, []) if isinstance(ref, str) and ref
    })
    digest_refs = [
        digest for row in release_rows.values()
        for digest in row.get("subject_digests", [])
        if isinstance(digest, dict)
    ]
    write_json(
        root,
        output_dir / "release-upstream-run-manifest.json",
        {
            "artifact_name": "phase26-release-signing-upstream-evidence",
            "generated_at_utc": generated_at,
            "output_root": output_dir.as_posix(),
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "real_release_evidence_supplied": real_release_evidence_supplied,
            "release_status": release_status,
            "upstream_criteria_count": len(upstream_rows),
            "generated_artifacts": GENERATED_ARTIFACTS,
        },
    )
    write_json(root, output_dir / "normalized-release-evidence-summary.json",
               release_summary)
    write_json(root, output_dir / "upstream-result-row-table.json",
               {"rows": upstream_rows})
    write_json(
        root,
        output_dir / "upstream-result-manifest.json",
        {
            "generated_at_utc": generated_at,
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "rows": upstream_rows,
            "source_contract": PHASE18_CONTRACT.as_posix(),
        },
    )
    write_json(
        root,
        output_dir / "redaction-provenance-summary.json",
        {
            "generated_at_utc": generated_at,
            "phase": PHASE,
            "redaction_status": "passed",
            "retained_private_key_material": False,
            "retained_raw_payloads": False,
            "retained_credentials": False,
            "signing_identity_mode": "reference-only",
        },
    )
    write_json(
        root,
        output_dir / "artifact-reference-summary.json",
        {
            "artifact_refs": artifact_refs,
            "digest_refs": digest_refs,
            "generated_at_utc": generated_at,
            "phase": PHASE,
            "real_release_evidence_supplied": real_release_evidence_supplied,
        },
    )
    write_operator_template(root, output_dir, phase20_contract)
    write_contract_snapshots(root, output_dir)


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in [CONTRACT_MANIFEST, PHASE20_RELEASE_INPUT_TEMPLATE]:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_field_names(json.loads(text), path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


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
                'name = "phase26_release_signing_upstream_evidence_docs"',
                'name = "phase26_verify"',
                'actual = "//tools/bazel:phase26_verify"',
                'name = "phase26_verify_tests"',
                'actual = "//tools/bazel:phase26_verify_tests"',
                *[f'"{doc}"' for doc in PHASE26_DOCS],
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase26_source_ref_manifests"',
                'name = "phase26_verify"',
                'name = "phase26_verify_tests"',
                "phase26_release_signing_upstream_evidence.py",
                "phase26_release_signing_upstream_evidence_test.py",
                "phase26_release_signing_upstream_evidence_contract.json",
                "//:phase26_release_signing_upstream_evidence_docs",
                *[
                    f'"{manifest}"'
                    for manifest in PHASE26_SOURCE_REF_MANIFESTS
                ],
            ],
        ))
    try:
        workflow_text = read_text(root, Path("tools/bazel/rust_workflow.sh"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        verify_commands = shell_case_commands(workflow_text, "phase26_verify")
        test_commands = shell_case_commands(workflow_text,
                                            "phase26_verify_tests")
        if verify_commands is None:
            errors.append(
                "tools/bazel/rust_workflow.sh phase26_verify case arm missing")
        else:
            errors.extend(
                missing_required_items(
                    "tools/bazel/rust_workflow.sh phase26_verify case arm",
                    verify_commands, PHASE26_VERIFY_COMMANDS))
            errors.extend(
                check_command_order(
                    "tools/bazel/rust_workflow.sh phase26_verify case arm",
                    verify_commands,
                    PHASE26_VERIFY_COMMANDS[0],
                    PHASE26_VERIFY_COMMANDS[1],
                    "must run --wiring-only before --quick",
                ))
        if test_commands is None:
            errors.append(
                "tools/bazel/rust_workflow.sh phase26_verify_tests case arm missing"
            )
        else:
            errors.extend(
                missing_required_items(
                    "tools/bazel/rust_workflow.sh phase26_verify_tests case arm",
                    test_commands, [PHASE26_TEST_COMMAND]))
    try:
        just_text = read_text(root, Path("justfile"))
    except VerificationError as error:
        errors.append(str(error))
    else:
        just_commands = just_recipe_commands(just_text, "phase26-verify")
        test_line = "bazel run //tools/bazel:phase26_verify_tests"
        verify_line = "bazel run //tools/bazel:phase26_verify"
        if just_commands is None:
            errors.append("justfile phase26-verify recipe missing")
        else:
            errors.extend(
                missing_required_items("justfile phase26-verify recipe",
                                       just_commands,
                                       [test_line, verify_line]))
            errors.extend(
                check_command_order(
                    "justfile phase26-verify recipe",
                    just_commands,
                    test_line,
                    verify_line,
                    "must run tests before verifier",
                ))
    if errors:
        raise VerificationError("\n".join(errors))


def run_quick(
    root: Path,
    output_dir: Path,
    maybe_release_input: str | None,
    maybe_upstream_paths: dict[str, str | None],
) -> None:
    check_contract(root)
    check_security(root)
    release_rows = validate_release_input(root, maybe_release_input)
    relative_output_dir = reset_output_root(root, output_dir)
    write_retained_outputs(root, relative_output_dir, release_rows,
                           maybe_release_input is not None,
                           maybe_upstream_paths)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=
        "Validate Phase 26 release signing and upstream result evidence")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 26 contract")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="scan checked-in Phase 26 evidence inputs")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel and just workflow wiring")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="validate quick Phase 26 inputs and output containment")
    parser.add_argument("--release-input",
                        help="optional sanitized release-manager input JSON")
    parser.add_argument("--phase23-simulator-row",
                        help="optional Phase 23 upstream simulator row JSON")
    parser.add_argument(
        "--phase24-hardware-media-safety-row",
        help="optional Phase 24 upstream hardware/media/safety row JSON")
    parser.add_argument(
        "--phase25-live-service-row",
        help="optional Phase 25 upstream live-service row JSON")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 26 evidence output directory")
    args = parser.parse_args()
    selected_modes = [
        args.contract_only, args.security_only, args.wiring_only, args.quick
    ]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.release_input and not args.quick:
        parser.error("--release-input is only valid with --quick")
    maybe_upstream_paths = {
        "phase23_simulator_row": args.phase23_simulator_row,
        "phase24_hardware_media_safety_row":
        args.phase24_hardware_media_safety_row,
        "phase25_live_service_row": args.phase25_live_service_row,
    }
    if any(maybe_upstream_paths.values()) and not args.quick:
        parser.error(
            "Phase 23, Phase 24, and Phase 25 upstream row inputs are only valid with --quick"
        )
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 26 release signing upstream evidence contract passed")
        elif args.security_only:
            check_contract(ROOT)
            check_security(ROOT)
            print(
                "Phase 26 release signing upstream evidence security scan passed"
            )
        elif args.wiring_only:
            check_wiring(ROOT)
        else:
            run_quick(ROOT, Path(args.output_dir), args.release_input,
                      maybe_upstream_paths)
            print(
                "Phase 26 release signing upstream evidence quick validation passed"
            )
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
