#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "28-final-readiness-packet-and-demotion-gate"
PHASE_LIFECYCLE_ID = "28-2026-06-25T03-31-49"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase28_final_readiness_packet_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase28")
REQUIRED_REQUIREMENT_IDS = ["READ-01", "READ-02", "READ-03"]
SOURCE_CONTRACTS = [
    "tools/bazel/manifests/phase18_cutover_review_contract.json",
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json",
    "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/foreign_code_inventory.json",
    "tools/bazel/manifests/unsafe_boundary_audit.json",
]
CANONICAL_CRITERIA = [
    "final-ci-evidence",
    "final-simulator-evidence",
    "final-hardware-safety-media-evidence",
    "final-live-network-transfer-evidence",
    "final-release-artifact-signing-evidence",
    "final-retained-code-acceptance",
    "final-residual-risk-review",
    "final-maintainer-decision",
    "final-reference-demotion-allowed",
]
HARD_BLOCKER_REASONS = [
    "redaction-failed",
    "overclaim-failed",
    "lifecycle-mismatch",
    "source-ref-failed",
    "unsafe-ref",
    "secret-tainted",
]
DEMOTION_DECISION_REQUIRED_FIELDS = [
    "phase",
    "phase_lifecycle_id",
    "demotion_authorization",
    "approver",
    "approver_role",
    "decision_timestamp",
    "rationale",
    "scope",
    "evidence_refs",
]
EXCEPTION_REQUIRED_FIELDS = [
    "scope",
    "owner",
    "approver",
    "approver_role",
    "rationale",
    "affected_printer_or_release_surface",
    "evidence_refs",
    "residual_risk",
    "mitigation_or_follow_up",
    "expiry_or_review_trigger",
]
GENERATED_ARTIFACTS = [
    "final-readiness-run-manifest.json",
    "final-readiness-packet.json",
    "normalized-readiness-criteria-table.json",
    "blocker-summary.json",
    "exception-residual-risk-summary.json",
    "reference-demotion-authorization-record.json",
    "demotion-decision-input-template.json",
    "redacted-readiness-report.md",
    "artifact-reference-summary.json",
    "contract-snapshots/phase18_cutover_review_contract.json",
    "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase26-upstream-result-row-table.json",
    "contract-snapshots/phase27-phase28-handoff-manifest.json",
]


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


def require_dict(row: dict[str, Any], field: str, row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_list(row: dict[str, Any], field: str, row_name: str) -> list[Any]:
    value = row.get(field)
    if not isinstance(value, list):
        raise VerificationError(f"{row_name} {field} must be a list")
    return value


def require_string_list(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = require_list(row, field, row_name)
    if not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a list of non-empty strings")
    return value


def check_exact_string_list(row: dict[str, Any], field: str, expected: list[str], errors: list[str], row_name: str) -> None:
    try:
        actual = require_string_list(row, field, row_name)
    except VerificationError as error:
        errors.append(str(error))
        return
    if actual != expected:
        errors.append(f"{row_name} {field} does not match expected Phase 28 contract values")


def check_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_values = {
        "schema_version": "1",
        "id": "phase28_final_readiness_packet_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase28-final-readiness-packet",
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, expected in expected_values.items():
        if contract.get(field) != expected:
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected!r}")
    check_exact_string_list(contract, "source_contracts", SOURCE_CONTRACTS, errors, "contract")
    check_exact_string_list(contract, "generated_artifacts", GENERATED_ARTIFACTS, errors, "contract")
    check_exact_string_list(contract, "top_level_verdicts", ["final_readiness_status", "reference_demotion_authorization"], errors, "contract")

    requirements = require_list(contract, "requirements", "contract")
    requirement_ids = [row.get("id") for row in requirements if isinstance(row, dict)]
    if requirement_ids != REQUIRED_REQUIREMENT_IDS:
        errors.append("contract requirements must be exactly READ-01, READ-02, READ-03")

    required_inputs = require_dict(contract, "required_inputs", "contract")
    expected_inputs = {
        "phase26_upstream_rows": "build/ci-evidence/phase26/upstream-result-row-table.json",
        "phase27_handoff": "build/ci-evidence/phase27/phase28-handoff-manifest.json",
        "demotion_decision_input": "optional",
    }
    if required_inputs != expected_inputs:
        errors.append("contract required_inputs must match Phase 28 plan inputs")

    readiness_policy = require_dict(contract, "readiness_policy", "contract")
    if readiness_policy.get("default_status") != "blocked":
        errors.append("readiness_policy default_status must be blocked")
    if readiness_policy.get("hard_blockers_outrank_exceptions") is not True:
        errors.append("readiness_policy hard_blockers_outrank_exceptions must be true")
    check_exact_string_list(readiness_policy, "pass_statuses", ["passed"], errors, "readiness_policy")
    check_exact_string_list(readiness_policy, "exception_statuses", ["exception-approved"], errors, "readiness_policy")
    check_exact_string_list(
        readiness_policy,
        "exception_coverable_statuses",
        ["failed", "blocked", "exception-requested"],
        errors,
        "readiness_policy",
    )
    check_exact_string_list(readiness_policy, "hard_blocker_reasons", HARD_BLOCKER_REASONS, errors, "readiness_policy")
    check_exact_string_list(readiness_policy, "canonical_phase18_criteria", CANONICAL_CRITERIA, errors, "readiness_policy")

    demotion_policy = require_dict(contract, "demotion_authorization_policy", "contract")
    if demotion_policy.get("default_authorization") != "blocked":
        errors.append("demotion_authorization_policy default_authorization must be blocked")
    if demotion_policy.get("explicit_input_required") is not True:
        errors.append("demotion_authorization_policy explicit_input_required must be true")
    if demotion_policy.get("evidence_status_never_implies_approval") is not True:
        errors.append("demotion_authorization_policy evidence_status_never_implies_approval must be true")
    if demotion_policy.get("requires_final_readiness_unblocked") is not True:
        errors.append("demotion_authorization_policy requires_final_readiness_unblocked must be true")
    check_exact_string_list(demotion_policy, "allowed_authorizations", ["blocked", "approved"], errors, "demotion_authorization_policy")

    phase27_policy = require_dict(contract, "phase27_handoff_policy", "contract")
    if phase27_policy.get("demotion_authorization") != "blocked":
        errors.append("phase27_handoff_policy demotion_authorization must be blocked")
    if phase27_policy.get("phase27_may_authorize_demotion") is not False:
        errors.append("phase27_handoff_policy phase27_may_authorize_demotion must be false")
    if phase27_policy.get("phase28_required_decision") != "explicit-maintainer-reference-demotion-decision":
        errors.append("phase27_handoff_policy phase28_required_decision must match Phase 27 handoff")

    demotion_schema = require_dict(contract, "demotion_decision_schema", "contract")
    exception_schema = require_dict(contract, "exception_schema", "contract")
    check_exact_string_list(
        demotion_schema,
        "required_fields",
        DEMOTION_DECISION_REQUIRED_FIELDS,
        errors,
        "demotion_decision_schema",
    )
    check_exact_string_list(exception_schema, "required_fields", EXCEPTION_REQUIRED_FIELDS, errors, "exception_schema")
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and generate the Phase 28 final readiness packet.")
    parser.add_argument("--contract-only", action="store_true", help="validate only the Phase 28 contract")
    parser.add_argument("--quick", action="store_true", help="write deterministic Phase 28 readiness packet artifacts")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 28 inputs and generated artifacts")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel, workflow, and just wiring")
    parser.add_argument("--phase26-upstream-rows", default="build/ci-evidence/phase26/upstream-result-row-table.json")
    parser.add_argument("--phase27-handoff", default="build/ci-evidence/phase27/phase28-handoff-manifest.json")
    parser.add_argument("--demotion-decision-input")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        check_contract(ROOT)
        if args.contract_only:
            print("Phase 28 final readiness packet contract passed")
            return 0
        if args.quick or args.security_only or args.wiring_only:
            raise VerificationError("Phase 28 mode is not implemented yet in this task")
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Phase 28 final readiness packet contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
