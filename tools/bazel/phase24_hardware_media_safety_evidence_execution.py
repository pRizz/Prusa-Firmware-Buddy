#!/usr/bin/env python3
from __future__ import annotations

from phase24_execution_policy import *


def quick_rows(root: Path, output_dir: Path,
               phase15: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    logs_dir = root / output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    for scenario in phase15_scenarios(phase15):
        scenario_id = require_string(scenario, "id", "scenario")
        log_ref = output_dir / "logs" / f"{scenario_id}.log"
        allowed_source_statuses = require_list_of_strings(
            scenario, "allowed_statuses", "scenario")
        source_status = (
            "blocked-hardware-unavailable" if "blocked-hardware-unavailable"
            in allowed_source_statuses else "failed" if "failed"
            in allowed_source_statuses else allowed_source_statuses[0])
        log_text = (
            f"phase: {PHASE}\n"
            f"scenario: {scenario_id}\n"
            "mode: quick-placeholder\n"
            "status: blocked\n"
            "reason: real hardware/media/safety evidence input was not supplied.\n"
        )
        sanitized_log, redaction_errors = sanitized_for_artifact(
            log_ref, log_text)
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        (root / log_ref).write_text(sanitized_log, encoding="utf-8")
        rows.append({
            "artifact_refs": [log_ref.as_posix()],
            "auxiliary_surface":
            require_string(scenario, "auxiliary_surface", "scenario"),
            "board":
            require_string(scenario, "board", "scenario"),
            "device":
            "quick-placeholder",
            "exception_request":
            None,
            "failure_observations":
            "real hardware/media/safety evidence input was not supplied",
            "firmware_build":
            "quick-placeholder",
            "hardware_requirement_ids":
            require_list_of_strings(scenario, "requirement_ids", "scenario"),
            "media_surface":
            require_string(scenario, "media_surface", "scenario"),
            "observed_behavior":
            "not observed in quick-placeholder mode",
            "operator":
            "quick-placeholder",
            "phase15_source_contract_refs":
            require_list_of_strings(scenario, "source_contract_refs",
                                    "scenario"),
            "printer_family":
            require_string(scenario, "printer_family", "scenario"),
            "proof_scope":
            require_string(scenario, "proof_scope", "scenario"),
            "redaction_status":
            "passed",
            "requirement_ids": ["EVID-02"],
            "residual_risk":
            "real hardware/media/safety evidence input was not supplied",
            "retained_artifact_kind":
            require_string(scenario, "retained_artifact_kind", "scenario"),
            "runtime_metadata": {},
            "scenario_id":
            scenario_id,
            "source_ref_status":
            "passed",
            "source_status":
            source_status,
            "status":
            "blocked",
            "status_reason":
            "real hardware/media/safety evidence input was not supplied",
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
    sanitized_snapshot, redaction_errors = sanitized_for_artifact(
        snapshot, snapshot_text)
    if redaction_errors:
        raise VerificationError("\n".join(redaction_errors))
    snapshot_path = output_dir / "contract-snapshots" / snapshot.name
    full_snapshot_path = root / snapshot_path
    full_snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    full_snapshot_path.write_text(sanitized_snapshot, encoding="utf-8")


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
    hardware_requirement_ids = sorted({
        requirement
        for row in rows
        for requirement in row["hardware_requirement_ids"]
    })
    requirement_coverage = {
        "EVID-02": sorted(str(row["scenario_id"]) for row in rows),
        **{
            requirement:
            sorted(
                str(row["scenario_id"]) for row in rows if requirement in row["hardware_requirement_ids"])
            for requirement in hardware_requirement_ids
        },
    }
    manifest = {
        "artifact_name":
        "phase24-hardware-media-safety-evidence-execution",
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
        "real_hardware_evidence_supplied":
        real_input_supplied,
        "requirement_coverage":
        requirement_coverage,
        "scenario_count":
        len(rows),
        "scenarios":
        rows,
        "source_contract_ref":
        PHASE15_CONTRACT.as_posix(),
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
        "real_hardware_evidence_supplied":
        real_input_supplied,
        "scenarios": [{
            "artifact_refs":
            row["artifact_refs"],
            "auxiliary_surface":
            row["auxiliary_surface"],
            "board":
            row["board"],
            "hardware_requirement_ids":
            row["hardware_requirement_ids"],
            "media_surface":
            row["media_surface"],
            "printer_family":
            row["printer_family"],
            "requirement_ids":
            row["requirement_ids"],
            "scenario_id":
            row["scenario_id"],
            "source_status":
            row["source_status"],
            "status":
            row["status"],
            "status_reason":
            row["status_reason"],
            "v1_requirement_ids":
            row["v1_requirement_ids"],
        } for row in rows],
    }
    redacted_summary = {
        "generated_at":
        generated_at,
        "phase":
        PHASE,
        "real_hardware_evidence_supplied":
        real_input_supplied,
        "scenario_status": [{
            "auxiliary_surface": row["auxiliary_surface"],
            "board": row["board"],
            "media_surface": row["media_surface"],
            "printer_family": row["printer_family"],
            "scenario_id": row["scenario_id"],
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
            (output_dir /
             "normalized-hardware-media-safety-results.json").as_posix(),
            (output_dir /
             "redacted-hardware-media-safety-summary.json").as_posix(),
        ],
        "criterion_id":
        "final-hardware-safety-media-evidence",
        "evidence_family":
        "hardware",
        "manifest_ref":
        (output_dir / "hardware-media-safety-result-manifest.json").as_posix(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "real_hardware_evidence_supplied":
        real_input_supplied,
        "redaction_status":
        "passed",
        "requirement_ids": ["EVID-02"],
        "scenario_status_counts":
        status_summary,
        "source_ref_status":
        "passed",
        "status":
        run_status,
    }
    operator_template = {
        "hardware_media_safety_evidence_packet": {
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
                "auxiliary_surface": row["auxiliary_surface"],
                "board": row["board"],
                "device": "",
                "failure_observations": "",
                "firmware_build": "",
                "media_surface": row["media_surface"],
                "operator": "",
                "printer_family": row["printer_family"],
                "redaction_status": "",
                "residual_risk": "",
                "scenario_id": row["scenario_id"],
                "source_ref_status": "",
                "source_status": "",
                "status": "",
                "status_reason": "",
                "timestamp": "",
            } for row in rows],
            "source_contract_ref":
            PHASE15_CONTRACT.as_posix(),
            "started_at":
            "",
        }
    }
    artifact_summary = {
        "allowed_artifact_roots":
        [DEFAULT_OUTPUT_DIR.as_posix() + "/", "external://phase24/"],
        "generated_at":
        generated_at,
        "phase":
        PHASE,
        "retained_files": [
            (output_dir /
             "hardware-media-safety-result-manifest.json").as_posix(),
            (output_dir /
             "normalized-hardware-media-safety-results.json").as_posix(),
            (output_dir /
             "redacted-hardware-media-safety-summary.json").as_posix(),
            (output_dir /
             "upstream-hardware-media-safety-result-row.json").as_posix(),
            (output_dir /
             "operator-hardware-media-safety-template.json").as_posix(),
        ],
        "scenario_count":
        len(rows),
        "status":
        run_status,
    }
    write_json(root, output_dir / "hardware-media-safety-result-manifest.json",
               manifest)
    write_json(root,
               output_dir / "normalized-hardware-media-safety-results.json",
               normalized)
    write_json(root,
               output_dir / "redacted-hardware-media-safety-summary.json",
               redacted_summary)
    write_json(root,
               output_dir / "upstream-hardware-media-safety-result-row.json",
               upstream_row)
    write_json(root, output_dir / "upstream-hardware-result-row.json",
               upstream_row)
    write_json(root,
               output_dir / "operator-hardware-media-safety-template.json",
               operator_template)
    write_json(root, output_dir / "operator-evidence-input-template.json",
               operator_template)
    write_json(
        root, output_dir / "artifact-summaries" /
        "hardware-media-safety-artifact-summary.json", artifact_summary)
    for snapshot in [CONTRACT_MANIFEST, PHASE15_CONTRACT]:
        write_snapshot(root, output_dir, snapshot)
    check_security(root)


def security_paths(root: Path) -> list[Path]:
    paths = [CONTRACT_MANIFEST]
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
                'name = "phase24_source_ref_manifests"',
                'name = "phase24_verify"',
                'name = "phase24_verify_tests"',
                "phase24_hardware_media_safety_evidence_execution.py",
                "phase24_hardware_media_safety_evidence_execution_test.py",
                "phase24_hardware_media_safety_evidence_execution_contract.json",
                "//:phase24_hardware_media_safety_evidence_execution_docs",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase24_hardware_media_safety_evidence_execution_docs"',
                'name = "phase24_verify"',
                'name = "phase24_verify_tests"',
                ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-PLAN.md",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase24_verify)",
                "python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --wiring-only",
                "python3 tools/bazel/phase24_hardware_media_safety_evidence_execution.py --quick --output-dir build/ci-evidence/phase24",
                "phase24_verify_tests)",
                "python3 tools/bazel/phase24_hardware_media_safety_evidence_execution_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase24-verify:",
                "bazel run //tools/bazel:phase24_verify_tests",
                "bazel run //tools/bazel:phase24_verify",
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
    contract, phase15 = check_contract(root)
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
        rows = quick_rows(root, output_relative, phase15)
        write_retained_outputs(root, output_relative, rows,
                               "quick-placeholder", False)
        return
    if args.evidence_input:
        output_relative = reset_output_root(root, output_dir)
        packet, rows = load_evidence_rows(root, Path(args.evidence_input),
                                          phase15)
        write_retained_outputs(root, output_relative, rows, "evidence-input",
                               True, packet)
        return
    check_security(root)
    check_wiring(root)
    _ = contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Validate and retain Phase 24 hardware/media/safety evidence execution results."
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
            f"Phase 24 hardware/media/safety evidence execution verification failed:\n{error}",
            file=sys.stderr)
        return 1
    print(
        "Phase 24 hardware/media/safety evidence execution verification passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
