from __future__ import annotations

from phase20_artifact_contract import *


def load_release_input(root: Path,
                       maybe_path: str | None) -> list[dict[str, Any]]:
    if maybe_path is None:
        return []
    input_path = Path(maybe_path)
    full_path = input_path if input_path.is_absolute() else root / input_path
    if not full_path.exists():
        raise VerificationError(
            f"release input file does not exist: {maybe_path}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"release input is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    rows = data.get("evidence_rows") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise VerificationError(
            "release input must contain an evidence_rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(
                f"release input row {index} must be an object")
        parsed_rows.append(row)
    return parsed_rows


def validated_release_rows(
        root: Path, contract: dict[str, Any],
        maybe_path: str | None) -> dict[str, dict[str, Any]]:
    rows = load_release_input(root, maybe_path)
    if not rows:
        return {}
    contract_by_id = {str(row["id"]): row for row in contract_rows(contract)}
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(rows):
        row_name = f"release input row {index}"
        try:
            row_id = require_string(row, "id", row_name)
            if row_id not in contract_by_id:
                raise VerificationError(
                    f"{row_name} uses unknown row id: {row_id}")
            if row_id in parsed_rows:
                raise VerificationError(
                    f"{row_name} duplicates row id: {row_id}")
            validate_release_row(row, contract_by_id[row_id], row_name)
            parsed_rows[row_id] = dict(row)
        except VerificationError as error:
            errors.append(str(error))
    missing = [
        row_id for row_id in REQUIRED_ROW_IDS if row_id not in parsed_rows
    ]
    if missing:
        errors.append("release input missing rows: " + ", ".join(missing))
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def validate_release_row(row: dict[str, Any], contract_row: dict[str, Any],
                         row_name: str) -> None:
    errors: list[str] = []
    status = require_string(row, "status", row_name)
    proof_class = require_string(row, "proof_class", row_name)
    if status not in STATUS_VOCABULARY:
        errors.append(f"{row_name} status is invalid: {status}")
    if proof_class not in PROOF_CLASS_VOCABULARY:
        errors.append(f"{row_name} proof_class is invalid: {proof_class}")
    if row.get("artifact_surface") and row.get(
            "artifact_surface") != contract_row["artifact_surface"]:
        errors.append(
            f"{row_name} artifact_surface does not match contract row {contract_row['id']}"
        )
    for field in ["artifact_refs", "retention_refs"]:
        try:
            validate_ref_list(row,
                              field,
                              row_name,
                              require_nonempty=status == "passed")
        except VerificationError as error:
            errors.append(str(error))
    if status == "passed":
        for field in contract_row["comparison_metadata_required"]:
            try:
                value = require_string(row, field, row_name)
            except VerificationError as error:
                errors.append(str(error))
                continue
            if field == "owner_phase" and value != PHASE:
                errors.append(f"{row_name} owner_phase must be {PHASE}")
            if field == "affected_artifact_surface" and value != contract_row[
                    "artifact_surface"]:
                errors.append(
                    f"{row_name} affected_artifact_surface must match contract row {contract_row['id']}"
                )
    mismatch_class = row.get("mismatch_class")
    if mismatch_class is not None and mismatch_class not in MISMATCH_CLASS_VOCABULARY:
        errors.append(
            f"{row_name} mismatch_class is invalid: {mismatch_class}")
    if status == "passed":
        if proof_class not in APPROVED_PASS_PROOF_CLASSES:
            errors.append(
                f"{row_name} cannot pass with proof_class={proof_class!r}")
        for field in REQUIRED_PASS_FIELDS:
            try:
                if field in ["subject_digests", "retention_refs"]:
                    require_non_empty_list(row, field, row_name)
                else:
                    require_string(row, field, row_name)
            except VerificationError as error:
                errors.append(str(error))
        validate_subject_digests(row, row_name, errors)
        validate_required_metadata(row, contract_row, row_name, errors)
    if errors:
        raise VerificationError("\n".join(errors))


def validate_required_metadata(row: dict[str, Any], contract_row: dict[str,
                                                                       Any],
                               row_name: str, errors: list[str]) -> None:
    metadata_fields = [
        *contract_row["release_metadata_required"],
        *contract_row["signing_metadata_required"],
        *contract_row["provenance_metadata_required"],
        *contract_row["retention_metadata_required"],
    ]
    for field in dict.fromkeys(metadata_fields):
        try:
            if field in {"artifact_refs", "retention_refs"}:
                validate_ref_list(row, field, row_name, require_nonempty=True)
            elif field == "subject_digests":
                validate_subject_digests(row, row_name, errors)
            else:
                require_string(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))


def validate_subject_digests(row: dict[str, Any], row_name: str,
                             errors: list[str]) -> None:
    subject_digests = row.get("subject_digests")
    if not isinstance(subject_digests, list) or not subject_digests:
        errors.append(f"{row_name} subject_digests must be non-empty")
        return
    for index, digest_row in enumerate(subject_digests):
        digest_name = f"{row_name} subject_digests[{index}]"
        if not isinstance(digest_row, dict):
            errors.append(f"{digest_name} must be an object")
            continue
        artifact_ref = digest_row.get("artifact_ref")
        if not isinstance(artifact_ref, str):
            errors.append(f"{digest_name} artifact_ref must be a string")
        else:
            try:
                validate_ref(artifact_ref, digest_name, "artifact_ref")
            except VerificationError as error:
                errors.append(str(error))
        sha256 = digest_row.get("sha256")
        if not isinstance(sha256, str) or not re.fullmatch(
                r"[0-9a-f]{64}", sha256):
            errors.append(
                f"{digest_name} sha256 must be lowercase SHA-256 hex")


def quick_result_row(
        contract_row: dict[str, Any],
        maybe_release_row: dict[str, Any] | None) -> dict[str, Any]:
    row = {
        "id": contract_row["id"],
        "title": contract_row["title"],
        "requirement_ids": contract_row["requirement_ids"],
        "artifact_surface": contract_row["artifact_surface"],
        "artifact_outputs": contract_row["artifact_outputs"],
        "proof_class": "template-only",
        "status": contract_row["default_status"],
        "artifact_refs": [],
        "release_run_id": "",
        "timestamp": "",
        "operator": "",
        "subject_digests": [],
        "build_input_identity": "",
        "key_identity_ref": "",
        "signing_mode": "",
        "contract_validation": "",
        "redaction_scan": "",
        "source_contract_snapshot": "",
        "retention_refs": [],
        "verification_outcome": "pending-release-input",
        "mismatch_class": "blocker",
        "mismatch_reason": "Awaiting approved release comparison metadata.",
        "owner_phase": PHASE,
        "affected_artifact_surface": contract_row["artifact_surface"],
        "residual_risk": "Awaiting approved release-run evidence.",
    }
    if maybe_release_row is None:
        return row
    for field in [
            "proof_class",
            "status",
            "artifact_refs",
            "release_run_id",
            "timestamp",
            "operator",
            "subject_digests",
            "build_input_identity",
            "key_identity_ref",
            "signing_mode",
            "contract_validation",
            "redaction_scan",
            "source_contract_snapshot",
            "retention_refs",
            "verification_outcome",
            "mismatch_class",
            "mismatch_reason",
            "owner_phase",
            "affected_artifact_surface",
            "residual_risk",
    ]:
        if field in maybe_release_row:
            row[field] = maybe_release_row[field]
    return row
