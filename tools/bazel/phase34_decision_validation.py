from __future__ import annotations


def validate_normalized_decisions(
        decisions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    decisions_by_id: dict[str, dict[str, Any]] = {}
    for index, decision in enumerate(decisions):
        field_prefix = f"normalized decision rows[{index}]"
        missing_fields = [
            field for field in PHASE33_REQUIRED_DECISION_FIELDS
            if field not in decision
        ]
        if missing_fields:
            raise VerificationError(
                f"{field_prefix} missing required fields: {', '.join(missing_fields)}"
            )
        decision_id = require_string(decision.get("decision_id"),
                                     f"{field_prefix}.decision_id")
        if decision_id in decisions_by_id:
            raise VerificationError(
                f"duplicate Phase 33 decision_id: {decision_id}")
        decision_type = require_string(decision.get("decision_type"),
                                       f"{decision_id}.decision_type")
        maybe_values = PHASE33_DECISION_VALUE_ENUMS.get(decision_type)
        if maybe_values is None:
            raise VerificationError(
                f"{decision_id} unknown decision_type: {decision_type}")
        decision_value = require_string(decision.get("decision_value"),
                                        f"{decision_id}.decision_value")
        if decision.get("phase") != "33-maintainer-decision-inputs":
            raise VerificationError(
                f"{decision_id}.phase must be 33-maintainer-decision-inputs")
        require_string(
            decision.get("phase_lifecycle_id"),
            f"{decision_id}.phase_lifecycle_id",
        )
        require_string(
            decision.get("decision_axis"),
            f"{decision_id}.decision_axis",
        )
        source_refs = string_list(decision.get("source_row_refs"),
                                  f"{decision_id}.source_row_refs")
        if not source_refs:
            raise VerificationError(
                f"{decision_id}.source_row_refs must contain at least one entry"
            )
        raw_targets = require_list(
            decision.get("decision_targets"),
            f"{decision_id}.decision_targets",
        )
        if not raw_targets:
            raise VerificationError(
                f"{decision_id}.decision_targets must contain at least one entry"
            )
        decision_targets: list[dict[str, str]] = []
        for target_index, raw_target in enumerate(raw_targets):
            if not isinstance(raw_target, dict):
                raise VerificationError(
                    f"{decision_id}.decision_targets[{target_index}] must be an object"
                )
            target = {
                field:
                require_string(
                    raw_target.get(field),
                    f"{decision_id}.decision_targets[{target_index}].{field}",
                )
                for field in (
                    "row_ref",
                    "decision_axis",
                    "decision_subject_id",
                )
            }
            decision_targets.append(target)
        if source_refs != [target["row_ref"] for target in decision_targets]:
            raise VerificationError(
                f"{decision_id}.source_row_refs must exactly project "
                "decision_targets[*].row_ref")
        for field in ("maintainer_identity_ref", "maintainer_role",
                      "owner_signoff_ref", "rationale"):
            require_string(decision.get(field), f"{decision_id}.{field}")
        require_iso_utc(
            require_string(decision.get("decision_timestamp"),
                           f"{decision_id}.decision_timestamp"),
            f"{decision_id}.decision_timestamp",
        )
        for field in ("evidence_refs", "artifact_refs"):
            string_list(decision.get(field), f"{decision_id}.{field}")
        decisions_by_id[decision_id] = decision
    return decisions_by_id


def validate_handoff_decision(
    projection: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
    expected_type: str,
    expected_value: str,
    matching_fields: tuple[str, ...],
) -> dict[str, Any]:
    decision_id = require_string(projection.get("decision_id"), "decision_id")
    maybe_decision = decisions_by_id.get(decision_id)
    if maybe_decision is None:
        raise VerificationError(f"unknown Phase 33 decision_id: {decision_id}")
    decision = maybe_decision
    if decision.get("decision_type") != expected_type or decision.get(
            "decision_value") != expected_value:
        raise VerificationError(
            f"{decision_id} does not authorize {expected_type}={expected_value}"
        )
    if decision.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        raise VerificationError(
            f"{decision_id}.phase_lifecycle_id must be {PHASE33_LIFECYCLE_ID}")
    for field in matching_fields:
        if projection.get(field) != decision.get(field):
            raise VerificationError(
                f"{decision_id} projection mismatch for {field}")
    require_iso_utc(str(decision["decision_timestamp"]),
                    f"{decision_id}.decision_timestamp")
    return decision
