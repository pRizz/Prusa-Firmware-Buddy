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
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase28_final_readiness_packet_contract.json")
PHASE18_CONTRACT = Path(
    "tools/bazel/manifests/phase18_cutover_review_contract.json")
PHASE26_CONTRACT = Path(
    "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
)
PHASE27_CONTRACT = Path(
    "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
)
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase28")
DEFAULT_PHASE26_ROWS = Path(
    "build/ci-evidence/phase26/upstream-result-row-table.json")
DEFAULT_PHASE27_HANDOFF = Path(
    "build/ci-evidence/phase27/phase28-handoff-manifest.json")
PHASE26_QUICK_COMMAND = (
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py "
    "--quick --output-dir build/ci-evidence/phase26")
PHASE27_QUICK_COMMAND = (
    "python3 tools/bazel/phase27_retained_code_acceptance_decisions.py "
    "--quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
    "--output-dir build/ci-evidence/phase27")
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
    segments = [
        segment for segment in re.split(r"[^A-Za-z0-9]+", field_name)
        if segment
    ]
    field_pattern = r"[\s_-]*".join(re.escape(segment) for segment in segments)
    return re.compile(rf"\b{field_pattern}\s*[:=]", re.IGNORECASE)


FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-marker",
     re.compile(r"BEGIN (?:RSA |EC )?PRIVATE KEY", re.IGNORECASE)),
    ("firmware-payload-marker",
     re.compile(r"\b(?:raw )?firmware payload\b", re.IGNORECASE)),
    ("raw-crash-dump-marker", re.compile(r"\braw crash dump\b",
                                         re.IGNORECASE)),
    ("authorization-header",
     re.compile(r"\bauthorization\s*:\s*bearer\b", re.IGNORECASE)),
    ("bearer-token",
     re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE)),
    ("reference-demotion-approved",
     re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("demotion-allowed-overclaim",
     re.compile(r"\bdemotion allowed\b", re.IGNORECASE)),
    ("final-readiness-approved",
     re.compile(r"\bfinal readiness approved\b", re.IGNORECASE)),
    ("evidence-alone-acceptance",
     re.compile(r"\baccepted by evidence alone\b", re.IGNORECASE)),
    *((f"{field_name}-assignment", forbidden_assignment_pattern(field_name))
      for field_name in sorted(FORBIDDEN_ASSIGNMENT_FIELD_NAMES)),
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
        ("python3 tools/bazel/phase28_final_readiness_packet.py --quick "
         "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
         "--phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json "
         "--output-dir build/ci-evidence/phase28"),
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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_bool(row: dict[str, Any], field: str, row_name: str) -> bool:
    value = row.get(field)
    if not isinstance(value, bool):
        raise VerificationError(f"{row_name} {field} must be boolean")
    return value


def require_dict(row: dict[str, Any], field: str,
                 row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_list(row: dict[str, Any], field: str, row_name: str) -> list[Any]:
    value = row.get(field)
    if not isinstance(value, list):
        raise VerificationError(f"{row_name} {field} must be a list")
    return value


def require_string_list(row: dict[str, Any], field: str,
                        row_name: str) -> list[str]:
    value = require_list(row, field, row_name)
    if not all(isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_iso_utc(timestamp_text: str, row_name: str) -> None:
    if not timestamp_text.endswith("Z"):
        raise VerificationError(
            f"{row_name} decision_timestamp must be ISO UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(
            f"{row_name} decision_timestamp must be ISO UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(
            parsed):
        raise VerificationError(
            f"{row_name} decision_timestamp must be ISO UTC")


def require_repo_relative(path_value: str | Path, row_name: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} path must be repo-relative and cannot traverse: {relative_path.as_posix()}"
        )
    return relative_path


def require_repo_relative_under(path_value: str | Path,
                                expected_root: str | Path,
                                row_name: str) -> Path:
    relative_path = require_repo_relative(path_value, row_name)
    root_path = Path(expected_root)
    try:
        relative_path.relative_to(root_path)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} must be under {root_path.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


def contained_output_dir(root: Path, output_dir_arg: str | Path) -> Path:
    relative_path = require_repo_relative_under(output_dir_arg,
                                                DEFAULT_OUTPUT_DIR,
                                                "--output-dir")
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(
                f"--output-dir symlink escape risk: {relative_path.as_posix()}"
            )
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    full_path = (root / relative_path).resolve(strict=False)
    try:
        full_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_path}"
        ) from error
    return full_path


def reset_output_root(path: Path) -> None:
    if path.exists():
        if path.is_symlink():
            raise VerificationError(
                f"--output-dir symlink escape risk: {path.as_posix()}")
        if not path.is_dir():
            raise VerificationError(
                f"--output-dir exists and is not a directory: {path.as_posix()}"
            )
        shutil.rmtree(path)
    path.mkdir(parents=True)


def normalized_field_name(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


FORBIDDEN_NORMALIZED_FIELD_NAMES = {
    normalized_field_name(field_name)
    for field_name in FORBIDDEN_FIELD_NAMES
}


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


def reject_forbidden_json_fields(data: Any,
                                 source_name: str,
                                 maybe_path: str = "$") -> None:
    errors: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                nested_path = f"{path}.{key}"
                if key in FORBIDDEN_FIELD_NAMES or normalized_field_name(
                        key) in FORBIDDEN_NORMALIZED_FIELD_NAMES:
                    errors.append(
                        f"{source_name} contains forbidden field name {key} at {nested_path}"
                    )
                walk(nested, nested_path)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                walk(nested, f"{path}[{index}]")

    walk(data, maybe_path)
    if errors:
        raise VerificationError("\n".join(errors))


def check_exact_string_list(row: dict[str,
                                      Any], field: str, expected: list[str],
                            errors: list[str], row_name: str) -> None:
    try:
        actual = require_string_list(row, field, row_name)
    except VerificationError as error:
        errors.append(str(error))
        return
    if actual != expected:
        errors.append(
            f"{row_name} {field} does not match expected Phase 28 contract values"
        )


def phase18_upstream_requirements(root: Path) -> dict[str, dict[str, Any]]:
    contract = load_json(root, PHASE18_CONTRACT)
    raw_requirements = contract.get("upstream_result_requirements")
    if not isinstance(raw_requirements, list):
        raise VerificationError(
            "Phase 18 contract upstream_result_requirements must be a list")
    requirements: dict[str, dict[str, Any]] = {}
    for index, requirement in enumerate(raw_requirements):
        if not isinstance(requirement, dict):
            raise VerificationError(
                f"Phase 18 upstream_result_requirements[{index}] must be an object"
            )
        criterion_id = require_string(
            requirement, "criterion_id",
            f"Phase 18 upstream_result_requirements[{index}]")
        requirements[criterion_id] = requirement
    return requirements


def phase18_canonical_criteria(root: Path) -> list[str]:
    return list(phase18_upstream_requirements(root).keys())


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
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected!r}")
    check_exact_string_list(contract, "source_contracts", SOURCE_CONTRACTS,
                            errors, "contract")
    check_exact_string_list(contract, "generated_artifacts",
                            GENERATED_ARTIFACTS, errors, "contract")
    check_exact_string_list(
        contract, "top_level_verdicts",
        ["final_readiness_status", "reference_demotion_authorization"], errors,
        "contract")

    try:
        requirements = require_list(contract, "requirements", "contract")
        requirement_ids = [
            row.get("id") for row in requirements if isinstance(row, dict)
        ]
        if requirement_ids != REQUIRED_REQUIREMENT_IDS:
            errors.append(
                "contract requirements must be exactly READ-01, READ-02, READ-03"
            )
        required_inputs = require_dict(contract, "required_inputs", "contract")
        expected_inputs = {
            "phase26_upstream_rows": DEFAULT_PHASE26_ROWS.as_posix(),
            "phase27_handoff": DEFAULT_PHASE27_HANDOFF.as_posix(),
            "demotion_decision_input": "optional",
        }
        if required_inputs != expected_inputs:
            errors.append(
                "contract required_inputs must match Phase 28 plan inputs")

        readiness_policy = require_dict(contract, "readiness_policy",
                                        "contract")
        if readiness_policy.get("default_status") != "blocked":
            errors.append("readiness_policy default_status must be blocked")
        if readiness_policy.get(
                "hard_blockers_outrank_exceptions") is not True:
            errors.append(
                "readiness_policy hard_blockers_outrank_exceptions must be true"
            )
        check_exact_string_list(readiness_policy, "pass_statuses", ["passed"],
                                errors, "readiness_policy")
        check_exact_string_list(readiness_policy, "exception_statuses",
                                ["exception-approved"], errors,
                                "readiness_policy")
        check_exact_string_list(
            readiness_policy,
            "exception_coverable_statuses",
            ["failed", "blocked", "exception-requested"],
            errors,
            "readiness_policy",
        )
        check_exact_string_list(readiness_policy, "hard_blocker_reasons",
                                HARD_BLOCKER_REASONS, errors,
                                "readiness_policy")
        check_exact_string_list(
            readiness_policy,
            "canonical_phase18_criteria",
            phase18_canonical_criteria(root),
            errors,
            "readiness_policy",
        )

        demotion_policy = require_dict(contract,
                                       "demotion_authorization_policy",
                                       "contract")
        if demotion_policy.get("default_authorization") != "blocked":
            errors.append(
                "demotion_authorization_policy default_authorization must be blocked"
            )
        if demotion_policy.get("explicit_input_required") is not True:
            errors.append(
                "demotion_authorization_policy explicit_input_required must be true"
            )
        if demotion_policy.get(
                "evidence_status_never_implies_approval") is not True:
            errors.append(
                "demotion_authorization_policy evidence_status_never_implies_approval must be true"
            )
        if demotion_policy.get(
                "requires_final_readiness_unblocked") is not True:
            errors.append(
                "demotion_authorization_policy requires_final_readiness_unblocked must be true"
            )
        check_exact_string_list(demotion_policy, "allowed_authorizations",
                                ["blocked", "approved"], errors,
                                "demotion_authorization_policy")

        phase27_policy = require_dict(contract, "phase27_handoff_policy",
                                      "contract")
        if phase27_policy.get("demotion_authorization") != "blocked":
            errors.append(
                "phase27_handoff_policy demotion_authorization must be blocked"
            )
        if phase27_policy.get("phase27_may_authorize_demotion") is not False:
            errors.append(
                "phase27_handoff_policy phase27_may_authorize_demotion must be false"
            )
        if phase27_policy.get(
                "phase28_required_decision"
        ) != "explicit-maintainer-reference-demotion-decision":
            errors.append(
                "phase27_handoff_policy phase28_required_decision must match Phase 27 handoff"
            )

        demotion_schema = require_dict(contract, "demotion_decision_schema",
                                       "contract")
        exception_schema = require_dict(contract, "exception_schema",
                                        "contract")
        check_exact_string_list(
            demotion_schema,
            "required_fields",
            DEMOTION_DECISION_REQUIRED_FIELDS,
            errors,
            "demotion_decision_schema",
        )
        check_exact_string_list(exception_schema, "required_fields",
                                EXCEPTION_REQUIRED_FIELDS, errors,
                                "exception_schema")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract
