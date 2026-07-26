#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from phase34_decision_reconciliation import reconcile_decision_rows


ROOT = Path(__file__).resolve().parents[2]
PHASE = "34-final-readiness-and-demotion-dry-run"
PHASE_LIFECYCLE_ID = "34-2026-07-25T18-18-48"
PHASE31_LIFECYCLE_ID = "31-2026-07-03T02-04-07"
PHASE32_LIFECYCLE_ID = "32-2026-07-03T14-13-51"
PHASE33_LIFECYCLE_ID = "33-2026-07-04T01-36-41"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json")
PHASE31_CONTRACT = Path("tools/bazel/manifests/phase31_final_evidence_intake_contract.json")
PHASE32_CONTRACT = Path("tools/bazel/manifests/phase32_blocker_register_triage_contract.json")
PHASE33_CONTRACT = Path("tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json")
PHASE28_CONTRACT = Path("tools/bazel/manifests/phase28_final_readiness_packet_contract.json")
DEFAULT_PHASE31_OUTPUT_DIR = Path("build/ci-evidence/phase31")
DEFAULT_PHASE31_MANIFEST = DEFAULT_PHASE31_OUTPUT_DIR / "final-intake-manifest.json"
DEFAULT_PHASE33_HANDOFF = Path("build/ci-evidence/phase33/downstream-handoff-manifest.json")
PHASE33_OUTPUT_ROOT = Path("build/ci-evidence/phase33")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase34")
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
REQUIRED_REQUIREMENT_IDS = ["READY-01", "READY-02", "READY-03"]
REQUIRED_PHASE31_STREAMS = (
    "simulator",
    "hardware-media-safety",
    "live-service",
    "release-signing",
)
LEDGER_FIELDS = [
    "row_id",
    "ledger_row_kind",
    "source_domain",
    "producer_phase",
    "producer_artifact_kind",
    "source_row_kind",
    "source_subject_id",
    "decision_axis",
    "decision_subject_id",
    "phase_lifecycle_id",
    "source_stream",
    "source_ref",
    "requirement_ids",
    "affected_gates",
    "proof_eligibility",
    "evidence_status",
    "row_problem_kind",
    "blocker_kind",
    "severity",
    "evidence_refs",
    "artifact_refs",
    "classification_ref",
    "retained_code_decision_refs",
    "residual_risk_decision_refs",
    "exception_decision_refs",
    "readiness_decision_refs",
    "demotion_decision_refs",
    "coverage_state",
    "readiness_effect",
    "reason_codes",
]
GENERATED_ARTIFACTS = [
    "final-readiness-run-manifest.json",
    "readiness-coverage-ledger.json",
    "final-readiness-packet.json",
    "readiness-blocker-summary.json",
    "demotion-dry-run.json",
    "redacted-readiness-report.md",
    "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase33-downstream-handoff-manifest.json",
    "contract-snapshots/phase32-blocker-register.json",
    "contract-snapshots/phase31-final-intake-manifest.json",
    "contract-snapshots/phase31-accepted-receipts.json",
]
HARD_BLOCKER_PROBLEM_KINDS = {
    "redaction_failed",
    "source_ref_failed",
    "secret_tainted",
    "lifecycle_mismatch",
    "unsafe_ref",
}
PROBLEM_REASON_CODES = {
    "missing": "required-row-missing",
    "failed": "evidence-failed",
    "stale": "evidence-stale",
    "malformed": "evidence-malformed",
    "redaction_failed": "redaction-failed",
    "source_ref_failed": "source-ref-failed",
    "secret_tainted": "secret-tainted",
    "lifecycle_mismatch": "lifecycle-mismatched",
    "unsafe_ref": "unsafe-ref",
    "non_final_placeholder": "non-final-evidence",
    "smoke_fixture": "non-final-evidence",
    "local_dry_run": "non-final-evidence",
    "prose_attestation": "non-final-evidence",
    "row_only_submission": "non-final-evidence",
    "unknown_unclassified": "unknown-classification",
}
PHASE33_REQUIRED_DECISION_FIELDS = [
    "decision_id",
    "decision_type",
    "decision_value",
    "source_row_refs",
    "decision_targets",
    "maintainer_identity_ref",
    "maintainer_role",
    "owner_signoff_ref",
    "decision_timestamp",
    "rationale",
    "evidence_refs",
    "artifact_refs",
]
PHASE33_DECISION_VALUE_ENUMS = {
    "retained_code": {"accept", "reject", "exception_approve"},
    "residual_risk": {"accept", "reject"},
    "exception": {"approve", "reject"},
    "readiness": {"approve", "block"},
    "reference_demotion": {"approve", "reject"},
}
PHASE33_DECISION_AXES = {
    "retained_code": "retained_code",
    "residual_risk": "residual_risk",
    "exception": "exception",
    "readiness": "readiness",
    "reference_demotion": "demotion",
}
DECISION_DOMAIN_PRODUCER_PHASES = {"phase27", "phase28"}
EXPECTED_GATE_BY_STREAM = {
    "simulator": "final-simulator-evidence",
    "hardware-media-safety": "final-hardware-safety-media-evidence",
    "live-service": "final-live-network-transfer-evidence",
    "release-signing": "final-release-artifact-signing-evidence",
    "upstream-result": "final-upstream-result-evidence",
    "retained-code": "final-retained-code-acceptance",
    "readiness": "final-readiness",
    "unknown": "cutover-decision",
}
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api_key",
    "authorization_header",
    "certificate_private_material",
    "client_secret",
    "connect_token",
    "credential_value",
    "demotion_allowed",
    "password",
    "private_key",
    "raw_crash_dump",
    "raw_release_log",
    "secret",
    "secret_value",
    "service_payload",
    "signing_key_value",
    "signing_payload_bytes",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("bearer-token", re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE)),
    ("service-payload", re.compile(r"\bservice[_ -]?payload\b", re.IGNORECASE)),
    ("raw-crash-dump", re.compile(r"\braw[_ -]?crash[_ -]?dump\b", re.IGNORECASE)),
    ("demotion-allowed", re.compile(r'"?demotion_allowed"?\s*:', re.IGNORECASE)),
    ("evidence-demotion-overclaim", re.compile(r"\breference demotion approved by evidence\b", re.IGNORECASE)),
    ("production-demotion", re.compile(r"\bproduction demotion complete\b", re.IGNORECASE)),
    ("cutover-verdict", re.compile(r"\bcutover verdict approved\b", re.IGNORECASE)),
    ("evidence-alone", re.compile(r"\baccepted by evidence alone\b", re.IGNORECASE)),
)
NON_SNAPSHOT_OUTPUTS = [
    artifact
    for artifact in GENERATED_ARTIFACTS
    if not artifact.startswith("contract-snapshots/")
]
PHASE34_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31",
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26",
    (
        "python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick "
        "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
        "--output-dir build/ci-evidence/phase27"
    ),
    (
        "python3 tools/bazel/phase28_final_readiness_packet.py --quick "
        "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
        "--phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json "
        "--output-dir build/ci-evidence/phase28"
    ),
    (
        "python3 tools/bazel/phase32_blocker_register_triage.py --quick "
        "--phase31-output-dir build/ci-evidence/phase31 "
        "--phase27-output-dir build/ci-evidence/phase27 "
        "--phase28-output-dir build/ci-evidence/phase28 "
        "--output-dir build/ci-evidence/phase32"
    ),
    (
        "python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick "
        "--phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json "
        "--output-dir build/ci-evidence/phase33"
    ),
    "python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --wiring-only",
    (
        "python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --quick "
        "--phase31-output-dir build/ci-evidence/phase31 "
        "--phase33-handoff build/ci-evidence/phase33/downstream-handoff-manifest.json "
        "--output-dir build/ci-evidence/phase34"
    ),
]
SOURCE_FAILURE_REASON_CODES = [
    "phase31-input-invalid",
    "phase33-handoff-invalid",
    "phase33-normalized-decisions-invalid",
    "phase33-readiness-input-invalid",
    "phase33-register-invalid",
    "phase32-blocker-register-invalid",
    "phase33-demotion-input-invalid",
]
SOURCE_FAILURE_AUTHORITY_FIELDS = {
    "readiness_state": "blocked",
    "cutover_verdict_state": "blocked",
    "production_cutover_route_state": "blocked",
    "demotion_gate_state": "blocked",
}


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(root: Path, relative_path: Path, field: str | None = None) -> dict[str, Any]:
    full_path = root / relative_path
    if not full_path.is_file():
        raise VerificationError(f"missing required file: {relative_path.as_posix()}")
    try:
        value = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{relative_path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise VerificationError(f"{field or relative_path.as_posix()} must contain a top-level object")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError(f"{field} must be a list")
    return value


def string_list(value: Any, field: str) -> list[str]:
    values = require_list(value, field)
    if not all(isinstance(item, str) and item.strip() for item in values):
        raise VerificationError(f"{field} must contain non-blank strings")
    return values


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VerificationError(f"{field} must be a non-blank string")
    return value


def require_iso_utc(timestamp_text: str, field: str) -> None:
    if not timestamp_text.endswith("Z"):
        raise VerificationError(f"{field} must be ISO UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(f"{field} must be ISO UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise VerificationError(f"{field} must be ISO UTC")


def normalized_field_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


FORBIDDEN_NORMALIZED_FIELDS = {normalized_field_name(value) for value in FORBIDDEN_FIELD_NAMES}


def reject_forbidden_fields(value: Any, source: str, candidate_path: str = "$") -> None:
    errors: list[str] = []

    def walk(candidate: Any, current_path: str) -> None:
        if isinstance(candidate, dict):
            for key, nested in candidate.items():
                nested_path = f"{current_path}.{key}"
                if normalized_field_name(str(key)) in FORBIDDEN_NORMALIZED_FIELDS:
                    errors.append(f"{source} contains forbidden field {key} at {nested_path}")
                walk(nested, nested_path)
        elif isinstance(candidate, list):
            for index, nested in enumerate(candidate):
                walk(nested, f"{current_path}[{index}]")

    walk(value, candidate_path)
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_text(relative_path: Path, text: str) -> None:
    errors = [
        f"{relative_path.as_posix()} contains forbidden marker {label}"
        for label, pattern in FORBIDDEN_TEXT_PATTERNS
        if pattern.search(text)
    ]
    if errors:
        raise VerificationError("\n".join(errors))


def scan_json(value: dict[str, Any], source: Path) -> None:
    reject_forbidden_fields(value, source.as_posix())
    reject_forbidden_text(source, json.dumps(value, sort_keys=True))
    validate_refs(value, source.as_posix())


def repo_relative_path(value: str | Path, field: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        raise VerificationError(f"{field} must be repo-relative: {candidate.as_posix()}")
    if ".." in candidate.parts:
        raise VerificationError(f"{field} contains parent traversal: {candidate.as_posix()}")
    return candidate


def path_under(value: str | Path, expected_root: Path, field: str) -> Path:
    candidate = repo_relative_path(value, field)
    try:
        candidate.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"{field} must be under {expected_root.as_posix()}: {candidate.as_posix()}") from error
    return candidate


def resolved_under(root: Path, relative_path: Path, expected_root: Path, field: str) -> Path:
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(f"{field} contains a symlink escape: {relative_path.as_posix()}")
    full_path = (root / relative_path).resolve(strict=False)
    expected = (root / expected_root).resolve(strict=False)
    try:
        full_path.relative_to(expected)
    except ValueError as error:
        raise VerificationError(f"{field} resolves outside {expected_root.as_posix()}: {relative_path.as_posix()}") from error
    return full_path


def output_paths(root: Path, output_arg: str | Path) -> tuple[Path, Path]:
    relative_output = path_under(output_arg, DEFAULT_OUTPUT_DIR, "--output-dir")
    full_output = resolved_under(root, relative_output, DEFAULT_OUTPUT_DIR, "--output-dir")
    return relative_output, full_output


def validate_refs(value: Any, field: str) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("_ref") and isinstance(nested, str) and nested:
                validate_ref(nested, f"{field}.{key}")
            elif key.endswith("_refs") and isinstance(nested, list):
                for index, ref in enumerate(nested):
                    if not isinstance(ref, str):
                        raise VerificationError(f"{field}.{key}[{index}] must be a string")
                    validate_ref(ref, f"{field}.{key}[{index}]")
            else:
                validate_refs(nested, f"{field}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            validate_refs(nested, f"{field}[{index}]")


def validate_ref(value: str, field: str) -> None:
    if value.startswith(("external://", "maintainer://", "owner://")):
        return
    repo_relative_path(value.split("#", 1)[0], field)


def validate_contract(contract: dict[str, Any]) -> None:
    expected = {
        "schema_version": "1",
        "id": "phase34_final_readiness_demotion_dry_run_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase34-final-readiness-demotion-dry-run",
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, value in expected.items():
        if contract.get(field) != value:
            raise VerificationError(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {value!r}")
    if string_list(contract.get("requirement_ids"), "requirement_ids") != REQUIRED_REQUIREMENT_IDS:
        raise VerificationError("requirement_ids must be READY-01, READY-02, READY-03")
    ledger_schema = contract.get("ledger_schema")
    if not isinstance(ledger_schema, dict) or string_list(ledger_schema.get("required_fields"), "ledger fields") != LEDGER_FIELDS:
        raise VerificationError("ledger_schema.required_fields must match the Phase 34 interface")
    if ledger_schema.get("row_kinds") != ["evidence", "decision-domain"]:
        raise VerificationError("ledger_schema.row_kinds must define evidence and decision-domain rows")
    decision_policy = contract.get("decision_domain_policy")
    if not isinstance(decision_policy, dict):
        raise VerificationError("decision_domain_policy must be an object")
    if decision_policy.get("canonical_rows_from") != "phase32 canonical Phase 27/28 decision-domain rows":
        raise VerificationError("decision-domain rows must come from canonical Phase 32 Phase 27/28 rows")
    if decision_policy.get("evidence_authority") != "phase31 accepted-final receipts only":
        raise VerificationError("Phase 31 must remain the sole evidence authority")
    if decision_policy.get("exact_decision_target_fields") != [
        "row_ref",
        "decision_axis",
        "decision_subject_id",
    ]:
        raise VerificationError("decision targets must use the exact typed identity")
    if decision_policy.get("readiness_and_demotion_are_orthogonal") is not True:
        raise VerificationError("readiness and demotion must remain orthogonal")
    if string_list(contract.get("generated_artifacts"), "generated_artifacts") != GENERATED_ARTIFACTS:
        raise VerificationError("generated_artifacts must list the exact Phase 34 bundle")
    source_contracts = require_list(contract.get("source_contracts"), "source_contracts")
    source_ids = [row.get("id") for row in source_contracts if isinstance(row, dict)]
    if source_ids != [
        "phase31_final_evidence_intake_contract",
        "phase32_blocker_register_triage_contract",
        "phase33_maintainer_decision_inputs_contract",
        "phase28_final_readiness_packet_contract",
    ]:
        raise VerificationError("source_contracts must list Phase 31, 32, 33, and precedent-only Phase 28")
    source_inputs = contract.get("source_inputs")
    if not isinstance(source_inputs, dict) or source_inputs.get("raw_evidence_consumed") is not False:
        raise VerificationError("source_inputs.raw_evidence_consumed must be false")
    overlay_policy = contract.get("sparse_blocker_overlay_policy")
    if not isinstance(overlay_policy, dict):
        raise VerificationError("sparse_blocker_overlay_policy must be an object")
    if overlay_policy.get("required_streams_from") != "phase31 contract stream_adapters":
        raise VerificationError("required streams must derive from Phase 31 stream_adapters")
    if overlay_policy.get("absent_required_stream_state") != "required-row-missing":
        raise VerificationError("absent required streams must use required-row-missing")
    open_requires = contract.get("demotion_dry_run_schema", {}).get("open_requires")
    if open_requires != {
        "readiness_state": "unblocked",
        "approval_validation_state": "valid",
        "approval_decision_state": "approve",
    }:
        raise VerificationError("demotion dry-run open predicate is invalid")
    source_failure_policy = contract.get("source_failure_policy")
    if not isinstance(source_failure_policy, dict):
        raise VerificationError("source_failure_policy must be an object")
    if source_failure_policy.get("reason_codes") != SOURCE_FAILURE_REASON_CODES:
        raise VerificationError(
            "source_failure_policy.reason_codes must list the exact safe vocabulary"
        )
    if (
        source_failure_policy.get("blocked_authority_fields")
        != SOURCE_FAILURE_AUTHORITY_FIELDS
    ):
        raise VerificationError(
            "source_failure_policy.blocked_authority_fields must block every authority projection"
        )
    if source_failure_policy.get("copies_source_payloads") is not False:
        raise VerificationError(
            "source_failure_policy.copies_source_payloads must be false"
        )


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    validate_contract(contract)
    return contract


def load_phase31_required_streams(root: Path) -> dict[str, dict[str, Any]]:
    contract = load_json(root, PHASE31_CONTRACT)
    if contract.get("id") != "phase31_final_evidence_intake_contract":
        raise VerificationError("Phase 31 contract id must be phase31_final_evidence_intake_contract")
    if contract.get("phase_lifecycle_id") != PHASE31_LIFECYCLE_ID:
        raise VerificationError(f"Phase 31 contract phase_lifecycle_id must be {PHASE31_LIFECYCLE_ID}")

    required_streams: dict[str, dict[str, Any]] = {}
    for index, adapter in enumerate(require_list(contract.get("stream_adapters"), "Phase 31 stream_adapters")):
        if not isinstance(adapter, dict):
            raise VerificationError(f"Phase 31 stream_adapters[{index}] must be an object")
        stream = require_string(adapter.get("stream"), f"Phase 31 stream_adapters[{index}].stream")
        if stream in required_streams:
            raise VerificationError(f"duplicate Phase 31 stream adapter: {stream}")
        if stream not in REQUIRED_PHASE31_STREAMS:
            raise VerificationError(f"unknown Phase 31 required stream: {stream}")
        output_root = repo_relative_path(
            require_string(adapter.get("output_root"), f"{stream}.output_root"),
            f"{stream}.output_root",
        )
        maybe_upstream_row = adapter.get("upstream_row")
        maybe_upstream_table = adapter.get("upstream_row_table")
        if (isinstance(maybe_upstream_row, str) and maybe_upstream_row) == (
            isinstance(maybe_upstream_table, str) and maybe_upstream_table
        ):
            raise VerificationError(f"{stream} must declare exactly one upstream row or row table")
        upstream_name = maybe_upstream_row if isinstance(maybe_upstream_row, str) else maybe_upstream_table
        upstream_path = repo_relative_path(
            require_string(upstream_name, f"{stream}.upstream row"),
            f"{stream}.upstream row",
        )
        expected_source_ref = (output_root / upstream_path).as_posix()
        required_streams[stream] = {
            "stream": stream,
            "requirement_ids": string_list(adapter.get("requirement_ids"), f"{stream}.requirement_ids"),
            "expected_source_ref": expected_source_ref,
            "expected_gate": EXPECTED_GATE_BY_STREAM[stream],
        }

    if set(required_streams) != set(REQUIRED_PHASE31_STREAMS):
        missing = sorted(set(REQUIRED_PHASE31_STREAMS) - set(required_streams))
        raise VerificationError(f"Phase 31 stream_adapters missing required streams: {', '.join(missing)}")
    return required_streams


def stable_row_id(stream: str, source_ref: str) -> str:
    digest = hashlib.sha256(f"{stream}\0{source_ref}".encode()).hexdigest()[:12]
    return f"phase34-{stream}-{digest}"


def receipt_problem_kind(receipt: dict[str, Any]) -> str:
    if receipt.get("redaction_status") != "passed":
        return "redaction_failed"
    if receipt.get("source_ref_status") != "passed":
        return "source_ref_failed"
    if receipt.get("finality_status") != "accepted-final":
        return "non_final_placeholder"
    evidence_status = str(receipt.get("evidence_status") or ("failed" if receipt.get("failure_reason") else "passed"))
    if evidence_status not in {"passed", "eligible"}:
        return evidence_status
    if receipt.get("exception_status") not in {None, "", "none"}:
        return "exception_requested"
    return ""


def derive_evidence_rows(
    receipts: list[dict[str, Any]],
    required_streams: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_refs: set[str] = set()
    duplicate_refs: set[str] = set()
    for receipt in receipts:
        stream = str(receipt.get("stream") or "unknown")
        consumed_refs = string_list(receipt.get("consumed_upstream_row_refs"), f"{stream}.consumed_upstream_row_refs")
        for source_ref in consumed_refs:
            if source_ref in seen_refs:
                duplicate_refs.add(source_ref)
            seen_refs.add(source_ref)
            problem_kind = receipt_problem_kind(receipt)
            artifact_summary = receipt.get("artifact_reference_summary")
            artifact_refs = []
            if isinstance(artifact_summary, dict):
                maybe_refs = artifact_summary.get("artifact_refs", [])
                if isinstance(maybe_refs, list):
                    artifact_refs = sorted({str(ref) for ref in maybe_refs if isinstance(ref, str) and ref})
            rows.append(
                {
                    "row_id": stable_row_id(stream, source_ref),
                    "ledger_row_kind": "evidence",
                    "source_domain": "final_evidence_intake",
                    "producer_phase": "phase31",
                    "producer_artifact_kind": "phase31_final_intake_receipt",
                    "source_row_kind": "accepted_final_receipt",
                    "source_subject_id": str(
                        receipt.get("submission_id") or source_ref
                    ),
                    "decision_axis": "",
                    "decision_subject_id": "",
                    "phase_lifecycle_id": PHASE31_LIFECYCLE_ID,
                    "source_stream": stream,
                    "source_ref": source_ref,
                    "expected_gate": EXPECTED_GATE_BY_STREAM.get(stream, EXPECTED_GATE_BY_STREAM["unknown"]),
                    "requirement_ids": sorted({str(value) for value in receipt.get("requirement_ids", [])}),
                    "proof_eligibility": "ineligible" if problem_kind else "eligible",
                    "evidence_status": str(receipt.get("evidence_status") or ("failed" if receipt.get("failure_reason") else "passed")),
                    "row_problem_kind": problem_kind,
                    "evidence_refs": sorted({source_ref, *[str(ref) for ref in receipt.get("validator_output_refs", [])]}),
                    "artifact_refs": artifact_refs,
                    "duplicate_source_ref": source_ref in duplicate_refs,
                }
            )
    present_streams = {row["source_stream"] for row in rows}
    for stream, specification in sorted((required_streams or {}).items()):
        if stream in present_streams:
            continue
        source_ref = str(specification["expected_source_ref"])
        rows.append(
            {
                "row_id": stable_row_id(stream, source_ref),
                "ledger_row_kind": "evidence",
                "source_domain": "final_evidence_intake",
                "producer_phase": "phase31",
                "producer_artifact_kind": "phase31_required_stream",
                "source_row_kind": "missing_required_stream",
                "source_subject_id": stream,
                "decision_axis": "",
                "decision_subject_id": "",
                "phase_lifecycle_id": PHASE31_LIFECYCLE_ID,
                "source_stream": stream,
                "source_ref": source_ref,
                "expected_gate": str(specification["expected_gate"]),
                "requirement_ids": sorted({str(value) for value in specification["requirement_ids"]}),
                "proof_eligibility": "ineligible",
                "evidence_status": "missing",
                "row_problem_kind": "missing",
                "evidence_refs": [source_ref],
                "artifact_refs": [],
                "duplicate_source_ref": False,
            }
        )
    for row in rows:
        row["duplicate_source_ref"] = row["source_ref"] in duplicate_refs
    return sorted(rows, key=lambda row: (row["source_stream"], row["source_ref"], row["row_id"]))


def derive_expected_rows(
    receipts: list[dict[str, Any]],
    required_streams: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Compatibility name for the Phase 31 evidence-row constructor."""
    return derive_evidence_rows(receipts, required_streams)


def decisions_for(
    decisions: list[dict[str, Any]],
    decision_type: str,
    blocker_ref: str,
    affected_gate: str,
) -> list[dict[str, Any]]:
    matches = []
    for decision in decisions:
        if decision.get("decision_type") != decision_type:
            continue
        if blocker_ref not in decision.get("source_row_refs", []):
            continue
        if decision_type in {"exception", "residual_risk"} and affected_gate not in decision.get("affected_gates", []):
            continue
        if decision_type == "exception" and blocker_ref not in decision.get("linked_blocker_refs", []):
            continue
        matches.append(decision)
    return sorted(matches, key=lambda row: str(row.get("decision_id", "")))


def decision_refs(rows: list[dict[str, Any]]) -> list[str]:
    return [f"build/ci-evidence/phase33/normalized-decision-records.json#{row.get('decision_id')}" for row in rows]


def validate_normalized_decisions(decisions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    decisions_by_id: dict[str, dict[str, Any]] = {}
    for index, decision in enumerate(decisions):
        field_prefix = f"normalized decision rows[{index}]"
        missing_fields = [
            field
            for field in PHASE33_REQUIRED_DECISION_FIELDS
            if field not in decision
        ]
        if missing_fields:
            raise VerificationError(f"{field_prefix} missing required fields: {', '.join(missing_fields)}")
        decision_id = require_string(decision.get("decision_id"), f"{field_prefix}.decision_id")
        if decision_id in decisions_by_id:
            raise VerificationError(f"duplicate Phase 33 decision_id: {decision_id}")
        decision_type = require_string(decision.get("decision_type"), f"{decision_id}.decision_type")
        maybe_values = PHASE33_DECISION_VALUE_ENUMS.get(decision_type)
        if maybe_values is None:
            raise VerificationError(f"{decision_id} unknown decision_type: {decision_type}")
        decision_value = require_string(decision.get("decision_value"), f"{decision_id}.decision_value")
        if decision.get("phase") != "33-maintainer-decision-inputs":
            raise VerificationError(f"{decision_id}.phase must be 33-maintainer-decision-inputs")
        require_string(
            decision.get("phase_lifecycle_id"),
            f"{decision_id}.phase_lifecycle_id",
        )
        require_string(
            decision.get("decision_axis"),
            f"{decision_id}.decision_axis",
        )
        source_refs = string_list(decision.get("source_row_refs"), f"{decision_id}.source_row_refs")
        if not source_refs:
            raise VerificationError(f"{decision_id}.source_row_refs must contain at least one entry")
        raw_targets = require_list(
            decision.get("decision_targets"),
            f"{decision_id}.decision_targets",
        )
        if not raw_targets:
            raise VerificationError(
                f"{decision_id}.decision_targets must contain at least one entry"
            )
        decision_targets: list[dict[str, str]] = []
        for target_index, raw_target in enumerate(raw_targets):
            if not isinstance(raw_target, dict):
                raise VerificationError(
                    f"{decision_id}.decision_targets[{target_index}] must be an object"
                )
            target = {
                field: require_string(
                    raw_target.get(field),
                    f"{decision_id}.decision_targets[{target_index}].{field}",
                )
                for field in (
                    "row_ref",
                    "decision_axis",
                    "decision_subject_id",
                )
            }
            decision_targets.append(target)
        if source_refs != [
            target["row_ref"] for target in decision_targets
        ]:
            raise VerificationError(
                f"{decision_id}.source_row_refs must exactly project "
                "decision_targets[*].row_ref"
            )
        for field in ("maintainer_identity_ref", "maintainer_role", "owner_signoff_ref", "rationale"):
            require_string(decision.get(field), f"{decision_id}.{field}")
        require_iso_utc(
            require_string(decision.get("decision_timestamp"), f"{decision_id}.decision_timestamp"),
            f"{decision_id}.decision_timestamp",
        )
        for field in ("evidence_refs", "artifact_refs"):
            string_list(decision.get(field), f"{decision_id}.{field}")
        decisions_by_id[decision_id] = decision
    return decisions_by_id


def validate_handoff_decision(
    projection: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
    expected_type: str,
    expected_value: str,
    matching_fields: tuple[str, ...],
) -> dict[str, Any]:
    decision_id = require_string(projection.get("decision_id"), "decision_id")
    maybe_decision = decisions_by_id.get(decision_id)
    if maybe_decision is None:
        raise VerificationError(f"unknown Phase 33 decision_id: {decision_id}")
    decision = maybe_decision
    if decision.get("decision_type") != expected_type or decision.get("decision_value") != expected_value:
        raise VerificationError(f"{decision_id} does not authorize {expected_type}={expected_value}")
    if decision.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        raise VerificationError(
            f"{decision_id}.phase_lifecycle_id must be {PHASE33_LIFECYCLE_ID}"
        )
    for field in matching_fields:
        if projection.get(field) != decision.get(field):
            raise VerificationError(f"{decision_id} projection mismatch for {field}")
    require_iso_utc(str(decision["decision_timestamp"]), f"{decision_id}.decision_timestamp")
    return decision


def coverage_for_row(
    expected: dict[str, Any],
    maybe_blocker: dict[str, Any] | None,
    duplicate_classification: bool,
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    problem_kind = str(expected["row_problem_kind"])
    reason_codes: list[str] = []
    if expected["duplicate_source_ref"]:
        reason_codes.append("duplicate-row")
    if problem_kind == "missing":
        reason_codes.append("required-row-missing")
        coverage_state = "required-row-missing"
        readiness_effect = "blocked"
        affected_gates = [str(expected["expected_gate"])]
        blocker_kind = "missing_required_evidence"
        severity = "critical"
        classification_ref = ""
        retained_refs = []
        residual_refs = []
        exception_refs = []
    elif maybe_blocker is None and problem_kind:
        reason_codes.append("underclassified")
        coverage_state = "underclassified"
        readiness_effect = "blocked"
        affected_gates: list[str] = []
        blocker_kind = ""
        severity = "critical"
        classification_ref = ""
        retained_refs: list[str] = []
        residual_refs: list[str] = []
        exception_refs: list[str] = []
    elif maybe_blocker is None:
        coverage_state = "clean-no-blocker"
        readiness_effect = "unblocked"
        affected_gates = []
        blocker_kind = ""
        severity = ""
        classification_ref = ""
        retained_refs = []
        residual_refs = []
        exception_refs = []
    else:
        blocker_id = str(maybe_blocker.get("row_id") or "")
        classification_ref = f"{PHASE32_REGISTER_REF}#{blocker_id}"
        affected_gate = str(maybe_blocker.get("affected_gate") or "")
        affected_gates = [affected_gate] if affected_gate else []
        problem_kind = str(maybe_blocker.get("row_problem_kind") or problem_kind or "unknown_unclassified")
        blocker_kind = str(maybe_blocker.get("blocker_kind") or "unresolved_decision_blocker")
        severity = str(maybe_blocker.get("severity") or "critical")
        reason_codes.append(PROBLEM_REASON_CODES.get(problem_kind, "unknown-classification"))
        retained = decisions_for(decisions, "retained_code", classification_ref, affected_gate)
        residual = decisions_for(decisions, "residual_risk", classification_ref, affected_gate)
        exceptions = decisions_for(decisions, "exception", classification_ref, affected_gate)
        retained_refs = decision_refs(retained)
        residual_refs = decision_refs(residual)
        exception_refs = decision_refs(exceptions)
        covered = any(row.get("decision_value") in {"accept", "exception_approve"} for row in retained)
        covered = covered or any(row.get("decision_value") == "accept" for row in residual)
        exception_approved = any(row.get("decision_value") == "approve" for row in exceptions)
        if problem_kind in HARD_BLOCKER_PROBLEM_KINDS:
            covered = False
            exception_approved = False
        if blocker_kind == "exception_request":
            if exception_approved:
                coverage_state = "exception-covered"
                readiness_effect = "unblocked"
                reason_codes = []
            else:
                coverage_state = "exception-uncovered"
                readiness_effect = "blocked"
                reason_codes.append("exception-uncovered")
        elif covered:
            coverage_state = "decision-covered"
            readiness_effect = "unblocked"
            reason_codes = []
        else:
            coverage_state = "classified-blocker"
            readiness_effect = "blocked"
    if duplicate_classification:
        coverage_state = "duplicate-classification"
        readiness_effect = "blocked"
        reason_codes.append("duplicate-row")
    if expected["duplicate_source_ref"]:
        readiness_effect = "blocked"
    readiness_decisions = [
        row
        for row in decisions
        if row.get("decision_type") == "readiness"
        and (not classification_ref or classification_ref in row.get("source_row_refs", []))
    ]
    row = {
        "row_id": expected["row_id"],
        "ledger_row_kind": expected["ledger_row_kind"],
        "source_domain": expected["source_domain"],
        "producer_phase": expected["producer_phase"],
        "producer_artifact_kind": expected["producer_artifact_kind"],
        "source_row_kind": expected["source_row_kind"],
        "source_subject_id": expected["source_subject_id"],
        "decision_axis": expected["decision_axis"],
        "decision_subject_id": expected["decision_subject_id"],
        "phase_lifecycle_id": expected["phase_lifecycle_id"],
        "source_stream": expected["source_stream"],
        "source_ref": expected["source_ref"],
        "requirement_ids": expected["requirement_ids"],
        "affected_gates": affected_gates,
        "proof_eligibility": expected["proof_eligibility"],
        "evidence_status": expected["evidence_status"],
        "row_problem_kind": problem_kind,
        "blocker_kind": blocker_kind,
        "severity": severity,
        "evidence_refs": expected["evidence_refs"],
        "artifact_refs": expected["artifact_refs"],
        "classification_ref": classification_ref,
        "retained_code_decision_refs": retained_refs,
        "residual_risk_decision_refs": residual_refs,
        "exception_decision_refs": exception_refs,
        "readiness_decision_refs": decision_refs(readiness_decisions),
        "demotion_decision_refs": [],
        "coverage_state": coverage_state,
        "readiness_effect": readiness_effect,
        "reason_codes": sorted(set(reason_codes)),
    }
    return row


def is_decision_domain_row(row: dict[str, Any]) -> bool:
    return (
        row.get("producer_phase") in DECISION_DOMAIN_PRODUCER_PHASES
        and row.get("source_domain") in {"retained_code", "readiness"}
        and row.get("decision_axis") in set(PHASE33_DECISION_AXES.values())
        and all(
            isinstance(row.get(field), str) and row[field].strip()
            for field in (
                "row_id",
                "producer_artifact_kind",
                "source_row_kind",
                "source_subject_id",
                "decision_subject_id",
            )
        )
    )


def derive_decision_domain_rows(
    blocker_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for blocker in blocker_rows:
        if not is_decision_domain_row(blocker):
            continue
        row = dict(blocker)
        row["phase_lifecycle_id"] = str(
            blocker.get("phase_lifecycle_id") or PHASE32_LIFECYCLE_ID
        )
        rows.append(row)
    return sorted(
        rows,
        key=lambda row: (
            str(row["row_id"]),
            str(row["decision_axis"]),
            str(row["decision_subject_id"]),
        ),
    )


def canonical_decision_ref(decision: dict[str, Any]) -> str:
    return (
        "build/ci-evidence/phase33/normalized-decision-records.json#"
        f"{decision.get('decision_id')}"
    )


def decision_targets_domain_rows(
    decision: dict[str, Any],
    decision_rows: list[dict[str, Any]],
) -> bool:
    row_refs = {
        f"{PHASE32_REGISTER_REF}#{row['row_id']}"
        for row in decision_rows
    }
    axis_subjects = {
        (str(row["decision_axis"]), str(row["decision_subject_id"]))
        for row in decision_rows
    }
    raw_targets = decision.get("decision_targets")
    if not isinstance(raw_targets, list):
        return False
    for target in raw_targets:
        if not isinstance(target, dict):
            continue
        if target.get("row_ref") in row_refs:
            return True
        if (
            str(target.get("decision_axis") or ""),
            str(target.get("decision_subject_id") or ""),
        ) in axis_subjects:
            return True
    return False


def decision_domain_ledger_row(
    canonical_row: dict[str, Any],
    reconciliation: dict[str, Any],
) -> dict[str, Any]:
    decision_refs_by_axis = {
        "retained_code": [],
        "residual_risk": [],
        "exception": [],
        "readiness": [],
        "demotion": [],
    }
    decision_refs_by_axis[str(canonical_row["decision_axis"])] = list(
        reconciliation["linked_decision_refs"]
    )
    affected_gate = str(canonical_row.get("affected_gate") or "")
    return {
        "row_id": str(canonical_row["row_id"]),
        "ledger_row_kind": "decision-domain",
        "source_domain": str(canonical_row["source_domain"]),
        "producer_phase": str(canonical_row["producer_phase"]),
        "producer_artifact_kind": str(
            canonical_row["producer_artifact_kind"]
        ),
        "source_row_kind": str(canonical_row["source_row_kind"]),
        "source_subject_id": str(canonical_row["source_subject_id"]),
        "decision_axis": str(canonical_row["decision_axis"]),
        "decision_subject_id": str(canonical_row["decision_subject_id"]),
        "phase_lifecycle_id": str(canonical_row["phase_lifecycle_id"]),
        "source_stream": str(canonical_row.get("source_stream") or "unknown"),
        "source_ref": str(canonical_row.get("source_ref") or ""),
        "requirement_ids": sorted({
            str(value)
            for value in canonical_row.get("requirement_ids", [])
        }),
        "affected_gates": [affected_gate] if affected_gate else [],
        "proof_eligibility": str(
            canonical_row.get("proof_eligibility") or "ineligible"
        ),
        "evidence_status": "decision-domain",
        "row_problem_kind": str(
            canonical_row.get("row_problem_kind") or "unknown_unclassified"
        ),
        "blocker_kind": str(
            canonical_row.get("blocker_kind")
            or "unresolved_decision_blocker"
        ),
        "severity": str(canonical_row.get("severity") or "critical"),
        "evidence_refs": sorted({
            str(ref)
            for ref in canonical_row.get("evidence_refs", [])
            if isinstance(ref, str)
        }),
        "artifact_refs": sorted({
            str(ref)
            for ref in canonical_row.get("artifact_refs", [])
            if isinstance(ref, str)
        }),
        "classification_ref": (
            f"{PHASE32_REGISTER_REF}#{canonical_row['row_id']}"
        ),
        "retained_code_decision_refs": decision_refs_by_axis[
            "retained_code"
        ],
        "residual_risk_decision_refs": decision_refs_by_axis[
            "residual_risk"
        ],
        "exception_decision_refs": decision_refs_by_axis["exception"],
        "readiness_decision_refs": decision_refs_by_axis["readiness"],
        "demotion_decision_refs": decision_refs_by_axis["demotion"],
        "coverage_state": reconciliation["coverage_state"],
        "readiness_effect": reconciliation["readiness_effect"],
        "reason_codes": list(reconciliation["reason_codes"]),
    }


def decision_diagnostic_row(
    diagnostic: dict[str, str],
    index: int,
    decisions_by_ref: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    decision_ref = str(
        diagnostic.get("decision_ref") or f"decision-diagnostic-{index}"
    )
    maybe_decision = decisions_by_ref.get(decision_ref)
    decision_axis = (
        str(maybe_decision.get("decision_axis") or "")
        if maybe_decision is not None
        else ""
    )
    readiness_effect = (
        "independent" if decision_axis == "demotion" else "blocked"
    )
    return {
        "row_id": stable_row_id(
            "decision-diagnostic",
            f"{decision_ref}\0{diagnostic.get('reason_code')}\0{index}",
        ),
        "ledger_row_kind": "decision-domain",
        "source_domain": "phase33_decision",
        "producer_phase": "phase33",
        "producer_artifact_kind": "normalized_decision_records",
        "source_row_kind": "decision_diagnostic",
        "source_subject_id": decision_ref,
        "decision_axis": decision_axis,
        "decision_subject_id": "",
        "phase_lifecycle_id": PHASE33_LIFECYCLE_ID,
        "source_stream": "phase33-decision",
        "source_ref": decision_ref,
        "requirement_ids": REQUIRED_REQUIREMENT_IDS,
        "affected_gates": [],
        "proof_eligibility": "ineligible",
        "evidence_status": "invalid",
        "row_problem_kind": "unknown_unclassified",
        "blocker_kind": "unresolved_decision_blocker",
        "severity": "critical",
        "evidence_refs": [],
        "artifact_refs": [],
        "classification_ref": "",
        "retained_code_decision_refs": (
            [decision_ref] if decision_axis == "retained_code" else []
        ),
        "residual_risk_decision_refs": (
            [decision_ref] if decision_axis == "residual_risk" else []
        ),
        "exception_decision_refs": (
            [decision_ref] if decision_axis == "exception" else []
        ),
        "readiness_decision_refs": (
            [decision_ref] if decision_axis == "readiness" else []
        ),
        "demotion_decision_refs": (
            [decision_ref] if decision_axis == "demotion" else []
        ),
        "coverage_state": "blocked",
        "readiness_effect": readiness_effect,
        "reason_codes": [str(diagnostic["reason_code"])],
    }


def evaluate_coverage(
    receipts: list[dict[str, Any]],
    blocker_rows: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    required_streams: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    expected_rows = derive_evidence_rows(receipts, required_streams)
    decision_domain_rows = derive_decision_domain_rows(blocker_rows)
    blocker_id_counts: dict[str, int] = {}
    blockers_by_join_key: dict[tuple[str, str], list[tuple[int, dict[str, Any]]]] = {}
    blockers_by_id: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, blocker in enumerate(blocker_rows):
        if is_decision_domain_row(blocker):
            continue
        blocker_id = str(blocker.get("row_id") or "")
        blocker_id_counts[blocker_id] = blocker_id_counts.get(blocker_id, 0) + 1
        join_key = (
            str(blocker.get("source_ref") or ""),
            str(blocker.get("affected_gate") or ""),
        )
        blockers_by_join_key.setdefault(join_key, []).append((index, blocker))
        blockers_by_id.setdefault(blocker_id, []).append((index, blocker))

    ledger: list[dict[str, Any]] = []
    matched_blocker_indices: set[int] = set()
    for expected in expected_rows:
        join_key = (str(expected["source_ref"]), str(expected["expected_gate"]))
        matches = [
            (index, blocker)
            for index, blocker in blockers_by_join_key.get(join_key, [])
            if blocker.get("source_stream") == expected["source_stream"]
        ]
        matches.sort(key=lambda item: (str(item[1].get("row_id") or ""), json.dumps(item[1], sort_keys=True)))
        matched_blocker_indices.update(index for index, _ in matches)
        maybe_blocker = matches[0][1] if matches else None
        duplicate_classification = len(matches) > 1
        if maybe_blocker is not None:
            blocker_id = str(maybe_blocker.get("row_id") or "")
            duplicate_classification = duplicate_classification or blocker_id_counts.get(blocker_id, 0) > 1
        ledger.append(coverage_for_row(expected, maybe_blocker, duplicate_classification, decisions))

    domain_decisions = [
        {
            **decision,
            "decision_ref": canonical_decision_ref(decision),
        }
        for decision in decisions
        if decision_targets_domain_rows(decision, decision_domain_rows)
    ]
    handled_decision_ids = {
        str(decision.get("decision_id") or "")
        for decision in domain_decisions
    }
    if decision_domain_rows:
        reconciliation = reconcile_decision_rows(
            decision_domain_rows,
            domain_decisions,
            expected_phase32_lifecycle_id=PHASE32_LIFECYCLE_ID,
            expected_phase33_lifecycle_id=PHASE33_LIFECYCLE_ID,
        )
        results_by_identity = {
            (
                str(result["row_id"]),
                str(result["decision_axis"]),
                str(result["decision_subject_id"]),
            ): result
            for result in reconciliation["rows"]
        }
        decisions_by_ref = {
            str(decision["decision_ref"]): decision
            for decision in domain_decisions
        }
        blocking_diagnostics = [
            diagnostic
            for diagnostic in reconciliation["diagnostics"]
            if (
                decisions_by_ref.get(
                    str(diagnostic.get("decision_ref") or ""),
                    {},
                ).get("decision_axis")
                != "demotion"
            )
        ]
        prerequisites_blocked = (
            any(row["readiness_effect"] == "blocked" for row in ledger)
            or any(
                result["readiness_effect"] == "blocked"
                and result["decision_axis"] != "readiness"
                for result in reconciliation["rows"]
            )
            or bool(blocking_diagnostics)
        )
        if prerequisites_blocked:
            for result in results_by_identity.values():
                if (
                    result["decision_axis"] == "readiness"
                    and result["readiness_effect"] == "unblocked"
                ):
                    result["coverage_state"] = "blocked"
                    result["readiness_effect"] = "blocked"
                    result["reason_codes"] = [
                        "decision-readiness-prerequisites-blocked"
                    ]
        for canonical_row in decision_domain_rows:
            identity = (
                str(canonical_row["row_id"]),
                str(canonical_row["decision_axis"]),
                str(canonical_row["decision_subject_id"]),
            )
            maybe_result = results_by_identity.get(identity)
            if maybe_result is None:
                continue
            ledger.append(
                decision_domain_ledger_row(canonical_row, maybe_result)
            )
        for diagnostic_index, diagnostic in enumerate(
            reconciliation["diagnostics"]
        ):
            ledger.append(
                decision_diagnostic_row(
                    diagnostic,
                    diagnostic_index,
                    decisions_by_ref,
                )
            )

    duplicate_blocker_ids = {
        blocker_id
        for blocker_id, count in blocker_id_counts.items()
        if count > 1
    }
    for index, blocker in enumerate(blocker_rows):
        if index in matched_blocker_indices or is_decision_domain_row(blocker):
            continue
        reasons = ["dangling-row-ref"]
        if str(blocker.get("row_id") or "") in duplicate_blocker_ids:
            reasons.append("duplicate-row")
        ledger.append(dangling_blocker_row(blocker, index, reasons))

    decision_id_counts: dict[str, int] = {}
    for decision in decisions:
        decision_id = str(decision.get("decision_id") or "")
        decision_id_counts[decision_id] = decision_id_counts.get(decision_id, 0) + 1
    for index, decision in enumerate(decisions):
        if str(decision.get("decision_id") or "") in handled_decision_ids:
            continue
        reasons = dangling_decision_reasons(
            decision,
            blockers_by_id,
            matched_blocker_indices,
        )
        if decision_id_counts.get(str(decision.get("decision_id") or ""), 0) > 1:
            reasons.append("duplicate-row")
        if reasons:
            ledger.append(dangling_decision_row(decision, index, sorted(set(reasons))))
    return ledger


def dangling_blocker_row(
    blocker: dict[str, Any],
    index: int,
    reason_codes: list[str],
) -> dict[str, Any]:
    blocker_id = str(blocker.get("row_id") or f"row-{index}")
    affected_gate = str(blocker.get("affected_gate") or "")
    source_ref = str(blocker.get("source_ref") or "")
    return {
        "row_id": stable_row_id("dangling-phase32", f"{blocker_id}\0{index}\0{source_ref}\0{affected_gate}"),
        "ledger_row_kind": "decision-domain",
        "source_domain": str(blocker.get("source_domain") or "unknown"),
        "producer_phase": str(blocker.get("producer_phase") or "phase32"),
        "producer_artifact_kind": str(
            blocker.get("producer_artifact_kind")
            or "unmatched_blocker_register_row"
        ),
        "source_row_kind": str(
            blocker.get("source_row_kind") or "unmatched_blocker"
        ),
        "source_subject_id": str(
            blocker.get("source_subject_id") or blocker_id
        ),
        "decision_axis": str(blocker.get("decision_axis") or ""),
        "decision_subject_id": str(
            blocker.get("decision_subject_id") or ""
        ),
        "phase_lifecycle_id": str(
            blocker.get("phase_lifecycle_id") or PHASE32_LIFECYCLE_ID
        ),
        "source_stream": str(blocker.get("source_stream") or "unknown"),
        "source_ref": source_ref,
        "requirement_ids": sorted({str(value) for value in blocker.get("requirement_ids", [])}),
        "affected_gates": [affected_gate] if affected_gate else [],
        "proof_eligibility": str(blocker.get("proof_eligibility") or "ineligible"),
        "evidence_status": "unmatched",
        "row_problem_kind": str(blocker.get("row_problem_kind") or "unknown_unclassified"),
        "blocker_kind": str(blocker.get("blocker_kind") or "unresolved_decision_blocker"),
        "severity": str(blocker.get("severity") or "critical"),
        "evidence_refs": sorted({str(ref) for ref in blocker.get("evidence_refs", []) if isinstance(ref, str)}),
        "artifact_refs": [],
        "classification_ref": f"{PHASE32_REGISTER_REF}#{blocker_id}",
        "retained_code_decision_refs": [],
        "residual_risk_decision_refs": [],
        "exception_decision_refs": [],
        "readiness_decision_refs": [],
        "demotion_decision_refs": [],
        "coverage_state": "dangling-blocker",
        "readiness_effect": "blocked",
        "reason_codes": sorted(set(reason_codes)),
    }


def dangling_decision_reasons(
    decision: dict[str, Any],
    blockers_by_id: dict[str, list[tuple[int, dict[str, Any]]]],
    matched_blocker_indices: set[int],
) -> list[str]:
    source_refs = decision.get("source_row_refs")
    if not isinstance(source_refs, list) or not source_refs:
        return ["dangling-row-ref"]
    affected_gates = {
        str(value)
        for value in decision.get("affected_gates", [])
        if isinstance(value, str)
    }
    prefix = f"{PHASE32_REGISTER_REF}#"
    reasons: list[str] = []
    for source_ref in source_refs:
        if not isinstance(source_ref, str) or not source_ref.startswith(prefix):
            reasons.append("dangling-row-ref")
            continue
        blocker_id = source_ref[len(prefix):]
        matches = blockers_by_id.get(blocker_id, [])
        if len(matches) != 1:
            reasons.append("dangling-row-ref")
            if len(matches) > 1:
                reasons.append("duplicate-row")
            continue
        blocker_index, blocker = matches[0]
        if blocker_index not in matched_blocker_indices:
            reasons.append("dangling-row-ref")
        affected_gate = str(blocker.get("affected_gate") or "")
        if not affected_gate or affected_gate not in affected_gates:
            reasons.append("dangling-row-ref")
    return reasons


def dangling_decision_row(
    decision: dict[str, Any],
    index: int,
    reason_codes: list[str],
) -> dict[str, Any]:
    decision_id = str(decision.get("decision_id") or f"decision-{index}")
    decision_ref = f"build/ci-evidence/phase33/normalized-decision-records.json#{decision_id}"
    source_refs = [
        str(ref)
        for ref in decision.get("source_row_refs", [])
        if isinstance(ref, str)
    ]
    affected_gates = sorted({
        str(value)
        for value in decision.get("affected_gates", [])
        if isinstance(value, str) and value
    })
    return {
        "row_id": stable_row_id("dangling-phase33", f"{decision_id}\0{index}"),
        "ledger_row_kind": "decision-domain",
        "source_domain": "phase33_decision",
        "producer_phase": "phase33",
        "producer_artifact_kind": "normalized_decision_records",
        "source_row_kind": "unmatched_decision",
        "source_subject_id": decision_id,
        "decision_axis": str(decision.get("decision_axis") or ""),
        "decision_subject_id": "",
        "phase_lifecycle_id": str(
            decision.get("phase_lifecycle_id") or PHASE33_LIFECYCLE_ID
        ),
        "source_stream": "phase33-decision",
        "source_ref": decision_ref,
        "requirement_ids": REQUIRED_REQUIREMENT_IDS,
        "affected_gates": affected_gates,
        "proof_eligibility": "ineligible",
        "evidence_status": "unmatched",
        "row_problem_kind": "unknown_unclassified",
        "blocker_kind": "unresolved_decision_blocker",
        "severity": "critical",
        "evidence_refs": sorted(set(source_refs)),
        "artifact_refs": sorted({
            str(ref)
            for ref in decision.get("artifact_refs", [])
            if isinstance(ref, str)
        }),
        "classification_ref": "",
        "retained_code_decision_refs": [],
        "residual_risk_decision_refs": [],
        "exception_decision_refs": [],
        "readiness_decision_refs": [decision_ref] if decision.get("decision_type") == "readiness" else [],
        "demotion_decision_refs": [decision_ref] if decision.get("decision_axis") == "demotion" else [],
        "coverage_state": "dangling-decision",
        "readiness_effect": (
            "independent"
            if decision.get("decision_axis") == "demotion"
            else "blocked"
        ),
        "reason_codes": reason_codes,
    }


def evaluate_demotion(
    readiness_state: str,
    approval_validation_state: str,
    approval_decision_state: str,
    source_refs: list[str],
) -> dict[str, Any]:
    reason_codes = []
    if readiness_state != "unblocked":
        reason_codes.append("readiness-input-invalid")
    if approval_validation_state == "missing":
        reason_codes.append("approval-missing")
    elif approval_validation_state != "valid":
        reason_codes.append("approval-invalid")
    if approval_decision_state == "missing" and "approval-missing" not in reason_codes:
        reason_codes.append("approval-missing")
    elif approval_decision_state == "reject":
        reason_codes.append("approval-rejected")
    gate_state = "open"
    if (readiness_state, approval_validation_state, approval_decision_state) != ("unblocked", "valid", "approve"):
        gate_state = "blocked"
    return {
        "readiness_state": readiness_state,
        "approval_validation_state": approval_validation_state,
        "approval_decision_state": approval_decision_state,
        "gate_state": gate_state,
        "reason_codes": sorted(set(reason_codes)),
        "source_refs": sorted(set(source_refs)),
    }


def load_phase31(root: Path, output_arg: str | Path) -> tuple[Path, dict[str, Any], list[dict[str, Any]], list[str]]:
    output_dir = path_under(output_arg, DEFAULT_PHASE31_OUTPUT_DIR, "--phase31-output-dir")
    resolved_under(root, output_dir, DEFAULT_PHASE31_OUTPUT_DIR, "--phase31-output-dir")
    manifest_path = output_dir / "final-intake-manifest.json"
    manifest = load_json(root, manifest_path)
    scan_json(manifest, manifest_path)
    if manifest.get("artifact_name") != "phase31-final-evidence-intake":
        raise VerificationError("Phase 31 manifest artifact_name must be phase31-final-evidence-intake")
    if manifest.get("phase_lifecycle_id") != PHASE31_LIFECYCLE_ID:
        raise VerificationError(f"Phase 31 manifest phase_lifecycle_id must be {PHASE31_LIFECYCLE_ID}")
    if manifest.get("output_root") != output_dir.as_posix():
        raise VerificationError("Phase 31 manifest output_root must match --phase31-output-dir")
    receipt_refs = string_list(manifest.get("receipt_refs"), "Phase 31 receipt_refs")
    receipts: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]] = []
    for receipt_ref in sorted(receipt_refs):
        receipt_path = path_under(receipt_ref, output_dir, "Phase 31 receipt_ref")
        resolved_under(root, receipt_path, output_dir, "Phase 31 receipt_ref")
        receipt = load_json(root, receipt_path)
        scan_json(receipt, receipt_path)
        if receipt.get("finality_status") != "accepted-final":
            raise VerificationError(f"{receipt_path.as_posix()} must have finality_status accepted-final")
        receipts.append(receipt)
        snapshot_rows.append({"receipt_ref": receipt_path.as_posix(), "receipt": receipt})
    return manifest_path, manifest, receipts, [json.dumps(row, sort_keys=True) for row in snapshot_rows]


def phase33_register_path(root: Path, register_refs: dict[str, Any], name: str) -> Path:
    value = register_refs.get(name)
    if not isinstance(value, str):
        raise VerificationError(f"Phase 33 register_refs.{name} must be a path")
    register_path = path_under(value, PHASE33_OUTPUT_ROOT, f"register_refs.{name}")
    resolved_under(root, register_path, PHASE33_OUTPUT_ROOT, f"register_refs.{name}")
    return register_path


def load_phase33_register(root: Path, register_refs: dict[str, Any], name: str) -> dict[str, Any]:
    register_path = phase33_register_path(root, register_refs, name)
    payload = load_json(root, register_path)
    scan_json(payload, register_path)
    return payload


def phase33_register_digests(root: Path, register_refs: dict[str, Any]) -> dict[str, str]:
    return {
        name: hashlib.sha256(
            json.dumps(
                load_phase33_register(root, register_refs, name),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        for name in sorted(register_refs)
    }


def load_phase33_handoff(
    root: Path,
    handoff_arg: str | Path,
    full_output: Path,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    raw_path = repo_relative_path(handoff_arg, "--phase33-handoff")
    resolved_input = (root / raw_path).resolve(strict=False)
    if resolved_input == full_output or full_output in resolved_input.parents:
        raise VerificationError(
            "--phase33-handoff must be outside the generated --output-dir"
        )
    handoff_path = path_under(
        raw_path,
        PHASE33_OUTPUT_ROOT,
        "--phase33-handoff",
    )
    resolved_under(
        root,
        handoff_path,
        PHASE33_OUTPUT_ROOT,
        "--phase33-handoff",
    )
    handoff = load_json(root, handoff_path)
    scan_json(handoff, handoff_path)
    if handoff.get("artifact_name") != "phase33-maintainer-decision-inputs":
        raise VerificationError(
            "Phase 33 handoff artifact_name must be phase33-maintainer-decision-inputs"
        )
    if handoff.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        raise VerificationError(
            f"Phase 33 handoff phase_lifecycle_id must be {PHASE33_LIFECYCLE_ID}"
        )
    if handoff.get("raw_evidence_consumed") not in {None, False}:
        raise VerificationError(
            "Phase 33 handoff raw_evidence_consumed must be false"
        )
    source_inputs = handoff.get("source_inputs")
    if (
        not isinstance(source_inputs, dict)
        or source_inputs.get("phase32_canonical_register_ref")
        != PHASE32_REGISTER_REF
    ):
        raise VerificationError(
            f"Phase 33 handoff must reference {PHASE32_REGISTER_REF}"
        )
    register_refs = handoff.get("register_refs")
    if not isinstance(register_refs, dict):
        raise VerificationError("Phase 33 handoff register_refs must be an object")
    return handoff_path, handoff, register_refs


def load_phase32_blocker_register(root: Path) -> dict[str, Any]:
    blocker_register_path = Path(PHASE32_REGISTER_REF)
    resolved_under(
        root,
        blocker_register_path,
        Path("build/ci-evidence/phase32"),
        "Phase 32 blocker register",
    )
    blocker_register = load_json(root, blocker_register_path)
    scan_json(blocker_register, blocker_register_path)
    if blocker_register.get("phase_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError(
            f"Phase 32 blocker register phase_lifecycle_id must be {PHASE32_LIFECYCLE_ID}"
        )
    return blocker_register


def validate_readiness_handoff(
    readiness: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
) -> None:
    if readiness.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        raise VerificationError(
            "Phase 33 readiness handoff lifecycle is stale or malformed"
        )
    handoff_state = readiness.get("handoff_state")
    if handoff_state == "blocked-pending-maintainer-input":
        if readiness.get("readiness_input_supplied") is not False:
            raise VerificationError(
                "blocked Phase 33 readiness handoff must not claim supplied input"
            )
        return
    if handoff_state != "approval-input-recorded":
        raise VerificationError("Phase 33 readiness handoff state is invalid")
    validate_handoff_decision(
        readiness,
        decisions_by_id,
        "readiness",
        "approve",
        ("source_row_refs", "rationale"),
    )


def validate_demotion_handoff(
    demotion: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
) -> tuple[str, str, list[str]]:
    validation, decision, source_refs, maybe_error = approval_state(
        demotion,
        decisions_by_id,
    )
    if maybe_error is not None:
        raise VerificationError(maybe_error)
    return validation, decision, source_refs


def approval_state(
    maybe_demotion: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
) -> tuple[str, str, list[str], str | None]:
    if maybe_demotion.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        return "invalid", "missing", [], "Phase 33 demotion approval lifecycle is stale or malformed"
    authorization_state = maybe_demotion.get("authorization_state")
    if authorization_state == "blocked" and maybe_demotion.get("demotion_input_supplied") is False:
        return "missing", "missing", [], None
    source_refs = [str(ref) for ref in maybe_demotion.get("source_row_refs", []) if isinstance(ref, str)]
    if authorization_state == "rejected":
        try:
            validate_handoff_decision(
                maybe_demotion,
                decisions_by_id,
                "reference_demotion",
                "reject",
                ("source_row_refs", "rationale"),
            )
        except VerificationError as error:
            return "invalid", "reject", source_refs, str(error)
        return "valid", "reject", source_refs, None
    if authorization_state != "approved-input-recorded":
        return "invalid", "missing", source_refs, "Phase 33 demotion approval state is invalid"
    try:
        validate_handoff_decision(
            maybe_demotion,
            decisions_by_id,
            "reference_demotion",
            "approve",
            (
                "source_row_refs",
                "maintainer_identity_ref",
                "maintainer_role",
                "decision_timestamp",
                "rationale",
            ),
        )
    except VerificationError as error:
        return "invalid", "missing", source_refs, str(error)
    return "valid", "approve", source_refs, None


def readiness_state(
    ledger: list[dict[str, Any]],
    readiness: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
) -> tuple[str, list[str], str | None]:
    reason_codes = sorted({
        reason
        for row in ledger
        if row["readiness_effect"] == "blocked"
        for reason in row["reason_codes"]
    })
    maybe_error = None
    if not ledger:
        reason_codes.append("required-row-missing")
    if readiness.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        reason_codes.append("readiness-input-invalid")
    elif readiness.get("handoff_state") == "approval-input-recorded":
        try:
            validate_handoff_decision(
                readiness,
                decisions_by_id,
                "readiness",
                "approve",
                ("source_row_refs", "rationale"),
            )
        except VerificationError as error:
            reason_codes.append("readiness-input-invalid")
            maybe_error = str(error)
    else:
        reason_codes.append("readiness-input-invalid")
    if any(row["readiness_effect"] == "blocked" for row in ledger):
        return "blocked", sorted(set(reason_codes)), maybe_error
    if reason_codes:
        return "blocked", sorted(set(reason_codes)), maybe_error
    return "unblocked", [], maybe_error


def reset_output_root(full_output: Path) -> None:
    if full_output.exists():
        if full_output.is_symlink() or not full_output.is_dir():
            raise VerificationError(f"--output-dir contains a symlink escape or is not a normal directory: {full_output}")
        shutil.rmtree(full_output)
    full_output.mkdir(parents=True, exist_ok=True)


def source_failure_ledger_row(reason_code: str) -> dict[str, Any]:
    return {
        "row_id": f"phase34-source-failure-{reason_code}",
        "ledger_row_kind": "evidence",
        "source_domain": "source-validation",
        "producer_phase": "phase34",
        "producer_artifact_kind": "blocked-source-failure",
        "source_row_kind": "safe-source-failure",
        "source_subject_id": reason_code,
        "decision_axis": "",
        "decision_subject_id": "",
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "source_stream": "source-validation",
        "source_ref": f"external://phase34/source-failure/{reason_code}",
        "requirement_ids": REQUIRED_REQUIREMENT_IDS,
        "affected_gates": [
            "final-readiness",
            "cutover-decision",
            "production-cutover-route",
            "final-reference-demotion-allowed",
        ],
        "proof_eligibility": "ineligible",
        "evidence_status": "invalid",
        "row_problem_kind": "source_validation_failed",
        "blocker_kind": "source_failure",
        "severity": "critical",
        "evidence_refs": [],
        "artifact_refs": [],
        "classification_ref": "",
        "retained_code_decision_refs": [],
        "residual_risk_decision_refs": [],
        "exception_decision_refs": [],
        "readiness_decision_refs": [],
        "demotion_decision_refs": [],
        "coverage_state": "blocked-source-failure",
        "readiness_effect": "blocked",
        "reason_codes": [reason_code],
    }


def write_safe_source_failure_snapshots(
    root: Path,
    output_dir: Path,
    reason_code: str,
) -> list[str]:
    snapshot_dir = output_dir / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        root / CONTRACT_MANIFEST,
        snapshot_dir / CONTRACT_MANIFEST.name,
    )
    shutil.copy2(
        root / PHASE33_CONTRACT,
        snapshot_dir / PHASE33_CONTRACT.name,
    )
    safe_snapshot = {
        "snapshot_state": "unavailable-source-failure",
        "source_failure_reason_code": reason_code,
        "raw_evidence_consumed": False,
    }
    write_json(
        snapshot_dir / "phase33-downstream-handoff-manifest.json",
        safe_snapshot,
    )
    write_json(
        snapshot_dir / "phase32-blocker-register.json",
        {**safe_snapshot, "rows": []},
    )
    write_json(
        snapshot_dir / "phase31-final-intake-manifest.json",
        safe_snapshot,
    )
    write_json(
        snapshot_dir / "phase31-accepted-receipts.json",
        {**safe_snapshot, "receipts": []},
    )
    return [
        artifact
        for artifact in GENERATED_ARTIFACTS
        if artifact.startswith("contract-snapshots/")
    ]


def write_source_failure_bundle(
    root: Path,
    relative_output: Path,
    staging_output: Path,
    reason_code: str,
    approval_validation_state: str,
) -> None:
    reset_output_root(staging_output)
    snapshot_refs = write_safe_source_failure_snapshots(
        root,
        staging_output,
        reason_code,
    )
    ledger_rows = [source_failure_ledger_row(reason_code)]
    demotion = evaluate_demotion(
        "blocked",
        approval_validation_state,
        "missing",
        [],
    )
    demotion["source_failure_reason_code"] = reason_code
    packet = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_ids": REQUIRED_REQUIREMENT_IDS,
        "readiness_state": "blocked",
        "cutover_verdict_state": "blocked",
        "production_cutover_route_state": "blocked",
        "reason_codes": [reason_code],
        "ledger_rows": ledger_rows,
        "demotion_dry_run": demotion,
        "raw_evidence_consumed": False,
    }
    blocker_summary = {
        "readiness_state": "blocked",
        "reason_codes": [reason_code],
        "blocker_count": 1,
        "blockers": ledger_rows,
    }
    run_manifest = {
        "artifact_name": "phase34-final-readiness-demotion-dry-run",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generated_at_utc": utc_now(),
        "output_root": relative_output.as_posix(),
        "run_state": "blocked-source-failure",
        "source_failure_reason_code": reason_code,
        "readiness_state": "blocked",
        "cutover_verdict_state": "blocked",
        "production_cutover_route_state": "blocked",
        "demotion_gate_state": "blocked",
        "generated_artifacts": GENERATED_ARTIFACTS,
        "snapshot_refs": [
            (relative_output / artifact).as_posix()
            for artifact in snapshot_refs
        ],
        "source_refs": [],
        "phase33_register_digests": {},
        "raw_evidence_consumed": False,
    }
    ledger = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "canonical": True,
        "rows": ledger_rows,
    }
    write_json(
        staging_output / "final-readiness-run-manifest.json",
        run_manifest,
    )
    write_json(
        staging_output / "readiness-coverage-ledger.json",
        ledger,
    )
    write_json(
        staging_output / "final-readiness-packet.json",
        packet,
    )
    write_json(
        staging_output / "readiness-blocker-summary.json",
        blocker_summary,
    )
    write_json(staging_output / "demotion-dry-run.json", demotion)
    (staging_output / "redacted-readiness-report.md").write_text(
        report_text(packet, ledger_rows),
        encoding="utf-8",
    )
    validate_generated_outputs(staging_output)
    validate_output_security(
        staging_output,
        relative_output.as_posix(),
    )


def replace_output_with_staging(
    full_output: Path,
    staging_output: Path,
) -> None:
    backup_output = full_output.with_name(
        f".{full_output.name}.source-failure-backup"
    )
    if backup_output.exists():
        if backup_output.is_symlink() or not backup_output.is_dir():
            raise VerificationError(
                "Phase 34 source-failure backup is not a normal directory"
            )
        shutil.rmtree(backup_output)
    moved_prior = False
    if full_output.exists():
        if full_output.is_symlink() or not full_output.is_dir():
            raise VerificationError(
                "Phase 34 canonical output is not a normal directory"
            )
        full_output.rename(backup_output)
        moved_prior = True
    try:
        staging_output.rename(full_output)
    except OSError as error:
        if moved_prior and backup_output.is_dir() and not full_output.exists():
            backup_output.rename(full_output)
        raise VerificationError(
            "Phase 34 blocked source-failure bundle installation failed"
        ) from error
    if moved_prior and backup_output.exists():
        shutil.rmtree(backup_output)


def publish_source_failure_bundle(
    root: Path,
    relative_output: Path,
    full_output: Path,
    reason_code: str,
    approval_validation_state: str = "invalid",
) -> None:
    staging_output = full_output.with_name(
        f".{full_output.name}.source-failure-staging"
    )
    write_source_failure_bundle(
        root,
        relative_output,
        staging_output,
        reason_code,
        approval_validation_state,
    )
    replace_output_with_staging(full_output, staging_output)
    validate_generated_outputs(full_output)
    validate_output_security(full_output, relative_output.as_posix())


def copy_snapshots(
    root: Path,
    output_dir: Path,
    phase31_manifest_path: Path,
    phase31_manifest: dict[str, Any],
    accepted_receipt_rows: list[str],
    phase33_handoff_path: Path,
    phase33_handoff: dict[str, Any],
    phase32_register: dict[str, Any],
) -> list[str]:
    snapshot_dir = output_dir / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / CONTRACT_MANIFEST, snapshot_dir / CONTRACT_MANIFEST.name)
    shutil.copy2(root / PHASE33_CONTRACT, snapshot_dir / PHASE33_CONTRACT.name)
    write_json(snapshot_dir / "phase33-downstream-handoff-manifest.json", phase33_handoff)
    write_json(snapshot_dir / "phase32-blocker-register.json", phase32_register)
    write_json(snapshot_dir / "phase31-final-intake-manifest.json", phase31_manifest)
    accepted = [json.loads(value) for value in sorted(accepted_receipt_rows)]
    write_json(snapshot_dir / "phase31-accepted-receipts.json", {"receipts": accepted})
    if phase31_manifest_path.name != "final-intake-manifest.json" or phase33_handoff_path.name != "downstream-handoff-manifest.json":
        raise VerificationError("source manifest filenames are not canonical")
    relative_output = output_dir.relative_to(root)
    return [
        (relative_output / artifact).as_posix()
        for artifact in GENERATED_ARTIFACTS
        if artifact.startswith("contract-snapshots/")
    ]


def report_text(packet: dict[str, Any], ledger: list[dict[str, Any]]) -> str:
    lines = [
        "# Phase 34 Final Readiness and Demotion Dry Run",
        "",
        "Machine-readable JSON is authoritative. This redacted report is derived from the canonical coverage ledger.",
        "",
        f"readiness_state: {packet['readiness_state']}",
        f"gate_state: {packet['demotion_dry_run']['gate_state']}",
        f"reason_codes: {', '.join(packet['reason_codes']) or 'none'}",
        "",
        "| Row | Kind | Producer | Source kind | Decision axis | Decision subject | Stream | Coverage | Readiness | Reasons |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in ledger:
        values = [
            row["row_id"],
            row["ledger_row_kind"],
            row["producer_phase"],
            row["source_row_kind"],
            row["decision_axis"] or "none",
            row["decision_subject_id"] or "none",
            row["source_stream"],
            row["coverage_state"],
            row["readiness_effect"],
            ", ".join(row["reason_codes"]) or "none",
        ]
        lines.append("| " + " | ".join(html.escape(str(value), quote=False).replace("|", r"\|") for value in values) + " |")
    return "\n".join(lines) + "\n"


def write_bundle(
    root: Path,
    relative_output: Path,
    full_output: Path,
    manifest_path: Path,
    manifest: dict[str, Any],
    accepted_receipt_rows: list[str],
    handoff_path: Path,
    handoff: dict[str, Any],
    blocker_register: dict[str, Any],
    ledger: list[dict[str, Any]],
    readiness: str,
    readiness_reasons: list[str],
    demotion: dict[str, Any],
    register_digests: dict[str, str],
) -> None:
    reset_output_root(full_output)
    snapshot_refs = copy_snapshots(
        root,
        full_output,
        manifest_path,
        manifest,
        accepted_receipt_rows,
        handoff_path,
        handoff,
        blocker_register,
    )
    reason_codes = sorted(set(readiness_reasons) | set(demotion["reason_codes"]))
    ledger_payload = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "canonical": True,
        "rows": ledger,
    }
    packet = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_ids": REQUIRED_REQUIREMENT_IDS,
        "readiness_state": readiness,
        "reason_codes": reason_codes,
        "ledger_rows": ledger,
        "demotion_dry_run": demotion,
        "raw_evidence_consumed": False,
    }
    blockers = [row for row in ledger if row["readiness_effect"] == "blocked"]
    blocker_summary = {
        "readiness_state": readiness,
        "reason_codes": reason_codes,
        "blocker_count": len(blockers),
        "blockers": blockers,
    }
    run_manifest = {
        "artifact_name": "phase34-final-readiness-demotion-dry-run",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generated_at_utc": utc_now(),
        "output_root": relative_output.as_posix(),
        "generated_artifacts": GENERATED_ARTIFACTS,
        "snapshot_refs": snapshot_refs,
        "source_refs": [manifest_path.as_posix(), handoff_path.as_posix()],
        "accepted_receipt_snapshot_ref": (relative_output / "contract-snapshots/phase31-accepted-receipts.json").as_posix(),
        "phase33_register_digests": register_digests,
        "raw_evidence_consumed": False,
    }
    write_json(full_output / "final-readiness-run-manifest.json", run_manifest)
    write_json(full_output / "readiness-coverage-ledger.json", ledger_payload)
    write_json(full_output / "final-readiness-packet.json", packet)
    write_json(full_output / "readiness-blocker-summary.json", blocker_summary)
    write_json(full_output / "demotion-dry-run.json", demotion)
    (full_output / "redacted-readiness-report.md").write_text(report_text(packet, ledger), encoding="utf-8")
    validate_generated_outputs(full_output)


def validate_generated_outputs(output_dir: Path) -> None:
    for artifact in GENERATED_ARTIFACTS:
        if not (output_dir / artifact).is_file():
            raise VerificationError(f"generated artifact is missing: {artifact}")
    ledger = json.loads((output_dir / "readiness-coverage-ledger.json").read_text(encoding="utf-8"))
    packet = json.loads((output_dir / "final-readiness-packet.json").read_text(encoding="utf-8"))
    blockers = json.loads((output_dir / "readiness-blocker-summary.json").read_text(encoding="utf-8"))
    demotion = json.loads((output_dir / "demotion-dry-run.json").read_text(encoding="utf-8"))
    report = (output_dir / "redacted-readiness-report.md").read_text(encoding="utf-8")
    for index, row in enumerate(ledger.get("rows", [])):
        missing_fields = [
            field for field in LEDGER_FIELDS if field not in row
        ]
        if missing_fields:
            raise VerificationError(
                f"ledger row {index} missing required fields: "
                f"{', '.join(missing_fields)}"
            )
    if packet.get("ledger_rows") != ledger.get("rows"):
        raise VerificationError("packet and canonical ledger rows differ")
    expected_blockers = [row for row in ledger.get("rows", []) if row.get("readiness_effect") == "blocked"]
    if blockers.get("blockers") != expected_blockers:
        raise VerificationError("blocker summary is not derived from the canonical ledger")
    if packet.get("demotion_dry_run") != demotion:
        raise VerificationError("packet and demotion dry-run differ")
    if f"readiness_state: {packet.get('readiness_state')}" not in report or f"gate_state: {demotion.get('gate_state')}" not in report:
        raise VerificationError("redacted report is not derived from packet state")


def run_quick(
    root: Path,
    phase31_output: str,
    phase33_handoff: str,
    output_arg: str,
) -> str | None:
    load_contract(root)
    relative_output, full_output = output_paths(root, output_arg)
    reason_code = SOURCE_FAILURE_REASON_CODES[1]
    try:
        raw_handoff_path = repo_relative_path(
            phase33_handoff,
            "--phase33-handoff",
        )
        resolved_handoff = (root / raw_handoff_path).resolve(strict=False)
        if (
            resolved_handoff == full_output
            or full_output in resolved_handoff.parents
        ):
            raise VerificationError(
                "--phase33-handoff must be outside the generated --output-dir"
            )
        path_under(
            raw_handoff_path,
            PHASE33_OUTPUT_ROOT,
            "--phase33-handoff",
        )

        reason_code = SOURCE_FAILURE_REASON_CODES[0]
        required_streams = load_phase31_required_streams(root)
        manifest_path, manifest, receipts, accepted_receipt_rows = load_phase31(
            root,
            phase31_output,
        )

        reason_code = SOURCE_FAILURE_REASON_CODES[1]
        handoff_path, handoff, register_refs = load_phase33_handoff(
            root,
            phase33_handoff,
            full_output,
        )

        reason_code = SOURCE_FAILURE_REASON_CODES[2]
        normalized = load_phase33_register(
            root,
            register_refs,
            "normalized_decision_records",
        )
        raw_decisions = require_list(
            normalized.get("rows"),
            "normalized decision rows",
        )
        if not all(isinstance(row, dict) for row in raw_decisions):
            raise VerificationError(
                "normalized decision rows must contain objects"
            )
        decisions = [dict(row) for row in raw_decisions]
        decisions_by_id = validate_normalized_decisions(decisions)

        reason_code = SOURCE_FAILURE_REASON_CODES[3]
        readiness_input = load_phase33_register(
            root,
            register_refs,
            "readiness_decision_handoff",
        )
        validate_readiness_handoff(readiness_input, decisions_by_id)

        reason_code = SOURCE_FAILURE_REASON_CODES[5]
        blocker_register = load_phase32_blocker_register(root)
        blocker_rows = require_list(
            blocker_register.get("rows"),
            "Phase 32 blocker rows",
        )
        if not all(isinstance(row, dict) for row in blocker_rows):
            raise VerificationError(
                "Phase 32 blocker rows must contain objects"
            )

        reason_code = SOURCE_FAILURE_REASON_CODES[6]
        demotion_input = load_phase33_register(root, register_refs, "demotion_decision_handoff")
        validation, decision, source_refs = validate_demotion_handoff(
            demotion_input,
            decisions_by_id,
        )

        reason_code = SOURCE_FAILURE_REASON_CODES[4]
        register_digests = phase33_register_digests(root, register_refs)
    except VerificationError as error:
        approval_validation_state = (
            "missing"
            if reason_code == "phase33-demotion-input-invalid"
            and str(error).startswith("missing required file:")
            else "invalid"
        )
        publish_source_failure_bundle(
            root,
            relative_output,
            full_output,
            reason_code,
            approval_validation_state,
        )
        return reason_code
    ledger = evaluate_coverage(receipts, blocker_rows, decisions, required_streams)
    readiness, readiness_reasons, maybe_readiness_error = readiness_state(
        ledger,
        readiness_input,
        decisions_by_id,
    )
    demotion = evaluate_demotion(readiness, validation, decision, source_refs)
    write_bundle(
        root,
        relative_output,
        full_output,
        manifest_path,
        manifest,
        accepted_receipt_rows,
        handoff_path,
        handoff,
        blocker_register,
        ledger,
        readiness,
        readiness_reasons,
        demotion,
        register_digests,
    )
    run_security_scan(root, relative_output)
    return maybe_readiness_error


def validate_output_security(
    full_output: Path,
    display_root: str,
) -> None:
    errors = []
    for artifact in NON_SNAPSHOT_OUTPUTS:
        candidate = full_output / artifact
        if not candidate.is_file():
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
            reject_forbidden_text(Path(artifact), text)
            if candidate.suffix == ".json":
                reject_forbidden_fields(
                    json.loads(text),
                    artifact,
                )
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    print(f"Phase 34 security scan passed for {display_root}")


def run_security_scan(root: Path, output_arg: str | Path = DEFAULT_OUTPUT_DIR) -> None:
    relative_output = path_under(output_arg, DEFAULT_OUTPUT_DIR, "--output-dir")
    full_output = root / relative_output
    if not full_output.exists():
        print(f"no Phase 34 outputs to scan at {relative_output.as_posix()}")
        return
    if full_output.is_symlink() or not full_output.is_dir():
        raise VerificationError(f"Phase 34 output root contains a symlink escape: {relative_output.as_posix()}")
    validate_output_security(full_output, relative_output.as_posix())


def shell_case_commands(text: str, case_name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{case_name})":
            continue
        commands = []
        for body_line in lines[index + 1:]:
            stripped = body_line.strip()
            if stripped == ";;":
                return commands
            if stripped.startswith("python3 "):
                commands.append(stripped)
    return None


def just_recipe_commands(text: str, recipe_name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{recipe_name}:":
            continue
        commands = []
        for body_line in lines[index + 1:]:
            if body_line and not body_line[0].isspace():
                break
            if body_line.strip():
                commands.append(body_line.strip())
        return commands
    return None


def check_wiring(root: Path) -> None:
    required = {
        "tools/bazel/BUILD.bazel": [
            'name = "phase34_source_ref_manifests"',
            'name = "phase34_verify"',
            'name = "phase34_verify_tests"',
            '"phase34_decision_reconciliation.py"',
            '"phase34_decision_reconciliation_test.py"',
            '"phase34_decision_reconciliation_integration_test.py"',
            "//:phase34_final_readiness_demotion_dry_run_docs",
        ],
        "BUILD.bazel": [
            'name = "phase34_final_readiness_demotion_dry_run_docs"',
            'name = "phase34_verify"',
            'actual = "//tools/bazel:phase34_verify"',
            'name = "phase34_verify_tests"',
        ],
        "tools/bazel/rust_workflow.sh": ["phase34_verify)", "phase34_verify_tests)"],
        "justfile": ["phase34-verify:", "bazel run //tools/bazel:phase34_verify_tests", "bazel run //tools/bazel:phase34_verify"],
    }
    errors = []
    texts: dict[str, str] = {}
    for relative_path, snippets in required.items():
        path = root / relative_path
        if not path.is_file():
            errors.append(f"missing required file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        texts[relative_path] = text
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{relative_path} missing {snippet}")
    workflow = texts.get("tools/bazel/rust_workflow.sh", "")
    if shell_case_commands(workflow, "phase34_verify") != PHASE34_VERIFY_COMMANDS:
        errors.append("tools/bazel/rust_workflow.sh phase34_verify command order is invalid")
    if shell_case_commands(workflow, "phase34_verify_tests") != [
        "python3 tools/bazel/phase33_maintainer_decision_inputs_test.py",
        "python3 tools/bazel/phase34_decision_reconciliation_test.py",
        "python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py",
        "python3 tools/bazel/phase34_decision_reconciliation_integration_test.py",
    ]:
        errors.append("tools/bazel/rust_workflow.sh phase34_verify_tests command is invalid")
    if just_recipe_commands(texts.get("justfile", ""), "phase34-verify") != [
        "bazel run //tools/bazel:phase34_verify_tests",
        "bazel run //tools/bazel:phase34_verify",
    ]:
        errors.append("justfile phase34-verify must run tests before verifier")
    if errors:
        raise VerificationError("\n".join(errors))
    print("Phase 34 wiring passed")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Phase 34 final readiness and demotion dry-run artifacts.")
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--phase31-output-dir", default=DEFAULT_PHASE31_OUTPUT_DIR.as_posix())
    parser.add_argument("--phase33-handoff", default=DEFAULT_PHASE33_HANDOFF.as_posix())
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.contract_only:
            contract = load_contract(ROOT)
            print(f"{contract['id']} ok")
            return 0
        if args.security_only:
            run_security_scan(ROOT, args.output_dir)
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            return 0
        if args.quick:
            maybe_error = run_quick(ROOT, args.phase31_output_dir, args.phase33_handoff, args.output_dir)
            if maybe_error is not None:
                raise VerificationError(maybe_error)
            print("Phase 34 final readiness and demotion dry-run quick validation passed")
            return 0
        raise VerificationError("no mode selected")
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
