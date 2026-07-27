#!/usr/bin/env python3
from __future__ import annotations

from phase17_release_evidence_policy import *


def default_status_for(row: dict[str, Any]) -> str:
    if row.get("proof_scope") == "source-contract":
        return "source-contract-passed"
    return str(row.get("default_status", "pending-release-input"))


def result_row(contract_row: dict[str, Any],
               maybe_release_row: dict[str, Any] | None) -> dict[str, Any]:
    status = default_status_for(contract_row)
    artifact_refs = [str(contract_row["expected_artifact_path"])]
    signing_mode = "external-release-key" if contract_row[
        "signing_metadata_required"] else "not-applicable"
    row = {
        "artifact_digest_sha256":
        "",
        "artifact_refs":
        artifact_refs,
        "artifact_outputs":
        contract_row["artifact_outputs"],
        "artifact_surface":
        contract_row["artifact_surface"],
        "bazel_label":
        contract_row["bazel_label"],
        "comparison_refs": [],
        "id":
        contract_row["id"],
        "key_identity_ref":
        "",
        "mismatch_class":
        contract_row["mismatch_class"],
        "mismatch_reason":
        "Awaiting approved release comparison metadata.",
        "owner_phase":
        contract_row["owner_phase"],
        "product_profile":
        contract_row["product_profile"],
        "proof_scope":
        contract_row["proof_scope"],
        "provenance_refs": [],
        "release_command":
        contract_row["release_command"],
        "release_run_required":
        contract_row["release_run_required"],
        "residual_risk":
        "Awaiting approved release-run evidence." if status
        != "source-contract-passed" else "Source contract boundary only.",
        "retention_path":
        str(contract_row["expected_artifact_path"]),
        "signing_mode":
        signing_mode,
        "status":
        status,
        "verification_outcome":
        "pending-release-input",
    }
    if maybe_release_row is not None:
        row.update({
            "artifact_digest_sha256":
            maybe_release_row["artifact_digest_sha256"],
            "artifact_refs":
            maybe_release_row["artifact_refs"],
            "comparison_refs":
            maybe_release_row["comparison_refs"],
            "key_identity_ref":
            maybe_release_row["key_identity_ref"],
            "mismatch_class":
            maybe_release_row["mismatch_class"],
            "mismatch_reason":
            maybe_release_row["mismatch_reason"],
            "provenance_refs":
            maybe_release_row["provenance_refs"],
            "residual_risk":
            maybe_release_row["residual_risk"],
            "retention_path":
            maybe_release_row["retention_path"],
            "signing_mode":
            maybe_release_row["signing_mode"],
            "status":
            maybe_release_row["result"],
            "verification_outcome":
            maybe_release_row["verification_outcome"],
        })
    return row


def write_json(root: Path, relative_path: Path, data: dict[str, Any]) -> None:
    full_path = root / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")


def write_log(root: Path, output_dir: Path, row: dict[str, Any]) -> None:
    log_path = output_dir / "logs" / f"{row['id']}.log"
    lines = [
        f"row_id={row['id']}",
        f"status={row['status']}",
        f"proof_scope={row['proof_scope']}",
        f"artifact_surface={row['artifact_surface']}",
        f"bazel_label={row['bazel_label']}",
        f"release_run_required={str(row['release_run_required']).lower()}",
        f"artifact_refs={','.join(row['artifact_refs'])}",
        f"residual_risk={row['residual_risk']}",
    ]
    full_path = root / log_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_quick_artifacts(root: Path, contract: dict[str,
                                                     Any], output_dir: Path,
                          release_rows: dict[str, dict[str, Any]]) -> None:
    relative_output_dir = require_repo_relative_under(output_dir,
                                                      DEFAULT_OUTPUT_DIR,
                                                      "--output-dir")
    full_output_dir = contained_output_dir(root, relative_output_dir)
    if full_output_dir.exists():
        shutil.rmtree(full_output_dir)
    (full_output_dir / "logs").mkdir(parents=True)
    (full_output_dir / "source-contract-snapshots").mkdir(parents=True)
    rows = [
        result_row(row, release_rows.get(str(row["id"])))
        for row in contract_rows(contract)
    ]
    for row in rows:
        write_log(root, relative_output_dir, row)
    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    snapshot_path = relative_output_dir / "source-contract-snapshots" / CONTRACT_MANIFEST.name
    run_manifest = {
        "artifact_name":
        contract["artifact_name"],
        "command_mode":
        "quick",
        "output_root":
        relative_output_dir.as_posix(),
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "release_inputs_supplied":
        bool(release_rows),
        "requirement_coverage":
        sorted(REQUIRED_REQUIREMENT_IDS),
        "row_summaries": [{
            key: row[key]
            for key in [
                "id", "artifact_surface", "proof_scope", "status",
                "bazel_label", "release_run_required"
            ]
        } for row in rows],
        "source_contract_snapshot_path":
        snapshot_path.as_posix(),
        "status_counts":
        status_counts,
    }
    normalized = {
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "results": rows
    }
    signing_summary = {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "release_inputs_supplied":
        bool(release_rows),
        "rows": [{
            key: row[key]
            for key in [
                "id", "status", "signing_mode", "key_identity_ref",
                "artifact_digest_sha256", "retention_path",
                "verification_outcome"
            ]
        } for row in rows if "REL-02" in next(
            contract_row["requirement_ids"]
            for contract_row in contract_rows(contract)
            if contract_row["id"] == row["id"])],
    }
    comparison_report = {
        "phase":
        PHASE,
        "phase_lifecycle_id":
        PHASE_LIFECYCLE_ID,
        "comparisons": [{
            "artifact_refs":
            row["artifact_refs"],
            "artifact_surface":
            row["artifact_surface"],
            "mismatch_class":
            row["mismatch_class"],
            "mismatch_reason":
            row["mismatch_reason"],
            "normalized_fields_compared": [
                "artifact-kind",
                "product-profile",
                "package-member-identities",
                "signing-mode-name",
                "provenance-metadata",
            ],
            "owner_phase":
            row["owner_phase"],
            "product_profile":
            row["product_profile"],
            "reference_source":
            "tools/bazel/manifests/phase11_reference_comparisons.json",
            "residual_risk":
            row["residual_risk"],
            "rust_bazel_surface":
            row["bazel_label"],
        } for row in rows
                        if row["artifact_surface"] == "reference-comparison"],
    }
    write_json(root, relative_output_dir / "run-manifest.json", run_manifest)
    write_json(root, relative_output_dir / "normalized-release-results.json",
               normalized)
    write_json(
        root, relative_output_dir / "redacted-signing-provenance-summary.json",
        signing_summary)
    write_json(root,
               relative_output_dir / "comparison-classification-report.json",
               comparison_report)
    write_json(root,
               relative_output_dir / "release-operator-evidence-input.json",
               {"evidence_rows": list(release_rows.values())})
    shutil.copy2(root / CONTRACT_MANIFEST, root / snapshot_path)
