from __future__ import annotations

from phase32_triage_policy import *


def missing_optional_row(path: Path, source_stream: str,
                         decision_impact: str) -> dict[str, Any]:
    artifact_subject = path.name.replace(".json", "")
    decision_axis = {
        "demotion_decision_required": "demotion",
        "residual_risk_decision_required": "residual_risk",
        "retained_code_decision_required": "retained_code",
    }.get(decision_impact, "readiness")
    return build_blocker_row(
        source_domain="retained_code"
        if source_stream == "retained-code" else "readiness",
        producer_phase="phase32",
        producer_artifact_kind="phase32_missing_source_artifact",
        source_row_kind="missing_source_artifact",
        source_subject_id=artifact_subject,
        decision_axis=decision_axis,
        decision_subject_id=artifact_subject,
        source_stream=source_stream,
        source_ref=path.as_posix(),
        signal={
            "status": "missing",
            "requirement_ids": sorted(REQUIRED_REQUIREMENT_IDS)
        },
        policy_override={
            "blocker_kind":
            "unresolved_decision_blocker",
            "severity":
            "high",
            "decision_impact":
            decision_impact,
            "proof_eligibility":
            "ineligible",
            "required_next_action":
            f"Generate the missing {path.name} handoff artifact before downstream decisions.",
        },
    )


def load_phase27_28_container(
    root: Path,
    artifact_path: Path,
    adapter_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mapping = PHASE27_28_CONTAINER_ADAPTERS.get(adapter_path)
    if mapping is None:
        raise VerificationError(
            f"no Phase 27/28 container adapter for {adapter_path.as_posix()}")
    try:
        container = json.loads(read_text(root, artifact_path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{artifact_path.as_posix()} is not valid JSON: {error}"
        ) from error

    problem_kind: str | None = None
    failure_reason = ""
    if not isinstance(container, dict):
        problem_kind = "unknown_unclassified"
        failure_reason = "producer artifact must contain a top-level object"
    elif ("producer_artifact_kind" in container
          and container.get("producer_artifact_kind")
          != mapping["producer_artifact_kind"]):
        problem_kind = "unknown_unclassified"
        failure_reason = (
            "producer artifact has an incompatible producer_artifact_kind")
    else:
        collection_field = mapping["collection_field"]
        collection = container.get(collection_field)
        if not isinstance(collection, list):
            problem_kind = "malformed"
            failure_reason = (
                f"producer artifact {collection_field} must be a list")
        elif not all(isinstance(item, dict) for item in collection):
            problem_kind = "malformed"
            failure_reason = (
                f"producer artifact {collection_field} must contain only objects"
            )
        else:
            return list(collection), []

    source_ref = f"{artifact_path.as_posix()}#container"
    problem_row = build_blocker_row(
        source_domain=mapping["source_domain"],
        producer_phase=mapping["producer_phase"],
        producer_artifact_kind=mapping["producer_artifact_kind"],
        source_row_kind=mapping["source_row_kind"],
        source_subject_id=mapping["source_subject_id"],
        decision_axis=mapping["decision_axis"],
        decision_subject_id=mapping["decision_subject_id"],
        source_stream=mapping["source_stream"],
        source_ref=source_ref,
        signal={
            "adapter_problem_kind": problem_kind,
            "affected_gate": mapping["affected_gate"],
            "evidence_refs": [artifact_path.as_posix()],
            "failure_reason": failure_reason,
        },
    )
    return [], [problem_row]


def phase27_rows(root: Path, phase27_output_dir: Path) -> list[dict[str, Any]]:
    phase27_dir = path_under(phase27_output_dir, DEFAULT_PHASE27_OUTPUT_DIR,
                             "--phase27-output-dir")
    rows: list[dict[str, Any]] = []
    residual_path = phase27_dir / "residual-risk-register.json"
    exception_path = phase27_dir / "exception-decision-register.json"
    handoff_path = phase27_dir / "phase28-handoff-manifest.json"

    if not (root / residual_path).exists():
        rows.append(
            missing_optional_row(residual_path, "retained-code",
                                 "residual_risk_decision_required"))
    else:
        residual_items, residual_problem_rows = load_phase27_28_container(
            root,
            residual_path,
            DEFAULT_PHASE27_OUTPUT_DIR / "residual-risk-register.json",
        )
        rows.extend(residual_problem_rows)
        for item_index, item in enumerate(residual_items):
            row_type = str(item.get("row_type") or "")
            source_stream = ("retained-code" if row_type
                             == "retained_code_decision" else "readiness")
            decision_impact = "retained_code_decision_required" if source_stream == "retained-code" else "residual_risk_decision_required"
            row_id = str(
                item.get("row_id") or f"unknown-residual-row-{item_index}")
            maybe_unknown_kind = (None if row_type in {
                "retained_code_decision", "final_readiness_decision"
            } else "unknown_unclassified")
            decision_axis = ("retained_code" if row_type
                             == "retained_code_decision" else "residual_risk")
            rows.append(
                build_blocker_row(
                    source_domain="retained_code"
                    if source_stream == "retained-code" else "readiness",
                    producer_phase="phase27",
                    producer_artifact_kind="phase27_residual_risk_register",
                    source_row_kind=row_type if row_type in {
                        "retained_code_decision", "final_readiness_decision"
                    } else "residual_risk",
                    source_subject_id=row_id,
                    decision_axis=decision_axis,
                    decision_subject_id=row_id,
                    source_stream=source_stream,
                    source_ref=f"{residual_path.as_posix()}#{row_id}",
                    signal={
                        "adapter_problem_kind":
                        maybe_unknown_kind,
                        "failure_reason":
                        (f"unsupported Phase 27 residual row_type: {row_type}"
                         if maybe_unknown_kind else ""),
                        "status":
                        "missing",
                        "owner":
                        item.get("owner"),
                        "row_id":
                        row_id,
                        "evidence_refs": [residual_path.as_posix()],
                    },
                    policy_override={
                        "blocker_kind":
                        "unresolved_decision_blocker",
                        "severity":
                        "medium",
                        "decision_impact":
                        decision_impact,
                        "proof_eligibility":
                        "ineligible",
                        "required_next_action":
                        "Route residual-risk or retained-code item to Phase 33 decision input.",
                    } if maybe_unknown_kind is None else None,
                ))

    if not (root / exception_path).exists():
        rows.append(
            missing_optional_row(exception_path, "retained-code",
                                 "exception_decision_required"))
    else:
        exception_items, exception_problem_rows = load_phase27_28_container(
            root,
            exception_path,
            DEFAULT_PHASE27_OUTPUT_DIR / "exception-decision-register.json",
        )
        rows.extend(exception_problem_rows)
        for item_index, item in enumerate(exception_items):
            row_type = str(item.get("row_type") or "")
            source_stream = "retained-code" if row_type == "retained_code_decision" else "readiness"
            gate_id = str(
                item.get("criterion_id") or item.get("row_id")
                or f"unknown-exception-row-{item_index}")
            maybe_unknown_kind = (None if row_type in {
                "retained_code_decision", "final_readiness_decision"
            } else "unknown_unclassified")
            rows.append(
                build_blocker_row(
                    source_domain="retained_code"
                    if source_stream == "retained-code" else "readiness",
                    producer_phase="phase27",
                    producer_artifact_kind=
                    "phase27_exception_decision_register",
                    source_row_kind="exception_request",
                    source_subject_id=gate_id,
                    decision_axis="exception",
                    decision_subject_id=gate_id,
                    source_stream=source_stream,
                    source_ref=f"{exception_path.as_posix()}#{gate_id}",
                    signal={
                        "status":
                        "exception-requested",
                        "adapter_problem_kind":
                        maybe_unknown_kind,
                        "failure_reason":
                        (f"unsupported Phase 27 exception row_type: {row_type}"
                         if maybe_unknown_kind else ""),
                        "exception_status":
                        item.get("exception_state", "exception-requested"),
                        "owner":
                        item.get("owner"),
                        "criterion_id":
                        gate_id,
                        "row_id":
                        gate_id,
                        "evidence_refs": [exception_path.as_posix()],
                    },
                ))

    if not (root / handoff_path).exists():
        rows.append(
            missing_optional_row(handoff_path, "readiness",
                                 "demotion_decision_required"))
    else:
        handoff = load_json(root, handoff_path)
        authorization = handoff.get("demotion_authorization")
        is_blocked = authorization == "blocked"
        signal = ({
            "status": "missing",
            "criterion_id": "final-reference-demotion-allowed",
            "evidence_refs": [handoff_path.as_posix()],
        } if is_blocked else {
            "adapter_problem_kind": "unknown_unclassified",
            "failure_reason":
            f"unsupported Phase 27 demotion authorization: {authorization}",
            "criterion_id": "final-reference-demotion-allowed",
            "evidence_refs": [handoff_path.as_posix()],
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
            "Route reference-demotion authorization to the later explicit maintainer decision gate.",
        } if is_blocked else None)
        rows.append(
            build_blocker_row(
                source_domain="readiness",
                producer_phase="phase27",
                producer_artifact_kind="phase27_phase28_handoff_manifest",
                source_row_kind="demotion_authorization",
                source_subject_id="final-reference-demotion-allowed",
                decision_axis="demotion",
                decision_subject_id="final-reference-demotion-allowed",
                source_stream="readiness",
                source_ref=f"{handoff_path.as_posix()}#demotion-authorization",
                signal=signal,
                policy_override=policy_override,
            ))
    return rows


def phase28_problem_status(raw_status: str) -> str:
    if raw_status.startswith("pending-") or raw_status == "not-required":
        return "missing"
    return raw_status
