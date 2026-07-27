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
PHASE = "18-retained-code-acceptance-and-cutover-review"
PHASE_LIFECYCLE_ID = "18-2026-06-20T14-27-15"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase18_cutover_review_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase18")
REQUIRED_REQUIREMENT_IDS = {"REV-01", "REV-02", "REV-03"}
RETAINED_PACKET_STATUS_VOCABULARY = [
    "pending-evidence",
    "pending-maintainer-review",
    "accepted",
    "rejected",
    "blocked",
    "deferred-approved-exception",
    "rejected-redaction",
    "rejected-overclaim",
]
FINAL_CRITERION_STATUS_VOCABULARY = [
    "pending",
    "passed",
    "failed",
    "blocked",
    "exception-requested",
    "exception-approved",
    "exception-rejected",
    "not-applicable",
    "rejected-redaction",
    "rejected-overclaim",
]
REVIEW_DECISION_VOCABULARY = ["approve", "reject", "exception"]
ALLOWED_DEMOTION_STATUSES = ["passed", "exception-approved", "not-applicable"]
UPSTREAM_RESULT_STATUS_VOCABULARY = [
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
]
ACCEPTABLE_UPSTREAM_RESULT_STATUSES = ["passed", "not-required"]
EXCEPTION_POLICY_STATUSES = {
    "exception-requested",
    "exception-approved",
    "exception-rejected",
    "not-applicable",
}
REQUIRED_RETAINED_PACKET_IDS = {
    "packet-hal-cmsis-startup-asm",
    "packet-freertos-runtime",
    "packet-marlin-cpp-print-core-oracle",
    "packet-network-lwip-mbedtls-wui",
    "packet-filesystem-fatfs-littlefs-libsysbase",
    "packet-usb-tinyusb-and-media",
    "packet-generated-assets-resource-pipeline",
    "packet-release-signing-and-packaging",
    "packet-mmu-modbus-auxiliary-controllers",
    "packet-runtime-safety-crashdump-watchdog",
}
REQUIRED_FINAL_CRITERION_IDS = {
    "final-ci-evidence",
    "final-simulator-evidence",
    "final-hardware-safety-media-evidence",
    "final-live-network-transfer-evidence",
    "final-release-artifact-signing-evidence",
    "final-retained-code-acceptance",
    "final-residual-risk-review",
    "final-maintainer-decision",
    "final-reference-demotion-allowed",
}
REQUIRED_FINAL_EVIDENCE_FAMILIES = {
    "ci",
    "simulator",
    "hardware",
    "live-service",
    "release",
    "retained-code",
    "residual-risk",
    "maintainer-decision",
}
REQUIRED_PACKET_FIELDS = [
    "id",
    "title",
    "requirement_ids",
    "taxonomy_tags",
    "retained_source_refs",
    "prior_phase_refs",
    "required_evidence_refs",
    "supplied_evidence_result_refs",
    "owner",
    "approver_role",
    "approval_metadata",
    "status",
    "rationale",
    "residual_risk",
    "blocker_or_deferred_action",
    "exception_ref",
    "secret_handling_policy",
    "unsupported_claims",
]
REQUIRED_FINAL_CRITERION_FIELDS = [
    "id",
    "title",
    "requirement_ids",
    "evidence_family",
    "source_refs",
    "required_decision",
    "default_status",
    "allowed_statuses",
    "maintainer_decision_required",
    "exception_allowed",
    "blocks_demotion",
    "residual_risk_ref",
    "local_proof_boundary",
    "non_local_evidence_boundary",
    "unsupported_claims",
]
FINAL_DECISION_REQUIRED_FIELDS = [
    "decision_id",
    "criterion_id",
    "decision",
    "status",
    "approver",
    "approver_role",
    "decision_timestamp",
    "rationale",
    "evidence_refs",
    "residual_risk",
    "exception",
    "redaction_summary",
]
UPSTREAM_RESULT_REQUIREMENT_FIELDS = [
    "criterion_id",
    "evidence_family",
    "result_required",
    "source_phase",
    "source_lifecycle_id",
    "required_manifest_refs",
    "approved_ref_roots",
    "acceptable_statuses",
    "hard_blocking_statuses",
    "exception_coverable_statuses",
    "required_row_fields",
    "redaction_status_field",
    "source_ref_status_field",
    "hard_blocker_reasons",
    "requirement_ids",
]
UPSTREAM_RESULT_ROW_REQUIRED_FIELDS = [
    "criterion_id",
    "evidence_family",
    "owning_phase",
    "source_lifecycle_id",
    "status",
    "failure_reason",
    "artifact_refs",
    "redaction_status",
    "source_ref_status",
    "generated_at_utc",
    "requirement_ids",
]
EXCEPTION_REQUIRED_FIELDS = [
    "scope",
    "rationale",
    "approver",
    "approver_role",
    "affected_printer_or_release_surface",
    "mitigation_or_follow_up",
    "expiry_or_review_trigger",
    "evidence_refs",
]
REQUIRED_UNSUPPORTED_CLAIMS = {
    "claim-local-proof-is-maintainer-acceptance",
    "claim-reference-demotion-without-decision-input",
    "claim-sensitive-payload-retained",
}
REQUIRED_GENERATED_ARTIFACTS = {
    "run-manifest.json",
    "normalized-final-demotion-results.json",
    "upstream-result-consumption.json",
    "retained-code-acceptance-summary.json",
    "residual-risk-register.json",
    "redacted-readiness-report.md",
    "source-contract-snapshots/phase18_cutover_review_contract.json",
    "maintainer-decision-input-template.json",
}
REQUIRED_RETAINED_REVIEW_FIELDS = [
    "packet_id",
    "status",
    "approver",
    "approver_role",
    "decision_timestamp",
    "rationale",
    "supplied_evidence_result_refs",
    "residual_risk",
    "blocker_or_deferred_action",
    "exception_ref",
    "redaction_summary",
]
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api-key",
    "api_key",
    "apikey",
    "bearer_token",
    "credential",
    "private_key",
    "signing_key_value",
    "certificate_private_material",
    "raw_key_bytes",
    "certificate_pem",
    "certificate_bytes",
    "firmware_payload",
    "raw_firmware_payload",
    "bbf_payload",
    "dfu_payload",
    "raw_crash_dump",
    "token",
    "password",
    "secret",
    "credential_value",
    "wifi_password",
    "connect_token",
    "prusalink_password",
}
FORBIDDEN_ASSIGNMENT_FIELD_NAMES = FORBIDDEN_FIELD_NAMES | {
    "authorization",
    "authorization_header",
}


def forbidden_assignment_pattern(field_name: str):
    segments = [
        segment for segment in re.split(r"[^A-Za-z0-9]+", field_name)
        if segment
    ]
    if len(segments) > 1:
        field_pattern = r"[\s_-]*".join(
            re.escape(segment) for segment in segments)
    else:
        field_pattern = re.escape(segments[0] if segments else field_name)
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
    ("final-cutover-complete",
     re.compile(r"\bfinal cutover complete\b", re.IGNORECASE)),
    ("cutover-readiness-proven",
     re.compile(r"\bcutover readiness proven\b", re.IGNORECASE)),
    ("retained-code-accepted",
     re.compile(r"\bretained[- ]code accepted by maintainer\b",
                re.IGNORECASE)),
    ("maintainer-approval-complete",
     re.compile(r"\bmaintainer approval complete\b", re.IGNORECASE)),
    ("local-proof-approved-demotion",
     re.compile(r"\blocal proof approved demotion\b", re.IGNORECASE)),
    *((f"{field_name}-assignment", forbidden_assignment_pattern(field_name))
      for field_name in sorted(FORBIDDEN_ASSIGNMENT_FIELD_NAMES)),
)
SOURCE_REF_ROW_COLLECTIONS = {
    "tools/bazel/manifests/phase11_retained_code_justifications.json":
    ("retained_code_justifications", "id"),
    "tools/bazel/manifests/foreign_code_inventory.json": ("components", "id"),
    "tools/bazel/manifests/unsafe_boundary_audit.json": ("surfaces",
                                                         "surface_id"),
    "tools/bazel/manifests/phase11_cutover_readiness.json":
    ("cutover_criteria", "id"),
    "tools/bazel/manifests/phase13_ci_evidence_contract.json": ("gates", "id"),
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json":
    ("scenarios", "id"),
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json":
    ("scenarios", "id"),
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json":
    ("scenarios", "id"),
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json":
    ("rows", "id"),
}
UPSTREAM_SOURCE_LIFECYCLES = {
    PHASE: PHASE_LIFECYCLE_ID,
    "19-aggregate-cutover-evidence-ci": "19-2026-06-21T01-07-45",
    "20-release-candidate-artifact-production": "20-2026-06-21T12-40-17",
}
RETAINED_SURFACE_SOURCE_PATHS = [
    "tools/bazel/manifests/phase11_retained_code_justifications.json",
    "tools/bazel/manifests/foreign_code_inventory.json",
    "tools/bazel/manifests/unsafe_boundary_audit.json",
]
EXPECTED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "id",
    "phase",
    "phase_lifecycle_id",
    "artifact_name",
    "output_root",
    "retained_packet_status_vocabulary",
    "final_criterion_status_vocabulary",
    "upstream_result_status_vocabulary",
    "review_decision_vocabulary",
    "allowed_demotion_statuses",
    "acceptable_upstream_result_statuses",
    "retained_source_collections",
    "retained_code_acceptance_packet_schema",
    "final_decision_schema",
    "upstream_result_requirements",
    "retained_code_acceptance_packets",
    "final_demotion_criteria",
    "generated_artifacts",
}
WIRING_REQUIRED_TEXT = {
    Path("tools/bazel/BUILD.bazel"): [
        'name = "phase18_source_ref_manifests"',
        '"manifests/phase11_cutover_readiness.json"',
        '"manifests/phase11_retained_code_justifications.json"',
        '"manifests/foreign_code_inventory.json"',
        '"manifests/unsafe_boundary_audit.json"',
        '"manifests/phase13_ci_evidence_contract.json"',
        '"manifests/phase14_simulator_evidence_contract.json"',
        '"manifests/phase15_hardware_evidence_contract.json"',
        '"manifests/phase16_live_network_evidence_contract.json"',
        '"manifests/phase17_release_candidate_evidence_contract.json"',
        'name = "phase18_verify"',
        'name = "phase18_verify_tests"',
        'src = "rust_workflow.sh"',
        '"phase18_cutover_review.py"',
        '"phase18_cutover_review_test.py"',
        '"manifests/phase18_cutover_review_contract.json"',
        '":phase18_source_ref_manifests"',
        '"//:phase18_cutover_review_docs"',
        '"//:phase11_cutover_evidence_docs"',
        '"//:phase13_ci_evidence_docs"',
        '"//:phase14_simulator_evidence_docs"',
        '"//:phase15_hardware_evidence_docs"',
        '"//:phase16_live_network_evidence_docs"',
        '"//:phase17_release_candidate_evidence_docs"',
    ],
    Path("BUILD.bazel"): [
        'name = "phase18_cutover_review_docs"',
        '".planning/phases/18-retained-code-acceptance-and-cutover-review/18-CONTEXT.md"',
        '".planning/phases/18-retained-code-acceptance-and-cutover-review/18-RESEARCH.md"',
        '".planning/phases/18-retained-code-acceptance-and-cutover-review/18-VALIDATION.md"',
        '".planning/phases/18-retained-code-acceptance-and-cutover-review/18-01-PLAN.md"',
        'name = "phase18_verify"',
        'actual = "//tools/bazel:phase18_verify"',
        'name = "phase18_verify_tests"',
        'actual = "//tools/bazel:phase18_verify_tests"',
    ],
    Path("tools/bazel/rust_workflow.sh"): [
        "phase18_verify)",
        "python3 tools/bazel/phase18_cutover_review.py --wiring-only",
        "python3 tools/bazel/phase18_cutover_review.py --quick",
        "phase18_verify_tests)",
        "python3 tools/bazel/phase18_cutover_review_test.py",
    ],
    Path("justfile"): [
        "phase18-verify:",
        "bazel run //tools/bazel:phase18_verify_tests",
        "bazel run //tools/bazel:phase18_verify",
    ],
}


class VerificationError(Exception):
    pass


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


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = require_list(row, field, row_name)
    if not all(isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields if field in row and row[field] in ("", None)
    ]
    if missing or empty:
        details = []
        if missing:
            details.append("missing required fields: " + ", ".join(missing))
        if empty:
            details.append("empty required fields: " + ", ".join(empty))
        raise VerificationError(f"{row_name} " + "; ".join(details))


def require_repo_relative(path_value: str, row_name: str) -> Path:
    relative_path = Path(path_value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} path must be repo-relative and cannot traverse: {path_value}"
        )
    return relative_path


def require_repo_relative_under(path_value: str, output_root: str | Path,
                                row_name: str) -> Path:
    relative_path = require_repo_relative(path_value, row_name)
    expected_root = Path(output_root)
    try:
        relative_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} must be under {expected_root.as_posix()} or external://phase18/: {path_value}"
        ) from error
    return relative_path


def contained_output_dir(root: Path, output_dir: str | Path) -> Path:
    relative_path = require_repo_relative_under(str(output_dir),
                                                DEFAULT_OUTPUT_DIR,
                                                "--output-dir")
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    full_path = (root / relative_path).resolve(strict=False)
    try:
        full_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir}"
        ) from error
    return full_path


def require_phase18_artifact_ref(ref: str, row_name: str) -> None:
    if ref.startswith("external://phase18/"):
        return
    if ref.startswith("external://") or ref.startswith("artifact://"):
        raise VerificationError(
            f"{row_name} artifact ref must stay under phase18 evidence: {ref}")
    require_repo_relative_under(ref, DEFAULT_OUTPUT_DIR, row_name)


def require_external_ref(ref: str, allowed_roots: list[str],
                         row_name: str) -> None:
    if not any(
            ref.startswith(root)
            for root in allowed_roots if root.startswith("external://")):
        raise VerificationError(
            f"{row_name} external ref is outside approved roots: {ref}")
    if ".." in ref.split("/"):
        raise VerificationError(
            f"{row_name} external ref cannot traverse: {ref}")


def require_upstream_artifact_ref(ref: str, allowed_roots: list[str],
                                  row_name: str) -> None:
    if ref.startswith("artifact://"):
        raise VerificationError(
            f"{row_name} artifact ref is outside approved roots: {ref}")
    if ref.startswith("external://"):
        require_external_ref(ref, allowed_roots, row_name)
        return
    matching_repo_roots = [
        root for root in allowed_roots if not root.startswith("external://")
    ]
    if not matching_repo_roots:
        raise VerificationError(
            f"{row_name} repo ref is outside approved roots: {ref}")
    last_error: VerificationError | None = None
    for root in matching_repo_roots:
        try:
            require_repo_relative_under(ref, root, row_name)
            return
        except VerificationError as error:
            last_error = error
    if last_error is not None:
        raise last_error
    raise VerificationError(
        f"{row_name} repo ref is outside approved roots: {ref}")


def require_iso_utc(timestamp_text: str, row_name: str) -> None:
    if not timestamp_text.endswith("Z"):
        raise VerificationError(
            f"{row_name} decision_timestamp must be ISO-8601 UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(
            f"{row_name} decision_timestamp must be ISO-8601 UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(
            parsed):
        raise VerificationError(
            f"{row_name} decision_timestamp must be ISO-8601 UTC")


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


def normalized_field_name(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


FORBIDDEN_NORMALIZED_FIELD_NAMES = {
    normalized_field_name(field_name)
    for field_name in FORBIDDEN_FIELD_NAMES
} | {
    "authorization",
    "authorizationheader",
}


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
