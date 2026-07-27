#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "14-simulator-evidence-gates"
PHASE_LIFECYCLE_ID = "14-2026-06-17T16-11-34"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase14_simulator_evidence_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase14")
REQUIRED_REQUIREMENT_IDS = {"SIM-01", "SIM-02", "SIM-03"}
REQUIRED_SCENARIO_IDS = {
    "sim-startup-bootstrap-ready",
    "sim-task-readiness-home-wui",
    "sim-watchdog-visible-startup-readiness",
    "sim-gcode-file-print-telemetry",
    "sim-gui-filebrowser-navigation",
    "sim-storage-resource-wui-list-delete",
    "sim-transfer-negative-and-conflict",
    "sim-selected-thermal-failures",
    "sim-traceability-non-simulator-boundaries",
}
REQUIRED_ARTIFACT_KINDS = {
    "machine-readable-run-manifest",
    "simulator-log-reference",
    "normalized-scenario-summary",
    "redacted-evidence-summary",
    "contract-snapshot",
}
REQUIRED_EXTERNAL_INPUTS = {
    "firmware_bin",
    "firmware_bbf_adjacent",
    "mini404_qemu",
    "pytest_environment",
    "ocr_cache",
}
BOUNDARY_STATUSES = {
    "pending-hardware",
    "pending-live-service",
    "pending-release",
    "pending-review",
}
FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"-----BEGIN CERTIFICATE-----", re.IGNORECASE),
    re.compile(
        r"\b(certificate[_-]?pem|password[_-]?value|token[_-]?value|certificate[_-]?bytes|private[_-]?key|signing[_-]?key[_-]?value|raw[_-]?crash[_-]?dump|firmware[_-]?payload)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bConnect token\b", re.IGNORECASE),
    re.compile(r"\bWi-Fi credential\b", re.IGNORECASE),
    re.compile(r"\bcredential value\b", re.IGNORECASE),
)
OVERCLAIM_STRINGS = {
    "hardware verified locally",
    "local hardware proof",
    "simulator passed locally",
    "live service passed locally",
    "release-candidate passed locally",
    "signing verified locally",
    "retained-code accepted by maintainer",
    "reference demotion approved",
    "reference removal complete",
    "cutover complete",
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


def load_json(root: Path, path: str | Path) -> dict[str, Any]:
    relative_path = Path(path)
    try:
        data = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as error:
        raise VerificationError(
            f"{relative_path.as_posix()} is not valid JSON: {error}"
        ) from error
    if not isinstance(data, dict):
        raise VerificationError(
            f"{relative_path.as_posix()} must contain a top-level object")
    return data


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of non-empty strings")
    return value


def require_dict(row: dict[str, Any], field: str,
                 row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_fields(row: dict[str, Any], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields
        if field in row and row[field] in ("", None, {})
    ]
    if missing or empty:
        parts: list[str] = []
        if missing:
            parts.append("missing required fields: " + ", ".join(missing))
        if empty:
            parts.append("empty required fields: " + ", ".join(empty))
        raise VerificationError(f"{row_name} " + "; ".join(parts))


def require_repo_relative_under(path_value: str | Path,
                                output_root: str | Path,
                                row_name: str) -> Path:
    relative_path = Path(path_value)
    expected_root = Path(output_root)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} path must be repo-relative and cannot traverse: {path_value}"
        )
    try:
        relative_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} path must stay under {expected_root.as_posix()}: {relative_path.as_posix()}"
        ) from error
    return relative_path


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


def sanitized_for_artifact(path: Path, text: str) -> tuple[str, list[str]]:
    errors: list[str] = []
    sanitized = text
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(sanitized):
            errors.append(
                f"{path.as_posix()} contained forbidden evidence content")
            sanitized = pattern.sub("[REDACTED-FORBIDDEN-EVIDENCE]", sanitized)
    for phrase in sorted(OVERCLAIM_STRINGS):
        if phrase.lower() in sanitized.lower():
            errors.append(
                f"{path.as_posix()} contained non-local evidence overclaim wording"
            )
            sanitized = re.sub(
                re.escape(phrase),
                "[REDACTED-NON-LOCAL-OVERCLAIM]",
                sanitized,
                flags=re.IGNORECASE,
            )
    return sanitized, errors


def contract_scenarios(contract: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = contract.get("scenarios")
    if not isinstance(scenarios, list):
        raise VerificationError(
            f"{CONTRACT_MANIFEST.as_posix()} must contain a scenarios list")
    parsed: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} scenarios[{index}] must be an object"
            )
        parsed.append(scenario)
    return parsed


def row_id_exists(data: Any, row_id: str) -> bool:
    if isinstance(data, dict):
        if data.get("id") == row_id:
            return True
        return any(row_id_exists(value, row_id) for value in data.values())
    if isinstance(data, list):
        return any(row_id_exists(value, row_id) for value in data)
    return False


def resolve_source_ref(root: Path, source_ref: str, row_name: str) -> None:
    if "#" not in source_ref:
        raise VerificationError(
            f"{row_name} source ref must use file#row-id: {source_ref}")
    path_text, row_id = source_ref.split("#", 1)
    if not path_text or not row_id:
        raise VerificationError(
            f"{row_name} source ref must include file and row ID: {source_ref}"
        )
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationError(
            f"{row_name} source ref must be repo-relative: {source_ref}")
    data = load_json(root, relative_path)
    if not row_id_exists(data, row_id):
        raise VerificationError(
            f"{row_name} source ref row not found: {source_ref}")


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase14_simulator_evidence_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase14-simulator-evidence",
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    try:
        status_vocabulary = set(
            require_list_of_strings(contract, "status_vocabulary", "contract"))
        artifact_kinds = set(
            require_list_of_strings(contract, "required_artifact_kinds",
                                    "contract"))
        external_inputs = set(
            require_dict(contract, "external_inputs", "contract"))
        scenarios = contract_scenarios(contract)
    except VerificationError as error:
        raise VerificationError(str(error)) from error
    missing_artifact_kinds = sorted(REQUIRED_ARTIFACT_KINDS - artifact_kinds)
    if missing_artifact_kinds:
        errors.append("missing required artifact kinds: " +
                      ", ".join(missing_artifact_kinds))
    missing_external_inputs = sorted(REQUIRED_EXTERNAL_INPUTS -
                                     external_inputs)
    if missing_external_inputs:
        errors.append("missing external inputs: " +
                      ", ".join(missing_external_inputs))
    scenario_ids = [str(scenario.get("id")) for scenario in scenarios]
    missing_scenarios = sorted(REQUIRED_SCENARIO_IDS - set(scenario_ids))
    extra_scenarios = sorted(set(scenario_ids) - REQUIRED_SCENARIO_IDS)
    if missing_scenarios:
        errors.append("missing required scenarios: " +
                      ", ".join(missing_scenarios))
    if extra_scenarios:
        errors.append("unexpected scenarios: " + ", ".join(extra_scenarios))
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("duplicate scenario IDs are not allowed")
    covered_requirements: set[str] = set()
    scenario_fields = [
        "id",
        "title",
        "requirement_ids",
        "v1_requirement_ids",
        "phase11_source_refs",
        "pytest_node_ids",
        "skipped_pytest_node_ids",
        "proof_scope",
        "expected_pass_semantics",
        "expected_failure_semantics",
        "expected_artifact_path",
        "retained_artifact_kind",
        "allowed_statuses",
        "residual_non_simulator_gates",
        "unsupported_claims",
    ]
    for scenario in scenarios:
        row_name = f"{CONTRACT_MANIFEST.as_posix()} scenario {scenario.get('id', '<unknown>')}"
        try:
            require_fields(scenario, scenario_fields, row_name)
            scenario_id = require_string(scenario, "id", row_name)
            requirement_ids = set(
                require_list_of_strings(scenario, "requirement_ids", row_name))
            if not requirement_ids:
                raise VerificationError(
                    f"{row_name} must map to at least one SIM requirement ID")
            unknown_requirements = sorted(requirement_ids -
                                          REQUIRED_REQUIREMENT_IDS)
            if unknown_requirements:
                raise VerificationError(
                    f"{row_name} requirement_ids contains unsupported values: "
                    + ", ".join(unknown_requirements))
            covered_requirements.update(requirement_ids)
            v1_ids = require_list_of_strings(scenario, "v1_requirement_ids",
                                             row_name)
            if not v1_ids:
                raise VerificationError(
                    f"{row_name} must map to at least one v1 requirement or reference ID"
                )
            phase11_refs = require_list_of_strings(scenario,
                                                   "phase11_source_refs",
                                                   row_name)
            if not phase11_refs:
                raise VerificationError(
                    f"{row_name} must map to at least one Phase 11 source ref")
            for source_ref in phase11_refs:
                resolve_source_ref(root, source_ref, row_name)
            proof_scope = require_string(scenario, "proof_scope", row_name)
            expected_scope = ("contract-boundary" if scenario_id
                              == "sim-traceability-non-simulator-boundaries"
                              else "simulator")
            if proof_scope != expected_scope:
                raise VerificationError(
                    f"{row_name} proof_scope must be {expected_scope!r}")
            pytest_node_ids = set(
                require_list_of_strings(scenario, "pytest_node_ids", row_name))
            skipped_pytest_node_ids = set(
                require_list_of_strings(scenario, "skipped_pytest_node_ids",
                                        row_name))
            overlapping_nodes = sorted(pytest_node_ids
                                       & skipped_pytest_node_ids)
            if overlapping_nodes:
                raise VerificationError(
                    f"{row_name} cannot use skipped nodes as pass evidence: " +
                    ", ".join(overlapping_nodes))
            if scenario_id != "sim-traceability-non-simulator-boundaries" and not pytest_node_ids:
                raise VerificationError(
                    f"{row_name} must include at least one active pytest node")
            retained_kind = require_string(scenario, "retained_artifact_kind",
                                           row_name)
            if retained_kind not in artifact_kinds:
                raise VerificationError(
                    f"{row_name} retained_artifact_kind is not declared: {retained_kind}"
                )
            allowed_statuses = set(
                require_list_of_strings(scenario, "allowed_statuses",
                                        row_name))
            unsupported_statuses = sorted(allowed_statuses - status_vocabulary)
            if unsupported_statuses:
                raise VerificationError(
                    f"{row_name} allowed_statuses contains unsupported values: "
                    + ", ".join(unsupported_statuses))
            residual_statuses = set(
                require_list_of_strings(scenario,
                                        "residual_non_simulator_gates",
                                        row_name))
            unsupported_residuals = sorted(residual_statuses -
                                           status_vocabulary)
            if unsupported_residuals:
                raise VerificationError(
                    f"{row_name} residual_non_simulator_gates contains unsupported values: "
                    + ", ".join(unsupported_residuals))
            if scenario_id == "sim-traceability-non-simulator-boundaries":
                missing_boundaries = sorted(BOUNDARY_STATUSES -
                                            residual_statuses)
                if missing_boundaries:
                    raise VerificationError(
                        f"{row_name} missing boundary statuses: {', '.join(missing_boundaries)}"
                    )
            require_repo_relative_under(
                require_string(scenario, "expected_artifact_path", row_name),
                DEFAULT_OUTPUT_DIR,
                row_name,
            )
            failure_semantics = require_string(scenario,
                                               "expected_failure_semantics",
                                               row_name)
            if "reason" not in failure_semantics:
                raise VerificationError(
                    f"{row_name} expected_failure_semantics must describe a reason"
                )
            unsupported_claims = require_list_of_strings(
                scenario, "unsupported_claims", row_name)
            if not unsupported_claims:
                raise VerificationError(
                    f"{row_name} must name unsupported claims")
        except VerificationError as error:
            errors.append(str(error))
    missing_requirements = sorted(REQUIRED_REQUIREMENT_IDS -
                                  covered_requirements)
    if missing_requirements:
        errors.append("contract does not cover requirements: " +
                      ", ".join(missing_requirements))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


def security_paths(root: Path) -> list[Path]:
    paths = [CONTRACT_MANIFEST]
    output_root = root / DEFAULT_OUTPUT_DIR
    if output_root.exists():
        paths.extend(
            path.relative_to(root) for path in sorted(output_root.rglob("*"))
            if path.is_file())
    return [path for path in paths if (root / path).exists()]


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in security_paths(root):
        try:
            reject_forbidden_text(path, read_text(root, path))
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def require_file_contains(root: Path, path: Path,
                          needles: list[str]) -> list[str]:
    try:
        text = read_text(root, path)
    except VerificationError as error:
        return [str(error)]
    return [
        f"{path.as_posix()} missing required wiring text: {needle}"
        for needle in needles if needle not in text
    ]


def check_wiring(root: Path) -> None:
    errors: list[str] = []
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/BUILD.bazel"),
            [
                'name = "phase14_verify"',
                'name = "phase14_verify_tests"',
                "phase14_simulator_evidence.py",
                "phase14_simulator_evidence_test.py",
                "phase14_simulator_evidence_contract.json",
                "//:phase14_simulator_evidence_docs",
                "//:phase11_cutover_evidence_docs",
                "phase14_phase11_source_ref_manifests",
                "manifests/phase11_cutover_readiness.json",
                "manifests/phase11_parity_pyramid.json",
                "manifests/phase11_reference_comparisons.json",
                "manifests/phase11_requirement_evidence.json",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase14_simulator_evidence_docs"',
                'name = "phase14_verify"',
                'name = "phase14_verify_tests"',
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase14_verify)",
                "python3 tools/bazel/phase14_simulator_evidence.py --wiring-only",
                "python3 tools/bazel/phase14_simulator_evidence.py --quick",
                "phase14_verify_tests)",
                "python3 tools/bazel/phase14_simulator_evidence_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase14-verify:",
                "bazel run //tools/bazel:phase14_verify_tests",
                "bazel run //tools/bazel:phase14_verify",
            ],
        ))
    try:
        just_lines = [
            line.strip() for line in read_text(root, "justfile").splitlines()
        ]
        just_tests_line = "bazel run //tools/bazel:phase14_verify_tests"
        just_verify_line = "bazel run //tools/bazel:phase14_verify"
        if just_tests_line not in just_lines:
            errors.append(
                "justfile missing exact phase14_verify_tests recipe line")
        if just_verify_line not in just_lines:
            errors.append("justfile missing exact phase14_verify recipe line")
        if just_tests_line in just_lines and just_verify_line in just_lines:
            if just_lines.index(just_tests_line) > just_lines.index(
                    just_verify_line):
                errors.append(
                    "justfile phase14-verify must run tests before verifier")
        workflow_text = read_text(root, "tools/bazel/rust_workflow.sh")
        tests_case_index = workflow_text.find("phase14_verify_tests)")
        verify_case_index = workflow_text.find("phase14_verify)")
        if tests_case_index == -1 or verify_case_index == -1:
            errors.append("rust_workflow.sh missing phase14 dispatch cases")
    except VerificationError as error:
        errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
