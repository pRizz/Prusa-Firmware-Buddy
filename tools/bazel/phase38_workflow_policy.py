from __future__ import annotations

from collections.abc import Callable, Collection
from typing import Any


def safe_reason(
    reason_category: str,
    safe_reason_categories: Collection[str],
    fallback: str,
) -> str:
    if reason_category in safe_reason_categories:
        return reason_category
    return fallback


def authority_is_consistent(authority: Any) -> bool:
    if not authority.available:
        return False
    if authority.verdict == "approved":
        return (
            authority.route == "production-cutover-planning"
            and authority.readiness_state == "unblocked"
            and not authority.requires_fresh_cutover_decision
        )
    if authority.verdict in {"blocked", "approved-with-exceptions"}:
        return (
            authority.route == "targeted-blocker-repair"
            and authority.requires_fresh_cutover_decision
        )
    return False


def evaluate_final_status(
    phase34_outcome: Any,
    phase35_outcome: Any,
    authority: Any,
    *,
    result_factory: Callable[..., Any],
    safe_reason_categories: Collection[str],
) -> Any:
    authority_consistent = authority_is_consistent(authority)
    operations_succeeded = (
        phase34_outcome.status == 0 and phase35_outcome.status == 0
    )
    production_cutover_planning = (
        operations_succeeded
        and authority_consistent
        and authority.verdict == "approved"
        and authority.route == "production-cutover-planning"
    )
    reference_demotion_authorized = (
        operations_succeeded
        and authority_consistent
        and authority.readiness_state == "unblocked"
        and authority.demotion_validation_state == "valid"
        and authority.demotion_decision_state == "approve"
        and authority.demotion_gate_state == "open"
    )

    if phase34_outcome.status != 0:
        status = phase34_outcome.status
        reason_category = safe_reason(
            phase34_outcome.reason_category,
            safe_reason_categories,
            "phase34-operation-failed",
        )
    elif phase35_outcome.status != 0:
        status = phase35_outcome.status
        reason_category = safe_reason(
            phase35_outcome.reason_category,
            safe_reason_categories,
            "phase35-operation-failed",
        )
    elif not authority.available:
        status = 1
        reason_category = safe_reason(
            authority.reason_category,
            safe_reason_categories,
            "phase35-authority-invalid",
        )
    elif not authority_consistent:
        status = 1
        reason_category = "phase35-authority-contradictory"
    else:
        status = 0
        reason_category = "none"

    return result_factory(
        status=status,
        reason_category=reason_category,
        phase34_status=phase34_outcome.status,
        phase35_status=phase35_outcome.status,
        final_authority_available=(
            operations_succeeded
            and authority.available
            and authority_consistent
        ),
        verdict=authority.verdict,
        route=authority.route,
        readiness_state=authority.readiness_state,
        production_cutover_planning=production_cutover_planning,
        reference_demotion_authorized=reference_demotion_authorized,
        requires_fresh_cutover_decision=(
            authority.requires_fresh_cutover_decision
        ),
    )
