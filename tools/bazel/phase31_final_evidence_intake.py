#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "31-final-evidence-intake"
PHASE_LIFECYCLE_ID = "31-2026-07-03T02-04-07"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase31_final_evidence_intake_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase31")
STREAM_ORDER = [
    "simulator", "hardware-media-safety", "live-service", "release-signing"
]
REQUIRED_STREAMS = set(STREAM_ORDER)
REQUIRED_REQUIREMENT_IDS = {"INTAKE-01", "INTAKE-02", "INTAKE-03", "INTAKE-04"}
SOURCE_CONTRACTS = [
    "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json",
    "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
    "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json",
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json",
]
PHASE31_DOCS = [
    ".planning/phases/31-final-evidence-intake/31-CONTEXT.md",
    ".planning/phases/31-final-evidence-intake/31-RESEARCH.md",
    ".planning/phases/31-final-evidence-intake/31-VALIDATION.md",
    ".planning/phases/31-final-evidence-intake/31-01-PLAN.md",
]
PHASE31_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase31_final_evidence_intake.py --wiring-only",
    "python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31",
]
PHASE31_TEST_COMMAND = "python3 tools/bazel/phase31_final_evidence_intake_test.py"
REF_LIST_FIELDS = {
    "artifact_refs", "evidence_refs", "retention_refs", "validator_output_refs"
}
REF_STRING_FIELDS = {"artifact_ref", "manifest_ref"}
PHASE31_ALLOWED_SOURCE_REF_ROOTS = [
    "build/ci-evidence/phase20/",
    "build/ci-evidence/phase23/",
    "build/ci-evidence/phase24/",
    "build/ci-evidence/phase25/",
    "build/ci-evidence/phase26/",
    "external://phase20/",
    "external://phase23/",
    "external://phase24/",
    "external://phase25/",
    "external://phase26/",
]
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api_key",
    "api_key_value",
    "auth_header",
    "authorization_header",
    "binary_dump",
    "binary_dump_bytes",
    "certificate_bytes",
    "certificate_pem",
    "client_secret",
    "connect_token",
    "cookie_header",
    "credential",
    "credential_value",
    "crash_dump_bytes",
    "firmware_payload",
    "firmware_payload_bytes",
    "password",
    "password_value",
    "private_certificate",
    "private_certificate_pem",
    "private_key",
    "raw_crash_dump",
    "raw_firmware_payload",
    "raw_key_bytes",
    "raw_log",
    "raw_log_bytes",
    "raw_logs",
    "secret",
    "secret_value",
    "service_payload",
    "service_payload_bytes",
    "signing_key_value",
    "signing_payload_bytes",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-block",
     re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
    (
        "forbidden-evidence-marker",
        re.compile(
            r"\b(access[_-]?token|api[_-]?key[_-]?value|auth(?:orization)?[_-]?header|"
            r"certificate[_-]?pem|client[_-]?secret|connect[_-]?token|cookie[_-]?header|"
            r"credential[_-]?value|password[_-]?value|"
            r"private[_-]?certificate|private[_-]?key|raw[_-]?crash[_-]?dump|raw[_-]?logs?|"
            r"secret[_-]?value|service[_-]?payload|signing[_-]?key[_-]?value|"
            r"signing[_-]?payload[_-]?bytes|tls[_-]?keylog|token[_-]?value|"
            r"wi[-_ ]?fi credential|wifi[_-]?password)\b",
            re.IGNORECASE,
        ),
    ),
)

from phase31_intake_policy import *
from phase31_intake_wiring import check_wiring
from phase31_intake_receipts import *


def rejection(stream: str,
              reason: str,
              submitter_identity_ref: str = "") -> dict[str, Any]:
    reason_digest = hashlib.sha256(reason.encode("utf-8")).hexdigest()[:12]
    return {
        "finality_status": "rejected-final",
        "reason": reason,
        "receipt_generated_at_utc": utc_now(),
        "stream": stream,
        "submission_id": f"phase31-{stream}-rejected-{reason_digest}",
        "submitter_identity_ref": submitter_identity_ref,
    }


def quick_rejections(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for stream in STREAM_ORDER:
        adapter = contract_adapters(contract)[stream]
        row = rejection(
            stream,
            "quick/default Phase 31 execution is a workflow smoke check and is quarantined as non-final evidence",
        )
        row["finality_status"] = "quarantined-non-final"
        row["requirement_ids"] = require_list_of_strings(
            adapter, "requirement_ids", f"{stream} adapter")
        rows.append(row)
    return rows


def copy_contract_snapshots(root: Path, output_dir: Path) -> None:
    snapshots_dir = root / output_dir / "contract-snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    for snapshot in [
            CONTRACT_MANIFEST, *[Path(path) for path in SOURCE_CONTRACTS]
    ]:
        shutil.copy2(root / snapshot, snapshots_dir / snapshot.name)


def write_phase31_outputs(root: Path, output_dir: Path,
                          receipts: list[dict[str, Any]],
                          rejected: list[dict[str, Any]]) -> None:
    receipt_refs: list[str] = []
    receipts_dir = output_dir / "stream-receipts"
    for receipt in receipts:
        stream = require_string(receipt, "stream", "receipt")
        receipt_name = {
            "simulator": "simulator-final-intake-receipt.json",
            "hardware-media-safety":
            "hardware-media-safety-final-intake-receipt.json",
            "live-service": "live-service-final-intake-receipt.json",
            "release-signing": "release-signing-final-intake-receipt.json",
        }[stream]
        receipt_path = receipts_dir / receipt_name
        write_json(root, receipt_path, receipt)
        receipt_refs.append(receipt_path.as_posix())
    rejected_path = output_dir / "rejected-submissions.json"
    write_json(
        root,
        rejected_path,
        {
            "generated_at_utc": utc_now(),
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "rejected_submissions": rejected,
        },
    )
    copy_contract_snapshots(root, output_dir)
    finality_status = "accepted-final" if receipts and not rejected else "quarantined-non-final"
    if rejected and any(
            row.get("finality_status") == "rejected-final"
            for row in rejected):
        finality_status = "rejected-final"
    manifest = {
        "accepted_count":
        len(receipts),
        "artifact_name":
        "phase31-final-evidence-intake",
        "finality_status":
        finality_status,
        "generated_at_utc":
        utc_now(),
        "output_root":
        output_dir.as_posix(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "receipt_refs":
        receipt_refs,
        "rejected_count":
        len(rejected),
        "rejected_submissions_ref":
        rejected_path.as_posix(),
        "streams": [{
            "finality_status": receipt["finality_status"],
            "receipt_ref": receipt_refs[index],
            "stream": receipt["stream"],
            "submission_id": receipt["submission_id"],
        } for index, receipt in enumerate(receipts)],
    }
    write_json(root, output_dir / "final-intake-manifest.json", manifest)


def run_quick(root: Path, output_dir: Path) -> None:
    contract = check_contract(root)
    check_security(root)
    relative_output_dir = reset_output_root(root, output_dir)
    write_phase31_outputs(root, relative_output_dir, [],
                          quick_rejections(contract))


def process_submission(root: Path, args: argparse.Namespace) -> None:
    contract = check_contract(root)
    check_security(root)
    adapters = contract_adapters(contract)
    relative_output_dir = reset_output_root(root, Path(args.output_dir))
    submitter_identity_ref = str(args.submitter_identity_ref or "")
    raw_by_stream = {
        "simulator": args.simulator_evidence_input,
        "hardware-media-safety": args.hardware_media_safety_evidence_input,
        "live-service": args.live_service_evidence_input,
        "release-signing": args.release_input,
    }
    retained_by_stream = {
        "simulator": args.phase23_retained_output,
        "hardware-media-safety": args.phase24_retained_output,
        "live-service": args.phase25_retained_output,
        "release-signing": args.phase26_retained_output,
    }
    upstream_rows: dict[str, Path] = {}
    for key, path_value in [
        ("phase23_simulator_row", args.phase23_simulator_row),
        ("phase24_hardware_media_safety_row",
         args.phase24_hardware_media_safety_row),
        ("phase25_live_service_row", args.phase25_live_service_row),
    ]:
        if path_value:
            allowed_root = {
                "phase23_simulator_row":
                Path("build/ci-evidence/phase23"),
                "phase24_hardware_media_safety_row":
                Path("build/ci-evidence/phase24"),
                "phase25_live_service_row":
                Path("build/ci-evidence/phase25"),
            }[key]
            upstream_rows[key] = require_existing_file_under(
                root, path_value, allowed_root, key)

    receipts: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for stream in STREAM_ORDER:
        adapter = adapters[stream]
        raw_path_value = raw_by_stream[stream]
        retained_path_value = retained_by_stream[stream]
        if not raw_path_value and not retained_path_value:
            continue
        if raw_path_value and retained_path_value:
            rejected.append(
                rejection(
                    stream,
                    "raw input and retained output registration are mutually exclusive",
                    submitter_identity_ref))
            continue
        if not submitter_identity_ref:
            rejected.append(
                rejection(
                    stream,
                    "submitter_identity_ref is required for final evidence intake"
                ))
            continue
        try:
            if raw_path_value:
                raw_path, packet_hash = validate_raw_input(
                    root, raw_path_value, f"{stream} raw input")
                command = run_source_validator(root, adapter, raw_path,
                                               upstream_rows)
                source_output_dir = Path(
                    require_string(adapter, "output_root",
                                   f"{stream} adapter"))
            else:
                source_output_dir = retained_output_dir(
                    root, adapter, retained_path_value)
                manifest_path = source_output_dir / require_string(
                    adapter, "manifest", f"{stream} adapter")
                if stream == "release-signing":
                    row_path = source_output_dir / require_string(
                        adapter, "upstream_row_table", f"{stream} adapter")
                else:
                    row_path = source_output_dir / require_string(
                        adapter, "upstream_row", f"{stream} adapter")
                for required_path in [manifest_path, row_path]:
                    require_existing_file_under(root, required_path,
                                                source_output_dir,
                                                "retained source output")
                packet_hash = paths_sha256(root, [manifest_path, row_path])
                command = [
                    "registered-retained-output",
                    source_output_dir.as_posix()
                ]
            receipt, upstream_path = validate_stream_output(
                root, adapter, source_output_dir, submitter_identity_ref,
                command, packet_hash)
            receipts.append(receipt)
            if stream == "simulator":
                upstream_rows["phase23_simulator_row"] = upstream_path
            elif stream == "hardware-media-safety":
                upstream_rows[
                    "phase24_hardware_media_safety_row"] = upstream_path
            elif stream == "live-service":
                upstream_rows["phase25_live_service_row"] = upstream_path
        except VerificationError as error:
            rejected.append(
                rejection(stream, str(error), submitter_identity_ref))
    write_phase31_outputs(root, relative_output_dir, receipts, rejected)
    if rejected:
        reasons = "\n".join(f"- {row['stream']}: {row['reason']}"
                            for row in rejected)
        raise VerificationError(
            f"Phase 31 rejected final submissions:\n{reasons}")


def submission_requested(args: argparse.Namespace) -> bool:
    return any([
        args.simulator_evidence_input,
        args.hardware_media_safety_evidence_input,
        args.live_service_evidence_input,
        args.release_input,
        args.phase23_retained_output,
        args.phase24_retained_output,
        args.phase25_retained_output,
        args.phase26_retained_output,
    ])


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=
        "Validate Phase 31 final evidence intake receipts over Phase 23-26 outputs."
    )
    parser.add_argument("--contract-only",
                        action="store_true",
                        help="validate the Phase 31 wrapper contract")
    parser.add_argument(
        "--security-only",
        action="store_true",
        help="scan Phase 31 checked-in policy for raw secret blocks")
    parser.add_argument("--wiring-only",
                        action="store_true",
                        help="validate Bazel, rust workflow, and just wiring")
    parser.add_argument("--quick",
                        action="store_true",
                        help="write quarantined non-final smoke outputs")
    parser.add_argument(
        "--simulator-evidence-input",
        help="sanitized final simulator evidence packet for Phase 23")
    parser.add_argument(
        "--hardware-media-safety-evidence-input",
        help="sanitized final hardware/media/safety packet for Phase 24")
    parser.add_argument(
        "--live-service-evidence-input",
        help="sanitized final live-service packet for Phase 25")
    parser.add_argument(
        "--release-input",
        help="sanitized final release/signing/provenance packet for Phase 26")
    parser.add_argument(
        "--phase23-retained-output",
        help="repo-relative Phase 23 retained output directory")
    parser.add_argument(
        "--phase24-retained-output",
        help="repo-relative Phase 24 retained output directory")
    parser.add_argument(
        "--phase25-retained-output",
        help="repo-relative Phase 25 retained output directory")
    parser.add_argument(
        "--phase26-retained-output",
        help="repo-relative Phase 26 retained output directory")
    parser.add_argument(
        "--phase23-simulator-row",
        help="optional Phase 23 upstream row for release intake")
    parser.add_argument(
        "--phase24-hardware-media-safety-row",
        help="optional Phase 24 upstream row for release intake")
    parser.add_argument(
        "--phase25-live-service-row",
        help="optional Phase 25 upstream row for release intake")
    parser.add_argument(
        "--submitter-identity-ref",
        help="opaque non-secret identity reference recorded as provenance")
    parser.add_argument("--output-dir",
                        default=DEFAULT_OUTPUT_DIR.as_posix(),
                        help="Phase 31 output directory")
    args = parser.parse_args(argv)
    explicit_mode_count = sum(
        bool(mode) for mode in
        [args.contract_only, args.security_only, args.wiring_only, args.quick])
    requested_submission = submission_requested(args)
    if explicit_mode_count + int(requested_submission) != 1:
        parser.error(
            "select exactly one mode: contract/security/wiring/quick or final evidence submission"
        )
    upstream_rows_requested = any([
        args.phase23_simulator_row, args.phase24_hardware_media_safety_row,
        args.phase25_live_service_row
    ])
    if upstream_rows_requested and not args.release_input:
        parser.error(
            "Phase 23-25 upstream row flags are only valid with --release-input"
        )
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 31 final evidence intake contract passed")
        elif args.security_only:
            check_security(ROOT)
            print("Phase 31 final evidence intake security scan passed")
        elif args.wiring_only:
            check_wiring(ROOT)
            print("Phase 31 final evidence intake wiring passed")
        elif args.quick:
            run_quick(ROOT, Path(args.output_dir))
            print("Phase 31 final evidence intake quick validation passed")
        else:
            process_submission(ROOT, args)
            print("Phase 31 final evidence intake accepted final submissions")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
