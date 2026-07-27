#!/usr/bin/env python3
from __future__ import annotations

from phase16_evidence_policy import *

SOURCE_REF_MANIFESTS = [
    "tools/bazel/manifests/phase9_connect_contracts.json",
    "tools/bazel/manifests/phase9_wui_contracts.json",
    "tools/bazel/manifests/phase9_network_service_contracts.json",
    "tools/bazel/manifests/phase9_transfer_contracts.json",
    "tools/bazel/manifests/phase9_network_concern_dispositions.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_parity_pyramid.json",
    "tools/bazel/manifests/phase11_reference_comparisons.json",
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/phase13_ci_evidence_contract.json",
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json",
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json",
]


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
            text = read_text(root, relative_path)
            reject_forbidden_text(relative_path, text)
        except UnicodeDecodeError as error:
            errors.append(
                f"{relative_path.as_posix()} is not UTF-8 text: {error}")
        except VerificationError as error:
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


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    phase16_manifest_srcs = [
        Path(path).relative_to("tools/bazel").as_posix()
        for path in SOURCE_REF_MANIFESTS
    ]
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase16_source_ref_manifests"',
                'name = "phase16_verify"',
                'name = "phase16_verify_tests"',
                "phase16_live_network_evidence.py",
                "phase16_live_network_evidence_test.py",
                "phase16_live_network_evidence_contract.json",
                ":phase16_source_ref_manifests",
                "//:phase16_live_network_evidence_docs",
                "//:phase11_cutover_evidence_docs",
                *phase16_manifest_srcs,
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase16_live_network_evidence_docs"',
                'name = "phase16_verify"',
                'name = "phase16_verify_tests"',
                ".planning/phases/16-live-network-and-transfer-qualification/16-CONTEXT.md",
                ".planning/phases/16-live-network-and-transfer-qualification/16-RESEARCH.md",
                ".planning/phases/16-live-network-and-transfer-qualification/16-VALIDATION.md",
                ".planning/phases/16-live-network-and-transfer-qualification/16-01-PLAN.md",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase16_verify)",
                "python3 tools/bazel/phase16_live_network_evidence.py --wiring-only",
                "python3 tools/bazel/phase16_live_network_evidence.py --quick",
                "phase16_verify_tests)",
                "python3 tools/bazel/phase16_live_network_evidence_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase16-verify:",
                "bazel run //tools/bazel:phase16_verify_tests",
                "bazel run //tools/bazel:phase16_verify",
            ],
        ))
    try:
        just_lines = [
            line.strip() for line in read_text(root, "justfile").splitlines()
        ]
        just_tests_line = "bazel run //tools/bazel:phase16_verify_tests"
        just_verify_line = "bazel run //tools/bazel:phase16_verify"
        if just_tests_line not in just_lines:
            errors.append(
                "justfile missing exact phase16_verify_tests recipe line")
        if just_verify_line not in just_lines:
            errors.append("justfile missing exact phase16_verify recipe line")
        if just_tests_line in just_lines and just_verify_line in just_lines:
            if just_lines.index(just_tests_line) > just_lines.index(
                    just_verify_line):
                errors.append(
                    "justfile phase16-verify must run tests before verifier")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def load_operator_evidence_path(
        root: Path, path: str | None) -> tuple[Path | None, list[Any] | None]:
    if not path:
        return None, None
    evidence_path = Path(path)
    full_path = evidence_path if evidence_path.is_absolute(
    ) else root / evidence_path
    if not full_path.exists():
        raise VerificationError(
            f"operator evidence file does not exist: {path}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(evidence_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"operator evidence is not valid JSON: {error}") from error
    if isinstance(data, list):
        return evidence_path, data
    if isinstance(data, dict):
        rows = data.get("evidence_rows")
        if isinstance(rows, list):
            return evidence_path, rows
    raise VerificationError(
        "operator evidence must contain an evidence_rows list or be a top-level list"
    )


def validate_artifact_refs(artifact_refs: Any, row_name: str) -> list[str]:
    if not isinstance(artifact_refs, list) or not artifact_refs:
        raise VerificationError(
            f"{row_name} artifact_refs must be a non-empty list")
    parsed_refs: list[str] = []
    for index, artifact_ref in enumerate(artifact_refs):
        ref_name = f"{row_name} artifact_refs[{index}]"
        if not isinstance(artifact_ref, str) or not artifact_ref:
            raise VerificationError(f"{ref_name} must be a non-empty string")
        if artifact_ref.startswith(("external://", "artifact://")):
            parsed_refs.append(artifact_ref)
            continue
        require_repo_relative_under(artifact_ref, DEFAULT_OUTPUT_DIR, ref_name)
        parsed_refs.append(artifact_ref)
    return parsed_refs


def validated_operator_rows(root: Path, contract: dict[str, Any],
                            path: str | None) -> dict[str, dict[str, Any]]:
    evidence_path, rows = load_operator_evidence_path(root, path)
    if rows is None:
        return {}
    schema = require_dict(contract, "operator_input_schema", "contract")
    allowed_results = set(
        require_list_of_strings(schema, "allowed_results",
                                "operator_input_schema"))
    scenarios_by_id = {
        scenario["id"]: scenario
        for scenario in contract_scenarios(contract)
    }
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"operator evidence row {index}"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        try:
            require_fields(row, REQUIRED_OPERATOR_FIELDS, row_name)
            row_text = json.dumps(row, sort_keys=True)
            reject_forbidden_text(evidence_path or Path("operator-evidence"),
                                  row_text)
            scenario_id = require_string(row, "scenario_id", row_name)
            result = require_string(row, "result", row_name)
            require_iso_8601_utc_timestamp(row, "timestamp", row_name)
            evidence_type = require_string(row, "evidence_type", row_name)
            service_surface = require_string(row, "service_surface", row_name)
            mode = require_string(row, "mode", row_name)
            if scenario_id not in scenarios_by_id:
                raise VerificationError(
                    f"{row_name} references unknown scenario: {scenario_id}")
            if scenario_id in parsed_rows:
                raise VerificationError(
                    f"{row_name} duplicates scenario evidence: {scenario_id}")
            if result not in allowed_results:
                raise VerificationError(
                    f"{row_name} uses unsupported result: {result}")
            scenario = scenarios_by_id[scenario_id]
            allowed_statuses = set(
                require_list_of_strings(scenario, "allowed_statuses",
                                        scenario_id))
            if result not in allowed_statuses:
                raise VerificationError(
                    f"{row_name} result {result} is not allowed for {scenario_id}"
                )
            if service_surface != scenario["service_surface"]:
                raise VerificationError(
                    f"{row_name} service_surface does not match {scenario_id}")
            if mode != scenario["mode"]:
                raise VerificationError(
                    f"{row_name} mode does not match {scenario_id}")
            if scenario[
                    "proof_scope"] == "live-service-observation" and result == "passed":
                if evidence_type not in LIVE_PASS_EVIDENCE_TYPES:
                    raise VerificationError(
                        f"{row_name} passed live evidence must be live or controlled-service evidence"
                    )
            artifact_refs = validate_artifact_refs(row["artifact_refs"],
                                                   row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue
        parsed = {field: row[field] for field in REQUIRED_OPERATOR_FIELDS}
        parsed["artifact_refs"] = artifact_refs
        parsed_rows[scenario_id] = parsed
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def write_json(root: Path, relative_path: Path, data: dict[str, Any]) -> None:
    full_path = root / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")


def default_status_for(scenario: dict[str, Any]) -> str:
    if scenario.get("proof_scope") == "source-contract":
        return "source-contract-passed"
    return "pending-live-input"


def scenario_result_row(
        scenario: dict[str, Any],
        maybe_operator_row: dict[str, Any] | None) -> dict[str, Any]:
    scenario_id = str(scenario["id"])
    status = default_status_for(scenario)
    artifact_refs = [str(scenario["expected_artifact_path"])]
    redaction_summary = "No operator evidence supplied; live/control-service evidence pending."
    residual_risk = "Awaiting approved live or controlled-service operator evidence."
    operator_metadata: dict[str, str] = {
        "device": "",
        "firmware_build": "",
        "operator": "",
        "timestamp": "",
        "evidence_type": "",
    }
    if scenario.get("proof_scope") == "source-contract":
        redaction_summary = "Source contract and redaction guard validation only."
        residual_risk = "Live/control-service rows still require operator evidence."
    if maybe_operator_row is not None:
        status = str(maybe_operator_row["result"])
        artifact_refs = [
            str(ref) for ref in maybe_operator_row["artifact_refs"]
        ]
        redaction_summary = str(maybe_operator_row["redaction_summary"])
        residual_risk = str(maybe_operator_row["residual_risk"])
        operator_metadata = {
            "device": str(maybe_operator_row["device"]),
            "firmware_build": str(maybe_operator_row["firmware_build"]),
            "operator": str(maybe_operator_row["operator"]),
            "timestamp": str(maybe_operator_row["timestamp"]),
            "evidence_type": str(maybe_operator_row["evidence_type"]),
        }
    return {
        "artifact_refs": artifact_refs,
        "credential_boundary": scenario["credential_boundary"],
        "id": scenario_id,
        "mode": scenario["mode"],
        "operator_metadata_present": maybe_operator_row is not None,
        "proof_scope": scenario["proof_scope"],
        "redaction_summary": redaction_summary,
        "requirement_ids": scenario["requirement_ids"],
        "residual_risk": residual_risk,
        "scenario_id": scenario_id,
        "service_surface": scenario["service_surface"],
        "source_contract_refs": scenario["source_contract_refs"],
        "source_doc_refs": scenario["source_doc_refs"],
        "status": status,
        "title": scenario["title"],
        "unsupported_claims": scenario["unsupported_claims"],
        "v1_requirement_ids": scenario["v1_requirement_ids"],
        **operator_metadata,
    }


def write_log(root: Path, output_dir: Path, result_row: dict[str,
                                                             Any]) -> None:
    log_path = output_dir / "logs" / f"{result_row['id']}.log"
    lines = [
        f"scenario_id={result_row['id']}",
        f"status={result_row['status']}",
        f"proof_scope={result_row['proof_scope']}",
        f"service_surface={result_row['service_surface']}",
        f"mode={result_row['mode']}",
        f"artifact_refs={','.join(result_row['artifact_refs'])}",
        f"redaction_summary={result_row['redaction_summary']}",
        f"residual_risk={result_row['residual_risk']}",
    ]
    if result_row["operator_metadata_present"]:
        lines.append("operator_evidence=accepted-redacted-reference-only")
    elif result_row["proof_scope"] == "source-contract":
        lines.append("operator_evidence=not-required-for-source-contract-row")
    else:
        lines.append(
            "operator_evidence=pending-live-or-controlled-service-input")
    full_path = root / log_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quick_artifacts(
    root: Path,
    contract: dict[str, Any],
    output_dir: Path,
    operator_rows: dict[str, dict[str, Any]],
) -> None:
    relative_output_dir = require_repo_relative_under(output_dir,
                                                      DEFAULT_OUTPUT_DIR,
                                                      "--output-dir")
    full_output_dir = contained_output_dir(root, relative_output_dir)
    if full_output_dir.exists():
        shutil.rmtree(full_output_dir)
    (full_output_dir / "logs").mkdir(parents=True)
    (full_output_dir / "source-contract-snapshots").mkdir(parents=True)

    scenarios = contract_scenarios(contract)
    result_rows = [
        scenario_result_row(scenario, operator_rows.get(str(scenario["id"])))
        for scenario in scenarios
    ]
    for row in result_rows:
        write_log(root, full_output_dir, row)

    status_counts: dict[str, int] = {}
    for row in result_rows:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    generated_at = datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")
    snapshot_path = relative_output_dir / "source-contract-snapshots" / CONTRACT_MANIFEST.name
    run_manifest = {
        "artifact_name":
        contract["artifact_name"],
        "command_mode":
        "quick",
        "generated_at":
        generated_at,
        "live_inputs_supplied":
        bool(operator_rows),
        "output_root":
        relative_output_dir.as_posix(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "requirement_coverage":
        sorted(REQUIRED_REQUIREMENT_IDS),
        "scenarios": [{
            "artifact_refs": row["artifact_refs"],
            "id": row["id"],
            "mode": row["mode"],
            "proof_scope": row["proof_scope"],
            "scenario_id": row["scenario_id"],
            "service_surface": row["service_surface"],
            "status": row["status"],
        } for row in result_rows],
        "source_contract_snapshot_path":
        snapshot_path.as_posix(),
        "status_counts":
        status_counts,
    }
    normalized_results = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "scenarios": result_rows,
    }
    redacted_summary = {
        "credential_boundaries": {
            row["id"]: row["credential_boundary"]
            for row in result_rows
        },
        "generated_at":
        generated_at,
        "operator_evidence_summary": {
            "accepted_rows": sorted(operator_rows),
            "count": len(operator_rows),
        },
        "pending_live_input_rows": [
            row["id"] for row in result_rows
            if row["status"] == "pending-live-input"
        ],
        "redaction_boundary":
        "Phase 16 retains only redacted summaries, operator metadata, source snapshots, and artifact references.",
        "scenario_status": {
            row["id"]: row["status"]
            for row in result_rows
        },
        "status_counts":
        status_counts,
        "unsupported_claims": {
            row["id"]: row["unsupported_claims"]
            for row in result_rows
        },
    }
    write_json(root, full_output_dir / "run-manifest.json", run_manifest)
    write_json(root, full_output_dir / "normalized-scenario-results.json",
               normalized_results)
    write_json(root, full_output_dir / "redacted-network-summary.json",
               redacted_summary)
    write_json(
        root,
        full_output_dir / "operator-evidence-input.json",
        {"evidence_rows": list(operator_rows.values())},
    )
    shutil.copy2(
        root / CONTRACT_MANIFEST,
        full_output_dir / "source-contract-snapshots" / CONTRACT_MANIFEST.name)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 16 live network evidence contract")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 16 evidence contract")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="scan Phase 16 contract and generated artifacts")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel and just workflow wiring")
    parser.add_argument("--quick",
                        action="store_true",
                        help="write deterministic Phase 16 evidence artifacts")
    parser.add_argument("--operator-evidence",
                        help="optional operator evidence JSON input")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 16 evidence output directory")
    args = parser.parse_args()
    selected_modes = [
        args.contract_only, args.security_only, args.wiring_only, args.quick
    ]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.operator_evidence and not args.quick:
        parser.error("--operator-evidence is only valid with --quick")
    output_dir = Path(args.output_dir)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 16 live network evidence contract passed")
        elif args.security_only:
            check_security(ROOT, output_dir)
            print("Phase 16 live network evidence security scan passed")
        elif args.quick:
            contract = check_contract(ROOT)
            operator_rows = validated_operator_rows(ROOT, contract,
                                                    args.operator_evidence)
            write_quick_artifacts(ROOT, contract, output_dir, operator_rows)
            check_security(ROOT, output_dir)
            print(
                f"Phase 16 live network evidence written to {output_dir.as_posix()}"
            )
        else:
            check_wiring(ROOT)
            print("Phase 16 live network evidence wiring passed")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
