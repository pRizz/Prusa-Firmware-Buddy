from __future__ import annotations

from phase32_phase27_adapter import load_phase27_28_container, missing_optional_row
from phase32_triage_policy import *


def phase28_problem_status(raw_status: str) -> str:
    if raw_status.startswith("pending-") or raw_status == "not-required":
        return "missing"
    return raw_status


def phase28_rows(root: Path, phase28_output_dir: Path) -> list[dict[str, Any]]:
    phase28_dir = path_under(phase28_output_dir, DEFAULT_PHASE28_OUTPUT_DIR,
                             "--phase28-output-dir")
    rows: list[dict[str, Any]] = []
    blocker_path = phase28_dir / "blocker-summary.json"
    residual_path = phase28_dir / "exception-residual-risk-summary.json"
    demotion_path = phase28_dir / "reference-demotion-authorization-record.json"

    if not (root / blocker_path).exists():
        rows.append(
            missing_optional_row(blocker_path, "readiness",
                                 "final_readiness_blocked"))
    else:
        blocker_items, blocker_problem_rows = load_phase27_28_container(
            root,
            blocker_path,
            DEFAULT_PHASE28_OUTPUT_DIR / "blocker-summary.json",
        )
        rows.extend(blocker_problem_rows)
        for item_index, item in enumerate(blocker_items):
            criterion_id = str(
                item.get("criterion_id")
                or f"unknown-readiness-row-{item_index}")
            raw_status = str(
                item.get("phase27_status") or item.get("phase26_status")
                or "blocked")
            problem_status = phase28_problem_status(raw_status)
            is_unknown_status = classify_problem_kind(
                {"status": problem_status}) == "unknown_unclassified"
            rows.append(
                build_blocker_row(
                    source_domain="readiness",
                    producer_phase="phase28",
                    producer_artifact_kind="phase28_blocker_summary",
                    source_row_kind="readiness_blocker",
                    source_subject_id=criterion_id,
                    decision_axis="readiness",
                    decision_subject_id=criterion_id,
                    source_stream="readiness",
                    source_ref=f"{blocker_path.as_posix()}#{criterion_id}",
                    signal={
                        "status": problem_status,
                        "criterion_id": criterion_id,
                        "evidence_refs": [blocker_path.as_posix()],
                    },
                    policy_override={
                        "blocker_kind":
                        "unresolved_decision_blocker",
                        "severity":
                        "high",
                        "decision_impact":
                        "final_readiness_blocked",
                        "proof_eligibility":
                        "ineligible",
                        "required_next_action":
                        "Resolve readiness blocker or route it through explicit later decision input.",
                    } if not is_unknown_status else None,
                ))

    if not (root / residual_path).exists():
        rows.append(
            missing_optional_row(residual_path, "readiness",
                                 "residual_risk_decision_required"))
    else:
        residual_items, residual_problem_rows = load_phase27_28_container(
            root,
            residual_path,
            DEFAULT_PHASE28_OUTPUT_DIR /
            "exception-residual-risk-summary.json",
        )
        rows.extend(residual_problem_rows)
        for item_index, item in enumerate(residual_items):
            criterion_id = str(
                item.get("criterion_id")
                or f"unknown-residual-row-{item_index}")
            rows.append(
                build_blocker_row(
                    source_domain="readiness",
                    producer_phase="phase28",
                    producer_artifact_kind=
                    "phase28_exception_residual_risk_summary",
                    source_row_kind="residual_risk",
                    source_subject_id=criterion_id,
                    decision_axis="residual_risk",
                    decision_subject_id=criterion_id,
                    source_stream="readiness",
                    source_ref=f"{residual_path.as_posix()}#{criterion_id}",
                    signal={
                        "status": "missing",
                        "criterion_id": criterion_id,
                        "evidence_refs": [residual_path.as_posix()]
                    },
                    policy_override={
                        "blocker_kind":
                        "unresolved_decision_blocker",
                        "severity":
                        "medium",
                        "decision_impact":
                        "residual_risk_decision_required",
                        "proof_eligibility":
                        "ineligible",
                        "required_next_action":
                        "Route residual-risk row to explicit later decision input.",
                    },
                ))

    if not (root / demotion_path).exists():
        rows.append(
            missing_optional_row(demotion_path, "readiness",
                                 "demotion_decision_required"))
    else:
        demotion = load_json(root, demotion_path)
        authorization = demotion.get("reference_demotion_authorization")
        if authorization != "approved":
            is_blocked = authorization == "blocked"
            signal = ({
                "status": "missing",
                "criterion_id": "final-reference-demotion-allowed",
                "evidence_refs": [demotion_path.as_posix()],
            } if is_blocked else {
                "adapter_problem_kind": "unknown_unclassified",
                "failure_reason":
                f"unsupported Phase 28 demotion authorization: {authorization}",
                "criterion_id": "final-reference-demotion-allowed",
                "evidence_refs": [demotion_path.as_posix()],
            })
            policy_override = ({
                "blocker_kind":
                "unresolved_decision_blocker",
                "severity":
                "high",
                "decision_impact":
                "demotion_decision_required",
                "proof_eligibility":
                "ineligible",
                "required_next_action":
                "Provide a valid explicit demotion decision in the later demotion gate.",
            } if is_blocked else None)
            rows.append(
                build_blocker_row(
                    source_domain="readiness",
                    producer_phase="phase28",
                    producer_artifact_kind=
                    "phase28_reference_demotion_authorization_record",
                    source_row_kind="demotion_authorization",
                    source_subject_id="final-reference-demotion-allowed",
                    decision_axis="demotion",
                    decision_subject_id="final-reference-demotion-allowed",
                    source_stream="readiness",
                    source_ref=
                    f"{demotion_path.as_posix()}#reference-demotion-authorization",
                    signal=signal,
                    policy_override=policy_override,
                ))
    return rows
