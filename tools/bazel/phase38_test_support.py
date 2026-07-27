from __future__ import annotations

import phase38_cutover_workflow as workflow


def approved_authority(
    *,
    demotion_validation_state: str = "missing",
    demotion_decision_state: str = "missing",
    demotion_gate_state: str = "blocked",
) -> workflow.FinalAuthority:
    return workflow.FinalAuthority(
        available=True,
        verdict="approved",
        route="production-cutover-planning",
        readiness_state="unblocked",
        requires_fresh_cutover_decision=False,
        demotion_validation_state=demotion_validation_state,
        demotion_decision_state=demotion_decision_state,
        demotion_gate_state=demotion_gate_state,
        reason_category="none",
    )


def blocked_authority() -> workflow.FinalAuthority:
    return workflow.FinalAuthority(
        available=True,
        verdict="blocked",
        route="targeted-blocker-repair",
        readiness_state="blocked",
        requires_fresh_cutover_decision=True,
        demotion_validation_state="missing",
        demotion_decision_state="missing",
        demotion_gate_state="blocked",
        reason_category="none",
    )
