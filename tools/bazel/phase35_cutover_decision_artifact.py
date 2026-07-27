#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import stat
import sys
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

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
AUTHORITY_GUARD = Path("build/ci-evidence/.phase35-authority-guard.json")
PREVIOUS_OUTPUT = Path("build/ci-evidence/.phase35-previous")
WORKFLOW_ATTEMPT_SHELL = Path(
    "build/ci-evidence/.phase38-workflow-attempt"
)
AUTHORITY_GUARD_FIELDS = [
    "phase",
    "phase_lifecycle_id",
    "authority_state",
    "reason_code",
    "attempted_output_root",
]
AUTHORITY_GUARD_REASON = "publication-in-progress"
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
PHASE34_LEDGER_REF = "build/ci-evidence/phase34/readiness-coverage-ledger.json"
PHASE33_NORMALIZED_REGISTER = "build/ci-evidence/phase33/normalized-decision-records.json"
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
SOURCE_FAILURE_ARTIFACTS = [
    "cutover-decision-run-manifest.json",
    "cutover-decision.json",
    "next-milestone-route.json",
]
SOURCE_FAILURE_MANIFEST_FIELDS = [
    "artifact_name",
    "phase",
    "phase_lifecycle_id",
    "generation_state",
    "output_root",
    "generated_artifacts",
    "source_manifest_ref",
    "source_failure_reason_codes",
    "raw_evidence_consumed",
]
SOURCE_FAILURE_REASON_CODES = [
    "source-artifact-missing",
    "source-artifact-malformed",
    "source-artifact-stale",
    "source-artifact-lifecycle-mismatched",
    "secret-tainted",
    "unsafe-ref",
    "source-ref-failed",
]
SAFE_SOURCE_FAILURE_REASONS = set(SOURCE_FAILURE_REASON_CODES)
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
    "artifact_name",
    "audit_link_failure_modes",
    "audit_link_schema",
    "authority_boundaries",
    "authority_guard",
    "blocked_reason_codes",
    "cutover_decision_fields",
    "default_behavior",
    "demotion_projection",
    "generated_artifacts",
    "id",
    "output_root",
    "phase",
    "phase_lifecycle_id",
    "repair_scope_fields",
    "repair_scope_ref_policy",
    "requirement_ids",
    "route_enum",
    "route_fields",
    "route_semantics",
    "route_truth_table",
    "schema_version",
    "security",
    "source_contract",
    "source_failure_behavior",
    "source_lifecycle_ids",
    "verdict_enum",
    "verdict_truth_table",
    "verification_commands",
}
PHASE34_CONTRACT_FIELDS = {
    "artifact_name",
    "blocked_reason_codes",
    "decision_domain_policy",
    "default_behavior",
    "demotion_dry_run_schema",
    "generated_artifacts",
    "hard_blocker_problem_kinds",
    "id",
    "io_validation_responsibilities",
    "ledger_schema",
    "output_root",
    "phase",
    "phase_lifecycle_id",
    "prohibited_output_markers",
    "prohibited_semantics",
    "pure_evaluator_outputs",
    "requirement_ids",
    "schema_version",
    "source_contracts",
    "source_inputs",
    "source_failure_policy",
    "sparse_blocker_overlay_policy",
    "test_command",
    "verification_commands",
}
PHASE34_MANIFEST_FIELDS = {
    "accepted_receipt_snapshot_ref",
    "artifact_name",
    "generated_artifacts",
    "generated_at_utc",
    "output_root",
    "phase",
    "phase_lifecycle_id",
    "phase33_register_digests",
    "raw_evidence_consumed",
    "snapshot_refs",
    "source_refs",
}
PHASE33_REGISTER_NAMES = {
    "decision_validation_report",
    "demotion_decision_handoff",
    "exception_decision_register",
    "normalized_decision_records",
    "readiness_decision_handoff",
    "residual_risk_decision_register",
    "retained_code_decision_register",
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
    "python3 tools/bazel/phase35_cutover_decision_artifact.py --wiring-only",
    "run_phase38_coordinator",
]
PHASE35_TEST_COMMANDS = [
    "python3 tools/bazel/phase35_cutover_decision_artifact_test.py",
]


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
        maybe_timestamp = parse_timestamp(
            maybe_exception.get("decision_timestamp"))
        valid = (maybe_exception.get("decision_type") == "exception"
                 and maybe_exception.get("decision_value") == "approve"
                 and maybe_exception.get("phase_lifecycle_id")
                 == PHASE33_LIFECYCLE_ID and maybe_timestamp is not None
                 and maybe_timestamp >= STALE_BEFORE and isinstance(
                     maybe_exception.get("maintainer_identity_ref"), str)
                 and bool(maybe_exception["maintainer_identity_ref"])
                 and isinstance(maybe_exception.get("maintainer_role"), str)
                 and bool(maybe_exception["maintainer_role"])
                 and isinstance(maybe_exception.get("owner_signoff_ref"), str)
                 and bool(maybe_exception["owner_signoff_ref"])
                 and isinstance(maybe_exception.get("scope"), str)
                 and bool(maybe_exception["scope"])
                 and maybe_exception.get("linked_blocker_refs")
                 == maybe_exception.get("source_row_refs")
                 and bool(maybe_exception.get("affected_gates"))
                 and bool(maybe_exception.get("expiry_or_review_trigger")))
        if not valid:
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


def resolve_audit_target(root: Path, target_ref: str) -> Any:
    validate_ref(target_ref, "audit target_ref")
    path_text, separator, fragment = target_ref.partition("#")
    payload = load_json(root, Path(path_text))
    scan_security(payload, target_ref)
    if not separator:
        return payload
    if not fragment or "/" in fragment:
        raise VerificationError(
            f"audit target fragment is invalid: {target_ref}")
    for collection_name in ("rows", "receipts", "blockers"):
        rows = payload.get(collection_name)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            candidate = row.get("receipt", row)
            if not isinstance(candidate, dict):
                continue
            identities = {
                str(candidate.get(field) or "")
                for field in ("row_id", "decision_id", "submission_id")
            }
            if fragment in identities:
                return candidate
    raise VerificationError(f"audit target fragment is dangling: {target_ref}")


def validate_resolved_audit_links(root: Path,
                                  links: list[dict[str, Any]]) -> list[str]:
    reasons: set[str] = set()
    for link in links:
        target_ref = link.get("target_ref")
        if not isinstance(target_ref, str):
            reasons.add("audit-link-dangling")
            continue
        if target_ref.startswith("external://"):
            continue
        try:
            resolved = resolve_audit_target(root, target_ref)
        except VerificationError:
            reasons.add("audit-link-dangling")
            continue
        expected_digest = hashlib.sha256(canonical_json(resolved)).hexdigest()
        if link.get("digest") != expected_digest:
            reasons.add("audit-link-digest-mismatched")
    return sorted(reasons)


def referenced_decisions(
    ledger: dict[str, Any],
    ref_field: str,
    rows: list[dict[str, Any]],
    blocker_ref: str,
    reasons: set[str],
) -> list[dict[str, Any]]:
    refs = ledger.get(ref_field, [])
    if not isinstance(refs, list):
        reasons.add("route-scope-incomplete")
        return []
    prefix = f"{PHASE33_NORMALIZED_REGISTER}#"
    decision_ids = []
    for ref in refs:
        if not isinstance(
                ref,
                str) or not ref.startswith(prefix) or not ref[len(prefix):]:
            reasons.add("route-scope-incomplete")
            continue
        decision_ids.append(ref[len(prefix):])
    row_by_id = {
        str(row.get("decision_id") or ""): row
        for row in rows if row.get("decision_id")
    }
    if len(row_by_id) != len(rows) or len(
            set(decision_ids)) != len(decision_ids):
        reasons.add("route-scope-incomplete")
    matches = []
    for decision_id in sorted(set(decision_ids)):
        maybe_decision = row_by_id.get(decision_id)
        if maybe_decision is None or blocker_ref not in maybe_decision.get(
                "source_row_refs",
            []) or blocker_ref not in maybe_decision.get(
                "linked_blocker_refs", maybe_decision.get(
                    "source_row_refs", [])):
            reasons.add("route-scope-incomplete")
            continue
        matches.append(maybe_decision)
    return matches


def build_repair_scope(
    blockers: list[dict[str, Any]],
    ledger_rows: list[dict[str, Any]],
    exception_rows: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    scope = []
    reasons: set[str] = set()
    blocker_by_ref = {
        f"{PHASE32_REGISTER_REF}#{row.get('row_id')}": row
        for row in blockers if row.get("row_id")
    }
    route_rows = [
        row for row in ledger_rows if row.get("readiness_effect") == "blocked"
        or row.get("coverage_state") == "exception-covered"
    ]
    if not route_rows:
        reasons.add("route-scope-incomplete")
    for ledger in sorted(route_rows,
                         key=lambda row: str(row.get("row_id", ""))):
        ledger_row_id = str(ledger.get("row_id") or "")
        ledger_ref = f"{PHASE34_LEDGER_REF}#{ledger_row_id}"
        classification_ref = str(ledger.get("classification_ref") or "")
        maybe_blocker = blocker_by_ref.get(classification_ref)
        if not ledger_row_id:
            reasons.add("route-scope-incomplete")
            continue
        if ("reason_codes" not in ledger
                or not isinstance(ledger.get("requirement_ids"), list)
                or not isinstance(ledger.get("affected_gates"), list)):
            reasons.add("route-scope-incomplete")
            continue
        if maybe_blocker is None and classification_ref:
            reasons.add("route-scope-incomplete")
            continue
        if maybe_blocker is None:
            source_stream = re.sub(
                r"[^a-z0-9-]+", "-",
                str(ledger.get("source_stream") or "unknown").casefold())
            blocker_refs = [ledger_ref]
            owner_ref = f"owner://phase34/{source_stream}"
            required_action_ref = f"{ledger_ref}/source_ref"
            criteria = [
                f"{ledger_ref}/source_ref",
                f"{ledger_ref}/reason_codes",
                f"{ledger_ref}/readiness_effect",
            ]
        else:
            required = ("owner_ref", "required_next_action", "requirement_ids",
                        "affected_gate")
            if any(field not in maybe_blocker for field in required):
                reasons.add("route-scope-incomplete")
                continue
            blocker_refs = [ledger_ref, classification_ref]
            owner_ref = str(maybe_blocker["owner_ref"])
            required_action_ref = f"{classification_ref}/required_next_action"
            criteria = [
                f"{classification_ref}/affected_gate",
                f"{classification_ref}/required_next_action",
                f"{ledger_ref}/reason_codes",
                f"{ledger_ref}/readiness_effect",
            ]
        exception_matches = referenced_decisions(
            ledger,
            "exception_decision_refs",
            exception_rows,
            classification_ref,
            reasons,
        )
        residual_matches = referenced_decisions(
            ledger,
            "residual_risk_decision_refs",
            residual_rows,
            classification_ref,
            reasons,
        )
        if ledger.get("coverage_state"
                      ) == "exception-covered" and not exception_matches:
            reasons.add("route-scope-incomplete")
        valid_exception_matches = []
        for decision in exception_matches:
            decision_id = str(decision.get("decision_id") or "")
            if not decision_id or not decision.get(
                    "expiry_or_review_trigger") or not decision.get(
                        "affected_gates"):
                reasons.add("route-scope-incomplete")
                continue
            valid_exception_matches.append(decision)
            criteria.extend([
                f"{PHASE33_EXCEPTION_REGISTER}#{decision_id}/expiry_or_review_trigger",
                f"{PHASE33_EXCEPTION_REGISTER}#{decision_id}/affected_gates",
            ])
        valid_residual_matches = []
        for decision in residual_matches:
            decision_id = str(decision.get("decision_id") or "")
            if not decision_id or "follow_up_refs" not in decision or not decision.get(
                    "affected_gates"):
                reasons.add("route-scope-incomplete")
                continue
            valid_residual_matches.append(decision)
            criteria.extend([
                f"{PHASE33_RESIDUAL_REGISTER}#{decision_id}/follow_up_refs",
                f"{PHASE33_RESIDUAL_REGISTER}#{decision_id}/affected_gates",
            ])
        scope.append({
            "scope_id":
            f"repair-{ledger_row_id}",
            "blocker_refs":
            blocker_refs,
            "exception_refs": [
                f"{PHASE33_EXCEPTION_REGISTER}#{row['decision_id']}"
                for row in valid_exception_matches
            ],
            "residual_risk_refs": [
                f"{PHASE33_RESIDUAL_REGISTER}#{row['decision_id']}"
                for row in valid_residual_matches
            ],
            "requirement_ids":
            sorted(
                set(str(value)
                    for value in ledger.get("requirement_ids", []))),
            "affected_gates":
            sorted(
                set(str(value) for value in ledger.get("affected_gates", []))),
            "owner_ref":
            owner_ref,
            "required_action_ref":
            required_action_ref,
            "exit_review_criterion_refs":
            criteria,
        })
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
        gate_reasons.append("source-artifact-malformed")
    if validation_state != "valid" or decision_state != "approve":
        gate_state = "blocked"
        if not gate_reasons:
            gate_reasons.append("approval-missing" if validation_state ==
                                "missing" else "approval-invalid")
    if dry_run.get("readiness_state") != "unblocked":
        gate_state = "blocked"
        gate_reasons.append("readiness-input-invalid")
    if gate_reasons:
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
        sorted(
            set(
                str(value) for value in gate_reasons
                if isinstance(value, str) and value)),
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
        for row in ledger_rows
        if row.get("readiness_effect") == "blocked"
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
    if not isinstance(payload, dict) or list(payload) != AUTHORITY_GUARD_FIELDS:
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
        if (
            index < len(WORKFLOW_ATTEMPT_SHELL.parts) - 1
            and not stat.S_ISDIR(status.st_mode)
        ):
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
        raise VerificationError(
            "Phase 35 recoverable backup already exists")

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
                "unable to recover Phase 35 staged publication") from recovery_error
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


def validate_installed_full_bundle(output: Path) -> None:
    validate_generated_outputs(output)
    try:
        decision = json.loads(
            (output / "cutover-decision.json").read_text(encoding="utf-8"))
        route = json.loads(
            (output /
             "next-milestone-route.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError) as error:
        raise VerificationError(
            "Phase 35 installed decision is unreadable") from error
    verdict = decision.get("cutover_verdict")
    follow_up_scope = route.get("follow_up_scope")
    if verdict not in {"approved", "blocked", "approved-with-exceptions"
                       } or not isinstance(follow_up_scope, list):
        raise VerificationError(
            "Phase 35 installed verdict or route is invalid")
    if route != build_route(str(verdict), follow_up_scope):
        raise VerificationError(
            "Phase 35 installed route contradicts its verdict")
    validation_state = decision.get("demotion_decision_validation_state")
    decision_state = decision.get("demotion_decision_state")
    gate_state = decision.get("demotion_gate_state")
    gate_reasons = decision.get("demotion_gate_reason_codes")
    if (validation_state not in {
            "missing", "valid", "invalid", "malformed", "stale",
            "lifecycle-mismatched"
    } or decision_state not in {"missing", "approve", "reject"}
            or gate_state not in {"blocked", "open"}
            or not isinstance(gate_reasons, list)
            or (gate_state == "open"
                and (validation_state != "valid"
                     or decision_state != "approve" or gate_reasons))):
        raise VerificationError(
            "Phase 35 installed demotion projection is invalid")


def write_bundle(
    root: Path,
    relative_output: Path,
    contract: dict[str, Any],
    phase34_contract: dict[str, Any],
    phase34_manifest: dict[str, Any],
    source: dict[str, Any],
    *,
    staging_output: Path | None = None,
) -> None:
    output = staging_output or root / relative_output
    reset_output(output)
    expected_links = derive_audit_links(audit_sources_from_bundle(source))
    index_links = [dict(link) for link in expected_links]
    link_reasons = sorted(
        set(validate_audit_links(expected_links, index_links))
        | set(validate_resolved_audit_links(root, index_links)))
    ledger_rows = source["ledger"]["rows"]
    readiness_state = str(source["packet"].get("readiness_state") or "blocked")
    upstream_reasons = cutover_reason_codes(readiness_state, ledger_rows)
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
    active_ids = active_exception_ids_from_ledger(ledger_rows)
    active_exceptions = [
        row for row in source["exceptions"]
        if row.get("decision_id") in active_ids
    ]
    verdict = evaluate_verdict({
        "readiness_state": readiness_state,
        "reason_codes": reasons,
        "active_exception_ids": active_ids,
        "exceptions": active_exceptions,
    })
    if verdict["cutover_verdict"] == "approved":
        scope, scope_reasons = [], []
    else:
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
        kind: sum(link["kind"] == kind for link in index_links)
        for kind in AUDIT_KINDS
    }
    blocker_ids = sorted(
        str(row.get("row_id")) for row in ledger_rows
        if row.get("row_id") and row.get("readiness_effect") == "blocked")
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
        "link_count": len(index_links),
        "counts_by_kind": counts,
        "links": index_links,
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
        render_report(decision, route, index_links), encoding="utf-8")
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
    output = validate_output_path(root, output_arg)
    canonical_output = root / output
    stage: Path | None = None
    try:
        phase34 = validate_source_path(root, phase34_arg, output)
        contract = load_contract(root)
        source, phase34_contract = load_bundle(root, phase34, contract)
        manifest = load_json(root,
                             phase34 / "final-readiness-run-manifest.json")
        stage = create_staging_directory(root, output)
        write_bundle(
            root,
            output,
            contract,
            phase34_contract,
            manifest,
            source,
            staging_output=stage,
        )
    except VerificationError as error:
        publish_authority_guard(root)
        discard_staging_directory(root, stage)
        reason_code = source_failure_reason(error)
        failure_stage = create_staging_directory(root, output)
        try:
            write_source_failure_bundle(output, failure_stage, reason_code)
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
        raise VerificationError("Phase 35 source validation failed",
                                reason_code) from error
    install_staged_bundle(
        root,
        stage,
        canonical_output,
        validate_installed_full_bundle,
    )
    run_security_scan(root, output.as_posix())


def run_security_scan(root: Path,
                      output_arg: str | Path = DEFAULT_OUTPUT) -> None:
    output = repo_relative(output_arg, "--output-dir")
    if output != DEFAULT_OUTPUT:
        raise VerificationError(
            f"--output-dir must be {DEFAULT_OUTPUT.as_posix()}")
    ensure_canonical_authority(root, output)
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
            if (stripped.startswith("python3 ")
                    or stripped == "run_phase38_coordinator"):
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
        print(f"Phase 35 verification failed: {error.reason_code}",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
