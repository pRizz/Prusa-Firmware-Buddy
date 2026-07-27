from __future__ import annotations

from phase28_readiness_contract import *


def input_path_under(path_value: str, expected_root: Path,
                     row_name: str) -> Path:
    return require_repo_relative_under(path_value, expected_root, row_name)


def load_json_input(root: Path, path: Path, row_name: str) -> dict[str, Any]:
    raw_text = read_text(root, path)
    reject_forbidden_text(path, raw_text)
    data = load_json(root, path)
    reject_forbidden_json_fields(data, path.as_posix())
    return data


def load_phase26_rows(root: Path,
                      path_value: str) -> tuple[Path, list[dict[str, Any]]]:
    path = input_path_under(path_value, Path("build/ci-evidence/phase26"),
                            "--phase26-upstream-rows")
    if not (root / path).exists():
        raise VerificationError(
            f"missing Phase 26 upstream rows: {path.as_posix()}\nRun: {PHASE26_QUICK_COMMAND}"
        )
    data = load_json_input(root, path, "--phase26-upstream-rows")
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise VerificationError("--phase26-upstream-rows rows must be a list")
    requirements = phase18_upstream_requirements(root)
    canonical_criteria = list(requirements.keys())
    normalized_rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"phase26 rows[{index}] must be an object")
        row_name = f"phase26 {row.get('criterion_id', index)}"
        criterion_id = require_string(row, "criterion_id", row_name)
        if criterion_id not in canonical_criteria:
            raise VerificationError(
                f"{row_name} criterion_id is not a canonical Phase 18 criterion"
            )
        if criterion_id in seen:
            raise VerificationError(
                f"duplicate Phase 26 criterion row: {criterion_id}")
        seen.add(criterion_id)
        requirement = requirements.get(criterion_id)
        if requirement is None:
            raise VerificationError(
                f"{row_name} does not resolve in Phase 18 upstream requirements"
            )
        if row.get("source_lifecycle_id") != requirement.get(
                "source_lifecycle_id"):
            raise VerificationError(
                f"{row_name} source_lifecycle_id must match Phase 18 upstream requirement"
            )
        if row.get("source_lifecycle_status") != "current":
            raise VerificationError(
                f"{row_name} source_lifecycle_status must be current")
        if row.get("source_ref_status") != "passed":
            raise VerificationError(
                f"{row_name} source_ref_status must be passed")
        normalized_rows.append(row)
    missing = sorted(set(canonical_criteria) - seen)
    if missing:
        raise VerificationError("Phase 26 upstream rows missing criteria: " +
                                ", ".join(missing))
    return path, normalized_rows


def load_phase27_supporting(root: Path, handoff_path: Path,
                            filename: str) -> dict[str, Any]:
    path = handoff_path.parent / filename
    if not (root / path).exists():
        raise VerificationError(
            f"missing Phase 27 supporting artifact: {path.as_posix()}\nRun: {PHASE27_QUICK_COMMAND}"
        )
    return load_json_input(root, path, f"Phase 27 {filename}")


def load_phase27_bundle(
        root: Path,
        path_value: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    handoff_path = input_path_under(path_value,
                                    Path("build/ci-evidence/phase27"),
                                    "--phase27-handoff")
    if not (root / handoff_path).exists():
        raise VerificationError(
            f"missing Phase 27 handoff: {handoff_path.as_posix()}\nRun: {PHASE27_QUICK_COMMAND}"
        )
    handoff = load_json_input(root, handoff_path, "--phase27-handoff")
    if handoff.get("phase") != PHASE27:
        raise VerificationError(f"--phase27-handoff phase must be {PHASE27}")
    if handoff.get("phase_lifecycle_id") != PHASE27_LIFECYCLE_ID:
        raise VerificationError(
            f"--phase27-handoff phase_lifecycle_id must be {PHASE27_LIFECYCLE_ID}"
        )
    if handoff.get("demotion_authorization") != "blocked":
        raise VerificationError(
            "--phase27-handoff demotion_authorization must remain blocked")
    if handoff.get("phase27_may_authorize_demotion") is not False:
        raise VerificationError(
            "--phase27-handoff phase27_may_authorize_demotion must be false")
    if handoff.get("phase28_required_decision"
                   ) != "explicit-maintainer-reference-demotion-decision":
        raise VerificationError(
            "--phase27-handoff phase28_required_decision is invalid")
    bundle = {
        "final_readiness":
        load_phase27_supporting(root, handoff_path,
                                "final-readiness-decision-summary.json"),
        "residual_risk":
        load_phase27_supporting(root, handoff_path,
                                "residual-risk-register.json"),
        "exceptions":
        load_phase27_supporting(root, handoff_path,
                                "exception-decision-register.json"),
        "artifact_refs":
        load_phase27_supporting(root, handoff_path,
                                "artifact-reference-summary.json"),
        "decision_rows":
        load_phase27_supporting(root, handoff_path, "decision-row-table.json"),
    }
    return handoff_path, handoff, bundle


def rows_by_field(data: dict[str, Any], field: str,
                  source_name: str) -> dict[str, dict[str, Any]]:
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{source_name} rows must be a list")
    mapped: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(
                f"{source_name} rows[{index}] must be an object")
        row_id = row.get(field)
        if not isinstance(row_id, str) or not row_id:
            raise VerificationError(
                f"{source_name} rows[{index}] {field} must be a non-empty string"
            )
        if row_id in mapped:
            raise VerificationError(
                f"{source_name} duplicate {field}: {row_id}")
        mapped[row_id] = row
    return mapped


def detect_hard_failure_reasons(phase26_row: dict[str, Any],
                                phase27_row: dict[str, Any]) -> list[str]:
    reasons = set()
    status_values = {
        str(phase26_row.get("status", "")),
        str(phase27_row.get("status", ""))
    }
    if phase26_row.get("redaction_status") != "passed" or phase27_row.get(
            "redaction_summary") == "redaction_status=failed":
        reasons.add("redaction-failed")
    if "rejected-redaction" in status_values:
        reasons.add("redaction-failed")
    if "rejected-overclaim" in status_values:
        reasons.add("overclaim-failed")
    overclaim_status = phase26_row.get("overclaim_status")
    if isinstance(overclaim_status,
                  str) and overclaim_status not in {"passed", "not-required"}:
        reasons.add("overclaim-failed")
    if phase26_row.get("source_lifecycle_status") != "current":
        reasons.add("lifecycle-mismatch")
    if phase26_row.get("source_ref_status") != "passed":
        reasons.add("source-ref-failed")
    unsafe_ref_status = phase26_row.get("unsafe_ref_status")
    if isinstance(unsafe_ref_status,
                  str) and unsafe_ref_status not in {"passed", "not-required"}:
        reasons.add("unsafe-ref")
    for reason in phase27_row.get("hard_failure_reasons", []):
        if isinstance(reason, str) and reason:
            reasons.add(reason)
    failure_text = f"{phase26_row.get('failure_reason', '')} {phase27_row.get('rationale', '')}".lower(
    )
    for reason in HARD_BLOCKER_REASONS:
        if reason in failure_text or reason.replace("-", " ") in failure_text:
            reasons.add(reason)
    return [reason for reason in HARD_BLOCKER_REASONS if reason in reasons]


def validate_exception_metadata(exception: Any,
                                row_name: str) -> dict[str, Any]:
    if not isinstance(exception, dict):
        raise VerificationError(f"{row_name} exception must be an object")
    for field in EXCEPTION_REQUIRED_FIELDS:
        if field not in exception:
            raise VerificationError(
                f"{row_name} exception missing required field: {field}")
        if field == "evidence_refs":
            refs = exception[field]
            if not isinstance(refs, list) or not all(
                    isinstance(ref, str) and ref for ref in refs) or not refs:
                raise VerificationError(
                    f"{row_name} exception evidence_refs must not be empty")
        elif not isinstance(exception[field], str) or not exception[field]:
            raise VerificationError(
                f"{row_name} exception {field} must be a non-empty string")
    return exception


def exception_covers_row(
        phase26_row: dict[str, Any], phase27_row: dict[str, Any],
        hard_failure_reasons: list[str]) -> tuple[bool, list[dict[str, Any]]]:
    if hard_failure_reasons:
        return False, []
    status = str(phase26_row.get("status", ""))
    phase27_status = str(phase27_row.get("status", ""))
    exception_state = str(phase27_row.get("exception_state", ""))
    exception = phase27_row.get("exception")
    if status not in EXCEPTION_COVERABLE_STATUSES and phase27_status not in EXCEPTION_STATUSES:
        return False, []
    if phase27_status not in EXCEPTION_STATUSES and exception_state not in {
            "approved-exception", "exception-approved"
    }:
        return False, []
    exception_row = validate_exception_metadata(
        exception, str(phase27_row.get("criterion_id", "criterion")))
    return True, [exception_row]


def matching_rows(rows: list[dict[str, Any]],
                  row_id: str) -> list[dict[str, Any]]:
    return [
        row for row in rows
        if row.get("row_id") == row_id or row.get("criterion_id") == row_id
    ]


def normalize_readiness_criteria(
    phase26_rows: list[dict[str, Any]],
    phase27_bundle: dict[str, Any],
    canonical_criteria: list[str],
) -> list[dict[str, Any]]:
    phase26_by_id = {str(row["criterion_id"]): row for row in phase26_rows}
    phase27_by_id = rows_by_field(phase27_bundle["final_readiness"],
                                  "criterion_id",
                                  "Phase 27 final-readiness-decision-summary")
    residual_rows = phase27_bundle["residual_risk"].get("rows", [])
    exception_rows = phase27_bundle["exceptions"].get("rows", [])
    if not isinstance(residual_rows, list) or not isinstance(
            exception_rows, list):
        raise VerificationError(
            "Phase 27 residual risk and exception artifacts must contain rows lists"
        )
    normalized: list[dict[str, Any]] = []
    for criterion_id in canonical_criteria:
        phase26_row = phase26_by_id[criterion_id]
        phase27_row = phase27_by_id.get(criterion_id)
        if phase27_row is None:
            raise VerificationError(
                f"Phase 27 final readiness summary missing criterion: {criterion_id}"
            )
        hard_failure_reasons = detect_hard_failure_reasons(
            phase26_row, phase27_row)
        covered_by_exception, inline_exceptions = exception_covers_row(
            phase26_row, phase27_row, hard_failure_reasons)
        phase26_status = str(phase26_row.get("status", "blocked"))
        phase27_status = str(phase27_row.get("status", "blocked"))
        if criterion_id == DEMOTION_CRITERION:
            readiness_effect = "blocked-pending-explicit-demotion-decision"
        elif hard_failure_reasons:
            readiness_effect = "blocked-hard-failure"
        elif covered_by_exception:
            readiness_effect = "exception-covered"
        elif phase26_status in PASS_STATUSES and phase27_status in PASS_STATUSES:
            readiness_effect = "passed"
        else:
            readiness_effect = "blocked"
        residual_refs = [
            f"build/ci-evidence/phase27/residual-risk-register.json#{row.get('row_id')}"
            for row in matching_rows(residual_rows, criterion_id)
            if isinstance(row, dict)
        ]
        exception_refs = [
            f"build/ci-evidence/phase27/exception-decision-register.json#{row.get('row_id', row.get('criterion_id', criterion_id))}"
            for row in matching_rows(exception_rows, criterion_id)
            if isinstance(row, dict)
        ]
        phase26_evidence_refs = [
            str(ref) for ref in phase26_row.get("evidence_refs", [])
            if isinstance(ref, str)
        ]
        phase27_evidence_refs = [
            str(ref) for ref in phase27_row.get("evidence_refs", [])
            if isinstance(ref, str)
        ]
        normalized.append({
            "criterion_id":
            criterion_id,
            "requirement_ids":
            list(phase26_row.get("requirement_ids", [])),
            "evidence_family":
            phase26_row.get("evidence_family", ""),
            "phase26_status":
            phase26_status,
            "phase27_status":
            phase27_status,
            "readiness_effect":
            readiness_effect,
            "hard_failure_reasons":
            hard_failure_reasons,
            "exception_state":
            "covered" if covered_by_exception else str(
                phase27_row.get("exception_state", "none")),
            "exception_refs":
            exception_refs,
            "exception_metadata":
            inline_exceptions,
            "residual_risk":
            str(
                phase27_row.get("residual_risk",
                                "Pending final readiness review.")),
            "residual_risk_refs":
            residual_refs,
            "source_refs":
            phase26_evidence_refs,
            "evidence_refs":
            sorted(set([*phase26_evidence_refs, *phase27_evidence_refs])),
            "artifact_refs":
            sorted(
                set([
                    *[
                        str(ref)
                        for ref in phase26_row.get("artifact_refs", [])
                        if isinstance(ref, str)
                    ],
                    *[
                        str(ref)
                        for ref in phase27_row.get("artifact_refs", [])
                        if isinstance(ref, str)
                    ],
                ])),
            "rationale":
            str(
                phase27_row.get("rationale",
                                phase26_row.get("failure_reason", ""))),
            "demotion_gate_effect":
            "requires-explicit-phase28-decision"
            if criterion_id == DEMOTION_CRITERION else "readiness-input",
        })
    return normalized


def final_readiness_status(criteria: list[dict[str, Any]]) -> str:
    for row in criteria:
        if row["criterion_id"] == DEMOTION_CRITERION:
            continue
        if row["readiness_effect"] not in {"passed", "exception-covered"}:
            return "blocked"
    return "unblocked"


def load_demotion_decision_input(
    root: Path,
    maybe_path: str | None,
    maybe_final_readiness_status: str | None = None,
) -> dict[str, Any] | None:
    if not maybe_path:
        return None
    path = require_repo_relative(maybe_path, "--demotion-decision-input")
    raw_text = read_text(root, path)
    reject_forbidden_text(path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(
            "--demotion-decision-input must contain a top-level object")
    reject_forbidden_json_fields(data, path.as_posix())
    for field in DEMOTION_DECISION_REQUIRED_FIELDS:
        if field not in data:
            raise VerificationError(
                f"--demotion-decision-input missing required field: {field}")
    if data["phase"] != PHASE:
        raise VerificationError(
            f"--demotion-decision-input phase must be {PHASE}")
    if data["phase_lifecycle_id"] != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"--demotion-decision-input phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
        )
    authorization = data["demotion_authorization"]
    if authorization not in {"blocked", "approved"}:
        raise VerificationError(
            "--demotion-decision-input demotion_authorization must be blocked or approved"
        )
    for field in ["approver", "approver_role", "rationale", "scope"]:
        if not isinstance(data[field], str) or not data[field]:
            raise VerificationError(
                f"--demotion-decision-input {field} must be a non-empty string"
            )
    require_iso_utc(
        require_string(data, "decision_timestamp",
                       "--demotion-decision-input"),
        "--demotion-decision-input")
    evidence_refs = data["evidence_refs"]
    if not isinstance(evidence_refs, list) or not all(
            isinstance(ref, str) and ref for ref in evidence_refs):
        raise VerificationError(
            "--demotion-decision-input evidence_refs must be a list of non-empty strings"
        )
    if authorization == "approved":
        if not evidence_refs:
            raise VerificationError(
                "--demotion-decision-input approved authorization requires evidence_refs"
            )
        if maybe_final_readiness_status != "unblocked":
            raise VerificationError(
                "approved reference demotion requires final_readiness_status unblocked"
            )
    return data


def demotion_authorization_record(
    decision_input: dict[str, Any] | None,
    readiness_status: str,
) -> dict[str, Any]:
    if decision_input is None:
        return {
            "reference_demotion_authorization": "blocked",
            "real_maintainer_demotion_approval_supplied": False,
            "authorization_source": "no-phase28-demotion-decision-input",
            "rationale":
            "Reference demotion requires an explicit Phase 28 maintainer decision.",
            "evidence_refs": [],
        }
    authorization = str(decision_input["demotion_authorization"])
    if authorization == "approved" and readiness_status != "unblocked":
        raise VerificationError(
            "approved reference demotion requires final_readiness_status unblocked"
        )
    return {
        "reference_demotion_authorization": authorization,
        "real_maintainer_demotion_approval_supplied":
        authorization == "approved",
        "authorization_source": "phase28-demotion-decision-input",
        "approver": decision_input["approver"],
        "approver_role": decision_input["approver_role"],
        "decision_timestamp": decision_input["decision_timestamp"],
        "scope": decision_input["scope"],
        "rationale": decision_input["rationale"],
        "evidence_refs": decision_input["evidence_refs"],
    }


def apply_demotion_authorization_to_criteria(
        criteria: list[dict[str, Any]], demotion_record: dict[str,
                                                              Any]) -> None:
    authorization = demotion_record["reference_demotion_authorization"]
    for row in criteria:
        if row["criterion_id"] != DEMOTION_CRITERION:
            continue
        if authorization == "approved":
            row["readiness_effect"] = "reference-demotion-authorized"
            row["demotion_gate_effect"] = "explicit-phase28-decision-approved"
            row["rationale"] = demotion_record["rationale"]
            row["evidence_refs"] = sorted(
                set([*row["evidence_refs"],
                     *demotion_record["evidence_refs"]]))
        else:
            row["readiness_effect"] = "blocked-pending-explicit-demotion-decision"
            row["demotion_gate_effect"] = "requires-explicit-phase28-decision"


def build_blocker_rows(
        criteria: list[dict[str, Any]], readiness_status: str,
        demotion_record: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = []
    for row in criteria:
        if row["criterion_id"] == DEMOTION_CRITERION:
            continue
        if row["readiness_effect"] in {"passed", "exception-covered"}:
            continue
        blockers.append({
            "criterion_id": row["criterion_id"],
            "readiness_effect": row["readiness_effect"],
            "phase26_status": row["phase26_status"],
            "phase27_status": row["phase27_status"],
            "hard_failure_reasons": row["hard_failure_reasons"],
            "rationale": row["rationale"],
        })
    if demotion_record["reference_demotion_authorization"] != "approved":
        blockers.append({
            "criterion_id": DEMOTION_CRITERION,
            "readiness_effect": "reference-demotion-authorization-blocked",
            "phase26_status": "not-applicable",
            "phase27_status": "blocked",
            "hard_failure_reasons": [],
            "rationale": demotion_record["rationale"],
        })
    if readiness_status == "blocked" and not blockers:
        raise VerificationError(
            "blocked final readiness must include at least one blocker")
    return blockers
