#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "32-blocker-register-and-evidence-triage"
PHASE_LIFECYCLE_ID = "32-2026-07-03T14-13-51"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase32_blocker_register_triage_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase32")
DEFAULT_PHASE31_OUTPUT_DIR = Path("build/ci-evidence/phase31")
DEFAULT_PHASE27_OUTPUT_DIR = Path("build/ci-evidence/phase27")
DEFAULT_PHASE28_OUTPUT_DIR = Path("build/ci-evidence/phase28")
SOURCE_CONTRACT_SNAPSHOTS = {
    "phase32_blocker_register_triage_contract.json": CONTRACT_MANIFEST,
    "phase31_final_evidence_intake_contract.json": Path("tools/bazel/manifests/phase31_final_evidence_intake_contract.json"),
    "phase23_simulator_evidence_execution_contract.json": Path("tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json"),
    "phase24_hardware_media_safety_evidence_execution_contract.json": Path(
        "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json"
    ),
    "phase25_live_service_evidence_execution_contract.json": Path("tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json"),
    "phase26_release_signing_upstream_evidence_contract.json": Path(
        "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
    ),
    "phase27_retained_code_acceptance_decisions_contract.json": Path(
        "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
    ),
    "phase28_final_readiness_packet_contract.json": Path("tools/bazel/manifests/phase28_final_readiness_packet_contract.json"),
}

REQUIRED_REQUIREMENT_IDS = {"TRIAGE-01", "TRIAGE-02", "TRIAGE-03"}
REQUIRED_SOURCE_CONTRACT_IDS = {
    "phase31_final_evidence_intake_contract",
    "phase23_simulator_evidence_execution_contract",
    "phase24_hardware_media_safety_evidence_execution_contract",
    "phase25_live_service_evidence_execution_contract",
    "phase26_release_signing_upstream_evidence_contract",
    "phase27_retained_code_acceptance_decisions_contract",
    "phase28_final_readiness_packet_contract",
}
REQUIRED_CANONICAL_FIELDS = {
    "row_id",
    "source_stream",
    "source_ref",
    "requirement_ids",
    "affected_gate",
    "row_problem_kind",
    "blocker_kind",
    "severity",
    "owner_ref",
    "required_next_action",
    "decision_impact",
    "proof_eligibility",
    "evidence_refs",
}
REQUIRED_ENUMS = {
    "blocker_kind": {"repair_item", "exception_request", "unresolved_decision_blocker"},
    "row_problem_kind": {
        "failed",
        "missing",
        "stale",
        "malformed",
        "redaction_failed",
        "source_ref_failed",
        "secret_tainted",
        "lifecycle_mismatch",
        "unsafe_ref",
        "exception_requested",
        "non_final_placeholder",
        "smoke_fixture",
        "local_dry_run",
        "prose_attestation",
        "row_only_submission",
        "unknown_unclassified",
    },
    "severity": {"critical", "high", "medium"},
    "proof_eligibility": {"eligible", "ineligible"},
    "decision_impact": {
        "repair_required_before_cutover",
        "exception_decision_required",
        "residual_risk_decision_required",
        "retained_code_decision_required",
        "final_readiness_blocked",
        "demotion_decision_required",
        "cutover_verdict_blocked",
    },
}
REQUIRED_OWNER_DEFAULTS = {
    "simulator": "simulator-maintainer",
    "hardware-media-safety": "safety-maintainer",
    "live-service": "network-security-maintainer",
    "release-signing": "release-maintainer",
    "upstream-result": "release-maintainer",
    "retained-code": "retained-code-maintainer",
    "readiness": "readiness-maintainer",
    "unknown": "cutover-maintainer",
}
REQUIRED_GENERATED_ARTIFACTS = {
    "blocker-register.json",
    "decision-impact-index.json",
    "exception-request-register.json",
    "residual-risk-request-register.json",
    "downstream-handoff-manifest.json",
    "redacted-blocker-register-report.md",
    "contract-snapshots/phase32_blocker_register_triage_contract.json",
    "contract-snapshots/phase31_final_evidence_intake_contract.json",
    "contract-snapshots/phase23_simulator_evidence_execution_contract.json",
    "contract-snapshots/phase24_hardware_media_safety_evidence_execution_contract.json",
    "contract-snapshots/phase25_live_service_evidence_execution_contract.json",
    "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase28_final_readiness_packet_contract.json",
}
REASON_PROBLEM_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("non_final_placeholder", re.compile(r"\b(quick|default|placeholder|template[-_ ]?only|non[-_ ]?final)\b", re.IGNORECASE)),
    ("smoke_fixture", re.compile(r"\bsmoke(?:[-_ ]?fixture|[-_ ]?output)?\b", re.IGNORECASE)),
    ("local_dry_run", re.compile(r"\b(local[-_ ]?only|dry[-_ ]?run|local[-_ ]?dry)\b", re.IGNORECASE)),
    ("prose_attestation", re.compile(r"\b(prose[-_ ]?only|attestation|narrative)\b", re.IGNORECASE)),
    ("row_only_submission", re.compile(r"\b(upstream[-_ ]?row[-_ ]?only|row[-_ ]?only)\b", re.IGNORECASE)),
    ("lifecycle_mismatch", re.compile(r"\b(stale[-_ ]?lifecycle|lifecycle[-_ ]?mismatch|stale)\b", re.IGNORECASE)),
)
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
    ("certificate-private-material", re.compile(r"certificate[_ -]?private[_ -]?material", re.IGNORECASE)),
    ("service-payload-marker", re.compile(r"\bservice[_ -]?payload\b", re.IGNORECASE)),
    ("raw-crash-dump-marker", re.compile(r"\braw[_ -]?crash[_ -]?dump\b", re.IGNORECASE)),
    ("raw-release-log-marker", re.compile(r"\braw[_ -]?release[_ -]?log\b", re.IGNORECASE)),
    ("tls-keylog-marker", re.compile(r"\btls[_ -]?keylog\b", re.IGNORECASE)),
    ("wifi-credential-marker", re.compile(r"\bwi[-_ ]?fi credential\b", re.IGNORECASE)),
    ("demotion-allowed-true", re.compile(r'"?demotion_allowed"?\s*:\s*true', re.IGNORECASE)),
    ("reference-demotion-approved", re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("final-readiness-unblocked", re.compile(r'"?final_readiness_status"?\s*:\s*"unblocked"', re.IGNORECASE)),
    ("cutover-verdict-approved", re.compile(r"\bcutover verdict approved\b", re.IGNORECASE)),
)
STREAM_GATE_DEFAULTS = {
    "simulator": "final-simulator-evidence",
    "hardware-media-safety": "final-hardware-safety-media-evidence",
    "live-service": "final-live-network-transfer-evidence",
    "release-signing": "final-release-artifact-signing-evidence",
    "upstream-result": "final-upstream-result-evidence",
    "retained-code": "final-retained-code-acceptance",
    "readiness": "final-readiness",
    "unknown": "cutover-decision",
}


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(root: Path, path: str | Path) -> str:
    relative_path = Path(path)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: str | Path) -> dict[str, Any]:
    relative_path = Path(path)
    try:
        data = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{relative_path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(f"{relative_path.as_posix()} must contain a top-level object")
    return data


def write_json(root: Path, path: Path, data: Any) -> None:
    full_path = root / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError(f"{field} must be a list")
    return value


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{field} must be a non-empty string")
    return value


def require_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{field} must be an object")
    return value


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def repo_relative_path(path_value: str | Path, field: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{field} must be repo-relative without traversal: {relative_path.as_posix()}")
    return relative_path


def path_under(path_value: str | Path, expected_root: Path, field: str) -> Path:
    relative_path = repo_relative_path(path_value, field)
    try:
        relative_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"{field} must stay under {expected_root.as_posix()}: {relative_path.as_posix()}") from error
    return relative_path


def reject_symlink_components(root: Path, relative_path: Path, field: str) -> None:
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(f"{field} contains a symlink component: {relative_path.as_posix()}")


def reset_output_root(root: Path, output_dir: Path) -> Path:
    relative_output_dir = path_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    reject_symlink_components(root, relative_output_dir, "--output-dir")
    full_output_dir = root / relative_output_dir
    if full_output_dir.exists():
        if full_output_dir.is_symlink() or not full_output_dir.is_dir():
            raise VerificationError(f"--output-dir exists and is not a normal directory: {relative_output_dir.as_posix()}")
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)
    return relative_output_dir


def stable_sha12(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:12]


def stable_row_id(prefix: str, source_stream: str, payload: Any) -> str:
    safe_stream = re.sub(r"[^a-z0-9-]", "-", source_stream.casefold()).strip("-") or "unknown"
    return f"{prefix}-{safe_stream}-{stable_sha12(payload)}"


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("id") != "phase32_blocker_register_triage_contract":
        raise VerificationError("contract id must be phase32_blocker_register_triage_contract")
    if contract.get("phase") != PHASE:
        raise VerificationError(f"contract phase must be {PHASE}")
    if contract.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(f"contract lifecycle must be {PHASE_LIFECYCLE_ID}")
    if contract.get("output_root") != DEFAULT_OUTPUT_DIR.as_posix():
        raise VerificationError(f"contract output_root must be {DEFAULT_OUTPUT_DIR.as_posix()}")

    requirement_ids = set(require_list(contract.get("requirement_ids"), "requirement_ids"))
    if requirement_ids != REQUIRED_REQUIREMENT_IDS:
        raise VerificationError(f"requirement_ids must be {sorted(REQUIRED_REQUIREMENT_IDS)}")

    source_contracts = require_list(contract.get("source_contracts"), "source_contracts")
    source_contract_ids = {require_string(require_dict(item, "source_contracts[]").get("id"), "source_contracts[].id") for item in source_contracts}
    if source_contract_ids != REQUIRED_SOURCE_CONTRACT_IDS:
        raise VerificationError(f"source_contracts ids must be {sorted(REQUIRED_SOURCE_CONTRACT_IDS)}")

    canonical_schema = require_dict(contract.get("canonical_row_schema"), "canonical_row_schema")
    canonical_fields = set(require_list(canonical_schema.get("required_fields"), "canonical_row_schema.required_fields"))
    if canonical_fields != REQUIRED_CANONICAL_FIELDS:
        raise VerificationError(f"canonical fields must be {sorted(REQUIRED_CANONICAL_FIELDS)}")

    enums = require_dict(contract.get("enums"), "enums")
    for enum_name, expected_values in REQUIRED_ENUMS.items():
        actual_values = set(require_list(enums.get(enum_name), f"enums.{enum_name}"))
        if actual_values != expected_values:
            raise VerificationError(f"enums.{enum_name} must be {sorted(expected_values)}")

    owner_defaults = require_dict(contract.get("owner_defaults"), "owner_defaults")
    if owner_defaults != REQUIRED_OWNER_DEFAULTS:
        raise VerificationError("owner_defaults must match Phase 32 stream owner policy")

    policy_map = require_dict(contract.get("policy_map"), "policy_map")
    missing_policy = REQUIRED_ENUMS["row_problem_kind"] - set(policy_map)
    if missing_policy:
        raise VerificationError(f"policy_map missing problem kinds: {', '.join(sorted(missing_policy))}")

    generated_artifacts = set(require_list(contract.get("generated_artifacts"), "generated_artifacts"))
    if generated_artifacts != REQUIRED_GENERATED_ARTIFACTS:
        raise VerificationError(f"generated_artifacts must be {sorted(REQUIRED_GENERATED_ARTIFACTS)}")


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    validate_contract(contract)
    return contract


def classify_reason(reason: str) -> str | None:
    for problem_kind, pattern in REASON_PROBLEM_PATTERNS:
        if pattern.search(reason):
            return problem_kind
    return None


def classify_problem_kind(signal: dict[str, Any]) -> str:
    reason = str(signal.get("failure_reason") or signal.get("reason") or "")
    maybe_reason_problem = classify_reason(reason)
    if maybe_reason_problem is not None:
        return maybe_reason_problem

    finality_status = str(signal.get("finality_status") or "")
    if finality_status in {"rejected-final", "quarantined-non-final"}:
        return "unknown_unclassified"

    if signal.get("redaction_status") in {"failed", "rejected", "redaction-failed", "rejected-redaction"}:
        return "redaction_failed"
    if signal.get("source_ref_status") in {"failed", "rejected", "source-ref-failed"}:
        return "source_ref_failed"
    if signal.get("source_lifecycle_status") in {"stale", "mismatch", "lifecycle-mismatch"}:
        return "lifecycle_mismatch"
    if signal.get("exception_status") in {"exception-requested", "requested"} or signal.get("status") == "exception-requested":
        return "exception_requested"
    if signal.get("redaction_status") in {"secret-tainted", "secret_tainted"} or signal.get("status") in {"secret-tainted", "secret_tainted"}:
        return "secret_tainted"
    if signal.get("source_ref_status") in {"unsafe-ref", "unsafe_ref"} or signal.get("status") in {"unsafe-ref", "unsafe_ref"}:
        return "unsafe_ref"
    if signal.get("status") in {"stale", "stale-lifecycle"}:
        return "stale"
    if signal.get("status") in {"failed", "blocked"}:
        return "failed"
    if signal.get("status") in {"missing", "pending", "pending-input", "pending-live-input"}:
        return "missing"
    if signal.get("status") in {"malformed", "invalid"}:
        return "malformed"
    return "unknown_unclassified"


def blocker_policy_for(problem_kind: str, source_stream: str = "unknown") -> dict[str, str]:
    contract = load_contract()
    policy_map = require_dict(contract["policy_map"], "policy_map")
    owner_defaults = require_dict(contract["owner_defaults"], "owner_defaults")
    if problem_kind not in policy_map:
        problem_kind = "unknown_unclassified"
    policy = require_dict(policy_map[problem_kind], f"policy_map.{problem_kind}")
    owner_ref = str(owner_defaults.get(source_stream) or owner_defaults["unknown"])
    return {
        "blocker_kind": require_string(policy.get("blocker_kind"), f"policy_map.{problem_kind}.blocker_kind"),
        "severity": require_string(policy.get("severity"), f"policy_map.{problem_kind}.severity"),
        "decision_impact": require_string(policy.get("decision_impact"), f"policy_map.{problem_kind}.decision_impact"),
        "proof_eligibility": require_string(policy.get("proof_eligibility"), f"policy_map.{problem_kind}.proof_eligibility"),
        "owner_ref": owner_ref,
        "required_next_action": require_string(policy.get("required_next_action"), f"policy_map.{problem_kind}.required_next_action"),
    }


def classify_signal(signal: dict[str, Any]) -> dict[str, str]:
    source_stream = str(signal.get("source_stream") or signal.get("stream") or "unknown")
    problem_kind = classify_problem_kind(signal)
    return {
        "row_problem_kind": problem_kind,
        **blocker_policy_for(problem_kind, source_stream),
    }


def gate_for(source_stream: str, signal: dict[str, Any]) -> str:
    for field in ("criterion_id", "affected_gate", "row_id"):
        value = signal.get(field)
        if isinstance(value, str) and value:
            return value
    return STREAM_GATE_DEFAULTS.get(source_stream, STREAM_GATE_DEFAULTS["unknown"])


def evidence_refs_from(signal: dict[str, Any], source_ref: str) -> list[str]:
    refs: list[str] = []
    for field in ("evidence_refs", "artifact_refs", "validator_output_refs", "residual_risk_refs", "exception_refs"):
        refs.extend(string_list(signal.get(field)))
    for field in ("artifact_ref", "manifest_ref"):
        value = signal.get(field)
        if isinstance(value, str) and value:
            refs.append(value)
    if source_ref:
        refs.append(source_ref)
    unique_refs: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        unique_refs.append(ref)
    return unique_refs or [source_ref or "external://phase32/no-evidence-ref"]


def source_requirement_ids(signal: dict[str, Any]) -> list[str]:
    maybe_requirement_ids = string_list(signal.get("requirement_ids"))
    if maybe_requirement_ids:
        return maybe_requirement_ids
    maybe_source_requirement_ids = string_list(signal.get("source_requirement_ids"))
    if maybe_source_requirement_ids:
        return maybe_source_requirement_ids
    return sorted(REQUIRED_REQUIREMENT_IDS)


def build_blocker_row(
    *,
    row_id_prefix: str,
    source_stream: str,
    source_ref: str,
    signal: dict[str, Any],
    policy_override: dict[str, str] | None = None,
) -> dict[str, Any]:
    classification = classify_signal({"source_stream": source_stream, **signal})
    if policy_override:
        classification.update(policy_override)
    owner = signal.get("owner")
    if isinstance(owner, str) and owner:
        classification["owner_ref"] = owner
    if not classification.get("owner_ref") or not classification.get("required_next_action"):
        raise VerificationError(f"blocker row for {source_ref} did not receive explicit owner/action")
    return {
        "row_id": stable_row_id(row_id_prefix, source_stream, {"source_ref": source_ref, "signal": signal}),
        "source_stream": source_stream,
        "source_ref": source_ref,
        "requirement_ids": source_requirement_ids(signal),
        "affected_gate": gate_for(source_stream, signal),
        "row_problem_kind": classification["row_problem_kind"],
        "blocker_kind": classification["blocker_kind"],
        "severity": classification["severity"],
        "owner_ref": classification["owner_ref"],
        "required_next_action": classification["required_next_action"],
        "decision_impact": classification["decision_impact"],
        "proof_eligibility": classification["proof_eligibility"],
        "evidence_refs": evidence_refs_from(signal, source_ref),
    }


def is_non_blocking_source_row(signal: dict[str, Any]) -> bool:
    return (
        signal.get("status") == "passed"
        and signal.get("redaction_status", "passed") == "passed"
        and signal.get("source_ref_status", "passed") == "passed"
        and signal.get("source_lifecycle_status", "passed") in {"passed", "", None}
        and signal.get("exception_status", "none") in {"none", "", None}
    )


def load_phase31_rows(root: Path, phase31_output_dir: Path) -> list[dict[str, Any]]:
    phase31_dir = path_under(phase31_output_dir, DEFAULT_PHASE31_OUTPUT_DIR, "--phase31-output-dir")
    manifest_path = phase31_dir / "final-intake-manifest.json"
    rejected_path = phase31_dir / "rejected-submissions.json"
    manifest = load_json(root, manifest_path)
    rejected = load_json(root, rejected_path)
    rows: list[dict[str, Any]] = []

    for rejected_row in require_list(rejected.get("rejected_submissions"), "rejected_submissions"):
        if not isinstance(rejected_row, dict):
            raise VerificationError("rejected_submissions entries must be objects")
        source_stream = str(rejected_row.get("stream") or "unknown")
        submission_id = str(rejected_row.get("submission_id") or stable_sha12(rejected_row))
        signal = {
            "finality_status": rejected_row.get("finality_status"),
            "failure_reason": rejected_row.get("reason", ""),
            "requirement_ids": rejected_row.get("requirement_ids", []),
            "status": rejected_row.get("finality_status"),
        }
        rows.append(
            build_blocker_row(
                row_id_prefix="phase31-rejection",
                source_stream=source_stream,
                source_ref=f"{rejected_path.as_posix()}#{submission_id}",
                signal=signal,
            )
        )

    for receipt_ref in string_list(manifest.get("receipt_refs")):
        receipt_path = repo_relative_path(receipt_ref, "receipt_refs[]")
        receipt = load_json(root, receipt_path)
        source_stream = str(receipt.get("stream") or "unknown")
        if receipt.get("finality_status") != "accepted-final":
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase31-receipt",
                    source_stream=source_stream,
                    source_ref=receipt_path.as_posix(),
                    signal={
                        "finality_status": receipt.get("finality_status"),
                        "failure_reason": receipt.get("failure_reason", ""),
                        "requirement_ids": receipt.get("requirement_ids", []),
                    },
                )
            )
            continue
        consumed_refs = string_list(receipt.get("consumed_upstream_row_refs"))
        if not consumed_refs:
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase31-receipt-row",
                    source_stream=source_stream,
                    source_ref=f"{receipt_path.as_posix()}#missing-consumed-upstream-row-refs",
                    signal={
                        "status": "missing",
                        "failure_reason": "accepted-final receipt did not list consumed upstream row refs",
                        "requirement_ids": receipt.get("requirement_ids", []),
                    },
                )
            )
            continue
        for consumed_ref in consumed_refs:
            consumed_path = repo_relative_path(consumed_ref, "consumed_upstream_row_refs[]")
            if not (root / consumed_path).exists():
                rows.append(
                    build_blocker_row(
                        row_id_prefix="phase31-receipt-row",
                        source_stream=source_stream,
                        source_ref=consumed_path.as_posix(),
                        signal={
                            "status": "missing",
                            "failure_reason": "accepted-final receipt referenced a missing upstream row detail",
                            "requirement_ids": receipt.get("requirement_ids", []),
                            "evidence_refs": [receipt_path.as_posix()],
                        },
                    )
                )
                continue
            source_row = load_json(root, consumed_path)
            source_signal = {**source_row, "source_stream": source_stream}
            if is_non_blocking_source_row(source_signal):
                continue
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase31-receipt-row",
                    source_stream=source_stream,
                    source_ref=consumed_path.as_posix(),
                    signal=source_signal,
                )
            )
    return rows


def missing_optional_row(path: Path, source_stream: str, decision_impact: str) -> dict[str, Any]:
    return build_blocker_row(
        row_id_prefix=f"phase32-missing-{source_stream}",
        source_stream=source_stream,
        source_ref=path.as_posix(),
        signal={"status": "missing", "requirement_ids": sorted(REQUIRED_REQUIREMENT_IDS)},
        policy_override={
            "blocker_kind": "unresolved_decision_blocker",
            "severity": "high",
            "decision_impact": decision_impact,
            "proof_eligibility": "ineligible",
            "required_next_action": f"Generate the missing {path.name} handoff artifact before downstream decisions.",
        },
    )


def phase27_rows(root: Path, phase27_output_dir: Path) -> list[dict[str, Any]]:
    phase27_dir = path_under(phase27_output_dir, DEFAULT_PHASE27_OUTPUT_DIR, "--phase27-output-dir")
    rows: list[dict[str, Any]] = []
    residual_path = phase27_dir / "residual-risk-register.json"
    exception_path = phase27_dir / "exception-decision-register.json"
    handoff_path = phase27_dir / "phase28-handoff-manifest.json"

    if not (root / residual_path).exists():
        rows.append(missing_optional_row(residual_path, "retained-code", "residual_risk_decision_required"))
    else:
        residual = load_json(root, residual_path)
        for item in require_list(residual.get("rows"), "phase27 residual rows"):
            if not isinstance(item, dict):
                raise VerificationError("phase27 residual rows must be objects")
            row_type = str(item.get("row_type") or "")
            source_stream = "retained-code" if row_type == "retained_code_decision" else "readiness"
            decision_impact = "retained_code_decision_required" if source_stream == "retained-code" else "residual_risk_decision_required"
            row_id = str(item.get("row_id") or stable_sha12(item))
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase27-residual-risk",
                    source_stream=source_stream,
                    source_ref=f"{residual_path.as_posix()}#{row_id}",
                    signal={"status": "missing", "owner": item.get("owner"), "row_id": row_id, "evidence_refs": [residual_path.as_posix()]},
                    policy_override={
                        "blocker_kind": "unresolved_decision_blocker",
                        "severity": "medium",
                        "decision_impact": decision_impact,
                        "proof_eligibility": "ineligible",
                        "required_next_action": "Route residual-risk or retained-code item to Phase 33 decision input.",
                    },
                )
            )

    if not (root / exception_path).exists():
        rows.append(missing_optional_row(exception_path, "retained-code", "exception_decision_required"))
    else:
        exceptions = load_json(root, exception_path)
        for item in require_list(exceptions.get("rows"), "phase27 exception rows"):
            if not isinstance(item, dict):
                raise VerificationError("phase27 exception rows must be objects")
            row_id = str(item.get("row_id") or item.get("criterion_id") or stable_sha12(item))
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase27-exception",
                    source_stream="retained-code",
                    source_ref=f"{exception_path.as_posix()}#{row_id}",
                    signal={
                        "status": "exception-requested",
                        "exception_status": item.get("exception_state", "exception-requested"),
                        "owner": item.get("owner"),
                        "criterion_id": item.get("criterion_id"),
                        "evidence_refs": [exception_path.as_posix()],
                    },
                )
            )

    if not (root / handoff_path).exists():
        rows.append(missing_optional_row(handoff_path, "readiness", "demotion_decision_required"))
    else:
        handoff = load_json(root, handoff_path)
        if handoff.get("demotion_authorization") == "blocked":
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase27-handoff",
                    source_stream="readiness",
                    source_ref=f"{handoff_path.as_posix()}#demotion-authorization",
                    signal={"status": "missing", "criterion_id": "final-reference-demotion-allowed", "evidence_refs": [handoff_path.as_posix()]},
                    policy_override={
                        "blocker_kind": "unresolved_decision_blocker",
                        "severity": "high",
                        "decision_impact": "demotion_decision_required",
                        "proof_eligibility": "ineligible",
                        "required_next_action": "Route reference-demotion authorization to the later explicit maintainer decision gate.",
                    },
                )
            )
    return rows


def phase28_rows(root: Path, phase28_output_dir: Path) -> list[dict[str, Any]]:
    phase28_dir = path_under(phase28_output_dir, DEFAULT_PHASE28_OUTPUT_DIR, "--phase28-output-dir")
    rows: list[dict[str, Any]] = []
    blocker_path = phase28_dir / "blocker-summary.json"
    residual_path = phase28_dir / "exception-residual-risk-summary.json"
    demotion_path = phase28_dir / "reference-demotion-authorization-record.json"

    if not (root / blocker_path).exists():
        rows.append(missing_optional_row(blocker_path, "readiness", "final_readiness_blocked"))
    else:
        blocker_summary = load_json(root, blocker_path)
        for item in require_list(blocker_summary.get("blockers"), "phase28 blockers"):
            if not isinstance(item, dict):
                raise VerificationError("phase28 blockers must be objects")
            criterion_id = str(item.get("criterion_id") or stable_sha12(item))
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase28-readiness",
                    source_stream="readiness",
                    source_ref=f"{blocker_path.as_posix()}#{criterion_id}",
                    signal={
                        "status": item.get("phase27_status") or item.get("phase26_status") or "blocked",
                        "criterion_id": criterion_id,
                        "evidence_refs": [blocker_path.as_posix()],
                    },
                    policy_override={
                        "blocker_kind": "unresolved_decision_blocker",
                        "severity": "high",
                        "decision_impact": "final_readiness_blocked",
                        "proof_eligibility": "ineligible",
                        "required_next_action": "Resolve readiness blocker or route it through explicit later decision input.",
                    },
                )
            )

    if not (root / residual_path).exists():
        rows.append(missing_optional_row(residual_path, "readiness", "residual_risk_decision_required"))
    else:
        residual_summary = load_json(root, residual_path)
        for item in require_list(residual_summary.get("rows"), "phase28 residual rows"):
            if not isinstance(item, dict):
                raise VerificationError("phase28 residual rows must be objects")
            criterion_id = str(item.get("criterion_id") or stable_sha12(item))
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase28-residual-risk",
                    source_stream="readiness",
                    source_ref=f"{residual_path.as_posix()}#{criterion_id}",
                    signal={"status": "missing", "criterion_id": criterion_id, "evidence_refs": [residual_path.as_posix()]},
                    policy_override={
                        "blocker_kind": "unresolved_decision_blocker",
                        "severity": "medium",
                        "decision_impact": "residual_risk_decision_required",
                        "proof_eligibility": "ineligible",
                        "required_next_action": "Route residual-risk row to explicit later decision input.",
                    },
                )
            )

    if not (root / demotion_path).exists():
        rows.append(missing_optional_row(demotion_path, "readiness", "demotion_decision_required"))
    else:
        demotion = load_json(root, demotion_path)
        if demotion.get("reference_demotion_authorization") == "blocked":
            rows.append(
                build_blocker_row(
                    row_id_prefix="phase28-demotion",
                    source_stream="readiness",
                    source_ref=f"{demotion_path.as_posix()}#reference-demotion-authorization",
                    signal={"status": "missing", "criterion_id": "final-reference-demotion-allowed", "evidence_refs": [demotion_path.as_posix()]},
                    policy_override={
                        "blocker_kind": "unresolved_decision_blocker",
                        "severity": "high",
                        "decision_impact": "demotion_decision_required",
                        "proof_eligibility": "ineligible",
                        "required_next_action": "Provide a valid explicit demotion decision in the later demotion gate.",
                    },
                )
            )
    return rows


def validate_register_rows(rows: list[dict[str, Any]]) -> None:
    row_ids: set[str] = set()
    for row in rows:
        missing_fields = REQUIRED_CANONICAL_FIELDS - set(row)
        if missing_fields:
            raise VerificationError(f"{row.get('row_id', '<unknown>')} missing fields: {', '.join(sorted(missing_fields))}")
        if row["row_id"] in row_ids:
            raise VerificationError(f"duplicate row_id: {row['row_id']}")
        row_ids.add(row["row_id"])
        if row["proof_eligibility"] != "ineligible":
            raise VerificationError(f"{row['row_id']} must be proof-ineligible in the blocker register")
        for field in ("owner_ref", "required_next_action", "decision_impact"):
            if not isinstance(row[field], str) or not row[field]:
                raise VerificationError(f"{row['row_id']} {field} must be explicit")


def build_derived_views(rows: list[dict[str, Any]]) -> dict[str, Any]:
    register_ids = {row["row_id"] for row in rows}
    decision_rows = [
        {
            "row_id": row["row_id"],
            "source_stream": row["source_stream"],
            "affected_gate": row["affected_gate"],
            "blocker_kind": row["blocker_kind"],
            "severity": row["severity"],
            "decision_impact": row["decision_impact"],
        }
        for row in rows
    ]
    exception_rows = [
        {
            "row_id": row["row_id"],
            "source_ref": row["source_ref"],
            "owner_ref": row["owner_ref"],
            "required_next_action": row["required_next_action"],
            "decision_impact": row["decision_impact"],
        }
        for row in rows
        if row["blocker_kind"] == "exception_request"
    ]
    residual_rows = [
        {
            "row_id": row["row_id"],
            "source_ref": row["source_ref"],
            "owner_ref": row["owner_ref"],
            "required_next_action": row["required_next_action"],
            "decision_impact": row["decision_impact"],
        }
        for row in rows
        if row["decision_impact"] == "residual_risk_decision_required"
    ]
    for derived_row in [*decision_rows, *exception_rows, *residual_rows]:
        if derived_row["row_id"] not in register_ids:
            raise VerificationError(f"derived row does not reference canonical row_id: {derived_row['row_id']}")
    return {
        "decision-impact-index.json": {"rows": decision_rows},
        "exception-request-register.json": {"rows": exception_rows},
        "residual-risk-request-register.json": {"rows": residual_rows},
    }


def write_report(root: Path, output_dir: Path, rows: list[dict[str, Any]]) -> None:
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
            "| {row_id} | {source_stream} | {row_problem_kind} | {blocker_kind} | {severity} | {proof_eligibility} | {owner_ref} | {decision_impact} |".format(
                **row
            )
        )
    (root / output_dir / "redacted-blocker-register-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_contract_snapshots(root: Path, output_dir: Path) -> list[str]:
    snapshot_dir = root / output_dir / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    refs: list[str] = []
    for snapshot_name, source_path in SOURCE_CONTRACT_SNAPSHOTS.items():
        source = root / source_path
        if not source.exists():
            raise VerificationError(f"missing contract snapshot source: {source_path.as_posix()}")
        destination = snapshot_dir / snapshot_name
        shutil.copy2(source, destination)
        refs.append((output_dir / "contract-snapshots" / snapshot_name).as_posix())
    return refs


def generate_handoff(root: Path, output_dir: Path, rows: list[dict[str, Any]], snapshot_refs: list[str]) -> dict[str, Any]:
    row_ids_by_kind: dict[str, list[str]] = {kind: [] for kind in sorted(REQUIRED_ENUMS["blocker_kind"])}
    for row in rows:
        row_ids_by_kind[row["blocker_kind"]].append(row["row_id"])
    return {
        "artifact_name": "phase32-blocker-register-triage",
        "canonical_register_ref": (output_dir / "blocker-register.json").as_posix(),
        "contract_snapshot_refs": snapshot_refs,
        "generated_at_utc": utc_now(),
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "proof_policy": "blocker rows are visible for triage and proof-ineligible until later phases resolve them",
        "row_count": len(rows),
        "row_ids_by_blocker_kind": row_ids_by_kind,
        "downstream_consumers": ["phase33-maintainer-decisions", "phase34-final-readiness", "phase35-cutover-decision"],
    }


def run_quick(root: Path, phase31_output_dir: Path, phase27_output_dir: Path, phase28_output_dir: Path, output_dir: Path) -> None:
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
    write_json(root, relative_output_dir / "downstream-handoff-manifest.json", generate_handoff(root, relative_output_dir, rows, snapshot_refs))
    write_report(root, relative_output_dir, rows)
    run_security_scan(root, relative_output_dir)
    print(f"wrote {len(rows)} blocker rows to {(relative_output_dir / 'blocker-register.json').as_posix()}")


def normalized_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", field_name.casefold())


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(
            key
            for key in value
            for forbidden_name in FORBIDDEN_FIELD_NAMES
            if normalized_field_name(key) == normalized_field_name(forbidden_name)
        )
        if forbidden:
            raise VerificationError(f"{path} contains forbidden fields: {', '.join(forbidden)}")
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
            errors.append(f"{path.as_posix()} contains forbidden marker {label}: {match.group(0)}")
    if errors:
        raise VerificationError("\n".join(errors))


def run_security_scan(root: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    relative_output_dir = path_under(output_dir, DEFAULT_OUTPUT_DIR, "--output-dir")
    output_root = root / relative_output_dir
    if not output_root.exists():
        print(f"no Phase 32 outputs to scan at {relative_output_dir.as_posix()}")
        return
    if output_root.is_symlink() or not output_root.is_dir():
        raise VerificationError(f"Phase 32 output root is not a normal directory: {relative_output_dir.as_posix()}")
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
                raise VerificationError(f"{relative_path.as_posix()} is not valid JSON: {error}") from error
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
    parser = argparse.ArgumentParser(description="Phase 32 blocker register and evidence triage verifier")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 32 contract and exit")
    parser.add_argument("--quick", action="store_true", help="write the Phase 32 quick blocker-register handoff bundle")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 32 generated outputs for secret or approval markers")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel/root/just workflow wiring")
    parser.add_argument("--phase31-output-dir", default=DEFAULT_PHASE31_OUTPUT_DIR.as_posix())
    parser.add_argument("--phase27-output-dir", default=DEFAULT_PHASE27_OUTPUT_DIR.as_posix())
    parser.add_argument("--phase28-output-dir", default=DEFAULT_PHASE28_OUTPUT_DIR.as_posix())
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
