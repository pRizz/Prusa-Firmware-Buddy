from __future__ import annotations


def normalized_decision_record(decision: dict[str, Any]) -> dict[str, Any]:
    row = {field: decision[field] for field in REQUIRED_DECISION_FIELDS}
    row["phase"] = PHASE
    row["phase_lifecycle_id"] = PHASE_LIFECYCLE_ID
    row["source_row_ids"] = [
        source_ref_row_id(ref) for ref in decision["source_row_refs"]
    ]
    row["affected_gates"] = sorted({
        str(source_row.get("affected_gate", ""))
        for source_row in decision["source_rows"]
        if source_row.get("affected_gate")
    })
    row["decision_axis"] = DECISION_TYPE_AXES[str(decision["decision_type"])]
    return row


def register_decision_record(decision: dict[str, Any]) -> dict[str, Any]:
    row = normalized_decision_record(decision)
    for field in AXIS_SPECIFIC_REGISTER_FIELDS.get(
            str(decision["decision_type"]), []):
        if field in decision:
            row[field] = decision[field]
    return row


def decision_records_by_type(decisions: list[dict[str, Any]],
                             decision_type: str) -> list[dict[str, Any]]:
    return [
        register_decision_record(decision) for decision in decisions
        if decision["decision_type"] == decision_type
    ]


def exception_register_rows(
        decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for decision in decisions:
        if decision["decision_type"] != "exception":
            continue
        row = register_decision_record(decision)
        row["coverage_state"] = "approved-exception" if decision[
            "decision_value"] == "approve" else "rejected"
        rows.append(row)
    return rows


def approved_exception_covered_refs(
        decisions: list[dict[str, Any]]) -> set[str]:
    refs: set[str] = set()
    for decision in decisions:
        if decision["decision_type"] == "exception" and decision[
                "decision_value"] == "approve":
            refs.update(decision["source_row_refs"])
    return refs


def accepted_residual_risk_covered_refs(
        decisions: list[dict[str, Any]]) -> set[str]:
    refs: set[str] = set()
    for decision in decisions:
        if decision["decision_type"] == "residual_risk" and decision[
                "decision_value"] == "accept":
            refs.update(decision["source_row_refs"])
    return refs


def accepted_retained_code_covered_refs(
        decisions: list[dict[str, Any]]) -> set[str]:
    refs: set[str] = set()
    for decision in decisions:
        if decision["decision_type"] == "retained_code" and decision[
                "decision_value"] in {"accept", "exception_approve"}:
            refs.update(decision["source_row_refs"])
    return refs


def readiness_uncovered_blocker_refs(row_map: dict[str, dict[str, Any]],
                                     covered_refs: set[str]) -> list[str]:
    uncovered = []
    for row_id, row in row_map.items():
        row_ref = f"{PHASE32_REGISTER_REF}#{row_id}"
        if row_ref in covered_refs:
            continue
        if row.get("severity") == "critical" or row.get(
                "row_problem_kind") in HARD_BLOCKER_PROBLEM_KINDS:
            uncovered.append(row_ref)
    return sorted(uncovered)


def readiness_handoff(decisions: list[dict[str, Any]],
                      row_map: dict[str, dict[str, Any]],
                      maintainer_input_supplied: bool) -> dict[str, Any]:
    maybe_latest = latest_decision(decisions, "readiness")
    if maybe_latest is None:
        return {
            "phase":
            PHASE,
            "phase_lifecycle_id":
            PHASE_LIFECYCLE_ID,
            "handoff_state":
            "blocked-pending-maintainer-input",
            "readiness_input_supplied":
            False,
            "blocked_source_row_refs": [],
            "rationale":
            "No explicit Phase 33 readiness decision input was supplied.",
        }
    latest = maybe_latest
    if latest["decision_value"] == "approve":
        covered = (approved_exception_covered_refs(decisions)
                   | accepted_residual_risk_covered_refs(decisions)
                   | accepted_retained_code_covered_refs(decisions))
        uncovered = readiness_uncovered_blocker_refs(row_map, covered)
        if uncovered:
            raise VerificationError(
                "readiness approval has uncovered critical blocker or hard blocker rows: "
                + ", ".join(uncovered))
        return {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "handoff_state": "approval-input-recorded",
            "readiness_input_supplied": maintainer_input_supplied,
            "decision_id": latest["decision_id"],
            "source_row_refs": latest["source_row_refs"],
            "phase34_must_generate_final_readiness": True,
            "rationale": latest["rationale"],
        }
    blocked_refs = latest.get("blocked_source_row_refs",
                              latest["source_row_refs"])
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "handoff_state": "blocked-by-maintainer-input",
        "readiness_input_supplied": maintainer_input_supplied,
        "decision_id": latest["decision_id"],
        "blocked_source_row_refs": blocked_refs,
        "rationale": latest["rationale"],
    }


def demotion_handoff(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    maybe_latest = latest_decision(decisions, "reference_demotion")
    if maybe_latest is None:
        return {
            "phase":
            PHASE,
            "phase_lifecycle_id":
            PHASE_LIFECYCLE_ID,
            "authorization_state":
            "blocked",
            "demotion_input_supplied":
            False,
            "phase34_must_validate_readiness":
            True,
            "rationale":
            "Reference demotion requires a separate explicit Phase 33 decision input.",
        }
    latest = maybe_latest
    if latest["decision_value"] == "approve":
        return {
            "phase": PHASE,
            "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
            "authorization_state": "approved-input-recorded",
            "demotion_input_supplied": True,
            "decision_id": latest["decision_id"],
            "source_row_refs": latest["source_row_refs"],
            "maintainer_identity_ref": latest["maintainer_identity_ref"],
            "maintainer_role": latest["maintainer_role"],
            "decision_timestamp": latest["decision_timestamp"],
            "phase34_must_validate_readiness": True,
            "rationale": latest["rationale"],
        }
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "authorization_state": "rejected",
        "demotion_input_supplied": True,
        "decision_id": latest["decision_id"],
        "source_row_refs": latest["source_row_refs"],
        "phase34_must_validate_readiness": True,
        "rationale": latest["rationale"],
    }


def latest_decision(decisions: list[dict[str, Any]],
                    decision_type: str) -> dict[str, Any] | None:
    matching = [
        decision for decision in decisions
        if decision["decision_type"] == decision_type
    ]
    if not matching:
        return None
    return max(
        matching,
        key=lambda decision: datetime.fromisoformat(
            str(decision["decision_timestamp"]).replace("Z", "+00:00")),
    )


def maintainer_input_template(
        row_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    maybe_target: dict[str, str] | None = None
    if row_map:
        first_row_id = next(iter(sorted(row_map)))
        first_row = row_map[first_row_id]
        maybe_target = {
            "row_ref":
            f"{PHASE32_REGISTER_REF}#{first_row_id}",
            "decision_axis":
            require_string(
                first_row.get("decision_axis"),
                f"Phase 32 row {first_row_id}.decision_axis",
            ),
            "decision_subject_id":
            require_string(
                first_row.get("decision_subject_id"),
                f"Phase 32 row {first_row_id}.decision_subject_id",
            ),
        }
    return {
        "schema_version":
        "1",
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "decisions": [{
            "decision_id":
            "phase33-example-decision",
            "decision_type":
            "readiness",
            "decision_value":
            "block",
            "decision_targets": [maybe_target] if maybe_target else [],
            "source_row_refs":
            [maybe_target["row_ref"]] if maybe_target else [],
            "maintainer_identity_ref":
            "maintainer://name-or-group",
            "maintainer_role":
            "cutover-maintainer",
            "owner_signoff_ref":
            "owner://signoff/ref",
            "decision_timestamp":
            "2026-07-04T00:00:00Z",
            "rationale":
            "Explicit maintainer rationale goes here.",
            "evidence_refs": [],
            "artifact_refs": [],
        }],
    }


def validation_report(decisions: list[dict[str, Any]],
                      maintainer_input_supplied: bool) -> dict[str, Any]:
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "maintainer_input_supplied": maintainer_input_supplied,
        "decision_count": len(decisions),
        "decision_counts_by_type": {
            decision_type:
            sum(1 for decision in decisions
                if decision["decision_type"] == decision_type)
            for decision_type in DECISION_TYPES
        },
        "validation_state": "passed",
    }


def redacted_report(records: list[dict[str, Any]], readiness: dict[str, Any],
                    demotion: dict[str, Any]) -> str:
    lines = [
        "# Phase 33 Maintainer Decision Input Report",
        "",
        "Machine-readable JSON records are authoritative. This report summarizes explicit decision inputs only.",
        "",
        f"phase: {PHASE}",
        f"phase_lifecycle_id: {PHASE_LIFECYCLE_ID}",
        f"decision_count: {len(records)}",
        f"readiness_handoff_state: {readiness['handoff_state']}",
        f"reference_demotion_authorization_state: {demotion['authorization_state']}",
        "",
        "| Decision ID | Type | Value | Source Rows |",
        "| ----------- | ---- | ----- | ----------- |",
    ]
    for record in records:
        lines.append("| " + " | ".join([
            markdown_table_cell(record["decision_id"]),
            markdown_table_cell(record["decision_type"]),
            markdown_table_cell(record["decision_value"]),
            str(len(record["source_row_refs"])),
        ]) + " |")
    return "\n".join(lines) + "\n"


def markdown_table_cell(value: object) -> str:
    text = " ".join(str(value).splitlines())
    return html.escape(text, quote=False).replace("|", r"\|")


def copy_contract_snapshots(root: Path, output_dir: Path,
                            phase32_handoff_path: Path,
                            phase32_register: dict[str, Any],
                            phase32_register_ref: str) -> list[str]:
    snapshot_dir = output_dir / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    refs: list[str] = []
    for snapshot_name, source in SOURCE_CONTRACT_SNAPSHOTS.items():
        source_path = root / source
        if not source_path.exists():
            raise VerificationError(
                f"missing snapshot source: {source.as_posix()}")
        destination = snapshot_dir / snapshot_name
        shutil.copy2(source_path, destination)
        refs.append((output_dir.relative_to(root) / "contract-snapshots" /
                     snapshot_name).as_posix())
    shutil.copy2(root / phase32_handoff_path,
                 snapshot_dir / "phase32-downstream-handoff-manifest.json")
    write_json(snapshot_dir / "phase32-blocker-register.json",
               phase32_register)
    refs.append((output_dir.relative_to(root) /
                 "contract-snapshots/phase32-downstream-handoff-manifest.json"
                 ).as_posix())
    refs.append(
        (output_dir.relative_to(root) /
         "contract-snapshots/phase32-blocker-register.json").as_posix())
    if phase32_register_ref != PHASE32_REGISTER_REF:
        raise VerificationError(
            f"Phase 33 source row refs require canonical Phase 32 register {PHASE32_REGISTER_REF}"
        )
    return refs


def downstream_handoff_manifest(
    output_dir: Path,
    phase32_handoff_ref: Path,
    maintainer_input_supplied: bool,
    snapshot_refs: list[str],
) -> dict[str, Any]:
    relative_output_dir = repo_relative_output_dir(output_dir)
    return {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "artifact_name":
        "phase33-maintainer-decision-inputs",
        "generated_at_utc":
        utc_now(),
        "output_root":
        relative_output_dir.as_posix(),
        "maintainer_input_supplied":
        maintainer_input_supplied,
        "raw_evidence_consumed":
        False,
        "source_inputs": {
            "phase32_handoff_ref": phase32_handoff_ref.as_posix(),
            "phase32_canonical_register_ref": PHASE32_REGISTER_REF,
            "raw_evidence_consumed": False,
        },
        "register_refs": {
            "normalized_decision_records":
            (relative_output_dir /
             "normalized-decision-records.json").as_posix(),
            "retained_code_decision_register":
            (relative_output_dir /
             "retained-code-decision-register.json").as_posix(),
            "residual_risk_decision_register":
            (relative_output_dir /
             "residual-risk-decision-register.json").as_posix(),
            "exception_decision_register":
            (relative_output_dir /
             "exception-decision-register.json").as_posix(),
            "readiness_decision_handoff":
            (relative_output_dir /
             "readiness-decision-handoff.json").as_posix(),
            "demotion_decision_handoff":
            (relative_output_dir /
             "demotion-decision-handoff.json").as_posix(),
            "decision_validation_report":
            (relative_output_dir /
             "decision-validation-report.json").as_posix(),
        },
        "contract_snapshot_refs":
        snapshot_refs,
        "downstream_consumers": [
            "phase34-final-readiness-and-demotion-dry-run",
            "phase35-cutover-decision-artifact",
        ],
    }


def write_phase33_outputs(
    root: Path,
    output_dir_arg: str | Path,
    handoff_path: Path,
    row_map: dict[str, dict[str, Any]],
    phase32_register: dict[str, Any],
    decisions: list[dict[str, Any]],
    maintainer_input_supplied: bool,
) -> None:
    relative_output_dir, full_output_dir = output_dir_path(
        root, output_dir_arg)
    reset_output_root(full_output_dir)
    records = [normalized_decision_record(decision) for decision in decisions]
    readiness = readiness_handoff(decisions, row_map,
                                  maintainer_input_supplied)
    demotion = demotion_handoff(decisions)
    snapshot_refs = copy_contract_snapshots(root, full_output_dir,
                                            handoff_path, phase32_register,
                                            PHASE32_REGISTER_REF)
    write_json(full_output_dir / "maintainer-decision-input-template.json",
               maintainer_input_template(row_map))
    write_json(full_output_dir / "normalized-decision-records.json",
               {"rows": records})
    write_json(full_output_dir / "retained-code-decision-register.json",
               {"rows": decision_records_by_type(decisions, "retained_code")})
    write_json(full_output_dir / "residual-risk-decision-register.json",
               {"rows": decision_records_by_type(decisions, "residual_risk")})
    write_json(full_output_dir / "exception-decision-register.json",
               {"rows": exception_register_rows(decisions)})
    write_json(full_output_dir / "readiness-decision-handoff.json", readiness)
    write_json(full_output_dir / "demotion-decision-handoff.json", demotion)
    write_json(full_output_dir / "decision-validation-report.json",
               validation_report(decisions, maintainer_input_supplied))
    manifest = downstream_handoff_manifest(relative_output_dir, handoff_path,
                                           maintainer_input_supplied,
                                           snapshot_refs)
    write_json(full_output_dir / "downstream-handoff-manifest.json", manifest)
    (full_output_dir / "redacted-maintainer-decision-report.md").write_text(
        redacted_report(records, readiness, demotion), encoding="utf-8")
    run_security_scan(root, output_dir=relative_output_dir)


def run_quick(root: Path, phase32_handoff: str | Path, output_dir: str | Path,
              maybe_decisions_path: str | None) -> None:
    load_contract(root)
    _relative_output_dir, full_output_dir = output_dir_path(root, output_dir)
    reject_decisions_inside_output(root, maybe_decisions_path, full_output_dir)
    handoff_path, _handoff, row_map, phase32_register = load_phase32_handoff(
        root, phase32_handoff)
    decisions, maintainer_input_supplied = load_maintainer_decisions(
        root, maybe_decisions_path, row_map)
    write_phase33_outputs(root, output_dir, handoff_path, row_map,
                          phase32_register, decisions,
                          maintainer_input_supplied)
    print(
        f"Phase 33 maintainer decision inputs quick validation passed; decision_count={len(decisions)}"
    )


def run_security_scan(root: Path,
                      maybe_decisions_path: str | None = None,
                      output_dir: str | Path = DEFAULT_OUTPUT_DIR,
                      *,
                      scan_existing_outputs: bool = True) -> None:
    errors: list[str] = []
    if maybe_decisions_path is not None:
        try:
            decisions_path = repo_relative_path(maybe_decisions_path,
                                                "--maintainer-decisions")
            resolved_under(root, decisions_path, Path("."),
                           "--maintainer-decisions")
            data = load_json(root, decisions_path)
            scan_json_payload(data, decisions_path)
        except VerificationError as error:
            errors.append(str(error))
    if not scan_existing_outputs:
        if errors:
            raise VerificationError("\n".join(errors))
        print("Phase 33 input security scan passed")
        return
    relative_output_dir = path_under(output_dir, DEFAULT_OUTPUT_DIR,
                                     "--output-dir")
    full_output_dir = root / relative_output_dir
    if full_output_dir.exists():
        if full_output_dir.is_symlink() or not full_output_dir.is_dir():
            errors.append(
                f"Phase 33 output root is not a normal directory: {relative_output_dir.as_posix()}"
            )
        else:
            for artifact in EMITTED_OUTPUT_SCAN_ARTIFACTS:
                path = full_output_dir / artifact
                if not path.exists() or path.is_dir():
                    continue
                relative_path = path.relative_to(root)
                try:
                    text = path.read_text(encoding="utf-8")
                    reject_forbidden_text(relative_path, text)
                    if path.suffix == ".json":
                        reject_forbidden_field_names(json.loads(text),
                                                     relative_path.as_posix())
                except (json.JSONDecodeError, VerificationError) as error:
                    errors.append(str(error))
    else:
        print(
            f"no Phase 33 outputs to scan at {relative_output_dir.as_posix()}")
    if errors:
        raise VerificationError("\n".join(errors))
    print(
        f"Phase 33 security scan passed for {relative_output_dir.as_posix()}")
