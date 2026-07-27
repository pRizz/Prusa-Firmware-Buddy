#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE = "13-ci-evidence-orchestration"
PHASE_LIFECYCLE_ID = "13-2026-06-16T14-21-01"

CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase13_ci_evidence_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase13")
WORKFLOW_FILE = Path(".github/workflows/ci-evidence.yml")
VALIDATION_FILE = Path(
    ".planning/phases/13-ci-evidence-orchestration/13-VALIDATION.md")

PHASE11_REQUIREMENT_EVIDENCE = Path(
    "tools/bazel/manifests/phase11_requirement_evidence.json")
PHASE11_CUTOVER_READINESS = Path(
    "tools/bazel/manifests/phase11_cutover_readiness.json")
PHASE11_RETAINED_CODE_JUSTIFICATIONS = Path(
    "tools/bazel/manifests/phase11_retained_code_justifications.json")
PHASE11_REFERENCE_COMPARISONS = Path(
    "tools/bazel/manifests/phase11_reference_comparisons.json")

ALLOWED_REQUIREMENT_IDS = {"CIEV-01", "CIEV-02", "CIEV-03"}
REQUIRED_GATE_IDS = {
    "ciev-01-pr-path-trigger",
    "ciev-01-aggregate-cutover-verifier",
    "ciev-02-run-manifest",
    "ciev-03-manifest-and-comparison-snapshots",
    "ciev-03-redacted-summary",
}
STATIC_GATE_DEFINITIONS = {
    "ciev-01-pr-path-trigger": {
        "id": "ciev-01-pr-path-trigger",
        "requirement_id": "CIEV-01",
        "owning_phase": PHASE,
        "command":
        "python3 tools/bazel/phase13_ci_evidence.py --workflow-only",
        "proof_scope": "ci-orchestration",
        "expected_artifact_path":
        "build/ci-evidence/phase13/logs/phase13-workflow.log",
        "retained_artifact_kind": "verifier-log",
    },
    "ciev-01-aggregate-cutover-verifier": {
        "id": "ciev-01-aggregate-cutover-verifier",
        "requirement_id": "CIEV-01",
        "owning_phase": PHASE,
        "command": "python3 tools/bazel/phase11_verify.py --quick",
        "proof_scope": "ci-local-aggregate",
        "expected_artifact_path":
        "build/ci-evidence/phase13/logs/phase11-quick.log",
        "retained_artifact_kind": "verifier-log",
    },
    "ciev-02-run-manifest": {
        "id": "ciev-02-run-manifest",
        "requirement_id": "CIEV-02",
        "owning_phase": PHASE,
        "command":
        "python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13",
        "proof_scope": "ci-generated-manifest",
        "expected_artifact_path":
        "build/ci-evidence/phase13/run-manifest.json",
        "retained_artifact_kind": "machine-readable-ci-manifest",
    },
    "ciev-03-manifest-and-comparison-snapshots": {
        "id": "ciev-03-manifest-and-comparison-snapshots",
        "requirement_id": "CIEV-03",
        "owning_phase": PHASE,
        "command":
        "python3 tools/bazel/phase13_ci_evidence.py --ci --output-dir build/ci-evidence/phase13",
        "proof_scope": "ci-artifact-retention",
        "expected_artifact_path":
        "build/ci-evidence/phase13/manifest-snapshots/phase13_ci_evidence_contract.json",
        "retained_artifact_kind": "manifest-snapshot",
    },
    "ciev-03-redacted-summary": {
        "id": "ciev-03-redacted-summary",
        "requirement_id": "CIEV-03",
        "owning_phase": PHASE,
        "command":
        "python3 tools/bazel/phase13_ci_evidence.py --security-only",
        "proof_scope": "ci-artifact-retention",
        "expected_artifact_path":
        "build/ci-evidence/phase13/redacted-summary.json",
        "retained_artifact_kind": "redacted-evidence-summary",
    },
}
REQUIRED_SOURCE_REFS = {
    ".planning/milestones/v1.0-phases/11-parity-pyramid-and-cutover-evidence/11-VERIFICATION.md",
    "tools/bazel/manifests/phase11_requirement_evidence.json",
    "tools/bazel/manifests/phase11_cutover_readiness.json",
}
REQUIRED_WORKFLOW_PATH_FILTERS = [
    ".github/workflows/ci-evidence.yml",
    ".github/workflows/**",
    "BUILD.bazel",
    "MODULE.bazel",
    ".bazelrc",
    "platforms/**",
    "tools/bazel/**",
    "tools/bazel/manifests/**",
    "Cargo.toml",
    "Cargo.lock",
    "rust/**",
    ".planning/PROJECT.md",
    ".planning/ROADMAP.md",
    ".planning/REQUIREMENTS.md",
    ".planning/STATE.md",
    ".planning/phases/**",
    ".planning/milestones/**",
    "CMakeLists.txt",
    "ProjectOptions.cmake",
    "cmake/**",
    "utils/build.py",
    "utils/pack_fw.py",
    "utils/dfu.py",
    "utils/presets/**",
    "src/resources/**",
    "src/lang/**",
    "lib/Add*.cmake",
]
REQUIRED_WORKFLOW_STRINGS = [
    "workflow_dispatch:",
    "permissions:",
    "contents: read",
    "actions/checkout@v6",
    "actions/upload-artifact@v7",
    "if: always()",
    "retention-days: 30",
    "if-no-files-found: error",
    "build/ci-evidence/phase13/",
]
FORBIDDEN_WORKFLOW_STRINGS = [
    "contents: write",
    "pull-requests: write",
    "id-token: write",
    "secrets.",
    "bash -c",
    "python -c",
    "node -e",
    "run: |",
    "run: >",
]
PENDING_NON_LOCAL_EVIDENCE = [
    "simulator evidence (Phase 14)",
    "hardware safety and media evidence (Phase 15)",
    "live network and transfer evidence (Phase 16)",
    "release-candidate artifact and signing evidence (Phase 17)",
    "retained-code acceptance and cutover review evidence (Phase 18)",
]
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


def require_fields(row: dict[str, object], fields: list[str],
                   row_name: str) -> None:
    missing = [field for field in fields if field not in row]
    empty = [
        field for field in fields
        if field in row and row[field] in ("", None, [], {})
    ]
    if not missing and not empty:
        return
    details: list[str] = []
    if missing:
        details.append("missing required fields: " + ", ".join(missing))
    if empty:
        details.append("empty required fields: " + ", ".join(empty))
    raise VerificationError(f"{row_name} " + "; ".join(details))


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


def contract_gates(contract: dict[str, object]) -> list[dict[str, object]]:
    gates = contract.get("gates")
    if not isinstance(gates, list):
        raise VerificationError(
            f"{CONTRACT_MANIFEST.as_posix()} must contain a gates list")
    parsed_gates: list[dict[str, object]] = []
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} gates[{index}] must be an object"
            )
        parsed_gates.append(gate)
    return parsed_gates


def gate_by_id(contract: dict[str, object], gate_id: str) -> dict[str, object]:
    for gate in contract_gates(contract):
        if gate.get("id") == gate_id:
            return gate
    raise VerificationError(
        f"{CONTRACT_MANIFEST.as_posix()} missing gate: {gate_id}")


def gate_by_id_or_static(contract: dict[str, object],
                         gate_id: str) -> dict[str, object]:
    try:
        return gate_by_id(contract, gate_id)
    except VerificationError:
        return STATIC_GATE_DEFINITIONS[gate_id]


def safe_gate_for_artifact(contract: dict[str, object],
                           gate_id: str) -> dict[str, object]:
    gate = dict(gate_by_id_or_static(contract, gate_id))
    artifact_fields = [
        "id",
        "requirement_id",
        "owning_phase",
        "command",
        "proof_scope",
        "expected_artifact_path",
        "retained_artifact_kind",
    ]
    for field in artifact_fields:
        value = str(gate.get(field, ""))
        sanitized_value, errors = sanitized_for_artifact(Path(field), value)
        if errors:
            return STATIC_GATE_DEFINITIONS[gate_id]
        gate[field] = sanitized_value
    return gate


def check_contract(root: Path) -> None:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase13_ci_evidence_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase13-ci-evidence",
        "retention_days": 30,
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    try:
        status_vocabulary = set(
            require_list_of_strings(contract, "status_vocabulary", "contract"))
        required_artifact_kinds = set(
            require_list_of_strings(contract, "required_artifact_kinds",
                                    "contract"))
        require_list_of_strings(contract, "forbidden_generated_artifacts",
                                "contract")
        gates = contract_gates(contract)
    except VerificationError as error:
        errors.append(str(error))
        gates = []
        status_vocabulary = set()
        required_artifact_kinds = set()
    gate_ids = [str(gate.get("id")) for gate in gates]
    missing_gate_ids = sorted(REQUIRED_GATE_IDS - set(gate_ids))
    extra_gate_ids = sorted(set(gate_ids) - REQUIRED_GATE_IDS)
    if missing_gate_ids:
        errors.append("missing required gates: " + ", ".join(missing_gate_ids))
    if extra_gate_ids:
        errors.append("unexpected gates: " + ", ".join(extra_gate_ids))
    if len(gate_ids) != len(set(gate_ids)):
        errors.append("duplicate gate IDs are not allowed")
    gate_fields = [
        "id",
        "requirement_id",
        "owning_phase",
        "command",
        "proof_scope",
        "expected_artifact_path",
        "retained_artifact_kind",
        "allowed_statuses",
        "failure_reason_semantics",
        "source_evidence_refs",
    ]
    for gate in gates:
        gate_name = f"{CONTRACT_MANIFEST.as_posix()} gate {gate.get('id', '<unknown>')}"
        try:
            require_fields(gate, gate_fields, gate_name)
            gate_id = require_string(gate, "id", gate_name)
            requirement_id = require_string(gate, "requirement_id", gate_name)
            if requirement_id not in ALLOWED_REQUIREMENT_IDS:
                raise VerificationError(
                    f"{gate_name} requirement_id is not allowed: {requirement_id}"
                )
            if gate.get("owning_phase") != PHASE:
                raise VerificationError(
                    f"{gate_name} owning_phase must be {PHASE}")
            retained_artifact_kind = require_string(gate,
                                                    "retained_artifact_kind",
                                                    gate_name)
            if retained_artifact_kind not in required_artifact_kinds:
                raise VerificationError(
                    f"{gate_name} retained_artifact_kind is not declared: {retained_artifact_kind}"
                )
            allowed_statuses = set(
                require_list_of_strings(gate, "allowed_statuses", gate_name))
            unsupported_statuses = sorted(allowed_statuses - status_vocabulary)
            if unsupported_statuses:
                raise VerificationError(
                    f"{gate_name} allowed_statuses contains unsupported values: "
                    + ", ".join(unsupported_statuses))
            require_repo_relative_under(
                require_string(gate, "expected_artifact_path", gate_name),
                DEFAULT_OUTPUT_DIR,
                gate_name,
            )
            source_refs = set(
                require_list_of_strings(gate, "source_evidence_refs",
                                        gate_name))
            missing_refs = sorted(REQUIRED_SOURCE_REFS - source_refs)
            if missing_refs:
                raise VerificationError(
                    f"{gate_name} missing source_evidence_refs: {', '.join(missing_refs)}"
                )
            for source_ref in source_refs:
                relative_ref = Path(source_ref)
                if relative_ref.is_absolute() or ".." in relative_ref.parts:
                    raise VerificationError(
                        f"{gate_name} source_evidence_ref is not repo-relative: {source_ref}"
                    )
                if relative_ref.name in {"ROADMAP.md", "v1.0-ROADMAP.md"}:
                    raise VerificationError(
                        f"{gate_name} source_evidence_refs must not be roadmap-only proof"
                    )
                if not (root / relative_ref).exists():
                    raise VerificationError(
                        f"{gate_name} references missing source evidence: {source_ref}"
                    )
            failure_reason_semantics = require_string(
                gate, "failure_reason_semantics", gate_name)
            if "reason" not in failure_reason_semantics:
                raise VerificationError(
                    f"{gate_name} failure_reason_semantics must describe a reason"
                )
            if gate_id in REQUIRED_GATE_IDS and not require_string(
                    gate, "command", gate_name).startswith("python3 "):
                raise VerificationError(
                    f"{gate_name} command must be a repo-owned python3 entrypoint"
                )
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))


def check_workflow(root: Path) -> None:
    workflow_text = read_text(root, WORKFLOW_FILE)
    reject_forbidden_text(WORKFLOW_FILE, workflow_text)
    errors = [
        f"{WORKFLOW_FILE.as_posix()} missing required workflow path filter: {path_filter}"
        for path_filter in REQUIRED_WORKFLOW_PATH_FILTERS
        if path_filter not in workflow_text
    ]
    errors.extend(
        f"{WORKFLOW_FILE.as_posix()} missing required workflow text: {needle}"
        for needle in REQUIRED_WORKFLOW_STRINGS if needle not in workflow_text)
    errors.extend(
        f"{WORKFLOW_FILE.as_posix()} contains forbidden workflow text: {needle}"
        for needle in FORBIDDEN_WORKFLOW_STRINGS if needle in workflow_text)
    if not re.search(
            r"python3 tools/bazel/phase13_ci_evidence\.py --ci --output-dir build/ci-evidence/phase13",
            workflow_text,
    ):
        errors.append(
            f"{WORKFLOW_FILE.as_posix()} missing Phase 13 CI evidence command")
    if re.search(r"(?m)^\s*path:\s*\.planning\b", workflow_text):
        errors.append(
            f"{WORKFLOW_FILE.as_posix()} must not upload hidden planning paths"
        )
    if errors:
        raise VerificationError("\n".join(errors))


def existing_security_paths(root: Path) -> list[Path]:
    paths = [
        CONTRACT_MANIFEST,
        WORKFLOW_FILE,
        VALIDATION_FILE,
    ]
    output_root = root / DEFAULT_OUTPUT_DIR
    if output_root.exists():
        paths.extend(
            path.relative_to(root) for path in sorted(output_root.rglob("*"))
            if path.is_file())
    return [path for path in paths if (root / path).exists()]


def check_security(root: Path) -> None:
    errors: list[str] = []
    for path in existing_security_paths(root):
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
                'name = "phase13_verify"',
                'name = "phase13_verify_tests"',
                "phase13_ci_evidence.py",
                "phase13_ci_evidence_test.py",
                "phase13_ci_evidence_contract.json",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase13_verify)",
                "python3 tools/bazel/phase13_ci_evidence.py --wiring-only",
                "python3 tools/bazel/phase13_ci_evidence.py --quick",
                "phase13_verify_tests)",
                "python3 tools/bazel/phase13_ci_evidence_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase13_ci_evidence_docs"',
                'name = "phase13_verify"',
                'name = "phase13_verify_tests"',
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase13-verify:",
                "bazel run //tools/bazel:phase13_verify_tests",
                "bazel run //tools/bazel:phase13_verify",
            ],
        ))
    if errors:
        raise VerificationError("\n".join(errors))
