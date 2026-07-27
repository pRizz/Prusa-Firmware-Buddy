from __future__ import annotations


def validate_installed_full_bundle(output: Path) -> None:
    validate_generated_outputs(output)
    try:
        decision = json.loads(
            (output / "cutover-decision.json").read_text(encoding="utf-8"))
        route = json.loads(
            (output / "next-milestone-route.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError) as error:
        raise VerificationError(
            "Phase 35 installed decision is unreadable") from error
    verdict = decision.get("cutover_verdict")
    follow_up_scope = route.get("follow_up_scope")
    if verdict not in {"approved", "blocked", "approved-with-exceptions"
                       } or not isinstance(follow_up_scope, list):
        raise VerificationError(
            "Phase 35 installed verdict or route is invalid")
    if route != build_route(str(verdict), follow_up_scope):
        raise VerificationError(
            "Phase 35 installed route contradicts its verdict")
    validation_state = decision.get("demotion_decision_validation_state")
    decision_state = decision.get("demotion_decision_state")
    gate_state = decision.get("demotion_gate_state")
    gate_reasons = decision.get("demotion_gate_reason_codes")
    if (validation_state not in {
            "missing", "valid", "invalid", "malformed", "stale",
            "lifecycle-mismatched"
    } or decision_state not in {"missing", "approve", "reject"}
            or gate_state not in {"blocked", "open"}
            or not isinstance(gate_reasons, list)
            or (gate_state == "open" and
                (validation_state != "valid" or decision_state != "approve"
                 or gate_reasons))):
        raise VerificationError(
            "Phase 35 installed demotion projection is invalid")


def write_bundle(
    root: Path,
    relative_output: Path,
    contract: dict[str, Any],
    phase34_contract: dict[str, Any],
    phase34_manifest: dict[str, Any],
    source: dict[str, Any],
    *,
    staging_output: Path | None = None,
) -> None:
    output = staging_output or root / relative_output
    reset_output(output)
    expected_links = derive_audit_links(audit_sources_from_bundle(source))
    index_links = [dict(link) for link in expected_links]
    link_reasons = sorted(
        set(validate_audit_links(expected_links, index_links))
        | set(validate_resolved_audit_links(root, index_links)))
    ledger_rows = source["ledger"]["rows"]
    readiness_state = str(source["packet"].get("readiness_state") or "blocked")
    upstream_reasons = cutover_reason_codes(readiness_state, ledger_rows)
    reason_map = {
        "required-row-missing": "coverage-incomplete",
        "duplicate-row": "source-artifact-duplicate",
        "dangling-row-ref": "source-ref-failed",
        "redaction-failed": "redaction-failed",
        "source-ref-failed": "source-ref-failed",
        "secret-tainted": "secret-tainted",
        "lifecycle-mismatched": "source-artifact-lifecycle-mismatched",
        "unsafe-ref": "unsafe-ref",
        "unknown-classification": "unknown-input",
        "underclassified": "underclassified",
        "exception-uncovered": "exception-invalid",
        "readiness-input-invalid": "readiness-blocked",
    }
    reasons = sorted({
        reason_map.get(reason, "readiness-blocked")
        for reason in upstream_reasons
    } | set(link_reasons))
    active_ids = active_exception_ids_from_ledger(ledger_rows)
    active_exceptions = [
        row for row in source["exceptions"]
        if row.get("decision_id") in active_ids
    ]
    verdict = evaluate_verdict({
        "readiness_state": readiness_state,
        "reason_codes": reasons,
        "active_exception_ids": active_ids,
        "exceptions": active_exceptions,
    })
    if verdict["cutover_verdict"] == "approved":
        scope, scope_reasons = [], []
    else:
        scope, scope_reasons = build_repair_scope(
            source["blockers"],
            ledger_rows,
            source["exceptions"],
            source["residuals"],
        )
    final_reasons = sorted(set(verdict["reason_codes"]) | set(scope_reasons))
    if final_reasons:
        verdict["cutover_verdict"] = "blocked"
        verdict["reason_codes"] = final_reasons
    route = build_route(verdict["cutover_verdict"], scope)
    demotion = project_demotion(source["demotion_handoff"],
                                source["normalized"], source["dry_run"])
    counts = {
        kind: sum(link["kind"] == kind for link in index_links)
        for kind in AUDIT_KINDS
    }
    blocker_ids = sorted(
        str(row.get("row_id")) for row in ledger_rows
        if row.get("row_id") and row.get("readiness_effect") == "blocked")
    decision = {
        "artifact_name": "phase35-cutover-decision",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_ids": REQUIREMENTS,
        "cutover_verdict": verdict["cutover_verdict"],
        "reason_codes": verdict["reason_codes"],
        "readiness_state": readiness_state,
        "readiness_result_ref":
        "build/ci-evidence/phase34/final-readiness-packet.json",
        "active_exception_ids": verdict["active_exception_ids"],
        "blocker_ids": blocker_ids,
        "audit_link_index_ref":
        "build/ci-evidence/phase35/cutover-audit-link-index.json",
        "audit_link_counts_by_kind": counts,
        **demotion,
        "route_ref": "build/ci-evidence/phase35/next-milestone-route.json",
        "raw_evidence_consumed": False,
    }
    index = {
        "artifact_name": "phase35-cutover-audit-link-index",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "link_count": len(index_links),
        "counts_by_kind": counts,
        "links": index_links,
    }
    manifest = {
        "artifact_name": "phase35-cutover-decision-artifact",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generated_at_utc": utc_now(),
        "output_root": relative_output.as_posix(),
        "generated_artifacts": GENERATED_ARTIFACTS,
        "source_manifest_ref":
        "build/ci-evidence/phase34/final-readiness-run-manifest.json",
        "raw_evidence_consumed": False,
    }
    write_json(output / "cutover-decision-run-manifest.json", manifest)
    write_json(output / "cutover-audit-link-index.json", index)
    write_json(output / "cutover-decision.json", decision)
    write_json(output / "next-milestone-route.json", route)
    (output / "redacted-cutover-decision-report.md").write_text(
        render_report(decision, route, index_links), encoding="utf-8")
    write_json(
        output /
        "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
        contract)
    write_json(
        output /
        "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
        phase34_contract)
    write_json(
        output /
        "contract-snapshots/phase34-final-readiness-run-manifest.json",
        phase34_manifest)
    validate_generated_outputs(output)


def run_quick(root: Path, phase34_arg: str, output_arg: str) -> None:
    output = validate_output_path(root, output_arg)
    canonical_output = root / output
    stage: Path | None = None
    try:
        phase34 = validate_source_path(root, phase34_arg, output)
        contract = load_contract(root)
        source, phase34_contract = load_bundle(root, phase34, contract)
        manifest = load_json(root,
                             phase34 / "final-readiness-run-manifest.json")
        stage = create_staging_directory(root, output)
        write_bundle(
            root,
            output,
            contract,
            phase34_contract,
            manifest,
            source,
            staging_output=stage,
        )
    except VerificationError as error:
        publish_authority_guard(root)
        discard_staging_directory(root, stage)
        reason_code = source_failure_reason(error)
        failure_stage = create_staging_directory(root, output)
        try:
            write_source_failure_bundle(output, failure_stage, reason_code)
            install_staged_bundle(
                root,
                failure_stage,
                canonical_output,
                validate_source_failure_bundle,
            )
        except VerificationError:
            if failure_stage.exists():
                discard_staging_directory(root, failure_stage)
            raise
        raise VerificationError("Phase 35 source validation failed",
                                reason_code) from error
    install_staged_bundle(
        root,
        stage,
        canonical_output,
        validate_installed_full_bundle,
    )
    run_security_scan(root, output.as_posix())


def run_security_scan(root: Path,
                      output_arg: str | Path = DEFAULT_OUTPUT) -> None:
    output = repo_relative(output_arg, "--output-dir")
    if output != DEFAULT_OUTPUT:
        raise VerificationError(
            f"--output-dir must be {DEFAULT_OUTPUT.as_posix()}")
    ensure_canonical_authority(root, output)
    full_output = root / output
    if not full_output.exists():
        print(f"no Phase 35 outputs to scan at {output.as_posix()}")
        return
    if full_output.is_symlink() or not full_output.is_dir():
        raise VerificationError(
            "Phase 35 output root contains a symlink escape")
    for artifact in GENERATED_ARTIFACTS:
        path = full_output / artifact
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            payload = json.loads(text)
            if artifact.startswith("contract-snapshots/"):
                if not isinstance(payload, dict):
                    raise VerificationError(
                        f"{artifact} must contain an object")
                validate_snapshot(artifact, payload)
            else:
                scan_security(payload, artifact)
        else:
            for pattern in FORBIDDEN_TEXT:
                if pattern.search(text):
                    raise VerificationError(
                        f"{artifact} contains forbidden text")
    print(f"Phase 35 security scan passed for {output.as_posix()}")


def shell_case_commands(text: str, name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{name})":
            continue
        commands = []
        for body in lines[index + 1:]:
            stripped = body.strip()
            if stripped == ";;":
                return commands
            if (stripped.startswith("python3 ")
                    or stripped == "run_phase38_coordinator"):
                commands.append(stripped)
    return None


def required_wiring_strings() -> dict[str, Any]:
    return {
        "tools_bazel": [
            "phase35_source_ref_manifests",
            "phase35_verify",
            "phase35_verify_tests",
            "manifests/phase31_final_evidence_intake_contract.json",
            "manifests/phase32_blocker_register_triage_contract.json",
            "manifests/phase33_maintainer_decision_inputs_contract.json",
            "manifests/phase34_final_readiness_demotion_dry_run_contract.json",
            "manifests/phase35_cutover_decision_artifact_contract.json",
            "phase35_cutover_decision_artifact.py",
            "phase35_cutover_decision_artifact_test.py",
            "//:phase35_cutover_decision_artifact_docs",
        ],
        "root_bazel": [
            "phase35_cutover_decision_artifact_docs",
            "phase35_verify",
            "phase35_verify_tests",
            ".planning/phases/35-cutover-decision-artifact/35-CONTEXT.md",
            ".planning/phases/35-cutover-decision-artifact/35-RESEARCH.md",
            ".planning/phases/35-cutover-decision-artifact/35-VALIDATION.md",
            ".planning/phases/35-cutover-decision-artifact/35-01-PLAN.md",
        ],
        "workflow": ["phase35_verify_tests)", "phase35_verify)"],
        "just": [
            "phase35-verify:",
            "bazel run //tools/bazel:phase35_verify_tests",
            "bazel run //tools/bazel:phase35_verify",
        ],
    }


def check_wiring(root: Path) -> None:
    expected = required_wiring_strings()
    files = {
        "tools_bazel": "tools/bazel/BUILD.bazel",
        "root_bazel": "BUILD.bazel",
        "workflow": "tools/bazel/rust_workflow.sh",
        "just": "justfile",
    }
    errors = []
    for group, path_text in files.items():
        path = root / path_text
        if not path.is_file():
            errors.append(f"missing required file: {path_text}")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in expected[group]:
            if snippet not in text:
                errors.append(f"{path_text} missing {snippet}")
    workflow_text = (root / files["workflow"]).read_text(encoding="utf-8")
    if shell_case_commands(workflow_text,
                           "phase35_verify") != PHASE35_VERIFY_COMMANDS:
        errors.append(
            "tools/bazel/rust_workflow.sh phase35_verify command order is invalid"
        )
    if shell_case_commands(workflow_text,
                           "phase35_verify_tests") != PHASE35_TEST_COMMANDS:
        errors.append(
            "tools/bazel/rust_workflow.sh phase35_verify_tests command is invalid"
        )
    just_lines = (root /
                  files["just"]).read_text(encoding="utf-8").splitlines()
    expected_just_lines = [
        expected["just"][0], f"    {expected['just'][1]}",
        f"    {expected['just'][2]}"
    ]
    if not any(just_lines[index:index + 3] == expected_just_lines
               for index in range(len(just_lines) - 2)):
        errors.append(
            "justfile phase35-verify recipe or command order is invalid")
    if errors:
        raise VerificationError("\n".join(errors))
    print("Phase 35 wiring passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the Phase 35 cutover decision artifact.")
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--phase34-output-dir",
                        default=DEFAULT_PHASE34_OUTPUT.as_posix())
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT.as_posix())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv or sys.argv[1:])
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
            run_quick(ROOT, args.phase34_output_dir, args.output_dir)
            print("Phase 35 cutover decision artifact quick validation passed")
            return 0
        raise VerificationError("no mode selected")
    except VerificationError as error:
        print(f"Phase 35 verification failed: {error.reason_code}",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
