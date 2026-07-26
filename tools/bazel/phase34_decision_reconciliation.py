#!/usr/bin/env python3
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, NamedTuple


PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
SUPPORTED_AXES = {
    "retained_code",
    "residual_risk",
    "exception",
    "readiness",
    "demotion",
}
ALLOWED_VALUES = {
    "retained_code": {"accept", "reject", "exception_approve"},
    "residual_risk": {"accept", "reject"},
    "exception": {"approve", "reject"},
    "readiness": {"approve", "block"},
    "demotion": {"approve", "reject"},
}
APPROVING_VALUES = {
    "retained_code": {"accept", "exception_approve"},
    "residual_risk": {"accept"},
    "exception": {"approve"},
    "readiness": {"approve"},
    "demotion": {"approve"},
}
HARD_BLOCKER_PROBLEM_KINDS = {
    "redaction_failed",
    "source_ref_failed",
    "secret_tainted",
    "lifecycle_mismatch",
    "unsafe_ref",
}


class CanonicalDecisionRow(NamedTuple):
    row_id: str
    row_ref: str
    phase_lifecycle_id: str
    decision_axis: str
    decision_subject_id: str
    row_problem_kind: str
    blocker_kind: str

    @property
    def exact_key(self) -> tuple[str, str, str]:
        return (
            self.row_ref,
            self.decision_axis,
            self.decision_subject_id,
        )


class DecisionTarget(NamedTuple):
    row_ref: str
    decision_axis: str
    decision_subject_id: str

    @property
    def exact_key(self) -> tuple[str, str, str]:
        return (
            self.row_ref,
            self.decision_axis,
            self.decision_subject_id,
        )


class TargetedDecision(NamedTuple):
    decision_ref: str
    decision_axis: str
    decision_value: str
    phase_lifecycle_id: str
    target: DecisionTarget


def non_blank_string(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def parse_canonical_row(
    raw_row: Mapping[str, Any],
    expected_phase32_lifecycle_id: str,
) -> tuple[CanonicalDecisionRow | None, str | None]:
    row_id = non_blank_string(raw_row.get("row_id"))
    decision_axis = non_blank_string(raw_row.get("decision_axis"))
    decision_subject_id = non_blank_string(raw_row.get("decision_subject_id"))
    phase_lifecycle_id = non_blank_string(
        raw_row.get("phase_lifecycle_id", expected_phase32_lifecycle_id)
    )
    row_problem_kind = non_blank_string(raw_row.get("row_problem_kind"))
    blocker_kind = non_blank_string(raw_row.get("blocker_kind"))
    if None in {
        row_id,
        decision_axis,
        decision_subject_id,
        phase_lifecycle_id,
        row_problem_kind,
        blocker_kind,
    }:
        return None, "decision-target-malformed"
    if decision_axis not in SUPPORTED_AXES:
        return None, "decision-target-axis-mismatch"
    expected_row_ref = f"{PHASE32_REGISTER_REF}#{row_id}"
    row_ref = raw_row.get("row_ref", expected_row_ref)
    if row_ref != expected_row_ref:
        return None, "decision-target-row-mismatch"
    row = CanonicalDecisionRow(
        row_id=row_id,
        row_ref=expected_row_ref,
        phase_lifecycle_id=phase_lifecycle_id,
        decision_axis=decision_axis,
        decision_subject_id=decision_subject_id,
        row_problem_kind=row_problem_kind,
        blocker_kind=blocker_kind,
    )
    if phase_lifecycle_id != expected_phase32_lifecycle_id:
        return row, "decision-lifecycle-stale"
    return row, None


def parse_decision_targets(
    decisions: Sequence[Mapping[str, Any]],
) -> tuple[list[TargetedDecision], list[dict[str, str]]]:
    targeted: list[TargetedDecision] = []
    diagnostics: list[dict[str, str]] = []
    for decision_index, raw_decision in enumerate(decisions):
        decision_id = non_blank_string(raw_decision.get("decision_id"))
        decision_ref = non_blank_string(raw_decision.get("decision_ref"))
        record_axis = non_blank_string(raw_decision.get("decision_axis"))
        decision_value = non_blank_string(raw_decision.get("decision_value"))
        phase_lifecycle_id = non_blank_string(raw_decision.get("phase_lifecycle_id"))
        raw_targets = raw_decision.get("decision_targets")
        maybe_ref = decision_ref or decision_id or f"decision-index-{decision_index}"
        if (
            decision_id is None
            or record_axis not in SUPPORTED_AXES
            or decision_value is None
            or phase_lifecycle_id is None
            or not isinstance(raw_targets, list)
            or not raw_targets
        ):
            diagnostics.append({
                "decision_ref": maybe_ref,
                "reason_code": "decision-target-malformed",
            })
            continue
        for target_index, raw_target in enumerate(raw_targets):
            if not isinstance(raw_target, Mapping):
                diagnostics.append({
                    "decision_ref": maybe_ref,
                    "reason_code": "decision-target-malformed",
                    "target_index": str(target_index),
                })
                continue
            row_ref = non_blank_string(raw_target.get("row_ref"))
            target_axis = non_blank_string(raw_target.get("decision_axis"))
            decision_subject_id = non_blank_string(
                raw_target.get("decision_subject_id")
            )
            if (
                row_ref is None
                or target_axis not in SUPPORTED_AXES
                or decision_subject_id is None
            ):
                diagnostics.append({
                    "decision_ref": maybe_ref,
                    "reason_code": "decision-target-malformed",
                    "target_index": str(target_index),
                })
                continue
            targeted.append(
                TargetedDecision(
                    decision_ref=maybe_ref,
                    decision_axis=record_axis,
                    decision_value=decision_value,
                    phase_lifecycle_id=phase_lifecycle_id,
                    target=DecisionTarget(
                        row_ref=row_ref,
                        decision_axis=target_axis,
                        decision_subject_id=decision_subject_id,
                    ),
                )
            )
    return targeted, diagnostics


def blocked_result(
    row: CanonicalDecisionRow,
    reason_code: str,
    linked_decision_refs: Sequence[str] = (),
) -> dict[str, Any]:
    readiness_effect = (
        "independent" if row.decision_axis == "demotion" else "blocked"
    )
    return {
        "row_id": row.row_id,
        "row_ref": row.row_ref,
        "decision_axis": row.decision_axis,
        "decision_subject_id": row.decision_subject_id,
        "coverage_state": "blocked",
        "readiness_effect": readiness_effect,
        "linked_decision_refs": sorted(set(linked_decision_refs)),
        "reason_codes": [reason_code],
    }


def approved_result(
    row: CanonicalDecisionRow,
    decision_ref: str,
) -> dict[str, Any]:
    is_demotion = row.decision_axis == "demotion"
    return {
        "row_id": row.row_id,
        "row_ref": row.row_ref,
        "decision_axis": row.decision_axis,
        "decision_subject_id": row.decision_subject_id,
        "coverage_state": (
            "authorization-recorded" if is_demotion else "covered"
        ),
        "readiness_effect": "independent" if is_demotion else "unblocked",
        "linked_decision_refs": [decision_ref],
        "reason_codes": [],
    }


def evaluate_exact_matches(
    row: CanonicalDecisionRow,
    matches: Sequence[TargetedDecision],
    *,
    expected_phase33_lifecycle_id: str,
    readiness_prerequisites_unblocked: bool,
) -> dict[str, Any]:
    decision_refs = [match.decision_ref for match in matches]
    if len(matches) > 1:
        values = {match.decision_value for match in matches}
        reason_code = (
            "decision-target-conflict"
            if len(values) > 1
            else "decision-target-duplicate"
        )
        return blocked_result(row, reason_code, decision_refs)
    decision = matches[0]
    if decision.decision_axis != row.decision_axis:
        return blocked_result(
            row,
            "decision-target-axis-mismatch",
            decision_refs,
        )
    if decision.phase_lifecycle_id != expected_phase33_lifecycle_id:
        return blocked_result(
            row,
            "decision-lifecycle-stale",
            decision_refs,
        )
    if row.row_problem_kind in HARD_BLOCKER_PROBLEM_KINDS:
        return blocked_result(row, "decision-hard-blocker", decision_refs)
    if decision.decision_value not in ALLOWED_VALUES[row.decision_axis]:
        return blocked_result(row, "decision-value-invalid", decision_refs)
    if decision.decision_value not in APPROVING_VALUES[row.decision_axis]:
        return blocked_result(row, "decision-rejected", decision_refs)
    if (
        row.decision_axis == "readiness"
        and not readiness_prerequisites_unblocked
    ):
        return blocked_result(
            row,
            "decision-readiness-prerequisites-blocked",
            decision_refs,
        )
    return approved_result(row, decision.decision_ref)


def reconcile_decision_rows(
    canonical_rows: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
    *,
    expected_phase32_lifecycle_id: str,
    expected_phase33_lifecycle_id: str,
    readiness_prerequisites_unblocked: bool = True,
) -> dict[str, Any]:
    """Reconcile exact typed decisions into deterministic row coverage state."""
    parsed_rows: list[tuple[CanonicalDecisionRow, str | None]] = []
    diagnostics: list[dict[str, str]] = []
    for index, raw_row in enumerate(canonical_rows):
        row, maybe_reason = parse_canonical_row(
            raw_row,
            expected_phase32_lifecycle_id,
        )
        if row is None:
            diagnostics.append({
                "row_index": str(index),
                "reason_code": maybe_reason or "decision-target-malformed",
            })
            continue
        parsed_rows.append((row, maybe_reason))

    targeted_decisions, target_diagnostics = parse_decision_targets(decisions)
    diagnostics.extend(target_diagnostics)
    canonical_keys: dict[tuple[str, str, str], int] = {}
    canonical_refs = {row.row_ref for row, _reason in parsed_rows}
    for row, _reason in parsed_rows:
        canonical_keys[row.exact_key] = canonical_keys.get(row.exact_key, 0) + 1
    for targeted in targeted_decisions:
        if targeted.target.row_ref not in canonical_refs:
            diagnostics.append({
                "decision_ref": targeted.decision_ref,
                "reason_code": "decision-target-row-mismatch",
            })

    results: list[dict[str, Any]] = []
    for row, maybe_row_reason in sorted(
        parsed_rows,
        key=lambda item: item[0].exact_key,
    ):
        same_ref = [
            targeted
            for targeted in targeted_decisions
            if targeted.target.row_ref == row.row_ref
        ]
        exact_matches = [
            targeted
            for targeted in same_ref
            if targeted.target.exact_key == row.exact_key
        ]
        if maybe_row_reason is not None:
            results.append(blocked_result(row, maybe_row_reason))
            continue
        if canonical_keys[row.exact_key] > 1:
            results.append(
                blocked_result(
                    row,
                    "decision-target-multi-match",
                    [match.decision_ref for match in exact_matches],
                )
            )
            continue
        if not exact_matches:
            if any(
                targeted.target.decision_axis != row.decision_axis
                for targeted in same_ref
            ):
                reason_code = "decision-target-axis-mismatch"
            elif same_ref:
                reason_code = "decision-target-subject-mismatch"
            else:
                reason_code = "decision-target-missing"
            results.append(
                blocked_result(
                    row,
                    reason_code,
                    [targeted.decision_ref for targeted in same_ref],
                )
            )
            continue
        results.append(
            evaluate_exact_matches(
                row,
                exact_matches,
                expected_phase33_lifecycle_id=expected_phase33_lifecycle_id,
                readiness_prerequisites_unblocked=readiness_prerequisites_unblocked,
            )
        )
    readiness_state = (
        "blocked"
        if diagnostics
        or any(row["readiness_effect"] == "blocked" for row in results)
        else "unblocked"
    )
    return {
        "rows": results,
        "diagnostics": sorted(
            diagnostics,
            key=lambda item: tuple(sorted(item.items())),
        ),
        "readiness_state": readiness_state,
    }
