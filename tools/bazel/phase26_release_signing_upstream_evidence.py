#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PHASE = "26-release-signing-and-upstream-result-evidence"
PHASE_LIFECYCLE_ID = "26-2026-06-24T13-36-46"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase26_release_signing_upstream_evidence_contract.json")
PHASE20_CONTRACT = Path("tools/bazel/manifests/phase20_release_candidate_artifacts_contract.json")
PHASE20_RELEASE_INPUT_TEMPLATE = Path("tools/bazel/manifests/phase20_release_environment_inputs.template.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase26")
PASS_CAPABLE_PROOF_CLASSES = {"approved-release-run", "external-release-key-evidence"}
NON_PASS_PROOF_CLASSES = {
    "template-only",
    "local-smoke",
    "pending-release-input",
    "release-run-required",
    "external-signing-required",
    "blocked-signing-key-unavailable",
    "release-candidate",
}
REQUIRED_PASS_METADATA = [
    "release_run_id",
    "artifact_refs",
    "operator",
    "timestamp",
    "subject_digests",
    "build_input_identity",
    "retention_refs",
    "verification_outcome",
    "mismatch_class",
    "mismatch_reason",
    "owner_phase",
    "affected_artifact_surface",
    "residual_risk",
]
REQUIRED_SIGNING_METADATA = ["key_identity_ref", "signing_mode"]
FORBIDDEN_FIELD_NAMES = {
    "binary_dump",
    "binary_dump_bytes",
    "credential",
    "credential_value",
    "crash_dump_bytes",
    "firmware_payload_bytes",
    "password",
    "password_value",
    "private_certificate",
    "private_certificate_pem",
    "private_key",
    "raw_firmware_payload",
    "raw_key_bytes",
    "raw_log",
    "raw_log_bytes",
    "raw_logs",
    "secret",
    "secret_value",
    "signing_key_value",
    "signing_payload_bytes",
    "token",
    "token_value",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("certificate-block", re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE)),
    (
        "forbidden-release-evidence-marker",
        re.compile(
            r"\b(private[_-]?key|private[_-]?certificate|raw[_-]?key[_-]?bytes|signing[_-]?key[_-]?value|"
            r"signing[_-]?payload[_-]?bytes|raw[_-]?firmware[_-]?payload|firmware[_-]?payload[_-]?bytes|"
            r"raw[_-]?logs?|binary[_-]?dump|token[_-]?value|password[_-]?value|credential[_-]?value|secret[_-]?value)\b",
            re.IGNORECASE,
        ),
    ),
)


class VerificationError(Exception):
    pass


def read_text(root: Path, path: Path) -> str:
    full_path = root / path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: Path) -> dict[str, Any]:
    try:
        data = json.loads(read_text(root, path))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(f"{path.as_posix()} must contain a top-level object")
    return data


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_list(row: dict[str, Any], field: str, row_name: str) -> list[Any]:
    value = row.get(field)
    if not isinstance(value, list):
        raise VerificationError(f"{row_name} {field} must be a list")
    return value


def require_non_empty_list(row: dict[str, Any], field: str, row_name: str) -> list[Any]:
    values = require_list(row, field, row_name)
    if not values:
        raise VerificationError(f"{row_name} {field} must be non-empty")
    return values


def normalized_field_name(field_name: str) -> str:
    return field_name.replace("-", "_").casefold()


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for label, pattern in FORBIDDEN_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            marker = match.group(0) if match.group(0) else label
            errors.append(f"{path.as_posix()} contains forbidden release evidence marker: {marker}")
    if errors:
        raise VerificationError("\n".join(errors))


def reject_forbidden_field_names(value: Any, path: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(key for key in value if normalized_field_name(key) in FORBIDDEN_FIELD_NAMES)
        if forbidden:
            raise VerificationError(f"{path} contains forbidden evidence fields: {', '.join(forbidden)}")
        for key, child in value.items():
            reject_forbidden_field_names(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden_field_names(child, f"{path}[{index}]")


def contract_rows(contract: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    rows = contract.get("rows")
    if not isinstance(rows, list):
        raise VerificationError(f"{path.as_posix()} must contain a rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{path.as_posix()} rows[{index}] must be an object")
        parsed_rows.append(row)
    return parsed_rows


def phase20_release_row_ids(phase20_contract: dict[str, Any]) -> list[str]:
    row_ids: list[str] = []
    for row in contract_rows(phase20_contract, PHASE20_CONTRACT):
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise VerificationError(f"{PHASE20_CONTRACT.as_posix()} contains a release row without an id")
        row_ids.append(row_id)
    return row_ids


def phase20_status_vocabulary(phase20_contract: dict[str, Any]) -> set[str]:
    values = phase20_contract.get("status_vocabulary")
    if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
        raise VerificationError(f"{PHASE20_CONTRACT.as_posix()} status_vocabulary must contain strings")
    return set(values)


def phase20_proof_class_vocabulary(phase20_contract: dict[str, Any]) -> set[str]:
    values = phase20_contract.get("proof_class_vocabulary")
    if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
        raise VerificationError(f"{PHASE20_CONTRACT.as_posix()} proof_class_vocabulary must contain strings")
    return set(values)


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    reject_forbidden_field_names(contract, CONTRACT_MANIFEST.as_posix())
    phase20_contract = load_json(root, PHASE20_CONTRACT)
    phase20_row_ids = phase20_release_row_ids(phase20_contract)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase26_release_signing_upstream_evidence_contract",
        "artifact_name": "phase26-release-signing-upstream-evidence",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}")
    source_contracts = contract.get("source_contracts")
    if not isinstance(source_contracts, list):
        errors.append(f"{CONTRACT_MANIFEST.as_posix()} source_contracts must be a list")
    else:
        for index, source_contract in enumerate(source_contracts):
            if not isinstance(source_contract, dict):
                errors.append(f"source_contracts[{index}] must be an object")
                continue
            source_path = source_contract.get("path")
            if not isinstance(source_path, str) or not source_path:
                errors.append(f"source_contracts[{index}] path must be a non-empty string")
                continue
            relative_path = Path(source_path)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                errors.append(f"source_contracts[{index}] path must be repo-relative: {source_path}")
                continue
            if not (root / relative_path).exists():
                errors.append(f"source_contracts[{index}] path does not exist: {source_path}")
    release_policy = contract.get("release_policy")
    if not isinstance(release_policy, dict):
        errors.append(f"{CONTRACT_MANIFEST.as_posix()} release_policy must be an object")
    else:
        if release_policy.get("canonical_phase20_release_row_ids") != phase20_row_ids:
            errors.append("release_policy canonical_phase20_release_row_ids must match Phase 20 rows exactly")
        if set(release_policy.get("pass_capable_proof_classes", [])) != PASS_CAPABLE_PROOF_CLASSES:
            errors.append("release_policy pass_capable_proof_classes must be Phase 26 pass-capable classes")
        non_pass = set(release_policy.get("non_pass_proof_classes", []))
        for proof_class in NON_PASS_PROOF_CLASSES:
            if proof_class not in non_pass:
                errors.append(f"release_policy non_pass_proof_classes missing {proof_class}")
        if release_policy.get("required_pass_metadata") != REQUIRED_PASS_METADATA:
            errors.append("release_policy required_pass_metadata must match Phase 26 pass metadata")
        if release_policy.get("required_signing_metadata_when_phase20_requires_signing") != REQUIRED_SIGNING_METADATA:
            errors.append("release_policy required signing metadata must require key_identity_ref and signing_mode")
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def validate_output_dir(root: Path, output_dir: Path) -> tuple[Path, Path]:
    if output_dir.is_absolute() or ".." in output_dir.parts:
        raise VerificationError(f"--output-dir must be repo-relative under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}")
    try:
        output_dir.relative_to(DEFAULT_OUTPUT_DIR)
    except ValueError as error:
        raise VerificationError(f"--output-dir must stay under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}") from error
    current = root
    for part in output_dir.parts:
        current = current / part
        if current.is_symlink():
            raise VerificationError(f"--output-dir contains a symlink escape risk: {output_dir.as_posix()}")
    full_output_dir = (root / output_dir).resolve(strict=False)
    expected_root = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    try:
        full_output_dir.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(f"--output-dir must resolve under {DEFAULT_OUTPUT_DIR.as_posix()}: {output_dir.as_posix()}") from error
    return output_dir, full_output_dir


def validate_ref(ref: str, allowed_roots: list[str], row_name: str, field: str) -> str:
    if not ref:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    for allowed_root in allowed_roots:
        if allowed_root.startswith("external://") and ref.startswith(allowed_root):
            if ".." in ref or ref.endswith("/"):
                raise VerificationError(f"{row_name} {field} ref is unsafe: {ref}")
            return ref
        if not allowed_root.startswith("external://"):
            relative_path = Path(ref)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                raise VerificationError(f"{row_name} {field} ref escapes allowed roots: {ref}")
            try:
                relative_path.relative_to(Path(allowed_root))
                return ref
            except ValueError:
                continue
    raise VerificationError(f"{row_name} {field} ref must stay under allowed release roots: {ref}")


def validate_ref_list(
    row: dict[str, Any],
    field: str,
    row_name: str,
    allowed_roots: list[str],
    require_nonempty: bool,
) -> list[str]:
    values = require_list(row, field, row_name)
    if require_nonempty and not values:
        raise VerificationError(f"{row_name} {field} must be non-empty")
    refs: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str):
            raise VerificationError(f"{row_name} {field}[{index}] must be a string")
        refs.append(validate_ref(value, allowed_roots, row_name, f"{field}[{index}]"))
    return refs


def validate_subject_digests(row: dict[str, Any], row_name: str, allowed_roots: list[str], errors: list[str]) -> None:
    subject_digests = row.get("subject_digests")
    if not isinstance(subject_digests, list) or not subject_digests:
        errors.append(f"{row_name} subject_digests must be non-empty")
        return
    for index, digest_row in enumerate(subject_digests):
        digest_name = f"{row_name} subject_digests[{index}]"
        if not isinstance(digest_row, dict):
            errors.append(f"{digest_name} must be an object")
            continue
        artifact_ref = digest_row.get("artifact_ref")
        if not isinstance(artifact_ref, str):
            errors.append(f"{digest_name} artifact_ref must be a string")
        else:
            try:
                validate_ref(artifact_ref, allowed_roots, digest_name, "artifact_ref")
            except VerificationError as error:
                errors.append(str(error))
        sha256 = digest_row.get("sha256")
        if not isinstance(sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
            errors.append(f"{digest_name} sha256 must be lowercase SHA-256 hex")


def release_input_rows(root: Path, maybe_path: str | None) -> list[dict[str, Any]]:
    input_path = Path(maybe_path) if maybe_path is not None else PHASE20_RELEASE_INPUT_TEMPLATE
    full_path = input_path if input_path.is_absolute() else root / input_path
    if not full_path.exists():
        raise VerificationError(f"release input file does not exist: {input_path.as_posix()}")
    raw_text = full_path.read_text(encoding="utf-8")
    reject_forbidden_text(input_path, raw_text)
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise VerificationError(f"release input is not valid JSON: {error}") from error
    reject_forbidden_field_names(data, input_path.as_posix())
    rows = data.get("evidence_rows") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise VerificationError("release input must contain an evidence_rows list")
    parsed_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"release input row {index} must be an object")
        parsed_rows.append(row)
    return parsed_rows


def validate_release_row(
    row: dict[str, Any],
    contract_row: dict[str, Any],
    row_name: str,
    status_vocabulary: set[str],
    proof_class_vocabulary: set[str],
    allowed_roots: list[str],
) -> None:
    errors: list[str] = []
    status = require_string(row, "status", row_name)
    proof_class = require_string(row, "proof_class", row_name)
    if status not in status_vocabulary:
        errors.append(f"{row_name} status is invalid: {status}")
    if proof_class not in proof_class_vocabulary and proof_class not in NON_PASS_PROOF_CLASSES:
        errors.append(f"{row_name} proof_class is invalid: {proof_class}")
    if row.get("artifact_surface") and row.get("artifact_surface") != contract_row.get("artifact_surface"):
        errors.append(f"{row_name} artifact_surface does not match contract row {contract_row.get('id')}")
    for field in ["artifact_refs", "retention_refs"]:
        try:
            validate_ref_list(row, field, row_name, allowed_roots, require_nonempty=status == "passed")
        except VerificationError as error:
            errors.append(str(error))
    if status == "passed":
        if proof_class not in PASS_CAPABLE_PROOF_CLASSES:
            errors.append(f"{row_name} cannot pass with proof_class={proof_class!r}; release-candidate cannot pass Phase 26")
        for field in REQUIRED_PASS_METADATA:
            try:
                if field in {"artifact_refs", "retention_refs"}:
                    validate_ref_list(row, field, row_name, allowed_roots, require_nonempty=True)
                elif field == "subject_digests":
                    validate_subject_digests(row, row_name, allowed_roots, errors)
                else:
                    require_string(row, field, row_name)
            except VerificationError as error:
                errors.append(str(error))
        if contract_row.get("signing_metadata_required"):
            for field in REQUIRED_SIGNING_METADATA:
                try:
                    require_string(row, field, row_name)
                except VerificationError as error:
                    errors.append(str(error))
    mismatch_class = row.get("mismatch_class")
    mismatch_values = {"pass", "intentional-delta", "blocker", "deferred-retained-code-issue"}
    if mismatch_class is not None and mismatch_class not in mismatch_values:
        errors.append(f"{row_name} mismatch_class is invalid: {mismatch_class}")
    if errors:
        raise VerificationError("\n".join(errors))


def validate_release_input(root: Path, maybe_path: str | None) -> dict[str, dict[str, Any]]:
    phase20_contract = load_json(root, PHASE20_CONTRACT)
    contract_by_id = {str(row["id"]): row for row in contract_rows(phase20_contract, PHASE20_CONTRACT)}
    expected_ids = phase20_release_row_ids(phase20_contract)
    status_vocabulary = phase20_status_vocabulary(phase20_contract)
    proof_class_vocabulary = phase20_proof_class_vocabulary(phase20_contract)
    release_input_schema = phase20_contract.get("release_input_schema")
    if not isinstance(release_input_schema, dict):
        raise VerificationError(f"{PHASE20_CONTRACT.as_posix()} release_input_schema must be an object")
    allowed_roots = release_input_schema.get("allowed_ref_roots")
    if not isinstance(allowed_roots, list) or not all(isinstance(root_value, str) and root_value for root_value in allowed_roots):
        raise VerificationError("Phase 20 release_input_schema allowed_ref_roots must contain strings")
    parsed_rows: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for index, row in enumerate(release_input_rows(root, maybe_path)):
        row_name = f"release input row {index}"
        try:
            row_id = require_string(row, "id", row_name)
            if row_id not in contract_by_id:
                raise VerificationError(f"{row_name} uses unknown row id: {row_id}")
            if row_id in parsed_rows:
                raise VerificationError(f"{row_name} duplicates row id: {row_id}")
            validate_release_row(
                row,
                contract_by_id[row_id],
                row_name,
                status_vocabulary,
                proof_class_vocabulary,
                allowed_roots,
            )
            parsed_rows[row_id] = dict(row)
        except VerificationError as error:
            errors.append(str(error))
    missing = [row_id for row_id in expected_ids if row_id not in parsed_rows]
    if missing:
        errors.append("release input missing rows: " + ", ".join(missing))
    ordered_ids = list(parsed_rows)
    if not missing and ordered_ids != expected_ids:
        errors.append("release input row order must match Phase 20 canonical rows")
    if errors:
        raise VerificationError("\n".join(errors))
    return parsed_rows


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in [CONTRACT_MANIFEST, PHASE20_RELEASE_INPUT_TEMPLATE]:
        try:
            text = read_text(root, path)
            reject_forbidden_text(path, text)
            reject_forbidden_field_names(json.loads(text), path.as_posix())
        except (json.JSONDecodeError, VerificationError) as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_wiring(root: Path) -> None:
    _ = root
    print("Phase 26 wiring checks are added in the workflow wiring task")


def run_quick(root: Path, output_dir: Path, maybe_release_input: str | None) -> None:
    check_contract(root)
    check_security(root)
    validate_output_dir(root, output_dir)
    validate_release_input(root, maybe_release_input)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 26 release signing and upstream result evidence")
    parser.add_argument("--contract-only", action="store_true", help="validate the Phase 26 contract")
    parser.add_argument("--security-only", action="store_true", help="scan checked-in Phase 26 evidence inputs")
    parser.add_argument("--wiring-only", action="store_true", help="validate Bazel and just workflow wiring")
    parser.add_argument("--quick", action="store_true", help="validate quick Phase 26 inputs and output containment")
    parser.add_argument("--release-input", help="optional sanitized release-manager input JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix(), help="Phase 26 evidence output directory")
    args = parser.parse_args()
    selected_modes = [args.contract_only, args.security_only, args.wiring_only, args.quick]
    if sum(bool(mode) for mode in selected_modes) != 1:
        parser.error("select exactly one verifier mode")
    if args.release_input and not args.quick:
        parser.error("--release-input is only valid with --quick")
    try:
        if args.contract_only:
            check_contract(ROOT)
            print("Phase 26 release signing upstream evidence contract passed")
        elif args.security_only:
            check_contract(ROOT)
            check_security(ROOT)
            print("Phase 26 release signing upstream evidence security scan passed")
        elif args.wiring_only:
            check_wiring(ROOT)
        else:
            run_quick(ROOT, Path(args.output_dir), args.release_input)
            print("Phase 26 release signing upstream evidence quick validation passed")
    except VerificationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
