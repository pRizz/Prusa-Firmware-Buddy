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
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase34")
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
REQUIRED_REQUIREMENT_IDS = ["READY-01", "READY-02", "READY-03"]
LEDGER_FIELDS = [
    "row_id",
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
    open_requires = contract.get("demotion_dry_run_schema", {}).get("open_requires")
    if open_requires != {
        "readiness_state": "unblocked",
        "approval_validation_state": "valid",
        "approval_decision_state": "approve",
    }:
        raise VerificationError("demotion dry-run open predicate is invalid")


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    validate_contract(contract)
    return contract


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


def derive_expected_rows(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
                    "source_stream": stream,
                    "source_ref": source_ref,
                    "requirement_ids": sorted({str(value) for value in receipt.get("requirement_ids", [])}),
                    "proof_eligibility": "ineligible" if problem_kind else "eligible",
                    "evidence_status": str(receipt.get("evidence_status") or ("failed" if receipt.get("failure_reason") else "passed")),
                    "row_problem_kind": problem_kind,
                    "evidence_refs": sorted({source_ref, *[str(ref) for ref in receipt.get("validator_output_refs", [])]}),
                    "artifact_refs": artifact_refs,
                    "duplicate_source_ref": source_ref in duplicate_refs,
                }
            )
    for row in rows:
        row["duplicate_source_ref"] = row["source_ref"] in duplicate_refs
    return sorted(rows, key=lambda row: (row["source_stream"], row["source_ref"], row["row_id"]))


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
    if maybe_blocker is None and problem_kind:
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
        "coverage_state": coverage_state,
        "readiness_effect": readiness_effect,
        "reason_codes": sorted(set(reason_codes)),
    }
    return row


def evaluate_coverage(
    receipts: list[dict[str, Any]],
    blocker_rows: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    expected_rows = derive_expected_rows(receipts)
    blockers_by_source: dict[str, list[dict[str, Any]]] = {}
    for blocker in blocker_rows:
        source_ref = str(blocker.get("source_ref") or "")
        blockers_by_source.setdefault(source_ref, []).append(blocker)
    ledger = []
    for expected in expected_rows:
        matches = blockers_by_source.get(str(expected["source_ref"]), [])
        maybe_blocker = matches[0] if matches else None
        ledger.append(coverage_for_row(expected, maybe_blocker, len(matches) > 1, decisions))
    return ledger


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


def load_phase33(
    root: Path,
    handoff_arg: str | Path,
    full_output: Path,
) -> tuple[Path, dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    raw_path = repo_relative_path(handoff_arg, "--phase33-handoff")
    resolved_input = (root / raw_path).resolve(strict=False)
    if resolved_input == full_output or full_output in resolved_input.parents:
        raise VerificationError("--phase33-handoff must be outside the generated --output-dir")
    handoff_path = path_under(raw_path, Path("build/ci-evidence/phase33"), "--phase33-handoff")
    resolved_under(root, handoff_path, Path("build/ci-evidence/phase33"), "--phase33-handoff")
    handoff = load_json(root, handoff_path)
    scan_json(handoff, handoff_path)
    if handoff.get("artifact_name") != "phase33-maintainer-decision-inputs":
        raise VerificationError("Phase 33 handoff artifact_name must be phase33-maintainer-decision-inputs")
    if handoff.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        raise VerificationError(f"Phase 33 handoff phase_lifecycle_id must be {PHASE33_LIFECYCLE_ID}")
    if handoff.get("raw_evidence_consumed") not in {None, False}:
        raise VerificationError("Phase 33 handoff raw_evidence_consumed must be false")
    source_inputs = handoff.get("source_inputs")
    if not isinstance(source_inputs, dict) or source_inputs.get("phase32_canonical_register_ref") != PHASE32_REGISTER_REF:
        raise VerificationError(f"Phase 33 handoff must reference {PHASE32_REGISTER_REF}")
    register_refs = handoff.get("register_refs")
    if not isinstance(register_refs, dict):
        raise VerificationError("Phase 33 handoff register_refs must be an object")

    def load_register(name: str) -> dict[str, Any]:
        value = register_refs.get(name)
        if not isinstance(value, str):
            raise VerificationError(f"Phase 33 register_refs.{name} must be a path")
        register_path = path_under(value, Path("build/ci-evidence/phase33"), f"register_refs.{name}")
        payload = load_json(root, register_path)
        scan_json(payload, register_path)
        return payload

    normalized = load_register("normalized_decision_records")
    readiness = load_register("readiness_decision_handoff")
    demotion = load_register("demotion_decision_handoff")
    decisions = require_list(normalized.get("rows"), "normalized decision rows")
    if not all(isinstance(row, dict) for row in decisions):
        raise VerificationError("normalized decision rows must contain objects")
    blocker_register = load_json(root, Path(PHASE32_REGISTER_REF))
    scan_json(blocker_register, Path(PHASE32_REGISTER_REF))
    if blocker_register.get("phase_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError(f"Phase 32 blocker register phase_lifecycle_id must be {PHASE32_LIFECYCLE_ID}")
    return handoff_path, handoff, decisions, readiness, demotion, blocker_register


def approval_state(maybe_demotion: dict[str, Any]) -> tuple[str, str, list[str], str | None]:
    if maybe_demotion.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        return "invalid", "missing", [], "Phase 33 demotion approval lifecycle is stale or malformed"
    authorization_state = maybe_demotion.get("authorization_state")
    if authorization_state == "blocked" and maybe_demotion.get("demotion_input_supplied") is False:
        return "missing", "missing", [], None
    source_refs = [str(ref) for ref in maybe_demotion.get("source_row_refs", []) if isinstance(ref, str)]
    if authorization_state == "rejected":
        return "valid", "reject", source_refs, None
    if authorization_state != "approved-input-recorded":
        return "invalid", "missing", source_refs, "Phase 33 demotion approval state is invalid"
    required = ["decision_id", "maintainer_identity_ref", "maintainer_role", "decision_timestamp"]
    if any(not isinstance(maybe_demotion.get(field), str) or not str(maybe_demotion.get(field)).strip() for field in required):
        return "invalid", "missing", source_refs, "Phase 33 demotion approval metadata is malformed"
    return "valid", "approve", source_refs, None


def readiness_state(ledger: list[dict[str, Any]], readiness: dict[str, Any]) -> tuple[str, list[str]]:
    reason_codes = sorted({reason for row in ledger for reason in row["reason_codes"]})
    if not ledger:
        reason_codes.append("required-row-missing")
    if readiness.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        reason_codes.append("readiness-input-invalid")
    if readiness.get("handoff_state") != "approval-input-recorded":
        reason_codes.append("readiness-input-invalid")
    if any(row["readiness_effect"] == "blocked" for row in ledger):
        return "blocked", sorted(set(reason_codes))
    if reason_codes:
        return "blocked", sorted(set(reason_codes))
    return "unblocked", []


def reset_output_root(full_output: Path) -> None:
    if full_output.exists():
        if full_output.is_symlink() or not full_output.is_dir():
            raise VerificationError(f"--output-dir contains a symlink escape or is not a normal directory: {full_output}")
        shutil.rmtree(full_output)
    full_output.mkdir(parents=True, exist_ok=True)


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
        "| Row | Stream | Coverage | Readiness | Reasons |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in ledger:
        values = [
            row["row_id"],
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
    if packet.get("ledger_rows") != ledger.get("rows"):
        raise VerificationError("packet and canonical ledger rows differ")
    expected_blockers = [row for row in ledger.get("rows", []) if row.get("readiness_effect") == "blocked"]
    if blockers.get("blockers") != expected_blockers:
        raise VerificationError("blocker summary is not derived from the canonical ledger")
    if packet.get("demotion_dry_run") != demotion:
        raise VerificationError("packet and demotion dry-run differ")
    if f"readiness_state: {packet.get('readiness_state')}" not in report or f"gate_state: {demotion.get('gate_state')}" not in report:
        raise VerificationError("redacted report is not derived from packet state")


def run_quick(root: Path, phase31_output: str, phase33_handoff: str, output_arg: str) -> str | None:
    load_contract(root)
    relative_output, full_output = output_paths(root, output_arg)
    raw_handoff_path = repo_relative_path(phase33_handoff, "--phase33-handoff")
    resolved_handoff = (root / raw_handoff_path).resolve(strict=False)
    if resolved_handoff == full_output or full_output in resolved_handoff.parents:
        raise VerificationError("--phase33-handoff must be outside the generated --output-dir")
    path_under(raw_handoff_path, Path("build/ci-evidence/phase33"), "--phase33-handoff")
    manifest_path, manifest, receipts, accepted_receipt_rows = load_phase31(root, phase31_output)
    handoff_path, handoff, decisions, readiness_input, demotion_input, blocker_register = load_phase33(
        root,
        phase33_handoff,
        full_output,
    )
    blocker_rows = require_list(blocker_register.get("rows"), "Phase 32 blocker rows")
    if not all(isinstance(row, dict) for row in blocker_rows):
        raise VerificationError("Phase 32 blocker rows must contain objects")
    ledger = evaluate_coverage(receipts, blocker_rows, decisions)
    readiness, readiness_reasons = readiness_state(ledger, readiness_input)
    validation, decision, source_refs, maybe_error = approval_state(demotion_input)
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
    )
    run_security_scan(root, relative_output)
    return maybe_error


def run_security_scan(root: Path, output_arg: str | Path = DEFAULT_OUTPUT_DIR) -> None:
    relative_output = path_under(output_arg, DEFAULT_OUTPUT_DIR, "--output-dir")
    full_output = root / relative_output
    if not full_output.exists():
        print(f"no Phase 34 outputs to scan at {relative_output.as_posix()}")
        return
    if full_output.is_symlink() or not full_output.is_dir():
        raise VerificationError(f"Phase 34 output root contains a symlink escape: {relative_output.as_posix()}")
    errors = []
    for artifact in NON_SNAPSHOT_OUTPUTS:
        candidate = full_output / artifact
        if not candidate.is_file():
            continue
        relative_path = candidate.relative_to(root)
        try:
            text = candidate.read_text(encoding="utf-8")
            reject_forbidden_text(relative_path, text)
            if candidate.suffix == ".json":
                reject_forbidden_fields(json.loads(text), relative_path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    print(f"Phase 34 security scan passed for {relative_output.as_posix()}")


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
        "python3 tools/bazel/phase34_final_readiness_demotion_dry_run_test.py"
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
