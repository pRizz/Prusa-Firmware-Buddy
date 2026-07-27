from __future__ import annotations

from phase32_triage_contract import *


def classify_reason(reason: str) -> str | None:
    for problem_kind, pattern in REASON_PROBLEM_PATTERNS:
        if pattern.search(reason):
            return problem_kind
    return None


def classify_problem_kind(signal: dict[str, Any]) -> str:
    maybe_adapter_problem = signal.get("adapter_problem_kind")
    if maybe_adapter_problem in {"malformed", "unknown_unclassified"}:
        return str(maybe_adapter_problem)
    if signal.get("redaction_status") in {
            "secret-tainted", "secret_tainted"
    } or signal.get("status") in {"secret-tainted", "secret_tainted"}:
        return "secret_tainted"
    if signal.get("redaction_status") in {
            "failed", "rejected", "redaction-failed", "rejected-redaction"
    }:
        return "redaction_failed"
    if signal.get("source_ref_status") in {
            "unsafe-ref", "unsafe_ref"
    } or signal.get("status") in {"unsafe-ref", "unsafe_ref"}:
        return "unsafe_ref"
    if signal.get("source_ref_status") in {
            "failed", "rejected", "source-ref-failed"
    }:
        return "source_ref_failed"
    if signal.get("source_lifecycle_status") in {
            "stale", "mismatch", "lifecycle-mismatch"
    }:
        return "lifecycle_mismatch"

    reason = str(signal.get("failure_reason") or signal.get("reason") or "")
    maybe_reason_problem = classify_reason(reason)
    if maybe_reason_problem is not None:
        return maybe_reason_problem

    finality_status = str(signal.get("finality_status") or "")
    if finality_status in {"rejected-final", "quarantined-non-final"}:
        return "unknown_unclassified"

    if signal.get("exception_status") in {
            "exception-requested", "requested"
    } or signal.get("status") == "exception-requested":
        return "exception_requested"
    if signal.get("status") in {"stale", "stale-lifecycle"}:
        return "stale"
    if signal.get("status") in {"failed", "blocked"}:
        return "failed"
    if signal.get("status") in {
            "missing", "pending", "pending-input", "pending-live-input"
    }:
        return "missing"
    if signal.get("status") in {"malformed", "invalid"}:
        return "malformed"
    return "unknown_unclassified"


def blocker_policy_for(problem_kind: str,
                       source_stream: str = "unknown") -> dict[str, str]:
    contract = load_contract()
    policy_map = require_dict(contract["policy_map"], "policy_map")
    owner_defaults = require_dict(contract["owner_defaults"], "owner_defaults")
    if problem_kind not in policy_map:
        problem_kind = "unknown_unclassified"
    policy = require_dict(policy_map[problem_kind],
                          f"policy_map.{problem_kind}")
    owner_ref = str(
        owner_defaults.get(source_stream) or owner_defaults["unknown"])
    return {
        "blocker_kind":
        require_string(policy.get("blocker_kind"),
                       f"policy_map.{problem_kind}.blocker_kind"),
        "severity":
        require_string(policy.get("severity"),
                       f"policy_map.{problem_kind}.severity"),
        "decision_impact":
        require_string(policy.get("decision_impact"),
                       f"policy_map.{problem_kind}.decision_impact"),
        "proof_eligibility":
        require_string(policy.get("proof_eligibility"),
                       f"policy_map.{problem_kind}.proof_eligibility"),
        "owner_ref":
        owner_ref,
        "required_next_action":
        require_string(policy.get("required_next_action"),
                       f"policy_map.{problem_kind}.required_next_action"),
    }


def classify_signal(signal: dict[str, Any]) -> dict[str, str]:
    source_stream = str(
        signal.get("source_stream") or signal.get("stream") or "unknown")
    problem_kind = classify_problem_kind(signal)
    return {
        "row_problem_kind": problem_kind,
        **blocker_policy_for(problem_kind, source_stream),
    }


def gate_for(source_stream: str, signal: dict[str, Any]) -> str:
    for field in ("criterion_id", "affected_gate", "row_id"):
        value = signal.get(field)
        if isinstance(value, str) and value:
            return value
    return STREAM_GATE_DEFAULTS.get(source_stream,
                                    STREAM_GATE_DEFAULTS["unknown"])


def evidence_refs_from(signal: dict[str, Any], source_ref: str) -> list[str]:
    refs: list[str] = []
    for field in ("evidence_refs", "artifact_refs", "validator_output_refs",
                  "residual_risk_refs", "exception_refs"):
        refs.extend(string_list(signal.get(field)))
    for field in ("artifact_ref", "manifest_ref"):
        value = signal.get(field)
        if isinstance(value, str) and value:
            refs.append(value)
    if source_ref:
        refs.append(source_ref)
    unique_refs: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        unique_refs.append(ref)
    return unique_refs or [source_ref or "external://phase32/no-evidence-ref"]


def source_requirement_ids(signal: dict[str, Any]) -> list[str]:
    maybe_requirement_ids = string_list(signal.get("requirement_ids"))
    if maybe_requirement_ids:
        return maybe_requirement_ids
    maybe_source_requirement_ids = string_list(
        signal.get("source_requirement_ids"))
    if maybe_source_requirement_ids:
        return maybe_source_requirement_ids
    return sorted(REQUIRED_REQUIREMENT_IDS)


def build_blocker_row(
    *,
    source_domain: str,
    producer_phase: str,
    producer_artifact_kind: str,
    source_row_kind: str,
    source_subject_id: str,
    decision_axis: str,
    decision_subject_id: str,
    source_stream: str,
    source_ref: str,
    signal: dict[str, Any],
    policy_override: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        source_identity = canonical_source_identity(
            source_domain=source_domain,
            producer_phase=producer_phase,
            producer_artifact_kind=producer_artifact_kind,
            source_row_kind=source_row_kind,
            source_subject_id=source_subject_id,
        )
        resolution_identity = decision_identity(
            decision_axis=decision_axis,
            decision_subject_id=decision_subject_id,
        )
    except NormalizationError as error:
        raise VerificationError(str(error)) from error
    classification = classify_signal({
        "source_stream": source_stream,
        **signal
    })
    if policy_override:
        classification.update(policy_override)
    owner = signal.get("owner")
    if isinstance(owner, str) and owner:
        classification["owner_ref"] = owner
    if not classification.get("owner_ref") or not classification.get(
            "required_next_action"):
        raise VerificationError(
            f"blocker row for {source_ref} did not receive explicit owner/action"
        )
    return {
        "row_id": canonical_row_id(source_identity),
        **source_identity,
        **resolution_identity,
        "source_stream": source_stream,
        "source_ref": source_ref,
        "requirement_ids": source_requirement_ids(signal),
        "affected_gate": gate_for(source_stream, signal),
        "row_problem_kind": classification["row_problem_kind"],
        "blocker_kind": classification["blocker_kind"],
        "severity": classification["severity"],
        "owner_ref": classification["owner_ref"],
        "required_next_action": classification["required_next_action"],
        "decision_impact": classification["decision_impact"],
        "proof_eligibility": classification["proof_eligibility"],
        "evidence_refs": evidence_refs_from(signal, source_ref),
    }


def is_non_blocking_source_row(signal: dict[str, Any]) -> bool:
    return (signal.get("status") == "passed"
            and signal.get("redaction_status", "passed") == "passed"
            and signal.get("source_ref_status", "passed") == "passed"
            and signal.get("source_lifecycle_status",
                           "current") in CLEAN_SOURCE_LIFECYCLE_STATUSES
            and signal.get("exception_status", "none") in {"none", "", None})
