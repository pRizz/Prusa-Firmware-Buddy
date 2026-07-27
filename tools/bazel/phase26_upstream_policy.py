from __future__ import annotations

from phase26_release_policy import *


def require_string_list(row: dict[str, Any], field: str,
                        row_name: str) -> list[str]:
    values = require_list(row, field, row_name)
    if not all(isinstance(value, str) and value for value in values):
        raise VerificationError(
            f"{row_name} {field} must contain non-empty strings")
    return values


def require_exact_string_list(row: dict[str, Any], field: str,
                              expected: list[str], row_name: str) -> list[str]:
    values = require_string_list(row, field, row_name)
    if values != expected:
        raise VerificationError(f"{row_name} {field} must be {expected}")
    return values


def unique_strings(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def validate_upstream_input_path(root: Path, descriptor: dict[str, Any],
                                 maybe_path: str) -> Path:
    input_path = Path(maybe_path)
    row_name = str(descriptor["flag"])
    if input_path.is_absolute() or ".." in input_path.parts:
        raise VerificationError(
            f"{row_name} input path must be repo-relative under {descriptor['input_root']}: {maybe_path}"
        )
    validate_ref(input_path.as_posix(), [str(descriptor["input_root"])],
                 row_name, "input path")
    if not (root / input_path).exists():
        raise VerificationError(
            f"{row_name} input row file does not exist: {input_path.as_posix()}"
        )
    return input_path


def load_upstream_input_row(root: Path, descriptor: dict[str, Any],
                            maybe_path: str) -> tuple[Path, dict[str, Any]]:
    input_path = validate_upstream_input_path(root, descriptor, maybe_path)
    raw_text = (root / input_path).read_text(encoding="utf-8")
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{input_path.as_posix()} is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    if not isinstance(data, dict):
        raise VerificationError(
            f"{input_path.as_posix()} must contain a top-level object")
    return input_path, data


def validate_compact_upstream_row(
    descriptor: dict[str, Any],
    input_path: Path,
    row: dict[str, Any],
    status_vocabulary: set[str],
) -> tuple[str | None, list[str]]:
    row_name = f"{descriptor['flag']} row"
    errors: list[str] = []
    try:
        criterion_id = require_string(row, "criterion_id", row_name)
        if criterion_id != descriptor["source_criterion_id"]:
            errors.append(
                f"{row_name} criterion_id must be {descriptor['source_criterion_id']}"
            )
    except VerificationError as error:
        errors.append(str(error))
    try:
        require_exact_string_list(row, "requirement_ids",
                                  list(descriptor["producer_requirement_ids"]),
                                  row_name)
    except VerificationError as error:
        errors.append(str(error))
    try:
        phase = require_string(row, "phase", row_name)
        if phase != descriptor["source_phase"]:
            errors.append(
                f"{row_name} phase must be {descriptor['source_phase']}")
    except VerificationError as error:
        errors.append(str(error))
    try:
        require_string(row, "phase_lifecycle_id", row_name)
    except VerificationError as error:
        errors.append(str(error))
    status = None
    try:
        status = require_string(row, "status", row_name)
        if status not in status_vocabulary:
            errors.append(f"{row_name} status is invalid: {status}")
    except VerificationError as error:
        errors.append(str(error))
    for field in ["redaction_status", "source_ref_status"]:
        try:
            require_string(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if "exception_status" in row:
        try:
            require_string(row, "exception_status", row_name)
        except VerificationError as error:
            errors.append(str(error))
    allowed_roots = [
        str(descriptor["input_root"]),
        str(descriptor["external_root"])
    ]
    try:
        validate_ref_list(row,
                          "artifact_refs",
                          row_name,
                          allowed_roots,
                          require_nonempty=True)
    except VerificationError as error:
        errors.append(str(error))
    maybe_manifest_ref = row.get("manifest_ref")
    if maybe_manifest_ref is not None:
        if not isinstance(maybe_manifest_ref, str) or not maybe_manifest_ref:
            errors.append(
                f"{row_name} manifest_ref must be a non-empty string when present"
            )
        else:
            try:
                validate_ref(maybe_manifest_ref, allowed_roots, row_name,
                             "manifest_ref")
            except VerificationError as error:
                errors.append(str(error))
    try:
        validate_ref(input_path.as_posix(), [str(descriptor["input_root"])],
                     row_name, "input path")
    except VerificationError as error:
        errors.append(str(error))
    return status, errors


def consumed_row_maintainer_state(status: str) -> str:
    if status == "passed":
        return "not-required"
    if status in {
            "failed", "blocked", "rejected-redaction", "rejected-overclaim"
    }:
        return "blocked"
    return "pending"


def canonicalize_compact_upstream_row(
    descriptor: dict[str, Any],
    input_path: Path,
    row: dict[str, Any],
    requirement: dict[str, Any],
    generated_at: str,
    status_vocabulary: set[str],
) -> dict[str, Any]:
    status, errors = validate_compact_upstream_row(descriptor, input_path, row,
                                                   status_vocabulary)
    if errors:
        raise VerificationError("\n".join(errors))
    assert status is not None
    evidence_refs = [input_path.as_posix()]
    maybe_manifest_ref = row.get("manifest_ref")
    if isinstance(maybe_manifest_ref, str) and maybe_manifest_ref:
        evidence_refs.insert(0, maybe_manifest_ref)
    artifact_refs = [
        *require_string_list(row, "artifact_refs",
                             f"{descriptor['flag']} row"),
        input_path.as_posix(),
    ]
    return {
        "artifact_refs":
        unique_strings(artifact_refs),
        "criterion_id":
        descriptor["canonical_criterion_id"],
        "evidence_family":
        require_string(requirement, "evidence_family",
                       str(descriptor["canonical_criterion_id"])),
        "evidence_refs":
        unique_strings(evidence_refs),
        "exception_status":
        row.get("exception_status", "none"),
        "failure_reason":
        "none" if status == "passed" else
        f"Consumed upstream {descriptor['source_phase']} row status is {status}.",
        "generated_at_utc":
        generated_at,
        "maintainer_state":
        consumed_row_maintainer_state(status),
        "owning_phase":
        require_string(requirement, "source_phase",
                       str(descriptor["canonical_criterion_id"])),
        "redaction_status":
        require_string(row, "redaction_status", f"{descriptor['flag']} row"),
        "requirement_ids":
        [*descriptor["producer_requirement_ids"], "ACPT-01"],
        "source_lifecycle_id":
        require_string(requirement, "source_lifecycle_id",
                       str(descriptor["canonical_criterion_id"])),
        "source_lifecycle_status":
        "current",
        "source_ref_status":
        require_string(row, "source_ref_status", f"{descriptor['flag']} row"),
        "source_requirement_ids":
        require_string_list(requirement, "requirement_ids",
                            str(descriptor["canonical_criterion_id"])),
        "status":
        status,
    }


def consumed_upstream_rows(
    root: Path,
    maybe_paths: dict[str, str | None],
    requirements_by_id: dict[str, dict[str, Any]],
    generated_at: str,
    status_vocabulary: set[str],
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for descriptor in UPSTREAM_ROW_INPUTS:
        maybe_path = maybe_paths.get(str(descriptor["arg_name"]))
        if maybe_path is None:
            continue
        input_path, compact_row = load_upstream_input_row(
            root, descriptor, maybe_path)
        canonical_criterion_id = str(descriptor["canonical_criterion_id"])
        requirement = requirements_by_id.get(canonical_criterion_id)
        if requirement is None:
            raise VerificationError(
                f"{canonical_criterion_id} is not a canonical Phase 18 upstream criterion"
            )
        rows[canonical_criterion_id] = canonicalize_compact_upstream_row(
            descriptor,
            input_path,
            compact_row,
            requirement,
            generated_at,
            status_vocabulary,
        )
    return rows


def release_status_counts(rows: dict[str, dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows.values():
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return counts


def aggregate_release_status(rows: dict[str, dict[str, Any]]) -> str:
    statuses = {str(row["status"]) for row in rows.values()}
    for status in [
            "rejected-redaction",
            "rejected-overclaim",
            "failed",
            "blocked",
            "blocked-signing-key-unavailable",
            "external-signing-required",
            "release-run-required",
            "pending-release-input",
            "source-contract-passed",
    ]:
        if status in statuses:
            return status
    if statuses == {"passed"}:
        return "passed"
    return "blocked"


def release_failure_reason(status: str,
                           real_release_evidence_supplied: bool) -> str:
    if status == "passed":
        return "none"
    if not real_release_evidence_supplied:
        return "Release-manager evidence input was not supplied; quick mode used the checked-in Phase 20 template."
    return f"Release evidence aggregate status is {status}; all Phase 20 rows must pass with Phase 26-approved proof classes."


def phase26_requirement_ids(criterion_id: str) -> list[str]:
    if criterion_id == "final-release-artifact-signing-evidence":
        return ["EVID-04", "ACPT-01"]
    return ["ACPT-01"]


def default_upstream_status(criterion_id: str, release_status: str) -> str:
    return {
        "final-ci-evidence": "pending-ci-input",
        "final-simulator-evidence": "pending-simulator-input",
        "final-hardware-safety-media-evidence": "pending-hardware-input",
        "final-live-network-transfer-evidence": "pending-live-input",
        "final-release-artifact-signing-evidence": release_status,
        "final-retained-code-acceptance": "blocked",
        "final-residual-risk-review": "not-required",
        "final-maintainer-decision": "pending",
        "final-reference-demotion-allowed": "blocked",
    }[criterion_id]


def default_maintainer_state(criterion_id: str) -> str:
    if criterion_id in {
            "final-retained-code-acceptance",
            "final-reference-demotion-allowed"
    }:
        return "blocked"
    if criterion_id == "final-residual-risk-review":
        return "not-required"
    return "pending"


def default_failure_reason(criterion_id: str, status: str,
                           release_reason: str) -> str:
    if criterion_id == "final-release-artifact-signing-evidence":
        return release_reason
    if criterion_id == "final-ci-evidence":
        return "Aggregate CI cutover evidence is outside Phase 26 quick input and remains pending."
    if criterion_id == "final-simulator-evidence":
        return "Simulator evidence is owned by Phase 23 and remains pending for final cutover review."
    if criterion_id == "final-hardware-safety-media-evidence":
        return "Hardware, media, and safety evidence is owned by Phase 24 and remains pending for final cutover review."
    if criterion_id == "final-live-network-transfer-evidence":
        return "Live-service evidence is owned by Phase 25 and maps to the Phase 18 live-network criterion."
    if criterion_id == "final-retained-code-acceptance":
        return "Retained-code acceptance is deferred to Phase 27 and cannot be approved by Phase 26."
    if criterion_id == "final-residual-risk-review":
        return "Residual-risk review is not required in Phase 26; Phase 27 owns acceptance input."
    if criterion_id == "final-maintainer-decision":
        return "Maintainer final readiness decision is pending and belongs to Phase 28."
    if criterion_id == "final-reference-demotion-allowed":
        return "Reference demotion requires explicit Phase 28 maintainer approval and is blocked by default."
    return f"Upstream criterion remains {status}."


def evidence_refs_for_criterion(criterion_id: str) -> list[str]:
    return {
        "final-ci-evidence": [
            ".planning/phases/23-simulator-evidence-execution/23-01-SUMMARY.md",
            ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-SUMMARY.md",
            ".planning/phases/25-live-service-evidence-execution/25-01-SUMMARY.md",
        ],
        "final-simulator-evidence": [
            ".planning/phases/23-simulator-evidence-execution/23-01-SUMMARY.md",
            "tools/bazel/manifests/phase23_simulator_evidence_execution_contract.json",
        ],
        "final-hardware-safety-media-evidence": [
            ".planning/phases/24-hardware-media-and-safety-evidence-execution/24-01-SUMMARY.md",
            "tools/bazel/manifests/phase24_hardware_media_safety_evidence_execution_contract.json",
        ],
        "final-live-network-transfer-evidence": [
            ".planning/phases/25-live-service-evidence-execution/25-01-SUMMARY.md",
            "tools/bazel/manifests/phase25_live_service_evidence_execution_contract.json",
        ],
        "final-release-artifact-signing-evidence": [
            (DEFAULT_OUTPUT_DIR /
             "normalized-release-evidence-summary.json").as_posix(),
            (DEFAULT_OUTPUT_DIR /
             "redaction-provenance-summary.json").as_posix(),
        ],
        "final-retained-code-acceptance": [
            "tools/bazel/manifests/phase18_cutover_review_contract.json#final-retained-code-acceptance",
        ],
        "final-residual-risk-review": [
            "tools/bazel/manifests/phase18_cutover_review_contract.json#final-residual-risk-review",
        ],
        "final-maintainer-decision": [
            "tools/bazel/manifests/phase18_cutover_review_contract.json#final-maintainer-decision",
        ],
        "final-reference-demotion-allowed": [
            "tools/bazel/manifests/phase18_cutover_review_contract.json#final-reference-demotion-allowed",
        ],
    }[criterion_id]


def artifact_refs_for_criterion(output_dir: Path,
                                criterion_id: str) -> list[str]:
    if criterion_id == "final-release-artifact-signing-evidence":
        return [
            (output_dir /
             "normalized-release-evidence-summary.json").as_posix(),
            (output_dir / "artifact-reference-summary.json").as_posix(),
        ]
    return [
        (output_dir / "upstream-result-row-table.json").as_posix(),
        (output_dir / "upstream-result-manifest.json").as_posix(),
    ]


def normalize_upstream_row(row: dict[str, Any],
                           requirement: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    status = require_string(
        normalized, "status",
        f"upstream row {row.get('criterion_id', '<missing>')}")
    exception_coverable = set(
        requirement.get("exception_coverable_statuses", []))
    hard_blocking_statuses = set(requirement.get("hard_blocking_statuses", []))
    acceptable_statuses = set(requirement.get("acceptable_statuses", []))
    if normalized.get("redaction_status") != "passed":
        normalized["status"] = "blocked"
        normalized[
            "failure_reason"] = "redaction-failed: redaction_status must be passed before upstream review"
        normalized["maintainer_state"] = "blocked"
    elif normalized.get("source_ref_status") != "passed":
        normalized["status"] = "blocked"
        normalized[
            "failure_reason"] = "source-ref-failed: source_ref_status must be passed before upstream review"
        normalized["maintainer_state"] = "blocked"
    elif normalized.get("source_lifecycle_status") not in {
            "current", "not-required"
    }:
        normalized["status"] = "blocked"
        normalized[
            "failure_reason"] = "lifecycle-mismatch: source lifecycle is not current"
        normalized["maintainer_state"] = "blocked"
    elif status in hard_blocking_statuses:
        normalized["maintainer_state"] = "blocked"
    elif status not in acceptable_statuses and status not in exception_coverable:
        normalized["maintainer_state"] = "blocked"
    return normalized


def build_upstream_rows(
    root: Path,
    output_dir: Path,
    release_rows: dict[str, dict[str, Any]],
    real_release_evidence_supplied: bool,
    generated_at: str,
    consumed_rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    phase18_contract = load_json(root, PHASE18_CONTRACT)
    status_vocabulary = phase18_upstream_status_vocabulary(phase18_contract)
    release_status = aggregate_release_status(release_rows)
    release_reason = release_failure_reason(release_status,
                                            real_release_evidence_supplied)
    rows: list[dict[str, Any]] = []
    for requirement in phase18_upstream_requirements(phase18_contract):
        criterion_id = require_string(requirement, "criterion_id",
                                      "upstream_result_requirement")
        maybe_consumed_row = consumed_rows.get(criterion_id)
        if maybe_consumed_row is None:
            status = default_upstream_status(criterion_id, release_status)
            if status not in status_vocabulary:
                raise VerificationError(
                    f"{criterion_id} produced unknown upstream status: {status}"
                )
            row = {
                "artifact_refs":
                artifact_refs_for_criterion(output_dir, criterion_id),
                "criterion_id":
                criterion_id,
                "evidence_family":
                require_string(requirement, "evidence_family", criterion_id),
                "evidence_refs":
                evidence_refs_for_criterion(criterion_id),
                "exception_status":
                "none",
                "failure_reason":
                default_failure_reason(criterion_id, status, release_reason),
                "generated_at_utc":
                generated_at,
                "maintainer_state":
                default_maintainer_state(criterion_id),
                "owning_phase":
                require_string(requirement, "source_phase", criterion_id),
                "redaction_status":
                "passed",
                "requirement_ids":
                phase26_requirement_ids(criterion_id),
                "source_lifecycle_id":
                require_string(requirement, "source_lifecycle_id",
                               criterion_id),
                "source_lifecycle_status":
                "current",
                "source_ref_status":
                "passed",
                "source_requirement_ids":
                require_list(requirement, "requirement_ids", criterion_id),
                "status":
                status,
            }
        else:
            row = maybe_consumed_row
        normalized = normalize_upstream_row(row, requirement)
        missing = [
            field for field in UPSTREAM_RESULT_ROW_FIELDS
            if field not in normalized
        ]
        if missing:
            raise VerificationError(
                f"{criterion_id} normalized upstream row missing fields: {', '.join(missing)}"
            )
        rows.append(normalized)
    row_ids = [str(row["criterion_id"]) for row in rows]
    if row_ids != CANONICAL_PHASE18_CRITERIA:
        raise VerificationError(
            "normalized upstream rows must match the nine canonical Phase 18 criteria"
        )
    return rows
