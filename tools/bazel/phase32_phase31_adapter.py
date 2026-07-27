from __future__ import annotations

from phase32_triage_policy import *


def release_receipt_provenance_problem(
    receipt: dict[str, Any],
    required_fields: list[Any],
    expected_table_path: Path,
) -> str | None:
    missing_fields = sorted(
        str(field) for field in required_fields
        if isinstance(field, str) and field not in receipt)
    if missing_fields:
        return (
            "accepted release receipt is missing required provenance fields: "
            f"{', '.join(missing_fields)}")

    required_strings = [
        "submission_id",
        "stream",
        "finality_status",
        "packet_sha256",
        "submitter_identity_ref",
        "receipt_generated_at_utc",
        "redaction_status",
        "source_ref_status",
        "exception_status",
        "failure_reason",
    ]
    invalid_string_fields = [
        field for field in required_strings
        if not isinstance(receipt.get(field), str)
    ]
    if invalid_string_fields:
        return ("accepted release receipt has invalid provenance field types: "
                f"{', '.join(invalid_string_fields)}")

    packet_sha256 = str(receipt["packet_sha256"])
    if re.fullmatch(r"[0-9a-f]{64}", packet_sha256) is None:
        return "accepted release receipt packet_sha256 must be a lowercase SHA-256 digest"
    if not receipt["submission_id"] or not receipt[
            "submitter_identity_ref"] or not receipt[
                "receipt_generated_at_utc"]:
        return "accepted release receipt identity and timestamp provenance must be non-empty"
    if receipt["stream"] != "release-signing":
        return "accepted release receipt stream must be release-signing"
    if receipt["finality_status"] != "accepted-final":
        return "accepted release receipt finality_status must be accepted-final"
    if receipt["redaction_status"] != "passed" or receipt[
            "source_ref_status"] != "passed":
        return "accepted release receipt security provenance must be passed"

    requirement_ids = receipt.get("requirement_ids")
    if (not isinstance(requirement_ids, list) or not requirement_ids
            or not all(
                isinstance(requirement_id, str) and requirement_id
                for requirement_id in requirement_ids)):
        return "accepted release receipt requirement_ids must be a non-empty string list"

    validator_command = receipt.get("validator_command")
    if (not isinstance(validator_command, list) or not validator_command
            or not all(
                isinstance(argument, str) and argument
                for argument in validator_command)):
        return "accepted release receipt validator_command must be a non-empty string list"

    consumed_refs = string_list(receipt.get("consumed_upstream_row_refs"))
    if consumed_refs != [expected_table_path.as_posix()]:
        return ("accepted release receipt must consume exactly the contracted "
                f"Phase 26 table at {expected_table_path.as_posix()}")

    validator_output_refs = string_list(receipt.get("validator_output_refs"))
    if expected_table_path.as_posix() not in validator_output_refs:
        return (
            "accepted release receipt validator outputs do not include the "
            f"contracted Phase 26 table at {expected_table_path.as_posix()}")
    if not isinstance(receipt.get("artifact_reference_summary"), dict):
        return "accepted release receipt artifact_reference_summary must be an object"
    return None


def release_receipt_provenance_blocker(
    receipt_path: Path,
    receipt: dict[str, Any],
    failure_reason: str,
) -> dict[str, Any]:
    submission_id = str(
        receipt.get("submission_id") or "release-signing-receipt")
    return build_blocker_row(
        source_domain="release_signing",
        producer_phase="phase26",
        producer_artifact_kind="phase26_upstream_result_row_table",
        source_row_kind="upstream_result_criterion",
        source_subject_id=f"{submission_id}:release-receipt-provenance",
        decision_axis="readiness",
        decision_subject_id="phase26-upstream-result-row-table",
        source_stream="release-signing",
        source_ref=f"{receipt_path.as_posix()}#release-receipt-provenance",
        signal={
            "adapter_problem_kind": "unknown_unclassified",
            "failure_reason": failure_reason,
            "requirement_ids": receipt.get("requirement_ids", []),
            "evidence_refs": [receipt_path.as_posix()],
        },
    )


def load_phase31_rows(root: Path,
                      phase31_output_dir: Path) -> list[dict[str, Any]]:
    phase31_dir = path_under(phase31_output_dir, DEFAULT_PHASE31_OUTPUT_DIR,
                             "--phase31-output-dir")
    manifest_path = phase31_dir / "final-intake-manifest.json"
    rejected_path = phase31_dir / "rejected-submissions.json"
    manifest = load_json(root, manifest_path)
    rejected = load_json(root, rejected_path)
    phase32_contract = load_contract(root)
    phase26_adapter = require_dict(
        require_dict(phase32_contract["producer_adapters"],
                     "producer_adapters").get("phase26_release_signing_table"),
        "producer_adapters.phase26_release_signing_table",
    )
    expected_phase26_table_path = Path(
        require_string(
            phase26_adapter.get("expected_artifact_path"),
            "producer_adapters.phase26_release_signing_table.expected_artifact_path",
        ))
    phase31_contract = load_json(
        root,
        SOURCE_CONTRACT_SNAPSHOTS[
            "phase31_final_evidence_intake_contract.json"],
    )
    receipt_provenance_fields = require_list(
        phase31_contract.get("receipt_provenance_fields"),
        "phase31 receipt_provenance_fields",
    )
    rows: list[dict[str, Any]] = []

    for rejection_index, rejected_row in enumerate(
            require_list(rejected.get("rejected_submissions"),
                         "rejected_submissions")):
        if not isinstance(rejected_row, dict):
            raise VerificationError(
                "rejected_submissions entries must be objects")
        source_stream = str(rejected_row.get("stream") or "unknown")
        submission_id = str(
            rejected_row.get("submission_id")
            or f"{source_stream}-rejection-{rejection_index}")
        signal = {
            "finality_status": rejected_row.get("finality_status"),
            "failure_reason": rejected_row.get("reason", ""),
            "requirement_ids": rejected_row.get("requirement_ids", []),
            "status": rejected_row.get("finality_status"),
        }
        rows.append(
            build_blocker_row(
                source_domain="final_evidence_intake",
                producer_phase="phase31",
                producer_artifact_kind="phase31_rejected_submissions",
                source_row_kind="rejected_submission",
                source_subject_id=submission_id,
                decision_axis="readiness",
                decision_subject_id=submission_id,
                source_stream=source_stream,
                source_ref=f"{rejected_path.as_posix()}#{submission_id}",
                signal=signal,
            ))

    for receipt_ref in string_list(manifest.get("receipt_refs")):
        receipt_path = repo_relative_path(receipt_ref, "receipt_refs[]")
        receipt = load_json(root, receipt_path)
        source_stream = str(receipt.get("stream") or "unknown")
        submission_id = str(
            receipt.get("submission_id") or f"{source_stream}-receipt")
        if receipt.get("finality_status") != "accepted-final":
            rows.append(
                build_blocker_row(
                    source_domain="final_evidence_intake",
                    producer_phase="phase31",
                    producer_artifact_kind="phase31_final_intake_receipt",
                    source_row_kind="intake_receipt",
                    source_subject_id=submission_id,
                    decision_axis="readiness",
                    decision_subject_id=submission_id,
                    source_stream=source_stream,
                    source_ref=receipt_path.as_posix(),
                    signal={
                        "finality_status": receipt.get("finality_status"),
                        "failure_reason": receipt.get("failure_reason", ""),
                        "requirement_ids": receipt.get("requirement_ids", []),
                    },
                ))
            continue
        if source_stream == "release-signing":
            maybe_provenance_problem = release_receipt_provenance_problem(
                receipt,
                receipt_provenance_fields,
                expected_phase26_table_path,
            )
            if maybe_provenance_problem is not None:
                rows.append(
                    release_receipt_provenance_blocker(
                        receipt_path,
                        receipt,
                        maybe_provenance_problem,
                    ))
                continue
        consumed_refs = string_list(receipt.get("consumed_upstream_row_refs"))
        if not consumed_refs:
            rows.append(
                build_blocker_row(
                    source_domain="final_evidence_intake",
                    producer_phase="phase31",
                    producer_artifact_kind="phase31_final_intake_receipt",
                    source_row_kind="intake_receipt",
                    source_subject_id=f"{submission_id}:consumed-upstream-rows",
                    decision_axis="readiness",
                    decision_subject_id=submission_id,
                    source_stream=source_stream,
                    source_ref=
                    f"{receipt_path.as_posix()}#missing-consumed-upstream-row-refs",
                    signal={
                        "status": "missing",
                        "failure_reason":
                        "accepted-final receipt did not list consumed upstream row refs",
                        "requirement_ids": receipt.get("requirement_ids", []),
                    },
                ))
            continue
        for consumed_index, consumed_ref in enumerate(consumed_refs):
            consumed_path = repo_relative_path(consumed_ref,
                                               "consumed_upstream_row_refs[]")
            if not (root / consumed_path).exists():
                rows.append(
                    build_blocker_row(
                        source_domain="final_evidence_intake",
                        producer_phase="phase31",
                        producer_artifact_kind="phase31_final_intake_receipt",
                        source_row_kind="missing_source_artifact",
                        source_subject_id=
                        f"{submission_id}:missing-upstream-{consumed_index}",
                        decision_axis="readiness",
                        decision_subject_id=submission_id,
                        source_stream=source_stream,
                        source_ref=consumed_path.as_posix(),
                        signal={
                            "status": "missing",
                            "failure_reason":
                            "accepted-final receipt referenced a missing upstream row detail",
                            "requirement_ids":
                            receipt.get("requirement_ids", []),
                            "evidence_refs": [receipt_path.as_posix()],
                        },
                    ))
                continue
            source_row = load_json(root, consumed_path)
            if source_stream == "release-signing":
                if consumed_path != expected_phase26_table_path:
                    rows.append(
                        build_blocker_row(
                            source_domain="release_signing",
                            producer_phase="phase26",
                            producer_artifact_kind=
                            "phase26_upstream_result_row_table",
                            source_row_kind="upstream_result_criterion",
                            source_subject_id=
                            "phase26-upstream-result-row-table",
                            decision_axis="readiness",
                            decision_subject_id=
                            "phase26-upstream-result-row-table",
                            source_stream=source_stream,
                            source_ref=consumed_path.as_posix(),
                            signal={
                                "adapter_problem_kind":
                                "unknown_unclassified",
                                "failure_reason":
                                "accepted release receipt referenced an unsupported artifact",
                                "requirement_ids":
                                receipt.get("requirement_ids", []),
                                "evidence_refs": [receipt_path.as_posix()],
                            },
                        ))
                    continue
                phase26_contract = load_json(
                    root,
                    Path(
                        "tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json"
                    ),
                )
                upstream_policy = require_dict(
                    phase26_contract.get("upstream_policy"),
                    "phase26 upstream_policy",
                )
                signals = adapt_phase26_table(
                    source_row,
                    expected_criteria=require_list(
                        upstream_policy.get("canonical_phase18_criteria"),
                        "phase26 canonical criteria",
                    ),
                    required_row_fields=require_list(
                        upstream_policy.get("row_required_fields"),
                        "phase26 row required fields",
                    ),
                    allowed_statuses=PHASE26_ALLOWED_STATUSES,
                    receipt_ref=receipt_path.as_posix(),
                    table_ref=consumed_path.as_posix(),
                )
                for signal in signals:
                    if is_non_blocking_source_row(signal):
                        continue
                    source_subject_id = str(
                        signal.get("source_subject_id")
                        or "phase26-upstream-result-row-table")
                    rows.append(
                        build_blocker_row(
                            source_domain="release_signing",
                            producer_phase="phase26",
                            producer_artifact_kind=
                            "phase26_upstream_result_row_table",
                            source_row_kind="upstream_result_criterion",
                            source_subject_id=source_subject_id,
                            decision_axis="readiness",
                            decision_subject_id=source_subject_id,
                            source_stream=source_stream,
                            source_ref=
                            f"{consumed_path.as_posix()}#{source_subject_id}",
                            signal={
                                **signal,
                                "requirement_ids":
                                signal.get(
                                    "requirement_ids",
                                    receipt.get("requirement_ids", []),
                                ),
                                "evidence_refs": [
                                    *string_list(signal.get("evidence_refs")),
                                    receipt_path.as_posix(),
                                    consumed_path.as_posix(),
                                ],
                            },
                        ))
                continue
            source_signal = {**source_row, "source_stream": source_stream}
            if is_non_blocking_source_row(source_signal):
                continue
            criterion_id = str(
                source_signal.get("criterion_id")
                or f"upstream-row-{consumed_index}")
            rows.append(
                build_blocker_row(
                    source_domain="final_evidence_intake",
                    producer_phase="phase31",
                    producer_artifact_kind="phase31_final_intake_receipt",
                    source_row_kind="intake_receipt",
                    source_subject_id=
                    f"{submission_id}:{criterion_id}:{consumed_index}",
                    decision_axis="readiness",
                    decision_subject_id=criterion_id,
                    source_stream=source_stream,
                    source_ref=consumed_path.as_posix(),
                    signal=source_signal,
                ))
    return rows
