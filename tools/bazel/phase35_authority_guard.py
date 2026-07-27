from __future__ import annotations


def touch_guard(path: Path) -> None:
    path.touch(exist_ok=True)


def write_guard_payload(path: Path, payload: dict[str, object]) -> None:
    write_json(path, payload)


def rename_path(source: Path, target: Path) -> None:
    source.rename(target)


def remove_directory(path: Path) -> None:
    shutil.rmtree(path)


def remove_guard(path: Path) -> None:
    path.unlink()


def authority_guard_payload() -> dict[str, object]:
    return {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "authority_state": "blocked",
        "reason_code": AUTHORITY_GUARD_REASON,
        "attempted_output_root": DEFAULT_OUTPUT.as_posix(),
    }


def validate_authority_guard(root: Path) -> None:
    guard = validate_mutation_target(
        root,
        AUTHORITY_GUARD,
        AUTHORITY_GUARD,
        "authority guard",
        expect_directory=False,
        allow_missing=False,
    )
    try:
        payload = json.loads(guard.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError) as error:
        raise VerificationError(
            "Phase 35 authority guard is unreadable",
            "unsafe-ref",
        ) from error
    if not isinstance(payload,
                      dict) or list(payload) != AUTHORITY_GUARD_FIELDS:
        raise VerificationError("Phase 35 authority guard is malformed",
                                "unsafe-ref")
    if payload != authority_guard_payload():
        raise VerificationError("Phase 35 authority guard is stale or unsafe",
                                "unsafe-ref")


def ensure_canonical_authority(root: Path, relative_output: Path) -> None:
    ensure_no_workflow_attempt_marker(root)
    validate_mutation_target(
        root,
        relative_output,
        DEFAULT_OUTPUT,
        "canonical output",
        expect_directory=True,
        allow_missing=True,
    )
    guard = root / AUTHORITY_GUARD
    if not guard.exists() and not guard.is_symlink():
        return
    validate_authority_guard(root)
    raise VerificationError("Phase 35 canonical authority is blocked",
                            "unsafe-ref")


def ensure_no_workflow_attempt_marker(root: Path) -> None:
    current = root
    for index, part in enumerate(WORKFLOW_ATTEMPT_SHELL.parts):
        current /= part
        try:
            status = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as error:
            raise VerificationError(
                "Phase 38 workflow attempt is blocking",
                "unsafe-ref",
            ) from error
        if stat.S_ISLNK(status.st_mode):
            raise VerificationError(
                "Phase 38 workflow attempt is blocking",
                "unsafe-ref",
            )
        if (index < len(WORKFLOW_ATTEMPT_SHELL.parts) - 1
                and not stat.S_ISDIR(status.st_mode)):
            raise VerificationError(
                "Phase 38 workflow attempt is blocking",
                "unsafe-ref",
            )
    shell = root / WORKFLOW_ATTEMPT_SHELL
    try:
        shell.lstat()
    except FileNotFoundError:
        return
    except OSError as error:
        raise VerificationError(
            "Phase 38 workflow attempt is blocking",
            "unsafe-ref",
        ) from error
    raise VerificationError(
        "Phase 38 workflow attempt is blocking",
        "unsafe-ref",
    )


def publish_authority_guard(root: Path) -> None:
    guard = validate_mutation_target(
        root,
        AUTHORITY_GUARD,
        AUTHORITY_GUARD,
        "authority guard",
        expect_directory=False,
        allow_missing=True,
    )
    guard.parent.mkdir(parents=True, exist_ok=True)
    try:
        validate_mutation_target(
            root,
            AUTHORITY_GUARD,
            AUTHORITY_GUARD,
            "authority guard",
            expect_directory=False,
            allow_missing=True,
        )
        touch_guard(guard)
        validate_mutation_target(
            root,
            AUTHORITY_GUARD,
            AUTHORITY_GUARD,
            "authority guard",
            expect_directory=False,
            allow_missing=False,
        )
        write_guard_payload(guard, authority_guard_payload())
        validate_authority_guard(root)
    except (OSError, VerificationError) as error:
        raise VerificationError(
            "unable to publish Phase 35 authority guard",
            "unsafe-ref",
        ) from error


def discard_staging_directory(root: Path, stage: Path | None) -> None:
    if stage is None or not stage.exists():
        return
    relative_stage = stage.relative_to(root)
    validate_mutation_target(
        root,
        relative_stage,
        relative_stage,
        "staging output",
        expect_directory=True,
        allow_missing=False,
    )
    try:
        remove_directory(stage)
    except OSError as error:
        raise VerificationError(
            "unable to discard Phase 35 staging directory") from error


def restore_previous_bundle(root: Path, canonical_output: Path,
                            backup: Path) -> None:
    if canonical_output.exists():
        validate_mutation_target(
            root,
            DEFAULT_OUTPUT,
            DEFAULT_OUTPUT,
            "canonical output",
            expect_directory=True,
            allow_missing=False,
        )
        remove_directory(canonical_output)
    validate_mutation_target(
        root,
        PREVIOUS_OUTPUT,
        PREVIOUS_OUTPUT,
        "previous output",
        expect_directory=True,
        allow_missing=False,
    )
    validate_mutation_target(
        root,
        DEFAULT_OUTPUT,
        DEFAULT_OUTPUT,
        "canonical output",
        expect_directory=True,
        allow_missing=True,
    )
    rename_path(backup, canonical_output)


def install_staged_bundle(
    root: Path,
    stage: Path,
    canonical_output: Path,
    validate_installed: Callable[[Path], None],
) -> None:
    relative_stage = stage.relative_to(root)
    if canonical_output != root / DEFAULT_OUTPUT:
        raise VerificationError("Phase 35 canonical output path is invalid",
                                "unsafe-ref")
    backup = root / PREVIOUS_OUTPUT
    publish_authority_guard(root)
    validate_mutation_target(
        root,
        relative_stage,
        relative_stage,
        "staging output",
        expect_directory=True,
        allow_missing=False,
    )
    validate_mutation_target(
        root,
        DEFAULT_OUTPUT,
        DEFAULT_OUTPUT,
        "canonical output",
        expect_directory=True,
        allow_missing=True,
    )
    validate_mutation_target(
        root,
        PREVIOUS_OUTPUT,
        PREVIOUS_OUTPUT,
        "previous output",
        expect_directory=True,
        allow_missing=True,
    )
    if backup.exists():
        raise VerificationError("Phase 35 recoverable backup already exists")

    moved_previous = False
    installed = False
    try:
        if canonical_output.exists():
            validate_mutation_target(
                root,
                DEFAULT_OUTPUT,
                DEFAULT_OUTPUT,
                "canonical output",
                expect_directory=True,
                allow_missing=False,
            )
            validate_mutation_target(
                root,
                PREVIOUS_OUTPUT,
                PREVIOUS_OUTPUT,
                "previous output",
                expect_directory=True,
                allow_missing=True,
            )
            rename_path(canonical_output, backup)
            moved_previous = True
        validate_mutation_target(
            root,
            relative_stage,
            relative_stage,
            "staging output",
            expect_directory=True,
            allow_missing=False,
        )
        validate_mutation_target(
            root,
            DEFAULT_OUTPUT,
            DEFAULT_OUTPUT,
            "canonical output",
            expect_directory=True,
            allow_missing=True,
        )
        rename_path(stage, canonical_output)
        installed = True
        validate_installed(canonical_output)
    except (OSError, VerificationError) as error:
        try:
            if moved_previous:
                restore_previous_bundle(root, canonical_output, backup)
            elif installed and canonical_output.exists():
                validate_mutation_target(
                    root,
                    DEFAULT_OUTPUT,
                    DEFAULT_OUTPUT,
                    "canonical output",
                    expect_directory=True,
                    allow_missing=False,
                )
                remove_directory(canonical_output)
            if stage.exists():
                discard_staging_directory(root, stage)
        except (OSError, VerificationError) as recovery_error:
            raise VerificationError(
                "unable to recover Phase 35 staged publication"
            ) from recovery_error
        raise VerificationError(
            "unable to install Phase 35 staged bundle") from error

    if moved_previous:
        validate_mutation_target(
            root,
            PREVIOUS_OUTPUT,
            PREVIOUS_OUTPUT,
            "previous output",
            expect_directory=True,
            allow_missing=False,
        )
        try:
            remove_directory(backup)
        except OSError as error:
            raise VerificationError(
                "unable to remove Phase 35 recoverable backup") from error
    validate_authority_guard(root)
    guard = validate_mutation_target(
        root,
        AUTHORITY_GUARD,
        AUTHORITY_GUARD,
        "authority guard",
        expect_directory=False,
        allow_missing=False,
    )
    try:
        remove_guard(guard)
    except OSError as error:
        raise VerificationError(
            "unable to clear Phase 35 authority guard") from error


def source_failure_reason(error: VerificationError) -> str:
    if error.reason_code in SAFE_SOURCE_FAILURE_REASONS:
        return error.reason_code
    return "source-artifact-malformed"


def write_source_failure_bundle(relative_output: Path, output: Path,
                                reason_code: str) -> None:
    if reason_code not in SAFE_SOURCE_FAILURE_REASONS:
        reason_code = "source-artifact-malformed"
    reset_output(output)
    counts = {kind: 0 for kind in AUDIT_KINDS}
    manifest = {
        "artifact_name": "phase35-cutover-decision-artifact",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generation_state": "blocked-source-error",
        "output_root": relative_output.as_posix(),
        "generated_artifacts": SOURCE_FAILURE_ARTIFACTS,
        "source_manifest_ref":
        "build/ci-evidence/phase34/final-readiness-run-manifest.json",
        "source_failure_reason_codes": [reason_code],
        "raw_evidence_consumed": False,
    }
    decision = {
        "artifact_name": "phase35-cutover-decision",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_ids": REQUIREMENTS,
        "cutover_verdict": "blocked",
        "reason_codes": sorted({reason_code, "route-scope-incomplete"}),
        "readiness_state": "blocked",
        "readiness_result_ref": "",
        "active_exception_ids": [],
        "blocker_ids": [],
        "audit_link_index_ref": "",
        "audit_link_counts_by_kind": counts,
        "demotion_decision_validation_state": "invalid",
        "demotion_decision_state": "missing",
        "demotion_decision_source_refs": [],
        "demotion_gate_state": "blocked",
        "demotion_gate_reason_codes": [reason_code],
        "route_ref": "build/ci-evidence/phase35/next-milestone-route.json",
        "raw_evidence_consumed": False,
    }
    route = {
        "artifact_name": "phase35-next-milestone-route",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "route": "targeted-blocker-repair",
        "source_verdict": "blocked",
        "follow_up_scope": [],
        "requires_fresh_cutover_decision": True,
        "planning_only": True,
        "production_actions_authorized": False,
    }
    write_json(output / "cutover-decision-run-manifest.json", manifest)
    write_json(output / "cutover-decision.json", decision)
    write_json(output / "next-milestone-route.json", route)
    validate_source_failure_bundle(output)


def validate_source_failure_bundle(output: Path) -> None:
    actual = sorted(
        path.relative_to(output).as_posix() for path in output.rglob("*")
        if path.is_file())
    if actual != SOURCE_FAILURE_ARTIFACTS:
        raise VerificationError(
            "Phase 35 source failure artifact set is not exact")
    try:
        manifest = json.loads(
            (output /
             "cutover-decision-run-manifest.json").read_text(encoding="utf-8"))
        decision = json.loads(
            (output / "cutover-decision.json").read_text(encoding="utf-8"))
        route = json.loads(
            (output / "next-milestone-route.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError) as error:
        raise VerificationError(
            "Phase 35 source failure bundle is unreadable") from error
    if (list(manifest) != SOURCE_FAILURE_MANIFEST_FIELDS
            or list(decision) != DECISION_FIELDS
            or list(route) != ROUTE_FIELDS):
        raise VerificationError("Phase 35 source failure fields are not exact")
    reasons = manifest.get("source_failure_reason_codes")
    if (not isinstance(reasons, list) or len(reasons) != 1
            or reasons[0] not in SAFE_SOURCE_FAILURE_REASONS):
        raise VerificationError("Phase 35 source failure reasons are invalid")
    reason_code = reasons[0]
    expected_counts = {kind: 0 for kind in AUDIT_KINDS}
    if (manifest.get("generation_state") != "blocked-source-error"
            or manifest.get("generated_artifacts") != SOURCE_FAILURE_ARTIFACTS
            or manifest.get("raw_evidence_consumed") is not False
            or decision.get("cutover_verdict") != "blocked"
            or decision.get("reason_codes") != sorted(
                {reason_code, "route-scope-incomplete"})
            or decision.get("readiness_state") != "blocked"
            or decision.get("readiness_result_ref") != ""
            or decision.get("active_exception_ids") != []
            or decision.get("blocker_ids") != []
            or decision.get("audit_link_index_ref") != ""
            or decision.get("audit_link_counts_by_kind") != expected_counts
            or decision.get("demotion_decision_validation_state") != "invalid"
            or decision.get("demotion_decision_state") != "missing"
            or decision.get("demotion_decision_source_refs") != []
            or decision.get("demotion_gate_state") != "blocked"
            or decision.get("demotion_gate_reason_codes") != [reason_code]
            or decision.get("raw_evidence_consumed") is not False
            or route.get("route") != "targeted-blocker-repair"
            or route.get("source_verdict") != "blocked"
            or route.get("follow_up_scope") != []
            or route.get("requires_fresh_cutover_decision") is not True
            or route.get("planning_only") is not True
            or route.get("production_actions_authorized") is not False):
        raise VerificationError(
            "Phase 35 source failure semantics are invalid")
    for artifact, payload in (
        ("cutover-decision-run-manifest.json", manifest),
        ("cutover-decision.json", decision),
        ("next-milestone-route.json", route),
    ):
        scan_security(payload, artifact)


def publish_failed_phase34_bundle(root: Path) -> None:
    output = validate_output_path(root, DEFAULT_OUTPUT.as_posix())
    canonical_output = root / output
    failure_stage = create_staging_directory(root, output)
    try:
        write_source_failure_bundle(
            output,
            failure_stage,
            "source-artifact-malformed",
        )
        install_staged_bundle(
            root,
            failure_stage,
            canonical_output,
            validate_source_failure_bundle,
        )
    except VerificationError:
        if failure_stage.exists():
            discard_staging_directory(root, failure_stage)
        raise


def validate_generated_outputs(output: Path) -> None:
    actual = sorted(
        path.relative_to(output).as_posix() for path in output.rglob("*")
        if path.is_file())
    if actual != sorted(GENERATED_ARTIFACTS):
        raise VerificationError("Phase 35 generated artifact set is not exact")
    decision = json.loads(
        (output / "cutover-decision.json").read_text(encoding="utf-8"))
    route = json.loads(
        (output / "next-milestone-route.json").read_text(encoding="utf-8"))
    index = json.loads(
        (output / "cutover-audit-link-index.json").read_text(encoding="utf-8"))
    report = (output / "redacted-cutover-decision-report.md").read_text(
        encoding="utf-8")
    if list(decision) != DECISION_FIELDS or list(route) != ROUTE_FIELDS:
        raise VerificationError(
            "Phase 35 decision or route field set is not exact")
    links = index.get("links")
    if not isinstance(links, list):
        raise VerificationError("Phase 35 audit index is invalid")
    resolution_reasons = validate_resolved_audit_links(output.parents[2],
                                                       links)
    if not set(resolution_reasons).issubset(decision.get("reason_codes", [])):
        raise VerificationError(
            "Phase 35 audit index resolution failures are not fail-closed")
    expected_report = render_report(decision, route, links)
    if report != expected_report:
        raise VerificationError(
            "Phase 35 Markdown projection drifted from JSON")
    for artifact in GENERATED_ARTIFACTS:
        path = output / artifact
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".json":
                payload = json.loads(text)
                if not isinstance(payload, dict):
                    raise VerificationError(
                        f"{artifact} must contain an object")
                if artifact.startswith("contract-snapshots/"):
                    scan_security(
                        payload,
                        artifact,
                        allow_contract_vocabulary=artifact.endswith(
                            "_contract.json"),
                    )
                else:
                    scan_security(payload, artifact)
            else:
                for pattern in FORBIDDEN_TEXT:
                    if pattern.search(text):
                        raise VerificationError(
                            f"{artifact} contains forbidden text",
                            "secret-tainted",
                        )
        except (json.JSONDecodeError, UnicodeError, OSError) as error:
            raise VerificationError(
                f"generated artifact is unreadable: {artifact}") from error
