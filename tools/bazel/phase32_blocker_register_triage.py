#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from phase32_phase27_adapter import phase27_rows
from phase32_phase28_adapter import phase28_rows
from phase32_phase31_adapter import load_phase31_rows
from phase32_triage_policy import *


def validate_register_rows(rows: list[dict[str, Any]]) -> None:
    row_ids: set[str] = set()
    for row in rows:
        missing_fields = REQUIRED_CANONICAL_FIELDS - set(row)
        if missing_fields:
            raise VerificationError(
                f"{row.get('row_id', '<unknown>')} missing fields: {', '.join(sorted(missing_fields))}"
            )
        if row["row_id"] in row_ids:
            raise VerificationError(f"duplicate row_id: {row['row_id']}")
        row_ids.add(row["row_id"])
        if row["proof_eligibility"] != "ineligible":
            raise VerificationError(
                f"{row['row_id']} must be proof-ineligible in the blocker register"
            )
        for field in ("owner_ref", "required_next_action", "decision_impact"):
            if not isinstance(row[field], str) or not row[field]:
                raise VerificationError(
                    f"{row['row_id']} {field} must be explicit")
        try:
            expected_row_id = canonical_row_id(row)
        except NormalizationError as error:
            raise VerificationError(str(error)) from error
        if row["row_id"] != expected_row_id:
            raise VerificationError(
                f"{row['row_id']} does not match immutable source identity")
    try:
        validate_identity_bindings(rows)
    except NormalizationError as error:
        raise VerificationError(str(error)) from error


def build_derived_views(rows: list[dict[str, Any]]) -> dict[str, Any]:
    register_ids = {row["row_id"] for row in rows}
    decision_rows = [{
        "row_id": row["row_id"],
        "source_domain": row["source_domain"],
        "producer_phase": row["producer_phase"],
        "producer_artifact_kind": row["producer_artifact_kind"],
        "source_row_kind": row["source_row_kind"],
        "source_subject_id": row["source_subject_id"],
        "decision_axis": row["decision_axis"],
        "decision_subject_id": row["decision_subject_id"],
        "source_stream": row["source_stream"],
        "affected_gate": row["affected_gate"],
        "blocker_kind": row["blocker_kind"],
        "severity": row["severity"],
        "decision_impact": row["decision_impact"],
    } for row in rows]
    exception_rows = [{
        "row_id": row["row_id"],
        "decision_axis": row["decision_axis"],
        "decision_subject_id": row["decision_subject_id"],
        "source_ref": row["source_ref"],
        "owner_ref": row["owner_ref"],
        "required_next_action": row["required_next_action"],
        "decision_impact": row["decision_impact"],
    } for row in rows if row["blocker_kind"] == "exception_request"]
    residual_rows = [
        {
            "row_id": row["row_id"],
            "decision_axis": row["decision_axis"],
            "decision_subject_id": row["decision_subject_id"],
            "source_ref": row["source_ref"],
            "owner_ref": row["owner_ref"],
            "required_next_action": row["required_next_action"],
            "decision_impact": row["decision_impact"],
        } for row in rows
        if row["decision_impact"] == "residual_risk_decision_required"
    ]
    for derived_row in [*decision_rows, *exception_rows, *residual_rows]:
        if derived_row["row_id"] not in register_ids:
            raise VerificationError(
                f"derived row does not reference canonical row_id: {derived_row['row_id']}"
            )
    return {
        "decision-impact-index.json": {
            "rows": decision_rows
        },
        "exception-request-register.json": {
            "rows": exception_rows
        },
        "residual-risk-request-register.json": {
            "rows": residual_rows
        },
    }


def write_report(root: Path, output_dir: Path, rows: list[dict[str,
                                                               Any]]) -> None:
    lines = [
        "# Phase 32 Redacted Blocker Register Report",
        "",
        "This report is generated from `blocker-register.json`; it is not a cutover verdict, readiness approval, exception approval, retained-code acceptance, residual-risk acceptance, or reference-demotion authorization.",
        "",
        "| Row ID | Stream | Problem | Blocker | Severity | Proof | Owner | Impact |",
        "| ------ | ------ | ------- | ------- | -------- | ----- | ----- | ------ |",
    ]
    for row in rows:
        lines.append(
            "| {row_id} | {source_stream} | {row_problem_kind} | {blocker_kind} | {severity} | {proof_eligibility} | {owner_ref} | {decision_impact} |"
            .format(**row))
    (root / output_dir / "redacted-blocker-register-report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


def copy_contract_snapshots(root: Path, output_dir: Path) -> list[str]:
    snapshot_dir = root / output_dir / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    refs: list[str] = []
    for snapshot_name, source_path in SOURCE_CONTRACT_SNAPSHOTS.items():
        source = root / source_path
        if not source.exists():
            raise VerificationError(
                f"missing contract snapshot source: {source_path.as_posix()}")
        destination = snapshot_dir / snapshot_name
        shutil.copy2(source, destination)
        refs.append(
            (output_dir / "contract-snapshots" / snapshot_name).as_posix())
    return refs


def generate_handoff(root: Path, output_dir: Path, rows: list[dict[str, Any]],
                     snapshot_refs: list[str]) -> dict[str, Any]:
    row_ids_by_kind: dict[str, list[str]] = {
        kind: []
        for kind in sorted(REQUIRED_ENUMS["blocker_kind"])
    }
    for row in rows:
        row_ids_by_kind[row["blocker_kind"]].append(row["row_id"])
    return {
        "artifact_name":
        "phase32-blocker-register-triage",
        "canonical_register_ref":
        (output_dir / "blocker-register.json").as_posix(),
        "contract_snapshot_refs":
        snapshot_refs,
        "generated_at_utc":
        utc_now(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "proof_policy":
        "blocker rows are visible for triage and proof-ineligible until later phases resolve them",
        "row_count":
        len(rows),
        "row_identities": [{
            "row_id":
            row["row_id"],
            "source_domain":
            row["source_domain"],
            "producer_phase":
            row["producer_phase"],
            "producer_artifact_kind":
            row["producer_artifact_kind"],
            "source_row_kind":
            row["source_row_kind"],
            "source_subject_id":
            row["source_subject_id"],
            "decision_axis":
            row["decision_axis"],
            "decision_subject_id":
            row["decision_subject_id"],
        } for row in rows],
        "row_ids_by_blocker_kind":
        row_ids_by_kind,
        "downstream_consumers": [
            "phase33-maintainer-decisions", "phase34-final-readiness",
            "phase35-cutover-decision"
        ],
    }


def run_quick(root: Path, phase31_output_dir: Path, phase27_output_dir: Path,
              phase28_output_dir: Path, output_dir: Path) -> None:
    load_contract(root)
    relative_output_dir = reset_output_root(root, output_dir)
    rows = [
        *load_phase31_rows(root, phase31_output_dir),
        *phase27_rows(root, phase27_output_dir),
        *phase28_rows(root, phase28_output_dir),
    ]
    validate_register_rows(rows)
    register = {
        "artifact_name": "phase32-blocker-register-triage",
        "generated_at_utc": utc_now(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "rows": rows,
    }
    write_json(root, relative_output_dir / "blocker-register.json", register)
    for filename, data in build_derived_views(rows).items():
        write_json(root, relative_output_dir / filename, data)
    snapshot_refs = copy_contract_snapshots(root, relative_output_dir)
    write_json(
        root, relative_output_dir / "downstream-handoff-manifest.json",
        generate_handoff(root, relative_output_dir, rows, snapshot_refs))
    write_report(root, relative_output_dir, rows)
    run_security_scan(root, relative_output_dir)
    print(
        f"wrote {len(rows)} blocker rows to {(relative_output_dir / 'blocker-register.json').as_posix()}"
    )


def normalized_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", field_name.casefold())


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(key for key in value
                           for forbidden_name in FORBIDDEN_FIELD_NAMES
                           if normalized_field_name(key) ==
                           normalized_field_name(forbidden_name))
        if forbidden:
            raise VerificationError(
                f"{path} contains forbidden fields: {', '.join(forbidden)}")
        for key, child in value.items():
            reject_forbidden_field_names(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden_field_names(child, f"{path}[{index}]")


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(
                f"{path.as_posix()} contains forbidden marker {label}: {match.group(0)}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def run_security_scan(root: Path,
                      output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    relative_output_dir = path_under(output_dir, DEFAULT_OUTPUT_DIR,
                                     "--output-dir")
    output_root = root / relative_output_dir
    if not output_root.exists():
        print(
            f"no Phase 32 outputs to scan at {relative_output_dir.as_posix()}")
        return
    if output_root.is_symlink() or not output_root.is_dir():
        raise VerificationError(
            f"Phase 32 output root is not a normal directory: {relative_output_dir.as_posix()}"
        )
    for path in sorted(output_root.rglob("*")):
        if path.is_dir():
            continue
        relative_path = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        reject_forbidden_text(relative_path, text)
        if path.suffix == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError as error:
                raise VerificationError(
                    f"{relative_path.as_posix()} is not valid JSON: {error}"
                ) from error
            reject_forbidden_field_names(data, relative_path.as_posix())
    print(f"security scan passed for {relative_output_dir.as_posix()}")


def check_wiring(root: Path) -> None:
    required_text = {
        Path("tools/bazel/BUILD.bazel"): [
            'name = "phase32_source_ref_manifests"',
            '"phase32_blocker_register_triage.py"',
            '"phase32_blocker_register_triage_test.py"',
            '"manifests/phase32_blocker_register_triage_contract.json"',
            'name = "phase32_verify"',
            'name = "phase32_verify_tests"',
        ],
        Path("BUILD.bazel"): [
            'name = "phase32_blocker_register_triage_docs"',
            'name = "phase32_verify"',
            'actual = "//tools/bazel:phase32_verify"',
            'name = "phase32_verify_tests"',
            'actual = "//tools/bazel:phase32_verify_tests"',
        ],
        Path("tools/bazel/rust_workflow.sh"): [
            "phase32_verify)",
            "phase32_verify_tests)",
            "python3 tools/bazel/phase32_blocker_register_triage.py --wiring-only",
        ],
        Path("justfile"): [
            "phase32-verify:",
            "bazel run //tools/bazel:phase32_verify_tests",
            "bazel run //tools/bazel:phase32_verify",
        ],
    }
    errors: list[str] = []
    for path, snippets in required_text.items():
        text = read_text(root, path)
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{path.as_posix()} missing {snippet}")
    if errors:
        raise VerificationError("\n".join(errors))
    print("phase32 wiring ok")


def contract_only() -> None:
    contract = load_contract()
    print(f"{contract['id']} ok")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 32 blocker register and evidence triage verifier")
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 32 contract and exit")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="write the Phase 32 quick blocker-register handoff bundle")
    parser.add_argument(
        "--security-only",
        action="store_true",
        help="scan Phase 32 generated outputs for secret or approval markers")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel/root/just workflow wiring")
    parser.add_argument("--phase31-output-dir",
                        default=DEFAULT_PHASE31_OUTPUT_DIR.as_posix())
    parser.add_argument("--phase27-output-dir",
                        default=DEFAULT_PHASE27_OUTPUT_DIR.as_posix())
    parser.add_argument("--phase28-output-dir",
                        default=DEFAULT_PHASE28_OUTPUT_DIR.as_posix())
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.contract_only:
            contract_only()
            return 0
        if args.security_only:
            run_security_scan(ROOT, Path(args.output_dir))
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            return 0
        if args.quick:
            run_quick(
                ROOT,
                Path(args.phase31_output_dir),
                Path(args.phase27_output_dir),
                Path(args.phase28_output_dir),
                Path(args.output_dir),
            )
            return 0
        raise VerificationError("no mode selected")
    except VerificationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
