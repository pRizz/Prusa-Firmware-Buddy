from __future__ import annotations


def load_json(root: Path,
              relative_path: Path,
              field: str | None = None) -> dict[str, Any]:
    full_path = root / relative_path
    if not full_path.is_file():
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    try:
        value = json.loads(full_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError) as error:
        raise VerificationError(
            f"{field or relative_path.as_posix()} is unreadable or invalid JSON"
        ) from error
    if not isinstance(value, dict):
        raise VerificationError(
            f"{field or relative_path.as_posix()} must contain a top-level object"
        )
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError(f"{field} must be a list")
    return value


def string_list(value: Any, field: str) -> list[str]:
    values = require_list(value, field)
    if not all(isinstance(item, str) and item.strip() for item in values):
        raise VerificationError(f"{field} must contain non-blank strings")
    return values


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VerificationError(f"{field} must be a non-blank string")
    return value


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


def normalized_field_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


FORBIDDEN_NORMALIZED_FIELDS = {
    normalized_field_name(value)
    for value in FORBIDDEN_FIELD_NAMES
}


def reject_forbidden_fields(value: Any,
                            source: str,
                            candidate_path: str = "$") -> None:
    errors: list[str] = []

    def walk(candidate: Any, current_path: str) -> None:
        if isinstance(candidate, dict):
            for key, nested in candidate.items():
                nested_path = f"{current_path}.{key}"
                if normalized_field_name(
                        str(key)) in FORBIDDEN_NORMALIZED_FIELDS:
                    errors.append(
                        f"{source} contains forbidden field {key} at {nested_path}"
                    )
                walk(nested, nested_path)
        elif isinstance(candidate, list):
            for index, nested in enumerate(candidate):
                walk(nested, f"{current_path}[{index}]")

    walk(value, candidate_path)
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_text(relative_path: Path, text: str) -> None:
    errors = [
        f"{relative_path.as_posix()} contains forbidden marker {label}"
        for label, pattern in FORBIDDEN_TEXT_PATTERNS if pattern.search(text)
    ]
    if errors:
        raise VerificationError("\n".join(errors))


def scan_json(value: dict[str, Any], source: Path) -> None:
    reject_forbidden_fields(value, source.as_posix())
    reject_forbidden_text(source, json.dumps(value, sort_keys=True))
    validate_refs(value, source.as_posix())


def repo_relative_path(value: str | Path, field: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        raise VerificationError(
            f"{field} must be repo-relative: {candidate.as_posix()}")
    if ".." in candidate.parts:
        raise VerificationError(
            f"{field} contains parent traversal: {candidate.as_posix()}")
    return candidate


def path_under(value: str | Path, expected_root: Path, field: str) -> Path:
    candidate = repo_relative_path(value, field)
    try:
        candidate.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{field} must be under {expected_root.as_posix()}: {candidate.as_posix()}"
        ) from error
    return candidate


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
    expected = (root / expected_root).resolve(strict=False)
    try:
        full_path.relative_to(expected)
    except ValueError as error:
        raise VerificationError(
            f"{field} resolves outside {expected_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return full_path


def output_paths(root: Path, output_arg: str | Path) -> tuple[Path, Path]:
    relative_output = path_under(output_arg, DEFAULT_OUTPUT_DIR,
                                 "--output-dir")
    full_output = resolved_under(root, relative_output, DEFAULT_OUTPUT_DIR,
                                 "--output-dir")
    return relative_output, full_output


def validate_refs(value: Any, field: str) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("_ref") and isinstance(nested, str) and nested:
                validate_ref(nested, f"{field}.{key}")
            elif key.endswith("_refs") and isinstance(nested, list):
                for index, ref in enumerate(nested):
                    if not isinstance(ref, str):
                        raise VerificationError(
                            f"{field}.{key}[{index}] must be a string")
                    validate_ref(ref, f"{field}.{key}[{index}]")
            else:
                validate_refs(nested, f"{field}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            validate_refs(nested, f"{field}[{index}]")


def validate_ref(value: str, field: str) -> None:
    if value.startswith(("external://", "maintainer://", "owner://")):
        return
    repo_relative_path(value.split("#", 1)[0], field)


def validate_contract(contract: dict[str, Any]) -> None:
    expected = {
        "schema_version": "1",
        "id": "phase34_final_readiness_demotion_dry_run_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "artifact_name": "phase34-final-readiness-demotion-dry-run",
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, value in expected.items():
        if contract.get(field) != value:
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {value!r}")
    if string_list(contract.get("requirement_ids"),
                   "requirement_ids") != REQUIRED_REQUIREMENT_IDS:
        raise VerificationError(
            "requirement_ids must be READY-01, READY-02, READY-03")
    ledger_schema = contract.get("ledger_schema")
    if not isinstance(ledger_schema, dict) or string_list(
            ledger_schema.get("required_fields"),
            "ledger fields") != LEDGER_FIELDS:
        raise VerificationError(
            "ledger_schema.required_fields must match the Phase 34 interface")
    if ledger_schema.get("row_kinds") != ["evidence", "decision-domain"]:
        raise VerificationError(
            "ledger_schema.row_kinds must define evidence and decision-domain rows"
        )
    decision_policy = contract.get("decision_domain_policy")
    if not isinstance(decision_policy, dict):
        raise VerificationError("decision_domain_policy must be an object")
    if decision_policy.get(
            "canonical_rows_from"
    ) != "phase32 canonical Phase 27/28 decision-domain rows":
        raise VerificationError(
            "decision-domain rows must come from canonical Phase 32 Phase 27/28 rows"
        )
    if decision_policy.get(
            "evidence_authority") != "phase31 accepted-final receipts only":
        raise VerificationError(
            "Phase 31 must remain the sole evidence authority")
    if decision_policy.get("exact_decision_target_fields") != [
            "row_ref",
            "decision_axis",
            "decision_subject_id",
    ]:
        raise VerificationError(
            "decision targets must use the exact typed identity")
    if decision_policy.get(
            "readiness_and_demotion_are_orthogonal") is not True:
        raise VerificationError(
            "readiness and demotion must remain orthogonal")
    if string_list(contract.get("generated_artifacts"),
                   "generated_artifacts") != GENERATED_ARTIFACTS:
        raise VerificationError(
            "generated_artifacts must list the exact Phase 34 bundle")
    source_contracts = require_list(contract.get("source_contracts"),
                                    "source_contracts")
    source_ids = [
        row.get("id") for row in source_contracts if isinstance(row, dict)
    ]
    if source_ids != [
            "phase31_final_evidence_intake_contract",
            "phase32_blocker_register_triage_contract",
            "phase33_maintainer_decision_inputs_contract",
            "phase28_final_readiness_packet_contract",
    ]:
        raise VerificationError(
            "source_contracts must list Phase 31, 32, 33, and precedent-only Phase 28"
        )
    source_inputs = contract.get("source_inputs")
    if not isinstance(source_inputs, dict) or source_inputs.get(
            "raw_evidence_consumed") is not False:
        raise VerificationError(
            "source_inputs.raw_evidence_consumed must be false")
    overlay_policy = contract.get("sparse_blocker_overlay_policy")
    if not isinstance(overlay_policy, dict):
        raise VerificationError(
            "sparse_blocker_overlay_policy must be an object")
    if overlay_policy.get(
            "required_streams_from") != "phase31 contract stream_adapters":
        raise VerificationError(
            "required streams must derive from Phase 31 stream_adapters")
    if overlay_policy.get(
            "absent_required_stream_state") != "required-row-missing":
        raise VerificationError(
            "absent required streams must use required-row-missing")
    open_requires = contract.get("demotion_dry_run_schema",
                                 {}).get("open_requires")
    if open_requires != {
            "readiness_state": "unblocked",
            "approval_validation_state": "valid",
            "approval_decision_state": "approve",
    }:
        raise VerificationError("demotion dry-run open predicate is invalid")
    source_failure_policy = contract.get("source_failure_policy")
    if not isinstance(source_failure_policy, dict):
        raise VerificationError("source_failure_policy must be an object")
    if source_failure_policy.get(
            "reason_codes") != SOURCE_FAILURE_REASON_CODES:
        raise VerificationError(
            "source_failure_policy.reason_codes must list the exact safe vocabulary"
        )
    if (source_failure_policy.get("blocked_authority_fields")
            != SOURCE_FAILURE_AUTHORITY_FIELDS):
        raise VerificationError(
            "source_failure_policy.blocked_authority_fields must block every authority projection"
        )
    if source_failure_policy.get("copies_source_payloads") is not False:
        raise VerificationError(
            "source_failure_policy.copies_source_payloads must be false")


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_MANIFEST)
    validate_contract(contract)
    return contract


def load_phase31_required_streams(root: Path) -> dict[str, dict[str, Any]]:
    contract = load_json(root, PHASE31_CONTRACT)
    if contract.get("id") != "phase31_final_evidence_intake_contract":
        raise VerificationError(
            "Phase 31 contract id must be phase31_final_evidence_intake_contract"
        )
    if contract.get("phase_lifecycle_id") != PHASE31_LIFECYCLE_ID:
        raise VerificationError(
            f"Phase 31 contract phase_lifecycle_id must be {PHASE31_LIFECYCLE_ID}"
        )

    required_streams: dict[str, dict[str, Any]] = {}
    for index, adapter in enumerate(
            require_list(contract.get("stream_adapters"),
                         "Phase 31 stream_adapters")):
        if not isinstance(adapter, dict):
            raise VerificationError(
                f"Phase 31 stream_adapters[{index}] must be an object")
        stream = require_string(adapter.get("stream"),
                                f"Phase 31 stream_adapters[{index}].stream")
        if stream in required_streams:
            raise VerificationError(
                f"duplicate Phase 31 stream adapter: {stream}")
        if stream not in REQUIRED_PHASE31_STREAMS:
            raise VerificationError(
                f"unknown Phase 31 required stream: {stream}")
        output_root = repo_relative_path(
            require_string(adapter.get("output_root"),
                           f"{stream}.output_root"),
            f"{stream}.output_root",
        )
        maybe_upstream_row = adapter.get("upstream_row")
        maybe_upstream_table = adapter.get("upstream_row_table")
        if (isinstance(maybe_upstream_row, str) and
                maybe_upstream_row) == (isinstance(maybe_upstream_table, str)
                                        and maybe_upstream_table):
            raise VerificationError(
                f"{stream} must declare exactly one upstream row or row table")
        upstream_name = maybe_upstream_row if isinstance(
            maybe_upstream_row, str) else maybe_upstream_table
        upstream_path = repo_relative_path(
            require_string(upstream_name, f"{stream}.upstream row"),
            f"{stream}.upstream row",
        )
        expected_source_ref = (output_root / upstream_path).as_posix()
        required_streams[stream] = {
            "stream":
            stream,
            "requirement_ids":
            string_list(adapter.get("requirement_ids"),
                        f"{stream}.requirement_ids"),
            "expected_source_ref":
            expected_source_ref,
            "expected_gate":
            EXPECTED_GATE_BY_STREAM[stream],
        }

    if set(required_streams) != set(REQUIRED_PHASE31_STREAMS):
        missing = sorted(set(REQUIRED_PHASE31_STREAMS) - set(required_streams))
        raise VerificationError(
            f"Phase 31 stream_adapters missing required streams: {', '.join(missing)}"
        )
    return required_streams


def stable_row_id(stream: str, source_ref: str) -> str:
    digest = hashlib.sha256(
        f"{stream}\0{source_ref}".encode()).hexdigest()[:12]
    return f"phase34-{stream}-{digest}"


def receipt_problem_kind(receipt: dict[str, Any]) -> str:
    if receipt.get("redaction_status") != "passed":
        return "redaction_failed"
    if receipt.get("source_ref_status") != "passed":
        return "source_ref_failed"
    if receipt.get("finality_status") != "accepted-final":
        return "non_final_placeholder"
    evidence_status = str(
        receipt.get("evidence_status")
        or ("failed" if receipt.get("failure_reason") else "passed"))
    if evidence_status not in {"passed", "eligible"}:
        return evidence_status
    if receipt.get("exception_status") not in {None, "", "none"}:
        return "exception_requested"
    return ""


def derive_evidence_rows(
    receipts: list[dict[str, Any]],
    required_streams: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_refs: set[str] = set()
    duplicate_refs: set[str] = set()
    for receipt in receipts:
        stream = str(receipt.get("stream") or "unknown")
        consumed_refs = string_list(receipt.get("consumed_upstream_row_refs"),
                                    f"{stream}.consumed_upstream_row_refs")
        for source_ref in consumed_refs:
            if source_ref in seen_refs:
                duplicate_refs.add(source_ref)
            seen_refs.add(source_ref)
            problem_kind = receipt_problem_kind(receipt)
            artifact_summary = receipt.get("artifact_reference_summary")
            artifact_refs = []
            if isinstance(artifact_summary, dict):
                maybe_refs = artifact_summary.get("artifact_refs", [])
                if isinstance(maybe_refs, list):
                    artifact_refs = sorted({
                        str(ref)
                        for ref in maybe_refs if isinstance(ref, str) and ref
                    })
            rows.append({
                "row_id":
                stable_row_id(stream, source_ref),
                "ledger_row_kind":
                "evidence",
                "source_domain":
                "final_evidence_intake",
                "producer_phase":
                "phase31",
                "producer_artifact_kind":
                "phase31_final_intake_receipt",
                "source_row_kind":
                "accepted_final_receipt",
                "source_subject_id":
                str(receipt.get("submission_id") or source_ref),
                "decision_axis":
                "",
                "decision_subject_id":
                "",
                "phase_lifecycle_id":
                PHASE31_LIFECYCLE_ID,
                "source_stream":
                stream,
                "source_ref":
                source_ref,
                "expected_gate":
                EXPECTED_GATE_BY_STREAM.get(
                    stream, EXPECTED_GATE_BY_STREAM["unknown"]),
                "requirement_ids":
                sorted({
                    str(value)
                    for value in receipt.get("requirement_ids", [])
                }),
                "proof_eligibility":
                "ineligible" if problem_kind else "eligible",
                "evidence_status":
                str(
                    receipt.get("evidence_status") or
                    ("failed" if receipt.get("failure_reason") else "passed")),
                "row_problem_kind":
                problem_kind,
                "evidence_refs":
                sorted({
                    source_ref, *[
                        str(ref)
                        for ref in receipt.get("validator_output_refs", [])
                    ]
                }),
                "artifact_refs":
                artifact_refs,
                "duplicate_source_ref":
                source_ref in duplicate_refs,
            })
    present_streams = {row["source_stream"] for row in rows}
    for stream, specification in sorted((required_streams or {}).items()):
        if stream in present_streams:
            continue
        source_ref = str(specification["expected_source_ref"])
        rows.append({
            "row_id":
            stable_row_id(stream, source_ref),
            "ledger_row_kind":
            "evidence",
            "source_domain":
            "final_evidence_intake",
            "producer_phase":
            "phase31",
            "producer_artifact_kind":
            "phase31_required_stream",
            "source_row_kind":
            "missing_required_stream",
            "source_subject_id":
            stream,
            "decision_axis":
            "",
            "decision_subject_id":
            "",
            "phase_lifecycle_id":
            PHASE31_LIFECYCLE_ID,
            "source_stream":
            stream,
            "source_ref":
            source_ref,
            "expected_gate":
            str(specification["expected_gate"]),
            "requirement_ids":
            sorted({str(value)
                    for value in specification["requirement_ids"]}),
            "proof_eligibility":
            "ineligible",
            "evidence_status":
            "missing",
            "row_problem_kind":
            "missing",
            "evidence_refs": [source_ref],
            "artifact_refs": [],
            "duplicate_source_ref":
            False,
        })
    for row in rows:
        row["duplicate_source_ref"] = row["source_ref"] in duplicate_refs
    return sorted(rows,
                  key=lambda row:
                  (row["source_stream"], row["source_ref"], row["row_id"]))


def derive_expected_rows(
    receipts: list[dict[str, Any]],
    required_streams: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Compatibility name for the Phase 31 evidence-row constructor."""
    return derive_evidence_rows(receipts, required_streams)


def decisions_for(
    decisions: list[dict[str, Any]],
    decision_type: str,
    blocker_ref: str,
    affected_gate: str,
) -> list[dict[str, Any]]:
    matches = []
    for decision in decisions:
        if decision.get("decision_type") != decision_type:
            continue
        if blocker_ref not in decision.get("source_row_refs", []):
            continue
        if decision_type in {"exception", "residual_risk"
                             } and affected_gate not in decision.get(
                                 "affected_gates", []):
            continue
        if decision_type == "exception" and blocker_ref not in decision.get(
                "linked_blocker_refs", []):
            continue
        matches.append(decision)
    return sorted(matches, key=lambda row: str(row.get("decision_id", "")))


def decision_refs(rows: list[dict[str, Any]]) -> list[str]:
    return [
        f"build/ci-evidence/phase33/normalized-decision-records.json#{row.get('decision_id')}"
        for row in rows
    ]
