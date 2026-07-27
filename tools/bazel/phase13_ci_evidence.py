#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from phase13_evidence_policy import (
    CONTRACT_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    PENDING_NON_LOCAL_EVIDENCE,
    PHASE,
    PHASE11_CUTOVER_READINESS,
    PHASE11_REFERENCE_COMPARISONS,
    PHASE11_REQUIREMENT_EVIDENCE,
    PHASE11_RETAINED_CODE_JUSTIFICATIONS,
    PHASE_LIFECYCLE_ID,
    ROOT,
    VerificationError,
    check_contract,
    check_security,
    check_wiring,
    check_workflow,
    load_json,
    read_text,
    require_repo_relative_under,
    require_string,
    safe_gate_for_artifact,
    sanitized_for_artifact,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def run_logged_command(root: Path, command: list[str],
                       log_path: Path) -> tuple[int, str, list[str]]:
    result = subprocess.run(
        command,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_text = "$ " + " ".join(command) + "\n" + result.stdout
    sanitized_log_text, redaction_errors = sanitized_for_artifact(
        log_path, log_text)
    if redaction_errors:
        sanitized_log_text = (
            "$ " + " ".join(command) +
            "\n[REDACTED] command output contained forbidden evidence content.\n"
        )
    log_path.write_text(sanitized_log_text, encoding="utf-8")
    if redaction_errors:
        return (
            result.returncode,
            f"{' '.join(command)} produced forbidden evidence content",
            redaction_errors,
        )
    if result.returncode == 0:
        return result.returncode, "", []
    return result.returncode, f"{' '.join(command)} failed with exit code {result.returncode}", []


def gate_result(
    gate: dict[str, object],
    status: str,
    failure_reason: str,
) -> dict[str, object]:
    return {
        "id":
        require_string(gate, "id", "gate"),
        "requirement_id":
        require_string(gate, "requirement_id", "gate"),
        "owning_phase":
        require_string(gate, "owning_phase", "gate"),
        "command":
        require_string(gate, "command", "gate"),
        "proof_scope":
        require_string(gate, "proof_scope", "gate"),
        "artifact_path":
        require_string(gate, "expected_artifact_path", "gate"),
        "retained_artifact_kind":
        require_string(gate, "retained_artifact_kind", "gate"),
        "status":
        status,
        "failure_reason":
        failure_reason,
    }


def copy_evidence_file(root: Path, source: Path,
                       destination: Path) -> tuple[str, list[str]]:
    if not (root / source).exists():
        return f"missing source snapshot: {source.as_posix()}", []
    source_text = read_text(root, source)
    sanitized_text, redaction_errors = sanitized_for_artifact(
        source, source_text)
    if redaction_errors:
        return f"{source.as_posix()} contained forbidden evidence content", redaction_errors
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(sanitized_text, encoding="utf-8")
    return "", []


def write_ci_evidence(root: Path, output_dir: Path) -> None:
    output_relative = require_repo_relative_under(output_dir,
                                                  DEFAULT_OUTPUT_DIR,
                                                  "--output-dir")
    output_root = root / output_relative
    if output_root.exists():
        shutil.rmtree(output_root)
    logs_dir = output_root / "logs"
    snapshots_dir = output_root / "manifest-snapshots"
    comparisons_dir = output_root / "normalized-comparisons"
    logs_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    comparisons_dir.mkdir(parents=True, exist_ok=True)

    try:
        check_contract(root)
        contract = load_json(root, CONTRACT_MANIFEST)
    except VerificationError:
        contract = {"gates": []}
    gates: list[dict[str, object]] = []
    local_failures: list[str] = []
    redaction_failures: list[str] = []

    command_plan = [
        (
            "ciev-02-run-manifest",
            [
                "python3", "tools/bazel/phase13_ci_evidence.py",
                "--contract-only"
            ],
            logs_dir / "phase13-contract.log",
        ),
        (
            "ciev-01-pr-path-trigger",
            [
                "python3", "tools/bazel/phase13_ci_evidence.py",
                "--workflow-only"
            ],
            logs_dir / "phase13-workflow.log",
        ),
        (
            "ciev-01-aggregate-cutover-verifier",
            ["python3", "tools/bazel/phase11_verify.py", "--quick"],
            logs_dir / "phase11-quick.log",
        ),
    ]
    for gate_id, command, log_path in command_plan:
        gate = safe_gate_for_artifact(contract, gate_id)
        returncode, failure_reason, redaction_errors = run_logged_command(
            root, command, log_path)
        status = "passed" if returncode == 0 else "failed"
        if redaction_errors:
            status = "failed"
            redaction_failures.extend(redaction_errors)
        gates.append(gate_result(gate, status, failure_reason))
        if failure_reason:
            local_failures.append(failure_reason)

    snapshot_sources = [
        CONTRACT_MANIFEST,
        PHASE11_REQUIREMENT_EVIDENCE,
        PHASE11_CUTOVER_READINESS,
        PHASE11_RETAINED_CODE_JUSTIFICATIONS,
    ]
    copy_results = [
        copy_evidence_file(root, source, snapshots_dir / source.name)
        for source in snapshot_sources
    ]
    comparison_failure, comparison_redaction_errors = copy_evidence_file(
        root,
        PHASE11_REFERENCE_COMPARISONS,
        comparisons_dir / PHASE11_REFERENCE_COMPARISONS.name,
    )
    copy_results.append((comparison_failure, comparison_redaction_errors))
    snapshot_failures = [failure for failure, _ in copy_results if failure]
    for _, redaction_errors in copy_results:
        redaction_failures.extend(redaction_errors)
    snapshot_status = "failed" if snapshot_failures else "passed"
    snapshot_reason = "; ".join(snapshot_failures)
    gates.append(
        gate_result(
            safe_gate_for_artifact(
                contract, "ciev-03-manifest-and-comparison-snapshots"),
            snapshot_status,
            snapshot_reason,
        ))

    generated_at_utc = utc_now()
    redaction_reason = "; ".join(redaction_failures)
    redacted_summary_gate = gate_result(
        safe_gate_for_artifact(contract, "ciev-03-redacted-summary"),
        "failed" if redaction_failures else "passed",
        redaction_reason,
    )
    gates.append(redacted_summary_gate)

    redacted_summary = {
        "schema_version":
        "1",
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "generated_at_utc":
        generated_at_utc,
        "summary":
        ("Phase 13 CI evidence contains verifier logs, manifest snapshots, "
         "normalized comparison output, and pending non-local evidence classes."
         ),
        "gates":
        gates,
        "pending_non_local_evidence":
        PENDING_NON_LOCAL_EVIDENCE,
    }
    write_json(output_root / "redacted-summary.json", redacted_summary)

    run_manifest = {
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generated_at_utc": generated_at_utc,
        "output_root": output_relative.as_posix(),
        "artifact_name": "phase13-ci-evidence",
        "retention_days": 30,
        "gates": gates,
    }
    write_json(output_root / "run-manifest.json", run_manifest)
    check_security(root)
    if snapshot_failures:
        local_failures.extend(snapshot_failures)
    if redaction_failures:
        local_failures.append(redaction_reason)
    if local_failures:
        raise VerificationError("\n".join(local_failures))


def check_quick(root: Path) -> None:
    check_contract(root)
    check_security(root)


def collect_errors(checks: list[object]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify Phase 13 CI evidence orchestration.")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to inspect; useful for verifier fixtures.",
    )
    parser.add_argument("--quick",
                        action="store_true",
                        help="run quick Phase 13 checks")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="verify only the CI evidence contract")
    parser.add_argument("--workflow-only",
                        action="store_true",
                        help="verify only the CI workflow")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="verify only secret and overclaim scans")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="verify only Bazel/just wiring")
    parser.add_argument("--ci",
                        action="store_true",
                        help="write the Phase 13 CI evidence output tree")
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR.as_posix(),
        help="Repo-relative CI evidence output directory.",
    )
    return parser.parse_args()


def selected_checks(root: Path, args: argparse.Namespace) -> list[object]:
    checks: list[object] = []
    if args.quick:
        checks.append(lambda: check_quick(root))
    if args.contract_only:
        checks.append(lambda: check_contract(root))
    if args.workflow_only:
        checks.append(lambda: check_workflow(root))
    if args.security_only:
        checks.append(lambda: check_security(root))
    if args.wiring_only:
        checks.append(lambda: check_wiring(root))
    if args.ci:
        checks.append(lambda: write_ci_evidence(root, Path(args.output_dir)))
    if not checks:
        checks.append(lambda: check_quick(root))
    return checks


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else ROOT
    try:
        collect_errors(selected_checks(root, args))
    except VerificationError as error:
        print(f"Phase 13 CI evidence verification failed:\n{error}")
        return 1
    print("Phase 13 CI evidence verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
