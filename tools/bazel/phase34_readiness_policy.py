from __future__ import annotations


def coverage_for_row(
    expected: dict[str, Any],
    maybe_blocker: dict[str, Any] | None,
    duplicate_classification: bool,
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    problem_kind = str(expected["row_problem_kind"])
    reason_codes: list[str] = []
    if expected["duplicate_source_ref"]:
        reason_codes.append("duplicate-row")
    if problem_kind == "missing":
        reason_codes.append("required-row-missing")
        coverage_state = "required-row-missing"
        readiness_effect = "blocked"
        affected_gates = [str(expected["expected_gate"])]
        blocker_kind = "missing_required_evidence"
        severity = "critical"
        classification_ref = ""
        retained_refs = []
        residual_refs = []
        exception_refs = []
    elif maybe_blocker is None and problem_kind:
        reason_codes.append("underclassified")
        coverage_state = "underclassified"
        readiness_effect = "blocked"
        affected_gates: list[str] = []
        blocker_kind = ""
        severity = "critical"
        classification_ref = ""
        retained_refs: list[str] = []
        residual_refs: list[str] = []
        exception_refs: list[str] = []
    elif maybe_blocker is None:
        coverage_state = "clean-no-blocker"
        readiness_effect = "unblocked"
        affected_gates = []
        blocker_kind = ""
        severity = ""
        classification_ref = ""
        retained_refs = []
        residual_refs = []
        exception_refs = []
    else:
        blocker_id = str(maybe_blocker.get("row_id") or "")
        classification_ref = f"{PHASE32_REGISTER_REF}#{blocker_id}"
        affected_gate = str(maybe_blocker.get("affected_gate") or "")
        affected_gates = [affected_gate] if affected_gate else []
        problem_kind = str(
            maybe_blocker.get("row_problem_kind") or problem_kind
            or "unknown_unclassified")
        blocker_kind = str(
            maybe_blocker.get("blocker_kind") or "unresolved_decision_blocker")
        severity = str(maybe_blocker.get("severity") or "critical")
        reason_codes.append(
            PROBLEM_REASON_CODES.get(problem_kind, "unknown-classification"))
        retained = decisions_for(decisions, "retained_code",
                                 classification_ref, affected_gate)
        residual = decisions_for(decisions, "residual_risk",
                                 classification_ref, affected_gate)
        exceptions = decisions_for(decisions, "exception", classification_ref,
                                   affected_gate)
        retained_refs = decision_refs(retained)
        residual_refs = decision_refs(residual)
        exception_refs = decision_refs(exceptions)
        covered = any(
            row.get("decision_value") in {"accept", "exception_approve"}
            for row in retained)
        covered = covered or any(
            row.get("decision_value") == "accept" for row in residual)
        exception_approved = any(
            row.get("decision_value") == "approve" for row in exceptions)
        if problem_kind in HARD_BLOCKER_PROBLEM_KINDS:
            covered = False
            exception_approved = False
        if blocker_kind == "exception_request":
            if exception_approved:
                coverage_state = "exception-covered"
                readiness_effect = "unblocked"
                reason_codes = []
            else:
                coverage_state = "exception-uncovered"
                readiness_effect = "blocked"
                reason_codes.append("exception-uncovered")
        elif covered:
            coverage_state = "decision-covered"
            readiness_effect = "unblocked"
            reason_codes = []
        else:
            coverage_state = "classified-blocker"
            readiness_effect = "blocked"
    if duplicate_classification:
        coverage_state = "duplicate-classification"
        readiness_effect = "blocked"
        reason_codes.append("duplicate-row")
    if expected["duplicate_source_ref"]:
        readiness_effect = "blocked"
    readiness_decisions = [
        row for row in decisions
        if row.get("decision_type") == "readiness" and (
            not classification_ref
            or classification_ref in row.get("source_row_refs", []))
    ]
    row = {
        "row_id": expected["row_id"],
        "ledger_row_kind": expected["ledger_row_kind"],
        "source_domain": expected["source_domain"],
        "producer_phase": expected["producer_phase"],
        "producer_artifact_kind": expected["producer_artifact_kind"],
        "source_row_kind": expected["source_row_kind"],
        "source_subject_id": expected["source_subject_id"],
        "decision_axis": expected["decision_axis"],
        "decision_subject_id": expected["decision_subject_id"],
        "phase_lifecycle_id": expected["phase_lifecycle_id"],
        "source_stream": expected["source_stream"],
        "source_ref": expected["source_ref"],
        "requirement_ids": expected["requirement_ids"],
        "affected_gates": affected_gates,
        "proof_eligibility": expected["proof_eligibility"],
        "evidence_status": expected["evidence_status"],
        "row_problem_kind": problem_kind,
        "blocker_kind": blocker_kind,
        "severity": severity,
        "evidence_refs": expected["evidence_refs"],
        "artifact_refs": expected["artifact_refs"],
        "classification_ref": classification_ref,
        "retained_code_decision_refs": retained_refs,
        "residual_risk_decision_refs": residual_refs,
        "exception_decision_refs": exception_refs,
        "readiness_decision_refs": decision_refs(readiness_decisions),
        "demotion_decision_refs": [],
        "coverage_state": coverage_state,
        "readiness_effect": readiness_effect,
        "reason_codes": sorted(set(reason_codes)),
    }
    return row


def is_decision_domain_row(row: dict[str, Any]) -> bool:
    return (row.get("producer_phase") in DECISION_DOMAIN_PRODUCER_PHASES
            and row.get("source_domain") in {"retained_code", "readiness"}
            and row.get("decision_axis") in set(PHASE33_DECISION_AXES.values())
            and all(
                isinstance(row.get(field), str) and row[field].strip()
                for field in (
                    "row_id",
                    "producer_artifact_kind",
                    "source_row_kind",
                    "source_subject_id",
                    "decision_subject_id",
                )))


def derive_decision_domain_rows(
    blocker_rows: list[dict[str, Any]], ) -> list[dict[str, Any]]:
    rows = []
    for blocker in blocker_rows:
        if not is_decision_domain_row(blocker):
            continue
        row = dict(blocker)
        row["phase_lifecycle_id"] = str(
            blocker.get("phase_lifecycle_id") or PHASE32_LIFECYCLE_ID)
        rows.append(row)
    return sorted(
        rows,
        key=lambda row: (
            str(row["row_id"]),
            str(row["decision_axis"]),
            str(row["decision_subject_id"]),
        ),
    )


def canonical_decision_ref(decision: dict[str, Any]) -> str:
    return ("build/ci-evidence/phase33/normalized-decision-records.json#"
            f"{decision.get('decision_id')}")


def decision_targets_domain_rows(
    decision: dict[str, Any],
    decision_rows: list[dict[str, Any]],
) -> bool:
    row_refs = {
        f"{PHASE32_REGISTER_REF}#{row['row_id']}"
        for row in decision_rows
    }
    axis_subjects = {(str(row["decision_axis"]),
                      str(row["decision_subject_id"]))
                     for row in decision_rows}
    raw_targets = decision.get("decision_targets")
    if not isinstance(raw_targets, list):
        return False
    for target in raw_targets:
        if not isinstance(target, dict):
            continue
        if target.get("row_ref") in row_refs:
            return True
        if (
                str(target.get("decision_axis") or ""),
                str(target.get("decision_subject_id") or ""),
        ) in axis_subjects:
            return True
    return False


def decision_domain_ledger_row(
    canonical_row: dict[str, Any],
    reconciliation: dict[str, Any],
) -> dict[str, Any]:
    decision_refs_by_axis = {
        "retained_code": [],
        "residual_risk": [],
        "exception": [],
        "readiness": [],
        "demotion": [],
    }
    decision_refs_by_axis[str(canonical_row["decision_axis"])] = list(
        reconciliation["linked_decision_refs"])
    affected_gate = str(canonical_row.get("affected_gate") or "")
    return {
        "row_id":
        str(canonical_row["row_id"]),
        "ledger_row_kind":
        "decision-domain",
        "source_domain":
        str(canonical_row["source_domain"]),
        "producer_phase":
        str(canonical_row["producer_phase"]),
        "producer_artifact_kind":
        str(canonical_row["producer_artifact_kind"]),
        "source_row_kind":
        str(canonical_row["source_row_kind"]),
        "source_subject_id":
        str(canonical_row["source_subject_id"]),
        "decision_axis":
        str(canonical_row["decision_axis"]),
        "decision_subject_id":
        str(canonical_row["decision_subject_id"]),
        "phase_lifecycle_id":
        str(canonical_row["phase_lifecycle_id"]),
        "source_stream":
        str(canonical_row.get("source_stream") or "unknown"),
        "source_ref":
        str(canonical_row.get("source_ref") or ""),
        "requirement_ids":
        sorted(
            {str(value)
             for value in canonical_row.get("requirement_ids", [])}),
        "affected_gates": [affected_gate] if affected_gate else [],
        "proof_eligibility":
        str(canonical_row.get("proof_eligibility") or "ineligible"),
        "evidence_status":
        "decision-domain",
        "row_problem_kind":
        str(canonical_row.get("row_problem_kind") or "unknown_unclassified"),
        "blocker_kind":
        str(
            canonical_row.get("blocker_kind")
            or "unresolved_decision_blocker"),
        "severity":
        str(canonical_row.get("severity") or "critical"),
        "evidence_refs":
        sorted({
            str(ref)
            for ref in canonical_row.get("evidence_refs", [])
            if isinstance(ref, str)
        }),
        "artifact_refs":
        sorted({
            str(ref)
            for ref in canonical_row.get("artifact_refs", [])
            if isinstance(ref, str)
        }),
        "classification_ref":
        (f"{PHASE32_REGISTER_REF}#{canonical_row['row_id']}"),
        "retained_code_decision_refs":
        decision_refs_by_axis["retained_code"],
        "residual_risk_decision_refs":
        decision_refs_by_axis["residual_risk"],
        "exception_decision_refs":
        decision_refs_by_axis["exception"],
        "readiness_decision_refs":
        decision_refs_by_axis["readiness"],
        "demotion_decision_refs":
        decision_refs_by_axis["demotion"],
        "coverage_state":
        reconciliation["coverage_state"],
        "readiness_effect":
        reconciliation["readiness_effect"],
        "reason_codes":
        list(reconciliation["reason_codes"]),
    }


def decision_diagnostic_row(
    diagnostic: dict[str, str],
    index: int,
    decisions_by_ref: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    decision_ref = str(
        diagnostic.get("decision_ref") or f"decision-diagnostic-{index}")
    maybe_decision = decisions_by_ref.get(decision_ref)
    decision_axis = (str(maybe_decision.get("decision_axis") or "")
                     if maybe_decision is not None else "")
    readiness_effect = ("independent"
                        if decision_axis == "demotion" else "blocked")
    return {
        "row_id":
        stable_row_id(
            "decision-diagnostic",
            f"{decision_ref}\0{diagnostic.get('reason_code')}\0{index}",
        ),
        "ledger_row_kind":
        "decision-domain",
        "source_domain":
        "phase33_decision",
        "producer_phase":
        "phase33",
        "producer_artifact_kind":
        "normalized_decision_records",
        "source_row_kind":
        "decision_diagnostic",
        "source_subject_id":
        decision_ref,
        "decision_axis":
        decision_axis,
        "decision_subject_id":
        "",
        "phase_lifecycle_id":
        PHASE33_LIFECYCLE_ID,
        "source_stream":
        "phase33-decision",
        "source_ref":
        decision_ref,
        "requirement_ids":
        REQUIRED_REQUIREMENT_IDS,
        "affected_gates": [],
        "proof_eligibility":
        "ineligible",
        "evidence_status":
        "invalid",
        "row_problem_kind":
        "unknown_unclassified",
        "blocker_kind":
        "unresolved_decision_blocker",
        "severity":
        "critical",
        "evidence_refs": [],
        "artifact_refs": [],
        "classification_ref":
        "",
        "retained_code_decision_refs":
        ([decision_ref] if decision_axis == "retained_code" else []),
        "residual_risk_decision_refs":
        ([decision_ref] if decision_axis == "residual_risk" else []),
        "exception_decision_refs":
        ([decision_ref] if decision_axis == "exception" else []),
        "readiness_decision_refs":
        ([decision_ref] if decision_axis == "readiness" else []),
        "demotion_decision_refs":
        ([decision_ref] if decision_axis == "demotion" else []),
        "coverage_state":
        "blocked",
        "readiness_effect":
        readiness_effect,
        "reason_codes": [str(diagnostic["reason_code"])],
    }


def evaluate_coverage(
    receipts: list[dict[str, Any]],
    blocker_rows: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    required_streams: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    expected_rows = derive_evidence_rows(receipts, required_streams)
    decision_domain_rows = derive_decision_domain_rows(blocker_rows)
    blocker_id_counts: dict[str, int] = {}
    blockers_by_join_key: dict[tuple[str, str],
                               list[tuple[int, dict[str, Any]]]] = {}
    blockers_by_id: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, blocker in enumerate(blocker_rows):
        if is_decision_domain_row(blocker):
            continue
        blocker_id = str(blocker.get("row_id") or "")
        blocker_id_counts[blocker_id] = blocker_id_counts.get(blocker_id,
                                                              0) + 1
        join_key = (
            str(blocker.get("source_ref") or ""),
            str(blocker.get("affected_gate") or ""),
        )
        blockers_by_join_key.setdefault(join_key, []).append((index, blocker))
        blockers_by_id.setdefault(blocker_id, []).append((index, blocker))

    ledger: list[dict[str, Any]] = []
    matched_blocker_indices: set[int] = set()
    for expected in expected_rows:
        join_key = (str(expected["source_ref"]),
                    str(expected["expected_gate"]))
        matches = [
            (index, blocker)
            for index, blocker in blockers_by_join_key.get(join_key, [])
            if blocker.get("source_stream") == expected["source_stream"]
        ]
        matches.sort(key=lambda item: (str(item[1].get("row_id") or ""),
                                       json.dumps(item[1], sort_keys=True)))
        matched_blocker_indices.update(index for index, _ in matches)
        maybe_blocker = matches[0][1] if matches else None
        duplicate_classification = len(matches) > 1
        if maybe_blocker is not None:
            blocker_id = str(maybe_blocker.get("row_id") or "")
            duplicate_classification = duplicate_classification or blocker_id_counts.get(
                blocker_id, 0) > 1
        ledger.append(
            coverage_for_row(expected, maybe_blocker, duplicate_classification,
                             decisions))

    domain_decisions = [
        {
            **decision,
            "decision_ref": canonical_decision_ref(decision),
        } for decision in decisions
        if decision_targets_domain_rows(decision, decision_domain_rows)
    ]
    handled_decision_ids = {
        str(decision.get("decision_id") or "")
        for decision in domain_decisions
    }
    if decision_domain_rows:
        reconciliation = reconcile_decision_rows(
            decision_domain_rows,
            domain_decisions,
            expected_phase32_lifecycle_id=PHASE32_LIFECYCLE_ID,
            expected_phase33_lifecycle_id=PHASE33_LIFECYCLE_ID,
        )
        results_by_identity = {
            (
                str(result["row_id"]),
                str(result["decision_axis"]),
                str(result["decision_subject_id"]),
            ):
            result
            for result in reconciliation["rows"]
        }
        decisions_by_ref = {
            str(decision["decision_ref"]): decision
            for decision in domain_decisions
        }
        blocking_diagnostics = [
            diagnostic for diagnostic in reconciliation["diagnostics"]
            if (decisions_by_ref.get(
                str(diagnostic.get("decision_ref") or ""),
                {},
            ).get("decision_axis") != "demotion")
        ]
        prerequisites_blocked = (any(row["readiness_effect"] == "blocked"
                                     for row in ledger) or
                                 any(result["readiness_effect"] == "blocked"
                                     and result["decision_axis"] != "readiness"
                                     for result in reconciliation["rows"])
                                 or bool(blocking_diagnostics))
        if prerequisites_blocked:
            for result in results_by_identity.values():
                if (result["decision_axis"] == "readiness"
                        and result["readiness_effect"] == "unblocked"):
                    result["coverage_state"] = "blocked"
                    result["readiness_effect"] = "blocked"
                    result["reason_codes"] = [
                        "decision-readiness-prerequisites-blocked"
                    ]
        for canonical_row in decision_domain_rows:
            identity = (
                str(canonical_row["row_id"]),
                str(canonical_row["decision_axis"]),
                str(canonical_row["decision_subject_id"]),
            )
            maybe_result = results_by_identity.get(identity)
            if maybe_result is None:
                continue
            ledger.append(
                decision_domain_ledger_row(canonical_row, maybe_result))
        for diagnostic_index, diagnostic in enumerate(
                reconciliation["diagnostics"]):
            ledger.append(
                decision_diagnostic_row(
                    diagnostic,
                    diagnostic_index,
                    decisions_by_ref,
                ))

    duplicate_blocker_ids = {
        blocker_id
        for blocker_id, count in blocker_id_counts.items() if count > 1
    }
    for index, blocker in enumerate(blocker_rows):
        if index in matched_blocker_indices or is_decision_domain_row(blocker):
            continue
        reasons = ["dangling-row-ref"]
        if str(blocker.get("row_id") or "") in duplicate_blocker_ids:
            reasons.append("duplicate-row")
        ledger.append(dangling_blocker_row(blocker, index, reasons))

    decision_id_counts: dict[str, int] = {}
    for decision in decisions:
        decision_id = str(decision.get("decision_id") or "")
        decision_id_counts[decision_id] = decision_id_counts.get(
            decision_id, 0) + 1
    for index, decision in enumerate(decisions):
        if str(decision.get("decision_id") or "") in handled_decision_ids:
            continue
        reasons = dangling_decision_reasons(
            decision,
            blockers_by_id,
            matched_blocker_indices,
        )
        if decision_id_counts.get(str(decision.get("decision_id") or ""),
                                  0) > 1:
            reasons.append("duplicate-row")
        if reasons:
            ledger.append(
                dangling_decision_row(decision, index, sorted(set(reasons))))
    return ledger
