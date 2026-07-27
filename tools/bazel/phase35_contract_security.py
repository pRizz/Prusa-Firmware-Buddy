from __future__ import annotations


class VerificationError(Exception):

    def __init__(self,
                 message: str,
                 reason_code: str = "source-artifact-malformed") -> None:
        super().__init__(message)
        self.reason_code = (reason_code
                            if reason_code in SAFE_SOURCE_FAILURE_REASONS else
                            "source-artifact-malformed")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def resolve_source_file(root: Path, relative_path: Path) -> Path:
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"source artifact escapes repository root: {relative_path.as_posix()}",
            "unsafe-ref",
        )
    current = root
    for part in relative_path.parts:
        current /= part
        if current.is_symlink():
            raise VerificationError(
                f"source artifact contains a symlink escape: {relative_path.as_posix()}",
                "source-ref-failed",
            )
    try:
        resolved_root = root.resolve(strict=True)
        resolved = (root / relative_path).resolve(strict=True)
    except OSError as error:
        raise VerificationError(
            f"source artifact missing: {relative_path.as_posix()}",
            "source-artifact-missing",
        ) from error
    if resolved_root not in resolved.parents:
        raise VerificationError(
            f"source artifact escapes repository root: {relative_path.as_posix()}",
            "unsafe-ref",
        )
    if not resolved.is_file():
        raise VerificationError(
            f"source artifact missing: {relative_path.as_posix()}",
            "source-artifact-missing",
        )
    return resolved


def load_json(root: Path,
              relative_path: Path,
              field: str | None = None) -> dict[str, Any]:
    full_path = resolve_source_file(root, relative_path)
    try:
        value = json.loads(full_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError) as error:
        raise VerificationError(
            f"source artifact malformed: {relative_path.as_posix()}",
            "source-artifact-malformed",
        ) from error
    if not isinstance(value, dict):
        raise VerificationError(
            f"{field or relative_path.as_posix()} must contain an object")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n",
                    encoding="utf-8")


def string_list(value: Any,
                field: str,
                *,
                allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(f"{field} must contain non-blank strings")
    if not allow_empty and not value:
        raise VerificationError(f"{field} must not be empty")
    return list(value)


def normalized_field(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


FORBIDDEN_NORMALIZED_FIELDS = {
    normalized_field(value)
    for value in FORBIDDEN_FIELDS
}


def validate_exact_fields(value: dict[str, Any], expected_fields: set[str],
                          field: str) -> None:
    if set(value) != expected_fields:
        raise VerificationError(f"{field} field set is not exact")


def decode_ref_component(value: str, field: str) -> str:
    if re.search(r"%(?![0-9a-fA-F]{2})", value):
        raise VerificationError(f"unsafe ref in {field}: malformed encoding",
                                "unsafe-ref")
    try:
        decoded = unquote(value, encoding="utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise VerificationError(
            f"unsafe ref in {field}: malformed encoding",
            "unsafe-ref",
        ) from error
    if "\\" in decoded or any(
            ord(character) < 32 or ord(character) == 127
            for character in decoded):
        raise VerificationError(f"unsafe ref in {field}: decoded control",
                                "unsafe-ref")
    return decoded


def validate_ref(value: str, field: str = "ref") -> None:
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{field} must be a non-blank string",
                                "unsafe-ref")
    if "\\" in value or any(
            ord(character) < 32 or ord(character) == 127
            for character in value):
        raise VerificationError(f"unsafe ref in {field}: {value}",
                                "unsafe-ref")
    if not value.startswith(ALLOWED_REF_PREFIXES):
        raise VerificationError(f"unsafe ref in {field}: {value}",
                                "unsafe-ref")
    if value.startswith(("external://", "maintainer://", "owner://")):
        parsed = urlsplit(value)
        if (parsed.scheme not in {"external", "maintainer", "owner"}
                or not parsed.netloc or parsed.query or "@" in parsed.netloc
                or ":" in parsed.netloc):
            raise VerificationError(f"unsafe ref in {field}: {value}",
                                    "unsafe-ref")
        decoded_netloc = decode_ref_component(parsed.netloc, field)
        decoded_path = decode_ref_component(parsed.path, field)
        if decoded_netloc != parsed.netloc or any(delimiter in decoded_path
                                                  for delimiter in "?#"):
            raise VerificationError(f"unsafe ref in {field}: {value}",
                                    "unsafe-ref")
        if parsed.scheme == "external" and (parsed.netloc not in {
                f"phase{phase}"
                for phase in range(23, 35)
        } or not decoded_path.startswith("/") or decoded_path in {"", "/"}):
            raise VerificationError(f"unsafe ref in {field}: {value}",
                                    "unsafe-ref")
        path_parts = decoded_path[1:].split("/") if decoded_path else []
        if any(part in {"", ".", ".."} for part in path_parts):
            raise VerificationError(f"unsafe ref in {field}: {value}")
        if parsed.fragment:
            decoded_fragment = decode_ref_component(parsed.fragment, field)
            if any(delimiter in decoded_fragment for delimiter in "?#"):
                raise VerificationError(f"unsafe ref in {field}: {value}")
            fragment_parts = decoded_fragment.split("/")
            if any(part in {"", ".", ".."} for part in fragment_parts):
                raise VerificationError(f"unsafe ref in {field}: {value}",
                                        "unsafe-ref")
        elif "#" in value:
            raise VerificationError(f"unsafe ref in {field}: {value}",
                                    "unsafe-ref")
        return
    path_text, separator, fragment = value.partition("#")
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts or "\\" in path_text:
        raise VerificationError(f"unsafe ref in {field}: {value}",
                                "unsafe-ref")
    if separator:
        decoded_fragment = decode_ref_component(fragment, field)
        fragment_parts = decoded_fragment.split("/")
        if any(part in {"", ".", ".."} for part in fragment_parts):
            raise VerificationError(f"unsafe ref in {field}: {value}",
                                    "unsafe-ref")


def scan_security(value: Any,
                  field: str = "$",
                  *,
                  allow_contract_vocabulary: bool = False) -> None:
    errors: list[str] = []

    def walk(candidate: Any, candidate_field: str) -> None:
        if isinstance(candidate, dict):
            for key, nested in candidate.items():
                nested_field = f"{candidate_field}.{key}"
                if normalized_field(str(key)) in FORBIDDEN_NORMALIZED_FIELDS:
                    errors.append(
                        f"secret-tainted field {key} at {nested_field}")
                is_path_ref = key != "owner_ref" and (key.endswith("_ref")
                                                      or key.endswith("_refs"))
                if is_path_ref and isinstance(nested, str) and nested:
                    try:
                        validate_ref(nested, nested_field)
                    except VerificationError as error:
                        errors.append(str(error))
                if is_path_ref and key.endswith("_refs") and isinstance(
                        nested, list):
                    for index, ref in enumerate(nested):
                        try:
                            validate_ref(ref, f"{nested_field}[{index}]")
                        except VerificationError as error:
                            errors.append(str(error))
                walk(nested, nested_field)
        elif isinstance(candidate, list):
            for index, nested in enumerate(candidate):
                walk(nested, f"{candidate_field}[{index}]")
        elif isinstance(candidate, str):
            for pattern in FORBIDDEN_TEXT:
                if pattern.search(candidate):
                    is_policy_value = (
                        ".security.prohibited_text_markers[" in candidate_field
                        or ".prohibited_output_markers[" in candidate_field)
                    if (allow_contract_vocabulary and is_policy_value
                            and candidate in CONTRACT_VOCABULARY):
                        continue
                    errors.append(f"forbidden text at {candidate_field}")

    walk(value, field)
    if errors:
        reason_code = ("secret-tainted" if any(
            "secret-tainted" in error or "forbidden text" in error
            for error in errors) else "unsafe-ref")
        raise VerificationError("\n".join(errors), reason_code)


def repo_relative(value: str | Path, field: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        raise VerificationError(f"{field} must be repo-relative", "unsafe-ref")
    if ".." in path.parts:
        raise VerificationError(f"{field} contains parent traversal",
                                "unsafe-ref")
    return path


def validate_output_path(root: Path, output_arg: str | Path) -> Path:
    output = repo_relative(output_arg, "--output-dir")
    if output != DEFAULT_OUTPUT:
        raise VerificationError(
            f"--output-dir must be {DEFAULT_OUTPUT.as_posix()}")
    current = root
    for part in output.parts:
        current /= part
        if current.is_symlink():
            raise VerificationError("--output-dir contains a symlink escape",
                                    "unsafe-ref")
    if current.exists() and not current.is_dir():
        raise VerificationError("--output-dir is not a normal directory",
                                "unsafe-ref")
    return output


def validate_source_path(root: Path, phase34_arg: str | Path,
                         output: Path) -> Path:
    phase34 = repo_relative(phase34_arg, "--phase34-output-dir")
    if phase34 != DEFAULT_PHASE34_OUTPUT:
        raise VerificationError(
            f"--phase34-output-dir must be {DEFAULT_PHASE34_OUTPUT.as_posix()}",
            "unsafe-ref",
        )
    phase34_resolved = (root / phase34).resolve(strict=False)
    output_resolved = (root / output).resolve(strict=False)
    if (phase34_resolved == output_resolved
            or phase34_resolved in output_resolved.parents
            or output_resolved in phase34_resolved.parents):
        raise VerificationError("input and output roots must not overlap",
                                "unsafe-ref")
    current = root
    for part in phase34.parts:
        current /= part
        if current.is_symlink():
            raise VerificationError(
                "--phase34-output-dir contains a symlink escape",
                "source-ref-failed",
            )
    return phase34


def validate_paths(root: Path, phase34_arg: str | Path,
                   output_arg: str | Path) -> tuple[Path, Path]:
    output = validate_output_path(root, output_arg)
    phase34 = validate_source_path(root, phase34_arg, output)
    return phase34, output


def validate_contract(contract: dict[str, Any]) -> None:
    validate_exact_fields(contract, PHASE35_CONTRACT_FIELDS,
                          CONTRACT_PATH.as_posix())
    expected = {
        "schema_version": "1",
        "id": "phase35_cutover_decision_artifact_contract",
        "artifact_name": "phase35-cutover-decision-artifact",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT.as_posix(),
    }
    for field, expected_value in expected.items():
        if contract.get(field) != expected_value:
            raise VerificationError(
                f"{CONTRACT_PATH.as_posix()} {field} must be {expected_value!r}"
            )
    if contract.get("requirement_ids") != REQUIREMENTS:
        raise VerificationError("Phase 35 requirement_ids are invalid")
    if contract.get("generated_artifacts") != GENERATED_ARTIFACTS:
        raise VerificationError("Phase 35 generated_artifacts are invalid")
    expected_guard = {
        "artifact": AUTHORITY_GUARD.as_posix(),
        "required_fields": AUTHORITY_GUARD_FIELDS,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "authority_state": "blocked",
        "safe_reason_code": AUTHORITY_GUARD_REASON,
        "attempted_output_root": DEFAULT_OUTPUT.as_posix(),
    }
    if contract.get("authority_guard") != expected_guard:
        raise VerificationError("Phase 35 authority_guard is invalid")
    schema = contract.get("audit_link_schema")
    if not isinstance(
            schema, dict) or schema.get("kinds") != AUDIT_KINDS or schema.get(
                "required_fields") != AUDIT_FIELDS:
        raise VerificationError("Phase 35 audit link schema is invalid")
    behavior = contract.get("source_failure_behavior")
    if not isinstance(behavior, dict):
        raise VerificationError(
            "Phase 35 source_failure_behavior must be an object")
    expected_behavior = {
        "generated_artifacts": SOURCE_FAILURE_ARTIFACTS,
        "manifest_fields": SOURCE_FAILURE_MANIFEST_FIELDS,
        "decision_fields": DECISION_FIELDS,
        "route_fields": ROUTE_FIELDS,
        "safe_reason_codes": SOURCE_FAILURE_REASON_CODES,
        "generation_state": "blocked-source-error",
        "cutover_verdict": "blocked",
        "route": "targeted-blocker-repair",
        "requires_fresh_cutover_decision": True,
        "planning_only": True,
        "production_actions_authorized": False,
        "raw_evidence_consumed": False,
        "readiness_state": "blocked",
        "readiness_result_ref": "",
        "active_exception_ids": [],
        "blocker_ids": [],
        "audit_link_index_ref": "",
        "audit_link_counts_by_kind": {
            kind: 0
            for kind in AUDIT_KINDS
        },
        "repair_scope": [],
        "repair_scope_reason_code": "route-scope-incomplete",
        "demotion_decision_validation_state": "invalid",
        "demotion_decision_state": "missing",
        "demotion_decision_source_refs": [],
        "demotion_gate_state": "blocked",
    }
    if behavior != expected_behavior:
        raise VerificationError("Phase 35 source_failure_behavior is invalid")


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_PATH)
    validate_contract(contract)
    scan_security(contract,
                  CONTRACT_PATH.as_posix(),
                  allow_contract_vocabulary=True)
    return contract


def validate_phase34_manifest(contract: dict[str, Any],
                              manifest: dict[str, Any]) -> None:
    scan_security(manifest, "Phase 34 manifest")
    validate_exact_fields(manifest, PHASE34_MANIFEST_FIELDS,
                          "Phase 34 manifest")
    register_digests = manifest.get("phase33_register_digests")
    if (not isinstance(register_digests, dict)
            or set(register_digests) != PHASE33_REGISTER_NAMES or not all(
                isinstance(digest, str)
                and re.fullmatch(r"[0-9a-f]{64}", digest)
                for digest in register_digests.values())):
        raise VerificationError(
            "Phase 34 manifest Phase 33 register digests are invalid")
    source = contract.get("source_contract")
    if not isinstance(source, dict):
        raise VerificationError("Phase 35 source_contract must be an object")
    expected = {
        "artifact_name": source["artifact_name"],
        "phase_lifecycle_id": source["phase_lifecycle_id"],
        "output_root": source["output_root"],
        "raw_evidence_consumed": False,
        "generated_artifacts": PHASE34_ARTIFACTS,
    }
    for field, expected_value in expected.items():
        if manifest.get(field) != expected_value:
            reason_code = ("source-artifact-lifecycle-mismatched"
                           if field == "phase_lifecycle_id" else
                           "source-artifact-malformed")
            raise VerificationError(
                f"Phase 34 manifest {field} is stale, malformed, or lifecycle-mismatched",
                reason_code,
            )
    maybe_generated_at = parse_timestamp(manifest.get("generated_at_utc"))
    if maybe_generated_at is None:
        raise VerificationError(
            "Phase 34 manifest generated_at_utc is malformed",
            "source-artifact-malformed",
        )
    if maybe_generated_at < STALE_BEFORE:
        raise VerificationError(
            "Phase 34 manifest generated_at_utc is stale",
            "source-artifact-stale",
        )


def validate_phase34_contract(contract: dict[str, Any]) -> None:
    validate_exact_fields(contract, PHASE34_CONTRACT_FIELDS,
                          PHASE34_CONTRACT_PATH.as_posix())
    expected = {
        "schema_version": "1",
        "id": "phase34_final_readiness_demotion_dry_run_contract",
        "artifact_name": "phase34-final-readiness-demotion-dry-run",
        "phase": "34-final-readiness-and-demotion-dry-run",
        "phase_lifecycle_id": PHASE34_LIFECYCLE_ID,
        "output_root": DEFAULT_PHASE34_OUTPUT.as_posix(),
        "generated_artifacts": PHASE34_ARTIFACTS,
    }
    for field, expected_value in expected.items():
        if contract.get(field) != expected_value:
            raise VerificationError(
                f"{PHASE34_CONTRACT_PATH.as_posix()} {field} is invalid")
    scan_security(
        contract,
        PHASE34_CONTRACT_PATH.as_posix(),
        allow_contract_vocabulary=True,
    )


def validate_snapshot(artifact: str, payload: dict[str, Any]) -> None:
    if artifact.endswith("phase35_cutover_decision_artifact_contract.json"):
        validate_contract(payload)
        scan_security(payload, artifact, allow_contract_vocabulary=True)
        return
    if artifact.endswith(
            "phase34_final_readiness_demotion_dry_run_contract.json"):
        validate_phase34_contract(payload)
        return
    if artifact.endswith("phase34-final-readiness-run-manifest.json"):
        validate_exact_fields(payload, PHASE34_MANIFEST_FIELDS, artifact)
        scan_security(payload, artifact)
        return
    raise VerificationError(f"uncontracted snapshot: {artifact}")
