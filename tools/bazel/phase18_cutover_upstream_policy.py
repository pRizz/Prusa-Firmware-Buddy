from __future__ import annotations

from phase18_cutover_contract import *
from phase18_cutover_policy import *
from phase18_cutover_validation import *


def requirements_by_criterion(
        contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row["criterion_id"]): row
        for row in contract_upstream_requirements(contract)
    }


def upstream_manifest_ref(row: dict[str, Any], row_name: str) -> str:
    manifest_path = row.get("manifest_path")
    external_ref = row.get("external_ref")
    if isinstance(manifest_path, str) and manifest_path:
        if isinstance(external_ref, str) and external_ref:
            raise VerificationError(
                f"{row_name} must use either manifest_path or external_ref, not both"
            )
        return manifest_path
    if isinstance(external_ref, str) and external_ref:
        return external_ref
    raise VerificationError(
        f"{row_name} must include manifest_path or external_ref")


def validate_upstream_result_row(
    row: Any,
    row_index: int,
    criteria_by_id: dict[str, dict[str, Any]],
    upstream_requirements: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise VerificationError(
            f"upstream_results[{row_index}] must be an object")
    row_name = str(row.get("criterion_id", f"upstream_results[{row_index}]"))
    require_fields(row, UPSTREAM_RESULT_ROW_REQUIRED_FIELDS, row_name)
    criterion_id = require_string(row, "criterion_id", row_name)
    criterion = criteria_by_id.get(criterion_id)
    if criterion is None:
        raise VerificationError(
            f"{row_name} criterion_id does not resolve: {criterion_id}")
    requirement = upstream_requirements.get(criterion_id)
    if requirement is None:
        raise VerificationError(
            f"{row_name} upstream result requirement does not resolve: {criterion_id}"
        )
    evidence_family = require_string(row, "evidence_family", row_name)
    if evidence_family != criterion[
            "evidence_family"] or evidence_family != requirement[
                "evidence_family"]:
        raise VerificationError(
            f"{row_name} evidence_family must match final criterion")
    owning_phase = require_string(row, "owning_phase", row_name)
    if owning_phase != requirement["source_phase"]:
        raise VerificationError(
            f"{row_name} owning_phase must be {requirement['source_phase']}")
    source_lifecycle_id = require_string(row, "source_lifecycle_id", row_name)
    if source_lifecycle_id != requirement["source_lifecycle_id"]:
        raise VerificationError(
            f"{row_name} source_lifecycle_id must be {requirement['source_lifecycle_id']}"
        )
    status = require_string(row, "status", row_name)
    if status not in UPSTREAM_RESULT_STATUS_VOCABULARY:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    require_string(row, "failure_reason", row_name)
    require_iso_utc(require_string(row, "generated_at_utc", row_name),
                    row_name)
    require_list_of_strings(row, "requirement_ids", row_name)
    artifact_refs = require_list_of_strings(row, "artifact_refs", row_name)
    approved_roots = require_list_of_strings(requirement, "approved_ref_roots",
                                             f"{row_name} requirement")
    manifest_ref = upstream_manifest_ref(row, row_name)
    require_upstream_artifact_ref(manifest_ref, approved_roots,
                                  f"{row_name} manifest_ref")
    for artifact_ref in artifact_refs:
        require_upstream_artifact_ref(artifact_ref, approved_roots,
                                      f"{row_name} artifact_refs")
    redaction_status = require_string(row, "redaction_status", row_name)
    source_ref_status = require_string(row, "source_ref_status", row_name)
    normalized = dict(row)
    normalized["manifest_ref"] = manifest_ref
    normalized[
        "upstream_status_allows_cutover"] = upstream_row_status_allows_cutover(
            normalized, requirement, None)
    normalized["upstream_blocking_reasons"] = upstream_row_blocking_reasons(
        normalized, requirement, None)
    if redaction_status != "passed":
        normalized["upstream_status_allows_cutover"] = False
    if source_ref_status != "passed":
        normalized["upstream_status_allows_cutover"] = False
    return normalized


def validated_upstream_result_rows(
    upstream_results: dict[str, Any] | None,
    criteria: list[dict[str, Any]],
    upstream_requirements: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    rows_by_criterion = {str(criterion["id"]): [] for criterion in criteria}
    if upstream_results is None:
        return rows_by_criterion
    criteria_by_id = {
        str(criterion["id"]): criterion
        for criterion in criteria
    }
    seen_manifest_refs: set[tuple[str, str]] = set()
    for index, row in enumerate(upstream_results["upstream_results"]):
        normalized = validate_upstream_result_row(row, index, criteria_by_id,
                                                  upstream_requirements)
        key = (str(normalized["criterion_id"]),
               str(normalized["manifest_ref"]))
        if key in seen_manifest_refs:
            raise VerificationError(
                f"duplicate upstream result row: {key[0]} {key[1]}")
        seen_manifest_refs.add(key)
        rows_by_criterion[str(normalized["criterion_id"])].append(normalized)
    return rows_by_criterion


def upstream_exception_ref(criterion_id: str) -> str:
    return f"build/ci-evidence/phase18/upstream-result-consumption.json#{criterion_id}"


def decision_exception_covers_upstream_result(
    maybe_decision: dict[str, Any] | None,
    requirement: dict[str, Any],
    row: dict[str, Any],
) -> bool:
    if maybe_decision is None or maybe_decision.get(
            "status") != "exception-approved":
        return False
    status = str(row["status"])
    if status not in set(requirement.get("exception_coverable_statuses", [])):
        return False
    if status in set(requirement.get("hard_blocking_statuses", [])):
        return False
    if row.get("redaction_status") != "passed" or row.get(
            "source_ref_status") != "passed":
        return False
    exception = maybe_decision.get("exception")
    if not isinstance(exception, dict):
        return False
    evidence_refs = exception.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        return False
    expected_ref = upstream_exception_ref(str(row["criterion_id"]))
    return any(
        isinstance(ref, str) and ref == expected_ref for ref in evidence_refs)


def upstream_row_blocking_reasons(
    row: dict[str, Any],
    requirement: dict[str, Any],
    maybe_decision: dict[str, Any] | None,
) -> list[str]:
    reasons: list[str] = []
    status = str(row["status"])
    if row.get("redaction_status") != "passed":
        reasons.append(
            f"{row['criterion_id']} upstream redaction_status {row.get('redaction_status')} blocks reference demotion"
        )
    if row.get("source_ref_status") != "passed":
        reasons.append(
            f"{row['criterion_id']} upstream source_ref_status {row.get('source_ref_status')} blocks reference demotion"
        )
    if status in set(requirement.get("hard_blocking_statuses", [])):
        reasons.append(
            f"{row['criterion_id']} upstream status {status} is a hard blocker"
        )
    elif status in set(requirement.get("acceptable_statuses", [])):
        return reasons
    elif decision_exception_covers_upstream_result(maybe_decision, requirement,
                                                   row):
        return reasons
    else:
        reasons.append(
            f"{row['criterion_id']} upstream status {status} blocks reference demotion"
        )
    return reasons


def upstream_row_status_allows_cutover(
    row: dict[str, Any],
    requirement: dict[str, Any],
    maybe_decision: dict[str, Any] | None,
) -> bool:
    return not upstream_row_blocking_reasons(row, requirement, maybe_decision)


def synthetic_upstream_consumption_row(
    criterion: dict[str, Any],
    requirement: dict[str, Any],
    status: str,
    reason: str,
) -> dict[str, Any]:
    criterion_id = str(criterion["id"])
    allows = status in set(requirement.get("acceptable_statuses", []))
    blocking_reasons = [] if allows else [f"{criterion_id} {reason}"]
    manifest_refs = list(requirement["required_manifest_refs"])
    return {
        "criterion_id": criterion_id,
        "evidence_family": criterion["evidence_family"],
        "owning_phase": requirement["source_phase"],
        "source_lifecycle_id": requirement["source_lifecycle_id"],
        "manifest_ref": manifest_refs[0],
        "status": status,
        "failure_reason": reason,
        "artifact_refs": manifest_refs,
        "redaction_status": "passed",
        "source_ref_status": "passed",
        "generated_at_utc": "2026-06-21T00:00:00Z",
        "requirement_ids": requirement["requirement_ids"],
        "upstream_status_allows_cutover": allows,
        "upstream_blocking_reasons": blocking_reasons,
    }


def normalize_upstream_consumption(
    criteria: list[dict[str, Any]],
    upstream_results: dict[str, Any] | None,
    upstream_requirements: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    input_rows = validated_upstream_result_rows(upstream_results, criteria,
                                                upstream_requirements)
    consumption: dict[str, dict[str, Any]] = {}
    for criterion in criteria:
        criterion_id = str(criterion["id"])
        requirement = upstream_requirements[criterion_id]
        rows = input_rows.get(criterion_id, [])
        if not rows and requirement["result_required"] is False:
            rows = [
                synthetic_upstream_consumption_row(
                    criterion, requirement, "not-required",
                    "decision-owned upstream result not required")
            ]
        elif not rows:
            rows = [
                synthetic_upstream_consumption_row(
                    criterion, requirement, "missing",
                    "upstream result evidence is missing")
            ]
        maybe_decision = decisions.get(criterion_id)
        normalized_rows: list[dict[str, Any]] = []
        for row in rows:
            normalized_row = dict(row)
            blocking_reasons = upstream_row_blocking_reasons(
                normalized_row, requirement, maybe_decision)
            normalized_row[
                "upstream_status_allows_cutover"] = not blocking_reasons
            normalized_row["upstream_blocking_reasons"] = blocking_reasons
            normalized_rows.append(normalized_row)
        upstream_allows = all(
            bool(row["upstream_status_allows_cutover"])
            for row in normalized_rows)
        if upstream_allows:
            aggregate_status = "not-required" if all(
                row["status"] == "not-required"
                for row in normalized_rows) else "passed"
        elif any(row["status"] == "missing" for row in normalized_rows):
            aggregate_status = "missing"
        else:
            aggregate_status = str(normalized_rows[0]["status"])
        consumption[criterion_id] = {
            "criterion_id":
            criterion_id,
            "evidence_family":
            criterion["evidence_family"],
            "result_required":
            requirement["result_required"],
            "status":
            aggregate_status,
            "upstream_result_status":
            aggregate_status,
            "upstream_result_refs":
            [str(row["manifest_ref"]) for row in normalized_rows],
            "upstream_artifact_refs": [
                artifact_ref for row in normalized_rows
                for artifact_ref in row.get("artifact_refs", [])
            ],
            "upstream_blocking_reasons": [
                reason for row in normalized_rows
                for reason in row.get("upstream_blocking_reasons", [])
            ],
            "upstream_status_allows_cutover":
            upstream_allows,
            "rows":
            normalized_rows,
        }
    return consumption
