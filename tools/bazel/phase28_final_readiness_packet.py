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


ROOT = Path(__file__).resolve().parents[2]
PHASE = "28-final-readiness-packet-and-demotion-gate"
PHASE_LIFECYCLE_ID = "28-2026-06-25T03-31-49"
PHASE27 = "27-retained-code-and-maintainer-acceptance-decisions"
PHASE27_LIFECYCLE_ID = "27-2026-06-25T01-06-06"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase28_final_readiness_packet_contract.json")
PHASE18_CONTRACT = Path("tools/bazel/manifests/phase18_cutover_review_contract.json")
PHASE26_CONTRACT = Path("tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json")
PHASE27_CONTRACT = Path("tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase28")
DEFAULT_PHASE26_ROWS = Path("build/ci-evidence/phase26/upstream-result-row-table.json")
DEFAULT_PHASE27_HANDOFF = Path("build/ci-evidence/phase27/phase28-handoff-manifest.json")
PHASE26_QUICK_COMMAND = (
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py "
    "--quick --output-dir build/ci-evidence/phase26"
)
PHASE27_QUICK_COMMAND = (
    "python3 tools/bazel/phase27_retained_code_acceptance_decisions.py "
    "--quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
    "--output-dir build/ci-evidence/phase27"
)
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
DEMOTION_CRITERION = "final-reference-demotion-allowed"
HARD_BLOCKER_REASONS = [
    "redaction-failed",
    "overclaim-failed",
    "lifecycle-mismatch",
    "source-ref-failed",
    "unsafe-ref",
    "secret-tainted",
]
PASS_STATUSES = {"passed"}
EXCEPTION_STATUSES = {"exception-approved"}
EXCEPTION_COVERABLE_STATUSES = {"failed", "blocked", "exception-requested"}
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
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api-key",
    "api_key",
    "apikey",
    "bearer_token",
    "bbf_payload",
    "certificate_bytes",
    "certificate_pem",
    "certificate_private_material",
    "connect_token",
    "credential",
    "credential_value",
    "demotion_allowed",
    "dfu_payload",
    "firmware_payload",
    "password",
    "private_key",
    "prusalink_password",
    "raw_crash_dump",
    "raw_firmware_payload",
    "raw_key_bytes",
    "secret",
    "signing_key_value",
    "token",
    "wifi_password",
}
FORBIDDEN_ASSIGNMENT_FIELD_NAMES = FORBIDDEN_FIELD_NAMES | {
    "authorization_header",
}


def forbidden_assignment_pattern(field_name: str) -> re.Pattern[str]:
    segments = [segment for segment in re.split(r"[^A-Za-z0-9]+", field_name) if segment]
    field_pattern = r"[\s_-]*".join(re.escape(segment) for segment in segments)
    return re.compile(rf"\b{field_pattern}\s*[:=]", re.IGNORECASE)


FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-marker", re.compile(r"BEGIN (?:RSA |EC )?PRIVATE KEY", re.IGNORECASE)),
    ("firmware-payload-marker", re.compile(r"\b(?:raw )?firmware payload\b", re.IGNORECASE)),
    ("raw-crash-dump-marker", re.compile(r"\braw crash dump\b", re.IGNORECASE)),
    ("authorization-header", re.compile(r"\bauthorization\s*:\s*bearer\b", re.IGNORECASE)),
    ("bearer-token", re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE)),
    ("reference-demotion-approved", re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("demotion-allowed-overclaim", re.compile(r"\bdemotion allowed\b", re.IGNORECASE)),
    ("final-readiness-approved", re.compile(r"\bfinal readiness approved\b", re.IGNORECASE)),
    ("evidence-alone-acceptance", re.compile(r"\baccepted by evidence alone\b", re.IGNORECASE)),
    *(
        (f"{field_name}-assignment", forbidden_assignment_pattern(field_name))
        for field_name in sorted(FORBIDDEN_ASSIGNMENT_FIELD_NAMES)
    ),
)
WIRING_REQUIRED_TEXT = {
    Path("tools/bazel/BUILD.bazel"): [
        'name = "phase28_source_ref_manifests"',
        '"phase28_final_readiness_packet.py"',
        '"phase28_final_readiness_packet_test.py"',
        '"manifests/phase28_final_readiness_packet_contract.json"',
        'name = "phase28_verify"',
        'name = "phase28_verify_tests"',
    ],
    Path("BUILD.bazel"): [
        'name = "phase28_final_readiness_packet_docs"',
        'name = "phase28_verify"',
        'actual = "//tools/bazel:phase28_verify"',
        'name = "phase28_verify_tests"',
        'actual = "//tools/bazel:phase28_verify_tests"',
    ],
    Path("tools/bazel/rust_workflow.sh"): [
        "phase28_verify)",
        "python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only",
        PHASE26_QUICK_COMMAND,
        PHASE27_QUICK_COMMAND,
        (
            "python3 tools/bazel/phase28_final_readiness_packet.py --quick "
            "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
            "--phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json "
            "--output-dir build/ci-evidence/phase28"
        ),
        "phase28_verify_tests)",
        "python3 tools/bazel/phase28_final_readiness_packet_test.py",
    ],
    Path("justfile"): [
        "phase28-verify:",
        "bazel run //tools/bazel:phase28_verify_tests",
        "bazel run //tools/bazel:phase28_verify",
    ],
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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_bool(row: dict[str, Any], field: str, row_name: str) -> bool:
    value = row.get(field)
    if not isinstance(value, bool):
        raise VerificationError(f"{row_name} {field} must be boolean")
    return value


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


def require_iso_utc(timestamp_text: str, row_name: str) -> None:
    if not timestamp_text.endswith("Z"):
        raise VerificationError(f"{row_name} decision_timestamp must be ISO UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(f"{row_name} decision_timestamp must be ISO UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise VerificationError(f"{row_name} decision_timestamp must be ISO UTC")


def require_repo_relative(path_value: str | Path, row_name: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(f"{row_name} path must be repo-relative and cannot traverse: {relative_path.as_posix()}")
    return relative_path


def require_repo_relative_under(path_value: str | Path, expected_root: str | Path, row_name: str) -> Path:
    relative_path = require_repo_relative(path_value, row_name)
    root_path = Path(expected_root)
    try:
        relative_path.relative_to(root_path)
    except ValueError as error:
        raise VerificationError(f"{row_name} must be under {root_path.as_posix()}: {relative_path.as_posix()}") from error
    return relative_path


def contained_output_dir(root: Path, output_dir_arg: str | Path) -> Path:
    relative_path = require_repo_relative_under(output_dir_arg, DEFAULT_OUTPUT_DIR, "--output-dir")
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(f"--output-dir symlink escape risk: {relative_path.as_posix()}")
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    full_path = (root / relative_path).resolve(strict=False)
    try:
        full_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_path}") from error
    return full_path


def reset_output_root(path: Path) -> None:
    if path.exists():
        if path.is_symlink():
            raise VerificationError(f"--output-dir symlink escape risk: {path.as_posix()}")
        shutil.rmtree(path)
    path.mkdir(parents=True)


def normalized_field_name(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


FORBIDDEN_NORMALIZED_FIELD_NAMES = {normalized_field_name(field_name) for field_name in FORBIDDEN_FIELD_NAMES}


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(f"{path.as_posix()} contains forbidden marker {label}: {match.group(0)}")
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_json_fields(data: Any, source_name: str, maybe_path: str = "$") -> None:
    errors: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                nested_path = f"{path}.{key}"
                if key in FORBIDDEN_FIELD_NAMES or normalized_field_name(key) in FORBIDDEN_NORMALIZED_FIELD_NAMES:
                    errors.append(f"{source_name} contains forbidden field name {key} at {nested_path}")
                walk(nested, nested_path)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                walk(nested, f"{path}[{index}]")

    walk(data, maybe_path)
    if errors:
        raise VerificationError("\n".join(errors))


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

    try:
        requirements = require_list(contract, "requirements", "contract")
        requirement_ids = [row.get("id") for row in requirements if isinstance(row, dict)]
        if requirement_ids != REQUIRED_REQUIREMENT_IDS:
            errors.append("contract requirements must be exactly READ-01, READ-02, READ-03")
        required_inputs = require_dict(contract, "required_inputs", "contract")
        expected_inputs = {
            "phase26_upstream_rows": DEFAULT_PHASE26_ROWS.as_posix(),
            "phase27_handoff": DEFAULT_PHASE27_HANDOFF.as_posix(),
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
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def phase18_upstream_requirements(root: Path) -> dict[str, dict[str, Any]]:
    contract = load_json(root, PHASE18_CONTRACT)
    raw_requirements = contract.get("upstream_result_requirements")
    if not isinstance(raw_requirements, list):
        raise VerificationError("Phase 18 contract upstream_result_requirements must be a list")
    requirements: dict[str, dict[str, Any]] = {}
    for index, requirement in enumerate(raw_requirements):
        if not isinstance(requirement, dict):
            raise VerificationError(f"Phase 18 upstream_result_requirements[{index}] must be an object")
        criterion_id = require_string(requirement, "criterion_id", f"Phase 18 upstream_result_requirements[{index}]")
        requirements[criterion_id] = requirement
    return requirements


def input_path_under(path_value: str, expected_root: Path, row_name: str) -> Path:
    return require_repo_relative_under(path_value, expected_root, row_name)


def load_json_input(root: Path, path: Path, row_name: str) -> dict[str, Any]:
    raw_text = read_text(root, path)
    reject_forbidden_text(path, raw_text)
    data = load_json(root, path)
    reject_forbidden_json_fields(data, path.as_posix())
    return data


def load_phase26_rows(root: Path, path_value: str) -> tuple[Path, list[dict[str, Any]]]:
    path = input_path_under(path_value, Path("build/ci-evidence/phase26"), "--phase26-upstream-rows")
    if not (root / path).exists():
        raise VerificationError(
            f"missing Phase 26 upstream rows: {path.as_posix()}\nRun: {PHASE26_QUICK_COMMAND}"
        )
    data = load_json_input(root, path, "--phase26-upstream-rows")
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise VerificationError("--phase26-upstream-rows rows must be a list")
    requirements = phase18_upstream_requirements(root)
    normalized_rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"phase26 rows[{index}] must be an object")
        row_name = f"phase26 {row.get('criterion_id', index)}"
        criterion_id = require_string(row, "criterion_id", row_name)
        if criterion_id not in CANONICAL_CRITERIA:
            raise VerificationError(f"{row_name} criterion_id is not a canonical Phase 18 criterion")
        if criterion_id in seen:
            raise VerificationError(f"duplicate Phase 26 criterion row: {criterion_id}")
        seen.add(criterion_id)
        requirement = requirements.get(criterion_id)
        if requirement is None:
            raise VerificationError(f"{row_name} does not resolve in Phase 18 upstream requirements")
        if row.get("source_lifecycle_id") != requirement.get("source_lifecycle_id"):
            raise VerificationError(f"{row_name} source_lifecycle_id must match Phase 18 upstream requirement")
        if row.get("source_lifecycle_status") != "current":
            raise VerificationError(f"{row_name} source_lifecycle_status must be current")
        if row.get("source_ref_status") != "passed":
            raise VerificationError(f"{row_name} source_ref_status must be passed")
        normalized_rows.append(row)
    missing = sorted(set(CANONICAL_CRITERIA) - seen)
    if missing:
        raise VerificationError("Phase 26 upstream rows missing criteria: " + ", ".join(missing))
    return path, normalized_rows


def load_phase27_supporting(root: Path, handoff_path: Path, filename: str) -> dict[str, Any]:
    path = handoff_path.parent / filename
    if not (root / path).exists():
        raise VerificationError(f"missing Phase 27 supporting artifact: {path.as_posix()}\nRun: {PHASE27_QUICK_COMMAND}")
    return load_json_input(root, path, f"Phase 27 {filename}")


def load_phase27_bundle(root: Path, path_value: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    handoff_path = input_path_under(path_value, Path("build/ci-evidence/phase27"), "--phase27-handoff")
    if not (root / handoff_path).exists():
        raise VerificationError(f"missing Phase 27 handoff: {handoff_path.as_posix()}\nRun: {PHASE27_QUICK_COMMAND}")
    handoff = load_json_input(root, handoff_path, "--phase27-handoff")
    if handoff.get("phase") != PHASE27:
        raise VerificationError(f"--phase27-handoff phase must be {PHASE27}")
    if handoff.get("phase_lifecycle_id") != PHASE27_LIFECYCLE_ID:
        raise VerificationError(f"--phase27-handoff phase_lifecycle_id must be {PHASE27_LIFECYCLE_ID}")
    if handoff.get("demotion_authorization") != "blocked":
        raise VerificationError("--phase27-handoff demotion_authorization must remain blocked")
    if handoff.get("phase27_may_authorize_demotion") is not False:
        raise VerificationError("--phase27-handoff phase27_may_authorize_demotion must be false")
    if handoff.get("phase28_required_decision") != "explicit-maintainer-reference-demotion-decision":
        raise VerificationError("--phase27-handoff phase28_required_decision is invalid")
    bundle = {
        "final_readiness": load_phase27_supporting(root, handoff_path, "final-readiness-decision-summary.json"),
        "residual_risk": load_phase27_supporting(root, handoff_path, "residual-risk-register.json"),
        "exceptions": load_phase27_supporting(root, handoff_path, "exception-decision-register.json"),
        "artifact_refs": load_phase27_supporting(root, handoff_path, "artifact-reference-summary.json"),
        "decision_rows": load_phase27_supporting(root, handoff_path, "decision-row-table.json"),
    }
    return handoff_path, handoff, bundle


def rows_by_field(data: dict[str, Any], field: str, source_name: str) -> dict[str, dict[str, Any]]:
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{source_name} rows must be a list")
    mapped: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{source_name} rows[{index}] must be an object")
        row_id = row.get(field)
        if not isinstance(row_id, str) or not row_id:
            raise VerificationError(f"{source_name} rows[{index}] {field} must be a non-empty string")
        if row_id in mapped:
            raise VerificationError(f"{source_name} duplicate {field}: {row_id}")
        mapped[row_id] = row
    return mapped


def detect_hard_failure_reasons(phase26_row: dict[str, Any], phase27_row: dict[str, Any]) -> list[str]:
    reasons = set()
    status_values = {str(phase26_row.get("status", "")), str(phase27_row.get("status", ""))}
    if phase26_row.get("redaction_status") != "passed" or phase27_row.get("redaction_summary") == "redaction_status=failed":
        reasons.add("redaction-failed")
    if "rejected-redaction" in status_values:
        reasons.add("redaction-failed")
    if "rejected-overclaim" in status_values:
        reasons.add("overclaim-failed")
    if phase26_row.get("source_lifecycle_status") != "current":
        reasons.add("lifecycle-mismatch")
    if phase26_row.get("source_ref_status") != "passed":
        reasons.add("source-ref-failed")
    for reason in phase27_row.get("hard_failure_reasons", []):
        if isinstance(reason, str) and reason:
            reasons.add(reason)
    failure_text = f"{phase26_row.get('failure_reason', '')} {phase27_row.get('rationale', '')}".lower()
    if "unsafe-ref" in failure_text or "unsafe ref" in failure_text:
        reasons.add("unsafe-ref")
    if "secret-tainted" in failure_text or "secret tainted" in failure_text:
        reasons.add("secret-tainted")
    return [reason for reason in HARD_BLOCKER_REASONS if reason in reasons]


def validate_exception_metadata(exception: Any, row_name: str) -> dict[str, Any]:
    if not isinstance(exception, dict):
        raise VerificationError(f"{row_name} exception must be an object")
    for field in EXCEPTION_REQUIRED_FIELDS:
        if field not in exception:
            raise VerificationError(f"{row_name} exception missing required field: {field}")
        if field == "evidence_refs":
            refs = exception[field]
            if not isinstance(refs, list) or not all(isinstance(ref, str) and ref for ref in refs) or not refs:
                raise VerificationError(f"{row_name} exception evidence_refs must not be empty")
        elif not isinstance(exception[field], str) or not exception[field]:
            raise VerificationError(f"{row_name} exception {field} must be a non-empty string")
    return exception


def exception_covers_row(phase26_row: dict[str, Any], phase27_row: dict[str, Any], hard_failure_reasons: list[str]) -> tuple[bool, list[dict[str, Any]]]:
    if hard_failure_reasons:
        return False, []
    status = str(phase26_row.get("status", ""))
    phase27_status = str(phase27_row.get("status", ""))
    exception_state = str(phase27_row.get("exception_state", ""))
    exception = phase27_row.get("exception")
    if status not in EXCEPTION_COVERABLE_STATUSES and phase27_status not in EXCEPTION_STATUSES:
        return False, []
    if phase27_status not in EXCEPTION_STATUSES and exception_state not in {"approved-exception", "exception-approved"}:
        return False, []
    exception_row = validate_exception_metadata(exception, str(phase27_row.get("criterion_id", "criterion")))
    return True, [exception_row]


def matching_rows(rows: list[dict[str, Any]], row_id: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("row_id") == row_id or row.get("criterion_id") == row_id]


def normalize_readiness_criteria(
    phase26_rows: list[dict[str, Any]],
    phase27_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    phase26_by_id = {str(row["criterion_id"]): row for row in phase26_rows}
    phase27_by_id = rows_by_field(phase27_bundle["final_readiness"], "criterion_id", "Phase 27 final-readiness-decision-summary")
    residual_rows = phase27_bundle["residual_risk"].get("rows", [])
    exception_rows = phase27_bundle["exceptions"].get("rows", [])
    if not isinstance(residual_rows, list) or not isinstance(exception_rows, list):
        raise VerificationError("Phase 27 residual risk and exception artifacts must contain rows lists")
    normalized: list[dict[str, Any]] = []
    for criterion_id in CANONICAL_CRITERIA:
        phase26_row = phase26_by_id[criterion_id]
        phase27_row = phase27_by_id.get(criterion_id)
        if phase27_row is None:
            raise VerificationError(f"Phase 27 final readiness summary missing criterion: {criterion_id}")
        hard_failure_reasons = detect_hard_failure_reasons(phase26_row, phase27_row)
        covered_by_exception, inline_exceptions = exception_covers_row(phase26_row, phase27_row, hard_failure_reasons)
        phase26_status = str(phase26_row.get("status", "blocked"))
        phase27_status = str(phase27_row.get("status", "blocked"))
        if criterion_id == DEMOTION_CRITERION:
            readiness_effect = "blocked-pending-explicit-demotion-decision"
        elif hard_failure_reasons:
            readiness_effect = "blocked-hard-failure"
        elif covered_by_exception:
            readiness_effect = "exception-covered"
        elif phase26_status in PASS_STATUSES and phase27_status in PASS_STATUSES:
            readiness_effect = "passed"
        else:
            readiness_effect = "blocked"
        residual_refs = [
            f"build/ci-evidence/phase27/residual-risk-register.json#{row.get('row_id')}"
            for row in matching_rows(residual_rows, criterion_id)
            if isinstance(row, dict)
        ]
        exception_refs = [
            f"build/ci-evidence/phase27/exception-decision-register.json#{row.get('row_id', row.get('criterion_id', criterion_id))}"
            for row in matching_rows(exception_rows, criterion_id)
            if isinstance(row, dict)
        ]
        normalized.append(
            {
                "criterion_id": criterion_id,
                "requirement_ids": list(phase26_row.get("requirement_ids", [])),
                "evidence_family": phase26_row.get("evidence_family", ""),
                "phase26_status": phase26_status,
                "phase27_status": phase27_status,
                "readiness_effect": readiness_effect,
                "hard_failure_reasons": hard_failure_reasons,
                "exception_state": "covered" if covered_by_exception else str(phase27_row.get("exception_state", "none")),
                "exception_refs": exception_refs,
                "exception_metadata": inline_exceptions,
                "residual_risk": str(phase27_row.get("residual_risk", "Pending final readiness review.")),
                "residual_risk_refs": residual_refs,
                "source_refs": list(phase26_row.get("evidence_refs", [])),
                "evidence_refs": list(phase27_row.get("evidence_refs", phase26_row.get("evidence_refs", []))),
                "artifact_refs": sorted(
                    set(
                        [
                            *[str(ref) for ref in phase26_row.get("artifact_refs", []) if isinstance(ref, str)],
                            *[str(ref) for ref in phase27_row.get("artifact_refs", []) if isinstance(ref, str)],
                        ]
                    )
                ),
                "rationale": str(phase27_row.get("rationale", phase26_row.get("failure_reason", ""))),
                "demotion_gate_effect": "requires-explicit-phase28-decision"
                if criterion_id == DEMOTION_CRITERION
                else "readiness-input",
            }
        )
    return normalized


def final_readiness_status(criteria: list[dict[str, Any]]) -> str:
    for row in criteria:
        if row["criterion_id"] == DEMOTION_CRITERION:
            continue
        if row["readiness_effect"] not in {"passed", "exception-covered"}:
            return "blocked"
    return "unblocked"


def load_demotion_decision_input(
    root: Path,
    maybe_path: str | None,
    maybe_final_readiness_status: str | None = None,
) -> dict[str, Any] | None:
    if not maybe_path:
        return None
    path = require_repo_relative(maybe_path, "--demotion-decision-input")
    raw_text = read_text(root, path)
    reject_forbidden_text(path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError("--demotion-decision-input must contain a top-level object")
    reject_forbidden_json_fields(data, path.as_posix())
    for field in DEMOTION_DECISION_REQUIRED_FIELDS:
        if field not in data:
            raise VerificationError(f"--demotion-decision-input missing required field: {field}")
    if data["phase"] != PHASE:
        raise VerificationError(f"--demotion-decision-input phase must be {PHASE}")
    if data["phase_lifecycle_id"] != PHASE_LIFECYCLE_ID:
        raise VerificationError(f"--demotion-decision-input phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
    authorization = data["demotion_authorization"]
    if authorization not in {"blocked", "approved"}:
        raise VerificationError("--demotion-decision-input demotion_authorization must be blocked or approved")
    for field in ["approver", "approver_role", "rationale", "scope"]:
        if not isinstance(data[field], str) or not data[field]:
            raise VerificationError(f"--demotion-decision-input {field} must be a non-empty string")
    require_iso_utc(require_string(data, "decision_timestamp", "--demotion-decision-input"), "--demotion-decision-input")
    evidence_refs = data["evidence_refs"]
    if not isinstance(evidence_refs, list) or not all(isinstance(ref, str) and ref for ref in evidence_refs):
        raise VerificationError("--demotion-decision-input evidence_refs must be a list of non-empty strings")
    if authorization == "approved":
        if not evidence_refs:
            raise VerificationError("--demotion-decision-input approved authorization requires evidence_refs")
        if maybe_final_readiness_status != "unblocked":
            raise VerificationError("approved reference demotion requires final_readiness_status unblocked")
    return data


def demotion_authorization_record(
    decision_input: dict[str, Any] | None,
    readiness_status: str,
) -> dict[str, Any]:
    if decision_input is None:
        return {
            "reference_demotion_authorization": "blocked",
            "real_maintainer_demotion_approval_supplied": False,
            "authorization_source": "no-phase28-demotion-decision-input",
            "rationale": "Reference demotion requires an explicit Phase 28 maintainer decision.",
            "evidence_refs": [],
        }
    authorization = str(decision_input["demotion_authorization"])
    if authorization == "approved" and readiness_status != "unblocked":
        raise VerificationError("approved reference demotion requires final_readiness_status unblocked")
    return {
        "reference_demotion_authorization": authorization,
        "real_maintainer_demotion_approval_supplied": authorization == "approved",
        "authorization_source": "phase28-demotion-decision-input",
        "approver": decision_input["approver"],
        "approver_role": decision_input["approver_role"],
        "decision_timestamp": decision_input["decision_timestamp"],
        "scope": decision_input["scope"],
        "rationale": decision_input["rationale"],
        "evidence_refs": decision_input["evidence_refs"],
    }


def build_blocker_rows(criteria: list[dict[str, Any]], readiness_status: str, demotion_record: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = []
    for row in criteria:
        if row["readiness_effect"] in {"passed", "exception-covered"}:
            continue
        blockers.append(
            {
                "criterion_id": row["criterion_id"],
                "readiness_effect": row["readiness_effect"],
                "phase26_status": row["phase26_status"],
                "phase27_status": row["phase27_status"],
                "hard_failure_reasons": row["hard_failure_reasons"],
                "rationale": row["rationale"],
            }
        )
    if demotion_record["reference_demotion_authorization"] != "approved":
        blockers.append(
            {
                "criterion_id": DEMOTION_CRITERION,
                "readiness_effect": "reference-demotion-authorization-blocked",
                "phase26_status": "not-applicable",
                "phase27_status": "blocked",
                "hard_failure_reasons": [],
                "rationale": demotion_record["rationale"],
            }
        )
    if readiness_status == "blocked" and not blockers:
        raise VerificationError("blocked final readiness must include at least one blocker")
    return blockers


def demotion_decision_input_template() -> dict[str, Any]:
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "demotion_authorization": "blocked",
        "approver": "maintainer-name",
        "approver_role": "release-maintainer",
        "decision_timestamp": "2026-06-25T00:00:00Z",
        "rationale": "Reference demotion remains blocked until final readiness is unblocked and maintainer approval is supplied.",
        "scope": "supported-printer-release-surface",
        "evidence_refs": [],
    }


def artifact_reference_summary(output_dir_relative: Path, phase26_path: Path, phase27_path: Path, phase27_bundle: dict[str, Any]) -> dict[str, Any]:
    refs = [
        {
            "path": (output_dir_relative / artifact).as_posix(),
            "purpose": "phase28-final-readiness-packet",
        }
        for artifact in GENERATED_ARTIFACTS
    ]
    phase27_refs = phase27_bundle["artifact_refs"].get("artifact_refs", [])
    if not isinstance(phase27_refs, list):
        phase27_refs = []
    return {
        "phase26_upstream_rows": phase26_path.as_posix(),
        "phase27_handoff": phase27_path.as_posix(),
        "source_contract_refs": [{"path": path} for path in SOURCE_CONTRACTS],
        "phase27_artifact_refs": phase27_refs,
        "generated_artifact_refs": refs,
    }


def redacted_report_text(packet: dict[str, Any]) -> str:
    lines = [
        "# Phase 28 Final Readiness Packet",
        "",
        "Review material only; machine-readable packet rows and explicit maintainer input determine gate status.",
        "",
        f"phase: {packet['phase']}",
        f"phase_lifecycle_id: {packet['phase_lifecycle_id']}",
        f"final_readiness_status: {packet['final_readiness_status']}",
        f"reference_demotion_authorization: {packet['reference_demotion_authorization']}",
        f"real_maintainer_demotion_approval_supplied: {str(packet['real_maintainer_demotion_approval_supplied']).lower()}",
        "",
        "## Criteria",
    ]
    for row in packet["criteria"]:
        lines.append(f"- {row['criterion_id']} -> {row['readiness_effect']} (phase26={row['phase26_status']}, phase27={row['phase27_status']})")
        for reason in row["hard_failure_reasons"]:
            lines.append(f"  - hard blocker: {reason}")
    return "\n".join(lines) + "\n"


def generated_artifacts_to_scan(output_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for artifact in GENERATED_ARTIFACTS:
        path = output_dir / artifact
        if path.exists():
            paths.append(path)
    return paths


def validate_generated_outputs(root: Path, output_dir: Path) -> None:
    packet_path = output_dir / "final-readiness-packet.json"
    if not packet_path.exists():
        return
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(packet, dict):
        raise VerificationError("final-readiness-packet.json must contain an object")
    for field in [
        "final_readiness_status",
        "reference_demotion_authorization",
        "criteria",
        "requirements",
        "real_maintainer_demotion_approval_supplied",
    ]:
        if field not in packet:
            raise VerificationError(f"final-readiness-packet.json missing top-level field: {field}")
    if packet["reference_demotion_authorization"] == "approved":
        if packet["final_readiness_status"] != "unblocked":
            raise VerificationError("generated packet cannot approve reference demotion while final readiness is blocked")
        if packet["real_maintainer_demotion_approval_supplied"] is not True:
            raise VerificationError("generated packet approved authorization requires maintainer approval flag")
    criteria = packet.get("criteria")
    if not isinstance(criteria, list) or {row.get("criterion_id") for row in criteria if isinstance(row, dict)} != set(CANONICAL_CRITERIA):
        raise VerificationError("final-readiness-packet.json criteria must cover all canonical Phase 18 criteria")
    record_path = output_dir / "reference-demotion-authorization-record.json"
    if record_path.exists():
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if isinstance(record, dict) and record.get("reference_demotion_authorization") == "approved":
            if packet.get("reference_demotion_authorization") != "approved":
                raise VerificationError("authorization record and packet disagree")
            if record.get("real_maintainer_demotion_approval_supplied") is not True:
                raise VerificationError("authorization record approved status requires maintainer approval flag")
    for path in generated_artifacts_to_scan(output_dir):
        relative_path = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        reject_forbidden_text(relative_path, text)
        if path.suffix == ".json":
            try:
                reject_forbidden_json_fields(json.loads(text), relative_path.as_posix())
            except json.JSONDecodeError as error:
                raise VerificationError(f"{relative_path.as_posix()} is not valid JSON: {error}") from error


def run_security_scan(
    root: Path,
    maybe_demotion_decision_input: str | None = None,
    output_dir: Path | None = None,
) -> None:
    errors: list[str] = []
    paths_to_scan = [CONTRACT_MANIFEST, PHASE18_CONTRACT, PHASE26_CONTRACT, PHASE27_CONTRACT]
    for path in paths_to_scan:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_json_fields(load_json(root, path), path.as_posix())
        except VerificationError as error:
            errors.append(str(error))
    if maybe_demotion_decision_input:
        try:
            load_demotion_decision_input(root, maybe_demotion_decision_input, maybe_final_readiness_status="blocked")
        except VerificationError as error:
            errors.append(str(error))
    scan_dir = output_dir or (root / DEFAULT_OUTPUT_DIR)
    if scan_dir.exists():
        try:
            validate_generated_outputs(root, scan_dir)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def copy_snapshot(root: Path, output_dir: Path, source: Path, target: str) -> None:
    source_path = root / source
    if not source_path.exists():
        raise VerificationError(f"missing snapshot source: {source.as_posix()}")
    target_path = output_dir / target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)


def write_phase28_outputs(
    root: Path,
    contract: dict[str, Any],
    phase26_path: Path,
    phase26_rows: list[dict[str, Any]],
    phase27_path: Path,
    phase27_handoff: dict[str, Any],
    phase27_bundle: dict[str, Any],
    demotion_decision_input: dict[str, Any] | None,
    output_dir_arg: str,
) -> dict[str, Any]:
    output_dir = contained_output_dir(root, output_dir_arg)
    criteria = normalize_readiness_criteria(phase26_rows, phase27_bundle)
    readiness_status = final_readiness_status(criteria)
    if demotion_decision_input is not None and demotion_decision_input["demotion_authorization"] == "approved" and readiness_status != "unblocked":
        raise VerificationError("approved reference demotion requires final_readiness_status unblocked")
    demotion_record = demotion_authorization_record(demotion_decision_input, readiness_status)
    blockers = build_blocker_rows(criteria, readiness_status, demotion_record)
    output_dir_relative = output_dir.relative_to(root)
    generated_at_utc = utc_now()
    packet = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": contract["artifact_name"],
        "generated_at_utc": generated_at_utc,
        "final_readiness_status": readiness_status,
        "reference_demotion_authorization": demotion_record["reference_demotion_authorization"],
        "real_maintainer_demotion_approval_supplied": demotion_record["real_maintainer_demotion_approval_supplied"],
        "requirements": contract["requirements"],
        "criteria": criteria,
        "source_inputs": {
            "phase26_upstream_rows": phase26_path.as_posix(),
            "phase27_handoff": phase27_path.as_posix(),
        },
        "phase27_handoff": phase27_handoff,
    }
    run_manifest = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": contract["artifact_name"],
        "generated_at_utc": generated_at_utc,
        "output_root": output_dir_relative.as_posix(),
        "phase26_upstream_rows": phase26_path.as_posix(),
        "phase27_handoff": phase27_path.as_posix(),
        "demotion_decision_input_supplied": demotion_decision_input is not None,
        "final_readiness_status": readiness_status,
        "reference_demotion_authorization": demotion_record["reference_demotion_authorization"],
        "real_maintainer_demotion_approval_supplied": demotion_record["real_maintainer_demotion_approval_supplied"],
        "generated_artifacts": [(output_dir_relative / artifact).as_posix() for artifact in GENERATED_ARTIFACTS],
    }
    exception_rows = [
        {
            "criterion_id": row["criterion_id"],
            "exception_state": row["exception_state"],
            "exception_refs": row["exception_refs"],
            "exception_metadata": row["exception_metadata"],
            "residual_risk": row["residual_risk"],
            "residual_risk_refs": row["residual_risk_refs"],
        }
        for row in criteria
        if row["exception_state"] != "none" or row["residual_risk_refs"]
    ]
    reset_output_root(output_dir)
    write_json(output_dir / "final-readiness-run-manifest.json", run_manifest)
    write_json(output_dir / "final-readiness-packet.json", packet)
    write_json(output_dir / "normalized-readiness-criteria-table.json", {"rows": criteria})
    write_json(
        output_dir / "blocker-summary.json",
        {
            "final_readiness_status": readiness_status,
            "reference_demotion_authorization": demotion_record["reference_demotion_authorization"],
            "blockers": blockers,
        },
    )
    write_json(output_dir / "exception-residual-risk-summary.json", {"rows": exception_rows})
    write_json(output_dir / "reference-demotion-authorization-record.json", demotion_record)
    write_json(output_dir / "demotion-decision-input-template.json", demotion_decision_input_template())
    (output_dir / "redacted-readiness-report.md").write_text(redacted_report_text(packet), encoding="utf-8")
    write_json(output_dir / "artifact-reference-summary.json", artifact_reference_summary(output_dir_relative, phase26_path, phase27_path, phase27_bundle))
    copy_snapshot(root, output_dir, PHASE18_CONTRACT, "contract-snapshots/phase18_cutover_review_contract.json")
    copy_snapshot(root, output_dir, PHASE26_CONTRACT, "contract-snapshots/phase26_release_signing_upstream_evidence_contract.json")
    copy_snapshot(root, output_dir, PHASE27_CONTRACT, "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json")
    copy_snapshot(root, output_dir, phase26_path, "contract-snapshots/phase26-upstream-result-row-table.json")
    copy_snapshot(root, output_dir, phase27_path, "contract-snapshots/phase27-phase28-handoff-manifest.json")
    run_security_scan(root, output_dir=output_dir)
    return run_manifest


def shell_case_commands(text: str, case_name: str) -> list[str]:
    case_index = text.find(f"  {case_name})")
    if case_index == -1:
        return []
    commands: list[str] = []
    for line in text[case_index:].splitlines()[1:]:
        if line.startswith("  ") and not line.startswith("    ") and line.strip().endswith(")"):
            break
        stripped = line.strip()
        if stripped.startswith("python3 "):
            commands.append(stripped)
    return commands


def just_recipe_commands(text: str, recipe_name: str) -> list[str]:
    recipe_index = text.find(f"{recipe_name}:")
    if recipe_index == -1:
        return []
    next_recipe = text.find("\n\n", recipe_index)
    body = text[recipe_index:] if next_recipe == -1 else text[recipe_index:next_recipe]
    return [line.strip() for line in body.splitlines()[1:] if line.strip()]


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    for path, required_values in WIRING_REQUIRED_TEXT.items():
        try:
            text = read_text(root, path)
        except VerificationError as error:
            errors.append(str(error))
            continue
        for required_text in required_values:
            if required_text not in text:
                errors.append(f"{path.as_posix()} missing required wiring text: {required_text}")
    try:
        workflow = read_text(root, "tools/bazel/rust_workflow.sh")
        commands = shell_case_commands(workflow, "phase28_verify")
        expected = [
            "python3 tools/bazel/phase28_final_readiness_packet.py --wiring-only",
            PHASE26_QUICK_COMMAND,
            PHASE27_QUICK_COMMAND,
            (
                "python3 tools/bazel/phase28_final_readiness_packet.py --quick "
                "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
                "--phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json "
                "--output-dir build/ci-evidence/phase28"
            ),
        ]
        if commands != expected:
            errors.append("tools/bazel/rust_workflow.sh phase28_verify command order does not match Phase 28 plan")
        if shell_case_commands(workflow, "phase28_verify_tests") != ["python3 tools/bazel/phase28_final_readiness_packet_test.py"]:
            errors.append("tools/bazel/rust_workflow.sh phase28_verify_tests command is invalid")
    except VerificationError as error:
        errors.append(str(error))
    try:
        just_text = read_text(root, "justfile")
        commands = just_recipe_commands(just_text, "phase28-verify")
        expected = [
            "bazel run //tools/bazel:phase28_verify_tests",
            "bazel run //tools/bazel:phase28_verify",
        ]
        if commands != expected:
            errors.append("justfile phase28-verify must run tests before verifier")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and generate the Phase 28 final readiness packet.")
    parser.add_argument("--contract-only", action="store_true", help="validate only the Phase 28 contract")
    parser.add_argument("--quick", action="store_true", help="write deterministic Phase 28 readiness packet artifacts")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 28 inputs and generated artifacts")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel, workflow, and just wiring")
    parser.add_argument("--phase26-upstream-rows", default=DEFAULT_PHASE26_ROWS.as_posix())
    parser.add_argument("--phase27-handoff", default=DEFAULT_PHASE27_HANDOFF.as_posix())
    parser.add_argument("--demotion-decision-input")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        contract = check_contract(ROOT)
        if args.security_only:
            output_dir = contained_output_dir(ROOT, args.output_dir)
            run_security_scan(ROOT, args.demotion_decision_input, output_dir)
            print("Phase 28 security scan passed")
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            print("Phase 28 wiring passed")
            return 0
        if args.quick:
            phase26_path, phase26_rows = load_phase26_rows(ROOT, args.phase26_upstream_rows)
            phase27_path, handoff, phase27_bundle = load_phase27_bundle(ROOT, args.phase27_handoff)
            preliminary_criteria = normalize_readiness_criteria(phase26_rows, phase27_bundle)
            preliminary_status = final_readiness_status(preliminary_criteria)
            decision_input = load_demotion_decision_input(ROOT, args.demotion_decision_input, preliminary_status)
            run_manifest = write_phase28_outputs(
                ROOT,
                contract,
                phase26_path,
                phase26_rows,
                phase27_path,
                handoff,
                phase27_bundle,
                decision_input,
                args.output_dir,
            )
            print(
                "Phase 28 final readiness packet quick validation passed; "
                f"final_readiness_status={run_manifest['final_readiness_status']} "
                f"reference_demotion_authorization={run_manifest['reference_demotion_authorization']}"
            )
            return 0
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Phase 28 final readiness packet contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
