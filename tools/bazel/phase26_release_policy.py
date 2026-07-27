from __future__ import annotations

from phase26_release_contract import *


def validate_output_dir(root: Path, output_dir: Path) -> tuple[Path, Path]:
    if output_dir.is_absolute() or ".." in output_dir.parts:
        raise VerificationError(
            f"--output-dir must be repo-relative under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        )
    try:
        output_dir.relative_to(DEFAULT_OUTPUT_DIR)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        ) from error
    current = root
    for part in output_dir.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(
                f"--output-dir contains a symlink escape risk: {output_dir.as_posix()}"
            )
    full_output_dir = (root / output_dir).resolve(strict=False)
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir must resolve under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}"
        ) from error
    return output_dir, full_output_dir


def validate_ref(ref: str, allowed_roots: list[str], row_name: str,
                 field: str) -> str:
    if not ref:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    for allowed_root in allowed_roots:
        if allowed_root.startswith("external://") and ref.startswith(
                allowed_root):
            if ".." in ref or ref.endswith("/"):
                raise VerificationError(
                    f"{row_name} {field} ref is unsafe: {ref}")
            return ref
        if not allowed_root.startswith("external://"):
            relative_path = Path(ref)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise VerificationError(
                    f"{row_name} {field} ref escapes allowed roots: {ref}")
            try:
                relative_path.relative_to(Path(allowed_root))
                return ref
            except ValueError:
                continue
    raise VerificationError(
        f"{row_name} {field} ref must stay under allowed release roots: {ref}")


def validate_ref_list(
    row: dict[str, Any],
    field: str,
    row_name: str,
    allowed_roots: list[str],
    require_nonempty: bool,
) -> list[str]:
    values = require_list(row, field, row_name)
    if require_nonempty and not values:
        raise VerificationError(f"{row_name} {field} must be non-empty")
    refs: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str):
            raise VerificationError(
                f"{row_name} {field}[{index}] must be a string")
        refs.append(
            validate_ref(value, allowed_roots, row_name, f"{field}[{index}]"))
    return refs


def validate_subject_digests(
    row: dict[str, Any],
    row_name: str,
    allowed_roots: list[str],
    errors: list[str],
    require_nonempty: bool = True,
) -> None:
    subject_digests = row.get("subject_digests")
    if not isinstance(subject_digests, list):
        errors.append(f"{row_name} subject_digests must be a list")
        return
    if not subject_digests:
        if require_nonempty:
            errors.append(f"{row_name} subject_digests must be non-empty")
        return
    for index, digest_row in enumerate(subject_digests):
        digest_name = f"{row_name} subject_digests[{index}]"
        if not isinstance(digest_row, dict):
            errors.append(f"{digest_name} must be an object")
            continue
        extra_fields = sorted(set(digest_row) - DIGEST_FIELDS)
        if extra_fields:
            errors.append(
                f"{digest_name} contains unsupported fields: {', '.join(extra_fields)}"
            )
            continue
        artifact_ref = digest_row.get("artifact_ref")
        if not isinstance(artifact_ref, str):
            errors.append(f"{digest_name} artifact_ref must be a string")
        else:
            try:
                validate_ref(artifact_ref, allowed_roots, digest_name,
                             "artifact_ref")
            except VerificationError as error:
                errors.append(str(error))
        sha256 = digest_row.get("sha256")
        if not isinstance(sha256, str) or not re.fullmatch(
                r"[0-9a-f]{64}", sha256):
            errors.append(
                f"{digest_name} sha256 must be lowercase SHA-256 hex")


def phase20_required_metadata_fields(
        contract_row: dict[str, Any]) -> list[str]:
    fields: list[str] = []
    row_id = contract_row.get("id", "<unknown>")
    for group in PHASE20_REQUIRED_METADATA_GROUPS:
        values = contract_row.get(group, [])
        if not isinstance(values, list) or not all(
                isinstance(value, str) and value for value in values):
            raise VerificationError(
                f"Phase 20 row {row_id} {group} must contain strings")
        fields.extend(values)
    return list(dict.fromkeys(fields))


def phase20_allowed_metadata_fields(contract_row: dict[str, Any]) -> list[str]:
    fields = [
        "id",
        "artifact_surface",
        "proof_class",
        "status",
        "mismatch_class",
        *REQUIRED_PASS_METADATA,
        *phase20_required_metadata_fields(contract_row),
    ]
    row_id = contract_row.get("id", "<unknown>")
    for group in PHASE20_OPTIONAL_METADATA_GROUPS:
        values = contract_row.get(group, [])
        if not isinstance(values, list) or not all(
                isinstance(value, str) and value for value in values):
            raise VerificationError(
                f"Phase 20 row {row_id} {group} must contain strings")
        fields.extend(values)
    return list(dict.fromkeys(fields))


def sanitized_release_row(row: dict[str, Any],
                          contract_row: dict[str, Any]) -> dict[str, Any]:
    allowed_fields = set(phase20_allowed_metadata_fields(contract_row))
    extra_fields = sorted(set(row) - allowed_fields)
    if extra_fields:
        raise VerificationError("release input contains unsupported fields: " +
                                ", ".join(extra_fields))
    sanitized = {
        field: row[field]
        for field in phase20_allowed_metadata_fields(contract_row)
        if field in row
    }
    if "subject_digests" in sanitized:
        sanitized["subject_digests"] = [
            {
                "artifact_ref": digest["artifact_ref"],
                "sha256": digest["sha256"]
            } for digest in sanitized["subject_digests"]
            if isinstance(digest, dict) and DIGEST_FIELDS <= digest.keys()
        ]
    return sanitized


def validate_required_phase20_metadata(
    row: dict[str, Any],
    contract_row: dict[str, Any],
    row_name: str,
    allowed_roots: list[str],
    errors: list[str],
) -> None:
    try:
        metadata_fields = phase20_required_metadata_fields(contract_row)
    except VerificationError as error:
        errors.append(str(error))
        return
    for field in metadata_fields:
        try:
            if field in {"artifact_refs", "retention_refs"}:
                validate_ref_list(row,
                                  field,
                                  row_name,
                                  allowed_roots,
                                  require_nonempty=True)
            elif field == "subject_digests":
                validate_subject_digests(row, row_name, allowed_roots, errors)
            else:
                require_string(row, field, row_name)
        except VerificationError as error:
            errors.append(str(error))


def release_input_rows(root: Path,
                       maybe_path: str | None) -> list[dict[str, Any]]:
    input_path = Path(
        maybe_path
    ) if maybe_path is not None else PHASE20_RELEASE_INPUT_TEMPLATE
    full_path = input_path if input_path.is_absolute() else root / input_path
    if not full_path.exists():
        raise VerificationError(
            f"release input file does not exist: {input_path.as_posix()}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"release input is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    rows = data.get("evidence_rows") if isinstance(data, dict) else None
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


def validate_release_row(
    row: dict[str, Any],
    contract_row: dict[str, Any],
    row_name: str,
    status_vocabulary: set[str],
    proof_class_vocabulary: set[str],
    allowed_roots: list[str],
) -> None:
    errors: list[str] = []
    status = require_string(row, "status", row_name)
    proof_class = require_string(row, "proof_class", row_name)
    if status not in status_vocabulary:
        errors.append(f"{row_name} status is invalid: {status}")
    if proof_class not in proof_class_vocabulary and proof_class not in NON_PASS_PROOF_CLASSES:
        errors.append(f"{row_name} proof_class is invalid: {proof_class}")
    if row.get("artifact_surface") and row.get(
            "artifact_surface") != contract_row.get("artifact_surface"):
        errors.append(
            f"{row_name} artifact_surface does not match contract row {contract_row.get('id')}"
        )
    for field in ["artifact_refs", "retention_refs"]:
        try:
            validate_ref_list(row,
                              field,
                              row_name,
                              allowed_roots,
                              require_nonempty=status == "passed")
        except VerificationError as error:
            errors.append(str(error))
    if status != "passed" and "subject_digests" in row:
        validate_subject_digests(row,
                                 row_name,
                                 allowed_roots,
                                 errors,
                                 require_nonempty=False)
    if status == "passed":
        if proof_class not in PASS_CAPABLE_PROOF_CLASSES:
            errors.append(
                f"{row_name} cannot pass with proof_class={proof_class!r}; release-candidate cannot pass Phase 26"
            )
        for field in REQUIRED_PASS_METADATA:
            try:
                if field in {"artifact_refs", "retention_refs"}:
                    validate_ref_list(row,
                                      field,
                                      row_name,
                                      allowed_roots,
                                      require_nonempty=True)
                elif field == "subject_digests":
                    validate_subject_digests(row, row_name, allowed_roots,
                                             errors)
                else:
                    require_string(row, field, row_name)
            except VerificationError as error:
                errors.append(str(error))
        validate_required_phase20_metadata(row, contract_row, row_name,
                                           allowed_roots, errors)
    mismatch_class = row.get("mismatch_class")
    mismatch_values = {
        "pass", "intentional-delta", "blocker", "deferred-retained-code-issue"
    }
    if mismatch_class is not None and mismatch_class not in mismatch_values:
        errors.append(
            f"{row_name} mismatch_class is invalid: {mismatch_class}")
    if errors:
        raise VerificationError("\n".join(errors))


def validate_release_input(
        root: Path, maybe_path: str | None) -> dict[str, dict[str, Any]]:
    phase20_contract = load_json(root, PHASE20_CONTRACT)
    contract_by_id = {
        str(row["id"]): row
        for row in contract_rows(phase20_contract, PHASE20_CONTRACT)
    }
    expected_ids = phase20_release_row_ids(phase20_contract)
    status_vocabulary = phase20_status_vocabulary(phase20_contract)
    proof_class_vocabulary = phase20_proof_class_vocabulary(phase20_contract)
    release_input_schema = phase20_contract.get("release_input_schema")
    if not isinstance(release_input_schema, dict):
        raise VerificationError(
            f"{PHASE20_CONTRACT.as_posix()} release_input_schema must be an object"
        )
    allowed_roots = release_input_schema.get("allowed_ref_roots")
    if not isinstance(allowed_roots, list) or not all(
            isinstance(root_value, str) and root_value
            for root_value in allowed_roots):
        raise VerificationError(
            "Phase 20 release_input_schema allowed_ref_roots must contain strings"
        )
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(release_input_rows(root, maybe_path)):
        row_name = f"release input row {index}"
        try:
            row_id = require_string(row, "id", row_name)
            if row_id not in contract_by_id:
                raise VerificationError(
                    f"{row_name} uses unknown row id: {row_id}")
            if row_id in parsed_rows:
                raise VerificationError(
                    f"{row_name} duplicates row id: {row_id}")
            validate_release_row(
                row,
                contract_by_id[row_id],
                row_name,
                status_vocabulary,
                proof_class_vocabulary,
                allowed_roots,
            )
            parsed_rows[row_id] = sanitized_release_row(
                row, contract_by_id[row_id])
        except VerificationError as error:
            errors.append(str(error))
    missing = [row_id for row_id in expected_ids if row_id not in parsed_rows]
    if missing:
        errors.append("release input missing rows: " + ", ".join(missing))
    ordered_ids = list(parsed_rows)
    if not missing and ordered_ids != expected_ids:
        errors.append(
            "release input row order must match Phase 20 canonical rows")
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows
