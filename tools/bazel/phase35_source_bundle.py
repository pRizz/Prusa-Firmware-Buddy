from __future__ import annotations


def audit_sources_from_bundle(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []

    def add(kind: str, target_id: str, target_ref: str, lifecycle: str,
            effect: str, digest_source: Any) -> None:
        sources.append({
            "kind": kind,
            "target_id": target_id,
            "target_ref": target_ref,
            "source_phase_lifecycle_id": lifecycle,
            "verdict_effect": effect,
            "digest_source": digest_source,
        })

    for receipt in bundle["receipts"]:
        receipt_value = receipt.get("receipt", receipt)
        add(
            "evidence-packet",
            str(
                receipt_value.get("submission_id")
                or receipt.get("receipt_ref")),
            str(receipt.get("receipt_ref")),
            "31-2026-07-03T02-04-07",
            "supports",
            receipt_value,
        )
    for blocker in bundle["blockers"]:
        add("blocker", str(blocker["row_id"]),
            f"{PHASE32_REGISTER_REF}#{blocker['row_id']}",
            "32-2026-07-03T14-13-51", "blocks", blocker)
    for kind, rows, register in [
        ("exception", bundle["exceptions"], PHASE33_EXCEPTION_REGISTER),
        ("residual-risk", bundle["residuals"], PHASE33_RESIDUAL_REGISTER),
        ("retained-code-decision", bundle["retained"],
         "build/ci-evidence/phase33/retained-code-decision-register.json"),
    ]:
        for row in rows:
            add(kind, str(row["decision_id"]),
                f"{register}#{row['decision_id']}", PHASE33_LIFECYCLE_ID,
                "conditions", row)
    readiness = bundle["readiness_handoff"]
    demotion_handoff = bundle["demotion_handoff"]
    add("readiness-decision", str(readiness.get("decision_id") or "missing"),
        "build/ci-evidence/phase33/readiness-decision-handoff.json",
        PHASE33_LIFECYCLE_ID, "controls-readiness", readiness)
    add("readiness-result", "phase34-final-readiness",
        "build/ci-evidence/phase34/final-readiness-packet.json",
        PHASE34_LIFECYCLE_ID, "controls-verdict", bundle["packet"])
    add("demotion-decision",
        str(demotion_handoff.get("decision_id") or "missing"),
        "build/ci-evidence/phase33/demotion-decision-handoff.json",
        PHASE33_LIFECYCLE_ID, "independent", demotion_handoff)
    add("demotion-dry-run", "phase34-demotion-dry-run",
        "build/ci-evidence/phase34/demotion-dry-run.json",
        PHASE34_LIFECYCLE_ID, "independent", bundle["dry_run"])
    return sources


def reached_register(root: Path, refs: dict[str, Any],
                     expected_digests: dict[str,
                                            str], name: str) -> dict[str, Any]:
    value = refs.get(name)
    if not isinstance(value, str):
        raise VerificationError(f"Phase 33 register ref missing: {name}",
                                "source-ref-failed")
    validate_ref(value, f"register_refs.{name}")
    path = Path(value)
    if not path.as_posix().startswith("build/ci-evidence/phase33/"):
        raise VerificationError(
            f"Phase 33 register ref has wrong root: {value}",
            "source-ref-failed",
        )
    payload = load_json(root, path)
    scan_security(payload, value)
    actual_digest = hashlib.sha256(canonical_json(payload)).hexdigest()
    if actual_digest != expected_digests.get(name):
        raise VerificationError(
            f"Phase 33 register changed after Phase 34 validation: {name}",
            "source-ref-failed",
        )
    return payload


def validate_register_projection(rows: list[dict[str, Any]],
                                 normalized_rows: list[dict[str, Any]],
                                 decision_type: str) -> None:
    allowed_extension_fields = {
        "retained_code": {"residual_risk_rationale"},
        "residual_risk": {"follow_up_refs"},
        "exception": {
            "scope",
            "expiry_or_review_trigger",
            "affected_requirements",
            "affected_gates",
            "linked_blocker_refs",
            "coverage_state",
        },
    }
    forbidden_legacy_fields = {"validation_state", "active", "exact_scope"}
    expected = {
        str(row.get("decision_id")): row
        for row in normalized_rows if row.get("decision_type") == decision_type
    }
    actual = {str(row.get("decision_id")): row for row in rows}
    if len(actual) != len(rows) or set(actual) != set(expected):
        raise VerificationError(
            f"Phase 33 {decision_type} register does not match the normalized decisions"
        )
    for decision_id, normalized in expected.items():
        projection = actual[decision_id]
        if forbidden_legacy_fields & set(projection):
            raise VerificationError(
                f"Phase 33 {decision_type} register contains forbidden legacy validation fields"
            )
        unexpected_fields = (
            set(projection) - set(normalized) -
            allowed_extension_fields.get(decision_type, set()))
        if unexpected_fields:
            raise VerificationError(
                f"Phase 33 {decision_type} register contains uncontracted fields for {decision_id}"
            )
        if any(
                projection.get(field) != value
                for field, value in normalized.items()):
            raise VerificationError(
                f"Phase 33 {decision_type} projection differs for {decision_id}"
            )
        if decision_type != "exception":
            continue
        for field in ("scope", "expiry_or_review_trigger"):
            if not isinstance(projection.get(field),
                              str) or not projection[field]:
                raise VerificationError(
                    f"Phase 33 exception {decision_id} {field} is invalid")
        for field in ("affected_requirements", "affected_gates",
                      "linked_blocker_refs"):
            if not isinstance(projection.get(field), list) or not all(
                    isinstance(value, str) and value
                    for value in projection[field]):
                raise VerificationError(
                    f"Phase 33 exception {decision_id} {field} is invalid")
        if projection["linked_blocker_refs"] != projection.get(
                "source_row_refs"):
            raise VerificationError(
                f"Phase 33 exception {decision_id} scope is not exact")


def active_exception_ids_from_ledger(
        ledger_rows: list[dict[str, Any]]) -> list[str]:
    prefix = "build/ci-evidence/phase33/normalized-decision-records.json#"
    active_ids: set[str] = set()
    for row in ledger_rows:
        if row.get("coverage_state") != "exception-covered":
            continue
        refs = row.get("exception_decision_refs")
        if not isinstance(refs, list) or not refs:
            raise VerificationError(
                "Phase 34 exception coverage lacks canonical decision refs")
        for ref in refs:
            if not isinstance(ref, str) or not ref.startswith(prefix):
                raise VerificationError(
                    "Phase 34 exception coverage has an unsafe decision ref")
            active_ids.add(ref[len(prefix):])
    return sorted(active_ids)


def cutover_reason_codes(
    readiness_state: str,
    ledger_rows: list[dict[str, Any]],
) -> list[str]:
    reasons = sorted({
        str(reason)
        for row in ledger_rows if row.get("readiness_effect") == "blocked"
        for reason in row.get("reason_codes", [])
        if isinstance(reason, str) and reason
    })
    if readiness_state != "unblocked" and not reasons:
        return ["readiness-input-invalid"]
    return reasons


def load_bundle(
        root: Path, phase34: Path,
        contract: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_path = phase34 / "final-readiness-run-manifest.json"
    manifest = load_json(root, manifest_path)
    validate_phase34_manifest(contract, manifest)
    phase34_contract = load_json(root, PHASE34_CONTRACT_PATH)
    validate_phase34_contract(phase34_contract)
    paths = {
        "ledger": phase34 / "readiness-coverage-ledger.json",
        "packet": phase34 / "final-readiness-packet.json",
        "blocker_summary": phase34 / "readiness-blocker-summary.json",
        "dry_run": phase34 / "demotion-dry-run.json",
        "phase33_handoff": phase34 /
        "contract-snapshots/phase33-downstream-handoff-manifest.json",
        "phase32_register":
        phase34 / "contract-snapshots/phase32-blocker-register.json",
        "receipts":
        phase34 / "contract-snapshots/phase31-accepted-receipts.json",
    }
    loaded = {name: load_json(root, path) for name, path in paths.items()}
    for name, payload in loaded.items():
        scan_security(payload, paths[name].as_posix())
    if loaded["ledger"].get("phase_lifecycle_id"
                            ) != PHASE34_LIFECYCLE_ID or loaded["packet"].get(
                                "phase_lifecycle_id") != PHASE34_LIFECYCLE_ID:
        raise VerificationError(
            "Phase 34 packet or ledger lifecycle is mismatched",
            "source-artifact-lifecycle-mismatched",
        )
    if loaded["packet"].get("ledger_rows") != loaded["ledger"].get("rows"):
        raise VerificationError(
            "Phase 34 packet and ledger projections differ")
    if loaded["packet"].get("demotion_dry_run") != loaded["dry_run"]:
        raise VerificationError(
            "Phase 34 packet and demotion dry-run projections differ")
    handoff = loaded["phase33_handoff"]
    if handoff.get(
            "phase_lifecycle_id") != PHASE33_LIFECYCLE_ID or handoff.get(
                "artifact_name") != "phase33-maintainer-decision-inputs":
        reason_code = ("source-artifact-lifecycle-mismatched"
                       if handoff.get("phase_lifecycle_id")
                       != PHASE33_LIFECYCLE_ID else
                       "source-artifact-malformed")
        raise VerificationError(
            "Phase 33 reached handoff lifecycle or identity is invalid",
            reason_code,
        )
    refs = handoff.get("register_refs")
    if not isinstance(refs, dict):
        raise VerificationError(
            "Phase 33 reached handoff register_refs must be an object")
    register_digests = manifest["phase33_register_digests"]
    normalized = reached_register(root, refs, register_digests,
                                  "normalized_decision_records")
    loaded["retained"] = reached_register(
        root, refs, register_digests,
        "retained_code_decision_register").get("rows", [])
    loaded["residuals"] = reached_register(
        root, refs, register_digests,
        "residual_risk_decision_register").get("rows", [])
    loaded["exceptions"] = reached_register(root, refs, register_digests,
                                            "exception_decision_register").get(
                                                "rows", [])
    loaded["readiness_handoff"] = reached_register(
        root, refs, register_digests, "readiness_decision_handoff")
    loaded["demotion_handoff"] = reached_register(root, refs, register_digests,
                                                  "demotion_decision_handoff")
    loaded["normalized"] = normalized.get("rows", [])
    loaded["blockers"] = loaded["phase32_register"].get("rows", [])
    loaded["receipts"] = loaded["receipts"].get("receipts", [])
    for name in ("retained", "residuals", "exceptions", "normalized",
                 "blockers", "receipts"):
        if not isinstance(loaded[name], list) or not all(
                isinstance(row, dict) for row in loaded[name]):
            raise VerificationError(f"{name} must contain object rows")
    validate_register_projection(loaded["retained"], loaded["normalized"],
                                 "retained_code")
    validate_register_projection(loaded["residuals"], loaded["normalized"],
                                 "residual_risk")
    validate_register_projection(loaded["exceptions"], loaded["normalized"],
                                 "exception")
    return loaded, phase34_contract


def render_report(decision: dict[str, Any], route: dict[str, Any],
                  links: list[dict[str, Any]]) -> str:
    lines = [
        "# Phase 35 Cutover Decision",
        "",
        "Machine-readable JSON is authoritative. This report is derived from the canonical audit index, verdict, route, and demotion projection.",
        "",
        f"cutover_verdict: {decision['cutover_verdict']}",
        f"route: {route['route']}",
        f"reason_codes: {', '.join(decision['reason_codes']) or 'none'}",
        f"readiness_state: {decision['readiness_state']}",
        f"active_exception_ids: {', '.join(decision['active_exception_ids']) or 'none'}",
        f"blocker_ids: {', '.join(decision['blocker_ids']) or 'none'}",
        f"demotion_decision_validation_state: {decision['demotion_decision_validation_state']}",
        f"demotion_decision_state: {decision['demotion_decision_state']}",
        f"demotion_decision_source_refs: {', '.join(decision['demotion_decision_source_refs']) or 'none'}",
        f"demotion_gate_state: {decision['demotion_gate_state']}",
        f"demotion_gate_reason_codes: {', '.join(decision['demotion_gate_reason_codes']) or 'none'}",
        "",
        "## Audit Link Counts",
        "",
    ]
    for kind in AUDIT_KINDS:
        lines.append(
            f"{kind}: {decision['audit_link_counts_by_kind'].get(kind, 0)}")
    lines.extend(["", "## Blocking Predicates", ""])
    lines.extend(f"- {html.escape(reason)}"
                 for reason in decision["reason_codes"])
    if not decision["reason_codes"]:
        lines.append("- none")
    lines.extend(["", "## Repair Scope", ""])
    for row in route["follow_up_scope"]:
        lines.append(
            f"- {html.escape(row['scope_id'])}: {html.escape(row['required_action_ref'])}"
        )
    if not route["follow_up_scope"]:
        lines.append("- none")
    lines.extend([
        "", "## Canonical Audit Links", "",
        "| Link | Kind | Target | Effect |", "| --- | --- | --- | --- |"
    ])
    for link in links:
        values = [
            link["link_id"], link["kind"], link["target_ref"],
            link["verdict_effect"]
        ]
        lines.append("| " + " | ".join(
            html.escape(str(value), quote=False).replace("|", r"\|")
            for value in values) + " |")
    return "\n".join(lines) + "\n"


def reset_output(output: Path) -> None:
    if output.exists():
        if output.is_symlink() or not output.is_dir():
            raise VerificationError(
                "Phase 35 output contains a symlink escape")
        shutil.rmtree(output)
    output.mkdir(parents=True)


def create_staging_directory(root: Path, relative_output: Path) -> Path:
    parent = root / relative_output.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix=".phase35-stage-", dir=parent))
    except OSError as error:
        raise VerificationError(
            "unable to create Phase 35 staging directory") from error


def validate_mutation_target(
    root: Path,
    relative_target: Path,
    expected_target: Path,
    target_name: str,
    *,
    expect_directory: bool,
    allow_missing: bool,
) -> Path:
    target = repo_relative(relative_target, target_name)
    expected = repo_relative(expected_target, f"expected {target_name}")
    if target != expected:
        raise VerificationError(
            f"Phase 35 {target_name} target is outside its canonical path",
            "unsafe-ref",
        )
    root_resolved = root.resolve(strict=False)
    candidate = root / target
    current = root
    for index, part in enumerate(target.parts):
        current /= part
        if current.is_symlink():
            raise VerificationError(
                f"Phase 35 {target_name} target contains a symlink escape",
                "unsafe-ref",
            )
        if index < len(target.parts) - 1 and current.exists(
        ) and not current.is_dir():
            raise VerificationError(
                f"Phase 35 {target_name} parent is not a directory",
                "unsafe-ref",
            )
    resolved = candidate.resolve(strict=False)
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise VerificationError(
            f"Phase 35 {target_name} target escapes the repository",
            "unsafe-ref",
        )
    if candidate.exists():
        valid_type = (candidate.is_dir()
                      if expect_directory else candidate.is_file())
        if not valid_type:
            raise VerificationError(
                f"Phase 35 {target_name} target has the wrong type",
                "unsafe-ref",
            )
    elif not allow_missing:
        raise VerificationError(
            f"Phase 35 {target_name} target is missing",
            "unsafe-ref",
        )
    return candidate
