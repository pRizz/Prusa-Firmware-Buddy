from __future__ import annotations

from phase18_cutover_contract import *
from phase18_cutover_validation import *


def check_contract(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    validate_schema(contract, errors)
    try:
        packets = contract_packets(contract)
        final_criteria = contract_final_criteria(contract)
        upstream_requirements = contract_upstream_requirements(contract)
        packet_ids = validate_packets(root, packets, errors)
        validate_final_criteria(root, final_criteria, packet_ids, errors)
        validate_upstream_result_requirements(upstream_requirements,
                                              final_criteria, errors)
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def load_decision_input(root: Path,
                        maybe_path: str | None) -> dict[str, Any] | None:
    if not maybe_path:
        return None
    input_path = require_repo_relative(maybe_path, "--decision-input")
    raw_text = read_text(root, input_path)
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{input_path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(
            "--decision-input must contain a top-level object")
    reject_forbidden_json_fields(data, input_path.as_posix())
    packet = data.get("decision_packet")
    if not isinstance(packet, dict):
        raise VerificationError(
            "decision_packet must be present and must be an object")
    if packet.get("phase") != PHASE:
        raise VerificationError(f"decision_packet phase must be {PHASE}")
    if packet.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"decision_packet phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
    if "retained_code_reviews" not in data:
        data["retained_code_reviews"] = []
    if "final_criterion_decisions" not in data:
        data["final_criterion_decisions"] = []
    if not isinstance(data["retained_code_reviews"], list):
        raise VerificationError("retained_code_reviews must be a list")
    if not isinstance(data["final_criterion_decisions"], list):
        raise VerificationError("final_criterion_decisions must be a list")
    return data


def load_upstream_results(root: Path,
                          maybe_path: str | None) -> dict[str, Any] | None:
    if not maybe_path:
        return None
    input_path = require_repo_relative(maybe_path, "--upstream-results")
    raw_text = read_text(root, input_path)
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{input_path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(
            "--upstream-results must contain a top-level object")
    reject_forbidden_json_fields(data, input_path.as_posix())
    packet = data.get("upstream_result_packet")
    if not isinstance(packet, dict):
        raise VerificationError(
            "upstream_result_packet must be present and must be an object")
    if packet.get("phase") != PHASE:
        raise VerificationError(
            f"upstream_result_packet phase must be {PHASE}")
    if packet.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"upstream_result_packet phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
        )
    if "upstream_results" not in data:
        data["upstream_results"] = []
    if not isinstance(data["upstream_results"], list):
        raise VerificationError("upstream_results must be a list")
    return data


def validate_exception_metadata(exception: Any,
                                row_name: str) -> dict[str, Any]:
    if not isinstance(exception, dict):
        raise VerificationError(f"{row_name} exception must be an object")
    require_fields(exception, EXCEPTION_REQUIRED_FIELDS,
                   f"{row_name} exception")
    for field in EXCEPTION_REQUIRED_FIELDS:
        if field == "evidence_refs":
            continue
        require_string(exception, field, f"{row_name} exception")
    evidence_refs = require_list_of_strings(exception, "evidence_refs",
                                            f"{row_name} exception")
    require_non_empty_refs(evidence_refs, f"{row_name} exception",
                           "evidence_refs")
    for ref in evidence_refs:
        require_phase18_artifact_ref(ref,
                                     f"{row_name} exception evidence_refs")
    return exception


def require_non_empty_refs(refs: list[str], row_name: str, field: str) -> None:
    if not refs:
        raise VerificationError(
            f"{row_name} {field} must include at least one Phase 18 evidence ref"
        )


def criterion_allows_status(criterion: dict[str, Any], status: str) -> bool:
    allowed_statuses = criterion.get("allowed_statuses")
    if not isinstance(allowed_statuses,
                      list) or status not in allowed_statuses:
        return False
    if criterion.get("exception_allowed"
                     ) is not True and status in EXCEPTION_POLICY_STATUSES:
        return False
    return True


def validate_final_decision(row: Any, criteria_by_id: dict[str, dict[str,
                                                                     Any]],
                            row_index: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise VerificationError(
            f"final_criterion_decisions[{row_index}] must be an object")
    row_name = str(
        row.get("criterion_id", f"final_criterion_decisions[{row_index}]"))
    require_fields(row, FINAL_DECISION_REQUIRED_FIELDS, row_name)
    require_string(row, "decision_id", row_name)
    criterion_id = require_string(row, "criterion_id", row_name)
    criterion = criteria_by_id.get(criterion_id)
    if criterion is None:
        raise VerificationError(
            f"{row_name} criterion_id does not resolve: {criterion_id}")
    decision = require_string(row, "decision", row_name)
    status = require_string(row, "status", row_name)
    if decision not in REVIEW_DECISION_VOCABULARY:
        raise VerificationError(f"{row_name} decision is invalid: {decision}")
    if status not in FINAL_CRITERION_STATUS_VOCABULARY:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    if not criterion_allows_status(criterion, status):
        raise VerificationError(
            f"{row_name} status {status} is not allowed by criterion policy")
    require_string(row, "approver", row_name)
    require_string(row, "approver_role", row_name)
    require_iso_utc(require_string(row, "decision_timestamp", row_name),
                    row_name)
    require_string(row, "rationale", row_name)
    evidence_refs = require_list_of_strings(row, "evidence_refs", row_name)
    for ref in evidence_refs:
        require_phase18_artifact_ref(ref, f"{row_name} evidence_refs")
    require_string(row, "residual_risk", row_name)
    require_string(row, "redaction_summary", row_name)
    if status == "passed":
        if decision != "approve":
            raise VerificationError(
                f"{row_name} status passed requires decision approve")
        require_non_empty_refs(evidence_refs, row_name, "evidence_refs")
    elif status in {"exception-approved", "not-applicable"}:
        if decision != "exception":
            raise VerificationError(
                f"{row_name} status {status} requires decision exception")
        require_non_empty_refs(evidence_refs, row_name, "evidence_refs")
        validate_exception_metadata(row["exception"], row_name)
    elif not isinstance(row.get("exception"), dict):
        raise VerificationError(f"{row_name} exception must be an object")
    return row


def validate_retained_review(row: Any, packets_by_id: dict[str, dict[str,
                                                                     Any]],
                             row_index: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise VerificationError(
            f"retained_code_reviews[{row_index}] must be an object")
    row_name = str(row.get("packet_id", f"retained_code_reviews[{row_index}]"))
    require_fields(row, REQUIRED_RETAINED_REVIEW_FIELDS, row_name)
    packet_id = require_string(row, "packet_id", row_name)
    packet = packets_by_id.get(packet_id)
    if packet is None:
        raise VerificationError(
            f"{row_name} packet_id does not resolve: {packet_id}")
    status = require_string(row, "status", row_name)
    if status not in RETAINED_PACKET_STATUS_VOCABULARY:
        raise VerificationError(f"{row_name} status is invalid: {status}")
    require_string(row, "approver", row_name)
    approver_role = require_string(row, "approver_role", row_name)
    expected_role = require_string(packet, "approver_role", packet_id)
    if approver_role != expected_role:
        raise VerificationError(
            f"{row_name} approver_role must be {expected_role}")
    require_iso_utc(require_string(row, "decision_timestamp", row_name),
                    row_name)
    require_string(row, "rationale", row_name)
    supplied_refs = require_list_of_strings(row,
                                            "supplied_evidence_result_refs",
                                            row_name)
    for ref in supplied_refs:
        require_phase18_artifact_ref(
            ref, f"{row_name} supplied_evidence_result_refs")
    require_string(row, "residual_risk", row_name)
    require_string(row, "blocker_or_deferred_action", row_name)
    require_string(row, "exception_ref", row_name)
    require_string(row, "redaction_summary", row_name)
    if status in {"accepted", "deferred-approved-exception"}:
        require_non_empty_refs(supplied_refs, row_name,
                               "supplied_evidence_result_refs")
    if status == "deferred-approved-exception":
        if row["exception_ref"] == "none" or row[
                "blocker_or_deferred_action"] == "none":
            raise VerificationError(
                f"{row_name} deferred-approved-exception requires exception_ref and blocker action"
            )
    if status in {
            "rejected", "blocked", "rejected-redaction", "rejected-overclaim"
    }:
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
    criteria_by_id = {str(row["id"]): row for row in criteria}
    criterion_ids = set(criteria_by_id)
    packets_by_id = {str(row["id"]): row for row in packets}
    final_decisions: dict[str, dict[str, Any]] = {}
    retained_reviews: dict[str, dict[str, Any]] = {}
    final_decision_ids: set[str] = set()
    for index, row in enumerate(decision_input["final_criterion_decisions"]):
        decision = validate_final_decision(row, criteria_by_id, index)
        decision_id = str(decision["decision_id"])
        if decision_id in final_decision_ids:
            raise VerificationError(
                f"duplicate final decision id: {decision_id}")
        final_decision_ids.add(decision_id)
        criterion_id = str(decision["criterion_id"])
        if criterion_id in final_decisions:
            raise VerificationError(
                f"duplicate final criterion decision: {criterion_id}")
        final_decisions[criterion_id] = decision
    for index, row in enumerate(decision_input["retained_code_reviews"]):
        review = validate_retained_review(row, packets_by_id, index)
        packet_id = str(review["packet_id"])
        if packet_id in retained_reviews:
            raise VerificationError(
                f"duplicate retained code review: {packet_id}")
        retained_reviews[packet_id] = review
    if final_decisions and set(final_decisions) != criterion_ids:
        missing = ", ".join(sorted(criterion_ids - set(final_decisions)))
        raise VerificationError(
            "decision input missing final criterion decisions: " + missing)
    if retained_reviews and set(retained_reviews) != set(packets_by_id):
        missing = ", ".join(sorted(set(packets_by_id) - set(retained_reviews)))
        raise VerificationError(
            "decision input missing retained code reviews: " + missing)
    return retained_reviews, final_decisions


def has_non_empty_evidence_refs(decision: dict[str, Any]) -> bool:
    refs = decision.get("evidence_refs")
    return isinstance(refs, list) and bool(refs) and all(
        isinstance(ref, str) and ref for ref in refs)


def has_complete_exception_metadata(decision: dict[str, Any]) -> bool:
    try:
        validate_exception_metadata(
            decision.get("exception"),
            str(decision.get("criterion_id", "criterion")))
    except VerificationError:
        return False
    return True


def valid_not_applicable(decision: dict[str, Any]) -> bool:
    if decision.get("status") != "not-applicable":
        return False
    if decision.get("decision") != "exception":
        return False
    if not decision.get("rationale") or not has_non_empty_evidence_refs(
            decision):
        return False
    return has_complete_exception_metadata(decision)


def final_status_allows_demotion(
    status: str,
    maybe_decision: dict[str, Any] | None,
    criterion: dict[str, Any] | None = None,
) -> bool:
    if maybe_decision is None or maybe_decision.get("status") != status:
        return False
    if criterion is not None and not criterion_allows_status(
            criterion, status):
        return False
    if status == "passed":
        return maybe_decision.get(
            "decision") == "approve" and has_non_empty_evidence_refs(
                maybe_decision)
    if status == "exception-approved":
        return (maybe_decision.get("decision") == "exception"
                and has_non_empty_evidence_refs(maybe_decision)
                and has_complete_exception_metadata(maybe_decision))
    if status == "not-applicable":
        return valid_not_applicable(maybe_decision)
    return False


def demotion_allowed(
    decision_inputs_supplied: bool,
    upstream_results_supplied: bool,
    normalized_results: list[dict[str, Any]],
) -> bool:
    if not decision_inputs_supplied:
        return False
    if not upstream_results_supplied:
        return False
    return all(
        bool(row["demotion_status_allows_cutover"])
        for row in normalized_results)


def validate_retained_acceptance_consistency(
    packets: list[dict[str, Any]],
    retained_reviews: dict[str, dict[str, Any]],
    final_decisions: dict[str, dict[str, Any]],
) -> None:
    retained_acceptance_decision = final_decisions.get(
        "final-retained-code-acceptance")
    if not retained_acceptance_decision or not final_status_allows_demotion(
            str(retained_acceptance_decision["status"]),
            retained_acceptance_decision,
    ):
        return
    packet_ids = {str(packet["id"]) for packet in packets}
    missing_reviews = packet_ids - set(retained_reviews)
    if missing_reviews:
        raise VerificationError(
            "final-retained-code-acceptance cannot pass without retained reviews: "
            + ", ".join(sorted(missing_reviews)))
    bad_statuses = [
        f"{packet_id}:{review['status']}"
        for packet_id, review in sorted(retained_reviews.items())
        if review["status"] not in {"accepted", "deferred-approved-exception"}
    ]
    if bad_statuses:
        raise VerificationError(
            "final-retained-code-acceptance has non-accepted retained reviews: "
            + ", ".join(bad_statuses))


def generated_artifact_paths(output_dir: Path) -> dict[str, Path]:
    return {
        artifact: output_dir / artifact
        for artifact in sorted(REQUIRED_GENERATED_ARTIFACTS)
    }
