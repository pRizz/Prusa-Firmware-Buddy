from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from phase31_intake_policy import *


def validate_raw_input(root: Path, path_value: str,
                       row_name: str) -> tuple[Path, str]:
    relative_path = require_existing_file(root, path_value, row_name)
    text = read_text(root, relative_path)
    reject_forbidden_text(relative_path, text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{relative_path.as_posix()} is not valid JSON evidence: {error}"
        ) from error
    reject_secret_bearing_json(relative_path, data)
    return relative_path, file_sha256(root, relative_path)


def run_source_validator(root: Path, adapter: dict[str,
                                                   Any], raw_input_path: Path,
                         maybe_upstream_rows: dict[str, Path]) -> list[str]:
    validator = require_string(adapter, "validator",
                               f"{adapter['stream']} adapter")
    validator_path = root / validator
    output_root = require_string(adapter, "output_root",
                                 f"{adapter['stream']} adapter")
    if adapter["stream"] == "release-signing":
        command = [
            sys.executable,
            validator_path.as_posix(),
            "--quick",
            "--release-input",
            raw_input_path.as_posix(),
            "--output-dir",
            output_root,
        ]
        row_flags = [
            ("phase23_simulator_row", "--phase23-simulator-row"),
            ("phase24_hardware_media_safety_row",
             "--phase24-hardware-media-safety-row"),
            ("phase25_live_service_row", "--phase25-live-service-row"),
        ]
        for key, flag in row_flags:
            maybe_path = maybe_upstream_rows.get(key)
            if maybe_path is not None:
                command.extend([flag, maybe_path.as_posix()])
    else:
        command = [
            sys.executable,
            validator_path.as_posix(),
            require_string(adapter, "source_validator_input_flag",
                           f"{adapter['stream']} adapter"),
            raw_input_path.as_posix(),
            "--output-dir",
            output_root,
        ]
    result = subprocess.run(
        command,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        raise VerificationError(
            f"{adapter['stream']} source validator failed with exit {result.returncode}:\n{result.stdout.strip()}"
        )
    return [
        "python3",
        validator,
        *command[2:],
    ]


def retained_output_dir(root: Path, adapter: dict[str, Any],
                        path_value: str | Path) -> Path:
    output_root = Path(
        require_string(adapter, "output_root", f"{adapter['stream']} adapter"))
    return require_existing_dir_under(root, path_value, output_root,
                                      f"{adapter['stream']} retained output")


def status_field(rows: list[dict[str, Any]], field: str, default: str) -> str:
    values = sorted({
        str(row.get(field, default))
        for row in rows if row.get(field, default) not in ("", None)
    })
    if not values:
        return default
    if len(values) == 1:
        return values[0]
    return "mixed"


def collect_artifact_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REF_LIST_FIELDS and isinstance(child, list):
                refs.extend(
                    str(item) for item in child
                    if isinstance(item, str) and item)
            elif key in REF_STRING_FIELDS and isinstance(child, str) and child:
                refs.append(child)
            else:
                refs.extend(collect_artifact_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(collect_artifact_refs(child))
    return list(dict.fromkeys(refs))


def validate_source_row(row: dict[str, Any], adapter: dict[str, Any],
                        row_name: str) -> tuple[str, str, str]:
    reject_secret_bearing_json(Path(row_name), row)
    validate_refs_in_json(row, adapter, row_name)
    if row.get("redaction_status") != "passed":
        raise VerificationError(f"{row_name} redaction_status must be passed")
    if row.get("source_ref_status") != "passed":
        raise VerificationError(f"{row_name} source_ref_status must be passed")
    maybe_lifecycle_status = row.get("source_lifecycle_status")
    if maybe_lifecycle_status not in (None, "current", "not-required"):
        raise VerificationError(
            f"{row_name} source_lifecycle_status must be current or not-required"
        )
    return (
        str(row.get("redaction_status", "passed")),
        str(row.get("source_ref_status", "passed")),
        str(row.get("exception_status", "none")),
    )


def validate_stream_output(
    root: Path,
    adapter: dict[str, Any],
    output_dir: Path,
    submitter_identity_ref: str,
    validator_command: list[str],
    packet_sha256: str,
) -> tuple[dict[str, Any], Path]:
    stream = require_string(adapter, "stream", "adapter")
    manifest_path = output_dir / require_string(adapter, "manifest",
                                                f"{stream} adapter")
    require_existing_file_under(root, manifest_path, output_dir,
                                f"{stream} manifest")
    manifest = load_json(root, manifest_path)
    reject_secret_bearing_json(manifest_path, manifest)
    validate_refs_in_json(manifest, adapter, f"{stream} manifest")
    expected_lifecycle_id = require_string(adapter, "source_lifecycle_id",
                                           f"{stream} adapter")
    if manifest.get("phase_lifecycle_id") != expected_lifecycle_id:
        raise VerificationError(
            f"{stream} manifest phase_lifecycle_id must be {expected_lifecycle_id}"
        )
    real_evidence_flag = require_string(adapter, "real_evidence_flag",
                                        f"{stream} adapter")
    if not require_bool(manifest, real_evidence_flag, f"{stream} manifest"):
        raise VerificationError(
            f"{stream} manifest {real_evidence_flag} must be true for final intake"
        )
    if str(manifest.get("command_mode", "")).casefold() in {
            "quick-placeholder", "default-placeholder", "local-smoke"
    }:
        raise VerificationError(
            f"{stream} manifest command_mode is non-final: {manifest.get('command_mode')}"
        )

    if stream == "release-signing":
        upstream_path = output_dir / require_string(
            adapter, "upstream_row_table", f"{stream} adapter")
        require_existing_file_under(root, upstream_path, output_dir,
                                    f"{stream} upstream row table")
        row_table = load_json(root, upstream_path)
        rows = require_list(row_table, "rows",
                            "release-signing upstream row table")
        if not rows or not all(isinstance(row, dict) for row in rows):
            raise VerificationError(
                "release-signing upstream row table rows must contain objects")
        release_ref_adapter = adapter_with_allowed_ref_roots(
            adapter, PHASE31_ALLOWED_SOURCE_REF_ROOTS)
        for row in rows:
            validate_source_row(
                row, release_ref_adapter,
                f"{stream} upstream row {row.get('criterion_id', '<missing>')}"
            )
        redaction_status = status_field(rows, "redaction_status", "passed")
        source_ref_status = status_field(rows, "source_ref_status", "passed")
        exception_status = status_field(rows, "exception_status", "none")
        failure_reason = "; ".join(
            str(row.get("failure_reason")) for row in rows
            if isinstance(row, dict) and row.get("status") not in
            {"passed", "not-required"} and row.get("failure_reason"))
        artifact_reference_summary_path = output_dir / "artifact-reference-summary.json"
        if (root / artifact_reference_summary_path).is_file():
            require_existing_file_under(
                root,
                artifact_reference_summary_path,
                output_dir,
                "release-signing artifact reference summary",
            )
            artifact_reference_summary = load_json(
                root, artifact_reference_summary_path)
            reject_secret_bearing_json(artifact_reference_summary_path,
                                       artifact_reference_summary)
            validate_refs_in_json(
                artifact_reference_summary, release_ref_adapter,
                "release-signing artifact reference summary")
        else:
            artifact_reference_summary = {
                "artifact_refs": collect_artifact_refs(rows)
            }
    else:
        upstream_path = output_dir / require_string(adapter, "upstream_row",
                                                    f"{stream} adapter")
        require_existing_file_under(root, upstream_path, output_dir,
                                    f"{stream} upstream row")
        row = load_json(root, upstream_path)
        redaction_status, source_ref_status, exception_status = validate_source_row(
            row, adapter, f"{stream} upstream row")
        failure_reason = str(row.get("failure_reason", ""))
        artifact_reference_summary = {
            "artifact_refs": collect_artifact_refs(row)
        }

    receipt = {
        "artifact_reference_summary":
        artifact_reference_summary,
        "consumed_upstream_row_refs": [upstream_path.as_posix()],
        "exception_status":
        exception_status,
        "failure_reason":
        failure_reason,
        "finality_status":
        "accepted-final",
        "packet_sha256":
        packet_sha256,
        "receipt_generated_at_utc":
        utc_now(),
        "redaction_status":
        redaction_status,
        "requirement_ids":
        require_list_of_strings(adapter, "requirement_ids",
                                f"{stream} adapter"),
        "source_contract":
        require_string(adapter, "source_contract", f"{stream} adapter"),
        "source_phase":
        require_string(adapter, "source_phase", f"{stream} adapter"),
        "source_ref_status":
        source_ref_status,
        "stream":
        stream,
        "submission_id":
        f"phase31-{stream}-{packet_sha256[:12]}",
        "submitter_identity_ref":
        submitter_identity_ref,
        "validator_command":
        validator_command,
        "validator_output_refs":
        [manifest_path.as_posix(),
         upstream_path.as_posix()],
    }
    return receipt, upstream_path
