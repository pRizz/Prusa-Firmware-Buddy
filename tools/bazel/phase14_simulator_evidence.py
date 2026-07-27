#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from phase14_evidence_policy import (
    CONTRACT_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    PHASE,
    PHASE_LIFECYCLE_ID,
    REQUIRED_REQUIREMENT_IDS,
    ROOT,
    VerificationError,
    check_contract,
    check_security,
    check_wiring,
    contract_scenarios,
    read_text,
    require_dict,
    require_list_of_strings,
    require_repo_relative_under,
    require_string,
    sanitized_for_artifact,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def scenario_status_for_quick(scenario: dict[str, Any]) -> str:
    if require_string(
            scenario, "id",
            "scenario") == "sim-traceability-non-simulator-boundaries":
        return "passed"
    return "pending-simulator-input"


def scenario_result(scenario: dict[str, Any], status: str,
                    reason: str) -> dict[str, Any]:
    return {
        "artifact_refs":
        [require_string(scenario, "expected_artifact_path", "scenario")],
        "phase11_source_refs":
        require_list_of_strings(scenario, "phase11_source_refs", "scenario"),
        "proof_scope":
        require_string(scenario, "proof_scope", "scenario"),
        "pytest_node_ids":
        require_list_of_strings(scenario, "pytest_node_ids", "scenario"),
        "requirement_ids":
        require_list_of_strings(scenario, "requirement_ids", "scenario"),
        "residual_non_simulator_gates":
        require_list_of_strings(scenario, "residual_non_simulator_gates",
                                "scenario"),
        "scenario_id":
        require_string(scenario, "id", "scenario"),
        "skipped_pytest_node_ids":
        require_list_of_strings(scenario, "skipped_pytest_node_ids",
                                "scenario"),
        "status":
        status,
        "status_reason":
        reason,
        "title":
        require_string(scenario, "title", "scenario"),
        "unsupported_claims":
        require_list_of_strings(scenario, "unsupported_claims", "scenario"),
        "v1_requirement_ids":
        require_list_of_strings(scenario, "v1_requirement_ids", "scenario"),
    }


def write_quick_artifacts(root: Path, output_dir: Path) -> None:
    contract = check_contract(root)
    check_security(root)
    output_relative = require_repo_relative_under(output_dir,
                                                  DEFAULT_OUTPUT_DIR,
                                                  "--output-dir")
    output_root = root / output_relative
    if output_root.exists():
        shutil.rmtree(output_root)
    logs_dir = output_root / "logs"
    snapshots_dir = output_root / "contract-snapshots"
    logs_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    scenarios = contract_scenarios(contract)
    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        status = scenario_status_for_quick(scenario)
        reason = (
            "contract-boundary row passed by structural validation"
            if status == "passed" else
            "real simulator inputs were not supplied; dry-run evidence remains pending-simulator-input"
        )
        log_relative = Path(
            require_string(scenario, "expected_artifact_path", "scenario"))
        log_path = root / log_relative
        log_text = (
            f"phase: {PHASE}\n"
            f"scenario: {scenario['id']}\n"
            f"mode: quick-dry-run\n"
            f"status: {status}\n"
            f"reason: {reason}\n"
            "note: this file is a dry-run log reference, not real simulator output.\n"
        )
        sanitized_log, redaction_errors = sanitized_for_artifact(
            log_relative, log_text)
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        log_path.write_text(sanitized_log, encoding="utf-8")
        results.append(scenario_result(scenario, status, reason))

    requirement_coverage = {
        requirement_id:
        sorted(result["scenario_id"] for result in results
               if requirement_id in result["requirement_ids"])
        for requirement_id in sorted(REQUIRED_REQUIREMENT_IDS)
    }
    residual_gates = sorted({
        residual_gate
        for result in results
        for residual_gate in result["residual_non_simulator_gates"]
    })
    external_inputs = require_dict(contract, "external_inputs", "contract")
    run_manifest = {
        "artifact_name": contract["artifact_name"],
        "command_mode": "quick-dry-run",
        "external_inputs": {
            name: {
                "description": description,
                "status": "required-for-run-simulator",
            }
            for name, description in external_inputs.items()
        },
        "generated_at": utc_now(),
        "output_root": output_relative.as_posix(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_coverage": requirement_coverage,
        "residual_gate_summary": residual_gates,
        "scenarios": results,
    }
    normalized = [{
        "artifact_refs":
        result["artifact_refs"],
        "phase11_source_refs":
        result["phase11_source_refs"],
        "requirement_ids":
        result["requirement_ids"],
        "residual_non_simulator_gates":
        result["residual_non_simulator_gates"],
        "scenario_id":
        result["scenario_id"],
        "status":
        result["status"],
        "v1_requirement_ids":
        result["v1_requirement_ids"],
    } for result in results]
    redacted_summary = {
        "external_input_names":
        sorted(external_inputs),
        "generated_at":
        run_manifest["generated_at"],
        "mode":
        "quick-dry-run",
        "phase":
        PHASE,
        "real_run_command":
        "python3 tools/bazel/phase14_simulator_evidence.py --run-simulator --firmware <firmware.bin>",
        "requirement_coverage":
        requirement_coverage,
        "scenario_status": [{
            "scenario_id": result["scenario_id"],
            "status": result["status"],
            "status_reason": result["status_reason"],
        } for result in results],
        "unsupported_boundaries":
        sorted({
            claim
            for result in results
            for claim in result["unsupported_claims"]
        }),
    }
    write_json(output_root / "run-manifest.json", run_manifest)
    write_json(output_root / "normalized-scenarios.json", normalized)
    write_json(output_root / "redacted-summary.json", redacted_summary)
    snapshot_text = read_text(root, CONTRACT_MANIFEST)
    sanitized_snapshot, redaction_errors = sanitized_for_artifact(
        CONTRACT_MANIFEST, snapshot_text)
    if redaction_errors:
        raise VerificationError("\n".join(redaction_errors))
    (snapshots_dir / CONTRACT_MANIFEST.name).write_text(sanitized_snapshot,
                                                        encoding="utf-8")
    check_security(root)


def build_pytest_command(firmware: Path, maybe_simulator: Path | None,
                         node_ids: list[str]) -> list[str]:
    command = [
        sys.executable, "-m", "pytest", *node_ids, "--firmware",
        firmware.as_posix()
    ]
    if maybe_simulator is not None:
        command.extend(["--simulator", maybe_simulator.as_posix()])
    return command


def redacted_command_for_log(command: list[str]) -> list[str]:
    redacted: list[str] = []
    redact_next = False
    for token in command:
        if redact_next:
            redacted.append(Path(token).name)
            redact_next = False
            continue
        redacted.append(token)
        if token in {"--firmware", "--simulator"}:
            redact_next = True
    return redacted


def validate_real_inputs(
        root: Path, maybe_firmware: str | None,
        maybe_simulator: str | None) -> tuple[Path, Path | None]:
    if maybe_firmware is None:
        raise VerificationError(
            "--run-simulator requires --firmware <firmware.bin>")
    firmware = Path(maybe_firmware)
    if not firmware.is_file() or firmware.suffix != ".bin":
        raise VerificationError(
            "--firmware must point to an existing .bin file")
    adjacent_bbf = firmware.with_suffix(".bbf")
    if not adjacent_bbf.is_file():
        raise VerificationError(
            "--firmware requires an adjacent .bbf file for integration bootstrap"
        )
    simulator = None
    if maybe_simulator is not None:
        simulator = Path(maybe_simulator)
        if not simulator.is_file():
            raise VerificationError(
                "--simulator must point to an existing file when supplied")
    return firmware, simulator


def run_simulator(root: Path, output_dir: Path, maybe_firmware: str | None,
                  maybe_simulator: str | None) -> None:
    contract = check_contract(root)
    firmware, simulator = validate_real_inputs(root, maybe_firmware,
                                               maybe_simulator)
    output_relative = require_repo_relative_under(output_dir,
                                                  DEFAULT_OUTPUT_DIR,
                                                  "--output-dir")
    output_root = root / output_relative
    if output_root.exists():
        shutil.rmtree(output_root)
    (output_root / "logs").mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for scenario in contract_scenarios(contract):
        node_ids = require_list_of_strings(scenario, "pytest_node_ids",
                                           "scenario")
        log_relative = Path(
            require_string(scenario, "expected_artifact_path", "scenario"))
        log_path = root / log_relative
        if not node_ids:
            reason = "contract-boundary row passed by structural validation"
            log_path.write_text(
                f"phase: {PHASE}\nscenario: {scenario['id']}\nmode: run-simulator\nstatus: passed\n",
                encoding="utf-8",
            )
            results.append(scenario_result(scenario, "passed", reason))
            continue
        command = build_pytest_command(firmware, simulator, node_ids)
        result = subprocess.run(
            command,
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        log_text = "$ " + " ".join(
            redacted_command_for_log(command)) + "\n" + result.stdout
        sanitized_log_text, redaction_errors = sanitized_for_artifact(
            log_relative, log_text)
        log_path.write_text(sanitized_log_text, encoding="utf-8")
        if redaction_errors:
            raise VerificationError("\n".join(redaction_errors))
        status = "passed" if result.returncode == 0 else "failed"
        reason = "pytest nodes passed" if status == "passed" else f"pytest exited {result.returncode}"
        results.append(scenario_result(scenario, status, reason))
    write_json(
        output_root / "run-manifest.json",
        {
            "command_mode":
            "run-simulator",
            "firmware_basename":
            firmware.name,
            "generated_at":
            utc_now(),
            "phase":
            PHASE,
            "phase_lifecycle_id":
            PHASE_LIFECYCLE_ID,
            "scenarios":
            results,
            "simulator_basename":
            simulator.name if simulator is not None else None,
        },
    )
    write_json(output_root / "normalized-scenarios.json", results)
    write_json(
        output_root / "redacted-summary.json",
        {
            "firmware_basename":
            firmware.name,
            "generated_at":
            utc_now(),
            "phase":
            PHASE,
            "scenario_status": [{
                "scenario_id": result["scenario_id"],
                "status": result["status"],
                "status_reason": result["status_reason"],
            } for result in results],
            "simulator_basename":
            simulator.name if simulator is not None else None,
        },
    )
    snapshot_dir = output_root / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / CONTRACT_MANIFEST.name).write_text(read_text(
        root, CONTRACT_MANIFEST),
                                                       encoding="utf-8")
    check_security(root)
    failures = [result for result in results if result["status"] == "failed"]
    if failures:
        raise VerificationError("one or more simulator scenarios failed")


def run_or_raise(args: argparse.Namespace) -> None:
    root = ROOT
    output_dir = Path(args.output_dir)
    if args.contract_only:
        check_contract(root)
        return
    if args.security_only:
        check_contract(root)
        check_security(root)
        return
    if args.wiring_only:
        check_wiring(root)
        return
    if args.quick:
        write_quick_artifacts(root, output_dir)
        return
    if args.run_simulator:
        run_simulator(root, output_dir, args.firmware, args.simulator)
        return
    check_contract(root)
    check_security(root)
    check_wiring(root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and write Phase 14 simulator evidence.")
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--run-simulator", action="store_true")
    parser.add_argument("--firmware")
    parser.add_argument("--simulator")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args()


def main() -> int:
    try:
        run_or_raise(parse_args())
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
