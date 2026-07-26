#!/usr/bin/env python3
from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from typing import Any

SourceIdentity = dict[str, str]
DecisionIdentity = dict[str, str]
NormalizedSignal = dict[str, Any]


class NormalizationError(ValueError):
    """Raised when producer data cannot be normalized into canonical blocker identity."""


def canonical_source_identity(
    *,
    source_domain: str,
    producer_phase: str,
    producer_artifact_kind: str,
    source_row_kind: str,
    source_subject_id: str,
) -> SourceIdentity:
    """Return the exact immutable five-field identity for one producer row."""
    raise NotImplementedError


def canonical_row_id(source_identity: Mapping[str, str]) -> str:
    """Derive a deterministic row ID exclusively from immutable source identity."""
    raise NotImplementedError


def decision_identity(*, decision_axis: str,
                      decision_subject_id: str) -> DecisionIdentity:
    """Return the exact decision-resolution identity pair for a blocker row."""
    raise NotImplementedError


def validate_identity_bindings(rows: Sequence[Mapping[str, Any]]) -> None:
    """Reject duplicate sources and incompatible source-to-decision remappings."""
    raise NotImplementedError


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
    raise NotImplementedError
