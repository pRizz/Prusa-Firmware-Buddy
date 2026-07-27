#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from phase15_evidence_policy import (
    CONTRACT_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    PHASE,
    PHASE_LIFECYCLE_ID,
    REQUIRED_OPERATOR_FIELDS,
    REQUIRED_REQUIREMENT_IDS,
    ROOT,
    SOURCE_REF_MANIFESTS,
    VerificationError,
    check_contract,
    check_security,
    contract_scenarios,
    read_text,
    reject_forbidden_text,
    require_fields,
    require_list_of_strings,
    require_repo_relative_under,
    require_string,
)


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
    phase15_manifest_srcs = [
        Path(path).relative_to("tools/bazel").as_posix()
        for path in SOURCE_REF_MANIFESTS
    ]
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase15_source_ref_manifests"',
                'name = "phase15_verify"',
                'name = "phase15_verify_tests"',
                "phase15_hardware_evidence.py",
                "phase15_hardware_evidence_test.py",
                "phase15_hardware_evidence_contract.json",
                ":phase15_source_ref_manifests",
                "//:phase15_hardware_evidence_docs",
                "//:phase11_cutover_evidence_docs",
                *phase15_manifest_srcs,
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase15_hardware_evidence_docs"',
                'name = "phase15_verify"',
                'name = "phase15_verify_tests"',
                ".planning/phases/15-hardware-safety-and-media-qualification/15-CONTEXT.md",
                ".planning/phases/15-hardware-safety-and-media-qualification/15-RESEARCH.md",
                ".planning/phases/15-hardware-safety-and-media-qualification/15-VALIDATION.md",
                ".planning/phases/15-hardware-safety-and-media-qualification/15-01-PLAN.md",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase15_verify)",
                "python3 tools/bazel/phase15_hardware_evidence.py --wiring-only",
                "python3 tools/bazel/phase15_hardware_evidence.py --quick",
                "phase15_verify_tests)",
                "python3 tools/bazel/phase15_hardware_evidence_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase15-verify:",
                "bazel run //tools/bazel:phase15_verify_tests",
                "bazel run //tools/bazel:phase15_verify",
            ],
        ))
    try:
        just_lines = [
            line.strip() for line in read_text(root, "justfile").splitlines()
        ]
        just_tests_line = "bazel run //tools/bazel:phase15_verify_tests"
        just_verify_line = "bazel run //tools/bazel:phase15_verify"
        if just_tests_line not in just_lines:
            errors.append(
                "justfile missing exact phase15_verify_tests recipe line")
        if just_verify_line not in just_lines:
            errors.append("justfile missing exact phase15_verify recipe line")
        if just_tests_line in just_lines and just_verify_line in just_lines:
            if just_lines.index(just_tests_line) > just_lines.index(
                    just_verify_line):
                errors.append(
                    "justfile phase15-verify must run tests before verifier")
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


def validated_operator_rows(root: Path, contract: dict[str, Any],
                            path: str | None) -> dict[str, dict[str, str]]:
    evidence_path, rows = load_operator_evidence_path(root, path)
    if rows is None:
        return {}
    scenarios_by_id = {
        scenario["id"]: scenario
        for scenario in contract_scenarios(contract)
    }
    parsed_rows: dict[str, dict[str, str]] = {}
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
            artifact_ref = require_string(row, "artifact_ref", row_name)
            if scenario_id not in scenarios_by_id:
                raise VerificationError(
                    f"{row_name} references unknown scenario: {scenario_id}")
            if result not in {
                    "passed", "failed", "blocked-hardware-unavailable"
            }:
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
            require_repo_relative_under(artifact_ref, DEFAULT_OUTPUT_DIR,
                                        row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue
        parsed_rows[str(row["scenario_id"])] = {
            field: str(row[field])
            for field in REQUIRED_OPERATOR_FIELDS
        }
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
    return "pending-hardware-input"


def scenario_result_row(
        scenario: dict[str, Any],
        maybe_operator_row: dict[str, str] | None) -> dict[str, Any]:
    scenario_id = str(scenario["id"])
    status = default_status_for(scenario)
    artifact_ref = str(scenario["expected_artifact_path"])
    residual_risk = "Awaiting physical operator evidence." if status == "pending-hardware-input" else "Source contract boundary only."
    operator = ""
    timestamp = ""
    firmware_build = ""
    device = ""
    if maybe_operator_row is not None:
        status = maybe_operator_row["result"]
        artifact_ref = maybe_operator_row["artifact_ref"]
        residual_risk = maybe_operator_row["residual_risk"]
        operator = maybe_operator_row["operator"]
        timestamp = maybe_operator_row["timestamp"]
        firmware_build = maybe_operator_row["firmware_build"]
        device = maybe_operator_row["device"]
    return {
        "artifact_refs": [artifact_ref],
        "artifact_ref": artifact_ref,
        "auxiliary_surface": scenario["auxiliary_surface"],
        "board": scenario["board"],
        "device": device,
        "firmware_build": firmware_build,
        "id": scenario_id,
        "media_surface": scenario["media_surface"],
        "operator": operator,
        "operator_metadata_present": maybe_operator_row is not None,
        "printer_family": scenario["printer_family"],
        "proof_scope": scenario["proof_scope"],
        "requirement_ids": scenario["requirement_ids"],
        "residual_risk": residual_risk,
        "scenario_id": scenario_id,
        "source_contract_refs": scenario["source_contract_refs"],
        "status": status,
        "timestamp": timestamp,
        "title": scenario["title"],
        "v1_requirement_ids": scenario["v1_requirement_ids"],
    }


def write_log(root: Path, output_dir: Path, result_row: dict[str,
                                                             Any]) -> None:
    log_path = output_dir / "logs" / f"{result_row['id']}.log"
    lines = [
        f"scenario_id={result_row['id']}",
        f"status={result_row['status']}",
        f"proof_scope={result_row['proof_scope']}",
        f"printer_family={result_row['printer_family']}",
        f"board={result_row['board']}",
        f"artifact_ref={result_row['artifact_ref']}",
        f"residual_risk={result_row['residual_risk']}",
    ]
    full_path = root / log_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quick_artifacts(
    root: Path,
    contract: dict[str, Any],
    output_dir: Path,
    operator_rows: dict[str, dict[str, str]],
) -> None:
    require_repo_relative_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    full_output_dir = root / output_dir
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
        write_log(root, output_dir, row)

    status_counts: dict[str, int] = {}
    for row in result_rows:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    generated_at = datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")
    run_manifest = {
        "artifact_name":
        contract["artifact_name"],
        "command_mode":
        "quick",
        "generated_at":
        generated_at,
        "output_root":
        output_dir.as_posix(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "requirement_coverage":
        sorted(REQUIRED_REQUIREMENT_IDS),
        "scenarios": [{
            "artifact_ref": row["artifact_ref"],
            "id": row["id"],
            "proof_scope": row["proof_scope"],
            "status": row["status"],
        } for row in result_rows],
        "source_contract_snapshot": (output_dir / "source-contract-snapshots" /
                                     CONTRACT_MANIFEST.name).as_posix(),
        "status_counts":
        status_counts,
    }
    normalized_results = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "scenarios": result_rows,
    }
    redacted_summary = {
        "generated_at":
        generated_at,
        "operator_evidence_count":
        len(operator_rows),
        "pending_hardware_input": [
            row["id"] for row in result_rows
            if row["status"] == "pending-hardware-input"
        ],
        "redaction_boundary":
        "Phase 15 retains only sanitized references and operator metadata required by the contract.",
        "source_contract_rows": [
            row["id"] for row in result_rows
            if row["proof_scope"] == "source-contract"
        ],
        "status_counts":
        status_counts,
    }
    write_json(root, output_dir / "run-manifest.json", run_manifest)
    write_json(root, output_dir / "normalized-scenario-results.json",
               normalized_results)
    write_json(root, output_dir / "redacted-hardware-summary.json",
               redacted_summary)
    write_json(
        root,
        output_dir / "operator-evidence-input.json",
        {"evidence_rows": list(operator_rows.values())},
    )
    shutil.copy2(
        root / CONTRACT_MANIFEST,
        root / output_dir / "source-contract-snapshots" /
        CONTRACT_MANIFEST.name,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 15 hardware evidence contract")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 15 evidence contract")
    parser.add_argument("--security-only",
                        action="store_true",
                        help="scan Phase 15 contract and generated artifacts")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel and just workflow wiring")
    parser.add_argument("--quick",
                        action="store_true",
                        help="write deterministic Phase 15 evidence artifacts")
    parser.add_argument("--operator-evidence",
                        help="optional operator evidence JSON input")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 15 evidence output directory")
    args = parser.parse_args()
    selected_modes = [
        args.contract_only, args.security_only, args.wiring_only, args.quick
    ]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    output_dir = Path(args.output_dir)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 15 hardware evidence contract passed")
        elif args.security_only:
            check_security(ROOT, output_dir)
            print("Phase 15 hardware evidence security scan passed")
        elif args.quick:
            contract = check_contract(ROOT)
            operator_rows = validated_operator_rows(ROOT, contract,
                                                    args.operator_evidence)
            write_quick_artifacts(ROOT, contract, output_dir, operator_rows)
            check_security(ROOT, output_dir)
            print(
                f"Phase 15 hardware evidence written to {output_dir.as_posix()}"
            )
        else:
            check_wiring(ROOT)
            print("Phase 15 hardware evidence wiring passed")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
