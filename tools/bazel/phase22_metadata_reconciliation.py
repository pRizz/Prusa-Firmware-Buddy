#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PHASE = "22-evidence-metadata-reconciliation"
PHASE_LIFECYCLE_ID = "22-2026-06-21T16-59-18"
CONTRACT_MANIFEST = Path("tools/bazel/manifests/phase22_metadata_reconciliation_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase22")

REQUIRED_ARTIFACTS = [
    "metadata-reconciliation-report.json",
    "audit-rerun-readiness.json",
    "redacted-summary.md",
]

REQUIRED_CORRECTION_IDS = [
    "requirements-sim-03",
    "requirements-rev-02",
    "requirements-rev-03",
    "validation-phase14",
    "validation-phase15",
    "validation-phase16",
    "validation-phase17",
    "validation-phase18",
    "validation-phase20-adjacent-drift",
    "roadmap-phase21-progress",
    "roadmap-phase22-plan-count",
    "state-phase22-position",
    "audit-rerun-readiness",
]

REQUIRED_AUDIT_GAP_IDS = [
    "aggregate-ci-gap",
    "release-identity-gap",
    "upstream-result-consumption-gap",
    "requirements-status-gap",
    "validation-metadata-gap",
]

CORRECTION_REQUIRED_FIELDS = [
    "id",
    "target_file",
    "correction_type",
    "old_state",
    "required_new_markers",
    "source_refs",
    "no_overclaim_rationale",
    "verification_command",
]

DEBT_REQUIRED_FIELDS = [
    "owner",
    "rationale",
    "follow_up_or_expiry",
    "source_refs",
]

SENSITIVE_CONTRACT_MARKERS = [
    "private key",
    "token",
    "credential",
    "raw payload",
    "crash dump",
]

FORBIDDEN_OVERCLAIM_MARKERS = [
    "hardware verified locally",
    "reference demotion approved",
    "cutover complete",
    "signing verified locally",
]

FILE_SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE), "private key"),
    (re.compile(r"\b(?:api[_-]?key|token|credential|password|secret)\s*[:=]", re.IGNORECASE), "credential"),
    (re.compile(r"\braw[_ -]?payload\s*[:=]", re.IGNORECASE), "raw payload"),
    (re.compile(r"\braw[_ -]?crash[_ -]?dump\b", re.IGNORECASE), "crash dump"),
]

PHASES_WITH_VALIDATION_METADATA = [14, 15, 16, 17, 18, 20]


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise VerificationError(f"missing JSON file: {path}") from error
    except json.JSONDecodeError as error:
        raise VerificationError(f"invalid JSON in {path}: {error}") from error


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise VerificationError(f"missing text file: {path}") from error


def require_dict(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{context} must be a JSON object")
    return value


def require_list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError(f"{context} must be a list")
    return value


def is_safe_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and value.strip() == value and value != ""


def ensure_safe_repo_relative(value: str, context: str, errors: list[str]) -> None:
    source_path = value.split("#", 1)[0]
    if source_path == "":
        errors.append(f"{context}: empty source path")
        return
    if not is_safe_relative_path(source_path):
        errors.append(f"{context}: unsafe path {value}")


def validate_output_dir(root: Path, output_dir: Path) -> Path:
    if output_dir.is_absolute() or ".." in output_dir.parts:
        raise VerificationError(f"output directory must stay under {DEFAULT_OUTPUT_DIR}: {output_dir}")

    target = (root / output_dir).resolve(strict=False)
    allowed = (root / DEFAULT_OUTPUT_DIR).resolve(strict=False)
    if target != allowed and allowed not in target.parents:
        raise VerificationError(f"output directory must stay under {DEFAULT_OUTPUT_DIR}: {output_dir}")

    current = root
    for part in output_dir.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise VerificationError(f"output directory contains symlink component: {current.relative_to(root)}")

    return target


def validate_generated_artifacts(contract: dict[str, Any], errors: list[str]) -> None:
    artifacts = require_list(contract.get("generated_artifacts"), "generated_artifacts")
    if artifacts != REQUIRED_ARTIFACTS:
        errors.append(f"generated_artifacts must be {REQUIRED_ARTIFACTS}")

    for artifact in artifacts:
        if not isinstance(artifact, str):
            errors.append(f"generated_artifacts contains non-string entry: {artifact!r}")
            continue
        if not is_safe_relative_path(artifact):
            errors.append(f"generated_artifacts unsafe path: {artifact}")


def validate_source_refs(row_id: str, source_refs: Any, errors: list[str]) -> None:
    if not isinstance(source_refs, list) or not source_refs:
        errors.append(f"{row_id}: missing source_refs")
        return
    for source_ref in source_refs:
        if not isinstance(source_ref, str) or source_ref == "":
            errors.append(f"{row_id}: source_refs contains invalid entry")
            continue
        ensure_safe_repo_relative(source_ref, f"{row_id} source_refs", errors)


def validate_correction_rows(contract: dict[str, Any], errors: list[str]) -> None:
    rows = require_list(contract.get("metadata_corrections"), "metadata_corrections")
    rows_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_row in enumerate(rows):
        if not isinstance(raw_row, dict):
            errors.append(f"metadata_corrections[{index}] must be an object")
            continue
        row = raw_row
        row_id = str(row.get("id", f"metadata_corrections[{index}]"))
        rows_by_id[row_id] = row
        missing = [field for field in CORRECTION_REQUIRED_FIELDS if row.get(field) in (None, "", [])]
        if missing:
            errors.append(f"{row_id}: missing {', '.join(missing)}")
        target_file = row.get("target_file")
        if isinstance(target_file, str):
            ensure_safe_repo_relative(target_file, f"{row_id} target_file", errors)
        validate_source_refs(row_id, row.get("source_refs"), errors)
        markers = row.get("required_new_markers")
        if not isinstance(markers, list) or not markers:
            errors.append(f"{row_id}: missing required_new_markers")

    missing_ids = [row_id for row_id in REQUIRED_CORRECTION_IDS if row_id not in rows_by_id]
    if missing_ids:
        errors.append(f"metadata_corrections missing required rows: {', '.join(missing_ids)}")


def validate_debt_rows(contract: dict[str, Any], errors: list[str]) -> None:
    rows = require_list(contract.get("non_blocking_debt"), "non_blocking_debt")
    for index, raw_row in enumerate(rows):
        if not isinstance(raw_row, dict):
            errors.append(f"non_blocking_debt[{index}] must be an object")
            continue
        row_id = str(raw_row.get("id", f"non_blocking_debt[{index}]"))
        missing = [field for field in DEBT_REQUIRED_FIELDS if raw_row.get(field) in (None, "", [])]
        if missing:
            errors.append(f"{row_id}: missing {', '.join(missing)}")
        validate_source_refs(row_id, raw_row.get("source_refs"), errors)


def validate_audit_gap_rows(contract: dict[str, Any], errors: list[str]) -> None:
    rows = require_list(contract.get("audit_gap_mappings"), "audit_gap_mappings")
    rows_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_row in enumerate(rows):
        if not isinstance(raw_row, dict):
            errors.append(f"audit_gap_mappings[{index}] must be an object")
            continue
        row = raw_row
        row_id = str(row.get("id", f"audit_gap_mappings[{index}]"))
        rows_by_id[row_id] = row
        for field in ["id", "original_audit_gap", "mapped_status", "source_refs", "correction_ids", "no_overclaim_rationale"]:
            if row.get(field) in (None, "", []):
                errors.append(f"{row_id}: missing {field}")
        validate_source_refs(row_id, row.get("source_refs"), errors)
        correction_ids = row.get("correction_ids")
        if not isinstance(correction_ids, list) or not correction_ids:
            errors.append(f"{row_id}: missing correction_ids")

    missing_ids = [row_id for row_id in REQUIRED_AUDIT_GAP_IDS if row_id not in rows_by_id]
    if missing_ids:
        errors.append(f"audit_gap_mappings missing required rows: {', '.join(missing_ids)}")


def check_contract(root: Path) -> dict[str, Any]:
    contract = require_dict(load_json(root / CONTRACT_MANIFEST), CONTRACT_MANIFEST.as_posix())
    errors: list[str] = []

    expected_scalars = {
        "schema_version": "1",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
    }
    for field, expected in expected_scalars.items():
        actual = contract.get(field)
        if actual != expected:
            errors.append(f"{field} must be {expected!r}, got {actual!r}")

    requirements = contract.get("requirements")
    if requirements != ["Metadata debt from v1.1 audit"]:
        errors.append("requirements must be ['Metadata debt from v1.1 audit']")

    snapshots = contract.get("sanitized_source_snapshots")
    if not isinstance(snapshots, list) or not snapshots:
        errors.append("sanitized_source_snapshots must be a non-empty list")
    elif not all(isinstance(snapshot, str) and is_safe_relative_path(snapshot) for snapshot in snapshots):
        errors.append("sanitized_source_snapshots contains unsafe paths")

    validate_generated_artifacts(contract, errors)
    validate_correction_rows(contract, errors)
    validate_audit_gap_rows(contract, errors)
    validate_debt_rows(contract, errors)

    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def iter_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
        return strings
    if isinstance(value, dict):
        for nested in value.values():
            strings.extend(iter_strings(nested))
        return strings
    if isinstance(value, list):
        for nested in value:
            strings.extend(iter_strings(nested))
    return strings


def check_forbidden_contract_text(contract: dict[str, Any]) -> None:
    errors: list[str] = []
    markers = SENSITIVE_CONTRACT_MARKERS + FORBIDDEN_OVERCLAIM_MARKERS
    for text in iter_strings(contract):
        lowered = text.lower()
        for marker in markers:
            if marker in lowered:
                errors.append(f"forbidden marker {marker} in contract text: {text}")
    if errors:
        raise VerificationError("\n".join(errors))


def check_file_security_text(path: Path, text: str, broad_markers: bool) -> list[str]:
    errors: list[str] = []
    for pattern, marker in FILE_SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(f"{path}: forbidden {marker} marker")
    lowered = text.lower()
    for marker in FORBIDDEN_OVERCLAIM_MARKERS:
        if marker in lowered:
            errors.append(f"{path}: forbidden overclaim marker {marker}")
    if broad_markers:
        for marker in SENSITIVE_CONTRACT_MARKERS:
            if marker in lowered:
                errors.append(f"{path}: forbidden marker {marker}")
    return errors


def target_metadata_paths(root: Path, contract: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for raw_row in require_list(contract.get("metadata_corrections"), "metadata_corrections"):
        if not isinstance(raw_row, dict):
            continue
        target_file = raw_row.get("target_file")
        if isinstance(target_file, str) and is_safe_relative_path(target_file):
            path = root / target_file
            if path.exists() and path not in paths:
                paths.append(path)
    return paths


def generated_artifact_paths(root: Path, output_dir: Path, contract: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for artifact in require_list(contract.get("generated_artifacts"), "generated_artifacts"):
        if isinstance(artifact, str) and is_safe_relative_path(artifact):
            path = root / output_dir / artifact
            if path.exists():
                paths.append(path)
    return paths


def check_security(root: Path, output_dir: Path) -> None:
    contract = check_contract(root)
    validate_output_dir(root, output_dir)
    check_forbidden_contract_text(contract)

    errors: list[str] = []
    for path in target_metadata_paths(root, contract):
        text = read_text(path)
        errors.extend(check_file_security_text(path.relative_to(root), text, broad_markers=False))
    for path in generated_artifact_paths(root, output_dir, contract):
        text = read_text(path)
        errors.extend(check_file_security_text(path.relative_to(root), text, broad_markers=True))

    if errors:
        raise VerificationError("\n".join(errors))


def requirement_rows(text: str, requirement_id: str) -> list[str]:
    return [line for line in text.splitlines() if re.search(rf"\|\s*{re.escape(requirement_id)}\s*\|", line)]


def check_requirements(root: Path) -> None:
    text = read_text(root / ".planning/REQUIREMENTS.md")
    errors: list[str] = []
    caveats = {
        "SIM-03": "hardware-only behavior is not simulator-proven",
        "REV-02": "demotion_allowed remains blocked",
        "REV-03": "demotion_allowed remains blocked",
    }

    for requirement_id, caveat in caveats.items():
        if re.search(rf"-\s+\[ \]\s+\*\*{re.escape(requirement_id)}\*\*", text):
            errors.append(f"{requirement_id}: checklist row is unchecked")
        for row in requirement_rows(text, requirement_id):
            if re.search(r"\bPending\b", row, re.IGNORECASE):
                errors.append(f"{requirement_id}: traceability row is Pending")
            if re.search(r"\bComplete\b", row, re.IGNORECASE) and caveat not in row:
                errors.append(f"{requirement_id}: Complete row must include caveat: {caveat}")

    if errors:
        raise VerificationError("\n".join(errors))


def validation_path_for_phase(root: Path, phase: int) -> Path:
    matches = sorted((root / ".planning/phases").glob(f"{phase:02d}-*/{phase:02d}-VALIDATION.md"))
    if not matches:
        raise VerificationError(f"missing Phase {phase} validation file")
    return matches[0]


def has_unchecked_wave_zero_bullet(text: str) -> bool:
    in_wave_zero = False
    for line in text.splitlines():
        if line.startswith("#"):
            in_wave_zero = bool(re.search(r"\bwave\s*0\b|\bw0\b", line, re.IGNORECASE))
            continue
        if in_wave_zero and re.match(r"\s*-\s+\[ \]", line):
            return True
    return False


def check_validation(root: Path) -> None:
    errors: list[str] = []
    stale_markers = ["no - Wave 0", "No - Wave 0", "no W0"]
    for phase in PHASES_WITH_VALIDATION_METADATA:
        path = validation_path_for_phase(root, phase)
        text = read_text(path)
        rel = path.relative_to(root)
        if "wave_0_complete: false" in text:
            errors.append(f"{rel}: wave_0_complete is false")
        if "nyquist_compliant: false" in text:
            errors.append(f"{rel}: nyquist_compliant is false")
        for marker in stale_markers:
            if marker in text:
                errors.append(f"{rel}: stale Wave 0 marker {marker}")
        if has_unchecked_wave_zero_bullet(text):
            errors.append(f"{rel}: unchecked Wave 0 bullet")
        for line in text.splitlines():
            if line.strip().startswith("|") and re.search(r"\|\s*pending\s*\|", line, re.IGNORECASE):
                errors.append(f"{rel}: pending validation row: {line.strip()}")

    if errors:
        raise VerificationError("\n".join(errors))


def check_roadmap_state(root: Path) -> None:
    roadmap = read_text(root / ".planning/ROADMAP.md")
    state = read_text(root / ".planning/STATE.md")
    errors: list[str] = []

    if re.search(r"\|\s*21\.[^|\n]*\|\s*v?1\.1\s*\|\s*0/0\s*\|\s*Planned\s*\|", roadmap):
        errors.append("Phase 21 roadmap row is stale: 0/0 | Planned")
    if re.search(r"\|\s*22\.[^|\n]*\|\s*v?1\.1\s*\|\s*0/3\s*\|\s*Planned\s*\|", roadmap):
        errors.append("Phase 22 roadmap row is stale: 0/3 | Planned")

    for line in state.splitlines():
        lowered = line.lower()
        if "current focus" in lowered or "current position" in lowered:
            if "phase 20" in lowered or "phase 21" in lowered:
                errors.append(f"STATE current-position text is stale: {line.strip()}")

    if errors:
        raise VerificationError("\n".join(errors))


def check_audit_readiness(root: Path) -> dict[str, Any]:
    contract = check_contract(root)
    gap_rows = require_list(contract.get("audit_gap_mappings"), "audit_gap_mappings")
    debt_rows = require_list(contract.get("non_blocking_debt"), "non_blocking_debt")
    allowed_statuses = {"closed", "still_blocking", "non_blocking_debt", "metadata-correction-required"}
    errors: list[str] = []
    normalized_rows: list[dict[str, Any]] = []

    for raw_row in gap_rows:
        if not isinstance(raw_row, dict):
            errors.append("audit gap row must be an object")
            continue
        row_id = str(raw_row.get("id", "missing-id"))
        status = str(raw_row.get("mapped_status", ""))
        if status not in allowed_statuses:
            errors.append(f"{row_id}: unsupported mapped_status {status}")
        normalized_rows.append({
            "id": row_id,
            "mapped_status": status,
            "source_refs": raw_row.get("source_refs", []),
            "correction_ids": raw_row.get("correction_ids", []),
        })

    if debt_rows:
        validate_debt_rows(contract, errors)

    if errors:
        raise VerificationError("\n".join(errors))

    status = "passed"
    if any(row["mapped_status"] == "still_blocking" for row in normalized_rows):
        status = "blocked"
    elif debt_rows:
        status = "non_blocking_debt"

    return {
        "status": status,
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "audit_gap_mappings": normalized_rows,
        "non_blocking_debt": debt_rows,
    }


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    for path in [CONTRACT_MANIFEST, Path("tools/bazel/phase22_metadata_reconciliation.py"), Path("tools/bazel/phase22_metadata_reconciliation_test.py")]:
        if not (root / path).exists():
            errors.append(f"missing wiring file: {path}")
    if errors:
        raise VerificationError("\n".join(errors))


def run_quick(root: Path, output_dir: Path) -> None:
    check_contract(root)
    check_audit_readiness(root)
    check_security(root, output_dir)
    check_wiring(root)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify Phase 22 metadata reconciliation evidence.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR.as_posix())
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--requirements-only", action="store_true")
    parser.add_argument("--validation-only", action="store_true")
    parser.add_argument("--roadmap-state-only", action="store_true")
    parser.add_argument("--audit-readiness-only", action="store_true")
    parser.add_argument("--security-only", action="store_true")
    parser.add_argument("--wiring-only", action="store_true")
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path.cwd()
    output_dir = Path(args.output_dir)

    try:
        if args.contract_only:
            check_contract(root)
        elif args.requirements_only:
            check_requirements(root)
        elif args.validation_only:
            check_validation(root)
        elif args.roadmap_state_only:
            check_roadmap_state(root)
        elif args.audit_readiness_only:
            check_audit_readiness(root)
        elif args.security_only:
            check_security(root, output_dir)
        elif args.wiring_only:
            check_wiring(root)
        elif args.quick:
            run_quick(root, output_dir)
        else:
            check_contract(root)
    except VerificationError as error:
        print(error)
        return 1

    # Keep imported helpers exercised in normal execution; Task 3 uses these for artifact writes.
    _ = shutil.copy2
    _ = utc_now
    print("phase22 metadata reconciliation verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
