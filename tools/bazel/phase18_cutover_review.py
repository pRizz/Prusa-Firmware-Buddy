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
PHASE = "18-retained-code-acceptance-and-cutover-review"
PHASE_LIFECYCLE_ID = "18-2026-06-20T14-27-15"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase18_cutover_review_contract.json")
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
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-marker", re.compile(r"BEGIN (?:RSA |EC )?PRIVATE KEY", re.IGNORECASE)),
    ("firmware-payload-marker", re.compile(r"\b(?:raw )?firmware payload\b", re.IGNORECASE)),
    ("raw-crash-dump-marker", re.compile(r"\braw crash dump\b", re.IGNORECASE)),
    ("password-assignment", re.compile(r"\bpassword\s*=", re.IGNORECASE)),
    ("token-assignment", re.compile(r"\btoken\s*=", re.IGNORECASE)),
    ("secret-assignment", re.compile(r"\bsecret\s*=", re.IGNORECASE)),
    ("reference-demotion-approved", re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("final-cutover-complete", re.compile(r"\bfinal cutover complete\b", re.IGNORECASE)),
    ("cutover-readiness-proven", re.compile(r"\bcutover readiness proven\b", re.IGNORECASE)),
    ("retained-code-accepted", re.compile(r"\bretained[- ]code accepted by maintainer\b", re.IGNORECASE)),
    ("maintainer-approval-complete", re.compile(r"\bmaintainer approval complete\b", re.IGNORECASE)),
    ("local-proof-approved-demotion", re.compile(r"\blocal proof approved demotion\b", re.IGNORECASE)),
)
SOURCE_REF_ROW_COLLECTIONS = {
    "tools/bazel/manifests/phase11_retained_code_justifications.json": ("retained_code_justifications", "id"),
    "tools/bazel/manifests/foreign_code_inventory.json": ("components", "id"),
    "tools/bazel/manifests/unsafe_boundary_audit.json": ("surfaces", "surface_id"),
    "tools/bazel/manifests/phase11_cutover_readiness.json": ("cutover_criteria", "id"),
    "tools/bazel/manifests/phase13_ci_evidence_contract.json": ("gates", "id"),
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json": ("scenarios", "id"),
    "tools/bazel/manifests/phase15_hardware_evidence_contract.json": ("scenarios", "id"),
    "tools/bazel/manifests/phase16_live_network_evidence_contract.json": ("scenarios", "id"),
    "tools/bazel/manifests/phase17_release_candidate_evidence_contract.json": ("rows", "id"),
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
    "review_decision_vocabulary",
    "allowed_demotion_statuses",
    "retained_source_collections",
    "retained_code_acceptance_packet_schema",
    "final_decision_schema",
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


def require_list_of_strings(row: dict[str, Any], field: str, row_name: str) -> list[str]:
    value = require_list(row, field, row_name)
    if not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_fields(row: dict[str, Any], fields: list[str], row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and row[field] in ("", None)]
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
        raise VerificationError(f"{row_name} path must be repo-relative and cannot traverse: {path_value}")
    return relative_path


def require_repo_relative_under(path_value: str, output_root: str | Path, row_name: str) -> Path:
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
    relative_path = require_repo_relative_under(str(output_dir), DEFAULT_OUTPUT_DIR, "--output-dir")
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    full_path = (root / relative_path).resolve(strict=False)
    try:
        full_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir}") from error
    return full_path


def require_phase18_artifact_ref(ref: str, row_name: str) -> None:
    if ref.startswith("external://phase18/"):
        return
    if ref.startswith("external://") or ref.startswith("artifact://"):
        raise VerificationError(f"{row_name} artifact ref must stay under phase18 evidence: {ref}")
    require_repo_relative_under(ref, DEFAULT_OUTPUT_DIR, row_name)


def require_iso_utc(timestamp_text: str, row_name: str) -> None:
    if not timestamp_text.endswith("Z"):
        raise VerificationError(f"{row_name} decision_timestamp must be ISO-8601 UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(f"{row_name} decision_timestamp must be ISO-8601 UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise VerificationError(f"{row_name} decision_timestamp must be ISO-8601 UTC")


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
                if key in FORBIDDEN_FIELD_NAMES:
                    errors.append(f"{source_name} contains forbidden field name {key} at {nested_path}")
                walk(nested, nested_path)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                walk(nested, f"{path}[{index}]")

    walk(data, maybe_path)
    if errors:
        raise VerificationError("\n".join(errors))


def source_ref_manifest_paths() -> set[Path]:
    return {Path(path) for path in SOURCE_REF_ROW_COLLECTIONS}


def resolve_source_ref(root: Path, source_ref: str, row_name: str) -> None:
    if "#" not in source_ref:
        raise VerificationError(f"{row_name} source ref must use file#row-id: {source_ref}")
    path_text, row_id = source_ref.split("#", 1)
    if not path_text or not row_id:
        raise VerificationError(f"{row_name} source ref must include file and row ID: {source_ref}")
    relative_path = require_repo_relative(path_text, row_name)
    if relative_path not in source_ref_manifest_paths():
        raise VerificationError(f"{row_name} source ref path is not an approved Phase 18 source manifest: {source_ref}")
    data = load_json(root, relative_path)
    collection_name, key_name = SOURCE_REF_ROW_COLLECTIONS[relative_path.as_posix()]
    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(f"{row_name} source ref collection is missing: {source_ref}")
    matches = [
        f"{collection_name}[{index}]"
        for index, candidate in enumerate(rows)
        if isinstance(candidate, dict) and candidate.get(key_name) == row_id
    ]
    if not matches:
        raise VerificationError(f"{row_name} source ref row not found in approved row collections: {source_ref}")
    if len(matches) > 1:
        raise VerificationError(f"{row_name} source ref row matches multiple approved rows: {source_ref}")


def retained_surface_source_refs(root: Path) -> set[str]:
    refs: set[str] = set()
    for path in RETAINED_SURFACE_SOURCE_PATHS:
        data = load_json(root, path)
        collection_name, key_name = SOURCE_REF_ROW_COLLECTIONS[path]
        rows = data.get(collection_name)
        if not isinstance(rows, list):
            raise VerificationError(f"{path} must contain {collection_name} list")
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise VerificationError(f"{path} {collection_name}[{index}] must be an object")
            row_id = row.get(key_name)
            if not isinstance(row_id, str) or not row_id:
                raise VerificationError(f"{path} {collection_name}[{index}] {key_name} must be a non-empty string")
            refs.add(f"{path}#{row_id}")
    return refs


def contract_packets(contract: dict[str, Any]) -> list[dict[str, Any]]:
    raw_packets = contract.get("retained_code_acceptance_packets")
    if not isinstance(raw_packets, list):
        raise VerificationError("contract retained_code_acceptance_packets must be a list")
    packets: list[dict[str, Any]] = []
    for index, packet in enumerate(raw_packets):
        if not isinstance(packet, dict):
            raise VerificationError(f"retained_code_acceptance_packets[{index}] must be an object")
        packets.append(packet)
    return packets


def contract_final_criteria(contract: dict[str, Any]) -> list[dict[str, Any]]:
    raw_criteria = contract.get("final_demotion_criteria")
    if not isinstance(raw_criteria, list):
        raise VerificationError("contract final_demotion_criteria must be a list")
    criteria: list[dict[str, Any]] = []
    for index, criterion in enumerate(raw_criteria):
        if not isinstance(criterion, dict):
            raise VerificationError(f"final_demotion_criteria[{index}] must be an object")
        criteria.append(criterion)
    return criteria


def validate_schema(contract: dict[str, Any], errors: list[str]) -> None:
    top_level_fields = set(contract)
    for missing in sorted(EXPECTED_TOP_LEVEL_FIELDS - top_level_fields):
        errors.append(f"{CONTRACT_MANIFEST.as_posix()} missing top-level field: {missing}")
    for extra in sorted(top_level_fields - EXPECTED_TOP_LEVEL_FIELDS):
        errors.append(f"{CONTRACT_MANIFEST.as_posix()} unexpected top-level field: {extra}")
    expected_values = {
        "schema_version": "1",
        "id": "phase18_cutover_review_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase18-cutover-review",
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, expected in expected_values.items():
        if contract.get(field) != expected:
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected!r}")
    try:
        if require_list_of_strings(contract, "retained_packet_status_vocabulary", "contract") != RETAINED_PACKET_STATUS_VOCABULARY:
            errors.append("retained_packet_status_vocabulary does not match the Phase 18 vocabulary")
        if require_list_of_strings(contract, "final_criterion_status_vocabulary", "contract") != FINAL_CRITERION_STATUS_VOCABULARY:
            errors.append("final_criterion_status_vocabulary does not match the Phase 18 vocabulary")
        if require_list_of_strings(contract, "review_decision_vocabulary", "contract") != REVIEW_DECISION_VOCABULARY:
            errors.append("review_decision_vocabulary does not match the Phase 18 vocabulary")
        if require_list_of_strings(contract, "allowed_demotion_statuses", "contract") != ALLOWED_DEMOTION_STATUSES:
            errors.append("allowed_demotion_statuses does not match the Phase 18 demotion policy")
        validate_source_collection_map(contract, errors)
        validate_packet_schema(contract, errors)
        validate_decision_schema(contract, errors)
        validate_generated_artifacts(contract, errors)
    except VerificationError as error:
        errors.append(str(error))


def validate_source_collection_map(contract: dict[str, Any], errors: list[str]) -> None:
    source_collections = require_dict(contract, "retained_source_collections", "contract")
    for path, (collection_name, key_name) in SOURCE_REF_ROW_COLLECTIONS.items():
        entry = source_collections.get(path)
        if not isinstance(entry, dict):
            errors.append(f"retained_source_collections missing source manifest: {path}")
            continue
        if entry.get("collection") != collection_name:
            errors.append(f"{path} retained_source_collections collection must be {collection_name}")
        if entry.get("key") != key_name:
            errors.append(f"{path} retained_source_collections key must be {key_name}")


def validate_packet_schema(contract: dict[str, Any], errors: list[str]) -> None:
    schema = require_dict(contract, "retained_code_acceptance_packet_schema", "contract")
    required_fields = require_list_of_strings(schema, "required_fields", "retained_code_acceptance_packet_schema")
    if required_fields != REQUIRED_PACKET_FIELDS:
        errors.append("retained_code_acceptance_packet_schema required_fields do not match Phase 18 packet requirements")
    if schema.get("secret_handling_policy") != "name-only-or-redacted":
        errors.append("retained_code_acceptance_packet_schema secret_handling_policy must be name-only-or-redacted")


def validate_decision_schema(contract: dict[str, Any], errors: list[str]) -> None:
    schema = require_dict(contract, "final_decision_schema", "contract")
    required_fields = require_list_of_strings(schema, "required_fields", "final_decision_schema")
    if required_fields != FINAL_DECISION_REQUIRED_FIELDS:
        errors.append("final_decision_schema required_fields do not match Phase 18 decision input requirements")
    decisions = require_list_of_strings(schema, "decision_vocabulary", "final_decision_schema")
    if decisions != REVIEW_DECISION_VOCABULARY:
        errors.append("final_decision_schema decision_vocabulary does not match review_decision_vocabulary")
    exception = require_dict(schema, "exception", "final_decision_schema")
    exception_fields = require_list_of_strings(exception, "required_fields", "final_decision_schema.exception")
    if exception_fields != EXCEPTION_REQUIRED_FIELDS:
        errors.append("final_decision_schema exception.required_fields do not match Phase 18 exception requirements")


def validate_generated_artifacts(contract: dict[str, Any], errors: list[str]) -> None:
    artifacts = require_list_of_strings(contract, "generated_artifacts", "contract")
    seen = set(artifacts)
    for missing in sorted(REQUIRED_GENERATED_ARTIFACTS - seen):
        errors.append(f"missing required generated artifact: {missing}")
    for artifact in artifacts:
        try:
            require_repo_relative(artifact, "generated_artifacts")
        except VerificationError as error:
            errors.append(str(error))


def validate_packets(root: Path, packets: list[dict[str, Any]], errors: list[str]) -> set[str]:
    packet_ids = [str(packet.get("id")) for packet in packets]
    for missing in sorted(REQUIRED_RETAINED_PACKET_IDS - set(packet_ids)):
        errors.append("missing required retained packet: " + missing)
    if len(packet_ids) != len(set(packet_ids)):
        errors.append("duplicate retained packet IDs are not allowed")
    covered_source_refs: set[str] = set()
    for packet in packets:
        packet_name = str(packet.get("id", "unknown retained packet"))
        try:
            validate_packet(root, packet, packet_name)
            covered_source_refs.update(packet["retained_source_refs"])
        except VerificationError as error:
            errors.append(str(error))
    for missing in sorted(retained_surface_source_refs(root) - covered_source_refs):
        errors.append("missing retained source coverage: " + missing)
    return set(packet_ids)


def validate_packet(root: Path, packet: dict[str, Any], packet_name: str) -> None:
    errors: list[str] = []
    try:
        require_fields(packet, REQUIRED_PACKET_FIELDS, packet_name)
        requirement_ids = set(require_list_of_strings(packet, "requirement_ids", packet_name))
        require_list_of_strings(packet, "taxonomy_tags", packet_name)
        status = require_string(packet, "status", packet_name)
        source_refs = require_list_of_strings(packet, "retained_source_refs", packet_name)
        require_list_of_strings(packet, "prior_phase_refs", packet_name)
        require_list_of_strings(packet, "required_evidence_refs", packet_name)
        require_list_of_strings(packet, "supplied_evidence_result_refs", packet_name)
        require_string(packet, "approver_role", packet_name)
        require_dict(packet, "approval_metadata", packet_name)
        require_string(packet, "rationale", packet_name)
        require_string(packet, "residual_risk", packet_name)
        require_string(packet, "blocker_or_deferred_action", packet_name)
        require_string(packet, "exception_ref", packet_name)
        require_list_of_strings(packet, "unsupported_claims", packet_name)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    unknown_requirements = sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)
    if "REV-01" not in requirement_ids:
        errors.append(f"{packet_name} must cover REV-01")
    if unknown_requirements:
        errors.append(f"{packet_name} uses unknown REV requirement IDs: {', '.join(unknown_requirements)}")
    if status not in RETAINED_PACKET_STATUS_VOCABULARY:
        errors.append(f"{packet_name} status is invalid: {status}")
    if packet.get("secret_handling_policy") != "name-only-or-redacted":
        errors.append(f"{packet_name} secret_handling_policy must be name-only-or-redacted")
    unsupported_claims = set(packet.get("unsupported_claims", []))
    for missing in sorted(REQUIRED_UNSUPPORTED_CLAIMS - unsupported_claims):
        errors.append(f"{packet_name} missing unsupported claim guard: {missing}")
    for source_ref in source_refs:
        try:
            resolve_source_ref(root, source_ref, packet_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def validate_final_criteria(root: Path, criteria: list[dict[str, Any]], packet_ids: set[str], errors: list[str]) -> None:
    criterion_ids = [str(criterion.get("id")) for criterion in criteria]
    for missing in sorted(REQUIRED_FINAL_CRITERION_IDS - set(criterion_ids)):
        errors.append("missing required final demotion criterion: " + missing)
    if len(criterion_ids) != len(set(criterion_ids)):
        errors.append("duplicate final demotion criterion IDs are not allowed")
    covered_families: set[str] = set()
    for criterion in criteria:
        criterion_name = str(criterion.get("id", "unknown final criterion"))
        try:
            validate_final_criterion(root, criterion, criterion_name, packet_ids)
            covered_families.add(criterion["evidence_family"])
        except VerificationError as error:
            errors.append(str(error))
    for missing in sorted(REQUIRED_FINAL_EVIDENCE_FAMILIES - covered_families):
        errors.append("missing required final evidence family coverage: " + missing)


def validate_final_criterion(root: Path, criterion: dict[str, Any], criterion_name: str, packet_ids: set[str]) -> None:
    errors: list[str] = []
    try:
        require_fields(criterion, REQUIRED_FINAL_CRITERION_FIELDS, criterion_name)
        requirement_ids = set(require_list_of_strings(criterion, "requirement_ids", criterion_name))
        evidence_family = require_string(criterion, "evidence_family", criterion_name)
        required_decision = require_string(criterion, "required_decision", criterion_name)
        default_status = require_string(criterion, "default_status", criterion_name)
        allowed_statuses = set(require_list_of_strings(criterion, "allowed_statuses", criterion_name))
        source_refs = require_list_of_strings(criterion, "source_refs", criterion_name)
        require_bool(criterion, "maintainer_decision_required", criterion_name)
        require_bool(criterion, "exception_allowed", criterion_name)
        require_bool(criterion, "blocks_demotion", criterion_name)
        require_string(criterion, "residual_risk_ref", criterion_name)
        require_string(criterion, "local_proof_boundary", criterion_name)
        require_string(criterion, "non_local_evidence_boundary", criterion_name)
        require_list_of_strings(criterion, "unsupported_claims", criterion_name)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    unknown_requirements = sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)
    if not requirement_ids:
        errors.append(f"{criterion_name} must cover at least one REV- requirement")
    if unknown_requirements:
        errors.append(f"{criterion_name} uses unknown REV requirement IDs: {', '.join(unknown_requirements)}")
    if evidence_family not in REQUIRED_FINAL_EVIDENCE_FAMILIES:
        errors.append(f"{criterion_name} evidence_family is invalid: {evidence_family}")
    if required_decision not in REVIEW_DECISION_VOCABULARY:
        errors.append(f"{criterion_name} required_decision is invalid: {required_decision}")
    if default_status not in FINAL_CRITERION_STATUS_VOCABULARY:
        errors.append(f"{criterion_name} default_status is invalid: {default_status}")
    if not allowed_statuses <= set(FINAL_CRITERION_STATUS_VOCABULARY):
        errors.append(f"{criterion_name} allowed_statuses contains unknown statuses")
    if default_status in FINAL_CRITERION_STATUS_VOCABULARY and default_status not in allowed_statuses:
        errors.append(f"{criterion_name} default_status {default_status} is not allowed by allowed_statuses")
    if criterion.get("blocks_demotion") is not True:
        errors.append(f"{criterion_name} blocks_demotion must be true")
    if criterion_name in {
        "final-retained-code-acceptance",
        "final-residual-risk-review",
        "final-maintainer-decision",
        "final-reference-demotion-allowed",
    } and criterion.get("maintainer_decision_required") is not True:
        errors.append(f"{criterion_name} maintainer_decision_required must be true")
    unsupported_claims = set(criterion.get("unsupported_claims", []))
    if "claim-reference-demotion-without-decision-input" not in unsupported_claims:
        errors.append(f"{criterion_name} must guard against reference demotion without decision input")
    for source_ref in source_refs:
        try:
            resolve_source_ref(root, source_ref, criterion_name)
        except VerificationError as error:
            errors.append(str(error))
    for packet_id in criterion.get("packet_refs", []):
        if packet_id not in packet_ids:
            errors.append(f"{criterion_name} packet ref does not resolve: {packet_id}")
    if errors:
        raise VerificationError("\n".join(errors))


def check_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    validate_schema(contract, errors)
    try:
        packets = contract_packets(contract)
        final_criteria = contract_final_criteria(contract)
        packet_ids = validate_packets(root, packets, errors)
        validate_final_criteria(root, final_criteria, packet_ids, errors)
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def load_decision_input(root: Path, maybe_path: str | None) -> dict[str, Any] | None:
    if not maybe_path:
        return None
    input_path = require_repo_relative(maybe_path, "--decision-input")
    raw_text = read_text(root, input_path)
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"{input_path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError("--decision-input must contain a top-level object")
    reject_forbidden_json_fields(data, input_path.as_posix())
    packet = data.get("decision_packet")
    if not isinstance(packet, dict):
        raise VerificationError("decision_packet must be present and must be an object")
    if packet.get("phase") != PHASE:
        raise VerificationError(f"decision_packet phase must be {PHASE}")
    if packet.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(f"decision_packet phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
    if "retained_code_reviews" not in data:
        data["retained_code_reviews"] = []
    if "final_criterion_decisions" not in data:
        data["final_criterion_decisions"] = []
    if not isinstance(data["retained_code_reviews"], list):
        raise VerificationError("retained_code_reviews must be a list")
    if not isinstance(data["final_criterion_decisions"], list):
        raise VerificationError("final_criterion_decisions must be a list")
    return data


def validate_exception_metadata(exception: Any, row_name: str) -> dict[str, Any]:
    if not isinstance(exception, dict):
        raise VerificationError(f"{row_name} exception must be an object")
    require_fields(exception, EXCEPTION_REQUIRED_FIELDS, f"{row_name} exception")
    for field in EXCEPTION_REQUIRED_FIELDS:
        if field == "evidence_refs":
            continue
        require_string(exception, field, f"{row_name} exception")
    evidence_refs = require_list_of_strings(exception, "evidence_refs", f"{row_name} exception")
    require_non_empty_refs(evidence_refs, f"{row_name} exception", "evidence_refs")
    for ref in evidence_refs:
        require_phase18_artifact_ref(ref, f"{row_name} exception evidence_refs")
    return exception


def require_non_empty_refs(refs: list[str], row_name: str, field: str) -> None:
    if not refs:
        raise VerificationError(f"{row_name} {field} must include at least one Phase 18 evidence ref")


def validate_final_decision(row: Any, criterion_ids: set[str], row_index: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise VerificationError(f"final_criterion_decisions[{row_index}] must be an object")
    row_name = str(row.get("criterion_id", f"final_criterion_decisions[{row_index}]"))
    require_fields(row, FINAL_DECISION_REQUIRED_FIELDS, row_name)
    require_string(row, "decision_id", row_name)
    criterion_id = require_string(row, "criterion_id", row_name)
    if criterion_id not in criterion_ids:
        raise VerificationError(f"{row_name} criterion_id does not resolve: {criterion_id}")
    decision = require_string(row, "decision", row_name)
    status = require_string(row, "status", row_name)
    if decision not in REVIEW_DECISION_VOCABULARY:
        raise VerificationError(f"{row_name} decision is invalid: {decision}")
    if status not in FINAL_CRITERION_STATUS_VOCABULARY:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    require_string(row, "approver", row_name)
    require_string(row, "approver_role", row_name)
    require_iso_utc(require_string(row, "decision_timestamp", row_name), row_name)
    require_string(row, "rationale", row_name)
    evidence_refs = require_list_of_strings(row, "evidence_refs", row_name)
    for ref in evidence_refs:
        require_phase18_artifact_ref(ref, f"{row_name} evidence_refs")
    require_string(row, "residual_risk", row_name)
    require_string(row, "redaction_summary", row_name)
    if status == "passed":
        if decision != "approve":
            raise VerificationError(f"{row_name} status passed requires decision approve")
        require_non_empty_refs(evidence_refs, row_name, "evidence_refs")
    elif status in {"exception-approved", "not-applicable"}:
        if decision != "exception":
            raise VerificationError(f"{row_name} status {status} requires decision exception")
        require_non_empty_refs(evidence_refs, row_name, "evidence_refs")
        validate_exception_metadata(row["exception"], row_name)
    elif not isinstance(row.get("exception"), dict):
        raise VerificationError(f"{row_name} exception must be an object")
    return row


def validate_retained_review(row: Any, packets_by_id: dict[str, dict[str, Any]], row_index: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise VerificationError(f"retained_code_reviews[{row_index}] must be an object")
    row_name = str(row.get("packet_id", f"retained_code_reviews[{row_index}]"))
    require_fields(row, REQUIRED_RETAINED_REVIEW_FIELDS, row_name)
    packet_id = require_string(row, "packet_id", row_name)
    packet = packets_by_id.get(packet_id)
    if packet is None:
        raise VerificationError(f"{row_name} packet_id does not resolve: {packet_id}")
    status = require_string(row, "status", row_name)
    if status not in RETAINED_PACKET_STATUS_VOCABULARY:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    require_string(row, "approver", row_name)
    approver_role = require_string(row, "approver_role", row_name)
    expected_role = require_string(packet, "approver_role", packet_id)
    if approver_role != expected_role:
        raise VerificationError(f"{row_name} approver_role must be {expected_role}")
    require_iso_utc(require_string(row, "decision_timestamp", row_name), row_name)
    require_string(row, "rationale", row_name)
    supplied_refs = require_list_of_strings(row, "supplied_evidence_result_refs", row_name)
    for ref in supplied_refs:
        require_phase18_artifact_ref(ref, f"{row_name} supplied_evidence_result_refs")
    require_string(row, "residual_risk", row_name)
    require_string(row, "blocker_or_deferred_action", row_name)
    require_string(row, "exception_ref", row_name)
    require_string(row, "redaction_summary", row_name)
    if status in {"accepted", "deferred-approved-exception"}:
        require_non_empty_refs(supplied_refs, row_name, "supplied_evidence_result_refs")
    if status == "deferred-approved-exception":
        if row["exception_ref"] == "none" or row["blocker_or_deferred_action"] == "none":
            raise VerificationError(f"{row_name} deferred-approved-exception requires exception_ref and blocker action")
    if status in {"rejected", "blocked", "rejected-redaction", "rejected-overclaim"}:
        require_string(row, "rationale", row_name)
        require_string(row, "approver_role", row_name)
    return row


def validated_decision_maps(
    decision_input: dict[str, Any] | None,
    packets: list[dict[str, Any]],
    criteria: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if decision_input is None:
        return {}, {}
    criterion_ids = {str(row["id"]) for row in criteria}
    packets_by_id = {str(row["id"]): row for row in packets}
    final_decisions: dict[str, dict[str, Any]] = {}
    retained_reviews: dict[str, dict[str, Any]] = {}
    final_decision_ids: set[str] = set()
    for index, row in enumerate(decision_input["final_criterion_decisions"]):
        decision = validate_final_decision(row, criterion_ids, index)
        decision_id = str(decision["decision_id"])
        if decision_id in final_decision_ids:
            raise VerificationError(f"duplicate final decision id: {decision_id}")
        final_decision_ids.add(decision_id)
        criterion_id = str(decision["criterion_id"])
        if criterion_id in final_decisions:
            raise VerificationError(f"duplicate final criterion decision: {criterion_id}")
        final_decisions[criterion_id] = decision
    for index, row in enumerate(decision_input["retained_code_reviews"]):
        review = validate_retained_review(row, packets_by_id, index)
        packet_id = str(review["packet_id"])
        if packet_id in retained_reviews:
            raise VerificationError(f"duplicate retained code review: {packet_id}")
        retained_reviews[packet_id] = review
    if final_decisions and set(final_decisions) != criterion_ids:
        missing = ", ".join(sorted(criterion_ids - set(final_decisions)))
        raise VerificationError("decision input missing final criterion decisions: " + missing)
    if retained_reviews and set(retained_reviews) != set(packets_by_id):
        missing = ", ".join(sorted(set(packets_by_id) - set(retained_reviews)))
        raise VerificationError("decision input missing retained code reviews: " + missing)
    return retained_reviews, final_decisions


def has_non_empty_evidence_refs(decision: dict[str, Any]) -> bool:
    refs = decision.get("evidence_refs")
    return isinstance(refs, list) and bool(refs) and all(isinstance(ref, str) and ref for ref in refs)


def has_complete_exception_metadata(decision: dict[str, Any]) -> bool:
    try:
        validate_exception_metadata(decision.get("exception"), str(decision.get("criterion_id", "criterion")))
    except VerificationError:
        return False
    return True


def valid_not_applicable(decision: dict[str, Any]) -> bool:
    if decision.get("status") != "not-applicable":
        return False
    if decision.get("decision") != "exception":
        return False
    if not decision.get("rationale") or not has_non_empty_evidence_refs(decision):
        return False
    return has_complete_exception_metadata(decision)


def final_status_allows_demotion(status: str, maybe_decision: dict[str, Any] | None) -> bool:
    if maybe_decision is None or maybe_decision.get("status") != status:
        return False
    if status == "passed":
        return maybe_decision.get("decision") == "approve" and has_non_empty_evidence_refs(maybe_decision)
    if status == "exception-approved":
        return (
            maybe_decision.get("decision") == "exception"
            and has_non_empty_evidence_refs(maybe_decision)
            and has_complete_exception_metadata(maybe_decision)
        )
    if status == "not-applicable":
        return valid_not_applicable(maybe_decision)
    return False


def demotion_allowed(decision_inputs_supplied: bool, normalized_results: list[dict[str, Any]]) -> bool:
    if not decision_inputs_supplied:
        return False
    return all(bool(row["demotion_status_allows_cutover"]) for row in normalized_results)


def generated_artifact_paths(output_dir: Path) -> dict[str, Path]:
    return {artifact: output_dir / artifact for artifact in sorted(REQUIRED_GENERATED_ARTIFACTS)}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_final_results(
    criteria: list[dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for criterion in criteria:
        criterion_id = str(criterion["id"])
        maybe_decision = decisions.get(criterion_id)
        status = str(maybe_decision["status"]) if maybe_decision else str(criterion["default_status"])
        decision = str(maybe_decision["decision"]) if maybe_decision else "pending"
        evidence_refs = list(maybe_decision["evidence_refs"]) if maybe_decision else []
        residual_risk = str(maybe_decision["residual_risk"]) if maybe_decision else str(criterion["residual_risk_ref"])
        status_allows = final_status_allows_demotion(status, maybe_decision)
        blocking_reason = "" if status_allows else f"{criterion_id} status {status} blocks reference demotion"
        results.append(
            {
                "id": criterion_id,
                "requirement_ids": criterion["requirement_ids"],
                "evidence_family": criterion["evidence_family"],
                "status": status,
                "decision": decision,
                "maintainer_decision_required": criterion["maintainer_decision_required"],
                "exception_allowed": criterion["exception_allowed"],
                "blocks_demotion": criterion["blocks_demotion"],
                "source_refs": criterion["source_refs"],
                "evidence_refs": evidence_refs,
                "residual_risk": residual_risk,
                "demotion_blocking_reason": blocking_reason,
                "demotion_status_allows_cutover": status_allows,
            }
        )
    return results


def normalize_retained_reviews(
    packets: list[dict[str, Any]],
    reviews: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for packet in packets:
        packet_id = str(packet["id"])
        maybe_review = reviews.get(packet_id)
        rows.append(
            {
                "id": packet_id,
                "taxonomy_tags": packet["taxonomy_tags"],
                "status": str(maybe_review["status"]) if maybe_review else str(packet["status"]),
                "owner": packet["owner"],
                "approver_role": str(maybe_review["approver_role"]) if maybe_review else str(packet["approver_role"]),
                "retained_source_refs": packet["retained_source_refs"],
                "required_evidence_refs": packet["required_evidence_refs"],
                "supplied_evidence_result_refs": list(maybe_review["supplied_evidence_result_refs"])
                if maybe_review
                else list(packet["supplied_evidence_result_refs"]),
                "residual_risk": str(maybe_review["residual_risk"]) if maybe_review else str(packet["residual_risk"]),
                "blocker_or_deferred_action": str(maybe_review["blocker_or_deferred_action"])
                if maybe_review
                else str(packet["blocker_or_deferred_action"]),
                "exception_ref": str(maybe_review["exception_ref"]) if maybe_review else str(packet["exception_ref"]),
            }
        )
    return rows


def build_residual_risk_register(
    final_results: list[dict[str, Any]],
    retained_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for row in final_results:
        if row["status"] in {"passed", "exception-approved"} or row["demotion_status_allows_cutover"]:
            continue
        risks.append(
            {
                "id": row["id"],
                "source": "final-demotion-criterion",
                "status": row["status"],
                "risk": row["residual_risk"],
                "owner": "release-maintainer",
                "required_action": row["demotion_blocking_reason"],
                "evidence_refs": row["evidence_refs"],
            }
        )
    for row in retained_rows:
        if row["status"] in {"accepted", "deferred-approved-exception"}:
            continue
        risks.append(
            {
                "id": row["id"],
                "source": "retained-code-packet",
                "status": row["status"],
                "risk": row["residual_risk"],
                "owner": row["owner"],
                "required_action": row["blocker_or_deferred_action"],
                "evidence_refs": row["supplied_evidence_result_refs"],
            }
        )
    return risks


def count_statuses(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def requirement_coverage(packets: list[dict[str, Any]], criteria: list[dict[str, Any]]) -> dict[str, list[str]]:
    coverage = {requirement_id: [] for requirement_id in sorted(REQUIRED_REQUIREMENT_IDS)}
    for row in [*packets, *criteria]:
        row_id = str(row["id"])
        for requirement_id in row["requirement_ids"]:
            if requirement_id in coverage:
                coverage[requirement_id].append(row_id)
    return coverage


def decision_input_template(contract: dict[str, Any]) -> dict[str, Any]:
    first_packet = contract["retained_code_acceptance_packets"][0]
    first_criterion = contract["final_demotion_criteria"][0]
    exception_template = {
        "scope": "phase18-final-review",
        "rationale": "Describe why an exception is justified.",
        "approver": "maintainer-name",
        "approver_role": "release-maintainer",
        "affected_printer_or_release_surface": "supported-release-surface",
        "mitigation_or_follow_up": "Follow-up required before reference demotion.",
        "expiry_or_review_trigger": "before-reference-demotion",
        "evidence_refs": ["external://phase18/example-evidence"],
    }
    return {
        "decision_packet": {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        },
        "retained_code_reviews": [
            {
                "packet_id": first_packet["id"],
                "status": "pending-maintainer-review",
                "approver": "maintainer-name",
                "approver_role": first_packet["approver_role"],
                "decision_timestamp": "2026-06-20T00:00:00Z",
                "rationale": "Describe retained-code packet disposition.",
                "supplied_evidence_result_refs": ["external://phase18/example-retained-evidence"],
                "residual_risk": "Describe residual retained-code risk.",
                "blocker_or_deferred_action": "Describe required follow-up.",
                "exception_ref": "none",
                "redaction_summary": "Name-only and redacted references only.",
            }
        ],
        "final_criterion_decisions": [
            {
                "decision_id": f"decision-{first_criterion['id']}",
                "criterion_id": first_criterion["id"],
                "decision": "approve",
                "status": "pending",
                "approver": "maintainer-name",
                "approver_role": "release-maintainer",
                "decision_timestamp": "2026-06-20T00:00:00Z",
                "rationale": "Describe final criterion disposition.",
                "evidence_refs": ["external://phase18/example-final-evidence"],
                "residual_risk": "Describe residual final criterion risk.",
                "exception": exception_template,
                "redaction_summary": "Name-only and redacted references only.",
            }
        ],
    }


def redacted_report_text(
    run_manifest: dict[str, Any],
    final_results: list[dict[str, Any]],
    retained_rows: list[dict[str, Any]],
) -> str:
    lines = [
        "# Phase 18 Cutover Review",
        "",
        "Review material only; machine-readable gate rows and maintainer decision input determine final status.",
        "",
        f"phase: {PHASE}",
        f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
        f"decision_inputs_supplied: {str(run_manifest['decision_inputs_supplied']).lower()}",
        f"demotion_allowed: {str(run_manifest['demotion_allowed']).lower()}",
        "",
        "## Final Criteria",
    ]
    for row in final_results:
        lines.append(f"- {row['id']}: {row['status']} ({row['evidence_family']})")
    lines.extend(["", "## Retained Packets"])
    for row in retained_rows:
        lines.append(f"- {row['id']}: {row['status']} ({', '.join(row['taxonomy_tags'])})")
    return "\n".join(lines) + "\n"


def write_quick_artifacts(
    root: Path,
    contract: dict[str, Any],
    decision_input: dict[str, Any] | None,
    output_dir_arg: str,
) -> dict[str, Any]:
    output_dir = contained_output_dir(root, output_dir_arg)
    packets = contract_packets(contract)
    criteria = contract_final_criteria(contract)
    retained_reviews, final_decisions = validated_decision_maps(decision_input, packets, criteria)
    retained_acceptance_decision = final_decisions.get("final-retained-code-acceptance")
    if retained_acceptance_decision and final_status_allows_demotion(
        str(retained_acceptance_decision["status"]),
        retained_acceptance_decision,
    ):
        packet_ids = {str(packet["id"]) for packet in packets}
        missing_reviews = packet_ids - set(retained_reviews)
        if missing_reviews:
            raise VerificationError(
                "final-retained-code-acceptance cannot pass without retained reviews: "
                + ", ".join(sorted(missing_reviews))
            )
        bad_statuses = [
            f"{packet_id}:{review['status']}"
            for packet_id, review in sorted(retained_reviews.items())
            if review["status"] not in {"accepted", "deferred-approved-exception"}
        ]
        if bad_statuses:
            raise VerificationError("final-retained-code-acceptance has non-accepted retained reviews: " + ", ".join(bad_statuses))
    final_results = normalize_final_results(criteria, final_decisions)
    retained_rows = normalize_retained_reviews(packets, retained_reviews)
    decision_inputs_supplied = decision_input is not None
    allowed = demotion_allowed(decision_inputs_supplied, final_results)
    artifacts = generated_artifact_paths(output_dir)
    output_dir_relative = output_dir.relative_to(root)
    snapshot_relative = Path("source-contract-snapshots/phase18_cutover_review_contract.json")
    run_manifest = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": contract["artifact_name"],
        "command_mode": "quick",
        "output_root": output_dir_relative.as_posix(),
        "decision_inputs_supplied": decision_inputs_supplied,
        "demotion_allowed": allowed,
        "requirement_coverage": requirement_coverage(packets, criteria),
        "status_counts": {
            "final": count_statuses(final_results),
            "retained": count_statuses(retained_rows),
        },
        "retained_packet_status_counts": count_statuses(retained_rows),
        "final_criterion_status_counts": count_statuses(final_results),
        "source_contract_snapshot_path": (output_dir_relative / snapshot_relative).as_posix(),
        "generated_artifacts": [
            (output_dir_relative / artifact).as_posix() for artifact in sorted(REQUIRED_GENERATED_ARTIFACTS)
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifacts["normalized-final-demotion-results.json"], {"results": final_results, "demotion_allowed": allowed})
    write_json(artifacts["retained-code-acceptance-summary.json"], {"packets": retained_rows})
    write_json(artifacts["residual-risk-register.json"], {"risks": build_residual_risk_register(final_results, retained_rows)})
    write_json(artifacts["maintainer-decision-input-template.json"], decision_input_template(contract))
    snapshot_path = artifacts["source-contract-snapshots/phase18_cutover_review_contract.json"]
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / CONTRACT_MANIFEST, snapshot_path)
    write_json(artifacts["run-manifest.json"], run_manifest)
    artifacts["redacted-readiness-report.md"].write_text(
        redacted_report_text(run_manifest, final_results, retained_rows),
        encoding="utf-8",
    )
    run_security_scan(root, None, output_dir)
    return run_manifest


def generated_artifacts_to_scan(root: Path, output_dir: Path | None = None) -> list[Path]:
    scan_dir = output_dir or root / DEFAULT_OUTPUT_DIR
    paths: list[Path] = []
    for artifact in sorted(REQUIRED_GENERATED_ARTIFACTS):
        full_path = scan_dir / artifact
        if full_path.exists():
            paths.append(full_path)
    return paths


def run_security_scan(root: Path, maybe_decision_input_path: str | None, output_dir: Path | None = None) -> None:
    errors: list[str] = []
    for path in [CONTRACT_MANIFEST]:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_json_fields(load_json(root, path), path.as_posix())
        except VerificationError as error:
            errors.append(str(error))
    if maybe_decision_input_path:
        try:
            load_decision_input(root, maybe_decision_input_path)
        except VerificationError as error:
            errors.append(str(error))
    for full_path in generated_artifacts_to_scan(root, output_dir):
        relative_path = full_path.relative_to(root)
        try:
            text = full_path.read_text(encoding="utf-8")
            reject_forbidden_text(relative_path, text)
            if full_path.suffix == ".json":
                reject_forbidden_json_fields(json.loads(text), relative_path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    validate_generated_overclaim_guards(root, errors, output_dir)
    if errors:
        raise VerificationError("\n".join(errors))


def validate_generated_overclaim_guards(root: Path, errors: list[str], output_dir: Path | None = None) -> None:
    output_dir = output_dir or root / DEFAULT_OUTPUT_DIR
    run_manifest_path = output_dir / "run-manifest.json"
    if not run_manifest_path.exists():
        return
    try:
        run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"{run_manifest_path.relative_to(root).as_posix()} is not valid JSON: {error}")
        return
    if not isinstance(run_manifest, dict):
        errors.append("build/ci-evidence/phase18/run-manifest.json must contain an object")
        return
    decision_inputs_supplied = run_manifest.get("decision_inputs_supplied")
    if not isinstance(decision_inputs_supplied, bool):
        errors.append("generated run-manifest.json decision_inputs_supplied must be boolean")
        return
    if decision_inputs_supplied:
        return
    if run_manifest.get("demotion_allowed") is True:
        errors.append("generated no-decision run-manifest.json cannot set demotion_allowed true")
    normalized_path = output_dir / "normalized-final-demotion-results.json"
    if normalized_path.exists():
        try:
            normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
            results = normalized.get("results") if isinstance(normalized, dict) else None
            if isinstance(results, list):
                for row in results:
                    if isinstance(row, dict) and row.get("status") in ALLOWED_DEMOTION_STATUSES:
                        errors.append(
                            "generated no-decision normalized-final-demotion-results.json cannot set "
                            f"{row.get('id', 'unknown')} to {row.get('status')}"
                        )
        except json.JSONDecodeError as error:
            errors.append(f"{normalized_path.relative_to(root).as_posix()} is not valid JSON: {error}")
    retained_path = output_dir / "retained-code-acceptance-summary.json"
    if retained_path.exists():
        try:
            retained = json.loads(retained_path.read_text(encoding="utf-8"))
            packets = retained.get("packets") if isinstance(retained, dict) else None
            if isinstance(packets, list):
                for row in packets:
                    if isinstance(row, dict) and row.get("status") in {"accepted", "deferred-approved-exception"}:
                        errors.append(
                            "generated no-decision retained-code-acceptance-summary.json cannot set "
                            f"{row.get('id', 'unknown')} to {row.get('status')}"
                        )
        except json.JSONDecodeError as error:
            errors.append(f"{retained_path.relative_to(root).as_posix()} is not valid JSON: {error}")


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
        just_text = read_text(root, "justfile")
        recipe_index = just_text.find("phase18-verify:")
        tests_index = just_text.find("\n    bazel run //tools/bazel:phase18_verify_tests\n", recipe_index)
        verify_index = just_text.find("\n    bazel run //tools/bazel:phase18_verify\n", recipe_index)
        if recipe_index == -1 or tests_index == -1 or verify_index == -1:
            errors.append("justfile missing complete phase18-verify recipe")
        elif tests_index > verify_index:
            errors.append("justfile phase18-verify must run phase18_verify_tests before phase18_verify")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the Phase 18 retained-code cutover review contract.")
    parser.add_argument("--contract-only", action="store_true", help="validate only the Phase 18 source contract")
    parser.add_argument("--quick", action="store_true", help="write deterministic redacted Phase 18 review artifacts")
    parser.add_argument("--security-only", action="store_true", help="scan Phase 18 inputs and generated artifacts")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel, workflow, and just wiring")
    parser.add_argument("--decision-input", help="optional Phase 18 maintainer decision input JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 18 output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        contract = check_contract(ROOT)
        if args.security_only:
            output_dir = contained_output_dir(ROOT, args.output_dir)
            run_security_scan(ROOT, args.decision_input, output_dir)
            print("Phase 18 security scan passed")
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            print("Phase 18 wiring passed")
            return 0
        if args.quick:
            decision_input = load_decision_input(ROOT, args.decision_input)
            run_manifest = write_quick_artifacts(ROOT, contract, decision_input, args.output_dir)
            print(f"Phase 18 quick artifacts written; demotion_allowed={str(run_manifest['demotion_allowed']).lower()}")
            return 0
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Phase 18 cutover review contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
