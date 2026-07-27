from __future__ import annotations

from phase18_cutover_contract import *
from phase18_cutover_policy import *
from phase18_cutover_upstream_policy import *
from phase18_cutover_validation import *


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def normalize_final_results(
    criteria: list[dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
    upstream_consumption: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for criterion in criteria:
        criterion_id = str(criterion["id"])
        maybe_decision = decisions.get(criterion_id)
        status = str(maybe_decision["status"]) if maybe_decision else str(
            criterion["default_status"])
        decision = str(
            maybe_decision["decision"]) if maybe_decision else "pending"
        evidence_refs = list(
            maybe_decision["evidence_refs"]) if maybe_decision else []
        residual_risk = str(
            maybe_decision["residual_risk"]) if maybe_decision else str(
                criterion["residual_risk_ref"])
        maintainer_status_allows = final_status_allows_demotion(
            status, maybe_decision, criterion)
        upstream = upstream_consumption[criterion_id]
        upstream_status_allows = bool(
            upstream["upstream_status_allows_cutover"])
        status_allows = maintainer_status_allows and upstream_status_allows
        blocking_reasons = []
        if not maintainer_status_allows:
            blocking_reasons.append(
                f"{criterion_id} status {status} blocks reference demotion")
        blocking_reasons.extend(upstream["upstream_blocking_reasons"])
        blocking_reason = "; ".join(blocking_reasons)
        results.append({
            "id":
            criterion_id,
            "requirement_ids":
            criterion["requirement_ids"],
            "evidence_family":
            criterion["evidence_family"],
            "status":
            status,
            "decision":
            decision,
            "maintainer_decision_required":
            criterion["maintainer_decision_required"],
            "exception_allowed":
            criterion["exception_allowed"],
            "blocks_demotion":
            criterion["blocks_demotion"],
            "source_refs":
            criterion["source_refs"],
            "evidence_refs":
            evidence_refs,
            "upstream_result_status":
            upstream["upstream_result_status"],
            "upstream_result_refs":
            upstream["upstream_result_refs"],
            "upstream_artifact_refs":
            upstream["upstream_artifact_refs"],
            "upstream_status_allows_cutover":
            upstream_status_allows,
            "upstream_blocking_reasons":
            upstream["upstream_blocking_reasons"],
            "maintainer_status_allows_cutover":
            maintainer_status_allows,
            "residual_risk":
            residual_risk,
            "demotion_blocking_reason":
            blocking_reason,
            "demotion_status_allows_cutover":
            status_allows,
        })
    return results


def normalize_retained_reviews(
    packets: list[dict[str, Any]],
    reviews: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for packet in packets:
        packet_id = str(packet["id"])
        maybe_review = reviews.get(packet_id)
        rows.append({
            "id":
            packet_id,
            "taxonomy_tags":
            packet["taxonomy_tags"],
            "status":
            str(maybe_review["status"])
            if maybe_review else str(packet["status"]),
            "owner":
            packet["owner"],
            "approver_role":
            str(maybe_review["approver_role"])
            if maybe_review else str(packet["approver_role"]),
            "retained_source_refs":
            packet["retained_source_refs"],
            "required_evidence_refs":
            packet["required_evidence_refs"],
            "supplied_evidence_result_refs":
            list(maybe_review["supplied_evidence_result_refs"])
            if maybe_review else list(packet["supplied_evidence_result_refs"]),
            "residual_risk":
            str(maybe_review["residual_risk"])
            if maybe_review else str(packet["residual_risk"]),
            "blocker_or_deferred_action":
            str(maybe_review["blocker_or_deferred_action"])
            if maybe_review else str(packet["blocker_or_deferred_action"]),
            "exception_ref":
            str(maybe_review["exception_ref"])
            if maybe_review else str(packet["exception_ref"]),
        })
    return rows


def build_residual_risk_register(
    final_results: list[dict[str, Any]],
    retained_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for row in final_results:
        if row["status"] in {"passed", "exception-approved"
                             } or row["demotion_status_allows_cutover"]:
            continue
        risks.append({
            "id": row["id"],
            "source": "final-demotion-criterion",
            "status": row["status"],
            "risk": row["residual_risk"],
            "owner": "release-maintainer",
            "required_action": row["demotion_blocking_reason"],
            "evidence_refs": row["evidence_refs"],
        })
    for row in retained_rows:
        if row["status"] in {"accepted", "deferred-approved-exception"}:
            continue
        risks.append({
            "id": row["id"],
            "source": "retained-code-packet",
            "status": row["status"],
            "risk": row["residual_risk"],
            "owner": row["owner"],
            "required_action": row["blocker_or_deferred_action"],
            "evidence_refs": row["supplied_evidence_result_refs"],
        })
    return risks


def count_statuses(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def requirement_coverage(
        packets: list[dict[str, Any]],
        criteria: list[dict[str, Any]]) -> dict[str, list[str]]:
    coverage = {
        requirement_id: []
        for requirement_id in sorted(REQUIRED_REQUIREMENT_IDS)
    }
    for row in [*packets, *criteria]:
        row_id = str(row["id"])
        for requirement_id in row["requirement_ids"]:
            if requirement_id in coverage:
                coverage[requirement_id].append(row_id)
    return coverage


def decision_input_template(contract: dict[str, Any]) -> dict[str, Any]:
    first_packet = contract["retained_code_acceptance_packets"][0]
    first_criterion = contract["final_demotion_criteria"][0]
    exception_template = {
        "scope": "phase18-final-review",
        "rationale": "Describe why an exception is justified.",
        "approver": "maintainer-name",
        "approver_role": "release-maintainer",
        "affected_printer_or_release_surface": "supported-release-surface",
        "mitigation_or_follow_up":
        "Follow-up required before reference demotion.",
        "expiry_or_review_trigger": "before-reference-demotion",
        "evidence_refs": ["external://phase18/example-evidence"],
    }
    return {
        "decision_packet": {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        },
        "retained_code_reviews": [{
            "packet_id":
            first_packet["id"],
            "status":
            "pending-maintainer-review",
            "approver":
            "maintainer-name",
            "approver_role":
            first_packet["approver_role"],
            "decision_timestamp":
            "2026-06-20T00:00:00Z",
            "rationale":
            "Describe retained-code packet disposition.",
            "supplied_evidence_result_refs":
            ["external://phase18/example-retained-evidence"],
            "residual_risk":
            "Describe residual retained-code risk.",
            "blocker_or_deferred_action":
            "Describe required follow-up.",
            "exception_ref":
            "none",
            "redaction_summary":
            "Name-only and redacted references only.",
        }],
        "final_criterion_decisions": [{
            "decision_id":
            f"decision-{first_criterion['id']}",
            "criterion_id":
            first_criterion["id"],
            "decision":
            "approve",
            "status":
            "pending",
            "approver":
            "maintainer-name",
            "approver_role":
            "release-maintainer",
            "decision_timestamp":
            "2026-06-20T00:00:00Z",
            "rationale":
            "Describe final criterion disposition.",
            "evidence_refs": ["external://phase18/example-final-evidence"],
            "residual_risk":
            "Describe residual final criterion risk.",
            "exception":
            exception_template,
            "redaction_summary":
            "Name-only and redacted references only.",
        }],
    }


def redacted_report_text(
    run_manifest: dict[str, Any],
    final_results: list[dict[str, Any]],
    retained_rows: list[dict[str, Any]],
    upstream_consumption: dict[str, dict[str, Any]],
) -> str:
    lines = [
        "# Phase 18 Cutover Review",
        "",
        "Review material only; machine-readable gate rows and maintainer decision input determine final status.",
        "",
        f"phase: {PHASE}",
        f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
        f"decision_inputs_supplied: {str(run_manifest['decision_inputs_supplied']).lower()}",
        f"upstream_results_supplied: {str(run_manifest['upstream_results_supplied']).lower()}",
        f"demotion_allowed: {str(run_manifest['demotion_allowed']).lower()}",
        "",
        "## Final Criteria",
    ]
    for row in final_results:
        lines.append(
            f"- {row['id']}: decision={row['status']} upstream={row['upstream_result_status']} ({row['evidence_family']})"
        )
        for reason in row["upstream_blocking_reasons"]:
            lines.append(f"  - upstream blocker: {reason}")
    lines.extend(["", "## Upstream Result Consumption"])
    for row in upstream_consumption.values():
        lines.append(
            f"- {row['criterion_id']}: {row['upstream_result_status']}")
    lines.extend(["", "## Retained Packets"])
    for row in retained_rows:
        lines.append(
            f"- {row['id']}: {row['status']} ({', '.join(row['taxonomy_tags'])})"
        )
    return "\n".join(lines) + "\n"


def write_quick_artifacts(
    root: Path,
    contract: dict[str, Any],
    decision_input: dict[str, Any] | None,
    upstream_results: dict[str, Any] | None,
    output_dir_arg: str,
) -> dict[str, Any]:
    output_dir = contained_output_dir(root, output_dir_arg)
    packets = contract_packets(contract)
    criteria = contract_final_criteria(contract)
    upstream_requirements = requirements_by_criterion(contract)
    retained_reviews, final_decisions = validated_decision_maps(
        decision_input, packets, criteria)
    validate_retained_acceptance_consistency(packets, retained_reviews,
                                             final_decisions)
    upstream_consumption = normalize_upstream_consumption(
        criteria, upstream_results, upstream_requirements, final_decisions)
    final_results = normalize_final_results(criteria, final_decisions,
                                            upstream_consumption)
    retained_rows = normalize_retained_reviews(packets, retained_reviews)
    decision_inputs_supplied = decision_input is not None
    upstream_results_supplied = upstream_results is not None
    allowed = demotion_allowed(decision_inputs_supplied,
                               upstream_results_supplied, final_results)
    artifacts = generated_artifact_paths(output_dir)
    output_dir_relative = output_dir.relative_to(root)
    snapshot_relative = Path(
        "source-contract-snapshots/phase18_cutover_review_contract.json")
    run_manifest = {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "artifact_name":
        contract["artifact_name"],
        "command_mode":
        "quick",
        "output_root":
        output_dir_relative.as_posix(),
        "decision_inputs_supplied":
        decision_inputs_supplied,
        "upstream_results_supplied":
        upstream_results_supplied,
        "demotion_allowed":
        allowed,
        "requirement_coverage":
        requirement_coverage(packets, criteria),
        "status_counts": {
            "final": count_statuses(final_results),
            "retained": count_statuses(retained_rows),
            "upstream": count_statuses(list(upstream_consumption.values())),
        },
        "retained_packet_status_counts":
        count_statuses(retained_rows),
        "final_criterion_status_counts":
        count_statuses(final_results),
        "upstream_result_status_counts":
        count_statuses(list(upstream_consumption.values())),
        "source_contract_snapshot_path":
        (output_dir_relative / snapshot_relative).as_posix(),
        "generated_artifacts":
        [(output_dir_relative / artifact).as_posix()
         for artifact in sorted(REQUIRED_GENERATED_ARTIFACTS)],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifacts["normalized-final-demotion-results.json"], {
        "results": final_results,
        "demotion_allowed": allowed
    })
    write_json(
        artifacts["upstream-result-consumption.json"],
        {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "upstream_results_supplied": upstream_results_supplied,
            "results": list(upstream_consumption.values()),
        },
    )
    write_json(artifacts["retained-code-acceptance-summary.json"],
               {"packets": retained_rows})
    write_json(
        artifacts["residual-risk-register.json"],
        {"risks": build_residual_risk_register(final_results, retained_rows)})
    write_json(artifacts["maintainer-decision-input-template.json"],
               decision_input_template(contract))
    snapshot_path = artifacts[
        "source-contract-snapshots/phase18_cutover_review_contract.json"]
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / CONTRACT_MANIFEST, snapshot_path)
    write_json(artifacts["run-manifest.json"], run_manifest)
    artifacts["redacted-readiness-report.md"].write_text(
        redacted_report_text(run_manifest, final_results, retained_rows,
                             upstream_consumption),
        encoding="utf-8",
    )
    expected_final_statuses = {
        row["id"]: row["status"]
        for row in final_results
    }
    expected_final_allows = {
        row["id"]: bool(row["demotion_status_allows_cutover"])
        for row in final_results
    }
    expected_retained_statuses = {
        row["id"]: row["status"]
        for row in retained_rows
    }
    from phase18_cutover_security import run_security_scan

    run_security_scan(
        root,
        None,
        None,
        output_dir,
        decision_input_validated=decision_input is not None,
        upstream_results_validated=upstream_results is not None,
        expected_demotion_allowed=allowed,
        expected_final_statuses=expected_final_statuses,
        expected_final_allows=expected_final_allows,
        expected_retained_statuses=expected_retained_statuses,
        expected_upstream_statuses={
            row["criterion_id"]: row["upstream_result_status"]
            for row in upstream_consumption.values()
        },
    )
    return run_manifest
