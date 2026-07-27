#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE = "33-maintainer-decision-inputs"
PHASE_LIFECYCLE_ID = "33-2026-07-04T01-36-41"
PHASE32_LIFECYCLE_ID = "32-2026-07-03T14-13-51"
CONTRACT_MANIFEST = Path(
    "tools/bazel/manifests/phase33_maintainer_decision_inputs_contract.json")
DEFAULT_PHASE32_HANDOFF = Path(
    "build/ci-evidence/phase32/downstream-handoff-manifest.json")
DEFAULT_OUTPUT_DIR = Path("build/ci-evidence/phase33")
PHASE32_REGISTER_REF = "build/ci-evidence/phase32/blocker-register.json"
PHASE32_OUTPUT_ROOT = Path("build/ci-evidence/phase32")
SOURCE_CONTRACT_SNAPSHOTS = {
    "phase33_maintainer_decision_inputs_contract.json":
    CONTRACT_MANIFEST,
    "phase32_blocker_register_triage_contract.json":
    Path(
        "tools/bazel/manifests/phase32_blocker_register_triage_contract.json"),
    "phase27_retained_code_acceptance_decisions_contract.json":
    Path(
        "tools/bazel/manifests/phase27_retained_code_acceptance_decisions_contract.json"
    ),
    "phase28_final_readiness_packet_contract.json":
    Path("tools/bazel/manifests/phase28_final_readiness_packet_contract.json"),
}
REQUIRED_REQUIREMENT_IDS = ["DECIDE-01", "DECIDE-02", "DECIDE-03"]
REQUIRED_SOURCE_CONTRACT_IDS = [
    "phase32_blocker_register_triage_contract",
    "phase27_retained_code_acceptance_decisions_contract",
    "phase28_final_readiness_packet_contract",
]
REQUIRED_DECISION_FIELDS = [
    "decision_id",
    "decision_type",
    "decision_value",
    "decision_targets",
    "source_row_refs",
    "maintainer_identity_ref",
    "maintainer_role",
    "owner_signoff_ref",
    "decision_timestamp",
    "rationale",
    "evidence_refs",
    "artifact_refs",
]
REQUIRED_DECISION_TARGET_FIELDS = [
    "row_ref",
    "decision_axis",
    "decision_subject_id",
]
DECISION_VALUE_ENUMS = {
    "retained_code": ["accept", "reject", "exception_approve"],
    "residual_risk": ["accept", "reject"],
    "exception": ["approve", "reject"],
    "readiness": ["approve", "block"],
    "reference_demotion": ["approve", "reject"],
}
DECISION_TYPES = list(DECISION_VALUE_ENUMS)
DECISION_TYPE_AXES = {
    "retained_code": "retained_code",
    "residual_risk": "residual_risk",
    "exception": "exception",
    "readiness": "readiness",
    "reference_demotion": "demotion",
}
DECISION_TYPE_IMPACTS = {
    "retained_code": {"retained_code_decision_required"},
    "residual_risk": {"residual_risk_decision_required"},
    "exception": {"exception_decision_required"},
    "readiness": {"final_readiness_blocked"},
    "reference_demotion": {"demotion_decision_required"},
}
APPROVAL_DECISION_VALUES = {
    "retained_code": {"accept", "exception_approve"},
    "residual_risk": {"accept"},
    "exception": {"approve"},
    "readiness": {"approve"},
    "reference_demotion": {"approve"},
}
AXIS_SPECIFIC_REGISTER_FIELDS = {
    "retained_code": ["residual_risk_rationale"],
    "residual_risk": ["affected_gates", "follow_up_refs"],
    "exception": [
        "scope",
        "expiry_or_review_trigger",
        "affected_requirements",
        "affected_gates",
        "linked_blocker_refs",
    ],
}
HARD_BLOCKER_PROBLEM_KINDS = {
    "redaction_failed",
    "source_ref_failed",
    "secret_tainted",
    "lifecycle_mismatch",
    "unsafe_ref",
}
SECURITY_SCAN_CONTRACT_ALLOWLIST = {
    CONTRACT_MANIFEST.as_posix(),
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase32_blocker_register_triage_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase28_final_readiness_packet_contract.json",
}
GENERATED_ARTIFACTS = [
    "maintainer-decision-input-template.json",
    "normalized-decision-records.json",
    "retained-code-decision-register.json",
    "residual-risk-decision-register.json",
    "exception-decision-register.json",
    "readiness-decision-handoff.json",
    "demotion-decision-handoff.json",
    "decision-validation-report.json",
    "downstream-handoff-manifest.json",
    "redacted-maintainer-decision-report.md",
    "contract-snapshots/phase33_maintainer_decision_inputs_contract.json",
    "contract-snapshots/phase32_blocker_register_triage_contract.json",
    "contract-snapshots/phase27_retained_code_acceptance_decisions_contract.json",
    "contract-snapshots/phase28_final_readiness_packet_contract.json",
    "contract-snapshots/phase32-downstream-handoff-manifest.json",
    "contract-snapshots/phase32-blocker-register.json",
]
EMITTED_OUTPUT_SCAN_ARTIFACTS = [
    artifact for artifact in GENERATED_ARTIFACTS
    if artifact not in SECURITY_SCAN_CONTRACT_ALLOWLIST
]
FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api_key",
    "authorization_header",
    "certificate_private_material",
    "client_secret",
    "connect_token",
    "credential_value",
    "demotion_allowed",
    "password",
    "private_key",
    "raw_crash_dump",
    "raw_release_log",
    "secret",
    "secret_value",
    "service_payload",
    "signing_key_value",
    "signing_payload_bytes",
    "tls_keylog",
    "token",
    "token_value",
    "wifi_credential",
    "wifi_password",
}
FORBIDDEN_TEXT_PATTERNS = (
    ("private-key-block",
     re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE)),
    ("bearer-token",
     re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE)),
    ("certificate-private-material",
     re.compile(r"\bcertificate[_ -]?private[_ -]?material\b", re.IGNORECASE)),
    ("service-payload", re.compile(r"\bservice[_ -]?payload\b",
                                   re.IGNORECASE)),
    ("raw-crash-dump",
     re.compile(r"\braw[_ -]?crash[_ -]?dump\b", re.IGNORECASE)),
    ("raw-release-log",
     re.compile(r"\braw[_ -]?release[_ -]?log\b", re.IGNORECASE)),
    ("tls-keylog", re.compile(r"\btls[_ -]?keylog\b", re.IGNORECASE)),
    ("wifi-credential",
     re.compile(r"\bwi[-_ ]?fi[_ -]?credential\b", re.IGNORECASE)),
    ("demotion-allowed",
     re.compile(r'"?demotion_allowed"?\s*:\s*(true|false|"[^"]*")',
                re.IGNORECASE)),
    ("reference-demotion-approved",
     re.compile(r"\breference demotion approved\b", re.IGNORECASE)),
    ("final-readiness-approved",
     re.compile(r"\bfinal readiness approved\b", re.IGNORECASE)),
    ("final-readiness-unblocked",
     re.compile(r'"?final_readiness_status"?\s*:\s*"unblocked"',
                re.IGNORECASE)),
    ("cutover-verdict-approved",
     re.compile(r"\bcutover verdict approved\b", re.IGNORECASE)),
    ("accepted-by-evidence-alone",
     re.compile(r"\baccepted by evidence alone\b", re.IGNORECASE)),
)
PHASE33_VERIFY_COMMANDS = [
    "python3 tools/bazel/phase31_final_evidence_intake.py --quick --output-dir build/ci-evidence/phase31",
    "python3 tools/bazel/phase26_release_signing_upstream_evidence.py --quick --output-dir build/ci-evidence/phase26",
    ("python3 tools/bazel/phase27_retained_code_acceptance_decisions.py --quick "
     "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
     "--output-dir build/ci-evidence/phase27"),
    ("python3 tools/bazel/phase28_final_readiness_packet.py --quick "
     "--phase26-upstream-rows build/ci-evidence/phase26/upstream-result-row-table.json "
     "--phase27-handoff build/ci-evidence/phase27/phase28-handoff-manifest.json "
     "--output-dir build/ci-evidence/phase28"),
    ("python3 tools/bazel/phase32_blocker_register_triage.py --quick "
     "--phase31-output-dir build/ci-evidence/phase31 "
     "--phase27-output-dir build/ci-evidence/phase27 "
     "--phase28-output-dir build/ci-evidence/phase28 "
     "--output-dir build/ci-evidence/phase32"),
    "python3 tools/bazel/phase33_maintainer_decision_inputs.py --wiring-only",
    ("python3 tools/bazel/phase33_maintainer_decision_inputs.py --quick "
     "--phase32-handoff build/ci-evidence/phase32/downstream-handoff-manifest.json "
     "--output-dir build/ci-evidence/phase33"),
]


def _install_phase33_modules() -> None:
    module_dir = Path(__file__).resolve().parent
    for module_name in (
            "phase33_decision_policy.py",
            "phase33_decision_validation.py",
            "phase33_decision_outputs.py",
            "phase33_decision_wiring.py",
    ):
        source = (module_dir / module_name).read_text(encoding="utf-8")
        exec(compile(source, module_name, "exec"), globals())


_install_phase33_modules()
