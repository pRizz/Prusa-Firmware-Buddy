from __future__ import annotations

from phase27_decision_policy import *


def validate_final_decision_status(row_name: str, decision: str,
                                   status: str) -> None:
    if status == "passed" and decision != "approve":
        raise VerificationError(
            f"{row_name} status passed requires decision approve")
    if status in {"exception-approved", "not-applicable"
                  } and decision != "exception":
        raise VerificationError(
            f"{row_name} status {status} requires decision exception")
    if decision == "approve" and status != "passed":
        raise VerificationError(f"{row_name} approve requires status passed")
    if decision == "reject" and status in {
            "passed", "exception-approved", "not-applicable"
    }:
        raise VerificationError(
            f"{row_name} reject cannot use accepting status {status}")
    if decision == "exception" and status not in {
            "exception-approved", "not-applicable"
    }:
        raise VerificationError(
            f"{row_name} exception requires status exception-approved or not-applicable"
        )


def normalize_retained_decisions(
    phase18_contract: dict[str, Any],
    contract: dict[str, Any],
    maintainer_input: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    packets = phase18_retained_packets(phase18_contract)
    packet_by_id = {
        require_string(packet, "id", "Phase 18 retained packet"): packet
        for packet in packets
    }
    allowed_decisions = set(
        check_phase18_surfaces(phase18_contract)["review_decision_vocabulary"])
    allowed_hard_reasons = require_string_list(
        require_dict(contract, "hard_blocker_policy", "Phase 27 contract"),
        "reasons", "hard blocker policy")
    if maintainer_input is None:
        return [{
            "packet_id": packet_id,
            "title": packet.get("title", ""),
            "status": "pending-maintainer-review",
            "decision": "pending",
            "evidence_state": str(packet.get("status", "pending-evidence")),
            "maintainer_decision": "pending",
            "exception_state": "none",
            "residual_risk_state": "unreviewed",
            "hard_failure_state": "none",
            "hard_failure_reasons": [],
            "demotion_authorization": "blocked",
            "residual_risk": packet.get("residual_risk", ""),
            "evidence_refs": packet.get("required_evidence_refs", []),
            "source_packet": packet,
        } for packet_id, packet in packet_by_id.items()]

    rows = maintainer_input.get("retained_code_decisions")
    if not isinstance(rows, list):
        raise VerificationError(
            "maintainer input must contain retained_code_decisions list")
    parsed: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"retained_code_decisions[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        try:
            packet_id = require_string(row, "packet_id", row_name)
            if packet_id not in packet_by_id:
                raise VerificationError(
                    f"{row_name} uses unknown packet_id: {packet_id}")
            if packet_id in parsed:
                raise VerificationError(
                    f"{row_name} duplicates packet_id: {packet_id}")
            decision = require_string(row, "decision", row_name)
            if decision not in allowed_decisions:
                raise VerificationError(
                    f"{row_name} decision is invalid: {decision}")
            packet = packet_by_id[packet_id]
            hard_reasons = detect_hard_failure_reasons(row,
                                                       allowed_hard_reasons,
                                                       row_name)
            validate_decision_common(
                row,
                row_name,
                require_evidence_refs=decision in {"approve", "exception"}
                and not hard_reasons)
            expected_role = require_string(
                packet, "approver_role",
                f"Phase 18 retained packet {packet_id}")
            approver_role = require_string(row, "approver_role", row_name)
            if approver_role != expected_role:
                raise VerificationError(
                    f"{row_name} approver_role must be {expected_role}")
            maybe_exception = row.get("exception")
            exception_surface = maybe_exception.get(
                "affected_printer_or_release_surface") if isinstance(
                    maybe_exception, dict) else ""
            validate_sensitive_role(
                contract,
                subject_text(packet_id, packet.get("title"),
                             packet.get("taxonomy_tags"), exception_surface),
                approver_role,
                row_name,
            )
            maybe_exception = normalize_exception(
                row, contract, row_name
            ) if decision == "exception" and not hard_reasons else {
                "status": "none"
            }
            if hard_reasons:
                status = status_for_hard_failure(hard_reasons)
                maintainer_decision = "blocked-by-hard-failure"
                exception_state = "blocked-by-hard-failure"
                residual_risk_state = "blocked"
                hard_failure_state = "blocked"
            elif decision == "approve":
                status = "accepted"
                maintainer_decision = "accepted"
                exception_state = "none"
                residual_risk_state = "accepted-with-risk"
                hard_failure_state = "none"
            elif decision == "reject":
                status = "rejected"
                maintainer_decision = "rejected"
                exception_state = "none"
                residual_risk_state = "rejected"
                hard_failure_state = "none"
            else:
                status = "deferred-approved-exception"
                maintainer_decision = "deferred-approved-exception"
                exception_state = "approved-exception"
                residual_risk_state = "owner-assigned"
                hard_failure_state = "none"
            parsed[packet_id] = {
                "packet_id": packet_id,
                "title": packet.get("title", ""),
                "status": status,
                "decision": decision,
                "approver": row["approver"],
                "approver_role": row["approver_role"],
                "decision_timestamp": row["decision_timestamp"],
                "rationale": row["rationale"],
                "evidence_refs": row["evidence_refs"],
                "redaction_summary": row["redaction_summary"],
                "evidence_state": "linked",
                "maintainer_decision": maintainer_decision,
                "exception_state": exception_state,
                "residual_risk_state": residual_risk_state,
                "hard_failure_state": hard_failure_state,
                "hard_failure_reasons": hard_reasons,
                "demotion_authorization": "blocked",
                "residual_risk": row["residual_risk"],
                "exception": maybe_exception,
                "source_packet": packet,
            }
        except VerificationError as error:
            errors.append(str(error))
    missing = [
        packet_id for packet_id in packet_by_id if packet_id not in parsed
    ]
    if missing:
        errors.append("maintainer input missing retained packet decisions: " +
                      ", ".join(missing))
    if errors:
        raise VerificationError("\n".join(errors))
    return [parsed[packet_id] for packet_id in packet_by_id]


def phase26_rows_by_id(
        rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        require_string(row, "criterion_id", "Phase 26 row"): row
        for row in rows
    }


def normalize_default_final_decisions(
    phase18_contract: dict[str, Any],
    phase26_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    upstream_by_id = phase26_rows_by_id(phase26_rows)
    final_rows: list[dict[str, Any]] = []
    for requirement in phase18_upstream_requirements(phase18_contract):
        criterion_id = require_string(requirement, "criterion_id",
                                      "Phase 18 upstream requirement")
        upstream_row = upstream_by_id[criterion_id]
        status = str(upstream_row.get("status", "blocked"))
        if criterion_id in {
                "final-retained-code-acceptance", "final-maintainer-decision",
                "final-reference-demotion-allowed"
        }:
            status = "blocked" if criterion_id != "final-maintainer-decision" else "pending"
        final_rows.append({
            "decision_id":
            f"phase27-final-readiness-{criterion_id}",
            "criterion_id":
            criterion_id,
            "decision":
            "pending",
            "status":
            status,
            "approver":
            "",
            "approver_role":
            "",
            "decision_timestamp":
            "",
            "rationale":
            upstream_row.get("failure_reason",
                             "Pending maintainer final readiness decision."),
            "evidence_refs":
            upstream_row.get("evidence_refs", []),
            "artifact_refs":
            upstream_row.get("artifact_refs", []),
            "residual_risk":
            "Pending Phase 27 maintainer decision input.",
            "exception": {
                "status": "none"
            },
            "redaction_summary":
            f"redaction_status={upstream_row.get('redaction_status', 'unknown')}",
            "evidence_state":
            status,
            "maintainer_decision":
            "pending",
            "exception_state":
            "none",
            "residual_risk_state":
            "unreviewed",
            "hard_failure_state":
            "none",
            "hard_failure_reasons": [],
            "demotion_authorization":
            "blocked",
        })
    return final_rows


def normalize_final_decisions(
    phase18_contract: dict[str, Any],
    contract: dict[str, Any],
    phase26_rows: list[dict[str, Any]],
    maintainer_input: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if maintainer_input is None:
        return normalize_default_final_decisions(phase18_contract,
                                                 phase26_rows)
    surfaces = check_phase18_surfaces(phase18_contract)
    requirements = phase18_upstream_requirements(phase18_contract)
    requirement_by_id = {
        require_string(requirement, "criterion_id", "Phase 18 upstream requirement"):
        requirement
        for requirement in requirements
    }
    upstream_by_id = phase26_rows_by_id(phase26_rows)
    allowed_decisions = set(surfaces["review_decision_vocabulary"])
    allowed_statuses = set(surfaces["final_criterion_status_vocabulary"])
    allowed_hard_reasons = require_string_list(
        require_dict(contract, "hard_blocker_policy", "Phase 27 contract"),
        "reasons", "hard blocker policy")
    rows = maintainer_input.get("final_readiness_decisions")
    if not isinstance(rows, list):
        raise VerificationError(
            "maintainer input must contain final_readiness_decisions list")
    parsed: dict[str, dict[str, Any]] = {}
    decision_ids: set[str] = set()
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"final_readiness_decisions[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        try:
            missing = [
                field for field in surfaces["final_decision_required_fields"]
                if field not in row
            ]
            if missing:
                raise VerificationError(
                    f"{row_name} missing required final decision fields: {', '.join(missing)}"
                )
            criterion_id = require_string(row, "criterion_id", row_name)
            decision_id = require_string(row, "decision_id", row_name)
            if decision_id in decision_ids:
                raise VerificationError(
                    f"{row_name} duplicate decision_id: {decision_id}")
            decision_ids.add(decision_id)
            if criterion_id not in requirement_by_id:
                raise VerificationError(
                    f"{row_name} uses unknown criterion_id: {criterion_id}")
            if criterion_id in parsed:
                raise VerificationError(
                    f"{row_name} duplicates criterion_id: {criterion_id}")
            decision = require_string(row, "decision", row_name)
            status = require_string(row, "status", row_name)
            if decision not in allowed_decisions:
                raise VerificationError(
                    f"{row_name} decision is invalid: {decision}")
            if status not in allowed_statuses:
                raise VerificationError(
                    f"{row_name} status is invalid: {status}")
            validate_final_decision_status(row_name, decision, status)
            if criterion_id == "final-reference-demotion-allowed" and (
                    decision == "approve"
                    or status in {"passed", "exception-approved"}):
                raise VerificationError(
                    f"{row_name} cannot approve reference demotion in Phase 27"
                )
            upstream_row = upstream_by_id[criterion_id]
            hard_reasons = detect_hard_failure_reasons(upstream_row,
                                                       allowed_hard_reasons,
                                                       row_name)
            hard_reasons.extend(reason
                                for reason in detect_hard_failure_reasons(
                                    row, allowed_hard_reasons, row_name)
                                if reason not in hard_reasons)
            validate_decision_common(
                row,
                row_name,
                require_status=True,
                require_evidence_refs=status
                in {"passed", "exception-approved", "not-applicable"}
                and not hard_reasons,
            )
            validate_sensitive_role(
                contract,
                subject_text(
                    criterion_id,
                    requirement_by_id[criterion_id].get("evidence_family"),
                    row.get("rationale")),
                require_string(row, "approver_role", row_name),
                row_name,
            )
            maybe_exception = normalize_exception(
                row, contract, row_name
            ) if decision == "exception" and not hard_reasons else {
                "status": "none"
            }
            if hard_reasons:
                normalized_status = status_for_hard_failure(hard_reasons)
                maintainer_decision = "blocked-by-hard-failure"
                exception_state = "blocked-by-hard-failure"
                residual_risk_state = "blocked"
                hard_failure_state = "blocked"
            elif decision == "approve":
                normalized_status = status
                maintainer_decision = "accepted"
                exception_state = "none"
                residual_risk_state = "accepted-with-risk"
                hard_failure_state = "none"
            elif decision == "reject":
                normalized_status = status
                maintainer_decision = "rejected"
                exception_state = "none"
                residual_risk_state = "rejected"
                hard_failure_state = "none"
            else:
                normalized_status = "exception-approved"
                maintainer_decision = "deferred-approved-exception"
                exception_state = "approved-exception"
                residual_risk_state = "owner-assigned"
                hard_failure_state = "none"
            parsed[criterion_id] = {
                "decision_id": decision_id,
                "criterion_id": criterion_id,
                "decision": decision,
                "status": normalized_status,
                "approver": row["approver"],
                "approver_role": row["approver_role"],
                "decision_timestamp": row["decision_timestamp"],
                "rationale": row["rationale"],
                "evidence_refs": row["evidence_refs"],
                "artifact_refs": upstream_row.get("artifact_refs", []),
                "residual_risk": row["residual_risk"],
                "exception": maybe_exception,
                "redaction_summary": row["redaction_summary"],
                "evidence_state": str(upstream_row.get("status", "unknown")),
                "maintainer_decision": maintainer_decision,
                "exception_state": exception_state,
                "residual_risk_state": residual_risk_state,
                "hard_failure_state": hard_failure_state,
                "hard_failure_reasons": hard_reasons,
                "demotion_authorization": "blocked",
            }
        except VerificationError as error:
            errors.append(str(error))
    missing = [
        criterion_id for criterion_id in requirement_by_id
        if criterion_id not in parsed
    ]
    if missing:
        errors.append("maintainer input missing final readiness decisions: " +
                      ", ".join(missing))
    if errors:
        raise VerificationError("\n".join(errors))
    return [parsed[criterion_id] for criterion_id in requirement_by_id]
