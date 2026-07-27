from __future__ import annotations

from phase27_decision_contract import *


def source_contract_refs(contract: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for source_contract in require_list(contract, "source_contracts",
                                        "Phase 27 contract"):
        if not isinstance(source_contract, dict):
            raise VerificationError(
                "Phase 27 source_contracts entries must be objects")
        refs.append({
            "id":
            require_string(source_contract, "id", "Phase 27 source contract"),
            "path":
            require_string(source_contract, "path",
                           "Phase 27 source contract"),
        })
    return refs


def phase26_required_row_fields(phase26_contract: dict[str, Any]) -> list[str]:
    upstream_policy = require_dict(phase26_contract, "upstream_policy",
                                   "Phase 26 contract")
    return require_string_list(upstream_policy, "row_required_fields",
                               "Phase 26 upstream policy")


def load_phase26_upstream_rows(
        root: Path, path: Path, phase18_contract: dict[str, Any],
        phase26_contract: dict[str, Any]) -> list[dict[str, Any]]:
    if not (root / path).exists():
        raise VerificationError(
            f"missing Phase 26 upstream result row table: {path.as_posix()}\n"
            f"Generate it first with: {PHASE26_GENERATION_COMMAND}")
    text = read_text(root, path)
    reject_forbidden_text(path, text)
    data = json.loads(text)
    reject_forbidden_field_names(data, path.as_posix())
    if not isinstance(data, dict):
        raise VerificationError(
            f"{path.as_posix()} must contain a top-level object")
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{path.as_posix()} must contain a rows list")
    required_fields = phase26_required_row_fields(phase26_contract)
    expected_ids = phase18_upstream_criterion_ids(phase18_contract)
    requirement_by_id = {
        require_string(requirement, "criterion_id", "Phase 18 upstream requirement"):
        requirement
        for requirement in phase18_upstream_requirements(phase18_contract)
    }
    parsed_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"Phase 26 upstream row {index}"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        missing = [field for field in required_fields if field not in row]
        if missing:
            errors.append(
                f"{row_name} missing required fields: {', '.join(missing)}")
        try:
            criterion_id = require_string(row, "criterion_id", row_name)
            require_string(row, "status", row_name)
            require_string(row, "redaction_status", row_name)
            require_string(row, "source_ref_status", row_name)
            require_string(row, "source_lifecycle_status", row_name)
            requirement = requirement_by_id.get(criterion_id)
            if requirement is None:
                errors.append(
                    f"{row_name} uses unknown criterion_id: {criterion_id}")
            else:
                if row.get("evidence_family") != requirement.get(
                        "evidence_family"):
                    errors.append(
                        f"{row_name} evidence_family must match Phase 18")
                if row.get("owning_phase") != requirement.get("source_phase"):
                    errors.append(
                        f"{row_name} owning_phase must match Phase 18")
                if row.get("source_lifecycle_id") != requirement.get(
                        "source_lifecycle_id"):
                    errors.append(
                        f"{row_name} source_lifecycle_id must match Phase 18")
        except VerificationError as error:
            errors.append(str(error))
        parsed_rows.append(row)
    ids = [str(row.get("criterion_id")) for row in parsed_rows]
    if ids != expected_ids:
        errors.append(
            "Phase 26 upstream rows must match the nine Phase 18 criteria in canonical order"
        )
    if len(ids) != len(set(ids)):
        errors.append("Phase 26 upstream rows must not duplicate criterion_id")
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def maintainer_input_template(phase18_contract: dict[str, Any],
                              contract: dict[str, Any]) -> dict[str, Any]:
    retained_rows = []
    for packet in phase18_retained_packets(phase18_contract):
        retained_rows.append({
            "packet_id":
            require_string(packet, "id", "retained packet"),
            "decision":
            "",
            "approver":
            "",
            "approver_role":
            packet.get("approver_role", ""),
            "decision_timestamp":
            "",
            "rationale":
            "",
            "evidence_refs":
            list(packet.get("required_evidence_refs", [])),
            "residual_risk":
            "",
            "redaction_summary":
            "",
            "hard_failure_reasons": [],
            "exception": {
                "scope": "",
                "rationale": "",
                "approver": "",
                "approver_role": "",
                "affected_printer_or_release_surface": "",
                "mitigation_or_follow_up": "",
                "expiry_or_review_trigger": "",
                "evidence_refs": [],
                "residual_risk": "",
                "owner": "",
            },
        })
    final_rows = []
    for requirement in phase18_upstream_requirements(phase18_contract):
        criterion_id = require_string(requirement, "criterion_id",
                                      "upstream requirement")
        final_rows.append({
            "decision_id": f"phase27-final-readiness-{criterion_id}",
            "criterion_id": criterion_id,
            "decision": "",
            "status": "pending",
            "approver": "",
            "approver_role": "",
            "decision_timestamp": "",
            "rationale": "",
            "evidence_refs": [],
            "residual_risk": "",
            "exception": {},
            "redaction_summary": "",
            "hard_failure_reasons": [],
        })
    handoff_policy = require_dict(contract, "phase28_handoff_policy",
                                  "Phase 27 contract")
    return {
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "retained_code_decisions": retained_rows,
        "final_readiness_decisions": final_rows,
        "reference_demotion_decision": {
            "demotion_authorization":
            handoff_policy["demotion_authorization"],
            "phase27_may_authorize_demotion":
            handoff_policy["phase27_may_authorize_demotion"],
            "phase28_required_decision":
            handoff_policy["phase28_required_decision"],
        },
    }


def load_maintainer_input(root: Path,
                          maybe_path: str | None) -> dict[str, Any] | None:
    if maybe_path is None:
        return None
    path = repo_relative_path(maybe_path, "--maintainer-input")
    text = read_text(root, path)
    reject_forbidden_text(path, text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{path.as_posix()} is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, path.as_posix())
    if not isinstance(data, dict):
        raise VerificationError(
            "--maintainer-input must contain a top-level object")
    expected_metadata = {
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
    }
    errors = [
        f"--maintainer-input {field} must be {expected_value!r}"
        for field, expected_value in expected_metadata.items()
        if data.get(field) != expected_value
    ]
    demotion = data.get("reference_demotion_decision")
    if not isinstance(demotion, dict):
        errors.append(
            "--maintainer-input reference_demotion_decision must be an object")
    else:
        if demotion.get("demotion_authorization") != "blocked":
            errors.append(
                "reference_demotion_decision demotion_authorization must stay blocked"
            )
        if demotion.get("phase27_may_authorize_demotion") is not False:
            errors.append(
                "reference_demotion_decision phase27_may_authorize_demotion must be false"
            )
    if errors:
        raise VerificationError("\n".join(errors))
    return data


def detect_hard_failure_reasons(row: dict[str,
                                          Any], allowed_reasons: list[str],
                                row_name: str) -> list[str]:
    reasons: list[str] = []
    explicit_reasons = row.get("hard_failure_reasons")
    if explicit_reasons is not None:
        if not isinstance(explicit_reasons, list) or not all(
                isinstance(reason, str) and reason
                for reason in explicit_reasons):
            raise VerificationError(
                f"{row_name} hard_failure_reasons must contain non-empty strings"
            )
        for reason in explicit_reasons:
            if reason not in allowed_reasons:
                raise VerificationError(
                    f"{row_name} hard_failure_reasons contains unknown reason: {reason}"
                )
            reasons.append(reason)

    def add(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    status = row.get("status")
    if status == "rejected-redaction":
        add("redaction-failed")
    if status == "rejected-overclaim":
        add("overclaim-failed")
    redaction_status = row.get("redaction_status")
    if isinstance(redaction_status,
                  str) and redaction_status not in {"passed", "not-required"}:
        add("redaction-failed")
    overclaim_status = row.get("overclaim_status")
    if isinstance(overclaim_status,
                  str) and overclaim_status not in {"passed", "not-required"}:
        add("overclaim-failed")
    source_ref_status = row.get("source_ref_status")
    if isinstance(source_ref_status,
                  str) and source_ref_status not in {"passed", "not-required"}:
        add("source-ref-failed")
    source_lifecycle_status = row.get("source_lifecycle_status")
    if isinstance(source_lifecycle_status,
                  str) and source_lifecycle_status not in {
                      "current", "not-required"
                  }:
        add("lifecycle-mismatch")
    unsafe_ref_status = row.get("unsafe_ref_status")
    if isinstance(unsafe_ref_status,
                  str) and unsafe_ref_status not in {"passed", "not-required"}:
        add("unsafe-ref")
    return reasons


def status_for_hard_failure(reasons: list[str]) -> str:
    if "redaction-failed" in reasons:
        return "rejected-redaction"
    if "overclaim-failed" in reasons:
        return "rejected-overclaim"
    return "blocked"


def subject_text(*values: Any) -> str:
    parts: list[str] = []
    for value in values:
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value is not None:
            parts.append(str(value))
    return " ".join(parts).casefold()


def validate_sensitive_role(contract: dict[str, Any], text: str,
                            approver_role: str, row_name: str) -> None:
    role_policy = require_dict(contract, "sensitive_role_policy",
                               "Phase 27 contract")
    for role, tokens in role_policy.items():
        if not isinstance(role, str) or not isinstance(tokens, list):
            raise VerificationError(
                "sensitive_role_policy must map role names to token lists")
        for token in tokens:
            if not isinstance(token, str):
                continue
            token_pattern = re.compile(
                rf"(?<![a-z0-9]){re.escape(token.casefold())}(?![a-z0-9])")
            if token_pattern.search(text) and approver_role != role:
                raise VerificationError(
                    f"{row_name} violates sensitive_role_policy: token {token!r} requires approver_role {role!r}"
                )


def require_iso_utc(value: str, row_name: str) -> None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        raise VerificationError(
            f"{row_name} decision_timestamp must be ISO UTC")


def normalize_exception(row: dict[str, Any], contract: dict[str, Any],
                        row_name: str) -> dict[str, Any]:
    exception = row.get("exception")
    if not isinstance(exception, dict):
        raise VerificationError(
            f"{row_name} exception must be an object for exception decisions")
    normalized = dict(exception)
    required_fields = list(
        require_dict(contract, "exception_policy",
                     "Phase 27 contract")["phase18_required_fields"])
    errors: list[str] = []
    for field in required_fields:
        try:
            if field == "evidence_refs":
                evidence_refs = require_string_list(normalized, field,
                                                    f"{row_name} exception")
                if not evidence_refs:
                    errors.append(
                        f"{row_name} exception evidence_refs must not be empty"
                    )
            else:
                require_string(normalized, field, f"{row_name} exception")
        except VerificationError as error:
            errors.append(str(error))
    if not isinstance(normalized.get("residual_risk"),
                      str) or not normalized["residual_risk"]:
        residual_risk = row.get("residual_risk")
        if isinstance(residual_risk, str) and residual_risk:
            normalized["residual_risk"] = residual_risk
        else:
            errors.append(
                f"{row_name} exception residual_risk must be a non-empty string"
            )
    if not isinstance(normalized.get("owner"), str) or not normalized["owner"]:
        approver = normalized.get("approver") or row.get("approver")
        if isinstance(approver, str) and approver:
            normalized["owner"] = approver
        else:
            errors.append(
                f"{row_name} exception owner must be a non-empty string or default from approver"
            )
    if errors:
        raise VerificationError("\n".join(errors))
    normalized["status"] = "approved-exception"
    return normalized


def validate_decision_common(row: dict[str, Any],
                             row_name: str,
                             require_status: bool = False,
                             require_evidence_refs: bool = False) -> None:
    fields = [
        "decision", "approver", "approver_role", "rationale", "residual_risk",
        "redaction_summary"
    ]
    if require_status:
        fields.append("status")
    errors: list[str] = []
    for field in fields:
        try:
            require_string(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))
    try:
        require_iso_utc(require_string(row, "decision_timestamp", row_name),
                        row_name)
    except VerificationError as error:
        errors.append(str(error))
    try:
        evidence_refs = require_string_list(row, "evidence_refs", row_name)
        if require_evidence_refs and not evidence_refs:
            errors.append(f"{row_name} evidence_refs must not be empty")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
