from __future__ import annotations


def evaluate_verdict(facts: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(facts, dict):
        return {
            "cutover_verdict": "blocked",
            "reason_codes": ["unknown-input"],
            "active_exception_ids": []
        }
    readiness = facts.get("readiness_state")
    raw_reasons = facts.get("reason_codes")
    active_ids = facts.get("active_exception_ids")
    exceptions = facts.get("exceptions")
    if readiness not in {
            "blocked", "unblocked"
    } or not isinstance(raw_reasons, list) or not isinstance(
            active_ids, list) or not isinstance(exceptions, list):
        return {
            "cutover_verdict": "blocked",
            "reason_codes": ["unknown-input"],
            "active_exception_ids": []
        }
    reasons = sorted({
        str(reason)
        for reason in raw_reasons if isinstance(reason, str) and reason
    })
    exception_by_id = {
        row.get("decision_id"): row
        for row in exceptions
        if isinstance(row, dict) and isinstance(row.get("decision_id"), str)
    }
    exception_invalid = False
    for decision_id in active_ids:
        maybe_exception = exception_by_id.get(decision_id)
        if maybe_exception is None:
            exception_invalid = True
            continue
        maybe_timestamp = parse_timestamp(
            maybe_exception.get("decision_timestamp"))
        valid = (maybe_exception.get("decision_type") == "exception"
                 and maybe_exception.get("decision_value") == "approve"
                 and maybe_exception.get("phase_lifecycle_id")
                 == PHASE33_LIFECYCLE_ID and maybe_timestamp is not None
                 and maybe_timestamp >= STALE_BEFORE and isinstance(
                     maybe_exception.get("maintainer_identity_ref"), str)
                 and bool(maybe_exception["maintainer_identity_ref"])
                 and isinstance(maybe_exception.get("maintainer_role"), str)
                 and bool(maybe_exception["maintainer_role"])
                 and isinstance(maybe_exception.get("owner_signoff_ref"), str)
                 and bool(maybe_exception["owner_signoff_ref"])
                 and isinstance(maybe_exception.get("scope"), str)
                 and bool(maybe_exception["scope"])
                 and maybe_exception.get("linked_blocker_refs")
                 == maybe_exception.get("source_row_refs")
                 and bool(maybe_exception.get("affected_gates"))
                 and bool(maybe_exception.get("expiry_or_review_trigger")))
        if not valid:
            exception_invalid = True
    if set(exception_by_id) != set(active_ids):
        exception_invalid = True
    if exception_invalid:
        reasons.append("exception-invalid")
    reasons = sorted(set(reasons))
    if readiness != "unblocked" or reasons:
        if readiness == "blocked" and not reasons:
            reasons.append("readiness-blocked")
        verdict = "blocked"
    elif active_ids:
        verdict = "approved-with-exceptions"
    else:
        verdict = "approved"
    return {
        "cutover_verdict": verdict,
        "reason_codes": sorted(set(reasons)),
        "active_exception_ids":
        sorted(set(str(value) for value in active_ids)),
    }


def build_route(verdict: str,
                follow_up_scope: list[dict[str, Any]]) -> dict[str, Any]:
    approved = verdict == "approved"
    return {
        "artifact_name": "phase35-next-milestone-route",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "route": "production-cutover-planning"
        if approved else "targeted-blocker-repair",
        "source_verdict": verdict,
        "follow_up_scope": [] if approved else follow_up_scope,
        "requires_fresh_cutover_decision": not approved,
        "planning_only": True,
        "production_actions_authorized": False,
    }


def stable_link_id(kind: str, target_id: str, target_ref: str) -> str:
    safe_target = re.sub(r"[^a-z0-9]+", "-", target_id.casefold()).strip("-")
    if safe_target:
        return f"audit-{kind}-{safe_target}"
    digest = hashlib.sha256(f"{kind}\0{target_ref}".encode()).hexdigest()[:16]
    return f"audit-{kind}-{digest}"


def derive_audit_links(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    links = []
    for source in sources:
        kind = str(source.get("kind") or "")
        target_id = str(source.get("target_id") or "")
        target_ref = str(source.get("target_ref") or "")
        lifecycle = str(source.get("source_phase_lifecycle_id") or "")
        verdict_effect = str(source.get("verdict_effect") or "")
        if kind not in AUDIT_KINDS or not target_id or not lifecycle or not verdict_effect:
            raise VerificationError("audit source is malformed")
        validate_ref(target_ref, f"{kind}.target_ref")
        link = {
            "link_id": stable_link_id(kind, target_id, target_ref),
            "kind": kind,
            "target_id": target_id,
            "target_ref": target_ref,
            "source_phase_lifecycle_id": lifecycle,
            "verdict_effect": verdict_effect,
        }
        if not target_ref.startswith("external://"):
            digest_source = source.get("digest_source", source)
            link["digest"] = hashlib.sha256(
                canonical_json(digest_source)).hexdigest()
        links.append(link)
    return sorted(links,
                  key=lambda link: (AUDIT_KINDS.index(link["kind"]), link[
                      "target_id"], link["target_ref"]))


def validate_audit_links(expected: list[dict[str, Any]],
                         emitted: list[dict[str, Any]]) -> list[str]:
    reasons: set[str] = set()
    expected_by_id = {row["link_id"]: row for row in expected}
    emitted_ids = [row.get("link_id") for row in emitted]
    emitted_by_id = {row.get("link_id"): row for row in emitted}
    if len(emitted_ids) != len(set(emitted_ids)):
        reasons.add("audit-link-duplicate")
    if set(expected_by_id) - set(emitted_by_id):
        reasons.add("audit-link-missing")
    if set(emitted_by_id) - set(expected_by_id):
        reasons.add("audit-link-extra")
    for link_id in set(expected_by_id) & set(emitted_by_id):
        expected_row = expected_by_id[link_id]
        emitted_row = emitted_by_id[link_id]
        if emitted_row.get("kind") != expected_row.get("kind"):
            reasons.add("audit-link-category-mismatched")
        if emitted_row.get("target_ref") != expected_row.get("target_ref"):
            reasons.add("audit-link-dangling")
        if emitted_row.get("source_phase_lifecycle_id") != expected_row.get(
                "source_phase_lifecycle_id"):
            reasons.add("audit-link-lifecycle-mismatched")
        if emitted_row.get("digest") != expected_row.get("digest"):
            reasons.add("audit-link-digest-mismatched")
    return sorted(reasons)


def resolve_audit_target(root: Path, target_ref: str) -> Any:
    validate_ref(target_ref, "audit target_ref")
    path_text, separator, fragment = target_ref.partition("#")
    payload = load_json(root, Path(path_text))
    scan_security(payload, target_ref)
    if not separator:
        return payload
    if not fragment or "/" in fragment:
        raise VerificationError(
            f"audit target fragment is invalid: {target_ref}")
    for collection_name in ("rows", "receipts", "blockers"):
        rows = payload.get(collection_name)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            candidate = row.get("receipt", row)
            if not isinstance(candidate, dict):
                continue
            identities = {
                str(candidate.get(field) or "")
                for field in ("row_id", "decision_id", "submission_id")
            }
            if fragment in identities:
                return candidate
    raise VerificationError(f"audit target fragment is dangling: {target_ref}")


def validate_resolved_audit_links(root: Path,
                                  links: list[dict[str, Any]]) -> list[str]:
    reasons: set[str] = set()
    for link in links:
        target_ref = link.get("target_ref")
        if not isinstance(target_ref, str):
            reasons.add("audit-link-dangling")
            continue
        if target_ref.startswith("external://"):
            continue
        try:
            resolved = resolve_audit_target(root, target_ref)
        except VerificationError:
            reasons.add("audit-link-dangling")
            continue
        expected_digest = hashlib.sha256(canonical_json(resolved)).hexdigest()
        if link.get("digest") != expected_digest:
            reasons.add("audit-link-digest-mismatched")
    return sorted(reasons)


def referenced_decisions(
    ledger: dict[str, Any],
    ref_field: str,
    rows: list[dict[str, Any]],
    blocker_ref: str,
    reasons: set[str],
) -> list[dict[str, Any]]:
    refs = ledger.get(ref_field, [])
    if not isinstance(refs, list):
        reasons.add("route-scope-incomplete")
        return []
    prefix = f"{PHASE33_NORMALIZED_REGISTER}#"
    decision_ids = []
    for ref in refs:
        if not isinstance(
                ref,
                str) or not ref.startswith(prefix) or not ref[len(prefix):]:
            reasons.add("route-scope-incomplete")
            continue
        decision_ids.append(ref[len(prefix):])
    row_by_id = {
        str(row.get("decision_id") or ""): row
        for row in rows if row.get("decision_id")
    }
    if len(row_by_id) != len(rows) or len(
            set(decision_ids)) != len(decision_ids):
        reasons.add("route-scope-incomplete")
    matches = []
    for decision_id in sorted(set(decision_ids)):
        maybe_decision = row_by_id.get(decision_id)
        if maybe_decision is None or blocker_ref not in maybe_decision.get(
                "source_row_refs",
            []) or blocker_ref not in maybe_decision.get(
                "linked_blocker_refs", maybe_decision.get(
                    "source_row_refs", [])):
            reasons.add("route-scope-incomplete")
            continue
        matches.append(maybe_decision)
    return matches


def build_repair_scope(
    blockers: list[dict[str, Any]],
    ledger_rows: list[dict[str, Any]],
    exception_rows: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    scope = []
    reasons: set[str] = set()
    blocker_by_ref = {
        f"{PHASE32_REGISTER_REF}#{row.get('row_id')}": row
        for row in blockers if row.get("row_id")
    }
    route_rows = [
        row for row in ledger_rows if row.get("readiness_effect") == "blocked"
        or row.get("coverage_state") == "exception-covered"
    ]
    if not route_rows:
        reasons.add("route-scope-incomplete")
    for ledger in sorted(route_rows,
                         key=lambda row: str(row.get("row_id", ""))):
        ledger_row_id = str(ledger.get("row_id") or "")
        ledger_ref = f"{PHASE34_LEDGER_REF}#{ledger_row_id}"
        classification_ref = str(ledger.get("classification_ref") or "")
        maybe_blocker = blocker_by_ref.get(classification_ref)
        if not ledger_row_id:
            reasons.add("route-scope-incomplete")
            continue
        if ("reason_codes" not in ledger
                or not isinstance(ledger.get("requirement_ids"), list)
                or not isinstance(ledger.get("affected_gates"), list)):
            reasons.add("route-scope-incomplete")
            continue
        if maybe_blocker is None and classification_ref:
            reasons.add("route-scope-incomplete")
            continue
        if maybe_blocker is None:
            source_stream = re.sub(
                r"[^a-z0-9-]+", "-",
                str(ledger.get("source_stream") or "unknown").casefold())
            blocker_refs = [ledger_ref]
            owner_ref = f"owner://phase34/{source_stream}"
            required_action_ref = f"{ledger_ref}/source_ref"
            criteria = [
                f"{ledger_ref}/source_ref",
                f"{ledger_ref}/reason_codes",
                f"{ledger_ref}/readiness_effect",
            ]
        else:
            required = ("owner_ref", "required_next_action", "requirement_ids",
                        "affected_gate")
            if any(field not in maybe_blocker for field in required):
                reasons.add("route-scope-incomplete")
                continue
            blocker_refs = [ledger_ref, classification_ref]
            owner_ref = str(maybe_blocker["owner_ref"])
            required_action_ref = f"{classification_ref}/required_next_action"
            criteria = [
                f"{classification_ref}/affected_gate",
                f"{classification_ref}/required_next_action",
                f"{ledger_ref}/reason_codes",
                f"{ledger_ref}/readiness_effect",
            ]
        exception_matches = referenced_decisions(
            ledger,
            "exception_decision_refs",
            exception_rows,
            classification_ref,
            reasons,
        )
        residual_matches = referenced_decisions(
            ledger,
            "residual_risk_decision_refs",
            residual_rows,
            classification_ref,
            reasons,
        )
        if ledger.get("coverage_state"
                      ) == "exception-covered" and not exception_matches:
            reasons.add("route-scope-incomplete")
        valid_exception_matches = []
        for decision in exception_matches:
            decision_id = str(decision.get("decision_id") or "")
            if not decision_id or not decision.get(
                    "expiry_or_review_trigger") or not decision.get(
                        "affected_gates"):
                reasons.add("route-scope-incomplete")
                continue
            valid_exception_matches.append(decision)
            criteria.extend([
                f"{PHASE33_EXCEPTION_REGISTER}#{decision_id}/expiry_or_review_trigger",
                f"{PHASE33_EXCEPTION_REGISTER}#{decision_id}/affected_gates",
            ])
        valid_residual_matches = []
        for decision in residual_matches:
            decision_id = str(decision.get("decision_id") or "")
            if not decision_id or "follow_up_refs" not in decision or not decision.get(
                    "affected_gates"):
                reasons.add("route-scope-incomplete")
                continue
            valid_residual_matches.append(decision)
            criteria.extend([
                f"{PHASE33_RESIDUAL_REGISTER}#{decision_id}/follow_up_refs",
                f"{PHASE33_RESIDUAL_REGISTER}#{decision_id}/affected_gates",
            ])
        scope.append({
            "scope_id":
            f"repair-{ledger_row_id}",
            "blocker_refs":
            blocker_refs,
            "exception_refs": [
                f"{PHASE33_EXCEPTION_REGISTER}#{row['decision_id']}"
                for row in valid_exception_matches
            ],
            "residual_risk_refs": [
                f"{PHASE33_RESIDUAL_REGISTER}#{row['decision_id']}"
                for row in valid_residual_matches
            ],
            "requirement_ids":
            sorted(
                set(str(value)
                    for value in ledger.get("requirement_ids", []))),
            "affected_gates":
            sorted(
                set(str(value) for value in ledger.get("affected_gates", []))),
            "owner_ref":
            owner_ref,
            "required_action_ref":
            required_action_ref,
            "exit_review_criterion_refs":
            criteria,
        })
    return scope, sorted(reasons)


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def project_demotion(
    handoff: Any,
    normalized_records: list[dict[str, Any]],
    dry_run: dict[str, Any],
) -> dict[str, Any]:
    source_refs: list[str] = []
    decision_state = "missing"
    validation_state = "malformed"
    if isinstance(handoff, dict):
        source_refs = sorted({
            ref
            for ref in handoff.get("source_row_refs", [])
            if isinstance(ref, str) and ref.startswith(ALLOWED_REF_PREFIXES)
        })
        required_shape = (
            isinstance(handoff.get("phase"), str)
            and isinstance(handoff.get("phase_lifecycle_id"), str)
            and isinstance(handoff.get("demotion_input_supplied"), bool))
        if not required_shape:
            validation_state = "malformed"
        elif handoff.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
            validation_state = "lifecycle-mismatched"
        elif handoff.get("demotion_input_supplied") is False:
            validation_state = "missing"
        elif handoff.get("demotion_input_supplied") is True and isinstance(
                handoff.get("decision_id"), str):
            matches = [
                row for row in normalized_records
                if row.get("decision_id") == handoff["decision_id"]
            ]
            if len(matches) != 1:
                validation_state = "invalid"
            else:
                decision = matches[0]
                maybe_value = decision.get("decision_value")
                if maybe_value in {"approve", "reject"}:
                    decision_state = str(maybe_value)
                if decision.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
                    validation_state = "lifecycle-mismatched"
                elif decision.get(
                        "decision_type"
                ) != "reference_demotion" or maybe_value not in {
                        "approve", "reject"
                }:
                    validation_state = "invalid"
                elif decision.get("source_row_refs") != handoff.get(
                        "source_row_refs"):
                    validation_state = "invalid"
                else:
                    maybe_timestamp = parse_timestamp(
                        decision.get("decision_timestamp"))
                    validation_state = "malformed" if maybe_timestamp is None else "valid"
                    if maybe_timestamp is not None and maybe_timestamp < STALE_BEFORE:
                        validation_state = "stale"
    gate_state = dry_run.get("gate_state")
    gate_reasons = dry_run.get("reason_codes")
    if gate_state not in {"blocked", "open"
                          } or not isinstance(gate_reasons, list):
        gate_state = "blocked"
        gate_reasons = ["source-artifact-malformed"]
    expected_dry_validation = {
        "missing": "missing",
        "valid": "valid"
    }.get(validation_state, "invalid")
    expected_dry_decision = decision_state
    if dry_run.get("approval_validation_state"
                   ) != expected_dry_validation or dry_run.get(
                       "approval_decision_state") != expected_dry_decision:
        gate_state = "blocked"
        gate_reasons.append("source-artifact-malformed")
    if validation_state != "valid" or decision_state != "approve":
        gate_state = "blocked"
        if not gate_reasons:
            gate_reasons.append("approval-missing" if validation_state ==
                                "missing" else "approval-invalid")
    if dry_run.get("readiness_state") != "unblocked":
        gate_state = "blocked"
        gate_reasons.append("readiness-input-invalid")
    if gate_reasons:
        gate_state = "blocked"
    return {
        "demotion_decision_validation_state":
        validation_state,
        "demotion_decision_state":
        decision_state,
        "demotion_decision_source_refs":
        source_refs,
        "demotion_gate_state":
        gate_state,
        "demotion_gate_reason_codes":
        sorted(
            set(
                str(value) for value in gate_reasons
                if isinstance(value, str) and value)),
    }
