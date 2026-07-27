#!/usr/bin/env python3
from __future__ import annotations

from phase25_execution_policy import *


def quick_rows(root: Path, output_dir: Path,
               phase16: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    logs_dir = root / output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    for scenario in phase16_scenarios(phase16):
        scenario_id = require_string(scenario, "id", "scenario")
        log_ref = output_dir / "logs" / f"{scenario_id}.log"
        allowed_source_statuses = require_list_of_strings(
            scenario, "allowed_statuses", "scenario")
        source_status = "pending-live-input" if "pending-live-input" in allowed_source_statuses else allowed_source_statuses[
            0]
        log_text = (
            f"phase: {PHASE}\n"
            f"scenario: {scenario_id}\n"
            "mode: quick-placeholder\n"
            "status: blocked\n"
            "reason: real live-service evidence input was not supplied.\n")
        sanitized_log, redaction_errors = sanitized_for_artifact(
            log_ref, log_text)
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        (root / log_ref).write_text(sanitized_log, encoding="utf-8")
        rows.append({
            "artifact_refs": [log_ref.as_posix()],
            "credential_boundary":
            require_string(scenario, "credential_boundary", "scenario"),
            "device":
            "quick-placeholder",
            "evidence_type":
            "source-contract-validation" if require_string(
                scenario, "proof_scope", "scenario") == "source-contract" else
            "controlled-service-observation",
            "exception_request":
            None,
            "firmware_build":
            "quick-placeholder",
            "live_requirement_ids":
            require_list_of_strings(scenario, "requirement_ids", "scenario"),
            "mode":
            require_string(scenario, "mode", "scenario"),
            "operator":
            "quick-placeholder",
            "phase16_source_contract_refs":
            require_list_of_strings(scenario, "source_contract_refs",
                                    "scenario"),
            "proof_scope":
            require_string(scenario, "proof_scope", "scenario"),
            "redaction_status":
            "passed",
            "redaction_summary":
            "quick placeholder retained no service secrets, credentials, payloads, or raw dumps",
            "requirement_ids": ["EVID-03"],
            "residual_non_live_gates":
            require_list_of_strings(scenario, "residual_non_live_gates",
                                    "scenario"),
            "residual_risk":
            "real live-service evidence input was not supplied",
            "retained_artifact_kind":
            require_string(scenario, "retained_artifact_kind", "scenario"),
            "runtime_metadata": {},
            "scenario_id":
            scenario_id,
            "service_surface":
            require_string(scenario, "service_surface", "scenario"),
            "source_ref_status":
            "passed",
            "source_status":
            source_status,
            "status":
            "blocked",
            "status_reason":
            "real live-service evidence input was not supplied",
            "timestamp":
            utc_now(),
            "title":
            require_string(scenario, "title", "scenario"),
            "unsupported_claims":
            require_list_of_strings(scenario, "unsupported_claims",
                                    "scenario"),
            "v1_requirement_ids":
            require_list_of_strings(scenario, "v1_requirement_ids",
                                    "scenario"),
        })
    return rows


def aggregate_status(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row["status"]) for row in rows}
    if "failed" in statuses:
        return "failed"
    if "blocked" in statuses:
        return "blocked"
    if "exception-requested" in statuses:
        return "exception-requested"
    return "passed"


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return counts


def write_snapshot(root: Path, output_dir: Path, snapshot: Path) -> None:
    snapshot_text = read_text(root, snapshot)
    snapshot_path = output_dir / "contract-snapshots" / snapshot.name
    snapshot_digest = hashlib.sha256(snapshot_text.encode("utf-8")).hexdigest()
    write_json(
        root,
        snapshot_path,
        {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "source_contract_ref": snapshot.as_posix(),
            "source_sha256": snapshot_digest,
            "snapshot_kind": "source-contract-hash",
        },
    )


def write_retained_outputs(
    root: Path,
    output_dir: Path,
    rows: list[dict[str, Any]],
    command_mode: str,
    real_input_supplied: bool,
    maybe_packet: dict[str, Any] | None = None,
) -> None:
    output_root = root / output_dir
    (output_root / "logs").mkdir(parents=True, exist_ok=True)
    (output_root / "artifact-summaries").mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    status_summary = status_counts(rows)
    run_status = aggregate_status(rows)
    live_requirement_ids = sorted({
        requirement
        for row in rows
        for requirement in row["live_requirement_ids"]
    })
    requirement_coverage = {
        "EVID-03": sorted(str(row["scenario_id"]) for row in rows),
        **{
            requirement:
            sorted(
                str(row["scenario_id"]) for row in rows if requirement in row["live_requirement_ids"])
            for requirement in live_requirement_ids
        },
    }
    manifest = {
        "artifact_name":
        "phase25-live-service-evidence-execution",
        "command_mode":
        command_mode,
        "evidence_run_id":
        maybe_packet.get("evidence_run_id", "") if maybe_packet else "",
        "firmware_identity":
        maybe_packet.get("firmware_identity", {}) if maybe_packet else {},
        "generated_at":
        generated_at,
        "operator":
        maybe_packet.get("operator", "") if maybe_packet else "",
        "output_root":
        output_dir.as_posix(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "real_live_service_evidence_supplied":
        real_input_supplied,
        "requirement_coverage":
        requirement_coverage,
        "scenario_count":
        len(rows),
        "scenarios":
        rows,
        "source_contract_ref":
        PHASE16_CONTRACT.as_posix(),
        "status":
        run_status,
        "status_counts":
        status_summary,
    }
    normalized = {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "real_live_service_evidence_supplied":
        real_input_supplied,
        "scenarios": [{
            "artifact_refs": row["artifact_refs"],
            "evidence_type": row["evidence_type"],
            "live_requirement_ids": row["live_requirement_ids"],
            "mode": row["mode"],
            "redaction_status": row["redaction_status"],
            "requirement_ids": row["requirement_ids"],
            "scenario_id": row["scenario_id"],
            "service_surface": row["service_surface"],
            "source_status": row["source_status"],
            "status": row["status"],
            "status_reason": row["status_reason"],
            "v1_requirement_ids": row["v1_requirement_ids"],
        } for row in rows],
    }
    redacted_summary = {
        "generated_at":
        generated_at,
        "phase":
        PHASE,
        "real_live_service_evidence_supplied":
        real_input_supplied,
        "scenario_status": [{
            "mode": row["mode"],
            "scenario_id": row["scenario_id"],
            "service_surface": row["service_surface"],
            "source_status": row["source_status"],
            "status": row["status"],
            "status_reason": row["status_reason"],
        } for row in rows],
        "status":
        run_status,
        "status_counts":
        status_summary,
        "unsupported_boundaries":
        sorted({claim
                for row in rows
                for claim in row["unsupported_claims"]}),
    }
    upstream_row = {
        "artifact_refs": [
            (output_dir / "normalized-live-service-results.json").as_posix(),
            (output_dir / "redacted-live-service-summary.json").as_posix(),
        ],
        "criterion_id":
        "final-live-service-evidence",
        "evidence_family":
        "live-service",
        "manifest_ref":
        (output_dir / "live-service-result-manifest.json").as_posix(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "real_live_service_evidence_supplied":
        real_input_supplied,
        "redaction_status":
        "passed",
        "requirement_ids": ["EVID-03"],
        "scenario_status_counts":
        status_summary,
        "source_ref_status":
        "passed",
        "status":
        run_status,
    }
    operator_template = {
        "live_service_evidence_packet": {
            "completed_at":
            "",
            "evidence_run_id":
            "",
            "firmware_identity": {
                "build_id": "",
                "firmware_basename": "",
            },
            "operator":
            "",
            "phase":
            PHASE,
            "phase_lifecycle_id":
            PHASE_LIFECYCLE_ID,
            "scenario_results": [{
                "artifact_refs": [],
                "device": "",
                "evidence_type": "",
                "firmware_build": "",
                "mode": row["mode"],
                "operator": "",
                "redaction_status": "",
                "redaction_summary": "",
                "residual_risk": "",
                "scenario_id": row["scenario_id"],
                "service_surface": row["service_surface"],
                "source_ref_status": "",
                "source_status": "",
                "status": "",
                "status_reason": "",
                "timestamp": "",
            } for row in rows],
            "source_contract_ref":
            PHASE16_CONTRACT.as_posix(),
            "started_at":
            "",
        }
    }
    artifact_summary = {
        "allowed_artifact_roots":
        [DEFAULT_OUTPUT_DIR.as_posix() + "/", "external://phase25/"],
        "generated_at":
        generated_at,
        "phase":
        PHASE,
        "retained_files": [
            (output_dir / "live-service-result-manifest.json").as_posix(),
            (output_dir / "normalized-live-service-results.json").as_posix(),
            (output_dir / "redacted-live-service-summary.json").as_posix(),
            (output_dir / "upstream-live-service-result-row.json").as_posix(),
            (output_dir / "operator-live-service-template.json").as_posix(),
        ],
        "scenario_count":
        len(rows),
        "status":
        run_status,
    }
    write_json(root, output_dir / "live-service-result-manifest.json",
               manifest)
    write_json(root, output_dir / "normalized-live-service-results.json",
               normalized)
    write_json(root, output_dir / "redacted-live-service-summary.json",
               redacted_summary)
    write_json(root, output_dir / "upstream-live-service-result-row.json",
               upstream_row)
    write_json(root, output_dir / "upstream-live-result-row.json",
               upstream_row)
    write_json(root, output_dir / "operator-live-service-template.json",
               operator_template)
    write_json(root, output_dir / "operator-evidence-input-template.json",
               operator_template)
    write_json(
        root, output_dir / "artifact-summaries" /
        "live-service-artifact-summary.json", artifact_summary)
    for snapshot in [CONTRACT_MANIFEST, PHASE16_CONTRACT]:
        write_snapshot(root, output_dir, snapshot)
    check_security(root)


def security_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    output_root = root / DEFAULT_OUTPUT_DIR
    if output_root.exists():
        paths.extend(
            path.relative_to(root) for path in sorted(output_root.rglob("*"))
            if path.is_file())
    return [path for path in paths if (root / path).exists()]


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in security_paths(root):
        try:
            reject_forbidden_text(path, read_text(root, path))
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
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase25_source_ref_manifests"',
                'name = "phase25_verify"',
                'name = "phase25_verify_tests"',
                "phase25_live_service_evidence_execution.py",
                "phase25_live_service_evidence_execution_test.py",
                "phase25_live_service_evidence_execution_contract.json",
                "//:phase25_live_service_evidence_execution_docs",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase25_live_service_evidence_execution_docs"',
                'name = "phase25_verify"',
                'name = "phase25_verify_tests"',
                ".planning/phases/25-live-service-evidence-execution/25-01-PLAN.md",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase25_verify)",
                "python3 tools/bazel/phase25_live_service_evidence_execution.py --wiring-only",
                "python3 tools/bazel/phase25_live_service_evidence_execution.py --quick --output-dir build/ci-evidence/phase25",
                "phase25_verify_tests)",
                "python3 tools/bazel/phase25_live_service_evidence_execution_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase25-verify:",
                "bazel run //tools/bazel:phase25_verify_tests",
                "bazel run //tools/bazel:phase25_verify",
            ],
        ))
    if errors:
        raise VerificationError("\n".join(errors))


def reset_output_root(root: Path, output_dir: Path) -> Path:
    output_relative = require_repo_relative_under(output_dir,
                                                  DEFAULT_OUTPUT_DIR,
                                                  "--output-dir")
    output_root = root / output_relative
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    return output_relative


def run_or_raise(args: argparse.Namespace) -> None:
    root = ROOT
    contract, phase16 = check_contract(root)
    output_dir = Path(args.output_dir)
    if args.contract_only:
        return
    if args.security_only:
        check_security(root)
        return
    if args.wiring_only:
        check_wiring(root)
        return
    if args.quick:
        output_relative = reset_output_root(root, output_dir)
        rows = quick_rows(root, output_relative, phase16)
        write_retained_outputs(root, output_relative, rows,
                               "quick-placeholder", False)
        return
    if args.evidence_input:
        output_relative = reset_output_root(root, output_dir)
        packet, rows = load_evidence_rows(root, Path(args.evidence_input),
                                          phase16)
        write_retained_outputs(root, output_relative, rows, "evidence-input",
                               True, packet)
        return
    check_security(root)
    check_wiring(root)
    _ = contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Validate and retain Phase 25 live-service evidence execution results."
    )
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--evidence-input")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args()


def main() -> int:
    try:
        run_or_raise(parse_args())
    except VerificationError as error:
        print(
            f"Phase 25 live-service evidence execution verification failed:\n{error}",
            file=sys.stderr)
        return 1
    print("Phase 25 live-service evidence execution verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
