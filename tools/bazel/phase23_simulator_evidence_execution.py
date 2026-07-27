#!/usr/bin/env python3
from __future__ import annotations

from phase23_execution_policy import *


def write_retained_outputs(
    root: Path,
    output_dir: Path,
    rows: list[dict[str, Any]],
    command_mode: str,
    real_input_supplied: bool,
    maybe_packet: dict[str, Any] | None = None,
) -> None:
    output_root = root / output_dir
    snapshots_dir = output_root / "contract-snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    if not (output_root / "logs").exists():
        (output_root / "logs").mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    status_summary = status_counts(rows)
    run_status = aggregate_status(rows)
    requirement_coverage = {
        "EVID-01":
        sorted(str(row["scenario_id"]) for row in rows),
        "SIM-01":
        sorted(
            str(row["scenario_id"]) for row in rows
            if "SIM-01" in row["simulator_requirement_ids"]),
        "SIM-02":
        sorted(
            str(row["scenario_id"]) for row in rows
            if "SIM-02" in row["simulator_requirement_ids"]),
        "SIM-03":
        sorted(
            str(row["scenario_id"]) for row in rows
            if "SIM-03" in row["simulator_requirement_ids"]),
    }
    manifest = {
        "artifact_name":
        "phase23-simulator-evidence-execution",
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
        "real_simulator_evidence_supplied":
        real_input_supplied,
        "requirement_coverage":
        requirement_coverage,
        "scenario_count":
        len(rows),
        "scenarios":
        rows,
        "simulator_identity":
        maybe_packet.get("simulator_identity", {}) if maybe_packet else {},
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
        "real_simulator_evidence_supplied":
        real_input_supplied,
        "scenarios": [{
            "artifact_refs":
            row["artifact_refs"],
            "requirement_ids":
            row["requirement_ids"],
            "residual_non_simulator_gates":
            row["residual_non_simulator_gates"],
            "scenario_id":
            row["scenario_id"],
            "simulator_requirement_ids":
            row["simulator_requirement_ids"],
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
        "real_simulator_evidence_supplied":
        real_input_supplied,
        "scenario_status": [{
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
            (output_dir / "normalized-simulator-results.json").as_posix(),
            (output_dir / "redacted-evidence-summary.json").as_posix(),
        ],
        "criterion_id":
        "final-simulator-evidence",
        "evidence_family":
        "simulator",
        "manifest_ref":
        (output_dir / "simulator-result-manifest.json").as_posix(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "real_simulator_evidence_supplied":
        real_input_supplied,
        "redaction_status":
        "passed",
        "requirement_ids": ["EVID-01"],
        "scenario_status_counts":
        status_summary,
        "source_ref_status":
        "passed",
        "status":
        run_status,
    }
    write_json(root, output_dir / "simulator-result-manifest.json", manifest)
    write_json(root, output_dir / "normalized-simulator-results.json",
               normalized)
    write_json(root, output_dir / "redacted-evidence-summary.json",
               redacted_summary)
    write_json(root, output_dir / "upstream-simulator-result-row.json",
               upstream_row)
    for snapshot in [CONTRACT_MANIFEST, PHASE14_CONTRACT]:
        snapshot_text = read_text(root, snapshot)
        sanitized_snapshot, redaction_errors = sanitized_for_artifact(
            snapshot, snapshot_text)
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        (root / snapshots_dir / snapshot.name).write_text(sanitized_snapshot,
                                                          encoding="utf-8")
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
                'name = "phase23_source_ref_manifests"',
                'name = "phase23_verify"',
                'name = "phase23_verify_tests"',
                "phase23_simulator_evidence_execution.py",
                "phase23_simulator_evidence_execution_test.py",
                "phase23_simulator_evidence_execution_contract.json",
                "//:phase23_simulator_evidence_execution_docs",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase23_simulator_evidence_execution_docs"',
                'name = "phase23_verify"',
                'name = "phase23_verify_tests"',
                ".planning/phases/23-simulator-evidence-execution/23-01-PLAN.md",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase23_verify)",
                "python3 tools/bazel/phase23_simulator_evidence_execution.py --wiring-only",
                "python3 tools/bazel/phase23_simulator_evidence_execution.py --quick --output-dir build/ci-evidence/phase23",
                "phase23_verify_tests)",
                "python3 tools/bazel/phase23_simulator_evidence_execution_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase23-verify:",
                "bazel run //tools/bazel:phase23_verify_tests",
                "bazel run //tools/bazel:phase23_verify",
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
    contract, phase14 = check_contract(root)
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
        rows = quick_rows(root, output_relative, phase14)
        write_retained_outputs(root, output_relative, rows,
                               "quick-placeholder", False)
        return
    if args.evidence_input:
        output_relative = reset_output_root(root, output_dir)
        packet, rows = load_evidence_rows(root, Path(args.evidence_input),
                                          phase14)
        write_retained_outputs(root, output_relative, rows, "evidence-input",
                               True, packet)
        return
    check_security(root)
    check_wiring(root)
    _ = contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Validate and retain Phase 23 simulator evidence execution results.")
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
            f"Phase 23 simulator evidence execution verification failed:\n{error}",
            file=sys.stderr)
        return 1
    print("Phase 23 simulator evidence execution verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
