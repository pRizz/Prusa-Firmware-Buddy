#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "35-cutover-decision-artifact"
PHASE_LIFECYCLE_ID = "35-2026-07-25T21-06-10"
PHASE33_LIFECYCLE_ID = "33-2026-07-04T01-36-41"
PHASE34_LIFECYCLE_ID = "34-2026-07-25T18-18-48"
CONTRACT_PATH = Path(
    "tools/bazel/manifests/phase35_cutover_decision_artifact_contract.json")
PHASE34_CONTRACT_PATH = Path(
    "tools/bazel/manifests/phase34_final_readiness_demotion_dry_run_contract.json"
)
DEFAULT_PHASE34_OUTPUT = Path("build/ci-evidence/phase34")
DEFAULT_OUTPUT = Path("build/ci-evidence/phase35")
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
PHASE34_LEDGER_REF = "build/ci-evidence/phase34/readiness-coverage-ledger.json"
PHASE33_EXCEPTION_REGISTER = "build/ci-evidence/phase33/exception-decision-register.json"
PHASE33_RESIDUAL_REGISTER = "build/ci-evidence/phase33/residual-risk-decision-register.json"
REQUIREMENTS = ["CUTOVER-01", "CUTOVER-02", "CUTOVER-03"]
AUDIT_KINDS = [
    "evidence-packet",
    "blocker",
    "exception",
    "residual-risk",
    "retained-code-decision",
    "readiness-decision",
    "readiness-result",
    "demotion-decision",
    "demotion-dry-run",
]
AUDIT_FIELDS = [
    "link_id",
    "kind",
    "target_id",
    "target_ref",
    "source_phase_lifecycle_id",
    "verdict_effect",
]
GENERATED_ARTIFACTS = [
    "cutover-decision-run-manifest.json",
    "cutover-audit-link-index.json",
    "cutover-decision.json",
    "next-milestone-route.json",
    "redacted-cutover-decision-report.md",
    "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
    "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
    "contract-snapshots/phase34-final-readiness-run-manifest.json",
]
DECISION_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "requirement_ids",
    "cutover_verdict",
    "reason_codes",
    "readiness_state",
    "readiness_result_ref",
    "active_exception_ids",
    "blocker_ids",
    "audit_link_index_ref",
    "audit_link_counts_by_kind",
    "demotion_decision_validation_state",
    "demotion_decision_state",
    "demotion_decision_source_refs",
    "demotion_gate_state",
    "demotion_gate_reason_codes",
    "route_ref",
    "raw_evidence_consumed",
]
ROUTE_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "route",
    "source_verdict",
    "follow_up_scope",
    "requires_fresh_cutover_decision",
    "planning_only",
    "production_actions_authorized",
]
PHASE34_ARTIFACTS = [
    "final-readiness-run-manifest.json",
    "readiness-coverage-ledger.json",
    "final-readiness-packet.json",
    "readiness-blocker-summary.json",
    "demotion-dry-run.json",
    "redacted-readiness-report.md",
    "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase33-downstream-handoff-manifest.json",
    "contract-snapshots/phase32-blocker-register.json",
    "contract-snapshots/phase31-final-intake-manifest.json",
    "contract-snapshots/phase31-accepted-receipts.json",
]
PHASE35_CONTRACT_FIELDS = {
    "artifact_name", "audit_link_failure_modes", "audit_link_schema",
    "authority_boundaries", "blocked_reason_codes", "cutover_decision_fields",
    "default_behavior", "demotion_projection", "generated_artifacts", "id",
    "output_root", "phase", "phase_lifecycle_id", "repair_scope_fields",
    "repair_scope_ref_policy", "requirement_ids", "route_enum", "route_fields",
    "route_semantics", "route_truth_table", "schema_version", "security",
    "source_contract", "source_lifecycle_ids", "verdict_enum",
    "verdict_truth_table", "verification_commands",
}
PHASE34_CONTRACT_FIELDS = {
    "artifact_name", "blocked_reason_codes", "default_behavior",
    "demotion_dry_run_schema", "generated_artifacts",
    "hard_blocker_problem_kinds", "id", "io_validation_responsibilities",
    "ledger_schema", "output_root", "phase", "phase_lifecycle_id",
    "prohibited_output_markers", "prohibited_semantics", "pure_evaluator_outputs",
    "requirement_ids", "schema_version", "source_contracts", "source_inputs",
    "sparse_blocker_overlay_policy", "test_command", "verification_commands",
}
PHASE34_MANIFEST_FIELDS = {
    "accepted_receipt_snapshot_ref", "artifact_name", "generated_artifacts",
    "generated_at_utc", "output_root", "phase", "phase_lifecycle_id",
    "raw_evidence_consumed", "snapshot_refs", "source_refs",
}
ALLOWED_REF_PREFIXES = (
    "build/ci-evidence/phase23/",
    "build/ci-evidence/phase24/",
    "build/ci-evidence/phase25/",
    "build/ci-evidence/phase26/",
    "build/ci-evidence/phase27/",
    "build/ci-evidence/phase28/",
    "build/ci-evidence/phase29/",
    "build/ci-evidence/phase30/",
    "build/ci-evidence/phase31/",
    "build/ci-evidence/phase32/",
    "build/ci-evidence/phase33/",
    "build/ci-evidence/phase34/",
    "build/ci-evidence/phase35/",
    "external://phase23/",
    "external://phase24/",
    "external://phase25/",
    "external://phase26/",
    "external://phase27/",
    "external://phase28/",
    "external://phase29/",
    "external://phase30/",
    "external://phase31/",
    "external://phase32/",
    "external://phase33/",
    "external://phase34/",
    "maintainer://",
    "owner://",
)
FORBIDDEN_FIELDS = {
    "access_token",
    "api_key",
    "authorization_header",
    "certificate_pem",
    "client_secret",
    "credential_value",
    "password",
    "private_key",
    "raw_crash_dump",
    "raw_payload",
    "raw_release_log",
    "secret",
    "secret_value",
    "service_payload",
    "signing_key_value",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE),
    re.compile(r"\bproduction demotion complete\b", re.IGNORECASE),
    re.compile(r"\breference demotion authorized by cutover\b", re.IGNORECASE),
    re.compile(r"\bproduction rollout authorized\b", re.IGNORECASE),
    re.compile(r"\braw evidence payload\b", re.IGNORECASE),
)
CONTRACT_VOCABULARY = {
    "production demotion complete",
    "reference demotion authorized by cutover",
    "production rollout authorized",
    "raw evidence payload",
}
STALE_BEFORE = datetime(2026, 4, 26, tzinfo=timezone.utc)
PHASE35_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31",
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26",
    "python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --output-dir build/ci-evidence/phase27",
    "python3 tools/bazel/phase28_final_readiness_packet.py --quick --phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json --phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json --output-dir build/ci-evidence/phase28",
    "python3 tools/bazel/phase32_blocker_register_triage.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase27-output-dir build/ci-evidence/phase27 --phase28-output-dir build/ci-evidence/phase28 --output-dir build/ci-evidence/phase32",
    "python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick --phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase33",
    "python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --wiring-only",
    "python3 tools/bazel/phase34_final_readiness_demotion_dry_run.py --quick --phase31-output-dir build/ci-evidence/phase31 --phase33-handoff build/ci-evidence/phase33/downstream-handoff-manifest.json --output-dir build/ci-evidence/phase34",
    "python3 tools/bazel/phase35_cutover_decision_artifact.py --wiring-only",
    "python3 tools/bazel/phase35_cutover_decision_artifact.py --quick --phase34-output-dir build/ci-evidence/phase34 --output-dir build/ci-evidence/phase35",
]
PHASE35_TEST_COMMANDS = [
    "python3 tools/bazel/phase35_cutover_decision_artifact_test.py",
]


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_json(root: Path,
              relative_path: Path,
              field: str | None = None) -> dict[str, Any]:
    full_path = root / relative_path
    if not full_path.is_file():
        raise VerificationError(
            f"source artifact missing: {relative_path.as_posix()}")
    try:
        value = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"source artifact malformed: {relative_path.as_posix()}: {error}"
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


def validate_ref(value: str, field: str = "ref") -> None:
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{field} must be a non-blank string")
    if not value.startswith(ALLOWED_REF_PREFIXES):
        raise VerificationError(f"unsafe ref in {field}: {value}")
    if value.startswith(("external://", "maintainer://", "owner://")):
        return
    path_text = value.split("#", 1)[0]
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts or "\\" in path_text:
        raise VerificationError(f"unsafe ref in {field}: {value}")


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
        raise VerificationError("\n".join(errors))


def repo_relative(value: str | Path, field: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        raise VerificationError(f"{field} must be repo-relative")
    if ".." in path.parts:
        raise VerificationError(f"{field} contains parent traversal")
    return path


def validate_paths(root: Path, phase34_arg: str | Path,
                   output_arg: str | Path) -> tuple[Path, Path]:
    phase34 = repo_relative(phase34_arg, "--phase34-output-dir")
    output = repo_relative(output_arg, "--output-dir")
    if phase34 != DEFAULT_PHASE34_OUTPUT:
        raise VerificationError(
            f"--phase34-output-dir must be {DEFAULT_PHASE34_OUTPUT.as_posix()}"
        )
    if output != DEFAULT_OUTPUT:
        raise VerificationError(
            f"--output-dir must be {DEFAULT_OUTPUT.as_posix()}")
    phase34_resolved = (root / phase34).resolve(strict=False)
    output_resolved = (root / output).resolve(strict=False)
    if phase34_resolved == output_resolved or phase34_resolved in output_resolved.parents or output_resolved in phase34_resolved.parents:
        raise VerificationError("input and output roots must not overlap")
    for relative_path, label in ((phase34, "--phase34-output-dir"),
                                 (output, "--output-dir")):
        current = root
        for part in relative_path.parts:
            current = current / part
            if current.is_symlink():
                raise VerificationError(f"{label} contains a symlink escape")
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
    schema = contract.get("audit_link_schema")
    if not isinstance(
            schema, dict) or schema.get("kinds") != AUDIT_KINDS or schema.get(
                "required_fields") != AUDIT_FIELDS:
        raise VerificationError("Phase 35 audit link schema is invalid")


def load_contract(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_PATH)
    validate_contract(contract)
    scan_security(contract,
                  CONTRACT_PATH.as_posix(),
                  allow_contract_vocabulary=True)
    return contract


def validate_phase34_manifest(contract: dict[str, Any],
                              manifest: dict[str, Any]) -> None:
    validate_exact_fields(manifest, PHASE34_MANIFEST_FIELDS,
                          "Phase 34 manifest")
    scan_security(manifest, "Phase 34 manifest")
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
            raise VerificationError(
                f"Phase 34 manifest {field} is stale, malformed, or lifecycle-mismatched"
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
        scan_security(payload,
                      artifact,
                      allow_contract_vocabulary=True)
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


def evaluate_verdict(facts: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(facts, dict):
        return {
            "cutover_verdict": "blocked",
            "reason_codes": ["unknown-input"],
            "active_exception_ids": []
        }
    readiness = facts.get("readiness_state")
    raw_reasons = facts.get("reason_codes")
    active_ids = facts.get("active_exception_ids")
    exceptions = facts.get("exceptions")
    if readiness not in {
            "blocked", "unblocked"
    } or not isinstance(raw_reasons, list) or not isinstance(
            active_ids, list) or not isinstance(exceptions, list):
        return {
            "cutover_verdict": "blocked",
            "reason_codes": ["unknown-input"],
            "active_exception_ids": []
        }
    reasons = sorted({
        str(reason)
        for reason in raw_reasons if isinstance(reason, str) and reason
    })
    exception_by_id = {
        row.get("decision_id"): row
        for row in exceptions
        if isinstance(row, dict) and isinstance(row.get("decision_id"), str)
    }
    exception_invalid = False
    for decision_id in active_ids:
        maybe_exception = exception_by_id.get(decision_id)
        if maybe_exception is None:
            exception_invalid = True
            continue
        if (maybe_exception.get("decision_value") != "approve"
                or maybe_exception.get("validation_state") != "valid"
                or maybe_exception.get("active") is not True
                or maybe_exception.get("exact_scope") is not True):
            exception_invalid = True
    if set(exception_by_id) != set(active_ids):
        exception_invalid = True
    if exception_invalid:
        reasons.append("exception-invalid")
    reasons = sorted(set(reasons))
    if readiness != "unblocked" or reasons:
        if readiness == "blocked" and not reasons:
            reasons.append("readiness-blocked")
        verdict = "blocked"
    elif active_ids:
        verdict = "approved-with-exceptions"
    else:
        verdict = "approved"
    return {
        "cutover_verdict": verdict,
        "reason_codes": sorted(set(reasons)),
        "active_exception_ids":
        sorted(set(str(value) for value in active_ids)),
    }


def build_route(verdict: str,
                follow_up_scope: list[dict[str, Any]]) -> dict[str, Any]:
    approved = verdict == "approved"
    return {
        "artifact_name": "phase35-next-milestone-route",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "route": "production-cutover-planning"
        if approved else "targeted-blocker-repair",
        "source_verdict": verdict,
        "follow_up_scope": [] if approved else follow_up_scope,
        "requires_fresh_cutover_decision": not approved,
        "planning_only": True,
        "production_actions_authorized": False,
    }


def stable_link_id(kind: str, target_id: str, target_ref: str) -> str:
    safe_target = re.sub(r"[^a-z0-9]+", "-", target_id.casefold()).strip("-")
    if safe_target:
        return f"audit-{kind}-{safe_target}"
    digest = hashlib.sha256(f"{kind}\0{target_ref}".encode()).hexdigest()[:16]
    return f"audit-{kind}-{digest}"


def derive_audit_links(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    links = []
    for source in sources:
        kind = str(source.get("kind") or "")
        target_id = str(source.get("target_id") or "")
        target_ref = str(source.get("target_ref") or "")
        lifecycle = str(source.get("source_phase_lifecycle_id") or "")
        verdict_effect = str(source.get("verdict_effect") or "")
        if kind not in AUDIT_KINDS or not target_id or not lifecycle or not verdict_effect:
            raise VerificationError("audit source is malformed")
        validate_ref(target_ref, f"{kind}.target_ref")
        link = {
            "link_id": stable_link_id(kind, target_id, target_ref),
            "kind": kind,
            "target_id": target_id,
            "target_ref": target_ref,
            "source_phase_lifecycle_id": lifecycle,
            "verdict_effect": verdict_effect,
        }
        if not target_ref.startswith("external://"):
            digest_source = source.get("digest_source", source)
            link["digest"] = hashlib.sha256(
                canonical_json(digest_source)).hexdigest()
        links.append(link)
    return sorted(links,
                  key=lambda link: (AUDIT_KINDS.index(link["kind"]), link[
                      "target_id"], link["target_ref"]))


def validate_audit_links(expected: list[dict[str, Any]],
                         emitted: list[dict[str, Any]]) -> list[str]:
    reasons: set[str] = set()
    expected_by_id = {row["link_id"]: row for row in expected}
    emitted_ids = [row.get("link_id") for row in emitted]
    emitted_by_id = {row.get("link_id"): row for row in emitted}
    if len(emitted_ids) != len(set(emitted_ids)):
        reasons.add("audit-link-duplicate")
    if set(expected_by_id) - set(emitted_by_id):
        reasons.add("audit-link-missing")
    if set(emitted_by_id) - set(expected_by_id):
        reasons.add("audit-link-extra")
    for link_id in set(expected_by_id) & set(emitted_by_id):
        expected_row = expected_by_id[link_id]
        emitted_row = emitted_by_id[link_id]
        if emitted_row.get("kind") != expected_row.get("kind"):
            reasons.add("audit-link-category-mismatched")
        if emitted_row.get("target_ref") != expected_row.get("target_ref"):
            reasons.add("audit-link-dangling")
        if emitted_row.get("source_phase_lifecycle_id") != expected_row.get(
                "source_phase_lifecycle_id"):
            reasons.add("audit-link-lifecycle-mismatched")
        if emitted_row.get("digest") != expected_row.get("digest"):
            reasons.add("audit-link-digest-mismatched")
    return sorted(reasons)


def matching_decisions(rows: list[dict[str, Any]],
                       blocker_ref: str) -> list[dict[str, Any]]:
    return [
        row for row in rows
        if blocker_ref in row.get("source_row_refs", []) and blocker_ref in
        row.get("linked_blocker_refs", row.get("source_row_refs", []))
    ]


def build_repair_scope(
    blockers: list[dict[str, Any]],
    ledger_rows: list[dict[str, Any]],
    exception_rows: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    scope = []
    reasons: set[str] = set()
    matched_exception_ids: set[str] = set()
    matched_residual_ids: set[str] = set()
    for blocker in sorted(blockers,
                          key=lambda row: str(row.get("row_id", ""))):
        row_id = str(blocker.get("row_id") or "")
        blocker_ref = f"{PHASE32_REGISTER_REF}#{row_id}"
        ledger_matches = [
            row for row in ledger_rows
            if row.get("classification_ref") == blocker_ref
        ]
        if not row_id or len(ledger_matches) != 1:
            reasons.add("route-scope-incomplete")
            continue
        ledger = ledger_matches[0]
        required = ("owner_ref", "required_next_action", "requirement_ids",
                    "affected_gate")
        if any(
                field not in blocker for field in required
        ) or "reason_codes" not in ledger or "readiness_effect" not in ledger:
            reasons.add("route-scope-incomplete")
            continue
        criteria = [
            f"{blocker_ref}/affected_gate",
            f"{blocker_ref}/required_next_action",
            f"{PHASE34_LEDGER_REF}#{ledger['row_id']}/reason_codes",
            f"{PHASE34_LEDGER_REF}#{ledger['row_id']}/readiness_effect",
        ]
        exception_matches = matching_decisions(exception_rows, blocker_ref)
        residual_matches = matching_decisions(residual_rows, blocker_ref)
        for decision in exception_matches:
            decision_id = str(decision.get("decision_id") or "")
            if not decision_id or not decision.get(
                    "expiry_or_review_trigger") or not decision.get(
                        "affected_gates"):
                reasons.add("route-scope-incomplete")
                continue
            matched_exception_ids.add(decision_id)
            criteria.extend([
                f"{PHASE33_EXCEPTION_REGISTER}#{decision_id}/expiry_or_review_trigger",
                f"{PHASE33_EXCEPTION_REGISTER}#{decision_id}/affected_gates",
            ])
        for decision in residual_matches:
            decision_id = str(decision.get("decision_id") or "")
            if not decision_id or "follow_up_refs" not in decision or not decision.get(
                    "affected_gates"):
                reasons.add("route-scope-incomplete")
                continue
            matched_residual_ids.add(decision_id)
            criteria.extend([
                f"{PHASE33_RESIDUAL_REGISTER}#{decision_id}/follow_up_refs",
                f"{PHASE33_RESIDUAL_REGISTER}#{decision_id}/affected_gates",
            ])
        scope.append({
            "scope_id":
            f"repair-{row_id}",
            "blocker_refs": [blocker_ref],
            "exception_refs": [
                f"{PHASE33_EXCEPTION_REGISTER}#{row['decision_id']}"
                for row in exception_matches
                if row.get("decision_id") in matched_exception_ids
            ],
            "residual_risk_refs": [
                f"{PHASE33_RESIDUAL_REGISTER}#{row['decision_id']}"
                for row in residual_matches
                if row.get("decision_id") in matched_residual_ids
            ],
            "requirement_ids":
            sorted(set(str(value) for value in blocker["requirement_ids"])),
            "affected_gates": [str(blocker["affected_gate"])],
            "owner_ref":
            str(blocker["owner_ref"]),
            "required_action_ref":
            f"{blocker_ref}/required_next_action",
            "exit_review_criterion_refs":
            criteria,
        })
    all_exception_ids = {
        str(row.get("decision_id") or "")
        for row in exception_rows
    }
    all_residual_ids = {
        str(row.get("decision_id") or "")
        for row in residual_rows
    }
    if all_exception_ids - matched_exception_ids or all_residual_ids - matched_residual_ids:
        reasons.add("route-scope-incomplete")
    return scope, sorted(reasons)


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def project_demotion(
    handoff: Any,
    normalized_records: list[dict[str, Any]],
    dry_run: dict[str, Any],
) -> dict[str, Any]:
    source_refs: list[str] = []
    decision_state = "missing"
    validation_state = "malformed"
    if isinstance(handoff, dict):
        source_refs = sorted({
            ref
            for ref in handoff.get("source_row_refs", [])
            if isinstance(ref, str) and ref.startswith(ALLOWED_REF_PREFIXES)
        })
        required_shape = (
            isinstance(handoff.get("phase"), str)
            and isinstance(handoff.get("phase_lifecycle_id"), str)
            and isinstance(handoff.get("demotion_input_supplied"), bool))
        if not required_shape:
            validation_state = "malformed"
        elif handoff.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
            validation_state = "lifecycle-mismatched"
        elif handoff.get("demotion_input_supplied") is False:
            validation_state = "missing"
        elif handoff.get("demotion_input_supplied") is True and isinstance(
                handoff.get("decision_id"), str):
            matches = [
                row for row in normalized_records
                if row.get("decision_id") == handoff["decision_id"]
            ]
            if len(matches) != 1:
                validation_state = "invalid"
            else:
                decision = matches[0]
                maybe_value = decision.get("decision_value")
                if maybe_value in {"approve", "reject"}:
                    decision_state = str(maybe_value)
                if decision.get("phase_lifecycle_id") != PHASE33_LIFECYCLE_ID:
                    validation_state = "lifecycle-mismatched"
                elif decision.get(
                        "decision_type"
                ) != "reference_demotion" or maybe_value not in {
                        "approve", "reject"
                }:
                    validation_state = "invalid"
                elif decision.get("source_row_refs") != handoff.get(
                        "source_row_refs"):
                    validation_state = "invalid"
                else:
                    maybe_timestamp = parse_timestamp(
                        decision.get("decision_timestamp"))
                    validation_state = "malformed" if maybe_timestamp is None else "valid"
                    if maybe_timestamp is not None and maybe_timestamp < STALE_BEFORE:
                        validation_state = "stale"
    gate_state = dry_run.get("gate_state")
    gate_reasons = dry_run.get("reason_codes")
    if gate_state not in {"blocked", "open"
                          } or not isinstance(gate_reasons, list):
        gate_state = "blocked"
        gate_reasons = ["source-artifact-malformed"]
    expected_dry_validation = {
        "missing": "missing",
        "valid": "valid"
    }.get(validation_state, "invalid")
    expected_dry_decision = decision_state
    if dry_run.get("approval_validation_state"
                   ) != expected_dry_validation or dry_run.get(
                       "approval_decision_state") != expected_dry_decision:
        gate_state = "blocked"
    return {
        "demotion_decision_validation_state":
        validation_state,
        "demotion_decision_state":
        decision_state,
        "demotion_decision_source_refs":
        source_refs,
        "demotion_gate_state":
        gate_state,
        "demotion_gate_reason_codes":
        sorted(set(str(value) for value in gate_reasons)),
    }


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
            receipt,
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
                     name: str) -> dict[str, Any]:
    value = refs.get(name)
    if not isinstance(value, str):
        raise VerificationError(f"Phase 33 register ref missing: {name}")
    validate_ref(value, f"register_refs.{name}")
    path = Path(value)
    if not path.as_posix().startswith("build/ci-evidence/phase33/"):
        raise VerificationError(
            f"Phase 33 register ref has wrong root: {value}")
    payload = load_json(root, path)
    scan_security(payload, value)
    return payload


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
            "Phase 34 packet or ledger lifecycle is mismatched")
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
        raise VerificationError(
            "Phase 33 reached handoff lifecycle or identity is invalid")
    refs = handoff.get("register_refs")
    if not isinstance(refs, dict):
        raise VerificationError(
            "Phase 33 reached handoff register_refs must be an object")
    normalized = reached_register(root, refs, "normalized_decision_records")
    loaded["retained"] = reached_register(
        root, refs, "retained_code_decision_register").get("rows", [])
    loaded["residuals"] = reached_register(
        root, refs, "residual_risk_decision_register").get("rows", [])
    loaded["exceptions"] = reached_register(root, refs,
                                            "exception_decision_register").get(
                                                "rows", [])
    loaded["readiness_handoff"] = reached_register(
        root, refs, "readiness_decision_handoff")
    loaded["demotion_handoff"] = reached_register(root, refs,
                                                  "demotion_decision_handoff")
    loaded["normalized"] = normalized.get("rows", [])
    loaded["blockers"] = loaded["phase32_register"].get("rows", [])
    loaded["receipts"] = loaded["receipts"].get("receipts", [])
    for name in ("retained", "residuals", "exceptions", "normalized",
                 "blockers", "receipts"):
        if not isinstance(loaded[name], list) or not all(
                isinstance(row, dict) for row in loaded[name]):
            raise VerificationError(f"{name} must contain object rows")
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
    if not isinstance(links, list) or validate_audit_links(links, links):
        raise VerificationError("Phase 35 audit index is invalid")
    expected_report = render_report(decision, route, links)
    if report != expected_report:
        raise VerificationError(
            "Phase 35 Markdown projection drifted from JSON")


def write_bundle(
    root: Path,
    relative_output: Path,
    contract: dict[str, Any],
    phase34_contract: dict[str, Any],
    phase34_manifest: dict[str, Any],
    source: dict[str, Any],
) -> None:
    output = root / relative_output
    reset_output(output)
    links = derive_audit_links(audit_sources_from_bundle(source))
    link_reasons = validate_audit_links(links, links)
    ledger_rows = source["ledger"]["rows"]
    readiness_state = str(source["packet"].get("readiness_state") or "blocked")
    upstream_reasons = [
        str(reason) for reason in source["packet"].get("reason_codes", [])
    ]
    reason_map = {
        "required-row-missing": "coverage-incomplete",
        "duplicate-row": "source-artifact-duplicate",
        "dangling-row-ref": "source-ref-failed",
        "redaction-failed": "redaction-failed",
        "source-ref-failed": "source-ref-failed",
        "secret-tainted": "secret-tainted",
        "lifecycle-mismatched": "source-artifact-lifecycle-mismatched",
        "unsafe-ref": "unsafe-ref",
        "unknown-classification": "unknown-input",
        "underclassified": "underclassified",
        "exception-uncovered": "exception-invalid",
        "readiness-input-invalid": "readiness-blocked",
    }
    reasons = sorted({
        reason_map.get(reason, "readiness-blocked")
        for reason in upstream_reasons
    } | set(link_reasons))
    active_exceptions = [{
        "decision_id": row["decision_id"],
        "decision_value": row.get("decision_value"),
        "validation_state": "valid",
        "active": row.get("coverage_state") == "approved-exception",
        "exact_scope": True,
    } for row in source["exceptions"]
                         if row.get("decision_value") == "approve"]
    active_ids = [
        row["decision_id"] for row in active_exceptions if row["active"]
    ]
    verdict = evaluate_verdict({
        "readiness_state": readiness_state,
        "reason_codes": reasons,
        "active_exception_ids": active_ids,
        "exceptions": active_exceptions,
    })
    scope, scope_reasons = build_repair_scope(
        source["blockers"],
        ledger_rows,
        source["exceptions"],
        source["residuals"],
    )
    final_reasons = sorted(set(verdict["reason_codes"]) | set(scope_reasons))
    if final_reasons:
        verdict["cutover_verdict"] = "blocked"
        verdict["reason_codes"] = final_reasons
    route = build_route(verdict["cutover_verdict"], scope)
    demotion = project_demotion(source["demotion_handoff"],
                                source["normalized"], source["dry_run"])
    counts = {
        kind: sum(link["kind"] == kind for link in links)
        for kind in AUDIT_KINDS
    }
    blocker_ids = sorted(
        str(row.get("row_id")) for row in source["blockers"]
        if row.get("row_id"))
    decision = {
        "artifact_name": "phase35-cutover-decision",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "requirement_ids": REQUIREMENTS,
        "cutover_verdict": verdict["cutover_verdict"],
        "reason_codes": verdict["reason_codes"],
        "readiness_state": readiness_state,
        "readiness_result_ref":
        "build/ci-evidence/phase34/final-readiness-packet.json",
        "active_exception_ids": verdict["active_exception_ids"],
        "blocker_ids": blocker_ids,
        "audit_link_index_ref":
        "build/ci-evidence/phase35/cutover-audit-link-index.json",
        "audit_link_counts_by_kind": counts,
        **demotion,
        "route_ref": "build/ci-evidence/phase35/next-milestone-route.json",
        "raw_evidence_consumed": False,
    }
    index = {
        "artifact_name": "phase35-cutover-audit-link-index",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "link_count": len(links),
        "counts_by_kind": counts,
        "links": links,
    }
    manifest = {
        "artifact_name": "phase35-cutover-decision-artifact",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "generated_at_utc": utc_now(),
        "output_root": relative_output.as_posix(),
        "generated_artifacts": GENERATED_ARTIFACTS,
        "source_manifest_ref":
        "build/ci-evidence/phase34/final-readiness-run-manifest.json",
        "raw_evidence_consumed": False,
    }
    write_json(output / "cutover-decision-run-manifest.json", manifest)
    write_json(output / "cutover-audit-link-index.json", index)
    write_json(output / "cutover-decision.json", decision)
    write_json(output / "next-milestone-route.json", route)
    (output / "redacted-cutover-decision-report.md").write_text(
        render_report(decision, route, links), encoding="utf-8")
    write_json(
        output /
        "contract-snapshots/phase35_cutover_decision_artifact_contract.json",
        contract)
    write_json(
        output /
        "contract-snapshots/phase34_final_readiness_demotion_dry_run_contract.json",
        phase34_contract)
    write_json(
        output /
        "contract-snapshots/phase34-final-readiness-run-manifest.json",
        phase34_manifest)
    validate_generated_outputs(output)


def run_quick(root: Path, phase34_arg: str, output_arg: str) -> None:
    phase34, output = validate_paths(root, phase34_arg, output_arg)
    contract = load_contract(root)
    source, phase34_contract = load_bundle(root, phase34, contract)
    manifest = load_json(root, phase34 / "final-readiness-run-manifest.json")
    write_bundle(root, output, contract, phase34_contract, manifest, source)
    run_security_scan(root, output.as_posix())


def run_security_scan(root: Path,
                      output_arg: str | Path = DEFAULT_OUTPUT) -> None:
    output = repo_relative(output_arg, "--output-dir")
    if output != DEFAULT_OUTPUT:
        raise VerificationError(
            f"--output-dir must be {DEFAULT_OUTPUT.as_posix()}")
    full_output = root / output
    if not full_output.exists():
        print(f"no Phase 35 outputs to scan at {output.as_posix()}")
        return
    if full_output.is_symlink() or not full_output.is_dir():
        raise VerificationError(
            "Phase 35 output root contains a symlink escape")
    for artifact in GENERATED_ARTIFACTS:
        path = full_output / artifact
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            payload = json.loads(text)
            if artifact.startswith("contract-snapshots/"):
                if not isinstance(payload, dict):
                    raise VerificationError(
                        f"{artifact} must contain an object")
                validate_snapshot(artifact, payload)
            else:
                scan_security(payload, artifact)
        else:
            for pattern in FORBIDDEN_TEXT:
                if pattern.search(text):
                    raise VerificationError(
                        f"{artifact} contains forbidden text")
    print(f"Phase 35 security scan passed for {output.as_posix()}")


def shell_case_commands(text: str, name: str) -> list[str] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{name})":
            continue
        commands = []
        for body in lines[index + 1:]:
            stripped = body.strip()
            if stripped == ";;":
                return commands
            if stripped.startswith("python3 "):
                commands.append(stripped)
    return None


def required_wiring_strings() -> dict[str, Any]:
    return {
        "tools_bazel": [
            "phase35_source_ref_manifests",
            "phase35_verify",
            "phase35_verify_tests",
            "manifests/phase31_final_evidence_intake_contract.json",
            "manifests/phase32_blocker_register_triage_contract.json",
            "manifests/phase33_maintainer_decision_inputs_contract.json",
            "manifests/phase34_final_readiness_demotion_dry_run_contract.json",
            "manifests/phase35_cutover_decision_artifact_contract.json",
            "phase35_cutover_decision_artifact.py",
            "phase35_cutover_decision_artifact_test.py",
            "//:phase35_cutover_decision_artifact_docs",
        ],
        "root_bazel": [
            "phase35_cutover_decision_artifact_docs",
            "phase35_verify",
            "phase35_verify_tests",
            ".planning/phases/35-cutover-decision-artifact/35-CONTEXT.md",
            ".planning/phases/35-cutover-decision-artifact/35-RESEARCH.md",
            ".planning/phases/35-cutover-decision-artifact/35-VALIDATION.md",
            ".planning/phases/35-cutover-decision-artifact/35-01-PLAN.md",
        ],
        "workflow": ["phase35_verify_tests)", "phase35_verify)"],
        "just": [
            "phase35-verify:",
            "bazel run //tools/bazel:phase35_verify_tests",
            "bazel run //tools/bazel:phase35_verify",
        ],
    }


def check_wiring(root: Path) -> None:
    expected = required_wiring_strings()
    files = {
        "tools_bazel": "tools/bazel/BUILD.bazel",
        "root_bazel": "BUILD.bazel",
        "workflow": "tools/bazel/rust_workflow.sh",
        "just": "justfile",
    }
    errors = []
    for group, path_text in files.items():
        path = root / path_text
        if not path.is_file():
            errors.append(f"missing required file: {path_text}")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in expected[group]:
            if snippet not in text:
                errors.append(f"{path_text} missing {snippet}")
    workflow_text = (root / files["workflow"]).read_text(encoding="utf-8")
    if shell_case_commands(workflow_text,
                           "phase35_verify") != PHASE35_VERIFY_COMMANDS:
        errors.append(
            "tools/bazel/rust_workflow.sh phase35_verify command order is invalid"
        )
    if shell_case_commands(workflow_text,
                           "phase35_verify_tests") != PHASE35_TEST_COMMANDS:
        errors.append(
            "tools/bazel/rust_workflow.sh phase35_verify_tests command is invalid"
        )
    just_lines = (root /
                  files["just"]).read_text(encoding="utf-8").splitlines()
    expected_just_lines = [
        expected["just"][0], f"    {expected['just'][1]}",
        f"    {expected['just'][2]}"
    ]
    if not any(just_lines[index:index + 3] == expected_just_lines
               for index in range(len(just_lines) - 2)):
        errors.append(
            "justfile phase35-verify recipe or command order is invalid")
    if errors:
        raise VerificationError("\n".join(errors))
    print("Phase 35 wiring passed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the Phase 35 cutover decision artifact.")
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--phase34-output-dir",
                        default=DEFAULT_PHASE34_OUTPUT.as_posix())
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT.as_posix())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv or sys.argv[1:])
    try:
        if args.contract_only:
            contract = load_contract(ROOT)
            print(f"{contract['id']} ok")
            return 0
        if args.security_only:
            run_security_scan(ROOT, args.output_dir)
            return 0
        if args.wiring_only:
            check_wiring(ROOT)
            return 0
        if args.quick:
            run_quick(ROOT, args.phase34_output_dir, args.output_dir)
            print("Phase 35 cutover decision artifact quick validation passed")
            return 0
        raise VerificationError("no mode selected")
    except VerificationError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
