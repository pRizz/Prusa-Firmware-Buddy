#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the Phase 18 retained-code cutover review contract.")
    parser.add_argument("--contract-only", action="store_true", help="validate only the Phase 18 source contract")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    parse_args(argv or sys.argv[1:])
    try:
        check_contract(ROOT)
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Phase 18 cutover review contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
