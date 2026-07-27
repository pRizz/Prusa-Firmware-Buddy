#!/usr/bin/env python3
from __future__ import annotations

from phase17_evidence_policy import *


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase17_release_candidate_evidence_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase17-release-candidate-evidence",
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    try:
        statuses = require_list_of_strings(contract, "status_vocabulary",
                                           "contract")
        mismatch_classes = require_list_of_strings(
            contract, "mismatch_class_vocabulary", "contract")
        artifact_kinds = set(
            require_list_of_strings(contract, "required_artifact_kinds",
                                    "contract"))
        products = set(
            require_list_of_strings(contract, "supported_release_products",
                                    "contract"))
        boards = set(
            require_list_of_strings(contract, "supported_release_boards",
                                    "contract"))
        rows = contract_rows(contract)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    if statuses != STATUS_VOCABULARY:
        errors.append(
            "status_vocabulary does not match the Phase 17 vocabulary")
    if mismatch_classes != MISMATCH_CLASS_VOCABULARY:
        errors.append(
            "mismatch_class_vocabulary does not match the Phase 17 vocabulary")
    for missing in sorted(REQUIRED_ARTIFACT_KINDS - artifact_kinds):
        errors.append(f"missing required artifact kind: {missing}")
    for missing in sorted(REQUIRED_RELEASE_PRODUCTS - products):
        errors.append(f"missing required supported release product: {missing}")
    for missing in sorted(REQUIRED_RELEASE_BOARDS - boards):
        errors.append(f"missing required supported release board: {missing}")
    validate_release_input_schema(contract, errors)
    validate_workflow_identities(contract, errors)
    validate_rows(root, rows, artifact_kinds, errors)
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def validate_rows(root: Path, rows: list[dict[str, Any]],
                  artifact_kinds: set[str], errors: list[str]) -> None:
    row_ids = [str(row.get("id")) for row in rows]
    for missing in sorted(REQUIRED_ROW_IDS - set(row_ids)):
        errors.append("missing required release row: " + missing)
    if len(row_ids) != len(set(row_ids)):
        errors.append("duplicate release row IDs are not allowed")
    covered_requirements: set[str] = set()
    covered_surfaces: set[str] = set()
    for row in rows:
        row_name = str(row.get("id", "unknown row"))
        try:
            validate_row_shape(root, row, row_name, artifact_kinds)
            covered_requirements.update(row["requirement_ids"])
            covered_surfaces.add(str(row["artifact_surface"]))
        except VerificationError as error:
            errors.append(str(error))
    for missing in sorted(REQUIRED_REQUIREMENT_IDS - covered_requirements):
        errors.append("missing REL requirement coverage: " + missing)
    for missing in sorted(REQUIRED_ARTIFACT_SURFACES - covered_surfaces):
        errors.append("missing required artifact surface coverage: " + missing)


def validate_row_shape(root: Path, row: dict[str, Any], row_name: str,
                       artifact_kinds: set[str]) -> None:
    errors: list[str] = []
    try:
        require_fields(row, REQUIRED_ROW_FIELDS, row_name)
        requirement_ids = set(
            require_list_of_strings(row, "requirement_ids", row_name))
        source_refs = require_list_of_strings(row, "source_contract_refs",
                                              row_name)
        source_doc_refs = require_list_of_strings(row, "source_doc_refs",
                                                  row_name)
        allowed_statuses = set(
            require_list_of_strings(row, "allowed_statuses", row_name))
        fallback_status = "source-contract-passed" if row.get(
            "proof_scope") == "source-contract" else "pending-release-input"
        default_status = str(row.get("default_status", fallback_status))
        artifact_outputs = require_list_of_strings(row, "artifact_outputs",
                                                   row_name)
        retained_artifact_kind = require_string(row, "retained_artifact_kind",
                                                row_name)
        artifact_path = require_string(row, "expected_artifact_path", row_name)
        mismatch_class = require_string(row, "mismatch_class", row_name)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    unknown_requirements = sorted(requirement_ids - REQUIRED_REQUIREMENT_IDS)
    if unknown_requirements:
        errors.append(
            f"{row_name} uses unknown requirement IDs: {', '.join(unknown_requirements)}"
        )
    for source_ref in source_refs:
        try:
            resolve_source_ref(root, source_ref, row_name)
        except VerificationError as error:
            errors.append(str(error))
    for doc_ref in source_doc_refs:
        try:
            validate_doc_ref(root, doc_ref, row_name)
        except VerificationError as error:
            errors.append(str(error))
    try:
        require_repo_relative_under(artifact_path, DEFAULT_OUTPUT_DIR,
                                    row_name)
    except VerificationError as error:
        errors.append(str(error))
    if retained_artifact_kind not in artifact_kinds:
        errors.append(
            f"{row_name} retained_artifact_kind is not declared: {retained_artifact_kind}"
        )
    if not allowed_statuses <= set(STATUS_VOCABULARY):
        errors.append(f"{row_name} allowed_statuses contains unknown statuses")
    if default_status not in STATUS_VOCABULARY:
        errors.append(
            f"{row_name} default_status is invalid: {default_status}")
    elif default_status not in allowed_statuses:
        errors.append(
            f"{row_name} default_status {default_status} is not allowed by allowed_statuses"
        )
    if mismatch_class not in MISMATCH_CLASS_VOCABULARY:
        errors.append(
            f"{row_name} mismatch_class is invalid: {mismatch_class}")
    if default_status == "passed" and row.get(
            "proof_scope") != "source-contract":
        errors.append(
            f"{row_name} default_status cannot be passed without approved release evidence"
        )
    if row.get("release_run_required") is True:
        expected = RELEASE_WORKFLOW_IDENTITIES[
            "phase17_release_candidate_artifacts"]
        if row.get("bazel_label") != expected["bazel_label"]:
            errors.append(
                f"{row_name} bazel_label must be {expected['bazel_label']!r}, not {row.get('bazel_label')!r}"
            )
        if row.get("release_command") != expected["release_command"]:
            errors.append(
                f"{row_name} release_command must be {expected['release_command']!r}"
            )
        if row.get("bazel_label") in LOCAL_SMOKE_WORKFLOW_IDENTITIES:
            errors.append(
                f"{row_name} representative smoke label cannot satisfy release_run_required"
            )
    if row.get("release_run_required") is not True and row.get(
            "release_run_required") is not False:
        errors.append(f"{row_name} release_run_required must be boolean")
    if not artifact_outputs:
        errors.append(f"{row_name} artifact_outputs must not be empty")
    for list_field in [
            "release_metadata_required",
            "signing_metadata_required",
            "provenance_metadata_required",
            "comparison_metadata_required",
            "residual_cutover_gates",
            "unsupported_claims",
    ]:
        if not isinstance(row.get(list_field), list):
            errors.append(f"{row_name} {list_field} must be a list")
    if row.get("redaction_required") is not True:
        errors.append(f"{row_name} redaction_required must be true")
    if errors:
        raise VerificationError("\n".join(errors))


def load_release_evidence_path(
        root: Path, path: str | None) -> tuple[Path | None, list[Any] | None]:
    if not path:
        return None, None
    evidence_path = Path(path)
    full_path = evidence_path if evidence_path.is_absolute(
    ) else root / evidence_path
    if not full_path.exists():
        raise VerificationError(
            f"release evidence file does not exist: {path}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(evidence_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"release evidence is not valid JSON: {error}") from error
    if isinstance(data, list):
        return evidence_path, data
    if isinstance(data, dict) and isinstance(data.get("evidence_rows"), list):
        return evidence_path, data["evidence_rows"]
    raise VerificationError(
        "release evidence must contain an evidence_rows list or be a top-level list"
    )


def validate_refs(refs: Any,
                  row_name: str,
                  field: str,
                  require_nonempty: bool = True) -> list[str]:
    if not isinstance(refs, list) or (require_nonempty and not refs):
        raise VerificationError(f"{row_name} {field} must be a non-empty list")
    parsed: list[str] = []
    for index, ref in enumerate(refs):
        ref_name = f"{row_name} {field}[{index}]"
        if not isinstance(ref, str) or not ref:
            raise VerificationError(f"{ref_name} must be a non-empty string")
        if ref.startswith("external://phase17/"):
            parsed.append(ref)
            continue
        if ref.startswith("artifact://") or ref.startswith("external://"):
            raise VerificationError(
                f"{ref_name} must use repo-relative path or external://phase17/... reference"
            )
        require_repo_relative_under(ref, DEFAULT_OUTPUT_DIR, ref_name)
        parsed.append(ref)
    return parsed


def require_iso_8601_utc(row: dict[str, Any], field: str,
                         row_name: str) -> None:
    timestamp_text = require_string(row, field, row_name)
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(
            f"{row_name} {field} must be ISO-8601 UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(
            parsed):
        raise VerificationError(f"{row_name} {field} must be ISO-8601 UTC")


def matching_contract_row(rows: list[dict[str, Any]], evidence_row: dict[str,
                                                                         Any],
                          row_name: str) -> dict[str, Any]:
    artifact_surface = evidence_row.get("artifact_surface")
    product_profile = evidence_row.get("product_profile")
    matches = [
        row for row in rows if row.get("artifact_surface") == artifact_surface
        and row.get("product_profile") == product_profile
    ]
    if len(matches) != 1:
        raise VerificationError(
            f"{row_name} does not match exactly one contract row")
    return matches[0]


def validated_release_rows(root: Path, contract: dict[str, Any],
                           path: str | None) -> dict[str, dict[str, Any]]:
    evidence_path, rows = load_release_evidence_path(root, path)
    if rows is None:
        return {}
    contract_rows_by_match = contract_rows(contract)
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"release evidence row {index}"
        if not isinstance(row, dict):
            errors.append(f"{row_name} must be an object")
            continue
        try:
            require_fields(row, REQUIRED_RELEASE_EVIDENCE_FIELDS, row_name)
            forbidden_keys = sorted(FORBIDDEN_FIELD_NAMES & set(row))
            if forbidden_keys:
                raise VerificationError(
                    f"{row_name} contains forbidden evidence fields: {', '.join(forbidden_keys)}"
                )
            reject_forbidden_text(evidence_path or Path("release-evidence"),
                                  json.dumps(row, sort_keys=True))
            require_iso_8601_utc(row, "timestamp", row_name)
            contract_row = matching_contract_row(contract_rows_by_match, row,
                                                 row_name)
            contract_row_id = str(contract_row["id"])
            if contract_row_id in parsed_rows:
                raise VerificationError(
                    f"{row_name} duplicates release evidence for {contract_row_id}"
                )
            validate_release_row_against_contract(row, contract_row, row_name)
        except VerificationError as error:
            errors.append(str(error))
            continue
        parsed_rows[contract_row_id] = dict(row)
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def validate_release_row_against_contract(row: dict[str, Any],
                                          contract_row: dict[str, Any],
                                          row_name: str) -> None:
    errors: list[str] = []
    for field in [
            "bazel_label", "release_command", "artifact_outputs",
            "release_run_required"
    ]:
        if row.get(field) != contract_row.get(field):
            errors.append(
                f"{row_name} {field} {row.get(field)!r} does not match contract row {contract_row['id']}"
            )
    result = require_string(row, "result", row_name)
    allowed_statuses = set(
        require_list_of_strings(contract_row, "allowed_statuses",
                                str(contract_row["id"])))
    if result not in STATUS_VOCABULARY:
        errors.append(f"{row_name} uses unsupported result: {result}")
    elif result not in allowed_statuses:
        errors.append(
            f"{row_name} result {result} is not allowed for {contract_row['id']}"
        )
    evidence_type = require_string(row, "evidence_type", row_name)
    digest = require_string(row, "artifact_digest_sha256", row_name)
    if digest and not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append(
            f"{row_name} artifact_digest_sha256 must be lowercase SHA-256 hex")
    if not digest and contract_row.get("proof_scope") != "source-contract":
        errors.append(
            f"{row_name} artifact_digest_sha256 is required for release evidence"
        )
    for field in ["artifact_refs", "provenance_refs", "comparison_refs"]:
        try:
            validate_refs(row[field],
                          row_name,
                          field,
                          require_nonempty=result == "passed")
        except VerificationError as error:
            errors.append(str(error))
    if row.get("retention_path", "").startswith("external://"):
        if not str(row["retention_path"]).startswith("external://phase17/"):
            errors.append(
                f"{row_name} retention_path must use external://phase17/... reference"
            )
    else:
        try:
            require_repo_relative_under(str(row["retention_path"]),
                                        DEFAULT_OUTPUT_DIR, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if row.get("mismatch_class") not in MISMATCH_CLASS_VOCABULARY:
        errors.append(
            f"{row_name} mismatch_class is invalid: {row.get('mismatch_class')}"
        )
    if result == "passed" and contract_row.get("release_run_required") is True:
        expected = RELEASE_WORKFLOW_IDENTITIES[
            "phase17_release_candidate_artifacts"]
        if evidence_type not in APPROVED_RELEASE_EVIDENCE_TYPES:
            errors.append(
                f"{row_name} passed release evidence must use approved-release evidence_type"
            )
        if row.get("bazel_label") != expected["bazel_label"]:
            errors.append(
                f"{row_name} passed release evidence must use {expected['bazel_label']}"
            )
        if row.get("release_command") != expected["release_command"]:
            errors.append(
                f"{row_name} passed release evidence must use {expected['release_command']}"
            )
        if not all(
                str(row.get(field, "")) for field in [
                    "key_identity_ref", "verification_outcome",
                    "mismatch_reason", "owner_phase", "residual_risk"
                ]):
            errors.append(
                f"{row_name} passed release evidence is missing required verification metadata"
            )
    if row.get("bazel_label"
               ) in LOCAL_SMOKE_WORKFLOW_IDENTITIES and contract_row.get(
                   "release_run_required") is True:
        errors.append(
            f"{row_name} representative smoke labels cannot satisfy production release proof"
        )
    if errors:
        raise VerificationError("\n".join(errors))
