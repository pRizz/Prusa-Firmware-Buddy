#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections.abc import Collection, Mapping, Sequence
from typing import Any

SourceIdentity = dict[str, str]
DecisionIdentity = dict[str, str]
NormalizedSignal = dict[str, Any]

SOURCE_IDENTITY_FIELDS = (
    "source_domain",
    "producer_phase",
    "producer_artifact_kind",
    "source_row_kind",
    "source_subject_id",
)
DECISION_AXES = {
    "retained_code",
    "residual_risk",
    "exception",
    "readiness",
    "demotion",
}
PHASE26_ARTIFACT_NAME = "phase26-release-signing-upstream-evidence"
PHASE26_LIST_FIELDS = {
    "artifact_refs",
    "evidence_refs",
    "requirement_ids",
    "source_requirement_ids",
}


class NormalizationError(ValueError):
    """Raised when producer data cannot be normalized into canonical blocker identity."""


def non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise NormalizationError(f"{field} must be a non-empty string")
    return value


def canonical_source_identity(
    *,
    source_domain: str,
    producer_phase: str,
    producer_artifact_kind: str,
    source_row_kind: str,
    source_subject_id: str,
) -> SourceIdentity:
    """Return the exact immutable five-field identity for one producer row."""
    values = {
        "source_domain": source_domain,
        "producer_phase": producer_phase,
        "producer_artifact_kind": producer_artifact_kind,
        "source_row_kind": source_row_kind,
        "source_subject_id": source_subject_id,
    }
    return {
        field: non_empty_string(values[field], field)
        for field in SOURCE_IDENTITY_FIELDS
    }


def canonical_row_id(source_identity: Mapping[str, str]) -> str:
    """Derive a deterministic row ID exclusively from immutable source identity."""
    canonical = {
        field: non_empty_string(source_identity.get(field), field)
        for field in SOURCE_IDENTITY_FIELDS
    }
    encoded = json.dumps(canonical, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return f"blocker-{hashlib.sha256(encoded).hexdigest()[:16]}"


def decision_identity(
    *,
    decision_axis: str,
    decision_subject_id: str,
) -> DecisionIdentity:
    """Return the exact decision-resolution identity pair for a blocker row."""
    if decision_axis not in DECISION_AXES:
        raise NormalizationError(
            f"decision_axis is unsupported: {decision_axis}")
    return {
        "decision_axis":
        decision_axis,
        "decision_subject_id":
        non_empty_string(
            decision_subject_id,
            "decision_subject_id",
        ),
    }


def validate_identity_bindings(rows: Sequence[Mapping[str, Any]]) -> None:
    """Reject duplicate sources and incompatible source-to-decision remappings."""
    bindings: dict[tuple[str, ...], tuple[str, str]] = {}
    row_ids: set[str] = set()
    for index, row in enumerate(rows):
        source = canonical_source_identity(
            **{field: row.get(field)
               for field in SOURCE_IDENTITY_FIELDS})
        decision = decision_identity(
            decision_axis=row.get("decision_axis"),
            decision_subject_id=row.get("decision_subject_id"),
        )
        source_tuple = tuple(source[field] for field in SOURCE_IDENTITY_FIELDS)
        decision_tuple = (
            decision["decision_axis"],
            decision["decision_subject_id"],
        )
        maybe_existing = bindings.get(source_tuple)
        if maybe_existing is not None:
            if maybe_existing != decision_tuple:
                raise NormalizationError(
                    f"source identity at row {index} has incompatible decision remapping"
                )
            raise NormalizationError(
                f"duplicate source identity at row {index}")
        bindings[source_tuple] = decision_tuple

        row_id = canonical_row_id(source)
        if row_id in row_ids:
            raise NormalizationError(
                f"duplicate canonical row_id at row {index}: {row_id}")
        row_ids.add(row_id)


def adapter_problem(
    problem_kind: str,
    reason: str,
    *,
    receipt_ref: str,
    table_ref: str,
) -> NormalizedSignal:
    return {
        "adapter_problem_kind": problem_kind,
        "failure_reason": reason,
        "receipt_ref": receipt_ref,
        "source_subject_id": "phase26-upstream-result-row-table",
        "status":
        "malformed" if problem_kind == "malformed" else "unsupported",
        "table_ref": table_ref,
    }


def malformed_problem(
    reason: str,
    *,
    receipt_ref: str,
    table_ref: str,
) -> list[NormalizedSignal]:
    return [
        adapter_problem(
            "malformed",
            reason,
            receipt_ref=receipt_ref,
            table_ref=table_ref,
        )
    ]


def unknown_problem(
    reason: str,
    *,
    receipt_ref: str,
    table_ref: str,
) -> list[NormalizedSignal]:
    return [
        adapter_problem(
            "unknown_unclassified",
            reason,
            receipt_ref=receipt_ref,
            table_ref=table_ref,
        )
    ]


def adapt_phase26_table(
    table: Mapping[str, Any],
    *,
    expected_criteria: Collection[str],
    required_row_fields: Collection[str],
    allowed_statuses: Collection[str],
    receipt_ref: str,
    table_ref: str,
) -> list[NormalizedSignal]:
    """Atomically adapt the accepted-final Phase 26 release/signing row table."""
    artifact_name = table.get("artifact_name")
    if artifact_name not in (None, PHASE26_ARTIFACT_NAME):
        return unknown_problem(
            f"unsupported Phase 26 table envelope: {artifact_name}",
            receipt_ref=receipt_ref,
            table_ref=table_ref,
        )

    rows = table.get("rows")
    if not isinstance(rows, list) or not rows:
        return malformed_problem(
            "Phase 26 table rows must be a non-empty list",
            receipt_ref=receipt_ref,
            table_ref=table_ref,
        )

    expected = set(expected_criteria)
    required = set(required_row_fields)
    allowed = set(allowed_statuses)
    normalized: list[NormalizedSignal] = []
    seen: set[str] = set()
    for index, maybe_row in enumerate(rows):
        if not isinstance(maybe_row, Mapping):
            return malformed_problem(
                f"Phase 26 table rows[{index}] must be an object",
                receipt_ref=receipt_ref,
                table_ref=table_ref,
            )
        row = dict(maybe_row)
        missing = required - set(row)
        if missing:
            return malformed_problem(
                f"Phase 26 table rows[{index}] missing fields: {', '.join(sorted(missing))}",
                receipt_ref=receipt_ref,
                table_ref=table_ref,
            )
        for field in required:
            value = row[field]
            if field in PHASE26_LIST_FIELDS:
                if not isinstance(value, list):
                    return malformed_problem(
                        f"Phase 26 table rows[{index}].{field} must be a list",
                        receipt_ref=receipt_ref,
                        table_ref=table_ref,
                    )
            elif not isinstance(value, str):
                return malformed_problem(
                    f"Phase 26 table rows[{index}].{field} must be a string",
                    receipt_ref=receipt_ref,
                    table_ref=table_ref,
                )

        criterion_id = row["criterion_id"]
        if not criterion_id or criterion_id not in expected:
            return malformed_problem(
                f"Phase 26 table rows[{index}] uses unknown criterion_id: {criterion_id}",
                receipt_ref=receipt_ref,
                table_ref=table_ref,
            )
        if criterion_id in seen:
            return malformed_problem(
                f"Phase 26 table duplicates criterion_id: {criterion_id}",
                receipt_ref=receipt_ref,
                table_ref=table_ref,
            )
        seen.add(criterion_id)

        status = row["status"]
        if status not in allowed:
            return unknown_problem(
                f"Phase 26 table rows[{index}] uses unsupported status: {status}",
                receipt_ref=receipt_ref,
                table_ref=table_ref,
            )
        normalized.append({
            **row,
            "receipt_ref": receipt_ref,
            "source_subject_id": criterion_id,
            "table_ref": table_ref,
        })

    if seen != expected:
        return malformed_problem(
            "Phase 26 table is missing canonical criteria: " +
            ", ".join(sorted(expected - seen)),
            receipt_ref=receipt_ref,
            table_ref=table_ref,
        )
    return normalized
