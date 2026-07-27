from __future__ import annotations


def dangling_blocker_row(
    blocker: dict[str, Any],
    index: int,
    reason_codes: list[str],
) -> dict[str, Any]:
    blocker_id = str(blocker.get("row_id") or f"row-{index}")
    affected_gate = str(blocker.get("affected_gate") or "")
    source_ref = str(blocker.get("source_ref") or "")
    return {
        "row_id":
        stable_row_id("dangling-phase32",
                      f"{blocker_id}\0{index}\0{source_ref}\0{affected_gate}"),
        "ledger_row_kind":
        "decision-domain",
        "source_domain":
        str(blocker.get("source_domain") or "unknown"),
        "producer_phase":
        str(blocker.get("producer_phase") or "phase32"),
        "producer_artifact_kind":
        str(
            blocker.get("producer_artifact_kind")
            or "unmatched_blocker_register_row"),
        "source_row_kind":
        str(blocker.get("source_row_kind") or "unmatched_blocker"),
        "source_subject_id":
        str(blocker.get("source_subject_id") or blocker_id),
        "decision_axis":
        str(blocker.get("decision_axis") or ""),
        "decision_subject_id":
        str(blocker.get("decision_subject_id") or ""),
        "phase_lifecycle_id":
        str(blocker.get("phase_lifecycle_id") or PHASE32_LIFECYCLE_ID),
        "source_stream":
        str(blocker.get("source_stream") or "unknown"),
        "source_ref":
        source_ref,
        "requirement_ids":
        sorted({str(value)
                for value in blocker.get("requirement_ids", [])}),
        "affected_gates": [affected_gate] if affected_gate else [],
        "proof_eligibility":
        str(blocker.get("proof_eligibility") or "ineligible"),
        "evidence_status":
        "unmatched",
        "row_problem_kind":
        str(blocker.get("row_problem_kind") or "unknown_unclassified"),
        "blocker_kind":
        str(blocker.get("blocker_kind") or "unresolved_decision_blocker"),
        "severity":
        str(blocker.get("severity") or "critical"),
        "evidence_refs":
        sorted({
            str(ref)
            for ref in blocker.get("evidence_refs", [])
            if isinstance(ref, str)
        }),
        "artifact_refs": [],
        "classification_ref":
        f"{PHASE32_REGISTER_REF}#{blocker_id}",
        "retained_code_decision_refs": [],
        "residual_risk_decision_refs": [],
        "exception_decision_refs": [],
        "readiness_decision_refs": [],
        "demotion_decision_refs": [],
        "coverage_state":
        "dangling-blocker",
        "readiness_effect":
        "blocked",
        "reason_codes":
        sorted(set(reason_codes)),
    }


def dangling_decision_reasons(
    decision: dict[str, Any],
    blockers_by_id: dict[str, list[tuple[int, dict[str, Any]]]],
    matched_blocker_indices: set[int],
) -> list[str]:
    source_refs = decision.get("source_row_refs")
    if not isinstance(source_refs, list) or not source_refs:
        return ["dangling-row-ref"]
    affected_gates = {
        str(value)
        for value in decision.get("affected_gates", [])
        if isinstance(value, str)
    }
    prefix = f"{PHASE32_REGISTER_REF}#"
    reasons: list[str] = []
    for source_ref in source_refs:
        if not isinstance(source_ref,
                          str) or not source_ref.startswith(prefix):
            reasons.append("dangling-row-ref")
            continue
        blocker_id = source_ref[len(prefix):]
        matches = blockers_by_id.get(blocker_id, [])
        if len(matches) != 1:
            reasons.append("dangling-row-ref")
            if len(matches) > 1:
                reasons.append("duplicate-row")
            continue
        blocker_index, blocker = matches[0]
        if blocker_index not in matched_blocker_indices:
            reasons.append("dangling-row-ref")
        affected_gate = str(blocker.get("affected_gate") or "")
        if not affected_gate or affected_gate not in affected_gates:
            reasons.append("dangling-row-ref")
    return reasons


def dangling_decision_row(
    decision: dict[str, Any],
    index: int,
    reason_codes: list[str],
) -> dict[str, Any]:
    decision_id = str(decision.get("decision_id") or f"decision-{index}")
    decision_ref = f"build/ci-evidence/phase33/normalized-decision-records.json#{decision_id}"
    source_refs = [
        str(ref) for ref in decision.get("source_row_refs", [])
        if isinstance(ref, str)
    ]
    affected_gates = sorted({
        str(value)
        for value in decision.get("affected_gates", [])
        if isinstance(value, str) and value
    })
    return {
        "row_id":
        stable_row_id("dangling-phase33", f"{decision_id}\0{index}"),
        "ledger_row_kind":
        "decision-domain",
        "source_domain":
        "phase33_decision",
        "producer_phase":
        "phase33",
        "producer_artifact_kind":
        "normalized_decision_records",
        "source_row_kind":
        "unmatched_decision",
        "source_subject_id":
        decision_id,
        "decision_axis":
        str(decision.get("decision_axis") or ""),
        "decision_subject_id":
        "",
        "phase_lifecycle_id":
        str(decision.get("phase_lifecycle_id") or PHASE33_LIFECYCLE_ID),
        "source_stream":
        "phase33-decision",
        "source_ref":
        decision_ref,
        "requirement_ids":
        REQUIRED_REQUIREMENT_IDS,
        "affected_gates":
        affected_gates,
        "proof_eligibility":
        "ineligible",
        "evidence_status":
        "unmatched",
        "row_problem_kind":
        "unknown_unclassified",
        "blocker_kind":
        "unresolved_decision_blocker",
        "severity":
        "critical",
        "evidence_refs":
        sorted(set(source_refs)),
        "artifact_refs":
        sorted({
            str(ref)
            for ref in decision.get("artifact_refs", [])
            if isinstance(ref, str)
        }),
        "classification_ref":
        "",
        "retained_code_decision_refs": [],
        "residual_risk_decision_refs": [],
        "exception_decision_refs": [],
        "readiness_decision_refs":
        [decision_ref] if decision.get("decision_type") == "readiness" else [],
        "demotion_decision_refs":
        [decision_ref] if decision.get("decision_axis") == "demotion" else [],
        "coverage_state":
        "dangling-decision",
        "readiness_effect": ("independent" if decision.get("decision_axis")
                             == "demotion" else "blocked"),
        "reason_codes":
        reason_codes,
    }


def evaluate_demotion(
    readiness_state: str,
    approval_validation_state: str,
    approval_decision_state: str,
    source_refs: list[str],
) -> dict[str, Any]:
    reason_codes = []
    if readiness_state != "unblocked":
        reason_codes.append("readiness-input-invalid")
    if approval_validation_state == "missing":
        reason_codes.append("approval-missing")
    elif approval_validation_state != "valid":
        reason_codes.append("approval-invalid")
    if approval_decision_state == "missing" and "approval-missing" not in reason_codes:
        reason_codes.append("approval-missing")
    elif approval_decision_state == "reject":
        reason_codes.append("approval-rejected")
    gate_state = "open"
    if (readiness_state, approval_validation_state,
            approval_decision_state) != ("unblocked", "valid", "approve"):
        gate_state = "blocked"
    return {
        "readiness_state": readiness_state,
        "approval_validation_state": approval_validation_state,
        "approval_decision_state": approval_decision_state,
        "gate_state": gate_state,
        "reason_codes": sorted(set(reason_codes)),
        "source_refs": sorted(set(source_refs)),
    }


def load_phase31(
    root: Path, output_arg: str | Path
) -> tuple[Path, dict[str, Any], list[dict[str, Any]], list[str]]:
    output_dir = path_under(output_arg, DEFAULT_PHASE31_OUTPUT_DIR,
                            "--phase31-output-dir")
    resolved_under(root, output_dir, DEFAULT_PHASE31_OUTPUT_DIR,
                   "--phase31-output-dir")
    manifest_path = output_dir / "final-intake-manifest.json"
    manifest = load_json(root, manifest_path)
    scan_json(manifest, manifest_path)
    if manifest.get("artifact_name") != "phase31-final-evidence-intake":
        raise VerificationError(
            "Phase 31 manifest artifact_name must be phase31-final-evidence-intake"
        )
    if manifest.get("phase_lifecycle_id") != PHASE31_LIFECYCLE_ID:
        raise VerificationError(
            f"Phase 31 manifest phase_lifecycle_id must be {PHASE31_LIFECYCLE_ID}"
        )
    if manifest.get("output_root") != output_dir.as_posix():
        raise VerificationError(
            "Phase 31 manifest output_root must match --phase31-output-dir")
    receipt_refs = string_list(manifest.get("receipt_refs"),
                               "Phase 31 receipt_refs")
    receipts: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]] = []
    for receipt_ref in sorted(receipt_refs):
        receipt_path = path_under(receipt_ref, output_dir,
                                  "Phase 31 receipt_ref")
        resolved_under(root, receipt_path, output_dir, "Phase 31 receipt_ref")
        receipt = load_json(root, receipt_path)
        scan_json(receipt, receipt_path)
        if receipt.get("finality_status") != "accepted-final":
            raise VerificationError(
                f"{receipt_path.as_posix()} must have finality_status accepted-final"
            )
        receipts.append(receipt)
        snapshot_rows.append({
            "receipt_ref": receipt_path.as_posix(),
            "receipt": receipt
        })
    return manifest_path, manifest, receipts, [
        json.dumps(row, sort_keys=True) for row in snapshot_rows
    ]


def phase33_register_path(root: Path, register_refs: dict[str, Any],
                          name: str) -> Path:
    value = register_refs.get(name)
    if not isinstance(value, str):
        raise VerificationError(
            f"Phase 33 register_refs.{name} must be a path")
    register_path = path_under(value, PHASE33_OUTPUT_ROOT,
                               f"register_refs.{name}")
    resolved_under(root, register_path, PHASE33_OUTPUT_ROOT,
                   f"register_refs.{name}")
    return register_path


def load_phase33_register(root: Path, register_refs: dict[str, Any],
                          name: str) -> dict[str, Any]:
    register_path = phase33_register_path(root, register_refs, name)
    payload = load_json(root, register_path)
    scan_json(payload, register_path)
    return payload


def phase33_register_digests(root: Path,
                             register_refs: dict[str, Any]) -> dict[str, str]:
    return {
        name:
        hashlib.sha256(
            json.dumps(
                load_phase33_register(root, register_refs, name),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()).hexdigest()
        for name in sorted(register_refs)
    }


def load_phase33_handoff(
    root: Path,
    handoff_arg: str | Path,
    full_output: Path,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    raw_path = repo_relative_path(handoff_arg, "--phase33-handoff")
    resolved_input = (root / raw_path).resolve(strict=False)
    if resolved_input == full_output or full_output in resolved_input.parents:
        raise VerificationError(
            "--phase33-handoff must be outside the generated --output-dir")
    handoff_path = path_under(
        raw_path,
        PHASE33_OUTPUT_ROOT,
        "--phase33-handoff",
    )
    resolved_under(
        root,
        handoff_path,
        PHASE33_OUTPUT_ROOT,
        "--phase33-handoff",
    )
    handoff = load_json(root, handoff_path)
    scan_json(handoff, handoff_path)
    if handoff.get("artifact_name") != "phase33-maintainer-decision-inputs":
        raise VerificationError(
            "Phase 33 handoff artifact_name must be phase33-maintainer-decision-inputs"
        )
    if handoff.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        raise VerificationError(
            f"Phase 33 handoff phase_lifecycle_id must be {PHASE33_LIFECYCLE_ID}"
        )
    if handoff.get("raw_evidence_consumed") not in {None, False}:
        raise VerificationError(
            "Phase 33 handoff raw_evidence_consumed must be false")
    source_inputs = handoff.get("source_inputs")
    if (not isinstance(source_inputs, dict)
            or source_inputs.get("phase32_canonical_register_ref")
            != PHASE32_REGISTER_REF):
        raise VerificationError(
            f"Phase 33 handoff must reference {PHASE32_REGISTER_REF}")
    register_refs = handoff.get("register_refs")
    if not isinstance(register_refs, dict):
        raise VerificationError(
            "Phase 33 handoff register_refs must be an object")
    return handoff_path, handoff, register_refs


def load_phase32_blocker_register(root: Path) -> dict[str, Any]:
    blocker_register_path = Path(PHASE32_REGISTER_REF)
    resolved_under(
        root,
        blocker_register_path,
        Path("build/ci-evidence/phase32"),
        "Phase 32 blocker register",
    )
    blocker_register = load_json(root, blocker_register_path)
    scan_json(blocker_register, blocker_register_path)
    if blocker_register.get("phase_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError(
            f"Phase 32 blocker register phase_lifecycle_id must be {PHASE32_LIFECYCLE_ID}"
        )
    return blocker_register


def validate_readiness_handoff(
    readiness: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
) -> None:
    if readiness.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        raise VerificationError(
            "Phase 33 readiness handoff lifecycle is stale or malformed")
    handoff_state = readiness.get("handoff_state")
    if handoff_state == "blocked-pending-maintainer-input":
        if readiness.get("readiness_input_supplied") is not False:
            raise VerificationError(
                "blocked Phase 33 readiness handoff must not claim supplied input"
            )
        return
    if handoff_state != "approval-input-recorded":
        raise VerificationError("Phase 33 readiness handoff state is invalid")
    validate_handoff_decision(
        readiness,
        decisions_by_id,
        "readiness",
        "approve",
        ("source_row_refs", "rationale"),
    )


def validate_demotion_handoff(
    demotion: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
) -> tuple[str, str, list[str]]:
    validation, decision, source_refs, maybe_error = approval_state(
        demotion,
        decisions_by_id,
    )
    if maybe_error is not None:
        raise VerificationError(maybe_error)
    return validation, decision, source_refs


def approval_state(
    maybe_demotion: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
) -> tuple[str, str, list[str], str | None]:
    if maybe_demotion.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        return "invalid", "missing", [], "Phase 33 demotion approval lifecycle is stale or malformed"
    authorization_state = maybe_demotion.get("authorization_state")
    if authorization_state == "blocked" and maybe_demotion.get(
            "demotion_input_supplied") is False:
        return "missing", "missing", [], None
    source_refs = [
        str(ref) for ref in maybe_demotion.get("source_row_refs", [])
        if isinstance(ref, str)
    ]
    if authorization_state == "rejected":
        try:
            validate_handoff_decision(
                maybe_demotion,
                decisions_by_id,
                "reference_demotion",
                "reject",
                ("source_row_refs", "rationale"),
            )
        except VerificationError as error:
            return "invalid", "reject", source_refs, str(error)
        return "valid", "reject", source_refs, None
    if authorization_state != "approved-input-recorded":
        return "invalid", "missing", source_refs, "Phase 33 demotion approval state is invalid"
    try:
        validate_handoff_decision(
            maybe_demotion,
            decisions_by_id,
            "reference_demotion",
            "approve",
            (
                "source_row_refs",
                "maintainer_identity_ref",
                "maintainer_role",
                "decision_timestamp",
                "rationale",
            ),
        )
    except VerificationError as error:
        return "invalid", "missing", source_refs, str(error)
    return "valid", "approve", source_refs, None


def readiness_state(
    ledger: list[dict[str, Any]],
    readiness: dict[str, Any],
    decisions_by_id: dict[str, dict[str, Any]],
) -> tuple[str, list[str], str | None]:
    reason_codes = sorted({
        reason
        for row in ledger if row["readiness_effect"] == "blocked"
        for reason in row["reason_codes"]
    })
    maybe_error = None
    if not ledger:
        reason_codes.append("required-row-missing")
    if readiness.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
        reason_codes.append("readiness-input-invalid")
    elif readiness.get("handoff_state") == "approval-input-recorded":
        try:
            validate_handoff_decision(
                readiness,
                decisions_by_id,
                "readiness",
                "approve",
                ("source_row_refs", "rationale"),
            )
        except VerificationError as error:
            reason_codes.append("readiness-input-invalid")
            maybe_error = str(error)
    else:
        reason_codes.append("readiness-input-invalid")
    if any(row["readiness_effect"] == "blocked" for row in ledger):
        return "blocked", sorted(set(reason_codes)), maybe_error
    if reason_codes:
        return "blocked", sorted(set(reason_codes)), maybe_error
    return "unblocked", [], maybe_error
