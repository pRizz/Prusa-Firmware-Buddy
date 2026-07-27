#!/usr/bin/env python3
from __future__ import annotations

from phase19_aggregate_policy import *


def run_logged_command(root: Path, command: list[str],
                       log_path: Path) -> tuple[int, str, list[str]]:
    result = subprocess.run(command,
                            cwd=root,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            check=False)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_text = "$ " + " ".join(command) + "\n" + result.stdout
    sanitized_log_text, redaction_errors = sanitized_for_artifact(
        log_path, log_text)
    if redaction_errors:
        sanitized_log_text = "$ " + " ".join(
            command
        ) + "\n[REDACTED] command output contained forbidden evidence content.\n"
    log_path.write_text(sanitized_log_text, encoding="utf-8")
    if redaction_errors:
        return result.returncode, f"{' '.join(command)} produced forbidden evidence content", redaction_errors
    if result.returncode == 0:
        return result.returncode, "", []
    return result.returncode, f"{' '.join(command)} failed with exit code {result.returncode}", []


def command_for_mode(phase: dict[str, Any], mode: str) -> list[str]:
    command = ["python3", require_string(phase, "script", "phase")]
    if mode == "contract-only":
        command.append("--contract-only")
    elif mode == "wiring-only":
        command.append("--wiring-only")
    elif mode == "quick":
        command.extend([
            "--quick", "--output-dir",
            require_string(phase, "quick_output_dir", "phase")
        ])
    elif mode == "security-only":
        command.extend([
            "--security-only", "--output-dir",
            require_string(phase, "quick_output_dir", "phase")
        ])
    else:
        raise VerificationError(f"unsupported mode: {mode}")
    return command


def manifest_row(
    row_id: str,
    requirement_ids: list[str],
    owning_phase: str,
    command: str,
    artifact_path: Path,
    status: str,
    failure_reason: str,
    evidence_input: str = "",
) -> dict[str, Any]:
    row = {
        "artifact_path": artifact_path.as_posix(),
        "command": command,
        "evidence_input": evidence_input,
        "failure_reason": failure_reason,
        "id": row_id,
        "owning_phase": owning_phase,
        "requirement_ids": requirement_ids,
        "status": status,
    }
    if status == "passed" and evidence_input:
        raise VerificationError(
            f"{row_id} cannot pass external evidence input without explicit validation"
        )
    return row


def copy_text_artifact(root: Path, source: Path,
                       destination: Path) -> tuple[str, list[str]]:
    if not (root / source).exists():
        return f"missing source artifact: {source.as_posix()}", []
    source_text = read_text(root, source)
    sanitized_text, redaction_errors = sanitized_for_artifact(
        source, source_text)
    if redaction_errors:
        return f"{source.as_posix()} contained forbidden evidence content", redaction_errors
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(sanitized_text, encoding="utf-8")
    return "", []


def copy_artifact_tree(root: Path, source_dir: Path,
                       destination_dir: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    redaction_failures: list[str] = []
    if not (root / source_dir).exists():
        return [f"missing source output directory: {source_dir.as_posix()}"
                ], []
    if destination_dir.exists():
        shutil.rmtree(destination_dir)
    for source_file in sorted((root / source_dir).rglob("*")):
        if not source_file.is_file():
            continue
        relative_source = source_file.relative_to(root)
        relative_destination = source_file.relative_to(root / source_dir)
        failure, redaction_errors = copy_text_artifact(
            root, relative_source, destination_dir / relative_destination)
        if failure:
            failures.append(failure)
        redaction_failures.extend(redaction_errors)
    return failures, redaction_failures


def collect_statuses(value: Any) -> set[str]:
    statuses: set[str] = set()
    if isinstance(value, dict):
        maybe_status = value.get("status")
        if isinstance(maybe_status, str):
            statuses.add(maybe_status)
        for child in value.values():
            statuses.update(collect_statuses(child))
    elif isinstance(value, list):
        for child in value:
            statuses.update(collect_statuses(child))
    return statuses


def write_ci_evidence(root: Path, output_dir: Path) -> None:
    output_relative = require_safe_output_dir(root, output_dir, "--output-dir")
    output_root = root / output_relative
    if output_root.exists():
        shutil.rmtree(output_root)
    logs_dir = output_root / "logs"
    snapshots_dir = output_root / "manifest-snapshots"
    phase_artifacts_dir = output_root / "phase-artifacts"
    logs_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    phase_artifacts_dir.mkdir(parents=True, exist_ok=True)

    contract = check_contract(root)
    gates: list[dict[str, Any]] = []
    local_failures: list[str] = []
    redaction_failures: list[str] = []
    observed_statuses: dict[str, list[str]] = {}
    external_placeholders: list[dict[str, Any]] = []

    snapshot_sources = [CONTRACT_MANIFEST]
    for phase in contract_phases(contract):
        script = Path(require_string(phase, "script", "phase"))
        snapshot_sources.append(
            Path("tools/bazel/manifests") /
            f"{script.stem.replace('_test', '')}_contract.json")

    for source in snapshot_sources:
        if not (root / source).exists():
            continue
        failure, errors = copy_text_artifact(root, source,
                                             snapshots_dir / source.name)
        if failure:
            local_failures.append(failure)
        redaction_failures.extend(errors)

    for phase in contract_phases(contract):
        owning_phase = require_string(phase, "owning_phase", "phase")
        requirements = require_list_of_strings(phase, "requirements",
                                               owning_phase)
        artifact_subdir = require_string(phase, "artifact_subdir",
                                         owning_phase)
        quick_output_dir = Path(
            require_string(phase, "quick_output_dir", owning_phase))
        local_modes = require_list_of_strings(phase, "local_modes",
                                              owning_phase)
        expected_artifacts = require_list_of_strings(phase,
                                                     "expected_artifacts",
                                                     owning_phase)
        for mode in local_modes:
            command = command_for_mode(phase, mode)
            log_path = output_relative / "logs" / f"{artifact_subdir}-{mode}.log"
            returncode, failure_reason, errors = run_logged_command(
                root, command, root / log_path)
            status = "passed" if returncode == 0 and not errors else "failed"
            redaction_failures.extend(errors)
            if failure_reason:
                local_failures.append(failure_reason)
            gates.append(
                manifest_row(
                    f"{artifact_subdir}-{mode}",
                    requirements,
                    owning_phase,
                    " ".join(command),
                    log_path,
                    status,
                    failure_reason,
                ))
        destination_dir = phase_artifacts_dir / artifact_subdir
        copy_failures, copy_redactions = copy_artifact_tree(
            root, quick_output_dir, destination_dir)
        for artifact in expected_artifacts:
            if not (root / quick_output_dir / artifact).is_file():
                copy_failures.append(
                    f"missing expected source artifact: {(quick_output_dir / artifact).as_posix()}"
                )
            elif not (destination_dir / artifact).is_file():
                copy_failures.append(
                    f"missing expected retained artifact: {(output_relative / 'phase-artifacts' / artifact_subdir / artifact).as_posix()}"
                )
        redaction_failures.extend(copy_redactions)
        copy_status = "failed" if copy_failures else "passed"
        copy_reason = "; ".join(copy_failures)
        if copy_failures:
            local_failures.extend(copy_failures)
        gates.append(
            manifest_row(
                f"{artifact_subdir}-artifact-retention",
                requirements,
                owning_phase,
                "copy generated quick artifacts into Phase 19 aggregate bundle",
                output_relative / "phase-artifacts" / artifact_subdir,
                copy_status,
                copy_reason,
            ))
        maybe_run_manifest = root / quick_output_dir / "run-manifest.json"
        if maybe_run_manifest.exists():
            observed_statuses[artifact_subdir] = sorted(
                collect_statuses(
                    load_json(root, quick_output_dir / "run-manifest.json")))
        external_input = require_dict(phase, "external_input", owning_phase)
        placeholder = {
            "artifact_path":
            require_string(external_input, "artifact_path",
                           f"{owning_phase} external_input"),
            "description":
            require_string(external_input, "description",
                           f"{owning_phase} external_input"),
            "id":
            require_string(external_input, "id",
                           f"{owning_phase} external_input"),
            "owning_phase":
            owning_phase,
            "requirement_ids":
            requirements,
            "status":
            require_string(external_input, "status",
                           f"{owning_phase} external_input"),
        }
        external_placeholders.append(placeholder)
        gates.append(
            manifest_row(
                placeholder["id"],
                requirements,
                owning_phase,
                "",
                output_relative / "external-input-placeholders.json",
                placeholder["status"],
                "external evidence input was not supplied to aggregate CI",
                placeholder["description"],
            ))

    if redaction_failures:
        local_failures.extend(redaction_failures)

    generated_at_utc = utc_now()
    run_manifest = {
        "artifact_name": "phase19-ci-evidence",
        "external_input_placeholders": external_placeholders,
        "gates": gates,
        "generated_at_utc": generated_at_utc,
        "observed_source_statuses": observed_statuses,
        "output_root": output_relative.as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "retention_days": 30,
        "schema_version": "1",
    }
    redacted_summary = {
        "external_rows_pending_or_blocked": [
            row["id"] for row in gates
            if row["status"] in EXTERNAL_PENDING_STATUSES
            or str(row["status"]).startswith("blocked")
        ],
        "generated_at_utc":
        generated_at_utc,
        "local_failed_rows":
        [row["id"] for row in gates if row["status"] == "failed"],
        "local_passed_rows":
        [row["id"] for row in gates if row["status"] == "passed"],
        "phase":
        PHASE,
        "requirements_covered":
        sorted({req
                for row in gates
                for req in row["requirement_ids"]}),
        "summary":
        "Phase 19 aggregate CI evidence retains Phase 14-18 local verifier outputs and explicit external-input placeholders.",
    }
    write_json(output_root / "external-input-placeholders.json",
               {"evidence_rows": external_placeholders})
    write_json(output_root / "run-manifest.json", run_manifest)
    write_json(output_root / "redacted-summary.json", redacted_summary)
    check_security(root, output_relative)
    if local_failures:
        raise VerificationError("\n".join(local_failures))


def collect_errors(checks: list[Any]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify Phase 19 aggregate cutover CI evidence.")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to inspect; useful for verifier fixtures.")
    parser.add_argument("--quick",
                        action="store_true",
                        help="run quick Phase 19 aggregate checks")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="verify only the Phase 19 aggregate contract")
    parser.add_argument("--workflow-only",
                        action="store_true",
                        help="verify only the CI workflow")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="verify only secret and overclaim scans")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="verify only Bazel/just wiring")
    parser.add_argument(
        "--ci",
        action="store_true",
        help="write the Phase 19 aggregate CI evidence output tree")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Repo-relative CI evidence output directory.")
    return parser.parse_args(argv)


def selected_checks(root: Path, args: argparse.Namespace) -> list[Any]:
    output_dir = Path(args.output_dir)
    checks: list[Any] = []
    if args.quick:
        checks.append(lambda: check_contract(root))
        checks.append(lambda: check_security(root, output_dir))
    if args.contract_only:
        checks.append(lambda: check_contract(root))
    if args.workflow_only:
        checks.append(lambda: check_workflow(root))
    if args.security_only:
        checks.append(lambda: check_security(root, output_dir))
    if args.wiring_only:
        checks.append(lambda: check_wiring(root))
    if args.ci:
        checks.append(lambda: write_ci_evidence(root, output_dir))
    if not checks:
        checks.extend([
            lambda: check_contract(root), lambda: check_workflow(root),
            lambda: check_security(root), lambda: check_wiring(root)
        ])
    return checks


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.repo_root).resolve() if args.repo_root else ROOT
    try:
        collect_errors(selected_checks(root, args))
    except VerificationError as error:
        print(f"Phase 19 aggregate CI evidence verification failed:\n{error}",
              file=sys.stderr)
        return 1
    print("Phase 19 aggregate CI evidence verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
