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
PHASE = "19-aggregate-cutover-evidence-ci"
PHASE_LIFECYCLE_ID = "19-2026-06-21T01-07-45"

CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase19_aggregate_ci_evidence_contract.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase19")
WORKFLOW_FILE = Path(".github/workflows/ci-evidence.yml")
VALIDATION_FILE = Path(
    ".planning/phases/19-aggregate-cutover-evidence-ci/19-VALIDATION.md")

ALLOWED_REQUIREMENT_IDS = {
    "CIEV-01",
    "CIEV-02",
    "CIEV-03",
    "SIM-01",
    "SIM-02",
    "HARD-01",
    "HARD-02",
    "HARD-03",
    "LIVE-01",
    "LIVE-02",
    "LIVE-03",
}
EXPECTED_PHASES = {
    "14-simulator-evidence-gates",
    "15-hardware-safety-and-media-qualification",
    "16-live-network-and-transfer-qualification",
    "17-release-candidate-artifact-and-signing-gates",
    "18-retained-code-acceptance-and-cutover-review",
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
    "python3 tools/bazel/phase19_aggregate_ci_evidence.py --ci --output-dir build/ci-evidence/phase19",
    "build/ci-evidence/phase19/",
    "phase19-ci-evidence-${{ github.run_id }}-${{ github.run_attempt }}",
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
    "phase13_ci_evidence.py --ci",
    "build/ci-evidence/phase13/",
]
FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(
        r"\b(password[_-]?value|token[_-]?value|private[_-]?key|signing[_-]?key[_-]?value)\b",
        re.IGNORECASE),
    re.compile(
        r"\b(raw[_-]?crash[_-]?dump[_-]?value|firmware[_-]?payload[_-]?value|certificate[_-]?bytes)\b",
        re.IGNORECASE),
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
EXTERNAL_PENDING_STATUSES = {
    "pending-simulator-input",
    "pending-hardware-input",
    "pending-live-input",
    "pending-release-input",
    "pending-maintainer-review",
}


class VerificationError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(
        microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(root: Path, path: str | Path) -> str:
    relative_path = Path(path)
    full_path = root / relative_path
    if not full_path.exists():
        raise VerificationError(
            f"missing required file: {relative_path.as_posix()}")
    return full_path.read_text(encoding="utf-8")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


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
            f"{relative_path.as_posix()} must contain a top-level JSON object")
    return data


def require_string(row: dict[str, Any], field: str, row_name: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise VerificationError(
            f"{row_name} {field} must be a non-empty string")
    return value


def require_dict(row: dict[str, Any], field: str,
                 row_name: str) -> dict[str, Any]:
    value = row.get(field)
    if not isinstance(value, dict):
        raise VerificationError(f"{row_name} {field} must be an object")
    return value


def require_list_of_strings(row: dict[str, Any], field: str,
                            row_name: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value):
        raise VerificationError(
            f"{row_name} {field} must be a list of strings")
    return value


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


def require_safe_output_dir(root: Path, path_value: str | Path,
                            row_name: str) -> Path:
    relative_path = require_repo_relative_under(path_value, DEFAULT_OUTPUT_DIR,
                                                row_name)
    expected_root = root.resolve(strict=False) / DEFAULT_OUTPUT_DIR
    resolved_path = (root / relative_path).resolve(strict=False)
    try:
        resolved_path.relative_to(expected_root)
    except ValueError as error:
        raise VerificationError(
            f"{row_name} resolves outside {DEFAULT_OUTPUT_DIR.as_posix()}: {relative_path.as_posix()}"
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
            sanitized = re.sub(re.escape(phrase),
                               "[REDACTED-NON-LOCAL-OVERCLAIM]",
                               sanitized,
                               flags=re.IGNORECASE)
    return sanitized, errors


def contract_phases(contract: dict[str, Any]) -> list[dict[str, Any]]:
    phases = contract.get("phases")
    if not isinstance(phases, list):
        raise VerificationError(
            f"{CONTRACT_MANIFEST.as_posix()} phases must be a list")
    parsed_phases: list[dict[str, Any]] = []
    for index, phase in enumerate(phases):
        if not isinstance(phase, dict):
            raise VerificationError(
                f"{CONTRACT_MANIFEST.as_posix()} phases[{index}] must be an object"
            )
        parsed_phases.append(phase)
    return parsed_phases


def check_contract(root: Path) -> dict[str, Any]:
    contract_text = read_text(root, CONTRACT_MANIFEST)
    reject_forbidden_text(CONTRACT_MANIFEST, contract_text)
    contract = load_json(root, CONTRACT_MANIFEST)
    errors: list[str] = []
    expected_top_level = {
        "schema_version": "1",
        "id": "phase19_aggregate_ci_evidence_contract",
        "phase": PHASE,
        "phase_lifecycle_id": PHASE_LIFECYCLE_ID,
        "output_root": DEFAULT_OUTPUT_DIR.as_posix(),
        "artifact_name": "phase19-ci-evidence",
        "retention_days": 30,
    }
    for field, expected_value in expected_top_level.items():
        if contract.get(field) != expected_value:
            errors.append(
                f"{CONTRACT_MANIFEST.as_posix()} {field} must be {expected_value!r}"
            )
    try:
        requirement_ids = set(
            require_list_of_strings(contract, "requirement_ids", "contract"))
        status_vocabulary = set(
            require_list_of_strings(contract, "status_vocabulary", "contract"))
        required_manifest_fields = set(
            require_list_of_strings(contract, "required_manifest_fields",
                                    "contract"))
        phases = contract_phases(contract)
    except VerificationError as error:
        errors.append(str(error))
        requirement_ids = set()
        status_vocabulary = set()
        required_manifest_fields = set()
        phases = []
    missing_requirements = sorted(ALLOWED_REQUIREMENT_IDS - requirement_ids)
    extra_requirements = sorted(requirement_ids - ALLOWED_REQUIREMENT_IDS)
    if missing_requirements:
        errors.append("missing requirement IDs: " +
                      ", ".join(missing_requirements))
    if extra_requirements:
        errors.append("unexpected requirement IDs: " +
                      ", ".join(extra_requirements))
    for field in [
            "id", "requirement_ids", "owning_phase", "command",
            "artifact_path", "status", "failure_reason"
    ]:
        if field not in required_manifest_fields:
            errors.append(f"required_manifest_fields missing {field}")
    if not EXTERNAL_PENDING_STATUSES <= status_vocabulary:
        errors.append("status_vocabulary missing external pending statuses")
    owning_phases = {str(phase.get("owning_phase")) for phase in phases}
    if owning_phases != EXPECTED_PHASES:
        errors.append(
            "phases must cover exactly Phase 14-18 owning phases; got " +
            ", ".join(sorted(owning_phases)))
    for phase in phases:
        row_name = f"{CONTRACT_MANIFEST.as_posix()} phase {phase.get('owning_phase', '<unknown>')}"
        try:
            owning_phase = require_string(phase, "owning_phase", row_name)
            script = require_string(phase, "script", row_name)
            quick_output_dir = require_string(phase, "quick_output_dir",
                                              row_name)
            artifact_subdir = require_string(phase, "artifact_subdir",
                                             row_name)
            requirements = set(
                require_list_of_strings(phase, "requirements", row_name))
            modes = set(require_list_of_strings(phase, "local_modes",
                                                row_name))
            expected_artifacts = require_list_of_strings(
                phase, "expected_artifacts", row_name)
            external_input = require_dict(phase, "external_input", row_name)
            external_status = require_string(external_input, "status",
                                             f"{row_name} external_input")
            if owning_phase not in EXPECTED_PHASES:
                raise VerificationError(
                    f"{row_name} unexpected owning_phase: {owning_phase}")
            if not script.startswith("tools/bazel/phase"):
                raise VerificationError(
                    f"{row_name} script must be a repo-owned phase verifier")
            if not (root / script).exists():
                raise VerificationError(
                    f"{row_name} script does not exist: {script}")
            require_repo_relative_under(quick_output_dir,
                                        Path("build/ci-evidence"), row_name)
            if Path(quick_output_dir) == DEFAULT_OUTPUT_DIR:
                raise VerificationError(
                    f"{row_name} quick_output_dir must be a phase-specific source output"
                )
            if Path(artifact_subdir).is_absolute() or ".." in Path(
                    artifact_subdir).parts:
                raise VerificationError(
                    f"{row_name} artifact_subdir must be a safe relative path")
            if not requirements <= ALLOWED_REQUIREMENT_IDS:
                raise VerificationError(
                    f"{row_name} has unsupported requirements: {sorted(requirements - ALLOWED_REQUIREMENT_IDS)}"
                )
            if not {"contract-only", "wiring-only", "quick", "security-only"
                    } <= modes:
                raise VerificationError(
                    f"{row_name} local_modes must include contract-only, wiring-only, quick, security-only"
                )
            if external_status not in EXTERNAL_PENDING_STATUSES:
                raise VerificationError(
                    f"{row_name} external_input status must remain pending: {external_status}"
                )
            require_repo_relative_under(
                require_string(external_input, "artifact_path",
                               f"{row_name} external_input"),
                DEFAULT_OUTPUT_DIR,
                f"{row_name} external_input",
            )
            if not expected_artifacts:
                raise VerificationError(
                    f"{row_name} expected_artifacts cannot be empty")
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
    return contract


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
    if re.search(r"(?m)^\s*path:\s*\.planning\b", workflow_text):
        errors.append(
            f"{WORKFLOW_FILE.as_posix()} must not upload hidden planning paths"
        )
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
                'name = "phase19_verify"',
                'name = "phase19_verify_tests"',
                "phase19_aggregate_ci_evidence.py",
                "phase19_aggregate_ci_evidence_test.py",
                "phase19_aggregate_ci_evidence_contract.json",
                "phase14_simulator_evidence.py",
                "phase18_cutover_review.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("tools/bazel/rust_workflow.sh"),
            [
                "phase19_verify)",
                "python3 tools/bazel/phase19_aggregate_ci_evidence.py --wiring-only",
                "python3 tools/bazel/phase19_aggregate_ci_evidence.py --ci --output-dir build/ci-evidence/phase19",
                "phase19_verify_tests)",
                "python3 tools/bazel/phase19_aggregate_ci_evidence_test.py",
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("BUILD.bazel"),
            [
                'name = "phase19_aggregate_ci_evidence_docs"',
                'name = "phase19_verify"',
                'name = "phase19_verify_tests"',
            ],
        ))
    errors.extend(
        require_file_contains(
            root,
            Path("justfile"),
            [
                "phase19-verify:",
                "bazel run //tools/bazel:phase19_verify_tests",
                "bazel run //tools/bazel:phase19_verify",
            ],
        ))
    if errors:
        raise VerificationError("\n".join(errors))


def existing_security_paths(root: Path,
                            output_dir: Path = DEFAULT_OUTPUT_DIR
                            ) -> list[Path]:
    paths = [CONTRACT_MANIFEST, WORKFLOW_FILE, VALIDATION_FILE]
    output_root = root / output_dir
    if output_root.exists():
        paths.extend(
            path.relative_to(root) for path in sorted(output_root.rglob("*"))
            if path.is_file())
    return [path for path in paths if (root / path).exists()]


def check_security(root: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    errors: list[str] = []
    for path in existing_security_paths(root, output_dir):
        try:
            reject_forbidden_text(path, read_text(root, path))
        except VerificationError as error:
            errors.append(str(error))
    if errors:
        raise VerificationError("\n".join(errors))
