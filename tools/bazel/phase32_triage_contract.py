#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from phase32_blocker_normalization import (
    NormalizationError,
    adapt_phase26_table,
    canonical_row_id,
    canonical_source_identity,
    decision_identity,
    validate_identity_bindings,
)

ROOT = Path(__file__).resolve().parents[2]
PHASE = "32-blocker-register-and-evidence-triage"
PHASE_LIFECYCLE_ID = "32-2026-07-03T14-13-51"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase32_blocker_register_triage_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase32")
DEFAULT_PHASE31_OUTPUT_DIR = Path("build/ci-evidence/phase31")
DEFAULT_PHASE27_OUTPUT_DIR = Path("build/ci-evidence/phase27")
DEFAULT_PHASE28_OUTPUT_DIR = Path("build/ci-evidence/phase28")
EXPECTED_PHASE26_TABLE_PATH = Path(
    "build/ci-evidence/phase26/upstream-result-row-table.json")
SOURCE_CONTRACT_SNAPSHOTS = {
    "phase32_blocker_register_triage_contract.json":
    CONTRACT_MANIFEST,
    "phase31_final_evidence_intake_contract.json":
    Path("tools/bazel/manifests/phase31_final_evidence_intake_contract.json"),
    "phase23_simulator_evidence_execution_contract.json":
    Path(
        "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json"
    ),
    "phase24_hardware_media_safety_evidence_execution_contract.json":
    Path(
        "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json"
    ),
    "phase25_live_service_evidence_execution_contract.json":
    Path(
        "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json"
    ),
    "phase26_release_signing_upstream_evidence_contract.json":
    Path(
        "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
    ),
    "phase27_retained_code_acceptance_decisions_contract.json":
    Path(
        "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
    ),
    "phase28_final_readiness_packet_contract.json":
    Path("tools/bazel/manifests/phase28_final_readiness_packet_contract.json"),
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
    "source_domain",
    "producer_phase",
    "producer_artifact_kind",
    "source_row_kind",
    "source_subject_id",
    "decision_axis",
    "decision_subject_id",
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
    "source_domain":
    {"final_evidence_intake", "release_signing", "retained_code", "readiness"},
    "producer_phase": {"phase26", "phase27", "phase28", "phase31", "phase32"},
    "producer_artifact_kind": {
        "phase26_upstream_result_row_table",
        "phase27_exception_decision_register",
        "phase27_phase28_handoff_manifest",
        "phase27_residual_risk_register",
        "phase28_blocker_summary",
        "phase28_exception_residual_risk_summary",
        "phase28_reference_demotion_authorization_record",
        "phase31_final_intake_receipt",
        "phase31_rejected_submissions",
        "phase32_missing_source_artifact",
    },
    "source_row_kind": {
        "demotion_authorization",
        "exception_request",
        "final_readiness_decision",
        "intake_receipt",
        "missing_source_artifact",
        "readiness_blocker",
        "rejected_submission",
        "residual_risk",
        "retained_code_decision",
        "upstream_result_criterion",
    },
    "decision_axis":
    {"retained_code", "residual_risk", "exception", "readiness", "demotion"},
    "blocker_kind":
    {"repair_item", "exception_request", "unresolved_decision_blocker"},
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
CLEAN_SOURCE_LIFECYCLE_STATUSES = {
    "current", "not-required", "passed", "", None
}
PHASE26_ALLOWED_STATUSES = {
    "missing",
    "not-required",
    "pending",
    "pending-ci-input",
    "pending-simulator-input",
    "pending-hardware-input",
    "pending-live-input",
    "pending-release-input",
    "release-run-required",
    "external-signing-required",
    "blocked-signing-key-unavailable",
    "source-contract-passed",
    "passed",
    "failed",
    "blocked",
    "rejected-redaction",
    "rejected-overclaim",
}
REASON_PROBLEM_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("non_final_placeholder",
     re.compile(
         r"\b(quick|default|placeholder|template[-_ ]?only|non[-_ ]?final)\b",
         re.IGNORECASE)),
    ("smoke_fixture",
     re.compile(r"\bsmoke(?:[-_ ]?fixture|[-_ ]?output)?\b", re.IGNORECASE)),
    ("local_dry_run",
     re.compile(r"\b(local[-_ ]?only|dry[-_ ]?run|local[-_ ]?dry)\b",
                re.IGNORECASE)),
    ("prose_attestation",
     re.compile(r"\b(prose[-_ ]?only|attestation|narrative)\b",
                re.IGNORECASE)),
    ("row_only_submission",
     re.compile(r"\b(upstream[-_ ]?row[-_ ]?only|row[-_ ]?only)\b",
                re.IGNORECASE)),
    ("lifecycle_mismatch",
     re.compile(r"\b(stale[-_ ]?lifecycle|lifecycle[-_ ]?mismatch|stale)\b",
                re.IGNORECASE)),
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
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-private-material",
     re.compile(r"certificate[_ -]?private[_ -]?material", re.IGNORECASE)),
    ("service-payload-marker",
     re.compile(r"\bservice[_ -]?payload\b", re.IGNORECASE)),
    ("raw-crash-dump-marker",
     re.compile(r"\braw[_ -]?crash[_ -]?dump\b", re.IGNORECASE)),
    ("raw-release-log-marker",
     re.compile(r"\braw[_ -]?release[_ -]?log\b", re.IGNORECASE)),
    ("tls-keylog-marker", re.compile(r"\btls[_ -]?keylog\b", re.IGNORECASE)),
    ("wifi-credential-marker",
     re.compile(r"\bwi[-_ ]?fi credential\b", re.IGNORECASE)),
    ("demotion-allowed-true",
     re.compile(r'"?demotion_allowed"?\s*:\s*true', re.IGNORECASE)),
    ("reference-demotion-approved",
     re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("final-readiness-unblocked",
     re.compile(r'"?final_readiness_status"?\s*:\s*"unblocked"',
                re.IGNORECASE)),
    ("cutover-verdict-approved",
     re.compile(r"\bcutover verdict approved\b", re.IGNORECASE)),
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
PHASE27_28_CONTAINER_ADAPTERS = {
    Path("build/ci-evidence/phase27/residual-risk-register.json"): {
        "collection_field": "rows",
        "source_domain": "retained_code",
        "producer_phase": "phase27",
        "producer_artifact_kind": "phase27_residual_risk_register",
        "source_row_kind": "residual_risk",
        "source_subject_id": "phase27-residual-risk-register-container",
        "decision_axis": "residual_risk",
        "decision_subject_id": "phase27-residual-risk-register-container",
        "source_stream": "retained-code",
        "affected_gate": "final-retained-code-acceptance",
    },
    Path("build/ci-evidence/phase27/exception-decision-register.json"): {
        "collection_field": "rows",
        "source_domain": "retained_code",
        "producer_phase": "phase27",
        "producer_artifact_kind": "phase27_exception_decision_register",
        "source_row_kind": "exception_request",
        "source_subject_id": "phase27-exception-decision-register-container",
        "decision_axis": "exception",
        "decision_subject_id": "phase27-exception-decision-register-container",
        "source_stream": "retained-code",
        "affected_gate": "final-retained-code-acceptance",
    },
    Path("build/ci-evidence/phase28/blocker-summary.json"): {
        "collection_field": "blockers",
        "source_domain": "readiness",
        "producer_phase": "phase28",
        "producer_artifact_kind": "phase28_blocker_summary",
        "source_row_kind": "readiness_blocker",
        "source_subject_id": "phase28-blocker-summary-container",
        "decision_axis": "readiness",
        "decision_subject_id": "phase28-blocker-summary-container",
        "source_stream": "readiness",
        "affected_gate": "final-readiness",
    },
    Path("build/ci-evidence/phase28/exception-residual-risk-summary.json"): {
        "collection_field": "rows",
        "source_domain": "readiness",
        "producer_phase": "phase28",
        "producer_artifact_kind": "phase28_exception_residual_risk_summary",
        "source_row_kind": "residual_risk",
        "source_subject_id":
        "phase28-exception-residual-risk-summary-container",
        "decision_axis": "residual_risk",
        "decision_subject_id":
        "phase28-exception-residual-risk-summary-container",
        "source_stream": "readiness",
        "affected_gate": "final-readiness",
    },
}


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(root: Path, path: str | Path) -> str:
    relative_path = Path(path)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: str | Path) -> dict[str, Any]:
    relative_path = Path(path)
    try:
        data = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{relative_path.as_posix()} is not valid JSON: {error}"
        ) from error
    if not isinstance(data, dict):
        raise VerificationError(
            f"{relative_path.as_posix()} must contain a top-level object")
    return data


def write_json(root: Path, path: Path, data: Any) -> None:
    full_path = root / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")


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
        raise VerificationError(
            f"{field} must be repo-relative without traversal: {relative_path.as_posix()}"
        )
    return relative_path


def path_under(path_value: str | Path, expected_root: Path,
               field: str) -> Path:
    relative_path = repo_relative_path(path_value, field)
    try:
        relative_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{field} must stay under {expected_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


def reject_symlink_components(root: Path, relative_path: Path,
                              field: str) -> None:
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(
                f"{field} contains a symlink component: {relative_path.as_posix()}"
            )


def reset_output_root(root: Path, output_dir: Path) -> Path:
    relative_output_dir = path_under(output_dir, DEFAULT_OUTPUT_DIR,
                                     "--output-dir")
    reject_symlink_components(root, relative_output_dir, "--output-dir")
    full_output_dir = root / relative_output_dir
    if full_output_dir.exists():
        if full_output_dir.is_symlink() or not full_output_dir.is_dir():
            raise VerificationError(
                f"--output-dir exists and is not a normal directory: {relative_output_dir.as_posix()}"
            )
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)
    return relative_output_dir


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("id") != "phase32_blocker_register_triage_contract":
        raise VerificationError(
            "contract id must be phase32_blocker_register_triage_contract")
    if contract.get("phase") != PHASE:
        raise VerificationError(f"contract phase must be {PHASE}")
    if contract.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"contract lifecycle must be {PHASE_LIFECYCLE_ID}")
    if contract.get("output_root") != DEFAULT_OUTPUT_DIR.as_posix():
        raise VerificationError(
            f"contract output_root must be {DEFAULT_OUTPUT_DIR.as_posix()}")

    requirement_ids = set(
        require_list(contract.get("requirement_ids"), "requirement_ids"))
    if requirement_ids != REQUIRED_REQUIREMENT_IDS:
        raise VerificationError(
            f"requirement_ids must be {sorted(REQUIRED_REQUIREMENT_IDS)}")

    source_contracts = require_list(contract.get("source_contracts"),
                                    "source_contracts")
    source_contract_ids = {
        require_string(
            require_dict(item, "source_contracts[]").get("id"),
            "source_contracts[].id")
        for item in source_contracts
    }
    if source_contract_ids != REQUIRED_SOURCE_CONTRACT_IDS:
        raise VerificationError(
            f"source_contracts ids must be {sorted(REQUIRED_SOURCE_CONTRACT_IDS)}"
        )

    canonical_schema = require_dict(contract.get("canonical_row_schema"),
                                    "canonical_row_schema")
    canonical_fields = set(
        require_list(canonical_schema.get("required_fields"),
                     "canonical_row_schema.required_fields"))
    if canonical_fields != REQUIRED_CANONICAL_FIELDS:
        raise VerificationError(
            f"canonical fields must be {sorted(REQUIRED_CANONICAL_FIELDS)}")

    enums = require_dict(contract.get("enums"), "enums")
    for enum_name, expected_values in REQUIRED_ENUMS.items():
        actual_values = set(
            require_list(enums.get(enum_name), f"enums.{enum_name}"))
        if actual_values != expected_values:
            raise VerificationError(
                f"enums.{enum_name} must be {sorted(expected_values)}")

    identity_policy = require_dict(
        contract.get("canonical_identity_policy"),
        "canonical_identity_policy",
    )
    if identity_policy.get("row_id_source_fields") != [
            "source_domain",
            "producer_phase",
            "producer_artifact_kind",
            "source_row_kind",
            "source_subject_id",
    ]:
        raise VerificationError(
            "canonical_identity_policy.row_id_source_fields must be the exact immutable source tuple"
        )
    if identity_policy.get("decision_identity_fields") != [
            "decision_axis",
            "decision_subject_id",
    ]:
        raise VerificationError(
            "canonical_identity_policy.decision_identity_fields must be the exact decision pair"
        )

    producer_adapters = require_dict(
        contract.get("producer_adapters"),
        "producer_adapters",
    )
    phase26_adapter = require_dict(
        producer_adapters.get("phase26_release_signing_table"),
        "producer_adapters.phase26_release_signing_table",
    )
    if phase26_adapter.get("selected_stream") != "release-signing":
        raise VerificationError(
            "Phase 26 table adapter must select release-signing")
    if phase26_adapter.get("expected_artifact_path"
                           ) != EXPECTED_PHASE26_TABLE_PATH.as_posix():
        raise VerificationError(
            "Phase 26 table adapter must require the contracted upstream row table path"
        )
    if phase26_adapter.get("atomic_validation") is not True:
        raise VerificationError(
            "Phase 26 table adapter must validate atomically")

    owner_defaults = require_dict(contract.get("owner_defaults"),
                                  "owner_defaults")
    if owner_defaults != REQUIRED_OWNER_DEFAULTS:
        raise VerificationError(
            "owner_defaults must match Phase 32 stream owner policy")

    policy_map = require_dict(contract.get("policy_map"), "policy_map")
    missing_policy = REQUIRED_ENUMS["row_problem_kind"] - set(policy_map)
    if missing_policy:
        raise VerificationError(
            f"policy_map missing problem kinds: {', '.join(sorted(missing_policy))}"
        )
    fail_closed_policy = require_dict(
        contract.get("fail_closed_shape_policy"),
        "fail_closed_shape_policy",
    )
    fail_closed_problem_kinds = {
        "recognized_invalid_shape": "malformed",
        "unsupported_envelope_row_kind_or_status": "unknown_unclassified",
    }
    for policy_name, expected_problem_kind in fail_closed_problem_kinds.items(
    ):
        shape_policy = require_dict(
            fail_closed_policy.get(policy_name),
            f"fail_closed_shape_policy.{policy_name}",
        )
        if shape_policy.get("row_problem_kind") != expected_problem_kind:
            raise VerificationError(
                f"fail_closed_shape_policy.{policy_name}.row_problem_kind must be {expected_problem_kind}"
            )
        problem_policy = require_dict(
            policy_map.get(expected_problem_kind),
            f"policy_map.{expected_problem_kind}",
        )
        for field in ("severity", "proof_eligibility"):
            if shape_policy.get(field) != problem_policy.get(field):
                raise VerificationError(
                    f"fail_closed_shape_policy.{policy_name}.{field} must match policy_map.{expected_problem_kind}.{field}"
                )

    generated_artifacts = set(
        require_list(contract.get("generated_artifacts"),
                     "generated_artifacts"))
    if generated_artifacts != REQUIRED_GENERATED_ARTIFACTS:
        raise VerificationError(
            f"generated_artifacts must be {sorted(REQUIRED_GENERATED_ARTIFACTS)}"
        )


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    validate_contract(contract)
    return contract
