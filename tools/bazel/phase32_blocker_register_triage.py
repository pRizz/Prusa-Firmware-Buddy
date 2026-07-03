#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "32-blocker-register-and-evidence-triage"
PHASE_LIFECYCLE_ID = "32-2026-07-03T14-13-51"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase32_blocker_register_triage_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase32")

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
    ("smoke_fixture", re.compile(r"\bsmoke(?:[-_ ]?fixture|[-_ ]?output)?\b", re.IGNORECASE)),
    ("local_dry_run", re.compile(r"\b(local[-_ ]?only|dry[-_ ]?run|local[-_ ]?dry)\b", re.IGNORECASE)),
    ("prose_attestation", re.compile(r"\b(prose[-_ ]?only|attestation|narrative)\b", re.IGNORECASE)),
    ("row_only_submission", re.compile(r"\b(upstream[-_ ]?row[-_ ]?only|row[-_ ]?only)\b", re.IGNORECASE)),
    ("lifecycle_mismatch", re.compile(r"\b(stale[-_ ]?lifecycle|lifecycle[-_ ]?mismatch|stale)\b", re.IGNORECASE)),
    ("non_final_placeholder", re.compile(r"\b(quick|default|placeholder|template[-_ ]?only|non[-_ ]?final)\b", re.IGNORECASE)),
)


class VerificationError(Exception):
    pass


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


def contract_only() -> None:
    contract = load_contract()
    print(f"{contract['id']} ok")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 32 blocker register and evidence triage verifier")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 32 contract and exit")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.contract_only:
            contract_only()
            return 0
        raise VerificationError("no mode selected")
    except VerificationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
