from __future__ import annotations


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(root: Path, path: str | Path) -> str:
    relative_path = Path(path)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: str | Path) -> dict[str, Any]:
    relative_path = Path(path)
    try:
        data = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{relative_path.as_posix()} is not valid JSON: {error}"
        ) from error
    if not isinstance(data, dict):
        raise VerificationError(
            f"{relative_path.as_posix()} must contain a top-level object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def require_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{field} must be an object")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError(f"{field} must be a list")
    return value


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VerificationError(f"{field} must be a non-blank string")
    return value


def require_string_list(value: Any, field: str) -> list[str]:
    values = require_list(value, field)
    if not all(isinstance(item, str) and item.strip() for item in values):
        raise VerificationError(f"{field} must contain non-blank strings")
    return values


def require_non_empty_string_list(value: Any, field: str) -> list[str]:
    values = require_string_list(value, field)
    if not values:
        raise VerificationError(f"{field} must contain at least one entry")
    return values


def require_iso_utc(timestamp_text: str, field: str) -> None:
    if not timestamp_text.endswith("Z"):
        raise VerificationError(f"{field} must be ISO UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as error:
        raise VerificationError(f"{field} must be ISO UTC") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(
            parsed):
        raise VerificationError(f"{field} must be ISO UTC")


def repo_relative_path(value: str | Path, field: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise VerificationError(
            f"{field} must be repo-relative without traversal: {path.as_posix()}"
        )
    return path


def path_under(value: str | Path, expected_root: Path, field: str) -> Path:
    path = repo_relative_path(value, field)
    try:
        path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{field} must be under {expected_root.as_posix()}: {path.as_posix()}"
        ) from error
    return path


def resolved_under(root: Path, relative_path: Path, expected_root: Path,
                   field: str) -> Path:
    current = root
    for part in relative_path.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(
                f"{field} contains a symlink escape: {relative_path.as_posix()}"
            )
    full_path = (root / relative_path).resolve(strict=False)
    trusted_root = (root / expected_root).resolve(strict=False)
    try:
        full_path.relative_to(trusted_root)
    except ValueError as error:
        raise VerificationError(
            f"{field} resolves outside {expected_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return full_path


def path_is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def output_dir_path(root: Path, output_dir: str | Path) -> tuple[Path, Path]:
    relative_output_dir = path_under(output_dir, DEFAULT_OUTPUT_DIR,
                                     "--output-dir")
    current = root
    for part in relative_output_dir.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(
                f"--output-dir contains a symlink component: {relative_output_dir.as_posix()}"
            )
    full_output_dir = (root / relative_output_dir).resolve(strict=False)
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"--output-dir resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_output_dir.as_posix()}"
        ) from error
    return relative_output_dir, full_output_dir


def reset_output_root(full_output_dir: Path) -> None:
    if full_output_dir.exists():
        if full_output_dir.is_symlink() or not full_output_dir.is_dir():
            raise VerificationError(
                f"--output-dir exists and is not a normal directory: {full_output_dir.as_posix()}"
            )
        shutil.rmtree(full_output_dir)
    full_output_dir.mkdir(parents=True, exist_ok=True)


def reject_decisions_inside_output(root: Path,
                                   maybe_decisions_path: str | None,
                                   full_output_dir: Path) -> None:
    if maybe_decisions_path is None:
        return
    decisions_path = (root / repo_relative_path(
        maybe_decisions_path, "--maintainer-decisions")).resolve(strict=False)
    if path_is_under(decisions_path, full_output_dir.resolve(strict=False)):
        raise VerificationError(
            "--maintainer-decisions must be outside the generated --output-dir"
        )


def repo_relative_output_dir(output_dir: Path) -> Path:
    if not output_dir.is_absolute():
        return output_dir
    try:
        return output_dir.relative_to(ROOT)
    except ValueError as error:
        raise VerificationError(
            f"output directory is outside repo: {output_dir.as_posix()}"
        ) from error


def normalized_field_name(field_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", field_name.casefold())


FORBIDDEN_NORMALIZED_FIELD_NAMES = {
    normalized_field_name(field_name)
    for field_name in FORBIDDEN_FIELD_NAMES
}


def reject_forbidden_field_names(value: Any,
                                 source_name: str,
                                 path: str = "$") -> None:
    errors: list[str] = []

    def walk(candidate: Any, candidate_path: str) -> None:
        if isinstance(candidate, dict):
            for key, nested in candidate.items():
                nested_path = f"{candidate_path}.{key}"
                if normalized_field_name(
                        str(key)) in FORBIDDEN_NORMALIZED_FIELD_NAMES:
                    errors.append(
                        f"{source_name} contains forbidden field {key} at {nested_path}"
                    )
                walk(nested, nested_path)
            return
        if isinstance(candidate, list):
            for index, nested in enumerate(candidate):
                walk(nested, f"{candidate_path}[{index}]")

    walk(value, path)
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(text):
            errors.append(
                f"{path.as_posix()} contains forbidden marker {label}")
    if errors:
        raise VerificationError("\n".join(errors))


def validate_reference_text(value: str, field: str) -> None:
    if value.startswith("external://") or value.startswith(
            "maintainer://") or value.startswith("owner://"):
        return
    path_part = value.split("#", 1)[0]
    repo_relative_path(path_part, field)


def validate_contract(contract: dict[str, Any]) -> None:
    expected_top_level = {
        "schema_version": "1",
        "id": "phase33_maintainer_decision_inputs_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase33-maintainer-decision-inputs",
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    if require_string_list(contract.get("requirement_ids"),
                           "requirement_ids") != REQUIRED_REQUIREMENT_IDS:
        raise VerificationError(
            "requirement_ids must be DECIDE-01, DECIDE-02, DECIDE-03")
    source_contracts = require_list(contract.get("source_contracts"),
                                    "source_contracts")
    source_ids = [
        require_string(
            require_dict(item, "source_contracts[]").get("id"),
            "source_contracts[].id") for item in source_contracts
    ]
    if source_ids != REQUIRED_SOURCE_CONTRACT_IDS:
        raise VerificationError(
            "source_contracts must list Phase 32, Phase 27, and Phase 28 contracts in order"
        )
    source_inputs = require_dict(contract.get("source_inputs"),
                                 "source_inputs")
    if source_inputs.get(
            "phase32_handoff") != DEFAULT_PHASE32_HANDOFF.as_posix():
        raise VerificationError(
            "source_inputs.phase32_handoff must point to the Phase 32 handoff")
    if source_inputs.get("phase32_canonical_register") != PHASE32_REGISTER_REF:
        raise VerificationError(
            "source_inputs.phase32_canonical_register must point to the Phase 32 register"
        )
    if source_inputs.get("phase32_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError(
            "source_inputs.phase32_lifecycle_id must match Phase 32")
    if source_inputs.get("raw_evidence_consumed") is not False:
        raise VerificationError(
            "source_inputs.raw_evidence_consumed must be false")
    decision_schema = require_dict(contract.get("decision_record_schema"),
                                   "decision_record_schema")
    if require_string_list(decision_schema.get("required_fields"),
                           "decision_record_schema.required_fields"
                           ) != REQUIRED_DECISION_FIELDS:
        raise VerificationError(
            "decision_record_schema.required_fields must match Phase 33 required fields"
        )
    target_schema = require_dict(contract.get("decision_target_schema"),
                                 "decision_target_schema")
    if require_string_list(target_schema.get("required_fields"),
                           "decision_target_schema.required_fields"
                           ) != REQUIRED_DECISION_TARGET_FIELDS:
        raise VerificationError(
            "decision_target_schema.required_fields must match the exact typed target identity"
        )
    if require_string_list(
            target_schema.get("exact_phase32_match_fields"),
            "decision_target_schema.exact_phase32_match_fields"
    ) != REQUIRED_DECISION_TARGET_FIELDS:
        raise VerificationError(
            "decision_target_schema.exact_phase32_match_fields must require the complete typed target identity"
        )
    if target_schema.get(
            "source_row_refs_projection") != "decision_targets[*].row_ref":
        raise VerificationError(
            "decision_target_schema.source_row_refs_projection is invalid")
    if target_schema.get("fallback_matching_allowed") is not False:
        raise VerificationError(
            "decision_target_schema must prohibit fallback matching")
    enums = require_dict(contract.get("enums"), "enums")
    if require_string_list(enums.get("decision_type"),
                           "enums.decision_type") != DECISION_TYPES:
        raise VerificationError(
            "enums.decision_type must match Phase 33 decision axes")
    values = require_dict(enums.get("decision_value"), "enums.decision_value")
    for decision_type, expected_values in DECISION_VALUE_ENUMS.items():
        if require_string_list(
                values.get(decision_type),
                f"enums.decision_value.{decision_type}") != expected_values:
            raise VerificationError(
                f"enums.decision_value.{decision_type} is invalid")
    if set(
            require_string_list(
                contract.get("hard_blocker_problem_kinds"),
                "hard_blocker_problem_kinds")) != HARD_BLOCKER_PROBLEM_KINDS:
        raise VerificationError(
            "hard_blocker_problem_kinds must match Phase 33 fail-closed policy"
        )
    exception_policy = require_dict(contract.get("exception_policy"),
                                    "exception_policy")
    if exception_policy.get(
            "exact_source_row_ref_match") is not True or exception_policy.get(
                "affected_gate_must_match") is not True:
        raise VerificationError(
            "exception_policy must require exact row and gate matching")
    generated_artifacts = require_string_list(
        contract.get("generated_artifacts"), "generated_artifacts")
    if generated_artifacts != GENERATED_ARTIFACTS:
        raise VerificationError(
            "generated_artifacts must list the Phase 33 output bundle exactly")
    markers = require_string_list(contract.get("prohibited_output_markers"),
                                  "prohibited_output_markers")
    if "demotion_allowed" not in markers:
        raise VerificationError(
            "prohibited_output_markers must include demotion_allowed")


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    validate_contract(contract)
    return contract


def load_phase32_handoff(
    root: Path, handoff_arg: str | Path
) -> tuple[Path, dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    handoff_path = path_under(handoff_arg, PHASE32_OUTPUT_ROOT,
                              "--phase32-handoff")
    resolved_under(root, handoff_path, PHASE32_OUTPUT_ROOT,
                   "--phase32-handoff")
    handoff = load_json(root, handoff_path)
    scan_json_payload(handoff, handoff_path)
    if handoff.get("phase_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError(
            f"--phase32-handoff phase_lifecycle_id must be {PHASE32_LIFECYCLE_ID}"
        )
    register_ref = require_string(handoff.get("canonical_register_ref"),
                                  "canonical_register_ref")
    if register_ref != PHASE32_REGISTER_REF:
        raise VerificationError(
            f"canonical_register_ref must be {PHASE32_REGISTER_REF}")
    register_path = path_under(register_ref, PHASE32_OUTPUT_ROOT,
                               "canonical_register_ref")
    resolved_under(root, register_path, PHASE32_OUTPUT_ROOT,
                   "canonical_register_ref")
    register = load_json(root, register_path)
    scan_json_payload(register, register_path)
    if register.get("phase_lifecycle_id") != PHASE32_LIFECYCLE_ID:
        raise VerificationError(
            f"Phase 32 canonical register phase_lifecycle_id must be {PHASE32_LIFECYCLE_ID}"
        )
    row_map: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(
            require_list(register.get("rows"), "Phase 32 register rows")):
        row_dict = require_dict(row, f"Phase 32 register row {index}")
        row_id = require_string(row_dict.get("row_id"),
                                f"Phase 32 register row {index}.row_id")
        if row_id in row_map:
            raise VerificationError(f"duplicate Phase 32 row_id: {row_id}")
        row_map[row_id] = row_dict
    return handoff_path, handoff, row_map, register


def source_ref_row_id(source_ref: str, field: str = "source_row_refs") -> str:
    prefix = f"{PHASE32_REGISTER_REF}#"
    if not source_ref.startswith(prefix):
        raise VerificationError(
            f"{field} must use {prefix}<row_id>: {source_ref}")
    row_id = source_ref[len(prefix):]
    if not row_id or "/" in row_id or ".." in row_id:
        raise VerificationError(
            f"{field} contains malformed row id: {source_ref}")
    return row_id


def validate_source_row_refs(
        decision_id: str, field: str, source_refs: list[str],
        row_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    source_rows: list[dict[str, Any]] = []
    for source_ref in source_refs:
        row_id = source_ref_row_id(source_ref, field)
        maybe_row = row_map.get(row_id)
        if maybe_row is None:
            raise VerificationError(
                f"{decision_id}.{field} references unresolved Phase 32 row: {source_ref}"
            )
        source_rows.append(maybe_row)
    return source_rows


def scan_json_payload(data: Any, path: Path) -> None:
    reject_forbidden_field_names(data, path.as_posix())
    reject_forbidden_text(path, json.dumps(data, sort_keys=True))


def load_maintainer_decisions(
        root: Path, maybe_decisions_path: str | None,
        row_map: dict[str, dict[str,
                                Any]]) -> tuple[list[dict[str, Any]], bool]:
    if maybe_decisions_path is None:
        return [], False
    decisions_path = repo_relative_path(maybe_decisions_path,
                                        "--maintainer-decisions")
    resolved_under(root, decisions_path, Path("."), "--maintainer-decisions")
    data = load_json(root, decisions_path)
    scan_json_payload(data, decisions_path)
    if data.get("schema_version") != "1":
        raise VerificationError(
            "maintainer decisions schema_version must be 1")
    if data.get("phase") != PHASE:
        raise VerificationError(f"maintainer decisions phase must be {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"maintainer decisions phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
        )
    raw_decisions = require_list(data.get("decisions"), "decisions")
    decision_ids: set[str] = set()
    parsed: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, raw_decision in enumerate(raw_decisions):
        try:
            decision = validate_decision(
                require_dict(raw_decision, f"decisions[{index}]"), row_map)
            decision_id = decision["decision_id"]
            if decision_id in decision_ids:
                raise VerificationError(
                    f"duplicate decision_id: {decision_id}")
            decision_ids.add(decision_id)
            parsed.append(decision)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    reject_duplicate_axis_refs(parsed)
    return parsed, True


def reject_duplicate_axis_refs(decisions: list[dict[str, Any]]) -> None:
    seen: dict[tuple[str, str, str], tuple[str, str]] = {}
    for decision in decisions:
        for target in decision["decision_targets"]:
            key = (
                str(target["row_ref"]),
                str(target["decision_axis"]),
                str(target["decision_subject_id"]),
            )
            maybe_previous = seen.get(key)
            if maybe_previous is not None:
                previous_id, previous_value = maybe_previous
                conflict_kind = "conflicts with" if previous_value != decision[
                    "decision_value"] else "duplicates"
                raise VerificationError(
                    f"{decision['decision_id']} {conflict_kind} decision target {key}; "
                    f"already decided by {previous_id}")
            seen[key] = (
                str(decision["decision_id"]),
                str(decision["decision_value"]),
            )
