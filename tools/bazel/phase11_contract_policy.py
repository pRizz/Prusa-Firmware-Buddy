#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE = "11-parity-pyramid-and-cutover-evidence"
PHASE_LIFECYCLE_ID = "11-2026-06-14T18-48-49"

PARITY_PYRAMID_MANIFEST = Path(
    "tools/bazel/manifests/phase11_parity_pyramid.json")
REQUIREMENT_EVIDENCE_MANIFEST = Path(
    "tools/bazel/manifests/phase11_requirement_evidence.json")
REFERENCE_COMPARISONS_MANIFEST = Path(
    "tools/bazel/manifests/phase11_reference_comparisons.json")
CUTOVER_READINESS_MANIFEST = Path(
    "tools/bazel/manifests/phase11_cutover_readiness.json")
RETAINED_CODE_JUSTIFICATIONS_MANIFEST = Path(
    "tools/bazel/manifests/phase11_retained_code_justifications.json")
REQUIREMENTS_FILE = Path(".planning/REQUIREMENTS.md")
ARCHIVED_REQUIREMENTS_FILE = Path(".planning/milestones/v1.0-REQUIREMENTS.md")
ARCHIVED_PHASES_ROOT = Path(".planning/milestones/v1.0-phases")
PHASE11_DOC_DIR = Path(
    ".planning/phases/11-parity-pyramid-and-cutover-evidence")
VALIDATION_CONTRACT = Path(
    ".planning/phases/11-parity-pyramid-and-cutover-evidence/11-VALIDATION.md")
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
FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE),
    re.compile(
        r"(certificate[_-]?pem|password[_-]?value|token[_-]?value|certificate[_-]?bytes|private[_-]?key|signing[_-]?key[_-]?value|raw[_-]?crash[_-]?dump|firmware[_-]?payload)",
        re.IGNORECASE,
    ),
)
OVERCLAIM_STRINGS = {
    "hardware verified locally",
    "local hardware proof",
    "simulator passed locally",
    "byte-identical firmware",
    "cutover complete",
    "reference path removed",
    "reference removal complete",
}
STALE_PLAN_MARKER_PATTERNS = (
    re.compile(r"\bpending-plan-[A-Za-z0-9-]+\b"),
    re.compile(r"\brequires-plan-11-03[A-Za-z0-9-]*\b"),
    re.compile(r"\brequires-plan-11-04[A-Za-z0-9-]*\b"),
    re.compile(r"not created yet", re.IGNORECASE),
)

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
PENDING_REQUIREMENT_IDS = {
    "BAZL-03", "BAZL-05", "VERF-01", "VERF-03", "VERF-04", "VERF-05"
}
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
ALLOWED_REFERENCE_COMPARISON_KINDS = {
    "normalized-semantic",
    "byte-identity-with-fixture",
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
REQUIRED_KNOWN_CONCERN_ROW_IDS = {
    "concern-phase11-known-defect-ledger",
    "concern-phase11-non-local-hardware-proof",
    "concern-phase11-secret-redaction",
    "concern-phase11-byte-identity-overclaim",
    "concern-phase11-reference-demotion",
}
ALLOWED_KNOWN_CONCERN_DISPOSITIONS = {
    "preserved-temporarily",
    "blocked",
    "accepted-retained-behavior",
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
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def maybe_archived_phase_path(path: Path) -> Path | None:
    parts = path.parts
    if len(parts) < 3 or parts[0:2] != (".planning", "phases"):
        return None
    return ARCHIVED_PHASES_ROOT.joinpath(*parts[2:])


def source_artifact_exists(root: Path, path: Path) -> bool:
    if (root / path).exists():
        return True
    maybe_archived_path = maybe_archived_phase_path(path)
    return maybe_archived_path is not None and (root /
                                                maybe_archived_path).exists()


def phase11_requirements_file(root: Path) -> Path:
    if (root / ARCHIVED_REQUIREMENTS_FILE).exists():
        return ARCHIVED_REQUIREMENTS_FILE
    return REQUIREMENTS_FILE


def load_json(root: Path, path: Path) -> dict[str, object]:
    try:
        data = json.loads(read_text(root, path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{path.as_posix()} is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise VerificationError(
            f"{path.as_posix()} must contain a top-level JSON object")
    return data


def is_missing(value: object) -> bool:
    return value in ("", None) or value == [] or value == {}


def require_string(row: dict[str, object], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, object], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of strings")
    return value


def require_non_empty_list_of_strings(row: dict[str, object], field: str,
                                      row_name: str) -> list[str]:
    values = require_list_of_strings(row, field, row_name)
    if not values:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty list of strings")
    return values


def require_required_non_local_evidence(
    row: dict[str, object],
    row_name: str,
    proof_scope: str,
) -> None:
    if proof_scope in NON_LOCAL_PROOF_SCOPES:
        require_non_empty_list_of_strings(row, "required_non_local_evidence",
                                          row_name)
        return
    require_list_of_strings(row, "required_non_local_evidence", row_name)


def require_fields(
    row: dict[str, object],
    fields: list[str],
    row_name: str,
    maybe_empty_fields: set[str] | None = None,
) -> None:
    allowed_empty = maybe_empty_fields or set()
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields if field in row
        and field not in allowed_empty and is_missing(row[field])
    ]
    if missing or empty:
        parts: list[str] = []
        if missing:
            parts.append("missing required fields: " + ", ".join(missing))
        if empty:
            parts.append("empty required fields: " + ", ".join(empty))
        raise VerificationError(f"{row_name} " + "; ".join(parts))


def require_top_level(root: Path, path: Path,
                      collection_name: str) -> list[dict[str, object]]:
    data = load_json(root, path)
    if data.get("schema_version") != "1":
        raise VerificationError(
            f"{path.as_posix()} must set schema_version to \"1\"")
    if data.get("phase") != PHASE:
        raise VerificationError(f"{path.as_posix()} must set phase to {PHASE}")
    if data.get("phase_lifecycle_id") != PHASE_LIFECYCLE_ID:
        raise VerificationError(
            f"{path.as_posix()} must set phase_lifecycle_id to {PHASE_LIFECYCLE_ID}"
        )

    rows = data.get(collection_name)
    if not isinstance(rows, list):
        raise VerificationError(
            f"{path.as_posix()} must contain a {collection_name} list")
    parsed_rows: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(
                f"{path.as_posix()} {collection_name}[{index}] must be an object"
            )
        parsed_rows.append(row)
    return parsed_rows


def require_exact_row_ids(rows: list[dict[str, object]],
                          expected_ids: set[str], path: Path) -> None:
    actual_ids: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        row_id = row.get("id")
        if not isinstance(row_id, str):
            raise VerificationError(
                f"{path.as_posix()} row has non-string id: {row_id!r}")
        require_row_id_shape(row_id, f"{path.as_posix()} row {row_id}")
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
        details.append("has duplicate row IDs: " +
                       ", ".join(sorted(duplicates)))
    if details:
        raise VerificationError(f"{path.as_posix()} " + "; ".join(details))


def require_row_id_shape(row_id: str, row_name: str) -> None:
    try:
        encoded = row_id.encode("ascii")
    except UnicodeEncodeError as error:
        raise VerificationError(
            f"{row_name} id must be printable ASCII") from error
    if len(encoded) > 96:
        raise VerificationError(f"{row_name} id must be at most 96 bytes")
    if any(ord(char) < 33 or ord(char) > 126 for char in row_id):
        raise VerificationError(f"{row_name} id must be printable ASCII")
    if row_id in {".", ".."
                  } or "/" in row_id or "\\" in row_id or ".." in row_id:
        raise VerificationError(f"{row_name} id must be path-free")


def require_source_artifacts(root: Path, row: dict[str, object],
                             row_name: str) -> None:
    source_artifacts = require_non_empty_list_of_strings(
        row, "source_artifacts", row_name)
    resolved_root = root.resolve()
    for source_artifact in source_artifacts:
        relative_path = Path(source_artifact)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise VerificationError(
                f"{row_name} source artifact must be repo-relative: {source_artifact}"
            )
        full_path = (resolved_root / relative_path).resolve()
        try:
            full_path.relative_to(resolved_root)
        except ValueError as error:
            raise VerificationError(
                f"{row_name} source artifact escapes repo: {source_artifact}"
            ) from error
        if not source_artifact_exists(root, relative_path):
            raise VerificationError(
                f"{row_name} references missing source artifact: {source_artifact}"
            )


def reject_forbidden_text(path: Path, text: str) -> None:
    errors: list[str] = []
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            errors.append(
                f"{path.as_posix()} contains forbidden evidence marker: {match.group(0)}"
            )
    lowered = text.lower()
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase.lower() in lowered:
            errors.append(
                f"{path.as_posix()} contains non-local evidence overclaim: {phrase}"
            )
    if errors:
        raise VerificationError("\n".join(errors))


def later_phase_artifacts_exist(root: Path) -> bool:
    return all((root / path).exists() for path in [
        REFERENCE_COMPARISONS_MANIFEST,
        CUTOVER_READINESS_MANIFEST,
        RETAINED_CODE_JUSTIFICATIONS_MANIFEST,
        CUTOVER_RUST,
    ])


def stale_plan_markers(text: str) -> list[str]:
    markers: set[str] = set()
    for pattern in STALE_PLAN_MARKER_PATTERNS:
        markers.update(match.group(0) for match in pattern.finditer(text))
    return sorted(markers, key=str.lower)


def require_no_stale_plan_markers_after_later_artifacts(
        root: Path, path: Path, text: str) -> None:
    if not later_phase_artifacts_exist(root):
        return
    markers = stale_plan_markers(text)
    if markers:
        raise VerificationError(
            f"{path.as_posix()} contains stale Plan 11-03/11-04 markers after Plan 11-03/11-04 artifacts exist: "
            + ", ".join(markers))


def check_pyramid(root: Path) -> None:
    manifest_text = read_text(root, PARITY_PYRAMID_MANIFEST)
    errors: list[str] = []
    try:
        reject_forbidden_text(PARITY_PYRAMID_MANIFEST, manifest_text)
        require_no_stale_plan_markers_after_later_artifacts(
            root, PARITY_PYRAMID_MANIFEST, manifest_text)
    except VerificationError as error:
        errors.append(str(error))
    rows = require_top_level(root, PARITY_PYRAMID_MANIFEST, "parity_pyramid")
    require_exact_row_ids(rows, REQUIRED_PYRAMID_ROW_IDS,
                          PARITY_PYRAMID_MANIFEST)
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
            require_fields(row, required_fields, row_name,
                           {"required_non_local_evidence"})
            row_id = require_string(row, "id", row_name)
            require_row_id_shape(row_id, row_name)
            proof_scope = require_string(row, "proof_scope", row_name)
            if proof_scope not in ALLOWED_PROOF_SCOPES:
                raise VerificationError(
                    f"{row_name} proof_scope is not allowed: {proof_scope}")
            require_required_non_local_evidence(row, row_name, proof_scope)
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
                raise VerificationError(
                    f"{row_name} phase_lifecycle_id must be {PHASE_LIFECYCLE_ID}"
                )
            if row.get("secret_handling") != "name-only-or-redacted":
                raise VerificationError(
                    f"{row_name} secret_handling must be name-only-or-redacted"
                )
            require_source_artifacts(root, row, row_name)
            require_non_empty_list_of_strings(row, "verifier_commands",
                                              row_name)
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def extract_v1_requirement_ids(root: Path) -> set[str]:
    requirements_file = phase11_requirements_file(root)
    text = read_text(root, requirements_file)
    ids: set[str] = set()
    in_v1 = False
    for line in text.splitlines():
        if line.startswith("## v1 Requirements"):
            in_v1 = True
            continue
        if line.startswith("## v2 Requirements"):
            break
        if not in_v1 or "**" not in line or not line.lstrip().startswith(
                "- ["):
            continue
        parts = line.split("**")
        if len(parts) >= 3:
            ids.add(parts[1])
    if len(ids) != 30:
        raise VerificationError(
            f"{requirements_file.as_posix()} must define 30 v1 requirements")
    return ids


def require_source_artifact_values(
    row: dict[str, object],
    row_name: str,
    required_artifacts: set[str],
) -> None:
    source_artifacts = set(
        require_non_empty_list_of_strings(row, "source_artifacts", row_name))
    missing = sorted(required_artifacts - source_artifacts)
    if missing:
        raise VerificationError(
            f"{row_name} missing source_artifacts: {', '.join(missing)}")


def require_final_verf03_row(row: dict[str, object], row_name: str) -> None:
    if row.get("current_status") != "source-backed-local-passed":
        raise VerificationError(
            f"{row_name} current_status must be source-backed-local-passed")
    require_source_artifact_values(
        row,
        row_name,
        {
            REFERENCE_COMPARISONS_MANIFEST.as_posix(),
            CUTOVER_RUST.as_posix(),
        },
    )
    require_text_values(
        row,
        ["verifier_command_or_evidence_class"],
        row_name,
        [
            "python3 tools/bazel/phase11_verify.py --comparison-only",
            "python3 tools/bazel/phase11_verify.py --rust-only",
        ],
    )
    require_text_values(
        row,
        ["required_non_local_evidence", "cutover_blocker"],
        row_name,
        [
            "simulator",
            "hardware",
            "live network",
            "release-candidate",
        ],
    )


def require_final_verf05_row(row: dict[str, object], row_name: str) -> None:
    if row.get("current_status") != "source-backed-local-passed":
        raise VerificationError(
            f"{row_name} current_status must be source-backed-local-passed")
    if row.get("cutover_status") != "not-cutover-ready":
        raise VerificationError(
            f"{row_name} cutover_status must remain not-cutover-ready")
    require_source_artifact_values(
        row,
        row_name,
        {
            CUTOVER_READINESS_MANIFEST.as_posix(),
            RETAINED_CODE_JUSTIFICATIONS_MANIFEST.as_posix(),
        },
    )
    require_text_values(
        row,
        ["verifier_command_or_evidence_class"],
        row_name,
        ["python3 tools/bazel/phase11_verify.py --cutover-only"],
    )
    require_text_values(
        row,
        ["required_non_local_evidence", "cutover_blocker"],
        row_name,
        [
            "criteria-reference-demotion-blocked",
            "simulator",
            "hardware",
            "live network",
            "release-candidate",
            "MMU",
            "RS485",
            "toolchanger",
        ],
    )


def require_text_values(
    row: dict[str, object],
    fields: list[str],
    row_name: str,
    needles: list[str],
) -> None:
    text = "\n".join(str(row.get(field, "")) for field in fields).lower()
    missing = [needle for needle in needles if needle.lower() not in text]
    if missing:
        raise VerificationError(
            f"{row_name} missing final evidence text: {', '.join(missing)}")
