#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE = "11-parity-pyramid-and-cutover-evidence"
PHASE_LIFECYCLE_ID = "11-2026-06-14T18-48-49"

PARITY_PYRAMID_MANIFEST = Path("tools/bazel/manifests/phase11_parity_pyramid.json")
REQUIREMENT_EVIDENCE_MANIFEST = Path("tools/bazel/manifests/phase11_requirement_evidence.json")
REFERENCE_COMPARISONS_MANIFEST = Path("tools/bazel/manifests/phase11_reference_comparisons.json")
CUTOVER_READINESS_MANIFEST = Path("tools/bazel/manifests/phase11_cutover_readiness.json")
RETAINED_CODE_JUSTIFICATIONS_MANIFEST = Path(
    "tools/bazel/manifests/phase11_retained_code_justifications.json"
)
REQUIREMENTS_FILE = Path(".planning/REQUIREMENTS.md")
VALIDATION_CONTRACT = Path(".planning/phases/11-parity-pyramid-and-cutover-evidence/11-VALIDATION.md")
CUTOVER_RUST = Path("rust/crates/domain/src/cutover.rs")
RUST_DOMAIN_LIB = Path("rust/crates/domain/src/lib.rs")

ALLOWED_PROOF_SCOPES = {
    "local",
    "ci",
    "simulator",
    "hardware-smoke",
    "manual-hardware-required",
    "retained-code-justification",
}
LOCAL_ONLY_EVIDENCE_CLASSES = {
    "rust-unit-test",
    "adapter-contract-test",
    "generated-drift-check",
    "reference-fixture-comparison",
    "source-audit",
    "static-verifier",
}
NON_LOCAL_PROOF_SCOPES = {
    "ci",
    "simulator",
    "hardware-smoke",
    "manual-hardware-required",
    "retained-code-justification",
}
REQUIRED_PYRAMID_ROW_IDS = {
    "pyramid-rust-unit-tests",
    "pyramid-adapter-domain-contract-tests",
    "pyramid-generated-drift-checks",
    "pyramid-reference-fixture-comparisons",
    "pyramid-simulator-flows",
    "pyramid-network-tls-api-checks",
    "pyramid-release-artifact-checks",
    "pyramid-hardware-smoke-manual-gates",
    "pyramid-retained-code-justifications",
}
FORBIDDEN_MARKERS = {
    "password_value",
    "token_value",
    "certificate_bytes",
    "private_key",
    "SIGNING_KEY_VALUE",
    "raw_crash_dump",
    "firmware_payload",
}
OVERCLAIM_STRINGS = {
    "hardware verified locally",
    "simulator passed locally",
    "byte-identical firmware",
    "cutover complete",
    "reference path removed",
}

REQUIRED_REQUIREMENT_ROWS = {
    "req-base-01": "BASE-01",
    "req-base-02": "BASE-02",
    "req-base-03": "BASE-03",
    "req-base-04": "BASE-04",
    "req-bazl-01": "BAZL-01",
    "req-bazl-02": "BAZL-02",
    "req-bazl-03": "BAZL-03",
    "req-bazl-04": "BAZL-04",
    "req-bazl-05": "BAZL-05",
    "req-rust-01": "RUST-01",
    "req-rust-02": "RUST-02",
    "req-rust-03": "RUST-03",
    "req-rust-04": "RUST-04",
    "req-rust-05": "RUST-05",
    "req-core-01": "CORE-01",
    "req-core-02": "CORE-02",
    "req-core-03": "CORE-03",
    "req-core-04": "CORE-04",
    "req-core-05": "CORE-05",
    "req-ifce-01": "IFCE-01",
    "req-ifce-02": "IFCE-02",
    "req-ifce-03": "IFCE-03",
    "req-ifce-04": "IFCE-04",
    "req-ifce-05": "IFCE-05",
    "req-ifce-06": "IFCE-06",
    "req-verf-01": "VERF-01",
    "req-verf-02": "VERF-02",
    "req-verf-03": "VERF-03",
    "req-verf-04": "VERF-04",
    "req-verf-05": "VERF-05",
}
PENDING_REQUIREMENT_IDS = {"BAZL-03", "BAZL-05", "VERF-01", "VERF-03", "VERF-04", "VERF-05"}
REQUIRED_COMPARISON_ROW_IDS = {
    "ref-product-artifacts",
    "ref-generated-resources",
    "ref-storage-migrations",
    "ref-protocol-traces",
    "ref-gcode-behavior-fixtures",
    "ref-ui-display-state-fixtures",
    "ref-network-tls-api-behavior",
    "ref-auxiliary-controller-flows",
    "ref-release-metadata",
}
REQUIRED_CUTOVER_CRITERION_ROW_IDS = {
    "criteria-all-v1-requirements-mapped",
    "criteria-local-verifier-passed",
    "criteria-non-local-gates-identified",
    "criteria-retained-code-justifications-accepted",
    "criteria-intentional-deltas-documented",
    "criteria-overclaim-scan-clean",
    "criteria-reference-demotion-blocked",
}
REQUIRED_RETAINED_CODE_ROW_IDS = {
    "retained-hal-cmsis-vendor",
    "retained-freertos-rtos",
    "retained-marlin-print-core-oracle",
    "retained-lwip-mbedtls-wui",
    "retained-fatfs-littlefs",
    "retained-tinyusb-usb",
    "retained-auxiliary-mmu-modbus",
    "retained-generated-assets-tools",
}
REQUIRED_RUST_API_STRINGS = {
    "CutoverEvidenceRowId",
    "ProofScope",
    "EvidenceClass",
    "CutoverStatus",
    "ReferenceComparisonKind",
    "ReferenceComparisonContract",
    "CutoverCriterion",
    "RetainedCodeDisposition",
}
UNSAFE_RUST_PATTERNS = {
    "unsafe block": "unsafe {",
    "unsafe function": "unsafe fn",
    "unsafe trait": "unsafe trait",
    "unsafe impl": "unsafe impl",
    "unsafe extern": "unsafe extern",
    "unsafe allowance": "#![allow(unsafe_code)]",
    "unsafe item allowance": "#[allow(unsafe_code)]",
}


class VerificationError(Exception):
    pass


def read_text(root: Path, path: str | Path) -> str:
    relative_path = Path(path)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def load_json(root: Path, path: Path) -> dict[str, object]:
    try:
        data = json.loads(read_text(root, path))
    except json.JSONDecodeError as error:
        raise VerificationError(f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(f"{path.as_posix()} must contain a top-level JSON object")
    return data


def is_missing(value: object) -> bool:
    return value in ("", None) or value == [] or value == {}


def require_string(row: dict[str, object], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, object], field: str, row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise VerificationError(f"{row_name} {field} must be a list of strings")
    return value


def require_non_empty_list_of_strings(row: dict[str, object], field: str, row_name: str) -> list[str]:
    values = require_list_of_strings(row, field, row_name)
    if not values:
        raise VerificationError(f"{row_name} {field} must be a non-empty list of strings")
    return values


def require_fields(
    row: dict[str, object],
    fields: list[str],
    row_name: str,
    maybe_empty_fields: set[str] | None = None,
) -> None:
    allowed_empty = maybe_empty_fields or set()
    missing = [field for field in fields if field not in row]
    empty = [field for field in fields if field in row and field not in allowed_empty and is_missing(row[field])]
    if missing or empty:
        parts: list[str] = []
        if missing:
            parts.append("missing required fields: " + ", ".join(missing))
        if empty:
            parts.append("empty required fields: " + ", ".join(empty))
        raise VerificationError(f"{row_name} " + "; ".join(parts))


def require_top_level(root: Path, path: Path, collection_name: str) -> list[dict[str, object]]:
    data = load_json(root, path)
    if data.get("schema_version") != "1":
        raise VerificationError(f"{path.as_posix()} must set schema_version to \"1\"")
    if data.get("phase") != PHASE:
        raise VerificationError(f"{path.as_posix()} must set phase to {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"{path.as_posix()} must set phase_lifecycle_id to {PHASE_LIFECYCLE_ID}"
        )

    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(f"{path.as_posix()} must contain a {collection_name} list")
    parsed_rows: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"{path.as_posix()} {collection_name}[{index}] must be an object")
        parsed_rows.append(row)
    return parsed_rows


def require_exact_row_ids(rows: list[dict[str, object]], expected_ids: set[str], path: Path) -> None:
    actual_ids: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        row_id = row.get("id")
        if not isinstance(row_id, str):
            raise VerificationError(f"{path.as_posix()} row has non-string id: {row_id!r}")
        if row_id in actual_ids:
            duplicates.add(row_id)
        actual_ids.add(row_id)
    missing = sorted(expected_ids - actual_ids)
    extra = sorted(actual_ids - expected_ids)
    details: list[str] = []
    if missing:
        details.append("missing required row IDs: " + ", ".join(missing))
    if extra:
        details.append("has unexpected row IDs: " + ", ".join(extra))
    if duplicates:
        details.append("has duplicate row IDs: " + ", ".join(sorted(duplicates)))
    if details:
        raise VerificationError(f"{path.as_posix()} " + "; ".join(details))


def require_row_id_shape(row_id: str, row_name: str) -> None:
    try:
        encoded = row_id.encode("ascii")
    except UnicodeEncodeError as error:
        raise VerificationError(f"{row_name} id must be printable ASCII") from error
    if len(encoded) > 96:
        raise VerificationError(f"{row_name} id must be at most 96 bytes")
    if any(ord(char) < 32 or ord(char) > 126 for char in row_id):
        raise VerificationError(f"{row_name} id must be printable ASCII")
    if "/" in row_id or "\\" in row_id or ".." in row_id:
        raise VerificationError(f"{row_name} id must be path-free")


def require_source_artifacts(root: Path, row: dict[str, object], row_name: str) -> None:
    source_artifacts = require_non_empty_list_of_strings(row, "source_artifacts", row_name)
    resolved_root = root.resolve()
    for source_artifact in source_artifacts:
        relative_path = Path(source_artifact)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise VerificationError(f"{row_name} source artifact must be repo-relative: {source_artifact}")
        full_path = (resolved_root / relative_path).resolve()
        try:
            full_path.relative_to(resolved_root)
        except ValueError as error:
            raise VerificationError(f"{row_name} source artifact escapes repo: {source_artifact}") from error
        if not full_path.exists():
            raise VerificationError(f"{row_name} references missing source artifact: {source_artifact}")


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for marker in sorted(FORBIDDEN_MARKERS):
        if marker in text:
            errors.append(f"{path.as_posix()} contains forbidden evidence marker: {marker}")
    lowered = text.lower()
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase.lower() in lowered:
            errors.append(f"{path.as_posix()} contains non-local evidence overclaim: {phrase}")
    if errors:
        raise VerificationError("\n".join(errors))


def check_pyramid(root: Path) -> None:
    manifest_text = read_text(root, PARITY_PYRAMID_MANIFEST)
    reject_forbidden_text(PARITY_PYRAMID_MANIFEST, manifest_text)
    rows = require_top_level(root, PARITY_PYRAMID_MANIFEST, "parity_pyramid")
    require_exact_row_ids(rows, REQUIRED_PYRAMID_ROW_IDS, PARITY_PYRAMID_MANIFEST)
    errors: list[str] = []
    required_fields = [
        "id",
        "layer",
        "requirement_id",
        "proof_scope",
        "evidence_class",
        "local_status",
        "cutover_status",
        "source_artifacts",
        "verifier_commands",
        "required_non_local_evidence",
        "secret_handling",
        "overclaim_guard",
        "phase_lifecycle_id",
    ]
    for row in rows:
        row_name = f"{PARITY_PYRAMID_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, required_fields, row_name, {"required_non_local_evidence"})
            row_id = require_string(row, "id", row_name)
            require_row_id_shape(row_id, row_name)
            proof_scope = require_string(row, "proof_scope", row_name)
            if proof_scope not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(f"{row_name} proof_scope is not allowed: {proof_scope}")
            evidence_class = require_string(row, "evidence_class", row_name)
            if proof_scope == "local" and evidence_class not in LOCAL_ONLY_EVIDENCE_CLASSES:
                raise VerificationError(
                    f"{row_name} local proof cannot use evidence_class: {evidence_class}"
                )
            local_status = require_string(row, "local_status", row_name)
            if proof_scope in NON_LOCAL_PROOF_SCOPES and local_status == "passed-local":
                raise VerificationError(
                    f"{row_name} proof_scope {proof_scope} must not use local_status passed-local"
                )
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
            if row.get("secret_handling") != "name-only-or-redacted":
                raise VerificationError(f"{row_name} secret_handling must be name-only-or-redacted")
            require_source_artifacts(root, row, row_name)
            require_non_empty_list_of_strings(row, "verifier_commands", row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def extract_v1_requirement_ids(root: Path) -> set[str]:
    text = read_text(root, REQUIREMENTS_FILE)
    ids: set[str] = set()
    in_v1 = False
    for line in text.splitlines():
        if line.startswith("## v1 Requirements"):
            in_v1 = True
            continue
        if line.startswith("## v2 Requirements"):
            break
        if not in_v1 or "**" not in line or not line.lstrip().startswith("- ["):
            continue
        parts = line.split("**")
        if len(parts) >= 3:
            ids.add(parts[1])
    if len(ids) != 30:
        raise VerificationError(f"{REQUIREMENTS_FILE.as_posix()} must define 30 v1 requirements")
    return ids


def check_requirements(root: Path) -> None:
    rows = require_top_level(root, REQUIREMENT_EVIDENCE_MANIFEST, "requirement_evidence")
    required_requirement_ids = extract_v1_requirement_ids(root)
    require_exact_row_ids(rows, set(REQUIRED_REQUIREMENT_ROWS), REQUIREMENT_EVIDENCE_MANIFEST)
    actual_requirement_ids: set[str] = set()
    errors: list[str] = []
    fields = [
        "id",
        "requirement_id",
        "owning_phase",
        "source_artifacts",
        "verifier_command_or_evidence_class",
        "current_status",
        "cutover_status",
        "intentional_delta_status",
        "retained_code_justification",
        "required_non_local_evidence",
        "cutover_blocker",
        "proof_scope",
        "phase_lifecycle_id",
    ]
    for row in rows:
        row_name = f"{REQUIREMENT_EVIDENCE_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, fields, row_name, {"required_non_local_evidence", "cutover_blocker"})
            row_id = require_string(row, "id", row_name)
            expected_requirement_id = REQUIRED_REQUIREMENT_ROWS[row_id]
            requirement_id = require_string(row, "requirement_id", row_name)
            if requirement_id != expected_requirement_id:
                raise VerificationError(f"{row_name} requirement_id must be {expected_requirement_id}")
            actual_requirement_ids.add(requirement_id)
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
            proof_scope = require_string(row, "proof_scope", row_name)
            if proof_scope not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(f"{row_name} proof_scope is not allowed: {proof_scope}")
            source_artifacts = require_non_empty_list_of_strings(row, "source_artifacts", row_name)
            if source_artifacts == [".planning/ROADMAP.md"]:
                raise VerificationError(f"{row_name} must not use roadmap-only evidence")
            if row.get("verifier_command_or_evidence_class") == "roadmap-only":
                raise VerificationError(f"{row_name} must not use roadmap-only evidence")
            require_source_artifacts(root, row, row_name)
            if requirement_id in PENDING_REQUIREMENT_IDS:
                current_status = require_string(row, "current_status", row_name)
                has_named_blocker = not is_missing(row.get("cutover_blocker"))
                has_non_local_evidence = not is_missing(row.get("required_non_local_evidence"))
                if current_status != "source-backed-local-passed" and not has_named_blocker and not has_non_local_evidence:
                    raise VerificationError(
                        f"{row_name} missing pending-requirement handling for {requirement_id}"
                    )
        except VerificationError as error:
            errors.append(str(error))
    missing_requirements = sorted(required_requirement_ids - actual_requirement_ids)
    extra_requirements = sorted(actual_requirement_ids - required_requirement_ids)
    if missing_requirements:
        errors.append("missing v1 requirement IDs: " + ", ".join(missing_requirements))
    if extra_requirements:
        errors.append("unexpected requirement IDs: " + ", ".join(extra_requirements))
    if errors:
        raise VerificationError("\n".join(errors))


def check_comparisons(root: Path) -> None:
    rows = require_top_level(root, REFERENCE_COMPARISONS_MANIFEST, "reference_comparisons")
    require_exact_row_ids(rows, REQUIRED_COMPARISON_ROW_IDS, REFERENCE_COMPARISONS_MANIFEST)
    fields = [
        "id",
        "requirement_id",
        "comparison_kind",
        "normalization_rule",
        "byte_identity_claim",
        "reference_command_policy",
        "guard_environment",
        "source_artifacts",
        "required_non_local_evidence",
        "secret_handling",
        "proof_scope",
        "phase_lifecycle_id",
    ]
    errors: list[str] = []
    for row in rows:
        row_name = f"{REFERENCE_COMPARISONS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, fields, row_name, {"required_non_local_evidence"})
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
            if row.get("secret_handling") != "name-only-or-redacted":
                raise VerificationError(f"{row_name} secret_handling must be name-only-or-redacted")
            proof_scope = require_string(row, "proof_scope", row_name)
            if proof_scope not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(f"{row_name} proof_scope is not allowed: {proof_scope}")
            if row.get("byte_identity_claim") is True:
                if is_missing(row.get("reference_fixture")) or is_missing(row.get("normalization_rule")):
                    raise VerificationError(
                        f"{row_name} byte_identity_claim true requires reference_fixture and normalization_rule"
                    )
            policy = require_string(row, "reference_command_policy", row_name)
            if "reference-only" in policy and row.get("guard_environment") != "BUDDY_BAZEL_EXECUTE_REFERENCE=1":
                raise VerificationError(f"{row_name} reference-only commands must be guarded")
            require_source_artifacts(root, row, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_cutover(root: Path) -> None:
    errors: list[str] = []
    cutover_rows: list[dict[str, object]] = []
    retained_rows: list[dict[str, object]] = []
    try:
        cutover_rows = require_top_level(root, CUTOVER_READINESS_MANIFEST, "cutover_criteria")
        require_exact_row_ids(
            cutover_rows,
            REQUIRED_CUTOVER_CRITERION_ROW_IDS,
            CUTOVER_READINESS_MANIFEST,
        )
    except VerificationError as error:
        errors.append(str(error))
    try:
        retained_rows = require_top_level(
            root,
            RETAINED_CODE_JUSTIFICATIONS_MANIFEST,
            "retained_code_justifications",
        )
        require_exact_row_ids(
            retained_rows,
            REQUIRED_RETAINED_CODE_ROW_IDS,
            RETAINED_CODE_JUSTIFICATIONS_MANIFEST,
        )
    except VerificationError as error:
        errors.append(str(error))
    cutover_fields = [
        "id",
        "requirement_id",
        "criterion",
        "status",
        "blocking_reason",
        "source_artifacts",
        "verifier_commands",
        "required_evidence",
        "demotion_allowed",
        "proof_scope",
        "phase_lifecycle_id",
    ]
    retained_fields = [
        "id",
        "requirement_id",
        "retained_surface",
        "owner",
        "disposition",
        "justification",
        "boundary",
        "safe_facade_or_contract",
        "source_artifacts",
        "required_evidence",
        "proof_scope",
        "secret_handling",
        "phase_lifecycle_id",
    ]
    for row in cutover_rows:
        row_name = f"{CUTOVER_READINESS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        try:
            require_fields(row, cutover_fields, row_name)
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
            if row.get("proof_scope") not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(f"{row_name} proof_scope is not allowed: {row.get('proof_scope')}")
            if row.get("id") == "criteria-reference-demotion-blocked" and row.get("demotion_allowed") is not False:
                raise VerificationError(f"{row_name} must keep demotion_allowed false")
            require_source_artifacts(root, row, row_name)
        except VerificationError as error:
            errors.append(str(error))
    for row in retained_rows:
        row_name = (
            f"{RETAINED_CODE_JUSTIFICATIONS_MANIFEST.as_posix()} row {row.get('id', '<unknown>')}"
        )
        try:
            require_fields(row, retained_fields, row_name)
            if row.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
                raise VerificationError(f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}")
            if row.get("proof_scope") != "retained-code-justification":
                raise VerificationError(f"{row_name} proof_scope must be retained-code-justification")
            if row.get("secret_handling") != "name-only-or-redacted":
                raise VerificationError(f"{row_name} secret_handling must be name-only-or-redacted")
            if row.get("disposition") not in {"accepted", "blocked", "deferred"}:
                raise VerificationError(f"{row_name} disposition must be accepted, blocked, or deferred")
            require_source_artifacts(root, row, row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def existing_security_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    manifest_dir = root / "tools/bazel/manifests"
    if manifest_dir.exists():
        paths.extend(path.relative_to(root) for path in sorted(manifest_dir.glob("phase11_*.json")))
    if (root / VALIDATION_CONTRACT).exists():
        paths.append(VALIDATION_CONTRACT)
    phase_dir = root / ".planning/phases/11-parity-pyramid-and-cutover-evidence"
    if phase_dir.exists():
        paths.extend(path.relative_to(root) for path in sorted(phase_dir.glob("11-*-SUMMARY.md")))
    return paths


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in existing_security_paths(root):
        try:
            reject_forbidden_text(path, read_text(root, path))
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_rust(root: Path) -> None:
    cutover_text = read_text(root, CUTOVER_RUST)
    lib_text = read_text(root, RUST_DOMAIN_LIB)
    errors: list[str] = []
    if "pub mod cutover;" not in lib_text:
        errors.append(f"{RUST_DOMAIN_LIB.as_posix()} must export pub mod cutover;")
    for api_string in sorted(REQUIRED_RUST_API_STRINGS):
        if api_string not in cutover_text:
            errors.append(f"{CUTOVER_RUST.as_posix()} missing Rust API surface: {api_string}")
    for label, pattern in UNSAFE_RUST_PATTERNS.items():
        if pattern in cutover_text:
            errors.append(f"{CUTOVER_RUST.as_posix()} contains {label}: {pattern}")
    if errors:
        raise VerificationError("\n".join(errors))


def require_file_contains(root: Path, path: Path, needles: list[str]) -> list[str]:
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    return [f"{path.as_posix()} missing required wiring text: {needle}" for needle in needles if needle not in text]


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase11_verify"',
                'name = "phase11_verify_tests"',
                "phase11_parity_pyramid.json",
                "phase11_requirement_evidence.json",
                "phase11_reference_comparisons.json",
                "phase11_cutover_readiness.json",
                "phase11_retained_code_justifications.json",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase11_verify)",
                "python3 tools/bazel/phase11_verify.py --wiring-only",
                "python3 tools/bazel/phase11_verify.py --quick",
                "phase11_verify_tests)",
                "python3 tools/bazel/phase11_verify_test.py",
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase11_cutover_evidence_docs"',
                'name = "phase11_verify"',
                'name = "phase11_verify_tests"',
            ],
        )
    )
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase11-verify:",
                "bazel run //tools/bazel:phase11_verify_tests",
                "bazel run //tools/bazel:phase11_verify",
                "bazel run //tools/bazel:rust_format_check",
                "bazel run //tools/bazel:rust_lint",
                "bazel run //tools/bazel:rust_build",
                "bazel run //tools/bazel:rust_unit_tests",
            ],
        )
    )
    if errors:
        raise VerificationError("\n".join(errors))


def check_quick(root: Path) -> None:
    collect_errors([lambda: check_pyramid(root), lambda: check_security(root)])


def run_command(root: Path, command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise VerificationError(
            f"{' '.join(command)} failed with exit code {result.returncode}\n{result.stdout}"
        )


def check_all(root: Path) -> None:
    collect_errors(
        [
            lambda: check_quick(root),
            lambda: check_requirements(root),
            lambda: check_comparisons(root),
            lambda: check_cutover(root),
            lambda: check_rust(root),
            lambda: check_wiring(root),
        ]
    )


def collect_errors(checks: list[object]) -> None:
    errors: list[str] = []
    for check in checks:
        try:
            check()
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n\n".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 11 parity pyramid and cutover evidence.")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to inspect; useful for wiring fixtures.",
    )
    parser.add_argument("--quick", action="store_true", help="run pyramid plus existing security scans")
    parser.add_argument("--all", action="store_true", help="run all Phase 11 verification modes")
    parser.add_argument("--pyramid-only", action="store_true", help="verify only the parity pyramid")
    parser.add_argument("--requirements-only", action="store_true", help="verify only requirement evidence")
    parser.add_argument("--comparison-only", action="store_true", help="verify only reference comparisons")
    parser.add_argument("--cutover-only", action="store_true", help="verify only cutover readiness")
    parser.add_argument("--security-only", action="store_true", help="verify only secret and overclaim scans")
    parser.add_argument("--rust-only", action="store_true", help="verify only Rust cutover contracts")
    parser.add_argument("--wiring-only", action="store_true", help="verify only Bazel/just wiring")
    return parser.parse_args()


def selected_checks(root: Path, args: argparse.Namespace) -> list[object]:
    checks: list[object] = []
    if args.all:
        checks.append(lambda: check_all(root))
    if args.quick:
        checks.append(lambda: check_quick(root))
    if args.pyramid_only:
        checks.append(lambda: check_pyramid(root))
    if args.requirements_only:
        checks.append(lambda: check_requirements(root))
    if args.comparison_only:
        checks.append(lambda: check_comparisons(root))
    if args.cutover_only:
        checks.append(lambda: check_cutover(root))
    if args.security_only:
        checks.append(lambda: check_security(root))
    if args.rust_only:
        checks.append(lambda: check_rust(root))
    if args.wiring_only:
        checks.append(lambda: check_wiring(root))
    if not checks:
        checks.append(lambda: check_quick(root))
    return checks


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else ROOT
    try:
        collect_errors(selected_checks(root, args))
    except VerificationError as error:
        print(f"Phase 11 parity/cutover verification failed:\n{error}")
        return 1
    print("Phase 11 parity/cutover verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
