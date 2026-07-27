#!/usr/bin/env python3
from __future__ import annotations

from phase28_readiness_policy import *


def demotion_decision_input_template() -> dict[str, Any]:
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "demotion_authorization": "blocked",
        "approver": "maintainer-name",
        "approver_role": "release-maintainer",
        "decision_timestamp": "2026-06-25T00:00:00Z",
        "rationale":
        "Reference demotion remains blocked until final readiness is unblocked and maintainer approval is supplied.",
        "scope": "supported-printer-release-surface",
        "evidence_refs": [],
    }


def artifact_reference_summary(
        output_dir_relative: Path, phase26_path: Path, phase27_path: Path,
        phase27_bundle: dict[str, Any]) -> dict[str, Any]:
    refs = [{
        "path": (output_dir_relative / artifact).as_posix(),
        "purpose": "phase28-final-readiness-packet",
    } for artifact in GENERATED_ARTIFACTS]
    phase27_refs = phase27_bundle["artifact_refs"].get("artifact_refs", [])
    if not isinstance(phase27_refs, list):
        phase27_refs = []
    return {
        "phase26_upstream_rows": phase26_path.as_posix(),
        "phase27_handoff": phase27_path.as_posix(),
        "source_contract_refs": [{
            "path": path
        } for path in SOURCE_CONTRACTS],
        "phase27_artifact_refs": phase27_refs,
        "generated_artifact_refs": refs,
    }


def redacted_report_text(packet: dict[str, Any]) -> str:
    lines = [
        "# Phase 28 Final Readiness Packet",
        "",
        "Review material only; machine-readable packet rows and explicit maintainer input determine gate status.",
        "",
        f"phase: {packet['phase']}",
        f"phase_lifecycle_id: {packet['phase_lifecycle_id']}",
        f"final_readiness_status: {packet['final_readiness_status']}",
        f"reference_demotion_authorization: {packet['reference_demotion_authorization']}",
        f"real_maintainer_demotion_approval_supplied: {str(packet['real_maintainer_demotion_approval_supplied']).lower()}",
        "",
        "## Criteria",
    ]
    for row in packet["criteria"]:
        lines.append(
            f"- {row['criterion_id']} -> {row['readiness_effect']} (phase26={row['phase26_status']}, phase27={row['phase27_status']})"
        )
        for reason in row["hard_failure_reasons"]:
            lines.append(f"  - hard blocker: {reason}")
    return "\n".join(lines) + "\n"


def generated_artifacts_to_scan(output_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for artifact in GENERATED_ARTIFACTS:
        path = output_dir / artifact
        if path.exists():
            paths.append(path)
    return paths


def validate_generated_outputs(root: Path, output_dir: Path) -> None:
    packet_path = output_dir / "final-readiness-packet.json"
    if not packet_path.exists():
        return
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(packet, dict):
        raise VerificationError(
            "final-readiness-packet.json must contain an object")
    for field in [
            "final_readiness_status",
            "reference_demotion_authorization",
            "criteria",
            "requirements",
            "real_maintainer_demotion_approval_supplied",
    ]:
        if field not in packet:
            raise VerificationError(
                f"final-readiness-packet.json missing top-level field: {field}"
            )
    if packet["reference_demotion_authorization"] == "approved":
        if packet["final_readiness_status"] != "unblocked":
            raise VerificationError(
                "generated packet cannot approve reference demotion while final readiness is blocked"
            )
        if packet["real_maintainer_demotion_approval_supplied"] is not True:
            raise VerificationError(
                "generated packet approved authorization requires maintainer approval flag"
            )
    criteria = packet.get("criteria")
    canonical_criteria = phase18_canonical_criteria(root)
    if not isinstance(criteria, list) or {
            row.get("criterion_id")
            for row in criteria if isinstance(row, dict)
    } != set(canonical_criteria):
        raise VerificationError(
            "final-readiness-packet.json criteria must cover all canonical Phase 18 criteria"
        )
    record_path = output_dir / "reference-demotion-authorization-record.json"
    if record_path.exists():
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and record.get(
                "reference_demotion_authorization") == "approved":
            if packet.get("reference_demotion_authorization") != "approved":
                raise VerificationError(
                    "authorization record and packet disagree")
            if record.get(
                    "real_maintainer_demotion_approval_supplied") is not True:
                raise VerificationError(
                    "authorization record approved status requires maintainer approval flag"
                )
    for path in generated_artifacts_to_scan(output_dir):
        relative_path = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        reject_forbidden_text(relative_path, text)
        if path.suffix == ".json":
            try:
                reject_forbidden_json_fields(json.loads(text),
                                             relative_path.as_posix())
            except json.JSONDecodeError as error:
                raise VerificationError(
                    f"{relative_path.as_posix()} is not valid JSON: {error}"
                ) from error


def run_security_scan(
    root: Path,
    maybe_demotion_decision_input: str | None = None,
    output_dir: Path | None = None,
) -> None:
    errors: list[str] = []
    paths_to_scan = [
        CONTRACT_MANIFEST, PHASE18_CONTRACT, PHASE26_CONTRACT, PHASE27_CONTRACT
    ]
    for path in paths_to_scan:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_json_fields(load_json(root, path),
                                         path.as_posix())
        except VerificationError as error:
            errors.append(str(error))
    scan_dir = output_dir or (root / DEFAULT_OUTPUT_DIR)
    if maybe_demotion_decision_input:
        try:
            maybe_status = None
            packet_path = scan_dir / "final-readiness-packet.json"
            if packet_path.exists():
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if isinstance(packet, dict) and isinstance(
                        packet.get("final_readiness_status"), str):
                    maybe_status = packet["final_readiness_status"]
            load_demotion_decision_input(
                root,
                maybe_demotion_decision_input,
                maybe_final_readiness_status=maybe_status)
        except VerificationError as error:
            errors.append(str(error))
    if scan_dir.exists():
        try:
            validate_generated_outputs(root, scan_dir)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def copy_snapshot(root: Path, output_dir: Path, source: Path,
                  target: str) -> None:
    source_path = root / source
    if not source_path.exists():
        raise VerificationError(
            f"missing snapshot source: {source.as_posix()}")
    target_path = output_dir / target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)


def write_phase28_outputs(
    root: Path,
    contract: dict[str, Any],
    phase26_path: Path,
    phase26_rows: list[dict[str, Any]],
    phase27_path: Path,
    phase27_handoff: dict[str, Any],
    phase27_bundle: dict[str, Any],
    demotion_decision_input: dict[str, Any] | None,
    output_dir_arg: str,
) -> dict[str, Any]:
    output_dir = contained_output_dir(root, output_dir_arg)
    criteria = normalize_readiness_criteria(phase26_rows, phase27_bundle,
                                            phase18_canonical_criteria(root))
    readiness_status = final_readiness_status(criteria)
    if demotion_decision_input is not None and demotion_decision_input[
            "demotion_authorization"] == "approved" and readiness_status != "unblocked":
        raise VerificationError(
            "approved reference demotion requires final_readiness_status unblocked"
        )
    demotion_record = demotion_authorization_record(demotion_decision_input,
                                                    readiness_status)
    apply_demotion_authorization_to_criteria(criteria, demotion_record)
    blockers = build_blocker_rows(criteria, readiness_status, demotion_record)
    output_dir_relative = output_dir.relative_to(root)
    generated_at_utc = utc_now()
    packet = {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "artifact_name":
        contract["artifact_name"],
        "generated_at_utc":
        generated_at_utc,
        "final_readiness_status":
        readiness_status,
        "reference_demotion_authorization":
        demotion_record["reference_demotion_authorization"],
        "real_maintainer_demotion_approval_supplied":
        demotion_record["real_maintainer_demotion_approval_supplied"],
        "requirements":
        contract["requirements"],
        "criteria":
        criteria,
        "source_inputs": {
            "phase26_upstream_rows": phase26_path.as_posix(),
            "phase27_handoff": phase27_path.as_posix(),
        },
        "phase27_handoff":
        phase27_handoff,
    }
    run_manifest = {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "artifact_name":
        contract["artifact_name"],
        "generated_at_utc":
        generated_at_utc,
        "output_root":
        output_dir_relative.as_posix(),
        "phase26_upstream_rows":
        phase26_path.as_posix(),
        "phase27_handoff":
        phase27_path.as_posix(),
        "demotion_decision_input_supplied":
        demotion_decision_input is not None,
        "final_readiness_status":
        readiness_status,
        "reference_demotion_authorization":
        demotion_record["reference_demotion_authorization"],
        "real_maintainer_demotion_approval_supplied":
        demotion_record["real_maintainer_demotion_approval_supplied"],
        "generated_artifacts": [(output_dir_relative / artifact).as_posix()
                                for artifact in GENERATED_ARTIFACTS],
    }
    exception_rows = [
        {
            "criterion_id": row["criterion_id"],
            "exception_state": row["exception_state"],
            "exception_refs": row["exception_refs"],
            "exception_metadata": row["exception_metadata"],
            "residual_risk": row["residual_risk"],
            "residual_risk_refs": row["residual_risk_refs"],
        } for row in criteria
        if row["exception_state"] != "none" or row["residual_risk_refs"]
    ]
    reset_output_root(output_dir)
    write_json(output_dir / "final-readiness-run-manifest.json", run_manifest)
    write_json(output_dir / "final-readiness-packet.json", packet)
    write_json(output_dir / "normalized-readiness-criteria-table.json",
               {"rows": criteria})
    write_json(
        output_dir / "blocker-summary.json",
        {
            "final_readiness_status":
            readiness_status,
            "reference_demotion_authorization":
            demotion_record["reference_demotion_authorization"],
            "blockers":
            blockers,
        },
    )
    write_json(output_dir / "exception-residual-risk-summary.json",
               {"rows": exception_rows})
    write_json(output_dir / "reference-demotion-authorization-record.json",
               demotion_record)
    write_json(output_dir / "demotion-decision-input-template.json",
               demotion_decision_input_template())
    (output_dir / "redacted-readiness-report.md").write_text(
        redacted_report_text(packet), encoding="utf-8")
    write_json(
        output_dir / "artifact-reference-summary.json",
        artifact_reference_summary(output_dir_relative, phase26_path,
                                   phase27_path, phase27_bundle))
    copy_snapshot(root, output_dir, PHASE18_CONTRACT,
                  "contract-snapshots/phase18_cutover_review_contract.json")
    copy_snapshot(
        root, output_dir, PHASE26_CONTRACT,
        "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json"
    )
    copy_snapshot(
        root, output_dir, PHASE27_CONTRACT,
        "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json"
    )
    copy_snapshot(root, output_dir, phase26_path,
                  "contract-snapshots/phase26-upstream-result-row-table.json")
    copy_snapshot(root, output_dir, phase27_path,
                  "contract-snapshots/phase27-phase28-handoff-manifest.json")
    run_security_scan(root, output_dir=output_dir)
    return run_manifest


def shell_case_commands(text: str, case_name: str) -> list[str]:
    case_index = text.find(f"  {case_name})")
    if case_index == -1:
        return []
    commands: list[str] = []
    for line in text[case_index:].splitlines()[1:]:
        if line.startswith("  ") and not line.startswith(
                "    ") and line.strip().endswith(")"):
            break
        stripped = line.strip()
        if stripped.startswith("python3 "):
            commands.append(stripped)
    return commands


def just_recipe_commands(text: str, recipe_name: str) -> list[str]:
    recipe_index = text.find(f"{recipe_name}:")
    if recipe_index == -1:
        return []
    next_recipe = text.find("\n\n", recipe_index)
    body = text[recipe_index:] if next_recipe == -1 else text[
        recipe_index:next_recipe]
    return [line.strip() for line in body.splitlines()[1:] if line.strip()]


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    for path, required_values in WIRING_REQUIRED_TEXT.items():
        try:
            text = read_text(root, path)
        except VerificationError as error:
            errors.append(str(error))
            continue
        for required_text in required_values:
            if required_text not in text:
                errors.append(
                    f"{path.as_posix()} missing required wiring text: {required_text}"
                )
    try:
        workflow = read_text(root, "tools/bazel/rust_workflow.sh")
        commands = shell_case_commands(workflow, "phase28_verify")
        expected = [
            "python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only",
            PHASE26_QUICK_COMMAND,
            PHASE27_QUICK_COMMAND,
            ("python3 tools/bazel/phase28_final_readiness_packet.py --quick "
             "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
             "--phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json "
             "--output-dir build/ci-evidence/phase28"),
        ]
        if commands != expected:
            errors.append(
                "tools/bazel/rust_workflow.sh phase28_verify command order does not match Phase 28 plan"
            )
        if shell_case_commands(workflow, "phase28_verify_tests") != [
                "python3 tools/bazel/phase28_final_readiness_packet_test.py"
        ]:
            errors.append(
                "tools/bazel/rust_workflow.sh phase28_verify_tests command is invalid"
            )
    except VerificationError as error:
        errors.append(str(error))
    try:
        just_text = read_text(root, "justfile")
        commands = just_recipe_commands(just_text, "phase28-verify")
        expected = [
            "bazel run //tools/bazel:phase28_verify_tests",
            "bazel run //tools/bazel:phase28_verify",
        ]
        if commands != expected:
            errors.append(
                "justfile phase28-verify must run tests before verifier")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and generate the Phase 28 final readiness packet."
    )
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate only the Phase 28 contract")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="write deterministic Phase 28 readiness packet artifacts")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="scan Phase 28 inputs and generated artifacts")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel, workflow, and just wiring")
    parser.add_argument("--phase26-upstream-rows",
                        default=DEFAULT_PHASE26_ROWS.as_posix())
    parser.add_argument("--phase27-handoff",
                        default=DEFAULT_PHASE27_HANDOFF.as_posix())
    parser.add_argument("--demotion-decision-input")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        contract = check_contract(ROOT)
        if args.security_only:
            output_dir = contained_output_dir(ROOT, args.output_dir)
            run_security_scan(ROOT, args.demotion_decision_input, output_dir)
            print("Phase 28 security scan passed")
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            print("Phase 28 wiring passed")
            return 0
        if args.quick:
            phase26_path, phase26_rows = load_phase26_rows(
                ROOT, args.phase26_upstream_rows)
            phase27_path, handoff, phase27_bundle = load_phase27_bundle(
                ROOT, args.phase27_handoff)
            preliminary_criteria = normalize_readiness_criteria(
                phase26_rows, phase27_bundle, phase18_canonical_criteria(ROOT))
            preliminary_status = final_readiness_status(preliminary_criteria)
            decision_input = load_demotion_decision_input(
                ROOT, args.demotion_decision_input, preliminary_status)
            run_manifest = write_phase28_outputs(
                ROOT,
                contract,
                phase26_path,
                phase26_rows,
                phase27_path,
                handoff,
                phase27_bundle,
                decision_input,
                args.output_dir,
            )
            print(
                "Phase 28 final readiness packet quick validation passed; "
                f"final_readiness_status={run_manifest['final_readiness_status']} "
                f"reference_demotion_authorization={run_manifest['reference_demotion_authorization']}"
            )
            return 0
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Phase 28 final readiness packet contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
