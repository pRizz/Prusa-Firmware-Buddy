from __future__ import annotations


def validate_decision_targets(
    decision_id: str,
    decision_type: str,
    raw_targets: Any,
    source_row_refs: list[str],
    row_map: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    raw_target_list = require_list(raw_targets,
                                   f"{decision_id}.decision_targets")
    if not raw_target_list:
        raise VerificationError(
            f"{decision_id}.decision_targets must contain at least one entry")
    expected_axis = DECISION_TYPE_AXES[decision_type]
    targets: list[dict[str, str]] = []
    source_rows: list[dict[str, Any]] = []
    seen_refs: set[str] = set()
    seen_triples: set[tuple[str, str, str]] = set()
    for index, raw_target in enumerate(raw_target_list):
        target = require_dict(raw_target,
                              f"{decision_id}.decision_targets[{index}]")
        target_values: dict[str, str] = {}
        for field in REQUIRED_DECISION_TARGET_FIELDS:
            target_values[field] = require_string(
                target.get(field),
                f"{decision_id}.decision_targets[{index}].{field}",
            )
        row_ref = target_values["row_ref"]
        triple = tuple(target_values[field]
                       for field in REQUIRED_DECISION_TARGET_FIELDS)
        if triple in seen_triples:
            raise VerificationError(
                f"{decision_id} contains duplicate decision target triple: {triple}"
            )
        seen_triples.add(triple)
        if row_ref in seen_refs:
            raise VerificationError(
                f"{decision_id} contains duplicate decision target row_ref: {row_ref}"
            )
        seen_refs.add(row_ref)

        row_id = source_ref_row_id(
            row_ref,
            f"{decision_id}.decision_targets[{index}].row_ref",
        )
        maybe_row = row_map.get(row_id)
        if maybe_row is None:
            raise VerificationError(
                f"{decision_id} decision target row mismatch: {row_ref}")
        canonical_axis = require_string(
            maybe_row.get("decision_axis"),
            f"Phase 32 row {row_id}.decision_axis",
        )
        canonical_subject = require_string(
            maybe_row.get("decision_subject_id"),
            f"Phase 32 row {row_id}.decision_subject_id",
        )
        if target_values["decision_axis"] != expected_axis:
            raise VerificationError(
                f"{decision_id} decision target axis mismatch for {row_ref}: "
                f"expected {expected_axis}, got {target_values['decision_axis']}"
            )
        if target_values["decision_axis"] != canonical_axis:
            raise VerificationError(
                f"{decision_id} decision target axis mismatch for {row_ref}: "
                f"canonical Phase 32 axis is {canonical_axis}")
        if target_values["decision_subject_id"] != canonical_subject:
            raise VerificationError(
                f"{decision_id} decision target subject mismatch for {row_ref}: "
                f"canonical Phase 32 subject is {canonical_subject}")
        targets.append(target_values)
        source_rows.append(maybe_row)

    projected_refs = [target["row_ref"] for target in targets]
    if source_row_refs != projected_refs:
        raise VerificationError(
            f"{decision_id}.source_row_refs must exactly project decision_targets[*].row_ref"
        )
    return targets, source_rows


def validate_decision(raw_decision: dict[str, Any],
                      row_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    decision_id = require_string(raw_decision.get("decision_id"),
                                 "decision_id")
    for field in REQUIRED_DECISION_FIELDS:
        if field not in raw_decision:
            raise VerificationError(
                f"{decision_id} missing required field: {field}")
    decision_type = require_string(raw_decision.get("decision_type"),
                                   f"{decision_id}.decision_type")
    if decision_type not in DECISION_VALUE_ENUMS:
        raise VerificationError(
            f"{decision_id} unknown decision_type: {decision_type}")
    decision_value = require_string(raw_decision.get("decision_value"),
                                    f"{decision_id}.decision_value")
    if decision_value not in DECISION_VALUE_ENUMS[decision_type]:
        raise VerificationError(
            f"{decision_id} invalid decision_value for {decision_type}: {decision_value}"
        )
    source_row_refs = require_non_empty_string_list(
        raw_decision.get("source_row_refs"), f"{decision_id}.source_row_refs")
    decision_targets, source_rows = validate_decision_targets(
        decision_id,
        decision_type,
        raw_decision.get("decision_targets"),
        source_row_refs,
        row_map,
    )
    for field in ("maintainer_identity_ref", "maintainer_role",
                  "owner_signoff_ref", "rationale"):
        require_string(raw_decision.get(field), f"{decision_id}.{field}")
    require_iso_utc(
        require_string(raw_decision.get("decision_timestamp"),
                       f"{decision_id}.decision_timestamp"),
        f"{decision_id}.decision_timestamp")
    for field in ("evidence_refs", "artifact_refs"):
        refs = require_string_list(raw_decision.get(field),
                                   f"{decision_id}.{field}")
        for ref in refs:
            validate_reference_text(ref, f"{decision_id}.{field}")
    decision = dict(raw_decision)
    decision["decision_id"] = decision_id
    decision["decision_type"] = decision_type
    decision["decision_value"] = decision_value
    decision["decision_targets"] = decision_targets
    decision["source_row_refs"] = source_row_refs
    decision["source_rows"] = source_rows
    validate_axis_specific_decision(decision, row_map)
    return decision


def validate_axis_specific_decision(
        decision: dict[str, Any], row_map: dict[str, dict[str, Any]]) -> None:
    decision_id = str(decision["decision_id"])
    decision_type = str(decision["decision_type"])
    decision_value = str(decision["decision_value"])
    source_rows = list(decision["source_rows"])
    validate_decision_axis_rows(decision_id, decision_type, source_rows)
    if decision_value in APPROVAL_DECISION_VALUES[decision_type]:
        reject_hard_blocker_acceptance(decision_id, source_rows)
    if decision_type == "retained_code":
        if decision_value in {"accept", "exception_approve"}:
            require_string(decision.get("residual_risk_rationale"),
                           f"{decision_id}.residual_risk_rationale")
        return
    if decision_type == "residual_risk":
        require_string_list(decision.get("affected_gates"),
                            f"{decision_id}.affected_gates")
        require_string_list(decision.get("follow_up_refs"),
                            f"{decision_id}.follow_up_refs")
        return
    if decision_type == "exception":
        if decision_value == "approve":
            validate_exception_approval(decision, source_rows)
        return
    if decision_type == "readiness":
        if decision_value == "block" and "blocked_source_row_refs" in decision:
            blocked_source_refs = require_string_list(
                decision.get("blocked_source_row_refs"),
                f"{decision_id}.blocked_source_row_refs")
            validate_source_row_refs(decision_id, "blocked_source_row_refs",
                                     blocked_source_refs, row_map)
            decision["blocked_source_row_refs"] = blocked_source_refs
        return
    if decision_type == "reference_demotion":
        return
    raise VerificationError(
        f"{decision_id} unknown decision_type: {decision_type}")


def validate_decision_axis_rows(decision_id: str, decision_type: str,
                                source_rows: list[dict[str, Any]]) -> None:
    allowed_impacts = DECISION_TYPE_IMPACTS[decision_type]
    for row in source_rows:
        decision_impact = row.get("decision_impact")
        if decision_impact not in allowed_impacts:
            raise VerificationError(
                f"{decision_id} {decision_type} decision cannot reference "
                f"{row.get('row_id')} with decision_impact={decision_impact}")


def reject_hard_blocker_acceptance(decision_id: str,
                                   source_rows: list[dict[str, Any]]) -> None:
    hard_rows = [
        str(row["row_id"]) for row in source_rows
        if row.get("row_problem_kind") in HARD_BLOCKER_PROBLEM_KINDS
    ]
    if hard_rows:
        raise VerificationError(
            f"{decision_id} cannot accept hard blocker rows: {', '.join(hard_rows)}"
        )


def validate_exception_approval(decision: dict[str, Any],
                                source_rows: list[dict[str, Any]]) -> None:
    decision_id = str(decision["decision_id"])
    for field in [
            "scope",
            "expiry_or_review_trigger",
            "affected_requirements",
            "affected_gates",
            "linked_blocker_refs",
    ]:
        if field in {"scope", "expiry_or_review_trigger"}:
            require_string(decision.get(field), f"{decision_id}.{field}")
        elif field == "linked_blocker_refs":
            decision[field] = require_non_empty_string_list(
                decision.get(field), f"{decision_id}.{field}")
        else:
            require_string_list(decision.get(field), f"{decision_id}.{field}")
    require_string(decision.get("rationale"), f"{decision_id}.rationale")
    require_string(decision.get("owner_signoff_ref"),
                   f"{decision_id}.owner_signoff_ref")
    reject_hard_blocker_acceptance(decision_id, source_rows)
    source_refs = list(decision["source_row_refs"])
    if list(decision["linked_blocker_refs"]) != source_refs:
        raise VerificationError(
            f"{decision_id} linked_blocker_refs must exactly match source_row_refs"
        )
    affected_gates = set(decision["affected_gates"])
    for row in source_rows:
        if row.get("blocker_kind") != "exception_request":
            raise VerificationError(
                f"{decision_id} exception approval source row is not an exception_request: {row.get('row_id')}"
            )
        affected_gate = require_string(row.get("affected_gate"),
                                       f"{decision_id}.affected_gate")
        if affected_gate not in affected_gates:
            raise VerificationError(
                f"{decision_id} affected_gate mismatch for {affected_gate}")
