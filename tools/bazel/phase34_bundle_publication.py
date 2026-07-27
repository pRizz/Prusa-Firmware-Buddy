from __future__ import annotations


def reset_output_root(full_output: Path) -> None:
    if full_output.exists():
        if full_output.is_symlink() or not full_output.is_dir():
            raise VerificationError(
                f"--output-dir contains a symlink escape or is not a normal directory: {full_output}"
            )
        shutil.rmtree(full_output)
    full_output.mkdir(parents=True, exist_ok=True)


def source_failure_ledger_row(reason_code: str) -> dict[str, Any]:
    return {
        "row_id":
        f"phase34-source-failure-{reason_code}",
        "ledger_row_kind":
        "evidence",
        "source_domain":
        "source-validation",
        "producer_phase":
        "phase34",
        "producer_artifact_kind":
        "blocked-source-failure",
        "source_row_kind":
        "safe-source-failure",
        "source_subject_id":
        reason_code,
        "decision_axis":
        "",
        "decision_subject_id":
        "",
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "source_stream":
        "source-validation",
        "source_ref":
        f"external://phase34/source-failure/{reason_code}",
        "requirement_ids":
        REQUIRED_REQUIREMENT_IDS,
        "affected_gates": [
            "final-readiness",
            "cutover-decision",
            "production-cutover-route",
            "final-reference-demotion-allowed",
        ],
        "proof_eligibility":
        "ineligible",
        "evidence_status":
        "invalid",
        "row_problem_kind":
        "source_validation_failed",
        "blocker_kind":
        "source_failure",
        "severity":
        "critical",
        "evidence_refs": [],
        "artifact_refs": [],
        "classification_ref":
        "",
        "retained_code_decision_refs": [],
        "residual_risk_decision_refs": [],
        "exception_decision_refs": [],
        "readiness_decision_refs": [],
        "demotion_decision_refs": [],
        "coverage_state":
        "blocked-source-failure",
        "readiness_effect":
        "blocked",
        "reason_codes": [reason_code],
    }


def write_safe_source_failure_snapshots(
    root: Path,
    output_dir: Path,
    reason_code: str,
) -> list[str]:
    snapshot_dir = output_dir / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        root / CONTRACT_MANIFEST,
        snapshot_dir / CONTRACT_MANIFEST.name,
    )
    shutil.copy2(
        root / PHASE33_CONTRACT,
        snapshot_dir / PHASE33_CONTRACT.name,
    )
    safe_snapshot = {
        "snapshot_state": "unavailable-source-failure",
        "source_failure_reason_code": reason_code,
        "raw_evidence_consumed": False,
    }
    write_json(
        snapshot_dir / "phase33-downstream-handoff-manifest.json",
        safe_snapshot,
    )
    write_json(
        snapshot_dir / "phase32-blocker-register.json",
        {
            **safe_snapshot, "rows": []
        },
    )
    write_json(
        snapshot_dir / "phase31-final-intake-manifest.json",
        safe_snapshot,
    )
    write_json(
        snapshot_dir / "phase31-accepted-receipts.json",
        {
            **safe_snapshot, "receipts": []
        },
    )
    return [
        artifact for artifact in GENERATED_ARTIFACTS
        if artifact.startswith("contract-snapshots/")
    ]


def write_source_failure_bundle(
    root: Path,
    relative_output: Path,
    staging_output: Path,
    reason_code: str,
    approval_validation_state: str,
    attempt_id: str,
) -> None:
    reset_output_root(staging_output)
    snapshot_refs = write_safe_source_failure_snapshots(
        root,
        staging_output,
        reason_code,
    )
    ledger_rows = [source_failure_ledger_row(reason_code)]
    demotion = evaluate_demotion(
        "blocked",
        approval_validation_state,
        "missing",
        [],
    )
    demotion["source_failure_reason_code"] = reason_code
    packet = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_ids": REQUIRED_REQUIREMENT_IDS,
        "readiness_state": "blocked",
        "cutover_verdict_state": "blocked",
        "production_cutover_route_state": "blocked",
        "reason_codes": [reason_code],
        "ledger_rows": ledger_rows,
        "demotion_dry_run": demotion,
        "raw_evidence_consumed": False,
    }
    blocker_summary = {
        "readiness_state": "blocked",
        "reason_codes": [reason_code],
        "blocker_count": 1,
        "blockers": ledger_rows,
    }
    run_manifest = {
        "artifact_name":
        "phase34-final-readiness-demotion-dry-run",
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "generated_at_utc":
        utc_now(),
        "output_root":
        relative_output.as_posix(),
        "run_state":
        "blocked-source-failure",
        "attempt_id":
        attempt_id,
        "source_failure_reason_code":
        reason_code,
        "readiness_state":
        "blocked",
        "cutover_verdict_state":
        "blocked",
        "production_cutover_route_state":
        "blocked",
        "demotion_gate_state":
        "blocked",
        "generated_artifacts":
        GENERATED_ARTIFACTS,
        "snapshot_refs": [(relative_output / artifact).as_posix()
                          for artifact in snapshot_refs],
        "source_refs": [],
        "phase33_register_digests": {},
        "raw_evidence_consumed":
        False,
    }
    ledger = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "canonical": True,
        "rows": ledger_rows,
    }
    write_json(
        staging_output / "final-readiness-run-manifest.json",
        run_manifest,
    )
    write_json(
        staging_output / "readiness-coverage-ledger.json",
        ledger,
    )
    write_json(
        staging_output / "final-readiness-packet.json",
        packet,
    )
    write_json(
        staging_output / "readiness-blocker-summary.json",
        blocker_summary,
    )
    write_json(staging_output / "demotion-dry-run.json", demotion)
    (staging_output / "redacted-readiness-report.md").write_text(
        report_text(packet, ledger_rows),
        encoding="utf-8",
    )
    validate_generated_outputs(staging_output)
    validate_output_security(
        staging_output,
        relative_output.as_posix(),
    )


def replace_output_with_staging(
    full_output: Path,
    staging_output: Path,
) -> None:
    backup_output = full_output.with_name(
        f".{full_output.name}.source-failure-backup")
    if backup_output.exists():
        if backup_output.is_symlink() or not backup_output.is_dir():
            raise VerificationError(
                "Phase 34 source-failure backup is not a normal directory")
        shutil.rmtree(backup_output)
    moved_prior = False
    if full_output.exists():
        if full_output.is_symlink() or not full_output.is_dir():
            raise VerificationError(
                "Phase 34 canonical output is not a normal directory")
        full_output.rename(backup_output)
        moved_prior = True
    try:
        staging_output.rename(full_output)
    except OSError as error:
        if moved_prior and backup_output.is_dir() and not full_output.exists():
            backup_output.rename(full_output)
        raise VerificationError(
            "Phase 34 blocked source-failure bundle installation failed"
        ) from error
    if moved_prior and backup_output.exists():
        shutil.rmtree(backup_output)


def publish_source_failure_bundle(
    root: Path,
    relative_output: Path,
    full_output: Path,
    reason_code: str,
    approval_validation_state: str = "invalid",
    attempt_id: str | None = None,
) -> None:
    effective_attempt_id = attempt_id or uuid.uuid4().hex
    publish_publication_state(
        root,
        effective_attempt_id,
        reason_code,
    )
    staging_output = full_output.with_name(
        f".{full_output.name}.source-failure-staging")
    write_source_failure_bundle(
        root,
        relative_output,
        staging_output,
        reason_code,
        approval_validation_state,
        effective_attempt_id,
    )
    replace_output_with_staging(full_output, staging_output)
    validate_generated_outputs(full_output)
    validate_output_security(
        full_output,
        relative_output.as_posix(),
    )
    clear_publication_state(root, effective_attempt_id)


def copy_snapshots(
    root: Path,
    output_dir: Path,
    phase31_manifest_path: Path,
    phase31_manifest: dict[str, Any],
    accepted_receipt_rows: list[str],
    phase33_handoff_path: Path,
    phase33_handoff: dict[str, Any],
    phase32_register: dict[str, Any],
) -> list[str]:
    snapshot_dir = output_dir / "contract-snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / CONTRACT_MANIFEST,
                 snapshot_dir / CONTRACT_MANIFEST.name)
    shutil.copy2(root / PHASE33_CONTRACT, snapshot_dir / PHASE33_CONTRACT.name)
    write_json(snapshot_dir / "phase33-downstream-handoff-manifest.json",
               phase33_handoff)
    write_json(snapshot_dir / "phase32-blocker-register.json",
               phase32_register)
    write_json(snapshot_dir / "phase31-final-intake-manifest.json",
               phase31_manifest)
    accepted = [json.loads(value) for value in sorted(accepted_receipt_rows)]
    write_json(snapshot_dir / "phase31-accepted-receipts.json",
               {"receipts": accepted})
    if phase31_manifest_path.name != "final-intake-manifest.json" or phase33_handoff_path.name != "downstream-handoff-manifest.json":
        raise VerificationError("source manifest filenames are not canonical")
    relative_output = output_dir.relative_to(root)
    return [(relative_output / artifact).as_posix()
            for artifact in GENERATED_ARTIFACTS
            if artifact.startswith("contract-snapshots/")]


def report_text(packet: dict[str, Any], ledger: list[dict[str, Any]]) -> str:
    lines = [
        "# Phase 34 Final Readiness and Demotion Dry Run",
        "",
        "Machine-readable JSON is authoritative. This redacted report is derived from the canonical coverage ledger.",
        "",
        f"readiness_state: {packet['readiness_state']}",
        f"gate_state: {packet['demotion_dry_run']['gate_state']}",
        f"reason_codes: {', '.join(packet['reason_codes']) or 'none'}",
        "",
        "| Row | Kind | Producer | Source kind | Decision axis | Decision subject | Stream | Coverage | Readiness | Reasons |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in ledger:
        values = [
            row["row_id"],
            row["ledger_row_kind"],
            row["producer_phase"],
            row["source_row_kind"],
            row["decision_axis"] or "none",
            row["decision_subject_id"] or "none",
            row["source_stream"],
            row["coverage_state"],
            row["readiness_effect"],
            ", ".join(row["reason_codes"]) or "none",
        ]
        lines.append("| " + " | ".join(
            html.escape(str(value), quote=False).replace("|", r"\|")
            for value in values) + " |")
    return "\n".join(lines) + "\n"


def write_bundle(
    root: Path,
    relative_output: Path,
    full_output: Path,
    manifest_path: Path,
    manifest: dict[str, Any],
    accepted_receipt_rows: list[str],
    handoff_path: Path,
    handoff: dict[str, Any],
    blocker_register: dict[str, Any],
    ledger: list[dict[str, Any]],
    readiness: str,
    readiness_reasons: list[str],
    demotion: dict[str, Any],
    register_digests: dict[str, str],
) -> None:
    reset_output_root(full_output)
    snapshot_refs = copy_snapshots(
        root,
        full_output,
        manifest_path,
        manifest,
        accepted_receipt_rows,
        handoff_path,
        handoff,
        blocker_register,
    )
    reason_codes = sorted(
        set(readiness_reasons) | set(demotion["reason_codes"]))
    ledger_payload = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "canonical": True,
        "rows": ledger,
    }
    packet = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_ids": REQUIRED_REQUIREMENT_IDS,
        "readiness_state": readiness,
        "reason_codes": reason_codes,
        "ledger_rows": ledger,
        "demotion_dry_run": demotion,
        "raw_evidence_consumed": False,
    }
    blockers = [row for row in ledger if row["readiness_effect"] == "blocked"]
    blocker_summary = {
        "readiness_state": readiness,
        "reason_codes": reason_codes,
        "blocker_count": len(blockers),
        "blockers": blockers,
    }
    run_manifest = {
        "artifact_name":
        "phase34-final-readiness-demotion-dry-run",
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "generated_at_utc":
        utc_now(),
        "output_root":
        relative_output.as_posix(),
        "generated_artifacts":
        GENERATED_ARTIFACTS,
        "snapshot_refs":
        snapshot_refs,
        "source_refs": [manifest_path.as_posix(),
                        handoff_path.as_posix()],
        "accepted_receipt_snapshot_ref":
        (relative_output /
         "contract-snapshots/phase31-accepted-receipts.json").as_posix(),
        "phase33_register_digests":
        register_digests,
        "raw_evidence_consumed":
        False,
    }
    write_json(full_output / "final-readiness-run-manifest.json", run_manifest)
    write_json(full_output / "readiness-coverage-ledger.json", ledger_payload)
    write_json(full_output / "final-readiness-packet.json", packet)
    write_json(full_output / "readiness-blocker-summary.json", blocker_summary)
    write_json(full_output / "demotion-dry-run.json", demotion)
    (full_output / "redacted-readiness-report.md").write_text(report_text(
        packet, ledger),
                                                              encoding="utf-8")
    validate_generated_outputs(full_output)


def validate_generated_outputs(output_dir: Path) -> None:
    for artifact in GENERATED_ARTIFACTS:
        if not (output_dir / artifact).is_file():
            raise VerificationError(
                f"generated artifact is missing: {artifact}")
    ledger = json.loads(
        (output_dir /
         "readiness-coverage-ledger.json").read_text(encoding="utf-8"))
    packet = json.loads(
        (output_dir /
         "final-readiness-packet.json").read_text(encoding="utf-8"))
    blockers = json.loads(
        (output_dir /
         "readiness-blocker-summary.json").read_text(encoding="utf-8"))
    demotion = json.loads(
        (output_dir / "demotion-dry-run.json").read_text(encoding="utf-8"))
    report = (output_dir /
              "redacted-readiness-report.md").read_text(encoding="utf-8")
    for index, row in enumerate(ledger.get("rows", [])):
        missing_fields = [field for field in LEDGER_FIELDS if field not in row]
        if missing_fields:
            raise VerificationError(
                f"ledger row {index} missing required fields: "
                f"{', '.join(missing_fields)}")
    if packet.get("ledger_rows") != ledger.get("rows"):
        raise VerificationError("packet and canonical ledger rows differ")
    expected_blockers = [
        row for row in ledger.get("rows", [])
        if row.get("readiness_effect") == "blocked"
    ]
    if blockers.get("blockers") != expected_blockers:
        raise VerificationError(
            "blocker summary is not derived from the canonical ledger")
    if packet.get("demotion_dry_run") != demotion:
        raise VerificationError("packet and demotion dry-run differ")
    if f"readiness_state: {packet.get('readiness_state')}" not in report or f"gate_state: {demotion.get('gate_state')}" not in report:
        raise VerificationError(
            "redacted report is not derived from packet state")


def run_quick(
    root: Path,
    phase31_output: str,
    phase33_handoff: str,
    output_arg: str,
    attempt_id: str | None = None,
) -> str | None:
    load_contract(root)
    relative_output, full_output = output_paths(root, output_arg)
    reason_code = SOURCE_FAILURE_REASON_CODES[1]
    try:
        raw_handoff_path = repo_relative_path(
            phase33_handoff,
            "--phase33-handoff",
        )
        resolved_handoff = (root / raw_handoff_path).resolve(strict=False)
        if (resolved_handoff == full_output
                or full_output in resolved_handoff.parents):
            raise VerificationError(
                "--phase33-handoff must be outside the generated --output-dir")
        path_under(
            raw_handoff_path,
            PHASE33_OUTPUT_ROOT,
            "--phase33-handoff",
        )

        reason_code = SOURCE_FAILURE_REASON_CODES[0]
        required_streams = load_phase31_required_streams(root)
        manifest_path, manifest, receipts, accepted_receipt_rows = load_phase31(
            root,
            phase31_output,
        )

        reason_code = SOURCE_FAILURE_REASON_CODES[1]
        handoff_path, handoff, register_refs = load_phase33_handoff(
            root,
            phase33_handoff,
            full_output,
        )

        reason_code = SOURCE_FAILURE_REASON_CODES[2]
        normalized = load_phase33_register(
            root,
            register_refs,
            "normalized_decision_records",
        )
        raw_decisions = require_list(
            normalized.get("rows"),
            "normalized decision rows",
        )
        if not all(isinstance(row, dict) for row in raw_decisions):
            raise VerificationError(
                "normalized decision rows must contain objects")
        decisions = [dict(row) for row in raw_decisions]
        decisions_by_id = validate_normalized_decisions(decisions)

        reason_code = SOURCE_FAILURE_REASON_CODES[3]
        readiness_input = load_phase33_register(
            root,
            register_refs,
            "readiness_decision_handoff",
        )
        validate_readiness_handoff(readiness_input, decisions_by_id)

        reason_code = SOURCE_FAILURE_REASON_CODES[5]
        blocker_register = load_phase32_blocker_register(root)
        blocker_rows = require_list(
            blocker_register.get("rows"),
            "Phase 32 blocker rows",
        )
        if not all(isinstance(row, dict) for row in blocker_rows):
            raise VerificationError(
                "Phase 32 blocker rows must contain objects")

        reason_code = SOURCE_FAILURE_REASON_CODES[6]
        demotion_input = load_phase33_register(root, register_refs,
                                               "demotion_decision_handoff")
        validation, decision, source_refs = validate_demotion_handoff(
            demotion_input,
            decisions_by_id,
        )

        reason_code = SOURCE_FAILURE_REASON_CODES[4]
        register_digests = phase33_register_digests(root, register_refs)
    except VerificationError as error:
        approval_validation_state = (
            "missing" if reason_code == "phase33-demotion-input-invalid"
            and str(error).startswith("missing required file:") else "invalid")
        publish_source_failure_bundle(
            root,
            relative_output,
            full_output,
            reason_code,
            approval_validation_state,
            attempt_id,
        )
        return reason_code
    ledger = evaluate_coverage(receipts, blocker_rows, decisions,
                               required_streams)
    readiness, readiness_reasons, maybe_readiness_error = readiness_state(
        ledger,
        readiness_input,
        decisions_by_id,
    )
    demotion = evaluate_demotion(readiness, validation, decision, source_refs)
    write_bundle(
        root,
        relative_output,
        full_output,
        manifest_path,
        manifest,
        accepted_receipt_rows,
        handoff_path,
        handoff,
        blocker_register,
        ledger,
        readiness,
        readiness_reasons,
        demotion,
        register_digests,
    )
    run_security_scan(root, relative_output)
    return maybe_readiness_error
